from functools import wraps

import epicevent.bootstrap as bootstrap
import epicevent.config as config

from .token_storage import TokenStorage


def with_app(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        with bootstrap.application_factory.create() as app:
            return func(app, *args, **kwargs)

    return wrapper


def get_token_storage() -> TokenStorage:
    return TokenStorage(config.TOKEN_PATH)
