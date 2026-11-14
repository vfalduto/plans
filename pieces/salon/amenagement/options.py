"""Options « choix » du salon/aménagement (Personnaliser) : les réglages que l'ancienne page offrait au lecteur, par des
boutons posés sur ses dessins (Table, Siège, Déco) et sous ses rendus (Bois). Les dessins (dessins.py) marquent chaque
état de son jeton ; les rendus (vues.py) portent une image par valeur du bois.

Défauts : ceux de l'ancienne page (table au quotidien, DYVLINGE, déco masquée, chêne). Les rendus montrent la table du
quotidien, le DYVLINGE et la décoration (rendu.py, CONFIG et ASSISE).
"""
from commun.blocs import jeton, si
from commun.modele import Option, Valeur

# les noms des valeurs de la table sont ceux de CONFIGS dans le modèle (quotidien, ouverte) avec leur nombre de couverts
TABLE = Option("table", "Table", (), "choix", "quotidien",
               (Valeur("quotidien", "Au quotidien, 4 couverts"), Valeur("ouverte", "Ouverte, 12 couverts", rendue=False)),
               "Visible sur le plan et les coupes ; les rendus montrent la table du quotidien.")
SIEGE = Option("siege", "Siège", (), "choix", "dyvlinge",
               (Valeur("dyvlinge", "DYVLINGE"), Valeur("chilienne", "Chilienne", rendue=False)),
               "Visible sur le plan et les coupes ; les rendus montrent le DYVLINGE.")
# les rendus montrent toujours la déco : la portée le dit, aucune valeur n'est « pas encore rendue » (rendue=True)
DECO = Option("deco", "Décoration", (), "choix", "masquee",
              (Valeur("masquee", "Masquée"), Valeur("affichee", "Affichée")),
              "Visible sur le plan et les coupes ; les rendus la montrent toujours.")
BOIS = Option("bois", "Bois des meubles", (), "choix", "chene",
              (Valeur("chene", "Chêne miel"), Valeur("noyer", "Noyer")),
              "Visible sur les rendus iso ; le plan et les coupes ne changent pas. En noyer, tout le chêne (enfilade, "
              "étagères, desserte, table basse, meuble bas) passe en noyer.")
OPTIONS = (TABLE, SIEGE, DECO, BOIS)

QUOTIDIEN, OUVERTE = jeton(TABLE, "quotidien"), jeton(TABLE, "ouverte")
DYVLINGE, CHILIENNE = jeton(SIEGE, "dyvlinge"), jeton(SIEGE, "chilienne")
AFFICHEE = jeton(DECO, "affichee")
JETON_TABLE = {"f": QUOTIDIEN, "o": OUVERTE}
JETON_SIEGE = {"dyv": DYVLINGE, "chil": CHILIENNE}


def marque_bloc(b) -> str:
    """` data-si="…"` d'un bloc du modèle : sa table (`config`), son siège (`assise`) et sa déco ; rien s'il est
    toujours là."""
    return si(JETON_TABLE.get(b.config, ""), JETON_SIEGE.get(b.assise, ""), AFFICHEE if b.deco else "")


def essences_rendues():
    """Un Blender par bois rendu : [(variable de la scène, code, suffixe du fichier)] ; le chêne, valeur d'origine,
    garde le nom sans suffixe (rendus/iso_se.jpg, rendus/iso_se-noyer.jpg)."""
    return [("SALON_ESSENCE", v.code, "" if v.code == "chene" else f"-{v.code}") for v in BOIS.valeurs if v.rendue]
