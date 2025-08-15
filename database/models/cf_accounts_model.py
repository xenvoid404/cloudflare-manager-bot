from database.db import get_db_connection


def save_cloudflare_account(account_data: dict):
    """Simpan konfigurasi akun cloudflare"""
    query = """
    INSERT INTO cf_accounts (user_id, email, api_key, account_id, zone_id, zone_name)
    VALUES (?, ?, ?, ?, ?, ?)
    """
    with get_db_connection() as conn:
        conn.execute(
            query,
            (
                account_data["user_id"],
                account_data["email"],
                account_data["api_key"],  # Ingat, ini harus dienkripsi!
                account_data["account_id"],
                account_data["zone_id"],
                account_data["zone_name"],
            ),
        )
        conn.commit()


def get_cloudflare_account(chat_id: int):
    """Ambil data akun cloudflare untuk user tertentu"""
    query = """
    SELECT user_id, email, api_key, zone_id, zone_name, account_id
    FROM cf_accounts
    WHERE user_id = ?
    LIMIT 1
    """
    with get_db_connection() as conn:
        result = conn.execute(query, (chat_id,)).fetchone()

    return result if result else None
