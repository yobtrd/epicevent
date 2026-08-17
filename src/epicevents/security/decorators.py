import functools

from epicevents.security import authorization
from epicevents.security.permission import Permission


def require_permission(permission: Permission):
    """
    Require a specific permission before executing a service method.

    The decorated function must receive the authenticated user as a
    `current_user` keyword argument or as its second positional argument.

    Raises:
        RolePermissionError: If the user does not have the required permission.
    """

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
