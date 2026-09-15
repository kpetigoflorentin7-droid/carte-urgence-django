Système de badge d'accès

Ce projet est une petite application web créée avec Django.

Elle permet de créer un badge pour une personne avec ses informations personnelles et un QR code.

Informations enregistrées

Le badge contient :

Nom
Prénom
Date de naissance
Lieu de naissance
Nationalité
Photo
Groupe A ou B
Numéro de badge
Fonctionnement du QR code

Le QR code se trouve au verso du badge.

Lorsqu'il est scanné, le système vérifie le groupe de la personne et l'heure actuelle.

Minute paire → accès autorisé au groupe A
Minute impaire → accès autorisé au groupe B

Le système affiche ensuite :

ACCÈS AUTORISÉ ou ACCÈS REFUSÉ

Technologies utilisées
Python
Django
HTML
CSS
SQLite
QR Code
ReportLab pour le PDF
Installation

Créer et activer l'environnement virtuel :

python -m venv venv

Windows PowerShell :

venv\Scripts\Activate.ps1

Installer les dépendances :

pip install django qrcode pillow reportlab

Faire les migrations :

python manage.py makemigrations
python manage.py migrate

Lancer le projet :

python manage.py runserver

Puis ouvrir :

http://127.0.0.1:8000/
Auteur

KPETIGO Florentin
