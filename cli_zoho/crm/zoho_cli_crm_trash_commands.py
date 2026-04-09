"""Click commands for Zoho CRM Recycle Bin. Routes through App #3."""

import click

from cli_zoho import config
from cli_zoho.crm.zoho_cli_crm_trash import TrashClient
from cli_zoho.shared.zoho_cli_shared_output import render, dry_run_output


def _client(ctx) -> TrashClient:
    return TrashClient(ctx.obj["auth_app3"])


@click.group("trash", short_help="CRM recycle bin (deleted records)")
@click.pass_context
def trash_group(ctx):
    """Zoho CRM recycle bin: list, restore, or permanently purge deleted records."""
    pass


@trash_group.command("list", short_help="List deleted records")
@click.option("--module", default="", help="Filter by CRM module (e.g., Deals, Contacts)")
@click.option("--limit", default=config.DEFAULT_PAGE_SIZE, type=int, help="Records per page")
@click.option("--page", default=1, type=int, help="Page number")
@click.option("--json", "json_mode", is_flag=True, help="JSON output")
@click.option("--quiet", is_flag=True, help="Suppress non-data output")
@click.pass_context
def list_trash(ctx, module, limit, page, json_mode, quiet):
    """List records in the CRM recycle bin."""
    client = _client(ctx)
    result = client.list_trash(module, page=page, per_page=limit)
    render(result, json_mode=json_mode, quiet=quiet)


@trash_group.command("restore", short_help="Restore deleted records")
@click.argument("record_ids", nargs=-1, required=True)
@click.option("--dry-run", is_flag=True, help="Show request without executing")
@click.option("--json", "json_mode", is_flag=True, help="JSON output")
@click.option("--quiet", is_flag=True, help="Suppress non-data output")
@click.pass_context
def restore_records(ctx, record_ids, dry_run, json_mode, quiet):
    """Restore one or more records from the CRM recycle bin."""
    ids = list(record_ids)
    if dry_run:
        dry_run_output("PUT", f"{config.get_crm_base()}/recycle_bin", {"ids": ",".join(ids)})
        return
    client = _client(ctx)
    result = client.restore(ids)
    render(result, json_mode=json_mode, quiet=quiet)


@trash_group.command("purge", short_help="Permanently delete records from recycle bin")
@click.argument("record_ids", nargs=-1, required=True)
@click.option("--dry-run", is_flag=True, help="Show request without executing")
@click.option("--json", "json_mode", is_flag=True, help="JSON output")
@click.option("--quiet", is_flag=True, help="Suppress non-data output")
@click.pass_context
def purge_records(ctx, record_ids, dry_run, json_mode, quiet):
    """Permanently delete records from the recycle bin (irreversible)."""
    ids = list(record_ids)
    if dry_run:
        dry_run_output("DELETE", f"{config.get_crm_base()}/recycle_bin", {"ids": ",".join(ids)})
        return
    client = _client(ctx)
    result = client.purge(ids)
    render(result, json_mode=json_mode, quiet=quiet)
