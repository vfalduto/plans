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

VERSION = "V3.5"
H = 250                 # plafond (confirmé par le client)
X0, X1 = 167, 234       # alcôve : bord ouest (ouverture) et mur du fond (est)
Y0, Y1 = 0, 114         # alcôve : mur nord et mur sud
FACE = 168.1            # nu des façades (1 cm en retrait du bord de l'alcôve)

# V3.1 : tout le meuble en tablettes mélaminées de 18 (seul panneau de 12 à 18 vendu au Weldom Saint-Barnabé), plan
# de travail de 28 (format du magasin 1800 × 640). Les lettres A, B, C, S gardent les familles de pièces.
T, F, B, PT, S = 1.8, 1.8, 1.8, 2.8, 1.8   # épaisseurs : caissons, fonds, bacs, plan, socle


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
SOCLE_H = 10            # surélévation de la machine (V3 : 20 ; V3.5 : 10)
LL = dict(l=60, p=60, h=85, nom="lave-linge 60 × 60 × 85 (pieds réglés)")
JEU_PLAN = 1.5          # entre le dessus de la machine et le dessous du plan
Z_PLAN = SOCLE_H + LL["h"] + JEU_PLAN          # dessous du plan : 96,5
Z_DESSUS = Z_PLAN + PT                         # dessus du plan : 99,3
Z_HAUT1 = H - 2         # dessus du caisson haut ; fileur jusqu'au plafond
H_HAUT = 90             # hauteur du caisson haut (V3.4 : 96 → 90)
Z_HAUT = Z_HAUT1 - H_HAUT                      # dessous du caisson haut (niche de Z_DESSUS à Z_HAUT) : 158
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
SOCLE = dict(x0=FACE, x1=FACE + 60, y0=LLZ["y0"] + 0.3, y1=Y1 - J, rebord=1.5)   # rebord : baguette 18 × 15 sur chant
_s = SOCLE
_zs = SOCLE_H - S
P("socle", "socle_longeron_n", _s["x0"], _s["x1"], _s["y0"], _s["y0"] + S, 0, _zs, rep="S2", etape=1, groupe="socle")
P("socle", "socle_longeron_s", _s["x0"], _s["x1"], _s["y1"] - S, _s["y1"], 0, _zs, rep="S2", etape=1, groupe="socle")
for k, x in enumerate((_s["x0"], (_s["x0"] + _s["x1"] - S) / 2, _s["x1"] - S)):
    P("socle", f"socle_traverse_{k + 1}", x, x + S, _s["y0"] + S, _s["y1"] - S, 0, _zs, rep="S3", etape=1, groupe="socle")
P("socle", "socle_plateau", _s["x0"], _s["x1"], _s["y0"], _s["y1"], _zs, SOCLE_H, rep="S1", etape=1, groupe="socle")
P("rebord", "socle_rebord_avant", _s["x0"], _s["x0"] + S, _s["y0"] + S, _s["y1"] - S,
  SOCLE_H, SOCLE_H + _s["rebord"], rep="S4", etape=1, groupe="socle")
for nom, y in (("n", _s["y0"]), ("s", _s["y1"] - S)):
    P("rebord", f"socle_rebord_{nom}", _s["x0"], _s["x1"], y, y + S, SOCLE_H, SOCLE_H + _s["rebord"],
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
# tablette placée pour que les deux façades aient la même hauteur (la façade 1 couvre le dessous, la 2 la traverse)
_ztab = (Z_PLAN + PLINTHE - T) / 2
_case = _ztab - (PLINTHE + T)           # hauteur libre de la case du bas (celle du haut : 0,1 de plus)
P("caisson", "cb_tablette", _c["x0"], _xi, _yi0, _yi1, _ztab, _ztab + T, rep="A3", etape=2, groupe="caisson_bas")
P("caisson", "cb_traverse_av", _c["x0"], _c["x0"] + 10, _yi0, _yi1, _zt1, Z_PLAN, rep="A4", etape=2, groupe="caisson_bas")
P("caisson", "cb_traverse_ar", _xi - 10, _xi, _yi0, _yi1, _zt1, Z_PLAN, rep="A4", etape=2, groupe="caisson_bas")
P("fond", "cb_fond", _xi, _c["x1"], _c["y0"], _c["y1"], PLINTHE, Z_PLAN, rep="C2", etape=3, groupe="caisson_bas")
P("plinthe", "cb_plinthe", _c["x0"] + 3, _c["x0"] + 3 + T, _yi0, _yi1, 0, PLINTHE - 0.2, rep="A5", etape=3,
  groupe="caisson_bas")
CASES = [(PLINTHE + T, _ztab), (_ztab + T, _zt1)]   # (fond de case = axe des charnières, plafond de case)

# ------------------------------------------------------------------ ③ sacs basculants (V3.3)
# Plus de bac en bois : dans chaque case, un sac en tissu pend entre deux barres de bois (tasseau 20 × 40). La barre
# avant repose dans deux supports entaillés vissés au dos de la façade, la barre arrière dans deux supports vissés aux
# côtés du caisson. La façade pivote sur une charnière piano au bord avant de sa case ; deux compas l'arrêtent à ANGLE :
# la barre avant suit la façade, la bouche du sac s'ouvre. Pour vider, on soulève les deux barres hors de leurs
# entailles et on sort le sac par ses barres.
BAC = dict(angle=30, prof=30, jeu=0.3, barre=(2.0, 4.0), entaille=2.0, sous_plafond=3.0,
           sup=dict(x=4.5, z=6.0))          # barre : x × z ; support : bloc de 18 (x × z), entaille en U sur le dessus
_b = BAC
_bx, _bz = _b["barre"]
FACADES = []
SACS = []
for k, (zc, zp) in enumerate(CASES):
    g = f"bac{k + 1}"
    xa = _c["x0"]                                   # dos de la façade = bord avant de la case = axe
    zb1 = zp - _b["sous_plafond"]                   # dessus des barres : place pour les sortir des entailles
    zb0 = zb1 - _bz
    zs0, zs1 = zb0 - (_b["sup"]["z"] - _b["entaille"]), zb0 + _b["entaille"]   # supports : la barre entre de 2
    xf0 = xa + (_b["sup"]["x"] - _bx) / 2           # barre avant, centrée sur ses supports
    xr0 = xa + _b["prof"]                           # barre arrière
    # supports de la barre avant : au dos de la façade, aux deux bouts
    for nom, y in (("n", _yi0 + _b["jeu"]), ("s", _yi1 - _b["jeu"] - T)):
        P("support", f"bac{k + 1}_support_av_{nom}", xa, xa + _b["sup"]["x"], y, y + T, zs0, zs1, rep="B1", etape=6,
          groupe=g)
    # supports de la barre arrière : contre les côtés du caisson
    for nom, y in (("n", _yi0), ("s", _yi1 - T)):
        P("support", f"bac{k + 1}_support_ar_{nom}", xr0 - (_b["sup"]["x"] - _bx) / 2,
          xr0 + (_b["sup"]["x"] + _bx) / 2, y, y + T, zs0, zs1, rep="B1", etape=5, groupe=g)
    for nom, x in (("av", xf0), ("ar", xr0)):
        P("barre", f"bac{k + 1}_barre_{nom}", x, x + _bx, _yi0 + _b["jeu"], _yi1 - _b["jeu"], zb0, zb1, rep="E4",
          etape=5, groupe=g)
    # sac (pas à découper) : pend entre les deux barres, jusqu'à 1 au-dessus du fond de la case
    ys0, ys1 = _yi0 + T + 0.5, _yi1 - T - 0.5
    sac = [(xf0, zb0 + 1), (xr0 + _bx, zb0 + 1), (xr0 + _bx - 1, zc + 1), (xf0 + 1, zc + 1)]
    SACS.append(Profil("sac", f"bac{k + 1}_sac", sac, ys0, ys1, etape=5, groupe=g))
    # façade en applique : du bas de la case (bac 1 : couvre le dessous) au dessous de la tablette (bac 2 : de la tablette
    # au plan) ; jeu de 0,3 autour
    zf0 = (PLINTHE + 0.3) if k == 0 else (_ztab + T + 0.05)
    zf1 = (_ztab - 0.05) if k == 0 else (Z_PLAN - 0.3)
    FACADES.append((zf0, zf1))
    P("facade", f"bac{k + 1}_facade", FACE, FACE + T, _c["y0"] + 0.15, _c["y1"] - 0.15, zf0, zf1, rep="A6", etape=6,
      groupe=g, etiq=f"Sac {k + 1}")
    BAC[f"axe{k + 1}"] = (xa, zc)
    BAC[f"plafond{k + 1}"] = zp
    BAC[f"barres{k + 1}"] = (xf0, xr0, zb0, zb1)
CASE_H = _case
assert abs((FACADES[0][1] - FACADES[0][0]) - (FACADES[1][1] - FACADES[1][0])) < 1e-9, FACADES   # façades identiques
assert BAC["prof"] + _bx < _xi - _c["x0"] - 1, "barre arrière dans le caisson"


def bascule(x, z, axe, angle):
    """Position d'un point (x, z) de la façade une fois basculée de angle degrés vers la pièce autour de axe = (xa, za)."""
    a = math.radians(angle)
    u, w = axe[0] - x, z - axe[1]                     # u : vers la pièce (ouest), w : vers le haut
    u2, w2 = u * math.cos(a) + w * math.sin(a), -u * math.sin(a) + w * math.cos(a)
    return axe[0] - u2, axe[1] + w2


_ax = BAC["axe1"]
_xf0, _xr0, _zb0, _zb1 = BAC["barres1"]
_haut_facade = bascule(FACE, FACADES[0][1], _ax, _b["angle"])
_barre_ouverte = bascule(_xf0, _zb1, _ax, _b["angle"])          # coin arrière haut de la barre avant, façade ouverte
# le bas de la façade du bac 2 descend en basculant : il doit rester au-dessus de la façade du bac 1
_bas2 = bascule(FACE, FACADES[1][0], BAC["axe2"], _b["angle"])
assert _bas2[1] > FACADES[0][1] + 0.3, (_bas2, FACADES[0])
# la barre avant ne touche pas le plafond de la case pendant la bascule (elle s'en éloigne)
assert _barre_ouverte[1] < BAC["plafond1"], _barre_ouverte
BAC["avancee"] = FACE - _haut_facade[0]          # le haut de la façade avance de tant dans la pièce
BAC["bouche_fermee"] = _xr0 - (_xf0 + _bx)       # entre les barres, façade fermée
BAC["bouche"] = _xr0 - _barre_ouverte[0]         # entre les barres, façade ouverte
BAC["fente"] = _c["x0"] - _haut_facade[0] + 0  # passage entre le haut de la façade ouverte et le bord de la case
BAC["largeur_sac"] = _yi1 - _yi0 - 2 * T - 1
BAC["h_sac"] = _zb0 + 1 - (CASES[0][0] + 1)
# tissu : bouche à façade ouverte (plus 4 de jeu) ; fourreaux de 14 de tour (barre 20 × 40)
BAC["sac"] = (f"sac en tissu {BAC['largeur_sac']:.0f} de large, {BAC['h_sac']:.0f} de haut, "
              f"{BAC['bouche'] + 4:.0f} de bouche, deux fourreaux de 14 de tour pour les barres")
VOLUME_BAC = BAC["largeur_sac"] * BAC["h_sac"] * (BAC["bouche_fermee"] + _bx) / 1000

# ------------------------------------------------------------------ ④ plan de travail filant (30) et supports
# Tasseaux contre le mur du fond, cornière alu sur le mur latéral côté machine, le caisson bas de l'autre côté.
# Trappe 30 × 10 au fond du plan, centrée sur le meuble : on atteint le robinet d'arrêt derrière la machine.
PLAN_P = 64             # profondeur du plan de travail du commerce (1800 × 640 × 28)
PLAN_X1 = FACE + PLAN_P                        # 1,9 de jeu contre le mur du fond (joint silicone)
FEUIL = 0.3             # feuillures de la trappe : plats alu tirés de la chute de cornière (passent dans le jeu de 1,5)
TAS = dict(l=4.4, h=2.7)                       # tasseau sapin 44 × 27 posé à plat : 2,5 sous le plan
TRAPPE = dict(x0=PLAN_X1 - 10, x1=PLAN_X1, y0=CENTRE - 15, y1=CENTRE + 15)
ROBINET = dict(y=CENTRE, z=80)
P("tasseau", "tasseau_fond_n", X1 - TAS["l"], X1, Y0 + J, TRAPPE["y0"] - 4, Z_PLAN - TAS["h"], Z_PLAN, rep="E1", etape=4,
  groupe="supports")
P("tasseau", "tasseau_fond_s", X1 - TAS["l"], X1, TRAPPE["y1"] + 4, Y1 - J, Z_PLAN - TAS["h"], Z_PLAN, rep="E1", etape=4,
  groupe="supports")
P("corniere", "corniere_aile_v", FACE + 2, X1 - TAS["l"], Y1 - 0.3, Y1, Z_PLAN - 3, Z_PLAN, rep="E2", etape=4, groupe="supports")
P("corniere", "corniere_aile_h", FACE + 2, X1 - TAS["l"], Y1 - 3, Y1, Z_PLAN - 0.3, Z_PLAN, rep="E2", etape=4, groupe="supports")
P("plan", "plan_travail", FACE, PLAN_X1, Y0 + J, Y1 - J, Z_PLAN, Z_DESSUS, rep="D1", etape=8, groupe="plan",
  miroir=False, encoche=(TRAPPE["x0"], TRAPPE["x1"], TRAPPE["y0"], TRAPPE["y1"]))
P("trappe", "trappe_couvercle", TRAPPE["x0"] + 0.2, TRAPPE["x1"] - 0.2, TRAPPE["y0"] + 0.2, TRAPPE["y1"] - 0.2,
  Z_PLAN, Z_DESSUS, rep="D2", etape=8, groupe="plan", miroir=False)
for nom, y in (("n", TRAPPE["y0"] - 2), ("s", TRAPPE["y1"] - 1)):    # plats de 30 : 1 sous le couvercle, 2 sous le plan
    P("corniere", f"feuillure_{nom}", TRAPPE["x0"], TRAPPE["x1"], y, y + 3, Z_PLAN - FEUIL, Z_PLAN, rep="E3", etape=8,
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
# fond en deux moitiés (une tablette fait 600 de large), jointes derrière le montant central
H_("fond", "ch_fond_n", _hx, _h["x1"], _h["y0"], CENTRE - 0.1, _h["z0"], _h["z1"], rep="C1", etape=9)
H_("fond", "ch_fond_s", _hx, _h["x1"], CENTRE + 0.1, _h["y1"], _h["z0"], _h["z1"], rep="C1", etape=9)
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
    t = PIECES + SACS + EQUIPEMENTS
    return t if c == "d" else [miroir(b) for b in t]


VERSIONS = {"d": "Machine à droite · côté lavabo", "g": "Machine à gauche · côté porte"}

# ------------------------------------------------------------------ matériaux, débit, quincaillerie
MATERIAUX = {
    "A": ("Tablette mélaminée blanche 18 mm", "caissons, façades, portes, étagères (aggloméré non hydrofuge : chants coupés à "
          "recouvrir de chant thermocollant blanc)", T),
    "B": ("Tablette mélaminée blanche 18 mm", "bacs basculants", B),
    "C": ("Tablette mélaminée blanche 18 mm", "fonds (celui du caisson haut en deux moitiés)", F),
    "D": ("Plan de travail stratifié 28 mm", "CPL blanc bords droits 1800 × 640 ; le couvercle de trappe vient de l'encoche", PT),
    "S": ("Tablette mélaminée blanche 18 mm", "socle de la machine, rebords en baguettes refendues", S),
    "E": ("Tasseaux et cornière", "sapin raboté 44 × 27 posé à plat, cornière alu 29,5 × 29,5 (1 m : support du "
          "plan et feuillures de la trappe)", 0),
}
# Panneaux du commerce pour le calepinage, par matériau (Weldom Marseille Saint-Barnabé, relevé du 12/10/2026, prix TTC,
# stock lu sur la fiche produit). Les tablettes ont leurs deux chants longs finis : pas de délignage.
TABLETTES_18 = [
    dict(L=2500, l=600, prix=16.50, stock=25, ref="9134941", nom="Tablette mélaminé 250 × 60 × 18 blanc"),
    dict(L=2500, l=500, prix=13.59, stock=50, ref="9134940", nom="Tablette mélaminé 250 × 50 × 18 blanc"),
    dict(L=2500, l=400, prix=12.50, stock=30, ref="9134939", nom="Tablette mélaminé 250 × 40 × 18 blanc"),
    dict(L=2500, l=300, prix=11.50, stock=37, ref="9134938", nom="Tablette mélaminé 250 × 30 × 18 blanc"),
]
PANNEAUX = {
    "M18": TABLETTES_18,
    "D": [dict(L=1800, l=640, prix=36.50, stock=23, ref="9121132", nom="Plan de travail 1800 × 640 × 28 CPL blanc bords droits")],
}
STOCK = {"A": "M18", "B": "M18", "C": "M18", "S": "M18", "D": "D"}   # matériau → panneau acheté
FIL = ()                # repères à ne pas tourner (aucun : mélaminé uni)
MAGASIN = dict(nom="Weldom Marseille Saint-Barnabé", adresse="90 rue François Scaramelli, 13012 Marseille",
               tel="04 91 49 27 27", url="https://www.weldom.fr/m/weldom-marseille-saint-barnabe", releve="12/10/2026")
NOMS = {
    "A1": "Côté du caisson bas", "A2": "Dessous du caisson bas", "A3": "Tablette entre les sacs",
    "A4": "Traverse sous le plan", "A5": "Plinthe", "A6": "Façade basculante", "A7": "Côté du caisson haut",
    "A8": "Dessus et dessous du caisson haut", "A9": "Montant central haut", "A10": "Étagère serviettes",
    "A11": "Étagère pharmacie et produits divers", "A12": "Porte coulissante", "A13": "Fileur de plafond",
    "B1": "Support de barre", "E4": "Barre du sac",
    "E3": "Feuillure de la trappe (plat alu)", "C1": "Fond du caisson haut", "C2": "Fond du caisson bas",
    "D1": "Plan de travail", "D2": "Couvercle de trappe", "E1": "Tasseau du mur du fond", "E2": "Cornière alu",
    "S1": "Plateau du socle", "S2": "Longeron du socle", "S3": "Traverse du socle", "S4": "Rebord avant",
    "S5": "Rebord latéral",
}
USINAGES = {
    "A1": "Charnière piano de la façade 1 sur le dessous, de la façade 2 sur la tablette ; descend jusqu'au sol",
    "A3": "Chant avant visible entre les deux façades (le chanter)",
    "A6": "Poignée en haut, centrée ; deux supports de barre B1 vissés au dos, en haut, aux deux bouts",
    "A7": "Taquets Ø 5 pas 32 côté intérieur, à 6 cm du chant avant ; rails du kit coulissant",
    "A9": "En retrait de 6 derrière les rails ; taquets sur les deux faces",
    "B1": f"Bloc de chute ; entaille en U de {(BAC['barre'][0] + 0.1) * 10:.0f} de large et {BAC['entaille'] * 10:.0f} "
          "de profond sur le dessus, où la barre se pose",
    "E4": "Tasseau raboté 20 × 40, arêtes arrondies ; glissé dans le fourreau du sac",
    "D1": "Recoupé de 1800 à 1134 ; encoche 300 × 100 au fond, centrée sur la largeur ; joint silicone sur les murs",
    "D2": "Taillé dans la chute de l'encoche ; trou de doigt Ø 25",
    "S1": "Tapis antivibration 60 × 60 dessus",
    "S4": "Baguette refendue dans une chute, posée sur chant (18 × 15)",
    "S5": "Baguette refendue dans une chute, posée sur chant (18 × 15)",
    "C1": "Deux moitiés, jointes derrière le montant central A9",
    "E2": "Aile horizontale sous le plan, sur le mur côté machine",
    "E3": "Chute de la cornière E2, une aile sciée : plat de 3 qui dépasse de 1 sous le couvercle",
}
QUINCAILLERIE = {
    "vis50": "vis à bois 4 × 50",
    "vis40": "vis à bois 4 × 40",
    "vis16": "vis à bois 4 × 16",
    "confirmat": "vis d'assemblage Direkta Ø 6,3 × 50 (à la place du confirmat 7 × 50)",
    "colle": "colle à bois D3",
    "equerre": "équerre d'assemblage 60",
    "cheville": "cheville + vis 6 × 60 (mur carrelé : percer au foret carrelage, dans les joints si possible)",
    "piano": "charnière piano 600 × 32, recoupée à 490",
    "compas": "compas d'abattant Hettich L 250, réglé à 30°",
    "vis30": "vis à bois 4 × 30",
    "poignee": "poignée de façade",
    "taquet": "taquet d'étagère Ø 5",
    "rails": "kit 2 portes coulissantes intérieures (rails haut et bas, portes de 18)",
    "led": "ruban LED 1,5 m 4000 K + profil alu",
    "silicone": "silicone sanitaire",
    "tapis": "tapis antivibration 60 × 60",
    "sac": BAC["sac"],
    "vérin": "patin réglable",
    "chant": "chant thermocollant blanc 20 mm (rouleau)",
}
# Achats au Weldom Saint-Barnabé (relevé du 12/10/2026) : code de quincaillerie ou de bois → (désignation Weldom, prix
# unitaire, quantité achetée, stock, réf.) ; None : absent du catalogue du magasin, à acheter ailleurs.
WELDOM = {
    "E1": ("Tasseau sapin nord raboté 240 × 4,4 × 2,7", 5.99, 1, 11, "9000477"),
    "E2": ("Cornière égale alu brut 1 m 29,5 × 29,5", 8.50, 1, 6, "9143660"),
    "E4": ("Tasseau raboté sapin 1er choix 20 × 40, 1 m", 3.65, 2, 20, "5584231"),
    "confirmat": ("Lot de 16 vis Direkta Hettich 50 mm", 5.20, 2, 5, "1098014"),
    "equerre": ("Équerre d'assemblage Hettich 60 mm", 2.19, 4, None, "70207935"),
    "piano": ("Charnière piano inox Hettich 600 × 32", 8.35, 2, 6, "5575916"),
    "compas": ("Lot de 2 compas d'abattant Hettich L 250", 6.20, 2, 3, "9155214"),
    "taquet": ("Lot de 20 taquets acier gris Ø 5", 5.35, 2, 4, "5567370"),
    "tapis": ("Plaque anti-vibrations Noma Rub 60 × 60 × 1", 13.50, 1, 30, "9161504"),
    "led": ("Kit ruban LED 1,5 m 4000 K (profil alu : absent)", 7.50, 1, 4, "87978094"),
    "poignee": ("Lot de 6 poignées SOA plastique blanc entraxe 96", 3.99, 1, None, "90496580"),
    "rails": None,
    "sac": None,
    "chant": None,
}
# Étapes de la notice : (titre, consigne courte, quincaillerie {code: quantité}). Les pièces de chaque étape sont celles
# dont etape == numéro.
ETAPES = [
    ("Avant de commencer", "Faire poser par le plombier le robinet d'arrêt encastré à 80 du sol, centré sur l'alcôve, et "
     "par l'électricien la prise de la machine (circuit 20 A spécialisé) et le bloc de prises de la niche à 126. "
     "Relever l'alcôve en trois hauteurs : garder la plus petite largeur.", {}),
    ("Socle", "Au fer à repasser, plaquer le chant blanc sur tous les chants coupés qui resteront visibles (toutes les "
     "pièces). Visser le cadre (longerons S2, traverses S3) à la colle, poser le plateau S1, puis les rebords S4 et S5.",
     {"vis50": 20, "colle": 1, "chant": 1}),
    ("Caisson bas", "Assembler les côtés A1, le dessous A2 (sur la plinthe), la tablette A3 et les deux traverses A4.",
     {"confirmat": 16}),
    ("Fond et plinthe", "Visser le fond C2 au dos (il met le caisson d'équerre), puis la plinthe A5, en retrait de 3.",
     {"vis16": 14, "vis40": 4}),
    ("Pose dans l'alcôve", "Caisson bas contre le mur latéral côté bacs, socle de l'autre côté contre le caisson. "
     "Visser le caisson au mur, le socle au caisson et au mur. Tasseaux E1 au mur du fond et cornière E2 au mur côté "
     "machine, le dessus à " + f"{Z_PLAN:g}".replace(".", ",") + " (au niveau du caisson).",
     {"equerre": 4, "cheville": 8, "vis40": 8}),
    ("Barres et sacs", "Dans chaque case, visser deux supports B1 contre les côtés, à " + f"{BAC['prof']}" + " du bord "
     "avant, entaille en haut. Glisser les barres E4 dans les fourreaux des sacs ; poser la barre arrière dans ses "
     "entailles.", {"vis40": 8, "sac": 2}),
    ("Façades et charnières", "Visser deux supports B1 au dos de chaque façade A6, en haut, aux deux bouts. Charnière "
     "piano entre le bas de la façade et le bord avant de la case, deux compas de chaque côté : la façade doit s'arrêter "
     "à 30°. Poser la barre avant du sac dans ses entailles. Poser les poignées.",
     {"piano": 2, "compas": 4, "vis16": 40, "vis30": 8, "poignee": 2}),
    ("Machine", "Poser le tapis sur le socle. À deux, monter la machine sur une cale de " + f"{SOCLE_H}" + " placée devant, "
     "raccorder, "
     "la pousser sur le socle et régler les pieds : 1,5 sous le plan.", {"tapis": 1}),
    ("Plan de travail", "Découper l'encoche de la trappe, visser les feuillures E3 dessous, poser le plan D1 sur le "
     "caisson, les tasseaux et la cornière. Joint silicone contre les murs. Ajuster le couvercle D2.",
     {"vis16": 8, "silicone": 1}),
    ("Caisson haut", "Assembler les côtés A7, dessus et dessous A8, le montant A9 et le fond C1. Poser les rails du kit.",
     {"confirmat": 12, "vis16": 20, "rails": 1}),
    ("Pose du caisson haut", "Poser le caisson haut sur deux cales de " + f"{Z_HAUT - Z_DESSUS:.1f}".replace(".", ",") + " sur le plan "
     "(niche), le visser dans les trois murs.", {"cheville": 6}),
    ("Finitions", "Étagères A10 et A11, portes A12, fileur A13 ajusté au plafond, profil LED sous le caisson.",
     {"taquet": 24, "led": 1, "silicone": 1}),
]
POSE_HAUT = 10          # étape où le caisson haut monte sur ses cales (pas de nouvelle pièce)

CHANGEMENTS = [
    ("V3.5", "12/10/2026",
     f"Socle de la machine abaissé de 20 à {SOCLE_H} : plan de travail à " + f"{Z_DESSUS:.1f}".replace(".", ",") +
     " (au lieu de 109,3), niche de " + f"{Z_HAUT - Z_DESSUS:.1f}".replace(".", ",") + ". Tablette du caisson bas "
     "placée pour que les deux façades des sacs aient exactement la même hauteur (" +
     f"{FACADES[0][1] - FACADES[0][0]:.1f}".replace(".", ",") + ")."),
    ("V3.4", "12/10/2026",
     f"Placards du haut réduits à {H_HAUT} de haut (au lieu de 96) : toujours jusqu'au plafond, le dessous remonte à "
     f"{Z_HAUT} ; la niche passe à " + f"{Z_HAUT - Z_DESSUS:.1f}".replace(".", ",") + " de haut."),
    ("V3.3", "12/10/2026",
     "Les bacs en bois sont remplacés par des sacs en tissu : dans chaque case, un sac pend entre deux barres de bois "
     "(tasseau 20 × 40), l'une posée dans des supports au dos de la façade, l'autre dans des supports aux côtés du "
     f"caisson. La façade bascule toujours à {BAC['angle']}° et ouvre la bouche du sac ; pour vider, on prend les deux "
     "barres et on sort le sac. Murs carrelés : perçage au foret carrelage (notice, à vérifier)."),
    ("V3.2", "12/10/2026", "Sommaire : chaque section a une ancre lisible (#plan, #debit, #achats…) ; un clic met l'adresse à "
     "jour, et une adresse avec ancre ouvre la page sur la section (plans et notice)."),
    ("V3.1", "12/10/2026",
     "Bois revu pour des panneaux du commerce, croisé avec le stock du Weldom Marseille Saint-Barnabé : pas de 12 ni de "
     "contreplaqué au magasin, donc tout le meuble (caissons, bacs, fonds, socle) en tablettes mélaminées blanches de 18 "
     "(2500 × 600 / 500 / 400 / 300) au lieu de 19, 12, 8 et 22 ; plan de travail 1800 × 640 × 28 au lieu de 30 "
     f"(dessus à {Z_DESSUS:g}, 1,9 de jeu au fond) ; tasseaux 44 × 27 à plat ; fond du caisson haut en deux moitiés. "
     "Nouvelle section Achats : calepinage des tablettes et liste de courses avec prix et stock."),
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
