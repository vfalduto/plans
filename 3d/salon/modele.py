# Salon V4 : source unique (repart du relevé du salon V3.1 et de la bibliothèque du mur ouest).
#
# Ce fichier ne contient que des données : il est lu par plan.py (HTML : plan et coupes, projetés
# depuis ces volumes). Toute modification se fait ici, jamais dans le HTML.
#
# Cotes en cm : x vers l'est depuis le mur ouest, y vers le sud depuis le mur nord, z depuis le sol fini.
# Chaque volume : Bloc(role, nom, x0, x1, y0, y1, z0, z1). Le rôle fixe le style du plan et des coupes.

import math
from dataclasses import dataclass

VERSION = "V4.0"
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
    config: str = ""    # "" : toujours ; "4" / "12" : seulement avec la table à 4 ou à 12 couverts


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
CANAPE = dict(x0=ENFILADE["p"] + ALLEE_ENFILADE, l=200, p=90, assise=42, dos=80, accoudoir=15, dossier=20)
CANAPE["x1"] = CANAPE["x0"] + CANAPE["l"]
_c = CANAPE
MEUBLES += [
    Bloc("canape", "canape_assise", _c["x0"], _c["x1"], 0, _c["p"], 10, _c["assise"], etiq="③"),
    Bloc("canape", "canape_dossier", _c["x0"], _c["x1"], 0, _c["dossier"], _c["assise"], _c["dos"]),
    Bloc("canape", "canape_accoudoir_o", _c["x0"], _c["x0"] + _c["accoudoir"], 0, _c["p"], _c["assise"], 62),
    Bloc("canape", "canape_accoudoir_e", _c["x1"] - _c["accoudoir"], _c["x1"], 0, _c["p"], _c["assise"], 62),
]

# ------------------------------------------------------------------ ④ desserte et platine vinyle, devant la baie
# Contre le vantail nord de la baie (y 78 → 171) : le vantail sud reste le passage quand la baie est ouverte.
DESSERTE = dict(x0=L - 45, x1=L - 1, y0=52, y1=172, z1=75, pieds=5, niveaux=[7, 40], ep=2)
_d = DESSERTE
MEUBLES.append(Bloc("desserte", "desserte_dessus", _d["x0"], _d["x1"], _d["y0"], _d["y1"], _d["z1"] - _d["ep"], _d["z1"],
                    etiq="④"))
for z in _d["niveaux"]:
    MEUBLES.append(Bloc("desserte", f"desserte_tablette_{z}", _d["x0"], _d["x1"], _d["y0"], _d["y1"], z - _d["ep"], z))
for y in (_d["y0"], _d["y1"] - _d["ep"]):
    MEUBLES.append(Bloc("desserte", f"desserte_joue_{y}", _d["x0"], _d["x1"], y, y + _d["ep"], 0, _d["z1"]))
for z0, z1 in ((_d["niveaux"][0], _d["niveaux"][1] - _d["ep"]), (_d["niveaux"][1], _d["z1"] - _d["ep"])):
    MEUBLES.append(Bloc("vinyles", f"vinyles_{z0}", _d["x0"] + 6, _d["x0"] + 6 + 31.5, _d["y0"] + 4, _d["y1"] - 30,
                        z0, z0 + 31.5, contenu="vinyles"))
PLATINE = Bloc("platine", "platine", _d["x0"] + 4, _d["x0"] + 40, 98, 143, _d["z1"], _d["z1"] + 14, etiq="platine")
MEUBLES.append(PLATINE)
CM_VINYLES = 2 * (_d["y1"] - _d["y0"] - 2 * _d["ep"] - 26)        # rangées de 31,5 de profondeur, 26 laissés libres
VINYLES = round(CM_VINYLES / 0.35)                                   # ≈ 3,5 mm par disque sous pochette

# ------------------------------------------------------------------ ⑤ table ronde à allonges, 4 → 12 couverts
# Ronde Ø 130 au quotidien ; trois allonges de 55 l'ouvrent en ovale de 295 × 130 (est-ouest : la seule direction
# où 12 couverts tiennent). Quatre pieds : chaque moitié emporte deux pieds quand on tire.
TABLE = dict(cx=300, cy=225, d=130, allonges=3, allonge=55, z1=75, ep=3, pied=(35, 35))
TABLE["r"] = TABLE["d"] / 2
TABLE["s"] = TABLE["allonges"] * TABLE["allonge"] / 2              # demi-longueur des allonges
TABLE["long"] = TABLE["d"] + 2 * TABLE["s"]
_t = TABLE
for cfg, s in (("4", 0), ("12", _t["s"])):
    MEUBLES.append(Bloc("table", f"table_plateau_{cfg}", _t["cx"] - _t["r"] - s, _t["cx"] + _t["r"] + s,
                        _t["cy"] - _t["r"], _t["cy"] + _t["r"], _t["z1"] - _t["ep"], _t["z1"], etiq="⑤", config=cfg))
    for sx in (-1, 1):
        for sy in (-1, 1):
            MEUBLES.append(Cyl("pied", f"table_pied_{cfg}_{sx}_{sy}", _t["cx"] + sx * (_t["pied"][0] + s),
                               _t["cy"] + sy * _t["pied"][1], 2.5, 0, _t["z1"] - _t["ep"], config=cfg))

# chaises 45 × 45, assise à 46, dossier à 85 ; centre à 12,5 au-delà du bord (assise glissée de 10 sous le plateau)
CHAISE = dict(l=45, assise=46, dos=85, recul=12.5)


def _chaises_table(s, n_par_bout, angles=None):
    """Centres et orientations (angle vers l'extérieur, degrés, y vers le sud) des chaises autour de la table."""
    r = TABLE["r"] + CHAISE["recul"]
    cx, cy = TABLE["cx"], TABLE["cy"]
    if angles is not None:   # table ronde : chaises aux angles donnés
        return [(cx + r * math.cos(math.radians(a)), cy + r * math.sin(math.radians(a)), a) for a in angles]
    # ovale : 3 chaises par grand côté (pas de 68), n_par_bout sur chaque demi-cercle
    pas = (2 * 2 * s + 2 * math.pi * r) / (6 + 2 * n_par_bout)
    o = []
    for dx in (-pas, 0, pas):
        o += [(cx + dx, cy - r, -90), (cx + dx, cy + r, 90)]
    reste = s - pas
    for k in range(n_par_bout):
        a = math.degrees((pas * (k + 1) - reste) / r)       # depuis le haut du demi-cercle
        for sens in (1, -1):
            ang = -90 + a if sens > 0 else -90 - a
            ox = cx + sens * s
            o.append((ox + r * math.cos(math.radians(ang)), cy + r * math.sin(math.radians(ang)), ang))
    return o


CHAISES = {"4": _chaises_table(0, 0, angles=[-30, 30, 150, 210]), "12": _chaises_table(TABLE["s"], 3)}


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

# suspension au-dessus du centre de la table (abat-jour Ø 45, bas à 150 : 75 au-dessus du plateau)
SUSPENSION = dict(d=45, z0=150, z1=172)
MEUBLES.append(Cyl("lampe", "suspension", TABLE["cx"], TABLE["cy"], SUSPENSION["d"] / 2, SUSPENSION["z0"],
                   SUSPENSION["z1"]))

# ------------------------------------------------------------------ dégagements (cotés sur le plan)
_ch12 = CHAISES["12"]
DEGAGEMENTS = dict(
    canape_table=TABLE["cy"] - TABLE["r"] - CANAPE["p"],
    table_sud=P - TABLE["cy"] - TABLE["r"],
    bout_ouest=TABLE["cx"] - TABLE["r"] - TABLE["s"] - ENFILADE["p"],
    bout_est=L - (TABLE["cx"] + TABLE["r"] + TABLE["s"]),
    table_desserte=DESSERTE["x0"] - (TABLE["cx"] + TABLE["r"]),
)

CHANGEMENTS = [
    ("V4.0", "11/10/2026",
     "Nouveau départ (source unique 3d/salon/modele.py → plan et coupes générés). Bibliothèque du mur ouest validée "
     "à sa place (258 utiles) : enfilade 258 × 45 × 80 sur pieds, trois modules de 86, et quatre étagères suspendues "
     "au-dessus (fixation à étudier). Canapé 200 × 90 dos au mur nord, dans l'angle de la bibliothèque. Desserte "
     "120 × 45 avec la platine vinyle devant le vantail nord de la baie. Table ronde Ø 130 à trois allonges "
     "(295 × 130, 12 couverts), bouton 4 / 12 couverts sur le plan et les coupes. La V3.1 est archivée."),
]
