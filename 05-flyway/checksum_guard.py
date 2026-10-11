"""Checksum guard that mimics Flyway's migration checksum protection.

Flyway stores a checksum for every applied migration and refuses to continue
if a previously applied migration file changes. Alembic does not store
checksums by default, so this module adds the same protection on top.
"""

import hashlib
from pathlib import Path

from sqlalchemy import create_engine, text


def compute_checksum(file_path) -> str:
    return hashlib.sha256(Path(file_path).read_bytes()).hexdigest()


def ensure_checksum_table(engine) -> None:
    with engine.begin() as conn:
        conn.execute(
            text(
                "CREATE TABLE IF NOT EXISTS migration_checksum "
                "(version VARCHAR(32) PRIMARY KEY, checksum VARCHAR(64) NOT NULL)"
            )
        )


def record_checksums(engine, versions_dir: Path) -> None:
    ensure_checksum_table(engine)
    with engine.begin() as conn:
        for file_path in sorted(versions_dir.glob("*.py")):
            version = file_path.stem.split("_")[0]
            checksum = compute_checksum(file_path)
            conn.execute(
                text(
                    "INSERT OR REPLACE INTO migration_checksum "
                    "(version, checksum) VALUES (:version, :checksum)"
                ),
                {"version": version, "checksum": checksum},
            )


def verify_checksums(engine, versions_dir: Path) -> None:
    ensure_checksum_table(engine)
    with engine.connect() as conn:
        rows = conn.execute(
            text("SELECT version, checksum FROM migration_checksum")
        ).all()

    current = {
        p.stem.split("_")[0]: compute_checksum(p)
        for p in sorted(versions_dir.glob("*.py"))
    }

    for version, stored_checksum in rows:
        if version not in current:
            raise RuntimeError(
                f"Applied migration file for revision {version} is missing"
            )
        if stored_checksum != current[version]:
            raise RuntimeError(f"Checksum mismatch for migration {version}")
