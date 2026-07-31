import click

from epicevent.bootstrap import Application
from epicevent.cli.decorators import handle_errors, require_auth, with_app
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
    app.event_controller.ensure_can_manage_event(current_user, target_contract)

    event_view.display_event_create_resume(target_contract)
    data = event_view.ask_event_creation_data()
    event = app.event_controller.create_event(current_user, contract_id, data)
    event_view.display_event_creation_success(event)
