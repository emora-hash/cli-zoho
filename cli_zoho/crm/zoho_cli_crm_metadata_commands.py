"""Click commands for Zoho CRM metadata — layouts, custom views, related lists."""

import click

from cli_zoho.crm.zoho_cli_crm_metadata import MetadataClient
from cli_zoho.shared.zoho_cli_shared_output import render


def _client(ctx) -> MetadataClient:
    return MetadataClient(ctx.obj["auth"])


# --- Layouts ---

@click.group("layouts", short_help="Module layouts")
@click.pass_context
def layouts_group(ctx):
    """CRM layouts: list and inspect page layouts per module."""
    pass


@layouts_group.command("list", short_help="List layouts for a module")
@click.argument("module")
@click.option("--json", "json_mode", is_flag=True, help="JSON output")
@click.option("--quiet", is_flag=True, help="Suppress non-data output")
@click.pass_context
def layouts_list(ctx, module, json_mode, quiet):
    """List all layouts for a CRM module."""
    client = _client(ctx)
    result = client.get_layouts(module)
    compact = [
        {"id": l.get("id"), "name": l.get("name"), "status": l.get("status")}
        for l in result
    ]
    render(compact, json_mode=json_mode, quiet=quiet)


@layouts_group.command("get", short_help="Get a specific layout")
@click.argument("module")
@click.argument("layout_id")
@click.option("--json", "json_mode", is_flag=True, help="JSON output")
@click.option("--quiet", is_flag=True, help="Suppress non-data output")
@click.pass_context
def layouts_get(ctx, module, layout_id, json_mode, quiet):
    """Get full detail of a specific layout."""
    client = _client(ctx)
    result = client.get_layout(module, layout_id)
    render(result, json_mode=json_mode, quiet=quiet)


# --- Custom Views ---

@click.group("views", short_help="Custom views")
@click.pass_context
def views_group(ctx):
    """CRM custom views: list and inspect saved views/filters per module."""
    pass


@views_group.command("list", short_help="List custom views for a module")
@click.argument("module")
@click.option("--json", "json_mode", is_flag=True, help="JSON output")
@click.option("--quiet", is_flag=True, help="Suppress non-data output")
@click.pass_context
def views_list(ctx, module, json_mode, quiet):
    """List all custom views for a CRM module."""
    client = _client(ctx)
    result = client.get_custom_views(module)
    compact = [
        {"id": v.get("id"), "name": v.get("name"), "system_name": v.get("system_name")}
        for v in result
    ]
    render(compact, json_mode=json_mode, quiet=quiet)


@views_group.command("get", short_help="Get a specific custom view")
@click.argument("module")
@click.argument("view_id")
@click.option("--json", "json_mode", is_flag=True, help="JSON output")
@click.option("--quiet", is_flag=True, help="Suppress non-data output")
@click.pass_context
def views_get(ctx, module, view_id, json_mode, quiet):
    """Get full detail of a specific custom view including criteria."""
    client = _client(ctx)
    result = client.get_custom_view(module, view_id)
    render(result, json_mode=json_mode, quiet=quiet)


# --- Related Lists ---

@click.group("related-lists", short_help="Related list metadata")
@click.pass_context
def related_lists_group(ctx):
    """CRM related lists: list related record types per module."""
    pass


@related_lists_group.command("list", short_help="List related lists for a module")
@click.argument("module")
@click.option("--json", "json_mode", is_flag=True, help="JSON output")
@click.option("--quiet", is_flag=True, help="Suppress non-data output")
@click.pass_context
def related_lists_list(ctx, module, json_mode, quiet):
    """List all related lists for a CRM module."""
    client = _client(ctx)
    result = client.get_related_lists(module)
    compact = [
        {"api_name": r.get("api_name"), "name": r.get("name"), "module": r.get("module", {}).get("api_name", "")}
        for r in result
    ]
    render(compact, json_mode=json_mode, quiet=quiet)
