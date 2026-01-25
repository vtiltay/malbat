#!/bin/bash
# This script creates the PostgreSQL database and user needed for the malbat.org project.

DB_NAME="malbat_db"
DB_USER="malbat_user"
DB_PASSWORD="your_password"  # Change this to a secure password

# It is recommended to run this script as a user with sudo privileges.
# The script will use sudo to switch to the 'postgres' user to create the database and user.

echo "Creating PostgreSQL user: $DB_USER"
sudo -u postgres psql -c "CREATE USER $DB_USER WITH PASSWORD '$DB_PASSWORD';"

echo "Creating PostgreSQL database: $DB_NAME"
sudo -u postgres psql -c "CREATE DATABASE $DB_NAME OWNER $DB_USER;"

echo "Database setup is complete."
echo "Please make sure to create a .env file in the root of your project with the following content:"
echo "DB_NAME=$DB_NAME"
echo "DB_USER=$DB_USER"
echo "DB_PASSWORD=$DB_PASSWORD"
