# Media Utilities Documentation

## Overview

The `familytree/utils.py` module provides comprehensive utilities for handling Gramps media files in Django. These functions ensure safe file operations, proper Linux permissions, and consistent path handling.

## Table of Contents

1. [Path Normalization](#path-normalization)
2. [File Copying](#file-copying)
3. [File Discovery](#file-discovery)
4. [Permissions Management](#permissions-management)
5. [Validation](#validation)
6. [Cleanup](#cleanup)
7. [Common Use Cases](#common-use-cases)

---

## Path Normalization

### `normalize_gramps_media_path(gramps_path, media_subfolder='imported', create_dirs=True)`

Converts Gramps media paths (which may be absolute) to safe relative paths within Django's media folder.

**Parameters:**
- `gramps_path` (str): Original path from Gramps (can be absolute or relative)
- `media_subfolder` (str): Subfolder within MEDIA_ROOT (default: 'imported')
- `create_dirs` (bool): Whether to create directory structure (default: True)

**Returns:**
- Tuple: `(relative_path, was_absolute)`
  - `relative_path`: Path relative to MEDIA_ROOT (e.g., 'imported/photo.jpg')
  - `was_absolute`: Boolean indicating if original path was absolute

**Examples:**
```python
from familytree.utils import normalize_gramps_media_path

# Absolute Linux path
relative_path, was_abs = normalize_gramps_media_path('/home/user/photos/photo.jpg')
# Returns: ('imported/photo.jpg', True)

# Relative path
relative_path, was_abs = normalize_gramps_media_path('photos/photo.jpg')
# Returns: ('imported/photo.jpg', False)

# Windows path (sanitized automatically)
relative_path, was_abs = normalize_gramps_media_path('C:\\Users\\photos\\photo.jpg')
# Returns: ('imported/photo.jpg', True)
```

### `sanitize_filename(filename)`

Removes or replaces dangerous characters in filenames to ensure filesystem and URL compatibility.

**Parameters:**
- `filename` (str): Original filename

**Returns:**
- str: Sanitized filename safe for filesystem storage

**Dangerous Characters Removed:**
- `< > : " / \ | ? *`
- Spaces → underscores
- Parentheses → underscores
- Consecutive underscores collapsed

**Examples:**
```python
from familytree.utils import sanitize_filename

sanitize_filename('photo (copy 1).jpg')
# Returns: 'photo_copy_1.jpg'

sanitize_filename('my file?.jpg')
# Returns: 'my_file.jpg'

sanitize_filename('test<script>.jpg')
# Returns: 'testscript.jpg'
```

---

## File Copying

### `copy_gramps_media_to_django(source_path, destination_subfolder='imported', handle_duplicates=True, set_permissions=True)`

Copies a Gramps media file to Django's media directory with proper Linux permissions.

**Parameters:**
- `source_path` (str): Original path to the media file
- `destination_subfolder` (str): Subfolder within MEDIA_ROOT (default: 'imported')
- `handle_duplicates` (bool): Append counter to duplicate filenames (default: True)
- `set_permissions` (bool): Set permissions to 0o644 (default: True)

**Returns:**
- str or None: Relative path within MEDIA_ROOT if successful, None if failed

**File Permissions:**
- Files: `0o644` (rw-r--r--) - Owner can read/write, others can only read
- Directories: `0o755` (rwxr-xr-x) - Owner full access, others can read/execute

**Examples:**
```python
from familytree.utils import copy_gramps_media_to_django

# Simple copy
relative_path = copy_gramps_media_to_django('/home/user/photos/photo.jpg')
# Returns: 'imported/photo.jpg'

# Copy with custom subfolder
relative_path = copy_gramps_media_to_django(
    '/home/user/photos/photo.jpg',
    destination_subfolder='family_photos'
)
# Returns: 'family_photos/photo.jpg'

# If photo.jpg already exists and handle_duplicates=True
relative_path = copy_gramps_media_to_django('/home/user/photos/photo.jpg')
# Returns: 'imported/photo_1.jpg'
```

### `handle_duplicate_filename(relative_path, subfolder='imported', max_attempts=9999)`

Generates unique filename by appending a counter if file exists.

**Parameters:**
- `relative_path` (str): Original relative path
- `subfolder` (str): Subfolder within MEDIA_ROOT
- `max_attempts` (int): Maximum counter attempts (default: 9999)

**Returns:**
- str: Unique relative path

**Examples:**
```python
from familytree.utils import handle_duplicate_filename

# If 'imported/photo.jpg' exists
unique_path = handle_duplicate_filename('imported/photo.jpg')
# Returns: 'imported/photo_1.jpg'

# If photo_1.jpg also exists
unique_path = handle_duplicate_filename('imported/photo.jpg')
# Returns: 'imported/photo_2.jpg'
```

---

## File Discovery

### `find_gramps_media_file(gramps_path, search_locations=None)`

Searches multiple locations to find a Gramps media file.

**Parameters:**
- `gramps_path` (str): Path from Gramps (absolute or relative)
- `search_locations` (list, optional): Additional directories to search

**Returns:**
- Path or None: Path object if found, None otherwise

**Default Search Locations:**
1. Original path (if absolute)
2. `MEDIA_ROOT/filename`
3. `MEDIA_ROOT/imported/filename`
4. `BASE_DIR/media/filename`
5. Any custom locations provided

**Examples:**
```python
from familytree.utils import find_gramps_media_file

# Search with default locations
found = find_gramps_media_file('photos/wedding.jpg')
if found:
    print(f"Found at: {found}")

# Search with additional locations
found = find_gramps_media_file(
    'family_photo.jpg',
    search_locations=['/mnt/gramps_export', '/backup/photos']
)
```

---

## Permissions Management

### `ensure_media_directory_permissions(subfolder='imported', dir_mode=0o755, file_mode=0o644)`

Ensures media directory and files have proper permissions for web server access.

**Parameters:**
- `subfolder` (str): Subfolder within MEDIA_ROOT
- `dir_mode` (int): Permissions for directories (default: 0o755)
- `file_mode` (int): Permissions for files (default: 0o644)

**Returns:**
- bool: True if successful, False otherwise

**Permission Modes Explained:**
- **0o755** (rwxr-xr-x):
  - Owner: read, write, execute
  - Group: read, execute
  - Others: read, execute
  - Used for directories to allow web server traversal

- **0o644** (rw-r--r--):
  - Owner: read, write
  - Group: read
  - Others: read
  - Used for files to allow web server to serve files

**Why This Matters:**
Web servers (nginx, Apache running as `www-data` or `nginx` user) need:
- **Read** permission on files to serve them
- **Execute** permission on directories to access contents
- Without proper permissions, media files return 403 Forbidden

**Examples:**
```python
from familytree.utils import ensure_media_directory_permissions

# Set proper permissions for web server
success = ensure_media_directory_permissions('imported')

# Custom permissions for restricted access
success = ensure_media_directory_permissions(
    'private_photos',
    dir_mode=0o750,   # Only owner and group
    file_mode=0o640   # Only owner write, group read
)
```

**Command Line Alternative:**
```bash
# From command line (requires sudo if owned by different user)
sudo chmod 755 /path/to/media/imported
sudo chmod 644 /path/to/media/imported/*

# Recursively
sudo chmod 755 /path/to/media/imported/
sudo find /path/to/media/imported/ -type f -exec chmod 644 {} \;
sudo find /path/to/media/imported/ -type d -exec chmod 755 {} \;

# Change ownership to web server user
sudo chown -R www-data:www-data /path/to/media/imported/
```

---

## Validation

### `validate_media_file(filepath)`

Validates that a media file is safe and accessible.

**Parameters:**
- `filepath` (Path): Path to the media file

**Returns:**
- Tuple: `(is_valid, error_message)`
  - `is_valid`: True if file is valid and safe
  - `error_message`: Description of issues (empty if valid)

**Validation Checks:**
1. File exists
2. Is a regular file (not directory/symlink)
3. No path traversal (stays within MEDIA_ROOT)
4. File size within limits (default 100MB)
5. File is readable

**Examples:**
```python
from familytree.utils import validate_media_file
from pathlib import Path

# Validate a safe file
is_valid, error = validate_media_file(Path('/path/to/media/imported/photo.jpg'))
if is_valid:
    print("File is safe to use")
else:
    print(f"Validation failed: {error}")

# This will detect path traversal
dangerous = Path('/path/to/media/../../../etc/passwd')
is_valid, error = validate_media_file(dangerous)
# Returns: (False, 'Path traversal detected')
```

### `get_media_url(relative_path)`

Converts relative media path to full URL for templates/views.

**Parameters:**
- `relative_path` (str): Path relative to MEDIA_ROOT

**Returns:**
- str: Full URL to access the media file

**Examples:**
```python
from familytree.utils import get_media_url

url = get_media_url('imported/photo.jpg')
# Returns: '/media/imported/photo.jpg'

# Use in templates
context = {'photo_url': get_media_url('imported/wedding.jpg')}
```

**Template Usage:**
```django
<!-- In your template -->
<img src="{{ photo_url }}" alt="Wedding photo">

<!-- Or with Person model -->
{% for media in person.media.all %}
    <img src="{{ media.file_path|media_url }}" alt="{{ media.description }}">
{% endfor %}
```

---

## Cleanup

### `cleanup_orphaned_media(subfolder='imported', dry_run=True)`

Identifies and optionally removes media files not referenced in the database.

**Parameters:**
- `subfolder` (str): Subfolder within MEDIA_ROOT
- `dry_run` (bool): If True, only reports without deleting (default: True)

**Returns:**
- Tuple: `(count, list_of_paths)`
  - `count`: Number of orphaned files found
  - `list_of_paths`: List of relative paths to orphaned files

**⚠️ Warning:** Set `dry_run=False` carefully - this permanently deletes files!

**Examples:**
```python
from familytree.utils import cleanup_orphaned_media

# Dry run (safe) - only reports
count, orphaned = cleanup_orphaned_media(subfolder='imported', dry_run=True)
print(f"Found {count} orphaned files:")
for path in orphaned:
    print(f"  - {path}")

# Actually delete (DANGEROUS!)
count, orphaned = cleanup_orphaned_media(subfolder='imported', dry_run=False)
print(f"Deleted {count} orphaned files")
```

**Management Command Version:**
```bash
# Create a management command for this
python manage.py cleanup_media --dry-run
python manage.py cleanup_media --confirm  # Actually delete
```

---

## Common Use Cases

### Use Case 1: Gramps Import with Media

```python
from familytree.utils import (
    find_gramps_media_file,
    copy_gramps_media_to_django,
    normalize_gramps_media_path
)
from familytree.models import Media

def import_gramps_media(gramps_path, gramps_id, description, mime_type):
    """Import a single Gramps media entry"""
    
    # Try to find and copy the file
    found_file = find_gramps_media_file(gramps_path)
    
    if found_file:
        relative_path = copy_gramps_media_to_django(
            str(found_file),
            destination_subfolder='imported',
            handle_duplicates=True,
            set_permissions=True
        )
    else:
        # File not found, normalize path anyway for database
        relative_path, _ = normalize_gramps_media_path(gramps_path)
    
    # Save to database
    media, created = Media.objects.update_or_create(
        gramps_id=gramps_id,
        defaults={
            'file_path': relative_path,
            'mime_type': mime_type,
            'description': description
        }
    )
    
    return media
```

### Use Case 2: Manual Media Upload

```python
from django.core.files.uploadedfile import UploadedFile
from familytree.utils import (
    sanitize_filename,
    copy_gramps_media_to_django,
    ensure_media_directory_permissions
)

def handle_uploaded_media(uploaded_file: UploadedFile, person_id):
    """Handle a media file uploaded through Django form"""
    
    # Sanitize filename
    safe_filename = sanitize_filename(uploaded_file.name)
    
    # Save temporarily
    temp_path = f'/tmp/{safe_filename}'
    with open(temp_path, 'wb') as f:
        for chunk in uploaded_file.chunks():
            f.write(chunk)
    
    try:
        # Copy to media directory with proper permissions
        relative_path = copy_gramps_media_to_django(
            temp_path,
            destination_subfolder='uploads',
            handle_duplicates=True
        )
        
        # Create media record and associate with person
        media = Media.objects.create(
            gramps_id=f'M{person_id}_{safe_filename}',
            file_path=relative_path,
            mime_type=uploaded_file.content_type,
            description=f'Uploaded: {safe_filename}'
        )
        
        return media
    finally:
        # Cleanup temp file
        import os
        if os.path.exists(temp_path):
            os.remove(temp_path)
```

### Use Case 3: Post-Import Cleanup

```python
from familytree.utils import (
    ensure_media_directory_permissions,
    cleanup_orphaned_media,
    validate_media_file
)
from familytree.models import Media
from pathlib import Path
from django.conf import settings

def post_import_maintenance():
    """Perform maintenance after Gramps import"""
    
    # 1. Ensure proper permissions
    print("Setting permissions...")
    ensure_media_directory_permissions('imported')
    
    # 2. Validate all media files in database
    print("Validating database entries...")
    invalid_count = 0
    for media in Media.objects.all():
        filepath = Path(settings.MEDIA_ROOT) / media.file_path
        is_valid, error = validate_media_file(filepath)
        if not is_valid:
            print(f"Invalid: {media.file_path} - {error}")
            invalid_count += 1
    
    print(f"Found {invalid_count} invalid files")
    
    # 3. Find orphaned files
    print("Finding orphaned files...")
    count, orphaned = cleanup_orphaned_media(dry_run=True)
    print(f"Found {count} orphaned files")
    
    if count > 0:
        response = input("Delete orphaned files? (yes/no): ")
        if response.lower() == 'yes':
            count, _ = cleanup_orphaned_media(dry_run=False)
            print(f"Deleted {count} orphaned files")
```

### Use Case 4: Bulk Permission Fix

```bash
# Create a management command
# familytree/management/commands/fix_media_permissions.py

from django.core.management.base import BaseCommand
from familytree.utils import ensure_media_directory_permissions

class Command(BaseCommand):
    help = 'Fix media file permissions for web server access'
    
    def handle(self, *args, **options):
        self.stdout.write('Fixing media permissions...')
        
        success = ensure_media_directory_permissions(
            subfolder='imported',
            dir_mode=0o755,
            file_mode=0o644
        )
        
        if success:
            self.stdout.write(self.style.SUCCESS(
                'Successfully updated media permissions'
            ))
        else:
            self.stdout.write(self.style.ERROR(
                'Failed to update permissions'
            ))
```

**Run it:**
```bash
python manage.py fix_media_permissions
```

---

## Troubleshooting

### Problem: Media files return 403 Forbidden

**Cause:** Incorrect file permissions

**Solution:**
```python
from familytree.utils import ensure_media_directory_permissions
ensure_media_directory_permissions('imported')
```

Or from command line:
```bash
sudo chmod 755 /path/to/media/imported
sudo chmod 644 /path/to/media/imported/*
sudo chown -R www-data:www-data /path/to/media/imported/
```

### Problem: Media files not found after import

**Cause:** Files weren't copied or paths are incorrect

**Solution:**
```python
from familytree.utils import find_gramps_media_file, copy_gramps_media_to_django

# Search for the file
found = find_gramps_media_file('photo.jpg', search_locations=['/backup'])
if found:
    # Copy it manually
    copy_gramps_media_to_django(str(found))
```

### Problem: Duplicate filenames causing conflicts

**Cause:** Multiple files with same name

**Solution:** The utilities automatically handle this with `handle_duplicates=True`:
```python
copy_gramps_media_to_django(path, handle_duplicates=True)
# Automatically becomes: photo.jpg, photo_1.jpg, photo_2.jpg, etc.
```

---

## Linux Permissions Primer

### Understanding File Permissions

```
-rw-r--r--  (0o644)
│││ │ │ │
││└─┴─┴─┴──── Others (read)
│└───────────── Group (read)
└────────────── Owner (read, write)
```

### Common Permission Values

| Code | Binary | Symbolic | Description |
|------|--------|----------|-------------|
| 755 | rwxr-xr-x | Directories | Owner full, others read/execute |
| 644 | rw-r--r-- | Files | Owner write, others read |
| 750 | rwxr-x--- | Restricted dirs | Group access, no others |
| 640 | rw-r----- | Restricted files | Group read, no others |
| 777 | rwxrwxrwx | **AVOID** | Everyone full access (insecure) |

### Best Practices

1. **Never use 777** - Security risk
2. **Directories need execute** - Otherwise can't list contents
3. **Web server user** - Usually `www-data`, `nginx`, or `apache`
4. **Group ownership** - Add your user to web server group for easy management

```bash
# Add your user to www-data group
sudo usermod -a -G www-data your_username

# Set group ownership
sudo chown -R your_username:www-data /path/to/media/

# Set proper permissions
sudo chmod -R 775 /path/to/media/  # Directories
sudo find /path/to/media/ -type f -exec chmod 664 {} \;  # Files
```

---

## Performance Considerations

### Batch Operations

When importing many files:

```python
from familytree.utils import copy_gramps_media_to_django

# Good: Process in batches
media_files = [...list of 1000 files...]

for batch_start in range(0, len(media_files), 100):
    batch = media_files[batch_start:batch_start + 100]
    
    for media_file in batch:
        copy_gramps_media_to_django(media_file)
    
    print(f"Processed {batch_start + 100} files...")
```

### Caching File Lookups

```python
from functools import lru_cache
from familytree.utils import find_gramps_media_file

@lru_cache(maxsize=1000)
def cached_find_media(gramps_path):
    return find_gramps_media_file(gramps_path)
```

---

## Security Considerations

1. **Path Traversal Prevention**: All utilities validate paths stay within MEDIA_ROOT
2. **Filename Sanitization**: Dangerous characters automatically removed
3. **File Size Limits**: Default 100MB, configurable via `settings.MAX_MEDIA_FILE_SIZE`
4. **Permission Control**: Files set to 0o644 (not executable)
5. **Symlink Detection**: `validate_media_file` checks for regular files only

---

## Integration with Django Settings

Add to `settings.py`:

```python
# Media settings
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# Optional: Configure max file size
MAX_MEDIA_FILE_SIZE = 100 * 1024 * 1024  # 100MB

# Optional: Configure default permissions
DEFAULT_FILE_PERMISSIONS = 0o644
DEFAULT_DIR_PERMISSIONS = 0o755
```

---

## Summary

The `familytree.utils` module provides production-ready utilities for handling Gramps media files with:

✅ **Safe path handling** - Prevents path traversal attacks  
✅ **Automatic permission management** - Ensures web server access  
✅ **Duplicate handling** - Prevents file overwrites  
✅ **Multi-location search** - Finds files in various locations  
✅ **Comprehensive validation** - Security and integrity checks  
✅ **Cleanup utilities** - Removes orphaned files  
✅ **Linux-first design** - Proper permission modes for production servers  

Use these utilities in your import scripts, management commands, and views for consistent, safe media file handling.
