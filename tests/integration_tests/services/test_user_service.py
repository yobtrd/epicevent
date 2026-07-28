import pytest

from epicevent.exception import (
    EmailAlreadyExistsError,
    EmployeeNumberAlreadyExistsError,
    RolePermissionError,
    UserNotFoundError,
)
from epicevent.schemas.user_schema import UserUpdateManagement, UserUpdateSelf
from epicevent.security.roles import UserRole
from epicevent.services.password_service import PasswordService
from tests.conftest import create_persisted_user, create_user, create_user_dto


# create_user
###########################
def test_create_user_management_success(user_service):
    current_user = create_user(role_id=UserRole.MANAGEMENT)
    user_dto = create_user_dto()

    created = user_service.create_user(current_user, user_dto)

    assert created.id is not None
    assert created.first_name == user_dto.first_name


def test_create_user_hashes_password(uow, user_service):
    current_user = create_user(role_id=UserRole.MANAGEMENT)
    user_dto = create_user_dto()

    created = user_service.create_user(current_user, user_dto)

    persisted_user = uow.users.find_by_id(created.id)

    assert persisted_user.password_hash != user_dto.password
    assert user_service.password_service.verify(
        persisted_user.password_hash,
        user_dto.password,
    )


def test_create_user_with_same_email_raises_error(user_service, session):
    current_user = create_user(role_id=UserRole.MANAGEMENT)

    create_persisted_user(session, email="same@email.com")
    user_dto = create_user_dto(email="same@email.com")

    with pytest.raises(EmailAlreadyExistsError):
        user_service.create_user(current_user, user_dto)


def test_create_user_with_same_employee_number_raises_error(user_service, session):
    current_user = create_user(role_id=UserRole.MANAGEMENT)

    create_persisted_user(session, employee_number="001")
    user_dto = create_user_dto(employee_number="001")

    with pytest.raises(EmployeeNumberAlreadyExistsError):
        user_service.create_user(current_user, user_dto)


@pytest.mark.parametrize("role", [UserRole.SALES, UserRole.SUPPORT])
def test_unauthorized_user_cannot_create_user(user_service, role):
    current_user = create_user(role_id=role)

    user_dto = create_user_dto()

    with pytest.raises(RolePermissionError):
        user_service.create_user(current_user, user_dto)


# update_user_management
###########################
def test_management_can_update_profile(user_service, session):
    current_user = create_user(role_id=UserRole.MANAGEMENT)
    persisted_user = create_persisted_user(session, role_id=UserRole.SALES)

    new_data = UserUpdateManagement(role_id=UserRole.SUPPORT)
    user_service.update_user(current_user, persisted_user.employee_number, new_data)

    session.refresh(persisted_user)
    assert persisted_user.role_id == UserRole.SUPPORT


def test_update_profile_with_invalid_user_returns_error(user_service):
    current_user = create_user(role_id=UserRole.MANAGEMENT)
    bad_employee_number = "9999"

    new_data = UserUpdateManagement(email="new@email.com")

    with pytest.raises(UserNotFoundError):
        user_service.update_user(current_user, bad_employee_number, new_data)


@pytest.mark.parametrize("role", [UserRole.SALES, UserRole.SUPPORT])
def test_unauthorized_user_cannot_update_user(user_service, session, role):
    current_user = create_user(role_id=role, employee_number="001")
    persisted_user = create_persisted_user(
        session, employee_number="002", email="original@email.com"
    )

    new_data = UserUpdateManagement(email="new@email.com")

    with pytest.raises(RolePermissionError):
        user_service.update_user(current_user, persisted_user.employee_number, new_data)


# update_self_profile
###########################
def test_current_user_can_update_his_profile(user_service, session):
    password_service = PasswordService()
    current_user = create_persisted_user(
        session,
        email="old@email.com",
        password_hash=password_service.hash("defautpassword"),
    )

    new_data = UserUpdateSelf(email="new@email.com", password="newpassword")
    user_service.update_self(current_user, new_data)

    session.refresh(current_user)
    assert current_user.email == "new@email.com"
    assert password_service.verify(current_user.password_hash, "newpassword")


def test_update_self_partial_data_preserves_other_fields(user_service, session):
    current_user = create_persisted_user(
        session, first_name="John", last_name="Doe", email="john@test.com"
    )

    new_data = UserUpdateSelf(email="john.new@test.com")
    user_service.update_self(current_user, new_data)

    session.refresh(current_user)
    assert current_user.email == "john.new@test.com"
    assert current_user.first_name == "John"
    assert current_user.last_name == "Doe"


# deactivate
###########################
def test_management_can_deactivate_user(user_service, session):
    current_user = create_user(role_id=UserRole.MANAGEMENT)
    persisted_user = create_persisted_user(session)

    user_service.deactivate(current_user, persisted_user.employee_number)

    session.refresh(persisted_user)
    assert persisted_user.is_active is False


def test_deactivate_with_invalid_user_returns_error(user_service):
    current_user = create_user(role_id=UserRole.MANAGEMENT)
    bad_employee_number = "9999"

    with pytest.raises(UserNotFoundError):
        user_service.deactivate(current_user, bad_employee_number)


@pytest.mark.parametrize("role", [UserRole.SALES, UserRole.SUPPORT])
def test_unauthorized_user_cannot_deactivate_user(user_service, session, role):
    current_user = create_user(role_id=role)
    persisted_user = create_persisted_user(session)

    with pytest.raises(RolePermissionError):
        user_service.deactivate(current_user, persisted_user.id)
