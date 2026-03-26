"""Zoho CRM Mass Update/Delete API client — thin wrapper around shared auth."""

from cli_zoho import config
from cli_zoho.auth import ZohoAuth


class MassClient:
    """Zoho CRM V8 Mass Update/Delete operations."""

    def __init__(self, auth: ZohoAuth):
        self.auth = auth
        self.base = config.get_crm_base()

    def mass_update(
        self,
        module: str,
        data: list[dict],
        ids: list[str] | None = None,
        criteria: dict | None = None,
    ) -> dict:
        body: dict = {"data": data}
        if ids:
            body["ids"] = ids
        if criteria:
            body["criteria"] = criteria
        resp = self.auth.request(
            "POST",
            f"{self.base}/{module}/actions/mass_update",
            json=body,
        )
        return resp.json()

    def get_mass_update_status(self, module: str, job_id: str) -> dict:
        resp = self.auth.request(
            "GET",
            f"{self.base}/{module}/actions/mass_update",
            params={"job_id": job_id},
        )
        return resp.json()

    def mass_delete(
        self,
        module: str,
        ids: list[str] | None = None,
        criteria: dict | None = None,
    ) -> dict:
        body: dict = {}
        if ids:
            body["ids"] = ids
        if criteria:
            body["criteria"] = criteria
        resp = self.auth.request(
            "POST",
            f"{self.base}/{module}/actions/mass_delete",
            json=body,
        )
        return resp.json()

    def get_mass_delete_status(self, module: str, job_id: str) -> dict:
        resp = self.auth.request(
            "GET",
            f"{self.base}/{module}/actions/mass_delete",
            params={"job_id": job_id},
        )
        return resp.json()
