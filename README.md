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
├── Main.py                          # Entry point aplikasi
├── config.py                        # Konfigurasi bot  
├── constants.py                     # Constants, messages, dan konfigurasi terpusat
├── requirements.txt                 # Dependencies
├── README.md                        # Dokumentasi project
│
├── database/                        # Database layer dengan async support
│   ├── __init__.py
│   ├── db.py                       # DatabaseManager dengan connection pooling
│   ├── models/                     # Database models
│   │   ├── __init__.py
│   │   ├── users_model.py          # User data operations
│   │   └── cf_accounts_model.py    # Cloudflare account operations
│   └── bot.db                      # SQLite database file
│
├── services/                        # Service layer untuk external APIs
│   ├── __init__.py
│   └── cloudflare_service.py       # Cloudflare API client dengan error handling
│
├── utils/                           # Utility functions dan helpers
│   ├── __init__.py
│   ├── decorators.py               # Middleware decorators (auth, error handling)
│   └── helpers.py                  # Common utilities dan ResponseBuilder
│
└── handlers/                        # Request handlers dengan clean architecture
    ├── __init__.py
    ├── start_handler.py            # /start command handler
    ├── menu_handler.py             # Main menu dan navigation
    ├── registration.py             # Handler registration
    ├── others_menu_handler.py      # Additional menu features
    └── cloudflare/
        ├── __init__.py
        ├── add_cloudflare_handler.py  # Cloudflare account setup
        └── records/
            ├── __init__.py
            ├── base_records_handler.py   # Base class untuk DNS operations
            ├── get_records_handler.py    # DNS records export (JSON)
            ├── add_records_handler.py    # Add DNS records
            ├── edit_records_handler.py   # Edit DNS records
            └── remove_records_handler.py # Remove DNS records
```

### 📋 **Architectural Patterns**

**🏛️ Clean Architecture:**
- **Presentation Layer**: Handlers untuk user interaction
- **Business Logic**: Services untuk domain operations  
- **Data Layer**: Models dan database operations
- **Infrastructure**: Utils, constants, dan external integrations

**🔧 Design Patterns:**
- **Factory Pattern**: Service instantiation 
- **Decorator Pattern**: Middleware untuk cross-cutting concerns
- **Builder Pattern**: Response construction dengan fluent interface
- **Template Method**: Base handlers dengan customizable behavior

**⚡ Async Architecture:**
- Non-blocking database operations dengan connection pooling
- Concurrent API requests dengan proper timeout handling
- Thread pool execution untuk CPU-bound operations
- Graceful error handling dengan fallback mechanisms

## 🔧 Perbaikan Terbaru

### v3.0.0 - Major Refactoring & Architecture Improvements

#### 🏗️ **Complete Code Refactoring**
- **Clean Architecture**: Implementasi clean architecture dengan separation of concerns
- **DRY Principle**: Eliminasi duplikasi kode dengan base classes dan utility functions
- **SOLID Principles**: Struktur kode yang mengikuti prinsip SOLID untuk maintainability
- **Scalable Design**: Arsitektur yang mudah di-extend dan di-maintain

#### 🔧 **New Infrastructure Components**

**Constants Management** (`constants.py`):
- Centralized message templates dengan MarkdownV2 escaping
- Button labels dan callback data constants  
- Configuration constants dan API endpoints
- Emoji constants untuk konsistensi UI

**Service Layer** (`services/`):
- `CloudflareService`: Centralized API client dengan proper error handling
- Async support dengan connection pooling
- Custom exception handling (`CloudflareAPIError`)
- Factory pattern untuk service instantiation

**Utility Layer** (`utils/`):
- `decorators.py`: Middleware decorators untuk authentication, error handling, logging
- `helpers.py`: Common utility functions dan ResponseBuilder pattern
- API key masking, validation functions, safe message formatting

**Database Improvements** (`database/`):
- `DatabaseManager` class dengan proper async support
- Connection pooling dan transaction management
- Better error handling dan rollback support
- Database indexes untuk performance optimization

#### 🎯 **Handler Refactoring**

**Base Classes**:
- `BaseRecordsHandler`: Abstract base untuk DNS operations (Add, Edit, Remove)
- Eliminasi 80% duplikasi kode di record handlers
- Consistent error handling dan validation patterns

**Middleware Integration**:
- `@authenticated_handler`: Combined user validation dan error handling
- `@cloudflare_handler`: Cloudflare account validation dengan context injection
- `@handle_errors`: Consistent error handling across all handlers

**Smart Response Handling**:
- Unified `send_response()` function untuk callback dan message handling
- Automatic MarkdownV2 escaping dan validation
- Keyboard builder dengan type safety

#### ✨ **Enhanced Features**

**Improved DNS Records Export**:
- Structured JSON export dengan metadata
- Timestamp formatting dan file naming conventions
- Better error messages dan user feedback

**Better Validation**:
- Email, API key, dan Account ID validation helpers
- Input sanitization dan security improvements
- Comprehensive error messages

**Enhanced User Experience**:
- Consistent messaging across all features
- Better loading states dan progress indicators
- Improved error recovery dan user guidance

#### 🚀 **Performance & Reliability**

**Database Performance**:
- Proper indexing untuk faster queries
- Connection pooling untuk reduced latency
- Async operations dengan thread pool execution

**Error Handling**:
- Graceful degradation dengan fallback responses
- Comprehensive logging untuk debugging
- User-friendly error messages

**Code Quality**:
- Type hints throughout codebase
- Comprehensive docstrings
- Clean import management

#### 🔄 **Migration Improvements**
- **Backward Compatibility**: Legacy functions tetap tersedia
- **Gradual Migration**: Refactored components dapat digunakan bertahap
- **Database Migration**: Automatic schema updates dengan indexes

### v2.1.0 - Previous Updates

#### 🐛 Bug Fixes
- **Fixed select_zone_* callback error**: Memperbaiki masalah callback `select_zone_*` yang menyebabkan error pada proses penambahan akun Cloudflare
- **Improved menu_command handling**: Menu command sekarang dapat menangani baik command (`/menu`) maupun callback dengan kondisi yang tepat

#### ✨ New Features  
- **Complete DNS Records Viewer**: Fitur "Lihat Records" sekarang fully implemented dengan:
  - Real-time fetching dari Cloudflare API
  - Export dalam format JSON yang terstruktur dan rapi
  - Informasi lengkap termasuk metadata zone dan export info
  - Error handling yang komprehensif

#### 🔄 Previous Improvements
- **Unified Navigation**: Menggabungkan logika `back_to_main_menu` ke dalam `menu_handler.py` untuk simplifikasi
- **Better Callback Pattern Matching**: Perbaikan pattern matching untuk callback handlers
- **Enhanced Error Messages**: Pesan error yang lebih informatif dan user-friendly

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