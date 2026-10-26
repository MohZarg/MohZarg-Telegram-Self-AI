"""Minimal asynchronous Bot API adapter with an admin-chat allowlist.

The token is never included in logs or raised exception messages. This module
does not poll updates, create webhooks, or execute arbitrary user commands.
"""
from __future__ import annotations

from typing import Any

import httpx


class TelegramBotApiError(RuntimeError):
    """Sanitized Bot API failure without request URLs or credential material."""


class TelegramBotAPI:
    def __init__(
        self,
        *,
        token: str,
        admin_chat_id: int,
        timeout_seconds: float = 10.0,
        transport: httpx.AsyncBaseTransport | None = None,
    ) -> None:
        if not token or not token.strip():
            raise ValueError("A Bot API token is required")
        if not isinstance(admin_chat_id, int) or isinstance(admin_chat_id, bool) or admin_chat_id == 0:
            raise ValueError("A non-zero admin chat ID is required")
        if not 0 < timeout_seconds <= 60:
            raise ValueError("timeout_seconds must be greater than 0 and at most 60")
        self._token = token.strip()
        self._admin_chat_id = admin_chat_id
        self._timeout_seconds = timeout_seconds
        self._transport = transport

    async def _request(self, method: str, payload: dict[str, Any] | None = None) -> dict[str, Any]:
        try:
            async with httpx.AsyncClient(
                base_url=f"https://api.telegram.org/bot{self._token}/",
                timeout=self._timeout_seconds,
                transport=self._transport,
            ) as client:
                response = await client.post(method, json=payload or {})
                response.raise_for_status()
                body = response.json()
        except (httpx.HTTPError, ValueError) as exc:
            # Avoid propagating HTTP exceptions, which can contain the token-bearing URL.
            raise TelegramBotApiError("Telegram Bot API request failed") from None
        if not isinstance(body, dict) or body.get("ok") is not True:
            raise TelegramBotApiError("Telegram Bot API returned an unsuccessful response")
        result = body.get("result")
        if not isinstance(result, dict):
            raise TelegramBotApiError("Telegram Bot API returned an invalid response shape")
        return result

    async def get_me(self) -> dict[str, Any]:
        """Return Telegram's bot identity response; callers must not log the token."""
        return await self._request("getMe")

    async def send_admin_message(self, text: str) -> dict[str, Any]:
        """Send plain text only to the configured admin chat, never a caller-chosen ID."""
        if not isinstance(text, str) or not text.strip():
            raise ValueError("Message text must not be empty")
        if len(text) > 4096:
            raise ValueError("Message text exceeds Telegram's 4096-character limit")
        return await self._request(
            "sendMessage",
            {"chat_id": self._admin_chat_id, "text": text.strip()},
        )
