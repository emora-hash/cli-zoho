"""Zoho CRM Recycle Bin API client. Routes through App #3 (bulk/admin scopes)."""

from cli_zoho import config
from cli_zoho.zoho_cli_auth import ZohoAuth


class TrashClient:
    """Zoho CRM V8 Recycle Bin operations."""

    def __init__(self, auth: ZohoAuth):
        self.auth = auth
        self.base = config.get_crm_base()

    def list_trash(self, module: str = "", *, page: int = 1, per_page: int = 10) -> dict:
        params: dict = {"page": page, "per_page": min(per_page, 200)}
        if module:
            params["module"] = module
        resp = self.auth.request("GET", f"{self.base}/recycle_bin", params=params)
        if resp.status_code == 204:
            return {"data": [], "has_more": False, "count": 0}
        body = resp.json()
        info = body.get("info", {})
        return {
            "data": body.get("data", []),
            "has_more": info.get("more_records", False),
            "count": len(body.get("data", [])),
        }

    def restore(self, record_ids: list[str]) -> dict:
        resp = self.auth.request(
            "PUT",
            f"{self.base}/recycle_bin",
            params={"ids": ",".join(record_ids)},
        )
        return resp.json()

    def purge(self, record_ids: list[str]) -> dict:
        resp = self.auth.request(
            "DELETE",
            f"{self.base}/recycle_bin",
            params={"ids": ",".join(record_ids)},
        )
        return resp.json()
