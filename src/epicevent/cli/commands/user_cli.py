import click

from epicevent.bootstrap import Application
from epicevent.cli.authentification import get_authenticated_user
from epicevent.cli.helpers import with_app
from epicevent.cli.views import user_view
from epicevent.cli.views.error_view import ErrorMessage, display_error
from epicevent.exception import (
    EmailAlreadyExistsError,
    EmployeeNumberAlreadyExistsError,
)


@click.group()
def user():
    """user commands."""
    pass


@user.command()
@with_app
def create(app: Application):
    current_user = get_authenticated_user(app)
    app.authorization.ensure_can_create_user(current_user)

    data = data = user_view.ask_user_creation_data()

    try:
        user = app.users.create_user(current_user, data)
        user_view.display_creation_success(user)
    except EmailAlreadyExistsError:
        display_error(ErrorMessage.EMAIL_ALREADY_EXISTS)
        return
    except EmployeeNumberAlreadyExistsError:
        display_error(ErrorMessage.EMPLOYEE_NUMBER_ALREADY_EXISTS)
        return
