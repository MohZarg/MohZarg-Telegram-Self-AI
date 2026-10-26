"""Restricted long-polling handler for the configured administrative user only."""
from __future__ import annotations

import asyncio
import logging
from typing import Any

from app.telegram.bot_api import TelegramBotAPI, TelegramBotApiError


class TelegramBotPoller:
    """Allowlisted read-only commands; never executes arbitrary message content."""

    def __init__(self, bot: TelegramBotAPI, *, admin_user_id: int, admin_chat_id: int):
        if admin_user_id <= 0 or admin_chat_id == 0
            raise ValueError("Admin user ID must be positive and chat ID must be non-zero")
        self.bot = bot
        self.admin_user_id = admin_user_id
        self.admin_chat_id = admin_chat_id
        self._offset: int | None = None
        self._logger = logging.getLogger(__name__)

    async def process_update(self, update: dict[str, Any]) -> bool:
        """Process only a message from the exact configured user in the configured chat."""
        update_id = update.get("update_id")
        if not isinstance(update_id, int):
            return False
        message = update.get("message")
        if not isinstance(message, dict):
            return False
        sender = message.get("from")
        chat = message.get("chat")
        text = message.get("text")
        if not isinstance(sender, dict) or not isinstance(chat, dict) or not isinstance(text, str):
            return False
        if sender.get("id") != self.admin_user_id or chat.get("id") != self.admin_chat_id:
            return False
        stripped = text.strip()
        if not stripped:
            return False
        command = stripped.split(maxsplit=1)[0].split("@", 1)[0].lower()
        if command in {"/start", "/help"}:
            await self.bot.send_admin_message("GhYiAb Self admin bot\\nAllowed commands: /help, /status")
            return True
        if command == "/status":
            await self.bot.send_admin_message("GhYiAb Self is running. Bot API polling is active; MTProto is not enabled.")
            return True
        # Unknown commands and ordinary messages are deliberately ignored.
        return False

    async def run(self) -> None:
        """Poll until cancelled. Errors are logged by type only; credentials are never logged."""
        while True:
            try:
                updates = await self.bot.get_updates(offset=self._offset, timeout=20)
                for update in updates:
                    try:
                        await self.process_update(update)
                    except TelegramBotApiError as exc:
                        self._logger.warning("Telegram command response failed (%s)", type(exc).__name__)
                    update_id = update.get("update_id")
                    if isinstance(update_id, int):
                        self._offset = max(self._offset or 0, update_id + 1)
            except asyncio.CancelledError:
                raise
            except TelegramBotApiError as exc:
                self._logger.warning("Telegram polling failed (%s)", type(exc).__name__)
                await asyncio.sleep(2)
