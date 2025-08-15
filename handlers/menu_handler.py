from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CommandHandler, ContextTypes, CallbackQueryHandler
from telegram.constants import ParseMode
from database.models.users_model import user_exists, user_has_account
from database.models.cf_accounts_model import get_cloudflare_account


async def menu_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Menangani perintah /menu dan menampilkan menu utama."""
    user = update.effective_user

    # Cek apakah pengguna sudah terdaftar (menjalankan /start)
    if not user_exists(user.id):
        await update.message.reply_text(
            "⚠️ Silakan jalankan /start terlebih dahulu untuk menggunakan bot ini."
        )
        return

    # Ambil data akun dari database
    account = get_cloudflare_account(user.id)

    if account:
        # Tampilan jika user SUDAH punya akun
        keyboard = [
            [InlineKeyboardButton("Tambah Record", callback_data="add_records")],
            [InlineKeyboardButton("Lihat Record", callback_data="get_records")],
            [InlineKeyboardButton("Hapus Akun", callback_data="remove_account")],
        ]
        # Menyembunyikan API Key
        api_key_hidden = (
            f"`{account['api_key'][:4]}...{account['api_key'][-4:]}`"
            if account["api_key"]
            else "`Tidak ada`"
        )

        text = (
            "*𝗖𝗟𝗢𝗨𝗗𝗙𝗟𝗔𝗥𝗘 𝗗𝗡𝗦 𝗠𝗔𝗡𝗔𝗚𝗘𝗥*\n"
            "────────────────────────\n"
            f"`Nama      :` `{user.first_name}`\n"
            f"`Email     :` `{account['email']}`\n"
            f"`API Key   :` {api_key_hidden}\n"
            f"`Zone Name :` `{account['zone_name']}`\n"
            "────────────────────────\n"
        )
    else:
        # Tampilan jika user BELUM punya akun
        keyboard = [
            [
                InlineKeyboardButton(
                    "➕ Tambah Akun Cloudflare", callback_data="add_cf_account"
                )
            ]
        ]
        text = (
            "*𝗖𝗟𝗢𝗨𝗗𝗙𝗟𝗔𝗥𝗘 𝗗𝗡𝗦 𝗠𝗔𝗡𝗔𝗚𝗘𝗥*\n"
            "────────────────────────\n"
            f"`Nama      :` `{user.first_name}`\n"
            "`Status    :` `Belum ada akun terdaftar.`\n"
            "────────────────────────\n"
            "Silakan tambahkan akun Cloudflare Anda untuk memulai."
        )

    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        text, parse_mode=ParseMode.MARKDOWN, reply_markup=reply_markup
    )


async def menu_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Menangani semua klik tombol dari menu."""
    query = update.callback_query
    await query.answer()

    callback_data = query.data

    if callback_data == "add_records":
        await query.edit_message_text(
            text="Fitur 'Tambah Record' sedang dalam pengembangan."
        )
    elif callback_data == "get_records":
        await query.edit_message_text(
            text="Fitur 'Lihat Record' sedang dalam pengembangan."
        )
    elif callback_data == "add_cf_account":
        await query.edit_message_text(
            text="Fitur 'Tambah Akun' sedang dalam pengembangan."
        )
    else:
        await query.edit_message_text(text=f"Anda menekan tombol: {callback_data}")


menu_handlers = [
    CommandHandler("menu", menu_command),
    CallbackQueryHandler(menu_callback),
]
