"""Authenticated encryption for serialized user-session bytes at rest.

The caller must keep the Fernet key outside the repository and rotate/revoke sessions
when a key is lost. This module does not implement Telegram login or session lifecycle.
"""
import os
from pathlib import Path
from cryptography.fernet import Fernet, InvalidToken

class SessionVault:
    def __init__(self, key: bytes):
        try:
            self._cipher = Fernet(key)
        except (ValueError, TypeError) as exc:
            raise ValueError("SESSION_VAULT_KEY must be a valid Fernet key") from exc

    def encrypt(self, session_data: bytes) -> bytes:
        if not isinstance(session_data, bytes) or not session_data:
            raise ValueError("session_data must be non-empty bytes")
        return self._cipher.encrypt(session_data)

    def decrypt(self, ciphertext: bytes) -> bytes:
        try:
            return self._cipher.decrypt(ciphertext)
        except InvalidToken as exc:
            raise ValueError("Session ciphertext is invalid or key does not match") from exc

    def write(self, path: str | Path, session_data: bytes) -> None:
        target = Path(path)
        target.parent.mkdir(parents=True, exist_ok=True)
        temporary = target.with_suffix(target.suffix + ".tmp")
        temporary.write_bytes(self.encrypt(session_data))
        try:
            os.chmod(temporary, 0o600)
            temporary.replace(target)
            os.chmod(target, 0o600)
        finally:
            if temporary.exists():
                temporary.unlink()

    def read(self, path: str | Path) -> bytes:
        return self.decrypt(Path(path).read_bytes())
