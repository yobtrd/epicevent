from datetime import datetime, timedelta

import pytest

from epicevent.exception import (
    ClientOwnershipError,
    ContractNotFoundError,
    ContractNotSignedError,
    EventNotFoundError,
    EventOwnershipError,
    RolePermissionError,
    SupportAssignmentError,
    UserNotFoundError,
)
from epicevent.models.event import Event
from epicevent.schemas.event_schema import EventUpdate
from epicevent.security.roles import UserRole
from tests.conftest import (
    create_contract_graph,
    create_event_dto,
    create_persisted_client,
    create_persisted_contract,
    create_persisted_event,
    create_persisted_user,
)


# create_event
###################
def test_create_event_success(session, event_service):
    current_user = create_persisted_user(session, role_id=UserRole.SALES)
    client = create_persisted_client(
        session,
        sales_representative_id=current_user.id,
    )
    contract = create_persisted_contract(
        session,
        client_id=client.id,
        sales_representative_id=current_user.id,
        is_signed=True,
    )
    event_dto = create_event_dto()

    created = event_service.create_event(current_user, contract.id, event_dto)

    session.refresh(created)
    assert created.id is not None
    assert created.start == event_dto.start
    assert created.end == event_dto.end
    assert created.location == event_dto.location
    assert created.attendees == event_dto.attendees
    assert created.notes == event_dto.notes
    assert created.contract_id == contract.id


def test_create_event_with_unknown_contract_raise_error(
    session,
    event_service,
):
    current_user = create_persisted_user(session, role_id=UserRole.SALES)
    event_dto = create_event_dto()

    with pytest.raises(ContractNotFoundError):
        event_service.create_event(current_user, 9999, event_dto)


def test_create_event_by_non_owner_raise_error(session, event_service):
    owner = create_persisted_user(session, role_id=UserRole.SALES)
    other = create_persisted_user(
        session,
        employee_number="999",
        email="other@test.com",
        role_id=UserRole.SALES,
    )

    client = create_persisted_client(
        session,
        sales_representative_id=owner.id,
    )
    contract = create_persisted_contract(
        session,
        client_id=client.id,
        sales_representative_id=owner.id,
        is_signed=True,
    )

    event_dto = create_event_dto()

    with pytest.raises(ClientOwnershipError):
        event_service.create_event(other, contract.id, event_dto)


def test_create_event_with_unsigned_contract_raise_error(session, event_service):
    current_user = create_persisted_user(session, role_id=UserRole.SALES)
    client = create_persisted_client(
        session,
        sales_representative_id=current_user.id,
    )
    contract = create_persisted_contract(
        session,
        client_id=client.id,
        sales_representative_id=current_user.id,
        is_signed=False,
    )

    event_dto = create_event_dto()

    with pytest.raises(ContractNotSignedError):
        event_service.create_event(current_user, contract.id, event_dto)


# update_event
###################
def test_support_can_update_owned_event(event_service, session):
    current_user = create_persisted_user(session, role_id=UserRole.SUPPORT)

    sales_rep = create_persisted_user(
        session,
        employee_number="002",
        email="sales@test.com",
        role_id=UserRole.SALES,
    )

    client = create_persisted_client(
        session,
        sales_representative_id=sales_rep.id,
    )

    contract = create_persisted_contract(
        session,
        client_id=client.id,
        sales_representative_id=sales_rep.id,
    )

    persisted_event = create_persisted_event(
        session,
        contract_id=contract.id,
        support_representative_id=current_user.id,
        location="Paris",
        attendees=100,
        notes="Anciennes notes",
    )

    new_data = EventUpdate(
        location="Lyon",
        attendees=250,
        notes="Nouvelles notes",
    )

    event_service.update_event(
        current_user,
        persisted_event.id,
        new_data,
    )

    session.refresh(persisted_event)

    assert persisted_event.location == "Lyon"
    assert persisted_event.attendees == 250
    assert persisted_event.notes == "Nouvelles notes"


def test_update_event_support_not_owned_event_raises_error(event_service, session):
    current_user = create_persisted_user(
        session,
        role_id=UserRole.SUPPORT,
    )

    other_support = create_persisted_user(
        session,
        employee_number="002",
        email="support@test.com",
        role_id=UserRole.SUPPORT,
    )

    sales_rep = create_persisted_user(
        session,
        employee_number="003",
        email="sales@test.com",
        role_id=UserRole.SALES,
    )

    client = create_persisted_client(
        session,
        sales_representative_id=sales_rep.id,
    )

    contract = create_persisted_contract(
        session,
        client_id=client.id,
        sales_representative_id=sales_rep.id,
    )

    persisted_event = create_persisted_event(
        session,
        contract_id=contract.id,
        support_representative_id=other_support.id,
    )

    new_data = EventUpdate(
        notes="Modification",
    )

    with pytest.raises(EventOwnershipError):
        event_service.update_event(
            current_user,
            persisted_event.id,
            new_data,
        )


def test_update_event_with_invalid_event_returns_error(event_service, session):
    current_user = create_persisted_user(
        session,
        role_id=UserRole.SUPPORT,
    )

    new_data = EventUpdate(
        notes="Modification",
    )

    with pytest.raises(EventNotFoundError):
        event_service.update_event(
            current_user,
            999,
            new_data,
        )


def test_update_event_unauthorized_user_raises_error(event_service, session):
    current_user = create_persisted_user(
        session,
        role_id=UserRole.SALES,
    )

    new_data = EventUpdate(
        notes="Modification",
    )

    from epicevent.exception import RolePermissionError

    with pytest.raises(RolePermissionError):
        event_service.update_event(
            current_user,
            999,
            new_data,
        )


def test_management_can_update_any_event(event_service, session):
    management = create_persisted_user(
        session,
        role_id=UserRole.MANAGEMENT,
    )

    support = create_persisted_user(
        session,
        employee_number="002",
        email="support@test.com",
        role_id=UserRole.SUPPORT,
    )

    sales_rep = create_persisted_user(
        session,
        employee_number="003",
        email="sales@test.com",
        role_id=UserRole.SALES,
    )

    client = create_persisted_client(
        session,
        sales_representative_id=sales_rep.id,
    )

    contract = create_persisted_contract(
        session,
        client_id=client.id,
        sales_representative_id=sales_rep.id,
    )

    persisted_event = create_persisted_event(
        session,
        contract_id=contract.id,
        support_representative_id=support.id,
        notes="Anciennes notes",
    )

    new_data = EventUpdate(
        notes="Notes modifiées",
    )

    event_service.update_event(
        management,
        persisted_event.id,
        new_data,
    )

    session.refresh(persisted_event)

    assert persisted_event.notes == "Notes modifiées"


# list_events
###################
@pytest.mark.parametrize(
    "role",
    [
        UserRole.MANAGEMENT,
        UserRole.SALES,
        UserRole.SUPPORT,
    ],
)
def test_list_events_returns_events_for_all_contributors(event_service, session, role):
    current_user = create_persisted_user(
        session,
        employee_number="400",
        email="contributor@email.com",
        role_id=role,
    )

    contract = create_contract_graph(session)

    for _ in range(3):
        create_persisted_event(
            session,
            contract_id=contract.id,
            support_representative_id=current_user.id,
        )

    events_list, total_count = event_service.list_events(current_user)

    assert len(events_list) == 3
    assert total_count == 3
    assert isinstance(events_list[0], Event)


def test_list_events_pagination(event_service, session):
    current_user = create_persisted_user(
        session,
        employee_number="400",
        email="support@email.com",
        role_id=UserRole.SUPPORT,
    )

    contract = create_contract_graph(session)

    for _ in range(15):
        create_persisted_event(
            session,
            contract_id=contract.id,
            support_representative_id=current_user.id,
        )

    events_page1, total_count = event_service.list_events(
        current_user,
        limit=10,
        offset=0,
    )

    assert len(events_page1) == 10
    assert total_count == 15

    events_page2, total_count = event_service.list_events(
        current_user,
        limit=10,
        offset=10,
    )

    assert len(events_page2) == 5
    assert total_count == 15


def test_list_events_filters_assigned(event_service, session):
    current_user = create_persisted_user(
        session,
        employee_number="300",
        email="managemet@email.com",
        role_id=UserRole.MANAGEMENT,
    )

    support_rep = create_persisted_user(
        session,
        employee_number="400",
        email="support@email.com",
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

    events_list, total_count = event_service.list_events(
        current_user,
        is_assigned=True,
    )

    assert len(events_list) == 1
    assert total_count == 1
    assert events_list[0].support_representative_id == support_rep.id


def test_list_events_filters_unassigned(event_service, session):
    current_user = create_persisted_user(
        session,
        employee_number="300",
        email="managemet@email.com",
        role_id=UserRole.MANAGEMENT,
    )

    support_rep = create_persisted_user(
        session,
        employee_number="400",
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

    events_list, total_count = event_service.list_events(
        current_user,
        is_assigned=False,
    )

    assert len(events_list) == 1
    assert total_count == 1
    assert events_list[0].support_representative_id is None


def test_list_events_filters_support_assigned_with_support(event_service, session):
    current_user = create_persisted_user(
        session,
        employee_number="300",
        email="support1@email.com",
        role_id=UserRole.SUPPORT,
    )

    other_support = create_persisted_user(
        session,
        employee_number="400",
        email="support2@email.com",
        role_id=UserRole.SUPPORT,
    )

    contract = create_contract_graph(session)

    create_persisted_event(
        session,
        contract_id=contract.id,
        support_representative_id=current_user.id,
    )
    create_persisted_event(
        session,
        contract_id=contract.id,
        support_representative_id=other_support.id,
    )

    events_list, total_count = event_service.list_events(
        current_user, support_assigned=True
    )

    assert len(events_list) == 1
    assert total_count == 1
    assert isinstance(events_list[0], Event)


@pytest.mark.parametrize("role", [UserRole.MANAGEMENT, UserRole.SALES])
def test_list_events_filters_support_assigned_with_other_contributors(
    event_service,
    session,
    role,
):
    current_user = create_persisted_user(
        session,
        employee_number="003",
        email="test@email.com",
        role_id=role,
    )
    support_user = create_persisted_user(
        session,
        employee_number="004",
        email="support@email.com",
        role_id=UserRole.SUPPORT,
    )

    contract = create_contract_graph(session)

    for _ in range(3):
        create_persisted_event(
            session,
            contract_id=contract.id,
            support_representative_id=support_user.id,
        )

    events_list, total_count = event_service.list_events(
        current_user, support_assigned=True
    )

    assert len(events_list) == 0
    assert total_count == 0


def test_list_events_filters_upcoming_only(event_service, session):
    current_user = create_persisted_user(
        session,
        employee_number="500",
        email="upcoming@email.com",
        role_id=UserRole.SUPPORT,
    )
    contract = create_contract_graph(session)

    create_persisted_event(
        session,
        contract_id=contract.id,
        start=datetime.now() - timedelta(days=2),
        end=datetime.now() - timedelta(days=1),
    )

    create_persisted_event(
        session,
        contract_id=contract.id,
        start=datetime.now(),
        end=datetime.now() + timedelta(days=1),
    )

    create_persisted_event(
        session,
        contract_id=contract.id,
        start=datetime.now() - timedelta(hours=1),
        end=datetime.now() + timedelta(days=2),
    )

    events_list, total_count = event_service.list_events(current_user, upcoming=True)

    assert len(events_list) == 2
    assert total_count == 2

    events_list_all, total_count_all = event_service.list_events(
        current_user, upcoming=False
    )
    assert len(events_list_all) == 3
    assert total_count_all == 3


# assign_support
###################
def test_assign_support_success(session, uow, event_service, logged_user_factory):
    manager = logged_user_factory(role_id=UserRole.MANAGEMENT)
    support_user = create_persisted_user(
        session,
        role_id=UserRole.SUPPORT,
        employee_number="333",
        email="support@email.com",
    )

    contract = create_contract_graph(session)
    event = create_persisted_event(session, name="Test Event", contract_id=contract.id)

    event_service.assign_support(
        current_user=manager, event_id=event.id, employee_number="333"
    )

    session.refresh(event)
    assert event.support_representative_id == support_user.id
    assert event.support_representative.employee_number == "333"


def test_assign_support_permission_denied(
    session, uow, event_service, logged_user_factory
):
    sales_user = logged_user_factory(
        role_id=UserRole.SALES,
        employee_number="010",
        email="sales@email.com",
    )

    contract = create_contract_graph(session)
    event = create_persisted_event(session, contract_id=contract.id)

    create_persisted_user(
        session,
        role_id=UserRole.SUPPORT,
        employee_number="333",
        email="support@email.com",
    )

    with pytest.raises(RolePermissionError):
        event_service.assign_support(
            current_user=sales_user, event_id=event.id, employee_number="333"
        )


def test_assign_support_user_not_found(
    session, uow, event_service, logged_user_factory
):
    manager = logged_user_factory(role_id=UserRole.MANAGEMENT)

    contract = create_contract_graph(session)
    event = create_persisted_event(session, contract_id=contract.id)

    with pytest.raises(UserNotFoundError):
        event_service.assign_support(
            current_user=manager, event_id=event.id, employee_number="9999"
        )


def test_assign_support_invalid_role(session, uow, event_service, logged_user_factory):
    manager = logged_user_factory(role_id=UserRole.MANAGEMENT)
    create_persisted_user(
        session,
        role_id=UserRole.SALES,
        employee_number="444",
        email="support@email.com",
    )

    contract = create_contract_graph(session)
    event = create_persisted_event(session, contract_id=contract.id)

    with pytest.raises(SupportAssignmentError):
        event_service.assign_support(
            current_user=manager, event_id=event.id, employee_number="444"
        )


# unassign_support
###################
def test_unassign_support_success(session, uow, event_service, logged_user_factory):
    manager = logged_user_factory(role_id=UserRole.MANAGEMENT)
    support_user = create_persisted_user(
        session,
        role_id=UserRole.SUPPORT,
        employee_number="333",
        email="support@email.com",
    )

    contract = create_contract_graph(session)
    event = create_persisted_event(
        session,
        name="Test Event",
        contract_id=contract.id,
        support_representative_id=support_user.id,
    )

    event_service.unassign_support(current_user=manager, event_id=event.id)

    session.refresh(event)
    assert event.support_representative is None
    assert event.support_representative_id is None


def test_unassign_support_permission_denied(
    session, uow, event_service, logged_user_factory
):
    sales_user = logged_user_factory(
        role_id=UserRole.SALES,
        employee_number="010",
        email="sales@email.com",
    )

    contract = create_contract_graph(session)
    event = create_persisted_event(session, contract_id=contract.id)

    with pytest.raises(RolePermissionError):
        event_service.unassign_support(current_user=sales_user, event_id=event.id)
