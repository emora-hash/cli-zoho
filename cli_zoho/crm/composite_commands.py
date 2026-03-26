"""Click commands for Zoho CRM Composite API."""

import click

from cli_zoho import config
from cli_zoho.crm.composite import CompositeClient
from cli_zoho.shared.output import render, parse_data, dry_run_output


def _client(ctx) -> CompositeClient:
    return CompositeClient(ctx.obj["auth"])


@click.group("composite", short_help="Zoho CRM Composite API")
@click.pass_context
def composite_group(ctx):
    """Zoho CRM: execute composite (batch) API requests."""
    pass


@composite_group.command("execute", short_help="Execute a composite API request")
@click.option("--data", default=None, help="JSON string of composite_requests array")
@click.option("--file", "file_path", default=None, type=click.Path(exists=True),
              help="Path to JSON file containing composite_requests array")
@click.option("--dry-run", is_flag=True, help="Show request payload without executing")
@click.option("--json", "json_mode", is_flag=True, help="JSON output")
@click.option("--quiet", is_flag=True, help="Suppress non-data output")
@click.pass_context
def execute(ctx, data, file_path, dry_run, json_mode, quiet):
    """Execute a composite API request.

    The --data or --file value must be a JSON array of sub-request objects,
    each with keys: method, url, referenceId, and optionally body.

    Example:
      zoho crm composite execute --data '[{"method":"GET","url":"/crm/v8/Leads/123","referenceId":"lead1"}]'
    """
    requests_list = parse_data(data, file_path)
    # parse_data returns a dict; if user passed an array, handle both shapes
    if isinstance(requests_list, dict):
        # Allow wrapping: {"composite_requests": [...]}
        requests_list = requests_list.get("composite_requests", requests_list)

    if dry_run:
        dry_run_output(
            "POST",
            f"{config.get_crm_base()}/composite",
            {"composite_requests": requests_list},
        )
        return

    client = _client(ctx)
    result = client.execute(requests_list)
    render(result, json_mode=json_mode, quiet=quiet)
