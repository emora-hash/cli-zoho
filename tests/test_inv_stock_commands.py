"""Tests for Inventory Stock and Warehouse commands."""

import json


class TestInvStockSummary:
    def test_stock_summary_json(self, invoke):
        payload = {
            "item_stock_summary": {
                "item_id": "1001",
                "name": "Excavator Bucket 24in",
                "warehouses": [
                    {"warehouse_id": "w1", "warehouse_name": "Main", "quantity_available": 15},
                    {"warehouse_id": "w2", "warehouse_name": "East", "quantity_available": 3},
                ],
                "total_available": 18,
            }
        }
        result = invoke(["inv", "stock", "summary", "1001", "--json"], mock_response=payload)
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert "item_stock_summary" in data

    def test_stock_summary_table(self, invoke):
        payload = {
            "item_stock_summary": {
                "item_id": "1001",
                "name": "Excavator Bucket 24in",
                "total_available": 18,
            }
        }
        result = invoke(["inv", "stock", "summary", "1001"], mock_response=payload)
        assert result.exit_code == 0

    def test_inventory_alias_works(self, invoke):
        payload = {"item_stock_summary": {"item_id": "1001", "total_available": 5}}
        result = invoke(["inventory", "stock", "summary", "1001", "--json"], mock_response=payload)
        assert result.exit_code == 0


class TestInvStockWarehouses:
    def test_list_warehouses_json(self, invoke):
        payload = {
            "warehouses": [
                {"warehouse_id": "w1", "warehouse_name": "Main Warehouse", "is_primary": True},
                {"warehouse_id": "w2", "warehouse_name": "East Warehouse", "is_primary": False},
            ]
        }
        result = invoke(["inv", "stock", "warehouses", "--json"], mock_response=payload)
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert "warehouses" in data

    def test_list_warehouses_table(self, invoke):
        payload = {"warehouses": [{"warehouse_id": "w1", "warehouse_name": "Main"}]}
        result = invoke(["inv", "stock", "warehouses"], mock_response=payload)
        assert result.exit_code == 0


class TestInvStockWarehouse:
    def test_get_warehouse_json(self, invoke):
        payload = {
            "warehouse": {
                "warehouse_id": "w1",
                "warehouse_name": "Main Warehouse",
                "address": {"address": "123 Main St"},
            }
        }
        result = invoke(["inv", "stock", "warehouse", "w1", "--json"], mock_response=payload)
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert "warehouse" in data
