import click

from epicevent.bootstrap import Application
from epicevent.cli.decorators import handle_errors, require_auth, with_app
from epicevent.cli.pagination import handle_pagination
from epicevent.cli.views import contract_view
from epicevent.schemas.user_schema import UserResponse
from epicevent.security import authorization
from epicevent.security.permission import Permission


@click.group()
def contract() -> None:
    """Gestion des contrats."""
    pass


@contract.command("create")
@click.argument("client_email")
@with_app
@handle_errors
@require_auth
def create_contract(
    app: Application,
    current_user: UserResponse,
    client_email: str,
) -> None:
    """Créer un nouveau contrat à partir de l'email du client concerné."""
    authorization.ensure_permission(current_user, Permission.CREATE_CONTRACT)
    target_client = app.client_controller.get_client_by_email(client_email)

    contract_view.display_contract_create_resume(target_client)
    data = contract_view.ask_contract_creation_data()

    contract = app.contract_controller.create_contract(current_user, client_email, data)
    contract_view.display_contract_creation_success(contract)


@contract.command("update")
@click.argument("contract_id", type=int)
@with_app
@handle_errors
@require_auth
def update_contract(
    app: Application,
    current_user: UserResponse,
    contract_id: int,
) -> None:
    """Mettre à jour un contrat à partir de son identifiant."""
    authorization.ensure_permission(current_user, Permission.UPDATE_CONTRACT)
    target_contract = app.contract_controller.get_contract_by_id(contract_id)
    app.contract_controller.ensure_can_update_contract(current_user, target_contract)

    contract_view.display_contract_update_resume(target_contract)
    data = contract_view.ask_contract_update_data()
    if data:
        updated_contract = app.contract_controller.update_contract(
            current_user,
            contract_id,
            data,
        )
        contract_view.display_contract_update_success(updated_contract)
    else:
        contract_view.display_contract_update_cancel()


@contract.command("list")
@click.option(
    "--signed/--unsigned",
    help="Inclut seulement les contrats signés/non signés",
    default=None,
)
@click.option(
    "--paid/--unpaid",
    help="Inclut seulement les contrats payés/non payés",
    default=None,
)
@click.option(
    "--mine",
    help="Inclut seulement les contrats du commercial connecté",
    is_flag=True,
)
@with_app
@handle_errors
@require_auth
def list_contracts(
    app: Application,
    current_user: UserResponse,
    signed: bool | None,
    paid: bool | None,
    mine: bool,
) -> None:
    """Lister les contrats."""
    authorization.ensure_permission(current_user, Permission.LIST_CONTRACTS)

    offset = 0
    limit = 10
    while True:
        contracts_list, total_count = app.contract_controller.list_contracts(
            current_user,
            is_signed=signed,
            is_paid=paid,
            sales_assigned=mine,
            limit=limit,
            offset=offset,
        )
        if not contracts_list and offset == 0:
            contract_view.display_contract_list_empty_message()
            return

        contract_view.display_contracts_table(contracts_list, total_count)

        new_offset = handle_pagination(
            offset=offset,
            limit=limit,
            received_count=len(contracts_list),
            total_count=total_count,
        )
        if new_offset is None:
            break
        offset = new_offset


@contract.command("show")
@click.argument("contract_id", type=int)
@with_app
@handle_errors
@require_auth
def show_contract(
    app: Application,
    current_user: UserResponse,
    contract_id: int,
) -> None:
    """Afficher un contrat."""
    authorization.ensure_permission(current_user, Permission.SHOW_CONTRACT)

    contract = app.contract_controller.show_contract(current_user, contract_id)
    contract_view.display_contract_details(contract)
