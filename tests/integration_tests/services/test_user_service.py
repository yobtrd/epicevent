import pytest

from epicevent.constants.roles import RoleId
from epicevent.exception import (
    EmailAlreadyExistsError,
    RolePermissionError,
    UserNotFoundError,
)
from epicevent.schemas.user import UserUpdate
from epicevent.services.user_service import UserService
from tests.conftest import create_persisted_user, create_user, create_user_dto


# create
######################
def test_management_can_create_user(uow):
    user_service = UserService(uow)
    current_user = create_user(role_id=RoleId.MANAGEMENT)
    user_dto = create_user_dto()

    created = user_service.create_user(current_user, user_dto)

    assert created.first_name == user_dto.first_name
    assert created.id is not None


def test_create_user_hashes_password(uow):
    user_service = UserService(uow)
    current_user = create_user(role_id=RoleId.MANAGEMENT)
    user_dto = create_user_dto()

    created = user_service.create_user(current_user, user_dto)

    persisted_user = uow.users.find_by_id(created.id)

    assert persisted_user.password_hash != user_dto.password
    assert user_service.password_service.verify(
        persisted_user.password_hash,
        user_dto.password,
    )


def test_create_user_with_same_email_raises_error(uow, session):
    user_service = UserService(uow)
    current_user = create_user(role_id=RoleId.MANAGEMENT)

    create_persisted_user(session, employee_number="001", email="same@email.com")
    user_dto = create_user_dto(employee_number="002", email="same@email.com")

    with pytest.raises(EmailAlreadyExistsError):
        user_service.create_user(current_user, user_dto)


@pytest.mark.parametrize("role", [RoleId.SALES, RoleId.SUPPORT])
def test_unauthorized_user_cannot_create_user(uow, role):
    user_service = UserService(uow)
    current_user = create_user(role_id=role)

    user_dto = create_user_dto()

    with pytest.raises(RolePermissionError):
        user_service.create_user(current_user, user_dto)


# change_role
######################
def test_management_can_modify_role(uow, session):
    user_service = UserService(uow)
    current_user = create_user(role_id=RoleId.MANAGEMENT)
    persisted_user = create_persisted_user(session, role_id=RoleId.SUPPORT)

    assert persisted_user.role.name == "support"
    user_service.change_role(current_user, persisted_user.id, RoleId.SALES)

    session.refresh(persisted_user)
    assert persisted_user.role_id == RoleId.SALES
    assert persisted_user.role.name == "sales"


def test_change_role_with_invalid_user_returns_error(uow):
    user_service = UserService(uow)
    current_user = create_user(role_id=RoleId.MANAGEMENT)
    bad_user_id = 9999

    with pytest.raises(UserNotFoundError):
        user_service.change_role(current_user, bad_user_id, RoleId.SALES)


@pytest.mark.parametrize("role", [RoleId.SALES, RoleId.SUPPORT])
def test_unauthorized_user_cannot_modify_role(uow, session, role):
    user_service = UserService(uow)
    current_user = create_user(role_id=role)
    persisted_user = create_persisted_user(session, role_id=RoleId.SUPPORT)

    with pytest.raises(RolePermissionError):
        user_service.change_role(current_user, persisted_user.id, RoleId.MANAGEMENT)


# update_profile
######################
def test_management_can_update_profile(uow, session):
    user_service = UserService(uow)
    current_user = create_user(role_id=RoleId.MANAGEMENT)
    persisted_user = create_persisted_user(session, email="original@email.com")

    new_data = UserUpdate(email="new@email.com")
    user_service.update_profile(current_user, persisted_user.id, new_data)

    session.refresh(persisted_user)
    assert persisted_user.email == "new@email.com"


def test_current_user_can_update_his_profile(uow, session):
    user_service = UserService(uow)
    persisted_user = create_persisted_user(session, last_name="Doe")
    current_user = persisted_user

    new_data = UserUpdate(last_name="Dae")
    user_service.update_profile(current_user, persisted_user.id, new_data)

    session.refresh(persisted_user)
    assert persisted_user.last_name == "Dae"


def test_update_profile_with_invalid_user_returns_error(uow):
    user_service = UserService(uow)
    current_user = create_user(role_id=RoleId.MANAGEMENT)
    bad_user_id = 9999

    new_data = UserUpdate(email="new@email.com")

    with pytest.raises(UserNotFoundError):
        user_service.update_profile(current_user, bad_user_id, new_data)


@pytest.mark.parametrize("role", [RoleId.SALES, RoleId.SUPPORT])
def test_unauthorized_user_cannot_update_user(uow, session, role):
    user_service = UserService(uow)
    current_user = create_user(role_id=role)
    persisted_user = create_persisted_user(session, email="original@email.com")

    new_data = UserUpdate(email="new@email.com")

    with pytest.raises(RolePermissionError):
        user_service.update_profile(current_user, persisted_user.id, new_data)


# deactivate
######################
def test_management_can_deactivate_user(uow, session):
    user_service = UserService(uow)
    current_user = create_user(role_id=RoleId.MANAGEMENT)
    persisted_user = create_persisted_user(session)

    user_service.deactivate(current_user, persisted_user.id)

    session.refresh(persisted_user)
    assert persisted_user.is_active is False


def test_deactivate_with_invalid_user_returns_error(uow):
    user_service = UserService(uow)
    current_user = create_user(role_id=RoleId.MANAGEMENT)
    bad_user_id = 9999

    with pytest.raises(UserNotFoundError):
        user_service.deactivate(current_user, bad_user_id)


@pytest.mark.parametrize("role", [RoleId.SALES, RoleId.SUPPORT])
def test_unauthorized_user_cannot_deactivate_user(uow, session, role):
    user_service = UserService(uow)
    current_user = create_user(role_id=role)
    persisted_user = create_persisted_user(session)

    with pytest.raises(RolePermissionError):
        user_service.deactivate(current_user, persisted_user.id)
