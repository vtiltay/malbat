#!/bin/bash
# Script pour forcer la recompilation et vider TOUS les caches

echo ""
echo "=========================================="
echo "🧹 NETTOYAGE COMPLET DES CACHES"
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

echo "🔧 Étape 1: Suppression des fichiers .pyc et __pycache__..."
find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null
find . -type f -name "*.pyc" -delete 2>/dev/null
echo "✅ Cache Python vidé"
echo ""

echo "🔧 Étape 2: Suppression des fichiers .mo compilés..."
rm -f locale/fr/LC_MESSAGES/django.mo
echo "✅ Fichiers .mo supprimés (seront regénérés)"
echo ""

echo "🔧 Étape 3: Recompilation des traductions..."
python manage.py compilemessages -v 2
if [ $? -eq 0 ]; then
    echo "✅ Recompilation réussie"
else
    echo "❌ Erreur lors de la compilation"
    exit 1
fi
echo ""

echo "🔧 Étape 4: Collecte des fichiers statiques..."
python manage.py collectstatic --noinput
if [ $? -eq 0 ]; then
    echo "✅ Fichiers statiques collectés"
else
    echo "⚠️  Erreur à la collecte (non-critique)"
fi
echo ""

echo "🔧 Étape 5: Arrêt de Gunicorn..."
pkill -f gunicorn
pkill -f daphne
sleep 2
echo "✅ Serveur arrêté"
echo ""

echo "🔧 Étape 6: Redémarrage du serveur..."
./restart_gunicorn.sh
sleep 3
echo "✅ Serveur redémarré"
echo ""

echo "=========================================="
echo "✨ CACHES COMPLÈTEMENT VIDÉS!"
echo "=========================================="
echo ""
echo "📋 Vérification à faire IMMÉDIATEMENT:"
echo ""
echo "1️⃣  Mode PRIVÉ du navigateur:"
echo "   Firefox: Ctrl+Shift+P"
echo "   Chrome: Ctrl+Shift+N"
echo ""
echo "2️⃣  Allez à votre site et changez la langue en FR"
echo ""
echo "3️⃣  Cherchez une personne et 'Ajouter un enfant'"
echo ""
echo "4️⃣  Le formulaire DOIT afficher:"
echo "   ✅ 'Prénom' (pas 'First name')"
echo "   ✅ 'Nom de famille' (pas 'Last name')"
echo "   ✅ 'Genre' (pas 'Gender')"
echo "   ✅ 'Date de naissance' (pas 'Birth date')"
echo ""
echo "=========================================="
echo ""
echo "📊 État des traductions:"
echo ""
echo "Vérifiez que django.mo a été regénéré:"
ls -lh locale/fr/LC_MESSAGES/django.mo
echo ""
