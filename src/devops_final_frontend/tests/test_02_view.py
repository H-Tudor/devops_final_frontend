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
def test_api_ok(mock_api_service):
    """Error should not be shown if both external api dependencies are ok"""

    mock_api_service.health_check.return_value = True
    at = AppTest.from_file("../view.py").run()

    assert len(at.columns) == 2
    assert len(at.columns[0].error) == 0


# pylint: disable=redefined-outer-name
def test_api_unavailable(mock_api_service):
    """Error should not be shown if both external api dependencies are ok"""

    mock_api_service.health_check.return_value = False
    at = AppTest.from_file("../view.py").run()

    assert len(at.columns) == 2
    assert len(at.columns[0].error) == 1
