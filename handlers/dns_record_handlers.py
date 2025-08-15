import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, CallbackQueryHandler
from telegram.constants import ParseMode
from database.models.users_model import user_exists
from database.models.cf_accounts_model import get_cloudflare_account

logger = logging.getLogger(__name__)


async def get_records_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle Get Records button click."""
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
                parse_mode=ParseMode.MARKDOWN_V2
            )
            return

        keyboard = [
            [
                InlineKeyboardButton("Single Record", callback_data="get_single_record"),
                InlineKeyboardButton("From File", callback_data="get_record_from_file"),
            ],
            [
                InlineKeyboardButton("🔙 Back to Main Menu", callback_data="back_to_main_menu"),
            ],
        ]

        await query.edit_message_text(
            text="*📋 Lihat Record DNS*\n\n"
            "Pilih cara melihat record DNS:\n\n"
            "1\\. *Single Record* \\- Lihat record DNS tertentu\n"
            "2\\. *From File* \\- Lihat semua record DNS",
            parse_mode=ParseMode.MARKDOWN_V2,
            reply_markup=InlineKeyboardMarkup(keyboard),
        )

        logger.info(f"Get records menu displayed for user {user.id}")

    except Exception as e:
        logger.error(f"Error in get records handler for user {update.effective_user.id}: {e}")
        await update.callback_query.edit_message_text(
            "⚠️ Terjadi kesalahan. Gunakan /menu untuk mencoba lagi."
        )


async def add_records_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
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
                parse_mode=ParseMode.MARKDOWN_V2
            )
            return

        keyboard = [
            [
                InlineKeyboardButton("Single Record", callback_data="add_single_record"),
                InlineKeyboardButton("From File", callback_data="add_record_from_file"),
            ],
            [
                InlineKeyboardButton("🔙 Back to Main Menu", callback_data="back_to_main_menu"),
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
        logger.error(f"Error in add records handler for user {update.effective_user.id}: {e}")
        await update.callback_query.edit_message_text(
            "⚠️ Terjadi kesalahan. Gunakan /menu untuk mencoba lagi."
        )


async def edit_records_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
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
                parse_mode=ParseMode.MARKDOWN_V2
            )
            return

        keyboard = [
            [
                InlineKeyboardButton("Single Record", callback_data="edit_single_record"),
                InlineKeyboardButton("From File", callback_data="edit_record_from_file"),
            ],
            [
                InlineKeyboardButton("🔙 Back to Main Menu", callback_data="back_to_main_menu"),
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
        logger.error(f"Error in edit records handler for user {update.effective_user.id}: {e}")
        await update.callback_query.edit_message_text(
            "⚠️ Terjadi kesalahan. Gunakan /menu untuk mencoba lagi."
        )


async def remove_records_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle Remove Records button click."""
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
                parse_mode=ParseMode.MARKDOWN_V2
            )
            return

        keyboard = [
            [
                InlineKeyboardButton("Single Record", callback_data="remove_single_record"),
                InlineKeyboardButton("From File", callback_data="remove_record_from_file"),
            ],
            [
                InlineKeyboardButton("🔙 Back to Main Menu", callback_data="back_to_main_menu"),
            ],
        ]

        await query.edit_message_text(
            text="*🗑️ Hapus Record DNS*\n\n"
            "Pilih cara menghapus record DNS:\n\n"
            "1\\. *Single Record* \\- Hapus satu DNS Record\n"
            "2\\. *From File* \\- Hapus banyak DNS Record dari file JSON",
            parse_mode=ParseMode.MARKDOWN_V2,
            reply_markup=InlineKeyboardMarkup(keyboard),
        )

        logger.info(f"Remove records menu displayed for user {user.id}")

    except Exception as e:
        logger.error(f"Error in remove records handler for user {update.effective_user.id}: {e}")
        await update.callback_query.edit_message_text(
            "⚠️ Terjadi kesalahan. Gunakan /menu untuk mencoba lagi."
        )


async def dns_record_actions(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle DNS record sub-actions (Single Record, From File)."""
    try:
        query = update.callback_query
        await query.answer()

        user = query.from_user
        callback_data = query.data

        logger.info(f"User {user.id} clicked: {callback_data}")

        # Handle Single Record actions
        if callback_data in ["get_single_record", "add_single_record", "edit_single_record", "remove_single_record"]:
            action_name = callback_data.replace("_single_record", "").replace("_", " ").title()
            await query.edit_message_text(
                text=f"🚧 *{action_name} Single Record*\n\n"
                "Fitur ini sedang dalam pengembangan\\.\n\n"
                "Fitur ini akan memungkinkan Anda untuk:\n"
                "• Memilih record DNS yang spesifik\n"
                f"• {action_name.lower()} record tersebut\n"
                "• Melihat detail lengkap record\n\n"
                "Gunakan /menu untuk kembali ke menu utama\\.",
                parse_mode=ParseMode.MARKDOWN_V2,
            )

        # Handle From File actions
        elif callback_data in ["get_record_from_file", "add_record_from_file", "edit_record_from_file", "remove_record_from_file"]:
            action_name = callback_data.replace("_record_from_file", "").replace("_", " ").title()
            await query.edit_message_text(
                text=f"🚧 *{action_name} Record From File*\n\n"
                "Fitur ini sedang dalam pengembangan\\.\n\n"
                "Fitur ini akan memungkinkan Anda untuk:\n"
                "• Upload file JSON dengan format tertentu\n"
                f"• {action_name.lower()} banyak record sekaligus\n"
                "• Melihat progress dan hasil operasi\n\n"
                "Gunakan /menu untuk kembali ke menu utama\\.",
                parse_mode=ParseMode.MARKDOWN_V2,
            )

        else:
            await query.edit_message_text(
                text=f"⚠️ Aksi tidak dikenal: {callback_data}\n\n"
                "Gunakan /menu untuk kembali ke menu utama\\.",
                parse_mode=ParseMode.MARKDOWN_V2,
            )

    except Exception as e:
        logger.error(f"Error in DNS record actions for user {update.effective_user.id}: {e}")
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
dns_record_handlers = [
    CallbackQueryHandler(get_records_handler, pattern="^get_records$"),
    CallbackQueryHandler(add_records_handler, pattern="^add_records$"),
    CallbackQueryHandler(edit_records_handler, pattern="^edit_record$"),
    CallbackQueryHandler(remove_records_handler, pattern="^remove_record$"),
    CallbackQueryHandler(dns_record_actions, pattern="^(get_single_record|add_single_record|edit_single_record|remove_single_record|get_record_from_file|add_record_from_file|edit_record_from_file|remove_record_from_file)$"),
]