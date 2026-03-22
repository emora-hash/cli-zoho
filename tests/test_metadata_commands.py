"""Tests for CRM metadata Click commands — layouts, views, related-lists."""

import json
from unittest.mock import MagicMock, patch

from cli_zoho.auth import ZohoAuth
from cli_zoho.main import cli


def _mock_resp(payload, status_code=200):
    resp = MagicMock()
    resp.status_code = status_code
    resp.json.return_value = payload
    resp.raise_for_status = MagicMock()
    return resp


# ---------------------------------------------------------------------------
# Layouts
# ---------------------------------------------------------------------------

class TestLayoutsList:
    def test_list_json(self, runner):
        payload = {
            "layouts": [
                {"id": "l1", "name": "Standard", "status": "active"},
                {"id": "l2", "name": "Custom", "status": "active"},
            ]
        }
        with patch.object(ZohoAuth, "refresh", return_value="t"):
            with patch.object(ZohoAuth, "request", return_value=_mock_resp(payload)):
                result = runner.invoke(cli, ["crm", "layouts", "list", "Deals", "--json"])

        assert result.exit_code == 0
        data = json.loads(result.output)
        # metadata_commands compacts to list of {id, name, status}
        assert isinstance(data, list)
        assert len(data) == 2
        assert data[0]["id"] == "l1"
        assert data[0]["name"] == "Standard"
        assert data[0]["status"] == "active"

    def test_list_table_output(self, runner):
        payload = {"layouts": [{"id": "l1", "name": "Standard", "status": "active"}]}
        with patch.object(ZohoAuth, "refresh", return_value="t"):
            with patch.object(ZohoAuth, "request", return_value=_mock_resp(payload)):
                result = runner.invoke(cli, ["crm", "layouts", "list", "Deals"])

        assert result.exit_code == 0

    def test_list_missing_module_arg(self, runner):
        with patch.object(ZohoAuth, "refresh", return_value="t"):
            result = runner.invoke(cli, ["crm", "layouts", "list"])
        assert result.exit_code != 0


class TestLayoutsGet:
    def test_get_json(self, runner):
        # get_layout returns layouts[0] — a single dict
        payload = {
            "layouts": [
                {
                    "id": "l1",
                    "name": "Standard",
                    "status": "active",
                    "sections": [{"name": "Basic Info", "fields": []}],
                }
            ]
        }
        with patch.object(ZohoAuth, "refresh", return_value="t"):
            with patch.object(ZohoAuth, "request", return_value=_mock_resp(payload)):
                result = runner.invoke(cli, ["crm", "layouts", "get", "Deals", "l1", "--json"])

        assert result.exit_code == 0
        data = json.loads(result.output)
        assert data["id"] == "l1"
        assert data["name"] == "Standard"
        assert "sections" in data

    def test_get_missing_args(self, runner):
        with patch.object(ZohoAuth, "refresh", return_value="t"):
            result = runner.invoke(cli, ["crm", "layouts", "get", "Deals"])
        assert result.exit_code != 0


# ---------------------------------------------------------------------------
# Custom Views
# ---------------------------------------------------------------------------

class TestViewsList:
    def test_list_json(self, runner):
        payload = {
            "custom_views": [
                {"id": "v1", "name": "All Deals", "system_name": "All"},
                {"id": "v2", "name": "My Deals", "system_name": "My"},
            ]
        }
        with patch.object(ZohoAuth, "refresh", return_value="t"):
            with patch.object(ZohoAuth, "request", return_value=_mock_resp(payload)):
                result = runner.invoke(cli, ["crm", "views", "list", "Deals", "--json"])

        assert result.exit_code == 0
        data = json.loads(result.output)
        # metadata_commands compacts to list of {id, name, system_name}
        assert isinstance(data, list)
        assert len(data) == 2
        assert data[0]["id"] == "v1"
        assert data[0]["system_name"] == "All"

    def test_list_table_output(self, runner):
        payload = {"custom_views": [{"id": "v1", "name": "All Deals", "system_name": "All"}]}
        with patch.object(ZohoAuth, "refresh", return_value="t"):
            with patch.object(ZohoAuth, "request", return_value=_mock_resp(payload)):
                result = runner.invoke(cli, ["crm", "views", "list", "Deals"])

        assert result.exit_code == 0

    def test_list_missing_module_arg(self, runner):
        with patch.object(ZohoAuth, "refresh", return_value="t"):
            result = runner.invoke(cli, ["crm", "views", "list"])
        assert result.exit_code != 0


class TestViewsGet:
    def test_get_json(self, runner):
        # get_custom_view returns custom_views[0] — a single dict
        payload = {
            "custom_views": [
                {
                    "id": "v1",
                    "name": "All Deals",
                    "system_name": "All",
                    "criteria": {"comparator": "and", "conditions": []},
                }
            ]
        }
        with patch.object(ZohoAuth, "refresh", return_value="t"):
            with patch.object(ZohoAuth, "request", return_value=_mock_resp(payload)):
                result = runner.invoke(cli, ["crm", "views", "get", "Deals", "v1", "--json"])

        assert result.exit_code == 0
        data = json.loads(result.output)
        assert data["id"] == "v1"
        assert data["name"] == "All Deals"
        assert "criteria" in data

    def test_get_missing_args(self, runner):
        with patch.object(ZohoAuth, "refresh", return_value="t"):
            result = runner.invoke(cli, ["crm", "views", "get", "Deals"])
        assert result.exit_code != 0


# ---------------------------------------------------------------------------
# Related Lists
# ---------------------------------------------------------------------------

class TestRelatedListsList:
    def test_list_json(self, runner):
        payload = {
            "related_lists": [
                {"api_name": "Contacts", "name": "Contacts", "module": {"api_name": "Contacts"}},
                {"api_name": "Activities", "name": "Activities", "module": {"api_name": "Activities"}},
            ]
        }
        with patch.object(ZohoAuth, "refresh", return_value="t"):
            with patch.object(ZohoAuth, "request", return_value=_mock_resp(payload)):
                result = runner.invoke(cli, ["crm", "related-lists", "list", "Deals", "--json"])

        assert result.exit_code == 0
        data = json.loads(result.output)
        # metadata_commands compacts to list of {api_name, name, module}
        assert isinstance(data, list)
        assert len(data) == 2
        assert data[0]["api_name"] == "Contacts"
        assert data[0]["module"] == "Contacts"

    def test_list_table_output(self, runner):
        payload = {
            "related_lists": [
                {"api_name": "Contacts", "name": "Contacts", "module": {"api_name": "Contacts"}}
            ]
        }
        with patch.object(ZohoAuth, "refresh", return_value="t"):
            with patch.object(ZohoAuth, "request", return_value=_mock_resp(payload)):
                result = runner.invoke(cli, ["crm", "related-lists", "list", "Deals"])

        assert result.exit_code == 0

    def test_list_missing_module_arg(self, runner):
        with patch.object(ZohoAuth, "refresh", return_value="t"):
            result = runner.invoke(cli, ["crm", "related-lists", "list"])
        assert result.exit_code != 0

    def test_list_empty_module_field(self, runner):
        """Related list entries with missing module dict should not crash."""
        payload = {
            "related_lists": [
                {"api_name": "Notes", "name": "Notes"},  # no 'module' key
            ]
        }
        with patch.object(ZohoAuth, "refresh", return_value="t"):
            with patch.object(ZohoAuth, "request", return_value=_mock_resp(payload)):
                result = runner.invoke(cli, ["crm", "related-lists", "list", "Deals", "--json"])

        assert result.exit_code == 0
        data = json.loads(result.output)
        assert data[0]["module"] == ""
