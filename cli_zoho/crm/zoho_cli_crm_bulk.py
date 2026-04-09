"""Zoho CRM Bulk Read/Write API client — thin wrapper around shared auth."""

from pathlib import Path

from cli_zoho import config
from cli_zoho.zoho_cli_auth import ZohoAuth


class BulkClient:
    """Zoho CRM V8 Bulk API operations."""

    def __init__(self, auth: ZohoAuth):
        self.auth = auth
        self.base = config.get_crm_base()

    def create_read_job(
        self,
        module: str,
        query: dict | None = None,
        file_type: str = "csv",
        page: int | None = None,
    ) -> dict:
        body: dict = {
            "query": {"module": {"api_name": module}},
            "file_type": file_type,
        }
        if query:
            body["query"].update(query)
        if page is not None:
            body["page"] = page
        resp = self.auth.request("POST", f"{self.base}/bulk/read", json=body)
        return resp.json()

    def get_read_job(self, job_id: str) -> dict:
        resp = self.auth.request("GET", f"{self.base}/bulk/read/{job_id}")
        return resp.json()

    def download_read_result(self, job_id: str):
        """Returns raw response — caller must handle binary content."""
        return self.auth.request("GET", f"{self.base}/bulk/read/{job_id}/result")

    def create_write_job(
        self,
        module: str,
        file_path: str,
        operation: str = "insert",
        file_type: str = "csv",
    ) -> dict:
        path = Path(file_path)
        with path.open("rb") as fh:
            resp = self.auth.request(
                "POST",
                f"{self.base}/bulk/write",
                files={"file": (path.name, fh, f"text/{file_type}")},
                data={
                    "module": module,
                    "operation": operation,
                    "file_type": file_type,
                },
            )
        return resp.json()

    def get_write_job(self, job_id: str) -> dict:
        resp = self.auth.request("GET", f"{self.base}/bulk/write/{job_id}")
        return resp.json()
