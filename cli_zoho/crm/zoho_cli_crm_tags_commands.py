"""Click commands for Zoho CRM Tags."""

import click

from cli_zoho import config
from cli_zoho.crm.zoho_cli_crm_tags import TagsClient
from cli_zoho.shared.zoho_cli_shared_output import render, dry_run_output


def _client(ctx) -> TagsClient:
    return TagsClient(ctx.obj["auth"])


@click.group("tags", short_help="Tags on CRM modules and records")
@click.pass_context
def tags_group(ctx):
    """Zoho CRM: list module tags, add/remove tags on records."""
    pass


@tags_group.command("list", short_help="List all tags for a module")
@click.argument("module")
@click.option("--json", "json_mode", is_flag=True, help="JSON output")
@click.option("--quiet", is_flag=True, help="Suppress non-data output")
@click.pass_context
def list_tags(ctx, module, json_mode, quiet):
    """List all tags defined for a CRM module."""
    client = _client(ctx)
    result = client.list_tags(module)
    render(result, json_mode=json_mode, quiet=quiet)


@tags_group.command("add", short_help="Add tags to a record")
@click.argument("module")
@click.argument("record_id")
@click.argument("tags", nargs=-1, required=True)
@click.option("--dry-run", is_flag=True, help="Show request without executing")
@click.option("--json", "json_mode", is_flag=True, help="JSON output")
@click.option("--quiet", is_flag=True, help="Suppress non-data output")
@click.pass_context
def add_tags(ctx, module, record_id, tags, dry_run, json_mode, quiet):
    """Add one or more tags to a CRM record."""
    tag_list = list(tags)
    if dry_run:
        dry_run_output(
            "POST",
            f"{config.get_crm_base()}/{module}/{record_id}/tags",
            {"tags": [{"name": t} for t in tag_list]},
        )
        return
    client = _client(ctx)
    result = client.add_tags(module, record_id, tag_list)
    render(result, json_mode=json_mode, quiet=quiet)


@tags_group.command("remove", short_help="Remove tags from a record")
@click.argument("module")
@click.argument("record_id")
@click.argument("tags", nargs=-1, required=True)
@click.option("--dry-run", is_flag=True, help="Show request without executing")
@click.option("--json", "json_mode", is_flag=True, help="JSON output")
@click.option("--quiet", is_flag=True, help="Suppress non-data output")
@click.pass_context
def remove_tags(ctx, module, record_id, tags, dry_run, json_mode, quiet):
    """Remove one or more tags from a CRM record."""
    tag_list = list(tags)
    if dry_run:
        dry_run_output(
            "DELETE",
            f"{config.get_crm_base()}/{module}/{record_id}/tags",
            {"tags": [{"name": t} for t in tag_list]},
        )
        return
    client = _client(ctx)
    result = client.remove_tags(module, record_id, tag_list)
    render(result, json_mode=json_mode, quiet=quiet)
