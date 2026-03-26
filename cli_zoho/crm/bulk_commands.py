"""Click commands for Zoho CRM Bulk Read/Write operations."""

import json

import click

from cli_zoho.crm.bulk import BulkClient
from cli_zoho.shared.output import render, error_out, dry_run_output, parse_data


def _client(ctx) -> BulkClient:
    return BulkClient(ctx.obj["auth_app3"])


@click.group("bulk")
def bulk_group():
    """Zoho CRM Bulk Read/Write API operations."""


@bulk_group.command("read")
@click.argument("module")
@click.option("--query", default=None, help="Extra query params as JSON (merged into query body).")
@click.option("--file-type", default="csv", type=click.Choice(["csv", "ics"]), show_default=True)
@click.option("--page", default=None, type=int, help="Page number for paginated bulk read.")
@click.option("--dry-run", is_flag=True, help="Preview request without executing.")
@click.option("--json", "as_json", is_flag=True, help="Output raw JSON.")
@click.option("--quiet", is_flag=True, help="Suppress output, exit 0 on success.")
@click.pass_context
def bulk_read(ctx, module, query, file_type, page, dry_run, as_json, quiet):
    """Create a bulk read job for MODULE."""
    parsed_query = None
    if query:
        try:
            parsed_query = json.loads(query)
        except json.JSONDecodeError as exc:
            error_out(f"Invalid JSON for --query: {exc}")

    if dry_run:
        dry_run_output(
            "POST",
            "/crm/v8/bulk/read",
            body={"module": module, "query": parsed_query, "file_type": file_type, "page": page},
        )
        return

    result = _client(ctx).create_read_job(module, query=parsed_query, file_type=file_type, page=page)
    render(result, as_json=as_json, quiet=quiet)


@bulk_group.command("read-status")
@click.argument("job_id")
@click.option("--json", "as_json", is_flag=True, help="Output raw JSON.")
@click.option("--quiet", is_flag=True, help="Suppress output.")
@click.pass_context
def bulk_read_status(ctx, job_id, as_json, quiet):
    """Check status of a bulk read job JOB_ID."""
    result = _client(ctx).get_read_job(job_id)
    render(result, as_json=as_json, quiet=quiet)


@bulk_group.command("download")
@click.argument("job_id")
@click.option("--output", required=True, help="Local file path to save downloaded result.")
@click.pass_context
def bulk_download(ctx, job_id, output):
    """Download bulk read result for JOB_ID to --output file."""
    resp = _client(ctx).download_read_result(job_id)
    if not resp.ok:
        error_out(f"Download failed: HTTP {resp.status_code}")
    with open(output, "wb") as fh:
        fh.write(resp.content)
    click.echo(f"Saved to {output} ({len(resp.content)} bytes)")


@bulk_group.command("write")
@click.argument("module")
@click.argument("file_path")
@click.option(
    "--operation",
    default="insert",
    type=click.Choice(["insert", "update", "upsert"]),
    show_default=True,
)
@click.option("--file-type", default="csv", type=click.Choice(["csv", "ics"]), show_default=True)
@click.option("--dry-run", is_flag=True, help="Preview request without executing.")
@click.option("--json", "as_json", is_flag=True, help="Output raw JSON.")
@click.option("--quiet", is_flag=True, help="Suppress output.")
@click.pass_context
def bulk_write(ctx, module, file_path, operation, file_type, dry_run, as_json, quiet):
    """Create a bulk write job for MODULE using FILE_PATH."""
    if dry_run:
        dry_run_output(
            "POST",
            "/crm/v8/bulk/write",
            body={"module": module, "file_path": file_path, "operation": operation, "file_type": file_type},
        )
        return

    result = _client(ctx).create_write_job(module, file_path, operation=operation, file_type=file_type)
    render(result, as_json=as_json, quiet=quiet)


@bulk_group.command("write-status")
@click.argument("job_id")
@click.option("--json", "as_json", is_flag=True, help="Output raw JSON.")
@click.option("--quiet", is_flag=True, help="Suppress output.")
@click.pass_context
def bulk_write_status(ctx, job_id, as_json, quiet):
    """Check status of a bulk write job JOB_ID."""
    result = _client(ctx).get_write_job(job_id)
    render(result, as_json=as_json, quiet=quiet)
