from django.core.management.base import BaseCommand, CommandError
from django.core.files.storage import FileSystemStorage
from django.utils import timezone
from django.conf import settings
import xml.etree.ElementTree as ET
import gzip
import tarfile
import os
import shutil
import tempfile
from datetime import datetime, date
from pathlib import Path
from familytree.models import Person, Family, Event, Place, Note, Media, FamilyChild

GRAMPS_NS = 'http://gramps-project.org/xml/1.7.2/'
BASE_DIR = Path(settings.BASE_DIR)


class Command(BaseCommand):
    help = 'Import Gramps genealogy data from XML file'

    def add_arguments(self, parser):
        parser.add_argument('file_path', type=str, help='Path to the Gramps XML file (.gramps or .gramps.gz)')
        parser.add_argument('--import-media', action='store_true', help='Import loose media files from the workspace and associate with persons')

    def handle(self, *args, **options):
        file_path = options['file_path']

        if not os.path.exists(file_path):
            raise CommandError(f'File "{file_path}" does not exist')
        
        # Store file path for media handling
        self.current_file_path = file_path

        self.stdout.write(f'Starting incremental import from: {file_path}')

        # INCREMENTAL IMPORT - No data deletion
        # This preserves existing ProposedModification links and other manual changes
        # self.stdout.write('Clearing existing data...')
        # Person.objects.all().delete()
        # Family.objects.all().delete()
        # Event.objects.all().delete()
        # Place.objects.all().delete()
        # Note.objects.all().delete()
        # Media.objects.all().delete()
        # FamilyChild.objects.all().delete()

        # Extract and parse the file
        self.stdout.write('Parsing XML data...')
        places, people, families, events, notes, media, people_event_refs, people_obj_refs, people_note_refs, families_note_refs, events_note_refs = self._parse_xml(file_path)

        # Import data
        self.stdout.write('Importing places...')
        self._import_places(places)

        self.stdout.write('Importing people...')
        self._import_people(people)

        self.stdout.write('Importing families...')
        self._import_families(families, people)

        self.stdout.write('Importing events...')
        self._import_events(events, people, places, people_event_refs)

        self.stdout.write('Importing notes...')
        self._import_notes(notes)

        self.stdout.write('Associating notes...')
        self._associate_notes(notes, people, families, events, people_note_refs, families_note_refs, events_note_refs)

        self.stdout.write('Importing media...')
        self._import_media(media, people, people_obj_refs)

        self.stdout.write('Updating birth/death dates...')
        self._update_dates()

        # Import loose media files if requested
        if options['import_media']:
            self.stdout.write('Importing loose media files...')
            self._import_loose_media(people)

        self.stdout.write(
            self.style.SUCCESS(
                f'Successfully imported {len(people)} people, {len(families)} families, '
                f'{len(events)} events, {len(places)} places, {len(notes)} notes, and {len(media)} media items'
            )
        )

    def _parse_xml(self, file_path):
        """Parse the XML file and return dictionaries of elements"""
        import shutil
        temp_dir = None
        gramps_file_path = file_path
        media_root = BASE_DIR / 'media'
        media_root.mkdir(exist_ok=True)

        # Check if it's a tar.gz containing the gramps file
        try:
            with gzip.open(file_path, 'rb') as gz_file:
                with tarfile.open(fileobj=gz_file, mode='r') as tar:
                    temp_dir = tempfile.mkdtemp()
                    self.stdout.write(f'Extracting Gramps package...')
                    for member in tar.getmembers():
                        if member.name.endswith('.gramps'):
                            tar.extract(member, temp_dir)
                            gramps_file_path = os.path.join(temp_dir, member.name)
                        # Extract media files
                        elif member.isfile() and any(member.name.lower().endswith(ext) for ext in ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.webp']):
                            tar.extract(member, temp_dir)
                            extracted_path = os.path.join(temp_dir, member.name)
                            filename = os.path.basename(member.name)
                            dest_path = media_root / filename
                            try:
                                shutil.copy2(extracted_path, dest_path)
                                self.stdout.write(f'Extracted media: {filename}')
                            except Exception as e:
                                self.stdout.write(f'Warning: Could not copy media {filename}: {e}')
        except (tarfile.TarError, gzip.BadGzipFile, OSError):
            # Not a tar.gz, assume it's the gramps file directly
            pass

        try:
            # Try to open as gzip first
            try:
                file_obj = gzip.open(gramps_file_path, 'rt', encoding='utf-8')
            except (gzip.BadGzipFile, OSError, UnicodeDecodeError):
                # Fall back to regular file
                file_obj = open(gramps_file_path, 'r', encoding='utf-8')

            # Parse the entire XML tree
            tree = ET.parse(file_obj)
            root = tree.getroot()
            file_obj.close()

            places = {}
            people = {}
            families = {}
            events = {}
            notes = {}
            media = {}
            people_event_refs = {}  # Store event refs separately
            people_obj_refs = {}  # Store media refs separately

            # Extract places
            for place_elem in root.findall(f'.//{{{GRAMPS_NS}}}placeobj'):
                place_id = place_elem.get('id')
                place_name_elem = place_elem.find(f'{{{GRAMPS_NS}}}ptitle')
                place_name = place_name_elem.text if place_name_elem is not None and place_name_elem.text else ''
                places[place_id] = {'id': place_id, 'name': place_name}

            # Extract people with their media references
            people_obj_refs = {}  # Store media refs separately
            people_note_refs = {}  # Store note refs separately
            for person_elem in root.findall(f'.//{{{GRAMPS_NS}}}person'):
                # Extract name data
                name_elem = person_elem.find(f'{{{GRAMPS_NS}}}name')
                first_name = ''
                last_name = ''
                
                if name_elem is not None:
                    first_elem = name_elem.find(f'{{{GRAMPS_NS}}}first')
                    if first_elem is not None and first_elem.text:
                        first_name = first_elem.text.strip()
                    
                    surname_elem = name_elem.find(f'{{{GRAMPS_NS}}}surname') 
                    if surname_elem is not None and surname_elem.text:
                        last_name = surname_elem.text.strip()
                
                gender_elem = person_elem.find(f'{{{GRAMPS_NS}}}gender')
                gender = 'U'
                if gender_elem is not None and gender_elem.text:
                    gender = gender_elem.text.strip().upper()
                
                # Extract last change timestamp from Gramps
                gramps_last_updated = None
                # The change attribute is directly on the person element
                change_time = person_elem.get('change')
                if change_time:
                    try:
                        # Gramps stores timestamps as seconds since epoch
                        gramps_last_updated = datetime.fromtimestamp(int(change_time), tz=timezone.utc)
                    except (ValueError, TypeError):
                        gramps_last_updated = None
                
                # If no change attribute found or time extraction failed, use current time
                if gramps_last_updated is None:
                    gramps_last_updated = timezone.now()
                
                # Extract event references
                event_refs = []
                for eventref_elem in person_elem.findall(f'{{{GRAMPS_NS}}}eventref'):
                    event_hlink = eventref_elem.get('hlink')
                    event_role = eventref_elem.get('role', 'Primary')
                    if event_hlink:
                        event_refs.append({'hlink': event_hlink, 'role': event_role})
                
                # Extract media references
                obj_refs = []
                for objref_elem in person_elem.findall(f'{{{GRAMPS_NS}}}objref'):
                    obj_hlink = objref_elem.get('hlink')
                    if obj_hlink:
                        obj_refs.append(obj_hlink)
                
                # Extract note references
                note_refs = []
                for noteref_elem in person_elem.findall(f'{{{GRAMPS_NS}}}noteref'):
                    note_hlink = noteref_elem.get('hlink')
                    if note_hlink:
                        note_refs.append(note_hlink)
                
                person_handle = person_elem.get('handle')
                person_data = {
                    'id': person_elem.get('id'),
                    'first_name': first_name,
                    'last_name': last_name,
                    'gender': gender,
                    'gramps_last_updated': gramps_last_updated
                }
                people[person_handle] = person_data
                people_event_refs[person_handle] = event_refs
                people_obj_refs[person_handle] = obj_refs
                people_note_refs[person_handle] = note_refs

            # Extract families
            families_note_refs = {}  # Store note refs separately
            for family_elem in root.findall(f'.//{{{GRAMPS_NS}}}family'):
                families[family_elem.get('handle')] = family_elem
                # Extract note references
                note_refs = []
                for noteref_elem in family_elem.findall(f'{{{GRAMPS_NS}}}noteref'):
                    note_hlink = noteref_elem.get('hlink')
                    if note_hlink:
                        note_refs.append(note_hlink)
                families_note_refs[family_elem.get('handle')] = note_refs

            # Extract events
            events_note_refs = {}  # Store note refs separately
            for event_elem in root.findall(f'.//{{{GRAMPS_NS}}}event'):
                # Extract event type from child element
                type_elem = event_elem.find(f'{{{GRAMPS_NS}}}type')
                event_type = type_elem.text.lower() if type_elem is not None and type_elem.text else 'unknown'
                
                # Map Gramps event types to Django model choices
                type_mapping = {
                    'birth': 'birth',
                    'death': 'death',
                    'marriage': 'marriage',
                    'divorce': 'divorce',
                    'baptism': 'baptism',
                    'burial': 'burial',
                }
                event_type = type_mapping.get(event_type, 'unknown')
                
                # Extract date
                date_elem = event_elem.find(f'{{{GRAMPS_NS}}}dateval')
                date_str = date_elem.get('val') if date_elem is not None else None
                event_date = None
                if date_str:
                    try:
                        if len(date_str) == 4 and date_str.isdigit():
                            from datetime import date
                            event_date = date(int(date_str), 1, 1)
                        elif len(date_str) == 7 and date_str.count('-') == 1:
                            year, month = date_str.split('-')
                            if year.isdigit() and month.isdigit():
                                event_date = date(int(year), int(month), 1)
                        elif len(date_str) == 10 and date_str.count('-') == 2:
                            from datetime import date
                            event_date = date.fromisoformat(date_str)
                    except (ValueError, TypeError):
                        event_date = None
                
                # Extract place
                place_elem = event_elem.find(f'{{{GRAMPS_NS}}}place')
                place_hlink = place_elem.get('hlink') if place_elem is not None else None
                
                # Extract description
                description_elem = event_elem.find(f'{{{GRAMPS_NS}}}description')
                description = description_elem.text if description_elem is not None and description_elem.text else ''
                
                # Extract note references
                note_refs = []
                for noteref_elem in event_elem.findall(f'{{{GRAMPS_NS}}}noteref'):
                    note_hlink = noteref_elem.get('hlink')
                    if note_hlink:
                        note_refs.append(note_hlink)
                
                event_data = {
                    'id': event_elem.get('id'),
                    'type': event_type,
                    'date': event_date,
                    'place_hlink': place_hlink,
                    'description': description
                }
                events[event_elem.get('handle')] = event_data
                events_note_refs[event_elem.get('handle')] = note_refs

            # Extract notes
            for note_elem in root.findall(f'.//{{{GRAMPS_NS}}}note'):
                notes[note_elem.get('handle')] = note_elem

            # Extract media
            for media_elem in root.findall(f'.//{{{GRAMPS_NS}}}object'):
                media[media_elem.get('handle')] = media_elem

            return places, people, families, events, notes, media, people_event_refs, people_obj_refs, people_note_refs, families_note_refs, events_note_refs

        finally:
            # Clean up temporary directory
            if temp_dir and os.path.exists(temp_dir):
                import shutil
                shutil.rmtree(temp_dir)

    def _import_places(self, places):
        """Import places into the database using update_or_create for incremental updates"""
        for place_data in places.values():
            place, created = Place.objects.update_or_create(
                gramps_id=place_data['id'],
                defaults={'name': place_data['name']}
            )
            places[place_data['id']] = place
            if created:
                self.stdout.write(f'Created place: {place.name}')
            else:
                self.stdout.write(f'Updated place: {place.name}')

    def _import_people(self, people):
        """Import people into the database using update_or_create for incremental updates"""
        for person_handle, person_data in list(people.items()):
            person_id = person_data['id'] or person_handle
            first_name = person_data['first_name']
            last_name = person_data['last_name']
            gender = person_data['gender']
            gramps_last_updated = person_data.get('gramps_last_updated')
            
            person, created = Person.objects.update_or_create(
                gramps_id=person_id,
                defaults={
                    'first_name': first_name,
                    'last_name': last_name,
                    'gender': gender,
                    'gramps_last_updated': gramps_last_updated
                }
            )
            
            # Update the people dict with the model instance
            people[person_handle] = person
            
            if created:
                self.stdout.write(f'Created person: {person.first_name} {person.last_name}')
            else:
                self.stdout.write(f'Updated person: {person.first_name} {person.last_name}')

    def _import_families(self, families, people):
        """Import families into the database using update_or_create for incremental updates"""
        for family_handle, family_elem in families.items():
            family_id = family_elem.get('id')
            if not family_id:
                continue
            
            father_elem = family_elem.find(f'{{{GRAMPS_NS}}}father')
            father = people.get(father_elem.get('hlink')) if father_elem is not None else None
            mother_elem = family_elem.find(f'{{{GRAMPS_NS}}}mother')
            mother = people.get(mother_elem.get('hlink')) if mother_elem is not None else None

            family, created = Family.objects.update_or_create(
                gramps_id=family_id,
                defaults={
                    'father': father,
                    'mother': mother
                }
            )
            
            families[family_handle] = family
            
            if created:
                self.stdout.write(f'Created family: {family.gramps_id}')
            else:
                self.stdout.write(f'Updated family: {family.gramps_id}')
            
            # Update children - remove existing and recreate to maintain order
            FamilyChild.objects.filter(family=family).delete()
            
            # Add children with their order from Gramps
            for order, child_elem in enumerate(family_elem.findall(f'{{{GRAMPS_NS}}}childref')):
                child_handle = child_elem.get('hlink')
                if child_handle in people:
                    FamilyChild.objects.create(
                        family=family,
                        child=people[child_handle],
                        order=order
                    )

    def _import_events(self, events, people, places, people_event_refs):
        """Import events into the database using update_or_create for incremental updates"""
        event_handle_to_obj = {}
        
        # Create/update all events
        for event_handle, event_data in events.items():
            event_id = event_data['id']
            if not event_id:
                continue
            
            place = places.get(event_data['place_hlink']) if event_data['place_hlink'] else None
            
            # Initially create without person association
            event, created = Event.objects.update_or_create(
                gramps_id=event_id,
                defaults={
                    'type': event_data['type'],
                    'date': event_data['date'],
                    'place': place,
                    'description': event_data['description']
                    # person and family will be updated separately
                }
            )
            
            event_handle_to_obj[event_handle] = event
            events[event_handle] = event
            
            if created:
                self.stdout.write(f'Created event: {event.type} ({event.gramps_id})')
            else:
                self.stdout.write(f'Updated event: {event.type} ({event.gramps_id})')
        
        # Now associate events with persons based on event_refs
        for person_handle, event_refs in people_event_refs.items():
            if person_handle in people:
                person_obj = people[person_handle]
                for event_ref in event_refs:
                    event_handle = event_ref['hlink']
                    if event_handle in event_handle_to_obj:
                        event_obj = event_handle_to_obj[event_handle]
                        if event_obj.person != person_obj:
                            event_obj.person = person_obj
                            event_obj.save(update_fields=['person'])

    def _import_notes(self, notes):
        """Import notes into the database using update_or_create for incremental updates"""
        for note_handle, note_elem in list(notes.items()):
            note_id = note_elem.get('id')
            if not note_id:
                continue
            
            text_elem = note_elem.find(f'{{{GRAMPS_NS}}}text')
            text = ''
            if text_elem is not None:
                text = ''.join(text_elem.itertext()).strip()
            
            note, created = Note.objects.update_or_create(
                gramps_id=note_id,
                defaults={'text': text}
                # person, family, event will be updated in _associate_notes
            )
            
            notes[note_handle] = note
            
            if created:
                self.stdout.write(f'Created note: {note.gramps_id[:20]}...')
            else:
                self.stdout.write(f'Updated note: {note.gramps_id[:20]}...')

    def _import_media(self, media, people, people_obj_refs):
        """Import media into the database using update_or_create for incremental updates"""
        import os
        from pathlib import Path
        
        # Get media folder path - use imported subfolder for consistency
        media_root = Path(settings.MEDIA_ROOT) / 'imported'
        media_root.mkdir(exist_ok=True, parents=True)
        
        media_handle_to_obj = {}
        
        for media_handle, media_elem in media.items():
            obj_id = media_elem.get('id')
            if not obj_id:
                continue
            
            # Extract file information
            file_elem = media_elem.find(f'{{{GRAMPS_NS}}}file')
            if file_elem is None:
                self.stdout.write(f'Warning: No file element found for media {obj_id}')
                file_path = ''
                mime_type = ''
            else:
                original_file_path = file_elem.get('src', '')
                mime_type = file_elem.get('mime', '')
                
                # Extract just the filename from the path
                filename = os.path.basename(original_file_path)
                
                # Try to find and copy the file
                relative_path = original_file_path
                dest_path = media_root / filename
                
                # Check if file already exists in imported folder
                if dest_path.exists():
                    relative_path = f'imported/{filename}'
                    self.stdout.write(f'Media file already exists: {filename}')
                else:
                    # Try to find source file in various locations
                    possible_sources = [
                        original_file_path,
                        os.path.join(BASE_DIR, 'media', filename),
                        os.path.join(os.path.dirname(self.current_file_path or ''), filename) if hasattr(self, 'current_file_path') else None
                    ]
                    
                    source_found = False
                    for source_path in possible_sources:
                        if source_path and os.path.isfile(source_path):
                            try:
                                # Handle duplicate filenames
                                counter = 1
                                name, ext = os.path.splitext(filename)
                                final_dest = dest_path
                                while final_dest.exists():
                                    filename = f"{name}_{counter}{ext}"
                                    final_dest = media_root / filename
                                    counter += 1
                                
                                shutil.copy2(source_path, final_dest)
                                relative_path = f'imported/{filename}'
                                self.stdout.write(f'Copied media {obj_id}: {filename}')
                                source_found = True
                                break
                            except Exception as e:
                                self.stdout.write(f'Warning: Could not copy {source_path}: {e}')
                    
                    if not source_found:
                        # File doesn't exist, store original path
                        relative_path = original_file_path
                        self.stdout.write(f'Media file not found locally: {original_file_path}')
                
                file_path = relative_path
            
            # Extract description from file element attribute
            description = file_elem.get('description', '') if file_elem is not None else ''

            media_obj, created = Media.objects.update_or_create(
                gramps_id=obj_id,
                defaults={
                    'file_path': file_path,
                    'mime_type': mime_type,
                    'description': description
                }
            )
            
            media_handle_to_obj[media_handle] = media_obj
            
            if created:
                self.stdout.write(f'Created media: {obj_id}')
            else:
                self.stdout.write(f'Updated media: {obj_id}')
        
        # Now associate media with persons based on obj_refs
        for person_handle, obj_refs in people_obj_refs.items():
            if person_handle in people and obj_refs:
                person_obj = people[person_handle]
                # Clear existing media associations for this person
                person_obj.media.clear()
                # Add current media associations
                for obj_hlink in obj_refs:
                    if obj_hlink in media_handle_to_obj:
                        media_obj = media_handle_to_obj[obj_hlink]
                        person_obj.media.add(media_obj)

    def _import_loose_media(self, people):
        """Import loose media files from the workspace and associate with persons"""
        import os
        import glob
        
        # Find all image files in the workspace
        image_extensions = ['*.jpg', '*.jpeg', '*.png', '*.gif', '*.bmp', '*.tiff', '*.webp']
        media_files = []
        
        for ext in image_extensions:
            media_files.extend(glob.glob(f'**/{ext}', recursive=True))
        
        self.stdout.write(f'Found {len(media_files)} potential media files')
        
        imported_count = 0
        for media_path in media_files:
            # Skip files in .venv, __pycache__, etc.
            if any(skip in media_path for skip in ['.venv', '__pycache__', '.git', 'migrations']):
                continue
            
            # Try to match with persons based on filename
            filename = os.path.basename(media_path).lower()
            
            # Look for Gramps ID in filename
            matched_person = None
            for person_handle, person_obj in people.items():
                gramps_id = person_obj.gramps_id.lower()
                if gramps_id in filename:
                    matched_person = person_obj
                    break
            
            # If no Gramps ID match, try name matching
            if not matched_person:
                for person_handle, person_obj in people.items():
                    first_name = person_obj.first_name.lower()
                    last_name = person_obj.last_name.lower()
                    if first_name and first_name in filename and last_name and last_name in filename:
                        matched_person = person_obj
                        break
            
            if matched_person:
                # Determine MIME type
                ext = os.path.splitext(media_path)[1].lower()
                mime_types = {
                    '.jpg': 'image/jpeg',
                    '.jpeg': 'image/jpeg', 
                    '.png': 'image/png',
                    '.gif': 'image/gif',
                    '.bmp': 'image/bmp',
                    '.tiff': 'image/tiff',
                    '.webp': 'image/webp'
                }
                mime_type = mime_types.get(ext, 'image/jpeg')
                
                # Create media object
                media_id = f"{matched_person.gramps_id}_photo_{imported_count}"
                media_obj, created = Media.objects.get_or_create(
                    gramps_id=media_id,
                    defaults={
                        'file_path': media_path,
                        'mime_type': mime_type,
                        'description': f'Photo of {matched_person.first_name} {matched_person.last_name}'
                    }
                )
                
                # Associate with person
                matched_person.media.add(media_obj)
                imported_count += 1
                self.stdout.write(f'Associated {media_path} with {matched_person.first_name} {matched_person.last_name}')
        
        self.stdout.write(f'Successfully imported {imported_count} loose media files')

    def _associate_notes(self, notes, people, families, events, people_note_refs, families_note_refs, events_note_refs):
        """Associate notes with persons, families, and events using individual updates"""
        # Associate notes with persons
        for person_handle, note_refs in people_note_refs.items():
            if person_handle in people and note_refs:
                person_obj = people[person_handle]
                for note_hlink in note_refs:
                    if note_hlink in notes:
                        note_obj = notes[note_hlink]
                        if note_obj.person != person_obj:
                            note_obj.person = person_obj
                            note_obj.save(update_fields=['person'])
        
        # Associate notes with families
        for family_handle, note_refs in families_note_refs.items():
            if family_handle in families and note_refs:
                family_obj = families[family_handle]
                for note_hlink in note_refs:
                    if note_hlink in notes:
                        note_obj = notes[note_hlink]
                        if note_obj.family != family_obj:
                            note_obj.family = family_obj
                            note_obj.save(update_fields=['family'])
        
        # Associate notes with events
        for event_handle, note_refs in events_note_refs.items():
            if event_handle in events and note_refs:
                event_obj = events[event_handle]
                for note_hlink in note_refs:
                    if note_hlink in notes:
                        note_obj = notes[note_hlink]
                        if note_obj.event != event_obj:
                            note_obj.event = event_obj
                            note_obj.save(update_fields=['event'])

    def _update_dates(self):
        """Update persons with birth and death dates from events using individual updates"""
        updated_people = set()
        
        for event in Event.objects.all().select_related('person'):
            if not event.person or event.person.id in updated_people:
                continue
            
            needs_update = False
            
            if event.type.lower() == 'birth' and event.date:
                if event.person.birth_date != event.date:
                    event.person.birth_date = event.date
                    needs_update = True
            elif event.type.lower() == 'death':
                if event.date and event.person.death_date != event.date:
                    event.person.death_date = event.date
                    needs_update = True
                if not event.person.is_deceased:
                    event.person.is_deceased = True
                    needs_update = True
            
            if needs_update:
                event.person.save(update_fields=['birth_date', 'death_date', 'is_deceased'])
                updated_people.add(event.person.id)
