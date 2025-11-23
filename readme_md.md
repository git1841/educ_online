# Plateforme Éducative avec FastAPI et Google Drive

## 📋 Description

Plateforme éducative complète avec:
- **Backend**: FastAPI avec MySQL
- **Stockage Cloud**: Google Drive pour tous les médias
- **Messagerie**: Temps réel avec WebSocket
- **Appels Vidéo**: WebRTC intégré
- **Administration**: Panneau complet de gestion
- **Authentification**: Sessions sécurisées

## 🏗️ Architecture

```
educational-platform/
├── main.py                 # Application FastAPI principale
├── config.py              # Configuration
├── database.py            # Gestion base de données
├── google_drive.py        # Intégration Google Drive
├── auth.py                # Authentification & sessions
├── models.py              # Modèles de données
├── websocket_manager.py   # Gestion WebSocket
├── requirements.txt       # Dépendances Python
├── .env                   # Variables d'environnement
├── credentials.json       # Credentials Google Drive (à créer)
├── templates/             # Templates HTML Jinja2
│   ├── index.html
│   ├── inscription.html
│   ├── login.html
│   ├── pg_pro.html
│   ├── pg_gr.html
│   ├── message_pro.html
│   ├── message_prive.html
│   ├── groupe_pro.html
│   ├── groupe_gr.html
│   ├── group_chat.html
│   ├── video_call.html
│   └── admin_panel.html
└── static/                # Fichiers statiques CSS/JS
    ├── css/
    └── js/
```

## 🚀 Installation

### 1. Prérequis

- Python 3.8+
- MySQL 8.0+
- Compte Google Cloud avec Drive API activé

### 2. Configuration MySQL

```sql
CREATE DATABASE educational_platform;
```

### 3. Installation des dépendances

```bash
pip install -r requirements.txt
```

### 4. Configuration Google Drive API

1. Allez sur [Google Cloud Console](https://console.cloud.google.com/)
2. Créez un nouveau projet
3. Activez l'API Google Drive
4. Créez des identifiants OAuth 2.0 (Application de bureau)
5. Téléchargez le fichier JSON et renommez-le en `credentials.json`
6. Placez-le à la racine du projet

### 5. Configuration des variables d'environnement

Copiez `.env.example` vers `.env` et configurez:

```bash
cp .env.example .env
```

Modifiez `.env` avec vos paramètres:
```
MYSQL_HOST=localhost
MYSQL_USER=root
MYSQL_PASSWORD=votre_mot_de_passe
MYSQL_DATABASE=educational_platform
SECRET_KEY=votre_clé_secrète_aléatoire
```

### 6. Initialisation de la base de données

```bash
python database.py
```

### 7. Première authentification Google Drive

Au premier lancement, vous devrez vous authentifier avec Google:

```bash
python google_drive.py
```

Suivez les instructions dans le navigateur pour autoriser l'application.

## 🎯 Lancement de l'application

### Développement

```bash
python main.py
```

ou

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

L'application sera accessible sur: `http://localhost:8000`

### Production

```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4
```

## 📊 Structure de la base de données

### Tables principales

1. **users** - Utilisateurs de la plateforme
2. **admin** - Administrateurs
3. **contents** - Contenus éducatifs
4. **conversations** - Conversations privées et groupes
5. **conversation_participants** - Participants aux conversations
6. **messages** - Messages
7. **video_calls** - Appels vidéo
8. **admin_publications** - Publications administrateur
9. **group_requests** - Demandes de création de groupes
10. **warnings** - Avertissements utilisateurs

## 🔐 Types d'utilisateurs

### Free
- Accès au contenu gratuit
- Messagerie privée
- Demandes de groupes (approbation requise)

### Pro
- Accès à tout le contenu
- Création directe de groupes
- Toutes fonctionnalités de messagerie

### Admin
- Gestion complète des utilisateurs
- Upload de contenu
- Modération des groupes
- Publications
- Système d'avertissements

## 🌐 Routes principales

### Authentification
- `GET/POST /inscription` - Inscription
- `GET/POST /login` - Connexion
- `GET /logout` - Déconnexion

### Utilisateurs
- `GET /pg_pro` - Page utilisateur Pro
- `GET /pg_gr` - Page utilisateur Free
- `POST /update_profile` - Mise à jour profil
- `POST /change_password` - Changement mot de passe

### Messagerie
- `GET /message_pro` - Messagerie Pro
- `GET /message_prive` - Messagerie Free
- `POST /start_private_chat` - Nouvelle conversation
- `POST /send_private_message` - Envoyer message
- `GET /get_private_messages/{id}` - Historique

### Groupes
- `GET /groupe_pro` - Groupes Pro
- `GET /groupe_gr` - Groupes Free
- `POST /create_group_request` - Créer groupe/demande
- `GET /group_chat/{id}` - Chat de groupe
- `POST /send_group_message` - Message de groupe
- `POST /invite_members` - Inviter membres

### Administration
- `GET /admin_panel` - Panneau admin
- `POST /admin/upload_content` - Upload contenu
- `POST /admin/toggle_user_active/{id}` - Activer/désactiver
- `POST /admin/verify_user/{id}` - Vérifier utilisateur
- `POST /admin/approve_group/{id}` - Approuver groupe
- `POST /admin/create_publication` - Créer publication

### Appels Vidéo
- `POST /start_group_call` - Démarrer appel
- `GET /video_call/{id}` - Page d'appel
- `WebSocket /ws/call/{call_id}/{user_id}` - Signalisation WebRTC

### WebSocket
- `WebSocket /ws/notifications/{user_id}` - Notifications temps réel

## 📁 Stockage Google Drive

### Organisation des dossiers

```
Google Drive/
├── profile_pictures/       # Photos de profil
├── group_avatars/          # Avatars de groupes
├── educational_content/    # Contenu pédagogique
│   ├── pdf/
│   ├── videos/
│   ├── images/
│   └── books/
├── shared_files/           # Fichiers partagés
│   ├── images/
│   └── videos/
└── call_recordings/        # Enregistrements d'appels
```

## 🔒 Sécurité

- Mots de passe hashés avec SHA-256
- Sessions sécurisées avec UUID
- Cookies HTTPOnly
- Validation des permissions à chaque route
- Protection contre l'injection SQL
- Upload de fichiers sécurisé avec validation

## 🛠️ Développement

### Ajouter un nouvel endpoint

1. Définir le modèle dans `models.py`
2. Créer la route dans `main.py`
3. Ajouter la logique de base de données
4. Créer le template HTML si nécessaire

### Ajouter une nouvelle fonctionnalité Google Drive

1. Ajouter la méthode dans `google_drive.py`
2. L'utiliser dans les routes nécessaires

## 📝 Templates HTML à créer

Chaque template doit hériter d'un layout de base et inclure:
- Bootstrap 5 pour le style
- JavaScript pour les interactions
- WebSocket pour le temps réel

### Templates requis:
1. `index.html` - Page d'accueil
2. `inscription.html` - Formulaire d'inscription
3. `login.html` - Formulaire de connexion
4. `pg_pro.html` - Dashboard Pro
5. `pg_gr.html` - Dashboard Free
6. `message_pro.html` - Messagerie Pro
7. `message_prive.html` - Messagerie Free
8. `groupe_pro.html` - Groupes Pro
9. `groupe_gr.html` - Groupes Free
10. `group_chat.html` - Chat de groupe
11. `video_call.html` - Interface d'appel vidéo
12. `admin_panel.html` - Panneau administrateur

## 🐛 Debugging

### Problèmes courants

1. **Erreur de connexion MySQL**
   - Vérifier les credentials dans `.env`
   - S'assurer que MySQL est démarré

2. **Erreur Google Drive API**
   - Vérifier `credentials.json`
   - Re-authentifier avec `python google_drive.py`
   - Vérifier que l'API Drive est activée

3. **WebSocket déconnecté**
   - Vérifier le pare-feu
   - S'assurer que le port WebSocket est ouvert

## 📞 Support

Pour toute question ou problème, consultez la documentation FastAPI:
- [FastAPI Docs](https://fastapi.tiangolo.com/)
- [Google Drive API Python](https://developers.google.com/drive/api/v3/quickstart/python)

## 📄 Licence

Ce projet est sous licence MIT.

## 👥 Contribution

Les contributions sont les bienvenues! Créez une issue ou une pull request.

---

**Note**: Ce projet nécessite des templates HTML complets pour fonctionner. Le frontend sera fourni séparément.