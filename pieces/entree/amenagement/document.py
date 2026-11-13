# Entrée, variante principale : l'aménagement (meubles, finitions, changements). La pièce est dans ../piece.py.
#
# Ce fichier ne contient que des données : il est lu par les générateurs de l'entrée. Toute modification se fait ici,
# jamais dans le HTML.
#
# Cotes en cm : x vers l'est depuis le mur ouest du couloir, y vers le sud depuis son mur nord, z depuis le sol fini.

from commun.modele import Changement, Document, Option, Valeur, Variante
from pieces.entree.piece import Bloc, EP, ENVELOPPE, H, H_PORTE, MURS, PORTES, SOL, SURFACE  # noqa: F401

VERSION = "V4.8"

# silhouette de chaque caméra
HUMAINS = {"iso_so": "couloir", "iso_no": "couloir", "iso_se": "entree"}

# meubles touchables du plan (cm) : principe = rang de l'explication, coupe = repère de la coupe, iso = coin
ZONES = (
    dict(x0=92, y0=0, x1=187, y1=38, principe=0, cotes="95 × 38, h 45", coupe="A", iso="so"),
    dict(x0=85, y0=208, x1=110, y1=374, principe=1, cotes="166 × 25, h 95", coupe="B", iso="so"),
    dict(x0=110, y0=170, x1=185, y1=208, principe=2, cotes="75 × 35, h 236", coupe="C", iso="no"),
    dict(x0=0, y0=170, x1=85, y1=208, principe=3, cotes="110 × 38, h 46, dessous à 204", coupe="B", iso="se"),
    dict(x0=-10, y0=83, x1=14, y1=160, principe=4, cotes="vantail de 77", coupe=None, iso="no"),
)

# versions figées : (version, chemin sous site/)
FIGEES_ANCIENNES = (("V3.3", "archive/entree-amenagement-v3.3.html"), ("V2", "archive/entree-amenagement-v2.html"),
                    ("V1", "archive/entree-amenagement-v1.html"))

# Tableau électrique encastré dans le trumeau nord, entre la cuisine et le WC : position et taille à relever
# (dessiné au milieu du banc, 60 × 80, bas à 95).
TABLEAU = dict(x0=110, x1=170, z0=95, z1=175)

# ------------------------------------------------------------------ ① banc sous le tableau électrique
# Posé, pas fixé dans la zone du tableau ; dessous ouvert ; on s'y assoit pour se chausser, face au meuble à chaussures.
BANC = dict(x0=92, x1=187, y0=0, y1=38, z1=45, ep=3)

# ------------------------------------------------------------------ ② meuble à chaussures, branche d'entrée
# Contre la cloison de la salle de bain (x 110), 25 de profondeur pour garder 85 de passage ; deux modules de 83,
# chacun à deux abattants superposés (≈ 6 paires par abattant, ≈ 24 en tout) ; plateau vide-poche à 98.
CHAUSSURES = dict(x0=85, x1=110, y0=208, y1=374, z1=95, facade=2, rangs=(0, 48, 95), plateau=3)
CHAUSSURES["modules"] = [(208, 291), (291, 374)]
PAIRES = 24

# Nu nord de la penderie PAX (V4.7) : caisson 35,5 + porte 1,6 + jeu ≈ 38 depuis la face nord de la salle de bain (y 208).
# L'angle arrondi et le meuble haut s'alignent dessus.
NU_PENDERIE = 170

# ------------------------------------------------------------------ angle arrondi
# Le meuble à chaussures se prolonge jusqu'au nu de la penderie (y 168) et s'y termine par un quart de cercle de
# rayon 25 : étagères ouvertes (clés, courrier) à 95 de haut, pas d'arête dans le passage.
ANGLE = dict(x0=85, x1=110, y0=NU_PENDERIE, y1=208, r=25, etageres=(31, 63))

# ------------------------------------------------------------------ ③ penderie IKEA PAX (V4.7)
# Contre la face nord de la salle de bain, à partir de la cloison (x 110) : caisson PAX 75 × 35 × 236 (cotes réelles
# 74,8 × 35,5 × 236,4, pieds réglables), le seul qui tienne dans les 84 (un 100 mangerait l'huisserie de la salle de
# bain à x 200) ; 9 libres à l'est. Portes FORSAND blanc 50 + 25 (règle IKEA pour un caisson de 75), charnières
# KOMPLEMENT à fermeture silencieuse fournies avec les portes. Intérieur KOMPLEMENT pour 35 de profondeur : tringle
# 75 × 35 (cadre à deux barres d'avant en arrière, cintres de face, ≈ 5 manteaux par barre, 12 kg), deux tablettes
# au-dessus, deux étagères à chaussures en bas, lampe LED à détecteur sur pile sous la tablette. Bandeau blanc de 14
# du caisson (236) au plafond. Montage debout possible dès 237 de hauteur sous plafond (fiche IKEA).
PENDERIE = dict(x0=110, x1=185, y0=NU_PENDERIE, y1=208, z1=236, facade=2, portes=(50, 25), porte_z=(4, 233.4),
                tringle=195, barres=(129, 166), etageres=(200, 218), chaussures=(10, 32), manteaux=10)
IKEA = [   # IKEA France, fiches produit relevées le 13/11/2026, blanc
    ("PAX caisson d'armoire 75 × 35 × 236", "604.582.27", 1, 80),
    ("FORSAND porte avec charnières 50 × 229", "692.443.12", 1, 55),
    ("FORSAND porte avec charnières 25 × 229", "292.794.74", 1, 50),
    ("KOMPLEMENT tringle à habits 75 × 35", "804.464.55", 1, 12),
    ("KOMPLEMENT tablette 75 × 35", "702.779.95", 2, 11),
    ("KOMPLEMENT étagère à chaussures 75 × 35", "802.572.61", 2, 15),
    ("KÖLVATTEN éclairage LED à détecteur, sur pile, 50 cm", "205.689.87", 1, 14.99),
]
# Portes possibles pour ce caisson (prix de la porte avec ses charnières) : FORSAND blanc 50 + 25 = 105 € ;
# ÅHEIM miroir 25 à la place de la FORSAND 25 (80 €) ; FARDAL brillant blanc 105 + 75 ; Plum Living : deux portes
# 37 × 236 en laque mate (232 € pièce, toutes teintes dont India) + 2 × 4 charnières KOMPLEMENT (16 € les 4).
PORTES_PAX = [
    ("FORSAND blanc 50 + 25 (retenu)", 105),
    ("FORSAND 50 + ÅHEIM miroir 25", 135),
    ("FARDAL brillant blanc 50 + 25", 180),
    ("Plum Living 2 × 37 laque mate (India possible)", 496),
]

# ------------------------------------------------------------------ mur de la salle de bain, au-dessus du meuble
# V4.1 : miroir ramené à 50 de large (raccourci au sud), quatre patères de plus à sa droite (vu du couloir)
# V4.2 : coins du miroir arrondis ; patères au nord du miroir retirées, les quatre du sud en bois, plus haut
MIROIR = dict(y0=251, y1=301, z0=110, z1=210, r=12)
PATERES = [316, 331, 346, 361]          # y
PATERE = dict(z=180, d=3.5, saillie=8)  # patères en bois (chevilles de chêne) : hauteur d'axe, diamètre, saillie
APPLIQUE = dict(y=276, z=220)

# ------------------------------------------------------------------ ④ meuble haut (V4.1)
# Suspendu au plafond en travers de la branche d'entrée, du mur ouest à la cloison de la salle de bain, au droit du
# coin de la salle de bain : il marque l'entrée. Dessous à 204 (hauteur des portes), dessus au plafond. Côté nord,
# étagères ouvertes (vers le couloir) ; côté sud, placard à deux portes (vers la porte d'entrée), séparés par un dos.
# V4.3 : aligné sur la penderie (mêmes nus nord et sud, y 168 → 208), donc 40 de profondeur
MEUBLE_HAUT = dict(x0=0, x1=110, y0=NU_PENDERIE, y1=208, z0=204, z1=250, ep=2, etagere=14, facade=2, tablette=226)

# ------------------------------------------------------------------ peinture de l'entrée (V4.1)
# Au sud du meuble haut : murs, plafond et porte d'entrée en India Yellow (Farrow & Ball n° 66, teinte supposée).
# V4.2 : India de Plum Living (« Beige 11 - India », jaune soleil lumineux), valeur écran relevée sur plum-living.com
INDIA = dict(nom="India de Plum Living (Beige 11)", couleur="#F5D58C", y0=MEUBLE_HAUT["y0"])

MEUBLES = [
    Bloc("tableau", "tableau", TABLEAU["x0"], TABLEAU["x1"], -1, 0.5, TABLEAU["z0"], TABLEAU["z1"], "tableau", mur="n"),
    Bloc("banc", "banc_plateau", BANC["x0"], BANC["x1"], BANC["y0"], BANC["y1"], BANC["z1"] - BANC["ep"], BANC["z1"], "① banc"),
    Bloc("banc", "banc_joue_o", BANC["x0"], BANC["x0"] + BANC["ep"], BANC["y0"], BANC["y1"], 0, BANC["z1"] - BANC["ep"]),
    Bloc("banc", "banc_joue_e", BANC["x1"] - BANC["ep"], BANC["x1"], BANC["y0"], BANC["y1"], 0, BANC["z1"] - BANC["ep"]),
    Bloc("banc", "banc_traverse", BANC["x0"] + BANC["ep"], BANC["x1"] - BANC["ep"], BANC["y0"], BANC["y0"] + 2, 30, BANC["z1"] - BANC["ep"]),
    Bloc("angle", "angle", ANGLE["x0"], ANGLE["x1"], ANGLE["y0"], ANGLE["y1"], 0, CHAUSSURES["z1"], "angle", arrondi=ANGLE["r"]),
    Bloc("caisson", "chaussures", CHAUSSURES["x0"] + CHAUSSURES["facade"], CHAUSSURES["x1"], CHAUSSURES["y0"],
         CHAUSSURES["y1"], 0, CHAUSSURES["z1"], "② chaussures"),
    Bloc("plateau", "vide_poche", ANGLE["x0"], CHAUSSURES["x1"], ANGLE["y0"], CHAUSSURES["y1"], CHAUSSURES["z1"],
         CHAUSSURES["z1"] + CHAUSSURES["plateau"], arrondi=ANGLE["r"]),
    Bloc("tall", "penderie", PENDERIE["x0"], PENDERIE["x1"], PENDERIE["y0"] + PENDERIE["facade"], PENDERIE["y1"],
         0, PENDERIE["z1"], "③ penderie PAX"),
    Bloc("tall", "bandeau", PENDERIE["x0"], PENDERIE["x1"], PENDERIE["y0"], PENDERIE["y1"], PENDERIE["z1"], H),
    Bloc("miroir", "miroir", 109.4, 110, MIROIR["y0"], MIROIR["y1"], MIROIR["z0"], MIROIR["z1"], mur="e"),
    Bloc("applique", "applique", 104, 110, APPLIQUE["y"] - 6, APPLIQUE["y"] + 6, APPLIQUE["z"] - 6, APPLIQUE["z"] + 6, mur="e"),
] + [Bloc("patere", f"patere_{k}", 110 - PATERE["saillie"], 110, y - PATERE["d"] / 2, y + PATERE["d"] / 2,
          PATERE["z"] - PATERE["d"] / 2, PATERE["z"] + PATERE["d"] / 2, mur="e") for k, y in enumerate(PATERES)]

# interphone (téléphone de la sonnette, blanc) au mur ouest, à droite de la porte d'entrée vue de l'intérieur ;
# position et taille à relever (dessiné 10 × 22, haut à 162)
INTERPHONE = dict(y0=335, y1=345, z0=140, z1=162)
MEUBLES.append(Bloc("interphone", "interphone", 0, 3, INTERPHONE["y0"], INTERPHONE["y1"], INTERPHONE["z0"], INTERPHONE["z1"], mur="o"))

# ------------------------------------------------------------------ cadres (V4.4)
# Mur ouest de l'entrée, entre le meuble haut et l'interphone (≈ 115 libres, y 210 → 325) : galerie de 6 cadres
# 30 × 40 en grille 3 × 2, 6 d'écart (règle de galerie : cadres identiques, écarts égaux et serrés, 5 à 8), centrée à
# 150 (hauteur d'œil) et sur le mur libre ; fins cadres noirs, passe-partout blanc.
CADRES = dict(l=30, h=40, ecart=6, colonnes=3, rangs=2, zc=150, ep=2.5)
_lg = CADRES["colonnes"] * CADRES["l"] + (CADRES["colonnes"] - 1) * CADRES["ecart"]
_hg = CADRES["rangs"] * CADRES["h"] + (CADRES["rangs"] - 1) * CADRES["ecart"]
CADRES["yc"] = (MEUBLE_HAUT["y1"] + INTERPHONE["y0"]) / 2
CADRES["y0"], CADRES["y1"] = CADRES["yc"] - _lg / 2, CADRES["yc"] + _lg / 2
CADRES["z0"], CADRES["z1"] = CADRES["zc"] - _hg / 2, CADRES["zc"] + _hg / 2
for i in range(CADRES["colonnes"]):
    for j in range(CADRES["rangs"]):
        _y = CADRES["y0"] + i * (CADRES["l"] + CADRES["ecart"])
        _z = CADRES["z0"] + j * (CADRES["h"] + CADRES["ecart"])
        MEUBLES.append(Bloc("cadre_mur", f"cadre_{i}{j}", 0, CADRES["ep"], _y, _y + CADRES["l"], _z, _z + CADRES["h"], mur="o"))

# meuble haut : étagères ouvertes au nord, dos, placard au sud
_mh = MEUBLE_HAUT
_yd = _mh["y0"] + _mh["etagere"]
MEUBLES += [
    Bloc("haut", "mh_dessous", _mh["x0"], _mh["x1"], _mh["y0"], _yd, _mh["z0"], _mh["z0"] + _mh["ep"], "④ meuble haut"),
    Bloc("haut", "mh_tablette", _mh["x0"] + _mh["ep"], _mh["x1"] - _mh["ep"], _mh["y0"], _yd, _mh["tablette"], _mh["tablette"] + _mh["ep"]),
    Bloc("haut", "mh_dessus", _mh["x0"], _mh["x1"], _mh["y0"], _yd, _mh["z1"] - _mh["ep"], _mh["z1"]),
    Bloc("haut", "mh_joue_o", _mh["x0"], _mh["x0"] + _mh["ep"], _mh["y0"], _yd, _mh["z0"], _mh["z1"]),
    Bloc("haut", "mh_joue_e", _mh["x1"] - _mh["ep"], _mh["x1"], _mh["y0"], _yd, _mh["z0"], _mh["z1"]),
    Bloc("haut", "mh_placard", _mh["x0"], _mh["x1"], _yd, _mh["y1"] - _mh["facade"], _mh["z0"], _mh["z1"]),
]
for k in range(2):
    _l = (_mh["x1"] - _mh["x0"]) / 2
    MEUBLES.append(Bloc("facade_h", f"mh_porte_{k}", _mh["x0"] + k * _l + 0.2, _mh["x0"] + (k + 1) * _l - 0.2,
                        _mh["y1"] - _mh["facade"], _mh["y1"], _mh["z0"] + 0.2, _mh["z1"] - 0.2))

# peinture India : fines couches sur les faces côté couloir, au sud du meuble haut ; le plafond aussi
_y = INDIA["y0"]
MEUBLES += [
    Bloc("india", "india_ouest", 0, 0.3, _y, 374, 0, H, mur="o"),
    Bloc("india", "india_sdb", 109.7, 110, max(_y, PENDERIE["y1"]), 374, 0, H, mur="e"),
    Bloc("india", "india_sud_o", 0, 2, 373.7, 374, 0, H, mur="s"),
    Bloc("india", "india_sud_e", 77, 110, 373.7, 374, 0, H, mur="s"),
    Bloc("india", "india_sud_linteau", 2, 77, 373.7, 374, H_PORTE, H, mur="s"),
    Bloc("india_plafond", "india_plafond", 0, 110, _y, 374, H - 0.3, H, mur="p"),
    # V4.2 : flanc ouest de la penderie, dans le prolongement de l'angle arrondi, en laque India
    Bloc("india_l", "india_penderie", PENDERIE["x0"] - 0.3, PENDERIE["x0"], PENDERIE["y0"], PENDERIE["y1"], 0, H),
]

# façades : abattants du meuble à chaussures, portes de la penderie
for k, (y0, y1) in enumerate(CHAUSSURES["modules"]):
    for r, (z0, z1) in enumerate(zip(CHAUSSURES["rangs"], CHAUSSURES["rangs"][1:])):
        MEUBLES.append(Bloc("facade", f"abattant_{k}{r}", CHAUSSURES["x0"], CHAUSSURES["x0"] + CHAUSSURES["facade"],
                            y0 + 0.2, y1 - 0.2, z0 + 0.2, z1 - 0.2))
_xm = PENDERIE["x0"] + PENDERIE["portes"][0]          # joint des portes de 50 (ouest) et 25 (est)
for k, (x0, x1) in enumerate(((PENDERIE["x0"], _xm), (_xm, PENDERIE["x1"]))):
    MEUBLES.append(Bloc("facade_p", f"porte_penderie_{k}", x0 + 0.2, x1 - 0.2, PENDERIE["y0"],
                        PENDERIE["y0"] + PENDERIE["facade"], *PENDERIE["porte_z"]))

# ------------------------------------------------------------------ déco (variante décorée de la vue du banc, V4.4)
# Emprises seulement ; rendu.py y place des modèles (plante, bol, vase, paniers, livres) ou des volumes simples.
# Tapis de couloir plat (la porte d'entrée passe dessus) de 60 × 140, à 10 du mur ouest et de l'angle.
DECO = [
    Bloc("tapis", "tapis", 10, 70, 222, 362, 0, 0.8),
    Bloc("plante", "plante_angle", 88, 108, 172, 194, 98, 150),                   # sur le plateau, au-dessus de l'angle
    Bloc("bol", "bol_cles", 89, 107, 226, 244, 98, 104),                         # vide-poche pour les clés
    Bloc("vase", "vase_plateau", 92, 106, 352, 366, 98, 128),
    Bloc("panier", "panier_angle", 90, 108, 180, 200, 3, 27),                    # bonnets, gants, sur l'étagère du bas
    Bloc("livres", "livres_mh", 8, 52, 169, 181, 206, 224),                      # meuble haut, étagère ouverte du bas
    Bloc("panier", "panier_mh", 62, 100, 169, 181, 228, 247),                    # meuble haut, étagère du haut
    Bloc("vase", "vase_mh", 12, 24, 170, 180, 228, 246),
    Bloc("sac", "sac_patere", 104.5, 108, 318, 346, 140, 180),                   # tote en toile à la première patère
]

# ------------------------------------------------------------------ dégagements (cm)
PASSAGES = [
    dict(a=(0, 270), b=(CHAUSSURES["x0"], 270), label=f"{CHAUSSURES['x0']}"),
    dict(a=(150, BANC["y1"]), b=(150, PENDERIE["y0"]), label=f"{PENDERIE['y0'] - BANC['y1']}"),
    dict(a=(230, 104), b=(230, 208), label="104"),
]

CARRELAGE = dict(taille=60, joint=0.3, couleur="#D9D2C6", nuance="#CFC7B9", couleur_joint="#BDB5A7",
                 nom="grès cérame 60 × 60 effet pierre claire, comme le salon")
MUR_COULEUR = "#EFE9DC"

RENDUS = [("iso_so", "Isométrique depuis le sud-ouest : banc sous le tableau, meuble à chaussures, miroir"),
          ("iso_no", "Isométrique depuis le nord-ouest : penderie, angle arrondi, meuble à chaussures, porte d'entrée"),
          ("iso_se", "Isométrique depuis le sud-est, sur l'entrée : mur ouest en India et interphone, meuble haut côté placard"),
          ("banc", "Assis sur le banc, vers la porte d'entrée : penderie, meuble haut, entrée en India")]

CHANGEMENTS = [
    ("V4.8", "13/11/2026", "Sélecteur « Teinte » dans la barre du haut : les 52 teintes Plum Living (40 laques de "
     "façade, 30 peintures murales, relevées sur plum-living.com), groupées selon la gamme. Il change ensemble toutes "
     "les surfaces India : plan, coupes et vues 3D, sans un rendu par couleur (rendu neutre + masque, recoloré par "
     "un filtre SVG : un mur bien éclairé prend la teinte affichée par Plum Living). Choix gardé d'une page de l'entrée à l'autre. Constat : India "
     "n'existe pas en peinture murale chez Plum Living."),
    ("V4.7", "13/11/2026", "Penderie remplacée par une IKEA PAX 75 × 35 × 236 (la seule largeur qui tienne dans les 84) : "
     "portes FORSAND blanc 50 + 25 avec charnières à fermeture silencieuse, tringle KOMPLEMENT 75 × 35 (cintres de "
     "face, ≈ 10 manteaux), deux tablettes, deux étagères à chaussures, lampe LED à détecteur ; bandeau de 14 "
     "jusqu'au plafond ; ≈ 264 €. Nu nord à y 170 (au lieu de 168) : l'angle arrondi, le meuble haut et la "
     "peinture India suivent. Section Achats IKEA et comparatif des portes."),
    ("V4.6", "13/11/2026", "Silhouette remplacée par un corps humain réaliste (Human Base Meshes de Blender Studio, CC0), mis à 1,75 m."),
    ("V4.5", "13/11/2026", "Silhouette de 1,75 m semi-transparente dans les trois vues isométriques, pour l'échelle."),
    ("V4.4", "13/11/2026", "Galerie de 6 cadres 30 × 40 (grille 3 × 2, centrée à 150) sur le mur ouest de l'entrée, "
     "entre le meuble haut et l'interphone. La vue décorée du banc, essayée, est retirée de la page."),
    ("V4.3", "13/11/2026", "Meuble haut aligné sur la penderie (y 168 → 208, 40 de profondeur) : la couleur India commence "
     "à son nu nord. Interphone blanc au mur ouest, à droite de la porte d'entrée. Deux vues de plus : isométrique "
     "depuis le sud-est sur l'entrée, et vue assis sur le banc."),
    ("V4.2", "13/11/2026", "Couleur India : celle de Plum Living (Beige 11 - India, jaune soleil, #F5D58C) au lieu de "
     "l'India Yellow de Farrow & Ball. Flanc ouest de la penderie, dans le prolongement de l'angle arrondi, en India. "
     "Miroir à coins arrondis (R 12). Les deux patères au nord du miroir sont retirées ; les quatre du sud sont des "
     "chevilles en chêne, montées à 180. Vues isométriques refaites."),
    ("V4.1", "13/11/2026", "Miroir réduit à 50 de large (raccourci au sud, applique recentrée) et quatre patères de "
     "plus à sa droite (six en tout). Nouveau meuble haut ④ suspendu au plafond en travers de la branche d'entrée "
     "(110 × 34, de 204 au plafond) : étagères ouvertes côté couloir, placard à deux portes côté porte d'entrée ; il "
     "délimite l'entrée. Au sud de ce meuble, murs, plafond et porte d'entrée peints en India Yellow (Farrow & Ball "
     "n° 66). Vues isométriques refaites."),
    ("V4.0", "13/11/2026", "Page refaite sur le modèle du salon et de la cuisine : une source de données "
     "(3d/entree/modele.py) dont sont tirés le plan, trois coupes et le rendu 3D ; deux vues isométriques "
     "(sud-ouest et nord-ouest) ; boutons Explications et Changements, sommaire. Aménagement inchangé (V3.3). "
     "La V3.3 est archivée (archive/entree-amenagement-v3.3.html)."),
    ("V3.3", "01/10/2026", "Penderie moins profonde : 84 × 40 au lieu de 84 × 60, deux tringles extractibles (cintres "
     "de face) au lieu d'une tringle en travers. Angle arrondi raccourci en conséquence (meuble à chaussures jusqu'à "
     "y 193, quart de cercle R 25 jusqu'au nu de la penderie, y 168). 130 cm entre le banc et la penderie ; la porte de "
     "la pièce ouest n'a plus besoin de s'ouvrir à 180°."),
    ("V3.2", "01/10/2026", "Angle arrondi aligné sur la façade de la penderie : le meuble à chaussures se prolonge "
     "jusqu'à y 173, puis un quart de cercle de rayon 25 arrive au nu de la penderie (y 148)."),
    ("V3.1", "01/10/2026", "Angle arrondi redessiné : quart de cercle de rayon 25 au bout du meuble à chaussures, contre "
     "le flanc de la penderie (au lieu d'un quart d'ellipse 25 × 60)."),
    ("V3", "01/10/2026", "Banc et penderie échangés (demande du client) : banc 95 × 38 posé sous le tableau électrique, "
     "entre la cuisine et le WC ; penderie 84 × 60 toute hauteur contre la face nord de la salle de bain ; angle arrondi "
     "agrandi à 25 × 60, ouvert, à 95 de haut ; patères du mur nord de la SDB supprimées (2 restent au-dessus du meuble "
     "à chaussures). Porte de la pièce ouest à ouvrir à 180°. La V2.1 est archivée (archive/entree-amenagement-v2.html)."),
    ("V2.1", "01/10/2026", "Porte du salon supprimée : l'ouverture du couloir vers le salon est un passage libre."),
    ("V2", "01/10/2026", "Penderie supprimée : le tableau électrique est encastré dans le trumeau entre la cuisine et le "
     "WC, et la NF C 15-100 interdit d'y ranger quoi que ce soit devant. Les manteaux passent sur 8 patères (6 au-dessus "
     "du banc, 2 au-dessus du meuble à chaussures). Angle arrondi en quart de rond 25 × 38 entre le meuble à chaussures "
     "(166 × 25) et le banc (84 × 38). La V1 est archivée (archive/entree-amenagement-v1.html)."),
    ("V1", "01/10/2026", "Première proposition à partir du relevé : penderie 95 × 60 entre la cuisine et le WC, meuble "
     "à chaussures 160 × 25 avec miroir le long de la salle de bain, banc 82 × 38 avec patères face au nord. Plan et "
     "trois élévations."),
]


# ------------------------------------------------------------------ le document déclaré (tâche 13)
# DOCUMENT dépend de victor.py, qui lit ce fichier : on le construit à la première lecture (`document.DOCUMENT`),
# pas à l'import, pour éviter l'import circulaire.


def _gamme(c):
    if c[3] and c[4]:
        return "laque de façade et peinture murale"
    if c[3]:
        return "laque de façade seulement, peinture à faire teinter"
    return "peinture murale seulement, pas de laque de façade"


def _teinte():
    from pieces.entree.amenagement import plum
    # groupes du nuancier, selon la gamme ; ici et non en constante du module, que l'empreinte des rendus lit
    groupes = (("Laque et peinture murale", lambda c: c[3] and c[4]),
               ("Laque de façade seulement", lambda c: c[3] and not c[4]),
               ("Peinture murale seulement", lambda c: c[4] and not c[3]))
    valeurs = tuple(Valeur(code=c[0], nom=c[1], couleur=c[2], groupe=titre, note=_gamme(c),
                           lien=plum.URL_PEINTURE + c[4] if c[4] else "")
                    for titre, garde in groupes for c in plum.PALETTE if garde(c))
    return Option(id="teinte", nom="Teinte de l'entrée", surfaces=("murs", "plafond", "porte"), type="nuancier",
                  defaut=plum.DEFAUT, valeurs=valeurs, css="--india", filtre=True,
                  portee="Visible sur le plan, les coupes et les rendus.")


def _changements(liste):
    return tuple(Changement(*c) for c in liste)


def _document():
    from pieces.entree.amenagement import victor, vues
    principale = Variante("principale", "Principale", VERSION, _changements(CHANGEMENTS), FIGEES_ANCIENNES)
    var_victor = Variante("victor", "Victor", victor.VERSION, _changements(victor.CHANGEMENTS))
    # dessins.css sert toutes les variantes : il réunit le CSS du module de dessin de chacune (celui de Victor ajoute
    # .talli et .tallic) ; css_dessins n'en garde qu'une fois les règles communes
    css = "\n".join(dessin.CSS for _, dessin in vues.VARIANTES.values())
    return Document(piece="entree", id="amenagement", nom="Aménagement", type="amenagement",
                    variantes=(principale, var_victor), generer=vues.vues, options=(_teinte(),), css=css)


def __getattr__(nom):
    if nom == "DOCUMENT":
        globals()["DOCUMENT"] = _document()
        return globals()["DOCUMENT"]
    raise AttributeError(f"module {__name__!r} has no attribute {nom!r}")
