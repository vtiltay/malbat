#!/bin/bash

#############################################################################
# Malbat.org Installation Script for Debian-based Distributions
# Installs and configures the Family Tree Django application
#############################################################################

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
REPO_URL="git@github.com:vtiltay/malbat.git"
INSTALL_DIR="${1:-.}"
PROJECT_NAME="malbat.org"
VENV_DIR="$INSTALL_DIR/venv"
PYTHON_VERSION="3.8"

#############################################################################
# Helper Functions
#############################################################################

log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[✓]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
    exit 1
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

#############################################################################
# System Requirements Check
#############################################################################

check_requirements() {
    log_info "Checking system requirements..."
    
    # Check if running as root (not required but warn)
    if [ "$EUID" -eq 0 ]; then
        log_warning "Running as root. Consider running as a regular user."
    fi
    
    # Check for required commands
    if ! command -v git &> /dev/null; then
        log_error "git is not installed. Please install it first: sudo apt-get install git"
    fi
    
    if ! command -v python3 &> /dev/null; then
        log_error "python3 is not installed. Please install it first: sudo apt-get install python3 python3-pip python3-venv"
    fi
    
    log_success "System requirements OK"
}

#############################################################################
# Install System Dependencies
#############################################################################

install_system_deps() {
    log_info "Installing system dependencies..."
    
    sudo apt-get update
    sudo apt-get install -y \
        python3 \
        python3-pip \
        python3-venv \
        python3-dev \
        build-essential \
        libssl-dev \
        libffi-dev \
        postgresql-client \
        git \
        curl \
        wget
    
    log_success "System dependencies installed"
}

#############################################################################
# Clone Repository
#############################################################################

clone_repository() {
    if [ -d "$INSTALL_DIR/.git" ]; then
        log_info "Repository already exists. Updating..."
        cd "$INSTALL_DIR"
        git pull origin main
        cd - > /dev/null
    else
        log_info "Cloning repository from $REPO_URL..."
        git clone "$REPO_URL" "$INSTALL_DIR"
        cd "$INSTALL_DIR"
        log_success "Repository cloned successfully"
    fi
}

#############################################################################
# Setup Virtual Environment
#############################################################################

setup_venv() {
    log_info "Setting up Python virtual environment..."
    
    if [ ! -d "$VENV_DIR" ]; then
        python3 -m venv "$VENV_DIR"
        log_success "Virtual environment created"
    else
        log_warning "Virtual environment already exists"
    fi
    
    # Activate virtual environment
    source "$VENV_DIR/bin/activate"
    
    # Upgrade pip
    pip install --upgrade pip setuptools wheel
    log_success "Virtual environment ready"
}

#############################################################################
# Install Python Dependencies
#############################################################################

install_python_deps() {
    log_info "Installing Python dependencies..."
    
    cd "$INSTALL_DIR"
    source "$VENV_DIR/bin/activate"
    
    if [ -f "requirements.txt" ]; then
        pip install -r requirements.txt
        log_success "Python dependencies installed"
    else
        log_error "requirements.txt not found in $INSTALL_DIR"
    fi
}

#############################################################################
# Setup Django
#############################################################################

setup_django() {
    log_info "Setting up Django application..."
    
    cd "$INSTALL_DIR"
    source "$VENV_DIR/bin/activate"
    
    # Check if .env exists
    if [ ! -f ".env" ]; then
        log_warning ".env file not found. Creating minimal configuration..."
        cat > ".env" << EOF
DEBUG=True
SECRET_KEY=$(python3 -c 'import secrets; print(secrets.token_urlsafe(50))')
ALLOWED_HOSTS=localhost,127.0.0.1
DATABASE_URL=sqlite:///db.sqlite3
EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend
EOF
        log_success ".env file created"
    else
        log_warning ".env file already exists, skipping"
    fi
    
    # Run migrations
    log_info "Running database migrations..."
    python manage.py migrate
    log_success "Migrations completed"
    
    # Collect static files
    log_info "Collecting static files..."
    python manage.py collectstatic --noinput
    log_success "Static files collected"
}

#############################################################################
# Create Superuser (Optional)
#############################################################################

create_superuser() {
    cd "$INSTALL_DIR"
    source "$VENV_DIR/bin/activate"
    
    log_info "Creating default superuser (malbatuser)..."
    
    # Check if superuser already exists
    SUPERUSER_EXISTS=$(python manage.py shell -c "from django.contrib.auth.models import User; print(User.objects.filter(username='malbatuser').exists())" 2>/dev/null || echo "False")
    
    if [ "$SUPERUSER_EXISTS" = "True" ]; then
        log_warning "Superuser 'malbatuser' already exists, skipping creation"
    else
        # Create superuser non-interactively
        python manage.py shell << EOF
from django.contrib.auth.models import User
User.objects.create_superuser('malbatuser', 'admin@malbat.org', 'MalbatPass123')
print("Superuser created successfully")
EOF
        log_success "Superuser 'malbatuser' created with default password"
    fi
}

#############################################################################
# Display Installation Summary
#############################################################################

display_summary() {
    echo ""
    echo -e "${GREEN}========================================${NC}"
    echo -e "${GREEN}   Installation Completed Successfully!${NC}"
    echo -e "${GREEN}========================================${NC}"
    echo ""
    echo -e "Project installed at: ${BLUE}$INSTALL_DIR${NC}"
    echo -e "Virtual environment: ${BLUE}$VENV_DIR${NC}"
    echo ""
    echo -e "${YELLOW}Superuser Credentials:${NC}"
    echo -e "  Username: ${BLUE}malbatuser${NC}"
    echo -e "  Password: ${BLUE}MalbatPass123${NC}"
    echo ""
    echo -e "${YELLOW}⚠️  IMPORTANT: Change the password after first login!${NC}"
    echo ""
    echo -e "${YELLOW}To run the Django development server:${NC}"
    echo ""
    echo "  cd $INSTALL_DIR"
    echo "  source venv/bin/activate"
    echo "  python manage.py runserver"
    echo ""
    echo -e "${YELLOW}Then access the application at:${NC}"
    echo -e "  ${BLUE}http://localhost:8000${NC}"
    echo ""
    echo -e "${YELLOW}Admin interface (login with credentials above):${NC}"
    echo -e "  ${BLUE}http://localhost:8000/admin/${NC}"
    echo ""
    echo -e "${YELLOW}To run on a custom port:${NC}"
    echo "  python manage.py runserver 0.0.0.0:8080"
    echo ""
    echo -e "${YELLOW}For production deployment (Gunicorn):${NC}"
    echo "  pip install gunicorn"
    echo "  gunicorn malbat.wsgi:application --bind 0.0.0.0:8000"
    echo ""
    echo -e "${YELLOW}Or use the provided script:${NC}"
    echo "  ./restart_gunicorn.sh"
    echo ""
}

#############################################################################
# Main Installation Flow
#############################################################################

main() {
    echo -e "${BLUE}"
    echo "╔════════════════════════════════════════╗"
    echo "║  Malbat.org - Family Tree Installation║"
    echo "╚════════════════════════════════════════╝"
    echo -e "${NC}"
    echo ""
    
    check_requirements
    install_system_deps
    clone_repository
    setup_venv
    install_python_deps
    setup_django
    create_superuser
    display_summary
}

# Run main function
main "$@"
