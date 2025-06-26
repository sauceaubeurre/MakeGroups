# -*- coding: utf-8 -*-
"""
Interface graphique MakeGroups V3
----------------------------------
- UI moderne avec logo cliquable.
- Fonctionne avec le backend MakeGroups.py.
- Résumé rapide, aide utilisateur, pop-ups, etc.
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, simpledialog
from PIL import Image, ImageTk
import webbrowser
import os
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

class Application(tk.Tk):
    def __init__(self):
        super().__init__()
        script_dir = os.path.dirname(os.path.abspath(__file__))
        self.iconbitmap(os.path.join(script_dir, "icone.ico"))
        self.title("Outil de suivi des groupes de besoins")
        self.state('zoomed')  # Plein écran au démarrage
        self.configure(bg="#F7F9FA")

        self.df = None
        self.chemin_fichier = ""
        self.niveaux = {}
        self.nb_groupes = 0
        self.entrees = {}  # {niveau: [Entry, ...]}
        self.logo_image = None
        self.logo_frame = None
        self.resume_label = None
        self.frame_saisie = None
        self.frame_boutons = None

        self.style = ttk.Style()
        self.style.theme_use('clam')
        self.style.configure("TButton", font=("Segoe UI", 11), padding=6)
        self.style.configure("TLabel", font=("Segoe UI", 11))
        self.style.configure("Title.TLabel", font=("Segoe UI", 15, "bold"), background="#F7F9FA")

        self.init_ui()

    def init_ui(self):
        """Crée le header avec logo et le bouton d'ouverture de fichier."""
        self.logo_frame = tk.Frame(self, bg="#F7F9FA")
        self.logo_frame.pack(fill="x", pady=(20, 10))
        self.afficher_logo()

        titre = ttk.Label(self, text="Création des groupes de 6e", style="Title.TLabel", background="#F7F9FA")
        titre.pack()

        btn_ouvrir = ttk.Button(self, text="Ouvrir un fichier CSV", command=self.ouvrir_fichier_csv)
        btn_ouvrir.pack(pady=25)

    def afficher_logo(self):
        for widget in self.logo_frame.winfo_children():
            widget.destroy()
        try:
            script_dir = os.path.dirname(os.path.abspath(__file__))
            logo_labo_path = os.path.join(script_dir, "logo_labo.png")
            logo_college_path = os.path.join(script_dir, "logo_college.png")
            img_labo = Image.open(logo_labo_path)
            img_college = Image.open(logo_college_path)
            img_labo = img_labo.resize((120, 120), Image.Resampling.LANCZOS)
            img_college = img_college.resize((120, 120), Image.Resampling.LANCZOS)
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

    def ouvrir_fichier_csv(self):
        """Ouvre un fichier CSV et affiche le résumé dans l'interface."""
        chemin = filedialog.askopenfilename(
            filetypes=[("Fichier CSV", "*.csv")],
            title="Sélectionnez la liste d'élèves"
        )
        if not chemin:
            return
        try:
            self.df = charger_fichier(chemin)
            self.chemin_fichier = chemin
            self.niveaux = compter_niveaux(self.df)
            self.nb_classes = len(self.df['Classe'].unique())
            self.nb_groupes = self.nb_classes+1
            self.afficher_resume()
            self.afficher_champs_repartition()
        except Exception as e:
            self.afficher_message("Erreur lors du chargement", str(e), type="error")

    def afficher_resume(self):
        """Affiche le résumé rapide du fichier chargé."""
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
        self.resume_label.pack(pady=(0,12), fill="x", padx=40)

    def afficher_champs_repartition(self):
        """Affiche les champs de saisie pour chaque niveau/groupe."""
        if self.frame_saisie:
            self.frame_saisie.destroy()
        self.frame_saisie = tk.Frame(self, bg="#F7F9FA")
        self.frame_saisie.pack(pady=10, padx=30, fill="x")

        help_text = ("Entrez le nombre d'élèves par niveau et par groupe.\n"
                     "Laissez les cases vides pour une répartition automatique.\n")
        ttk.Label(self.frame_saisie, text=help_text, style="TLabel", background="#F7F9FA").pack(pady=7)

        # Création du tableau
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
            for col in range(self.nb_groupes - 1):  # Saisie pour tous sauf le dernier
                entry = ttk.Entry(table, width=5, font=("Segoe UI", 11))
                entry.grid(row=row, column=col + 1, padx=3)
                self.entrees[niveau].append(entry)
            lbl_last = ttk.Label(table, text="(auto)", font=("Segoe UI", 10, "italic"), foreground="#888")
            lbl_last.grid(row=row, column=self.nb_groupes, padx=4)
        
        # Boutons
        if self.frame_boutons:
            self.frame_boutons.destroy()
        self.frame_boutons = tk.Frame(self, bg="#F7F9FA")
        self.frame_boutons.pack(pady=(18,8))
        btn_recap = ttk.Button(self.frame_boutons, text="Récapitulatif", command=self.afficher_recapitulatif)
        btn_recap.pack(side="left", padx=10)
        btn_reset = ttk.Button(self.frame_boutons, text="Réinitialiser", command=self.reinitialiser_interface)
        btn_reset.pack(side="left", padx=10)

    def afficher_recapitulatif(self):
        """Affiche le récapitulatif des groupes par niveau et classe, avant génération."""
        try:
            # Si toutes les cases sont vides => répartit automatiquement avec le backend
            if all(all(not entry.get().strip() for entry in entrees) for entrees in self.entrees.values()):
                repartition = generer_repartition_auto(self.df, self.nb_groupes)
            else:
                repartition = {}
                for i, (niveau, entrees) in enumerate(self.entrees.items()):
                    total = self.niveaux[niveau]
                    vals = []
                    somme = 0
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
                    for j in range(restants-1):
                        vals.append(base + (1 if j < surplus else 0))
                    vals.append(total - sum(vals))
                    repartition[niveau] = vals

            verifier_coherence_repartition(repartition, self.niveaux, self.nb_groupes)
            groupes = generer_groupes(self.df, self.nb_groupes, repartition)

            # Création de la fenêtre récap
            recap = tk.Toplevel(self)
            recap.title("Récapitulatif des groupes")
            recap.state('zoomed')
            recap.configure(bg="#F7F9FA")

            ttk.Label(recap, text="Tableau récapitulatif avant génération des groupes :", font=("Segoe UI", 13, "bold"), background="#F7F9FA").pack(pady=8)
            for i, g in enumerate(groupes):
                resume = f"Groupe {i+1} : {len(g)} élèves  |  "
                niveaux_liste = [f"Niveau {n} : {len(g[g['Niveau']==n])} élève(s)" for n in sorted(self.niveaux)]
                resume += " / ".join(niveaux_liste)
                classes_liste = [f"Classe {c} : {len(g[g['Classe']==c])}élève(s)" for c in sorted(self.df['Classe'].unique())]
                resume += "  |  " + " / ".join(classes_liste)
                lbl = ttk.Label(recap, text=resume, background="#F7F9FA")
                lbl.pack(anchor="w", padx=15)

            warning = ""
            effectifs = [len(g) for g in groupes]
            if min(effectifs) == 0:
                warning = "⚠️ Certains groupes seront vides !"
            elif max(effectifs) - min(effectifs) > 2:
                warning = "⚠️ Les groupes sont déséquilibrés."
            if warning:
                tk.Label(recap, text=warning, fg="#C75A4A", font=("Segoe UI", 11, "bold"), bg="#F7F9FA").pack(pady=8)
            
            btns = ttk.Frame(recap)
            btns.pack(pady=18)
            ttk.Button(btns, text="Valider et Générer", command=lambda: self.generer_groupes_et_sauvegarder(repartition, recap)).pack(side="left", padx=8)
            ttk.Button(btns, text="Retour", command=recap.destroy).pack(side="left", padx=8)

        except Exception as e:
            self.afficher_message("Erreur de saisie", str(e), type="error")

    def generer_groupes_et_sauvegarder(self, repartition, fenetre_recap):
        """Génère les groupes et enregistre tout directement dans le dossier choisi par l'utilisateur."""
        dossier_complet = filedialog.askdirectory(
            title="Choisissez le dossier où enregistrer les fichiers de groupes"
        )
        if not dossier_complet:
            return

        try:
            groupes = generer_groupes(self.df, self.nb_groupes, repartition)
            dossier_complet, nom_classes, periode = ajouter_groupes_au_df(
                self.df, groupes, self.chemin_fichier, dossier_complet
            )
            sauvegarder_groupes(groupes, dossier_complet, nom_classes, periode)
            fenetre_recap.destroy()
            self.afficher_message(
                "Groupes créés avec succès",
                f"Tous les fichiers ont été enregistrés dans le dossier :\n\n{dossier_complet}",
                type="info"
            )
        except Exception as e:
            self.afficher_message("Erreur lors de la génération", str(e), type="error")

    def reinitialiser_interface(self):
        """Réinitialise complètement l'interface et les variables."""
        confirm = messagebox.askyesno("Réinitialiser", "Voulez-vous vraiment tout réinitialiser ?")
        if not confirm:
            return
        for w in self.winfo_children():
            if w not in [self.logo_frame]:
                w.destroy()
        self.df = None
        self.chemin_fichier = ""
        self.niveaux = {}
        self.nb_groupes = 0
        self.entrees = {}
        self.resume_label = None
        self.frame_saisie = None
        self.frame_boutons = None
        self.init_ui()

    def afficher_message(self, titre, message, type="info"):
        """Affiche un message d'info, de warning ou d'erreur."""
        if type == "info":
            messagebox.showinfo(titre, message)
        elif type == "warning":
            messagebox.showwarning(titre, message)
        elif type == "error":
            messagebox.showerror(titre, message)

if __name__ == "__main__":
    app = Application()
    app.mainloop()
