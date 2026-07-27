import click

from epicevent.bootstrap import Application
from epicevent.cli.decorators import handle_errors, require_auth, with_app
from epicevent.cli.views import user_view
from epicevent.schemas.user_schema import UserResponse
from epicevent.security import authorization
from epicevent.security.permission import Permission


@click.group()
def user():
    """user commands."""
    pass


def _verify_target_user_exists(app: Application, employee_number: str) -> UserResponse:
    target_user = app.user_controller.verify_user_exists(employee_number)
    return target_user


@user.command()
@with_app
@handle_errors
@require_auth
def create(app: Application, current_user: UserResponse):
    authorization.ensure_permission(current_user, Permission.CREATE_USER)
    data = user_view.ask_user_creation_data()
    user = app.user_controller.create_user(current_user, data)
    user_view.display_creation_success(user)


@user.command("profile")
@with_app
@handle_errors
@require_auth
def update_self(app: Application, current_user: UserResponse):
    data = user_view.ask_user_self_data()
    if data:
        app.user_controller.update_self(current_user, data)
        user_view.display_update_self_success()
    else:
        user_view.display_update_self_cancel()


@user.command()
@click.argument("employee_number")
@with_app
@handle_errors
@require_auth
def update(app: Application, current_user: UserResponse, employee_number: str):
    authorization.ensure_permission(current_user, Permission.UPDATE_USER)
    target_user = _verify_target_user_exists(app, employee_number)
    user_view.display_user_update_resume(target_user)
    data = user_view.ask_user_update_data()
    if data:
        user = app.user_controller.update_user(
            current_user, target_user.employee_number, data
        )
        user_view.display_update_success(user)
    else:
        user_view.display_update_cancel()


@user.command()
@click.argument("employee_number")
@with_app
@handle_errors
@require_auth
def deactivate(app: Application, current_user: UserResponse, employee_number: str):
    authorization.ensure_permission(current_user, Permission.DEACTIVATE_USER)
    target_user = _verify_target_user_exists(app, employee_number)
    if user_view.ask_user_deactivate_confirmation(target_user):
        app.user_controller.deactivate_user(current_user, target_user.employee_number)
        user_view.diplay_user_deactivate_success(target_user)
    else:
        user_view.display_user_deactivate_cancel()
