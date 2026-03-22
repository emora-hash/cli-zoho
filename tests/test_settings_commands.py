"""Tests for CRM settings Click commands — pipelines, variables, org-settings."""

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
# Pipelines
# ---------------------------------------------------------------------------

class TestPipelinesList:
    def test_list_json(self, runner):
        # get_pipelines returns resp.json().get("pipeline", []) — a list
        payload = {
            "pipeline": [
                {"id": "p1", "display_value": "Default Pipeline", "child_available": False},
                {"id": "p2", "display_value": "Enterprise Pipeline", "child_available": True},
            ]
        }
        with patch.object(ZohoAuth, "refresh", return_value="t"):
            with patch.object(ZohoAuth, "request", return_value=_mock_resp(payload)):
                result = runner.invoke(cli, ["crm", "pipelines", "list", "--json"])

        assert result.exit_code == 0
        data = json.loads(result.output)
        assert isinstance(data, list)
        assert len(data) == 2
        assert data[0]["id"] == "p1"

    def test_list_with_layout_id_filter(self, runner):
        payload = {"pipeline": [{"id": "p1", "display_value": "Default Pipeline"}]}
        with patch.object(ZohoAuth, "refresh", return_value="t"):
            with patch.object(ZohoAuth, "request", return_value=_mock_resp(payload)):
                result = runner.invoke(cli, ["crm", "pipelines", "list", "--layout-id", "123456", "--json"])

        assert result.exit_code == 0

    def test_list_table_output(self, runner):
        payload = {"pipeline": [{"id": "p1", "display_value": "Default Pipeline"}]}
        with patch.object(ZohoAuth, "refresh", return_value="t"):
            with patch.object(ZohoAuth, "request", return_value=_mock_resp(payload)):
                result = runner.invoke(cli, ["crm", "pipelines", "list"])

        assert result.exit_code == 0


class TestPipelinesCreate:
    def test_create_json(self, runner):
        payload = {"pipeline": [{"code": "SUCCESS", "details": {"id": "p3"}, "status": "success"}]}
        with patch.object(ZohoAuth, "refresh", return_value="t"):
            with patch.object(ZohoAuth, "request", return_value=_mock_resp(payload)):
                result = runner.invoke(
                    cli,
                    ["crm", "pipelines", "create", "--data", '{"display_value": "New Pipeline"}', "--json"],
                )

        assert result.exit_code == 0
        data = json.loads(result.output)
        assert data["pipeline"][0]["status"] == "success"

    def test_create_invalid_json(self, runner):
        with patch.object(ZohoAuth, "refresh", return_value="t"):
            result = runner.invoke(cli, ["crm", "pipelines", "create", "--data", "not-json"])
        assert result.exit_code != 0

    def test_create_missing_data(self, runner):
        with patch.object(ZohoAuth, "refresh", return_value="t"):
            result = runner.invoke(cli, ["crm", "pipelines", "create"])
        assert result.exit_code != 0


class TestPipelinesUpdate:
    def test_update_json(self, runner):
        payload = {"pipeline": [{"code": "SUCCESS", "status": "success"}]}
        with patch.object(ZohoAuth, "refresh", return_value="t"):
            with patch.object(ZohoAuth, "request", return_value=_mock_resp(payload)):
                result = runner.invoke(
                    cli,
                    ["crm", "pipelines", "update", "p1", "--data", '{"display_value": "Renamed"}', "--json"],
                )

        assert result.exit_code == 0

    def test_update_invalid_json(self, runner):
        with patch.object(ZohoAuth, "refresh", return_value="t"):
            result = runner.invoke(cli, ["crm", "pipelines", "update", "p1", "--data", "bad"])
        assert result.exit_code != 0

    def test_update_missing_data(self, runner):
        with patch.object(ZohoAuth, "refresh", return_value="t"):
            result = runner.invoke(cli, ["crm", "pipelines", "update", "p1"])
        assert result.exit_code != 0


# ---------------------------------------------------------------------------
# Variables
# ---------------------------------------------------------------------------

class TestVariablesList:
    def test_list_json(self, runner):
        # get_variables returns resp.json().get("variables", []) — a list
        payload = {
            "variables": [
                {"id": "var1", "name": "Lead_Source_Budget", "api_name": "Lead_Source_Budget", "type": "text"},
                {"id": "var2", "name": "Max_Discount", "api_name": "Max_Discount", "type": "decimal"},
            ]
        }
        with patch.object(ZohoAuth, "refresh", return_value="t"):
            with patch.object(ZohoAuth, "request", return_value=_mock_resp(payload)):
                result = runner.invoke(cli, ["crm", "variables", "list", "--json"])

        assert result.exit_code == 0
        data = json.loads(result.output)
        assert isinstance(data, list)
        assert len(data) == 2
        assert data[0]["name"] == "Lead_Source_Budget"

    def test_list_empty_204(self, runner):
        """Variables returns 204 when none exist — should return empty list."""
        mock_resp = _mock_resp({})
        mock_resp.status_code = 204
        with patch.object(ZohoAuth, "refresh", return_value="t"):
            with patch.object(ZohoAuth, "request", return_value=mock_resp):
                result = runner.invoke(cli, ["crm", "variables", "list", "--json"])

        assert result.exit_code == 0

    def test_list_table_output(self, runner):
        payload = {"variables": [{"id": "var1", "name": "Budget"}]}
        with patch.object(ZohoAuth, "refresh", return_value="t"):
            with patch.object(ZohoAuth, "request", return_value=_mock_resp(payload)):
                result = runner.invoke(cli, ["crm", "variables", "list"])

        assert result.exit_code == 0


class TestVariablesCreate:
    def test_create_json(self, runner):
        payload = {"variables": [{"code": "SUCCESS", "details": {"id": "var3"}, "status": "success"}]}
        with patch.object(ZohoAuth, "refresh", return_value="t"):
            with patch.object(ZohoAuth, "request", return_value=_mock_resp(payload)):
                result = runner.invoke(
                    cli,
                    ["crm", "variables", "create", "--data", '{"name": "New_Var", "type": "text"}', "--json"],
                )

        assert result.exit_code == 0
        data = json.loads(result.output)
        assert data["variables"][0]["status"] == "success"

    def test_create_invalid_json(self, runner):
        with patch.object(ZohoAuth, "refresh", return_value="t"):
            result = runner.invoke(cli, ["crm", "variables", "create", "--data", "not-json"])
        assert result.exit_code != 0

    def test_create_missing_data(self, runner):
        with patch.object(ZohoAuth, "refresh", return_value="t"):
            result = runner.invoke(cli, ["crm", "variables", "create"])
        assert result.exit_code != 0


class TestVariablesUpdate:
    def test_update_json(self, runner):
        payload = {"variables": [{"code": "SUCCESS", "status": "success"}]}
        with patch.object(ZohoAuth, "refresh", return_value="t"):
            with patch.object(ZohoAuth, "request", return_value=_mock_resp(payload)):
                result = runner.invoke(
                    cli,
                    ["crm", "variables", "update", "var1", "--data", '{"name": "Updated_Var"}', "--json"],
                )

        assert result.exit_code == 0

    def test_update_invalid_json(self, runner):
        with patch.object(ZohoAuth, "refresh", return_value="t"):
            result = runner.invoke(cli, ["crm", "variables", "update", "var1", "--data", "bad"])
        assert result.exit_code != 0

    def test_update_missing_data(self, runner):
        with patch.object(ZohoAuth, "refresh", return_value="t"):
            result = runner.invoke(cli, ["crm", "variables", "update", "var1"])
        assert result.exit_code != 0


class TestVariablesDelete:
    def test_delete_json(self, runner):
        payload = {"variables": [{"code": "SUCCESS", "status": "success"}]}
        with patch.object(ZohoAuth, "refresh", return_value="t"):
            with patch.object(ZohoAuth, "request", return_value=_mock_resp(payload)):
                result = runner.invoke(cli, ["crm", "variables", "delete", "var1", "--json"])

        assert result.exit_code == 0

    def test_delete_missing_id_arg(self, runner):
        with patch.object(ZohoAuth, "refresh", return_value="t"):
            result = runner.invoke(cli, ["crm", "variables", "delete"])
        assert result.exit_code != 0


class TestVariablesGroups:
    def test_groups_json(self, runner):
        # get_variable_groups returns resp.json().get("variable_groups", []) — a list
        payload = {"variable_groups": [{"id": "g1", "name": "Sales"}, {"id": "g2", "name": "Marketing"}]}
        with patch.object(ZohoAuth, "refresh", return_value="t"):
            with patch.object(ZohoAuth, "request", return_value=_mock_resp(payload)):
                result = runner.invoke(cli, ["crm", "variables", "groups", "--json"])

        assert result.exit_code == 0
        data = json.loads(result.output)
        assert isinstance(data, list)
        assert len(data) == 2
        assert data[0]["name"] == "Sales"

    def test_groups_table_output(self, runner):
        payload = {"variable_groups": [{"id": "g1", "name": "Sales"}]}
        with patch.object(ZohoAuth, "refresh", return_value="t"):
            with patch.object(ZohoAuth, "request", return_value=_mock_resp(payload)):
                result = runner.invoke(cli, ["crm", "variables", "groups"])

        assert result.exit_code == 0


# ---------------------------------------------------------------------------
# Org Settings
# ---------------------------------------------------------------------------

class TestOrgSettingsBusinessHours:
    def test_business_hours_json(self, runner):
        # get_business_hours returns resp.json().get("business_hours", {}) — the inner dict
        payload = {
            "business_hours": {
                "days": [
                    {"day": "Monday", "open": True, "from": "09:00", "to": "18:00"},
                    {"day": "Friday", "open": True, "from": "09:00", "to": "17:00"},
                ]
            }
        }
        with patch.object(ZohoAuth, "refresh", return_value="t"):
            with patch.object(ZohoAuth, "request", return_value=_mock_resp(payload)):
                result = runner.invoke(cli, ["crm", "org-settings", "business-hours", "--json"])

        assert result.exit_code == 0
        data = json.loads(result.output)
        assert "days" in data
        assert len(data["days"]) == 2

    def test_business_hours_table_output(self, runner):
        payload = {"business_hours": {"days": [{"day": "Monday", "open": True}]}}
        with patch.object(ZohoAuth, "refresh", return_value="t"):
            with patch.object(ZohoAuth, "request", return_value=_mock_resp(payload)):
                result = runner.invoke(cli, ["crm", "org-settings", "business-hours"])

        assert result.exit_code == 0


class TestOrgSettingsFiscalYear:
    def test_fiscal_year_json(self, runner):
        # get_fiscal_year returns resp.json().get("fiscal_year", {}) — the inner dict
        payload = {
            "fiscal_year": {
                "start_month": "January",
                "day_of_month": "1",
                "fiscal_year_name": "Calendar Year",
            }
        }
        with patch.object(ZohoAuth, "refresh", return_value="t"):
            with patch.object(ZohoAuth, "request", return_value=_mock_resp(payload)):
                result = runner.invoke(cli, ["crm", "org-settings", "fiscal-year", "--json"])

        assert result.exit_code == 0
        data = json.loads(result.output)
        assert data["start_month"] == "January"
        assert data["fiscal_year_name"] == "Calendar Year"

    def test_fiscal_year_table_output(self, runner):
        payload = {"fiscal_year": {"start_month": "January", "day_of_month": "1"}}
        with patch.object(ZohoAuth, "refresh", return_value="t"):
            with patch.object(ZohoAuth, "request", return_value=_mock_resp(payload)):
                result = runner.invoke(cli, ["crm", "org-settings", "fiscal-year"])

        assert result.exit_code == 0


# ---------------------------------------------------------------------------
# Org Settings — write commands
# ---------------------------------------------------------------------------

class TestOrgSettingsUpdateBusinessHours:
    def test_update_business_hours_json(self, runner):
        payload = {"business_hours": {"status": "success"}}
        with patch.object(ZohoAuth, "refresh", return_value="t"):
            with patch.object(ZohoAuth, "request", return_value=_mock_resp(payload)):
                result = runner.invoke(
                    cli,
                    [
                        "crm", "org-settings", "update-business-hours",
                        "--data", '{"days": [{"day": "Monday", "open": true}]}',
                        "--json",
                    ],
                )

        assert result.exit_code == 0

    def test_update_business_hours_invalid_json(self, runner):
        with patch.object(ZohoAuth, "refresh", return_value="t"):
            result = runner.invoke(
                cli,
                ["crm", "org-settings", "update-business-hours", "--data", "not-json"],
            )
        assert result.exit_code != 0


class TestOrgSettingsUpdateFiscalYear:
    def test_update_fiscal_year_json(self, runner):
        payload = {"fiscal_year": {"status": "success"}}
        with patch.object(ZohoAuth, "refresh", return_value="t"):
            with patch.object(ZohoAuth, "request", return_value=_mock_resp(payload)):
                result = runner.invoke(
                    cli,
                    [
                        "crm", "org-settings", "update-fiscal-year",
                        "--data", '{"start_month": "April"}',
                        "--json",
                    ],
                )

        assert result.exit_code == 0

    def test_update_fiscal_year_invalid_json(self, runner):
        with patch.object(ZohoAuth, "refresh", return_value="t"):
            result = runner.invoke(
                cli,
                ["crm", "org-settings", "update-fiscal-year", "--data", "bad-json"],
            )
        assert result.exit_code != 0


class TestOrgSettingsEnableMultiCurrency:
    def test_enable_multi_currency_json(self, runner):
        payload = {"currencies": {"status": "success"}}
        with patch.object(ZohoAuth, "refresh", return_value="t"):
            with patch.object(ZohoAuth, "request", return_value=_mock_resp(payload)):
                result = runner.invoke(
                    cli,
                    [
                        "crm", "org-settings", "enable-multi-currency",
                        "--data", '{"iso_code": "EUR"}',
                        "--json",
                    ],
                )

        assert result.exit_code == 0

    def test_enable_multi_currency_invalid_json(self, runner):
        with patch.object(ZohoAuth, "refresh", return_value="t"):
            result = runner.invoke(
                cli,
                ["crm", "org-settings", "enable-multi-currency", "--data", "not-valid-json"],
            )
        assert result.exit_code != 0
