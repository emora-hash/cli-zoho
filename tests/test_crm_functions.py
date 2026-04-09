"""Tests for CRM Functions client — execute standalone Deluge functions via REST API."""

from unittest.mock import MagicMock, call

import pytest

from cli_zoho.crm.zoho_cli_crm_functions import FunctionsClient


def _mock_resp(payload, status_code=200):
    resp = MagicMock()
    resp.status_code = status_code
    resp.json.return_value = payload
    resp.raise_for_status = MagicMock()
    return resp


class TestFunctionsClient:
    def setup_method(self):
        self.auth = MagicMock()
        self.client = FunctionsClient(self.auth)

    def test_execute_success(self):
        """POST with apikey auth (default) — URL and params are correct."""
        payload = {"code": "success", "details": {"output": "pong"}}
        self.auth.request.return_value = _mock_resp(payload)

        result = self.client.execute("test_ping", api_key="testapikey123")

        call_args = self.auth.request.call_args
        method, url = call_args[0]
        params = call_args[1]["params"]

        assert method == "POST"
        assert "/crm/v7/functions/test_ping/actions/execute" in url
        assert params["auth_type"] == "apikey"
        assert params["zapikey"] == "testapikey123"
        assert result == payload

    def test_execute_with_arguments(self):
        """Arguments are sent as json={"arguments": {...}} for POST."""
        payload = {"code": "success", "details": {"output": "hello world"}}
        self.auth.request.return_value = _mock_resp(payload)

        args = {"name": "world", "greeting": "hello"}
        self.client.execute("test_fn", arguments=args, api_key="key")

        call_kwargs = self.auth.request.call_args[1]
        assert "json" in call_kwargs
        assert call_kwargs["json"] == {"arguments": args}

    def test_execute_get_method(self):
        """method='GET' uses GET HTTP method."""
        payload = {"code": "success", "details": {}}
        self.auth.request.return_value = _mock_resp(payload)

        self.client.execute("test_fn", method="GET", api_key="key")

        method = self.auth.request.call_args[0][0]
        assert method == "GET"

    def test_execute_oauth_auth(self):
        """auth_type='oauth' — no zapikey in params."""
        payload = {"code": "success", "details": {}}
        self.auth.request.return_value = _mock_resp(payload)

        self.client.execute("test_fn", auth_type="oauth")

        params = self.auth.request.call_args[1]["params"]
        assert params["auth_type"] == "oauth"
        assert "zapikey" not in params

    def test_execute_failure(self):
        """Function returning code='failure' is returned as-is (no exception raised)."""
        payload = {"code": "failure", "details": {"output": "error occurred"}}
        self.auth.request.return_value = _mock_resp(payload)

        result = self.client.execute("test_fn", api_key="key")

        assert result["code"] == "failure"
        assert result == payload

    def test_execute_uses_v7_endpoint(self):
        """URL contains /crm/v7/ not /crm/v8/."""
        payload = {"code": "success", "details": {}}
        self.auth.request.return_value = _mock_resp(payload)

        self.client.execute("any_fn", api_key="key")

        url = self.auth.request.call_args[0][1]
        assert "/crm/v7/" in url
        assert "/crm/v8/" not in url
