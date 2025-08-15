import os
import logging
from dotenv import load_dotenv
from typing import Optional

# Load environment variables from .env file
load_dotenv()

logger = logging.getLogger(__name__)


class Config:
    """Centralized configuration class for the Telegram bot."""

    # --- Bot Configuration ---
    BOT_TOKEN: str = os.getenv("BOT_TOKEN", "")
    if not BOT_TOKEN:
        raise ValueError(
            "BOT_TOKEN is required! Please set it in your .env file or environment variables."
        )

    # --- Webhook Configuration ---
    WEBHOOK_URL: str = os.getenv("WEBHOOK_URL", "")
    WEBHOOK_PATH: str = os.getenv("WEBHOOK_PATH", "wangshu")

    # Validate webhook URL for production
    if WEBHOOK_URL and not WEBHOOK_URL.startswith("https://"):
        logger.warning("WEBHOOK_URL should use HTTPS for production!")

    # --- Server Configuration ---
    LISTEN_IP: str = os.getenv("LISTEN_IP", "127.0.0.1")
    PORT: int = int(os.getenv("PORT", "8000"))

    # --- Database Configuration ---
    DATABASE_FILE: str = os.getenv("DATABASE_FILE", "database/bot.db")
    DATABASE_POOL_SIZE: int = int(os.getenv("DATABASE_POOL_SIZE", "10"))

    # --- Logging Configuration ---
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    LOG_FILE: Optional[str] = os.getenv("LOG_FILE")

    # --- Application Settings ---
    DEBUG: bool = os.getenv("DEBUG", "False").lower() in ("true", "1", "yes")
    MAX_RETRIES: int = int(os.getenv("MAX_RETRIES", "3"))
    REQUEST_TIMEOUT: int = int(os.getenv("REQUEST_TIMEOUT", "30"))

    @classmethod
    def validate(cls) -> bool:
        """Validate critical configuration values."""
        errors = []

        if not cls.BOT_TOKEN:
            errors.append("BOT_TOKEN is required")

        if cls.WEBHOOK_URL and not cls.WEBHOOK_URL.startswith("https://"):
            errors.append("WEBHOOK_URL must use HTTPS in production")

        if cls.PORT < 1024 or cls.PORT > 65535:
            errors.append("PORT must be between 1024 and 65535")

        if errors:
            for error in errors:
                logger.error(f"Configuration error: {error}")
            return False

        return True

    @classmethod
    def get_webhook_info(cls) -> dict:
        """Get webhook configuration info."""
        if not cls.WEBHOOK_URL:
            return {}

        return {
            "url": f"{cls.WEBHOOK_URL}/{cls.WEBHOOK_PATH}",
            "allowed_updates": ["message", "callback_query"],
            "drop_pending_updates": True,
        }


# Initialize configuration
config = Config()

# Validate configuration on import
if not config.validate():
    raise ValueError(
        "Configuration validation failed! Please check your environment variables."
    )

# Legacy compatibility - export commonly used values
BOT_TOKEN = config.BOT_TOKEN
WEBHOOK_URL = config.WEBHOOK_URL
WEBHOOK_PATH = config.WEBHOOK_PATH
LISTEN_IP = config.LISTEN_IP
PORT = config.PORT
DATABASE_FILE = config.DATABASE_FILE
