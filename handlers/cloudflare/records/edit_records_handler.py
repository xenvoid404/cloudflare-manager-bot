from telegram.ext import CallbackQueryHandler

from constants import CallbackData
from .base_records_handler import EditRecordsHandler

# Create handler instance
edit_handler = EditRecordsHandler()

# Handler exports
edit_records_handlers = [
    CallbackQueryHandler(
        edit_handler.handle_operation, pattern=f"^{CallbackData.EDIT_RECORDS}$"
    ),
]
