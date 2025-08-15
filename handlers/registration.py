import logging
from telegram.ext import Application
from handlers.start_handler import start_command_handler
from handlers.menu_handler import menu_handlers
from handlers.add_cloudflare_handler import add_cloudflare_conversation
from handlers.other_menu_handler import other_menu_handlers
from handlers.dns_record_handlers import dns_record_handlers
from handlers.navigation_handler import navigation_handlers

logger = logging.getLogger(__name__)


def register_all_handlers(application: Application) -> None:
    """Centralized function to register all handlers to the bot application."""
    try:
        # Register command handlers
        application.add_handler(start_command_handler)

        # Register menu handlers (command & callback handlers)
        for handler in menu_handlers:
            application.add_handler(handler)

        # Register Cloudflare account addition conversation handler
        application.add_handler(add_cloudflare_conversation)

        # Register other menu handlers
        for handler in other_menu_handlers:
            application.add_handler(handler)

        # Register DNS record handlers
        for handler in dns_record_handlers:
            application.add_handler(handler)

        # Register navigation handlers
        for handler in navigation_handlers:
            application.add_handler(handler)

        logger.info("All handlers registered successfully")

    except Exception as e:
        logger.error(f"Failed to register handlers: {e}")
        raise
