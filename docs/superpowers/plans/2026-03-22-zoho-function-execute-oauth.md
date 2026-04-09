# Zoho CRM Function Execute — OAuth Scope Resolution

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Resolve the "invalid oauth scope" error blocking REST API execution of standalone Zoho CRM Functions, then ship `cli-zoho crm functions execute` command.

**Architecture:** Three-phase approach — Phase 1 adds the documented OAuth scope (`ZohoCRM.functions.execute.CREATE`) to the Server-based client and regenerates the refresh token. Phase 2 implements the CLI command with TDD. Phase 3 audits Zoho Inventory automation endpoints.

**Tech Stack:** Python 3.10+, Click, requests, pytest, GCP Secret Manager (via `~/.salted/load-secrets.sh`)

---

## Root Cause (confirmed 03-22-2026)

**Zoho CRM function execution does NOT work with OAuth.** Despite the official docs at
`serverless-fn-oauth.html` documenting scopes `ZohoCRM.functions.execute.READ` (GET) and
`ZohoCRM.functions.execute.CREATE` (POST), these scopes **do not exist** in Zoho's OAuth system.
The token refresh endpoint rejects them with `invalid_scope`.

**Working auth method: API Key** (`auth_type=apikey`). Each function has its own API key,
set in Zoho CRM > Setup > Developer Hub > Functions > [function] > REST API.

Verified: `POST .../crm/v7/functions/test_ping/actions/execute?auth_type=apikey&zapikey=<key>`
returns `{"code":"success","details":{"output":"pong"}}`.

**CLI implication:** The `crm functions execute` command defaults to `--auth-type apikey`
and requires `--api-key` (or reads from env/config). OAuth auth is kept as an option
in case Zoho fixes the scopes in the future, but is not expected to work.

---

## File Structure

### Phase 1 — Scope Fix (manual + verification script)

| File | Purpose |
|------|---------|
| `scripts/verify_function_scope.py` | Verify function execute works after scope fix |

### Phase 2 — Implementation (permanent code)

| File | Purpose |
|------|---------|
| `cli_zoho/crm/functions.py` | Function execution API client |
| `cli_zoho/crm/functions_commands.py` | Click commands for `crm functions execute` |
| `tests/test_crm_functions.py` | Unit tests for function client |
| `tests/test_crm_functions_commands.py` | CLI integration tests |

### Phase 3 — Inventory Audit

| File | Purpose |
|------|---------|
| `scripts/audit_inventory_automation.py` | Probe Inventory automation endpoints |

---

## Phase 1: Complete ✅

Scope investigation resolved — API key auth works. OAuth scopes are invalid.
Verified with test_ping API key: `1003.80dd86dd...686160`

---

## Phase 2: Implementation

### Task 4: Write failing tests for function client

**Files:**
- Create: `tests/test_crm_functions.py`

- [ ] **Step 1: Write the failing test**

```python
"""Tests for Zoho CRM function execution client."""

from unittest.mock import MagicMock

from cli_zoho.crm.functions import FunctionsClient


class TestFunctionsClient:
    """Tests for FunctionsClient."""

    def setup_method(self):
        self.auth = MagicMock()
        self.client = FunctionsClient(self.auth)

    def test_execute_function_success(self):
        """Execute a standalone function and get the response."""
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = {
            "code": "success",
            "details": {"output": '"pong"', "id": "test_ping"},
            "message": "function executed successfully",
        }
        self.auth.request.return_value = mock_resp

        result = self.client.execute("test_ping")

        assert result["code"] == "success"
        assert result["details"]["output"] == '"pong"'
        self.auth.request.assert_called_once()
        call_args = self.auth.request.call_args
        assert call_args[0][0] == "POST"
        assert "functions/test_ping/actions/execute" in call_args[0][1]
        assert call_args[1]["params"]["auth_type"] == "oauth"

    def test_execute_function_with_arguments(self):
        """Execute a function with input arguments."""
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = {
            "code": "success",
            "details": {"output": '"hello world"'},
            "message": "function executed successfully",
        }
        self.auth.request.return_value = mock_resp

        result = self.client.execute("greet", arguments={"name": "world"})

        assert result["code"] == "success"
        call_args = self.auth.request.call_args
        assert call_args[1]["json"]["arguments"] == {"name": "world"}

    def test_execute_function_with_apikey_auth(self):
        """Execute a function with apikey auth instead of oauth."""
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = {"code": "success"}
        self.auth.request.return_value = mock_resp

        result = self.client.execute("test_ping", auth_type="apikey", api_key="abc123")

        call_args = self.auth.request.call_args
        assert call_args[1]["params"]["auth_type"] == "apikey"
        assert call_args[1]["params"]["zapikey"] == "abc123"

    def test_execute_function_get_method(self):
        """Execute a function with GET method uses READ scope path."""
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = {"code": "success"}
        self.auth.request.return_value = mock_resp

        result = self.client.execute("test_ping", method="GET")

        call_args = self.auth.request.call_args
        assert call_args[0][0] == "GET"

    def test_execute_function_failure(self):
        """Handle function execution errors gracefully."""
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = {
            "code": "failure",
            "details": {"output": "null"},
            "message": "function execution failed",
        }
        self.auth.request.return_value = mock_resp

        result = self.client.execute("bad_function")

        assert result["code"] == "failure"

    def test_execute_uses_v7_endpoint(self):
        """Function execute uses v7 endpoint per Zoho docs."""
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = {"code": "success"}
        self.auth.request.return_value = mock_resp

        self.client.execute("test_ping")

        call_url = self.auth.request.call_args[0][1]
        assert "/crm/v7/functions/test_ping/actions/execute" in call_url
```

- [ ] **Step 2: Run tests — verify they FAIL**

```bash
cd /Users/eduardomora/projects/cli-zoho
python3 -m pytest tests/test_crm_functions.py -v
```

Expected: `ModuleNotFoundError: No module named 'cli_zoho.crm.functions'`

- [ ] **Step 3: Commit failing tests**

```bash
git add tests/test_crm_functions.py
git commit -m "test: add failing tests for CRM function execution client"
```

---

### Task 5: Implement function client (make tests pass)

**Files:**
- Create: `cli_zoho/crm/functions.py`

- [ ] **Step 1: Write minimal implementation**

```python
"""Zoho CRM Functions API client — execute standalone Deluge functions via REST API.

Scopes required:
- GET:  ZohoCRM.functions.execute.READ
- POST: ZohoCRM.functions.execute.CREATE

Docs: https://www.zoho.com/crm/developer/docs/functions/serverless-fn-oauth.html
"""

from cli_zoho import config
from cli_zoho.auth import ZohoAuth


class FunctionsClient:
    """Execute Zoho CRM standalone functions via REST API.

    Endpoint: {GET|POST} /crm/v7/functions/{api_name}/actions/execute
    """

    def __init__(self, auth: ZohoAuth):
        self.auth = auth
        # Derive v7 base from the CRM v8 base (replace v8 → v7)
        self.base = config.get_crm_base().replace("/v8", "/v7")

    def execute(
        self,
        function_name: str,
        *,
        arguments: dict | None = None,
        method: str = "POST",
        auth_type: str = "oauth",
        api_key: str | None = None,
    ) -> dict:
        """Execute a standalone CRM function.

        Args:
            function_name: API name of the function (e.g., "test_ping").
            arguments: Optional dict of input arguments to pass to the function.
            method: HTTP method — "POST" (needs execute.CREATE scope) or
                    "GET" (needs execute.READ scope). Default: POST.
            auth_type: "oauth" (default) or "apikey".
            api_key: Required if auth_type is "apikey".

        Returns:
            Dict with keys: code, details (contains output), message.
        """
        url = f"{self.base}/functions/{function_name}/actions/execute"

        params = {"auth_type": auth_type}
        if auth_type == "apikey" and api_key:
            params["zapikey"] = api_key

        kwargs = {"params": params}
        if arguments and method == "POST":
            kwargs["json"] = {"arguments": arguments}
        elif arguments and method == "GET":
            # For GET, arguments go as query params
            for k, v in arguments.items():
                params[k] = v

        resp = self.auth.request(method, url, **kwargs)
        return resp.json()
```

- [ ] **Step 2: Run tests — verify they PASS**

```bash
cd /Users/eduardomora/projects/cli-zoho
python3 -m pytest tests/test_crm_functions.py -v
```

Expected: All 6 tests PASS.

- [ ] **Step 3: Commit**

```bash
git add cli_zoho/crm/functions.py
git commit -m "feat: add CRM function execution client"
```

---

### Task 6: Write failing tests for CLI commands

**Files:**
- Create: `tests/test_crm_functions_commands.py`

- [ ] **Step 1: Write the failing test**

```python
"""Tests for CRM function execute CLI commands.

Uses the established cli-zoho testing pattern:
- patch.object(ZohoAuth, "refresh") to prevent real token refresh
- patch.object(ZohoAuth, "request") to mock HTTP responses
- conftest.py provides runner, mock_env, and invoke fixtures
"""

import json
from unittest.mock import MagicMock, patch

from cli_zoho.auth import ZohoAuth
from cli_zoho.main import cli


def _mock_resp(payload, status_code=200):
    resp = MagicMock()
    resp.status_code = status_code
    resp.json.return_value = payload
    resp.raise_for_status = MagicMock()
    resp.headers = {}
    return resp


class TestFunctionExecute:
    """Tests for `cli-zoho crm functions execute`."""

    def test_execute_basic(self, runner):
        """Execute a function with no arguments."""
        payload = {
            "code": "success",
            "details": {"output": '"pong"'},
            "message": "function executed successfully",
        }
        with patch.object(ZohoAuth, "refresh", return_value="t"):
            with patch.object(ZohoAuth, "request", return_value=_mock_resp(payload)) as mock_req:
                result = runner.invoke(cli, ["crm", "functions", "execute", "test_ping", "--json"])

        assert result.exit_code == 0
        data = json.loads(result.output)
        assert data["code"] == "success"
        # Verify POST method and correct URL
        call_args = mock_req.call_args
        assert call_args[0][0] == "POST"
        assert "functions/test_ping/actions/execute" in call_args[0][1]
        assert call_args[1]["params"]["auth_type"] == "oauth"

    def test_execute_with_args(self, runner):
        """Execute a function with JSON arguments."""
        payload = {"code": "success", "details": {"output": '"hello world"'}}
        with patch.object(ZohoAuth, "refresh", return_value="t"):
            with patch.object(ZohoAuth, "request", return_value=_mock_resp(payload)) as mock_req:
                result = runner.invoke(
                    cli, ["crm", "functions", "execute", "greet",
                          "--args", '{"name": "world"}', "--json"]
                )

        assert result.exit_code == 0
        call_args = mock_req.call_args
        assert call_args[1]["json"]["arguments"] == {"name": "world"}

    def test_execute_with_apikey(self, runner):
        """Execute a function with API key auth."""
        payload = {"code": "success"}
        with patch.object(ZohoAuth, "refresh", return_value="t"):
            with patch.object(ZohoAuth, "request", return_value=_mock_resp(payload)) as mock_req:
                result = runner.invoke(
                    cli, ["crm", "functions", "execute", "test_ping",
                          "--auth-type", "apikey", "--api-key", "abc123", "--json"]
                )

        assert result.exit_code == 0
        call_args = mock_req.call_args
        assert call_args[1]["params"]["auth_type"] == "apikey"
        assert call_args[1]["params"]["zapikey"] == "abc123"

    def test_execute_get_method(self, runner):
        """Execute with GET method."""
        payload = {"code": "success"}
        with patch.object(ZohoAuth, "refresh", return_value="t"):
            with patch.object(ZohoAuth, "request", return_value=_mock_resp(payload)) as mock_req:
                result = runner.invoke(
                    cli, ["crm", "functions", "execute", "test_ping",
                          "--method", "GET", "--json"]
                )

        assert result.exit_code == 0
        assert mock_req.call_args[0][0] == "GET"

    def test_execute_invalid_json_args(self, runner):
        """Reject invalid JSON in --args — error_out writes to stderr and exits."""
        with patch.object(ZohoAuth, "refresh", return_value="t"):
            result = runner.invoke(
                cli, ["crm", "functions", "execute", "test_ping", "--args", "not-json"]
            )

        assert result.exit_code != 0
```

- [ ] **Step 2: Run tests — verify they FAIL**

```bash
cd /Users/eduardomora/projects/cli-zoho
python3 -m pytest tests/test_crm_functions_commands.py -v
```

Expected: FAIL — commands don't exist yet.

- [ ] **Step 3: Commit**

```bash
git add tests/test_crm_functions_commands.py
git commit -m "test: add failing tests for CRM function execute CLI commands"
```

---

### Task 7: Implement CLI commands (make tests pass)

**Files:**
- Create: `cli_zoho/crm/functions_commands.py`
- Modify: `cli_zoho/crm/commands.py:185-204` (register the new group)

- [ ] **Step 1: Write the Click commands**

```python
"""Click commands for Zoho CRM function execution."""

import json

import click

from cli_zoho.crm.functions import FunctionsClient
from cli_zoho.shared.output import render, error_out


def _client(ctx) -> FunctionsClient:
    return FunctionsClient(ctx.obj["auth"])


@click.group("functions", short_help="CRM function execution")
@click.pass_context
def functions_group(ctx):
    """Execute standalone Deluge functions via REST API."""
    pass


@functions_group.command("execute", short_help="Execute a standalone function")
@click.argument("function_name")
@click.option("--args", "arguments", default=None, help="JSON string of function arguments")
@click.option("--method", default="POST", type=click.Choice(["GET", "POST"]),
              help="HTTP method (default: POST)")
@click.option("--auth-type", default="oauth", type=click.Choice(["oauth", "apikey"]),
              help="Auth method (default: oauth)")
@click.option("--api-key", default=None, help="Per-function API key (required for apikey auth)")
@click.option("--json", "json_mode", is_flag=True, help="JSON output")
@click.option("--quiet", is_flag=True, help="Suppress non-data output")
@click.pass_context
def fn_execute(ctx, function_name, arguments, method, auth_type, api_key, json_mode, quiet):
    """Execute a standalone CRM function by API name.

    Example: cli-zoho crm functions execute test_ping --json
    """
    parsed_args = None
    if arguments:
        try:
            parsed_args = json.loads(arguments)
        except json.JSONDecodeError as e:
            error_out(f"Invalid JSON in --args: {e}")
            return

    if auth_type == "apikey" and not api_key:
        error_out("--api-key is required when --auth-type is apikey")
        return

    client = _client(ctx)
    result = client.execute(
        function_name,
        arguments=parsed_args,
        method=method,
        auth_type=auth_type,
        api_key=api_key,
    )
    render(result, json_mode=json_mode, quiet=quiet)
```

- [ ] **Step 2: Register the functions group in commands.py**

In `cli_zoho/crm/commands.py`, add a new import line after the existing imports at line 193 (after `from cli_zoho.crm.settings_commands import ...`):

```python
from cli_zoho.crm.functions_commands import functions_group
```

And add a new `add_command` line after line 204 (after `crm_group.add_command(org_settings_group)`):

```python
crm_group.add_command(functions_group)
```

**Note:** `cli_zoho/crm/__init__.py` is empty — no changes needed there.

- [ ] **Step 3: Run ALL tests**

```bash
cd /Users/eduardomora/projects/cli-zoho
python3 -m pytest tests/ -v
```

Expected: All tests pass (including existing auth, CRM, inventory tests).

- [ ] **Step 4: Commit**

```bash
git add cli_zoho/crm/functions_commands.py cli_zoho/crm/commands.py
git commit -m "feat: add 'crm functions execute' CLI command"
```

---

### Task 8: Live smoke test

- [ ] **Step 1: Test against Zoho**

```bash
source ~/.salted/load-secrets.sh
rm -f ~/.cli-zoho/.token_cache
cd /Users/eduardomora/projects/cli-zoho
python3 -m cli_zoho crm functions execute test_ping --json
```

Expected:
```json
{
  "code": "success",
  "details": {
    "output": "\"pong\"",
    "id": "test_ping"
  },
  "message": "function executed successfully"
}
```

- [ ] **Step 2: Test with arguments**

```bash
python3 -m cli_zoho crm functions execute test_ping --args '{"key": "value"}' --json
```

- [ ] **Step 3: Test GET method**

```bash
python3 -m cli_zoho crm functions execute test_ping --method GET --json
```

- [ ] **Step 4: Commit any adjustments from live testing**

---

## Phase 3: Zoho Inventory Automation Audit

### Task 9: Audit Inventory automation endpoints

- [ ] **Step 1: Write inventory audit script**

```python
#!/usr/bin/env python3
"""Audit Zoho Inventory for automation/function endpoints.

Tests: workflows, webhooks, custom functions, automation rules.

Usage:
    source ~/.salted/load-secrets.sh
    python3 scripts/audit_inventory_automation.py
"""

import sys
sys.path.insert(0, ".")

from cli_zoho.auth import ZohoAuth
from cli_zoho import config


def main():
    auth = ZohoAuth()
    base = config.get_inventory_base()
    org_id = config.get_org_id()

    endpoints = [
        ("Workflows", f"{base}/settings/workflows?organization_id={org_id}"),
        ("Webhooks", f"{base}/settings/webhooks?organization_id={org_id}"),
        ("Custom Functions", f"{base}/settings/customfunctions?organization_id={org_id}"),
        ("Automation Rules", f"{base}/settings/automationrules?organization_id={org_id}"),
        ("Workflow Rules", f"{base}/settings/workflowrules?organization_id={org_id}"),
    ]

    print("Zoho Inventory Automation Audit")
    print("=" * 60)

    for name, url in endpoints:
        try:
            resp = auth.request("GET", url)
            status = resp.status_code
            body = resp.text[:200]
            marker = "✅" if status == 200 else "⚠️"
        except Exception as e:
            status = getattr(e, "status_code", 0)
            body = str(e)[:200]
            marker = "❌"

        print(f"\n{marker} {name}")
        print(f"   Status: {status}")
        print(f"   Body:   {body}")

    print("\n" + "=" * 60)


if __name__ == "__main__":
    main()
```

- [ ] **Step 2: Run the audit**

```bash
source ~/.salted/load-secrets.sh
python3 scripts/audit_inventory_automation.py
```

- [ ] **Step 3: Commit**

```bash
git add scripts/audit_inventory_automation.py
git commit -m "chore: audit Zoho Inventory automation endpoints"
```

---

## Decision Log

| Decision | Rationale |
|----------|-----------|
| Scope fix before implementation | No point building CLI if we can't authenticate |
| `ZohoCRM.functions.execute.CREATE` scope | Zoho official docs specify this for POST method |
| Full OAuth re-grant needed | Scopes can't be added to existing refresh tokens |
| Self Client fallback path | In case Server-based clients can't use function scopes |
| v7 endpoint (not v8) | Zoho function docs reference v2/v7, not v8 |
| Support both oauth and apikey | Docs show both methods; apikey is simpler for webhooks |
| Support both GET and POST | Different scopes (READ vs CREATE), different use cases |
| Separate Inventory audit | Different API, different scope system |

## Key Reference URLs

- OAuth function scopes: https://www.zoho.com/crm/developer/docs/functions/serverless-fn-oauth.html
- API key auth: https://www.zoho.com/crm/developer/docs/functions/serverless-fn-apikey.html
- Request/response format: https://www.zoho.com/crm/developer/docs/functions/request-response.html
- Input types: https://www.zoho.com/crm/developer/docs/functions/input-type.html
