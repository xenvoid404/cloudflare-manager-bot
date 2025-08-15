"""
Decorators untuk operasi middleware seperti autentikasi dan penanganan error.
"""

import logging
import functools
from typing import Callable, Any
from telegram import Update
from telegram.ext import ContextTypes
from telegram.constants import ParseMode

from database.models.users_model import user_exists
from database.models.cf_accounts_model import get_cloudflare_account
from constants import Messages

logger = logging.getLogger(__name__)


def require_user_registration(func: Callable) -> Callable:
    """
    Decorator untuk memastikan user sudah terdaftar sebelum menjalankan handler.
    """

    @functools.wraps(func)
    async def wrapper(
        update: Update, context: ContextTypes.DEFAULT_TYPE, *args, **kwargs
    ) -> Any:
        user = update.effective_user

        if not await user_exists(user.id):
            # Tentukan metode response
            if hasattr(update, "callback_query") and update.callback_query:
                await update.callback_query.edit_message_text(
                    Messages.Common.UNAUTHORIZED, parse_mode=ParseMode.MARKDOWN_V2
                )
            else:
                await update.message.reply_text(
                    Messages.Common.UNAUTHORIZED, parse_mode=ParseMode.MARKDOWN_V2
                )
            return

        return await func(update, context, *args, **kwargs)

    return wrapper


def require_cloudflare_account(func: Callable) -> Callable:
    """
    Decorator untuk memastikan user memiliki akun Cloudflare sebelum menjalankan handler.
    """

    @functools.wraps(func)
    async def wrapper(
        update: Update, context: ContextTypes.DEFAULT_TYPE, *args, **kwargs
    ) -> Any:
        user = update.effective_user

        # Cek apakah user memiliki akun Cloudflare
        account = await get_cloudflare_account(user.id)
        if not account:
            # Tentukan metode response
            if hasattr(update, "callback_query") and update.callback_query:
                await update.callback_query.edit_message_text(
                    Messages.Common.NO_ACCOUNT, parse_mode=ParseMode.MARKDOWN_V2
                )
            else:
                await update.message.reply_text(
                    Messages.Common.NO_ACCOUNT, parse_mode=ParseMode.MARKDOWN_V2
                )
            return

        # Tambahkan akun ke context untuk akses mudah
        context.user_data["cf_account"] = account
        return await func(update, context, *args, **kwargs)

    return wrapper


def handle_errors(func: Callable) -> Callable:
    """
    Decorator untuk penanganan error yang konsisten di semua handler.
    """

    @functools.wraps(func)
    async def wrapper(
        update: Update, context: ContextTypes.DEFAULT_TYPE, *args, **kwargs
    ) -> Any:
        try:
            return await func(update, context, *args, **kwargs)
        except Exception as e:
            user_id = update.effective_user.id if update.effective_user else "Unknown"
            logger.error(f"Error dalam {func.__name__} untuk user {user_id}: {e}")

            # Tentukan metode response
            try:
                if hasattr(update, "callback_query") and update.callback_query:
                    await update.callback_query.edit_message_text(
                        Messages.Common.ERROR_GENERIC, parse_mode=ParseMode.MARKDOWN_V2
                    )
                else:
                    await update.message.reply_text(
                        Messages.Common.ERROR_GENERIC, parse_mode=ParseMode.MARKDOWN_V2
                    )
            except Exception as send_error:
                logger.error(f"Gagal mengirim pesan error: {send_error}")
                # Fallback: coba kirim ke chat
                try:
                    await update.effective_chat.send_message(
                        Messages.Common.ERROR_GENERIC
                    )
                except:
                    pass  # Give up gracefully

    return wrapper


def log_user_action(action_name: str = None):
    """
    Decorator untuk log aksi user.
    """

    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        async def wrapper(
            update: Update, context: ContextTypes.DEFAULT_TYPE, *args, **kwargs
        ) -> Any:
            user = update.effective_user
            action = action_name or func.__name__

            logger.info(
                f"User {user.id} ({user.username or user.first_name}) menjalankan: {action}"
            )

            result = await func(update, context, *args, **kwargs)

            logger.debug(f"Aksi {action} selesai untuk user {user.id}")
            return result

        return wrapper

    return decorator


def combine_decorators(*decorators):
    """
    Utility untuk menggabungkan multiple decorators dengan cara yang clean.
    """

    def decorator(func):
        for d in reversed(decorators):
            func = d(func)
        return func

    return decorator


# Kombinasi decorator yang umum
def authenticated_handler(func: Callable) -> Callable:
    """
    Menggabungkan pengecekan registrasi user dengan penanganan error dan logging.
    """
    return combine_decorators(
        handle_errors, require_user_registration, log_user_action()
    )(func)


def cloudflare_handler(func: Callable) -> Callable:
    """
    Menggabungkan registrasi user, pengecekan akun Cloudflare, penanganan error, dan logging.
    """
    return combine_decorators(
        handle_errors,
        require_user_registration,
        require_cloudflare_account,
        log_user_action(),
    )(func)
