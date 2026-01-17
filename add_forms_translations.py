#!/usr/bin/env python3
"""
Script pour ajouter les traductions exactes des labels de formulaires
Ces traductions viennent de forms.py et utilisent des minuscules
"""

import re
from pathlib import Path

# Traductions EXACTES qui manquent - avec minuscules
FORMS_TRANSLATIONS = {
    "First name": "Prénom",
    "Last name": "Nom de famille",
    "Gender": "Genre",
    "Birth date": "Date de naissance",
    "Password": "Mot de passe",
    "Confirm password": "Confirmer le mot de passe",
    "Person ID to delete (Gramps ID)": "ID de la personne à supprimer (ID Gramps)",
    "I confirm the deletion": "Je confirme la suppression",
}

def add_missing_translations(po_path):
    """Ajoute les traductions manquantes au fichier .po"""
    with open(po_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    print(f"📄 Ajout des traductions de formulaires à {po_path}")
    print()
    
    added = 0
    updated = 0
    
    for msgid, msgstr in FORMS_TRANSLATIONS.items():
        # Échapper pour la regex
        escaped_msgid = re.escape(msgid)
        
        # Chercher si la traduction existe
        pattern = f'msgid "{escaped_msgid}"\nmsgstr "([^"]*)"'
        match = re.search(pattern, content)
        
        if match:
            current_msgstr = match.group(1)
            if current_msgstr == "":
                # Mettre à jour une traduction vide
                old = f'msgid "{msgid}"\nmsgstr ""'
                new = f'msgid "{msgid}"\nmsgstr "{msgstr}"'
                content = content.replace(old, new)
                updated += 1
                print(f"✏️  Mise à jour: {msgid} → {msgstr}")
            else:
                print(f"ℹ️  Déjà traduit: {msgid} → {current_msgstr}")
        else:
            # Ajouter une nouvelle traduction avant la dernière ligne vide
            new_entry = f'\nmsgid "{msgid}"\nmsgstr "{msgstr}"'
            # Insérer avant la dernière ligne
            lines = content.rstrip().split('\n')
            lines.insert(-1, new_entry)
            content = '\n'.join(lines) + '\n'
            added += 1
            print(f"➕ Ajout: {msgid} → {msgstr}")
    
    # Sauvegarder
    with open(po_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print()
    print("=" * 60)
    print(f"✅ Traductions ajoutées: {added}")
    print(f"✏️  Traductions mises à jour: {updated}")
    print("=" * 60)
    print()
    print("Prochaines étapes:")
    print("1. Compiler les traductions:")
    print("   python manage.py compilemessages")
    print()
    print("2. Redémarrer le serveur:")
    print("   ./restart_gunicorn.sh")
    print()
    print("3. Vider le cache du navigateur:")
    print("   Chrome: Ctrl+Shift+Suppr")
    
    return True

def main():
    po_path = Path("locale/fr/LC_MESSAGES/django.po")
    
    if not po_path.exists():
        print(f"❌ Erreur: {po_path} non trouvé")
        return False
    
    return add_missing_translations(po_path)

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
