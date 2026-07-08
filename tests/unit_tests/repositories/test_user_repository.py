from src.epicevent.constants.roles import RoleName
from src.epicevent.repositories.user_repository import UserRepository


def test_create_user(session, user, roles):
    repository = UserRepository(session)

    created = repository.create(user)

    assert created.id is not None
    assert created.email == user.email
    assert created.role_id == roles[RoleName.SALES]


def test_get_by_email_returns_user(session, persisted_user):
    repository = UserRepository(session)

    found = repository.get_by_email(persisted_user.email)

    assert found is not None
    assert found.email == persisted_user.email


def test_get_by_email_returns_none_when_email_does_not_exist(session):
    repository = UserRepository(session)

    assert repository.get_by_email("invalid@test.com") is None


def test_get_by_id_returns_user(session, persisted_user):
    repository = UserRepository(session)

    found = repository.get_by_id(persisted_user.id)

    assert found is not None
    assert found.id == persisted_user.id


def test_get_by_id_returns_none_when_user_does_not_exist(session):
    repository = UserRepository(session)

    assert repository.get_by_id(999999) is None
