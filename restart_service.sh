#!/bin/bash

PROJECT_DIR="malbat.org"
VENV_PYTHON="malbat.org/bin/python"
MANAGE_PY="$PROJECT_DIR/manage.py"
SERVICE_NAME="django_malbat.org.service"
ENV_FILE="/home/debian/dotenvs/malbat.org"
DB_HOST="localhost"
DB_PORT="5432"
DB_USER="django_user"

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[0;33m'
NC='\033[0m'

# Fonction pour vérifier si la BDD est disponible
check_db_connection() {
    if pg_isready -h "$DB_HOST" -p "$DB_PORT" >/dev/null 2>&1; then
        return 0
    fi
    return 1
}

echo -e "${GREEN}--- Starting Deployment/Restart Process ---${NC}"

# 0. Load Environment Variables
echo -e "${GREEN}[0/5] Loading environment variables...${NC}"
set -a
source "$ENV_FILE"
set +a

# Navigate to project directory
cd "$PROJECT_DIR" || { echo "Directory not found"; exit 1; }

# 3. Collect Static Files
echo -e "${GREEN}[3/5] Collecting static files...${NC}"
$VENV_PYTHON "$MANAGE_PY" collectstatic --noinput 2>/dev/null || true

# 4. Check Database Connection & Apply Migrations
echo -e "${GREEN}[4/5] Checking database connection...${NC}"
if check_db_connection; then
    echo -e "${GREEN}[+] BDD OK - Applying migrations...${NC}"
    $VENV_PYTHON "$MANAGE_PY" makemigrations 2>/dev/null || true
    $VENV_PYTHON "$MANAGE_PY" migrate 2>/dev/null || true
else
    echo -e "${YELLOW}[!] BDD indisponible sur $DB_HOST:$DB_PORT - Migrations ignorées${NC}"
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
