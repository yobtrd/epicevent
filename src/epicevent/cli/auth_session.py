from epicevent.bootstrap import Application
from epicevent.cli.token_storage import get_token_storage
from epicevent.exception import (
    AuthenticationError,
)
from epicevent.schemas.user_schema import UserResponse


def get_authenticated_user(app: Application) -> UserResponse:
    """
    Retrieve the authenticated user from the current CLI session.

    Refreshes and stores tokens when the session is renewed.

    Raises:
        AuthenticationError: If the session cannot be authenticated.
    """
    storage = get_token_storage()
    access_token, refresh_token = storage.get_tokens()

    try:
        session_result = app.auth_controller.authenticate_session(
            access_token,
            refresh_token,
        )
        if session_result.new_tokens:
            new = session_result.new_tokens
            storage.save(new.access_token, new.refresh_token)
        return session_result.user
    except AuthenticationError:
        storage.clear()
        raise
