"""
Decorators for middleware operations like authentication and error handling.
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
    Decorator to ensure user is registered before executing handler.
    """
    @functools.wraps(func)
    async def wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE, *args, **kwargs) -> Any:
        user = update.effective_user
        
        if not await user_exists(user.id):
            # Determine response method
            if hasattr(update, 'callback_query') and update.callback_query:
                await update.callback_query.edit_message_text(
                    Messages.Common.UNAUTHORIZED,
                    parse_mode=ParseMode.MARKDOWN_V2
                )
            else:
                await update.message.reply_text(
                    Messages.Common.UNAUTHORIZED,
                    parse_mode=ParseMode.MARKDOWN_V2
                )
            return
        
        return await func(update, context, *args, **kwargs)
    
    return wrapper


def require_cloudflare_account(func: Callable) -> Callable:
    """
    Decorator to ensure user has a Cloudflare account before executing handler.
    """
    @functools.wraps(func)
    async def wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE, *args, **kwargs) -> Any:
        user = update.effective_user
        
        # Check if user has Cloudflare account
        account = await get_cloudflare_account(user.id)
        if not account:
            # Determine response method
            if hasattr(update, 'callback_query') and update.callback_query:
                await update.callback_query.edit_message_text(
                    Messages.Common.NO_ACCOUNT,
                    parse_mode=ParseMode.MARKDOWN_V2
                )
            else:
                await update.message.reply_text(
                    Messages.Common.NO_ACCOUNT,
                    parse_mode=ParseMode.MARKDOWN_V2
                )
            return
        
        # Add account to context for easy access
        context.user_data['cf_account'] = account
        return await func(update, context, *args, **kwargs)
    
    return wrapper


def handle_errors(func: Callable) -> Callable:
    """
    Decorator for consistent error handling across handlers.
    """
    @functools.wraps(func)
    async def wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE, *args, **kwargs) -> Any:
        try:
            return await func(update, context, *args, **kwargs)
        except Exception as e:
            user_id = update.effective_user.id if update.effective_user else "Unknown"
            logger.error(f"Error in {func.__name__} for user {user_id}: {e}")
            
            # Determine response method
            try:
                if hasattr(update, 'callback_query') and update.callback_query:
                    await update.callback_query.edit_message_text(
                        Messages.Common.ERROR_GENERIC,
                        parse_mode=ParseMode.MARKDOWN_V2
                    )
                else:
                    await update.message.reply_text(
                        Messages.Common.ERROR_GENERIC,
                        parse_mode=ParseMode.MARKDOWN_V2
                    )
            except Exception as send_error:
                logger.error(f"Failed to send error message: {send_error}")
                # Fallback: try to send to chat
                try:
                    await update.effective_chat.send_message(
                        Messages.Common.ERROR_GENERIC
                    )
                except:
                    pass  # Give up gracefully
    
    return wrapper


def log_user_action(action_name: str = None):
    """
    Decorator to log user actions.
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        async def wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE, *args, **kwargs) -> Any:
            user = update.effective_user
            action = action_name or func.__name__
            
            logger.info(f"User {user.id} ({user.username or user.first_name}) executed: {action}")
            
            result = await func(update, context, *args, **kwargs)
            
            logger.debug(f"Action {action} completed for user {user.id}")
            return result
        
        return wrapper
    return decorator


def combine_decorators(*decorators):
    """
    Utility to combine multiple decorators in a clean way.
    """
    def decorator(func):
        for d in reversed(decorators):
            func = d(func)
        return func
    return decorator


# Common decorator combinations
def authenticated_handler(func: Callable) -> Callable:
    """
    Combines user registration check with error handling and logging.
    """
    return combine_decorators(
        handle_errors,
        require_user_registration,
        log_user_action()
    )(func)


def cloudflare_handler(func: Callable) -> Callable:
    """
    Combines user registration, Cloudflare account check, error handling, and logging.
    """
    return combine_decorators(
        handle_errors,
        require_user_registration,
        require_cloudflare_account,
        log_user_action()
    )(func)