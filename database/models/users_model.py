import logging
from typing import Optional, Dict, Any
from database.db import get_db_connection

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
        
        with get_db_connection() as conn:
            conn.execute(
                query,
                (
                    user_data.get("chat_id"),
                    user_data.get("username"),
                    user_data.get("first_name"),
                    user_data.get("last_name"),
                ),
            )
            conn.commit()
            
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
        
        with get_db_connection() as conn:
            result = conn.execute(query, (user_id,)).fetchone()
            
        if result:
            return dict(result)
        return None
        
    except Exception as e:
        logger.error(f"Failed to get user {user_id}: {e}")
        return None

async def user_exists(user_id: int) -> bool:
    """Check if user is registered in database."""
    try:
        with get_db_connection() as conn:
            cursor = conn.execute(
                "SELECT 1 FROM users WHERE chat_id = ? LIMIT 1", (user_id,)
            )
            return cursor.fetchone() is not None
            
    except Exception as e:
        logger.error(f"Failed to check user existence {user_id}: {e}")
        return False

async def user_has_account(user_id: int) -> bool:
    """Check if user has a Cloudflare account stored."""
    try:
        with get_db_connection() as conn:
            cursor = conn.execute(
                "SELECT 1 FROM cf_accounts WHERE user_id = ? LIMIT 1", (user_id,)
            )
            return cursor.fetchone() is not None
            
    except Exception as e:
        logger.error(f"Failed to check user account {user_id}: {e}")
        return False

async def delete_user(user_id: int) -> bool:
    """Delete user and all associated data."""
    try:
        with get_db_connection() as conn:
            # Delete user (CASCADE will handle cf_accounts)
            cursor = conn.execute("DELETE FROM users WHERE chat_id = ?", (user_id,))
            conn.commit()
            
            if cursor.rowcount > 0:
                logger.info(f"User {user_id} deleted successfully")
                return True
            else:
                logger.warning(f"User {user_id} not found for deletion")
                return False
                
    except Exception as e:
        logger.error(f"Failed to delete user {user_id}: {e}")
        return False

async def get_all_users() -> list:
    """Get all registered users (admin function)."""
    try:
        query = """
        SELECT chat_id, username, first_name, last_name, created_at
        FROM users 
        ORDER BY created_at DESC
        """
        
        with get_db_connection() as conn:
            results = conn.execute(query).fetchall()
            
        return [dict(row) for row in results]
        
    except Exception as e:
        logger.error(f"Failed to get all users: {e}")
        return []
