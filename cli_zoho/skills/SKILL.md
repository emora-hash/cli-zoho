---
name: cli-zoho
description: Agent-native CLI for Zoho CRM and Zoho Inventory with full CRUD, COQL queries, and field discovery
version: 0.1.0
---

# cli-zoho

Unified CLI for Zoho CRM (V2 API) and Zoho Inventory (V1 API). Supports all 20 JMA-synced entities plus field/module discovery.

## Agent Usage

Always use `--json --quiet` for structured output. Use `--fields` to reduce response size.

```bash
cli-zoho crm list Deals --limit 5 --json --quiet --fields Deal_Name,Amount,Stage
```

## CRM Commands

### Records
```bash
cli-zoho crm list <module> [--limit N] [--page N] [--fields f1,f2] [--json]
cli-zoho crm get <module> <id> [--fields f1,f2] [--json]
cli-zoho crm create <module> --data '{"Field":"Value"}' [--json]
cli-zoho crm update <module> <id> --data '{"Field":"Value"}' [--json]
cli-zoho crm delete <module> <id> [--json]
cli-zoho crm search <module> "(Field:equals:Value)" [--limit N] [--json]
```

### COQL Query
```bash
cli-zoho crm query "SELECT Last_Name, Email FROM Contacts WHERE Lead_Source = 'Web' LIMIT 10" --json
```

### Discovery
```bash
cli-zoho crm modules --json          # List all CRM modules
cli-zoho crm fields <module> --json  # List fields with api_name, label, type, required
```

### Automation
```bash
cli-zoho crm workflows list [--module M] [--json]       # List workflow rules
cli-zoho crm workflows get <rule_id> [--json]            # Get workflow detail
cli-zoho crm workflows update <rule_id> --data '{...}' [--json]
cli-zoho crm workflows delete <rule_id> [--json]
cli-zoho crm workflows reorder <module> --ids id1,id2,id3 [--json]
cli-zoho crm workflows usage [--json]                    # Usage report
cli-zoho crm workflows limits [--json]                   # Org workflow limits
cli-zoho crm blueprint get <module> <record_id> [--json] # Available transitions
cli-zoho crm blueprint advance <module> <record_id> --transition-id T --data '{...}' [--json]
cli-zoho crm scoring list [--module M] [--json]          # Scoring rules
cli-zoho crm scoring create --data '{...}' [--json]
cli-zoho crm scoring update <rule_id> --data '{...}' [--json]
cli-zoho crm scoring delete <rule_id> [--json]
cli-zoho crm scoring execute <rule_id> <module> [--json]
cli-zoho crm assignments list [--module M] [--json]      # Assignment rules
```

### Metadata
```bash
cli-zoho crm layouts list <module> [--json]              # Page layouts
cli-zoho crm layouts get <module> <layout_id> [--json]   # Layout detail
cli-zoho crm views list <module> [--json]                # Custom views/filters
cli-zoho crm views get <module> <view_id> [--json]       # View detail + criteria
cli-zoho crm related-lists list <module> [--json]        # Related record types
```

### Settings
```bash
cli-zoho crm pipelines list [--module M] [--json]        # Sales pipelines
cli-zoho crm pipelines create --data '{...}' [--json]
cli-zoho crm pipelines update <pipeline_id> --data '{...}' [--json]
cli-zoho crm variables list [--group G] [--json]         # Org variables
cli-zoho crm variables create --data '{...}' [--json]
cli-zoho crm variables update <variable_id> --data '{...}' [--json]
cli-zoho crm variables delete <variable_id> [--json]
cli-zoho crm variables groups [--json]                   # Variable groups
cli-zoho crm org-settings business-hours [--json]        # Business hours config
cli-zoho crm org-settings fiscal-year [--json]           # Fiscal year config
```

### CRM Modules
Deals, Contacts, Accounts, Leads, Invoices, Sales_Orders, Quotes, Calls, Cases, Tasks, DialPad_Logs

## Inventory Commands

### Records
```bash
cli-zoho inv list <entity> [--limit N] [--page N] [--fields f1,f2] [--json]
cli-zoho inv get <entity> <id> [--fields f1,f2] [--json]
cli-zoho inv create <entity> --data '{"name":"Item"}' [--json]
cli-zoho inv update <entity> <id> --data '{"name":"Updated"}' [--json]
cli-zoho inv delete <entity> <id> [--json]
cli-zoho inv search <entity> "search text" [--limit N] [--json]
```

### Discovery
```bash
cli-zoho inv entities --json          # List all Inventory entities
cli-zoho inv fields <entity> --json   # List custom fields
```

### Inventory Entities
items, item_groups, packages, shipments, purchase_orders, purchase_receives, bills, payments_made, vendors

## Auth & Info
```bash
cli-zoho auth status --json    # Check if credentials are valid
cli-zoho auth refresh --json   # Force token refresh
cli-zoho info version          # CLI version
cli-zoho info org --json       # Zoho organization details
```

## JSON Response Format

All list commands return:
```json
{"data": [...], "has_more": true, "next_page": 2, "count": 10}
```

Paginate by incrementing `--page` until `has_more` is false.

## Prerequisites

Requires env vars: `ZOHO_CLIENT_ID`, `ZOHO_CLIENT_SECRET`, `ZOHO_REFRESH_TOKEN`, `ZOHO_ORG_ID`

Load via: `source ~/.jma/load-secrets.sh`
