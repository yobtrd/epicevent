import click

from epicevent.exception import (
    ApplicationError,
    AuthenticationError,
    AuthorizationError,
)

from .commands.auth_cli import auth
from .commands.user_cli import user
from .views.error_view import ErrorMessage, display_error


@click.group()
def cli():
    """Epicevent CLI"""


def main():
    try:
        cli()
    except AuthenticationError:
        display_error(ErrorMessage.NOT_AUTHENTICATED)
    except AuthorizationError:
        display_error(ErrorMessage.NOT_AUTHORIZED)
    # except UserNotFoundError:
    #     display_error(ErrorMessage.USER_NOT_FOUND)
    # except InvalidInputError as e:
    #     display_invalid_input_error(e)
    except ApplicationError:
        display_error(ErrorMessage.UNKNOWN)


cli.add_command(auth)
cli.add_command(user)
