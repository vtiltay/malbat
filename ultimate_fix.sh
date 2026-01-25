#!/bin/bash
# Script ULTIME - Règle DÉFINITIVEMENT les traductions

echo ""
echo "=========================================="
echo "🎯 RÉPARATION ULTIME DES TRADUCTIONS"
echo "=========================================="
echo ""

VENV_PATH="/srv/venvs/malbat.org"
PROJECT_PATH="/home/malbat.org"

if [ ! -d "$VENV_PATH" ]; then
    echo "❌ Erreur: Venv non trouvé à $VENV_PATH"
    exit 1
fi

cd "$PROJECT_PATH"
source "$VENV_PATH/bin/activate"

echo "📋 Plan d'action:"
echo "  1. Dédupliquer les clés (Birth date vs Birth Date)"
echo "  2. Réparer l'en-tête (charset)"
echo "  3. Ajouter les traductions manquantes"
echo "  4. Compiler les traductions"
echo "  5. Redémarrer le serveur"
echo ""
echo "=========================================="
echo ""

echo "🔧 Étape 1/5: Déduplication..."
python deduplicate_po.py
if [ $? -ne 0 ]; then
    echo "❌ Erreur à l'étape 1"
    exit 1
fi
echo ""
sleep 1

echo "🔧 Étape 2/5: Réparation de l'en-tête..."
python fix_po_header.py
if [ $? -ne 0 ]; then
    echo "❌ Erreur à l'étape 2"
    exit 1
fi
echo ""
sleep 1

echo "🔧 Étape 3/5: Ajout des traductions de formulaires..."
python add_forms_translations.py
if [ $? -ne 0 ]; then
    echo "❌ Erreur à l'étape 3"
    exit 1
fi
echo ""
sleep 1

echo "🔧 Étape 4/5: Compilation des traductions..."
python manage.py compilemessages
if [ $? -eq 0 ]; then
    echo "✅ Compilation réussie!"
else
    echo "❌ Erreur lors de la compilation"
    exit 1
fi
echo ""
sleep 1

echo "🔧 Étape 5/5: Redémarrage du serveur..."
./restart_gunicorn.sh
if [ $? -eq 0 ]; then
    echo "✅ Serveur redémarré!"
else
    echo "⚠️  Problème au redémarrage (à vérifier)"
fi
echo ""
sleep 2

echo "=========================================="
echo "✨ RÉPARATION COMPLÈTE!"
echo "=========================================="
echo ""
echo "📋 À vérifier MAINTENANT:"
echo ""
echo "1️⃣  Ouvrez votre navigateur en MODE PRIVÉ/INCOGNITO"
echo "   (pour éviter les cache du navigateur)"
echo ""
echo "2️⃣  Allez à: https://votre-site.com/fr/family/search/"
echo "   ou changez la langue en FR dans le menu"
echo ""
echo "3️⃣  Cherchez un enfant et cliquez 'Ajouter un enfant'"
echo ""
echo "4️⃣  Vérifiez le formulaire - DOIT afficher:"
echo "   ✅ 'Ajouter un enfant' (pas 'Add Child')"
echo "   ✅ 'Prénom' (pas 'First name')"
echo "   ✅ 'Nom de famille' (pas 'Last name')"
echo "   ✅ 'Genre' (pas 'Gender')"
echo "   ✅ 'Date de naissance' (pas 'Birth date')"
echo ""
echo "5️⃣  Si ENCORE en anglais:"
echo "   A. Videz le cache Chrome: Ctrl+Shift+Suppr (TOUT)"
echo "   B. Rechargez: Ctrl+Shift+R (cache dur)"
echo "   C. Essayez en mode privé (Ctrl+Shift+N)"
echo ""
echo "=========================================="
echo ""
echo "✅ Les fichiers .py et .sh ont been used:"
for script in deduplicate_po.py fix_po_header.py add_forms_translations.py; do
    if [ -f "$script" ]; then
        echo "  ✓ $script"
    fi
done
