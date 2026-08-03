import click

from epicevent.bootstrap import Application
from epicevent.cli.decorators import handle_errors, require_auth, with_app
from epicevent.cli.pagination import handle_pagination
from epicevent.cli.views import user_view
from epicevent.schemas.user_schema import UserResponse
from epicevent.security import authorization
from epicevent.security.permission import Permission


@click.group()
def user():
    """user commands."""
    pass


@user.command("create-superuser")
@with_app
@handle_errors
def create_superuser(app: Application):
    app.user_controller.ensure_can_create_superuser()

    data = user_view.ask_user_creation_data(include_role=False)
    superuser = app.user_controller.create_superuser(data)
    user_view.display_superuser_creation_success(superuser)


@user.command()
@with_app
@handle_errors
@require_auth
def create(app: Application, current_user: UserResponse):
    authorization.ensure_permission(current_user, Permission.CREATE_USER)

    data = user_view.ask_user_creation_data()
    user = app.user_controller.create_user(current_user, data)
    user_view.display_user_creation_success(user)


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
    target_user = app.user_controller.get_user_by_employee_number(employee_number)

    user_view.display_user_update_resume(target_user)
    data = user_view.ask_user_update_data()
    if data:
        updated_user = app.user_controller.update_user(
            current_user,
            employee_number,
            data,
        )
        user_view.display_user_update_success(updated_user)
    else:
        user_view.display_user_update_cancel()


@user.command()
@click.option("--include-inactive", is_flag=True)
@with_app
@handle_errors
@require_auth
def list(app: Application, current_user: UserResponse, include_inactive: bool):
    authorization.ensure_permission(current_user, Permission.LIST_USER)

    offset = 0
    limit = 10
    while True:
        users_list, total_count = app.user_controller.list_users(
            current_user,
            include_inactive=include_inactive,
            limit=limit,
            offset=offset,
        )
        if not users_list and offset == 0:
            user_view.display_users_list_empty_message()
            return

        user_view.display_users_table(users_list, total_count)

        new_offset = handle_pagination(
            offset=offset,
            limit=limit,
            received_count=len(users_list),
            total_count=total_count,
        )
        if new_offset is None:
            break
        offset = new_offset


@user.command()
@click.argument("employee_number")
@with_app
@handle_errors
@require_auth
def deactivate(app: Application, current_user: UserResponse, employee_number: str):
    authorization.ensure_permission(current_user, Permission.DEACTIVATE_USER)
    target_user = app.user_controller.get_user_by_employee_number(employee_number)

    if user_view.ask_user_deactivate_confirmation(target_user):
        deactivated_user = app.user_controller.deactivate_user(
            current_user,
            employee_number,
        )
        user_view.diplay_user_deactivate_success(deactivated_user)
    else:
        user_view.display_user_deactivate_cancel()
