import os
from pathlib import Path
from typing import Annotated, Optional

from dotenv import load_dotenv
from pydantic import BaseModel, Field, ConfigDict

BASE_DIR = Path(__file__).resolve().parent.parent
ENV_FILE = BASE_DIR / ".env"
STORAGE_DIR = BASE_DIR / "storage"
DATABASE_PATH = STORAGE_DIR / "database.db"
SESSION_PATH = STORAGE_DIR / "session"


class TelegramConfig(BaseModel):
    api_id: int
    api_hash: str
    bot_token: str
    admin_id: int = 0
    session: str = str(SESSION_PATH)


class PauseConfig(BaseModel):
    after_get: Annotated[float, Field(ge=0, default=10)]
    after_buy: Annotated[float, Field(ge=0, default=1)]


class AppConfig(BaseModel):
    telegram: TelegramConfig
    pause: PauseConfig
    db_url: str = f"sqlite://{DATABASE_PATH}"


def load_config() -> AppConfig:
    load_dotenv()
    telegram = TelegramConfig(
        api_id=int(os.environ.get("API_ID")),
        api_hash=os.environ.get("API_HASH"),
        bot_token=os.environ.get("BOT_TOKEN"),
    )
    pause = PauseConfig(
        after_get=float(os.environ.get("PAUSE_AFTER_GET")),
        after_buy=float(os.environ.get("PAUSE_AFTER_BUY")),
    )
    app = AppConfig(
        telegram=telegram,
        pause=pause
    )
    return app
