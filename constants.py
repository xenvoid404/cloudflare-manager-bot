"""
Constants for the Cloudflare DNS Manager Bot.
Centralizes all messages, emojis, and configuration constants.
"""


# ========== EMOJIS ==========
class Emojis:
    # General
    WAVE = "👋"
    WARNING = "⚠️"
    ERROR = "❌"
    SUCCESS = "✅"
    LOADING = "🔄"
    CONSTRUCTION = "🚧"

    # Menu and Navigation
    MENU = "📋"
    BACK = "🔙"
    HOME = "🏠"
    SETTINGS = "⚙️"
    HELP = "📖"

    # DNS Operations
    VIEW_RECORDS = "📋"
    ADD_RECORD = "📝"
    EDIT_RECORD = "♻️"
    DELETE_RECORD = "🗑️"

    # Cloudflare
    CLOUDFLARE = "🌐"
    KEY = "🔑"
    EMAIL = "📧"
    ID = "🆔"
    ZONE = "🌍"

    # File Operations
    FILE = "📁"
    EXPORT = "📊"
    IMPORT = "📥"

    # Status
    LOCKED = "🔒"
    UNLOCKED = "🔓"
    ACTIVE = "🟢"
    INACTIVE = "🔴"


# ========== MESSAGES ==========
class Messages:
    class Common:
        UNAUTHORIZED = f"{Emojis.WARNING} Silakan jalankan /start terlebih dahulu untuk menggunakan bot ini."
        NO_ACCOUNT = f"{Emojis.WARNING} Anda belum menambahkan akun Cloudflare. Gunakan /menu dan pilih 'Tambah Akun Cloudflare'."
        ERROR_GENERIC = (
            f"{Emojis.ERROR} Terjadi kesalahan. Gunakan /menu untuk mencoba lagi."
        )
        LOADING = (
            f"{Emojis.LOADING} Memproses permintaan Anda...\nMohon tunggu sebentar."
        )
        SUCCESS = f"{Emojis.SUCCESS} Operasi berhasil dilakukan!"
        CANCELLED = f"{Emojis.ERROR} Operasi dibatalkan."

    class Start:
        WELCOME = """
{emoji_wave} Halo *{{name}}*\\! Selamat datang di *Cloudflare DNS Manager Bot*\\.

Bot ini membantu Anda mengelola DNS Cloudflare langsung dari Telegram\\.

{emoji_settings} *Fitur yang tersedia:*
• Menambah record DNS
• Melihat record yang ada  
• Mengedit record DNS
• Menghapus record DNS
• Mengelola akun Cloudflare

Ketik /menu untuk mengakses menu utama\\.
        """.format(emoji_wave=Emojis.WAVE, emoji_settings=Emojis.SETTINGS)

        SAVE_ERROR = f"{Emojis.WARNING} Terjadi kesalahan saat menyimpan data Anda. Silakan coba lagi nanti."

    class Menu:
        MAIN_WITH_ACCOUNT = """
*{emoji_cloudflare} CLOUDFLARE DNS MANAGER*
━━━━━━━━━━━━━━━━━━━━━━━━
{emoji_wave} *Nama:* `{{name}}`
{emoji_email} *Email:* `{{email}}`
{emoji_key} *API Key:* {{api_key_masked}}
{emoji_zone} *Zone:* `{{zone_name}}`
━━━━━━━━━━━━━━━━━━━━━━━━
Pilih menu di bawah untuk mengelola DNS Anda\\.
        """.format(
            emoji_cloudflare=Emojis.CLOUDFLARE,
            emoji_wave=Emojis.WAVE,
            emoji_email=Emojis.EMAIL,
            emoji_key=Emojis.KEY,
            emoji_zone=Emojis.ZONE,
        )

        MAIN_WITHOUT_ACCOUNT = """
*{emoji_cloudflare} CLOUDFLARE DNS MANAGER*
━━━━━━━━━━━━━━━━━━━━━━━━
{emoji_wave} *Nama:* `{{name}}`
📱 *Status:* `Belum ada akun terdaftar`
━━━━━━━━━━━━━━━━━━━━━━━━
Silakan tambahkan akun Cloudflare Anda untuk memulai mengelola DNS\\.
        """.format(emoji_cloudflare=Emojis.CLOUDFLARE, emoji_wave=Emojis.WAVE)

    class Records:
        VIEW_TITLE = f"*{Emojis.VIEW_RECORDS} DNS Records Export*"
        VIEW_SUMMARY = """
{title}

{emoji_zone} *Zone:* `{{zone_name}}`
{emoji_export} *Total Records:* `{{total_records}}`
📅 *Exported:* `{{export_time}}`

File JSON berisi semua DNS records dengan format yang rapi.
        """.format(title=VIEW_TITLE, emoji_zone=Emojis.ZONE, emoji_export=Emojis.EXPORT)

        NO_RECORDS = f"*{Emojis.VIEW_RECORDS} DNS Records*\n\nTidak ada DNS records ditemukan di zone ini.\n\nGunakan /menu untuk kembali ke menu utama."

        FETCH_ERROR = f"""
{Emojis.ERROR} Gagal mengambil DNS records.

Kemungkinan penyebab:
• API Key tidak valid
• Zone tidak ditemukan  
• Masalah koneksi internet

Gunakan /menu untuk mencoba lagi.
        """

        ADD_TITLE = f"*{Emojis.ADD_RECORD} Tambah Record DNS*"
        EDIT_TITLE = f"*{Emojis.EDIT_RECORD} Edit Record DNS*"
        DELETE_TITLE = f"*{Emojis.DELETE_RECORD} Hapus Record DNS*"

        OPERATION_MENU = """
{title}

Pilih cara {operation} record DNS:

1. *Single Record* - {operation_desc} satu DNS Record
2. *From File* - {operation_desc} banyak DNS Record dari file JSON
        """

    class CloudflareAccount:
        ADD_START = f"""
*➕ Tambah Akun Cloudflare*

Saya akan memandu Anda untuk menambahkan akun Cloudflare\\.

{Emojis.EMAIL} *Langkah 1/3*
Silakan masukkan email Cloudflare Anda\\:
        """

        EMAIL_SUCCESS = f"""
{Emojis.SUCCESS} Email berhasil disimpan\\!

{Emojis.KEY} *Langkah 2/3*
Silakan masukkan Global API Key Cloudflare Anda\\:

_API Key dapat ditemukan di\\:_
My Profile → API Tokens → Global API Key → View
        """

        API_KEY_SUCCESS = f"""
{Emojis.SUCCESS} API Key berhasil disimpan!

{Emojis.ID} *Langkah 3/3*
Silakan masukkan Account ID Cloudflare Anda:

_Account ID dapat ditemukan di:_
Dashboard → Right sidebar → Account ID
        """

        VERIFYING = f"{Emojis.LOADING} Memverifikasi kredensial dan mengambil daftar zone...\nMohon tunggu sebentar..."

        VERIFICATION_FAILED = f"""
{Emojis.ERROR} Gagal mengambil daftar zone. Kemungkinan penyebab:
• Email, API Key, atau Account ID tidak valid
• Tidak ada zone di akun Cloudflare
• Masalah koneksi internet

Gunakan /menu untuk mencoba lagi.
        """

        ZONES_FOUND = f"{Emojis.SUCCESS} Berhasil terhubung ke Cloudflare!\n\n{Emojis.MENU} *Ditemukan {{count}} zone:*\nSilakan pilih zone yang ingin dikelola:"

        ACCOUNT_SAVED = f"""
{Emojis.SUCCESS} *Akun Cloudflare berhasil ditambahkan!*

{Emojis.EMAIL} *Email:* `{{email}}`
{Emojis.ZONE} *Zone:* `{{zone_name}}`

Sekarang Anda dapat mengelola DNS record.
Gunakan /menu untuk mengakses fitur-fitur yang tersedia.
        """

        SAVE_FAILED = f"{Emojis.ERROR} Gagal menyimpan akun ke database. Silakan coba lagi.\n\nGunakan /menu untuk mencoba lagi."

        CANCELLED = f"{Emojis.ERROR} Penambahan akun Cloudflare dibatalkan.\n\nGunakan /menu untuk kembali ke menu utama."

    class Help:
        CONTENT = f"""
*{Emojis.HELP} Bantuan Cloudflare DNS Manager*

*Fitur yang tersedia:*
• {Emojis.ADD_RECORD} Tambah Record - Menambah record DNS baru
• {Emojis.VIEW_RECORDS} Lihat Record - Melihat semua record DNS
• {Emojis.EDIT_RECORD} Edit Record - Mengubah record DNS yang ada
• {Emojis.DELETE_RECORD} Hapus Record - Menghapus record DNS
• {Emojis.SETTINGS} Others Menu - Menu tambahan dan pengaturan

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
        INVALID_EMAIL = f"{Emojis.WARNING} Format email tidak valid. Silakan masukkan email yang benar:"
        INVALID_API_KEY = f"{Emojis.WARNING} API Key tampaknya tidak valid. Silakan periksa kembali dan masukkan API Key yang benar:"
        INVALID_ACCOUNT_ID = f"{Emojis.WARNING} Account ID tampaknya tidak valid. Silakan periksa kembali dan masukkan Account ID yang benar:"
        INVALID_SELECTION = (
            f"{Emojis.WARNING} Pilihan tidak valid. Gunakan /menu untuk mencoba lagi."
        )
        ZONE_NOT_FOUND = (
            f"{Emojis.WARNING} Zone tidak ditemukan. Gunakan /menu untuk mencoba lagi."
        )


# ========== BUTTON LABELS ==========
class Buttons:
    # Main Menu
    VIEW_RECORDS = f"{Emojis.VIEW_RECORDS} Lihat Record"
    ADD_RECORD = f"{Emojis.ADD_RECORD} Tambah Record"
    EDIT_RECORD = f"{Emojis.EDIT_RECORD} Edit Record"
    DELETE_RECORD = f"{Emojis.DELETE_RECORD} Hapus Record"
    OTHERS_MENU = f"{Emojis.SETTINGS} Others Menu"
    ADD_CLOUDFLARE = "➕ Tambah Akun Cloudflare"

    # Operations
    SINGLE_RECORD = "Single Record"
    FROM_FILE = "From File"

    # Navigation
    BACK_TO_MAIN = f"{Emojis.BACK} Back to Main Menu"
    CANCEL = f"{Emojis.ERROR} Batal"

    # Others Menu
    HELP = f"{Emojis.HELP} Bantuan"
    DELETE_ACCOUNT = f"{Emojis.DELETE_RECORD} Hapus Akun"
    SWITCH_ZONE = f"{Emojis.ZONE} Ganti Zone"


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
