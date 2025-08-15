import logging
from telegram import Update
from telegram.ext import CommandHandler, ContextTypes, CallbackQueryHandler
from telegram.constants import ParseMode

from database.models.cf_accounts_model import get_cloudflare_account
from constants import Messages, Buttons, CallbackData, Patterns
from utils.decorators import authenticated_handler, handle_errors, log_user_action
from utils.helpers import (
    mask_api_key,
    get_user_display_name,
    safe_format_message,
    send_response,
    create_inline_keyboard,
)

logger = logging.getLogger(__name__)


@authenticated_handler
async def menu_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle command /menu dan callback untuk menampilkan menu utama."""
    user = update.effective_user

    # Dapatkan data akun Cloudflare
    account = await get_cloudflare_account(user.id)

    if account:
        # Tampilkan menu untuk user dengan akun Cloudflare
        keyboard_buttons = [
            [
                (Buttons.VIEW_RECORDS, CallbackData.GET_RECORDS),
                (Buttons.ADD_RECORD, CallbackData.ADD_RECORDS),
            ],
            [
                (Buttons.EDIT_RECORD, CallbackData.EDIT_RECORDS),
                (Buttons.DELETE_RECORD, CallbackData.REMOVE_RECORDS),
            ],
            [
                (Buttons.OTHERS_MENU, CallbackData.OTHERS_MENU),
            ],
        ]

        # Format pesan dengan info akun
        text = safe_format_message(
            Messages.Menu.MAIN_WITH_ACCOUNT,
            name=get_user_display_name(user),
            email=account.get("email", "N/A"),
            api_key_masked=mask_api_key(account.get("api_key", "")),
            zone_name=account.get("zone_name", "N/A"),
        )
    else:
        # Tampilkan menu untuk user tanpa akun Cloudflare
        keyboard_buttons = [
            [
                (Buttons.ADD_CLOUDFLARE, CallbackData.ADD_CLOUDFLARE),
            ],
        ]

        text = safe_format_message(
            Messages.Menu.MAIN_WITHOUT_ACCOUNT, name=get_user_display_name(user)
        )

    keyboard = create_inline_keyboard(keyboard_buttons)
    await send_response(update, text, reply_markup=keyboard)


async def menu_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle semua klik button dari menu."""
    try:
        query = update.callback_query
        await query.answer()

        user = query.from_user
        callback_data = query.data

        logger.info(f"User {user.id} mengklik: {callback_data}")

        await query.edit_message_text(
            text=f"Aksi tidak dikenal: {callback_data}\n\n"
            "Gunakan /menu untuk kembali ke menu utama\\.",
            parse_mode=ParseMode.MARKDOWN_V2,
        )

    except Exception as e:
        logger.error(f"Error dalam menu callback untuk user {update.effective_user.id}: {e}")
        try:
            await update.callback_query.edit_message_text(
                "Terjadi kesalahan. Gunakan /menu untuk mencoba lagi."
            )
        except:
            # Jika edit gagal, kirim pesan baru
            await update.effective_chat.send_message(
                "Terjadi kesalahan. Gunakan /menu untuk mencoba lagi."
            )


@handle_errors
@log_user_action("back_to_main_menu")
async def back_to_main_menu_callback(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> None:
    """Handle callback kembali ke menu utama."""
    query = update.callback_query
    await query.answer()

    # Panggil menu_command untuk menampilkan menu utama
    await menu_command(update, context)


menu_handlers = [
    CommandHandler("menu", menu_command),
    CallbackQueryHandler(
        back_to_main_menu_callback, pattern=f"^{CallbackData.BACK_TO_MAIN_MENU}$"
    ),
    CallbackQueryHandler(
        menu_callback, pattern=Patterns.get_menu_callback_exclusions()
    ),
]
