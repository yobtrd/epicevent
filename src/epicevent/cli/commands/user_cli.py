import click

from epicevent.bootstrap import Application
from epicevent.cli.auth import get_authorized_user
from epicevent.cli.decorators import with_app
from epicevent.cli.views import user_view
from epicevent.cli.views.error_view import ErrorMessage, display_error
from epicevent.exception import (
    EmailAlreadyExistsError,
    EmployeeNumberAlreadyExistsError,
)
from epicevent.security.permission import Permission


@click.group()
def user():
    """user commands."""
    pass


@user.command()
@with_app
def create(app: Application):
    authorized_user = get_authorized_user(app, Permission.CREATE_USER)
    data = user_view.ask_user_creation_data()

    try:
        user = app.user_controller.create_user(authorized_user, data)
        user_view.display_creation_success(user)
    except EmailAlreadyExistsError:
        display_error(ErrorMessage.EMAIL_ALREADY_EXISTS)
        return
    except EmployeeNumberAlreadyExistsError:
        display_error(ErrorMessage.EMPLOYEE_NUMBER_ALREADY_EXISTS)
        return
