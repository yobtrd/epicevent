from epicevent.cli.decorators import handle_errors
from epicevent.exception import (
    DatabaseError,
    EmailAlreadyExistsError,
    InvalidInputError,
)


# handle_errors
#################
def test_handle_errors_captures_unknown_application_error(mocker):
    capture = mocker.patch("epicevent.cli.decorators.capture_exception")

    @handle_errors
    def command():
        raise DatabaseError()

    command()

    capture.assert_called_once()
    assert isinstance(capture.call_args.args[0], DatabaseError)


def test_handle_errors_does_not_capture_known_application_error(mocker):
    capture = mocker.patch("epicevent.cli.decorators.capture_exception")

    @handle_errors
    def command():
        raise EmailAlreadyExistsError()

    command()

    capture.assert_not_called()


def test_handle_errors_does_not_capture_validation_error(mocker):
    capture = mocker.patch("epicevent.cli.decorators.capture_exception")

    @handle_errors
    def command():
        raise InvalidInputError([])

    command()

    capture.assert_not_called()
