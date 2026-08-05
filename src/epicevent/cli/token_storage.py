import json
from pathlib import Path

from epicevent import config


class TokenStorage:
    """
    Handle persistence of authentication tokens for the CLI session.
    """

    def __init__(self, path: Path):
        self.path = path

    def _load(self) -> dict:
        """
        Load stored tokens from the storage file.

        Returns an empty dictionary if the storage is unavailable.
        """
        try:
            return json.loads(self.path.read_text())
        except (FileNotFoundError, json.JSONDecodeError):
            return {}

    def save(self, access_token: str, refresh_token: str) -> None:
        """Store authentication tokens locally."""
        self.path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        self.path.write_text(
            json.dumps(
                {
                    "access_token": access_token,
                    "refresh_token": refresh_token,
                }
            )
        )

    def get_access_token(self) -> str | None:
        return self._load().get("access_token")

    def get_refresh_token(self) -> str | None:
        return self._load().get("refresh_token")

    def clear(self) -> None:
        """Remove stored authentication tokens."""
        self.path.unlink(missing_ok=True)


def get_token_storage() -> TokenStorage:
    return TokenStorage(config.TOKEN_PATH)
