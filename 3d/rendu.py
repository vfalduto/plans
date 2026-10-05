# Rendu Blender (Cycles) de la cuisine, variante A, à partir de 3d/sortie/cuisine-a[-deco].glb.
#
# Prérequis : python3 3d/textures.py (textures, vue extérieure et modèles CC0 dans 3d/textures/ et 3d/modeles/).
# Lancement (sans interface) :
#   /Applications/Blender.app/Contents/MacOS/Blender -b --python 3d/rendu.py -- [échantillons] [sans|deco] [vue ...]
#   ex. : ... -- 32 deco cellier   (aperçu rapide d'une vue, avec décoration)
#         ... -- aucune            (régénère seulement les .blend, sans rendu)
# Sans précision : 256 échantillons (échantillonnage adaptatif), les deux versions, toutes les vues.
#
# Produit dans 3d/sortie/ : rendu-<vue>.png (sans déco), rendu-<vue>-deco.png (avec),
# cuisine-a.blend et cuisine-a-deco.blend (à ouvrir pour changer de point de vue).
# Matériaux : d'après le préfixe du nom de l'objet (« facade_couleur__… » → MATS["facade_couleur"]).

import math
import os
import re
import sys

import bmesh
import bpy
from mathutils import Vector

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "sortie")
TEX = os.path.join(HERE, "textures")
MOD = os.path.join(HERE, "modeles")
args = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
SAMPLES = next((int(a) for a in args if a.isdigit()), 256)
# Essences des meubles toute hauteur, étagères, portes et chaises : texture, couleur de repli, (saturation, valeur)
# Fil de la texture : « u » horizontal dans l'image (noyer), « v » vertical (chêne) ; sert à orienter le fil sur les meubles.
BOIS = {
    "noyer": ("noyer", "#45291A", (1.25, 0.36), "u"),    # noyer huilé, foncé
    "chene": ("chene", "#A8743F", (1.15, 0.72), "v"),    # chêne miel (façades Plum Living)
}
# Variantes de teintes : (couleur des meubles bas et hauts, terrazzo (saturation, valeur, éclats éclaircis 0–1),
# suffixe des fichiers, bois, lampes allumées)
VARIANTES = {
    "sauge": ("#8D9B80", (1.0, 1.0, 0.0), "", "noyer", ()),             # sauge des rendus Gemini, terrazzo clair d'origine
    "fonce": ("#5E6E55", (0.0, 0.82, 0.0), "-fonce", "noyer", ()),      # vert plus foncé, terrazzo gris
    # Canopée Plum Living, chêne miel, terrazzo gris à éclats clairs, suspension allumée
    "canopee": ("#3C524C", (0.0, 0.9, 0.45), "-canopee", "chene", ("suspension",)),
}
VERSIONS = [a for a in args if a in ("sans", "deco")] or ["sans", "deco"]
TEINTES = [a for a in args if a in VARIANTES] or list(VARIANTES)
VUES = [a for a in args if not a.isdigit() and a not in ("sans", "deco") and a not in VARIANTES] or ["entree", "fenetre", "cellier", "assis", "plongee"]
COULEUR_BAS, TEINTE_TERRAZZO, _, ESSENCE, LAMPES = VARIANTES["sauge"]   # remplacés pour chaque variante

# Soleil : position calculée (lieu, date, heure légale). Azimut compté depuis le nord vers l'est.
LIEU = (48.86, 2.35)                 # Paris (latitude, longitude)
DATE_HEURE = (2026, 6, 21, 17, 0)    # 21 juin, 17 h 00 heure d'été
UTC_DECALAGE = 2
SOLEIL_FORCE = 60.0                  # W/m² Blender : rapport soleil / ciel d'une fin de journée claire
CIEL_FORCE = 0.35                    # intensité du ciel physique (éclairage)
EXPOSITION = -0.2                    # compensation d'exposition (IL)
# LAMPES (par variante) : lampes de la cuisine allumées parmi « suspension » et « plafonniers » (plafonniers et réglette) ;
# le cellier, sans fenêtre, reste toujours éclairé.

CHANFREIN = 0.002                    # arêtes arrondies : 2 mm, 2 segments


def position_soleil(lat, lon, an, mois, jour, h, mn, decalage):
    """Hauteur et azimut du soleil en degrés (formules simplifiées de l'almanach, ± 0,5°)."""
    import datetime
    t = datetime.datetime(an, mois, jour, h, mn) - datetime.timedelta(hours=decalage)
    d = (t - datetime.datetime(2000, 1, 1, 12)).total_seconds() / 86400
    g = math.radians((357.529 + 0.98560028 * d) % 360)
    q = (280.459 + 0.98564736 * d) % 360
    lam = math.radians((q + 1.915 * math.sin(g) + 0.020 * math.sin(2 * g)) % 360)
    eps = math.radians(23.439 - 0.00000036 * d)
    ra = math.atan2(math.cos(eps) * math.sin(lam), math.cos(lam))
    dec = math.asin(math.sin(eps) * math.sin(lam))
    gmst = (18.697374558 + 24.06570982441908 * d) % 24
    ha = math.radians(gmst * 15 + lon) - ra
    la = math.radians(lat)
    alt = math.asin(math.sin(la) * math.sin(dec) + math.cos(la) * math.cos(dec) * math.cos(ha))
    az = math.atan2(-math.sin(ha), math.tan(dec) * math.cos(la) - math.sin(la) * math.cos(ha))
    return math.degrees(alt), math.degrees(az) % 360


SUN_ALT, SUN_AZ = position_soleil(*LIEU, *DATE_HEURE, UTC_DECALAGE)


def hexrgb(h):
    h = h.lstrip("#")
    c = [int(h[i:i + 2], 16) / 255 for i in (0, 2, 4)]
    return tuple(((v + 0.055) / 1.055) ** 2.4 if v > 0.04045 else v / 12.92 for v in c) + (1,)


# couleur, rugosité, options :
#   tex     : texture de 3d/textures (noyer, parquet, terrazzo), plaquée en UV ;
#             sens : "v" fil vertical, "h" fil horizontal, "sol" (parquet, tourné de 90°), "bloc"
#   teinte  : (saturation, valeur) appliquées à la texture (noyer huilé = plus sombre, plus saturé)
#   metal, verre (transmission), emission, zellige, cannage, enduit (mur), laque (brillance irrégulière)
NOYER = {"tex": "noyer", "sens": "v", "teinte": (1.25, 0.36)}
MATS = {
    "mur":              ("#F3EEE4", 0.9, {"enduit": True}),
    "plafond":          ("#F5F2EC", 0.95, {"enduit": True}),
    "sol_bois":         ("#B98A55", 0.5, {"tex": "parquet", "sens": "sol", "echelle": 3.4}),
    "sol_carrelage":    ("#D8D5CE", 0.5, {}),
    "facade_couleur":   ("COULEUR_BAS", 0.45, {"laque": True}),
    "facade_noyer":     ("#45291A", 0.5, NOYER),
    "etagere":          ("#45291A", 0.5, dict(NOYER, sens="h")),
    "chaise":           ("#45291A", 0.5, NOYER),
    "porte_bois":       ("#45291A", 0.5, NOYER),
    "table":            ("#A87A4C", 0.45, dict(NOYER, sens="h", teinte=(1.2, 0.85))),
    "stratifie":        ("#D9BDBB", 0.35, {}),                                # stratifié rose poudré (table Véra)
    "epoxy_blanc":      ("#F2F0EC", 0.35, {}),                                # acier laqué époxy blanc
    "caisson":          ("#E9E5DC", 0.6, {}),
    "socle":            ("#2B3436", 0.6, {}),
    "plan":             ("#CFCDC7", 0.3, {"tex": "terrazzo", "sens": "bloc", "echelle": 0.6, "teinte": "terrazzo"}),
    "credence":         ("#EFE7D6", 0.08, {"zellige": True}),                 # zellige ivoire
    "inox":             ("#C9C9C7", 0.3, {"metal": True}),
    "chrome":           ("#E8E8E8", 0.08, {"metal": True}),
    "alu":              ("#B9BCBF", 0.35, {"metal": True}),                   # aluminium anodisé naturel
    # extérieur : rue, façade d'en face
    "sol_ext":          ("#5E5F60", 0.85, {}),
    "pelouse":          ("#4F6B35", 0.9, {"enduit": True}),
    "facade_ext":       ("#B8A488", 0.85, {"enduit": True}),
    "vitre_ext":        ("#1C2228", 0.03, {}),
    "cannage":          ("#D9B98A", 0.6, {"cannage": True}),
    "vitro":            ("#0B0B0C", 0.04, {}),
    "noir":             ("#18181A", 0.35, {}),
    "verre":            ("#FFFFFF", 0.0, {"verre": True}),
    "verre_ambre":      ("#B5651D", 0.05, {"verre": True}),
    "verre_fume":       ("#1A1C1E", 0.05, {}),
    "menuiserie":       ("#F1F1EF", 0.4, {}),
    "porte_peinte":     ("#EEECE6", 0.5, {"laque": True}),
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

# Objets simplifiés remplacés par des modèles Poly Haven (version avec décoration).
#   cacher : objets masqués ; cadre : objets (ou boîte du plan en cm) dans lesquels le modèle est ajusté ;
#   ajuste : "dedans" (échelle pour tenir dans le cadre), "hauteur" (hauteur du cadre) ou "reel" (taille réelle) ;
#   rot : rotation en degrés.
REMPLACEMENTS = [
    dict(cacher=r"__(pot_plante_haut|plante_haut)$", cadre=r"__(pot_plante_haut|plante_haut)$", modele="potted_plant_04"),
    dict(cacher=r"__(vase|tige_\d|fleur_\d)$", cadre=r"__vase$", modele="ceramic_vase_04"),
    dict(cacher=r"__coupe_fruits$", cadre=r"__coupe_fruits$", modele="wooden_bowl_01"),
    dict(cacher=r"__fruit_1$", cadre=r"__fruit_1$", modele="food_apple_01"),
    dict(cacher=r"__fruit_2$", cadre=r"__fruit_2$", modele="food_apple_01", rot=70),
    dict(cacher=r"__fruit_3$", cadre=r"__fruit_3$", modele="lemon", rot=30),
    dict(cacher=r"__(casserole|manche_casserole)$", cadre=r"__casserole$", modele="pot_enamel_01", rot=-90),
    dict(cacher=r"__livre_\d$", cadre=(72, 134, 230, 250, 200, 224), modele="book_encyclopedia_set_01", rot=180),
    dict(cacher=r"__cellier_bas_1$", cadre=r"__cellier_bas_1$", modele="wicker_basket_01", rot=90),
    dict(cacher=r"__cellier_bas_2$", cadre=r"__cellier_bas_2$", modele="wicker_basket_01", rot=90),
    dict(cacher=r"__panier_linge$", cadre=r"__panier_linge$", modele="wicker_basket_01"),
    dict(cacher=r"__cellier_carton_1$", cadre=r"__cellier_carton_1$", modele="cardboard_box_01"),
    dict(cacher=r"__cellier_carton_2$", cadre=r"__cellier_carton_2$", modele="cardboard_box_01"),
    dict(cacher=r"__balai_\d$", cadre=(358, 378, 0, 12, 0, 150), modele="wooden_broom", ajuste="reel"),
]
# Arbres de la rue (dans les deux versions) : cadre en cm du plan, pied au niveau de la rue (-560).
ARBRES = [
    dict(cadre=(-860, -420, -420, 20, -560, 440), modele="island_tree_01", rot=20, ajuste="hauteur"),
    dict(cadre=(-900, -500, 380, 780, -560, 340), modele="island_tree_02", rot=-40, ajuste="hauteur"),
]


def p(x, y, z):
    """Coordonnées du plan (cm, y vers le sud) → Blender (m, Y vers le nord)."""
    return Vector((x / 100, -y / 100, z / 100))


def look_at(obj, target):
    d = Vector(target) - obj.location
    obj.rotation_euler = d.to_track_quat("-Z", "Y").to_euler()


# ------------------------------------------------------------------ géométrie : UV et chanfreins

def make_uvs(obj, sens, echelle):
    """UV en vraie grandeur (m / échelle), projetées par face selon son orientation, fil du bois maîtrisé."""
    me = obj.data
    bm = bmesh.new()
    bm.from_mesh(me)
    uv = bm.loops.layers.uv.verify()
    mw = obj.matrix_world
    for f in bm.faces:
        n = f.normal
        ax = max(range(3), key=lambda i: abs(n[i]))
        for loop in f.loops:
            co = mw @ loop.vert.co
            x, y, z = co.x / echelle, co.y / echelle, co.z / echelle
            if sens == "sol":                      # parquet tourné de 90°
                u, v = y, -x
            elif ax == 2:                          # dessus / dessous
                u, v = x, y
            else:
                h = x if ax == 1 else y            # coordonnée horizontale le long de la face
                u, v = (z, h) if sens == "v" else (h, z)
            loop[uv].uv = (u, v)
    bm.to_mesh(me)
    bm.free()


def chanfreiner(obj):
    """Fusionne les sommets (le glTF les sépare par face) puis arrondit les arêtes vives."""
    me = obj.data
    bm = bmesh.new()
    bm.from_mesh(me)
    bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=0.00005)
    bm.to_mesh(me)
    bm.free()
    mod = obj.modifiers.new("chanfrein", "BEVEL")
    mod.width = CHANFREIN
    mod.segments = 2
    mod.limit_method = "ANGLE"
    mod.angle_limit = math.radians(30)
    mod.use_clamp_overlap = True
    mod.harden_normals = True


# ------------------------------------------------------------------ matériaux

def image(nt, name, short, vec, data=False):
    node = nt.nodes.new("ShaderNodeTexImage")
    node.image = bpy.data.images.load(os.path.join(TEX, f"{name}_{short}.jpg"), check_existing=True)
    if data:
        node.image.colorspace_settings.name = "Non-Color"
    nt.links.new(vec, node.inputs["Vector"])
    return node


def noise(nt, scale, vec=None, detail=4.0):
    n = nt.nodes.new("ShaderNodeTexNoise")
    n.inputs["Scale"].default_value = scale
    n.inputs["Detail"].default_value = detail
    if vec is not None:
        nt.links.new(vec, n.inputs["Vector"])
    return n


def map_range(nt, src, lo, hi):
    m = nt.nodes.new("ShaderNodeMapRange")
    m.inputs["To Min"].default_value = lo
    m.inputs["To Max"].default_value = hi
    nt.links.new(src, m.inputs["Value"])
    return m.outputs["Result"]


def make_material(key):
    col, rough, opt = MATS.get(key, ("#FF00FF", 0.5, {}))
    if col == "COULEUR_BAS":
        col = COULEUR_BAS
    if opt.get("tex") == "noyer" and ESSENCE != "noyer":
        # autre essence : texture, couleur et teinte de la variante (la table garde son éclaircissement relatif)
        tex, col, (sat, val), _ = BOIS[ESSENCE]
        if opt is not NOYER and opt.get("teinte") != NOYER["teinte"]:
            sat, val = sat * opt["teinte"][0] / NOYER["teinte"][0], min(1.0, val * opt["teinte"][1] / NOYER["teinte"][1])
        opt = dict(opt, tex=tex, teinte=(sat, val))
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
    tc = nt.nodes.new("ShaderNodeTexCoord")
    name = opt.get("tex")
    if name:
        vec = tc.outputs["UV"]
        diff = image(nt, name, "diff", vec)
        out = diff.outputs["Color"]
        if "teinte" in opt:
            hsv = nt.nodes.new("ShaderNodeHueSaturation")
            teinte = TEINTE_TERRAZZO if opt["teinte"] == "terrazzo" else opt["teinte"]
            hsv.inputs["Saturation"].default_value, hsv.inputs["Value"].default_value = teinte[:2]
            nt.links.new(out, hsv.inputs["Color"])
            out = hsv.outputs["Color"]
            if len(teinte) > 2 and teinte[2]:
                # éclats éclaircis : rapproche les éclats sombres de la teinte du fond (couleur de repli du matériau)
                mix = nt.nodes.new("ShaderNodeMix")
                mix.data_type = "RGBA"
                mix.blend_type = "LIGHTEN"
                mix.inputs["Factor"].default_value = teinte[2]
                mix.inputs["B"].default_value = hexrgb(col)
                nt.links.new(out, mix.inputs["A"])
                out = mix.outputs["Result"]
        nt.links.new(out, bsdf.inputs["Base Color"])
        rgh = image(nt, name, "rough", vec, data=True)
        mul = nt.nodes.new("ShaderNodeMath")
        mul.operation = "MULTIPLY"
        mul.inputs[1].default_value = rough / 0.6
        nt.links.new(rgh.outputs["Color"], mul.inputs[0])
        nt.links.new(mul.outputs[0], bsdf.inputs["Roughness"])
        nor = image(nt, name, "nor", vec, data=True)
        nmap = nt.nodes.new("ShaderNodeNormalMap")
        nmap.inputs["Strength"].default_value = 0.8
        nt.links.new(nor.outputs["Color"], nmap.inputs["Color"])
        nt.links.new(nmap.outputs["Normal"], bsdf.inputs["Normal"])
    if opt.get("laque"):
        # brillance légèrement irrégulière (traces, voile)
        n = noise(nt, 8.0, tc.outputs["Object"])
        nt.links.new(map_range(nt, n.outputs["Fac"], rough - 0.08, rough + 0.08), bsdf.inputs["Roughness"])
    if opt.get("enduit"):
        # enduit : micro-relief et nuances très faibles
        n = noise(nt, 60.0, tc.outputs["Object"], detail=8.0)
        bump = nt.nodes.new("ShaderNodeBump")
        bump.inputs["Strength"].default_value = 0.05
        nt.links.new(n.outputs["Fac"], bump.inputs["Height"])
        nt.links.new(bump.outputs["Normal"], bsdf.inputs["Normal"])
        mix = nt.nodes.new("ShaderNodeMix")
        mix.data_type = "RGBA"
        mix.inputs["Factor"].default_value = 0.04
        mix.inputs["A"].default_value = hexrgb(col)
        mix.inputs["B"].default_value = hexrgb("#D9D0C2")
        big = noise(nt, 1.5, tc.outputs["Object"])
        mul = nt.nodes.new("ShaderNodeMath")
        mul.operation = "MULTIPLY"
        mul.inputs[1].default_value = 0.5
        nt.links.new(big.outputs["Fac"], mul.inputs[0])
        nt.links.new(mul.outputs[0], mix.inputs["Factor"])
        nt.links.new(mix.outputs["Result"], bsdf.inputs["Base Color"])
    if opt.get("zellige"):
        # carreaux 10 × 10 émaillés posés à joints fins : teinte et inclinaison variables par carreau, émail ondulé
        sep = nt.nodes.new("ShaderNodeSeparateXYZ")
        nt.links.new(tc.outputs["Object"], sep.inputs["Vector"])
        comb = nt.nodes.new("ShaderNodeCombineXYZ")
        add = nt.nodes.new("ShaderNodeMath")
        add.operation = "ADD"
        nt.links.new(sep.outputs["X"], add.inputs[0])
        nt.links.new(sep.outputs["Y"], add.inputs[1])
        nt.links.new(add.outputs[0], comb.inputs["X"])
        nt.links.new(sep.outputs["Z"], comb.inputs["Y"])
        vec = comb.outputs["Vector"]
        brick = nt.nodes.new("ShaderNodeTexBrick")
        brick.offset = 0.0
        brick.inputs["Scale"].default_value = 10.0
        brick.inputs["Brick Width"].default_value = 1.0
        brick.inputs["Row Height"].default_value = 1.0
        brick.inputs["Mortar Size"].default_value = 0.015
        brick.inputs["Mortar Smooth"].default_value = 0.3
        base = hexrgb(col)
        brick.inputs["Color1"].default_value = base
        brick.inputs["Color2"].default_value = tuple(c * 0.82 for c in base[:3]) + (1,)
        brick.inputs["Mortar"].default_value = hexrgb("#CFC6B6")
        nt.links.new(vec, brick.inputs["Vector"])
        nt.links.new(brick.outputs["Color"], bsdf.inputs["Base Color"])
        # relief : joint en creux + carreaux inclinés + ondulation de l'émail
        bw = nt.nodes.new("ShaderNodeRGBToBW")
        nt.links.new(brick.outputs["Color"], bw.inputs["Color"])
        wav = noise(nt, 25.0, vec)
        h = nt.nodes.new("ShaderNodeMath")
        h.operation = "ADD"
        nt.links.new(bw.outputs["Val"], h.inputs[0])
        nt.links.new(wav.outputs["Fac"], h.inputs[1])
        hm = nt.nodes.new("ShaderNodeMath")
        hm.operation = "MULTIPLY"
        nt.links.new(h.outputs[0], hm.inputs[0])
        nt.links.new(brick.outputs["Fac"], hm.inputs[1])
        inv = nt.nodes.new("ShaderNodeMath")
        inv.operation = "SUBTRACT"
        inv.inputs[0].default_value = 1.0
        nt.links.new(brick.outputs["Fac"], inv.inputs[1])
        hj = nt.nodes.new("ShaderNodeMath")
        hj.operation = "ADD"
        nt.links.new(hm.outputs[0], hj.inputs[0])
        nt.links.new(inv.outputs[0], hj.inputs[1])
        bump = nt.nodes.new("ShaderNodeBump")
        bump.inputs["Strength"].default_value = 0.5
        bump.inputs["Distance"].default_value = 0.002
        nt.links.new(hj.outputs[0], bump.inputs["Height"])
        nt.links.new(bump.outputs["Normal"], bsdf.inputs["Normal"])
        nt.links.new(map_range(nt, brick.outputs["Fac"], 0.6, 0.06), bsdf.inputs["Roughness"])
    if opt.get("cannage"):
        # cannage viennois : brins clairs, jours réguliers (transparents) de 6 mm au pas de 12 mm
        sep = nt.nodes.new("ShaderNodeSeparateXYZ")
        nt.links.new(tc.outputs["Object"], sep.inputs["Vector"])
        comb = nt.nodes.new("ShaderNodeCombineXYZ")
        add = nt.nodes.new("ShaderNodeMath")
        add.operation = "ADD"
        nt.links.new(sep.outputs["X"], add.inputs[0])
        nt.links.new(sep.outputs["Z"], add.inputs[1])
        add2 = nt.nodes.new("ShaderNodeMath")
        add2.operation = "ADD"
        nt.links.new(sep.outputs["Y"], add2.inputs[0])
        nt.links.new(sep.outputs["Z"], add2.inputs[1])
        nt.links.new(add.outputs[0], comb.inputs["X"])
        nt.links.new(add2.outputs[0], comb.inputs["Y"])
        vor = nt.nodes.new("ShaderNodeTexVoronoi")
        vor.inputs["Scale"].default_value = 83.0
        vor.inputs["Randomness"].default_value = 0.0
        nt.links.new(comb.outputs["Vector"], vor.inputs["Vector"])
        hole = nt.nodes.new("ShaderNodeMath")
        hole.operation = "GREATER_THAN"
        hole.inputs[1].default_value = 0.3
        nt.links.new(vor.outputs["Distance"], hole.inputs[0])
        transp = nt.nodes.new("ShaderNodeBsdfTransparent")
        mix = nt.nodes.new("ShaderNodeMixShader")
        nt.links.new(hole.outputs[0], mix.inputs["Fac"])
        nt.links.new(transp.outputs[0], mix.inputs[1])
        nt.links.new(bsdf.outputs[0], mix.inputs[2])
        nt.links.new(mix.outputs[0], nt.nodes["Material Output"].inputs["Surface"])
        grain = noise(nt, 300.0, comb.outputs["Vector"])
        nt.links.new(map_range(nt, grain.outputs["Fac"], 0.0, 1.0), bsdf.inputs["Coat Weight"])
    return m


# ------------------------------------------------------------------ modèles Poly Haven

def bbox(objs):
    pts = [o.matrix_world @ Vector(c) for o in objs if o.type == "MESH" for c in o.bound_box]
    lo = Vector((min(v.x for v in pts), min(v.y for v in pts), min(v.z for v in pts)))
    hi = Vector((max(v.x for v in pts), max(v.y for v in pts), max(v.z for v in pts)))
    return lo, hi


def remplacer(sc, liste):
    objs = [o for o in sc.objects if o.type == "MESH"]
    for r in liste:
        cacher = [o for o in objs if "cacher" in r and re.search(r["cacher"], o.name)]
        if "cacher" in r and not cacher:
            continue
        if isinstance(r["cadre"], tuple):
            x0, x1, y0, y1, z0, z1 = r["cadre"]
            lo, hi = p(x0, y1, z0), p(x1, y0, z1)
        else:
            lo, hi = bbox([o for o in objs if re.search(r["cadre"], o.name)])
        for o in cacher:
            o.hide_render = o.hide_viewport = True
        path = os.path.join(MOD, r["modele"], r["modele"] + ".gltf")
        if not os.path.exists(path):
            print("Modèle absent (lancer 3d/textures.py) :", r["modele"])
            continue
        before = set(sc.objects)
        bpy.ops.import_scene.gltf(filepath=path)
        new = [o for o in sc.objects if o not in before]
        root = bpy.data.objects.new("modele_" + r["modele"], None)
        sc.collection.objects.link(root)
        root["exterieur"] = "cacher" not in r
        for o in new:
            o["modele"] = True
            if o.parent is None:
                o.parent = root
        root.rotation_euler.z = math.radians(r.get("rot", 0))
        bpy.context.view_layer.update()
        mlo, mhi = bbox(new)
        size, target = mhi - mlo, hi - lo
        if r.get("ajuste") == "reel":
            s = 1.0
        elif r.get("ajuste") == "hauteur":
            s = target.z / size.z
        else:
            s = min(target[i] / size[i] for i in range(3) if size[i] > 1e-6)
        root.scale = (s, s, s)
        bpy.context.view_layer.update()
        mlo, mhi = bbox(new)
        centre = (lo + hi) / 2
        root.location += Vector((centre.x - (mlo.x + mhi.x) / 2, centre.y - (mlo.y + mhi.y) / 2, lo.z - mlo.z))


# ------------------------------------------------------------------ scène

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


def reglages_cycles(sc):
    """Réglages Cycles pour un intérieur éclairé par une fenêtre (manuel Blender : Light Paths, Sampling, Denoising)."""
    cy = sc.cycles
    cy.samples = SAMPLES
    cy.use_adaptive_sampling = True
    cy.adaptive_threshold = 0.01          # s'arrête plus tôt dans les zones déjà propres
    cy.max_bounces = 16
    cy.diffuse_bounces = 8                 # la lumière rebondit beaucoup dans une petite pièce claire
    cy.glossy_bounces = 6
    cy.transmission_bounces = 12
    cy.transparent_max_bounces = 16
    cy.sample_clamp_direct = 0.0
    cy.sample_clamp_indirect = 10.0        # supprime les « lucioles » des rebonds sans assombrir
    cy.blur_glossy = 1.0                   # filtre des caustiques
    cy.caustics_reflective = False
    cy.caustics_refractive = False
    cy.use_light_tree = True
    cy.use_denoising = True
    cy.denoiser = "OPENIMAGEDENOISE"
    cy.denoising_input_passes = "RGB_ALBEDO_NORMAL"
    cy.denoising_prefilter = "ACCURATE"
    try:
        cy.denoising_use_gpu = True
    except AttributeError:
        pass
    sc.render.use_persistent_data = True   # garde la scène en mémoire entre les vues
    prefs = bpy.context.preferences.addons["cycles"].preferences
    try:
        prefs.compute_device_type = "METAL"
        prefs.get_devices()
        for d in prefs.devices:
            d.use = True
        cy.device = "GPU"
    except Exception as e:  # repli CPU
        print("GPU indisponible, rendu CPU :", e)


def monde(sc):
    """Éclairage et vue par la fenêtre : ciel physique calé sur le soleil.
    Vu directement par la caméra (vue plongeante) : fond gris clair uni."""
    world = bpy.data.worlds.new("ciel")
    sc.world = world
    world.use_nodes = True
    nt = world.node_tree
    sky = nt.nodes.new("ShaderNodeTexSky")
    sky.sky_type = "MULTIPLE_SCATTERING"
    sky.sun_disc = False
    sky.sun_elevation = math.radians(SUN_ALT)
    sky.sun_rotation = math.radians(SUN_AZ)
    bg = nt.nodes["Background"]
    bg.inputs["Strength"].default_value = CIEL_FORCE
    nt.links.new(sky.outputs["Color"], bg.inputs["Color"])
    fond = nt.nodes.new("ShaderNodeBackground")
    fond.inputs["Color"].default_value = hexrgb("#E4E9EC")
    path = nt.nodes.new("ShaderNodeLightPath")
    cam = nt.nodes.new("ShaderNodeMixShader")
    nt.links.new(path.outputs["Is Camera Ray"], cam.inputs["Fac"])
    nt.links.new(bg.outputs["Background"], cam.inputs[1])
    nt.links.new(fond.outputs["Background"], cam.inputs[2])
    nt.links.new(cam.outputs["Shader"], nt.nodes["World Output"].inputs["Surface"])


def build_scene(glb, deco):
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.ops.import_scene.gltf(filepath=glb, import_shading="FLAT")
    sc = bpy.context.scene
    mats = {}
    ceiling = []  # plafonds, masqués dans la vue plongeante
    globes = []
    for o in list(sc.objects):
        if o.type != "MESH":
            continue
        key = o.name.split("__")[0]
        if key not in mats:
            mats[key] = make_material(key)
        o.data.materials.clear()
        o.data.materials.append(mats[key])
        opt = MATS.get(key, (None, None, {}))[2]
        if opt.get("tex"):
            sens = opt.get("sens", "bloc")
            if opt["tex"] == "noyer" and BOIS[ESSENCE][3] == "v" and sens in ("v", "h"):
                sens = "h" if sens == "v" else "v"   # fil vertical dans l'image : on croise la projection
            make_uvs(o, sens, opt.get("echelle", 1.0))
        smooth = key in ("globe", "feuillage", "fleurs", "fruits", "chrome", "tige", "epoxy_blanc")
        for poly in o.data.polygons:
            poly.use_smooth = smooth
        if not smooth and key not in ("verre", "plafond", "credence", "cannage", "stratifie") and "__ext_" not in o.name:
            chanfreiner(o)
        if key == "verre":
            o.visible_shadow = False  # vitrage mince : laisse passer le soleil (pas de caustiques)
        if key == "plafond" or "__ext_" in o.name:
            ceiling.append(o)  # masqués dans la vue plongeante
        if key == "globe":
            globes.append(o)
    missing = sorted(k for k in mats if k not in MATS)
    if missing:
        print("Matériaux non définis (magenta) :", missing)
    remplacer(sc, ARBRES)
    if deco:
        remplacer(sc, REMPLACEMENTS)

    sc.render.engine = "CYCLES"
    reglages_cycles(sc)
    sc.render.resolution_x, sc.render.resolution_y = 1600, 1200
    sc.view_settings.view_transform = "AgX"
    sc.view_settings.look = "AgX - Base Contrast"
    sc.view_settings.exposure = EXPOSITION
    monde(sc)

    # soleil réel : fenêtre ouest, 17 h (heure d'été) le 21 juin à Paris
    bpy.ops.object.light_add(type="SUN", location=(0, 0, 5))
    sun = bpy.context.object
    sun.data.energy = SOLEIL_FORCE
    sun.data.angle = math.radians(0.53)
    sun.data.color = (1.0, 0.95, 0.88)
    a, h = math.radians(SUN_AZ), math.radians(SUN_ALT)
    vers_soleil = Vector((math.sin(a) * math.cos(h), math.cos(a) * math.cos(h), math.sin(h)))
    look_at(sun, sun.location - vers_soleil)

    # portail dans la baie de la fenêtre
    portal = area(p(-21, 129, 160.5), 1.42, 0, shape="RECTANGLE", size_y=1.09)
    portal.data.cycles.is_portal = True
    look_at(portal, p(100, 129, 160.5))

    # cellier (sans fenêtre) éclairé ; plafonniers cuisine, réglette et suspension selon LAMPES
    area(p(375, 50, 248), 0.4, 45)
    if "plafonniers" in LAMPES:
        for x, y in [(90, 110), (230, 140)]:
            area(p(x, y, 248), 0.45, 60)
        area(p(179, 28, 146.5), 1.3, 25, color=(1.0, 0.88, 0.72), shape="RECTANGLE", size_y=0.04)
    if "suspension" not in LAMPES:
        for g in globes:
            g.active_material.node_tree.nodes["Principled BSDF"].inputs["Emission Strength"].default_value = 0.0
        return ceiling
    for g in globes:  # la suspension éclaire vraiment la table
        c = sum((g.matrix_world @ Vector(b) for b in g.bound_box), Vector()) / 8
        bpy.ops.object.light_add(type="POINT", location=c)
        lt = bpy.context.object
        lt.data.energy = 40
        lt.data.shadow_soft_size = 0.14
        lt.data.color = (1.0, 0.85, 0.65)
    return ceiling


# Vues à hauteur d'yeux : personne de 1,75 m, yeux à 163 debout, 120 assise (assise de chaise à 46).
# Visée horizontale et décentrement vertical (shift) : les verticales restent droites, comme en photo d'architecture.
DEBOUT, ASSIS = 163, 120
VIEWS = {
    # depuis la baie d'entrée, regard vers la rangée nord et la fenêtre
    "entree":  dict(loc=(268, 236, DEBOUT), target=(105, 40, DEBOUT), lens=18, shift=-0.12),
    # depuis l'angle de la fenêtre, regard vers le frigo, le four et le cellier
    "fenetre": dict(loc=(12, 120, DEBOUT), target=(320, 150, DEBOUT), lens=18, shift=-0.12),
    # depuis le seuil du cellier, porte ouverte : étagères, râtelier à balais, lave-linge, ballon
    "cellier": dict(loc=(326, 100, DEBOUT), target=(420, 40, DEBOUT), lens=12, shift=-0.15),
    # assis sur la chaise 2 (dossier à l'est), regard vers la fenêtre et la rangée nord
    "assis":   dict(loc=(197, 195, ASSIS), target=(40, 110, ASSIS), lens=20, shift=0.02),
    # vue plongeante, plafond masqué (vue de coupe, hors hauteur d'yeux)
    "plongee": dict(loc=(330, 360, 470), target=(160, 110, 40), lens=22, no_ceiling=True),
}

# Sans effet quand le module est importé (3d/salon_biblio.py réutilise matériaux, soleil et réglages).
if __name__ == "__main__":
    for teinte in TEINTES:
        COULEUR_BAS, TEINTE_TERRAZZO, suffixe_teinte, ESSENCE, LAMPES = VARIANTES[teinte]
        for version in VERSIONS:
            suffix = ("-deco" if version == "deco" else "") + suffixe_teinte
            glb = "cuisine-a-deco.glb" if version == "deco" else "cuisine-a.glb"
            ceiling = build_scene(os.path.join(OUT, glb), deco=version == "deco")
            sc = bpy.context.scene
            for name in VIEWS:  # toutes les caméras dans le .blend, rendu des seules vues demandées
                v = VIEWS[name]
                cam_data = bpy.data.cameras.new(name)
                cam_data.lens = v["lens"]
                cam_data.sensor_width = 36
                cam_data.shift_y = v.get("shift", 0.0)
                cam = bpy.data.objects.new("cam_" + name, cam_data)
                sc.collection.objects.link(cam)
                cam.location = p(*v["loc"])
                look_at(cam, p(*v["target"]))
                sc.camera = cam
                if name not in VUES:
                    continue
                for c in ceiling + [o for o in sc.objects if o.get("exterieur")]:
                    c.hide_render = bool(v.get("no_ceiling"))
                    for ch in c.children_recursive:
                        ch.hide_render = bool(v.get("no_ceiling"))
                sc.render.filepath = os.path.join(OUT, f"rendu-{name}{suffix}.png")
                bpy.ops.render.render(write_still=True)
                print("Rendu :", sc.render.filepath, f"(soleil h {SUN_ALT:.1f}°, az {SUN_AZ:.1f}°)")
            for c in ceiling:
                c.hide_render = False
            bpy.ops.wm.save_as_mainfile(filepath=os.path.join(OUT, f"cuisine-a{suffix}.blend"), compress=True)
