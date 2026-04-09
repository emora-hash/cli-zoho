"""Click commands for Zoho CRM Related Records."""

import click

from cli_zoho import config
from cli_zoho.crm.zoho_cli_crm_related import RelatedClient
from cli_zoho.shared.zoho_cli_shared_output import render
from cli_zoho.shared.zoho_cli_shared_pagination import paginate_all


def _client(ctx) -> RelatedClient:
    return RelatedClient(ctx.obj["auth"])


@click.group("related", short_help="Related records on CRM records")
@click.pass_context
def related_group(ctx):
    """Zoho CRM: list related records (line items, activities, contacts, etc.)."""
    pass


@related_group.command("list", short_help="List related records")
@click.argument("module")
@click.argument("record_id")
@click.argument("related_module")
@click.option("--limit", default=config.DEFAULT_PAGE_SIZE, type=int, help="Records per page")
@click.option("--page", default=1, type=int, help="Page number")
@click.option("--all", "fetch_all", is_flag=True, help="Auto-paginate all results")
@click.option("--json", "json_mode", is_flag=True, help="JSON output")
@click.option("--fields", default=None, help="Comma-separated field names")
@click.option("--quiet", is_flag=True, help="Suppress non-data output")
@click.pass_context
def list_related(ctx, module, record_id, related_module, limit, page, fetch_all, json_mode, fields, quiet):
    """List records related to a CRM record.

    Examples:

    \b
      crm related list Deals 999 Contacts
      crm related list Deals 999 Products
      crm related list Accounts 888 Contacts --all
    """
    client = _client(ctx)
    if fetch_all:
        result = paginate_all(
            lambda p: client.list_related(module, record_id, related_module, page=p, per_page=config.MAX_PAGE_SIZE)
        )
    else:
        result = client.list_related(module, record_id, related_module, page=page, per_page=limit)
    render(result, json_mode=json_mode, quiet=quiet, fields=fields)
