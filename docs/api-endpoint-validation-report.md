---
date: 03-22-2025
type: validation
project: cli-zoho
source: vault knowledge-base + code audit
---

# CLI-Zoho API Endpoint Validation Report

Generated: 03-22-2025
Sources: `/Users/eduardomora/projects/cli-zoho/`, vault at `adjacent-systems/zoho-stack/knowledge-base/`

---

## CRITICAL: CRM Base URL is Wrong Version

**Issue:** `config.py` sets `ZOHO_CRM_BASE = "https://www.zohoapis.com/crm/v2"`.

**Vault says:** The COQL endpoint doc explicitly states `POST https://www.zohoapis.com/crm/v8/coql` and notes _"v8 is current as of March 2026"_. The vault's full v8 API reference lives at `api-reference/v8/` with docs for auth, limits, metadata, core, query, bulk, composite, automation, users, compliance, settings, etc.

**Impact:** All CLI endpoints use the wrong version base. The correct base is:
```
ZOHO_CRM_BASE = "https://www.zohoapis.com/crm/v8"
```

This affects every CRM call: records CRUD, search, COQL, settings/fields, settings/modules, layouts, custom views, related lists, automation, workflows, scoring rules, assignment rules, blueprints.

---

## Correct Endpoints (confirmed against vault docs)

| Client | Endpoint pattern | Status |
|--------|-----------------|--------|
| crm/client.py | `{base}/{module}/{id}` | Correct path structure |
| crm/client.py | `{base}/{module}/search` with `criteria` param | Correct |
| crm/client.py | `{base}/coql` with `select_query` body | Correct (wrong base version) |
| crm/client.py | `{base}/settings/fields?module=X` | Correct |
| crm/client.py | `{base}/settings/modules` | Correct |
| crm/metadata.py | `{base}/settings/layouts?module=X` | Correct |
| crm/metadata.py | `{base}/settings/custom_views?module=X` | Correct |
| crm/metadata.py | `{base}/settings/related_lists?module=X` | Correct |
| crm/automation.py | `{base}/settings/automation/workflow_rules` | Correct path |
| crm/automation.py | `{base}/{module}/{id}/actions/blueprint` | Correct |
| crm/automation.py | `{base}/settings/wizards` | Correct path |
| inventory/client.py | `{base}/items`, `/itemgroups`, `/packages`, etc. | Correct V1 paths |
| inventory/client.py | `X-com-zoho-inventory-organizationid` header | Correct header name |

---

## OAuth Scope Mismatches — Automation Client Will Fail

The vault's scope audit (`api-reference/scopes.md`, verified 03-19-2026) shows these scopes are **NOT active** in the JMA token:

| AutomationClient method | Required scope | JMA token status |
|------------------------|---------------|-----------------|
| `get_workflows()` | `ZohoCRM.settings.workflow_rules.READ` | NOT active — returns OAUTH_SCOPE_MISMATCH |
| `get_workflow()` | same | NOT active |
| `update_workflow()` | `ZohoCRM.settings.workflow_rules.ALL` | NOT active |
| `get_scoring_rules()` | `ZohoCRM.settings.scoring_rules` | NOT active |
| `get_wizards()` | `ZohoCRM.settings.wizards` | NOT active |

The CLI's `AutomationClient` will consistently return `OAUTH_SCOPE_MISMATCH` errors on these until the JMA token scopes are updated. The blueprint endpoints (`/actions/blueprint`) use `ZohoCRM.modules.ALL` which IS active.

---

## Missing Inventory Entities

Entities documented in the vault (`key-fields-by-module/`) but absent from `INVENTORY_ENTITIES` in `config.py`:

| Missing entity | Vault doc |
|---------------|-----------|
| `sales_orders` (Inventory SO, distinct from CRM) | `key-fields-by-module/sales-orders.md` — 1,162 records, primary WooCommerce bridge |
| `invoices` (Inventory invoices) | `key-fields-by-module/` (implied by sales order downstream link) |
| `contacts` (customers in Inventory, not just vendors) | developer-data shows `salesorders.All` scope |
| `transfer_orders` | `key-fields-by-module/transfer-orders.md` |
| `contact_persons` | `key-fields-by-module/contact-persons.md` |

Note: `config.py` has a `vendors` entity that maps to `/contacts?contact_type=vendor`, but there is no `customers` entity for the buyer side (`contact_type=customer`).

---

## API Quirks the CLI Does NOT Handle

Sourced from `~/.claude/projects/-Users-eduardomora/memory/zoho-api.md` and vault rate-limits doc:

### 1. Rate Limits — No Retry Logic
- CRM: 5,000 calls/day per org, 100/minute per token, **10 COQL queries/minute**
- CLI has no 429 retry/backoff logic. Vault documents exact retry strategy: honor `Retry-After` header; exponential backoff 1s/2s/4s/8s/16s; for COQL, wait at least 6s between queries.

### 2. COQL Quirks Not Handled
- **LIMIT silently truncates at 200** — vault note says "Always specify `LIMIT 2000` or results silently truncate at 200." CLI's `coql_query()` sends no LIMIT clause — callers must add it.
- **BETWEEN operator broken on DateTime fields** — vault explicitly warns this.
- **Timezone in DateTime literals: use `Z`, not `+00:00`** — vault documents this as a known quirk.
- **No parentheses around WHERE conditions** — Zoho COQL rejects standard SQL parentheses syntax.

### 3. Inventory `get_record()` Key Extraction Bug
The `singular_key = entity_cfg["list_key"].rstrip("s")` heuristic will produce wrong keys for some entities:
- `purchasereceives` → strips to `purchasereceive` (likely correct but fragile)
- `shipmentorders` → strips to `shipmentorder` (correct)
- `vendorpayments` → strips to `vendorpayment` (correct)
- `contacts` → strips to `contact` (correct)

Not a confirmed bug but a fragile pattern — entity configs should have an explicit `get_key` field.

### 4. Inventory `per_page` Max is 200 — But Zoho Inventory Default is 25
CLI passes `per_page: min(limit, 200)` which is fine for the cap, but Inventory's actual max per page is **200** per the API — this is correct.

### 5. Field API Names Differ Across CRM Modules
Vault documents that `G_clid` / `Google_Click_Identifier` / `Google_Click_ID` are all the same concept but different API names per module. The CLI passes field names through without translation — any agent using the CLI to build COQL queries must handle this upstream.

---

## Missing High-Value CLI Endpoints

Based on vault docs (`api-reference/v8/` sections and Deluge function patterns):

| Missing capability | Vault evidence | Priority |
|-------------------|---------------|----------|
| `GET /crm/v8/org` | Scopes doc: `ZohoCRM.org.READ` is active | High |
| `GET /crm/v8/users` | Scopes doc: `ZohoCRM.users.ALL` is active | High |
| CRM Related Records (`/{module}/{id}/{related_module}`) | Deluge functions extensively use related lists; `relatedlist` connection was created specifically for this | High |
| Inventory Sales Orders as a first-class entity | 1,162 records, primary WooCommerce bridge (`PurchaseOrder` field 99.9%) | High |
| Inventory Customers (`/contacts?contact_type=customer`) | Inventory `inventory_full_access` scope includes contacts | Medium |
| `GET /crm/v8/settings/roles`, `/profiles`, `/territories` | `ZohoCRM.settings.ALL` is active; vault tree shows `09-users-roles-profiles` doc section | Medium |
| Inventory Transfer Orders | `key-fields-by-module/transfer-orders.md` exists | Medium |
| Bulk read API (`/crm/v8/read`, `/crm/v8/write`) | `api-reference/v8/06-bulk-apis/` section exists in vault | Low |
| Composite API | `api-reference/v8/07-composite-api/` section; Deluge uses it for create-invoice-and-payment flows | Low |

---

## CRM_ENTITIES Assessment

Defined in `config.py`:

| Entity | Module value | Assessment |
|--------|-------------|------------|
| deals | Deals | Correct |
| contacts | Contacts | Correct |
| accounts | Accounts | Correct |
| leads | Leads | Correct |
| invoices | Invoices | Correct (CRM invoices) |
| sales_orders | Sales_Orders | Correct |
| quotes | Quotes | Correct |
| calls | Calls | Correct |
| cases | Cases | Correct |
| tasks | Tasks | Correct |
| visit_logs | DialPad_Logs | Questionable — vault has `attach-visitlogs-with-contacts.md` Deluge functions; module name `DialPad_Logs` may not be a standard CRM module accessible via standard records API |

---

## Summary of Actions Required

1. **Change `ZOHO_CRM_BASE` from `crm/v2` to `crm/v8`** — every CRM call is on the wrong API version.
2. **Add retry/backoff logic** — especially for COQL (10/min limit, 6s minimum between queries).
3. **Add `sales_orders` to `INVENTORY_ENTITIES`** — it's the primary WooCommerce order bridge (1,162 records).
4. **Add `customers` to `INVENTORY_ENTITIES`** — buyers distinct from vendors.
5. **Add `CRMClient.get_related_records(module, id, related_module)`** — Deluge functions use this pattern heavily; a dedicated vault connection (`relatedlist`) exists for it.
6. **Add `CRMClient.get_org()` and `CRMClient.get_users()`** — both scopes are confirmed active.
7. **Document COQL quirks in CLI** — LIMIT truncation, BETWEEN broken on DateTime, timezone Z-only, no parentheses.
8. **Add graceful degradation for `AutomationClient`** — workflow/scoring/wizard methods will return scope errors until token is updated; methods should surface a clear `ScopeNotActive` error rather than a raw HTTP 403.
9. **Verify `visit_logs` / `DialPad_Logs` module** — confirm this is a real accessible CRM module or remove it.
