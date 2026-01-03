from django.db import models, connection
from django.utils import timezone
import xml.etree.ElementTree as ET
import gzip
import tarfile
import os
import tempfile
from datetime import date



class Place(models.Model):
    gramps_id = models.CharField(max_length=50, unique=True)
    name = models.CharField(max_length=255)
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)
    # Add more fields as needed

    def __str__(self):
        return self.name

class Person(models.Model):
    GENDER_CHOICES = [
        ('M', 'Homme'),
        ('F', 'Femme'),
        ('U', 'Inconnu'),
    ]
    
    gramps_id = models.CharField(max_length=50, unique=True)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES, default='U')
    birth_date = models.DateField(null=True, blank=True)
    death_date = models.DateField(null=True, blank=True)
    is_deceased = models.BooleanField(default=False, help_text="Marquer comme décédé même sans date")
    media = models.ManyToManyField('Media', related_name='persons', blank=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True)
    gramps_last_updated = models.DateTimeField(null=True, blank=True, help_text="Dernière modification dans Gramps")
    # Add more fields like notes, etc.

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

    @property
    def is_alive(self):
        """Check if person is still alive"""
        return not self.death_date and not self.is_deceased
    
    @property
    def gramps_id_numeric(self):
        return int(self.gramps_id[1:])

class Family(models.Model):
    gramps_id = models.CharField(max_length=50, unique=True)
    father = models.ForeignKey(Person, on_delete=models.SET_NULL, null=True, blank=True, related_name='father_families')
    mother = models.ForeignKey(Person, on_delete=models.SET_NULL, null=True, blank=True, related_name='mother_families')
    children = models.ManyToManyField(Person, through='FamilyChild', related_name='child_families', blank=True)

    def __str__(self):
        return f"Family of {self.father} and {self.mother}"
    
    def get_ordered_children(self):
        """Retourne les enfants triés par ordre Gramps, puis par date de naissance"""
        return self.children.through.objects.filter(family=self).select_related('child').order_by('order', 'child__birth_date')

class FamilyChild(models.Model):
    """Modèle intermédiaire pour gérer l'ordre des enfants"""
    family = models.ForeignKey(Family, on_delete=models.CASCADE)
    child = models.ForeignKey(Person, on_delete=models.CASCADE)
    order = models.PositiveIntegerField(default=0, help_text="Ordre de l'enfant dans la famille (depuis Gramps)")
    
    class Meta:
        ordering = ['order', 'child__birth_date']
        unique_together = ('family', 'child')
    
    def __str__(self):
        return f"{self.family} - {self.child.first_name} (ordre: {self.order})"

class Event(models.Model):
    EVENT_TYPES = [
        ('birth', 'Naissance'),
        ('death', 'Décès'),
        ('marriage', 'Mariage'),
        ('divorce', 'Divorce'),
        ('baptism', 'Baptême'),
        ('burial', 'Enterrement'),
        # Add more as needed
    ]
    
    gramps_id = models.CharField(max_length=50, unique=True)
    type = models.CharField(max_length=20, choices=EVENT_TYPES)
    date = models.DateField(null=True, blank=True)
    place = models.ForeignKey(Place, on_delete=models.SET_NULL, null=True, blank=True)
    description = models.TextField(blank=True)
    person = models.ForeignKey(Person, on_delete=models.CASCADE, null=True, blank=True, related_name='events')
    family = models.ForeignKey(Family, on_delete=models.CASCADE, null=True, blank=True, related_name='events')

    def __str__(self):
        return f"{self.type} event for {self.person or self.family}"

class Note(models.Model):
    gramps_id = models.CharField(max_length=50, unique=True)
    text = models.TextField()
    person = models.ForeignKey(Person, on_delete=models.CASCADE, null=True, blank=True, related_name='notes')
    family = models.ForeignKey(Family, on_delete=models.CASCADE, null=True, blank=True, related_name='notes')
    event = models.ForeignKey(Event, on_delete=models.CASCADE, null=True, blank=True, related_name='notes')

    def __str__(self):
        return f"Note for {self.person or self.family or self.event}"

class GrampsImport(models.Model):
    name = models.CharField(max_length=100, help_text="Name for this import")
    gramps_file = models.FileField(upload_to='gramps_imports/')
    imported_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if self.gramps_file:
            # Utiliser la commande Django import_gramps qui est plus complète
            from django.core.management import call_command
            try:
                call_command('import_gramps', self.gramps_file.path)
            except Exception as e:
                import logging
                logger = logging.getLogger(__name__)
                logger.error(f'Erreur lors de l\'importation Gramps: {e}')
                raise

    def __str__(self):
        return self.name

class Media(models.Model):
    gramps_id = models.CharField(max_length=50, unique=True)
    file_path = models.CharField(max_length=255)  # Path to the media file
    mime_type = models.CharField(max_length=100, blank=True)
    description = models.TextField(blank=True)
    # Add more fields as needed

    def __str__(self):
        return self.description or self.file_path


class ProposedModification(models.Model):
    """Stocke les propositions de modifications des utilisateurs"""
    
    ACTIONS = [
        ('add', 'Ajouter'),
        ('update', 'Modifier'),
        ('delete', 'Supprimer'),
    ]
    
    STATUS = [
        ('proposed', 'Proposée'),
        ('acknowledged', 'Prise en compte'),
        ('completed', 'Complétée'),
        ('rejected', 'Rejetée'),
    ]
    
    ENTITY_TYPES = [
        ('spouse', 'Époux/Épouse'),
        ('child', 'Enfant'),
        ('parent', 'Parent'),
        ('sibling', 'Frère/Sœur'),
        ('other', 'Autre'),
    ]
    
    # Informations de la proposition
    user = models.ForeignKey('auth.User', on_delete=models.SET_NULL, null=True)
    action = models.CharField(max_length=10, choices=ACTIONS)  # add, update, delete
    entity_type = models.CharField(max_length=50, choices=ENTITY_TYPES)  # spouse, child, parent, etc.
    person = models.ForeignKey(Person, on_delete=models.SET_NULL, null=True, blank=True, related_name='modification_proposals')
    entity_id = models.CharField(max_length=255, blank=True, help_text="ID Gramps de la personne pour modification/suppression")
    
    # Contenu de la proposition (stocké en JSON)
    data = models.JSONField(default=dict, help_text="Les données à ajouter/modifier")
    
    # Statut et historique
    status = models.CharField(max_length=20, choices=STATUS, default='proposed')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Notes de l'admin
    admin_notes = models.TextField(blank=True, help_text="Notes lors du traitement dans Gramps")
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['status', '-created_at']),
        ]
    
    def __str__(self):
        return f"{self.get_action_display()} {self.get_entity_type_display()} pour {self.person} - {self.get_status_display()}"
