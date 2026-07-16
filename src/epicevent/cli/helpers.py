from functools import wraps

import epicevent.bootstrap as bootstrap
import epicevent.config as config
from epicevent.exception import (
    AuthenticationError,
    InvalidSessionError,
    InvalidTokenError,
    UserNotFoundError,
)
from epicevent.schemas.user import UserResponse

from .token_storage import TokenStorage


def with_app(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        with bootstrap.application_factory.create() as app:
            return func(app, *args, **kwargs)

    return wrapper


def get_token_storage() -> TokenStorage:
    return TokenStorage(config.TOKEN_PATH)


def get_current_user(app: bootstrap.Application) -> UserResponse:
    storage = get_token_storage()
    try:
        token = storage.get_access_token()
        user = app.auth.get_current_user(token)
        return user
    except (InvalidSessionError, InvalidTokenError, UserNotFoundError) as exc:
        raise AuthenticationError() from exc
