# Salon V4 : source unique (repart du relevé du salon V3.1 et de la bibliothèque du mur ouest).
#
# Ce fichier ne contient que des données : il est lu par plan.py (HTML : plan et coupes, projetés
# depuis ces volumes). Toute modification se fait ici, jamais dans le HTML.
#
# Cotes en cm : x vers l'est depuis le mur ouest, y vers le sud depuis le mur nord, z depuis le sol fini.
# Chaque volume : Bloc(role, nom, x0, x1, y0, y1, z0, z1). Le rôle fixe le style du plan et des coupes.

import math
from dataclasses import dataclass

VERSION = "V4.10"
H = 250                 # hauteur sous plafond
L, P = 544, 358         # salon : 544 (ouest → est) × 358 (nord → sud)


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
# Mur ouest : cloison du cellier et du WC, puis le passage sans porte vers le couloir (cadre de 10 de chaque côté).
# Mur est : baie coulissante 2 vantaux de 202, sans allège (y 72 → 274, h 215). Décroché nord-est : à partir de
# x 414, le mur nord est 3 cm plus au sud.
PASSAGE = dict(y0=268, y1=343, h=204, cadre=10)
# sol : carrelage grès cérame grand format, pose droite parallèle aux murs, joints fins (teinte à choisir) ;
# murs : même blanc chaud que la cuisine (piste Farrow & Ball Wimborne White), plinthes de la couleur des murs
CARRELAGE = dict(taille=60, joint=0.3, couleur="#D9D2C6", nuance="#CFC7B9", couleur_joint="#BDB5A7",
                 nom="grès cérame 60 × 60 effet pierre claire")
MURS = dict(couleur="#EFE9DC", nom="Blanc chaud, comme la cuisine (piste Farrow & Ball Wimborne White)")
# mur derrière la desserte (mur nord du décroché, x 414 → 544) : papier peint de la cuisine, Hermione (4murs,
# intissé, cerise noire et vert-de-gris), motif ≈ 64 cm répété en miroir dans la hauteur
PAPIER_PEINT = dict(nom="Hermione (4murs), intissé cerise noire et vert-de-gris, comme l'essai de la cuisine",
                    image="3d/textures/papier-hermione.png", motif=64, couleur="#4B2E3B")
BAIE = dict(y0=72, y1=274, h=215, milieu=171)
DECROCHE = dict(x0=414, y=3)

ENVELOPPE = [
    Bloc("mur", "mur_nord", -10, 556, -12, 0, 0, H),
    Bloc("mur", "mur_nord_decroche", DECROCHE["x0"], 556, 0, DECROCHE["y"], 0, H),
    Bloc("mur", "mur_sud", -10, 556, P, P + 12, 0, H),
    Bloc("mur", "mur_ouest_n", -10, 0, 0, PASSAGE["y0"], 0, H),
    Bloc("mur", "mur_ouest_s", -10, 0, PASSAGE["y1"], P, 0, H),
    Bloc("linteau", "linteau_passage", -10, 0, PASSAGE["y0"], PASSAGE["y1"], PASSAGE["h"], H),
    Bloc("cadre", "cadre_passage_n", -11, 1.5, PASSAGE["y0"] - PASSAGE["cadre"], PASSAGE["y0"], 0, PASSAGE["h"] + 10),
    Bloc("cadre", "cadre_passage_s", -11, 1.5, PASSAGE["y1"], PASSAGE["y1"] + PASSAGE["cadre"], 0, PASSAGE["h"] + 10),
    Bloc("mur", "mur_est_n", L, 556, DECROCHE["y"], BAIE["y0"], 0, H),
    Bloc("mur", "mur_est_s", L, 556, BAIE["y1"], P, 0, H),
    Bloc("linteau", "linteau_baie", L, 556, BAIE["y0"], BAIE["y1"], BAIE["h"], H),
    Bloc("baie", "baie_est", L, 556, BAIE["y0"], BAIE["y1"], 0, BAIE["h"]),
    Bloc("papier_peint", "papier_desserte", DECROCHE["x0"], L, DECROCHE["y"], DECROCHE["y"] + 0.3, 0, H),
]

MEUBLES = []

# ------------------------------------------------------------------ ① enfilade, mur ouest
# Position validée par le client : mur ouest, du coin nord au cadre du passage (258 utiles).
# Meuble bas style enfilade, sur pieds, profond pour avoir du volume ; trois modules de 86.
ENFILADE = dict(y0=0, y1=PASSAGE["y0"] - PASSAGE["cadre"], p=45, pieds=15, z1=80, facade=2, ep=1.8)
_MODULES = [  # (façades, contenu)
    (["porte", "porte"], "jeux, albums, vinyles"),
    (["tiroir", "tiroir", "tiroir"], "linge de table, couverts"),
    (["porte", "porte"], "vaisselle, verres (×12)"),
]
_e = ENFILADE
_lm = (_e["y1"] - _e["y0"]) / len(_MODULES)
ENFILADE["modules"] = [(_e["y0"] + i * _lm, _e["y0"] + (i + 1) * _lm) for i in range(len(_MODULES))]
_xf = _e["p"] - _e["facade"]                       # nu du caisson, côté pièce
MEUBLES.append(Bloc("caisson", "enfilade_caisson", 0, _xf, _e["y0"], _e["y1"], _e["pieds"], _e["z1"], etiq="①"))
for i, ((y0, y1), (facades, contenu)) in enumerate(zip(ENFILADE["modules"], _MODULES)):
    n = len(facades)
    if facades[0] == "porte":   # portes côte à côte
        for k in range(n):
            a, b = y0 + (y1 - y0) * k / n, y0 + (y1 - y0) * (k + 1) / n
            MEUBLES.append(Bloc("facade", f"enfilade_m{i + 1}_porte{k + 1}", _xf, _e["p"], a + 0.2, b - 0.2,
                                _e["pieds"] + 0.2, _e["z1"] - 0.2, contenu=contenu if k == 0 else ""))
    else:                       # tiroirs superposés
        h = (_e["z1"] - _e["pieds"]) / n
        for k in range(n):
            a, b = _e["z1"] - (k + 1) * h, _e["z1"] - k * h
            MEUBLES.append(Bloc("facade", f"enfilade_m{i + 1}_tiroir{k + 1}", _xf, _e["p"], y0 + 0.2, y1 - 0.2,
                                a + 0.2, b - 0.2, contenu=contenu if k == 0 else ""))
for y in (_e["y0"] + 6, _e["y1"] - 6):
    for x in (6, _e["p"] - 8):
        MEUBLES.append(Cyl("pied", f"enfilade_pied_{x}_{y}", x, y, 1.6, 0, _e["pieds"]))
VOLUME_ENFILADE = (_xf - 2 * _e["ep"]) * (_e["y1"] - _e["y0"] - (len(_MODULES) + 1) * _e["ep"]) \
    * (_e["z1"] - _e["pieds"] - 2 * _e["ep"]) / 1000   # litres utiles

# ------------------------------------------------------------------ ② étagères suspendues au-dessus
# Fixation à étudier (R&D) : rien n'est encore choisi, les tablettes sont dessinées « flottantes ».
ETAGERES = dict(p=28, ep=3, zs=[125, 160, 195, 230], y0=ENFILADE["y0"], y1=ENFILADE["y1"])
for i, z in enumerate(ETAGERES["zs"]):
    MEUBLES.append(Bloc("etagere", f"etagere_{i + 1}", 0, ETAGERES["p"], ETAGERES["y0"], ETAGERES["y1"],
                        z - ETAGERES["ep"], z, etiq="②" if i == len(ETAGERES["zs"]) - 1 else ""))
METRES_ETAGERES = len(ETAGERES["zs"]) * (ETAGERES["y1"] - ETAGERES["y0"]) / 100
CHARGE_LIVRES = 25          # kg par mètre de tablette pleine de livres (ordre de grandeur)

# ------------------------------------------------------------------ ③ canapé, mur nord, dans l'angle de la bibliothèque
# Dos au mur nord, tourné vers le sud ; une allée de 60 devant l'enfilade pour en ouvrir les portes.
ALLEE_ENFILADE = 60
# IKEA SÖDERHAMN 3 places avec accoudoirs, housse Gunnared gris moyen : 198 × 99 × 83, assise 186 × 48 à 40, 519 €
CANAPE = dict(x0=ENFILADE["p"] + ALLEE_ENFILADE, l=198, p=99, assise=40, dos=83, accoudoir=6, dossier=22,
              nom="IKEA SÖDERHAMN 3 places, Gunnared gris moyen", prix=519,
              url="https://www.ikea.com/fr/fr/p/soederhamn-canape-3-places-gunnared-gris-moyen-s69528099/")
CANAPE["x1"] = CANAPE["x0"] + CANAPE["l"]
_c = CANAPE
MEUBLES += [
    Bloc("canape", "canape_assise", _c["x0"], _c["x1"], 0, _c["p"], 10, _c["assise"], etiq="③"),
    Bloc("canape", "canape_dossier", _c["x0"], _c["x1"], 0, _c["dossier"], _c["assise"], _c["dos"]),
    Bloc("canape", "canape_accoudoir_o", _c["x0"], _c["x0"] + _c["accoudoir"], 0, _c["p"], _c["assise"], 62),
    Bloc("canape", "canape_accoudoir_e", _c["x1"] - _c["accoudoir"], _c["x1"], 0, _c["p"], _c["assise"], 62),
]

# ------------------------------------------------------------------ ④ desserte et platine vinyle, à côté de la baie
# Contre le mur nord, dans le décroché nord-est (x 414 → 544), à côté de la baie : rien devant le vitrage (V4.3).
# Façade vers le sud ; les vinyles sont rangés en rangées est-ouest, dos vers la pièce.
DESSERTE = dict(x0=DECROCHE["x0"] + 1, x1=L - 1, y0=DECROCHE["y"] + 1, y1=DECROCHE["y"] + 46, z1=75, pieds=5,
                niveaux=[7, 40], ep=2)
_d = DESSERTE
MEUBLES.append(Bloc("desserte", "desserte_dessus", _d["x0"], _d["x1"], _d["y0"], _d["y1"], _d["z1"] - _d["ep"], _d["z1"],
                    etiq="④"))
for z in _d["niveaux"]:
    MEUBLES.append(Bloc("desserte", f"desserte_tablette_{z}", _d["x0"], _d["x1"], _d["y0"], _d["y1"], z - _d["ep"], z))
for x in (_d["x0"], _d["x1"] - _d["ep"]):
    MEUBLES.append(Bloc("desserte", f"desserte_joue_{x}", x, x + _d["ep"], _d["y0"], _d["y1"], 0, _d["z1"]))
for z0 in _d["niveaux"]:
    MEUBLES.append(Bloc("vinyles", f"vinyles_{z0}", _d["x0"] + _d["ep"] + 2, _d["x1"] - _d["ep"] - 2,
                        _d["y0"] + 6, _d["y0"] + 6 + 31.5, z0, z0 + 31.5, contenu="vinyles"))
_xm = (_d["x0"] + _d["x1"]) / 2
PLATINE = Bloc("platine", "platine", _xm - 22.5, _xm + 22.5, _d["y0"] + 4, _d["y0"] + 40, _d["z1"], _d["z1"] + 14)
MEUBLES.append(PLATINE)
CM_VINYLES = 2 * (_d["x1"] - _d["x0"] - 2 * _d["ep"] - 4)         # deux rangées de 31,5 de profondeur
VINYLES = round(CM_VINYLES / 0.35)                                   # ≈ 3,5 mm par disque sous pochette

# ------------------------------------------------------------------ ⑧ meuble bas face au canapé, écran de projection
# Le mur sud, en face du canapé, sert d'écran : un meuble bas style enfilade scandinave, peu profond (35) pour laisser
# la place à la table ouverte, centré sur le canapé ; l'image commence 25 au-dessus.
CONSOLE = dict(l=160, p=35, z1=55, pieds=15)
CONSOLE["x0"] = (CANAPE["x0"] + CANAPE["x1"]) / 2 - CONSOLE["l"] / 2
CONSOLE["x1"] = CONSOLE["x0"] + CONSOLE["l"]
CONSOLE["y1"] = P - 1
CONSOLE["y0"] = CONSOLE["y1"] - CONSOLE["p"]
_k = CONSOLE
MEUBLES.append(Bloc("caisson", "console_caisson", _k["x0"], _k["x1"], _k["y0"] + 2, _k["y1"], _k["pieds"], _k["z1"],
                    etiq="⑧"))
for k in range(3):     # trois façades : deux portes et un abattant au milieu (box, lecteur, câbles)
    a = _k["x0"] + _k["l"] * k / 3
    MEUBLES.append(Bloc("facade", f"console_facade_{k}", a + 0.2, a + _k["l"] / 3 - 0.2, _k["y0"], _k["y0"] + 2,
                        _k["pieds"] + 0.2, _k["z1"] - 0.2, contenu="box, câbles" if k == 1 else ""))
for x in (_k["x0"] + 8, _k["x1"] - 10):
    for y in (_k["y0"] + 6, _k["y1"] - 8):
        MEUBLES.append(Cyl("pied", f"console_pied_{x}_{y}", x, y, 1.6, 0, _k["pieds"]))
# image 16/9 de 200 de large, centrée sur le canapé ; vidéoprojecteur au plafond au-dessus du canapé
ECRAN = dict(l=200, bas=CONSOLE["z1"] + 25)
ECRAN["h"] = round(ECRAN["l"] * 9 / 16)
ECRAN["x0"] = (CANAPE["x0"] + CANAPE["x1"]) / 2 - ECRAN["l"] / 2
ECRAN["x1"] = ECRAN["x0"] + ECRAN["l"]
PROJECTEUR = dict(cx=(CANAPE["x0"] + CANAPE["x1"]) / 2, cy=50, l=30, p=25, z0=226)
PROJECTEUR["recul"] = P - PROJECTEUR["cy"]                            # distance de projection
PROJECTEUR["rapport"] = PROJECTEUR["recul"] / ECRAN["l"]             # rapport de projection nécessaire
MEUBLES += [
    Bloc("projection", "ecran", ECRAN["x0"], ECRAN["x1"], P - 1, P, ECRAN["bas"], ECRAN["bas"] + ECRAN["h"]),
    Bloc("projecteur", "projecteur", PROJECTEUR["cx"] - PROJECTEUR["l"] / 2, PROJECTEUR["cx"] + PROJECTEUR["l"] / 2,
         PROJECTEUR["cy"] - PROJECTEUR["p"] / 2, PROJECTEUR["cy"] + PROJECTEUR["p"] / 2, PROJECTEUR["z0"],
         PROJECTEUR["z0"] + 12),
    Cyl("pied", "projecteur_tige", PROJECTEUR["cx"], PROJECTEUR["cy"], 1.5, PROJECTEUR["z0"] + 12, H),
]

# ------------------------------------------------------------------ climatisation (existante)
# Unité murale sur le mur sud, tout à l'est (position et dimensions à relever).
CLIM = dict(x0=L - 94, x1=L - 4, p=22, z0=205, z1=235)
ENVELOPPE.append(Bloc("clim", "clim", CLIM["x0"], CLIM["x1"], P - CLIM["p"], P, CLIM["z0"], CLIM["z1"]))

# ------------------------------------------------------------------ ⑤ table ronde à volets et allonges
# Type « Louis-Philippe » (souvent d'occasion). Au quotidien, ronde Ø 100 (volets levés) avec 4 chaises, dans l'angle
# sud-est, face à la baie ; pour recevoir, on la tire au milieu et on ajoute 4 allonges de 45 : ovale 280 × 100
# est-ouest, entre le canapé et le meuble bas. Une Ø 90 plafonne vers 190 ouverte (8 à 10 couverts).
# Les 8 chaises pliantes de plus sont rangées dans le kafoutche extérieur.
TABLE = dict(cx=295, d=100, allonges=4, allonge=45, z1=75, ep=3, pied=(18, 18), ronde=(440, 262))
TABLE["cy"] = (CANAPE["p"] + CONSOLE["y0"]) / 2                      # à égale distance du canapé et du meuble bas
TABLE["r"] = TABLE["d"] / 2
TABLE["ouvert"] = TABLE["d"] + TABLE["allonges"] * TABLE["allonge"]
CONFIGS = {"f": dict(nom="ronde", chaises=4), "o": dict(nom="ouverte", chaises=12, long=TABLE["ouvert"])}
_t = TABLE
_rx, _ry = TABLE["ronde"]
MEUBLES.append(Bloc("table", "table_plateau_f", _rx - _t["r"], _rx + _t["r"], _ry - _t["r"], _ry + _t["r"],
                    _t["z1"] - _t["ep"], _t["z1"], etiq="⑤", config="f"))
for sx in (-1, 1):
    for sy in (-1, 1):
        MEUBLES.append(Cyl("pied", f"table_pied_f_{sx}_{sy}", _rx + sx * _t["pied"][0], _ry + sy * _t["pied"][1], 2.5,
                           0, _t["z1"] - _t["ep"], config="f"))
# ouverte
_s = (TABLE["ouvert"] - TABLE["d"]) / 2                             # demi-longueur des allonges
CONFIGS["o"]["s"] = _s
MEUBLES.append(Bloc("table", "table_plateau_o", _t["cx"] - _s - _t["r"], _t["cx"] + _s + _t["r"],
                    _t["cy"] - _t["r"], _t["cy"] + _t["r"], _t["z1"] - _t["ep"], _t["z1"], etiq="⑤", config="o"))
for sx in (-1, 1):
    for sy in (-1, 1):
        MEUBLES.append(Cyl("pied", f"table_pied_o_{sx}_{sy}", _t["cx"] + sx * (_s + _t["pied"][0]),
                           _t["cy"] + sy * _t["pied"][1], 2.5, 0, _t["z1"] - _t["ep"], config="o"))

# chaises 45 × 45, assise à 46, dossier à 85 ; centre à 12,5 au-delà du bord (assise glissée de 10 sous le plateau)
CHAISE = dict(l=45, assise=46, dos=85, recul=12.5)


def _chaises_table(s, n):
    """n chaises à pas égal sur le contour décalé de l'ovale, une à chaque bout : (x, y, angle vers l'extérieur)."""
    r = TABLE["r"] + CHAISE["recul"]
    cx, cy = TABLE["cx"], TABLE["cy"]
    arc = math.pi * r
    per = 4 * s + 2 * arc
    o = []
    for k in range(n):
        d = (k * per / n) % per                                      # depuis le bout est, vers le sud
        if d < arc / 2:                                              # demi-cercle est, moitié sud
            a = d / r
            o.append((cx + s + r * math.cos(a), cy + r * math.sin(a), math.degrees(a)))
        elif d < arc / 2 + 2 * s:                                    # grand côté sud, vers l'ouest
            o.append((cx + s - (d - arc / 2), cy + r, 90))
        elif d < 1.5 * arc + 2 * s:                                  # demi-cercle ouest
            a = math.pi / 2 + (d - arc / 2 - 2 * s) / r
            o.append((cx - s + r * math.cos(a), cy + r * math.sin(a), math.degrees(a)))
        elif d < 1.5 * arc + 4 * s:                                  # grand côté nord, vers l'est
            o.append((cx - s + (d - 1.5 * arc - 2 * s), cy - r, -90))
        else:                                                        # demi-cercle est, moitié nord
            a = 1.5 * math.pi + (d - 1.5 * arc - 4 * s) / r
            o.append((cx + s + r * math.cos(a), cy + r * math.sin(a), math.degrees(a)))
    return o


_rc = TABLE["r"] + CHAISE["recul"]
CHAISES = {"f": [(_rx + _rc * math.cos(math.radians(a)), _ry + _rc * math.sin(math.radians(a)), a)
                 for a in (45, 135, 225, 315)],
           "o": _chaises_table(_s, CONFIGS["o"]["chaises"])}
CHAISES_PLIANTES = CONFIGS["o"]["chaises"] - CONFIGS["f"]["chaises"]
PAS_CHAISES = (4 * _s + 2 * math.pi * (TABLE["r"] + CHAISE["recul"])) / CONFIGS["o"]["chaises"]


def chaise_blocs(cx, cy, a, cfg, i):
    """Emprise d'une chaise tournée (assise, puis dossier côté extérieur) pour les coupes."""
    c, s, h = math.cos(math.radians(a)), math.sin(math.radians(a)), CHAISE["l"] / 2
    ex, ey = h * (abs(c) + abs(s)), h * (abs(s) + abs(c))
    bx, by = cx + c * (h - 2), cy + s * (h - 2)                  # milieu du dossier
    dx, dy = h * abs(s) + 2, h * abs(c) + 2
    return [Bloc("chaise", f"chaise_{cfg}_{i}", cx - ex, cx + ex, cy - ey, cy + ey, 0, CHAISE["assise"], config=cfg),
            Bloc("chaise", f"chaise_{cfg}_{i}_dos", bx - dx, bx + dx, by - dy, by + dy, CHAISE["assise"], CHAISE["dos"],
                 config=cfg)]


for cfg, lst in CHAISES.items():
    for i, (x, y, a) in enumerate(lst):
        MEUBLES += chaise_blocs(x, y, a, cfg, i)

# suspension au-dessus de la table ronde (place du quotidien) : Ø ≈ moitié de la table, 75 au-dessus du plateau
SUSPENSION = dict(d=50, z0=150, z1=172)
MEUBLES.append(Cyl("lampe", "suspension", _rx, _ry, SUSPENSION["d"] / 2, SUSPENSION["z0"],
                   SUSPENSION["z1"]))

# ------------------------------------------------------------------ ⑥ table basse, ⑦ siège (DYVLINGE ou chilienne)
# Ovale 105 × 55 (un peu plus de la moitié du canapé, angles adoucis pour circuler), dessus à 38, sous l'assise (42),
# à 40 du canapé. Table ouverte, elle se range debout dans l'allée devant le module nord de l'enfilade.
TABLE_BASSE = dict(l=105, p=55, z1=38, ecart=40)
_tb = TABLE_BASSE
_tbx = (CANAPE["x0"] + CANAPE["x1"]) / 2 - _tb["l"] / 2
_tby = CANAPE["p"] + _tb["ecart"]
_ax = ENFILADE["p"] + (ALLEE_ENFILADE - _tb["p"]) / 2
TABLE_BASSE["pos"] = {"f": (_tbx, _tby, _tbx + _tb["l"], _tby + _tb["p"]), "o": (_ax, 2, _ax + _tb["p"], 2 + _tb["l"])}
for cfg, (x0, y0, x1, y1) in TABLE_BASSE["pos"].items():
    MEUBLES.append(Bloc("table_basse", f"table_basse_{cfg}", x0, x1, y0, y1, _tb["z1"] - 3, _tb["z1"], etiq="⑥",
                        config=cfg))
    for px in (x0 + 4, x1 - 6):
        for py in (y0 + 4, y1 - 6):
            MEUBLES.append(Bloc("pied", f"table_basse_{cfg}_pied_{px}_{py}", px, px + 2, py, py + 2, 0, _tb["z1"] - 3,
                                config=cfg))
# ⑦ siège pivotant IKEA DYVLINGE (63 × 75 × 68, assise 43), tourné vers le canapé, pieds avant sur le tapis ;
# table ouverte, il recule contre le mur nord, à côté de la desserte.
DYVLINGE = dict(l=63, p=75, h=68, assise=43, prix=189,
                url="https://www.ikea.com/fr/fr/p/dyvlinge-siege-pivotant-kelinge-orange-00581918/",
                pos={"f": (322, 108), "o": (340, 52)})                 # angle nord-ouest de l'emprise


def _dyvlinge(cfg, x0, y0):
    d = DYVLINGE
    x1, y1 = x0 + d["p"], y0 + d["l"]
    return [Bloc("fauteuil", f"dyvlinge_{cfg}_assise", x0, x1, y0, y1, 25, d["assise"], etiq="⑦", config=cfg,
                 assise="dyv"),
            Bloc("fauteuil", f"dyvlinge_{cfg}_dos", x1 - 18, x1, y0, y1, d["assise"], d["h"], config=cfg, assise="dyv"),
            Cyl("pied", f"dyvlinge_{cfg}_pied", (x0 + x1) / 2, (y0 + y1) / 2, 2.5, 3, 25, config=cfg, assise="dyv"),
            Cyl("pied", f"dyvlinge_{cfg}_etoile", (x0 + x1) / 2, (y0 + y1) / 2, 30, 0, 3, config=cfg, assise="dyv")]


for cfg, (x0, y0) in DYVLINGE["pos"].items():
    MEUBLES += _dyvlinge(cfg, x0, y0)
# ⑦ variante : chilienne (transat), 130 × 60 dépliée, tête à l'est ; table ouverte, pliée contre le mur sud.
CHILIENNE = dict(l=60, long=130, x0=318, y0=100, pliee=12)
_ch = CHILIENNE
MEUBLES += [
    Bloc("chilienne", "chilienne_toile", _ch["x0"], _ch["x0"] + _ch["long"], _ch["y0"], _ch["y0"] + _ch["l"], 25, 40,
         etiq="⑦", config="f", assise="chil"),
    Bloc("chilienne", "chilienne_dos", _ch["x0"] + _ch["long"] - 40, _ch["x0"] + _ch["long"], _ch["y0"],
         _ch["y0"] + _ch["l"], 40, 95, config="f", assise="chil"),
    Bloc("chilienne", "chilienne_pliee", 60, 60 + _ch["l"], P - 1 - _ch["pliee"], P - 1, 0, 120,
         etiq="⑦", config="o", assise="chil"),
]

# ------------------------------------------------------------------ décoration (bouton Déco)
# Tapis, luminaires, plantes, cadres et livres : indicatifs, ils ne comptent pas dans les dégagements.
DECO = []
# tapis : un seul, sous le coin canapé (pas sous la table à manger). 250 × 180 : 25 de plus que le canapé de chaque
# côté, pieds avant du canapé dessus (20), il dépasse la table basse de 65 et reçoit les pieds avant du siège :
# il réunit le canapé, la table basse et le siège en un seul coin.
TAPIS = dict(l=250, p=180, sous_canape=20)
TAPIS["x0"] = (CANAPE["x0"] + CANAPE["x1"]) / 2 - TAPIS["l"] / 2
TAPIS["x1"] = TAPIS["x0"] + TAPIS["l"]
TAPIS["y0"] = CANAPE["p"] - TAPIS["sous_canape"]
TAPIS["y1"] = TAPIS["y0"] + TAPIS["p"]
DECO.append(Bloc("tapis", "tapis_salon", TAPIS["x0"], TAPIS["x1"], TAPIS["y0"], TAPIS["y1"], 0, 1, deco=True))
# coussins velours jaune moutarde sur le canapé : deux à l'ouest (50 et 45, décalés), un à l'est (45) ; posés sur
# l'assise contre les coussins de dossier
COUSSINS = dict(couleur="#C08A2E", nom="velours jaune moutarde (comme les coussins de la banquette de la cuisine)")
for nom, x0, l, h in (("o1", CANAPE["x0"] + 10, 50, 50), ("o2", CANAPE["x0"] + 52, 45, 45),
                      ("e1", CANAPE["x1"] - 10 - 45, 45, 45)):
    DECO.append(Bloc("coussin", f"coussin_{nom}", x0, x0 + l, 57, 71, CANAPE["assise"] + 3, CANAPE["assise"] + 3 + h,
                     deco=True))
# luminaires : lampadaire de lecture contre l'accoudoir est du canapé, derrière l'épaule de qui est dans le siège
# (hors du passage devant la desserte) ; lampe à poser sur l'enfilade (sous la 1re tablette) ; petite lampe au bout
# est de la desserte
LAMPADAIRE = dict(cx=CANAPE["x1"] + 17, cy=62, base=15, abat=20, z=(118, 142))
DECO += [Cyl("lampe_pied", "lampadaire_socle", LAMPADAIRE["cx"], LAMPADAIRE["cy"], LAMPADAIRE["base"], 0, 3, deco=True),
         Cyl("lampe_pied", "lampadaire_tige", LAMPADAIRE["cx"], LAMPADAIRE["cy"], 1, 3, LAMPADAIRE["z"][0], deco=True),
         Cyl("lampe", "lampadaire_abat_jour", LAMPADAIRE["cx"], LAMPADAIRE["cy"], LAMPADAIRE["abat"], *LAMPADAIRE["z"],
             deco=True)]
for nom, cx, cy, z0, h, r in (("enfilade", 22, 40, ENFILADE["z1"], 40, 14), ("desserte", DESSERTE["x1"] - 16, 22, DESSERTE["z1"], 35, 11)):
    DECO += [Cyl("lampe_pied", f"lampe_{nom}_pied", cx, cy, 5, z0, z0 + h - 16, deco=True),
             Cyl("lampe", f"lampe_{nom}_abat_jour", cx, cy, r, z0 + h - 18, z0 + h, deco=True)]
# plantes : une grande à droite du meuble bas, hors de l'image et loin de la clim (air froid et sec) ;
# des branches sur l'enfilade
for nom, cx, cy, r, h in (("sud", CONSOLE["x1"] + 52, 337, 16, 160),):
    DECO += [Cyl("pot", f"pot_{nom}", cx, cy, r, 0, 35, deco=True),
             Cyl("plante", f"plante_{nom}", cx, cy, r + 6, 35, h, deco=True)]
DECO += [Cyl("pot", "vase_enfilade", 22, 205, 8, ENFILADE["z1"], ENFILADE["z1"] + 28, deco=True),
         Cyl("plante", "branches_enfilade", 22, 205, 12, ENFILADE["z1"] + 28, ENFILADE["z1"] + 40, deco=True)]
# cadres : au-dessus du canapé, une paire 55 × 70 espacée de 8 (118 de large ≈ 2/3 du canapé), centrée, bas à 20 du
# dossier ; au-dessus de la desserte, 80 × 60 centré, bas à 135 pour ouvrir le capot de la platine. Mur sud : écran.
_xc = (CANAPE["x0"] + CANAPE["x1"]) / 2
_zc = CANAPE["dos"] + 20
CADRES = [(_xc - 59, _xc - 4, 0, _zc, _zc + 70), (_xc + 4, _xc + 59, 0, _zc, _zc + 70),
          (_xm - 40, _xm + 40, DECROCHE["y"], 135, 195)]
for i, (x0, x1, y, z0, z1) in enumerate(CADRES):
    DECO.append(Bloc("cadre_mur", f"cadre_{i}", x0, x1, y, y + 3, z0, z1, deco=True))
# livres sur les étagères : rangées de hauteurs variées, avec des vides pour les objets
_alea = [23, 27, 30, 21, 25, 28, 24, 22, 29, 26]
for k, z in enumerate(ETAGERES["zs"][:-1]):
    y, n = ETAGERES["y0"] + 4, 0
    while y < ETAGERES["y1"] - 30:
        l = 30 + 12 * ((k + n) % 4)                       # longueur de la rangée
        h = _alea[(k * 3 + n) % len(_alea)]
        DECO.append(Bloc("livres", f"livres_{k}_{n}", 1, 22, y, min(y + l, ETAGERES["y1"] - 4), z, z + h, deco=True))
        y += l + (14 if (k + n) % 3 == 0 else 3)
        n += 1
MEUBLES += DECO

# ------------------------------------------------------------------ dégagements (cotés sur le plan)
_o = CONFIGS["o"]
DEGAGEMENTS = dict(
    canape_table=TABLE["cy"] - TABLE["r"] - CANAPE["p"],
    table_sud=CONSOLE["y0"] - TABLE["cy"] - TABLE["r"],
    bout_ouest=TABLE["cx"] - _o["long"] / 2 - ENFILADE["p"],
    bout_est=L - (TABLE["cx"] + _o["long"] / 2),
    derriere_chaises=TABLE["cy"] - TABLE["r"] - CHAISE["recul"] - CHAISE["l"] / 2 - CANAPE["p"],
    canape_basse=TABLE_BASSE["ecart"],
    canape_console=CONSOLE["y0"] - CANAPE["p"],
)

# ------------------------------------------------------------------ tables qui se replient (recherche du 11/10/2026)
# (type, modèle, repliée, ouverte, places, prix, source)
TABLES_REPLIABLES = [
    ("Ronde à volets et allonges", "dessin V4.6 (à chiner)", "Ø 100 (≈ 50 de large volets baissés)",
     "280 × 100 avec 4 allonges de 45", "4 / 12 (serré)", "—", ""),
    ("Ronde extensible Ø 90", "Kaufland PERO (stratifié, pied hêtre)", "Ø 90", "Ø 190", "4 à 10", "409 €",
     "https://www.kaufland.fr/product/501274403/"),
    ("Ronde Louis-Philippe Ø 120", "reproduction chêne, 4 allonges de 50 (1stDibs)", "Ø 120", "≈ 320 × 120", "12",
     "—", "https://www.1stdibs.com/fr/meubles/tables/tables-de-salle-%C3%A0-manger/table-ronde-extensible-de-style-louis-philippe-en-ch%C3%AAne-massif-et-4-feuilles/id-f_24516482"),
    ("Ovale à volets et allonges", "Louis-Philippe, antiquaire (exemple)", "59 × 118 (volets baissés)",
     "100 × 118, 229 avec 3 allonges", "12 annoncées (serré)", "2 200 €",
     "https://www.antiguedades-en-francia.es/item/120656/small-oval-table-with-3-extensions-xixth"),
    ("Console extensible", "Konte Design Gaiole (bois, acier oxydé)", "90 × 45", "295 × 90 (5 rallonges de 50)",
     "12", "789 € (soldé)", "https://www.kontedesign.com/fr/p/console-gaiole-en-bois-et-acier-oxyde-90x45-cm-extensible-a-90x295-cm/"),
    ("Console extensible", "Vente-unique Evolve (frêne blanc)", "90 × 42", "302 × 90 (5 rallonges de 52, rangées dans la console)",
     "12 à 14", "840 €", "https://www.vente-unique.com/p/console-extensible-90x42-302-cm-evolve-frene-blanc"),
    ("Table à abattants", "IKEA NORDEN", "26 × 80", "152 × 80", "2 à 4 (6 serrés)", "—",
     "https://www.dimensions.com/element/ikea-norden-gateleg-table"),
]
# rendus 3D : (titre, version du modèle rendue, [(vue, nom de la variante)])
RENDUS = [("Vue isométrique depuis le sud-est (murs sud et est coupés) : table ronde, DYVLINGE, déco", "V4.10",
           [("iso", "Chêne"), ("iso_noyer", "Noyer")])]

CHANGEMENTS = [
    ("V4.10", "11/10/2026",
     "Rendu : variante noyer (vue iso_noyer) où tout le chêne (enfilade, étagères, desserte, table basse, meuble "
     "bas) passe en noyer ; bouton Chêne / Noyer sous le titre du rendu."),
    ("V4.9", "11/10/2026",
     "Canapé SÖDERHAMN en housse Gunnared gris moyen (519 €, assise à 40 relevée sur la fiche). Trois coussins "
     "velours jaune moutarde (déco). Mur derrière la desserte (mur nord du décroché) en papier peint Hermione, celui "
     "essayé dans la cuisine. Rendu iso refait (la fiche Gunnared n'a pas de modèle 3D : géométrie du modèle Fridtuna, "
     "tissu reteinté en gris)."),
    ("V4.8", "11/10/2026",
     "Canapé = IKEA SÖDERHAMN 3 places avec accoudoirs, 198 × 99 × 83 (au lieu de 200 × 90) : la table ouverte "
     "se recentre entre lui et le meuble bas (61,5 de chaque côté). Rendu : modèles 3D IKEA du SÖDERHAMN et du "
     "DYVLINGE (fichiers .glb de la vue 3D des fiches produit, 3d/modeles/ikea/) à la place des volumes simplifiés."),
    ("V4.7", "11/10/2026",
     "Sol carrelé (grès cérame 60 × 60 effet pierre claire, pose droite, teinte à choisir) ; murs et plinthes du même "
     "blanc chaud que la cuisine (#EFE9DC, piste Wimborne White). Premier rendu 3D : vue isométrique depuis le "
     "sud-est (3d/salon/rendu.py, just salon-rendu), table ronde, DYVLINGE, déco."),
    ("V4.6", "11/10/2026",
     "Mur sud = écran de projection : meuble bas style enfilade scandinave 160 × 35 × 55 face au canapé, image "
     "200 × 112 au-dessus, vidéoprojecteur au plafond au-dessus du canapé (recul 308). Clim existante sur le mur "
     "sud, tout à l'est (plante déplacée hors du souffle). Table Ø 100 au lieu de 120 (Ø 90 : 190 ouverte au plus, "
     "8 à 10 couverts) : 280 × 100 ouverte avec 4 allonges, entre le canapé et le meuble bas. Siège pivotant IKEA "
     "DYVLINGE à la place de la chilienne, bouton Siège DYVLINGE / chilienne. Lampadaire déplacé contre "
     "l'accoudoir est du canapé (il gênait le passage devant la desserte). Table ouverte : table basse debout dans "
     "l'allée de l'enfilade, DYVLINGE contre le mur nord. Coupe D-D sur le mur sud."),
    ("V4.5", "11/10/2026",
     "Plus de tapis sous la table à manger. Proportions revues : tapis 250 × 180 (25 de plus que le canapé de chaque "
     "côté, pieds avant du canapé et de la chilienne dessus) ; table basse ovale 105 × 55 × 38 ; paire de cadres "
     "55 × 70 au-dessus du canapé (118 de large, bas à 20 du dossier) ; cadre 80 × 60 au-dessus de la desserte, bas à "
     "135 pour le capot de la platine ; cadre à côté de la baie retiré (la grande plante suffit) ; lampadaire de "
     "lecture abaissé (abat-jour 104 → 128, sous le cadre de la desserte) ; suspension Ø 60 au-dessus de la table ronde."),
    ("V4.4", "11/10/2026",
     "Bouton Déco (barre du haut) : tapis sous la table basse, "
     "lampadaire liseuse près de la chilienne, lampes à poser sur l'enfilade et la desserte, plantes (angle sud-est, mur sud, branches sur l'enfilade) ; chilienne pliée contre le mur sud quand la table est ouverte, quatre "
     "cadres (au-dessus du canapé, de la desserte, à côté de la baie au-dessus de la plante) et des livres sur les étagères, sur le plan "
     "et les coupes."),
    ("V4.3", "11/10/2026",
     "Desserte contre le mur nord, dans le décroché nord-est : 128 × 45, façade au sud, à côté de la baie sans la "
     "masquer (≈ 700 vinyles). Table à volets et allonges laissée ronde au quotidien : Ø 120 avec 4 chaises dans "
     "l'angle sud-est, face à la baie, suspension au-dessus ; ouverte au milieu pour 12, les 8 chaises pliantes de "
     "plus sortent du kafoutche extérieur. Chilienne tournée vers le canapé, tête à l'est ; table basse poussée "
     "à côté du canapé quand la table est ouverte. Bouton Table ronde / ouverte."),
    ("V4.2", "11/10/2026",
     "Desserte 65 × 44 contre le trumeau nord de la baie (y 5 → 70). Table basse 100 × 50 devant le canapé (à 40) et "
     "chilienne 60 × 130 tournée vers lui. Table ovale à volets et allonges (type Louis-Philippe) : repliée 120 × 60 "
     "contre le mur sud au quotidien, ouverte 300 × 120 avec 4 allonges de 45 au milieu pour 12 ; ouverte, la table "
     "basse va dans l'angle nord-est et la chilienne se plie contre le mur est. Bouton Table repliée / ouverte. "
     "Section « Tables qui se replient » : consoles extensibles, table à volets, table à abattants, avec sources."),
    ("V4.1", "11/10/2026",
     "Desserte déplacée : elle n'est plus devant la baie mais contre le trumeau sud du mur est, au ras de la baie "
     "(80 × 45). Table ovale 110 de large à deux rallonges de 60 : 200 fermée (6 couverts), 320 ouverte (12 "
     "couverts, chaises à pas de 70) ; bouton Table ouverte / fermée sur le plan et la coupe C-C, à la place de "
     "4 / 12 couverts. Table recentrée (295, 224) : 79 entre le canapé et la table, 79 au sud."),
    ("V4.0", "11/10/2026",
     "Nouveau départ (source unique 3d/salon/modele.py → plan et coupes générés). Bibliothèque du mur ouest validée "
     "à sa place (258 utiles) : enfilade 258 × 45 × 80 sur pieds, trois modules de 86, et quatre étagères suspendues "
     "au-dessus (fixation à étudier). Canapé 200 × 90 dos au mur nord, dans l'angle de la bibliothèque. Desserte "
     "120 × 45 avec la platine vinyle devant le vantail nord de la baie. Table ronde Ø 130 à trois allonges "
     "(295 × 130, 12 couverts), bouton 4 / 12 couverts sur le plan et les coupes. La V3.1 est archivée."),
]
