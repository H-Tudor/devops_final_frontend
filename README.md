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

