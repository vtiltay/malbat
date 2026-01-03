#!/usr/bin/env python
"""
Script de test pour envoyer un email via Django
Usage: python test_email.py
"""

import os
import sys
import django

# Configuration de Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'malbat.settings')
django.setup()

from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.contrib.auth.models import User

def test_simple_email():
    """Test d'envoi simple"""
    print("📧 Test 1: Envoi simple d'un email de test")
    
    result = send_mail(
        'Test Email - Généalogie Mala Haco & Izêr',
        'Ceci est un email de test pour vérifier la configuration des mails.',
        'noreply@malbat.org',
        ['admin@malbat.org'],
        fail_silently=False,
    )
    
    if result:
        print("✅ Email envoyé avec succès!\n")
    else:
        print("❌ Erreur lors de l'envoi de l'email\n")
    
    return result

def test_html_email():
    """Test d'envoi avec HTML"""
    print("📧 Test 2: Envoi d'un email HTML")
    
    context = {
        'name': 'Administrateur',
        'proposal_id': 999,
        'user_name': 'test_user',
    }
    
    html_message = render_to_string('familytree/emails/proposal_notification.html', context)
    plain_message = strip_tags(html_message)
    
    result = send_mail(
        'Test HTML Email - Généalogie',
        plain_message,
        'noreply@malbat.org',
        ['admin@malbat.org'],
        html_message=html_message,
        fail_silently=False,
    )
    
    if result:
        print("✅ Email HTML envoyé avec succès!\n")
    else:
        print("❌ Erreur lors de l'envoi de l'email HTML\n")
    
    return result

def show_email_config():
    """Afficher la configuration actuelle des mails"""
    from django.conf import settings
    
    print("⚙️  Configuration actuelle des mails:")
    print(f"  Backend: {settings.EMAIL_BACKEND}")
    print(f"  Host: {settings.EMAIL_HOST}")
    print(f"  Port: {settings.EMAIL_PORT}")
    print(f"  TLS: {settings.EMAIL_USE_TLS}")
    print(f"  User: {settings.EMAIL_HOST_USER if settings.EMAIL_HOST_USER else '(vide)'}")
    print(f"  From: {settings.DEFAULT_FROM_EMAIL}")
    print()

if __name__ == '__main__':
    print("🌳 Teste d'envoi d'emails - Généalogie Mala Haco & Izêr\n")
    print("=" * 60)
    print()
    
    show_email_config()
    
    try:
        test_simple_email()
        test_html_email()
        
        print("=" * 60)
        print("✅ Tests terminés!")
        print("\nNote: Si vous utilisez 'console' comme backend, les emails")
        print("s'afficheront dans la console au lieu d'être envoyés.")
        print("\nPour utiliser un serveur SMTP réel, configurez les variables")
        print("d'environnement:")
        print("  EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend")
        print("  EMAIL_HOST=smtp.gmail.com")
        print("  EMAIL_PORT=587")
        print("  EMAIL_HOST_USER=votre_email@gmail.com")
        print("  EMAIL_HOST_PASSWORD=votre_mot_de_passe")
        
    except Exception as e:
        print(f"❌ Erreur: {e}")
        sys.exit(1)
