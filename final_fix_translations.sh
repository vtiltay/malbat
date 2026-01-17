#!/bin/bash
# Script FINAL pour corriger COMPLÈTEMENT tous les problèmes de traduction

echo ""
echo "======================================"
echo "🎯 CORRECTION FINALE DES TRADUCTIONS"
echo "======================================"
echo ""

VENV_PATH="/srv/venvs/malbat.org"
PROJECT_PATH="/home/malbat.org"

# Vérifier les chemins
if [ ! -d "$VENV_PATH" ]; then
    echo "❌ Erreur: Venv non trouvé à $VENV_PATH"
    exit 1
fi

if [ ! -d "$PROJECT_PATH" ]; then
    echo "❌ Erreur: Projet non trouvé à $PROJECT_PATH"
    exit 1
fi

cd "$PROJECT_PATH"
source "$VENV_PATH/bin/activate"

echo "🔧 Étape 1: Nettoyage des doublons..."
python clean_merge_po.py
echo ""
sleep 1

echo "🔧 Étape 2: Réparation de l'en-tête..."
python fix_po_header.py
echo ""
sleep 1

echo "🔧 Étape 3: Ajout des traductions de formulaires..."
python add_forms_translations.py
echo ""
sleep 1

echo "🔧 Étape 4: Compilation des traductions..."
python manage.py compilemessages
if [ $? -eq 0 ]; then
    echo "✅ Compilation réussie!"
else
    echo "❌ Erreur lors de la compilation"
    exit 1
fi
echo ""
sleep 1

echo "🔧 Étape 5: Redémarrage du serveur..."
./restart_gunicorn.sh
echo ""
sleep 2

echo "======================================"
echo "✨ CORRECTION COMPLÈTE!"
echo "======================================"
echo ""
echo "📋 Vérification à faire:"
echo ""
echo "1️⃣  Ouvrez votre navigateur sur:"
echo "   https://votre-site.com/en/family/search/"
echo ""
echo "2️⃣  Regardez le formulaire 'Add Child':"
echo "   ❌ AVANT: 'First name', 'Last name', 'Gender', 'Birth date'"
echo "   ✅ APRÈS: 'Prénom', 'Nom de famille', 'Genre', 'Date de naissance'"
echo ""
echo "3️⃣  Changez la langue:"
echo "   - Cliquez sur 'FR' en haut à droite"
echo "   - Le formulaire doit s'afficher 100% en français"
echo ""
echo "4️⃣  Si encore en anglais:"
echo "   - Videz le cache: Ctrl+Shift+Suppr (tout sélectionner)"
echo "   - Rechargez la page: Ctrl+R"
echo ""
echo "======================================"
