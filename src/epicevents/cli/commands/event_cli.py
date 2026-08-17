import click

from epicevents.bootstrap import Application
from epicevents.cli.decorators import handle_errors, require_auth, with_app
from epicevents.cli.pagination import handle_pagination
from epicevents.cli.views import event_view
from epicevents.schemas.user_schema import UserResponse
from epicevents.security import authorization
from epicevents.security.permission import Permission


@click.group()
def event() -> None:
    """Gestion des événements."""
    pass


@event.command("create")
@click.argument("contract_id", type=int)
@with_app
@handle_errors
@require_auth
def create_event(
    app: Application,
    current_user: UserResponse,
    contract_id: int,
) -> None:
    """Créer un nouvel événement à partir de l'ID du contrat concerné."""
    authorization.ensure_permission(current_user, Permission.CREATE_EVENT)
    target_contract = app.contract_controller.get_contract_by_id(contract_id)
    app.event_controller.ensure_can_create_event(current_user, target_contract)

    event_view.display_event_create_resume(target_contract)
    data = event_view.ask_event_creation_data()

    event = app.event_controller.create_event(current_user, contract_id, data)
    event_view.display_event_creation_success(event)


@event.command("update")
@click.argument("event_id", type=int)
@with_app
@handle_errors
@require_auth
def update_event(
    app: Application,
    current_user: UserResponse,
    event_id: int,
) -> None:
    """Mettre à jour un événement à partir de son identifiant."""
    authorization.ensure_permission(current_user, Permission.UPDATE_EVENT)
    target_event = app.event_controller.get_event_by_id(event_id)
    app.event_controller.ensure_can_update_event(current_user, target_event)

    event_view.display_event_update_resume(target_event)
    data = event_view.ask_event_update_data()
    if data:
        updated_event = app.event_controller.update_event(current_user, event_id, data)
        event_view.display_event_update_success(updated_event)
    else:
        event_view.display_event_update_cancel()


@event.command("list")
@click.option(
    "--upcoming",
    help="Inclut seulement les événements futurs",
    is_flag=True,
)
@click.option(
    "--assigned/--unassigned",
    help="Filtre les événements avec ou sans support assigné.",
    default=None,
)
@click.option(
    "--mine",
    help="Inclut seulement les événements du support connecté",
    is_flag=True,
)
@with_app
@handle_errors
@require_auth
def list_events(
    app: Application,
    current_user: UserResponse,
    upcoming: bool,
    assigned: bool | None,
    mine: bool,
) -> None:
    """Lister les événements."""
    authorization.ensure_permission(current_user, Permission.LIST_EVENTS)

    offset = 0
    limit = 10
    while True:
        events_list, total_count = app.event_controller.list_events(
            current_user,
            upcoming=upcoming,
            is_assigned=assigned,
            support_assigned=mine,
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


@event.command("show")
@click.argument("event_id", type=int)
@with_app
@handle_errors
@require_auth
def show_event(
    app: Application,
    current_user: UserResponse,
    event_id: int,
) -> None:
    """Afficher un événement."""
    authorization.ensure_permission(current_user, Permission.SHOW_EVENT)

    event = app.event_controller.show_event(current_user, event_id)
    event_view.display_event_details(event)


@event.command("assign")
@click.argument("event_id", type=int)
@click.option(
    "--support",
    metavar="MATRICULE",
    help="Matricule du collaborateur support",
)
@with_app
@handle_errors
@require_auth
def assign_support(
    app: Application,
    current_user: UserResponse,
    event_id: int,
    support: str,
) -> None:
    """Assigner un collaborateur support à un événement."""
    authorization.ensure_permission(current_user, Permission.ASSIGN_SUPPORT)
    target_event = app.event_controller.get_event_by_id(event_id)
    target_support = app.user_controller.get_user_by_employee_number(
        employee_number=support
    )

    if event_view.ask_assign_support_confirmation(target_event, target_support):
        assigned_support, updated_event = app.event_controller.assign_support(
            current_user,
            event_id=event_id,
            employee_number=support,
        )
        event_view.display_assign_support_success(assigned_support, updated_event)
    else:
        event_view.display_assign_support_cancel()


@event.command("unassign")
@click.argument("event_id", type=int)
@with_app
@handle_errors
@require_auth
def unassign_support(
    app: Application,
    current_user: UserResponse,
    event_id: int,
) -> None:
    """Désassigner le collaborateur support d'un événement."""
    authorization.ensure_permission(current_user, Permission.ASSIGN_SUPPORT)
    target_event = app.event_controller.get_detailed_event_by_id(event_id)

    if event_view.ask_unassign_support_confirmation(target_event):
        updated_event = app.event_controller.unassign_support(
            current_user,
            event_id=event_id,
        )
        event_view.display_unassign_support_success(updated_event)
    else:
        event_view.display_unassign_support_cancel()
