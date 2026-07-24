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


def _get_target_user_by_employee_number(app: Application):
    while True:
        employee_number = user_view.ask_target_user_employee_number()
        if app.user_controller.verify_user_exists(employee_number):
            return employee_number
        user_view.display_employee_not_found_warning()


@user.command()
@with_app
@handle_errors
@require_auth
def create(app: Application, current_user: UserResponse):
    app.authorization_controller.require_permission(
        current_user, Permission.CREATE_USER
    )
    data = user_view.ask_user_creation_data()

    user = app.user_controller.create_user(current_user, data)
    user_view.display_creation_success(user)


@user.command()
@with_app
@handle_errors
@require_auth
def update(app: Application, current_user: UserResponse):
    target_user = _get_target_user_by_employee_number(app)
    app.authorization_controller.ensure_can_update_user(current_user, target_user)
    data = user_view.ask_user_update_data()

    user = app.user_controller.update_user(current_user, target_user, data)
    user_view.display_update_success(user)


@user.command("update-role")
@with_app
@handle_errors
@require_auth
def update_role(app: Application, current_user: UserResponse):
    app.authorization_controller.require_permission(
        current_user, Permission.UPDATE_USER_ROLE
    )
    target_user = _get_target_user_by_employee_number(app)
    new_role = user_view.ask_user_new_role()

    user = app.user_controller.update_role(current_user, target_user, new_role)
    user_view.display_update_role_success(user)
