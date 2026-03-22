"""Click commands for Zoho CRM function execution."""
import json
import click
from cli_zoho.crm.functions import FunctionsClient
from cli_zoho.shared.output import render, error_out


def _client(ctx) -> FunctionsClient:
    return FunctionsClient(ctx.obj["auth"])


@click.group("functions", short_help="CRM function execution")
@click.pass_context
def functions_group(ctx):
    """Execute standalone Deluge functions via REST API."""
    pass


@functions_group.command("execute", short_help="Execute a standalone function")
@click.argument("function_name")
@click.option("--args", "arguments", default=None, help="JSON string of function arguments")
@click.option("--method", default="POST", type=click.Choice(["GET", "POST"]), help="HTTP method (default: POST)")
@click.option("--auth-type", default="apikey", type=click.Choice(["oauth", "apikey"]), help="Auth method (default: apikey)")
@click.option("--api-key", default=None, help="Per-function API key (required for apikey auth)")
@click.option("--json", "json_mode", is_flag=True, help="JSON output")
@click.option("--quiet", is_flag=True, help="Suppress non-data output")
@click.pass_context
def fn_execute(ctx, function_name, arguments, method, auth_type, api_key, json_mode, quiet):
    """Execute a standalone CRM function by API name."""
    parsed_args = None
    if arguments:
        try:
            parsed_args = json.loads(arguments)
        except json.JSONDecodeError as e:
            error_out(f"Invalid JSON in --args: {e}")
            return

    if auth_type == "apikey" and not api_key:
        error_out("--api-key is required when --auth-type is apikey")
        return

    client = _client(ctx)
    result = client.execute(function_name, arguments=parsed_args, method=method, auth_type=auth_type, api_key=api_key)
    render(result, json_mode=json_mode, quiet=quiet)
