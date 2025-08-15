import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CommandHandler, ContextTypes, CallbackQueryHandler
from telegram.constants import ParseMode
from database.models.users_model import user_exists
from database.models.cf_accounts_model import get_cloudflare_account

logger = logging.getLogger(__name__)


async def menu_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /menu command and display the main menu."""
    try:
        user = update.effective_user

        # Check if user is registered
        if not await user_exists(user.id):
            await update.message.reply_text(
                "⚠️ Silakan jalankan /start terlebih dahulu untuk menggunakan bot ini."
            )
            return

        # Get Cloudflare account data
        account = await get_cloudflare_account(user.id)

        if account:
            # Display menu for users with Cloudflare account
            keyboard = [
                [
                    InlineKeyboardButton(
                        "📋 Lihat Record", callback_data="get_records"
                    ),
                    InlineKeyboardButton(
                        "📝 Tambah Record", callback_data="add_records"
                    ),
                ],
                [
                    InlineKeyboardButton("♻️ Edit Record", callback_data="edit_record"),
                    InlineKeyboardButton(
                        "🗑️ Hapus Record", callback_data="remove_record"
                    ),
                ],
                [InlineKeyboardButton("⚙️ Others Menu", callback_data="others_menu")],
            ]

            # Hide API Key for security (show only first and last 4 characters)
            api_key_hidden = (
                f"`{account['api_key'][:4]}...{account['api_key'][-4:]}`"
                if account.get("api_key") and len(account["api_key"]) > 8
                else "`Tidak tersedia`"
            )

            text = (
                "*🌐 CLOUDFLARE DNS MANAGER*\n"
                "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                f"👤 *Nama:* `{user.first_name or 'N/A'}`\n"
                f"📧 *Email:* `{account.get('email', 'N/A')}`\n"
                f"🔑 *API Key:* {api_key_hidden}\n"
                f"🌍 *Zone:* `{account.get('zone_name', 'N/A')}`\n"
                "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                "Pilih menu di bawah untuk mengelola DNS Anda\\."
            )
        else:
            # Display menu for users without Cloudflare account
            keyboard = [
                [
                    InlineKeyboardButton(
                        "➕ Tambah Akun Cloudflare", callback_data="add_cf_account"
                    )
                ],
            ]

            text = (
                "*🌐 CLOUDFLARE DNS MANAGER*\n"
                "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                f"👤 *Nama:* `{user.first_name or 'N/A'}`\n"
                "📱 *Status:* `Belum ada akun terdaftar`\n"
                "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                "Silakan tambahkan akun Cloudflare Anda untuk memulai mengelola DNS\\."
            )

        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text(
            text, parse_mode=ParseMode.MARKDOWN_V2, reply_markup=reply_markup
        )

        logger.info(f"Menu displayed for user {user.id}")

    except Exception as e:
        logger.error(f"Error in menu command for user {update.effective_user.id}: {e}")
        await update.message.reply_text(
            "⚠️ Terjadi kesalahan saat menampilkan menu. Silakan coba lagi."
        )


async def menu_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle all button clicks from the menu."""
    try:
        query = update.callback_query
        await query.answer()

        user = query.from_user
        callback_data = query.data

        logger.info(f"User {user.id} clicked: {callback_data}")

        if callback_data == "get_records":
            await query.edit_message_text(
                text="🚧 *Fitur Lihat Record DNS*\n\n"
                "Fitur ini sedang dalam pengembangan\\.\n"
                "Akan menampilkan semua record DNS yang ada di zone Anda\\.\n\n"
                "Gunakan /menu untuk kembali ke menu utama\\.",
                parse_mode=ParseMode.MARKDOWN_V2,
            )

        # Note: DNS record handlers are now handled in separate files
        # The following callbacks are handled by dedicated handlers:
        # - get_records, add_records, edit_record, remove_record
        # - others_menu

        else:
            await query.edit_message_text(
                text=f"⚠️ Aksi tidak dikenal: {callback_data}\n\n"
                "Gunakan /menu untuk kembali ke menu utama\\.",
                parse_mode=ParseMode.MARKDOWN_V2,
            )

    except Exception as e:
        logger.error(f"Error in menu callback for user {update.effective_user.id}: {e}")
        try:
            await update.callback_query.edit_message_text(
                "⚠️ Terjadi kesalahan. Gunakan /menu untuk mencoba lagi."
            )
        except:
            # If edit fails, send new message
            await update.effective_chat.send_message(
                "⚠️ Terjadi kesalahan. Gunakan /menu untuk mencoba lagi."
            )


menu_handlers = [
    CommandHandler("menu", menu_command),
    CallbackQueryHandler(menu_callback, pattern="^(?!add_cf_account|get_records|add_records|edit_record|remove_record|others_menu|back_to_main_menu|switch_zone|help_menu).*$"),
]
