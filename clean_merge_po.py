#!/usr/bin/env python3
"""
Script pour nettoyer et fusionner les doublons dans django.po
"""

import re
from pathlib import Path
from collections import OrderedDict

def parse_po_entries(content):
    """Parse les entrées .po"""
    entries = OrderedDict()
    
    # Diviser par entrées vides
    blocks = content.split('\n\n')
    
    for block in blocks:
        lines = block.strip().split('\n')
        if not lines or not lines[0]:
            continue
        
        entry_data = {
            'comments': [],
            'msgid': '',
            'msgstr': '',
            'full_text': block
        }
        
        for line in lines:
            if line.startswith('#'):
                entry_data['comments'].append(line)
            elif line.startswith('msgid "'):
                # Extraire le msgid
                match = re.search(r'msgid "([^"]*)"', line)
                if match:
                    entry_data['msgid'] = match.group(1)
            elif line.startswith('msgstr "'):
                # Extraire le msgstr
                match = re.search(r'msgstr "([^"]*)"', line)
                if match:
                    entry_data['msgstr'] = match.group(1)
        
        # Utiliser msgid comme clé
        if entry_data['msgid']:
            # Garder la version avec la meilleure traduction
            if entry_data['msgid'] in entries:
                # Si la nouvelle a une meilleure traduction, remplacer
                if entry_data['msgstr'] and not entries[entry_data['msgid']]['msgstr']:
                    entries[entry_data['msgid']] = entry_data
            else:
                entries[entry_data['msgid']] = entry_data
    
    return entries

def rebuild_po_file(po_path):
    """Nettoie et reconstruit le fichier .po"""
    with open(po_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    print(f"📄 Nettoyage de {po_path}")
    print()
    
    # Séparer le header
    header_match = re.match(r'(#.*?\nmsgid ""\nmsgstr.*?\n)', content, re.DOTALL)
    if not header_match:
        print("❌ Erreur: Header not found")
        return False
    
    header = header_match.group(1)
    rest = content[len(header):]
    
    print(f"Header trouvé: {len(header)} caractères")
    
    # Parser les entrées
    entries = parse_po_entries(rest)
    
    print(f"Entrées trouvées: {len(entries)}")
    print()
    
    # Reconstruire le fichier
    new_entries = []
    
    for msgid, entry_data in entries.items():
        # Construire l'entrée
        lines = []
        
        # Ajouter les commentaires
        if entry_data['comments']:
            lines.extend(entry_data['comments'])
        
        # Ajouter msgid et msgstr
        escaped_msgid = msgid.replace('\\', '\\\\').replace('"', '\\"')
        escaped_msgstr = entry_data['msgstr'].replace('\\', '\\\\').replace('"', '\\"')
        
        lines.append(f'msgid "{escaped_msgid}"')
        lines.append(f'msgstr "{escaped_msgstr}"')
        
        new_entries.append('\n'.join(lines))
    
    # Créer le nouveau contenu
    new_content = header + '\n' + '\n\n'.join(new_entries) + '\n'
    
    # Sauvegarder
    with open(po_path, 'w', encoding='utf-8') as f:
        f.write(new_content)
    
    print("=" * 60)
    print(f"✅ Nettoyage terminé!")
    print(f"   Entrées conservées: {len(entries)}")
    print("=" * 60)
    print()
    print("Vérification de la syntaxe:")
    print("1. Compiler les traductions:")
    print("   python manage.py compilemessages")
    print()
    print("2. Si des erreurs restent, vérifier:")
    print("   msgfmt --check locale/fr/LC_MESSAGES/django.po")
    
    return True

def main():
    po_path = Path("locale/fr/LC_MESSAGES/django.po")
    
    if not po_path.exists():
        print(f"❌ Erreur: {po_path} non trouvé")
        return False
    
    return rebuild_po_file(po_path)

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
