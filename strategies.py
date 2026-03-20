"""
strategies.py — Stratégies de joueurs pour la simulation LowBid

Chaque stratégie est une fonction :
    strategie(prix_max, historique) -> int
Elle retourne le prix choisi par le joueur pour cette manche.

`historique` est une liste des prix gagnants des manches précédentes.
"""

import random
import math


# ------------------------------------------------------------------ #
#  STRATÉGIE 1 : Aléatoire pur                                        #
# ------------------------------------------------------------------ #

def strategie_aleatoire(prix_max: int, historique: list[int]) -> int:
    """Choisit un prix au hasard dans [0, prix_max]."""
    return random.randint(0, prix_max)


# ------------------------------------------------------------------ #
#  STRATÉGIE 2 : Prudente (évite les tout petits prix)               #
# ------------------------------------------------------------------ #

def strategie_prudente(prix_max: int, historique: list[int]) -> int:
    """
    Évite les prix très bas (coûteux à cause de la prime de risque).
    Choisit uniformément dans [prix_max//4, prix_max//2].
    """
    borne_inf = max(1, prix_max // 4)
    borne_sup = max(borne_inf + 1, prix_max // 2)
    return random.randint(borne_inf, borne_sup)


# ------------------------------------------------------------------ #
#  STRATÉGIE 3 : Adaptative (suit l'historique des gagnants)         #
# ------------------------------------------------------------------ #

def strategie_adaptative(prix_max: int, historique: list[int]) -> int:
    """
    Si l'historique est riche, choisit autour du prix gagnant moyen
    avec une légère variation aléatoire (±2).
    Sinon, revient à la stratégie aléatoire.
    """
    if len(historique) < 5:
        return strategie_aleatoire(prix_max, historique)
    # Moyenne des 10 derniers prix gagnants
    recents = [p for p in historique[-10:] if p is not None]
    if not recents:
        return strategie_aleatoire(prix_max, historique)
    moyenne = sum(recents) / len(recents)
    variation = random.randint(-2, 2)
    prix = int(round(moyenne)) + variation
    return max(0, min(prix_max, prix))


# ------------------------------------------------------------------ #
#  STRATÉGIE 4 : Agressive (mise sur les très bas prix)              #
# ------------------------------------------------------------------ #

def strategie_agressive(prix_max: int, historique: list[int]) -> int:
    """
    Mise systématiquement sur de très petits prix (0 à 3).
    Coûte cher à cause de la prime de risque, mais vise les prix bas.
    """
    return random.randint(0, min(3, prix_max))


# ------------------------------------------------------------------ #
#  STRATÉGIE 5 : Calculée (compromis coût/unicité)                   #
# ------------------------------------------------------------------ #

def strategie_calculee(prix_max: int, historique: list[int],
                        cout_base: float = 1.0, alpha: float = 5.0) -> int:
    """
    Cherche un compromis entre prime de risque et chances d'être unique.
    Utilise une distribution de probabilité pondérée :
    poids(p) ∝ 1 / cout_mise(p) = 1 / (cout_base + alpha/(p+1))
    Les prix moins chers sont favorisés, mais pas à l'extrême.
    """
    poids = []
    for p in range(prix_max + 1):
        cout = cout_base + alpha / (p + 1)
        poids.append(1.0 / cout)
    # Sélection pondérée
    total = sum(poids)
    r = random.uniform(0, total)
    cumul = 0.0
    for p, w in enumerate(poids):
        cumul += w
        if r <= cumul:
            return p
    return prix_max


# ------------------------------------------------------------------ #
#  REGISTRE DES STRATÉGIES                                            #
# ------------------------------------------------------------------ #

STRATEGIES = {
    "Aleatoire":   strategie_aleatoire,
    "Prudente":    strategie_prudente,
    "Adaptative":  strategie_adaptative,
    "Agressive":   strategie_agressive,
    "Calculee":    strategie_calculee,
}
