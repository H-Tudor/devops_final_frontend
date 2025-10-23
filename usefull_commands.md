# Usefull comands

## Docker container

### Build the image

```sh
docker build . -t tudor0h/devops_final_frontend:latest
```

### Run the container

```sh
docker run --env-file .env.devops_final_frontend -p 8000:80 tudor0h/devops_final_backend:latest
```

## Pre-Commit Hooks

### Install

```sh
uv run pre-commit install && uv run pre-commit install-hooks
```

### Run

```sh
uv run pre-commit run --all-files
```

## Compile the [requirements.txt](requirements.txt)

```sh
uv export -o requirements.txt --no-header --no-hashes
```

## Lint files with ruff

```sh
uv run ruff check
uv run ruff format
uv run ruff clear
```

## Lint files with mypy

```sh
uv run mypy .
```

## Lint files with pylint

```sh
uv run pylint src/devops_final_frontend
```
