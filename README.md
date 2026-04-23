# 📖 Bibliothèque de Recettes Familiales

Application web complète développée avec le framework Django dans le cadre du projet de fin de session.  
Elle permet aux utilisateurs de partager, consulter et gérer leurs recettes de cuisine préférées dans un environnement sécurisé et élégant.

---

## 🌐 Accès en ligne

| Ressource | Lien |
|-----------|------|
| Application déployée | [https://jwj.pythonanywhere.com/](https://jwj.pythonanywhere.com/) |
| Dépôt GitHub | [https://github.com/JWJonathan/LOG3300_Projet_Final](https://github.com/JWJonathan/LOG3300_Projet_Final) |
| Vidéo de démonstration | [https://drive.google.com/file/d/xxxxx/view](https://drive.google.com/file/d/xxxxx/view) |

---

## 📝 Description du projet

Le **Livre de Recettes Familiales** est une plateforme collaborative où les passionnés de cuisine peuvent :

- 🍳 **Publier** leurs recettes personnelles avec photos, ingrédients et étapes détaillées
- 🔍 **Rechercher** et filtrer les recettes par catégorie ou mot-clé
- 👤 **Gérer** leur propre collection de recettes (modification, suppression)
- 🔒 **Protéger** leur contenu grâce à un système d'authentification et d'autorisations

L'application met en œuvre tous les concepts fondamentaux du développement web moderne :  
opérations CRUD, authentification, autorisations granulaires, design responsive et déploiement cloud.

---

## 🎯 Fonctionnalités principales

### ✅ Fonctionnalités obligatoires (cahier des charges)

| Fonctionnalité | Statut | Détail |
|---------------|--------|--------|
| Création de recettes | ✅ | Formulaire complet avec validation des données |
| Lecture (liste et détail) | ✅ | Pagination, recherche textuelle, filtrage par catégorie |
| Mise à jour | ✅ | Réservée à l'auteur de la recette uniquement |
| Suppression | ✅ | Réservée à l'auteur, avec confirmation |
| Authentification | ✅ | Connexion, déconnexion, inscription |
| Autorisations | ✅ | `UserPassesTestMixin` pour restreindre l'accès |
| Design CSS moderne | ✅ | Bootstrap 5 avec composants responsives |
| Base de données | ✅ | SQLite (développement) / MySQL (production) |

### 🌟 Fonctionnalités supplémentaires

- 🖼️ **Upload d'images** pour illustrer les recettes
- 📊 **Pagination** des listes (9 ou 12 éléments par page)
- 🏷️ **Catégories** : Entrées, Plats, Desserts, Boissons, Brunchs
- ⏱️ **Temps total** calculé automatiquement (préparation + cuisson)
- 📱 **Design entièrement responsive** (mobile, tablette, desktop)
- 🔔 **Messages de confirmation** après chaque action (succès, erreur)
- 🛡️ **Protection CSRF** sur tous les formulaires
- ⚡ **Optimisation des requêtes** : `select_related` et `prefetch_related`

---

## 🏗️ Architecture du projet
LOGT3300_Projet_Final/
│
├── config/ # Configuration principale Django
│ ├── settings.py
│ ├── urls.py
│ └── wsgi.py
│
├── users/ # Application de gestion des utilisateurs
│ ├── models.py # Modèle User personnalisé (si nécessaire)
│ ├── views.py # Vues d'authentification
│ ├── forms.py # Formulaires login/register
│ └── urls.py
│
├── recipes/ # Application principale de recettes
│ ├── models.py # Modèles Category et Recipe
│ ├── views.py # Vues CRUD avec permissions
│ ├── forms.py # Formulaire RecipeForm
│ ├── admin.py # Interface d'administration personnalisée
│ └── urls.py # Routes de l'application
│
├── templates/ # Templates HTML
│ ├── base.html # Layout principal avec Bootstrap
│ └── recipes/ # Templates spécifiques
│ ├── recipe_list.html
│ ├── recipe_detail.html
│ ├── recipe_form.html
│ ├── recipe_confirm_delete.html
│ ├── user_recipe_list.html
│ └── category_detail.html
│
├── media/ # Fichiers uploadés (images)
├── static/ # Fichiers statiques (CSS, JS)
├── requirements.txt # Dépendances Python
├── manage.py # Script de gestion Django
└── README.md # Ce fichier

text

---

## 🗃️ Modèle de données

### Category (Catégorie)

| Champ | Type | Description |
|-------|------|-------------|
| `name` | CharField(100) | Nom unique de la catégorie |
| `description` | TextField | Description optionnelle |
| `slug` | SlugField(100) | Identifiant URL auto-généré |

### Recipe (Recette)

| Champ | Type | Description |
|-------|------|-------------|
| `title` | CharField(200) | Titre de la recette |
| `slug` | SlugField(200) | Identifiant URL unique |
| `author` | ForeignKey → User | Auteur de la recette |
| `category` | ForeignKey → Category | Catégorie (optionnelle) |
| `description` | TextField | Résumé de la recette |
| `ingredients` | TextField | Liste des ingrédients |
| `steps` | TextField | Étapes de préparation |
| `prep_time` | PositiveIntegerField | Temps de préparation (min) |
| `cook_time` | PositiveIntegerField | Temps de cuisson (min) |
| `servings` | PositiveIntegerField | Nombre de portions |
| `difficulty` | CharField(10) | Facile / Moyen / Difficile |
| `image` | ImageField | Photo du plat (optionnelle) |
| `created_at` | DateTimeField | Date de création |
| `updated_at` | DateTimeField | Dernière modification |

---

## 🔒 Sécurité et autorisations

| Action | Utilisateur non connecté | Utilisateur connecté | Auteur de la recette |
|--------|--------------------------|----------------------|----------------------|
| Voir la liste des recettes | ✅ | ✅ | ✅ |
| Voir le détail d'une recette | ✅ | ✅ | ✅ |
| Créer une recette | ❌ | ✅ | N/A |
| Modifier une recette | ❌ | ❌ | ✅ |
| Supprimer une recette | ❌ | ❌ | ✅ |
| Voir "Mes Recettes" | ❌ | ✅ | ✅ |

---

## 🛠️ Installation en local

### Prérequis

- Python 3.10 ou supérieur
- pip (gestionnaire de paquets Python)
- Git (optionnel)

### Étapes

```bash
# 1. Cloner le dépôt
git clone https://github.com/votre-username/livre-recettes-familiales.git
cd livre-recettes-familiales

# 2. Créer un environnement virtuel
python -m venv venv
source venv/bin/activate      # Linux/Mac
# ou
venv\Scripts\activate         # Windows

# 3. Installer les dépendances
pip install -r requirements.txt

# 4. Appliquer les migrations
python manage.py migrate

# 5. Charger les données initiales (catégories prédéfinies)
python manage.py loaddata initial_data.json

# 6. Créer un super-utilisateur (admin)
python manage.py createsuperuser

# 7. Lancer le serveur de développement
python manage.py runserver

# 8. Accéder à l'application
# Site public : http://127.0.0.1:8000
# Administration : http://127.0.0.1:8000/admin
🚀 Déploiement sur PythonAnywhere
Créer un compte sur pythonanywhere.com

Cloner le dépôt depuis GitHub dans l'onglet "Consoles"

Créer un environnement virtuel et installer les dépendances

Configurer l'application web :

Framework : Django

Version Python : 3.12

WSGI configuration file : adapter le chemin

Configurer la base de données MySQL dans les paramètres

Appliquer les migrations et collecter les fichiers statiques

Redémarrer l'application

👨‍💻 Technologies utilisées
Technologie	Usage
Django 6.0	Framework principal
Bootstrap 5	Design responsive
Bootstrap Icons	Icônes vectorielles
Pillow	Gestion des images
SQLite / MySQL	Base de données
PythonAnywhere	Hébergement cloud
📹 Vidéo de démonstration
La démonstration couvre les points suivants :

Navigation sur la page d'accueil (recettes publiques)

Tentative d'accès à une page protégée → Redirection vers login

Inscription et connexion d'un utilisateur

Création d'une nouvelle recette avec upload d'image

Modification et sauvegarde d'une recette existante

Suppression d'une recette avec confirmation

Preuve de sécurité : connexion avec un autre compte → impossible de modifier les recettes d'autrui

📄 Licence
Projet réalisé dans le cadre académique du cours LOG3300 - Développement Web
Institut des Sciences, des Technologies et des Études Avancées d'Haïti (ISTEAH)
Session : Hiver 2026

👤 Auteur
Nom : Williams Jonathan JUSNE

Cours : LOG3300 - Développement Web

Professeur : Jean Kenel Dessources

Contact : isteah.jwjusne@gmail.com

« La cuisine, c'est l'art de transformer des ingrédients simples en souvenirs inoubliables. »

Ce projet est le fruit de l'apprentissage des technologies web modernes et de la mise en pratique des bonnes pratiques de développement.