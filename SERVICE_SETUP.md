# Cloudflare DNS Manager Bot - Service Setup

Panduan lengkap untuk setup dan menjalankan bot sebagai systemd service.

## 🚀 Quick Start

### 1. Perbaikan Error

Error yang telah diperbaiki:
- **Pattern callback handler**: Menambahkan `$` di akhir pattern untuk exact match
- **Handler registration order**: Memindahkan `add_cloudflare_conversation` ke urutan pertama
- Hal ini memastikan callback `add_cloudflare` ditangani dengan benar

### 2. Install Service

```bash
# Jalankan script instalasi sebagai root
sudo ./install_service.sh install
```

### 3. Konfigurasi

Edit file `.env` dengan bot token Anda:
```bash
nano .env
```

Isi dengan token bot Telegram Anda:
```env
BOT_TOKEN=your_actual_bot_token_here
```

### 4. Start Service

```bash
# Start bot service
sudo systemctl start cloudflare-dns-bot

# Check status
sudo systemctl status cloudflare-dns-bot
```

## 📋 Perintah Service

### Systemd Commands

```bash
# Start service
sudo systemctl start cloudflare-dns-bot

# Stop service
sudo systemctl stop cloudflare-dns-bot

# Restart service
sudo systemctl restart cloudflare-dns-bot

# Check status
sudo systemctl status cloudflare-dns-bot

# View logs
sudo journalctl -u cloudflare-dns-bot -f

# Enable auto-start on boot (sudah dilakukan saat install)
sudo systemctl enable cloudflare-dns-bot

# Disable auto-start
sudo systemctl disable cloudflare-dns-bot
```

### Manual Control Commands

```bash
# Start bot manually
./start_bot.sh start

# Stop bot
./start_bot.sh stop

# Restart bot
./start_bot.sh restart

# Check status
./start_bot.sh status

# View logs (tail -f)
./start_bot.sh logs

# Setup environment only
./start_bot.sh setup
```

## 📁 File Structure

```
/workspace/
├── Main.py                           # Bot utama
├── start_bot.sh                      # Script startup
├── install_service.sh                # Script instalasi
├── cloudflare-dns-bot.service        # Systemd service file
├── .env                              # Environment variables
├── logs/                             # Log files
│   └── bot.log                       # Bot log file
├── database/                         # Database files
│   └── bot.db                        # SQLite database
└── venv/                             # Python virtual environment
```

## 🔧 Configuration

### Environment Variables (.env)

```env
# Required
BOT_TOKEN=your_telegram_bot_token_here

# Optional - Webhook (leave empty for polling)
WEBHOOK_URL=https://yourdomain.com
WEBHOOK_PATH=wangshu
LISTEN_IP=0.0.0.0
PORT=8000

# Database
DATABASE_FILE=database/bot.db

# Logging
LOG_LEVEL=INFO
LOG_FILE=logs/bot.log

# Application
DEBUG=False
MAX_RETRIES=3
REQUEST_TIMEOUT=30
```

### Service Configuration

File: `/etc/systemd/system/cloudflare-dns-bot.service`

Konfigurasi utama:
- **Auto-restart**: Service akan restart otomatis jika crash
- **Boot startup**: Service akan start otomatis saat system boot
- **Resource limits**: Memory limit 512MB, CPU quota 80%
- **Security**: Hardened security settings
- **Logging**: Integrated dengan systemd journal

## 🐛 Troubleshooting

### 1. Service Tidak Start

```bash
# Check service status
sudo systemctl status cloudflare-dns-bot

# Check logs
sudo journalctl -u cloudflare-dns-bot -n 50

# Check script logs
tail -f logs/bot.log
```

### 2. Permission Errors

```bash
# Fix permissions
sudo chown -R root:root /workspace
sudo chmod +x /workspace/start_bot.sh
```

### 3. Environment Issues

```bash
# Test environment setup
./start_bot.sh setup

# Check if .env file exists and has correct content
cat .env
```

### 4. Python/Dependencies Issues

```bash
# Manually install dependencies
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## 📊 Monitoring

### Logs

```bash
# Systemd journal logs
sudo journalctl -u cloudflare-dns-bot -f

# Bot application logs
tail -f logs/bot.log

# Show last 100 lines
sudo journalctl -u cloudflare-dns-bot -n 100
```

### Status Monitoring

```bash
# Service status
sudo systemctl is-active cloudflare-dns-bot

# Check if enabled for auto-start
sudo systemctl is-enabled cloudflare-dns-bot

# Memory and CPU usage
sudo systemctl status cloudflare-dns-bot

# Process details
ps aux | grep python
```

## 🛠 Maintenance

### Update Bot

```bash
# Stop service
sudo systemctl stop cloudflare-dns-bot

# Update code (git pull, etc.)
git pull origin main

# Install new dependencies if any
source venv/bin/activate
pip install -r requirements.txt

# Start service
sudo systemctl start cloudflare-dns-bot
```

### Backup

```bash
# Backup database
cp database/bot.db database/bot.db.backup.$(date +%Y%m%d_%H%M%S)

# Backup configuration
cp .env .env.backup.$(date +%Y%m%d_%H%M%S)
```

### Log Rotation

Service menggunakan systemd journal yang sudah memiliki log rotation otomatis. Untuk log file manual:

```bash
# Manual log rotation (jika menggunakan LOG_FILE)
mv logs/bot.log logs/bot.log.$(date +%Y%m%d_%H%M%S)
sudo systemctl restart cloudflare-dns-bot
```

## 🔒 Security

Service sudah dikonfigurasi dengan security hardening:
- `NoNewPrivileges=true`: Mencegah privilege escalation
- `PrivateTmp=true`: Isolated /tmp directory
- `ProtectSystem=strict`: Read-only system directories
- `ReadWritePaths=/workspace`: Hanya bisa write di workspace

## ❌ Uninstall

```bash
# Uninstall service
sudo ./install_service.sh uninstall

# Remove files (optional)
rm -rf venv/ logs/ database/ .env
```

## 📞 Support

Jika mengalami masalah:

1. Check service status: `sudo systemctl status cloudflare-dns-bot`
2. Check logs: `sudo journalctl -u cloudflare-dns-bot -f`
3. Test manual start: `./start_bot.sh start`
4. Verify configuration: `cat .env`

---

**Note**: Service ini dirancang untuk production use dengan auto-recovery, resource limits, dan security hardening.