# Entrée, version Victor : variante de la V4.3 (document.py), même relevé, même entrée en India.
#
# Lu par les vues de l'entrée (vues.py, dessin_victor.py ; just entree) et par rendu.py (ENTREE_VARIANTE=victor,
# just entree-rendu). Toute modification se fait ici.
#
# Différences avec la V4.3 :
#   - rien sous le tableau électrique (mur nord libre) ;
#   - meuble à chaussures bas à abattants à la place de la penderie, contre la face nord de la salle de bain, terminé
#     par un arrondi qui rejoint la façade du PAX ; deux étagères flottantes au-dessus ;
#   - penderie IKEA PAX contre la cloison de la salle de bain, à la place du premier module du meuble à chaussures et
#     du meuble haut ; angle arrondi retiré ;
#   - second module du meuble à chaussures remplacé par une planche à chaussures sous les patères ;
#   - miroir et cadres sur le mur ouest de l'entrée.

from pieces.entree import piece
from pieces.entree.amenagement import document
# noms de la pièce et de la principale que les dessins, les vues et rendu.py lisent à travers ce module (M.SOL,
# M.CARRELAGE…), comme dans document.py
from pieces.entree.piece import Bloc, EP, ENVELOPPE, H, H_PORTE, MURS, PORTES, SOL, SURFACE  # noqa: F401
from pieces.entree.amenagement.document import (CARRELAGE, INDIA, INTERPHONE, MUR_COULEUR, PATERE, PATERES,  # noqa: F401
                                                TABLEAU)

VERSION = "V1.5"
BASE = "V4.3"           # version de la page principale dont cette variante est tirée

# ------------------------------------------------------------------ ③ penderie IKEA PAX (V1.2)
# Contre la cloison de la salle de bain (x 110), à partir de son coin (y 208) : caisson PAX 75 × 35 × 236 posé au sol,
# une porte FORSAND 50 × 229 et une 25 × 229 (règle IKEA pour un caisson de 75), vers l'ouest. Profondeur 35 + porte
# 2 : 73 de passage devant. À 35, les cintres se suspendent de face (tringle KOMPLEMENT 75 × 35, 12 kg), pas
# d'extractible dans cette profondeur. Le haut de la penderie, derrière les mêmes portes, remplace le meuble haut :
# deux tablettes. Bandeau de 14 du caisson (236) au plafond (250). V1.4 : caisson, portes et bandeau peints en India,
# comme les murs de l'entrée (FORSAND blanc repeint).
PENDERIE = dict(x0=73, x1=110, y0=208, y1=283, z1=236, socle=0, facade=2, portes=(50, 25), tringle=180,
                etageres=(196, 216), manteaux=10)
BANDEAU = dict(z0=PENDERIE["z1"], z1=H)
IKEA = [   # prix IKEA France relevés le 13/11/2026 (fiches produit, blanc)
    ("PAX caisson d'armoire 75 × 35 × 236", "604.582.27", 1, 80),
    ("FORSAND porte 50 × 229", "603.910.91", 1, 39),
    ("FORSAND porte 25 × 229", "804.236.04", 1, 34),
    ("KOMPLEMENT tringle à habits 75 × 35", "804.464.55", 1, 12),
]

# ------------------------------------------------------------------ ① meuble à chaussures (V1.3, remplace le banc)
# Contre la face nord de la salle de bain, comme celui de la V4.3 mais d'un seul niveau d'abattants et plus profond.
# V1.4 : tout est tracé depuis un seul centre, le coin de la salle de bain (x 110, y 208) : le meuble prend la
# profondeur du PAX porte comprise (37), et son bout ouest est un quart de cercle de rayon 37 centré sur ce coin,
# tangent à la fois à la façade du PAX (x 73) et à celle des abattants (y 171), sans plat ; le socle en retrait de 4
# (R 33) et les étagères flottantes (R 25) suivent des arcs concentriques. Socle de 8 en retrait : le meuble flotte.
# Deux abattants de 42 (≈ 4 paires chacun), plateau vide-poche en chêne à 53.
CENTRE_ARRONDI = (110, 208)
CHAUSSURES = dict(x0=73, xa=110, x1=194, y0=171, y1=208, z1=50, plateau=3, facade=2, socle=8, retrait=4)
CHAUSSURES["r"] = CENTRE_ARRONDI[0] - CHAUSSURES["x0"]          # 37
CHAUSSURES["modules"] = [(110, 152), (152, 194)]

# ------------------------------------------------------------------ étagères flottantes au-dessus du meuble à chaussures
# Fixations invisibles dans la cloison ; 25 de profondeur, la première à 160 pour garder la tête libre assis.
# V1.4 : arrondies au bout ouest, arc de rayon 25 concentrique à celui du meuble ; elles vont jusqu'au flanc du PAX.
ETAGERES = dict(x0=CENTRE_ARRONDI[0] - 25, x1=192, y0=CENTRE_ARRONDI[1] - 25, y1=208, z=(160, 195), ep=3, r=25)

# ------------------------------------------------------------------ ⑤ planche à chaussures sous les patères (V1.1)
# Contre la cloison de la salle de bain, de la penderie au mur sud ; dessus à 25 sur deux pieds pleins : chaussures
# dessous (22 de haut) et dessus. 28 de profondeur : la porte d'entrée ouverte à 90° (vantail sur x 77 → 81) vient
# juste contre son chant, elle lui sert de butée.
PLANCHE = dict(x0=82, x1=110, y0=PENDERIE["y1"] + 1, y1=373, z1=25, ep=3, pied=2)   # V1.2 : 89 de long (PAX de 75)
PAIRES_MEUBLE, PAIRES_PLANCHE = 8, 9
PAIRES = PAIRES_MEUBLE + PAIRES_PLANCHE

# ------------------------------------------------------------------ mur ouest de l'entrée (V1.1) : cadres et miroir
# Du jambage de la pièce ouest (y 160) à l'interphone (y 335) : miroir 50 × 100 à coins arrondis juste au nord de
# l'interphone, puis une galerie de 4 cadres 30 × 40 (grille 2 × 2, 6 d'écart : cadres identiques, écarts égaux et
# serrés), centrée sur le mur libre entre la porte et le miroir et à la même hauteur que le centre du miroir (160).
MIROIR = dict(y0=INTERPHONE["y0"] - 8 - 50, y1=INTERPHONE["y0"] - 8, z0=110, z1=210, r=12)
CADRES = dict(l=30, h=40, ecart=6, colonnes=2, rangs=2, zc=(MIROIR["z0"] + MIROIR["z1"]) / 2, ep=2.5)
_lg = CADRES["colonnes"] * CADRES["l"] + (CADRES["colonnes"] - 1) * CADRES["ecart"]
_hg = CADRES["rangs"] * CADRES["h"] + (CADRES["rangs"] - 1) * CADRES["ecart"]
CADRES["yc"] = (160 + MIROIR["y0"]) / 2
CADRES["y0"], CADRES["y1"] = CADRES["yc"] - _lg / 2, CADRES["yc"] + _lg / 2
CADRES["z0"], CADRES["z1"] = CADRES["zc"] - _hg / 2, CADRES["zc"] + _hg / 2
APPLIQUE = dict(y=338, z=220)           # au-dessus des patères

MEUBLES = [
    Bloc("tableau", "tableau", TABLEAU["x0"], TABLEAU["x1"], -1, 0.5, TABLEAU["z0"], TABLEAU["z1"], "tableau", mur="n"),
    # meuble à chaussures : socle en retrait, caisson, arrondi plein, plateau (étiquette posée par la coupe C)
    Bloc("socle", "chaussures_socle", CHAUSSURES["xa"], CHAUSSURES["x1"] - CHAUSSURES["retrait"],
         CHAUSSURES["y0"] + CHAUSSURES["retrait"], CHAUSSURES["y1"], 0, CHAUSSURES["socle"]),
    Bloc("socle", "chaussures_socle_arrondi", CHAUSSURES["x0"] + CHAUSSURES["retrait"], CHAUSSURES["xa"],
         CHAUSSURES["y0"] + CHAUSSURES["retrait"], CHAUSSURES["y1"], 0, CHAUSSURES["socle"],
         arrondi=CHAUSSURES["r"] - CHAUSSURES["retrait"]),
    Bloc("caisson", "chaussures", CHAUSSURES["xa"], CHAUSSURES["x1"], CHAUSSURES["y0"] + CHAUSSURES["facade"],
         CHAUSSURES["y1"], CHAUSSURES["socle"], CHAUSSURES["z1"]),
    Bloc("caisson", "chaussures_arrondi", CHAUSSURES["x0"], CHAUSSURES["xa"], CHAUSSURES["y0"], CHAUSSURES["y1"],
         CHAUSSURES["socle"], CHAUSSURES["z1"], arrondi=CHAUSSURES["r"]),
    Bloc("plateau", "vide_poche", CHAUSSURES["x0"], CHAUSSURES["x1"], CHAUSSURES["y0"], CHAUSSURES["y1"], CHAUSSURES["z1"],
         CHAUSSURES["z1"] + CHAUSSURES["plateau"], arrondi=CHAUSSURES["r"]),
    # planche à chaussures
    Bloc("banc", "planche", PLANCHE["x0"], PLANCHE["x1"], PLANCHE["y0"], PLANCHE["y1"], PLANCHE["z1"] - PLANCHE["ep"],
         PLANCHE["z1"], mur="e"),
    Bloc("banc", "planche_pied_n", PLANCHE["x0"] + 2, PLANCHE["x1"], PLANCHE["y0"], PLANCHE["y0"] + PLANCHE["pied"], 0,
         PLANCHE["z1"] - PLANCHE["ep"], mur="e"),
    Bloc("banc", "planche_pied_s", PLANCHE["x0"] + 2, PLANCHE["x1"], PLANCHE["y1"] - PLANCHE["pied"], PLANCHE["y1"], 0,
         PLANCHE["z1"] - PLANCHE["ep"], mur="e"),
    # penderie (corps, socle ; portes plus bas)
    Bloc("tall_i", "penderie", PENDERIE["x0"] + PENDERIE["facade"], PENDERIE["x1"], PENDERIE["y0"], PENDERIE["y1"],
         PENDERIE["socle"], PENDERIE["z1"], "③ penderie PAX"),
    Bloc("tall_i", "bandeau", PENDERIE["x0"] + PENDERIE["facade"], PENDERIE["x0"] + PENDERIE["facade"] + 1.8,
         PENDERIE["y0"], PENDERIE["y1"], BANDEAU["z0"], BANDEAU["z1"]),
    # mur ouest : miroir, interphone ; mur de la salle de bain : applique
    Bloc("miroir", "miroir", 0, 0.6, MIROIR["y0"], MIROIR["y1"], MIROIR["z0"], MIROIR["z1"], mur="o"),
    Bloc("interphone", "interphone", 0, 3, INTERPHONE["y0"], INTERPHONE["y1"], INTERPHONE["z0"], INTERPHONE["z1"], mur="o"),
    Bloc("applique", "applique", 104, 110, APPLIQUE["y"] - 6, APPLIQUE["y"] + 6, APPLIQUE["z"] - 6, APPLIQUE["z"] + 6, mur="e"),
] + [Bloc("plateau", f"etagere_{z}", ETAGERES["x0"], ETAGERES["x1"], ETAGERES["y0"], ETAGERES["y1"], z, z + ETAGERES["ep"],
          arrondi=ETAGERES["r"])
     for z in ETAGERES["z"]] \
  + [Bloc("patere", f"patere_{k}", 110 - PATERE["saillie"], 110, y - PATERE["d"] / 2, y + PATERE["d"] / 2,
          PATERE["z"] - PATERE["d"] / 2, PATERE["z"] + PATERE["d"] / 2, mur="e") for k, y in enumerate(PATERES)]

for i in range(CADRES["colonnes"]):
    for j in range(CADRES["rangs"]):
        _yc = CADRES["y0"] + i * (CADRES["l"] + CADRES["ecart"])
        _zc = CADRES["z0"] + j * (CADRES["h"] + CADRES["ecart"])
        MEUBLES.append(Bloc("cadre_mur", f"cadre_{i}{j}", 0, CADRES["ep"], _yc, _yc + CADRES["l"], _zc, _zc + CADRES["h"], mur="o"))

# abattants du meuble à chaussures, face au nord
for k, (x0, x1) in enumerate(CHAUSSURES["modules"]):
    MEUBLES.append(Bloc("facade", f"abattant_{k}", x0 + 0.2, x1 - 0.2, CHAUSSURES["y0"], CHAUSSURES["y0"] + CHAUSSURES["facade"],
                        CHAUSSURES["socle"] + 0.2, CHAUSSURES["z1"] - 0.2))

# portes FORSAND de la penderie, face à l'ouest : 50 au nord, 25 au sud
_yj = PENDERIE["y0"] + PENDERIE["portes"][0]          # joint des deux portes
for k, (y0, y1) in enumerate(((PENDERIE["y0"], _yj), (_yj, PENDERIE["y1"]))):
    MEUBLES.append(Bloc("facade_pi", f"porte_penderie_{k}", PENDERIE["x0"], PENDERIE["x0"] + PENDERIE["facade"],
                        y0 + 0.2, y1 - 0.2, 3.5, 3.5 + 229.4))

# peinture India : comme la V4.3, à partir de y 168 ; la penderie PAX aussi (V1.4)
_y = INDIA["y0"]
MEUBLES += [
    Bloc("india", "india_ouest", 0, 0.3, _y, 374, 0, H, mur="o"),
    Bloc("india", "india_sdb", 109.7, 110, 208, 374, 0, H, mur="e"),
    Bloc("india", "india_sud_o", 0, 2, 373.7, 374, 0, H, mur="s"),
    Bloc("india", "india_sud_e", 77, 110, 373.7, 374, 0, H, mur="s"),
    Bloc("india", "india_sud_linteau", 2, 77, 373.7, 374, H_PORTE, H, mur="s"),
    Bloc("india_plafond", "india_plafond", 0, 110, _y, 374, H - 0.3, H, mur="p"),
]

# poignées (rendu) : barres verticales de part et d'autre du joint des portes
POIGNEES = [(f"penderie_{dy}", PENDERIE["x0"] - 1.5, PENDERIE["x0"], _yj + dy, _yj + dy + 1, 104, 128) for dy in (-6, 5)]
POIGNEES += [(f"abattant_{k}", (x0 + x1) / 2 - 6, (x0 + x1) / 2 + 6, CHAUSSURES["y0"] - 1.2, CHAUSSURES["y0"],
              CHAUSSURES["z1"] - 8, CHAUSSURES["z1"] - 7) for k, (x0, x1) in enumerate(CHAUSSURES["modules"])]

# ------------------------------------------------------------------ silhouettes de 1,75 m (rendus, homme semi-transparent
# de rendu.py) : au milieu du couloir devant le meuble à chaussures, et dans la branche d'entrée devant le miroir
POSITIONS_HUMAINS = {"couloir": (150, 95), "entree": (36, 300)}

# ------------------------------------------------------------------ dégagements (cm)
PASSAGES = [
    dict(a=(0, 245), b=(PENDERIE["x0"], 245), label=f"{PENDERIE['x0']}"),
    dict(a=(0, 312), b=(PLANCHE["x0"], 312), label=f"{PLANCHE['x0']}"),
    dict(a=(150, 0), b=(150, CHAUSSURES["y0"]), label=f"{CHAUSSURES['y0']}"),
    dict(a=(230, 104), b=(230, 208), label="104"),
]

# ------------------------------------------------------------------ vues 3D (rendu.py)
# silhouette de chaque caméra (les caméras elles-mêmes sont celles de la pièce)
HUMAINS = {"iso_no": "entree", "iso_so": "couloir", "iso_se": "entree"}

# meubles touchables du plan (cm)
ZONES = (
    dict(x0=73, y0=171, x1=194, y1=208, principe=0, cotes="121 × 37, h 53", coupe="C", iso="no"),
    dict(x0=73, y0=208, x1=110, y1=283, principe=1, cotes="75 × 35, h 236", coupe="B", iso="no"),
    dict(x0=82, y0=284, x1=110, y1=373, principe=2, cotes="89 × 28, h 25", coupe="B", iso="no"),
    dict(x0=0, y0=215, x1=9, y1=350, principe=3, cotes="mur ouest de l'entrée", coupe="D", iso="se"),
)
RENDUS = [("iso_no", "Isométrique depuis le nord-ouest : meuble à chaussures arrondi et étagères, penderie PAX, "
                     "planche à chaussures sous les patères"),
          ("iso_so", "Isométrique depuis le sud-ouest : mur nord libre sous le tableau, penderie PAX, planche"),
          ("iso_se", "Isométrique depuis le sud-est, cloison de la salle de bain retirée : mur ouest en India avec cadres, "
                     "miroir et interphone ; dos de la penderie, meuble à chaussures et étagères"),
          ("couloir", "Debout devant la porte de la pièce ouest : meuble à chaussures et son arrondi contre le PAX, étagères flottantes")]

CHANGEMENTS = [
    ("V1.5", "13/11/2026", "Sélecteur « Teinte » dans la barre du haut : les 52 teintes Plum Living (40 laques de "
     "façade, 30 peintures murales, relevées sur plum-living.com), groupées selon la gamme. Il change ensemble toutes "
     "les surfaces India : plan, coupes et vues 3D, sans un rendu par couleur (rendu neutre + masque, recoloré par "
     "un filtre SVG : un mur bien éclairé prend la teinte affichée par Plum Living). Choix gardé d'une page de l'entrée à l'autre. Constat : India "
     "n'existe pas en peinture murale chez Plum Living."),
    ("V1.4", "13/11/2026", "Arrondi retravaillé : le meuble à chaussures prend la profondeur du PAX porte comprise "
     "(37) et son bout est un quart de cercle de rayon 37 centré sur le coin de la salle de bain, tangent à la façade "
     "du PAX et à celle des abattants, sans plat ; socle de 8 en retrait de 4 qui suit le même arc. Étagères flottantes "
     "arrondies au bout ouest (R 25, même centre), prolongées jusqu'au flanc du PAX. PAX (caisson, portes, bandeau) "
     "peint en India comme les murs de l'entrée. Silhouette semi-transparente de 1,75 m dans les vues isométriques."),
    ("V1.3", "13/11/2026", "Banc remplacé par un meuble à chaussures bas, comme celui de la V4.3 mais d'un seul niveau "
     "et plus profond : 35, deux abattants de 42 (≈ 8 paires), plateau vide-poche à 53. Il se prolonge vers l'ouest "
     "jusqu'à la façade du PAX par un quart de cercle plein de rayon 35. Passage de 73 entre l'arrondi et le mur ouest, "
     "173 entre le meuble et le mur nord ; étagères flottantes gardées au-dessus."),
    ("V1.2", "13/11/2026", "Penderie et meuble haut remplacés par une penderie IKEA PAX : caisson 75 × 35 × 236, portes "
     "FORSAND blanches 50 et 25 × 229, tringle KOMPLEMENT pour cintres de face, deux tablettes en haut à la place du "
     "meuble haut, bandeau de 14 jusqu'au plafond (≈ 165 € hors charnières). Passage devant la penderie 73 au lieu de "
     "70. Planche à chaussures allongée à 89 pour reprendre les 8 cm libérés."),
    ("V1.1", "13/11/2026", "Meuble haut déplacé au-dessus de la penderie (mêmes nus, 83 × 40, de 204 au plafond, laque "
     "India) : il ne dépasse plus du coin de la salle de bain. Banc rehaussé à 50 (étagère à chaussures à 24). Angle "
     "arrondi et ses étagères retirés : 110 de passage à cet endroit. Planche à chaussures sous les patères, dessus à 25 "
     "sur deux pieds, chaussures dessous et dessus ; elle sert de butée à la porte d'entrée. Miroir 50 × 100 sur le mur "
     "ouest, à côté de l'interphone, et galerie de 4 cadres 30 × 40 entre la porte de la pièce ouest et le miroir."),
    ("V1.0", "13/11/2026", "Variante tirée de l'entrée V4.3 selon les choix de Victor : plus rien sous le tableau "
     "électrique ; banc à chaussures (84 × 40, deux niveaux de chaussures) et deux étagères flottantes à la place de la "
     "penderie, contre la face nord de la salle de bain ; penderie (83 × 40, haut à 204, laque India) contre la cloison "
     "de la salle de bain juste après l'angle arrondi, à la place du premier module à chaussures ; second module "
     "supprimé, patères gardées. Angle arrondi élargi à R 40 pour suivre la penderie ; miroir sur la porte sud de la "
     "penderie ; applique au-dessus des patères."),
]
