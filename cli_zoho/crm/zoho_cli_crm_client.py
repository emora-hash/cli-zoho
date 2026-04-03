"""Zoho CRM API client — thin wrapper around shared auth."""

from cli_zoho import config
from cli_zoho.zoho_cli_auth import ZohoAuth
from cli_zoho.shared.zoho_cli_shared_errors import ResourceNotFoundError
from cli_zoho.shared.zoho_cli_shared_pagination import paginate_crm


class CRMClient:
    """Zoho CRM V8 API operations."""

    def __init__(self, auth: ZohoAuth):
        self.auth = auth
        self.base = config.get_crm_base()
        self._field_cache: dict[str, str] = {}

    # Common CRM fields present on most modules — safe for v8 list endpoint
    _COMMON_FIELDS = "id,Owner,Created_Time,Modified_Time"

    # Module-specific default fields for human-friendly listing
    _MODULE_DEFAULTS: dict[str, str] = {
        "Deals": "Deal_Name,Amount,Stage,Account_Name,Contact_Name,Closing_Date,Lead_Source",
        "Contacts": "Full_Name,Email,Phone,Account_Name,Lead_Source,Created_Time",
        "Leads": "Full_Name,Email,Phone,Company,Lead_Source,Lead_Status,Created_Time",
        "Accounts": "Account_Name,Phone,Website,Industry,Account_Type,Created_Time",
        "Invoices": "Subject,Grand_Total,Status,Account_Name,Invoice_Date,Due_Date",
        "Sales_Orders": "Subject,Grand_Total,Status,Account_Name,Due_Date",
        "Quotes": "Subject,Grand_Total,Stage,Account_Name,Valid_Till",
        "Tasks": "Subject,Status,Priority,Due_Date,Owner",
        "Calls": "Subject,Call_Type,Call_Duration,Call_Start_Time,Owner",
        "Cases": "Subject,Status,Priority,Case_Origin,Owner",
    }

    def _resolve_fields(self, module: str) -> str:
        """Get default field set for a module. Uses curated defaults or common fields."""
        if module not in self._field_cache:
            defaults = self._MODULE_DEFAULTS.get(module, self._COMMON_FIELDS)
            self._field_cache[module] = f"{defaults},{self._COMMON_FIELDS}"
        return self._field_cache[module]

    def list_records(self, module: str, *, limit: int = 10, page: int = 1, fields: str = "") -> dict:
        api_fields = fields if fields else self._resolve_fields(module)
        return paginate_crm(self.auth, module, limit=limit, page=page, fields=api_fields)

    def get_record(self, module: str, record_id: str) -> dict:
        resp = self.auth.request("GET", f"{self.base}/{module}/{record_id}")
        body = resp.json()
        data = body.get("data", [])
        if not data:
            raise ResourceNotFoundError(
                f"Record {record_id} not found in {module}",
                status_code=200, code="RECORD_NOT_FOUND",
            )
        return data[0]

    def create_record(self, module: str, data: dict) -> dict:
        resp = self.auth.request(
            "POST",
            f"{self.base}/{module}",
            json={"data": [data]},
        )
        return resp.json()

    def update_record(self, module: str, record_id: str, data: dict) -> dict:
        resp = self.auth.request(
            "PUT",
            f"{self.base}/{module}/{record_id}",
            json={"data": [data]},
        )
        return resp.json()

    def update_records(self, module: str, records: list[dict]) -> dict:
        """Bulk-update up to 100 records in a single API call.

        Each record dict must include an 'id' key. Zoho returns per-record
        status in the response 'data' list.
        """
        resp = self.auth.request(
            "PUT",
            f"{self.base}/{module}",
            json={"data": records},
        )
        return resp.json()

    def delete_record(self, module: str, record_id: str) -> dict:
        resp = self.auth.request("DELETE", f"{self.base}/{module}/{record_id}")
        return resp.json()

    def search(self, module: str, criteria: str, *, limit: int = 10, page: int = 1) -> dict:
        resp = self.auth.request(
            "GET",
            f"{self.base}/{module}/search",
            params={"criteria": criteria, "page": page, "per_page": min(limit, 200)},
        )
        if resp.status_code == 204:
            return {"data": [], "has_more": False, "next_page": None, "count": 0}
        body = resp.json()
        info = body.get("info", {})
        return {
            "data": body.get("data", []),
            "has_more": info.get("more_records", False),
            "next_page": page + 1 if info.get("more_records") else None,
            "count": len(body.get("data", [])),
        }

    @staticmethod
    def _ensure_where(query: str) -> str:
        """CRM v8 COQL requires a WHERE clause. Inject a no-op if missing."""
        upper = query.upper()
        if " WHERE " not in upper:
            # Insert before ORDER BY, GROUP BY, LIMIT, or end of query
            for keyword in (" ORDER ", " GROUP ", " LIMIT "):
                idx = upper.find(keyword)
                if idx != -1:
                    return query[:idx] + " where id is not null" + query[idx:]
            return query + " where id is not null"
        return query

    def coql_query(self, query: str) -> dict:
        safe_query = self._ensure_where(query)
        resp = self.auth.request(
            "POST",
            f"{self.base}/coql",
            json={"select_query": safe_query},
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

    def get_fields(self, module: str) -> list:
        resp = self.auth.request(
            "GET",
            f"{self.base}/settings/fields",
            params={"module": module},
        )
        return resp.json().get("fields", [])

    def get_modules(self) -> list:
        resp = self.auth.request("GET", f"{self.base}/settings/modules")
        return resp.json().get("modules", [])
