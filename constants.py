"""
Constants untuk Cloudflare DNS Manager Bot.
Mengumpulkan semua pesan dan konfigurasi constants.
"""

# ========== MESSAGES ==========
class Messages:
    class Common:
        UNAUTHORIZED = "Silakan jalankan /start terlebih dahulu untuk menggunakan bot ini."
        NO_ACCOUNT = "Anda belum menambahkan akun Cloudflare. Gunakan /menu dan pilih 'Tambah Akun Cloudflare'."
        ERROR_GENERIC = "Terjadi kesalahan. Gunakan /menu untuk mencoba lagi."
        LOADING = "Memproses permintaan Anda...\nMohon tunggu sebentar."
        SUCCESS = "Operasi berhasil dilakukan!"
        CANCELLED = "Operasi dibatalkan."

    class Start:
        WELCOME = """
Halo *{name}\\! Selamat datang di *Cloudflare DNS Manager Bot*\\.

Bot ini membantu Anda mengelola DNS Cloudflare langsung dari Telegram\\.

*Fitur yang tersedia:*
• Menambah record DNS
• Melihat record yang ada  
• Mengedit record DNS
• Menghapus record DNS
• Mengelola akun Cloudflare

Ketik /menu untuk mengakses menu utama\\.
        """

        SAVE_ERROR = "Terjadi kesalahan saat menyimpan data Anda. Silakan coba lagi nanti."

    class Menu:
        MAIN_WITH_ACCOUNT = """
*CLOUDFLARE DNS MANAGER*
━━━━━━━━━━━━━━━━━━━━━━━━
*Nama:* `{name}`
*Email:* `{email}`
*API Key:* {api_key_masked}
*Zone:* `{zone_name}`
━━━━━━━━━━━━━━━━━━━━━━━━
Pilih menu di bawah untuk mengelola DNS Anda\\.
        """

        MAIN_WITHOUT_ACCOUNT = """
*CLOUDFLARE DNS MANAGER*
━━━━━━━━━━━━━━━━━━━━━━━━
*Nama:* `{name}`
*Status:* `Belum ada akun terdaftar`
━━━━━━━━━━━━━━━━━━━━━━━━
Silakan tambahkan akun Cloudflare Anda untuk memulai mengelola DNS\\.
        """

    class Records:
        VIEW_TITLE = "*DNS Records Export*"
        VIEW_SUMMARY = """
{title}

*Zone:* `{zone_name}`
*Total Records:* `{total_records}`
*Exported:* `{export_time}`

File JSON berisi semua DNS records dengan format yang rapi.
        """.format(title=VIEW_TITLE)

        NO_RECORDS = "*DNS Records*\n\nTidak ada DNS records ditemukan di zone ini.\n\nGunakan /menu untuk kembali ke menu utama."

        FETCH_ERROR = """
Gagal mengambil DNS records.

Kemungkinan penyebab:
• API Key tidak valid
• Zone tidak ditemukan  
• Masalah koneksi internet

Gunakan /menu untuk mencoba lagi.
        """

        ADD_TITLE = "*Tambah Record DNS*"
        EDIT_TITLE = "*Edit Record DNS*"
        DELETE_TITLE = "*Hapus Record DNS*"

        OPERATION_MENU = """
{title}

Pilih cara {operation} record DNS:

1. *Single Record* - {operation_desc} satu DNS Record
2. *From File* - {operation_desc} banyak DNS Record dari file JSON
        """

    class CloudflareAccount:
        ADD_START = """
*Tambah Akun Cloudflare*

Saya akan memandu Anda untuk menambahkan akun Cloudflare\\.

*Langkah 1/3*
Silakan masukkan email Cloudflare Anda\\:
        """

        EMAIL_SUCCESS = """
Email berhasil disimpan\\!

*Langkah 2/3*
Silakan masukkan Global API Key Cloudflare Anda\\:

_API Key dapat ditemukan di\\:_
My Profile → API Tokens → Global API Key → View
        """

        API_KEY_SUCCESS = """
API Key berhasil disimpan!

*Langkah 3/3*
Silakan masukkan Account ID Cloudflare Anda:

_Account ID dapat ditemukan di:_
Dashboard → Right sidebar → Account ID
        """

        VERIFYING = "Memverifikasi kredensial dan mengambil daftar zone...\nMohon tunggu sebentar..."

        VERIFICATION_FAILED = """
Gagal mengambil daftar zone. Kemungkinan penyebab:
• Email, API Key, atau Account ID tidak valid
• Tidak ada zone di akun Cloudflare
• Masalah koneksi internet

Gunakan /menu untuk mencoba lagi.
        """

        ZONES_FOUND = "Berhasil terhubung ke Cloudflare!\n\n*Ditemukan {count} zone:*\nSilakan pilih zone yang ingin dikelola:"

        ACCOUNT_SAVED = """
*Akun Cloudflare berhasil ditambahkan!*

*Email:* `{email}`
*Zone:* `{zone_name}`

Sekarang Anda dapat mengelola DNS record.
Gunakan /menu untuk mengakses fitur-fitur yang tersedia.
        """

        SAVE_FAILED = "Gagal menyimpan akun ke database. Silakan coba lagi.\n\nGunakan /menu untuk mencoba lagi."

        CANCELLED = "Penambahan akun Cloudflare dibatalkan.\n\nGunakan /menu untuk kembali ke menu utama."

    class Help:
        CONTENT = """
*Bantuan Cloudflare DNS Manager*

*Fitur yang tersedia:*
• Tambah Record - Menambah record DNS baru
• Lihat Record - Melihat semua record DNS
• Edit Record - Mengubah record DNS yang ada
• Hapus Record - Menghapus record DNS
• Others Menu - Menu tambahan dan pengaturan

*Perintah:*
• /start - Memulai bot dan registrasi
• /menu - Menu utama
• /help - Bantuan

*Tips:*
• Pastikan email, API Key, dan Account ID Cloudflare sudah benar
• API Key dapat ditemukan di My Profile → API Tokens → Global API Key
• Account ID dapat ditemukan di Dashboard sidebar kanan

Gunakan /menu untuk mengakses menu utama.
        """

    class Validation:
        INVALID_EMAIL = "Format email tidak valid. Silakan masukkan email yang benar:"
        INVALID_API_KEY = "API Key tampaknya tidak valid. Silakan periksa kembali dan masukkan API Key yang benar:"
        INVALID_ACCOUNT_ID = "Account ID tampaknya tidak valid. Silakan periksa kembali dan masukkan Account ID yang benar:"
        INVALID_SELECTION = "Pilihan tidak valid. Gunakan /menu untuk mencoba lagi."
        ZONE_NOT_FOUND = "Zone tidak ditemukan. Gunakan /menu untuk mencoba lagi."


# ========== BUTTON LABELS ==========
class Buttons:
    # Main Menu
    VIEW_RECORDS = "Lihat Record"
    ADD_RECORD = "Tambah Record"
    EDIT_RECORD = "Edit Record"
    DELETE_RECORD = "Hapus Record"
    OTHERS_MENU = "Others Menu"
    ADD_CLOUDFLARE = "Tambah Akun Cloudflare"

    # Operations
    SINGLE_RECORD = "Single Record"
    FROM_FILE = "From File"

    # Navigation
    BACK_TO_MAIN = "Back to Main Menu"
    CANCEL = "Batal"

    # Others Menu
    HELP = "Bantuan"
    DELETE_ACCOUNT = "Hapus Akun"
    SWITCH_ZONE = "Ganti Zone"


# ========== CALLBACK DATA ==========
class CallbackData:
    # Main Actions
    GET_RECORDS = "get_records"
    ADD_RECORDS = "add_records"
    EDIT_RECORDS = "edit_records"
    REMOVE_RECORDS = "remove_records"
    OTHERS_MENU = "others_menu"
    ADD_CLOUDFLARE = "add_cloudflare"

    # Navigation
    BACK_TO_MAIN_MENU = "back_to_main_menu"

    # Record Operations
    ADD_SINGLE_RECORD = "add_single_record"
    ADD_RECORD_FROM_FILE = "add_record_from_file"
    EDIT_SINGLE_RECORD = "edit_single_record"
    EDIT_RECORD_FROM_FILE = "edit_record_from_file"
    REMOVE_SINGLE_RECORD = "remove_single_record"
    REMOVE_RECORD_FROM_FILE = "remove_record_from_file"

    # Others Menu
    HELP_MENU = "help_menu"
    DELETE_ACCOUNT = "delete_account"
    SWITCH_ZONE = "switch_zone"

    # Cloudflare Account
    CANCEL_ADD_ACCOUNT = "cancel_add_account"
    SELECT_ZONE_PREFIX = "select_zone_"


# ========== REGEX PATTERNS ==========
class Patterns:
    # Email validation (basic)
    EMAIL_BASIC = r"^[^@]+@[^@]+\.[^@]+$"

    @classmethod
    def get_menu_callback_exclusions(cls) -> str:
        """Get the pattern for menu callback exclusions."""
        return (
            f"^(?!{CallbackData.ADD_CLOUDFLARE}|{CallbackData.GET_RECORDS}|"
            f"{CallbackData.ADD_RECORDS}|{CallbackData.EDIT_RECORDS}|"
            f"{CallbackData.REMOVE_RECORDS}|{CallbackData.OTHERS_MENU}|"
            f"{CallbackData.BACK_TO_MAIN_MENU}|switch_zone|help_menu|"
            f"{CallbackData.SELECT_ZONE_PREFIX}|{CallbackData.CANCEL_ADD_ACCOUNT}).*$"
        )


# ========== CONFIGURATION ==========
class Config:
    # API Timeouts
    CLOUDFLARE_API_TIMEOUT = 30

    # Conversation timeouts (seconds)
    CONVERSATION_TIMEOUT = 300  # 5 minutes

    # API Key masking
    API_KEY_VISIBLE_CHARS = 4

    # File naming
    EXPORT_FILENAME_FORMAT = "dns_records_{zone_name}_{timestamp}.json"
    EXPORT_TIMESTAMP_FORMAT = "%Y%m%d_%H%M%S"
    DISPLAY_TIMESTAMP_FORMAT = "%Y-%m-%d %H:%M:%S"

    # Validation lengths
    MIN_API_KEY_LENGTH = 32
    MIN_ACCOUNT_ID_LENGTH = 32


# ========== API ENDPOINTS ==========
class CloudflareAPI:
    BASE_URL = "https://api.cloudflare.com/client/v4"
    ZONES = f"{BASE_URL}/zones"

    @staticmethod
    def zones_endpoint():
        return CloudflareAPI.ZONES

    @staticmethod
    def dns_records_endpoint(zone_id: str):
        return f"{CloudflareAPI.ZONES}/{zone_id}/dns_records"

    @staticmethod
    def dns_record_endpoint(zone_id: str, record_id: str):
        return f"{CloudflareAPI.ZONES}/{zone_id}/dns_records/{record_id}"


# ========== HEADERS TEMPLATES ==========
class Headers:
    @staticmethod
    def cloudflare_auth(email: str, api_key: str) -> dict:
        return {
            "X-Auth-Email": email,
            "X-Auth-Key": api_key,
            "Content-Type": "application/json",
        }
