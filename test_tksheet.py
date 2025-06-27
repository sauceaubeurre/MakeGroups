import tkinter as tk
import tksheet

# Données d'exemple pour 3 groupes
groupes_data = [
    [  # Groupe 1
        ["601", "Dupont", "Alice", 3],
        ["601", "Petit", "Emma", 2],
    ],
    [  # Groupe 2
        ["602", "Martin", "Bob", 2],
        ["602", "Bernard", "David", 4],
    ],
    [  # Groupe 3
        ["601", "Durand", "Chloé", 1],
        ["602", "Lemoine", "Franck", 3],
    ]
]

colonnes = ["Classe", "Nom", "Prénom", "Niveau"]

# Trie chaque groupe avant affichage
for g in groupes_data:
    g.sort(key=lambda x: x[1])

root = tk.Tk()
root.title("Prototype Groupes - tksheet + boutons transfert")

main_frame = tk.Frame(root)
main_frame.pack(padx=18, pady=18)

sheets = []
frames = []

# Pour chaque groupe, on crée un frame et un tksheet dedans
for i, data in enumerate(groupes_data):
    frame = tk.Frame(main_frame)
    frame.grid(row=0, column=2*i)  # On laisse un espace pour les boutons
    label = tk.Label(frame, text=f"Groupe {i+1} ({len(data)} élèves)", font=("Segoe UI", 11, "bold"))
    label.pack()
    sheet = tksheet.Sheet(frame,
                          data=data,
                          headers=colonnes,
                          show_row_index=True,
                          height=140,
                          width=290
    )
    sheet.enable_bindings((
        "single_select",
        "row_select"
    ))
    sheet.pack()
    sheets.append(sheet)
    frames.append(frame)

# Fonctions de transfert
def transfer(src, dst):
    """Transfère la ligne sélectionnée du sheet src vers dst."""
    selected = sheets[src].get_selected_rows()
    if selected:
        idx = list(selected)[0]
        row = groupes_data[src].pop(idx)
        groupes_data[dst].append(row)
        groupes_data[src].sort(key=lambda x: x[1])
        groupes_data[dst].sort(key=lambda x: x[1])
        sheets[src].set_sheet_data(groupes_data[src])
        sheets[dst].set_sheet_data(groupes_data[dst])
        sheets[src].deselect("all")
        sheets[dst].deselect("all")
        # Actualise les labels de taille de groupe
        for i in range(3):
            frames[i].winfo_children()[0].config(text=f"Groupe {i+1} ({len(groupes_data[i])} élèves)")

# Ajout des boutons de transfert entre chaque groupe
for i in range(2):  # entre groupe 0-1 et 1-2
    btns = tk.Frame(main_frame)
    btns.grid(row=0, column=2*i + 1, padx=7)
    btn_right = tk.Button(btns, text=">", width=4, font=("Segoe UI", 12, "bold"),
                          command=lambda i=i: transfer(i, i+1))
    btn_right.pack(pady=3)
    btn_left = tk.Button(btns, text="<", width=4, font=("Segoe UI", 12, "bold"),
                         command=lambda i=i: transfer(i+1, i))
    btn_left.pack(pady=3)

root.mainloop()
