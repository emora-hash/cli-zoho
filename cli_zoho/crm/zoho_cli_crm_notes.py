"""Zoho CRM Notes API client."""

from cli_zoho import config
from cli_zoho.zoho_cli_auth import ZohoAuth


class NotesClient:
    """Zoho CRM V8 Notes API operations."""

    def __init__(self, auth: ZohoAuth):
        self.auth = auth
        self.base = config.get_crm_base()

    def list_notes(self, module: str, record_id: str, *, page: int = 1, per_page: int = 10) -> dict:
        resp = self.auth.request(
            "GET",
            f"{self.base}/{module}/{record_id}/Notes",
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

    def create_note(self, module: str, record_id: str, note: str, title: str = "") -> dict:
        payload: dict = {
            "Note_Content": note,
            "Parent_Id": {"id": record_id, "module": {"api_name": module}},
            "$se_module": module,
        }
        if title:
            payload["Note_Title"] = title
        resp = self.auth.request(
            "POST",
            f"{self.base}/Notes",
            json={"data": [payload]},
        )
        return resp.json()

    def delete_note(self, note_id: str) -> dict:
        resp = self.auth.request("DELETE", f"{self.base}/Notes/{note_id}")
        return resp.json()
