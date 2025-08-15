import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, CallbackQueryHandler, CommandHandler
from telegram.constants import ParseMode
from database.models.users_model import user_exists

logger = logging.getLogger(__name__)


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /help command."""
    try:
        help_text = (
            "*📖 Bantuan Cloudflare DNS Manager*\n\n"
            "*Fitur yang tersedia:*\n"
            "• 📝 Tambah Record \\- Menambah record DNS baru\n"
            "• 📋 Lihat Record \\- Melihat semua record DNS\n"
            "• ♻️ Edit Record \\- Mengubah record DNS yang ada\n"
            "• 🗑️ Hapus Record \\- Menghapus record DNS\n"
            "• ⚙️ Others Menu \\- Menu tambahan dan pengaturan\n\n"
            "*Perintah:*\n"
            "• /start \\- Memulai bot dan registrasi\n"
            "• /menu \\- Menu utama\n"
            "• /help \\- Bantuan\n\n"
            "*Tips:*\n"
            "• Pastikan email, API Key, dan Account ID Cloudflare sudah benar\n"
            "• API Key dapat ditemukan di My Profile → API Tokens → Global API Key\n"
            "• Account ID dapat ditemukan di Dashboard sidebar kanan\n\n"
            "Gunakan /menu untuk mengakses menu utama\\."
        )

        await update.message.reply_text(
            text=help_text, parse_mode=ParseMode.MARKDOWN_V2
        )

        logger.info(f"Help displayed for user {update.effective_user.id}")

    except Exception as e:
        logger.error(f"Error in help command for user {update.effective_user.id}: {e}")
        await update.message.reply_text(
            "⚠️ Terjadi kesalahan saat menampilkan bantuan. Silakan coba lagi."
        )


async def others_menu_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle Others Menu button click."""
    try:
        query = update.callback_query
        await query.answer()

        user = query.from_user

        # Check if user is registered
        if not await user_exists(user.id):
            await query.edit_message_text(
                "⚠️ Silakan jalankan /start terlebih dahulu untuk menggunakan bot ini."
            )
            return

        keyboard = [
            [
                InlineKeyboardButton("🔄 Switch Zone", callback_data="switch_zone"),
                InlineKeyboardButton("❓ Help", callback_data="help_menu"),
            ],
            [
                InlineKeyboardButton("🔙 Back to Main Menu", callback_data="back_to_main_menu"),
            ],
        ]

        await query.edit_message_text(
            text="*⚙️ Others Menu*\n\n"
            "Pilih opsi yang tersedia:\n\n"
            "🔄 *Switch Zone* \\- Ganti zone yang dikelola\n"
            "❓ *Help* \\- Bantuan penggunaan bot",
            parse_mode=ParseMode.MARKDOWN_V2,
            reply_markup=InlineKeyboardMarkup(keyboard),
        )

        logger.info(f"Others menu displayed for user {user.id}")

    except Exception as e:
        logger.error(f"Error in others menu for user {update.effective_user.id}: {e}")
        await update.callback_query.edit_message_text(
            "⚠️ Terjadi kesalahan. Gunakan /menu untuk mencoba lagi."
        )


async def others_menu_actions(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle actions from Others Menu."""
    try:
        query = update.callback_query
        await query.answer()

        user = query.from_user
        callback_data = query.data

        logger.info(f"User {user.id} clicked: {callback_data}")

        if callback_data == "switch_zone":
            await query.edit_message_text(
                text="🚧 *Switch Zone*\n\n"
                "Fitur ini sedang dalam pengembangan\\.\n\n"
                "Fitur ini akan memungkinkan Anda untuk:\n"
                "• Melihat daftar zone yang tersedia\n"
                "• Mengganti zone aktif\n"
                "• Mengelola beberapa zone sekaligus\n\n"
                "Gunakan /menu untuk kembali ke menu utama\\.",
                parse_mode=ParseMode.MARKDOWN_V2,
            )

        elif callback_data == "help_menu":
            help_text = (
                "*📖 Bantuan Cloudflare DNS Manager*\n\n"
                "*Fitur yang tersedia:*\n"
                "• 📝 Tambah Record \\- Menambah record DNS baru\n"
                "• 📋 Lihat Record \\- Melihat semua record DNS\n"
                "• ♻️ Edit Record \\- Mengubah record DNS yang ada\n"
                "• 🗑️ Hapus Record \\- Menghapus record DNS\n"
                "• ⚙️ Others Menu \\- Menu tambahan dan pengaturan\n\n"
                "*Perintah:*\n"
                "• /start \\- Memulai bot dan registrasi\n"
                "• /menu \\- Menu utama\n"
                "• /help \\- Bantuan\n\n"
                "*Tips:*\n"
                "• Pastikan email, API Key, dan Account ID Cloudflare sudah benar\n"
                "• API Key dapat ditemukan di My Profile → API Tokens → Global API Key\n"
                "• Account ID dapat ditemukan di Dashboard sidebar kanan\n\n"
                "Gunakan /menu untuk mengakses menu utama\\."
            )

            keyboard = [
                [
                    InlineKeyboardButton("🔙 Back to Others Menu", callback_data="others_menu"),
                ],
                [
                    InlineKeyboardButton("🏠 Main Menu", callback_data="back_to_main_menu"),
                ],
            ]

            await query.edit_message_text(
                text=help_text,
                parse_mode=ParseMode.MARKDOWN_V2,
                reply_markup=InlineKeyboardMarkup(keyboard),
            )

        else:
            await query.edit_message_text(
                text=f"⚠️ Aksi tidak dikenal: {callback_data}\n\n"
                "Gunakan /menu untuk kembali ke menu utama\\.",
                parse_mode=ParseMode.MARKDOWN_V2,
            )

    except Exception as e:
        logger.error(f"Error in others menu actions for user {update.effective_user.id}: {e}")
        try:
            await update.callback_query.edit_message_text(
                "⚠️ Terjadi kesalahan. Gunakan /menu untuk mencoba lagi."
            )
        except:
            # If edit fails, send new message
            await update.effective_chat.send_message(
                "⚠️ Terjadi kesalahan. Gunakan /menu untuk mencoba lagi."
            )


# Handler exports
other_menu_handlers = [
    CommandHandler("help", help_command),
    CallbackQueryHandler(others_menu_callback, pattern="^others_menu$"),
    CallbackQueryHandler(others_menu_actions, pattern="^(switch_zone|help_menu)$"),
]