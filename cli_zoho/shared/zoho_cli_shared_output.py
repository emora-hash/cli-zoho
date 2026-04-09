"""Output formatting: JSON for agents, compact tables for humans."""

import json
import os
import sys
from typing import NoReturn

import click


def render(data: dict | list, *, json_mode: bool, quiet: bool, pretty: bool = False, fields: str | None = None):
    """Render data to stdout. Filters fields if specified."""
    filtered = _filter_fields(data, fields)

    # Auto-detect --pretty from root CLI context if not explicitly passed
    if not pretty:
        ctx = click.get_current_context(silent=True)
        if ctx:
            root = ctx.find_root()
            pretty = root.params.get("pretty", False) or (root.obj or {}).get("pretty", False)

    if json_mode:
        indent = 2 if pretty else None
        click.echo(json.dumps(filtered, indent=indent, default=str))
        return

    if quiet:
        return

    if isinstance(filtered, dict) and "data" in filtered:
        _print_table(filtered["data"], filtered.get("has_more"), filtered.get("next_page"))
    elif isinstance(filtered, list):
        _print_table(filtered)
    elif isinstance(filtered, dict):
        for k, v in filtered.items():
            click.echo(f"{k}: {v}")


def _filter_fields(data: dict | list, fields: str | None):
    """Filter records to only requested fields."""
    if not fields:
        return data

    wanted = {f.strip() for f in fields.split(",")}

    if isinstance(data, dict) and "data" in data:
        filtered_records = [{k: r.get(k) for k in wanted} for r in data["data"]]
        return {**data, "data": filtered_records}
    elif isinstance(data, list):
        return [{k: r.get(k) for k in wanted} for r in data if isinstance(r, dict)]
    return data


def _terminal_width() -> int:
    """Get terminal width, defaulting to 120 for non-TTY (agent pipelines)."""
    try:
        return os.get_terminal_size().columns
    except (ValueError, OSError):
        return 120


def _print_table(records: list, has_more: bool | None = None, next_page: int | None = None):
    """Print records as a compact aligned table."""
    if not records:
        click.echo("No records found.")
        return

    all_cols = list(records[0].keys())
    term_width = _terminal_width()

    # Determine how many columns fit in terminal width
    col_width = 30
    col_gap = 2
    max_cols = max(1, (term_width + col_gap) // (col_width + col_gap))
    cols = all_cols[:max_cols]
    hidden = len(all_cols) - len(cols)

    widths = {c: min(col_width, max(len(c), max((len(str(r.get(c, ""))[:col_width]) for r in records), default=0))) for c in cols}

    header = "  ".join(c.ljust(widths[c])[:col_width] for c in cols)
    click.echo(header)
    click.echo("-" * len(header))

    for r in records:
        row = "  ".join(str(r.get(c, ""))[:col_width].ljust(widths[c]) for c in cols)
        click.echo(row)

    summary = f"\n{len(records)} records"
    if hidden > 0:
        summary += f" [+{hidden} columns hidden]"
    if has_more:
        summary += f" (more available, next page: {next_page})"
    click.echo(summary)


def dry_run_output(method: str, url: str, body: dict | None = None):
    """Print what a destructive operation WOULD do, without executing."""
    click.echo(f"[DRY RUN] {method} {url}", err=True)
    if body:
        click.echo(json.dumps(body, indent=2, default=str), err=True)


def error_out(message: str, code: int = 1) -> NoReturn:
    """Print error to stderr and exit."""
    click.echo(f"Error: {message}", err=True)
    sys.exit(code)


def parse_data(data_str: str | None, file_path: str | None) -> dict:
    """Parse record data from --data JSON string or --file path."""
    if data_str:
        try:
            return json.loads(data_str)
        except json.JSONDecodeError as e:
            error_out(f"Invalid JSON in --data: {e}")
    if file_path:
        try:
            with open(file_path) as f:
                return json.load(f)
        except (json.JSONDecodeError, OSError) as e:
            error_out(f"Failed to read --file: {e}")
    error_out("Provide --data or --file with record data")
