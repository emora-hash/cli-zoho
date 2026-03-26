"""Zoho CRM Tags API client."""

from cli_zoho import config
from cli_zoho.auth import ZohoAuth


class TagsClient:
    """Zoho CRM V8 Tags API operations."""

    def __init__(self, auth: ZohoAuth):
        self.auth = auth
        self.base = config.get_crm_base()

    def list_tags(self, module: str) -> dict:
        resp = self.auth.request(
            "GET",
            f"{self.base}/settings/tags",
            params={"module": module},
        )
        return resp.json()

    def add_tags(self, module: str, record_id: str, tag_names: list[str]) -> dict:
        resp = self.auth.request(
            "POST",
            f"{self.base}/{module}/{record_id}/tags",
            json={"tags": [{"name": t} for t in tag_names]},
        )
        return resp.json()

    def remove_tags(self, module: str, record_id: str, tag_names: list[str]) -> dict:
        resp = self.auth.request(
            "DELETE",
            f"{self.base}/{module}/{record_id}/tags",
            json={"tags": [{"name": t} for t in tag_names]},
        )
        return resp.json()
