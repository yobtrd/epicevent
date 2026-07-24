import functools

from epicevent.security import authorization
from epicevent.security.permission import Permission


def require_permission(permission: Permission):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            current_user = kwargs.get("current_user")
            if current_user is None and len(args) > 1:
                current_user = args[1]

            authorization.ensure_permission(current_user, permission)

            return func(*args, **kwargs)

        return wrapper

    return decorator
