"""Zoho CRM Users, Roles, and Profiles API client."""

from cli_zoho import config
from cli_zoho.auth import ZohoAuth


class UsersClient:
    """Zoho CRM V8 Users, Roles, and Profiles API operations."""

    def __init__(self, auth: ZohoAuth):
        self.auth = auth
        self.base = config.get_crm_base()

    def get_users(self, type: str = "AllUsers", page: int = 1, per_page: int = 200) -> dict:
        resp = self.auth.request(
            "GET",
            f"{self.base}/users",
            params={"type": type, "page": page, "per_page": per_page},
        )
        return resp.json()

    def get_user(self, user_id: str) -> dict:
        resp = self.auth.request("GET", f"{self.base}/users/{user_id}")
        return resp.json()

    def get_roles(self) -> dict:
        resp = self.auth.request("GET", f"{self.base}/settings/roles")
        return resp.json()

    def get_role(self, role_id: str) -> dict:
        resp = self.auth.request("GET", f"{self.base}/settings/roles/{role_id}")
        return resp.json()

    def get_profiles(self) -> dict:
        resp = self.auth.request("GET", f"{self.base}/settings/profiles")
        return resp.json()

    def get_profile(self, profile_id: str) -> dict:
        resp = self.auth.request("GET", f"{self.base}/settings/profiles/{profile_id}")
        return resp.json()
