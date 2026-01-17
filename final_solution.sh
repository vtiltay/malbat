#!/bin/bash
# Script FINAL - Corrige TOUT et redémarre

echo ""
echo "=========================================="
echo "🎯 CORRECTION FINALE - Prêt?"
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

echo "🔧 Étape 1: Correction des valeurs de traductions..."
python fix_translation_values.py
if [ $? -ne 0 ]; then
    echo "❌ Erreur à l'étape 1"
    exit 1
fi
echo ""
sleep 1

echo "🔧 Étape 2: Nettoyage complet des caches..."
find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null
find . -type f -name "*.pyc" -delete 2>/dev/null
rm -f locale/fr/LC_MESSAGES/django.mo
echo "✅ Caches nettoyés"
echo ""
sleep 1

echo "🔧 Étape 3: Recompilation des traductions..."
python manage.py compilemessages -v 2
if [ $? -eq 0 ]; then
    echo "✅ Recompilation réussie"
else
    echo "❌ Erreur lors de la compilation"
    exit 1
fi
echo ""
sleep 1

echo "🔧 Étape 4: Arrêt du serveur..."
pkill -f gunicorn 2>/dev/null || true
pkill -f daphne 2>/dev/null || true
sleep 2
echo "✅ Serveur arrêté"
echo ""

echo "🔧 Étape 5: Redémarrage du serveur..."
./restart_gunicorn.sh
sleep 3
echo "✅ Serveur redémarré"
echo ""

echo "=========================================="
echo "✨ CORRECTION COMPLÈTE!"
echo "=========================================="
echo ""
echo "🧪 TEST IMMÉDIAT:"
echo ""
echo "1️⃣  Ouvrez Firefox en MODE PRIVÉ:"
echo "    about:privatebrowsing"
echo ""
echo "2️⃣  Allez à votre site:"
echo "    https://votre-site.com/"
echo ""
echo "3️⃣  Cliquez 'FR' en haut à droite"
echo ""
echo "4️⃣  Cherchez une personne"
echo "    Cliquez 'Ajouter un enfant'"
echo ""
echo "5️⃣  Le formulaire DOIT afficher:"
echo "   ✅ 'Ajouter un enfant' (pas 'Add Child')"
echo "   ✅ 'Prénom' (pas 'First name')"
echo "   ✅ 'Nom de famille' (pas 'Last name')"
echo "   ✅ 'Genre' (pas 'Gender')"
echo "   ✅ 'Date de naissance' (pas 'Birth date')"
echo ""
echo "=========================================="
echo ""
echo "✅ Fichier .mo regénéré:"
ls -lh locale/fr/LC_MESSAGES/django.mo
echo ""
