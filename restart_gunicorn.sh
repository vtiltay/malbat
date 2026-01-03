#!/bin/bash

# Restart Gunicorn service for malbat.org
# This script restarts the Gunicorn daemon and reloads Nginx

set -e

echo "🔄 Restarting malbat service..."
sudo systemctl restart malbat

sleep 2

echo "🔄 Checking service status..."
sudo systemctl status malbat --no-pager

echo ""
echo "🔄 Testing Nginx configuration..."
sudo nginx -t

echo ""
echo "🔄 Reloading Nginx..."
sudo systemctl reload nginx

echo ""
echo "✅ Service restart complete!"
echo ""
echo "Service Status:"
sudo systemctl status gunicorn_dev_malbat --no-pager | grep -E "Active|CPU|Memory" || true
