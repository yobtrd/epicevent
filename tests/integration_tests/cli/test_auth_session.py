import pytest
from freezegun import freeze_time

from epicevent.cli.auth_session import get_authenticated_user
from epicevent.cli.token_storage import TokenStorage
from epicevent.exception import AuthenticationError
from epicevent.services.token_service import TokenService
from tests.conftest import create_persisted_user


def test_get_authenticated_user_returns_correct_user(app_factory, session, token_path):
    token_storage = TokenStorage(token_path)
    token_service = TokenService()

    user = create_persisted_user(session, last_name="Doe")
    access_token = token_service.create_access_token(user)
    refresh_token = token_service.create_refresh_token(user)
    token_storage.save(access_token, refresh_token)

    with app_factory.create() as app:
        returned_user = get_authenticated_user(app)

    assert returned_user.id == user.id
    assert returned_user.last_name == "Doe"


def test_get_authenticated_user_saves_new_tokens_after_refresh(
    app_factory,
    session,
    token_path,
):
    token_service = TokenService()
    token_storage = TokenStorage(token_path)

    user = create_persisted_user(session, last_name="Doe")

    with freeze_time("2020-01-01 10:00:00"):
        initial_access_token = token_service.create_access_token(user)
        initial_refresh_token = token_service.create_refresh_token(user)

    token_storage.save(initial_access_token, initial_refresh_token)

    with freeze_time("2020-01-01 11:00:00"):
        with app_factory.create() as app:
            get_authenticated_user(app)

    final_access_token, final_refresh_token = token_storage.get_tokens()

    assert final_access_token != initial_access_token
    assert final_refresh_token != initial_refresh_token


def test_get_authenticated_user_with_expired_tokens_raises_error_and_clears_files(
    app_factory,
    session,
    token_path,
):
    token_storage = TokenStorage(token_path)
    token_service = TokenService()

    user = create_persisted_user(session, last_name="Doe")

    with freeze_time("2020-01-01 10:00:00"):
        access_token = token_service.create_access_token(user)
        refresh_token = token_service.create_refresh_token(user)

    token_storage.save(access_token, refresh_token)

    with pytest.raises(AuthenticationError):
        with freeze_time("2030-01-10 10:00:00"):
            with app_factory.create() as app:
                get_authenticated_user(app)
    assert not token_path.exists()
