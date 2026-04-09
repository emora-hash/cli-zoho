"""Tests for field discovery commands."""

import json
from unittest.mock import MagicMock, patch

from cli_zoho.zoho_cli_auth import ZohoAuth
from cli_zoho.zoho_cli_main import cli


class TestCRMFields:
    def test_fields_returns_compact_format(self, runner, crm_fields_response):
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
        field = data[0]
        assert set(field.keys()) == {"api_name", "label", "type", "required"}
        assert field["api_name"] == "Deal_Name"
        assert field["required"] is True

    def test_fields_table_output(self, runner, crm_fields_response):
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = crm_fields_response
        mock_resp.raise_for_status = MagicMock()

        with patch.object(ZohoAuth, "refresh", return_value="t"):
            with patch.object(ZohoAuth, "request", return_value=mock_resp):
                result = runner.invoke(cli, ["crm", "fields", "Deals"])

        assert "Deal_Name" in result.output
        assert "Amount" in result.output


class TestCRMModulesDiscovery:
    def test_modules_returns_compact_format(self, runner, crm_modules_response):
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = crm_modules_response
        mock_resp.raise_for_status = MagicMock()

        with patch.object(ZohoAuth, "refresh", return_value="t"):
            with patch.object(ZohoAuth, "request", return_value=mock_resp):
                result = runner.invoke(cli, ["crm", "modules", "--json"])

        data = json.loads(result.output)
        names = {m["api_name"] for m in data}
        assert "Deals" in names
        assert "Contacts" in names


class TestInventoryEntitiesDiscovery:
    def test_entities_lists_all_configured(self, runner):
        with patch.object(ZohoAuth, "refresh", return_value="t"):
            result = runner.invoke(cli, ["inv", "entities", "--json"])

        data = json.loads(result.output)
        names = {e["name"] for e in data}
        expected = {"items", "item_groups", "packages", "shipments",
                    "purchase_orders", "purchase_receives", "bills",
                    "payments_made", "vendors", "sales_orders",
                    "customers", "transfer_orders", "contact_persons",
                    "invoices", "payments_received", "warehouses",
                    "price_lists", "composite_items"}
        assert names == expected
