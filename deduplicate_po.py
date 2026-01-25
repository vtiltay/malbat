#!/usr/bin/env python3
"""
Script pour dédupliquer le fichier .po et garder les BONNES traductions
Supprime les doublons avec majuscules et minuscules mixtes
"""

import re
from pathlib import Path
from collections import OrderedDict

def normalize_po_file(po_path):
    """Déduplique et normalise le fichier .po"""
    with open(po_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    print(f"📄 Normalisation et déduplication de {po_path}")
    print()
    
    # Séparer l'en-tête
    header_match = re.match(r'(#.*?\nmsgid ""\nmsgstr "".*?\n)', content, re.DOTALL)
    if not header_match:
        print("❌ Erreur: En-tête non trouvé")
        return False
    
    header = header_match.group(1)
    rest = content[len(header):]
    
    # Parser les entrées
    entries = OrderedDict()
    current_block = []
    
    for line in rest.split('\n'):
        if line.startswith('msgid "') and current_block:
            # Nouvelle entrée trouvée, traiter la précédente
            block_text = '\n'.join(current_block)
            msgid_match = re.search(r'msgid "([^"]*)"', block_text)
            
            if msgid_match:
                msgid = msgid_match.group(1)
                msgstr_match = re.search(r'msgstr "([^"]*)"', block_text)
                msgstr = msgstr_match.group(1) if msgstr_match else ""
                
                # Clé normalisée (minuscules pour comparaison)
                key_normalized = msgid.lower()
                
                # Garder la version avec la meilleure traduction
                if key_normalized not in entries:
                    entries[key_normalized] = {
                        'msgid': msgid,
                        'msgstr': msgstr,
                        'comments': [l for l in current_block if l.startswith('#')]
                    }
                elif msgstr and not entries[key_normalized]['msgstr']:
                    # Nouvelle entrée a une meilleure traduction
                    entries[key_normalized] = {
                        'msgid': msgid,
                        'msgstr': msgstr,
                        'comments': [l for l in current_block if l.startswith('#')]
                    }
                else:
                    print(f"⚠️  Doublon trouvé: '{msgid}' (gardé la version existante)")
            
            current_block = []
        
        if line.strip():
            current_block.append(line)
    
    # Traiter la dernière entrée
    if current_block:
        block_text = '\n'.join(current_block)
        msgid_match = re.search(r'msgid "([^"]*)"', block_text)
        
        if msgid_match:
            msgid = msgid_match.group(1)
            msgstr_match = re.search(r'msgstr "([^"]*)"', block_text)
            msgstr = msgstr_match.group(1) if msgstr_match else ""
            
            key_normalized = msgid.lower()
            
            if key_normalized not in entries:
                entries[key_normalized] = {
                    'msgid': msgid,
                    'msgstr': msgstr,
                    'comments': [l for l in current_block if l.startswith('#')]
                }
    
    # Vérifier les paires clés différentes qui devraient être les mêmes
    print(f"Entrées trouvées: {len(entries)}")
    print()
    
    # Lister les clés qui existent en plusieurs variantes
    key_variants = {}
    for key_norm, data in entries.items():
        msgid = data['msgid']
        if key_norm not in key_variants:
            key_variants[key_norm] = []
        key_variants[key_norm].append(msgid)
    
    print("Variantes trouvées:")
    for key_norm, variants in key_variants.items():
        if len(variants) > 1:
            print(f"  ⚠️  '{key_norm}':")
            for v in variants:
                print(f"      - '{v}'")
    
    # Reconstruire le fichier
    new_entries = []
    
    for key_norm, data in entries.items():
        lines = []
        
        # Ajouter les commentaires
        if data['comments']:
            lines.extend(data['comments'])
        
        # Ajouter msgid et msgstr
        escaped_msgid = data['msgid'].replace('\\', '\\\\').replace('"', '\\"')
        escaped_msgstr = data['msgstr'].replace('\\', '\\\\').replace('"', '\\"')
        
        lines.append(f'msgid "{escaped_msgid}"')
        lines.append(f'msgstr "{escaped_msgstr}"')
        
        new_entries.append('\n'.join(lines))
    
    # Créer le nouveau contenu
    new_content = header + '\n' + '\n\n'.join(new_entries) + '\n'
    
    # Sauvegarder
    with open(po_path, 'w', encoding='utf-8') as f:
        f.write(new_content)
    
    print()
    print("=" * 60)
    print(f"✅ Normalisation terminée!")
    print(f"   Entrées gardées: {len(entries)}")
    print("=" * 60)
    print()
    print("Prochaines étapes:")
    print("1. Compiler les traductions:")
    print("   python manage.py compilemessages")
    print()
    print("2. Redémarrer le serveur:")
    print("   ./restart_gunicorn.sh")
    
    return True

def main():
    po_path = Path("locale/fr/LC_MESSAGES/django.po")
    
    if not po_path.exists():
        print(f"❌ Erreur: {po_path} non trouvé")
        return False
    
    return normalize_po_file(po_path)

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
