#!/usr/bin/env python3
"""
Script pour ajouter automatiquement les traductions manquantes dans django.po
Usage: python3 add_translations.py
"""

import os
import re
from pathlib import Path

# Dictionnaire des traductions FR → EN
TRANSLATIONS = {
    # Formulaires
    "First name": "Prénom",
    "Last name": "Nom de famille",
    "Gender": "Genre",
    "Male": "Homme",
    "Female": "Femme",
    "Unknown": "Inconnu",
    "Birth date": "Date de naissance",
    
    # Pages
    "Add Spouse": "Ajouter un époux/épouse",
    "Add Child": "Ajouter un enfant",
    "Propose Deletion": "Proposer une suppression",
    
    # Labels
    "Parents": "Parents",
    "Choose a family...": "Choisir une famille...",
    "Propose Addition": "Proposer l'ajout",
    "Cancel": "Annuler",
    "Select a family to add a child to:": "Sélectionnez une famille pour ajouter un enfant :",
    "child of": "enfant de",
    "Select Parents": "Sélectionnez les parents",
    "Child Information": "Informations sur l'enfant",
    "Spouse": "Époux/épouse",
    "Child": "Enfant",
    "Advanced": "Avancé",
    "Add a spouse first": "Ajoutez d'abord un époux/épouse",
    
    # Admin
    "Proposed": "Proposée",
    "Acknowledged": "Prise en compte",
    "Completed": "Complétée",
    "Rejected": "Rejetée",
    "Relationship type": "Type de relation",
    "Status": "Statut",
    
    # Messages
    "You must add a spouse first before adding children.": "Vous devez d'abord ajouter un époux/épouse avant d'ajouter des enfants.",
    "Please select a spouse to add a child.": "Veuillez sélectionner un époux/épouse pour ajouter un enfant.",
    "Your spouse addition proposal has been sent. Number: #": "Votre proposition d'ajout d'époux/épouse a été envoyée. Numéro : #",
    "Your child addition proposal has been sent. Number: #": "Votre proposition d'ajout d'enfant a été envoyée. Numéro : #",
}

def find_po_file():
    """Trouver le fichier django.po"""
    po_path = Path("locale/fr/LC_MESSAGES/django.po")
    if po_path.exists():
        return po_path
    
    # Chercher dans le répertoire courant
    for p in Path(".").rglob("django.po"):
        if "LC_MESSAGES" in str(p):
            return p
    
    return None

def add_translations(po_file):
    """Ajouter les traductions au fichier .po"""
    with open(po_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    original_content = content
    added = 0
    skipped = 0
    
    # Pattern pour trouver les msgid/msgstr vides
    # Format:
    # msgid "texte"
    # msgstr ""
    pattern = r'(msgid "([^"]+)"\nmsgstr "")'
    
    def replace_func(match):
        nonlocal added, skipped
        full_match = match.group(1)
        msgid = match.group(2)
        
        if msgid in TRANSLATIONS:
            translation = TRANSLATIONS[msgid]
            replacement = f'msgid "{msgid}"\nmsgstr "{translation}"'
            added += 1
            return replacement
        else:
            skipped += 1
            return full_match
    
    # Remplacer les traductions vides par les traductions
    new_content = re.sub(pattern, replace_func, content)
    
    # Écrire le fichier
    with open(po_file, 'w', encoding='utf-8') as f:
        f.write(new_content)
    
    return added, skipped, new_content != original_content

def main():
    print("=" * 50)
    print("Ajout automatique des traductions")
    print("=" * 50)
    
    po_file = find_po_file()
    
    if not po_file:
        print("❌ Erreur: Fichier django.po non trouvé!")
        print("Assurez-vous d'être dans le répertoire du projet.")
        return False
    
    print(f"📄 Fichier trouvé: {po_file}")
    
    added, skipped, modified = add_translations(po_file)
    
    print()
    print(f"✅ Traductions ajoutées: {added}")
    print(f"⏭️  Traductions ignorées: {skipped}")
    print()
    
    if modified:
        print("✨ Fichier mis à jour avec succès!")
        print()
        print("Prochaines étapes:")
        print("1. Compiler les traductions:")
        print("   python manage.py compilemessages")
        print()
        print("2. Redémarrer le serveur:")
        print("   ./restart_gunicorn.sh")
        print()
        print("3. Vérifier dans le navigateur que tout est en français")
        return True
    else:
        print("ℹ️  Aucune traduction à ajouter (déjà complètement traduites).")
        return True

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
