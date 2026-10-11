"""Packaging validation, the equivalent of spring-boot-maven-plugin checks.

spring-boot-maven-plugin packages the application into a single executable
JAR. The Python equivalent is a Docker image. This module validates the
Docker packaging artifacts without requiring Docker itself.
"""


def parse_dockerfile(content: str) -> list[str]:
    return [
        line.strip()
        for line in content.splitlines()
        if line.strip() and not line.strip().startswith("#")
    ]


def validate_dockerfile(content: str) -> None:
    if not content.strip():
        raise ValueError("Dockerfile is empty or missing")

    lines = parse_dockerfile(content)

    from_lines = [line for line in lines if line.startswith("FROM ")]
    if not from_lines:
        raise ValueError("Dockerfile must contain a FROM instruction")
    if not any("slim" in line for line in from_lines):
        raise ValueError("Dockerfile should use a slim base image")
    if len(from_lines) < 2:
        raise ValueError("Dockerfile should use a multi-stage build")

    if not any(line.startswith("EXPOSE ") for line in lines):
        raise ValueError("Dockerfile must expose a port with EXPOSE")

    if not any(
        line.startswith("CMD ") or line.startswith("ENTRYPOINT ") for line in lines
    ):
        raise ValueError("Dockerfile must define a startup command")

    user_lines = [line for line in lines if line.startswith("USER ")]
    if not user_lines or any(line == "USER root" for line in user_lines):
        raise ValueError("Dockerfile must run as a non-root user")


def validate_requirements(content: str) -> None:
    if not content.strip():
        raise ValueError("requirements.txt is empty")
    for line in content.splitlines():
        line = line.strip()
        if not line or line.startswith("#") or line.startswith("-r"):
            continue
        if "==" not in line:
            raise ValueError(f"Requirement is not pinned: {line}")


REQUIRED_DOCKERIGNORE = {".venv", "__pycache__", ".git", ".env"}


def validate_dockerignore(content: str) -> None:
    if not content.strip():
        raise ValueError(".dockerignore is empty or missing")
    patterns = {
        line.strip()
        for line in content.splitlines()
        if line.strip() and not line.strip().startswith("#")
    }
    missing = REQUIRED_DOCKERIGNORE - patterns
    if missing:
        raise ValueError(f".dockerignore is missing patterns: {sorted(missing)}")
