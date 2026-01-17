#!/bin/bash
# Git Sensitive Data Cleanup Script
# Run this to stop tracking sensitive files in your repository

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${YELLOW}=== Git Sensitive Data Cleanup ===${NC}"
echo ""

# Check if we're in a git repository
if [ ! -d ".git" ]; then
    echo -e "${RED}Error: Not a git repository${NC}"
    exit 1
fi

echo -e "${YELLOW}Step 1: Checking current status...${NC}"
git status

echo ""
echo -e "${YELLOW}Step 2: Files to stop tracking (but keep locally):${NC}"
cat << 'EOF'
- .env (environment variables)
- db.sqlite3 (database with personal data)
- GITHUB_COMMANDS.md (personal notes)
- gramps/ (genealogical data)
- media/ (photos and documents)
- logs/ (log files)
EOF

echo ""
read -p "Continue with cleanup? (yes/no): " -r
if [[ ! $REPLY =~ ^[Yy]es$ ]]; then
    echo "Cleanup cancelled."
    exit 0
fi

echo ""
echo -e "${YELLOW}Step 3: Removing files from Git tracking...${NC}"

# Stop tracking files but keep them locally
if [ -f ".env" ]; then
    echo "  Removing .env from tracking..."
    git rm --cached .env 2>/dev/null || echo "  .env not tracked"
fi

if [ -f "db.sqlite3" ]; then
    echo "  Removing db.sqlite3 from tracking..."
    git rm --cached db.sqlite3 2>/dev/null || echo "  db.sqlite3 not tracked"
fi

if [ -f "GITHUB_COMMANDS.md" ]; then
    echo "  Removing GITHUB_COMMANDS.md from tracking..."
    git rm --cached GITHUB_COMMANDS.md 2>/dev/null || echo "  GITHUB_COMMANDS.md not tracked"
fi

if [ -d "gramps" ]; then
    echo "  Removing gramps/ from tracking..."
    git rm -r --cached gramps/ 2>/dev/null || echo "  gramps/ not tracked"
fi

if [ -d "media" ]; then
    echo "  Removing media/ from tracking..."
    git rm -r --cached media/ 2>/dev/null || echo "  media/ not tracked"
fi

if [ -d "logs" ]; then
    echo "  Removing logs/ from tracking..."
    git rm -r --cached logs/ 2>/dev/null || echo "  logs/ not tracked"
fi

echo ""
echo -e "${YELLOW}Step 4: Committing changes...${NC}"
git add .gitignore
git commit -m "🔒 Stop tracking sensitive data and update .gitignore" || echo "  Nothing to commit"

echo ""
echo -e "${GREEN}✓ Cleanup complete!${NC}"
echo ""
echo -e "${YELLOW}Next steps:${NC}"
echo "1. Review changes: git status"
echo "2. Push to remote: git push origin main"
echo ""
echo -e "${YELLOW}⚠️  IMPORTANT:${NC}"
echo "These files are still in Git history. To completely remove them:"
echo "  See: GIT_SECURITY_GUIDE.md (Section: Remove Sensitive Data from Git History)"
echo ""
echo -e "${GREEN}Files are now protected and won't be committed in the future!${NC}"
