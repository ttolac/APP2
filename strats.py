import random
import math

#toutes les fonctions prennent historique en parametre pour faciliter l'appel dans les autres programmes
#aleatoire
def strategie_aleatoire(prix_max, historique):
    """prix au hasard entre 0 et prix_max"""
    return random.randint(0, prix_max)

#prudent = evite les prix bas
def strategie_prudente(prix_max, historique):
    """prix entre prix_max//4 et prix_max//2"""
    borne_inf = max(1, prix_max // 4)
    borne_sup = max(borne_inf + 1, prix_max // 2)
    return random.randint(borne_inf, borne_sup)

#adaptive = suit les mises des manches precedents
def strategie_adaptative(prix_max, historique):
    """aleatoire mais quand assez d'historique choisit moyenne des prix +-2"""
    if len(historique) < 5:
        return strategie_aleatoire(prix_max, historique)
    #moyenne
    recents = [p for p in historique[-10:] if p is not None]
    if not recents:
        return strategie_aleatoire(prix_max, historique)
    moyenne = sum(recents) / len(recents)
    variation = random.randint(-2, 2)
    prix = int(round(moyenne)) + variation
    return max(0, min(prix_max, prix))

#agressive = prix bas
def strategie_agressive(prix_max, historique):
    """prix entre 0 et 3"""
    return random.randint(0, min(3, prix_max))

#calculee = maths
def strategie_calculee(prix_max, historique, cout_base=1.0, alpha=5.0):
    """fait des calculs pour chercher le prix unique plus interessant interessant en cout/bas """
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

strategies = {
    "Aleatoire": strategie_aleatoire,
    "Prudente": strategie_prudente,
    "Adaptative": strategie_adaptative,
    "Agressive": strategie_agressive,
    "Calculee": strategie_calculee,
}
