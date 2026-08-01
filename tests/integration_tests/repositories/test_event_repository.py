from epicevent.infrastructure.repositories.event_repository import EventRepository
from epicevent.security.roles import UserRole
from tests.conftest import (
    create_contract_graph,
    create_event,
    create_persisted_client,
    create_persisted_contract,
    create_persisted_event,
    create_persisted_user,
)


# save
################
def test_save_event_success(session):
    repository = EventRepository(session)

    sales_rep = create_persisted_user(session, role_id=UserRole.SALES)
    client = create_persisted_client(
        session,
        sales_representative_id=sales_rep.id,
    )
    contract = create_persisted_contract(
        session,
        client_id=client.id,
        sales_representative_id=sales_rep.id,
    )

    event = create_event(contract_id=contract.id)
    created = repository.save(event)

    assert created.id is not None
    assert created.start == event.start
    assert created.end == event.end
    assert created.location == event.location
    assert created.attendees == event.attendees
    assert created.notes == event.notes
    assert created.contract_id == contract.id


# list
############################
def test_list_event_returns_event_list(session):
    repository = EventRepository(session)

    support_rep = create_persisted_user(
        session,
        employee_number="200",
        email="support@test.com",
        role_id=UserRole.SUPPORT,
    )

    contract = create_contract_graph(session)

    for _ in range(3):
        create_persisted_event(
            session,
            contract_id=contract.id,
            support_representative_id=support_rep.id,
        )

    events = repository.list(
        user_id=support_rep.id,
        user_role=UserRole.MANAGEMENT,
    )

    assert len(events) == 3


def test_list_event_pagination(session):
    repository = EventRepository(session)

    support_rep = create_persisted_user(
        session,
        employee_number="200",
        email="support@test.com",
        role_id=UserRole.SUPPORT,
    )

    contract = create_contract_graph(session)

    for _ in range(15):
        create_persisted_event(
            session,
            contract_id=contract.id,
            support_representative_id=support_rep.id,
        )

    page1 = repository.list(
        user_id=support_rep.id,
        user_role=UserRole.MANAGEMENT,
        limit=10,
        offset=0,
    )

    assert len(page1) == 10

    page2 = repository.list(
        user_id=support_rep.id,
        user_role=UserRole.MANAGEMENT,
        limit=10,
        offset=10,
    )

    assert len(page2) == 5


def test_list_management_user_sees_all_events(session):
    repository = EventRepository(session)

    support_rep_1 = create_persisted_user(
        session,
        employee_number="200",
        email="support1@test.com",
        role_id=UserRole.SUPPORT,
    )

    support_rep_2 = create_persisted_user(
        session,
        employee_number="201",
        email="support2@test.com",
        role_id=UserRole.SUPPORT,
    )

    contract = create_contract_graph(session)

    create_persisted_event(
        session,
        contract_id=contract.id,
        support_representative_id=support_rep_1.id,
    )

    create_persisted_event(
        session,
        contract_id=contract.id,
        support_representative_id=support_rep_2.id,
    )

    events = repository.list(
        user_id=support_rep_1.id,
        user_role=UserRole.MANAGEMENT,
    )

    assert len(events) == 2


def test_list_event_filters_support_representative(session):
    repository = EventRepository(session)

    support_rep_1 = create_persisted_user(
        session,
        employee_number="200",
        email="support1@test.com",
        role_id=UserRole.SUPPORT,
    )

    support_rep_2 = create_persisted_user(
        session,
        employee_number="201",
        email="support2@test.com",
        role_id=UserRole.SUPPORT,
    )

    contract = create_contract_graph(session)

    create_persisted_event(
        session,
        contract_id=contract.id,
        support_representative_id=support_rep_1.id,
    )

    create_persisted_event(
        session,
        contract_id=contract.id,
        support_representative_id=support_rep_2.id,
    )

    events = repository.list(
        user_id=support_rep_1.id,
        user_role=UserRole.SUPPORT,
    )

    assert len(events) == 1
    assert events[0].support_representative_id == support_rep_1.id


def test_list_event_filters_assigned(session):
    repository = EventRepository(session)

    support_rep = create_persisted_user(
        session,
        employee_number="200",
        email="support@test.com",
        role_id=UserRole.SUPPORT,
    )

    contract = create_contract_graph(session)

    create_persisted_event(
        session,
        contract_id=contract.id,
        support_representative_id=support_rep.id,
    )

    create_persisted_event(
        session,
        contract_id=contract.id,
        support_representative_id=None,
    )

    events = repository.list(
        user_id=support_rep.id,
        user_role=UserRole.MANAGEMENT,
        is_assigned=True,
    )

    assert len(events) == 1
    assert events[0].support_representative_id == support_rep.id


def test_list_event_filters_unassigned(session):
    repository = EventRepository(session)

    support_rep = create_persisted_user(
        session,
        employee_number="200",
        email="support@test.com",
        role_id=UserRole.SUPPORT,
    )

    contract = create_contract_graph(session)

    create_persisted_event(
        session,
        contract_id=contract.id,
        support_representative_id=support_rep.id,
    )

    create_persisted_event(
        session,
        contract_id=contract.id,
        support_representative_id=None,
    )

    events = repository.list(
        user_id=support_rep.id,
        user_role=UserRole.MANAGEMENT,
        is_assigned=False,
    )

    assert len(events) == 1
    assert events[0].support_representative_id is None


# count
############################
def test_count_returns_correct_length(session):
    repository = EventRepository(session)

    support_rep = create_persisted_user(
        session,
        employee_number="200",
        email="support@test.com",
        role_id=UserRole.SUPPORT,
    )

    contract = create_contract_graph(session)

    for _ in range(15):
        create_persisted_event(
            session,
            contract_id=contract.id,
            support_representative_id=support_rep.id,
        )

    length = repository.count(
        user_id=support_rep.id,
        user_role=UserRole.MANAGEMENT,
    )

    assert length == 15


def test_count_filters_assigned(session):
    repository = EventRepository(session)

    support_rep = create_persisted_user(
        session,
        employee_number="200",
        email="support@test.com",
        role_id=UserRole.SUPPORT,
    )

    contract = create_contract_graph(session)

    create_persisted_event(
        session,
        contract_id=contract.id,
        support_representative_id=support_rep.id,
    )

    create_persisted_event(
        session,
        contract_id=contract.id,
        support_representative_id=None,
    )

    length = repository.count(
        user_id=support_rep.id,
        user_role=UserRole.MANAGEMENT,
        is_assigned=True,
    )

    assert length == 1
