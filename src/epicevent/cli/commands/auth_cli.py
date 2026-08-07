import click

from epicevent.bootstrap import Application
from epicevent.cli.decorators import handle_errors, with_app
from epicevent.cli.token_storage import get_token_storage
from epicevent.cli.views import auth_view


@click.group()
def auth() -> None:
    """Gestion de l'authentification."""
    pass


@auth.command()
@with_app
@handle_errors
def login(app: Application) -> None:
    """Connexion d'un utilisateur."""
    auth_view.display_login_resume()
    credentials = auth_view.ask_user_credentials()

    auth_response = app.auth_controller.login(credentials)

    storage = get_token_storage()
    storage.save(auth_response.access_token, auth_response.refresh_token)

    auth_view.display_login_success(auth_response.user)


@auth.command()
def logout() -> None:
    """Déconnexion d'un utilisateur."""
    storage = get_token_storage()
    storage.clear()

    auth_view.display_logout_success()


@auth.command()
@with_app
@handle_errors
def test():
    print(1 / 0)
