import random
from enchere import Manche, cout_mise
from strats import strategies

class JoueurIA:
    def __init__(self, nom, strategie_nom,cout_base, alpha):
        self.nom = nom
        self.strategie_nom = strategie_nom
        self.strategie = strategies[strategie_nom]
        self.cout_base = cout_base
        self.alpha = alpha
        #stats total
        self.victoires = 0
        self.total_manches = 0
        self.gains_totaux = 0.0 
        self.couts_totaux = 0.0
        self.historique_gagnants: list[int] = []

    def choisir_prix(self, prix_max):
        """On calcule la mise pour chaque strat (calculee a besoin de 2 parametres en plus)"""
        fn = self.strategie
        if self.strategie_nom == "Calculee":
            return fn(prix_max, self.historique_gagnants,self.cout_base, self.alpha)
        return fn(prix_max, self.historique_gagnants)

    def enregistrer_manche(self, a_gagne, prix_mise,prix_gagnant_manche):
        self.total_manches += 1
        cout = cout_mise(prix_mise, self.cout_base, self.alpha)
        self.couts_totaux += cout
        if a_gagne:
            self.victoires += 1
        if prix_gagnant_manche is not None:
            self.historique_gagnants.append(prix_gagnant_manche)

class Simulation:
    def __init__(self, nb_manches =500, prix_max= 20, cout_base= 1.0, alpha= 5.0):
        self.nb_manches = nb_manches
        self.prix_max = prix_max
        self.cout_base = cout_base
        self.alpha = alpha
        self.joueurs: list[JoueurIA] = []
        self.recettes_vendeur: list[float] = []
        self.nb_manches_sans_gagnant = 0

    def ajouter_joueur(self, nom, strategie_nom):
        self.joueurs.append(JoueurIA(nom, strategie_nom, self.cout_base, self.alpha))

    def lancer(self):
        """lance toutes les manche"""
        for i in range(self.nb_manches):
            self.jouer_une_manche()

    def jouer_une_manche(self):
        manche = Manche(self.cout_base, self.alpha)

        #chaque joueru fait une mise
        prix_choisis = {}
        for joueur in self.joueurs:
            prix = joueur.choisir_prix(self.prix_max)
            prix_choisis[joueur.nom] = prix
            manche.ajouter_mise(joueur.nom, prix)

        #on determine le gagnant
        result = manche.determiner_gagnant()
        gagnant_nom = result["gagnant"]
        prix_gagnant = result["prix"]

        if result["statut"] != "gagnant":
            self.nb_manches_sans_gagnant += 1

        #calcul recette
        data = manche.calculer_recette()
        self.recettes_vendeur.append(data["recette_totale"])

        #mise a jour des stats
        for joueur in self.joueurs:
            a_gagne = (joueur.nom == gagnant_nom)
            joueur.enregistrer_manche(a_gagne, prix_choisis[joueur.nom],prix_gagnant)


    def afficher_resultats(self) :
        print("\n"+"-"*25)
        print(f"RÉSULTATS DE LA SIMULATION")
        print()
        print(f"Paramètres : cout_base={self.cout_base}, α={self.alpha}, prix_max={self.prix_max}")
        print(f"Manches sans gagnant : {self.nb_manches_sans_gagnant} ({100*self.nb_manches_sans_gagnant/self.nb_manches:.1f}%)")

        recette_moy = sum(self.recettes_vendeur) / len(self.recettes_vendeur)
        print(f"Recette moyenne vendeur/manche : {recette_moy:.2f} e")

        print()
        print(f"  {'Joueur':>12} | {'Stratégie':>11} | {'Victoires':>9} | {'Taux (%)':>8} | {'Coût total':>10} | {'Coût moy/m':>10}")

        for j in self.joueurs:
            taux = 100 * j.victoires / j.total_manches if j.total_manches else 0
            cout_moy = j.couts_totaux / j.total_manches if j.total_manches else 0
            print(f"  {j.nom:>12} | {j.strategie_nom:>11} | {j.victoires:>9} | "
                  f"{taux:>8.2f} | {j.couts_totaux:>10.2f} | {cout_moy:>10.2f}")

        print()
        self.afficher_analyse_parametres()

    def afficher_analyse_parametres(self):
        """analyse des parametres et limites de l'abr"""
        print("Analyse économique" + "\n")
        recette_moy = sum(self.recettes_vendeur) / len(self.recettes_vendeur)
        cout_total_joueurs = sum(j.couts_totaux for j in self.joueurs)
        print(f"Revenu total vendeur sur {self.nb_manches} manches : "
              f"{sum(self.recettes_vendeur):.2f} e")
        print(f"Coût total joueurs : {cout_total_joueurs:.2f} e")
        print(f"-> Le système N'EST PAS à somme nulle : le vendeur encaisse {sum(self.recettes_vendeur):.2f} e indépendamment du prix final.")

        print()
        print("Effet de la prime de risque (α)" + "\n")
        for p in [0, 1, 5, 10]:
            c = cout_mise(p, self.cout_base, self.alpha)
            print(f"Prix {p:>3} -> coût mise = {c:.3f} e")

        print()
        print("Limites de l'ABR & alternatives")
        print(" -Dégénérescence : si les prix sont insérés en ordre croissant,")
        print("    l'ABR dégénère en liste chaînée (O(n) par opération).")
        print(" -Alternative 1 : dictionnaire {prix: [joueurs]} + tri O(n log n)")
        print("    à la fin -> simple mais pas dynamique.")
        print(" -Alternative 2 : ABR auto-équilibré (AVL, Red-Black) -> O(log n)")
        print("    garanti, mais implémentation plus complexe.")
        print(" -Alternative 3 : tas min (heap) -> O(log n) insertion,")
        print("    O(n) pour trouver le minimum unique.")

    def comparer_strategies(self, nb_manches_test= 500,alpha_values= None):
        """compare les stratégies selon alpha"""
        if alpha_values is None:
            alpha_values = [1.0, 5.0, 20.0]

        print("\n" + "-"*35)
        print("COMPARAISON DES STRATÉGIES SELON α")
        print()

        for alpha in alpha_values:
            sim = Simulation(nb_manches=nb_manches_test, prix_max=self.prix_max,cout_base=self.cout_base, alpha=alpha)
            noms_strategies = list(set(j.strategie_nom for j in self.joueurs))
            for i, strat in enumerate(noms_strategies):
                sim.ajouter_joueur(f"J{i+1}_{strat[:3]}", strat)
            sim.lancer()

            print(f"\nα = {alpha}")
            recette_moy = sum(sim.recettes_vendeur) / len(sim.recettes_vendeur)
            print(f"Recette vendeur moy : {recette_moy:.2f} e")
            for j in sim.joueurs:
                taux = 100 * j.victoires / j.total_manches if j.total_manches else 0
                print(f"{j.strategie_nom:>11} : {taux:.2f}% victoires")
