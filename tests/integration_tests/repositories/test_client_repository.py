import pytest

from epicevent.exception import EmailAlreadyExistsError
from epicevent.infrastructure.repositories.client_repository import ClientRepository
from epicevent.security.roles import UserRole
from tests.conftest import create_client, create_persisted_client, create_persisted_user


# save
############################
def test_save_client_success(session):
    repository = ClientRepository(session)
    sales_representative = create_persisted_user(session, role_id=UserRole.SALES)

    client = create_client(sales_representative_id=sales_representative.id)
    created = repository.save(client)

    assert created.id is not None
    assert created.email == client.email
    assert created.sales_representative_id == sales_representative.id


def test_save_client_with_existing_email_raises_error(session):
    repository = ClientRepository(session)
    sales_representative = create_persisted_user(session, role_id=UserRole.SALES)
    create_persisted_client(
        session, email="same@email.com", sales_representative_id=sales_representative.id
    )

    client = create_client(
        email="same@email.com", sales_representative_id=sales_representative.id
    )

    with pytest.raises(EmailAlreadyExistsError):
        repository.save(client)
