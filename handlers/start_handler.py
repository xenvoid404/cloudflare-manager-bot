from telegram import Update
from telegram.ext import CommandHandler, ContextTypes
from telegram.constants import ParseMode
from database.models.users_model import save_user


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Menangani perintah /start"""
    user = update.effective_user
    save_user(
        {
            "chat_id": user.id,
            "username": user.username,
            "first_name": user.first_name,
            "last_name": user.last_name,
        }
    )

    welcome_msg = (
        f"👋 Halo *{user.first_name}*! Selamat datang di *Cloudflare DNS Manager Bot*.\n\n"
        "Bot ini membantu Anda mengelola DNS Cloudflare langsung dari Telegram.\n\n"
        "Ketik /menu untuk mengakses menu utama."
    )
    await update.message.reply_text(welcome_msg, parse_mode=ParseMode.MARKDOWN)


start_command_handler = CommandHandler("start", start)
