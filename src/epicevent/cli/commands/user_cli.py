import click

from epicevent.bootstrap import Application
from epicevent.cli.decorators import handle_errors, require_auth, with_app
from epicevent.cli.pagination import handle_pagination
from epicevent.cli.views import user_view
from epicevent.schemas.user_schema import UserResponse
from epicevent.security import authorization
from epicevent.security.permission import Permission


@click.group()
def user() -> None:
    """Gestion des utilisateurs."""
    pass


@user.command("create-superuser")
@with_app
@handle_errors
def create_superuser(app: Application) -> None:
    """Créer le superutilisateur."""
    app.user_controller.ensure_can_create_superuser()

    user_view.display_superuser_create_resume()
    data = user_view.ask_user_creation_data(include_role=False)

    superuser = app.user_controller.create_superuser(data)
    user_view.display_superuser_creation_success(superuser)


@user.command("create")
@with_app
@handle_errors
@require_auth
def create_user(app: Application, current_user: UserResponse) -> None:
    """Créer un nouvel utilisateur."""
    authorization.ensure_permission(current_user, Permission.CREATE_USER)

    user_view.display_user_create_resume()
    data = user_view.ask_user_creation_data()

    user = app.user_controller.create_user(current_user, data)
    user_view.display_user_creation_success(user)


@user.command("profile")
@with_app
@handle_errors
@require_auth
def update_self(app: Application, current_user: UserResponse) -> None:
    """Mettre à jour son profil utilisateur."""
    user_view.display_update_self_resume()
    data = user_view.ask_user_self_data()
    if data:
        app.user_controller.update_self(current_user, data)
        user_view.display_update_self_success()
    else:
        user_view.display_update_self_cancel()


@user.command("update")
@click.argument("employee_number")
@with_app
@handle_errors
@require_auth
def update_user(
    app: Application,
    current_user: UserResponse,
    employee_number: str,
) -> None:
    """Mettre à jour un utilisateur à partir de son matricule."""
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


@user.command("list")
@click.option(
    "--include-inactive",
    help="Inclut les utillisateurs désactivés",
    is_flag=True,
)
@with_app
@handle_errors
@require_auth
def list_user(
    app: Application,
    current_user: UserResponse,
    include_inactive: bool,
) -> None:
    """Lister les utilisateurs."""
    authorization.ensure_permission(current_user, Permission.LIST_USERS)

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


@user.command("show")
@click.argument("employee_number")
@with_app
@handle_errors
@require_auth
def show_user(
    app: Application,
    current_user: UserResponse,
    employee_number: str,
) -> None:
    """Afficher un utilisateur."""
    authorization.ensure_permission(current_user, Permission.SHOW_USER)

    user = app.user_controller.show_user(current_user, employee_number)
    user_view.display_user_details(user)


@user.command("deactivate")
@click.argument("employee_number")
@with_app
@handle_errors
@require_auth
def deactivate_user(
    app: Application,
    current_user: UserResponse,
    employee_number: str,
) -> None:
    """Désactiver un utilisateur à partir de son matricule."""
    authorization.ensure_permission(current_user, Permission.DEACTIVATE_USER)
    target_user = app.user_controller.get_user_by_employee_number(employee_number)

    if user_view.ask_user_deactivate_confirmation(target_user):
        deactivated_user = app.user_controller.deactivate_user(
            current_user,
            employee_number,
        )
        user_view.display_user_deactivate_success(deactivated_user)
    else:
        user_view.display_user_deactivate_cancel()
