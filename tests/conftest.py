"""Shared fixtures for cli-zoho tests."""

import pytest
from unittest.mock import MagicMock, patch
from click.testing import CliRunner

from cli_zoho.zoho_cli_auth import ZohoAuth
from cli_zoho.zoho_cli_main import cli


@pytest.fixture(autouse=True)
def mock_env(monkeypatch):
    """Set required env vars for all tests."""
    monkeypatch.setenv("ZOHO_CLIENT_ID", "test-client-id")
    monkeypatch.setenv("ZOHO_CLIENT_SECRET", "test-client-secret")
    monkeypatch.setenv("ZOHO_REFRESH_TOKEN", "test-refresh-token")
    monkeypatch.setenv("ZOHO_ORG_ID", "123456789")


@pytest.fixture
def runner():
    return CliRunner()


@pytest.fixture
def mock_auth():
    """A ZohoAuth with a pre-set token (no real HTTP)."""
    import time
    auth = ZohoAuth()
    auth._access_token = "fake-access-token"
    auth._token_expiry = time.time() + 3600
    return auth


@pytest.fixture
def invoke(runner):
    """Invoke CLI commands with mocked auth. Returns a helper function."""
    def _invoke(args, mock_response=None, status_code=200):
        mock_resp = MagicMock()
        mock_resp.status_code = status_code
        mock_resp.json.return_value = mock_response or {}
        mock_resp.headers = {}
        mock_resp.raise_for_status = MagicMock()

        with patch.object(ZohoAuth, "refresh", return_value="fake-token"):
            with patch.object(ZohoAuth, "request", return_value=mock_resp):
                result = runner.invoke(cli, args)
        return result
    return _invoke


def mock_resp(payload, status_code=200):
    """Create a mock HTTP response with given JSON payload."""
    resp = MagicMock()
    resp.status_code = status_code
    resp.json.return_value = payload
    resp.raise_for_status = MagicMock()
    resp.headers = {}
    return resp


# --- Sample API responses ---

@pytest.fixture
def crm_list_response():
    return {
        "data": [
            {"id": "111", "Deal_Name": "Test Deal", "Amount": 5000, "Stage": "Qualification"},
            {"id": "222", "Deal_Name": "Big Deal", "Amount": 25000, "Stage": "Closed Won"},
        ],
        "info": {"more_records": False, "count": 2, "page": 1, "per_page": 10},
    }


@pytest.fixture
def crm_single_response():
    return {
        "data": [{"id": "111", "Deal_Name": "Test Deal", "Amount": 5000, "Stage": "Qualification"}],
    }


@pytest.fixture
def crm_create_response():
    return {
        "data": [{"code": "SUCCESS", "details": {"id": "333"}, "message": "record added", "status": "success"}],
    }


@pytest.fixture
def crm_fields_response():
    return {
        "fields": [
            {"api_name": "Deal_Name", "field_label": "Deal Name", "data_type": "text", "system_mandatory": True},
            {"api_name": "Amount", "field_label": "Amount", "data_type": "currency", "system_mandatory": False},
            {"api_name": "Stage", "field_label": "Stage", "data_type": "picklist", "system_mandatory": True},
        ],
    }


@pytest.fixture
def crm_modules_response():
    return {
        "modules": [
            {"api_name": "Deals", "plural_label": "Deals", "generated_type": "default"},
            {"api_name": "Contacts", "plural_label": "Contacts", "generated_type": "default"},
            {"api_name": "Leads", "plural_label": "Leads", "generated_type": "default"},
        ],
    }


@pytest.fixture
def inv_list_response():
    return {
        "items": [
            {"item_id": "1001", "name": "Excavator Bucket 24in", "rate": 450.00},
            {"item_id": "1002", "name": "Hydraulic Hammer HB20", "rate": 2800.00},
        ],
        "page_context": {"has_more_page": False, "page": 1},
    }


@pytest.fixture
def inv_single_response():
    return {
        "item": {"item_id": "1001", "name": "Excavator Bucket 24in", "rate": 450.00, "sku": "EB-24"},
    }


@pytest.fixture
def coql_response():
    return {
        "data": [
            {"Last_Name": "Smith", "Email": "smith@example.com"},
            {"Last_Name": "Jones", "Email": "jones@example.com"},
        ],
        "info": {"more_records": False, "count": 2},
    }
