import pytest

from epicevent.cli.pagination import handle_pagination


@pytest.mark.parametrize(
    "user_choice, offset, limit, received, total, expected",
    [
        ("Q", 0, 10, 10, 50, None),
        ("N", 0, 10, 10, 50, 10),
        ("N", 40, 10, 10, 50, 40),
        ("P", 10, 10, 10, 50, 0),
        ("P", 0, 10, 10, 50, 0),
        ("X", 10, 10, 10, 50, 10),
    ],
)
def test_handle_pagination_logic(
    mocker, user_choice, offset, limit, received, total, expected
):
    mocker.patch("epicevent.cli.pagination.ask", return_value=user_choice)

    result = handle_pagination(offset, limit, received, total)

    assert result == expected
