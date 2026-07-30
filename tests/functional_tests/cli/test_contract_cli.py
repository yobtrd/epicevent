from click.testing import CliRunner

from epicevent.cli.main import cli
from epicevent.models.contract import Contract
from epicevent.security.roles import UserRole
from tests.conftest import create_sales_client


# create
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

    assert f"Le contrat (id: {created_contract.id}) a été enregistré." in result.output
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


def test_create_contract_with_invalid_input_displays_error(
    logged_user_factory, session
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
    assert "Le montant doit être un nombre entier." in result.output
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
