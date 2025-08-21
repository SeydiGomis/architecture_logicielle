#  Gestion d’emprunts de livres (Architecture microservices)

Ce projet est une application de gestion des emprunts de livres développée avec **Django** et **Django REST Framework**, en adoptant une architecture **basée sur deux microservices** distincts : un pour la gestion du **catalogue de livres**, et un pour la gestion des **emprunts** et des **utilisateurs**.

---

##  Fonctionnalités principales

###  Côté utilisateur
-  Consulter la **liste des livres disponibles**.
-  Voir les **détails d’un livre**.
-  Faire une demande d’**emprunt**.
-  Consulter ses **emprunts en cours**.
-  S’inscrire et se connecter.

###  Côté administrateur
-  Ajouter, modifier, supprimer des livres.
-  Gérer les utilisateurs.
- Suivre les emprunts.

---

##  Architecture

Le projet est organisé en **2 services indépendants** :

###  Catalogue Service (`catalogue_service/`)
- API exposée : `/api/books/`
- Interface web : `/catalogue/`
- Gestion des **livres**.

### Emprunt Service (`emprunt_service/`)
- API exposée : `/api/loans/`
- Interfaces web :  
  - `/mes-emprunts/` → liste des emprunts  
  - `/mes-emprunts/<id>/` → détail d’un emprunt  
  - `/nouveau/<id>/` → nouvel emprunt
- Gestion des **emprunts** et de l’**authentification**.

Chaque service possède **sa propre base de données** et peut être lancé indépendamment.

---

## Installation et utilisation

###  Cloner le projet
```bash
git clone https://github.com/<ton-utilisateur>/<ton-repo>.git
cd <ton-repo>
###  pour acceder au serveur de catalogue

cd catalogue_service
python manage.py migrate
python manage.py runserver 8001
#Accéder à : http://127.0.0.1:8001/catalogue/

###  pour acceder au serveur de emprunt
cd emprunt_service
python manage.py migrate
python manage.py runserver 8002
# Acceder à : Accéder à : http://127.0.0.1:8002/mes-emprunts/
