"""Standalone scheduler worker entry point for admin-only Telegram notifications."""
from __future__ import annotations

import asyncio
import logging
import os
import signal
import threading
from collections.abc import Callable
from typing import Any

from app.scheduler.store import JobStore
from app.scheduler.worker import JobWorker
from app.telegram.bot_api import TelegramBotAPI
from app.telegram.config import TelegramSettings


def make_admin_message_handler(bot: TelegramBotAPI) -> Callable[[dict[str, Any]], None]:
    """Create the sole built-in job handler; payloads cannot select a chat or API method."""
    def send_admin_message(payload: dict[str, Any]) -> None:
        if set(payload) != {"text"}:
            raise ValueError("telegram_admin_message payload must contain only text")
        text = payload.get("text")
        if not isinstance(text, str) or not text.strip() or len(text) > 4096:
            raise ValueError("telegram_admin_message text is invalid")
        asyncio.run(bot.send_admin_message(text.strip()))

    return send_admin_message


def main() -> int:
    logging.basicConfig(
        level=os.getenv("LOG_LEVEL", "INFO").upper(),
        format="%(asctime)s %(levelname)s %(name)s %(message)s",
    )
    settings = TelegramSettings.from_env()
    if settings.mode != "bot" or not settings.bot_token or settings.admin_chat_id is None:
        raise RuntimeError("Scheduler worker requires TELEGRAM_MODE=bot and valid admin bot settings")

    bot = TelegramBotAPI(
        token=settings.bot_token,
        admin_chat_id=settings.admin_chat_id,
        timeout_seconds=30,
    )
    identity = asyncio.run(bot.get_me())
    if identity.get("is_bot") is not True:
        raise RuntimeError("Configured Telegram identity is not a bot")

    database_path = os.getenv("SCHEDULER_DB_PATH", "./data/jobs.sqlite3").strip()
    if not database_path:
        raise RuntimeError("SCHEDULER_DB_PATH must not be empty")
    store = JobStore(database_path)
    worker = JobWorker(store, {"telegram_admin_message": make_admin_message_handler(bot)})
    stop_event = threading.Event()

    def request_stop(_signum: int, _frame: Any) -> None:
        stop_event.set()

    signal.signal(signal.SIGINT, request_stop)
    signal.signal(signal.SIGTERM, request_stop)
    poll_interval = float(os.getenv("SCHEDULER_POLL_INTERVAL", "1.0"))
    logging.getLogger(__name__).info("scheduler worker started; database=%s", database_path)
    worker.run_forever(stop_event, poll_interval=poll_interval)
    logging.getLogger(__name__).info("scheduler worker stopped")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
