import pytest

from epicevent.exception import EmailAlreadyExistsError, RolePermissionError
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
