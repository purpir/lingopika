from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field
from typing import List


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    APP_ENV: str = "development"
    APP_NAME: str = "LingoPika"
    SECRET_KEY: str = "change-me"
    DEBUG: bool = True

    DATABASE_URL: str = "sqlite+aiosqlite:///./lingopika.db"
    SYNC_DATABASE_URL: str = "sqlite:///./lingopika.db"

    REDIS_URL: str = "redis://localhost:6379/0"

    TELEGRAM_BOT_TOKEN: str = ""
    TELEGRAM_WEBHOOK_URL: str = ""
    TELEGRAM_WEBHOOK_SECRET: str = ""
    ADMIN_TELEGRAM_IDS: str = ""

    STARS_PROVIDER_TOKEN: str = ""

    CORS_ORIGINS: str = "http://localhost:5173"

    HEART_MAX: int = 5
    HEART_REGEN_HOURS: int = 4

    LEAGUE_SEASON_DAYS: int = 7

    @property
    def admin_ids(self) -> List[int]:
        out = []
        for part in self.ADMIN_TELEGRAM_IDS.split(","):
            part = part.strip()
            if part:
                try:
                    out.append(int(part))
                except ValueError:
                    pass
        return out

    @property
    def cors_list(self) -> List[str]:
        return [x.strip() for x in self.CORS_ORIGINS.split(",") if x.strip()]


settings = Settings()
