# 📧 Configuration Email - Malbat Haco & Izêr

## ✅ Configuration Complète

### Email Configuré
- **Adresse**: malbathaco@gmail.com
- **Serveur**: smtp.gmail.com:587
- **Authentification**: TLS (port 587)
- **Mot de passe**: Mot de passe d'application Gmail

### Statut
✅ Configuration activée et testée avec succès!

## 🔧 Comment ça fonctionne

### Fichier de Configuration
- **`.env`**: Contient les variables d'environnement pour l'email
- **`settings.py`**: Charge le fichier `.env` au démarrage

### Notifications Automatiques
Quand un utilisateur crée une proposition:
1. ✅ Une notification HTML est générée
2. ✅ L'email est envoyé à malbathaco@gmail.com
3. ✅ L'admin reçoit tous les détails de la proposition

## 🧪 Tests Effectués

```bash
# Test 1: Envoi simple
python test_email.py
# Résultat: ✅ Email de test envoyé

# Test 2: Configuration SMTP
python manage.py shell
# Résultat: ✅ Email SMTP envoyé à malbathaco@gmail.com

# Test 3: Notification de proposition
python manage.py test_proposal_email --person-id 1
# Résultat: ✅ Notification de proposition envoyée
```

## 📬 Vérification

Consultez votre boîte de réception malbathaco@gmail.com pour voir:
- Les emails de test
- Les notifications de propositions reçues des utilisateurs

## 🔐 Sécurité

- ✅ Le mot de passe d'application est utilisé (pas le mot de passe Gmail)
- ✅ Les variables sensibles sont stockées dans `.env` (non committé en Git)
- ✅ La configuration est chargée de manière sécurisée

## 📝 Variables d'Environnement Actuelles

```
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=malbathaco@gmail.com
EMAIL_HOST_PASSWORD=[mot de passe d'application]
DEFAULT_FROM_EMAIL=malbathaco@gmail.com
```

## ⚠️ Important

Si vous changez le mot de passe d'application Gmail:
1. Mettez à jour `.env`
2. Redémarrez le service: `sudo systemctl restart malbat.service`

## 📞 Dépannage

**Les emails ne s'envoient pas?**
- Vérifiez que `.env` existe et contient les bonnes variables
- Assurez-vous que le mot de passe d'application est correct
- Vérifiez la connexion Internet

**L'admin ne reçoit pas les notifications?**
- Consultez le log du serveur: `journalctl -u malbat.service`
- Vérifiez que l'utilisateur admin a une adresse email configurée

---
**Configuration à jour**: 1 janvier 2026
