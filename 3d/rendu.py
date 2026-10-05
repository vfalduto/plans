# Rendu Blender (Cycles) de la cuisine, variante A, à partir de 3d/sortie/cuisine-a[-deco].glb.
#
# Prérequis : python3 3d/textures.py (textures CC0 dans 3d/textures/).
# Lancement (sans interface) :
#   /Applications/Blender.app/Contents/MacOS/Blender -b --python 3d/rendu.py -- [échantillons] [sans|deco] [vue ...]
#   ex. : ... -- 32 deco cellier   (aperçu rapide d'une vue, avec décoration)
# Sans précision : 128 échantillons, les deux versions, toutes les vues.
#
# Produit dans 3d/sortie/ : rendu-<vue>.png (sans déco), rendu-<vue>-deco.png (avec),
# cuisine-a.blend et cuisine-a-deco.blend (à ouvrir pour changer de point de vue).
# Matériaux : d'après le préfixe du nom de l'objet (« facade_bleu__… » → MATS["facade_bleu"]).

import math
import os
import sys

import bpy
from mathutils import Vector

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "sortie")
TEX = os.path.join(HERE, "textures")
args = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
SAMPLES = next((int(a) for a in args if a.isdigit()), 128)
VERSIONS = [a for a in args if a in ("sans", "deco")] or ["sans", "deco"]
VUES = [a for a in args if not a.isdigit() and a not in ("sans", "deco")] or ["entree", "fenetre", "cellier", "plongee"]

BLEU = "#2F5557"   # pétrole fumé du nuancier, en attendant la référence exacte du « bleu canopé »


def hexrgb(h):
    h = h.lstrip("#")
    c = [int(h[i:i + 2], 16) / 255 for i in (0, 2, 4)]
    return tuple(((v + 0.055) / 1.055) ** 2.4 if v > 0.04045 else v / 12.92 for v in c) + (1,)


# couleur, rugosité, options :
#   tex     : texture de 3d/textures (noyer, parquet, terrazzo) ; sens : "v" fil vertical, "h" fil selon x, "sol", "bloc"
#   teinte  : (saturation, valeur) appliquées à la texture (noyer huilé = plus sombre, plus saturé)
#   metal, verre (transmission), emission, zellige
NOYER = {"tex": "noyer", "sens": "v", "teinte": (1.25, 0.36)}
MATS = {
    "mur":              ("#F3EEE4", 0.9, {}),
    "plafond":          ("#F5F2EC", 0.95, {}),
    "sol_bois":         ("#B98A55", 0.5, {"tex": "parquet", "sens": "sol", "echelle": 3.4}),
    "sol_carrelage":    ("#D8D5CE", 0.5, {}),
    "facade_bleu":      (BLEU, 0.45, {}),                                      # laque mate
    "facade_noyer":     ("#45291A", 0.5, NOYER),
    "etagere":          ("#45291A", 0.5, dict(NOYER, sens="h")),
    "chaise":           ("#45291A", 0.5, NOYER),
    "porte_bois":       ("#45291A", 0.5, NOYER),
    "table":            ("#A87A4C", 0.45, dict(NOYER, sens="h", teinte=(1.2, 0.85))),
    "caisson":          ("#E9E5DC", 0.6, {}),
    "socle":            ("#2B3436", 0.6, {}),
    "plan":             ("#CFCDC7", 0.3, {"tex": "terrazzo", "sens": "bloc", "echelle": 0.6}),
    "credence":         ("#EFE7D6", 0.08, {"zellige": True}),                 # zellige ivoire
    "inox":             ("#C9C9C7", 0.3, {"metal": True}),
    "vitro":            ("#0B0B0C", 0.04, {}),
    "noir":             ("#18181A", 0.35, {}),
    "verre":            ("#FFFFFF", 0.0, {"verre": True}),
    "verre_ambre":      ("#B5651D", 0.05, {"verre": True}),
    "verre_fume":       ("#1A1C1E", 0.05, {}),
    "menuiserie":       ("#F1F1EF", 0.4, {}),
    "porte_peinte":     ("#EEECE6", 0.5, {}),
    "ardoise":          ("#2F3A33", 0.9, {}),
    "electro_blanc":    ("#F2F2F0", 0.3, {}),
    "etagere_blanche":  ("#F0EEE9", 0.6, {}),
    "bois_clair":       ("#C9A57A", 0.6, {}),
    # décoration
    "tissu_noir":       ("#26272A", 0.95, {}),
    "terre_cuite":      ("#B5653E", 0.8, {}),
    "feuillage":        ("#3E6B35", 0.6, {}),
    "ceramique":        ("#F1EDE4", 0.15, {}),
    "ceramique_bleue":  ("#4F7FA0", 0.2, {}),
    "lin":              ("#D8CCB6", 0.95, {}),
    "fleurs":           ("#E8B04A", 0.7, {}),
    "tige":             ("#4C6B3A", 0.6, {}),
    "fruits":           ("#D9862E", 0.35, {}),
    "globe":            ("#FFF4E0", 0.2, {"emission": 4.0}),
    "craie":            ("#F4F4F0", 0.9, {}),
    "panier":           ("#B48A55", 0.85, {}),
    "bouteille":        ("#DDEBF2", 0.02, {"verre": True}),
    "carton":           ("#B9956A", 0.9, {}),
    "plastique":        ("#6A8FA8", 0.4, {}),
    "livre_a":          ("#8C3B2E", 0.8, {}),
    "livre_b":          ("#2F4F5A", 0.8, {}),
    "livre_c":          ("#C9B27C", 0.8, {}),
}


def tex_vector(nt, sens, echelle):
    """Coordonnées de texture sans UV : projection calculée depuis les coordonnées objet (m)."""
    tc = nt.nodes.new("ShaderNodeTexCoord")
    sep = nt.nodes.new("ShaderNodeSeparateXYZ")
    nt.links.new(tc.outputs["Object"], sep.inputs["Vector"])
    comb = nt.nodes.new("ShaderNodeCombineXYZ")

    def add(a, b):
        m = nt.nodes.new("ShaderNodeMath")
        m.operation = "ADD"
        nt.links.new(a, m.inputs[0])
        nt.links.new(b, m.inputs[1])
        return m.outputs[0]

    X, Y, Z = sep.outputs["X"], sep.outputs["Y"], sep.outputs["Z"]
    if sens == "v":        # fil (u de l'image) vertical, sur les faces nord-sud comme est-ouest
        nt.links.new(Z, comb.inputs["X"])
        nt.links.new(add(X, Y), comb.inputs["Y"])
    elif sens == "sol":
        nt.links.new(X, comb.inputs["X"])
        nt.links.new(Y, comb.inputs["Y"])
    else:                  # "h" (fil selon x) et "bloc" : dessus et chants sans étirement
        nt.links.new(add(X, Z), comb.inputs["X"])
        nt.links.new(add(Y, Z), comb.inputs["Y"])
    scale = nt.nodes.new("ShaderNodeVectorMath")
    scale.operation = "SCALE"
    scale.inputs["Scale"].default_value = 1.0 / echelle
    nt.links.new(comb.outputs["Vector"], scale.inputs[0])
    return scale.outputs["Vector"]


def image(nt, name, short, vec, data=False):
    node = nt.nodes.new("ShaderNodeTexImage")
    node.image = bpy.data.images.load(os.path.join(TEX, f"{name}_{short}.jpg"), check_existing=True)
    if data:
        node.image.colorspace_settings.name = "Non-Color"
    nt.links.new(vec, node.inputs["Vector"])
    return node


def make_material(key):
    col, rough, opt = MATS.get(key, ("#FF00FF", 0.5, {}))
    m = bpy.data.materials.new(key)
    m.use_nodes = True
    nt = m.node_tree
    bsdf = nt.nodes["Principled BSDF"]
    bsdf.inputs["Base Color"].default_value = hexrgb(col)
    bsdf.inputs["Roughness"].default_value = rough
    if opt.get("metal"):
        bsdf.inputs["Metallic"].default_value = 1.0
    if opt.get("verre"):
        bsdf.inputs["Transmission Weight"].default_value = 1.0
        bsdf.inputs["IOR"].default_value = 1.45
    if opt.get("emission"):
        bsdf.inputs["Emission Color"].default_value = hexrgb(col)
        bsdf.inputs["Emission Strength"].default_value = opt["emission"]
    name = opt.get("tex")
    if name:
        vec = tex_vector(nt, opt.get("sens", "bloc"), opt.get("echelle", 1.0))
        diff = image(nt, name, "diff", vec)
        out = diff.outputs["Color"]
        if "teinte" in opt:
            hsv = nt.nodes.new("ShaderNodeHueSaturation")
            hsv.inputs["Saturation"].default_value, hsv.inputs["Value"].default_value = opt["teinte"]
            nt.links.new(out, hsv.inputs["Color"])
            out = hsv.outputs["Color"]
        nt.links.new(out, bsdf.inputs["Base Color"])
        rgh = image(nt, name, "rough", vec, data=True)
        mul = nt.nodes.new("ShaderNodeMath")
        mul.operation = "MULTIPLY"
        mul.inputs[1].default_value = rough / 0.6
        nt.links.new(rgh.outputs["Color"], mul.inputs[0])
        nt.links.new(mul.outputs[0], bsdf.inputs["Roughness"])
        bump = nt.nodes.new("ShaderNodeBump")
        bump.inputs["Strength"].default_value = 0.15
        bump.inputs["Distance"].default_value = 0.001
        nt.links.new(diff.outputs["Color"], bump.inputs["Height"])
        nt.links.new(bump.outputs["Normal"], bsdf.inputs["Normal"])
    if opt.get("zellige"):
        # carreaux 10 × 10 émaillés : teinte variable par carreau, surface ondulée
        vec = tex_vector(nt, "v", 1.0)
        brick = nt.nodes.new("ShaderNodeTexBrick")
        brick.offset = 0.0
        brick.inputs["Scale"].default_value = 10.0
        brick.inputs["Brick Width"].default_value = 1.0
        brick.inputs["Row Height"].default_value = 1.0
        brick.inputs["Mortar Size"].default_value = 0.012
        brick.inputs["Bias"].default_value = 0.0
        base = hexrgb(col)
        brick.inputs["Color1"].default_value = base
        brick.inputs["Color2"].default_value = tuple(c * 0.86 for c in base[:3]) + (1,)
        brick.inputs["Mortar"].default_value = hexrgb("#E2DCCF")
        nt.links.new(vec, brick.inputs["Vector"])
        nt.links.new(brick.outputs["Color"], bsdf.inputs["Base Color"])
        noise = nt.nodes.new("ShaderNodeTexNoise")
        noise.inputs["Scale"].default_value = 18.0
        nt.links.new(vec, noise.inputs["Vector"])
        bump = nt.nodes.new("ShaderNodeBump")
        bump.inputs["Strength"].default_value = 0.35
        nt.links.new(noise.outputs["Fac"], bump.inputs["Height"])
        nt.links.new(bump.outputs["Normal"], bsdf.inputs["Normal"])
    return m


def look_at(obj, target):
    d = Vector(target) - obj.location
    obj.rotation_euler = d.to_track_quat("-Z", "Y").to_euler()


def p(x, y, z):
    """Coordonnées du plan (cm, y vers le sud) → Blender (m, Y vers le nord)."""
    return Vector((x / 100, -y / 100, z / 100))


def area(loc, size, energy, color=(1.0, 0.9, 0.78), shape="DISK", size_y=None):
    bpy.ops.object.light_add(type="AREA", location=loc)
    lt = bpy.context.object
    lt.data.shape = shape
    lt.data.size = size
    if size_y:
        lt.data.size_y = size_y
    lt.data.energy = energy
    lt.data.color = color
    return lt


def build_scene(glb):
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.ops.import_scene.gltf(filepath=glb)
    mats = {}
    ceiling = None
    globes = []
    for o in bpy.context.scene.objects:
        if o.type != "MESH":
            continue
        key = o.name.split("__")[0]
        if key not in mats:
            mats[key] = make_material(key)
        o.data.materials.clear()
        o.data.materials.append(mats[key])
        for poly in o.data.polygons:
            poly.use_smooth = key in ("globe", "feuillage", "fleurs", "fruits")
        if key == "plafond":
            ceiling = o
        if key == "globe":
            globes.append(o)
    missing = sorted(k for k in mats if k not in MATS)
    if missing:
        print("Matériaux non définis (magenta) :", missing)

    sc = bpy.context.scene
    sc.render.engine = "CYCLES"
    sc.cycles.samples = SAMPLES
    sc.cycles.use_denoising = True
    prefs = bpy.context.preferences.addons["cycles"].preferences
    try:
        prefs.compute_device_type = "METAL"
        prefs.get_devices()
        for d in prefs.devices:
            d.use = True
        sc.cycles.device = "GPU"
    except Exception as e:  # repli CPU
        print("GPU indisponible, rendu CPU :", e)
    sc.render.resolution_x, sc.render.resolution_y = 1600, 1200
    sc.view_settings.view_transform = "AgX"
    sc.view_settings.look = "AgX - Base Contrast"

    world = bpy.data.worlds.new("ciel")
    sc.world = world
    world.use_nodes = True
    bg = world.node_tree.nodes["Background"]
    bg.inputs["Color"].default_value = hexrgb("#BFD6EA")
    bg.inputs["Strength"].default_value = 1.6

    # soleil de fin d'après-midi par la fenêtre ouest
    bpy.ops.object.light_add(type="SUN", location=(0, 0, 5))
    sun = bpy.context.object
    sun.data.energy = 3.5
    sun.data.angle = math.radians(1.5)
    sun.data.color = (1.0, 0.93, 0.84)
    look_at(sun, sun.location + Vector((1.0, -0.45, -0.55)))

    # portail dans la baie de la fenêtre
    portal = area(p(-21, 129, 160.5), 1.42, 0, shape="RECTANGLE", size_y=1.09)
    portal.data.cycles.is_portal = True
    look_at(portal, p(100, 129, 160.5))

    # plafonniers cuisine et cellier, réglette sous les meubles hauts
    for x, y in [(90, 110), (230, 140)]:
        area(p(x, y, 248), 0.45, 60)
    area(p(375, 50, 248), 0.4, 45)
    area(p(179, 28, 146.5), 1.3, 25, color=(1.0, 0.88, 0.72), shape="RECTANGLE", size_y=0.04)
    # la suspension éclaire vraiment la table
    for g in globes:
        c = sum((g.matrix_world @ Vector(b) for b in g.bound_box), Vector()) / 8
        bpy.ops.object.light_add(type="POINT", location=c)
        lt = bpy.context.object
        lt.data.energy = 40
        lt.data.shadow_soft_size = 0.14
        lt.data.color = (1.0, 0.85, 0.65)
    return ceiling


VIEWS = {
    # depuis la baie d'entrée, regard vers la rangée nord et la fenêtre
    "entree":  dict(loc=(268, 236, 158), target=(105, 40, 105), lens=17),
    # depuis l'angle de la fenêtre, regard vers le frigo, le four et le cellier
    "fenetre": dict(loc=(12, 120, 160), target=(320, 150, 118), lens=17),
    # depuis le seuil du cellier, porte ouverte : étagères, râtelier à balais, lave-linge, ballon
    "cellier": dict(loc=(322, 110, 172), target=(415, 40, 105), lens=12),
    # vue plongeante, plafond masqué
    "plongee": dict(loc=(330, 360, 470), target=(160, 110, 40), lens=22, no_ceiling=True),
}

for version in VERSIONS:
    suffix = "-deco" if version == "deco" else ""
    ceiling = build_scene(os.path.join(OUT, f"cuisine-a{suffix}.glb"))
    sc = bpy.context.scene
    for name in VUES:
        v = VIEWS[name]
        cam_data = bpy.data.cameras.new(name)
        cam_data.lens = v["lens"]
        cam_data.sensor_width = 36
        cam = bpy.data.objects.new("cam_" + name, cam_data)
        sc.collection.objects.link(cam)
        cam.location = p(*v["loc"])
        look_at(cam, p(*v["target"]))
        sc.camera = cam
        if ceiling:
            ceiling.hide_render = bool(v.get("no_ceiling"))
        sc.render.filepath = os.path.join(OUT, f"rendu-{name}{suffix}.png")
        bpy.ops.render.render(write_still=True)
        print("Rendu :", sc.render.filepath)
    if ceiling:
        ceiling.hide_render = False
    bpy.ops.wm.save_as_mainfile(filepath=os.path.join(OUT, f"cuisine-a{suffix}.blend"), compress=True)
