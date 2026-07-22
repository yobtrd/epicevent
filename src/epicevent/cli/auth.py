import epicevent.bootstrap as bootstrap
from epicevent.bootstrap import Application
from epicevent.cli.token_storage import get_token_storage
from epicevent.exception import (
    AuthenticationError,
    ExpiredTokenError,
    InvalidSessionError,
    InvalidTokenError,
)
from epicevent.schemas.user_schema import UserResponse
from epicevent.security.permission import Permission


def get_authenticated_user(app: bootstrap.Application) -> UserResponse:
    storage = get_token_storage()
    try:
        access_token = storage.get_access_token()
        user = app.auth_controller.get_current_user(access_token)
        return user
    except ExpiredTokenError:
        try:
            refresh_token = storage.get_refresh_token()
            response = app.auth_controller.refresh_session(refresh_token)
            storage.save(response.access_token, response.refresh_token)
            return response.user
        except (InvalidSessionError, InvalidTokenError, ExpiredTokenError) as exc:
            storage.clear()
            raise AuthenticationError() from exc


def get_authorized_user(app: Application, permission: Permission):
    current_user = get_authenticated_user(app)
    app.authorization_controller.require_permission(current_user, permission)
    return current_user
