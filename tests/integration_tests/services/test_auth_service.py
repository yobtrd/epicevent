import pytest

from epicevent.exception import InvalidCredentialsError, UserNotFoundError
from epicevent.schemas.auth_schema import AuthRequest
from epicevent.services.auth_service import AuthService
from epicevent.services.password_service import PasswordService
from epicevent.services.token_service import TokenService
from tests.conftest import create_persisted_user, create_user


# authenticate
######################
def test_authenticate_correct_credentials(uow, session):
    auth_service = AuthService(uow)
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


def test_authenticate_unknow_email(uow, session):
    auth_service = AuthService(uow)
    password = "password"
    create_persisted_user(
        session,
        email="test@email.com",
        password_hash=PasswordService().hash(password),
    )

    auth_request = AuthRequest(email="incorrect@memail.com", password=password)
    with pytest.raises(InvalidCredentialsError):
        auth_service.authenticate(auth_request)


def test_authenticate_wrong_password(uow, session):
    auth_service = AuthService(uow)
    password = "password"
    user = create_persisted_user(
        session,
        email="test@email.com",
        password_hash=PasswordService().hash(password),
    )

    auth_request = AuthRequest(email=user.email, password="wrong-password")
    with pytest.raises(InvalidCredentialsError):
        auth_service.authenticate(auth_request)


# get_current_user
######################
def test_get_current_user_with_valid_token(uow, session):
    auth_service = AuthService(uow)
    token_service = TokenService()

    user = create_persisted_user(session, last_name="Doe")
    token = token_service.create_access_token(user)

    user_found = auth_service.get_current_user(token)

    assert user_found.id == user.id
    assert user_found.last_name == "Doe"


def test_get_current_user_when_user_not_found(uow):
    auth_service = AuthService(uow)

    user = create_user(id=999)

    token = TokenService().create_access_token(user)

    with pytest.raises(UserNotFoundError):
        auth_service.get_current_user(token)
