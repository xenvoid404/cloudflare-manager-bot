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
    """Handle the /start command with improved user experience."""
    user = update.effective_user

    # Save user information to database
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

    # Create welcome message with user's name
    welcome_msg = safe_format_message(
        Messages.Start.WELCOME, name=get_user_display_name(user)
    )

    await send_response(update, welcome_msg)


start_command_handler = CommandHandler("start", start_command)
