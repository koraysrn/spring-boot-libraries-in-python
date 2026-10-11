# spring-boot-maven-plugin

A Python implementation of the packaging provided by `spring-boot-maven-plugin`. This module packages the application into a single runnable unit using Docker, the Python equivalent of a Spring Boot executable JAR.

## Overview

In Spring Boot, `spring-boot-maven-plugin` packages the application into one executable JAR that contains Tomcat and everything else. Running `java -jar finance.jar` starts the application anywhere.

| Spring Boot Concept | Python Equivalent |
|---|---|
| Executable JAR | Docker image |
| `java -jar finance.jar` | `docker run -p 8080:8080 finance` |
| Maven build | `docker build` |

## Features

- Multi-stage Docker build using a slim base image.
- Dependencies installed in a virtual environment in the build stage.
- Runtime stage copies only the virtual environment and application code.
- Non-root user for the container.
- Pinned dependencies for reproducible builds.
- `.dockerignore` excluding derived and sensitive files.
- Validation of the Docker artifacts without requiring Docker.

## Project Structure

```
14-maven-plugin/
├── Dockerfile               # Multi-stage build
├── .dockerignore            # Files excluded from the build context
├── requirements.txt         # Pinned application dependencies
├── requirements-dev.txt     # Test dependencies
├── packaging.py             # Packaging validation
├── app/
│   └── main.py              # Minimal FastAPI application
├── conftest.py
└── tests/
    └── test_packaging.py
```

## Requirements

- Python 3.12 or newer
- pip
- Docker, to build the image

## Build and Run

```bash
docker build -t finance .
docker run -p 8080:8080 finance
```

## Testing

```bash
python -m venv .venv
.venv\Scripts\activate        # Windows
pip install -r requirements-dev.txt
pytest -v
```

The test suite focuses on non-happy-path scenarios. It verifies that an empty Dockerfile raises a clear error, that an unpinned requirement raises, that missing `.dockerignore` patterns raise, that the real Dockerfile passes validation, that the requirements are pinned, that the container runs as a non-root user, that the Dockerfile uses a slim multi-stage build, that it defines a port and a startup command, that parsing is deterministic, and that the packaged application responds to a health check.
