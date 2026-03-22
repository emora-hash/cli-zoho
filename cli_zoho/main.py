"""cli-zoho: Agent-native CLI for Zoho CRM and Zoho Inventory."""

import logging
import sys

import click

from cli_zoho import __version__
from cli_zoho.auth import ZohoAuth
from cli_zoho.crm.commands import crm_group
from cli_zoho.inventory.commands import inventory_group
from cli_zoho.shared.output import render


@click.group(invoke_without_command=True)
@click.version_option(version=__version__, prog_name="cli-zoho")
@click.option("--debug", is_flag=True, help="Enable debug logging to stderr")
@click.option("--pretty", is_flag=True, help="Pretty-print JSON output (use with --json)")
@click.pass_context
def cli(ctx, debug, pretty):
    """Zoho CRM + Inventory CLI — agent-native, context-friendly."""
    ctx.ensure_object(dict)
    ctx.obj["pretty"] = pretty
    if debug:
        logging.basicConfig(level=logging.DEBUG, stream=sys.stderr,
                            format="%(name)s %(levelname)s: %(message)s")
    ctx.obj["auth"] = ZohoAuth()
    if ctx.invoked_subcommand is None:
        click.echo(ctx.get_help())


# Register command groups
cli.add_command(crm_group)
cli.add_command(inventory_group, name="inventory")
cli.add_command(inventory_group, name="inv")  # alias


@cli.group("auth", short_help="Authentication management")
@click.pass_context
def auth_group(ctx):
    """Manage Zoho OAuth2 authentication."""
    pass


@auth_group.command("status", short_help="Check auth status")
@click.option("--json", "json_mode", is_flag=True, help="JSON output")
@click.pass_context
def auth_status(ctx, json_mode):
    """Check if Zoho credentials are valid."""
    auth = ctx.obj["auth"]
    result = auth.status()
    render(result, json_mode=json_mode, quiet=False)


@auth_group.command("refresh", short_help="Force token refresh")
@click.option("--json", "json_mode", is_flag=True, help="JSON output")
@click.pass_context
def auth_refresh(ctx, json_mode):
    """Force a new access token from the refresh token."""
    auth = ctx.obj["auth"]
    auth.refresh()
    result = {"refreshed": True, "has_token": True}
    render(result, json_mode=json_mode, quiet=False)


@cli.group("info", short_help="CLI and org information")
@click.pass_context
def info_group(ctx):
    """CLI version and Zoho org info."""
    pass


@info_group.command("version", short_help="Show CLI version")
def info_version():
    """Print cli-zoho version."""
    click.echo(f"cli-zoho {__version__}")


@info_group.command("org", short_help="Show Zoho org info")
@click.option("--json", "json_mode", is_flag=True, help="JSON output")
@click.pass_context
def info_org(ctx, json_mode):
    """Show Zoho organization details."""
    from cli_zoho import config
    auth = ctx.obj["auth"]
    resp = auth.request("GET", f"{config.get_inventory_base()}/organizations")
    orgs = resp.json().get("organizations", [])
    render(orgs, json_mode=json_mode, quiet=False)


if __name__ == "__main__":
    cli()
