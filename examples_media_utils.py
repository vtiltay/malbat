#!/usr/bin/env python
"""
Example usage of familytree.utils media handling functions.

This script demonstrates various use cases for the utility functions
that handle Gramps media path conversion and file management.
"""

import os
import sys
import django

# Setup Django environment
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'malbat.settings')
django.setup()

from familytree.utils import (
    normalize_gramps_media_path,
    sanitize_filename,
    copy_gramps_media_to_django,
    find_gramps_media_file,
    ensure_media_directory_permissions,
    get_media_url,
    validate_media_file,
    cleanup_orphaned_media
)
from pathlib import Path


def example_1_normalize_paths():
    """Example 1: Normalizing various Gramps path formats"""
    print("\n=== Example 1: Path Normalization ===")
    
    test_paths = [
        '/home/user/photos/family_photo.jpg',  # Absolute Linux path
        'C:\\Users\\user\\photos\\photo.jpg',  # Windows path
        'photos/vacation.jpg',                  # Relative path
        '../media/photo (1).jpg',               # Path with special chars
        'photo with spaces.JPG',                # Spaces in filename
    ]
    
    for gramps_path in test_paths:
        relative_path, was_absolute = normalize_gramps_media_path(gramps_path)
        print(f"Original: {gramps_path}")
        print(f"  → Normalized: {relative_path}")
        print(f"  → Was absolute: {was_absolute}")
        print()


def example_2_sanitize_filenames():
    """Example 2: Sanitizing dangerous filenames"""
    print("\n=== Example 2: Filename Sanitization ===")
    
    dangerous_filenames = [
        'photo (copy 1).jpg',
        'my file?.jpg',
        'test<script>.jpg',
        'file|name.png',
        'photo/with/slashes.jpg',
        '  spaces  .jpg',
    ]
    
    for filename in dangerous_filenames:
        sanitized = sanitize_filename(filename)
        print(f"{filename:30} → {sanitized}")


def example_3_copy_media():
    """Example 3: Copying media files with proper permissions"""
    print("\n=== Example 3: Copy Media Files ===")
    
    # Simulate copying a file from Gramps export
    test_file = '/tmp/test_photo.jpg'
    
    # Create a dummy test file
    Path(test_file).touch()
    
    try:
        relative_path = copy_gramps_media_to_django(
            test_file,
            destination_subfolder='imported',
            handle_duplicates=True,
            set_permissions=True
        )
        
        if relative_path:
            print(f"✓ File copied successfully to: {relative_path}")
            url = get_media_url(relative_path)
            print(f"  Access URL: {url}")
        else:
            print("✗ File copy failed")
    finally:
        # Cleanup test file
        if Path(test_file).exists():
            Path(test_file).unlink()


def example_4_find_media():
    """Example 4: Finding media files in multiple locations"""
    print("\n=== Example 4: Find Media Files ===")
    
    # Simulate searching for a file from Gramps
    gramps_paths = [
        'photos/family.jpg',
        '/absolute/path/photo.jpg',
        'imported/existing_photo.jpg',
    ]
    
    for gramps_path in gramps_paths:
        found = find_gramps_media_file(
            gramps_path,
            search_locations=['/tmp', '/var/tmp']
        )
        
        if found:
            print(f"✓ Found: {gramps_path}")
            print(f"  → Location: {found}")
        else:
            print(f"✗ Not found: {gramps_path}")


def example_5_validate_media():
    """Example 5: Validating media file safety"""
    print("\n=== Example 5: Validate Media Files ===")
    
    from django.conf import settings
    
    # Create test file
    test_file = Path(settings.MEDIA_ROOT) / 'imported' / 'test.jpg'
    test_file.parent.mkdir(parents=True, exist_ok=True)
    test_file.write_bytes(b'fake image data')
    
    try:
        is_valid, error_msg = validate_media_file(test_file)
        
        if is_valid:
            print(f"✓ File is valid: {test_file}")
        else:
            print(f"✗ File validation failed: {error_msg}")
        
        # Test path traversal detection
        dangerous_path = Path(settings.MEDIA_ROOT) / '../../../etc/passwd'
        is_valid, error_msg = validate_media_file(dangerous_path)
        print(f"\nPath traversal test: {error_msg}")
        
    finally:
        # Cleanup
        if test_file.exists():
            test_file.unlink()


def example_6_ensure_permissions():
    """Example 6: Setting proper directory permissions"""
    print("\n=== Example 6: Ensure Directory Permissions ===")
    
    success = ensure_media_directory_permissions(
        subfolder='imported',
        dir_mode=0o755,   # rwxr-xr-x
        file_mode=0o644   # rw-r--r--
    )
    
    if success:
        print("✓ Directory permissions updated successfully")
        print("  Directories: 0o755 (rwxr-xr-x)")
        print("  Files: 0o644 (rw-r--r--)")
    else:
        print("✗ Failed to update permissions")


def example_7_cleanup_orphaned():
    """Example 7: Finding and cleaning up orphaned media files"""
    print("\n=== Example 7: Cleanup Orphaned Media ===")
    
    # Dry run first (safe)
    count, orphaned_list = cleanup_orphaned_media(
        subfolder='imported',
        dry_run=True
    )
    
    print(f"Found {count} orphaned files:")
    for filepath in orphaned_list[:5]:  # Show first 5
        print(f"  - {filepath}")
    
    if len(orphaned_list) > 5:
        print(f"  ... and {len(orphaned_list) - 5} more")
    
    print("\n⚠ To actually delete these files, set dry_run=False")


def example_8_complete_workflow():
    """Example 8: Complete import workflow simulation"""
    print("\n=== Example 8: Complete Import Workflow ===")
    
    # Simulate processing a Gramps media entry
    gramps_media_entries = [
        {
            'id': 'O0001',
            'src': '/home/gramps/photos/wedding.jpg',
            'mime': 'image/jpeg',
            'description': 'Wedding photo 1990'
        },
        {
            'id': 'O0002',
            'src': 'photos/family reunion.JPG',
            'mime': 'image/jpeg',
            'description': 'Family reunion 2005'
        }
    ]
    
    print("Processing Gramps media entries...\n")
    
    for entry in gramps_media_entries:
        print(f"Entry {entry['id']}: {entry['description']}")
        
        # Step 1: Try to find the file
        found_file = find_gramps_media_file(entry['src'])
        
        if found_file:
            print(f"  1. ✓ Found source file: {found_file}")
            
            # Step 2: Copy to Django media
            relative_path = copy_gramps_media_to_django(
                str(found_file),
                destination_subfolder='imported'
            )
            
            if relative_path:
                print(f"  2. ✓ Copied to: {relative_path}")
                
                # Step 3: Generate URL
                url = get_media_url(relative_path)
                print(f"  3. ✓ Access URL: {url}")
                
                # Step 4: Validate
                full_path = Path(settings.MEDIA_ROOT) / relative_path
                is_valid, error = validate_media_file(full_path)
                if is_valid:
                    print(f"  4. ✓ Validation passed")
                else:
                    print(f"  4. ✗ Validation failed: {error}")
            else:
                print(f"  2. ✗ Copy failed")
        else:
            print(f"  1. ✗ Source file not found")
            
            # Normalize path for database anyway
            relative_path, _ = normalize_gramps_media_path(entry['src'])
            print(f"  → Using normalized path: {relative_path}")
        
        print()


def main():
    """Run all examples"""
    print("=" * 60)
    print("Familytree Utils - Media Handling Examples")
    print("=" * 60)
    
    try:
        example_1_normalize_paths()
        example_2_sanitize_filenames()
        example_3_copy_media()
        example_4_find_media()
        example_5_validate_media()
        example_6_ensure_permissions()
        example_7_cleanup_orphaned()
        example_8_complete_workflow()
        
        print("\n" + "=" * 60)
        print("All examples completed successfully!")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n✗ Error running examples: {e}")
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    main()
