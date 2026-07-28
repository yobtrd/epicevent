from click.testing import CliRunner

from epicevent.cli.main import cli
from epicevent.models.client import Client
from epicevent.security.roles import UserRole
from tests.conftest import create_persisted_client


# create
######################
def test_create_client_success(logged_user_factory, session):
    runner = CliRunner()
    current_user = logged_user_factory(role_id=UserRole.SALES)
    client_mail = "jon.doe@entreprise.com"

    result = runner.invoke(
        cli,
        ["client", "create"],
        input=(f"Doe\nJohn\n{client_mail}\n0123456789\nDoe&Co\n10/10/2010\n20/10/2010"),
    )

    assert result.exit_code == 0
    assert f"Le client (email: {client_mail}) a été enregistré." in result.output
    created_client = session.query(Client).filter_by(email=client_mail).first()
    assert created_client is not None
    assert created_client.last_name == "Doe"
    assert created_client.sales_representative_id == current_user.id


def test_create_client_duplicate_email_displays_error(logged_user_factory, session):
    runner = CliRunner()
    current_user = logged_user_factory(role_id=UserRole.SALES)
    create_persisted_client(
        session, email="same@email.com", sales_representative_id=current_user.id
    )

    result = runner.invoke(
        cli,
        ["client", "create"],
        input=("Doe\nJohn\nsame@email.com\n0123456789\nDoe&Co\n10/10/2010\n20/10/2010"),
    )

    assert result.exit_code == 0
    assert "Cet email existe déjà." in result.output


def test_create_client_with_invalid_input_displays_error(logged_user_factory):
    runner = CliRunner()
    logged_user_factory(role_id=UserRole.SALES)

    result = runner.invoke(
        cli,
        ["client", "create"],
        input=(
            "Doe\nJohn\njon.doe@entreprise.com\n0123456789\nDoe&Co\n10102010\n20/10/2010"
        ),
    )

    assert result.exit_code == 1
    assert "Format invalide. Veuillez utiliser JJ/MM/AAAA" in result.output


def test_create_client_with_no_authorization_displays_error(logged_user_factory):
    runner = CliRunner()
    logged_user_factory(role_id=UserRole.MANAGEMENT)

    result = runner.invoke(cli, ["client", "create"])

    assert result.exit_code == 0
    assert "Vous n'avez pas les droits pour cette action." in result.output
