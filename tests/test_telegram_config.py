"""Tests for fail-closed Telegram configuration validation."""
import pytest

from app.telegram.config import TelegramConfigurationError, TelegramSettings


@pytest.fixture(autouse=True)
def clear_telegram_env(monkeypatch):
    for key in (
        "TELEGRAM_MODE",
        "TELEGRAM_API_ID",
        "TELEGRAM_API_HASH",
        "TELEGRAM_ADMIN_BOT_TOKEN",
        "TELEGRAM_ADMIN_CHAT_ID",
        "TELEGRAM_ADMIN_USER_ID",
    ):
        monkeypatch.delenv(key, raising=False)


def test_defaults_to_disabled_without_credentials():
    settings = TelegramSettings.from_env()
    assert settings.mode == "disabled"
    assert settings.api_id is None
    assert settings.bot_token is None


def test_rejects_unknown_mode(monkeypatch):
    monkeypatch.setenv("TELEGRAM_MODE", "everything")
    with pytest.raises(TelegramConfigurationError, match="TELEGRAM_MODE"):
        TelegramSettings.from_env()


def test_bot_mode_requires_token_and_admin_chat(monkeypatch):
    monkeypatch.setenv("TELEGRAM_MODE", "bot")
    monkeypatch.setenv("TELEGRAM_ADMIN_BOT_TOKEN", "test-token")
    monkeypatch.setenv("TELEGRAM_ADMIN_CHAT_ID", "123")
    monkeypatch.setenv("TELEGRAM_ADMIN_USER_ID", "123")
    with pytest.raises(TelegramConfigurationError, match="TELEGRAM_ADMIN_USER_ID"):
        TelegramSettings.from_env()


def test_mtproto_mode_requires_positive_api_id_and_hash(monkeypatch):
    monkeypatch.setenv("TELEGRAM_MODE", "mtproto")
    monkeypatch.setenv("TELEGRAM_API_ID", "0")
    monkeypatch.setenv("TELEGRAM_API_HASH", "test-hash")
    with pytest.raises(TelegramConfigurationError, match="TELEGRAM_API_ID"):
        TelegramSettings.from_env()


def test_both_mode_requires_both_credential_sets(monkeypatch):
    monkeypatch.setenv("TELEGRAM_MODE", "both")
    monkeypatch.setenv("TELEGRAM_API_ID", "12345")
    monkeypatch.setenv("TELEGRAM_API_HASH", "test-hash")
    with pytest.raises(TelegramConfigurationError, match="TELEGRAM_ADMIN_BOT_TOKEN"):
        TelegramSettings.from_env()


def test_both_mode_returns_validated_settings_without_exposing_secrets(monkeypatch):
    monkeypatch.setenv("TELEGRAM_MODE", "both")
    monkeypatch.setenv("TELEGRAM_API_ID", "12345")
    monkeypatch.setenv("TELEGRAM_API_HASH", "private-hash")
    monkeypatch.setenv("TELEGRAM_ADMIN_BOT_TOKEN", "private-token")
    monkeypatch.setenv("TELEGRAM_ADMIN_CHAT_ID", "-100123")
    monkeypatch.setenv("TELEGRAM_ADMIN_USER_ID", "456")

    settings = TelegramSettings.from_env()

    assert settings.mode == "both"
    assert settings.api_id == 12345
    assert settings.admin_chat_id == -100123
    assert settings.admin_user_id == 456
    assert "private-hash" not in repr(settings)
    assert "private-token" not in repr(settings)


def test_bot_mode_does_not_require_mtproto_credentials(monkeypatch):
    monkeypatch.setenv("TELEGRAM_MODE", "bot")
    monkeypatch.setenv("TELEGRAM_ADMIN_BOT_TOKEN", "private-token")
    monkeypatch.setenv("TELEGRAM_ADMIN_CHAT_ID", "123")

    settings = TelegramSettings.from_env()

    assert settings.mode == "bot"
    assert settings.api_id is None
    assert settings.api_hash is None
