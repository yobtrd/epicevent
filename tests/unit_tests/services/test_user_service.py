import pytest

from src.epicevent.constants.roles import RoleId
from src.epicevent.schemas.user import UserUpdate
from src.epicevent.services.user_service import (
    EmailAlreadyExistsError,
    UserNotFoundError,
    UserService,
)
from tests.conftest import create_persisted_user, create_user_dto


def test_create_user(uow):
    user_service = UserService(uow)
    user_dto = create_user_dto()
    created = user_service.create(user_dto)

    assert created.first_name == user_dto.first_name
    assert created.id is not None


def test_create_user_hashes_password(uow):
    user_service = UserService(uow)
    user_dto = create_user_dto()
    created = user_service.create(user_dto)

    persisted_user = uow.users.get_by_id(created.id)

    assert persisted_user.password_hash != user_dto.password
    assert user_service.password_service.verify(
        persisted_user.password_hash,
        user_dto.password,
    )


def test_create_user_with_same_email_raises_error(uow, session):
    user_service = UserService(uow)
    create_persisted_user(session, employee_number="001", email="same@email.com")
    user_dto = create_user_dto(employee_number="002", email="same@email.com")

    with pytest.raises(EmailAlreadyExistsError):
        user_service.create(user_dto)


def test_change_role_modifies_role(uow, session):
    user_service = UserService(uow)
    persisted_user = create_persisted_user(session, role_id=1)

    assert persisted_user.role.name == "management"
    user_service.change_role(persisted_user.id, RoleId.SALES)

    session.refresh(persisted_user)
    assert persisted_user.role_id == RoleId.SALES
    assert persisted_user.role.name == "sales"


def test_change_role_with_invalid_user_returns_error(uow):
    user_service = UserService(uow)
    bad_user_id = 9999

    with pytest.raises(UserNotFoundError):
        user_service.change_role(bad_user_id, RoleId.SALES)


def test_update_profile_updates_profile(uow, session):
    user_service = UserService(uow)
    persisted_user = create_persisted_user(session, email="original@email.com")

    new_data = UserUpdate(email="new@email.com")
    user_service.update_profile(persisted_user.id, new_data)

    session.refresh(persisted_user)
    assert persisted_user.email == "new@email.com"


def test_update_profile_with_invalid_user_returns_error(uow):
    user_service = UserService(uow)
    bad_user_id = 9999

    new_data = UserUpdate(email="new@email.com")

    with pytest.raises(UserNotFoundError):
        user_service.update_profile(bad_user_id, new_data)


def test_deactivate_deactivates_user(uow, session):
    user_service = UserService(uow)
    persisted_user = create_persisted_user(session)

    user_service.deactivate(persisted_user.id)

    session.refresh(persisted_user)
    assert persisted_user.is_active is False


def test_deactivate_with_invalid_user_returns_error(uow):
    user_service = UserService(uow)
    bad_user_id = 9999

    with pytest.raises(UserNotFoundError):
        user_service.deactivate(bad_user_id)
