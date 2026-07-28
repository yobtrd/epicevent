import click

from epicevent.cli.views.error_view import display_application_error
from epicevent.exception import (
    ApplicationError,
)

from .commands.auth_cli import auth
from .commands.client_cli import client
from .commands.user_cli import user


@click.group()
def cli():
    """Epicevent CLI"""


def main():
    try:
        cli()
    except ApplicationError as error:
        display_application_error(error)


cli.add_command(auth)
cli.add_command(user)
cli.add_command(client)
