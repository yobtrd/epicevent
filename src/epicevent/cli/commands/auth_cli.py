import click

from epicevent.bootstrap import Application
from epicevent.cli.decorators import with_app
from epicevent.cli.token_storage import get_token_storage
from epicevent.cli.views import auth_view
from epicevent.exception import InvalidCredentialsError


@click.group()
def auth():
    """Authentication commands."""
    pass


@auth.command()
@with_app
def login(app: Application):
    credentials = auth_view.ask_user_credentials()

    try:
        response = app.auth_controller.login(credentials)
    except InvalidCredentialsError:
        auth_view.display_credentials_error()
        return

    storage = get_token_storage()
    storage.save(response.access_token, response.refresh_token)

    auth_view.display_login_success(response.user)


@auth.command()
def logout():
    storage = get_token_storage()
    storage.clear()

    auth_view.display_logout_success()
