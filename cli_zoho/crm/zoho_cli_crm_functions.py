"""Zoho CRM Functions API client — execute standalone Deluge functions via REST API.

Auth: Per-function API key (auth_type=apikey). OAuth scopes do not work (confirmed 03-22-2026).
Docs: https://www.zoho.com/crm/developer/docs/functions/serverless-fn-apikey.html
"""

from cli_zoho import config
from cli_zoho.zoho_cli_auth import ZohoAuth


class FunctionsClient:
    def __init__(self, auth: ZohoAuth):
        self.auth = auth
        self.base = config.get_crm_base().replace("/v8", "/v7")

    def execute(
        self,
        function_name: str,
        *,
        arguments: dict | None = None,
        method: str = "POST",
        auth_type: str = "apikey",
        api_key: str | None = None,
    ) -> dict:
        url = f"{self.base}/functions/{function_name}/actions/execute"
        params = {"auth_type": auth_type}
        if auth_type == "apikey" and api_key:
            params["zapikey"] = api_key

        kwargs = {"params": params}
        if arguments and method == "POST":
            kwargs["json"] = {"arguments": arguments}
        elif arguments and method == "GET":
            for k, v in arguments.items():
                params[k] = v

        resp = self.auth.request(method, url, **kwargs)
        return resp.json()
