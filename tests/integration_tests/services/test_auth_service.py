import pytest
from freezegun import freeze_time

from epicevent.exception import (
    AuthenticationError,
    InvalidCredentialsError,
    UserDisabledError,
    UserNotFoundError,
)
from epicevent.schemas.auth_schema import AuthRequest
from epicevent.services.password_service import PasswordService
from epicevent.services.token_service import TokenService
from tests.conftest import create_persisted_user, create_user


# authenticate
########################
def test_authenticate_correct_credentials(auth_service, session):
    password = "password"
    user = create_persisted_user(
        session,
        email="test@email.com",
        password_hash=PasswordService().hash(password),
    )

    auth_request = AuthRequest(email=user.email, password=password)
    response = auth_service.authenticate(auth_request)

    assert response.user.email == "test@email.com"
    assert response.user.id == user.id
    assert response.access_token is not None
    assert response.refresh_token is not None


def test_authenticate_unknow_email(auth_service, session):
    password = "password"
    create_persisted_user(
        session,
        email="test@email.com",
        password_hash=PasswordService().hash(password),
    )

    auth_request = AuthRequest(email="incorrect@memail.com", password=password)
    with pytest.raises(InvalidCredentialsError):
        auth_service.authenticate(auth_request)


def test_authenticate_wrong_password(auth_service, session):
    password = "password"
    user = create_persisted_user(
        session,
        email="test@email.com",
        password_hash=PasswordService().hash(password),
    )

    auth_request = AuthRequest(email=user.email, password="wrong-password")
    with pytest.raises(InvalidCredentialsError):
        auth_service.authenticate(auth_request)


def test_authenticate_with_deactivated_account(auth_service, session):
    password = "password"
    user = create_persisted_user(
        session,
        email="test@email.com",
        password_hash=PasswordService().hash(password),
        is_active=False,
    )

    auth_request = AuthRequest(email=user.email, password="password")
    with pytest.raises(UserDisabledError):
        auth_service.authenticate(auth_request)


# get_current_user
########################
def test_get_current_user_with_valid_token(auth_service, session):
    token_service = TokenService()

    user = create_persisted_user(session, last_name="Doe")
    token = token_service.create_access_token(user)

    user_found = auth_service.get_current_user(token)

    assert user_found.id == user.id
    assert user_found.last_name == "Doe"


def test_get_current_user_when_user_not_found_returns_error(auth_service):
    user = create_user(id=999)

    token = TokenService().create_access_token(user)

    with pytest.raises(UserNotFoundError):
        auth_service.get_current_user(token)


# refresh_session
########################
def test_refresh_session_return_new_session(auth_service, session):
    token_service = TokenService()

    user = create_persisted_user(session, last_name="Doe")
    refresh_token = token_service.create_refresh_token(user)

    response = auth_service.refresh_session(refresh_token)

    assert response.user.id == user.id
    assert response.user.last_name == "Doe"
    assert response.new_tokens.access_token is not None
    assert response.new_tokens.refresh_token is not None


def test_refresh_session_when_user_not_found_returns_error(auth_service):
    token_service = TokenService()

    user = create_user(id=999)
    refresh_token = token_service.create_refresh_token(user)

    with pytest.raises(UserNotFoundError):
        auth_service.refresh_session(refresh_token)


# authenticate_session
########################
def test_authenticate_with_valid_access_token_returns_user(auth_service, session):
    token_service = TokenService()

    user = create_persisted_user(session, last_name="Doe")
    access_token = token_service.create_access_token(user)
    refresh_token = token_service.create_refresh_token(user)

    response = auth_service.authenticate_session(
        access_token,
        refresh_token,
    )

    assert response.user.id == user.id
    assert response.user.last_name == "Doe"
    assert response.new_tokens is None


def test_authenticate_session_with_expired_access_token_returns_new_session(
    auth_service,
    session,
):
    token_service = TokenService()

    user = create_persisted_user(session, last_name="Doe")

    with freeze_time("2020-01-01 10:00:00"):
        access_token = token_service.create_access_token(user)
        refresh_token = token_service.create_refresh_token(user)

    with freeze_time("2020-01-01 12:00:00"):
        response = auth_service.authenticate_session(
            access_token,
            refresh_token,
        )

    assert response.user.id == user.id
    assert response.user.last_name == "Doe"
    assert response.new_tokens is not None
    assert response.new_tokens.access_token is not None
    assert response.new_tokens.refresh_token is not None


def test_authenticate_session_with_expired_refresh_token_returns_error(
    auth_service,
    session,
):
    token_service = TokenService()

    user = create_persisted_user(session)

    with freeze_time("2020-01-01 10:00:00"):
        access_token = token_service.create_access_token(user)
        refresh_token = token_service.create_refresh_token(user)

    with freeze_time("2030-01-01 10:00:00"):
        with pytest.raises(AuthenticationError):
            auth_service.authenticate_session(
                access_token,
                refresh_token,
            )


def test_authenticate_session_with_invalid_access_token_returns_error(auth_service):
    with pytest.raises(AuthenticationError):
        auth_service.authenticate_session(
            "this-is-not-a-valid-token",
            "this-is-not-a-valid-refresh-token",
        )


def test_authenticate_session_without_tokens_returns_error(auth_service):
    with pytest.raises(AuthenticationError):
        auth_service.authenticate_session(
            None,
            None,
        )


def test_authenticate_session_without_refresh_token_returns_error(
    auth_service, session
):
    token_service = TokenService()

    user = create_persisted_user(session)
    access_token = token_service.create_access_token(user)

    with pytest.raises(AuthenticationError):
        auth_service.authenticate_session(
            access_token,
            None,
        )


def test_authenticate_session_with_unknown_user_returns_authentication_error(
    auth_service,
):
    token_service = TokenService()

    user = create_user(id=999)

    access_token = token_service.create_access_token(user)
    refresh_token = token_service.create_refresh_token(user)

    with pytest.raises(AuthenticationError):
        auth_service.authenticate_session(
            access_token,
            refresh_token,
        )
