"""Click commands for Zoho CRM settings — pipelines, variables, business hours, fiscal year."""

import json

import click

from cli_zoho.crm.zoho_cli_crm_settings import SettingsClient
from cli_zoho import config
from cli_zoho.shared.zoho_cli_shared_output import render, error_out, dry_run_output


def _client(ctx) -> SettingsClient:
    return SettingsClient(ctx.obj["auth"])


# --- Pipelines ---

@click.group("pipelines", short_help="Sales pipeline management")
@click.pass_context
def pipelines_group(ctx):
    """CRM pipelines: list, create, update deal pipelines."""
    pass


@pipelines_group.command("list", short_help="List all pipelines")
@click.option("--layout-id", default=None, help="Layout ID (required by Zoho v8)")
@click.option("--json", "json_mode", is_flag=True, help="JSON output")
@click.option("--quiet", is_flag=True, help="Suppress non-data output")
@click.pass_context
def pipelines_list(ctx, layout_id, json_mode, quiet):
    """List all sales pipelines. Use --layout-id to filter (required by v8 API)."""
    client = _client(ctx)
    result = client.get_pipelines(layout_id=layout_id)
    render(result, json_mode=json_mode, quiet=quiet)


@pipelines_group.command("create", short_help="Create a pipeline")
@click.option("--data", required=True, help="JSON string of pipeline data")
@click.option("--dry-run", is_flag=True, help="Show request without executing")
@click.option("--json", "json_mode", is_flag=True, help="JSON output")
@click.option("--quiet", is_flag=True, help="Suppress non-data output")
@click.pass_context
def pipelines_create(ctx, data, dry_run, json_mode, quiet):
    """Create a new pipeline."""
    try:
        parsed = json.loads(data)
    except json.JSONDecodeError as e:
        error_out(f"Invalid JSON: {e}")
        return
    if dry_run:
        dry_run_output("POST", f"{config.get_crm_base()}/settings/pipeline", parsed)
        return
    client = _client(ctx)
    result = client.create_pipeline(parsed)
    render(result, json_mode=json_mode, quiet=quiet)


@pipelines_group.command("update", short_help="Update a pipeline")
@click.argument("pipeline_id")
@click.option("--data", required=True, help="JSON string of updated data")
@click.option("--dry-run", is_flag=True, help="Show request without executing")
@click.option("--json", "json_mode", is_flag=True, help="JSON output")
@click.option("--quiet", is_flag=True, help="Suppress non-data output")
@click.pass_context
def pipelines_update(ctx, pipeline_id, data, dry_run, json_mode, quiet):
    """Update a pipeline by ID."""
    try:
        parsed = json.loads(data)
    except json.JSONDecodeError as e:
        error_out(f"Invalid JSON: {e}")
        return
    if dry_run:
        dry_run_output("PUT", f"{config.get_crm_base()}/settings/pipeline/{pipeline_id}", parsed)
        return
    client = _client(ctx)
    result = client.update_pipeline(pipeline_id, parsed)
    render(result, json_mode=json_mode, quiet=quiet)


# --- Variables ---

@click.group("variables", short_help="CRM variables")
@click.pass_context
def variables_group(ctx):
    """CRM variables: list, create, update, delete org variables."""
    pass


@variables_group.command("list", short_help="List all variables")
@click.option("--json", "json_mode", is_flag=True, help="JSON output")
@click.option("--quiet", is_flag=True, help="Suppress non-data output")
@click.pass_context
def variables_list(ctx, json_mode, quiet):
    """List all CRM variables."""
    client = _client(ctx)
    result = client.get_variables()
    render(result, json_mode=json_mode, quiet=quiet)


@variables_group.command("create", short_help="Create a variable")
@click.option("--data", required=True, help="JSON string of variable data")
@click.option("--dry-run", is_flag=True, help="Show request without executing")
@click.option("--json", "json_mode", is_flag=True, help="JSON output")
@click.option("--quiet", is_flag=True, help="Suppress non-data output")
@click.pass_context
def variables_create(ctx, data, dry_run, json_mode, quiet):
    """Create a new CRM variable."""
    try:
        parsed = json.loads(data)
    except json.JSONDecodeError as e:
        error_out(f"Invalid JSON: {e}")
        return
    if dry_run:
        dry_run_output("POST", f"{config.get_crm_base()}/settings/variables", parsed)
        return
    client = _client(ctx)
    result = client.create_variable(parsed)
    render(result, json_mode=json_mode, quiet=quiet)


@variables_group.command("update", short_help="Update a variable")
@click.argument("variable_id")
@click.option("--data", required=True, help="JSON string of updated data")
@click.option("--dry-run", is_flag=True, help="Show request without executing")
@click.option("--json", "json_mode", is_flag=True, help="JSON output")
@click.option("--quiet", is_flag=True, help="Suppress non-data output")
@click.pass_context
def variables_update(ctx, variable_id, data, dry_run, json_mode, quiet):
    """Update a CRM variable by ID."""
    try:
        parsed = json.loads(data)
    except json.JSONDecodeError as e:
        error_out(f"Invalid JSON: {e}")
        return
    if dry_run:
        dry_run_output("PUT", f"{config.get_crm_base()}/settings/variables/{variable_id}", parsed)
        return
    client = _client(ctx)
    result = client.update_variable(variable_id, parsed)
    render(result, json_mode=json_mode, quiet=quiet)


@variables_group.command("delete", short_help="Delete a variable")
@click.argument("variable_id")
@click.option("--dry-run", is_flag=True, help="Show request without executing")
@click.option("--json", "json_mode", is_flag=True, help="JSON output")
@click.option("--quiet", is_flag=True, help="Suppress non-data output")
@click.pass_context
def variables_delete(ctx, variable_id, dry_run, json_mode, quiet):
    """Delete a CRM variable by ID."""
    if dry_run:
        dry_run_output("DELETE", f"{config.get_crm_base()}/settings/variables/{variable_id}")
        return
    client = _client(ctx)
    result = client.delete_variable(variable_id)
    render(result, json_mode=json_mode, quiet=quiet)


@variables_group.command("groups", short_help="List variable groups")
@click.option("--json", "json_mode", is_flag=True, help="JSON output")
@click.option("--quiet", is_flag=True, help="Suppress non-data output")
@click.pass_context
def variables_groups(ctx, json_mode, quiet):
    """List all variable groups."""
    client = _client(ctx)
    result = client.get_variable_groups()
    render(result, json_mode=json_mode, quiet=quiet)


# --- Business Hours & Fiscal Year ---

@click.group("org-settings", short_help="Org-level settings")
@click.pass_context
def org_settings_group(ctx):
    """CRM org settings: business hours, fiscal year."""
    pass


@org_settings_group.command("business-hours", short_help="Get business hours")
@click.option("--json", "json_mode", is_flag=True, help="JSON output")
@click.option("--quiet", is_flag=True, help="Suppress non-data output")
@click.pass_context
def get_business_hours(ctx, json_mode, quiet):
    """Get configured business hours."""
    client = _client(ctx)
    result = client.get_business_hours()
    render(result, json_mode=json_mode, quiet=quiet)


@org_settings_group.command("update-business-hours", short_help="Update business hours")
@click.option("--data", required=True, help="JSON string of business hours data")
@click.option("--dry-run", is_flag=True, help="Show request without executing")
@click.option("--json", "json_mode", is_flag=True, help="JSON output")
@click.option("--quiet", is_flag=True, help="Suppress non-data output")
@click.pass_context
def update_business_hours(ctx, data, dry_run, json_mode, quiet):
    """Update business hours configuration."""
    try:
        parsed = json.loads(data)
    except json.JSONDecodeError as e:
        error_out(f"Invalid JSON: {e}")
        return
    if dry_run:
        dry_run_output("PUT", f"{config.get_crm_base()}/settings/business_hours", parsed)
        return
    client = _client(ctx)
    result = client.update_business_hours(parsed)
    render(result, json_mode=json_mode, quiet=quiet)


@org_settings_group.command("fiscal-year", short_help="Get fiscal year config")
@click.option("--json", "json_mode", is_flag=True, help="JSON output")
@click.option("--quiet", is_flag=True, help="Suppress non-data output")
@click.pass_context
def get_fiscal_year(ctx, json_mode, quiet):
    """Get fiscal year configuration."""
    client = _client(ctx)
    result = client.get_fiscal_year()
    render(result, json_mode=json_mode, quiet=quiet)


@org_settings_group.command("update-fiscal-year", short_help="Update fiscal year config")
@click.option("--data", required=True, help="JSON string of fiscal year data")
@click.option("--dry-run", is_flag=True, help="Show request without executing")
@click.option("--json", "json_mode", is_flag=True, help="JSON output")
@click.option("--quiet", is_flag=True, help="Suppress non-data output")
@click.pass_context
def update_fiscal_year(ctx, data, dry_run, json_mode, quiet):
    """Update fiscal year configuration."""
    try:
        parsed = json.loads(data)
    except json.JSONDecodeError as e:
        error_out(f"Invalid JSON: {e}")
        return
    if dry_run:
        dry_run_output("PUT", f"{config.get_crm_base()}/settings/fiscal_year", parsed)
        return
    client = _client(ctx)
    result = client.update_fiscal_year(parsed)
    render(result, json_mode=json_mode, quiet=quiet)


@org_settings_group.command("enable-multi-currency", short_help="Enable multi-currency")
@click.option("--data", required=True, help="JSON string of currency data")
@click.option("--dry-run", is_flag=True, help="Show request without executing")
@click.option("--json", "json_mode", is_flag=True, help="JSON output")
@click.option("--quiet", is_flag=True, help="Suppress non-data output")
@click.pass_context
def enable_multi_currency(ctx, data, dry_run, json_mode, quiet):
    """Enable multi-currency for the org."""
    try:
        parsed = json.loads(data)
    except json.JSONDecodeError as e:
        error_out(f"Invalid JSON: {e}")
        return
    if dry_run:
        dry_run_output("POST", f"{config.get_crm_base()}/settings/currencies", parsed)
        return
    client = _client(ctx)
    result = client.enable_multi_currency(parsed)
    render(result, json_mode=json_mode, quiet=quiet)
