from functools import wraps

import epicevent.bootstrap as bootstrap


def with_app(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        with bootstrap.application_factory.create() as app:
            return func(app, *args, **kwargs)

    return wrapper
