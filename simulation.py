"""
simulation.py — Moteur de simulation multi-manches LowBid

Lance N manches avec des joueurs IA (chacun ayant une stratégie).
Collecte et affiche les statistiques comparatives.
"""

import random
from enchere import Manche, cout_mise
from strategies import STRATEGIES


# ------------------------------------------------------------------ #
#  JOUEUR IA                                                           #
# ------------------------------------------------------------------ #

class JoueurIA:
    def __init__(self, nom: str, strategie_nom: str,
                 cout_base: float, alpha: float):
        if strategie_nom not in STRATEGIES:
            raise ValueError(f"Stratégie inconnue : {strategie_nom}")
        self.nom = nom
        self.strategie_nom = strategie_nom
        self._strategie = STRATEGIES[strategie_nom]
        self.cout_base = cout_base
        self.alpha = alpha
        # Stats cumulées
        self.victoires = 0
        self.total_manches = 0
        self.gains_totaux = 0.0    # somme des (valeur_objet - coût) si gagné
        self.couts_totaux = 0.0    # somme de tous les coûts payés
        self.historique_gagnants: list[int] = []

    def choisir_prix(self, prix_max: int) -> int:
        """Appelle la stratégie pour obtenir le prix de la mise."""
        fn = self._strategie
        # strategie_calculee accepte cout_base et alpha
        if self.strategie_nom == "Calculee":
            return fn(prix_max, self.historique_gagnants,
                      self.cout_base, self.alpha)
        return fn(prix_max, self.historique_gagnants)

    def enregistrer_manche(self, a_gagne: bool, prix_mise: int,
                            prix_gagnant_manche) -> None:
        self.total_manches += 1
        cout = cout_mise(prix_mise, self.cout_base, self.alpha)
        self.couts_totaux += cout
        if a_gagne:
            self.victoires += 1
        if prix_gagnant_manche is not None:
            self.historique_gagnants.append(prix_gagnant_manche)


# ------------------------------------------------------------------ #
#  SIMULATION                                                          #
# ------------------------------------------------------------------ #

class Simulation:
    def __init__(self, nb_manches: int = 500, prix_max: int = 20,
                 cout_base: float = 1.0, alpha: float = 5.0,
                 valeur_objet: float = 100.0):
        self.nb_manches = nb_manches
        self.prix_max = prix_max
        self.cout_base = cout_base
        self.alpha = alpha
        self.valeur_objet = valeur_objet   # pour calculer le gain du gagnant
        self.joueurs: list[JoueurIA] = []
        self.recettes_vendeur: list[float] = []
        self.nb_manches_sans_gagnant = 0

    def ajouter_joueur(self, nom: str, strategie_nom: str) -> None:
        self.joueurs.append(
            JoueurIA(nom, strategie_nom, self.cout_base, self.alpha)
        )

    def lancer(self) -> None:
        """Lance toutes les manches."""
        if not self.joueurs:
            print("Aucun joueur enregistré.")
            return

        for i in range(self.nb_manches):
            self._jouer_une_manche()

    def _jouer_une_manche(self) -> None:
        manche = Manche(self.cout_base, self.alpha)

        # Chaque joueur fait une mise
        prix_choisis = {}
        for joueur in self.joueurs:
            prix = joueur.choisir_prix(self.prix_max)
            prix_choisis[joueur.nom] = prix
            manche.ajouter_mise(joueur.nom, prix)

        # Déterminer le gagnant
        result = manche.determiner_gagnant()
        gagnant_nom = result["gagnant"]
        prix_gagnant = result["prix"]

        if result["statut"] != "gagnant":
            self.nb_manches_sans_gagnant += 1

        # Calculer recette vendeur
        data = manche.calculer_recette()
        self.recettes_vendeur.append(data["recette_totale"])

        # Mettre à jour les stats des joueurs
        for joueur in self.joueurs:
            a_gagne = (joueur.nom == gagnant_nom)
            joueur.enregistrer_manche(a_gagne, prix_choisis[joueur.nom],
                                      prix_gagnant)

    # ------------------------------------------------------------------ #
    #  AFFICHAGE DES RÉSULTATS                                            #
    # ------------------------------------------------------------------ #

    def afficher_resultats(self) -> None:
        print("\n" + "=" * 60)
        print(f"  RÉSULTATS DE LA SIMULATION ({self.nb_manches} manches)")
        print("=" * 60)
        print(f"  Paramètres : cout_base={self.cout_base}, α={self.alpha}, "
              f"prix_max={self.prix_max}")
        print(f"  Manches sans gagnant : {self.nb_manches_sans_gagnant} "
              f"({100*self.nb_manches_sans_gagnant/self.nb_manches:.1f}%)")

        recette_moy = sum(self.recettes_vendeur) / len(self.recettes_vendeur)
        print(f"  Recette moyenne vendeur/manche : {recette_moy:.2f} €")

        print()
        print(f"  {'Joueur':>12} | {'Stratégie':>11} | {'Victoires':>9} | "
              f"{'Taux (%)':>8} | {'Coût total':>10} | {'Coût moy/m':>10}")
        print("  " + "-" * 72)

        for j in self.joueurs:
            taux = 100 * j.victoires / j.total_manches if j.total_manches else 0
            cout_moy = j.couts_totaux / j.total_manches if j.total_manches else 0
            print(f"  {j.nom:>12} | {j.strategie_nom:>11} | {j.victoires:>9} | "
                  f"{taux:>8.2f} | {j.couts_totaux:>10.2f} | {cout_moy:>10.2f}")

        print()
        self._afficher_analyse_parametres()

    def _afficher_analyse_parametres(self) -> None:
        """Analyse de l'effet des paramètres et des limites de l'ABR."""
        print("  ── Analyse économique ──")
        recette_moy = sum(self.recettes_vendeur) / len(self.recettes_vendeur)
        cout_total_joueurs = sum(j.couts_totaux for j in self.joueurs)
        print(f"  Revenu total vendeur sur {self.nb_manches} manches : "
              f"{sum(self.recettes_vendeur):.2f} €")
        print(f"  Coût total joueurs : {cout_total_joueurs:.2f} €")
        print(f"  → Le système N'EST PAS à somme nulle : "
              f"le vendeur encaisse {sum(self.recettes_vendeur):.2f} € "
              f"indépendamment du prix final.")

        print()
        print("  ── Effet de la prime de risque (α) ──")
        for p in [0, 1, 5, 10]:
            c = cout_mise(p, self.cout_base, self.alpha)
            print(f"  Prix {p:>3} → coût mise = {c:.3f} €")

        print()
        print("  ── Limites de l'ABR & alternatives ──")
        print("  • Dégénérescence : si les prix sont insérés en ordre croissant,")
        print("    l'ABR dégénère en liste chaînée (O(n) par opération).")
        print("  • Alternative 1 : dictionnaire {prix: [joueurs]} + tri O(n log n)")
        print("    à la fin → simple mais pas dynamique.")
        print("  • Alternative 2 : ABR auto-équilibré (AVL, Red-Black) → O(log n)")
        print("    garanti, mais implémentation plus complexe.")
        print("  • Alternative 3 : tas min (heap) → O(log n) insertion,")
        print("    O(n) pour trouver le minimum unique.")

    def comparer_strategies(self, nb_manches_test: int = 500,
                             alpha_values: list[float] = None) -> None:
        """
        Compare les stratégies sur plusieurs valeurs d'alpha.
        Affiche l'impact du paramètre alpha sur les taux de victoire.
        """
        if alpha_values is None:
            alpha_values = [1.0, 5.0, 20.0]

        print("\n" + "=" * 60)
        print("  COMPARAISON DES STRATÉGIES SELON α")
        print("=" * 60)

        for alpha in alpha_values:
            sim = Simulation(nb_manches=nb_manches_test, prix_max=self.prix_max,
                             cout_base=self.cout_base, alpha=alpha)
            noms_strategies = list(set(j.strategie_nom for j in self.joueurs))
            for i, strat in enumerate(noms_strategies):
                sim.ajouter_joueur(f"J{i+1}_{strat[:3]}", strat)
            sim.lancer()

            print(f"\n  α = {alpha}")
            recette_moy = sum(sim.recettes_vendeur) / len(sim.recettes_vendeur)
            print(f"  Recette vendeur moy : {recette_moy:.2f} €")
            for j in sim.joueurs:
                taux = 100 * j.victoires / j.total_manches if j.total_manches else 0
                print(f"    {j.strategie_nom:>11} : {taux:.2f}% victoires")
