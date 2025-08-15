from database.db import get_db_connection


def save_user(user_data: dict):
    """Simpan atau perbarui data user"""
    query = """
    INSERT INTO users (chat_id, username, first_name, last_name)
    VALUES (?, ?, ?, ?)
    ON CONFLICT(chat_id) DO UPDATE SET
        username=excluded.username,
        first_name=excluded.first_name,
        last_name=excluded.last_name;
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


def user_exists(user_id: int) -> bool:
    """Periksa apakah user sudah terdaftar di database"""
    with get_db_connection() as conn:
        cursor = conn.execute(
            "SELECT 1 FROM users WHERE chat_id = ? LIMIT 1", (user_id,)
        )
        return cursor.fetchone() is not None


def user_has_account(user_id: int) -> bool:
    """Cek apakah user punya akun Cloudflare yang tersimpan"""
    with get_db_connection() as conn:
        cursor = conn.execute(
            "SELECT 1 FROM cf_accounts WHERE user_id = ? LIMIT 1", (user_id,)
        )
        return cursor.fetchone() is not None
