import os
import logging
from dotenv import load_dotenv
from typing import Optional

# Load environment variables dari file .env
load_dotenv()

logger = logging.getLogger(__name__)


class Config:
    """Kelas konfigurasi terpusat untuk Telegram bot."""

    # --- Konfigurasi Bot ---
    BOT_TOKEN: str = os.getenv("BOT_TOKEN", "")
    if not BOT_TOKEN:
        raise ValueError(
            "BOT_TOKEN diperlukan! Silakan set di file .env atau environment variables."
        )

    # --- Konfigurasi Webhook ---
    WEBHOOK_URL: str = os.getenv("WEBHOOK_URL", "")
    WEBHOOK_PATH: str = os.getenv("WEBHOOK_PATH", "wangshu")

    # Validasi webhook URL untuk production
    if WEBHOOK_URL and not WEBHOOK_URL.startswith("https://"):
        logger.warning("WEBHOOK_URL sebaiknya menggunakan HTTPS untuk production!")

    # --- Konfigurasi Server ---
    LISTEN_IP: str = os.getenv("LISTEN_IP", "127.0.0.1")
    PORT: int = int(os.getenv("PORT", "8000"))

    # --- Konfigurasi Database ---
    DATABASE_FILE: str = os.getenv("DATABASE_FILE", "database/bot.db")
    DATABASE_POOL_SIZE: int = int(os.getenv("DATABASE_POOL_SIZE", "10"))

    # --- Konfigurasi Logging ---
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    LOG_FILE: Optional[str] = os.getenv("LOG_FILE")

    # --- Pengaturan Aplikasi ---
    DEBUG: bool = os.getenv("DEBUG", "False").lower() in ("true", "1", "yes")
    MAX_RETRIES: int = int(os.getenv("MAX_RETRIES", "3"))
    REQUEST_TIMEOUT: int = int(os.getenv("REQUEST_TIMEOUT", "30"))

    @classmethod
    def validate(cls) -> bool:
        """Validasi nilai konfigurasi kritis."""
        errors = []

        if not cls.BOT_TOKEN:
            errors.append("BOT_TOKEN diperlukan")

        if cls.WEBHOOK_URL and not cls.WEBHOOK_URL.startswith("https://"):
            errors.append("WEBHOOK_URL harus menggunakan HTTPS di production")

        if cls.PORT < 1024 or cls.PORT > 65535:
            errors.append("PORT harus antara 1024 dan 65535")

        if errors:
            for error in errors:
                logger.error(f"Error konfigurasi: {error}")
            return False

        return True

    @classmethod
    def get_webhook_info(cls) -> dict:
        """Dapatkan informasi konfigurasi webhook."""
        if not cls.WEBHOOK_URL:
            return {}

        return {
            "url": f"{cls.WEBHOOK_URL}/{cls.WEBHOOK_PATH}",
            "allowed_updates": ["message", "callback_query"],
            "drop_pending_updates": True,
        }


# Inisialisasi konfigurasi
config = Config()

# Validasi konfigurasi saat import
if not config.validate():
    raise ValueError(
        "Validasi konfigurasi gagal! Silakan periksa environment variables Anda."
    )

# Legacy compatibility - export nilai yang sering digunakan
BOT_TOKEN = config.BOT_TOKEN
WEBHOOK_URL = config.WEBHOOK_URL
WEBHOOK_PATH = config.WEBHOOK_PATH
LISTEN_IP = config.LISTEN_IP
PORT = config.PORT
DATABASE_FILE = config.DATABASE_FILE
