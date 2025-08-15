import logging
from telegram import Update
from telegram.ext import CommandHandler, ContextTypes
from telegram.constants import ParseMode

from database.models.users_model import save_user
from constants import Messages
from utils.decorators import handle_errors, log_user_action
from utils.helpers import get_user_display_name, safe_format_message, send_response

logger = logging.getLogger(__name__)


@handle_errors
@log_user_action("start_command")
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle command /start dengan pengalaman user yang lebih baik."""
    user = update.effective_user

    # Simpan informasi user ke database
    user_data = {
        "chat_id": user.id,
        "username": user.username,
        "first_name": user.first_name,
        "last_name": user.last_name,
    }

    success = await save_user(user_data)

    if not success:
        await send_response(update, Messages.Start.SAVE_ERROR)
        return

    # Buat pesan selamat datang dengan nama user
    welcome_msg = safe_format_message(
        Messages.Start.WELCOME, name=get_user_display_name(user)
    )

    await send_response(update, welcome_msg)


start_command_handler = CommandHandler("start", start_command)
