import pytest
from sqlalchemy import text

from epicevents.exception import (
    EmailAlreadyExistsError,
    EmployeeNumberAlreadyExistsError,
)
from epicevents.infrastructure.repositories.user_repository import UserRepository
from epicevents.security.roles import UserRole
from tests.conftest import create_persisted_user, create_user


# save
############################
def test_save_user_success(session):
    repository = UserRepository(session)
    user = create_user()

    created = repository.save(user)

    assert created.id is not None
    assert created.email == user.email
    assert created.role_id == UserRole.MANAGEMENT


def test_save_user_with_existing_email_raises_error(session):
    repository = UserRepository(session)

    create_persisted_user(session, employee_number="001", email="same@email.com")
    user = create_user(employee_number="002", email="same@email.com")

    with pytest.raises(EmailAlreadyExistsError):
        repository.save(user)


def test_save_user_with_existing_emp_number_raises_error(session):
    repository = UserRepository(session)

    create_persisted_user(session, employee_number="001", email="mail1@email.com")
    user = create_user(employee_number="001", email="mail2@email.com")

    with pytest.raises(EmployeeNumberAlreadyExistsError):
        repository.save(user)


# find_by_mail
############################
def test_find_by_email_returns_user(session):
    repository = UserRepository(session)
    persisted_user = create_persisted_user(session)

    found = repository.find_by_email(persisted_user.email)

    assert found is not None
    assert found.email == persisted_user.email


def test_find_by_email_returns_none_when_email_does_not_exist(session):
    repository = UserRepository(session)

    assert repository.find_by_email("invalid@test.com") is None


def test_email_is_stored_encrypted(session):
    persisted_user = create_persisted_user(session)

    result = session.execute(
        text('SELECT email FROM "user" WHERE id = :user_id'),
        {"user_id": persisted_user.id},
    ).scalar_one()

    assert result != persisted_user.email


# find_by_id
############################
def test_find_by_id_returns_user(session):
    repository = UserRepository(session)
    persisted_user = create_persisted_user(session)

    found = repository.find_by_id(persisted_user.id)

    assert found is not None
    assert found.id == persisted_user.id


def test_find_by_id_returns_none_when_user_does_not_exist(session):
    repository = UserRepository(session)

    assert repository.find_by_id(999999) is None


# find_by_employee_number
############################
def test_find_by_employee_number_returns_user(session):
    repository = UserRepository(session)
    persisted_user = create_persisted_user(session, employee_number="001")

    found = repository.find_by_employee_number("001")

    assert found is not None
    assert found.id == persisted_user.id


def test_find_by_employee_number_returns_none_when_user_does_not_exist(session):
    repository = UserRepository(session)

    assert repository.find_by_employee_number("99999") is None


# list
############################
def test_list_user_returns_active_users(session):
    repository = UserRepository(session)

    create_persisted_user(session, is_active=True)
    create_persisted_user(
        session,
        employee_number="002",
        email="inactive@test.com",
        is_active=False,
    )

    users = repository.list()

    assert len(users) == 1
    assert users[0].is_active is True


def test_list_user_includes_inactive_users(session):
    repository = UserRepository(session)

    create_persisted_user(session, is_active=True)
    create_persisted_user(
        session,
        employee_number="002",
        email="inactive@test.com",
        is_active=False,
    )

    users = repository.list(include_inactive=True)

    assert len(users) == 2


def test_list_user_pagination(session):
    repository = UserRepository(session)

    for index in range(15):
        create_persisted_user(
            session,
            employee_number=f"{index:03}",
            email=f"user{index}@test.com",
        )

    page1 = repository.list(limit=10, offset=0)

    assert len(page1) == 10

    page2 = repository.list(limit=10, offset=10)

    assert len(page2) == 5


# superuser_exists
############################
def test_superuser_exists_returns_true_when_management_user_exists(session):
    repository = UserRepository(session)

    create_persisted_user(
        session,
        role_id=UserRole.MANAGEMENT,
    )

    assert repository.superuser_exists() is True


def test_superuser_exists_returns_false_without_management_user(session):
    repository = UserRepository(session)

    create_persisted_user(
        session,
        role_id=UserRole.SALES,
    )

    assert repository.superuser_exists() is False
