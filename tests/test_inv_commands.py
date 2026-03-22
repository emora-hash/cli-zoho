"""Tests for Inventory Click commands."""

import json
from unittest.mock import MagicMock, patch

from cli_zoho.auth import ZohoAuth
from cli_zoho.main import cli


class TestInventoryList:
    def test_list_items_json(self, runner, inv_list_response):
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = inv_list_response
        mock_resp.raise_for_status = MagicMock()

        with patch.object(ZohoAuth, "refresh", return_value="t"):
            with patch.object(ZohoAuth, "request", return_value=mock_resp):
                result = runner.invoke(cli, ["inv", "list", "items", "--json"])

        assert result.exit_code == 0
        data = json.loads(result.output)
        assert len(data["data"]) == 2
        assert data["data"][0]["name"] == "Excavator Bucket 24in"

    def test_list_with_fields_filter(self, runner, inv_list_response):
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = inv_list_response
        mock_resp.raise_for_status = MagicMock()

        with patch.object(ZohoAuth, "refresh", return_value="t"):
            with patch.object(ZohoAuth, "request", return_value=mock_resp):
                result = runner.invoke(cli, ["inv", "list", "items", "--json", "--fields", "name,rate"])

        data = json.loads(result.output)
        record = data["data"][0]
        assert "name" in record
        assert "rate" in record
        assert "item_id" not in record

    def test_invalid_entity_exits(self, runner):
        with patch.object(ZohoAuth, "refresh", return_value="t"):
            result = runner.invoke(cli, ["inv", "list", "nonexistent"])
        assert result.exit_code != 0
        assert "Unknown entity" in result.output

    def test_alias_inv_works(self, runner, inv_list_response):
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = inv_list_response
        mock_resp.raise_for_status = MagicMock()

        with patch.object(ZohoAuth, "refresh", return_value="t"):
            with patch.object(ZohoAuth, "request", return_value=mock_resp):
                result = runner.invoke(cli, ["inv", "list", "items", "--json"])

        assert result.exit_code == 0


class TestInventoryGet:
    def test_get_item_json(self, runner, inv_single_response):
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = inv_single_response
        mock_resp.raise_for_status = MagicMock()

        with patch.object(ZohoAuth, "refresh", return_value="t"):
            with patch.object(ZohoAuth, "request", return_value=mock_resp):
                result = runner.invoke(cli, ["inv", "get", "items", "1001", "--json"])

        assert result.exit_code == 0
        data = json.loads(result.output)
        assert data["name"] == "Excavator Bucket 24in"


class TestInventoryCreate:
    def test_create_item(self, runner):
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = {"code": 0, "message": "success", "item": {"item_id": "9999"}}
        mock_resp.raise_for_status = MagicMock()

        with patch.object(ZohoAuth, "refresh", return_value="t"):
            with patch.object(ZohoAuth, "request", return_value=mock_resp):
                result = runner.invoke(
                    cli,
                    ["inv", "create", "items", "--data", '{"name": "Test Bucket"}', "--json"],
                )

        assert result.exit_code == 0

    def test_create_missing_data_exits(self, runner):
        with patch.object(ZohoAuth, "refresh", return_value="t"):
            result = runner.invoke(cli, ["inv", "create", "items"])
        assert result.exit_code != 0


class TestInventorySearch:
    def test_search_items(self, runner, inv_list_response):
        # Search is just a filtered list — response uses entity key (confirmed by MCP ref)
        search_response = {
            "items": inv_list_response["items"],
            "page_context": {"has_more_page": False},
        }
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = search_response
        mock_resp.raise_for_status = MagicMock()

        with patch.object(ZohoAuth, "refresh", return_value="t"):
            with patch.object(ZohoAuth, "request", return_value=mock_resp):
                result = runner.invoke(cli, ["inv", "search", "items", "bucket", "--json"])

        assert result.exit_code == 0
        data = json.loads(result.output)
        assert len(data["data"]) == 2


class TestInventoryEntities:
    def test_entities_list(self, runner):
        with patch.object(ZohoAuth, "refresh", return_value="t"):
            result = runner.invoke(cli, ["inv", "entities", "--json"])

        assert result.exit_code == 0
        data = json.loads(result.output)
        names = [e["name"] for e in data]
        assert "items" in names
        assert "vendors" in names
        assert "shipments" in names


class TestInventoryUpdate:
    def test_update_record(self, runner):
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = {"code": 0, "message": "success", "item": {"item_id": "1001"}}
        mock_resp.raise_for_status = MagicMock()

        with patch.object(ZohoAuth, "refresh", return_value="t"):
            with patch.object(ZohoAuth, "request", return_value=mock_resp):
                result = runner.invoke(
                    cli,
                    ["inv", "update", "items", "1001", "--data", '{"name": "Updated Bucket"}', "--json"],
                )

        assert result.exit_code == 0


class TestInventoryDelete:
    def test_delete_record(self, runner):
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = {"code": 0, "message": "The item has been deleted."}
        mock_resp.raise_for_status = MagicMock()

        with patch.object(ZohoAuth, "refresh", return_value="t"):
            with patch.object(ZohoAuth, "request", return_value=mock_resp):
                result = runner.invoke(cli, ["inv", "delete", "items", "1001", "--json"])

        assert result.exit_code == 0

    def test_delete_dry_run(self, runner):
        with patch.object(ZohoAuth, "refresh", return_value="t"):
            with patch.object(ZohoAuth, "request") as mock_request:
                result = runner.invoke(cli, ["inv", "delete", "items", "1001", "--dry-run"])

        mock_request.assert_not_called()
        assert result.exit_code == 0
        assert "[DRY RUN]" in result.output


class TestInventoryCreateDryRun:
    def test_create_dry_run(self, runner):
        with patch.object(ZohoAuth, "refresh", return_value="t"):
            with patch.object(ZohoAuth, "request") as mock_request:
                result = runner.invoke(
                    cli,
                    ["inv", "create", "items", "--data", '{"name": "Test Bucket"}', "--dry-run"],
                )

        mock_request.assert_not_called()
        assert result.exit_code == 0
        assert "[DRY RUN]" in result.output
