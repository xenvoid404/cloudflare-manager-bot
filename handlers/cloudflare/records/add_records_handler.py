import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, CallbackQueryHandler
from telegram.constants import ParseMode
from database.models.users_model import user_exists
from database.models.cf_accounts_model import get_cloudflare_account

logger = logging.getLogger(__name__)


async def add_records_handler(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> None:
    """Handle Add Records button click."""
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

        # Check if user has Cloudflare account
        account = await get_cloudflare_account(user.id)
        if not account:
            await query.edit_message_text(
                "⚠️ Anda belum menambahkan akun Cloudflare\\. "
                "Gunakan /menu dan pilih 'Tambah Akun Cloudflare'\\.",
                parse_mode=ParseMode.MARKDOWN_V2,
            )
            return

        keyboard = [
            [
                InlineKeyboardButton(
                    "Single Record", callback_data="add_single_record"
                ),
                InlineKeyboardButton("From File", callback_data="add_record_from_file"),
            ],
            [
                InlineKeyboardButton(
                    "🔙 Back to Main Menu", callback_data="back_to_main_menu"
                ),
            ],
        ]

        await query.edit_message_text(
            text="*📝 Tambah Record DNS*\n\n"
            "Pilih cara menambah record DNS:\n\n"
            "1\\. *Single Record* \\- Tambah satu DNS Record baru\n"
            "2\\. *From File* \\- Tambah banyak DNS Record dari file JSON",
            parse_mode=ParseMode.MARKDOWN_V2,
            reply_markup=InlineKeyboardMarkup(keyboard),
        )

        logger.info(f"Add records menu displayed for user {user.id}")

    except Exception as e:
        logger.error(
            f"Error in add records handler for user {update.effective_user.id}: {e}"
        )
        await update.callback_query.edit_message_text(
            "⚠️ Terjadi kesalahan. Gunakan /menu untuk mencoba lagi."
        )


add_records_handlers = [
    CallbackQueryHandler(add_records_handler, pattern="^add_records$"),
]
