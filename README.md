# MakeGroups V3

## 📋 Présentation

**MakeGroups V3** est un outil Python permettant de répartir automatiquement les élèves en groupes, à partir d’un fichier CSV.
L’interface graphique est simple et intuitive, conçue pour tous les enseignants, même sans compétences informatiques.

---

## 🚀 Installation rapide

> Pour plus de détails, voir le guide d’installation fourni.

1. **Installer Python**

   Télécharger et installer la dernière version sur [python.org](https://www.python.org/downloads/)

   > ⚠️ N’oubliez pas de cocher **Add Python to PATH** à l’installation.

2. **Installer les modules nécessaires**

   Ouvrir l’invite de commande (`Windows + R` → `cmd`) et taper : 

   ```
   pip install pandas pillow openpyxl pyinstaller
   ```

3. **Télécharger le programme**

   * Aller sur la page GitHub du projet : https://github.com/sauceaubeurre/MakeGroups
   * Cliquer sur **Code > Download ZIP**
   * Décompresser le ZIP dans un dossier

4. **Lancer le programme**

   Double-cliquer sur `MakeGroups_UI.py`
   
Tu peux aussi générer un .exe pour pouvoir lancer ton logiciel sur un PC qui n'a pas Python d'installé :
	-> Exécute le script `EXE_Generator.cmd`
---

## 🖥️ Utilisation

1. **Ouvrir un fichier CSV**

   Le programme attend un fichier CSV avec les colonnes suivantes :

   * `Classe`
   * `Nom`
   * `Prenom`
   * `Niveau`
     Le séparateur doit être **la virgule** (`,`).

2. **Renseigner ou non la répartition des élèves**

   * Tu peux indiquer, pour chaque niveau, le nombre d’élèves dans chaque groupe (sauf le dernier, complété automatiquement)
   * Ou laisser vide pour une répartition équilibrée automatique

3. **Récapitulatif**

   Une fenêtre te montre la composition des groupes avant validation.

4. **Enregistrement**

   Choisis le dossier où seront enregistrés tous les fichiers générés (groupes, fichier enrichi, etc.).

---

## 📑 Exemple de fichier CSV attendu

```csv
Classe,Nom,Prenom,Niveau
601,DUPONT,Alice,2
602,MARTIN,Hugo,3
601,LEMAIRE,Sarah,4
...
```

---

## ℹ️ Astuces et conseils

* Tu peux regénérer des groupes autant de fois que tu veux avec le fichier généré précédemment : chaque génération ajoute une colonne “Groupe Période X”.
* Les groupes sont équilibrés automatiquement si aucune case n’est renseignée lors de la saisie.
* Le logo en haut de la fenêtre est cliquable pour accéder au site de l’établissement.

---