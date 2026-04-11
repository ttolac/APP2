import matplotlib.pyplot as plt
from matplotlib.patches import Patch
from enchere import Manche

def afficher_graphique(chemin, format="simple", numero_manche=1, cout_base=1.0, alpha=5.0):
    manche = Manche(cout_base, alpha)
    if format == "multi":
        manche.charger_csv_multi_manches(chemin, numero_manche)
    else:
        manche.charger_csv(chemin)

    distrib  = manche.abr.distribution_prix()
    prix     = list(distrib.keys())
    nb       = list(distrib.values())
    couleurs = ["#2e7d4f" if n == 1 else "#b03030" for n in nb]

    fig, ax = plt.subplots(figsize=(10, 4))
    ax.bar(prix, nb, color=couleurs, edgecolor="white", linewidth=0.5)
    ax.set_title("Distribution des prix misés", fontsize=13, fontweight="bold", color="#1a3a5c")
    ax.set_xlabel("Prix", color="#1a3a5c")
    ax.set_ylabel("Nombre de joueurs", color="#1a3a5c")
    ax.set_facecolor("#f5f4f0")
    fig.patch.set_facecolor("#ffffff")

    legende = [Patch(color="#2e7d4f", label="Unique (candidat gagnant)"),
               Patch(color="#b03030", label="Non unique (éliminé)")]
    ax.legend(handles=legende)

    result = manche.determiner_gagnant()
    if result["statut"] == "gagnant":
        ax.annotate(f"Gagnant : {result['gagnant']}",
                    xy=(result["prix"], 1),
                    xytext=(result["prix"] + max(prix)*0.05, 1.5),
                    arrowprops=dict(arrowstyle="->", color="#1a3a5c"),
                    fontsize=9, color="#1a3a5c")

    plt.tight_layout()
    plt.show()