"""
Management command to fix media file permissions.
Run after Gramps import or when encountering permission issues.
"""
from django.core.management.base import BaseCommand
from familytree.utils import ensure_media_directory_permissions


class Command(BaseCommand):
    help = 'Fix media file permissions for web server access'

    def add_arguments(self, parser):
        parser.add_argument(
            '--subfolder',
            type=str,
            default='imported',
            help='Media subfolder to fix (default: imported)'
        )
        parser.add_argument(
            '--dir-mode',
            type=str,
            default='755',
            help='Directory permissions in octal (default: 755)'
        )
        parser.add_argument(
            '--file-mode',
            type=str,
            default='644',
            help='File permissions in octal (default: 644)'
        )

    def handle(self, *args, **options):
        subfolder = options['subfolder']
        dir_mode = int(options['dir_mode'], 8)   # Convert octal string to int
        file_mode = int(options['file_mode'], 8)

        self.stdout.write(f'Fixing permissions in media/{subfolder}/')
        self.stdout.write(f'  Directories: {oct(dir_mode)} ({self._mode_to_string(dir_mode)})')
        self.stdout.write(f'  Files: {oct(file_mode)} ({self._mode_to_string(file_mode)})')

        success = ensure_media_directory_permissions(
            subfolder=subfolder,
            dir_mode=dir_mode,
            file_mode=file_mode
        )

        if success:
            self.stdout.write(
                self.style.SUCCESS(
                    f'✓ Successfully updated permissions for media/{subfolder}/'
                )
            )
        else:
            self.stdout.write(
                self.style.ERROR(
                    '✗ Failed to update permissions. Check logs for details.'
                )
            )
            self.stdout.write(
                self.style.WARNING(
                    'You may need to run this command with sudo or as the media directory owner.'
                )
            )

    def _mode_to_string(self, mode):
        """Convert numeric mode to rwx string representation"""
        result = []
        for i in range(3):
            shift = (2 - i) * 3
            val = (mode >> shift) & 0o7
            result.append('r' if val & 0o4 else '-')
            result.append('w' if val & 0o2 else '-')
            result.append('x' if val & 0o1 else '-')
        return ''.join(result)
