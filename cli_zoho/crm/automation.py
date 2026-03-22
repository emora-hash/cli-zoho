"""Zoho CRM Automation API client — workflows, blueprints, scoring rules, assignment rules."""

from cli_zoho import config
from cli_zoho.auth import ZohoAuth


class AutomationClient:
    """Zoho CRM automation operations (workflows, blueprints, scoring, assignments)."""

    def __init__(self, auth: ZohoAuth):
        self.auth = auth
        self.base = config.get_crm_base()

    # --- Workflows ---

    def get_workflows(self, *, module: str | None = None) -> list:
        params = {}
        if module:
            params["module"] = module
        resp = self.auth.request("GET", f"{self.base}/settings/automation/workflow_rules", params=params)
        return resp.json().get("workflow_rules", [])

    def get_workflow(self, rule_id: str) -> dict:
        resp = self.auth.request("GET", f"{self.base}/settings/automation/workflow_rules/{rule_id}")
        return resp.json().get("workflow_rules", [{}])[0]

    def update_workflow(self, rule_id: str, data: dict) -> dict:
        resp = self.auth.request(
            "PUT",
            f"{self.base}/settings/automation/workflow_rules/{rule_id}",
            json={"workflow_rules": [data]},
        )
        return resp.json()

    def delete_workflow(self, rule_id: str) -> dict:
        resp = self.auth.request("DELETE", f"{self.base}/settings/automation/workflow_rules/{rule_id}")
        return resp.json()

    def reorder_workflows(self, module: str, rule_ids: list[str]) -> dict:
        resp = self.auth.request(
            "PUT",
            f"{self.base}/settings/automation/workflow_rules/reorder",
            params={"module": module},
            json={"workflow_rules": [{"id": rid} for rid in rule_ids]},
        )
        return resp.json()

    def workflow_usage_report(self) -> dict:
        resp = self.auth.request("GET", f"{self.base}/settings/automation/workflow_rules/usage_report")
        return resp.json()

    def workflow_limits(self) -> dict:
        resp = self.auth.request("GET", f"{self.base}/settings/automation/workflow_rules/limits")
        return resp.json()

    def workflow_actions_count(self, rule_id: str) -> dict:
        resp = self.auth.request(
            "GET", f"{self.base}/settings/automation/workflow_rules/{rule_id}/actions/count"
        )
        return resp.json()

    # --- Blueprint ---

    def get_blueprint(self, module: str, record_id: str) -> dict:
        resp = self.auth.request("GET", f"{self.base}/{module}/{record_id}/actions/blueprint")
        return resp.json().get("blueprint", {})

    def update_blueprint(self, module: str, record_id: str, transition_id: str, data: dict) -> dict:
        payload = {
            "blueprint": [
                {
                    "transition_id": transition_id,
                    "data": data,
                }
            ]
        }
        resp = self.auth.request("PUT", f"{self.base}/{module}/{record_id}/actions/blueprint", json=payload)
        return resp.json()

    # --- Scoring Rules ---

    def get_scoring_rules(self, *, module: str | None = None) -> list:
        params = {}
        if module:
            params["module"] = module
        resp = self.auth.request("GET", f"{self.base}/settings/automation/scoring_rules", params=params)
        return resp.json().get("scoring_rules", [])

    def create_scoring_rule(self, data: dict) -> dict:
        resp = self.auth.request(
            "POST",
            f"{self.base}/settings/automation/scoring_rules",
            json={"scoring_rules": [data]},
        )
        return resp.json()

    def update_scoring_rule(self, rule_id: str, data: dict) -> dict:
        resp = self.auth.request(
            "PUT",
            f"{self.base}/settings/automation/scoring_rules/{rule_id}",
            json={"scoring_rules": [data]},
        )
        return resp.json()

    def delete_scoring_rule(self, rule_id: str) -> dict:
        resp = self.auth.request("DELETE", f"{self.base}/settings/automation/scoring_rules/{rule_id}")
        return resp.json()

    def execute_scoring_rule(self, rule_id: str, module: str) -> dict:
        resp = self.auth.request(
            "PUT",
            f"{self.base}/settings/automation/scoring_rules/{rule_id}/actions/execute",
            params={"module": module},
        )
        return resp.json()

    # --- Assignment Rules ---

    def get_assignment_rules(self, *, module: str | None = None) -> list:
        params = {}
        if module:
            params["module"] = module
        resp = self.auth.request("GET", f"{self.base}/settings/automation/assignment_rules", params=params)
        return resp.json().get("assignment_rules", [])
