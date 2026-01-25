#!/bin/bash
# Script complet et automatisé pour les traductions Malbat.org
# Usage: bash complete_translations.sh

echo "======================================"
echo "Mise à jour COMPLÈTE des traductions"
echo "======================================"
echo ""

# Couleurs
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

# Configuration - ADAPTEZ CES CHEMINS À VOTRE SERVEUR
VENV_PATH="/srv/venvs/malbat.org"
PROJECT_PATH="/home/malbat.org"

# Vérifier les chemins
if [ ! -d "$VENV_PATH" ]; then
    echo -e "${RED}❌ Erreur: Venv non trouvé à $VENV_PATH${NC}"
    echo "Veuillez modifier VENV_PATH dans ce script."
    exit 1
fi

if [ ! -d "$PROJECT_PATH" ]; then
    echo -e "${RED}❌ Erreur: Projet non trouvé à $PROJECT_PATH${NC}"
    echo "Veuillez modifier PROJECT_PATH dans ce script."
    exit 1
fi

# Aller au répertoire du projet
cd "$PROJECT_PATH"

# Activer le venv
source "$VENV_PATH/bin/activate"

echo -e "${BLUE}Chemin du venv: $VENV_PATH${NC}"
echo -e "${BLUE}Chemin du projet: $PROJECT_PATH${NC}"
echo ""

# Étape 1: Générer les clés de traduction
echo -e "${BLUE}Étape 1: Génération des clés de traduction${NC}"
python manage.py makemessages -l fr --keep-pot
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ Clés de traduction générées${NC}"
else
    echo -e "${RED}❌ Erreur lors de la génération${NC}"
    exit 1
fi
echo ""

# Étape 2: Remplir automatiquement les traductions
echo -e "${BLUE}Étape 2: Remplissage automatique des traductions${NC}"
python "$PROJECT_PATH/add_translations.py"
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ Traductions remplies${NC}"
else
    echo -e "${YELLOW}⚠ Erreur lors du remplissage (le script peut ne pas exister)${NC}"
fi
echo ""

# Étape 3: Compiler les traductions
echo -e "${BLUE}Étape 3: Compilation des traductions${NC}"
python manage.py compilemessages
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ Traductions compilées${NC}"
else
    echo -e "${RED}❌ Erreur lors de la compilation${NC}"
    exit 1
fi
echo ""

# Étape 4: Redémarrer le serveur
echo -e "${BLUE}Étape 4: Redémarrage du serveur${NC}"
./restart_gunicorn.sh
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ Serveur redémarré${NC}"
else
    echo -e "${YELLOW}⚠ Erreur lors du redémarrage${NC}"
fi
echo ""

# Résumé final
echo -e "${GREEN}======================================"
echo "✨ Mise à jour terminée avec succès!"
echo "=====================================${NC}"
echo ""
echo "Vérification:"
echo "1. Allez sur votre site"
echo "2. Cherchez des textes en anglais:"
echo "   - 'Add Child' devrait être 'Ajouter un enfant'"
echo "   - 'First name' devrait être 'Prénom'"
echo "   - 'Gender' devrait être 'Genre'"
echo ""
echo "3. Si encore en anglais:"
echo "   - Videz le cache du navigateur (Ctrl+Shift+Suppr)"
echo "   - Redémarrez le serveur: ./restart_gunicorn.sh"
echo ""
