from argon2 import PasswordHasher
from argon2.exceptions import VerificationError, VerifyMismatchError


class PasswordService:
    """Handle password hashing and verification."""

    def __init__(self) -> None:
        self.ph = PasswordHasher()

    def hash(self, password: str) -> str:
        return self.ph.hash(password)

    def verify(self, password_hash: str, password: str) -> bool:
        """
        Verify a password against a hash.

        Returns False if verification fails.
        """
        try:
            return self.ph.verify(password_hash, password)
        except (VerifyMismatchError, VerificationError):
            return False
