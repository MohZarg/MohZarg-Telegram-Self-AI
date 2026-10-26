"""Tests for allowlisted Telegram bot commands; no network calls are made."""
import asyncio

from app.telegram.polling import TelegramBotPoller


class FakeBot:
    def __init__(self):
        self.sent = []

    async def send_admin_message(self, text):
        self.sent.append(text)
        return {"message_id": len(self.sent)}


def update(update_id=1, user_id=456, chat_id=-100123, text="/status"):
    return {
        "update_id": update_id,
        "message": {
            "from": {"id": user_id},
            "chat": {"id": chat_id},
            "text": text,
        },
    }


def test_only_exact_admin_user_and_chat_can_run_allowlisted_commands():
    bot = FakeBot()
    poller = TelegramBotPoller(bot, admin_user_id=456, admin_chat_id=-100123)
    assert asyncio.run(poller.process_update(update(text="/status@GhYiAbBot"))) is True
    assert len(bot.sent) == 1 and "running" in bot.sent[0]
    assert asyncio.run(poller.process_update(update(user_id=457))) is False
    assert asyncio.run(poller.process_update(update(chat_id=-100999))) is False
    assert len(bot.sent) == 1


def test_unknown_commands_and_plain_messages_are_ignored():
    bot = FakeBot()
    poller = TelegramBotPoller(bot, admin_user_id=456, admin_chat_id=-100123)
    assert asyncio.run(poller.process_update(update(text="/delete_everything"))) is False
    assert asyncio.run(poller.process_update(update(text="hello"))) is False
    assert asyncio.run(poller.process_update(update(text="   "))) is False
    assert bot.sent == []


def test_help_command_returns_only_fixed_safe_help_text():
    bot = FakeBot()
    poller = TelegramBotPoller(bot, admin_user_id=456, admin_chat_id=-100123)
    assert asyncio.run(poller.process_update(update(text="/help"))) is True
    assert bot.sent == ["GhYiAb Self admin bot\\nAllowed commands: /help, /status"]
