# Niveau 3 « Menuisé » du meuble bas : joues et traverses en chêne, plateaux coulissants, paniers en rotin doublés.
#
# Lecture de « deux traverses par panier » : deux traverses rainurées, une sur chaque joue, d'avant en arrière. Le bas d'un
# panier en rotin ne glisse pas et s'use sur le bois : il est posé sur un plateau de chêne, et c'est le plateau qui court dans
# les rainures des deux traverses. On soulève le panier, ou seulement sa doublure, sans toucher à l'autre niveau.
# Cotes en cm, repère de modele.py : x vers le mur du fond (234), y vers le sud, z depuis le sol.

import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import modele as M  # noqa: E402
import plan as PL  # noqa: E402
import cotes as CO  # noqa: E402
import niv_commun as NC  # noqa: E402

cm, f, Bloc, replace = PL.cm, PL.f, M.Bloc, M.replace

ID = "niv3"
TITRE = "Niveau 3 · Menuisé"
RELEVE = "04/11/2026"

# ------------------------------------------------------------------ panier : IKEA BRANÄS, rotin
# Fiche lue sur ikea.com/fr le RELEVE : 32 de large × 34 de profondeur × 32 de haut, réf. 001.384.32, 14,99 €, rotin verni,
# cadre en bois. Le côté de 34 se place en travers. Le cadre évite la déformation d'un panier souple.
PANIER = dict(nom="IKEA BRANÄS, rotin", ref="001.384.32", l=34.0, p=32.0, h=32.0, prix=14.99,
              url="https://www.ikea.com/fr/fr/p/branaes-panier-rotin-00138432/")
PANIER["litres"] = PANIER["l"] * PANIER["p"] * PANIER["h"] / 1000       # volume extérieur, le volume utile est plus petit
DENSITE_LINGE = 0.12                            # kg/L, estimé
MASSE_PANIER = 1.2                              # kg, panier et doublure, estimé
LINGE = PANIER["litres"] * DENSITE_LINGE
DENSITE_CHENE = 0.70                            # g/cm³, estimé

# ------------------------------------------------------------------ joues (tablettes de chêne de 18)
EP = M.PT                                       # 1,8
TAB = M.PANNEAUX["D"][0]
JX0, JX1 = NC.BAIE["x0"], NC.BAIE["x1"]         # 174 → 233,7
JZ0, JZ1 = M.Z0, NC.BAIE["z1"]                  # 2 (vérins) → 85,5, sous le plan
H_JOUE = JZ1 - JZ0                              # 83,5
Y_N = (NC.BAIE["y0"], NC.BAIE["y0"] + EP)       # 0,3 → 2,1
Y_C = (NC.BAIE["y1"] - EP, NC.BAIE["y1"])       # 48,4 → 50,2, à 6 mm de la machine
Y_S = (M.YM1 - EP, M.YM1)                       # 112,9 → 114,7, contre le mur sud
YI0, YI1 = Y_N[1], Y_C[0]                       # 2,1 et 48,4 : 46,3 entre les joues

# ------------------------------------------------------------------ traverses rainurées et plateaux
# Traverse : 1,8 d'épaisseur × 6,2 de haut, rainure de 2,2 de haut × 1,2 de profondeur, faite à la défonceuse.
# Plateau : fil du bois en travers (selon y). Il ne bouge pas dans sa largeur avec l'humidité, son fil porte entre les traverses
# et sa dilatation (selon x) reste libre. Seul le tourillon avant de chaque traverse est collé : la joue a son fil vertical et
# varie en x (oblongs côté joue), une traverse collée sur toute sa longueur la ferait fendre.
TR_H, GR_H, GR_P = 6.2, 2.2, 1.2
JEU_LAT = 0.3                                   # de chaque côté du plateau, au fond des rainures
TX0, TX1 = JX0 + 0.3, JX1 - 2.1                 # traverses en retrait de 3 mm sur le chant des joues, arrêtées devant la lisse
YT0, YT1 = YI0 + EP, YI1 - EP                   # faces intérieures des traverses : 3,9 et 46,6
P_Y0, P_Y1 = YT0 - GR_P + JEU_LAT, YT1 + GR_P - JEU_LAT
L_PLATEAU, P_X0 = 56.0, TX0
P_X1 = P_X0 + L_PLATEAU                         # 230,3
Z_PT = {0: 4.2, 1: 39.0}                        # dessous de chaque plateau
JEU_GR = (GR_H - EP) / 2                        # 2 mm dessus et dessous : bande de PTFE (≈ 1 mm, estimé) et vernis compris


def z_traverse(n):
    """Bas de la traverse du niveau n : la rainure est centrée sur l'épaisseur du plateau."""
    return Z_PT[n] - JEU_GR - (TR_H - GR_H) / 2


# ------------------------------------------------------------------ poignée, cale arrière, panier sur son plateau
H_POIGNEE = 8.0                                 # bandeau de chêne de 8 de haut, du dessous du plateau
PG_Y0, PG_Y1 = YT0 + JEU_LAT, YT1 - JEU_LAT     # entre les traverses
MAIN = 2.5                                      # place des doigts derrière la poignée
PA_X0 = P_X0 + EP + MAIN                        # 178,6
PA_X1 = PA_X0 + PANIER["p"]                     # 210,6
YC = (YI0 + YI1) / 2
PA_Y0, PA_Y1 = YC - PANIER["l"] / 2, YC + PANIER["l"] / 2
EP_PANIER = 1.0                                 # paroi dessinée
GARDE = 1.5                                     # panier soulevé : son arrière reste devant le nu du plan
COURSE = math.ceil(PA_X1 - M.FACE + GARDE)      # 39


RESUME = ("Meuble en chêne verni : deux paniers en rotin IKEA BRANÄS doublés, chacun posé sur un plateau de chêne qui "
          f"coulisse dans deux traverses rainurées et se tire de {COURSE} cm, jusqu'à dégager tout le panier.")


def ztop(n):
    return Z_PT[n] + EP


def pieces_fixes():
    r = []
    for k, (y0, y1) in (("n", Y_N), ("c", Y_C), ("s", Y_S)):
        r.append(Bloc("bois", f"joue_{k}", JX0, JX1, y0, y1, JZ0, JZ1))
        ys = (y0 + y1) / 2
        for x, c in ((M.XO0 + 0.2, "av"), (M.XO1 - 0.2, "ar")):
            r.append(Bloc("pied", f"verin_{k}_{c}", x - 1.2, x + 1.2, ys - 1.2, ys + 1.2, 0, JZ0))
    for n in Z_PT:
        z0 = z_traverse(n)
        r.append(Bloc("bois", f"traverse_n{n}", TX0, TX1, YI0, YT0, z0, z0 + TR_H))
        r.append(Bloc("bois", f"traverse_c{n}", TX0, TX1, YT1, YI1, z0, z0 + TR_H))
    r.append(Bloc("bois", "lisse_basse", JX1 - EP, JX1, YI0, YI1, 12.0, 20.0))
    r.append(Bloc("bois", "lisse_haute", JX1 - EP, JX1, YI0, YI1, 77.5, JZ1))
    return r


def mobiles(n, sortie=0.0, leve=0.0):
    """Plateau, poignée, cale et panier du niveau n, sortis de `sortie`, panier soulevé de `leve`."""
    zp, zt = Z_PT[n], ztop(n)
    d, e = -sortie, EP_PANIER
    x0, x1, y0, y1 = PA_X0 + d, PA_X1 + d, PA_Y0, PA_Y1
    z0, z1 = zt + leve, zt + PANIER["h"] + leve
    g = f"n{n}"
    return [
        Bloc("bois", f"plateau_{g}", P_X0 + EP + d, P_X1 + d, P_Y0, P_Y1, zp, zt, groupe=g),
        Bloc("bois", f"poignee_{g}", P_X0 + d, P_X0 + EP + d, PG_Y0, PG_Y1, zp, zp + H_POIGNEE, groupe=g),
        Bloc("bois", f"cale_{g}", PA_X1 + 0.2 + d, PA_X1 + 2.0 + d, YC - 10, YC + 10, zt, zt + 3, groupe=g),
        Bloc("bac", f"panier_fond_{g}", x0, x1, y0, y1, z0, z0 + e, groupe=g),
        Bloc("bac", f"panier_av_{g}", x0, x0 + e, y0, y1, z0, z1, groupe=g),
        Bloc("bac", f"panier_ar_{g}", x1 - e, x1, y0, y1, z0, z1, groupe=g),
        Bloc("bac", f"panier_n_{g}", x0 + e, x1 - e, y0, y0 + e, z0, z1, groupe=g),
        Bloc("bac", f"panier_s_{g}", x0 + e, x1 - e, y1 - e, y1, z0, z1, groupe=g),
    ]


def etat(sortie0=0.0, sortie1=0.0):
    return NC.BASE + pieces_fixes() + mobiles(0, sortie0) + mobiles(1, sortie1)


def _collisions(bl):
    e, r = 1e-6, []
    for i, a in enumerate(bl):
        for b in bl[i + 1:]:
            if (a.x0 < b.x1 - e and b.x0 < a.x1 - e and a.y0 < b.y1 - e and b.y0 < a.y1 - e and a.z0 < b.z1 - e
                    and b.z0 < a.z1 - e):
                r.append((a.nom, b.nom))
    return r


# ------------------------------------------------------------------ géométrie vérifiée
assert YI1 - YI0 > PANIER["l"] + 2, "le panier tient entre les joues, une main de chaque côté"
assert PG_Y1 - PG_Y0 > PANIER["l"], "le panier passe derrière la poignée"
assert YT0 - P_Y0 >= 0.8, "le plateau entre d'au moins 8 mm dans la rainure"
assert JZ1 == M.Z_PLAN and H_JOUE <= TAB["L"] / 10 - 114.4 - 0.3, "une joue se tire du reste de la tablette du plan"
assert P_X1 < JX1 - EP, "le plateau s'arrête devant la lisse arrière"
for _n in Z_PT:                                 # rainure, plateau
    _z = z_traverse(_n)
    assert _z + (TR_H - GR_H) / 2 <= Z_PT[_n] and ztop(_n) <= _z + (TR_H + GR_H) / 2, "le plateau est dans la rainure"
assert z_traverse(0) >= JZ0 - 1e-6, "la traverse basse reste au-dessus du bas de la joue"
# Rien ne se traverse : fermé, chaque niveau sorti, les deux sortis. Le plateau est dans la rainure : ce contact est voulu.
_socle = {b.nom for b in NC.BASE}               # le tuyau d'arrivée passe dans l'encoche du plan : déjà validé
for _s0, _s1 in ((0, 0), (COURSE, 0), (0, COURSE), (COURSE, COURSE)):
    _bl = etat(_s0, _s1)
    _gr = {b.nom: b.groupe for b in _bl}
    _c = [(u, v) for u, v in _collisions(_bl) if not (_gr[u] and _gr[u] == _gr[v]) and not {u, v} <= _socle
          and {u.split("_")[0], v.split("_")[0]} not in ({"traverse", "plateau"}, {"verin", "traverse"})]
    assert not _c, (_s0, _s1, _c)

# hauteurs
Z_HAUT_BAS = ztop(0) + PANIER["h"]              # 38
Z_HAUT_HAUT = ztop(1) + PANIER["h"]             # 72,8
JEU_ENTRE = Z_PT[1] - Z_HAUT_BAS                # 1,0 : rien ne passe, il faut tirer le panier du bas
FENTE = M.Z_PLAN - Z_HAUT_HAUT                  # 12,7 au-dessus du panier du haut
assert JEU_ENTRE > 0.5 and FENTE > 10 and Z_HAUT_HAUT < M.Z_PLAN

# sortie : le panier se soulève tout droit, et le plateau reste tenu par ses rainures
DEGAGE = M.FACE - (PA_X1 - COURSE)              # 2,4 entre l'arrière du panier et le nu du plan
PRISE = P_X1 - COURSE - TX0                     # 17 de plateau restent engagés dans les traverses
assert DEGAGE >= 1 and PRISE >= 15
PENTE = (GR_H - EP - 2 * 0.1) / PRISE * COURSE   # plateau sorti, sa poignée descend de tant (bandes de 1 mm, estimé)

# ------------------------------------------------------------------ bascule du plateau sorti
M_PLATEAU = (P_Y1 - P_Y0) * L_PLATEAU * EP * DENSITE_CHENE / 1000 + (PG_Y1 - PG_Y0) * H_POIGNEE * EP * DENSITE_CHENE / 1000
M_PANIER = MASSE_PANIER + LINGE
X_G_PANIER = (PA_X0 + PA_X1) / 2 - COURSE       # centre de gravité du panier plein, sorti
X_G_PLATEAU = (P_X0 + P_X1) / 2 - COURSE
_mt = M_PANIER * (TX0 - X_G_PANIER) + M_PLATEAU * (TX0 - X_G_PLATEAU)
EFFORT_LEVRE = _mt / PRISE                      # kgf repris par la lèvre haute des deux traverses, à l'arrière du plateau
assert X_G_PANIER < TX0, "sans lèvre haute, le plateau plein basculerait : les rainures sont nécessaires"
assert EFFORT_LEVRE < 15

# ------------------------------------------------------------------ bascule du meuble (estimations)
X_PIED = M.XO0 + 0.2                            # vérins avant : 176
_fixes = [b for b in pieces_fixes() if b.role == "bois"] + [NC.PLAN]


def _vol(b):
    return (b.x1 - b.x0) * (b.y1 - b.y0) * (b.z1 - b.z0)


MASSE_FIXE = sum(_vol(b) for b in _fixes) * DENSITE_CHENE / 1000
M_STAB = sum(_vol(b) * ((b.x0 + b.x1) / 2 - X_PIED) for b in _fixes) * DENSITE_CHENE / 1000
M_NIVEAU = M_PANIER * (X_PIED - X_G_PANIER) + M_PLATEAU * (X_PIED - X_G_PLATEAU)
M_RENV = 2 * M_NIVEAU                           # les deux plateaux sortis, paniers pleins
SECURITE = M_STAB / M_RENV
X_POIGNEE = P_X0 - COURSE
APPUI_MAX = (M_STAB - M_RENV) / (X_PIED - X_POIGNEE)
assert SECURITE > 1, "il ne bascule pas seul, paniers pleins et sortis"

# Poteau de niche : une quinzaine de kilos sur une poignée sortie suffisent (APPUI_MAX) ; on bloque donc l'arrière du plan sous le caisson haut.
_chn = next(b for b in M.PIECES if b.nom == "ch_cote_n")
_chf = next(b for b in M.PIECES if b.nom == "ch_fond_n")
POTEAU = Bloc("bois", "poteau_niche", _chf.x0 - 6.0, _chf.x0, _chn.y0, _chn.y1, M.Z_DESSUS, M.Z_HAUT)
H_POTEAU = POTEAU.z1 - POTEAU.z0
assert POTEAU.y1 < M.ROBINET["y"] - 30 and POTEAU.x0 >= M.CH["x0"], "dans le coin nord, sous le caisson haut"
APPUI_TEST = 30
POUSSEE = max(0.0, (APPUI_TEST * (X_PIED - X_POIGNEE) + M_RENV - M_STAB) / ((POTEAU.x0 + POTEAU.x1) / 2 - X_PIED))

# ------------------------------------------------------------------ plan : il porte des deux côtés, sans poser sur la machine
assert NC.MACHINE.z1 + M.JEU_PLAN == M.Z_PLAN and Y_C[1] < NC.MACHINE.y0 and Y_S[0] > NC.MACHINE.y1
PORTEE = Y_S[0] - Y_C[1]                        # 62,7 au-dessus de la machine
_E, _I = 11000.0, 600 * (EP * 10) ** 3 / 12     # N/mm² (estimé), mm⁴
FLECHE_50 = 500 * (PORTEE * 10) ** 3 / (48 * _E * _I)   # mm, 50 kg posés au milieu
assert FLECHE_50 < M.JEU_PLAN * 10, "50 kg au milieu du plan : il ne touche pas la machine"

# ------------------------------------------------------------------ portes
# Porte d'entrée
JEU_PORTE = NC.JEU_PORTE
assert P_X0 >= M.FACE and COURSE > JEU_PORTE, "fermé, rien ne dépasse ; sorti, le plateau entre dans le passage de la porte"
ANGLE_ENTREE = math.degrees(math.atan2(P_Y0, NC.X_PORTE - X_POIGNEE))   # plateau sorti : la porte d'entrée s'arrête là


# Porte de la machine, cotes estimées : charnière à (176, ≈ 57), dôme de 10 au milieu. Ouverte au-delà de 90°, le dôme revient
# vers le meuble. Elle bute sur la poignée du haut (z 39 → 47, le centre du dôme est à z 50), pas sur le rotin, plus en retrait.
def _x_dome(a):
    r = math.radians(a)
    return NC.X_LL_FACE - NC.HUBLOT["d"] / 2 * math.sin(r) - NC.HUBLOT["saillie"] * math.cos(r)


def _angle_butee(x_lim):
    a = 90.0
    while a < NC.HUBLOT["angle"] and _x_dome(a) < x_lim:
        a += 0.5
    return a


ANGLE_BUTEE = _angle_butee(P_X0)
Y_DOME_90 = NC.CHARNIERE_LL - NC.HUBLOT["saillie"]     # 47,1 : la porte à 90°, face au bord du plateau sorti
assert Z_PT[1] + H_POIGNEE >= NC.HUBLOT["z"] - 3 and PA_X0 > P_X0 + EP, "c'est la poignée qui reçoit le dôme, pas le rotin"
assert ANGLE_BUTEE < NC.HUBLOT["angle"]
assert NC.Y_LL_OUVERTE < YI1 < NC.CHARNIERE_LL, "ouverte à fond, la porte passe devant la baie"

# ------------------------------------------------------------------ prises
PL_PRISES = dict(l=24.3, h=8.3, saillie=0.9)    # plaque Legrand CP2403 : 243 × 83 × 9 mm (fiche Legrand, RELEVE)
PRISES = NC.prises(n=3, y0=84.0, z0=122.0, largeur_poste=PL_PRISES["l"] / 3, hauteur=PL_PRISES["h"], saillie=PL_PRISES["saillie"])
Z_AXE_PRISES = (PRISES.z0 + PRISES.z1) / 2
assert Z_AXE_PRISES <= 130, "axe du socle sous 1,30 m (doc Legrand citée par Selectra)"
assert PRISES.y0 - M.ROBINET["y"] >= 6 and PRISES.z0 > M.Z_DESSUS and PRISES.z1 < M.Z_HAUT

# ------------------------------------------------------------------ vernis et débit
_tout_bois = [b for b in pieces_fixes() + mobiles(0) + mobiles(1) if b.role == "bois"] + [NC.PLAN, POTEAU]
M2 = sum(M._surface(b) for b in _tout_bois)
LITRES = M2 * M.VERNIS["couches"] / M.VERNIS["rendement"]
_pots = sorted(((n * p["prix"], n, p) for p in M.VERNIS["pots"] for n in range(1, 4) if n * p["l"] >= LITRES), key=lambda t: t[0])
_, N_POTS, POT = _pots[0]
# Trois tablettes 200 × 60 : 1) plan + une joue ; 2) deux joues ; 3) deux plateaux, puis traverses, lisses, poignées, poteau.
_L, _W = TAB["L"] / 10, TAB["l"] / 10
assert 114.4 + H_JOUE + 0.6 <= _L and 2 * H_JOUE + 0.6 <= _L
_reste = _L - 2 * (P_Y1 - P_Y0) - 0.6           # reste en long de la 3ᵉ tablette
assert TX1 - TX0 + 48.1 + 0.6 <= _reste and L_PLATEAU <= _W
assert 2 * 8.3 + 2 * (TR_H + 0.3) + 6.3 + (H_POIGNEE + 0.3) <= _W and H_POTEAU <= _reste
N_TABLETTES = 3
METRES_TOILE = 1.3


def _l(libelle, qte, pu, source, statut="relevé"):
    return dict(libelle=libelle, qte=qte, pu=pu, source=source, statut=statut)


W = M.WELDOM
_w13 = "relevé d'octobre 2026, liste du meuble actuel"
LIGNES = [
    _l("Tablette chêne lamellé-collé FSC 200 × 60 × 18 (plan, joues, plateaux, traverses)", N_TABLETTES, TAB["prix"],
       f"Weldom réf. {TAB['ref']}, 26/10/2026"),
    _l(POT["nom"], N_POTS, POT["prix"], f"Weldom réf. {POT['ref']}, 26/10/2026"),
    _l(f"Panier {PANIER['nom']}, 32 × 34 × 32", 2, PANIER["prix"], f"IKEA France réf. {PANIER['ref']}, {RELEVE}"),
    _l("Toile de transat au mètre (2 doublures cousues, lavables)", METRES_TOILE, M.TOILE["prix_m"],
       f"Marseille Textiles, {M.TOILE['releve']}"),
    _l("Sangle coton et fil (anses des doublures)", 1, 6.00, "mercerie", "estimé"),
    _l("Lot de 2 patins glisseurs adhésifs PTFE 15 × 100 (12 bandes : 3 par bord de plateau)", 6, W["patins"][1],
       f"Weldom réf. {W['patins'][4]}, {_w13}"),
    _l("Lot de 2 vérins M8 × 30 (6 sous les 3 joues)", 3, W["verin"][1], f"Weldom réf. {W['verin'][4]}, {_w13}"),
    _l("Lot de 4 inserts M8 × 24", 2, W["insert"][1], f"Weldom réf. {W['insert'][4]}, {_w13}"),
    _l("Lot de 6 équerres 50 × 50 × 35 (plan sur joues, pied du poteau)", 2, W["equerre_a"][1],
       f"Weldom réf. {W['equerre_a'][4]}, {_w13}"),
    _l("Vis 4 × 40 (butées, joues), boîte de 150", 1, W["vis40"][1], f"Weldom réf. {W['vis40'][4]}, {_w13}"),
    _l("Vis 4 × 16 (équerres), lot de 400", 1, W["vis16"][1], f"Weldom réf. {W['vis16'][4]}, 26/10/2026"),
    _l("Mousses amortisseur adhésives (poignée, butée de porte)", 1, W["mousse"][1], f"Weldom réf. {W['mousse'][4]}, {_w13}"),
    _l("Silicone (joint du plan au mur)", 1, W["silicone"][1], f"Weldom réf. {W['silicone'][4]}, 26/10/2026"),
    _l("Tourillons chêne ou hêtre Ø 8, sachet", 1, 5.00, "Weldom, à vérifier", "estimé"),
    _l("Colle à bois D3, flacon", 1, 8.00, "Weldom, à vérifier", "estimé"),
    _l("Abrasifs 120 et 180", 1, 8.00, "Weldom, à vérifier", "estimé"),
    _l("Fraise droite Ø 12 pour les rainures, si absente", 1, 14.00, "Weldom ou Leroy Merlin, à vérifier", "estimé"),
    _l("Plaque Legrand Céliane chêne 3 postes CP2403", 1, 101.89, f"legrand.fr, prix conseillé, {RELEVE}"),
    _l("Prise 2P+T Céliane complète graphite (mécanisme et enjoliveur servent)", 3, 12.70,
       f"123elec, résultat de recherche, {RELEVE}"),
    _l("Support Batibox 3 postes et boîte d'encastrement", 1, 15.00, "Legrand, référence à fixer avec l'électricien", "estimé"),
]

FICHE = NC.verifier(dict(
    niveau=3, nom="Menuisé", resume=RESUME, lignes=LIGNES,
    heures=(32, 48),
    outils=["scie circulaire et rail", "défonceuse et fraise droite", "perceuse et gabarit de tourillonnage", "serre-joints",
            "ponceuse", "scie sauteuse", "machine à coudre"],
    paniers=dict(nombre=2, nom=PANIER["nom"], l=PANIER["l"], p=PANIER["p"], h=PANIER["h"], litres=round(PANIER["litres"], 1),
                 prix=PANIER["prix"], url=PANIER["url"], statut=f"relevé le {RELEVE}, volume calculé hors tout"),
    traverses=dict(matiere="chêne lamellé-collé verni, rainuré à la défonceuse", section=f"{cm(EP)} × {cm(TR_H)}",
                   longueur=round(TX1 - TX0, 1),
                   appui="le panier est posé sur un plateau de chêne ; le plateau court dans les rainures, sur bandes de PTFE"),
    gestes=dict(
        mettre=[f"panier du haut, plateau fermé : jeter le linge par la fente de {cm(FENTE)} cm sous le plan",
                "panier du haut plus confortable : tirer la poignée de 15 à 20 cm, jeter, repousser",
                f"panier du bas : tirer la poignée d'au moins 20 cm (il n'y a que {cm(JEU_ENTRE)} cm au-dessus), jeter, repousser",
                f"porte d'entrée ouverte à 90° : on ne peut tirer que de {cm(JEU_PORTE)} cm ; pour tirer plus, on la ferme d'abord"],
        retirer=[f"fermer la porte d'entrée, tirer le plateau à fond ({COURSE} cm), jusqu'à la butée",
                 "soulever la doublure par ses anses, ou le panier entier, tout droit ; l'autre niveau ne bouge pas",
                 "repousser le plateau, ouvrir la porte de la machine à fond, verser le linge dans le hublot",
                 "refermer la porte de la machine avant de ressortir un plateau : ouverte, elle est devant la baie"]),
    ouverture=dict(largeur=PANIER["l"] - 2 * EP_PANIER, profondeur=PANIER["p"] - 2 * EP_PANIER,
                   note=f"Plateau tiré à fond, chaque panier est libre au-dessus : {cm(PANIER['l'] - 2)} × {cm(PANIER['p'] - 2)}, "
                        f"sans rien sur sa tête. Plateau fermé, le panier du haut prend le linge par une fente de "
                        f"{cm(PANIER['l'] - 2)} × {cm(FENTE)} ; celui du bas, rien."),
    independants=True,
    prises=dict(nombre=3, modele="Legrand Céliane, plaque chêne 3 postes CP2403, mécanismes graphite",
                pose=f"encastrée dans le mur du fond, à {cm(Z_AXE_PRISES)} du sol ; carrelage à percer ; électricien"),
    finition=["chêne lamellé-collé verni satiné partout : plan, joues, traverses, plateaux, poignées",
              "chants de 18 visibles en façade, sans bande de chant",
              "rainures des traverses visibles en bout, tourillons Ø 8 apparents sur les traverses",
              "paniers en rotin blond, doublure de toile unie qui rabat sur le bord",
              "plaque de prises en chêne, assortie au plan"],
    risques=[f"basculement vers la pièce : sans le poteau de niche, ≈ {APPUI_MAX:.0f} kg sur une poignée sortie suffisent, "
             "coins de calage non comptés (estimé)",
             "le poteau de niche suppose le caisson haut chevillé : sans lui, il faut une fixation au mur carrelé",
             f"plateau sorti : la porte d'entrée, poussée de dehors, le heurte après ≈ {ANGLE_ENTREE:.0f}° d'ouverture et ne s'ouvre pas",
             f"porte de la machine ouverte à fond : dôme contre la poignée vers {ANGLE_BUTEE:.0f}° (cotes estimées, à mesurer)",
             "les bandes de PTFE adhésives peuvent se décoller avec l'humidité : à recoller ou à changer, 6,20 € le lot",
             "linge jeté à côté du panier : il reste sur le plateau, il faut le reprendre",
             "le rotin accroche : sans doublure, les mailles et les boutons s'y prennent",
             "hauteur de rainure à régler sur l'épaisseur réelle : tablette, vernis et bande de PTFE",
             "prises : si le mur est une cloison ou si la douche est à moins de 60 cm, la pose change ou devient interdite",
             "beaucoup d'heures de vernis : trois couches sur environ " + cm(M2) + " m², toutes faces"],
))
assert NC.cout(FICHE) <= 650, NC.cout(FICHE)


# ------------------------------------------------------------------ dessins
NEUVES = {b.nom for b in pieces_fixes() + mobiles(0) + mobiles(1) if b.role == "bois"}


def _noms(sortie0=0.0, sortie1=0.0):
    return NEUVES | {POTEAU.nom} | {b.nom for b in mobiles(0, sortie0) + mobiles(1, sortie1) if b.role == "bois"}


def face():
    o = [PL.text(YC, -(ztop(0) + Z_HAUT_BAS) / 2, "panier du bas", "lt"),
         PL.text(YC, -(ztop(1) + Z_HAUT_HAUT) / 2, "panier du haut", "lt"),
         PL.text(YC, -(Z_HAUT_HAUT + M.Z_PLAN) / 2 + 0.9, f"fente de {cm(FENTE)}", "lt"),
         CO.chaine_h([M.Y0, YI0, PA_Y0, PA_Y1, YI1, NC.MACHINE.y0, NC.MACHINE.y1, Y_S[0], M.Y1], 6, ext=0),
         CO.niveaux([(z_traverse(0), f"{cm(z_traverse(0))} traverse", YI0), (Z_HAUT_BAS, f"{cm(Z_HAUT_BAS)} panier", PA_Y0),
                     (z_traverse(1), f"{cm(z_traverse(1))} traverse", YI0), (Z_HAUT_HAUT, f"{cm(Z_HAUT_HAUT)} panier", PA_Y0),
                     (M.Z_PLAN, f"{cm(M.Z_PLAN)} plan", M.Y0)], M.Y0 - 7)]
    return NC.vue_face(etat(), o, "Vue de face, plateaux fermés")


def coupe():
    s = YC
    o = []
    for b in mobiles(1, COURSE):
        if b.y0 < s < b.y1:
            o.append(PL.poly(CO.contour(b, "cote", s), "oswing"))
    o += [CO.cote_h(P_X0 - COURSE, P_X0, -(M.Z_DESSUS + 3), f"{cm(COURSE)} de sortie", ext=-(ztop(1) + H_POIGNEE)),
          CO.chaine_h([P_X0, PA_X0, PA_X1, P_X1, M.X1], 6, ext=0),
          PL.text((PA_X0 + PA_X1) / 2, -(ztop(0) + 16), "panier du bas", "lt"),
          PL.text((PA_X0 + PA_X1) / 2, -(ztop(1) + 16), "panier du haut", "lt"),
          PL.text((PA_X0 + PA_X1) / 2 - COURSE, -(ztop(1) + 16), "sorti", "lt muted"),
          PL.text(PA_X1 + 3, -ztop(0) - 3.2, "plateau de chêne", "lt", "start"),
          CO.etiquette(TX1 - 6, -(z_traverse(1) + TR_H - 0.5), PA_X1 + 3, -(z_traverse(1) + TR_H + 6), "traverse rainurée", "start"),
          CO.cote_h(PA_X1 - COURSE, M.FACE, -(Z_HAUT_HAUT + 4), cm(DEGAGE), place="gauche", ext=-Z_HAUT_HAUT),
          CO.niveaux([(ztop(0), f"{cm(ztop(0))} dessus du plateau", P_X0), (Z_HAUT_BAS, f"{cm(Z_HAUT_BAS)} haut du panier", P_X0),
                      (ztop(1), f"{cm(ztop(1))} dessus du plateau", P_X0 - COURSE), (Z_HAUT_HAUT, f"{cm(Z_HAUT_HAUT)} haut du panier", P_X0 - COURSE),
                      (M.Z_PLAN, f"{cm(M.Z_PLAN)} dessous du plan", M.FACE)], M.FACE - 54)]
    return NC.vue_coupe(etat(), s, o, sortie=62, titre="Coupe par les paniers, panier du haut sorti")


def dessus():
    zs = 60.0
    o = []
    for b in mobiles(1, COURSE):
        if b.nom.startswith(("plateau", "poignee", "panier_av", "panier_ar", "panier_n", "panier_s")):
            o.append(PL.poly(CO.contour(b, "dessus", zs), "oswing"))
    h, a = NC.CHARNIERE_LL, NC.HUBLOT["d"]
    o += [f'<line class="oswing" x1="{f(NC.X_LL_FACE)}" y1="{f(h)}" x2="{f(NC.X_LL_FACE - a)}" y2="{f(h)}"/>',
          PL.text(NC.X_PORTE - 10, h + 3.2, "porte machine à 90°", "lt", "end"),
          PL.text(201, YC - 2, "panier du haut", "lt"),
          PL.text((PA_X0 + PA_X1) / 2 - COURSE, YC - 2, "sorti", "lt"),
          CO.cote_h(P_X0 - COURSE, P_X0, M.Y0 - 8, f"{cm(COURSE)} de sortie", ext=P_Y0),
          CO.cote_h(NC.X_PORTE, M.FACE, M.Y0 - 3, cm(JEU_PORTE)),
          CO.chaine_v([M.Y0, YI0, PA_Y0, PA_Y1, YI1], M.X1 + 8, ext=M.X1)]
    return NC.vue_dessus(etat(), zs, o, "Vue de dessus, coupée à 60 du sol")


def _base_iso():
    return [POTEAU, PRISES]


def section():
    n = NC.cout(FICHE)
    figs = "".join([
        CO.figure("niv3-face", "Vue de face, plateaux fermés", face(),
                  f"Trois joues de chêne portent le plan. Entre les deux de gauche, {cm(YI1 - YI0)} cm de large : les traverses, "
                  f"puis {cm((YT1 - YT0 - PANIER['l']) / 2)} cm de passage de chaque côté du panier. Derrière les paniers, on voit "
                  "les deux lisses arrière, en haut et en bas."),
        CO.figure("niv3-coupe", "Coupe par les paniers (vue vers le nord)", coupe(),
                  f"En tireté, le panier du haut sorti de {COURSE} cm. Son arrière passe {cm(DEGAGE)} cm devant le nu du plan : il "
                  f"monte tout droit. {cm(PRISE)} cm de plateau restent dans les rainures."),
        CO.figure("niv3-dessus", "Vue de dessus (coupée à 60 du sol)", dessus(),
                  f"Plateau sorti en tireté. La porte d'entrée ouverte passe à {cm(JEU_PORTE)} cm du nu ; la porte de la machine, "
                  f"à 90°, se dresse entre le panier sorti et le hublot ; ouverte à fond, elle est devant la baie."),
    ])
    i1 = NC.iso(etat() + _base_iso(), _noms(), "Fermé")
    i2 = NC.iso(etat(COURSE, 0) + _base_iso(), _noms(COURSE, 0), "Panier du bas sorti")
    return f"""<p>Trois joues de chêne portent le plan des deux côtés de la machine ; à gauche, chaque panier en rotin est posé sur un plateau de chêne qui coulisse dans deux traverses rainurées, une sur chaque joue.</p>

<div class="feuille">{figs}</div>
<div class="grid2">
<div class="fig">{i1}<p class="cap">Fermé : plan, joues et poignées affleurent. Au fond de la niche, le poteau bloque le plan sous le caisson haut (non dessiné).</p></div>
<div class="fig">{i2}<p class="cap">Panier du bas sorti à fond : le panier du haut ne bouge pas.</p></div>
</div>

<h3>Fonctionnement</h3>
<p><b>Mettre.</b> Panier du haut : on jette par la fente de {cm(FENTE)} cm sous le plan, sans rien ouvrir ; le panier fait {cm(PANIER["l"])} cm de large, ce qui tombe à côté reste sur le plateau. Panier du bas : il n'y a que {cm(JEU_ENTRE)} cm au-dessus de lui, il faut toujours tirer sa poignée, 20 cm suffisent. Tiré à fond, chaque panier s'offre entier, {cm(PANIER["l"] - 2)} × {cm(PANIER["p"] - 2)} cm d'ouverture, sans rien au-dessus. Chaque panier fait {PANIER["litres"]:.0f} L hors tout, soit ≈ {cm(LINGE)} kg de linge (0,12 kg/L, estimé).</p>
<p><b>Retirer.</b> On tire le plateau jusqu'à la butée, {COURSE} cm : l'arrière du panier passe alors {cm(DEGAGE)} cm devant le nu du plan. On soulève la doublure par ses anses, tout droit, ou le panier entier : l'autre niveau ne bouge pas. On repousse le plateau.</p>
<p><b>Vers la machine.</b> La charnière de la porte est du côté des paniers. À 90°, la porte fait un mur entre le panier sorti et le hublot, et son dôme arrive à {cm(Y_DOME_90)} cm du mur nord et mord de {cm((P_Y1 - Y_DOME_90) * 10)} mm sur le bord du plateau à {cm(P_Y1)} (estimé) : à 90°, la porte touche presque le plateau sorti. Ouverte à fond, elle est devant la baie et vient contre la poignée du haut vers {ANGLE_BUTEE:.0f}° (estimé, une mousse la reçoit). Donc on ne vide pas le panier en place : on sort la doublure pleine, on repousse le plateau, on ouvre la porte à fond et on verse depuis le devant de la machine. La doublure est un sac à deux anses : c'est elle qui rend le geste simple. Pour l'autre panier, on referme d'abord la porte.</p>
<p><b>Porte d'entrée.</b> Ouverte à 90°, son vantail passe à {cm(JEU_PORTE)} cm du nu : un plateau ne se tire alors que de {cm(JEU_PORTE)} cm. Pour le tirer à fond, on ferme la porte. Plateau sorti, la porte poussée de dehors le heurte après ≈ {ANGLE_ENTREE:.0f}° et ne s'ouvre pas.</p>
<p><b>Ce qui porte.</b> Le plan repose sur les trois joues : celle du nord, celle à {cm(Y_C[0])} cm et celle du mur sud. Il franchit {cm(PORTEE)} cm au-dessus de la machine, à {cm(M.JEU_PLAN * 10)} mm d'elle ; 50 kg posés au milieu le font descendre de ≈ {cm(FLECHE_50)} mm (estimé), il ne la touche pas. Deux lisses arrière lient les joues du linge. Chaque joue repose sur deux vérins, les coins de calage la serrent contre les murs, comme au meuble actuel.</p>
<p><b>Ce qui glisse.</b> Bois verni sur bande de PTFE adhésive : une sur le nez de chaque traverse, deux à l'arrière de chaque bord de plateau. Le PTFE ne craint pas l'eau et une bande se remplace facilement ; une cire demanderait d'y revenir (avis, durée non mesurée). Le fil du plateau court en travers : il ne gonfle pas dans sa largeur et ne se coince pas dans les rainures.</p>
<p><b>Ce qui arrête.</b> Une vis dans le haut de chaque traverse descend dans une rainure arrêtée du plateau : elle l'arrête à {COURSE} cm. Dévissée, le plateau sort pour le nettoyage. Sorti, le panier plein a son centre à {cm(TX0 - X_G_PANIER)} cm devant les traverses : posé à plat, il basculerait. La lèvre haute des rainures le retient, ≈ {EFFORT_LEVRE:.0f} kgf à l'arrière du plateau, et la poignée descend de ≈ {cm(PENTE * 10)} mm (estimé).</p>
<p><b>Basculement du meuble.</b> Le meuble n'est pas fixé au mur. Ses bois pèsent ≈ {cm(MASSE_FIXE)} kg (chêne à 0,70, estimé). Deux plateaux pleins sortis ne le font pas tomber (marge de {cm(SECURITE)}), mais ≈ {APPUI_MAX:.0f} kg appuyés sur une poignée sortie, oui, coins de calage non comptés. D'où un poteau de chêne de {cm(H_POTEAU)} cm debout dans le coin nord de la niche, entre le plan et le caisson haut chevillé : {APPUI_TEST} kg sur une poignée le chargent de ≈ {POUSSEE:.0f} kgf en compression. Il s'enfonce au maillet, et rien n'est vissé dans le carrelage.</p>
<p><b>Prises.</b> Trois postes Legrand Céliane sous une plaque en chêne, sur le mur du fond, de {cm(PRISES.y0)} à {cm(PRISES.y1)} cm du mur nord, axe à {cm(Z_AXE_PRISES)} cm du sol, {cm(PRISES.y0 - M.ROBINET["y"])} cm à droite du robinet d'arrêt, qui reste dégagé. Cette plaque se pose seulement en encastré : le cadre de saillie Céliane n'accepte pas les plaques en matière. Il faut donc percer le carrelage et passer le câble derrière. Sinon, cadre de saillie noir (CN0233, 58,63 €, prix conseillé) avec une plaque ordinaire, sans le chêne. Règles lues chez Legrand et Selectra : prise avec terre interdite dans les volumes 0, 1 et 2, permise hors volume, circuits de la pièce sous différentiel 30 mA, volume 2 jusqu'à 60 cm du bord de la baignoire ou de la douche. Le lavabo ne crée pas de volume. À faire confirmer par l'électricien.</p>

<h3>Finition</h3>
<p>Tout le bois visible est le même chêne lamellé-collé, verni marin satiné en trois couches sur toutes ses faces. En façade : trois chants de joue, le bout des traverses avec leur rainure, deux poignées de {cm(H_POIGNEE)} cm de haut percées d'une prise de main, et les paniers en rotin blond au-dessus d'elles. Plateau sorti, on voit les tourillons Ø 8 sur les traverses. Dans les paniers, une toile unie lavable rabattue sur le bord : elle évite que le rotin accroche le linge. La plaque de prises en chêne reprend le plan.</p>
<p class="note">Les paniers ne remplissent pas la baie : {cm(YI1 - YI0)} cm de large pour {cm(PANIER["l"])} cm de panier, et {cm(P_X1 - PA_X1)} cm de plateau vides derrière. Autre choix possible : panier à linge en jonc de mer 40 × 28 × 32 avec doublure bleue, 17,90 € (onrangetout.com, {RELEVE}), plus large mais souple.</p>

<h3>Le prix</h3>
{NC.tableau_cout(FICHE)}
<p class="note">Trois tablettes suffisent : plan et une joue ; deux joues ; plateaux, traverses, lisses, poignées et poteau. Vernis : {cm(M2)} m² × {M.VERNIS["couches"]} couches ≈ {cm(LITRES)} L, le pot de {cm(POT["l"])} L est le moins cher qui couvre. Relevé {RELEVE} : IKEA, Legrand. CP2403 vue à 91,86 € chez Domomat, page non lue. Marge restante sous 650 € : {PL.euros(650 - n)}.</p>

<h3>Limites</h3>
<ul>
<li>Le panier du bas ne se remplit jamais sans tirer sa poignée, et un plateau sorti ferme le passage de la porte d'entrée.</li>
<li>Le panier repose sur un plateau, non directement sur les traverses : c'est une pièce de plus par niveau, mais le rotin ne frotte sur rien.</li>
<li>Pas d'amortisseur ni de sortie sur billes : le plateau se pousse à la main, il s'arrête net sur sa vis.</li>
<li>{PANIER["litres"]:.0f} L par panier hors tout, soit ≈ {(PANIER["l"] - 2) * (PANIER["p"] - 2) * (PANIER["h"] - 1) / 1000 - 1.5:.0f} L utiles avec la doublure (estimé) ; il reste un vide derrière chaque panier : le plateau a besoin de cette longueur pour rester tenu quand il est sorti.</li>
<li>{FICHE["heures"][0]} à {FICHE["heures"][1]} h de travail (estimé), dont une bonne part de ponçage et de vernis ; les rainures doivent être justes.</li>
<li>Le poteau de la niche reste visible, et il faut le caisson haut en place.</li>
</ul>"""


if __name__ == "__main__":
    print(f"baie : {YI1 - YI0:.1f} entre joues, {YT1 - YT0:.1f} entre traverses, plateau y {P_Y0:.1f} → {P_Y1:.1f}, x {P_X0:.1f} → {P_X1:.1f}")
    print(f"hauteurs : traverses {z_traverse(0):.2f} et {z_traverse(1):.2f}, panier bas {ztop(0):.1f} → {Z_HAUT_BAS:.1f}, "
          f"haut {ztop(1):.1f} → {Z_HAUT_HAUT:.1f}, jeu entre {JEU_ENTRE:.1f}, fente {FENTE:.1f}")
    print(f"sortie {COURSE}, dégagé {DEGAGE:.1f}, engagé {PRISE:.1f}, effort lèvre {EFFORT_LEVRE:.1f} kgf, panier plein {M_PANIER:.1f} kg")
    print(f"meuble : masse {MASSE_FIXE:.1f} kg, stabilisant {M_STAB:.0f}, renversant {M_RENV:.0f}, marge {SECURITE:.2f}, "
          f"appui max {APPUI_MAX:.1f} kg, poteau {H_POTEAU:.1f}, poussée {POUSSEE:.1f} kgf")
    print(f"plan : portée {PORTEE:.1f}, flèche 50 kg {FLECHE_50:.2f} mm")
    print(f"portes : machine butée {ANGLE_BUTEE:.0f}°, dôme à 90° y {Y_DOME_90:.1f}, entrée {ANGLE_ENTREE:.1f}°")
    print(f"prises : y {PRISES.y0:.1f} → {PRISES.y1:.1f}, axe {Z_AXE_PRISES:.2f}")
    print(f"vernis : {M2:.2f} m² {LITRES:.2f} L → {N_POTS} × {POT['l']} L")
    print(f"coût : {NC.cout(FICHE):.2f} €")
