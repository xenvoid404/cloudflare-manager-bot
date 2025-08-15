import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, CallbackQueryHandler, CommandHandler
from telegram.constants import ParseMode
from database.models.users_model import user_exists
from constants import Messages

logger = logging.getLogger(__name__)


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle command /help."""
    try:
        help_text = Messages.Help.CONTENT

        await update.message.reply_text(
            text=help_text, parse_mode=ParseMode.MARKDOWN_V2
        )

        logger.info(f"Bantuan ditampilkan untuk user {update.effective_user.id}")

    except Exception as e:
        logger.error(f"Error dalam command help untuk user {update.effective_user.id}: {e}")
        await update.message.reply_text(
            "Terjadi kesalahan saat menampilkan bantuan. Silakan coba lagi."
        )


async def others_menu_callback(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> None:
    """Handle klik button Others Menu."""
    try:
        query = update.callback_query
        await query.answer()

        user = query.from_user

        # Cek apakah user sudah terdaftar
        if not await user_exists(user.id):
            await query.edit_message_text(
                "Silakan jalankan /start terlebih dahulu untuk menggunakan bot ini."
            )
            return

        keyboard = [
            [
                InlineKeyboardButton("Switch Zone", callback_data="switch_zone"),
                InlineKeyboardButton("Help", callback_data="help_menu"),
            ],
            [
                InlineKeyboardButton(
                    "Back to Main Menu", callback_data="back_to_main_menu"
                ),
            ],
        ]

        await query.edit_message_text(
            text="*Others Menu*\n\n"
            "Pilih opsi yang tersedia:\n\n"
            "*Switch Zone* - Ganti zone yang dikelola\n"
            "*Help* - Bantuan penggunaan bot",
            parse_mode=ParseMode.MARKDOWN_V2,
            reply_markup=InlineKeyboardMarkup(keyboard),
        )

        logger.info(f"Others menu ditampilkan untuk user {user.id}")

    except Exception as e:
        logger.error(f"Error dalam others menu untuk user {update.effective_user.id}: {e}")
        await update.callback_query.edit_message_text(
            "Terjadi kesalahan. Gunakan /menu untuk mencoba lagi."
        )


async def others_menu_actions(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> None:
    """Handle aksi dari Others Menu."""
    try:
        query = update.callback_query
        await query.answer()

        user = query.from_user
        callback_data = query.data

        logger.info(f"User {user.id} mengklik: {callback_data}")

        if callback_data == "switch_zone":
            await query.edit_message_text(
                text="*Switch Zone*\n\n"
                "Fitur ini sedang dalam pengembangan\\.\n\n"
                "Fitur ini akan memungkinkan Anda untuk:\n"
                "• Melihat daftar zone yang tersedia\n"
                "• Mengganti zone aktif\n"
                "• Mengelola beberapa zone sekaligus\n\n"
                "Gunakan /menu untuk kembali ke menu utama\\.",
                parse_mode=ParseMode.MARKDOWN_V2,
            )

        elif callback_data == "help_menu":
            help_text = Messages.Help.CONTENT

            keyboard = [
                [
                    InlineKeyboardButton(
                        "Back to Others Menu", callback_data="others_menu"
                    ),
                ],
                [
                    InlineKeyboardButton(
                        "Main Menu", callback_data="back_to_main_menu"
                    ),
                ],
            ]

            await query.edit_message_text(
                text=help_text,
                parse_mode=ParseMode.MARKDOWN_V2,
                reply_markup=InlineKeyboardMarkup(keyboard),
            )

        else:
            await query.edit_message_text(
                text=f"Aksi tidak dikenal: {callback_data}\n\n"
                "Gunakan /menu untuk kembali ke menu utama\\.",
                parse_mode=ParseMode.MARKDOWN_V2,
            )

    except Exception as e:
        logger.error(
            f"Error dalam others menu actions untuk user {update.effective_user.id}: {e}"
        )
        try:
            await update.callback_query.edit_message_text(
                "Terjadi kesalahan. Gunakan /menu untuk mencoba lagi."
            )
        except:
            # Jika edit gagal, kirim pesan baru
            await update.effective_chat.send_message(
                "Terjadi kesalahan. Gunakan /menu untuk mencoba lagi."
            )


other_menu_handlers = [
    CommandHandler("help", help_command),
    CallbackQueryHandler(others_menu_callback, pattern="^others_menu$"),
    CallbackQueryHandler(others_menu_actions, pattern="^(switch_zone|help_menu)$"),
]
