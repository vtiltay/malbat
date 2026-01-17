#!/usr/bin/env python3
"""
Script complet pour ajouter TOUTES les traductions manquantes
Inclut propose_child, propose_spouse, propose_delete, et les formulaires
"""

import re
from pathlib import Path

# TOUTES les traductions nécessaires
ALL_TRANSLATIONS = {
    # === PROPOSE_CHILD.HTML ===
    "Add Child": "Ajouter un enfant",
    "Select a family to add a child to:": "Sélectionnez une famille pour ajouter un enfant :",
    "child of": "enfant de",
    "Parents": "Parents",
    "Choose a family...": "Choisir une famille...",
    
    # === PROPOSE_SPOUSE.HTML ===
    "Add Spouse": "Ajouter un époux/épouse",
    
    # === PROPOSE_DELETE.HTML ===
    "Propose Deletion": "Proposer une suppression",
    
    # === FORMULAIRES - Placeholders et Labels ===
    # Variations de "First name"
    "First name": "Prénom",
    "First Name": "Prénom",
    
    # Variations de "Last name"
    "Last name": "Nom de famille",
    "Last Name": "Nom de famille",
    
    # Genre
    "Gender": "Genre",
    "Male": "Homme",
    "Female": "Femme",
    "Unknown": "Inconnu",
    
    # Birth date
    "Birth date": "Date de naissance",
    "Birth Date": "Date de naissance",
    
    # Boutons et actions
    "Propose Addition": "Proposer l'ajout",
    "Propose Deletion": "Proposer la suppression",
    "Confirm Deletion": "Confirmer la suppression",
    "Cancel": "Annuler",
    
    # Messages d'erreur et confirmation
    "You must add a spouse first before adding children.": "Vous devez d'abord ajouter un époux/épouse avant d'ajouter des enfants.",
    "Please select a spouse to add a child.": "Veuillez sélectionner un époux/épouse pour ajouter un enfant.",
    
    # Admin
    "Proposed": "Proposée",
    "Acknowledged": "Prise en compte",
    "Completed": "Complétée",
    "Rejected": "Rejetée",
    "Relationship type": "Type de relation",
    "Status": "Statut",
    
    # Navigation
    "Spouse": "Époux/épouse",
    "Child": "Enfant",
    "Advanced": "Avancé",
    "Add a spouse first": "Ajoutez d'abord un époux/épouse",
    
    # Autres
    "Propose Modification": "Proposer une modification",
    "Select Parents": "Sélectionnez les parents",
    "Child Information": "Informations sur l'enfant",
}

def escape_po_string(s):
    """Échappe une chaîne pour le format .po"""
    return s.replace('\\', '\\\\').replace('"', '\\"')

def find_missing_translations(po_path):
    """Trouve les traductions manquantes dans le fichier .po"""
    with open(po_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    missing = {}
    
    for msgid, msgstr in ALL_TRANSLATIONS.items():
        # Chercher la traduction dans le fichier
        pattern = f'msgid "{re.escape(msgid)}"\nmsgstr "([^"]*)"'
        match = re.search(pattern, content)
        
        if match:
            current_msgstr = match.group(1)
            if current_msgstr == "":
                # Traduction vide
                missing[msgid] = msgstr
        else:
            # Traduction inexistante
            missing[msgid] = msgstr
    
    return missing

def add_translations_to_po(po_path, translations):
    """Ajoute les traductions au fichier .po"""
    with open(po_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    # Trouver la position pour insérer (avant la dernière ligne vide)
    insert_index = len(lines) - 1
    
    # Créer les nouvelles entrées
    new_entries = []
    for msgid, msgstr in translations.items():
        escaped_msgid = escape_po_string(msgid)
        escaped_msgstr = escape_po_string(msgstr)
        new_entries.append(f'\nmsgid "{escaped_msgid}"\nmsgstr "{escaped_msgstr}"')
    
    # Insérer les nouvelles entrées
    for entry in sorted(new_entries):  # Trier pour avoir un ordre cohérent
        lines.insert(insert_index, entry + '\n')
    
    # Écrire le fichier
    with open(po_path, 'w', encoding='utf-8') as f:
        f.writelines(lines)

def update_empty_translations(po_path, translations):
    """Met à jour les traductions vides existantes"""
    with open(po_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    updated_count = 0
    
    for msgid, msgstr in translations.items():
        escaped_msgid = escape_po_string(msgid)
        escaped_msgstr = escape_po_string(msgstr)
        
        # Remplacer msgstr "" par msgstr "traduction"
        pattern = f'(msgid "{re.escape(escaped_msgid)}"\nmsgstr )""'
        replacement = f'\\1"{escaped_msgstr}"'
        new_content, count = re.subn(pattern, replacement, content)
        
        if count > 0:
            content = new_content
            updated_count += count
            print(f"✅ Mise à jour: {msgid} → {msgstr}")
    
    with open(po_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    return updated_count

def main():
    print("=" * 60)
    print("Mise à jour COMPLÈTE des traductions")
    print("=" * 60)
    print()
    
    po_path = Path("locale/fr/LC_MESSAGES/django.po")
    
    if not po_path.exists():
        print(f"❌ Erreur: {po_path} non trouvé")
        return False
    
    print(f"📄 Fichier: {po_path}")
    print()
    
    # Mettre à jour les traductions vides existantes
    print("Mise à jour des traductions vides...")
    updated = update_empty_translations(po_path, ALL_TRANSLATIONS)
    print(f"✨ {updated} traductions mises à jour")
    print()
    
    # Trouver les traductions manquantes
    print("Recherche des traductions manquantes...")
    missing = find_missing_translations(po_path)
    
    if missing:
        print(f"⚠️  {len(missing)} traductions manquantes trouvées:")
        for msgid, msgstr in sorted(missing.items()):
            print(f"   - {msgid} → {msgstr}")
        print()
        
        # Ajouter les traductions manquantes
        print("Ajout des traductions manquantes...")
        add_translations_to_po(po_path, missing)
        print(f"➕ {len(missing)} traductions ajoutées")
    else:
        print("✅ Aucune traduction manquante!")
    
    print()
    print("=" * 60)
    print("✨ Mise à jour terminée!")
    print("=" * 60)
    print()
    print("Prochaines étapes:")
    print("1. Compiler les traductions:")
    print("   python manage.py compilemessages")
    print()
    print("2. Redémarrer le serveur:")
    print("   ./restart_gunicorn.sh")
    print()
    print("3. Vider le cache Chrome (Ctrl+Shift+Suppr)")
    print()
    print("4. Vérifier que tout est traduit en français")
    
    return True

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
