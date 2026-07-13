from src.epicevent.constants.roles import RoleId
from src.epicevent.repositories.user_repository import UserRepository
from tests.conftest import create_persisted_user, create_user


def test_create_user(session):
    repository = UserRepository(session)
    user = create_user()

    created = repository.create(user)

    assert created.id is not None
    assert created.email == user.email
    assert created.role_id == RoleId.MANAGEMENT


def test_get_by_email_returns_user(session):
    repository = UserRepository(session)
    persisted_user = create_persisted_user(session)

    found = repository.get_by_email(persisted_user.email)

    assert found is not None
    assert found.email == persisted_user.email


def test_get_by_email_returns_none_when_email_does_not_exist(session):
    repository = UserRepository(session)

    assert repository.get_by_email("invalid@test.com") is None


def test_get_by_id_returns_user(session):
    repository = UserRepository(session)
    persisted_user = create_persisted_user(session)

    found = repository.get_by_id(persisted_user.id)

    assert found is not None
    assert found.id == persisted_user.id


def test_get_by_id_returns_none_when_user_does_not_exist(session):
    repository = UserRepository(session)

    assert repository.get_by_id(999999) is None
