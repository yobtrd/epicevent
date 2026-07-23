from click.testing import CliRunner

from epicevent.cli.main import cli
from epicevent.exception import RolePermissionError
from epicevent.security.roles import RoleId
from tests.conftest import create_persisted_user


# create_user
######################
def test_create_user_success(logged_user_factory):
    runner = CliRunner()
    logged_user_factory(role_id=RoleId.MANAGEMENT)
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
    logged_user_factory(role_id=RoleId.MANAGEMENT)

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
    logged_user_factory(role_id=RoleId.MANAGEMENT)

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
    logged_user_factory(role_id=RoleId.MANAGEMENT)

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
    logged_user_factory(role_id=RoleId.SALES)

    result = runner.invoke(
        cli,
        ["user", "create"],
    )

    assert isinstance(result.exception, RolePermissionError)


# update_user
######################
def test_update_user_by_management_success(logged_user_factory, session):
    runner = CliRunner()
    logged_user_factory(role_id=RoleId.MANAGEMENT)

    target_user_emp_number = "002"
    create_persisted_user(
        session, employee_number=target_user_emp_number, password_hash="password"
    )

    result = runner.invoke(
        cli,
        ["user", "update"],
        input=(f"{target_user_emp_number}\nJohn\nDoe\njohn@test.com\nnewpassword"),
    )

    assert result.exit_code == 0
    assert (
        f"L'utilisateur (n°{target_user_emp_number}) a été mis à jour." in result.output
    )


def test_update_user_by_owner_success(logged_user_factory, session):
    runner = CliRunner()
    owner_user_emp_number = "002"
    logged_user_factory(employee_number=owner_user_emp_number, role_id=RoleId.SUPPORT)

    result = runner.invoke(
        cli,
        ["user", "update"],
        input=(f"{owner_user_emp_number}\nJohn\nDoe\njohn@test.com\nnewpassword"),
    )

    assert result.exit_code == 0
    assert (
        f"L'utilisateur (n°{owner_user_emp_number}) a été mis à jour." in result.output
    )


def test_update_user_with_invalid_role_and_not_owner_displays_error(
    logged_user_factory, session
):
    runner = CliRunner()
    logged_user_factory(
        employee_number="001", email="sales@email.com", role_id=RoleId.SALES
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

    assert result.exit_code == 1
    assert "Erreur: Vous n'avez pas les droits pour cette action."


def test_update_user_duplicate_email_displays_error(session, logged_user_factory):
    runner = CliRunner()
    logged_user_factory(
        employee_number="001", email="oldmail@email.com", role_id=RoleId.SALES
    )

    create_persisted_user(session, employee_number="002", email="exists@email.com")

    result = runner.invoke(
        cli,
        ["user", "update"],
        input=("001\nJohn\nDoe\nexists@email.com\npassword\nSupport\n"),
    )

    assert result.exit_code == 0
    assert "Cet email existe déjà." in result.output
