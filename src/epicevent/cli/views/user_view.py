import click
from rich.table import Table

from epicevent.cli.console import ask, ask_required, console, display_message
from epicevent.schemas.user_schema import UserDetailResponse, UserResponse
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


# Helpers
######################
def _ask_choice(label: str, choices: list[str]) -> str:
    while True:
        value = ask_required(label).strip()

        if not value:
            console.print("Veuillez saisir un département.", style="warning")
            continue

        for choice in choices:
            if value.casefold() == choice.casefold():
                return choice

        console.print(
            f"Choix invalide. Valeurs possibles : {', '.join(choices)}.",
            style="warning",
        )


def _ask_for_role():
    role_labels = list(ROLE_MAPPING.keys())
    role_prompt = f"Département ({', '.join(role_labels)})"
    role_label = _ask_choice(role_prompt, role_labels)
    return role_label


def _ask_update_menu(fields: dict[str, tuple[str, str]]) -> dict:
    updates = {}
    while True:
        console.print("\nChoisissez le champ à modifier :", style="highlight")
        for key, (_, label) in fields.items():
            console.print(f"{key}. {label}")
        console.print("q. Terminer la saisie")

        choice = ask("Votre choix").strip()
        if choice.lower() == "q":
            break

        if choice == "5" and "role" in [f[0] for f in fields.values()]:
            role_label = _ask_for_role()
            updates["role_id"] = ROLE_MAPPING[role_label]
            continue

        if choice in fields:
            attr, label = fields[choice]
            kwargs = {"hide_input": True} if attr == "password" else {}
            value = ask(f"\nNouveau {label.lower()}", **kwargs)

            if value:
                updates[attr] = value
        else:
            console.print("Choix invalide", style="warning")
    return updates


# create-superuser
######################
def display_superuser_creation_success(superuser: UserResponse):
    display_message(
        f"Le superutilisateur ({superuser.email}) a bien été créé.",
        "success",
    )


# create
######################
def ask_user_creation_data(include_role: bool = True) -> dict:
    employee_number = ask_required("Numéro d'employé")
    last_name = ask_required("Nom")
    first_name = ask_required("Prénom")
    email = ask_required("Email")
    password = ask_required("Mot de passe", hide_input=True)

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


def display_creation_success(user_response: UserResponse):
    display_message(
        f"L'utilisateur (n°{user_response.employee_number}) a été enregistré.",
        "success",
    )


# update
######################
def display_user_update_resume(target_user: UserResponse):
    display_message(
        f"Mis à jour de l'employée {target_user.last_name} {target_user.first_name}",
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


def display_update_success(target_user: UserResponse):
    display_message(
        f"L'utilisateur (n°{target_user.employee_number}) a été mis à jour.",
        "success",
    )


def display_update_cancel():
    display_message("La mise à jour de l'utilisateur a été annulée.", "info")


# update_self
######################
def ask_user_self_data() -> dict:
    fields = {
        "1": ("first_name", "Prénom"),
        "2": ("last_name", "Nom"),
        "3": ("email", "Email"),
        "4": ("password", "Mot de passe"),
    }
    return _ask_update_menu(fields)


def display_update_self_success():
    display_message("Votre profil a été mis à jour.", "success")


def display_update_self_cancel():
    display_message("Votre profil n'a pas été modifié.", "info")


# list
#################
def display_users_table(users_list: list[UserDetailResponse], total_count: int):
    table = Table(title=f"\nListe des collaborateurs ({total_count} au total)")
    table.add_column("Numéro d'employé")
    table.add_column("Nom")
    table.add_column("Prénom")
    table.add_column("Email")
    table.add_column("Role")
    table.add_column("Actif")

    for user in users_list:
        role_label = ROLE_LABELS.get(user.role_id, "Inconnu")
        active = "Activé" if user.is_active else "Désactivé"
        table.add_row(
            user.employee_number,
            user.first_name,
            user.last_name,
            user.email,
            role_label,
            active,
        )

    console.print(table)


def display_users_list_empty_message():
    display_message("Aucun collaborateur trouvé", "warning")


# deactivate
######################
def ask_user_deactivate_confirmation(target_user: UserResponse) -> bool:
    display_message(
        f"Êtes-vous sûr de vouloir désactiver l'utilisateur {target_user.first_name} "
        f"{target_user.last_name} (n°{target_user.employee_number}) ?",
        "error",
    )
    return click.confirm("Entrer [Y] pour confirmer, [N] pour annuler")


def diplay_user_deactivate_success(target_user: UserResponse):
    display_message(
        f"L'utilisateur (n°{target_user.employee_number}) a bien été désactivé.",
        "success",
    )


def display_user_deactivate_cancel():
    display_message("L'opération de désactivation a été annulée.", "info")
