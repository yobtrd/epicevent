from epicevent.cli.console import ask, console
from epicevent.schemas.user_schema import UserResponse
from epicevent.security.roles import RoleId

ROLE_MAPPING = {
    "Gestion": RoleId.MANAGEMENT,
    "Commercial": RoleId.SALES,
    "Support": RoleId.SUPPORT,
}


def ask_choice(label: str, choices: list[str]) -> str:
    while True:
        value = ask(label)

        for choice in choices:
            if value.casefold() == choice.casefold():
                return choice

        console.print(
            f"[error]Choix invalide. Valeurs possibles : {', '.join(choices)}.[/error]"
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


def display_creation_success(user: UserResponse):
    console.print(
        f"[success]L'utilisateur {user.first_name} {user.last_name} "
        "a été enregistré.[/success]"
    )
