from epicevent.cli.views.console import ask_required, console
from epicevent.schemas.user_schema import UserResponse


def ask_user_credentials():
    email = ask_required("email")
    password = ask_required("password", hide_input=True)

    return {"email": email, "password": password}


def display_login_success(user: UserResponse):
    console.print(
        f"Bienvenue, votre session est ouverte (Utilisateur N°{user.employee_number}).",
        style="success",
    )


def display_logout_success():
    console.print("Votre session est fermée.", style="success")
