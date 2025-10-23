"""View tests

Check app rendering logic

Note: this is incomplete since AppTest does not expose all the Streamlit features used.
"""

from unittest.mock import patch

import pytest
from streamlit.testing.v1 import AppTest


@pytest.fixture
def mock_api_service():
    """
    Prepare a patchable api service
    """
    with patch("devops_final_frontend.api.ApiService") as mock_service:
        instance = mock_service.return_value
        yield instance


# pylint: disable=redefined-outer-name
def test_api_up(mock_api_service):
    """Error should not be shown if both external api dependencies are ok"""

    mock_api_service.is_api_up.return_value = True
    mock_api_service.is_keycloak_up.return_value = True
    at = AppTest.from_file("../view.py").run()

    assert len(at.columns) == 2
    assert len(at.columns[0].error) == 0


# pylint: disable=redefined-outer-name
def test_no_external(mock_api_service):
    """Error should be shown if both apis are unavailable"""

    mock_api_service.is_api_up.return_value = False
    mock_api_service.is_keycloak_up.return_value = False
    at = AppTest.from_file("../view.py").run()

    assert len(at.columns) == 2
    assert len(at.columns[0].error) == 1


# pylint: disable=redefined-outer-name
def test_no_keycloak(mock_api_service):
    """Error should be shown if Keycloak individualy is unavailable"""
    mock_api_service.is_api_up.return_value = True
    mock_api_service.is_keycloak_up.return_value = False
    at = AppTest.from_file("../view.py").run()

    assert len(at.columns) == 2
    assert len(at.columns[0].error) == 1


# pylint: disable=redefined-outer-name
def test_no_api(mock_api_service):
    """Error should be shown if Backend API individualy is unavailable"""
    mock_api_service.is_api_up.return_value = False
    mock_api_service.is_keycloak_up.return_value = True
    at = AppTest.from_file("../view.py").run()

    assert len(at.columns) == 2
    assert len(at.columns[0].error) == 1
