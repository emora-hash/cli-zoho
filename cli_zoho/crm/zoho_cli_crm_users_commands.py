"""Click commands for Zoho CRM Users, Roles, and Profiles."""

import click

from cli_zoho import config
from cli_zoho.crm.zoho_cli_crm_users import UsersClient
from cli_zoho.shared.zoho_cli_shared_output import render


def _client(ctx) -> UsersClient:
    return UsersClient(ctx.obj["auth"])


@click.group("users", short_help="Zoho CRM users, roles, and profiles")
@click.pass_context
def users_group(ctx):
    """Zoho CRM: users, roles, and profiles."""
    pass


@users_group.command("list", short_help="List CRM users")
@click.option("--type", "user_type", default="AllUsers", show_default=True,
              help="User type filter (AllUsers, ActiveUsers, DeactiveUsers, etc.)")
@click.option("--limit", default=config.DEFAULT_PAGE_SIZE, type=int, help="Records per page")
@click.option("--page", default=1, type=int, help="Page number")
@click.option("--json", "json_mode", is_flag=True, help="JSON output")
@click.option("--quiet", is_flag=True, help="Suppress non-data output")
@click.pass_context
def list_users(ctx, user_type, limit, page, json_mode, quiet):
    """List CRM users."""
    client = _client(ctx)
    result = client.get_users(type=user_type, page=page, per_page=min(limit, 200))
    render(result, json_mode=json_mode, quiet=quiet)


@users_group.command("get", short_help="Get a single user by ID")
@click.argument("user_id")
@click.option("--json", "json_mode", is_flag=True, help="JSON output")
@click.option("--quiet", is_flag=True, help="Suppress non-data output")
@click.pass_context
def get_user(ctx, user_id, json_mode, quiet):
    """Get a single CRM user by ID."""
    client = _client(ctx)
    result = client.get_user(user_id)
    render(result, json_mode=json_mode, quiet=quiet)


@users_group.command("roles", short_help="List all roles")
@click.option("--json", "json_mode", is_flag=True, help="JSON output")
@click.option("--quiet", is_flag=True, help="Suppress non-data output")
@click.pass_context
def list_roles(ctx, json_mode, quiet):
    """List all CRM roles."""
    client = _client(ctx)
    result = client.get_roles()
    render(result, json_mode=json_mode, quiet=quiet)


@users_group.command("role", short_help="Get a single role by ID")
@click.argument("role_id")
@click.option("--json", "json_mode", is_flag=True, help="JSON output")
@click.option("--quiet", is_flag=True, help="Suppress non-data output")
@click.pass_context
def get_role(ctx, role_id, json_mode, quiet):
    """Get a single CRM role by ID."""
    client = _client(ctx)
    result = client.get_role(role_id)
    render(result, json_mode=json_mode, quiet=quiet)


@users_group.command("profiles", short_help="List all profiles")
@click.option("--json", "json_mode", is_flag=True, help="JSON output")
@click.option("--quiet", is_flag=True, help="Suppress non-data output")
@click.pass_context
def list_profiles(ctx, json_mode, quiet):
    """List all CRM profiles."""
    client = _client(ctx)
    result = client.get_profiles()
    render(result, json_mode=json_mode, quiet=quiet)


@users_group.command("profile", short_help="Get a single profile by ID")
@click.argument("profile_id")
@click.option("--json", "json_mode", is_flag=True, help="JSON output")
@click.option("--quiet", is_flag=True, help="Suppress non-data output")
@click.pass_context
def get_profile(ctx, profile_id, json_mode, quiet):
    """Get a single CRM profile by ID."""
    client = _client(ctx)
    result = client.get_profile(profile_id)
    render(result, json_mode=json_mode, quiet=quiet)
