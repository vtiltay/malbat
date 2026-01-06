from django.db import models, connection
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
import xml.etree.ElementTree as ET
import gzip
import tarfile
import os
import tempfile
from datetime import date


# ==================== MODÈLES D'ARBRE GÉNÉALOGIQUE ====================
# Ce module contient tous les modèles pour l'application Malbat.org
# Il gère les personnes, familles, événements et les propositions de modification


class Place(models.Model):
    """
    Modèle représentant un lieu géographique
    Utilisé pour localiser les événements (naissances, mariages, etc.)
    """
    # Identifiant unique Gramps pour la synchronisation
    gramps_id = models.CharField(max_length=50, unique=True)
    # Nom du lieu (ville, région, pays, etc.)
    name = models.CharField(max_length=255)
    # Latitude du lieu (pour futures fonctionnalités cartographiques)
    latitude = models.FloatField(null=True, blank=True)
    # Longitude du lieu (pour futures fonctionnalités cartographiques)
    longitude = models.FloatField(null=True, blank=True)

    def __str__(self):
        return self.name

class Person(models.Model):
    """
    Modèle central de l'arbre généalogique
    Représente une personne avec ses informations personnelles et ses relations familiales
    """
    # Choix de genre disponibles (Homme, Femme, Inconnu)
    GENDER_CHOICES = [
        ('M', 'Homme'),
        ('F', 'Femme'),
        ('U', 'Inconnu'),
    ]
    
    # Identifiant unique Gramps pour la synchronisation des données
    gramps_id = models.CharField(max_length=50, unique=True)
    # Prénom de la personne
    first_name = models.CharField(max_length=100)
    # Nom de famille de la personne
    last_name = models.CharField(max_length=100)
    # Genre de la personne (Homme, Femme ou Inconnu)
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES, default='U')
    # Date de naissance (optionnelle)
    birth_date = models.DateField(null=True, blank=True)
    # Date de décès (optionnelle)
    death_date = models.DateField(null=True, blank=True)
    # Flag pour marquer comme décédé même sans date exacte
    is_deceased = models.BooleanField(default=False, help_text=_("Mark as deceased even without date"))
    # Médias associés (photos, documents, etc.)
    media = models.ManyToManyField('Media', related_name='persons', blank=True)
    # Timestamps pour le suivi
    created_at = models.DateTimeField(auto_now_add=True, null=True, help_text=_("When this record was first created in the database"))
    updated_at = models.DateTimeField(auto_now=True, help_text=_("Last modification time (any change, including web app edits)"))
    # Dernière synchronisation avec Gramps
    gramps_last_updated = models.DateTimeField(null=True, blank=True, help_text=_("Last update from Gramps synchronization"))

    class Meta:
        indexes = [
            models.Index(fields=['gramps_id']),
            models.Index(fields=['last_name', 'first_name']),
            models.Index(fields=['gramps_last_updated']),
        ]

    def __str__(self):
        return f"{self.first_name} {self.last_name}"
    
    def has_local_modifications(self):
        """
        Vérifie si cette personne a été modifiée dans l'application web
        après la dernière synchronisation avec Gramps.
        Retourne True si updated_at > gramps_last_updated (modifications locales présentes).
        """
        if not self.gramps_last_updated:
            # Jamais synchronisé avec Gramps, donc créé localement
            return True
        if not self.updated_at:
            # Pas de updated_at (cas improbable), considérer comme non modifié
            return False
        # Comparer les timestamps (avec une tolérance de 1 seconde pour les problèmes d'arrondi)
        from datetime import timedelta
        time_diff = self.updated_at - self.gramps_last_updated
        return time_diff > timedelta(seconds=1)

    @property
    def is_alive(self):
        """Vérifie si la personne est toujours vivante (pas de date de décès enregistrée)"""
        return not self.death_date and not self.is_deceased
    
    @property
    def gramps_id_numeric(self):
        """Extrait la partie numérique de l'identifiant Gramps (ex: I0001 -> 1)"""
        return int(self.gramps_id[1:])
    
    @property
    def was_modified_locally(self):
        """
        Property version de has_local_modifications() pour utilisation dans les templates.
        Retourne True si cette personne a des modifications locales non synchronisées.
        """
        return self.has_local_modifications()
    
    def get_parents(self):
        """Retourne la liste des parents (père et mère) de cette personne"""
        parents = []
        # Chercher les familles où cette personne est un enfant
        families = Family.objects.filter(children=self)
        for family in families:
            if family.father:
                parents.append(family.father)
            if family.mother:
                parents.append(family.mother)
        return parents

class Family(models.Model):
    """
    Modèle représentant une unité familiale
    Lie un père et une mère à leurs enfants (relation généalogique)
    """
    # Identifiant unique Gramps pour la synchronisation
    gramps_id = models.CharField(max_length=50, unique=True)
    # Référence au père (peut être null)
    father = models.ForeignKey(Person, on_delete=models.SET_NULL, null=True, blank=True, related_name='father_families')
    # Référence à la mère (peut être null)
    mother = models.ForeignKey(Person, on_delete=models.SET_NULL, null=True, blank=True, related_name='mother_families')
    # Liste des enfants (via le modèle intermédiaire FamilyChild)
    children = models.ManyToManyField(Person, through='FamilyChild', related_name='child_families', blank=True)

    def __str__(self):
        return f"Family of {self.father} and {self.mother}"
    
    def get_ordered_children(self):
        """Retourne les enfants triés par ordre Gramps, puis par date de naissance"""
        return self.children.through.objects.filter(family=self).select_related('child').order_by('order', 'child__birth_date')

class FamilyChild(models.Model):
    """
    Modèle intermédiaire de la relation Family-Person
    Gère l'ordre d'apparition des enfants (comme dans Gramps)
    """
    # Référence à la famille
    family = models.ForeignKey(Family, on_delete=models.CASCADE)
    # Référence à l'enfant
    child = models.ForeignKey(Person, on_delete=models.CASCADE)
    # Ordre de l'enfant (depuis Gramps)
    order = models.PositiveIntegerField(default=0, help_text=_("Child order in family (from Gramps)"))
    
    class Meta:
        ordering = ['order', 'child__birth_date']
        # Évite les doublons: une personne ne peut pas être deux fois enfant dans la même famille
        unique_together = ('family', 'child')
    
    def __str__(self):
        return f"{self.family} - {self.child.first_name} (ordre: {self.order})"

class Event(models.Model):
    """
    Modèle représentant un événement généalogique
    Peut être lié à une personne ou à une famille (naissance, mariage, décès, etc.)
    """
    # Types d'événements disponibles avec leurs libellés en français
    EVENT_TYPES = [
        ('birth', 'Naissance'),
        ('death', 'Décès'),
        ('marriage', 'Mariage'),
        ('divorce', 'Divorce'),
        ('baptism', 'Baptême'),
        ('burial', 'Enterrement'),
    ]
    
    # Identifiant unique Gramps pour la synchronisation
    gramps_id = models.CharField(max_length=50, unique=True)
    # Type d'événement (choix parmi EVENT_TYPES)
    type = models.CharField(max_length=20, choices=EVENT_TYPES)
    # Date de l'événement (optionnelle)
    date = models.DateField(null=True, blank=True)
    # Lieu de l'événement (optionnel)
    place = models.ForeignKey(Place, on_delete=models.SET_NULL, null=True, blank=True)
    # Description ou notes supplémentaires
    description = models.TextField(blank=True)
    # Personne concernée par cet événement (peut être null si lié à une famille)
    person = models.ForeignKey(Person, on_delete=models.CASCADE, null=True, blank=True, related_name='events')
    # Famille concernée par cet événement (peut être null si lié à une personne)
    family = models.ForeignKey(Family, on_delete=models.CASCADE, null=True, blank=True, related_name='events')

    def __str__(self):
        return f"{self.type} event for {self.person or self.family}"

class Note(models.Model):
    """
    Modèle représentant une note
    Peut être attachée à une personne, une famille ou un événement
    """
    # Identifiant unique Gramps pour la synchronisation
    gramps_id = models.CharField(max_length=50, unique=True)
    # Contenu texte de la note
    text = models.TextField()
    # Personne associée (peut être null)
    person = models.ForeignKey(Person, on_delete=models.CASCADE, null=True, blank=True, related_name='notes')
    # Famille associée (peut être null)
    family = models.ForeignKey(Family, on_delete=models.CASCADE, null=True, blank=True, related_name='notes')
    # Événement associé (peut être null)
    event = models.ForeignKey(Event, on_delete=models.CASCADE, null=True, blank=True, related_name='notes')

    def __str__(self):
        return f"Note for {self.person or self.family or self.event}"

class GrampsImport(models.Model):
    """
    Modèle pour gérer l'importation de fichiers Gramps
    Permet à l'utilisateur d'uploader et de synchroniser les données depuis Gramps
    """
    # Nom descriptif de cette importation
    name = models.CharField(max_length=100, help_text=_("Name for this import"))
    # Fichier Gramps à importer (.gramps ou .gpkg)
    gramps_file = models.FileField(upload_to='gramps_imports/')
    # Date/heure d'importation
    imported_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if self.gramps_file:
            # Utiliser la commande Django import_gramps qui est plus complète
            from django.core.management import call_command
            try:
                # Appeler la commande import_gramps avec le chemin du fichier
                call_command('import_gramps', self.gramps_file.path)
            except Exception as e:
                import logging
                logger = logging.getLogger(__name__)
                # Enregistrer l'erreur dans les logs pour debugging
                logger.error(f'Erreur lors de l\'importation Gramps: {e}')
                raise

    def __str__(self):
        return self.name

class Media(models.Model):
    """
    Modèle représentant un fichier média
    Peut être une photo, document, etc. associé à des personnes ou familles
    """
    # Identifiant unique Gramps pour la synchronisation
    gramps_id = models.CharField(max_length=50, unique=True)
    # Chemin vers le fichier média (relatif ou absolu)
    file_path = models.CharField(max_length=255)
    # Type MIME du fichier (image/jpeg, application/pdf, etc.)
    mime_type = models.CharField(max_length=100, blank=True)
    # Description ou titre du média
    description = models.TextField(blank=True)

    def __str__(self):
        return self.description or self.file_path


class ProposedModification(models.Model):
    """
    Modèle stockant les propositions de modifications des utilisateurs
    Permet aux utilisateurs de soumettre des changements pour révision par un administrateur
    """
    
    # Types d'actions possibles
    ACTIONS = [
        ('add', 'Ajouter'),
        ('update', 'Modifier'),
        ('delete', 'Supprimer'),
    ]
    
    # États possibles d'une proposition
    STATUS = [
        ('proposed', 'Proposée'),
        ('acknowledged', 'Prise en compte'),
        ('completed', 'Complétée'),
        ('rejected', 'Rejetée'),
    ]
    
    # Types d'entités généalogiques que l'utilisateur peut proposer
    ENTITY_TYPES = [
        ('spouse', 'Époux/Épouse'),
        ('child', 'Enfant'),
        ('parent', 'Parent'),
        ('sibling', 'Frère/Sœur'),
        ('other', 'Autre'),
    ]
    
    # Informations de la proposition
    # Utilisateur ayant soumis la proposition
    user = models.ForeignKey('auth.User', on_delete=models.SET_NULL, null=True)
    # Type d'action (ajouter, modifier, supprimer)
    action = models.CharField(max_length=10, choices=ACTIONS)
    # Type d'entité généalogique concernée
    entity_type = models.CharField(max_length=50, choices=ENTITY_TYPES)
    # Personne principal affectée par la modification
    person = models.ForeignKey(Person, on_delete=models.SET_NULL, null=True, blank=True, related_name='modification_proposals')
    # ID Gramps de la personne à modifier ou supprimer
    entity_id = models.CharField(max_length=255, blank=True, help_text=_("Gramps ID of person for update/deletion"))
    
    # Contenu de la proposition (stocké en JSON pour flexibilité)
    data = models.JSONField(default=dict, help_text=_("Data to add/modify"))
    
    # Statut et historique
    # Statut de la proposition (proposée, prise en compte, complétée, rejetée)
    status = models.CharField(max_length=20, choices=STATUS, default='proposed')
    # Date de création de la proposition
    created_at = models.DateTimeField(auto_now_add=True)
    # Dernière date de mise à jour de la proposition
    updated_at = models.DateTimeField(auto_now=True)
    
    # Notes de l'administrateur lors du traitement
    admin_notes = models.TextField(blank=True, help_text=_("Notes when processing in Gramps"))
    
    class Meta:
        # Ordonne les propositions par date de création (les plus récentes d'abord)
        ordering = ['-created_at']
        # Index pour accélérer les requêtes sur le statut et la date
        indexes = [
            models.Index(fields=['status', '-created_at']),
        ]
    
    def __str__(self):
        """Représentation textuelle de la proposition pour l'affichage dans l'admin"""
        return f"{self.get_action_display()} {self.get_entity_type_display()} pour {self.person} - {self.get_status_display()}"
