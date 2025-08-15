import logging
from telegram.ext import Application
from handlers.start_handler import start_command_handler
from handlers.menu_handler import menu_handlers
from handlers.cloudflare.add_cloudflare_handler import add_cloudflare_conversation
from handlers.cloudflare.records.get_records_handler import get_records_handlers
from handlers.cloudflare.record.add_cloudflare_handler import add_cloudflare_handlers
from handlers.cloudflare.record.edit_cloudflare_handler import edit_cloudflare_handlers
from handlers.cloudflare.record.remove_cloudflare_handler import (
    remove_cloudflare_handlers,
)
from handlers.others_menu_handler import other_menu_handlers

logger = logging.getLogger(__name__)


def register_all_handlers(application: Application) -> None:
    """Centralized function to register all handlers to the bot application."""
    try:
        # Register command handlers
        application.add_handler(start_command_handler)

        # Register menu handlers (command  callback handlers)
        for handler in menu_handlers:
            application.add_handler(handler)

        for handler in other_menu_handlers:
            application.add_handler(handler)

        for handler in get_records_handlers:
            application.add_handler(handler)

        for handler in add_cloudflare_handlers:
            application.add_handler(handler)

        for handler in edit_cloudflare_handlers:
            application.add_handler(handler)

        for handler in remove_cloudflare_handlers:
            application.add_handler(handler)

        # Register Cloudflare account addition conversation handler
        application.add_handler(add_cloudflare_conversation)

        logger.info("All handlers registered successfully")

    except Exception as e:
        logger.error(f"Failed to register handlers: {e}")
        raise
