import json
from pathlib import Path

from epicevent.exception import InvalidSessionError


class TokenStorage:
    def __init__(self, path: Path):
        self.path = path

    def save(self, access_token: str, refresh_token: str):
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

    def get_access_token(self) -> str:
        try:
            data = json.loads(self.path.read_text())
            return data["access_token"]
        except (FileNotFoundError, json.JSONDecodeError, KeyError) as exc:
            raise InvalidSessionError() from exc

    def get_refresh_token(self) -> str:
        try:
            data = json.loads(self.path.read_text())
            return data["refresh_token"]
        except (FileNotFoundError, json.JSONDecodeError, KeyError) as exc:
            raise InvalidSessionError() from exc

    def clear(self):
        self.path.unlink(missing_ok=True)
