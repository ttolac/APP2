"""
enchère.py — Logique métier de LowBid
Gestion d'une manche : chargement, coûts, gagnant, recette.
"""

import csv
import os
import random
from abr import ABR


# ------------------------------------------------------------------ #
#  FORMULE DE COÛT                                                     #
# ------------------------------------------------------------------ #

def cout_mise(prix: int, cout_base: float, alpha: float) -> float:
    """
    Coût payé par un joueur pour miser sur `prix`.
    cout_mise(prix) = cout_base + alpha / (prix + 1)
    """
    return cout_base + alpha / (prix + 1)


# ------------------------------------------------------------------ #
#  MANCHE                                                              #
# ------------------------------------------------------------------ #

class Manche:
    """
    Représente une manche complète de l'enchère LowBid.
    """

    def __init__(self, cout_base: float = 1.0, alpha: float = 5.0):
        self.cout_base = cout_base
        self.alpha = alpha
        self.abr = ABR()
        self.mises: list[tuple[str, int]] = []   # [(joueur, prix), ...]

    # ---- Chargement des données ------------------------------------ #

    def charger_csv(self, chemin: str) -> None:
        """
        Charge les mises depuis un fichier CSV.
        Format attendu : joueur,prix  (une mise par ligne, sans en-tête obligatoire)
        """
        if not os.path.exists(chemin):
            raise FileNotFoundError(f"Fichier introuvable : {chemin}")
        with open(chemin, newline='', encoding='utf-8') as f:
            reader = csv.reader(f)
            for ligne in reader:
                if len(ligne) < 2:
                    continue
                joueur = ligne[0].strip()
                try:
                    prix = int(ligne[1].strip())
                except ValueError:
                    continue   # ignore les lignes non numériques (en-tête éventuel)
                if prix < 0:
                    continue   # prix doit être ≥ 0
                self.ajouter_mise(joueur, prix)

    def generer_demo(self, nb_joueurs: int = 10, prix_max: int = 20,
                     nb_mises_par_joueur: int = 2) -> None:
        """Génère un jeu de données aléatoire pour démonstration."""
        for i in range(nb_joueurs):
            joueur = f"J{i+1:02d}"
            for _ in range(nb_mises_par_joueur):
                prix = random.randint(0, prix_max)
                self.ajouter_mise(joueur, prix)

    def ajouter_mise(self, joueur: str, prix: int) -> None:
        """Ajoute une mise et met à jour l'ABR."""
        self.mises.append((joueur, prix))
        self.abr.inserer(prix, joueur)

    # ---- Affichage -------------------------------------------------- #

    def afficher_etat(self) -> None:
        """Affiche l'état de l'enchère via parcours infixe."""
        print("\n  ── État de l'enchère (parcours infixe) ──")
        self.abr.afficher_infixe()
        print(f"\n  Nombre total de mises : {self.abr.nombre_total_mises()}")

    # ---- Calcul des coûts & recette --------------------------------- #

    def calculer_recette(self) -> dict:
        """
        Calcule le coût payé par chaque joueur et la recette totale du vendeur.
        Retourne un dict avec :
          - 'couts_par_joueur' : {joueur: coût_total}
          - 'recette_totale'   : float
          - 'cout_moyen'       : float
        """
        couts: dict[str, float] = {}
        for joueur, prix in self.mises:
            c = cout_mise(prix, self.cout_base, self.alpha)
            couts[joueur] = couts.get(joueur, 0.0) + c

        recette = sum(couts.values())
        nb_joueurs = len(couts)
        cout_moyen = recette / nb_joueurs if nb_joueurs > 0 else 0.0

        return {
            "couts_par_joueur": couts,
            "recette_totale": recette,
            "cout_moyen": cout_moyen,
        }

    def afficher_couts(self) -> None:
        """Affiche les coûts de chaque joueur et la recette vendeur."""
        data = self.calculer_recette()
        print("\n  ── Coûts par joueur ──")
        print(f"  {'Joueur':>8} | Coût total")
        print("  " + "-" * 25)
        for joueur, cout in sorted(data["couts_par_joueur"].items()):
            print(f"  {joueur:>8} | {cout:.2f} €")
        print(f"\n  Recette vendeur  : {data['recette_totale']:.2f} €")
        print(f"  Coût moyen/joueur: {data['cout_moyen']:.2f} €")

    # ---- Gagnant ---------------------------------------------------- #

    def determiner_gagnant(self) -> dict:
        """
        Recherche le plus bas prix unique dans l'ABR.
        Retourne un dict :
          - 'gagnant'  : str (nom du joueur) ou None
          - 'prix'     : int ou None
          - 'statut'   : 'gagnant' | 'aucun_unique' | 'arbre_vide'
        """
        if self.abr.est_vide():
            return {"gagnant": None, "prix": None, "statut": "arbre_vide"}

        noeud = self.abr.plus_bas_unique()
        if noeud is None:
            return {"gagnant": None, "prix": None, "statut": "aucun_unique"}

        return {
            "gagnant": noeud.joueurs[0],
            "prix": noeud.prix,
            "statut": "gagnant",
        }

    def afficher_gagnant(self) -> dict:
        """Affiche et retourne le résultat de la manche."""
        result = self.determiner_gagnant()
        print("\n  ── Résultat de la manche ──")
        if result["statut"] == "gagnant":
            print(f"  🏆 Gagnant : {result['gagnant']}  (prix = {result['prix']})")
        elif result["statut"] == "aucun_unique":
            print("  ⚠️  Aucun prix unique — manche annulée (pas de gagnant).")
        else:
            print("  ⚠️  Aucune mise — manche vide.")
        return result

    # ---- Requêtes d'analyse ----------------------------------------- #

    def requete_successeur(self, prix: int) -> None:
        n = self.abr.successeur(prix)
        if n:
            print(f"  Successeur de {prix} → prix={n.prix}, joueurs={n.joueurs}")
        else:
            print(f"  Aucun successeur pour le prix {prix}.")

    def requete_predecesseur(self, prix: int) -> None:
        n = self.abr.predecesseur(prix)
        if n:
            print(f"  Prédécesseur de {prix} → prix={n.prix}, joueurs={n.joueurs}")
        else:
            print(f"  Aucun prédécesseur pour le prix {prix}.")
