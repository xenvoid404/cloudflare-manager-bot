# Cloudflare DNS Manager Bot

Bot Telegram untuk mengelola DNS records Cloudflare dengan mudah dan aman.

## ✨ Fitur Utama

### 🔐 Manajemen Akun
- **Registrasi Pengguna**: Sistem registrasi otomatis untuk pengguna baru
- **Manajemen Akun Cloudflare**: Tambah dan kelola akun Cloudflare dengan validasi kredensial
- **Keamanan API Key**: API Key disembunyikan untuk keamanan (hanya menampilkan 4 karakter pertama dan terakhir)

### 🌐 Manajemen DNS Records
- **📋 Lihat Records**: Export semua DNS records dalam format JSON yang terstruktur dan rapi
- **📝 Tambah Record**: Menambahkan DNS record baru ke zone
- **♻️ Edit Record**: Mengedit DNS record yang sudah ada
- **🗑️ Hapus Record**: Menghapus DNS record

### 🛠️ Fitur Teknis
- **Multi-Zone Support**: Pilih zone yang ingin dikelola dari daftar zone yang tersedia
- **Real-time Validation**: Validasi kredensial dan data secara real-time
- **Error Handling**: Sistem error handling yang komprehensif
- **Logging**: Sistem logging untuk monitoring dan debugging
- **Database**: Penyimpanan data pengguna dan akun menggunakan SQLite

## 🚀 Instalasi

### Prasyarat
- Python 3.8+
- pip (Python package manager)
- Bot Token dari BotFather Telegram

### Langkah Instalasi

1. **Clone Repository**
   ```bash
   git clone <repository-url>
   cd cloudflare-dns-bot
   ```

2. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Konfigurasi**
   - Edit file `config.py` sesuai kebutuhan
   - Tambahkan Bot Token Telegram
   - Sesuaikan pengaturan database dan logging

4. **Jalankan Bot**
   ```bash
   python Main.py
   ```

## 📝 Cara Penggunaan

### Memulai Bot
1. Start bot dengan command `/start`
2. Pilih menu dengan command `/menu`

### Menambah Akun Cloudflare
1. Pilih "➕ Tambah Akun Cloudflare"
2. Masukkan email Cloudflare
3. Masukkan Global API Key
4. Masukkan Account ID
5. Pilih zone yang ingin dikelola

### Mengelola DNS Records

#### Melihat Records
1. Pilih "📋 Lihat Record" dari menu utama
2. Bot akan mengambil semua DNS records
3. File JSON dengan informasi lengkap akan dikirim

#### Format Export JSON
```json
{
  "zone_info": {
    "zone_name": "example.com",
    "zone_id": "zone_id_here",
    "email": "user@example.com",
    "total_records": 5
  },
  "records": [
    {
      "id": "record_id",
      "type": "A",
      "name": "example.com",
      "content": "192.168.1.1",
      "ttl": 300,
      "proxied": true,
      "locked": false,
      "created_on": "2023-01-01T00:00:00Z",
      "modified_on": "2023-01-01T00:00:00Z"
    }
  ],
  "export_info": {
    "exported_at": "2023-01-01T00:00:00",
    "exported_by": "User Name (123456789)"
  }
}
```

## 🏗️ Struktur Project

```
├── Main.py                     # Entry point aplikasi
├── config.py                   # Konfigurasi bot
├── database/
│   ├── db.py                  # Database connection handler
│   ├── models/
│   │   ├── users_model.py     # Model untuk data pengguna
│   │   └── cf_accounts_model.py # Model untuk akun Cloudflare
│   └── bot.db                 # SQLite database file
├── handlers/
│   ├── start_handler.py       # Handler untuk command /start
│   ├── menu_handler.py        # Handler untuk menu utama dan navigasi
│   ├── registration.py        # Registrasi semua handlers
│   ├── others_menu_handler.py # Handler untuk menu lainnya
│   └── cloudflare/
│       ├── add_cloudflare_handler.py # Handler penambahan akun CF
│       ├── records/
│       │   ├── get_records_handler.py    # Handler lihat records
│       │   ├── add_records_handler.py    # Handler tambah records
│       │   ├── edit_records_handler.py   # Handler edit records
│       │   └── remove_records_handler.py # Handler hapus records
└── README.md                  # Dokumentasi project
```

## 🔧 Perbaikan Terbaru

### v2.1.0 - Latest Updates

#### 🐛 Bug Fixes
- **Fixed select_zone_* callback error**: Memperbaiki masalah callback `select_zone_*` yang menyebabkan error pada proses penambahan akun Cloudflare
- **Improved menu_command handling**: Menu command sekarang dapat menangani baik command (`/menu`) maupun callback dengan kondisi yang tepat

#### ✨ New Features  
- **Complete DNS Records Viewer**: Fitur "Lihat Records" sekarang fully implemented dengan:
  - Real-time fetching dari Cloudflare API
  - Export dalam format JSON yang terstruktur dan rapi
  - Informasi lengkap termasuk metadata zone dan export info
  - Error handling yang komprehensif

#### 🔄 Improvements
- **Unified Navigation**: Menggabungkan logika `back_to_main_menu` ke dalam `menu_handler.py` untuk simplifikasi
- **Better Callback Pattern Matching**: Perbaikan pattern matching untuk callback handlers
- **Enhanced Error Messages**: Pesan error yang lebih informatif dan user-friendly
- **Code Structure**: Struktur kode yang lebih clean, scalable, dan mudah dipahami

## 🛡️ Keamanan

- **API Key Protection**: API Key tidak pernah ditampilkan secara penuh
- **Input Validation**: Semua input divalidasi sebelum diproses
- **Error Handling**: Error handling yang aman tanpa expose informasi sensitif
- **Timeout Protection**: Request timeout untuk mencegah hanging
- **Database Security**: Prepared statements untuk mencegah SQL injection

## 📊 Logging

Bot menggunakan sistem logging yang komprehensif:
- **Info Level**: Aktivitas normal pengguna
- **Warning Level**: Kondisi yang perlu perhatian
- **Error Level**: Error yang perlu investigasi
- **Debug Level**: Informasi detail untuk development

## 🤝 Kontribusi

Untuk berkontribusi pada project ini:
1. Fork repository
2. Buat feature branch
3. Commit perubahan
4. Push ke branch
5. Buat Pull Request

## 📞 Support

Jika mengalami masalah atau butuh bantuan:
- Buat issue di repository GitHub
- Periksa log untuk informasi error detail
- Pastikan semua dependencies terinstall dengan benar

## 📜 License

Project ini menggunakan lisensi MIT. Lihat file LICENSE untuk detail lengkap.

---

**Note**: Bot ini dikembangkan untuk memudahkan manajemen DNS Cloudflare melalui Telegram dengan fokus pada keamanan, kemudahan penggunaan, dan reliability.