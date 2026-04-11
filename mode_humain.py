from enchere import Manche, cout_mise
from strats import strategies, strategie_aleatoire, strategie_prudente,strategie_adaptative, strategie_calculee

bots = [
    ("Bot_Aleatoire", "Aleatoire"),
    ("Bot_Prudent", "Prudente"),
    ("Bot_Adaptatif", "Adaptative"),
    ("Bot_Calcule", "Calculee"),
]


def jouer_mode_humain(nb_manches=5, prix_max=20, cout_base=1.0, alpha=5.0, nom_humain = "Humain"):
    """mode ordi vs humain"""
    print("\n" +"-"*35)
    print("LOWBID - Mode Humain vs Ordinateur")
    print(f"Règles : proposez le PLUS BAS PRIX UNIQUE pour gagner!")
    print(f"Prix entier E [0, {prix_max}]")
    print(f"Coût d'une mise : {cout_base:.1f} + {alpha:.1f}/(prix+1) e")
    print()



    #stats humain
    victoires_humain = 0
    cout_total_humain = 0.0
    historique_gagnants: list[int] = []

    #stats bots
    stats_bots = {nom: {"victoires": 0, "cout": 0.0} for nom, _ in bots}

    for manche_num in range(1, nb_manches + 1):
        print(f"{'-'*50}")
        print(f"MANCHE {manche_num}/{nb_manches}")

        #on demande a lhumain ce quil veut jouer
        while True:
            try:
                saisie = input(f"{nom_humain}, entrez votre prix [0-{prix_max}] : ")
                prix_humain = int(saisie.strip())
                if 0 <= prix_humain <= prix_max:
                    break
                else:
                    print(f"X Prix hors limites. Choisissez entre 0 et {prix_max}")
            except ValueError:
                print("X Entrée invalide. Entrez un entier")

        #on cree une manche
        manche = Manche(cout_base, alpha)
        manche.ajouter_mise(nom_humain, prix_humain)

        #les bots jouent
        prix_bots = {}
        for nom_bot, strat_nom in bots:
            fn = strategies[strat_nom]
            if strat_nom == "Calculee":
                prix_bot = fn(prix_max, historique_gagnants, cout_base, alpha)
            else:
                prix_bot = fn(prix_max, historique_gagnants)
            prix_bots[nom_bot] = prix_bot
            manche.ajouter_mise(nom_bot, prix_bot)

        #on montre les mises du joueur puis des bots
        print(f"\nMises de cette manche :")
        print(f"{nom_humain:>15} -> prix = {prix_humain}")
        for nom_bot, prix_bot in prix_bots.items():
            print(f"{nom_bot:>15} -> prix = {prix_bot}")

        #on montre l'etat de lenchere
        print()
        manche.afficher_etat()

        #resultta de la manche
        result = manche.afficher_gagnant()
        gagnant = result["gagnant"]
        prix_gagnant = result["prix"]

        if prix_gagnant is not None:
            historique_gagnants.append(prix_gagnant)

        #couts de la manche
        data = manche.calculer_recette()
        cout_humain_manche = data["couts_par_joueur"].get(nom_humain, 0.0)
        cout_total_humain += cout_humain_manche

        for nom_bot in prix_bots:
            cout_bot = data["couts_par_joueur"].get(nom_bot, 0.0)
            stats_bots[nom_bot]["cout"] += cout_bot

        print(f"\nVotre coût cette manche : {cout_humain_manche:.2f} e")
        print(f"Recette vendeur : {data['recette_totale']:.2f} e")

        if gagnant == nom_humain:
            print(f"\n:P Félicitations {nom_humain} ! Vous gagnez cette manche !")
            victoires_humain += 1
        elif gagnant:
            print(f"\n:( {gagnant} remporte cette manche avec le prix {prix_gagnant}.")
            stats_bots[gagnant]["victoires"] += 1
        else:
            print(f"\nX Manche annulée : aucun prix unique.")

        #conseils
        conseil_strategie(prix_humain, prix_gagnant, historique_gagnants,cout_base, alpha)

    # Résumé final
    afficher_resume_humain(nom_humain, victoires_humain, cout_total_humain,nb_manches, stats_bots)


def conseil_strategie(prix_humain, prix_gagnant,historique,cout_base, alpha):
    """petits conseils strategiques"""
    print()
    print(":3 Conseil stratégique :")
    if len(historique) >= 3:
        if prix_gagnant is not None:
            print(f"Prix gagnant cette manche : {prix_gagnant}")
        moy = sum(historique[-5:]) / len(historique[-5:])
        print(f"Prix gagnant moyen (5 dernières manches) : {moy:.1f}")
        cout_0 = cout_mise(0, cout_base, alpha)
        cout_moy = cout_mise(int(moy), cout_base, alpha)
        print(f"Coût mise sur 0 : {cout_0:.2f} e / Coût mise sur ~{int(moy)} : {cout_moy:.2f} e")
        if prix_humain < moy / 2:
            print(" -> Vous jouez très bas : risque de collision ET coût élevé")
        elif prix_humain > moy * 2:
            print(" -> Vous jouez très haut : peu de concurrence mais prix unique rare")
        else:
            print(" -> Votre prix est dans la zone habituelle des gagnants")
    else:
        print("Pas encore assez de données pour conseiller")


def afficher_resume_humain(nom, victoires, cout_total,nb_manches, stats_bots):
    print("\n" + "-" * 60)
    print("  RÉSUMÉ FINAL")
    print(f"{nom} : {victoires}/{nb_manches} manches gagnées ({100*victoires/nb_manches:.1f}%) / Coût total : {cout_total:.2f} e")
    print()
    print(f"  {'Bot':>15} | {'Victoires':>9} | {'Coût total':>10}")
    for nom_bot, s in stats_bots.items():
        print(f"  {nom_bot:>15} | {s['victoires']:>9} | {s['cout']:>10.2f} e")

    print()
    print("Réflexion sur la stratégie gagnante")
    print(" -Le prix 0 semble attrayant, mais la prime de risque peut le rendre très cher")
    print(" -La vraie valeur est dans l'unicité : un prix légèrement au-dessus")
    print("    de la zone populaire a plus de chances d'être unique")
    print(" -La stratégie 'Calculée' pondère coût et unicité pour maximiser")
    print("    l'espérance de gain nette.")
    print(" -La stratégie 'Adaptative' apprend de l'historique, mais converge")
    print("    vers la même zone que les autres -> le système n'a pas de prix 'stable'")
    print("    unique")
