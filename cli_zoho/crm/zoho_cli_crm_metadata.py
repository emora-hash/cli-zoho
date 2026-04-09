"""Zoho CRM Metadata API client — layouts, custom views, related lists, field metadata."""

from cli_zoho import config
from cli_zoho.zoho_cli_auth import ZohoAuth


class MetadataClient:
    """Zoho CRM metadata operations (layouts, custom views, related lists)."""

    def __init__(self, auth: ZohoAuth):
        self.auth = auth
        self.base = config.get_crm_base()

    # --- Layouts ---

    def get_layouts(self, module: str) -> list:
        resp = self.auth.request(
            "GET",
            f"{self.base}/settings/layouts",
            params={"module": module},
        )

        return resp.json().get("layouts", [])

    def get_layout(self, module: str, layout_id: str) -> dict:
        resp = self.auth.request(
            "GET",
            f"{self.base}/settings/layouts/{layout_id}",
            params={"module": module},
        )

        layouts = resp.json().get("layouts", [])
        return layouts[0] if layouts else {}

    # --- Custom Views ---

    def get_custom_views(self, module: str) -> list:
        resp = self.auth.request(
            "GET",
            f"{self.base}/settings/custom_views",
            params={"module": module},
        )

        return resp.json().get("custom_views", [])

    def get_custom_view(self, module: str, view_id: str) -> dict:
        resp = self.auth.request(
            "GET",
            f"{self.base}/settings/custom_views/{view_id}",
            params={"module": module},
        )

        views = resp.json().get("custom_views", [])
        return views[0] if views else {}

    # --- Related Lists ---

    def get_related_lists(self, module: str) -> list:
        resp = self.auth.request(
            "GET",
            f"{self.base}/settings/related_lists",
            params={"module": module},
        )

        return resp.json().get("related_lists", [])

    # --- Field Metadata (extended) ---

    def get_field_metadata(self, module: str, field_id: str | None = None) -> list | dict:
        """Get detailed field metadata. If field_id given, returns single field."""
        if field_id:
            resp = self.auth.request(
                "GET",
                f"{self.base}/settings/fields/{field_id}",
                params={"module": module},
            )
    
            fields = resp.json().get("fields", [])
            return fields[0] if fields else {}

        resp = self.auth.request(
            "GET",
            f"{self.base}/settings/fields",
            params={"module": module},
        )

        return resp.json().get("fields", [])

    # --- Module Metadata ---

    def get_module_metadata(self, module: str | None = None) -> list | dict:
        """Get module metadata. If module given, returns single module detail."""
        if module:
            resp = self.auth.request("GET", f"{self.base}/settings/modules/{module}")
        else:
            resp = self.auth.request("GET", f"{self.base}/settings/modules")

        modules = resp.json().get("modules", [])
        if module:
            return modules[0] if modules else {}
        return modules
