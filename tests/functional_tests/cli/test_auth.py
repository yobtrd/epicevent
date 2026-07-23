import json

from click.testing import CliRunner

from epicevent.cli.main import cli
from epicevent.services.password_service import PasswordService
from tests.conftest import create_persisted_user


def test_login_with_correct_credentials(session, token_path, app_factory):
    runner = CliRunner()
    user = create_persisted_user(
        session,
        email="test@email.com",
        password_hash=PasswordService().hash("password"),
    )

    result = runner.invoke(
        cli,
        [
            "auth",
            "login",
        ],
        input="test@email.com\npassword\n",
        color=False,
    )

    assert result.exit_code == 0
    assert (
        f"Bienvenue, votre session est ouverte (Utilisateur N°{user.employee_number})."
        in result.output
    )
    assert token_path.exists()

    with open(token_path) as f:
        tokens = json.load(f)
    assert "access_token" in tokens
    assert "refresh_token" in tokens


def test_login_with_incorrect_email(session, token_path, app_factory):
    runner = CliRunner()
    create_persisted_user(
        session,
        email="test@email.com",
        password_hash=PasswordService().hash("password"),
    )

    result = runner.invoke(
        cli,
        [
            "auth",
            "login",
        ],
        input="bad@email.com\npassword\n",
    )

    assert result.exit_code == 0
    assert "Email ou mot de passe incorrect, veuillez réessayer" in result.output


def test_login_with_incorrect_password(session, token_path, app_factory):
    runner = CliRunner()
    create_persisted_user(
        session,
        email="test@email.com",
        password_hash=PasswordService().hash("password"),
    )

    result = runner.invoke(
        cli,
        [
            "auth",
            "login",
        ],
        input="test@email.com\nbadpassword\n",
    )

    assert result.exit_code == 0
    assert "Email ou mot de passe incorrect, veuillez réessayer" in result.output


def test_logout(token_path):
    runner = CliRunner()

    result = runner.invoke(
        cli,
        [
            "auth",
            "logout",
        ],
    )

    assert result.exit_code == 0
    assert "Votre session est fermée." in result.output
