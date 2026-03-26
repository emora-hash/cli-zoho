"""Zoho Inventory Stock and Warehouse API client."""

from cli_zoho import config
from cli_zoho.auth import ZohoAuth


class StockClient:
    """Zoho Inventory V1 Stock and Warehouse operations."""

    def __init__(self, auth: ZohoAuth):
        self.auth = auth
        self.base = config.get_inventory_base()

    def _headers(self) -> dict:
        return {"X-com-zoho-inventory-organizationid": config.get_org_id()}

    def stock_summary(self, item_id: str) -> dict:
        """Get stock levels for an item broken down by warehouse."""
        resp = self.auth.request(
            "GET",
            f"{self.base}/items/{item_id}/stocksummary",
            headers=self._headers(),
        )
        return resp.json()

    def list_warehouses(self) -> dict:
        """List all warehouses in the organization."""
        resp = self.auth.request(
            "GET",
            f"{self.base}/warehouses",
            headers=self._headers(),
        )
        return resp.json()

    def get_warehouse(self, warehouse_id: str) -> dict:
        """Get a single warehouse by ID."""
        resp = self.auth.request(
            "GET",
            f"{self.base}/warehouses/{warehouse_id}",
            headers=self._headers(),
        )
        return resp.json()
