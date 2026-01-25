#!/bin/bash
# Script de mise à jour des traductions pour Malbat.org

echo "======================================"
echo "Mise à jour des traductions - Malbat"
echo "======================================"
echo ""

# Couleurs
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Vérifier qu'on est dans le bon répertoire
if [ ! -f "manage.py" ]; then
    echo -e "${YELLOW}Erreur: manage.py non trouvé. Assurez-vous d'être dans le répertoire racine du projet.${NC}"
    exit 1
fi

# Étape 1: Générer le fichier .pot
echo -e "${BLUE}Étape 1: Génération du modèle de traduction (.pot)${NC}"
python manage.py makemessages -l fr --keep-pot
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ Modèle généré avec succès${NC}"
else
    echo -e "${YELLOW}⚠ Erreur lors de la génération du modèle${NC}"
fi
echo ""

# Étape 2: Mettre à jour les fichiers .po
echo -e "${BLUE}Étape 2: Mise à jour des fichiers de traduction (.po)${NC}"
python manage.py makemessages -l fr
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ Fichiers de traduction mis à jour${NC}"
else
    echo -e "${YELLOW}⚠ Erreur lors de la mise à jour des fichiers de traduction${NC}"
fi
echo ""

# Étape 3: Compiler les traductions
echo -e "${BLUE}Étape 3: Compilation des traductions (.mo)${NC}"
python manage.py compilemessages
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ Traductions compilées avec succès${NC}"
else
    echo -e "${YELLOW}⚠ Erreur lors de la compilation${NC}"
fi
echo ""

# Afficher le résumé
echo -e "${GREEN}======================================"
echo "Mise à jour terminée!"
echo "=====================================${NC}"
echo ""
echo "Prochaines étapes:"
echo "1. Ouvrir: locale/fr/LC_MESSAGES/django.po"
echo "2. Chercher les entrées 'fuzzy'"
echo "3. Remplir les traductions manquantes"
echo "4. Compiler à nouveau:"
echo "   python manage.py compilemessages"
echo "5. Redémarrer le serveur:"
echo "   ./restart_gunicorn.sh"
echo ""
echo "Strings nouveaux/modifiés à traduire:"
echo "  - Proposed → Proposée"
echo "  - Acknowledged → Prise en compte"
echo "  - Completed → Complétée"
echo "  - Rejected → Rejetée"
echo "  - Relationship type → Type de relation"
echo "  - Status → Statut"
