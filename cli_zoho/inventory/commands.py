"""Click commands for Zoho Inventory."""

import click

from cli_zoho import config
from cli_zoho.inventory.client import InventoryClient
from cli_zoho.shared.output import render, error_out, parse_data, dry_run_output
from cli_zoho.shared.pagination import paginate_all


@click.group("inventory", short_help="Zoho Inventory operations")
@click.pass_context
def inventory_group(ctx):
    """Zoho Inventory: items, orders, shipments, field discovery."""
    pass


def _client(ctx) -> InventoryClient:
    return InventoryClient(ctx.obj["auth"])


def _validate_entity(entity: str) -> str:
    """Validate entity name, return normalized version."""
    if entity in config.INVENTORY_ENTITIES:
        return entity
    error_out(
        f"Unknown entity: {entity}. "
        f"Valid: {', '.join(sorted(config.INVENTORY_ENTITIES.keys()))}"
    )


@inventory_group.command("list", short_help="List records from an entity")
@click.argument("entity")
@click.option("--limit", default=config.DEFAULT_PAGE_SIZE, type=int, help="Records per page")
@click.option("--page", default=1, type=int, help="Page number")
@click.option("--all", "fetch_all", is_flag=True, help="Auto-paginate all records")
@click.option("--json", "json_mode", is_flag=True, help="JSON output")
@click.option("--fields", default=None, help="Comma-separated field names")
@click.option("--quiet", is_flag=True, help="Suppress non-data output")
@click.pass_context
def list_records(ctx, entity, limit, page, fetch_all, json_mode, fields, quiet):
    """List records from an Inventory entity (e.g., items, shipments, vendors)."""
    entity = _validate_entity(entity)
    client = _client(ctx)
    if fetch_all:
        result = paginate_all(lambda p: client.list_records(entity, limit=config.MAX_PAGE_SIZE, page=p))
    else:
        result = client.list_records(entity, limit=limit, page=page)
    render(result, json_mode=json_mode, quiet=quiet, fields=fields)


@inventory_group.command("get", short_help="Get a single record by ID")
@click.argument("entity")
@click.argument("record_id")
@click.option("--json", "json_mode", is_flag=True, help="JSON output")
@click.option("--fields", default=None, help="Comma-separated field names")
@click.option("--quiet", is_flag=True, help="Suppress non-data output")
@click.pass_context
def get_record(ctx, entity, record_id, json_mode, fields, quiet):
    """Get a single Inventory record by entity and ID."""
    entity = _validate_entity(entity)
    client = _client(ctx)
    result = client.get_record(entity, record_id)
    render(result, json_mode=json_mode, quiet=quiet, fields=fields)


@inventory_group.command("create", short_help="Create a new record")
@click.argument("entity")
@click.option("--data", required=False, help="JSON string of record data")
@click.option("--file", "file_path", required=False, type=click.Path(exists=True), help="JSON file path")
@click.option("--dry-run", is_flag=True, help="Show request without executing")
@click.option("--json", "json_mode", is_flag=True, help="JSON output")
@click.option("--quiet", is_flag=True, help="Suppress non-data output")
@click.pass_context
def create_record(ctx, entity, data, file_path, dry_run, json_mode, quiet):
    """Create a record in an Inventory entity."""
    entity = _validate_entity(entity)
    record_data = parse_data(data, file_path)
    if dry_run:
        entity_cfg = config.INVENTORY_ENTITIES[entity]
        dry_run_output("POST", f"{config.get_inventory_base()}{entity_cfg['endpoint']}", record_data)
        return
    client = _client(ctx)
    result = client.create_record(entity, record_data)
    render(result, json_mode=json_mode, quiet=quiet)


@inventory_group.command("update", short_help="Update a record by ID")
@click.argument("entity")
@click.argument("record_id")
@click.option("--data", required=False, help="JSON string of fields to update")
@click.option("--file", "file_path", required=False, type=click.Path(exists=True), help="JSON file path")
@click.option("--dry-run", is_flag=True, help="Show request without executing")
@click.option("--json", "json_mode", is_flag=True, help="JSON output")
@click.option("--quiet", is_flag=True, help="Suppress non-data output")
@click.pass_context
def update_record(ctx, entity, record_id, data, file_path, dry_run, json_mode, quiet):
    """Update fields on an existing Inventory record."""
    entity = _validate_entity(entity)
    record_data = parse_data(data, file_path)
    if dry_run:
        entity_cfg = config.INVENTORY_ENTITIES[entity]
        dry_run_output("PUT", f"{config.get_inventory_base()}{entity_cfg['endpoint']}/{record_id}", record_data)
        return
    client = _client(ctx)
    result = client.update_record(entity, record_id, record_data)
    render(result, json_mode=json_mode, quiet=quiet)


@inventory_group.command("delete", short_help="Delete a record by ID")
@click.argument("entity")
@click.argument("record_id")
@click.option("--dry-run", is_flag=True, help="Show request without executing")
@click.option("--json", "json_mode", is_flag=True, help="JSON output")
@click.option("--quiet", is_flag=True, help="Suppress non-data output")
@click.pass_context
def delete_record(ctx, entity, record_id, dry_run, json_mode, quiet):
    """Delete an Inventory record by entity and ID."""
    entity = _validate_entity(entity)
    if dry_run:
        entity_cfg = config.INVENTORY_ENTITIES[entity]
        dry_run_output("DELETE", f"{config.get_inventory_base()}{entity_cfg['endpoint']}/{record_id}")
        return
    client = _client(ctx)
    result = client.delete_record(entity, record_id)
    render(result, json_mode=json_mode, quiet=quiet)


@inventory_group.command("search", short_help="Search records by text")
@click.argument("entity")
@click.argument("text")
@click.option("--limit", default=config.DEFAULT_PAGE_SIZE, type=int, help="Records per page")
@click.option("--page", default=1, type=int, help="Page number")
@click.option("--all", "fetch_all", is_flag=True, help="Auto-paginate all results")
@click.option("--json", "json_mode", is_flag=True, help="JSON output")
@click.option("--fields", default=None, help="Comma-separated field names")
@click.option("--quiet", is_flag=True, help="Suppress non-data output")
@click.pass_context
def search_records(ctx, entity, text, limit, page, fetch_all, json_mode, fields, quiet):
    """Search Inventory records by text."""
    entity = _validate_entity(entity)
    client = _client(ctx)
    if fetch_all:
        result = paginate_all(lambda p: client.search(entity, text, limit=config.MAX_PAGE_SIZE, page=p))
    else:
        result = client.search(entity, text, limit=limit, page=page)
    render(result, json_mode=json_mode, quiet=quiet, fields=fields)


@inventory_group.command("fields", short_help="List custom fields for an entity")
@click.argument("entity")
@click.option("--json", "json_mode", is_flag=True, help="JSON output")
@click.option("--quiet", is_flag=True, help="Suppress non-data output")
@click.pass_context
def list_fields(ctx, entity, json_mode, quiet):
    """List custom fields for an Inventory entity."""
    entity = _validate_entity(entity)
    client = _client(ctx)
    fields_data = client.get_fields(entity)
    render(fields_data, json_mode=json_mode, quiet=quiet)


from cli_zoho.inventory.stock_commands import stock_group
inventory_group.add_command(stock_group)


@inventory_group.command("entities", short_help="List all Inventory entities")
@click.option("--json", "json_mode", is_flag=True, help="JSON output")
@click.option("--quiet", is_flag=True, help="Suppress non-data output")
@click.pass_context
def list_entities(ctx, json_mode, quiet):
    """List all supported Inventory entities."""
    entities = [
        {"name": name, "endpoint": cfg["endpoint"], "id_field": cfg["id_field"]}
        for name, cfg in sorted(config.INVENTORY_ENTITIES.items())
    ]
    render(entities, json_mode=json_mode, quiet=quiet)


