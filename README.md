# Outil de suivi des groupes de besoins

Outil Python graphique pour la répartition intelligente des élèves en groupes de besoins.

---

## Fonctionnalités principales

- **Interface graphique moderne** (Tkinter + TTK + tksheet)
- **Logo cliquable** : accès au site du collège
- **Ouverture de fichier CSV** élèves (colonnes : Classe, Nom, Prenom, Niveau)
- **Résumé instantané** après chargement (effectifs, niveaux, classes, groupes)
- **Saisie manuelle** de la répartition des effectifs par niveau/groupe
    - **Saisie facilitée** : laisse vide pour une répartition automatique et équilibrée
    - **Dernier groupe auto-rempli**
- **Récapitulatif avant génération**
    - **Tableau dynamique (Treeview)** avec : effectif par groupe, par niveau, par classe
    - **Avertissements** si groupes vides ou déséquilibrés
- **Édition manuelle avancée des groupes**
    - **Tableaux éditables** (tksheet) : visualisation par groupe
    - **Transfert d'élèves** entre groupes avec boutons “>” et “<”
    - **Treeview récapitulatif mis à jour en temps réel**
- **Génération de fichiers**
    - **Choix du dossier d’enregistrement** au moment de la génération
    - **Création d’un sous-dossier** `<classes>_PériodeX` automatique pour chaque période
    - **Export CSV & Excel** de chaque groupe + fichier enrichi
    - **Gestion automatique des périodes** (“Groupe Période 1”, “Groupe Période 2”…)
- **Réinitialisation rapide** de l’interface
- **Pop-ups d’erreur et de confirmation**  
- **Compatible .exe** (PyInstaller)

---

## Nouveautés & Améliorations

- **Choix du dossier d’enregistrement** (plus flexible)
- **Treeview d’effectif mis à jour en temps réel** lors des transferts
- **Code plus lisible et modulaire**
- **Aide utilisateur** (textes d’aide, erreurs plus explicites)
- **Contrôle de cohérence renforcé** (validation avant génération)

---

## Prérequis

- Python 3.10+  
- Modules : `pandas`, `openpyxl`, `pillow`, `tksheet`, `pyinstaller`

---

## Installation rapide

1. **Installer Python**  
    - Télécharger depuis [python.org](https://www.python.org/downloads/)  
    - Installer et cocher “Add Python to PATH” lors de l’installation

2. **Installer les modules nécessaires**  
    - Ouvrir un terminal (Win+R, puis `cmd`)  
    - Lancer :  
      ```
      pip install pandas pillow openpyxl tksheet
      ```

3. **Télécharger le programme**  
    - Aller sur le dépôt GitHub  
    - Cliquer sur Code > Download ZIP  
    - Décompresser le dossier

4. **Lancer le programme**  
    - Double-cliquer sur `MakeGroups_UI.py`

---

## Utilisation

1. **Ouvrir le fichier CSV** (doit comporter les colonnes : Classe, Nom, Prenom, Niveau)
2. **Consulter le résumé** affiché
3. **Choisir la répartition** :
    - Saisir le nombre d’élèves de chaque niveau par groupe
    - Laisser vide pour générer une répartition équilibrée automatiquement
4. **Cliquer sur “Récapitulatif”**
5. **Éditer les groupes si besoin** :
    - Utiliser les boutons pour transférer des élèves d’un groupe à l’autre
    - Observer la mise à jour en temps réel du tableau récapitulatif
6. **Valider et Générer**
    - Choisir le dossier d’enregistrement
    - Tous les fichiers sont générés dans un sous-dossier “<classes>_PériodeX”
7. **Réinitialiser** pour recommencer avec un nouveau fichier

---

## Personnalisation & astuces

- **Changer les logos** : remplacer les fichiers `logo_college.png` et `logo_labo.png`
- **Changer l’icône du programme** : remplacer `icone.ico`
- **Adapter les colonnes affichées** : modifier les listes “columns” dans le code

---

## FAQ

- **“Le programme ne se lance pas”**  
    Vérifiez que Python est bien installé et que tous les modules sont présents.

- **“Problème d’encodage”**  
    Utilisez toujours le format CSV UTF-8 (Excel : “Enregistrer sous > CSV UTF-8”).

---

