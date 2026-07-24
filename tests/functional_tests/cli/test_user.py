from click.testing import CliRunner

from epicevent.cli.main import cli
from epicevent.security.roles import UserRole
from epicevent.services.password_service import PasswordService
from tests.conftest import create_persisted_user


# create_user
######################
def test_create_user_success(logged_user_factory):
    runner = CliRunner()
    logged_user_factory(role_id=UserRole.MANAGEMENT)
    user_emp_number = "003"

    result = runner.invoke(
        cli,
        ["user", "create"],
        input=(f"{user_emp_number}\nJane\nDoe\njane@test.com\npassword\nSupport\n"),
    )

    assert result.exit_code == 0
    assert f"L'utilisateur (n°{user_emp_number}) a été enregistré." in result.output


def test_create_user_duplicate_email_displays_error(session, logged_user_factory):
    runner = CliRunner()
    logged_user_factory(role_id=UserRole.MANAGEMENT)

    create_persisted_user(session, employee_number="002", email="exist@email.com")

    result = runner.invoke(
        cli,
        ["user", "create"],
        input=("003\nJohn\nDoe\nexist@email.com\npassword\nSupport\n"),
    )

    assert result.exit_code == 0
    assert "Cet email existe déjà." in result.output


def test_create_user_duplicate_emp_number_displays_error(session, logged_user_factory):
    runner = CliRunner()
    logged_user_factory(role_id=UserRole.MANAGEMENT)

    create_persisted_user(session, employee_number="010", email="exist@email.com")

    result = runner.invoke(
        cli,
        ["user", "create"],
        input=("010\nJohn\nDoe\nexist@email.com\npassword\nSupport\n"),
    )

    assert result.exit_code == 0
    assert "Ce numéro d'employé existe déjà." in result.output


def test_create_user_with_invalid_input_displays_error(logged_user_factory):
    runner = CliRunner()
    logged_user_factory(role_id=UserRole.MANAGEMENT)

    result = runner.invoke(
        cli,
        ["user", "create"],
        input=("003\nJohn\nDoe\nbademail\npassword\nGestion\n"),
    )

    assert result.exit_code == 0
    assert "Format invalide" in result.output
    assert "adresse email" in result.output


def test_create_user_with_no_authorization(logged_user_factory):
    runner = CliRunner()
    logged_user_factory(role_id=UserRole.SALES)

    result = runner.invoke(
        cli,
        ["user", "create"],
    )

    assert result.exit_code == 0
    assert "Vous n'avez pas les droits pour cette action." in result.output


# update
######################
def test_update_user_by_management_success(logged_user_factory, session):
    runner = CliRunner()
    logged_user_factory(role_id=UserRole.MANAGEMENT)

    target_user_emp_number = "002"
    target_user = create_persisted_user(
        session, employee_number=target_user_emp_number, role_id=UserRole.SALES
    )

    result = runner.invoke(
        cli,
        ["user", "update"],
        input=(f"{target_user_emp_number}\n5\nsupport\nq"),
    )

    assert result.exit_code == 0
    assert target_user.role_id == UserRole.SUPPORT
    assert (
        f"L'utilisateur (n°{target_user_emp_number}) a été mis à jour." in result.output
    )


def test_update_user_without_authorization_displays_error(logged_user_factory, session):
    runner = CliRunner()
    logged_user_factory(
        employee_number="001", email="sales@email.com", role_id=UserRole.SALES
    )

    target_user_emp_number = "002"
    create_persisted_user(
        session, employee_number=target_user_emp_number, password_hash="password"
    )

    result = runner.invoke(
        cli,
        ["user", "update"],
        input=(f"{target_user_emp_number}"),
    )

    assert result.exit_code == 0
    assert "Erreur: Vous n'avez pas les droits pour cette action."


# update_self
######################
def test_update_self_by_current_user_success(logged_user_factory):
    runner = CliRunner()
    password_service = PasswordService()
    current_user = logged_user_factory(
        email="old@email.com",
        password_hash=password_service.hash("oldpassword"),
        role_id=UserRole.SUPPORT,
    )

    result = runner.invoke(
        cli,
        ["user", "profile"],
        input=("\n3\nnew@test.com\n\n4\nnewpassword\nq"),
    )

    assert result.exit_code == 0
    assert current_user.email == "new@test.com"
    assert "Votre profil a été mis à jour." in result.output
    assert password_service.verify(current_user.password_hash, "newpassword")


def test_update_user_duplicate_email_displays_error(session, logged_user_factory):
    runner = CliRunner()
    logged_user_factory(
        employee_number="001", email="oldmail@email.com", role_id=UserRole.SALES
    )

    create_persisted_user(session, employee_number="002", email="exists@email.com")

    result = runner.invoke(
        cli,
        ["user", "profile"],
        input=("3\nexists@email.com\nq"),
    )

    assert result.exit_code == 0
    assert "Cet email existe déjà." in result.output
