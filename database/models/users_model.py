import logging
from typing import Optional, Dict, Any
from database.db import db_manager

logger = logging.getLogger(__name__)


async def save_user(user_data: Dict[str, Any]) -> bool:
    """Save or update user data with improved error handling."""
    try:
        query = """
        INSERT INTO users (chat_id, username, first_name, last_name)
        VALUES (?, ?, ?, ?)
        ON CONFLICT(chat_id) DO UPDATE SET
            username=excluded.username,
            first_name=excluded.first_name,
            last_name=excluded.last_name,
            updated_at=CURRENT_TIMESTAMP
        """

        await db_manager.execute_query(
            query,
            (
                user_data.get("chat_id"),
                user_data.get("username"),
                user_data.get("first_name"),
                user_data.get("last_name"),
            ),
        )

        logger.info(f"User {user_data.get('chat_id')} saved successfully")
        return True

    except Exception as e:
        logger.error(f"Failed to save user {user_data.get('chat_id')}: {e}")
        return False


async def get_user(user_id: int) -> Optional[Dict[str, Any]]:
    """Get user data by ID."""
    try:
        query = """
        SELECT chat_id, username, first_name, last_name, created_at, updated_at
        FROM users 
        WHERE chat_id = ?
        """

        result = await db_manager.execute_query(query, (user_id,), fetch_one=True)

        if result:
            return dict(result)
        return None

    except Exception as e:
        logger.error(f"Failed to get user {user_id}: {e}")
        return None


async def user_exists(user_id: int) -> bool:
    """Check if user is registered in database."""
    try:
        query = "SELECT 1 FROM users WHERE chat_id = ? LIMIT 1"
        result = await db_manager.execute_query(query, (user_id,), fetch_one=True)
        return result is not None

    except Exception as e:
        logger.error(f"Failed to check user existence {user_id}: {e}")
        return False


async def user_has_account(user_id: int) -> bool:
    """Check if user has a Cloudflare account stored."""
    try:
        query = "SELECT 1 FROM cf_accounts WHERE user_id = ? LIMIT 1"
        result = await db_manager.execute_query(query, (user_id,), fetch_one=True)
        return result is not None

    except Exception as e:
        logger.error(f"Failed to check user account {user_id}: {e}")
        return False


async def get_user_stats() -> Dict[str, int]:
    """Get user statistics."""
    try:
        total_users_query = "SELECT COUNT(*) as count FROM users"
        users_with_accounts_query = """
        SELECT COUNT(DISTINCT u.chat_id) as count 
        FROM users u 
        INNER JOIN cf_accounts cf ON u.chat_id = cf.user_id
        """

        total_result = await db_manager.execute_query(total_users_query, fetch_one=True)
        accounts_result = await db_manager.execute_query(
            users_with_accounts_query, fetch_one=True
        )

        return {
            "total_users": total_result["count"] if total_result else 0,
            "users_with_accounts": accounts_result["count"] if accounts_result else 0,
        }

    except Exception as e:
        logger.error(f"Failed to get user stats: {e}")
        return {"total_users": 0, "users_with_accounts": 0}
