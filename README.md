# Cloudflare DNS Manager Bot

Bot Telegram untuk mengelola DNS record Cloudflare dengan mudah dan efisien.

## 🚀 Fitur

### ✅ Fitur yang Sudah Tersedia

- **👤 Registrasi User** - Pendaftaran otomatis pengguna baru
- **➕ Tambah Akun Cloudflare** - Proses step-by-step untuk menambahkan akun Cloudflare:
  - Input email Cloudflare
  - Input Global API Key
  - Input Account ID
  - Validasi kredensial otomatis
  - Pemilihan zone dari daftar yang tersedia
- **📋 Menu Utama** - Interface utama dengan semua fitur yang tersedia
- **⚙️ Others Menu** - Menu tambahan dengan fitur:
  - 🔄 Switch Zone (dalam pengembangan)
  - ❓ Help - Bantuan penggunaan bot
- **❓ Bantuan** - Dokumentasi lengkap penggunaan bot

### 🚧 Fitur dalam Pengembangan

- **📋 Lihat Record DNS**
  - Single Record - Lihat record DNS tertentu
  - From File - Lihat semua record DNS
- **📝 Tambah Record DNS**
  - Single Record - Tambah satu DNS record baru
  - From File - Tambah banyak DNS record dari file JSON
- **♻️ Edit Record DNS**
  - Single Record - Edit satu DNS record
  - From File - Edit banyak DNS record dari file JSON
- **🗑️ Hapus Record DNS**
  - Single Record - Hapus satu DNS record
  - From File - Hapus banyak DNS record dari file JSON
- **🔄 Switch Zone** - Ganti zone yang dikelola

## 📦 Dependencies

- `python-telegram-bot` - Library untuk Telegram Bot API
- `cloudflare` - Library untuk Cloudflare API
- `python-dotenv` - Untuk manajemen environment variables
- `sqlite3` - Database untuk menyimpan data user dan akun

## 🛠️ Instalasi

1. Clone repository ini
2. Install dependencies:
   ```bash
   pip install python-telegram-bot cloudflare python-dotenv
   ```
3. Buat file `.env` dan isi dengan konfigurasi berikut:
   ```env
   BOT_TOKEN=your_telegram_bot_token
   WEBHOOK_URL=your_webhook_url (optional)
   DATABASE_FILE=database/bot.db
   LOG_LEVEL=INFO
   ```

## 🎯 Cara Penggunaan

### Memulai Bot

1. Start bot dengan `/start`
2. Registrasi otomatis akan dilakukan
3. Akses menu utama dengan `/menu`

### Menambah Akun Cloudflare

1. Pilih "➕ Tambah Akun Cloudflare" di menu utama
2. Masukkan email Cloudflare Anda
3. Masukkan Global API Key (My Profile → API Tokens → Global API Key → View)
4. Masukkan Account ID (Dashboard → Right sidebar → Account ID)
5. Pilih zone yang ingin dikelola dari daftar yang tersedia
6. Akun akan tersimpan otomatis

### Mengelola DNS Record

Setelah menambahkan akun Cloudflare, Anda dapat:
- **Lihat Record** - Melihat DNS record yang ada
- **Tambah Record** - Menambah DNS record baru
- **Edit Record** - Mengubah DNS record yang ada
- **Hapus Record** - Menghapus DNS record

### Menu Lainnya

Akses menu tambahan melalui "⚙️ Others Menu":
- **Switch Zone** - Ganti zone aktif (dalam pengembangan)
- **Help** - Bantuan penggunaan bot

## 📱 Perintah Bot

- `/start` - Memulai bot dan registrasi
- `/menu` - Tampilkan menu utama
- `/help` - Bantuan penggunaan bot

## 🗂️ Struktur Project

```
├── Main.py                          # Entry point aplikasi
├── config.py                        # Konfigurasi aplikasi
├── database/
│   ├── db.py                       # Konfigurasi database
│   ├── bot.db                      # File database SQLite
│   └── models/
│       ├── users_model.py          # Model untuk data user
│       └── cf_accounts_model.py    # Model untuk akun Cloudflare
└── handlers/
    ├── registration.py             # Registrasi semua handler
    ├── start_handler.py           # Handler untuk command /start
    ├── menu_handler.py            # Handler untuk menu utama
    ├── add_cloudflare_handler.py  # Handler untuk tambah akun Cloudflare
    ├── other_menu_handler.py      # Handler untuk menu lainnya
    ├── dns_record_handlers.py     # Handler untuk operasi DNS record
    └── navigation_handler.py      # Handler untuk navigasi
```

## 🔒 Keamanan

- API Key Cloudflare disimpan dengan aman di database
- API Key ditampilkan dengan format tersembunyi (hanya 4 karakter pertama dan terakhir)
- Validasi input untuk semua data yang dimasukkan
- Session timeout untuk proses input data

## 📋 Database Schema

### Tabel `users`
- `id` - Auto increment primary key
- `chat_id` - Telegram chat ID (unique)
- `username` - Username Telegram
- `first_name` - Nama depan user
- `last_name` - Nama belakang user
- `created_at` - Waktu registrasi
- `updated_at` - Waktu update terakhir

### Tabel `cf_accounts`
- `id` - Auto increment primary key
- `user_id` - Foreign key ke users.chat_id
- `email` - Email Cloudflare
- `api_key` - Global API Key Cloudflare (encrypted)
- `account_id` - Account ID Cloudflare
- `zone_id` - Zone ID yang dipilih
- `zone_name` - Nama zone yang dipilih
- `created_at` - Waktu pembuatan
- `updated_at` - Waktu update terakhir

## 🚀 Deployment

### Mode Polling (Development)
```bash
python Main.py
```

### Mode Webhook (Production)
1. Set `WEBHOOK_URL` di file `.env`
2. Deploy ke server dengan HTTPS
3. Jalankan aplikasi

## 🔧 Logging

Bot menggunakan sistem logging dengan level:
- `DEBUG` - Detail debug
- `INFO` - Informasi umum
- `WARNING` - Peringatan
- `ERROR` - Error

Log dapat disimpan ke file dengan mengset `LOG_FILE` di environment variables.

## 📞 Support

Jika mengalami masalah atau ada pertanyaan, gunakan command `/help` di bot untuk mendapatkan bantuan.

## 📄 License

Project ini menggunakan lisensi MIT.