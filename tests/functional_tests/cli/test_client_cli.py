from click.testing import CliRunner

from epicevent.cli.main import cli
from epicevent.models.client import Client
from epicevent.security.roles import UserRole
from tests.conftest import create_persisted_client, create_persisted_user


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


# update
######################
def test_update_client_by_sales_success(logged_user_factory, session):
    runner = CliRunner()
    current_user = logged_user_factory(role_id=UserRole.SALES)

    target_client = create_persisted_client(
        session,
        phone="010101010101",
        email="email@test.com",
        sales_representative_id=current_user.id,
    )

    result = runner.invoke(
        cli,
        ["client", "update", "email@test.com"],
        input=("4\n0909090909\nq"),
    )

    assert result.exit_code == 0
    session.refresh(target_client)
    assert target_client.phone == "0909090909"
    assert "Le client (email@test.com) a été mis à jour." in result.output


def test_update_duplicate_client_email_display_error(logged_user_factory, session):
    runner = CliRunner()
    current_user = logged_user_factory(role_id=UserRole.SALES)

    target_client = create_persisted_client(
        session,
        email="old@test.com",
        sales_representative_id=current_user.id,
    )
    create_persisted_client(
        session,
        email="existing@email.com",
        sales_representative_id=current_user.id,
    )

    result = runner.invoke(
        cli,
        ["client", "update", "old@test.com"],
        input=("3\nexisting@email.com\nq"),
    )

    assert result.exit_code == 0
    session.refresh(target_client)
    assert "Cet email existe déjà." in result.output


def test_update_client_sales_not_owned_client_displays_error(
    logged_user_factory, session
):
    runner = CliRunner()
    logged_user_factory(role_id=UserRole.SALES)
    owner_sales = create_persisted_user(session, role_id=UserRole.SALES)

    create_persisted_client(
        session,
        email="test@email.com",
        sales_representative_id=owner_sales.id,
    )

    result = runner.invoke(cli, ["client", "update", "test@email.com"])

    assert result.exit_code == 0
    assert "Vous n'avez pas la gestion de ce client." in result.output


def test_update_client_without_authorization_displays_error(
    logged_user_factory, session
):
    runner = CliRunner()
    logged_user_factory(role_id=UserRole.MANAGEMENT)
    sales = create_persisted_user(session, role_id=UserRole.SALES)

    create_persisted_client(
        session,
        email="test@email.com",
        sales_representative_id=sales.id,
    )

    result = runner.invoke(cli, ["client", "update", "test@email.com"])

    assert result.exit_code == 0
    assert "Vous n'avez pas les droits pour cette action." in result.output


def test_update_client_cancel_displays_cancel_message(
    logged_user_factory,
    session,
):
    runner = CliRunner()

    current_user = logged_user_factory(role_id=UserRole.SALES)

    client = create_persisted_client(
        session,
        email="client@test.com",
        sales_representative_id=current_user.id,
        first_name="John",
    )

    result = runner.invoke(
        cli,
        ["client", "update", client.email],
        input="q\n",
    )

    assert result.exit_code == 0

    session.refresh(client)

    assert client.first_name == "John"
    assert "La mise à jour du client a été annulée." in result.output


# list
######################
def test_list_returns_client_table(logged_user_factory, session, force_console_width):
    runner = CliRunner()
    sales_user = logged_user_factory(
        last_name="Doe", employee_number="002", role_id=UserRole.SALES
    )
    for i in range(3):
        create_persisted_client(
            session,
            email=f"client{i}@test.com",
            sales_representative_id=sales_user.id,
        )

    result = runner.invoke(
        cli,
        ["client", "list"],
        input=("q"),
    )
    assert result.exit_code == 0
    assert "Liste des clients (3 au total)" in result.output
    assert "Doe (n°002)" in result.output
    assert "client1@test.com" in result.output


def test_list_with_no_client_display_warning(logged_user_factory):
    runner = CliRunner()
    logged_user_factory(role_id=UserRole.SALES)

    result = runner.invoke(cli, ["client", "list"])
    assert result.exit_code == 0
    assert "Aucun client trouvé" in result.output


def test_list_pagination(logged_user_factory, session, force_console_width):
    runner = CliRunner()
    sales_user = logged_user_factory(role_id=UserRole.SALES)
    for i in range(15):
        create_persisted_client(
            session,
            email=f"client{i}@test.com",
            sales_representative_id=sales_user.id,
        )

    result = runner.invoke(cli, ["client", "list"], input="n\nq")

    assert result.exit_code == 0
    assert "client11@test.com" in result.output
