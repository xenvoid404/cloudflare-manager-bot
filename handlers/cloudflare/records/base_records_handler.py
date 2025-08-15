"""
Base handler for DNS record operations.
Provides common functionality for add, edit, remove record handlers.
"""

import logging
from abc import ABC, abstractmethod
from typing import List, Tuple
from telegram import Update
from telegram.ext import ContextTypes

from constants import Messages, Buttons, CallbackData
from utils.decorators import cloudflare_handler
from utils.helpers import safe_format_message, send_response, create_inline_keyboard

logger = logging.getLogger(__name__)


class BaseRecordsHandler(ABC):
    """
    Abstract base class for DNS record operations.
    """
    
    @property
    @abstractmethod
    def operation_name(self) -> str:
        """Name of the operation (e.g., 'menambah', 'mengedit', 'menghapus')"""
        pass
    
    @property
    @abstractmethod
    def operation_desc(self) -> str:
        """Description of the operation (e.g., 'Tambah', 'Edit', 'Hapus')"""
        pass
    
    @property
    @abstractmethod
    def title(self) -> str:
        """Title message for the operation"""
        pass
    
    @property
    @abstractmethod
    def single_callback_data(self) -> str:
        """Callback data for single record operation"""
        pass
    
    @property
    @abstractmethod
    def file_callback_data(self) -> str:
        """Callback data for file-based operation"""
        pass
    
    @cloudflare_handler
    async def handle_operation(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle the record operation menu."""
        query = update.callback_query
        await query.answer()
        
        # Create operation menu
        keyboard_buttons = [
            [
                (Buttons.SINGLE_RECORD, self.single_callback_data),
                (Buttons.FROM_FILE, self.file_callback_data),
            ],
            [
                (Buttons.BACK_TO_MAIN, CallbackData.BACK_TO_MAIN_MENU),
            ],
        ]
        
        # Format message
        message = Messages.Records.OPERATION_MENU.format(
            title=self.title,
            operation=self.operation_name,
            operation_desc=self.operation_desc
        )
        
        keyboard = create_inline_keyboard(keyboard_buttons)
        await send_response(update, message, reply_markup=keyboard)


class AddRecordsHandler(BaseRecordsHandler):
    """Handler for adding DNS records."""
    
    @property
    def operation_name(self) -> str:
        return "menambah"
    
    @property
    def operation_desc(self) -> str:
        return "Tambah"
    
    @property
    def title(self) -> str:
        return Messages.Records.ADD_TITLE
    
    @property
    def single_callback_data(self) -> str:
        return CallbackData.ADD_SINGLE_RECORD
    
    @property
    def file_callback_data(self) -> str:
        return CallbackData.ADD_RECORD_FROM_FILE


class EditRecordsHandler(BaseRecordsHandler):
    """Handler for editing DNS records."""
    
    @property
    def operation_name(self) -> str:
        return "mengedit"
    
    @property
    def operation_desc(self) -> str:
        return "Edit"
    
    @property
    def title(self) -> str:
        return Messages.Records.EDIT_TITLE
    
    @property
    def single_callback_data(self) -> str:
        return CallbackData.EDIT_SINGLE_RECORD
    
    @property
    def file_callback_data(self) -> str:
        return CallbackData.EDIT_RECORD_FROM_FILE


class RemoveRecordsHandler(BaseRecordsHandler):
    """Handler for removing DNS records."""
    
    @property
    def operation_name(self) -> str:
        return "menghapus"
    
    @property
    def operation_desc(self) -> str:
        return "Hapus"
    
    @property
    def title(self) -> str:
        return Messages.Records.DELETE_TITLE
    
    @property
    def single_callback_data(self) -> str:
        return CallbackData.REMOVE_SINGLE_RECORD
    
    @property
    def file_callback_data(self) -> str:
        return CallbackData.REMOVE_RECORD_FROM_FILE