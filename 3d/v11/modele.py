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
from dataclasses import dataclass

VERSION = "V11.16"
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
# ------------------------------------------------------------------ cellier : cloison et porte (variante C retenue)
# Cloison neuve de 7 à 10 de B5 (x 320 → 327), du mur nord à y 38, où passent les réseaux. La porte est dans l'axe de
# la cloison, jusqu'au flanc nord du frigo (joue de finition de C2, y 118). Un montant de 7 toute hauteur contre cette
# joue reçoit le dormant côté frigo. Bloc-porte double battant tiercé : dormant 4,5 × 7, traverse haute h 199,5 → 204,
# linteau au-dessus ; vantaux de 4, jeu de 1 entre vantaux, détalonnés de 1, 3 paumelles par vantail côté cellier.
# Règle de pose : baie = somme des vantaux + 10. Les vantaux s'ouvrent vers le cellier (vers l'est) : côté cuisine,
# ils heurteraient le plan de travail de B5.
PORTE_TITRE = "double battant tiercé 20 + 43"
CLOISON_Y1, MONTANT, _charnieres = 38, 7, ["n", "s"]   # charnières des vantaux, du nord au sud
JOUE_C2 = 118                                   # face nord de la joue du frigo
BAIE_Y0, BAIE_Y1 = CLOISON_Y1, JOUE_C2 - MONTANT
_somme = BAIE_Y1 - BAIE_Y0 - 10
VANTAUX_L = [_somme] if len(_charnieres) == 1 else [20, _somme - 20]
DORMANT, EP_VANTAIL, X_PORTE = 4.5, 4, 323.5     # x : axe de la cloison
ENVELOPPE += [
    Bloc("cloison", "cloison_cellier", 320, 327, 0, CLOISON_Y1, 0, H),
    Bloc("cloison", "montant_cellier", 320, 327, BAIE_Y1, JOUE_C2, 0, H),
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
    MEUBLES.append(Bloc("facade", f"facade_{nom}", x0, x1, P_CAISSON, P_CAISSON + FACADE, SOCLE, CAISSON_H))


# Meubles hauts : caisson P33 + façade 2, h 153 → 243 (remontés de 5 en V11.8 : 62 au-dessus du plan),
# fileur de 7 jusqu'au plafond.
HAUT_Z0, HAUT_Z1, P_HAUT = 153, 243, 33


def meuble_haut_nord(nom, x0, largeur):
    x1 = x0 + largeur
    MEUBLES.append(Bloc("caisson_haut", f"caisson_{nom}", x0, x1, 0, P_HAUT, HAUT_Z0, HAUT_Z1, nom.upper()))
    MEUBLES.append(Bloc("facade_haut", f"facade_{nom}", x0, x1, P_HAUT, P_HAUT + FACADE, HAUT_Z0, HAUT_Z1))


# mur nord : 5 meubles bas de 60, à 10 du mur ouest (x 10 → 310) ; plaque sur B2, LV en B3, évier sur B4
ECART_OUEST = 10
N_BAS, N_HAUTS = 5, 4
B_PLAQUE, B_LV, B_EVIER = 2, 3, 4
for i in range(N_BAS):
    meuble_bas_nord(f"b{i + 1}", ECART_OUEST + 60 * i, 60)



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
RESEAUX = [
    ("alim", "alim_evier", [NOURRICE, (NOURRICE[0], 47), (431, 47), (431, 3), (xe, 3), (xe, 8)], 50, 0.8),
    ("alim", "alim_lv", [(xe, 3), (xl1 - 15, 3), (xl1 - 15, 20)], 50, 0.8),
    ("evac", "evac_evier", [SIPHON, (xe, 10), (422, 10), (422, 56), (472, 56), (472, 88), (CHUTE[0], 88), CHUTE], 43, 2),
    ("evac", "evac_lv", [(xl0 + 20, 30), (xl0 + 20, 10), (xe, 10)], 43, 2),
]
_ev = RESEAUX[2][2]
EVAC_LONGUEUR = round(sum(math.dist(a, b) for a, b in zip(_ev, _ev[1:])))

# mur nord : 5 meubles hauts de 60, décalés d'un demi-meuble : ils partent du milieu du premier bas (x 40 → 340)
DEPART_HAUTS = ECART_OUEST + 60 / 2
for i in range(N_HAUTS):
    meuble_haut_nord(f"h{i + 1}", DEPART_HAUTS + 60 * i, 60)
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


def colonne_est(nom, y0, largeur, facades, etiq):
    """facades : (rôle, nom, z0, z1), de bas en haut."""
    y1 = y0 + largeur
    MEUBLES.append(Bloc("socle", f"socle_{nom}", COL_X + 5, COL_DOS, y0, y1, 0, SOCLE))
    MEUBLES.append(Bloc("colonne", f"caisson_{nom}", COL_X + FACADE, COL_DOS, y0, y1, SOCLE, COL_Z1, etiq))
    for role, n, z0, z1 in facades:
        MEUBLES.append(Bloc(role, f"{n}_{nom}", COL_X, COL_X + FACADE, y0, y1, z0, z1))


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
# Banquette du mur ouest (x 0 → 106), contre le mur sud : assise 45 (h 45, coffre dessous), dossier 5 (h 85).
BANQ = dict(x0=0, x1=106, y0=Y_MUR_SUD - 50, y1=Y_MUR_SUD)
MEUBLES += [
    Bloc("banquette", "banquette_assise", BANQ["x0"], BANQ["x1"], BANQ["y0"], BANQ["y1"] - 5, 0, 45, "banquette"),
    Bloc("banquette", "banquette_dossier", BANQ["x0"], BANQ["x1"], BANQ["y1"] - 5, BANQ["y1"], 0, 85),
]
# Table ronde Ø 80 à pied tulipe (h 75) devant la banquette : le plateau la recouvre de 15 ; une chaise à l'est.
TABLE = dict(cx=(BANQ["x0"] + BANQ["x1"]) / 2, cy=BANQ["y0"] + 15 - 40, r=40)
MEUBLES += [
    Cyl("table", "plateau", TABLE["cx"], TABLE["cy"], TABLE["r"], 72, 75),
    Cyl("pied", "pied_table", TABLE["cx"], TABLE["cy"], 4, 2, 72),
    Cyl("pied", "embase_table", TABLE["cx"], TABLE["cy"], 20, 0, 2),
]


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


def rayonnage(nom, x0, x1, y0, y1, zs, montants_en_x=True, z1=COL_Z1):
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
        MEUBLES.append(Bloc("etagere", f"etag_{nom}_{k + 1}", xi0, xi1, yi0, yi1, z, z + EP))
    return xi1 - xi0 if montants_en_x else yi1 - yi0


# Deux balais accrochés sur le flanc nord du frigo (joue de C2, y 118), derrière le grand vantail ouvert : crochets
# h 150, manches h 22 → 150, têtes de 24 × 6 à plat contre la joue (y 112 → 118), h 8 → 22, après le montant de la
# porte (x 327). Le grand vantail ouvert à 90° (face côté cellier à y 106) laisse 6 devant les têtes.
BALAIS = [343, 369]                              # axes des balais (x)
for k, xc in enumerate(BALAIS):
    MEUBLES.append(Bloc("ratelier", f"crochet_balai_{k + 1}", xc - 1, xc + 1, JOUE_C2 - 3, JOUE_C2, 148, 151))
    MEUBLES.append(Cyl("manche", f"manche_balai_{k + 1}", xc, JOUE_C2 - 2.5, 1.2, 22, 150))
    MEUBLES.append(Bloc("balai", f"tete_balai_{k + 1}", xc - 12, xc + 12, JOUE_C2 - 6, JOUE_C2, 8, 22))

# Rayonnage toute hauteur P40 contre le mur nord, jusqu'au mur de l'alcôve (x 434) : 6 tablettes, la première à h 60
# au-dessus des réseaux (h 43 → 50) qui passent dessous. Il part de la cloison (x 329) : le petit vantail balaie
# y 42 → 62, au-delà de sa profondeur (y 40).
# Plus de rayonnage devant le ballon : nourrice, groupe de sécurité et chute restent accessibles directement.
_nord_x0 = 329 if BAIE_Y0 + DORMANT >= 41 else math.ceil(X_PORTE + EP_VANTAIL / 2 + VANTAUX_L[0] + 1.5)
RAYON_NORD = dict(x0=_nord_x0, x1=434, y0=0, y1=40, zs=[60, 96, 132, 168, 204, 238])
L_NORD = rayonnage("nord", RAYON_NORD["x0"], RAYON_NORD["x1"], RAYON_NORD["y0"], RAYON_NORD["y1"], RAYON_NORD["zs"])

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
]

# ------------------------------------------------------------------ volumes de rangement
# Volume brut des caissons fermés (largeur × profondeur du caisson × hauteur des façades de rangement), en litres.
# Électroménager, socles et niches techniques exclus ; le sous-évier est compté à part.
def litres(l, p, h):
    return l * p * h / 1000


_BAS_LIBRES = [n for n in range(1, N_BAS + 1) if n not in (B_PLAQUE, B_LV, B_EVIER)]
RANGEMENT_V11 = [
    (", ".join(f"B{n}" for n in _BAS_LIBRES) + " : bas 60",
     len(_BAS_LIBRES) * litres(60, P_CAISSON, CAISSON_H - SOCLE), f"{len(_BAS_LIBRES)} × 60 × 58 × 72"),
    (f"B{B_PLAQUE} : tiroir sous la plaque aspirante", litres(60, P_CAISSON, 46), "60 × 58 × 46 (moteur au-dessus)"),
    (f"H1 → H{N_HAUTS} : hauts", N_HAUTS * litres(60, P_HAUT, HAUT_Z1 - HAUT_Z0), f"{N_HAUTS} × 60 × 33 × 90"),
    ("C1 : tiroirs + porte haute (four, micro-ondes)", litres(60, P_CAISSON, (86 - SOCLE) + (COL_Z1 - MO_Z1)),
     f"60 × 58 × (71 + {COL_Z1 - MO_Z1})"),
    ("C2 : porte haute du frigo", litres(60, P_CAISSON, COL_Z1 - 193), f"60 × 58 × {COL_Z1 - 193}"),
] + [
    # cellier fermé : largeur utile × profondeur × hauteur, de la première tablette au haut du rayonnage
    ("Cellier : rayonnage du mur nord", litres(L_NORD, RAYON_NORD["y1"], COL_Z1 - RAYON_NORD["zs"][0]),
     f"{L_NORD} × {RAYON_NORD['y1']} × {COL_Z1 - RAYON_NORD['zs'][0]}"),
]
# Proposition 9, variante A (cuisine-plan.html V3.x), cotes reprises de 3d/cuisine_a.py
RANGEMENT_P9A = [
    ("Tiroirs 40", litres(40, 58, 72), "40 × 58 × 72"),
    ("Tiroir sous la plaque aspirante", litres(60, 58, 46), "60 × 58 × 46"),
    ("Tiroirs 80", litres(80, 58, 72), "80 × 58 × 72"),
    ("Hauts (épicerie 2 × 40 + 60)", litres(140, 33, 90), "140 × 33 × 90"),
    ("Colonne LV : tiroir + vaisselier", litres(60, 58, 23 + 118), "60 × 58 × (23 + 118)"),
    ("Colonne frigo : porte haute", litres(59, 57, 45), "59 × 57 × 45"),
    ("Colonne four : tiroirs + abattant", litres(59, 57, 71 + 50), "59 × 57 × (71 + 50)"),
    ("Meuble café P28", litres(52, 28, 72), "52 × 28 × 72"),
    ("Cellier : 6 étagères P30 (h 20 → 214)", litres(38, 30, 194), "38 × 30 × 194"),
]
SOUS_EVIER = dict(v11=litres(60, P_CAISSON, CAISSON_H - SOCLE), p9a=litres(60, 58, 72))
# rangements ouverts, en cm linéaires d'étagère
OUVERT_V11 = [(f"Cellier, mur nord : {len(RAYON_NORD['zs'])} tablettes P{RAYON_NORD['y1']} de {L_NORD}", len(RAYON_NORD["zs"]) * L_NORD)]
OUVERT_P9A = [("Étagères P30 épices + enceinte (2 × 109)", 218), ("Étagère haute P25, mur sud", 140),
              ("Cellier : 6 étagères P30 de 38", 228), ("Porte d'entrée : 3 étagères P6 de 62", 186)]

# ------------------------------------------------------------------ historique (section Changements)
CHANGEMENTS = [
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
