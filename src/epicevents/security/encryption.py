from typing import Any

from cryptography.hazmat.primitives.ciphers.aead import AESSIV
from sqlalchemy.types import Text, TypeDecorator

from epicevents.config.settings import get_settings


class EncryptedString(TypeDecorator[str]):
    """SQLAlchemy type that transparently encrypts and decrypts strings."""

    impl = Text
    cache_ok = True
    cipher_instance: AESSIV | None = None

    @property
    def _cipher(self) -> AESSIV:
        """Return the AES-SIV cipher using the configured encryption key."""
        if EncryptedString.cipher_instance is None:
            key = bytes.fromhex(get_settings().encryption_key)
            EncryptedString.cipher_instance = AESSIV(key)
        return EncryptedString.cipher_instance

    def process_bind_param(self, value: str | None, dialect: Any) -> str | None:
        """Encrypt the value before sending it to the database."""
        if value is None:
            return None

        encrypted = self._cipher.encrypt(value.encode("utf-8"), None)
        return encrypted.hex()

    def process_result_value(self, value: str | None, dialect: Any) -> str | None:
        """Decrypt the value after retrieving it from the database."""
        if value is None:
            return None

        decrypted = self._cipher.decrypt(bytes.fromhex(value), None)
        return decrypted.decode("utf-8")
