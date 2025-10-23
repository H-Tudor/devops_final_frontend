# DevOps Final Fronted - LLM Compose Generator

Transform a loose list of services in a full docker compose file with the power of AI

## About

This is a Streamlit-based Web-UI for the `devops-final-backend`, thus it contains
the user interface as declarative python code with an abstracted websocket-based
backend where the user state is stored as a temporary session state.

For more information on how streamlit works, see the [official documentation](https://docs.streamlit.io/)

This application heavily depends on the backend API and the associated auth providers (keycloack instances) and such should they be unavailable the web interface will display a standard error
"Service Temporarily Unavailable"

## Setup

In terms of external software this application requires a backend instance of
the LLM generator API (with the appropriate keycloack instance) and a keycloack
instance for the frontend with a realm with a confidential client setup with standard
flow and user accounts for the intended audience

**Note**: keycloack allowes users to create their own accounts, but depending on the
intended use-case, you might want to keep that option disabled (as per default)

### 1. Install Dependencies

```sh
uv sync
```

or

```sh
uv venv
uv pip install r
```

### 2. Setup secrets file

Within the `.streamlit` folder there is a template file called `secrets.toml.example`.
Use the template to create `secrets.toml` and populate it with the appropiate values.

## Running the app

In order to run the app you have 2 options:

```sh
uv run streamlit run src/devops_final_frontend/view.py
```

or you can use a convenience script

```sh
uv run devops-final-frontend
```

## Testing

Run the unit & integration tests using the following command:

```sh
uv pytest
```

The API is tested using schemathesis and during testing it requires an available keycloak instance
and configured in settings a test_username and test_password

## Developer Notes

### PreCommit Strategy

This repository is configured with a precommit configuration comprised of the following stages:

Generic precommit checks:
- trim trailing whitespace
- fix end of files
- check for added large files

Code linting using
- ruff check & format
- mypy
- pylint

These linter cover not just the code but typing and docs too, thus ensuring the developer has documented their code.

Automation of manual actions
- running the unit tests using pytest, to ensure that when commiting a code change it is atomically functional
- clearing the caches
- exporting the requirements file if packages changed

As a developer, in order to prevent commit failures, you should manually run these checks before commiting the code using

```sh
uv run pre-commit run --all-files
```
