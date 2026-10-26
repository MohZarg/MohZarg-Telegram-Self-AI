import asyncio

import pytest

from app.scheduler.runner import make_admin_message_handler


class FakeBot:
    def __init__(self):
        self.sent = []

    async def send_admin_message(self, text):
        self.sent.append(text)


def test_worker_handler_sends_only_plain_text_to_configured_admin():
    bot = FakeBot()
    handler = make_admin_message_handler(bot)
    handler({"text": "  hello  "})
    assert bot.sent == ["hello"]


@pytest.mark.parametrize("payload", [{}, {"text": "hello", "chat_id": 999}, {"text": ""}, {"text": "x" * 4097}, {"text": 12}])
def test_worker_handler_rejects_unsafe_or_invalid_payloads(payload):
    handler = make_admin_message_handler(FakeBot())
    with pytest.raises(ValueError):
        handler(payload)
