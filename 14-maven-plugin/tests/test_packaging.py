"""
Non-happy-path tests for the spring-boot-maven-plugin equivalent (Docker).
"""

import pathlib

import pytest
from fastapi.testclient import TestClient

import packaging

BASE_DIR = pathlib.Path(__file__).resolve().parent.parent

DOCKERFILE = (BASE_DIR / "Dockerfile").read_text()
DOCKERIGNORE = (BASE_DIR / ".dockerignore").read_text()
REQUIREMENTS = (BASE_DIR / "requirements.txt").read_text()


def test_empty_dockerfile_raises_clear_error():
    with pytest.raises(ValueError, match="empty or missing"):
        packaging.validate_dockerfile("")


def test_unpinned_requirement_raises():
    with pytest.raises(ValueError, match="not pinned"):
        packaging.validate_requirements("fastapi\n")


def test_missing_dockerignore_patterns_raise():
    with pytest.raises(ValueError, match="missing patterns"):
        packaging.validate_dockerignore("# no patterns here\n")


def test_real_dockerfile_passes_validation():
    packaging.validate_dockerfile(DOCKERFILE)


def test_real_requirements_are_pinned():
    packaging.validate_requirements(REQUIREMENTS)


def test_real_dockerignore_passes_validation():
    packaging.validate_dockerignore(DOCKERIGNORE)


def test_dockerfile_runs_as_non_root():
    lines = packaging.parse_dockerfile(DOCKERFILE)
    user_lines = [line for line in lines if line.startswith("USER ")]
    assert user_lines
    assert "USER root" not in user_lines


def test_dockerfile_uses_slim_multi_stage():
    lines = packaging.parse_dockerfile(DOCKERFILE)
    from_lines = [line for line in lines if line.startswith("FROM ")]
    assert len(from_lines) >= 2
    assert all("slim" in line for line in from_lines)


def test_dockerfile_defines_port_and_command():
    lines = packaging.parse_dockerfile(DOCKERFILE)
    assert any(line.startswith("EXPOSE ") for line in lines)
    assert any(line.startswith("CMD ") for line in lines)


def test_same_source_parses_deterministically():
    first = packaging.parse_dockerfile(DOCKERFILE)
    second = packaging.parse_dockerfile(DOCKERFILE)
    assert first == second


def test_app_runs_in_clean_environment():
    from app.main import app

    client = TestClient(app)
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"
