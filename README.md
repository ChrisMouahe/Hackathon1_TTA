# Fitness Tracker IA

## 1. Description du projet

Fitness Tracker IA est une application Python permettant de suivre les activités sportives des utilisateurs, d'analyser leurs performances et de générer des recommandations personnalisées grâce à l'analyse de données.

Le projet simule des données d'entraînement réalistes, introduit volontairement des anomalies (valeurs manquantes, doublons, valeurs aberrantes) puis applique des techniques de nettoyage, de visualisation et d'analyse statistique afin d'aider les utilisateurs à améliorer leurs performances sportives.

---

## 2. Technologies utilisées

* Python 3.12+
* Pandas
* NumPy
* SciPy
* Matplotlib
* JSON
* Git & GitHub

---

## 3. Installation et exécution

### Cloner le projet

```bash
git clone https://github.com/votre-utilisateur/fitness-tracker-ia.git
cd fitness-tracker-ia
```

### Installer les dépendances

```bash
pip install pandas numpy scipy matplotlib
```

### Lancer l'application

```bash
python main.py
```

---

## 4. Structure du projet

```text
fitness-tracker-ia/
│
├── main.py
├── models.py
├── data_manager.py
├── workout_generator.py
├── scipy_analysis.py
├── visualizations.py
│
├── data/
│   ├── sessions.json
│   └── users.json
│
└── README.md
```

---

## 5. Fonctionnalités principales

### Gestion des utilisateurs

* Inscription de nouveaux utilisateurs
* Connexion à un compte existant
* Stockage des profils utilisateurs dans un fichier JSON

### Génération de données

* Création de données d'activités sportives simulées
* Génération de plusieurs utilisateurs
* Création d'un dataset réaliste sur plusieurs jours

### Qualité des données

* Introduction volontaire de données manquantes
* Introduction de valeurs aberrantes
* Création de doublons
* Nettoyage automatique du dataset

### Recommandations personnalisées

* Recommandation de séances adaptées au profil utilisateur
* Recommandation basée sur l'historique des activités

### Analyse statistique

* Analyse hebdomadaire des performances
* Test ANOVA
* Régression linéaire
* Test t apparié

### Visualisation

* Fréquence des entraînements
* Progression hebdomadaire
* Évolution des calories brûlées
* Génération automatique des graphiques

### Historique utilisateur

* Consultation de l'historique personnel des séances
* Suivi des performances dans le temps

---

## 6. Jeu de données

Le projet utilise deux fichiers JSON :

### users.json

Contient les informations des utilisateurs :

* user_id
* name
* age
* gender
* weight
* height
* goal

### sessions.json

Contient les informations des séances d'entraînement :

* user_id
* date
* workout_type
* duration
* intensity
* calories
* steps

---

## 7. Objectifs pédagogiques

Ce projet permet de pratiquer :

* La programmation orientée objet en Python
* La manipulation de données avec Pandas
* Le nettoyage de données
* L'analyse statistique avec SciPy
* La visualisation de données avec Matplotlib
* La gestion de fichiers JSON
* La conception d'un mini système de recommandation

---

## 8. Membres de l'équipe

| Nom                         | Rôle                                            |
| --------------------------  | ----------------------------------------------- |
| KOUAKOU Mouahé Chrisostome  | JSON,Pandas, Data Analysis & Intégration finale |
| YAO N'Guessan Lyld Rachelle | Clases POO, Moteur IA & Visualisation           |

---

## 9. Perspectives d'amélioration

* Interface graphique (Tkinter, Streamlit ou Web)
* Authentification sécurisée
* Base de données SQLite ou PostgreSQL
* Tableau de bord interactif
* Modèle de Machine Learning pour les recommandations avancées
* Déploiement Cloud

```
```