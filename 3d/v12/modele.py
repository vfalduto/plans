# Cuisine V12 : source unique (repart de la V11.50, 3d/v11/ gardé pour mémoire).
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

VERSION = "V12.2"
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
# Un retour de cloison de 8 (x 320 → 327, y 0 → 8) garde le passage des réseaux, qui longent le mur nord à h 43–50 ;
# la baie va de là au flanc nord de C3 (colonne de 39 au nord du frigo) : y 8 → 81, soit 73, sous un linteau à h 204.
# V11.40 : PORTE DE PLACARD PLIANTE à deux vantaux de 36 (2,5 d'épaisseur), posée sans dormant sur un rail haut côté
# cuisine (x 318,5). Pivot contre le retour de cloison, au nord ; en s'ouvrant, les deux vantaux se replient l'un
# contre l'autre et se rangent côté cuisine, perpendiculaires à la baie, devant le coffre des réseaux (x 282 → 318,5,
# y 8 → 13). Côté cellier, ils heurteraient le rayonnage nord. Le vantail du pivot balaie un quart de cercle de 36
# côté cuisine. Poignée au sud, côté C3.
PORTE_TITRE = "porte de placard pliante, 2 vantaux repliés au nord"
CLOISON_Y1, MONTANT, _charnieres = 8, 0, []          # plus de vantail battant
C3_L = 39                                       # largeur de C3 (colonne tiroirs à l'anglaise), au nord de C2
JOUE_C2 = 120 - C3_L                            # face nord de la colonne la plus au nord (C3), y 81
BAIE_Y0, BAIE_Y1 = CLOISON_Y1, JOUE_C2 - MONTANT
DORMANT, EP_VANTAIL, X_PORTE = 0, 2.5, 318.5    # pas de dormant ; x : rail de la porte pliante
PLIANTE = dict(rail=X_PORTE, y0=BAIE_Y0, y1=BAIE_Y1, l=(BAIE_Y1 - BAIE_Y0 - 1) / 2, ep=EP_VANTAIL, z1=203,
               mi=60)   # état mi-ouvert : vantail du pivot tourné de 60° vers la cuisine
ACCORDEON = None
VANTAUX_L = [BAIE_Y1 - BAIE_Y0]
CELLIER_VANTAUX = []
ENVELOPPE += [
    Bloc("cloison", "cloison_cellier", 320, 327, 0, CLOISON_Y1, 0, H),
    Bloc("linteau", "linteau_cellier", 320, 327, BAIE_Y0, BAIE_Y1, 204, H),
    # porte pliante fermée (deux vantaux dans la baie) ; repliée, voir PLIANTE
    Bloc("porte", "cellier_pliante", X_PORTE - EP_VANTAIL / 2, X_PORTE + EP_VANTAIL / 2, BAIE_Y0, BAIE_Y1, 1, 203),
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


def meuble_bas_nord(nom, x0, largeur):
    x1 = x0 + largeur
    MEUBLES.append(Bloc("socle", f"socle_{nom}", x0, x1, 0, P_CAISSON - 3, 0, SOCLE))
    MEUBLES.append(Bloc("caisson", f"caisson_{nom}", x0, x1, 0, P_CAISSON, SOCLE, CAISSON_H, nom.upper()))


# Meubles hauts : caisson P33 + façade 2, h 153 → 243 (remontés de 5 en V11.8 : 62 au-dessus du plan),
# fileur de 7 jusqu'au plafond.
HAUT_Z0, HAUT_Z1, P_HAUT = 153, 243, 33


HAUTS_CONTENU = ["hotte intégrée", "épices, huiles", "petit-déjeuner, épicerie", "assiettes, bols"]


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
ECART_OUEST = 5
LARGEURS_BAS = [20, 60, 60, 60, 60]
N_BAS, N_HAUTS = len(LARGEURS_BAS), 4
_X_BAS = [ECART_OUEST + sum(LARGEURS_BAS[:i]) for i in range(N_BAS + 1)]   # bords des meubles bas
# V11.50 : le LV monte en colonne (C1) ; B4 devient un meuble à tiroirs ; four encastré sous la plaque (B2)
B_COULISSANT, B_PLAQUE, B_TIROIRS, B_TIROIRS_2, B_EVIER = 1, 2, 3, 4, 5
B_LV = None
for i in range(N_BAS):
    meuble_bas_nord(f"b{i + 1}", _X_BAS[i], LARGEURS_BAS[i])

# ------------------------------------------------------------------ organisation des façades (A, tout en tiroirs)
# L'électroménager ne bouge pas : B2 (sous la plaque : four encastré 60 au-dessus d'un tiroir de 12)
# (LV, façade intégrée) sont fixes. Façades du haut vers le bas, hauteurs en cm (total 72, h 15 → 87).
# (genre, hauteur, contenu)
ORGA = dict(titre="Tout en tiroirs", hauts="porte",
            bas={B_TIROIRS: [("tiroir", 18, "ustensiles"), ("tiroir", 27, "poêles"), ("tiroir", 27, "casseroles")],
                 B_COULISSANT: [("tiroir", 72, "huiles, épices")],
                 B_TIROIRS_2: [("tiroir", 18, "couverts"), ("tiroir", 27, "moules, plats à four"),
                               ("tiroir", 27, "boîtes de conservation")],
                 5: [("tiroir", 72, "tri : 3 bacs")]})
FACADES_FIXES = {B_PLAQUE: [("four", 60, ""), ("tiroir", 12, "plaques, grilles")]}
for n in range(1, N_BAS + 1):
    x0, x1 = _X_BAS[n - 1], _X_BAS[n]
    z = CAISSON_H
    for k, (genre, h, contenu) in enumerate(FACADES_FIXES.get(n) or ORGA["bas"][n]):
        MEUBLES.append(Bloc("four" if genre == "four" else "facade", f"facade_b{n}_{k + 1}", x0, x1, P_CAISSON,
                            P_CAISSON + FACADE, z - h, z, poignee="" if genre in ("bandeau", "four") else genre,
                            contenu=contenu))
        z -= h



def sur_bas(n):
    """Emprise x du meuble bas n (1 = le plus à l'ouest)."""
    return _X_BAS[n - 1], _X_BAS[n]


# plan de travail 4, P62 (débord 2 devant les façades), sur toute la rangée basse
PT_Z1 = CAISSON_H + 4
MEUBLES.append(Bloc("plan", "plan_nord", 0, sur_bas(N_BAS)[1], 0, 62, CAISSON_H, PT_Z1))   # jusqu'au mur ouest
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
    # le mur nord du WC (y 99, h 20, sous le rayonnage sud qu'elle traverse) et entre dans C1 par son dos
    ("alim", "alim_lv", [NOURRICE, (481, NOURRICE[1]), (481, 99), (X_LV_RES, 99), (X_LV_RES, 110)], 20, 0.8),
    ("evac", "evac_evier", [SIPHON, (xe, 4), (422, 4), (422, 38)], 43, 2),
    ("evac", "evac_niche", [(422, 38), (422, 56), (472, 56), (472, 88), (CHUTE[0], 88), CHUTE], 25, 2),
    # vidange du LV (pompe) : de C1, le long du mur nord du WC (y 95, h 25), directement dans la chute
    ("evac", "evac_lv", [(X_LV_RES, 110), (X_LV_RES, 95), (CHUTE[0] - 5, 95)], 25, 2),
]
ZONE_TECH = 30
# coffre des réseaux entre B4 et la cloison du cellier : P8, h 0 → 55 (dessus utilisable en tablette)
COFFRE_RESEAUX = (_X_BAS[-1], 320, 0, 8, 0, 55)
MEUBLES.append(Bloc("tech", "coffre_reseaux", *COFFRE_RESEAUX))

_ev = RESEAUX[3][2] + RESEAUX[4][2][1:]
EVAC_LONGUEUR = round(sum(math.dist(a, b) for a, b in zip(_ev, _ev[1:])))

# mur nord : 3 meubles hauts de 60, réalignés sur les joints des bas (V11.39) : ils finissent au droit de B4
# (x 85 → 265, au-dessus de B2, B3, B4) ; à leur gauche, 3 étagères ouvertes en chêne du mur ouest à H1, P25.
# V11.41 : H1 passe à 80 comme B2, pour garder les joints des hauts au droit de ceux des bas (x 65 → 265)
# V11.50 : un haut de plus, H1 au-dessus de la plaque avec la hotte intégrée (groupe filtrant) ; hauts x 25 → 265
LARGEURS_HAUTS = [60, 60, 60, 60]
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
MEUBLES.append(Bloc("joue", "joue_h_est", FIN_HAUTS, FIN_HAUTS + 2, 0, P_HAUT + FACADE, HAUT_Z0, HAUT_Z1))
MEUBLES.append(Bloc("fileur", "fileur_hauts", DEPART_HAUTS - 2, FIN_HAUTS + 2, P_HAUT, P_HAUT + FACADE, HAUT_Z1, H))

# ------------------------------------------------------------------ colonnes, mur est
# Colonnes P60 (caisson 58 + façade 2), socle 15, dessus aligné sur les hauts, contre le mur du WC (x 382),
# à la place des anciens E1 / E2 : C2 frigo y 120 → 180, C1 four y 180 → 240 (jusqu'au décroché). Façades vers l'ouest.
Y_MUR_SUD = 252
X_MUR_EST = 382
COL_DOS = X_MUR_EST
COL_X = COL_DOS - P_CAISSON - FACADE      # nu des façades, x 322
COL_Z1 = HAUT_Z1
# V11.50 : du nord au sud, C1 LV + MO (60, y 81 → 141), C2 frigo (60), C3 tiroirs à l'anglaise (39, → 240)
COL_Y0, COL_Y1 = JOUE_C2 + 60, 240


COLONNES_CONTENU = {("c1", "tiroir_1"): "pastilles LV, torchons", ("c1", "lv"): "lave-vaisselle intégré",
                    ("c1", "porte_haute"): "réserves", ("c2", "porte_haute"): "grands plats, saladiers",
                    ("c3", "porte_anglaise"): "maxi tiroir, 5 paniers", ("c3", "porte_haute"): "bocaux, vases"}


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
# joues de finition de 2 sur les flancs visibles : nord de C2 (côté porte du cellier), sud de C1 jusqu'au décroché
# C3 (V11.50, au sud, jusqu'au décroché) : colonne de 39, porte basse sur tiroirs à l'anglaise (5 tiroirs intérieurs),
# porte haute ; paumelles au sud, poignée au nord.
TIROIRS_ANGLAISE = ["verres, tasses", "café, thé", "épicerie du quotidien", "boîtes, films", "torchons, sacs"]
colonne_est("c3", COL_Y0 + 60, C3_L, [
    ("facade_col", "porte_anglaise", SOCLE, 193), ("facade_col", "porte_haute", 193, COL_Z1)], "C3 anglaise")
MEUBLES.append(Bloc("joue", "joue_c1", COL_X, 341, COL_Y1, COL_Y1 + 2, 0, COL_Z1))
# fileur couleur des murs entre C1 et le mur sud (montant du galandage, x 312) : ferme la poche de l'angle sud-est
MEUBLES.append(Bloc("joue", "fileur_c1", 312, COL_X, COL_Y1, COL_Y1 + 2, 0, H))
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


# V11.41 : deux balais accrochés au mur nord, dans les 40 libérés par le rayonnage (x 327 → 367), sur un tasseau à 8 du
# mur pour passer devant les tuyaux (y 2 → 6, h 43 → 50) : l'un tête en bas, l'autre tête en haut, têtes 24 × 6 à plat.
BALAIS = [(342, "bas"), (352, "haut")]          # (axe x, position de la tête)
Y_BALAIS = 8                                    # face du tasseau
for k, (xc, tete) in enumerate(BALAIS):
    zt = (8, 22) if tete == "bas" else (146, 160)
    zm = (22, 150) if tete == "bas" else (18, 146)
    zc = 148 if tete == "bas" else 120
    MEUBLES.append(Bloc("ratelier", f"crochet_balai_{k + 1}", xc - 1, xc + 1, Y_BALAIS, Y_BALAIS + 3, zc, zc + 3))
    MEUBLES.append(Cyl("manche", f"manche_balai_{k + 1}", xc, Y_BALAIS + 2.5, 1.2, *zm))
    MEUBLES.append(Bloc("balai", f"tete_balai_{k + 1}", xc - 12, xc + 12, Y_BALAIS, Y_BALAIS + 6, *zt))

# Rayonnage toute hauteur P40 contre le mur nord, jusqu'au mur de l'alcôve (x 434) : 6 tablettes, la première à h 60
# au-dessus des réseaux (h 43 → 50) qui passent dessous. La porte s'ouvrant côté cuisine (V11.35), il part de la
# cloison (x 327).
# Plus de rayonnage devant le ballon : nourrice, groupe de sécurité et chute restent accessibles directement.
# V11.41 : rayonnage raccourci de 40 côté entrée (il part de x 367, toujours arrondi) ; les balais prennent la place
_nord_x0 = 327 + 40
# Contenu de chaque tablette (de bas en haut) et du sol sous la première tablette.
RAYON_NORD = dict(x0=_nord_x0, x1=434, y0=0, y1=40, zs=[60, 96, 132, 168, 204, 238],
                  contenus=["packs d'eau, bouteilles, lait", "conserves, bocaux, sauces",
                            "réserves : pâtes, riz, farine, sucre", "biscuits, apéritif",
                            "papier, petit électroménager rare (raclette, gaufrier)", ""],
                  sol="pommes de terre, oignons (à l'écart des produits d'entretien)")
# V11.37 : angle côté entrée arrondi (R 30) : on ne se cogne pas en entrant
ARRONDI_NORD = 30
L_NORD = rayonnage("nord", RAYON_NORD["x0"], RAYON_NORD["x1"], RAYON_NORD["y0"], RAYON_NORD["y1"], RAYON_NORD["zs"],
                   contenus=RAYON_NORD["contenus"], arrondi=ARRONDI_NORD)
# V11.36 : second rayonnage toute hauteur contre le mur nord du WC (y 100), de C3 (x 382) au retour de l'alcôve
# (x 434), mêmes hauteurs de tablettes ; V11.39 : réduit à P19 pour affleurer le flanc nord de C3 (y 81), ce qui laisse
# 41 (y 40 → 81) entre les deux rayonnages pour atteindre la niche
# (ballon, nourrice, groupe de sécurité), au-dessus du coffre technique (h 30). L'entretien quitte le sol du rayonnage
# nord (denrées) pour celui-ci.
RAYON_SUD = dict(x0=382, x1=434, y0=JOUE_C2, y1=100, zs=RAYON_NORD["zs"],   # V11.39 : affleure le flanc de C3 (P19)
                 contenus=["sacs de courses, cabas", "pharmacie, premiers soins", "piles, ampoules, petit outillage",
                           "linge de maison de réserve", "vases, saladiers rarement utilisés", ""],
                 sol="seau, produits d'entretien")
L_SUD = rayonnage("sud", RAYON_SUD["x0"], RAYON_SUD["x1"], RAYON_SUD["y0"], RAYON_SUD["y1"], RAYON_SUD["zs"],
                  contenus=RAYON_SUD["contenus"])

MEUBLES.append(Bloc("tech", "coffre_technique", 418, 434, 40, 62, 0, ZONE_TECH))

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
# passage libre : baie moins les deux vantaux repliés et leur ferrure (≈ 2)
PASSAGE_CELLIER = round(PLIANTE["y1"] - PLIANTE["y0"] - 2 * PLIANTE["ep"] - 2)
# accès à la porte depuis la cuisine : du coin du plan de B4 à l'angle nord-ouest de C3
ACCES_CELLIER = math.dist((sur_bas(N_BAS)[1], 62), (COL_X, JOUE_C2))
# passages dans le cellier : entre le rayonnage nord (P40) et le rayonnage sud (y 75), et le flanc de C3 (y 81)
PASSAGE_RAYONNAGES = RAYON_SUD["y0"] - RAYON_NORD["y1"]
PASSAGE_ENTREE = JOUE_C2 - RAYON_NORD["y1"]

# ------------------------------------------------------------------ ouvertures de l'électroménager (plan seulement)
# abattant : emprise de la porte abattue (x0, x1, y0, y1) ; battant : charnière, bout fermé, bout ouvert à 90°.
_pl = sur_bas(B_PLAQUE)
OUVERTURES = [
    ("abattant", "LV", (COL_X - 58, COL_X, JOUE_C2, JOUE_C2 + 60)),              # LV en hauteur (C1), porte à h 66
    ("abattant", "four", (_pl[0], _pl[1], P_CAISSON + FACADE, P_CAISSON + FACADE + 52)),   # four sous la plaque
    # frigo : charnières au sud (côté C1), la porte se rabat vers le sud, on accède par le nord (côté évier)
    ("battant", "frigo", ((COL_X, COL_Y0 + 60), (COL_X, COL_Y0), (COL_X - 60, COL_Y0 + 60))),
    # C3 : maxi tiroir (colonne coulissante), il se tire vers l'ouest d'environ 50
    ("tiroir", "C3 tiré", (COL_X - 50, COL_X, COL_Y1 - C3_L, COL_Y1)),
] + [("tiroir", "banquette", (a, b, BANQ["y0"] - 2 - 35, BANQ["y0"] - 2)) for a, b in TIROIRS_BANQ]

# ------------------------------------------------------------------ capacité, à la manière des cuisinistes
# Pas de volume : mètres linéaires de meubles, nombre de modules, tiroirs, plan de travail utile (hors évier et
# plaque), tablettes du cellier. Repères pour une cuisine d'environ 8 m² (la pièce fait 3,25 × 2,52 = 8,2 m² hors
# cellier) : 4 à 6 m linéaires de meubles bas + hauts, 8 à 11 meubles, 1,5 à 2,5 m de plan de travail utile ;
# implantation type : un linéaire de 2,50 à 3 m avec 6 ou 7 meubles.
_plaque_b = next(b for b in MEUBLES if b.role == "plaque")
_evier_b = next(b for b in MEUBLES if b.role == "evier")
_pt = next(b for b in MEUBLES if b.nom == "plan_nord")
_trous = sorted([(_plaque_b.x0, _plaque_b.x1), (_evier_b.x0, _evier_b.x1)])
_bords = [_pt.x0] + [v for t in _trous for v in t] + [_pt.x1]
PLAN_SEGMENTS = [(a, b) for a, b in zip(_bords[::2], _bords[1::2])]       # plan de travail libre, x0 → x1
_tiroirs = [b for b in MEUBLES if b.role in ("facade", "facade_col") and b.poignee == "tiroir"
            and not b.nom.startswith("tiroir_banquette")]
CAPACITE = dict(
    v11=dict(lin_bas=sum(LARGEURS_BAS), lin_hauts=sum(LARGEURS_HAUTS), lin_col=2 * 60 + C3_L,
             modules=(N_BAS, N_HAUTS, 3), tiroirs=len(_tiroirs), plan=PLAN_SEGMENTS, prof_plan=62,
             cellier=(RAYON_NORD["x1"] - RAYON_NORD["x0"], len(RAYON_NORD["zs"]), L_NORD, RAYON_NORD["y1"]),
             cellier_sud=(RAYON_SUD["x1"] - RAYON_SUD["x0"], len(RAYON_SUD["zs"]), L_SUD, RAYON_SUD["y1"] - RAYON_SUD["y0"]),
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
                          litres(C3_L, P_CAISSON, COL_Z1 - SOCLE),
                          litres(LARGEURS_BAS[B_PLAQUE - 1], P_CAISSON, 12),
                          litres(LARGEURS_BAS[B_TIROIRS_2 - 1], P_CAISSON, CAISSON_H - SOCLE),
                          litres(sum(LARGEURS_HAUTS[1:]), P_HAUT, HAUT_Z1 - HAUT_Z0),   # H1 : hotte, hors volume
                          litres(60, P_CAISSON, (LV_Z0 - SOCLE) + (COL_Z1 - MO_Z1)), litres(60, P_CAISSON, COL_Z1 - 193),
                          2 * litres(40, 40, 30)]),
             cellier=litres(L_NORD, RAYON_NORD["y1"], COL_Z1 - RAYON_NORD["zs"][0])
             + litres(L_SUD, RAYON_SUD["y1"] - RAYON_SUD["y0"], COL_Z1 - RAYON_SUD["zs"][0])),
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
    ("Étagères à gauche de H1", ", ".join(ETAGERES_MUR["contenus"])),
    ("H1, au-dessus de la plaque", "hotte intégrée (groupe filtrant en recyclage) ; petit rangement au-dessus"),
    ("H2, au-dessus de B3", "épices, huiles, condiments"),
    ("H3", "petit-déjeuner (céréales, thé, café, confitures) et épicerie sèche du quotidien : pâtes, riz, farine"),
    ("H4, au-dessus de l'évier", "assiettes et bols"),
    ("C1, à côté de la porte du cellier", "tiroir bas : pastilles et sel du LV, torchons ; lave-vaisselle en hauteur ; "
     "micro-ondes ; porte haute : réserves"),
    ("C2", "porte au-dessus du frigo : grands plats, saladiers, plateaux (rarement utilisés)"),
    ("C3, au sud du frigo", "maxi tiroir coulissant (colonne extractible) à 5 paniers : " + ", ".join(TIROIRS_ANGLAISE) + " ; porte haute : bocaux, vases"),
    ("Banquette", "tiroir entre les pieds de la table : nappes, sets de table ; tiroir est : jeux, bougies"),
    ("Cellier nord, sol sous la 1re tablette", RAYON_NORD["sol"] + " (les tuyaux passent derrière, contre le mur)"),
] + [(f"Cellier nord, tablette h {z}", c) for z, c in zip(RAYON_NORD["zs"], RAYON_NORD["contenus"]) if c] + [
    ("Cellier, mur nord à l'entrée", "2 balais (un tête en bas, un tête en haut)"),
    ("Cellier sud (mur du WC), sol", RAYON_SUD["sol"]),
] + [(f"Cellier sud, tablette h {z}", c) for z, c in zip(RAYON_SUD["zs"], RAYON_SUD["contenus"]) if c] + [
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
    ("Fileurs", "Canopée au mur ouest, couleur des murs au sud de C1",
     "Fileur de 5 entre B1 et le mur ouest (plan de travail prolongé jusqu'au mur) ; fileur de 10 entre C1 et le montant "
     "du galandage (mur sud), qui ferme la poche de l'angle.", ("#3C524C", "#EFE9DC")),
    ("Colonnes C1, C2, C3 et meubles hauts H1 → H4", "Chêne miel, Plum Living", "Façades, joues et fileurs.", ("#A8743F",)),
    ("Meubles bas B1 → B5", "Laque Canopée, Plum Living",
     "Vert profond (nuancier Plum Living), posé sur caissons type IKEA METOD.", ("#3C524C",)),
    ("Crédence", "Zellige greige", "Carreaux 10 × 10 émaillés à la main, h 91 → 153, sur toute la rangée.",
     ("#C6BCAC", "#B9AE9D", "#A99D8B")),
    ("Plan de travail", "Effet béton blanc-gris", "Matière à définir (compact, céramique, quartz…) ; elle décide du "
     "type d'évier possible (sous plan ou à encastrer).", ("#D6D4CE", "#BDBBB5")),
    ("Évier et robinetterie", "Inox brossé", "Bac et mitigeur.", ("#C9C9C7",)),
    ("Poignées des façades bois (C1, C2, C3, H1 → H4)", "Profilé toute longueur en chêne miel",
     "Même matière que la façade : sur toute la largeur des tiroirs, sur toute la hauteur des portes.", ("#A8743F", "#8A5A2B")),
    ("Poignées des meubles bas Canopée (B1 → B5)", "Barres en inox brossé",
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

# ------------------------------------------------------------------ rendus 3D (3d/v12/rendu.py, Blender Cycles → cuisine-v12-3d/)
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
    ("cellier", "E · Entrée du cellier", "Entré dans le cellier, porte refermée derrière soi : rayonnage nord, ballon, zone technique."),
    ("dos_cellier", "F · Dos à la porte du cellier", "Debout devant la porte du cellier, vers la table et la banquette."),
    ("iso_nuit", "G · Isométrique de nuit", "Même vue que A, de nuit, tous les éclairages allumés : suspension, LED sous les "
     "hauts, cellier (pas de plafonnier dans le modèle)."),
]

# Avant / après : V11.34 (figée, commit fab26e3), mesurée avec le même code, pour le tableau de comparaison
AVANT = dict(version="V11.34", lin_bas=300, lin_hauts=240, lin_col=120, modules=(5, 4, 2), tiroirs=10, anglaise=0,
             plan=[(0, 68), (122, 187), (243, 305)], cellier_m2=1.46, tablettes_cm=6 * 101,
             volume_cuisine=2055, volume_cellier=739)
# version de chaque image de cuisine-v12-3d/ (rendus sur demande : `just v12-rendu`, ou une vue : `-- 256 iso`)
RENDUS_VERSION = {v: "V11.50" for v in ("iso", "entree", "fenetre", "banquette", "cellier", "dos_cellier", "iso_nuit", "iso_no")}
RENDUS_VERSION["iso_no_hermione"] = "V11.50"   # essai papier peint (rendu à part, scratchpad)

# ------------------------------------------------------------------ historique (section Changements)
CHANGEMENTS = [
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
     "Nouvelle page de travail cuisine-v12.html, repartie de la V11.50 à l'identique (modèle, plan, rendus). "
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
     "Rendus 3D (Blender Cycles, 3d/v12/rendu.py) : isométrique, depuis l'entrée, depuis la fenêtre, assis sur la "
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
     "Plan et élévation générés depuis le modèle 3D (3d/v12/modele.py)."),
]
