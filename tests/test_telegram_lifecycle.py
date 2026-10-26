"""Application lifecycle tests for optional Telegram Bot API integration."""
import asyncio

import pytest

import app.main as main_module


class FakeBot:
    def __init__(self, **kwargs):
        self.kwargs = kwargs

    async def get_me(self):
        return {"id": 7, "is_bot": True}

    async def get_updates(self, *, offset=None, timeout=20):
        await asyncio.sleep(0.01)
        return []


def test_bot_mode_starts_and_stops_poller(monkeypatch):
    monkeypatch.setenv("TELEGRAM_MODE", "bot")
    monkeypatch.setenv("TELEGRAM_ADMIN_BOT_TOKEN", "test-token")
    monkeypatch.setenv("TELEGRAM_ADMIN_CHAT_ID", "-100123")
    monkeypatch.setenv("TELEGRAM_ADMIN_USER_ID", "456")
    monkeypatch.setattr(main_module, "TelegramBotAPI", FakeBot)

    async def exercise():
        async with main_module.lifespan(main_module.app):
            assert isinstance(main_module.app.state.telegram_bot, FakeBot)
            assert main_module.app.state.telegram_bot.kwargs["admin_chat_id"] == -100123
        assert main_module.app.state.telegram_bot is None

    asyncio.run(exercise())


def test_unimplemented_mtproto_mode_fails_closed(monkeypatch):
    monkeypatch.setenv("TELEGRAM_MODE", "mtproto")
    monkeypatch.setenv("TELEGRAM_API_ID", "12345")
    monkeypatch.setenv("TELEGRAM_API_HASH", "test-hash")

    async def exercise():
        with pytest.raises(RuntimeError, match="MTProto adapter is not implemented"):
            async with main_module.lifespan(main_module.app):
                pass

    asyncio.run(exercise())
