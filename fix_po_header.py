#!/usr/bin/env python3
"""
Script pour réparer l'en-tête du fichier .po
"""

from pathlib import Path
import re

def fix_po_header(po_path):
    """Répare l'en-tête du fichier .po"""
    with open(po_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    print(f"📄 Réparation de l'en-tête {po_path}")
    print()
    
    # En-tête correct pour français
    correct_header = '''# French translations for Malbat.org
# Copyright (C) 2026 Victor Tiltay
# This file is distributed under the same license as the PACKAGE package.
#
msgid ""
msgstr ""
"Project-Id-Version: Malbat.org 1.0\\n"
"Report-Msgid-Bugs-To: \\n"
"POT-Creation-Date: 2026-01-09 00:00+0000\\n"
"PO-Revision-Date: 2026-01-09 00:00+0000\\n"
"Last-Translator: Victor Tiltay <vtiltay@gmail.com>\\n"
"Language-Team: French <fr@li.org>\\n"
"Language: fr\\n"
"MIME-Version: 1.0\\n"
"Content-Type: text/plain; charset=UTF-8\\n"
"Content-Transfer-Encoding: 8bit\\n"
"Plural-Forms: nplurals=2; plural=(n > 1);\\n"
'''
    
    # Trouver où se termine l'en-tête (première ligne msgid après le header)
    # Chercher le premier msgid qui n'est pas ""
    match = re.search(r'(msgid ""\nmsgstr "".*?\n)(\n*)(#:|msgid)', content, re.DOTALL)
    
    if match:
        # Extraire tout ce qui suit l'en-tête
        rest = content[match.start(2):]
        
        # Reconstruire avec le nouvel en-tête
        new_content = correct_header + '\n' + rest
        
        with open(po_path, 'w', encoding='utf-8') as f:
            f.write(new_content)
        
        print("✅ En-tête réparé!")
        print()
        print("Changements:")
        print('  ✓ charset=UTF-8 ajouté')
        print('  ✓ fuzzy removed')
        print('  ✓ Dates mises à jour')
        print()
    else:
        print("❌ Structure d'en-tête non reconnue")
        return False
    
    print("=" * 60)
    print("Prochaines étapes:")
    print("1. Compiler les traductions:")
    print("   python manage.py compilemessages")
    print()
    print("2. Redémarrer le serveur:")
    print("   ./restart_gunicorn.sh")
    print("=" * 60)
    
    return True

def main():
    po_path = Path("locale/fr/LC_MESSAGES/django.po")
    
    if not po_path.exists():
        print(f"❌ Erreur: {po_path} non trouvé")
        return False
    
    return fix_po_header(po_path)

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
