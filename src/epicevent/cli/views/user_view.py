from epicevent.cli.console import ask, console
from epicevent.schemas.user_schema import UserResponse
from epicevent.security.roles import UserRole

ROLE_MAPPING = {
    "Gestion": UserRole.MANAGEMENT,
    "Commercial": UserRole.SALES,
    "Support": UserRole.SUPPORT,
}


def ask_choice(label: str, choices: list[str]) -> str:
    while True:
        value = ask(label)

        for choice in choices:
            if value.casefold() == choice.casefold():
                return choice

        console.print(
            f"Choix invalide. Valeurs possibles : {', '.join(choices)}.",
            style="error",
        )


def ask_user_creation_data():
    employee_number = ask("Numéro d'employé")
    first_name = ask("Prénom")
    last_name = ask("Nom")
    email = ask("Email")
    password = ask("Mot de passe", hide_input=True)
    role = ask_choice("Département (gestion/commercial/support)", list(ROLE_MAPPING))

    return {
        "employee_number": employee_number,
        "first_name": first_name,
        "last_name": last_name,
        "email": email,
        "password": password,
        "role_id": ROLE_MAPPING[role],
    }


def display_creation_success(user_response: UserResponse):
    console.print(
        f"L'utilisateur (n°{user_response.employee_number}) a été enregistré.",
        style="success",
    )


def ask_target_user_employee_number():
    return ask("Numéro de l'employé à mettre à jour")


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
