class Noeud:
    def __init__(self, prix, joueur):
        self.prix = prix
        self.joueurs = [joueur]   #plusieurs joueurs possibles pour un meme prix
        self.gauche = None
        self.droite = None


class ABR:
    def __init__(self):
        self.racine = None

    def inserer(self, prix, joueur):
        """inserer une mise dans l'abr"""
        if self.racine is None:
            self.racine = Noeud(prix, joueur)
        else:
            self.inserer_rec(self.racine, prix, joueur)

    def inserer_rec(self, noeud, prix, joueur):
        if prix == noeud.prix:
            noeud.joueurs.append(joueur)
        elif prix < noeud.prix:
            if noeud.gauche is None:
                noeud.gauche = Noeud(prix, joueur)
            else:
                self.inserer_rec(noeud.gauche, prix, joueur)
        else:
            if noeud.droite is None:
                noeud.droite = Noeud(prix, joueur)
            else:
                self.inserer_rec(noeud.droite, prix, joueur)

    def parcours_infixe(self):
        """execute le parcours infixe dans l'abr = ordre croissant"""
        resultat = []
        self.infixe_rec(self.racine, resultat)
        return resultat

    def infixe_rec(self, noeud, resultat):
        if noeud is not None:
            self.infixe_rec(noeud.gauche, resultat)
            resultat.append(noeud)
            self.infixe_rec(noeud.droite, resultat)

    def afficher_infixe(self):
        """affiche en colonnes les prix, le nombre de joueurs
        qui a mit ce prix et quels joeurs"""
        noeuds = self.parcours_infixe()
        if not noeuds:
            print("(arbre vide)")
            return
        print(f"{'Prix':>6} | {'Nb joueurs':>10} | Joueurs") #>6 et >10 servent a l'alignement pour que ca soit joli
        for n in noeuds:
            statut = "UNIQUE" if len(n.joueurs) == 1 else f"{len(n.joueurs)} joueurs"
            print(f"  {n.prix:>6} | {statut:>10} | {', '.join(n.joueurs)}")


    def plus_bas_unique(self):
        """trouve le 1er prix qui a ete mise par un seul joueur ou none"""
        return self.plus_bas_unique_rec(self.racine)

    def plus_bas_unique_rec(self, noeud):
        if noeud is None:
            return None
        #a gauche (car gauche = minimum)
        candidat = self.plus_bas_unique_rec(noeud.gauche)
        if candidat is not None:
            return candidat
        #verifier quil y a 1 seul joeur dessus
        if len(noeud.joueurs) == 1:
            return noeud
        #sinon on cheche a droite
        return self.plus_bas_unique_rec(noeud.droite)

    def successeur(self, prix):
        """retourne la liste des joeurs qui ont mit un prix superieur de 1 a un prix
        utilisation quand on a un prix non unique dcp on cherche le suivant"""
        successeur = None
        noeud = self.racine
        while noeud is not None:
            if prix < noeud.prix:
                successeur = noeud
                noeud = noeud.gauche
            elif prix > noeud.prix:
                noeud = noeud.droite
            else:
                if noeud.droite is not None:
                    successeur = self.minimum_abr(noeud.droite)
                break
        return successeur

    def predecesseur(self, prix):
        """retourne la liste des joeurs qui ont mit un prix inferieur de 1 a un prix"""
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
                    predecesseur = self.maximum_abr(noeud.gauche)
                break
        return predecesseur

    def minimum_abr(self, noeud):
        while noeud.gauche is not None:
            noeud = noeud.gauche
        return noeud

    def maximum_abr(self, noeud):
        while noeud.droite is not None:
            noeud = noeud.droite
        return noeud

    def supprimer_joueur(self, prix, joueur):
        """supprimer un joeur d'un noeud (consigne)"""
        self.racine, supprime = self.supprimer_joueur_rec(self.racine, prix, joueur)
        return supprime

    def supprimer_joueur_rec(self, noeud, prix, joueur):
        if noeud is None:
            return None, False
        if prix < noeud.prix:
            noeud.gauche, ok = self.supprimer_joueur_rec(noeud.gauche, prix, joueur)
            return noeud, ok
        elif prix > noeud.prix:
            noeud.droite, ok = self.supprimer_joueur_rec(noeud.droite, prix, joueur)
            return noeud, ok
        else:
            if joueur in noeud.joueurs:
                noeud.joueurs.remove(joueur)
                if not noeud.joueurs:
                    noeud = self.supprimer_noeud(noeud)
                return noeud, True
            return noeud, False

    def supprimer_noeud(self, noeud):
        """Supprime un nœud de l'abr"""
        if noeud.gauche is None:
            return noeud.droite
        elif noeud.droite is None:
            return noeud.gauche
        successeur = self.minimum_abr(noeud.droite)
        noeud.prix = successeur.prix
        noeud.joueurs = successeur.joueurs[:]
        noeud.droite = self.supprimer_noeud_valeur(noeud.droite, successeur.prix)
        return noeud

    def supprimer_noeud_valeur(self, noeud, prix):
        if noeud is None:
            return None
        if prix < noeud.prix:
            noeud.gauche = self.supprimer_noeud_valeur(noeud.gauche, prix)
        elif prix > noeud.prix:
            noeud.droite = self.supprimer_noeud_valeur(noeud.droite, prix)
        else:
            if noeud.gauche is None:
                return noeud.droite
            elif noeud.droite is None:
                return noeud.gauche
            succ = self.minimum_abr(noeud.droite)
            noeud.prix = succ.prix
            noeud.joueurs = succ.joueurs[:]
            noeud.droite = self.supprimer_noeud_valeur(noeud.droite, succ.prix)
        return noeud

    def nombre_total_mises(self):
        """Nombre total de mises"""
        return sum(len(n.joueurs) for n in self.parcours_infixe()) #somme des joueurs

    def distribution_prix(self):
        """dictionnaire avec chaque prix arrondi et le nb de joeurs qui ont mise ce prix"""
        return {n.prix: len(n.joueurs) for n in self.parcours_infixe()}

    def est_vide(self):
        return self.racine is None
