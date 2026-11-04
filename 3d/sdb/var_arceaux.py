# Variante 3 du meuble bas : meuble ouvert, deux coulisses et un arceau ; les bacs se posent sur l'arceau.
#
# Demande du client : « Le troisième meuble ouvert deux rails avec un arceau les bacs a linge se pose et dépose sur les
# arceaux. » Module du document de confrontation (variantes.py) : il ne remplace pas le meuble actuel.
#
# Lecture retenue : un seul arceau, porté par une paire de coulisses à billes à sortie totale vissées sur les faces
# intérieures des échelles nord et du milieu ; l'arceau est un cadre de trois traverses vissées en bout entre les profils
# mobiles des deux coulisses. Deux bacs rigides du commerce (IKEA HÅLLBAR 35 L) l'un derrière l'autre, posés par leur
# lèvre avant et arrière sur les traverses : on tire l'arceau, on soulève un bac, l'autre reste.
# Ce qui ne change pas (repris de modele.py) : les trois échelles, leurs écharpes et leurs vérins, les deux rails au sol,
# le plan de travail, la machine et ses tuyaux. Ce qui disparaît : le L, ses barres, ses sacs, la butée.
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

cm, f = PL.cm, PL.f

ID = "arceau"
TITRE = "Variante 3 · Meuble ouvert, coulisses et arceau"
RESUME = ("Sans porte : un arceau de trois traverses sur deux coulisses à sortie totale, deux bacs HÅLLBAR de 35 L "
          "posés dessus l'un derrière l'autre ; on jette dans le bac avant par la fente sous le plan, on tire l'arceau "
          "et on soulève le bac pour l'emporter.")
RELEVE = "01/11/2026"

# ------------------------------------------------------------------ ce qu'on reprend du meuble actuel
# Ossature (échelles, écharpes, vérins, rails au sol), plan, machine et tuyaux ; sans le L, ses barres, ses sacs, ni la
# butée (tire-fonds plantés dans les écharpes).
BASE = [b for b in CO.bas() if b.groupe != "bac" and not b.nom.startswith("butee_vis")]
assert not [b for b in BASE if b.role in ("facade", "sac", "barre", "support")], "plus rien du L"
_en, _ec = M.ECHELLES["n"], M.ECHELLES["c"]
YI0, YI1 = _en["av"].y1, _ec["av"].y0           # faces intérieures des échelles du linge : 4,1 et 46,4
X_PIED = (_en["av"].x0 + _en["av"].x1) / 2      # axe des vérins avant : ligne de basculement vers la pièce

# ------------------------------------------------------------------ bacs : IKEA HÅLLBAR 35 L (sans couvercle)
# Fiche IKEA (relevé en ligne du RELEVE, ikea.com/be/fr, réf. 504.202.06) : haut 38,8 × 25,1, bas 30,3 × 18,3, hauteur
# 55, 35 L, poignées intégrées, 14,99 €. Le long côté (38,8) va en travers de l'alcôve (y), le court (25,1) en profondeur.
# Deux bacs côte à côte demanderaient 2 × 25,1 = 50,2 de large : il n'y a que 42,3 entre les échelles, d'où l'un
# derrière l'autre. La lèvre (débord du rebord sur la paroi) et son épaisseur ne sont pas sur la fiche : estimées, à
# mesurer en magasin ; la position des traverses en dépend.
BAC = dict(nom="IKEA HÅLLBAR 35 L, gris clair", ref="504.202.06", l=38.8, p=25.1, l_bas=30.3, p_bas=18.3, h=55,
           litres=35, prix=14.99, levre=1.0, rebord=0.3, masse=1.0, linge=4.0,
           url="https://www.ikea.com/be/fr/p/hallbar-poubelle-avec-couvercle-gris-clair-50420206")
# masse du bac vide et du linge sale d'un bac plein (≈ 0,11 kg/L tassé à la main) : estimations, de mémoire

# ------------------------------------------------------------------ coulisses
# Paire de coulisses à billes à sortie totale, montage latéral, hauteur 45, épaisseur 12,7 (cote d'usage des coulisses
# latérales, de mémoire), longueur 550. Leroy Merlin vend une gamme de 250 à 700, sortie totale, portée 50 kg la paire
# (600 relevée à 13,90 € en ligne le RELEVE ; le 550 n'est pas relevé) ; Hettich KA 5632 et Emuca 45 × 550 existent aussi.
COUL = dict(L=55.0, h=4.5, e=1.27, charge=50, prix=13.90, nom="paire de coulisses à billes sortie totale 550, H 45, 50 kg",
            source="Leroy Merlin (gamme 250 à 700 ; 600 relevée à 13,90 € le " + RELEVE + ", 550 à vérifier)",
            url="https://www.leroymerlin.fr/produits/600mm-paire-de-coulisses-pour-tiroir-a-billes-h-45mm-sortie-totale-avec-fermeture-standard-guides-rails-coulissants-portee-50kg-84639744.html")
XC0 = M.FACE                                    # avant des coulisses au nu du plan : 174
XC1 = XC0 + COUL["L"]                           # arrière : 229, la face arrière des montants arrière
assert XC1 <= M.XO1 + 1e-9, "les coulisses tiennent entre le nu du plan et l'arrière des montants"
YM0, YM1 = YI0 + COUL["e"], YI1 - COUL["e"]     # faces intérieures des profils mobiles : 5,37 et 45,13
COURSE = COUL["L"]                              # sortie totale
LEVE = 32                                       # bac soulevé de tant dans les dessins

# ------------------------------------------------------------------ l'arceau : trois traverses
# Tasseau de 38 × 38 refendu en deux à la scie circulaire (trait de 2 mm) : 18 × 38, posé sur chant. Chaque traverse va
# d'un profil mobile à l'autre, vissée en bout à travers le profil (2 vis 4 × 40). Avant, milieu, arrière ; les bacs
# reposent par leur lèvre avant et arrière, le corps pendu entre deux traverses avec JEU_X de chaque côté.
TR = dict(e=(M.DE - 0.2) / 2, h=M.DL)           # 1,8 × 3,8
JEU_X = 0.3
_pc = BAC["p"] - 2 * BAC["levre"]               # corps du bac sous la lèvre, en profondeur : 23,1
_lc = BAC["l"] - 2 * BAC["levre"]               # en largeur : 36,8
# d'avant en arrière : traverse avant, jeu, corps du bac avant, jeu, traverse du milieu, jeu, corps du bac arrière, jeu,
# traverse arrière
_xs = [XC0]
for _w in (TR["e"], JEU_X, _pc, JEU_X, TR["e"], JEU_X, _pc, JEU_X, TR["e"]):
    _xs.append(_xs[-1] + _w)
X_TR = [(_xs[0], _xs[1]), (_xs[4], _xs[5]), (_xs[8], _xs[9])]
X_CORPS = [(_xs[2], _xs[3]), (_xs[6], _xs[7])]
X_LEVRE = [(a - BAC["levre"], b + BAC["levre"]) for a, b in X_CORPS]
assert X_TR[2][1] <= XC1 + 1e-9, "la traverse arrière est sur le profil mobile"
assert X_LEVRE[0][1] < X_LEVRE[1][0], "les lèvres des deux bacs ne se chevauchent pas sur la traverse du milieu"
APPUI = BAC["levre"] - JEU_X                    # largeur de lèvre posée sur chaque traverse : 0,7
assert X_TR[0][0] <= X_LEVRE[0][0] < X_TR[0][1] and X_TR[1][0] < X_LEVRE[0][1] <= X_TR[1][1], "bac avant sur F et M"
assert X_TR[1][0] <= X_LEVRE[1][0] < X_TR[1][1] and X_TR[2][0] < X_LEVRE[1][1] <= X_TR[2][1], "bac arrière sur M et R"
# en largeur : le rebord tient entre les profils mobiles
YC = (YI0 + YI1) / 2
Y_LEVRE = (YC - BAC["l"] / 2, YC + BAC["l"] / 2)
Y_CORPS = (YC - _lc / 2, YC + _lc / 2)
JEU_Y = Y_LEVRE[0] - YM0                        # entre le rebord et chaque profil mobile : 0,48
assert JEU_Y >= 0.3, "le rebord du bac passe entre les deux coulisses"
assert BAC["l"] < YM1 - YM0 and 2 * BAC["p"] > YM1 - YM0, "un bac en travers ; deux côte à côte ne passent pas"

# ------------------------------------------------------------------ hauteurs
# Le fond du bac passe à JEU_FOND au-dessus des rails au sol (le rail avant est sous la course) ; la lèvre est sur les
# traverses ; la coulisse est centrée sur les traverses (vis dans l'axe).
JEU_FOND = 1.0
Z_RAIL = M.RAILS[0].z1                          # dessus des rails : 5,8
Z_FOND = Z_RAIL + JEU_FOND                      # 6,8
Z_BORD = Z_FOND + BAC["h"]                      # dessus du rebord : 61,8
Z_TR1 = Z_BORD - BAC["rebord"]                  # dessus des traverses, dessous du rebord : 61,5
Z_TR0 = Z_TR1 - TR["h"]
ZC0 = (Z_TR0 + Z_TR1) / 2 - COUL["h"] / 2       # coulisses : 57,35 → 61,85
ZC1 = ZC0 + COUL["h"]
FENTE = M.Z_PLAN - max(Z_BORD, ZC1)             # entre le haut du bac avant et le dessous du plan : 23,7
assert FENTE > 20, "fente pour jeter le linge, arceau rentré"
for e_ in (_en, _ec):                           # les coulisses ne croisent ni les lisses ni le plan
    assert e_["basse"].z1 < ZC0 and ZC1 < e_["barre"].z0, "coulisse entre la lisse basse et la lisse de barre"


def _x_echarpe(z):
    """Étendue en x de l'écharpe de l'échelle nord au niveau z (bord avant, bord arrière)."""
    return CO._coupe_z(next(c for c in M.ECHARPES if c.nom == "echarpe_n"), z)


_ea, _eb = _x_echarpe(ZC0), _x_echarpe(ZC1)
X_ECHARPE = (min(_ea[0], _eb[0]), max(_ea[1], _eb[1]))   # appui du milieu de la coulisse, sur l'écharpe
APPUIS = [(_en["av"].x0, _en["av"].x1), X_ECHARPE, (_en["ar"].x0, _en["ar"].x1)]
assert all(XC0 <= a and b <= XC1 for a, b in APPUIS), "trois appuis sous chaque coulisse : montant avant, écharpe, montant arrière"
PORTEE = max(b0 - a1 for (_, a1), (b0, _) in zip(APPUIS, APPUIS[1:]))   # plus grand vide entre deux appuis

# ------------------------------------------------------------------ pièces
ARCEAU = "arceau"


def pieces():
    """Coulisses (profil fixe), traverses, bacs ; arceau rentré, bacs posés."""
    r = []
    for k, (y0, y1) in (("n", (YI0, YM0)), ("c", (YM1, YI1))):
        r.append(M.Bloc("vis", f"coulisse_{k}", XC0, XC1, y0, y1, ZC0, ZC1, groupe="coulisse"))
    for k, (x0, x1) in zip(("avant", "milieu", "arriere"), X_TR):
        r.append(M.Bloc("bois", f"traverse_{k}", x0, x1, YM0, YM1, Z_TR0, Z_TR1, groupe=ARCEAU))
    for k, ((c0, c1), (l0, l1)) in enumerate(zip(X_CORPS, X_LEVRE)):
        r += bac(f"bac_{k + 1}", c0, c1, l0, l1)
    return r


EP_BAC = 0.3            # paroi du bac (dessin)


def bac(nom, c0, c1, l0, l1):
    """Un bac ouvert : parois avant et arrière inclinées (le corps se resserre vers le fond), deux côtés, un fond, un
    rebord en cadre. Les côtés sont dessinés droits (la fiche donne 38,8 en haut, 30,3 en bas)."""
    e, rb = EP_BAC, (_pc - BAC["p_bas"]) / 2
    y0, y1 = Y_CORPS
    zf, zt = Z_FOND, Z_TR1
    g = dict(groupe=ARCEAU)
    return [
        M.Profil("bac", f"{nom}_avant", [(c0, zt), (c0 + e, zt), (c0 + rb + e, zf), (c0 + rb, zf)], y0 + e, y1 - e, **g),
        M.Profil("bac", f"{nom}_arriere", [(c1 - e, zt), (c1, zt), (c1 - rb, zf), (c1 - rb - e, zf)], y0 + e, y1 - e, **g),
        M.Profil("bac", f"{nom}_cote_n", [(c0, zt), (c1, zt), (c1 - rb, zf), (c0 + rb, zf)], y0, y0 + e, **g),
        M.Profil("bac", f"{nom}_cote_s", [(c0, zt), (c1, zt), (c1 - rb, zf), (c0 + rb, zf)], y1 - e, y1, **g),
        M.Bloc("bac", f"{nom}_fond", c0 + rb + e, c1 - rb - e, y0 + e, y1 - e, zf, zf + e, **g),
        M.Bloc("bac", f"{nom}_rebord_av", l0, c0 + e, Y_LEVRE[0], Y_LEVRE[1], zt, Z_BORD, **g),
        M.Bloc("bac", f"{nom}_rebord_ar", c1 - e, l1, Y_LEVRE[0], Y_LEVRE[1], zt, Z_BORD, **g),
        M.Bloc("bac", f"{nom}_rebord_n", c0 + e, c1 - e, Y_LEVRE[0], y0 + e, zt, Z_BORD, **g),
        M.Bloc("bac", f"{nom}_rebord_s", c0 + e, c1 - e, y1 - e, Y_LEVRE[1], zt, Z_BORD, **g),
    ]


def deplacer(b, dx=0.0, dz=0.0):
    if isinstance(b, M.Profil):
        return M.replace(b, xz=[(x + dx, z + dz) for x, z in b.xz])
    return M.replace(b, x0=b.x0 + dx, x1=b.x1 + dx, z0=b.z0 + dz, z1=b.z1 + dz)


def etat(sortie=0.0, leve=None):
    """Pièces de la variante, arceau sorti de `sortie`, bacs soulevés {numéro: dz}. Sorti, le profil mobile de chaque
    coulisse est dessiné devant le profil fixe."""
    leve = leve or {}
    r = []
    for b in pieces():
        if b.groupe == ARCEAU:
            n = int(b.nom.split("_")[1]) if b.nom.startswith("bac_") else 0
            r.append(deplacer(b, -sortie, leve.get(n, 0)))
        else:
            r.append(b)
            if sortie > 0:
                r.append(M.replace(b, nom=b.nom + "_mobile", x0=b.x0 - sortie, x1=b.x0))
    return r


NOUVELLES = {b.nom for b in pieces() if b.role != "bac"} | {b.nom + "_mobile" for b in pieces() if b.groupe == "coulisse"}


def _collisions(bl):
    """Paires de pièces dont les boîtes se recouvrent (au-delà d'un contact)."""
    e, r = 1e-6, []
    for i, a in enumerate(bl):
        for b in bl[i + 1:]:
            if (a.x0 < b.x1 - e and b.x0 < a.x1 - e and a.y0 < b.y1 - e and b.y0 < a.y1 - e and a.z0 < b.z1 - e
                    and b.z0 < a.z1 - e):
                r.append((a.nom, b.nom))
    return r


# rien ne traverse : ni rentré, ni sorti, ni avec le bac arrière soulevé (boîtes des pièces ; les écharpes, en biais,
# sont vérifiées à part)
_ok = set()
for _s, _lv in ((0, {}), (COURSE, {}), (COURSE, {2: LEVE})):
    _bl = BASE + etat(_s, _lv)
    _new = {b.nom for b in etat(_s, _lv)}
    _c = [p for p in _collisions(_bl) if (p[0] in _new or p[1] in _new) and p not in _ok and p[::-1] not in _ok]
    _c = [p for p in _c if not any(n.startswith("echarpe") for n in p)]
    assert not _c, (_s, _c)
for _b in pieces():                             # les écharpes, vraies formes : pas de pièce nouvelle dedans
    if _b.role == "vis":
        continue
    for _e in M.ECHARPES:
        assert _b.y0 >= _e.y1 - 1e-6 or _b.y1 <= _e.y0 + 1e-6, (_b.nom, _e.nom)

# sorti, le bac arrière quitte l'aplomb du plan : on le soulève tout droit
DEGAGE = M.FACE - (X_LEVRE[1][1] - COURSE)      # entre l'arrière du rebord du bac arrière et le chant du plan : 3,3
assert DEGAGE >= 1, "sorti, le bac arrière n'est plus sous le plan"
# rentré, le bac avant est sous la fente : son rebord avant est derrière le nu du plan
assert X_LEVRE[0][0] >= M.FACE
# porte d'entrée : vantail ouvert à 90° à X_PORTE ; l'arceau rentré n'avance pas devant le nu du plan
X_PORTE = M.PORTE["x1"]
PORTE_JEU = M.FACE - X_PORTE                    # 9
PORTE_SORTIE = PORTE_JEU                        # on peut sortir l'arceau de tant porte grande ouverte
assert XC0 - COURSE < X_PORTE, "sorti, l'arceau entre dans le débattement de la porte"


# ------------------------------------------------------------------ efforts et stabilité (estimations)
def _volume(b):
    if isinstance(b, M.Profil):
        p = b.xz
        return abs(sum(x0 * z1 - x1 * z0 for (x0, z0), (x1, z1) in zip(p, p[1:] + p[:1]))) / 2 * (b.y1 - b.y0)
    return (b.x1 - b.x0) * (b.y1 - b.y0) * (b.z1 - b.z0)


def _cx(b):
    if isinstance(b, M.Profil):
        return sum(x for x, _ in b.xz) / len(b.xz)
    return (b.x0 + b.x1) / 2


DENSITE = dict(sapin=0.45, chene=0.70)          # g/cm³, de mémoire
_stab = [(b, DENSITE["chene"] if b.role == "plan" else DENSITE["sapin"]) for b in BASE if b.role in ("bois", "plan")]
MASSE_FIXE = sum(_volume(b) * d for b, d in _stab) / 1000                       # kg : échelles, rails, plan
M_STAB = sum(_volume(b) * d / 1000 * (_cx(b) - X_PIED) for b, d in _stab)       # kg·cm, vers l'arrière
MOBILE_COUL = 0.8                               # kg, profils mobiles et intermédiaires de la paire (estimé)


def charge(sortie):
    """Masse portée par l'arceau (kg) et son moment autour des vérins avant (kg·cm, positif vers la pièce)."""
    q = [(BAC["masse"] + BAC["linge"], (a + b) / 2 - sortie) for a, b in X_CORPS]
    q.append((MOBILE_COUL, XC0 + COURSE / 2 - sortie))
    q += [(TR["e"] * TR["h"] * (YM1 - YM0) * DENSITE["sapin"] / 1000, (a + b) / 2 - sortie) for a, b in X_TR]
    m = sum(w for w, _ in q)
    return m, sum(w * (X_PIED - x) for w, x in q)


MASSE_ARCEAU, M_SORTI = charge(COURSE)
SECURITE = M_STAB / M_SORTI                     # sans les coins de calage ni le joint silicone
X_POIGNEE = (X_TR[0][0] + X_TR[0][1]) / 2 - COURSE
APPUI_MAX = (M_STAB - M_SORTI) / (X_PIED - X_POIGNEE)   # kg posés sur la traverse avant sortie qui font basculer
assert SECURITE > 1, "à vide de personne, le meuble ne bascule pas, bacs pleins et arceau sorti"
# par coulisse, arceau sorti : vis du montant avant (cisaillement) et du montant arrière (arrachement)
_q = MASSE_ARCEAU / 2
_xq = X_PIED - (sum((a + b) / 2 for a, b in X_CORPS) / 2 - COURSE)   # bras de la charge devant le montant avant
_l = (APPUIS[2][0] + APPUIS[2][1]) / 2 - (APPUIS[0][0] + APPUIS[0][1]) / 2
EFFORT = dict(par_coulisse=_q, arriere=_q * _xq / _l * 9.81, avant=_q * (1 + _xq / _l) * 9.81)   # kg, N, N

# ------------------------------------------------------------------ poteau de niche : ce qui empêche de basculer
# Sans lui, il suffit d'≈ APPUI_MAX kg sur la traverse avant sortie pour soulever l'arrière du meuble (les coins de calage
# et le joint silicone aident, sans chiffre sûr). Un tasseau debout dans le coin nord du fond de la niche, entre le dessus
# du plan et le dessous du caisson haut (lui-même chevillé au mur) : quand l'arrière du plan veut monter, il pousse le
# poteau contre le caisson haut. Il ne travaille qu'en compression : coupé à la hauteur de la niche plus 1 mm, enfoncé au
# maillet, une équerre en pied vissée dans le plan pour qu'il ne tombe pas. Rien n'est vissé au mur, le caisson haut
# ne change pas (c'est la cale de pose de l'étape 9 du meuble actuel, laissée en place).
_chn = next(b for b in M.PIECES if b.nom == "ch_cote_n")
_chf = next(b for b in M.PIECES if b.nom == "ch_fond_n")
POTEAU = M.Bloc("bois", "poteau_niche", _chf.x0 - M.DL, _chf.x0, _chn.y0, _chn.y0 + M.DE, M.Z_DESSUS, M.Z_HAUT,
                groupe="poteau")
assert M.Z_HAUT == _chn.z0, "le poteau bute sous le côté et le dessous du caisson haut"
assert POTEAU.x0 > M.CH["x0"] and POTEAU.x1 <= M.X1 and POTEAU.x0 < M.PLAN_X1, "sous le caisson haut, sur le plan"
for _q in (M.PRISES, M.ARRIVEE, M.SIPHON):
    assert POTEAU.y1 < _q.y0, "le poteau est loin du robinet, de l'arrivée et des prises"
assert POTEAU.y1 < M.TRAPPE["y0"], "pas sur l'encoche du passe-tuyau"
H_POTEAU = M.Z_HAUT - M.Z_DESSUS


def poussee(appui):
    """Effort (kgf) dans le poteau, arceau sorti, bacs pleins, `appui` kg posés sur la traverse avant."""
    return max(0.0, (appui * (X_PIED - X_POIGNEE) + M_SORTI - M_STAB) / ((POTEAU.x0 + POTEAU.x1) / 2 - X_PIED))


APPUI_TEST = 30                                 # kg : un adulte qui s'appuie sur l'arceau sorti
POUSSEE = poussee(APPUI_TEST)


# ------------------------------------------------------------------ dessins
def _murs_dessus():
    return [PL.rect(M.X1 - M.ALCOVE["nord"], M.Y0 - 4, M.X1 + 4, M.Y0, "omurc"),
            PL.rect(M.X1 - M.ALCOVE["sud"], M.Y1, M.X1 + 4, M.Y1 + 4, "omurc"),
            PL.rect(M.X1, M.Y0, M.X1 + 4, M.Y1, "omurc")]


def _porte_dessus():
    """Vantail de la porte d'entrée ouvert à 90° (épaisseur 4, estimée) et son débattement, au mur nord."""
    x1, l = M.PORTE["x1"], M.PORTE["l"]
    o = [PL.rect(M.PORTE["x0"] - 30, M.Y0 - 4, M.PORTE["x0"], M.Y0, "omurc"),
         PL.rect(x1, M.Y0 - 4, M.X1 - M.ALCOVE["nord"], M.Y0, "omurc"),
         PL.rect(x1 - 4, M.Y0, x1, M.Y0 + l, "ofac"),
         f'<path class="oswing" d="M {f(x1 - l)} {f(M.Y0)} A {f(l)} {f(l)} 0 0 0 {f(x1)} {f(M.Y0 + l)}"/>']
    return o


def dessus():
    """Vue de dessus coupée au niveau des coulisses : arceau rentré, et sorti en tireté ; la porte d'entrée ouverte."""
    zs = (Z_TR0 + Z_TR1) / 2
    o = _murs_dessus() + _porte_dessus()
    o += CO.projeter([b for b in BASE + etat(0) if b.role != "plan"], "dessus", zs)
    for b in etat(COURSE):
        if b.groupe == ARCEAU or b.nom.endswith("_mobile"):
            o.append(PL.poly(CO.contour(b, "dessus", zs), "oswing"))
    pl = CO.nom("plan_travail")
    o.append(PL.poly([(pl.x0, pl.y0), (pl.x1, pl.y0), (pl.x1, pl.encoche[2]), (pl.encoche[0], pl.encoche[2]),
                      (pl.encoche[0], pl.encoche[3]), (pl.x1, pl.encoche[3]), (pl.x1, pl.y1), (pl.x0, pl.y1)], "oplanl"))
    # en profondeur : course, coulisse, lame derrière ; au-dessous, les rebords des deux bacs
    o.append(CO.chaine_h([XC0 - COURSE, XC0, XC1, M.X1], M.Y0 - 17, ext=M.Y0 - 4))
    o.append(PL.text(XC0 - COURSE / 2, M.Y0 - 21.5, "course de l'arceau (sortie totale)", "lt muted"))
    o.append(PL.text((XC0 + XC1) / 2, M.Y0 - 21.5, "coulisse", "lt muted"))
    o.append(CO.chaine_h([X_LEVRE[0][0], X_LEVRE[0][1], X_LEVRE[1][0], X_LEVRE[1][1]], M.Y0 - 8, ext=M.Y0 - 4))
    for (a, b), t in zip(X_CORPS, ("bac avant", "bac arrière")):
        o.append(PL.text((a + b) / 2, YC + 1, t, "lt"))
        o.append(PL.text((a + b) / 2 - COURSE, YC + 1, t, "lt muted"))
    o.append(PL.text(XC0 - COURSE / 2, YI1 + 4.5, "arceau sorti (tireté)", "lt"))
    # en largeur
    o.append(CO.chaine_v([M.Y0, YI0, Y_LEVRE[0], Y_LEVRE[1], YI1, _ec["av"].y1], M.X1 + 9, ext=M.X1))
    o.append(CO.cote_v(M.Y0, M.Y1, M.X1 + 17, cm(M.Y1 - M.Y0)))
    # porte : 9 devant le nu, arceau sorti dans le débattement
    o.append(CO.cote_h(X_PORTE, M.FACE, M.Y0 + 60, cm(PORTE_JEU), ext=M.Y0 + 48))
    o.append(PL.text(X_PORTE - 5, M.Y0 + 70, "vantail de la porte d'entrée,", "lt", "end"))
    o.append(PL.text(X_PORTE - 5, M.Y0 + 73.4, "ouvert à 90°, et son débattement", "lt", "end"))
    o.append(PL.text((M.MACHINE.x0 + M.MACHINE.x1) / 2, (M.LLZ["y0"] + M.LLZ["y1"]) / 2 + 1, "machine", "lt"))
    o.append(PL.text(M.X1 - M.ALCOVE["sud"] - 1, M.Y1 + 3.4, "mur sud", "lt muted", "end"))
    o.append(PL.text(M.PORTE["x0"] - 1, M.Y0 - 5.4, "mur nord", "lt muted", "start"))
    return CO.svg(M.PORTE["x0"] - 6, M.Y0 - 25, M.X1 + 26, M.Y1 + 8, o, "Vue de dessus de l'alcôve, variante 3")


def face():
    """Vue de face depuis la salle de bain, arceau rentré : la fente pour jeter, la place en largeur."""
    h = M.Z_DESSUS + 8
    o = [PL.rect(M.Y0, -h, M.Y1, 0, "omur"), PL.rect(M.Y0 - 4, -h, M.Y0, 0, "omurc"), PL.rect(M.Y1, -h, M.Y1 + 4, 0, "omurc"),
         f'<line class="osol" x1="{f(M.Y0 - 6)}" y1="0" x2="{f(M.Y1 + 6)}" y2="0"/>']
    o += CO.projeter(BASE + etat(0), "face")
    o.append(CO.hublot(M.MACHINE, "face"))
    o.append(PL.text(YC, -(Z_FOND + Z_TR0) / 2, "bac avant", "lt"))
    o.append(PL.text(YC, -(Z_FOND + Z_TR0) / 2 + 3.4, "(le bac arrière derrière)", "lt muted"))
    o.append(PL.text(YC - 3, -(Z_BORD + M.Z_PLAN) / 2 + 1, "fente pour jeter", "lt"))
    o.append(PL.text((M.LLZ["y0"] + M.LLZ["y1"]) / 2, -(M.Z_PLAN - 12), "machine", "lt"))
    o.append(CO.cote_v(-Z_BORD, -M.Z_PLAN, YI1 - 4, cm(FENTE)))
    o.append(CO.chaine_h([M.Y0, YI0, Y_LEVRE[0], Y_LEVRE[1], YI1, _ec["av"].y1], 6, ext=0))
    o.append(PL.text(M.Y0, 12.5, f"{cm(YI1 - YI0)} entre les échelles : coulisse de 12,7 mm et 4,8 mm de jeu de chaque "
                     "côté du rebord", "lt muted", "start"))
    o.append(CO.niveaux([(Z_FOND, f"{cm(Z_FOND)} fond des bacs", Y_CORPS[0]),
                         (ZC0, f"{cm(ZC0)} bas des coulisses", YI0), (Z_BORD, f"{cm(Z_BORD)} haut des bacs", Y_LEVRE[0]),
                         (M.Z_PLAN, f"{cm(M.Z_PLAN)} dessous du plan", M.Y0),
                         (M.Z_DESSUS, f"{cm(M.Z_DESSUS)} dessus du plan", M.Y0)], M.Y0 - 9))
    o.append(PL.text(M.Y0 - 0.6, -h - 1, "nord", "lt muted", "end"))
    o.append(PL.text(M.Y1 + 0.6, -h - 1, "sud", "lt muted", "start"))
    return CO.svg(M.Y0 - 46, -h - 8, M.Y1 + 10, 17, o, "Vue de face, arceau rentré")


def coupe():
    """Coupe par le milieu des bacs, vue vers le nord : rentré en plein ; sorti, bac arrière soulevé, en tireté."""
    s = YC
    h = M.Z_HAUT + 10
    o = [PL.rect(M.X1, -h, M.X1 + 4, 0, "omurc"),
         f'<line class="osol" x1="{f(XC0 - COURSE - 8)}" y1="0" x2="{f(M.X1 + 4)}" y2="0"/>',
         PL.rect(M.CH["x0"], -h + 2, M.X1, -M.Z_HAUT, "ocache")]
    o += CO.projeter(BASE + etat(0) + [POTEAU], "cote", s)
    o.append(PL.text((M.CH["x0"] + M.X1) / 2, -M.Z_HAUT - 3.2, "caisson haut, chevillé au mur", "lt muted"))
    o.append(CO.etiquette(POTEAU.x0, -(M.Z_DESSUS + M.Z_HAUT) / 2, POTEAU.x0 - 12, -(M.Z_DESSUS + M.Z_HAUT) / 2 - 6,
                          f"poteau de niche ({cm(H_POTEAU)}) : l'arrière du plan ne peut pas monter", "end"))
    for b in etat(COURSE, {2: LEVE}):
        if b.groupe == ARCEAU or b.nom.endswith("_mobile"):
            o.append(PL.poly(CO.contour(b, "cote", s), "oswing"))
    o.append(CO.chaine_h([XC0 - COURSE, XC0, XC1, M.X1], 6, ext=0))
    o.append(PL.text(XC0 - COURSE / 2, 12.5, "course de l'arceau", "lt muted"))
    o.append(PL.text((XC0 + XC1) / 2, 12.5, "coulisse", "lt muted"))
    zd = Z_BORD + LEVE + 4
    o.append(CO.cote_h(X_LEVRE[1][1] - COURSE, M.FACE, -zd, cm(DEGAGE), ext=-M.Z_DESSUS, place="droite"))
    o.append(PL.text(M.FACE + 6, -zd - 0.2, "entre le bac soulevé et le chant du plan", "lt muted", "start"))
    xf = (M.XO0 + M.DL + X_ECHARPE[0]) / 2 - 8
    o.append(CO.cote_v(-Z_BORD, -M.Z_PLAN, xf, cm(FENTE)))
    o.append(PL.text(xf + 1.5, -(Z_BORD + M.Z_PLAN) / 2, "fente pour jeter", "lt", "start"))
    o.append(PL.text(sum(X_CORPS[0]) / 2, -30, "bac avant", "lt"))
    o.append(PL.text(sum(X_CORPS[1]) / 2, -30, "bac arrière", "lt"))
    o.append(PL.text(sum(X_CORPS[0]) / 2 - COURSE, -30, "sorti", "lt muted"))
    o.append(PL.text(sum(X_CORPS[1]) / 2 - COURSE, -(Z_FOND + LEVE + 36), "bac arrière", "lt muted"))
    o.append(PL.text(sum(X_CORPS[1]) / 2 - COURSE, -(Z_FOND + LEVE + 36) + 3.4, "soulevé", "lt muted"))
    o.append(CO.etiquette(sum(X_TR[0]) / 2 - COURSE, -(Z_TR0 + Z_TR1) / 2, XC0 - COURSE - 4, -Z_TR1 - 9,
                          "traverse avant (poignée)", "end"))
    o.append(CO.niveaux([(Z_FOND, f"{cm(Z_FOND)} fond des bacs", XC0 - COURSE),
                         (Z_RAIL, f"{cm(Z_RAIL)} dessus des rails", XC0 - COURSE),
                         (Z_BORD, f"{cm(Z_BORD)} haut des bacs", XC0 - COURSE),
                         (M.Z_PLAN, f"{cm(M.Z_PLAN)} dessous du plan", M.FACE),
                         (M.Z_HAUT, f"{cm(M.Z_HAUT)} dessous du caisson haut", M.CH["x0"])], XC0 - COURSE - 30))
    o.append(PL.text(M.X1 - 3, -h - 1.4, "mur du fond", "lt muted", "end"))
    return CO.svg(XC0 - COURSE - 80, -h - 8, M.X1 + 8, 17, o, "Coupe par les bacs, vue vers le nord")


def _zoom(b, k):
    """Pièce agrandie k fois (détails) : les traits et les textes gardent leur taille."""
    if isinstance(b, M.Profil):
        return M.replace(b, xz=[(x * k, z * k) for x, z in b.xz], y0=b.y0 * k, y1=b.y1 * k)
    return M.replace(b, x0=b.x0 * k, x1=b.x1 * k, y0=b.y0 * k, y1=b.y1 * k, z0=b.z0 * k, z1=b.z1 * k)


K_DET = 10


def detail_face():
    """Détail de la vue de face, côté nord, agrandi : échelle, coulisse, traverse avant, rebord du bac."""
    k = K_DET
    o = CO.projeter([_zoom(b, k) for b in BASE + etat(0)], "face")
    ys = [YI0, YM0, Y_LEVRE[0], Y_CORPS[0]]
    for (a, b), t in zip(zip(ys, ys[1:]), ("12,7", "4,8", "10")):
        o.append(CO.cote_h(a * k, b * k, -Z_TR0 * k + 8, t, ext=-Z_TR0 * k))
    o.append(CO.cote_v(-ZC0 * k, -ZC1 * k, YI0 * k - 4, "45", ext=YI0 * k))
    o.append(CO.cote_v(-Z_TR0 * k, -Z_TR1 * k, Y_CORPS[0] * k + 30, "38", ext=Y_CORPS[0] * k + 20))
    o.append(PL.text(YI0 * k - 1, -ZC1 * k - 6, "échelle nord", "lt", "end"))
    o.append(PL.text((YI0 + YM0) / 2 * k, -ZC1 * k - 6, "coulisse", "lt"))
    o.append(CO.etiquette((Y_CORPS[0] + 3) * k, -Z_BORD * k + 0.4, (Y_CORPS[0] + 3) * k + 8, -Z_BORD * k - 6,
                          "rebord du bac (lèvre estimée)", "start"))
    o.append(CO.etiquette((Y_CORPS[0] + 3) * k, -(Z_TR0 + Z_TR1) / 2 * k, (Y_CORPS[0] + 3) * k + 8,
                          -(Z_TR0 + Z_TR1) / 2 * k, "traverse avant 18 × 38", "start"))
    o.append(PL.text(Y_CORPS[0] * k + 2, -Z_TR0 * k + 14.5, "bac avant", "lt muted", "start"))
    return CO.svg(M.Y0 * k - 30, -ZC1 * k - 12, (Y_CORPS[0] + 12) * k, -Z_TR0 * k + 18, o,
                  "Détail : coulisse et traverse, côté nord")


def detail_coupe():
    """Détail de la coupe agrandi : les deux lèvres posées sur la traverse du milieu."""
    k = K_DET
    s = YC * k
    o = CO.projeter([_zoom(b, k) for b in BASE + etat(0)], "cote", s)
    t0, t1 = X_TR[1]
    xs = [X_CORPS[0][1], X_LEVRE[0][1], X_LEVRE[1][0], X_CORPS[1][0]]
    for (a, b), t in zip(zip(xs, xs[1:]), ("10", "4", "10")):
        o.append(CO.cote_h(a * k, b * k, -Z_BORD * k - 6, t, ext=-Z_BORD * k))
    for (a, b), t in zip(((X_CORPS[0][1], t0), (t0, t1), (t1, X_CORPS[1][0])), ("3", "18", "3")):
        o.append(CO.cote_h(a * k, b * k, -Z_TR0 * k + 7, t, ext=-Z_TR0 * k))
    o.append(CO.cote_v(-Z_TR0 * k, -Z_TR1 * k, t1 * k + 22, "38", ext=t1 * k))
    o.append(PL.text((t0 + t1) / 2 * k, -Z_TR0 * k + 13, "traverse du milieu", "lt"))
    o.append(PL.text(X_CORPS[0][1] * k - 10, -Z_TR0 * k - 4, "bac avant", "lt muted", "end"))
    o.append(PL.text(X_CORPS[1][0] * k + 10, -Z_TR0 * k - 4, "bac arrière", "lt muted", "start"))
    return CO.svg((t0 - 7) * k, -Z_BORD * k - 12, (t1 + 7) * k, -Z_TR0 * k + 17, o,
                  "Détail : les lèvres sur la traverse du milieu")


HAUT = [b for b in M.PIECES if b.nom == "ch_dessous"]   # le dessous du caisson haut, où bute le poteau


def iso(sortie=0.0, leve=None, titre="", haut=False):
    bl = BASE + etat(sortie, leve) + [POTEAU] + (HAUT if haut else [])
    return MO.dessin(bl, neuves=NOUVELLES | {POTEAU.nom}, reperes=False, titre=titre)


# ------------------------------------------------------------------ fiche pour le comparatif
QUINC = [
    (COUL["nom"], 1, COUL["source"], COUL["prix"]),
    (f"bac {BAC['nom']} (réf. {BAC['ref']}), couvercle laissé de côté", 2,
     f"IKEA (prix relevé sur ikea.com/be le {RELEVE}, prix France à vérifier)", BAC["prix"]),
    ("vis à bois 4 × 16 (profils fixes : 2 par appui, 3 appuis par coulisse)", 12, "Weldom, boîte déjà au meuble actuel",
     0.0),
    ("vis à bois 4 × 40 (traverses : 2 par bout, à travers le profil mobile)", 12, "Weldom, boîte déjà au meuble actuel",
     0.0),
    ("lot de 6 équerres galvanisées 50 × 50 × 35 (une au pied du poteau de niche)", 1,
     "Weldom réf. 5605252 (relevé du 13/10/2026)", M.WELDOM["equerre_a"][1]),
]
_TASSEAU = M.PANNEAUX["G"][0]["prix"]           # prix d'un tasseau de 2 m, au lot de 6
COUT = round(sum(q * p for _, q, _, p in QUINC) + _TASSEAU, 2)   # + 1 tasseau : poteau, puis le reste refendu (traverses)

FICHE = dict(
    variante=TITRE,
    lecture="un seul arceau sur une paire de coulisses à sortie totale, deux bacs posés dessus l'un derrière l'autre",
    mettre=["arceau rentré : jeter le linge par la fente sous le plan, il tombe dans le bac avant (un geste)",
            "pour le bac arrière : tirer l'arceau à fond par la traverse avant, lâcher le linge dans le bac arrière, "
            "repousser l'arceau (trois gestes)"],
    retirer=["porte d'entrée fermée, tirer l'arceau à fond (" + cm(COURSE) + ")",
             "soulever le bac voulu par ses poignées intégrées, tout droit (" + cm(DEGAGE) + " de dégagement sous le "
             "chant du plan pour le bac arrière)",
             "repousser l'arceau avec l'autre bac", "vider le bac dans le hublot à côté, le reposer sur l'arceau"],
    bouche=dict(largeur=round(_lc, 1), profondeur=round(_pc, 1), hauteur=round(Z_BORD, 1),
                fente=dict(largeur=round(YI1 - YI0, 1), hauteur=round(FENTE, 1)),
                note=f"intérieur du bac avant {cm(_lc)} × {cm(_pc)} à {cm(Z_BORD)} du sol, atteint arceau rentré par une "
                     f"fente de {cm(YI1 - YI0)} de large × {cm(FENTE)} de haut au nu du plan ; le bac arrière, même "
                     "ouverture, seulement arceau sorti"),
    contenants=dict(nombre=2, litres=BAC["litres"], independants=True,
                    note="bacs rigides HÅLLBAR 35 L, posés, on en soulève un sans toucher à l'autre"),
    pieces=4,
    pieces_note="3 traverses (un tasseau refendu) et le poteau de niche (le reste du même tasseau) ; l'ossature (3 échelles, 2 rails), le plan et la machine sont ceux du "
                "meuble actuel, sans le L (porte, plateau, contrefiches), ses supports, barres, accroche, sacs et butée",
    usinages=["refendre un tasseau 38 × 38 en deux à la scie circulaire (traverses 18 × 38)",
              "au besoin, percer le profil fixe de chaque coulisse (foret métal Ø 4) au droit du montant avant, de "
              "l'écharpe et du montant arrière"],
    quincaillerie=QUINC,
    outils=["perceuse-visseuse, forets bois Ø 2,5 et 3, foret métal Ø 4", "scie circulaire et règle (refente)",
            "scie à onglet ou égoïne (tasseaux)", "niveau, équerre, mètre, serre-joints",
            "cale de 12,7 mm et règle (écartement des coulisses)"],
    reglages=[f"écartement des échelles nord et du milieu : {cm(YI1 - YI0)} à l'avant comme à l'arrière, au mm (les "
              "coulisses à billes ne tolèrent qu'environ 1 mm)",
              f"les deux coulisses à la même hauteur ({cm(ZC0)} du sol), de niveau et parallèles",
              "longueur des traverses : écart mesuré entre les deux profils mobiles posés",
              "position des traverses : à reporter sur les bacs achetés (lèvre et corps mesurés)",
              "vérins : meuble de niveau, ou 1 à 2 mm plus bas à l'arrière pour que l'arceau ne sorte pas seul"],
    risques=[f"basculement vers la pièce, arceau sorti : sans le poteau de niche, ≈ {APPUI_MAX:.0f} kg appuyés sur la "
             f"traverse avant suffisent (marge {SECURITE:.2f} bacs pleins) ; avec, {APPUI_TEST} kg poussent le poteau "
             f"de ≈ {POUSSEE:.0f} kgf contre le caisson haut chevillé",
             "poteau de niche oublié ou retiré (pour nettoyer, changer le robinet) : le meuble redevient basculant",
             "lèvre des bacs plus étroite que les 10 mm estimés : traverses à rapprocher, appui plus court",
             "échelles qui bougent : coulisses dures ou qui coincent",
             "arceau sorti dans le débattement de la porte d'entrée",
             "bacs ouverts et visibles (pas de façade, pas de couvercle)",
             "linge lancé trop fort : tombe derrière le bac arrière, au sol sous le plan"],
    cout_estime=COUT,
    cout_note=f"paire de coulisses (prix du 600 relevé, 550 estimé), 2 bacs IKEA, 1 tasseau ; vis prises sur les boîtes "
              f"du meuble actuel ; ossature commune à toutes les variantes non comptée",
    porte_entree=f"pas de conflit arceau rentré (il reste au nu du plan, {cm(PORTE_JEU)} derrière le vantail ouvert) ; "
                 f"sorti, il entre dans le débattement : on le tire porte fermée (au plus {cm(PORTE_SORTIE)} porte ouverte)",
)


# ------------------------------------------------------------------ chapitre
def v(x, n=2):
    """Nombre décimal à la française."""
    return f"{x:.{n}f}".replace(".", ",")


def section():
    m, mom = MASSE_ARCEAU, M_SORTI
    figs = "".join([
        CO.figure("v3-dessus", "V3-1 · Plan de l'alcôve (vue de dessus, coupée au niveau des coulisses)", dessus(),
                  f"Arceau rentré en plein, sorti de {cm(COURSE)} en tireté rouge. Plan de travail en tireté brun ; "
                  f"échelles, rails et machine du meuble actuel. Le vantail de la porte d'entrée ouvert passe à "
                  f"{cm(PORTE_JEU)} devant le nu : l'arceau sorti entre dans son débattement."),
        CO.figure("v3-face", "V3-2 · Vue de face, arceau rentré", face(),
                  f"Depuis la salle de bain. Pas de façade : on voit le bac avant, la fente de {cm(FENTE)} au-dessus "
                  "et le bout des coulisses au nu du plan."),
        CO.figure("v3-coupe", "V3-3 · Coupe par les bacs (vue vers le nord)", coupe(),
                  f"Rentré en plein ; sorti à fond en tireté rouge, le bac arrière soulevé : son rebord est à "
                  f"{cm(DEGAGE)} devant le chant du plan, il monte tout droit. Au fond de la niche, le poteau entre le "
                  "plan et le caisson haut."),
    ])
    d1 = CO.figure("v3-det-face", "V3-4 · Détail : coulisse et traverse (face, côté nord)", detail_face(),
                   "Cotes en mm. Le rebord du bac passe entre les deux profils mobiles sans les toucher ; seules les "
                   "traverses le portent.")
    d2 = CO.figure("v3-det-coupe", "V3-5 · Détail : les deux lèvres sur la traverse du milieu", detail_coupe(),
                   f"Cotes en mm. {cm(APPUI * 10)} mm de chaque lèvre portent sur la traverse ; {cm(JEU_X * 10)} mm "
                   "entre le corps du bac et la traverse.")
    i1 = iso(0, titre="Arceau rentré, bacs posés", haut=True)
    i2 = iso(COURSE, {2: LEVE}, titre="Arceau sorti, bac arrière soulevé")
    return f"""<p>{escape(RESUME)}</p>
<p class="note">Lecture retenue : un seul arceau sur deux coulisses, plutôt qu'un arceau par bac sur deux rails fixes : une paire de coulisses au lieu de deux, un seul geste pour atteindre les deux bacs, et les coulisses du commerce apportent leurs butées.</p>

<h3>Principe</h3>
<p>On garde les trois échelles, les rails au sol, le plan et la machine du meuble actuel ; on retire le L, ses barres, ses sacs et sa butée. Sur la face intérieure de l'échelle nord et de celle du milieu, une coulisse à billes à sortie totale de {cm(COUL["L"])}, du nu du plan ({cm(XC0)}) à l'arrière des montants ({cm(XC1)}). Entre les deux profils mobiles, trois traverses en tasseau refendu (18 × 38) : c'est l'arceau. Deux bacs <a href="{BAC["url"]}">IKEA HÅLLBAR 35 L</a> ({cm(BAC["l"])} × {cm(BAC["p"])} en haut, {cm(BAC["h"])} de haut, poignées intégrées) y sont posés en travers, l'un derrière l'autre, par leur lèvre avant et arrière. Côte à côte, il faudrait {cm(2 * BAC["p"])} de large : il n'y a que {cm(YI1 - YI0)} entre les échelles. Au fond de la niche, un poteau de tasseau entre le plan et le caisson haut empêche le meuble de basculer quand l'arceau est sorti.</p>

<div class="feuille">{figs}</div>
<div class="grid2">{d1}{d2}</div>
<div class="grid2">
<div class="fig">{i1}<p class="cap">Rentré : rien ne dépasse du nu du plan ; le bac avant attend sous la fente. Au fond de la niche, le poteau monte jusqu'au dessous du caisson haut (seul son fond est dessiné).</p></div>
<div class="fig">{i2}<p class="cap">Sorti à fond : le bac arrière soulevé par ses poignées, le bac avant reste posé.</p></div>
</div>

<h3>Mécanisme</h3>
<p><b>Mettre le linge.</b> Arceau rentré, le haut du bac avant est à {cm(Z_BORD)} du sol et le dessous du plan à {cm(M.Z_PLAN)} : on jette par la fente de {cm(YI1 - YI0)} × {cm(FENTE)}, le linge tombe dans le bac avant, juste derrière le nu. Pour le bac arrière, on tire l'arceau à fond par la traverse avant, on lâche le linge d'en haut, on repousse.</p>
<p><b>Retirer le linge.</b> Porte d'entrée fermée, on tire l'arceau à fond et on soulève le bac voulu par ses poignées, tout droit ; l'autre reste posé. On le vide dans le hublot, juste à côté, et on le repose.</p>
<p><b>Comment ça bouge.</b> L'arceau roule sur les billes des deux coulisses, sur {cm(COURSE)} : sortie totale, sa traverse avant va de {cm(XC0)} à {cm(XC0 - COURSE)}. Le rebord des bacs passe entre les profils mobiles avec {cm(JEU_Y * 10)} mm de chaque côté ; leur fond passe à {cm(JEU_FOND * 10)} mm au-dessus du rail avant.</p>
<p><b>Ce qui porte.</b> Chaque bac pend par sa lèvre ({cm(BAC["levre"] * 10)} mm estimés, à mesurer) sur deux traverses ; chaque traverse est vissée en bout aux deux profils mobiles (deux vis 4 × 40) ; chaque coulisse est vissée par son profil fixe sur trois appuis de l'échelle : le montant avant, l'écharpe (qu'elle croise entre {cm(X_ECHARPE[0])} et {cm(X_ECHARPE[1])}) et le montant arrière, {cm(PORTEE)} au plus entre deux appuis. Le plan reste posé et vissé sur la tête des trois échelles, comme au meuble actuel ; côté linge, ce sont les échelles nord et du milieu qui le portent.</p>
<p><b>Ce qui arrête.</b> Les butées intégrées des coulisses, en fin de sortie et en fermeture : aucune butée à fabriquer. Rentré, la traverse avant affleure le nu du plan. Pour que l'arceau ne sorte pas seul : vérins réglés 1 à 2 mm plus bas à l'arrière, ou coulisses à retenue en fermeture.</p>
<p><b>Efforts.</b> Bacs pleins (≈ {cm(BAC["linge"])} kg de linge et {cm(BAC["masse"])} kg de bac chacun, estimés), l'arceau porte ≈ {cm(m)} kg : ≈ {cm(EFFORT["par_coulisse"])} kg par coulisse pour {COUL["charge"]} kg admis par paire. Sorti à fond, chaque coulisse tire sur les vis du montant arrière (≈ {EFFORT["arriere"]:.0f} N) et appuie sur celles du montant avant (≈ {EFFORT["avant"]:.0f} N) : deux vis 4 × 16 par appui suffisent dans le sapin.</p>
<p><b>Sans fixation murale.</b> Vérins au sol et coins de calage contre les murs nord et sud, comme au meuble actuel. Mais l'arceau sorti fait porte-à-faux : bacs pleins, il pousse le meuble à basculer vers la pièce autour des vérins avant ({mom:.0f} kg·cm), et les échelles, les rails et le plan ({cm(MASSE_FIXE)} kg) ne le retiennent que de {M_STAB:.0f} kg·cm (marge {v(SECURITE)}) : ≈ {APPUI_MAX:.0f} kg posés sur la traverse avant sortie le font partir, coins et joint silicone mis à part. D'où le <b>poteau de niche</b> : un tasseau de {cm(H_POTEAU)} debout dans le coin nord du fond de la niche, entre le dessus du plan et le dessous du caisson haut, qui est chevillé au mur. Quand l'arrière du plan veut monter, il pousse le poteau contre le caisson : un adulte appuyé de {APPUI_TEST} kg sur l'arceau sorti le charge de ≈ {POUSSEE:.0f} kgf, repris par les chevilles du caisson haut. Il ne travaille qu'en compression : coupé à la hauteur de la niche plus 1 mm, enfoncé au maillet, une équerre en pied vissée dans le plan. C'est la cale de pose du caisson haut, laissée en place ; rien n'est vissé au mur.</p>
<p><b>Porte d'entrée.</b> Rentré, rien ne dépasse du nu : le vantail ouvert passe à {cm(PORTE_JEU)} devant. Sorti, l'arceau va jusqu'à {cm(XC0 - COURSE)}, dans le débattement du vantail : on le tire porte fermée, comme pour charger la machine.</p>
<p class="note">Cotes HÅLLBAR d'après la fiche IKEA (relevé du {RELEVE}, ikea.com/be ; 14,99 €, prix France à vérifier). Lèvre et épaisseur du rebord, masses, densités (sapin {v(DENSITE["sapin"])}, chêne {v(DENSITE["chene"])}) : estimées, de mémoire. Coulisses : gamme Leroy Merlin H 45 à sortie totale, 50 kg la paire (600 relevée à 13,90 € le {RELEVE}, 550 à vérifier) ; épaisseur de 12,7 mm, cote d'usage à vérifier sur celles achetées.</p>"""

if __name__ == "__main__":
    print(f"fente {FENTE:.1f}  jeu_y {JEU_Y:.2f}  degage {DEGAGE:.1f}  securite {SECURITE:.2f}  appui_max {APPUI_MAX:.1f}")
    print(f"masse arceau {MASSE_ARCEAU:.1f}  fixe {MASSE_FIXE:.1f}  M_stab {M_STAB:.0f}  M_sorti {M_SORTI:.0f}")
    print(f"traverses {X_TR}  levres {X_LEVRE}  echarpe {X_ECHARPE}  portee {PORTEE:.1f}  effort {EFFORT}")
    print(f"cout {COUT}")
