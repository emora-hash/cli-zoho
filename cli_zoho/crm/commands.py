"""Click commands for Zoho CRM."""

import click

from cli_zoho import config
from cli_zoho.crm.client import CRMClient
from cli_zoho.shared.output import render, parse_data, dry_run_output
from cli_zoho.shared.pagination import paginate_all


@click.group("crm", short_help="Zoho CRM operations")
@click.pass_context
def crm_group(ctx):
    """Zoho CRM: records, search, COQL, field discovery."""
    pass


def _client(ctx) -> CRMClient:
    return CRMClient(ctx.obj["auth"])


@crm_group.command("list", short_help="List records from a module")
@click.argument("module")
@click.option("--limit", default=config.DEFAULT_PAGE_SIZE, type=int, help="Records per page")
@click.option("--page", default=1, type=int, help="Page number")
@click.option("--all", "fetch_all", is_flag=True, help="Auto-paginate all records")
@click.option("--json", "json_mode", is_flag=True, help="JSON output")
@click.option("--fields", default=None, help="Comma-separated field names")
@click.option("--quiet", is_flag=True, help="Suppress non-data output")
@click.pass_context
def list_records(ctx, module, limit, page, fetch_all, json_mode, fields, quiet):
    """List records from a CRM module (e.g., Deals, Contacts, Leads)."""
    client = _client(ctx)
    if fetch_all:
        result = paginate_all(lambda p: client.list_records(module, limit=config.MAX_PAGE_SIZE, page=p, fields=fields or ""))
    else:
        result = client.list_records(module, limit=limit, page=page, fields=fields or "")
    render(result, json_mode=json_mode, quiet=quiet, fields=fields)


@crm_group.command("get", short_help="Get a single record by ID")
@click.argument("module")
@click.argument("record_id")
@click.option("--json", "json_mode", is_flag=True, help="JSON output")
@click.option("--fields", default=None, help="Comma-separated field names")
@click.option("--quiet", is_flag=True, help="Suppress non-data output")
@click.pass_context
def get_record(ctx, module, record_id, json_mode, fields, quiet):
    """Get a single CRM record by module and ID."""
    client = _client(ctx)
    result = client.get_record(module, record_id)
    render(result, json_mode=json_mode, quiet=quiet, fields=fields)


@crm_group.command("create", short_help="Create a new record")
@click.argument("module")
@click.option("--data", required=False, help="JSON string of record data")
@click.option("--file", "file_path", required=False, type=click.Path(exists=True), help="JSON file path")
@click.option("--dry-run", is_flag=True, help="Show request without executing")
@click.option("--json", "json_mode", is_flag=True, help="JSON output")
@click.option("--quiet", is_flag=True, help="Suppress non-data output")
@click.pass_context
def create_record(ctx, module, data, file_path, dry_run, json_mode, quiet):
    """Create a record in a CRM module."""
    record_data = parse_data(data, file_path)
    if dry_run:
        dry_run_output("POST", f"{config.get_crm_base()}/{module}", {"data": [record_data]})
        return
    client = _client(ctx)
    result = client.create_record(module, record_data)
    render(result, json_mode=json_mode, quiet=quiet)


@crm_group.command("update", short_help="Update a record by ID")
@click.argument("module")
@click.argument("record_id")
@click.option("--data", required=False, help="JSON string of fields to update")
@click.option("--file", "file_path", required=False, type=click.Path(exists=True), help="JSON file path")
@click.option("--dry-run", is_flag=True, help="Show request without executing")
@click.option("--json", "json_mode", is_flag=True, help="JSON output")
@click.option("--quiet", is_flag=True, help="Suppress non-data output")
@click.pass_context
def update_record(ctx, module, record_id, data, file_path, dry_run, json_mode, quiet):
    """Update fields on an existing CRM record."""
    record_data = parse_data(data, file_path)
    if dry_run:
        dry_run_output("PUT", f"{config.get_crm_base()}/{module}/{record_id}", {"data": [record_data]})
        return
    client = _client(ctx)
    result = client.update_record(module, record_id, record_data)
    render(result, json_mode=json_mode, quiet=quiet)


@crm_group.command("delete", short_help="Delete a record by ID")
@click.argument("module")
@click.argument("record_id")
@click.option("--dry-run", is_flag=True, help="Show request without executing")
@click.option("--json", "json_mode", is_flag=True, help="JSON output")
@click.option("--quiet", is_flag=True, help="Suppress non-data output")
@click.pass_context
def delete_record(ctx, module, record_id, dry_run, json_mode, quiet):
    """Delete a CRM record by module and ID."""
    if dry_run:
        dry_run_output("DELETE", f"{config.get_crm_base()}/{module}/{record_id}")
        return
    client = _client(ctx)
    result = client.delete_record(module, record_id)
    render(result, json_mode=json_mode, quiet=quiet)


@crm_group.command("search", short_help="Search records by criteria")
@click.argument("module")
@click.argument("criteria")
@click.option("--limit", default=config.DEFAULT_PAGE_SIZE, type=int, help="Records per page")
@click.option("--page", default=1, type=int, help="Page number")
@click.option("--all", "fetch_all", is_flag=True, help="Auto-paginate all results")
@click.option("--json", "json_mode", is_flag=True, help="JSON output")
@click.option("--fields", default=None, help="Comma-separated field names")
@click.option("--quiet", is_flag=True, help="Suppress non-data output")
@click.pass_context
def search_records(ctx, module, criteria, limit, page, fetch_all, json_mode, fields, quiet):
    """Search CRM records. Criteria format: (Field:equals:Value)."""
    client = _client(ctx)
    if fetch_all:
        result = paginate_all(lambda p: client.search(module, criteria, limit=config.MAX_PAGE_SIZE, page=p))
    else:
        result = client.search(module, criteria, limit=limit, page=page)
    render(result, json_mode=json_mode, quiet=quiet, fields=fields)


@crm_group.command("query", short_help="Execute a COQL query")
@click.argument("coql")
@click.option("--json", "json_mode", is_flag=True, help="JSON output")
@click.option("--fields", default=None, help="Comma-separated field names")
@click.option("--quiet", is_flag=True, help="Suppress non-data output")
@click.pass_context
def coql_query(ctx, coql, json_mode, fields, quiet):
    """Execute a raw COQL query against CRM."""
    client = _client(ctx)
    result = client.coql_query(coql)
    render(result, json_mode=json_mode, quiet=quiet, fields=fields)


@crm_group.command("fields", short_help="List fields for a module")
@click.argument("module")
@click.option("--json", "json_mode", is_flag=True, help="JSON output")
@click.option("--quiet", is_flag=True, help="Suppress non-data output")
@click.pass_context
def list_fields(ctx, module, json_mode, quiet):
    """List all fields for a CRM module with API name, label, and type."""
    client = _client(ctx)
    raw_fields = client.get_fields(module)
    compact = [
        {
            "api_name": f["api_name"],
            "label": f.get("field_label", f.get("display_label", "")),
            "type": f.get("data_type", ""),
            "required": f.get("system_mandatory", False),
        }
        for f in raw_fields
    ]
    render(compact, json_mode=json_mode, quiet=quiet)


@crm_group.command("modules", short_help="List all CRM modules")
@click.option("--json", "json_mode", is_flag=True, help="JSON output")
@click.option("--quiet", is_flag=True, help="Suppress non-data output")
@click.pass_context
def list_modules(ctx, json_mode, quiet):
    """List all available CRM modules."""
    client = _client(ctx)
    raw = client.get_modules()
    compact = [
        {
            "api_name": m["api_name"],
            "label": m.get("plural_label", m.get("singular_label", "")),
            "generated_type": m.get("generated_type", ""),
        }
        for m in raw
    ]
    render(compact, json_mode=json_mode, quiet=quiet)


# --- Register Phase B subgroups ---
from cli_zoho.crm.automation_commands import (
    workflows_group, blueprint_group, scoring_group, assignments_group,
)
from cli_zoho.crm.metadata_commands import (
    layouts_group, views_group, related_lists_group,
)
from cli_zoho.crm.settings_commands import (
    pipelines_group, variables_group, org_settings_group,
)
from cli_zoho.crm.functions_commands import functions_group
from cli_zoho.crm.users_commands import users_group
from cli_zoho.crm.composite_commands import composite_group
from cli_zoho.crm.bulk_commands import bulk_group
from cli_zoho.crm.mass_commands import mass_group
from cli_zoho.crm.notes_commands import notes_group
from cli_zoho.crm.tags_commands import tags_group
from cli_zoho.crm.related_commands import related_group
from cli_zoho.crm.trash_commands import trash_group

crm_group.add_command(workflows_group)
crm_group.add_command(blueprint_group)
crm_group.add_command(scoring_group)
crm_group.add_command(assignments_group)
crm_group.add_command(layouts_group)
crm_group.add_command(views_group)
crm_group.add_command(related_lists_group)
crm_group.add_command(pipelines_group)
crm_group.add_command(variables_group)
crm_group.add_command(org_settings_group)
crm_group.add_command(functions_group)
crm_group.add_command(users_group)
crm_group.add_command(composite_group)
crm_group.add_command(bulk_group)
crm_group.add_command(mass_group)
crm_group.add_command(notes_group)
crm_group.add_command(tags_group)
crm_group.add_command(related_group)
crm_group.add_command(trash_group)


