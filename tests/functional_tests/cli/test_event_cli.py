from click.testing import CliRunner

from epicevent.cli.main import cli
from epicevent.models.event import Event
from epicevent.security.roles import UserRole
from tests.conftest import (
    create_persisted_client,
    create_persisted_contract,
    create_sales_client,
)


# create
######################
def test_create_event_success(logged_user_factory, session):
    runner = CliRunner()

    logged_user = logged_user_factory(role_id=UserRole.SALES)

    client = create_persisted_client(
        session,
        sales_representative_id=logged_user.id,
    )
    contract = create_persisted_contract(
        session,
        client_id=client.id,
        sales_representative_id=logged_user.id,
        is_signed=True,
    )

    result = runner.invoke(
        cli,
        ["event", "create", str(contract.id)],
        input=("01/08/2026 10:00\n01/08/2026 18:00\nParis\n150\nClient VIP\n"),
    )

    assert result.exit_code == 0

    created_event = session.query(Event).filter_by(contract_id=contract.id).one()

    assert f"L'évenement (id: {created_event.id}) a été enregistré." in result.output
    assert created_event.location == "Paris"
    assert created_event.attendees == 150
    assert created_event.notes == "Client VIP"
    assert created_event.contract_id == contract.id


def test_create_event_with_invalid_contract_displays_error(
    logged_user_factory,
    session,
):
    runner = CliRunner()

    logged_user_factory(role_id=UserRole.SALES)

    result = runner.invoke(
        cli,
        ["event", "create", "9999"],
    )

    assert result.exit_code == 0
    assert "Le contrat n'a pas été trouvé." in result.output
    assert session.query(Event).count() == 0


def test_create_event_with_unsigned_contract_displays_error(
    logged_user_factory,
    session,
):
    runner = CliRunner()

    logged_user = logged_user_factory(role_id=UserRole.SALES)

    client = create_persisted_client(
        session,
        sales_representative_id=logged_user.id,
    )
    contract = create_persisted_contract(
        session,
        client_id=client.id,
        sales_representative_id=logged_user.id,
        is_signed=False,
    )

    result = runner.invoke(
        cli,
        ["event", "create", str(contract.id)],
    )

    assert result.exit_code == 0
    assert "Le contrat n'a pas encore été signé." in result.output
    assert session.query(Event).count() == 0


def test_create_event_with_invalid_input_displays_error(
    logged_user_factory,
    session,
):
    runner = CliRunner()

    logged_user = logged_user_factory(role_id=UserRole.SALES)

    client = create_persisted_client(
        session,
        sales_representative_id=logged_user.id,
    )
    contract = create_persisted_contract(
        session,
        client_id=client.id,
        sales_representative_id=logged_user.id,
        is_signed=True,
    )

    result = runner.invoke(
        cli,
        ["event", "create", str(contract.id)],
        input=("01/08/2026 10:00\n01/08/2026 18:00\nParis\nabc\nClient VIP\n"),
    )

    assert result.exit_code == 0
    assert "Le nombre doit être un nombre entier" in result.output
    assert session.query(Event).count() == 0


def test_create_event_with_no_authorization_displays_error(
    logged_user_factory,
    session,
):
    runner = CliRunner()

    logged_user_factory(role_id=UserRole.SUPPORT)

    client = create_sales_client(session)
    contract = create_persisted_contract(
        session,
        client_id=client.id,
        sales_representative_id=client.sales_representative_id,
        is_signed=True,
    )

    result = runner.invoke(
        cli,
        ["event", "create", str(contract.id)],
    )

    assert result.exit_code == 0
    assert "Vous n'avez pas les droits pour cette action." in result.output
    assert session.query(Event).count() == 0
