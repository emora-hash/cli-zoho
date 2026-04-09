"""Click commands for Zoho CRM automation — workflows, blueprint, scoring, assignments."""

import json

import click

from cli_zoho.crm.zoho_cli_crm_automation import AutomationClient
from cli_zoho import config
from cli_zoho.shared.zoho_cli_shared_output import render, error_out, dry_run_output


def _client(ctx) -> AutomationClient:
    return AutomationClient(ctx.obj["auth_app3"])


# --- Workflows ---

@click.group("workflows", short_help="Workflow rules management")
@click.pass_context
def workflows_group(ctx):
    """CRM workflow rules: list, get, update, delete, usage."""
    pass


@workflows_group.command("list", short_help="List all workflow rules")
@click.option("--module", default=None, help="Filter by module name")
@click.option("--json", "json_mode", is_flag=True, help="JSON output")
@click.option("--quiet", is_flag=True, help="Suppress non-data output")
@click.pass_context
def wf_list(ctx, module, json_mode, quiet):
    """List all workflow rules, optionally filtered by module."""
    client = _client(ctx)
    result = client.get_workflows(module=module)
    render(result, json_mode=json_mode, quiet=quiet)


@workflows_group.command("get", short_help="Get a specific workflow rule")
@click.argument("rule_id")
@click.option("--json", "json_mode", is_flag=True, help="JSON output")
@click.option("--quiet", is_flag=True, help="Suppress non-data output")
@click.pass_context
def wf_get(ctx, rule_id, json_mode, quiet):
    """Get details of a specific workflow rule by ID."""
    client = _client(ctx)
    result = client.get_workflow(rule_id)
    render(result, json_mode=json_mode, quiet=quiet)


@workflows_group.command("update", short_help="Update a workflow rule")
@click.argument("rule_id")
@click.option("--data", required=True, help="JSON string of workflow data")
@click.option("--dry-run", is_flag=True, help="Show request without executing")
@click.option("--json", "json_mode", is_flag=True, help="JSON output")
@click.option("--quiet", is_flag=True, help="Suppress non-data output")
@click.pass_context
def wf_update(ctx, rule_id, data, dry_run, json_mode, quiet):
    """Update a workflow rule by ID."""
    try:
        parsed = json.loads(data)
    except json.JSONDecodeError as e:
        error_out(f"Invalid JSON: {e}")
        return
    if dry_run:
        dry_run_output("PUT", f"{config.get_crm_base()}/settings/workflow_rules/{rule_id}", parsed)
        return
    client = _client(ctx)
    result = client.update_workflow(rule_id, parsed)
    render(result, json_mode=json_mode, quiet=quiet)


@workflows_group.command("delete", short_help="Delete a workflow rule")
@click.argument("rule_id")
@click.option("--dry-run", is_flag=True, help="Show request without executing")
@click.option("--json", "json_mode", is_flag=True, help="JSON output")
@click.option("--quiet", is_flag=True, help="Suppress non-data output")
@click.pass_context
def wf_delete(ctx, rule_id, dry_run, json_mode, quiet):
    """Delete a workflow rule by ID."""
    if dry_run:
        dry_run_output("DELETE", f"{config.get_crm_base()}/settings/workflow_rules/{rule_id}")
        return
    client = _client(ctx)
    result = client.delete_workflow(rule_id)
    render(result, json_mode=json_mode, quiet=quiet)


@workflows_group.command("reorder", short_help="Reorder workflow rules")
@click.argument("module")
@click.option("--ids", required=True, help="Comma-separated rule IDs in desired order")
@click.option("--dry-run", is_flag=True, help="Show request without executing")
@click.option("--json", "json_mode", is_flag=True, help="JSON output")
@click.option("--quiet", is_flag=True, help="Suppress non-data output")
@click.pass_context
def wf_reorder(ctx, module, ids, dry_run, json_mode, quiet):
    """Reorder workflow rules for a module."""
    rule_ids = [i.strip() for i in ids.split(",") if i.strip()]
    if not rule_ids:
        error_out("--ids must contain at least one rule ID")
        return
    if dry_run:
        dry_run_output("PUT", f"{config.get_crm_base()}/settings/workflow_rules/actions/reorder", {"rule_ids": rule_ids})
        return
    client = _client(ctx)
    result = client.reorder_workflows(module, rule_ids)
    render(result, json_mode=json_mode, quiet=quiet)


@workflows_group.command("usage", short_help="Workflow usage report")
@click.option("--json", "json_mode", is_flag=True, help="JSON output")
@click.option("--quiet", is_flag=True, help="Suppress non-data output")
@click.pass_context
def wf_usage(ctx, json_mode, quiet):
    """Get workflow usage report across all modules."""
    client = _client(ctx)
    result = client.workflow_usage_report()
    render(result, json_mode=json_mode, quiet=quiet)


@workflows_group.command("limits", short_help="Workflow limits")
@click.option("--json", "json_mode", is_flag=True, help="JSON output")
@click.option("--quiet", is_flag=True, help="Suppress non-data output")
@click.pass_context
def wf_limits(ctx, json_mode, quiet):
    """Get workflow limits for the org."""
    client = _client(ctx)
    result = client.workflow_limits()
    render(result, json_mode=json_mode, quiet=quiet)


@workflows_group.command("actions-count", short_help="Get actions count for a rule")
@click.argument("rule_id")
@click.option("--json", "json_mode", is_flag=True, help="JSON output")
@click.option("--quiet", is_flag=True, help="Suppress non-data output")
@click.pass_context
def wf_actions_count(ctx, rule_id, json_mode, quiet):
    """Get the actions count for a workflow rule."""
    client = _client(ctx)
    result = client.workflow_actions_count(rule_id)
    render(result, json_mode=json_mode, quiet=quiet)


# --- Blueprint ---

@click.group("blueprint", short_help="Blueprint/process management")
@click.pass_context
def blueprint_group(ctx):
    """CRM blueprint: get transitions, advance records through processes."""
    pass


@blueprint_group.command("get", short_help="Get blueprint for a record")
@click.argument("module")
@click.argument("record_id")
@click.option("--json", "json_mode", is_flag=True, help="JSON output")
@click.option("--quiet", is_flag=True, help="Suppress non-data output")
@click.pass_context
def bp_get(ctx, module, record_id, json_mode, quiet):
    """Get available blueprint transitions for a record."""
    client = _client(ctx)
    result = client.get_blueprint(module, record_id)
    render(result, json_mode=json_mode, quiet=quiet)


@blueprint_group.command("advance", short_help="Advance a record through a transition")
@click.argument("module")
@click.argument("record_id")
@click.option("--transition-id", required=True, help="Blueprint transition ID")
@click.option("--data", required=True, help="JSON string of transition field data")
@click.option("--dry-run", is_flag=True, help="Show request without executing")
@click.option("--json", "json_mode", is_flag=True, help="JSON output")
@click.option("--quiet", is_flag=True, help="Suppress non-data output")
@click.pass_context
def bp_advance(ctx, module, record_id, transition_id, data, dry_run, json_mode, quiet):
    """Advance a record through a blueprint transition."""
    try:
        parsed = json.loads(data)
    except json.JSONDecodeError as e:
        error_out(f"Invalid JSON: {e}")
        return
    if dry_run:
        dry_run_output("PUT", f"{config.get_crm_base()}/{module}/{record_id}/actions/blueprint", parsed)
        return
    client = _client(ctx)
    result = client.update_blueprint(module, record_id, transition_id, parsed)
    render(result, json_mode=json_mode, quiet=quiet)


# --- Scoring Rules ---

@click.group("scoring", short_help="Scoring rules management")
@click.pass_context
def scoring_group(ctx):
    """CRM scoring rules: list, create, update, delete, execute."""
    pass


@scoring_group.command("list", short_help="List scoring rules")
@click.option("--module", default=None, help="Filter by module")
@click.option("--json", "json_mode", is_flag=True, help="JSON output")
@click.option("--quiet", is_flag=True, help="Suppress non-data output")
@click.pass_context
def scoring_list(ctx, module, json_mode, quiet):
    """List all scoring rules."""
    client = _client(ctx)
    result = client.get_scoring_rules(module=module)
    render(result, json_mode=json_mode, quiet=quiet)


@scoring_group.command("create", short_help="Create a scoring rule")
@click.option("--data", required=True, help="JSON string of scoring rule data")
@click.option("--dry-run", is_flag=True, help="Show request without executing")
@click.option("--json", "json_mode", is_flag=True, help="JSON output")
@click.option("--quiet", is_flag=True, help="Suppress non-data output")
@click.pass_context
def scoring_create(ctx, data, dry_run, json_mode, quiet):
    """Create a new scoring rule."""
    try:
        parsed = json.loads(data)
    except json.JSONDecodeError as e:
        error_out(f"Invalid JSON: {e}")
        return
    if dry_run:
        dry_run_output("POST", f"{config.get_crm_base()}/settings/scoring_rules", parsed)
        return
    client = _client(ctx)
    result = client.create_scoring_rule(parsed)
    render(result, json_mode=json_mode, quiet=quiet)


@scoring_group.command("update", short_help="Update a scoring rule")
@click.argument("rule_id")
@click.option("--data", required=True, help="JSON string of updated data")
@click.option("--dry-run", is_flag=True, help="Show request without executing")
@click.option("--json", "json_mode", is_flag=True, help="JSON output")
@click.option("--quiet", is_flag=True, help="Suppress non-data output")
@click.pass_context
def scoring_update(ctx, rule_id, data, dry_run, json_mode, quiet):
    """Update a scoring rule by ID."""
    try:
        parsed = json.loads(data)
    except json.JSONDecodeError as e:
        error_out(f"Invalid JSON: {e}")
        return
    if dry_run:
        dry_run_output("PUT", f"{config.get_crm_base()}/settings/scoring_rules/{rule_id}", parsed)
        return
    client = _client(ctx)
    result = client.update_scoring_rule(rule_id, parsed)
    render(result, json_mode=json_mode, quiet=quiet)


@scoring_group.command("delete", short_help="Delete a scoring rule")
@click.argument("rule_id")
@click.option("--dry-run", is_flag=True, help="Show request without executing")
@click.option("--json", "json_mode", is_flag=True, help="JSON output")
@click.option("--quiet", is_flag=True, help="Suppress non-data output")
@click.pass_context
def scoring_delete(ctx, rule_id, dry_run, json_mode, quiet):
    """Delete a scoring rule by ID."""
    if dry_run:
        dry_run_output("DELETE", f"{config.get_crm_base()}/settings/scoring_rules/{rule_id}")
        return
    client = _client(ctx)
    result = client.delete_scoring_rule(rule_id)
    render(result, json_mode=json_mode, quiet=quiet)


@scoring_group.command("execute", short_help="Execute a scoring rule")
@click.argument("rule_id")
@click.argument("module")
@click.option("--dry-run", is_flag=True, help="Show request without executing")
@click.option("--json", "json_mode", is_flag=True, help="JSON output")
@click.option("--quiet", is_flag=True, help="Suppress non-data output")
@click.pass_context
def scoring_execute(ctx, rule_id, module, dry_run, json_mode, quiet):
    """Execute a scoring rule against a module."""
    if dry_run:
        dry_run_output("POST", f"{config.get_crm_base()}/settings/scoring_rules/{rule_id}/actions/execute")
        return
    client = _client(ctx)
    result = client.execute_scoring_rule(rule_id, module)
    render(result, json_mode=json_mode, quiet=quiet)


# --- Assignment Rules ---

@click.group("assignments", short_help="Assignment rules")
@click.pass_context
def assignments_group(ctx):
    """CRM assignment rules: list rules by module."""
    pass


@assignments_group.command("list", short_help="List assignment rules")
@click.option("--module", default=None, help="Filter by module")
@click.option("--json", "json_mode", is_flag=True, help="JSON output")
@click.option("--quiet", is_flag=True, help="Suppress non-data output")
@click.pass_context
def assignments_list(ctx, module, json_mode, quiet):
    """List all assignment rules."""
    client = _client(ctx)
    result = client.get_assignment_rules(module=module)
    render(result, json_mode=json_mode, quiet=quiet)
