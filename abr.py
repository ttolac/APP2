"""
abr.py — Arbre Binaire de Recherche pour LowBid
Chaque nœud stocke un prix (clé) et la liste des joueurs ayant misé ce prix.
"""


class Noeud:
    def __init__(self, prix: int, joueur: str):
        self.prix = prix
        self.joueurs = [joueur]   # plusieurs joueurs possibles pour un même prix
        self.gauche = None
        self.droite = None


class ABR:
    def __init__(self):
        self.racine = None

    # ------------------------------------------------------------------ #
    #  INSERTION                                                           #
    # ------------------------------------------------------------------ #
    def inserer(self, prix: int, joueur: str) -> None:
        """Insère une mise (prix, joueur) dans l'ABR."""
        if self.racine is None:
            self.racine = Noeud(prix, joueur)
        else:
            self._inserer_rec(self.racine, prix, joueur)

    def _inserer_rec(self, noeud: Noeud, prix: int, joueur: str) -> None:
        if prix == noeud.prix:
            noeud.joueurs.append(joueur)
        elif prix < noeud.prix:
            if noeud.gauche is None:
                noeud.gauche = Noeud(prix, joueur)
            else:
                self._inserer_rec(noeud.gauche, prix, joueur)
        else:
            if noeud.droite is None:
                noeud.droite = Noeud(prix, joueur)
            else:
                self._inserer_rec(noeud.droite, prix, joueur)

    # ------------------------------------------------------------------ #
    #  PARCOURS INFIXE                                                     #
    # ------------------------------------------------------------------ #
    def parcours_infixe(self) -> list:
        """Retourne la liste des nœuds triés par prix croissant."""
        resultat = []
        self._infixe_rec(self.racine, resultat)
        return resultat

    def _infixe_rec(self, noeud: Noeud, resultat: list) -> None:
        if noeud is not None:
            self._infixe_rec(noeud.gauche, resultat)
            resultat.append(noeud)
            self._infixe_rec(noeud.droite, resultat)

    def afficher_infixe(self) -> None:
        """Affiche l'état de l'enchère (prix triés)."""
        noeuds = self.parcours_infixe()
        if not noeuds:
            print("  (arbre vide)")
            return
        print(f"  {'Prix':>6} | {'Nb joueurs':>10} | Joueurs")
        print("  " + "-" * 50)
        for n in noeuds:
            statut = "UNIQUE" if len(n.joueurs) == 1 else f"{len(n.joueurs)} joueurs"
            print(f"  {n.prix:>6} | {statut:>10} | {', '.join(n.joueurs)}")

    # ------------------------------------------------------------------ #
    #  RECHERCHE DU PLUS BAS PRIX UNIQUE                                  #
    # ------------------------------------------------------------------ #
    def plus_bas_unique(self):
        """
        Parcourt l'ABR en infixe (ordre croissant) et retourne le premier
        nœud dont la liste joueurs ne contient qu'un seul élément.
        Retourne None si aucun prix unique n'existe.
        """
        return self._plus_bas_unique_rec(self.racine)

    def _plus_bas_unique_rec(self, noeud: Noeud):
        if noeud is None:
            return None
        # Chercher d'abord à gauche (prix plus bas)
        candidat = self._plus_bas_unique_rec(noeud.gauche)
        if candidat is not None:
            return candidat
        # Vérifier ce nœud
        if len(noeud.joueurs) == 1:
            return noeud
        # Sinon chercher à droite
        return self._plus_bas_unique_rec(noeud.droite)

    # ------------------------------------------------------------------ #
    #  SUCCESSEUR & PRÉDÉCESSEUR                                          #
    # ------------------------------------------------------------------ #
    def successeur(self, prix: int):
        """
        Retourne le nœud dont le prix est le plus petit supérieur à `prix`.
        Utile pour trouver le prochain candidat après un prix non unique.
        """
        successeur = None
        noeud = self.racine
        while noeud is not None:
            if prix < noeud.prix:
                successeur = noeud
                noeud = noeud.gauche
            elif prix > noeud.prix:
                noeud = noeud.droite
            else:
                # On est sur le nœud : successeur = minimum du sous-arbre droit
                if noeud.droite is not None:
                    successeur = self._minimum(noeud.droite)
                break
        return successeur

    def predecesseur(self, prix: int):
        """
        Retourne le nœud dont le prix est le plus grand inférieur à `prix`.
        Utile pour naviguer dans l'ordre des prix.
        """
        predecesseur = None
        noeud = self.racine
        while noeud is not None:
            if prix > noeud.prix:
                predecesseur = noeud
                noeud = noeud.droite
            elif prix < noeud.prix:
                noeud = noeud.gauche
            else:
                if noeud.gauche is not None:
                    predecesseur = self._maximum(noeud.gauche)
                break
        return predecesseur

    def _minimum(self, noeud: Noeud) -> Noeud:
        while noeud.gauche is not None:
            noeud = noeud.gauche
        return noeud

    def _maximum(self, noeud: Noeud) -> Noeud:
        while noeud.droite is not None:
            noeud = noeud.droite
        return noeud

    # ------------------------------------------------------------------ #
    #  SUPPRESSION CONDITIONNELLE                                         #
    # ------------------------------------------------------------------ #
    def supprimer_joueur(self, prix: int, joueur: str) -> bool:
        """
        Supprime un joueur d'un prix donné.
        Si le nœud n'a plus de joueurs, supprime le nœud de l'ABR.
        Retourne True si la suppression a eu lieu.
        """
        self.racine, supprime = self._supprimer_joueur_rec(self.racine, prix, joueur)
        return supprime

    def _supprimer_joueur_rec(self, noeud: Noeud, prix: int, joueur: str):
        if noeud is None:
            return None, False
        if prix < noeud.prix:
            noeud.gauche, ok = self._supprimer_joueur_rec(noeud.gauche, prix, joueur)
            return noeud, ok
        elif prix > noeud.prix:
            noeud.droite, ok = self._supprimer_joueur_rec(noeud.droite, prix, joueur)
            return noeud, ok
        else:
            # Nœud trouvé
            if joueur in noeud.joueurs:
                noeud.joueurs.remove(joueur)
                if not noeud.joueurs:
                    # Supprimer le nœud de l'ABR
                    noeud = self._supprimer_noeud(noeud)
                return noeud, True
            return noeud, False

    def _supprimer_noeud(self, noeud: Noeud):
        """Supprime un nœud de l'ABR (logique classique ABR)."""
        if noeud.gauche is None:
            return noeud.droite
        elif noeud.droite is None:
            return noeud.gauche
        # Deux enfants : remplacer par le successeur (min du sous-arbre droit)
        successeur = self._minimum(noeud.droite)
        noeud.prix = successeur.prix
        noeud.joueurs = successeur.joueurs[:]
        noeud.droite = self._supprimer_noeud_valeur(noeud.droite, successeur.prix)
        return noeud

    def _supprimer_noeud_valeur(self, noeud: Noeud, prix: int):
        if noeud is None:
            return None
        if prix < noeud.prix:
            noeud.gauche = self._supprimer_noeud_valeur(noeud.gauche, prix)
        elif prix > noeud.prix:
            noeud.droite = self._supprimer_noeud_valeur(noeud.droite, prix)
        else:
            if noeud.gauche is None:
                return noeud.droite
            elif noeud.droite is None:
                return noeud.gauche
            succ = self._minimum(noeud.droite)
            noeud.prix = succ.prix
            noeud.joueurs = succ.joueurs[:]
            noeud.droite = self._supprimer_noeud_valeur(noeud.droite, succ.prix)
        return noeud

    # ------------------------------------------------------------------ #
    #  STATISTIQUES                                                        #
    # ------------------------------------------------------------------ #
    def nombre_total_mises(self) -> int:
        """Nombre total de mises (somme des joueurs sur tous les nœuds)."""
        return sum(len(n.joueurs) for n in self.parcours_infixe())

    def distribution_prix(self) -> dict:
        """Retourne {prix: nb_joueurs} pour chaque prix de l'ABR."""
        return {n.prix: len(n.joueurs) for n in self.parcours_infixe()}

    def est_vide(self) -> bool:
        return self.racine is None
