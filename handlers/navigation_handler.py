import logging
from telegram import Update
from telegram.ext import ContextTypes, CallbackQueryHandler
from handlers.menu_handler import menu_command

logger = logging.getLogger(__name__)


async def back_to_main_menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle back to main menu button click."""
    try:
        query = update.callback_query
        await query.answer()
        
        # Delete the current message
        await query.delete_message()
        
        # Create a fake update for menu command
        fake_update = Update(
            update_id=update.update_id,
            message=query.message,
            effective_chat=update.effective_chat,
            effective_user=update.effective_user,
        )
        
        # Call menu command
        await menu_command(fake_update, context)
        
        logger.info(f"User {update.effective_user.id} returned to main menu")
        
    except Exception as e:
        logger.error(f"Error returning to main menu for user {update.effective_user.id}: {e}")
        await update.effective_chat.send_message(
            "⚠️ Terjadi kesalahan. Gunakan /menu untuk kembali ke menu utama."
        )


# Handler exports
navigation_handlers = [
    CallbackQueryHandler(back_to_main_menu, pattern="^back_to_main_menu$"),
]