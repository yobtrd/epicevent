import json
from pathlib import Path


class TokenStorage:
    def __init__(self, path: Path):
        self.path = path

    def save(self, access_token: str, refresh_token: str):
        self.path.write_text(
            json.dumps(
                {
                    "access_token": access_token,
                    "refresh_token": refresh_token,
                }
            )
        )

    def get_access_token(self) -> str:
        data = json.loads(self.path.read_text())
        return data["access_token"]

    def get_refresh_token(self) -> str:
        data = json.loads(self.path.read_text())
        return data["refresh_token"]

    def clear(self):
        self.path.unlink(missing_ok=True)
