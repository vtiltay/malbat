from django.apps import AppConfig


class FamilytreeConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'familytree'    
    def ready(self):
        import familytree.signals  # Enregistrer les signaux