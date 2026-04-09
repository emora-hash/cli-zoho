"""Zoho CRM Settings API client — pipelines, variables, business hours, fiscal year."""

from cli_zoho import config
from cli_zoho.zoho_cli_auth import ZohoAuth


class SettingsClient:
    """Zoho CRM settings operations (pipelines, variables, business hours, fiscal year)."""

    def __init__(self, auth: ZohoAuth):
        self.auth = auth
        self.base = config.get_crm_base()

    # --- Pipelines ---

    def get_pipelines(self, *, layout_id: str | None = None) -> list:
        params = {}
        if layout_id:
            params["layout_id"] = layout_id
        resp = self.auth.request("GET", f"{self.base}/settings/pipeline", params=params)
        if resp.status_code == 204:
            return []
        return resp.json().get("pipeline", [])

    def create_pipeline(self, data: dict) -> dict:
        resp = self.auth.request(
            "POST",
            f"{self.base}/settings/pipeline",
            json={"pipeline": [data]},
        )

        return resp.json()

    def update_pipeline(self, pipeline_id: str, data: dict) -> dict:
        resp = self.auth.request(
            "PUT",
            f"{self.base}/settings/pipeline/{pipeline_id}",
            json={"pipeline": [data]},
        )

        return resp.json()

    # --- Variables (CRM Variables) ---

    def get_variables(self) -> list:
        resp = self.auth.request("GET", f"{self.base}/settings/variables")
        if resp.status_code == 204:
            return []
        return resp.json().get("variables", [])

    def create_variable(self, data: dict) -> dict:
        resp = self.auth.request(
            "POST",
            f"{self.base}/settings/variables",
            json={"variables": [data]},
        )

        return resp.json()

    def update_variable(self, variable_id: str, data: dict) -> dict:
        resp = self.auth.request(
            "PUT",
            f"{self.base}/settings/variables/{variable_id}",
            json={"variables": [data]},
        )

        return resp.json()

    def delete_variable(self, variable_id: str) -> dict:
        resp = self.auth.request("DELETE", f"{self.base}/settings/variables/{variable_id}")

        return resp.json()

    def get_variable_groups(self) -> list:
        resp = self.auth.request("GET", f"{self.base}/settings/variable_groups")

        return resp.json().get("variable_groups", [])

    # --- Business Hours ---

    def get_business_hours(self) -> dict:
        resp = self.auth.request("GET", f"{self.base}/settings/business_hours")

        return resp.json().get("business_hours", {})

    def update_business_hours(self, data: dict) -> dict:
        resp = self.auth.request(
            "PUT",
            f"{self.base}/settings/business_hours",
            json={"business_hours": data},
        )

        return resp.json()

    # --- Fiscal Year ---

    def get_fiscal_year(self) -> dict:
        resp = self.auth.request("GET", f"{self.base}/settings/fiscal_year")

        return resp.json().get("fiscal_year", {})

    def update_fiscal_year(self, data: dict) -> dict:
        resp = self.auth.request(
            "PUT",
            f"{self.base}/settings/fiscal_year",
            json={"fiscal_year": data},
        )

        return resp.json()

    # --- Currencies ---

    def enable_multi_currency(self, data: dict) -> dict:
        resp = self.auth.request(
            "POST",
            f"{self.base}/org/currencies",
            json={"currencies": [data]},
        )

        return resp.json()
