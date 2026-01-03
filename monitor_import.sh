#!/bin/bash

# Monitor Gramps import progress

echo "📊 Checking import progress..."
echo ""

if tail -f /var/www/dev.malbat.org/import_log.txt 2>/dev/null | head -20; then
    echo ""
    echo "✅ Import in progress or completed"
else
    echo "⏳ Waiting for import to start..."
fi
