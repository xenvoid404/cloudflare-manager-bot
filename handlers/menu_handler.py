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
                [InlineKeyboardButton("❓ Bantuan", callback_data="help")],
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
                [InlineKeyboardButton("❓ Bantuan", callback_data="help")],
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

        if callback_data == "add_cf_account":
            await query.edit_message_text(
                text="🚧 *Tambah Akun Cloudflare*\n\n"
                "Fitur ini sedang dalam pengembangan\\.\n"
                "Akan memungkinkan Anda menambahkan:\n"
                "• Email Cloudflare\n"
                "• API Key\n"
                "• Zone ID\n\n"
                "Gunakan /menu untuk kembali ke menu utama\\.",
                parse_mode=ParseMode.MARKDOWN_V2,
            )

        elif callback_data == "get_records":
            await query.edit_message_text(
                text="🚧 *Fitur Lihat Record DNS*\n\n"
                "Fitur ini sedang dalam pengembangan\\.\n"
                "Akan menampilkan semua record DNS yang ada di zone Anda\\.\n\n"
                "Gunakan /menu untuk kembali ke menu utama\\.",
                parse_mode=ParseMode.MARKDOWN_V2,
            )

        elif callback_data == "add_records":
            keyboard = [
                [
                    InlineKeyboardButton(
                        "Single Record", callback_data="add_single_record"
                    ),
                    InlineKeyboardButton(
                        "From File", callback_data="add_record_from_file"
                    ),
                ],
                [
                    InlineKeyboardButton(
                        "Back To Main Menu", callback_data="back_to_main_menu"
                    )
                ],
            ]

            await query.edit_message_text(
                text="*Tambah Record DNS*\n\n"
                "1. *Single Record*: Tambah satu DNS Record baru\\.\n"
                "2. *From File*: Tambah banyak DNS Record dari file JSON\\.",
                parse_mode=ParseMode.MARKDOWN_V2,
                reply_markup=InlineKeyboardMarkup(keyboard),
            )

        elif callback_data == "edit_records":
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
                        "Back To Main Menu", callback_data="back_to_main_menu"
                    )
                ],
            ]

            await query.edit_message_text(
                text="*Edit Record DNS*\n\n"
                "1. *Single Record*: Edit satu DNS Record baru\\.\n"
                "2. *From File*: Edit banyak DNS Record dari file JSON\\.",
                parse_mode=ParseMode.MARKDOWN_V2,
                reply_markup=InlineKeyboardMarkup(keyboard),
            )

        elif callback_data == "remove_record":
            keyboard = [
                [
                    InlineKeyboardButton(
                        "Single Record", callback_data="remove_single_record"
                    ),
                    InlineKeyboardButton(
                        "From File", callback_data="remove_record_from_file"
                    ),
                ],
                [
                    InlineKeyboardButton(
                        "Back To Main Menu", callback_data="back_to_main_menu"
                    )
                ],
            ]

            await query.edit_message_text(
                text="*Hapus Record DNS*\n\n"
                "1. *Single Record*: Hapus satu DNS Record baru\\.\n"
                "2. *From File*: Hapus banyak DNS Record dari file JSON\\.",
                parse_mode=ParseMode.MARKDOWN_V2,
                reply_markup=InlineKeyboardMarkup(keyboard),
            )

        elif callback_data == "others_menu":
            await query.edit_message_text(
                text="🚧 *Menu Lainnya*\n\n"
                "Fitur ini sedang dalam pengembangan\\.\n\n"
                "Gunakan /menu untuk kembali ke menu utama\\.",
                parse_mode=ParseMode.MARKDOWN_V2,
            )

        elif callback_data == "help":
            help_text = (
                "*📖 Bantuan Cloudflare DNS Manager*\n\n"
                "*Fitur yang tersedia:*\n"
                "• 📝 Tambah Record \\- Menambah record DNS baru\n"
                "• 📋 Lihat Record \\- Melihat semua record DNS\n"
                "• ⚙️ Edit Akun \\- Mengubah informasi akun\n"
                "• 🗑️ Hapus Akun \\- Menghapus akun dari bot\n\n"
                "*Perintah:*\n"
                "• /start \\- Memulai bot\n"
                "• /menu \\- Menu utama\n"
                "• /help \\- Bantuan\n\n"
                "Gunakan /menu untuk kembali ke menu utama\\."
            )

            await query.edit_message_text(
                text=help_text, parse_mode=ParseMode.MARKDOWN_V2
            )

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
    CallbackQueryHandler(menu_callback),
]
