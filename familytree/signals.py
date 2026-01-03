from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.models import User
from .models import ProposedModification


@receiver(post_save, sender=ProposedModification)
def send_proposal_notification(sender, instance, created, **kwargs):
    """Send email notification to administrators when a proposal is created"""
    if not created:
        return  # Do not send if this is an update
    
    try:
        # Retrieve administrators
        admins = User.objects.filter(is_staff=True)
        admin_emails = [admin.email for admin in admins if admin.email]
        
        if not admin_emails:
            return  # No administrators with email
        
        # Prepare email content
        subject = f'[Genealogy] New proposal #{instance.id}: {instance.get_action_display()} {instance.get_entity_type_display()}'
        
        context = {
            'proposal': instance,
            'user': instance.user,
            'person': instance.person,
            'action': instance.get_action_display(),
            'entity_type': instance.get_entity_type_display(),
        }
        
        # Render HTML template
        html_message = render_to_string('familytree/emails/proposal_notification.html', context)
        plain_message = strip_tags(html_message)
        
        # Send email
        send_mail(
            subject,
            plain_message,
            'noreply@malbat.org',
            admin_emails,
            html_message=html_message,
            fail_silently=True,
        )
    except Exception as e:
        # Log error but do not block proposal creation
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f'Error sending notification email: {e}')
