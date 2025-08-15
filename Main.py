import asyncio
import logging
import signal
import sys
from typing import NoReturn

from telegram import Update
from telegram.ext import Application, ContextTypes
from telegram.error import TelegramError

from config import config
from database import db
from handlers.registration import register_all_handlers

# Setup logging with improved configuration
def setup_logging() -> None:
    """Configure logging with both console and optional file output."""
    log_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    
    # Configure root logger
    logging.basicConfig(
        format=log_format,
        level=getattr(logging, config.LOG_LEVEL.upper()),
        handlers=[]
    )
    
    # Add console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(logging.Formatter(log_format))
    logging.getLogger().addHandler(console_handler)
    
    # Add file handler if configured
    if config.LOG_FILE:
        file_handler = logging.FileHandler(config.LOG_FILE)
        file_handler.setFormatter(logging.Formatter(log_format))
        logging.getLogger().addHandler(file_handler)
    
    # Reduce noise from external libraries
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("telegram").setLevel(logging.INFO)

logger = logging.getLogger(__name__)

class TelegramBot:
    """Main Telegram bot class with improved error handling and lifecycle management."""
    
    def __init__(self):
        self.application: Application = None
        self._shutdown_event = asyncio.Event()
        
    async def initialize(self) -> None:
        """Initialize the bot application and database."""
        try:
            # Initialize database first
            await self._init_database()
            
            # Build application with improved configuration
            builder = Application.builder()
            builder.token(config.BOT_TOKEN)
            
            # Configure request settings
            builder.read_timeout(config.REQUEST_TIMEOUT)
            builder.write_timeout(config.REQUEST_TIMEOUT)
            builder.connect_timeout(config.REQUEST_TIMEOUT)
            
            # Build the application
            self.application = builder.build()
            
            # Register all handlers
            register_all_handlers(self.application)
            logger.info("All handlers registered successfully")
            
            # Set up error handler
            self.application.add_error_handler(self._error_handler)
            
        except Exception as e:
            logger.error(f"Failed to initialize bot: {e}")
            raise
    
    async def _init_database(self) -> None:
        """Initialize database with async support."""
        try:
            # Run database initialization in thread pool to avoid blocking
            loop = asyncio.get_event_loop()
            await loop.run_in_executor(None, db.init_db)
            logger.info("Database initialized successfully")
        except Exception as e:
            logger.error(f"Database initialization failed: {e}")
            raise
    
    async def _error_handler(self, update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Global error handler for the bot."""
        logger.error(f"Exception while handling an update: {context.error}")
        
        # Log the update that caused the error
        if update:
            logger.error(f"Update that caused error: {update}")
        
        # Send error notification to user if possible
        if isinstance(update, Update) and update.effective_chat:
            try:
                await context.bot.send_message(
                    chat_id=update.effective_chat.id,
                    text="⚠️ Terjadi kesalahan saat memproses permintaan Anda. Silakan coba lagi nanti."
                )
            except TelegramError as e:
                logger.error(f"Failed to send error message to user: {e}")
    
    async def start_webhook(self) -> None:
        """Start the bot with webhook configuration."""
        if not config.WEBHOOK_URL:
            raise ValueError("WEBHOOK_URL is required for webhook mode")
        
        webhook_info = config.get_webhook_info()
        logger.info(f"Starting webhook at {config.LISTEN_IP}:{config.PORT}")
        logger.info(f"Webhook URL: {webhook_info['url']}")
        
        try:
            # Initialize the application
            await self.application.initialize()
            
            # Start the webhook
            await self.application.start()
            
            # Set up the webhook
            await self.application.updater.start_webhook(
                listen=config.LISTEN_IP,
                port=config.PORT,
                url_path=config.WEBHOOK_PATH,
                webhook_url=webhook_info["url"],
                allowed_updates=webhook_info["allowed_updates"],
                drop_pending_updates=webhook_info["drop_pending_updates"]
            )
            
            logger.info("Webhook started successfully")
            
            # Wait for shutdown signal
            await self._shutdown_event.wait()
            
        except Exception as e:
            logger.error(f"Failed to start webhook: {e}")
            raise
        finally:
            await self.stop()
    
    async def start_polling(self) -> None:
        """Start the bot with polling (for development)."""
        logger.info("Starting bot in polling mode")
        
        try:
            # Initialize and start the application
            await self.application.initialize()
            await self.application.start()
            
            # Start polling
            await self.application.updater.start_polling(
                allowed_updates=Update.ALL_TYPES,
                drop_pending_updates=True
            )
            
            logger.info("Polling started successfully")
            
            # Wait for shutdown signal
            await self._shutdown_event.wait()
            
        except Exception as e:
            logger.error(f"Failed to start polling: {e}")
            raise
        finally:
            await self.stop()
    
    async def stop(self) -> None:
        """Gracefully stop the bot."""
        if not self.application:
            return
            
        logger.info("Stopping bot...")
        
        try:
            # Stop the updater
            if self.application.updater.running:
                await self.application.updater.stop()
            
            # Stop the application
            if self.application.running:
                await self.application.stop()
            
            # Shutdown the application
            await self.application.shutdown()
            
            logger.info("Bot stopped successfully")
            
        except Exception as e:
            logger.error(f"Error during bot shutdown: {e}")
    
    def shutdown(self) -> None:
        """Signal shutdown from signal handler."""
        self._shutdown_event.set()

def signal_handler(bot: TelegramBot) -> None:
    """Handle shutdown signals gracefully."""
    def handler(signum, frame):
        logger.info(f"Received signal {signum}, shutting down...")
        bot.shutdown()
    
    return handler

async def main() -> NoReturn:
    """Main entry point for the bot."""
    setup_logging()
    logger.info("Starting Cloudflare DNS Manager Bot")
    
    # Create bot instance
    bot = TelegramBot()
    
    # Set up signal handlers for graceful shutdown
    for sig in (signal.SIGTERM, signal.SIGINT):
        signal.signal(sig, signal_handler(bot))
    
    try:
        # Initialize the bot
        await bot.initialize()
        
        # Start the bot based on configuration
        if config.WEBHOOK_URL:
            await bot.start_webhook()
        else:
            logger.info("No WEBHOOK_URL configured, starting in polling mode")
            await bot.start_polling()
            
    except KeyboardInterrupt:
        logger.info("Bot stopped by user")
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        sys.exit(1)
    finally:
        logger.info("Bot shutdown complete")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Process interrupted by user")
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        sys.exit(1)
