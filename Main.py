import asyncio
import logging
import signal
import sys
from typing import NoReturn

from telegram import Update
from telegram.ext import Application, ContextTypes
from telegram.error import TelegramError

from config import config
from database.db import init_db
from handlers.registration import register_all_handlers


def setup_logging() -> None:
    """Konfigurasi logging dengan output console dan file opsional."""
    log_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

    # Konfigurasi root logger
    logging.basicConfig(
        format=log_format, level=getattr(logging, config.LOG_LEVEL.upper()), handlers=[]
    )

    # Tambah console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(logging.Formatter(log_format))
    logging.getLogger().addHandler(console_handler)

    # Tambah file handler jika dikonfigurasi
    if config.LOG_FILE:
        file_handler = logging.FileHandler(config.LOG_FILE)
        file_handler.setFormatter(logging.Formatter(log_format))
        logging.getLogger().addHandler(file_handler)

    # Kurangi noise dari library eksternal
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("telegram").setLevel(logging.INFO)


logger = logging.getLogger(__name__)


class TelegramBot:
    """Kelas utama Telegram bot dengan penanganan error dan manajemen lifecycle yang lebih baik."""

    def __init__(self):
        self.application: Application = None
        self._shutdown_event = asyncio.Event()

    async def initialize(self) -> None:
        """Inisialisasi aplikasi bot dan database."""
        try:
            # Inisialisasi database terlebih dahulu
            await self._init_database()

            # Build aplikasi dengan konfigurasi yang lebih baik
            builder = Application.builder()
            builder.token(config.BOT_TOKEN)

            # Konfigurasi pengaturan request
            builder.read_timeout(config.REQUEST_TIMEOUT)
            builder.write_timeout(config.REQUEST_TIMEOUT)
            builder.connect_timeout(config.REQUEST_TIMEOUT)

            # Build aplikasi
            self.application = builder.build()

            # Daftarkan semua handler
            register_all_handlers(self.application)
            logger.info("Semua handler berhasil didaftarkan")

            # Setup error handler
            self.application.add_error_handler(self._error_handler)

        except Exception as e:
            logger.error(f"Gagal menginisialisasi bot: {e}")
            raise

    async def _init_database(self) -> None:
        """Inisialisasi database dengan dukungan async."""
        try:
            # Inisialisasi database dengan dukungan async yang tepat
            await init_db()
            logger.info("Database berhasil diinisialisasi")
        except Exception as e:
            logger.error(f"Inisialisasi database gagal: {e}")
            raise

    async def _error_handler(
        self, update: object, context: ContextTypes.DEFAULT_TYPE
    ) -> None:
        """Global error handler untuk bot."""
        logger.error(f"Exception saat menangani update: {context.error}")

        # Log update yang menyebabkan error
        if update:
            logger.error(f"Update yang menyebabkan error: {update}")

        # Kirim notifikasi error ke user jika memungkinkan
        if isinstance(update, Update) and update.effective_chat:
            try:
                await context.bot.send_message(
                    chat_id=update.effective_chat.id,
                    text="Terjadi kesalahan saat memproses permintaan Anda. Silakan coba lagi nanti.",
                )
            except TelegramError as e:
                logger.error(f"Gagal mengirim pesan error ke user: {e}")

    async def start_webhook(self) -> None:
        """Mulai bot dengan konfigurasi webhook."""
        if not config.WEBHOOK_URL:
            raise ValueError("WEBHOOK_URL diperlukan untuk mode webhook")

        webhook_info = config.get_webhook_info()
        logger.info(f"Memulai webhook di {config.LISTEN_IP}:{config.PORT}")
        logger.info(f"Webhook URL: {webhook_info['url']}")

        try:
            # Inisialisasi aplikasi
            await self.application.initialize()

            # Mulai aplikasi
            await self.application.start()

            # Setup webhook
            await self.application.updater.start_webhook(
                listen=config.LISTEN_IP,
                port=config.PORT,
                url_path=config.WEBHOOK_PATH,
                webhook_url=webhook_info["url"],
                allowed_updates=webhook_info["allowed_updates"],
                drop_pending_updates=webhook_info["drop_pending_updates"],
            )

            logger.info("Webhook berhasil dimulai")

            # Tunggu sinyal shutdown
            await self._shutdown_event.wait()

        except Exception as e:
            logger.error(f"Gagal memulai webhook: {e}")
            raise
        finally:
            await self.stop()

    async def start_polling(self) -> None:
        """Mulai bot dengan polling (untuk development)."""
        logger.info("Memulai bot dalam mode polling")

        try:
            # Inisialisasi dan mulai aplikasi
            await self.application.initialize()
            await self.application.start()

            # Mulai polling
            await self.application.updater.start_polling(
                allowed_updates=Update.ALL_TYPES, drop_pending_updates=True
            )

            logger.info("Polling berhasil dimulai")

            # Tunggu sinyal shutdown
            await self._shutdown_event.wait()

        except Exception as e:
            logger.error(f"Gagal memulai polling: {e}")
            raise
        finally:
            await self.stop()

    async def stop(self) -> None:
        """Hentikan bot dengan graceful."""
        if not self.application:
            return

        logger.info("Menghentikan bot...")

        try:
            # Hentikan updater
            if self.application.updater.running:
                await self.application.updater.stop()

            # Hentikan aplikasi
            if self.application.running:
                await self.application.stop()

            # Shutdown aplikasi
            await self.application.shutdown()

            logger.info("Bot berhasil dihentikan")

        except Exception as e:
            logger.error(f"Error saat shutdown bot: {e}")

    def shutdown(self) -> None:
        """Signal shutdown dari signal handler."""
        self._shutdown_event.set()


def signal_handler(bot: TelegramBot) -> None:
    """Handle sinyal shutdown dengan graceful."""

    def handler(signum, frame):
        logger.info(f"Menerima sinyal {signum}, melakukan shutdown...")
        bot.shutdown()

    return handler


async def main() -> NoReturn:
    """Entry point utama untuk bot."""
    setup_logging()
    logger.info("Memulai Cloudflare DNS Manager Bot")

    # Buat instance bot
    bot = TelegramBot()

    # Setup signal handler untuk graceful shutdown
    for sig in (signal.SIGTERM, signal.SIGINT):
        signal.signal(sig, signal_handler(bot))

    try:
        # Inisialisasi bot
        await bot.initialize()

        # Mulai bot berdasarkan konfigurasi
        if config.WEBHOOK_URL:
            await bot.start_webhook()
        else:
            logger.info("WEBHOOK_URL tidak dikonfigurasi, memulai dalam mode polling")
            await bot.start_polling()

    except KeyboardInterrupt:
        logger.info("Bot dihentikan oleh user")
    except Exception as e:
        logger.error(f"Error tidak terduga: {e}")
        sys.exit(1)
    finally:
        logger.info("Shutdown bot selesai")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Proses diinterupsi oleh user")
    except Exception as e:
        logger.error(f"Error fatal: {e}")
        sys.exit(1)
