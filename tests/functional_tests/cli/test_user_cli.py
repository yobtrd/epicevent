from click.testing import CliRunner

from epicevent.cli.main import cli
from epicevent.models import User
from epicevent.security.roles import UserRole
from epicevent.services.password_service import PasswordService
from tests.conftest import create_persisted_user


# create
######################
def test_create_user_success(logged_user_factory, session):
    runner = CliRunner()
    logged_user_factory(role_id=UserRole.MANAGEMENT)
    user_emp_number = "003"

    result = runner.invoke(
        cli,
        ["user", "create"],
        input=(f"{user_emp_number}\nDoe\nJane\njane@test.com\npassword\nSupport\n"),
    )

    assert result.exit_code == 0
    assert f"L'utilisateur (n°{user_emp_number}) a été enregistré." in result.output
    created_user = (
        session.query(User).filter_by(employee_number=user_emp_number).first()
    )
    assert created_user is not None
    assert created_user.email == "jane@test.com"
    assert created_user.last_name == "Doe"
    assert created_user.role_id == UserRole.SUPPORT


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
    user_in_db = session.query(User).filter_by(employee_number="002").first()
    assert user_in_db is None


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


def test_create_user_with_no_authorization_displays_error(logged_user_factory):
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

    target_user = create_persisted_user(
        session, employee_number="002", role_id=UserRole.SALES
    )

    result = runner.invoke(
        cli,
        ["user", "update", "002"],
        input=("5\nsupport\nq"),
    )

    assert result.exit_code == 0
    session.refresh(target_user)
    assert target_user.role_id == UserRole.SUPPORT
    assert "L'utilisateur (n°002) a été mis à jour." in result.output


def test_update_duplicate_emp_number_display_error(logged_user_factory, session):
    runner = CliRunner()
    logged_user_factory(role_id=UserRole.MANAGEMENT)

    create_persisted_user(session, employee_number="002", role_id=UserRole.SALES)
    create_persisted_user(
        session,
        email="another@email.com",
        employee_number="003",
        role_id=UserRole.SALES,
    )

    result = runner.invoke(
        cli,
        ["user", "update", "002"],
        input=("1\n003\nq"),
    )

    assert result.exit_code == 0
    assert "Ce numéro d'employé existe déjà." in result.output


def test_update_user_without_authorization_displays_error(logged_user_factory, session):
    runner = CliRunner()
    logged_user_factory(
        employee_number="001", email="sales@email.com", role_id=UserRole.SALES
    )

    target_user_emp_number = "002"
    create_persisted_user(
        session, employee_number=target_user_emp_number, password_hash="password"
    )

    result = runner.invoke(cli, ["user", "update", target_user_emp_number])

    assert result.exit_code == 0
    assert "Vous n'avez pas les droits pour cette action."


def test_update_user_cancel_displays_cancel_message(
    logged_user_factory,
    session,
):
    runner = CliRunner()

    logged_user_factory(role_id=UserRole.MANAGEMENT)

    user = create_persisted_user(session, first_name="John")

    result = runner.invoke(
        cli,
        ["user", "update", user.employee_number],
        input="q\n",
    )

    assert result.exit_code == 0

    session.refresh(user)

    assert user.first_name == "John"
    assert "La mise à jour de l'utilisateur a été annulée." in result.output


# update_self
######################
def test_update_self_by_current_user_success(logged_user_factory, session):
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
        input=("3\nnew@test.com\n\n4\nnewpassword\nq"),
    )
    assert result.exit_code == 0
    session.refresh(current_user)
    assert current_user.email == "new@test.com"
    assert "Votre profil a été mis à jour." in result.output
    assert password_service.verify(current_user.password_hash, "newpassword")


def test_update_user_duplicate_email_displays_error(logged_user_factory, session):
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


def test_update_self_cancel_deiplays_cancel_message(logged_user_factory, session):
    runner = CliRunner()
    current_user = logged_user_factory(
        email="support@email.com",
        role_id=UserRole.SUPPORT,
    )

    result = runner.invoke(
        cli,
        ["user", "profile"],
        input=("q\n"),
    )

    assert result.exit_code == 0

    session.refresh(current_user)

    assert current_user.email == "support@email.com"
    assert "Votre profil n'a pas été modifié." in result.output


# deactivate
######################
def test_deactivate_user_success(logged_user_factory, session):
    runner = CliRunner()
    logged_user_factory(role_id=UserRole.MANAGEMENT)

    user = create_persisted_user(session, employee_number="002")

    result = runner.invoke(
        cli,
        ["user", "deactivate", "002"],
        input=("y"),
    )

    assert result.exit_code == 0
    session.refresh(user)
    assert user.is_active is False
    assert "L'utilisateur (n°002) a bien été désactivé."


def test_deactivate_user_cancel_success(logged_user_factory, session):
    runner = CliRunner()
    logged_user_factory(role_id=UserRole.MANAGEMENT)

    user = create_persisted_user(session, employee_number="002")

    result = runner.invoke(
        cli,
        ["user", "deactivate", "002"],
        input=("n"),
    )

    assert result.exit_code == 0
    session.refresh(user)
    assert user.is_active is True
    assert "L'opération de désactivation a été annulée."


def test_deactivate_user_already_deactivated_displays_error(
    logged_user_factory, session
):
    runner = CliRunner()
    logged_user_factory(role_id=UserRole.MANAGEMENT)

    user = create_persisted_user(session, employee_number="002", is_active=False)

    result = runner.invoke(
        cli,
        ["user", "deactivate", "002"],
        input=("y"),
    )

    assert result.exit_code == 0
    session.refresh(user)
    assert user.is_active is False
    assert "Cet utilisateur est déjà désactivé"


def test_deactivate_user_unauthorized_displays_error(logged_user_factory, session):
    runner = CliRunner()
    logged_user_factory(role_id=UserRole.SUPPORT)

    user = create_persisted_user(session, employee_number="002")

    result = runner.invoke(cli, ["user", "deactivate", "002"])

    assert result.exit_code == 0
    session.refresh(user)
    assert user.is_active is True
    assert "Vous n'avez pas les droits pour cette action."
