# 📧 Système d'Envoi d'Emails - Généalogie Mala Haco & Izêr

## Configuration

### Mode Test (Console - Par défaut)
Par défaut, les emails s'affichent dans la console. C'est idéal pour le développement.

### Mode Production (SMTP)
Pour envoyer des emails réels, configurez les variables d'environnement :

```bash
export EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
export EMAIL_HOST=smtp.gmail.com
export EMAIL_PORT=587
export EMAIL_USE_TLS=True
export EMAIL_HOST_USER=votre_email@gmail.com
export EMAIL_HOST_PASSWORD=votre_mot_de_passe
export DEFAULT_FROM_EMAIL=noreply@votre_domaine.com
```

Ou via un fichier `.env` :

```
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=votre_email@gmail.com
EMAIL_HOST_PASSWORD=votre_mot_de_passe
DEFAULT_FROM_EMAIL=noreply@malbat.org
```

## Notifications

### Propositions de Modification
Quand un utilisateur crée une proposition, les administrateurs reçoivent un email de notification contenant :

- 📋 ID de la proposition
- 👤 Utilisateur qui a soumis
- 🎯 Action (Ajouter, Modifier, Supprimer)
- 🔗 Lien vers l'interface d'administration

L'email utilise un template HTML formaté avec :
- En-tête coloré avec le logo
- Détails de la proposition
- Bouton d'action pour consulter
- Pied de page avec copyright

## Tests

### Test Simple d'Envoi
```bash
python test_email.py
```

Cela teste :
1. L'envoi d'un email simple
2. L'envoi d'un email HTML avec template

### Test de Proposition
```bash
python manage.py test_proposal_email --person-id 1
```

Cela crée une proposition de test et envoie un email de notification aux administrateurs.

Options :
- `--person-id N` : ID numérique de la personne (par défaut: 1)

## Logs

Les erreurs d'envoi d'email sont enregistrées dans les logs et ne bloquent pas la création de propositions.

Pour activer le debug des emails :

```bash
# Dans manage.py shell
import logging
logging.basicConfig(level=logging.DEBUG)
```

## Structure des Templates

```
familytree/templates/familytree/emails/
├── proposal_notification.html    # Email de notification pour les propositions
```

## Signaux Django

Le système utilise les signaux Django pour déclencher automatiquement l'envoi d'emails :

- Signal `post_save` sur `ProposedModification`
- Enregistré dans `familytree/signals.py`
- Activé via `FamilytreeConfig.ready()` dans `apps.py`

## Dépannage

### Les emails n'apparaissent pas en console
Vérifiez que `EMAIL_BACKEND` est défini à `django.core.mail.backends.console.EmailBackend`

### Erreur "SMTP authentication failed"
Vérifiez vos identifiants EMAIL_HOST_USER et EMAIL_HOST_PASSWORD

### Gmail/2-Factor Authentication
Pour Gmail avec 2FA, générez un [mot de passe d'application](https://support.google.com/accounts/answer/185833)

### Erreur "Connection refused"
Vérifiez que le serveur SMTP est accessible sur EMAIL_HOST:EMAIL_PORT
