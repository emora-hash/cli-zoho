"""Zoho CRM Related Records API client."""

from cli_zoho import config
from cli_zoho.auth import ZohoAuth


class RelatedClient:
    """Zoho CRM V8 Related Records API operations."""

    def __init__(self, auth: ZohoAuth):
        self.auth = auth
        self.base = config.get_crm_base()

    def list_related(
        self,
        module: str,
        record_id: str,
        related_module: str,
        *,
        page: int = 1,
        per_page: int = 10,
    ) -> dict:
        resp = self.auth.request(
            "GET",
            f"{self.base}/{module}/{record_id}/{related_module}",
            params={"page": page, "per_page": min(per_page, 200)},
        )
        if resp.status_code == 204:
            return {"data": [], "has_more": False, "count": 0}
        body = resp.json()
        info = body.get("info", {})
        return {
            "data": body.get("data", []),
            "has_more": info.get("more_records", False),
            "count": len(body.get("data", [])),
        }
