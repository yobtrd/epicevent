import functools

from epicevent.security.permission import Permission


def require_permission(permission: Permission):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            instance = args[0]
            auth_service = getattr(instance, "authorization", None)

            current_user = kwargs.get("current_user")
            if current_user is None and len(args) > 1:
                current_user = args[1]

            if not auth_service or not current_user:
                raise RuntimeError(
                    "Authorization service or current_user missing in context"
                )

            auth_service.ensure_permission(current_user, permission)

            return func(*args, **kwargs)

        return wrapper

    return decorator
