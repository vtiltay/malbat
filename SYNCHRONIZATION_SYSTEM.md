# Malbat.org - Gramps Synchronization System

## Overview
The Person model now has robust timestamp tracking to distinguish between:
- **Gramps synchronizations** (external updates from genealogy software)
- **Web application edits** (manual changes made through the Django interface)

## Person Model Timestamp Fields

### 1. `created_at` (DateTimeField, auto_now_add=True)
- **Purpose**: Records when the Person record was first created in the database
- **Behavior**: Set once when the record is created, never changes
- **Use Case**: Track initial data entry

### 2. `updated_at` (DateTimeField, auto_now=True)
- **Purpose**: Automatically updated whenever ANY change is made to the Person
- **Behavior**: Updates on every `.save()` call, whether from Gramps sync or web edits
- **Use Case**: Track the most recent modification from any source

### 3. `gramps_last_updated` (DateTimeField, null=True, blank=True)
- **Purpose**: Records the last time this Person was synchronized from Gramps
- **Behavior**: Only updated during Gramps import operations
- **Use Case**: Identify when Gramps data was last synced

## Helper Methods

### `has_local_modifications()`
Returns `True` if the Person has been modified in the web application after the last Gramps synchronization.

**Logic:**
```python
if not gramps_last_updated:
    return True  # Never synced with Gramps, created locally
    
if updated_at > gramps_last_updated (+ 1 second tolerance):
    return True  # Modified after last Gramps sync
    
return False  # No local modifications
```

### `was_modified_locally` (property)
Template-friendly property version of `has_local_modifications()`.

**Usage in templates:**
```django
{% if person.was_modified_locally %}
    <span class="badge badge-warning">Local Changes</span>
{% endif %}
```

## Database Indexes

Three indexes optimize query performance:

1. **`gramps_id`**: Fast lookups by Gramps identifier
2. **`last_name, first_name`**: Efficient name-based searches
3. **`gramps_last_updated`**: Quick filtering by sync status

## Synchronization Workflow

### Import from Gramps (.gramps file)
```bash
python manage.py import_gramps path/to/file.gramps
```

**What happens:**
1. Parses Gramps XML data
2. Uses `update_or_create` for each Person:
   - Updates fields: `first_name`, `last_name`, `gender`
   - Sets `gramps_last_updated` to current timestamp
   - `updated_at` is automatically set by Django
3. Preserves local modifications and ProposedModification links
4. Media files copied to `MEDIA_ROOT/imported/`

### Web Application Edits
When a Person is edited through Django admin or views:
- `updated_at` is automatically updated (auto_now=True)
- `gramps_last_updated` remains unchanged
- Creates a gap between timestamps indicating local modifications

### Detecting Conflicts
To find Persons with local modifications not synced to Gramps:
```python
# People modified locally since last Gramps sync
locally_modified = [
    person for person in Person.objects.all() 
    if person.has_local_modifications()
]

# Or using a queryset (requires custom manager method)
from django.db.models import F, Q
from datetime import timedelta

locally_modified = Person.objects.filter(
    Q(gramps_last_updated__isnull=True) |  # Never synced
    Q(updated_at__gt=F('gramps_last_updated') + timedelta(seconds=1))  # Modified after sync
)
```

## ProposedModification Integration

The `ProposedModification` model tracks user-submitted changes:
- Foreign key to Person: `modification_proposals` (related_name)
- Status field: 'proposed', 'acknowledged', 'completed', 'rejected'
- Preserved during Gramps sync (no cascading deletes)

**Workflow:**
1. User submits modification via web form
2. ProposedModification record created
3. Admin reviews in Django admin
4. Admin applies changes in Gramps desktop application
5. Admin marks ProposedModification as 'completed'
6. Admin exports updated .gramps file
7. Admin runs `import_gramps` to sync back to database
8. Person record updated with new Gramps data

## Migration

Run the migration to add indexes and update help text:
```bash
python manage.py migrate familytree
```

This applies migration `0012_add_person_indexes_and_update_help_text.py`.

## Best Practices

### For Developers
1. Never manually set `gramps_last_updated` outside import operations
2. Use `update_or_create` with `gramps_last_updated=timezone.now()` during imports
3. Let Django's `auto_now` handle `updated_at` automatically
4. Check `has_local_modifications()` before overwriting data

### For Administrators
1. Regularly review ProposedModifications
2. Process local modifications in Gramps before importing
3. Keep Gramps as the "source of truth" for genealogical data
4. Use web interface for temporary annotations and proposals
5. Export from Gramps and import regularly to keep database synchronized

### For Users
1. Submit changes via ProposedModification forms
2. Do not expect instant updates (admin must review)
3. Local edits will be flagged with `was_modified_locally` indicator

## Example Usage

### Check for local modifications before syncing
```python
from familytree.models import Person

person = Person.objects.get(gramps_id='I0001')

if person.has_local_modifications():
    print(f"Warning: {person} has local changes since {person.gramps_last_updated}")
    print(f"Last modified: {person.updated_at}")
    # Handle conflict resolution
```

### Display sync status in templates
```django
<div class="person-card">
    <h3>{{ person.first_name }} {{ person.last_name }}</h3>
    
    {% if person.gramps_last_updated %}
        <small>Last synced: {{ person.gramps_last_updated|date:"Y-m-d H:i" }}</small>
    {% else %}
        <span class="badge badge-info">Local Record</span>
    {% endif %}
    
    {% if person.was_modified_locally %}
        <span class="badge badge-warning">
            Modified locally on {{ person.updated_at|date:"Y-m-d H:i" }}
        </span>
    {% endif %}
</div>
```

## Troubleshooting

### All persons show as "locally modified"
- Check that `gramps_last_updated` is being set during import
- Verify import command is using `update_or_create` with `gramps_last_updated=timezone.now()`

### Timestamps not updating
- Ensure `auto_now=True` is set on `updated_at` field
- Check if direct SQL updates bypass Django ORM (use `.save()` instead)

### Import conflicts
- Manually set `gramps_last_updated` to match `updated_at` for resolved conflicts
- Or accept Gramps data as authoritative by allowing overwrite

## Technical Details

### Timestamp Comparison Tolerance
The `has_local_modifications()` method includes a 1-second tolerance to account for:
- Floating-point precision in datetime operations
- Race conditions during rapid successive saves
- Clock skew between application servers

This prevents false positives from microsecond differences.

### Cascade Behavior
- `Person` deletion: `SET_NULL` on ProposedModification
- Preserves modification history even if person removed
- Allows tracking of rejected deletion proposals
