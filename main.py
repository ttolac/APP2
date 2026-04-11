from interface import lancer_interface
from enchere import Manche
from simulation import Simulation
from mode_humain import jouer_mode_humain

#defaut
COUT_BASE = 1.0
ALPHA = 5.0
PRIX_MAX = 20

FICHIERS_CSV = {
    "1": {
        "chemin": "APP_lowbid_data/lowbid_manche_demo.csv",
        "label":  "Manche démo (30 mises, 1 manche, prix max 49)",
        "format": "simple",          #joueur prix
        "prix_max_suggestion": 49, #prix max utilise dans le fichier
    },
    "2": {
        "chemin": "APP_lowbid_data/lowbid_multi_manches_500x40.csv",
        "label":  "Multi-manches (500 manches × 40 joueurs, prix max 60)",
        "format": "multi",           #manche joueur prix
        "prix_max_suggestion": 60,
    },
    "3": {
        "chemin": "APP_lowbid_data/lowbid_stress_200k.csv",
        "label":  "Stress test (200 000 mises, 1 manche, prix max 199)",
        "format": "simple",
        "prix_max_suggestion": 199,
    },
}


def menu():
    """menu d'affichage en console"""
    print()
    print("LOWBID - Qui perd gagne !")
    print()
    print(f"Paramètres : cout_base={COUT_BASE}, α={ALPHA}, prix_max={PRIX_MAX}")
    print()
    print("1. Charger et analyser un fichier CSV")
    print("2. Générer des données démo et analyser")
    print("3. Lancer la simulation multi-manches (500 manches aléatoires)")
    print("4. Comparer stratégies sur plusieurs valeurs d'α")
    print("5. Mode Humain vs Ordinateur")
    print("0. Quitter")
    print()

def choisir_fichier():
    """demande a l'utilisateur de choisir un parmis les 3 fichiers"""
    print("\nChoisissez un fichier CSV :")
    print()
    for k, v in FICHIERS_CSV.items():
        print(f"{k}. {v['label']}")
    print("0. Fichier personnalisé (saisie manuelle)")
    choix = input("Votre choix : ").strip()

    if choix in FICHIERS_CSV:
        return FICHIERS_CSV[choix]
    elif choix == "0":
        chemin = input("Chemin du fichier : ").strip()
        fmt = input("Format ? [simple=joueur,prix | multi=manche,joueur,prix] :").strip()
        return {"chemin": chemin, "format": fmt or "simple", "prix_max_suggestion": PRIX_MAX}
    else:
        print("Choix invalide, sortie")
        return None


def demo_fichier_csv():
    """choix du menu =1"""
    cfg = choisir_fichier()
    if cfg is None:
        return

    manche = Manche(COUT_BASE, ALPHA)

    if cfg["format"] == "multi":
        #demander quelle manche on veut analyser
        nb = input("Numéro de manche à analyser [1] (ou 'all' pour tout) : ").strip()
        if nb.lower() == "all":
            manche.charger_csv_multi_manches(cfg["chemin"], numero_manche=-1)
        else:
            numero = int(nb) if nb.isdigit() else 1
            manche.charger_csv_multi_manches(cfg["chemin"], numero_manche=numero)
    else:
        manche.charger_csv(cfg["chemin"])

    print(f"\nSuccès! {manche.abr.nombre_total_mises()} mises chargées")
    analyser_manche(manche)


def demo_generation():
    """choix du menu =2"""
    print("\nGénération d'un jeu de données démo...")
    manche = Manche(COUT_BASE, ALPHA)
    manche.generer_demo(nb_joueurs=12, prix_max=PRIX_MAX, nb_mises_par_joueur=2)
    print(f"Succès! {manche.abr.nombre_total_mises()} mises générées")
    analyser_manche(manche)


def analyser_manche(manche: Manche):
    """analyse complete dune manche chargee"""
    #on utilise le parcours infixe
    manche.afficher_etat()

    distrib = manche.abr.distribution_prix()
    print("\nDistribution des prix :")
    for prix, nb in distrib.items():
        barre = "█" * nb
        print(f"prix {prix:>3} : {barre} ({nb})")

    #couts et recette
    manche.afficher_couts()

    #gagnant
    manche.afficher_gagnant()

    #successeur/predecesseur
    print()
    try:
        ref = int(input("Entrez un prix pour tester successeur/prédécesseur [5 par défaut] : ") or "5")
    except ValueError:
        ref = 5
    manche.requete_successeur(ref)
    manche.requete_predecesseur(ref)


def lancer_simulation():
    """choix du menu =3"""
    sim = Simulation(nb_manches=500, prix_max=PRIX_MAX,
                     cout_base=COUT_BASE, alpha=ALPHA)
    sim.ajouter_joueur("Alice", "Aleatoire")
    sim.ajouter_joueur("Bob", "Prudente")
    sim.ajouter_joueur("Charlie", "Adaptative")
    sim.ajouter_joueur("Diana","Agressive")
    sim.ajouter_joueur("Eve", "Calculee")

    print("\nLancement de la simulation (500 manches)...")
    sim.lancer()
    sim.afficher_resultats()


def comparer_alpha():
    """choix du menu =4"""
    sim = Simulation(nb_manches=500, prix_max=PRIX_MAX,
                     cout_base=COUT_BASE, alpha=ALPHA)
    sim.ajouter_joueur("Alice","Aleatoire")
    sim.ajouter_joueur("Bob", "Prudente")
    sim.ajouter_joueur("Charlie", "Adaptative")
    sim.ajouter_joueur("Diana", "Agressive")
    sim.ajouter_joueur("Eve", "Calculee")

    sim.comparer_strategies(nb_manches_test=500, alpha_values=[0.5, 5.0, 20.0])


#boucle
def main():
    while True:
        menu()
        choix = input("Votre choix : ").strip()
        if choix == "1":
            demo_fichier_csv()
        elif choix == "2":
            demo_generation()
        elif choix == "3":
            lancer_simulation()
        elif choix == "4":
            comparer_alpha()
        elif choix == "5":
            nb = int(input("Nombre de manches [5 par défaut] : ").strip() or "5")
            jouer_mode_humain(nb_manches=nb, prix_max=PRIX_MAX,
                              cout_base=COUT_BASE, alpha=ALPHA)
        elif choix == "0":
            print("\nAu revoir !\n")
            break
        else:
            print("Choix invalide")


if __name__ == "__main__":
    print("\nLowBid — Mode de lancement")
    print("1. Interface graphique")
    print("2. Console (menu texte)")
    choix = input("\nVotre choix (1/2): ").strip()
    if choix == "1":
        lancer_interface()
    else:
        main()