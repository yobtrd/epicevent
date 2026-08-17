import jwt
import pytest
from freezegun import freeze_time

from epicevents.config.settings import get_settings
from epicevents.exception import ExpiredTokenError, InvalidTokenError
from epicevents.services.auth_service import TokenService
from tests.conftest import create_user


def test_create_access_token():
    token_service = TokenService()
    user = create_user(id=1)
    access_token = token_service.create_access_token(user)

    payload = jwt.decode(
        access_token,
        get_settings().secret_key,
        algorithms=["HS256"],
    )

    assert payload["sub"] == "1"
    assert payload["type"] == "access"
    assert payload["exp"] > payload["iat"]


def test_create_refresh_token():
    token_service = TokenService()
    user = create_user(id=1)
    refresh_token = token_service.create_refresh_token(user)

    payload = jwt.decode(
        refresh_token,
        get_settings().secret_key,
        algorithms=["HS256"],
    )

    assert payload["sub"] == "1"
    assert payload["type"] == "refresh"
    assert payload["exp"] > payload["iat"]


def test_decode_access_token():
    token_service = TokenService()
    user = create_user(id=1)

    token = token_service.create_access_token(user)

    payload = token_service.decode_token(token, "access")

    assert payload.sub == 1
    assert payload.type == "access"


def test_decode_refresh_token():
    token_service = TokenService()
    user = create_user(id=1)

    token = token_service.create_refresh_token(user)

    payload = token_service.decode_token(token, "refresh")

    assert payload.sub == 1
    assert payload.type == "refresh"


def test_decode_expired_access_token():
    token_service = TokenService()
    user = create_user()

    with freeze_time("2020-01-01 10:00:00"):
        token = token_service.create_access_token(user)

    with freeze_time("2020-01-01 12:00:00"):
        with pytest.raises(ExpiredTokenError):
            token_service.decode_token(token)


def test_decode_expired_refresh_token():
    token_service = TokenService()
    user = create_user()

    with freeze_time("2020-01-01 10:00:00"):
        token = token_service.create_refresh_token(user)

    with freeze_time("2030-01-01 11:00:00"):
        with pytest.raises(ExpiredTokenError):
            token_service.decode_token(token)


def test_decode_invalid_signature():
    token_service = TokenService()
    user = create_user()

    token = token_service.create_access_token(user)

    header, payload, signature = token.split(".")
    invalid_token = f"{header}.{payload}.invalidsignature"

    with pytest.raises(InvalidTokenError):
        token_service.decode_token(invalid_token)


def test_decode_malformed_token():
    token_service = TokenService()

    with pytest.raises(InvalidTokenError):
        token_service.decode_token("malformed.jwt")


def test_decode_wrong_type_token():
    token_service = TokenService()
    user = create_user()

    token = token_service.create_access_token(user)

    with pytest.raises(InvalidTokenError):
        token_service.decode_token(token, "refresh")
