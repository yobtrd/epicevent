from epicevent.cli.token_storage import TokenStorage


def test_save_token_create_json(tmp_path):
    token_path = tmp_path / "token.json"
    token_storage = TokenStorage(token_path)

    token_storage.save("access-token", "refresh-token")

    assert token_path.exists()


def test_get_access_token(tmp_path):
    token_storage = TokenStorage(tmp_path / "token.json")

    token_storage.save(
        "access-token",
        "refresh-token",
    )

    assert token_storage.get_access_token() == "access-token"


def test_get_refresh_token(tmp_path):
    token_storage = TokenStorage(tmp_path / "token.json")

    token_storage.save(
        "access-token",
        "refresh-token",
    )

    assert token_storage.get_refresh_token() == "refresh-token"


def test_clear_token(tmp_path):
    token_storage = TokenStorage(tmp_path / "token.json")

    token_storage.save(
        "access-token",
        "refresh-token",
    )

    token_storage.clear()

    assert not (tmp_path / "token.json").exists()


def test_get_access_token_returns_none_when_token_file_missing(tmp_path):
    token_storage = TokenStorage(tmp_path / "token.json")

    assert token_storage.get_access_token() is None


def test_get_refresh_token_returns_none_when_token_file_missing(tmp_path):
    token_storage = TokenStorage(tmp_path / "token.json")

    assert token_storage.get_refresh_token() is None


def test_get_access_token_returns_none_when_json_is_invalid(tmp_path):
    token_path = tmp_path / "token.json"
    token_path.write_text("invalid json")

    token_storage = TokenStorage(token_path)

    assert token_storage.get_access_token() is None


def test_get_refresh_token_returns_none_when_json_is_invalid(tmp_path):
    token_path = tmp_path / "token.json"
    token_path.write_text("invalid json")

    token_storage = TokenStorage(token_path)

    assert token_storage.get_refresh_token() is None


def test_get_access_token_returns_none_when_key_is_missing(tmp_path):
    token_path = tmp_path / "token.json"
    token_path.write_text("{}")

    token_storage = TokenStorage(token_path)

    assert token_storage.get_access_token() is None


def test_get_refresh_token_returns_none_when_key_is_missing(tmp_path):
    token_path = tmp_path / "token.json"
    token_path.write_text("{}")

    token_storage = TokenStorage(token_path)

    assert token_storage.get_refresh_token() is None
