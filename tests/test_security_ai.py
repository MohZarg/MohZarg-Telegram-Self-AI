import pytest
from cryptography.fernet import Fernet
from app.security.session_vault import SessionVault
from app.ai.providers import DisabledProvider, generate_safely


def test_session_vault_encrypts_and_round_trips(tmp_path):
    vault = SessionVault(Fernet.generate_key())
    secret = b"test-session-data-not-a-real-session"
    encrypted = vault.encrypt(secret)
    assert secret not in encrypted
    assert vault.decrypt(encrypted) == secret
    path = tmp_path / "session.enc"
    vault.write(path, secret)
    assert path.read_bytes() != secret
    assert vault.read(path) == secret


def test_session_vault_rejects_wrong_key():
    one = SessionVault(Fernet.generate_key())
    two = SessionVault(Fernet.generate_key())
    with pytest.raises(ValueError, match="ciphertext"):
        two.decrypt(one.encrypt(b"sample"))


def test_disabled_ai_degrades_without_leaking_prompt():
    result = generate_safely(DisabledProvider(), "private prompt")
    assert not result.ok
    assert result.provider == "disabled"
    assert "private prompt" not in result.error
