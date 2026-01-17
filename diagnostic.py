#!/usr/bin/env python3
"""
Script de diagnostic pour vérifier les traductions
"""

import subprocess
import sys
from pathlib import Path

def check_po_file():
    """Vérifier le contenu du fichier .po"""
    po_path = Path("locale/fr/LC_MESSAGES/django.po")
    
    if not po_path.exists():
        print("❌ Fichier .po manquant!")
        return False
    
    with open(po_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    print("📄 Vérification du fichier .po")
    print()
    
    keys_to_check = [
        "First name",
        "Last name",
        "Gender",
        "Birth date",
        "Male",
        "Female",
        "Unknown",
    ]
    
    found = {}
    for key in keys_to_check:
        if f'msgid "{key}"' in content:
            # Extraire la traduction
            import re
            pattern = f'msgid "{re.escape(key)}"\nmsgstr "([^"]*)"'
            match = re.search(pattern, content)
            if match:
                translation = match.group(1)
                found[key] = translation
                if translation:
                    print(f"✅ '{key}' → '{translation}'")
                else:
                    print(f"❌ '{key}' → VIDE")
            else:
                print(f"⚠️  '{key}' → Pas de msgstr trouvée")
        else:
            print(f"❌ '{key}' → MANQUANTE dans .po")
    
    print()
    return found

def check_mo_file():
    """Vérifier que le fichier .mo existe et est à jour"""
    mo_path = Path("locale/fr/LC_MESSAGES/django.mo")
    po_path = Path("locale/fr/LC_MESSAGES/django.po")
    
    print("📋 État des fichiers compilés")
    print()
    
    if not mo_path.exists():
        print("❌ Fichier .mo ABSENT!")
        print("   → Il faut compiler: python manage.py compilemessages")
        return False
    
    mo_time = mo_path.stat().st_mtime
    po_time = po_path.stat().st_mtime
    
    if mo_time < po_time:
        print("❌ Fichier .mo OBSOLÈTE!")
        print(f"   .po modifié: {po_time}")
        print(f"   .mo compilé: {mo_time}")
        print("   → Il faut recompiler: python manage.py compilemessages")
        return False
    else:
        print(f"✅ Fichier .mo à jour")
        return True

def check_django_settings():
    """Vérifier les paramètres Django"""
    print()
    print("⚙️  Vérification des paramètres Django")
    print()
    
    try:
        import django
        from django.conf import settings
        
        print(f"✅ Django: {django.get_version()}")
        print(f"✅ USE_I18N: {settings.USE_I18N}")
        print(f"✅ LANGUAGE_CODE: {settings.LANGUAGE_CODE}")
        print(f"✅ LANGUAGES: {settings.LANGUAGES}")
        print(f"✅ LOCALE_PATHS: {settings.LOCALE_PATHS}")
        
        # Vérifier le middleware
        if 'django.middleware.locale.LocaleMiddleware' in settings.MIDDLEWARE:
            print(f"✅ LocaleMiddleware: présent")
        else:
            print(f"❌ LocaleMiddleware: ABSENT!")
        
        return True
    except Exception as e:
        print(f"❌ Erreur: {e}")
        return False

def main():
    print("=" * 60)
    print("🔍 DIAGNOSTIC DES TRADUCTIONS")
    print("=" * 60)
    print()
    
    # Vérifier .po
    po_status = check_po_file()
    print()
    
    # Vérifier .mo
    mo_status = check_mo_file()
    print()
    
    # Vérifier Django
    django_status = check_django_settings()
    print()
    
    print("=" * 60)
    print("📋 RÉSUMÉ")
    print("=" * 60)
    print()
    
    if not po_status:
        print("❌ PROBLÈME: Le fichier .po n'a pas les bonnes traductions")
        print("   → Exécuter: python fix_translation_values.py")
    
    if not mo_status:
        print("❌ PROBLÈME: Le fichier .mo est obsolète ou absent")
        print("   → Exécuter: python manage.py compilemessages")
    
    if not django_status:
        print("❌ PROBLÈME: Configuration Django incorrecte")
    
    if po_status and mo_status and django_status:
        print("✅ TOUT SEMBLE BON!")
        print("   Essayez:")
        print("   1. Vider le cache: Ctrl+Shift+Suppr")
        print("   2. Redémarrer: ./restart_gunicorn.sh")
        print("   3. Recharger en mode privé")

if __name__ == "__main__":
    main()
