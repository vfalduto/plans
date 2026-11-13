# Rendu Blender (Cycles) de l'entrée, une variante à la fois, construit directement depuis les données de
# pieces/entree/ (pas de FreeCAD).
#
#   ENTREE_VARIANTE=principale|victor blender -b --python pieces/entree/amenagement/rendu.py -- [échantillons] [caméra ...]
# Lancé par `just entree-rendu` (cache des empreintes : commun/rendu_cache.py) et `just entree-apercu`.
# Caméras : celles de piece.CAMERAS ; la silhouette de chacune vient de HUMAINS (module de la variante), la position
# des silhouettes de POSITIONS_HUMAINS (à défaut, POSITIONS_HUMAINS_DEFAUT ci-dessous).
# Produit <sortie>/entree-<variante>-<caméra>.png et entree-<variante>-<caméra>-masque.png, avec <sortie> = 3d/sortie
# (ENTREE_SORTIE=<dossier> pour un autre, ENTREE_APERCU=1 pour 800 x 600).
#
# Réutilise 3d/rendu.py (matériaux, soleil, ciel, réglages Cycles). Portes fermées ; ce que le modèle ne dessine qu'en
# emprise (angle arrondi à étagères, poignées) est construit ici.

import math
import os
import re
import sys

import bmesh
import bpy
import numpy as np
from mathutils import Vector

RACINE = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
sys.path.insert(0, RACINE)
import importlib  # noqa: E402
import importlib.util  # noqa: E402

_spec = importlib.util.spec_from_file_location("rendu_3d", os.path.join(RACINE, "3d", "rendu.py"))
R = importlib.util.module_from_spec(_spec)
sys.modules["rendu_3d"] = R
_spec.loader.exec_module(R)

# Variante : principale (document.py) ou victor (victor.py)
VARIANTE = os.environ.get("ENTREE_VARIANTE", "principale")
M = importlib.import_module("pieces.entree.amenagement." + {"principale": "document", "victor": "victor"}[VARIANTE])
from pieces.entree import piece  # noqa: E402

PREFIXE = f"entree-{VARIANTE}"
APERCU = os.environ.get("ENTREE_APERCU") == "1"

OUT = os.environ.get("ENTREE_SORTIE", R.OUT)
os.makedirs(OUT, exist_ok=True)
VUES_DEMANDEES = [a for a in R.args if not a.isdigit()]

# Couleur des surfaces India : par défaut « neutre » (gris, recoloré dans la page par le sélecteur Plum Living, avec un
# masque rendu à part : voir galerie() de plan.py) ; ENTREE_INDIA=#RRGGBB fait un rendu Cycles avec la vraie teinte,
# sans masque (pour comparer).
INDIA_MODE = os.environ.get("ENTREE_INDIA", "neutre")
NEUTRE = "#C8C8C8"            # gris des surfaces India dans le rendu neutre
INDIA_MATS = ("s_india", "s_india_l")
INDIA_COULEUR = NEUTRE if INDIA_MODE == "neutre" else INDIA_MODE

# ------------------------------------------------------------------ matériaux
R.ESSENCE = "chene"
R.SUN_ALT, R.SUN_AZ = R.position_soleil(*R.LIEU, 2026, 6, 21, 13, 30, R.UTC_DECALAGE)   # soleil haut : couloir sans fenêtre
R.EXPOSITION = -0.6
CHENE = {"tex": "noyer", "sens": "h", "teinte": R.NOYER["teinte"]}   # remplacé par le chêne (ESSENCE)
R.MATS.update({
    "s_mur":     (M.MUR_COULEUR, 0.9, {"enduit": True}),
    "s_coupe":   ("#D9D4CA", 0.95, {}),                       # tranche des cloisons coupées
    "s_chene":   ("#A8743F", 0.5, CHENE),
    "s_chene_v": ("#A8743F", 0.5, dict(CHENE, sens="v")),
    "s_blanc":   (M.MUR_COULEUR, 0.45, {"laque": True}),      # penderie, couleur des murs
    "s_miroir":  ("#F2F4F5", 0.02, {"metal": True}),
    "s_india":   (INDIA_COULEUR, 0.9, {"enduit": True}),   # India (ou gris neutre recoloré dans la page), entrée
    "s_india_l": (INDIA_COULEUR, 0.45, {"laque": True}),   # porte d'entrée
    "s_tapis":   ("#A88E6A", 0.98, {}),                         # tapis de couloir en jute
})
ROLES = {"mur": "s_mur", "linteau": "s_mur", "porte": "porte_peinte", "tableau": "electro_blanc", "banc": "s_chene",
         "caisson": "s_chene", "plateau": "s_chene", "tall": "s_blanc", "socle": "s_mur", "miroir": "s_miroir",
         "applique": "globe", "patere": "s_chene", "facade": "s_chene_v", "facade_p": "s_blanc",
         "haut": "s_chene", "facade_h": "s_chene_v", "india": "s_india", "india_plafond": "s_india", "india_l": "s_india_l", "interphone": "electro_blanc",
         "tapis": "s_tapis", "sac": "lin",
         "tall_i": "s_india_l", "facade_pi": "s_india_l"}   # penderie en laque India (variante Victor)


def carrelage():
    """Grès cérame M.CARRELAGE : carreaux carrés, nuance par carreau, joints fins, légère brillance."""
    c = M.CARRELAGE
    m = bpy.data.materials.new("s_carrelage")
    m.use_nodes = True
    nt = m.node_tree
    bsdf = nt.nodes["Principled BSDF"]
    tc = nt.nodes.new("ShaderNodeTexCoord")
    br = nt.nodes.new("ShaderNodeTexBrick")
    br.offset, br.squash = 0.0, 1.0
    t = c["taille"] / 100
    br.inputs["Scale"].default_value = 1.0
    br.inputs["Brick Width"].default_value = t
    br.inputs["Row Height"].default_value = t
    br.inputs["Mortar Size"].default_value = c["joint"] / 100
    br.inputs["Mortar Smooth"].default_value = 0.2
    br.inputs["Bias"].default_value = 0.0
    br.inputs["Color1"].default_value = R.hexrgb(c["couleur"])
    br.inputs["Color2"].default_value = R.hexrgb(c["nuance"])
    br.inputs["Mortar"].default_value = R.hexrgb(c["couleur_joint"])
    nt.links.new(tc.outputs["Object"], br.inputs["Vector"])
    n = R.noise(nt, 6.0, tc.outputs["Object"], detail=5.0)
    mix = nt.nodes.new("ShaderNodeMix")
    mix.data_type, mix.blend_type = "RGBA", "MULTIPLY"
    mix.inputs["Factor"].default_value = 0.12
    nt.links.new(br.outputs["Color"], mix.inputs["A"])
    nt.links.new(n.outputs["Color"], mix.inputs["B"])
    nt.links.new(mix.outputs["Result"], bsdf.inputs["Base Color"])
    nt.links.new(R.map_range(nt, br.outputs["Fac"], 0.35, 0.8), bsdf.inputs["Roughness"])
    bump = nt.nodes.new("ShaderNodeBump")
    bump.inputs["Strength"].default_value = 0.15
    bump.invert = True
    nt.links.new(br.outputs["Fac"], bump.inputs["Height"])
    nt.links.new(bump.outputs["Normal"], bsdf.inputs["Normal"])
    return m


_mats = {}


def materiau(key):
    if key not in _mats:
        _mats[key] = carrelage() if key == "s_carrelage" else R.make_material(key)
    return _mats[key]


def habiller(o, key, sens=None):
    o.data.materials.clear()
    o.data.materials.append(materiau(key))
    opt = R.MATS.get(key, (None, None, {}))[2]
    if opt.get("tex"):
        R.make_uvs(o, sens or opt.get("sens", "h"), opt.get("echelle", 1.0))


# ------------------------------------------------------------------ primitives (cm du plan)
def boite(nom, x0, x1, y0, y1, z0, z1, key, chanfrein=True):
    bpy.ops.mesh.primitive_cube_add(size=1)
    o = bpy.context.object
    o.name = nom
    o.location = R.p((x0 + x1) / 2, (y0 + y1) / 2, (z0 + z1) / 2)
    o.scale = (abs(x1 - x0) / 100, abs(y1 - y0) / 100, abs(z1 - z0) / 100)
    bpy.ops.object.transform_apply(scale=True)
    habiller(o, key)
    if chanfrein and min(abs(x1 - x0), abs(y1 - y0), abs(z1 - z0)) > 0.6:
        R.chanfreiner(o)
    return o


def prisme(nom, pts, z0, z1, key, chanfrein=True):
    """Prisme vertical sur un contour du plan (liste de points x, y en cm)."""
    me = bpy.data.meshes.new(nom)
    bm = bmesh.new()
    bas = [bm.verts.new(R.p(x, y, z0)) for x, y in pts]
    face = bm.faces.new(bas)
    bmesh.ops.recalc_face_normals(bm, faces=[face])
    if face.normal.z > 0:
        face.normal_flip()
    ext = bmesh.ops.extrude_face_region(bm, geom=[face])
    haut = [e for e in ext["geom"] if isinstance(e, bmesh.types.BMVert)]
    bmesh.ops.translate(bm, verts=haut, vec=Vector((0, 0, (z1 - z0) / 100)))
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    bm.to_mesh(me)
    bm.free()
    o = bpy.data.objects.new(nom, me)
    bpy.context.scene.collection.objects.link(o)
    bpy.context.view_layer.objects.active = o
    habiller(o, key)
    if chanfrein:
        R.chanfreiner(o)
    return o


def contour_arrondi(x0, x1, y0, y1, r, n=16):
    """Contour vu de dessus, coin nord-ouest en quart de cercle de rayon r (sens des aiguilles du plan)."""
    arc = [(x0 + r - r * math.cos(math.pi / 2 * k / n), y0 + r - r * math.sin(math.pi / 2 * k / n)) for k in range(n + 1)]
    return [(x1, y1), (x0, y1)] + arc + [(x1, y0)]


def rect_arrondi(y0, y1, z0, z1, r, n=8):
    """Contour (y, z) d'un rectangle à coins arrondis de rayon r."""
    pts = []
    for cy, cz, a0 in ((y1 - r, z1 - r, 0), (y0 + r, z1 - r, 90), (y0 + r, z0 + r, 180), (y1 - r, z0 + r, 270)):
        for k in range(n + 1):
            a = math.radians(a0 + 90 * k / n)
            pts.append((cy + r * math.cos(a), cz + r * math.sin(a)))
    return pts


def plaque_x(nom, x0, x1, pts_yz, key):
    """Plaque d'épaisseur x0 → x1 sur un contour dans le plan du mur (y, z)."""
    me = bpy.data.meshes.new(nom)
    bm = bmesh.new()
    face = bm.faces.new([bm.verts.new(R.p(x0, y, z)) for y, z in pts_yz])
    ext = bmesh.ops.extrude_face_region(bm, geom=[face])
    vs = [e for e in ext["geom"] if isinstance(e, bmesh.types.BMVert)]
    bmesh.ops.translate(bm, verts=vs, vec=Vector(((x1 - x0) / 100, 0, 0)))
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    bm.to_mesh(me)
    bm.free()
    o = bpy.data.objects.new(nom, me)
    bpy.context.scene.collection.objects.link(o)
    habiller(o, key)
    return o


IMAGES = ["livre_b", "terre_cuite", "ceramique_bleue", "livre_c", "livre_a", "feuillage"]
MODELES_DECO = {"plante": "potted_plant_04", "bol": "wooden_bowl_01", "vase": "ceramic_vase_04", "livres": "book_encyclopedia_set_01"}


def deco(sc):
    """Variante décorée : modèles Poly Haven dans les emprises de M.DECO ; objets marqués « deco »."""
    avant = set(sc.objects)
    paniers = iter(["wicker_basket_01", "wicker_basket_02"])
    liste = []
    for b in getattr(M, "DECO", []):
        if b.role in ("tapis", "sac"):
            boite(f"deco__{b.nom}", b.x0, b.x1, b.y0, b.y1, b.z0, b.z1, ROLES[b.role], chanfrein=b.role == "sac")
            continue
        modele = next(paniers) if b.role == "panier" else MODELES_DECO[b.role]
        liste.append(dict(cadre=(b.x0, b.x1, b.y0, b.y1, b.z0, b.z1), modele=modele, rot=90 if b.role == "livres" else 0))
    R.remplacer(sc, liste)
    for o in set(sc.objects) - avant:
        o["deco"] = True


# ------------------------------------------------------------------ silhouette de référence (1,75 m)
# Homme de la collection Human Base Meshes de Blender Studio (CC0, maillage de base sans multirésolution),
# exporté dans 3d/modeles/humain/homme.glb ; gris neutre semi-transparent, sans ombre, tourné vers le sud.
HUMAIN_GLB = os.path.join(RACINE, "3d", "modeles", "humain", "homme.glb")
HUMAIN_TAILLE = 175
POSITIONS_HUMAINS_DEFAUT = {"couloir": (150, 100), "entree": (42, 290)}   # milieu du passage de 130 ; branche d'entrée


def humain(cle, x, y):
    mat = bpy.data.materials.new("humain")
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes["Principled BSDF"]
    bsdf.inputs["Base Color"].default_value = (*R.hexrgb("#8E8A84")[:3], 1)
    bsdf.inputs["Roughness"].default_value = 0.6
    bsdf.inputs["Alpha"].default_value = 0.45
    avant = set(bpy.data.objects)
    bpy.ops.import_scene.gltf(filepath=HUMAIN_GLB)
    for o in set(bpy.data.objects) - avant:
        if o.type != "MESH":
            bpy.data.objects.remove(o)
            continue
        h = max(c[2] for c in o.bound_box) - min(c[2] for c in o.bound_box)
        o.name = f"humain_{cle}__corps"
        o.scale = (HUMAIN_TAILLE / 100 / h,) * 3
        o.location = R.p(x, y, 0)
        o.data.materials.clear()
        o.data.materials.append(mat)
        bm = bmesh.new()   # le .glb sépare les sommets aux coutures UV : on les ressoude avant le lissage
        bm.from_mesh(o.data)
        bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=1e-5)
        bm.to_mesh(o.data)
        bm.free()
        o.visible_shadow = False
        o["humain"] = cle
        sub = o.modifiers.new("lisse", "SUBSURF")
        sub.levels = sub.render_levels = 1


# ------------------------------------------------------------------ scène
def nom_de(b):
    return f"{b.role}__{b.nom}__{b.mur or '-'}"


def poignees_v4():
    """Poignées de la V4 : abattants du meuble à chaussures, portes de la penderie, placard du meuble haut."""
    c = M.CHAUSSURES
    for k, (y0, y1) in enumerate(c["modules"]):
        ym = (y0 + y1) / 2
        for z in c["rangs"][1:]:
            boite(f"poignee__abattant_{k}_{z}__-", c["x0"] - 1.2, c["x0"], ym - 6, ym + 6, z - 8, z - 7, "noir")
    pe = M.PENDERIE
    xm = pe["x0"] + pe["portes"][0] if "portes" in pe else (pe["x0"] + pe["x1"]) / 2   # joint des portes
    for dx in (-6, 5):
        boite(f"poignee__penderie_{dx}__-", xm + dx, xm + dx + 1, pe["y0"] - 1.5, pe["y0"], 116, 140, "noir")
    mh = M.MEUBLE_HAUT
    for k in range(2):
        xp = mh["x0"] + (mh["x1"] - mh["x0"]) * (0.5 + (k - 0.5) * 0.12)
        boite(f"poignee__mh_{k}__-", xp - 0.5, xp + 0.5, mh["y1"], mh["y1"] + 1.5, mh["z0"] + 4, mh["z0"] + 14, "noir")


def portes_poignees():
    """Béquilles des portes battantes, des deux côtés."""
    for p in piece.PORTES:
        if p["type"] != "battante":
            continue
        autre = p["a"] + 6 if p["gond"] == "b" else p["b"] - 6
        d = p["face"] + (piece.EP / 2 if p["mur"] in "se" else -piece.EP / 2)
        for s in (-1, 1):
            if p["mur"] in "ns":
                boite(f"poignee__{p['nom']}_{s}__{p['mur']}", autre - 6, autre + 6, d + s * 2, d + s * 3.5, 104, 106, "noir")
            else:
                boite(f"poignee__{p['nom']}_{s}__{p['mur']}", d + s * 2, d + s * 3.5, autre - 6, autre + 6, 104, 106, "noir")


def build_scene():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    sc = bpy.context.scene
    # sol : couloir, seuils des ouvertures, bout du salon vu par le passage
    prisme("sol__couloir", piece.SOL, -2, 0, "s_carrelage", chanfrein=False)
    for b in piece.ENVELOPPE:
        if b.role == "linteau":
            boite(f"sol__seuil_{b.nom}__{b.mur}", b.x0, b.x1, b.y0, b.y1, -2, 0, "s_carrelage", chanfrein=False)
    boite("sol__salon__n", 274, 340, -10, 94, -2, 0, "s_carrelage", chanfrein=False)
    prisme("plafond__couloir__p", piece.SOL, piece.H, piece.H + 2, "plafond", chanfrein=False)   # vue du banc seulement

    for b in piece.ENVELOPPE + M.MEUBLES:
        nom = nom_de(b)
        if b.role == "angle":                      # étagères ouvertes en quart de cercle (le plateau couvre le haut)
            ct = contour_arrondi(b.x0, b.x1, b.y0, b.y1, b.arrondi)
            prisme(nom + "_bas", ct, 0, 3, "s_chene")
            for z in M.ANGLE["etageres"]:
                prisme(f"{nom}_{z}", ct, z - 2, z, "s_chene")
            continue
        if b.arrondi and b.role in ("plateau", "caisson", "socle"):   # volume plein à coin nord-ouest arrondi
            prisme(nom, contour_arrondi(b.x0, b.x1, b.y0, b.y1, b.arrondi), b.z0, b.z1, ROLES[b.role])
            continue
        if b.role == "applique":
            boite(nom + "_platine", 108, 110, b.y0 + 2, b.y1 - 2, b.z0, b.z1, "noir")
            bpy.ops.mesh.primitive_uv_sphere_add(radius=0.055, location=R.p(103, (b.y0 + b.y1) / 2, (b.z0 + b.z1) / 2))
            o = bpy.context.object
            o.name = nom
            bpy.ops.object.shade_smooth()
            habiller(o, "globe")
            continue
        if b.role == "miroir":                     # miroir à coins arrondis, liseré noir fin
            r = M.MIROIR["r"]
            xc = (b.x0, b.x1 - 0.2) if b.mur == "o" else (b.x0 + 0.2, b.x1)   # liseré derrière la glace, côté mur
            plaque_x(nom + "_cadre", *xc, rect_arrondi(b.y0 - 1, b.y1 + 1, b.z0 - 1, b.z1 + 1, r + 1), "noir")
            plaque_x(nom, b.x0, b.x1, rect_arrondi(b.y0, b.y1, b.z0, b.z1, r), "s_miroir")
            continue
        if b.role == "cadre_mur":                  # cadre noir, passe-partout blanc, image
            boite(nom, b.x0, b.x1, b.y0, b.y1, b.z0, b.z1, "noir", chanfrein=False)
            boite(nom + "_pp", b.x1, b.x1 + 0.1, b.y0 + 2, b.y1 - 2, b.z0 + 2, b.z1 - 2, "craie", chanfrein=False)
            boite(nom + "_image", b.x1 + 0.1, b.x1 + 0.2, b.y0 + 6, b.y1 - 6, b.z0 + 7, b.z1 - 7,
                  IMAGES[int(b.nom[-2:]) % len(IMAGES)], chanfrein=False)
            continue
        if b.role == "patere":                     # cheville de chêne, axe horizontal
            bpy.ops.mesh.primitive_cylinder_add(vertices=24, radius=(b.y1 - b.y0) / 200, depth=(b.x1 - b.x0) / 100,
                                                location=R.p((b.x0 + b.x1) / 2, (b.y0 + b.y1) / 2, (b.z0 + b.z1) / 2),
                                                rotation=(0, math.pi / 2, 0))
            o = bpy.context.object
            o.name = nom
            bpy.ops.object.shade_smooth()
            habiller(o, "s_chene")
            continue
        key = "s_india_l" if b.nom == "porte_entree" else ROLES[b.role]
        boite(nom, b.x0, b.x1, b.y0, b.y1, b.z0, b.z1, key,
              chanfrein=b.role not in ("mur", "linteau", "miroir"))

    # poignées : abattants (barre sous le chant haut), portes de la penderie (barres verticales), portes (béquilles)
    if hasattr(M, "POIGNEES"):                 # variante : poignées décrites par le modèle
        for nom, *bb in M.POIGNEES:
            boite(f"poignee__{nom}__-", *bb, "noir")
    else:
        poignees_v4()
    portes_poignees()

    deco(sc)
    positions = getattr(M, "POSITIONS_HUMAINS", POSITIONS_HUMAINS_DEFAUT)   # une variante place ses silhouettes
    for cle in sorted(set(getattr(M, "HUMAINS", {}).values())):
        humain(cle, *positions[cle])
    sc.render.engine = "CYCLES"
    R.reglages_cycles(sc)
    sc.render.resolution_x, sc.render.resolution_y = (800, 600) if APERCU else (1600, 1200)
    sc.view_settings.view_transform = "AgX"
    sc.view_settings.look = "AgX - Base Contrast"
    sc.view_settings.exposure = R.EXPOSITION
    R.monde(sc)
    bpy.ops.object.light_add(type="SUN", location=(0, 0, 5))
    sun = bpy.context.object
    sun.name = "soleil"
    sun.data.energy = R.SOLEIL_FORCE / 20
    sun.data.angle = math.radians(8)
    sun.data.color = (1.0, 0.96, 0.9)
    a, h = math.radians(R.SUN_AZ), math.radians(R.SUN_ALT)
    R.look_at(sun, sun.location - Vector((math.sin(a) * math.cos(h), math.cos(a) * math.cos(h), math.sin(h))))
    # plafonnier du couloir (le plafond est retiré, la lumière reste) et applique allumée
    lt = R.area(R.p(177, 150, piece.H - 1), 2.4, 260, color=(1.0, 0.9, 0.78), shape="RECTANGLE", size_y=2.4)
    R.look_at(lt, R.p(177, 150, 0))
    lt = R.area(R.p(55, 290, piece.H - 1), 0.8, 60, color=(1.0, 0.9, 0.78), shape="DISK")   # plafonnier de l'entrée
    R.look_at(lt, R.p(55, 290, 0))
    bpy.ops.object.light_add(type="POINT", location=R.p(100, M.APPLIQUE["y"], M.APPLIQUE["z"]))
    lt = bpy.context.object
    lt.data.energy, lt.data.shadow_soft_size, lt.data.color = 15, 0.05, (1.0, 0.84, 0.62)
    return sc


# ------------------------------------------------------------------ vues
def vue_de(c, humains):
    """Dictionnaire de vue d'une Camera de la pièce, avec la silhouette que la variante y montre."""
    v = {"murs": "", **c.reglages, "loc": c.loc, "target": c.cible}
    if c.ortho:
        v["ortho"] = c.ortho
    else:
        v["persp"] = c.focale
    if c.id in humains:
        v["humain"] = humains[c.id]
    return v


VIEWS = {c.id: vue_de(c, getattr(M, "HUMAINS", {})) for c in piece.CAMERAS}


def camera(sc, name, v):
    cam_data = bpy.data.cameras.new(name)
    if "persp" in v:
        cam_data.type, cam_data.lens, cam_data.sensor_width = "PERSP", v["persp"], 36
    else:
        cam_data.type = "ORTHO"
        cam_data.ortho_scale = v["ortho"]
    cam = bpy.data.objects.new("cam_" + name, cam_data)
    sc.collection.objects.link(cam)
    cam.location = R.p(*v["loc"])
    R.look_at(cam, R.p(*v["target"]))
    return cam


def rendre(sc, name, v, fichier):
    sc.camera = camera(sc, name, v)
    coupes = re.compile(rf"__[{v['murs']}](_|$|\.)") if v["murs"] else None
    plafond = re.compile(r"__p(_|$|\.)")
    for o in sc.objects:
        if o.type == "MESH":
            # plafond retiré : hors du rendu (il ne fait plus d'ombre) ; murs coupés : invisibles, ils gardent leur ombre
            o.hide_render = bool("p" in v["murs"] and plafond.search(o.name))
            coupe = bool(coupes and coupes.search(o.name))
            o.visible_camera = not coupe
            if not v.get("ombres", True):   # vue serrée : les murs coupés ne font pas d'ombre (dos des meubles éclairés)
                o.hide_render = o.hide_render or coupe
        if o.get("deco") and not v.get("deco"):
            o.hide_render = True
        if o.get("humain") and o["humain"] != v.get("humain"):   # silhouette de 1,75 m : vues iso seulement
            o.hide_render = True
    sc.view_settings.exposure = v.get("expo", R.EXPOSITION)
    sc.render.filepath = os.path.join(OUT, fichier)
    bpy.ops.render.render(write_still=True)
    print("Rendu :", sc.render.filepath)
    if INDIA_MODE == "neutre":
        rendre_masque(sc, fichier.replace(".png", "-masque.png"))


def _mat_masque(nom, blanc=0.0, miroir=False, alpha=1.0):
    """Matériau du rendu de masque : émission blanche (India) ou noire, miroir parfait, ou noir semi-transparent."""
    m = bpy.data.materials.new(nom)
    m.use_nodes = True
    nt = m.node_tree
    nt.nodes.clear()
    out = nt.nodes.new("ShaderNodeOutputMaterial")
    if miroir:
        s = nt.nodes.new("ShaderNodeBsdfPrincipled")
        s.inputs["Base Color"].default_value = (1, 1, 1, 1)
        s.inputs["Metallic"].default_value = 1.0
        s.inputs["Roughness"].default_value = 0.0
    else:
        s = nt.nodes.new("ShaderNodeEmission")
        s.inputs["Color"].default_value = (blanc, blanc, blanc, 1)
        s.inputs["Strength"].default_value = 1.0
        if alpha < 1:
            t = nt.nodes.new("ShaderNodeBsdfTransparent")
            mix = nt.nodes.new("ShaderNodeMixShader")
            mix.inputs["Fac"].default_value = alpha
            nt.links.new(t.outputs[0], mix.inputs[1])
            nt.links.new(s.outputs[0], mix.inputs[2])
            s = mix
    nt.links.new(s.outputs[0], out.inputs["Surface"])
    return m


def rendre_masque(sc, fichier):
    """Masque des surfaces India (blanc = India, noir ailleurs), vu par la même caméra : sert à recolorer le rendu
    neutre dans la page. Émission seule, sans lumière ni ciel ; le miroir reste un miroir (il recolore aussi le reflet
    des murs India) ; la silhouette garde sa transparence."""
    mats = {"blanc": _mat_masque("masque_blanc", 1.0), "noir": _mat_masque("masque_noir"),
            "miroir": _mat_masque("masque_miroir", miroir=True), "humain": _mat_masque("masque_humain", alpha=0.45)}
    gardes, ajouts, lumieres = [], [], []
    for o in sc.objects:
        if o.type == "LIGHT" and not o.hide_render:
            lumieres.append(o)
            o.hide_render = True
        if o.type != "MESH":
            continue
        if not o.material_slots:
            o.data.materials.append(mats["noir"])
            ajouts.append(o)
            continue
        for s in o.material_slots:
            n = s.material.name if s.material else ""
            gardes.append((s, s.material))
            s.material = mats["blanc" if n.split(".")[0] in INDIA_MATS else "miroir" if n.startswith("s_miroir")
                              else "humain" if n.startswith("humain") else "noir"]
    vs, cy, monde = sc.view_settings, sc.cycles, sc.world
    reglages = (vs.view_transform, vs.look, vs.exposure, cy.samples, cy.use_denoising, cy.use_adaptive_sampling)
    noir = bpy.data.worlds.new("masque_monde")
    noir.use_nodes = True
    noir.node_tree.nodes["Background"].inputs["Strength"].default_value = 0.0
    sc.world = noir
    vs.view_transform, vs.look, vs.exposure = "Standard", "None", 0.0
    cy.samples, cy.use_denoising, cy.use_adaptive_sampling = 64, False, False
    chemin = os.path.join(OUT, fichier)
    sc.render.filepath = chemin
    bpy.ops.render.render(write_still=True)
    # PNG blanc dont l'alpha est le masque (mask-image de la page, lu sur l'alpha par tous les navigateurs)
    im = bpy.data.images.load(chemin)
    px = np.empty(len(im.pixels), dtype=np.float32)
    im.pixels.foreach_get(px)
    px = px.reshape(-1, 4)
    px[:, 3] = np.round(np.clip(px[:, 0], 0, 1) * 32) / 32   # 33 niveaux : PNG léger, intégré à la page en base64
    px[:, :3] = 1.0
    im.pixels.foreach_set(px.ravel())
    im.scale(sc.render.resolution_x // 2, sc.render.resolution_y // 2)   # étiré à la taille du rendu dans la page
    sc.render.image_settings.compression = 100
    im.file_format = "PNG"
    im.filepath_raw = chemin
    im.save()
    bpy.data.images.remove(im)
    print("Masque :", chemin)
    vs.view_transform, vs.look, vs.exposure, cy.samples, cy.use_denoising, cy.use_adaptive_sampling = reglages
    sc.world = monde
    for s, m in gardes:
        s.material = m
    for o in ajouts:
        o.data.materials.clear()
    for o in lumieres:
        o.hide_render = False


if __name__ == "__main__":
    inconnues = [n for n in VUES_DEMANDEES if n not in VIEWS]
    if inconnues:
        raise SystemExit(f"caméra inconnue : {', '.join(inconnues)}")
    vues = {n: v for n, v in VIEWS.items() if not VUES_DEMANDEES or n in VUES_DEMANDEES}
    sc = build_scene()
    for name, v in vues.items():
        rendre(sc, name, v, f"{PREFIXE}-{name}.png")
    # un rendu qui n'a pas écrit son fichier fait échouer le lancement (la recette ne note rien)
    attendus = [f"{PREFIXE}-{n}{suffixe}.png" for n in vues
                for suffixe in ("", "-masque") if suffixe == "" or INDIA_MODE == "neutre"]   # sans masque si ENTREE_INDIA
    manquants = [f for f in attendus if not os.path.exists(os.path.join(OUT, f))]
    if manquants:
        raise SystemExit(f"rendus manquants : {', '.join(manquants)}")
