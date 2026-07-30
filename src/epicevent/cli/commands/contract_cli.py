import click

from epicevent.bootstrap import Application
from epicevent.cli.decorators import handle_errors, require_auth, with_app
from epicevent.cli.views import contract_view
from epicevent.schemas.user_schema import UserResponse
from epicevent.security import authorization
from epicevent.security.permission import Permission


@click.group()
def contract():
    """contract commands."""
    pass


@contract.command()
@click.argument("client_email")
@with_app
@handle_errors
@require_auth
def create(app: Application, current_user: UserResponse, client_email: str):
    authorization.ensure_permission(current_user, Permission.CREATE_CONTRACT)
    target_client = app.client_controller.get_client_by_email(client_email)

    contract_view.display_contract_create_resume(target_client)
    data = contract_view.ask_contract_creation_data()
    contract = app.contract_controller.create_contract(current_user, client_email, data)
    contract_view.display_creation_success(contract)


@contract.command()
@click.argument("contract_id")
@with_app
@handle_errors
@require_auth
def update(app: Application, current_user: UserResponse, contract_id: str):
    authorization.ensure_permission(current_user, Permission.UPDATE_CONTRACT)
    target_contract = app.contract_controller.get_contract_for_update(
        current_user, contract_id
    )

    contract_view.display_contract_update_resume(target_contract)
    data = contract_view.ask_contract_update_data()
    if data:
        app.contract_controller.update_contract(current_user, contract_id, data)
        contract_view.dispaly_update_success(target_contract)
