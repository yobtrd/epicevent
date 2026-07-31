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


# find_by_mail
############################
def test_find_by_email_returns_user(session):
    repository = ClientRepository(session)
    sales_representative = create_persisted_user(session, role_id=UserRole.SALES)
    persisted_client = create_persisted_client(
        session, sales_representative_id=sales_representative.id
    )

    found = repository.find_by_email(persisted_client.email)

    assert found is not None
    assert found.email == persisted_client.email


def test_find_by_email_returns_none_when_email_does_not_exist(session):
    repository = ClientRepository(session)

    assert repository.find_by_email("invalid@test.com") is None


# list
############################
def test_list_client_returns_client_list(session):
    repository = ClientRepository(session)
    sales_representative = create_persisted_user(session, role_id=UserRole.SALES)
    for i in range(3):
        create_persisted_client(
            session,
            email=f"client{i}@test.com",
            sales_representative_id=sales_representative.id,
        )

    clients = repository.list()

    assert len(clients) == 3


def test_list_client_pagination(session):
    repository = ClientRepository(session)
    sales_rep = create_persisted_user(session, role_id=UserRole.SALES)

    for i in range(15):
        create_persisted_client(
            session,
            email=f"client{i}@test.com",
            sales_representative_id=sales_rep.id,
        )

    page1 = repository.list(limit=10, offset=0)
    assert len(page1) == 10

    page2 = repository.list(limit=10, offset=10)
    assert len(page2) == 5


# count
############################
def test_count_returns_correct_length(session):
    repository = ClientRepository(session)
    sales_rep = create_persisted_user(session, role_id=UserRole.SALES)
    for i in range(15):
        create_persisted_client(
            session,
            email=f"client{i}@test.com",
            sales_representative_id=sales_rep.id,
        )

    length = repository.count()
    assert length == 15
