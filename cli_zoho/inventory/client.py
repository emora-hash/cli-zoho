"""Zoho Inventory API client — thin wrapper around shared auth."""

import json

from cli_zoho import config
from cli_zoho.auth import ZohoAuth
from cli_zoho.shared.pagination import paginate_inventory


class InventoryClient:
    """Zoho Inventory V1 API operations."""

    def __init__(self, auth: ZohoAuth):
        self.auth = auth
        self.base = config.get_inventory_base()

    def _headers(self) -> dict:
        return {"X-com-zoho-inventory-organizationid": config.get_org_id()}

    def list_records(self, entity_name: str, *, limit: int = 10, page: int = 1) -> dict:
        entity_cfg = config.INVENTORY_ENTITIES[entity_name]
        return paginate_inventory(self.auth, entity_cfg, limit=limit, page=page)

    def get_record(self, entity_name: str, record_id: str) -> dict:
        entity_cfg = config.INVENTORY_ENTITIES[entity_name]
        singular_key = entity_cfg["get_key"]
        resp = self.auth.request(
            "GET",
            f"{self.base}{entity_cfg['endpoint']}/{record_id}",
            headers=self._headers(),
        )

        body = resp.json()
        return body.get(singular_key, body)

    def create_record(self, entity_name: str, data: dict) -> dict:
        entity_cfg = config.INVENTORY_ENTITIES[entity_name]
        resp = self.auth.request(
            "POST",
            f"{self.base}{entity_cfg['endpoint']}",
            headers=self._headers(),
            data={"JSONString": json.dumps(data)},
        )

        return resp.json()

    def update_record(self, entity_name: str, record_id: str, data: dict) -> dict:
        entity_cfg = config.INVENTORY_ENTITIES[entity_name]
        resp = self.auth.request(
            "PUT",
            f"{self.base}{entity_cfg['endpoint']}/{record_id}",
            headers=self._headers(),
            data={"JSONString": json.dumps(data)},
        )

        return resp.json()

    def delete_record(self, entity_name: str, record_id: str) -> dict:
        entity_cfg = config.INVENTORY_ENTITIES[entity_name]
        resp = self.auth.request(
            "DELETE",
            f"{self.base}{entity_cfg['endpoint']}/{record_id}",
            headers=self._headers(),
        )

        return resp.json()

    def search(self, entity_name: str, text: str, *, limit: int = 10, page: int = 1) -> dict:
        entity_cfg = config.INVENTORY_ENTITIES[entity_name]
        params = {
            "search_text": text,
            "page": page,
            "per_page": min(limit, 200),
        }
        params.update(entity_cfg.get("extra_params", {}))
        resp = self.auth.request(
            "GET",
            f"{self.base}{entity_cfg['endpoint']}",
            headers=self._headers(),
            params=params,
        )

        body = resp.json()
        # Search is just a filtered list — response uses entity key (confirmed by MCP ref)
        records = body.get(entity_cfg["list_key"], [])
        has_more = body.get("has_more_page", False)
        return {
            "data": records,
            "has_more": has_more,
            "next_page": page + 1 if has_more else None,
            "count": len(records),
        }

    def get_fields(self, entity_name: str) -> list:
        """Get custom fields for an Inventory entity."""
        resp = self.auth.request(
            "GET",
            f"{self.base}/settings/customfields",
            headers=self._headers(),
            params={"entity": entity_name},
        )

        return resp.json().get("customfields", [])
