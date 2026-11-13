# Salon : la pièce (enveloppe, passage, baie) et les caméras communes à tous ses documents.
#
# Ce fichier ne contient que des données, reprises de 3d/salon/modele.py (V4.26) et des points de vue de
# 3d/salon/rendu.py. Les meubles sont dans amenagement/document.py ; l'enfilade et les étagères, qui ont leur
# document, dans enfilade/document.py et etageres/document.py.
#
# Cotes en cm : x vers l'est depuis le mur ouest, y vers le sud depuis le mur nord, z depuis le sol fini.
# Chaque volume : Bloc(role, nom, x0, x1, y0, y1, z0, z1). Le rôle fixe le style du plan et des coupes.

from dataclasses import dataclass

from commun.modele import Camera

ID = "salon"
NOM = "Salon"
# x, y (cm) et rotation (degrés) dans le repère de l'appartement (celui du couloir, pieces/entree/piece.py) : le coin
# nord-ouest du salon, posé comme dans le plan de l'accueil (commun/appartement.py, APPART)
POSITION = (274, -263, 0)

H = 254.5               # hauteur sous plafond (relevée)
L, P = 547, 367         # salon : 547 (ouest → est) × 367 (nord → sud), relevé du client (V4.12)
EP = 12                 # épaisseur dessinée des murs


@dataclass
class Bloc:
    role: str
    nom: str
    x0: float
    x1: float
    y0: float
    y1: float
    z0: float
    z1: float
    etiq: str = ""      # nom affiché sur le plan et les coupes
    contenu: str = ""   # ce qu'on range derrière (écrit sur les coupes)
    config: str = ""    # "" : toujours ; "f" / "o" : seulement avec la table fermée ou ouverte
    deco: bool = False  # décoration (tapis, luminaires, plantes, cadres, livres) : affichée par le bouton Déco
    assise: str = ""    # "" : toujours ; "dyv" / "chil" : seulement avec le siège DYVLINGE ou la chilienne


@dataclass
class Cyl:
    role: str
    nom: str
    cx: float
    cy: float
    r: float
    z0: float
    z1: float
    config: str = ""
    deco: bool = False
    assise: str = ""
    etiq = ""
    contenu = ""

    x0 = property(lambda c: c.cx - c.r)
    x1 = property(lambda c: c.cx + c.r)
    y0 = property(lambda c: c.cy - c.r)
    y1 = property(lambda c: c.cy + c.r)


# ------------------------------------------------------------------ enveloppe (relevé)
# Cotes relevées par le client (V4.12 → V4.15) : G 547, M 367, C 10, D 62,5, F 90, L 257,6, J 82, coffre sud-ouest
# 32 × 17, B 131, plafond 254,5, dessous de la poutre sud 231,7. Pas encore relevés : cadres du passage, clim.
# Mur ouest : cloison du cellier et du WC, puis le passage sans porte vers le couloir, un cadre de chaque côté ; le
# cadre sud est collé au coffre. Les cadres ne sont pas relevés : 257,6 + 82 + 2 cadres = 367 − 17 donne 10,4 pour
# les deux, soit 5,2 chacun (supposés égaux).
# Mur est : baie coulissante 2 vantaux, sans allège (y 72,5 → 277, soit 204,5 déduit de M − C − D − F, h 215).
# Décroché nord-est : sur les 131 derniers cm (B relevé, x 416 → 547), le mur nord est 10 cm plus au sud.
# Coffre plein dans l'angle sud-ouest : 32 le long du mur sud, 17 de saillie.
PASSAGE = dict(h=204, cadre=(P - 17 - 257.6 - 82) / 2)
PASSAGE["y0"] = 257.6 + PASSAGE["cadre"]
PASSAGE["y1"] = PASSAGE["y0"] + 82
COFFRE = dict(x1=32, y0=P - 17)
# Poutre tout le long du mur sud, même saillie que le coffre (17, supposée), dessous à 231,7 (relevé).
POUTRE = dict(y0=P - 17, z0=231.7)
DECROCHE = dict(x0=L - 131, y=10)
BAIE = dict(y0=DECROCHE["y"] + 62.5, y1=P - 90, h=215)
BAIE["milieu"] = (BAIE["y0"] + BAIE["y1"]) / 2
# Climatisation existante : unité murale sur le mur sud, tout à l'est (position et dimensions à relever), sous la
# poutre (dessous à 231,7).
CLIM = dict(x0=L - 94, x1=L - 4, p=22, z0=200, z1=230)

# Sol : contour intérieur, du coin nord-ouest dans le sens des aiguilles d'une montre (décroché nord-est, coffre
# sud-ouest déduits). Le passage du mur ouest n'en fait pas partie.
SOL = [(0, 0), (DECROCHE["x0"], 0), (DECROCHE["x0"], DECROCHE["y"]), (L, DECROCHE["y"]), (L, P), (COFFRE["x1"], P),
       (COFFRE["x1"], COFFRE["y0"]), (0, COFFRE["y0"])]
# m², calculée sur le contour (pas de relevé de surface)
SURFACE = abs(sum(x0 * y1 - x1 * y0 for (x0, y0), (x1, y1) in zip(SOL, SOL[1:] + SOL[:1]))) / 2 / 1e4

# Ouvertures, sur le modèle de pieces/entree/piece.py : mur, ouverture (a → b le long du mur), face (coordonnée du nu
# du mur côté salon), hauteur de passage.
PORTES = [
    dict(nom="passage", piece="Entrée", mur="o", face=0, a=PASSAGE["y0"], b=PASSAGE["y1"], h=PASSAGE["h"],
         type="passage"),
]
FENETRES = [
    dict(nom="baie", mur="e", face=L, a=BAIE["y0"], b=BAIE["y1"], h=BAIE["h"], type="coulissante", vantaux=2,
         allege=0),
]

ENVELOPPE = [
    Bloc("mur", "mur_nord", -10, L + EP, -12, 0, 0, H),
    Bloc("mur", "mur_nord_decroche", DECROCHE["x0"], L + EP, 0, DECROCHE["y"], 0, H),
    Bloc("mur", "mur_sud", -10, L + EP, P, P + 12, 0, H),
    Bloc("mur", "mur_ouest_n", -10, 0, 0, PASSAGE["y0"], 0, H),
    Bloc("mur", "mur_ouest_s", -10, 0, PASSAGE["y1"], P, 0, H),
    Bloc("mur", "coffre_so", 0, COFFRE["x1"], COFFRE["y0"], P, 0, H),
    Bloc("poutre", "poutre_sud", 0, L, POUTRE["y0"], P, POUTRE["z0"], H),
    Bloc("linteau", "linteau_passage", -10, 0, PASSAGE["y0"], PASSAGE["y1"], PASSAGE["h"], H),
    Bloc("cadre", "cadre_passage_n", -11, 1.5, PASSAGE["y0"] - PASSAGE["cadre"], PASSAGE["y0"], 0, PASSAGE["h"] + 10),
    Bloc("cadre", "cadre_passage_s", -11, 1.5, PASSAGE["y1"], PASSAGE["y1"] + PASSAGE["cadre"], 0, PASSAGE["h"] + 10),
    Bloc("mur", "mur_est_n", L, L + EP, DECROCHE["y"], BAIE["y0"], 0, H),
    Bloc("mur", "mur_est_s", L, L + EP, BAIE["y1"], P, 0, H),
    Bloc("linteau", "linteau_baie", L, L + EP, BAIE["y0"], BAIE["y1"], BAIE["h"], H),
    Bloc("baie", "baie_est", L, L + EP, BAIE["y0"], BAIE["y1"], 0, BAIE["h"]),
    # papier peint du mur nord du décroché (finition : amenagement/document.py, PAPIER_PEINT)
    Bloc("papier_peint", "papier_desserte", DECROCHE["x0"], L, DECROCHE["y"], DECROCHE["y"] + 0.3, 0, H),
    Bloc("clim", "clim", CLIM["x0"], CLIM["x1"], P - CLIM["p"], P, CLIM["z0"], CLIM["z1"]),
]
MURS = [b for b in ENVELOPPE if b.role == "mur"]

# ------------------------------------------------------------------ caméras, communes aux documents
# Points de vue de 3d/salon/rendu.py (VIEWS) ; coupes : objets Blender cachés à la caméra (motif sur leur nom).
# Les vues iso_noyer et iso_no_noyer de l'ancien rendu sont ces deux caméras avec tout le chêne en noyer : un réglage
# de la scène (essence), pas une caméra.
COUPES_ISO = r"^(mur__(mur_sud|mur_est_n|mur_est_s|couloir)|sol__couloir|linteau__linteau_baie|poutre__|plafond__|clim__|plinthe__(sud|est_)|baie__|rideau__|tringle__)"
COUPES_ISO_NO = (r"^(mur__(mur_nord|mur_nord_decroche|mur_ouest_n|mur_ouest_s|couloir)|sol__couloir|papier_peint__"
                 r"|linteau__linteau_passage|cadre__cadre_passage|cadre_mur__|plafond__|plinthe__(nord|ouest_n))")
CX, CY = 272, 179
CAMERAS = (
    # isométrique depuis le sud-est (murs sud et est et plafond coupés) : enfilade et étagères (ouest), canapé,
    # cadres et desserte (nord)
    Camera("iso", "Isométrique sud-est", (CX + 640, CY + 600, 600), (CX, CY, 70), ortho=8.2,
           reglages=dict(coupes=COUPES_ISO)),
    # vue opposée, depuis le nord-ouest (murs nord et ouest et plafond coupés) : écran et meuble bas (sud), baie et
    # rideau (est), table ronde ; le passage, les cadres du mur nord et le papier peint partent avec leurs murs
    Camera("iso_no", "Isométrique nord-ouest", (CX - 640, CY - 600, 600), (CX, CY, 70), ortho=8.2,
           reglages=dict(coupes=COUPES_ISO_NO)),
)
