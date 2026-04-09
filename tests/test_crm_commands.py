"""Tests for CRM Click commands."""

import json
from unittest.mock import MagicMock, patch

from cli_zoho.zoho_cli_auth import ZohoAuth
from cli_zoho.zoho_cli_main import cli


class TestCRMList:
    def test_list_json(self, runner, crm_list_response):
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = crm_list_response
        mock_resp.raise_for_status = MagicMock()

        with patch.object(ZohoAuth, "refresh", return_value="t"):
            with patch.object(ZohoAuth, "request", return_value=mock_resp):
                result = runner.invoke(cli, ["crm", "list", "Deals", "--json"])

        assert result.exit_code == 0
        data = json.loads(result.output)
        assert len(data["data"]) == 2
        assert data["data"][0]["Deal_Name"] == "Test Deal"

    def test_list_with_fields_filter(self, runner, crm_list_response):
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = crm_list_response
        mock_resp.raise_for_status = MagicMock()

        with patch.object(ZohoAuth, "refresh", return_value="t"):
            with patch.object(ZohoAuth, "request", return_value=mock_resp):
                result = runner.invoke(cli, ["crm", "list", "Deals", "--json", "--fields", "Deal_Name,Amount"])

        data = json.loads(result.output)
        record = data["data"][0]
        assert "Deal_Name" in record
        assert "Amount" in record
        assert "Stage" not in record

    def test_list_empty_204(self, runner):
        mock_resp = MagicMock()
        mock_resp.status_code = 204
        mock_resp.json.return_value = {}
        mock_resp.raise_for_status = MagicMock()

        with patch.object(ZohoAuth, "refresh", return_value="t"):
            with patch.object(ZohoAuth, "request", return_value=mock_resp):
                result = runner.invoke(cli, ["crm", "list", "Deals", "--json"])

        data = json.loads(result.output)
        assert data["data"] == []

    def test_list_table_output(self, runner, crm_list_response):
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = crm_list_response
        mock_resp.raise_for_status = MagicMock()

        with patch.object(ZohoAuth, "refresh", return_value="t"):
            with patch.object(ZohoAuth, "request", return_value=mock_resp):
                result = runner.invoke(cli, ["crm", "list", "Deals"])

        assert result.exit_code == 0
        assert "Test Deal" in result.output
        assert "2 records" in result.output


class TestCRMGet:
    def test_get_json(self, runner, crm_single_response):
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = crm_single_response
        mock_resp.raise_for_status = MagicMock()

        with patch.object(ZohoAuth, "refresh", return_value="t"):
            with patch.object(ZohoAuth, "request", return_value=mock_resp):
                result = runner.invoke(cli, ["crm", "get", "Deals", "111", "--json"])

        assert result.exit_code == 0
        data = json.loads(result.output)
        assert data["Deal_Name"] == "Test Deal"


class TestCRMCreate:
    def test_create_with_data_flag(self, runner, crm_create_response):
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = crm_create_response
        mock_resp.raise_for_status = MagicMock()

        with patch.object(ZohoAuth, "refresh", return_value="t"):
            with patch.object(ZohoAuth, "request", return_value=mock_resp):
                result = runner.invoke(
                    cli,
                    ["crm", "create", "Deals", "--data", '{"Deal_Name": "New Deal"}', "--json"],
                )

        assert result.exit_code == 0
        data = json.loads(result.output)
        assert data["data"][0]["code"] == "SUCCESS"

    def test_create_missing_data_exits(self, runner):
        with patch.object(ZohoAuth, "refresh", return_value="t"):
            result = runner.invoke(cli, ["crm", "create", "Deals"])
        assert result.exit_code != 0

    def test_create_invalid_json_exits(self, runner):
        with patch.object(ZohoAuth, "refresh", return_value="t"):
            result = runner.invoke(cli, ["crm", "create", "Deals", "--data", "not-json"])
        assert result.exit_code != 0


class TestCRMSearch:
    def test_search_json(self, runner, crm_list_response):
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = {
            "data": crm_list_response["data"],
            "info": {"more_records": False},
        }
        mock_resp.raise_for_status = MagicMock()

        with patch.object(ZohoAuth, "refresh", return_value="t"):
            with patch.object(ZohoAuth, "request", return_value=mock_resp):
                result = runner.invoke(
                    cli,
                    ["crm", "search", "Deals", "(Deal_Name:equals:Test Deal)", "--json"],
                )

        assert result.exit_code == 0
        data = json.loads(result.output)
        assert len(data["data"]) == 2


class TestCOQL:
    def test_coql_query(self, runner, coql_response):
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = coql_response
        mock_resp.raise_for_status = MagicMock()

        with patch.object(ZohoAuth, "refresh", return_value="t"):
            with patch.object(ZohoAuth, "request", return_value=mock_resp):
                result = runner.invoke(
                    cli,
                    ["crm", "query", "SELECT Last_Name, Email FROM Contacts LIMIT 2", "--json"],
                )

        assert result.exit_code == 0
        data = json.loads(result.output)
        assert len(data["data"]) == 2
        assert data["data"][0]["Last_Name"] == "Smith"


class TestCRMFields:
    def test_fields_json(self, runner, crm_fields_response):
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = crm_fields_response
        mock_resp.raise_for_status = MagicMock()

        with patch.object(ZohoAuth, "refresh", return_value="t"):
            with patch.object(ZohoAuth, "request", return_value=mock_resp):
                result = runner.invoke(cli, ["crm", "fields", "Deals", "--json"])

        assert result.exit_code == 0
        data = json.loads(result.output)
        assert len(data) == 3
        assert data[0]["api_name"] == "Deal_Name"


class TestCRMModules:
    def test_modules_json(self, runner, crm_modules_response):
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = crm_modules_response
        mock_resp.raise_for_status = MagicMock()

        with patch.object(ZohoAuth, "refresh", return_value="t"):
            with patch.object(ZohoAuth, "request", return_value=mock_resp):
                result = runner.invoke(cli, ["crm", "modules", "--json"])

        assert result.exit_code == 0
        data = json.loads(result.output)
        assert len(data) == 3
        names = [m["api_name"] for m in data]
        assert "Deals" in names
        assert "Contacts" in names


class TestCRMUpdate:
    def test_update_record(self, invoke):
        resp = {
            "data": [
                {"code": "SUCCESS", "details": {"id": "123"}, "message": "record updated", "status": "success"}
            ],
        }
        result = invoke(
            ["crm", "update", "Deals", "123", "--data", '{"Amount": 5000}', "--json"],
            mock_response=resp,
        )
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert data["data"][0]["code"] == "SUCCESS"

    def test_update_dry_run(self, runner):
        with patch.object(ZohoAuth, "refresh", return_value="t"):
            with patch.object(ZohoAuth, "request") as mock_request:
                result = runner.invoke(
                    cli,
                    ["crm", "update", "Deals", "123", "--data", '{"Amount": 5000}', "--dry-run"],
                )
        mock_request.assert_not_called()
        assert result.exit_code == 0
        assert "[DRY RUN]" in result.output


class TestCRMDelete:
    def test_delete_record(self, invoke):
        resp = {
            "data": [
                {"code": "SUCCESS", "details": {"id": "123"}, "message": "record deleted", "status": "success"}
            ],
        }
        result = invoke(["crm", "delete", "Deals", "123", "--json"], mock_response=resp)
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert data["data"][0]["code"] == "SUCCESS"

    def test_delete_dry_run(self, runner):
        with patch.object(ZohoAuth, "refresh", return_value="t"):
            with patch.object(ZohoAuth, "request") as mock_request:
                result = runner.invoke(cli, ["crm", "delete", "Deals", "123", "--dry-run"])
        mock_request.assert_not_called()
        assert result.exit_code == 0
        assert "[DRY RUN]" in result.output


class TestCRMGetNotFound:
    def test_get_record_not_found(self, runner):
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = {"data": []}
        mock_resp.raise_for_status = MagicMock()

        with patch.object(ZohoAuth, "refresh", return_value="t"):
            with patch.object(ZohoAuth, "request", return_value=mock_resp):
                result = runner.invoke(cli, ["crm", "get", "Deals", "NONEXISTENT", "--json"])

        assert result.exit_code != 0
