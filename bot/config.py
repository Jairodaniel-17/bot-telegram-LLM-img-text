from loguru import logger
import sys
import os
from dotenv import load_dotenv

load_dotenv(".env")

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
LOGGER_LEVEL = os.getenv("LOGGER_LEVEL", "ERROR").upper()
if not TELEGRAM_TOKEN:
    raise ValueError("❌ TELEGRAM_TOKEN no definido en .env.")


logger.remove()  # Elimina cualquier configuración previa
logger.add(
    sys.stderr,
    level=LOGGER_LEVEL,
    format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
)
logger.add(
    "bot.log",
    level=LOGGER_LEVEL,
    rotation="10 MB",
    retention="10 days",
    encoding="utf-8",
)
