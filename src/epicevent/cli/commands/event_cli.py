import click

from epicevent.bootstrap import Application
from epicevent.cli.decorators import handle_errors, require_auth, with_app
from epicevent.cli.pagination import handle_pagination
from epicevent.cli.views import event_view
from epicevent.schemas.user_schema import UserResponse
from epicevent.security import authorization
from epicevent.security.permission import Permission


@click.group()
def event():
    """event commands."""
    pass


@event.command()
@click.argument("contract_id")
@with_app
@handle_errors
@require_auth
def create(app: Application, current_user: UserResponse, contract_id=int):
    authorization.ensure_permission(current_user, Permission.CREATE_EVENT)
    target_contract = app.contract_controller.get_contract_by_id(contract_id)
    app.event_controller.ensure_can_create_event(current_user, target_contract)

    event_view.display_event_create_resume(target_contract)
    data = event_view.ask_event_creation_data()
    event = app.event_controller.create_event(current_user, contract_id, data)
    event_view.display_event_creation_success(event)


@event.command()
@click.argument("event_id")
@with_app
@handle_errors
@require_auth
def update(app: Application, current_user: UserResponse, event_id: str):
    authorization.ensure_permission(current_user, Permission.UPDATE_EVENT)
    target_event = app.event_controller.get_event_by_id(event_id)
    app.event_controller.ensure_can_update_event(current_user, target_event)

    event_view.display_event_update_resume(target_event)
    data = event_view.ask_event_update_data()
    if data:
        app.event_controller.update_event(current_user, event_id, data)
        event_view.dispaly_update_success(target_event)
    else:
        event_view.display_event_update_cancel()


@event.command()
@click.option("--assigned/--unassigned", default=None)
@with_app
@handle_errors
@require_auth
def list(
    app: Application,
    current_user: UserResponse,
    assigned: bool | None,
):
    authorization.ensure_permission(current_user, Permission.LIST_EVENT)

    offset = 0
    limit = 10
    while True:
        events_list, total_count = app.event_controller.list_events(
            current_user,
            is_assigned=assigned,
            limit=limit,
            offset=offset,
        )
        if not events_list and offset == 0:
            event_view.display_events_list_empty_message()
            return

        event_view.display_events_table(events_list, total_count)

        new_offset = handle_pagination(
            offset=offset,
            limit=limit,
            received_count=len(events_list),
            total_count=total_count,
        )
        if new_offset is None:
            break
        offset = new_offset


@event.command()
@click.argument("event_id")
@click.option("--support", help="Matricule du collaborateur support")
@with_app
@handle_errors
@require_auth
def assign(
    app: Application,
    current_user: UserResponse,
    event_id: int,
    support: str,
):
    authorization.ensure_permission(current_user, Permission.ASSIGN_SUPPORT)
    target_event = app.event_controller.get_event_by_id(event_id)
    target_support = app.user_controller.get_user_by_employee_number(
        employee_number=support
    )
    if event_view.ask_assign_support_confirmation(target_event, target_support):
        assigned_support, updated_event = app.event_controller.assign_support(
            current_user, event_id=event_id, employee_number=support
        )
        event_view.display_assign_support_success(assigned_support, updated_event)
    else:
        event_view.display_assign_support_cancel()
