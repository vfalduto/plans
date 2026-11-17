# Entrée, version Victor : variante de la V4.3 (document.py), même relevé, même entrée en India.
#
# Lu par les vues de l'entrée (vues.py, dessin_victor.py ; just site entree/amenagement) et par rendu.py (ENTREE_VARIANTE=victor,
# just rendu entree/amenagement). Toute modification se fait ici.
#
# Différences avec la V4.3 :
#   - rien sous le tableau électrique (mur nord libre) ;
#   - meuble à chaussures bas à abattants à la place de la penderie, contre la face nord de la salle de bain, terminé
#     par un arrondi qui rejoint la façade du PAX ; deux étagères flottantes au-dessus ;
#   - penderie IKEA PAX contre la cloison de la salle de bain, à la place du premier module du meuble à chaussures et
#     du meuble haut ; angle arrondi retiré ;
#   - second module du meuble à chaussures retiré, sol libre sous les patères (planche retirée à la V1.6) ;
#   - miroir et cadres sur le mur ouest de l'entrée ;
#   - V1.6 : console sous le tableau électrique, coussin sur le banc, meuble haut au-dessus du banc.

import math

from pieces.entree import piece
from pieces.entree.amenagement import document
# noms de la pièce et de la principale que les dessins, les vues et rendu.py lisent à travers ce module (M.SOL,
# M.CARRELAGE…), comme dans document.py
from pieces.entree.piece import Bloc, EP, ENVELOPPE, H, H_PORTE, MURS, PORTES, SOL, SURFACE  # noqa: F401
from pieces.entree.amenagement.document import (CARRELAGE, INDIA, INTERPHONE, MUR_COULEUR, MUR_TEINTE,  # noqa: F401
                                                PATERE, PATERES, TABLEAU)

VERSION = "V1.7"
BASE = "V4.3"           # version de la page principale dont cette variante est tirée

# ------------------------------------------------------------------ ③ penderie IKEA PAX (V1.2)
# Contre la cloison de la salle de bain (x 110), à partir de son coin (y 208) : caisson PAX 75 × 35 × 236, une porte
# FORSAND 50 × 229 et une 25 × 229 (règle IKEA pour un caisson de 75), vers l'ouest. Profondeur 35 + porte 2 : 73 de
# passage devant. À 35, les cintres se suspendent de face (tringle KOMPLEMENT 75 × 35, 12 kg), pas d'extractible dans
# cette profondeur. Le haut de la penderie, derrière les mêmes portes : deux tablettes. V1.4 : caisson, portes et
# bandeau peints en India, comme les murs de l'entrée (FORSAND blanc repeint).
# V1.6 : posée sur une plinthe de 8, comme la principale, dans le prolongement de celle du banc (même nu, 4 en retrait
# des portes, x 77) : caisson de 8 à 244, bandeau de 6 au-dessus ; hauteurs intérieures depuis le sol fini.
PENDERIE = dict(x0=73, x1=110, y0=208, y1=283, h=236, socle=8, retrait=4, facade=2, portes=(50, 25), manteaux=10)
PENDERIE.update(z1=PENDERIE["socle"] + PENDERIE["h"], tringle=PENDERIE["socle"] + 180,
                etageres=(PENDERIE["socle"] + 196, PENDERIE["socle"] + 216),
                porte_z=(PENDERIE["socle"] + 3.5, PENDERIE["socle"] + 3.5 + 229.4))
PENDERIE["caisson"] = PENDERIE["x1"] - PENDERIE["x0"] - PENDERIE["facade"]    # 35 : profondeur sans les portes
BANDEAU = dict(z0=PENDERIE["z1"], z1=H)
IKEA = [   # prix IKEA France relevés le 13/11/2026 (fiches produit, blanc)
    ("PAX caisson d'armoire 75 × 35 × 236", "604.582.27", 1, 80),
    ("FORSAND porte 50 × 229", "603.910.91", 1, 39),
    ("FORSAND porte 25 × 229", "804.236.04", 1, 34),
    ("KOMPLEMENT tringle à habits 75 × 35", "804.464.55", 1, 12),
]

# ------------------------------------------------------------------ ① meuble à chaussures, le « banc » (V1.3)
# Contre la face nord de la salle de bain, comme celui de la V4.3 mais d'un seul niveau d'abattants et plus profond :
# la profondeur du PAX porte comprise (37). Socle de 8 en retrait de 4 : le meuble flotte. Deux abattants de 42
# (≈ 4 paires chacun), plateau vide-poche en chêne à 53, assez bas pour s'y asseoir.
# V1.6 : même arrondi que le meuble à chaussures de la principale : le bout ouest (x 73 → 110, jusqu'au nu du PAX) est
# un volume plein en chêne, de la plinthe au plateau, coin nord-ouest en quart de cercle R 12 (au lieu du quart de
# cercle R 37 centré sur le coin de la salle de bain) ; la plinthe suit (R 8).
CHAUSSURES = dict(x0=73, xa=110, x1=194, y0=171, y1=208, z1=50, plateau=3, facade=2, socle=8, retrait=4, r=12)
CHAUSSURES["modules"] = [(110, 152), (152, 194)]

# ------------------------------------------------------------------ coussin sur le banc (V1.6)
# Galette de 6 sur la partie à abattants, 2 en retrait de chaque bord ; teinte au choix (option « coussin »).
COUSSIN = dict(x0=CHAUSSURES["xa"] + 2, x1=CHAUSSURES["x1"] - 2, y0=CHAUSSURES["y0"] + 2, y1=CHAUSSURES["y1"] - 2,
               z0=CHAUSSURES["z1"] + CHAUSSURES["plateau"], ep=6)
COUSSIN["z1"] = COUSSIN["z0"] + COUSSIN["ep"]

# Teintes de tissu proposées pour le coussin (valeurs d'écran indicatives, à choisir sur échantillon) : (code, nom, hex)
COUSSIN_TEINTES = [
    ("terracotta", "Terracotta", "#B4623F"), ("rouille", "Rouille", "#9A4A2A"), ("moutarde", "Moutarde", "#C8962E"),
    ("lin", "Lin naturel", "#C9B9A0"), ("ecru", "Écru", "#E9E2D2"), ("rose-poudre", "Rose poudré", "#D8B2A6"),
    ("sauge", "Vert sauge", "#9AA58C"), ("olive", "Vert olive", "#6B6A3E"), ("canard", "Bleu canard", "#2E5E66"),
    ("jean", "Bleu jean", "#4A6380"), ("perle", "Gris perle", "#B9B7B2"), ("anthracite", "Anthracite", "#3D3E42"),
]
COUSSIN_DEFAUT = "terracotta"

# ------------------------------------------------------------------ étagère flottante au-dessus du meuble à chaussures
# Fixations invisibles dans la cloison ; 25 de profondeur, à 160 pour garder la tête libre assis.
# V1.6 : l'étagère du haut (195) est retirée, le meuble haut prend sa place ; celle qui reste suit la forme du meuble
# (bout ouest au nu du PAX, coin nord-ouest R 12).
ETAGERES = dict(x0=CHAUSSURES["x0"], x1=192, y0=CHAUSSURES["y1"] - 25, y1=CHAUSSURES["y1"], z=(160,), ep=3, r=12)

# ------------------------------------------------------------------ ④ meuble haut au-dessus de l'étagère (V1.6)
# Même forme que le meuble à chaussures, vu de dessus (x 73 → 194, 37 de profondeur, coin R 12) : bout ouest plein en
# chêne, caisson de 84 fermé par deux portes de placard battantes de 42 (au lieu d'abattants), de 195 au plafond.
MEUBLE_HAUT = dict(x0=CHAUSSURES["x0"], xa=CHAUSSURES["xa"], x1=CHAUSSURES["x1"], y0=CHAUSSURES["y0"],
                   y1=CHAUSSURES["y1"], z0=195, z1=H, facade=2, r=CHAUSSURES["r"], portes=CHAUSSURES["modules"])

# ------------------------------------------------------------------ ② console en face du banc (V1.6)
# Sur le mur nord, sous le tableau électrique (centrée sur lui), en face du meuble à chaussures : plateau de chêne
# 90 × 30 à 80, sous le bas du tableau (95), sur quatre pieds fins ; posée, pas fixée dans la zone du tableau.
# V1.7 : un tiroir sous le plateau, sur toute la largeur entre les pieds (façade de 12 au nu des pieds, 24 de
# profondeur), poignée au milieu.
CONSOLE = dict(x0=95, x1=185, y0=0, y1=30, z1=80, ep=3, pied=3, tiroir=12, prof_tiroir=24)

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
PAIRES = 8                               # V1.6 : planche à chaussures retirée, il reste le meuble

_c, _mh, _co = CHAUSSURES, MEUBLE_HAUT, CONSOLE
MEUBLES = [
    Bloc("tableau", "tableau", TABLEAU["x0"], TABLEAU["x1"], -1, 0.5, TABLEAU["z0"], TABLEAU["z1"], "tableau", mur="n"),
    # meuble à chaussures : plinthe en retrait (avec celle du PAX, d'un seul tenant), bout ouest plein, caisson, plateau
    Bloc("socle", "chaussures_socle", _c["xa"], _c["x1"] - _c["retrait"], _c["y0"] + _c["retrait"], _c["y1"], 0, _c["socle"]),
    Bloc("socle", "chaussures_socle_angle", _c["x0"] + _c["retrait"], _c["xa"], _c["y0"] + _c["retrait"], _c["y1"], 0,
         _c["socle"], arrondi=_c["r"] - _c["retrait"]),
    Bloc("socle", "penderie_socle", PENDERIE["x0"] + PENDERIE["retrait"], PENDERIE["x1"], PENDERIE["y0"],
         PENDERIE["y1"] - PENDERIE["retrait"], 0, PENDERIE["socle"]),
    Bloc("angle", "angle", _c["x0"], _c["xa"], _c["y0"], _c["y1"], _c["socle"], _c["z1"], arrondi=_c["r"]),
    Bloc("caisson", "chaussures", _c["xa"], _c["x1"], _c["y0"] + _c["facade"], _c["y1"], _c["socle"], _c["z1"]),
    Bloc("plateau", "vide_poche", _c["x0"], _c["x1"], _c["y0"], _c["y1"], _c["z1"], _c["z1"] + _c["plateau"], arrondi=_c["r"]),
    Bloc("coussin", "coussin", COUSSIN["x0"], COUSSIN["x1"], COUSSIN["y0"], COUSSIN["y1"], COUSSIN["z0"], COUSSIN["z1"]),
    # meuble haut : bout ouest plein, caisson, portes de placard (plus bas)
    Bloc("angle", "mh_angle", _mh["x0"], _mh["xa"], _mh["y0"], _mh["y1"], _mh["z0"], _mh["z1"], arrondi=_mh["r"]),
    Bloc("caisson", "mh_caisson", _mh["xa"], _mh["x1"], _mh["y0"] + _mh["facade"], _mh["y1"], _mh["z0"], _mh["z1"],
         "④ meuble haut"),
    # console du mur nord : plateau, quatre pieds, traverse arrière
    Bloc("banc", "console", _co["x0"], _co["x1"], _co["y0"], _co["y1"], _co["z1"] - _co["ep"], _co["z1"], "② console", mur="n"),
] + [Bloc("banc", f"console_pied_{k}", x, x + _co["pied"], y, y + _co["pied"], 0, _co["z1"] - _co["ep"], mur="n")
     for k, (x, y) in enumerate((x, y) for x in (_co["x0"] + 1, _co["x1"] - 1 - _co["pied"])
                                for y in (_co["y0"] + 1, _co["y1"] - 1 - _co["pied"]))] + [
    # tiroir : caisson entre les pieds, façade au nu avant des pieds
    Bloc("caisson", "console_tiroir", _co["x0"] + 1 + _co["pied"], _co["x1"] - 1 - _co["pied"],
         _co["y1"] - 1 - 2 - _co["prof_tiroir"], _co["y1"] - 1 - 2, _co["z1"] - _co["ep"] - _co["tiroir"],
         _co["z1"] - _co["ep"], mur="n"),
    Bloc("facade", "console_tiroir_facade", _co["x0"] + 1 + _co["pied"] + 0.2, _co["x1"] - 1 - _co["pied"] - 0.2,
         _co["y1"] - 1 - 2, _co["y1"] - 1, _co["z1"] - _co["ep"] - _co["tiroir"] + 0.2, _co["z1"] - _co["ep"] - 0.2,
         mur="n"),
    # penderie (corps, bandeau ; portes plus bas)
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

# abattants du meuble à chaussures, face au nord ; portes de placard du meuble haut au-dessus
for k, (x0, x1) in enumerate(CHAUSSURES["modules"]):
    MEUBLES.append(Bloc("facade", f"abattant_{k}", x0 + 0.2, x1 - 0.2, CHAUSSURES["y0"], CHAUSSURES["y0"] + CHAUSSURES["facade"],
                        CHAUSSURES["socle"] + 0.2, CHAUSSURES["z1"] - 0.2))
for k, (x0, x1) in enumerate(MEUBLE_HAUT["portes"]):
    MEUBLES.append(Bloc("facade", f"mh_porte_{k}", x0 + 0.2, x1 - 0.2, MEUBLE_HAUT["y0"],
                        MEUBLE_HAUT["y0"] + MEUBLE_HAUT["facade"], MEUBLE_HAUT["z0"] + 0.2, MEUBLE_HAUT["z1"] - 0.2))

# portes FORSAND de la penderie, face à l'ouest : 50 au nord, 25 au sud
_yj = PENDERIE["y0"] + PENDERIE["portes"][0]          # joint des deux portes
for k, (y0, y1) in enumerate(((PENDERIE["y0"], _yj), (_yj, PENDERIE["y1"]))):
    MEUBLES.append(Bloc("facade_pi", f"porte_penderie_{k}", PENDERIE["x0"], PENDERIE["x0"] + PENDERIE["facade"],
                        y0 + 0.2, y1 - 0.2, *PENDERIE["porte_z"]))

# peinture India : comme la V4.3, à partir du nu nord de la penderie de la principale ; la penderie PAX aussi (V1.4)
_y = INDIA["y0"]
MEUBLES += [
    Bloc("india", "india_ouest", 0, 0.3, _y, 374, 0, H, mur="o"),
    Bloc("india", "india_sdb", 109.7, 110, 208, 374, 0, H, mur="e"),
    Bloc("india", "india_sud_o", 0, 2, 373.7, 374, 0, H, mur="s"),
    Bloc("india", "india_sud_e", 77, 110, 373.7, 374, 0, H, mur="s"),
    Bloc("india", "india_sud_linteau", 2, 77, 373.7, 374, H_PORTE, H, mur="s"),
    Bloc("india_plafond", "india_plafond", 0, 110, _y, 374, H - 0.3, H, mur="p"),
]

# poignées (rendu) : barres verticales de part et d'autre du joint des portes de la penderie et du meuble haut (en bas
# des portes, à portée de main), barre sous le chant haut des abattants
POIGNEES = [(f"penderie_{dy}", PENDERIE["x0"] - 1.5, PENDERIE["x0"], _yj + dy, _yj + dy + 1, PENDERIE["socle"] + 104,
             PENDERIE["socle"] + 128) for dy in (-6, 5)]
POIGNEES += [(f"abattant_{k}", (x0 + x1) / 2 - 6, (x0 + x1) / 2 + 6, CHAUSSURES["y0"] - 1.2, CHAUSSURES["y0"],
              CHAUSSURES["z1"] - 8, CHAUSSURES["z1"] - 7) for k, (x0, x1) in enumerate(CHAUSSURES["modules"])]
_xt = (CONSOLE["x0"] + CONSOLE["x1"]) / 2              # poignée du tiroir de la console, au milieu de la façade
_zt = CONSOLE["z1"] - CONSOLE["ep"] - CONSOLE["tiroir"] / 2
POIGNEES += [("console_tiroir", _xt - 6, _xt + 6, CONSOLE["y1"] - 1, CONSOLE["y1"] + 0.2, _zt - 0.5, _zt + 0.5)]
_xj = MEUBLE_HAUT["portes"][0][1]                     # joint des deux portes du meuble haut
POIGNEES += [(f"mh_{dx}", _xj + dx, _xj + dx + 1, MEUBLE_HAUT["y0"] - 1.5, MEUBLE_HAUT["y0"], MEUBLE_HAUT["z0"] + 3,
              MEUBLE_HAUT["z0"] + 15) for dx in (-5, 4)]

# ------------------------------------------------------------------ silhouettes de 1,75 m (rendus, homme semi-transparent
# de rendu.py) : au milieu du couloir devant le meuble à chaussures, et dans la branche d'entrée devant le miroir
POSITIONS_HUMAINS = {"couloir": (150, 95), "entree": (36, 300)}

# ------------------------------------------------------------------ dégagements (cm)
# V1.7 : coin nord-est du banc à chaussures (façade des abattants) → coin du mur qui sépare le salon du couloir et de
# la chambre (x 264, y 104), comme PAX_MUR dans la principale ; la cote 104 passe de x 230 à 310, hors de la diagonale.
BANC_MUR = dict(a=(CHAUSSURES["x1"], CHAUSSURES["y0"]), b=document.PAX_MUR["b"])
BANC_MUR["d"] = math.dist(BANC_MUR["a"], BANC_MUR["b"])
PASSAGES = [
    dict(a=(0, 245), b=(PENDERIE["x0"], 245), label=f"{PENDERIE['x0']}"),
    dict(a=BANC_MUR["a"], b=BANC_MUR["b"], label=f"{BANC_MUR['d']:.0f}"),
    dict(a=(0, 312), b=(110, 312), label="110"),
    dict(a=(150, CONSOLE["y1"]), b=(150, CHAUSSURES["y0"]), label=f"{CHAUSSURES['y0'] - CONSOLE['y1']}"),
    dict(a=(310, 104), b=(310, 208), label="104"),
]

# ------------------------------------------------------------------ vues 3D (rendu.py)
# silhouette de chaque caméra (les caméras elles-mêmes sont celles de la pièce)
HUMAINS = {"iso_no": "entree", "iso_so": "couloir", "iso_se": "entree"}

# meubles touchables du plan, comme dans document.py ; plateau : hauteur plateau compris. Le mur ouest n'est pas un
# meuble et aucune constante ne décrit son décor d'un seul tenant : sa zone (cm) et son texte sont donnés tels quels.
ZONES = (
    dict(meuble="CHAUSSURES", plateau=True, principe=0, coupe="C", iso="no"),
    dict(meuble="PENDERIE", principe=1, coupe="B", iso="no"),
    dict(meuble="CONSOLE", principe=2, coupe="A", iso="so"),
    dict(x0=0, y0=215, x1=9, y1=350, principe=3, cotes="mur ouest de l'entrée", coupe="D", iso="se"),
)
RENDUS = [("iso_no", "Isométrique depuis le nord-ouest : banc à chaussures avec son coussin, étagère et meuble haut, "
                     "penderie PAX sur plinthe, patères au-dessus du sol libre"),
          ("iso_so", "Isométrique depuis le sud-ouest : console sous le tableau, penderie PAX, patères"),
          ("iso_se", "Isométrique depuis le sud-est, cloison de la salle de bain retirée : mur ouest en India avec cadres, "
                     "miroir et interphone ; dos de la penderie, banc, étagère et meuble haut"),
          ("couloir", "Debout devant la porte de la pièce ouest : banc à chaussures et son coussin, étagère, meuble haut, "
                      "penderie PAX sur plinthe")]

CHANGEMENTS = [
    ("V1.7", "17/11/2026", "Plan : cote en diagonale du coin nord-est du banc à chaussures au coin du mur qui sépare le "
     f"salon de la chambre ({BANC_MUR['d']:.0f} cm). Console : un tiroir sous le plateau, entre les pieds (façade de "
     f"{CONSOLE['tiroir']}, {CONSOLE['prof_tiroir']} de profondeur). Plinthes murales le long des murs du couloir "
     "dans les rendus."),
    ("V1.6", "17/11/2026", "Penderie PAX posée sur une plinthe de 8, comme dans la principale, dans le prolongement de "
     "celle du banc (même nu, 4 en retrait des portes) ; caisson de 8 à 244, bandeau de 6. Planche à chaussures sous les "
     "patères retirée : sol libre, 110 de passage. Console de chêne 90 × 30 à 80 sous le tableau électrique, en face du "
     "banc. Coussin de 6 sur le banc, teinte au choix dans « Personnaliser ». Étagère du haut retirée. Bout du banc "
     "repris de la principale : volume plein en chêne au coin arrondi R 12 (au lieu du quart de cercle R 37). Meuble "
     "haut de la même forme que le banc au-dessus de l'étagère, de 195 au plafond, fermé par deux portes de placard "
     "de 42."),
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
