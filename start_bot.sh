#!/bin/bash

# Cloudflare DNS Manager Bot Startup Script
# This script ensures the environment is ready and starts the bot

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
BOT_DIR="/workspace"
PYTHON_EXECUTABLE="python3"
MAIN_SCRIPT="Main.py"
VENV_DIR="$BOT_DIR/venv"
LOG_DIR="$BOT_DIR/logs"
PID_FILE="$BOT_DIR/bot.pid"

# Function to print colored output
print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Function to check if bot is already running
check_if_running() {
    if [ -f "$PID_FILE" ]; then
        PID=$(cat "$PID_FILE")
        if ps -p "$PID" > /dev/null 2>&1; then
            print_error "Bot is already running with PID: $PID"
            exit 1
        else
            print_warning "Stale PID file found, removing..."
            rm -f "$PID_FILE"
        fi
    fi
}

# Function to create necessary directories
create_directories() {
    print_status "Creating necessary directories..."
    
    # Create log directory
    if [ ! -d "$LOG_DIR" ]; then
        mkdir -p "$LOG_DIR"
        print_status "Created log directory: $LOG_DIR"
    fi
    
    # Create database directory if it doesn't exist
    if [ ! -d "$BOT_DIR/database" ]; then
        mkdir -p "$BOT_DIR/database"
        print_status "Created database directory"
    fi
}

# Function to setup Python virtual environment
setup_venv() {
    print_status "Setting up Python virtual environment..."
    
    if [ ! -d "$VENV_DIR" ]; then
        print_status "Creating new virtual environment..."
        $PYTHON_EXECUTABLE -m venv "$VENV_DIR"
        print_status "Virtual environment created"
    fi
    
    # Activate virtual environment
    source "$VENV_DIR/bin/activate"
    print_status "Virtual environment activated"
    
    # Upgrade pip
    print_status "Upgrading pip..."
    pip install --upgrade pip > /dev/null 2>&1
    
    # Install requirements
    if [ -f "$BOT_DIR/requirements.txt" ]; then
        print_status "Installing requirements..."
        pip install -r "$BOT_DIR/requirements.txt" > /dev/null 2>&1
        print_status "Requirements installed successfully"
    else
        print_warning "requirements.txt not found, skipping dependency installation"
    fi
}

# Function to check environment variables
check_environment() {
    print_status "Checking environment variables..."
    
    if [ -f "$BOT_DIR/.env" ]; then
        print_status "Found .env file"
        # Source the .env file to check variables
        export $(grep -v '^#' "$BOT_DIR/.env" | xargs)
    else
        print_warning ".env file not found"
    fi
    
    if [ -z "$BOT_TOKEN" ]; then
        print_error "BOT_TOKEN environment variable is not set!"
        print_error "Please create a .env file with BOT_TOKEN=your_bot_token"
        exit 1
    fi
    
    print_status "Environment variables check passed"
}

# Function to start the bot
start_bot() {
    print_status "Starting Cloudflare DNS Manager Bot..."
    
    cd "$BOT_DIR"
    
    # Activate virtual environment if it exists
    if [ -d "$VENV_DIR" ]; then
        source "$VENV_DIR/bin/activate"
    fi
    
    # Start the bot in background and save PID
    nohup $PYTHON_EXECUTABLE "$MAIN_SCRIPT" > "$LOG_DIR/bot.log" 2>&1 &
    BOT_PID=$!
    
    # Save PID to file
    echo $BOT_PID > "$PID_FILE"
    
    # Give the bot a moment to start
    sleep 2
    
    # Check if bot is still running
    if ps -p $BOT_PID > /dev/null 2>&1; then
        print_status "Bot started successfully with PID: $BOT_PID"
        print_status "Log file: $LOG_DIR/bot.log"
        print_status "PID file: $PID_FILE"
    else
        print_error "Bot failed to start. Check the log file for details."
        rm -f "$PID_FILE"
        exit 1
    fi
}

# Function to stop the bot
stop_bot() {
    print_status "Stopping bot..."
    
    if [ -f "$PID_FILE" ]; then
        PID=$(cat "$PID_FILE")
        if ps -p "$PID" > /dev/null 2>&1; then
            kill "$PID"
            sleep 2
            
            # Force kill if still running
            if ps -p "$PID" > /dev/null 2>&1; then
                print_warning "Bot didn't stop gracefully, force killing..."
                kill -9 "$PID"
            fi
            
            rm -f "$PID_FILE"
            print_status "Bot stopped successfully"
        else
            print_warning "Bot is not running (stale PID file)"
            rm -f "$PID_FILE"
        fi
    else
        print_warning "Bot is not running (no PID file found)"
    fi
}

# Function to show bot status
show_status() {
    if [ -f "$PID_FILE" ]; then
        PID=$(cat "$PID_FILE")
        if ps -p "$PID" > /dev/null 2>&1; then
            print_status "Bot is running with PID: $PID"
            echo "Log file: $LOG_DIR/bot.log"
            echo "Memory usage: $(ps -p $PID -o rss= | awk '{print int($1/1024)" MB"}')"
            echo "Start time: $(ps -p $PID -o lstart= | sed 's/^ *//')"
        else
            print_warning "Bot is not running (stale PID file)"
            rm -f "$PID_FILE"
        fi
    else
        print_warning "Bot is not running"
    fi
}

# Function to restart the bot
restart_bot() {
    print_status "Restarting bot..."
    stop_bot
    sleep 1
    start_bot
}

# Function to show logs
show_logs() {
    if [ -f "$LOG_DIR/bot.log" ]; then
        tail -f "$LOG_DIR/bot.log"
    else
        print_error "Log file not found: $LOG_DIR/bot.log"
    fi
}

# Main script logic
case "${1:-start}" in
    start)
        check_if_running
        create_directories
        setup_venv
        check_environment
        start_bot
        ;;
    stop)
        stop_bot
        ;;
    restart)
        restart_bot
        ;;
    status)
        show_status
        ;;
    logs)
        show_logs
        ;;
    setup)
        create_directories
        setup_venv
        check_environment
        print_status "Setup completed successfully"
        ;;
    *)
        echo "Usage: $0 {start|stop|restart|status|logs|setup}"
        echo ""
        echo "Commands:"
        echo "  start   - Start the bot"
        echo "  stop    - Stop the bot"
        echo "  restart - Restart the bot"
        echo "  status  - Show bot status"
        echo "  logs    - Show bot logs (tail -f)"
        echo "  setup   - Setup environment without starting"
        exit 1
        ;;
esac