import sqlite3
import os
import logging
from config import DATABASE_FILE

logger = logging.getLogger(__name__)


def get_db_connection() -> sqlite3.Connection:
    """Membuat koneksi ke database"""
    # Pastikan direktori untuk file database ada
    os.makedirs(os.path.dirname(DATABASE_FILE), exist_ok=True)
    conn = sqlite3.connect(DATABASE_FILE)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """Membuat tabel-tabel database jika belum ada."""
    logger.info(f"Inisialisasi database di: {DATABASE_FILE}")
    with get_db_connection() as conn:
        # Tabel users
        conn.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            chat_id INTEGER UNIQUE,
            username TEXT,
            first_name TEXT,
            last_name TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """)

        # Tabel cf_accounts
        conn.execute("""
        CREATE TABLE IF NOT EXISTS cf_accounts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            email TEXT NOT NULL,
            api_key BLOB NOT NULL,
            zone_id TEXT NOT NULL,
            zone_name TEXT NOT NULL,
            account_id TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(user_id) REFERENCES users(chat_id) ON DELETE CASCADE
        );
        """)
        conn.commit()
    logger.info("Database siap.")
