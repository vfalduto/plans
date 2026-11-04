# Niveau 1 « Essentiel » du meuble bas : ossature en tasseaux gardée telle quelle, meuble ouvert, deux boîtes IKEA SAMLA de
# 45 L qui glissent par leur rebord sur quatre traverses rabotées. Module de niveaux.py, contrat dans niv_commun.py.
#
# Ce qu'on a appris en chiffrant : sans rien pour retenir l'arrière, 24 de sortie et moins de 1 kg de linge jeté à l'avant
# font basculer le panier ; d'où un petit tasseau au-dessus du rebord, à l'avant (contre-traverse), et une cordelette qui
# arrête la course. Le mur du fond sert de butée à l'entrée.
# Cotes en cm, repère de modele.py : x vers le mur du fond (234), y du nord vers le sud, z depuis le sol.

import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import modele as M  # noqa: E402
import plan as PL  # noqa: E402
import cotes as CO  # noqa: E402
import niv_commun as NC  # noqa: E402

cm, f = PL.cm, PL.f

ID = "niv1"
TITRE = "Niveau 1 · Essentiel"
RESUME = ("L'ossature en tasseaux reste, sans porte : deux boîtes IKEA SAMLA de 45 L glissent par leur rebord sur quatre "
          "traverses rabotées, chacune se tire de 38 cm pour jeter le linge et se sort à deux mains pour l'emporter.")
DATE = "04/11/2026"

# ------------------------------------------------------------------ ossature : celle du meuble actuel, sans le L ni la butée
# L'échelle nord perd son écharpe et sa lisse du milieu : le plan en tête et les deux rails en pied la lient à l'échelle du
# milieu, qui garde son écharpe. Un tasseau de moins à acheter : tout tient dans un lot et deux rabotés.
OSSATURE = [b for b in CO.bas() if b.groupe == "ossature" and not b.nom.startswith("butee_vis")
            and b.nom not in ("echarpe_n", "lisse_barre_n")]
_en, _ec, _es = M.ECHELLES["n"], M.ECHELLES["c"], M.ECHELLES["s"]
YI0, YI1 = _en["av"].y1, _ec["av"].y0           # faces intérieures des deux échelles du linge : 4,1 et 46,4
YC = (YI0 + YI1) / 2
LARGEUR = YI1 - YI0                             # 42,3
XF, XR = _en["av"].x0, _en["ar"].x1             # avant des montants avant 175,8 ; arrière des montants arrière 229
X_PIED = (_en["av"].x0 + _en["av"].x1) / 2      # axe des vérins avant : ligne de basculement du meuble

# ------------------------------------------------------------------ panier : IKEA SAMLA 56 × 39 × 28, 45 L
# Relevé sur ikea.com/fr le 04/11/2026 : 4,99 € (éco-part. comprise), 56 × 39 × 28 cm, 45 L, polypropylène, colis 1,23 kg ;
# la fiche ne décrit ni le rebord ni de poignée. Rebord, fond et épaisseurs : estimés, à mesurer en magasin.
PANIER = dict(nom="IKEA SAMLA 56 × 39 × 28, 45 L, transparent", ref="301.029.74", L=56.0, l=39.0, h=28.0, litres=45, prix=4.99,
              masse=1.23, rebord=1.5, ep_rebord=1.0, url="https://www.ikea.com/fr/fr/p/samla-boite-transparent-30102974/")
LINGE = 0.12                                    # kg/L, linge sale non tassé (estimé)
L_FOND = 47.0                                   # longueur du fond (estimé) ; la largeur du fond n'entre pas dans le calcul
EP = 0.3                                        # paroi, pour le dessin

# ------------------------------------------------------------------ traverses
# Tasseau raboté 35 × 35 de 240 refendu à 27 (Weldom réf. 9000481). La largeur se décide panier en main : le rebord doit
# reposer, le corps doit passer. 27 convient si le rebord fait bien 15 mm ; plage calculée ci-dessous.
T_L, T_H = 2.7, 3.5                             # largeur (en y), hauteur (en z)
JEU_REBORD = (LARGEUR - PANIER["l"]) / 2        # 1,65 entre le rebord et chaque échelle
APPUI = T_L - JEU_REBORD                        # 1,05 de rebord posé sur chaque traverse
JEU_CORPS = PANIER["rebord"] - APPUI            # 0,45 entre le corps du panier et chaque traverse
assert JEU_REBORD >= 0.5, "le panier passe entre les échelles"
assert APPUI >= 1.0 and JEU_CORPS >= 0.3, "le rebord repose, le corps passe"
T_MIN, T_MAX = JEU_REBORD + 1.0, JEU_REBORD + PANIER["rebord"] - 0.3   # 2,65 → 2,85 : largeur possible de refend
assert T_MIN <= T_L <= T_MAX
Y_REB = (YC - PANIER["l"] / 2, YC + PANIER["l"] / 2)
Y_CORPS = (Y_REB[0] + PANIER["rebord"], Y_REB[1] - PANIER["rebord"])
OUV_L = Y_CORPS[1] - Y_CORPS[0]                 # 36 : largeur de la bouche du panier

# ------------------------------------------------------------------ en profondeur : le mur du fond arrête le panier
X_MUR = M.X1 - 0.5                              # arrière du rebord en position rentrée (0,5 de carreau et de jeu : estimé)
X_AV = X_MUR - PANIER["L"]                      # avant du rebord, rentré : 177,5
assert X_AV > M.FACE, "rentré, le panier reste derrière le nu du plan"
assert X_MUR <= NC.BAIE["x1"], "et devant le mur du fond"

# ------------------------------------------------------------------ hauteurs
Z_RAIL = M.RAILS[0].z1                          # dessus du rail avant : 5,8
JEU_FOND = 1.0
Z1_FOND = Z_RAIL + JEU_FOND                     # panier du bas : fond à 6,8
Z1_HAUT = Z1_FOND + PANIER["h"]                 # haut du rebord à 34,8
LIBRE = M.Z_PLAN - 2 * PANIER["h"] - Z1_FOND    # reste à partager au-dessus des deux paniers : 22,7
G_HAUT = 14.0                                   # au-dessus du panier du haut, sous le plan : on y jette sans tirer
G_BAS = LIBRE - G_HAUT                          # au-dessus du panier du bas, sous le fond du panier du haut : 8,7
Z2_FOND = Z1_HAUT + G_BAS                       # 43,5
Z2_HAUT = Z2_FOND + PANIER["h"]                 # 71,5
assert abs(M.Z_PLAN - Z2_HAUT - G_HAUT) < 1e-6
assert PANIER["h"] * 2 + JEU_FOND + Z_RAIL + LIBRE <= NC.HAUT_BAIE + 1e-6, "deux paniers tiennent dans la hauteur de la baie"
assert G_BAS >= 8 and G_HAUT >= 12


def _z_tr(z_haut):
    """Dessus de traverse : dessous du rebord posé dessus."""
    return z_haut - PANIER["ep_rebord"]


# ------------------------------------------------------------------ contre-traverses : ce qui retient l'arrière
JEU_CT = 1.0                                    # entre le dessus du rebord et le dessous de la contre-traverse
CT_L = 14.2                                     # longueur : de l'avant des montants à x 190
X_CT = XF + CT_L
SORTIE = 38.0                                   # arrêt par la cordelette
SORTIE_LIBRE = X_MUR - X_CT                     # 43,5 : au-delà, le rebord arrière échappe à la contre-traverse
assert SORTIE + 5 <= SORTIE_LIBRE, "la cordelette arrête le panier avant que le rebord ne s'échappe"
X_AV_S = X_AV - SORTIE                          # 139,5 : avant du panier sorti
OUV_HAUT = M.FACE - X_AV_S                      # 34,5 : bouche dégagée devant le plan, panier du haut
OUV_BAS = X_AV - X_AV_S                         # 38 : bouche dégagée devant le panier du haut, panier du bas
SORTIE_TOTALE = X_MUR - M.FACE                  # 59,5 : le rebord arrière sort de sous le plan, le panier monte tout droit


# ------------------------------------------------------------------ pièces
def _deplacer(b, dx=0.0, dz=0.0):
    if isinstance(b, M.Profil):
        return M.replace(b, xz=[(x + dx, z + dz) for x, z in b.xz])
    return M.replace(b, x0=b.x0 + dx, x1=b.x1 + dx, z0=b.z0 + dz, z1=b.z1 + dz)


def panier(nom, zf, sortie=0.0, leve=0.0):
    """Une boîte ouverte : parois avant et arrière inclinées (le corps se resserre vers le fond), côtés dessinés droits, fond,
    rebord en cadre."""
    p = PANIER
    x0, x1 = X_AV, X_MUR
    c0, c1 = x0 + p["rebord"], x1 - p["rebord"]
    zt, zh = zf + p["h"] - p["ep_rebord"], zf + p["h"]
    y0, y1 = Y_CORPS
    rb = (c1 - c0 - L_FOND) / 2
    g = dict(groupe=nom)
    r = [M.Profil("bac", f"{nom}_avant", [(c0, zt), (c0 + EP, zt), (c0 + rb + EP, zf), (c0 + rb, zf)], y0 + EP, y1 - EP, **g),
         M.Profil("bac", f"{nom}_arriere", [(c1 - EP, zt), (c1, zt), (c1 - rb, zf), (c1 - rb - EP, zf)], y0 + EP, y1 - EP, **g),
         M.Profil("bac", f"{nom}_cote_n", [(c0, zt), (c1, zt), (c1 - rb, zf), (c0 + rb, zf)], y0, y0 + EP, **g),
         M.Profil("bac", f"{nom}_cote_s", [(c0, zt), (c1, zt), (c1 - rb, zf), (c0 + rb, zf)], y1 - EP, y1, **g),
         M.Bloc("bac", f"{nom}_fond", c0 + rb + EP, c1 - rb - EP, y0 + EP, y1 - EP, zf, zf + EP, **g),
         M.Bloc("bac", f"{nom}_rebord_av", x0, c0 + EP, Y_REB[0], Y_REB[1], zt, zh, **g),
         M.Bloc("bac", f"{nom}_rebord_ar", c1 - EP, x1, Y_REB[0], Y_REB[1], zt, zh, **g),
         M.Bloc("bac", f"{nom}_rebord_n", c0 + EP, c1 - EP, Y_REB[0], y0 + EP, zt, zh, **g),
         M.Bloc("bac", f"{nom}_rebord_s", c0 + EP, c1 - EP, y1 - EP, Y_REB[1], zt, zh, **g)]
    return [_deplacer(b, -sortie, leve) for b in r]


def supports():
    """Quatre traverses (montant avant → montant arrière) et quatre contre-traverses (à l'avant, au-dessus du rebord)."""
    r = []
    for n, zh in ((1, Z1_HAUT), (2, Z2_HAUT)):
        zt = _z_tr(zh)
        zc = zh + JEU_CT
        for k, (y0, y1), (c0, c1) in (("n", (YI0, YI0 + T_L), (YI0, YI0 + T_H)), ("s", (YI1 - T_L, YI1), (YI1 - T_H, YI1))):
            r.append(M.Bloc("bois", f"traverse_{n}{k}", XF, XR, y0, y1, zt - T_H, zt, groupe="traverses"))
            r.append(M.Bloc("bois", f"contre_{n}{k}", XF, X_CT, c0, c1, zc, zc + T_H, groupe="traverses"))
    return r


SUPPORTS = supports()
NEUVES = {b.nom for b in SUPPORTS}

# Poteau de niche : un tasseau debout dans le coin nord du fond de la niche, entre le plan et le dessous du caisson haut
# chevillé au mur (même principe que la variante à arceau). Il ne travaille qu'en compression : rien n'est vissé au mur.
_chn = next(b for b in M.PIECES if b.nom == "ch_cote_n")
_chf = next(b for b in M.PIECES if b.nom == "ch_fond_n")
POTEAU = M.Bloc("bois", "poteau_niche", _chf.x0 - T_H, _chf.x0, _chn.y0, _chn.y0 + T_H, M.Z_DESSUS, M.Z_HAUT, groupe="poteau")
H_POTEAU = M.Z_HAUT - M.Z_DESSUS
HAUT = [b for b in M.PIECES if b.nom == "ch_dessous"]
assert POTEAU.y1 < M.TRAPPE["y0"] and POTEAU.y1 < NC.ARRIVEE.y0, "le poteau reste loin du robinet et du passe-tuyau"

# Prises : un bloc de 3 prises en saillie sur le mur du fond, au-dessus de la machine, à droite du robinet d'arrêt.
# Cotes du bloc estimées (17,5 × 6 × 4) : la fiche Weldom n'a pas pu être lue.
BLOC = dict(l=17.5, h=6.0, s=4.0, y0=90.0, z0=122.0, prix=14.50, ref="5622364",
            nom="bloc 3 prises 2P+T en saillie, blanc, 16 A")
PRISES = NC.prises(n=3, y0=BLOC["y0"], z0=BLOC["z0"], largeur_poste=BLOC["l"] / 3, hauteur=BLOC["h"], saillie=BLOC["s"])
D_ROBINET = math.hypot(PRISES.y0 - M.ROBINET["y"], PRISES.z0 - M.ROBINET["z"])
assert PRISES.y1 < M.Y1 and D_ROBINET >= 20, "le bloc tient et s'écarte du robinet d'arrêt"
# Volumes de la salle de bain : volume 2 = 60 au-delà du receveur de douche (Legrand) ; le meuble est hors volume.
V2_X = M.DOUCHE[2] + 60
assert V2_X < M.FACE, "meuble et prises hors volume"
D_LAVABO = math.hypot(M.X1 - M.LAVABO[2], M.LAVABO[1] - PRISES.y1)
assert D_LAVABO >= 60, "à plus de 60 du lavabo (recommandation Engie)"


def scene(s1=0.0, s2=0.0, l1=0.0, l2=0.0):
    """Meuble, panier du bas sorti de s1 et levé de l1, panier du haut sorti de s2 et levé de l2."""
    return NC.BASE + OSSATURE + SUPPORTS + panier("bas", Z1_FOND, s1, l1) + panier("haut", Z2_FOND, s2, l2)


# ------------------------------------------------------------------ vérifications de géométrie
def _collisions(blocs, noms):
    e, r = 1e-6, []
    for i, a in enumerate(blocs):
        for b in blocs[i + 1:]:
            if a.nom not in noms and b.nom not in noms:
                continue
            if any(n.startswith("echarpe") for n in (a.nom, b.nom)):   # en biais : boîte englobante trop large, vérifié à part
                continue
            if (a.x0 < b.x1 - e and b.x0 < a.x1 - e and a.y0 < b.y1 - e and b.y0 < a.y1 - e and a.z0 < b.z1 - e
                    and b.z0 < a.z1 - e):
                # le rebord se pose exactement sur la traverse : contact, pas recouvrement ; le côté et le rebord d'un même
                # panier se touchent aussi par construction
                if a.groupe == b.groupe:
                    continue
                r.append((a.nom, b.nom))
    return r


for _s1, _s2 in ((0, 0), (SORTIE, 0), (0, SORTIE), (SORTIE, SORTIE)):
    _sc = scene(_s1, _s2)
    _n = NEUVES | {b.nom for b in _sc if b.groupe in ("bas", "haut")}
    _c = _collisions(_sc, _n)
    assert not _c, (_s1, _s2, _c)
for _e in M.ECHARPES:                           # les écharpes restent dans le plan des échelles
    for _b in SUPPORTS + panier("bas", Z1_FOND):
        assert _b.y0 >= _e.y1 - 1e-6 or _b.y1 <= _e.y0 + 1e-6, (_b.nom, _e.nom)
# le plan porte des deux côtés de la machine, sans poser sur elle
assert abs(M.Z_PLAN - NC.MACHINE.z1 - 0.5) < 1e-6, "0,5 de jeu entre la machine et le plan"
assert _ec["av"].y1 <= NC.MACHINE.y0 and NC.MACHINE.y1 <= _es["av"].y0, "une échelle de chaque côté de la machine"
assert _en["haute"].z1 == M.Z_PLAN == _es["haute"].z1 == _ec["haute"].z1

# ------------------------------------------------------------------ pourquoi il faut retenir l'arrière : le centre de gravité
P_LEV = XF                                      # le panier pivote sur le bout avant des traverses
M_LINGE = PANIER["litres"] * LINGE              # 5,4 kg
M_PLEIN = M_LINGE + PANIER["masse"]             # 6,63 kg
X_CDG = (X_AV + X_MUR) / 2                      # 205,5 : milieu du panier


def sans_retenue(s, av=None):
    """Masse de linge à l'avant (kg) qui fait basculer un panier vide sorti de s, sans contre-traverse. Le linge, jeté par
    ce qui est dégagé, tombe au milieu de cette zone."""
    a = X_AV - s
    x_p = a + PANIER["L"] / 2
    x_l = a + s / 2 if av is None else av
    if x_p <= P_LEV:
        return 0.0
    return PANIER["masse"] * (x_p - P_LEV) / (P_LEV - x_l)


S_LIBRE = X_CDG - P_LEV                         # 29,7 : plein et bien réparti, il bascule dès là
S_TEST = 24.0
M_TEST = sans_retenue(S_TEST)                   # ≈ 0,7 kg : un jean
assert M_TEST < 1, "sans retenue, un jean à l'avant fait basculer le panier"


def tas_avant(s):
    """Pire cas réaliste, sorti de s : la zone dégagée pleine de linge à l'avant, le reste du linge au milieu du panier."""
    v = min(PANIER["litres"], s * OUV_L * PANIER["h"] / 1000)
    m_av = v * LINGE
    a = X_AV - s
    return [(m_av, a + s / 2), (M_LINGE - m_av, a + PANIER["L"] / 2), (PANIER["masse"], a + PANIER["L"] / 2)]


def moment(q, x):
    """kg·cm autour de x, positif vers la pièce (vers les x petits)."""
    return sum(m * (x - xq) for m, xq in q)


_centre = [(M_PLEIN, X_CDG - SORTIE)]
_tas = tas_avant(SORTIE)
F_CT = moment(_tas, P_LEV) / CT_L               # kg, poussée du rebord sous les deux contre-traverses, pire cas
F_CT_CENTRE = moment(_centre, P_LEV) / CT_L
assert moment(_tas, P_LEV) > 0, "à 38 de sortie, le panier plein basculerait sans retenue"
assert F_CT < 10, "moins de 5 kg sous chaque contre-traverse"
PENTE = JEU_CT / CT_L                           # le panier sorti pique du nez de ce rapport
PIQUE = PENTE * (P_LEV - X_AV_S)                # 2,6 : l'avant du rebord descend d'autant
ANGLE = math.degrees(math.atan(PENTE))


# ------------------------------------------------------------------ stabilité du meuble, qui n'est pas fixé au mur
def _vol(b):
    if isinstance(b, M.Profil):
        p = b.xz
        return abs(sum(x0 * z1 - x1 * z0 for (x0, z0), (x1, z1) in zip(p, p[1:] + p[:1]))) / 2 * (b.y1 - b.y0)
    return (b.x1 - b.x0) * (b.y1 - b.y0) * (b.z1 - b.z0)


def _cx(b):
    if isinstance(b, M.Profil):
        return sum(x for x, _ in b.xz) / len(b.xz)
    return (b.x0 + b.x1) / 2


DENSITE = dict(sapin=0.45, chene=0.70)          # g/cm³, estimé
_stab = [(b, DENSITE["chene"]) for b in NC.BASE if b.role == "plan"]
_stab += [(b, DENSITE["sapin"]) for b in OSSATURE + SUPPORTS if b.role == "bois"]
MASSE_FIXE = sum(_vol(b) * d for b, d in _stab) / 1000
M_STAB = sum(_vol(b) * d / 1000 * (_cx(b) - X_PIED) for b, d in _stab)     # kg·cm vers l'arrière, paniers non comptés
M_PANIER = moment(_tas, X_PIED)                 # kg·cm vers la pièce, panier sorti, pire cas
SECURITE = M_STAB / M_PANIER
X_BORD = X_AV_S
APPUI_MAX = (M_STAB - M_PANIER) / (X_PIED - X_BORD)     # kg appuyés sur le bord avant sorti qui soulèvent l'arrière
assert SECURITE > 3, "panier plein sorti : le meuble ne bascule pas de lui-même"
APPUI_TEST = 30                                 # kg : un adulte qui s'appuie
POUSSEE = (APPUI_TEST * (X_PIED - X_BORD) + M_PANIER - M_STAB) / ((POTEAU.x0 + POTEAU.x1) / 2 - X_PIED)

# ------------------------------------------------------------------ porte de la machine et porte d'entrée
R_LL = NC.HUBLOT["d"]
X_LL_90 = NC.X_LL_FACE - R_LL                   # 129 : à 90°, la porte avance jusque-là, à y ≈ 57
JEU_LL_90 = NC.CHARNIERE_LL - Y_REB[1]          # 12,3 entre le panier sorti et la porte ouverte à 90°
assert JEU_LL_90 > 5, "à 90°, la porte de la machine laisse passer le panier"
assert NC.Y_LL_OUVERTE < Y_REB[1], "à fond, elle passe devant la baie : le panier ne sort plus"
_ang = math.radians(180 - NC.HUBLOT["angle"])
# à fond, la porte file de sa charnière vers le nord : au droit du coin sud du panier, elle est déjà devant lui
X_LL_FOND = NC.X_LL_FACE - (NC.CHARNIERE_LL - Y_REB[1]) * math.tan(_ang)   # ≈ 174, sans compter l'épaisseur de la porte
SORTIE_LL_FOND = X_AV - X_LL_FOND                                         # ≈ 3,7 : le panier ne sort presque plus
assert SORTIE_LL_FOND < 5, "machine ouverte à fond, on ne sort pas le panier"
assert X_LL_90 < NC.X_PORTE, "à 90°, la porte de la machine croise le vantail ouvert"
Z_LL_HAUT = NC.HUBLOT["z"] + R_LL / 2           # 73,5 : dessus de la porte
# Porte d'entrée : ouverte à 90°, le vantail est à 9 du nu du plan, donc à X_AV - X_PORTE de l'avant du panier rentré
SORTIE_PORTE = X_AV - NC.X_PORTE                # 12,5 : sortie permise, porte grande ouverte
assert X_AV_S < NC.X_PORTE, "à 38, le panier entre dans le débattement du vantail"
assert X_AV > NC.X_PORTE, "rentré, aucun conflit"
# Vantail venant de l'autre côté (quelqu'un entre) : il touche le coin avant nord du panier sorti
ANG_PORTE = math.degrees(math.atan2(Y_REB[0], NC.X_PORTE - X_AV_S))


# ------------------------------------------------------------------ débit : un lot de 6 × 200 et deux tasseaux rabotés de 240
TRAIT = 0.3


def _ffd(longueurs, barre):
    """Rangement dans des barres ; rend le contenu de chaque barre."""
    r = []
    for x in sorted(longueurs, reverse=True):
        for b in r:
            if sum(b) + x + TRAIT * len(b) <= barre:
                b.append(x)
                break
        else:
            r.append([x])
    return r


_sect38 = [b for b in OSSATURE if b.role == "bois" and b.nom not in ("rail_av", "rail_ar")]
_sect35 = SUPPORTS + [POTEAU] + list(M.RAILS)   # rails coupés dans le raboté de 35 : 3 mm plus bas que dessinés, sans effet
L38 = []
for _b in _sect38:
    if isinstance(_b, M.Profil):
        L38.append(M.ECHARPE["L"])
    else:
        L38.append(max(_b.x1 - _b.x0, _b.y1 - _b.y0, _b.z1 - _b.z0))
L35 = [max(b.x1 - b.x0, b.y1 - b.y0, b.z1 - b.z0) for b in _sect35]
B38, B35 = _ffd(L38, 200), _ffd(L35, 240)
assert len(B38) <= 6, B38
assert len(B35) <= 2, B35

# Le reste du pot de vernis du plan passe sur tous les tasseaux, deux couches (rendement du pot : 12 m²/L)
_achat = M.VERNIS["achat"][0][0]
RESTE_L = _achat["l"] - M.VERNIS["litres"]
SURF = (sum(L38) * 4 * M.DE + sum(L35) * 4 * T_H) / 1e4
VERNIS_TASSEAUX = SURF * 2 / M.VERNIS["rendement"]
assert VERNIS_TASSEAUX <= RESTE_L, (VERNIS_TASSEAUX, RESTE_L)


# ------------------------------------------------------------------ dessins
def _lbl(x, y, t, cls="lt", anchor="middle"):
    return PL.text(x, y, t, cls, anchor)


def face():
    o = [_lbl(YC, -(Z1_FOND + Z1_HAUT) / 2, "panier du bas"), _lbl(YC, -(Z2_FOND + Z2_HAUT) / 2, "panier du haut"),
         _lbl(YC, -(Z2_HAUT + M.Z_PLAN) / 2 + 1, "on jette ici sans tirer", "lt muted"),
         CO.chaine_h([M.Y0, YI0, YI1, _ec["av"].y1, M.Y1], 6, ext=0),
         CO.chaine_h([Y_REB[0], Y_REB[1]], 13),
         _lbl(YC, 17.5, f"rebord du panier ; {cm(LARGEUR)} entre les deux échelles", "lt muted"),
         CO.cote_v(-Z2_HAUT, -M.Z_PLAN, Y_REB[1] - 4, cm(G_HAUT), ext=Y_REB[1] - 8),
         CO.cote_v(-Z1_HAUT, -Z2_FOND, Y_REB[1] - 4, cm(G_BAS), ext=Y_REB[1] - 8),
         CO.niveaux([(Z1_FOND, f"{cm(Z1_FOND)} fond du bas", Y_REB[0]), (_z_tr(Z1_HAUT), f"{cm(_z_tr(Z1_HAUT))} traverse", YI0),
                     (Z2_FOND, f"{cm(Z2_FOND)} fond du haut", Y_REB[0]), (_z_tr(Z2_HAUT), f"{cm(_z_tr(Z2_HAUT))} traverse", YI0),
                     (M.Z_PLAN, f"{cm(M.Z_PLAN)} sous le plan", M.Y0)], M.Y0 - 6)]
    return NC.vue_face(scene(), o, "Vue de face, paniers rentrés")


def _sorti(blocs, s):
    return [PL.poly(CO.contour(b, "cote", s), "oswing") for b in blocs]


def coupe():
    s = YC
    bas = panier("bas", Z1_FOND, SORTIE)
    xr = X_MUR - SORTIE
    zr = Z1_HAUT + 0.2
    o = _sorti(bas, s)
    for b in SUPPORTS:                          # les traverses, derrière la paroi du panier
        if b.nom.startswith("traverse") and b.nom.endswith("n"):
            o.append(PL.rect(b.x0, -b.z1, b.x1, -b.z0, "ocache"))
    # la cordelette : du rebord arrière sorti à une vis dans le montant arrière
    o.append(f'<polyline class="oswing" points="{f(xr)},{f(-zr)} {f(XR - 3)},{f(-zr - 3)}"/>')
    o.append(_lbl((xr + XR - 3) / 2, -zr - 5.6, f"cordelette : arrêt à {cm(SORTIE)}"))
    o.append(CO.etiquette(XF + 7, -(Z2_HAUT + JEU_CT + T_H / 2), 163, -(Z2_HAUT + JEU_CT + T_H / 2) - 6, "contre-traverse", "end"))
    o.append(CO.etiquette(XF + 7, -(_z_tr(Z2_HAUT) - T_H / 2), 163, -(_z_tr(Z2_HAUT) - T_H / 2) + 6, "traverse (tiretée derrière le panier)", "end"))
    o.append(f'<line class="oswing" x1="{f(NC.X_PORTE)}" y1="{f(-M.Z_DESSUS - 2)}" x2="{f(NC.X_PORTE)}" y2="0"/>')
    o.append(_lbl(NC.X_PORTE + 0.8, -M.Z_DESSUS - 3, "vantail ouvert", "lt muted", "start"))
    o.append(_lbl(152, -(Z1_FOND + Z1_HAUT) / 2 - 1, "panier du bas", "lt muted"))
    o.append(_lbl(152, -(Z1_FOND + Z1_HAUT) / 2 + 2.4, "tiré", "lt muted"))
    o.append(_lbl((X_AV + X_MUR) / 2, -(Z2_FOND + Z2_HAUT) / 2, "panier du haut"))
    o.append(_lbl((X_AV + X_MUR) / 2 + 9, -(Z1_FOND + Z1_HAUT) / 2, "panier du bas rentré"))
    o.append(CO.chaine_h([X_AV_S, X_AV], 6, ext=0))
    o.append(_lbl((X_AV_S + X_AV) / 2, 12, "sortie arrêtée par la cordelette", "lt muted"))
    o.append(CO.chaine_h([XF, XR, X_MUR], 13))
    o.append(CO.cote_v(-Z2_HAUT, -M.Z_PLAN, X_AV + 17, cm(G_HAUT)))
    return NC.vue_coupe(scene(), s, o, sortie=48, titre="Coupe par les paniers")


def dessus():
    zs = 42.0                                   # entre le panier du bas et le fond de celui du haut
    assert Z1_HAUT + JEU_CT + T_H < zs < Z2_FOND
    o = [PL.rect(X_AV_S, Y_REB[0], X_AV_S + PANIER["L"], Y_REB[1], "oswing"),
         PL.rect(X_AV_S + PANIER["rebord"], Y_CORPS[0], X_AV_S + PANIER["L"] - PANIER["rebord"], Y_CORPS[1], "oswing")]
    o.append(PL.rect(X_LL_90, NC.CHARNIERE_LL - 1, NC.X_LL_FACE, NC.CHARNIERE_LL + 1, "ofac"))
    o.append(_lbl((X_LL_90 + NC.X_LL_FACE) / 2 - 8, NC.CHARNIERE_LL + 4.4, "porte de la machine à 90°"))
    o.append(_lbl((X_AV + X_MUR) / 2 + 8, YC + 1, "panier du bas, rentré"))
    o.append(_lbl((X_AV_S + M.FACE) / 2 - 3, YC - 1.6, "sorti", "lt muted"))
    o.append(_lbl((X_AV_S + M.FACE) / 2 - 3, YC + 1.8, f"de {cm(SORTIE)}", "lt muted"))
    o.append(CO.chaine_h([X_AV_S, NC.X_PORTE, M.FACE, X_AV, X_MUR], M.Y0 - 9, ext=M.Y0 - 4))
    o.append(CO.cote_v(NC.CHARNIERE_LL, Y_REB[1], NC.X_LL_FACE - 22, cm(JEU_LL_90), ext=NC.X_LL_FACE - 28))
    return NC.vue_dessus(scene(), zs, o, "Vue de dessus, coupée à 42 du sol, avec les deux portes")


def iso_ferme():
    bl = scene() + [POTEAU, PRISES] + HAUT
    return NC.iso(bl, NEUVES | {POTEAU.nom, PRISES.nom}, "Paniers rentrés")


def iso_sorti():
    bl = scene(SORTIE, 0) + [POTEAU, PRISES] + HAUT
    return NC.iso(bl, NEUVES | {POTEAU.nom, PRISES.nom}, "Panier du bas tiré")


# ------------------------------------------------------------------ fiche
RELEVE_REPO = "relevé en ligne du 13 au 26/10/2026"
_G = M.PANNEAUX["G"][0]
_D = M.PANNEAUX["D"][0]


def _w(code):
    return M.WELDOM[code]


LIGNES = [
    dict(libelle="Plan : tablette chêne lamellé-collé 200 × 60 × 18, recoupée à 114,4", qte=1, pu=_D["prix"],
         source=f"Weldom réf. {_D['ref']}, {RELEVE_REPO}", statut="relevé"),
    dict(libelle=f"{_achat['nom']} (le reste passe sur les tasseaux)", qte=1, pu=_achat["prix"],
         source=f"Weldom réf. {_achat['ref']}, {RELEVE_REPO}", statut="relevé"),
    dict(libelle="Lot de 6 tasseaux sapin brut 38 × 38 × 200 (ossature)", qte=1, pu=_G["prix_lot"],
         source=f"Weldom réf. {_G['ref']}, {RELEVE_REPO}", statut="relevé"),
    dict(libelle="Tasseau sapin raboté 35 × 35 × 240 (traverses, contre-traverses, rails, poteau)", qte=2, pu=6.10,
         source=f"Weldom réf. 9000481, {RELEVE_REPO}", statut="relevé"),
    dict(libelle=_w("verin")[0], qte=3, pu=_w("verin")[1], source=f"Weldom réf. {_w('verin')[4]}, {RELEVE_REPO}", statut="relevé"),
    dict(libelle=_w("insert")[0], qte=2, pu=_w("insert")[1], source=f"Weldom réf. {_w('insert')[4]}, {RELEVE_REPO}", statut="relevé"),
    dict(libelle=_w("vis60")[0], qte=1, pu=_w("vis60")[1], source=f"Weldom réf. {_w('vis60')[4]}, {RELEVE_REPO}", statut="relevé"),
    dict(libelle=_w("vis16")[0] + " (équerres)", qte=1, pu=_w("vis16")[1], source=f"Weldom réf. {_w('vis16')[4]}, {RELEVE_REPO}", statut="relevé"),
    dict(libelle=_w("equerre_a")[0] + " (plan, rails côté nord, poteau)", qte=2, pu=_w("equerre_a")[1],
         source=f"Weldom réf. {_w('equerre_a')[4]}, {RELEVE_REPO}", statut="relevé"),
    dict(libelle=_w("silicone")[0] + " (joint du plan au mur)", qte=1, pu=_w("silicone")[1],
         source=f"Weldom réf. {_w('silicone')[4]}, {RELEVE_REPO}", statut="relevé"),
    dict(libelle=PANIER["nom"], qte=2, pu=PANIER["prix"], source=f"IKEA France, réf. {PANIER['ref']}, relevé en ligne du {DATE}", statut="relevé"),
    dict(libelle="Bloc 3 prises 2P+T en saillie, blanc, 16 A", qte=1, pu=BLOC["prix"],
         source=f"Weldom réf. {BLOC['ref']}, prix vu dans un résultat de recherche du {DATE}, fiche non lue", statut="estimé"),
    dict(libelle="Moulure PVC blanche 20 × 10, 2 m", qte=1, pu=6.00, source="prix belge Gamma 4,29 à 7,39 €, prix français non lu", statut="estimé"),
    dict(libelle="Câble 3G2,5, 3 m (longueur selon le point d'arrivée)", qte=3, pu=1.50, source="ordre de grandeur, non relevé", statut="estimé"),
    dict(libelle="Sachet de 8 chevilles 8 × 50 (bloc et moulure sur carrelage)", qte=1, pu=4.19,
         source=f"Weldom réf. 5589927, {RELEVE_REPO}", statut="relevé"),
    dict(libelle="Cordelette Ø 3 et 2 mini-mousquetons", qte=1, pu=6.00, source="ordre de grandeur, non relevé", statut="estimé"),
]

_gestes_mettre = [
    f"panier du haut, petit linge : le jeter sans rien tirer, par le vide de {cm(G_HAUT)} sous le plan, sur {cm(YI1 - YI0 - 2 * T_H)} de large",
    f"panier du haut, le reste : tirer le rebord avant d'une main, le panier s'arrête seul à {cm(SORTIE)}, lâcher le linge, repousser jusqu'au mur",
    f"panier du bas : se baisser une fois pour tirer le rebord (il est à {cm(Z1_HAUT)} du sol), se relever, lâcher le linge d'en haut, repousser du pied ou de la main",
    "si la porte d'entrée est ouverte en grand, on ne peut tirer que de " + cm(SORTIE_PORTE) + " : la fermer d'abord",
]
_gestes_retirer = [
    "fermer la porte d'entrée et la porte de la machine",
    f"tirer le panier jusqu'à l'arrêt, passer la main dedans et décrocher le mousqueton au rebord arrière ({cm(X_MUR - SORTIE - M.FACE)} derrière le chant du plan, à portée de bras)",
    f"continuer à tirer à deux mains, doigts sous le rebord : à {cm(SORTIE_LIBRE)} le rebord arrière quitte la contre-traverse, à {cm(SORTIE_TOTALE)} il est sorti de sous le plan et on monte tout droit",
    "poser le panier au sol devant le hublot, côté sud de la porte de la machine",
    "ouvrir la porte de la machine, charger par brassées, refermer la porte de la machine (ou la laisser à 90° au plus)",
    "reposer le rebord arrière sur le bout des traverses, sous les contre-traverses, repousser, raccrocher le mousqueton, repousser jusqu'au mur",
    f"variante rapide, sans sortir le panier : porte de la machine à 90°, panier tiré de {cm(SORTIE)}, on passe les brassées par-dessus la porte, à {cm(Z_LL_HAUT)} du sol (estimé)",
]

FICHE = NC.verifier(dict(
    niveau=1, nom="Essentiel", resume=RESUME, lignes=LIGNES,
    heures=(12, 18),
    outils=["perceuse-visseuse, forets bois, foret carrelage", "scie circulaire et règle (refente, plan)", "scie à onglet ou égoïne",
            "pinceau, abrasif", "niveau, équerre, mètre"],
    paniers=dict(nombre=2, nom=PANIER["nom"], l=PANIER["L"], p=PANIER["l"], h=PANIER["h"], litres=PANIER["litres"],
                 prix=PANIER["prix"], url=PANIER["url"],
                 statut=f"relevé le {DATE} (prix, cotes hors tout, volume) ; rebord de 15 mm estimé"),
    traverses=dict(matiere="sapin raboté verni", section="27 × 35 (tasseau 35 × 35 refendu)",
                   longueur=round(XR - XF, 1), appui=f"rebord latéral du panier, {cm(APPUI * 10)} mm de chaque côté (estimé)"),
    gestes=dict(mettre=_gestes_mettre, retirer=_gestes_retirer),
    ouverture=dict(largeur=round(OUV_L, 1), profondeur=round(OUV_HAUT, 1),
                   note=f"panier tiré à {cm(SORTIE)} : bouche dégagée de {cm(OUV_L)} × {cm(OUV_HAUT)} pour le panier du haut (devant le plan), "
                        f"{cm(OUV_L)} × {cm(OUV_BAS)} pour celui du bas (devant le panier du haut) ; sans tirer, seulement le vide de "
                        f"{cm(G_HAUT)} au-dessus du panier du haut et de {cm(G_BAS)} au-dessus de celui du bas"),
    independants=True,
    prises=dict(nombre=3, modele=f"{BLOC['nom']}, Weldom réf. {BLOC['ref']}", pose="en saillie sur le carrelage, moulure PVC ; deux perçages dans le carreau ou le joint"),
    finition=["tasseaux de sapin vernis, nœuds apparents, vis visibles sur les faces intérieures",
              "plan en chêne verni marin, chant avant visible",
              "deux boîtes en plastique transparent : le linge se voit",
              "montants, écharpes et rail au sol visibles, meuble sans façade",
              "bloc de prises et moulure blancs posés sur le carrelage"],
    risques=[f"le rebord est estimé à 15 mm : s'il fait moins de 13 mm, il n'y a plus de largeur de traverse qui convienne, il faut un autre panier",
             "boîte fine en polypropylène : chargée, elle peut se déformer et perdre son appui ; essai à faire avec 6 kg avant de finir",
             "linge humide dans une boîte aux parois pleines : mauvaises odeurs ; percer quelques trous dans les flancs si besoin",
             f"poteau oublié ou retiré : {APPUI_MAX:.0f} kg appuyés sur le panier sorti soulèvent l'arrière du meuble",
             "cordelette qui se coince derrière le panier en le rentrant",
             "bloc de prises non vérifié sur sa fiche : il doit se raccorder à un câble fixe, pas à une fiche",
             "porte d'entrée qui cogne le panier sorti si quelqu'un entre",
             "vernis juste : si le sapin brut boit plus que prévu, un petit pot de 0,25 L en plus, à 20,90 €"],
))


# ------------------------------------------------------------------ chapitre
def section():
    figs = "".join([
        CO.figure("n1-face", "Vue de face", face(),
                  f"Sans façade. Au-dessus du panier du haut, {cm(G_HAUT)} libres sous le plan ; au-dessus du panier du bas, {cm(G_BAS)} seulement : "
                  "celui-là, il faut toujours le tirer."),
        CO.figure("n1-coupe", "Coupe par les paniers", coupe(),
                  f"En tireté, le panier du bas tiré jusqu'à l'arrêt. Il glisse par son rebord sur la traverse ; la contre-traverse, à l'avant, "
                  f"l'empêche de basculer. Le panier du haut peut sortir de la même façon."),
        CO.figure("n1-dessus", "Vue de dessus, coupée à 42 du sol, avec les deux portes", dessus(),
                  f"Panier du bas rentré, et tiré en tireté rouge. Le vantail de la porte d'entrée ouvert passe à {cm(NC.JEU_PORTE)} du nu du plan : le panier tiré à {cm(SORTIE)} entre dans son débattement. "
                  f"Porte de la machine à 90° : un mur à {cm(JEU_LL_90)} du panier sorti, qui ne le gêne pas mais le sépare du hublot. Ouverte à fond (arc en tireté, "
                  "cotes estimées), elle passe devant la baie."),
    ])
    i1, i2 = iso_ferme(), iso_sorti()
    return f"""<p>{RESUME}</p>
<div class="feuille">{figs}</div>
<div class="grid2">
<div class="fig">{i1}<p class="cap">Rentrés : rien ne dépasse du plan. Dans le coin de la niche, le poteau qui empêche le meuble de basculer, sous le fond du caisson haut (seul ce fond est dessiné) ; à droite, le bloc de prises, sur le mur du fond.</p></div>
<div class="fig">{i2}<p class="cap">Panier du bas tiré jusqu'à l'arrêt, celui du haut n'a pas bougé. En couleur : ce qui s'ajoute à l'ossature actuelle.</p></div>
</div>

<h3>Fonctionnement</h3>
<p><b>Les paniers.</b> Deux <a href="{PANIER["url"]}">boîtes IKEA SAMLA</a> de {cm(PANIER["L"])} × {cm(PANIER["l"])} × {cm(PANIER["h"])}, 45 L, {PL.euros(PANIER["prix"])} pièce (relevé du {DATE}). L'un sur l'autre, ils prennent {cm(2 * PANIER["h"])} cm sur les {cm(NC.HAUT_BAIE)} cm de haut. Il reste {cm(G_HAUT)} cm au-dessus de celui du haut et {cm(G_BAS)} cm au-dessus de celui du bas. Plein, chaque panier pèse environ {cm(M_PLEIN)} kg, soit {cm(M_LINGE)} kg de linge (0,12 kg/L, estimé).</p>
<p><b>Mettre le linge.</b> Dans le panier du haut, un tee-shirt se jette sans rien tirer. Pour le reste, on tire le panier d'une main : il s'arrête à {cm(SORTIE)} cm, et la bouche dégagée fait {cm(OUV_L)} × {cm(OUV_HAUT)} cm devant le plan. Celui du bas se tire de la même façon, en se baissant une fois : {cm(OUV_L)} × {cm(OUV_BAS)} cm dégagés, et on lâche le linge d'en haut. On peut remplir l'un sans toucher à l'autre.</p>
<p><b>Retirer le linge.</b> Porte d'entrée et porte de la machine fermées, on tire jusqu'à l'arrêt et on décroche la cordelette du rebord arrière, à portée de main dans le panier. On continue à deux mains, les doigts sous le rebord : à {cm(SORTIE_TOTALE)} cm le panier est sorti de sous le plan et monte tout droit. Rentré, il ne se soulève pas : {cm(G_BAS)} cm au-dessus de celui du bas et {cm(G_HAUT)} cm au-dessus de celui du haut, avec les contre-traverses devant. La fiche IKEA ne parle pas de poignée : on le porte par le rebord.</p>
<p><b>Vider dans la machine.</b> La porte de la machine s'ouvre du côté des paniers. À 90°, elle fait un mur entre le panier et le hublot. Ouverte à fond, elle passe devant la baie et le panier ne sort plus que de {cm(SORTIE_LL_FOND)} cm (cotes estimées). Le bon ordre : d'abord sortir le panier, le poser au sol devant le hublot, puis ouvrir la machine et charger par brassées. Après, on referme la porte de la machine avant de remettre le panier. Plus vite, sans poser le panier : machine à 90°, panier tiré, on passe les brassées par-dessus la porte, à {cm(Z_LL_HAUT)} cm du sol (estimé).</p>
<p><b>Porte d'entrée.</b> Rentré, le panier reste à {cm(X_AV - NC.X_PORTE)} cm du vantail ouvert : aucun conflit. Porte grande ouverte, on ne le tire que de {cm(SORTIE_PORTE)} cm. Tiré à {cm(SORTIE)} cm, il faut la porte fermée, et si quelqu'un entre, elle cogne le coin du panier après {ANG_PORTE:.0f}° d'ouverture : rien ne casse, mais il faut repousser le panier pour passer. La machine demande de toute façon la porte fermée : sa porte à 90° croise le vantail ouvert.</p>
<p><b>Ce qui porte.</b> Chaque panier repose par ses deux rebords longs sur deux traverses de {cm(XR - XF)} cm, en sapin raboté refendu à 27 × 35. Le rebord porte de {cm(APPUI * 10)} mm de chaque côté et le corps passe avec {cm(JEU_CORPS * 10)} mm de jeu (rebord estimé à 15 mm). La largeur de la traverse se décide panier en main, entre {cm(T_MIN * 10)} et {cm(T_MAX * 10)} mm. Les traverses sont vissées aux montants avant et arrière. L'ossature est celle du meuble actuel, moins l'écharpe et la lisse du milieu de l'échelle nord : le plan en tête et les rails en pied la lient à sa voisine. Le plan repose sur les trois échelles, une de chaque côté de la machine et une contre le mur nord ; il reste {cm(M.JEU_PLAN * 10)} mm au-dessus de la machine, qui ne porte rien.</p>
<p><b>Ce qui arrête.</b> En rentrant, le mur du fond : le panier a la même position à chaque fois, {cm(X_AV - M.FACE)} cm derrière le chant du plan. En sortant, une cordelette entre le rebord arrière et le montant arrière, à {cm(SORTIE)} cm. Et il faut retenir l'arrière : seul sur ses traverses, un panier plein et bien réparti bascule à {cm(S_LIBRE)} cm de sortie. Tiré de {cm(S_TEST)} cm seulement, {cm(M_TEST)} kg de linge jeté à l'avant suffisent, soit un jean (estimé). D'où un bout de tasseau de {cm(CT_L)} cm de chaque côté, à {cm(JEU_CT * 10)} mm au-dessus du rebord, à l'avant : la contre-traverse. Tiré à {cm(SORTIE)} cm et plein, le panier y pousse de {cm(F_CT)} kg au pire pour les deux, et il pique du nez de {cm(PIQUE)} cm.</p>
<p><b>Sans fixation au mur.</b> L'ossature, le plan et les vérins sont ceux d'aujourd'hui, avec les coins de calage contre les murs nord et sud. Le meuble pèse environ {cm(MASSE_FIXE)} kg sans la machine, et retient {M_STAB:.0f} kg·cm autour des vérins avant (densités estimées). Panier plein tiré à {cm(SORTIE)} cm, celui-ci pousse au pire de {M_PANIER:.0f} kg·cm : le meuble tient seul, avec une marge de {PL.cm(SECURITE)}. Mais {APPUI_MAX:.0f} kg appuyés sur le bord du panier sorti soulèvent l'arrière, coins et silicone mis à part. D'où un poteau de {cm(H_POTEAU)} cm, debout dans le coin de la niche, entre le plan et le caisson haut chevillé au mur : avec {APPUI_TEST} kg d'appui, il encaisse {POUSSEE:.0f} kgf. Sans caisson haut, il n'y a pas de poteau : il faudrait alors une équerre au mur.</p>
<p><b>Prises.</b> Un <a href="https://www.weldom.fr/produits-et-services/25-electricite/25252-rallonge-multiprise-enrouleur/2525201-bloc-multiprise/bloc-3-prises-avec-terre-saillie-blanc-5622364">bloc de 3 prises en saillie</a> sur le mur du fond, à {cm(BLOC["z0"])} cm du sol, au-dessus de la machine, à {cm(D_ROBINET)} cm du robinet d'arrêt. En saillie, on ne casse aucun carreau : deux perçages, une moulure blanche, et tout se démonte, mais le bloc et la moulure se voient. L'emplacement est hors volume : le volume 2 s'arrête à 60 cm du receveur de douche, et le meuble commence {cm(M.FACE - V2_X)} cm plus loin. Le bloc est à {cm(D_LAVABO)} cm du lavabo. Le circuit doit être protégé par un différentiel 30 mA. Il ne doit pas être repiqué sur la prise de la machine, qui a son circuit dédié. Aucune distance imposée n'a été trouvée pour un robinet d'arrêt : à faire confirmer par l'électricien, ainsi que le point d'arrivée du câble. Le bloc se raccorde-t-il bien à un câble fixe ? La fiche n'a pas pu être lue, à vérifier en magasin (autre choix : Leroy Merlin réf. 82016674, 13,90 €).</p>

<h3>Finition</h3>
<p>Ce qu'on voit : des tasseaux de sapin vernis, couleur miel, avec leurs nœuds et les têtes de vis sur les faces intérieures. Le chant du plan en chêne au-dessus. Au milieu, deux boîtes en plastique transparent à travers lesquelles le linge se voit. En bas, le rail de tasseau au sol. Tout est droit et solide, mais c'est un meuble d'atelier : pas de façade, pas de chant caché. Le reste du pot de vernis du plan suffit pour deux couches sur l'ossature ({f"{VERNIS_TASSEAUX:.2f}".replace(".", ",")} L pour {f"{RESTE_L:.2f}".replace(".", ",")} L restants, rendement estimé), ce qui évite un pot de peinture.</p>

<h3>Le prix</h3>
{NC.tableau_cout(FICHE)}
<p class="note">Sans plaque anti-vibrations sous la machine ni peinture, deux lignes du meuble actuel. Temps estimé : {FICHE["heures"][0]} à {FICHE["heures"][1]} h, hors séchage du vernis.</p>

<h3>Limites</h3>
<ul>
<li>Pas de glissière : le panier frotte, et la sortie à deux mains demande de porter {cm(M_PLEIN)} kg par le rebord.</li>
<li>Le rebord de 15 mm est une estimation, la fiche IKEA ne le donne pas. À mesurer en magasin avant de refendre, puis à essayer chargé de 6 kg : si la boîte se déforme et glisse entre les traverses, ce panier ne convient pas.</li>
<li>Rien ne cache le linge, et les parois pleines n'aèrent pas : quelques trous dans les flancs si le linge reste humide.</li>
<li>Le panier du bas est toujours à tirer, on se baisse pour l'atteindre.</li>
<li>La cordelette se décroche à chaque sortie complète. Sans elle, un panier tiré trop fort échappe à la contre-traverse à {cm(SORTIE_LIBRE)} cm.</li>
<li>Portes : à régler à chaque usage, entrée fermée pour tirer à fond, machine fermée pour sortir le panier. Le diamètre et l'angle de la porte de la machine sont estimés : à mesurer.</li>
</ul>
<p class="note">Règles électriques : guides <a href="https://www.legrand.fr/questions-frequentes/quelle-est-la-norme-nf-c-15-100-pour-la-salle-de-bain">Legrand</a> (volumes, prises, lave-linge hors volume), <a href="https://particuliers.engie.fr/economies-energie/conseils-equipements-chauffage/conseils-sante-securite/respect-normes-electriques-salle-de-bains">Engie</a> et <a href="https://www.totalenergies.fr/particuliers/parlons-energie/dossiers-energie/logement/l-installation-electrique-dans-la-salle-de-bain">TotalEnergies</a> (30 mA, prise à 60 cm du point d'eau), consultés le {DATE}, pas le texte de la norme. Relevé : prix et cotes hors tout du panier, prix Weldom. Estimé : rebord et fond du panier, densités, masse de linge, cotes de la porte de la machine et du bloc de prises.</p>"""


if __name__ == "__main__":
    print(f"cout {NC.cout(FICHE)}")
    print(f"hauteurs : fond bas {Z1_FOND}  rebord bas {Z1_HAUT}  fond haut {Z2_FOND}  rebord haut {Z2_HAUT}  libre {G_BAS:.1f}/{G_HAUT:.1f}")
    print(f"largeur : traverse {T_L}  appui {APPUI:.2f}  jeu corps {JEU_CORPS:.2f}  plage {T_MIN:.2f}-{T_MAX:.2f}")
    print(f"sortie {SORTIE}  bouches {OUV_L}x{OUV_HAUT} / {OUV_L}x{OUV_BAS}  libre {SORTIE_LIBRE}  totale {SORTIE_TOTALE}")
    print(f"sans retenue : plein {S_LIBRE:.1f}  à {S_TEST} : {M_TEST:.2f} kg  poussee contre-traverses {F_CT:.1f} kg (centré {F_CT_CENTRE:.1f})  pique {PIQUE:.1f} ({ANGLE:.1f}°)")
    print(f"meuble : {MASSE_FIXE:.1f} kg  stab {M_STAB:.0f}  panier {M_PANIER:.0f}  marge {SECURITE:.1f}  appui max {APPUI_MAX:.1f} kg  poteau {POUSSEE:.0f} kgf")
    print(f"portes : LL 90° jeu {JEU_LL_90:.1f}  LL fond sortie {SORTIE_LL_FOND:.1f}  x {X_LL_FOND:.1f}  entrée sortie {SORTIE_PORTE:.1f}  angle {ANG_PORTE:.0f}°")
    print(f"prises : robinet {D_ROBINET:.1f}  lavabo {D_LAVABO:.1f}  V2 {V2_X}")
    print(f"barres : {B38}\n  {B35}")
    print(f"vernis : surface {SURF:.2f}  besoin {VERNIS_TASSEAUX:.3f}  reste {RESTE_L:.3f}")
