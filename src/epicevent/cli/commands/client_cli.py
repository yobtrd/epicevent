import click

from epicevent.bootstrap import Application
from epicevent.cli.decorators import handle_errors, require_auth, with_app
from epicevent.cli.views import client_view
from epicevent.schemas.user_schema import UserResponse
from epicevent.security import authorization
from epicevent.security.permission import Permission


@click.group()
def client():
    """client commands."""
    pass


@client.command()
@with_app
@handle_errors
@require_auth
def create(app: Application, current_user: UserResponse):
    authorization.ensure_permission(current_user, Permission.CREATE_CLIENT)
    data = client_view.ask_client_creation_data()
    client = app.client_controller.create_client(current_user, data)
    client_view.display_creation_success(client)
