from epicevent.bootstrap import Application
from epicevent.cli.token_storage import get_token_storage
from epicevent.exception import (
    AuthenticationError,
)
from epicevent.schemas.user_schema import UserResponse


def get_authenticated_user(app: Application) -> UserResponse:
    storage = get_token_storage()
    access = storage.get_access_token()
    refresh = storage.get_refresh_token()

    try:
        session_result = app.auth_controller.authenticate_session(access, refresh)
        if session_result.new_tokens:
            new = session_result.new_tokens
            storage.save(new.access_token, new.refresh_token)
        return session_result.user
    except AuthenticationError:
        storage.clear()
        raise
