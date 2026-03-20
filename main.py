"""
main.py — Point d'entrée de LowBid
Propose un menu interactif pour tester toutes les fonctionnalités.
"""

import sys
import os

# Assurer que le dossier courant est dans le path
sys.path.insert(0, os.path.dirname(__file__))

from enchere import Manche
from simulation import Simulation
from mode_humain import jouer_mode_humain


# ------------------------------------------------------------------ #
#  PARAMÈTRES GLOBAUX PAR DÉFAUT                                       #
# ------------------------------------------------------------------ #

COUT_BASE = 1.0
ALPHA = 5.0
PRIX_MAX = 20


# ------------------------------------------------------------------ #
#  MENU PRINCIPAL                                                       #
# ------------------------------------------------------------------ #

def menu() -> None:
    print("\n" + "═" * 60)
    print("  🎯  LOWBID — « Qui perd gagne ! »")
    print("═" * 60)
    print(f"  Paramètres : cout_base={COUT_BASE}, α={ALPHA}, prix_max={PRIX_MAX}")
    print()
    print("  1. Charger et analyser un fichier CSV")
    print("  2. Générer des données démo et analyser")
    print("  3. Lancer la simulation multi-manches (500 manches)")
    print("  4. Comparer stratégies sur plusieurs valeurs d'α")
    print("  5. Mode Humain vs Ordinateur")
    print("  6. Questions de réflexion (séances aller/intermédiaire)")
    print("  0. Quitter")
    print()


def demo_fichier_csv() -> None:
    """Option 1 : Chargement depuis CSV."""
    chemin = input("  Chemin du fichier CSV [demo_mises.csv] : ").strip()
    if not chemin:
        chemin = os.path.join(os.path.dirname(__file__), "demo_mises.csv")

    manche = Manche(COUT_BASE, ALPHA)
    try:
        manche.charger_csv(chemin)
        print(f"\n  ✅ {manche.abr.nombre_total_mises()} mises chargées.")
    except FileNotFoundError as e:
        print(f"  ❌ {e}")
        return

    _analyser_manche(manche)


def demo_generation() -> None:
    """Option 2 : Données générées aléatoirement."""
    print("\n  Génération d'un jeu de données démo...")
    manche = Manche(COUT_BASE, ALPHA)
    manche.generer_demo(nb_joueurs=12, prix_max=PRIX_MAX, nb_mises_par_joueur=2)
    print(f"  {manche.abr.nombre_total_mises()} mises générées.")
    _analyser_manche(manche)


def _analyser_manche(manche: Manche) -> None:
    """Analyse complète d'une manche chargée."""
    # Parcours infixe
    manche.afficher_etat()

    # Distribution
    distrib = manche.abr.distribution_prix()
    print("\n  Distribution des prix :")
    for prix, nb in distrib.items():
        barre = "█" * nb
        print(f"    prix {prix:>3} : {barre} ({nb})")

    # Coûts et recette
    manche.afficher_couts()

    # Gagnant
    manche.afficher_gagnant()

    # Successeur / prédécesseur
    print()
    try:
        ref = int(input("  Entrez un prix pour tester successeur/prédécesseur [5] : ") or "5")
    except ValueError:
        ref = 5
    manche.requete_successeur(ref)
    manche.requete_predecesseur(ref)


def lancer_simulation() -> None:
    """Option 3 : Simulation 500 manches."""
    sim = Simulation(nb_manches=500, prix_max=PRIX_MAX,
                     cout_base=COUT_BASE, alpha=ALPHA)
    sim.ajouter_joueur("Alice",   "Aleatoire")
    sim.ajouter_joueur("Bob",     "Prudente")
    sim.ajouter_joueur("Charlie", "Adaptative")
    sim.ajouter_joueur("Diana",   "Agressive")
    sim.ajouter_joueur("Eve",     "Calculee")

    print("\n  Lancement de la simulation (500 manches)...")
    sim.lancer()
    sim.afficher_resultats()


def comparer_alpha() -> None:
    """Option 4 : Comparaison des stratégies sur différents α."""
    sim = Simulation(nb_manches=500, prix_max=PRIX_MAX,
                     cout_base=COUT_BASE, alpha=ALPHA)
    sim.ajouter_joueur("Alice",   "Aleatoire")
    sim.ajouter_joueur("Bob",     "Prudente")
    sim.ajouter_joueur("Charlie", "Adaptative")
    sim.ajouter_joueur("Diana",   "Agressive")
    sim.ajouter_joueur("Eve",     "Calculee")

    sim.comparer_strategies(nb_manches_test=500, alpha_values=[0.5, 5.0, 20.0])


def afficher_reflexions() -> None:
    """Option 6 : Réponses aux questions des séances."""
    print("""
═══════════════════════════════════════════════════════════
  QUESTIONS DE RÉFLEXION
═══════════════════════════════════════════════════════════

  ── SÉANCE ALLER ──

  Q: Pourquoi le prix 0 n'est-il pas une stratégie dominante ?
  R: Avec la prime de risque, cout_mise(0) = cout_base + α/1 = cout_base + α,
     ce qui est très élevé. De plus, tous les joueurs rationnels pensent la
     même chose → prix 0 surreprésenté → jamais unique. Double pénalité.

  Q: Le système est-il à somme nulle ?
  R: NON. Le vendeur encaisse la somme de TOUTES les mises, quel que soit le
     gagnant. La somme des paiements des joueurs > gain du gagnant (si le
     gagnant remporte un objet de valeur V, il paie son cout_mise, mais les
     autres perdent aussi leur mise). Le vendeur crée de la valeur nette.

  Q: Quelles informations pour déterminer le gagnant ?
  R: La liste complète des (joueur, prix), pour savoir quels prix sont
     apparus exactement une fois, puis le minimum parmi ces prix uniques.

  Q: Peut-on déterminer le gagnant sans trier les prix ?
  R: Oui, avec un ABR : le parcours infixe donne l'ordre naturellement.
     On peut aussi utiliser un dictionnaire {prix: count} et parcourir
     en O(n log n) via un tri, mais l'ABR évite un tri explicite.

  ── SÉANCE INTERMÉDIAIRE — STRUCTURES ──

  Q: Structures maintenant les prix ordonnés dynamiquement ?
  R: ABR, AVL, Red-Black Tree, Skip List, B-Tree. Toutes maintiennent
     l'ordre à l'insertion sans tri a posteriori.

  Q: Différence entre trier à la fin et maintenir l'ordre ?
  R: Maintenir l'ordre : O(log n) par insertion, accès ordonné immédiat.
     Trier à la fin : O(1) insertion, O(n log n) tri final.
     → Si on a besoin de l'ordre souvent (ex. plusieurs requêtes), l'ABR
       est plus efficace sur la durée.

  Q: En flux continu, quelle solution ?
  R: ABR auto-équilibré (AVL, Red-Black) : O(log n) insertion ET recherche,
     ordonnancement permanent garanti même pour un flux infini de mises.

  ── COMPLEXITÉ ──

  Q: Complexité d'une insertion dans :
  R: Tableau trié      → O(n)        (décalage nécessaire)
     ABR équilibré     → O(log n)    (recherche + insertion en hauteur log n)
     Dictionnaire + tri→ O(1) insert + O(n log n) tri final

  Q: Quand un ABR est-il inefficace ?
  R: Quand les données arrivent déjà triées (croissant ou décroissant) :
     l'ABR dégénère en liste chaînée → hauteur n → O(n) par opération.

  Q: Comment éviter la dégénérescence ?
  R: Utiliser un ABR auto-équilibré (AVL : rotations à chaque insertion pour
     maintenir |h_gauche - h_droite| ≤ 1), ou Red-Black Tree (5 propriétés
     de couleur garantissant h ≤ 2 log n).

  ── STRATÉGIE ──

  Q: Si tous jouent aléatoirement ?
  R: La distribution des prix est uniforme. Le prix unique le plus bas est
     statistiquement celui qui "tombe" dans un intervalle peu peuplé.
     Le vendeur maximise sa recette car les mises se distribuent largement.

  Q: Si tous jouent 0 ?
  R: Prix 0 jamais unique → aucun gagnant → manche annulée à chaque fois.
     Vendeur encaisse quand même (chacun a payé sa mise sur 0).

  Q: Existe-t-il un prix "stable" (équilibre de Nash) ?
  R: Il n'existe pas de prix dominant pur. En pratique, la simulation montre
     une oscillation autour d'une zone médiane (≈ prix_max/4 à prix_max/2).
     Quand trop de joueurs convergent vers un prix, il n'est plus unique →
     ils le quittent → le prix redevient rare → retour. C'est un équilibre
     mixte (probabiliste), pas un équilibre pur.
═══════════════════════════════════════════════════════════
    """)


# ------------------------------------------------------------------ #
#  BOUCLE PRINCIPALE                                                   #
# ------------------------------------------------------------------ #

def main() -> None:
    while True:
        menu()
        choix = input("  Votre choix : ").strip()
        if choix == "1":
            demo_fichier_csv()
        elif choix == "2":
            demo_generation()
        elif choix == "3":
            lancer_simulation()
        elif choix == "4":
            comparer_alpha()
        elif choix == "5":
            nb = int(input("  Nombre de manches [5] : ").strip() or "5")
            jouer_mode_humain(nb_manches=nb, prix_max=PRIX_MAX,
                              cout_base=COUT_BASE, alpha=ALPHA)
        elif choix == "6":
            afficher_reflexions()
        elif choix == "0":
            print("\n  Au revoir !\n")
            break
        else:
            print("  Choix invalide.")


if __name__ == "__main__":
    main()
