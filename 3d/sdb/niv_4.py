# Niveau 4 « Sur mesure » du meuble bas : deux tiroirs à façade pleine en chêne pleine lame, sur coulisses Blum cachées ; chaque
# tiroir n'a pas de fond : ses deux traverses hautes en chêne portent un panier Elfa posé, qui se soulève.
#
# Module du document des niveaux (niveaux.py). Cotes en cm, repère de modele.py : x vers le mur du fond (234), nu du plan à 174,
# y du nord (0) vers le sud (115), z depuis le sol. Relevés du 04/11/2026 sauf mention ; ce qui n'est pas lu est marqué estimé.

import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import niv_commun as NC  # noqa: E402
import modele as M  # noqa: E402
import plan as PL  # noqa: E402
import cotes as CO  # noqa: E402

cm, f, euros = NC.cm, NC.f, NC.euros
Bloc, replace = NC.Bloc, NC.replace

ID = "niv4"
TITRE = "Niveau 4 · Sur mesure"
RESUME = ("Deux façades pleines en chêne pleine lame, taillées dans la même planche que le plateau, sans poignée : une pression "
          "l'entrouvre, on le tire de 55 sur des coulisses Blum cachées, et le panier grillagé de 57 L, posé sur ses deux "
          "traverses, se soulève tout droit.")
RELEVE = "04/11/2026"

# ------------------------------------------------------------------ produits (source, date et statut dans les lignes du prix)
# Blum MOVENTO 760H5500S : sous tiroir, sortie totale, amorti, 40 kg la paire. Règles Blum relevées : largeur intérieure du
# tiroir = largeur du caisson − 42 mm ; longueur des côtés = longueur nominale − 10 mm ; côtés de 16 mm au plus ; retrait du
# fond ≥ 12 mm ; profondeur du caisson ≥ longueur nominale + 3 mm. Course et hauteur de la coulisse : non lues, estimées.
COUL = dict(NL=55.0, charge=40, course=55.0, h=1.4)            # course et h : estimées
SKW = 4.2                                                       # largeur du caisson − largeur intérieure du tiroir
# Elfa, panier filet 45 × 55 pour 3 glissières : hors tout 42,7 × 52,7 × 28,5 (relevé) ; poids conseillé par Elfa : 8 kg (relevé
# sur des paniers voisins de la même gamme). Corps sous le rebord, masse à vide : estimés, à mesurer.
PANIER = dict(l=42.7, p=52.7, h=28.5, corps_l=40.0, corps_p=51.0, rebord=0.5, masse=1.6, conseil=8.0, prix=55.0,
              url="https://www.maison-dressing-rangement.com/classic-by-elfa/22887-3636-panier-filet-largeur-45-cm-graphite-elfa-7315491451907.html")
LITRES = PANIER["corps_l"] * PANIER["corps_p"] * (PANIER["h"] - PANIER["rebord"]) / 1000       # ≈ 57 L, utiles
LINGE = 0.12 * LITRES                                           # kg : 0,12 kg/L, estimé
DENSITE = 0.70                                                  # chêne, estimé

# ------------------------------------------------------------------ plateau et caisson
EP_PLAN, EP_FACADE, EP = 2.0, 2.0, 1.8                          # pleine lame de 20 ; tablette Weldom de 18
PLAN = replace(NC.PLAN, z1=M.Z_PLAN + EP_PLAN)                  # dessus à 87,5
BASE = [PLAN, NC.MACHINE, NC.SIPHON, NC.ARRIVEE]
XF0, XF1 = M.FACE, M.FACE + EP_FACADE                           # façades au nu du plan : 174 → 176
XJ0, XJ1 = XF1 + 0.1, NC.BAIE["x1"]                             # joues : 176,1 → 233,7
Z_PLINTHE = 8.0
YJN = (NC.BAIE["y0"], NC.BAIE["y0"] + EP)                       # joue nord, contre le mur
YJC = (NC.BAIE["y1"] - EP, NC.BAIE["y1"])                       # joue centrale, à côté de la machine
YJS = (M.Y1 - 0.3 - EP, M.Y1 - 0.3)                             # joue sud, de l'autre côté de la machine
LW = YJC[0] - YJN[1]                                            # 46,3 entre les joues


def _b(role, nom, x0, x1, y0, y1, z0, z1, groupe=""):
    return Bloc(role, nom, x0, x1, y0, y1, z0, z1, groupe=groupe, miroir=False)


CAISSON = [_b("bois", "joue_n", XJ0, XJ1, *YJN, M.Z0, M.Z_PLAN),
           _b("bois", "joue_c", XJ0, XJ1, *YJC, M.Z0, M.Z_PLAN),
           _b("bois", "joue_s", XJ0, XJ1, *YJS, M.Z0, M.Z_PLAN),
           _b("bois", "traverse_mur", XJ1 - EP, XJ1, YJN[1], YJC[0], M.Z_PLAN - 8, M.Z_PLAN),     # vissée au mur du fond
           _b("bois", "traverse_basse", XJ1 - EP, XJ1, YJN[1], YJC[0], 12, 20),
           _b("plan", "plinthe", XF1 + 1, XF1 + 1 + EP_FACADE, YJN[1], YJC[0], 0.3, Z_PLINTHE)]
X_PIED = 178.0                                                  # axe des vérins avant, derrière la plinthe
Z_FIXE = M.Z_PLAN - 4                                           # hauteur des 2 vis dans le mur du fond

# ------------------------------------------------------------------ les deux tiroirs
JEU_F = 0.3
YF = (YJN[0] + JEU_F, YJC[1] - 0.2)                             # façades : 0,6 → 50,0
H_F = (M.Z_PLAN - JEU_F - (Z_PLINTHE + JEU_F) - JEU_F) / 2      # 38,3 chacune
ZF = dict(bas=(Z_PLINTHE + JEU_F, Z_PLINTHE + JEU_F + H_F), haut=(M.Z_PLAN - JEU_F - H_F, M.Z_PLAN - JEU_F))
ZT = dict(bas=41.3, haut=80.0)                                  # dessus des traverses, où pose le rebord du panier
L_COTE = COUL["NL"] - 1                                         # 54
YCI = (YJN[1] + (LW - (LW - SKW)) / 2, YJC[0] - SKW / 2)        # faces intérieures des traverses : 4,2 et 46,3
YC = (YCI[0] + YCI[1]) / 2
TRINGLE = 1.0                                                   # tringle de chêne collée dans le haut de chaque traverse
FOND = PANIER["h"] - PANIER["rebord"]                           # 28 de corps sous le rebord
H_T = FOND + 0.5 + EP + 1.2                                     # 31,5 : corps, jeu, semelle de 18, retrait de 12
X_R = (XF1, XF1 + PANIER["p"])                                  # rebord du panier, plaqué contre le dos de la façade


def tiroir(k):
    """Une façade, ses deux traverses avec leurs tringles, une semelle avant, une pièce arrière (rien entre les deux : pas de
    fond), et la partie mobile des coulisses."""
    zt, z0 = ZT[k], ZT[k] - H_T
    g = dict(groupe=k)
    y0, y1 = YCI
    return [_b("plan", f"facade_{k}", XF0, XF1, *YF, *ZF[k], **g),
            _b("bois", f"traverse_n_{k}", XF1, XF1 + L_COTE, y0 - EP, y0, z0, zt, **g),
            _b("bois", f"traverse_s_{k}", XF1, XF1 + L_COTE, y1, y1 + EP, z0, zt, **g),
            _b("bois", f"tringle_n_{k}", XF1, XF1 + L_COTE, y0, y0 + TRINGLE, zt - 3, zt, **g),
            _b("bois", f"tringle_s_{k}", XF1, XF1 + L_COTE, y1 - TRINGLE, y1, zt - 3, zt, **g),
            _b("bois", f"semelle_{k}", XF1, XF1 + 7.5, y0, y1, z0 + 1.2, z0 + 1.2 + EP, **g),
            _b("bois", f"arriere_{k}", XF1 + L_COTE - 3, XF1 + L_COTE, y0, y1, z0 + 1.2, z0 + 1.2 + EP, **g),
            _b("vis", f"coulisse_mob_n_{k}", XF1 + 0.1, XF1 + L_COTE, y0, y0 + 2.5, z0, z0 + 1.2, **g),
            _b("vis", f"coulisse_mob_s_{k}", XF1 + 0.1, XF1 + L_COTE, y1 - 2.5, y1, z0, z0 + 1.2, **g)]


def fixes(k):
    """Partie fixe des coulisses, vissée sur les joues sous les traverses."""
    z0 = ZT[k] - H_T
    x0, x1 = XJ0, XJ0 + COUL["NL"]
    return [_b("vis", f"coulisse_n_{k}", x0, x1, YJN[1], YCI[0], z0 - COUL["h"], z0),
            _b("vis", f"coulisse_s_{k}", x0, x1, YCI[1], YJC[0], z0 - COUL["h"], z0)]


def panier(k, parois=True):
    """Panier posé : rebord en cadre sur le haut des traverses, corps pendu entre les tringles. parois=False retire les flancs
    dans la coupe, pour qu'on y voie la traverse."""
    zt, zb = ZT[k], ZT[k] - FOND
    e = 0.3
    y0, y1 = YC - PANIER["corps_l"] / 2, YC + PANIER["corps_l"] / 2
    yr0, yr1 = YC - PANIER["l"] / 2, YC + PANIER["l"] / 2
    d = (PANIER["p"] - PANIER["corps_p"]) / 2
    x0, x1 = X_R[0] + d, X_R[1] - d
    g = dict(groupe=f"panier_{k}")
    r = [_b("bac", f"panier_{k}_avant", x0, x0 + e, y0, y1, zb, zt, **g),
         _b("bac", f"panier_{k}_arriere", x1 - e, x1, y0, y1, zb, zt, **g),
         _b("bac", f"panier_{k}_fond", x0, x1, y0, y1, zb, zb + e, **g),
         _b("bac", f"panier_{k}_rb_av", X_R[0], x0 + e, yr0, yr1, zt, zt + PANIER["rebord"], **g),
         _b("bac", f"panier_{k}_rb_ar", x1 - e, X_R[1], yr0, yr1, zt, zt + PANIER["rebord"], **g),
         _b("bac", f"panier_{k}_rb_n", x0 + e, x1 - e, yr0, y0 + e, zt, zt + PANIER["rebord"], **g),
         _b("bac", f"panier_{k}_rb_s", x0 + e, x1 - e, y1 - e, yr1, zt, zt + PANIER["rebord"], **g)]
    if parois:
        r += [_b("bac", f"panier_{k}_n", x0, x1, y0, y0 + e, zb, zt, **g),
              _b("bac", f"panier_{k}_s", x0, x1, y1 - e, y1, zb, zt, **g)]
    return r


def _dep(b, dx=0.0, dz=0.0):
    return replace(b, x0=b.x0 + dx, x1=b.x1 + dx, z0=b.z0 + dz, z1=b.z1 + dz)


def etat(sortie=None, leve=0.0, parois=True, prises=False):
    """Tout le meuble ; sortie : tiroir sorti à fond ("haut" ou "bas") ; leve : son panier soulevé de tant."""
    r = BASE + CAISSON + (([PRISES]) if prises else [])
    for k in ("bas", "haut"):
        dx = -COUL["course"] if k == sortie else 0.0
        r += fixes(k) + [_dep(b, dx) for b in tiroir(k)] + [_dep(b, dx, leve if k == sortie else 0.0) for b in panier(k, parois)]
    return r


PRISES = NC.prises(3)
NEUVES = {b.nom for b in etat(prises=True)} - {b.nom for b in BASE}
NEUVES -= {b.nom for k in ("bas", "haut") for b in panier(k)}    # les paniers restent de la teinte neutre, ils se détachent
NEUVES.add(PLAN.nom)

# ------------------------------------------------------------------ géométrie : ce qui doit tenir
for _j in CAISSON[:2]:
    assert NC.BAIE["y0"] <= _j.y0 and _j.y1 <= NC.BAIE["y1"] and _j.x1 <= NC.BAIE["x1"], _j.nom
assert NC.MACHINE.y0 - YJC[1] >= 0.5 and YJS[0] - NC.MACHINE.y1 >= 0.5, "jeu de chaque côté de la machine"
assert abs(PLAN.z0 - NC.MACHINE.z1 - M.JEU_PLAN) < 1e-9, "le plan passe à 0,5 au-dessus de la machine, sans la toucher"
assert PLAN.z1 < M.ROBINET["z"] and PLAN.z1 < PRISES.z0
assert XJ1 - XJ0 >= COUL["NL"] + 0.3, "profondeur du caisson ≥ longueur nominale + 3 mm (règle Blum)"
assert XJ0 + COUL["NL"] <= XJ1 - EP, "la coulisse s'arrête devant la traverse du mur"
assert abs(YCI[1] - YCI[0] - (LW - SKW)) < 1e-9, "largeur intérieure du tiroir = caisson − 42 mm (règle Blum)"
JEU_JOUE = YCI[0] - EP - YJN[1]                                 # 3 mm entre traverse de 18 et joue (5 sur la feuillure à 16)
assert JEU_JOUE >= 0.25
GORGE = (YCI[1] - TRINGLE) - (YCI[0] + TRINGLE)                 # 40,1 entre les tringles : le corps du panier passe là
assert PANIER["corps_l"] <= GORGE, "le corps du panier passe entre les tringles"
APPUI = (PANIER["l"] - GORGE) / 2                               # 1,3 de rebord posé de chaque côté
assert APPUI >= 0.8 and PANIER["l"] <= YCI[1] - YCI[0] + 2 * EP, "le rebord pose sur la tringle et la traverse"
assert X_R[1] <= XF1 + L_COTE - 1, "le rebord s'arrête avant le bout des traverses"
for _k in ZT:
    _z0 = ZT[_k] - H_T
    assert ZF[_k][0] <= _z0 - COUL["h"] and ZT[_k] < ZF[_k][1], "traverses et coulisses derrière la façade"
    assert ZT[_k] - FOND >= _z0 + 1.2 + EP + 0.5, "le corps passe au-dessus de la semelle"
assert ZT["bas"] - H_T - COUL["h"] >= Z_PLINTHE, "coulisse basse au-dessus de la plinthe"
TETE = dict(haut=M.Z_PLAN - ZT["haut"] - PANIER["rebord"],      # 5,0 entre le rebord et le dessous du plan
            bas=ZT["haut"] - H_T - COUL["h"] - ZT["bas"] - PANIER["rebord"])   # 5,3 sous la coulisse du tiroir du haut
assert min(TETE.values()) >= 4, "le tas qui dépasse du panier passe en refermant"
_tz = ZT["haut"] - H_T
assert ZT["bas"] + PANIER["rebord"] < _tz - COUL["h"], "le panier du bas passe sous les coulisses du haut"
DEGAGE = M.FACE - (X_R[1] - COUL["course"])                     # 0,3 entre l'arrière du rebord sorti et le nu du plan
assert DEGAGE >= 0, "sorti à fond, le panier n'est plus sous le plan ni sous la façade du dessus : il monte tout droit"
assert LITRES > 50 and LINGE < PANIER["conseil"], "un panier plein reste sous le poids conseillé par le fabricant"


def _collisions(bl):
    e, r = 1e-6, []
    for i, a in enumerate(bl):
        for b in bl[i + 1:]:
            if (a.x0 < b.x1 - e and b.x0 < a.x1 - e and a.y0 < b.y1 - e and b.y0 < a.y1 - e and a.z0 < b.z1 - e and b.z0 < a.z1 - e):
                r.append((a.nom, b.nom))
    return r


for _s, _lv in ((None, 0), ("haut", 0), ("bas", 0), ("bas", 25), ("haut", 25)):
    _c = [p for p in _collisions(etat(_s, _lv)) if not {"siphon", "arrivee"} & set(p)
          and not (p[0].startswith("panier_") and p[0][:10] == p[1][:10])]    # les parois d'un même panier se touchent
    assert not _c, (_s, _lv, _c)

# ------------------------------------------------------------------ portes
# Porte de la machine, cotes estimées de niv_commun. Le chant de la façade avance de 2 devant la machine.
_d = NC.HUBLOT["d"]
EP_LL = 4.0                                                     # épaisseur de la porte côté charnière, estimée
_vx, _vy = M.FACE - NC.X_LL_FACE, YF[1] - NC.CHARNIERE_LL
_dist = math.hypot(_vx, _vy)
A_FACADE = math.degrees(math.acos(_vy / _dist)) - math.degrees(math.asin(EP_LL / _dist))     # butée sur le coin de la façade
A_SORTI = math.degrees(math.acos((YF[1] - NC.CHARNIERE_LL) / _d))                            # tiroir sorti : butée sur son flanc
MUR = NC.CHARNIERE_LL - YF[1]                                   # 7,1 entre le flanc du tiroir sorti et la porte à 90°
Z_HAUT_LL = NC.HUBLOT["z"] + _d / 2                             # 73,5 : haut de la porte
assert 90 < A_SORTI < 110 and 110 < A_FACADE < 170
assert ZT["haut"] > Z_HAUT_LL > ZT["bas"], "on atteint le panier du haut par-dessus la porte, pas celui du bas"
# Porte d'entrée : vantail ouvert à 90° à 9 du nu ; sortie à fond, la façade atteint 119
ENTREE_LIBRE = NC.JEU_PORTE
X_SORTI = M.FACE - COUL["course"]
assert X_SORTI < NC.X_PORTE
A_ENTREE = math.degrees(math.atan2(YF[0], NC.X_PORTE - X_SORTI))     # angle où le vantail bute sur la façade sortie : < 1°
assert A_ENTREE < 2
POP = 5.0                                                       # ce que le déclencheur sort seul, estimé
assert POP < ENTREE_LIBRE, "le déclencheur ne touche pas le vantail ouvert"

# ------------------------------------------------------------------ masses, efforts, basculement (estimés)


def _kg(b):
    return (b.x1 - b.x0) * (b.y1 - b.y0) * (b.z1 - b.z0) * DENSITE / 1000


_tr = [b for b in tiroir("bas") if b.role != "vis"]
M_BERCEAU = sum(_kg(b) for b in _tr) + 0.9                      # bois du tiroir + 0,9 kg de partie mobile de coulisses (estimé)
M_VIDE = M_BERCEAU + PANIER["masse"]
M_PLEIN = M_VIDE + LINGE
assert M_PLEIN <= COUL["charge"], "charge Blum"
X_CDG = (XF1 + L_COTE / 2)                                      # centre du tiroir rentré, façade comprise (≈)
_fx = [(_kg(b), (b.x0 + b.x1) / 2) for b in [PLAN] + CAISSON]
M_FIXE = sum(m for m, _ in _fx)
M_STAB = sum(m * (x - X_PIED) for m, x in _fx)                  # kg·cm, retient vers l'arrière, tiroirs comptés à part
BRAS_SORTI = X_PIED - (X_CDG - COUL["course"])                  # bras d'un tiroir sorti devant les vérins
BRAS_RENTRE = X_CDG - X_PIED
M_UN = M_STAB + M_PLEIN * BRAS_RENTRE - M_PLEIN * BRAS_SORTI    # > 0 : un sorti, l'autre rentré plein
M_DEUX = M_STAB - 2 * M_PLEIN * BRAS_SORTI                      # < 0 : les deux sortis : ça bascule
assert M_UN > 0 and M_DEUX < 0, "un tiroir sorti tient, les deux sortis basculent"
APPUI_ADULTE = 30                                               # kg appuyés sur une façade sortie
BRAS_APPUI = X_PIED - X_SORTI
F_MUR = (2 * M_PLEIN * BRAS_SORTI + APPUI_ADULTE * BRAS_APPUI - M_STAB) / Z_FIXE    # kgf dans les 2 vis, pire cas
assert F_MUR / 2 < 50, "chaque vis du mur reste très en dessous de la tenue d'une cheville de 8 (estimée)"

# ------------------------------------------------------------------ planches : ce qu'on achète suffit
_J = M.Z_PLAN - M.Z0
assert 3 * _J <= 2 * 200 and 200 - 2 * _J >= 0                  # tablette 1 : 2 joues ; tablette 2 : 1 joue et 2 traverses
assert 200 - _J >= 2 * L_COTE and 2 * L_COTE <= 200 and H_T * 2 <= 200 - _J
assert PLAN.y1 - PLAN.y0 + 2 * H_F + 2 <= 250 and YF[1] - YF[0] <= 60, "plateau et façades dans la même planche de 250"

# ------------------------------------------------------------------ prix
_W, _V = M.WELDOM, next(p for p in M.VERNIS["pots"] if p["l"] == 2.5)
_D = M.PANNEAUX["D"][0]
_oct = "relevé oct. 2026, repris du meuble actuel"


def _L(libelle, qte, pu, source, statut="relevé"):
    return dict(libelle=libelle, qte=qte, pu=pu, source=source, statut=statut)


LIGNES = [
    _L("Tablette chêne pleine lame 250 × 60 × 2 : plateau et deux façades, même planche", 1, 119.00,
       "Leroy Merlin, réf. 70626031, 29/10/2026"),
    _L(f"{_D['nom']} : 3 joues, 4 traverses, pièces cachées", 3, _D["prix"], f"Weldom, réf. {_D['ref']}, 26/10/2026"),
    _L("Paire de coulisses Blum MOVENTO 760H5500S, sortie totale amortie, 550 mm, 40 kg", 2, 41.90,
       f"demos-trade.eu, code 349928, {RELEVE} ; livraison en France à confirmer"),
    _L("Attache de façade Blum T51.7601, 2 gauches et 2 droites", 4, 3.00,
       "2,22 € lu chez demos-trade.eu, mais par paquet de 100 ; prix à l'unité ailleurs non lu", "estimé"),
    _L("Déclencheur Blum TIP-ON BLUMOTION pour MOVENTO, classe jusqu'à 20 kg (jeu pour un tiroir)", 2, 24.83,
       f"demos-trade.eu, modules 275344 à 275347, 20,52 € HT, {RELEVE}"),
    _L("Axe de synchronisation Blum T60.1125W", 2, 6.50, "5,42 € HT chez Foussier en 2018, majoré", "estimé"),
    _L("Panier filet Elfa 45 × 55 × 28,5, graphite", 2, PANIER["prix"],
       f"maison-dressing-rangement.com, réf. 145228 : cotes lues {RELEVE}, 37,62 € lu pour la hauteur 8,5 seulement", "estimé"),
    _L(_V["nom"], 1, _V["prix"], f"Weldom, réf. {_V['ref']}, {_oct}"),
    _L(_W["verin"][0], 3, _W["verin"][1], f"Weldom, réf. {_W['verin'][4]}, {_oct}"),
    _L(_W["insert"][0], 2, _W["insert"][1], f"Weldom, réf. {_W['insert'][4]}, {_oct}"),
    _L(_W["vis60"][0], 1, _W["vis60"][1], f"Weldom, réf. {_W['vis60'][4]}, {_oct}"),
    _L(_W["vis40"][0], 1, _W["vis40"][1], f"Weldom, réf. {_W['vis40'][4]}, {_oct}"),
    _L(_W["vis16"][0], 1, _W["vis16"][1], f"Weldom, réf. {_W['vis16'][4]}, {_oct}"),
    _L(_W["equerre_a"][0], 2, _W["equerre_a"][1], f"Weldom, réf. {_W['equerre_a'][4]}, {_oct}"),
    _L(_W["cheville"][0][0], 1, _W["cheville"][0][1], f"Weldom, réf. {_W['cheville'][0][4]}, {_oct}"),
    _L(_W["cheville"][1][0], 1, _W["cheville"][1][1], f"Weldom, réf. {_W['cheville'][1][4]}, {_oct}"),
    _L(_W["silicone"][0], 1, _W["silicone"][1], f"Weldom, réf. {_W['silicone'][4]}, {_oct}"),
    _L(_W["mousse"][0], 1, _W["mousse"][1], f"Weldom, réf. {_W['mousse'][4]}, {_oct}"),
    _L("Colle à bois D3, abrasifs", 1, 24.00, "ordre de grandeur", "estimé"),
    _L("Prise Legrand Céliane 2P+T Surface, anodisé alu, complète", 3, 16.46, f"123elec.com, lu en résultat de recherche, {RELEVE}"),
    _L("Support triple Legrand Batibox 080253", 1, 5.89, f"123elec.com, lu en résultat de recherche, {RELEVE}"),
    _L("Plaque Legrand Céliane métal, 3 postes, aluminium", 1, 29.62, f"prix de la finition carbone 068983, domomat.com, {RELEVE}", "estimé"),
    _L("Boîte d'encastrement Legrand Batibox 3 postes, profondeur 50", 1, 11.00, "11,10 € lu pour la profondeur 40 (comparateur)", "estimé"),
    _L("Scie cloche diamant Ø 68 pour le carrelage", 1, 44.90, f"Brico Dépôt, en ligne, {RELEVE}"),
    _L("Foret diamant Ø 8 pour le carrelage", 1, 12.00, "ordre de grandeur", "estimé"),
    _L("Port des trois commandes en ligne (Blum, Elfa, Legrand)", 1, 45.00, "ordre de grandeur", "estimé"),
]
ATELIER = (800, 1400)                                           # estimé : 15 à 25 h d'atelier, sans devis

FICHE = NC.verifier(dict(
    niveau=4, nom="Sur mesure", resume=RESUME,
    lignes=LIGNES,
    heures=(20, 30),
    outils=["perceuse-visseuse", "scie circulaire et règle", "scie sauteuse", "défonceuse (feuillure des traverses)",
            "foret diamant et scie cloche Ø 68 sur la perceuse", "ponceuse", "serre-joints"],
    paniers=dict(nombre=2, nom="Elfa panier filet 45 × 55, 3 glissières, graphite", l=PANIER["l"], p=PANIER["p"], h=PANIER["h"],
                 litres=round(LITRES), prix=PANIER["prix"], url=PANIER["url"],
                 statut=f"cotes relevées le {RELEVE}, prix de cette hauteur estimé, corps sous le rebord estimé"),
    traverses=dict(matiere="chêne lamellé-collé, côtés du tiroir, avec tringle collée", section=f"1,8 × {cm(H_T)}",
                   longueur=L_COTE, appui=f"le rebord latéral du panier pose sur {cm(APPUI)} (tringle et haut de la traverse)"),
    gestes=dict(
        mettre=[f"genou ou main sur la façade : elle sort d'environ {cm(POP)} seule (estimé) ; la tirer d'un doigt jusqu'à la butée",
                f"tout le panier est alors devant le plan : lâcher le linge d'en haut, panier du bas à {cm(ZT['bas'])} du sol, du haut à {cm(ZT['haut'])}",
                "repousser du genou : l'amortisseur finit la course",
                "l'autre panier ne bouge pas"],
        retirer=["porte d'entrée fermée, sortir le tiroir à fond",
                 f"soulever le panier tout droit par son rebord (≈ {cm(LINGE + PANIER['masse'])} kg plein)",
                 f"panier du bas : même geste en se baissant, rebord à {cm(ZT['bas'])} du sol ; panier du haut : il est à {cm(ZT['haut'])}, à hauteur de hanche",
                 "repousser le tiroir vide, de la hanche",
                 "ouvrir la porte de la machine, poser le panier au sol devant le hublot, vider, reposer sur le tiroir",
                 f"sans sortir le panier : porte à 90°, on prend le linge du panier du haut par-dessus la porte ({cm(Z_HAUT_LL)}) ; impossible pour celui du bas"]),
    ouverture=dict(largeur=round(PANIER["corps_l"], 1), profondeur=round(PANIER["corps_p"], 1),
                   note=f"tiroir sorti, le panier est entièrement devant le plan : toute sa bouche ({cm(PANIER['corps_l'])} × "
                        f"{cm(PANIER['corps_p'])}) est libre jusqu'au plafond, pour chacun des deux ; tiroir rentré, on ne peut rien jeter"),
    independants=True,
    prises=dict(nombre=3, modele="Legrand Céliane 2P+T Surface, anodisé alu, plaque métal 3 postes",
                pose=f"encastrées dans le mur du fond carrelé, à {cm(PRISES.z0)} du sol, à {cm(PRISES.y0 - M.ROBINET['y'])} à droite du robinet "
                     "d'arrêt ; trois carottages Ø 68, boîte 3 postes"),
    finition=["plateau et façades : chêne pleine lame, sans aboutage, vernis marin satiné, trois couches",
              "façades sans poignée, fil du bois vertical, continu d'une façade à l'autre et coupé dans la planche du plateau",
              "joints de 3 mm entre façades et sous le plateau, façades au nu du chant du plateau",
              "plinthe en retrait, même chêne",
              "tiroir ouvert : traverses et joues en chêne lamellé-collé verni, panier graphite, aucune coulisse visible"],
    risques=[f"sortis tous les deux, paniers pleins, les tiroirs font basculer un meuble non fixé : deux vis dans le mur du fond sont obligatoires, donc deux trous dans le carrelage",
             f"tiroir sorti, la porte d'entrée ne s'ouvre plus (butée à moins de {math.ceil(A_ENTREE)}°) : quelqu'un dehors ne peut pas entrer tant qu'il n'est pas repoussé",
             f"porte de la machine limitée à ≈ {A_FACADE:.0f}° par le coin de la façade, ≈ {A_SORTI:.0f}° tiroir sorti (estimé, à mesurer)",
             f"course Blum estimée : il ne reste que {cm(DEGAGE * 10)} mm de dégagement sous le nu du plan ; si elle est plus courte, on incline le panier vers soi pour le sortir",
             f"corps du panier estimé à {cm(PANIER['corps_l'])} de large : à mesurer avant de coller les tringles ; poids conseillé de 8 kg presque atteint plein",
             "Blum limite les côtés à 16 mm : feuillure de 2 mm à la défonceuse sur le bas des traverses, hors notice",
             "le déclencheur s'active à la moindre pression : un enfant ou un coup de pied ouvre le tiroir",
             "carrelage qui éclate au carottage ; nature du mur et passage du câble inconnus",
             "pièces Blum à commander en ligne, dont l'attache vendue par paquet de 100 chez le vendeur relevé"],
))


# ------------------------------------------------------------------ dessins
def _vu_de_face():
    """Fermé, seulement ce qui se voit : sans les pièces cachées derrière les façades."""
    return BASE + [b for b in CAISSON if not b.nom.startswith("traverse")] + [
        b for k in ("bas", "haut") for b in tiroir(k) if b.nom.startswith("facade")]


def face():
    o = []
    for k, t in (("haut", "panier du haut"), ("bas", "panier du bas")):
        zt = ZT[k]
        y0, y1 = YC - PANIER["corps_l"] / 2, YC + PANIER["corps_l"] / 2
        o.append(PL.rect(y0, -zt, y1, -(zt - FOND), "ocache"))
        o.append(PL.rect(YC - PANIER["l"] / 2, -(zt + PANIER["rebord"]), YC + PANIER["l"] / 2, -zt, "ocache"))
        o.append(PL.text(YC, -(zt - FOND / 2), t, "lt"))
        o.append(PL.text(YC, -(zt - FOND / 2) + 3.4, f"{LITRES:.0f} L, derrière la façade", "lt muted"))
    o.append(CO.chaine_h([M.Y0, YF[0], YF[1], NC.MACHINE.y0, NC.MACHINE.y1, M.Y1], 6, ext=0))
    o.append(CO.cote_v(-ZF["bas"][0], -ZF["bas"][1], YF[1] - 2.5, cm(H_F)))
    o.append(CO.cote_v(-ZF["haut"][0], -ZF["haut"][1], YF[1] - 2.5, cm(H_F)))
    o.append(CO.niveaux([(Z_PLINTHE, f"{cm(Z_PLINTHE)} plinthe", M.Y0),
                         (ZT["bas"], f"{cm(ZT['bas'])} traverses", M.Y0),
                         (ZT["haut"], f"{cm(ZT['haut'])} traverses", M.Y0),
                         (M.Z_PLAN, f"{cm(M.Z_PLAN)} sous plan", M.Y0),
                         (PLAN.z1, f"{cm(PLAN.z1)} dessus", M.Y0)], M.Y0 - 9))
    return NC.vue_face(_vu_de_face(), o, "Vue de face, fermé")


def coupe():
    s = YC
    o = []
    # le panier du bas soulevé, en tireté
    for b in panier("bas", parois=False):
        if not b.nom.endswith(("_rb_n", "_rb_s")):      # en bout de tiroir sorti, le panier posé est aussi dessiné en plein
            o.append(PL.poly(CO.contour(_dep(b, -COUL["course"], 30), "cote", s), "oswing"))
    # vantail de la porte d'entrée ouverte à 90°
    h = PLAN.z1 + 6
    o.append(PL.rect(NC.X_PORTE - 4, -h, NC.X_PORTE, 0, "ocache"))
    o.append(PL.text(NC.X_PORTE - 1, -h - 1, "porte d'entrée ouverte à 90°", "lt muted", "middle"))
    o.append(CO.cote_h(X_SORTI, M.FACE, 6, cm(COUL["course"]), ext=0))
    o.append(CO.cote_h(M.FACE, XJ0 + COUL["NL"], 6, cm(COUL["NL"]), ext=0))
    o.append(CO.cote_h(NC.X_PORTE, M.FACE, -82, cm(NC.JEU_PORTE)))
    o.append(PL.text(X_SORTI + COUL["course"] / 2, 12.5, "course, sortie totale (estimée)", "lt muted"))
    o.append(PL.text(M.FACE + 27, 12.5, "coulisse sous le tiroir", "lt muted"))
    xt = X_R[0] - COUL["course"] + PANIER["p"] / 2
    o.append(PL.text(xt, -(ZT["bas"] + 30 - 12), "panier soulevé", "lt"))
    o.append(PL.text(xt, -(ZT["bas"] - 10), "panier posé,", "lt"))
    o.append(PL.text(xt, -(ZT["bas"] - 10) + 3.4, "traverse derrière lui", "lt muted"))
    o.append(PL.text(XF1 + L_COTE / 2, -(ZT["haut"] - 13), "panier du haut sur ses traverses", "lt"))
    o.append(PL.text(XF1 + L_COTE / 2, -(ZT["bas"] - 13), "vide : tiroir sorti", "lt muted"))
    o.append(CO.niveaux([(ZT["bas"], f"{cm(ZT['bas'])} rebord", X_SORTI + 2),
                         (ZT["haut"], f"{cm(ZT['haut'])} rebord", M.FACE)], X_SORTI - 6))
    o.append(CO.cote_v(-(ZT["haut"] + PANIER["rebord"]), -M.Z_PLAN, XF1 + 30, cm(TETE["haut"])))
    o.append(CO.etiquette(XJ1 - EP / 2, -(M.Z_PLAN - 4), XJ1 - 12, -(PLAN.z1 + 2.5), "2 vis dans le mur", "end"))
    bl = etat("bas", 0, parois=False)
    return NC.vue_coupe(bl, s, o, sortie=60, titre="Coupe par les paniers, tiroir du bas sorti")


def dessus():
    z = 60
    bl = etat("bas")
    o = []
    for b in bl:
        if b.nom in ("facade_haut", "facade_bas"):
            o.append(PL.poly(CO.contour(b, "dessus", z), "oplan" + (" cut" if b.nom == "facade_haut" else "")))
    o.append(PL.poly(CO.contour(PLAN, "dessus", z), "oplanl"))
    # porte de la machine à 90° : un mur entre le panier sorti et le hublot
    o.append(PL.rect(NC.X_LL_FACE - _d, NC.CHARNIERE_LL, NC.X_LL_FACE, NC.CHARNIERE_LL + EP_LL, "ofac"))
    o.append(PL.text(NC.X_LL_FACE - _d / 2 - 14, NC.CHARNIERE_LL + 2.9, "porte machine à 90°", "lt"))
    o.append(CO.cote_v(YF[1], NC.CHARNIERE_LL, NC.X_LL_FACE - 18, cm(MUR)))
    o.append(PL.text(X_SORTI + COUL["course"] / 2 - 4, YC + 1, "panier du bas sorti", "lt"))
    o.append(PL.text(XF1 + L_COTE / 2, YC + 1, "panier du haut, rentré", "lt"))
    o.append(CO.cote_h(X_SORTI, M.FACE, M.Y0 - 6, cm(COUL["course"]), ext=YF[0]))
    o.append(CO.cote_h(NC.X_PORTE, M.FACE, 60, cm(NC.JEU_PORTE), ext=53))
    o.append(CO.chaine_v([YF[0], YCI[0] - EP, YCI[1] + EP, YF[1]], M.X1 + 8, ext=M.X1))
    return NC.vue_dessus(bl, z, o, "Vue de dessus, coupée à 60 du sol, tiroir du bas sorti")


def section():
    t_h, t_b = cm(TETE["haut"]), cm(TETE["bas"])
    figs = "".join([
        CO.figure("n4-face", "Vue de face, fermé", face(),
                  f"Deux façades de {cm(YF[1] - YF[0])} × {cm(H_F)}, joints de 3 mm. En tireté, les paniers derrière elles."),
        CO.figure("n4-coupe", "Coupe par les paniers, tiroir du bas sorti", coupe(),
                  f"Le tiroir du bas sort de {cm(COUL['course'])} ; en tireté rouge, son panier soulevé tout droit. Il passe à "
                  f"{cm(DEGAGE * 10)} mm du nu du plan. Le panier du haut reste rentré. Au fond, en haut, la pièce vissée au mur."),
        CO.figure("n4-dessus", "Vue de dessus, à 60 du sol", dessus(),
                  f"Panier du bas sorti. La porte de la machine à 90° fait un mur à {cm(MUR)} de son flanc. L'arc montre la porte "
                  f"ouverte à fond, cote estimée : le coin de la façade l'arrête vers {A_FACADE:.0f}°. Le vantail de la porte d'entrée "
                  f"passe à {cm(NC.JEU_PORTE)} du nu : tiroir sorti, il est dans son débattement."),
    ])
    i1 = NC.iso(_vu_de_face() + [PRISES], NEUVES, titre="Fermé")
    i2 = NC.iso(etat("bas", 25, prises=True), NEUVES, titre="Tiroir du bas sorti, panier soulevé")
    prix = NC.cout(FICHE)
    return f"""<p>Deux façades de chêne sans poignée, chacune portant un tiroir sans fond : le panier est posé sur les deux traverses de son tiroir, sort avec lui en entier devant le plan et se soulève.</p>
<div class="feuille">{figs}</div>
<div class="grid2">
<div class="fig">{i1}<p class="cap">Fermé : plateau et façades dans la même planche, trois prises sur le mur du fond.</p></div>
<div class="fig">{i2}<p class="cap">Tiroir du bas sorti : les deux traverses, le panier soulevé au-dessus ; le tiroir du haut n'a pas bougé.</p></div>
</div>

<h3>Fonctionnement</h3>
<p><b>Mettre.</b> Une pression du genou ou de la main sur la façade et elle sort d'environ {cm(POP)} seule (déclencheur Blum TIP-ON, course estimée). On la tire d'un doigt jusqu'à la butée : {cm(COUL['course'])} de course. La façade pleine ne retire rien : tiroir sorti, tout le panier est devant le plan, sa bouche de {cm(PANIER['corps_l'])} × {cm(PANIER['corps_p'])} est libre jusqu'au plafond, en haut comme en bas. Rebord à {cm(ZT['bas'])} du sol pour le bas, {cm(ZT['haut'])} pour le haut. En échange, on ne jette rien tiroir fermé : il faut un geste de plus qu'à un meuble ouvert. On repousse du genou, l'amortisseur finit la course. L'autre panier ne bouge pas.</p>
<p><b>Retirer.</b> Tiroir sorti, on soulève le panier par son rebord, tout droit ({cm(LINGE + PANIER['masse'])} kg plein). Pour vider dans la machine, le bon ordre est celui-ci : sortir le panier, repousser le tiroir de la hanche, ouvrir la porte de la machine, poser le panier au sol devant le hublot, vider, remettre. Ouverte à 90°, la porte fait un mur à {cm(MUR)} du flanc du tiroir sorti : son haut est à {cm(Z_HAUT_LL)}, on passe encore par-dessus vers le panier du haut, jamais vers celui du bas. Ouverte plus loin, elle bute : vers {A_SORTI:.0f}° sur le flanc d'un tiroir sorti, vers {A_FACADE:.0f}° sur le coin d'une façade fermée, qui avance de 2 devant la machine (angles estimés, porte à mesurer). Ouverte au-delà de 100°, elle empêche à son tour de sortir un tiroir : on ne laisse pas tout ouvert.</p>
<p><b>Hauteurs.</b> Deux façades de {cm(H_F)} sur une plinthe de {cm(Z_PLINTHE)}. Au-dessus de chaque rebord, tiroir rentré, il reste {t_h} en haut et {t_b} en bas : le linge peut dépasser d'autant, pas plus. Il n'en faut pas plus pour remplir, puisque le remplissage se fait tiroir sorti.</p>
<p><b>Ce qui porte.</b> Le rebord du panier pose de {cm(APPUI)} de chaque côté sur une tringle de chêne collée en haut de la traverse. Les deux traverses sont les côtés du tiroir, vissés à la façade, posés sur les coulisses Blum MOVENTO qui passent dessous, cachées. Elles n'occupent que 5 mm par côté, contre 12,7 pour une coulisse latérale à billes : le panier de 42,7 tient dans les {cm(LW)} entre joues. Tiroir plein : {cm(M_PLEIN)} kg pour 40 kg admis par paire. Panier : {cm(LINGE)} kg de linge, {LITRES:.0f} L à 0,12 kg/L (estimé), pour 8 kg conseillés par Elfa. La marge est faible : un panier tassé dépasse. Sous le panier, deux pièces de bois seulement, à l'avant et à l'arrière : l'air passe, et la grille laisse sécher le linge humide.</p>
<p><b>Ce qui arrête.</b> Les coulisses en fin de course, l'amortisseur à la fermeture. Le plateau repose sur les trois joues, de {cm(YJC[0] - YJN[1])} puis {cm(YJS[0] - YJC[1])} d'écart, et passe à {cm(M.JEU_PLAN * 10)} mm au-dessus de la machine sans la toucher.</p>
<p><b>Basculement.</b> Plateau et caisson pèsent {cm(M_FIXE)} kg et retiennent {M_STAB:.0f} kg·cm autour des vérins avant. Un tiroir plein sorti pousse de {M_PLEIN * BRAS_SORTI:.0f} kg·cm : seul, le meuble tient. Les deux sortis font {2 * M_PLEIN * BRAS_SORTI:.0f} kg·cm : le meuble part en avant. La machine ne le retient pas, elle n'est pas liée. Donc une pièce de chêne, en haut derrière les tiroirs, vissée dans le mur du fond par 2 vis 6 × 90 et chevilles de 8, trous au foret diamant. Dans le pire cas, deux tiroirs sortis et {APPUI_ADULTE} kg appuyés sur une façade, chaque vis reprend ≈ {F_MUR / 2:.0f} kgf (estimé). Si l'on refuse de percer pour cela, le poteau entre le plan et le caisson haut fait le même travail, à condition que le caisson haut soit posé.</p>
<p><b>Porte d'entrée.</b> Ouverte à 90°, elle passe à {cm(NC.JEU_PORTE)} du nu : on n'a que cela de sortie. Le déclencheur ne la touche pas. Pour sortir à fond, on la ferme, ce qu'on fait de toute façon pour se tenir devant le meuble. Sens inverse : tiroir sorti, la porte fermée ne s'ouvre plus, elle bute sur le flanc de la façade dès l'entrebâillement. Une mousse collée sur ce flanc protège le bois. Il ne faut pas laisser un tiroir sorti en quittant la pièce.</p>
<p><b>Prises.</b> Trois postes Legrand Céliane sur le mur du fond, plaque métal, de {cm(PRISES.y0)} à {cm(PRISES.y1)} du mur nord, de {cm(PRISES.z0)} à {cm(PRISES.z1)} du sol, à {cm(PRISES.y0 - M.ROBINET['y'])} du robinet d'arrêt. Encastrer dans le carrelage demande trois carottages Ø 68 à la scie cloche diamant, et une boîte 3 postes scellée ; les ponts de carrelage entre trous peuvent casser, la plaque les couvre. Ce qu'on ne sait pas : la nature du mur et le chemin du câble, à décider avec l'électricien. Sans saignée sous carrelage, le câble doit arriver par derrière ou d'en haut. Norme NF C 15-100 d'après Legrand et TotalEnergies : prises interdites dans les volumes 0, 1 et 2 de la douche, le volume 2 s'arrêtant à 60 cm du volume 1 ; autorisées hors volume ; différentiel 30 mA sur le circuit. Le mur du fond est à plus de 140 de la douche, à l'ouest de la porte : hors volume, à confirmer sur place.</p>

<h3>Finition</h3>
<p>De face, on voit un seul panneau de chêne : plateau et façades viennent de la même tablette pleine lame de 250 × 60 × 2, sans aboutage, les façades coupées l'une à la suite de l'autre, fil vertical continu. Joints de 3 mm, façades au nu du chant du plateau, pas de poignée, plinthe en retrait. Vernis marin satiné, trois couches sur tout ce qui se voit. Tiroir ouvert : traverses et joues en chêne lamellé-collé de la tablette Weldom, moins uniforme que la façade, panier en grille graphite, aucun métal de coulisse à la vue. En haut, une plaque métal claire sur le carrelage. Pas d'éclairage : le panier sort à la lumière de la pièce, un ruban ne servirait qu'à la photo.</p>

<h3>Le prix</h3>
{NC.tableau_cout(FICHE)}
<p>Fait par le client, {heures_txt()} de travail. Confié à un atelier : compter {_e(ATELIER[0])} à {_e(ATELIER[1])} de main-d'œuvre en plus (ligne estimée, sans devis, 15 à 25 h d'atelier), soit ≈ {_e(prix + ATELIER[0])} à {_e(prix + ATELIER[1])}. Le compromis : ne confier que le plateau, les façades et leur vernis (≈ 250 à 400 € en plus, estimé), là où une erreur se voit, et monter le reste : ≈ {_e(prix + 250)} à {_e(prix + 400)}.</p>
<p>Ce qui coûte, et pourquoi. La planche pleine lame (119 €) : un plateau sans aboutage et des façades assorties, pour moins cher qu'un plan de 25 mm à 385 €. Les coulisses cachées et leurs déclencheurs (≈ {_e(2 * 41.90 + 12 + 2 * 24.83 + 13)}) : 7,7 mm de largeur gagnés par côté, façades réglables sans outil, ouverture sans poignée. Les paniers : grille fine, lavable, qui ventile ; un sac en toile ou feutre sur cadre coûterait plus cher à faire coudre (estimé), sans mieux servir.</p>

<p class="note">Sources : règles de pose <a href="https://ea.blum.com/en/building-a-movento-drawer/">Blum</a> ; prix <a href="https://demos-trade.eu/blum-760h5500s-movento-550mm-40kg">Blum chez demos-trade</a> ; cotes <a href="{PANIER['url']}">panier Elfa</a> ; poids conseillé <a href="https://elfa.com/fr-fr/produits/classic-by-elfa/systeme-paniers/fonctions-de-rangement/wiredrawer">Elfa</a> ; norme <a href="https://www.legrand.fr/questions-frequentes/quelle-est-la-norme-nf-c-15-100-pour-la-salle-de-bain">Legrand</a>, <a href="https://www.totalenergies.fr/particuliers/parlons-energie/dossiers-energie/logement/l-installation-electrique-dans-la-salle-de-bain">TotalEnergies</a>. Consultés le {RELEVE}. Non trouvée : la course de la coulisse, estimée égale à sa longueur.</p>

<h3>Limites</h3>
<ul>
<li>Deux trous dans le mur du fond pour le fixer, trois pour les prises : ce niveau renonce au meuble sans fixation et au carrelage intact.</li>
<li>On ne jette rien sans ouvrir. C'est le prix des façades pleines : tout se voit propre, rien ne reste accessible d'un seul lancer.</li>
<li>Tiroir sorti, porte d'entrée condamnée. Le déclencheur s'active au moindre choc, enfant compris : à essayer avant de le garder ; sans lui, une rainure de prise à la défonceuse dans le haut de la façade fait le travail pour moins cher.</li>
<li>Cotes à mesurer avant de couper : corps du panier sous le rebord ({cm(PANIER['corps_l'])} estimés, largeur de tringle à ajuster), course réelle de la coulisse (il ne reste que {cm(DEGAGE * 10)} mm de marge), porte de la machine (charnière, diamètre, angle).</li>
<li>Traverses de 18 pour 16 admis par Blum : une feuillure de 2 mm en bas, hors notice, à valider sur un premier tiroir. Le plateau de 20, fin pour ce niveau, reste au choix de la planche unique.</li>
<li>Poste long : {heures_txt()}, vernis compris. Prix des pièces Blum relevés chez un revendeur européen, port et livraison en France à confirmer.</li>
</ul>"""


def _e(x):
    """Montant arrondi à la dizaine, pour les ordres de grandeur."""
    return f"{round(x, -1):,.0f} €".replace(",", " ")


def heures_txt():
    return f"{FICHE['heures'][0]} à {FICHE['heures'][1]} h"


if __name__ == "__main__":
    print(f"joues LW {LW:.1f}  intérieur tiroir {YCI[1] - YCI[0]:.1f}  gorge {GORGE:.1f}  appui rebord {APPUI:.2f}")
    print(f"façades {YF[1] - YF[0]:.1f} × {H_F:.1f}  rebords z {ZT}  tête {TETE}  dégagement {DEGAGE:.2f}")
    print(f"panier {LITRES:.0f} L, linge {LINGE:.1f} kg, tiroir vide {M_VIDE:.1f} kg, plein {M_PLEIN:.1f} kg")
    print(f"fixe {M_FIXE:.1f} kg, stab {M_STAB:.0f}, un sorti {M_UN:.0f}, deux sortis {M_DEUX:.0f} kg·cm, effort mur {F_MUR:.1f} kgf")
    print(f"porte machine : butée façade {A_FACADE:.0f}°, tiroir sorti {A_SORTI:.0f}°, mur à {MUR:.1f} ; porte d'entrée {A_ENTREE:.1f}°")
    print(f"coût {NC.cout(FICHE)} ; atelier {NC.cout(FICHE) + ATELIER[0]} à {NC.cout(FICHE) + ATELIER[1]}")
