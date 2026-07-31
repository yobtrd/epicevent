import pytest

from epicevent.exception import (
    ClientOwnershipError,
    ContractNotFoundError,
    ContractNotSignedError,
)
from epicevent.security.roles import UserRole
from tests.conftest import (
    create_event_dto,
    create_persisted_client,
    create_persisted_contract,
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
