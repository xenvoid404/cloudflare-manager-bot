# Cloudflare DNS Manager Bot

Bot Telegram untuk mengelola DNS records Cloudflare dengan mudah dan aman.

## Fitur Utama

### Manajemen Akun
- **Registrasi Pengguna**: Sistem registrasi otomatis untuk pengguna baru
- **Manajemen Akun Cloudflare**: Tambah dan kelola akun Cloudflare dengan validasi kredensial
- **Keamanan API Key**: API Key disembunyikan untuk keamanan (hanya menampilkan 4 karakter pertama dan terakhir)

### Manajemen DNS Records
- **Lihat Records**: Export semua DNS records dalam format JSON yang terstruktur dan rapi
- **Tambah Record**: Menambahkan DNS record baru ke zone
- **Edit Record**: Mengedit DNS record yang sudah ada
- **Hapus Record**: Menghapus DNS record

### Fitur Teknis
- **Multi-Zone Support**: Pilih zone yang ingin dikelola dari daftar zone yang tersedia
- **Real-time Validation**: Validasi kredensial dan data secara real-time
- **Error Handling**: Sistem error handling yang komprehensif
- **Logging**: Sistem logging untuk monitoring dan debugging
- **Database**: Penyimpanan data pengguna dan akun menggunakan SQLite

## Instalasi

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

## Cara Penggunaan

### Memulai Bot
1. Start bot dengan command `/start`
2. Pilih menu dengan command `/menu`

### Menambah Akun Cloudflare
1. Pilih "Tambah Akun Cloudflare"
2. Masukkan email Cloudflare
3. Masukkan Global API Key
4. Masukkan Account ID
5. Pilih zone yang ingin dikelola

### Mengelola DNS Records

#### Melihat Records
1. Pilih "Lihat Record" dari menu utama
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