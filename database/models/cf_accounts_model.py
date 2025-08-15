import logging
from typing import Optional, Dict, Any, List
from database.db import db_manager

logger = logging.getLogger(__name__)


async def save_cloudflare_account(account_data: Dict[str, Any]) -> bool:
    """Save Cloudflare account configuration with improved error handling."""
    try:
        # Use INSERT OR REPLACE for better handling
        query = """
        INSERT OR REPLACE INTO cf_accounts 
        (user_id, email, api_key, account_id, zone_id, zone_name, 
         created_at, updated_at)
        VALUES (?, ?, ?, ?, ?, ?, 
                COALESCE((SELECT created_at FROM cf_accounts WHERE user_id = ?), CURRENT_TIMESTAMP),
                CURRENT_TIMESTAMP)
        """
        
        params = (
            account_data["user_id"],
            account_data["email"],
            account_data["api_key"],
            account_data["account_id"],
            account_data["zone_id"],
            account_data["zone_name"],
            account_data["user_id"]  # For the COALESCE subquery
        )

        await db_manager.execute_query(query, params)

        logger.info(
            f"Cloudflare account for user {account_data['user_id']} saved successfully"
        )
        return True

    except Exception as e:
        logger.error(
            f"Failed to save Cloudflare account for user {account_data.get('user_id')}: {e}"
        )
        return False


async def get_cloudflare_account(user_id: int) -> Optional[Dict[str, Any]]:
    """Get Cloudflare account data for a specific user."""
    try:
        query = """
        SELECT user_id, email, api_key, zone_id, zone_name, account_id, created_at, updated_at
        FROM cf_accounts
        WHERE user_id = ?
        LIMIT 1
        """

        result = await db_manager.execute_query(query, (user_id,), fetch_one=True)

        if result:
            return dict(result)
        return None

    except Exception as e:
        logger.error(f"Failed to get Cloudflare account for user {user_id}: {e}")
        return None


async def delete_cloudflare_account(user_id: int) -> bool:
    """Delete Cloudflare account for a user."""
    try:
        query = "DELETE FROM cf_accounts WHERE user_id = ?"
        
        async with db_manager.get_async_connection() as conn:
            loop = db_manager.loop if hasattr(db_manager, 'loop') else None
            if not loop:
                import asyncio
                loop = asyncio.get_event_loop()
                
            cursor = await loop.run_in_executor(None, conn.execute, query, (user_id,))
            await loop.run_in_executor(None, conn.commit)
            
            if cursor.rowcount > 0:
                logger.info(
                    f"Cloudflare account for user {user_id} deleted successfully"
                )
                return True
            else:
                logger.warning(f"No Cloudflare account found for user {user_id}")
                return False

    except Exception as e:
        logger.error(f"Failed to delete Cloudflare account for user {user_id}: {e}")
        return False


async def account_exists(user_id: int) -> bool:
    """Check if user has a Cloudflare account."""
    try:
        query = "SELECT 1 FROM cf_accounts WHERE user_id = ? LIMIT 1"
        result = await db_manager.execute_query(query, (user_id,), fetch_one=True)
        return result is not None

    except Exception as e:
        logger.error(f"Failed to check account existence for user {user_id}: {e}")
        return False


async def get_all_accounts() -> List[Dict[str, Any]]:
    """Get all Cloudflare accounts (for admin purposes)."""
    try:
        query = """
        SELECT cf.*, u.username, u.first_name, u.last_name
        FROM cf_accounts cf
        INNER JOIN users u ON cf.user_id = u.chat_id
        ORDER BY cf.created_at DESC
        """
        
        result = await db_manager.execute_query(query, fetch_all=True)
        
        if result:
            return [dict(row) for row in result]
        return []

    except Exception as e:
        logger.error(f"Failed to get all accounts: {e}")
        return []


async def get_accounts_stats() -> Dict[str, Any]:
    """Get Cloudflare accounts statistics."""
    try:
        total_query = "SELECT COUNT(*) as count FROM cf_accounts"
        zones_query = "SELECT COUNT(DISTINCT zone_id) as count FROM cf_accounts"
        recent_query = """
        SELECT COUNT(*) as count FROM cf_accounts 
        WHERE created_at >= datetime('now', '-7 days')
        """
        
        total_result = await db_manager.execute_query(total_query, fetch_one=True)
        zones_result = await db_manager.execute_query(zones_query, fetch_one=True)
        recent_result = await db_manager.execute_query(recent_query, fetch_one=True)
        
        return {
            "total_accounts": total_result["count"] if total_result else 0,
            "unique_zones": zones_result["count"] if zones_result else 0,
            "recent_accounts": recent_result["count"] if recent_result else 0
        }
        
    except Exception as e:
        logger.error(f"Failed to get accounts stats: {e}")
        return {"total_accounts": 0, "unique_zones": 0, "recent_accounts": 0}
