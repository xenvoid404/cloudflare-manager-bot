from telegram.ext import CallbackQueryHandler

from constants import CallbackData
from .base_records_handler import AddRecordsHandler

# Create handler instance
add_handler = AddRecordsHandler()

# Handler exports
add_records_handlers = [
    CallbackQueryHandler(
        add_handler.handle_operation, pattern=f"^{CallbackData.ADD_RECORDS}$"
    ),
]
