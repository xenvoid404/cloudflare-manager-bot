import sqlite3
import os
import logging
import asyncio
from contextlib import asynccontextmanager
from typing import AsyncGenerator, Optional
from config import DATABASE_FILE

logger = logging.getLogger(__name__)


class DatabaseManager:
    """
    Database manager for handling SQLite connections with proper async support.
    """
    
    def __init__(self, db_file: str = DATABASE_FILE):
        self.db_file = db_file
        self._ensure_directory()
    
    def _ensure_directory(self) -> None:
        """Ensure database directory exists."""
        os.makedirs(os.path.dirname(self.db_file), exist_ok=True)
    
    def get_connection(self) -> sqlite3.Connection:
        """Get database connection with proper row factory."""
        conn = sqlite3.connect(self.db_file, timeout=30.0)
        conn.row_factory = sqlite3.Row
        # Enable foreign key constraints
        conn.execute("PRAGMA foreign_keys = ON")
        return conn
    
    @asynccontextmanager
    async def get_async_connection(self) -> AsyncGenerator[sqlite3.Connection, None]:
        """Get async database connection using context manager."""
        conn = None
        try:
            # Run database operations in thread pool to avoid blocking
            loop = asyncio.get_event_loop()
            conn = await loop.run_in_executor(None, self.get_connection)
            yield conn
        except Exception as e:
            if conn:
                await loop.run_in_executor(None, conn.rollback)
            logger.error(f"Database error: {e}")
            raise
        finally:
            if conn:
                loop = asyncio.get_event_loop()
                await loop.run_in_executor(None, conn.close)
    
    async def execute_query(self, query: str, params: tuple = (), 
                          fetch_one: bool = False, fetch_all: bool = False,
                          commit: bool = True) -> Optional[sqlite3.Row]:
        """
        Execute database query with proper async handling.
        
        Args:
            query: SQL query to execute
            params: Query parameters
            fetch_one: Return single row
            fetch_all: Return all rows
            commit: Auto-commit transaction
            
        Returns:
            Query result or None
        """
        async with self.get_async_connection() as conn:
            loop = asyncio.get_event_loop()
            
            cursor = await loop.run_in_executor(None, conn.execute, query, params)
            
            if fetch_one:
                result = await loop.run_in_executor(None, cursor.fetchone)
            elif fetch_all:
                result = await loop.run_in_executor(None, cursor.fetchall)
            else:
                result = cursor
            
            if commit:
                await loop.run_in_executor(None, conn.commit)
            
            return result
    
    async def init_database(self) -> None:
        """Initialize database with required tables."""
        logger.info(f"Initializing database at: {self.db_file}")
        
        # Users table
        users_table = """
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            chat_id INTEGER UNIQUE NOT NULL,
            username TEXT,
            first_name TEXT,
            last_name TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """
        
        # Cloudflare accounts table
        cf_accounts_table = """
        CREATE TABLE IF NOT EXISTS cf_accounts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            email TEXT NOT NULL,
            api_key TEXT NOT NULL,
            zone_id TEXT NOT NULL,
            zone_name TEXT NOT NULL,
            account_id TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(user_id) REFERENCES users(chat_id) ON DELETE CASCADE,
            UNIQUE(user_id)
        );
        """
        
        # Create indexes for better performance
        indexes = [
            "CREATE INDEX IF NOT EXISTS idx_users_chat_id ON users(chat_id);",
            "CREATE INDEX IF NOT EXISTS idx_cf_accounts_user_id ON cf_accounts(user_id);",
            "CREATE INDEX IF NOT EXISTS idx_cf_accounts_zone_id ON cf_accounts(zone_id);"
        ]
        
        try:
            # Create tables
            await self.execute_query(users_table)
            await self.execute_query(cf_accounts_table)
            
            # Create indexes
            for index_query in indexes:
                await self.execute_query(index_query)
            
            logger.info("Database initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize database: {e}")
            raise


# Global database manager instance
db_manager = DatabaseManager()


# Legacy compatibility functions
def get_db_connection() -> sqlite3.Connection:
    """Legacy function for backward compatibility."""
    return db_manager.get_connection()


async def init_db() -> None:
    """Initialize database (async version)."""
    await db_manager.init_database()
