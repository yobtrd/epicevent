from rich.console import Console

from epicevent.schemas.user import UserResponse

console = Console()


def display_login_success(user: UserResponse):
    console.print(
        f"[green]Bienvenue {user.first_name}, votre session est ouverte.[/green]"
    )


def display_invalid_credentials():
    console.print("[red]Email ou mot de passe incorrect, veuillez réessayer[/red]")


def display_logout_success():
    console.print("[red]Votre session est fermée.[/red]")
