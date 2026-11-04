# Niveau 2 « Soigné » du meuble bas : caisson en mélaminé blanc, deux paniers Curver Knit 40 L qui coulissent par leur rebord
# sur quatre traverses en mélaminé. Module du document niveaux.py ; socle commun dans niv_commun.py.
#
# Principe : chaque traverse est un petit rail fait de trois épaisseurs de mélaminé de 18 : une lame qui passe sous le rebord,
# une lame plus étroite au-dessus qui guide le panier sur le côté, et une retenue de 16 cm à l'avant, au-dessus du rebord,
# qui empêche le panier de piquer du nez. Une vis sous le rebord court dans une rainure de la traverse : c'est la butée.
#
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
Bloc, Profil, replace = M.Bloc, M.Profil, M.replace

ID = "niv2"
TITRE = "Niveau 2 · Soigné"
RESUME = ("Un caisson en mélaminé blanc et deux paniers Curver Knit de 40 L qui coulissent par leur rebord sur quatre "
          "traverses du même mélaminé : on tire un panier jusqu'à sa butée, il reste seul de niveau et l'autre ne bouge pas.")
DATE = "2026-11-04"
T = M.T                                         # épaisseur du mélaminé : 1,8

# ------------------------------------------------------------------ le panier
# Curver Knit 40 L, plastique recyclé ajouré, deux poignées sur le rebord (petits côtés). Cotes relevées le 2026-11-04 :
# 595 × 385 × 270 (revendeur aio.lv), 38 × 27 × 59 (Action France), 60 × 39 × 27 (La Poste, arrondi).
# Rebord (débord 1,25, épaisseur 1,5), fond (50 × 30) et masse (1 kg) : estimés, à mesurer sur un panier acheté.
PANIER = dict(nom="Curver Knit 40 L", L=59.5, l=38.5, h=27.0, litres=40, masse=1.0, levre=1.25, rebord=1.5,
              fond_L=50.0, fond_l=30.0, prix=19.08)
KG_L = 0.12                                     # linge sale, estimé
LINGE = PANIER["litres"] * KG_L
PLEIN = LINGE + PANIER["masse"]                 # 5,8 kg

# ------------------------------------------------------------------ le caisson
X_NEZ = M.FACE + 0.5                            # avant des joues et des traverses : 174,5 (le plan déborde de 0,5)
X_AR = NC.BAIE["x1"]                            # arrière : 233,7
Y_JN = (NC.BAIE["y0"], NC.BAIE["y0"] + T)       # joue nord
Y_JC = (NC.BAIE["y1"] - T, NC.BAIE["y1"])       # joue du milieu, à côté de la machine
Y_JS = (NC.MACHINE.y1 + 0.6, NC.MACHINE.y1 + 0.6 + T)   # joue sud, de l'autre côté de la machine
YI0, YI1 = Y_JN[1], Y_JC[0]                     # entre les joues : 2,1 → 48,4
YC = (YI0 + YI1) / 2
Z_VERIN = M.Z0                                  # 2 cm d'air sous le meuble
Z_FOND = Z_VERIN + T                            # dessus du fond : 3,8
Z_J1 = M.Z_PLAN

# ------------------------------------------------------------------ les rails, le panier en plan
JEU_GUIDE = 0.3
Y_R0, Y_R1 = YC - PANIER["l"] / 2, YC + PANIER["l"] / 2           # rebord du panier : 6,0 → 44,5
GUIDE = Y_R0 - JEU_GUIDE - YI0                  # largeur de la lame de guidage : 3,6, soit deux épaisseurs de mélaminé
RECOUVRE = 0.9                                  # la lame basse passe sous le rebord de tant
SOLE = GUIDE + JEU_GUIDE + RECOUVRE             # largeur de la lame basse : 4,8
Y_C0, Y_C1 = Y_R0 + PANIER["levre"], Y_R1 - PANIER["levre"]       # corps du panier sous le rebord : 36 de large
assert abs(GUIDE - 3.6) < 0.01 and abs(SOLE - 4.8) < 0.01
assert YI0 + SOLE < Y_C0 - 0.2, "la lame basse ne touche pas le corps du panier"
assert 0.5 <= RECOUVRE < PANIER["levre"], "le rebord porte sur la lame sans buter sur le corps"

# en profondeur : rentré, le rebord dépasse à peine du nu du plan et garde 0,8 devant le carrelage
X_PA = M.X1 - 0.8                               # arrière du rebord : 233,2
X_PF = X_PA - PANIER["L"]                       # avant du rebord : 173,7
assert X_PA <= NC.BAIE["x1"] and M.FACE - X_PF <= 0.5, "le panier tient dans les 60 du plan"
X_RET = (176.0, 192.0)                          # retenue au-dessus du rebord
X_G = M.X1 - X_PA                               # jeu derrière le panier
CG = (X_PF + X_PA) / 2                          # centre de gravité du panier plein, linge bien réparti : 203,45

# ------------------------------------------------------------------ les hauteurs
JEU_FOND = 0.5
Z_F1 = Z_FOND + JEU_FOND                        # fond du panier du bas : 4,3
Z_R1 = Z_F1 + PANIER["h"]                       # haut de son rebord : 31,3
PLACE = (M.Z_PLAN - Z_R1 - PANIER["h"]) / 2     # place libre au-dessus de chaque panier : 13,6
Z_F2 = Z_R1 + PLACE                             # fond du panier du haut : 44,9
Z_R2 = Z_F2 + PANIER["h"]                       # haut de son rebord : 71,9
assert PLACE >= 10 and abs(M.Z_PLAN - Z_R2 - PLACE) < 1e-6
NIV = [(Z_F1, Z_R1), (Z_F2, Z_R2)]              # (fond, haut du rebord) du bas et du haut


def _rails(k, z_r):
    """Traverse et retenue d'un niveau : k (1 bas, 2 haut), z_r = haut du rebord."""
    z_a = z_r - PANIER["rebord"]                # dessous du rebord, dessus de la lame basse
    r = []
    for c, (a, b, c0, c1) in (("n", (YI0, YI0 + SOLE, YI0, YI0 + GUIDE)), ("s", (YI1 - SOLE, YI1, YI1 - GUIDE, YI1))):
        r += [Bloc("facade", f"traverse_{k}{c}", X_NEZ, X_AR, a, b, z_a - T, z_a, groupe="caisson"),
              Bloc("facade", f"guide_{k}{c}", X_NEZ, X_AR, c0, c1, z_a, z_a + T, groupe="caisson"),
              Bloc("facade", f"retenue_{k}{c}", X_RET[0], X_RET[1], a, b, z_a + T, z_a + 2 * T, groupe="caisson")]
    return r


JEU_RET = T - PANIER["rebord"]                  # entre le haut du rebord et le dessous de la retenue : 0,3
assert abs(JEU_RET - 0.3) < 1e-6

JOUES = [Bloc("facade", "joue_n", X_NEZ, X_AR, Y_JN[0], Y_JN[1], Z_FOND, Z_J1, groupe="caisson"),
         Bloc("facade", "joue_c", X_NEZ, X_AR, Y_JC[0], Y_JC[1], Z_FOND, Z_J1, groupe="caisson"),
         Bloc("facade", "joue_s", X_NEZ, X_AR, Y_JS[0], Y_JS[1], Z_FOND, Z_J1, groupe="caisson")]
FOND = Bloc("facade", "fond", X_NEZ, X_AR, Y_JN[0], Y_JC[1], Z_VERIN, Z_FOND, groupe="caisson")
SEMELLE_S = Bloc("facade", "semelle_s", X_NEZ, X_AR, Y_JS[0], Y_JS[0] + 2.8, Z_VERIN, Z_FOND, groupe="caisson")
# raidisseurs : en haut au fond de la baie, au-dessus du panier du haut ; au pied derrière la machine, sous les tuyaux
RAID_H = Bloc("facade", "raidisseur_haut", X_AR - T, X_AR, YI0, YI1, 78.0, Z_J1, groupe="caisson")
RAID_B = Bloc("facade", "raidisseur_bas", M.MACHINE.x1 + 0.5, M.MACHINE.x1 + 0.5 + T, Y_JC[1], Y_JS[0], Z_VERIN, 9.5,
              groupe="caisson")
_s = M.PIED["semelle"]
_xv = (X_NEZ + 3.0, X_AR - 3.0)
VERINS = [Bloc("pied", f"verin_{i}", x - _s / 2, x + _s / 2, y - _s / 2, y + _s / 2, 0, Z_VERIN, groupe="caisson")
          for i, (x, y) in enumerate((x, y) for x in _xv for y in (Y_JN[0] + 1.5, Y_JC[1] - 1.5, SEMELLE_S.y0 + 1.4))]
RAILS = _rails(1, Z_R1) + _rails(2, Z_R2)
CAISSON = JOUES + [FOND, SEMELLE_S, RAID_H, RAID_B] + RAILS + VERINS

# le poteau de niche : une lame de mélaminé sur chant, debout entre le plan et le caisson haut
_chf = next(b for b in M.PIECES if b.nom == "ch_fond_n")
POTEAU = Bloc("facade", "poteau_niche", _chf.x0 - 7.0, _chf.x0, Y_JN[0], Y_JN[0] + T, M.Z_DESSUS, M.Z_HAUT, groupe="caisson")
PRISES = NC.prises(n=3, y0=84.0, z0=122.0, largeur_poste=7.3, hauteur=8.0, saillie=4.0)
assert (PRISES.z0 + PRISES.z1) / 2 <= 130, "axe sous 1,30 du sol (Legrand, IZI by EDF ; Engie dit l'inverse, source isolée)"


def panier(nom, z_f, z_r, sortie=0.0):
    """Un panier ouvert : deux bouts inclinés, deux flancs, un fond, un rebord en cadre."""
    p, e = PANIER, 0.3
    z_a = z_r - p["rebord"]
    x0, x1 = X_PF + p["levre"] - sortie, X_PA - p["levre"] - sortie
    rx = (x1 - x0 - p["fond_L"]) / 2
    g = dict(groupe=nom)
    return [Profil("bac", f"{nom}_avant", [(x0, z_a), (x0 + e, z_a), (x0 + rx + e, z_f), (x0 + rx, z_f)], Y_C0 + e, Y_C1 - e, **g),
            Profil("bac", f"{nom}_arriere", [(x1 - e, z_a), (x1, z_a), (x1 - rx, z_f), (x1 - rx - e, z_f)], Y_C0 + e, Y_C1 - e, **g),
            Profil("bac", f"{nom}_flanc_n", [(x0, z_a), (x1, z_a), (x1 - rx, z_f), (x0 + rx, z_f)], Y_C0, Y_C0 + e, **g),
            Profil("bac", f"{nom}_flanc_s", [(x0, z_a), (x1, z_a), (x1 - rx, z_f), (x0 + rx, z_f)], Y_C1 - e, Y_C1, **g),
            Bloc("bac", f"{nom}_fond", x0 + rx + e, x1 - rx - e, Y_C0 + e, Y_C1 - e, z_f, z_f + e, **g),
            Bloc("bac", f"{nom}_rebord_av", X_PF - sortie, x0 + e, Y_R0, Y_R1, z_a, z_r, **g),
            Bloc("bac", f"{nom}_rebord_ar", x1 - e, X_PA - sortie, Y_R0, Y_R1, z_a, z_r, **g),
            Bloc("bac", f"{nom}_rebord_n", x0 + e, x1 - e, Y_R0, Y_C0 + e, z_a, z_r, **g),
            Bloc("bac", f"{nom}_rebord_s", x0 + e, x1 - e, Y_C1 - e, Y_R1, z_a, z_r, **g)]


def etat(haut=0.0, bas=0.0, tout=True):
    """Le meuble, le panier du haut sorti de `haut`, celui du bas de `bas`."""
    r = NC.BASE + CAISSON + [POTEAU, PRISES] if tout else list(CAISSON)
    return r + panier("bas", *NIV[0], bas) + panier("haut", *NIV[1], haut)


NEUVES = {b.nom for b in RAILS}                 # dessinées en couleur dans les vues iso : les traverses

# ------------------------------------------------------------------ coulissement
# Rainure dans la lame basse, ouverte à l'avant, fermée à l'arrière : la vis sous le rebord y court. Une seconde vis plantée
# au fond de la rainure, tête 3 mm sous la surface, fait la butée : la vis du rebord bute dessus (0,4 de saillie dans la
# rainure de 0,6). En appuyant sur la poignée avant, l'arrière se lève, la vis passe.
X_VIS = X_PA - 1.5                              # vis sous le rebord, près de l'arrière
S_BUTEE = 26.0                                  # butée normale
S_LONG = X_PA - X_RET[1]                        # le rebord arrière arrive sous la retenue : 41,2 ; sortie longue, lâchée sans risque
S_SORT = X_PA - X_NEZ                           # le panier quitte les traverses : 58,7
assert CG - S_BUTEE > X_NEZ, "à la butée, panier bien réparti : il reste de niveau, sans toucher la retenue"
MARGE = CG - S_BUTEE - X_NEZ                    # 2,95
LEVIER_RET = X_RET[1] - X_NEZ                   # 17,5


def effort_retenue(s, cg=CG):
    """Effort (kgf) sur les deux retenues ; panier plein sorti de s, centre de gravité cg ; 0 s'il reste posé."""
    bras = X_NEZ - (cg - s)
    lev = min(X_RET[1], X_PA - s) - X_NEZ
    return max(0.0, PLEIN * bras / lev)


# rempli par l'avant, le linge peut rester sur les 60 % avant du panier : centre de gravité à 30 % de la longueur
CG_AVANT = X_PF + 0.3 * PANIER["L"]
BASCULE_SANS_RETENUE = CG_AVANT - X_NEZ         # sans retenue, un panier chargé devant piquerait dès 16,8 de sortie
assert BASCULE_SANS_RETENUE < S_BUTEE, "d'où la retenue"
RET_BUTEE = effort_retenue(S_BUTEE, CG_AVANT)   # ≈ 3 kgf
RET_LONG = effort_retenue(S_LONG)               # ≈ 4 kgf
LEVE_VIS = JEU_RET * (X_VIS - S_BUTEE - X_NEZ) / LEVIER_RET     # en appuyant : la vis monte de 0,53
assert LEVE_VIS > 0.4, "la vis du rebord passe la butée (0,3 à franchir)"
# bouche à l'air libre devant le nu du plan
BOUCHE_L = PANIER["l"] - 2 * PANIER["levre"]    # 36
BOUCHE_B = M.FACE - (X_PF + PANIER["levre"] - S_BUTEE)          # à la butée : 25
BOUCHE_LG = M.FACE - (X_PF + PANIER["levre"] - S_LONG)          # en sortie longue : 40
assert BOUCHE_B >= 24 and BOUCHE_LG >= 39

# ------------------------------------------------------------------ portes
S_PORTE = NC.JEU_PORTE - (M.FACE - X_PF)        # porte d'entrée ouverte à 90° : on ne tire que de 8,7
assert S_PORTE < S_BUTEE, "on tire le panier porte d'entrée fermée"
_h = (NC.X_LL_FACE, NC.CHARNIERE_LL)            # charnière de la porte de la machine


def angle_porte(sortie):
    """Ouverture (°) de la porte de la machine qui touche l'angle avant sud du rebord, panier sorti de `sortie`."""
    dx, dy = _h[0] - (X_PF - sortie), _h[1] - Y_R1
    return 90 + math.degrees(math.atan2(dy, dx))


A_BUTEE = angle_porte(S_BUTEE)                  # ≈ 114° : panier à la butée, la porte s'ouvre jusque-là
A_RENTRE = 180 - math.degrees(math.atan2(_h[0] - X_PF, _h[1] - Y_R1))   # rentré : ≈ 170°, au bord du rebord
D_MUR = NC.CHARNIERE_LL - Y_R1                  # à 90°, entre le panier sorti et la porte : 12,6

# ------------------------------------------------------------------ structure et basculement
assert Y_JC[1] <= NC.MACHINE.y0 - 0.5 and Y_JS[0] >= NC.MACHINE.y1 + 0.5, "la machine ne touche pas les joues"
assert NC.PLAN.z0 - NC.MACHINE.z1 == M.JEU_PLAN, "le plan ne pose pas sur la machine"
assert all(j.z1 == NC.PLAN.z0 for j in JOUES), "le plan pose sur les trois joues"
PORTEE = Y_JS[0] - Y_JC[1]                      # 60,7 au-dessus de la machine, comme au meuble actuel
assert RAID_H.z0 > Z_R2 and M.Z_PLAN - RAID_H.z1 == 0, "le raidisseur haut passe au-dessus du panier du haut"
_z = M.TUYAUX["zone"]
for _b in CAISSON:
    assert not (_b.x0 < _z[1] and _b.x1 > _z[0] and _b.y0 < _z[3] and _b.y1 > _z[2] and _b.z0 < _z[5] and _b.z1 > _z[4]), _b.nom
assert NC.ZONE_TECHNIQUE["x1"] - NC.ZONE_TECHNIQUE["x0"] >= 5
assert POTEAU.x1 <= M.X1 and POTEAU.y1 < PRISES.y0 and POTEAU.y1 < M.TRAPPE["y0"]


def _collisions(bl, e=1e-6):
    r = []
    for i, a in enumerate(bl):
        for b in bl[i + 1:]:
            if a.x0 < b.x1 - e and b.x0 < a.x1 - e and a.y0 < b.y1 - e and b.y0 < a.y1 - e and a.z0 < b.z1 - e and b.z0 < a.z1 - e:
                if a.groupe != b.groupe or a.groupe == "caisson":
                    r.append((a.nom, b.nom))
    return r


_ASSEMBLE = {"traverse", "guide", "retenue", "joue", "fond", "semelle", "raidisseur", "verin"}
for _s1, _s2 in ((0, 0), (S_BUTEE, 0), (0, S_BUTEE), (S_LONG, S_LONG), (S_SORT, S_SORT)):
    _c = _collisions(etat(_s1, _s2))
    _c = [c for c in _c if not (c[0].split("_")[0] in _ASSEMBLE and c[1].split("_")[0] in _ASSEMBLE)
          and "plan_travail" not in c and "lave_linge" not in c]
    assert not _c, (_s1, _s2, _c)
assert not [c for c in _collisions(etat()) if "lave_linge" in c], "rien ne touche la machine"

DENS = dict(mel=0.65, chene=0.70)               # kg/dm³, de mémoire (mêmes valeurs que var_comparatif.py)
_FIXE = [(b, DENS["mel"]) for b in JOUES + [FOND, SEMELLE_S, RAID_H, RAID_B] + RAILS] + [(NC.PLAN, DENS["chene"])]
PIVOT = _xv[0] - _s / 2                         # avant des vérins avant : 176,3
_vol = [((b.x1 - b.x0) * (b.y1 - b.y0) * (b.z1 - b.z0) * d / 1000, (b.x0 + b.x1) / 2) for b, d in _FIXE]
MASSE = sum(m for m, _ in _vol)                 # kg
M_STAB = sum(m * (x - PIVOT) for m, x in _vol)  # kg·cm
SORTIE_MAX = S_LONG


def m_tire(n=1, s=SORTIE_MAX):
    return n * PLEIN * (PIVOT - (CG - s))


MARGE_UN = M_STAB / m_tire(1)
MARGE_DEUX = M_STAB / m_tire(2)
assert MARGE_DEUX > 1, "les deux paniers pleins, tirés, ne font pas basculer le meuble à eux seuls"
_x_app = X_PF - S_BUTEE                         # appui sur le bord avant d'un panier à la butée
APPUI = (M_STAB - PLEIN * (PIVOT - (CG - S_BUTEE))) / (PIVOT - _x_app)   # kg


def poussee(appui):
    """Effort (kgf) dans le poteau de niche, `appui` kg sur le bord avant du panier à la butée."""
    return max(0.0, (appui * (PIVOT - _x_app) + PLEIN * (PIVOT - (CG - S_BUTEE)) - M_STAB) / ((POTEAU.x0 + POTEAU.x1) / 2 - PIVOT))


APPUI_TEST = 50                                 # kg : un adulte qui s'appuie sur le panier tiré
assert APPUI_TEST > APPUI, "le poteau sert à ce cas"
POUSSEE = poussee(APPUI_TEST)

# ------------------------------------------------------------------ prises : volumes de la salle de bain
_px = (PRISES.x0 + PRISES.x1) / 2
_py = (PRISES.y0 + PRISES.y1) / 2
D_DOUCHE = _px - M.DOUCHE[2]                    # ≈ 153 : le volume 2 s'arrête à 60 du receveur
D_LAVABO = math.hypot(_px - M.LAVABO[2], M.LAVABO[1] - _py)     # ≈ 71
assert D_DOUCHE > 60 and D_LAVABO >= 60, "hors volume, à plus de 60 d'un point d'eau"

# ------------------------------------------------------------------ débit et chant
_L = X_AR - X_NEZ                               # 59,2
_trait = 0.3
PANNEAU_A = 3 * (Z_J1 - Z_FOND + _trait)        # 3 joues dans 250
PANNEAU_B = (FOND.y1 - FOND.y0) + _L + (Y_JS[0] - Y_JC[1]) + (M.Z_HAUT - M.Z_DESSUS) + 4 * _trait
# la seconde tablette : fond, puis une rangée de 59,2 pour les lames, puis raidisseurs et poteau en long
assert PANNEAU_A <= 250 and PANNEAU_B <= 250
assert 4 * (SOLE + _trait) + 4 * (GUIDE + _trait) + 3.1 <= 60
CHANT = (2 * (FOND.y1 - FOND.y0 + _L) + 2 * (_L + 2.8)                  # fond, semelle sud : quatre côtés
         + 4 * (_L + SOLE) + 4 * (_L + GUIDE)                           # lames : bout avant, long côté vu
         + 4 * (X_RET[1] - X_RET[0] + SOLE))                            # retenues : long côté vu, bout avant
ROULEAUX = math.ceil(CHANT / (M.CHANT["rouleau"] / 10 - M.CHANT["marge"] / 10))
assert M.VERNIS["litres"] < 0.75

# ------------------------------------------------------------------ fiche
_W = M.WELDOM
_RV = "26/10/2026"
_ELEC = "123elec"


def _l(libelle, qte, pu, source, statut="relevé"):
    return dict(libelle=libelle, qte=qte, pu=pu, source=source, statut=statut)


LIGNES = [
    _l("Tablette mélaminé blanc 250 × 60 × 18 (joues, fond, traverses, poteau)", 2, 16.50, f"Weldom réf. 9134941, {_RV}"),
    _l("Tablette chêne lamellé-collé 200 × 60 × 18 (plan)", 1, 66.90, f"Weldom réf. 82025610, {_RV}"),
    _l("Vernis marin Syntilor satiné 0,75 L (plan, chants du bas)", 1, 37.50, f"Weldom réf. 5603010, {_RV}"),
    _l("Bande de chant thermocollante blanche, rouleau de 5 m", ROULEAUX, 9.50, f"Weldom réf. 5566191, {_RV}"),
    _l("Vis Standers 5 × 60, boîte de 200", 1, 11.50, f"Weldom réf. 87401795, {_RV}"),
    _l("Vis Standers 4 × 40, boîte de 150", 1, 9.00, f"Weldom réf. 5618719, {_RV}"),
    _l("Vis Standers 4 × 16, lot de 400", 1, 7.95, f"Weldom réf. 5618694, {_RV}"),
    _l("Équerres galvanisées 50 × 50 × 35, lot de 6", 1, 5.95, f"Weldom réf. 5605252, {_RV}"),
    _l("Vérins Hettich M8 × 30, lot de 2", 3, 4.19, f"Weldom réf. 5572729, {_RV}"),
    _l("Inserts pour pied M8 × 24, lot de 4", 2, 3.19, f"Weldom réf. 96652796, {_RV}"),
    _l("Silicone blanc biocide 310 ml (plan contre carrelage)", 1, 9.00, f"Weldom réf. 95216443, {_RV}"),
    _l("Panier Curver Knit 40 L", 2, PANIER["prix"], f"Amazon via prix.net, {DATE} ; 6,92 € chez Action France si en rayon"),
    _l("Legrand Dooxie : cadre saillie 2 postes", 1, 7.50, f"{_ELEC} réf. 600042, {DATE}"),
    _l("Legrand Dooxie : cadre saillie 1 poste", 1, 5.50, f"{_ELEC} réf. 600041, {DATE}", "estimé"),
    _l("Legrand Dooxie : prise 2P+T", 3, 3.50, f"{_ELEC} réf. 600337, {DATE}"),
    _l("Legrand Dooxie : plaques 1 et 2 postes", 1, 7.00, "à confirmer en rayon", "estimé"),
    _l("Moulure PVC 32 × 12, 2 m", 1, 8.00, "à confirmer en rayon", "estimé"),
    _l("Câble 3G2,5, 5 m", 1, 12.00, "à confirmer en rayon", "estimé"),
]

FICHE = NC.verifier(dict(
    niveau=2, nom="Soigné", resume=RESUME, lignes=LIGNES,
    heures=(14, 20),
    outils=["scie circulaire et règle", "défonceuse, fraise droite Ø 8", "perceuse-visseuse", "fer à repasser (chant)",
            "foret carrelage (prises)", "pinceau"],
    paniers=dict(nombre=2, nom="Curver Knit 40 L, plastique recyclé ajouré", l=PANIER["l"], p=PANIER["L"], h=PANIER["h"],
                 litres=PANIER["litres"], prix=PANIER["prix"],
                 url="https://www.action.com/fr-fr/p/3218161/panier-a-linge-curver-knit/",
                 statut=f"relevé le {DATE} (Action, aio.lv, La Poste) ; rebord, fond et masse estimés"),
    traverses=dict(matiere="mélaminé blanc 18, chants plaqués",
                   section=f"lame basse {cm(SOLE)} × {cm(T)} et lame de guidage {cm(GUIDE)} × {cm(T)} au-dessus",
                   longueur=round(_L, 1),
                   appui=f"le rebord du panier, sur {cm(RECOUVRE)} de chaque côté (rebord estimé)"),
    gestes=dict(
        mettre=[f"porte d'entrée fermée, tirer le panier voulu par sa poignée avant jusqu'à la butée ({cm(S_BUTEE)})",
                f"lâcher le linge dans la bouche à l'air libre ({cm(BOUCHE_L)} × {cm(BOUCHE_B)}), repousser ; l'autre panier ne bouge pas",
                f"une seule pièce : la jeter sans tirer, par la fente de {cm(PLACE)} au-dessus du panier",
                f"panier du bas : même geste, son rebord est à {cm(Z_R1)} du sol, il faut se baisser"],
        retirer=[f"appuyer sur la poignée avant pour passer la butée, tirer sur {cm(S_SORT)} en prenant le panier à deux mains",
                 f"panier du bas : il descend de {cm(Z_F1)} et se pose au sol ; on le pousse devant le hublot",
                 f"panier du haut : {cm(PLEIN)} kg à porter depuis {cm(Z_R2)} du sol, à poser au sol devant le hublot",
                 "ouvrir ensuite la porte de la machine à fond, charger par brassées, reposer le panier vide sur ses traverses"]),
    ouverture=dict(largeur=BOUCHE_L, profondeur=BOUCHE_B,
                   note=f"pour chaque panier : {cm(BOUCHE_L)} × {cm(BOUCHE_B)} à la butée, {cm(BOUCHE_L)} × {cm(BOUCHE_LG)} en sortie "
                        f"longue, à l'air libre devant le plan ; sans tirer, fente de {cm(BOUCHE_L)} × {cm(PLACE)}"),
    independants=True,
    prises=dict(nombre=3, modele="Legrand Dooxie 2P+T, cadres saillie 2 + 1 postes", pose="saillie de 4 sur le carrelage, axe à 1,26 du sol"),
    finition=["caisson et traverses en mélaminé blanc, chants blancs thermocollés", "plan en chêne verni satiné",
              "paniers à motif tricot, crème ou blanc cassé, poignée à l'avant", "aucune vis visible de face, aucun tasseau",
              "2 cm d'air sous le meuble, vérins discrets"],
    risques=[f"panier de {cm(PANIER['L'])} pour {cm(M.PROF)} de plan : s'il mesure 60 (La Poste), il dépasse de {cm(M.FACE - X_PF + 0.5)} du plan",
             f"rebord estimé ({cm(PANIER['levre'])} de débord, {cm(PANIER['rebord'])} d'épais) : la largeur des traverses et le jeu sous la retenue en dépendent ; "
             "un rebord creux peut ne pas tenir la vis de butée",
             f"retenue chargée de ≈ {RET_LONG:.0f} kgf en sortie longue : au-delà de {cm(S_LONG)}, le panier ne tient plus seul",
             f"un appui de ≈ {APPUI:.0f} kg sur le bord d'un panier tiré ferait partir le meuble sans le poteau de niche ; retiré pour nettoyer, le risque revient",
             f"porte de la machine ouverte à fond : elle arrive au bord du rebord du panier rentré (≈ {A_RENTRE:.0f}°, cotes estimées), à mesurer",
             "poignées du panier supposées sur les petits côtés, à vérifier en magasin",
             "caisson sans dos plein : sa raideur tient aux coins de calage, au plan et au raidisseur haut",
             "porte d'entrée ouverte sur un panier tiré : le vantail cogne le panier",
             "paniers visibles : pas de façade, le linge se devine par les jours du tricot",
             "mélaminé : un dégât des eaux au sol gonfle le fond malgré le vernis ; 2 cm d'air, pas plus"],
))


# ------------------------------------------------------------------ dessins
def _contours(blocs, vue, s, cls="oswing"):
    return [PL.poly(CO.contour(b, vue, s), cls) for b in blocs]


def face():
    o = [PL.text(YC, -(Z_F1 + Z_R1) / 2, "panier du bas", "lt"), PL.text(YC, -(Z_F2 + Z_R2) / 2, "panier du haut", "lt")]
    ym = YC + 12
    o.append(CO.cote_v(-Z_R1, -Z_F2, ym, cm(PLACE)))
    o.append(CO.cote_v(-Z_R2, -M.Z_PLAN, ym, cm(PLACE)))
    o.append(CO.chaine_h([M.Y0, YI0, Y_R0, Y_R1, YI1, Y_JC[1]], 6, ext=0))
    o.append(CO.niveaux([(Z_VERIN, f"{cm(Z_VERIN)} dessous du meuble", Y_JN[0]), (Z_F1, f"{cm(Z_F1)} fond du panier", Y_C0),
                         (Z_R1, f"{cm(Z_R1)} rebord du bas", Y_JN[0]), (Z_F2, f"{cm(Z_F2)} fond du panier", Y_C0),
                         (Z_R2, f"{cm(Z_R2)} rebord du haut", Y_JN[0]), (M.Z_PLAN, f"{cm(M.Z_PLAN)} dessous du plan", Y_JN[0])],
                        M.Y0 - 3))
    return NC.vue_face([b for b in etat() if b.nom != PRISES.nom and b.nom != POTEAU.nom], o, "Vue de face, paniers rentrés")


def coupe():
    s = YC
    o = _contours(panier("bas", *NIV[0], S_LONG), "cote", s)
    o.append(CO.chaine_h([X_PF - S_LONG, X_PF - S_BUTEE, M.FACE, X_PA], 6, ext=0))
    o.append(f'<line class="odiag" x1="{f(NC.X_PORTE)}" y1="{f(-M.Z_DESSUS - 3)}" x2="{f(NC.X_PORTE)}" y2="0"/>')
    o.append(PL.text(NC.X_PORTE - 1, -M.Z_DESSUS - 4, "vantail de la porte d'entrée, ouvert à 90°", "lt muted", "end"))
    o.append(PL.text(188, -(Z_F2 + Z_R2) / 2, "panier du haut, à la butée", "lt"))
    o.append(PL.text(205, -(Z_F1 + Z_R1) / 2, "panier du bas, rentré", "lt"))
    o.append(PL.text(150, -(Z_F1 + Z_R1) / 2, "sortie longue", "lt muted"))
    o.append(PL.text(X_PF - S_LONG + 7, 12.5, "sortie longue", "lt muted"))
    o.append(PL.text((X_PF - S_BUTEE + M.FACE) / 2, 12.5, "à la butée", "lt muted"))
    o.append(PL.text((M.FACE + X_PA) / 2, 12.5, "panier rentré", "lt muted"))
    o.append(CO.etiquette(sum(X_RET) / 2, -(Z_R2 - PANIER["rebord"] + 1.5 * T), 170, -Z_R2 - 7, "retenue au-dessus du rebord", "end"))
    o.append(CO.etiquette(X_NEZ, -(Z_R1 - PANIER["rebord"] - T / 2), 166, -Z_R1 - 7, "avant de la traverse", "end"))
    o.append(CO.niveaux([(Z_R1, f"{cm(Z_R1)} rebord du bas", X_PF - S_LONG), (Z_R2, f"{cm(Z_R2)} rebord du haut", X_PF - S_BUTEE),
                         (M.Z_PLAN, f"{cm(M.Z_PLAN)} dessous du plan", M.FACE)], X_PF - S_LONG - 3))
    return NC.vue_coupe([b for b in etat(haut=S_BUTEE) if b.nom not in (PRISES.nom, POTEAU.nom)], s, o, 60, "Coupe par les paniers, vue vers le nord")


def dessus():
    z = Z_R2 - PANIER["rebord"] / 2
    o = [PL.rect(NC.X_LL_FACE - NC.HUBLOT["d"], NC.CHARNIERE_LL - 0.5, NC.X_LL_FACE, NC.CHARNIERE_LL + 0.5, "ofac")]
    o.append(PL.text(NC.X_LL_FACE - NC.HUBLOT["d"] + 1, NC.CHARNIERE_LL + 3.4, "porte machine à 90°", "lt muted", "start"))
    o.append(PL.text(188, YC + 1, "panier du haut, à la butée", "lt"))
    o.append(CO.chaine_h([X_PF - S_BUTEE, M.FACE, X_PA], M.Y0 - 8, ext=M.Y0 - 4))
    o.append(CO.cote_h(NC.X_PORTE, M.FACE, M.Y0 + 82, cm(NC.JEU_PORTE), ext=M.Y0 + 73))
    o.append(CO.cote_v(Y_R1, NC.CHARNIERE_LL, X_PF - S_BUTEE - 2, cm(D_MUR)))
    return NC.vue_dessus([b for b in etat(haut=S_BUTEE) if b.nom != PRISES.nom], z, o, "Vue de dessus, coupée au rebord du panier du haut")


def _zoom(b, k):
    if isinstance(b, Profil):
        return replace(b, xz=[(x * k, z * k) for x, z in b.xz], y0=b.y0 * k, y1=b.y1 * k)
    return replace(b, x0=b.x0 * k, x1=b.x1 * k, y0=b.y0 * k, y1=b.y1 * k, z0=b.z0 * k, z1=b.z1 * k)


def detail():
    """Coupe agrandie de la traverse nord du niveau du bas : la lame, le guide, la retenue, le rebord."""
    k = 8
    bl = [b for b in etat(tout=False) if b.nom in ("joue_n", "traverse_1n", "guide_1n", "retenue_1n") or b.nom.startswith("bas_rebord")
          or b.nom == "bas_flanc_n"]
    # coupe vue de l'avant : le rebord est tenu dans le rail ; le bout avant du panier ne doit pas masquer le rail
    bl = [b for b in bl if b.nom not in ("bas_rebord_av", "bas_rebord_ar")]
    o = CO.projeter([_zoom(b, k) for b in bl], "face")
    za, zr = (Z_R1 - PANIER["rebord"]) * k, Z_R1 * k
    yb = -za + T * k + 8
    for a, b, t, dy in ((YI0, YI0 + GUIDE, cm(GUIDE), 0), (YI0 + GUIDE, Y_R0, cm(JEU_GUIDE), 4.4), (Y_R0, YI0 + SOLE, cm(RECOUVRE), 0)):
        o.append(CO.cote_h(a * k, b * k, yb, t, dy=dy, ext=-za + T * k))
    o.append(CO.cote_v(-za, -(za + T * k), (YI0 - 1.2) * k, cm(T), ext=YI0 * k))
    o.append(CO.cote_v(-zr, -za, (Y_C0 + 1) * k, cm(PANIER["rebord"]), ext=Y_C0 * k))
    o.append(PL.text((YI0 + SOLE / 2) * k, -(za - T * k / 2) + 0.8, "traverse", "lt"))
    o.append(PL.text((YI0 + GUIDE / 2) * k, -(za + T * k / 2) + 0.8, "guide", "lt"))
    o.append(PL.text((YI0 + SOLE / 2) * k, -(za + 1.5 * T * k) + 0.8, "retenue (16 cm, à l'avant)", "lt"))
    o.append(CO.etiquette((Y_R0 + 0.5) * k, -(za + zr) / 2, (Y_C0 + 3) * k, -(zr + 6), "rebord du panier", "start"))
    o.append(PL.text((Y_C0 + 1.3) * k, -za + 12, "flanc du panier", "lt muted", "start"))
    return CO.svg((YI0 - 3) * k, -(za + 2 * T * k) - 8, (Y_C0 + 5.5) * k, -za + T * k + 15, o, "Détail d'une traverse")


def section():
    p = PANIER
    figs = "".join([
        CO.figure("n2-face", "N2-1 · Vue de face", face(),
                  f"Les deux paniers rentrés, chacun avec {cm(PLACE)} de libre au-dessus. Les trois joues portent le plan ; la machine reste "
                  f"à {cm(M.JEU_PLAN)} dessous et à {cm(0.6)} de chaque joue."),
        CO.figure("n2-coupe", "N2-2 · Coupe par les paniers", coupe(),
                  f"Le panier du haut à sa butée, sorti de {cm(S_BUTEE)}, celui du bas rentré ; en tireté, le panier du bas en sortie longue "
                  f"({cm(S_LONG)}). Tout entre dans le débattement du vantail de la porte d'entrée, à {cm(NC.JEU_PORTE)} du plan."),
        CO.figure("n2-dessus", "N2-3 · Vue de dessus, les deux portes", dessus(),
                  f"Porte de la machine à 90° : un mur à {cm(D_MUR)} du panier sorti. Plus ouverte (arc tireté), elle bute sur ce panier à "
                  f"≈ {A_BUTEE:.0f}° ; paniers rentrés, elle passe devant eux. Cotes de porte estimées, à mesurer."),
        CO.figure("n2-detail", "N2-4 · Une traverse, en coupe (× 8)", detail(),
                  f"Le rebord glisse dans ce rail, avec {cm(JEU_GUIDE)} de jeu sur le côté et dessous la retenue. Rebord estimé : "
                  "rail à ajuster sur le panier acheté."),
    ])
    i1 = NC.iso(etat(), NEUVES, "Fermé")
    i2 = NC.iso(etat(haut=S_BUTEE), NEUVES, "Panier du haut à la butée")
    return f"""<p>Un caisson en mélaminé blanc sans tasseau visible ; deux paniers à motif tricot de {p["litres"]} L glissent par leur rebord sur quatre traverses du même mélaminé, comme des tiroirs sans façade, et se tirent chacun sans toucher à l'autre.</p>

<div class="feuille">{figs}</div>
<div class="grid2">
<div class="fig">{i1}<p class="cap">Fermé : le plan en chêne sur les trois joues, trois prises en saillie sur le mur du fond (mur non dessiné), le poteau de niche à gauche. Traverses en couleur pour les repérer ; en vrai, tout le caisson est blanc.</p></div>
<div class="fig">{i2}<p class="cap">Le panier du haut à sa butée : il tient seul, de niveau.</p></div>
</div>

<h3>Fonctionnement</h3>
<p>Cotes en cm.</p>
<p><b>Mettre le linge.</b> On ferme la porte d'entrée (ouverte, elle ne laisse que {cm(S_PORTE)} de sortie), on tire le panier voulu par sa poignée avant jusqu'à la butée, à {cm(S_BUTEE)}. La bouche à l'air libre devant le plan fait {cm(BOUCHE_L)} × {cm(BOUCHE_B)} : on lâche le linge, on repousse. L'autre panier ne bouge pas. Sans tirer, la fente de {cm(PLACE)} au-dessus du panier suffit pour une pièce jetée, pas pour une brassée. Pour le panier du bas, le rebord est à {cm(Z_R1)} du sol : il faut se baisser. Pour plus de place, on appuie sur la poignée, la butée se passe et le panier va jusqu'à {cm(S_LONG)} : bouche de {cm(BOUCHE_L)} × {cm(BOUCHE_LG)}, et il tient encore seul.</p>
<p><b>Retirer le linge.</b> Porte d'entrée fermée et porte de la machine fermée. On appuie sur la poignée, on tire sur {cm(S_SORT)} en reprenant le panier à deux mains : il sort à l'horizontale, il ne se soulève pas sur place, sa retenue et le plan l'en empêchent. Celui du bas descend de {cm(Z_F1)} et se pose au sol ; on le pousse devant le hublot. Celui du haut pèse ≈ {cm(PLEIN)} kg plein (estimé), à poser au sol. On ouvre alors la porte de la machine à fond (≈ {NC.HUBLOT["angle"]}°, elle passe devant les paniers rentrés) et on charge par brassées.</p>
<p><b>La porte de la machine.</b> Les gestes se font dans cet ordre. Panier à la butée, la porte s'arrête contre lui à ≈ {A_BUTEE:.0f}° ; à 90°, elle fait un mur à {cm(D_MUR)} du panier, entre lui et le hublot : on ne vide pas un panier par-dessus. Cotes de porte estimées.</p>
<p><b>Ce qui porte.</b> Le rebord pose sur {cm(RECOUVRE)} de chaque traverse (estimé). Chaque traverse est vissée en bout à travers la joue (3 vis 5 × 60) ; le plan repose sur les trois joues, {cm(PORTEE)} entre les deux joues qui encadrent la machine, comme au meuble actuel, sans poser sur elle. Sous le meuble, six vérins, 2 cm d'air.</p>
<p><b>Ce qui arrête.</b> Une vis sous chaque rebord court dans une rainure de {cm(0.6)} de la traverse : au fond, elle arrête le panier rentré, à {cm(X_G)} du carrelage ; à {cm(S_BUTEE)}, elle bute sur une seconde vis plantée dans la rainure. En appuyant sur la poignée, l'arrière se lève de {cm(LEVE_VIS)} et passe. Linge bien réparti, le centre de gravité reste {cm(MARGE)} derrière l'avant de la traverse : le panier ne touche même pas la retenue. Linge tassé devant (sans retenue, il piquerait dès {cm(BASCULE_SANS_RETENUE)} de sortie), la retenue reprend ≈ {RET_BUTEE:.0f} kgf et le panier s'incline de moins de 1 cm à l'avant. Au-delà de {cm(S_LONG)}, l'arrière passe sous la retenue : la main doit prendre le relais.</p>
<p><b>Basculement.</b> Meuble ≈ {MASSE:.0f} kg (masses de mémoire), sans fixation murale, sur vérins et coins de calage. Deux paniers pleins en sortie longue ne le font pas partir (marge {cm(round(M_STAB / m_tire(2), 1))} sur son poids), mais ≈ {APPUI:.0f} kg appuyés sur le bord d'un panier tiré, oui. D'où un poteau en chute de mélaminé ({cm(M.Z_HAUT - M.Z_DESSUS)}, sur chant, enfoncé au maillet) entre le plan et le caisson haut chevillé, dans le coin nord : un appui de {APPUI_TEST} kg y fait ≈ {POUSSEE:.0f} kgf, en compression. Rien n'est vissé au mur. Le chiffre suppose le caisson haut posé.</p>
<p><b>Prises.</b> Trois postes Legrand Dooxie 2P+T, série courante, sur deux cadres saillie (1 + 2 postes), sur le mur du fond, au-dessus de la machine, à {cm(M.Y1 - PRISES.y1)} du mur sud et {cm(PRISES.z0)} du sol. Le robinet d'arrêt est à {cm(PRISES.y0 - M.ROBINET["y"])} sur le côté et {cm(PRISES.z0 - M.ROBINET["z"])} dessous. En saillie, 4 de profondeur (cadre P40) et une moulure jusqu'au plan : quatre trous au foret carrelage, rien à entailler. L'encastré (kit Dooxie 3 postes, 48,58 € au tarif Legrand) demande de carotter le carreau et le mur : écarté à ce niveau. Hors volume : à ≈ {cm(D_DOUCHE)} du receveur (le volume 2 s'arrête à 60) et ≈ {cm(D_LAVABO)} du lavabo. Prises de courant et lave-linge y sont admis ; le circuit doit être protégé par un différentiel 30 mA (Legrand et Engie, relevés le {DATE}). Hauteur : Legrand et IZI by EDF donnent 1,30 du sol au maximum, Engie donne ce chiffre comme un minimum ; l'axe à 1,26 suit la majorité, à faire confirmer par l'électricien.</p>

<h3>Finition</h3>
<p>Blanc mat partout, chêne verni au-dessus. De face, on voit trois chants blancs d'usine ou plaqués, le bout des traverses en deux épaisseurs, les deux paniers à motif tricot, crème ou blanc cassé, poignée en avant. Pas de tasseau, pas de vis de face, pas de plinthe : 2 cm d'air sous le fond, vérins en retrait. Le mélaminé n'aime pas l'eau en chant : les chants du fond et de la semelle sud sont plaqués sur les quatre côtés, puis vernis (le pot de 0,75 L en garde ≈ {cm(0.75 - M.VERNIS["litres"])} L après le plan). Le plan contre le carrelage reçoit un joint de silicone. Les paniers ajourés laissent respirer le linge humide.</p>

<h3>Le prix</h3>
{NC.tableau_cout(FICHE)}
<p class="note">Prix Weldom : relevés en ligne le {_RV}, stock non lu. Paniers : 19,08 € retenus par prudence, 6,92 € chez Action France quand ils sont en rayon, 36,69 € sur La Poste. Prises Dooxie : 123elec, hors Weldom ; à reprendre en rayon si Weldom les a. Plaque anti-vibrations de la machine non comptée.</p>

<h3>Limites</h3>
<p>Pas de coulisses : on tire à la main, à frottement, avec une butée de vis et un appui pour la passer, pas d'amorti. Le panier reste à moitié dedans à la butée : la sortie longue et le retrait demandent la porte d'entrée fermée et de la place devant. Pas de façade : le linge se devine, le choix est de ne rien retirer à l'ouverture. Le plastique reste du plastique, même tricoté. Les cotes tiennent au millimètre sur un panier qu'il faut mesurer avant de débiter : rebord et longueur d'abord. Le caisson n'a pas de dos plein.</p>"""


if __name__ == "__main__":
    print(f"baie {cm(YI1 - YI0)} entre joues ; panier {PANIER['L']} × {PANIER['l']} × {PANIER['h']} ; rebord {X_PF} → {X_PA}")
    print(f"hauteurs : fond {Z_F1} / rebord {Z_R1} ; fond {Z_F2} / rebord {Z_R2} ; place {PLACE:.1f}")
    print(f"sorties : butée {S_BUTEE}, longue {S_LONG:.1f}, quitte {S_SORT:.1f} ; marge cg {MARGE:.2f} ; levée vis {LEVE_VIS:.2f}")
    print(f"bouche {BOUCHE_L:.1f} × {BOUCHE_B:.1f} / {BOUCHE_LG:.1f} ; retenue butée {RET_BUTEE:.1f} kgf, longue {RET_LONG:.1f} kgf")
    print(f"porte machine : butée {A_BUTEE:.0f}°, rentré {A_RENTRE:.0f}°, mur {D_MUR:.1f} ; porte d'entrée S {S_PORTE:.1f}")
    print(f"meuble {MASSE:.1f} kg, stab {M_STAB:.0f}, marge 1 {MARGE_UN:.1f} / 2 {MARGE_DEUX:.1f}, appui {APPUI:.0f} kg, poussée {POUSSEE:.0f} kgf")
    print(f"prises y {PRISES.y0}→{PRISES.y1} z {PRISES.z0} ; douche {D_DOUCHE:.0f}, lavabo {D_LAVABO:.0f}")
    print(f"chant {CHANT:.0f} cm, {ROULEAUX} rouleaux ; panneaux {PANNEAU_A:.0f} / {PANNEAU_B:.0f}")
    print(f"coût {NC.cout(FICHE)}")
