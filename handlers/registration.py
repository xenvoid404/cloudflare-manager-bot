import logging
from telegram.ext import Application
from handlers.start_handler import start_command_handler, help_command_handler
from handlers.menu_handler import menu_handlers

logger = logging.getLogger(__name__)

def register_all_handlers(application: Application) -> None:
    """Centralized function to register all handlers to the bot application."""
    try:
        # Register command handlers
        application.add_handler(start_command_handler)
        application.add_handler(help_command_handler)
        
        # Register menu handlers (command + callback handlers)
        for handler in menu_handlers:
            application.add_handler(handler)
        
        logger.info("All handlers registered successfully")
        
    except Exception as e:
        logger.error(f"Failed to register handlers: {e}")
        raise
