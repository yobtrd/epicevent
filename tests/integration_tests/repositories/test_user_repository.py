import pytest

from epicevent.exception import (
    EmailAlreadyExistsError,
    EmployeeNumberAlreadyExistsError,
)
from epicevent.infrastructure.repositories.user_repository import UserRepository
from epicevent.security.roles import UserRole
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
