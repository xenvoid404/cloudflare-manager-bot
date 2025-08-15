"""
Helper utility functions for common operations.
"""

import re
import logging
from datetime import datetime
from typing import Optional, Dict, Any, Union
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from telegram.constants import ParseMode

from constants import Config, Patterns, Messages

logger = logging.getLogger(__name__)


def mask_api_key(api_key: str, visible_chars: int = Config.API_KEY_VISIBLE_CHARS) -> str:
    """
    Mask API key for security, showing only first and last characters.
    
    Args:
        api_key: The API key to mask
        visible_chars: Number of characters to show at start and end
        
    Returns:
        Masked API key string
    """
    if not api_key or len(api_key) <= visible_chars * 2:
        return "`Tidak tersedia`"
    
    return f"`{api_key[:visible_chars]}...{api_key[-visible_chars:]}`"


def validate_email(email: str) -> bool:
    """
    Basic email validation.
    
    Args:
        email: Email address to validate
        
    Returns:
        True if email format is valid
    """
    if not email:
        return False
    return re.match(Patterns.EMAIL_BASIC, email) is not None


def validate_api_key(api_key: str) -> bool:
    """
    Validate Cloudflare API key format.
    
    Args:
        api_key: API key to validate
        
    Returns:
        True if API key format is valid
    """
    if not api_key:
        return False
    return len(api_key.strip()) >= Config.MIN_API_KEY_LENGTH


def validate_account_id(account_id: str) -> bool:
    """
    Validate Cloudflare Account ID format.
    
    Args:
        account_id: Account ID to validate
        
    Returns:
        True if Account ID format is valid
    """
    if not account_id:
        return False
    return len(account_id.strip()) >= Config.MIN_ACCOUNT_ID_LENGTH


def format_timestamp(timestamp: Optional[datetime] = None, 
                    format_str: str = Config.DISPLAY_TIMESTAMP_FORMAT) -> str:
    """
    Format timestamp for display.
    
    Args:
        timestamp: Datetime to format (defaults to now)
        format_str: Format string to use
        
    Returns:
        Formatted timestamp string
    """
    if timestamp is None:
        timestamp = datetime.now()
    return timestamp.strftime(format_str)


def get_export_filename(zone_name: str, timestamp: Optional[datetime] = None) -> str:
    """
    Generate export filename for DNS records.
    
    Args:
        zone_name: Zone name for the file
        timestamp: Timestamp for the file (defaults to now)
        
    Returns:
        Generated filename
    """
    if timestamp is None:
        timestamp = datetime.now()
    
    # Clean zone name for filename
    clean_zone_name = re.sub(r'[^\w\-_.]', '_', zone_name)
    timestamp_str = timestamp.strftime(Config.EXPORT_TIMESTAMP_FORMAT)
    
    return Config.EXPORT_FILENAME_FORMAT.format(
        zone_name=clean_zone_name,
        timestamp=timestamp_str
    )


async def send_response(update: Update, message: str, 
                       parse_mode: ParseMode = ParseMode.MARKDOWN_V2,
                       reply_markup: Optional[InlineKeyboardMarkup] = None) -> None:
    """
    Send response handling both callback queries and regular messages.
    
    Args:
        update: Telegram update object
        message: Message to send
        parse_mode: Parse mode for the message
        reply_markup: Optional inline keyboard
    """
    try:
        if hasattr(update, 'callback_query') and update.callback_query:
            if reply_markup:
                await update.callback_query.edit_message_text(
                    message, parse_mode=parse_mode, reply_markup=reply_markup
                )
            else:
                await update.callback_query.edit_message_text(
                    message, parse_mode=parse_mode
                )
        else:
            await update.message.reply_text(
                message, parse_mode=parse_mode, reply_markup=reply_markup
            )
    except Exception as e:
        logger.error(f"Failed to send response: {e}")
        # Fallback: try to send to chat
        try:
            await update.effective_chat.send_message(message)
        except Exception as fallback_error:
            logger.error(f"Fallback send also failed: {fallback_error}")


def create_inline_keyboard(buttons: list) -> InlineKeyboardMarkup:
    """
    Create inline keyboard from button configuration.
    
    Args:
        buttons: List of button rows, where each row is a list of tuples (text, callback_data)
        
    Returns:
        InlineKeyboardMarkup object
    """
    keyboard = []
    for row in buttons:
        keyboard_row = []
        for button_text, callback_data in row:
            keyboard_row.append(InlineKeyboardButton(button_text, callback_data=callback_data))
        keyboard.append(keyboard_row)
    
    return InlineKeyboardMarkup(keyboard)


def escape_markdown_v2(text: str) -> str:
    """
    Escape special characters for MarkdownV2.
    
    Args:
        text: Text to escape
        
    Returns:
        Escaped text
    """
    # Characters that need to be escaped in MarkdownV2
    special_chars = ['_', '*', '[', ']', '(', ')', '~', '`', '>', '#', '+', '-', '=', '|', '{', '}', '.', '!']
    
    escaped_text = text
    for char in special_chars:
        escaped_text = escaped_text.replace(char, f'\\{char}')
    
    return escaped_text


def safe_format_message(template: str, **kwargs) -> str:
    """
    Safely format message template with MarkdownV2 escaping.
    
    Args:
        template: Message template with placeholders
        **kwargs: Values to substitute
        
    Returns:
        Formatted and escaped message
    """
    # Escape all string values
    escaped_kwargs = {}
    for key, value in kwargs.items():
        if isinstance(value, str):
            escaped_kwargs[key] = escape_markdown_v2(value)
        else:
            escaped_kwargs[key] = value
    
    try:
        return template.format(**escaped_kwargs)
    except KeyError as e:
        logger.error(f"Missing template variable: {e}")
        return Messages.Common.ERROR_GENERIC


def get_user_display_name(user) -> str:
    """
    Get display name for user (first_name or username).
    
    Args:
        user: Telegram user object
        
    Returns:
        Display name for the user
    """
    return user.first_name or user.username or "User"


def chunk_list(lst: list, chunk_size: int) -> list:
    """
    Split list into chunks of specified size.
    
    Args:
        lst: List to chunk
        chunk_size: Size of each chunk
        
    Returns:
        List of chunked lists
    """
    return [lst[i:i + chunk_size] for i in range(0, len(lst), chunk_size)]


class ResponseBuilder:
    """
    Builder pattern for creating structured responses.
    """
    
    def __init__(self):
        self.message_parts = []
        self.keyboard_rows = []
    
    def add_header(self, header: str) -> 'ResponseBuilder':
        """Add header to message."""
        self.message_parts.append(f"*{escape_markdown_v2(header)}*")
        return self
    
    def add_line(self, line: str) -> 'ResponseBuilder':
        """Add line to message."""
        self.message_parts.append(escape_markdown_v2(line))
        return self
    
    def add_separator(self) -> 'ResponseBuilder':
        """Add separator line."""
        self.message_parts.append("━━━━━━━━━━━━━━━━━━━━━━━━")
        return self
    
    def add_field(self, label: str, value: str, emoji: str = "") -> 'ResponseBuilder':
        """Add field with label and value."""
        escaped_label = escape_markdown_v2(label)
        escaped_value = escape_markdown_v2(value)
        self.message_parts.append(f"{emoji} *{escaped_label}:* `{escaped_value}`")
        return self
    
    def add_button_row(self, buttons: list) -> 'ResponseBuilder':
        """Add button row to keyboard."""
        self.keyboard_rows.append(buttons)
        return self
    
    def build_message(self) -> str:
        """Build the message text."""
        return "\n".join(self.message_parts)
    
    def build_keyboard(self) -> Optional[InlineKeyboardMarkup]:
        """Build the inline keyboard."""
        if not self.keyboard_rows:
            return None
        return create_inline_keyboard(self.keyboard_rows)
    
    def build(self) -> tuple[str, Optional[InlineKeyboardMarkup]]:
        """Build both message and keyboard."""
        return self.build_message(), self.build_keyboard()