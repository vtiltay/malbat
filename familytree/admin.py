from django.contrib import admin
from django.utils.html import format_html
from .models import Person, Family, Event, Place, Note, Media, GrampsImport, ProposedModification
import json

@admin.register(Person)
class PersonAdmin(admin.ModelAdmin):
    list_display = ('first_name', 'last_name', 'gender', 'birth_date', 'death_date')
    search_fields = ('first_name', 'last_name')

@admin.register(Family)
class FamilyAdmin(admin.ModelAdmin):
    list_display = ('gramps_id', 'father', 'mother')

@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ('type', 'date', 'person', 'family', 'place')

@admin.register(Place)
class PlaceAdmin(admin.ModelAdmin):
    list_display = ('name', 'latitude', 'longitude')

@admin.register(Note)
class NoteAdmin(admin.ModelAdmin):
    list_display = ('gramps_id', 'text')


@admin.register(Media)
class MediaAdmin(admin.ModelAdmin):
    list_display = ('gramps_id', 'file_path', 'mime_type', 'description')


@admin.register(GrampsImport)
class GrampsImportAdmin(admin.ModelAdmin):
    list_display = ('name', 'imported_at')
    readonly_fields = ('imported_at',)
    fields = ('name', 'gramps_file', 'imported_at')


@admin.register(ProposedModification)
class ProposedModificationAdmin(admin.ModelAdmin):
    list_display = ['id', 'user_display', 'action_badge', 'entity_type_display', 'person', 'status_badge', 'created_at_display']
    list_filter = ['status', 'action', 'entity_type', 'created_at']
    search_fields = ['user__username', 'user__first_name', 'user__last_name', 'entity_id', 'person__first_name', 'person__last_name']
    readonly_fields = ['created_at', 'updated_at', 'data_formatted', 'user_display']
    date_hierarchy = 'created_at'
    
    fieldsets = (
        ('Informations de la proposition', {
            'fields': ('user_display', 'action', 'entity_type', 'person', 'entity_id', 'created_at', 'updated_at')
        }),
        ('Données proposées', {
            'fields': ('data_formatted',),
            'classes': ('collapse',)
        }),
        ('Traitement par l\'admin', {
            'fields': ('status', 'admin_notes'),
            'description': 'Marquez le statut après traitement dans Gramps et ajoutez des notes'
        }),
    )
    
    # Rendre les champs non éditables
    def get_readonly_fields(self, request, obj=None):
        readonly = list(self.readonly_fields)
        if obj:  # Édition
            readonly.extend(['user', 'action', 'entity_type', 'person', 'entity_id', 'data'])
        return readonly
    
    def user_display(self, obj):
        """Afficher l'utilisateur avec un lien vers son profil admin"""
        if obj.user:
            return format_html(
                '<a href="/admin/auth/user/{}/change/">{}</a>',
                obj.user.id, obj.user.get_full_name() or obj.user.username
            )
        return "—"
    user_display.short_description = 'Utilisateur'
    
    def action_badge(self, obj):
        """Badge coloré pour l'action"""
        colors = {'add': '#28a745', 'update': '#007bff', 'delete': '#dc3545'}
        labels = {'add': '➕ Ajouter', 'update': '✏️ Modifier', 'delete': '🗑️ Supprimer'}
        color = colors.get(obj.action, '#6c757d')
        label = labels.get(obj.action, obj.action)
        return format_html(
            '<span style="background-color: {}; color: white; padding: 5px 10px; border-radius: 3px; font-weight: bold;">{}</span>',
            color, label
        )
    action_badge.short_description = 'Action'
    
    def entity_type_display(self, obj):
        """Afficher le type d'entité de manière lisible"""
        return obj.get_entity_type_display()
    entity_type_display.short_description = 'Type de relation'
    
    def status_badge(self, obj):
        """Badge coloré pour le statut"""
        colors = {
            'proposed': '#ff9800',
            'acknowledged': '#2196f3',
            'completed': '#4caf50',
            'rejected': '#f44336'
        }
        status_labels = {
            'proposed': '📋 Proposée',
            'acknowledged': '👀 Prise en compte',
            'completed': '✅ Complétée',
            'rejected': '❌ Rejetée'
        }
        color = colors.get(obj.status, '#6c757d')
        label = status_labels.get(obj.status, obj.status)
        return format_html(
            '<span style="background-color: {}; color: white; padding: 5px 10px; border-radius: 3px; font-weight: bold;">{}</span>',
            color, label
        )
    status_badge.short_description = 'Statut'
    
    def created_at_display(self, obj):
        """Afficher la date de création de manière lisible"""
        return obj.created_at.strftime('%d/%m/%Y %H:%M')
    created_at_display.short_description = 'Proposée le'
    
    def data_formatted(self, obj):
        """Afficher les données en JSON formaté"""
        try:
            data_str = json.dumps(obj.data, indent=2, ensure_ascii=False)
        except:
            data_str = str(obj.data)
        return format_html(
            '<pre style="background: #f5f5f5; padding: 10px; border-radius: 3px; font-size: 12px; max-height: 400px; overflow: auto;">{}</pre>',
            data_str
        )
    data_formatted.short_description = 'Données proposées'
    
    def has_add_permission(self, request):
        """Les propositions ne peuvent être créées que via le formulaire utilisateur"""
        return False
