# Cuisine V13 : source unique (repart de la V12.7, 3d/v12/ gardé pour mémoire).
#
# Ce fichier ne contient que des données : il est lu par plan.py (HTML : plan et élévations,
# projetés depuis ces volumes) et par cad.py (FreeCAD → .FCStd / .glb). Toute modification
# se fait ici, jamais dans le HTML ni dans le modèle 3D.
#
# Cotes en cm : x vers l'est, y vers le sud (comme le plan), z depuis le sol fini.
# Chaque volume : Bloc(role, nom, x0, x1, y0, y1, z0, z1). Le rôle fixe le style du plan
# et le matériau du rendu.

import math
import os
from dataclasses import dataclass

VERSION = "V13.15"
H = 250  # hauteur sous plafond


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
    etiq: str = ""  # nom affiché sur le plan et les coupes (B1, H1, C1…)
    poignee: str = ""  # façades : « tiroir », « porte » ou « relevable » (dessin de la poignée sur les coupes)
    contenu: str = ""  # façades : ce qu'on range derrière (écrit sur les coupes)
    arrondi: float = 0  # rayon de l'angle arrondi (x0, y1) : angle sud-ouest en plan
    coins: str = "so"  # angles arrondis : « so » (sud-ouest seul) ou « tous »


@dataclass
class Cyl:
    role: str
    nom: str
    cx: float
    cy: float
    r: float
    z0: float
    z1: float

    # emprise, pour les projections
    x0 = property(lambda c: c.cx - c.r)
    x1 = property(lambda c: c.cx + c.r)
    y0 = property(lambda c: c.cy - c.r)
    y1 = property(lambda c: c.cy + c.r)


@dataclass
class Pan:
    """Panneau vertical posé en biais, de a à b (axe), épaisseur ep centrée sur l'axe."""
    role: str
    nom: str
    a: tuple
    b: tuple
    ep: float
    z0: float
    z1: float

    # emprise, pour les projections (vu de face ou de profil, un panneau vertical couvre son emprise)
    x0 = property(lambda p: min(p.a[0], p.b[0]))
    x1 = property(lambda p: max(p.a[0], p.b[0]))
    y0 = property(lambda p: min(p.a[1], p.b[1]))
    y1 = property(lambda p: max(p.a[1], p.b[1]))


# ------------------------------------------------------------------ enveloppe (pièce vide)
# Chambre + ancien cellier ouverts : aucune cloison neuve. Relevé repris de cuisine-plan.html V3.6.
ENVELOPPE = [
    Bloc("mur", "nord", -20, 434, -20, 0, 0, H),
    Bloc("mur", "nord_alcove", 434, 494, -20, 44, 0, H),
    Bloc("mur", "est_wc", 484, 494, 44, 262, 0, H),
    Bloc("mur", "alcove_wc", 382, 484, 100, 110, 0, H),
    Bloc("mur", "ouest_wc", 382, 392, 110, 262, 0, H),
    # mur ouest, fenêtre coulissante y 58 → 200 (allège 106, linteau 215)
    Bloc("mur", "ouest_nord", -20, 0, -20, 58, 0, H),
    Bloc("mur", "ouest_sud", -20, 0, 200, 262, 0, H),
    Bloc("allege", "allege", -20, 0, 58, 200, 0, 106),
    Bloc("linteau", "linteau_fenetre", -20, 0, 58, 200, 215, H),
    # mur sud, baie d'entrée 78 × 204 (x 228 → 306)
    Bloc("mur", "sud_ouest", 0, 228, 252, 262, 0, H),
    Bloc("mur", "sud_est", 306, 382, 252, 262, 0, H),
    Bloc("linteau", "linteau_entree", 228, 306, 252, 262, 204, H),
    # décroché de maçonnerie de l'angle sud-est (relevé du 04/10/2026)
    Bloc("mur", "decroche_se", 341, 382, 240, 252, 0, H),
    # porte d'entrée à galandage : doublage de 10 côté cuisine contre le mur sud (y 242 → 252), avec le caisson du
    # galandage à l'ouest de la baie (x 140 → 225) et un montant de 4 à l'est ; vantail 83 × 204 (fermé), qui
    # recouvre la baie de 3 côté poche et de 2 côté montant. Face cuisine du caisson : tableau noir et zone aimantée.
    Bloc("cloison", "galandage_caisson", 140, 225, 242, 252, 0, H),
    Bloc("cloison", "galandage_montant", 308, 312, 242, 252, 0, H),
    Bloc("linteau", "linteau_galandage", 225, 308, 242, 252, 204, H),
    Bloc("porte", "entree_vantail", 225, 308, 245, 249, 0, 204),
    Bloc("ardoise", "tableau_noir", 142, 223, 241.5, 242, 120, 200),
    Bloc("aimant", "zone_aimantee", 142, 223, 241.5, 242, 70, 118),
]
# ------------------------------------------------------------------ cellier : cloison et porte
# Un retour de cloison (x 320 → 327) garde le passage des réseaux, qui longent le mur nord à h 43–50 ; la baie va de
# là au flanc nord de la première colonne, sous un linteau à h 204 (V13.4 : y 48 → 110, voir plus bas).
# V11.40 : PORTE DE PLACARD PLIANTE à deux vantaux de 36 (2,5 d'épaisseur), posée sans dormant sur un rail haut côté
# cuisine (x 318,5). Pivot contre le retour de cloison, au nord ; en s'ouvrant, les deux vantaux se replient l'un
# contre l'autre et se rangent côté cuisine, perpendiculaires à la baie, devant le coffre des réseaux (x 282 → 318,5,
# y 8 → 13). Côté cellier, ils heurteraient le rayonnage nord. Le vantail du pivot balaie un quart de cercle de 36
# côté cuisine. Poignée au sud, côté C1 (V13.0).
# V13.0 : C3 supprimée ; la porte descend de 45 vers le sud : le retour de cloison s'allonge d'autant (y 0 → 53, mur
# neuf de 45) et la baie va jusqu'au flanc nord de C1 (y 120), soit 67 (6 de moins : C1 + C2 = 120 tiennent juste
# entre la baie et le décroché du mur sud, y 240).
PORTE_TITRE = "porte pliante sur ferrure Mantion Tango, 2 vantaux repliés au nord"
DECALAGE_PORTE = 40                             # porte du cellier décalée vers le sud (V13.0 : 45 ; V13.4 : 40)
CLOISON_Y1, MONTANT, _charnieres = 8 + DECALAGE_PORTE, 0, []          # plus de vantail battant
C3_L = 0                                        # V13.0 : C3 (colonne tiroirs à l'anglaise) supprimée
# V13.1 : fileur de 10 entre C2 et le mur sud (décroché, y 240) : la porte du frigo s'ouvre à 90° sans toucher le
# fileur de l'entrée ; C1 et C2 remontent de 10, pris sur la baie (57, vantaux de 28, passage 50), le mur reste à 45
# V13.4 : mur neuf réduit à 40 (retour de cloison y 0 → 48) : baie 62 (y 48 → 110), vantaux de 30,5, passage 55
# V13.5 : fileur réduit à 5 (baie 67) ; ouverture du frigo calculée plus bas (FRIGO_ANGLES)
FILEUR_C2 = 5
JOUE_C2 = 240 - FILEUR_C2 - 2 * 60              # face nord de la colonne la plus au nord (C1), y 110
BAIE_Y0, BAIE_Y1 = CLOISON_Y1, JOUE_C2 - MONTANT
# V13.7 : fermée, la porte est dans l'épaisseur de la cloison, au nu du mur côté cuisine (vantaux x 320 → 322,5)
# V13.14 : modèle réel, ferrure Mantion TANGO40-120 (« système coulissant pliant pour portes de séparation et portes
# de placard ») : 2 panneaux de 16 à 40 mm, 40 kg chacun, 750 de large au plus ; rail alu 33 × 27 vissé sous le
# linteau, pivots haut et bas au nord, une monture à roulements au bout libre, pas de rail au sol. Notice : baie
# B = 2 Lp + 1,2 + J (mm ; J = 4 pour 16 à 22 d'épaisseur), H = Hp + 64 (rail 33 + jeu 20, jeu au sol 11).
# Panneaux de 19 (mélaminé ou plaqué chêne, à faire découper) : Lp = (670 − 1,2 − 4) / 2 ≈ 332, Hp = 2040 − 64 = 1976.
DORMANT, EP_VANTAIL = 0, 1.9                    # pas de dormant
X_PORTE = 320 + EP_VANTAIL / 2                  # rail de la porte pliante (axe des vantaux fermés), x 320,95
TANGO = dict(ref="TANGO40-120", nom="Mantion Tango", rail=(3.3, 2.7), jeu_haut=2.0, jeu_bas=1.1, j=0.4, joint=0.12,
             prix="≈ 110 € TTC (Bricozor, kit 2 panneaux)",
             notice="https://cdn.chausson.fr/catalog-document/67dbd044-7a74-4311-8f35-f17acf5a8f4f/notice-20commerciale-20-"
                    "20ensemble-20coulissant-20pour-20porte-20de-20placard-20tango-20-20mantion.pdf",
             achat="https://www.bricozor.com/vantail-40-kg-portes-pliantes-meubles-interieur-serie-tango-kit-complet-mantion.html")
_hl = 204                                      # sous-face du linteau
PLIANTE = dict(rail=X_PORTE, y0=BAIE_Y0, y1=BAIE_Y1, l=round((BAIE_Y1 - BAIE_Y0 - TANGO["joint"] - TANGO["j"]) / 2, 1),
               ep=EP_VANTAIL, z0=TANGO["jeu_bas"], z1=_hl - TANGO["rail"][0] - TANGO["jeu_haut"],
               mi=60)   # état mi-ouvert : vantail du pivot tourné de 60° vers la cuisine
ACCORDEON = None
VANTAUX_L = [BAIE_Y1 - BAIE_Y0]
CELLIER_VANTAUX = []
ENVELOPPE += [
    Bloc("cloison", "cloison_cellier", 320, 327, 0, CLOISON_Y1, 0, H),
    Bloc("linteau", "linteau_cellier", 320, 327, BAIE_Y0, BAIE_Y1, 204, H),
    # porte pliante fermée (deux vantaux dans la baie) ; repliée, voir PLIANTE
    Bloc("porte", "cellier_pliante", X_PORTE - EP_VANTAIL / 2, X_PORTE + EP_VANTAIL / 2, BAIE_Y0, BAIE_Y1, PLIANTE["z0"],
         PLIANTE["z1"]),
]
# Ballon d'eau chaude existant Ø 50 dans la niche du cellier (h 90 → 210). (La variante ballon extra-plat au WC a été
# retirée en V11.39.)
PLAT = False
BALLON = Cyl("ballon", "ballon_ecs", 459, 72, 25, 90, 210)
# Sols : parquet chêne en bâtons rompus dans l'ancienne chambre, béton ciré gris ciment dans l'ancien
# cellier et l'ancien placard (à partir du nu ouest de l'ancienne cloison, x 325).
SOL_PARQUET = [(0, 0), (325, 0), (325, 252), (0, 252)]
SOL_CIMENT = [(325, 0), (434, 0), (434, 44), (484, 44), (484, 100), (382, 100), (382, 240), (341, 240),
              (341, 252), (325, 252)]
# Cloisons déposées (relevé d'origine) : chambre / cellier + placard, cellier / placard. Dessinées en tireté.
CLOISONS_DEPOSEES = [
    Bloc("depose", "chambre_cellier", 325, 335, 0, 252, 0, H),
    Bloc("depose", "cellier_placard", 335, 382, 100, 110, 0, H),
]
# sol du cellier fermé (jusqu'au dos des portes, moins la chute, + niche du ballon x 434 → 484, y 44 → 100)
CELLIER_SOL = [(327, 0), (434, 0), (434, 44), (484, 44), (484, 100), (382, 100), (382, JOUE_C2),
               (325.5, JOUE_C2), (325.5, CLOISON_Y1), (327, CLOISON_Y1)]
ZONES = []
WC = [(392, 110), (484, 110), (484, 252), (392, 252)]
FENETRE = dict(y0=58, y1=200, allege=106, linteau=215)
# porte d'entrée à galandage : vantail fermé x 225 → 308, ouvert dans la poche x 142 → 225 (axe y 247)
ENTREE = dict(x0=228, x1=306, h=204, vantail=83, ferme=(225, 308), ouvert=(142, 225), y=247, poche=(140, 225))

# ------------------------------------------------------------------ meubles
# Conventions : socle 15 en retrait de 5 sous les façades, caisson P58 h 15 → 87, façade 2.
SOCLE, CAISSON_H, P_CAISSON, FACADE = 15, 87, 58, 2

MEUBLES = []


def meuble_bas_nord(nom, x0, largeur, p=P_CAISSON):
    x1 = x0 + largeur
    MEUBLES.append(Bloc("socle", f"socle_{nom}", x0, x1, 0, p - 3, 0, SOCLE))
    MEUBLES.append(Bloc("caisson", f"caisson_{nom}", x0, x1, 0, p, SOCLE, CAISSON_H, nom.upper()))


# Meubles hauts : caisson P33 + façade 2, h 153 → 243 (remontés de 5 en V11.8 : 62 au-dessus du plan),
# fileur de 7 jusqu'au plafond.
HAUT_Z0, HAUT_Z1, P_HAUT = 153, 243, 33


HAUTS_CONTENU = ["hotte intégrée", "épices, huiles", "petit-déjeuner, épicerie", "assiettes, bols",
                 "verres, tasses, café, thé"]


def meuble_haut_nord(nom, x0, largeur, contenu=""):
    x1 = x0 + largeur
    MEUBLES.append(Bloc("caisson_haut", f"caisson_{nom}", x0, x1, 0, P_HAUT, HAUT_Z0, HAUT_Z1, nom.upper()))
    MEUBLES.append(Bloc("facade_haut", f"facade_{nom}", x0, x1, P_HAUT, P_HAUT + FACADE, HAUT_Z0, HAUT_Z1,
                        poignee=ORGA["hauts"], contenu=contenu))
    # ruban LED sous le caisson, vers l'avant, éclairant le plan de travail
    MEUBLES.append(Bloc("led", f"led_{nom}", x0 + 2, x1 - 2, P_HAUT - 7, P_HAUT - 5, HAUT_Z0 - 0.8, HAUT_Z0))


# mur nord : 4 meubles bas de 60, à 25 du mur ouest (x 25 → 265), fileur de 25 au mur ; plaque sur B2, LV en B3, évier sur B4.
# V11.38 : la porte accordéon ne balaie plus la cuisine, la rangée se décale de 10 vers l'est ; elle s'arrête là pour que
# l'accès à la porte (coin du plan de B4 → angle de C3, ≈ 60) reste au moins égal au passage de la porte (59).
# V11.41 : fileur du mur ouest réduit à 5 ; la rangée finit toujours à x 265.
# V11.43 : B1 coulissant de 20, B2 plaque 60, B3 tiroirs 60, B4 LV, B5 évier (x 5 → 265).
# V13.0 : B6 de 40, P40 (caisson 38 + façade 2), entre B5 et le retour de cloison du cellier (x 265 → 305), puis un
# fileur Canopée de 15 jusqu'au mur (x 320) : plan de travail de mur à mur, P42 au-dessus de B6. P40 : le plan s'arrête
# à 6 des vantaux de la porte du cellier repliés (y 48, V13.4).
# V13.2 : fileurs de 10 aux deux bouts de la rangée (mur ouest et retour de cloison) : rangée x 10 → 310
ECART_OUEST = 10
LARGEURS_BAS = [20, 60, 60, 60, 60, 40]
N_BAS, N_HAUTS = len(LARGEURS_BAS), 5
X_CLOISON = 320                                 # nu ouest du retour de cloison du cellier : fin de la rangée nord
B_ETROIT, P_ETROIT = 6, 38                      # B6 : caisson P38 (façade 2 : P40)
P_BAS = {B_ETROIT: P_ETROIT}
_X_BAS = [ECART_OUEST + sum(LARGEURS_BAS[:i]) for i in range(N_BAS + 1)]   # bords des meubles bas
# V11.50 : le LV monte en colonne (C1) ; B4 devient un meuble à tiroirs ; four encastré sous la plaque (B2)
B_COULISSANT, B_PLAQUE, B_TIROIRS, B_TIROIRS_2, B_EVIER = 1, 2, 3, 4, 5
B_LV = None
for i in range(N_BAS):
    meuble_bas_nord(f"b{i + 1}", _X_BAS[i], LARGEURS_BAS[i], P_BAS.get(i + 1, P_CAISSON))

# ------------------------------------------------------------------ organisation des façades (A, tout en tiroirs)
# L'électroménager ne bouge pas : B2 (sous la plaque : four encastré 60 au-dessus d'un tiroir de 12)
# (LV, façade intégrée) sont fixes. Façades du haut vers le bas, hauteurs en cm (total 72, h 15 → 87).
# (genre, hauteur, contenu)
ORGA = dict(titre="Tout en tiroirs", hauts="porte",
            bas={B_TIROIRS: [("tiroir", 18, "ustensiles"), ("tiroir", 27, "poêles"), ("tiroir", 27, "casseroles")],
                 B_COULISSANT: [("tiroir", 72, "huiles, épices")],
                 B_TIROIRS_2: [("tiroir", 18, "couverts"), ("tiroir", 27, "moules, plats à four"),
                               ("tiroir", 27, "boîtes de conservation")],
                 5: [("tiroir", 72, "tri : 3 bacs")],
                 # V13.0 : B6 reprend une partie de C3 ; V13.8 : un placard (porte, charnières à l'ouest pour ne pas
                 # gêner la porte du cellier repliée ; une étagère, fond découpé pour les tuyaux) sous la machine à café
                 B_ETROIT: [("porte", 72, "café, détartrant, boîtes, torchons")]})
FACADES_FIXES = {B_PLAQUE: [("four", 60, ""), ("tiroir", 12, "plaques, grilles")]}
for n in range(1, N_BAS + 1):
    x0, x1 = _X_BAS[n - 1], _X_BAS[n]
    z, p = CAISSON_H, P_BAS.get(n, P_CAISSON)
    for k, (genre, h, contenu) in enumerate(FACADES_FIXES.get(n) or ORGA["bas"][n]):
        MEUBLES.append(Bloc("four" if genre == "four" else "facade", f"facade_b{n}_{k + 1}", x0, x1, p,
                            p + FACADE, z - h, z, poignee="" if genre in ("bandeau", "four") else genre,
                            contenu=contenu))
        z -= h



def sur_bas(n):
    """Emprise x du meuble bas n (1 = le plus à l'ouest)."""
    return _X_BAS[n - 1], _X_BAS[n]


# plan de travail 4, P62 (débord 2 devant les façades), sur toute la rangée basse
PT_Z1 = CAISSON_H + 4
MEUBLES.append(Bloc("plan", "plan_nord", 0, sur_bas(B_EVIER)[1], 0, 62, CAISSON_H, PT_Z1))   # jusqu'au mur ouest
# V13.0 : plan P42 au-dessus de B6 et de son fileur, jusqu'au retour de cloison (plan de mur à mur)
P_PLAN_ETROIT = P_ETROIT + FACADE + 2
MEUBLES.append(Bloc("plan", "plan_b6", sur_bas(B_ETROIT)[0], X_CLOISON, 0, P_PLAN_ETROIT, CAISSON_H, PT_Z1))
# fileur Canopée entre B6 et le retour de cloison (15 en V13.0, 10 en V13.2) (dans le plan des façades), socle prolongé dessous
FILEUR_EST = X_CLOISON - sur_bas(B_ETROIT)[1]
MEUBLES.append(Bloc("socle", "socle_fileur_est", sur_bas(B_ETROIT)[1], X_CLOISON, 0, P_ETROIT - 3, 0, SOCLE))
MEUBLES.append(Bloc("joue", "fileur_est", sur_bas(B_ETROIT)[1], X_CLOISON, P_ETROIT, P_ETROIT + FACADE, SOCLE, CAISSON_H))
# fileur Canopée de 25 entre B1 et le mur ouest (dans le plan des façades), socle prolongé dessous
MEUBLES.append(Bloc("socle", "socle_fileur_ouest", 0, ECART_OUEST, 0, P_CAISSON - 3, 0, SOCLE))
MEUBLES.append(Bloc("joue", "fileur_ouest", 0, ECART_OUEST, P_CAISSON, P_CAISSON + FACADE, SOCLE, CAISSON_H))

# induction 60 classique (V11.50 : sans aspiration, hotte intégrée dans H1 au-dessus), 54 × 50, à 3 des chants
x0, x1 = sur_bas(B_PLAQUE)
xm = (x0 + x1) / 2
MEUBLES.append(Bloc("plaque", "induction", x0 + 3, x1 - 3, 6, 56, PT_Z1, PT_Z1 + 0.6))

# évier inox 1 bac à encastrer 56 × 50, bac 40 × 40 × 20, mitigeur derrière le bac
x0, x1 = sur_bas(B_EVIER)
xm = (x0 + x1) / 2
# V11.37 : évier 1 bac + égouttoir à gauche, 100 × 50 : le bac reste centré sur B4, l'égouttoir passe au-dessus de B3
EVIER_L, EGOUTTOIR_L = 100, 40
MEUBLES.append(Bloc("evier", "evier_plage", x1 - 2 - EVIER_L, x1 - 2, 6, 56, PT_Z1, PT_Z1 + 0.4))
MEUBLES.append(Bloc("egouttoir", "egouttoir", x1 - 2 - EVIER_L + 4, x1 - 2 - EVIER_L + 4 + EGOUTTOIR_L, 10, 52,
                    PT_Z1 + 0.4, PT_Z1 + 0.7))
MEUBLES.append(Bloc("cuve", "evier_bac", xm - 20, xm + 20, 12, 52, PT_Z1 - 20, PT_Z1))
MEUBLES.append(Cyl("mitigeur", "mitigeur", xm, 8, 1.6, PT_Z1 + 0.4, PT_Z1 + 31))



def equiper(n, texte):
    """Ajoute l'équipement du meuble bas n à son étiquette (« B5 LV »)."""
    b = next(b for b in MEUBLES if b.nom == f"caisson_b{n}")
    b.etiq = f"B{n} {texte}"


equiper(B_EVIER, "poubelles")  # sous l'évier : tri sélectif sur coulissant
equiper(B_PLAQUE, "four")      # four 60 encastré sous la plaque
equiper(B_ETROIT, "placard")   # V13.8 : porte au lieu de 3 tiroirs

# ------------------------------------------------------------------ réseaux d'eau
# Pose type IKEA METOD : pas de vide technique (1 cm de jeu derrière les caissons). Le LV est repiqué sur l'évier
# (vidange sur le siphon, robinet d'arrêt dans B4) : aucun tuyau derrière sa niche. À l'est de l'évier (V11.35, plus de
# B5), les tuyaux passent dans un coffre bas couleur des murs (P8, h 0 → 55) contre le mur nord jusqu'à la cloison,
# puis dans le retour de cloison de 8 au nord de la porte du cellier.
# Tout longe les murs, en partie basse. Alimentation EF/EC (à 3 des murs) : de la nourrice sous le ballon, le long du
# retour sud du mur nord de l'alcôve (y 44), puis de sa face ouest (x 434), puis du mur nord jusqu'à l'évier.
# Évacuation (à 4 du mur nord dans la cuisine, à 12 des murs au-delà de la nourrice) : le long du mur nord, de la face ouest et du retour sud de
# l'alcôve, du mur est (x 484), puis du mur nord du WC (y 100) jusqu'à la chute existante (colonne d'eaux usées,
# contre le mur du WC sous le ballon). Contre l'alcôve, ils passent sous la première tablette du rayonnage du mur
# nord (h 60) ; sous le ballon (h 90), ils passent dessous.
# (rôle, nom, points (x, y), z, rayon)
CHUTE = (459, 94)
X_LV_RES = 378                                  # passage des réseaux du LV (colonne C1), contre le dos de C1
X_MUR_EST_C = 382
NOURRICE = (470, 52)
xe = (sur_bas(B_EVIER)[0] + sur_bas(B_EVIER)[1]) / 2   # axe de l'évier
SIPHON = (xe, 32)
# Dans la niche (x > 431), tout reste dans la zone technique des 30 premiers cm (la chute est basse : dernier étage) :
# l'alimentation y passe à h 20 et remonte à h 50 dans l'angle (x 431, y 47) ; l'évacuation descend de h 43 à h 25
# sous la première tablette du rayonnage nord (x 422, y 38). Un coffre technique (h 0 → 30) couvre l'angle.
RESEAUX = [
    ("alim", "alim_niche", [NOURRICE, (NOURRICE[0], 47), (431, 47)], 20, 0.8),
    ("alim", "alim_evier", [(431, 47), (431, 3), (xe, 3), (xe, 8)], 50, 0.8),
    # LV en colonne (C1, V11.50) : sans traverser le cellier, l'alimentation part de la nourrice, longe le mur est puis
    # le mur nord du WC (y 99, h 20, derrière les balais) et entre dans C1 par son dos
    ("alim", "alim_lv", [NOURRICE, (481, NOURRICE[1]), (481, 99), (X_LV_RES, 99), (X_LV_RES, JOUE_C2 + 10)], 20, 0.8),
    ("evac", "evac_evier", [SIPHON, (xe, 4), (422, 4), (422, 38)], 43, 2),
    ("evac", "evac_niche", [(422, 38), (422, 56), (472, 56), (472, 88), (CHUTE[0], 88), CHUTE], 25, 2),
    # vidange du LV (pompe) : de C1, le long du mur nord du WC (y 95, h 25), directement dans la chute
    ("evac", "evac_lv", [(X_LV_RES, JOUE_C2 + 10), (X_LV_RES, 95), (CHUTE[0] - 5, 95)], 25, 2),
]
ZONE_TECH = 30
# V13.8 : machine à café (expresso automatique, environ 24 × 36 × h 36) sur le plan de B6, contre la crédence ; 26 de
# dégagement sous H5
CAFE = dict(x0=sur_bas(B_ETROIT)[0] + 8, x1=sur_bas(B_ETROIT)[0] + 32, y0=3, y1=39, h=36)
MEUBLES.append(Bloc("cafetiere", "machine_cafe", CAFE["x0"], CAFE["x1"], CAFE["y0"], CAFE["y1"], PT_Z1, PT_Z1 + CAFE["h"]))
# V13.0 : plus de coffre des réseaux : B6 et son fileur les recouvrent jusqu'au retour de cloison (fond de B6 découpé)
COFFRE_RESEAUX = None

_ev = RESEAUX[3][2] + RESEAUX[4][2][1:]
EVAC_LONGUEUR = round(sum(math.dist(a, b) for a, b in zip(_ev, _ev[1:])))

# mur nord : 3 meubles hauts de 60, réalignés sur les joints des bas (V11.39) : ils finissent au droit de B4
# (x 85 → 265, au-dessus de B2, B3, B4) ; à leur gauche, 3 étagères ouvertes en chêne du mur ouest à H1, P25.
# V11.41 : H1 passe à 80 comme B2, pour garder les joints des hauts au droit de ceux des bas (x 65 → 265)
# V11.50 : un haut de plus, H1 au-dessus de la plaque avec la hotte intégrée (groupe filtrant) ; hauts x 25 → 265
# V13.0 : H5 de 40 au-dessus de B6, même profondeur que H4 (P33 + façade 2), fileur de 15 jusqu'au retour de cloison
LARGEURS_HAUTS = [60, 60, 60, 60, 40]
DEPART_HAUTS = sur_bas(N_BAS)[1] - sum(LARGEURS_HAUTS)
# V11.40 : étagères tout le long, du mur ouest à H1
ETAGERES_MUR = dict(x0=0, x1=DEPART_HAUTS - 2, p=25, zs=[160, 195, 230],
                    contenus=["livres de cuisine", "bocaux", "plantes, objets"])
for k, (z, c) in enumerate(zip(ETAGERES_MUR["zs"], ETAGERES_MUR["contenus"])):
    MEUBLES.append(Bloc("etagere_haute", f"etagere_mur_{k + 1}", ETAGERES_MUR["x0"], ETAGERES_MUR["x1"], 0,
                        ETAGERES_MUR["p"], z, z + 2.5, contenu=c))
for i in range(N_HAUTS):
    meuble_haut_nord(f"h{i + 1}", DEPART_HAUTS + sum(LARGEURS_HAUTS[:i]), LARGEURS_HAUTS[i], HAUTS_CONTENU[i])
# hotte intégrée dans H1 (au-dessus de la plaque) : groupe filtrant en recyclage dans le bas du meuble, visière inox
HOTTE = Bloc("hotte", "hotte_integree", DEPART_HAUTS + 2, DEPART_HAUTS + 58, 1, P_HAUT - 1, HAUT_Z0 - 0.6, HAUT_Z0 + 12)
MEUBLES.append(HOTTE)
# joues de finition de 2 sur les flancs visibles des hauts, fileur de 7 jusqu'au plafond sur toute la longueur
FIN_HAUTS = DEPART_HAUTS + sum(LARGEURS_HAUTS)
MEUBLES.append(Bloc("joue", "joue_h_ouest", DEPART_HAUTS - 2, DEPART_HAUTS, 0, P_HAUT + FACADE, HAUT_Z0, HAUT_Z1))
# V13.0 : à l'est, fileur de 15 jusqu'au retour de cloison (plus de flanc visible)
MEUBLES.append(Bloc("joue", "fileur_h_est", FIN_HAUTS, X_CLOISON, P_HAUT, P_HAUT + FACADE, HAUT_Z0, HAUT_Z1))
MEUBLES.append(Bloc("fileur", "fileur_hauts", DEPART_HAUTS - 2, X_CLOISON, P_HAUT, P_HAUT + FACADE, HAUT_Z1, H))

# ------------------------------------------------------------------ colonnes, mur est
# Colonnes P60 (caisson 58 + façade 2), socle 15, dessus aligné sur les hauts, contre le mur du WC (x 382),
# à la place des anciens E1 / E2 : C2 frigo y 120 → 180, C1 four y 180 → 240 (jusqu'au décroché). Façades vers l'ouest.
Y_MUR_SUD = 252
X_MUR_EST = 382
COL_DOS = X_MUR_EST
COL_X = COL_DOS - P_CAISSON - FACADE      # nu des façades, x 322
COL_Z1 = HAUT_Z1
# V11.50 : du nord au sud, C1 LV + MO (60, y 81 → 141), C2 frigo (60), C3 tiroirs à l'anglaise (39, → 240)
# V13.0 : C3 supprimée, C1 et C2 descendent jusqu'au décroché : C1 y 120 → 180, C2 y 180 → 240
# V13.1 : fileur de 10 au sud de C2 : C1 y 110 → 170, C2 y 170 → 230, fileur y 230 → 240
# V13.5 : fileur de 5 : C1 y 115 → 175, C2 y 175 → 235, fileur y 235 → 240
COL_Y0, COL_Y1 = JOUE_C2 + 60, 240


COLONNES_CONTENU = {("c1", "tiroir_1"): "pastilles LV, torchons", ("c1", "lv"): "lave-vaisselle intégré",
                    ("c1", "porte_haute"): "réserves", ("c2", "porte_haute"): "grands plats, saladiers"}


def colonne_est(nom, y0, largeur, facades, etiq):
    """facades : (rôle, nom, z0, z1), de bas en haut."""
    y1 = y0 + largeur
    MEUBLES.append(Bloc("socle", f"socle_{nom}", COL_X + 5, COL_DOS, y0, y1, 0, SOCLE))
    MEUBLES.append(Bloc("colonne", f"caisson_{nom}", COL_X + FACADE, COL_DOS, y0, y1, SOCLE, COL_Z1, etiq))
    for role, n, z0, z1 in facades:
        p = "tiroir" if n.startswith("tiroir") or n == "lv" else "porte" if n in ("porte_haute", "frigo", "porte_anglaise") else ""
        MEUBLES.append(Bloc(role, f"{n}_{nom}", COL_X, COL_X + FACADE, y0, y1, z0, z1, poignee=p,
                            contenu=COLONNES_CONTENU.get((nom, n), "")))


# C1 (V11.50, au nord) : lave-vaisselle 60 intégré en hauteur à la place du four (niche 82, h 66 → 148), micro-ondes
# encastrable au-dessus (niche 38, h 148 → 186), un tiroir dessous, rangement dessus
LV_Z0, MO_Z0, MO_Z1 = 66, 148, 186
colonne_est("c1", JOUE_C2, 60, [
    ("facade_col", "tiroir_1", SOCLE, LV_Z0), ("facade_col", "lv", LV_Z0, MO_Z0), ("micro_onde", "micro_onde", MO_Z0, MO_Z1),
    ("facade_col", "porte_haute", MO_Z1, COL_Z1)], "C1 LV + MO")
# C2 : réfrigérateur intégrable (niche 178), porte de rangement au-dessus
colonne_est("c2", COL_Y0, 60, [
    ("facade_col", "frigo", SOCLE, 193), ("facade_col", "porte_haute", 193, COL_Z1)], "C2 frigo")
# V13.0 : C3 (colonne de 39 à tiroirs à l'anglaise) supprimée ; son contenu passe dans B6 et H5, les bocaux et vases au
# cellier.
TIROIRS_ANGLAISE = []
# V13.1 : fileur chêne (10, puis 5 en V13.5) entre C2 et le mur sud, dans le plan des façades, socle dessous
# V13.7 : le fileur descend jusqu'au nu du montant de l'entrée (y 242), où il rejoint le fileur couleur des murs ; la
# joue x 322 → 341, enfermée derrière lui (entre C2 et le décroché), est retirée
Y_MONTANT = next(b for b in ENVELOPPE if b.nom == "galandage_montant").y0      # nu nord du montant de l'entrée, y 242
MEUBLES.append(Bloc("socle", "socle_fileur_c2", COL_X + 5, COL_DOS, COL_Y1 - FILEUR_C2, COL_Y1, 0, SOCLE))
MEUBLES.append(Bloc("joue", "fileur_c2", COL_X, COL_X + FACADE, COL_Y1 - FILEUR_C2, Y_MONTANT, SOCLE, COL_Z1))
# fileur couleur des murs entre C1 et le mur sud (montant du galandage, x 312) : ferme la poche de l'angle sud-est
# V13.7 : aligné sur le montant de l'entrée (nu nord y 242) au lieu de dépasser de 2 devant
MEUBLES.append(Bloc("joue", "fileur_c1", 312, COL_X + FACADE, Y_MONTANT, Y_MONTANT + 2, 0, H))
MEUBLES.append(Bloc("fileur", "fileur_colonnes", COL_X, COL_X + FACADE, JOUE_C2, COL_Y1 + 2, COL_Z1, H))

# ------------------------------------------------------------------ triangle d'activité (centres de l'évier et de la plaque,
# milieu de la façade du frigo)
_plaque = next(b for b in MEUBLES if b.role == "plaque")
_cuve = next(b for b in MEUBLES if b.role == "cuve")
_frigo = next(b for b in MEUBLES if b.nom == "caisson_c2")
TRIANGLE = [("frigo", (COL_X, (_frigo.y0 + _frigo.y1) / 2)),
            ("évier", ((_cuve.x0 + _cuve.x1) / 2, (_cuve.y0 + _cuve.y1) / 2)),
            ("plaque", ((_plaque.x0 + _plaque.x1) / 2, (_plaque.y0 + _plaque.y1) / 2))]


# ------------------------------------------------------------------ coin repas : banquette et table, angle sud-ouest
# Banquette contre le mur sud, du mur ouest au retour du doublage de la porte d'entrée (x 0 → 140, V11.45) : assise 45
# (h 45), dossier 5 (h 85). Deux places larges (70 chacune), trois en se serrant. Dessous, deux tiroirs (façades
# h 6 → 40) ; V11.46 : la table n'ayant plus qu'un pied central, ils passent au-dessus de son embase (h 2).
BANQ = dict(x0=0, x1=ENTREE["poche"][0], y0=Y_MUR_SUD - 50, y1=Y_MUR_SUD)
PLACES_BANQUETTE, LARGEUR_PLACE = 2, 70
TIROIRS_BANQ = [(3, 67), (73, 137)]   # V11.46 : pied central, ils passent au-dessus de l'embase
MEUBLES += [
    Bloc("banquette", "banquette_assise", BANQ["x0"], BANQ["x1"], BANQ["y0"], BANQ["y1"] - 5, 0, 45, "banquette"),
    Bloc("banquette", "banquette_dossier", BANQ["x0"], BANQ["x1"], BANQ["y1"] - 5, BANQ["y1"], 0, 85),
] + [Bloc("facade", f"tiroir_banquette_{k + 1}", a, b, BANQ["y0"] - 2, BANQ["y0"], 6, 40, poignee="tiroir",
          contenu=c) for k, ((a, b), c) in enumerate(zip(TIROIRS_BANQ, ("nappes, sets", "jeux, bougies")))]
# Étagère au-dessus de la banquette, contre le mur sud : P25, dessus à h 162,5 (assez haut pour la tête assise), avec
# l'enceinte audio (22 × 18 × 30) posée à l'est.
ETAGERE_BANQ = dict(x0=BANQ["x0"], x1=BANQ["x1"], y0=Y_MUR_SUD - 25, y1=Y_MUR_SUD, z0=160, z1=162.5)
MEUBLES += [
    Bloc("etagere_haute", "etagere_banquette", ETAGERE_BANQ["x0"], ETAGERE_BANQ["x1"], ETAGERE_BANQ["y0"],
         ETAGERE_BANQ["y1"], ETAGERE_BANQ["z0"], ETAGERE_BANQ["z1"]),
    Bloc("enceinte", "enceinte_audio", BANQ["x1"] - 28, BANQ["x1"] - 6, Y_MUR_SUD - 20, Y_MUR_SUD - 2, ETAGERE_BANQ["z1"],
         ETAGERE_BANQ["z1"] + 30),
    # plante retombante à l'ouest de l'étagère : pot Ø 16, feuillage Ø 28
    Cyl("pot", "pot_plante", 22, Y_MUR_SUD - 12, 8, ETAGERE_BANQ["z1"], ETAGERE_BANQ["z1"] + 14),
    Cyl("plante", "plante", 22, Y_MUR_SUD - 12, 14, ETAGERE_BANQ["z1"] + 14, ETAGERE_BANQ["z1"] + 40),
]
# V11.45 : table type Véra (Les Gambettes) 70 × 70 × h 75, plateau stratifié rose poudré à chant noir, devant la
# banquette, à 10 de son assise ; plus de chaise. Suspension centrée au-dessus.
# V11.46 : angles arrondis (R 12) et pied central laqué blanc (colonne Ø 8, embase Ø 44) à la place des quatre pieds :
# on se glisse sur la banquette sans pied dans les jambes.
TABLE = dict(cote=70, x0=35, y0=BANQ["y0"] - 10 - 70)
TABLE.update(x1=TABLE["x0"] + 70, y1=TABLE["y0"] + 70, cx=TABLE["x0"] + 35, cy=TABLE["y0"] + 35)
MEUBLES += [
    Bloc("table", "plateau_vera", TABLE["x0"], TABLE["x1"], TABLE["y0"], TABLE["y1"], 74.8, 75, arrondi=12, coins="tous"),
    Bloc("chant", "chant_vera", TABLE["x0"], TABLE["x1"], TABLE["y0"], TABLE["y1"], 73, 74.8, arrondi=12, coins="tous"),
    Cyl("pied", "pied_table", TABLE["cx"], TABLE["cy"], 4, 2, 73),
    Cyl("pied", "embase_table", TABLE["cx"], TABLE["cy"], 22, 0, 2),
] + [
    Cyl("lampe", "suspension", TABLE["cx"], TABLE["cy"], 17.5, 140, 160),
    Cyl("fil", "fil_suspension", TABLE["cx"], TABLE["cy"], 0.4, 160, H - 3),
    Cyl("fil", "rosace_suspension", TABLE["cx"], TABLE["cy"], 5, H - 3, H),
]
SUSPENSION = dict(d=35, z0=140, z1=160)
# pan de mur derrière la banquette, du mur ouest au doublage de l'entrée : peinture vert profond (V11.45 ; le papier
# peint seventies essayé en V11.46 → V11.48 a été retiré en V11.49)
PAPIER_PEINT = None
MEUBLES.append(Bloc("peinture", "pan_banquette", BANQ["x0"], BANQ["x1"], Y_MUR_SUD - 0.3, Y_MUR_SUD, 0, H))
# plinthe au pied du mur de la fenêtre, de la rangée nord à la banquette : couleur des murs, h 8, épaisseur 1,5
PLINTHE = dict(h=8, ep=1.5)
MEUBLES.append(Bloc("socle", "plinthe_fenetre", 0, PLINTHE["ep"], P_CAISSON + FACADE, BANQ["y0"], 0, PLINTHE["h"]))
# et au pied du doublage de l'entrée, côté tableau noir, de la banquette à la baie
MEUBLES.append(Bloc("socle", "plinthe_doublage", ENTREE["poche"][0], ENTREE["poche"][1], Y_MUR_SUD - 10 - PLINTHE["ep"],
                    Y_MUR_SUD - 10, 0, PLINTHE["h"]))


def chaise(nom, x0, y0, dossier):
    """Chaise 42 × 42, assise h 45, dossier h 85 du côté indiqué (« n », « s », « e », « o »)."""
    x1, y1 = x0 + 42, y0 + 42
    for i, (px, py) in enumerate(((x0, y0), (x1 - 2, y0), (x0, y1 - 2), (x1 - 2, y1 - 2))):
        MEUBLES.append(Bloc("chaise", f"pied_{nom}_{i + 1}", px, px + 2, py, py + 2, 0, 42))
    MEUBLES.append(Bloc("chaise", f"assise_{nom}", x0, x1, y0, y1, 42, 45))
    d = {"n": (x0, x1, y0, y0 + 3), "s": (x0, x1, y1 - 3, y1), "o": (x0, x0 + 3, y0, y1), "e": (x1 - 3, x1, y0, y1)}
    MEUBLES.append(Bloc("chaise", f"dossier_{nom}", *d[dossier], 45, 85))


GLISSE = 0   # plus de chaise (V11.45)
# chaise seule, ajoutée aux meubles à découper de la version imprimable (V12.4), pas posée dans le projet
CHAISE = dict(l=42, p=42)

# ------------------------------------------------------------------ cellier : rangements
# La porte du cellier s'ouvre vers le cellier : rien n'est posé dans le balayage des vantaux.
EP = 2  # épaisseur des tablettes et montants


def rayonnage(nom, x0, x1, y0, y1, zs, montants_en_x=True, z1=COL_Z1, contenus=(), arrondi=0):
    """Montants toute hauteur aux deux bouts + tablettes aux hauteurs zs (dessus de tablette = z + EP).
    arrondi : tablettes arrondies à l'angle (x0, y1), montant de ce bout raccourci d'autant."""
    if montants_en_x:
        MEUBLES.append(Bloc("montant", f"montant_{nom}_1", x0, x0 + EP, y0, y1 - arrondi, 0, z1))
        MEUBLES.append(Bloc("montant", f"montant_{nom}_2", x1 - EP, x1, y0, y1, 0, z1))
        xi0, xi1, yi0, yi1 = x0 + EP, x1 - EP, y0, y1
    else:
        MEUBLES.append(Bloc("montant", f"montant_{nom}_1", x0, x1, y0, y0 + EP, 0, z1))
        MEUBLES.append(Bloc("montant", f"montant_{nom}_2", x0, x1, y1 - EP, y1, 0, z1))
        xi0, xi1, yi0, yi1 = x0, x1, y0 + EP, y1 - EP
    for k, z in enumerate(zs):
        MEUBLES.append(Bloc("etagere", f"etag_{nom}_{k + 1}", x0 if arrondi else xi0, xi1, yi0, yi1, z, z + EP,
                            contenu=contenus[k] if k < len(contenus) else "", arrondi=arrondi))
    return xi1 - xi0 if montants_en_x else yi1 - yi0


# V11.41 : deux balais accrochés au mur nord, dans les 40 libérés par le rayonnage (x 327 → 367) : l'un tête en bas,
# l'autre tête en haut, têtes 24 × 6 à plat.
# V13.0 : le rayonnage nord reprend ces 40 ; les balais passent sur le flanc nord de C1 (y 120), côté cellier, à l'écart
# de la porte et des tuyaux du LV (x 378).
# V13.6 : rayonnage sud retiré, les balais prennent sa place contre le mur nord du WC (y 100), sur un tasseau à 8 du mur
# pour passer devant les tuyaux du LV (y 95 et 99, h 20 → 27)
BALAIS = [(398, "bas"), (412, "haut")]          # (axe x, position de la tête)
Y_BALAIS = 100 - 8                              # face du tasseau ; les balais pendent vers le nord
for k, (xc, tete) in enumerate(BALAIS):
    zt = (8, 22) if tete == "bas" else (146, 160)
    zm = (22, 150) if tete == "bas" else (18, 146)
    zc = 148 if tete == "bas" else 120
    MEUBLES.append(Bloc("ratelier", f"crochet_balai_{k + 1}", xc - 1, xc + 1, Y_BALAIS - 3, Y_BALAIS, zc, zc + 3))
    MEUBLES.append(Cyl("manche", f"manche_balai_{k + 1}", xc, Y_BALAIS - 2.5, 1.2, *zm))
    MEUBLES.append(Bloc("balai", f"tete_balai_{k + 1}", xc - 12, xc + 12, Y_BALAIS - 6, Y_BALAIS, *zt))

# Rayonnage toute hauteur P40 contre le mur nord, jusqu'au mur de l'alcôve (x 434) : 6 tablettes, la première à h 60
# au-dessus des réseaux (h 43 → 50) qui passent dessous. La porte s'ouvrant côté cuisine (V11.35), il part de la
# cloison (x 327).
# Plus de rayonnage devant le ballon : nourrice, groupe de sécurité et chute restent accessibles directement.
# V11.41 : rayonnage raccourci de 40 côté entrée (il part de x 367, toujours arrondi) ; les balais prennent la place
# V13.0 : prolongé jusqu'au retour de cloison (x 327), allongé de 40 : son bout ouest est contre le mur (y 0 → 48),
# l'arrondi n'a plus d'angle à adoucir
_nord_x0 = 327
# Contenu de chaque tablette (de bas en haut) et du sol sous la première tablette.
RAYON_NORD = dict(x0=_nord_x0, x1=434, y0=0, y1=40, zs=[60, 96, 132, 168, 204, 238],
                  contenus=["packs d'eau, bouteilles, lait", "conserves, bocaux, sauces",
                            "réserves : pâtes, riz, farine, sucre", "biscuits, apéritif",
                            "papier, petit électroménager rare (raclette, gaufrier)", ""],
                  sol="pommes de terre, oignons (à l'ouest), aspirateur couché (à l'est)")
# V11.37 : angle côté entrée arrondi (R 30) : on ne se cogne pas en entrant ; V13.0 : contre le mur, plus d'arrondi
ARRONDI_NORD = 0
L_NORD = rayonnage("nord", RAYON_NORD["x0"], RAYON_NORD["x1"], RAYON_NORD["y0"], RAYON_NORD["y1"], RAYON_NORD["zs"],
                   contenus=RAYON_NORD["contenus"], arrondi=ARRONDI_NORD)
# V11.36 : second rayonnage toute hauteur contre le mur nord du WC (y 100), de C3 (x 382) au retour de l'alcôve
# (x 434), mêmes hauteurs de tablettes ; V11.39 : réduit à P19 pour affleurer le flanc nord de C3 (y 81), ce qui laisse
# 41 (y 40 → 81) entre les deux rayonnages pour atteindre la niche
# (ballon, nourrice, groupe de sécurité), au-dessus du coffre technique (h 30). L'entretien quitte le sol du rayonnage
# nord (denrées) pour celui-ci.
# V13.6 : rayonnage sud retiré (les balais prennent sa place) ; son contenu (sacs, pharmacie, piles, linge de réserve,
# vases ; seau et produits d'entretien au sol) reste à replacer
RAYON_SUD, L_SUD = None, 0

MEUBLES.append(Bloc("tech", "coffre_technique", 418, 434, 40, 62, 0, ZONE_TECH))

# V13.8 : aspirateur dans l'angle sud-est du cellier (contre le flanc de C1, à quelques cm du mur du WC et des tuyaux
# du LV qui y descendent à x 378) ; prise P12 au-dessus des tuyaux.
# V13.9 : traîneau avec sac type Rowenta Silence Force (RO6841EA : 47,7 × 27,3 × h 26,1).
# V13.10 : rangé sous la première tablette du rayonnage nord (h 60), au bout est, couché (h 26 : sous les tuyaux qui
# longent le mur à h 41 → 50 et à l'ouest de leur descente à x 422) ; tube et brosse posés au sol devant et à côté
ASPI = dict(x0=356, x1=420, y0=8, y1=39)
MEUBLES += [
    Bloc("aspirateur", "aspirateur_bloc", ASPI["x1"] - 47.7, ASPI["x1"], ASPI["y0"], ASPI["y0"] + 27.3, 0, 26.1),
    Bloc("aspirateur", "aspirateur_tube", ASPI["x1"] - 62, ASPI["x1"] - 2, ASPI["y1"] - 3.5, ASPI["y1"], 0, 3.5),
    Bloc("aspirateur", "aspirateur_brosse", ASPI["x0"], ASPI["x0"] + 7, ASPI["y1"] - 26, ASPI["y1"], 0, 6),
]

# ------------------------------------------------------------------ porte du cellier : angle d'ouverture
# Chaque vantail tourne de sa position fermée vers l'est (cellier) ou l'ouest (cuisine) ; il s'arrête 3° avant le
# premier obstacle à sa portée, sinon à 90°.
_DX = 1
_obstacles = [((382, 100), "le coin du mur nord du WC"), ((RAYON_NORD["x0"], RAYON_NORD["y1"]), "le rayonnage du mur nord")]
for v in CELLIER_VANTAUX:
    (hx, hy), (fx, fy), w = v["h"], v["ferme"], v["w"]
    sens = 1 if fy > hy else -1                  # 1 : le vantail pend vers le sud depuis sa charnière
    # la face côté cellier mène la rotation : ce qui y est accroché (saillie) touche l'obstacle plus tôt
    contacts = [(math.degrees(math.atan2((px - hx) * _DX, (py - hy) * sens)
                              - math.asin(min(1, v["saillie"] / math.dist((hx, hy), (px, py))))) - 3, nom)
                for (px, py), nom in _obstacles
                if math.dist((hx, hy), (px, py)) <= w + 1 and (px - hx) * _DX > 0 and (py - hy) * sens > 0]
    v["angle"], v["butee"] = min([(90, "")] + contacts)
    a = math.radians(v["angle"])
    v["ouvert"] = (hx + _DX * w * math.sin(a), hy + sens * w * math.cos(a))
# passage libre : baie moins les deux vantaux repliés et leur ferrure (≈ 2 : jeu au pivot, charnières) ; à confirmer
# avec le logiciel SLIDESOFT de Mantion
PASSAGE_CELLIER = round(PLIANTE["y1"] - PLIANTE["y0"] - 2 * PLIANTE["ep"] - 2)
# accès à la porte depuis la cuisine : du coin du plan de B5 (P62) à l'angle nord-ouest de C1
ACCES_CELLIER = math.dist((sur_bas(B_EVIER)[1], 62), (COL_X, JOUE_C2))
# devant la porte, entre le plan de B6 (P42) et les vantaux repliés (y 48)
JEU_B6_PORTE = BAIE_Y0 - P_PLAN_ETROIT
# passages dans le cellier : entre le rayonnage nord (P40) et le flanc de C1, et entre le rayonnage nord et les balais
# (V13.6 : contre le mur du WC), vers la niche
PASSAGE_ENTREE = JOUE_C2 - RAYON_NORD["y1"]
PASSAGE_BALAIS = Y_BALAIS - 6 - RAYON_NORD["y1"]

# ------------------------------------------------------------------ ouvertures de l'électroménager (plan seulement)
# abattant : emprise de la porte abattue (x0, x1, y0, y1) ; battant : charnière, bout fermé, bout ouvert à 90°.
_pl = sur_bas(B_PLAQUE)
OUVERTURES = [
    ("abattant", "LV", (COL_X - 58, COL_X, JOUE_C2, JOUE_C2 + 60)),              # LV en hauteur (C1), porte à h 66
    ("abattant", "four", (_pl[0], _pl[1], P_CAISSON + FACADE, P_CAISSON + FACADE + 52)),   # four sous la plaque
    # frigo : charnières au sud (côté C1), la porte se rabat vers le sud, on accède par le nord (côté évier)
    ("battant", "frigo", ((COL_X, COL_Y0 + 60), (COL_X, COL_Y0), (COL_X - 60, COL_Y0 + 60))),
] + [("tiroir", "banquette", (a, b, BANQ["y0"] - 2 - 35, BANQ["y0"] - 2)) for a, b in TIROIRS_BANQ]


def angle_frigo(obstacles):
    """Ouverture maximale (degrés) de la porte du frigo (façade 60 × 2, charnière à l'angle avant sud de C2) avant de
    toucher un des obstacles (noms de Blocs) : (angle, nom de l'obstacle). Estimation : une vraie charnière de meuble
    pivote un peu en retrait."""
    obs = [b for b in ENVELOPPE + MEUBLES if b.nom in obstacles]
    px, py = COL_X, COL_Y0 + 60
    for d10 in range(900, 1800):
        t = math.radians(d10 / 10)
        u, v = (-math.sin(t), -math.cos(t)), (math.cos(t), -math.sin(t))
        for b in obs:
            for x in (b.x0, b.x1):
                for y in (b.y0, b.y1):
                    a, e = (x - px) * u[0] + (y - py) * u[1], (x - px) * v[0] + (y - py) * v[1]
                    if 0 <= a <= 60 and 0 <= e <= FACADE:
                        return d10 / 10, b.nom
            for k in range(601):
                x, y = px + u[0] * k / 10, py + u[1] * k / 10
                if b.x0 < x < b.x1 and b.y0 < y < b.y1:
                    return d10 / 10, b.nom
    return 180, ""


_CADRE = ("galandage_montant", "fileur_c1", "joue_c1", "sud_est", "decroche_se", "sud_ouest", "galandage_caisson")
# (porte d'entrée fermée : le bout de la porte bute sur le vantail ; ouverte : sur le montant du galandage)
FRIGO_ANGLES = dict(entree_fermee=angle_frigo(_CADRE + ("entree_vantail",)), entree_ouverte=angle_frigo(_CADRE))

# ------------------------------------------------------------------ capacité, à la manière des cuisinistes
# Pas de volume : mètres linéaires de meubles, nombre de modules, tiroirs, plan de travail utile (hors évier et
# plaque), tablettes du cellier. Repères pour une cuisine d'environ 8 m² (la pièce fait 3,25 × 2,52 = 8,2 m² hors
# cellier) : 4 à 6 m linéaires de meubles bas + hauts, 8 à 11 meubles, 1,5 à 2,5 m de plan de travail utile ;
# implantation type : un linéaire de 2,50 à 3 m avec 6 ou 7 meubles.
_plaque_b = next(b for b in MEUBLES if b.role == "plaque")
_evier_b = next(b for b in MEUBLES if b.role == "evier")
_pt = next(b for b in MEUBLES if b.nom == "plan_nord")
_trous = sorted([(_plaque_b.x0, _plaque_b.x1), (_evier_b.x0, _evier_b.x1)])
_bords = [_pt.x0] + [v for t in _trous for v in t] + [X_CLOISON]   # V13.0 : plan de B6 compris (contigu)
PLAN_SEGMENTS = [(a, b) for a, b in zip(_bords[::2], _bords[1::2])]       # plan de travail libre, x0 → x1
_tiroirs = [b for b in MEUBLES if b.role in ("facade", "facade_col") and b.poignee == "tiroir"
            and not b.nom.startswith("tiroir_banquette")]
CAPACITE = dict(
    v11=dict(lin_bas=sum(LARGEURS_BAS), lin_hauts=sum(LARGEURS_HAUTS), lin_col=2 * 60 + C3_L,
             modules=(N_BAS, N_HAUTS, 2), tiroirs=len(_tiroirs), plan=PLAN_SEGMENTS, prof_plan=62,
             cellier=(RAYON_NORD["x1"] - RAYON_NORD["x0"], len(RAYON_NORD["zs"]), L_NORD, RAYON_NORD["y1"]),
             cellier_sud=None,   # V13.6 : rayonnage sud retiré
             menage=None,
             autres="banquette : 2 tiroirs ; étagère P25 au-dessus"),
    # Proposition 9 A (3d/cuisine_a.py) : bas 40 + 60 + 80 + 60 (x 9 → 249) et meuble café P28 de 52 ; hauts 40 + 40 + 60 ;
    # colonnes LV, frigo, four ; plan x 0 → 249 moins plaque (52 → 106) et évier monobloc avec égouttoir (161 → 247) ;
    # cellier 6 tablettes P30 de 38. Tiroirs : 3 + 3 + 1 sous la plaque + 1 sous le LV + 2 sous le four.
    p9a=dict(lin_bas=240 + 52, lin_hauts=140, lin_col=180, modules=(5, 3, 3), tiroirs=10,
             plan=[(0, 52), (106, 161), (247, 249)], prof_plan=62, cellier=(38, 6, 38, 30),
             autres="étagères ouvertes P30 2 × 109, étagère haute P25 de 140, porte d'entrée 3 × 62"),
)
REPERES = dict(lin=(400, 600), modules=(8, 11), plan=(150, 250), implantation=(250, 300, 6, 7), volume=(2, 2.5))


# Volume brut, en litres : largeur × profondeur du caisson × hauteur des façades de rangement (électroménager, socles et
# sous-évier exclus) ; cellier : largeur utile × profondeur × hauteur, de la première tablette au haut du rayonnage.
def litres(l, p, h):
    return l * p * h / 1000


VOLUMES = dict(
    v11=dict(cuisine=sum([litres(LARGEURS_BAS[B_TIROIRS - 1], P_CAISSON, CAISSON_H - SOCLE),
                          litres(LARGEURS_BAS[B_COULISSANT - 1], P_CAISSON, CAISSON_H - SOCLE),
                          litres(LARGEURS_BAS[B_ETROIT - 1], P_ETROIT, CAISSON_H - SOCLE),   # B6 (V13.0)
                          litres(LARGEURS_BAS[B_PLAQUE - 1], P_CAISSON, 12),
                          litres(LARGEURS_BAS[B_TIROIRS_2 - 1], P_CAISSON, CAISSON_H - SOCLE),
                          litres(sum(LARGEURS_HAUTS[1:]), P_HAUT, HAUT_Z1 - HAUT_Z0),   # H1 : hotte, hors volume
                          litres(60, P_CAISSON, (LV_Z0 - SOCLE) + (COL_Z1 - MO_Z1)), litres(60, P_CAISSON, COL_Z1 - 193),
                          2 * litres(40, 40, 30)]),
             cellier=litres(L_NORD, RAYON_NORD["y1"], COL_Z1 - RAYON_NORD["zs"][0])),
    p9a=dict(cuisine=sum([litres(40, 58, 72), litres(60, 58, 46), litres(80, 58, 72), litres(140, 33, 90),
                          litres(60, 58, 23 + 118), litres(59, 57, 45), litres(59, 57, 71 + 50), litres(52, 28, 72)]),
             cellier=litres(38, 30, 194)),
)
# contenu des rangements ouverts et des tiroirs, pour le tableau « Contenu des rangements »
CONTENU = [
    ("B1, coulissant de 20 à gauche de la plaque", "huiles, vinaigres, épices, sel (paniers en hauteur)"),
    ("B2, sous la plaque", "four encastré ; tiroir de 12 : plaques et grilles du four"),
    ("B3, à droite de la plaque", "3 tiroirs : ustensiles (18), poêles (27), casseroles (27)"),
    ("B4, à gauche de l'évier", "3 tiroirs : couverts (18), moules et plats à four (27), boîtes de conservation (27)"),
    ("B5, sous l'évier", "1 tiroir découpé autour du siphon : tri en 3 bacs (ordures, emballages, verre) et produits "
     "d'évier dans le bac avant"),
    ("B6, P40, contre la porte du cellier", "placard, une étagère (les tuyaux passent dans le fond) : café, "
     "détartrant, boîtes et films, torchons ; machine à café posée dessus"),
    ("Étagères à gauche de H1", ", ".join(ETAGERES_MUR["contenus"])),
    ("H1, au-dessus de la plaque", "hotte intégrée (groupe filtrant en recyclage) ; petit rangement au-dessus"),
    ("H2, au-dessus de B3", "épices, huiles, condiments"),
    ("H3", "petit-déjeuner (céréales, thé, café, confitures) et épicerie sèche du quotidien : pâtes, riz, farine"),
    ("H4, au-dessus de l'évier", "assiettes et bols"),
    ("H5, au-dessus de B6", "verres, tasses, café, thé"),
    ("C1, à côté de la porte du cellier", "tiroir bas : pastilles et sel du LV, torchons ; lave-vaisselle en hauteur ; "
     "micro-ondes ; porte haute : réserves"),
    ("C2", "porte au-dessus du frigo : grands plats, saladiers, plateaux (rarement utilisés)"),
    ("Banquette", "tiroir entre les pieds de la table : nappes, sets de table ; tiroir est : jeux, bougies"),
    ("Cellier nord, sol sous la 1re tablette", RAYON_NORD["sol"] + " (les tuyaux passent derrière, contre le mur)"),
] + [(f"Cellier nord, tablette h {z}", c) for z, c in zip(RAYON_NORD["zs"], RAYON_NORD["contenus"]) if c] + [
    ("Cellier, mur du WC (à la place du rayonnage sud)", "2 balais (un tête en bas, un tête en haut)"),
    ("Cellier nord, sous la 1re tablette, à l'est", "aspirateur traîneau avec sac (type Rowenta Silence Force), "
     "couché, tube et brosse au sol devant lui"),
]

# ------------------------------------------------------------------ matériaux (section Matériaux)
# (élément, matériau, précision, échantillon : couleur(s) « #… » ou image)
MATERIAUX = [
    ("Sol, ancienne chambre", "Parquet chêne huilé en bâtons rompus",
     "Lames 8 × 32, rangs horizontaux, pointes vers le nord.", "images/cuisine-sol-reference.png"),
    ("Sol, ancien cellier et ancien placard", "Ciment (béton ciré gris)", "À partir du nu de l'ancienne cloison (x 325).",
     ("#B9B6AF",)),
    ("Murs", "Blanc légèrement chaud, à peine beige",
     "Piste : Farrow & Ball Wimborne White (n° 239, LRV ≈ 90), blanc à sous-ton crème discret ; à peine plus chaud : "
     "Pointing (n° 2003). Teinte à l'écran approximative : à valider sur échantillon, au mur, à la lumière de la pièce.",
     ("#EFE9DC",)),
    ("Plinthes (socles des meubles bas et des colonnes, pied du mur de la fenêtre et du doublage de l'entrée)", "Couleur des murs", "Même blanc que les murs.", ("#EFE9DC",)),
    ("Fileurs", "Canopée aux deux bouts de la rangée basse, chêne miel au bout des hauts, couleur des murs au sud de C2",
     f"Fileurs de {ECART_OUEST} entre B1 et le mur ouest et entre B6 et le retour de cloison du cellier (plan de travail "
     f"de mur à mur) ; fileur de {X_CLOISON - FIN_HAUTS} en chêne entre H5 et le même retour ; fileur de 10 entre C2 et le montant du "
     "galandage (mur sud), qui ferme la poche de l'angle ; fileur chêne de " + str(FILEUR_C2) + " entre C2 et le mur sud (la porte du "
     "frigo s'ouvre à 90° sans toucher le fileur de l'entrée).", ("#3C524C", "#A8743F", "#EFE9DC")),
    ("Colonnes C1, C2 et meubles hauts H1 → H5", "Chêne miel, Plum Living", "Façades, joues et fileurs.", ("#A8743F",)),
    ("Meubles bas B1 → B6", "Laque Canopée, Plum Living",
     "Vert profond (nuancier Plum Living), posé sur caissons type IKEA METOD.", ("#3C524C",)),
    ("Crédence", "Zellige greige", "Carreaux 10 × 10 émaillés à la main, h 91 → 153, sur toute la rangée.",
     ("#C6BCAC", "#B9AE9D", "#A99D8B")),
    ("Plan de travail", "Effet béton blanc-gris", "Matière à définir (compact, céramique, quartz…) ; elle décide du "
     "type d'évier possible (sous plan ou à encastrer).", ("#D6D4CE", "#BDBBB5")),
    ("Évier et robinetterie", "Inox brossé", "Bac et mitigeur.", ("#C9C9C7",)),
    ("Poignées des façades bois (C1, C2, H1 → H5)", "Profilé toute longueur en chêne miel",
     "Même matière que la façade : sur toute la largeur des tiroirs, sur toute la hauteur des portes.", ("#A8743F", "#8A5A2B")),
    ("Poignées des meubles bas Canopée (B1 → B6)", "Barres en inox brossé",
     "Comme l'évier et la robinetterie.", ("#3C524C", "#C9C9C7")),
    ("Table", "Stratifié rose poudré à chant noir", "Plateau type Véra (Les Gambettes) carré 70 × 70 aux angles "
     "arrondis (R 12), sur un pied central laqué blanc à embase ronde, adapté à la banquette.", ("#D9BDBB", "#18181A")),
    ("Pan de mur derrière la banquette", "Peinture vert profond",
     "Du mur ouest au doublage de l'entrée, jusqu'au plafond : un vert profond proche de Canopée (piste : peinture murale "
     "Vert sauvage de Plum Living, à comparer sur échantillon avec la façade Canopée) relie le coin repas aux meubles bas.",
     ("#3F5A4E",)),
    ("Banquette", "Coffre couleur des murs, coussins velours ocre moutarde", "Coffre, dossier et façades des tiroirs "
     "dans le blanc des murs ; coussins d'assise et de dossier en velours côtelé ocre moutarde (retenu face au "
     "terracotta et au vieux rose).", ("#EFE9DC", "#C08A2E")),
]

# ------------------------------------------------------------------ électricité (V12.5, proposition ; section Électricité)
# Position en plan (x, y) du boîtier, z : hauteur de son axe depuis le sol fini. Rien n'est dans le modèle 3D.
# Points lumineux : (repère, nom, x, y, précision)
LUMIERES = [
    ("L1", "Plafonnier", 215, 145, "au plafond (boîtier DCL), centré sur la zone de travail (entre la rangée nord, les "
     "colonnes et l'entrée) : éclairage général"),
    ("L2", "LED sous les hauts", (DEPART_HAUTS + FIN_HAUTS) / 2, P_HAUT - 6,
     f"rubans déjà prévus sous H1 → H{N_HAUTS} ; alimentation (driver 24 V) dans le haut de H4, au-dessus des assiettes"),
    ("L3", "Suspension", TABLE["cx"], TABLE["cy"], "point de plafond déjà prévu (boîtier DCL), centré sur la table"),
    ("L4", "Cellier", 400, 60, "hublot ou réglette LED au plafond du cellier, sans détecteur : "
     "commandé par S2, à côté de la porte"),
]
# Interrupteurs : (repère, nom, x, y, z, emplacement, [(touche, lumière, fonctionnement)])
INTERRUPTEURS = [
    ("S1", "Entrée", 317, Y_MONTANT, 110,
     "sur le fileur à droite de la baie (x 312 → 322, face nord), côté poignée de la porte : plaque verticale 3 postes "
     "(le fileur fait 10 de large) ; le câble descend du plafond dans la poche fermée par le fileur",
     [("haut", "L1", "simple allumage"), ("milieu", "L2", "va-et-vient avec S2"),
      ("bas", "L3", "poussoir du variateur, avec S3")]),
    ("S2", "Bout du plan", X_CLOISON, 21, 110,
     "retour de cloison au nord de la porte du cellier (face ouest, x 320), au-dessus du plan de B6, à 19 du plan : "
     "plaque verticale 2 postes (V13.4 : il ne reste que 6 de mur entre le plan et la baie)",
     [("haut", "L2", "va-et-vient avec S1"),
      ("bas", "L4", "simple allumage, à voyant : on voit la lumière restée allumée porte fermée")]),
    ("S3", "Banquette", 0, 212, 105,
     "mur ouest, au bout de la banquette, à portée de main assis ; sur la même plaque que P11",
     [("", "L3", "poussoir du variateur, avec S1")]),
]
# Prises : (repère, x, y, z, socles, circuit, usage, emplacement) ; « dans » : au fond d'un meuble, invisible
PRISES = [
    ("P1", 12, 0, 110, 1, "plan", "petit électroménager", "crédence, à gauche de la plaque"),
    ("P2", 100, 0, 110, 2, "plan", "bouilloire, grille-pain, robot", "crédence, au-dessus de B3"),
    ("P3", 150, 0, 110, 2, "plan", "cafetière, mixeur", "crédence, à gauche de l'égouttoir"),
    ("P4", 55, 0, 225, 1, "autres", "hotte", "dans H1, au-dessus du groupe filtrant"),
    ("P5", 15, 0, 30, 1, "four", "four (sous la plaque)", "dans B1, au fond, sous les paniers"),
    ("P6", 15, 0, 60, 1, "plaque", "induction (sortie de câble 32 A)", "dans B1, au fond"),
    ("P7", COL_DOS, JOUE_C2 + 30, 40, 1, "lv", "lave-vaisselle", "dans C1, derrière le tiroir bas"),
    ("P8", COL_DOS, JOUE_C2 + 30, 205, 1, "plan", "micro-ondes", "dans C1, derrière la porte haute"),
    ("P9", COL_DOS, COL_Y0 + 30, 210, 1, "frigo", "réfrigérateur", "dans C2, derrière la porte haute"),
    ("P10", BANQ["x1"] - 17, Y_MUR_SUD, 175, 1, "autres", "enceinte audio",
     "mur sud, derrière l'enceinte posée sur l'étagère"),
    ("P11", 0, 224, 105, 2, "autres", "téléphone, ordinateur (dont 1 USB)", "mur ouest, au bout de la banquette, avec S3"),
    ("P12", 400, 0, 75, 1, "autres", "aspirateur, raclette, gaufrier",
     "cellier, mur nord, dans le rayonnage au-dessus de l'aspirateur, entre les tablettes h 60 et h 96"),
    ("P13", 290, 0, 135, 1, "autres", "machine à café", "crédence, au-dessus de B6 (au-dessus de la machine)"),
]
# Circuits proposés au tableau : (clé, nom, protection, contenu)
CIRCUITS = [
    ("eclairage", "Éclairage", "10 A, 1,5 mm²", "L1, L2, L3, L4"),
    ("plan", "Prises de la cuisine (circuit dédié)", "20 A, 2,5 mm², 6 socles au plus", "P1, P2, P3 au-dessus du plan (5 socles), P8 (6 socles)"),
    ("autres", "Autres prises", "20 A, 2,5 mm²", "P4, P10, P11, P12, P13 (6 socles)"),
    ("plaque", "Plaque à induction", "32 A, 6 mm²", "P6"),
    ("four", "Four", "20 A, 2,5 mm², circuit spécialisé", "P5"),
    ("lv", "Lave-vaisselle", "20 A, 2,5 mm², circuit spécialisé", "P7"),
    ("frigo", "Réfrigérateur", "20 A, 2,5 mm², circuit dédié (conseillé)", "P9"),
    ("ballon", "Ballon d'eau chaude", "existant, inchangé", "ballon du cellier (heures creuses)"),
]

# ------------------------------------------------------------------ rendus 3D (3d/v13/rendu.py, Blender Cycles → cuisine-v13-3d/)
# groupes de rendus (titre, [(vue, libellé du bouton)]) : libellé vide = vues distinctes, sans bouton de variante
RENDUS_GROUPES = [
    ("Isométrique depuis le sud-ouest", [("iso", "Jour"), ("iso_nuit", "Nuit")]),
    ("Isométrique depuis le nord-ouest", [("iso_no", "Peinture vert profond"), ("iso_no_hermione", "Papier peint Hermione")]),
    ("Dans la cuisine", [("entree", ""), ("fenetre", ""), ("banquette", ""), ("dos_cellier", "")]),
    ("Cellier", [("cellier", "")]),
]
RENDUS = [
    ("iso", "A · Isométrique", "Depuis le sud-ouest, murs ouest et sud et plafond coupés (ils portent toujours ombres et lumière)."),
    ("iso_no", "A' · Isométrique, autre sens", "Depuis le nord-ouest, murs nord et ouest, plafond et rangée nord "
     "coupés (elle se voit dans la vue A) : la banquette, l'entrée, les colonnes et la porte du cellier."),
    ("iso_no_hermione", "A'' · Essai papier peint Hermione", "Même vue que A', avec le papier peint intissé Hermione "
     "(4murs, cerise noire et vert-de-gris) sur le pan derrière la banquette au lieu du vert profond : essai, pas retenu "
     "dans le modèle. Motif estimé à 64 cm, répété en miroir dans la hauteur."),
    ("entree", "B · Depuis l'entrée", "Debout dans la baie d'entrée, vers la rangée nord et la fenêtre."),
    ("fenetre", "C · Depuis la fenêtre", "Debout devant la fenêtre, vers les colonnes, la porte du cellier ouverte et l'entrée."),
    ("banquette", "D · Assis sur la banquette", "Place est de la banquette, yeux à 120, vers la rangée nord et les colonnes."),
    ("cellier", "E · Entrée du cellier", "Entré dans le cellier, porte refermée derrière soi, dans l'axe du passage vers la niche : rayonnage nord à "
     "gauche, ballon au fond, rayonnage sud à droite."),
    ("dos_cellier", "F · Dos à la porte du cellier", "Debout devant la porte du cellier, vers la table et la banquette."),
    ("iso_nuit", "G · Isométrique de nuit", "Même vue que A, de nuit, tous les éclairages allumés : suspension, LED sous les "
     "hauts, cellier (pas de plafonnier dans le modèle)."),
]

# Avant / après : V11.34 (figée, commit fab26e3), mesurée avec le même code, pour le tableau de comparaison
AVANT = dict(version="V11.34", lin_bas=300, lin_hauts=240, lin_col=120, modules=(5, 4, 2), tiroirs=10, anglaise=0,
             plan=[(0, 68), (122, 187), (243, 305)], cellier_m2=1.46, tablettes_cm=6 * 101,
             volume_cuisine=2055, volume_cellier=739)
# version de chaque image de cuisine-v13-3d/ (rendus sur demande : `just v13-rendu`, ou une vue : `-- 256 iso`)
RENDUS_VERSION = {v: "V11.50" for v in ("iso", "entree", "fenetre", "banquette", "cellier", "dos_cellier", "iso_nuit", "iso_no")}
RENDUS_VERSION["iso_no_hermione"] = "V11.50"
# V13.2 : toutes les vues refaites (sauf l'essai Hermione, rendu à part)
RENDUS_VERSION.update({v: "V13.2" for v in ("iso", "entree", "fenetre", "banquette", "cellier", "dos_cellier", "iso_nuit", "iso_no")})   # essai papier peint (rendu à part, scratchpad)

# ------------------------------------------------------------------ historique (section Changements)
CHANGEMENTS = [
    ("V13.15", "12/10/2026",
     "Essai de porte roto retiré (page et plans détaillés) ; nouvelle section « Porte du cellier · Mantion Tango » "
     "après les coupes : principe, ouverture, pose, panneaux, ce qui reste à vérifier. Page « Porte du cellier » "
     "réduite à la pliante. Sur ordinateur, sommaire repliable à gauche."),
    ("V13.14", "12/10/2026",
     "Porte du cellier : modèle réel. Ferrure Mantion Tango (TANGO40-120 : rail alu sous le linteau, pivots au nord, "
     "pas de rail au sol, 40 kg par panneau) et deux panneaux de 19 à faire découper (≈ 33,2 × 197,6), cotes tirées de "
     "la notice. Vantaux de 1,9 au lieu de 2,5 : passage libre ≈ 61 au lieu de 60. Page « Porte du cellier » : fiche "
     "du modèle et alternative clé en main (Centimetre, porte de placard pliante sur mesure, avec rail au sol)."),
    ("V13.13", "12/10/2026",
     "Page « Porte du cellier » : roto d'autres marques (Celegon, Ferplac, porte Forte 6) comparées à la Garofoli et à la "
     "pliante, à baie égale. Aucune ne fait mieux que la pliante : la meilleure (Celegon) laisse ≈ 54 de passage dans la "
     "baie de 67, contre 60. La pliante reste retenue ; plan et modèle inchangés."),
    ("V13.12", "11/10/2026",
     "Page à part « Porte du cellier » (cuisine-v13-porte-cellier.html, lien à droite du titre « Plan ») : vues de "
     "dessus agrandies et cotées de l'angle B6 / mur neuf / C1, placement et ouverture de la porte pliante (fermée, en "
     "cours, ouverte) et de la roto Garofoli (fermée, ouverte), détail du montant nord, tableau comparatif."),
    ("V13.11", "11/10/2026",
     "Essai dessiné à part, non retenu : porte du cellier Garofoli IO2023 à roto-translation L 600 (section « Essai : "
     "porte roto Garofoli »), comparée à la porte pliante actuelle. Le plan, les coupes et le modèle ne changent pas."),
    ("V13.10", "11/10/2026",
     "Aspirateur rangé sous la première tablette du rayonnage nord du cellier, au bout est, couché (h 26, sous les "
     "tuyaux), tube et brosse au sol devant lui ; pommes de terre et oignons à l'ouest. Prise P12 au-dessus, dans le "
     "rayonnage (h 75). L'angle sud-est du cellier redevient libre."),
    ("V13.9", "11/10/2026",
     "Cellier : l'aspirateur est un traîneau avec sac type Rowenta Silence Force (environ 48 × 27 × h 26), rangé debout "
     "en position parking dans l'angle sud-est, tube et brosse clipsés à côté ; passage de 47 devant lui."),
    ("V13.8", "11/10/2026",
     "B6 : un placard (porte, une étagère) au lieu de 3 tiroirs, machine à café posée sur son plan (prise P13 au-dessus). "
     "Aspirateur balai sur sa station, au sol dans l'angle sud-est du cellier, contre C1 ; sa prise (P12) passe sur le "
     "mur du WC, derrière lui."),
    ("V13.7", "11/10/2026",
     "Angle sud-est : le fileur couleur des murs entre C2 et le montant de l'entrée affleure maintenant le montant "
     "(il dépassait de 2 devant) ; le fileur chêne de C2 descend jusqu'à lui ; la joue enfermée derrière (entre C2 et le "
     "décroché, invisible) est retirée. Porte du cellier : fermée, les deux vantaux sont dans l'épaisseur de la "
     "cloison, au nu du mur côté cuisine (ils étaient 2,5 devant)."),
    ("V13.6", "11/10/2026",
     "Cellier : rayonnage sud (P19, contre le mur du WC) retiré ; les deux balais y sont accrochés, sur un tasseau à 8 "
     "du mur pour passer devant les tuyaux du LV, au lieu du flanc de C1. Passage de 46 entre le rayonnage nord et les "
     "balais pour atteindre la niche. Le contenu de l'ancien rayonnage sud (sacs, pharmacie, piles, linge de réserve, "
     "vases, entretien au sol) reste à replacer."),
    ("V13.5", "11/10/2026",
     "Fileur entre C2 et le mur sud réduit de 10 à 5 : C1 y 115 → 175, C2 y 175 → 235 ; baie du cellier 67 (y 48 → "
     "115, vantaux de 33, passage 60). Ouverture de la porte du frigo calculée sur le plan : environ 100° porte "
     "d'entrée fermée (le bout de la porte touche le vantail d'entrée), 117° porte d'entrée ouverte (montant du "
     "galandage)."),
    ("V13.4", "11/10/2026",
     "Mur neuf du cellier réduit de 45 à 40 (retour de cloison y 0 → 48) : baie 62 (y 48 → 110), vantaux pliants de "
     "30,5, passage 55 ; 6 entre le plan de B6 et les vantaux repliés. Interrupteur S2 remonté au-dessus du plan de B6 "
     "(sur le retour de cloison) ; prise P12 du cellier sur le mur nord, dans le rayonnage. Rendus 3D non refaits "
     "(V13.2 : porte encore à 45)."),
    ("V13.3", "11/10/2026",
     "Plan : la baie (57) et le passage libre (50) de la porte du cellier sont cotés côte à côte, côté cellier, juste "
     "derrière la porte (la cote du passage, côté cuisine, se perdait dans le triangle d'activité)."),
    ("V13.2", "11/10/2026",
     "Fileurs de 10 aux deux bouts de la rangée basse (5 au mur ouest et 15 au retour de cloison auparavant) : B1 → B6 "
     "décalés de 5 vers l'est (x 10 → 310), hauts d'autant (x 30 → 310, fileur de 10 à l'est de H5, étagères ouvertes "
     "x 0 → 28). Tous les rendus refaits (sauf l'essai de papier peint Hermione) ; vue F replacée au milieu de la "
     "nouvelle porte du cellier, vue E dans l'axe du passage vers le ballon."),
    ("V13.1", "11/10/2026",
     "Fileur chêne de 10 entre C2 et le mur sud : ouverte à 90°, la porte du frigo ne touche plus le fileur de "
     "l'entrée. C1 et C2 remontent de 10 (C1 y 110 → 170, C2 y 170 → 230) ; le mur neuf du cellier reste à 45 et la "
     "baie passe de 67 à 57 (vantaux pliants de 28, passage 50)."),
    ("V13.0", "11/10/2026",
     "Nouvelle page de travail cuisine-v13.html, repartie de la V12.7 (figée ; elle remplace V11.50 dans les versions "
     "comparables, l'ancienne page V12 est archivée). C3 supprimée. Porte du cellier décalée de 45 vers le sud : le "
     "retour de cloison s'allonge de 45 (y 0 → 53) et la baie va jusqu'au flanc nord de C1, soit 67 au lieu de 73 "
     "(vantaux pliants de 33, passage 60) pour que C1 (LV) et C2 (frigo) tiennent entre la baie et le décroché du mur "
     "sud (C1 y 120 → 180, C2 y 180 → 240). Nouveau B6 de 40 en P40 (3 tiroirs) entre B5 et le retour de cloison, "
     "avec un fileur Canopée de 15 : plan de travail de mur à mur, P42 au-dessus de B6 ; le coffre des réseaux "
     "disparaît (tuyaux dans le fond de B6). Nouveau H5 de 40 au-dessus de B6, même profondeur que H4, fileur de 15 "
     "jusqu'au mur. Cellier : rayonnage nord prolongé jusqu'au nouveau mur (x 327 → 434, sans arrondi, il est contre "
     "le mur) ; balais sur le flanc nord de C1. Interrupteur S2 sur le retour de cloison, prise P12 de l'autre côté. "
     "Rendus 3D non refaits (V11.50)."),
    ("V12.7", "09/10/2026",
     "Cellier : interrupteur au lieu du détecteur de présence ; S2 (mur nord, à côté de la porte) passe à 2 touches, "
     "LED du plan de travail en haut, lumière du cellier en bas (à voyant)."),
    ("V12.6", "09/10/2026",
     "Électricité vérifiée (NF C 15-100, sources en note) : une prise double compte pour 2 socles (5 socles au-dessus "
     "du plan, il en faut 4) ; le circuit dédié de la cuisine (20 A, 6 socles au plus) reçoit P1 → P3 et le micro-ondes "
     "(P8) ; boîtiers DCL pour le plafonnier et la suspension ; raison du détecteur au cellier expliquée."),
    ("V12.5", "09/10/2026",
     "Section « Électricité » : proposition de points lumineux (plafonnier, LED sous les hauts, suspension, cellier à "
     "détecteur), de prises (crédence, électroménager dans les meubles, banquette, enceinte, cellier) et "
     "d'interrupteurs (entrée, bout du plan, banquette), avec un plan, une élévation du mur nord, le tableau « quel "
     "interrupteur allume quoi » et les circuits proposés."),
    ("V12.4", "09/10/2026",
     "Version imprimable en noir et blanc (bouton à droite du titre « Plan ») : A4 paysage à l'échelle 1:20, pièce "
     "meublée, pièce vide et meubles à part à découper pour essayer d'autres positions, avec une chaise 42 × 42."),
    ("V12.3", "09/10/2026",
     "Capacité : dépasser le haut d'un repère n'est plus une erreur ; seul ce qui est en dessous passe en rouge (aussi "
     "dans les versions figées)."),
    ("V12.2", "09/10/2026",
     "Capacité : cellules en vert dans le repère d'une cuisine de 8 m², en rouge en dehors, et ligne « Meubles bas + "
     "hauts » (le repère porte sur la somme). Rendus 3D groupés avec un titre par groupe ; une même vue en variantes "
     "(jour / nuit, peinture / papier peint) se choisit par des boutons. Plans et coupes sans défilement horizontal "
     "sur mobile."),
    ("V12.1", "09/10/2026",
     "Tableaux « Avant / après » et « Capacité » fusionnés en un seul (V11.34, version affichée, écart, proposition 9 A, "
     "repères), y compris dans les versions figées V11.49 et V11.50 ; implantation du mur nord corrigée (2,65 m, la "
     "rangée va de x 5 à 265). Bouton « Changements » dans la barre pour afficher ou masquer l'historique des versions."),
    ("V12.0", "09/10/2026",
     "Nouvelle page de travail cuisine-v13.html, repartie de la V11.50 à l'identique (modèle, plan, rendus). "
     "V11.49 et V11.50 restent comparables en versions figées ; l'ancienne page V11 est archivée."),
    ("V11.50", "08/10/2026",
     "Tuyaux du LV : ils longent le mur nord du WC sous le rayonnage sud (plus de traversée du cellier) ; la vidange "
     "rejoint directement la chute. "
     "Plaque à induction classique (plus d'aspiration intégrée) avec un four encastré dessous (B2) et une hotte "
     "intégrée dans un meuble haut au-dessus (nouveau H1, hauts x 25 → 265). Colonnes du nord au sud : C1 lave-vaisselle "
     "en hauteur + micro-ondes (à la place du four), C2 frigo, C3 tiroirs à l'anglaise (C1 et C3 inversés). B4 devient "
     "un meuble à tiroirs (couverts, moules, boîtes). Réseaux du LV par le cellier, contre le dos de C1. Coussins de la banquette en velours ocre moutarde (mise à jour), rendus refaits. C3 : maxi tiroir coulissant (il se tire, ne pivote pas). Plinthe couleur des murs (h 8) au pied du mur de la fenêtre, entre la rangée nord et la banquette, et au pied du doublage de l'entrée ; rendus refaits. Essai de papier peint Hermione (4murs) sur le pan de la banquette : vue A'' ajoutée aux rendus."),
    ("V11.49", "08/10/2026",
     "Papier peint retiré : le pan de mur derrière la banquette revient à la peinture vert profond. Rendu F (dos à la "
     "porte du cellier) refait."),
    ("V11.48", "08/10/2026",
     "Papier peint : marge de fond chocolat autour de chaque fleur, les fleurs ne se touchent plus (environ 16 cm "
     "entre deux fleurs)."),
    ("V11.47", "08/10/2026",
     "Papier peint recoloré dans la gamme de la table (chocolat, rose pâle, rose poudré, vieux rose, bordeaux) et "
     "répété en miroir dans les deux sens pour former des fleurs à quatre pétales (environ 80 cm), une fleur centrée "
     "sur le pan au-dessus du dossier."),
    ("V11.46", "08/10/2026",
     "Papier peint seventies (cercles jaune, orange, rouille sur fond brun) sur le pan de mur derrière la banquette ; "
     "table Véra 70 × 70 aux angles arrondis (R 12) sur un pied central à embase, tiroirs de la banquette remis de part "
     "et d'autre (au-dessus de l'embase)."),
    ("V11.45", "08/10/2026",
     "Banquette prolongée jusqu'au retour du doublage de l'entrée (x 0 → 140, 2 places larges, 3 serrées), tiroirs "
     "replacés entre les pieds de la table et à l'est ; table ronde remplacée par la table type Véra 70 × 70 (rose "
     "poudré, chant noir, pieds tube blanc) ; chaise retirée ; proposition de peinture vert profond pour le pan de mur "
     "derrière la banquette. Rendu F (dos à la porte du cellier) refait."),
    ("V11.44", "08/10/2026",
     "Porte pliante du cellier : troisième état « mi-ouverte » sur le plan (vantaux en V, pivot tourné de 60°) ; le "
     "bouton passe de ouverte à mi-ouverte puis fermée."),
    ("V11.43", "08/10/2026",
     "B1 et B3 inversés : coulissant de 20 contre le fileur ouest, plaque en B2, tiroirs ustensiles / poêles / "
     "casseroles en B3. H1 revient à 60 pour garder les joints des hauts au droit des bas (hauts x 85 → 265, "
     "étagères ouvertes x 0 → 83)."),
    ("V11.42", "08/10/2026",
     "B2 revient à 60 ; B1 et B2 inversés (tiroirs ustensiles en B1, plaque en B2) ; coulissant de 20 entre la plaque et "
     "le LV (huiles, épices) : la rangée devient B1 tiroirs, B2 plaque, B3 coulissant, B4 LV, B5 évier (x 5 → 265). "
     "H1 (80) couvre la plaque et le coulissant, joints des hauts toujours au droit des bas."),
    ("V11.41", "08/10/2026",
     "B2 passe à 80 en prenant 20 sur le fileur du mur ouest (25 → 5) ; H1 suit à 80 pour garder les joints des hauts "
     "au droit des bas (étagères x 0 → 63). Cellier : rayonnage nord raccourci de 40 côté entrée (x 367 → 434, "
     "toujours arrondi) ; deux balais accrochés au mur nord dans l'espace libéré, devant les tuyaux."),
    ("V11.40", "08/10/2026",
     "Étagères ouvertes prolongées du mur ouest jusqu'à H1 (x 0 → 83). Porte du cellier : porte de placard pliante à "
     "deux vantaux de 36, pivot au nord ; elle se replie côté cuisine contre le retour de cloison (passage 66)."),
    ("V11.39", "08/10/2026",
     "Variante ballon extra-plat retirée (ballon rond au cellier seulement). Rayonnage sud du cellier réduit à P19 "
     "pour affleurer le flanc de C3 : 41 entre les deux rayonnages. Balais retirés. B1 et B2 inversés : plaque sur "
     "B1, tiroirs ustensiles / poêles / casseroles en B2. Hauts réalignés sur les joints des bas (x 85 → 265, au-dessus "
     "de B2, B3, B4) et 3 étagères ouvertes de 40 en chêne à gauche de H1 (x 45 → 85, P25)."),
    ("V11.38", "08/10/2026",
     "Porte du cellier accordéon (sans dormant, rail côté cuisine, paquet replié d'environ 14 au nord) : passage 59, "
     "rien ne balaie ; rangée nord décalée de 10 vers l'est (fileur ouest 25, x 25 → 265), accès à la porte ≈ 60. "
     "Cotes des passages du cellier : 35 entre les deux rayonnages, 41 entre le rayonnage nord et C3."),
    ("V11.37", "08/10/2026",
     "Fileur du mur ouest porté à 15 (rangée x 15 → 255, plan de travail toujours jusqu'au mur) ; évier 1 bac + "
     "égouttoir à gauche (100 × 50), l'égouttoir passant au-dessus de B3 ; rayonnage nord du cellier arrondi (R 30) "
     "côté entrée. Rendu isométrique refait (les autres vues restent en V11.34)."),
    ("V11.36", "08/10/2026",
     "Porte du cellier : paumelles au nord, elle s'ouvre côté cuisine et se rabat contre le mur nord (devant le coffre "
     "des réseaux) au lieu de se mettre en travers devant C3. Cellier réorganisé : rayonnage nord prolongé jusqu'à la "
     "cloison (x 327), second rayonnage toute hauteur P25 contre le mur du WC (x 382 → 434), l'entretien séparé des "
     "denrées. Tableau avant / après (V11.34 → V11.36). Rendus 3D inchangés (V11.34)."),
    ("V11.35", "08/10/2026",
     "Nouvel essai : B5 et H4 retirés (rangée x 5 → 245, 3 hauts) ; porte du cellier de 63 au plus près du mur nord "
     "(retour de cloison de 8 pour les réseaux, baie y 8 → 81), ouvrant côté cuisine (vers le cellier elle balaierait "
     "le rayonnage nord), paumelles au sud ; C3 de 39 au nord du frigo, toute hauteur, porte basse sur 5 tiroirs à "
     "l'anglaise (couverts, verres et tasses, café et thé, boîtes et films, torchons et sacs) ; réseaux dans un coffre "
     "bas couleur des murs (P8, h 55) entre B4 et la cloison ; balais sur le flanc nord de C3."),
    ("V11.34", "08/10/2026",
     "Crédence en zellige greige (retenu parmi blanc cassé, gris chaud et greige) ; hauts en chêne miel conservés "
     "(chêne fumé écarté) ; rendus refaits. La proposition 9 V2 A figée reçoit ses rendus 3D Canopée."),
    ("V11.33", "08/10/2026",
     "Plan : le plan de travail, prolongé jusqu'au mur ouest en V11.32, est dessiné sur un fond opaque (le parquet "
     "apparaissait à travers au droit du fileur de 5)."),
    ("V11.32", "08/10/2026",
     "Rangée nord à 5 du mur ouest (x 5 → 305) avec un fileur Canopée de 5, plan de travail prolongé jusqu'au mur ; "
     "fileur couleur des murs entre C1 et le montant du galandage (mur sud), qui ferme la poche de l'angle sud-est ; "
     "banquette couleur des murs, coussins terracotta. Rendus : chaise type Cesca (tube chromé, cadre chêne, cannage), "
     "balais, bac de l'évier (inox brossé, bonde) ; vues F (dos à la porte du cellier) et G (isométrique de nuit)."),
    ("V11.31", "08/10/2026",
     "Rendus 3D (Blender Cycles, 3d/v13/rendu.py) : isométrique, depuis l'entrée, depuis la fenêtre, assis sur la "
     "banquette, entrée du cellier ; matériaux de la section Matériaux, poignées, crédence, fenêtre et coussins "
     "construits depuis les cotes du modèle ; 21 juin, 17 h, suspension et LED allumées."),
    ("V11.30", "08/10/2026",
     "Murs blanc légèrement chaud (piste Farrow & Ball Wimborne White) et plinthes de la couleur des murs : section "
     "Matériaux, socles dessinés dans ce blanc dans les coupes."),
    ("V11.29", "08/10/2026",
     "Poignées : profilé toute longueur en chêne miel sur les façades bois (colonnes et hauts), barres en inox brossé sur "
     "les bas Canopée ; dessinées ainsi dans les coupes et ajoutées à la section Matériaux. Coupe C-C : poignée du frigo "
     "corrigée, côté nord (charnières au sud)."),
    ("V11.28", "08/10/2026",
     "Section Matériaux : parquet bâtons rompus (ancienne chambre), ciment (ancien cellier et placard), chêne miel "
     "Plum Living (colonnes et hauts), laque Canopée Plum Living (bas), crédence zellige blanc / gris, plan effet béton "
     "blanc-gris (matière à définir), évier et robinetterie inox brossé, table rose poudré ronde Ø 80, banquette à choisir."),
    ("V11.27", "08/10/2026",
     "Réseaux en pose type IKEA METOD (pas de vide technique, 1 cm de jeu derrière les caissons) : le LV est repiqué "
     "sur l'évier (vidange sur le siphon, robinet d'arrêt dans B4), plus aucun tuyau derrière sa niche ; à l'est de "
     "l'évier, évacuation (à 4 du mur) et alimentation passent derrière les tiroirs de B5, raccourcis à P50, dans le "
     "fond du caisson découpé sur 8. Texte des réseaux corrigé (hauteurs du modèle : h 43 sous le siphon → h 25 à la chute)."),
    ("V11.26", "07/10/2026",
     "Coupe C-C : bouton pour afficher la porte du cellier normale ou en transparence."),
    ("V11.25", "07/10/2026",
     "Coupe C-C : porte du cellier, dormant et linteau dessinés en transparence pour montrer le fond du cellier "
     "(rayonnage ménage, aspirateur et contenu des tablettes, ou ballon)."),
    ("V11.24", "07/10/2026",
     "Zone technique de 30 au sol dans la niche du cellier (chute basse, dernier étage) : tuyaux de la niche sous h 30, "
     "coffre technique dans l'angle. Variante ballon extra-plat : rayonnage ménage P50 sur toute la niche, plancher "
     "démontable à h 30 portant l'aspirateur traîneau (bloc et tuyau), 5 tablettes au-dessus. Volume de rangement "
     "remis dans le tableau de capacité. Plante sur l'étagère de la banquette."),
    ("V11.23", "07/10/2026",
     "Variante ballon extra-plat : rayonnage ménage P25 au fond de la niche, contre le mur est (y 46 → 88, avant la "
     "chute), aspirateur debout sur son socle juste devant. Coupe D-D regard vers l'est."),
    ("V11.22", "07/10/2026",
     "Variante (bouton) : ballon rond du cellier remplacé par un ballon extra-plat Atlantic Linéo 80 L (130 × 49 × 29) "
     "fixé dans le WC ; la niche du cellier reçoit l'aspirateur balai sur sa station et un rayonnage P25 de produits "
     "ménagers contre le mur du WC."),
    ("V11.21", "07/10/2026",
     "Option cave à vin retirée. Contenu du cellier, tablette par tablette, écrit sur la coupe A-A et dans le tableau. "
     "Capacité exprimée comme les cuisinistes (mètres linéaires, nombre de meubles, tiroirs, plan de travail utile, "
     "tablettes du cellier) au lieu du volume, comparée à la proposition 9 A et aux repères d'une cuisine de 8 m². "
     "Petit-déjeuner dans H2 (au lieu du cellier)."),
    ("V11.20", "07/10/2026",
     "Option cave à vin ESSENTIELB ECV28-ca1 (45 × 73 × 52,5, 28 bouteilles) au bout est du rayonnage du cellier, "
     "sur une tablette renforcée à h 60 ; bouton pour l'afficher ou non. Contenu des tiroirs, portes et rayonnages "
     "écrit sur les coupes et détaillé dans un tableau."),
    ("V11.19", "07/10/2026",
     "Organisation A retenue (tout en tiroirs), variantes B et C retirées. Interrupteur pour ouvrir et fermer la porte "
     "d'entrée sur le plan. Explications sous les plans masquées par défaut, bouton pour les afficher. Suspension "
     "au-dessus de la table (Ø 35, h 140 → 160)."),
    ("V11.18", "07/10/2026",
     "Étagère P25 au-dessus de la banquette (h 160) avec l'enceinte audio. Ruban LED sous H1 → H4. Deux tiroirs sous "
     "la banquette, de part et d'autre du pied de la table. Banquette : deux places. Trois organisations des façades à "
     "comparer (tout en tiroirs, portes et étagères, tiroirs côté cuisson et hauts relevables), électroménager inchangé."),
    ("V11.17", "07/10/2026",
     "Porte du cellier à un seul vantail de 63, poignée à droite (côté frigo), paumelles côté cloison ; montant "
     "contre le frigo supprimé, dormant directement contre la joue du frigo ; cloison prolongée jusqu'à y 45 pour "
     "garder la baie de 73. Balais tête en bas et tête en haut, rapprochés du mur du WC."),
    ("V11.16", "07/10/2026",
     "Porte du cellier 20 + 43 (et non 20 + 63) : cloison jusqu'à y 38. Les deux balais passent de la porte au flanc "
     "nord du frigo, derrière le grand vantail ouvert. Le rayonnage du mur nord repart de la cloison (x 329 → 434)."),
    ("V11.15", "07/10/2026",
     "Porte du cellier au standard : grand vantail de 63 (la plus petite largeur standard) et petit de 20, cloison "
     "raccourcie à y 18. Rayonnage devant le ballon et trappe supprimés ; rayonnage du mur nord prolongé jusqu'au "
     "mur de l'alcôve (x 434). Râtelier supprimé : deux balais accrochés derrière le grand vantail. Coupe D-D "
     "supprimée."),
    ("V11.14", "07/10/2026",
     "Four (C1) et frigo (C2) passent au mur est, à la place de E2 et E1 (C2 y 120 → 180, C1 y 180 → 240, façades "
     "x 322) ; E1 et E2 supprimés. Frigo charnières au sud. Micro-ondes encastrable au-dessus du four (h 148 → 186). "
     "Chaise à l'est de la table. Mur nord : induction sur B2, LV en B3, évier sur B4 avec les poubelles dessous, B5 "
     "libre. Porte d'entrée à galandage (vantail 83 × 204), caisson dans un doublage de 10 à l'ouest de la baie, avec "
     "tableau noir et zone aimantée sur sa face cuisine. Cellier : retour de la cloison supprimé, cloison raccourcie de "
     "20 (y 0 → 43), porte dans son axe, jusqu'au flanc nord du frigo, ouverture vers le "
     "cellier. Rayonnage toute hauteur P40 contre le mur nord (x 329 → 404), rayonnage P30 devant le ballon "
     "(y 18 → 98) avec une trappe d'accès amovible de 76 en bas ; le cellier entre dans le volume de rangement fermé "
     "(V11 et proposition 9 A). Alimentation : remontée derrière la trappe (x 408). "
     "Chute replacée contre le mur nord du WC, sous le ballon. Porte du "
     "cellier redessinée avec dormant, paumelles et vantaux de 4 : double battant tiercé 20 + 38 (variante C retenue "
     "parmi trois), deux interrupteurs pour l'ouvrir et la fermer sur le plan. Coin des balais derrière le petit "
     "battant (râtelier sur la cloison). Tuyaux le long des murs. Joues de finition sur les flancs visibles des colonnes et des hauts. Cote du "
     "passage devant la porte du cellier."),
    ("V11.13", "06/10/2026",
     "Coupe C-C sur le mur est (regard vers l'est). Bouton de retour à l'index. Proposition 9 V2, variante A, table "
     "carrée, ajoutée aux versions figées pour comparaison."),
    ("V11.12", "06/10/2026",
     "Porte d'entrée battante (vantail 73, charnières à l'est, ouverture vers la cuisine) à la place de la coulissante. "
     "Four et frigo contre le mur sud (façades y 192), couloir du vantail supprimé. E2 devient un placard toute hauteur P40. "
     "Cloison du cellier déplacée à 10 de B5 (x 320 → 327) avec retour contre le nord de E1 ; baie de 50 face ouest "
     "(y 63 → 113), porte à définir ; cellier agrandi."),
    ("V11.11", "06/10/2026",
     "Four et frigo décalés de 8 vers l'est, alignés sur le bord ouest du vantail d'entrée (x 106 → 226) ; banquette "
     "allongée d'autant (x 0 → 106), table recentrée. Plaque sur B3, LV en B4, évier sur B5 avec les poubelles dessous. "
     "B6 et H5 supprimés (rangée nord x 10 → 310, hauts x 40 → 280)."),
    ("V11.10", "06/10/2026",
     "Four (C1) et frigo (C2) déplacés vers l'est, x 98 → 218, à 10 du montant ouest de la porte d'entrée ; "
     "avancés de 12 (façades y 180) : le vantail coulisse derrière eux. Banquette du mur ouest à C1 (98 × 50), "
     "table Ø 80 devant, une chaise en face. Mur est : deux meubles bas de 60 en P40 (E1, E2), plan de travail."),
    ("V11.9", "06/10/2026",
     "Cotes de la porte d'entrée coulissante : baie 78 × 204, vantail 82 × 210, position ouverte x 144 → 226 "
     "(plan et coupe B-B). Version figée : bouton « V11.9 figée » en tête de page pour comparer."),
    ("V11.8", "06/10/2026",
     "Meubles hauts remontés de 5 (h 153 → 243, 62 au-dessus du plan de travail), fileur de 7 jusqu'au plafond. "
     "Colonnes C1 et C2 remontées d'autant (dessus aligné sur les hauts), avec le même fileur."),
    ("V11.7", "06/10/2026",
     "Plan : surface et volume du cellier, diamètre de la table, cotes four (C1) / B1. Traits de coupe A et B "
     "semi-transparents."),
    ("V11.6", "06/10/2026",
     "Table ronde Ø 80 et deux chaises dans l'angle sud-est. Ouvertures du LV, du four et du frigo. "
     "Comparaison des volumes de rangement avec la proposition 9, variante A."),
    ("V11.5", "06/10/2026",
     "LV en B5, poubelles en B4 (sous l'évier). Triangle d'activité frigo / évier / plaque. Réseaux : alimentation "
     "depuis la nourrice du ballon, évacuations de l'évier et du LV vers la chute. Cellier refermé par une cloison "
     "de 7 dans le prolongement du nu ouest du WC (x 382 → 389), baie de 72 (y 28 → 100), porte à définir."),
    ("V11.4", "06/10/2026",
     "Mur sud : colonnes C1 (four à h 88 → 148) et C2 (frigo intégrable) de 60, P60, h 238, x 10 → 130, "
     "à l'ouest de la porte d'entrée. Coupe B-B (regard vers le sud) ajoutée."),
    ("V11.3", "06/10/2026",
     "Plan de travail 4 (P62) sur les 6 meubles bas. Induction 60 à aspiration intégrée sur B2 (x 70 → 130), "
     "évier inox 1 bac 56 × 50 sur B4 (x 190 → 250). Meubles bas renommés B1 → B6."),
    ("V11.2", "06/10/2026",
     "Bâtons rompus dans l'autre sens. 6e meuble bas de 60 (x 310 → 370). 5 meubles hauts de 60 (P35, "
     "h 148 → 238), décalés d'un demi-meuble : x 40 → 340, à partir du milieu du premier meuble bas."),
    ("V11.1", "06/10/2026",
     "Sols : parquet en bâtons rompus dans l'ancienne chambre, gris ciment dans l'ancien cellier et l'ancien "
     "placard (à partir de x 325) ; cloisons déposées du relevé d'origine dessinées en tireté."),
    ("V11.0", "06/10/2026",
     "Nouveau départ, pièce vide (chambre + ancien cellier ouverts, sans cloison). "
     "Mur nord : 5 meubles bas de 60 (x 10 → 310), à 10 du mur ouest. "
     "Plan et élévation générés depuis le modèle 3D (3d/v13/modele.py)."),
]
