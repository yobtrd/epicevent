from click.testing import CliRunner

from epicevents.cli.main import cli
from epicevents.models import User
from epicevents.security.roles import UserRole
from epicevents.services.password_service import PasswordService
from tests.conftest import create_persisted_user


# create_superuser
######################
def test_create_superuser_creates_management_user(session, app_factory):
    runner = CliRunner()

    result = runner.invoke(
        cli,
        [
            "user",
            "create-superuser",
        ],
        input=("001\nDoe\nJohn\nadmin@test.com\nPassword\nPassword\n"),
    )

    assert result.exit_code == 0
    assert "Le superutilisateur (admin@test.com) a bien été créé." in result.output

    user = session.query(User).filter_by(email="admin@test.com").one()

    assert user.role_id == UserRole.MANAGEMENT


def test_create_superuser_fails_when_management_exists(session, app_factory):
    runner = CliRunner()

    create_persisted_user(
        session,
        email="existing-admin@test.com",
        role_id=UserRole.MANAGEMENT,
    )

    result = runner.invoke(
        cli,
        [
            "user",
            "create-superuser",
        ],
    )

    assert result.exit_code == 0
    assert "Un superuser a déjà été créé." in result.output


# create_user
######################
def test_create_user_success(logged_user_factory, session):
    runner = CliRunner()
    logged_user_factory(role_id=UserRole.MANAGEMENT)
    user_emp_number = "003"

    result = runner.invoke(
        cli,
        ["user", "create"],
        input=(
            f"{user_emp_number}\nDoe\nJane\njane@test.com\nPassword\nPassword\nSupport\n"
        ),
    )

    assert result.exit_code == 0
    assert (
        f"L'utilisateur Doe Jane (n°{user_emp_number}) a été enregistré."
        in result.output
    )
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
        input=("003\nJohn\nDoe\nexist@email.com\nPassword\nPassword\nSupport\n"),
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
        input=("010\nJohn\nDoe\nexist@email.com\nPassword\nPassword\nSupport\n"),
    )

    assert result.exit_code == 0
    assert "Ce numéro d'employé existe déjà." in result.output
    user_in_db = session.query(User).filter_by(employee_number="002").first()
    assert user_in_db is None


def test_create_user_with_invalid_input_email_error(logged_user_factory):
    runner = CliRunner()
    logged_user_factory(role_id=UserRole.MANAGEMENT)

    result = runner.invoke(
        cli,
        ["user", "create"],
        input=("003\nJohn\nDoe\nbademail\nPassword\nPassword\nGestion\n"),
    )

    assert result.exit_code == 0
    assert "Format invalide" in result.output
    assert "adresse email" in result.output


def test_create_user_with_unconfirmed_password_display_error(logged_user_factory):
    runner = CliRunner()
    logged_user_factory(role_id=UserRole.MANAGEMENT)

    result = runner.invoke(
        cli,
        ["user", "create"],
        input=("003\nJohn\nDoe\njohn.doe@test.com\nPassword\npassword\n"),
    )

    assert result.exit_code == 1
    assert "Les mots de passe ne correspondent pas." in result.output


def test_create_user_with_invalid_password_display_error(logged_user_factory):
    runner = CliRunner()
    logged_user_factory(role_id=UserRole.MANAGEMENT)

    result = runner.invoke(
        cli,
        ["user", "create"],
        input=("003\nJohn\nDoe\njohn.doe@test.com\nshort\nshort\n"),
    )

    assert result.exit_code == 1
    assert (
        "Le mot de passe doit contenir au moins 8 caractères et une majuscule."
        in result.output
    )


def test_create_user_with_no_authorization_displays_error(logged_user_factory):
    runner = CliRunner()
    logged_user_factory(role_id=UserRole.SALES)

    result = runner.invoke(
        cli,
        ["user", "create"],
    )

    assert result.exit_code == 0
    assert "Vous n'avez pas les droits pour cette action." in result.output


# update_user
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
    password_service = PasswordService()
    logged_user_factory(
        employee_number="001", email="sales@email.com", role_id=UserRole.SALES
    )

    target_user_emp_number = "002"
    create_persisted_user(
        session,
        employee_number=target_user_emp_number,
        password_hash=password_service.hash("Password"),
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
        password_hash=password_service.hash("oldPassword"),
        role_id=UserRole.SUPPORT,
    )

    result = runner.invoke(
        cli,
        ["user", "profile"],
        input=("3\nnew@test.com\n\n4\nnewPassword\nnewPassword\nq"),
    )
    assert result.exit_code == 0
    session.refresh(current_user)
    assert current_user.email == "new@test.com"
    assert "Votre profil a été mis à jour." in result.output
    assert password_service.verify(current_user.password_hash, "newPassword")


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


# list_users
######################
def test_list_returns_users_table(
    logged_user_factory,
    session,
    force_console_width,
):
    runner = CliRunner()

    logged_user_factory(role_id=UserRole.MANAGEMENT)

    create_persisted_user(
        session,
        employee_number="002",
        first_name="Jane",
        last_name="Doe",
        email="jane@test.com",
        role_id=UserRole.SALES,
    )

    create_persisted_user(
        session,
        employee_number="003",
        first_name="John",
        last_name="Martin",
        email="john@test.com",
        role_id=UserRole.SUPPORT,
        is_active=False,
    )

    result = runner.invoke(
        cli,
        ["user", "list"],
        input="q",
    )

    assert result.exit_code == 0
    assert "Liste des collaborateurs (2 au total)" in result.output
    assert "002" in result.output
    assert "Jane" in result.output
    assert "Doe" in result.output
    assert "Commercial" in result.output

    assert "003" not in result.output
    assert "john@test.com" not in result.output
    assert "Oui" not in result.output


def test_list_with_no_user_displays_warning(logged_user_factory):
    runner = CliRunner()

    logged_user_factory(role_id=UserRole.MANAGEMENT, is_active=False)

    result = runner.invoke(
        cli,
        ["user", "list"],
    )

    assert result.exit_code == 0
    assert "Aucun collaborateur trouvé" in result.output


def test_list_pagination(
    logged_user_factory,
    session,
    force_console_width,
):
    runner = CliRunner()

    logged_user_factory(role_id=UserRole.MANAGEMENT)

    for index in range(15):
        create_persisted_user(
            session,
            employee_number=f"{index + 2:03}",
            email=f"user{index}@test.com",
        )

    result = runner.invoke(
        cli,
        ["user", "list"],
        input="n\nq",
    )

    assert result.exit_code == 0
    assert "011" in result.output


def test_list_include_inactive(
    logged_user_factory,
    session,
    force_console_width,
):
    runner = CliRunner()

    logged_user_factory(role_id=UserRole.MANAGEMENT)

    create_persisted_user(
        session,
        employee_number="002",
        email="active@test.com",
        is_active=True,
    )

    create_persisted_user(
        session,
        employee_number="003",
        email="inactive@test.com",
        is_active=False,
    )

    result = runner.invoke(
        cli,
        ["user", "list", "--include-inactive"],
        input="q",
    )

    assert result.exit_code == 0
    assert "Liste des collaborateurs (3 au total)" in result.output
    assert "002" in result.output
    assert "003" in result.output


# show_user
######################
def test_show_user_returns_user_sheet(logged_user_factory, session):
    runner = CliRunner()

    logged_user_factory(role_id=UserRole.MANAGEMENT)

    create_persisted_user(
        session,
        employee_number="002",
        first_name="Jane",
        last_name="Doe",
        email="jane@test.com",
        role_id=UserRole.SALES,
    )

    result = runner.invoke(cli, ["user", "show", "002"])

    assert result.exit_code == 0
    assert "Collaborateur n°002" in result.output
    assert "Jane Doe" in result.output
    assert "jane@test.com" in result.output
    assert "Commercial" in result.output
    assert "Actif" in result.output
    assert "Oui" in result.output


def test_show_user_with_invalid_employee_number_display_error(
    logged_user_factory, session
):
    runner = CliRunner()
    logged_user_factory(role_id=UserRole.MANAGEMENT)

    result = runner.invoke(cli, ["user", "show", "9999"])

    assert result.exit_code == 0
    assert "Erreur: L'utilisateur n'a pas été trouvé." in result.output


# deactivate_user
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
