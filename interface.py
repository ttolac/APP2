import tkinter as tk
from tkinter import filedialog, messagebox
import os
from enchere import Manche
from simulation import Simulation

class LowBidApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("LowBid - Qui perd gagne !")
        self.configure(bg="#f5f4f0")
        self.geometry("880x660")
 
        #entete
        hdr = tk.Frame(self, bg="#1a3a5c", pady=14)
        hdr.pack(fill="x")
        tk.Label(hdr, text="⚖  LOWBID", font=("Georgia", 20, "bold"), fg="#c9a84c",
                 bg="#1a3a5c").pack(side="left", padx=24)
        tk.Label(hdr, text="Qui perd gagne !", font=("Georgia", 11, "italic"),
                 fg="#aabbcc", bg="#1a3a5c").pack(side="left")
 
        #corps
        body = tk.Frame(self, bg="#f5f4f0")
        body.pack(fill="both", expand=True, padx=16, pady=12)
        body.columnconfigure(0, weight=1)
        body.columnconfigure(1, weight=2)
        body.rowconfigure(0, weight=1)
 
        left = tk.Frame(body, bg="#ffffff", padx=14, pady=14,
                        relief="flat", bd=1)
        left.grid(row=0, column=0, sticky="nsew", padx=(0, 10))
 
        def sep():
            tk.Frame(left, bg="#c9a84c", height=1).pack(fill="x", pady=6)
 
        def lbl(text, fg="#888888"):
            tk.Label(left, text=text, font=("Courier New", 10), fg=fg,
                     bg="#ffffff").pack(anchor="w", pady=(6, 0))
 
        tk.Label(left, text="PARAMETRES", font=("Georgia", 11, "bold"),
                 fg="#1a3a5c", bg="#ffffff").pack(anchor="w")
        sep()
 
        lbl("Fichier CSV")
        fr = tk.Frame(left, bg="#ffffff")
        fr.pack(fill="x", pady=(2, 6))
        self.var_fichier = tk.StringVar(value="lowbid_manche_demo.csv")
        tk.Entry(fr, textvariable=self.var_fichier, font=("Courier New", 10),
                 relief="solid", bd=1).pack(side="left", fill="x", expand=True)
        tk.Button(fr, text="…", command=self.parcourir, font=("Courier New", 10, "bold"),
                  bg="#f5f4f0", fg="#1a3a5c", relief="flat", bd=1,
                  cursor="hand2").pack(side="left", padx=(4, 0))
 
        lbl("Format")
        self.var_format = tk.StringVar(value="simple")
        fr2 = tk.Frame(left, bg="#ffffff")
        fr2.pack(fill="x", pady=(2, 6))
        for val, txt in [("simple", "joueur,prix"), ("multi", "manche,joueur,prix")]:
            tk.Radiobutton(fr2, text=txt, variable=self.var_format, value=val,
                           bg="#ffffff", fg="#1a1a1a", font=("Courier New", 10),
                           activebackground="#ffffff").pack(side="left", padx=4)
 
        lbl("Num manche si multi (-1 merge toutes les manches en une)")
        self.var_manche = tk.StringVar(value="1")
        tk.Entry(left, textvariable=self.var_manche, font=("Courier New", 10),
                 relief="solid", bd=1, width=6).pack(anchor="w", pady=(2, 6))
 
        sep()
        tk.Label(left, text="ECONOMIE", font=("Georgia", 11, "bold"),
                 fg="#1a3a5c", bg="#ffffff").pack(anchor="w")
 
        self.var_cout_base = tk.StringVar(value="1.0")
        self.var_alpha     = tk.StringVar(value="5.0")
        for libelle, var in [("cout_base (euros)", self.var_cout_base),
                              ("α (prime risque)", self.var_alpha)]:
            lbl(libelle)
            tk.Entry(left, textvariable=var, font=("Courier New", 10),
                     relief="solid", bd=1, width=10).pack(anchor="w", pady=(2, 6))
 
        sep()
        tk.Label(left, text="ACTIONS", font=("Georgia", 11, "bold"),
                 fg="#1a3a5c", bg="#ffffff").pack(anchor="w")
 
        for text, cmd, bg, fg in [
            ("> Analyser la manche",  self.analyser, "#1a3a5c",  "#ffffff"),
            ("> Simuler 500 manches", self.simuler,  "#c9a84c", "#1a3a5c"),
            ("X Effacer",             self.effacer,  "#f5f4f0",      "#b03030"),
        ]:
            tk.Button(left, text=text, command=cmd, bg=bg, fg=fg,
                      font=("Courier New", 10, "bold"), relief="flat", bd=0,
                      padx=10, pady=7, cursor="hand2").pack(fill="x", pady=3)
 
        right = tk.Frame(body, bg="#ffffff", padx=14, pady=14)
        right.grid(row=0, column=1, sticky="nsew")
        right.rowconfigure(1, weight=1)
        right.columnconfigure(0, weight=1)
 
        tk.Label(right, text="RESULTATS", font=("Georgia", 11, "bold"),
                 fg="#1a3a5c", bg="#ffffff").pack(anchor="w")
        tk.Frame(right, bg="#c9a84c", height=1).pack(fill="x", pady=6)
 
        fr3 = tk.Frame(right, bg="#ffffff")
        fr3.pack(fill="both", expand=True)
        scroll = tk.Scrollbar(fr3)
        scroll.pack(side="right", fill="y")
 
        self.txt = tk.Text(fr3, bg="#ffffff", fg="#1a1a1a", font=("Courier New", 10),
                           relief="flat", bd=0, wrap="word", state="disabled",
                           yscrollcommand=scroll.set, padx=8, pady=6, spacing1=2)
        self.txt.pack(fill="both", expand=True)
        scroll.config(command=self.txt.yview)
 
        self.txt.tag_config("titre",  foreground="#1a3a5c",  font=("Courier New", 10, "bold"))
        self.txt.tag_config("succes", foreground="#2e7d4f", font=("Courier New", 10, "bold"))
        self.txt.tag_config("erreur", foreground="#b03030",  font=("Courier New", 10, "bold"))
        self.txt.tag_config("muted",  foreground="#888888")
        self.txt.tag_config("info",   foreground="#1a5c8a")
 
        self.ecrire("Bienvenue sur LowBid.\nChargez un fichier CSV et cliquez sur Analyser.\n", "muted")
 
    def ecrire(self, texte, tag=""):
        self.txt.config(state="normal")
        self.txt.insert("end", texte, tag) if tag else self.txt.insert("end", texte)
        self.txt.see("end")
        self.txt.config(state="disabled")
 
    def effacer(self):
        self.txt.config(state="normal")
        self.txt.delete("1.0", "end")
        self.txt.config(state="disabled")
 
    def parcourir(self):
        chemin = filedialog.askopenfilename(filetypes=[("CSV", "*.csv"), ("Tous", "*.*")])
        if chemin:
            self.var_fichier.set(chemin)
 
    def analyser(self):
        try:
            cout_base = float(self.var_cout_base.get())
            alpha     = float(self.var_alpha.get())
        except ValueError:
            messagebox.showerror("Erreur", "cout_base et α doivent être des nombres.")
            return
 
        chemin = self.var_fichier.get().strip()
        self.effacer()
        self.ecrire(f"Fichier : {os.path.basename(chemin)}\n\n", "titre")
 
        manche = Manche(cout_base, alpha)
        try:
            if self.var_format.get() == "multi":
                num = int(self.var_manche.get()) if self.var_manche.get().lstrip('-').isdigit() else 1
                manche.charger_csv_multi_manches(chemin, numero_manche=num)
            else:
                manche.charger_csv(chemin)
        except Exception as e:
            self.ecrire(f"Erreur : {e}\n", "erreur")
            return
 
        self.ecrire(f"{manche.abr.nombre_total_mises()} mises chargées\n\n", "info")
        self.ecrire("ETAT DE L'ENCHERE\n", "titre")
        self.ecrire(f"  {'Prix':>6}  {'Joueurs':>7}  Statut\n", "muted")
        noeuds = manche.abr.parcours_infixe()
        for n in (noeuds[:50] if len(noeuds) > 100 else noeuds):
            statut = "UNIQUE" if len(n.joueurs) == 1 else f"{len(n.joueurs)} joueurs"
            self.ecrire(f"  {n.prix:>6}  {len(n.joueurs):>7}  {statut}\n")
        if len(noeuds) > 100:
            self.ecrire(f"  … ({len(noeuds) - 50} autres prix)\n", "muted")
 
        data = manche.calculer_recette()
        self.ecrire(f"\nCOUTS PAR JOUEUR\n\n", "titre")
        self.ecrire(f"Rappel : la formule de calcul du cout de la mise est {cout_base} + {alpha}/(prix+1)\n\n", "info")

        self.ecrire(f"  {'Joueur':>14}  Cout (e)\n", "muted")
        for joueur, cout in sorted(data["couts_par_joueur"].items()):
            self.ecrire(f"  {joueur:>14}  {cout:.2f}\n")
        self.ecrire(f"\nRecette vendeur : {data['recette_totale']:.2f} e\n", "info")
        self.ecrire(f"Cout moyen/joueur : {data['cout_moyen']:.2f} e\n", "info")
 
        result = manche.determiner_gagnant()
        self.ecrire(f"\nRESULTAT\n", "titre")
        if result["statut"] == "gagnant":
            self.ecrire(f"Gagnant : {result['gagnant']}  -  prix = {result['prix']}\n", "succes")
        elif result["statut"] == "aucun_unique":
            self.ecrire("Aucun prix unique — manche annulée.\n", "erreur")
 
    def simuler(self):
        try:
            cout_base = float(self.var_cout_base.get())
            alpha     = float(self.var_alpha.get())
        except ValueError:
            messagebox.showerror("Erreur", "cout_base et α doivent être des nombres.")
            return
 
        self.effacer()
        self.ecrire("Simulation 500 manches\n\n", "titre")
        self.ecrire("Calcul en cours...\n", "muted")
        self.update()
 
        sim = Simulation(nb_manches=500, prix_max=60, cout_base=cout_base, alpha=alpha)
        for nom, strat in [("Alice","Aleatoire"), ("Bob","Prudente"),
                            ("Charlie","Adaptative"), ("Diana","Agressive"), ("Eve","Calculee")]:
            sim.ajouter_joueur(nom, strat)
        sim.lancer()
 
        recette_moy = sum(sim.recettes_vendeur) / len(sim.recettes_vendeur)
        self.ecrire(f"Paramètres : cout_base={cout_base}, α={alpha}\n", "muted")
        self.ecrire(f"Manches sans gagnant : {sim.nb_manches_sans_gagnant}\n", "muted")
        self.ecrire(f"Recette vendeur moy  : {recette_moy:.2f} e\n\n", "info")
        self.ecrire(f"  {'Joueur':>10}  {'Stratégie':>11}  {'Victoires':>9}  {'Taux%':>6}  {'Cout moy':>8}\n", "muted")
        self.ecrire("  " + "─" * 52 + "\n", "muted")
        for j in sim.joueurs:
            taux     = 100 * j.victoires / j.total_manches if j.total_manches else 0
            cout_moy = j.couts_totaux / j.total_manches    if j.total_manches else 0
            self.ecrire(f"  {j.nom:>10}  {j.strategie_nom:>11}  {j.victoires:>9}  {taux:>6.2f}  {cout_moy:>8.2f}\n")
        self.ecrire(f"Rappel : la formule de calcul du cout de la mise est {cout_base} + {alpha}/(prix+1)\n\n", "info")

 
def lancer_interface():
    LowBidApp().mainloop()
 
 
if __name__ == "__main__":
    lancer_interface()