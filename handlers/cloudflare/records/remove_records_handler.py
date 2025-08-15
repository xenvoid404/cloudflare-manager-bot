from telegram.ext import CallbackQueryHandler

from constants import CallbackData
from .base_records_handler import RemoveRecordsHandler

# Create handler instance
remove_handler = RemoveRecordsHandler()

# Handler exports
remove_records_handlers = [
    CallbackQueryHandler(
        remove_handler.handle_operation, pattern=f"^{CallbackData.REMOVE_RECORDS}$"
    ),
]
