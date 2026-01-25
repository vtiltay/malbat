# Media Utilities Quick Reference

## Quick Import

```python
from familytree.utils import *
```

## Most Common Functions

### 1. Copy Media File with Auto-Everything
```python
# Does: find file, copy, handle duplicates, set permissions
relative_path = copy_gramps_media_to_django('/path/to/photo.jpg')
# Returns: 'imported/photo.jpg'
```

### 2. Find File in Multiple Locations
```python
found = find_gramps_media_file('photo.jpg', search_locations=['/backup'])
if found:
    print(f"Found at: {found}")
```

### 3. Fix All Permissions (Run After Import)
```python
ensure_media_directory_permissions('imported')
# Sets: directories=755, files=644
```

### 4. Normalize Any Path to Django Format
```python
relative_path, was_abs = normalize_gramps_media_path('/home/user/photo.jpg')
# Returns: ('imported/photo.jpg', True)
```

### 5. Clean Up Orphaned Files (Dry Run)
```python
count, orphaned = cleanup_orphaned_media(dry_run=True)
print(f"Found {count} orphaned files")
```

## Permission Quick Fixes

### From Python
```python
from familytree.utils import ensure_media_directory_permissions
ensure_media_directory_permissions('imported')
```

### From Command Line
```bash
# Fix permissions
sudo chmod 755 /path/to/media/imported
sudo find /path/to/media/imported -type f -exec chmod 644 {} \;

# Fix ownership
sudo chown -R www-data:www-data /path/to/media/imported/
```

## Complete Import Example

```python
from familytree.utils import (
    find_gramps_media_file,
    copy_gramps_media_to_django,
    normalize_gramps_media_path
)

def import_media(gramps_path):
    # Try to find and copy
    found = find_gramps_media_file(gramps_path)
    
    if found:
        return copy_gramps_media_to_django(str(found))
    else:
        # File not found, normalize path anyway
        relative_path, _ = normalize_gramps_media_path(gramps_path)
        return relative_path
```

## Permission Codes

| Code | Description | Use For |
|------|-------------|---------|
| 0o755 | rwxr-xr-x | Directories |
| 0o644 | rw-r--r-- | Media files |
| 0o750 | rwxr-x--- | Restricted dirs |
| 0o640 | rw-r----- | Restricted files |

## Common Patterns

### Pattern 1: Safe File Copy
```python
if found := find_gramps_media_file(path):
    return copy_gramps_media_to_django(str(found))
return None
```

### Pattern 2: Path Normalization Only
```python
relative, _ = normalize_gramps_media_path(absolute_path)
```

### Pattern 3: Validation Before Use
```python
from pathlib import Path
from django.conf import settings

filepath = Path(settings.MEDIA_ROOT) / relative_path
is_valid, error = validate_media_file(filepath)
```

## Troubleshooting One-Liners

```python
# Fix permissions
ensure_media_directory_permissions('imported')

# Find orphaned files
count, orphaned = cleanup_orphaned_media(dry_run=True)

# Get URL for template
url = get_media_url('imported/photo.jpg')

# Sanitize dangerous filename
safe = sanitize_filename('photo (copy).jpg')  # → 'photo_copy.jpg'
```

## Web Server Configuration

### Nginx
```nginx
location /media/ {
    alias /path/to/media/;
    expires 30d;
    access_log off;
}
```

### Apache
```apache
Alias /media/ /path/to/media/
<Directory /path/to/media>
    Require all granted
</Directory>
```

## Django Settings

```python
# In settings.py
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'
MAX_MEDIA_FILE_SIZE = 100 * 1024 * 1024  # 100MB
```

## Error Handling

```python
try:
    relative_path = copy_gramps_media_to_django(source)
    if relative_path is None:
        logger.warning(f"Failed to copy: {source}")
except Exception as e:
    logger.error(f"Error copying media: {e}")
```

## Remember

✅ Always use utilities instead of manual `shutil.copy()`  
✅ Run `ensure_media_directory_permissions()` after imports  
✅ Use `dry_run=True` before cleanup operations  
✅ Validate paths with `validate_media_file()`  
✅ Never use 777 permissions  
✅ Set ownership to web server user (www-data)
