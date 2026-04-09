"""Click commands for Zoho CRM Notes."""

import click

from cli_zoho import config
from cli_zoho.crm.zoho_cli_crm_notes import NotesClient
from cli_zoho.shared.zoho_cli_shared_output import render, dry_run_output


def _client(ctx) -> NotesClient:
    return NotesClient(ctx.obj["auth"])


@click.group("notes", short_help="Notes on CRM records")
@click.pass_context
def notes_group(ctx):
    """Zoho CRM: list, create, and delete record notes."""
    pass


@notes_group.command("list", short_help="List notes on a record")
@click.argument("module")
@click.argument("record_id")
@click.option("--limit", default=config.DEFAULT_PAGE_SIZE, type=int, help="Records per page")
@click.option("--page", default=1, type=int, help="Page number")
@click.option("--json", "json_mode", is_flag=True, help="JSON output")
@click.option("--quiet", is_flag=True, help="Suppress non-data output")
@click.pass_context
def list_notes(ctx, module, record_id, limit, page, json_mode, quiet):
    """List all notes attached to a CRM record."""
    client = _client(ctx)
    result = client.list_notes(module, record_id, page=page, per_page=limit)
    render(result, json_mode=json_mode, quiet=quiet)


@notes_group.command("create", short_help="Add a note to a record")
@click.argument("module")
@click.argument("record_id")
@click.option("--note", "note_content", required=True, help="Note body text")
@click.option("--title", default="", help="Note title (optional)")
@click.option("--dry-run", is_flag=True, help="Show request without executing")
@click.option("--json", "json_mode", is_flag=True, help="JSON output")
@click.option("--quiet", is_flag=True, help="Suppress non-data output")
@click.pass_context
def create_note(ctx, module, record_id, note_content, title, dry_run, json_mode, quiet):
    """Add a note to a CRM record."""
    if dry_run:
        payload: dict = {
            "Note_Content": note_content,
            "Parent_Id": {"id": record_id},
            "$se_module": module,
        }
        if title:
            payload["Note_Title"] = title
        dry_run_output("POST", f"{config.get_crm_base()}/Notes", {"data": [payload]})
        return
    client = _client(ctx)
    result = client.create_note(module, record_id, note_content, title=title)
    render(result, json_mode=json_mode, quiet=quiet)


@notes_group.command("delete", short_help="Delete a note by ID")
@click.argument("note_id")
@click.option("--dry-run", is_flag=True, help="Show request without executing")
@click.option("--json", "json_mode", is_flag=True, help="JSON output")
@click.option("--quiet", is_flag=True, help="Suppress non-data output")
@click.pass_context
def delete_note(ctx, note_id, dry_run, json_mode, quiet):
    """Delete a CRM note by ID."""
    if dry_run:
        dry_run_output("DELETE", f"{config.get_crm_base()}/Notes/{note_id}")
        return
    client = _client(ctx)
    result = client.delete_note(note_id)
    render(result, json_mode=json_mode, quiet=quiet)
