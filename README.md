# CMEV – Gestion de clinique

Application de bureau (Python / Tkinter / SQLite) pour gérer une clinique :
patients, médecins, employés, consultations, examens, pharmacie, facturation,
statistiques et administration.

> ⚠️ Projet en cours de refonte. Cette version est un prototype d'apprentissage :
> elle ne doit pas être utilisée en production avec de vraies données de patients
> sans renforcement de la sécurité (voir « Limites connues »).

## Fonctionnalités

- 9 modules : Patients, Médecins, Employés, Consultations, Examens, Pharmacie,
  Facturation, Statistiques, Administration
- 5 rôles : `super_admin`, `admin`, `medecin`, `receptionniste`, `pharmacien`
- Permissions par rôle et code de validation quotidien (4 chiffres) pour les
  modifications et suppressions sensibles
- Journal d'activité et sauvegarde de la base depuis l'interface
- Thèmes sombre / clair

## Lancer l'application

Prérequis : Python 3 avec Tkinter (inclus par défaut sur Windows).

```bash
py CMEV_FINAL.py
```

Au premier lancement, la base `cmev.db` est créée automatiquement, ainsi qu'un
compte administrateur de démonstration (voir le code). **Changez son mot de passe
immédiatement.**

## Créer un exécutable Windows

```bash
py -m pip install pyinstaller
py -m PyInstaller --onefile --windowed --name "CMEV" --clean CMEV_FINAL.py
```

## Limites connues

- Mots de passe stockés en clair dans la base (à remplacer par un hachage)
- Compte de démonstration défini dans le code
- Base SQLite locale : pas de partage fiable entre plusieurs postes
- Tout le code est dans un seul fichier

## Suite du projet

Une nouvelle version, web et personnalisable (FastAPI, PostgreSQL, React),
est prévue.
