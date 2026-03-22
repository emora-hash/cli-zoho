# cli-zoho vs Zoho CRM v8 OAS Validation Report
Generated: 03-22-2026

---

## Summary

| Category | Count |
|---|---|
| PASS | 14 |
| MISMATCH | 7 |
| MISSING | 4 |

---

## 1. client.py — list_records

**OAS:** `GET /{module}` — record.json
**Our URL:** `GET /{module}` via `paginate_crm`

**Parameters:**
- PASS: `page`, `per_page`, `fields` — all correct names and types
- PASS: Response parsed via `body.get("data", [])` and `body.get("info", {})` — OAS 200 schema has exactly `{data, info}`
- PASS: 204 handled (returns empty envelope)
- MISSING: `sort_by`, `sort_order`, `territory_id`, `ids`, `cvid`, `page_token`, `include_child` — all valid OAS params that `list_records` never exposes. Not bugs (they're optional), but functionality gaps.

**Scopes needed:** `ZohoCRM.modules.READ` or any module-specific `.READ` scope — standard grant covers this.

---

## 2. client.py — get_record

**OAS:** `GET /{module}/{recordID}` — record.json
**Our URL:** `GET /{module}/{record_id}`

- PASS: URL path correct (`recordID` is the path param name in OAS; our value binding is correct)
- PASS: Response parsed via `body.get("data", [])[0]` — OAS 200 schema has `{data}` array
- PASS: Custom 404 raised on empty data array (OAS returns 200 with empty `data` for not-found; our guard is correct)

---

## 3. client.py — create_record

**OAS:** `POST /{module}` — record.json
**Our body:** `{"data": [data]}`

- PASS: Body key `data` is correct — OAS requestBody schema has `{data, apply_feature_execution, skip_feature_execution, trigger}`
- PASS: Wrapping single record in a list is correct per OAS (data is an array)
- MISMATCH (silent data loss): `create_record` returns `resp.json()` raw. OAS 201 response is `{"data": [{"code": "SUCCESS", "details": {"id": "...", ...}, "message": "...", "status": "success"}]}`. Callers expecting the new record ID must do `resp["data"][0]["details"]["id"]` — this is not documented or extracted. No runtime failure but callers have to know this structure.
- MISSING: `trigger`, `apply_feature_execution`, `skip_feature_execution` request body fields are never passed. These are optional but meaningful (e.g. suppressing workflow triggers on bulk imports).

---

## 4. client.py — update_record

**OAS:** `PUT /{module}/{recordID}` — record.json
**Our body:** `{"data": [data]}`

- PASS: URL, method, body structure all correct
- MISMATCH (same as create): Returns raw `resp.json()`. OAS 200 response is `{"data": [{"code", "details", "message", "status"}]}`. The updated record ID is at `resp["data"][0]["details"]["id"]`. No extraction helper.
- MISSING: `trigger` body field not passed — same as create_record.

---

## 5. client.py — delete_record

**OAS:** `DELETE /{module}/{recordID}` — record.json

- PASS: URL and method correct
- PASS: OAS 200 response has `{data, status, code, message, details}` — returning raw `resp.json()` is fine here since there's no record body to extract.

---

## 6. client.py — search

**OAS:** `GET /{module}/search` — module_search.json

- PASS: URL correct (`/{module}/search`)
- PASS: `criteria`, `page`, `per_page` params — correct names
- PASS: Response parsed via `body.get("data")` and `body.get("info")` — OAS 200 schema has `{data, info}`
- PASS: 204 handled
- MISSING: `word`, `email`, `phone` search params — OAS exposes these as separate query params for exact-match searches. Our `search()` only supports `criteria` (formula-style). No runtime failure since `criteria` is valid, but callers can't do phone/email exact lookups.
- MISSING: `sort_by`, `sort_order` not passed
- **SCOPE MISMATCH:** OAS specifies `ZohoSearch.securesearch.READ` is required alongside `ZohoCRM.modules.*.READ` for search. If the OAuth grant doesn't include `ZohoSearch.securesearch.READ`, search calls will fail with 403. This is a **runtime failure risk**. Standard CRM-only grants often omit this scope.

---

## 7. client.py — coql_query

**OAS:** `POST /coql` — coql.json

- PASS: URL correct (`/coql`)
- PASS: Body key `select_query` — correct (OAS requestBody has `{select_query, include_meta}`)
- PASS: Response parsed via `body.get("data")` and `body.get("info")` — OAS 200 has `{data, info, fields}`
- MISSING: `include_meta` body field never passed. When `include_meta: true`, OAS response includes a `fields` array with column metadata. Never accessible via our interface.
- **SCOPE NOTE:** OAS requires `ZohoCRM.coql.READ` in addition to the module READ scope. Most standard grants include this but it must be explicitly requested. Omitting it causes 403.

---

## 8. client.py — get_fields

**OAS:** `GET /settings/fields` — fields.json

- PASS: URL correct
- PASS: `module` query param sent — correct
- PASS: Response key `fields` correct — OAS 200 schema is `{fields}`
- **MISMATCH (missing required param):** OAS marks `include` as `required: true` with enum values `["allowed_permissions_to_update", "skip_field_permissionz"]`. Our implementation never sends `include`. This is a **required parameter we are omitting**. The Zoho API may return an error or a degraded response depending on server-side enforcement. This is a latent bug.
- MISSING: `type` param (optional, enum: `all|unused|used`) — not exposed

**Scope needed:** `ZohoCRM.settings.fields.READ`

---

## 9. client.py — get_modules

**OAS:** `GET /settings/modules` — modules.json

- PASS: URL correct
- PASS: Response key `modules` correct
- MISSING: `status` and `feature_name` query params not sent (both optional)

**Scope needed:** `ZohoCRM.settings.modules.READ`

---

## 10. automation.py — get_workflows

**OAS:** `GET /settings/automation/workflow_rules` — workflow_rules.json

- PASS: URL correct
- PASS: `module` param sent when provided
- PASS: Response key `workflow_rules` correct — OAS 200 schema has `{workflow_rules, info}`
- MISSING: `page`, `per_page`, `status`, `execute_on`, `sort_order`, `sort_by`, `include_inner_details`, `filter` params all available in OAS but never sent

**Scope needed:** `ZohoCRM.settings.workflow_rules.READ`

---

## 11. automation.py — get_blueprint

**OAS:** Blueprint path — **NOT FOUND in record.json or any OAS file in v8.0/**

- Our URL: `GET /{module}/{record_id}/actions/blueprint`
- The OAS v8.0 directory contains no file with a blueprint path. The endpoint likely exists (it's a known Zoho API) but is absent from the provided OAS set. Cannot validate against spec.
- **STATUS: UNVERIFIABLE** — no OAS coverage

---

## 12. automation.py — get_scoring_rules

**OAS:** `GET /settings/automation/scoring_rules` — scoring_rules.json

- PASS: URL correct
- PASS: `module` param sent when provided
- PASS: Response key `scoring_rules` correct — OAS 200 schema has `{scoring_rules, info}`
- MISSING: `layout_id`, `page`, `per_page`, `name`, `inner_details` params not sent

**Scope needed:** `settings.scoring_rules.READ` (note: OAS uses this scope without `ZohoCRM.` prefix — unusual, verify this is not a spec typo vs actual Zoho scope name `ZohoCRM.settings.scoring_rules.READ`)

---

## 13. automation.py — get_assignment_rules

**OAS:** `GET /settings/automation/assignment_rules` — assignment_rules.json

- PASS: URL correct
- PASS: `module` param sent when provided
- PASS: Response key `assignment_rules` correct — OAS 200 schema has `{assignment_rules}`
- MISSING: `include_inner_details` param not sent

**Scope needed:** `ZohoCRM.settings.assignment_rules.READ`

---

## 14. metadata.py — get_layouts

**OAS:** `GET /settings/layouts` — layouts.json

- PASS: URL correct
- PASS: `module` param sent
- PASS: Response key `layouts` correct
- MISSING: `mode`, `include`, `include_inner_details` params not sent

**Scope needed:** `ZohoCRM.settings.layouts.READ`

---

## 15. metadata.py — get_custom_views

**OAS:** `GET /settings/custom_views` — custom_views.json

- PASS: URL correct
- PASS: `module` param sent
- PASS: Response key `custom_views` correct — OAS 200 schema has `{custom_views, info, ...}`
- MISSING: `filters` param not sent

**Scope needed:** `ZohoCRM.settings.custom_views.READ`

---

## 16. metadata.py — get_related_lists

**OAS:** `GET /settings/related_lists` — related_lists.json

- PASS: URL correct
- PASS: `module` param sent
- PASS: Response key `related_lists` correct — OAS 200 schema has `{related_lists}`
- MISSING: `layout_id`, `status` params not sent

**Scope needed:** `ZohoCRM.settings.related_lists.READ`

---

## 17. settings.py — get_pipelines

**OAS:** `GET /settings/pipeline` — pipeline.json

- PASS: URL correct (`/settings/pipeline`)
- **MISMATCH (wrong response key):** We call `resp.json().get("pipeline", [])` but OAS 200 response schema has `{pipeline}` as a top-level key containing the array. This appears to match — **PASS on response key**.
- **MISMATCH (missing required param):** OAS marks `layout_id` as `required: true` (query param). Our `get_pipelines()` accepts a `module` param and sends it as `params["module"] = module`, but `layout_id` is the required param per OAS. We are sending the wrong parameter name (`module` instead of `layout_id`) and omitting the required one. **This will likely return a 400 or incorrect results at runtime.**

**Scope needed:** `ZohoCRM.settings.pipeline.READ`

---

## 18. settings.py — get_variables

**OAS:** `GET /settings/variables` — variables.json

- PASS: URL correct
- PASS: Response key `variables` correct — OAS 200 schema has `{variables}`
- MISMATCH: We send `group` param. OAS has no `group` parameter defined for this endpoint. The parameter is silently ignored by the server or causes unexpected behavior.

**Scope needed:** `ZohoCRM.settings.variables.READ`

---

## 19. settings.py — get_business_hours

**OAS:** `GET /settings/business_hours` — business_hours.json

- PASS: URL correct
- PASS: Response key `business_hours` correct — OAS 200 schema has `{business_hours}`
- PASS: No required params

**Scope needed:** `ZohoCRM.settings.business_hours.READ`

---

## 20. settings.py — get_fiscal_year

**OAS:** `GET /settings/fiscal_year` — fiscal_year.json

- PASS: URL correct
- PASS: Response key `fiscal_year` correct — OAS 200 schema has `{fiscal_year}`
- PASS: No required params

**Scope needed:** `ZohoCRM.settings.fiscal_year.READ`

---

## Critical Findings (Runtime Failures or Silent Data Loss)

### CRITICAL — Runtime Failures

| # | Location | Issue |
|---|---|---|
| C1 | `get_fields()` | `include` is a **required** OAS param, never sent. Server may reject with 400. |
| C2 | `get_pipelines()` | `layout_id` is a **required** OAS param. We send `module` instead. Wrong param name + missing required param. Will return 400 or wrong data. |
| C3 | `search()` | Requires `ZohoSearch.securesearch.READ` scope in addition to module READ. Grants missing this scope will get 403 on every search call. |
| C4 | `coql_query()` | Requires `ZohoCRM.coql.READ` scope explicitly. Must be in the OAuth grant. |

### HIGH — Silent Data Loss / Missing Functionality

| # | Location | Issue |
|---|---|---|
| H1 | `create_record()` | Returns raw response body. New record ID is at `resp["data"][0]["details"]["id"]` — not extracted, not documented. Callers must know this internal structure. |
| H2 | `update_record()` | Same as H1 — updated record ID buried in `resp["data"][0]["details"]["id"]`. |
| H3 | `get_variables()` | Sends `group` param which does not exist in OAS. Silently ignored. |
| H4 | `get_blueprint()` | No OAS coverage in v8.0 spec set. Cannot validate URL, params, or response. |

### MEDIUM — Missing Optional Params (Functionality Gaps)

| Location | Missing Params |
|---|---|
| `list_records` | `sort_by`, `sort_order`, `territory_id`, `ids`, `cvid`, `page_token`, `include_child` |
| `search` | `word`, `email`, `phone`, `sort_by`, `sort_order` |
| `coql_query` | `include_meta` |
| `get_fields` | `type` |
| `get_workflows` | `page`, `per_page`, `status`, `execute_on`, `sort_order`, `sort_by`, `filter` |
| `get_scoring_rules` | `layout_id`, `page`, `per_page`, `name`, `inner_details` |
| `get_pipelines` | `layout_id` (required — already listed as critical) |

---

## OAuth Scopes Checklist

All scopes the OAS specifies that your OAuth grant must include:

```
ZohoCRM.modules.READ           # list, get, search, coql
ZohoCRM.modules.CREATE         # create_record
ZohoCRM.modules.UPDATE         # update_record
ZohoCRM.modules.DELETE         # delete_record
ZohoSearch.securesearch.READ   # search — OFTEN MISSING from basic CRM grants
ZohoCRM.coql.READ              # coql_query
ZohoCRM.settings.fields.READ   # get_fields
ZohoCRM.settings.modules.READ  # get_modules
ZohoCRM.settings.workflow_rules.READ
ZohoCRM.settings.layouts.READ
ZohoCRM.settings.custom_views.READ
ZohoCRM.settings.related_lists.READ
ZohoCRM.settings.pipeline.READ
ZohoCRM.settings.variables.READ
ZohoCRM.settings.business_hours.READ
ZohoCRM.settings.fiscal_year.READ
ZohoCRM.settings.assignment_rules.READ
settings.scoring_rules.READ    # NOTE: OAS spec omits ZohoCRM. prefix — verify actual scope name
```
