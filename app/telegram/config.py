"""Fail-closed validation for the planned dual Telegram integration.

This module validates configuration only; it does not connect to Telegram or
start either client. Secrets are read from the process environment and never
included in validation errors or object representations.
"""
from dataclasses import dataclass, field
import os
from typing import Literal

TelegramMode = Literal["disabled", "bot", "mtproto", "both"]


class TelegramConfigurationError(ValueError):
    """Raised when a selected Telegram mode is missing valid configuration."""


@dataclass(frozen=True, slots=True)
class TelegramSettings:
    mode: TelegramMode
    api_id: int | None = None
    api_hash: str | None = field(default=None, repr=False)
    bot_token: str | None = field(default=None, repr=False)
    admin_chat_id: int | None = None
    admin_user_id: int | None = None

    @classmethod
    def from_env(cls) -> "TelegramSettings":
        raw_mode = os.getenv("TELEGRAM_MODE", "disabled").strip().lower()
        if raw_mode not in {"disabled", "bot", "mtproto", "both"}:
            raise TelegramConfigurationError(
                "TELEGRAM_MODE must be one of: disabled, bot, mtproto, both"
            )
        mode: TelegramMode = raw_mode  # type: ignore[assignment]
        if mode == "disabled":
            return cls(mode=mode)

        api_id: int | None = None
        api_hash = os.getenv("TELEGRAM_API_HASH", "").strip()
        bot_token = os.getenv("TELEGRAM_ADMIN_BOT_TOKEN", "").strip()
        raw_api_id = os.getenv("TELEGRAM_API_ID", "").strip()
        raw_chat_id = os.getenv("TELEGRAM_ADMIN_CHAT_ID", "").strip()
        raw_user_id = os.getenv("TELEGRAM_ADMIN_USER_ID", "").strip()
        chat_id: int | None = None
        user_id: int | None = None

        if mode in {"mtproto", "both"}:
            try:
                api_id = int(raw_api_id)
            except (TypeError, ValueError) as exc:
                raise TelegramConfigurationError(
                    "TELEGRAM_API_ID must be a positive integer for the selected mode"
                ) from exc
            if api_id <= 0:
                raise TelegramConfigurationError(
                    "TELEGRAM_API_ID must be a positive integer for the selected mode"
                )
            if not api_hash:
                raise TelegramConfigurationError(
                    "TELEGRAM_API_HASH is required for the selected mode"
                )

        if mode in {"bot", "both"}:
            if not bot_token:
                raise TelegramConfigurationError(
                    "TELEGRAM_ADMIN_BOT_TOKEN is required for the selected mode"
                )
            try:
                chat_id = int(raw_chat_id)
            except (TypeError, ValueError) as exc:
                raise TelegramConfigurationError(
                    "TELEGRAM_ADMIN_CHAT_ID must be a non-zero integer for the selected mode"
                ) from exc
            if chat_id == 0:
                raise TelegramConfigurationError(
                    "TELEGRAM_ADMIN_CHAT_ID must be a non-zero integer for the selected mode"
                )
            try:
                user_id = int(raw_user_id)
            except (TypeError, ValueError) as exc:
                raise TelegramConfigurationError(
                    "TELEGRAM_ADMIN_USER_ID must be a non-zero integer for the selected mode"
                ) from exc
            if user_id == 0:
                raise TelegramConfigurationError(
                    "TELEGRAM_ADMIN_USER_ID must be a non-zero integer for the selected mode"
                )

        return cls(
            mode=mode,
            api_id=api_id,
            api_hash=api_hash or None,
            bot_token=bot_token or None,
            admin_chat_id=chat_id,
            admin_user_id=user_id,
        )
