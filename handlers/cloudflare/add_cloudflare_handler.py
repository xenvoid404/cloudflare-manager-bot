import logging
import asyncio
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
from database.models.users_model import user_exists

logger = logging.getLogger(__name__)

# Conversation states
EMAIL, API_KEY, ACCOUNT_ID, ZONE_SELECTION = range(4)


class AddCloudflareHandler:
    """Handler for managing Cloudflare account addition process."""

    def __init__(self):
        self.user_data: Dict[int, Dict[str, Any]] = {}

    async def start_add_account(
        self, update: Update, context: ContextTypes.DEFAULT_TYPE
    ) -> int:
        """Start the Cloudflare account addition process."""
        try:
            user = update.effective_user

            # Check if user is registered
            if not await user_exists(user.id):
                await update.callback_query.edit_message_text(
                    "⚠️ Silakan jalankan /start terlebih dahulu untuk menggunakan bot ini."
                )
                return ConversationHandler.END

            # Initialize user data
            self.user_data[user.id] = {}

            await update.callback_query.edit_message_text(
                text="*➕ Tambah Akun Cloudflare*\n\n"
                "Saya akan memandu Anda untuk menambahkan akun Cloudflare\\.\n\n"
                "📧 *Langkah 1/3*\n"
                "Silakan masukkan email Cloudflare Anda:",
                parse_mode=ParseMode.MARKDOWN_V2,
            )

            logger.info(f"User {user.id} started Cloudflare account addition")
            return EMAIL
        except Exception as e:
            logger.error(
                f"Error starting add account for user {update.effective_user.id}: {e}"
            )
            await update.callback_query.edit_message_text(
                "⚠️ Terjadi kesalahan. Gunakan /menu untuk mencoba lagi."
            )
            return ConversationHandler.END

    async def handle_email(
        self, update: Update, context: ContextTypes.DEFAULT_TYPE
    ) -> int:
        """Handle email input."""
        try:
            user = update.effective_user
            email = update.message.text.strip()

            # Basic email validation
            if "@" not in email or "." not in email:
                await update.message.reply_text(
                    "⚠️ Format email tidak valid. Silakan masukkan email yang benar:"
                )
                return EMAIL

            # Store email
            self.user_data[user.id]["email"] = email

            await update.message.reply_text(
                text="✅ Email berhasil disimpan\\!\n\n"
                "🔑 *Langkah 2/3*\n"
                "Silakan masukkan Global API Key Cloudflare Anda:\n\n"
                "_API Key dapat ditemukan di:_\n"
                "My Profile → API Tokens → Global API Key → View",
                parse_mode=ParseMode.MARKDOWN_V2,
            )

            return API_KEY

        except Exception as e:
            logger.error(
                f"Error handling email for user {update.effective_user.id}: {e}"
            )
            await update.message.reply_text(
                "⚠️ Terjadi kesalahan. Gunakan /menu untuk memulai ulang."
            )
            return ConversationHandler.END

    async def handle_api_key(
        self, update: Update, context: ContextTypes.DEFAULT_TYPE
    ) -> int:
        """Handle API key input."""
        try:
            user = update.effective_user
            api_key = update.message.text.strip()

            # Basic API key validation (Cloudflare Global API Key length)
            if len(api_key) < 32:
                await update.message.reply_text(
                    "⚠️ API Key tampaknya tidak valid. Silakan periksa kembali dan masukkan API Key yang benar:"
                )
                return API_KEY

            # Store API key
            self.user_data[user.id]["api_key"] = api_key

            await update.message.reply_text(
                text="✅ API Key berhasil disimpan\\!\n\n"
                "🆔 *Langkah 3/3*\n"
                "Silakan masukkan Account ID Cloudflare Anda:\n\n"
                "_Account ID dapat ditemukan di:_\n"
                "Dashboard → Right sidebar → Account ID",
                parse_mode=ParseMode.MARKDOWN_V2,
            )

            return ACCOUNT_ID

        except Exception as e:
            logger.error(
                f"Error handling API key for user {update.effective_user.id}: {e}"
            )
            await update.message.reply_text(
                "⚠️ Terjadi kesalahan. Gunakan /menu untuk memulai ulang."
            )
            return ConversationHandler.END

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
            add_cloudflare_handler.start_add_account, pattern="^add_cloudflare"
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
