"""Shared pagination for CRM and Inventory APIs."""

import logging
from typing import Callable

from cli_zoho import config

logger = logging.getLogger(__name__)

MAX_AUTO_PAGINATE = 10_000


def paginate_crm(auth, module: str, *, limit: int, page: int = 1, fields: str = "") -> dict:
    """Fetch one page of CRM records. Returns envelope with data + pagination info.

    Args:
        fields: Comma-separated field API names. Required by CRM v8 — if empty,
                caller must resolve default fields before calling.
    """
    url = f"{config.get_crm_base()}/{module}"
    per_page = min(limit, config.MAX_PAGE_SIZE)
    params: dict = {"page": page, "per_page": per_page}
    if fields:
        params["fields"] = fields
    resp = auth.request("GET", url, params=params)

    if resp.status_code == 204:
        return {"data": [], "has_more": False, "next_page": None, "count": 0}


    body = resp.json()
    records = body.get("data", [])
    info = body.get("info", {})

    return {
        "data": records,
        "has_more": info.get("more_records", False),
        "next_page": page + 1 if info.get("more_records") else None,
        "count": len(records),
    }


def paginate_inventory(auth, entity_cfg: dict, *, limit: int, page: int = 1) -> dict:
    """Fetch one page of Inventory records. Returns envelope with data + pagination info."""
    url = f"{config.get_inventory_base()}{entity_cfg['endpoint']}"
    per_page = min(limit, config.MAX_PAGE_SIZE)
    params = {"page": page, "per_page": per_page}
    params.update(entity_cfg.get("extra_params", {}))

    headers = {"X-com-zoho-inventory-organizationid": config.get_org_id()}
    resp = auth.request("GET", url, headers=headers, params=params)

    if resp.status_code == 204:
        return {"data": [], "has_more": False, "next_page": None, "count": 0}


    body = resp.json()

    records = body.get(entity_cfg["list_key"], [])
    # page_context is the canonical location (confirmed by MCP ref); top-level is fallback
    has_more = body.get("page_context", {}).get("has_more_page", body.get("has_more_page", False))

    # Zoho sometimes lies about has_more_page on full pages
    if not has_more and len(records) == per_page:
        has_more = True  # assume more; caller will get empty on next page

    return {
        "data": records,
        "has_more": has_more,
        "next_page": page + 1 if has_more else None,
        "count": len(records),
    }


def paginate_all(fetch_page: Callable[[int], dict], *, max_records: int = MAX_AUTO_PAGINATE) -> dict:
    """Auto-paginate by calling fetch_page(page_num) until no more records.

    Returns aggregated envelope with all records combined.
    Safety cap at max_records to prevent runaway loops.
    """
    all_records: list = []
    page = 1
    while True:
        result = fetch_page(page)
        all_records.extend(result.get("data", []))
        logger.debug("paginate_all: page %d, got %d records (total %d)", page, result.get("count", 0), len(all_records))
        if len(all_records) >= max_records:
            logger.warning("paginate_all: hit safety cap at %d records", max_records)
            all_records = all_records[:max_records]
            break
        if not result.get("has_more"):
            break
        page += 1
    return {"data": all_records, "has_more": False, "next_page": None, "count": len(all_records)}
