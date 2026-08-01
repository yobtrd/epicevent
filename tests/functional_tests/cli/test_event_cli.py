from click.testing import CliRunner

from epicevent.cli.main import cli
from epicevent.models.event import Event
from epicevent.security.roles import UserRole
from tests.conftest import (
    create_contract_graph,
    create_persisted_client,
    create_persisted_contract,
    create_persisted_event,
    create_persisted_user,
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


# list
######################
def test_list_returns_event_table(
    logged_user_factory,
    session,
    force_console_width,
):
    runner = CliRunner()

    support_user = logged_user_factory(
        last_name="Doe",
        first_name="Jane",
        employee_number="002",
        role_id=UserRole.SUPPORT,
    )

    contract = create_contract_graph(
        session,
        sales_kwargs={
            "last_name": "Martin",
            "first_name": "Jean",
            "employee_number": "003",
            "email": "sales@test.com",
        },
        client_kwargs={
            "last_name": "Durand",
            "first_name": "Paul",
        },
    )

    for _ in range(3):
        create_persisted_event(
            session,
            contract_id=contract.id,
            support_representative_id=support_user.id,
        )

    result = runner.invoke(
        cli,
        ["event", "list"],
        input="q",
    )

    assert result.exit_code == 0
    assert "Liste des évènements (3 au total)" in result.output
    assert "Durand Paul" in result.output
    assert "Martin Jean (n°003)" in result.output
    assert "Paris" in result.output
    assert "150" in result.output


def test_list_with_no_event_displays_warning(logged_user_factory):
    runner = CliRunner()

    logged_user_factory(role_id=UserRole.SUPPORT)

    result = runner.invoke(
        cli,
        ["event", "list"],
    )

    assert result.exit_code == 0
    assert "Aucun événement trouvé" in result.output


def test_list_pagination(
    logged_user_factory,
    session,
    force_console_width,
):
    runner = CliRunner()

    support_user = logged_user_factory(role_id=UserRole.SUPPORT)

    contract = create_contract_graph(session)

    for _ in range(15):
        create_persisted_event(
            session,
            contract_id=contract.id,
            support_representative_id=support_user.id,
        )

    result = runner.invoke(
        cli,
        ["event", "list"],
        input="n\nq",
    )

    assert result.exit_code == 0
    assert "11" in result.output


def test_list_filters_assigned(
    logged_user_factory,
    session,
    force_console_width,
):
    runner = CliRunner()

    logged_user_factory(role_id=UserRole.MANAGEMENT)

    support_user = create_persisted_user(
        session,
        employee_number="400",
        email="support@email.com",
        role_id=UserRole.SUPPORT,
    )

    contract = create_contract_graph(session)

    create_persisted_event(
        session,
        contract_id=contract.id,
        support_representative_id=support_user.id,
    )
    create_persisted_event(
        session,
        contract_id=contract.id,
        support_representative_id=None,
    )

    result = runner.invoke(
        cli,
        ["event", "list", "--assigned"],
        input="q",
    )

    assert result.exit_code == 0
    assert "Liste des évènements (1 au total)" in result.output
    assert "Aucun support associé pour le moment." not in result.output


def test_list_filters_unassigned(
    logged_user_factory,
    session,
    force_console_width,
):
    runner = CliRunner()

    logged_user_factory(role_id=UserRole.MANAGEMENT)

    support_user = create_persisted_user(
        session,
        employee_number="400",
        email="support@email.com",
        role_id=UserRole.SUPPORT,
    )

    contract = create_contract_graph(session)

    create_persisted_event(
        session,
        contract_id=contract.id,
        support_representative_id=support_user.id,
    )
    create_persisted_event(
        session,
        contract_id=contract.id,
        support_representative_id=None,
    )

    result = runner.invoke(
        cli,
        ["event", "list", "--unassigned"],
        input="q",
    )

    assert result.exit_code == 0
    assert "Liste des évènements (1 au total)" in result.output
    assert "Aucun support associé pour le moment." in result.output
