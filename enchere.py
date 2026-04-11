import csv
import os
import random
from abr import ABR

def cout_mise(prix, cout_base, alpha):
    """cout_mise(prix) = cout_base + alpha / (prix + 1)"""
    return cout_base + alpha / (prix + 1)

class Manche:
    """classe pour une manche"""

    def __init__(self, cout_base = 1.0, alpha =5.0):
        self.cout_base = cout_base
        self.alpha = alpha
        self.abr = ABR()
        self.mises: list[tuple[str, int]] = []   # [(joueur, prix), ...]


    def charger_csv(self, chemin):
        """charger si on a un fichier csv correct (jouerr prix)"""
        if not os.path.exists(chemin):
            raise FileNotFoundError(f"Fichier introuvable : {chemin}")
        with open(chemin, newline='', encoding='utf-8') as f:
            reader = csv.reader(f)
            for ligne in reader:
                if len(ligne) >= 2  and ligne[1].strip() != "prix":
                    joueur = ligne[0].strip()
                    prix = int(ligne[1].strip())

                    if prix >= 0:
                        self.ajouter_mise(joueur, prix)  #prix doit être>= 0

    def charger_csv_multi_manches(self, chemin, numero_manche= 1):
        """charger une manche si on a un fichier (manche joueur prix) si numero_manche=-1, charge toutes les manches"""
        if not os.path.exists(chemin):
            raise FileNotFoundError(f"Fichier introuvable : {chemin}")
        with open(chemin, newline='', encoding='utf-8') as f:
            reader = csv.reader(f)
            for ligne in reader:
                if len(ligne) >= 3 and ligne[0].strip() != "manche":
                    manche = int(ligne[0].strip())
                    joueur = ligne[1].strip()
                    prix = int(ligne[2].strip())
                    if prix >= 0:
                        if numero_manche == -1 or manche == numero_manche:
                            self.ajouter_mise(joueur, prix)

    def generer_demo(self, nb_joueurs=10, prix_max=20, nb_mises_par_joueur=2):
        """demo aleatoire"""
        for i in range(nb_joueurs):
            joueur = f"J{i+1:02d}"
            for j in range(nb_mises_par_joueur):
                prix = random.randint(0, prix_max)
                self.ajouter_mise(joueur, prix)

    def ajouter_mise(self, joueur, prix):
        """ajoute une mise et met à jour l'abr"""
        self.mises.append((joueur, prix))
        self.abr.inserer(prix, joueur)


    def afficher_etat(self):
        """montre les mises dans lenchere par ordre croissant"""
        print("\nÉtat de l'enchère (parcours infixe)")
        self.abr.afficher_infixe()
        print(f"\nNombre total de mises : {self.abr.nombre_total_mises()}")


    def calculer_recette(self):
        """Calcule ce que les joueurs paient selon alpha et la recette totale du vendeur"""
        couts: dict[str, float] = {}
        for joueur, prix in self.mises:
            c = cout_mise(prix, self.cout_base, self.alpha)
            couts[joueur] = couts.get(joueur, 0.0) + c

        recette = sum(couts.values())
        nb_joueurs = len(couts)
        cout_moyen = recette / nb_joueurs if nb_joueurs > 0 else 0.0

        return {"couts_par_joueur": couts,"recette_totale": recette,"cout_moyen": cout_moyen}

    def afficher_couts(self):
        """calcule les couts et la recette finale"""
        data = self.calculer_recette()
        print("\nCoût par joueur")
        print(f"  {'Joueur':>8} | Coût total")
        for joueur, cout in sorted(data["couts_par_joueur"].items()):
            print(f"  {joueur:>8} | {cout:.2f} e")
        print(f"\nRecette vendeur : {data['recette_totale']:.2f} e")
        print(f"Coût moyen/joueur: {data['cout_moyen']:.2f} e")


    def determiner_gagnant(self):
        """recherche le plus pas prix unique (gagnant)"""
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

    def afficher_gagnant(self):
        """afficher le gagant"""
        result = self.determiner_gagnant()
        print("\nRésultat de la manche")
        if result["statut"] == "gagnant":
            print(f":D Gagnant : {result['gagnant']}  (prix = {result['prix']})")
        elif result["statut"] == "aucun_unique":
            print("X Aucun prix unique — manche annulée (pas de gagnant)")
        else:
            print("X Aucune mise — manche vide")
        return result


    def requete_successeur(self, prix):
        n = self.abr.successeur(prix)
        if n:
            print(f"Successeur de {prix} -> prix={n.prix}, joueurs={n.joueurs}")
        else:
            print(f"Aucun successeur pour le prix {prix}")

    def requete_predecesseur(self, prix):
        n = self.abr.predecesseur(prix)
        if n:
            print(f"Prédécesseur de {prix} -> prix={n.prix}, joueurs={n.joueurs}")
        else:
            print(f"Aucun prédécesseur pour le prix {prix}.")
