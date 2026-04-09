"""Configuration for cli-zoho. All secrets from environment variables."""

import os

# ─── Region → Domain Mapping ─────────────────────────────────────────────────
# Zoho operates 6 datacenters. Set ZOHO_REGION env var to match your org.

# Each region has an auth domain (accounts.*) and an API domain (www.zohoapis.*)
REGION_MAP = {
    "us": {"auth": "accounts.zoho.com",       "api": "www.zohoapis.com"},
    "eu": {"auth": "accounts.zoho.eu",         "api": "www.zohoapis.eu"},
    "in": {"auth": "accounts.zoho.in",         "api": "www.zohoapis.in"},
    "au": {"auth": "accounts.zoho.com.au",     "api": "www.zohoapis.com.au"},
    "jp": {"auth": "accounts.zoho.jp",         "api": "www.zohoapis.jp"},
    "ca": {"auth": "accounts.zohocloud.ca",    "api": "www.zohoapis.ca"},
}

DEFAULT_PAGE_SIZE = 10
MAX_PAGE_SIZE = 200

_region_cfg: dict | None = None


def _get_region() -> dict:
    """Resolve Zoho region config from ZOHO_REGION env var (cached)."""
    global _region_cfg
    if _region_cfg is None:
        region = os.environ.get("ZOHO_REGION", "us").lower()
        if region not in REGION_MAP:
            valid = ", ".join(REGION_MAP)
            raise SystemExit(f"Invalid ZOHO_REGION='{region}'. Valid: {valid}")
        _region_cfg = REGION_MAP[region]
    return _region_cfg


def get_token_url() -> str:
    return f"https://{_get_region()['auth']}/oauth/v2/token"


def get_crm_base() -> str:
    return f"https://{_get_region()['api']}/crm/v8"


def get_inventory_base() -> str:
    return f"https://{_get_region()['api']}/inventory/v1"


# ─── Env Var Accessors ───────────────────────────────────────────────────────


def _env(key: str) -> str:
    """Get required env var or raise clear error."""
    val = os.environ.get(key)
    if not val:
        raise SystemExit(
            f"Missing environment variable: {key}\n"
            f"Run: source ~/.salted/load-secrets.sh"
        )
    return val


def get_client_id() -> str:
    return _env("ZOHO_CLIENT_ID")


def get_client_secret() -> str:
    return _env("ZOHO_CLIENT_SECRET")


def get_refresh_token() -> str:
    return _env("ZOHO_REFRESH_TOKEN")


def get_org_id() -> str:
    return _env("ZOHO_ORG_ID")


# ─── App #3 (CLI Bulk + Automation) Credentials ───────────────────────────────
# Separate OAuth client with bulk, mass ops, workflow, functions, admin scopes.
# Falls back gracefully — returns None if not configured, letting auth.py decide.


def get_app3_client_id() -> str | None:
    return os.environ.get("ZOHO_APP3_CLIENT_ID")


def get_app3_client_secret() -> str | None:
    return os.environ.get("ZOHO_APP3_CLIENT_SECRET")


def get_app3_refresh_token() -> str | None:
    return os.environ.get("ZOHO_APP3_REFRESH_TOKEN")


# ─── CRM Entity Definitions ─────────────────────────────────────────────────

CRM_ENTITIES = {
    "deals": {"module": "Deals", "id_field": "id"},
    "contacts": {"module": "Contacts", "id_field": "id"},
    "accounts": {"module": "Accounts", "id_field": "id"},
    "leads": {"module": "Leads", "id_field": "id"},
    "invoices": {"module": "Invoices", "id_field": "id"},
    "sales_orders": {"module": "Sales_Orders", "id_field": "id"},
    "quotes": {"module": "Quotes", "id_field": "id"},
    "calls": {"module": "Calls", "id_field": "id"},
    "cases": {"module": "Cases", "id_field": "id"},
    "tasks": {"module": "Tasks", "id_field": "id"},
    "visit_logs": {"module": "DialPad_Logs", "id_field": "id"},
}

# ─── Inventory Entity Definitions ───────────────────────────────────────────

INVENTORY_ENTITIES = {
    "items": {
        "endpoint": "/items",
        "list_key": "items",
        "get_key": "item",
        "id_field": "item_id",
    },
    "item_groups": {
        "endpoint": "/itemgroups",
        "list_key": "itemgroups",
        "get_key": "itemgroup",
        "id_field": "group_id",
    },
    "packages": {
        "endpoint": "/packages",
        "list_key": "packages",
        "get_key": "package",
        "id_field": "package_id",
    },
    "shipments": {
        "endpoint": "/shipmentorders",
        "list_key": "shipmentorders",
        "get_key": "shipmentorder",
        "id_field": "shipment_id",
    },
    "purchase_orders": {
        "endpoint": "/purchaseorders",
        "list_key": "purchaseorders",
        "get_key": "purchaseorder",
        "id_field": "purchaseorder_id",
    },
    "purchase_receives": {
        "endpoint": "/purchasereceives",
        "list_key": "purchasereceives",
        "get_key": "purchase_receive",
        "id_field": "receive_id",
    },
    "bills": {
        "endpoint": "/bills",
        "list_key": "bills",
        "get_key": "bill",
        "id_field": "bill_id",
    },
    "payments_made": {
        "endpoint": "/vendorpayments",
        "list_key": "vendorpayments",
        "get_key": "vendorpayment",
        "id_field": "payment_id",
    },
    "vendors": {
        "endpoint": "/contacts",
        "list_key": "contacts",
        "get_key": "contact",
        "id_field": "contact_id",
        "extra_params": {"contact_type": "vendor"},
    },
    "sales_orders": {
        "endpoint": "/salesorders",
        "list_key": "salesorders",
        "get_key": "salesorder",
        "id_field": "salesorder_id",
    },
    "customers": {
        "endpoint": "/contacts",
        "list_key": "contacts",
        "get_key": "contact",
        "id_field": "contact_id",
        "extra_params": {"contact_type": "customer"},
    },
    "transfer_orders": {
        "endpoint": "/transferorders",
        "list_key": "transferorders",
        "get_key": "transferorder",
        "id_field": "transfer_order_id",
    },
    "contact_persons": {
        "endpoint": "/contacts/contactpersons",
        "list_key": "contactpersons",
        "get_key": "contactperson",
        "id_field": "contactperson_id",
    },
    "invoices": {
        "endpoint": "/invoices",
        "list_key": "invoices",
        "get_key": "invoice",
        "id_field": "invoice_id",
    },
    "payments_received": {
        "endpoint": "/customerpayments",
        "list_key": "customerpayments",
        "get_key": "payment",
        "id_field": "payment_id",
    },
    "warehouses": {
        "endpoint": "/warehouses",
        "list_key": "warehouses",
        "get_key": "warehouse",
        "id_field": "warehouse_id",
    },
    "price_lists": {
        "endpoint": "/pricebooks",
        "list_key": "pricebooks",
        "get_key": "pricebook",
        "id_field": "pricebook_id",
    },
    "composite_items": {
        "endpoint": "/compositeitems",
        "list_key": "composite_items",
        "get_key": "composite_item",
        "id_field": "composite_item_id",
    },
}
