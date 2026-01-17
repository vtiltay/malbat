#!/usr/bin/env python3
"""
Script pour corriger les VALEURS des traductions existantes
Remplace "Naissance" par "Date de naissance"
"""

import re
from pathlib import Path

# Corrections à apporter
CORRECTIONS = {
    ("Birth date", "Naissance"): ("Birth date", "Date de naissance"),
    ("First name", ""): ("First name", "Prénom"),
    ("Last name", ""): ("Last name", "Nom de famille"),
    ("Gender", ""): ("Gender", "Genre"),
}

def fix_translations(po_path):
    """Corrige les traductions dans le fichier .po"""
    with open(po_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    print(f"📄 Correction des traductions dans {po_path}")
    print()
    
    fixes = 0
    
    # 1. Remplacer "Naissance" par "Date de naissance"
    if 'msgstr "Naissance"' in content:
        # Chercher la ligne msgid avant
        pattern = r'msgid "Birth date"\nmsgstr "Naissance"'
        if re.search(pattern, content):
            content = re.sub(pattern, 'msgid "Birth date"\nmsgstr "Date de naissance"', content)
            fixes += 1
            print('✏️  "Birth date" → "Date de naissance" (au lieu de "Naissance")')
    
    # 2. Vérifier que "First name" a une traduction
    pattern_first_name = r'msgid "First name"\nmsgstr "([^"]*)"'
    match = re.search(pattern_first_name, content)
    if match:
        current = match.group(1)
        if current != "Prénom":
            content = re.sub(
                r'msgid "First name"\nmsgstr "' + re.escape(current) + '"',
                'msgid "First name"\nmsgstr "Prénom"',
                content
            )
            fixes += 1
            print(f'✏️  "First name" → "Prénom" (était: "{current}")')
    
    # 3. Vérifier que "Last name" a une traduction
    pattern_last_name = r'msgid "Last name"\nmsgstr "([^"]*)"'
    match = re.search(pattern_last_name, content)
    if match:
        current = match.group(1)
        if current != "Nom de famille":
            content = re.sub(
                r'msgid "Last name"\nmsgstr "' + re.escape(current) + '"',
                'msgid "Last name"\nmsgstr "Nom de famille"',
                content
            )
            fixes += 1
            print(f'✏️  "Last name" → "Nom de famille" (était: "{current}")')
    
    # 4. Vérifier que "Gender" a une traduction
    pattern_gender = r'msgid "Gender"\nmsgstr "([^"]*)"'
    match = re.search(pattern_gender, content)
    if match:
        current = match.group(1)
        if current != "Genre":
            content = re.sub(
                r'msgid "Gender"\nmsgstr "' + re.escape(current) + '"',
                'msgid "Gender"\nmsgstr "Genre"',
                content
            )
            fixes += 1
            print(f'✏️  "Gender" → "Genre" (était: "{current}")')
    
    # Sauvegarder
    with open(po_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print()
    print("=" * 60)
    print(f"✅ Corrections appliquées: {fixes}")
    print("=" * 60)
    print()
    print("Prochaines étapes:")
    print("1. Force la recompilation:")
    print("   bash force_recompile.sh")
    
    return True

def main():
    po_path = Path("locale/fr/LC_MESSAGES/django.po")
    
    if not po_path.exists():
        print(f"❌ Erreur: {po_path} non trouvé")
        return False
    
    return fix_translations(po_path)

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
