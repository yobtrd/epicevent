from epicevent.cli.console import ask, console
from epicevent.schemas.user_schema import UserResponse


def ask_user_credentials():
    email = ask("email")
    password = ask("password", hide_input=True)

    return {"email": email, "password": password}


def display_login_success(user: UserResponse):
    console.print(
        f"[success]Bienvenue, votre session est ouverte "
        f"(Utilisateur N°{user.employee_number}).[/success]"
    )


def display_logout_success():
    console.print("[success]Votre session est fermée.[/success]")


def display_credentials_error():
    console.print("[error]Email ou mot de passe incorrect, veuillez réessayer.[/error]")
