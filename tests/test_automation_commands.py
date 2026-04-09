"""Tests for CRM automation Click commands — workflows, blueprint, scoring, assignments."""

import json
from unittest.mock import MagicMock, patch

from cli_zoho.zoho_cli_auth import ZohoAuth
from cli_zoho.zoho_cli_main import cli


def _mock_resp(payload, status_code=200):
    resp = MagicMock()
    resp.status_code = status_code
    resp.json.return_value = payload
    resp.raise_for_status = MagicMock()
    return resp


# ---------------------------------------------------------------------------
# Workflows
# ---------------------------------------------------------------------------

class TestWorkflowsList:
    def test_list_json(self, runner):
        # get_workflows returns resp.json().get("workflow_rules", []) — a list
        payload = {"workflow_rules": [{"id": "w1", "name": "Lead Follow-up", "module": {"api_name": "Leads"}}]}
        with patch.object(ZohoAuth, "refresh", return_value="t"):
            with patch.object(ZohoAuth, "request", return_value=_mock_resp(payload)):
                result = runner.invoke(cli, ["crm", "workflows", "list", "--json"])

        assert result.exit_code == 0
        data = json.loads(result.output)
        assert isinstance(data, list)
        assert data[0]["id"] == "w1"

    def test_list_with_module_filter(self, runner):
        payload = {"workflow_rules": [{"id": "w2", "name": "Deal Rule", "module": {"api_name": "Deals"}}]}
        with patch.object(ZohoAuth, "refresh", return_value="t"):
            with patch.object(ZohoAuth, "request", return_value=_mock_resp(payload)):
                result = runner.invoke(cli, ["crm", "workflows", "list", "--module", "Deals", "--json"])

        assert result.exit_code == 0
        data = json.loads(result.output)
        assert isinstance(data, list)
        assert data[0]["module"]["api_name"] == "Deals"

    def test_list_table_output(self, runner):
        payload = {"workflow_rules": [{"id": "w1", "name": "Lead Follow-up"}]}
        with patch.object(ZohoAuth, "refresh", return_value="t"):
            with patch.object(ZohoAuth, "request", return_value=_mock_resp(payload)):
                result = runner.invoke(cli, ["crm", "workflows", "list"])

        assert result.exit_code == 0


class TestWorkflowsGet:
    def test_get_json(self, runner):
        # get_workflow returns resp.json().get("workflow_rules", [{}])[0] — a single dict
        payload = {"workflow_rules": [{"id": "w1", "name": "Lead Follow-up", "status": "Active"}]}
        with patch.object(ZohoAuth, "refresh", return_value="t"):
            with patch.object(ZohoAuth, "request", return_value=_mock_resp(payload)):
                result = runner.invoke(cli, ["crm", "workflows", "get", "w1", "--json"])

        assert result.exit_code == 0
        data = json.loads(result.output)
        assert data["id"] == "w1"
        assert data["status"] == "Active"


class TestWorkflowsUpdate:
    def test_update_json(self, runner):
        payload = {"workflow_rules": [{"code": "SUCCESS", "details": {"id": "w1"}, "status": "success"}]}
        with patch.object(ZohoAuth, "refresh", return_value="t"):
            with patch.object(ZohoAuth, "request", return_value=_mock_resp(payload)):
                result = runner.invoke(
                    cli,
                    ["crm", "workflows", "update", "w1", "--data", '{"name": "Updated Rule"}', "--json"],
                )

        assert result.exit_code == 0
        data = json.loads(result.output)
        assert data["workflow_rules"][0]["status"] == "success"

    def test_update_invalid_json(self, runner):
        with patch.object(ZohoAuth, "refresh", return_value="t"):
            result = runner.invoke(cli, ["crm", "workflows", "update", "w1", "--data", "not-json"])
        assert result.exit_code != 0


class TestWorkflowsDelete:
    def test_delete_json(self, runner):
        payload = {"workflow_rules": [{"code": "SUCCESS", "status": "success"}]}
        with patch.object(ZohoAuth, "refresh", return_value="t"):
            with patch.object(ZohoAuth, "request", return_value=_mock_resp(payload)):
                result = runner.invoke(cli, ["crm", "workflows", "delete", "w1", "--json"])

        assert result.exit_code == 0


class TestWorkflowsReorder:
    def test_reorder_json(self, runner):
        payload = {"status": "success"}
        with patch.object(ZohoAuth, "refresh", return_value="t"):
            with patch.object(ZohoAuth, "request", return_value=_mock_resp(payload)):
                result = runner.invoke(
                    cli,
                    ["crm", "workflows", "reorder", "Deals", "--ids", "w1,w2,w3", "--json"],
                )

        assert result.exit_code == 0

    def test_reorder_missing_ids(self, runner):
        with patch.object(ZohoAuth, "refresh", return_value="t"):
            result = runner.invoke(cli, ["crm", "workflows", "reorder", "Deals"])
        assert result.exit_code != 0

    def test_reorder_empty_ids_after_filtering(self, runner):
        # IDs string is all whitespace/commas — after filtering, list is empty
        with patch.object(ZohoAuth, "refresh", return_value="t"):
            result = runner.invoke(
                cli,
                ["crm", "workflows", "reorder", "Deals", "--ids", ",,, ,", "--json"],
            )
        assert result.exit_code != 0


class TestWorkflowsUsage:
    def test_usage_json(self, runner):
        payload = {"usage": [{"module": "Leads", "count": 3}]}
        with patch.object(ZohoAuth, "refresh", return_value="t"):
            with patch.object(ZohoAuth, "request", return_value=_mock_resp(payload)):
                result = runner.invoke(cli, ["crm", "workflows", "usage", "--json"])

        assert result.exit_code == 0
        data = json.loads(result.output)
        assert "usage" in data


class TestWorkflowsLimits:
    def test_limits_json(self, runner):
        payload = {"limits": {"max_rules": 50, "used": 12}}
        with patch.object(ZohoAuth, "refresh", return_value="t"):
            with patch.object(ZohoAuth, "request", return_value=_mock_resp(payload)):
                result = runner.invoke(cli, ["crm", "workflows", "limits", "--json"])

        assert result.exit_code == 0
        data = json.loads(result.output)
        assert "limits" in data


class TestWorkflowsActionsCount:
    def test_actions_count_json(self, runner):
        payload = {"actions_count": {"rule_id": "w1", "count": 3}}
        with patch.object(ZohoAuth, "refresh", return_value="t"):
            with patch.object(ZohoAuth, "request", return_value=_mock_resp(payload)):
                result = runner.invoke(cli, ["crm", "workflows", "actions-count", "w1", "--json"])

        assert result.exit_code == 0
        data = json.loads(result.output)
        assert "actions_count" in data


# ---------------------------------------------------------------------------
# Blueprint
# ---------------------------------------------------------------------------

class TestBlueprintGet:
    def test_get_json(self, runner):
        # get_blueprint returns resp.json().get("blueprint", {}) — a dict
        payload = {"blueprint": {"transitions": [{"id": "t1", "name": "Qualify"}]}}
        with patch.object(ZohoAuth, "refresh", return_value="t"):
            with patch.object(ZohoAuth, "request", return_value=_mock_resp(payload)):
                result = runner.invoke(cli, ["crm", "blueprint", "get", "Deals", "111", "--json"])

        assert result.exit_code == 0
        data = json.loads(result.output)
        assert "transitions" in data
        assert data["transitions"][0]["name"] == "Qualify"


class TestBlueprintAdvance:
    def test_advance_json(self, runner):
        payload = {"code": "SUCCESS", "status": "success"}
        with patch.object(ZohoAuth, "refresh", return_value="t"):
            with patch.object(ZohoAuth, "request", return_value=_mock_resp(payload)):
                result = runner.invoke(
                    cli,
                    [
                        "crm", "blueprint", "advance", "Deals", "111",
                        "--transition-id", "t1",
                        "--data", '{"Stage": "Qualified"}',
                        "--json",
                    ],
                )

        assert result.exit_code == 0

    def test_advance_invalid_json(self, runner):
        with patch.object(ZohoAuth, "refresh", return_value="t"):
            result = runner.invoke(
                cli,
                ["crm", "blueprint", "advance", "Deals", "111", "--transition-id", "t1", "--data", "bad-json"],
            )
        assert result.exit_code != 0

    def test_advance_missing_transition_id(self, runner):
        with patch.object(ZohoAuth, "refresh", return_value="t"):
            result = runner.invoke(
                cli,
                ["crm", "blueprint", "advance", "Deals", "111", "--data", '{"Stage": "Qualified"}'],
            )
        assert result.exit_code != 0


# ---------------------------------------------------------------------------
# Scoring
# ---------------------------------------------------------------------------

class TestScoringList:
    def test_list_json(self, runner):
        # get_scoring_rules returns a list extracted from the envelope
        payload = {"scoring_rules": [{"id": "s1", "name": "Lead Score", "module": {"api_name": "Leads"}}]}
        with patch.object(ZohoAuth, "refresh", return_value="t"):
            with patch.object(ZohoAuth, "request", return_value=_mock_resp(payload)):
                result = runner.invoke(cli, ["crm", "scoring", "list", "--json"])

        assert result.exit_code == 0
        data = json.loads(result.output)
        assert isinstance(data, list)
        assert data[0]["id"] == "s1"

    def test_list_with_module_filter(self, runner):
        payload = {"scoring_rules": [{"id": "s1", "module": {"api_name": "Leads"}}]}
        with patch.object(ZohoAuth, "refresh", return_value="t"):
            with patch.object(ZohoAuth, "request", return_value=_mock_resp(payload)):
                result = runner.invoke(cli, ["crm", "scoring", "list", "--module", "Leads", "--json"])

        assert result.exit_code == 0


class TestScoringCreate:
    def test_create_json(self, runner):
        payload = {"scoring_rules": [{"code": "SUCCESS", "details": {"id": "s2"}, "status": "success"}]}
        with patch.object(ZohoAuth, "refresh", return_value="t"):
            with patch.object(ZohoAuth, "request", return_value=_mock_resp(payload)):
                result = runner.invoke(
                    cli,
                    ["crm", "scoring", "create", "--data", '{"name": "New Score Rule"}', "--json"],
                )

        assert result.exit_code == 0
        data = json.loads(result.output)
        assert data["scoring_rules"][0]["status"] == "success"

    def test_create_invalid_json(self, runner):
        with patch.object(ZohoAuth, "refresh", return_value="t"):
            result = runner.invoke(cli, ["crm", "scoring", "create", "--data", "not-json"])
        assert result.exit_code != 0

    def test_create_missing_data(self, runner):
        with patch.object(ZohoAuth, "refresh", return_value="t"):
            result = runner.invoke(cli, ["crm", "scoring", "create"])
        assert result.exit_code != 0


class TestScoringUpdate:
    def test_update_json(self, runner):
        payload = {"scoring_rules": [{"code": "SUCCESS", "status": "success"}]}
        with patch.object(ZohoAuth, "refresh", return_value="t"):
            with patch.object(ZohoAuth, "request", return_value=_mock_resp(payload)):
                result = runner.invoke(
                    cli,
                    ["crm", "scoring", "update", "s1", "--data", '{"name": "Updated"}', "--json"],
                )

        assert result.exit_code == 0

    def test_update_invalid_json(self, runner):
        with patch.object(ZohoAuth, "refresh", return_value="t"):
            result = runner.invoke(cli, ["crm", "scoring", "update", "s1", "--data", "bad"])
        assert result.exit_code != 0


class TestScoringDelete:
    def test_delete_json(self, runner):
        payload = {"scoring_rules": [{"code": "SUCCESS", "status": "success"}]}
        with patch.object(ZohoAuth, "refresh", return_value="t"):
            with patch.object(ZohoAuth, "request", return_value=_mock_resp(payload)):
                result = runner.invoke(cli, ["crm", "scoring", "delete", "s1", "--json"])

        assert result.exit_code == 0


class TestScoringExecute:
    def test_execute_json(self, runner):
        payload = {"status": "success", "message": "Scoring rule executed"}
        with patch.object(ZohoAuth, "refresh", return_value="t"):
            with patch.object(ZohoAuth, "request", return_value=_mock_resp(payload)):
                result = runner.invoke(cli, ["crm", "scoring", "execute", "s1", "Leads", "--json"])

        assert result.exit_code == 0
        data = json.loads(result.output)
        assert data["status"] == "success"


# ---------------------------------------------------------------------------
# Assignments
# ---------------------------------------------------------------------------

class TestAssignmentsList:
    def test_list_json(self, runner):
        # get_assignment_rules returns a list extracted from the envelope
        payload = {"assignment_rules": [{"id": "a1", "name": "Round Robin", "module": {"api_name": "Leads"}}]}
        with patch.object(ZohoAuth, "refresh", return_value="t"):
            with patch.object(ZohoAuth, "request", return_value=_mock_resp(payload)):
                result = runner.invoke(cli, ["crm", "assignments", "list", "--json"])

        assert result.exit_code == 0
        data = json.loads(result.output)
        assert isinstance(data, list)
        assert data[0]["id"] == "a1"

    def test_list_with_module_filter(self, runner):
        payload = {"assignment_rules": [{"id": "a1", "module": {"api_name": "Contacts"}}]}
        with patch.object(ZohoAuth, "refresh", return_value="t"):
            with patch.object(ZohoAuth, "request", return_value=_mock_resp(payload)):
                result = runner.invoke(cli, ["crm", "assignments", "list", "--module", "Contacts", "--json"])

        assert result.exit_code == 0

    def test_list_table_output(self, runner):
        payload = {"assignment_rules": [{"id": "a1", "name": "Round Robin"}]}
        with patch.object(ZohoAuth, "refresh", return_value="t"):
            with patch.object(ZohoAuth, "request", return_value=_mock_resp(payload)):
                result = runner.invoke(cli, ["crm", "assignments", "list"])

        assert result.exit_code == 0
