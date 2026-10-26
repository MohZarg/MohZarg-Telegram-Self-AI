"""Unit tests use a fake HTTP transport and never contact Telegram."""
import asyncio
import json

import httpx
import pytest

from app.telegram.bot_api import TelegramBotAPI, TelegramBotApiError


def test_get_me_uses_api_and_returns_result():
    def handler(request: httpx.Request) -> httpx.Response:
        assert request.url.path.endswith("/getMe")
        return httpx.Response(200, json={"ok": True, "result": {"id": 7, "is_bot": True}})

    client = TelegramBotAPI(
        token="test-token", admin_chat_id=123, transport=httpx.MockTransport(handler)
    )
    assert asyncio.run(client.get_me()) == {"id": 7, "is_bot": True}


def test_send_message_only_uses_configured_admin_chat():
    def handler(request: httpx.Request) -> httpx.Response:
        assert request.url.path.endswith("/sendMessage")
        payload = json.loads(request.content)
        assert payload == {"chat_id": -100123, "text": "hello"}
        return httpx.Response(200, json={"ok": True, "result": {"message_id": 1}})

    client = TelegramBotAPI(
        token="test-token", admin_chat_id=-100123, transport=httpx.MockTransport(handler)
    )
    assert asyncio.run(client.send_admin_message(" hello ")) == {"message_id": 1}


def test_failed_response_does_not_leak_token():
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, json={"ok": False, "description": "bad token"})

    client = TelegramBotAPI(
        token="sensitive-test-token", admin_chat_id=123, transport=httpx.MockTransport(handler)
    )
    with pytest.raises(TelegramBotApiError) as error:
        asyncio.run(client.get_me())
    assert "sensitive-test-token" not in str(error.value)


def test_transport_error_is_sanitized():
    def handler(request: httpx.Request) -> httpx.Response:
        raise httpx.ConnectError("connection failed", request=request)

    client = TelegramBotAPI(
        token="sensitive-test-token", admin_chat_id=123, transport=httpx.MockTransport(handler)
    )
    with pytest.raises(TelegramBotApiError) as error:
        asyncio.run(client.get_me())
    assert "sensitive-test-token" not in str(error.value)


def test_rejects_empty_message_and_invalid_admin_id():
    client = TelegramBotAPI(token="test-token", admin_chat_id=123)
    with pytest.raises(ValueError, match="Message text"):
        asyncio.run(client.send_admin_message("   "))
    with pytest.raises(ValueError, match="admin chat ID"):
        TelegramBotAPI(token="test-token", admin_chat_id=0)


def test_get_updates_uses_long_poll_payload():
    def handler(request: httpx.Request) -> httpx.Response:
        assert request.url.path.endswith("/getUpdates")
        payload = json.loads(request.content)
        assert payload == {"timeout": 20, "allowed_updates": ["message"], "offset": 12}
        return httpx.Response(200, json={"ok": True, "result": [{"update_id": 12}]})

    client = TelegramBotAPI(token="test-token", admin_chat_id=123, transport=httpx.MockTransport(handler))
    assert asyncio.run(client.get_updates(offset=12)) == [{"update_id": 12}]
