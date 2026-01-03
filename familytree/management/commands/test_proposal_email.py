from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from familytree.models import Person, ProposedModification


class Command(BaseCommand):
    help = 'Créer une proposition de test pour vérifier l\'envoi d\'emails'

    def add_arguments(self, parser):
        parser.add_argument(
            '--person-id',
            type=int,
            help='ID numérique de la personne (gramps_id_numeric)',
            default=1
        )

    def handle(self, *args, **options):
        person_id = options['person_id']
        
        try:
            # Trouver la personne
            gramps_id = f'I{person_id:04d}'
            person = Person.objects.get(gramps_id=gramps_id)
            self.stdout.write(f'✅ Personne trouvée: {person.first_name} {person.last_name}')
        except Person.DoesNotExist:
            self.stdout.write(self.style.ERROR(f'❌ Personne avec ID {gramps_id} non trouvée'))
            return
        
        try:
            # Trouver ou créer un utilisateur de test
            user, created = User.objects.get_or_create(
                username='test_proposer',
                defaults={
                    'email': 'test@malbat.org',
                    'first_name': 'Test',
                    'last_name': 'User',
                }
            )
            
            if created:
                self.stdout.write(f'✅ Utilisateur créé: {user.username}')
            else:
                self.stdout.write(f'✅ Utilisateur existant: {user.username}')
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'❌ Erreur lors de la création de l\'utilisateur: {e}'))
            return
        
        try:
            # Créer une proposition
            proposal = ProposedModification.objects.create(
                user=user,
                person=person,
                action='add',
                entity_type='child',
                data={
                    'first_name': 'Test',
                    'last_name': 'Child',
                    'gender': 'M',
                    'birth_date': None,
                }
            )
            
            self.stdout.write(self.style.SUCCESS(f'✅ Proposition créée avec succès: #{proposal.id}'))
            self.stdout.write(f'   Action: {proposal.get_action_display()}')
            self.stdout.write(f'   Type: {proposal.get_entity_type_display()}')
            self.stdout.write(f'   Personne: {person.first_name} {person.last_name}')
            self.stdout.write('')
            self.stdout.write('📧 Un email de notification a été envoyé aux administrateurs.')
            self.stdout.write('   (Consultez la console pour voir l\'email en mode test)')
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'❌ Erreur lors de la création de la proposition: {e}'))
