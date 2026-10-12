# Meuble linge de la salle de bain V3 : source unique.
#
# Ce fichier ne contient que des données : plan.py (page HTML : plan, élévation, coupes, débit), montage.py (notice de
# montage) et cad.py (modèle FreeCAD) les lisent. Toute modification se fait ici, jamais dans le HTML.
#
# Cotes en cm : x vers l'est depuis le mur ouest de la salle de bain, y vers le sud depuis le mur nord, z depuis le sol.
# Le meuble est dans l'alcôve est (x 167 → 234, y 0 → 114). Il est décrit pièce par pièce, dans la version « machine à
# droite » (côté lavabo, au sud) ; la version « machine à gauche » (côté porte, au nord) en est le miroir nord-sud,
# sauf le caisson haut, identique dans les deux versions (serviettes au nord, pharmacie au sud).
#
# Chaque pièce : Bloc(role, nom, x0, x1, y0, y1, z0, z1, rep=…, etape=…) ou Profil (contour dans le plan x-z, extrudé en
# y) pour les côtés et le dos incliné des bacs basculants. rep = repère de la liste de débit, etape = étape de montage.

import math
from dataclasses import dataclass, field, replace

VERSION = "V3.0"
H = 250                 # plafond (confirmé par le client)
X0, X1 = 167, 234       # alcôve : bord ouest (ouverture) et mur du fond (est)
Y0, Y1 = 0, 114         # alcôve : mur nord et mur sud
FACE = 168.1            # nu des façades (1 cm en retrait du bord de l'alcôve)

T, F, B, PT, S = 1.9, 0.8, 1.2, 3.0, 2.2   # épaisseurs : panneau, fond, contreplaqué des bacs, plan, socle


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
    rep: str = ""        # repère de la liste de débit (vide : pas une pièce à découper)
    etape: int = 0       # étape de montage où la pièce apparaît (0 : existant)
    groupe: str = ""     # sous-ensemble (vue éclatée, bacs basculants)
    miroir: bool = True  # suit la bascule droite / gauche
    etiq: str = ""
    encoche: tuple = ()  # (x0, x1, y0, y1) découpée dans la pièce (plan de travail)

    def pts(self, axe):
        """Contour vu le long de l'axe donné : (u, z) avec u = x si axe == "y", u = y si axe == "x"."""
        a, b = (self.x0, self.x1) if axe == "y" else (self.y0, self.y1)
        return [(a, self.z0), (b, self.z0), (b, self.z1), (a, self.z1)]


@dataclass
class Profil:
    """Pièce à contour quelconque dans le plan x-z (côté de bac, dos incliné), extrudée de y0 à y1."""
    role: str
    nom: str
    xz: list
    y0: float
    y1: float
    rep: str = ""
    etape: int = 0
    groupe: str = ""
    miroir: bool = True
    etiq: str = ""
    encoche: tuple = ()

    x0 = property(lambda p: min(x for x, _ in p.xz))
    x1 = property(lambda p: max(x for x, _ in p.xz))
    z0 = property(lambda p: min(z for _, z in p.xz))
    z1 = property(lambda p: max(z for _, z in p.xz))

    def pts(self, axe):
        if axe == "y":
            return list(self.xz)
        return [(self.y0, self.z0), (self.y1, self.z0), (self.y1, self.z1), (self.y0, self.z1)]


def miroir(b):
    if not b.miroir:
        return b
    enc = (b.encoche[0], b.encoche[1], Y1 - b.encoche[3], Y1 - b.encoche[2]) if b.encoche else ()
    return replace(b, y0=Y1 - b.y1, y1=Y1 - b.y0, encoche=enc)


# ------------------------------------------------------------------ hauteurs
SOCLE_H = 20            # surélévation de la machine (demande V3)
LL = dict(l=60, p=60, h=85, nom="lave-linge 60 × 60 × 85 (pieds réglés)")
JEU_PLAN = 1.5          # entre le dessus de la machine et le dessous du plan
Z_PLAN = SOCLE_H + LL["h"] + JEU_PLAN          # dessous du plan : 106,5
Z_DESSUS = Z_PLAN + PT                         # dessus du plan : 109,5
Z_HAUT = 152            # dessous du caisson haut (niche de Z_DESSUS à Z_HAUT)
Z_HAUT1 = H - 2         # dessus du caisson haut ; fileur jusqu'au plafond
PLINTHE = 10

# ------------------------------------------------------------------ plan de l'alcôve (version machine à droite)
J = 0.3                 # jeu contre un mur
CB = dict(y0=Y0 + J, y1=Y0 + J + 52.5, x0=FACE + T, x1=X1 - 11)   # caisson bas des bacs : 52,5 × 53
LLZ = dict(y0=CB["y1"], y1=Y1)                                     # zone de la machine : 61,2
CENTRE = (Y0 + Y1) / 2

PIECES = []


def P(*a, **k):
    b = Bloc(*a, **k)
    PIECES.append(b)
    return b


# ------------------------------------------------------------------ ① socle de la machine (contreplaqué 22)
# Caisson plein : cadre (2 longerons, 3 traverses) sous un plateau, rebord sur trois côtés pour que la machine ne
# « marche » pas à l'essorage. Vissé au caisson bas et au mur latéral.
SOCLE = dict(x0=FACE, x1=FACE + 60, y0=LLZ["y0"] + 0.3, y1=Y1 - J, rebord=1.5)
_s = SOCLE
_zs = SOCLE_H - S
P("socle", "socle_longeron_n", _s["x0"], _s["x1"], _s["y0"], _s["y0"] + S, 0, _zs, rep="S2", etape=1, groupe="socle")
P("socle", "socle_longeron_s", _s["x0"], _s["x1"], _s["y1"] - S, _s["y1"], 0, _zs, rep="S2", etape=1, groupe="socle")
for k, x in enumerate((_s["x0"], (_s["x0"] + _s["x1"] - S) / 2, _s["x1"] - S)):
    P("socle", f"socle_traverse_{k + 1}", x, x + S, _s["y0"] + S, _s["y1"] - S, 0, _zs, rep="S3", etape=1, groupe="socle")
P("socle", "socle_plateau", _s["x0"], _s["x1"], _s["y0"], _s["y1"], _zs, SOCLE_H, rep="S1", etape=1, groupe="socle")
P("rebord", "socle_rebord_avant", _s["x0"], _s["x0"] + _s["rebord"], _s["y0"] + _s["rebord"], _s["y1"] - _s["rebord"],
  SOCLE_H, SOCLE_H + _s["rebord"], rep="S4", etape=1, groupe="socle")
for nom, y in (("n", _s["y0"]), ("s", _s["y1"] - _s["rebord"])):
    P("rebord", f"socle_rebord_{nom}", _s["x0"], _s["x1"], y, y + _s["rebord"], SOCLE_H, SOCLE_H + _s["rebord"],
      rep="S5", etape=1, groupe="socle")
SOCLE["l"], SOCLE["p"] = _s["y1"] - _s["y0"], _s["x1"] - _s["x0"]

# ------------------------------------------------------------------ ② caisson bas des deux bacs (panneau 19)
# Côtés jusqu'au sol, dessous sur la plinthe, une tablette fixe au milieu (deux cases égales), deux traverses à plat
# sous le plan, fond de 8. Les façades sont en applique, sauf la tablette dont le chant reste visible entre elles :
# chaque bac pivote sur le bord avant de sa case et rien ne doit passer sous l'axe.
_c = CB
_xi = _c["x1"] - F                      # arrière des côtés (le fond est vissé au dos)
P("caisson", "cb_cote_n", _c["x0"], _xi, _c["y0"], _c["y0"] + T, 0, Z_PLAN, rep="A1", etape=2, groupe="caisson_bas")
P("caisson", "cb_cote_s", _c["x0"], _xi, _c["y1"] - T, _c["y1"], 0, Z_PLAN, rep="A1", etape=2, groupe="caisson_bas")
_yi0, _yi1 = _c["y0"] + T, _c["y1"] - T
P("caisson", "cb_dessous", _c["x0"], _xi, _yi0, _yi1, PLINTHE, PLINTHE + T, rep="A2", etape=2, groupe="caisson_bas")
_zt1 = Z_PLAN - T                       # dessous des traverses hautes
_case = (_zt1 - (PLINTHE + T) - T) / 2  # hauteur libre de chaque case
_ztab = PLINTHE + T + _case
P("caisson", "cb_tablette", _c["x0"], _xi, _yi0, _yi1, _ztab, _ztab + T, rep="A3", etape=2, groupe="caisson_bas")
P("caisson", "cb_traverse_av", _c["x0"], _c["x0"] + 10, _yi0, _yi1, _zt1, Z_PLAN, rep="A4", etape=2, groupe="caisson_bas")
P("caisson", "cb_traverse_ar", _xi - 10, _xi, _yi0, _yi1, _zt1, Z_PLAN, rep="A4", etape=2, groupe="caisson_bas")
P("fond", "cb_fond", _xi, _c["x1"], _c["y0"], _c["y1"], PLINTHE, Z_PLAN, rep="C2", etape=3, groupe="caisson_bas")
P("plinthe", "cb_plinthe", _c["x0"] + 3, _c["x0"] + 3 + T, _yi0, _yi1, 0, PLINTHE - 0.2, rep="A5", etape=3,
  groupe="caisson_bas")
CASES = [(PLINTHE + T, _ztab), (_ztab + T, _zt1)]   # (fond de case = axe des charnières, plafond de case)

# ------------------------------------------------------------------ ③ bacs basculants (contreplaqué 12)
# Chaque bac est une caisse à côtés en trapèze, vissée derrière sa façade, qui pivote sur une charnière piano au bord
# avant de sa case. Le dos est incliné : aucun point du bac n'est à plus de RAYON de l'axe, il ne touche donc jamais le
# plafond de la case en basculant. Deux compas l'arrêtent à ANGLE. On jette le linge par le haut, dans un sac amovible.
BAC = dict(jeu=0.5, charniere=0.2, h=38, d_bas=42, d_haut=21, angle=30, sac="sac à linge amovible 45 × 35 × 35")
_b = BAC
BAC["y0"], BAC["y1"] = _yi0 + _b["jeu"], _yi1 - _b["jeu"]
FACADES = []
for k, (zc, zp) in enumerate(CASES):
    g = f"bac{k + 1}"
    z0 = zc + _b["charniere"]
    xa, xb, xt = _c["x0"], _c["x0"] + _b["d_bas"], _c["x0"] + _b["d_haut"]
    cote = [(xa, z0), (xb, z0), (xt, z0 + _b["h"]), (xa, z0 + _b["h"])]
    for nom, y in (("n", _b["y0"]), ("s", _b["y1"] - B)):
        PIECES.append(Profil("bac", f"bac{k + 1}_cote_{nom}", cote, y, y + B, rep="B1", etape=5, groupe=g))
    P("bac", f"bac{k + 1}_devant", xa, xa + B, _b["y0"] + B, _b["y1"] - B, z0 + B, z0 + _b["h"], rep="B2", etape=5, groupe=g)
    P("bac", f"bac{k + 1}_fond", xa, xb, _b["y0"] + B, _b["y1"] - B, z0, z0 + B, rep="B3", etape=5, groupe=g)
    # dos incliné : bande de 12 le long de la pente, de (xb, z0 + B) à (xt, z0 + h)
    n = math.hypot(xb - xt, _b["h"])
    ox, oz = -B * _b["h"] / n, -B * (xb - xt) / n   # normale vers l'intérieur
    dos = [(xb, z0 + B), (xt, z0 + _b["h"]), (xt + ox, z0 + _b["h"] + oz), (xb + ox, z0 + B + oz)]
    PIECES.append(Profil("bac", f"bac{k + 1}_dos", dos, _b["y0"] + B, _b["y1"] - B, rep="B4", etape=5, groupe=g))
    # façade en applique : du bas de la case (bac 1 : couvre le dessous) au dessous de la tablette (bac 2 : de la tablette
    # au plan) ; jeu de 0,3 autour
    zf0 = (PLINTHE + 0.3) if k == 0 else (_ztab + T + 0.05)
    zf1 = (_ztab - 0.05) if k == 0 else (Z_PLAN - 0.3)
    FACADES.append((zf0, zf1))
    P("facade", f"bac{k + 1}_facade", FACE, FACE + T, _c["y0"] + 0.15, _c["y1"] - 0.15, zf0, zf1, rep="A6", etape=6,
      groupe=g, etiq=f"Bac {k + 1}")
    BAC[f"axe{k + 1}"] = (xa, zc)
    BAC[f"plafond{k + 1}"] = zp
RAYON = max(math.dist((xa, 0), (x, z - CASES[0][0])) for x, z in
            [(xa + _b["d_bas"], _b["charniere"]), (xa + _b["d_haut"], _b["charniere"] + _b["h"]), (xa, _b["charniere"] + _b["h"])])
CASE_H = _case
assert RAYON < CASE_H - 0.5, (RAYON, CASE_H)   # le bac bascule sans toucher le plafond de sa case


def bascule(x, z, axe, angle):
    """Position d'un point du bac (x, z) une fois basculé de angle degrés vers la pièce autour de axe = (xa, za)."""
    a = math.radians(angle)
    u, w = axe[0] - x, z - axe[1]                     # u : vers la pièce (ouest), w : vers le haut
    u2, w2 = u * math.cos(a) + w * math.sin(a), -u * math.sin(a) + w * math.cos(a)
    return axe[0] - u2, axe[1] + w2


# volume utile d'un bac : intérieur du trapèze × largeur intérieure
_li = (_b["y1"] - _b["y0"]) - 2 * B
_hi = _b["h"] - B
_dbi = _b["d_bas"] - 2 * B
_dhi = _b["d_haut"] - 2 * B
VOLUME_BAC = (_dbi + _dhi) / 2 * _hi * _li / 1000
# bac ouvert : bord haut avant et bord haut arrière (intérieurs), avancée de la façade
_ax = BAC["axe1"]
_avant = bascule(_c["x0"] + B, _ax[1] + _b["charniere"] + _b["h"], _ax, _b["angle"])
_arriere = bascule(_c["x0"] + _b["d_haut"] - B, _ax[1] + _b["charniere"] + _b["h"], _ax, _b["angle"])
_haut_facade = bascule(FACE, FACADES[0][1], _ax, _b["angle"])
# le bas de la façade du bac 2 descend en basculant : il doit rester au-dessus de la façade du bac 1
_bas2 = bascule(FACE, FACADES[1][0], BAC["axe2"], _b["angle"])
assert _bas2[1] > FACADES[0][1] + 0.3, (_bas2, FACADES[0])
BAC["bouche"] = _arriere[0] - _avant[0]          # profondeur de l'ouverture une fois basculé
BAC["bouche_hors"] = CB["x0"] - _arriere[0]      # le bord arrière sort du caisson de tant
BAC["avancee"] = FACE - _haut_facade[0]          # le haut de la façade avance de tant dans la pièce
BAC["largeur_sac"] = _li

# ------------------------------------------------------------------ ④ plan de travail filant (30) et supports
# Tasseaux contre le mur du fond, cornière alu sur le mur latéral côté machine, le caisson bas de l'autre côté.
# Trappe 30 × 10 au fond du plan, centrée sur le meuble : on atteint le robinet d'arrêt derrière la machine.
TRAPPE = dict(x0=X1 - 1 - 10, x1=X1 - 1, y0=CENTRE - 15, y1=CENTRE + 15)
ROBINET = dict(y=CENTRE, z=80)
P("tasseau", "tasseau_fond_n", X1 - 2.7, X1, Y0 + J, TRAPPE["y0"] - 4, Z_PLAN - 4, Z_PLAN, rep="E1", etape=4,
  groupe="supports")
P("tasseau", "tasseau_fond_s", X1 - 2.7, X1, TRAPPE["y1"] + 4, Y1 - J, Z_PLAN - 4, Z_PLAN, rep="E1", etape=4,
  groupe="supports")
P("corniere", "corniere_aile_v", FACE + 2, X1 - 2.7, Y1 - 0.3, Y1, Z_PLAN - 3, Z_PLAN, rep="E2", etape=4, groupe="supports")
P("corniere", "corniere_aile_h", FACE + 2, X1 - 2.7, Y1 - 3, Y1, Z_PLAN - 0.3, Z_PLAN, rep="E2", etape=4, groupe="supports")
P("plan", "plan_travail", FACE, X1 - 1, Y0 + J, Y1 - J, Z_PLAN, Z_DESSUS, rep="D1", etape=8, groupe="plan",
  miroir=False, encoche=(TRAPPE["x0"], TRAPPE["x1"], TRAPPE["y0"], TRAPPE["y1"]))
P("trappe", "trappe_couvercle", TRAPPE["x0"] + 0.2, TRAPPE["x1"] - 0.2, TRAPPE["y0"] + 0.2, TRAPPE["y1"] - 0.2,
  Z_PLAN, Z_DESSUS, rep="D2", etape=8, groupe="plan", miroir=False)
for nom, y in (("n", TRAPPE["y0"] - 4), ("s", TRAPPE["y1"])):
    P("tasseau", f"feuillure_{nom}", TRAPPE["x0"], TRAPPE["x1"], y, y + 4, Z_PLAN - B, Z_PLAN, rep="B5", etape=8,
      groupe="plan", miroir=False)

# ------------------------------------------------------------------ ⑤ caisson haut, P 45, jusqu'au plafond
# Identique dans les deux versions : serviettes au nord, pharmacie et produits divers au sud, deux portes coulissantes.
CH = dict(x0=X1 - 45, x1=X1, y0=Y0 + 0.5, y1=Y1 - 0.5, z0=Z_HAUT, z1=Z_HAUT1, retrait=6)
_h = CH
_hx = _h["x1"] - F
_hy0, _hy1 = _h["y0"] + T, _h["y1"] - T
_hz0, _hz1 = _h["z0"] + T, _h["z1"] - T


def H_(*a, **k):
    return P(*a, miroir=False, groupe="caisson_haut", **k)


H_("caisson", "ch_cote_n", _h["x0"], _hx, _h["y0"], _hy0, _h["z0"], _h["z1"], rep="A7", etape=9)
H_("caisson", "ch_cote_s", _h["x0"], _hx, _hy1, _h["y1"], _h["z0"], _h["z1"], rep="A7", etape=9)
H_("caisson", "ch_dessous", _h["x0"], _hx, _hy0, _hy1, _h["z0"], _hz0, rep="A8", etape=9)
H_("caisson", "ch_dessus", _h["x0"], _hx, _hy0, _hy1, _hz1, _h["z1"], rep="A8", etape=9)
_ym = CENTRE
H_("caisson", "ch_montant", _h["x0"] + _h["retrait"], _hx, _ym - T / 2, _ym + T / 2, _hz0, _hz1, rep="A9", etape=9)
H_("fond", "ch_fond", _hx, _h["x1"], _h["y0"], _h["y1"], _h["z0"], _h["z1"], rep="C1", etape=9)
CH["serviettes"] = 2    # étagères côté serviettes (nord) : 3 cases
CH["pharmacie"] = 4     # étagères côté pharmacie (sud) : 5 cases
_hi_h = _hz1 - _hz0
CH["case_serviettes"] = (_hi_h - CH["serviettes"] * T) / (CH["serviettes"] + 1)
CH["case_pharmacie"] = (_hi_h - CH["pharmacie"] * T) / (CH["pharmacie"] + 1)
for cote, n, y0, y1, rep in (("n", CH["serviettes"], _hy0 + 0.2, _ym - T / 2 - 0.2, "A10"),
                             ("s", CH["pharmacie"], _ym + T / 2 + 0.2, _hy1 - 0.2, "A11")):
    case = (_hi_h - n * T) / (n + 1)
    for k in range(n):
        z = _hz0 + (k + 1) * case + k * T
        H_("etagere", f"ch_etagere_{cote}{k + 1}", _h["x0"] + _h["retrait"] + 0.5, _hx - 0.3, y0, y1, z, z + T,
           rep=rep, etape=11)
# portes coulissantes intérieures : deux rails, recouvrement 3 au milieu
_lp = (_hy1 - _hy0 + 3) / 2
_zp0, _zp1 = _hz0 + 0.6, _hz1 - 0.6
H_("porte", "ch_porte_n", _h["x0"] + 0.3, _h["x0"] + 0.3 + T, _hy0, _hy0 + _lp, _zp0, _zp1, rep="A12", etape=11,
   etiq="Serviettes")
H_("porte", "ch_porte_s", _h["x0"] + 2.6, _h["x0"] + 2.6 + T, _hy1 - _lp, _hy1, _zp0, _zp1, rep="A12", etape=11,
   etiq="Pharmacie et produits divers")
H_("fileur", "ch_fileur", _h["x0"], _h["x0"] + T, _h["y0"], _h["y1"], _h["z1"], H, rep="A13", etape=11)
CH["porte"] = (_lp, _zp1 - _zp0)

# ------------------------------------------------------------------ équipements (pas à découper)
MACHINE = Bloc("machine", "lave_linge", FACE, FACE + LL["p"], LLZ["y0"] + (LLZ["y1"] - LLZ["y0"] - LL["l"]) / 2,
               LLZ["y0"] + (LLZ["y1"] - LLZ["y0"] + LL["l"]) / 2, SOCLE_H, SOCLE_H + LL["h"], etape=7, groupe="machine")
LED = Bloc("led", "profil_led", _h["x0"] + 2, _h["x0"] + 4, _hy0 + 2, _hy1 - 2, Z_HAUT - 1, Z_HAUT, etape=11,
           miroir=False, groupe="caisson_haut")
PRISES = Bloc("prise", "prises_niche", X1 - 1, X1, 84, 104, 122, 130, miroir=False)   # bloc 2 prises + USB, mur du fond
EQUIPEMENTS = [MACHINE, LED, PRISES]

# ------------------------------------------------------------------ salle de bain (pour le plan)
SDB = dict(l=234, p=160)
PORTE = dict(x0=81, x1=157, l=76)       # porte d'entrée au mur nord, paumelles à x 157, vantail ouvert à 90° contre x 153
DOUCHE = (5, 50, 78, 155)               # x0, y0, x1, y1
LAVABO = (82, 114, 165, 160)


def version(c):
    """Pièces et équipements de la version c : "d" (machine à droite, au sud) ou "g" (à gauche, au nord)."""
    t = PIECES + EQUIPEMENTS
    return t if c == "d" else [miroir(b) for b in t]


VERSIONS = {"d": "Machine à droite · côté lavabo", "g": "Machine à gauche · côté porte"}

# ------------------------------------------------------------------ matériaux, débit, quincaillerie
MATERIAUX = {
    "A": ("Panneau hydrofuge 19 mm", "MDF hydrofuge à peindre, ou mélaminé hydrofuge", T),
    "B": ("Contreplaqué bouleau 12 mm", "bacs, feuillures de la trappe", B),
    "C": ("Panneau hydrofuge 8 mm", "fonds", F),
    "D": ("Plan de travail 30 mm", "contreplaqué, compact ou massif, hydrofuge (38 : ne passe plus)", PT),
    "S": ("Contreplaqué 22 mm", "socle de la machine (CTBX, classe 3)", S),
    "E": ("Tasseaux et cornière", "sapin raboté traité 27 × 40, cornière alu 30 × 30 × 3", 0),
}
NOMS = {
    "A1": "Côté du caisson bas", "A2": "Dessous du caisson bas", "A3": "Tablette entre les bacs",
    "A4": "Traverse sous le plan", "A5": "Plinthe", "A6": "Façade de bac", "A7": "Côté du caisson haut",
    "A8": "Dessus et dessous du caisson haut", "A9": "Montant central haut", "A10": "Étagère serviettes",
    "A11": "Étagère pharmacie et produits divers", "A12": "Porte coulissante", "A13": "Fileur de plafond",
    "B1": "Côté de bac (trapèze)", "B2": "Devant de bac", "B3": "Fond de bac", "B4": "Dos incliné de bac",
    "B5": "Feuillure de la trappe", "C1": "Fond du caisson haut", "C2": "Fond du caisson bas",
    "D1": "Plan de travail", "D2": "Couvercle de trappe", "E1": "Tasseau du mur du fond", "E2": "Cornière alu",
    "S1": "Plateau du socle", "S2": "Longeron du socle", "S3": "Traverse du socle", "S4": "Rebord avant",
    "S5": "Rebord latéral",
}
USINAGES = {
    "A1": "Charnière piano du bac 1 posée sur le dessous, du bac 2 sur la tablette ; descend jusqu'au sol",
    "A3": "Chant avant visible entre les deux façades (le chanter)",
    "A6": "Poignée en haut, centrée ; vissée par l'intérieur sur le devant du bac",
    "A7": "Taquets Ø 5 pas 32 côté intérieur, à 6 cm du chant avant ; rails du kit coulissant",
    "A9": "En retrait de 6 derrière les rails ; taquets sur les deux faces",
    "B1": f"Trapèze : {BAC['d_bas'] * 10:.0f} en bas, {BAC['d_haut'] * 10:.0f} en haut, {BAC['h'] * 10:.0f} de haut",
    "B4": "Chants haut et bas coupés en biais",
    "D1": "Encoche 300 × 100 au fond, centrée sur la largeur ; joint silicone sur les murs",
    "D2": "Taillé dans la chute de l'encoche ; trou de doigt Ø 25",
    "S1": "Tapis antivibration 60 × 60 dessus",
    "E2": "Aile horizontale sous le plan, sur le mur côté machine",
}
QUINCAILLERIE = {
    "vis50": "vis à bois 4 × 50",
    "vis40": "vis à bois 4 × 40",
    "vis16": "vis à bois 4 × 16",
    "confirmat": "vis d'assemblage (confirmat) 7 × 50",
    "colle": "colle à bois D3",
    "equerre": "équerre d'assemblage 40 × 40",
    "cheville": "cheville + vis 6 × 60 (selon le mur)",
    "piano": "charnière piano 40 × 450 (inox)",
    "compas": "compas d'abattant à frein, arrêt à 30°",
    "poignee": "poignée de façade",
    "taquet": "taquet d'étagère Ø 5",
    "rails": "kit 2 portes coulissantes intérieures (rails haut et bas, portes de 19)",
    "led": "profil LED + alimentation",
    "silicone": "silicone sanitaire",
    "tapis": "tapis antivibration 60 × 60",
    "sac": "sac à linge amovible",
    "vérin": "patin réglable",
}

# Étapes de la notice : (titre, consigne courte, quincaillerie {code: quantité}). Les pièces de chaque étape sont celles
# dont etape == numéro.
ETAPES = [
    ("Avant de commencer", "Faire poser par le plombier le robinet d'arrêt encastré à 80 du sol, centré sur l'alcôve, et "
     "par l'électricien la prise de la machine (circuit 20 A spécialisé) et le bloc de prises de la niche à 126. "
     "Relever l'alcôve en trois hauteurs : garder la plus petite largeur.", {}),
    ("Socle", "Visser le cadre (longerons S2, traverses S3) à la colle, poser le plateau S1, puis les rebords S4 et S5.",
     {"vis50": 20, "colle": 1}),
    ("Caisson bas", "Assembler les côtés A1, le dessous A2 (sur la plinthe), la tablette A3 et les deux traverses A4.",
     {"confirmat": 16}),
    ("Fond et plinthe", "Visser le fond C2 au dos (il met le caisson d'équerre), puis la plinthe A5, en retrait de 3.",
     {"vis16": 14, "vis40": 4}),
    ("Pose dans l'alcôve", "Caisson bas contre le mur latéral côté bacs, socle de l'autre côté contre le caisson. "
     "Visser le caisson au mur, le socle au caisson et au mur. Tasseaux E1 au mur du fond et cornière E2 au mur côté "
     "machine, le dessus à 106,5 (au niveau du caisson).",
     {"equerre": 4, "cheville": 8, "vis40": 8}),
    ("Bacs", "Assembler chaque bac : côtés B1, fond B3, devant B2, dos incliné B4. Coller et visser.",
     {"vis40": 24, "colle": 1}),
    ("Façades et charnières", "Visser la façade A6 sur le devant du bac. Charnière piano entre le bas du devant et le "
     "bord avant de la case, deux compas de chaque côté : le bac doit s'arrêter à 30°. Poser les poignées et les sacs.",
     {"piano": 2, "compas": 4, "vis16": 40, "poignee": 2, "sac": 2}),
    ("Machine", "Poser le tapis sur le socle. À deux, monter la machine sur une cale de 20 placée devant, raccorder, "
     "la pousser sur le socle et régler les pieds : 1,5 sous le plan.", {"tapis": 1}),
    ("Plan de travail", "Découper l'encoche de la trappe, visser les feuillures B5 dessous, poser le plan D1 sur le "
     "caisson, les tasseaux et la cornière. Joint silicone contre les murs. Ajuster le couvercle D2.",
     {"vis16": 8, "silicone": 1}),
    ("Caisson haut", "Assembler les côtés A7, dessus et dessous A8, le montant A9 et le fond C1. Poser les rails du kit.",
     {"confirmat": 12, "vis16": 20, "rails": 1}),
    ("Pose du caisson haut", "Poser le caisson haut sur deux cales de 42,5 sur le plan (niche), le visser dans les "
     "trois murs.", {"cheville": 6}),
    ("Finitions", "Étagères A10 et A11, portes A12, fileur A13 ajusté au plafond, profil LED sous le caisson.",
     {"taquet": 24, "led": 1, "silicone": 1}),
]
POSE_HAUT = 10          # étape où le caisson haut monte sur ses cales (pas de nouvelle pièce)

CHANGEMENTS = [
    ("V3.0", "12/10/2026",
     "Nouvelle page générée depuis 3d/sdb/modele.py (plan, élévation, coupes, débit, modèle FreeCAD, notice de montage). "
     f"Machine surélevée de {SOCLE_H} sur un socle plein en contreplaqué 22 ; plan de travail remonté de 90 à "
     f"{Z_DESSUS:g} ; niche {Z_DESSUS:g} → {Z_HAUT} ; caisson haut {Z_HAUT} → {Z_HAUT1}. Paniers : les deux tiroirs "
     "coulissants à fente sont remplacés par deux bacs basculants superposés sur toute la largeur (plus de fente, de volet "
     "ni de goulotte)."),
    ("V2.2", "01/10/2026", "Mise en page : notes en fin de document (archive/sdb-meuble-v2.html)."),
    ("V2.1", "01/10/2026", "Fentes à linge dans les façades des tiroirs ; trappe du robinet centrée sur le meuble."),
    ("V2", "01/10/2026", "Base P1 « Plan de pliage », plan filant, deux tiroirs-paniers, trappe, hauts P 45 jusqu'au "
     "plafond, deux versions machine à droite / à gauche."),
    ("V1", "30/09/2026", "Trois propositions (archive/sdb-meuble-v1.html)."),
]
