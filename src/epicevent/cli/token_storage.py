import json
from pathlib import Path

from epicevent.config.settings import settings


class TokenStorage:
    """Handle persistence of authentication tokens for the CLI session."""

    def __init__(self, path: Path):
        self.path = path

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

    def get_tokens(self) -> tuple[str | None, str | None]:
        """
        Load stored authentication tokens from the local session file.

        Returns:
            A tuple containing (access_token, refresh_token).
            Returns (None, None) if the session file is missing or corrupted.
        """
        try:
            data = json.loads(self.path.read_text())
            return data.get("access_token"), data.get("refresh_token")
        except (FileNotFoundError, json.JSONDecodeError):
            return None, None

    def clear(self) -> None:
        """Remove stored authentication tokens."""
        self.path.unlink(missing_ok=True)


def get_token_storage() -> TokenStorage:
    return TokenStorage(settings.token_path)
