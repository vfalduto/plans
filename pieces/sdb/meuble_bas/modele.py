# Meuble bas de la salle de bain (V8.7) : le modèle. Trois joues, un fond et un bas en mélaminé blanc de 18, levés sur
# des vérins, portent directement un plateau en chêne de 60 au-dessus de la machine. À côté de la machine, un placard à
# une étagère, deux bacs à linge et une porte découpée en U à chaque étage pour jeter le linge porte fermée. Rien de fixé
# au mur.
#
# Repris de 3d/sdb/bas.py (mêmes noms, mêmes valeurs). Les relevés de la pièce sont lus dans pieces/sdb/piece.py ; la
# cote du meuble haut (dessous, dessus, profil LED, version), encore en passerelle, dans 3d/sdb/modele.py
# (pieces.sdb.ancien.modele()). Dessins : dessins.py ; document : document.py.
#
# Cotes en cm, repère de la pièce : x vers l'est, y vers le sud, z depuis le sol.

import math
from dataclasses import dataclass

from pieces.sdb import ancien, piece as P

_HAUT = ancien.modele()
Z_HAUT = _HAUT.Z_HAUT                     # dessous du meuble haut : 158
Z_HAUT1 = _HAUT.Z_HAUT1                   # dessus du meuble haut : 248
VERSION_HAUT = _HAUT.VERSION              # version de la page du meuble haut


@dataclass
class Bloc:
    """Pièce rectangulaire (x0 → x1, y0 → y1, z0 → z1) ; encoche : (x0, x1, y0, y1) découpée dans le dessus ;
    entailles : rectangles (x0, x1, y0, y1) entaillés sur toute l'épaisseur."""
    role: str
    nom: str
    x0: float
    x1: float
    y0: float
    y1: float
    z0: float
    z1: float
    rep: str = ""
    groupe: str = ""
    encoche: tuple = ()
    entailles: tuple = ()


# vernis du plateau (3d/sdb/modele.py, V5.24 et V6.0) : Syntilor incolore satiné en phase aqueuse, rendement 12 m²/L par
# couche (fiche Weldom 5603010, relevée le 26/10/2026) ; trois couches
VERNIS = dict(couches=3, rendement=12, pots=[
    dict(l=0.25, prix=20.90, ref="5703473", nom="Vernis marin Syntilor incolore satiné 0,25 L"),
    dict(l=0.75, prix=37.50, ref="5603010", nom="Vernis marin Syntilor incolore satiné 0,75 L"),
    dict(l=2.5, prix=69.90, ref="1085572", nom="Vernis marin Syntilor Ultra Protect incolore satiné 2,5 L"),
])

EP = 1.8               # 18 mm : plateau en chêne, panneaux en mélaminé
# plateau : Weldom 82025610, chêne 200 × 60 × 18 (L et l en mm) ; relevé en ligne du 26/10/2026, stock non lu
PANNEAU = dict(L=2000, l=600, prix=66.90, stock=None, ref="82025610", magasin="Weldom",
               nom="Tablette chêne lamellé-collé brute FSC 200 × 60 × 18")
PANNEAU_L, PANNEAU_P = PANNEAU["L"] / 10, PANNEAU["l"] / 10
# mêmes tablettes que le meuble haut (haut.lignes) : même blanc, stock lu au Weldom
T60 = dict(L=250, l=60, prix=16.50, ref="9134941", stock=25, nom="Tablette mélaminé 250 × 60 × 18 blanc")
T50 = dict(L=250, l=50, prix=13.59, ref="9134940", stock=50, nom="Tablette mélaminé 250 × 50 × 18 blanc")
CHANT = dict(rouleau=500, prix=9.50, ref="5566191", nom="Bande de chant thermocollante blanc Primo 500 × 2,3 cm")
VERIN = dict(n=2, h=2, d=1.6, cmin=0.9, cmax=2.5, perce=0.8, prix=3.59, ref="3419935003173",   # prix en ligne du 04/11/2026, stock non lu
             nom="Vérin 6 pans blanc M6 H. 30 × Ø 8 — Castorama Saint-Loup")   # d : embout dessiné, diamètre non indiqué par la fiche
COLLE = dict(prix=8.99, ref="5059340615233", nom="Colle MS polymère Volden blanche 290 ml — Castorama Saint-Loup")
BAC = dict(l=40, p=54, h=25, litres=38, prix=5.99, ref="706.127.23", nom="Panier à linge SLIBB blanc 38 L, 54 × 40 × 25 — IKEA")   # fiche IKEA France
CHARNIERE = dict(angle=110, prix=10.00, ref="805.248.82", nom="Charnières UTRUSTA 110° amorties, lot de 2 — IKEA")   # fiche IKEA France
POIGNEE = dict(L=12, saillie=3, prix=6.00, ref="503.343.03", nom="Poignées BILLSBRO blanc 120 mm, lot de 2 — IKEA")  # L et prix : fiche ; saillie dessinée, non relevée
PRISE = dict(prix=5.59, ref="3414971087187", plaque=8, nom="Prise 2P+T affleurante Legrand Dooxie blanc — Castorama Saint-Loup")   # prix en ligne ; plaque : 8 de côté, de mémoire, à mesurer
BOITE = dict(prix=2.39, ref="3414972954365", d=6.7, prof=4, nom="Boîte d'encastrement Ø 67 × 40 Legrand Eco Batibox — Castorama Saint-Loup")   # prix en ligne ; tenue dans 18 mm non vérifiée
TRAIT = 0.4
PLATEAU_P = 60          # profondeur demandée : 60, contre le mur du fond (V5.10, client)
JEU_MUR = 0.3           # entre le meuble et les murs ; plateau à recouper à la mesure réelle
JEU_MACHINE = 1         # autour de la machine et sous le plateau : elle vibre sans rien toucher
JEU_FOND = 5            # entre le dos de la machine et le mur du fond (coudes des tuyaux)
TAPIS = dict(ep=1, l=60, p=54, brut=60, prix=13.50, ref="9161504", nom="Plaque anti-vibrations Noma Rub 60 × 60 × 1")

Z_MACH = TAPIS["ep"] + P.MACHINE["h"]          # dessus de la machine, posée sur le tapis : 86
Z_DESSUS = 92                             # dessus du plateau, demandé par le client (V8.7) : plan de travail à 92
Z_DESSOUS = Z_DESSUS - EP                 # dessous du plateau : 90,2, soit 4,2 d'air au-dessus de la machine
assert Z_DESSOUS - Z_MACH >= JEU_MACHINE

PX0, PX1 = P.X1 - PLATEAU_P, P.X1         # plateau : 174 → 234
PY0, PY1 = P.Y0 + JEU_MUR, P.Y1 - JEU_MUR # plateau : 0,3 → 114,7
MX1 = P.X1 - JEU_FOND
MX0 = MX1 - P.MACHINE["p"]                     # façade de la machine : 176
JX0, JX1 = MX0, P.X1 - JEU_MUR            # joues : au nu de la façade, le plateau dépasse de 2 devant
JOUE_P = JX1 - JX0                        # 57,7
JZ0 = VERIN["h"]                          # bas des panneaux, hors de l'eau : 2
JOUE_H = Z_DESSOUS - JZ0                  # 88,2

# du nord au sud : joue nord, placard, joue du milieu, machine, joue sud
NY0, NY1 = PY0, PY0 + EP
SY1 = PY1
SY0 = SY1 - EP
MY1 = SY0 - JEU_MACHINE
MY0 = MY1 - P.MACHINE["l"]
CY1 = MY0 - JEU_MACHINE
CY0 = CY1 - EP
BAIE = CY0 - NY1                          # largeur intérieure : 47,5
JEU_SUD = P.Y1 - MY1
JOUES = (("n", NY0, NY1), ("c", CY0, CY1), ("s", SY0, SY1))

# fond : entre les joues nord et milieu, au nu de leur arrière
DX0, DX1 = JX1 - EP, JX1                  # 231,9 → 233,7
PROF_LIBRE = DX0 - JX0                    # du plan des joues au fond : 55,9

# bas du placard au ras du bas des joues ; deux étages égaux, du dessus du bas au dessous du plateau
BZ0, BZ1 = JZ0, JZ0 + EP                  # bas : 2 → 3,8
NIV_H = (Z_DESSOUS - BZ1 - EP) / 2        # hauteur de chaque étage : 42,3
EZ0, EZ1 = BZ1 + NIV_H, BZ1 + NIV_H + EP  # étagère : 44,5 → 46,3
ETAGES = (BZ1, EZ1)                       # bas de chaque étage
EX0 = JX0 + 1                             # bas et étagère en retrait de 1 sur le plan des joues
ETAGERE_P = DX0 - EX0                     # 54,9
BAC_MAX = 0.75 * NIV_H                    # 3/4 de l'étage : 31,7
BX0, BX1 = EX0, EX0 + BAC["p"]            # bacs : au nu de l'étagère, 0,9 d'air devant le fond
BY0, BY1 = (NY1 + CY0 - BAC["l"]) / 2, (NY1 + CY0 + BAC["l"]) / 2

# porte en applique sur les joues nord et milieu, comme un meuble IKEA ; poignée à droite vue de face (au sud), charnières au nord
JEU_PORTE = 0.2                           # autour de la porte et devant les joues (charnière à régler ; de mémoire, à confirmer sur place)
PORTE_X0 = JX0 - JEU_PORTE - EP           # face avant : 174, au nu du plateau
PORTE_X1 = PORTE_X0 + EP
PORTE_Y0, PORTE_Y1 = NY0 + JEU_PORTE, CY1 - JEU_PORTE
PORTE_Z0, PORTE_Z1 = JZ0, Z_DESSOUS - JEU_PORTE
PORTE_L, PORTE_H = PORTE_Y1 - PORTE_Y0, PORTE_Z1 - PORTE_Z0   # 50,7 × 88
MONTANT = 6                               # bois gardé de chaque côté des découpes
FEN_H = PORTE_Z1 - (ETAGES[1] + BAC_MAX)  # hauteur des découpes, du point le plus bas au bord de la porte : 10
FEN_Y0, FEN_Y1 = PORTE_Y0 + MONTANT, PORTE_Y1 - MONTANT   # 38,7 de large
FEN_L = FEN_Y1 - FEN_Y0
FEN_R = 4                                 # rayon du fond du U : le chant suit, rien n'accroche
FEN_RH = 1.5                              # rayon des angles hauts de la découpe fermée
# (y0, y1, z0, z1) : la découpe du bas reste fermée, celle du haut s'ouvre sur le bord de la porte
FENETRES = ((FEN_Y0, FEN_Y1, ETAGES[0] + BAC_MAX, ETAGES[0] + BAC_MAX + FEN_H), (FEN_Y0, FEN_Y1, ETAGES[1] + BAC_MAX, PORTE_Z1))
CHARN_Z = (12, 70)                        # axes des charnières : la haute reste sous la découpe du haut
CUVETTE = 3.5                             # Ø de la cuvette (standard, de mémoire : à vérifier sur la notice)
CUV_RIVE = 4.0                            # de la rive de la porte au bord opposé de la cuvette
POI_Y = PORTE_Y1 - MONTANT / 2            # axe de la poignée, dans le montant droit
POI_Z0, POI_Z1 = 52, 52 + POIGNEE["L"]    # entre les deux découpes, à portée de main
OUVERTURE = 85                            # angle dessiné : la poignée arrive contre la porte d'entrée fermée (estimation)

# colonne : un panneau en diagonale dans l'angle du fond et du mur nord, posé sur le plateau, sous le meuble haut. Chants biseautés à 45°.
COL_H = Z_HAUT - Z_DESSUS - JEU_PORTE   # 65,8 : 2 mm de moins que l'écart, à recouper à la mesure réelle
COL_L = 18                                # largeur de la face avant, assez pour la boîte Ø 67 derrière
COL_JAMBE = COL_L / math.sqrt(2)          # emprise le long de chaque mur : 12,7
COL_XF, COL_YF = JX1, PY0                 # sommet de l'angle, à 0,3 des murs
COL_A = (COL_XF - COL_JAMBE, COL_YF)      # bout de la face avant côté mur nord
COL_B = (COL_XF, COL_YF + COL_JAMBE)      # bout de la face avant côté mur du fond
_ep_d = EP * math.sqrt(2)                 # épaisseur mesurée le long d'un mur
COL_XY = [COL_A, COL_B, (COL_XF, COL_YF + COL_JAMBE - _ep_d), (COL_XF - COL_JAMBE + _ep_d, COL_YF)]   # coupe du panneau
COL_U = (1 / math.sqrt(2), 1 / math.sqrt(2))     # le long de la face avant
COL_N = (1 / math.sqrt(2), -1 / math.sqrt(2))    # vers l'angle
COL_C = ((COL_A[0] + COL_B[0]) / 2, (COL_A[1] + COL_B[1]) / 2)    # milieu de la face avant
PRISES_Z = (103, 113, 123)                # axes des 3 prises libres (V8.7 : +3 avec le plateau, 7 sous la plaque la plus basse)
PRISE_LED_Z = 146                         # axe du 4e poste, pour le transformateur des LED
COL_TROU = dict(x=230, y=4, d=2)          # passage du câble dans le plateau, caché par la colonne, au-dessus du placard
GOUL = 2                                  # goulotte du câble, et entaille de l'étagère dans l'angle arrière côté nord
ARRIVEE = dict(x=200, z=8)                # sortie du câble en bas du mur nord (relevé client) : cotes supposées, à relever sur place
LED_X = _HAUT.LED.x0                      # profil LED sous le meuble haut


def col_pt(t, n=0):
    """Point à t de la largeur de la face avant, à n derrière elle."""
    return (COL_A[0] + t * COL_L * COL_U[0] + n * COL_N[0], COL_A[1] + t * COL_L * COL_U[1] + n * COL_N[1])


COL_VIS = tuple(col_pt(t, EP / 2) for t in (0.25, 0.5, 0.75))    # vis du bas et du haut, dans le chant du panneau

GONDS_X = P.X1 - P.GONDS
BOUT_NORD = P.X1 - P.ALCOVE["nord"]
BOUT_SUD = P.X1 - P.ALCOVE["sud"]
DEVANT = MX0 - GONDS_X                    # entre la façade de la machine et le vantail ouvert à 90°
DEVANT_PORTE = PORTE_X0 - GONDS_X         # entre la porte du placard fermée et le vantail ouvert à 90°
ANGLE_VANTAIL = math.degrees(math.asin((DEVANT_PORTE - POIGNEE["saillie"]) / (POI_Y - PORTE_Y0)))   # ouverture possible, vantail à 90°
RESTE_NIV = Z_HAUT - Z_DESSUS           # entre le dessus du plateau et le dessous du meuble haut
TX0, TX1 = MX1 + 0.5 - TAPIS["p"], MX1 + 0.5
TY0, TY1 = (MY0 + MY1 - TAPIS["l"]) / 2, (MY0 + MY1 + TAPIS["l"]) / 2

PIECES_DEBIT = [("A", "Plateau, chêne", 1, PY1 - PY0, PLATEAU_P), ("B", "Joue", 3, JOUE_H, JOUE_P), ("C", "Fond", 1, JOUE_H, BAIE),
                ("D", "Étagère", 1, BAIE, ETAGERE_P), ("E", "Porte", 1, PORTE_H, PORTE_L), ("F", "Bas", 1, BAIE, ETAGERE_P),
                ("G", "Colonne, biseautée", 1, COL_H, COL_L)]
VIS_PANNEAU = 3                           # vis 4 × 40 à chaque bout du fond, du bas et de l'étagère, à travers les joues

# elles ne portent rien, le plateau pose à plat sur le chant : elles l'empêchent de glisser ou de se lever
EQUERRES = [("Joue nord sous le plateau, côté placard", 2), ("Joue du milieu sous le plateau, côté placard", 2),
            ("Joue sud sous le plateau, côté machine", 2)]
N_EQUERRES = sum(n for _, n in EQUERRES)
EQUERRES_X = (JX0 + 6, JX1 - 6)
VERINS_X = (JX0 + 6, JX1 - 6)


def decoupe():
    """Les panneaux dans les tablettes : pour chacune, (tablette, [(repère, longueur, largeur)])."""
    j = ("B", JOUE_H, JOUE_P)
    return [(T60, [j, j, ("D", ETAGERE_P, BAIE)]), (T60, [j, ("E", PORTE_H, PORTE_L), ("F", ETAGERE_P, BAIE)]), (T50, [("C", JOUE_H, BAIE), ("G", COL_H, COL_L)])]


def chant_vu():
    """Longueur de chant à plaquer, en cm : avant des joues, tour de la porte, tour des deux découpes, avant du bas et de l'étagère.
    Les angles arrondis sont comptés droits : c'est un peu trop."""
    return 3 * JOUE_H + 2 * (PORTE_H + PORTE_L) + 2 * FEN_H + 2 * (FEN_L + FEN_H) + 2 * BAIE


def rouleaux_chant():
    return math.ceil(chant_vu() * 1.1 / CHANT["rouleau"])     # 10 % de chutes


def pot_vernis():
    """Le plus petit pot qui couvre le plateau ; sinon le plus grand."""
    litres = (2 * (PY1 - PY0) * PLATEAU_P + 2 * (PY1 - PY0 + PLATEAU_P) * EP) / 1e4 * VERNIS["couches"] / VERNIS["rendement"]
    pots = sorted(VERNIS["pots"], key=lambda x: x["l"])
    return next((x for x in pots if x["l"] >= litres), pots[-1])


def prix():
    """Achats du meuble entier : lignes (nom, réf., quantité, prix unitaire, stock), au format de plan.liste."""
    lots = -(-N_EQUERRES // 6)
    v = pot_vernis()
    n60 = sum(1 for t, _ in decoupe() if t is T60)
    n50 = sum(1 for t, _ in decoupe() if t is T50)
    return [(PANNEAU["nom"] + " — Weldom", PANNEAU["ref"], 1, PANNEAU["prix"], None),
            (T60["nom"], T60["ref"], n60, T60["prix"], T60["stock"]),
            (T50["nom"], T50["ref"], n50, T50["prix"], T50["stock"]),
            (CHANT["nom"], CHANT["ref"], rouleaux_chant(), CHANT["prix"], None),
            (CHARNIERE["nom"], CHARNIERE["ref"], 1, CHARNIERE["prix"], None),
            (POIGNEE["nom"], POIGNEE["ref"], 1, POIGNEE["prix"], None),
            (BAC["nom"], BAC["ref"], 2, BAC["prix"], None),
            (PRISE["nom"], PRISE["ref"], len(PRISES_Z) + 1, PRISE["prix"], None),
            (BOITE["nom"], BOITE["ref"], len(PRISES_Z) + 1, BOITE["prix"], None),
            (VERIN["nom"], VERIN["ref"], VERIN["n"] * len(JOUES), VERIN["prix"], None),
            (COLLE["nom"], COLLE["ref"], 1, COLLE["prix"], None),
            (v["nom"], v["ref"], 1, v["prix"], None),
            (TAPIS["nom"], TAPIS["ref"], 1, TAPIS["prix"], None),
            ("Lot de 6 équerres galvanisées 50 × 50 × 35", "5605252", lots, 5.95, None),
            ("Lot de 400 vis Standers 4 × 16", "5618694", 1, 7.95, None),
            ("Silicone d'étanchéité GEB 593350 blanc 310 ml", "95216443", 1, 9.00, None)]


def total():
    return sum(q * px for _, _, q, px, _ in prix())


# ------------------------------------------------------------------ tenue (ordres de grandeur)
E_CHENE = 10e9          # module du chêne, valeur courante de la littérature, non mesurée sur ce panneau
RHO_CHENE = 700         # kg/m³, valeur courante
E_AGGLO = 2.5e9         # module de l'aggloméré, valeur courante, non mesurée
RHO_AGGLO = 650         # kg/m³, valeur courante, non mesurée sur ce panneau
LINGE = 15              # kg sur l'étagère ou le bas : un bac plein, ordre de grandeur


def tenue():
    """Flèches du plateau (100 kg au milieu) et de l'étagère (bac plein), contrainte, masse, marge au basculement vers
    l'avant (100 kg sur le bord du plateau, à vide)."""
    b, h, L = PLATEAU_P / 100, EP / 100, (SY0 - CY1) / 100
    i = b * h ** 3 / 12
    p = 100 * 9.81
    fleche = p * L ** 3 / (48 * E_CHENE * i) * 1000
    contrainte = p * L / 4 / (b * h ** 2 / 6) / 1e6
    ie = ETAGERE_P / 100 * h ** 3 / 12
    fleche_e = 5 * LINGE * 9.81 * (BAIE / 100) ** 3 / (384 * E_AGGLO * ie) * 1000
    m = lambda a, c: a / 100 * c / 100 * h * RHO_AGGLO     # noqa: E731
    m_j, m_d, m_e = m(JOUE_H, JOUE_P), m(JOUE_H, BAIE), 2 * m(BAIE, ETAGERE_P)     # m_e : étagère et bas
    m_po = m(PORTE_H, PORTE_L) - 2 * m(FEN_L, FEN_H)
    m_p = (PY1 - PY0) / 100 * b * h * RHO_CHENE
    masse = 3 * m_j + m_d + m_e + m_po + m_p
    retenue = (3 * m_j * JOUE_P / 2 + m_d * (DX0 - JX0) + m_e * (EX0 + ETAGERE_P / 2 - JX0) + m_po * (PORTE_X0 + EP / 2 - JX0)
               + m_p * ((PX0 + PX1) / 2 - JX0)) * 9.81 / 100
    return dict(fleche=fleche, contrainte=contrainte, fleche_e=fleche_e, masse=masse, porte=m_po, marge=retenue / (p * (JX0 - PX0) / 100))


def _arc(cy, cz, r, de, a):
    """Points d'un arc de centre (cy, cz) : de et a en degrés."""
    return [(cy + r * math.cos(math.radians(t)), cz + r * math.sin(math.radians(t))) for t in (de + (a - de) * k / 8 for k in range(9))]


def contour(f, ouverte=False):
    """Contour (y, z) d'une découpe en U : fond arrondi ; ouverte : le haut donne sur le bord de la porte."""
    y0, y1, z0, z1 = f
    bas_ = _arc(y0 + FEN_R, z0 + FEN_R, FEN_R, 180, 270) + _arc(y1 - FEN_R, z0 + FEN_R, FEN_R, 270, 360)
    if ouverte:
        return bas_ + [(y1, z1), (y0, z1)]
    return bas_ + _arc(y1 - FEN_RH, z1 - FEN_RH, FEN_RH, 0, 90) + _arc(y0 + FEN_RH, z1 - FEN_RH, FEN_RH, 90, 180)


def contour_porte():
    """Contour (y, z) de la porte, encoche du haut comprise."""
    y0, y1, _, z1 = FENETRES[1]
    fond = contour(FENETRES[1], True)[:-2]
    return [(PORTE_Y0, PORTE_Z0), (PORTE_Y1, PORTE_Z0), (PORTE_Y1, PORTE_Z1), (y1, z1)] + fond[::-1] + [(y0, z1), (PORTE_Y0, PORTE_Z1)]


@dataclass
class Porte(Bloc):
    """Bloc percé sur sa face ouest : contours [(y, z)] des découpes."""
    fenetres: tuple = ()


@dataclass
class Prisme:
    """Pièce à contour quelconque dans le plan x-y, extrudée de z0 à z1 : pour le dessin et les tests."""
    role: str
    nom: str
    xy: list
    z0: float
    z1: float
    groupe: str = ""
    rep: str = ""
    decor: tuple = ()
    x0 = property(lambda p: min(x for x, _ in p.xy))
    x1 = property(lambda p: max(x for x, _ in p.xy))
    y0 = property(lambda p: min(y for _, y in p.xy))
    y1 = property(lambda p: max(y for _, y in p.xy))


def plaque_3d(z):
    d = PRISE["plaque"] / 2
    return [(COL_C[0] + a * d * COL_U[0], COL_C[1] + a * d * COL_U[1], z + b) for a, b in ((-1, -d), (1, -d), (1, d), (-1, d))]


def blocs():
    """Le meuble, ses bacs et la machine, pour la vue isométrique et les tests."""
    enc = (PX1 - P.PASSE["p"], PX1, P.ROBINET["y"] - P.PASSE["l"] / 2, P.ROBINET["y"] + P.PASSE["l"] / 2)
    o = [Bloc("melamine", f"joue_{k}", JX0, JX1, y0, y1, JZ0, Z_DESSOUS, groupe="meuble") for k, y0, y1 in JOUES]
    o += [Bloc("pied", f"verin_{k}{i}", x - VERIN["d"] / 2, x + VERIN["d"] / 2, (y0 + y1 - VERIN["d"]) / 2, (y0 + y1 + VERIN["d"]) / 2, 0, JZ0, groupe="meuble")
          for k, y0, y1 in JOUES for i, x in enumerate(VERINS_X)]
    o.append(Bloc("melamine", "fond", DX0, DX1, NY1, CY0, JZ0, Z_DESSOUS, groupe="meuble"))
    o.append(Bloc("melamine", "bas", EX0, DX0, NY1, CY0, BZ0, BZ1, groupe="meuble"))
    o.append(Bloc("melamine", "etagere", EX0, DX0, NY1, CY0, EZ0, EZ1, groupe="meuble", entailles=((DX0 - GOUL, DX0, NY1, NY1 + GOUL),)))
    for i, e in enumerate(ETAGES):
        o.append(Bloc("sac", f"bac_{i + 1}", BX0, BX1, BY0, BY1, e, e + BAC["h"], groupe="bacs"))
    o.append(Bloc("chene", "plateau", PX0, PX1, PY0, PY1, Z_DESSOUS, Z_DESSUS, groupe="plateau", encoche=enc))
    o.append(Porte("melamine", "porte", PORTE_X0, PORTE_X1, PORTE_Y0, PORTE_Y1, PORTE_Z0, PORTE_Z1, groupe="porte", fenetres=(contour(FENETRES[0]), contour(FENETRES[1], True))))
    o.append(Bloc("pied", "poignee", PORTE_X0 - POIGNEE["saillie"], PORTE_X0, POI_Y - 0.6, POI_Y + 0.6, POI_Z0, POI_Z1, groupe="porte"))
    zc = Z_DESSUS + COL_H
    o.append(Prisme("melamine", "colonne", COL_XY, Z_DESSUS, zc, groupe="colonne", decor=tuple(("idec", plaque_3d(z)) for z in PRISES_Z + (PRISE_LED_Z,))))
    o.append(Bloc("machine", "lave_linge", MX0, MX1, MY0, MY1, TAPIS["ep"], Z_MACH, groupe="machine"))
    o.append(Bloc("pied", "tapis", TX0, TX1, TY0, TY1, 0, TAPIS["ep"], groupe="machine"))
    return o


# ------------------------------------------------------------------ pièces et étapes de montage
# Étape (numéro de 1 à 13 dans etapes_montage(), vues.py) où chaque pièce de blocs() est posée. Les joues nord et du milieu
# entrent avec le U (7), la joue sud ensuite (8) ; les vérins se posent avant (4), sur les joues encore à plat.
POSE = {"joue_n": 7, "joue_c": 7, "joue_s": 8, "fond": 7, "bas": 7, "etagere": 7, "plateau": 9, "porte": 12,
        "poignee": 12, "bac_1": 12, "bac_2": 12, "lave_linge": 13, "tapis": 13,
        **{f"verin_{k}{i}": 4 for k, _, _ in JOUES for i in range(len(VERINS_X))}}
# Étape de la pose de la colonne (pose_colonne(), 1 à 5) où la colonne est glissée dans l'angle.
POSE_COLONNE = {"colonne": 3}
# Pièces mises en évidence à une étape où rien n'est posé, ou en avance sur leur pose : l'étape travaille dessus.
ACCENT = {1: ("plateau",), 3: ("porte", "poignee"), 5: ("joue_n", "joue_c", "joue_s"), 6: ("joue_n", "etagere"),
          10: ("plateau",), 11: ("verin_s0", "verin_s1")}
# Pièces dessinées en gris à une étape, sans y être posées ni mises en évidence : celles qu'on travaille.
CONTEXTE = {4: ("joue_n", "joue_c", "joue_s"), 6: ("joue_c", "joue_s")}
# Étape de pose de la colonne : pièces mises en évidence quand la colonne ne vient pas d'être posée.
ACCENT_COLONNE = {2: ("colonne",), 4: ("colonne",)}


def cm(v):
    return f"{round(v + 1e-9, 1):g}".replace(".", ",")
