# Rendu Blender (Cycles) de la cuisine V11, à partir de 3d/sortie/cuisine-v11.glb (just v11).
#
#   /Applications/Blender.app/Contents/MacOS/Blender -b --python 3d/v11/rendu.py -- [échantillons] [vue ...]
#   ex. : ... -- 16 iso      (aperçu rapide)
# Vues : iso (isométrique, murs ouest et sud coupés), entree, fenetre, banquette, cellier.
# Produit 3d/sortie/v11-rendu-<vue>.png et cuisine-v11.blend.
#
# Réutilise 3d/rendu.py (matériaux, textures, soleil, réglages Cycles). Les matériaux suivent le rôle des objets
# (« rôle__nom ») et la section Matériaux de modele.py ; ce que le modèle ne dessine pas encore (poignées, crédence,
# plafond, fenêtre, coussins de la banquette) est construit ici depuis ses cotes.

import math
import os
import re
import sys

import bmesh
import bpy
from mathutils import Matrix, Vector

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.dirname(HERE))
import modele as M  # noqa: E402
import rendu as R  # noqa: E402

OUT = R.OUT
VUES_DEMANDEES = [a for a in R.args if not a.isdigit()]

# ------------------------------------------------------------------ matériaux V11 (section Matériaux de modele.py)
MUR = "#EFE9DC"            # blanc légèrement chaud (piste Wimborne White) : murs et plinthes
R.COULEUR_BAS = "#3C524C"  # Canopée Plum Living
R.ESSENCE = "chene"
R.TEINTE_TERRAZZO = (0.0, 0.9, 0.45)
CHENE = {"tex": "noyer", "sens": "v", "teinte": R.NOYER["teinte"]}   # remplacé par le chêne miel (ESSENCE)
R.MATS.update({
    "v11_mur":       (MUR, 0.9, {"enduit": True}),
    "v11_plafond":   ("#F4F1EA", 0.95, {"enduit": True}),
    "v11_plinthe":   (MUR, 0.6, {}),
    "v11_canopee":   ("COULEUR_BAS", 0.45, {"laque": True}),
    "v11_chene":     ("#A8743F", 0.5, CHENE),
    "v11_chene_h":   ("#A8743F", 0.5, dict(CHENE, sens="h")),
    "v11_zellige":   ("#E7E5DF", 0.08, {"zellige": True}),
    "v11_inox":      ("#C9C9C7", 0.45, {"metal": True}),
    "v11_bac":       ("#B9B9B6", 0.5, {"metal": True}),
    "v11_bonde":     ("#8E8E8B", 0.25, {"metal": True}),
    "v11_banquette": (MUR, 0.5, {"laque": True}),
    "v11_soies":     ("#3B3833", 0.95, {}),
    "v11_chene_fume": ("#5A4636", 0.5, {"tex": "noyer", "sens": "v", "teinte": (R.NOYER["teinte"][0] * 0.6, R.NOYER["teinte"][1] * 0.42)}),
    "v11_zellige_blanc_casse": ("#EDE6D8", 0.08, {"zellige": True}),
    "v11_zellige_gris_chaud":  ("#CFC7BA", 0.08, {"zellige": True}),
    "v11_zellige_greige":      ("#B9AE9D", 0.08, {"zellige": True}),
    "v11_pan":       ("#3F5A4E", 0.85, {"enduit": True}),
    "v11_rose":      ("#D9BDBB", 0.35, {}),
    "v11_vitre":     ("#0B0B0C", 0.04, {}),
    "v11_four":      ("#1A1C1E", 0.08, {}),
    "v11_porte":     ("#EEECE6", 0.5, {"laque": True}),
    "v11_led":       ("#FFE2B8", 0.5, {"emission": 6.0}),
    "v11_cuivre":    ("#B87333", 0.3, {"metal": True}),
    "v11_pvc":       ("#9EA3A6", 0.5, {}),
    "v11_aimant":    ("#A9ABAD", 0.4, {"metal": True}),
    "v11_sol_wc":    ("#D8D5CE", 0.5, {}),
})
BETONS = {"v11_plan": ("#D6D4CE", "#BDBBB5", 0.45), "v11_ciment": ("#BDBAB3", "#A9A69F", 0.6)}
VELOURS = {"v11_velours": "#C08A2E"}   # ocre moutarde (V11.49 / V11.50)

ROLES = {
    "mur": "v11_mur", "allege": "v11_mur", "linteau": "v11_mur", "cloison": "v11_mur", "dormant": "v11_mur",
    "dormant_haut": "v11_mur", "tech": "v11_mur", "plafond": "v11_plafond",
    "sol_parquet": "sol_bois", "sol_ciment": "v11_ciment", "sol_wc": "v11_sol_wc",
    "socle": "v11_plinthe", "facade": "v11_canopee", "caisson": "v11_canopee",
    "caisson_haut": "v11_chene", "colonne": "v11_chene", "facade_haut": "v11_chene", "facade_col": "v11_chene",
    "joue": "v11_chene", "fileur": "v11_chene_h", "poignee_bois": "v11_chene",
    "poignee_inox": "v11_inox", "plan": "v11_plan", "credence": "v11_zellige_greige",
    "plaque": "vitro", "aspiration": "noir", "hotte": "v11_inox", "evier": "v11_inox", "egouttoir": "v11_inox", "cuve": "v11_bac", "mitigeur": "v11_inox",
    "four": "v11_four", "micro_onde": "v11_four", "led": "v11_led",
    "banquette": "v11_banquette", "coussin": "v11_velours", "etagere_haute": "v11_chene_h", "chaise": "v11_chene",
    "table": "v11_rose", "chant": "noir", "peinture": "v11_pan", "pied": "epoxy_blanc", "lampe": "globe", "fil": "noir", "enceinte": "tissu_noir",
    "pot": "terre_cuite", "plante": "feuillage",
    "porte": "v11_porte", "paumelle": "v11_inox", "ardoise": "ardoise", "aimant": "v11_aimant",
    "etagere": "bois_clair", "montant": "bois_clair", "ballon": "electro_blanc",
    "balai": "noir", "manche": "bois_clair", "ratelier": "v11_inox",
    "alim": "v11_cuivre", "evac": "v11_pvc", "verre": "verre", "alu": "alu",
    "ext_sol": "sol_ext", "ext_pelouse": "pelouse", "ext_facade": "facade_ext", "ext_alu": "alu", "ext_vitre": "vitre_ext",
}
# exceptions par nom d'objet (même rôle, autre matière)
NOMS = {"fileur_ouest": "v11_canopee", "fileur_c1": "v11_plinthe", "socle_fileur_ouest": "v11_plinthe",
        "bonde": "v11_bonde", "soies": "v11_soies", "monture": "bois_clair"}
NOMS.update({f"tiroir_banquette_{k}": "v11_banquette" for k in (1, 2)})
LISSES = {"lampe", "plante", "pot", "pied", "table", "fil", "mitigeur", "alim", "evac", "ballon", "manche"}
SANS_CHANFREIN = {"plafond", "credence", "verre", "led", "sol_parquet", "sol_ciment", "sol_wc"}


def beton(key, c1, c2, rough):
    """Effet béton : deux gris mêlés par un bruit large, nuances fines, rugosité irrégulière."""
    m = bpy.data.materials.new(key)
    m.use_nodes = True
    nt = m.node_tree
    bsdf = nt.nodes["Principled BSDF"]
    tc = nt.nodes.new("ShaderNodeTexCoord")
    big = R.noise(nt, 2.5, tc.outputs["Object"], detail=6.0)
    fine = R.noise(nt, 40.0, tc.outputs["Object"], detail=8.0)
    mix = nt.nodes.new("ShaderNodeMix")
    mix.data_type = "RGBA"
    mix.inputs["A"].default_value = R.hexrgb(c1)
    mix.inputs["B"].default_value = R.hexrgb(c2)
    nt.links.new(R.map_range(nt, big.outputs["Fac"], -0.4, 1.2), mix.inputs["Factor"])
    nt.links.new(mix.outputs["Result"], bsdf.inputs["Base Color"])
    nt.links.new(R.map_range(nt, fine.outputs["Fac"], rough - 0.1, rough + 0.1), bsdf.inputs["Roughness"])
    bump = nt.nodes.new("ShaderNodeBump")
    bump.inputs["Strength"].default_value = 0.04
    nt.links.new(fine.outputs["Fac"], bump.inputs["Height"])
    nt.links.new(bump.outputs["Normal"], bsdf.inputs["Normal"])
    return m


def papier_peint(key):
    """Papier peint : image du motif (modele.PAPIER_PEINT) plaquée en vraie grandeur, répétée en miroir, papier mat."""
    pp = M.PAPIER_PEINT
    m = bpy.data.materials.new(key)
    m.use_nodes = True
    nt = m.node_tree
    bsdf = nt.nodes["Principled BSDF"]
    bsdf.inputs["Roughness"].default_value = 0.8
    img = nt.nodes.new("ShaderNodeTexImage")
    img.image = bpy.data.images.load(os.path.join(os.path.dirname(os.path.dirname(HERE)), pp["image"]), check_existing=True)
    img.extension = "REPEAT"
    w, h = img.image.size
    tc = nt.nodes.new("ShaderNodeTexCoord")
    mp = nt.nodes.new("ShaderNodeMapping")
    mp.inputs["Scale"].default_value = (1.0, w / h, 1.0)   # UV en motifs (make_uvs, échelle = motif) ; image non carrée
    # centre de fleur (point de tangence, angle bas-droit du motif) en u impair, v pair : placé au centre demandé
    cx, cz = pp.get("centre", (0, 0))
    mp.inputs["Location"].default_value = (1 - cx / pp["motif"], 2 - cz / pp["motif"] * w / h, 0.0)
    nt.links.new(tc.outputs["UV"], mp.inputs["Vector"])
    # miroir dans les deux sens : les quatre motifs autour d'un point de tangence forment une fleur
    sep = nt.nodes.new("ShaderNodeSeparateXYZ")
    nt.links.new(mp.outputs["Vector"], sep.inputs["Vector"])
    pp_ = nt.nodes.new("ShaderNodeMath")
    pp_.operation = "PINGPONG"
    pp_.inputs[1].default_value = 1.0
    nt.links.new(sep.outputs["X"], pp_.inputs[0])
    fr = nt.nodes.new("ShaderNodeMath")
    fr.operation = "PINGPONG"
    fr.inputs[1].default_value = 1.0
    nt.links.new(sep.outputs["Y"], fr.inputs[0])
    comb = nt.nodes.new("ShaderNodeCombineXYZ")
    nt.links.new(pp_.outputs[0], comb.inputs["X"])
    nt.links.new(fr.outputs[0], comb.inputs["Y"])
    nt.links.new(comb.outputs["Vector"], img.inputs["Vector"])
    nt.links.new(img.outputs["Color"], bsdf.inputs["Base Color"])
    return m


def velours(key, col):
    m = bpy.data.materials.new(key)
    m.use_nodes = True
    bsdf = m.node_tree.nodes["Principled BSDF"]
    bsdf.inputs["Base Color"].default_value = R.hexrgb(col)
    bsdf.inputs["Roughness"].default_value = 0.9
    for nom, v in (("Sheen Weight", 0.8), ("Sheen Roughness", 0.4)):
        if nom in bsdf.inputs:
            bsdf.inputs[nom].default_value = v
    return m


def materiau(key):
    if key == "v11_pan" and getattr(M, "PAPIER_PEINT", None):
        return papier_peint(key)
    if key in BETONS:
        return beton(key, *BETONS[key])
    if key in VELOURS:
        return velours(key, VELOURS[key])
    return R.make_material(key)


# ------------------------------------------------------------------ géométrie complémentaire (cotes du modèle)
def boite(sc, nom, x0, x1, y0, y1, z0, z1):
    me = bpy.data.meshes.new(nom)
    bm = bmesh.new()
    bmesh.ops.create_cube(bm, size=1.0)
    bm.to_mesh(me)
    bm.free()
    o = bpy.data.objects.new(nom, me)
    o.scale = ((x1 - x0) / 100, (y1 - y0) / 100, (z1 - z0) / 100)
    o.location = R.p((x0 + x1) / 2, (y0 + y1) / 2, (z0 + z1) / 2)
    sc.collection.objects.link(o)
    bpy.context.view_layer.update()
    o.data.transform(Matrix.Diagonal(tuple(o.scale) + (1,)))
    o.scale = (1, 1, 1)
    return o


def complements(sc):
    # plafond, sol du WC (vu en isométrie)
    boite(sc, "plafond__plafond", -20, 494, -20, 262, M.H, M.H + 10)
    boite(sc, "sol_wc__wc", 392, 484, 110, 252, -2, 0)
    # crédence zellige entre le plan et les hauts, sur toute la rangée
    boite(sc, "credence__credence", 0, M.sur_bas(M.N_BAS)[1], 0, 0.4, M.PT_Z1 + 0.05, M.HAUT_Z0 - 0.05)
    # fenêtre coulissante (2 vantaux) dans la baie du mur ouest, alu, à 10 du nu intérieur
    fe = M.FENETRE
    y0, y1, z0, z1 = fe["y0"], fe["y1"], fe["allege"], fe["linteau"]
    ym = (y0 + y1) / 2
    boite(sc, "verre__fenetre", -11, -10.6, y0 + 4, y1 - 4, z0 + 4, z1 - 4)
    for k, (a, b, c, d) in enumerate([(y0, y1, z0, z0 + 4), (y0, y1, z1 - 4, z1), (y0, y0 + 4, z0, z1),
                                      (y1 - 4, y1, z0, z1), (ym - 2.5, ym + 2.5, z0, z1)]):
        boite(sc, f"alu__fenetre_{k}", -13, -8, a, b, c, d)
    boite(sc, "alu__appui", -13, 1, y0, y1, z0 - 1.5, z0)
    # porte pliante du cellier repliée (montrée quand la porte est ouverte) : deux vantaux côte à côte, côté cuisine
    if M.PLIANTE:
        a = M.PLIANTE
        for k in range(2):
            boite(sc, f"porte__pliante_replie_{k}", a["rail"] - a["l"], a["rail"], a["y0"] + k * (a["ep"] + 0.2),
                  a["y0"] + k * (a["ep"] + 0.2) + a["ep"], 1, a["z1"])
    # extérieur (comme la variante A) : cuisine au 2e étage, rue à -560, immeuble en face à 12 m, mêmes fenêtres
    sol, fx = -560, -1200
    boite(sc, "ext_sol__rue", -2400, -20, -1600, 2000, sol - 2, sol)
    boite(sc, "ext_pelouse__pelouse", -1100, -250, -1600, 2000, sol, sol + 2)
    boite(sc, "ext_facade__facade", fx - 40, fx, -1400, 1800, sol, 1100)
    for etage in range(6):
        z0 = sol + etage * 280 + fe["allege"]
        for k in range(-4, 6):
            a = y0 + k * 330
            boite(sc, f"ext_vitre__{etage}_{k}", fx, fx + 1, a + 5, a + 137, z0 + 5, z0 + 104)
            for n, (b0, b1, c0, c1) in enumerate([(a, a + 142, z0, z0 + 5), (a, a + 142, z0 + 104, z0 + 109),
                                                  (a, a + 5, z0, z0 + 109), (a + 137, a + 142, z0, z0 + 109),
                                                  (a + 68, a + 74, z0, z0 + 109)]):
                boite(sc, f"ext_alu__{etage}_{k}_{n}", fx, fx + 3, b0, b1, c0, c1)
    # banquette : coussins d'assise et de dossier en velours
    bq = M.BANQ
    boite(sc, "coussin__assise", bq["x0"] + 0.5, bq["x1"] - 0.5, bq["y0"] + 0.5, bq["y1"] - 5.5, 45, 50)
    boite(sc, "coussin__dossier", bq["x0"] + 0.5, bq["x1"] - 0.5, bq["y1"] - 11, bq["y1"] - 5.2, 50, 84)
    # poignées : profilé toute longueur en chêne sur les façades bois, barres inox sur les bas Canopée
    for b in M.MEUBLES:
        pg = getattr(b, "poignee", "")
        if not pg or b.role not in ("facade", "facade_haut", "facade_col"):
            continue
        if b.role == "facade":                       # barre inox Ø 1,2 de 20 ; bas : face au sud, banquette : au nord
            xm, zt = (b.x0 + b.x1) / 2, b.z1 - 4
            nord = b.nom.startswith("tiroir_banquette")
            f0, s = (b.y0, -1) if nord else (b.y1, 1)
            ya, yb = sorted((f0 + s * 2.2, f0 + s * 3.4))
            boite(sc, f"poignee_inox__{b.nom}", xm - 10, xm + 10, ya, yb, zt - 0.6, zt + 0.6)
            for xp in (xm - 9, xm + 9):
                ya, yb = sorted((f0, f0 + s * 2.4))
                boite(sc, f"poignee_inox__{b.nom}_pied{xp:.0f}", xp - 0.5, xp + 0.5, ya, yb, zt - 0.5, zt + 0.5)
        elif b.role == "facade_haut":               # hauts, face au sud : profilé vertical côté est
            boite(sc, f"poignee_bois__{b.nom}", b.x1 - 3, b.x1 - 0.8, b.y1, b.y1 + 1.8, b.z0 + 1, b.z1 - 1)
        else:                                        # colonnes, face à l'ouest (x0)
            if pg == "tiroir":
                boite(sc, f"poignee_bois__{b.nom}", b.x0 - 1.8, b.x0, b.y0 + 1, b.y1 - 1, b.z1 - 3, b.z1 - 0.8)
            else:                                    # porte : C2 (frigo) poignée au nord, C1 au sud
                ya, yb = (b.y0 + 0.8, b.y0 + 3) if b.nom.endswith(("_c2", "_c3")) else (b.y1 - 3, b.y1 - 0.8)
                boite(sc, f"poignee_bois__{b.nom}", b.x0 - 1.8, b.x0, ya, yb, b.z0 + 1, b.z1 - 1)


def bonde_et_balais(sc):
    # bonde au fond du bac de l'évier
    c = next(b for b in M.MEUBLES if b.role == "cuve")
    xm, ym = (c.x0 + c.x1) / 2, (c.y0 + c.y1) / 2
    bpy.ops.mesh.primitive_cylinder_add(radius=0.045, depth=0.006, location=R.p(xm, ym, c.z0 + 0.8))
    bpy.context.object.name = "cuve__bonde"
    # balais : tête = monture bois + soies ; tête en bas (soies vers le sol) ou en haut (soies vers le haut)
    for k, (xc, tete) in enumerate(M.BALAIS):
        b = next(o for o in M.MEUBLES if o.nom == f"tete_balai_{k + 1}")
        if tete == "bas":
            boite(sc, f"balai__monture_{k}", b.x0, b.x1, b.y0 + 1, b.y1 - 1, b.z1 - 4, b.z1)
            boite(sc, f"balai__soies_{k}", b.x0 + 0.5, b.x1 - 0.5, b.y0 + 0.5, b.y1 - 0.5, b.z0, b.z1 - 4)
        else:
            boite(sc, f"balai__monture_{k}", b.x0, b.x1, b.y0 + 1, b.y1 - 1, b.z0, b.z0 + 4)
            boite(sc, f"balai__soies_{k}", b.x0 + 0.5, b.x1 - 0.5, b.y0 + 0.5, b.y1 - 0.5, b.z0 + 4, b.z1)


def tube(sc, nom, pts, r, mat):
    cu = bpy.data.curves.new(nom, "CURVE")
    cu.dimensions = "3D"
    cu.bevel_depth = r / 100
    cu.bevel_resolution = 4
    sp = cu.splines.new("POLY")
    sp.points.add(len(pts) - 1)
    for pt, (x, y, z) in zip(sp.points, pts):
        pt.co = tuple(R.p(x, y, z)) + (1,)
    o = bpy.data.objects.new(nom, cu)
    sc.collection.objects.link(o)
    o.data.materials.append(mat)
    return o


def chaises(sc, mats):
    """Chaise type Cesca (Breuer) à la place des volumes du modèle : piètement luge en tube chromé Ø 2,5,
    assise et dossier en cadre chêne et cannage. Dossier du côté indiqué par le modèle (ici à l'est)."""
    for o in list(sc.objects):
        if o.name.startswith("chaise__"):
            o.hide_render = True
    a = next((b for b in M.MEUBLES if b.nom == "assise_chaise_1"), None)
    if a is None:          # plus de chaise dans le modèle
        return
    x0, x1, y0, y1 = a.x0, a.x1, a.y0, a.y1          # dossier à l'est (x1)
    for c in ("chrome", "cannage", "v11_chene"):
        mats.setdefault(c, materiau(c))
    for y in (y0 + 2, y1 - 2):
        tube(sc, f"cesca_cote_{y:.0f}", [(x1 - 4, y, 1.3), (x0 + 6, y, 1.3), (x0 + 2, y, 5), (x0 + 2, y, 38),
                                         (x0 + 5, y, 42), (x1 - 5, y, 42), (x1 - 2.5, y, 47), (x1 - 1.5, y, 84)],
             1.25, mats["chrome"])
    tube(sc, "cesca_traverse", [(x1 - 4, y0 + 2, 1.3), (x1 - 4, y1 - 2, 1.3)], 1.25, mats["chrome"])
    pieces = [("v11_chene", x0 + 1, x1 - 3, y0, y0 + 3, 42.5, 45.5), ("v11_chene", x0 + 1, x1 - 3, y1 - 3, y1, 42.5, 45.5),
              ("v11_chene", x0 + 1, x0 + 4, y0, y1, 42.5, 45.5), ("v11_chene", x1 - 6, x1 - 3, y0, y1, 42.5, 45.5),
              ("cannage", x0 + 4, x1 - 6, y0 + 3, y1 - 3, 44, 44.6),
              ("v11_chene", x1 - 3, x1 - 0.5, y0 + 1, y1 - 1, 80, 84), ("v11_chene", x1 - 3, x1 - 0.5, y0 + 1, y1 - 1, 58, 61),
              ("v11_chene", x1 - 3, x1 - 0.5, y0 + 1, y0 + 4, 58, 84), ("v11_chene", x1 - 3, x1 - 0.5, y1 - 4, y1 - 1, 58, 84),
              ("cannage", x1 - 2, x1 - 1.4, y0 + 4, y1 - 4, 61, 80)]
    for k, (m, *bx) in enumerate(pieces):
        o = boite(sc, f"cesca_{k}", *bx)
        o.data.materials.append(mats[m])
        if m == "v11_chene":
            R.make_uvs(o, "h", 1.0)
            R.chanfreiner(o)


def pieds_vera(sc, mats):
    """Pieds de la table Véra : tube Ø 3 laqué blanc, vertical sous le plateau puis incliné vers l'extérieur."""
    pieds = [b for b in M.MEUBLES if b.nom.startswith("pied_vera_")]
    if not pieds:
        return
    for o in list(sc.objects):
        if o.name.startswith("pied__pied_vera_"):
            o.hide_render = True
    mats.setdefault("epoxy_blanc", materiau("epoxy_blanc"))
    cx, cy = M.TABLE["cx"], M.TABLE["cy"]
    for k, b in enumerate(pieds):
        px, py = (b.x0 + b.x1) / 2, (b.y0 + b.y1) / 2
        dx, dy = (1 if px > cx else -1), (1 if py > cy else -1)
        tube(sc, f"vera_pied_{k}", [(px, py, 73), (px, py, 55), (px + 4 * dx, py + 4 * dy, 0.5)], 1.5, mats["epoxy_blanc"])


def porte_cellier(sc, ouverte):
    """Porte du cellier ouverte à son angle (charnière, sens et angle donnés par le modèle), ou fermée.
    Porte pliante : vantaux dans la baie (fermée) ou repliés côté cuisine (ouverte)."""
    if M.PLIANTE:
        for o in sc.objects:
            if o.name.startswith("porte__cellier_pliante"):
                o.hide_render = ouverte
            if o.name.startswith("porte__pliante_replie"):
                o.hide_render = not ouverte
        return
    v = M.CELLIER_VANTAUX[0]
    (hx, hy), (fx, fy), (ox, oy) = v["h"], v["ferme"], v["ouvert"]
    a0 = math.atan2(-(fy - hy), fx - hx)            # repère Blender : Y = -y
    a1 = math.atan2(-(oy - hy), ox - hx)
    pivot = R.p(hx, hy, 0)
    rot = Matrix.Translation(pivot) @ Matrix.Rotation(a1 - a0 if ouverte else 0, 4, "Z") @ Matrix.Translation(-pivot)
    for o in sc.objects:
        if re.match(r"(porte__cellier_vantail|paumelle__)", o.name):
            if "ferme" not in o:
                o["ferme"] = [list(r) for r in o.matrix_world]
            o.matrix_world = rot @ Matrix(o["ferme"])


# ------------------------------------------------------------------ scène
def build_scene():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.ops.import_scene.gltf(filepath=os.path.join(OUT, "cuisine-v11.glb"), import_shading="FLAT")
    sc = bpy.context.scene
    complements(sc)
    bonde_et_balais(sc)
    mats, inconnus = {}, set()
    for o in list(sc.objects):
        if o.type != "MESH":
            continue
        role, _, nom = o.name.partition("__")
        nom = re.sub(r"\.\d+$", "", nom)
        key = NOMS.get(nom) or NOMS.get(nom.split("_")[0]) or ROLES.get(role)
        if key is None:
            inconnus.add(role)
            key = role
        if key not in mats:
            mats[key] = materiau(key)
        o.data.materials.clear()
        o.data.materials.append(mats[key])
        opt = R.MATS.get(key, (None, None, {}))[2]
        if key == "v11_pan" and getattr(M, "PAPIER_PEINT", None):
            R.make_uvs(o, "h", M.PAPIER_PEINT["motif"] / 100)   # 1 unité UV = 1 motif
        if opt.get("tex"):
            sens = opt.get("sens", "bloc")
            if opt["tex"] == "noyer" and R.BOIS[R.ESSENCE][3] == "v" and sens in ("v", "h"):
                sens = "h" if sens == "v" else "v"
            R.make_uvs(o, sens, opt.get("echelle", 1.0))
        lisse = role in LISSES
        for poly in o.data.polygons:
            poly.use_smooth = lisse
        if not lisse and role not in SANS_CHANFREIN:
            R.chanfreiner(o)
        if role == "verre":
            o.visible_shadow = False
    if inconnus:
        print("Rôles sans matériau V11 :", sorted(inconnus))
    for o in list(sc.objects):     # têtes de balais du modèle remplacées par monture + soies
        if re.match(r"balai__tete_balai_", o.name):
            o.hide_render = True
    chaises(sc, mats)
    pieds_vera(sc, mats)
    R.remplacer(sc, R.ARBRES)
    R.remplacer(sc, [dict(cacher=r"^(pot__pot_plante|plante__plante)", cadre=r"^(pot__pot_plante|plante__plante)",
                          modele="potted_plant_04")])

    sc.render.engine = "CYCLES"
    R.reglages_cycles(sc)
    sc.render.resolution_x, sc.render.resolution_y = 1600, 1200
    sc.view_settings.view_transform = "AgX"
    sc.view_settings.look = "AgX - Base Contrast"
    sc.view_settings.exposure = R.EXPOSITION
    R.monde(sc)
    bpy.ops.object.light_add(type="SUN", location=(0, 0, 5))
    sun = bpy.context.object
    sun.name = "soleil"
    sun.data.energy = R.SOLEIL_FORCE
    sun.data.angle = math.radians(0.53)
    sun.data.color = (1.0, 0.95, 0.88)
    a, h = math.radians(R.SUN_AZ), math.radians(R.SUN_ALT)
    R.look_at(sun, sun.location - Vector((math.sin(a) * math.cos(h), math.cos(a) * math.cos(h), math.sin(h))))
    fe = M.FENETRE
    yc, zc = (fe["y0"] + fe["y1"]) / 2, (fe["allege"] + fe["linteau"]) / 2
    portal = R.area(R.p(-21, yc, zc), (fe["y1"] - fe["y0"]) / 100, 0, shape="RECTANGLE",
                    size_y=(fe["linteau"] - fe["allege"]) / 100)
    portal.data.cycles.is_portal = True
    R.look_at(portal, R.p(100, yc, zc))
    # cellier (sans fenêtre) ; LED sous les hauts ; suspension au-dessus de la table
    R.area(R.p(400, 40, 247), 0.4, 45)
    for b in M.MEUBLES:
        if b.role == "led":
            lt = R.area(R.p((b.x0 + b.x1) / 2, (b.y0 + b.y1) / 2, b.z0 - 0.2), (b.x1 - b.x0) / 100, 6,
                        color=(1.0, 0.86, 0.68), shape="RECTANGLE", size_y=0.02)
            R.look_at(lt, R.p((b.x0 + b.x1) / 2, (b.y0 + b.y1) / 2, 0))
    lampe = next(b for b in M.MEUBLES if b.role == "lampe")
    bpy.ops.object.light_add(type="POINT", location=R.p(lampe.cx, lampe.cy, (lampe.z0 + lampe.z1) / 2))
    lt = bpy.context.object
    lt.data.energy, lt.data.shadow_soft_size, lt.data.color = 40, 0.14, (1.0, 0.85, 0.65)
    return sc


def nuit(sc, oui):
    """Nuit : ni soleil ni ciel, fond sombre ; seules les lampes du modèle éclairent (suspension, LED, cellier)."""
    sc.objects["soleil"].hide_render = oui
    nt = sc.world.node_tree
    bgs = [n for n in nt.nodes if n.type == "BACKGROUND"]
    bgs[0].inputs["Strength"].default_value = 0.0 if oui else R.CIEL_FORCE
    bgs[1].inputs["Color"].default_value = R.hexrgb("#1D2126" if oui else "#E4E9EC")
    sc.view_settings.exposure = 1.0 if oui else R.EXPOSITION


# Vues : yeux à 163 debout, 120 assis ; visée horizontale et décentrement vertical (verticales droites).
DEBOUT, ASSIS = R.DEBOUT, R.ASSIS
COUPES_ISO = (r"^(mur__(ouest_nord|ouest_sud|sud_ouest|sud_est)|allege__|linteau__(linteau_fenetre|linteau_entree|"
              r"linteau_galandage)|cloison__galandage|porte__entree|ardoise__|aimant__|peinture__|plafond__|verre__|alu__|ext_)")
# isométrique depuis le nord-ouest : murs nord et ouest, plafond ET rangée nord coupés (vue de dos, elle masquait la
# pièce ; elle se voit dans la vue A)
COUPES_ISO_NO = (r"^(mur__(nord|nord_alcove|ouest_nord|ouest_sud)|allege__|linteau__linteau_fenetre|cloison__cloison_cellier|"
                 r"linteau__linteau_cellier|plafond__|verre__|alu__|ext_|caisson__|caisson_haut__|plan__|plaque__|evier__|"
                 r"cuve__|mitigeur__|egouttoir__|hotte__|led__|credence__|four__facade_b|facade__facade_b|facade_haut__|"
                 r"socle__socle_(b|fileur)|joue__(joue_h|fileur_ouest)|fileur__fileur_hauts|etagere_haute__etagere_mur|"
                 r"tech__coffre_reseaux|poignee_(inox|bois)__facade_(b|h)|aspiration__)")
ISO = dict(ortho=6.0, loc=(-380, 700, 640), target=(250, 120, 60), coupes=COUPES_ISO)
VIEWS = {
    # A — isométrique depuis le sud-ouest, murs ouest et sud et plafond coupés (ils portent toujours ombres et lumière)
    "iso":         ISO,
    # B — depuis la baie d'entrée, vers la rangée nord et la fenêtre
    "entree":      dict(loc=(268, 236, DEBOUT), target=(105, 40, DEBOUT), lens=18, shift=-0.12),
    # C — depuis la fenêtre, vers les colonnes et le cellier
    "fenetre":     dict(loc=(12, 105, DEBOUT), target=(330, 140, DEBOUT), lens=18, shift=-0.12),
    # D — assis sur la banquette, place est, vers la rangée nord et les colonnes
    "banquette":   dict(loc=(78, 226, ASSIS), target=(300, 70, ASSIS), lens=20, shift=0.02),
    # E — entré dans le cellier, porte refermée derrière soi : rayonnage du mur nord, ballon, zone technique
    "cellier":     dict(loc=(334, 76, DEBOUT), target=(440, 25, DEBOUT), lens=14, shift=-0.15, porte_fermee=True),
    # F — dos à la porte du cellier (fermée), vers la table et la banquette
    "dos_cellier": dict(loc=(312, 44, DEBOUT), target=(40, 215, DEBOUT), lens=18, shift=-0.15, porte_fermee=True),
    # G — isométrique de nuit, tous les éclairages allumés
    "iso_nuit":    dict(ISO, nuit=True),
    # A' — isométrique depuis le nord-ouest
    "iso_no":      dict(ortho=6.0, loc=(-400, -470, 700), target=(220, 140, 60), coupes=COUPES_ISO_NO),
}
# Rendus temporaires (hors page) : crédence zellige chaud (3 teintes empilées), hauts en chêne fumé
CREDENCE = dict(loc=(152, 235, 135), target=(152, 0, 135), lens=22, shift=0.0)
COUSSINS = [("ocre-moutarde", "#C08A2E"), ("vieux-rose", "#C49690")]
ZELLIGES = ["v11_zellige_blanc_casse", "v11_zellige_gris_chaud", "v11_zellige_greige"]


def exterieur(o):
    while o.parent is not None:
        o = o.parent
    return bool(o.get("exterieur"))


def camera(sc, name, v):
    cam_data = bpy.data.cameras.new(name)
    if "ortho" in v:
        cam_data.type = "ORTHO"
        cam_data.ortho_scale = v["ortho"]
    else:
        cam_data.lens = v["lens"]
        cam_data.sensor_width = 36
        cam_data.shift_y = v.get("shift", 0.0)
    cam = bpy.data.objects.new("cam_" + name, cam_data)
    sc.collection.objects.link(cam)
    cam.location = R.p(*v["loc"])
    R.look_at(cam, R.p(*v["target"]))
    return cam


def rendre(sc, name, v, fichier):
    sc.camera = camera(sc, name, v)
    porte_cellier(sc, ouverte=not v.get("porte_fermee"))
    nuit(sc, bool(v.get("nuit")))
    coupes = v.get("coupes")
    for o in sc.objects:
        if o.type in ("MESH", "CURVE"):
            o.visible_camera = not (coupes and (re.match(coupes, o.name) or exterieur(o)))
    sc.render.filepath = os.path.join(OUT, fichier)
    bpy.ops.render.render(write_still=True)
    print("Rendu :", sc.render.filepath)


def empiler(fichiers, sortie):
    """Empile verticalement des PNG de même largeur (le premier en haut)."""
    import numpy as np
    ims = [bpy.data.images.load(os.path.join(OUT, f)) for f in fichiers]
    w = ims[0].size[0]
    arrs = [np.array(im.pixels[:], dtype=np.float32).reshape(im.size[1], w, 4) for im in ims]
    tout = np.vstack(arrs[::-1])          # origine en bas à gauche
    out = bpy.data.images.new("pile", w, tout.shape[0], alpha=True)
    out.pixels.foreach_set(tout.ravel())
    out.filepath_raw = os.path.join(OUT, sortie)
    out.file_format = "PNG"
    out.save()
    print("Rendu :", out.filepath_raw)


def materiau_de(sc, motif, mat):
    for o in sc.objects:
        if o.type == "MESH" and re.match(motif, o.name):
            o.data.materials.clear()
            o.data.materials.append(mat)


if __name__ == "__main__":
    sc = build_scene()
    temporaires = [a for a in VUES_DEMANDEES if a in ("zellige", "fume", "coussins")]
    vues = [a for a in VUES_DEMANDEES if a not in temporaires]
    if not temporaires or vues:
        for name, v in VIEWS.items():
            if not vues or name in vues:
                rendre(sc, name, v, f"v11-rendu-{name}.png")
    if "zellige" in temporaires:
        sc.render.resolution_y = 800
        for k, z in enumerate(ZELLIGES):
            materiau_de(sc, r"^credence__", materiau(z))
            rendre(sc, "credence", CREDENCE, f"v11-tmp-zellige-{k + 1}.png")
        empiler([f"v11-tmp-zellige-{k + 1}.png" for k in range(3)], "v11-tmp-zellige.png")
        sc.render.resolution_y = 1200
        materiau_de(sc, r"^credence__", materiau("v11_zellige"))
    if "fume" in temporaires:
        fume = materiau("v11_chene_fume")
        motif = r"^(caisson_haut__|facade_haut__|poignee_bois__facade_h|joue__joue_h_|fileur__fileur_hauts)"
        for o in sc.objects:
            if o.type == "MESH" and re.match(motif, o.name):
                o.data.materials.clear()
                o.data.materials.append(fume)
        rendre(sc, "banquette", VIEWS["banquette"], "v11-tmp-hauts-fume.png")
    if "coussins" in temporaires:   # coussins de la banquette : autres teintes de velours, vue dos au cellier
        for nom, col in COUSSINS:
            materiau_de(sc, r"^coussin__", velours(f"v11_velours_{nom}", col))
            rendre(sc, "dos_cellier", VIEWS["dos_cellier"], f"v11-tmp-coussins-{nom}.png")
    for o in sc.objects:
        if o.type in ("MESH", "CURVE"):
            o.visible_camera = True
    if not temporaires:
        bpy.ops.wm.save_as_mainfile(filepath=os.path.join(OUT, "cuisine-v11.blend"), compress=True)
