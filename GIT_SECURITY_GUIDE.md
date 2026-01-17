# Git Sensitive Data Management Guide

## ⚠️ CRITICAL: Current Sensitive Files

Your repository currently contains these sensitive files that should **NOT** be in Git:

```
✗ .env                    # Environment variables with secrets
✗ db.sqlite3              # Database with personal data
✗ GITHUB_COMMANDS.md      # Personal documentation
✗ gramps/                 # Genealogical data (personal/family info)
✗ media/                  # Photos and personal documents
```

## 🛡️ Updated .gitignore

Your `.gitignore` has been updated with comprehensive protection for:
- Environment variables and secrets (.env, secrets.json, etc.)
- Database files (.sqlite3, .db, .sql)
- SSL/TLS certificates and keys (.pem, .key, .crt)
- SSH keys (id_rsa, id_ed25519, etc.)
- Cloud credentials (.aws/, credentials.json)
- Gramps files (.gramps, .gpkg, .ged)
- Media files (photos, documents)
- Personal documentation
- And much more...

## 🚨 IMMEDIATE ACTIONS REQUIRED

### Step 1: Stop Tracking Sensitive Files (But Keep Them Locally)

```bash
cd /Users/victor/Desktop/malbat.org

# Remove from Git tracking but keep files on disk
git rm --cached .env
git rm --cached db.sqlite3
git rm --cached GITHUB_COMMANDS.md
git rm -r --cached gramps/
git rm -r --cached media/
git rm -r --cached logs/

# Commit the removal
git add .gitignore
git commit -m "🔒 Stop tracking sensitive data and update .gitignore"
```

### Step 2: Verify Files Are Ignored

```bash
# Check what will be committed next time
git status

# These should NOT appear:
# - .env
# - db.sqlite3
# - gramps/
# - media/
```

### Step 3: Push Changes

```bash
git push origin main
```

## 🔥 ADVANCED: Remove Sensitive Data from Git History

**⚠️ WARNING:** This rewrites Git history. Coordinate with team if working with others!

### Option A: Using BFG Repo-Cleaner (Recommended)

```bash
# Install BFG
# macOS:
brew install bfg

# Linux:
wget https://repo1.maven.org/maven2/com/madgag/bfg/1.14.0/bfg-1.14.0.jar
alias bfg='java -jar bfg-1.14.0.jar'

# Create a backup
cp -r /Users/victor/Desktop/malbat.org /Users/victor/Desktop/malbat.org.backup

# Remove sensitive files from history
cd /Users/victor/Desktop/malbat.org
bfg --delete-files .env
bfg --delete-files db.sqlite3
bfg --delete-files GITHUB_COMMANDS.md
bfg --delete-folders gramps
bfg --delete-folders media
bfg --delete-folders logs

# Clean up
git reflog expire --expire=now --all
git gc --prune=now --aggressive

# Force push (⚠️ destructive!)
git push --force origin main
```

### Option B: Using git-filter-repo (Modern Approach)

```bash
# Install git-filter-repo
# macOS:
brew install git-filter-repo

# Linux:
pip3 install git-filter-repo

# Create backup
cp -r /Users/victor/Desktop/malbat.org /Users/victor/Desktop/malbat.org.backup

# Remove sensitive files
cd /Users/victor/Desktop/malbat.org
git filter-repo --invert-paths --path .env
git filter-repo --invert-paths --path db.sqlite3
git filter-repo --invert-paths --path GITHUB_COMMANDS.md
git filter-repo --invert-paths --path gramps/
git filter-repo --invert-paths --path media/
git filter-repo --invert-paths --path logs/

# Add remote back (filter-repo removes it)
git remote add origin YOUR_REPO_URL

# Force push
git push --force origin main
```

### Option C: Manual Cleanup with git filter-branch (Legacy)

```bash
# Backup first
cp -r /Users/victor/Desktop/malbat.org /Users/victor/Desktop/malbat.org.backup

cd /Users/victor/Desktop/malbat.org

# Remove .env from history
git filter-branch --force --index-filter \
  "git rm --cached --ignore-unmatch .env" \
  --prune-empty --tag-name-filter cat -- --all

# Remove db.sqlite3
git filter-branch --force --index-filter \
  "git rm --cached --ignore-unmatch db.sqlite3" \
  --prune-empty --tag-name-filter cat -- --all

# Remove directories
git filter-branch --force --index-filter \
  "git rm -r --cached --ignore-unmatch gramps media logs" \
  --prune-empty --tag-name-filter cat -- --all

# Clean up
git reflog expire --expire=now --all
git gc --prune=now --aggressive

# Force push
git push --force origin main
```

## 📋 Checklist: Verify Cleanup

```bash
# Check current files being tracked
git ls-files | grep -E '\.(env|sqlite|db)$|gramps|media|logs'
# Should return nothing!

# Check .gitignore is working
touch test.env
git status
# Should show: "nothing to commit" (file is ignored)
rm test.env

# Verify file sizes in history
git rev-list --objects --all | \
  git cat-file --batch-check='%(objecttype) %(objectname) %(objectsize) %(rest)' | \
  awk '/^blob/ {print substr($0,6)}' | \
  sort -n -k2 | \
  tail -20
# Should not see large media files
```

## 🔐 Environment Variables Management

### Create .env Template

```bash
cat > .env.example << 'EOF'
# Django Settings
SECRET_KEY=your-secret-key-here
DEBUG=False
ALLOWED_HOSTS=localhost,127.0.0.1,your-domain.com

# Database
DB_NAME=malbat_db
DB_USER=malbat_user
DB_PASSWORD=your-secure-password-here
DB_HOST=localhost
DB_PORT=5432

# Email Configuration
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@example.com
EMAIL_HOST_PASSWORD=your-email-password-here
DEFAULT_FROM_EMAIL=your-email@example.com
EOF

# Add to Git (this is safe - no actual secrets)
git add .env.example
git commit -m "Add environment variables template"
```

### On Server Setup

```bash
# Copy template
cp .env.example .env

# Edit with real values
nano .env

# Secure it
chmod 600 .env
```

## 🚀 Safe Git Workflow Going Forward

### Before Every Commit

```bash
# 1. Check what you're about to commit
git status

# 2. Review changes
git diff

# 3. Check for secrets (use git-secrets or gitleaks)
# Install git-secrets:
brew install git-secrets  # macOS
# or
apt-get install git-secrets  # Linux

# Initialize git-secrets
git secrets --install
git secrets --register-aws

# Scan for secrets
git secrets --scan
```

### Install Pre-commit Hooks

```bash
# Install pre-commit
pip install pre-commit

# Create .pre-commit-config.yaml
cat > .pre-commit-config.yaml << 'EOF'
repos:
  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v4.5.0
    hooks:
      - id: check-added-large-files
        args: ['--maxkb=500']
      - id: check-merge-conflict
      - id: detect-private-key
      - id: check-json
      - id: check-yaml
      - id: end-of-file-fixer
      - id: trailing-whitespace

  - repo: https://github.com/Yelp/detect-secrets
    rev: v1.4.0
    hooks:
      - id: detect-secrets
        args: ['--baseline', '.secrets.baseline']
EOF

# Install the hooks
pre-commit install

# Run on all files
pre-commit run --all-files
```

## 🔍 Regular Audits

### Monthly Security Check

```bash
# 1. Check for accidentally committed secrets
git log -p | grep -E 'password|secret|api_key|token' -i

# 2. Check file sizes in repo
git rev-list --objects --all | \
  git cat-file --batch-check='%(objecttype) %(objectname) %(objectsize) %(rest)' | \
  awk '/^blob/ {print substr($0,6)}' | \
  sort -n -k2 | \
  tail -20

# 3. Use gitleaks for comprehensive scan
docker run -v $(pwd):/path zricethezav/gitleaks:latest detect \
  --source="/path" --verbose
```

## 📝 .env File Best Practices

### DO ✅
- Keep .env in .gitignore
- Provide .env.example template
- Use different .env files for dev/staging/prod
- Rotate secrets regularly
- Use strong, random passwords
- Document required variables

### DON'T ❌
- Commit .env to Git
- Share .env via email/chat
- Use simple/guessable passwords
- Reuse passwords across environments
- Store production secrets in dev .env
- Hardcode secrets in code

## 🆘 Emergency: Secret Already Pushed

If you've accidentally pushed a secret:

```bash
# 1. IMMEDIATELY rotate the secret
# - Change password in database
# - Regenerate API key
# - Revoke access token
# - Update .env with new value

# 2. Remove from history (see above)

# 3. Force push
git push --force origin main

# 4. Notify team members to re-clone

# 5. Consider the secret compromised
# - Monitor for unauthorized access
# - Check logs for suspicious activity
```

## 📊 Repository Status Check

Run this to check your current situation:

```bash
#!/bin/bash
echo "=== Git Sensitive Data Audit ==="
echo ""

echo "Files currently tracked by Git:"
git ls-files | wc -l

echo ""
echo "Checking for sensitive patterns in tracked files:"
git ls-files | grep -E '\.(env|pem|key|sqlite|db|gramps|gpkg)$|secret|password|credential' || echo "✓ None found"

echo ""
echo "Repository size:"
du -sh .git

echo ""
echo "Largest files in repository:"
git rev-list --objects --all | \
  git cat-file --batch-check='%(objecttype) %(objectname) %(objectsize) %(rest)' | \
  awk '/^blob/ {print substr($0,6)}' | \
  sort -n -k2 | \
  tail -10

echo ""
echo "Files that should be ignored but aren't:"
git ls-files -i --exclude-standard || echo "✓ All good"
```

## 🎯 Summary

1. **Immediate**: Stop tracking sensitive files (Step 1-3 above)
2. **Important**: Clean Git history if secrets were committed
3. **Critical**: Rotate any secrets that were exposed
4. **Ongoing**: Use pre-commit hooks and regular audits
5. **Always**: Check `git status` before committing

Your `.gitignore` is now comprehensive and will prevent future accidents!
