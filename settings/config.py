# settings/config.py
import os
from dataclasses import dataclass
from dotenv import load_dotenv


load_dotenv()

@dataclass
class Config:
    TELEGRAM_BOT_TOKEN: str
    TELEGRAM_CHAT_ID_KNP: str
    ENABLE_ISNA: bool
    ENABLE_KNP: bool
    ENABLE_STAT: bool
    

def load_config() -> Config:
    """Загружает конфигурацию из переменных окружения"""
    return Config(
        TELEGRAM_BOT_TOKEN=os.getenv("TELEGRAM_BOT_TOKEN", ""),
        TELEGRAM_CHAT_ID_KNP=os.getenv("sTELEGRAM_CHAT_ID_KNP", ""),
        ENABLE_ISNA=os.getenv("ENABLE_ISNA", "false").lower() == "true",
        ENABLE_STAT=os.getenv("ENABLE_STAT", "false").lower() == "true",
        ENABLE_STAT=os.getenv("ENABLE_KNP", "false").lower() == "true",
    )