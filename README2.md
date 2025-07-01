MakeGroups : Outil graphique pour la gestion intelligente et équitable des groupes d’élèves par période

📚 Présentation

MakeGroups est une application Python avec interface graphique qui permet à tout enseignant ou établissement de :

    Charger des listes d’élèves (CSV ou Excel)

    Répartir automatiquement ou manuellement les élèves en groupes selon différents niveaux et classes

    Prendre en compte l’historique : chaque élève fait le tour des groupes sur l’année scolaire (système de rotation prioritaire)

    Visualiser, éditer et exporter les groupes pour chaque période (au format Excel, CSV)

    Suivre l’historique de chaque élève sur toutes les périodes

L’outil se veut simple, moderne, robuste et personnalisable.

🚀 Fonctionnalités principales

    Chargement de fichiers CSV ou Excel (.csv, .xlsx, .xls)

    Détection automatique des classes, niveaux, effectifs

    Répartition automatique ou personnalisée des élèves en groupes

    Prise en compte de l’historique : évite de remettre un élève dans un groupe déjà fait

    Interface graphique intuitive : logo cliquable, résumé instantané, pop-ups, tableaux éditables

    Exportation de tous les groupes et de l’historique au format Excel, par période et par classe/groupe

    Robustesse : gestion des noms, accents, espaces, fichiers Excel mal encodés, etc.

🖥️ Pré-requis et installation
1. Python

    Python 3.8 ou supérieur recommandé

    Télécharger Python ici : https://www.python.org/downloads/

2. Dépendances

Installer les librairies nécessaires avec :

pip install -r requirements.txt

3. Git

	Télécharger Git ici : https://git-scm.com/downloads

4. Cloner ou télécharger le projet

	Sur une invite de commande : git clone https://github.com/sauceaubeurre/MakeGroups

📁 Structure du projet

MakeGroups/
│
├── MakeGroups.py         # Backend principal (logique, traitement, gestion fichiers)
├── MakeGroups_UI.py      # Interface graphique (frontend)
├── logo_labo.png         # Logo laboratoire
├── logo_college.png      # Logo établissement
├── icone.ico             # Icône de l’application
├── README.md             # Ce fichier
├── exemples/
│    └── eleves_exemple.csv   # Exemple de fichier d’élèves
└── ... autres fichiers éventuels

⚡ Utilisation

Lancement de l’interface graphique

python MakeGroups_UI.py

    Cliquez sur "Ouvrir un fichier élèves"

    Choisissez votre fichier CSV ou Excel d’élèves (exemple fourni dans exemples/)

    Vérifiez le résumé, ajustez éventuellement les répartitions manuellement

    Cliquez sur Récapitulatif pour vérifier et éditer les groupes

    Validez : tous les groupes sont exportés dans un dossier créé pour la période

Format du fichier élèves attendu

Le fichier doit contenir au minimum les colonnes suivantes (dans n’importe quel ordre ou casse) :

    Nom (ou nom)

    Prenom (ou prénom)

    Classe

    Niveau

    Les accents et espaces sont automatiquement corrigés.

Exemple :

Nom,Prénom,Classe,Niveau
Durand,Lucas,601,6
Leroy,Sarah,601,6
...

💡 Fonctionnement en bref

    La première période génère les groupes de façon équilibrée et aléatoire

    Les périodes suivantes : l’algorithme essaie en priorité d’éviter de remettre chaque élève dans un groupe déjà fait lors des périodes précédentes (mais ce n’est pas bloquant si impossible)

    Toutes les affectations et exports se font dans des dossiers nommés 601-602_Période1, etc.

    Les fichiers d’historique et de groupes sont sauvegardés en Excel (et CSV pour chaque groupe si besoin)

🛠️ Personnalisation / Avancées possibles

    Ajout d’un suivi de progression individuel (stats élève)

    Gestion d’autres critères (fille/garçon, options, …)

    Prise en charge de formats de fichiers supplémentaires

📝 Auteurs

    Développé par Romain SEUSSE

    Contact : romain.seusse@gmail.com