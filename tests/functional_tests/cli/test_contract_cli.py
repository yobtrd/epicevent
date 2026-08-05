from decimal import Decimal

from click.testing import CliRunner

from epicevent.cli.main import cli
from epicevent.models.contract import Contract
from epicevent.security.roles import UserRole
from tests.conftest import (
    create_persisted_client,
    create_persisted_contract,
    create_persisted_user,
    create_sales_client,
)


# create_contract
######################
def test_create_contract_success(logged_user_factory, session):
    runner = CliRunner()

    logged_user_factory(role_id=UserRole.MANAGEMENT)

    client = create_sales_client(session)

    result = runner.invoke(
        cli,
        ["contract", "create", client.email],
        input="1000\n1000\nn\n",
    )

    assert result.exit_code == 0

    created_contract = session.query(Contract).filter_by(client_id=client.id).one()

    assert f"Le contrat n°{created_contract.id} a été enregistré." in result.output
    assert created_contract.total_amount == 1000
    assert created_contract.remaining_amount == 1000
    assert created_contract.is_signed is False
    assert created_contract.client_id == client.id
    assert created_contract.sales_representative_id == client.sales_representative_id


def test_create_contract_with_invalid_client_email_displays_error(
    logged_user_factory, session
):
    runner = CliRunner()

    logged_user_factory(role_id=UserRole.MANAGEMENT)

    result = runner.invoke(
        cli,
        ["contract", "create", "inexistant@email"],
    )

    assert result.exit_code == 0
    assert "Le client n'a pas été trouvé." in result.output


def test_create_contract_with_invalid_amount_input_displays_error(
    logged_user_factory, session, force_console_width
):
    runner = CliRunner()

    logged_user_factory(role_id=UserRole.MANAGEMENT)

    client = create_sales_client(session)

    result = runner.invoke(
        cli,
        ["contract", "create", client.email],
        input="1000\nddddd\nn\n",
    )

    assert result.exit_code == 0
    assert "Format invalide" in result.output
    assert "le montant doit être un nombre entier ou décimal" in result.output
    assert session.query(Contract).count() == 0


def test_create_contract_with_invalid_amounts_displays_error(
    logged_user_factory, session, force_console_width
):
    runner = CliRunner()

    logged_user_factory(role_id=UserRole.MANAGEMENT)

    client = create_sales_client(session)

    result = runner.invoke(
        cli,
        ["contract", "create", client.email],
        input="1000\n50000\nn\n",
    )

    assert result.exit_code == 0
    assert (
        "Le montant restant ne peut être inférieure au montant total." in result.output
    )
    assert session.query(Contract).count() == 0


def test_create_contract_with_no_authorization_displays_error(
    logged_user_factory, session
):
    runner = CliRunner()

    logged_user_factory(role_id=UserRole.SALES)

    client = create_sales_client(session)

    result = runner.invoke(
        cli,
        ["contract", "create", client.email],
    )

    assert result.exit_code == 0
    assert "Vous n'avez pas les droits pour cette action." in result.output
    assert session.query(Contract).count() == 0


# update_contract
######################
def test_update_contract_by_sales_success(logged_user_factory, session):
    runner = CliRunner()

    current_user = logged_user_factory(role_id=UserRole.SALES)

    client = create_persisted_client(
        session,
        email="client@test.com",
        sales_representative_id=current_user.id,
    )

    contract = create_persisted_contract(
        session,
        client_id=client.id,
        sales_representative_id=current_user.id,
        remaining_amount=500,
    )

    result = runner.invoke(
        cli,
        ["contract", "update", str(contract.id)],
        input=("2\n100\nq"),
    )

    assert result.exit_code == 0
    session.refresh(contract)
    assert contract.remaining_amount == 100
    assert f"Le contrat n°{contract.id} a été mis à jour." in result.output


def test_update_contract_not_found_display_error(logged_user_factory):
    runner = CliRunner()

    logged_user_factory(role_id=UserRole.SALES)

    result = runner.invoke(
        cli,
        ["contract", "update", "999"],
    )

    assert result.exit_code == 0
    assert "Le contrat n'a pas été trouvé." in result.output


def test_update_contract_sales_not_owned_contract_displays_error(
    logged_user_factory,
    session,
):
    runner = CliRunner()

    logged_user_factory(role_id=UserRole.SALES)

    other_sales = create_persisted_user(
        session,
        employee_number="002",
        role_id=UserRole.SALES,
    )

    client = create_persisted_client(
        session,
        email="client@test.com",
        sales_representative_id=other_sales.id,
    )

    contract = create_persisted_contract(
        session,
        client_id=client.id,
        sales_representative_id=other_sales.id,
    )

    result = runner.invoke(
        cli,
        ["contract", "update", str(contract.id)],
    )

    assert result.exit_code == 0
    assert "Vous n'avez pas la gestion de ce client." in result.output


def test_update_contract_without_authorization_displays_error(
    logged_user_factory,
    session,
):
    runner = CliRunner()

    logged_user_factory(role_id=UserRole.SUPPORT)

    sales = create_persisted_user(
        session,
        role_id=UserRole.SALES,
    )

    client = create_persisted_client(
        session,
        sales_representative_id=sales.id,
    )

    contract = create_persisted_contract(
        session,
        client_id=client.id,
        sales_representative_id=sales.id,
    )

    result = runner.invoke(
        cli,
        ["contract", "update", str(contract.id)],
    )

    assert result.exit_code == 0
    assert "Vous n'avez pas les droits pour cette action." in result.output


def test_update_contract_by_management_success(logged_user_factory, session):
    runner = CliRunner()
    logged_user_factory(role_id=UserRole.MANAGEMENT)
    sales = create_persisted_user(session, role_id=UserRole.SALES)

    client = create_persisted_client(
        session,
        email="client@test.com",
        sales_representative_id=sales.id,
    )

    contract = create_persisted_contract(
        session,
        client_id=client.id,
        sales_representative_id=sales.id,
        is_signed=False,
    )

    result = runner.invoke(
        cli,
        ["contract", "update", str(contract.id)],
        input=("3\ny\nq"),
    )

    assert result.exit_code == 0
    session.refresh(contract)
    assert contract.is_signed is True


def test_update_contract_cancel_displays_cancel_message(
    logged_user_factory,
    session,
):
    runner = CliRunner()

    current_user = logged_user_factory(role_id=UserRole.SALES)

    client = create_persisted_client(
        session,
        email="client@test.com",
        sales_representative_id=current_user.id,
    )

    contract = create_persisted_contract(
        session,
        client_id=client.id,
        sales_representative_id=current_user.id,
        remaining_amount=500,
    )

    result = runner.invoke(
        cli,
        ["contract", "update", str(contract.id)],
        input="q\n",
    )

    assert result.exit_code == 0

    session.refresh(contract)

    assert contract.remaining_amount == 500
    assert "La mise à jour du contrat a été annulée." in result.output


# list_contracts
######################
def test_list_returns_contract_table(
    logged_user_factory,
    session,
    force_console_width,
):
    runner = CliRunner()

    sales_user = logged_user_factory(
        last_name="Doe",
        first_name="Jane",
        employee_number="002",
        role_id=UserRole.SALES,
    )

    client = create_persisted_client(
        session,
        last_name="Martin",
        first_name="Jean",
        sales_representative_id=sales_user.id,
    )

    for _ in range(3):
        create_persisted_contract(
            session,
            client_id=client.id,
            sales_representative_id=sales_user.id,
        )

    result = runner.invoke(
        cli,
        ["contract", "list"],
        input="q",
    )

    assert result.exit_code == 0
    assert "Liste des contrats (3 au total)" in result.output
    assert "Martin Jean" in result.output
    assert "Doe Jane (n°002)" in result.output
    assert "1000.00" in result.output


def test_list_with_no_contract_displays_warning(logged_user_factory):
    runner = CliRunner()

    logged_user_factory(role_id=UserRole.SALES)

    result = runner.invoke(
        cli,
        ["contract", "list"],
    )

    assert result.exit_code == 0
    assert "Aucun contrat trouvé" in result.output


def test_list_pagination(
    logged_user_factory,
    session,
    force_console_width,
):
    runner = CliRunner()

    sales_user = logged_user_factory(role_id=UserRole.SALES)

    client = create_persisted_client(
        session,
        sales_representative_id=sales_user.id,
    )

    for _ in range(15):
        create_persisted_contract(
            session,
            client_id=client.id,
            sales_representative_id=sales_user.id,
        )

    result = runner.invoke(
        cli,
        ["contract", "list"],
        input="n\nq",
    )

    assert result.exit_code == 0
    assert "11" in result.output


def test_list_filters_signed(
    logged_user_factory,
    session,
    force_console_width,
):
    runner = CliRunner()

    sales_user = logged_user_factory(role_id=UserRole.SALES)

    client = create_persisted_client(
        session,
        sales_representative_id=sales_user.id,
    )

    create_persisted_contract(
        session,
        client_id=client.id,
        sales_representative_id=sales_user.id,
        is_signed=True,
    )
    create_persisted_contract(
        session,
        client_id=client.id,
        sales_representative_id=sales_user.id,
        is_signed=False,
    )

    result = runner.invoke(
        cli,
        ["contract", "list", "--signed"],
        input="q",
    )

    assert result.exit_code == 0
    assert "Liste des contrats (1 au total)" in result.output
    assert "Signé" in result.output
    assert "Non signé" not in result.output


def test_list_filters_paid(
    logged_user_factory,
    session,
    force_console_width,
):
    runner = CliRunner()

    sales_user = logged_user_factory(role_id=UserRole.SALES)

    client = create_persisted_client(
        session,
        sales_representative_id=sales_user.id,
    )

    create_persisted_contract(
        session,
        client_id=client.id,
        sales_representative_id=sales_user.id,
        remaining_amount=Decimal("0.00"),
    )
    create_persisted_contract(
        session,
        client_id=client.id,
        sales_representative_id=sales_user.id,
        remaining_amount=Decimal("500.00"),
    )

    result = runner.invoke(
        cli,
        ["contract", "list", "--paid"],
        input="q",
    )

    assert result.exit_code == 0
    assert "Liste des contrats (1 au total)" in result.output
    assert "0.00" in result.output
    assert "500.00" not in result.output


def test_list_filters_mine(
    logged_user_factory,
    session,
    force_console_width,
):
    runner = CliRunner()

    current_sales_user = logged_user_factory(
        employee_number="001",
        email="sales1@email.com",
        role_id=UserRole.SALES,
    )
    other_sales_user = create_persisted_user(
        session,
        employee_number="002",
        email="sales2@email.com",
        role_id=UserRole.SALES,
    )

    client = create_persisted_client(
        session,
        sales_representative_id=current_sales_user.id,
    )

    create_persisted_contract(
        session,
        client_id=client.id,
        sales_representative_id=current_sales_user.id,
        is_signed=True,
    )
    create_persisted_contract(
        session,
        client_id=client.id,
        sales_representative_id=current_sales_user.id,
        is_signed=True,
    )

    create_persisted_contract(
        session,
        client_id=client.id,
        sales_representative_id=other_sales_user.id,
        is_signed=False,
    )

    result = runner.invoke(
        cli,
        ["contract", "list", "--mine"],
        input="q",
    )

    assert result.exit_code == 0
    assert "Liste des contrats (2 au total)" in result.output
    assert "Signé" in result.output
    assert "Non signé" not in result.output
