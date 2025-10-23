"""API tests

Check if error cases are treated on api call
"""

# pylint: disable=redefined-outer-name,missing-function-docstring

from datetime import datetime

import httpx
import pytest

from devops_final_frontend.api import Api, ApiService, Auth, Token


@pytest.fixture
def api():
    return Api(host="http://api", version="v1")


@pytest.fixture
def auth():
    return Auth(
        host="http://auth",
        aux_host="http://aux",
        realm="dev",
        username="u",
        password="p",
        client_id="cid",
        client_secret="sec",
    )


@pytest.fixture
def token():
    return Token(access_token="a", refresh_token="r", access_exp=datetime.now(), refresh_exp=datetime.now())


@pytest.fixture
def service(api, auth, token):
    return ApiService(api, auth, token)


def test_is_api_up_ok(mocker, service):
    client = mocker.patch("httpx.Client")
    client.return_value.__enter__.return_value.get.return_value = True
    assert service.is_api_up() is True


def test_is_api_up_fail(mocker, service):
    client = mocker.patch("httpx.Client")
    client.return_value.__enter__.return_value.get.side_effect = httpx.HTTPError("fail")
    assert service.is_api_up() is False


def test_is_keycloak_up_ok(mocker, service):
    resp = mocker.Mock()
    resp.raise_for_status.return_value = None
    client = mocker.patch("httpx.Client")
    client.return_value.__enter__.return_value.get.return_value = resp
    assert service.is_keycloak_up() is True


def test_is_keycloak_up_fail(mocker, service):
    client = mocker.patch("httpx.Client")
    client.return_value.__enter__.return_value.get.side_effect = httpx.HTTPError("fail")
    assert service.is_keycloak_up() is False


def test_get_compose_get_ok(mocker, service):
    resp = mocker.Mock()
    resp.json.return_value = [{"ok": 1}]
    resp.raise_for_status.return_value = None
    client = mocker.patch("httpx.Client")
    client.return_value.__enter__.return_value.post.return_value = resp
    data = {"services": [], "network": {"name": "n", "exists": True}, "volume_mount": "/tmp"}
    assert service.get_compose_get(data) == [{"ok": 1}]


def test_get_compose_get_no_token(api, auth):
    s = ApiService(api, auth, None)
    with pytest.raises(httpx.HTTPError):
        s.get_compose_get({})


def test_get_token_ok(mocker, api, auth):
    data = {
        "access_token": "a",
        "refresh_token": "r",
        "expires_in": 100,
        "refresh_expires_in": 200,
    }
    resp = mocker.Mock()
    resp.raise_for_status.return_value = None
    resp.json.return_value = data
    client = mocker.patch("httpx.Client")
    client.return_value.__enter__.return_value.post.return_value = resp
    s = ApiService(api, auth, None)
    t = s.get_token()
    assert isinstance(t, Token)
    assert t.access_token == "a"


def test_refresh_token_ok(mocker, service):
    data = {
        "access_token": "a",
        "refresh_token": "r",
        "expires_in": 100,
        "refresh_expires_in": 200,
    }
    resp = mocker.Mock()
    resp.raise_for_status.return_value = None
    resp.json.return_value = data
    client = mocker.patch("httpx.Client")
    client.return_value.__enter__.return_value.post.return_value = resp
    t = service.refresh_token()
    assert isinstance(t, Token)
    assert t.refresh_token == "r"


def test_refresh_token_no_token(api, auth):
    s = ApiService(api, auth, None)
    with pytest.raises(httpx.HTTPError):
        s.refresh_token()
