from epicevent.cli.views.console import ask, ask_required, console
from epicevent.schemas.user_schema import UserResponse
from epicevent.security.roles import UserRole

ROLE_MAPPING = {
    "Gestion": UserRole.MANAGEMENT,
    "Commercial": UserRole.SALES,
    "Support": UserRole.SUPPORT,
}


def _ask_choice(label: str, choices: list[str]) -> str:
    while True:
        value = ask(label)

        for choice in choices:
            if value.casefold() == choice.casefold():
                return choice

        console.print(
            f"Choix invalide. Valeurs possibles : {', '.join(choices)}.",
            style="error",
        )


def _ask_for_role():
    role_labels = list(ROLE_MAPPING.keys())
    role_prompt = f"Département ({', '.join(role_labels)})"
    role_label = _ask_choice(role_prompt, role_labels)
    return role_label


def ask_user_creation_data():
    employee_number = ask_required("Numéro d'employé")
    first_name = ask_required("Prénom")
    last_name = ask_required("Nom")
    email = ask_required("Email")
    password = ask_required("Mot de passe", hide_input=True)
    role_label = _ask_for_role()
    return {
        "employee_number": employee_number,
        "first_name": first_name,
        "last_name": last_name,
        "email": email,
        "password": password,
        "role_id": ROLE_MAPPING[role_label],
    }


def display_creation_success(user_response: UserResponse):
    console.print(
        f"L'utilisateur (n°{user_response.employee_number}) a été enregistré.",
        style="success",
    )


def ask_target_user_employee_number():
    return ask_required("Numéro de l'employé à mettre à jour")


def ask_user_update_data():
    fields = {
        "1": ("first_name", "Prénom"),
        "2": ("last_name", "Nom"),
        "3": ("email", "Email"),
        "4": ("password", "Mot de passe"),
    }

    updates = {}

    while True:
        console.print("\nChoisissez le champ à modifier :", style="highlight")
        for key, (_attr, label) in fields.items():
            console.print(f"{key}. {label}")
        console.print("q. Terminer la saisie")

        choice = ask("Votre choix")

        if choice.lower() == "q":
            break

        if choice in fields:
            attr, label = fields[choice]
            value = ask(f"\nNouveau {label}")
            if value:
                updates[attr] = value
        else:
            console.print("Choix invalide", style="error")

    return updates


def display_update_success(user_response: UserResponse):
    console.print(
        f"L'utilisateur (n°{user_response.employee_number}) a été mis à jour.",
        style="success",
    )


def ask_user_new_role():
    role_label = _ask_for_role()
    return ROLE_MAPPING[role_label]


def display_update_role_success(user_response: UserResponse):
    console.print(
        f"Le role de l'utilisateur (n°{user_response.employee_number}) "
        "a été mis à jour.",
        style="success",
    )


def display_employee_not_found_warning():
    console.print("Cet employé n'existe pas. Veuillez réessayer.", style="warning")
