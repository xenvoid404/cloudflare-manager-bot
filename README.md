# Cloudflare DNS Manager Bot

Bot Telegram untuk mengelola DNS Cloudflare dengan mudah dan aman menggunakan python-telegram-bot versi terbaru.

## 🚀 Fitur

- ✅ **Manajemen User**: Registrasi dan penyimpanan data pengguna
- ✅ **Akun Cloudflare**: Menyimpan konfigurasi akun Cloudflare
- 🚧 **DNS Records**: Menambah, melihat, dan mengelola record DNS (dalam pengembangan)
- ✅ **Webhook Support**: Dukungan webhook dengan nginx untuk production
- ✅ **Polling Mode**: Mode polling untuk development
- ✅ **Async/Await**: Menggunakan pola async/await modern
- ✅ **Error Handling**: Penanganan error yang komprehensif
- ✅ **Logging**: Sistem logging yang dapat dikonfigurasi

## 📋 Persyaratan

- Python 3.8+
- python-telegram-bot 21.9+
- SQLite3
- Nginx (untuk production dengan webhook)
- SSL Certificate (untuk webhook HTTPS)

## 🛠️ Instalasi

### 1. Clone Repository

```bash
git clone <repository-url>
cd cloudflare-dns-bot
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Konfigurasi Environment

```bash
cp .env.example .env
```

Edit file `.env` dan isi dengan konfigurasi Anda:

```env
BOT_TOKEN=your_bot_token_from_botfather
WEBHOOK_URL=https://your-domain.com
WEBHOOK_PATH=your_bot_token_here
WEBHOOK_SECRET_TOKEN=your_secret_token_here
```

### 4. Inisialisasi Database

Database akan otomatis dibuat saat pertama kali bot dijalankan.

## 🚀 Menjalankan Bot

### Mode Development (Polling)

Untuk development, kosongkan `WEBHOOK_URL` di file `.env`:

```bash
python Main.py
```

### Mode Production (Webhook)

#### 1. Setup Nginx

Copy konfigurasi nginx:

```bash
sudo cp nginx.conf.example /etc/nginx/sites-available/telegram-bot
sudo ln -s /etc/nginx/sites-available/telegram-bot /etc/nginx/sites-enabled/
```

Edit konfigurasi dan ganti:
- `your-domain.com` dengan domain Anda
- `/path/to/your/ssl/certificate.pem` dengan path SSL certificate
- `/path/to/your/ssl/private.key` dengan path SSL private key
- `YOUR_BOT_TOKEN` dengan token bot Anda

#### 2. Test dan Reload Nginx

```bash
sudo nginx -t
sudo systemctl reload nginx
```

#### 3. Jalankan Bot

```bash
python Main.py
```

## 📁 Struktur Project

```
cloudflare-dns-bot/
├── Main.py                 # Entry point utama
├── config.py              # Konfigurasi aplikasi
├── requirements.txt       # Dependencies Python
├── .env.example          # Template environment variables
├── nginx.conf.example    # Template konfigurasi nginx
├── README.md             # Dokumentasi
├── database/
│   ├── db.py             # Database connection dan setup
│   ├── bot.db            # SQLite database file
│   └── models/
│       ├── users_model.py        # Model untuk users
│       └── cf_accounts_model.py  # Model untuk Cloudflare accounts
└── handlers/
    ├── registration.py   # Registrasi semua handlers
    ├── start_handler.py  # Handler untuk /start dan /help
    └── menu_handler.py   # Handler untuk menu utama
```

## 🔧 Konfigurasi

### Environment Variables

| Variable | Deskripsi | Default |
|----------|-----------|---------|
| `BOT_TOKEN` | Token bot dari BotFather | **Required** |
| `WEBHOOK_URL` | URL webhook (kosongkan untuk polling) | - |
| `WEBHOOK_PATH` | Path webhook | `BOT_TOKEN` |
| `WEBHOOK_SECRET_TOKEN` | Secret token untuk webhook | `your_secret_token_here` |
| `LISTEN_IP` | IP address untuk bind server | `127.0.0.1` |
| `PORT` | Port untuk server | `8000` |
| `DATABASE_FILE` | Path file database SQLite | `database/bot.db` |
| `LOG_LEVEL` | Level logging (DEBUG, INFO, WARNING, ERROR) | `INFO` |
| `LOG_FILE` | Path file log (optional) | - |
| `DEBUG` | Mode debug | `False` |

### Database Schema

#### Table: users
```sql
CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    chat_id INTEGER UNIQUE,
    username TEXT,
    first_name TEXT,
    last_name TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

#### Table: cf_accounts
```sql
CREATE TABLE cf_accounts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    email TEXT NOT NULL,
    api_key TEXT NOT NULL,
    zone_id TEXT NOT NULL,
    zone_name TEXT NOT NULL,
    account_id TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(user_id) REFERENCES users(chat_id) ON DELETE CASCADE
);
```

## 🤖 Penggunaan Bot

### Perintah Tersedia

- `/start` - Memulai bot dan registrasi user
- `/menu` - Menampilkan menu utama
- `/help` - Menampilkan bantuan

### Flow Penggunaan

1. **Mulai Bot**: Pengguna mengirim `/start`
2. **Akses Menu**: Pengguna mengirim `/menu`
3. **Tambah Akun**: Pilih "Tambah Akun Cloudflare" (dalam pengembangan)
4. **Kelola DNS**: Gunakan fitur tambah/lihat record (dalam pengembangan)

## 🔒 Keamanan

### Webhook Security

- Menggunakan HTTPS dengan SSL certificate
- Secret token untuk validasi webhook
- Rate limiting di nginx
- Hanya menerima POST request dari Telegram

### Data Security

- API key Cloudflare disimpan dalam database (tanpa enkripsi sesuai permintaan)
- Validasi input pengguna
- Error handling yang aman tanpa leak informasi sensitif

## 📊 Monitoring dan Logging

### Log Files

Bot menggunakan Python logging dengan konfigurasi:

- Console output untuk development
- File logging (optional) untuk production
- Level logging yang dapat dikonfigurasi
- Separate logs untuk error dan access

### Nginx Logs

```bash
# Access log
tail -f /var/log/nginx/telegram_bot_access.log

# Error log
tail -f /var/log/nginx/telegram_bot_error.log
```

## 🛠️ Development

### Menambah Handler Baru

1. Buat file handler di `handlers/`
2. Import dan daftarkan di `handlers/registration.py`
3. Handler menggunakan async/await pattern

Contoh:
```python
async def my_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text("Hello!")

my_command_handler = CommandHandler("mycommand", my_handler)
```

### Testing

```bash
# Test dengan polling mode
export WEBHOOK_URL=""
python Main.py

# Test webhook (butuh nginx dan SSL)
export WEBHOOK_URL="https://your-domain.com"
python Main.py
```

## 📈 Performance

### Optimizations

- Async/await untuk non-blocking operations
- Database connection pooling ready
- Nginx reverse proxy untuk load balancing
- Rate limiting untuk mencegah spam

### Recommended Production Setup

- **Server**: VPS dengan minimal 1GB RAM
- **Database**: SQLite untuk start, PostgreSQL untuk scale
- **Web Server**: Nginx dengan HTTP/2
- **SSL**: Let's Encrypt atau commercial certificate
- **Monitoring**: Setup log monitoring dan alerts

## 🐛 Troubleshooting

### Common Issues

1. **Bot tidak merespons**
   - Cek token bot
   - Pastikan webhook URL accessible
   - Cek nginx logs

2. **Database errors**
   - Pastikan directory database dapat ditulis
   - Cek file permissions

3. **Webhook tidak bekerja**
   - Pastikan SSL certificate valid
   - Cek nginx konfigurasi
   - Verify webhook URL di Telegram

### Debug Mode

Set `DEBUG=True` di `.env` untuk informasi debug lebih detail.

## 📝 License

[Tambahkan license sesuai kebutuhan]

## 👨‍💻 Contributing

1. Fork repository
2. Buat feature branch
3. Commit changes
4. Push ke branch
5. Create Pull Request

## 📞 Support

Untuk bantuan atau pertanyaan, silakan buat issue di repository ini.