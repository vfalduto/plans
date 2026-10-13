# Meuble linge de la salle de bain V3 : source unique.
#
# Ce fichier ne contient que des données : plan.py (page HTML : plan, élévation, coupes, débit), montage.py (notice de
# montage) et cad.py (modèle FreeCAD) les lisent. Toute modification se fait ici, jamais dans le HTML.
#
# Cotes en cm : x vers l'est depuis le mur ouest de la salle de bain, y vers le sud depuis le mur nord, z depuis le sol.
# Le meuble est dans l'alcôve est (x 167 → 234, y 0 → 114). Il est décrit pièce par pièce, dans la version « machine à
# droite » (côté lavabo, au sud), la seule retenue depuis la V3.8 (la version miroir, machine à gauche, est abandonnée ;
# miroir() reste pour mémoire).
#
# Chaque pièce : Bloc(role, nom, x0, x1, y0, y1, z0, z1, rep=…, etape=…) ou Profil (contour dans le plan x-z, extrudé en
# y) pour les côtés et le dos incliné des bacs basculants. rep = repère de la liste de débit, etape = étape de montage.

import math
from dataclasses import dataclass, field, replace

VERSION = "V5.23"
H = 250                 # plafond (confirmé par le client)
X0, X1 = 167, 234       # alcôve : bord ouest (ouverture) et mur du fond (est)
Y0, Y1 = 0, 115         # alcôve : mur nord et mur sud (V5.6 : relevé client, fond 115 ; avant : 114)
ALCOVE = dict(nord=62, sud=68)   # profondeur des murs de retour de l'alcôve depuis le mur du fond (relevé client)
X0 = X1 - ALCOVE["sud"]          # bout du mur sud (côté lavabo) : 166 (avant : 167)
PROF = 60               # V5.10 : profondeur totale du meuble bas, plan compris, collé au mur du fond (client)
FACE = X1 - PROF        # nu des façades et du plan : 174 (avant : 168,1, meuble de 65,9)

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
    entailles: tuple = ()  # rectangles (x0, x1, y0, y1) entaillés sur toute l'épaisseur (tablette autour des montants)

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


# ------------------------------------------------------------------ ossature en bois massif
# V4 : ossature en tasseaux (V4.2 : sapin autoclave classe III 36 × 36 ; V5.3 : sapin brut non traité 38 × 38, lots de
# 6 tasseaux de 2 m, peint ou verni, relevé Weldom du 13/10/2026). V5 (contre-analyse, coûts et simplicité) : plus de socle, la machine est
# posée au sol ; trois échelles debout sur le carrelage, le plan posé sur leur tête ; entre les deux échelles du caisson,
# un seul bac basculant (porte + fond en L, côtés, cloison, dos) qui reçoit deux sacs souples côte à côte.
DG = (3.8, 3.8)         # tasseau : épaisseur × largeur (V5.3 : sapin brut 38 × 38 ; avant : autoclave 36 × 36)
DE, DL = DG

# ------------------------------------------------------------------ hauteurs
SOCLE_H = 0             # V5 : plus de socle, la machine est au sol (V4.4 : 5,4)
LL = dict(l=59.5, p=53, h=85, nom="lave-linge 59,5 × 53 × 85 (relevé client)")
JEU_PLAN = 0.5          # entre le dessus de la machine et le dessous du plan (elle l'effleure sans toucher)
Z_PLAN = SOCLE_H + LL["h"] + JEU_PLAN          # dessous du plan, posé sur la tête des échelles : 85,5
Z_CADRE = Z_PLAN                               # tête des échelles
Z_DESSUS = Z_PLAN + PT                         # dessus du plan : 88,3
Z_HAUT1 = H - 2         # dessus du caisson haut ; fileur jusqu'au plafond
H_HAUT = 90             # hauteur du caisson haut (V3.4 : 96 → 90)
Z_HAUT = Z_HAUT1 - H_HAUT                      # dessous du caisson haut (niche de Z_DESSUS à Z_HAUT) : 158

# ------------------------------------------------------------------ plan de l'alcôve (machine à droite)
J = 0.3                 # jeu contre un mur
LL_ZONE = LL["l"] + 1.2  # entre l'échelle du caisson et celle du mur sud : machine + 0,6 de chaque côté
YM0, YM1 = Y0 + J, Y1 - J                      # emprise du meuble bas : 0,3 → 113,7
XO0 = FACE + T          # nu avant de l'ossature, derrière la porte : 169,9
JEU_LL = 5              # entre le dos de la machine et le mur du fond (coudes des tuyaux)
XO1 = X1 - JEU_LL       # nu arrière de l'ossature, aligné sur le dos de la machine : 229 (V5.12 ; avant : 218)
# trois échelles : contre le mur nord, entre le bac et la machine, contre le mur sud
ECH = dict(n=YM0, c=YM1 - DE - LL_ZONE - DE, s=YM1 - DE)
CB = dict(y0=YM0, y1=ECH["c"] + DE, x0=XO0, x1=XO1)          # caisson du bac : 0,3 → 48,9
LLZ = dict(y0=CB["y1"], y1=ECH["s"])                         # zone de la machine : 61,2
CENTRE = (Y0 + Y1) / 2


def cm_(v):
    return f"{round(v, 1):g}".replace(".", ",")


PIECES = []


def P(*a, **k):
    b = Bloc(*a, **k)
    PIECES.append(b)
    return b


# ------------------------------------------------------------------ perçages
# Chaque vissage est décrit par visser(a, b, vis) : vis à travers la pièce a dans la pièce b, qui se touchent. Les trous
# se placent sur la face de a opposée à b : en bout de pièce, n trous répartis sur la section ; le long d'une pièce, un
# trou à BORD de chaque bout puis au plus tous les PAS. La notice les dessine et les liste étape par étape.
TROUS = []
BORD, PAS = 4, 25
# vis → (passage dans la pièce traversée, avant-trou dans la pièce reçue) ; Ø en mm (usage courant, de mémoire)
PERCAGE = {
    "vis60": ("Ø 5 traversant + fraisure", "Ø 3, 30 de profondeur"),
    "vis40": ("Ø 4 traversant + fraisure", "Ø 2,5, 20 de profondeur"),
    "vis40l": ("lamage Ø 10, 10 de profondeur, puis Ø 4 traversant",
               "Ø 3, 12 de profondeur dans le plan (ruban sur le foret) : la vis y entre de 14"),
    "vis16l": ("lamage Ø 10, 8 de profondeur, puis Ø 4 traversant",
               "Ø 2,5, 8 de profondeur dans la porte (ruban sur le foret) : la vis n'en traverse pas plus de 6"),
    "vis16": ("—", "Ø 2,5, 10 de profondeur (ruban sur le foret)"),
    "confirmat": ("Ø 5 traversant + fraisure", "Ø 4, 50 de profondeur dans le chant (à vérifier sur le sachet Direkta)"),
    "cuvette": ("Forstner Ø 35, 12 de profondeur (butée)", "—"),
    "depart": ("Ø 10 traversant, dans l'angle, à l'intérieur du trait", "—"),
    "doigt": ("mèche plate Ø 20 traversante (finir par l'autre face)", "—"),
    "prise": ("mèche plate Ø 25 : percer jusqu'à ce que la pointe sorte, finir par l'autre face", "—"),
    "cheville": ("Ø 6 traversant", "dans le mur nu (au-dessus du carrelage), foret et cheville selon le mur, 50 de profondeur"),
    "insert": ("Ø 10, 25 de profondeur, dans le bout du montant ; vernir le trou, visser l'insert à fleur (clé six pans)", "—"),
    "butee": ("Ø 5, 35 de profondeur dans la face intérieure de l'écharpe (ruban sur le foret)", "—"),
}
VIS = {"vis60": "vis 5 × 60", "vis40": "vis 4 × 40", "vis40l": "vis 4 × 40", "vis16l": "vis 4 × 16",
       "vis16": "vis 4 × 16", "confirmat": "vis Direkta 6,3 × 50", "cuvette": "charnière invisible",
       "prise": "trou de prise (pas de poignée)", "butee": "tire-fond 8 × 60 laissé dépasser de 25 (butée)", "insert": "insert M8 + vérin", "depart": "départ de scie sauteuse", "doigt": "trou de doigt", "cheville": "cheville + vis 6 × 70"}


def _bornes(p):
    return [(p.x0, p.x1), (p.y0, p.y1), (p.z0, p.z1)]


def trou(etape, a, b, vis, c, n, pos=""):
    TROUS.append(dict(etape=etape, a=a.nom, b=b.nom if b else "", ra=a.rep, rb=b.rep if b else "", x=c[0], y=c[1],
                      z=c[2], n=n, vis=vis, pos=pos))


def visser(a, b, vis, etape, n=2, us=None):
    """Vis à travers a dans b ; us : positions imposées le long de l'assemblage (sinon calculées)."""
    A, Bb = _bornes(a), _bornes(b)
    for k in range(3):
        if abs(A[k][1] - Bb[k][0]) < 1e-6:
            s, w = -1, A[k][0]
            break
        if abs(A[k][0] - Bb[k][1]) < 1e-6:
            s, w = 1, A[k][1]
            break
    else:
        raise ValueError(f"{a.nom} et {b.nom} ne se touchent pas")
    autres = [i for i in range(3) if i != k]
    ov = {i: (max(A[i][0], Bb[i][0]), min(A[i][1], Bb[i][1])) for i in autres}
    assert all(o[1] > o[0] for o in ov.values()), (a.nom, b.nom, ov)
    lg = max(autres, key=lambda i: ov[i][1] - ov[i][0])
    tr = autres[0] if autres[1] == lg else autres[1]
    a0, a1 = ov[lg]
    long_ = a1 - a0
    if us is None and long_ <= 2 * BORD + 1:      # en bout : n trous répartis sur la section
        us = [a0 + long_ * (j + 1) / (n + 1) for j in range(n)]
        bord = ("du bord avant", "du bord nord", "du dessous")[lg]
        pos = f"{n} trous à " + " et ".join(f"{u - a0:.1f}".replace(".", ",") for u in us) + f" {bord}, dans l'axe"
    else:
        if us is None:
            m = max(n, math.ceil((long_ - 2 * BORD) / PAS) + 1)
            us = [a0 + BORD + (long_ - 2 * BORD) * j / (m - 1) for j in range(m)]
        ecart = max((v - u for u, v in zip(us, us[1:])), default=0)
        pos = (f"{len(us)} trous, à {us[0] - a0:.0f} des bouts, tous les ≈ {ecart:.0f}, dans l'axe".replace(".", ",")
               if len(us) > 2 else f"{len(us)} trous à {us[0] - a0:.1f} des bouts, dans l'axe".replace(".", ","))
    t = sum(ov[tr]) / 2
    for u in us:
        c = [0, 0, 0]
        c[k], c[lg], c[tr] = w, u, t
        nrm = [0, 0, 0]
        nrm[k] = s
        trou(etape, a, b, vis, c, tuple(nrm), pos)


# ------------------------------------------------------------------ ① échelles (tasseaux)
# Trois cadres verticaux debout sur le carrelage (V5 : plus de socle) : deux montants, une lisse basse au sol et une
# lisse haute sous le plan, vissées en bout à travers les montants (sans colle). Dans les deux échelles du bac, une lisse
# de barre G8 sous la lisse haute porte les supports de la barre arrière des sacs.
# V5.15 : l'ossature repose sur des pieds en plastique sous les six montants (l'eau au sol ne touche pas le bois) ; elle
# commence à Z0 au lieu du sol, le dessus du plan ne bouge pas (montants raccourcis d'autant)
PIED = dict(h=2.0, semelle=2.4)   # vérin M8 Hettich (tige 30, semelle plastique ≈ 24, estimée sur photo) dans un insert M8
Z0 = PIED["h"]
ECHELLES = {}
for nom, y in ECH.items():
    mav = P("bois", f"montant_av_{nom}", XO0, XO0 + DL, y, y + DE, Z0, Z_CADRE, rep="G3", etape=1, groupe="ossature")
    mar = P("bois", f"montant_ar_{nom}", XO1 - DL, XO1, y, y + DE, Z0, Z_CADRE, rep="G3", etape=1, groupe="ossature")
    lis = [P("bois", f"lisse_{k}_{nom}", XO0 + DL, XO1 - DL, y, y + DE, z - DL, z, rep="G4", etape=1,
             groupe="ossature") for k, z in (("basse", Z0 + DL), ("haute", Z_CADRE))]
    if nom in ("n", "c"):
        lis.append(P("bois", f"lisse_barre_{nom}", XO0 + DL, XO1 - DL, y, y + DE, Z_CADRE - 2 * DL, Z_CADRE - DL,
                     rep="G8", etape=1, groupe="ossature"))
    for l_ in lis:
        visser(mav, l_, "vis60", 1)
        visser(mar, l_, "vis60", 1)
    for m_ in (mav, mar):           # vérin sous chaque montant (pas à découper)
        xc, yc, sd = (m_.x0 + m_.x1) / 2, (m_.y0 + m_.y1) / 2, PIED["semelle"] / 2
        P("pied", f"verin_{m_.nom}", xc - sd, xc + sd, yc - sd, yc + sd, 0, Z0, etape=1, groupe="ossature")
        trou(1, m_, None, "insert", (xc, yc, Z0), (0, 0, -1), "1 trou Ø 10 au centre du bout du pied, 25 de profondeur")
    ECHELLES[nom] = dict(av=mav, ar=mar, basse=lis[0], haute=lis[1], barre=lis[2] if len(lis) > 2 else None)
# V5.15 : une écharpe dans chaque échelle (tasseaux en rab des deux lots) : diagonale du pied avant au haut arrière, coupée
# à l'horizontale aux deux bouts, posée sur la lisse basse et sous la lisse de barre (ou la lisse haute), contre les
# montants. Elle empêche l'échelle de se déformer en parallélogramme d'avant en arrière.
ECHARPES = []
for nom, y in ECH.items():
    e = ECHELLES[nom]
    xi0, xi1 = XO0 + DL, XO1 - DL
    zb, zt = Z0 + DL, (e["barre"].z0 if e["barre"] else e["haute"].z0)
    sin_ = (zt - zb) / math.hypot(xi1 - xi0, zt - zb)
    a_ = DE / sin_                                   # longueur de la coupe horizontale
    c_ = Profil("bois", f"echarpe_{nom}", [(xi0, zb), (xi0 + a_, zb), (xi1, zt), (xi1 - a_, zt)], y, y + DE, rep="G11",
                etape=1, groupe="ossature")
    PIECES.append(c_)
    ECHARPES.append(c_)
    _u = (xi1 - a_ - xi0, zt - zb)
    ECHARPE = dict(L=((xi1 - xi0) * _u[0] + (zt - zb) * _u[1]) / math.hypot(*_u), coupe=math.degrees(math.asin(sin_)))
ECHARPE["L"] = max(ECHARPE["L"], 0)
_ec, _en = ECHELLES["c"], ECHELLES["n"]
_yi0, _yi1 = _en["av"].y1, _ec["av"].y0       # entre les échelles du bac : 3,9 → 45,3

# ------------------------------------------------------------------ bascule
# V5.1 : le L (porte A6 + plateau A3, tenus par deux contrefiches en diagonale) pivote sur l'arête avant du rail avant,
# au coin arrière bas de la porte (deux charnières plates entre le rail et le plateau). On tire la porte : l'arrière du
# plateau monte et vient buter sous la butée G6, tasseau entre les montants arrière des échelles du bac ; la hauteur de
# la butée fixe l'angle. Les deux sacs pendent entre la barre de la porte et la barre arrière, sous le plan.
BAC = dict(angle=20, jeu=0.5, porte_bas=0.5, prof=20, barre=(2.2, 2.2), entaille=1.25, sous_plafond=3.0,
           sup=dict(x=4.5, z=5.0), contrefiche=30)
_b = BAC
AXE = (XO0, Z0 + DL)                                 # arête avant du rail avant = coin arrière bas de la porte
BAC["axe"] = AXE


def bascule(x, z, axe, angle):
    """Position d'un point (x, z) du L une fois basculé de angle degrés vers la pièce autour de axe = (xa, za)."""
    a = math.radians(angle)
    u, w = axe[0] - x, z - axe[1]                     # u : vers la pièce (ouest), w : vers le haut
    u2, w2 = u * math.cos(a) + w * math.sin(a), -u * math.sin(a) + w * math.cos(a)
    return axe[0] - u2, axe[1] + w2


# ------------------------------------------------------------------ ② rails et butée
# Deux rails au sol entre les échelles du bac, au droit des montants : ils les lient en bas et portent le plateau fermé ;
# le rail avant reçoit les charnières. Vissés à travers le montant du milieu ; côté nord, contre le mur, une équerre
# plate sur les faces affleurantes du montant et du tasseau.
# V5.10 : profondeur du plateau calculée pour que son coin arrière haut, basculé à BAC["angle"], arrive sous le milieu
# des montants arrière (là où était la butée jusqu'à la V5.19 ; V5.20 : la butée est plus loin, voir ⑥)
_a0 = math.radians(_b["angle"])
BAC["plateau"] = (XO1 - DL / 2 - XO0 + T * math.sin(_a0)) / math.cos(_a0)
_xp0, _xp1 = XO0, XO0 + _b["plateau"]           # plateau : du dos de la porte au rail arrière
_yp0, _yp1 = _yi0 + _b["jeu"], _yi1 - _b["jeu"]
_zp = Z0 + DL                                   # dessous du plateau, posé sur les rails
_coin = bascule(_xp1, _zp + T, AXE, _b["angle"])  # coin arrière haut du plateau, basculé
RAILS = [P("bois", f"rail_{k}", x0, x0 + DL, _yi0, _yi1, Z0, Z0 + DL, rep="G5", etape=2, groupe="ossature")
         for k, x0 in (("av", XO0), ("ar", XO1 - DL))]
for t_, m_ in zip(RAILS, ("av", "ar")):
    visser(_ec[m_], t_, "vis60", 2)
RAIL_EQUERRES = 2

# ------------------------------------------------------------------ ③ le L : plateau, porte, contrefiches
_pla = P("bac", "plateau", _xp0, _xp1, _yp0, _yp1, _zp, _zp + T, rep="A3", etape=3, groupe="bac")
# porte : du dessus du rail (0,5 de jeu : les nœuds des charnières) à 0,3 sous le plan ; elle couvre le chant avant du
# plateau
CHAMBRANLE = 0.5        # V5.16 : le chambranle de la porte d'entrée déborde de 0,5 du mur nord (relevé client) : la porte du
                        # linge, qui avance en basculant, doit passer devant lui avec 0,3 de jeu
PORTE_BAC = P("facade", "bac_porte", FACE, XO0, Y0 + CHAMBRANLE + 0.3, CB["y1"] - 0.15, Z0 + DL + _b["porte_bas"], Z_PLAN - 0.3,
              rep="A6", etape=3, groupe="bac", etiq="Linge sale")
trou(3, PORTE_BAC, None, "prise", (FACE, (PORTE_BAC.y0 + PORTE_BAC.y1) / 2, PORTE_BAC.z1 - 3), (-1, 0, 0),
     "1 trou au milieu de la largeur, centre à 30 du haut")
# deux contrefiches à 45° aux bords du plateau : tasseau coupé d'onglet aux deux bouts, une jambe de CONTREFICHE sur la
# porte et sur le plateau ; vissées par-dessous à travers le plateau, et à la porte par une équerre d'assemblage
_L, _d = _b["contrefiche"], DL * math.sqrt(2)
_zc = _zp + T
CONTREFICHES = []
for k, y0 in (("n", _yp0), ("s", _yp1 - DE)):
    c_ = Profil("bois", f"contrefiche_{k}", [(XO0, _zc + _L), (XO0, _zc + _L - _d), (XO0 + _L - _d, _zc),
                                             (XO0 + _L, _zc)], y0, y0 + DE, rep="G7", etape=3, groupe="bac")
    PIECES.append(c_)
    CONTREFICHES.append(c_)
    for x in (XO0 + _L - _d / 2 - 2, XO0 + _L - _d / 2 + 1):
        trou(3, _pla, c_, "vis40", (x, y0 + DE / 2, _zp), (0, 0, -1), "2 trous sous le bout de la contrefiche, dans l'axe")
BAC_EQUERRES = 4        # 2 entre porte et plateau (au milieu), 1 entre chaque contrefiche et la porte
ACCROCHE_EQUERRES = 2   # V5.13 : accroche centrale sous le plan (le lot de 6 équerres suffit)
CHARNIERES = dict(n=2, y=(_yp0 + 8, _yp1 - 8))
FACADES = [(PORTE_BAC.z0, PORTE_BAC.z1)]

# ------------------------------------------------------------------ ⑤ barres et sacs
# La barre de la porte repose dans deux supports B1 (demi-lune Ø 25) vissés au dos de la porte ; la barre arrière, à
# BAC["prof"] du nu avant, dans deux supports vissés aux lisses de barre G8, sous le plan : on la soulève pour sortir les
# sacs. Deux sacs à soufflet côte à côte, enfilés sur les deux barres, leur fond posé sur le plateau.
_bx, _bz = _b["barre"]


def rond(xc, zc, r, n=16):
    """Section ronde (barre) en polygone de n côtés, dans le plan x-z."""
    return [(xc + r * math.cos(2 * math.pi * k / n), zc + r * math.sin(2 * math.pi * k / n)) for k in range(n)]


def support(nom, x0, x1, y0, z0, z1, etape, groupe):
    """Support de barre B1, bloc de 18 avec une demi-lune Ø 25 au milieu du dessus, où la barre ronde se pose."""
    xc, rn = (x0 + x1) / 2, BAC["entaille"]
    arc = [(xc + rn * math.cos(-math.pi * j / 12), z1 + rn * math.sin(-math.pi * j / 12)) for j in range(13)]
    b = Profil("support", nom, [(x0, z0), (x1, z0), (x1, z1)] + arc + [(x0, z1)], y0, y0 + T, rep="B1", etape=etape,
               groupe=groupe)
    PIECES.append(b)
    return b


_zb1 = Z_PLAN - _b["sous_plafond"]              # dessus des barres : place pour les sortir des demi-lunes
_zb0 = _zb1 - _bz
_zs0, _zs1 = _zb0 - (_b["sup"]["z"] - _b["entaille"]), _zb0 + _b["entaille"]   # supports : barre au fond de la demi-lune
_xf0 = XO0 + (_b["sup"]["x"] - _bx) / 2         # barre de la porte, centrée sur ses supports
_xr0 = XO0 + _b["prof"]                         # barre arrière
for nom, y, e in (("n", _yi0, _en), ("s", _yi1 - T, _ec)):
    s_ = support(f"support_fixe_{nom}", _xr0 - (_b["sup"]["x"] - _bx) / 2, _xr0 + (_b["sup"]["x"] + _bx) / 2, y, _zs0,
                 _zs1, 5, "bac")
    visser(s_, e["barre"], "vis40", 5, us=[s_.x0 + 0.7, s_.x1 - 0.7])   # hors de la demi-lune
# V5.13 : chaque sac a ses deux demi-barres, on le sort sans toucher à l'autre. Au milieu de la largeur, deux supports B1
# côte à côte au dos de la porte (un par demi-barre) et, pour les barres arrière, une accroche centrale G10 : un bout de
# tasseau pendu sous le plan (deux équerres), entaillé d'un crochet ouvert vers la porte où entre le bout de chaque
# demi-barre arrière.
_ymb = (_yp0 + _yp1) / 2
for nom, y in (("n", _yi0 + _b["jeu"]), ("cn", _ymb - T - 0.1), ("cs", _ymb + 0.1), ("s", _yi1 - _b["jeu"] - T)):
    s_ = support(f"support_porte_{nom}", XO0, XO0 + _b["sup"]["x"], y, _zs0, _zs1, 4, "bac")
    visser(s_, PORTE_BAC, "vis16l", 4, us=[_zs0 + 1.0, _zs0 + 2.2])   # sous la demi-lune
# accroche : bout de tasseau debout sous le plan ; crochet en J ouvert vers la porte : une entrée horizontale un peu plus
# haute que la barre, puis une poche où la barre retombe (lèvre de LEVRE devant elle) ; deux équerres la vissent sous le
# plan, une de chaque côté (faces nord et sud), au-dessus du crochet
LEVRE = 0.7
_xa0, _xa1 = _xr0 + _bx / 2 - DE / 2, _xr0 + _bx / 2 + DE / 2
_p0, _p1 = _xr0 - 0.1, _xr0 + _bx + 0.1         # poche de la barre
_e0, _e1 = _zb0 + LEVRE - 0.1, _zb1 + LEVRE     # entrée : on soulève la barre de LEVRE pour la sortir
assert _xa0 < _p0 and _p1 < _xa1 and _e1 < Z_PLAN - 1.5, "crochet dans le tasseau, équerres au-dessus"
ACCROCHE = Profil("bois", "accroche_centrale", [(_xa0, _zs0), (_xa1, _zs0), (_xa1, Z_PLAN), (_xa0, Z_PLAN), (_xa0, _e1),
                                                (_p1, _e1), (_p1, _zb0 - 0.1), (_p0, _zb0 - 0.1), (_p0, _e0),
                                                (_xa0, _e0)], _ymb - DL / 2, _ymb + DL / 2, rep="G10", etape=7,
                  groupe="bac")
PIECES.append(ACCROCHE)
for y_, n_ in ((ACCROCHE.y0, (0, -1, 0)), (ACCROCHE.y1, (0, 1, 0))):
    trou(7, ACCROCHE, None, "vis16", ((_xa0 + _xa1) / 2, y_, Z_PLAN - 1.0), n_,
         "1 équerre par face (nord et sud), aile du bas : 2 vis 4 × 16 au-dessus du crochet")
BAC["crochet"] = 1.7                            # chaque demi-barre arrière entre de tant dans l'accroche
for k, (y0, y1) in enumerate(((_yi0 + _b["jeu"], _ymb - 0.2), (_ymb + 0.2, _yi1 - _b["jeu"]))):
    PIECES.append(Profil("barre", f"barre_porte_{'ns'[k]}", rond(_xf0 + _bx / 2, (_zb0 + _zb1) / 2, _bx / 2),
                         y0, y1, rep="E4", etape=5, groupe="bac"))
for k, (y0, y1) in enumerate(((_yi0 + _b["jeu"], _ymb - DL / 2 + BAC["crochet"]),
                              (_ymb + DL / 2 - BAC["crochet"], _yi1 - _b["jeu"]))):
    PIECES.append(Profil("barre", f"barre_fixe_{'ns'[k]}", rond(_xr0 + _bx / 2, (_zb0 + _zb1) / 2, _bx / 2),
                         y0, y1, rep="E4", etape=7, groupe="bac"))
# sacs (pas à découper), porte fermée : de la barre de la porte à la barre arrière en haut, le fond (soufflet) sur le
# plateau jusqu'à 1 de la butée ; entre les contrefiches, deux sacs côte à côte
_xs1 = XO1 - DL - 1
_ys = (_yp0 + DE + 0.3, _yp1 - DE - 0.3)
_gap = DL + 1.0                                 # V5.13 : entre les sacs, l'accroche centrale et 0,5 de chaque côté
_wl = (_ys[1] - _ys[0] - _gap) / 2
SACS = []
for k in range(2):
    y0 = _ys[0] + k * (_wl + _gap)
    SACS.append(Profil("sac", f"bac_sac_{k + 1}", [(_xf0, _zb0 + 1), (_xr0 + _bx, _zb0 + 1), (_xs1, _zc + 1),
                                                    (_xf0 + 1, _zc + 1)], y0, y0 + _wl, etape=5, groupe="bac"))
BAC["barres"] = (_xf0, _xr0, _zb0, _zb1)
BAC["largeur_sac"] = _wl
BAC["h_sac"] = _zb0 + 1 - (_zc + 1)
BAC["fond_sac"] = _xs1 - (_xf0 + 1)
_sp = SACS[0].xz
_aire = abs(sum(x0 * z1 - x1 * z0 for (x0, z0), (x1, z1) in zip(_sp, _sp[1:] + _sp[:1]))) / 2
VOLUME_BAC = _aire * _wl / 1000                 # par sac
VOLUME_CASE = 2 * VOLUME_BAC
_haut_porte = bascule(FACE, PORTE_BAC.z1, AXE, _b["angle"])
BAC["avancee"] = FACE - _haut_porte[0]           # le haut de la porte avance de tant dans la pièce
_barre_ouverte = bascule(_xf0, _zb1, AXE, _b["angle"])
BAC["bouche_fermee"] = _xr0 - (_xf0 + _bx)
BAC["bouche"] = _xr0 - _barre_ouverte[0]         # entre les barres, porte ouverte
BAC["coin"] = _coin
assert _barre_ouverte[1] < Z_PLAN, "la barre de la porte passe sous le plan"
assert bascule(FACE, PORTE_BAC.z0, AXE, _b["angle"])[1] > 0.5, "le bas de la porte ne touche pas le sol"
# équilibre à vide (estimation, mélaminé ≈ 650 kg/m³, sapin ≈ 450, de mémoire) : porte et supports devant l'axe,
# plateau et contrefiches derrière ; angle où le L à vide bascule seul vers la butée
_m = [(PORTE_BAC, 650), (_pla, 650)] + [(c_, 450) for c_ in CONTREFICHES]


def _moment(a):
    r = 0
    for b_, rho in _m:
        v = (b_.x1 - b_.x0) * (b_.y1 - b_.y0) * (b_.z1 - b_.z0) * (0.5 if isinstance(b_, Profil) else 1)
        x, _ = bascule((b_.x0 + b_.x1) / 2, (b_.z0 + b_.z1) / 2, AXE, a)
        r += rho * v * (x - AXE[0])
    return r


BAC["equilibre"] = next(a / 10 for a in range(0, 900) if _moment(a / 10) < 0)
assert _moment(0) > 0, "à vide, le L reste fermé"

# ------------------------------------------------------------------ ⑥ deux arrêts : les barres à 20°, la butée au-delà
# V5.20 (demande client) : à BAC["angle"], le haut des soufflets, coupé à la bouche, se tend entre la barre de la porte
# et la barre arrière : les barres arrêtent le L (usage courant). À 20°, l'ouverture entre le haut de la porte et le
# chant du plan est plus étroite que le fond du sac plein : pour le sortir, on lève la barre arrière et le L bascule
# jusqu'à la butée, à BAC["angle_max"], le premier angle où l'ouverture dépasse le fond du sac de MARGE_SAC.
# V5.21 (idée du client) : la butée est plantée dans la face intérieure de l'écharpe de chaque échelle du bac et dépasse
# de VIS_BUTEE["depasse"] au-dessus du bord du plateau. Le plateau, en montant, vient s'appuyer dessous à
# BAC["angle_max"]. V5.22 : passé l'équilibre (≈ 24°), le L à vide part seul et frappe la butée (≈ 0,7 J) : tire-fond
# inox 8 × 60 au lieu de la vis 5 × 60 (≈ 4 fois plus résistant en flexion), et une mousse amortisseur collée sur le
# plateau, là où il frappe. Position : sur la droite qui part de l'axe, à VIS_BUTEE["r"] de lui, cherchée pour la plus
# grande marge : plus près, le trou sort de l'écharpe par l'avant ; plus loin, la contrefiche heurte la tête en
# basculant (la butée passe dans le triangle entre plateau et contrefiche, au-dessus du plateau).
MARGE_SAC = 3.0


def ouverture(a):
    """Passage entre le haut du dos de la porte, basculée de a degrés, et le chant avant du dessous du plan."""
    x, z = bascule(XO0, PORTE_BAC.z1, AXE, a)
    return math.hypot(FACE - x, Z_PLAN - z)


BAC["angle_max"] = next(a for a in range(BAC["angle"], 90) if ouverture(a) >= BAC["fond_sac"] + MARGE_SAC)
BAC["ouverture"] = ouverture(BAC["angle"])
BAC["ouverture_max"] = ouverture(BAC["angle_max"])
BAC["avancee_max"] = FACE - bascule(FACE, PORTE_BAC.z1, AXE, BAC["angle_max"])[0]
assert BAC["ouverture"] < BAC["fond_sac"], "à 20°, le sac plein ne sort pas : d'où la butée plus loin"
assert BAC["angle_max"] > BAC["equilibre"]      # à vide, le L reste ouvert à la butée ; on le referme à la main
VIS_BUTEE = dict(d=0.8, tete=1.5, depasse=2.5, dans=3.5, mousse=0.3, avant_trou=0.5, marge_min=0.5,
                 nom="tirefond inox tête 6 pans 8 × 60")   # mousse : épaisseur estimée (8 × 16, épaisseur non lue)
_rv = VIS_BUTEE["d"] / 2
_cf1, _cf2 = CONTREFICHES[0].xz[1], CONTREFICHES[0].xz[2]


def _dist_cf(phi):
    """Distance de l'axe au bord intérieur de la contrefiche, dans la direction phi (repère du L)."""
    x1, z1, x2, z2 = _cf1[0] - AXE[0], _cf1[1] - AXE[1], _cf2[0] - AXE[0], _cf2[1] - AXE[1]
    c, s_ = math.cos(phi), math.sin(phi)
    return (x1 * (z1 - z2) - z1 * (x1 - x2)) / (c * (z1 - z2) - s_ * (x1 - x2))


_e0 = next(c_ for c_ in ECHARPES if c_.nom == "echarpe_n")


def _bords(e_, z):
    (xa, za), (xa2, _), (xb2, zb2), (xb, zb) = e_.xz
    return xa + (z - za) / (zb - za) * (xb - xa), xa2 + (z - za) / (zb2 - za) * (xb2 - xa2)


def _butee(r):
    """Position (x, z) de l'axe du tire-fond à r de l'axe du L, et ses marges (avant, arrière, contrefiche)."""
    ph0 = math.asin((T + VIS_BUTEE["mousse"] + _rv) / r)
    psi = math.radians(BAC["angle_max"]) + ph0
    x, z = AXE[0] + r * math.cos(psi), AXE[1] + r * math.sin(psi)
    av, ar = _bords(_e0, z)
    mc = min(_dist_cf(ph0 + k * (psi - ph0) / 50) for k in range(51)) - r - VIS_BUTEE["tete"] / 2
    return x, z, (x - av - _rv, ar - x - _rv, mc)


VIS_BUTEE["r"] = max((r / 10 for r in range(100, 260)), key=lambda r: min(_butee(r)[2]))
_xv, _zv, _mg = _butee(VIS_BUTEE["r"])
VIS_BUTEE["marges"] = _mg
VIS_BUTEE["marge"] = min(_mg)
assert VIS_BUTEE["marge"] >= VIS_BUTEE["marge_min"], VIS_BUTEE
Z_BUTEE = _zv
BAC["z_butee"] = Z_BUTEE
BAC["x_butee"] = _xv
# la mousse, sur le dessus du plateau, au droit du tire-fond : à tant du dos de la porte, le long du plateau
VIS_BUTEE["mousse_pos"] = math.sqrt(VIS_BUTEE["r"] ** 2 - (T + VIS_BUTEE["mousse"] + _rv) ** 2) - 0.0
BUTEES = []
for nom, y0, sy in (("n", _yi0, 1), ("c", _yi1, -1)):
    e_ = next(c_ for c_ in ECHARPES if c_.nom == f"echarpe_{nom}")
    y1 = y0 + sy * VIS_BUTEE["depasse"]
    b_ = P("vis", f"butee_vis_{nom}", _xv - _rv, _xv + _rv, min(y0, y1), max(y0, y1), _zv - _rv, _zv + _rv, etape=2,
           groupe="ossature")
    BUTEES.append(b_)
    trou(2, e_, None, "butee", (_xv, y0, _zv), (0, -sy, 0),
         f"1 trou à {cm_(_zv)} du sol, à {cm_(_xv - XO0)} du nu avant des montants, perpendiculaire à la face "
         f"(il reste {cm_(_mg[0] * 10)} mm de bois devant)")
    assert min(_yp1, max(y0, y1)) - max(_yp0, min(y0, y1)) >= 1.5, "le tire-fond passe au-dessus du plateau sur 1,5 au moins"
# effort sur chaque butée, L à vide posé dessus (estimation, densités de mémoire) ; énergie du choc depuis l'équilibre
VIS_BUTEE["effort"] = -_moment(BAC["angle_max"]) * 1e-8 * 9.81 / (VIS_BUTEE["r"] / 100) / 2   # N
VIS_BUTEE["choc"] = sum(-_moment(BAC["equilibre"] + k / 10) for k in
                        range(int((BAC["angle_max"] - BAC["equilibre"]) * 10))) * 1e-8 * 9.81 * math.radians(0.1)  # J
BUTEE = BUTEES[0]
assert BAC["angle_max"] > BAC["equilibre"]      # à vide, le L reste ouvert à la butée ; on le referme à la main

# ------------------------------------------------------------------ patron du sac
# Sac à soufflet, comme un cabas : une bande (devant + fond + dos) et deux soufflets (côtés). En haut du devant et du
# dos, un fourreau pour la barre. V5.20 : le haut des soufflets fait exactement la bouche à BAC["angle"] : il se tend
# et arrête le L (ourlet double, il porte l'effort).
COUTURE, OURLET, FOURREAU = 1.5, 2.0, 6.0      # fourreau : 10 de tour pour une barre Ø 22, plus 1 de rempli
_hs = BAC["h_sac"] + 3                          # du fond à la barre, plus de quoi faire le tour de la barre
_ds = BAC["fond_sac"]
_ws = BAC["largeur_sac"]
PATRON = dict(
    hauteur=_hs, fond=_ds, largeur=_ws,
    bande=(_ws + 2 * COUTURE, 2 * _hs + _ds + 2 * FOURREAU),        # largeur × longueur de coupe
    soufflet=(max(_ds, BAC["bouche"]) + 2 * COUTURE, _hs + COUTURE + OURLET),   # largeur × hauteur de coupe
    soufflet_haut=BAC["bouche"] + 2 * COUTURE,
    soufflet_bas=_ds + 2 * COUTURE,
    tissu=150,
)
# deux sacs dans une toile de 150 : les deux bandes côte à côte en long, les quatre soufflets en deux colonnes à côté
assert 2 * PATRON["bande"][0] + 2 * PATRON["soufflet"][0] <= PATRON["tissu"], PATRON
assert 2 * PATRON["soufflet"][1] <= PATRON["bande"][1], PATRON
PATRON["metrage"] = PATRON["bande"][1] / 100
# V5.19 : toile chiffrée chez Marseille Textiles (relevé en ligne du 13/10/2026), coupée au mètre : on arrondit aux 10 cm
TOILE = dict(nom="Toile de transat 100 % polyester 420 g/m², laize 150", prix_m=7.20, laize=150,
             magasin="Marseille Textiles, 10 rue Beaumont, 13001 Marseille", releve="13/10/2026",
             url="https://www.marseilletextiles.com/tissus-ameublement-decoration/73-tissu-toile-de-transat-.html")
assert TOILE["laize"] >= PATRON["tissu"]
TOILE["achat_m"] = math.ceil(PATRON["metrage"] * 10 - 1e-9) / 10
TOILE["prix"] = round(TOILE["achat_m"] * TOILE["prix_m"], 2)
# ------------------------------------------------------------------ ⑦ plan de travail
# Le plan est posé sur la tête des trois échelles et vissé par-dessous à travers les lisses hautes.
# V5.7 : plus de trappe. Le robinet d'arrêt est remonté dans la niche, au-dessus du plan (décision client), à 41 du mur
# sud : on l'atteint sans rien ouvrir, et la machine recule vers le mur du fond. Le tuyau d'arrivée monte derrière le
# plan par une encoche au chant arrière (passe-tuyau).
PLAN_P = PROF           # V5.10 : plan de 60, recoupé dans le 1800 × 640 × 28 du commerce
PLAN_X1 = FACE + PLAN_P                        # contre le mur du fond (joint silicone)
ROBINET = dict(y=Y1 - 41, z=round(Z_DESSUS + 15))
PASSE = dict(l=6, p=4)                         # encoche du passe-tuyau : 6 de large, 4 de profondeur dans le chant arrière
TRAPPE = dict(x0=PLAN_X1 - PASSE["p"], x1=PLAN_X1, y0=ROBINET["y"] - PASSE["l"] / 2, y1=ROBINET["y"] + PASSE["l"] / 2)
assert LLZ["y0"] < TRAPPE["y0"] and TRAPPE["y1"] < LLZ["y1"], "passe-tuyau au-dessus de la zone de la machine"
_plan = P("plan", "plan_travail", FACE, PLAN_X1, YM0, YM1, Z_PLAN, Z_DESSUS, rep="D1", etape=7, groupe="plan",
          miroir=False, encoche=(TRAPPE["x0"], TRAPPE["x1"], TRAPPE["y0"], TRAPPE["y1"]))
for e in ECHELLES.values():
    visser(e["haute"], _plan, "vis40l", 7)


# ------------------------------------------------------------------ ⑪ caisson haut, P 45, jusqu'au plafond
# Identique dans les deux versions : serviettes au nord, pharmacie et produits divers au sud, deux portes coulissantes.
CH = dict(x0=X1 - 45, x1=X1, y0=Y0 + 0.5, y1=Y1 - 0.5, z0=Z_HAUT, z1=Z_HAUT1, retrait=6)
_h = CH
_hx = _h["x1"] - F
_hy0, _hy1 = _h["y0"] + T, _h["y1"] - T
_hz0, _hz1 = _h["z0"] + T, _h["z1"] - T


def H_(*a, **k):
    return P(*a, miroir=False, groupe="caisson_haut", **k)


H_("caisson", "ch_cote_n", _h["x0"], _hx, _h["y0"], _hy0, _h["z0"], _h["z1"], rep="A7", etape=8)
H_("caisson", "ch_cote_s", _h["x0"], _hx, _hy1, _h["y1"], _h["z0"], _h["z1"], rep="A7", etape=8)
H_("caisson", "ch_dessous", _h["x0"], _hx, _hy0, _hy1, _h["z0"], _hz0, rep="A8", etape=8)
H_("caisson", "ch_dessus", _h["x0"], _hx, _hy0, _hy1, _hz1, _h["z1"], rep="A8", etape=8)
_ym = CENTRE
H_("caisson", "ch_montant", _h["x0"] + _h["retrait"], _hx, _ym - T / 2, _ym + T / 2, _hz0, _hz1, rep="A9", etape=8)
# fond en deux moitiés (une tablette fait 600 de large), jointes derrière le montant central
H_("fond", "ch_fond_n", _hx, _h["x1"], _h["y0"], CENTRE - 0.1, _h["z0"], _h["z1"], rep="C1", etape=8)
H_("fond", "ch_fond_s", _hx, _h["x1"], CENTRE + 0.1, _h["y1"], _h["z0"], _h["z1"], rep="C1", etape=8)
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
           rep=rep, etape=10)
# portes coulissantes intérieures, recouvrement 3 au milieu. V5.4 : pas de kit, deux rainures à la défonceuse dans le
# dessous du dessus et le dessus du dessous (A8) ; les portes glissent dedans sur des patins PTFE. Rainure du haut plus
# profonde : on soulève la porte dedans pour la dégager de celle du bas.
RAINURE = dict(l=2.0, haut=1.2, bas=0.5, bord=0.5, entre=1.0, prise=0.6)   # largeur, profondeurs, retraits (cm)
_rn = RAINURE
RAINURE["x"] = [_h["x0"] + _rn["bord"] + k * (_rn["l"] + _rn["entre"]) for k in range(2)]   # bord avant des rainures
assert _rn["haut"] - _rn["prise"] >= _rn["bas"] + 0.1, "la porte se soulève hors de la rainure du bas"
assert RAINURE["x"][1] + _rn["l"] < _h["x0"] + _h["retrait"], "rainures devant le montant central"
_lp = (_hy1 - _hy0 + 3) / 2
_zp0, _zp1 = _hz0 - _rn["bas"], _hz1 + _rn["prise"]
for k, (nom, y0, etiq) in enumerate((("n", _hy0, "Serviettes"), ("s", _hy1 - _lp, "Pharmacie et produits divers"))):
    xa = RAINURE["x"][k] + (_rn["l"] - T) / 2
    H_("porte", f"ch_porte_{nom}", xa, xa + T, y0, y0 + _lp, _zp0, _zp1, rep="A12", etape=10, etiq=etiq)
H_("fileur", "ch_fileur", _h["x0"], _h["x0"] + T, _h["y0"], _h["y1"], _h["z1"], H, rep="A13", etape=10)
CH["porte"] = (_lp, _zp1 - _zp0)


def touche(a, b):
    A, Bb = _bornes(a), _bornes(b)
    contact = any(abs(A[k][1] - Bb[k][0]) < 1e-6 or abs(A[k][0] - Bb[k][1]) < 1e-6 for k in range(3))
    return contact and sum(min(A[k][1], Bb[k][1]) > max(A[k][0], Bb[k][0]) for k in range(3)) == 2


_pc = {b.nom: b for b in PIECES}
for cote in ("ch_cote_n", "ch_cote_s"):
    for b_ in ("ch_dessous", "ch_dessus"):
        visser(_pc[cote], _pc[b_], "vis40", 8)
for b_ in ("ch_dessous", "ch_dessus"):
    visser(_pc[b_], _pc["ch_montant"], "vis40", 8)
for f_ in ("ch_fond_n", "ch_fond_s"):
    for b_ in ("ch_cote_n", "ch_cote_s", "ch_dessous", "ch_dessus", "ch_montant"):
        if touche(_pc[f_], _pc[b_]):
            visser(_pc[f_], _pc[b_], "vis40", 8)
# fixation au mur du fond : de l'intérieur, à travers le fond. V5.8 : le carrelage s'arrête à CARRELAGE (relevé
# client) : toutes les chevilles au-dessus, dans le mur nu (plus de perçage du carrelage) ; deux rangées de trois
CARRELAGE = 204
EP_CARRELAGE = 1.0      # V5.16 : épaisseur carreau + colle (estimée, à mesurer) ; les cotes du relevé sont prises sur le carreau
                        # (X1 = surface du carrelage) : au-dessus de CARRELAGE, le mur nu est EP_CARRELAGE plus loin. Le fond
                        # du caisson haut s'appuie sur le carreau en bas ; en haut, une cale de cette épaisseur derrière
                        # chaque cheville, et des vis plus longues d'autant.
_zf = (CARRELAGE + 6, _hz1 - 6)
assert _zf[0] < _zf[1] - 10, "deux rangées de chevilles au-dessus du carrelage"
for z in _zf:
    for y in (10, CENTRE - 8 if z == _zf[1] else CENTRE + 8, Y1 - 10):
        f_ = _pc["ch_fond_n" if y < CENTRE else "ch_fond_s"]
        trou(9, f_, None, "cheville", (_hx, y, z), (-1, 0, 0), f"6 trous au-dessus du carrelage ({CARRELAGE}) : deux "
             f"rangées à {cm_(_zf[0])} et {cm_(_zf[1])} du sol, à 10 des côtés et près du montant")

# meuble de chaque repère (code couleur des découpes) : le caisson haut, le reste est le meuble bas
HAUT = {b.rep for b in PIECES if b.groupe == "caisson_haut" and b.rep}
assert not HAUT & {b.rep for b in PIECES if b.groupe != "caisson_haut" and b.rep}, "repère commun haut et bas"


def meuble(rep):
    return "haut" if rep in HAUT else "bas"


# ------------------------------------------------------------------ équipements (pas à découper)
MACHINE = Bloc("machine", "lave_linge", X1 - JEU_LL - LL["p"], X1 - JEU_LL, LLZ["y0"] + (LLZ["y1"] - LLZ["y0"] - LL["l"]) / 2,
               LLZ["y0"] + (LLZ["y1"] - LLZ["y0"] + LL["l"]) / 2, SOCLE_H, SOCLE_H + LL["h"], etape=6, groupe="machine")
LED = Bloc("led", "profil_led", _h["x0"] + 2, _h["x0"] + 4, _hy0 + 2, _hy1 - 2, Z_HAUT - 1, Z_HAUT, etape=10,
           miroir=False, groupe="caisson_haut")
PRISES = Bloc("prise", "prises_niche", X1 - 1, X1, 84, 104, 122, 130, miroir=False)   # bloc 2 prises + USB, mur du fond
EQUIPEMENTS = [MACHINE, LED, PRISES]

# ------------------------------------------------------------------ salle de bain (pour le plan)
SDB = dict(l=234, p=160)
GONDS = 69              # V5.11 : gonds de la porte d'entrée à 69 du mur du fond (relevé client ; avant : 77)
PORTE = dict(x0=X1 - GONDS - 73, x1=X1 - GONDS, l=73)   # porte d'entrée standard de 73 (client) au mur nord, vantail ouvert à 90° le long des gonds
DOUCHE = (5, 50, 78, 155)               # x0, y0, x1, y1
LAVABO = (82, Y1, 165, 160)


# ------------------------------------------------------------------ variante : deux bacs à roulettes du commerce (V5.17)
# Le L basculant, ses barres et ses sacs sont remplacés par deux paniers étroits à roulettes Wenko Corno (18,5 × 40 × 60,
# 43 L, polyester, couvercle à cordon ; fiches La Redoute et Galaxus, à mesurer à réception) roulés côte à côte entre
# les échelles du bac. Le rail avant G5 disparaît (les roulettes doivent passer) ; le rail arrière reste au sol derrière
# les paniers et lie les échelles en bas, le plan les lie en haut. V5.18 : pas de porte (choix client), les paniers
# affleurent presque le nu du plan.
CORNO = dict(l=18.5, p=40, h=60, litres=43, prix=45.00, nom="panier à linge étroit à roulettes Wenko Corno 43 L",
             source="Amazon, relevé client du 13/10/2026", entre=1.0, recul=0.5)
_co = CORNO
_cy0 = (_yi0 + _yi1 - 2 * _co["l"] - _co["entre"]) / 2
CORNO["jeu_cote"] = _cy0 - _yi0
assert CORNO["jeu_cote"] > 1, "les deux paniers passent entre les échelles"
_cx0 = FACE + _co["recul"]                      # V5.18 : sans porte, au nu du plan à recul près
assert _cx0 + _co["p"] < RAILS[1].x0, "les paniers s'arrêtent devant le rail arrière"
assert _co["h"] < ECHELLES["n"]["barre"].z0 - 1, "les paniers passent sous les lisses de barre"
PANIERS = [Bloc("panier", f"panier_{k + 1}", _cx0, _cx0 + _co["p"], y, y + _co["l"], 0, _co["h"], etape=5, groupe="bac",
                etiq="")
           for k, y in enumerate((_cy0, _cy0 + _co["l"] + _co["entre"]))]
CORNO["place"] = dict(l=_yi1 - _yi0, p=RAILS[1].x0 - FACE, h=ECHELLES["n"]["barre"].z0)
# pièces du L retirées (porte, rail avant, butée, plateau, contrefiches, supports, barres, accroche) ; G8 et écharpes restent
RETIRES_ROUL = ({"rail_av", "plateau", "bac_porte", "accroche_centrale"} | {c_.nom for c_ in CONTREFICHES}
                | {b.nom for b in PIECES if b.role in ("support", "barre")} | {b_.nom for b_ in BUTEES})
VOLUME_ROUL = 2 * _co["litres"]


def version(c="d"):
    """Pièces et équipements de la version c : "d" (L basculant) ou "dr" (linge sale en deux paniers à roulettes).
    V5.23 : la variante du caisson haut en IKEA METOD (V5.2) est retirée."""
    pieces = list(PIECES)
    if c.endswith("r"):
        pieces = [b for b in pieces if b.nom not in RETIRES_ROUL] + PANIERS
    else:
        pieces += SACS
    return pieces + EQUIPEMENTS


VERSIONS = {"d": "L basculant", "dr": "bacs à roulettes"}

# ------------------------------------------------------------------ matériaux, débit, quincaillerie
MATERIAUX = {
    "A": ("Tablette mélaminée blanche 18 mm", "plateau et porte du bac, caisson haut (aggloméré non hydrofuge : chants "
          "coupés à recouvrir de chant thermocollant blanc)", T),
    "B": ("Tablette mélaminée blanche 18 mm", "supports des barres (chutes)", T),
    "E": ("Barres", "barres rondes Ø 22 des sacs", 0),
    "C": ("Tablette mélaminée blanche 18 mm", "fond du caisson haut, en deux moitiés", F),
    "D": ("Plan de travail stratifié 28 mm", "décor chêne clair (« oak »), bords droits, 1800 × 640, non hydrofuge", PT),
    "G": ("Tasseau sapin brut 38 × 38, non traité", "ossature du meuble bas : échelles, rails, contrefiches "
          "(non traité : poncer, puis peindre ou vernir toutes les faces, pieds compris)", DE),
}
# Panneaux du commerce pour le calepinage, par matériau (Weldom Marseille Saint-Barnabé, prix TTC, stock lu sur la fiche
# produit ; tablettes et plan relevés le 12/10/2026, tasseaux le 13/10/2026). Les tablettes ont leurs deux chants longs
# finis : pas de délignage. Un tasseau est rangé comme une « tablette » de 36 de large ; vendus par lots de 6 (lot).
TABLETTES_18 = [
    dict(L=2500, l=600, prix=16.50, stock=25, ref="9134941", nom="Tablette mélaminé 250 × 60 × 18 blanc"),
    dict(L=2500, l=500, prix=13.59, stock=50, ref="9134940", nom="Tablette mélaminé 250 × 50 × 18 blanc"),
    dict(L=2500, l=400, prix=12.50, stock=30, ref="9134939", nom="Tablette mélaminé 250 × 40 × 18 blanc"),
    dict(L=2500, l=300, prix=11.50, stock=37, ref="9134938", nom="Tablette mélaminé 250 × 30 × 18 blanc"),
]
PANNEAUX = {
    "M18": TABLETTES_18,
    "D": [dict(L=1800, l=640, prix=36.50, stock=3, ref="5634115", nom="Plan de travail 1800 × 640 × 28 décor chêne clair (oak), bords droits")],
    "G": [dict(L=2000, l=38, prix=23.60 / 6, lot=6, prix_lot=23.60, stock=12, ref="5634083",
               nom="Lot de 6 tasseaux sapin brut 38 × 38 × 2000, petits nœuds, FSC")],
}
STOCK = {"A": "M18", "B": "M18", "C": "M18", "D": "D", "G": "G"}   # matériau → panneau acheté
FIL = ()                # repères à ne pas tourner (aucun : mélaminé uni ; les tasseaux ne tiennent qu'en long)
MAGASIN = dict(nom="Weldom Marseille Saint-Barnabé", adresse="90 rue François Scaramelli, 13012 Marseille",
               tel="04 91 49 27 27", url="https://www.weldom.fr/m/weldom-marseille-saint-barnabe", releve="13/10/2026")
NOMS = {
    "G3": "Montant", "G4": "Lisse (basse ou haute)", "G5": "Rail (avant ou arrière)",
    "G11": "Écharpe d'échelle (diagonale)", "G7": "Contrefiche du L", "G8": "Lisse de barre (sous la lisse haute)", "G10": "Accroche centrale des barres arrière",
    "A3": "Plateau du bac", "A6": "Porte du bac", "B1": "Support de barre", "E4": "Barre du sac (ronde)",
    "A7": "Côté du caisson haut", "A8": "Dessus et dessous du caisson haut", "A9": "Montant central haut",
    "A10": "Étagère serviettes", "A11": "Étagère pharmacie et produits divers", "A12": "Porte coulissante",
    "A13": "Fileur de plafond",
    "C1": "Fond du caisson haut",
    "D1": "Plan de travail",
}
USINAGES = {
    "G3": "Les six identiques, de la hauteur du dessous du plan : coupés ensemble, serre-joint (la machine passe sous le "
          f"plan à {JEU_PLAN * 10:.0f} mm près)",
    "G4": "Entre les montants, au sol et en tête ; la lisse haute porte le plan de travail (lamages Ø 10 dessous pour "
          "les vis du plan)",
    "G5": "Entre les montants avant (rail avant) ou arrière (rail arrière) des échelles du bac, au sol ; le rail "
          "avant reçoit les deux charnières, le plateau fermé repose sur les deux",
    "G7": f"Coupée d'onglet à 45° aux deux bouts, jambes de {BAC['contrefiche']} sur la porte et sur le plateau ; vissée "
          "par-dessous à travers le plateau, une équerre d'assemblage contre la porte",
    "G11": f"Diagonale de chaque échelle, du pied avant au haut arrière ; les deux bouts coupés à l'horizontale "
           f"(angle de {90 - ECHARPE['coupe']:.0f}° avec la longueur, rapporteur ou fausse équerre) ; posée sur la lisse "
           "basse et sous la lisse de barre (lisse haute pour l'échelle du mur sud), contre les montants : deux vis 5 × 60 "
           "en biais à chaque bout",
    "G10": "Bout de tasseau vertical pendu sous le plan, au milieu de la largeur du bac, au droit des barres arrière ; deux "
           "équerres d'assemblage le vissent sous le plan, une sur chaque face. Crochet en J à la scie sauteuse : entrée "
           "horizontale de 23 de haut "
           f"ouverte côté porte, puis poche où le bout de chaque demi-barre arrière retombe (lèvre de {LEVRE * 10:.0f} mm devant)",
    "G8": "Sous la lisse haute des deux échelles du bac, vissée en bout dans les montants ; porte les supports B1 de la "
          "barre arrière",
    "A3": "Rectangle ; deux charnières plates dessous au bord avant ; reçoit les contrefiches",
    "A6": "Trou de prise Ø 25 en haut, au milieu ; au dos, quatre supports B1 en haut (deux aux bouts, deux au milieu), deux équerres en bas "
          "(plateau) et une sur chaque contrefiche",
    "B1": "Bloc de chute de 45 × 50 ; demi-lune Ø 25 au milieu du dessus, où la barre se pose : percer à la mèche plate "
          "sur le trait de scie entre deux supports, puis scier (un trou fait deux demi-lunes) ; sur la porte, deux "
          "lamages Ø 10 de 8 pour les vis 4 × 16",
    "E4": "Manche à balai coupé ou tringle de rideau de 2 m, Ø 20 à 25, en quatre demi-barres (une devant et une derrière "
          "par sac) ; glissées dans les fourreaux",
    "A7": "Taquets Ø 5 pas 32 côté intérieur, à 6 cm du chant avant",
    "A8": f"Deux rainures de {RAINURE['l'] * 10:.0f} de large à la défonceuse, sur toute la longueur, à "
          f"{RAINURE['bord'] * 10:.0f} et {(RAINURE['bord'] + RAINURE['l'] + RAINURE['entre']) * 10:.0f} du chant avant : "
          f"{RAINURE['haut'] * 10:.0f} de profondeur sous le dessus, {RAINURE['bas'] * 10:.0f} sur le dessous",
    "A12": f"Patins PTFE adhésifs sous le chant bas ; on la pose en la soulevant dans la rainure du haut "
           f"({RAINURE['haut'] * 10:.0f}) puis en la laissant descendre dans celle du bas ({RAINURE['bas'] * 10:.0f})",
    "A9": "En retrait de 6 derrière les rails ; taquets sur les deux faces",
    "D1": f"Recoupé de 1800 à 1134 ; au chant arrière, au-dessus du robinet, une encoche de {PASSE['l']} × "
          f"{PASSE['p']} pour le tuyau d'arrivée (scie sauteuse) ; non hydrofuge : vernir ou siliconer la coupe et "
          "l'encoche, joint silicone sur les murs",
    "C1": "Deux moitiés, jointes derrière le montant central A9",
}
QUINCAILLERIE = {
    "vis60": "vis à bois 5 × 60 (assemblages des tasseaux)",
    "vis40": "vis à bois 4 × 40",
    "vis16": "vis à bois 4 × 16 (charnières, équerres)",
    "colle": "colle à bois D3",
    "equerre_p": "équerre plate 100 (rails côté nord, vis 4 × 16)",
    "equerre_a": "équerre d'assemblage 50 × 50 (porte ↔ plateau et contrefiches, accroche centrale sous le plan ; vis 4 × 16)",
    "charniere_p": "charnière plate (universelle) 60 × 35, acier",
    "cheville": "cheville Ø 8 adaptée au mur + vis 6 × 70 et rondelle (mur nu, au-dessus du carrelage) + cale de l'épaisseur du carrelage derrière le fond",
    "taquet": "taquet d'étagère Ø 5",
    "patins": "patins glisseurs PTFE adhésifs 15 × 100, lot de 2 (sous les portes coulissantes)",
    "verin": "vérin de réglage M8 × 30, semelle plastique, 50 kg (un sous chaque montant)",
    "insert": "insert à visser M8 × 24 pour le bois (foret Ø 10), un par montant",
    "fraise": "fraise droite Ø 20 pour défonceuse (ou Ø 10 en deux passes), rainures des portes coulissantes",
    "led": "ruban LED 1,5 m 4000 K + profil alu",
    "silicone": "silicone sanitaire",
    "tirefond": "tire-fond inox 8 × 60, tête 6 pans (clé de 13) : butée du L, un par échelle du bac",
    "mousse": "mousse amortisseur adhésive 8 × 16 mm, collée sur le plateau sous chaque tire-fond",
    "tapis": "tapis antivibration 60 × 60",
    "sac": "sac en tissu",
    "E4": "barres rondes Ø 20 à 25 : manche à balai (récupération) ou tringle de rideau de 2 m (non relevée au magasin)",
    "chant": "chant thermocollant blanc 20 mm (rouleau)",
    "peinture": "peinture bois blanche microporeuse 0,5 L, pour les tasseaux (deux couches)",
}
# Achats au Weldom Saint-Barnabé : code → (désignation Weldom, prix unitaire, quantité achetée, stock, réf.) ; None :
# absent du catalogue du magasin, à acheter ailleurs. Relevé du 12/10/2026, quincaillerie de la V4 et de la V5 le 13/10/2026.
WELDOM = {
    "vis60": ("Boîte de 200 vis Standers 5 × 60", 11.50, 1, 4, "87401795"),
    "vis40": ("Boîte de 150 vis Standers 4 × 40", 9.00, 1, 3, "5618719"),
    "equerre_p": ("Équerre plate Hettich 100 mm", 1.79, 2, 13, "9154961"),
    "equerre_a": ("Lot de 6 équerres galvanisées 50 × 50 × 35", 5.95, 1, 23, "5605252"),
    "charniere_p": ("Charnière universelle acier Hettich 60 × 35", 1.79, 2, 5, "9154839"),
    "taquet": ("Lot de 20 taquets acier gris Ø 5", 5.35, 2, 4, "5567370"),
    "tapis": ("Plaque anti-vibrations Noma Rub 60 × 60 × 1", 13.50, 1, 30, "9161504"),
    "led": ("Kit ruban LED 1,5 m 4000 K (profil alu : absent)", 7.50, 1, 4, "87978094"),
    "patins": ("Lot de 2 patins glisseurs adhésifs PTFE Standers 15 × 100", 6.20, 2, None, "85066315"),
    "verin": ("Lot de 2 vérins acier Hettich M8 × 30", 4.19, 3, 6, "5572729"),
    "insert": ("Lot de 4 inserts pour pied BAR PLUS M8 × 24", 3.19, 2, 4, "96652796"),
    "sac": None,
    "toile": None,      # V5.19 : Marseille Textiles, prix dans QUINCAILLERIE["toile"]
    "E4": None,
    "chant": None,
    "peinture": ("Peinture bois Luxens int./ext. blanc satiné 0,5 L (microporeuse, à l'eau)", 17.70, 1, 13, "5620869"),
    "tirefond": ("Lot de 4 tirefonds inox tête 6 pans Standers 8 × 60", 5.60, 1, None, "5618626"),
    "mousse": ("Lot de 20 mousses amortisseur adhésif blanc 8 × 16 mm", 3.49, 1, None, "85066295"),
}
# Étapes de la notice : (titre, consigne courte, quincaillerie {code: quantité}). Les pièces de chaque étape sont celles
# dont etape == numéro ; les perçages, ceux de TROUS.
_n = lambda e, v: sum(1 for t in TROUS if t["etape"] == e and t["vis"] == v)   # noqa: E731
ETAPES = [
    ("Avant de commencer", "Faire remonter par le plombier le robinet d'arrêt dans la niche, au mur du fond, à " +
     cm_(ROBINET["z"]) + " du sol et à " + cm_(Y1 - ROBINET["y"]) + " du mur sud (relevé : 66 aujourd'hui) ; et par "
     "l'électricien la prise de la machine (circuit 20 A spécialisé) et le bloc de prises de "
     "la niche à 126. Mesurer la machine pieds réglés au plus bas : les montants se coupent à sa hauteur plus "
     f"{JEU_PLAN * 10:.0f} mm. Relever l'alcôve en trois hauteurs : garder la plus petite largeur. Les tasseaux sont en "
     "sapin brut non traité : les couper, les poncer, puis les peindre en blanc (deux couches, le bout des pieds "
     "compris) avant l'assemblage.", {"peinture": 1}),
    ("Échelles", "Assembler les trois échelles à plat sur le sol : deux montants G3, la lisse basse G4 au ras du pied "
     "des montants et la lisse haute au ras de la tête ; dans les deux échelles du bac (nord et milieu), une lisse de "
     "barre G8 juste sous la lisse haute. Deux vis 5 × 60 à travers le montant dans chaque bout de lisse, sans colle. "
     "Vérifier l'équerrage (diagonales égales), puis caler l'écharpe G11 en diagonale, du pied avant au haut arrière, "
     "et la visser en biais à chaque bout (deux vis 5 × 60) : l'échelle ne se déforme plus. Sous chaque montant, "
     "percer Ø 10 au centre du bout sur 25, passer du vernis dans le trou, visser l'insert M8 à fleur (clé six pans), "
     f"puis le vérin : régler à {PIED['h'] * 10:.0f} mm sous le bois. Les vérins se règlent ensuite sur place pour "
     "mettre le meuble de niveau.",
     {"vis60": _n(1, "vis60") + 4 * len(ECH), "insert": 2 * len(ECH), "verin": 2 * len(ECH)}),
    ("Pose, rails et butée", "Avant de dresser les échelles du bac (nord et milieu), planter dans la face intérieure "
     "de leur écharpe le tire-fond de butée : avant-trou Ø 5 de 35, à " + cm_(Z_BUTEE) + " du sol et à " +
     cm_(BAC["x_butee"] - XO0) + " du nu avant des montants, perpendiculaire à la face, puis le tire-fond 8 × 60 vissé "
     "à la clé de 13 jusqu'à ce qu'il dépasse de 25. Dresser les échelles dans l'alcôve, contre le mur "
     "du fond : une contre le mur nord, une à " + cm_(ECH["c"] - YM0) + " d'elle (place du bac), une contre le mur sud. "
     "Entre les deux premières, au sol, les rails G5 au droit des montants avant et arrière. Deux vis 5 × 60 à travers "
     "le montant du milieu dans chaque bout, et côté nord, contre le mur, une équerre plate sur les faces affleurantes "
     "du montant et du tasseau. Rien ne se fixe aux murs.", {"vis60": _n(2, "vis60"), "tirefond": _n(2, "butee"), "equerre_p": RAIL_EQUERRES, "vis16": 4 * RAIL_EQUERRES}),
    ("Le L", "Au fer à repasser, plaquer le chant blanc sur les chants coupés visibles de la porte et du plateau. Porte "
     "A6 à plat, face vers le sol : poser le plateau A3 debout contre son dos, le dessous du plateau 0,5 sous le bas de "
     "la porte, et le fixer par deux équerres d'assemblage. Couper les deux contrefiches G7 d'onglet, les poser aux "
     "bords du plateau, jambes de " + f"{BAC['contrefiche']}" + " sur la porte et sur le plateau : deux vis 4 × 40 "
     "par-dessous à travers le plateau, une équerre contre la porte (vis 4 × 16 : avec l'aile, 14 dans la porte de 18, "
     "ruban sur le foret). Percer le trou de prise Ø 25.",
     {"vis40": _n(3, "vis40"), "equerre_a": BAC_EQUERRES, "vis16": 4 * BAC_EQUERRES, "chant": 1}),
    ("Charnières et supports de la porte", "Sous le plateau, au bord avant, deux charnières plates, nœud à l'arête : "
     "une lame sous le plateau, l'autre sur le dessus du rail avant. Poser le L sur les rails, visser les lames dans le "
     "rail. Au dos de la porte, en haut, les quatre supports B1 des demi-barres de la porte, deux aux bouts et deux "
     "côte à côte au milieu (lamés, vis "
     f"4 × 16). Coller une mousse amortisseur sur le dessus du plateau, de chaque côté, à {cm_(VIS_BUTEE['mousse_pos'])} "
     "du dos de la porte et à 1 du chant latéral, sous le tire-fond. Essayer : sans les barres, le L bascule jusqu'à ce "
     "que le plateau s'appuie sous les tire-fonds, "
     f"à {BAC['angle_max']}° ; avec les sacs et les barres arrière en place (étape 7), il s'arrête à {BAC['angle']}°.",
     {"charniere_p": CHARNIERES["n"], "vis16": 4 * CHARNIERES["n"] + _n(4, "vis16l"), "mousse": 2}),
    ("Barres et sacs", "Visser les deux supports B1 des barres arrière sur les lisses de barre G8, à " +
     f"{BAC['prof']}" + " du nu avant, demi-lune en haut. Coudre les deux sacs (voir la page des plans) et enfiler chacun "
     "sur ses deux demi-barres E4. Poser les demi-barres de la porte dans leurs supports. Les demi-barres arrière se posent "
     "une fois le plan en place (étape 7), entre leur support et l'accroche centrale.",
     {"vis40": _n(5, "vis40"), "sac": 2, "toile": 1}),
    ("Machine", "Poser le tapis au sol entre les échelles du milieu et du mur sud. Raccorder la machine (le tuyau "
     f"d'arrivée monte au robinet par le passe-tuyau), la glisser sur le tapis jusqu'à {JEU_LL} du mur du fond et régler les pieds : {JEU_PLAN * 10:.0f} mm sous la tête des échelles, donc sous le plan (une cale "
     "de 5 posée sur la machine doit passer juste sous une règle posée sur les échelles).", {"tapis": 1}),
    ("Plan de travail", "Découper au chant arrière l'encoche du passe-tuyau, au droit du robinet. Le plan n'est pas "
     "hydrofuge : passer du vernis (ou du silicone) sur la coupe et l'encoche. Poser le plan D1 sur la tête des "
     "échelles. Le visser par-dessous à travers les lisses hautes : lamage Ø 10 de 10 dans la lisse, avant-trou de 12 "
     "seulement dans le plan, la vis 4 × 40 y entre de 14. Joint silicone contre les murs. Sous le plan, au milieu du "
     "bac, visser l'accroche centrale G10 (deux équerres, crochet tourné vers la porte). Poser chaque demi-barre arrière : "
     "un bout dans son support B1 (demi-lune), l'autre glissé dans le crochet puis "
     "retombé dans sa poche. Pour vider : basculer la porte (les sacs l'arrêtent à " + f"{BAC['angle']}" + "°), soulever "
     "les deux demi-barres arrière hors du crochet, laisser le L basculer jusqu'à la butée (" + f"{BAC['angle_max']}" +
     "°), puis sortir chaque sac en tenant ses deux demi-barres (l'autre sac, tant que sa barre arrière est en place, "
     "garde le L à " + f"{BAC['angle']}" + "° : lever les deux). Repousser le L fermé à la main : à vide il reste ouvert "
     "à la butée.",
     {"vis40": _n(7, "vis40l"), "silicone": 1, "equerre_a": ACCROCHE_EQUERRES, "vis16": 4 * ACCROCHE_EQUERRES}),
    ("Caisson haut", "Assembler les côtés A7, dessus et dessous A8, le montant A9, puis le fond C1 (vis 4 × 40, "
     "avant-trous). Avant l'assemblage, rainurer le dessous du dessus et le dessus du dessous A8 à la défonceuse : deux "
     f"rainures de {RAINURE['l'] * 10:.0f} de large, {RAINURE['haut'] * 10:.0f} de profondeur en haut, "
     f"{RAINURE['bas'] * 10:.0f} en bas (règle de guidage, deux passes).", {"vis40": _n(8, "vis40"), "fraise": 1}),
    ("Pose du caisson haut", "Poser le caisson haut sur deux cales de " + f"{Z_HAUT - Z_DESSUS:.1f}".replace(".", ",") +
     " sur le plan (niche). Les chevilles sont toutes au-dessus du carrelage (" + f"{CARRELAGE}" + ") : marquer à "
     "travers le fond, retirer le caisson, percer le mur nu (détecteur de câbles d'abord), cheviller selon le mur, "
     "revisser le caisson (voir « Fixer le caisson haut au mur » en tête de notice).", {"cheville": 6}),
    ("Finitions", "Étagères A10 et A11 ; portes A12 : coller les patins sous leur chant bas, les soulever dans la rainure du haut et les laisser descendre dans celle du bas ; fileur A13 ajusté au plafond, profil LED sous le caisson.",
     {"taquet": 24, "led": 1, "silicone": 1, "patins": 2}),
]
# V4.3 : les deux meubles s'achètent et se montent séparément ; les consommables forment une liste commune, achetée
# avec le meuble bas
MEUBLE_HAUT_ETAPES = (8, 9, 10)
CONSOMMABLES = ("vis60", "vis40", "vis16", "colle", "silicone", "chant")
POSE_HAUT = 9           # étape où le caisson haut monte sur ses cales (pas de nouvelle pièce)
BAC["sac"] = (f"sac en tissu à soufflet : {cm_(PATRON['largeur'])} de large, {cm_(PATRON['fond'])} de fond, "
              f"{cm_(PATRON['hauteur'])} de haut, deux fourreaux de 10 de tour pour les barres")
QUINCAILLERIE["sac"] = BAC["sac"]
_eu = lambda v: f"{v:.2f}".replace(".", ",")  # noqa: E731
QUINCAILLERIE["toile"] = (f"{cm_(TOILE['achat_m'])} m de {TOILE['nom'].lower()} pour les deux sacs, "
                          f"{_eu(TOILE['prix_m'])} € le mètre, soit {_eu(TOILE['prix'])} € ({TOILE['magasin']}, "
                          f"relevé en ligne du {TOILE['releve']})")

CHANGEMENTS = [
    ("V5.23", "13/10/2026",
     "Variante IKEA METOD du caisson haut retirée (demande client) : bouton, dessins, section et comparatif de prix ; "
     "le caisson haut est fait maison."),
    ("V5.22", "13/10/2026",
     "Butée renforcée : passé ≈ " + f"{BAC['equilibre']:.0f}" + "°, le L à vide part seul et frappe la butée (≈ " +
     cm_(VIS_BUTEE["choc"]) + " J à chaque fois) : tire-fond inox 8 × 60 (Weldom 5618626, lot de 4, 5,60 €) au lieu de "
     "la vis 5 × 60, à " + cm_(VIS_BUTEE["r"]) + " de l'axe (" + cm_(Z_BUTEE) + " du sol), et une mousse amortisseur "
     "adhésive sur le plateau à l'endroit du choc (Weldom 85066295, lot de 20, 3,49 €)."),
    ("V5.21", "13/10/2026",
     "Butée simplifiée (idée du client) : plus de taquets G6, une vis 5 × 60 plantée dans la face intérieure de chaque "
     "écharpe du bac, qui dépasse de 25 au-dessus du bord du plateau ; à 16,5 de l'axe, à 17,5 du sol, le plateau s'y "
     "appuie à " + f"{BAC['angle_max']}" + "°. Effort estimé ≈ 17 N par vis, L à vide."),
    ("V5.20", "13/10/2026",
     "Sortie du sac plein vérifiée : à " + f"{BAC['angle']}" + "°, le passage entre le haut de la porte et le chant du "
     "plan fait " + cm_(BAC["ouverture"]) + " pour un fond de sac de " + cm_(BAC["fond_sac"]) + " : il ne passe pas. "
     "Deux arrêts (idée du client) : à " + f"{BAC['angle']}" + "°, les barres (haut des soufflets coupé juste à la "
     "bouche, il se tend) ; barres arrière levées, le L bascule jusqu'à la butée, à " + f"{BAC['angle_max']}" + "° (passage "
     + cm_(BAC["ouverture_max"]) + "). La butée G6 entre les montants arrière devient deux taquets vissés sur la face "
     "intérieure des échelles du bac, de l'écharpe au montant arrière, dessous à " + cm_(Z_BUTEE) + "."),
    ("V5.19", "13/10/2026",
     "Toile des sacs chiffrée : " + cm_(TOILE["achat_m"]) + " m de toile de transat polyester 420 g/m² en 150 chez "
     "Marseille Textiles (7,20 € le mètre, " + f"{TOILE['prix']:.2f}".replace(".", ",") + " €) ; ajoutée aux achats ailleurs et au comparatif "
     "L basculant / bacs à roulettes."),
    ("V5.18", "13/10/2026",
     "Variante bacs à roulettes sans porte (client) : les deux paniers affleurent presque le nu du plan, plus de "
     "charnières invisibles ; Wenko Corno à 45 € pièce (Amazon, relevé client) au lieu de 86,95 €."),
    ("V5.17", "13/10/2026",
     "Variante « bacs à roulettes » (bouton Linge sale en haut de page, toutes les vues) : deux paniers étroits à "
     "roulettes Wenko Corno 18,5 × 40 × 60 (43 L) roulés côte à côte à la place du L basculant ; rail avant, butée, "
     "plateau, contrefiches, supports, barres, accroche et sacs supprimés ; porte A6 jusqu'en bas, sur deux charnières "
     "invisibles au montant de l'échelle du milieu, ouverture vers la machine."),
    ("V5.16", "13/10/2026",
     "Épaisseur du carrelage prise en compte : au-dessus de 204, le mur nu est en retrait du carreau (≈ " +
     cm_(EP_CARRELAGE) + ", à mesurer) ; le caisson haut s'appuie sur le carreau en bas et sur une cale de cette "
     "épaisseur derrière chaque cheville en haut, vis 6 × 70. Porte du linge rétrécie de " + cm_(CHAMBRANLE + 0.3 - 0.45) +
     " côté nord : le chambranle de la porte d'entrée déborde de 0,5 du mur et la porte passe devant en basculant."),
    ("V5.15", "13/10/2026",
     "Pieds : un vérin M8 Hettich (semelle plastique) sous chacun des six montants, vissé dans un insert M8 au bout du "
     "montant ; le bois est à " + f"{PIED['h'] * 10:.0f}" + " mm du carrelage (l'eau ne le touche pas) et les vérins "
     "rattrapent le niveau du sol. Le plan reste à la même hauteur (montants raccourcis d'autant). Notice : outils "
     "par meuble, et méthode pour fixer le caisson haut au mur."),
    ("V5.14", "13/10/2026",
     "Ossature consolidée avec les tasseaux en rab des deux lots : une écharpe G11 en diagonale dans chacune des trois "
     "échelles (du pied avant au haut arrière, vissée en biais) ; plus de déformation d'avant en arrière, sans achat en "
     "plus. Accroche centrale dessinée avec son crochet en J et ses équerres ; « barres fixes » renommées « barres "
     "arrière » (on les enlève)."),
    ("V5.13", "13/10/2026",
     "Les deux sacs se retirent indépendamment : chaque barre est coupée en deux demi-barres, une par sac. Au milieu, "
     "deux supports B1 côte à côte au dos de la porte, et une accroche centrale G10 pendue sous le plan (bout de "
     "tasseau, crochet ouvert vers la porte) pour les demi-barres arrière. Sacs de " + cm_(BAC["largeur_sac"]) +
     " de large (≈ " + f"{VOLUME_BAC:.0f}" + " L) pour laisser passer l'accroche."),
    ("V5.12", "13/10/2026",
     "Meuble à linge sale aussi profond que la machine : l'ossature va jusqu'à son dos (" + cm_(X1 - XO1) + " du mur du "
     "fond, 16 avant). Plateau du L recalculé à " + cm_(BAC["plateau"]) + ", butée à " + cm_(BAC["coin"][1]) + " ; sacs de ≈ " +
     f"{VOLUME_BAC:.0f}" + " L."),
    ("V5.11", "13/10/2026",
     "Porte d'entrée replacée : porte standard de 73 (76 avant), gonds à 69 du mur du fond (relevé client ; 77 dessinés "
     "avant). Vantail ouvert à 90° à " +
     cm_(FACE - (X1 - GONDS)) + " devant la façade du meuble."),
    ("V5.10", "13/10/2026",
     "Meuble bas de 60 de profondeur au plus, collé au mur du fond (client) : plan de 60 contre le mur (recoupé dans le "
     "1800 × 640), façade à 60 du fond (65,9 avant) ; il tient dans le mur nord de 62. Plateau du L raccourci à " +
     cm_(BAC["plateau"]) + " pour buter au même angle. La niche garde toute la profondeur du plan (60) sous le caisson "
     "haut de 45."),
    ("V5.9", "13/10/2026",
     "Murs de retour de l'alcôve dessinés sur le plan : 62 au nord (porte), 68 au sud (lavabo) ; le bout du mur sud "
     "passe à 166 (167). Plan de travail : stratifié chêne clair conservé."),
    ("V5.8", "13/10/2026",
     "Le carrelage s'arrête à 204 (relevé client) : les six chevilles du caisson haut passent au-dessus, dans le mur "
     "nu (deux rangées à 210 et 240) ; plus aucun perçage dans le carrelage. Variante METOD : le rail de suspension, en "
     "haut des structures, est lui aussi au-dessus du carrelage."),
    ("V5.7", "13/10/2026",
     "Robinet d'arrêt remonté dans la niche, au-dessus du plan (" + cm_(ROBINET["z"]) + " du sol, 41 du mur sud) : plus "
     "de trappe ni de couvercle ; une encoche au chant arrière du plan laisse passer le tuyau. La machine recule à " +
     f"{JEU_LL}" + " du mur du fond."),
    ("V5.6", "13/10/2026",
     "Mesures relevées sur place : alcôve de 115 de large au fond (114), murs de retour de 62 au nord et 68 au sud ; "
     "machine de 59,5 × 53 × 85 (60 × 60 × 85) ; robinet d'arrêt à 66 de haut et à 41 du mur sud, donc derrière la "
     "machine : la trappe du plan est déplacée au-dessus, ses tasseaux de feuillure derrière la machine."),
    ("V5.5", "13/10/2026",
     "Plan de travail en décor chêne clair (Weldom 5634115, même format 1800 × 640 × 28 et même prix, 36,50 €) au lieu "
     "du blanc ; non hydrofuge : coupe et chants du trou de trappe vernis ou siliconés."),
    ("V5.4", "13/10/2026",
     "Portes coulissantes du caisson haut sans kit : deux rainures à la défonceuse dans le dessus et le dessous (12 et "
     "5 de profondeur), les portes glissent dedans sur des patins PTFE (2 lots à 6,20 €) au lieu d'un kit à 99,90 €. "
     "Variante METOD : deux bandeaux rainurés vissés sous et sur les structures. Ossature peinte en blanc (Luxens 0,5 L)."),
    ("V5.3", "13/10/2026",
     "Ossature en sapin brut non traité 38 × 38 (lots de 6 × 2 m, 23,60 € le lot) au lieu de l'autoclave 36 × 36 : "
     "pas de bois humide, pas de produit de traitement ; les tasseaux sont peints ou vernis (pieds compris) avant "
     "l'assemblage. Toutes les cotes de l'ossature suivent (+ 2 mm par tasseau). Index : cuisine et salon sans numéro "
     "de version ; comparatif de prix fait maison / METOD en tableau."),
    ("V5.2", "13/10/2026",
     "Variante du caisson haut en IKEA METOD (bouton en haut de page, toutes les vues) : deux structures « rangement "
     "mural » 60 × 37 × 80 sur rail de suspension, celle de la pharmacie recoupée à 53 ; même dessous qu'en fait "
     "maison (niche identique), fileur de 12 ; tablettes UTRUSTA ; portes coulissantes en applique (kit de meuble à "
     "rails clipsés, deux portes de 18 en mélaminé). Index : titre sans numéro de version."),
    ("V5.1", "13/10/2026",
     "Bac basculant revu (correction client) : le L se limite à la porte A6 et au plateau A3, tenus par deux "
     "contrefiches G7 en tasseau à 45° aux bords du plateau ; plus de côtés, dos ni cloison. La butée G6 n'est plus "
     "sous le plan : c'est un tasseau entre les montants arrière des échelles du bac, sous lequel vient buter l'arrière "
     "du plateau ; sa hauteur (" + cm_(BAC["coin"][1]) + ") fixe l'angle (" + f"{BAC['angle']}" + "°). Les deux sacs à "
     "soufflet, côte à côte, pendent de nouveau entre deux barres rondes : celle de la porte dans deux supports B1 au "
     "dos de la porte, la barre fixe, amovible, dans deux supports sur des lisses de barre G8 sous le plan ; leur fond "
     "repose sur le plateau. ≈ " + f"{VOLUME_BAC:.0f}" + " L par sac."),
    ("V5.0", "13/10/2026",
     "Contre-analyse du meuble bas (coûts et simplicité). Machine posée au sol : plus de socle (longerons, traverses, "
     "plateau, tasseau d'embase), plan à " + cm_(Z_DESSUS) + " (93,7 en V4.4), niche de " + cm_(Z_HAUT - Z_DESSUS) +
     ". Trois échelles debout sur le carrelage (lisse basse + lisse haute), deux rails au sol entre les échelles du "
     "caisson. Un seul bac basculant au lieu de deux portes : porte et fond en L, deux côtés, un dos et une cloison, "
     "deux sacs souples côte à côte (≈ " + f"{VOLUME_BAC:.0f}" + " L chacun) ; deux charnières plates entre le rail "
     "avant et le fond au lieu de quatre charnières invisibles (plus de mèche Forstner) ; le dos s'arrête contre une "
     "butée vissée sous le plan à " + f"{BAC['angle']}" + "°, le bac retombe fermé tout seul. Plus de tablette, de "
     "barres, de supports ni de lisses de barre ; sacs droits à rabat élastiqué. Plus de colle dans l'ossature. "
     "État V4.4 gardé dans git stash."),
    ("V4.4", "13/10/2026",
     "Tablette sans entaille : un rectangle posé sur les lisses du milieu, entre les montants ; devant elle, une "
     "traverse d'embase G9 entre les deux montants avant porte avec elle les charnières de la porte du sac 2. Supports "
     "B1 avec une demi-lune Ø 25 (mèche plate) où la barre se pose. Trappe carrée de 11 affleurante, "
     "découpée à la scie sauteuse derrière les sacs côté machine, couvercle taillé dans la chute du plan, posé sur deux "
     "tasseaux en feuillure, trou de doigt ; robinet déplacé dessous."),
    ("V4.3", "13/10/2026",
     "Plus de cadre haut : le plan est posé sur la tête des trois échelles et vissé dans les lisses hautes (dessus à " +
     cm_(Z_DESSUS) + "). Plus d'équerres renforcées au socle (assemblages collés et vissés, alcôve fermée sur trois "
     "côtés). Trois sortes de vis seulement : 5 × 60 (tasseaux), 4 × 40 (panneaux, plan avec lamage), 4 × 16 "
     "(charnières, équerres plates, supports des portes avec lamage). Lisses de barre collées. Meubles bas et haut "
     "séparés : débit, achats (consommables communs, achat du bas, puis du haut dans les chutes du bas) et notice ; "
     "plans de chaque sous-ensemble avec ses pièces cotées et percées."),
    ("V4.2", "13/10/2026",
     "Ossature en tasseaux de sapin traité autoclave classe III 36 × 36 (lots de 6 × 2 m, seul classe 3 en stock au "
     "Weldom) au lieu de la traverse douglas 33 × 66 : socle de 5,4, plan à 97,3 (100 en V4.1). Dans les échelles du caisson, une lisse de barre G8 sous chaque lisse porte les supports des barres. "
     "Plan vissé en 4 × 50. Débit et calepinage : code couleur meuble bas / caisson haut."),
    ("V4.1", "13/10/2026",
     "Liste allégée. Plus de plateau sous les sacs (S1) : le sac pend ; le plateau ne reste que sous la machine, "
     "entaillé autour des montants, qui reposent sur le cadre du socle. Plus de joue côté machine (A20) : le caisson "
     "gagne 1,8 de large (sac de 37,7). Plus de plinthe (S3) : le longeron avant du socle, "
     "avancé au nu de l'ossature, fait plinthe (retrait de 1,8) et porte, avec un tasseau d'embase taillé dans une "
     "chute, les charnières de la porte du bas. Plus de compas : le haut des soufflets du sac, tendu porte ouverte, "
     "arrête la porte. Plus d'équerres plates au cadre haut (le plan le tient), elles passent au pied des montants. "
     "Plus de vis Direkta (vis 4 × 40) ni de poignées (trou de prise Ø 25)."),
    ("V4.0", "13/10/2026",
     "Meuble bas refait de zéro pour la rigidité. Socle commun au caisson et à la machine : cadre en traverses douglas "
     "33 × 66 sur chant, une équerre renforcée dans chaque angle, plateau en mélaminé, plinthe devant seulement ; "
     "dessus du socle à 8,4. Trois échelles en douglas (montants, lisse au milieu, lisse haute) et un "
     "cadre haut à plat, renforcé aux angles, sur lequel le plan est posé : la machine passe dessous à "
     "5 mm, dessus du plan à 100. Joue en mélaminé côté machine, tablette entaillée "
     "autour des montants. Barre fixe à 20 du nu avant (au lieu de 30) : les barres sont plus proches "
     "porte fermée ; sac à soufflet, patron et couture sur la page. Charnières invisibles Ø 35 au lieu de la "
     "charnière piano. Notice : tous les perçages dessinés et cotés, étape par étape. Douglas, quincaillerie et "
     "prix relevés au Weldom le 13/10/2026."),
    ("V3.9", "12/10/2026",
     "Côtés du caisson bas en ossature, comme la joue : montant avant de 10, montant arrière de 6, une lisse basse et "
     "deux lisses hautes (sous la tablette et sous le plan) qui portent les supports arrière des barres ; tout en "
     "chutes. Traverses A4 inchangées : les prolonger jusqu'à la joue n'apporte rien (voir Explications)."),
    ("V3.8", "12/10/2026",
     "Machine à droite seulement : la version à gauche est abandonnée. Joue côté machine en ossature (deux montants, "
     "deux traverses de 6 taillés dans les chutes) au lieu d'un panneau plein. Trappe déplacée derrière le "
     "caisson bas (raccourci de 5, fond à 16 du mur) : le disque repose sur deux tasseaux A16 collés sous le plan, "
     "taillés dans les chutes ; plus de plaque à acheter. Le robinet d'arrêt se pose dessous. Volume des sacs calculé "
     "sur leur section réelle (trapèze) au lieu d'une boîte."),
    ("V3.7", "12/10/2026",
     "Le plan de travail ne se fixe plus aux murs : tasseaux E1 et cornière E2 supprimés. Il repose sur le caisson bas "
     "et sur une joue A14 posée au sol contre le mur côté machine, et s'y visse par-dessous. Pour garder " +
     "61,2 à la machine, le caisson bas passe de 52,5 à 50,4 de large. Le meuble bas ne touche plus aux murs (silicone "
     "seulement) ; le disque de la trappe repose sur deux plaques de jonction plates en acier."),
    ("V3.6", "12/10/2026",
     "Simplifications. Caisson bas sans fond (C2 supprimé). Socle de la machine réduit à un plateau sur deux cales "
     "posées sur chant et une plinthe en façade, en retrait comme celle du caisson : on garde la place des pieds devant "
     "la machine au plan de travail ; rebords supprimés. Trappe du robinet percée à la scie cloche Ø " +
     "114 : le disque découpé sert de couvercle. Barres des sacs rondes (manche à balai coupé ou "
     "tringle de rideau, Ø 22) au lieu du tasseau 20 × 40."),
    ("V3.5", "12/10/2026",
     "Socle de la machine abaissé de 20 à 10 : plan de travail à 99,3 (au lieu de 109,3), niche de 58,7. Tablette du caisson bas "
     "placée pour que les deux façades des sacs aient exactement la même hauteur (" +
     "42)."),
    ("V3.4", "12/10/2026",
     "Placards du haut réduits à 90 de haut (au lieu de 96) : toujours jusqu'au plafond, le dessous remonte à 158 ; "
     "la niche passe à 48,7 de haut."),
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
     "(dessus à 109,3, 1,9 de jeu au fond) ; tasseaux 44 × 27 à plat ; fond du caisson haut en deux moitiés. "
     "Nouvelle section Achats : calepinage des tablettes et liste de courses avec prix et stock."),
    ("V3.0", "12/10/2026",
     "Nouvelle page générée depuis 3d/sdb/modele.py (plan, élévation, coupes, débit, modèle FreeCAD, notice de montage). "
     "Machine surélevée de 20 sur un socle plein en contreplaqué 22 ; plan de travail remonté de 90 à 109,5 ; niche "
     "109,5 → 152 ; caisson haut 152 → 248. Paniers : les deux tiroirs "
     "coulissants à fente sont remplacés par deux bacs basculants superposés sur toute la largeur (plus de fente, de volet "
     "ni de goulotte)."),
    ("V2.2", "01/10/2026", "Mise en page : notes en fin de document (archive/sdb-meuble-v2.html)."),
    ("V2.1", "01/10/2026", "Fentes à linge dans les façades des tiroirs ; trappe du robinet centrée sur le meuble."),
    ("V2", "01/10/2026", "Base P1 « Plan de pliage », plan filant, deux tiroirs-paniers, trappe, hauts P 45 jusqu'au "
     "plafond, deux versions machine à droite / à gauche."),
    ("V1", "30/09/2026", "Trois propositions (archive/sdb-meuble-v1.html)."),
]
