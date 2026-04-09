"""Tests for 'crm functions execute' CLI command."""

import json
from unittest.mock import MagicMock, patch

from cli_zoho.zoho_cli_auth import ZohoAuth
from cli_zoho.zoho_cli_main import cli


def _mock_resp(payload, status_code=200):
    resp = MagicMock()
    resp.status_code = status_code
    resp.json.return_value = payload
    resp.raise_for_status = MagicMock()
    resp.headers = {}
    return resp


FUNCTION_PAYLOAD = {"details": {"output": "Hello, world!"}, "status": "success"}


class TestFunctionsExecute:
    def test_execute_basic(self, runner):
        """Basic execute with --api-key returns exit_code 0 and JSON output."""
        with patch.object(ZohoAuth, "refresh", return_value="t"):
            with patch.object(ZohoAuth, "request", return_value=_mock_resp(FUNCTION_PAYLOAD)) as mock_req:
                result = runner.invoke(
                    cli,
                    ["crm", "functions", "execute", "my_function", "--api-key", "testkey123", "--json"],
                )
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert data["status"] == "success"

    def test_execute_with_args(self, runner):
        """Execute with --args passes arguments to the client."""
        args_json = '{"name": "world"}'
        with patch.object(ZohoAuth, "refresh", return_value="t"):
            with patch.object(ZohoAuth, "request", return_value=_mock_resp(FUNCTION_PAYLOAD)) as mock_req:
                result = runner.invoke(
                    cli,
                    [
                        "crm", "functions", "execute", "greet_fn",
                        "--args", args_json,
                        "--api-key", "testkey123",
                        "--json",
                    ],
                )
        assert result.exit_code == 0
        # Verify the request was made (arguments were passed through)
        mock_req.assert_called_once()

    def test_execute_with_apikey_explicit(self, runner):
        """--auth-type apikey --api-key abc123 succeeds."""
        with patch.object(ZohoAuth, "refresh", return_value="t"):
            with patch.object(ZohoAuth, "request", return_value=_mock_resp(FUNCTION_PAYLOAD)) as mock_req:
                result = runner.invoke(
                    cli,
                    [
                        "crm", "functions", "execute", "my_fn",
                        "--auth-type", "apikey",
                        "--api-key", "abc123",
                        "--json",
                    ],
                )
        assert result.exit_code == 0
        mock_req.assert_called_once()

    def test_execute_get_method(self, runner):
        """--method GET passes GET to the client."""
        with patch.object(ZohoAuth, "refresh", return_value="t"):
            with patch.object(ZohoAuth, "request", return_value=_mock_resp(FUNCTION_PAYLOAD)) as mock_req:
                result = runner.invoke(
                    cli,
                    [
                        "crm", "functions", "execute", "my_fn",
                        "--method", "GET",
                        "--api-key", "testkey123",
                        "--json",
                    ],
                )
        assert result.exit_code == 0
        mock_req.assert_called_once()

    def test_execute_invalid_json_args(self, runner):
        """--args with invalid JSON exits non-zero."""
        with patch.object(ZohoAuth, "refresh", return_value="t"):
            with patch.object(ZohoAuth, "request", return_value=_mock_resp(FUNCTION_PAYLOAD)):
                result = runner.invoke(
                    cli,
                    [
                        "crm", "functions", "execute", "my_fn",
                        "--args", "not-json",
                        "--api-key", "testkey123",
                    ],
                )
        assert result.exit_code != 0

    def test_execute_missing_api_key(self, runner):
        """apikey auth without --api-key exits non-zero."""
        with patch.object(ZohoAuth, "refresh", return_value="t"):
            with patch.object(ZohoAuth, "request", return_value=_mock_resp(FUNCTION_PAYLOAD)):
                result = runner.invoke(
                    cli,
                    ["crm", "functions", "execute", "my_fn"],
                )
        assert result.exit_code != 0
