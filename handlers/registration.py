import logging
from telegram.ext import Application
from handlers.start_handler import start_command_handler
from handlers.menu_handler import menu_handlers
from handlers.others_menu_handler import other_menu_handlers
from handlers.cloudflare.add_cloudflare_handler import add_cloudflare_conversation
from handlers.cloudflare.records.get_records_handler import get_records_handlers

logger = logging.getLogger(__name__)


def register_all_handlers(application: Application) -> None:
    """Fungsi terpusat untuk mendaftarkan semua handler ke aplikasi bot."""
    try:
        # Daftarkan command handlers
        application.add_handler(start_command_handler)

        # Daftarkan menu handlers (command dan callback handlers)
        for handler in menu_handlers:
            application.add_handler(handler)

        for handler in other_menu_handlers:
            application.add_handler(handler)

        for handler in get_records_handlers:
            application.add_handler(handler)

        # Daftarkan Cloudflare account addition conversation handler
        application.add_handler(add_cloudflare_conversation)

        logger.info("Semua handler berhasil didaftarkan")

    except Exception as e:
        logger.error(f"Gagal mendaftarkan handlers: {e}")
        raise
