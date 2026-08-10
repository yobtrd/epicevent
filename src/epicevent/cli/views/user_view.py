import click
from pydantic import ValidationError
from rich.panel import Panel
from rich.table import Table

from epicevent.cli.console import ask, ask_required, console, display_message
from epicevent.schemas.user_schema import (
    UserDetailResponse,
    UserResponse,
    password_validator,
)
from epicevent.security.roles import UserRole

ROLE_MAPPING = {
    "Gestion": UserRole.MANAGEMENT,
    "Commercial": UserRole.SALES,
    "Support": UserRole.SUPPORT,
}

ROLE_LABELS = {
    UserRole.MANAGEMENT: "Gestion",
    UserRole.SALES: "Commercial",
    UserRole.SUPPORT: "Support",
}


# helpers
######################
def _ask_for_password() -> str:
    """
    Prompt for a password and validate its confirmation.

    Returns:
        The validated password.
    """
    while True:
        password = ask_required("Mot de passe", hide_input=True)
        try:
            password_validator.validate_python(password)
        except ValidationError:
            display_message(
                "Le mot de passe doit contenir au moins 8 caractères et une majuscule.",
                "warning",
            )
            continue

        confirm = ask_required("Confirmer le mot de passe", hide_input=True)

        if password != confirm:
            display_message("Les mots de passe ne correspondent pas.", "warning")
            continue
        else:
            return password


def _ask_for_role() -> str:
    """
    Prompt for a user role and return the selected role label.

    Returns:
        The selected role label.
    """
    role_labels = list(ROLE_MAPPING.keys())
    role_prompt = f"Département ({', '.join(role_labels)})"
    while True:
        value = ask_required(role_prompt).strip()

        if not value:
            console.print("Veuillez saisir un département.", style="warning")
            continue

        for role_label in role_labels:
            if value.casefold() == role_label.casefold():
                return role_label

        console.print(
            f"Choix invalide. Valeurs possibles : {', '.join(role_labels)}.",
            style="warning",
        )


def _ask_update_menu(fields: dict[str, tuple[str, str]]) -> dict:
    """
    Display a dynamic update menu and collect modified fields.

    Args:
        fields: Mapping of menu choices to model attributes and display labels.

    Returns:
        Updated fields ready to be validated by the controller.
    """
    updates = {}
    while True:
        console.print("\nChoisissez le champ à modifier :", style="highlight")
        for key, (_, label) in fields.items():
            console.print(f"{key}. {label}")
        console.print("q. Terminer la saisie")

        choice = ask("Votre choix")
        if choice.lower() == "q":
            break

        if choice in fields:
            attr, label = fields[choice]

            if attr == "role":
                role_label = _ask_for_role()
                updates["role_id"] = ROLE_MAPPING[role_label]
                continue

            if attr == "password":
                password = _ask_for_password()
                updates["password"] = password
                continue

            value = ask(f"\nNouveau {label.lower()}")

            if value:
                updates[attr] = value
        else:
            console.print("Choix invalide", style="warning")
    return updates


# create_superuser
######################
def display_superuser_create_resume() -> None:
    display_message("Création du superutilisateur", "info")


def display_superuser_creation_success(superuser: UserResponse) -> None:
    display_message(
        f"Le superutilisateur ({superuser.email}) a bien été créé.",
        "success",
    )


# create_user
######################
def display_user_create_resume() -> None:
    display_message("Création d'un nouvel utilisateur", "info")


def ask_user_creation_data(include_role: bool = True) -> dict:
    """
    Collect user/superuser creation data from CLI inputs.

    Args:
        include_role: Whether the role selection should be requested
        (= False for superuser).

    Returns:
        Raw user data collected from the CLI.
    """
    employee_number = ask_required("Numéro d'employé")
    last_name = ask_required("Nom de famille")
    first_name = ask_required("Prénom")
    email = ask_required("Email")
    password = _ask_for_password()

    data = {
        "employee_number": employee_number,
        "last_name": last_name,
        "first_name": first_name,
        "email": email,
        "password": password,
    }

    if include_role:
        role_label = _ask_for_role()
        data["role_id"] = ROLE_MAPPING[role_label]

    return data


def display_user_creation_success(user: UserResponse) -> None:
    display_message(
        f"L'utilisateur {user.last_name} {user.first_name} "
        f"(n°{user.employee_number}) a été enregistré.",
        "success",
    )


# update_self
######################
def display_update_self_resume() -> None:
    display_message("Mise à jour de votre profil", "info")


def ask_user_self_data() -> dict:
    fields = {
        "1": ("first_name", "Prénom"),
        "2": ("last_name", "Nom"),
        "3": ("email", "Email"),
        "4": ("password", "Mot de passe"),
    }
    return _ask_update_menu(fields)


def display_update_self_success() -> None:
    display_message("Votre profil a été mis à jour.", "success")


def display_update_self_cancel() -> None:
    display_message("Votre profil n'a pas été modifié.", "info")


# update_user
######################
def display_user_update_resume(target_user: UserResponse) -> None:
    display_message(
        f"Mise à jour de l'employée {target_user.last_name} {target_user.first_name}",
        "info",
    )


def ask_user_update_data() -> dict:
    fields = {
        "1": ("employee_number", "Numéro d'employé"),
        "2": ("first_name", "Prénom"),
        "3": ("last_name", "Nom"),
        "4": ("email", "Email"),
        "5": ("role", "Role"),
    }
    return _ask_update_menu(fields)


def display_user_update_success(user: UserResponse) -> None:
    display_message(
        f"L'utilisateur (n°{user.employee_number}) a été mis à jour.",
        "success",
    )


def display_user_update_cancel() -> None:
    display_message("La mise à jour de l'utilisateur a été annulée.", "info")


# list_users
#################
def display_users_table(users_list: list[UserResponse], total_count: int) -> None:
    """
    Display users in a formatted table.

    Args:
        users_list: Users to display.
        total_count: Total number of users matching the query.
    """
    table = Table(title=f"\nListe des collaborateurs ({total_count} au total)")
    table.add_column("Matricule")
    table.add_column("Nom")
    table.add_column("Prénom")
    table.add_column("Département")

    for user in users_list:
        role_label = ROLE_LABELS.get(user.role_id)
        table.add_row(
            user.employee_number,
            user.last_name,
            user.first_name,
            role_label,
        )

    console.print(table)


def display_users_list_empty_message() -> None:
    display_message("Aucun collaborateur trouvé", "warning")


# show_user
######################
def display_user_details(user: UserDetailResponse) -> None:
    table = Table(show_header=False, box=None)

    table.add_column(style="highlight")

    table.add_row("Matricule:", user.employee_number)
    table.add_row("Nom complet:", f"{user.first_name} {user.last_name}")
    table.add_row("Email:", user.email)
    table.add_row("Département: ", ROLE_LABELS.get(user.role_id))
    table.add_row("Actif:", "Oui" if user.is_active else "Non")

    console.print(
        "",
        Panel(
            table,
            expand=False,
            title=f"[italic]Collaborateur n°{user.employee_number}[/italic]",
        ),
    )


# deactivate_user
######################
def ask_user_deactivate_confirmation(target_user: UserResponse) -> bool:
    display_message(
        f"Êtes-vous sûr de vouloir désactiver l'utilisateur {target_user.first_name} "
        f"{target_user.last_name} (n°{target_user.employee_number}) ?",
        "error",
    )
    return click.confirm("Entrer [Y] pour confirmer, [N] pour annuler")


def display_user_deactivate_success(user: UserResponse) -> None:
    display_message(
        f"L'utilisateur (n°{user.employee_number}) a bien été désactivé.",
        "success",
    )


def display_user_deactivate_cancel() -> None:
    display_message("L'opération de désactivation a été annulée.", "info")
