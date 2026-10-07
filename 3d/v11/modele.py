# Cuisine V11 : source unique.
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

VERSION = "V11.26"
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
# Cloison neuve de 7 à 10 de B5 (x 320 → 327), du mur nord à y 45, où passent les réseaux. La porte est dans l'axe de
# la cloison ; son dormant vient directement contre le flanc nord du frigo (joue de finition de C2, y 118), sans
# montant. Bloc-porte à un vantail de 63 × 199 (largeur standard), poignée à droite vue de la cuisine (côté frigo),
# paumelles à gauche (côté cloison) : dormant 4,5 × 7, traverse haute h 199,5 → 204, linteau au-dessus ; vantail de 4,
# détalonné de 1, 3 paumelles côté cellier. Règle de pose : baie = vantail + 10. Il s'ouvre vers le cellier (vers
# l'est) : côté cuisine, il heurterait le plan de travail de B5.
PORTE_TITRE = "porte simple de 63, poignée à droite"
CLOISON_Y1, MONTANT, _charnieres = 45, 0, ["n"]       # charnières des vantaux, du nord au sud
JOUE_C2 = 118                                   # face nord de la joue du frigo
BAIE_Y0, BAIE_Y1 = CLOISON_Y1, JOUE_C2 - MONTANT
_somme = BAIE_Y1 - BAIE_Y0 - 10
VANTAUX_L = [_somme] if len(_charnieres) == 1 else [20, _somme - 20]
DORMANT, EP_VANTAIL, X_PORTE = 4.5, 4, 323.5     # x : axe de la cloison
ENVELOPPE += [
    Bloc("cloison", "cloison_cellier", 320, 327, 0, CLOISON_Y1, 0, H),
    Bloc("linteau", "linteau_cellier", 320, 327, BAIE_Y0, BAIE_Y1, 204, H),
    Bloc("dormant", "dormant_n", 320, 327, BAIE_Y0, BAIE_Y0 + DORMANT, 0, 204),
    Bloc("dormant", "dormant_s", 320, 327, BAIE_Y1 - DORMANT, BAIE_Y1, 0, 204),
    Bloc("dormant_haut", "dormant_haut", 320, 327, BAIE_Y0, BAIE_Y1, 204 - DORMANT, 204),
]
# vantaux fermés (ils mordent de 0,5 dans la feuillure du dormant) et charnières : (largeur, charnière, bout fermé)
CELLIER_VANTAUX = []
_y = BAIE_Y0 + DORMANT - 0.5
_xc = X_PORTE + EP_VANTAIL / 2                   # face côté cellier, où sont les paumelles
for k, (w, c) in enumerate(zip(VANTAUX_L, _charnieres)):
    ENVELOPPE.append(Bloc("porte", f"cellier_vantail_{k + 1}", X_PORTE - EP_VANTAIL / 2, _xc, _y, _y + w, 1, 199))
    h, fe = ((_xc, _y), (_xc, _y + w)) if c == "n" else ((_xc, _y + w), (_xc, _y))
    CELLIER_VANTAUX.append(dict(w=w, h=h, ferme=fe, balais=[], saillie=0))
    for z in (20, 100, 180):
        ENVELOPPE.append(Cyl("paumelle", f"paumelle_{k + 1}_{z}", h[0], h[1], 0.8, z, z + 10))
    _y += w + 1
if MONTANT:
    ENVELOPPE.append(Bloc("cloison", "montant_cellier", 320, 327, BAIE_Y1, JOUE_C2, 0, H))
# Ballon d'eau chaude, 2 variantes (V11_BALLON) :
#   « rond » : ballon existant Ø 50 dans la niche du cellier (h 90 → 210) ;
#   « plat » : remplacé par un ballon extra-plat Atlantic Linéo 80 L (réf. 157209, 130 × 49 × 29, 37,5 kg, vertical)
#   fixé dans le WC, sur la face sud du mur entre WC et cellier (y 110 → 139), h 115 → 245. La niche du cellier se
#   libère : aspirateur et produits ménagers.
BALLON_V = os.environ.get("V11_BALLON", "rond")
PLAT = BALLON_V == "plat"
BALLON_PLAT = dict(nom="Atlantic Linéo 80 L", ref="157209", h=130, l=49, p=29, x0=414.5, y0=110, z0=115)
BALLON = (Bloc("ballon", "ballon_plat", BALLON_PLAT["x0"], BALLON_PLAT["x0"] + BALLON_PLAT["l"], BALLON_PLAT["y0"],
               BALLON_PLAT["y0"] + BALLON_PLAT["p"], BALLON_PLAT["z0"], BALLON_PLAT["z0"] + BALLON_PLAT["h"])
          if PLAT else Cyl("ballon", "ballon_ecs", 459, 72, 25, 90, 210))
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


HAUTS_CONTENU = ["épices, huiles", "petit-déjeuner, épicerie", "assiettes, bols", "verres, tasses"]


def meuble_haut_nord(nom, x0, largeur, contenu=""):
    x1 = x0 + largeur
    MEUBLES.append(Bloc("caisson_haut", f"caisson_{nom}", x0, x1, 0, P_HAUT, HAUT_Z0, HAUT_Z1, nom.upper()))
    MEUBLES.append(Bloc("facade_haut", f"facade_{nom}", x0, x1, P_HAUT, P_HAUT + FACADE, HAUT_Z0, HAUT_Z1,
                        poignee=ORGA["hauts"], contenu=contenu))
    # ruban LED sous le caisson, vers l'avant, éclairant le plan de travail
    MEUBLES.append(Bloc("led", f"led_{nom}", x0 + 2, x1 - 2, P_HAUT - 7, P_HAUT - 5, HAUT_Z0 - 0.8, HAUT_Z0))


# mur nord : 5 meubles bas de 60, à 10 du mur ouest (x 10 → 310) ; plaque sur B2, LV en B3, évier sur B4
ECART_OUEST = 10
N_BAS, N_HAUTS = 5, 4
B_PLAQUE, B_LV, B_EVIER = 2, 3, 4
for i in range(N_BAS):
    meuble_bas_nord(f"b{i + 1}", ECART_OUEST + 60 * i, 60)

# ------------------------------------------------------------------ organisation des façades (A, tout en tiroirs)
# L'électroménager ne bouge pas : B2 (sous la plaque : bandeau devant le moteur d'aspiration + un tiroir de 46) et B3
# (LV, façade intégrée) sont fixes. Façades du haut vers le bas, hauteurs en cm (total 72, h 15 → 87).
# (genre, hauteur, contenu)
ORGA = dict(titre="Tout en tiroirs", hauts="porte",
            bas={1: [("tiroir", 18, "ustensiles"), ("tiroir", 27, "poêles"), ("tiroir", 27, "casseroles")],
                 4: [("tiroir", 72, "tri : 3 bacs")],
                 5: [("tiroir", 18, "couverts"), ("tiroir", 27, "boîtes, films"), ("tiroir", 27, "torchons, sacs")]})
FACADES_FIXES = {2: [("bandeau", 26, ""), ("tiroir", 46, "couvercles, plats")], 3: [("tiroir", 72, "")]}
for n in range(1, N_BAS + 1):
    x0, x1 = ECART_OUEST + 60 * (n - 1), ECART_OUEST + 60 * n
    z = CAISSON_H
    for k, (genre, h, contenu) in enumerate(FACADES_FIXES.get(n) or ORGA["bas"][n]):
        MEUBLES.append(Bloc("facade", f"facade_b{n}_{k + 1}", x0, x1, P_CAISSON, P_CAISSON + FACADE, z - h, z,
                            poignee="" if genre == "bandeau" else genre, contenu=contenu))
        z -= h



def sur_bas(n):
    """Emprise x du meuble bas n (1 = le plus à l'ouest)."""
    return ECART_OUEST + 60 * (n - 1), ECART_OUEST + 60 * n


# plan de travail 4, P62 (débord 2 devant les façades), sur toute la rangée basse
PT_Z1 = CAISSON_H + 4
MEUBLES.append(Bloc("plan", "plan_nord", sur_bas(1)[0], sur_bas(N_BAS)[1], 0, 62, CAISSON_H, PT_Z1))

# induction 60 à aspiration intégrée, 54 × 50, à 3 des chants
x0, x1 = sur_bas(B_PLAQUE)
xm = (x0 + x1) / 2
MEUBLES.append(Bloc("plaque", "induction", x0 + 3, x1 - 3, 6, 56, PT_Z1, PT_Z1 + 0.6))
MEUBLES.append(Bloc("aspiration", "aspiration", xm - 4, xm + 4, 9, 53, PT_Z1 + 0.6, PT_Z1 + 0.8))

# évier inox 1 bac à encastrer 56 × 50, bac 40 × 40 × 20, mitigeur derrière le bac
x0, x1 = sur_bas(B_EVIER)
xm = (x0 + x1) / 2
MEUBLES.append(Bloc("evier", "evier_plage", x0 + 2, x1 - 2, 6, 56, PT_Z1, PT_Z1 + 0.4))
MEUBLES.append(Bloc("cuve", "evier_bac", xm - 20, xm + 20, 12, 52, PT_Z1 - 20, PT_Z1))
MEUBLES.append(Cyl("mitigeur", "mitigeur", xm, 8, 1.6, PT_Z1 + 0.4, PT_Z1 + 31))



def equiper(n, texte):
    """Ajoute l'équipement du meuble bas n à son étiquette (« B5 LV »)."""
    b = next(b for b in MEUBLES if b.nom == f"caisson_b{n}")
    b.etiq = f"B{n} {texte}"


equiper(B_EVIER, "poubelles")  # sous l'évier : tri sélectif sur coulissant
equiper(B_LV, "LV")            # lave-vaisselle 60 tout intégrable

# ------------------------------------------------------------------ réseaux d'eau (dans le vide technique, derrière les caissons)
# Tout longe les murs, en partie basse. Alimentation EF/EC (à 3 des murs) : de la nourrice sous le ballon, le long du
# retour sud du mur nord de l'alcôve (y 44), puis de sa face ouest (x 434), puis du mur nord jusqu'à l'évier.
# Évacuation (à 12 des murs, au-delà de la nourrice) : le long du mur nord, de la face ouest et du retour sud de
# l'alcôve, du mur est (x 484), puis du mur nord du WC (y 100) jusqu'à la chute existante (colonne d'eaux usées,
# contre le mur du WC sous le ballon). Contre l'alcôve, ils passent sous la première tablette du rayonnage du mur
# nord (h 60) ; sous le ballon (h 90), ils passent dessous.
# (rôle, nom, points (x, y), z, rayon)
CHUTE = (459, 94)
NOURRICE = (470, 52)
xe = (sur_bas(B_EVIER)[0] + sur_bas(B_EVIER)[1]) / 2   # axe de l'évier
xl0, xl1 = sur_bas(B_LV)
SIPHON = (xe, 32)
# Dans la niche (x > 431), tout reste dans la zone technique des 30 premiers cm (la chute est basse : dernier étage) :
# l'alimentation y passe à h 20 et remonte à h 50 dans l'angle (x 431, y 47) ; l'évacuation descend de h 43 à h 25
# sous la première tablette du rayonnage nord (x 422, y 38). Un coffre technique (h 0 → 30) couvre l'angle.
RESEAUX = [
    ("alim", "alim_niche", [NOURRICE, (NOURRICE[0], 47), (431, 47)], 20, 0.8),
    ("alim", "alim_evier", [(431, 47), (431, 3), (xe, 3), (xe, 8)], 50, 0.8),
    ("alim", "alim_lv", [(xe, 3), (xl1 - 15, 3), (xl1 - 15, 20)], 50, 0.8),
    ("evac", "evac_evier", [SIPHON, (xe, 10), (422, 10), (422, 38)], 43, 2),
    ("evac", "evac_niche", [(422, 38), (422, 56), (472, 56), (472, 88), (CHUTE[0], 88), CHUTE], 25, 2),
    ("evac", "evac_lv", [(xl0 + 20, 30), (xl0 + 20, 10), (xe, 10)], 43, 2),
]
ZONE_TECH = 30
_ev = RESEAUX[3][2] + RESEAUX[4][2][1:]
EVAC_LONGUEUR = round(sum(math.dist(a, b) for a, b in zip(_ev, _ev[1:])))

# mur nord : 5 meubles hauts de 60, décalés d'un demi-meuble : ils partent du milieu du premier bas (x 40 → 340)
DEPART_HAUTS = ECART_OUEST + 60 / 2
for i in range(N_HAUTS):
    meuble_haut_nord(f"h{i + 1}", DEPART_HAUTS + 60 * i, 60, HAUTS_CONTENU[i])
# joues de finition de 2 sur les flancs visibles des hauts, fileur de 7 jusqu'au plafond sur toute la longueur
FIN_HAUTS = DEPART_HAUTS + N_HAUTS * 60
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
COL_Y0, COL_Y1 = 120, 240


COLONNES_CONTENU = {("c1", "tiroir_1"): "plaques, grilles", ("c1", "tiroir_2"): "moules, plats à four",
                    ("c1", "porte_haute"): "réserves", ("c2", "porte_haute"): "grands plats, saladiers"}


def colonne_est(nom, y0, largeur, facades, etiq):
    """facades : (rôle, nom, z0, z1), de bas en haut."""
    y1 = y0 + largeur
    MEUBLES.append(Bloc("socle", f"socle_{nom}", COL_X + 5, COL_DOS, y0, y1, 0, SOCLE))
    MEUBLES.append(Bloc("colonne", f"caisson_{nom}", COL_X + FACADE, COL_DOS, y0, y1, SOCLE, COL_Z1, etiq))
    for role, n, z0, z1 in facades:
        p = "tiroir" if n.startswith("tiroir") else "porte" if n in ("porte_haute", "frigo") else ""
        MEUBLES.append(Bloc(role, f"{n}_{nom}", COL_X, COL_X + FACADE, y0, y1, z0, z1, poignee=p,
                            contenu=COLONNES_CONTENU.get((nom, n), "")))


# C1 : four 60 à h 88 → 148, micro-ondes encastrable (niche 38) au-dessus, h 148 → 186 ; 2 tiroirs dessous,
# rangement dessus
MO_Z0, MO_Z1 = 148, 186
colonne_est("c1", COL_Y1 - 60, 60, [
    ("facade_col", "tiroir_1", SOCLE, 50), ("facade_col", "tiroir_2", 50, 86), ("facade_col", "bandeau", 86, 88),
    ("four", "four", 88, MO_Z0), ("micro_onde", "micro_onde", MO_Z0, MO_Z1),
    ("facade_col", "porte_haute", MO_Z1, COL_Z1)], "C1 four + MO")
# C2 : réfrigérateur intégrable (niche 178), porte de rangement au-dessus
colonne_est("c2", COL_Y0, 60, [
    ("facade_col", "frigo", SOCLE, 193), ("facade_col", "porte_haute", 193, COL_Z1)], "C2 frigo")
# joues de finition de 2 sur les flancs visibles : nord de C2 (côté porte du cellier), sud de C1 jusqu'au décroché
MEUBLES.append(Bloc("joue", "joue_c2", COL_X, COL_DOS, COL_Y0 - 2, COL_Y0, 0, COL_Z1))
MEUBLES.append(Bloc("joue", "joue_c1", COL_X, 341, COL_Y1, COL_Y1 + 2, 0, COL_Z1))
MEUBLES.append(Bloc("fileur", "fileur_colonnes", COL_X, COL_X + FACADE, COL_Y0 - 2, COL_Y1 + 2, COL_Z1, H))

# ------------------------------------------------------------------ triangle d'activité (centres de l'évier et de la plaque,
# milieu de la façade du frigo)
_plaque = next(b for b in MEUBLES if b.role == "plaque")
_cuve = next(b for b in MEUBLES if b.role == "cuve")
_frigo = next(b for b in MEUBLES if b.nom == "caisson_c2")
TRIANGLE = [("frigo", (COL_X, (_frigo.y0 + _frigo.y1) / 2)),
            ("évier", ((_cuve.x0 + _cuve.x1) / 2, (_cuve.y0 + _cuve.y1) / 2)),
            ("plaque", ((_plaque.x0 + _plaque.x1) / 2, (_plaque.y0 + _plaque.y1) / 2))]


# ------------------------------------------------------------------ coin repas : banquette et table, angle sud-ouest
# Banquette du mur ouest (x 0 → 106), contre le mur sud : assise 45 (h 45), dossier 5 (h 85). Deux places assises
# (53 chacune ; 50 à 60 par adulte). Dessous, deux tiroirs de 44 × 40 (façades h 6 → 40) de part et d'autre du pied
# de la table : ils passent au-dessus de l'embase (h 2) ; pour ouvrir le tiroir est, on écarte la chaise.
BANQ = dict(x0=0, x1=106, y0=Y_MUR_SUD - 50, y1=Y_MUR_SUD)
PLACES_BANQUETTE, LARGEUR_PLACE = 2, 53
TIROIRS_BANQ = [(3, 47), (59, 103)]
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
    Bloc("enceinte", "enceinte_audio", 78, 100, Y_MUR_SUD - 20, Y_MUR_SUD - 2, ETAGERE_BANQ["z1"], ETAGERE_BANQ["z1"] + 30),
    # plante retombante à l'ouest de l'étagère : pot Ø 16, feuillage Ø 28
    Cyl("pot", "pot_plante", 22, Y_MUR_SUD - 12, 8, ETAGERE_BANQ["z1"], ETAGERE_BANQ["z1"] + 14),
    Cyl("plante", "plante", 22, Y_MUR_SUD - 12, 14, ETAGERE_BANQ["z1"] + 14, ETAGERE_BANQ["z1"] + 40),
]
# Table ronde Ø 80 à pied tulipe (h 75) devant la banquette : le plateau la recouvre de 15 ; une chaise à l'est.
# Suspension au-dessus (point lumineux au plafond centré sur la table) : abat-jour Ø 35, bas à h 140 (65 au-dessus du
# plateau), fil jusqu'à la rosace.
TABLE = dict(cx=(BANQ["x0"] + BANQ["x1"]) / 2, cy=BANQ["y0"] + 15 - 40, r=40)
MEUBLES += [
    Cyl("table", "plateau", TABLE["cx"], TABLE["cy"], TABLE["r"], 72, 75),
    Cyl("pied", "pied_table", TABLE["cx"], TABLE["cy"], 4, 2, 72),
    Cyl("pied", "embase_table", TABLE["cx"], TABLE["cy"], 20, 0, 2),
    Cyl("lampe", "suspension", TABLE["cx"], TABLE["cy"], 17.5, 140, 160),
    Cyl("fil", "fil_suspension", TABLE["cx"], TABLE["cy"], 0.4, 160, H - 3),
    Cyl("fil", "rosace_suspension", TABLE["cx"], TABLE["cy"], 5, H - 3, H),
]
SUSPENSION = dict(d=35, z0=140, z1=160)


def chaise(nom, x0, y0, dossier):
    """Chaise 42 × 42, assise h 45, dossier h 85 du côté indiqué (« n », « s », « e », « o »)."""
    x1, y1 = x0 + 42, y0 + 42
    for i, (px, py) in enumerate(((x0, y0), (x1 - 2, y0), (x0, y1 - 2), (x1 - 2, y1 - 2))):
        MEUBLES.append(Bloc("chaise", f"pied_{nom}_{i + 1}", px, px + 2, py, py + 2, 0, 42))
    MEUBLES.append(Bloc("chaise", f"assise_{nom}", x0, x1, y0, y1, 42, 45))
    d = {"n": (x0, x1, y0, y0 + 3), "s": (x0, x1, y1 - 3, y1), "o": (x0, x0 + 3, y0, y1), "e": (x1 - 3, x1, y0, y1)}
    MEUBLES.append(Bloc("chaise", f"dossier_{nom}", *d[dossier], 45, 85))


GLISSE = 10
CHAISE_X0 = TABLE["cx"] + TABLE["r"] - GLISSE
chaise("chaise_1", CHAISE_X0, TABLE["cy"] - 21, "e")

# ------------------------------------------------------------------ cellier : rangements
# La porte du cellier s'ouvre vers le cellier : rien n'est posé dans le balayage des vantaux.
EP = 2  # épaisseur des tablettes et montants


def rayonnage(nom, x0, x1, y0, y1, zs, montants_en_x=True, z1=COL_Z1, contenus=()):
    """Montants toute hauteur aux deux bouts + tablettes aux hauteurs zs (dessus de tablette = z + EP)."""
    if montants_en_x:
        MEUBLES.append(Bloc("montant", f"montant_{nom}_1", x0, x0 + EP, y0, y1, 0, z1))
        MEUBLES.append(Bloc("montant", f"montant_{nom}_2", x1 - EP, x1, y0, y1, 0, z1))
        xi0, xi1, yi0, yi1 = x0 + EP, x1 - EP, y0, y1
    else:
        MEUBLES.append(Bloc("montant", f"montant_{nom}_1", x0, x1, y0, y0 + EP, 0, z1))
        MEUBLES.append(Bloc("montant", f"montant_{nom}_2", x0, x1, y1 - EP, y1, 0, z1))
        xi0, xi1, yi0, yi1 = x0, x1, y0 + EP, y1 - EP
    for k, z in enumerate(zs):
        MEUBLES.append(Bloc("etagere", f"etag_{nom}_{k + 1}", xi0, xi1, yi0, yi1, z, z + EP,
                            contenu=contenus[k] if k < len(contenus) else ""))
    return xi1 - xi0 if montants_en_x else yi1 - yi0


# Deux balais accrochés sur le flanc nord du frigo (joue de C2, y 118), contre le mur du WC (x 382) : l'un tête en bas,
# l'autre tête en haut, si bien que leurs têtes (24 × 6, à plat contre la joue, y 112 → 118) se chevauchent en x
# sans se toucher et que les manches ne sont qu'à 6 l'un de l'autre. Crochets h 150 (tête en bas) et h 120 (tête
# en haut, le manche pend dessous).
BALAIS = [(364, "bas"), (370, "haut")]          # (axe x, position de la tête)
for k, (xc, tete) in enumerate(BALAIS):
    zt = (8, 22) if tete == "bas" else (146, 160)
    zm = (22, 150) if tete == "bas" else (18, 146)
    zc = 148 if tete == "bas" else 120
    MEUBLES.append(Bloc("ratelier", f"crochet_balai_{k + 1}", xc - 1, xc + 1, JOUE_C2 - 3, JOUE_C2, zc, zc + 3))
    MEUBLES.append(Cyl("manche", f"manche_balai_{k + 1}", xc, JOUE_C2 - 2.5, 1.2, *zm))
    MEUBLES.append(Bloc("balai", f"tete_balai_{k + 1}", xc - 12, xc + 12, JOUE_C2 - 6, JOUE_C2, *zt))

# Rayonnage toute hauteur P40 contre le mur nord, jusqu'au mur de l'alcôve (x 434) : 6 tablettes, la première à h 60
# au-dessus des réseaux (h 43 → 50) qui passent dessous. Il part de la cloison (x 329) : le petit vantail balaie
# y 42 → 62, au-delà de sa profondeur (y 40).
# Plus de rayonnage devant le ballon : nourrice, groupe de sécurité et chute restent accessibles directement.
_nord_x0 = 329 if BAIE_Y0 + DORMANT >= 41 else math.ceil(X_PORTE + EP_VANTAIL / 2 + VANTAUX_L[0] + 1.5)
# Contenu de chaque tablette (de bas en haut) et du sol sous la première tablette.
RAYON_NORD = dict(x0=_nord_x0, x1=434, y0=0, y1=40, zs=[60, 96, 132, 168, 204, 238],
                  contenus=["packs d'eau, bouteilles, lait", "conserves, bocaux, sauces",
                            "réserves : pâtes, riz, farine, sucre", "biscuits, apéritif",
                            "papier, petit électroménager rare (raclette, gaufrier)", ""],
                  sol="produits d'entretien, seau, pommes de terre, oignons")
L_NORD = rayonnage("nord", RAYON_NORD["x0"], RAYON_NORD["x1"], RAYON_NORD["y0"], RAYON_NORD["y1"], RAYON_NORD["zs"],
                   contenus=RAYON_NORD["contenus"])

# Variante ballon extra-plat : la niche du cellier (x 434 → 484, y 44 → 100) se libère. La chute est basse : le
# rayonnage ménage prend toute la niche, P50, du retour de l'alcôve au mur du WC. En bas, la zone technique (h 0 → 30 :
# nourrice, vannes, chute, évacuation) est couverte d'un plancher démontable à h 30, sur lequel repose l'aspirateur
# traîneau (bloc, flexible enroulé dessus, tube replié et brosse devant) ; puis 5 tablettes.
#   Eau chaude : du ballon, à travers le mur du WC, puis le long du mur du WC et du mur est jusqu'à la nourrice (h 20).
if PLAT:
    RAYON_MENAGE = dict(x0=434, x1=484, y0=44, y1=100, zs=[ZONE_TECH, 72, 108, 144, 180, 216],
                        contenus=["", "lessive, assouplissant", "produits sols, vitres, salle de bains",
                                  "éponges, chiffons, sacs poubelle", "recharges, ampoules, piles",
                                  "outillage léger, réserve"],
                        sol="zone technique : nourrice, vannes, chute (plancher démontable)")
    L_MENAGE = rayonnage("menage", RAYON_MENAGE["x0"], RAYON_MENAGE["x1"], RAYON_MENAGE["y0"], RAYON_MENAGE["y1"],
                         RAYON_MENAGE["zs"], montants_en_x=False, contenus=RAYON_MENAGE["contenus"])
    _zp = ZONE_TECH + EP
    ASPIRATEUR = Bloc("aspirateur", "aspirateur_bloc", 440, 480, 50, 78, _zp, _zp + 28)
    MEUBLES += [ASPIRATEUR,
                Cyl("aspirateur", "aspirateur_flexible", 460, 64, 10, _zp + 28, _zp + 36),
                Bloc("aspirateur", "aspirateur_tube_brosse", 436, 482, 82, 94, _zp, _zp + 6)]
    _xb = BALLON_PLAT["x0"] + BALLON_PLAT["l"] / 2
    RESEAUX.append(("alim", "alim_ecs", [(_xb, BALLON_PLAT["y0"] + 2), (_xb, 97), (481, 97), (481, NOURRICE[1]), NOURRICE],
                    20, 0.8))
MEUBLES.append(Bloc("tech", "coffre_technique", 418, 434, 40, 62, 0, ZONE_TECH))

# ------------------------------------------------------------------ porte du cellier : angle d'ouverture
# Chaque vantail tourne de sa position fermée vers l'est ; il s'arrête 3° avant le premier obstacle à sa portée
# (coin du mur nord du WC, rayonnages), sinon à 90°.
_obstacles = [((382, 100), "le coin du mur nord du WC"),
              ((RAYON_NORD["x0"], RAYON_NORD["y1"]), "le rayonnage du mur nord")]
for v in CELLIER_VANTAUX:
    (hx, hy), (fx, fy), w = v["h"], v["ferme"], v["w"]
    sens = 1 if fy > hy else -1                  # 1 : le vantail pend vers le sud depuis sa charnière
    # la face côté cellier mène la rotation : ce qui y est accroché (saillie) touche l'obstacle plus tôt
    contacts = [(math.degrees(math.atan2(px - hx, (py - hy) * sens)
                              - math.asin(min(1, v["saillie"] / math.dist((hx, hy), (px, py))))) - 3, nom)
                for (px, py), nom in _obstacles
                if math.dist((hx, hy), (px, py)) <= w + 1 and px > hx and (py - hy) * sens > 0]
    v["angle"], v["butee"] = min([(90, "")] + contacts)
    a = math.radians(v["angle"])
    v["ouvert"] = (hx + w * math.sin(a), hy + sens * w * math.cos(a))
PASSAGE_CELLIER = VANTAUX_L[-1] - 6              # passage libre par le grand vantail ouvert (vantail, paumelles, butée)

# ------------------------------------------------------------------ ouvertures de l'électroménager (plan seulement)
# abattant : emprise de la porte abattue (x0, x1, y0, y1) ; battant : charnière, bout fermé, bout ouvert à 90°.
_lv = sur_bas(B_LV)
OUVERTURES = [
    ("abattant", "LV", (_lv[0], _lv[1], P_CAISSON + FACADE, P_CAISSON + FACADE + CAISSON_H - SOCLE)),
    ("abattant", "four", (COL_X - 60, COL_X, COL_Y1 - 60, COL_Y1)),
    # frigo : charnières au sud (côté C1), la porte se rabat vers le sud, on accède par le nord (côté évier)
    ("battant", "frigo", ((COL_X, COL_Y0 + 60), (COL_X, COL_Y0), (COL_X - 60, COL_Y0 + 60))),
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
            and not b.nom.startswith(("tiroir_banquette", f"facade_b{B_LV}_"))]
CAPACITE = dict(
    v11=dict(lin_bas=N_BAS * 60, lin_hauts=N_HAUTS * 60, lin_col=2 * 60,
             modules=(N_BAS, N_HAUTS, 2), tiroirs=len(_tiroirs), plan=PLAN_SEGMENTS, prof_plan=62,
             cellier=(RAYON_NORD["x1"] - RAYON_NORD["x0"], len(RAYON_NORD["zs"]), L_NORD, RAYON_NORD["y1"]),
             menage=(RAYON_MENAGE["y1"] - RAYON_MENAGE["y0"], len(RAYON_MENAGE["zs"]) - 1, L_MENAGE,
                     RAYON_MENAGE["x1"] - RAYON_MENAGE["x0"]) if PLAT else None,
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
    v11=dict(cuisine=sum([2 * litres(60, P_CAISSON, CAISSON_H - SOCLE), litres(60, P_CAISSON, 46),
                          N_HAUTS * litres(60, P_HAUT, HAUT_Z1 - HAUT_Z0),
                          litres(60, P_CAISSON, (86 - SOCLE) + (COL_Z1 - MO_Z1)), litres(60, P_CAISSON, COL_Z1 - 193),
                          2 * litres(40, 40, 30)]),
             cellier=litres(L_NORD, RAYON_NORD["y1"], COL_Z1 - RAYON_NORD["zs"][0])
             + (litres(L_MENAGE, RAYON_MENAGE["x1"] - RAYON_MENAGE["x0"], COL_Z1 - ZONE_TECH - EP) if PLAT else 0)),
    p9a=dict(cuisine=sum([litres(40, 58, 72), litres(60, 58, 46), litres(80, 58, 72), litres(140, 33, 90),
                          litres(60, 58, 23 + 118), litres(59, 57, 45), litres(59, 57, 71 + 50), litres(52, 28, 72)]),
             cellier=litres(38, 30, 194)),
)
# contenu des rangements ouverts et des tiroirs, pour le tableau « Contenu des rangements »
CONTENU = [
    ("B1, à côté de la plaque", "3 tiroirs : ustensiles (18), poêles (27), casseroles (27)"),
    ("B2, sous la plaque", "bandeau devant le moteur d'aspiration ; tiroir de 46 : couvercles, plats"),
    ("B3", "lave-vaisselle"),
    ("B4, sous l'évier", "1 tiroir découpé autour du siphon : tri en 3 bacs (ordures, emballages, verre) et produits "
     "d'évier dans le bac avant"),
    ("B5, plan libre", "3 tiroirs : couverts (18), boîtes de conservation et films (27), torchons et sacs (27)"),
    ("H1, au-dessus de la plaque", "épices, huiles, condiments"),
    ("H2", "petit-déjeuner (céréales, thé, café, confitures) et épicerie sèche du quotidien : pâtes, riz, farine"),
    ("H3, au-dessus du LV", "assiettes et bols (vidage du LV sans se déplacer)"),
    ("H4, au-dessus de l'évier et de B5", "verres et tasses, près du coin café sur B5"),
    ("C1", "tiroir bas : plaques et grilles du four ; tiroir haut : moules, plats à four ; porte haute : réserves"),
    ("C2", "porte au-dessus du frigo : grands plats, saladiers, plateaux (rarement utilisés)"),
    ("Banquette", "tiroir ouest : nappes, sets de table ; tiroir est : jeux, bougies"),
    ("Cellier, sol sous la 1re tablette", RAYON_NORD["sol"] + " (les tuyaux passent derrière, contre le mur)"),
] + [(f"Cellier, tablette h {z}", c) for z, c in zip(RAYON_NORD["zs"], RAYON_NORD["contenus"]) if c] + [
    ("Cellier, flanc du frigo", "2 balais (un tête en bas, un tête en haut)"),
] + ([("Cellier, niche (ballon au WC) : sous le plancher h 30", RAYON_MENAGE["sol"]),
      ("Cellier, niche : plancher h 30", "aspirateur traîneau : bloc, flexible enroulé dessus, tube replié et brosse")]
     + [(f"Cellier, niche : tablette h {z}", c) for z, c in zip(RAYON_MENAGE["zs"], RAYON_MENAGE["contenus"]) if c]
     if PLAT else []) + [
]

# ------------------------------------------------------------------ historique (section Changements)
CHANGEMENTS = [
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
     "Plan et élévation générés depuis le modèle 3D (3d/v11/modele.py)."),
]
