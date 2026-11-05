# Meuble bas (V8.5) : sdb-meuble-bas.html, à la racine. Trois joues, un fond et un bas en mélaminé blanc de 18, levés sur des vérins,
# portent directement un plateau en chêne de 60 au-dessus de la machine. À côté de la machine, un placard à une étagère, deux
# bacs à linge et une porte découpée en U à chaque étage pour jeter le linge porte fermée. Rien de fixé au mur.
#
#   python3 3d/sdb/bas.py   (just sdb)
#
# Cotes en cm, même repère que modele.py : x vers l'est, y vers le sud, z depuis le sol. Les relevés de la pièce sont lus
# dans modele.py ; le meuble est donné ici.

import math
import os
import sys
from dataclasses import dataclass
from html import escape

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import modele as M  # noqa: E402
import plan as PL  # noqa: E402
import cotes as CO  # noqa: E402
import pages as PG  # noqa: E402
import montage as MO  # noqa: E402

PAGE = "sdb-meuble-bas.html"
VERSION = "V8.5"
CHANGEMENTS = [
    ("V8.5", "05/11/2026", "Panneau perforé et ses deux montants retirés, à la demande du client. Le meuble bas revient à 296,82 €."),
    ("V8.4", "05/11/2026", "Colonne en diagonale : un seul panneau biseauté de 18 de large coupe l'angle à 45°, les prises regardent la pièce. Panneau perforé SKÅDIS de 36 × 56 sur le mur nord, au-dessus du plateau, porté par deux montants vissés au plateau et au meuble haut : rien n'est percé dans le carrelage. Le meuble bas passe à 306,82 €."),
    ("V8.3", "05/11/2026", "Arrivée du courant relevée par le client : en bas du mur nord. Le câble traverse la joue nord, longe sa face intérieure jusqu'à l'angle arrière et monte à la colonne. Le bas du placard n'a plus d'entaille. Position exacte de la sortie à relever. Prix inchangé."),
    ("V8.2", "05/11/2026", "Colonne en mélaminé dans l'angle du fond et du mur nord, entre le plateau et le meuble haut : 3 prises libres et un 4e poste en haut pour le transformateur des LED, dont le fil monte dans la colonne. Rien n'est percé dans le carrelage. Étagère et bas entaillés dans l'angle arrière pour le câble d'alimentation, qui passe par un trou dans le plateau. Le meuble bas passe à 296,82 €."),
    ("V8.1", "05/11/2026", "Placard fermé en bas : un panneau de mélaminé à 2 du sol porte le bac du bas, qui ne pose plus au sol. Étages ramenés à 40,7. Les fenêtres deviennent des U à fond arrondi de 10 de haut : celle du haut est une encoche ouverte sur le bord de la porte, celle du bas reste fermée. Prix inchangé : le bas sort d'une chute de tablette."),
    ("V8.0", "04/11/2026", "Placard : le cadre en tasseau est retiré, le fond est un panneau dans la même matière que les joues. Joues, fond, étagère et porte en mélaminé blanc. Étagère à mi-hauteur, deux bacs SLIBB, porte à poignée à droite sur charnières IKEA UTRUSTA, percée d'une fenêtre à 3/4 de la hauteur de chaque étage. Plus de peinture."),
    ("V7.9", "04/11/2026", "Le dos devient un vrai cadre : 2 montants, 2 traverses et 1 diagonale en tasseau, vissé contre les joues nord et milieu. Les 4 équerres de l'arrière disparaissent : 6 équerres en tout."),
    ("V7.8", "04/11/2026", "Dos remplacé par 2 traverses et 1 diagonale en tasseau de 38 × 38, à la demande du client. Le mur reste visible et la place libre passe à 53,9 de profondeur. Prix inchangé : les tasseaux et les vis de la diagonale sont pris dans les achats du meuble haut."),
    ("V7.7", "04/11/2026", "Pieds : les tubes d'aluminium et les cales sont remplacés par 2 vérins réglables encastrés sous chaque joue, à 2 du sol. Joues et dos de 85 de haut."),
    ("V7.6", "04/11/2026", "Dos en panneau rétabli : le client refusait une structure en tasseaux, pas ce panneau. Aucun tasseau au sol, sous le plateau ou à l'arrière. 10 équerres. Le dos est peint côté place libre et levé comme les joues."),
    ("V7.5", "04/11/2026", "Joues levées à 2,3 du sol sur un tube d'aluminium collé. Dos retiré : plus rien entre les joues et le plateau. 6 équerres au lieu de 17. Finition limitée aux chants avant et aux faces de la place libre. Deux dalles hydrofuges au lieu de la plaque."),
    ("V7.4", "04/11/2026", "Joues et dos en aggloméré hydrofuge peint, plateau en chêne : choix provisoire tant que la matière n'est pas tranchée. Le tableau d'achats passe dans la liste d'achats."),
    ("V7.3", "04/11/2026", "Structure refaite sur un autre principe : trois joues pleines et un dos en chêne de 18, sans ossature ni diagonale. Découpe et ordre de montage vérifiés. Place libre portée à 47,5 de large."),
    ("V7.2", "04/11/2026", "Lambourdes 45 × 70 avec écharpes, tapis anti-vibration sous la machine. Structure abandonnée : trop épaisse, et les écharpes ne s'assemblaient pas."),
    ("V7.1", "04/11/2026", "Bastaings 63 × 175 en trois portiques. Structure abandonnée : trop épaisse."),
    ("V7.0", "04/11/2026", "Conception reprise de zéro : alcôve, mesures et machine en place. L'ancien meuble bas (V6.2) reste dans les archives."),
]
ARCHIVE = "archive/sdb-meuble-v4-bas.html"
ACHATS = "sdb-meuble-achats.html"
BARRE = '<div class="vbar"><a class="back" href="index.html">← Plans</a><span class="sp"></span></div>'
CSS = """
.olibre{fill:var(--water);fill-opacity:.12;stroke:var(--water);stroke-width:.25;stroke-dasharray:1.4 .8}
.omasse{fill:var(--tile);stroke:var(--ink);stroke-width:.25}
.oequip{fill:var(--panel);stroke:var(--muted);stroke-width:.25}
.ovant{stroke:var(--tri);stroke-width:.6}
.ocarr{stroke:var(--water);stroke-width:.25;stroke-dasharray:1.4 .8}
.omel{fill:#fbfaf5;stroke:var(--ink);stroke-width:.25}.omel.cut{fill:#dedbd0;stroke-width:.35}
.otrou{fill:var(--ink);fill-opacity:.62;stroke:var(--ink);stroke-width:.25}
.opoi{fill:var(--muted);stroke:var(--ink);stroke-width:.2}
.ofil{fill:none;stroke:var(--tri);stroke-width:.35;stroke-dasharray:1.2 .8}
.otq{stroke:var(--tri);stroke-width:.3;stroke-dasharray:1.6 .9}
ol.pose li{margin:6px 0}
"""

# ------------------------------------------------------------------ dimensions
EP = M.PT               # 18 mm : plateau en chêne, panneaux en mélaminé
PANNEAU = M.PANNEAUX["D"][0]   # plateau : Weldom 82025610, chêne 200 × 60 × 18 (L et l en mm)
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
PLATEAU_P = M.PROF      # profondeur demandée : 60, contre le mur du fond
JEU_MUR = 0.3           # entre le meuble et les murs ; plateau à recouper à la mesure réelle
JEU_MACHINE = 1         # autour de la machine et sous le plateau : elle vibre sans rien toucher
JEU_FOND = 5            # entre le dos de la machine et le mur du fond (coudes des tuyaux)
TAPIS = dict(ep=1, l=60, p=54, brut=60, prix=13.50, ref="9161504", nom="Plaque anti-vibrations Noma Rub 60 × 60 × 1")

Z_MACH = TAPIS["ep"] + M.LL["h"]          # dessus de la machine, posée sur le tapis : 86
Z_DESSOUS = Z_MACH + JEU_MACHINE          # dessous du plateau : 87
Z_DESSUS = Z_DESSOUS + EP                 # dessus du plateau : 88,8

PX0, PX1 = M.X1 - PLATEAU_P, M.X1         # plateau : 174 → 234
PY0, PY1 = M.Y0 + JEU_MUR, M.Y1 - JEU_MUR # plateau : 0,3 → 114,7
MX1 = M.X1 - JEU_FOND
MX0 = MX1 - M.LL["p"]                     # façade de la machine : 176
JX0, JX1 = MX0, M.X1 - JEU_MUR            # joues : au nu de la façade, le plateau dépasse de 2 devant
JOUE_P = JX1 - JX0                        # 57,7
JZ0 = VERIN["h"]                          # bas des panneaux, hors de l'eau : 2
JOUE_H = Z_DESSOUS - JZ0                  # 85

# du nord au sud : joue nord, placard, joue du milieu, machine, joue sud
NY0, NY1 = PY0, PY0 + EP
SY1 = PY1
SY0 = SY1 - EP
MY1 = SY0 - JEU_MACHINE
MY0 = MY1 - M.LL["l"]
CY1 = MY0 - JEU_MACHINE
CY0 = CY1 - EP
BAIE = CY0 - NY1                          # largeur intérieure : 47,5
JEU_SUD = M.Y1 - MY1
JOUES = (("n", NY0, NY1), ("c", CY0, CY1), ("s", SY0, SY1))

# fond : entre les joues nord et milieu, au nu de leur arrière
DX0, DX1 = JX1 - EP, JX1                  # 231,9 → 233,7
PROF_LIBRE = DX0 - JX0                    # du plan des joues au fond : 55,9

# bas du placard au ras du bas des joues ; deux étages égaux, du dessus du bas au dessous du plateau
BZ0, BZ1 = JZ0, JZ0 + EP                  # bas : 2 → 3,8
NIV_H = (Z_DESSOUS - BZ1 - EP) / 2        # hauteur de chaque étage : 40,7
EZ0, EZ1 = BZ1 + NIV_H, BZ1 + NIV_H + EP  # étagère : 44,5 → 46,3
ETAGES = (BZ1, EZ1)                       # bas de chaque étage
EX0 = JX0 + 1                             # bas et étagère en retrait de 1 sur le plan des joues
ETAGERE_P = DX0 - EX0                     # 54,9
BAC_MAX = 0.75 * NIV_H                    # 3/4 de l'étage : 30,5
BX0, BX1 = EX0, EX0 + BAC["p"]            # bacs : au nu de l'étagère, 0,9 d'air devant le fond
BY0, BY1 = (NY1 + CY0 - BAC["l"]) / 2, (NY1 + CY0 + BAC["l"]) / 2

# porte en applique sur les joues nord et milieu, comme un meuble IKEA ; poignée à droite vue de face (au sud), charnières au nord
JEU_PORTE = 0.2                           # autour de la porte et devant les joues (charnière à régler ; de mémoire, à confirmer sur place)
PORTE_X0 = JX0 - JEU_PORTE - EP           # face avant : 174, au nu du plateau
PORTE_X1 = PORTE_X0 + EP
PORTE_Y0, PORTE_Y1 = NY0 + JEU_PORTE, CY1 - JEU_PORTE
PORTE_Z0, PORTE_Z1 = JZ0, Z_DESSOUS - JEU_PORTE
PORTE_L, PORTE_H = PORTE_Y1 - PORTE_Y0, PORTE_Z1 - PORTE_Z0   # 50,7 × 84,8
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
COL_H = M.Z_HAUT - Z_DESSUS - JEU_PORTE   # 69 : 2 mm de moins que l'écart, à recouper à la mesure réelle
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
PRISES_Z = (100, 110, 120)                # axes des 3 prises libres
PRISE_LED_Z = 146                         # axe du 4e poste, pour le transformateur des LED
COL_TROU = dict(x=230, y=4, d=2)          # passage du câble dans le plateau, caché par la colonne, au-dessus du placard
GOUL = 2                                  # goulotte du câble, et entaille de l'étagère dans l'angle arrière côté nord
ARRIVEE = dict(x=200, z=8)                # sortie du câble en bas du mur nord (relevé client) : cotes supposées, à relever sur place
LED_X = M.LED.x0                          # profil LED sous le meuble haut


def col_pt(t, n=0):
    """Point à t de la largeur de la face avant, à n derrière elle."""
    return (COL_A[0] + t * COL_L * COL_U[0] + n * COL_N[0], COL_A[1] + t * COL_L * COL_U[1] + n * COL_N[1])


COL_VIS = tuple(col_pt(t, EP / 2) for t in (0.25, 0.5, 0.75))    # vis du bas et du haut, dans le chant du panneau

GONDS_X = M.X1 - M.GONDS
BOUT_NORD = M.X1 - M.ALCOVE["nord"]
BOUT_SUD = M.X1 - M.ALCOVE["sud"]
DEVANT = MX0 - GONDS_X                    # entre la façade de la machine et le vantail ouvert à 90°
DEVANT_PORTE = PORTE_X0 - GONDS_X         # entre la porte du placard fermée et le vantail ouvert à 90°
ANGLE_VANTAIL = math.degrees(math.asin((DEVANT_PORTE - POIGNEE["saillie"]) / (POI_Y - PORTE_Y0)))   # ouverture possible, vantail à 90°
RESTE_NIV = M.Z_HAUT - Z_DESSUS           # entre le dessus du plateau et le dessous du meuble haut
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
    litres = (2 * (PY1 - PY0) * PLATEAU_P + 2 * (PY1 - PY0 + PLATEAU_P) * EP) / 1e4 * M.VERNIS["couches"] / M.VERNIS["rendement"]
    pots = sorted(M.VERNIS["pots"], key=lambda x: x["l"])
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
class Porte(M.Bloc):
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
    enc = (PX1 - M.PASSE["p"], PX1, M.ROBINET["y"] - M.PASSE["l"] / 2, M.ROBINET["y"] + M.PASSE["l"] / 2)
    o = [M.Bloc("melamine", f"joue_{k}", JX0, JX1, y0, y1, JZ0, Z_DESSOUS, groupe="meuble") for k, y0, y1 in JOUES]
    o += [M.Bloc("pied", f"verin_{k}{i}", x - VERIN["d"] / 2, x + VERIN["d"] / 2, (y0 + y1 - VERIN["d"]) / 2, (y0 + y1 + VERIN["d"]) / 2, 0, JZ0, groupe="meuble")
          for k, y0, y1 in JOUES for i, x in enumerate(VERINS_X)]
    o.append(M.Bloc("melamine", "fond", DX0, DX1, NY1, CY0, JZ0, Z_DESSOUS, groupe="meuble"))
    o.append(M.Bloc("melamine", "bas", EX0, DX0, NY1, CY0, BZ0, BZ1, groupe="meuble"))
    o.append(M.Bloc("melamine", "etagere", EX0, DX0, NY1, CY0, EZ0, EZ1, groupe="meuble", entailles=((DX0 - GOUL, DX0, NY1, NY1 + GOUL),)))
    for i, e in enumerate(ETAGES):
        o.append(M.Bloc("sac", f"bac_{i + 1}", BX0, BX1, BY0, BY1, e, e + BAC["h"], groupe="bacs"))
    o.append(M.Bloc("chene", "plateau", PX0, PX1, PY0, PY1, Z_DESSOUS, Z_DESSUS, groupe="plateau", encoche=enc))
    o.append(Porte("melamine", "porte", PORTE_X0, PORTE_X1, PORTE_Y0, PORTE_Y1, PORTE_Z0, PORTE_Z1, groupe="porte", fenetres=(contour(FENETRES[0]), contour(FENETRES[1], True))))
    o.append(M.Bloc("pied", "poignee", PORTE_X0 - POIGNEE["saillie"], PORTE_X0, POI_Y - 0.6, POI_Y + 0.6, POI_Z0, POI_Z1, groupe="porte"))
    zc = Z_DESSUS + COL_H
    o.append(Prisme("melamine", "colonne", COL_XY, Z_DESSUS, zc, groupe="colonne", decor=tuple(("idec", plaque_3d(z)) for z in PRISES_Z + (PRISE_LED_Z,))))
    o.append(M.Bloc("machine", "lave_linge", MX0, MX1, MY0, MY1, TAPIS["ep"], Z_MACH, groupe="machine"))
    o.append(M.Bloc("pied", "tapis", TX0, TX1, TY0, TY1, 0, TAPIS["ep"], groupe="machine"))
    return o


def cm(v):
    return f"{round(v + 1e-9, 1):g}".replace(".", ",")


def rect(x0, y0, x1, y1, cls):
    return f'<rect class="{cls}" x="{CO.f(x0)}" y="{CO.f(y0)}" width="{CO.f(x1 - x0)}" height="{CO.f(y1 - y0)}"/>'


def trait(x0, y0, x1, y1, cls):
    return f'<line class="{cls}" x1="{CO.f(x0)}" y1="{CO.f(y0)}" x2="{CO.f(x1)}" y2="{CO.f(y1)}"/>'


def fil(pts):
    """Tracé ouvert, sans fermer le contour."""
    return '<polyline class="ofil" points="' + " ".join(f"{CO.f(a)},{CO.f(b)}" for a, b in pts) + '"/>'


def poly_yz(pts, cls):
    return PL.poly([(y, -z) for y, z in pts], cls)


# ------------------------------------------------------------------ plan
def vue_plan():
    x_g, ep = 78, 4
    y_sud = M.SDB["p"]
    px0, px1 = M.PORTE["x0"], M.PORTE["x1"]
    lx0, ly0, lx1, ly1 = M.LAVABO
    px_, py_ = PORTE_X1, PORTE_Y0 + 0.5                # pivot approché de la porte du placard
    a = math.radians(OUVERTURE)
    ox, oy = px_ - PORTE_L * math.sin(a), py_ + PORTE_L * math.cos(a)
    o = [rect(x_g, -ep, px0, M.Y0, "omur"), rect(px1, -ep, M.X1 + ep, M.Y0, "omur"),
         rect(M.X1, -ep, M.X1 + ep, y_sud + ep, "omur"),
         rect(BOUT_SUD, M.Y1, M.X1, y_sud, "omasse"),
         rect(x_g, y_sud, M.X1 + ep, y_sud + ep, "omur"),
         rect(lx0, ly0, lx1, ly1, "oequip"), PL.text((lx0 + lx1) / 2, (ly0 + ly1) / 2 + 1, "Lavabo", "lt", "middle"),
         rect(JX0, NY1, DX0, CY0, "olibre"),
         rect(BX0, BY0, BX1, BY1, "omet"),
         PL.text((BX0 + BX1) / 2, (BY0 + BY1) / 2 - 1, "Bacs", "lt", "middle"),
         PL.text((BX0 + BX1) / 2, (BY0 + BY1) / 2 + 2.4, f'{BAC["p"]} × {BAC["l"]}', "ct", "middle"),
         rect(TX0, TY0, TX1, TY1, "omet"),
         rect(MX0, MY0, MX1, MY1, "omach"),
         PL.text((MX0 + MX1) / 2, (MY0 + MY1) / 2 - 1, "Machine", "lt", "middle"),
         PL.text((MX0 + MX1) / 2, (MY0 + MY1) / 2 + 2.4, f'{cm(M.LL["l"])} × {cm(M.LL["p"])}', "ct", "middle"),
         trait(GONDS_X, M.Y0, GONDS_X, M.PORTE["l"], "ovant"),
         f'<path class="oswing" d="M {px0} {M.Y0} A {M.PORTE["l"]} {M.PORTE["l"]} 0 0 0 {GONDS_X} {M.PORTE["l"]}"/>',
         PL.text(GONDS_X - 3, 66, "Porte d'entrée à 90°", "lt", "end"),
         trait(px_, py_, ox, oy, "ovant"),
         f'<path class="oswing" d="M {CO.f(PORTE_X0)} {CO.f(PORTE_Y1)} A {CO.f(PORTE_L)} {CO.f(PORTE_L)} 0 0 1 {CO.f(ox)} {CO.f(oy)}"/>',
         PL.text(ox + 1, oy + 4, "Porte du placard ouverte", "lt", "start")]
    for _, y0, y1 in JOUES:
        o.append(rect(JX0, y0, JX1, y1, "omel cut"))
    o.append(rect(DX0, NY1, DX1, CY0, "omel cut"))
    o.append(rect(PORTE_X0, PORTE_Y0, PORTE_X1, PORTE_Y1, "omel cut"))
    o.append(rect(PORTE_X0 - POIGNEE["saillie"], POI_Y - 0.6, PORTE_X0, POI_Y + 0.6, "opoi"))
    o.append(rect(PX0, PY0, PX1, PY1, "oplanl"))
    o += [PL.poly(COL_XY, "omel cut"), CO.etiquette(COL_C[0], COL_C[1], COL_C[0] - 10, COL_C[1] + 7, "Colonne", "end")]
    o += [PL.text(PX0 - 1.5, 112, "Plateau", "lt", "end"),
          CO.cote_h(px0, px1, -9, f'{M.PORTE["l"]} porte'), CO.cote_h(px1, M.X1, -9, f"{M.GONDS} gonds"),
          CO.cote_h(BOUT_NORD, M.X1, -15, f'{M.ALCOVE["nord"]} mur nord', ext=-4),
          CO.cote_v(NY1, CY0, M.X1 + 10, ext=M.X1 + ep), CO.cote_v(MY0, MY1, M.X1 + 10, ext=M.X1 + ep),
          CO.cote_v(PY0, PY1, M.X1 + 18, f"{cm(PY1 - PY0)} plateau", ext=M.X1 + ep),
          CO.cote_v(M.Y0, M.Y1, M.X1 + 26, f"{cm(M.Y1 - M.Y0)} fond", ext=M.X1 + ep),
          CO.cote_h(MX0, MX1, M.Y1 + 8, ext=MY1), CO.cote_h(MX1, M.X1, M.Y1 + 8, ext=MY1, place="droite"),
          CO.cote_h(PX0, PX1, M.Y1 + 18, f"{PLATEAU_P} plateau"),
          CO.cote_h(BOUT_SUD, M.X1, M.Y1 + 28, f'{M.ALCOVE["sud"]} mur sud'),
          CO.cote_h(GONDS_X, MX0, 80, ext=None)]
    return CO.svg(x_g - 2, -20, M.X1 + 32, y_sud + ep + 2, o, "Plan de l'alcôve avec le meuble, les portes et la machine")


# ------------------------------------------------------------------ élévation vue depuis la salle de bain
def vue_face():
    ep, r = 4, M.ROBINET
    t = M.TUYAUX
    o = [rect(M.Y0 - ep, -M.H - ep, M.Y0, ep, "omur"), rect(M.Y1, -M.H - ep, M.Y1 + ep, ep, "omur"),
         rect(M.Y0, -M.H - ep, M.Y1, -M.H, "omur"), rect(M.Y0, 0, M.Y1, ep, "omur"),
         trait(M.Y0, -M.CARRELAGE, M.Y1, -M.CARRELAGE, "ocarr"),
         rect(M.Y0 + 0.5, -M.Z_HAUT1, M.Y1 - 0.5, -M.Z_HAUT, "oequip"),
         PL.text((M.Y0 + M.Y1) / 2, -(M.Z_HAUT + M.Z_HAUT1) / 2, "Meuble haut", "lt", "middle"),
         rect(MY0, -Z_MACH, MY1, -TAPIS["ep"], "omach"), rect(TY0, -TAPIS["ep"], TY1, 0, "omet"),
         PL.text((MY0 + MY1) / 2, -Z_MACH / 2 - 8, "Machine", "lt", "middle"),
         f'<circle class="ocache" cx="{r["y"]}" cy="{-t["evacuation_z"]}" r="3"/>',
         f'<line class="ocache" x1="{r["y"]}" y1="{-t["arrivee_z"]}" x2="{r["y"]}" y2="{-r["z"]}"/>',
         f'<circle class="ovanne" cx="{r["y"]}" cy="{-r["z"]}" r="1.2"/>',
         CO.etiquette(r["y"], -r["z"], r["y"] + 8, -r["z"] - 4, f'Robinet à {r["z"]}')]
    for _, y0, y1 in JOUES:
        o.append(rect(y0, -Z_DESSOUS, y1, -JZ0, "omel cut"))
        o.append(rect((y0 + y1 - VERIN["d"]) / 2, -JZ0, (y0 + y1 + VERIN["d"]) / 2, 0, "omet"))
    o += [poly_yz(contour(FENETRES[1], True), "otrou"), poly_yz(contour_porte(), "omel"), poly_yz(contour(FENETRES[0]), "otrou")]
    o += [rect(NY1, -EZ1, CY0, -EZ0, "ocache"), rect(NY1, -BZ1, CY0, -BZ0, "ocache")]
    o += [rect(BY0, -(e + BAC["h"]), BY1, -e, "ocache") for e in ETAGES]
    o.append(rect(POI_Y - 0.6, -POI_Z1, POI_Y + 0.6, -POI_Z0, "opoi"))
    o.append(rect(PY0, -Z_DESSUS, PY1, -Z_DESSOUS, "oplan cut"))
    o += [rect(COL_YF, -(Z_DESSUS + COL_H), COL_B[1], -Z_DESSUS, "omel"), CO.etiquette(COL_B[1], -125, COL_B[1] + 10, -130, "Colonne")]
    o += [CO.cote_h(PORTE_Y0, PORTE_Y1, 11, ext=ep), CO.cote_h(MY0, MY1, 11, ext=ep),
          CO.cote_h(M.Y0, M.Y1, 18, f"{cm(M.Y1 - M.Y0)} fond", ext=ep),
          CO.niveaux([(Z_MACH, f"{cm(Z_MACH)} machine", M.Y0), (Z_DESSUS, f"{cm(Z_DESSUS)} plateau", M.Y0), (M.Z_HAUT, None, M.Y0),
                      (M.CARRELAGE, f"{M.CARRELAGE} carrelage", M.Y0), (M.H, f"{M.H} plafond", M.Y0)], M.Y0 - ep - 3),
          CO.cote_v(-M.Z_HAUT, -Z_DESSUS, M.Y1 - 0.6)]
    return CO.svg(-34, -M.H - ep - 2, M.Y1 + ep + 2, 22, o, "Élévation de l'alcôve vue depuis la salle de bain")


# ------------------------------------------------------------------ porte vue de face
def vue_porte():
    y0, y1 = PORTE_Y0, PORTE_Y1
    o = [trait(y0 - 6, 0, y1 + 6, 0, "ocarr"), poly_yz(contour_porte(), "omel"), poly_yz(contour(FENETRES[0]), "otrou")]
    for z in CHARN_Z:
        o.append(f'<circle class="ocache" cx="{CO.f(y0 + CUV_RIVE - CUVETTE / 2)}" cy="{CO.f(-z)}" r="{CUVETTE / 2}"/>')
    o += [rect(POI_Y - 0.6, -POI_Z1, POI_Y + 0.6, -POI_Z0, "opoi"),
                    CO.etiquette(y0 + CUV_RIVE - CUVETTE / 2, -CHARN_Z[0], y0 + 12, -CHARN_Z[0] - 5, "Charnière"),
          CO.etiquette(POI_Y, -(POI_Z0 + POI_Z1) / 2, y1 - 16, -(POI_Z0 + POI_Z1) / 2 - 5, "Poignée", "end"),
          CO.cote_h(y0, FEN_Y0, 6, ext=0, place="gauche"), CO.cote_h(FEN_Y0, FEN_Y1, 6, ext=0), CO.cote_h(FEN_Y1, y1, 6, ext=0, place="droite"),
          CO.cote_h(y0, y1, 13, ext=0),
          CO.cote_v(-PORTE_Z1, -PORTE_Z0, y0 - 12),
          CO.niveaux([(FENETRES[0][2], cm(FENETRES[0][2]), y1), (FENETRES[0][3], cm(FENETRES[0][3]), y1), (FENETRES[1][2], cm(FENETRES[1][2]), y1), (PORTE_Z1, cm(PORTE_Z1), y1)], y1 + 3, droite=True)]
    return CO.svg(y0 - 20, -PORTE_Z1 - 4, y1 + 22, 19, o, "Porte du placard vue de face")


# ------------------------------------------------------------------ coupe par le placard
def vue_placard():
    ep = 4
    z_f = [PORTE_Z0, FENETRES[0][2], FENETRES[0][3], FENETRES[1][2]]        # bois de la porte : sous chaque découpe
    o = [rect(M.X1, -Z_DESSUS - 6, M.X1 + ep, ep, "omur"), rect(PX0 - 14, 0, M.X1, ep, "omur"),
         rect(JX0, -Z_DESSOUS, JX1, -JZ0, "omel"),
         rect(EX0, -EZ1, DX0, -EZ0, "omel cut"), rect(EX0, -BZ1, DX0, -BZ0, "omel cut"), rect(DX0, -Z_DESSOUS, DX1, -JZ0, "omel cut"),
         rect(PX0, -Z_DESSUS, PX1, -Z_DESSOUS, "oplan cut")]
    for a, b in zip(z_f[::2], z_f[1::2]):
        o.append(rect(PORTE_X0, -b, PORTE_X1, -a, "omel cut"))
    o.append(rect(PORTE_X0 - POIGNEE["saillie"], -POI_Z1, PORTE_X0, -POI_Z0, "opoi"))
    for i, e in enumerate(ETAGES):
        o += [rect(BX0, -(e + BAC["h"]), BX1, -e, "olibre"),
              PL.text((BX0 + BX1) / 2, -e - BAC["h"] / 2 + 1, f'Bac {i + 1}', "lt", "middle"),
              trait(PORTE_X0, -(e + BAC_MAX), JX1, -(e + BAC_MAX), "otq"),
              CO.cote_v(-(e + BAC["h"]), -e, BX1 - 4, cm(BAC["h"]))]
    xg = DX0 - GOUL / 2
    o += [fil([(ARRIVEE["x"], -ARRIVEE["z"]), (xg, -ARRIVEE["z"]), (xg, -Z_DESSUS)]),
          CO.etiquette(ARRIVEE["x"], -ARRIVEE["z"], ARRIVEE["x"] - 3, -ARRIVEE["z"], "Sortie du câble", "end")]
    o += [CO.cote_h(JX0, DX0, 11, cm(PROF_LIBRE), ext=ep), CO.cote_h(PX0, PX1, 18, f"{PLATEAU_P} plateau", ext=ep),
          CO.niveaux([(BZ1, f"{cm(BZ1)} bas", M.X1), (ETAGES[0] + BAC_MAX, f"{cm(ETAGES[0] + BAC_MAX)} 3/4", M.X1), (EZ0, f"{cm(EZ0)} étagère", M.X1), (EZ1, f"{cm(EZ1)}", M.X1),
                      (EZ1 + BAC_MAX, f"{cm(EZ1 + BAC_MAX)} 3/4", M.X1), (Z_DESSOUS, f"{cm(Z_DESSOUS)} plateau", M.X1)], M.X1 + ep + 3, droite=True)]
    return CO.svg(PX0 - 16, -Z_DESSUS - 8, M.X1 + ep + 28, 22, o, "Coupe par le placard, le mur du fond à droite")


# ------------------------------------------------------------------ colonne vue de face
def vue_colonne():
    d = PRISE["plaque"] / 2
    zc = Z_DESSUS + COL_H
    u0, u1 = 0, COL_L
    uc = COL_L / 2
    o = [rect(u0 - 10, -M.Z_HAUT - 6, u1 + 10, -M.Z_HAUT, "oequip"), PL.text(uc, -M.Z_HAUT - 2, "Meuble haut", "lt", "middle"),
         rect(u0 - 10, -Z_DESSUS, u1 + 10, -Z_DESSOUS, "oplan cut"),
         rect(u0, -zc, u1, -Z_DESSUS, "omel")]
    for z in PRISES_Z + (PRISE_LED_Z,):
        o += [rect(uc - d, -z - d, uc + d, -z + d, "omel"), f'<circle class="ocache" cx="{CO.f(uc)}" cy="{CO.f(-z)}" r="2"/>']
    o += [fil([(uc, -PRISE_LED_Z), (uc, -PRISE_LED_Z - d - 1), (u0 + 1, -PRISE_LED_Z - d - 1), (u0 + 1, -M.Z_HAUT + 0.6), (u0 - 10, -M.Z_HAUT + 0.6)]),
          CO.etiquette(u0 + 1, -PRISE_LED_Z - 7, u0 - 8, -PRISE_LED_Z - 3, "Fil des LED", "end"),
          fil([(uc + 3, -Z_DESSOUS + 8), (uc + 3, -PRISES_Z[0])]),
          CO.etiquette(uc + 3, -Z_DESSOUS + 5, u0 - 8, -Z_DESSOUS + 5, "Alimentation", "end"),
          CO.cote_h(u0, u1, -Z_DESSOUS + 14, cm(COL_L), ext=-Z_DESSUS),
          CO.cote_v(-zc, -Z_DESSUS, u0 - 14, cm(COL_H)),
          CO.niveaux([(z, cm(z), u1) for z in (Z_DESSUS,) + PRISES_Z + (PRISE_LED_Z, M.Z_HAUT)], u1 + 13, droite=True)]
    return CO.svg(u0 - 34, -M.Z_HAUT - 8, u1 + 28, -Z_DESSOUS + 20, o, "Colonne de prises vue de face")


def vue_colonne_dessus():
    x_m, y_m = M.X1 + 3, COL_B[1] + 5
    b0, b1 = col_pt(0.5 - BOITE["d"] / 2 / COL_L), col_pt(0.5 + BOITE["d"] / 2 / COL_L)
    n = BOITE["prof"]
    boite = [b0, b1, (b1[0] + n * COL_N[0], b1[1] + n * COL_N[1]), (b0[0] + n * COL_N[0], b0[1] + n * COL_N[1])]
    p = PRISE["plaque"] / 2 / COL_L
    o = [rect(COL_A[0] - 5, -3, x_m, M.Y0, "omur"), rect(M.X1, M.Y0, x_m, y_m, "omur"),
         PL.poly(COL_XY, "omel cut"), PL.poly(boite, "ocache"),
         trait(*col_pt(0.5 - p), *col_pt(0.5 + p), "ovant"),
         f'<circle class="pt" cx="{CO.f(COL_TROU["x"])}" cy="{CO.f(COL_TROU["y"])}" r="{COL_TROU["d"] / 2}"/>',
         PL.text(COL_C[0] - 5, COL_C[1] + 3, "Prises", "lt", "end"),
         CO.cote_h(COL_A[0], M.X1 - JEU_MUR, y_m + 2, cm(COL_JAMBE), ext=None),
         CO.cote_v(M.Y0 + JEU_MUR, COL_B[1], COL_A[0] - 14, cm(COL_JAMBE), ext=None)]
    return CO.svg(COL_A[0] - 28, -6, x_m + 28, y_m + 8, o, "Colonne vue de dessus, dans l'angle")


# ------------------------------------------------------------------ joue vue de côté
def vue_joue():
    ep = 4
    o = [rect(M.X1, -Z_DESSUS - 6, M.X1 + ep, ep, "omur"), rect(PX0 - 6, 0, M.X1, ep, "omur"),
         rect(JX0, -Z_DESSOUS, JX1, -JZ0, "omel"),
         rect(PX0, -Z_DESSUS, PX1, -Z_DESSOUS, "oplan cut"),
         rect(VERINS_X[0] - VERIN["d"] / 2, -JZ0, VERINS_X[0] + VERIN["d"] / 2, 0, "omet"),
         rect(VERINS_X[1] - VERIN["d"] / 2, -JZ0, VERINS_X[1] + VERIN["d"] / 2, 0, "omet"),
         PL.text((JX0 + JX1) / 2, -Z_DESSOUS / 2, f"Joue {cm(JOUE_H)} × {cm(JOUE_P)}", "lt", "middle"),
         CO.etiquette(VERINS_X[0], -1, VERINS_X[0] + 7, -12, "Vérin"),
         CO.cote_h(PX0, JX0, 11, ext=ep, place="gauche"), CO.cote_h(JX0, JX1, 11, ext=ep),
         CO.cote_h(PX0, PX1, 18, f"{PLATEAU_P} plateau", ext=ep),
         CO.cote_v(-Z_DESSOUS, -JZ0, JX0 - 3, cm(JOUE_H)),
         CO.niveaux([(Z_DESSOUS, f"{cm(Z_DESSOUS)} dessous", M.X1), (Z_DESSUS, f"{cm(Z_DESSUS)} dessus", M.X1)],
                    M.X1 + ep + 3, droite=True)]
    for x in EQUERRES_X:      # équerres sous le plateau
        o.append(rect(x - 1.75, -Z_DESSOUS, x + 1.75, -Z_DESSOUS + 5, "omet"))
    return CO.svg(PX0 - 16, -Z_DESSUS - 8, M.X1 + ep + 28, 22, o, "Joue vue de côté")


# ------------------------------------------------------------------ coupe par la machine
def vue_coupe():
    ep, r, t = 4, M.ROBINET, M.TUYAUX
    hx0 = M.X1 - 45
    x_g = GONDS_X - 12
    o = [rect(M.X1, -M.H - ep, M.X1 + ep, ep, "omur"), rect(x_g, -M.H - ep, M.X1, -M.H, "omur"),
         rect(x_g, 0, M.X1, ep, "omur"),
         trait(M.X1, -M.CARRELAGE, M.X1 + ep, -M.CARRELAGE, "ocarr"),
         trait(GONDS_X, 0, GONDS_X, -204, "ovant"), PL.text(GONDS_X - 1.5, -196, "Vantail", "lt", "end"),
         rect(hx0, -M.Z_HAUT1, M.X1, -M.Z_HAUT, "oequip"),
         PL.text((hx0 + M.X1) / 2, -(M.Z_HAUT + M.Z_HAUT1) / 2, "Meuble haut", "lt", "middle"),
         rect(TX0, -TAPIS["ep"], TX1, 0, "omet"),
         rect(MX0, -Z_MACH, MX1, -TAPIS["ep"], "omach cut"),
         PL.text((MX0 + MX1) / 2, -Z_MACH / 2, "Machine", "lt", "middle"),
         rect(PX0, -Z_DESSUS, PX1, -Z_DESSOUS, "oplan cut"),
         rect(M.X1 - 4, -t["evacuation_z"] - 3, M.X1, -t["evacuation_z"] + 3, "otuy"),
         trait(M.X1 - 1, -t["arrivee_z"], M.X1 - 1, -r["z"], "ocache"),
         f'<circle class="ovanne" cx="{M.X1 - 1}" cy="{-r["z"]}" r="1.2"/>',
         CO.cote_h(GONDS_X, MX0, 11, ext=ep), CO.cote_h(MX0, MX1, 11, ext=ep), CO.cote_h(MX1, M.X1, 11, ext=ep),
         CO.cote_h(GONDS_X, M.X1, 18, f"{M.GONDS} gonds", ext=ep),
         CO.niveaux([(t["evacuation_z"], f'{t["evacuation_z"]} siphon', M.X1), (t["arrivee_z"], f'{t["arrivee_z"]} arrivée', M.X1),
                     (Z_DESSUS, f"{cm(Z_DESSUS)} plateau", M.X1), (r["z"], f'{r["z"]} robinet', M.X1), (M.Z_HAUT, None, M.X1),
                     (M.CARRELAGE, f"{M.CARRELAGE} carrelage", M.X1), (M.H, f"{M.H} plafond", M.X1)],
                    M.X1 + ep + 3, droite=True)]
    return CO.svg(x_g - 8, -M.H - ep - 2, M.X1 + ep + 26, 22, o, "Coupe par la machine, le mur du fond à droite")


# ------------------------------------------------------------------ textes
def structure():
    t = tenue()
    li = "".join(f'<tr><td class="mono">{r}</td><td>{n}</td><td class="num">{q}</td><td class="num">{cm(lg)}</td><td class="num">{cm(la)}</td><td class="num">{cm(EP)}</td></tr>'
                 for r, n, q, lg, la in PIECES_DEBIT)
    ta = "".join(f'<li>Tablette {k + 1}, {tb["L"]} × {tb["l"]} : {" + ".join(f"{r} ({cm(lg)})" for r, lg, _ in d)}</li>' for k, (tb, d) in enumerate(decoupe()))
    eq = "".join(f"<li>{escape(o)} : {n}</li>" for o, n in EQUERRES)
    return f"""<h2 id="structure">Structure</h2>
<p><b>Trois joues pleines</b> de {cm(EP)} debout autour de la machine, un <b>fond</b>, un <b>bas</b> et une <b>étagère</b> entre les joues nord et milieu, le <b>plateau</b> posé directement sur le tout. Rien n'est vissé au mur. Joues, fond, bas, étagère et porte en mélaminé blanc, plateau en chêne.</p>
<ul>
<li><b>Devant-derrière.</b> Une joue est un panneau plein : elle ne peut pas se déformer dans son plan. Le mur du fond arrête le recul.</li>
<li><b>Nord-sud.</b> Le fond empêche le placard de se déformer : vissé aux joues nord et milieu, il fait un U qui tient debout seul. Le plateau y relie la joue sud, et il est pris entre les murs, à {cm(JEU_MUR)} de chaque côté.</li>
<li><b>Devant la machine.</b> Les joues s'arrêtent au nu de sa façade : sa porte passe devant elles. Le plateau dépasse de {cm(JX0 - PX0)}.</li>
<li><b>Derrière la machine.</b> Rien ne passe : les {JEU_FOND} restent libres pour les tuyaux, et une encoche de {M.PASSE["l"]} × {M.PASSE["p"]} à {cm(M.ROBINET["y"])} du mur nord laisse monter l'arrivée d'eau au robinet.</li>
<li><b>Tapis anti-vibration.</b> {escape(TAPIS["nom"])} recoupée à {TAPIS["p"]} de profondeur. Elle monte la machine de {cm(TAPIS["ep"])}, et ses {TAPIS["l"]} de large entrent entre les joues.</li>
</ul>
<h3 id="placard">Placard</h3>
{CO.figure("f-placard", "Coupe par le placard", vue_placard(), f"Le mur du fond à droite. En pointillé, les 3/4 de chaque étage : les bacs restent dessous, les découpes de la porte partent de là. En tirets rouges, le câble de la colonne, le long de la joue nord ; sa sortie est dessinée à titre d'exemple, à relever.")}
<ul>
<li><b>Étages.</b> L'étagère coupe la hauteur en deux étages égaux de {cm(NIV_H)} : du bas à l'étagère, puis de l'étagère au plateau.</li>
<li><b>Bas.</b> {cm(BAIE)} × {cm(ETAGERE_P)}, à {cm(BZ0)} du sol comme les joues. Le bac du bas pose dessus, rien ne touche le sol sauf les vérins.</li>
<li><b>Limite des bacs.</b> 3/4 de {cm(NIV_H)}, soit {cm(BAC_MAX)} de haut au maximum.</li>
<li><b>Bacs.</b> Deux <a href="https://www.ikea.com/fr/fr/p/slibb-panier-a-linge-blanc-70612723/">paniers IKEA SLIBB</a> de {BAC["litres"]} L, {BAC["p"]} × {BAC["l"]} × {BAC["h"]}, en plastique souple avec 4 poignées. Ils laissent {cm(BY0 - NY1)} de chaque côté et {cm(DX0 - BX1)} devant le fond, et ils montent à {cm(BAC["h"] / NIV_H * 100)} % de l'étage.</li>
<li><b>Étagère.</b> Mêmes dimensions que le bas. Les deux sont en retrait de {cm(EX0 - JX0)} sur le plan des joues, pour que la porte ferme sans y toucher.</li>
<li><b>Fond.</b> {cm(JOUE_H)} × {cm(BAIE)}, levé à {cm(JZ0)} du sol comme les joues, entre elles et au nu de leur arrière.</li>
<li><b>Assemblage.</b> {VIS_PANNEAU} vis 4 × 40 à chaque bout du fond, du bas et de l'étagère, à travers les joues, avant perçage Ø 2,5 et tête fraisée : ces têtes restent cachées, contre le mur côté nord et contre la machine côté milieu. {VIS_PANNEAU} vis de plus à travers le fond dans l'arrière du bas et de l'étagère.</li>
</ul>
<h3 id="porte">Porte</h3>
{CO.figure("f-porte", "Porte vue de face", vue_porte(), f"Le nord à gauche. Les charnières côté mur, la poignée côté machine.")}
<ul>
<li><b>Dimensions.</b> {cm(PORTE_H)} × {cm(PORTE_L)}, en applique devant les joues nord et milieu, comme un meuble IKEA, avec {cm(JEU_PORTE)} de jeu autour. Sa face avant arrive au nu du plateau.</li>
<li><b>Découpes en U.</b> Une par étage, de {cm(FEN_L)} de large et {cm(FEN_H)} de haut, à fond arrondi. Le point le plus bas est à 3/4 de l'étage : à {cm(FENETRES[0][2])} et à {cm(FENETRES[1][2])} du sol. On jette le linge porte fermée, il tombe dans le bac placé dessous.</li>
<li><b>En haut.</b> La découpe est une encoche ouverte sur le bord de la porte : plus de bois au-dessus, et il reste 2 cornes de {MONTANT} × {cm(FEN_H)}. C'est le point fragile de la porte, à ne pas prendre pour attraper.</li>
<li><b>En bas.</b> La découpe reste fermée : l'ouvrir vers le haut couperait la porte en deux. Il reste {cm(EZ0 - FENETRES[0][3])} entre son haut et le dessous de l'étagère.</li>
<li><b>Bois gardé.</b> {MONTANT} de chaque côté des découpes, et {cm(FENETRES[1][2] - FENETRES[0][3])} entre les deux.</li>
<li><b>Découpe.</b> Fond arrondi à {cm(FEN_R)}, angles hauts de la découpe fermée à {cm(FEN_RH)} : percer un trou dans chaque angle fermé, couper à la scie sauteuse, adhésif de masquage sur le tracé. Plaquer le chant sur tout le tour pour que rien n'accroche.</li>
<li><b>Charnières.</b> 2 <a href="https://www.ikea.com/fr/fr/p/utrusta-charn-a-amort-integre-cuisine-80524882/">IKEA UTRUSTA {CHARNIERE["angle"]}°</a> amorties, côté mur nord, à {CHARN_Z[0]} et {CHARN_Z[1]} du sol. La haute reste sous la découpe. Cuvette Ø {cm(CUVETTE * 10)} mm à percer dans la porte, plaque vissée sur la joue nord. Cotes de perçage à reprendre sur la notice IKEA avant de percer : les caissons METOD sont percés d'usine, pas nos joues.</li>
<li><b>Poignée.</b> <a href="https://www.ikea.com/fr/fr/p/billsbro-poignee-blanc-50334303/">IKEA BILLSBRO blanc</a> de {POIGNEE["L"]}, à droite, dans le montant côté machine, entre les deux découpes, de {POI_Z0} à {POI_Z1} du sol. Elle convient aux portes de 16 à 19 mm. Le lot en contient 2, une seule sert.</li>
<li><b>Ouverture.</b> Porte d'entrée fermée, la porte du placard s'ouvre à environ {OUVERTURE}°, estimation à vérifier sur place : la poignée arrive contre la porte d'entrée. Les bacs sortent alors tout droit. <b>Porte d'entrée ouverte à 90°, elle ne s'ouvre que d'environ {ANGLE_VANTAIL:.0f}°</b> : le vantail n'est qu'à {cm(DEVANT_PORTE)} devant elle. Il faut donc fermer la porte d'entrée pour sortir un bac, pas pour jeter du linge.</li>
<li><b>Porte de la machine.</b> Elle s'ouvre vers le placard, et la poignée dépasse maintenant de {cm(JX0 - PORTE_X0 + POIGNEE["saillie"])} devant les joues. Son angle maximal n'a pas été relevé : à vérifier avant de percer pour la poignée.</li>
</ul>
<h3 id="pieds">Pieds</h3>
<p>Le mélaminé ne touche jamais le sol. Sous chaque joue, <b>{VERIN["n"]} vérins réglables</b> encastrés dans le chant du bas, à {cm(VERINS_X[0] - JX0)} de chaque bord. Le fond, le bas et la porte restent suspendus, sans pied.</p>
<ul>
<li><b>Hauteur.</b> Le bas des joues est à {cm(JZ0)} du sol. Le vérin se règle de {cm(VERIN["cmin"])} à {cm(VERIN["cmax"])}, ce qui rattrape aussi un sol qui n'est pas droit.</li>
<li><b>Étanchéité.</b> Le trou de chaque vérin est garni de colle MS. Le chant du bas des joues, du fond et de la porte en est enduit : le mélaminé n'est pas hydrofuge, et son aggloméré gonfle à l'eau.</li>
<li><b>Écoulement.</b> Seuls les embouts plastique touchent le sol : l'eau et la serpillère passent dessous. On ne pose pas de joint au pied, il retiendrait l'eau.</li>
<li><b>Point à tester.</b> Le trou de {cm(VERIN["perce"] * 10)} mm laisse {cm((EP - VERIN["perce"]) / 2 * 10)} mm d'aggloméré de chaque côté : faire un essai sur une chute de tablette avant de percer les joues.</li>
</ul>
<h3>Joue</h3>
{CO.figure("f-joue", "Joue vue de côté", vue_joue(), f"Le mur du fond à droite. Deux équerres sous le plateau. Le bas de la joue est à {cm(JZ0)} du sol.")}
<h3 id="finition">Finition</h3>
<p>Le mélaminé ne se peint pas. Chant blanc thermocollant sur tout ce qui se voit : l'avant des 3 joues, le tour de la porte, le tour des 2 découpes et l'avant du bas et de l'étagère, soit {cm(chant_vu() / 100)} m. Le plateau, lui, reçoit {M.VERNIS["couches"]} couches de vernis sur toutes ses faces.</p>
<h3>Pièces</h3>
<div class="scroll"><table><thead><tr><th>Rep.</th><th>Pièce</th><th class="num">Qté</th><th class="num">Longueur</th><th class="num">Largeur</th><th class="num">Ép.</th></tr></thead><tbody>{li}</tbody></table></div>
<p><b>A, le plateau</b> : une tablette de chêne de {cm(PANNEAU_L)} × {cm(PANNEAU_P)}. <b>B à F</b> : trois tablettes de mélaminé blanc, les mêmes que le meuble haut :</p>
<ul>{ta}</ul>
<p><b>Pieds</b> : {VERIN["n"] * len(JOUES)} vérins.</p>
<h3>Montage</h3>
<ol class="pose">
<li><b>Mesurer l'alcôve</b> devant et au fond. Recouper le plateau à la plus petite mesure, moins {cm(2 * JEU_MUR)} : les murs ne sont jamais parfaitement droits. Faire l'encoche et le trou de la colonne, vernir.</li>
<li><b>Couper les panneaux</b> à la scie circulaire avec rail, la face visible dessous, puis plaquer les chants visibles.</li>
<li><b>Percer et découper la porte</b> : les 2 découpes, leur chant, les 2 cuvettes, les trous de la poignée. Visser la poignée et les charnières sur la porte.</li>
<li><b>Poser les vérins.</b> Faire un essai sur une chute. Percer Ø {cm(VERIN["perce"] * 10)} bien droit dans le chant du bas de chaque joue, garnir le trou de colle MS, enfoncer le vérin. Enduire de colle les chants du bas des joues, du fond et de la porte. Laisser prendre selon la cartouche.</li>
<li><b>À plat, sur les joues</b> : visser les équerres sous le plateau, en 4 × 16, à {cm(EQUERRES_X[0] - JX0)} de chaque bord, ras du haut, et les plaques de charnière sur la joue nord, en face des cuvettes.</li>
<li><b>Pour le câble de la colonne</b> : percer la joue nord en face de la sortie relevée sur le mur, et entailler l'étagère de {GOUL} × {GOUL} dans son angle arrière côté nord.</li>
<li><b>Assembler le U hors de l'alcôve</b> : le fond entre les joues nord et milieu, au nu du haut et de l'arrière, puis le bas au ras du bas des joues, puis l'étagère, posée sur deux cales de {cm(NIV_H)} sur le bas. {VIS_PANNEAU} vis 4 × 40 à chaque bout, à travers les joues, avant perçage, puis {VIS_PANNEAU} vis à travers le fond dans le bas et dans l'étagère. Le U tient debout seul.</li>
<li><b>Pousser le U dans l'alcôve</b>, puis dresser la joue sud à sa place et la tenir debout.</li>
<li><b>Glisser le plateau par l'avant</b> sur les joues et le fond, jusqu'au mur du fond : l'encoche vient autour du tuyau. Vérifier le niveau, régler les vérins.</li>
<li><b>Visser les équerres dans le plateau</b> par en dessous, en 4 × 16. La machine n'est pas encore là : tout est accessible. Les vis ne traversent pas le plateau.</li>
<li><b>Bloquer les pieds</b> : un point de colle MS autour de chaque embout de la joue sud, pour qu'elle ne glisse pas vers la machine. <b>Silicone</b> entre le plateau et les murs.</li>
<li><b>Clipser la porte</b> sur ses plaques, en la tenant par les côtés et pas par les cornes du haut, régler les charnières pour un jeu égal partout, et rentrer les bacs.</li>
<li><b>Poser le tapis</b> et rentrer la machine par l'avant, puis raccorder. Ouvrir sa porte à fond pour vérifier qu'elle ne bute pas sur la poignée.</li>
</ol>
<p>Les {N_EQUERRES} équerres :</p>
<ul>{eq}</ul>
<h3>Tenue</h3>
<div class="scroll"><table><thead><tr><th>Contrôle</th><th class="num">Valeur</th></tr></thead><tbody>
<tr><td>Flèche du plateau sur la machine, 100 kg au milieu</td><td class="num">{cm(t["fleche"])} mm</td></tr>
<tr><td>Contrainte dans le plateau, même charge</td><td class="num">{cm(t["contrainte"])} MPa</td></tr>
<tr><td>Flèche de l'étagère, {LINGE} kg de linge répartis</td><td class="num">{cm(t["fleche_e"])} mm</td></tr>
<tr><td>Marge au basculement, 100 kg sur le bord avant</td><td class="num">× {cm(t["marge"])}</td></tr>
</tbody></table></div>
<p class="note">{N_EQUERRES} équerres suffisent parce qu'elles ne portent pas : le plateau pose à plat sur les joues. Ordres de grandeur : chêne à {E_CHENE / 1e9:.0f} GPa et {RHO_CHENE} kg/m³, aggloméré à {E_AGGLO / 1e9:g} GPa et {RHO_AGGLO} kg/m³, valeurs courantes non mesurées. Les vis dans le chant de l'aggloméré ne sont pas calculées : à éprouver à la main avant de rentrer la machine. Masse du meuble ≈ {t["masse"]:.0f} kg, dont ≈ {t["porte"]:.1f} kg pour la porte.</p>
<h3>Achats</h3>
<p>Le meuble bas entier coûte <b>{PL.euros(total())}</b> : plateau, tablettes, chant, charnières, poignées, 2 bacs, 4 prises et leurs boîtes, vérins, colle, vernis, tapis, équerres, vis et silicone. Les vis 4 × 40 sont prises dans les achats du meuble haut, le kit LED aussi. Le câble, la goulotte et l'électricien ne sont pas comptés. Le détail est dans <a href="{ACHATS}#bas">la liste d'achats</a>.</p>"""


def colonne():
    z = [cm(x) for x in PRISES_Z]
    return f"""<h2 id="colonne">Colonne de prises</h2>
<p>Un seul panneau de mélaminé qui coupe l'angle du mur du fond et du mur nord à 45°, posé sur le plateau et vissé au meuble haut. Rien n'est percé dans le carrelage.</p>
{CO.figure("f-colonne", "Colonne vue de face", vue_colonne(), "Vue perpendiculairement au panneau. Le fil des LED et l'alimentation, en tirets rouges, passent derrière.")}
{CO.figure("f-colonne-dessus", "Colonne vue de dessus", vue_colonne_dessus(), f"Dans l'angle. En tirets, la boîte de {cm(BOITE['d'] * 10)} × {cm(BOITE['prof'] * 10)} mm, qui tient derrière le panneau. Le point marque le trou du plateau.")}
<ul>
<li><b>Panneau.</b> {cm(COL_L)} de large et {cm(COL_H)} de haut, chants longs biseautés à 45° à la scie circulaire. Il prend {cm(COL_JAMBE)} sur chaque mur, et les murs ferment le triangle. Il sort de la chute de la tablette du fond.</li>
<li><b>Prises.</b> 3 prises libres sur la face en diagonale, à {z[0]}, {z[1]} et {z[2]} du sol. Elles regardent vers la pièce et restent à {cm(M.ROBINET["y"] - COL_B[1])} du robinet.</li>
<li><b>LED.</b> Le kit se branche sur un transformateur. Il a son propre poste, à {PRISE_LED_Z} du sol, pour que les 3 autres restent libres. Son fil entre par un trou de Ø 1 juste au-dessus, monte derrière le panneau, sort par une encoche en haut côté mur nord, et file sous le meuble haut jusqu'au profil LED : ≈ {COL_C[0] - LED_X + M.Z_HAUT - PRISE_LED_Z:.0f} cm. Longueur du fil du kit et présence de l'interrupteur à vérifier sur la boîte : la fiche lue est celle d'une référence voisine.</li>
<li><b>Alimentation.</b> Le courant arrive en bas du mur nord, derrière la joue nord. Le câble traverse la joue, longe sa face intérieure en goulotte jusqu'à l'angle arrière, passe par une entaille de {GOUL} × {GOUL} dans l'étagère et par un trou Ø {cm(COL_TROU["d"] * 10)} mm dans le plateau, caché par la colonne. Le circuit, protégé en 30 mA, et le raccordement sont pour l'électricien. La machine garde sa prise à part, sur son circuit de 20 A.</li>
<li><b>À relever.</b> La hauteur de la sortie et sa distance au mur du fond. Dessin fait avec {ARRIVEE["z"]} du sol et {cm(M.X1 - ARRIVEE["x"])} du fond, à titre d'exemple. Le trajet reste valable si la sortie est au-dessus du bas du placard, à plus de {cm(BZ1)} du sol. Si une boîte dépasse du mur de plus de {cm(JEU_MUR)}, il faut aussi la dégager dans la joue.</li>
<li><b>Point à tester.</b> Les griffes de la boîte Batibox sont prévues pour les cloisons : faire un essai sur une chute de 18 avant de percer le panneau à Ø {cm(BOITE["d"] * 10)} mm.</li>
<li><b>Tenue.</b> Le panneau n'est tenu qu'à ses deux bouts, par {len(COL_VIS)} vis à chacun. Un cordon qu'on tire ne le sollicite pas beaucoup, mais à éprouver à la main avant de brancher.</li>
</ul>
<h3>Pose de la colonne</h3>
<ol class="pose">
<li><b>Avant de vernir le plateau</b> : percer son trou à {cm(M.X1 - COL_TROU["x"])} du mur du fond et {cm(COL_TROU["y"])} du mur nord. Avant le montage du placard : percer la joue nord en face de la sortie du câble, entailler l'étagère.</li>
<li><b>À l'atelier</b> : recouper le panneau à la mesure réelle entre plateau et meuble haut, moins 2 mm, couper les biseaux, percer les 4 trous Ø {cm(BOITE["d"] * 10)}, le trou du fil et l'encoche du haut.</li>
<li><b>Une fois les deux meubles posés</b> : tirer le câble, glisser le panneau dans l'angle, visser {len(COL_VIS)} vis 4 × 40 à travers le plateau dans son chant depuis le placard, bacs sortis, et {len(COL_VIS)} vis à travers le dessous du meuble haut, depuis l'intérieur, étagère retirée. Avant perçage Ø 2,5 au milieu du chant.</li>
<li><b>Électricien</b> : poser les boîtes et les prises, courant coupé.</li>
<li><b>Fil des LED</b> : passer le fil, le fixer sous le meuble haut avec des clips adhésifs, brancher le transformateur.</li>
</ol>
"""


def mesures():
    relevees = [
        ("Plafond", f"{M.H}", "Confirmé par le client"),
        ("Mur du fond, de nord à sud", cm(M.Y1 - M.Y0), "Relevé client"),
        ("Mur de retour nord", f'{M.ALCOVE["nord"]}', "Relevé client"),
        ("Mur de retour sud", f'{M.ALCOVE["sud"]}', "Relevé client"),
        ("Gonds de la porte d'entrée, depuis le mur du fond", f"{M.GONDS}", "Relevé client"),
        ("Largeur de la porte d'entrée", f'{M.PORTE["l"]}', "Porte standard, d'après le client"),
        ("Chambranle, saillie sur le mur nord", cm(M.CHAMBRANLE), "Relevé client"),
        ("Carrelage, hauteur", f"{M.CARRELAGE}", "Relevé client"),
        ("Machine, largeur × profondeur × hauteur", f'{cm(M.LL["l"])} × {cm(M.LL["p"])} × {cm(M.LL["h"])}', "Relevé client"),
    ]
    reprises = [
        ("Machine, côté", "à droite, au sud", "Choix du client depuis la V3.8"),
        ("Porte de la machine", "s'ouvre à gauche", "Validé par le client ; débattement non relevé"),
        ("Machine, jeu derrière", cm(JEU_FOND), "Reprise de la V6.2, pour les coudes des tuyaux"),
        ("Machine, distance au mur sud", cm(JEU_SUD), f"Joue de {cm(EP)} + {JEU_MACHINE} de jeu + {cm(JEU_MUR)} au mur"),
        ("Tapis sous la machine, épaisseur", cm(TAPIS["ep"]), "Plaque Noma Rub, épaisseur de la fiche Weldom"),
        ("Plateau, profondeur", f"{PLATEAU_P}", "Demande du client"),
        ("Siphon d'évacuation, à " + cm(M.ROBINET["y"]) + " du mur nord", f'{M.TUYAUX["evacuation_z"]} de haut', "Position de la V6.0, à vérifier sur place"),
        ("Arrivée d'eau, même axe", f'{M.TUYAUX["arrivee_z"]} de haut', "Position de la V6.0, à vérifier sur place"),
        ("Robinet d'arrêt, même axe", f'{M.ROBINET["z"]} de haut', "Position de la V5.7, à recaler sur le nouveau plateau"),
        ("Dessous du meuble haut", f"{M.Z_HAUT}", f"Page du meuble haut {M.VERSION}"),
    ]

    def table(lignes):
        corps = "".join(f'<tr><td>{escape(n)}</td><td class="num">{escape(v)}</td><td>{escape(s)}</td></tr>' for n, v, s in lignes)
        return (f'<div class="scroll"><table><thead><tr><th>Mesure</th><th class="num">Valeur</th><th>Origine</th></tr></thead>'
                f'<tbody>{corps}</tbody></table></div>')
    deduites = [
        ("Placard, largeur entre les joues nord et milieu", cm(BAIE)),
        ("Placard, profondeur des joues au fond", cm(PROF_LIBRE)),
        ("Bas des joues au-dessus du sol", cm(JZ0)),
        ("Chaque étage, hauteur", cm(NIV_H)),
        ("Entre la porte du placard et le vantail ouvert", cm(DEVANT_PORTE)),
        ("Entre le dessus du plateau et le dessous du meuble haut", cm(RESTE_NIV)),
    ]
    li = "".join(f"<li>{escape(n)} : <b>{v}</b></li>" for n, v in deduites)
    return f"""<h2 id="mesures">Mesures</h2>
<p>Toutes les cotes sont en cm.</p>
<h3>Relevées</h3>
{table(relevees)}
<h3>Reprises des versions précédentes</h3>
{table(reprises)}
<h3>Ce qu'il reste</h3>
<ul>{li}</ul>
<p class="note">À confirmer : le mur de retour nord s'arrête à {M.ALCOVE["nord"]} du fond et les gonds sont à {M.GONDS}. Ces {M.GONDS - M.ALCOVE["nord"]} cm d'écart ne sont pas relevés ; le plan les dessine en mur continu.</p>"""


def page():
    lignes = "".join(f'<tr><td class="mono">{v}</td><td class="mono">{d}</td><td>{escape(x)}</td></tr>' for v, d, x in CHANGEMENTS)
    iso = MO.dessin(blocs(), murs=True, reperes=False, carrelage=M.CARRELAGE, titre="Meuble bas dans l'alcôve, porte fermée")
    dedans = MO.dessin([b for b in blocs() if b.groupe != "porte"], murs=True, reperes=False, carrelage=M.CARRELAGE, titre="Meuble bas sans la porte")
    eclate = MO.dessin([b for b in blocs() if b.groupe != "colonne"], reperes=False, decale={"plateau": (0, 0, 35), "machine": (-80, 75, 0), "porte": (-40, 0, 0)}, titre="Vue éclatée")
    plan_ = CO.figure("f-plan", "Plan", vue_plan(), f"Le nord en haut. La machine est à {cm(JEU_FOND)} du mur du fond et à {cm(JEU_SUD)} du mur sud. Panneaux en coupe, contour du plateau en tirets. La porte d'entrée, ouverte à 90°, passe à {cm(DEVANT_PORTE)} de la porte du placard fermée.")
    face = CO.figure("f-face", "Élévation, vue depuis la salle de bain", vue_face(), "Le nord à gauche, le sud à droite. En tirets, le bas, l'étagère, les bacs et les réseaux derrière la machine. Sous chaque joue, ses vérins.")
    coupe = CO.figure("f-coupe", "Coupe par la machine", vue_coupe(), "Le mur du fond à droite, vu vers le nord.")
    corps = f"""<div class="kicker">Salle de bain · alcôve {cm(M.Y1 - M.Y0)} × {M.ALCOVE["nord"]} à {M.ALCOVE["sud"]} · meuble bas · {VERSION}</div>
<h1>Meuble bas</h1>
<p class="pitch">Trois joues et un fond en mélaminé blanc de {cm(EP)}, levés sur des vérins, portent directement un plateau en chêne de {PLATEAU_P} de profondeur sur toute la longueur, sans aucune fixation au mur. À côté de la machine, un placard à deux étages reçoit deux bacs à linge, derrière une porte découpée en U pour jeter le linge sans l'ouvrir. Une colonne de prises en diagonale monte dans l'angle jusqu'au meuble haut. <a href="{ARCHIVE}">L'ancien meuble bas</a> reste dans les archives.</p>

<h2 id="iso">Le meuble</h2>
<div class="fig ens">{iso}</div>
<div class="fig ens">{dedans}<p class="cap">Sans la porte : le bas, l'étagère, les deux bacs et le fond.</p></div>
<div class="fig ens">{eclate}<p class="cap">Vue éclatée : le plateau levé, la porte sortie vers l'avant, la machine et son tapis aussi. La colonne n'est pas dessinée ici.</p></div>

{structure()}

{colonne()}

<h2 id="plan">Plan</h2>
{plan_}

<h2 id="elevation">Élévation</h2>
{face}

<h2 id="coupe">Coupe</h2>
{coupe}

{mesures()}

<p class="note">Repère : origine à l'angle nord-ouest intérieur, x vers l'est, y vers le sud, z depuis le sol, cotes en cm. Source : <span class="mono">3d/sdb/modele.py</span> pour les relevés, <span class="mono">3d/sdb/bas.py</span> pour la page (<span class="mono">just sdb</span>).</p>

<section id="changements">
<h2>Changements</h2>
<div class="scroll"><table><thead><tr><th>Version</th><th>Date</th><th>Changements</th></tr></thead>
<tbody>{lignes}</tbody></table></div>
</section>"""
    h = PG.gabarit("Meuble bas · nouvelle conception", "bas", corps, barre_html=BARRE)
    return h.replace("</style>", CO.CSS + CSS + "</style>", 1)


def ecrire():
    chemin = os.path.join(PL.ROOT, PAGE)
    with open(chemin, "w", encoding="utf-8") as fh:
        fh.write(page())
    print(chemin)


if __name__ == "__main__":
    ecrire()
