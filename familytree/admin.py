from django.contrib import admin
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _
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
        (_('Proposal information'), {
            'fields': ('user_display', 'action', 'entity_type', 'person', 'entity_id', 'created_at', 'updated_at')
        }),
        (_('Proposed data'), {
            'fields': ('data_formatted',),
            'classes': ('collapse',)
        }),
        (_('Admin processing'), {
            'fields': ('status', 'admin_notes'),
            'description': _('Mark the status after processing in Gramps and add notes')
        }),
    )
    
    # Make fields non-editable
    def get_readonly_fields(self, request, obj=None):
        readonly = list(self.readonly_fields)
        if obj:  # Edit mode
            readonly.extend(['user', 'action', 'entity_type', 'person', 'entity_id', 'data'])
        return readonly
    
    def user_display(self, obj):
        """Display user with a link to their admin profile"""
        if obj.user:
            return format_html(
                '<a href="/admin/auth/user/{}/change/">{}</a>',
                obj.user.id, obj.user.get_full_name() or obj.user.username
            )
        return "—"
    user_display.short_description = _('User')
    
    def action_badge(self, obj):
        """Colored badge for the action"""
        colors = {'add': '#28a745', 'update': '#007bff', 'delete': '#dc3545'}
        labels = {'add': '➕ ' + _('Add').upper(), 'update': '✏️ ' + _('Update').upper(), 'delete': '🗑️ ' + _('Delete').upper()}
        color = colors.get(obj.action, '#6c757d')
        label = labels.get(obj.action, obj.action)
        return format_html(
            '<span style="background-color: {}; color: white; padding: 5px 10px; border-radius: 3px; font-weight: bold;">{}</span>',
            color, label
        )
    action_badge.short_description = _('Action')
    
    def entity_type_display(self, obj):
        """Display relationship type in readable format"""
        return obj.get_entity_type_display()
    entity_type_display.short_description = _('Relationship type')
    
    def status_badge(self, obj):
        """Badge coloré pour le statut"""
        colors = {
            'proposed': '#ff9800',
            'acknowledged': '#2196f3',
            'completed': '#4caf50',
            'rejected': '#f44336'
        }
        status_labels = {
            'proposed': '📋 ' + _('Proposed'),
            'acknowledged': '👀 ' + _('Acknowledged'),
            'completed': '✅ ' + _('Completed'),
            'rejected': '❌ ' + _('Rejected')
        }
        color = colors.get(obj.status, '#6c757d')
        label = status_labels.get(obj.status, obj.status)
        return format_html(
            '<span style="background-color: {}; color: white; padding: 5px 10px; border-radius: 3px; font-weight: bold;">{}</span>',
            color, label
        )
    status_badge.short_description = _('Status')
    
    def created_at_display(self, obj):
        """Display creation date in readable format"""
        return obj.created_at.strftime('%d/%m/%Y %H:%M')
    created_at_display.short_description = _('Proposed on')
    
    def data_formatted(self, obj):
        """Display data in formatted JSON"""
        try:
            data_str = json.dumps(obj.data, indent=2, ensure_ascii=False)
        except:
            data_str = str(obj.data)
        return format_html(
            '<pre style="background: #f5f5f5; padding: 10px; border-radius: 3px; font-size: 12px; max-height: 400px; overflow: auto;">{}</pre>',
            data_str
        )
    data_formatted.short_description = _('Proposed data')
    
    def has_add_permission(self, request):
        """Proposals can only be created via the user form"""
        return False
