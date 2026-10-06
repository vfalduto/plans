# Cuisine V11 : source unique.
#
# Ce fichier ne contient que des données : il est lu par plan.py (HTML : plan et élévations,
# projetés depuis ces volumes) et par cad.py (FreeCAD → .FCStd / .glb). Toute modification
# se fait ici, jamais dans le HTML ni dans le modèle 3D.
#
# Cotes en cm : x vers l'est, y vers le sud (comme le plan), z depuis le sol fini.
# Chaque volume : Bloc(role, nom, x0, x1, y0, y1, z0, z1). Le rôle fixe le style du plan
# et le matériau du rendu.

from dataclasses import dataclass

VERSION = "V11.13"
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
    # réseaux existants
    Bloc("tech", "coffrage_chute", 418, 434, 0, 18, 0, H),
    # cloison neuve du cellier (7) à 10 de B5 (x 320 → 327), du mur nord à y 120, puis retour vers l'est contre
    # le nord de E1 (y 113 → 120) jusqu'au mur du WC ; baie de 50 face ouest (y 63 → 113, h 204), porte à définir
    Bloc("cloison", "cloison_cellier", 320, 327, 0, 63, 0, H),
    Bloc("linteau", "linteau_cellier", 320, 327, 63, 113, 204, H),
    Bloc("cloison", "cloison_cellier_retour", 320, 382, 113, 120, 0, H),
    # porte d'entrée battante, vantail 73 × 204 dans la baie (huisserie 2), charnières à l'est (fermée)
    Bloc("porte", "entree_vantail", 231, 304, 252, 256, 0, 204),
]
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
# sol du cellier fermé (x 389 → 434 moins la chute, + niche du ballon x 434 → 484, y 44 → 100)
CELLIER_SOL = [(327, 0), (418, 0), (418, 18), (434, 18), (434, 44), (484, 44), (484, 100), (382, 100), (382, 113),
               (327, 113)]
BAIE_CELLIER = dict(x0=320, x1=327, y0=63, y1=113, h=204)
ZONES = [("cellier", 380, 60)]
WC = [(392, 110), (484, 110), (484, 252), (392, 252)]
FENETRE = dict(y0=58, y1=200, allege=106, linteau=215)
# porte d'entrée : battante, poussant à droite vue du couloir (charnières à l'est), s'ouvre vers la cuisine
ENTREE = dict(x0=228, x1=306, h=204, charniere=(304, 252), vantail=73)

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


# mur nord : 5 meubles bas de 60, à 10 du mur ouest (x 10 → 310) ; plaque sur B3, LV en B4, évier sur B5
ECART_OUEST = 10
N_BAS, N_HAUTS = 5, 4
B_PLAQUE, B_LV, B_EVIER = 3, 4, 5
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
# Alimentation EF/EC depuis la nourrice sous le ballon, évacuation vers la chute (coffrage x 418 → 434).
# (rôle, nom, points (x, y), z, rayon)
CHUTE = (426, 9)
NOURRICE = (470, 52)
xe = (sur_bas(B_EVIER)[0] + sur_bas(B_EVIER)[1]) / 2   # axe de l'évier
xl0, xl1 = sur_bas(B_LV)
SIPHON = (xe, 32)
RESEAUX = [
    ("alim", "alim_evier", [NOURRICE, (432, 52), (432, 4), (xe, 4), (xe, 8)], 50, 0.8),
    ("alim", "alim_lv", [(xe, 4), (xl1 - 15, 4), (xl1 - 15, 20)], 50, 0.8),
    ("evac", "evac_evier", [SIPHON, (xe, 10), CHUTE], 43, 2),
    ("evac", "evac_lv", [(xl0 + 20, 30), (xl0 + 20, 10), (xe, 10)], 43, 2),
]
EVAC_LONGUEUR = (SIPHON[1] - 10) + (CHUTE[0] - xe)

# mur nord : 5 meubles hauts de 60, décalés d'un demi-meuble : ils partent du milieu du premier bas (x 40 → 340)
DEPART_HAUTS = ECART_OUEST + 60 / 2
for i in range(N_HAUTS):
    meuble_haut_nord(f"h{i + 1}", DEPART_HAUTS + 60 * i, 60)
MEUBLES.append(Bloc("fileur", "fileur_hauts", DEPART_HAUTS, DEPART_HAUTS + N_HAUTS * 60, P_HAUT, P_HAUT + FACADE, HAUT_Z1, H))

# ------------------------------------------------------------------ colonnes, mur sud
# Colonnes P60 (caisson 58 + façade 2), socle 15, dessus aligné sur les hauts, contre le mur sud, x 106 → 226.
Y_MUR_SUD = 252
COL_DOS = Y_MUR_SUD                       # contre le mur sud
COL_Y0 = COL_DOS - P_CAISSON - FACADE     # nu des façades, y 192
COL_Z1 = HAUT_Z1
COL_X1 = 226                              # 2 avant le montant ouest de la porte (x 228)
COL_X0 = COL_X1 - 2 * 60


def colonne_sud(nom, x0, largeur, facades, etiq):
    """facades : (rôle, nom, z0, z1), de bas en haut."""
    x1 = x0 + largeur
    MEUBLES.append(Bloc("socle", f"socle_{nom}", x0, x1, COL_Y0 + 5, COL_DOS, 0, SOCLE))
    MEUBLES.append(Bloc("colonne", f"caisson_{nom}", x0, x1, COL_Y0 + FACADE, COL_DOS, SOCLE, COL_Z1, etiq))
    for role, n, z0, z1 in facades:
        MEUBLES.append(Bloc(role, f"{n}_{nom}", x0, x1, COL_Y0, COL_Y0 + FACADE, z0, z1))


# C1 : four 60 à h 88 → 148 (2 tiroirs dessous, rangement dessus)
colonne_sud("c1", COL_X0, 60, [
    ("facade_col", "tiroir_1", SOCLE, 50), ("facade_col", "tiroir_2", 50, 86), ("facade_col", "bandeau", 86, 88),
    ("four", "four", 88, 148), ("facade_col", "porte_haute", 148, COL_Z1)], "C1 four")
# C2 : réfrigérateur intégrable (niche 178), porte de rangement au-dessus
colonne_sud("c2", COL_X0 + 60, 60, [
    ("facade_col", "frigo", SOCLE, 193), ("facade_col", "porte_haute", 193, COL_Z1)], "C2 frigo")
MEUBLES.append(Bloc("fileur", "fileur_colonnes", COL_X0, COL_X1, COL_Y0, COL_Y0 + FACADE, COL_Z1, H))
# joue de fermeture du couloir côté ouest (le vantail ne va pas au-delà de x 144)

# ------------------------------------------------------------------ mur est : deux meubles bas de 60, P40
# Contre le mur du WC (x 382), du décroché (y 240) vers le nord : E2 y 180 → 240, E1 y 120 → 180.
# Caisson P38 + façade 2, socle 15, plan de travail 4 (P42) au même niveau que la rangée nord.
P_EST = 38
X_MUR_EST = 382


def meuble_bas_est(nom, y0, largeur):
    y1 = y0 + largeur
    x = X_MUR_EST - P_EST
    MEUBLES.append(Bloc("socle", f"socle_{nom}", x + 5, X_MUR_EST, y0, y1, 0, SOCLE))
    MEUBLES.append(Bloc("caisson", f"caisson_{nom}", x, X_MUR_EST, y0, y1, SOCLE, CAISSON_H, nom.upper()))
    MEUBLES.append(Bloc("facade", f"facade_{nom}", x - FACADE, x, y0, y1, SOCLE, CAISSON_H))


meuble_bas_est("e1", 120, 60)
MEUBLES.append(Bloc("plan", "plan_est", X_MUR_EST - P_EST - FACADE - 2, X_MUR_EST, 120, 180, CAISSON_H, CAISSON_H + 4))
# E2 : placard toute hauteur P40 (dessus aligné sur les colonnes et les hauts, fileur jusqu'au plafond)
_xe2 = X_MUR_EST - P_EST
MEUBLES += [
    Bloc("socle", "socle_e2", _xe2 + 5, X_MUR_EST, 180, 240, 0, SOCLE),
    Bloc("colonne", "caisson_e2", _xe2, X_MUR_EST, 180, 240, SOCLE, COL_Z1, "E2"),
    Bloc("facade_col", "porte_e2", _xe2 - FACADE, _xe2, 180, 240, SOCLE, COL_Z1),
    Bloc("fileur", "fileur_e2", _xe2 - FACADE, _xe2, 180, 240, COL_Z1, H),
]

# ------------------------------------------------------------------ triangle d'activité (centres de l'évier et de la plaque,
# milieu de la façade du frigo)
_plaque = next(b for b in MEUBLES if b.role == "plaque")
_cuve = next(b for b in MEUBLES if b.role == "cuve")
_frigo = next(b for b in MEUBLES if b.nom == "caisson_c2")
TRIANGLE = [("frigo", ((_frigo.x0 + _frigo.x1) / 2, COL_Y0)),
            ("évier", ((_cuve.x0 + _cuve.x1) / 2, (_cuve.y0 + _cuve.y1) / 2)),
            ("plaque", ((_plaque.x0 + _plaque.x1) / 2, (_plaque.y0 + _plaque.y1) / 2))]


# ------------------------------------------------------------------ coin repas : banquette et table, angle sud-ouest
# Banquette du mur ouest jusqu'à C1 (x 0 → 98), contre le mur sud : assise 45 (h 45, coffre dessous), dossier 5 (h 85).
BANQ = dict(x0=0, x1=COL_X0, y0=Y_MUR_SUD - 50, y1=Y_MUR_SUD)
MEUBLES += [
    Bloc("banquette", "banquette_assise", BANQ["x0"], BANQ["x1"], BANQ["y0"], BANQ["y1"] - 5, 0, 45, "banquette"),
    Bloc("banquette", "banquette_dossier", BANQ["x0"], BANQ["x1"], BANQ["y1"] - 5, BANQ["y1"], 0, 85),
]
# Table ronde Ø 80 à pied tulipe (h 75) devant la banquette : le plateau la recouvre de 15 ; une chaise en face.
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
CHAISE_Y0 = TABLE["cy"] - TABLE["r"] + GLISSE - 42
chaise("chaise_1", TABLE["cx"] - 21, CHAISE_Y0, "n")

# ------------------------------------------------------------------ ouvertures de l'électroménager (plan seulement)
# abattant : emprise de la porte abattue (x0, x1, y0, y1) ; battant : charnière (x, y), largeur, sens d'ouverture.
_lv = sur_bas(B_LV)
OUVERTURES = [
    ("abattant", "LV", (_lv[0], _lv[1], P_CAISSON + FACADE, P_CAISSON + FACADE + CAISSON_H - SOCLE)),
    ("abattant", "four", (COL_X0, COL_X0 + 60, COL_Y0 - 60, COL_Y0)),
    # frigo : charnières à l'est (côté porte d'entrée), la porte s'ouvre vers l'ouest ; dessinée à 90°
    ("battant", "frigo", ((COL_X1, COL_Y0), 60, "ouest")),
]

# ------------------------------------------------------------------ volumes de rangement
# Volume brut des caissons fermés (largeur × profondeur du caisson × hauteur des façades de rangement), en litres.
# Électroménager, socles et niches techniques exclus ; le sous-évier est compté à part.
def litres(l, p, h):
    return l * p * h / 1000


RANGEMENT_V11 = [
    ("B1, B2 : bas 60", 2 * litres(60, P_CAISSON, CAISSON_H - SOCLE), "2 × 60 × 58 × 72"),
    ("B3 : tiroir sous la plaque aspirante", litres(60, P_CAISSON, 46), "60 × 58 × 46 (moteur au-dessus)"),
    (f"H1 → H{N_HAUTS} : hauts", N_HAUTS * litres(60, P_HAUT, HAUT_Z1 - HAUT_Z0), f"{N_HAUTS} × 60 × 33 × 90"),
    ("C1 : tiroirs + porte haute du four", litres(60, P_CAISSON, (86 - SOCLE) + (COL_Z1 - 148)),
     f"60 × 58 × (71 + {COL_Z1 - 148})"),
    ("C2 : porte haute du frigo", litres(60, P_CAISSON, COL_Z1 - 193), f"60 × 58 × {COL_Z1 - 193}"),
    ("E1 : bas 60 P40, mur est", litres(60, P_EST, CAISSON_H - SOCLE), f"60 × {P_EST} × 72"),
    ("E2 : placard toute hauteur P40", litres(60, P_EST, COL_Z1 - SOCLE), f"60 × {P_EST} × {COL_Z1 - SOCLE}"),
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
]
SOUS_EVIER = dict(v11=litres(60, P_CAISSON, CAISSON_H - SOCLE), p9a=litres(60, 58, 72))
# rangements ouverts, en cm linéaires d'étagère
OUVERT_V11 = [("Cellier : à aménager (≈ 45 × 100, chute dans l'angle)", 0)]
OUVERT_P9A = [("Étagères P30 épices + enceinte (2 × 109)", 218), ("Étagère haute P25, mur sud", 140),
              ("Cellier : 6 étagères P30 de 38", 228), ("Porte d'entrée : 3 étagères P6 de 62", 186)]

# ------------------------------------------------------------------ historique (section Changements)
CHANGEMENTS = [
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
