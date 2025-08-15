import os
from dotenv import load_dotenv

# Muat environment variable dari file .env
load_dotenv()

# --- Konfigurasi Bot dan Webhook ---
BOT_TOKEN = os.getenv("BOT_TOKEN")
if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN tidak ditemukan di environment variables!")

WEBHOOK_URL = os.getenv("WEBHOOK_URL")
WEBHOOK_PATH = os.getenv("WEBHOOK_PATH", BOT_TOKEN)

# --- Konfigurasi Server ---
LISTEN_IP = os.getenv("LISTEN_IP", "0.0.0.0")
PORT = int(os.getenv("PORT", "5000"))

# --- Konfigurasi Database ---
DATABASE_FILE = os.getenv("DATABASE_FILE", "database/bot.db")
