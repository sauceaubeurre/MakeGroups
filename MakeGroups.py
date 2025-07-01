# -*- coding: utf-8 -*-
"""
Backend - MakeGroups V3 (Robuste et lisible)
--------------------------------------------
Fonctions pour charger, répartir, enregistrer, et gérer l'historique de groupes d'élèves par niveaux.
"""

from pathlib import Path
import pandas as pd
import os
import re
from collections import defaultdict

def read_csv_utf8_fallback(path):
    """
    Tente de lire un CSV en UTF-8, puis latin1 si une erreur Unicode survient.
    """
    try:
        return pd.read_csv(path, encoding='utf-8')
    except UnicodeDecodeError:
        return pd.read_csv(path, encoding='latin1')

# ======================= 0. Normaliser les colonnes ============================
def normaliser_colonnes(df):
    """
    Normalise les noms de colonnes :
    - Remplace 'é'/'É' par 'e'
    - Enlève les espaces en début/fin
    - Met en majuscule la première lettre
    """
    mapping = {col: col.replace('é', 'e').replace('É', 'E') for col in df.columns}
    mapping = {col: mapped_col.strip().capitalize() for col, mapped_col in mapping.items()}
    return df.rename(columns=mapping)


# ======================= 1. Charger un fichier ============================
def charger_fichier(path):
    """
    Charge un fichier d'élèves (CSV ou Excel) dans un DataFrame pandas.
    - Accepte : .csv, .xlsx, .xls
    - Normalise les colonnes pour garantir 'Nom', 'Prenom', 'Classe', 'Niveau'
    - Remplit les valeurs manquantes par '' (chaine vide)
    - Renvoie le DataFrame prêt à l'emploi

    Paramètres :
        path (str) : chemin du fichier à charger

    Exceptions :
        ValueError si le format de fichier est incorrect ou si les colonnes sont absentes
    """
    ext = Path(path).suffix.lower()
    open_funcs = {
        '.csv': read_csv_utf8_fallback,
        '.xlsx': pd.read_excel,
        '.xls': pd.read_excel,
    }
    if ext not in open_funcs:
        raise ValueError(
            f"Format de fichier non pris en charge : {ext}\n"
            "Formats acceptés : .csv, .xlsx, .xls"
        )
    # Chargement du fichier via la bonne fonction
    try:
        df = open_funcs[ext](path)
    except Exception as e:
        raise ValueError(f"Erreur lors de la lecture du fichier {os.path.basename(path)} :\n{e}")
    df = normaliser_colonnes(df)
    # Vérification des colonnes attendues
    expected = {'Nom', 'Prenom', 'Classe', 'Niveau'}
    if not expected.issubset(df.columns):
        raise ValueError(
            f"Le fichier doit contenir les colonnes suivantes : {expected}\n"
            f"Colonnes trouvées : {list(df.columns)}"
        )
    df.fillna('', inplace=True)
    return df


# ======================= 2. Compter les niveaux ============================
def compter_niveaux(df):
    """
    Retourne un dictionnaire {niveau: nombre d'élèves}.
    """
    return dict(df['Niveau'].value_counts().sort_index())

# ======================= 3. Répartir un niveau avec alternance =================
def repartir_niveau(nb_eleves, nb_groupes, alternance_start=0):
    """
    Répartit nb_eleves équitablement dans nb_groupes avec alternance du surplus.
    Exemple : 10 élèves, 3 groupes => [4,3,3] puis [3,4,3] puis [3,3,4]...
    """
    base = nb_eleves // nb_groupes
    reste = nb_eleves % nb_groupes
    repartition = [base] * nb_groupes
    for i in range(reste):
        repartition[(i + alternance_start) % nb_groupes] += 1
    return repartition

# ======================= 4. Ajouter groupes au DataFrame =====================
def ajouter_groupes_au_df(df_original, groupes, chemin_csv, dossier_parent):
    """
    Ajoute une nouvelle colonne "Groupe Période X" au DataFrame original
    et sauvegarde le fichier dans un dossier du type "<nom_classes>_PériodeX".
    Retourne (chemin_dossier, nom_classes, periode)
    """
    # Déterminer la prochaine période
    periode = detecter_prochaine_periode(df_original)
    nouvelle_colonne = f"Groupe Période {periode}"

    df_original[nouvelle_colonne] = ""

    for i, groupe in enumerate(groupes):
        for _, eleve in groupe.iterrows():
            masque = (
                (df_original['Nom'] == eleve['Nom']) &
                (df_original['Prenom'] == eleve['Prenom']) &
                (df_original['Classe'] == eleve['Classe'])
            )
            df_original.loc[masque, nouvelle_colonne] = i + 1

    # Génération des noms/dossiers
    nom_classes = extraire_nom_classes(df_original)
    nom_dossier = f"{nom_classes}_Période{periode}"
    dossier_complet = os.path.join(dossier_parent, nom_dossier)
    os.makedirs(dossier_complet, exist_ok=True)

    # Sauvegarde du fichier enrichi
    base_path = os.path.join(dossier_complet, f"{nom_classes}_Période{periode}")
    df_original.to_csv(f"{base_path}.csv", index=False, sep=",")
    df_original.to_excel(f"{base_path}.xlsx", index=False)

    return dossier_complet, nom_classes, periode

# ======================= 5. Sauvegarder groupes =============================
def sauvegarder_groupes(groupes, dossier_sortie, nom_classes, periode):
    """
    Sauvegarde chaque groupe dans un fichier CSV et Excel, dans le dossier donné.
    Les noms suivent le schéma : <nom_classes>_GroupeX_PériodeY.[csv/xlsx]
    """
    for i, g in enumerate(groupes, 1):
        base = os.path.join(dossier_sortie, f"{nom_classes}_Groupe{i}_Période{periode}")
        os.makedirs(os.path.dirname(base), exist_ok=True)
        g.to_csv(f"{base}.csv", index=False, sep=",")
        g.to_excel(f"{base}.xlsx", index=False)

# ======================= 6. Générer groupes (attribution) ====================
def generer_groupes(df, nb_groupes, repartition):
    """
    Génère les groupes à partir d'une répartition validée :
    repartition = {niveau: [nb_groupe1, nb_groupe2, ...]}
    Retourne : liste de DataFrame (un par groupe)
    """
    groupes = [[] for _ in range(nb_groupes)]
    for niveau, quotas in repartition.items():
        eleves_niveau = df[df['Niveau'] == niveau].sample(frac=1).reset_index(drop=True)
        index = 0
        for i, quota in enumerate(quotas):
            groupes[i].extend(eleves_niveau.iloc[index:index+quota].to_dict('records'))
            index += quota
    return [pd.DataFrame(g) for g in groupes]

# ======================= 7. Répartition automatique ===========================
def generer_repartition_auto(df, nb_groupes):
    """
    Génère une répartition équilibrée automatique par niveau avec alternance.
    """
    niveaux = compter_niveaux(df)
    repartition = {}
    for i, (niveau, total) in enumerate(niveaux.items()):
        repartition[niveau] = repartir_niveau(total, nb_groupes, alternance_start=i)
    return repartition

# ======================= 8. Vérification cohérence ============================
def verifier_coherence_repartition(repartition, niveaux, nb_groupes):
    """
    Vérifie que la répartition par niveau est cohérente avec les effectifs attendus.
    """
    for niveau, valeurs in repartition.items():
        if len(valeurs) != nb_groupes:
            raise ValueError(f"Le niveau {niveau} doit avoir {nb_groupes} groupes.")
        if sum(valeurs) != niveaux[niveau]:
            raise ValueError(f"Répartition invalide pour le niveau {niveau}: somme = {sum(valeurs)}, attendu = {niveaux[niveau]}.")

# ======================= 9. Extraire nom des classes ==========================
def extraire_nom_classes(df):
    """
    Retourne un nom combiné des classes triées (ex : "601-602").
    """
    classes = sorted(str(x) for x in df['Classe'].unique())
    return "-".join(classes)

# ======================= 10. Détecter prochaine période =======================
def detecter_prochaine_periode(df):
    """Renvoie le numéro de la prochaine période à ajouter, debug inclut."""
    pattern = re.compile(r"Groupe P[ée]riode (\d+)")
    periodes = []
    for col in df.columns:
        m = pattern.match(col)
        if m:
            periodes.append(int(m.group(1)))
    if periodes:
        return max(periodes) + 1
    else:
        return 1



