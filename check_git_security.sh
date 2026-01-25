#!/bin/bash
# Quick Git Security Audit
# Run this to check for sensitive data issues

echo "🔍 Git Security Audit"
echo "====================="
echo ""

# Check 1: Is .gitignore working?
echo "✓ Checking .gitignore..."
if [ -f ".gitignore" ]; then
    echo "  ✓ .gitignore exists"
else
    echo "  ✗ .gitignore missing!"
fi

# Check 2: Are sensitive files tracked?
echo ""
echo "✓ Checking for tracked sensitive files..."
SENSITIVE=$(git ls-files 2>/dev/null | grep -E '\.(env|pem|key|sqlite|db|gramps|gpkg)$|secret|password|credential')
if [ -z "$SENSITIVE" ]; then
    echo "  ✓ No obvious sensitive files tracked"
else
    echo "  ✗ Found sensitive files in Git:"
    echo "$SENSITIVE" | sed 's/^/    /'
fi

# Check 3: Are there large files?
echo ""
echo "✓ Checking for large files..."
LARGE=$(git ls-files 2>/dev/null | xargs du -sh 2>/dev/null | awk '$1 ~ /M$/ {print}' | sort -h)
if [ -z "$LARGE" ]; then
    echo "  ✓ No large files found"
else
    echo "  ⚠ Large files found:"
    echo "$LARGE" | sed 's/^/    /'
fi

# Check 4: Does .env exist but is not tracked?
echo ""
echo "✓ Checking .env file..."
if [ -f ".env" ]; then
    if git ls-files --error-unmatch .env 2>/dev/null >/dev/null; then
        echo "  ✗ .env is tracked by Git (DANGEROUS!)"
    else
        echo "  ✓ .env exists but is properly ignored"
    fi
else
    echo "  ℹ .env file not found"
fi

# Check 5: Database files
echo ""
echo "✓ Checking database files..."
if [ -f "db.sqlite3" ]; then
    if git ls-files --error-unmatch db.sqlite3 2>/dev/null >/dev/null; then
        echo "  ✗ db.sqlite3 is tracked by Git (contains personal data!)"
    else
        echo "  ✓ db.sqlite3 exists but is properly ignored"
    fi
else
    echo "  ℹ db.sqlite3 not found"
fi

# Summary
echo ""
echo "========================================"
echo "📊 Summary"
echo "========================================"

ISSUES=0

if [ ! -f ".gitignore" ]; then
    echo "✗ Missing .gitignore"
    ISSUES=$((ISSUES + 1))
fi

if [ -n "$SENSITIVE" ]; then
    echo "✗ Sensitive files are tracked"
    ISSUES=$((ISSUES + 1))
fi

if [ -f ".env" ] && git ls-files --error-unmatch .env 2>/dev/null >/dev/null; then
    echo "✗ .env is tracked"
    ISSUES=$((ISSUES + 1))
fi

if [ -f "db.sqlite3" ] && git ls-files --error-unmatch db.sqlite3 2>/dev/null >/dev/null; then
    echo "✗ Database is tracked"
    ISSUES=$((ISSUES + 1))
fi

echo ""
if [ $ISSUES -eq 0 ]; then
    echo "🎉 All checks passed! Your repository is secure."
else
    echo "⚠️  Found $ISSUES issue(s). Run: ./cleanup_sensitive_data.sh"
    echo ""
    echo "Or read: GIT_SECURITY_QUICKSTART.md"
fi
