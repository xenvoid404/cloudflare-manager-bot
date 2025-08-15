import logging
import requests
from typing import Dict, Any, Optional
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ContextTypes,
    ConversationHandler,
    MessageHandler,
    filters,
    CallbackQueryHandler,
)
from telegram.constants import ParseMode

from database.models.cf_accounts_model import save_cloudflare_account
from services.cloudflare_service import create_cloudflare_service, CloudflareAPIError
from constants import Messages, Buttons, CallbackData, Config
from utils.decorators import handle_errors, require_user_registration
from utils.helpers import (
    validate_email,
    validate_api_key,
    validate_account_id,
    send_response,
    create_inline_keyboard,
    get_user_display_name,
)

logger = logging.getLogger(__name__)

# Conversation states
EMAIL, API_KEY, ACCOUNT_ID, ZONE_SELECTION = range(4)


class AddCloudflareHandler:
    """Handler for managing Cloudflare account addition process."""

    def __init__(self):
        self.user_data: Dict[int, Dict[str, Any]] = {}

    @require_user_registration
    @handle_errors
    async def start_add_account(
        self, update: Update, context: ContextTypes.DEFAULT_TYPE
    ) -> int:
        """Start the Cloudflare account addition process."""
        user = update.effective_user

        # Initialize user data
        self.user_data[user.id] = {}

        await send_response(update, Messages.CloudflareAccount.ADD_START)

        logger.info(f"User {user.id} started Cloudflare account addition")
        return EMAIL

    @handle_errors
    async def handle_email(
        self, update: Update, context: ContextTypes.DEFAULT_TYPE
    ) -> int:
        """Handle email input."""
        user = update.effective_user
        email = update.message.text.strip()

        # Validate email format
        if not validate_email(email):
            await send_response(update, Messages.Validation.INVALID_EMAIL)
            return EMAIL

        # Store email
        self.user_data[user.id]["email"] = email

        await send_response(update, Messages.CloudflareAccount.EMAIL_SUCCESS)
        return API_KEY

    @handle_errors
    async def handle_api_key(
        self, update: Update, context: ContextTypes.DEFAULT_TYPE
    ) -> int:
        """Handle API key input."""
        user = update.effective_user
        api_key = update.message.text.strip()

        # Validate API key format
        if not validate_api_key(api_key):
            await send_response(update, Messages.Validation.INVALID_API_KEY)
            return API_KEY

        # Store API key
        self.user_data[user.id]["api_key"] = api_key

        await send_response(update, Messages.CloudflareAccount.API_KEY_SUCCESS)
        return ACCOUNT_ID

    async def handle_account_id(
        self, update: Update, context: ContextTypes.DEFAULT_TYPE
    ) -> int:
        """Handle Account ID input and fetch zones."""
        try:
            user = update.effective_user
            account_id = update.message.text.strip()

            # Basic Account ID validation
            if len(account_id) < 32:
                await update.message.reply_text(
                    "⚠️ Account ID tampaknya tidak valid. Silakan periksa kembali dan masukkan Account ID yang benar:"
                )
                return ACCOUNT_ID

            # Store Account ID
            self.user_data[user.id]["account_id"] = account_id

            # Show loading message
            loading_msg = await update.message.reply_text(
                "🔄 Memverifikasi kredensial dan mengambil daftar zone...\n"
                "Mohon tunggu sebentar..."
            )

            # Fetch zones from Cloudflare
            zones = await self._fetch_zones(user.id)

            if not zones:
                await loading_msg.edit_text(
                    "❌ Gagal mengambil daftar zone\\. Kemungkinan penyebab:\n"
                    "• Email, API Key, atau Account ID tidak valid\n"
                    "• Tidak ada zone di akun Cloudflare\n"
                    "• Masalah koneksi internet\n\n"
                    "Gunakan /menu untuk mencoba lagi\\.",
                    parse_mode=ParseMode.MARKDOWN_V2,
                )
                self._cleanup_user_data(user.id)
                return ConversationHandler.END

            # Create inline keyboard for zone selection
            keyboard = []
            for zone in zones:
                keyboard.append(
                    [
                        InlineKeyboardButton(
                            f"🌐 {zone['name']}",
                            callback_data=f"select_zone_{zone['id']}",
                        )
                    ]
                )

            keyboard.append(
                [InlineKeyboardButton("❌ Batal", callback_data="cancel_add_account")]
            )

            await loading_msg.edit_text(
                text=f"✅ Berhasil terhubung ke Cloudflare\\!\n\n"
                f"📋 *Ditemukan {len(zones)} zone:*\n"
                "Silakan pilih zone yang ingin dikelola:",
                parse_mode=ParseMode.MARKDOWN_V2,
                reply_markup=InlineKeyboardMarkup(keyboard),
            )

            return ZONE_SELECTION

        except Exception as e:
            logger.error(
                f"Error handling account ID for user {update.effective_user.id}: {e}"
            )
            await update.message.reply_text(
                "⚠️ Terjadi kesalahan. Gunakan /menu untuk memulai ulang."
            )
            self._cleanup_user_data(user.id)
            return ConversationHandler.END

    async def handle_zone_selection(
        self, update: Update, context: ContextTypes.DEFAULT_TYPE
    ) -> int:
        """Handle zone selection and save account data."""
        try:
            query = update.callback_query
            await query.answer()

            user = query.from_user
            callback_data = query.data

            if callback_data == "cancel_add_account":
                await query.edit_message_text(
                    "❌ Penambahan akun Cloudflare dibatalkan\\.\n\n"
                    "Gunakan /menu untuk kembali ke menu utama\\.",
                    parse_mode=ParseMode.MARKDOWN_V2,
                )
                self._cleanup_user_data(user.id)
                return ConversationHandler.END

            if not callback_data.startswith("select_zone_"):
                await query.edit_message_text(
                    "⚠️ Pilihan tidak valid\\. Gunakan /menu untuk mencoba lagi\\.",
                    parse_mode=ParseMode.MARKDOWN_V2,
                )
                self._cleanup_user_data(user.id)
                return ConversationHandler.END

            zone_id = callback_data.replace("select_zone_", "")

            # Get zone name from the stored zones
            user_data = self.user_data.get(user.id, {})
            zones = user_data.get("zones", [])
            selected_zone = next((z for z in zones if z["id"] == zone_id), None)

            if not selected_zone:
                await query.edit_message_text(
                    "⚠️ Zone tidak ditemukan\\. Gunakan /menu untuk mencoba lagi\\.",
                    parse_mode=ParseMode.MARKDOWN_V2,
                )
                self._cleanup_user_data(user.id)
                return ConversationHandler.END

            # Prepare account data for database
            account_data = {
                "user_id": user.id,
                "email": user_data["email"],
                "api_key": user_data["api_key"],
                "account_id": user_data["account_id"],
                "zone_id": zone_id,
                "zone_name": selected_zone["name"],
            }

            # Save to database
            success = await save_cloudflare_account(account_data)

            if success:
                await query.edit_message_text(
                    text=f"✅ *Akun Cloudflare berhasil ditambahkan\\!*\n\n"
                    f"📧 *Email:* `{user_data['email']}`\n"
                    f"🌐 *Zone:* `{selected_zone['name']}`\n\n"
                    "Sekarang Anda dapat mengelola DNS record\\.\n"
                    "Gunakan /menu untuk mengakses fitur\\-fitur yang tersedia\\.",
                    parse_mode=ParseMode.MARKDOWN_V2,
                )
                logger.info(f"Cloudflare account successfully added for user {user.id}")
            else:
                await query.edit_message_text(
                    "❌ Gagal menyimpan akun ke database\\. Silakan coba lagi\\.\n\n"
                    "Gunakan /menu untuk mencoba lagi\\.",
                    parse_mode=ParseMode.MARKDOWN_V2,
                )

            self._cleanup_user_data(user.id)
            return ConversationHandler.END

        except Exception as e:
            logger.error(
                f"Error handling zone selection for user {update.effective_user.id}: {e}"
            )
            await update.callback_query.edit_message_text(
                "⚠️ Terjadi kesalahan. Gunakan /menu untuk mencoba lagi."
            )
            self._cleanup_user_data(update.effective_user.id)
            return ConversationHandler.END

    async def cancel(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """Cancel the conversation."""
        user = update.effective_user
        await update.message.reply_text(
            "❌ Penambahan akun Cloudflare dibatalkan\\.\n\n"
            "Gunakan /menu untuk kembali ke menu utama\\.",
            parse_mode=ParseMode.MARKDOWN_V2,
        )
        self._cleanup_user_data(user.id)
        return ConversationHandler.END

    async def _fetch_zones(self, user_id: int) -> Optional[list]:
        """Fetch zones from Cloudflare API."""
        try:
            user_data = self.user_data.get(user_id, {})
            email = user_data.get("email")
            api_key = user_data.get("api_key")

            if not email or not api_key:
                logger.error("Missing Email or API Key")
                return None

            # Fetch zones
            response = requests.get(
                "https://api.cloudflare.com/client/v4/zones",
                headers={
                    "X-Auth-Email": email,
                    "X-Auth-Key": api_key,
                    "Content-Type": "application/json",
                },
                timeout=10,
            )

            # Result
            data = response.json()
            zones_result = data.get("result", [])

            # Format zones data
            zones = []
            for zone in zones_result:
                zones.append(
                    {"id": zone["id"], "name": zone["name"], "status": zone["status"]}
                )

            # Store zones in user data for later use
            self.user_data[user_id]["zones"] = zones

            logger.info(f"Successfully fetched {len(zones)} zones for user {user_id}")
            return zones

        except Exception as e:
            logger.error(f"Error fetching zones for user {user_id}: {e}")
            return None

    def _cleanup_user_data(self, user_id: int) -> None:
        """Clean up user data after conversation ends."""
        if user_id in self.user_data:
            del self.user_data[user_id]


# Create handler instance
add_cloudflare_handler = AddCloudflareHandler()

# Create conversation handler
add_cloudflare_conversation = ConversationHandler(
    entry_points=[
        CallbackQueryHandler(
            add_cloudflare_handler.start_add_account, pattern="^add_cloudflare$"
        )
    ],
    states={
        EMAIL: [
            MessageHandler(
                filters.TEXT & ~filters.COMMAND, add_cloudflare_handler.handle_email
            )
        ],
        API_KEY: [
            MessageHandler(
                filters.TEXT & ~filters.COMMAND, add_cloudflare_handler.handle_api_key
            )
        ],
        ACCOUNT_ID: [
            MessageHandler(
                filters.TEXT & ~filters.COMMAND,
                add_cloudflare_handler.handle_account_id,
            )
        ],
        ZONE_SELECTION: [
            CallbackQueryHandler(add_cloudflare_handler.handle_zone_selection)
        ],
    },
    fallbacks=[MessageHandler(filters.COMMAND, add_cloudflare_handler.cancel)],
    conversation_timeout=300,  # 5 minutes timeout
)
