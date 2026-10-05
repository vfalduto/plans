# Modèle 3D de la cuisine, variante A (cuisine-plan.html, V3.3), table carrée 70 × 70.
#
# Lancement (sans interface) :
#   /Applications/FreeCAD.app/Contents/Resources/bin/freecadcmd 3d/cuisine_a.py
#
# Cotes en cm, reprises du plan et des coupes : x vers l'est, y vers le sud (comme le plan SVG),
# z depuis le sol fini. Dans FreeCAD : X = x, Y = -y (nord en haut), Z = z, en mm.
# Chaque objet s'appelle « matériau__élément » : Blender choisit le matériau d'après le préfixe.
#
# Produit dans 3d/sortie/ : cuisine-a.FCStd (décoration dans le groupe « Decoration »),
# cuisine-a.glb / .obj (sans décoration), cuisine-a-deco.glb / .obj (avec), cuisine-a.dxf (plan 2D par calques).

import os
import FreeCAD
import Part
import Mesh
from FreeCAD import Vector as V

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "sortie")
os.makedirs(OUT, exist_ok=True)

doc = FreeCAD.newDocument("cuisine_a")
objs = []        # objets FreeCAD du projet
deco = []        # objets de décoration (exportés à part)
_deco = [False]
plan2d = []      # (calque, "rect"|"circle", données) pour le DXF
_names = {}
_layer = ["divers"]


def calque(nom):
    _layer[0] = nom


def _add(mat, name, shape, foot):
    key = f"{mat}__{name}"
    n = _names.get(key, 0)
    _names[key] = n + 1
    if n:
        key = f"{key}_{n + 1}"
    o = doc.addObject("Part::Feature", key)
    o.Shape = shape
    (deco if _deco[0] else objs).append(o)
    if foot:
        plan2d.append((_layer[0],) + foot)
    return o


def solid(x0, x1, y0, y1, z0, z1):
    return Part.makeBox((x1 - x0) * 10, (y1 - y0) * 10, (z1 - z0) * 10, V(x0 * 10, -y1 * 10, z0 * 10))


def box(mat, name, x0, x1, y0, y1, z0, z1, plan=True):
    return _add(mat, name, solid(x0, x1, y0, y1, z0, z1), ("rect", (x0, y0, x1, y1)) if plan else None)


def cyl(mat, name, cx, cy, r, z0, z1, plan=True):
    s = Part.makeCylinder(r * 10, (z1 - z0) * 10, V(cx * 10, -cy * 10, z0 * 10))
    return _add(mat, name, s, ("circle", (cx, cy, r)) if plan else None)


def handle(name, x0, x1, y0, y1, z0, z1):
    box("inox", "poignee_" + name, x0, x1, y0, y1, z0, z1, plan=False)


J = 0.15  # demi-jeu entre façades


BAS = "facade_couleur"     # meubles bas et hauts
COL = "facade_noyer"    # meubles toute hauteur
# Poignées : profilé toute longueur, dans le matériau de la façade, saillie 2,5, épaisseur 1,5.
# « haut » / « bas » : le long du chant haut ou bas ; « g » / « d » / « n » : le long du chant vertical.


def front_s(name, x0, x1, z0, z1, y, mat, poignee="haut"):
    """Façade tournée vers le sud, posée de y-2 à y (y = nu des façades)."""
    box(mat, name, x0 + J, x1 - J, y - 2, y, z0 + J, z1 - J, plan=False)
    a, b = x0 + J, x1 - J
    if poignee == "haut":
        box(mat, "poignee_" + name, a, b, y, y + 2.5, z1 - 2.5, z1 - J, plan=False)
    elif poignee == "bas":
        box(mat, "poignee_" + name, a, b, y, y + 2.5, z0 + J, z0 + 2.5, plan=False)
    elif poignee == "g":
        box(mat, "poignee_" + name, a, a + 1.5, y, y + 2.5, z0 + J, z1 - J, plan=False)
    elif poignee == "d":
        box(mat, "poignee_" + name, b - 1.5, b, y, y + 2.5, z0 + J, z1 - J, plan=False)


def front_w(name, y0, y1, z0, z1, x, mat, poignee=None):
    """Façade tournée vers l'ouest, posée de x à x+2."""
    box(mat, name, x, x + 2, y0 + J, y1 - J, z0 + J, z1 - J, plan=False)
    a, b = y0 + J, y1 - J
    if poignee == "haut":
        box(mat, "poignee_" + name, x - 2.5, x, a, b, z1 - 2.5, z1 - J, plan=False)
    elif poignee == "bas":
        box(mat, "poignee_" + name, x - 2.5, x, a, b, z0 + J, z0 + 2.5, plan=False)
    elif poignee == "n":
        box(mat, "poignee_" + name, x - 2.5, x, a, a + 1.5, z0 + J, z1 - J, plan=False)


# ------------------------------------------------------------------ bâti
calque("murs")
H = 250
box("mur", "nord", -20, 434, -20, 0, 0, H)
box("mur", "nord_cellier", 434, 494, -20, 44, 0, H)
box("mur", "est_wc", 484, 494, 44, 262, 0, H)
box("mur", "cellier_wc", 382, 484, 100, 110, 0, H)
box("mur", "ouest_wc", 382, 392, 110, 262, 0, H)
# mur ouest et fenêtre (y 58 → 200, allège 106, linteau 215)
box("mur", "ouest_nord", -20, 0, 0, 58, 0, H)
box("mur", "ouest_sud", -20, 0, 200, 262, 0, H)
box("mur", "allege", -20, 0, 58, 200, 0, 106)
box("mur", "linteau_fenetre", -20, 0, 58, 200, 215, H)
# mur sud et baie d'entrée 78 × 204 (x 228 → 306)
box("mur", "sud_ouest", 0, 228, 252, 262, 0, H)
box("mur", "sud_est", 306, 382, 252, 262, 0, H)
box("mur", "linteau_entree", 228, 306, 252, 262, 204, H)
box("mur", "sud_wc", 483, 484, 252, 262, 0, H)
box("mur", "decroche_se", 341, 382, 240, 252, 0, H)
# cloison neuve x 312 → 317 et baie du cellier 58 (y 62 → 120)
calque("cloisons")
box("mur", "cloison_cellier", 312, 317, 0, 62, 0, H)
box("mur", "linteau_cellier", 312, 317, 62, 120, 238, H)
box("mur", "montant_cellier", 312, 317, 120, 122, 0, H)
box("mur", "gaine", 371, 382, 122, 240, 0, H)
box("mur", "coffrage_chute", 418, 434, 0, 18, 0, H)

calque("sols")
box("sol_bois", "cuisine", 0, 312, 0, 252, -2, 0)
box("sol_bois", "seuil_entree", 228, 306, 252, 262, -2, 0)
cell = Part.Face(Part.makePolygon([V(x * 10, -y * 10, -20) for x, y in
                                   [(317, 0), (434, 0), (434, 44), (484, 44), (484, 100), (382, 100),
                                    (382, 122), (312, 122), (312, 62), (317, 62), (317, 0)]]))
_add("sol_carrelage", "cellier", cell.extrude(V(0, 0, 20)), None)
box("sol_carrelage", "wc", 392, 484, 110, 252, -2, 0, plan=False)
# amorce du couloir derrière la porte d'entrée (vue par la baie)
box("sol_bois", "couloir", 180, 382, 262, 330, -2, 0, plan=False)
box("mur", "couloir_fond", 180, 382, 330, 340, 0, H, plan=False)
box("plafond", "couloir", 180, 382, 262, 330, H, H + 2, plan=False)
box("plafond", "plafond", -20, 494, -20, 262, H, H + 2, plan=False)

# ------------------------------------------------------------------ fenêtre coulissante
calque("fenetre")
box("menuiserie", "appui", -20, 0, 58, 200, 105, 106)


def vantail(name, x0, x1, y0, y1):
    outer = solid(x0, x1, y0, y1, 106, 215)
    inner = solid(x0 - 1, x1 + 1, y0 + 5, y1 - 5, 111, 210)
    _add("menuiserie", name, outer.cut(inner), None)
    box("verre", name, (x0 + x1) / 2 - 0.3, (x0 + x1) / 2 + 0.3, y0 + 5, y1 - 5, 111, 210, plan=False)


vantail("vantail_fixe", -9, -6, 58, 131)
vantail("vantail_mobile", -16, -13, 127, 200)

# ------------------------------------------------------------------ rangée nord (décalée de 7)
calque("meubles_bas")
box("socle", "rangee_nord", 0, 312, 0, 55, 0, 15)
box("caisson", "bas_nord", 9, 249, 0, 58, 15, 87)
front_s("fileur_9", 0, 9, 15, 87, 60, BAS, poignee=None)
for i, (z0, z1) in enumerate([(15, 39), (39, 63), (63, 87)]):
    front_s(f"tiroirs40_{i + 1}", 9, 49, z0, z1, 60, BAS)
front_s("tiroir_plaque", 49, 109, 15, 61, 60, BAS)
front_s("bandeau_plaque", 49, 109, 61, 87, 60, BAS, poignee=None)
for i, (z0, z1) in enumerate([(15, 40), (40, 65), (65, 87)]):
    front_s(f"tiroirs80_{i + 1}", 109, 189, z0, z1, 60, BAS)
front_s("sous_evier", 189, 249, 15, 87, 60, BAS)

# plan de travail 4 cm (x 0 → 249, profondeur 62), percé pour le bac de l'évier
calque("plan_de_travail")
bac = (203, 243, 10, 50)
wt = solid(0, 249, 0, 62, 87, 91).cut(solid(*bac, 70, 92))
_add("plan", "rangee_nord", wt, ("rect", (0, 0, 249, 62)))

# évier monobloc inox 86 collé : égouttoir à gauche, bac 40 × 40 × 20
plate = solid(161, 247, 6, 56, 91, 91.4).cut(solid(*bac, 70, 92))
_add("inox", "evier_plage", plate, ("rect", (161, 6, 247, 56)))
basin = solid(bac[0] - 0.5, bac[1] + 0.5, bac[2] - 0.5, bac[3] + 0.5, 70.5, 91).cut(solid(*bac, 71, 92))
_add("inox", "evier_bac", basin, None)
for k in range(6):  # rainures de l'égouttoir
    box("inox", f"egouttoir_{k}", 168, 196, 15 + 6 * k, 16 + 6 * k, 91.4, 91.7, plan=False)
# mitigeur inox
cyl("inox", "mitigeur", 223, 8, 1.6, 91.4, 122)
s = Part.makeCylinder(10, 180, V(2230, -80, 1200), V(0, -1, 0))
_add("inox", "bec", s, None)
cyl("inox", "bec_sortie", 223, 26, 1, 113, 121, plan=False)

# induction 60 à hotte intégrée
box("vitro", "induction", 52, 106, 6, 56, 91, 91.6)
box("noir", "aspiration", 75, 83, 9, 53, 91.6, 91.8, plan=False)

# crédence
box("credence", "nord", 0, 249, 0, 1, 91, 148, plan=False)
box("credence", "sous_etageres", 0, 109, 0, 1, 148, 159, plan=False)

# étagères ouvertes P30 (h 162 et 200) et meubles hauts P35 (h 148 → 238)
calque("meubles_hauts")
box("etagere", "epices", 0, 109, 1, 30, 159, 162)
box("etagere", "enceinte", 0, 109, 1, 30, 197, 200, plan=False)
box("caisson", "hauts_nord", 109, 249, 0, 33, 148, 238)
front_s("epicerie_g", 109, 149, 148, 238, 35, BAS, poignee="bas")
front_s("epicerie_d", 149, 189, 148, 238, 35, BAS, poignee="bas")
front_s("haut_60", 189, 249, 148, 238, 35, BAS, poignee="bas")

# colonne LV surélevée + fileur 3
calque("colonnes")
box("caisson", "colonne_lv", 249, 309, 0, 58, 15, 238)
front_s("tiroir_lv", 249, 309, 15, 38, 60, COL)
front_s("lave_vaisselle", 249, 309, 38, 120, 60, COL)
front_s("vaisselier", 249, 309, 120, 238, 60, COL, poignee="g")
front_s("fileur_3", 309, 312, 0, 238, 60, COL, poignee=None)

# ------------------------------------------------------------------ mur est : frigo et four au nu x 312
box("socle", "colonnes_est", 316, 371, 122, 240, 0, 15)
box("caisson", "frigo", 314, 371, 122, 181, 15, 238)
box("caisson", "four", 314, 371, 181, 240, 15, 238)
front_w("frigo_bas", 122, 181, 15, 193, 312, COL, poignee="n")
front_w("frigo_haut", 122, 181, 193, 238, 312, COL, poignee="n")
front_w("four_tiroir_1", 181, 240, 15, 50, 312, COL, poignee="haut")
front_w("four_tiroir_2", 181, 240, 50, 86, 312, COL, poignee="haut")
front_w("four_niche_bas", 181, 240, 86, 88, 312, COL)
box("noir", "four", 312, 314, 181.5, 239.5, 88, 148, plan=False)
box("verre_fume", "four_porte", 311.6, 312, 185, 236, 92, 140, plan=False)
handle("four", 310, 311.6, 186, 235, 143.5, 145)
front_w("four_entre", 181, 240, 148, 150, 312, COL)
box("noir", "micro_ondes", 312, 314, 181.5, 239.5, 150, 188, plan=False)
box("verre_fume", "micro_ondes_porte", 311.6, 312, 184, 225, 153, 185, plan=False)
front_w("abattant", 181, 240, 188, 238, 312, COL, poignee="bas")
front_w("bandeau_colonnes", 122, 240, 238, H, 312, COL)
front_w("fileur_12", 240, 252, 0, H, 312, COL)
box(COL, "fileur_12_retour", 312, 341, 250.5, 252, 0, H, plan=False)

# porte battante du cellier : huisserie, vantail 53 ouvert à 90° dans le sas
calque("portes")
box("porte_peinte", "huisserie_n", 312, 317, 62, 65, 0, 238)
box("porte_peinte", "huisserie_s", 312, 317, 118, 120, 0, 238)
box("porte_peinte", "huisserie_haut", 312, 317, 62, 120, 237, 238, plan=False)
box("porte_peinte", "cellier_vantail", 316, 369, 114, 118, 1, 237)
handle("cellier", 360, 364, 118, 120.5, 103, 104)

# porte d'entrée coulissante côté cuisine, ouverte vers la table (x 144 → 226)
box("noir", "rail_entree", 142, 310, 246.5, 250.5, 212, 222)
box("porte_bois", "entree_vantail", 144, 226, 246, 250, 1, 211)
for zz in (165, 182, 199):
    box("etagere", f"porte_p6_{zz}", 154, 216, 240, 246, zz - 1.6, zz, plan=zz == 165)
    box("inox", f"porte_galerie_{zz}", 154, 216, 240, 240.4, zz, zz + 3, plan=False)
box("ardoise", "porte", 154, 216, 245.4, 246, 85, 155, plan=False)
handle("entree", 220, 221, 250, 252.5, 100, 130)

# ------------------------------------------------------------------ coin repas (table carrée 70 × 70)
calque("coin_repas")
box("socle", "cafe", 0, 27, 200, 252, 0, 15)
box("caisson", "cafe", 0, 28, 200, 252, 15, 87)
box(BAS, "cafe", 28, 30, 200 + J, 252 - J, 15 + J, 87 - J, plan=False)
box(BAS, "poignee_cafe", 30, 32.5, 200 + J, 252 - J, 84.5, 87 - J, plan=False)
box("plan", "cafe", 0, 30, 200, 252, 87, 91)
box("noir", "machine_cafe", 3, 27, 214, 246, 91, 131)


def table_carree():
    top = Part.makeBox(700, 700, 30, V(1080, -2300, 720))
    top = top.makeFillet(98, [e for e in top.Edges if abs(e.Vertexes[0].Point.z - e.Vertexes[1].Point.z) > 1])
    _add("table", "plateau", top, ("rect", (108, 160, 178, 230)))
    for i, (x, y) in enumerate([(111, 163), (171, 163), (111, 223), (171, 223)]):
        box("table", f"pied_{i + 1}", x, x + 4, y, y + 4, 0, 72, plan=False)


table_carree()


def chaise(name, x0, y0, dossier):
    """Chaise type Cesca dans l'emprise 42 × 42 : luge en tube chromé Ø 2,5, cadres noyer, assise et dossier cannés.
    u = profondeur depuis le dossier, v = largeur ; dossier « ouest » (x0) ou « est » (x0 + 42)."""
    def P(u, v, z):
        x = x0 + u if dossier == "ouest" else x0 + 42 - u
        return V(x * 10, -(y0 + v) * 10, z * 10)

    r = 12.5  # rayon du tube (mm)

    def tube(n, a, b):
        d = b - a
        _add("chrome", f"{name}_{n}", Part.makeCylinder(r, d.Length, a, d), None)

    for side, v in (("g", 2), ("d", 40)):
        pts = [P(3, v, 78.5), P(1, v, 46), P(39, v, 43), P(41, v, 1.3), P(5, v, 1.3)]
        for i in range(len(pts) - 1):
            tube(f"tube_{side}{i}", pts[i], pts[i + 1])
        for i, pt in enumerate(pts):
            _add("chrome", f"{name}_coude_{side}{i}", Part.makeSphere(r, pt), None)
    tube("traverse_sol", P(5, 2, 1.3), P(5, 40, 1.3))
    # assise : cadre noyer 42 × 42 × 3, cannage tendu dedans
    seat_o = solid(*_uv_box(x0, y0, dossier, 0, 42, 0, 42), 44, 47)
    seat_i = solid(*_uv_box(x0, y0, dossier, 5, 37, 5, 37), 43, 48)
    _add("chaise", name + "_cadre_assise", seat_o.cut(seat_i), ("rect", (x0, y0, x0 + 42, y0 + 42)))
    box("cannage", name + "_cannage_assise", *_uv_box(x0, y0, dossier, 5, 37, 5, 37), 45.2, 45.6, plan=False)
    # dossier : cadre 42 × 22, épaisseur 2,5, entre h 58 et 80
    back_o = solid(*_uv_box(x0, y0, dossier, 1.5, 4, 0, 42), 58, 80)
    back_i = solid(*_uv_box(x0, y0, dossier, 1, 4.5, 5, 37), 62, 76)
    _add("chaise", name + "_cadre_dossier", back_o.cut(back_i), None)
    box("cannage", name + "_cannage_dossier", *_uv_box(x0, y0, dossier, 2.6, 2.9, 5, 37), 62, 76, plan=False)


def _uv_box(x0, y0, dossier, u0, u1, v0, v1):
    """Rectangle (u, v) de la chaise → (x0, x1, y0, y1) du plan."""
    if dossier == "ouest":
        return x0 + u0, x0 + u1, y0 + v0, y0 + v1
    return x0 + 42 - u1, x0 + 42 - u0, y0 + v0, y0 + v1


chaise("chaise_1", 76, 174, "ouest")
chaise("chaise_2", 168, 174, "est")

# étagère haute P25 le long du mur sud (h 200)
box("etagere", "haute_sud", 0, 140, 227, 252, 197, 200)

# ------------------------------------------------------------------ cellier
calque("cellier")
for zz in (22, 60, 98, 136, 174, 212):
    box("etagere_blanche", f"cellier_{zz}", 317, 355, 0, 30, zz - 2, zz, plan=zz == 22)
box("etagere_blanche", "cellier_montant", 353, 355, 0, 30, 0, 214, plan=False)
box("electro_blanc", "lave_linge", 374, 434, 40, 100, 0, 85)
box("verre_fume", "hublot_ll", 373.6, 374, 58, 82, 48, 72, plan=False)
cyl("electro_blanc", "ballon", 459, 72, 25, 90, 210)

# ------------------------------------------------------------------ décoration (export séparé)
_deco[0] = True


def sphere(mat, name, cx, cy, cz, r):
    _add(mat, name, Part.makeSphere(r * 10, V(cx * 10, -cy * 10, cz * 10)), None)


def bocal(mat, name, cx, cy, r, z0, h, couvercle="bois_clair"):
    cyl(mat, name, cx, cy, r, z0, z0 + h - 1, plan=False)
    cyl(couvercle, name + "_couvercle", cx, cy, r + 0.2, z0 + h - 1, z0 + h, plan=False)


# étagère basse h 162 : épices ; étagère haute h 200 : enceinte, plante
for i, x in enumerate((13, 21, 29, 37, 45, 67, 75, 83)):
    bocal("verre_ambre", f"epices_{i + 1}", x, 12, 2.8, 162, 10, couvercle="noir")
bocal("verre", "bocal_huile", 92, 14, 3.5, 162, 13, couvercle="noir")
bocal("verre", "bocal_sel", 101, 14, 3.5, 162, 13, couvercle="noir")
box("tissu_noir", "enceinte", 45, 71, 8, 22, 200, 215, plan=False)
cyl("terre_cuite", "pot_plante_haut", 95, 14, 6, 200, 211, plan=False)
sphere("feuillage", "plante_haut", 95, 14, 220, 10)

# plan de travail : planche, pot à ustensiles, casserole sur l'induction, liquide vaisselle
box("bois_clair", "planche", 118, 153, 16, 46, 91, 93, plan=False)
cyl("ceramique", "pot_ustensiles", 22, 16, 6, 91, 107, plan=False)
for i, (dx, dy) in enumerate(((-2, -1), (1.5, 1), (0, 2.5))):
    cyl("bois_clair", f"spatule_{i + 1}", 22 + dx, 16 + dy, 0.8, 100, 128, plan=False)
cyl("inox", "casserole", 63, 19, 9, 91.6, 102, plan=False)
s = Part.makeCylinder(10, 160, V(720, -190, 990), V(1, 0, 0))
_add("noir", "manche_casserole", s, None)
cyl("ceramique_bleue", "liquide_vaisselle", 199, 9, 2.6, 91, 110, plan=False)

# table : sets de table, vase et fleurs, corbeille de fruits
box("lin", "set_1", 112, 140, 178, 212, 75, 75.3, plan=False)
box("lin", "set_2", 146, 174, 178, 212, 75, 75.3, plan=False)
cyl("verre", "vase", 125, 208, 4, 75, 95, plan=False)
for i, (dx, dy, h) in enumerate(((0, 0, 118), (-3, 1.5, 112), (3, -1.5, 114))):
    cyl("tige", f"tige_{i + 1}", 125 + dx, 208 + dy, 0.25, 90, h, plan=False)
    sphere("fleurs", f"fleur_{i + 1}", 125 + dx, 208 + dy, h + 1.5, 2.2)
cyl("ceramique", "coupe_fruits", 145, 190, 9, 75, 80, plan=False)
for i, (dx, dy) in enumerate(((-4, -2), (4, -1), (0, 4))):
    sphere("fruits", f"fruit_{i + 1}", 145 + dx, 190 + dy, 83, 3.8)

# suspension globe au-dessus de la table
cyl("noir", "fil_suspension", 143, 195, 0.4, 187, 250, plan=False)
sphere("globe", "suspension", 143, 195, 176, 12)

# meuble café : deux tasses
cyl("ceramique", "tasse_1", 9, 207, 4, 91, 100, plan=False)
cyl("ceramique", "tasse_2", 20, 207, 4, 91, 100, plan=False)

# étagère haute sud (h 200) : bocaux, boîte, livres
bocal("verre", "bocal_sud_1", 15, 240, 4.5, 200, 15)
bocal("verre", "bocal_sud_2", 26, 240, 4.5, 200, 18)
box("ceramique", "boite_sud", 38, 68, 232, 248, 200, 218, plan=False)
for i, mat in enumerate(("livre_a", "livre_b", "livre_c", "livre_a", "livre_b")):
    box(mat, f"livre_{i + 1}", 90 + 3.2 * i, 93 + 3.2 * i, 232, 248, 200, 222 - (i % 3) * 2, plan=False)

# étagères de la porte d'entrée (h 165 / 182 / 199) et ardoise
for i, x in enumerate((162, 172, 182)):
    bocal("verre_ambre", f"porte_165_{i + 1}", x, 243, 2.5, 165, 9, couvercle="noir")
for i, x in enumerate((190, 200)):
    bocal("verre", f"porte_182_{i + 1}", x, 243, 2.5, 182, 11)
for i, x in enumerate((165, 173, 181, 189)):
    bocal("verre_ambre", f"porte_199_{i + 1}", x, 243, 2.2, 199, 8, couvercle="noir")
box("craie", "ardoise_texte", 162, 196, 245.3, 245.4, 130, 131, plan=False)
box("craie", "ardoise_texte_2", 162, 186, 245.3, 245.4, 122, 123, plan=False)

# cellier : paniers, packs, cartons ; balais, aspirateur, seau ; panier à linge sur le LL
box("panier", "cellier_bas_1", 319, 335, 3, 28, 22, 40, plan=False)
box("panier", "cellier_bas_2", 337, 352, 3, 28, 22, 40, plan=False)
for i, x in enumerate((322, 330, 338, 346)):
    cyl("bouteille", f"eau_{i + 1}", x, 15, 3.8, 60, 90, plan=False)
for i, x in enumerate((323, 333, 343)):
    bocal("verre", f"cellier_bocal_{i + 1}", x, 15, 4.5, 98, 18)
box("carton", "cellier_carton_1", 319, 340, 4, 28, 136, 156, plan=False)
box("carton", "cellier_carton_2", 341, 352, 4, 28, 136, 150, plan=False)
box("ceramique_bleue", "lessive", 320, 338, 6, 26, 174, 200, plan=False)
for k, yy in enumerate((364, 371)):
    cyl("bois_clair", f"balai_{k}", yy, 5, 1.2, 5, 190, plan=False)
cyl("electro_blanc", "aspirateur_manche", 386, 8, 1.6, 4, 115, plan=False)
box("electro_blanc", "aspirateur_corps", 382, 390, 4, 13, 70, 95, plan=False)
box("noir", "aspirateur_brosse", 377, 395, 2, 14, 0, 4, plan=False)
cyl("plastique", "seau", 398, 24, 12, 0, 28, plan=False)
box("panier", "panier_linge", 382, 426, 48, 92, 85, 112, plan=False)

_deco[0] = False

grp = doc.addObject("App::DocumentObjectGroup", "Decoration")
for o in deco:
    grp.addObject(o)

doc.recompute()

# ------------------------------------------------------------------ exports
fc = os.path.join(OUT, "cuisine-a.FCStd")
if os.path.exists(fc):
    os.remove(fc)  # évite les copies de sauvegarde .FCBak
doc.saveAs(fc)

for o in objs + deco:
    o.Shape.tessellate(0.5)
import Import  # noqa: E402
# deux exports : sans décoration (cuisine-a) et avec (cuisine-a-deco)
for suffix, items in (("", objs), ("-deco", objs + deco)):
    Import.export(items, os.path.join(OUT, f"cuisine-a{suffix}.glb"))
    Mesh.export(items, os.path.join(OUT, f"cuisine-a{suffix}.obj"))


def write_dxf(path, items):
    """DXF R12 ASCII minimal : un calque par famille, unités cm, nord en haut."""
    layers = sorted({it[0] for it in items})
    out = ["0", "SECTION", "2", "HEADER", "9", "$INSUNITS", "70", "5", "0", "ENDSEC",
           "0", "SECTION", "2", "TABLES", "0", "TABLE", "2", "LAYER", "70", str(len(layers))]
    for i, ly in enumerate(layers):
        out += ["0", "LAYER", "2", ly.upper(), "70", "0", "62", str(i % 7 + 1), "6", "CONTINUOUS"]
    out += ["0", "ENDTAB", "0", "ENDSEC", "0", "SECTION", "2", "ENTITIES"]
    for ly, kind, d in items:
        if kind == "rect":
            x0, y0, x1, y1 = d
            out += ["0", "POLYLINE", "8", ly.upper(), "66", "1", "70", "1"]
            for x, y in [(x0, y0), (x1, y0), (x1, y1), (x0, y1)]:
                out += ["0", "VERTEX", "8", ly.upper(), "10", f"{x:g}", "20", f"{-y:g}", "30", "0"]
            out += ["0", "SEQEND"]
        else:
            cx, cy, r = d
            out += ["0", "CIRCLE", "8", ly.upper(), "10", f"{cx:g}", "20", f"{-cy:g}", "30", "0", "40", f"{r:g}"]
    out += ["0", "ENDSEC", "0", "EOF"]
    with open(path, "w") as f:
        f.write("\n".join(out) + "\n")


write_dxf(os.path.join(OUT, "cuisine-a.dxf"), plan2d)
print(f"OK : {len(objs)} objets + {len(deco)} de décoration -> {OUT}")
