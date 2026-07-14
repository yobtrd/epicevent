import jwt
import pytest
from freezegun import freeze_time
from jwt.exceptions import (
    DecodeError,
    ExpiredSignatureError,
    InvalidSignatureError,
)

from src.epicevent.config import SECRET_KEY
from src.epicevent.exception import InvalidTokenTypeError
from src.epicevent.services.auth_service import TokenService
from tests.conftest import create_user


def test_create_access_token():
    token_service = TokenService()
    user = create_user(id=1)
    access_token = token_service.create_access_token(user)

    payload = jwt.decode(
        access_token,
        SECRET_KEY,
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
        SECRET_KEY,
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


def test_decode_expired_token():
    token_service = TokenService()
    user = create_user(id=1)

    with freeze_time("2023-01-01 10:00:00"):
        token = token_service.create_access_token(user)

    with freeze_time("2023-01-01 11:00:00"):
        with pytest.raises(ExpiredSignatureError):
            token_service.decode_token(token)


def test_decode_invalid_signature():
    token_service = TokenService()
    user = create_user(id=1)

    token = token_service.create_access_token(user)

    invalid_token = token[:-1] + ("a" if token[-1] != "a" else "b")

    with pytest.raises(InvalidSignatureError):
        token_service.decode_token(invalid_token)


def test_decode_malformed_token():
    token_service = TokenService()

    with pytest.raises(DecodeError):
        token_service.decode_token("malformed.jwt")


def test_decode_wrong_type_token():
    token_service = TokenService()
    user = create_user(id=1)

    token = token_service.create_access_token(user)

    with pytest.raises(InvalidTokenTypeError):
        token_service.decode_token(token, "refresh")
