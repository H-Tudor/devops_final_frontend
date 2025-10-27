"""View Module

The user interface rendering using streamlit
"""

import io
import zipfile
from datetime import datetime

import httpx
import streamlit as st

from devops_final_frontend.api import ApiService, ResponseType
from devops_final_frontend.models import Api, Auth, Token

st.set_page_config(page_title="App", layout="wide")

API_PARAMS = Api(**st.secrets["backend"])
AUTH_PARAMS = Auth(**st.secrets["backend"]["auth"])
TOKEN = Token(**st.session_state["auth"]) if "auth" in st.session_state else None

api = ApiService(API_PARAMS, AUTH_PARAMS, TOKEN)
buf = io.BytesIO()

API_AVAILABLE = api.is_api_up()
AUTH_AVAILABLE = api.is_keycloak_up()
SERVICE_AVAILABLE = API_AVAILABLE and AUTH_AVAILABLE


def init_download_buffer():
    """
    On page load, if the LLM generated a configuration, create a in-memory zip archive
    of the docker compose file and env files which can be downloaded by the download button
    """
    if not st.session_state.get("docker-compose", {}):
        return

    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as zf:
        zf.writestr("compose.yml", st.session_state["docker-compose"])
        for generated_env in st.session_state.get("envs", []):
            zf.writestr(generated_env["title"], generated_env["body"])

    buf.seek(0)


def service_update(service_key, service_idx):
    """
    State change function for the dynamic service input list
    """
    st.session_state["services"][service_idx] = st.session_state[service_key]
    st.session_state["last_empty"] = not bool(st.session_state.get("services", [""])[-1])
    st.session_state["is_default"] = len(st.session_state.get("services")) == 1 and not bool(
        st.session_state.get("services", [""])[0]
    )


def get_compose():
    """
    Invoke the API call and load the results into session state
    """
    now = datetime.now()
    if st.user.get("exp", 0) < now.timestamp() or st.session_state["auth"]["access_exp"] < now:
        st.rerun()

    with st.spinner("LLM generation in progress, please wait", show_time=True):
        st.session_state["envs"] = []

        try:
            result_data = api.get_compose_get(st.session_state)
        except KeyError as kerr:
            st.error(f"Internal System Error - Key Error: {kerr}")
            st.rerun()
        except httpx.HTTPError:
            st.error("Service failed to respond.")
            st.rerun()

        for result in result_data:
            if result["type"] == ResponseType.COMPOSE_FILE.value:
                st.session_state["docker-compose"] = result["data"]
            elif result["type"] == ResponseType.ENV_FILE.value:
                st.session_state["envs"].append({"title": result["name"], "body": result["data"]})


header_left, header_right = st.columns([6, 1])
with header_left:
    st.title("Devops Final - LLM Compose Generator")
    st.write("Automate the creation of docker compose configurations using the power of LLM")

    if not SERVICE_AVAILABLE:
        st.error("Service Temporarily Unavailable")
        st.stop()

    user_exp = int(st.user.get("exp") or 0)
    if st.user.get("is_logged_in", False) and user_exp < datetime.now().timestamp():
        st.logout()

    if not st.user.get("is_logged_in", False):
        st.subheader("Login Required")
        st.write("Currently this is a private system.")
        st.write("In order to apply, contact admin at: compose@test.trakosoft.ro")

        if st.button("Log in"):
            st.login("keycloak")

        st.stop()

with header_right:
    user_left, user_right = cols = st.columns([1, 1], gap=None, width=500)
    user_left.write(f"User: {st.user.name}")
    if user_right.button("Logout"):
        st.logout()
        st.stop()

# APP backend auth
if not TOKEN:
    try:
        st.session_state["auth"] = api.get_token().model_dump()
        st.rerun()
    except httpx.HTTPError:
        st.error("Service Temporarily Unavailable")
        st.stop()

else:
    if TOKEN.refresh_exp <= datetime.now():
        del st.session_state["auth"]
        st.rerun()

    if TOKEN.access_exp <= datetime.now():
        try:
            st.session_state["auth"] = api.get_token().model_dump()
            st.rerun()
        except httpx.HTTPError:
            st.error("Service Temporarily Unavailable")
            st.stop()
    buf = io.BytesIO()


st.divider()
services, results = st.columns([1, 2])
with services:
    init_download_buffer()
    if not st.session_state.get("services", []):
        st.session_state["services"] = [""]
        st.session_state["first_empty"] = True
        st.session_state["last_empty"] = True

    if not st.session_state.get("network"):
        st.session_state["network"] = {"name": "", "exists": False}

    for i in range(len(st.session_state.get("services", [])) - 1, 1, -1):
        if not st.session_state["services"][i] and not st.session_state["services"][i - 1]:
            st.session_state["services"].pop(i)

    st.subheader("Input Services")

    buttons = st.columns([1, 1, 1, 1])
    if buttons[0].button(
        "Clear", icon=":material/delete:", disabled=st.session_state.get("is_default", True), width="stretch"
    ):
        st.session_state["services"] = [""]
        st.session_state["last_empty"] = not bool(st.session_state.get("services", [""])[-1])
        st.rerun()

    if buttons[1].button(
        "Add", icon=":material/add:", disabled=st.session_state.get("last_empty", True), width="stretch"
    ):
        st.session_state["services"].append("")
        st.session_state["last_empty"] = not bool(st.session_state.get("services", [""])[-1])
        st.rerun()

    if buttons[2].button(
        "Generate", icon=":material/send:", disabled=st.session_state.get("last_empty", True), width="stretch"
    ):
        get_compose()

    buttons[3].download_button(
        label="Download",
        icon=":material/download:",
        data=buf,
        file_name="compose_export.zip",
        mime="application/zip",
        disabled=not st.session_state.get("docker-compose", {}),
        width="stretch",
    )

    st.session_state["network"]["name"] = services.text_input(
        label="Docker Network", help="Specify the Docker network to use for these services."
    )

    toggles = services.columns([1, 1], gap=None)
    st.session_state["network"]["exists"] = toggles[0].toggle(
        label="Network Already Exists",
        help="Enable if the network is already created and managed externally. "
        + "Disable to create and manage a new network within this project.",
        width="stretch",
    )
    st.session_state["volume_mount"] = not toggles[1].toggle(
        label="Mount Volumes in Project Folder",
        help="Enable to mount volumes inside this project's local directory. "
        + "Disable to mount them in Docker's default volume directory.",
        width="stretch",
    )

    for idx, val in enumerate(st.session_state["services"]):
        key = f"{idx}_{datetime.now().timestamp()}"
        service = st.columns([7, 1])
        service[0].text_input(
            label=f"Service {idx + 1}",
            value=val,
            key=f"svc_{key}",
            max_chars=64,
            on_change=service_update,
            args=(f"svc_{key}", idx),
        )
        if service[1].button("❌", key=f"del_{key}"):
            st.session_state["services"].pop(idx)
            st.rerun()

with results:
    if not st.session_state.get("docker-compose", ""):
        st.stop()

    compose, envs = results.columns(2, border=True)
    with compose:
        st.subheader("Docker Compose File")
        st.code(body=st.session_state["docker-compose"], language="yaml")

    with envs:
        st.subheader("Service Environment Files")
        st.warning(
            "AI Models might have deprecated knowledge, some configuration data such as environment variables"
            "might be outdated, be sure to cross-reference the official documentation"
        )

        for env in st.session_state.get("envs", []):
            st.write(env["title"])
            st.code(env["body"], language="ini")
