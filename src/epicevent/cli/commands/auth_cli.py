import click

from epicevent.cli.helpers import get_token_storage, with_app
from epicevent.cli.views import auth_view
from epicevent.exception import InvalidCredentialsError


@click.group()
def auth():
    """Authentication commands."""
    pass


@auth.command()
@with_app
def login(app):
    email = click.prompt("Email")
    password = click.prompt("Password", hide_input=True)

    try:
        response = app.auth.login(email, password)
    except InvalidCredentialsError:
        auth_view.display_invalid_credentials()
        return

    storage = get_token_storage()
    storage.save(response.access_token, response.refresh_token)

    auth_view.display_login_success(response.user)


@auth.command()
def logout():
    storage = get_token_storage()
    storage.clear()

    auth_view.display_logout_success()
