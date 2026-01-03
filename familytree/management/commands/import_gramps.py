from django.core.management.base import BaseCommand, CommandError
from django.core.files.storage import FileSystemStorage
from django.utils import timezone
from django.conf import settings
import xml.etree.ElementTree as ET
import gzip
import tarfile
import os
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

        self.stdout.write(f'Starting import from: {file_path}')

        # Clear existing data
        self.stdout.write('Clearing existing data...')
        Person.objects.all().delete()
        Family.objects.all().delete()
        Event.objects.all().delete()
        Place.objects.all().delete()
        Note.objects.all().delete()
        Media.objects.all().delete()
        FamilyChild.objects.all().delete()

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
        """Import places into the database using bulk_create"""
        place_objects = [
            Place(
                gramps_id=place_data['id'],
                name=place_data['name']
            )
            for place_data in places.values()
        ]
        Place.objects.bulk_create(place_objects, batch_size=100)

    def _import_people(self, people):
        """Import people into the database using bulk_create"""
        people_objects = []
        for person_handle, person_data in people.items():
            person_id = person_data['id'] or person_handle
            first_name = person_data['first_name']
            last_name = person_data['last_name']
            gender = person_data['gender']
            gramps_last_updated = person_data.get('gramps_last_updated')
            
            person = Person(
                gramps_id=person_id,
                first_name=first_name,
                last_name=last_name,
                gender=gender,
                gramps_last_updated=gramps_last_updated
            )
            people_objects.append(person)
        
        # Bulk create all people at once
        created_people = Person.objects.bulk_create(people_objects, batch_size=500)
        
        # Create a mapping of gramps_id to Person object for later use
        gramps_id_map = {p.gramps_id: p for p in created_people}
        
        # Update the people dict with model instances
        for person_handle, person_data in list(people.items()):
            person_id = person_data['id'] or person_handle
            if person_id in gramps_id_map:
                people[person_handle] = gramps_id_map[person_id]

    def _import_families(self, families, people):
        """Import families into the database with ordered children from Gramps"""
        family_objects = []
        family_children = []  # Store children to add later in bulk
        
        for family_handle, family_elem in families.items():
            family_id = family_elem.get('id')
            if not family_id:
                continue
            father_elem = family_elem.find(f'{{{GRAMPS_NS}}}father')
            father = people.get(father_elem.get('hlink')) if father_elem is not None else None
            mother_elem = family_elem.find(f'{{{GRAMPS_NS}}}mother')
            mother = people.get(mother_elem.get('hlink')) if mother_elem is not None else None

            family = Family(
                gramps_id=family_id,
                father=father,
                mother=mother
            )
            family_objects.append((family, family_handle, family_elem))
        
        # Bulk create all families
        created_families = Family.objects.bulk_create([f[0] for f in family_objects], batch_size=100)
        
        # Create mapping for families
        family_map = {}
        for idx, (family, family_handle, family_elem) in enumerate(family_objects):
            if idx < len(created_families):
                family_map[family_handle] = created_families[idx]
                families[family_handle] = created_families[idx]
                
                # Collect children
                for order, child_elem in enumerate(family_elem.findall(f'{{{GRAMPS_NS}}}childref')):
                    child_handle = child_elem.get('hlink')
                    if child_handle in people:
                        family_children.append(
                            FamilyChild(
                                family=created_families[idx],
                                child=people[child_handle],
                                order=order
                            )
                        )
        
        # Bulk create all family children
        if family_children:
            FamilyChild.objects.bulk_create(family_children, batch_size=500)

    def _import_events(self, events, people, places, people_event_refs):
        """Import events into the database using bulk_create"""
        # First create all events
        event_objects = []
        event_handle_map = {}
        
        for event_handle, event_data in events.items():
            event_id = event_data['id']
            if not event_id:
                continue
            
            place = places.get(event_data['place_hlink']) if event_data['place_hlink'] else None
            
            event = Event(
                gramps_id=event_id,
                type=event_data['type'],
                date=event_data['date'],
                place=place,
                description=event_data['description'],
                person=None,
                family=None
            )
            event_objects.append(event)
            event_handle_map[len(event_objects) - 1] = event_handle
        
        # Bulk create all events
        created_events = Event.objects.bulk_create(event_objects, batch_size=500)
        
        # Create a mapping of event_handle to Event object
        event_handle_to_obj = {}
        for idx, event in enumerate(created_events):
            event_handle = event_handle_map.get(idx)
            if event_handle:
                event_handle_to_obj[event_handle] = event
                events[event_handle] = event
        
        # Now associate events with persons based on event_refs - batch the updates
        events_to_update = []
        for person_handle, event_refs in people_event_refs.items():
            if person_handle in people:
                person_obj = people[person_handle]
                for event_ref in event_refs:
                    event_handle = event_ref['hlink']
                    if event_handle in event_handle_to_obj:
                        event_obj = event_handle_to_obj[event_handle]
                        if event_obj.person is None:
                            event_obj.person = person_obj
                            events_to_update.append(event_obj)
        
        # Bulk update events with person associations
        if events_to_update:
            Event.objects.bulk_update(events_to_update, ['person'], batch_size=500)

    def _import_notes(self, notes):
        """Import notes into the database using bulk_create"""
        note_objects = []
        note_handle_map = {}
        
        for note_handle, note_elem in notes.items():
            note_id = note_elem.get('id')
            if not note_id:
                continue
            text_elem = note_elem.find(f'{{{GRAMPS_NS}}}text')
            text = ''
            if text_elem is not None:
                text = ''.join(text_elem.itertext()).strip()
            
            note = Note(
                gramps_id=note_id,
                text=text,
                person=None,
                family=None,
                event=None
            )
            note_objects.append(note)
            note_handle_map[len(note_objects) - 1] = note_handle
        
        # Bulk create all notes
        created_notes = Note.objects.bulk_create(note_objects, batch_size=500)
        
        # Update the notes dict with model instances
        for idx, note in enumerate(created_notes):
            note_handle = note_handle_map.get(idx)
            if note_handle:
                notes[note_handle] = note

    def _import_media(self, media, people, people_obj_refs):
        """Import media into the database and associate with persons using bulk operations"""
        import shutil
        import os
        from pathlib import Path
        
        # Get media folder path
        media_root = BASE_DIR / 'media'
        media_root.mkdir(exist_ok=True)
        
        # First create all media objects
        media_objects = []
        media_handle_map = {}
        
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
                
                # Check if the file was already extracted to media folder
                potential_path = media_root / filename
                if potential_path.exists():
                    file_path = f'media/{filename}'
                    self.stdout.write(f'Using extracted media {obj_id}: {filename}')
                else:
                    # Try to copy file if it exists locally
                    if original_file_path and os.path.exists(original_file_path):
                        try:
                            dest_path = media_root / filename
                            shutil.copy2(original_file_path, dest_path)
                            file_path = f'media/{filename}'
                            self.stdout.write(f'Copied media {obj_id}: {filename}')
                        except Exception as e:
                            self.stdout.write(f'Warning: Could not copy {original_file_path}: {e}')
                            file_path = original_file_path
                    else:
                        # File doesn't exist, just store the original path
                        file_path = original_file_path
                        self.stdout.write(f'Importing media {obj_id}: {original_file_path} ({mime_type}) [file not found locally]')
            
            # Extract description from file element attribute
            description = file_elem.get('description', '') if file_elem is not None else ''

            media_obj = Media(
                gramps_id=obj_id,
                file_path=file_path,
                mime_type=mime_type,
                description=description
            )
            media_objects.append(media_obj)
            media_handle_map[len(media_objects) - 1] = media_handle
        
        # Bulk create all media objects
        created_media = Media.objects.bulk_create(media_objects, batch_size=500)
        
        # Create mapping and associate with persons
        media_handle_to_obj = {}
        for idx, media_obj in enumerate(created_media):
            media_handle = media_handle_map.get(idx)
            if media_handle:
                media_handle_to_obj[media_handle] = media_obj
        
        # Now associate media with persons based on obj_refs
        for person_handle, obj_refs in people_obj_refs.items():
            if person_handle in people and obj_refs:
                person_obj = people[person_handle]
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
        """Associate notes with persons, families, and events using bulk_update"""
        notes_to_update = []
        
        # Associate notes with persons
        for person_handle, note_refs in people_note_refs.items():
            if person_handle in people and note_refs:
                person_obj = people[person_handle]
                for note_hlink in note_refs:
                    if note_hlink in notes:
                        note_obj = notes[note_hlink]
                        note_obj.person = person_obj
                        notes_to_update.append(note_obj)
        
        # Associate notes with families
        for family_handle, note_refs in families_note_refs.items():
            if family_handle in families and note_refs:
                family_obj = families[family_handle]
                for note_hlink in note_refs:
                    if note_hlink in notes:
                        note_obj = notes[note_hlink]
                        note_obj.family = family_obj
                        notes_to_update.append(note_obj)
        
        # Associate notes with events
        for event_handle, note_refs in events_note_refs.items():
            if event_handle in events and note_refs:
                event_obj = events[event_handle]
                for note_hlink in note_refs:
                    if note_hlink in notes:
                        note_obj = notes[note_hlink]
                        note_obj.event = event_obj
                        notes_to_update.append(note_obj)
        
        # Bulk update all notes
        if notes_to_update:
            Note.objects.bulk_update(notes_to_update, ['person', 'family', 'event'], batch_size=500)

    def _update_dates(self):
        """Update persons with birth and death dates from events using bulk_update"""
        people_to_update = []
        
        for event in Event.objects.all().select_related('person'):
            if not event.person:
                continue
                
            if event.type.lower() == 'birth' and event.date:
                event.person.birth_date = event.date
                people_to_update.append(event.person)
            elif event.type.lower() == 'death':
                if event.date:
                    event.person.death_date = event.date
                event.person.is_deceased = True
                people_to_update.append(event.person)
        
        # Deduplicate people (in case multiple events for same person)
        unique_people = {}
        for person in people_to_update:
            unique_people[person.id] = person
        
        # Bulk update all people
        if unique_people:
            Person.objects.bulk_update(list(unique_people.values()), ['birth_date', 'death_date', 'is_deceased'], batch_size=500)
