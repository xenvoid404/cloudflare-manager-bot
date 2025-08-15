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
    Database manager untuk menangani koneksi SQLite dengan dukungan async yang tepat.
    """

    def __init__(self, db_file: str = DATABASE_FILE):
        self.db_file = db_file
        self._ensure_directory()

    def _ensure_directory(self) -> None:
        """Pastikan direktori database ada."""
        os.makedirs(os.path.dirname(self.db_file), exist_ok=True)

    def get_connection(self) -> sqlite3.Connection:
        """Dapatkan koneksi database dengan row factory yang tepat."""
        conn = sqlite3.connect(self.db_file, timeout=30.0)
        conn.row_factory = sqlite3.Row
        # Aktifkan foreign key constraints
        conn.execute("PRAGMA foreign_keys = ON")
        return conn

    @asynccontextmanager
    async def get_async_connection(self) -> AsyncGenerator[sqlite3.Connection, None]:
        """Dapatkan koneksi database async menggunakan context manager."""
        conn = None
        try:
            # Jalankan operasi database di thread pool untuk menghindari blocking
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

    async def execute_query(
        self,
        query: str,
        params: tuple = (),
        fetch_one: bool = False,
        fetch_all: bool = False,
        commit: bool = True,
    ) -> Optional[sqlite3.Row]:
        """
        Jalankan query database dengan penanganan async yang tepat.

        Args:
            query: SQL query yang akan dijalankan
            params: Parameter query
            fetch_one: Return single row
            fetch_all: Return all rows
            commit: Auto-commit transaction

        Returns:
            Hasil query atau None
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
        """Inisialisasi database dengan tabel yang diperlukan."""
        logger.info(f"Inisialisasi database di: {self.db_file}")

        # Tabel users
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

        # Tabel Cloudflare accounts
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

        # Buat index untuk performa yang lebih baik
        indexes = [
            "CREATE INDEX IF NOT EXISTS idx_users_chat_id ON users(chat_id);",
            "CREATE INDEX IF NOT EXISTS idx_cf_accounts_user_id ON cf_accounts(user_id);",
            "CREATE INDEX IF NOT EXISTS idx_cf_accounts_zone_id ON cf_accounts(zone_id);",
        ]

        try:
            # Buat tabel
            await self.execute_query(users_table)
            await self.execute_query(cf_accounts_table)

            # Buat index
            for index_query in indexes:
                await self.execute_query(index_query)

            logger.info("Database berhasil diinisialisasi")

        except Exception as e:
            logger.error(f"Gagal menginisialisasi database: {e}")
            raise


# Global database manager instance
db_manager = DatabaseManager()


# Legacy compatibility functions
def get_db_connection() -> sqlite3.Connection:
    """Fungsi legacy untuk backward compatibility."""
    return db_manager.get_connection()


async def init_db() -> None:
    """Inisialisasi database (versi async)."""
    await db_manager.init_database()
