"""
Backend - MakeGroups V3 (Robuste et lisible)
--------------------------------------------
Fonctions pour charger, répartir, enregistrer, et gérer l'historique de groupes d'élèves par niveaux.
"""

from pathlib import Path
import pandas as pd
import os
import unicodedata
import re
import random

# ==============================================================================
# 0. Lecture et normalisation des fichiers d'élèves
# ==============================================================================

def read_csv_utf8_fallback(path):
    """
    Tente de lire un CSV en UTF-8, puis latin1 si une erreur Unicode survient.
    """
    try:
        return pd.read_csv(path, encoding='utf-8')
    except UnicodeDecodeError:
        return pd.read_csv(path, encoding='latin1')

def normaliser_colonnes(df):
    """
    Normalise les noms de colonnes :
    - Remplace 'é'/'É' par 'e'
    - Supprime les espaces en début/fin
    - Met en majuscule la première lettre
    """
    mapping = {col: col.replace('é', 'e').replace('É', 'E') for col in df.columns}
    mapping = {col: mapped_col.strip().capitalize() for col, mapped_col in mapping.items()}
    return df.rename(columns=mapping)

def charger_fichier(path):
    """
    Charge un fichier d'élèves (CSV ou Excel) dans un DataFrame pandas.
    - Accepte : .csv, .xlsx, .xls
    - Normalise les colonnes pour garantir 'Nom', 'Prenom', 'Classe', 'Niveau'
    - Remplit les valeurs manquantes par '' (chaine vide)
    - Renvoie le DataFrame prêt à l'emploi

    Paramètres :
        path (str) : chemin du fichier à charger

    Exceptions :
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
    try:
        df = open_funcs[ext](path)
    except Exception as e:
        raise ValueError(f"Erreur lors de la lecture du fichier {os.path.basename(path)} :\n{e}")
    df = normaliser_colonnes(df)
    expected = {'Nom', 'Prenom', 'Classe', 'Niveau'}
    if not expected.issubset(df.columns):
        raise ValueError(
            f"Le fichier doit contenir les colonnes suivantes : {expected}\n"
            f"Colonnes trouvées : {list(df.columns)}"
        )
    df.fillna('', inplace=True)
    return df

# ==============================================================================
# 1. Fonctions de gestion des groupes et périodes
# ==============================================================================

def compter_niveaux(df):
    """
    Retourne un dictionnaire {niveau: nombre d'élèves}.
    """
    return dict(df['Niveau'].value_counts().sort_index())

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

def generer_repartition_auto(df, nb_groupes):
    """
    Génère une répartition équilibrée automatique par niveau avec alternance.
    """
    niveaux = compter_niveaux(df)
    repartition = {}
    for i, (niveau, total) in enumerate(niveaux.items()):
        repartition[niveau] = repartir_niveau(total, nb_groupes, alternance_start=i)
    return repartition

def verifier_coherence_repartition(repartition, niveaux, nb_groupes):
    """
    Vérifie que la répartition par niveau est cohérente avec les effectifs attendus.
    """
    for niveau, valeurs in repartition.items():
        if len(valeurs) != nb_groupes:
            raise ValueError(f"Le niveau {niveau} doit avoir {nb_groupes} groupes.")
        if sum(valeurs) != niveaux[niveau]:
            raise ValueError(f"Répartition invalide pour le niveau {niveau}: somme = {sum(valeurs)}, attendu = {niveaux[niveau]}.")

def extraire_nom_classes(df):
    """
    Retourne un nom combiné des classes triées (ex : "601-602").
    """
    classes = sorted(str(x) for x in df['Classe'].unique())
    return "-".join(classes)

def normalize_str(s):
    """
    Supprime les accents, met en minuscule, enlève les espaces superflus.
    """
    if not isinstance(s, str):
        return s
    s = unicodedata.normalize('NFKD', s).encode('ascii', 'ignore').decode('utf-8')
    return s.lower().strip()

def detecter_prochaine_periode(df):
    """
    Détecte la prochaine période à créer à partir des colonnes du DataFrame,
    robustement (casse, accents, espaces...).
    """
    periodes = []
    for col in df.columns:
        col_norm = normalize_str(col)
        m = re.search(r"groupe\s*periode\s*(\d+)", col_norm)
        if m:
            periodes.append(int(m.group(1)))
    if periodes:
        return max(periodes) + 1
    else:
        return 1

def ajouter_groupes_au_df(df_original, groupes, chemin_csv, dossier_parent):
    """
    Ajoute une nouvelle colonne "Groupe Période X" au DataFrame original
    et sauvegarde le fichier dans un dossier du type "<nom_classes>_PériodeX".
    Retourne (chemin_dossier, nom_classes, periode)
    """
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

    nom_classes = extraire_nom_classes(df_original)
    nom_dossier = f"{nom_classes}_Période{periode}"
    dossier_complet = os.path.join(dossier_parent, nom_dossier)
    os.makedirs(dossier_complet, exist_ok=True)
    base_path = os.path.join(dossier_complet, f"{nom_classes}_Période{periode}")
    df_original.to_excel(f"{base_path}.xlsx", index=False)
    return dossier_complet, nom_classes, periode

def sauvegarder_groupes(groupes, dossier_sortie, nom_classes, periode):
    """
    Sauvegarde chaque groupe dans un fichier Excel, dans le dossier donné.
    Les noms suivent le schéma : <nom_classes>_GroupeX_PériodeY.xlsx
    """
    for i, g in enumerate(groupes, 1):
        base = os.path.join(dossier_sortie, f"{nom_classes}_Groupe{i}_Période{periode}")
        os.makedirs(os.path.dirname(base), exist_ok=True)
        g.to_excel(f"{base}.xlsx", index=False)

# ==============================================================================
# 2. Attribution des groupes en évitant les répétitions (priorité à la nouveauté)
# ==============================================================================

def historique_groupes_par_eleve(df):
    """
    Retourne pour chaque élève l'ensemble des groupes déjà faits (par période).
    Renvoie : {(nom, prenom, classe): set(num_groupes)}
    """
    histo = {}
    # Colonnes type "Groupe Periode X" ou "Groupe Période X"
    pattern = re.compile(r"groupe p[ée]riode ?(\d+)", re.IGNORECASE)
    groupe_cols = [col for col in df.columns if pattern.match(normalize_str(col))]
    for idx, row in df.iterrows():
        key = (row['Nom'], row['Prenom'], row['Classe'])
        groupes_faits = set()
        for col in groupe_cols:
            try:
                val = int(row[col])
                groupes_faits.add(val)
            except Exception:
                continue
        histo[key] = groupes_faits
    return histo

def choisir_groupe_possible(histo_eleve, quotas_restants, nb_groupes):
    """
    Retourne la liste des groupes possibles pour un élève : d’abord les groupes JAMAIS faits,
    puis ceux déjà faits (si besoin). Prend en compte les quotas restants.
    """
    groupes_jamais_faits = [g for g in range(1, nb_groupes + 1) if g not in histo_eleve and quotas_restants[g - 1] > 0]
    if groupes_jamais_faits:
        return groupes_jamais_faits
    # Sinon, retourne tous les groupes où il reste de la place
    return [g for g in range(1, nb_groupes + 1) if quotas_restants[g - 1] > 0]

def generer_groupes(df, nb_groupes, repartition):
    """
    Répartition qui tente d'éviter de remettre un élève dans un groupe déjà fait (priorité à la nouveauté).
    Si impossible (tous déjà faits ou groupes pleins), complète quand même.
    """
    histo = historique_groupes_par_eleve(df)
    groupes = [[] for _ in range(nb_groupes)]
    for niveau, quotas in repartition.items():
        eleves_niveau = df[df['Niveau'] == niveau].copy()
        eleves_niveau = eleves_niveau.sample(frac=1, random_state=None).reset_index(drop=True)
        quotas_restants = quotas.copy()
        for _, eleve in eleves_niveau.iterrows():
            key = (eleve['Nom'], eleve['Prenom'], eleve['Classe'])
            histo_eleve = histo.get(key, set())
            groupes_possibles = choisir_groupe_possible(histo_eleve, quotas_restants, nb_groupes)
            if groupes_possibles:
                grp = random.choice(groupes_possibles)
                groupes[grp - 1].append(eleve)
                quotas_restants[grp - 1] -= 1
            else:
                pass  # Sécurité
    return [pd.DataFrame(g) for g in groupes]
