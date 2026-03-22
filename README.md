# cli-zoho

The first open-source, unified CLI for **Zoho CRM v8** and **Zoho Inventory v1**. Designed for terminal power users and AI agent pipelines.

```bash
pip install cli-zoho
```

## Why This Exists

Zoho has 3 official CLIs (`zet`, `zdk`, `@zohofinance/cli`) — none of them do data operations. They handle widget packaging, metadata versioning, and custom function deployment. If you want to list deals, search inventory, or run a COQL query from the terminal, you're out of luck.

The official Python SDK (`zohocrm-python-sdk-8.0`) covers the full API surface but weighs ~50K LOC with hundreds of auto-generated model classes. Not practical for scripting or agent toolchains.

**cli-zoho** is ~2K LOC, two runtime dependencies (`click` + `requests`), and covers 57 commands across both CRM and Inventory.

## Quick Start

```bash
# Set credentials (4 env vars)
export ZOHO_CLIENT_ID="your-client-id"
export ZOHO_CLIENT_SECRET="your-client-secret"
export ZOHO_REFRESH_TOKEN="your-refresh-token"
export ZOHO_ORG_ID="your-inventory-org-id"

# Verify auth
cli-zoho auth status

# List deals
cli-zoho crm list Deals --limit 5

# COQL query
cli-zoho crm query "select Deal_Name, Amount from Deals where Stage = 'Qualification' limit 10"

# Search inventory
cli-zoho inv search items "hydraulic hammer"

# Auto-paginate all items
cli-zoho inv list items --all --json
```

## Features

- **CRM v8 + Inventory v1** in one tool — 11 CRM modules, 13 Inventory entities
- **COQL queries** with automatic v8 WHERE clause injection
- **v8 field auto-resolution** — handles the required `fields` param transparently
- **`--json` on every command** — structured output for agent pipelines
- **`--pretty`** — indented JSON for human readability
- **`--all`** — auto-paginate through all records (capped at 10K)
- **`--dry-run`** — preview destructive operations without executing
- **`--debug`** — full HTTP request/response logging to stderr
- **Disk-cached OAuth tokens** — no redundant refreshes across invocations
- **Exponential backoff** with jitter on 429/5xx — production-grade retry logic
- **Multi-region** — US, EU, IN, AU, JP, CA datacenters via `ZOHO_REGION`
- **Typed error hierarchy** — `AuthenticationError`, `RateLimitError`, `ValidationError`, `ResourceNotFoundError`, `ServerError`

## Commands

### CRM

```
cli-zoho crm list <module>          List records (paginated)
cli-zoho crm get <module> <id>      Get single record
cli-zoho crm create <module>        Create record (--data JSON or --file)
cli-zoho crm update <module> <id>   Update record
cli-zoho crm delete <module> <id>   Delete record
cli-zoho crm search <module> <criteria>  Search by criteria
cli-zoho crm query <coql>           Raw COQL query
cli-zoho crm fields <module>        List fields + types
cli-zoho crm modules                List all modules
```

Plus automation (`workflows`, `blueprint`, `scoring`, `assignments`), metadata (`layouts`, `views`, `related-lists`), and settings (`pipelines`, `variables`, `org-settings`).

### Inventory

```
cli-zoho inv list <entity>          List records
cli-zoho inv get <entity> <id>      Get single record
cli-zoho inv create <entity>        Create record
cli-zoho inv update <entity> <id>   Update record
cli-zoho inv delete <entity> <id>   Delete record
cli-zoho inv search <entity> <text> Search by text
cli-zoho inv fields <entity>        List custom fields
cli-zoho inv entities               List all entities
```

Supported entities: items, item_groups, packages, shipments, purchase_orders, purchase_receives, bills, payments_made, vendors, sales_orders, customers, transfer_orders, contact_persons.

## Agent Integration

Every command supports `--json` for structured output, making cli-zoho usable as a tool in AI agent pipelines:

```bash
# Claude Code / AI agent can call:
cli-zoho crm query "select Deal_Name, Amount from Deals where Stage = 'Closed Won'" --json

# Pipe to jq:
cli-zoho inv list items --all --json | jq '.data[] | {name, sku, stock_on_hand}'

# Use in n8n Execute Command nodes:
cli-zoho crm get Deals 6171402000012868034 --json
```

## Multi-Region Support

Zoho operates 6 datacenters. Set `ZOHO_REGION` to match your org:

| Region | Value | Auth Domain | API Domain |
|--------|-------|-------------|------------|
| United States | `us` (default) | accounts.zoho.com | www.zohoapis.com |
| Europe | `eu` | accounts.zoho.eu | www.zohoapis.eu |
| India | `in` | accounts.zoho.in | www.zohoapis.in |
| Australia | `au` | accounts.zoho.com.au | www.zohoapis.com.au |
| Japan | `jp` | accounts.zoho.jp | www.zohoapis.jp |
| Canada | `ca` | accounts.zohocloud.ca | www.zohoapis.ca |

```bash
export ZOHO_REGION=eu
cli-zoho auth status
```

## Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `ZOHO_CLIENT_ID` | Yes | OAuth client ID from api-console.zoho.com |
| `ZOHO_CLIENT_SECRET` | Yes | OAuth client secret |
| `ZOHO_REFRESH_TOKEN` | Yes | Long-lived refresh token |
| `ZOHO_ORG_ID` | Yes* | Inventory organization ID (*required for Inventory commands) |
| `ZOHO_REGION` | No | Datacenter region: us, eu, in, au, jp, ca (default: us) |

## How It Compares

|  | Zoho SDK | zdk CLI | Zoho MCP | cli-zoho |
|--|----------|---------|----------|----------|
| CRM record CRUD | Yes | No | Yes | Yes |
| COQL queries | Yes | No | Yes | Yes |
| Inventory CRUD | No | No | ? | Yes |
| Unified CRM+Inventory | No | No | No | **Yes** |
| v8 field auto-resolution | No | No | No | **Yes** |
| Token caching | No | Yes | ? | Yes |
| Rate limit + backoff | No | ? | ? | Yes |
| Agent-native (--json) | No | Yes | Yes | Yes |
| pip installable | Yes | No (npm) | No | Yes |
| LOC | ~50K | ? | ? | **~2K** |

## Development

```bash
git clone https://github.com/emora-hash/cli-zoho.git
cd cli-zoho
pip install -e ".[dev]"
pytest
```

## License

MIT
