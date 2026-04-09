"""Click commands for Zoho CRM Mass Update/Delete operations."""

import json

import click

from cli_zoho.crm.zoho_cli_crm_mass import MassClient
from cli_zoho.shared.zoho_cli_shared_output import render, error_out, dry_run_output, parse_data


def _client(ctx) -> MassClient:
    return MassClient(ctx.obj["auth_app3"])


@click.group("mass")
def mass_group():
    """Zoho CRM Mass Update/Delete operations."""


@mass_group.command("update")
@click.argument("module")
@click.option("--data", required=True, help="JSON array or object with fields to update.")
@click.option("--ids", default=None, help="Comma-separated record IDs to target.")
@click.option("--criteria", default=None, help="Criteria as JSON for targeted update.")
@click.option("--dry-run", is_flag=True, help="Preview request without executing.")
@click.option("--json", "as_json", is_flag=True, help="Output raw JSON.")
@click.option("--quiet", is_flag=True, help="Suppress output.")
@click.pass_context
def mass_update(ctx, module, data, ids, criteria, dry_run, as_json, quiet):
    """Mass update records in MODULE."""
    try:
        parsed_data = json.loads(data)
    except json.JSONDecodeError as exc:
        error_out(f"Invalid JSON for --data: {exc}")

    # Normalize to list
    if isinstance(parsed_data, dict):
        parsed_data = [parsed_data]

    parsed_ids = [i.strip() for i in ids.split(",")] if ids else None

    parsed_criteria = None
    if criteria:
        try:
            parsed_criteria = json.loads(criteria)
        except json.JSONDecodeError as exc:
            error_out(f"Invalid JSON for --criteria: {exc}")

    if not parsed_ids and not parsed_criteria:
        error_out("Provide --ids or --criteria to target records.")

    if dry_run:
        dry_run_output(
            "POST",
            f"/crm/v8/{module}/actions/mass_update",
            body={"data": parsed_data, "ids": parsed_ids, "criteria": parsed_criteria},
        )
        return

    result = _client(ctx).mass_update(module, parsed_data, ids=parsed_ids, criteria=parsed_criteria)
    render(result, as_json=as_json, quiet=quiet)


@mass_group.command("update-status")
@click.argument("module")
@click.argument("job_id")
@click.option("--json", "as_json", is_flag=True, help="Output raw JSON.")
@click.option("--quiet", is_flag=True, help="Suppress output.")
@click.pass_context
def mass_update_status(ctx, module, job_id, as_json, quiet):
    """Check status of a mass update job JOB_ID in MODULE."""
    result = _client(ctx).get_mass_update_status(module, job_id)
    render(result, as_json=as_json, quiet=quiet)


@mass_group.command("delete")
@click.argument("module")
@click.option("--ids", default=None, help="Comma-separated record IDs to delete.")
@click.option("--criteria", default=None, help="Criteria as JSON for targeted delete.")
@click.option("--dry-run", is_flag=True, help="Preview request without executing.")
@click.option("--json", "as_json", is_flag=True, help="Output raw JSON.")
@click.option("--quiet", is_flag=True, help="Suppress output.")
@click.pass_context
def mass_delete(ctx, module, ids, criteria, dry_run, as_json, quiet):
    """Mass delete records in MODULE."""
    parsed_ids = [i.strip() for i in ids.split(",")] if ids else None

    parsed_criteria = None
    if criteria:
        try:
            parsed_criteria = json.loads(criteria)
        except json.JSONDecodeError as exc:
            error_out(f"Invalid JSON for --criteria: {exc}")

    if not parsed_ids and not parsed_criteria:
        error_out("Provide --ids or --criteria to target records.")

    if dry_run:
        dry_run_output(
            "POST",
            f"/crm/v8/{module}/actions/mass_delete",
            body={"ids": parsed_ids, "criteria": parsed_criteria},
        )
        return

    result = _client(ctx).mass_delete(module, ids=parsed_ids, criteria=parsed_criteria)
    render(result, as_json=as_json, quiet=quiet)


@mass_group.command("delete-status")
@click.argument("module")
@click.argument("job_id")
@click.option("--json", "as_json", is_flag=True, help="Output raw JSON.")
@click.option("--quiet", is_flag=True, help="Suppress output.")
@click.pass_context
def mass_delete_status(ctx, module, job_id, as_json, quiet):
    """Check status of a mass delete job JOB_ID in MODULE."""
    result = _client(ctx).get_mass_delete_status(module, job_id)
    render(result, as_json=as_json, quiet=quiet)
