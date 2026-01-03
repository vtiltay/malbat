from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.contrib.auth.models import User
from .models import ProposedModification


@receiver(post_save, sender=ProposedModification)
def send_proposal_notification(sender, instance, created, **kwargs):
    """Envoyer une notification par email aux administrateurs quand une proposition est créée"""
    if not created:
        return  # Ne pas envoyer si c'est une mise à jour
    
    try:
        # Récupérer les administrateurs
        admins = User.objects.filter(is_staff=True)
        admin_emails = [admin.email for admin in admins if admin.email]
        
        if not admin_emails:
            return  # Pas d'administrateurs avec email
        
        # Préparer le contenu du mail
        subject = f'[Généalogie] Nouvelle proposition #{instance.id}: {instance.get_action_display()} {instance.get_entity_type_display()}'
        
        context = {
            'proposal': instance,
            'user': instance.user,
            'person': instance.person,
            'action': instance.get_action_display(),
            'entity_type': instance.get_entity_type_display(),
        }
        
        # Rendu du template HTML
        html_message = render_to_string('familytree/emails/proposal_notification.html', context)
        plain_message = strip_tags(html_message)
        
        # Envoyer le mail
        send_mail(
            subject,
            plain_message,
            'noreply@malbat.org',
            admin_emails,
            html_message=html_message,
            fail_silently=True,
        )
    except Exception as e:
        # Enregistrer l'erreur mais ne pas bloquer la création de la proposition
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f'Erreur lors de l\'envoi de l\'email de notification: {e}')
