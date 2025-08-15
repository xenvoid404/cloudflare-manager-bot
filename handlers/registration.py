from telegram.ext import Application
from handlers.start_handler import start_command_handler
from handlers.menu_handler import menu_handlers


def register_all_handlers(application: Application):
    """Fungsi terpusat untuk mendaftarkan semua handler ke aplikasi bot."""
    # Daftarkan handler tunggal
    application.add_handler(start_command_handler)

    # Daftarkan grup handler (seperti di menu_handler)
    for handler in menu_handlers:
        application.add_handler(handler)
