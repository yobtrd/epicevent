from epicevent.cli.console import ask_required, display_message
from epicevent.schemas.user_schema import UserResponse


# login
#############
def display_login_resume() -> None:
    display_message("Veuillez saisir vos identifiants de connexion", "info")


def ask_user_credentials() -> dict:
    email = ask_required("Email")
    password = ask_required("Mot de passe", hide_input=True)

    return {"email": email, "password": password}


def display_login_success(user: UserResponse) -> None:
    display_message(
        f"Bienvenue {user.first_name} {user.last_name}, votre session est ouverte.",
        "success",
    )


# logout
#############
def display_logout_success() -> None:
    display_message("Votre session est fermée.", "success")
