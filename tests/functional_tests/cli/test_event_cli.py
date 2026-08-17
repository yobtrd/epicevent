from datetime import datetime, timedelta

from click.testing import CliRunner

from epicevents.cli.main import cli
from epicevents.models.event import Event
from epicevents.security.roles import UserRole
from tests.conftest import (
    create_contract_graph,
    create_persisted_client,
    create_persisted_contract,
    create_persisted_event,
    create_persisted_user,
    create_sales_client,
)


# create_event
######################
def test_create_event_success(logged_user_factory, session, force_console_width):
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
        input=("événement\n01/08/2026 10:00\n01/08/2026 18:00\nParis\n150\nNote\n"),
    )

    assert result.exit_code == 0
    created_event = session.query(Event).filter_by(contract_id=contract.id).one()

    assert (
        f'L\'événement "{created_event.name}" (n°{created_event.id}) a été enregistré.'
        in result.output
    )
    assert created_event.name == "événement"
    assert created_event.location == "Paris"
    assert created_event.attendees == 150
    assert created_event.notes == "Note"
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


def test_create_event_with_invalid_attendees_input_displays_error(
    logged_user_factory, session, force_console_width
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
        input=("événement\n01/08/2026 10:00\n01/08/2026 18:00\nParis\nabc\nnotes\n"),
    )

    assert result.exit_code == 0
    assert "le nombre doit être un nombre entier sans espaces" in result.output
    assert session.query(Event).count() == 0


def test_create_event_with_invalid_dates_displays_error(
    logged_user_factory, session, force_console_width
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
        input=("événement\n01/08/2026 10:00\n01/08/1990 18:00\nParis\n1000\nnotes\n"),
    )

    assert result.exit_code == 0
    assert (
        "La date de fin de l'événement ne peut être antérieure à sa date de début"
        in result.output
    )
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


# update_event
######################
def test_update_event_by_support_success(logged_user_factory, session):
    runner = CliRunner()

    current_user = logged_user_factory(role_id=UserRole.SUPPORT)

    sales = create_persisted_user(
        session,
        employee_number="002",
        email="sales@test.com",
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

    event = create_persisted_event(
        session,
        contract_id=contract.id,
        support_representative_id=current_user.id,
        attendees=150,
    )

    result = runner.invoke(
        cli,
        ["event", "update", str(event.id)],
        input=("5\n100\nq"),
    )

    assert result.exit_code == 0

    session.refresh(event)

    assert event.attendees == 100
    assert (
        f'L\'événement "{event.name}" (n°{event.id}) a bien été mis à jour.'
        in result.output
    )


def test_update_event_not_found_display_error(logged_user_factory):
    runner = CliRunner()

    logged_user_factory(role_id=UserRole.SUPPORT)

    result = runner.invoke(
        cli,
        ["event", "update", "999"],
    )

    assert result.exit_code == 0
    assert "L'événement n'a pas été trouvé." in result.output


def test_update_event_support_not_owned_event_displays_error(
    logged_user_factory,
    session,
):
    runner = CliRunner()

    logged_user_factory(role_id=UserRole.SUPPORT)

    other_support = create_persisted_user(
        session,
        employee_number="002",
        email="support@test.com",
        role_id=UserRole.SUPPORT,
    )

    sales = create_persisted_user(
        session,
        employee_number="003",
        email="sales@test.com",
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

    event = create_persisted_event(
        session,
        contract_id=contract.id,
        support_representative_id=other_support.id,
    )

    result = runner.invoke(
        cli,
        ["event", "update", str(event.id)],
    )

    assert result.exit_code == 0
    assert "Vous n'avez pas la gestion de cet événement." in result.output


def test_update_event_without_authorization_displays_error(
    logged_user_factory,
    session,
):
    runner = CliRunner()

    logged_user_factory(role_id=UserRole.SALES)

    sales = create_persisted_user(
        session,
        employee_number="002",
        email="sales@test.com",
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

    event = create_persisted_event(
        session,
        contract_id=contract.id,
    )

    result = runner.invoke(
        cli,
        ["event", "update", str(event.id)],
    )

    assert result.exit_code == 0
    assert "Vous n'avez pas les droits pour cette action." in result.output


def test_update_event_by_management_success(logged_user_factory, session):
    runner = CliRunner()

    logged_user_factory(role_id=UserRole.MANAGEMENT)

    sales = create_persisted_user(
        session,
        employee_number="002",
        email="sales@test.com",
        role_id=UserRole.SALES,
    )

    support = create_persisted_user(
        session,
        employee_number="003",
        email="support@test.com",
        role_id=UserRole.SUPPORT,
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

    event = create_persisted_event(
        session,
        contract_id=contract.id,
        support_representative_id=support.id,
        notes="Anciennes notes",
    )

    result = runner.invoke(
        cli,
        ["event", "update", str(event.id)],
        input=("6\nNouvelles notes\nq"),
    )

    assert result.exit_code == 0

    session.refresh(event)

    assert event.notes == "Nouvelles notes"


def test_update_event_cancel_displays_cancel_message(
    logged_user_factory,
    session,
):
    runner = CliRunner()

    current_user = logged_user_factory(role_id=UserRole.SUPPORT)

    sales = create_persisted_user(
        session,
        employee_number="002",
        email="sales@test.com",
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

    event = create_persisted_event(
        session,
        contract_id=contract.id,
        support_representative_id=current_user.id,
        notes="Notes initiales",
    )

    result = runner.invoke(
        cli,
        ["event", "update", str(event.id)],
        input="q\n",
    )

    assert result.exit_code == 0

    session.refresh(event)

    assert event.notes == "Notes initiales"
    assert "La mise à jour de l'événement a été annulée." in result.output


# list_events
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
    assert "Liste des événements (3 au total)" in result.output
    assert "Durand Paul" in result.output
    assert "Paris" in result.output


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
    assert "Liste des événements (1 au total)" in result.output
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
    assert "Liste des événements (1 au total)" in result.output
    assert "Non assigné" in result.output


def test_list_filters_mine(
    logged_user_factory,
    session,
    force_console_width,
):
    runner = CliRunner()

    current_support_user = logged_user_factory(
        employee_number="101",
        email="support1@email.com",
        role_id=UserRole.SUPPORT,
    )
    other_support_user = create_persisted_user(
        session,
        employee_number="102",
        email="support2@email.com",
        role_id=UserRole.SUPPORT,
    )

    contract = create_contract_graph(session)

    create_persisted_event(
        session,
        contract_id=contract.id,
        support_representative_id=current_support_user.id,
    )
    create_persisted_event(
        session,
        contract_id=contract.id,
        support_representative_id=current_support_user.id,
    )

    create_persisted_event(
        session,
        contract_id=contract.id,
        support_representative_id=other_support_user.id,
    )

    result = runner.invoke(
        cli,
        ["event", "list", "--mine"],
        input="q",
    )

    assert result.exit_code == 0
    assert "Liste des événements (2 au total)" in result.output


def test_list_filters_upcoming(
    logged_user_factory,
    session,
    force_console_width,
):
    runner = CliRunner()
    support_user = logged_user_factory(role_id=UserRole.SUPPORT)
    contract = create_contract_graph(session)

    create_persisted_event(
        session,
        contract_id=contract.id,
        support_representative_id=support_user.id,
        start=datetime.now() - timedelta(days=5),
        end=datetime.now() - timedelta(days=1),
    )

    create_persisted_event(
        session,
        contract_id=contract.id,
        support_representative_id=support_user.id,
        start=datetime.now() - timedelta(days=1),
        end=datetime.now() + timedelta(days=1),
    )

    create_persisted_event(
        session,
        contract_id=contract.id,
        support_representative_id=support_user.id,
        start=datetime.now() + timedelta(days=1),
        end=datetime.now() + timedelta(days=2),
    )

    result = runner.invoke(
        cli,
        ["event", "list", "--upcoming"],
        input="q",
    )

    assert result.exit_code == 0
    assert "Liste des événements (2 au total)" in result.output


# show_event
######################
def test_show_event_returns_event_sheet(
    logged_user_factory,
    session,
):
    runner = CliRunner()

    current_user = logged_user_factory(
        employee_number="400",
        role_id=UserRole.SALES,
    )

    contract = create_contract_graph(session)

    event = create_persisted_event(
        session,
        name="Mariage de John",
        contract_id=contract.id,
        start=datetime(2023, 11, 20, 14, 30),
        end=datetime(2023, 11, 20, 23, 30),
        location="53 Rue du Château",
        attendees=75,
        notes="Réception prévue à 18h.",
        support_representative_id=current_user.id,
    )

    result = runner.invoke(cli, ["event", "show", str(event.id)])

    assert result.exit_code == 0
    assert f"Événement n°{event.id}" in result.output
    assert "Mariage de John" in result.output
    assert "20/11/2023 14:30" in result.output
    assert "20/11/2023 23:30" in result.output
    assert "53 Rue du Château" in result.output
    assert "75" in result.output
    assert "Réception prévue à 18h." in result.output
    assert "400" in result.output


def test_show_event_with_invalid_id_display_error(
    logged_user_factory,
    session,
):
    runner = CliRunner()

    logged_user_factory(role_id=UserRole.SALES)

    result = runner.invoke(cli, ["event", "show", "9999"])

    assert result.exit_code == 0
    assert "Erreur: L'événement n'a pas été trouvé." in result.output


# assign_support
######################
def test_assign_support_success(logged_user_factory, session, force_console_width):
    runner = CliRunner()

    logged_user_factory(role_id=UserRole.MANAGEMENT)
    support_user = create_persisted_user(
        session,
        role_id=UserRole.SUPPORT,
        employee_number="111",
        email="support@email.com",
    )

    contract = create_contract_graph(session)
    event = create_persisted_event(session, contract_id=contract.id)

    result = runner.invoke(
        cli,
        ["event", "assign", str(event.id), "--support", "111"],
        input="y",
    )

    assert result.exit_code == 0

    assert (
        f"Le collaborateur {support_user.last_name} {support_user.first_name} "
        f"(n°{support_user.employee_number}) a bien été assigné comme support "
        f"à l'événement n°{event.id}" in result.output
    )

    session.refresh(event)
    assert event.support_representative_id == support_user.id


def test_assign_support_user_not_found_displays_error(logged_user_factory, session):
    runner = CliRunner()
    logged_user_factory(role_id=UserRole.MANAGEMENT)

    contract = create_contract_graph(session)
    event = create_persisted_event(session, contract_id=contract.id)

    result = runner.invoke(
        cli,
        ["event", "assign", str(event.id), "--support", "9999"],
    )

    assert result.exit_code == 0
    assert "L'utilisateur n'a pas été trouvé." in result.output


def test_assign_support_invalid_role_displays_error(logged_user_factory, session):
    runner = CliRunner()
    logged_user_factory(role_id=UserRole.MANAGEMENT)

    create_persisted_user(
        session,
        role_id=UserRole.SALES,
        employee_number="444",
        email="sales@email.com",
    )

    contract = create_contract_graph(session)
    event = create_persisted_event(session, contract_id=contract.id)

    result = runner.invoke(
        cli,
        ["event", "assign", str(event.id), "--support", "444"],
        input="y",
    )

    assert result.exit_code == 0
    assert "L'utilisateur assigné n'est pas du département support." in result.output


def test_assign_support_no_authorization_displays_error(logged_user_factory, session):
    runner = CliRunner()

    logged_user_factory(role_id=UserRole.SALES)

    contract = create_contract_graph(session)
    event = create_persisted_event(session, contract_id=contract.id)
    create_persisted_user(
        session, role_id=UserRole.SUPPORT, employee_number="111", email="s@e.com"
    )

    result = runner.invoke(
        cli,
        ["event", "assign", str(event.id), "--support", "111"],
    )

    assert result.exit_code == 0
    assert "Vous n'avez pas les droits pour cette action." in result.output


# unassign_support
######################
def test_unassign_support_success(logged_user_factory, session, force_console_width):
    runner = CliRunner()

    logged_user_factory(role_id=UserRole.MANAGEMENT)
    support_user = create_persisted_user(
        session,
        role_id=UserRole.SUPPORT,
        employee_number="111",
        email="support@email.com",
    )

    contract = create_contract_graph(session)
    event = create_persisted_event(
        session,
        name="Test Event",
        contract_id=contract.id,
        support_representative_id=support_user.id,
    )

    result = runner.invoke(
        cli,
        ["event", "unassign", str(event.id)],
        input="y",
    )

    assert result.exit_code == 0
    assert (
        f"Le support a bien été désassigner de l'événement n°{event.id}"
        in result.output
    )

    session.refresh(event)
    assert event.support_representative_id is None


def test_unassign_support_cancel_displays_message(logged_user_factory, session):
    runner = CliRunner()
    logged_user_factory(role_id=UserRole.MANAGEMENT)

    contract = create_contract_graph(session)
    support_user = create_persisted_user(
        session,
        employee_number="005",
        email="support@email.com",
        role_id=UserRole.SUPPORT,
    )
    event = create_persisted_event(
        session,
        contract_id=contract.id,
        support_representative_id=support_user.id,
    )

    result = runner.invoke(
        cli,
        ["event", "unassign", str(event.id)],
        input="n",
    )

    assert result.exit_code == 0
    assert "La désassignation du collaborateur support a été annulée." in result.output
