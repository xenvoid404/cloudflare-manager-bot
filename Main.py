import logging
import config
from telegram import Update
from telegram.ext import Application
from database import db
from handlers.registration import register_all_handlers

# Setup logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logging.getLogger("httpx").setLevel(logging.WARNING)
logger = logging.getLogger(__name__)


def main() -> None:
    """
    Fungsi utama untuk setup dan menjalankan bot.
    Fungsi ini sekarang synchronous karena run_webhook() adalah blocking call
    yang mengelola event loop-nya sendiri.
    """

    # 1. Inisialisasi Aplikasi Bot
    application = Application.builder().token(config.BOT_TOKEN).build()

    # 2. Daftarkan semua handler
    register_all_handlers(application)
    logger.info("Semua handler telah didaftarkan.")

    # 3. Inisialisasi database
    db.init_db()
    logger.info("Database telah diinisialisasi.")

    # 4. Jalankan bot dengan mode webhook
    # run_webhook() adalah fungsi blocking. Ia akan terus berjalan sampai
    # prosesnya dihentikan (misal dengan Ctrl+C).
    logger.info(f"Menjalankan webhook di {config.LISTEN_IP}:{config.PORT}")

    # Menghapus 'await' dan mengubah 'main' menjadi fungsi sync
    application.run_webhook(
        listen=config.LISTEN_IP,
        port=config.PORT,
        webhook_url=f"{config.WEBHOOK_URL}/{config.WEBHOOK_PATH}",
        allowed_updates=Update.ALL_TYPES,
        secret_token=config.WEBHOOK_PATH,  # Menambah lapisan keamanan
    )


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        logger.info("Proses dihentikan oleh pengguna.")
    except Exception as e:
        logger.error(f"Terjadi error tak terduga: {e}")
