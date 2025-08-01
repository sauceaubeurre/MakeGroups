"""
Interface graphique MakeGroups V3
----------------------------------
- UI moderne avec logo cliquable.
- Fonctionne avec le backend MakeGroups.py.
- Résumé rapide, aide utilisateur, pop-ups, etc.
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from PIL import Image, ImageTk
from tksheet import Sheet
import webbrowser
import os
import pandas as pd
from MakeGroups import (
    charger_fichier,
    compter_niveaux,
    generer_repartition_auto,
    generer_groupes,
    ajouter_groupes_au_df,
    sauvegarder_groupes,
    verifier_coherence_repartition,
    extraire_nom_classes,
)

# ==============================================================================
# Classe principale de l'application
# ==============================================================================

class Application(tk.Tk):
    def __init__(self):
        super().__init__()
        script_dir = os.path.dirname(os.path.abspath(__file__))
        self.iconbitmap(os.path.join(script_dir, "icone.ico"))
        self.title("Outil de suivi des groupes de besoins")
        self.state('zoomed')
        self.configure(bg="#F7F9FA")

        # Attributs principaux
        self.df = None
        self.chemin_fichier = ""
        self.niveaux = {}
        self.nb_groupes = 0
        self.entrees = {}            # {niveau: [Entry, ...]}
        self.logo_frame = None
        self.resume_label = None
        self.frame_saisie = None
        self.frame_boutons = None

        # Style global
        self.style = ttk.Style()
        self.style.theme_use('clam')
        self.style.configure("TButton", font=("Segoe UI", 11), padding=6)
        self.style.configure("TLabel", font=("Segoe UI", 11))
        self.style.configure("Title.TLabel", font=("Segoe UI", 15, "bold"), background="#F7F9FA")

        self.init_ui()

    # ==========================================================================
    # Initialisation interface : header/logo/bouton ouverture fichier
    # ==========================================================================

    def init_ui(self):
        self.logo_frame = tk.Frame(self, bg="#F7F9FA")
        self.logo_frame.pack(fill="x", pady=(20, 10))
        self.afficher_logo()

        titre = ttk.Label(self, text="Outil de suivi des groupes de besoins", style="Title.TLabel", background="#F7F9FA")
        titre.pack(side="top", pady=10)

        btn_ouvrir = ttk.Button(self, text="Ouvrir un fichier élèves (CSV/Excel)", command=self.ouvrir_fichier_eleves)
        btn_ouvrir.pack(pady=25)

    def afficher_logo(self):
        for widget in self.logo_frame.winfo_children():
            widget.destroy()
        try:
            script_dir = os.path.dirname(os.path.abspath(__file__))
            logo_labo_path = os.path.join(script_dir, "logo_labo.png")
            logo_college_path = os.path.join(script_dir, "logo_college.png")
            img_labo = Image.open(logo_labo_path).resize((360, 360), Image.Resampling.LANCZOS)
            img_college = Image.open(logo_college_path).resize((360, 360), Image.Resampling.LANCZOS)
            self.logo_labo_image = ImageTk.PhotoImage(img_labo)
            self.logo_college_image = ImageTk.PhotoImage(img_college)
            logo_labo_label = tk.Label(self.logo_frame, image=self.logo_labo_image, bg="#F7F9FA", cursor="hand2")
            logo_college_label = tk.Label(self.logo_frame, image=self.logo_college_image, bg="#F7F9FA", cursor="hand2")
        except Exception as e:
            print("Erreur lors de l'affichage du logo :", e)
            logo_labo_label = tk.Label(self.logo_frame, text="LOGO", bg="#F7F9FA", font=("Segoe UI", 17, "bold"), fg="#AAAAAA", cursor="hand2", width=10, height=6)
            logo_college_label = tk.Label(self.logo_frame, text="LOGO", bg="#F7F9FA", font=("Segoe UI", 17, "bold"), fg="#AAAAAA", cursor="hand2", width=10, height=6)
        logo_labo_label.pack(side="right", padx=25)
        logo_college_label.pack(side="left", padx=25)
        logo_college_label.bind("<Button-1>", lambda e: webbrowser.open_new_tab("https://etab.ac-reunion.fr/clg-cambuston/"))

    # ==========================================================================
    # Chargement du fichier élèves
    # ==========================================================================

    def ouvrir_fichier_eleves(self):
        chemin = filedialog.askopenfilename(
            filetypes=[
                ("Fichiers élèves (CSV, Excel)", "*.csv *.xlsx *.xls"),
                ("Tous les fichiers", "*.*"),
            ],
            title="Sélectionnez la liste d'élèves"
        )
        if not chemin:
            return
        try:
            self.df = charger_fichier(chemin)
            self.chemin_fichier = chemin
            self.niveaux = compter_niveaux(self.df)
            self.nb_classes = len(self.df['Classe'].unique())
            self.nb_groupes = self.nb_classes + 1
            self.afficher_resume()
            self.afficher_champs_repartition()
        except Exception as e:
            self.afficher_message("Erreur lors du chargement du fichier", str(e), type="error")

    # ==========================================================================
    # Affichage du résumé
    # ==========================================================================

    def afficher_resume(self):
        if self.resume_label:
            self.resume_label.destroy()
        resume = ""
        if self.df is not None:
            resume += f"🗂️ Fichier chargé : {os.path.basename(self.chemin_fichier)}\n"
            resume += f"👩‍🎓 Total élèves : {len(self.df)}\n"
            classes = sorted(self.df['Classe'].unique())
            resume += f"📚 Classes : {', '.join(str(c) for c in classes)}\n"
            resume += f"🔢 Niveaux détectés : "
            for niveau, eff in self.niveaux.items():
                resume += f"{niveau} ({eff} élèves), "
            resume = resume.rstrip(", ") + "\n"
            resume += f"🧩 Nombre de groupes à créer : {self.nb_groupes}\n"
        self.resume_label = tk.Label(self, text=resume, bg="#F7F9FA", font=("Segoe UI", 11), justify="left", anchor="w")
        self.resume_label.pack(pady=(0, 12), fill="x", padx=40)

    # ==========================================================================
    # Saisie et affichage des répartitions
    # ==========================================================================

    def afficher_champs_repartition(self):
        if self.frame_saisie:
            self.frame_saisie.destroy()
        self.frame_saisie = tk.Frame(self, bg="#F7F9FA")
        self.frame_saisie.pack(pady=10, padx=30, fill="x")

        help_text = ("Entrez le nombre d'élèves par niveau et par groupe.\n"
                     "Laissez les cases vides pour une répartition automatique.\n")
        ttk.Label(self.frame_saisie, text=help_text, style="TLabel", background="#F7F9FA").pack(pady=7)

        table = ttk.Frame(self.frame_saisie)
        table.pack()

        entetes = ["Effectif"] + [f"Groupe {i+1}" for i in range(self.nb_groupes)]
        for col, entete in enumerate(entetes):
            label = ttk.Label(table, text=entete, font=("Segoe UI", 11, "bold"), anchor="center")
            label.grid(row=0, column=col, padx=6, pady=5)

        self.entrees = {}
        for row, (niveau, effectif) in enumerate(self.niveaux.items(), 1):
            lbl = ttk.Label(table, text=f"Niveau {niveau} : {effectif} élève(s)", font=("Segoe UI", 11), anchor="center")
            lbl.grid(row=row, column=0, padx=5, pady=5)
            self.entrees[niveau] = []
            for col in range(self.nb_groupes - 1):
                entry = ttk.Entry(table, width=5, font=("Segoe UI", 11))
                entry.grid(row=row, column=col + 1, padx=3)
                self.entrees[niveau].append(entry)
            lbl_last = ttk.Label(table, text="(auto)", font=("Segoe UI", 10, "italic"), foreground="#888")
            lbl_last.grid(row=row, column=self.nb_groupes, padx=4)

        if self.frame_boutons:
            self.frame_boutons.destroy()
        self.frame_boutons = tk.Frame(self, bg="#F7F9FA")
        self.frame_boutons.pack(pady=(18, 8))
        btn_recap = ttk.Button(self.frame_boutons, text="Récapitulatif", command=self.afficher_recapitulatif)
        btn_recap.pack(side="left", padx=10)

    # ==========================================================================
    # Affichage du récapitulatif, édition des groupes
    # ==========================================================================

    def afficher_recapitulatif(self):
        try:
            # Détermination de la répartition selon la saisie utilisateur
            if all(all(not entry.get().strip() for entry in entrees) for entrees in self.entrees.values()):
                repartition = generer_repartition_auto(self.df, self.nb_groupes)
            else:
                repartition = {}
                for niveau, entrees in self.entrees.items():
                    total = self.niveaux[niveau]
                    vals, somme = [], 0
                    for entry in entrees:
                        txt = entry.get().strip()
                        if txt:
                            val = int(txt)
                            if val < 0 or val > total:
                                raise ValueError("Valeur incohérente !")
                            vals.append(val)
                            somme += val
                    restants = self.nb_groupes - len(vals)
                    base = (total - somme) // restants if restants > 0 else 0
                    surplus = (total - somme) % restants if restants > 0 else 0
                    for j in range(restants - 1):
                        vals.append(base + (1 if j < surplus else 0))
                    vals.append(total - sum(vals))
                    repartition[niveau] = vals

            verifier_coherence_repartition(repartition, self.niveaux, self.nb_groupes)
            groupes = generer_groupes(self.df, self.nb_groupes, repartition)

            # --- Fenêtre récap ---
            recap = tk.Toplevel(self)
            recap.title("Récapitulatif des groupes")
            recap.state('zoomed')
            recap.configure(bg="#F7F9FA")

            ttk.Label(recap, text="Tableau récapitulatif avant édition des groupes :", font=("Segoe UI", 13, "bold"), background="#F7F9FA").pack(pady=8)

            # Tableau effectif par groupe/niveau/classe
            colonnes = ["Groupe", "Effectif total"] + \
                       [f"Niveau {n}" for n in sorted(self.niveaux)] + \
                       [f"Classe {c}" for c in sorted(self.df['Classe'].unique())]

            tree = ttk.Treeview(recap, columns=colonnes, show="headings", height=len(groupes))
            for col in colonnes:
                tree.heading(col, text=col)
                tree.column(col, width=100, anchor="center")
            tree.pack(fill="x", padx=20, pady=10)

            for i, g in enumerate(groupes):
                ligne = [f"Groupe {i+1}", len(g)]
                for n in sorted(self.niveaux):
                    ligne.append(len(g[g["Niveau"] == n]))
                for c in sorted(self.df["Classe"].unique()):
                    ligne.append(len(g[g["Classe"] == c]))
                tree.insert("", "end", values=ligne)

            effectifs = [len(g) for g in groupes]
            warning = ""
            if min(effectifs) == 0:
                warning = "⚠️ Certains groupes sont vides !"
            elif max(effectifs) - min(effectifs) > 2:
                warning = "⚠️ Les groupes sont déséquilibrés."
            if warning:
                tk.Label(recap, text=warning, fg="#C75A4A", font=("Segoe UI", 11, "bold"), bg="#F7F9FA").pack(pady=8)

            # --- Tableaux d'édition (tksheet)
            edit_frame = tk.Frame(recap, bg="#F7F9FA")
            edit_frame.pack(fill="x", padx=15, pady=8)

            sheets = []
            group_data = []
            columns = ["Nom", "Prenom", "Niveau"]

            for g in groupes:
                df_g = g.sort_values(by="Nom").reset_index(drop=True)
                group_data.append(df_g)

            header_row = tk.Frame(edit_frame, bg="#F7F9FA")
            header_row.pack(fill="x")
            for idx in range(self.nb_groupes):
                tk.Label(header_row, text=f"Groupe {idx+1}", font=("Segoe UI", 12, "bold"), bg="#F7F9FA", width=45, anchor="center").pack(side="left", padx=15, pady=(0,4))

            table_row = tk.Frame(edit_frame, bg="#F7F9FA")
            table_row.pack(fill="x")

            for idx in range(self.nb_groupes):
                sheet = Sheet(table_row,
                              data=group_data[idx][columns].values.tolist(),
                              headers=columns,
                              width=450,
                              height=550)
                sheet.enable_bindings((
                    "single_select",
                    "row_select",
                    "arrowkeys",
                ))
                sheet.readonly_columns(columns=columns)
                sheet.extra_bindings("cell_edit", lambda *a, **kw: "break")
                sheet.grid(row=0, column=2*idx, padx=(0,0), pady=2)
                sheets.append(sheet)

                if idx < self.nb_groupes-1:
                    btns = tk.Frame(table_row, bg="#F7F9FA")
                    btns.grid(row=0, column=2*idx+1, sticky="ns", padx=2)
                    btn_right = ttk.Button(btns, text=">", width=3, command=lambda i=idx: transfer(i, i+1))
                    btn_left = ttk.Button(btns, text="<", width=3, command=lambda i=idx+1: transfer(i, i-1))
                    btn_right.pack(pady=2)
                    btn_left.pack(pady=2)

            def update_treeview():
                for row in tree.get_children():
                    tree.delete(row)
                for i, g in enumerate(group_data):
                    ligne = [f"Groupe {i+1}", len(g)]
                    for n in sorted(self.niveaux):
                        ligne.append(len(g[g["Niveau"] == n]))
                    for c in sorted(self.df["Classe"].unique()):
                        ligne.append(len(g[g["Classe"] == c]))
                    tree.insert("", "end", values=ligne)

            def transfer(src, dest):
                selected = sheets[src].get_selected_rows()
                if not selected:
                    return
                idx = list(selected)[0]
                row_vals = group_data[src].iloc[idx]
                # Supprimer du src
                group_data[src] = group_data[src].drop(idx).reset_index(drop=True)
                # Ajouter au dest
                group_data[dest] = pd.concat([group_data[dest], pd.DataFrame([row_vals])], ignore_index=True)
                # Trier les deux groupes
                group_data[src] = group_data[src].sort_values(by="Nom").reset_index(drop=True)
                group_data[dest] = group_data[dest].sort_values(by="Nom").reset_index(drop=True)
                # Mettre à jour l'affichage
                sheets[src].set_sheet_data(group_data[src][columns].values.tolist())
                sheets[dest].set_sheet_data(group_data[dest][columns].values.tolist())
                sheets[src].deselect("all")
                sheets[dest].deselect("all")
                update_treeview()

            # --- Boutons Valider/Retour
            btns = ttk.Frame(recap)
            btns.pack(pady=18)
            def valider_final():
                groupes_final = [df.copy() for df in group_data]
                dossier_complet = filedialog.askdirectory(
                    title="Choisissez le dossier où enregistrer les fichiers de groupes"
                )
                if not dossier_complet:
                    return
                try:
                    dossier_complet, nom_classes, periode = ajouter_groupes_au_df(
                        self.df, groupes_final, self.chemin_fichier, dossier_complet
                    )
                    sauvegarder_groupes(groupes_final, dossier_complet, nom_classes, periode)
                    recap.destroy()
                    self.afficher_message(
                        "Groupes créés avec succès",
                        f"Tous les fichiers ont été enregistrés dans le dossier :\n\n{dossier_complet}",
                        type="info"
                    )
                except Exception as e:
                    self.afficher_message("Erreur lors de la génération", str(e), type="error")

            ttk.Button(btns, text="Valider et Générer", command=valider_final).pack(side="left", padx=8)
            ttk.Button(btns, text="Retour", command=recap.destroy).pack(side="left", padx=8)

        except Exception as e:
            self.afficher_message("Erreur de saisie", str(e), type="error")

    # ==========================================================================
    # Messages pop-up : info, warning, erreur
    # ==========================================================================

    def afficher_message(self, titre, message, type="info"):
        if type == "info":
            messagebox.showinfo(titre, message)
        elif type == "warning":
            messagebox.showwarning(titre, message)
        elif type == "error":
            messagebox.showerror(titre, message)

# ==============================================================================
# Lancement de l'application
# ==============================================================================

if __name__ == "__main__":
    app = Application()
    app.mainloop()
