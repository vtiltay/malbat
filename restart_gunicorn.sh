#!/bin/bash

# Restart Gunicorn service for malbat.org
# This script restarts the Gunicorn daemon and reloads Nginx


set -e

echo "⚙️ Running Django migrations and collectstatic..."
source /srv/venvs/malbat.org/bin/activate 2>/dev/null || true
python3 manage.py makemigrations
python3 manage.py migrate
python3 manage.py collectstatic --noinput

echo "🔄 Restarting malbat service..."
sudo systemctl restart django_malbat_org.service

sleep 2

echo "🔄 Checking service status..."
sudo systemctl status django_malbat_org.service --no-pager

echo ""
echo "🔄 Testing Nginx configuration..."
sudo nginx -t

echo ""
echo "🔄 Reloading Nginx..."
sudo systemctl reload nginx
