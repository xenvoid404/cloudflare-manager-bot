"""
Helper utility functions untuk operasi umum.
"""

import re
import logging
from datetime import datetime
from typing import Optional, Dict, Any, Union, List
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from telegram.constants import ParseMode

from constants import Config, Patterns, Messages

logger = logging.getLogger(__name__)


def escape_markdown_v2(text: str) -> str:
    """
    Escape karakter khusus untuk MarkdownV2 dengan penanganan yang lebih baik.
    
    Args:
        text: Teks yang akan di-escape
        
    Returns:
        Teks yang sudah di-escape untuk MarkdownV2
    """
    if not text:
        return text
    
    # Karakter yang perlu di-escape dalam MarkdownV2
    # Urutan penting: escape backslash terlebih dahulu
    escape_chars = [
        ('\\', '\\\\'),  # Backslash harus di-escape pertama
        ('_', '\\_'),    # Underscore
        ('*', '\\*'),    # Asterisk
        ('[', '\\['),    # Square bracket
        (']', '\\]'),    # Square bracket
        ('(', '\\('),    # Parenthesis
        (')', '\\)'),    # Parenthesis
        ('~', '\\~'),    # Tilde
        ('`', '\\`'),    # Backtick
        ('>', '\\>'),    # Greater than
        ('#', '\\#'),    # Hash
        ('+', '\\+'),    # Plus
        ('-', '\\-'),    # Minus
        ('=', '\\='),    # Equals
        ('|', '\\|'),    # Pipe
        ('{', '\\{'),    # Curly brace
        ('}', '\\}'),    # Curly brace
        ('.', '\\.'),    # Dot
        ('!', '\\!'),    # Exclamation mark
    ]
    
    escaped_text = text
    for char, escaped_char in escape_chars:
        escaped_text = escaped_text.replace(char, escaped_char)
    
    return escaped_text


def safe_format_message(template: str, **kwargs) -> str:
    """
    Format template pesan dengan escape MarkdownV2 yang aman.
    
    Args:
        template: Template pesan dengan placeholder
        **kwargs: Nilai yang akan disubstitusi
        
    Returns:
        Pesan yang sudah diformat dan di-escape
    """
    if not template:
        return Messages.Common.ERROR_GENERIC
    
    # Escape semua nilai string
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
    except Exception as e:
        logger.error(f"Error formatting message: {e}")
        return Messages.Common.ERROR_GENERIC


def mask_api_key(
    api_key: str, visible_chars: int = Config.API_KEY_VISIBLE_CHARS
) -> str:
    """
    Mask API key untuk keamanan, hanya menampilkan karakter pertama dan terakhir.
    
    Args:
        api_key: API key yang akan di-mask
        visible_chars: Jumlah karakter yang ditampilkan di awal dan akhir
        
    Returns:
        API key yang sudah di-mask
    """
    if not api_key or len(api_key) <= visible_chars * 2:
        return "`Tidak tersedia`"
    
    return f"`{api_key[:visible_chars]}...{api_key[-visible_chars:]}`"


def validate_email(email: str) -> bool:
    """
    Validasi format email dasar.
    
    Args:
        email: Alamat email yang akan divalidasi
        
    Returns:
        True jika format email valid
    """
    if not email:
        return False
    return re.match(Patterns.EMAIL_BASIC, email) is not None


def validate_api_key(api_key: str) -> bool:
    """
    Validasi format Cloudflare API key.
    
    Args:
        api_key: API key yang akan divalidasi
        
    Returns:
        True jika format API key valid
    """
    if not api_key:
        return False
    return len(api_key.strip()) >= Config.MIN_API_KEY_LENGTH


def validate_account_id(account_id: str) -> bool:
    """
    Validasi format Cloudflare Account ID.
    
    Args:
        account_id: Account ID yang akan divalidasi
        
    Returns:
        True jika format Account ID valid
    """
    if not account_id:
        return False
    return len(account_id.strip()) >= Config.MIN_ACCOUNT_ID_LENGTH


def format_timestamp(
    timestamp: Optional[datetime] = None,
    format_str: str = Config.DISPLAY_TIMESTAMP_FORMAT,
) -> str:
    """
    Format timestamp untuk tampilan.
    
    Args:
        timestamp: Datetime yang akan diformat (default: sekarang)
        format_str: Format string yang digunakan
        
    Returns:
        String timestamp yang sudah diformat
    """
    if timestamp is None:
        timestamp = datetime.now()
    return timestamp.strftime(format_str)


def get_export_filename(zone_name: str, timestamp: Optional[datetime] = None) -> str:
    """
    Generate nama file export untuk DNS records.
    
    Args:
        zone_name: Nama zone untuk file
        timestamp: Timestamp untuk file (default: sekarang)
        
    Returns:
        Nama file yang di-generate
    """
    if timestamp is None:
        timestamp = datetime.now()
    
    # Bersihkan nama zone untuk nama file
    clean_zone_name = re.sub(r"[^\w\-_.]", "_", zone_name)
    timestamp_str = timestamp.strftime(Config.EXPORT_TIMESTAMP_FORMAT)
    
    return Config.EXPORT_FILENAME_FORMAT.format(
        zone_name=clean_zone_name, timestamp=timestamp_str
    )


async def send_response(
    update: Update,
    message: str,
    parse_mode: ParseMode = ParseMode.MARKDOWN_V2,
    reply_markup: Optional[InlineKeyboardMarkup] = None,
) -> None:
    """
    Kirim response dengan penanganan callback query dan pesan biasa.
    
    Args:
        update: Objek Telegram update
        message: Pesan yang akan dikirim
        parse_mode: Parse mode untuk pesan
        reply_markup: Optional inline keyboard
    """
    try:
        if hasattr(update, "callback_query") and update.callback_query:
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
        # Fallback: coba kirim ke chat
        try:
            await update.effective_chat.send_message(message)
        except Exception as fallback_error:
            logger.error(f"Fallback send also failed: {fallback_error}")


def create_inline_keyboard(buttons: List[List[tuple]]) -> InlineKeyboardMarkup:
    """
    Buat inline keyboard dari konfigurasi button.
    
    Args:
        buttons: List baris button, dimana setiap baris adalah list dari tuple (text, callback_data)
        
    Returns:
        Objek InlineKeyboardMarkup
    """
    keyboard = []
    for row in buttons:
        keyboard_row = []
        for button_text, callback_data in row:
            keyboard_row.append(
                InlineKeyboardButton(button_text, callback_data=callback_data)
            )
        keyboard.append(keyboard_row)
    
    return InlineKeyboardMarkup(keyboard)


def get_user_display_name(user) -> str:
    """
    Dapatkan nama tampilan untuk user (first_name atau username).
    
    Args:
        user: Objek Telegram user
        
    Returns:
        Nama tampilan untuk user
    """
    return user.first_name or user.username or "User"


def chunk_list(lst: list, chunk_size: int) -> List[List]:
    """
    Bagi list menjadi chunk dengan ukuran tertentu.
    
    Args:
        lst: List yang akan dibagi
        chunk_size: Ukuran setiap chunk
        
    Returns:
        List dari chunked lists
    """
    return [lst[i : i + chunk_size] for i in range(0, len(lst), chunk_size)]


class ResponseBuilder:
    """
    Builder pattern untuk membuat response terstruktur.
    """
    
    def __init__(self):
        self.message_parts = []
        self.keyboard_rows = []
    
    def add_header(self, header: str) -> "ResponseBuilder":
        """Tambah header ke pesan."""
        self.message_parts.append(f"*{escape_markdown_v2(header)}*")
        return self
    
    def add_line(self, line: str) -> "ResponseBuilder":
        """Tambah baris ke pesan."""
        self.message_parts.append(escape_markdown_v2(line))
        return self
    
    def add_separator(self) -> "ResponseBuilder":
        """Tambah garis pemisah."""
        self.message_parts.append("━━━━━━━━━━━━━━━━━━━━━━━━")
        return self
    
    def add_field(self, label: str, value: str, emoji: str = "") -> "ResponseBuilder":
        """Tambah field dengan label dan value."""
        escaped_label = escape_markdown_v2(label)
        escaped_value = escape_markdown_v2(value)
        self.message_parts.append(f"{emoji} *{escaped_label}:* `{escaped_value}`")
        return self
    
    def add_button_row(self, buttons: List[tuple]) -> "ResponseBuilder":
        """Tambah baris button ke keyboard."""
        self.keyboard_rows.append(buttons)
        return self
    
    def build_message(self) -> str:
        """Build teks pesan."""
        return "\n".join(self.message_parts)
    
    def build_keyboard(self) -> Optional[InlineKeyboardMarkup]:
        """Build inline keyboard."""
        if not self.keyboard_rows:
            return None
        return create_inline_keyboard(self.keyboard_rows)
    
    def build(self) -> tuple[str, Optional[InlineKeyboardMarkup]]:
        """Build pesan dan keyboard."""
        return self.build_message(), self.build_keyboard()


def escape_text_for_markdown_v2(text: str) -> str:
    """
    Fungsi khusus untuk escape teks yang akan digunakan dalam MarkdownV2.
    Lebih robust dan menangani edge cases.
    
    Args:
        text: Teks yang akan di-escape
        
    Returns:
        Teks yang sudah di-escape dengan aman
    """
    if not text:
        return ""
    
    # Gunakan fungsi escape yang sudah ada
    return escape_markdown_v2(text)


def format_dns_record_for_display(record: Dict[str, Any]) -> str:
    """
    Format DNS record untuk tampilan yang rapi.
    
    Args:
        record: Dictionary DNS record dari Cloudflare API
        
    Returns:
        String yang sudah diformat untuk tampilan
    """
    try:
        name = escape_markdown_v2(record.get('name', 'N/A'))
        record_type = escape_markdown_v2(record.get('type', 'N/A'))
        content = escape_markdown_v2(record.get('content', 'N/A'))
        ttl = record.get('ttl', 'N/A')
        proxied = "Ya" if record.get('proxied', False) else "Tidak"
        
        return f"*{name}*\n`{record_type}` → `{content}`\nTTL: {ttl} | Proxied: {proxied}"
    except Exception as e:
        logger.error(f"Error formatting DNS record: {e}")
        return "Error formatting record"
