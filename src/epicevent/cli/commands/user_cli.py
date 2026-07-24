import click

from epicevent.bootstrap import Application
from epicevent.cli.decorators import handle_errors, require_auth, with_app
from epicevent.cli.views import user_view
from epicevent.schemas.user_schema import UserResponse
from epicevent.security.permission import Permission


@click.group()
def user():
    """user commands."""
    pass


@user.command()
@with_app
@handle_errors
@require_auth
def create(app: Application, auth_user: UserResponse):
    app.authorization_controller.require_permission(auth_user, Permission.CREATE_USER)
    data = user_view.ask_user_creation_data()
    user_response = app.user_controller.create_user(auth_user, data)
    if user_response:
        user_view.display_creation_success(user_response)


@user.command()
@with_app
@handle_errors
@require_auth
def update(app: Application, auth_user: UserResponse):
    employee_number = user_view.ask_target_user_employee_number()
    app.authorization_controller.ensure_can_update_user(auth_user, employee_number)
    data = user_view.ask_user_update_data()
    user_response = app.user_controller.update_user(auth_user, employee_number, data)
    if user_response:
        user_view.display_update_success(user_response)
