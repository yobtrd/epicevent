from click.testing import CliRunner

from epicevent.cli.main import cli
from epicevent.exception import InvalidInputError, RolePermissionError
from tests.conftest import create_persisted_user


def test_create_user(logged_management_user):
    runner = CliRunner()

    result = runner.invoke(
        cli,
        ["user", "create"],
        input=("003\nJohn\nDoe\njohn@test.com\npassword\nSupport\n"),
    )

    assert result.exit_code == 0
    assert "L'utilisateur John Doe a été enregistré." in result.output


def test_create_user_duplicate_email_display_error(session, logged_management_user):
    runner = CliRunner()

    create_persisted_user(session, employee_number="002", email="exist@email.com")

    result = runner.invoke(
        cli,
        ["user", "create"],
        input=("003\nJohn\nDoe\nexist@email.com\npassword\nSupport\n"),
    )

    assert result.exit_code == 0
    assert "Cet email existe déjà." in result.output


def test_create_user_duplicate_emp_number_display_error(
    session, logged_management_user
):
    runner = CliRunner()

    create_persisted_user(session, employee_number="010", email="exist@email.com")

    result = runner.invoke(
        cli,
        ["user", "create"],
        input=("010\nJohn\nDoe\nexist@email.com\npassword\nSupport\n"),
    )

    assert result.exit_code == 0
    assert "Ce numéro d'employé existe déjà." in result.output


def test_create_user_with_invalid_input_raises_error(logged_management_user):
    runner = CliRunner()

    result = runner.invoke(
        cli,
        ["user", "create"],
        input=("003\nJohn\nDoe\nbademail\npassword\nGestion\n"),
    )

    assert isinstance(result.exception, InvalidInputError)
    assert result.exception.errors[0]["loc"] == ("email",)


def test_create_user_with_no_authorization(logged_sales_user):
    runner = CliRunner()

    result = runner.invoke(
        cli,
        ["user", "create"],
    )

    assert isinstance(result.exception, RolePermissionError)
