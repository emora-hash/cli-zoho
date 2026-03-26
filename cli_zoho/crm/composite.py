"""Zoho CRM Composite API client."""

from cli_zoho import config
from cli_zoho.auth import ZohoAuth


class CompositeClient:
    """Zoho CRM V8 Composite API operations."""

    def __init__(self, auth: ZohoAuth):
        self.auth = auth
        self.base = config.get_crm_base()

    def execute(self, requests_list: list) -> dict:
        """Execute a composite API request.

        Each item in requests_list should have:
          - method: HTTP method (GET, POST, PUT, DELETE)
          - url: relative or absolute URL
          - referenceId: unique identifier for this sub-request
          - body: (optional) request body dict
        """
        resp = self.auth.request(
            "POST",
            f"{self.base}/composite",
            json={"composite_requests": requests_list},
        )
        return resp.json()
