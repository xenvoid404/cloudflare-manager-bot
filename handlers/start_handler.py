import logging
from telegram import Update
from telegram.ext import CommandHandler, ContextTypes
from telegram.constants import ParseMode
from database.models.users_model import save_user

logger = logging.getLogger(__name__)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle the /start command with improved user experience."""
    try:
        user = update.effective_user
        chat = update.effective_chat
        
        # Save user information to database
        user_data = {
            "chat_id": user.id,
            "username": user.username,
            "first_name": user.first_name,
            "last_name": user.last_name,
        }
        
        success = await save_user(user_data)
        
        if not success:
            await update.message.reply_text(
                "⚠️ Terjadi kesalahan saat menyimpan data Anda. Silakan coba lagi nanti.",
                parse_mode=ParseMode.MARKDOWN
            )
            return
        
        # Create welcome message
        welcome_msg = (
            f"👋 Halo *{user.first_name}*! Selamat datang di *Cloudflare DNS Manager Bot*\\.\n\n"
            "Bot ini membantu Anda mengelola DNS Cloudflare langsung dari Telegram\\.\n\n"
            "🔧 *Fitur yang tersedia:*\n"
            "• Menambah record DNS\n"
            "• Melihat record yang ada\n"
            "• Mengelola akun Cloudflare\n\n"
            "Ketik /menu untuk mengakses menu utama\\."
        )
        
        await update.message.reply_text(
            welcome_msg, 
            parse_mode=ParseMode.MARKDOWN_V2
        )
        
        logger.info(f"User {user.id} ({user.username}) started the bot")
        
    except Exception as e:
        logger.error(f"Error in start command: {e}")
        await update.message.reply_text(
            "⚠️ Terjadi kesalahan. Silakan coba lagi nanti."
        )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle the /help command."""
    try:
        help_text = (
            "*📖 Bantuan Cloudflare DNS Manager Bot*\n\n"
            "*Perintah yang tersedia:*\n"
            "• /start \\- Memulai bot dan pendaftaran\n"
            "• /menu \\- Menampilkan menu utama\n"
            "• /help \\- Menampilkan bantuan ini\n\n"
            "*Cara penggunaan:*\n"
            "1\\. Mulai dengan /start\n"
            "2\\. Tambahkan akun Cloudflare di /menu\n"
            "3\\. Kelola record DNS Anda\n\n"
            "*Butuh bantuan lebih lanjut?*\n"
            "Hubungi administrator bot\\."
        )
        
        await update.message.reply_text(
            help_text,
            parse_mode=ParseMode.MARKDOWN_V2
        )
        
        logger.info(f"Help command used by user {update.effective_user.id}")
        
    except Exception as e:
        logger.error(f"Error in help command: {e}")
        await update.message.reply_text(
            "⚠️ Terjadi kesalahan saat menampilkan bantuan."
        )

# Export handlers
start_command_handler = CommandHandler("start", start)
help_command_handler = CommandHandler("help", help_command)
