"""Click commands for Zoho Inventory Stock and Warehouses."""

import click

from cli_zoho.inventory.stock import StockClient
from cli_zoho.shared.output import render


def _client(ctx) -> StockClient:
    return StockClient(ctx.obj["auth"])


@click.group("stock", short_help="Stock levels and warehouse management")
@click.pass_context
def stock_group(ctx):
    """Zoho Inventory: stock summary per item and warehouse details."""
    pass


@stock_group.command("summary", short_help="Stock summary for an item across warehouses")
@click.argument("item_id")
@click.option("--json", "json_mode", is_flag=True, help="JSON output")
@click.option("--quiet", is_flag=True, help="Suppress non-data output")
@click.pass_context
def stock_summary(ctx, item_id, json_mode, quiet):
    """Get stock levels for an item broken down by warehouse."""
    client = _client(ctx)
    result = client.stock_summary(item_id)
    render(result, json_mode=json_mode, quiet=quiet)


@stock_group.command("warehouses", short_help="List all warehouses")
@click.option("--json", "json_mode", is_flag=True, help="JSON output")
@click.option("--quiet", is_flag=True, help="Suppress non-data output")
@click.pass_context
def list_warehouses(ctx, json_mode, quiet):
    """List all Inventory warehouses."""
    client = _client(ctx)
    result = client.list_warehouses()
    render(result, json_mode=json_mode, quiet=quiet)


@stock_group.command("warehouse", short_help="Get a single warehouse by ID")
@click.argument("warehouse_id")
@click.option("--json", "json_mode", is_flag=True, help="JSON output")
@click.option("--quiet", is_flag=True, help="Suppress non-data output")
@click.pass_context
def get_warehouse(ctx, warehouse_id, json_mode, quiet):
    """Get details of a single Inventory warehouse."""
    client = _client(ctx)
    result = client.get_warehouse(warehouse_id)
    render(result, json_mode=json_mode, quiet=quiet)
