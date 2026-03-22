# cli-zoho: Comprehensive State of the Project & Improvement Design

**Date:** 03-22-2026
**Author:** Eduardo Mora / Claude Opus 4.6
**Status:** Planning — ready for implementation session

---

## 1. Problem Statement

Zoho CRM and Zoho Inventory are powerful platforms, but their developer tooling has a critical gap: **there is no unified, lightweight CLI for data operations across both systems.**

Zoho offers three official CLIs, none of which solve this problem:

| Tool | Package | Purpose | Data API Access |
|------|---------|---------|-----------------|
| **zet** | `zoho-extension-toolkit` | Build/package CRM widgets | None |
| **zdk** | ZDK CLI (npm) | Pull/push CRM metadata (modules, fields, layouts) like git | Config only, no record CRUD |
| **@zohofinance/cli** | npm | Push/pull custom function code (Deluge alternatives in Java/Node/Python) to Books/Inventory | None — code deployment only |

Zoho also publishes **official Python SDKs** (`zohocrm-python-sdk-8.0`, etc.) and **OpenAPI specs** (`crm-oas`). The SDK is auto-generated from OAS, covers the full API surface, but is a thick wrapper — hundreds of classes, complex initialization, and a dependency tree that makes it unsuitable for scripting, agent toolchains, or terminal use.

The **MCP landscape** is equally sparse:
- **Zoho's hosted MCP** (zoho.com/mcp) — closed-source, early access waitlist, 15+ apps, ~30K token footprint. Not self-hostable.
- **zoho/analytics-mcp-server** — Zoho's only open-source MCP. Analytics only, Docker-only.
- **kkeeling/zoho-mcp** (37 stars) — Books only, FastMCP, solid auth/retry patterns.
- **Mgabr90/zoho-mcp-server** (2 stars) — CRM+Books stub, 6 commits.
- No unified CRM+Inventory MCP or CLI exists in the public ecosystem.

**cli-zoho fills this gap**: a single `pip install`, 57 commands, CRM v8 + Inventory v1, designed for both human terminal use and AI agent pipelines.

---

## 2. Competitive Positioning

### What exists vs what cli-zoho does

```
                          Zoho SDKs    zdk CLI    Zoho MCP    kkeeling    cli-zoho
                          ---------    -------    --------    --------    --------
CRM record CRUD              Y           N           Y           N          Y
CRM COQL queries             Y           N           Y           N          Y
CRM metadata/config          Y           Y           ?           N          Y
CRM automation               Y           N           ?           N          Y
Inventory CRUD               N*          N           ?           Y(Books)   Y
Unified CRM+Inventory        N           N           ?           N          Y
Token caching to disk        N           Y           ?           Y          Y
Rate limit w/ backoff+jitter N           ?           ?           Y          Y
Agent-native (--json)        N           Y           Y           Y          Y
v8 field auto-resolution     N           N           N           N          Y
COQL WHERE auto-inject (v8)  N           N           N           N          Y
Self-contained (~2K LOC)     N(~50K)     N           N           Y(~2K)     Y
pip installable              Y           N(npm)      N           Y          Y
```

*Zoho has no official Inventory Python SDK — only Books SDK, which shares some endpoints.

### cli-zoho's unique contributions
1. **First unified CRM v8 + Inventory v1 CLI** — no other tool covers both
2. **v8 compatibility layer** — auto-resolves required `fields` param, auto-injects COQL `WHERE` clause
3. **Agent-native design** — `--json` on every command, structured pagination envelopes, exit codes
4. **Production auth** — disk-cached tokens, global rate limit state, exponential backoff with jitter, 401 auto-refresh, credential-safe (form body, not URL params)

---

## 3. Current Architecture

### 3.1 Project Structure (18 source files, ~2,045 LOC)

```
cli_zoho/
  __init__.py                  3 LOC    Version
  main.py                     85 LOC    Click entry point, auth/info groups
  auth.py                    204 LOC    OAuth2 with disk cache, retry, backoff
  config.py                  138 LOC    URLs, env vars, entity definitions
  shared/
    errors.py                104 LOC    Exception hierarchy + Zoho error map
    output.py                 90 LOC    JSON/table render, field filter, parse_data
    pagination.py             66 LOC    CRM + Inventory pagination helpers
  crm/
    client.py                136 LOC    CRM v8 API client (CRUD, search, COQL, fields, modules)
    commands.py              185 LOC    9 core commands + Phase B subgroup registration
    automation.py            141 LOC    Workflows, blueprint, scoring, assignments
    automation_commands.py   271 LOC    15 Click commands
    metadata.py              102 LOC    Layouts, views, related lists, field/module metadata
    metadata_commands.py     112 LOC    5 Click commands
    settings.py              122 LOC    Pipelines, variables, org settings
    settings_commands.py     230 LOC    11 Click commands
  inventory/
    client.py                104 LOC    Inventory v1 API client (CRUD, search, fields)
    commands.py              152 LOC    8 Click commands
tests/                      ~1,820 LOC  128 tests across 9 files
```

### 3.2 Command Hierarchy (57 leaf commands)

```
cli-zoho
  auth     status | refresh
  info     version | org
  crm
    list | get | create | update | delete | search | query | fields | modules
    workflows    list | get | update | delete | reorder | usage | limits | actions-count
    blueprint    get | advance
    scoring      list | create | update | delete | execute
    assignments  list
    layouts      list | get
    views        list | get
    related-lists  list
    pipelines    list | create | update
    variables    list | create | update | delete | groups
    org-settings business-hours | fiscal-year | update-business-hours |
                 update-fiscal-year | enable-multi-currency
  inv (alias: inventory)
    list | get | create | update | delete | search | fields | entities
```

### 3.3 Auth Lifecycle

```
CLI invocation
  -> ZohoAuth.__init__()
     -> _load_cached_token() from ~/.cli-zoho/.token_cache
        -> If valid (expires_at - 60s > now): use cached token
        -> If expired/missing: _access_token = None

  -> First API call triggers access_token property
     -> If None or expired: refresh()
        -> POST accounts.zoho.com/oauth/v2/token (form body)
        -> Save to disk cache (chmod 600)
     -> Return cached token

  -> request() wraps every HTTP call:
     -> _check_global_rate_limit() — sleep if 429 cooldown active
     -> Retry loop (4 attempts max):
        401 (attempt 0): refresh token, retry
        429: exponential backoff (1s, 2s, 4s) with ±25% jitter + global cooldown
        5xx: exponential backoff, retry
        else: return response
```

### 3.4 Entity Coverage

**CRM (11 modules):** Deals, Contacts, Accounts, Leads, Invoices, Sales_Orders, Quotes, Calls, Cases, Tasks, DialPad_Logs

**Inventory (13 entities):** items, item_groups, packages, shipments, purchase_orders, purchase_receives, bills, payments_made, vendors, sales_orders, customers, transfer_orders, contact_persons

### 3.5 Dependencies

```
Runtime:  click >= 8.1, requests >= 2.31
Dev:      pytest >= 7.0, pytest-mock >= 3.0
Dead:     responses >= 0.23 (listed but never imported)
Python:   >= 3.10 (match/case, X | Y unions)
```

### 3.6 E2E Validation Status (03-22-2026)

| Test | Status | Notes |
|------|--------|-------|
| Auth status (CRM v8) | PASS | Token cached, reused across invocations |
| CRM list Deals | PASS | v8 fields auto-resolved from curated defaults |
| CRM COQL query | PASS | WHERE auto-injected |
| CRM fields (Contacts) | PASS | 121 fields returned |
| CRM modules | PASS | 101 modules |
| Inventory list items | PASS | page_context pagination confirmed |
| Inventory get item | PASS | Singular key extraction |
| Inventory search | PASS | search_text on list endpoint, entity key response |
| Inventory sales orders | PASS | |

---

## 4. Research Findings

### 4.1 CRM v8 Breaking Changes (discovered this session)

**v8 requires `fields` parameter on GET /{module}** — v7 returned all default fields automatically. Without `fields`, v8 returns `REQUIRED_PARAM_MISSING`. This is undocumented in Zoho's migration guides. Neither the official SDK auto-generated code nor any third-party MCP handles this correctly — they either use v7 or pass `fields` as optional.

**v8 requires WHERE clause in COQL** — v7 accepted `SELECT ... FROM ... LIMIT N`. v8 returns `SYNTAX_ERROR: missing clause: where`. The fix is injecting `WHERE id IS NOT NULL` as a no-op predicate.

**v8 introduces page_token pagination** — beyond record 2000, traditional page/per_page fails. Must use `next_page_token` from the `info` response. Tokens are user-specific, expire after 24 hours, and are bound to the original request params.

### 4.2 Zoho OAuth Rate Limiting (discovered this session)

Zoho's OAuth token endpoint (`accounts.zoho.com/oauth/v2/token`) has aggressive rate limiting. During development, we hit `"You have made too many requests continuously"` after ~8 rapid token refreshes. The cooldown period exceeds 2 minutes. This confirms that disk-based token caching is not optional — it's mandatory for any tool making multiple CLI invocations.

### 4.3 kkeeling/zoho-mcp Patterns (adopted this session)

From the most mature open-source Zoho MCP (Books, 37 stars):
- **Disk token cache** with `expires_at` + 60s buffer — adopted
- **Global `_rate_limit_retry_after` state** — adopted
- **Exponential backoff** `min(1.0 * 2^attempt, 60.0)` with ±25% jitter — adopted
- **5-minute response cache** with MD5 key — not yet adopted
- **Pydantic v2 input validation** — not yet adopted
- **Error class hierarchy** with `sanitize_error_message()` — partially adopted

### 4.4 Zoho Official CLI Landscape

| CLI | npm Package | What it Does | Gap it Fills |
|-----|-------------|--------------|-------------|
| **zet** | `zoho-extension-toolkit` | Build/validate/pack CRM widgets. `zet init`, `zet run`, `zet validate`, `zet pack` | Widget development only |
| **zdk** | ZDK CLI | Git-like pull/push for CRM metadata (modules, fields, layouts, functions). `zdk org:pull`, `zdk org:push`, conflict resolution, `.zdkignore`. Sandbox-only in beta. | CRM config version control |
| **@zohofinance/cli** | `@zohofinance/cli` | Push/pull custom function code (Deluge alternatives in Java/Node/Python) to Books/Inventory. `login`, `pull`, `execute`, `push`, `logout` | Custom function deployment |

**Critical insight:** None of these handle data operations (record CRUD, queries, search). They are all development/deployment tools. cli-zoho is the only CLI for runtime data access.

### 4.5 Zoho Official SDKs (GitHub: zoho/)

220 repos on github.com/zoho. CRM Python SDKs for every API version:
- `zohocrm-python-sdk-8.0` (v8, 7 stars) — latest, auto-generated from OAS
- `zohocrm-python-sdk-7.0`, `6.0`, `5.0`, `2.1`, `2.0`, `zcrm-python-sdk` (legacy)
- `crm-oas` — OpenAPI spec files for CRM

The v8 SDK is comprehensive but heavy — hundreds of auto-generated model classes, multi-file initialization, token store abstraction. Not suitable for quick CLI use or agent toolchains. cli-zoho's ~2K LOC achieves 80% of the same coverage with 2% of the code.

---

## 5. Full Audit — Issues by Priority

### P0 — Will break in production

| # | Issue | Location | Impact |
|---|-------|----------|--------|
| 1 | **US-only datacenter** — `ZOHO_TOKEN_URL` hardcoded to `accounts.zoho.com`. EU/IN/AU/JP/CA orgs fail silently at auth. | `config.py:5` | Blocks all non-US users |
| 2 | **`raise_for_zoho()` is dead code** — defined in `errors.py`, imported in `auth.py`, but never called anywhere. All HTTP errors surface as raw `requests.HTTPError`. The entire typed error hierarchy is unused. | `shared/errors.py`, all clients | No structured error handling at runtime |
| 3 | **`refresh()` raises `RuntimeError`** not `AuthenticationError` — inconsistent with the error hierarchy | `auth.py:35` | Auth errors not catchable by type |

### P1 — Functional gaps

| # | Issue | Location | Impact |
|---|-------|----------|--------|
| 4 | **Field cache lost per invocation** — `CRMClient._field_cache` is in-memory only. Every `crm list` call re-fetches fields from settings/fields API. | `crm/client.py:17` | Extra API call per list command |
| 5 | **`crm get` returns `{}` silently on not-found** — no error raised when record doesn't exist | `crm/client.py:22` | Misleading empty output |
| 6 | **No `--verbose`/`--debug` flag** — logging infrastructure exists (`logger = logging.getLogger`) but no way to enable it from CLI | `main.py` | Can't debug API issues |
| 7 | **`_MODULE_DEFAULTS` may not match all modules** — e.g., Tasks, Calls, custom modules have different field names. Unknown modules fall back to `id,Owner,Created_Time,Modified_Time` which works but shows minimal data. | `crm/client.py:28` | Sparse output for unlisted modules |
| 8 | **No auto-paginate `--all` flag** — users must manually loop `--page 1`, `--page 2`, etc. | All list commands | Tedious for bulk retrieval |
| 9 | **JSON parsing duplicated 10+ times** — `json.loads(data)` with try/except in every command file | automation_commands, settings_commands | Maintainability |
| 10 | **`responses` dev dependency unused** — listed in pyproject.toml, never imported | `pyproject.toml` | Dead dependency |
| 11 | **`DEFAULT_PAGE_SIZE = 10` defined but never read** — each Click option hard-codes `default=10` independently | `config.py:9`, all commands | Config not centralized |

### P2 — Missing for publishable quality

| # | Issue | Location | Impact |
|---|-------|----------|--------|
| 12 | **No `setup.cfg` or `pyproject.toml` classifiers** — missing PyPI metadata for discoverability | `pyproject.toml` | Can't publish to PyPI properly |
| 13 | **No README.md** — no documentation for external users | project root | Unpublishable |
| 14 | **No `--dry-run` on destructive operations** | create/update/delete commands | Safety risk |
| 15 | **No confirmation prompt on delete** | delete commands | Safety risk |
| 16 | **No `--output-file` option** | All commands | Can't redirect cleanly |
| 17 | **Table output silently drops columns 9+** and truncates values at 30 chars with no indication | `shared/output.py:52` | Hidden data loss |
| 18 | **No `--pretty` flag for formatted JSON** | All commands | Agent-friendly but human-unfriendly |
| 19 | **`crm update`, `crm delete`, `inv update`, `inv delete` have zero tests** | tests/ | Untested destructive ops |
| 20 | **`info org` command has zero tests** | tests/ | |

---

## 6. API Coverage Gap Analysis

### CRM v8 — Top Missing Endpoints (by super-admin value)

| Priority | Category | Endpoints | Why Valuable |
|----------|----------|-----------|-------------|
| HIGH | Users/Roles/Profiles | `/users`, `/settings/roles`, `/settings/profiles` | User management without admin UI |
| HIGH | Bulk Read/Write | `/bulk/read`, `/bulk/write` | Mass exports, data migrations |
| HIGH | Mass Operations | mass-delete, mass-update, convert-lead, inventory-convert | Bulk ops via CLI |
| HIGH | Notes | `/{module}/{id}/notes` | Add/read notes without opening UI |
| HIGH | Tags | `/settings/tags`, add/remove on records | Bulk segmentation |
| HIGH | Related Records | `/{module}/{id}/{related_api_name}` | Manage deal-contact links, line items |
| HIGH | Recycle Bin | `/recycle_bin` | Recover deleted records |
| HIGH | Composite API | `/composite` | Batch multiple calls in one request |
| MEDIUM | Email/Activities | `/Emails` send/view | Email activity audit |
| MEDIUM | Attachments | `/{module}/{id}/Attachments` | File management |

### Inventory v1 — Top Missing Endpoints

| Priority | Category | Endpoints | Why Valuable |
|----------|----------|-----------|-------------|
| HIGH | Invoices | `/invoices` | Central billing object |
| HIGH | Sales Returns | `/salesreturns` | Returns flow (matches JMA project) |
| HIGH | Credit Notes | `/creditnotes` | Tied to returns/refunds |
| HIGH | Customer Payments | `/customerpayments` | Payment tracking |
| HIGH | Composite Items | `/compositeitems` | Kits/bundles |
| HIGH | Item Adjustments | `/inventoryadjustments` | Stock corrections without UI |
| HIGH | Warehouses | `/locations` | Multi-warehouse management |
| HIGH | Price Lists | `/pricebooks` | Pricing operations |
| HIGH | Status Transitions | mark-as-confirmed, void, delivered, etc. | Status changes without UI |

---

## 7. Design Principles for Next Phase

### 7.1 What Makes This Publishable

cli-zoho is positioned to be the **first open-source, unified Zoho CRM+Inventory CLI**. To be publishable:

1. **Solve v8 properly** — we're the only tool handling `fields` and COQL WHERE requirements. Document this as a feature, not a workaround.
2. **Multi-region support** — handle all Zoho datacenters (US, EU, IN, AU, JP, CA). This alone blocks every non-US Zoho org.
3. **Production error handling** — wire `raise_for_zoho()` into the actual call chain. Typed errors for agents.
4. **Documentation** — README with quickstart, examples, architecture diagram.
5. **PyPI publication** — proper classifiers, license, entry points.

### 7.2 Architecture Improvements

**Response caching (from kkeeling):** 5-minute in-memory cache with MD5(method+url+params) key for GET requests. Eliminates redundant field discovery calls within a session.

**Field cache persistence:** Write resolved field lists to `~/.cli-zoho/field_cache.json` with module-level TTL. Eliminates the settings/fields API call on every `crm list` invocation.

**Plugin architecture for new entities:** Instead of hardcoding `CRM_ENTITIES` and `INVENTORY_ENTITIES`, support a `~/.cli-zoho/entities.json` override file. Users can add custom modules without modifying source.

**Structured output modes:**
- `--json` (current) — compact single-line JSON
- `--json --pretty` — indented JSON
- `--table` (current default) — aligned columns
- `--csv` — for piping to spreadsheets/scripts
- `--fields` — both API-side filtering and output filtering (current)

### 7.3 Agent Integration Layer

cli-zoho's `--json` mode makes it immediately usable as a tool in AI agent pipelines:

```bash
# Claude Code agent can call:
cli-zoho crm query "select Deal_Name, Amount from Deals where Stage = 'Qualification'" --json

# Pipe to jq for field extraction:
cli-zoho inv list items --limit 50 --json | jq '.data[] | {name, sku, stock_on_hand}'

# Use in n8n Execute Command nodes:
cli-zoho crm get Deals 6171402000012868034 --json
```

Future: publish as an MCP server too — the same client code can serve both CLI and MCP transport. FastMCP wrapping of `CRMClient` and `InventoryClient` would take ~100 LOC.

---

## 8. Proposed Improvement Phases

### Phase 1: Production Hardening (wire what exists)
- Wire `raise_for_zoho()` into all client methods (replace `raise_for_status()`)
- Add multi-region support (`ZOHO_REGION` env var → domain mapping)
- Fix `refresh()` to raise `AuthenticationError`
- Add `--verbose`/`--debug` flag
- Remove dead `responses` dependency
- Centralize `DEFAULT_PAGE_SIZE` usage
- Add `--dry-run` on destructive ops
- Fill test gaps (update, delete, info org, errors.py)

### Phase 2: Performance & UX
- Field cache persistence to disk
- Response caching (5-min TTL, GET only)
- Auto-paginate `--all` flag
- `--pretty` JSON flag
- `--csv` output mode
- Table output: show column count indicator when truncated
- Consolidate duplicated JSON parsing into `parse_json_arg()`

### Phase 3: API Expansion (HIGH priority gaps)
- CRM: Users, Roles, Profiles
- CRM: Notes, Tags, Related Records
- CRM: Bulk Read/Write
- Inventory: Invoices, Sales Returns, Credit Notes
- Inventory: Item Adjustments, Warehouses, Price Lists
- Inventory: Status transition commands

### Phase 4: Publication
- README.md with quickstart, examples, architecture
- PyPI classifiers, license (MIT), entry points
- GitHub repo setup, CI/CD (pytest + type check)
- MCP server wrapper (~100 LOC FastMCP over existing clients)
- Blog post / announcement

---

## 9. Metrics Summary

```
Source files .............. 18
Source LOC ................ 2,045
Test files ............... 9
Test LOC ................. 1,820
Tests passing ............ 128
CLI commands .............. 57
CRM modules covered ....... 11
Inventory entities ........ 13
CRM endpoints implemented . 38
Inventory endpoints ....... 7 (CRUD + search + fields per entity)
Dependencies (runtime) .... 2 (click, requests)
Python version ............ >= 3.10
Token cache ............... ~/.cli-zoho/.token_cache (chmod 600)
```

---

*This document serves as the comprehensive context for a one-shot planning session. All research, audit findings, and design decisions are captured here so a fresh agent can produce a complete implementation plan without re-reading the codebase.*
