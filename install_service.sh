#!/bin/bash

# Installation script for Cloudflare DNS Manager Bot
# This script will install the systemd service and setup the bot

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
BOT_DIR="/workspace"
SERVICE_NAME="cloudflare-dns-bot"
SERVICE_FILE="$SERVICE_NAME.service"
SYSTEMD_DIR="/etc/systemd/system"

# Function to print colored output
print_header() {
    echo -e "${BLUE}================================${NC}"
    echo -e "${BLUE}  Cloudflare DNS Manager Bot${NC}"
    echo -e "${BLUE}     Installation Script${NC}"
    echo -e "${BLUE}================================${NC}"
}

print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Function to check if running as root
check_root() {
    if [[ $EUID -ne 0 ]]; then
        print_error "This script must be run as root (use sudo)"
        exit 1
    fi
}

# Function to check prerequisites
check_prerequisites() {
    print_status "Checking prerequisites..."
    
    # Check if Python 3 is installed
    if ! command -v python3 &> /dev/null; then
        print_error "Python 3 is not installed. Please install Python 3 first."
        exit 1
    fi
    
    # Check if pip is installed
    if ! command -v pip3 &> /dev/null; then
        print_warning "pip3 is not installed. Installing..."
        apt-get update > /dev/null 2>&1
        apt-get install -y python3-pip > /dev/null 2>&1
    fi
    
    # Check if venv module is available
    if ! python3 -m venv --help &> /dev/null; then
        print_warning "python3-venv is not installed. Installing..."
        apt-get install -y python3-venv > /dev/null 2>&1
    fi
    
    print_status "Prerequisites check completed"
}

# Function to setup directory permissions
setup_permissions() {
    print_status "Setting up directory permissions..."
    
    # Make start script executable
    chmod +x "$BOT_DIR/start_bot.sh"
    
    # Create necessary directories
    mkdir -p "$BOT_DIR/logs"
    mkdir -p "$BOT_DIR/database"
    
    # Set proper ownership (adjust as needed)
    # chown -R your_user:your_group "$BOT_DIR"
    
    print_status "Permissions set successfully"
}

# Function to install systemd service
install_service() {
    print_status "Installing systemd service..."
    
    # Copy service file to systemd directory
    if [ -f "$BOT_DIR/$SERVICE_FILE" ]; then
        cp "$BOT_DIR/$SERVICE_FILE" "$SYSTEMD_DIR/"
        print_status "Service file copied to $SYSTEMD_DIR"
    else
        print_error "Service file not found: $BOT_DIR/$SERVICE_FILE"
        exit 1
    fi
    
    # Reload systemd daemon
    systemctl daemon-reload
    print_status "Systemd daemon reloaded"
    
    # Enable service (start on boot)
    systemctl enable "$SERVICE_NAME"
    print_status "Service enabled for auto-start on boot"
}

# Function to create sample .env file
create_sample_env() {
    if [ ! -f "$BOT_DIR/.env" ]; then
        print_status "Creating sample .env file..."
        
        cat > "$BOT_DIR/.env" << 'EOF'
# Telegram Bot Configuration
BOT_TOKEN=your_telegram_bot_token_here

# Webhook Configuration (optional, leave empty for polling mode)
# WEBHOOK_URL=https://yourdomain.com
# WEBHOOK_PATH=wangshu
# LISTEN_IP=0.0.0.0
# PORT=8000

# Database Configuration
DATABASE_FILE=database/bot.db

# Logging Configuration
LOG_LEVEL=INFO
# LOG_FILE=logs/bot.log

# Application Settings
DEBUG=False
MAX_RETRIES=3
REQUEST_TIMEOUT=30
EOF
        
        print_warning "Sample .env file created. Please edit it with your bot token:"
        print_warning "  nano $BOT_DIR/.env"
    else
        print_status ".env file already exists"
    fi
}

# Function to test the installation
test_installation() {
    print_status "Testing installation..."
    
    # Test the start script
    if "$BOT_DIR/start_bot.sh" setup; then
        print_status "Setup test passed"
    else
        print_error "Setup test failed"
        return 1
    fi
    
    # Check service status
    if systemctl is-enabled "$SERVICE_NAME" &> /dev/null; then
        print_status "Service is properly enabled"
    else
        print_error "Service is not enabled"
        return 1
    fi
    
    print_status "Installation test completed successfully"
}

# Function to show post-installation instructions
show_instructions() {
    echo ""
    echo -e "${BLUE}================================${NC}"
    echo -e "${BLUE}    Installation Completed!${NC}"
    echo -e "${BLUE}================================${NC}"
    echo ""
    echo -e "${GREEN}Next steps:${NC}"
    echo "1. Edit the .env file with your bot token:"
    echo "   nano $BOT_DIR/.env"
    echo ""
    echo "2. Start the bot service:"
    echo "   systemctl start $SERVICE_NAME"
    echo ""
    echo "3. Check service status:"
    echo "   systemctl status $SERVICE_NAME"
    echo ""
    echo -e "${GREEN}Useful commands:${NC}"
    echo "• Start service:    systemctl start $SERVICE_NAME"
    echo "• Stop service:     systemctl stop $SERVICE_NAME"
    echo "• Restart service:  systemctl restart $SERVICE_NAME"
    echo "• View logs:        journalctl -u $SERVICE_NAME -f"
    echo "• Manual control:   $BOT_DIR/start_bot.sh {start|stop|status|logs}"
    echo ""
    echo -e "${GREEN}Service will automatically start on system boot.${NC}"
}

# Function to uninstall service
uninstall_service() {
    print_status "Uninstalling service..."
    
    # Stop service if running
    if systemctl is-active --quiet "$SERVICE_NAME"; then
        systemctl stop "$SERVICE_NAME"
        print_status "Service stopped"
    fi
    
    # Disable service
    if systemctl is-enabled --quiet "$SERVICE_NAME"; then
        systemctl disable "$SERVICE_NAME"
        print_status "Service disabled"
    fi
    
    # Remove service file
    if [ -f "$SYSTEMD_DIR/$SERVICE_FILE" ]; then
        rm "$SYSTEMD_DIR/$SERVICE_FILE"
        print_status "Service file removed"
    fi
    
    # Reload daemon
    systemctl daemon-reload
    print_status "Systemd daemon reloaded"
    
    print_status "Service uninstalled successfully"
}

# Main installation function
main_install() {
    print_header
    check_root
    check_prerequisites
    setup_permissions
    install_service
    create_sample_env
    test_installation
    show_instructions
}

# Main script logic
case "${1:-install}" in
    install)
        main_install
        ;;
    uninstall)
        print_header
        check_root
        uninstall_service
        echo "Uninstallation completed."
        ;;
    test)
        check_prerequisites
        test_installation
        ;;
    *)
        echo "Usage: $0 {install|uninstall|test}"
        echo ""
        echo "Commands:"
        echo "  install   - Install the systemd service (default)"
        echo "  uninstall - Remove the systemd service"
        echo "  test      - Test the installation"
        exit 1
        ;;
esac