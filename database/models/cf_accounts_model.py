import logging
from typing import Optional, Dict, Any
from database.db import get_db_connection

logger = logging.getLogger(__name__)

async def save_cloudflare_account(account_data: Dict[str, Any]) -> bool:
    """Save Cloudflare account configuration with improved error handling."""
    try:
        # Check if account already exists for this user
        existing = await get_cloudflare_account(account_data["user_id"])
        
        if existing:
            # Update existing account
            query = """
            UPDATE cf_accounts 
            SET email=?, api_key=?, account_id=?, zone_id=?, zone_name=?, updated_at=CURRENT_TIMESTAMP
            WHERE user_id=?
            """
            params = (
                account_data["email"],
                account_data["api_key"],
                account_data["account_id"],
                account_data["zone_id"],
                account_data["zone_name"],
                account_data["user_id"]
            )
        else:
            # Insert new account
            query = """
            INSERT INTO cf_accounts (user_id, email, api_key, account_id, zone_id, zone_name)
            VALUES (?, ?, ?, ?, ?, ?)
            """
            params = (
                account_data["user_id"],
                account_data["email"],
                account_data["api_key"],
                account_data["account_id"],
                account_data["zone_id"],
                account_data["zone_name"],
            )
        
        with get_db_connection() as conn:
            conn.execute(query, params)
            conn.commit()
            
        logger.info(f"Cloudflare account for user {account_data['user_id']} saved successfully")
        return True
        
    except Exception as e:
        logger.error(f"Failed to save Cloudflare account for user {account_data.get('user_id')}: {e}")
        return False

async def get_cloudflare_account(chat_id: int) -> Optional[Dict[str, Any]]:
    """Get Cloudflare account data for a specific user."""
    try:
        query = """
        SELECT user_id, email, api_key, zone_id, zone_name, account_id, created_at, updated_at
        FROM cf_accounts
        WHERE user_id = ?
        LIMIT 1
        """
        
        with get_db_connection() as conn:
            result = conn.execute(query, (chat_id,)).fetchone()
        
        if result:
            return dict(result)
        return None
        
    except Exception as e:
        logger.error(f"Failed to get Cloudflare account for user {chat_id}: {e}")
        return None

async def delete_cloudflare_account(user_id: int) -> bool:
    """Delete Cloudflare account for a user."""
    try:
        with get_db_connection() as conn:
            cursor = conn.execute("DELETE FROM cf_accounts WHERE user_id = ?", (user_id,))
            conn.commit()
            
            if cursor.rowcount > 0:
                logger.info(f"Cloudflare account for user {user_id} deleted successfully")
                return True
            else:
                logger.warning(f"No Cloudflare account found for user {user_id}")
                return False
                
    except Exception as e:
        logger.error(f"Failed to delete Cloudflare account for user {user_id}: {e}")
        return False

async def get_all_accounts() -> list:
    """Get all Cloudflare accounts (admin function)."""
    try:
        query = """
        SELECT ca.user_id, ca.email, ca.zone_name, ca.created_at,
               u.username, u.first_name
        FROM cf_accounts ca
        LEFT JOIN users u ON ca.user_id = u.chat_id
        ORDER BY ca.created_at DESC
        """
        
        with get_db_connection() as conn:
            results = conn.execute(query).fetchall()
            
        return [dict(row) for row in results]
        
    except Exception as e:
        logger.error(f"Failed to get all accounts: {e}")
        return []

async def account_exists(user_id: int) -> bool:
    """Check if user has a Cloudflare account."""
    try:
        with get_db_connection() as conn:
            cursor = conn.execute(
                "SELECT 1 FROM cf_accounts WHERE user_id = ? LIMIT 1", (user_id,)
            )
            return cursor.fetchone() is not None
            
    except Exception as e:
        logger.error(f"Failed to check account existence for user {user_id}: {e}")
        return False
