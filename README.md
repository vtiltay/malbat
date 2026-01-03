# 🌳 Malbat.org - Family Tree

Une application web Django pour gérer et visualiser un arbre généalogique avec support d'import Gramps.

## 📋 Description

Malbat.org est une plateforme web complète permettant de gérer un arbre généalogique familial avec les fonctionnalités suivantes :

### ✨ Fonctionnalités principales
- **Import Gramps** : Importer facilement vos données généalogiques depuis Gramps
- **Visualisation interactive** : Parcourir et visualiser l'arbre généalogique
- **Propositions de modifications** : Ajouter/modifier/supprimer des personnes et relations
- **Système de validation** : Approuver ou rejeter les propositions de modifications
- **Authentification utilisateur** : Gestion des utilisateurs et des droits d'accès
- **Notifications email** : Alertes pour les propositions et validations
- **Gestion des médias** : Associer des photos aux personnes

## 🚀 Installation

### Prérequis

- Python 3.8+
- pip
- Virtual environment (vivement recommandé)
- PostgreSQL (optionnel, SQLite par défaut)

### Setup local

```bash
# 1. Cloner le dépôt
git clone git@github.com:vtiltay/malbat.git
cd malbat.org

# 2. Créer et activer l'environnement virtuel
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
# ou sur Windows:
# venv\Scripts\activate

# 3. Installer les dépendances
pip install -r requirements.txt

# 4. Créer le fichier .env (copier depuis template si disponible)
cp .env.example .env  # ou créer manuellement

# 5. Appliquer les migrations
python manage.py migrate

# 6. Créer un superuser
python manage.py createsuperuser

# 7. Collecter les fichiers statiques (production)
python manage.py collectstatic --noinput

# 8. Démarrer le serveur de développement
python manage.py runserver
```

Accéder à l'application : http://localhost:8000

## 📁 Structure du projet

```
malbat.org/
├── familytree/              # Application Django principale
│   ├── models.py            # Modèles (Person, FamilyChild, Event, etc.)
│   ├── views.py             # Vues et logique métier
│   ├── forms.py             # Formulaires
│   ├── urls.py              # Routes
│   ├── filters.py           # Filtres personnalisés
│   ├── signals.py           # Signaux Django
│   ├── admin.py             # Configuration admin
│   ├── management/
│   │   └── commands/        # Commandes personnalisées
│   │       ├── import_gramps.py
│   │       └── test_proposal_email.py
│   ├── migrations/          # Migrations Django
│   └── templates/           # Templates HTML
├── malbat/                  # Configuration Django
│   ├── settings.py          # Paramètres du projet
│   ├── urls.py              # URLs globales
│   ├── wsgi.py              # WSGI pour production
│   └── asgi.py              # ASGI pour WebSockets
├── gramps/                  # Données Gramps (ignoré par Git)
├── media/                   # Fichiers uploadés (ignoré par Git)
├── staticfiles/             # Fichiers statiques compilés
├── requirements.txt         # Dépendances Python
├── manage.py                # Utilitaire Django
├── db.sqlite3               # Base de données (ignoré par Git)
└── .gitignore               # Fichiers à ignorer
```

## 🔧 Commandes utiles

```bash
# Lancer le serveur de développement
python manage.py runserver

# Créer les migrations après modification des modèles
python manage.py makemigrations

# Appliquer les migrations
python manage.py migrate

# Accéder à la console Django
python manage.py shell

# Importer des données Gramps
python manage.py import_gramps chemin/vers/fichier.gramps

# Tester les emails
python manage.py test_proposal_email

# Créer un superuser
python manage.py createsuperuser

# Collecter les fichiers statiques
python manage.py collectstatic
```

## 📧 Configuration Email

Pour activer les notifications email, configurer les variables d'environnement :

```env
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
DEFAULT_FROM_EMAIL=your-email@gmail.com
```

## 🗄️ Modèles de données

### Person
Représente une personne dans l'arbre généalogique.
- `first_name` : Prénom
- `last_name` : Nom de famille
- `gender` : Genre (M/F)
- `birth_date` : Date de naissance
- `death_date` : Date de décès
- `is_deceased` : Statut décédé
- `gramps_id` : ID Gramps

### FamilyChild
Relie les parents et enfants.
- `parent` : Parent (Person)
- `child` : Enfant (Person)

### Event
Événements liés aux personnes.
- `person` : Personne concernée
- `type` : Type d'événement (birth, death, marriage, etc.)
- `date` : Date de l'événement

### ProposedModification
Système de proposition de modifications.
- `proposer` : Utilisateur qui propose
- `type` : Type de proposition
- `status` : Statut (pending, approved, rejected)
- `content` : Détails de la proposition

## 🔐 Sécurité

- ⚠️ **Ne jamais commiter** : `.env`, `db.sqlite3`, clés SSH/API, données Gramps
- ✅ Utiliser `.gitignore` pour exclure les fichiers sensibles
- ✅ Configurer les secrets via variables d'environnement
- ✅ Utiliser HTTPS en production
- ✅ Activer CSRF protection (activé par défaut)

## 📝 Déploiement

### Avec Gunicorn (production)

```bash
pip install gunicorn
gunicorn malbat.wsgi:application --bind 0.0.0.0:8000
```

Utiliser le script fourni :
```bash
./restart_gunicorn.sh
```

### Avec Nginx

Configurer Nginx comme reverse proxy pointant vers Gunicorn.

## 📚 Documentation supplémentaire

- [Email Configuration](EMAIL_CONFIG.md)
- [Email Setup Final](EMAIL_SETUP_FINAL.md)
- [Django Documentation](https://docs.djangoproject.com/)
- [Gramps Documentation](https://gramps-project.org/)

## 🤝 Contribution

Pour contribuer :
1. Créer une branche feature : `git checkout -b feature/ma-feature`
2. Commit les changements : `git commit -am 'Add new feature'`
3. Pousser la branche : `git push origin feature/ma-feature`
4. Ouvrir une Pull Request

## 📄 Licence

À définir

## 👤 Auteur

Victor Tiltay - victor@malbat.org

---

**Dernière mise à jour** : 3 janvier 2026
