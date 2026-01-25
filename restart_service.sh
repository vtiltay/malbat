#!/bin/bash

# Get project name from script location
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_NAME="$(basename "$SCRIPT_DIR")"
PROJECT_DIR="$SCRIPT_DIR"

# Use venv from standard location
VENV_DIR="/home/debian/venvs/$PROJECT_NAME"
VENV_PYTHON="$VENV_DIR/bin/python"
MANAGE_PY="$PROJECT_DIR/manage.py"

# Service name (passed as argument or constructed)
SERVICE_NAME="${1:-django_${PROJECT_NAME}.service}"

# Environment file (loaded from .env file, not hardcoded)
ENV_FILE="/home/debian/dotenvs/$PROJECT_NAME"

# Database settings from environment (not hardcoded)
DB_HOST="${DB_HOST:-localhost}"
DB_PORT="${DB_PORT:-5432}"

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[0;33m'
NC='\033[0m'

# Check database connection
check_db_connection() {
    if pg_isready -h "$DB_HOST" -p "$DB_PORT" >/dev/null 2>&1; then
        return 0
    fi
    return 1
}

echo -e "${GREEN}--- Starting Deployment/Restart Process ---${NC}"

# 0. Load Environment Variables
echo -e "${GREEN}[0/5] Loading environment variables...${NC}"
if [ -f "$ENV_FILE" ]; then
    set -a
    source "$ENV_FILE"
    set +a
else
    echo -e "${YELLOW}[!] Warning: ENV file not found at $ENV_FILE${NC}"
fi

# Navigate to project directory
cd "$PROJECT_DIR" || { echo "Directory not found"; exit 1; }

# 3. Collect Static Files
echo -e "${GREEN}[3/5] Collecting static files...${NC}"
$VENV_PYTHON "$MANAGE_PY" collectstatic --noinput 2>/dev/null || true

# 4. Check Database Connection & Apply Migrations
echo -e "${GREEN}[4/5] Checking database connection...${NC}"
if check_db_connection; then
    echo -e "${GREEN}[+] Database OK - Applying migrations...${NC}"
    $VENV_PYTHON "$MANAGE_PY" makemigrations 2>/dev/null || true
    $VENV_PYTHON "$MANAGE_PY" migrate 2>/dev/null || true
else
    echo -e "${YELLOW}[!] Database unavailable at $DB_HOST:$DB_PORT - Migrations skipped${NC}"
fi

# 5. Restart Gunicorn Service
echo -e "${GREEN}[5/5] Restarting Gunicorn...${NC}"
sudo systemctl restart "$SERVICE_NAME"

# Check Status
if systemctl is-active --quiet "$SERVICE_NAME"; then
    echo -e "${GREEN}>>> SUCCESS: Service is running!${NC}"
    sleep 1
    if check_db_connection; then
        echo -e "${GREEN}>>> DATABASE: OK${NC}"
    else
        echo -e "${YELLOW}>>> WARNING: Database not responding but service is running${NC}"
    fi
else
    echo -e "${RED}>>> ERROR: Service failed to restart${NC}"
    exit 1
fi
