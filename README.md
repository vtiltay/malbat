# 🌳 Malbat.org - Family Tree

A Django web application to manage and visualize a family tree with Gramps import support.

## 📋 Description

Malbat.org is a complete web platform for managing a family genealogy with the following features:

### ✨ Key Features
- **Gramps Import**: Easily import your genealogical data from Gramps
- **Interactive Visualization**: Browse and visualize the family tree
- **Modification Proposals**: Add/modify/delete people and relationships
- **Validation System**: Approve or reject modification proposals
- **User Authentication**: User management and access control
- **Email Notifications**: Alerts for proposals and validations
- **Media Management**: Associate photos with people

## 🚀 Installation

### ⚡ Quick Install (One Command - Standalone Script)

**The easiest way!** Just download and run the script - it handles everything:

```bash
# Option 1: Direct download and run
curl -O https://raw.githubusercontent.com/vtiltay/malbat/main/install-malbat.sh
bash install-malbat.sh

# Option 2: Install in a specific directory
bash install-malbat.sh /home/your-user
```

The script will automatically:
- ✅ Check and install system dependencies (git, Python 3, build tools)
- ✅ Clone the repository
- ✅ Create Python virtual environment
- ✅ Install all Python packages
- ✅ Setup Django and database
- ✅ Create superuser automatically
- ✅ Collect static files

**Default Credentials (created automatically):**
- 👤 **Username**: `malbatuser`
- 🔑 **Password**: `MalbatPass123`

⚠️ **Important**: Change the password after your first login!

**After installation**, start the server:
```bash
cd malbat.org
source venv/bin/activate
python manage.py runserver
```

Then access:
- 🌐 **Website**: http://localhost:8000
- 🔐 **Admin**: http://localhost:8000/admin/

---

### Manual Installation

If you prefer to install manually or have a specific setup:

#### Requirements

- Python 3.8+
- pip
- Virtual environment (highly recommended)
- PostgreSQL (optional, SQLite by default)

#### Local Setup

```bash
# 1. Clone the repository
git clone git@github.com:vtiltay/malbat.git
cd malbat.org

# 2. Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
# or on Windows:
# venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Create .env file
cat > .env << EOF
DEBUG=True
SECRET_KEY=$(python3 -c 'import secrets; print(secrets.token_urlsafe(50))')
ALLOWED_HOSTS=localhost,127.0.0.1
DATABASE_URL=sqlite:///db.sqlite3
EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend
EOF

# 5. Apply migrations
python manage.py migrate

# 6. Create superuser
python manage.py createsuperuser

# 7. Collect static files (production)
python manage.py collectstatic --noinput

# 8. Start development server
python manage.py runserver
```

Access the application: http://localhost:8000

## 📁 Project Structure

```
malbat.org/
├── familytree/                  # Main Django application
│   ├── models.py                # Models (Person, FamilyChild, Event, etc.)
│   ├── views.py                 # Views and business logic
│   ├── forms.py                 # Forms
│   ├── filters.py               # Custom filters
│   ├── signals.py               # Django signals
│   ├── admin.py                 # Admin configuration
│   ├── urls.py                  # Routes
│   ├── management/
│   │   └── commands/            # Custom commands
│   │       └── import_gramps.py # Gramps data import
│   ├── migrations/              # Django migrations
│   └── templates/               # HTML templates
├── malbat/                      # Django configuration
│   ├── settings.py              # Project settings
│   ├── urls.py                  # Global URLs
│   ├── wsgi.py                  # WSGI for production
│   └── asgi.py                  # ASGI for WebSockets
├── media/                       # Uploaded files (ignored by Git)
├── staticfiles/                 # Compiled static files
├── gramps/                      # Gramps data (ignored by Git)
├── manage.py                    # Django CLI
├── restart_gunicorn.sh          # Production deployment script
├── requirements.txt             # Python dependencies
├── .env                         # Environment variables (ignored by Git)
├── .gitignore                   # Files to ignore
└── README.md                    # Documentation
```

## 🔧 Useful Commands

```bash
# Start development server
python manage.py runserver

# Create migrations after model changes
python manage.py makemigrations

# Apply migrations
python manage.py migrate

# Access Django shell
python manage.py shell

# Import Gramps data
python manage.py import_gramps path/to/file.gramps

# Create superuser
python manage.py createsuperuser

# Collect static files
python manage.py collectstatic
```

## 📧 Email Configuration

To enable email notifications, configure environment variables:

```env
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
DEFAULT_FROM_EMAIL=your-email@gmail.com
```

## 🗄️ Data Models

### Person
Represents a person in the family tree.
- `first_name`: First name
- `last_name`: Last name
- `gender`: Gender (M/F)
- `birth_date`: Birth date
- `death_date`: Death date
- `is_deceased`: Deceased status
- `gramps_id`: Gramps ID

### FamilyChild
Links parents and children.
- `parent`: Parent (Person)
- `child`: Child (Person)

### Event
Events related to people.
- `person`: Person involved
- `type`: Event type (birth, death, marriage, etc.)
- `date`: Event date

### ProposedModification
System for proposing modifications.
- `proposer`: User making proposal
- `type`: Proposal type
- `status`: Status (pending, approved, rejected)
- `content`: Proposal details

## 🔐 Security

- ⚠️ **Never commit**: `.env`, `db.sqlite3`, SSH/API keys, Gramps data
- ✅ Use `.gitignore` to exclude sensitive files
- ✅ Configure secrets via environment variables
- ✅ Use HTTPS in production
- ✅ Enable CSRF protection (enabled by default)

## 📝 Deployment

### With Gunicorn (production)

```bash
pip install gunicorn
gunicorn malbat.wsgi:application --bind 0.0.0.0:8000
```

Or use the provided script:
```bash
./restart_gunicorn.sh
```

### With Nginx

Configure Nginx as a reverse proxy pointing to Gunicorn.

## 📚 Additional Documentation

- [Django Documentation](https://docs.djangoproject.com/)
- [Gramps Documentation](https://gramps-project.org/)

## 🤝 Contributing

To contribute:
1. Create a feature branch: `git checkout -b feature/my-feature`
2. Commit changes: `git commit -am 'Add new feature'`
3. Push the branch: `git push origin feature/my-feature`
4. Open a Pull Request

## 📄 License

To be defined

## 👤 Author

Victor Tiltay - vtiltay@gmail.com

---

**Last Updated**: January 3, 2026
