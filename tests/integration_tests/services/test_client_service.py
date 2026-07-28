from datetime import date

import pytest

from epicevent.exception import (
    ClientNotFoundError,
    ClientOwnershipError,
    EmailAlreadyExistsError,
    RolePermissionError,
)
from epicevent.schemas.client_schema import ClientUpdate
from epicevent.security.roles import UserRole
from tests.conftest import (
    create_client_dto,
    create_persisted_client,
    create_persisted_user,
)


# create_client
###################
def test_create_client_by_sales_success(session, client_service):
    current_user = create_persisted_user(session, role_id=UserRole.SALES)
    client_dto = create_client_dto()

    created = client_service.create_client(current_user, client_dto)

    assert created.id is not None
    assert created.email == client_dto.email
    assert created.sales_representative_id == current_user.id


def test_create_client_with_same_email_raises_error(session, client_service):
    current_user = create_persisted_user(session, role_id=UserRole.SALES)
    create_persisted_client(
        session, email="same@email.com", sales_representative_id=current_user.id
    )
    client_dto = create_client_dto(email="same@email.com")

    with pytest.raises(EmailAlreadyExistsError):
        client_service.create_client(current_user, client_dto)


@pytest.mark.parametrize("role", [UserRole.MANAGEMENT, UserRole.SUPPORT])
def test_unauthorized_user_cannot_create_client(session, client_service, role):
    current_user = create_persisted_user(session, role_id=role)
    client_dto = create_client_dto()

    with pytest.raises(RolePermissionError):
        client_service.create_client(current_user, client_dto)


# update_client
###################
def test_sales_can_update_owned_client(client_service, session):
    current_user = create_persisted_user(session, role_id=UserRole.SALES)
    persisted_client = create_persisted_client(
        session,
        last_name="Doe",
        last_contact="2020-10-10",
        sales_representative_id=current_user.id,
    )
    new_data = ClientUpdate(last_name="Dae", last_contact="2020-11-15")

    client_service.update_client(current_user, persisted_client.email, new_data)

    session.refresh(persisted_client)
    assert persisted_client.last_name == "Dae"
    assert persisted_client.last_contact == date(2020, 11, 15)


def test_update_client_sales_not_owned_client_raises_error(client_service, session):
    current_user = create_persisted_user(
        session,
        employee_number="001",
        email="current@email.com",
        role_id=UserRole.SALES,
    )
    other_sales = create_persisted_user(
        session,
        employee_number="002",
        email="other@email.com",
        role_id=UserRole.SALES,
    )
    persisted_client = create_persisted_client(
        session, last_contact="2020-10-10", sales_representative_id=other_sales.id
    )

    new_data = ClientUpdate(last_contact="2020-11-15")

    with pytest.raises(ClientOwnershipError):
        client_service.update_client(current_user, persisted_client.email, new_data)


def test_update_client_with_invalid_client_returns_error(client_service, session):
    current_user = create_persisted_user(session, role_id=UserRole.SALES)
    bad_client_email = "bad@email.com"

    new_data = ClientUpdate(last_contact="2020-11-15")

    with pytest.raises(ClientNotFoundError):
        client_service.update_client(current_user, bad_client_email, new_data)


@pytest.mark.parametrize("role", [UserRole.MANAGEMENT, UserRole.SUPPORT])
def test_update_user_unauthorized_user_raises_error(client_service, session, role):
    current_user = create_persisted_user(session, role_id=role)
    persisted_client = create_persisted_client(
        session, sales_representative_id=current_user.id
    )

    new_data = new_data = ClientUpdate(last_contact="2020-11-15")

    with pytest.raises(RolePermissionError):
        client_service.update_client(current_user, persisted_client.email, new_data)
