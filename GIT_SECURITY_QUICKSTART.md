# Quick Reference: Protecting Sensitive Data in Git

## 🎯 What Was Done

### 1. Enhanced `.gitignore` ✅
Your `.gitignore` file has been completely rewritten with comprehensive protection for:

**Secrets & Credentials:**
- `.env` files (all variants)
- `secrets.json`, `secrets.py`
- SSL certificates (`.pem`, `.key`, `.crt`)
- SSH keys (`id_rsa`, `id_ed25519`)
- Cloud credentials (`.aws/`, `credentials.json`)
- API keys and tokens
- Password files

**Personal/Family Data:**
- Gramps files (`.gramps`, `.gpkg`, `.ged`)
- Media files (photos in `media/` folder)
- Database files (`.sqlite3`, `.db`, `.sql`)
- Backup files

**Development Files:**
- Python cache (`__pycache__/`)
- Virtual environments
- IDE settings (`.vscode/`, `.idea/`)
- Log files
- Temporary files

## ⚡ Quick Actions (3 Commands)

```bash
# 1. Stop tracking sensitive files (keeps them on disk)
cd /Users/victor/Desktop/malbat.org
./cleanup_sensitive_data.sh

# 2. Or manually:
git rm --cached .env db.sqlite3 GITHUB_COMMANDS.md
git rm -r --cached gramps/ media/ logs/
git add .gitignore
git commit -m "🔒 Stop tracking sensitive data"

# 3. Push changes
git push origin main
```

## 📋 Files You Should Stop Tracking

Currently in your repo but should be removed:

| File/Folder | Why Remove | Command |
|-------------|------------|---------|
| `.env` | Contains secrets (DB password, SECRET_KEY) | `git rm --cached .env` |
| `db.sqlite3` | Personal/family data | `git rm --cached db.sqlite3` |
| `gramps/` | Genealogical data | `git rm -r --cached gramps/` |
| `media/` | Photos and documents | `git rm -r --cached media/` |
| `logs/` | May contain sensitive info | `git rm -r --cached logs/` |

## 🛡️ What's Now Protected

After updating `.gitignore`, these will **never** be committed:

### Environment Files
```
.env, .env.local, .env.production, .env.*, *.env
secrets.py, secrets.json, config.local.py
```

### Credentials
```
*.pem, *.key, *.crt, *.cert
id_rsa, id_rsa.pub, id_ed25519*
.aws/, .credentials, credentials.json
*api_key*, *apikey*, *token*, *secret*
*password*, *passwd*, htpasswd
```

### Personal Data
```
*.gramps, *.gpkg, *.ged, *.gedcom
media/, media/imported/, media/uploads/
gramps/
*.db, *.sqlite, *.sqlite3, *.sql, *.dump
```

### Documentation
```
GITHUB_COMMANDS.md, NOTES.md, TODO.md
*PRIVATE*.md, *SENSITIVE*.md, *CONFIDENTIAL*.md
```

## ✅ Verify Protection Works

```bash
# Test that sensitive files are ignored
touch test.env
git status
# Should NOT show test.env

# Clean up test
rm test.env

# Check what's being tracked
git ls-files | grep -E '\.env|sqlite|gramps|media'
# Should return nothing
```

## 🚨 If You Already Pushed Secrets

**CRITICAL:** If secrets are in Git history, they're still accessible even after removing from tracking!

### Immediate Actions:
1. **Rotate ALL secrets immediately**
   - Change database passwords
   - Regenerate SECRET_KEY
   - Revoke API keys
   - Update .env with new values

2. **Remove from history** (choose one method):

**Option A - Quick (BFG):**
```bash
brew install bfg  # macOS
bfg --delete-files .env
bfg --delete-files db.sqlite3
git reflog expire --expire=now --all
git gc --prune=now --aggressive
git push --force origin main
```

**Option B - Modern (git-filter-repo):**
```bash
brew install git-filter-repo
git filter-repo --invert-paths --path .env
git filter-repo --invert-paths --path db.sqlite3
git push --force origin main
```

**Option C - Manual:**
```bash
git filter-branch --force --index-filter \
  "git rm --cached --ignore-unmatch .env db.sqlite3" \
  --prune-empty --tag-name-filter cat -- --all
git push --force origin main
```

## 📚 Documentation Created

1. **`GIT_SECURITY_GUIDE.md`** (comprehensive guide)
   - Step-by-step cleanup instructions
   - History cleaning methods
   - Best practices
   - Emergency procedures
   - Regular audit scripts

2. **`cleanup_sensitive_data.sh`** (automation script)
   - Interactive cleanup
   - Safe removal from tracking
   - Automatic commit
   - Usage: `./cleanup_sensitive_data.sh`

3. **`.gitignore`** (updated with 280+ patterns)
   - Organized by category
   - Well-commented
   - Production-ready

## 🎓 Best Practices Going Forward

### DO ✅
- Always check `git status` before committing
- Use `.env.example` for templates (without secrets)
- Keep separate .env files for dev/staging/prod
- Review diffs before pushing: `git diff`
- Use pre-commit hooks to catch secrets
- Rotate secrets regularly

### DON'T ❌
- Never commit `.env` files
- Never commit database files with real data
- Never commit personal photos/documents
- Never commit API keys or passwords
- Never force push without backing up first
- Never share secrets via Git, even in private repos

## 🔧 Optional: Install Pre-commit Hooks

```bash
# Install pre-commit
pip install pre-commit

# It will automatically check for:
# - Large files (>500KB)
# - Private keys
# - Merge conflicts
# - JSON/YAML syntax
# - Trailing whitespace
```

## 📱 Quick Commands Reference

```bash
# Stop tracking but keep file locally
git rm --cached FILE

# Stop tracking entire directory
git rm -r --cached DIRECTORY/

# Check what Git is tracking
git ls-files

# See what will be committed
git status

# See file changes
git diff

# Check if .gitignore is working
git check-ignore -v FILE
```

## 🎯 Summary

| Status | Action | Time |
|--------|--------|------|
| ✅ | `.gitignore` updated with 280+ patterns | Done |
| ⚠️ | Run `cleanup_sensitive_data.sh` | 2 minutes |
| ⚠️ | Push changes to remote | 1 minute |
| 📖 | Read `GIT_SECURITY_GUIDE.md` for full details | 10 minutes |
| 🔥 | Clean Git history if secrets were pushed | 15 minutes |
| 🔐 | Rotate any exposed secrets | 30 minutes |

## 🆘 Help

- **Full guide**: Open `GIT_SECURITY_GUIDE.md`
- **Quick cleanup**: Run `./cleanup_sensitive_data.sh`
- **Check protection**: Run `git status` and verify sensitive files don't appear

Your repository is now protected! 🛡️
