from epicevent.cli.main import main
from epicevent.exception import ApplicationError


def test_main_handles_application_error(mocker, capsys):
    mocker.patch(
        "epicevent.cli.main.cli",
        side_effect=ApplicationError("Message de test"),
    )

    main()

    captured = capsys.readouterr()
    assert "Erreur:" in captured.out


def test_main_displays_unexpected_error(mocker, capsys):
    class UnknownApplicationError(ApplicationError):
        pass

    mocker.patch(
        "epicevent.cli.main.cli",
        side_effect=UnknownApplicationError(),
    )

    main()

    captured = capsys.readouterr()
    assert "Erreur: Une erreur inattendue est survenue." in captured.out


def test_main_captures_unexpected_error(mocker):
    capture = mocker.patch("epicevent.cli.main.capture_exception")

    display = mocker.patch("epicevent.cli.main.display_unexpected_error")

    mocker.patch("epicevent.cli.main.cli", side_effect=RuntimeError())

    main()

    capture.assert_called_once()
    display.assert_called_once()
