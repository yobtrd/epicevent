from epicevent.cli.main import main
from epicevent.exception import (
    AuthenticationError,
    AuthorizationError,
    InvalidInputError,
)


def test_main_displays_authorization_error(mocker, capsys):
    mocker.patch(
        "epicevent.cli.main.cli",
        side_effect=AuthorizationError(),
    )

    main()

    captured = capsys.readouterr()

    assert "Vous n'avez pas les droits pour cette action." in captured.out


def test_main_displays_authentication_error(mocker, capsys):
    mocker.patch(
        "epicevent.cli.main.cli",
        side_effect=AuthenticationError(),
    )

    main()

    captured = capsys.readouterr()

    assert "Vous n'êtes pas connecté à une session." in captured.out


def test_main_displays_invalid_input_error(mocker, capsys):
    error = InvalidInputError(
        [
            {
                "loc": ("email",),
                "type": "value_error",
            }
        ]
    )

    mocker.patch(
        "epicevent.cli.main.cli",
        side_effect=error,
    )

    main()

    captured = capsys.readouterr()

    assert "Erreur sur le champ email" in captured.out
