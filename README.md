# Malbat.org - Family Tree Project

Un projet Django pour gérer un arbre généalogique avec support d'import Gramps.

## Description

Malbat.org est une application web permettant de visualiser et gérer un arbre généalogique. Elle supporte :
- L'import de données depuis Gramps
- La proposition de modifications (ajout de personnes, relations, suppressions)
- Un système de validation des modifications
- La gestion des utilisateurs et authentification
- Un système de notifications par email

## Installation

### Prérequis
- Python 3.x
- pip
- Virtual environment (recommandé)

### Configuration

1. Cloner le dépôt:
```bash
git clone <url-du-repo>
cd malbat.org
```

2. Créer et activer l'environnement virtuel:
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# ou
venv\Scripts\activate  # Windows
```

3. Installer les dépendances:
```bash
pip install -r requirements.txt
```

4. Appliquer les migrations:
```bash
python manage.py migrate
```

5. Créer un super utilisateur:
```bash
python manage.py createsuperuser
```

6. Démarrer le serveur:
```bash
python manage.py runserver
```

## Structure du projet

- `familytree/` - Application Django principale
- `malbat/` - Configuration Django
- `gramps/` - Fichiers de données Gramps
- `media/` - Fichiers uploadés
- `staticfiles/` - Fichiers statiques

## Documentation

- [Configuration Email](EMAIL_CONFIG.md)
- [Configuration Email - Final](EMAIL_SETUP_FINAL.md)

## Licence

À définir
