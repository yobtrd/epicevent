from epicevent.cli.console import ask_required, display_message
from epicevent.schemas.user_schema import UserResponse


def ask_user_credentials():
    email = ask_required("email")
    password = ask_required("password", hide_input=True)

    return {"email": email, "password": password}


def display_login_success(user: UserResponse):
    display_message(
        f"Bienvenue {user.first_name} {user.last_name}, votre session est ouverte.",
        "success",
    )


def display_logout_success():
    display_message("Votre session est fermée.", "success")
