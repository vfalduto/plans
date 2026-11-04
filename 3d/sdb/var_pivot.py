# Variante 1 du meuble bas : la porte en L du meuble actuel, sur un axe pivotant au lieu des deux charnières plates.
#
# Module lu par variantes.py (contrat : ID, TITRE, RESUME, section(), FICHE). Il ne modifie rien dans modele.py : il en
# reprend l'alcôve, les échelles, le rail avant, les barres, les supports, l'accroche, le plan, la machine et les tuyaux,
# et redécrit ici ce que l'axe change : la porte, le plateau, les contrefiches, le rail arrière, les sacs et la butée.
#
# Demande du client (01/11/2026) : « on reprend la porte de base mais il faut améliorer le pivot, la charnière ne
# convient pas, on partirait plus sur un axe mobile sur lequel est accroché la porte et le bas ».
#
# Principe retenu : un tube rond en aluminium traverse l'espace entre les deux montants avant des échelles du bac et
# tourne dans un trou percé dans chacun d'eux (borgne au nord, contre le mur ; traversant au milieu, côté machine). Le
# plateau du L est posé sur le tube, dans une rainure peu profonde faite à la défonceuse, et vissé dessus par trois vis
# à tôle données depuis l'intérieur du bac : le tube et le L tournent ensemble, les montants sont les paliers.
# Deux bouts de tasseau de lest à l'arrière du plateau rendent au L vide son retour seul depuis 20° (l'axe est 1,9 plus
# en arrière que l'ancienne charnière).
#
# Cotes en cm, repère de modele.py : x vers l'est (mur du fond à 234), y vers le sud, z depuis le sol.

import math
import os
import sys
from html import escape

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import modele as M  # noqa: E402
import plan as PL  # noqa: E402
import cotes as CO  # noqa: E402
import montage as MO  # noqa: E402

ID = "pivot"
TITRE = "Variante 1 · Porte en L sur un axe pivotant"
RESUME = ("La porte en L du meuble actuel, sans charnières : elle est vissée sur un tube en aluminium de 16 qui tourne "
          "dans deux trous percés dans les montants avant des échelles.")

cm, f = PL.cm, PL.f
T, DL, DE = M.T, M.DL, M.DE
G = 9.81

# ------------------------------------------------------------------ l'axe et ses paliers
# Tube rond aluminium brut Ø 16 × 1 (Castorama 3232630508800, 7,19 € le mètre, prix lu en ligne le 01/11/2026, stock
# non lu ; existe aussi chez Brico Dépôt). L'aluminium ne rouille pas près de la machine et du linge humide.
TUBE = dict(d=1.6, ep=0.1, prix=7.19, nom="tube rond aluminium brut Ø 16 × 1 mm, 1 m",
            source="Castorama, réf. 3232630508800, prix lu en ligne le 01/11/2026 (stock non lu)")
TROU = 1.62             # mèche plate Ø 16 : le trou sort à 16 à 16,5 dans le sapin (le tube doit tourner à la main)
BORGNE = 2.0            # profondeur du trou nord (montant contre le mur) ; il reste 1,8 de bois côté mur
RECUL_SUD = 0.6         # le bout sud du tube reste 0,6 en retrait de la face du montant du milieu (machine à 0,6)
_r, _rt = TUBE["d"] / 2, TROU / 2
XA = M.XO0 + DL / 2     # l'axe au milieu de l'épaisseur des montants avant : 177,7
D_AV = XA - M.XO0       # recul de l'axe derrière le dos de la porte : 1,9
_en, _ec = M.ECHELLES["n"], M.ECHELLES["c"]
_yi0, _yi1 = M._yi0, M._yi1                     # faces intérieures des montants du bac : 4,1 et 46,4
_yp0, _yp1 = M._yp0, M._yp1                     # plateau : 0,5 de jeu de chaque côté (inchangé)
_ymb = (_yp0 + _yp1) / 2
Y_TUBE = (_yi0 - BORGNE, _ec["av"].y1 - RECUL_SUD)   # 2,1 → 49,6
TUBE["L"] = Y_TUBE[1] - Y_TUBE[0]

# rainure sous le plateau, à la défonceuse (fraise droite Ø 10) : le tube repose sur ses deux arêtes, ce qui le place
# exactement d'avant en arrière ; la flèche est ce dont il s'enfonce
RAINURE = dict(l=1.0, p=0.2)
FLECHE = _r - math.sqrt(_r ** 2 - (RAINURE["l"] / 2) ** 2)          # 0,18
assert RAINURE["p"] > FLECHE, "le tube porte sur les arêtes de la rainure, pas au fond"
H_PLAT = _r - FLECHE    # dessous du plateau au-dessus de l'axe : 0,62

# vis de blocage : vis à tôle tête fraisée 4,2 × 25, du dessus du plateau, au fond de la rainure, dans la paroi
# supérieure du tube (avant-trou Ø 3,5 percé à travers le trou du plateau, tube en place)
VIS_AXE = dict(n=3, d=0.42, L=2.5, nom="vis à tôle tête fraisée 4,2 × 25", ys=(_ymb - 15.5, _ymb, _ymb + 15.5))
assert T - RAINURE["p"] + (RAINURE["p"] - FLECHE) + TUBE["ep"] < VIS_AXE["L"] < T - RAINURE["p"] + TUBE["d"] - TUBE["ep"], \
    "la vis prend la paroi du dessus du tube sans toucher celle du dessous"
assert VIS_AXE["ys"][0] - VIS_AXE["d"] > _yp0 + DE + 0.8, "les vis passent à côté des contrefiches"

# ------------------------------------------------------------------ position de l'axe
# Trois contraintes, la plus haute gagne :
#   - le trou du palier passe au-dessus de l'insert du vérin (Ø 10, 25 de profondeur sous le montant) avec 1 de bois ;
#   - le tube passe au-dessus du rail avant (gardé : il lie les échelles en bas) ;
#   - le coin avant du dessous du plateau, devant l'axe, descend quand le L bascule : il reste JEU_RAIL au-dessus du
#     rail avant jusqu'à la butée.
# L'angle de la butée dépend lui-même de l'axe (ouverture pour sortir un sac plein) : on itère.
Z_INSERT = M.Z0 + 2.5
BOIS = 1.0
JEU_RAIL = 0.3
RAIL_H = M.RAILS[0].z1                          # dessus du rail avant : 5,8
ANGLE = M.BAC["angle"]                          # 20° : les soufflets des sacs arrêtent le L (inchangé)
MARGE_SAC = M.MARGE_SAC
_xf0, _xr0, _zb0, _zb1 = M.BAC["barres"]
_bx = M.BAC["barre"][0]
_xs1 = M.XO1 - DL - 1
FOND_SAC = _xs1 - (_xf0 + 1)                    # fond du sac : inchangé (46,2)
Z_HAUT_PORTE = M.PORTE_BAC.z1                   # le haut de la porte ne change pas (0,3 sous le plan)


def ouverture(a, axe):
    """Passage entre le haut du dos de la porte, basculée de a degrés autour de axe, et le chant avant du plan."""
    x, z = M.bascule(M.XO0, Z_HAUT_PORTE, axe, a)
    return math.hypot(M.FACE - x, M.Z_PLAN - z)


def _za(a_max):
    chute = max(D_AV * math.sin(math.radians(k / 2)) - H_PLAT * math.cos(math.radians(k / 2))
                for k in range(0, 2 * a_max + 1))
    z = max(Z_INSERT + BOIS + _rt, RAIL_H + JEU_RAIL + _r, RAIL_H + JEU_RAIL + chute)
    return math.ceil(z * 10 - 1e-9) / 10


ZA = _za(40)
for _ in range(4):
    A_MAX = next(a for a in range(ANGLE, 90) if ouverture(a, (XA, ZA)) >= FOND_SAC + MARGE_SAC)
    ZA = _za(A_MAX)
AXE = (XA, ZA)
A_MAX = next(a for a in range(ANGLE, 90) if ouverture(a, AXE) >= FOND_SAC + MARGE_SAC)
assert ZA == _za(A_MAX)
ZP = ZA + H_PLAT                                # dessous du plateau
DZ = ZP - M._zp                                 # le plateau monte de tant par rapport au meuble actuel

# bas de la porte : son dos passe devant les montants (qu'elle recouvre de chaque côté) jusqu'à la butée, avec JEU_PORTE.
# Un point du dos de la porte à w au-dessus de l'axe recule de D_AV(1 − cos a) et avance de w·sin a.
JEU_PORTE = 0.15
_am = math.radians(A_MAX)
_w = (JEU_PORTE + D_AV * (1 - math.cos(_am))) / math.sin(_am)
Z_BAS_PORTE = math.ceil((ZA + _w) * 10 - 1e-9) / 10
assert ZP <= Z_BAS_PORTE < ZP + T, "la porte couvre le chant avant du plateau"


def jeu_porte(a):
    """Écart entre le dos du bas de la porte et la face avant des montants, porte basculée de a degrés."""
    return M.XO0 - M.bascule(M.XO0, Z_BAS_PORTE, AXE, a)[0]


assert all(jeu_porte(k / 2) >= -1e-9 for k in range(0, 2 * A_MAX + 1)), "le bas de la porte ne recule pas dans les montants"
assert jeu_porte(A_MAX) >= JEU_PORTE - 1e-9

# ------------------------------------------------------------------ pièces de la variante
P0 = M.PORTE_BAC
PORTE = M.Bloc("facade", "pv_porte", M.FACE, M.XO0, P0.y0, P0.y1, Z_BAS_PORTE, Z_HAUT_PORTE, rep="A6", groupe="bac",
               etiq="Linge sale")
PLATEAU = M.Bloc("bac", "pv_plateau", M.XO0, M.XO0 + M.BAC["plateau"], _yp0, _yp1, ZP, ZP + T, rep="A3", groupe="bac")
_zc = ZP + T
_L, _d = M.BAC["contrefiche"], DL * math.sqrt(2)
CONTREFICHES = [M.Profil("bois", f"pv_contrefiche_{k}", [(M.XO0, _zc + _L), (M.XO0, _zc + _L - _d),
                                                       (M.XO0 + _L - _d, _zc), (M.XO0 + _L, _zc)], y0, y0 + DE,
                         rep="G7", groupe="bac") for k, y0 in (("n", _yp0), ("s", _yp1 - DE))]
TUBE_P = M.Profil("barre", "pv_axe", M.rond(XA, ZA, _r, 20), Y_TUBE[0], Y_TUBE[1], rep="E5", groupe="bac")
# rail arrière : même pièce G5, remontée de DZ pour porter le plateau fermé (vissée plus haut dans les montants arrière)
_ra = M.RAILS[1]
RAIL_AR = M.replace(_ra, nom="pv_rail_ar", z0=_ra.z0 + DZ, z1=_ra.z1 + DZ)
assert RAIL_AR.z1 == PLATEAU.z0
# ses deux vis 5 × 60 traversent le montant arrière du milieu à mi-hauteur du rail : au-dessus de l'insert du vérin
assert (RAIL_AR.z0 + RAIL_AR.z1) / 2 - 0.25 - Z_INSERT > 0.5, "les vis du rail arrière passent au-dessus de l'insert"
# pièces reprises telles quelles : sur la porte (supports, barres de porte) ou fixes
_pc = {b.nom: b for b in M.PIECES}
SUR_PORTE = [_pc[n] for n in ("support_porte_n", "support_porte_cn", "support_porte_cs", "support_porte_s",
                              "barre_porte_n", "barre_porte_s")]
assert all(b.z0 > Z_BAS_PORTE for b in SUR_PORTE), "les supports de la porte restent sur la porte raccourcie"
MOBILES = [PORTE, PLATEAU] + CONTREFICHES + SUR_PORTE           # le L et ce qu'il porte (sans le tube) ; + le lest


def lest(n):
    """Lest : n tasseaux (chutes) empilés à plat sur l'arrière du plateau, derrière les sacs. L'axe, au milieu des
    montants, est 1,9 plus en arrière que l'ancienne charnière : sans lest, le L vide ne se referme plus seul depuis 20°."""
    return [M.Bloc("bois", f"pv_lest_{k + 1}", PLATEAU.x1 - DE, PLATEAU.x1, _yp0, _yp1, ZP + T + k * DL,
                   ZP + T + (k + 1) * DL, rep="G13", groupe="bac") for k in range(n)]


REMPLACEES = {"plateau", "bac_porte", "contrefiche_n", "contrefiche_s", "rail_ar", "butee_vis_n", "butee_vis_c",
              "support_porte_n", "support_porte_cn", "support_porte_cs", "support_porte_s", "barre_porte_n",
              "barre_porte_s"}
FIXES_M = [b for b in M.PIECES if b.groupe != "caisson_haut" and b.nom not in REMPLACEES]

# sacs : même découpe, fond posé sur le plateau remonté (DZ de moins en hauteur)
_ys = (_yp0 + DE + 0.3, _yp1 - DE - 0.3)
_gap = DL + 1.0
_wl = (_ys[1] - _ys[0] - _gap) / 2
SACS = [M.Profil("sac", f"pv_sac_{k + 1}", [(_xf0, _zb0 + 1), (_xr0 + _bx, _zb0 + 1), (_xs1, _zc + 1), (_xf0 + 1, _zc + 1)],
                 _ys[0] + k * (_wl + _gap), _ys[0] + k * (_wl + _gap) + _wl, groupe="bac") for k in range(2)]


def aire(pts):
    return abs(sum(x0 * z1 - x1 * z0 for (x0, z0), (x1, z1) in zip(pts, pts[1:] + pts[:1]))) / 2


VOLUME_SAC = aire(SACS[0].xz) * _wl / 1000
H_SAC = _zb0 + 1 - (_zc + 1)


def tourne(b, a):
    """La pièce b du L basculée de a degrés autour de l'axe (Profil dans le plan x-z)."""
    if not a:
        return b
    pts = b.xz if isinstance(b, M.Profil) else b.pts("y")
    return M.Profil(b.role, b.nom, [M.bascule(x, z, AXE, a) for x, z in pts], b.y0, b.y1, rep=b.rep, groupe=b.groupe,
                    etiq=b.etiq)


def sac_ouvert(s, a):
    """Sac tendu entre la barre de la porte basculée, la barre arrière fixe et le plateau basculé."""
    fa = M.bascule(_xf0 + _bx, _zb0 + 1, AXE, a)
    fb = M.bascule(_xs1, _zc + 1, AXE, a)
    fc = M.bascule(_xf0 + 1, _zc + 1, AXE, a)
    return M.Profil("sac", s.nom, [fa, (_xr0 + _bx, _zb0 + 1), fb, fc], s.y0, s.y1, groupe="bac")


# ------------------------------------------------------------------ ouverture, bouche, butée
_bo = M.bascule(_xf0, _zb1, AXE, ANGLE)
BOUCHE = _xr0 - _bo[0]                          # entre les barres, à 20° : longueur du haut des soufflets
assert _bo[1] < M.Z_PLAN, "la barre de la porte passe sous le plan"
OUV = ouverture(ANGLE, AXE)
OUV_MAX = ouverture(A_MAX, AXE)
assert OUV < FOND_SAC, "à 20°, un sac plein ne sort pas : d'où la butée plus loin (comme le meuble actuel)"
AVANCE = M.FACE - M.bascule(M.FACE, Z_HAUT_PORTE, AXE, ANGLE)[0]
AVANCE_MAX = M.FACE - M.bascule(M.FACE, Z_HAUT_PORTE, AXE, A_MAX)[0]
Z_HAUT_20 = M.bascule(M.XO0, Z_HAUT_PORTE, AXE, ANGLE)[1]
SOL_MAX = M.bascule(M.FACE, Z_BAS_PORTE, AXE, A_MAX)[1]          # coin avant bas de la porte à la butée
assert SOL_MAX > 0.5 + M.Z0, "le bas de la porte reste loin du sol"
RAIL_MAX = min(M.bascule(M.XO0, ZP, AXE, k / 2)[1] for k in range(0, 2 * A_MAX + 1)) - RAIL_H
assert RAIL_MAX >= JEU_RAIL - 1e-9, "le plateau ne touche pas le rail avant"

# butée : tire-fond inox 8 × 60 planté dans la face intérieure de l'écharpe de chaque échelle du bac (même idée que le
# meuble actuel), recalculé pour l'axe : à R de l'axe, le plateau vient s'appuyer dessous à A_MAX (mousse de 3 mm).
VB = M.VIS_BUTEE
_rv = VB["d"] / 2
_H_TOP = H_PLAT + T                             # dessus du plateau au-dessus de l'axe, dans le repère du L
_cf1, _cf2 = CONTREFICHES[0].xz[1], CONTREFICHES[0].xz[2]
_ech_n = next(e for e in M.ECHARPES if e.nom == "echarpe_n")


def _dist_cf(phi):
    x1, z1, x2, z2 = _cf1[0] - XA, _cf1[1] - ZA, _cf2[0] - XA, _cf2[1] - ZA
    c, s_ = math.cos(phi), math.sin(phi)
    return (x1 * (z1 - z2) - z1 * (x1 - x2)) / (c * (z1 - z2) - s_ * (x1 - x2))


def _butee(r):
    ph0 = math.asin((_H_TOP + VB["mousse"] + _rv) / r)
    psi = math.radians(A_MAX) + ph0
    x, z = XA + r * math.cos(psi), ZA + r * math.sin(psi)
    av, ar = M._bords(_ech_n, z)
    mc = min(_dist_cf(ph0 + k * (psi - ph0) / 50) for k in range(51)) - r - VB["tete"] / 2
    return x, z, (x - av - _rv, ar - x - _rv, mc)


R_BUTEE = max((r / 10 for r in range(100, 260)), key=lambda r: min(_butee(r)[2]))
X_BUTEE, Z_BUTEE, MARGES_BUTEE = _butee(R_BUTEE)
assert min(MARGES_BUTEE) >= VB["marge_min"], MARGES_BUTEE
BUTEES = []
for nom, y0, sy in (("n", _yi0, 1), ("c", _yi1, -1)):
    y1 = y0 + sy * VB["depasse"]
    BUTEES.append(M.Bloc("vis", f"pv_butee_{nom}", X_BUTEE - _rv, X_BUTEE + _rv, min(y0, y1), max(y0, y1),
                         Z_BUTEE - _rv, Z_BUTEE + _rv, groupe="ossature"))
assert min(_yp1, BUTEES[0].y1) - max(_yp0, BUTEES[0].y0) >= 1.5, "le tire-fond passe au-dessus du plateau sur 1,5 au moins"
FIXES = FIXES_M + [RAIL_AR] + BUTEES
EQUIP = [M.MACHINE, M.SIPHON, M.ARRIVEE]

# ------------------------------------------------------------------ vérification : rien ne se traverse
# Toutes les pièces du L (et ce qu'il porte), basculées de 0 à A_MAX par demi-degré, contre toutes les pièces fixes et la
# machine qui partagent leur tranche en y : polygones convexes dans le plan x-z, séparés (contact permis).


def _env(pts):
    p = sorted(set(pts))
    if len(p) < 3:
        return p

    def cr(o, a, b):
        return (a[0] - o[0]) * (b[1] - o[1]) - (a[1] - o[1]) * (b[0] - o[0])
    bas, haut = [], []
    for q in p:
        while len(bas) >= 2 and cr(bas[-2], bas[-1], q) <= 0:
            bas.pop()
        bas.append(q)
    for q in reversed(p):
        while len(haut) >= 2 and cr(haut[-2], haut[-1], q) <= 0:
            haut.pop()
        haut.append(q)
    return bas[:-1] + haut[:-1]


def _separes(p, q, tol=0.005):
    for poly in (p, q):
        for (x0, z0), (x1, z1) in zip(poly, poly[1:] + poly[:1]):
            n = (z0 - z1, x1 - x0)
            a = [n[0] * x + n[1] * z for x, z in p]
            b = [n[0] * x + n[1] * z for x, z in q]
            ln = math.hypot(*n) or 1
            if max(a) <= min(b) + tol * ln or max(b) <= min(a) + tol * ln:
                return True
    return False


def collisions():
    fixes = [b for b in FIXES + EQUIP if b.role not in ("pied",)]
    r = []
    for k in range(0, 2 * A_MAX + 1):
        a = k / 2
        for m_ in MOBILES:
            pm = _env(tourne(m_, a).pts("y") if a else m_.pts("y"))
            for b in fixes:
                if min(m_.y1, b.y1) - max(m_.y0, b.y0) <= 0.01:
                    continue
                if not _separes(pm, _env(b.pts("y"))):
                    r.append((a, m_.nom, b.nom))
    return r


# le tube ne touche que les montants avant (ses paliers) ; il passe au-dessus du rail avant et des inserts
assert ZA - _r - RAIL_H >= JEU_RAIL - 1e-9 and ZA - _rt - Z_INSERT >= BOIS - 1e-9
assert Y_TUBE[1] + (_yp0 - _yi0) <= _ec["av"].y1, "même poussé au sud de tout son jeu, le tube ne sort pas côté machine"
assert BORGNE + 0.8 < DE - 0.5, "la pointe de la mèche plate ne débouche pas côté mur"
assert max(b.y1 for b in MOBILES) < M.MACHINE.y0, "rien du L dans la zone de la machine"

# ------------------------------------------------------------------ équilibre et efforts (estimations)
# Densités de modele.py (mélaminé ≈ 650 kg/m³, sapin ≈ 450, de mémoire). Mêmes pièces comptées que le meuble actuel
# (porte, plateau, contrefiches) pour l'équilibre ; le linge : LINGE kg par sac plein (estimé, ≈ 0,12 kg/L).
LINGE = 4.0
# Toutes les pièces du L comptées, supports et barres de la porte compris (le modèle actuel ne compte que porte, plateau
# et contrefiches : son équilibre de 23,9° compté comme ici vaut moins, voir EQUILIBRE_ACTUEL).
RHO = dict(facade=650, bac=650, support=650, bois=450, barre=600)        # barre : manche à balai (estimé)


def _cg(b):
    """Masse (kg) et centre (x, z) d'une pièce du L fermé."""
    pts = b.pts("y")
    A = aire(pts)
    cx = sum((x0 + x1) * (x0 * z1 - x1 * z0) for (x0, z0), (x1, z1) in zip(pts, pts[1:] + pts[:1]))
    cz = sum((z0 + z1) * (x0 * z1 - x1 * z0) for (x0, z0), (x1, z1) in zip(pts, pts[1:] + pts[:1]))
    s6 = 6 * sum(x0 * z1 - x1 * z0 for (x0, z0), (x1, z1) in zip(pts, pts[1:] + pts[:1])) / 2
    return A * (b.y1 - b.y0), (cx / s6, cz / s6)


def masses(pieces):
    return [(RHO[b.role] * _cg(b)[0] * 1e-6, _cg(b)[1]) for b in pieces]


MASSES = masses(MOBILES)
_cs = _cg(SACS[0])[1]
LINGE_CG = _cs                                  # le linge, au centre du sac fermé, porté par le plateau


def moment(a, linge=0.0, sac_porte=0.0):
    """Moment du poids autour de l'axe, en kg·cm (> 0 : le L se referme) ; linge : kg posés sur le plateau ;
    sac_porte : kg pendus à la barre de la porte (barre arrière levée pour sortir le sac)."""
    r = sum(m * (M.bascule(x, z, AXE, a)[0] - XA) for m, (x, z) in MASSES)
    r += linge * (M.bascule(*LINGE_CG, AXE, a)[0] - XA)
    r += sac_porte * (M.bascule(_xf0 + _bx / 2, (_zb0 + _zb1) / 2, AXE, a)[0] - XA)
    return r


def equilibre():
    return next(k / 10 for k in range(0, 900) if moment(k / 10) < 0)


# lest : le moins de tasseaux qui laisse MARGE_EQ entre l'arrêt à 20° et l'équilibre
MARGE_EQ = 3
EQUILIBRE_SANS_LEST = equilibre()
for N_LEST in range(0, 4):
    MASSES = masses(MOBILES + lest(N_LEST))
    if equilibre() >= ANGLE + MARGE_EQ:
        break
LESTS = lest(N_LEST)
MOBILES = MOBILES + LESTS
MASSES = masses(MOBILES)
M_L = sum(m for m, _ in MASSES)
EQUILIBRE = equilibre()
assert moment(0) > 0 and EQUILIBRE >= ANGLE + MARGE_EQ, "à vide, le L ouvert à 20° se referme seul"
assert A_MAX > EQUILIBRE, "à vide, le L reste ouvert à la butée"
assert all(l_.x0 > _xs1 for l_ in LESTS), "le lest est derrière les sacs"
# le meuble actuel compté de la même façon (toutes ses pièces mobiles, autour de son axe)
_act = [_pc[n] for n in ("bac_porte", "plateau", "contrefiche_n", "contrefiche_s")] + SUR_PORTE
_ma = masses(_act)
EQUILIBRE_ACTUEL = next(k / 10 for k in range(0, 900)
                        if sum(m * (M.bascule(x, z, M.AXE, k / 10)[0] - M.AXE[0]) for m, (x, z) in _ma) < 0)
COLLISIONS = collisions()
assert not COLLISIONS, COLLISIONS[:5]


def poignee(a, linge=0.0):
    """Effort horizontal (N) à la prise pour tenir le L à a degrés."""
    zh = M.bascule(M.FACE, Z_HAUT_PORTE - 3, AXE, a)[1]
    return moment(a, linge) * G / (zh - ZA)


_xr = (RAIL_AR.x0 + RAIL_AR.x1) / 2


def efforts():
    """Cas de charge, en N : paliers (par montant), rail arrière, butée (par tire-fond)."""
    a = math.radians(A_MAX)
    nb = (math.sin(a), -math.cos(a))           # le tire-fond appuie sur le dessus du plateau

    def axe_butee(m_tot, mom, tire=0.0):
        fb = (-mom * G + tire * (M.bascule(M.FACE, Z_HAUT_PORTE - 3, AXE, A_MAX)[1] - ZA)) / R_BUTEE   # N
        fx, fz = fb * nb[0] - tire, fb * nb[1] - m_tot * G
        return math.hypot(fx, fz) / 2, fb / 2
    plein = 2 * LINGE
    r_rail = moment(0, plein) * G / (_xr - XA)
    c = dict(
        ferme=((M_L + plein) * G - r_rail) / 2, rail=r_rail,
        butee_vide=axe_butee(M_L, moment(A_MAX)),
        butee_sac=axe_butee(M_L + LINGE, moment(A_MAX, sac_porte=LINGE)),
        butee_tire=axe_butee(M_L + LINGE, moment(A_MAX, sac_porte=LINGE), tire=50.0),
    )
    c["palier_max"] = max(c["ferme"], c["butee_vide"][0], c["butee_sac"][0], c["butee_tire"][0])
    c["tirefond_max"] = max(c["butee_vide"][1], c["butee_sac"][1], c["butee_tire"][1])
    return c


EFF = efforts()
# tube : le L est raide en long (la porte est une poutre de 77 de haut) ; le tube ne travaille qu'entre le bord du plateau
# et le milieu du palier sud (le plus long porte-à-faux), en flexion
_D, _di = TUBE["d"] * 10, (TUBE["d"] - 2 * TUBE["ep"]) * 10
I_TUBE = math.pi * (_D ** 4 - _di ** 4) / 64      # mm⁴
W_TUBE = I_TUBE / (_D / 2)                       # mm³
LEVIER = ((_ec["av"].y0 + Y_TUBE[1]) / 2 - _yp1) * 10    # mm
SIGMA = EFF["palier_max"] * LEVIER / W_TUBE      # MPa
PRESSION = EFF["palier_max"] / (TROU * 10 * BORGNE * 10)                          # MPa, palier borgne (le plus court)
CHOC = sum(-moment(EQUILIBRE + k / 10) for k in range(int((A_MAX - EQUILIBRE) * 10))) * 1e-2 * G * math.radians(0.1)
assert SIGMA < 60 and PRESSION < 1.0


# ------------------------------------------------------------------ dessins
def _poly(pts, cls, style=""):
    st = f' style="{style}"' if style else ""
    return f'<polygon class="{cls}"{st} points="{" ".join(f"{f(x)},{f(y)}" for x, y in pts)}"/>'


def _fixes_bas():
    return FIXES + EQUIP


def plan_dessus():
    """P1 · vue de dessus de l'alcôve coupée à 20 du sol : échelles, rails, L fermé, axe (caché, en tireté), machine ;
    le plan en tireté, les positions du haut de la porte à 20° et à la butée, le vantail de la porte d'entrée."""
    zs = 20
    xg = M.PORTE["x1"] - 16
    o = [PL.rect(M.X1 - M.ALCOVE["nord"], M.Y0 - 4, M.X1 + 4, M.Y0, "omurc"),
         PL.rect(M.X1 - M.ALCOVE["sud"], M.Y1, M.X1 + 4, M.Y1 + 4, "omurc"), PL.rect(M.X1, M.Y0, M.X1 + 4, M.Y1, "omurc"),
         PL.rect(M.PORTE["x1"], M.Y0 - 4, M.X1 - M.ALCOVE["nord"], M.Y0, "omurc")]
    # vantail de la porte d'entrée grand ouvert (épaisseur 4, estimée) et son arc
    xv = M.PORTE["x1"]
    o.append(PL.rect(xv - 4, M.Y0, xv, M.Y0 + M.PORTE["l"], "ocache"))
    o.append(f'<path class="ocache" d="M{f(xv - M.PORTE["l"])} {f(M.Y0)} A{M.PORTE["l"]} {M.PORTE["l"]} 0 0 0 '
             f'{f(xv)} {f(M.Y0 + M.PORTE["l"])}" style="fill:none"/>')
    o.append(PL.text(xv - 5, M.Y0 + 60, "porte d'entrée ouverte", "lt muted", "end"))
    o += CO.projeter([b for b in _fixes_bas() if b.role not in ("sac", "barre")] + [PORTE, PLATEAU] + CONTREFICHES,
                     "dessus", zs)
    pl = _pc["plan_travail"]
    o.append(PL.poly([(pl.x0, pl.y0), (pl.x1, pl.y0), (pl.x1, pl.encoche[2]), (pl.encoche[0], pl.encoche[2]),
                      (pl.encoche[0], pl.encoche[3]), (pl.x1, pl.encoche[3]), (pl.x1, pl.y1), (pl.x0, pl.y1)], "oplanl"))
    # l'axe sous le plateau et ses deux trous, cachés
    o.append(PL.rect(XA - _r, Y_TUBE[0], XA + _r, Y_TUBE[1], "ocache"))
    o.append(f'<line class="odiag" x1="{f(XA)}" y1="{f(Y_TUBE[0] - 3)}" x2="{f(XA)}" y2="{f(Y_TUBE[1] + 3)}" '
             'style="stroke:var(--tri);stroke-dasharray:3 .8 .6 .8"/>')
    for y in VIS_AXE["ys"]:
        o.append(f'<circle class="otrou" cx="{f(XA)}" cy="{f(y)}" r=".45"/>')
    # haut de la porte basculée : 20° et butée
    for av, lab, st, yt in ((AVANCE, f"{ANGLE}°", "", P0.y0 + 4), (AVANCE_MAX, f"{A_MAX}°", "stroke:var(--water)", P0.y1 - 1.5)):
        o.append(_poly([(M.FACE - av, P0.y0), (M.FACE, P0.y0), (M.FACE, P0.y1), (M.FACE - av, P0.y1)], "oswing", st))
        o.append(PL.text(M.FACE - av + 1, yt, f"haut de la porte à {lab}", "lt", "start"))
    o.append(CO.etiquette(XA, Y_TUBE[0] + 6, XA + 7, Y_TUBE[0] + 7.5, "axe : tube alu Ø 16 sous le plateau"))
    o.append(CO.etiquette(XA, VIS_AXE["ys"][1], XA + 14, VIS_AXE["ys"][1] + 6, "3 vis de blocage"))
    e = M.ECH
    o.append(CO.chaine_v([M.Y0, e["n"], e["n"] + DE, _yp0, _yp1, e["c"], e["c"] + DE, M.Y1], M.X1 + 9, ext=M.X1))
    o.append(CO.chaine_h([M.FACE, M.XO0, M.XO0 + DL, M.XO1 - DL, M.XO1, M.X1], M.Y1 + 9, ext=M.Y1))
    o.append(CO.cote_h(M.FACE, XA, M.Y1 + 15, f"{cm(XA - M.FACE)} façade → axe", ext=M.Y1, place="droite"))
    o.append(CO.cote_h(M.FACE - AVANCE_MAX, M.FACE, M.Y0 - 6, f"{cm(AVANCE_MAX)} à {A_MAX}°", ext=M.Y0))
    o.append(CO.cote_h(M.FACE - AVANCE, M.FACE, M.Y0 - 12, f"{cm(AVANCE)} à {ANGLE}°", ext=M.Y0))
    o.append(CO.cote_h(xv, M.FACE, M.Y0 + 78, f"{cm(M.FACE - xv)}", ext=M.Y0 + M.PORTE["l"]))
    o.append(PL.text((M.MACHINE.x0 + M.MACHINE.x1) / 2, (M.LLZ["y0"] + M.LLZ["y1"]) / 2 + 1, "machine", "lt"))
    o.append(PL.text((M.XO0 + M.XO1) / 2 + 6, 40, "plateau du L", "lt muted"))
    o.append(PL.text(M.X1 - M.ALCOVE["nord"] - 1, M.Y0 - 1.2, "mur nord", "lt muted", "end"))
    return CO.svg(xg - 8, M.Y0 - 20, M.X1 + 30, M.Y1 + 20, o, "Plan de l'alcôve, variante à axe")


def coupe_cote():
    """P2 · coupe de côté par le sac nord (vue vers le nord) : le L fermé, à 20° (tireté rouge), à la butée (bleu)."""
    s = (SACS[0].y0 + SACS[0].y1) / 2
    h = M.Z_DESSUS + 8
    o = [PL.rect(M.X1, -h, M.X1 + 4, 0, "omurc"),
         f'<line class="osol" x1="{f(M.FACE - 14)}" y1="0" x2="{f(M.X1 + 4)}" y2="0"/>']
    o += CO.projeter(_fixes_bas() + MOBILES + [TUBE_P] + SACS, "cote", s)
    for a, st in ((ANGLE, ""), (A_MAX, "stroke:var(--water)")):
        for b in (PLATEAU, CONTREFICHES[0], PORTE):
            o.append(_poly([(x, -z) for x, z in tourne(b, a).pts("y")], "oswing", st))
    o.append(f'<circle class="oaxe" cx="{f(XA)}" cy="{f(-ZA)}" r=".8"/>')
    o.append(CO.chaine_h([M.FACE, M.XO0, M.XO0 + DL, M.XO1 - DL, M.XO1, M.X1], 6, ext=0))
    o.append(CO.cote_h(M.FACE, M.X1, 13, f"{cm(M.PROF)} profondeur, plan compris"))
    o.append(CO.cote_h(M.FACE, XA, 19, f"{cm(XA - M.FACE)} façade → axe", ext=0, place="droite"))
    o.append(CO.cote_h(M.XO0, X_BUTEE, -Z_BUTEE + 5.5, cm(X_BUTEE - M.XO0), ext=-Z_BUTEE))
    o.append(CO.etiquette(X_BUTEE, -Z_BUTEE, M.X1 + 6, -Z_BUTEE - 14, f"tire-fond de butée ({A_MAX}°)"))
    o.append(CO.etiquette(XA, -ZA, M.FACE - 6, -ZA - 9, "axe Ø 16", "end"))
    for a, st in ((ANGLE, "lt"), (A_MAX, "lt")):
        hp = M.bascule(M.FACE, Z_HAUT_PORTE, AXE, a)
        o.append(PL.text(hp[0] - 1, -hp[1] + 4, f"{a}°", st, "end"))
    o.append(PL.text((M.XO0 + M.XO1) / 2 + 2, -45, "sac (coupé)", "lt"))
    o.append(CO.niveaux([(M.Z0, f"{cm(M.Z0)} vérins", M.FACE), (RAIL_H, f"{cm(RAIL_H)} rail avant", M.XO0),
                         (ZA, f"{cm(ZA)} axe", XA), (Z_BAS_PORTE, f"{cm(Z_BAS_PORTE)} bas de la porte", M.FACE),
                         (Z_BUTEE, f"{cm(Z_BUTEE)} tire-fond", M.XO0),
                         ((_zb0 + _zb1) / 2, f"{cm((_zb0 + _zb1) / 2)} axe des barres", M.XO0),
                         (M.Z_PLAN, f"{cm(M.Z_PLAN)} dessous du plan", M.FACE)], M.FACE - 30))
    o.append(CO.niveaux([(ZP, f"{cm(ZP)} dessous du plateau", _xr), (RAIL_AR.z0, f"{cm(RAIL_AR.z0)} rail arrière", _xr)],
                        M.X1 + 8, droite=True))
    o.append(PL.text(M.FACE - 8, 4.5, "salle de bain", "lt muted", "end"))
    o.append(PL.text(M.X1 + 1, -h - 1.4, "mur du fond", "lt muted", "end"))
    return CO.svg(M.FACE - 60, -h - 8, M.X1 + 34, 23, o, "Coupe de côté, variante à axe")


K = 6.0                 # détails agrandis : 6 unités de dessin par cm


def _niv_k(liste, x, z0, k, droite=False):
    """Niveaux (▽) d'un dessin agrandi : CO.niveaux attend des cotes non agrandies, on lui passe z agrandi."""
    return CO.niveaux([((z - z0) * k, lab, xe) for z, lab, xe in liste], x, droite)


def detail_pivot():
    """P3 · coupe agrandie au pivot, par une vis de blocage (vue vers le nord) : rail avant coupé, montant avant vu
    derrière avec son trou, tube, plateau rainuré, porte ; tireté : à 20° et à la butée."""
    x0, x1, z0, z1 = M.FACE - 5, M.XO0 + 11, -0.5, ZA + 9
    X = lambda x: (x - x0) * K  # noqa: E731
    Z = lambda z: -(z - z0) * K  # noqa: E731
    P = lambda pts, cls, st="": _poly([(X(x), Z(z)) for x, z in pts], cls, st)  # noqa: E731
    g = []                      # géométrie, coupée au cadre du détail
    mav = _en["av"]
    g.append(P(mav.pts("y"), "obois"))                             # montant nord, vu derrière
    g.append(P(M.RAILS[0].pts("y"), "obois cut"))
    g.append(P(_pc["verin_montant_av_n"].pts("y"), "omet"))
    cx, cy = X(XA), Z(ZA)
    g.append(f'<circle class="ocache" cx="{f(cx)}" cy="{f(cy)}" r="{f(_rt * K)}" style="fill:var(--panel)"/>')
    g0, g1, gp = XA - RAINURE["l"] / 2, XA + RAINURE["l"] / 2, RAINURE["p"]
    pla = [(M.XO0, ZP), (g0, ZP), (g0, ZP + gp), (g1, ZP + gp), (g1, ZP), (x1 + 5, ZP), (x1 + 5, ZP + T), (M.XO0, ZP + T)]
    por = [(M.FACE, Z_BAS_PORTE), (M.XO0, Z_BAS_PORTE), (M.XO0, z1 + 5), (M.FACE, z1 + 5)]
    g.append(P(pla, "omel cut"))
    g.append(P(por, "ofac cut"))
    g.append(f'<circle class="obar cut" cx="{f(cx)}" cy="{f(cy)}" r="{f(_r * K)}"/>')
    g.append(f'<circle class="ohub" cx="{f(cx)}" cy="{f(cy)}" r="{f((_r - TUBE["ep"]) * K)}" style="fill:var(--panel)"/>')
    vz1 = ZP + T
    vz0 = vz1 - VIS_AXE["L"]
    g.append(P([(XA - 0.21, vz0 + 0.3), (XA, vz0), (XA + 0.21, vz0 + 0.3), (XA + 0.21, vz1 - 0.42), (XA + 0.4, vz1),
                (XA - 0.4, vz1), (XA - 0.21, vz1 - 0.42)], "omet"))
    for a, st in ((ANGLE, ""), (A_MAX, "stroke:var(--water)")):
        for pts in (pla, por):
            g.append(P([M.bascule(x, z, AXE, a) for x, z in pts], "oswing", st))
    g.append(f'<circle class="oaxe" cx="{f(cx)}" cy="{f(cy)}" r=".9"/>')
    w, h = X(x1), Z(z0) - Z(z1)
    o = [f'<defs><clipPath id="pv-clip-d"><rect x="0" y="{f(Z(z1))}" width="{f(w)}" height="{f(h)}"/></clipPath></defs>',
         f'<line class="osol" x1="0" y1="{f(Z(0))}" x2="{f(w)}" y2="{f(Z(0))}"/>',
         f'<g clip-path="url(#pv-clip-d)">{"".join(g)}</g>',
         f'<rect x="0" y="{f(Z(z1))}" width="{f(w)}" height="{f(h)}" style="fill:none;stroke:var(--line);stroke-width:.3"/>']
    o.append(CO.cote_h(X(M.XO0), X(XA), Z(z1) - 3, cm(D_AV), ext=Z(z1)))
    o.append(CO.cote_h(X(M.FACE), X(M.XO0), Z(z1) - 3, cm(T), ext=Z(z1), place="gauche"))
    o.append(_niv_k([(0, "0 sol", 0), (RAIL_H, f"{cm(RAIL_H)} dessus du rail avant", X(M.XO0)),
                     (ZA, f"{cm(ZA)} axe", cx), (ZP, f"{cm(ZP)} dessous du plateau", X(M.XO0)),
                     (Z_BAS_PORTE, f"{cm(Z_BAS_PORTE)} bas de la porte", X(M.FACE)),
                     (ZP + T, f"{cm(ZP + T)} dessus du plateau", X(M.XO0))], -4, z0, K))
    d = X(x1) + 3
    o.append(CO.etiquette(X(XA + 0.15), Z(ZP + T - 0.5), d, Z(ZP + T) - 9, "vis à tôle 4,2 × 25 (3 en tout)"))
    o.append(CO.etiquette(X(g1 - 0.1), Z(ZP + 0.1), d, Z(ZP + T) - 3, f"rainure {cm(RAINURE['l'] * 10)} × "
                                                                          f"{cm(RAINURE['p'] * 10)} mm"))
    o.append(CO.etiquette(X(x1 - 1), Z(ZP + T / 2), d, Z(ZP + T / 2) + 2, "plateau A3"))
    o.append(CO.etiquette(cx + _r * K * 0.7, cy + _r * K * 0.7, d, Z(ZA) + 7, "tube alu Ø 16 × 1"))
    o.append(CO.etiquette(cx + _rt * K, cy - 1.5, d, Z(ZA) + 13, "trou Ø 16 du montant (vu derrière)"))
    o.append(CO.etiquette(X(M.XO0 + 3), Z(z1 - 3), d, Z(z1 - 3), "montant avant (vu derrière)"))
    o.append(CO.etiquette(X(M.XO0 + 2.5), Z(RAIL_H - 1.5), d, Z(RAIL_H - 1.5) + 4, "rail avant G5 (coupé)"))
    o.append(CO.etiquette(X(M.FACE + 0.9), Z(z1 - 2), X(M.FACE) - 4, Z(z1 - 2) + 8, "porte A6", "end"))
    hb = M.bascule(M.FACE, Z_BAS_PORTE, AXE, A_MAX)
    o.append(CO.etiquette(X(hb[0]), Z(hb[1]), X(hb[0]) - 6, Z(hb[1]) + 13, f"bas de la porte à {A_MAX}°", "end"))
    return CO.svg(-52, Z(z1) - 8, d + 46, Z(z0) + 4, o, "Détail du pivot, coupe de côté")


def detail_axe():
    """P4 · coupe agrandie le long de l'axe (vue de face, vers le mur du fond) : les deux montants avant et leurs trous,
    le tube, le plateau et ses vis, le rail avant ; la machine à droite."""
    y0, y1, z0, z1 = M.Y0 - 2, M.MACHINE.y0 + 4, -0.5, ZA + 6
    k = 3.0
    Y = lambda y: (y - y0) * k  # noqa: E731
    Z = lambda z: -(z - z0) * k  # noqa: E731
    R = lambda a, b, c, d, cls, st="": _poly([(Y(a), Z(c)), (Y(b), Z(c)), (Y(b), Z(d)), (Y(a), Z(d))], cls, st)  # noqa: E731
    o = [R(y0, M.Y0, z0, z1, "omurc"), f'<line class="osol" x1="0" y1="{f(Z(0))}" x2="{f(Y(y1))}" y2="{f(Z(0))}"/>']
    for e in (_en, _ec):
        m_ = e["av"]
        o.append(R(m_.y0, m_.y1, M.Z0, z1, "obois cut"))
        v = _pc[f"verin_{m_.nom}"]
        o.append(R(v.y0, v.y1, 0, M.Z0, "omet"))
    o.append(R(M.RAILS[0].y0, M.RAILS[0].y1, M.RAILS[0].z0, M.RAILS[0].z1, "obois"))
    o.append(R(M.MACHINE.y0, y1, 0, z1, "omach"))
    o.append(R(Y_TUBE[0], Y_TUBE[1], ZA - _r, ZA + _r, "obar cut"))
    o.append(f'<line class="ext" x1="{f(Y(Y_TUBE[0] - 1))}" y1="{f(Z(ZA))}" x2="{f(Y(Y_TUBE[1] + 1))}" y2="{f(Z(ZA))}" '
             'style="stroke-dasharray:3 .8 .6 .8"/>')
    # trous des paliers par-dessus le tube : borgne au nord, traversant au milieu
    for a, b in ((_yi0 - BORGNE, _yi0), (_ec["av"].y0, _ec["av"].y1)):
        o.append(R(a, b, ZA - _rt, ZA + _rt, "ocache"))
    # plateau coupé dans l'axe : la rainure y fait 2 mm ; les vis de blocage
    o.append(R(_yp0, _yp1, ZP + RAINURE["p"], ZP + T, "omel cut"))
    for y in VIS_AXE["ys"]:
        o.append(R(y - 0.21, y + 0.21, ZA + _r - TUBE["ep"] - 0.3, ZP + T, "omet"))
    pts = [M.Y0, Y_TUBE[0], _yi0, _yp0, _yp1, _yi1, Y_TUBE[1], _ec["av"].y1, M.MACHINE.y0]
    for a, b in zip(pts, pts[1:]):
        o.append(CO.cote_h(Y(a), Y(b), Z(0) + 7, cm(b - a) if b - a >= 1.5 else " ", ext=Z(0)))
    o.append(CO.cote_h(Y(Y_TUBE[0]), Y(Y_TUBE[1]), Z(0) + 15, f"tube {cm(TUBE['L'])}", ext=Z(ZA - _r)))
    for yv in VIS_AXE["ys"]:
        o.append(f'<line class="ext" x1="{f(Y(yv))}" y1="{f(Z(ZP + T))}" x2="{f(Y(yv))}" y2="{f(Z(z1) - 3)}"/>')
    o.append(CO.cote_h(Y(_yp0), Y(VIS_AXE["ys"][0]), Z(z1) - 3, cm(VIS_AXE["ys"][0] - _yp0), ext=Z(ZP + T)))
    for a, b in zip(VIS_AXE["ys"], VIS_AXE["ys"][1:]):
        o.append(CO.cote_h(Y(a), Y(b), Z(z1) - 3, cm(b - a)))
    o.append(PL.text(Y((_yp0 + _yp1) / 2), Z(z1) - 7.5, "plateau A3 posé sur le tube, 3 vis de blocage", "lt"))
    o.append(PL.text(Y((_yp0 + _yp1) / 2), Z(RAIL_H / 2 + 1), "rail avant G5 (vu)", "lt muted"))
    o.append(CO.etiquette(Y(_yi0 - BORGNE / 2), Z(ZA), Y(_yi0) + 18, Z(ZA) + 9.5, f"trou borgne de {cm(BORGNE)}"))
    o.append(CO.etiquette(Y((_ec["av"].y0 + _ec["av"].y1) / 2), Z(ZA), Y(_ec["av"].y0) - 18, Z(ZA) + 9.5,
                          "trou traversant", "end"))
    o.append(PL.text(Y(M.MACHINE.y0) + 2, Z(z1 / 2), "machine", "lt", "start"))
    o.append(PL.text(Y(M.Y0) - 1, Z(z1) + 3, "mur", "lt muted", "end"))
    o.append(PL.text(Y((_en["av"].y0 + _en["av"].y1) / 2), Z(0) + 22.5, "montant nord", "lt muted"))
    o.append(PL.text(Y((_ec["av"].y0 + _ec["av"].y1) / 2), Z(0) + 22.5, "montant du milieu", "lt muted"))
    o.append(_niv_k([(ZA, f"{cm(ZA)} axe", Y(M.Y0)), (ZP + T, f"{cm(ZP + T)} dessus du plateau", Y(_yp0))], -4, z0, k))
    return CO.svg(-40, Z(z1) - 12, Y(y1) + 4, Z(0) + 25, o, "Détail de l'axe, coupe de face")


def iso(etat):
    """Vue isométrique du meuble bas : etat = "ferme", "ouvert" (20°, sacs tendus), "butee" (sacs retirés) ou
    "souleve" (le L soulevé de son axe, sans plan ni machine : on voit le tube dans les montants)."""
    if etat == "souleve":
        fix = [b for b in FIXES if b.groupe == "ossature" and b.y0 < _ec["av"].y1 + 0.1 and b.role != "vis"]
        mob = [M.replace(b, groupe="leve") for b in MOBILES if b.role != "barre"]
        return MO.dessin(fix + [TUBE_P] + mob, neuves={b.nom for b in mob} | {TUBE_P.nom}, reperes=False,
                         decale={"leve": (-40, 0, 45)}, titre="Le L soulevé de son axe")
    a = {"ferme": 0, "ouvert": ANGLE, "butee": A_MAX}[etat]
    fix = [b for b in _fixes_bas() if not (etat == "butee" and b.role == "barre")]
    mob = [tourne(b, a) for b in MOBILES + [TUBE_P] if not (etat == "butee" and b.role == "barre" and b is not TUBE_P)]
    sacs = [] if etat == "butee" else (SACS if a == 0 else [sac_ouvert(s, a) for s in SACS])
    neuves = {b.nom for b in mob}
    return MO.dessin(fix + mob + sacs, neuves=neuves, reperes=False, titre=f"Meuble bas, variante à axe ({etat})")


# ------------------------------------------------------------------ texte
ANGLE_SANS_LEST = math.floor(EQUILIBRE_SANS_LEST - 2)
OUV_SANS_LEST = ouverture(ANGLE_SANS_LEST, AXE)


def lettres_lest():
    return {1: "un bout", 2: "deux bouts", 3: "trois bouts"}.get(N_LEST, f"{N_LEST} bouts")


def _tab(lignes):
    return ('<div class="scroll"><table><thead><tr><th>Quoi</th><th>Valeur</th><th>Commentaire</th></tr></thead><tbody>'
            + "".join(f"<tr><td>{a}</td><td class=\"mono\">{b}</td><td>{c}</td></tr>" for a, b, c in lignes)
            + "</tbody></table></div>")


def _n(v):
    return f"{v:.0f}"


def section():
    e = EFF
    figs_plan = CO.figure(
        "pivot-plan", "P1 · Plan de l'alcôve (vue de dessus, coupée à 20 du sol)", plan_dessus(),
        f"Le L fermé (porte, plateau, contrefiches coupées), l'axe en tireté rouge sous le plateau, de {cm(Y_TUBE[0])} à "
        f"{cm(Y_TUBE[1])} depuis le mur nord, et ses trois vis de blocage. Rectangles tiretés : où arrive le haut de la "
        f"porte à {ANGLE}° (on jette le linge) et à {A_MAX}° (on sort un sac). La porte d'entrée grande ouverte est à "
        f"{cm(M.FACE - M.PORTE['x1'])} de la façade : on ne peut pas ouvrir les deux à la fois, comme aujourd'hui.")
    figs_coupes = "".join([
        CO.figure("pivot-coupe", "P2 · Coupe par le sac nord (vue vers le nord)", coupe_cote(),
                  f"Fermé en plein, à {ANGLE}° en tireté rouge (les soufflets des sacs l'arrêtent), à {A_MAX}° en bleu "
                  f"(sac sorti, le plateau appuie sous le tire-fond). Le plateau et le rail arrière sont "
                  f"{cm(DZ)} plus haut qu'aujourd'hui."),
        CO.figure("pivot-detail", "P3 · Détail du pivot (coupe agrandie, par une vis de blocage)", detail_pivot(),
                  f"L'axe est au milieu de l'épaisseur du montant, {cm(D_AV)} derrière le dos de la porte et "
                  f"{cm(ZA)} du sol. En tournant, le coin avant du plateau descend devant l'axe (il garde "
                  f"{cm(RAIL_MAX * 10)} mm au-dessus du rail) et le bas de la porte frôle les montants sans y entrer "
                  f"({cm(jeu_porte(A_MAX) * 10)} mm à {A_MAX}°)."),
        CO.figure("pivot-axe", "P4 · Détail de l'axe (coupe de face, dans l'axe)", detail_axe(),
                  f"Le tube de {cm(TUBE['L'])} entre de {cm(BORGNE)} dans un trou borgne du montant nord (il reste "
                  f"{cm(DE - BORGNE)} de bois côté mur) et traverse le montant du milieu ; son bout reste "
                  f"{cm(RECUL_SUD)} en retrait côté machine. Le plateau a {cm(_yp0 - _yi0)} de jeu de chaque côté : "
                  "même poussé à fond, le tube ne sort pas."),
    ])
    isos = "".join(
        f'<div class="fig">{iso(k)}<p class="cap">{t}</p></div>' for k, t in (
            ("ferme", "Fermé. En orange, ce qui tourne : la porte, le plateau, les contrefiches, l'axe et les barres de "
                      "la porte."),
            ("ouvert", f"Ouvert à {ANGLE}° pour jeter le linge : les soufflets des sacs se tendent et arrêtent la porte."),
            ("butee", f"À la butée, {A_MAX}°, sacs sortis : le plateau est appuyé sous les deux tire-fonds."),
            ("souleve", "Le L soulevé de son axe (plan, machine et sacs ôtés pour voir) : le tube reste dans les deux "
                        "montants avant ; le plateau se pose dessus, sa rainure sur le tube, et se visse par le haut."),
        ))
    lignes = [
        ("Axe", f"tube alu Ø 16 × 1, {cm(TUBE['L'])} de long",
         f"coupé à la scie à métaux dans un tube de 1 m ({TUBE['prix']:.2f} € chez Castorama, prix lu en ligne)".replace(".", ",")),
        ("Paliers", f"trous Ø 16 à {cm(ZA)} du sol", f"au milieu des montants avant ; borgne de {cm(BORGNE)} au nord, "
                                                     "traversant au milieu ; cire de bougie dans les trous"),
        ("Jeu dans les paliers", "0,1 à 0,3 mm au rayon", "le tube doit tourner à la main dans un trou d'essai sur une chute"),
        ("Fixation du L", f"rainure {cm(RAINURE['l'] * 10)} × {cm(RAINURE['p'] * 10)} mm + 3 vis à tôle 4,2 × 25",
         f"le tube s'enfonce de {cm(FLECHE * 10)} mm entre les arêtes ; les vis bloquent rotation et glissement"),
        ("Équilibre à vide", f"{cm(EQUILIBRE)}°", f"avec le lest (sans : {cm(EQUILIBRE_SANS_LEST)}° ; meuble actuel compté "
                                                  f"pareil : {cm(EQUILIBRE_ACTUEL)}°) ; en dessous, le L se referme seul, "
                                                  "au-dessus il part vers la butée"),
        ("Effort pour ouvrir", f"{_n(poignee(0.5))} N à vide, {_n(poignee(0.5, 2 * LINGE))} N sacs pleins",
         f"à la prise, au départ ; sacs pleins : {cm(2 * LINGE)} kg de linge (estimé)"),
        ("Paliers, fermé, sacs pleins", f"{_n(e['ferme'])} N par montant", f"le reste ({_n(e['rail'])} N) sur le rail arrière"),
        ("Paliers, à la butée", f"{_n(e['butee_vide'][0])} N à vide ; {_n(e['butee_sac'][0])} N sac plein pendu ; "
                                f"{_n(e['butee_tire'][0])} N si on tire à 50 N",
         f"pression dans le bois ≤ {cm(PRESSION)} MPa (sapin en travers du fil : ≈ 2 à 3 MPa admissibles, de mémoire)"),
        ("Tire-fond de butée", f"{_n(e['butee_vide'][1])} à {_n(e['tirefond_max'])} N chacun",
         f"à {cm(R_BUTEE)} de l'axe ; choc à vide ≈ {cm(CHOC)} J si on lâche la porte au-delà de l'équilibre (mousse)"),
        ("Tube", f"{_n(SIGMA)} MPa au plus",
         f"flexion sur les {cm(LEVIER / 10)} entre le bord du plateau et le milieu du palier sud ; le L, raide en long, "
         "porte le reste (aluminium : ≥ 100 MPa, de mémoire)"),
        ("Jeu plateau – rail avant", f"≥ {cm(RAIL_MAX * 10)} mm", f"le coin avant du plateau descend jusqu'à {A_MAX}°"),
        ("Jeu porte – montants", f"0 → {cm(jeu_porte(A_MAX) * 10)} mm", "le bas de la porte frôle la face des montants "
                                                                       "qu'elle recouvre : pas de place pour un doigt"),
        ("Bas de la porte – sol", f"{cm(SOL_MAX)} à {A_MAX}°", "le coin avant du bas descend un peu en basculant"),
        ("Sortie d'un sac", f"{cm(OUV_MAX)} à {A_MAX}° (fond du sac : {cm(FOND_SAC)})",
         f"à {ANGLE}° : {cm(OUV)}, trop juste pour un sac plein, d'où la butée plus loin"),
    ]
    return f"""<p>{escape(RESUME)} Le reste du meuble ne bouge pas : trois échelles, rail avant, sacs à soufflet sur deux demi-barres chacun, tire-fonds de butée, plan et machine. Ce qui change à cause de l'axe : le plateau et le rail arrière montent de {cm(DZ)}, la porte perd {cm(Z_BAS_PORTE - P0.z0)} par le bas, les sacs {cm(DZ)} de haut ({_n(VOLUME_SAC)} L chacun au lieu de {_n(M.VOLUME_BAC)}), les tire-fonds se déplacent, et {lettres_lest()} de tasseau servent de lest à l'arrière du plateau (voir Équilibre). Les deux charnières plates disparaissent.</p>

<h3>Plan</h3>
<div class="feuille">{figs_plan}</div>

<h3>Coupes et détails du pivot</h3>
<div class="feuille">{figs_coupes}</div>

<h3>Vues</h3>
<div class="grid2">{isos}</div>

<h3>Le mécanisme</h3>
<p><b>Comment ça bouge.</b> On tire la porte par son trou de prise. Le L entier (porte, plateau, contrefiches) tourne autour du tube, et le tube tourne avec lui dans les deux trous des montants : il n'y a plus de charnière, seulement un rond qui tourne dans du bois. À {ANGLE}°, les soufflets des sacs se tendent entre la barre de la porte et la barre arrière et arrêtent la porte : on jette le linge par la fente de {cm(OUV)} entre le haut de la porte et le plan. Pour sortir un sac, on soulève sa demi-barre arrière : le L continue jusqu'à {A_MAX}°, la fente fait {cm(OUV_MAX)}, le sac sort avec ses deux demi-barres.</p>
<p><b>Ce qui porte.</b> Le plateau est posé sur le tube, dans une rainure de {cm(RAINURE['l'] * 10)} mm de large faite à la défonceuse : le tube porte sur ses deux arêtes, ce qui place le L exactement d'avant en arrière. Trois vis à tôle, données d'en haut depuis l'intérieur du bac, le tiennent sur le tube (le L ne peut pas se soulever) et le font tourner avec lui. Fermé, le poids va pour {_n(100 * 2 * e['ferme'] / (2 * e['ferme'] + e['rail']))} % dans les deux paliers et le reste sur le rail arrière, remonté pour cela de {cm(DZ)}. Les paliers sont les montants eux-mêmes : {_n(e['palier_max'])} N au plus par montant, très loin de ce que supporte le sapin.</p>
<p><b>Ce qui arrête.</b> Fermé : le plateau sur le rail arrière et le dos de la porte contre les montants avant (comme aujourd'hui). Ouvert : les soufflets des sacs à {ANGLE}°, puis, sans eux, les deux tire-fonds inox 8 × 60 plantés dans les écharpes, à {cm(Z_BUTEE)} du sol et {cm(X_BUTEE - M.XO0)} derrière la face des montants : le plateau vient s'appuyer dessous, sur sa mousse, à {A_MAX}°. En long, le tube bute au fond du trou nord et le plateau a {cm(_yp0 - _yi0)} de jeu de chaque côté.</p>
<p><b>Équilibre.</b> L'axe est {cm(D_AV)} plus en arrière que l'ancienne charnière : la porte, lourde et haute, est un peu plus en avant de lui, et le L vide ne retomberait plus fermé seul depuis {ANGLE}° (équilibre à {cm(EQUILIBRE_SANS_LEST)}°, contre {cm(EQUILIBRE_ACTUEL)}° pour le meuble actuel compté de la même façon, déjà juste). D'où le lest : {lettres_lest()} de tasseau de {cm(PLATEAU.y1 - PLATEAU.y0)} empilés et vissés sur l'arrière du plateau, derrière les sacs ({cm(sum(m for m, _ in masses(LESTS)))} kg). Avec lui, à vide, le L ouvert à moins de {cm(EQUILIBRE)}° retombe fermé seul ; au-delà il part vers la butée (choc ≈ {cm(CHOC)} J, amorti par la mousse) et y reste. Avec du linge, il se referme toujours seul, et plus fort : accompagner la porte.</p>
<p><b>Monter et démonter.</b> Le tube se glisse par le côté sud du montant du milieu, avant de rentrer la machine ; on pose le L dessus, puis on perce les trois avant-trous Ø 3,5 dans le tube à travers les trous du plateau et on visse. Pour sortir le L plus tard : sacs sortis, trois vis et deux tire-fonds dévissés, on l'entrouvre, on le soulève de quelques millimètres hors de la rainure et on le tire vers soi. Le tube reste en place.</p>
{_tab(lignes)}
<p class="note">Efforts estimés : densités du modèle actuel (mélaminé ≈ 650 kg/m³, sapin ≈ 450), {cm(LINGE)} kg de linge par sac plein, résistances du sapin et de l'aluminium de mémoire. Tube et vis non relevés au magasin : prix du tube lu en ligne chez Castorama le 01/11/2026.</p>

<h3>À trancher</h3>
<ul>
<li>Lest ou angle : au lieu des deux bouts de tasseau, on peut faire arrêter la porte par les sacs à {ANGLE_SANS_LEST}° au lieu de {ANGLE}° (sous l'équilibre sans lest, {cm(EQUILIBRE_SANS_LEST)}°) ; la fente pour jeter le linge passe alors de {cm(OUV)} à {cm(OUV_SANS_LEST)}.</li>
<li>Fraise de la rainure : une fraise droite de 10 mm. Si la vôtre est plus large, on se passe de rainure : le tube est alors placé par les trois vis seules, et le plateau est {cm(FLECHE * 10)} mm plus haut.</li>
</ul>"""


# ------------------------------------------------------------------ fiche pour le comparatif
_reps = [b.rep for b in M.PIECES if b.groupe != "caisson_haut" and b.rep and b.rep != "D1"]
_cout_lignes = [(n, round(p, 2)) for n, p in [
    ("Tasseaux sapin 38 × 38, 2 lots de 6 (ossature et L)", 2 * 23.60),
    ("Tablette mélaminé 250 × 50 × 18 (porte, plateau, supports)", 13.59),
    ("Équerres plates (2) et lot de 6 équerres", 2 * 1.79 + 5.95),
    ("Vérins (3 lots) et inserts (2 lots)", 3 * 4.19 + 2 * 3.19),
    ("Peinture des tasseaux 0,5 L", 17.70),
    ("Tire-fonds inox (lot de 4) et mousses", 5.60 + 3.49),
    ("Toile des sacs (Marseille Textiles)", M.TOILE["prix"]),
    ("Vis 5 × 60, 4 × 40, 4 × 16 (boîtes) et 1 rouleau de chant", 11.50 + 9.00 + 7.95 + 9.50),
    ("Tube alu Ø 16 × 1 m (Castorama, prix lu en ligne)", TUBE["prix"]),
    ("Vis à tôle 4,2 × 25, petit lot (estimé)", 2.50),
]]
COUT = round(sum(p for _, p in _cout_lignes), 2)
COUT_LINGE_SEUL = round(13.59 + 5.95 + 5.60 + 3.49 + M.TOILE["prix"] + TUBE["prix"] + 2.50, 2)

FICHE = dict(
    nom="Porte en L sur axe pivotant",
    principe=RESUME,
    mettre=[f"tirer la porte par le trou de prise : elle bascule et s'arrête seule à {ANGLE}° (soufflets tendus)",
            f"jeter le linge dans le sac voulu, par la fente de {cm(OUV)} entre le haut de la porte et le plan",
            "lâcher : la porte se referme seule (accompagner si les sacs sont pleins)"],
    retirer=[f"ouvrir à {ANGLE}°",
             "soulever la demi-barre arrière du sac (sortie de son support ou de l'accroche centrale)",
             f"laisser basculer la porte jusqu'à la butée ({A_MAX}°)",
             "sortir le sac par le haut avec ses deux demi-barres (barre de la porte soulevée de sa demi-lune)",
             "le porter à la machine, juste à droite ; remettre le sac vide sur ses barres, refermer"],
    bouche=dict(largeur=round(_yp1 - _yp0, 1), profondeur=round(OUV, 1), hauteur=round(Z_HAUT_20, 1),
                texte=f"{cm(_yp1 - _yp0)} × {cm(OUV)} (deux sacs de {cm(_wl)} de large), fente entre le haut de la "
                      f"porte à {cm(Z_HAUT_20)} du sol et le plan à {cm(M.Z_PLAN)}, porte ouverte à {ANGLE}°"),
    contenants=dict(nombre=2, volume_l=round(VOLUME_SAC, 1), independants=True,
                    texte=f"2 sacs à soufflet de {_n(VOLUME_SAC)} L, chacun sur ses deux demi-barres : on en sort un "
                          "sans toucher à l'autre"),
    pieces=len(_reps) + 1 + N_LEST,
    pieces_detail=f"{len(_reps)} pièces du meuble bas actuel (hors plan) + le tube + {N_LEST} bouts de tasseau de lest ; "
                  f"même débit, porte raccourcie de {cm(Z_BAS_PORTE - P0.z0)}",
    usinages=["2 trous Ø 16 dans les montants avant (borgne de 2 au nord, traversant au milieu), à la même hauteur",
              f"rainure {cm(RAINURE['l'] * 10)} × {cm(RAINURE['p'] * 10)} mm sous le plateau, à la défonceuse (fraise droite Ø 10)",
              "3 trous Ø 4,5 fraisés dans le plateau, puis 3 avant-trous Ø 3,5 dans le tube, percés en place",
              "tube coupé à longueur (scie à métaux, ébavurer)",
              "comme le meuble actuel : trou de prise Ø 25, demi-lunes des supports B1, crochet de l'accroche, "
              "coupes d'onglet des contrefiches et des écharpes, 2 trous de tire-fond dans les écharpes, inserts des vérins"],
    quincaillerie=[(TUBE["nom"], 1, "Castorama (réf. 3232630508800)", 7.19),
                   (VIS_AXE["nom"], 3, "Weldom (lot, estimé)", 2.50),
                   ("tire-fond inox 8 × 60 (butée)", 2, "Weldom 5618626 (lot de 4)", 5.60),
                   ("mousse amortisseur 8 × 16", 2, "Weldom 85066295 (lot de 20)", 3.49),
                   ("équerre d'assemblage 50 × 50", 4, "Weldom 5605252 (lot de 6)", 5.95),
                   ("équerre plate 100 (rails côté nord)", 2, "Weldom 9154961", 3.58),
                   ("vérin M8 + insert M8 (sous les montants)", 6, "Weldom 5572729 + 96652796", 18.95),
                   ("barres rondes Ø 22 (manche à balai ou tringle)", 4, "récupération", 0.0)],
    outils=["perceuse-visseuse", "mèche plate Ø 16 (≈ 4 €, estimé, si absente) et forets bois", "foret métal Ø 3,5",
            "défonceuse + fraise droite Ø 10 et guide parallèle", "scie à métaux et lime", "scies, équerre, niveau "
            "(comme le meuble actuel)", "clé de 13 (tire-fonds)", "machine à coudre (sacs)"],
    reglages=["percer les deux trous à la même distance de la tête des montants : quand les vérins mettent le plan de "
              "niveau, l'axe l'est aussi",
              "tube libre à la main dans les deux trous (poncer ou cirer), avant de poser le L",
              "lest : vérifier que la porte vide ouverte à 20° retombe seule ; sinon un 3ᵉ bout de tasseau",
              f"rail arrière vissé {cm(DZ)} plus haut : le plateau fermé repose dessus pendant que la porte touche les montants",
              "hauteur des tire-fonds dans les écharpes (angle de butée)",
              f"haut des soufflets à {cm(BOUCHE)} (arrêt à {ANGLE}°)"],
    risques=["sapin qui gonfle à l'humidité : le tube serre dans les trous (cire, trou à peine plus grand)",
             "grincement bois / alu (cire)",
             f"choc à la butée si l'on lâche la porte au-delà de {cm(EQUILIBRE)}° (≈ {cm(CHOC)} J, mousse)",
             "porte qui claque en se refermant sacs pleins",
             "vis à tôle dans une paroi de 1 mm : à ne pas trop serrer (elles foirent)",
             "comme aujourd'hui, la porte d'entrée doit être fermée pour ouvrir le meuble"],
    cout_estime=COUT,
    cout_detail=_cout_lignes,
    cout_note=(f"meuble bas complet hors plan, machine, tapis et caisson haut (ossature comprise), prix Weldom relevés du "
               f"modèle actuel + tube et vis estimés ; la seule partie linge (L, sacs, butée, axe) ≈ "
               f"{COUT_LINGE_SEUL:.2f} €".replace(".", ",") + ". Par rapport au meuble actuel : − 3,58 € de charnières, + "
               + f"{TUBE['prix'] + 2.50:.2f} € de tube et de vis".replace(".", ",")),
    porte_entree=(f"oui, comme le meuble actuel : à {ANGLE}° le haut de la porte avance de {cm(AVANCE)} et de "
                  f"{cm(AVANCE_MAX)} à la butée, alors que la porte d'entrée grande ouverte passe à "
                  f"{cm(M.FACE - M.PORTE['x1'])} de la façade ; on ouvre l'un ou l'autre"),
    angle=ANGLE, angle_max=A_MAX, axe=dict(x=XA, z=ZA), equilibre=EQUILIBRE,
)


if __name__ == "__main__":
    print(f"axe ({cm(XA)}, {cm(ZA)}), butée {A_MAX}°, équilibre {cm(EQUILIBRE)}°, plateau +{cm(DZ)}, porte dès "
          f"{cm(Z_BAS_PORTE)}, tire-fond r {cm(R_BUTEE)} à ({cm(X_BUTEE)}, {cm(Z_BUTEE)}) marges {MARGES_BUTEE}")
    print(f"ouverture {cm(OUV)} → {cm(OUV_MAX)} ; bouche {cm(BOUCHE)} (actuel {cm(M.BAC['bouche'])}) ; sac {_n(VOLUME_SAC)} L")
    print({k: v for k, v in EFF.items()}, f"sigma {SIGMA:.1f} p {PRESSION:.2f}")
    print(f"lest {N_LEST}, équilibre sans lest {EQUILIBRE_SANS_LEST}°, actuel compté pareil {EQUILIBRE_ACTUEL}°, masse L {M_L:.2f} kg")
    print(f"poignée {poignee(0.5):.0f} / {poignee(0.5, 8):.0f} N ; choc {CHOC:.2f} J ; coût {COUT} ; linge {COUT_LINGE_SEUL}")
