from epicevent.infrastructure.repositories.event_repository import EventRepository
from epicevent.security.roles import UserRole
from tests.conftest import (
    create_event,
    create_persisted_client,
    create_persisted_contract,
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
