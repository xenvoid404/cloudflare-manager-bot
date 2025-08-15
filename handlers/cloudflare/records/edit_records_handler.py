import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, CallbackQueryHandler
from telegram.constants import ParseMode
from database.models.users_model import user_exists
from database.models.cf_accounts_model import get_cloudflare_account

logger = logging.getLogger(__name__)


async def edit_records_handler(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> None:
    """Handle Edit Records button click."""
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
                    "Single Record", callback_data="edit_single_record"
                ),
                InlineKeyboardButton(
                    "From File", callback_data="edit_record_from_file"
                ),
            ],
            [
                InlineKeyboardButton(
                    "🔙 Back to Main Menu", callback_data="back_to_main_menu"
                ),
            ],
        ]

        await query.edit_message_text(
            text="*♻️ Edit Record DNS*\n\n"
            "Pilih cara mengedit record DNS:\n\n"
            "1\\. *Single Record* \\- Edit satu DNS Record\n"
            "2\\. *From File* \\- Edit banyak DNS Record dari file JSON",
            parse_mode=ParseMode.MARKDOWN_V2,
            reply_markup=InlineKeyboardMarkup(keyboard),
        )

        logger.info(f"Edit records menu displayed for user {user.id}")

    except Exception as e:
        logger.error(
            f"Error in edit records handler for user {update.effective_user.id}: {e}"
        )
        await update.callback_query.edit_message_text(
            "⚠️ Terjadi kesalahan. Gunakan /menu untuk mencoba lagi."
        )


edit_records_handlers = [
    CallbackQueryHandler(edit_records_handler, pattern="^edit_record$"),
]
