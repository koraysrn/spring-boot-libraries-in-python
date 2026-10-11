"""
Non-happy-path tests for the Flyway equivalent (Alembic).

Each test runs against a fresh SQLite database in a temporary directory.
"""

import threading
from pathlib import Path

import pytest
from alembic import command
from alembic.config import Config
from sqlalchemy import create_engine, inspect, text

import checksum_guard

BASE_DIR = Path(__file__).resolve().parent.parent
VERSIONS_DIR = BASE_DIR / "alembic" / "versions"


def make_config(db_url: str) -> Config:
    cfg = Config(str(BASE_DIR / "alembic.ini"))
    cfg.set_main_option("script_location", str(BASE_DIR / "alembic"))
    cfg.set_main_option("sqlalchemy.url", db_url)
    return cfg


def get_version(engine) -> str:
    with engine.connect() as conn:
        return conn.execute(text("SELECT version_num FROM alembic_version")).scalar()


def get_columns(engine, table: str) -> set:
    inspector = inspect(engine)
    return {c["name"] for c in inspector.get_columns(table)}


BAD_MIGRATION = '''"""bad migration"""
from alembic import op
import sqlalchemy as sa

revision = "0003"
down_revision = "0002"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "broken_table",
        sa.Column("id", sa.Integer, primary_key=True),
    )
    op.execute("THIS IS NOT VALID SQL")


def downgrade():
    op.drop_table("broken_table")
'''

DUP_A = '''"""duplicate a"""
from alembic import op
import sqlalchemy as sa

revision = "0003"
down_revision = "0002"
branch_labels = None
depends_on = None


def upgrade():
    pass


def downgrade():
    pass
'''

DUP_B = '''"""duplicate b"""
from alembic import op
import sqlalchemy as sa

revision = "0003"
down_revision = "0002"
branch_labels = None
depends_on = None


def upgrade():
    pass


def downgrade():
    pass
'''

ADD_REQUIRED_COLUMN = '''"""add required column"""
from alembic import op
import sqlalchemy as sa

revision = "0003"
down_revision = "0002"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column(
        "account",
        sa.Column("new_required", sa.String(50), nullable=False),
    )


def downgrade():
    op.drop_column("account", "new_required")
'''

NO_DOWNGRADE = '''"""no downgrade"""
from alembic import op
import sqlalchemy as sa

revision = "0003"
down_revision = "0002"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "extra_table",
        sa.Column("id", sa.Integer, primary_key=True),
    )


def downgrade():
    raise NotImplementedError("downgrade is not implemented")
'''

BATCH_MIGRATION = '''"""batch add column"""
from alembic import op
import sqlalchemy as sa

revision = "0003"
down_revision = "0002"
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table("account") as batch_op:
        batch_op.add_column(sa.Column("note", sa.String(200), nullable=True))


def downgrade():
    with op.batch_alter_table("account") as batch_op:
        batch_op.drop_column("note")
'''


# --- Non-happy-path tests ---

def test_empty_database_upgrade_head_applies_all_migrations(tmp_path):
    db_url = f"sqlite:///{tmp_path / 'migrations.db'}"
    cfg = make_config(db_url)

    command.upgrade(cfg, "head")

    engine = create_engine(db_url)
    inspector = inspect(engine)
    assert "account" in inspector.get_table_names()
    assert "alembic_version" in inspector.get_table_names()
    assert get_version(engine) == "0002"
    assert {"id", "email", "name", "balance"} <= get_columns(engine, "account")


def test_downgrade_then_upgrade_roundtrip(tmp_path):
    db_url = f"sqlite:///{tmp_path / 'migrations.db'}"
    cfg = make_config(db_url)
    command.upgrade(cfg, "head")

    command.downgrade(cfg, "-1")
    engine = create_engine(db_url)
    assert get_version(engine) == "0001"
    assert "balance" not in get_columns(engine, "account")

    command.upgrade(cfg, "head")
    assert get_version(engine) == "0002"
    assert "balance" in get_columns(engine, "account")


def test_modifying_applied_migration_raises_checksum_error(tmp_path):
    db_url = f"sqlite:///{tmp_path / 'migrations.db'}"
    cfg = make_config(db_url)
    command.upgrade(cfg, "head")
    engine = create_engine(db_url)
    checksum_guard.record_checksums(engine, VERSIONS_DIR)

    migration_file = VERSIONS_DIR / "0001_create_account.py"
    original = migration_file.read_text()
    try:
        migration_file.write_text(original + "\n# modified after application\n")
        with pytest.raises(RuntimeError):
            checksum_guard.verify_checksums(engine, VERSIONS_DIR)
    finally:
        migration_file.write_text(original)


def test_failed_migration_is_not_recorded_as_applied(tmp_path):
    # SQLite through SQLAlchemy does not roll back DDL statements, so a
    # failing migration can leave partial DDL behind on SQLite. On PostgreSQL
    # (Flyway's target database) transactional DDL rolls back the entire
    # migration. The invariant tested here is that the failed migration is
    # never recorded in the version table, so the next upgrade retries it.
    db_url = f"sqlite:///{tmp_path / 'migrations.db'}"
    cfg = make_config(db_url)
    bad_file = VERSIONS_DIR / "0003_bad.py"
    bad_file.write_text(BAD_MIGRATION)
    try:
        with pytest.raises(Exception):
            command.upgrade(cfg, "head")

        engine = create_engine(db_url)
        assert get_version(engine) == "0002"
    finally:
        bad_file.unlink(missing_ok=True)


def test_duplicate_revision_raises_conflict(tmp_path):
    db_url = f"sqlite:///{tmp_path / 'migrations.db'}"
    cfg = make_config(db_url)
    file_a = VERSIONS_DIR / "0003_a.py"
    file_b = VERSIONS_DIR / "0003_b.py"
    file_a.write_text(DUP_A)
    file_b.write_text(DUP_B)
    try:
        with pytest.raises(Exception):
            command.upgrade(cfg, "head")
    finally:
        file_a.unlink(missing_ok=True)
        file_b.unlink(missing_ok=True)


def test_missing_migration_file_is_not_silently_skipped(tmp_path):
    db_url = f"sqlite:///{tmp_path / 'migrations.db'}"
    cfg = make_config(db_url)
    command.upgrade(cfg, "head")

    migration_file = VERSIONS_DIR / "0002_add_balance_column.py"
    backup = migration_file.with_suffix(".py.bak")
    migration_file.rename(backup)
    try:
        with pytest.raises(Exception):
            command.upgrade(cfg, "head")
    finally:
        backup.rename(migration_file)


def test_not_null_column_without_default_fails_on_populated_table(tmp_path):
    db_url = f"sqlite:///{tmp_path / 'migrations.db'}"
    cfg = make_config(db_url)
    command.upgrade(cfg, "head")

    engine = create_engine(db_url)
    with engine.begin() as conn:
        conn.execute(
            text("INSERT INTO account (email, name) VALUES ('a@example.com', 'A')")
        )

    migration_file = VERSIONS_DIR / "0003_add_required.py"
    migration_file.write_text(ADD_REQUIRED_COLUMN)
    try:
        with pytest.raises(Exception):
            command.upgrade(cfg, "head")
        assert "new_required" not in get_columns(engine, "account")
    finally:
        migration_file.unlink(missing_ok=True)


def test_migration_without_downgrade_cannot_be_reverted(tmp_path):
    db_url = f"sqlite:///{tmp_path / 'migrations.db'}"
    cfg = make_config(db_url)
    migration_file = VERSIONS_DIR / "0003_no_downgrade.py"
    migration_file.write_text(NO_DOWNGRADE)
    try:
        command.upgrade(cfg, "head")
        with pytest.raises(NotImplementedError):
            command.downgrade(cfg, "0002")
    finally:
        migration_file.unlink(missing_ok=True)


def test_batch_alter_table_handles_large_table(tmp_path):
    db_url = f"sqlite:///{tmp_path / 'migrations.db'}"
    cfg = make_config(db_url)
    command.upgrade(cfg, "head")

    engine = create_engine(db_url)
    with engine.begin() as conn:
        for i in range(1000):
            conn.execute(
                text("INSERT INTO account (email, name) VALUES (:email, :name)"),
                {"email": f"user{i}@example.com", "name": f"User{i}"},
            )

    migration_file = VERSIONS_DIR / "0003_batch.py"
    migration_file.write_text(BATCH_MIGRATION)
    try:
        command.upgrade(cfg, "head")
        assert "note" in get_columns(engine, "account")
    finally:
        migration_file.unlink(missing_ok=True)


def test_concurrent_upgrade_with_lock_leaves_consistent_schema(tmp_path):
    # Flyway serializes concurrent migrations with a database level lock.
    # This thread lock is the process level stand-in for that lock.
    db_url = f"sqlite:///{tmp_path / 'concurrent.db'}"
    lock = threading.Lock()

    def run_upgrade():
        with lock:
            command.upgrade(make_config(db_url), "head")

    threads = [threading.Thread(target=run_upgrade) for _ in range(2)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()

    engine = create_engine(db_url)
    inspector = inspect(engine)
    assert "account" in inspector.get_table_names()
    assert {"id", "email", "name", "balance"} <= get_columns(engine, "account")
    assert get_version(engine) == "0002"
