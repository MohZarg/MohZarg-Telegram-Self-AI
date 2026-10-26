"""Small, dependency-light settings loader for the application."""
from dataclasses import dataclass
import os


@dataclass(frozen=True, slots=True)
class Settings:
    app_env: str
    app_host: str
    app_port: int
    log_level: str
    donation_url: str

    @classmethod
    def from_env(cls) -> "Settings":
        raw_port = os.getenv("APP_PORT", "8000")
        try:
            port = int(raw_port)
        except ValueError as exc:
            raise ValueError("APP_PORT must be an integer") from exc
        if not 1 <= port <= 65535:
            raise ValueError("APP_PORT must be between 1 and 65535")
        host = os.getenv("APP_HOST", "127.0.0.1")
        if not host.strip():
            raise ValueError("APP_HOST must not be empty")
        return cls(
            app_env=os.getenv("APP_ENV", "development"),
            app_host=host,
            app_port=port,
            log_level=os.getenv("LOG_LEVEL", "INFO").upper(),
            donation_url=os.getenv("DONATION_URL", "").strip(),
        )
