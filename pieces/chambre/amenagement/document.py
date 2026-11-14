# Chambre, aménagement : lit, chevets, plan sur deux commodes (V2.1). La pièce est dans ../piece.py.
#
# Ce fichier ne contient que des données : il est lu par les générateurs de la chambre. Toute modification se fait
# ici, jamais dans le HTML.
#
# Cotes en cm : x vers l'est depuis le nu du mur ouest, y vers le sud depuis le nu du mur nord, z depuis le sol fini.
# Les meubles sont des dicts x0, x1, y0, y1 (plan) et z0, z1 (hauteurs) ; une valeur absente est une valeur que la
# page ne donne pas.

from commun.modele import Changement, Document, Variante
from pieces.chambre.amenagement import dessin
from pieces.chambre.piece import (CAMERAS, CLIM, DECROCHE, EP, FENETRE, H, H_PORTE, ID, L, NOM, P, PLACARD, PORTE,  # noqa: F401
                                  PORTES, POSITION, SOL, SURFACE)

VERSION = "V2.1"

# versions figées : (version, chemin sous site/)
FIGEES_ANCIENNES = (("V1.2", "archive/chambre-amenagement-v1.2.html"),)

CHANGEMENTS = [
    ("V2.1", "04/10/2026", "Précisions du client. Lit sur sommier sans cadre : 160 × 200, pieds 22, sommier 25, matelas 35 (dessus à 82) ; tête de lit fixée au mur (168 × 4, de 50 à 140). Le pied du lit passe à 47 cm, 75 entre le lit et le plan. Chevets à 70 de haut, appliques à 140, prises à 85. Pas de radiateur ; ajout de la clim au plafond, mur nord, contre le décroché."),
    ("V2", "04/10/2026", "Demande du client : tout le mur est, sous la fenêtre, devient un plan de 241 × 42 posé sur deux commodes de 80 × 40 (dessus à 85) et sur une joue au nord. Patères réduites à 3, au-dessus du plan, au nord de la fenêtre. Niche à pantalons sous le plan (2 barres fixes, 6 pantalons). Chevet est réduit à 30 × 35 pour les tiroirs. Plus de variantes A/B : la V1.2 est archivée (archive/chambre-amenagement-v1.2.html)."),
    ("V1.2", "04/10/2026", "Correction du placard (relevé du client) : 164 de long, porte de 155 ; il n'y a donc pas de pan de mur libre à côté de la porte. La variante A devient un compartiment valet de 40 cm au nord du placard, avec cloison, 3 patères à 165 et une tablette, à la place du banc et des patères sur le mur."),
    ("V1.1", "04/10/2026", "Fenêtre comme celle de la cuisine : coulissante, sans battant (vantail fixe au nord, mobile au sud qui glisse vers le nord), allège 106, linteau 215. Décroché de 13 × 10 dans l'angle nord-est : la commode descend à y 12 → 97, sous l'allège. Ajout d'un coin pour les vêtements portés, en deux variantes : A, valet à l'entrée (banc 40 × 35 et 3 patères sur le trumeau du placard) ; B, 5 patères au-dessus de la commode."),
    ("V1", "04/10/2026", "Première proposition à partir du relevé : lit 160 × 200 tête au mur sud, centré entre le placard et le mur est (115 cm de chaque côté, 41 au pied), deux chevets 40 × 35, commode 85 × 40 au mur est au nord de la fenêtre. Plan et trois élévations (sud, est, ouest)."),
]

# ------------------------------------------------------------------ ① le lit
# Sommier sur pieds, sans cadre, centré entre le placard et le mur est (117 de chaque côté). Dessus du matelas à 82 :
# pieds 22 (0 → 22), sommier 25 (22 → 47), matelas 35 (47 → 82).
LIT = dict(x0=164, x1=324, y0=47, y1=247, z1=82, pieds=22, sommier=25, matelas=35)
# Panneau fixé au mur sud, 58 au-dessus du matelas.
TETE = dict(x0=160, x1=328, y0=247, y1=251, z0=50, z1=140)
COUETTE = dict(x0=166, x1=322, y0=49, y1=177)
# Deux oreillers de 68 × 34 posés sur le matelas (18 de haut).
OREILLERS = [dict(x0=172, x1=240, y0=203, y1=237, z0=82, z1=100),
             dict(x0=248, x1=316, y0=203, y1=237, z0=82, z1=100)]

# ------------------------------------------------------------------ ② chevets, appliques, prises
# Le chevet est est réduit à 30 pour laisser sortir les tiroirs de la commode sud.
CHEVET_OUEST = dict(x0=117, x1=157, y0=216, y1=251, z1=70)
CHEVET_EST = dict(x0=329, x1=359, y0=216, y1=251, z1=70)
# Appliques (h 140, corps de 8 × 8 de z 135 à 143) et prises (h 85, 10 × 4 de z 83 à 87), au-dessus de chaque chevet.
APPLIQUES = dict(x=(137, 344), h=140, l=8, z0=135, z1=143)
PRISES = dict(x=(137, 344), h=85, l=10, z0=83, z1=87)

# ------------------------------------------------------------------ ③ plan sur deux commodes, mur est
# Plan de bois de 241 × 42, du décroché au mur sud, dessus à 85 ; il dépasse de 2 devant les commodes. Pas de z0 :
# la fiche dit « h 85 » et l'épaisseur est ep.
PLAN = dict(x0=399, x1=441, y0=10, y1=251, z1=85, ep=3)
COMMODE_NORD = dict(x0=401, x1=441, y0=91, y1=171, z1=82)
COMMODE_SUD = dict(x0=401, x1=441, y0=COMMODE_NORD["y1"], y1=251, z1=82)
# Quatre tiroirs par commode : séparations (z) et poignées (z du bas ; 12 de large, 2 de haut) vues en élévation.
COMMODE = dict(tiroirs=4, separations=(20, 41, 62), poignees=(71, 50, 29, 9), poignee_l=12, poignee_h=2)
# Joue de 2 au nord des commodes, qui porte le plan.
JOUE = dict(x0=401, x1=441, y0=10, y1=12, z1=82)
# ------------------------------------------------------------------ ④ niche à pantalons et patères
# Deux barres fixes parallèles au mur, décalées : (x, h), devant (côté pièce, x 413) à 70, derrière à 76 ; 3 pantalons
# par barre.
NICHE = dict(x0=401, x1=441, y0=12, y1=91, z1=82, barres=((413, 70), (429, 76)), pantalons=3)
PATERES = dict(x=439.5, y=(28, 48, 68), z=165)
# Zone de débattement d'un tiroir ouvert de la commode nord (pas un meuble) : 35 de profondeur.
TIROIR_OUVERT = dict(x0=COMMODE_NORD["x0"] - 35, x1=COMMODE_NORD["x0"], y0=95, y1=167)

# Cercle au centre du lit dans le plan, que la page n'explique pas.
LAMPE = dict(cx=244, cy=149, r=5)


def passages(M):
    """Les six passages cotés du plan, dont les bouts sont tirés des meubles du module M (le module `document`)."""
    return [
        dict(a=(250, 0), b=(250, M.LIT["y0"])),                                    # pied du lit
        dict(a=(M.PLACARD["x1"], 180), b=(M.LIT["x0"], 180)),                      # placard → lit
        dict(a=(M.PLACARD["x1"], 226), b=(M.CHEVET_OUEST["x0"], 226)),             # placard → chevet ouest
        dict(a=(M.LIT["x1"], 70), b=(M.PLAN["x0"], 70)),                           # lit → plan
        dict(a=(M.LIT["x1"], 185), b=(M.TIROIR_OUVERT["x0"], 185)),                # lit → tiroir ouvert
        dict(a=(M.CHEVET_EST["x1"], 233), b=(M.TIROIR_OUVERT["x0"], 233)),         # chevet est → tiroir
    ]


# ------------------------------------------------------------------ meubles touchables du plan
# Une zone par meuble, son id stable ; carte : rang de la carte « Principe » (vues.PRINCIPES) qui fait sa fiche ;
# coupe : l'élévation où il se voit. Un bord donné ici remplace celui du meuble : la zone « commodes » part du nu nord
# de la commode nord, la zone « niche » prend le plan qui la couvre. cotes="largeur" : la fiche donne largeur (x) ×
# profondeur (y), comme la page pour le lit (« 160 × 200 ») et les chevets (« 30 × 35 »), au lieu du grand côté
# d'abord.
ZONES = (
    dict(id="lit", meuble="LIT", carte=0, coupe="sud", cotes="largeur"),
    dict(id="chevet_ouest", meuble="CHEVET_OUEST", carte=1, coupe="sud", cotes="largeur"),
    dict(id="chevet_est", meuble="CHEVET_EST", carte=1, coupe="sud", cotes="largeur"),
    dict(id="commodes", meuble="PLAN", y0=COMMODE_NORD["y0"], carte=2, coupe="est"),
    dict(id="niche", meuble="NICHE", x0=PLAN["x0"], y0=PLAN["y0"], carte=3, coupe="est"),
)


def _document():
    # import ici : vues importe ce module
    from pieces.chambre.amenagement import vues
    changements = tuple(Changement(*c) for c in CHANGEMENTS)
    return Document(piece="chambre", id="amenagement", nom="Aménagement", type="amenagement",
                    variantes=(Variante("", "Principale", VERSION, changements, FIGEES_ANCIENNES),),
                    generer=vues.vues, css=dessin.CSS)


def __getattr__(nom):
    if nom == "DOCUMENT":
        globals()["DOCUMENT"] = _document()
        return globals()["DOCUMENT"]
    raise AttributeError(f"module {__name__!r} has no attribute {nom!r}")
