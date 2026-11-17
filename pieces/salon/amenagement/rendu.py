# Rendu Blender (Cycles) du salon/aménagement, construit directement depuis les volumes de pieces/salon/ (pas de FreeCAD).
# Repris de l'ancien 3d/salon/rendu.py (supprimé, l'historique git le garde) : les données viennent de
# pieces/salon/piece.py (caméras), pieces/salon/amenagement/document.py (meubles) et pieces/salon/etageres/volumes.py
# (étagères), les matériaux de pieces/salon/meubles.py. pieces/salon/rendu_meubles.py le charge pour ses matériaux et ses boîtes.
#
#   [SALON_ESSENCE=chene|noyer] blender -b --python-exit-code 1 --python pieces/salon/amenagement/rendu.py -- [échantillons] [caméra ...]
# Lancé par `just rendu salon/amenagement` (cache des empreintes : commun/rendu_cache.py, une passe par essence, car
# l'option Bois de la page change le bois des meubles) et `just rendu-apercu salon/amenagement`.
# Caméras : celles de piece.CAMERAS (iso_se, iso_no), toutes sans argument.
# Configuration rendue : table ronde (quotidien), siège DYVLINGE, décoration affichée. Bois : chêne miel, ou noyer quand
# SALON_ESSENCE=noyer (tout le chêne, enfilade, étagères, desserte, table basse et meuble bas, passe en noyer).
# Modèles IKEA (3d/modeles/ikea/) : canapé SÖDERHAMN, siège DYVLINGE, table basse UGGLERUM.
# Produit <sortie>/salon-<caméra>.png, ou salon-<caméra>-noyer.png, avec <sortie> = 3d/sortie (SALON_SORTIE=<dossier>
# pour un autre, SALON_APERCU=1 pour 800 x 600 au lieu de 1600 x 1200).
#
# Réutilise 3d/rendu.py (matériaux, soleil, ciel, réglages Cycles). Les volumes suivent le rôle des objets ;
# ce que le modèle ne dessine qu'en emprise (chaises, plateaux ronds et ovales, baie, plinthes) est construit ici.

import math
import os
import random
import re
import sys

import bpy
from mathutils import Vector

RACINE = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
sys.path.insert(0, RACINE)
import importlib.util  # noqa: E402

_spec = importlib.util.spec_from_file_location("rendu_3d", os.path.join(RACINE, "3d", "rendu.py"))
R = importlib.util.module_from_spec(_spec)
sys.modules["rendu_3d"] = R
_spec.loader.exec_module(R)

from pieces.salon import piece  # noqa: E402
from pieces.salon.amenagement import document as M  # noqa: E402
from pieces.salon.etageres import volumes as etageres_volumes  # noqa: E402
from pieces.salon.meubles import MATIERES  # noqa: E402

OUT = os.environ.get("SALON_SORTIE", R.OUT)
os.makedirs(OUT, exist_ok=True)
APERCU = os.environ.get("SALON_APERCU") == "1"
ESSENCE_RENDUE = os.environ.get("SALON_ESSENCE", "chene")
if ESSENCE_RENDUE not in ("chene", "noyer"):
    raise SystemExit(f"SALON_ESSENCE inconnue : {ESSENCE_RENDUE} (chene ou noyer)")
VUES_DEMANDEES = [a for a in R.args if not a.isdigit()]
CONFIG, ASSISE = "f", "dyv"            # table du quotidien, siège DYVLINGE

# ------------------------------------------------------------------ matériaux
MUR = "#EFE9DC"                         # même blanc chaud que la cuisine (piste Farrow & Ball Wimborne White)
R.ESSENCE = "chene"                     # bois du salon : chêne miel, comme les meubles hauts de la cuisine
R.SUN_ALT, R.SUN_AZ = R.position_soleil(*R.LIEU, 2026, 6, 21, 10, 0, R.UTC_DECALAGE)   # matin : soleil par la baie est
R.EXPOSITION = 1.9
CHENE = {"tex": "noyer", "sens": "h", "teinte": R.NOYER["teinte"]}   # remplacé par le chêne (ESSENCE)
R.MATS.update({
    "s_mur":        (MUR, 0.9, {"enduit": True}),
    "s_plafond":    ("#F4F1EA", 0.95, {"enduit": True}),
    "s_plinthe":    (M.PLINTHES["couleur"], 0.6, {"laque": True}),   # plinthes de l'entrée
    "s_chene":      ("#A8743F", 0.5, CHENE),
    "s_chene_v":    ("#A8743F", 0.5, dict(CHENE, sens="v")),
    "s_noyer":      ("#45291A", 0.45, dict(R.NOYER, sens="h")),        # table Louis-Philippe ancienne
    "s_lin":        ("#CFC5B3", 0.95, {}),                              # canapé, housse lin
    "s_dyvlinge":   ("#D9772B", 0.9, {}),                               # DYVLINGE Kelinge orange
    "s_tapis":      ("#B9A88E", 0.98, {}),
    "s_abat_jour":  ("#F3E9D6", 0.9, {"emission": 0.6}),
    "s_cadre":      ("#1E1E20", 0.4, {}),
    "s_pin_noir":   ("#1C1C1E", 0.75, {}),                              # montants pin peint noir mat
    "s_platine":    ("#1B1B1D", 0.3, {}),
    "s_clim":       ("#F4F4F2", 0.4, {}),
    "s_vinyle":     ("#2A2A2D", 0.5, {}),
    "s_baie":       ("#3A3D40", 0.35, {"metal": True}),
})
ROLES = {
    "mur": "s_mur", "linteau": "s_mur", "cadre": "porte_peinte", "caisson": "s_chene", "facade": "s_chene_v",
    "etagere": "s_chene", "montant": "s_pin_noir", "canape": "s_lin", "table": "s_noyer", "desserte": "s_chene", "vinyles": "s_vinyle",
    "platine": "s_platine", "lampe": "s_abat_jour", "table_basse": "s_chene", "fauteuil": "s_dyvlinge",
    "chilienne": "lin", "tapis": "s_tapis", "lampe_pied": "noir", "plante": "feuillage", "pot": "terre_cuite",
    "cadre_mur": "s_cadre", "projecteur": "noir", "clim": "s_clim", "pied": "noir",
    "papier_peint": "s_papier", "objet": "ceramique", "livre": "livre_c", "rideau": "lin", "tringle": "noir", "poutre": "s_mur",
}
PIEDS_BOIS = r"^pied__(enfilade|console|table_pied)"     # pieds en bois (le reste en acier noir)
LIVRES = ["livre_a", "livre_b", "livre_c", "lin", "tissu_noir", "s_chene", "ceramique_bleue"]
SANS_CHANFREIN = {"tapis", "mur", "linteau", "poutre", "sol", "plafond", "livres", "cadre_mur"}


def carrelage():
    """Carrelage M.CARRELAGE : la photo d'un carreau (texture), un carreau par cellule, retournée en miroir d'une cellule
    à l'autre (moins de répétition visible), joints fins ; position dans le monde, pour que les seuils suivent le sol."""
    c = M.CARRELAGE
    m = bpy.data.materials.new("s_carrelage")
    m.use_nodes = True
    nt = m.node_tree
    bsdf = nt.nodes["Principled BSDF"]
    geo = nt.nodes.new("ShaderNodeNewGeometry")
    t = c["taille"] / 100
    # carreaux : la photo, une image par carreau (échelle 1 / taille), retournée en miroir au-delà de chaque bord
    mp = nt.nodes.new("ShaderNodeMapping")
    mp.inputs["Scale"].default_value = (1 / t, 1 / t, 1 / t)
    nt.links.new(geo.outputs["Position"], mp.inputs["Vector"])
    img = nt.nodes.new("ShaderNodeTexImage")
    img.image = bpy.data.images.load(os.path.join(RACINE, c["texture"]), check_existing=True)
    img.extension = "MIRROR"
    img.interpolation = "Cubic"
    nt.links.new(mp.outputs["Vector"], img.inputs["Vector"])
    # joints : le motif de briques aligné sur les mêmes cellules, son facteur vaut 1 dans le joint
    br = nt.nodes.new("ShaderNodeTexBrick")
    br.offset, br.squash = 0.0, 1.0
    br.inputs["Scale"].default_value = 1.0
    br.inputs["Brick Width"].default_value = t
    br.inputs["Row Height"].default_value = t
    br.inputs["Mortar Size"].default_value = c["joint"] / 100
    br.inputs["Mortar Smooth"].default_value = 0.2
    br.inputs["Bias"].default_value = 0.0
    nt.links.new(geo.outputs["Position"], br.inputs["Vector"])
    # la photo, aplanie, sort pâle sous la lumière du couloir : plus de contraste (gamma) et teinte beige du sol en place
    gam = nt.nodes.new("ShaderNodeGamma")
    gam.inputs["Gamma"].default_value = c["gamma"]
    nt.links.new(img.outputs["Color"], gam.inputs["Color"])
    teinte = nt.nodes.new("ShaderNodeMix")
    teinte.data_type, teinte.blend_type = "RGBA", "MULTIPLY"
    teinte.inputs["Factor"].default_value = 1.0
    nt.links.new(gam.outputs["Color"], teinte.inputs["A"])
    teinte.inputs["B"].default_value = R.hexrgb(c["couleur"])
    mix = nt.nodes.new("ShaderNodeMix")
    mix.data_type = "RGBA"
    nt.links.new(br.outputs["Fac"], mix.inputs["Factor"])
    nt.links.new(teinte.outputs["Result"], mix.inputs["A"])
    mix.inputs["B"].default_value = R.hexrgb(c["couleur_joint"])
    nt.links.new(mix.outputs["Result"], bsdf.inputs["Base Color"])
    nt.links.new(R.map_range(nt, br.outputs["Fac"], 0.45, 0.85), bsdf.inputs["Roughness"])   # carreau satiné, joint mat
    bump = nt.nodes.new("ShaderNodeBump")
    bump.inputs["Strength"].default_value = 0.15
    bump.invert = True
    nt.links.new(br.outputs["Fac"], bump.inputs["Height"])
    nt.links.new(bump.outputs["Normal"], bsdf.inputs["Normal"])
    return m


_mats = {}


def materiau(key):
    if key not in _mats:
        _mats[key] = carrelage() if key == "s_carrelage" else papier_peint() if key == "s_papier" else R.make_material(key)
    return _mats[key]


def papier_peint():
    """Papier peint M.PAPIER_PEINT : image du motif en vraie grandeur (UV en motifs), répétée en miroir dans la hauteur."""
    pp = M.PAPIER_PEINT
    m = bpy.data.materials.new("s_papier")
    m.use_nodes = True
    nt = m.node_tree
    bsdf = nt.nodes["Principled BSDF"]
    bsdf.inputs["Roughness"].default_value = 0.8
    img = nt.nodes.new("ShaderNodeTexImage")
    img.image = bpy.data.images.load(os.path.join(RACINE, pp["image"]), check_existing=True)
    img.extension = "REPEAT"
    tc = nt.nodes.new("ShaderNodeTexCoord")
    sep = nt.nodes.new("ShaderNodeSeparateXYZ")
    nt.links.new(tc.outputs["UV"], sep.inputs["Vector"])
    fr = nt.nodes.new("ShaderNodeMath")
    fr.operation = "PINGPONG"
    fr.inputs[1].default_value = 1.0
    nt.links.new(sep.outputs["Y"], fr.inputs[0])
    comb = nt.nodes.new("ShaderNodeCombineXYZ")
    nt.links.new(sep.outputs["X"], comb.inputs["X"])
    nt.links.new(fr.outputs[0], comb.inputs["Y"])
    nt.links.new(comb.outputs["Vector"], img.inputs["Vector"])
    nt.links.new(img.outputs["Color"], bsdf.inputs["Base Color"])
    return m


def habiller(o, key, sens=None):
    o.data.materials.clear()
    o.data.materials.append(materiau(key))
    if key == "s_papier":
        R.make_uvs(o, "h", M.PAPIER_PEINT["motif"] / 100)
        return
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


def cylindre(nom, cx, cy, r, z0, z1, key, rx=None, n=48):
    """Cylindre vertical ; rx : demi-axe en x différent (ellipse)."""
    bpy.ops.mesh.primitive_cylinder_add(vertices=n, radius=r / 100, depth=(z1 - z0) / 100,
                                        location=R.p(cx, cy, (z0 + z1) / 2))
    o = bpy.context.object
    o.name = nom
    if rx:
        o.scale.x = rx / r
        bpy.ops.object.transform_apply(scale=True)
    bpy.ops.object.shade_smooth()
    habiller(o, key)
    return o


def tourner(objs, cx, cy, angle_plan):
    """Fait tourner des objets autour de l'axe vertical (cx, cy) ; angle du plan (y vers le sud)."""
    pivot = R.p(cx, cy, 0)
    a = math.radians(-angle_plan)
    for o in objs:
        d = o.location - pivot
        o.location = pivot + Vector((d.x * math.cos(a) - d.y * math.sin(a), d.x * math.sin(a) + d.y * math.cos(a), d.z))
        o.rotation_euler.z += a


def chaise(i, cx, cy, a):
    """Chaise bistrot en bois : assise 45 × 45 à 46, dossier côté extérieur (direction a)."""
    h, l = M.CHAISE["l"] / 2, M.CHAISE["l"]
    objs = [boite(f"chaise__{i}_assise", cx - h, cx + h, cy - h, cy + h, 43, 46, "s_noyer")]
    for dx in (-h + 2, h - 5):
        for dy in (-h + 2, h - 5):
            objs.append(boite(f"chaise__{i}_pied_{dx}_{dy}", cx + dx, cx + dx + 3, cy + dy, cy + dy + 3, 0, 43, "s_noyer"))
    objs.append(boite(f"chaise__{i}_dos", cx + h - 4, cx + h - 1, cy - h + 3, cy + h - 3, 62, 85, "s_noyer"))
    for dy in (-h + 2, h - 5):
        objs.append(boite(f"chaise__{i}_montant_{dy}", cx + h - 5, cx + h - 2, cy + dy, cy + dy + 3, 46, 62, "s_noyer"))
    tourner(objs, cx, cy, a)


IKEA = os.path.join(R.MOD, "ikea")


def cacher(motif):
    for o in bpy.context.scene.objects:
        if re.match(motif, o.name):
            o.hide_render = o.hide_viewport = True


def ikea(nom, x0, x1, y0, y1, rot, debout=False):
    """Importe 3d/modeles/ikea/<nom>.glb (dossier vers +Y, face vers -Y), le tourne de rot degrés et le centre sur
    l'emprise du plan, posé au sol, à sa taille réelle (les modèles IKEA sont à l'échelle). debout : posé sur son grand
    côté (couché de 90° autour de x)."""
    sc = bpy.context.scene
    avant = set(sc.objects)
    bpy.ops.import_scene.gltf(filepath=os.path.join(IKEA, nom + ".glb"))
    nouveaux = [o for o in sc.objects if o not in avant]
    racine = bpy.data.objects.new("ikea__" + nom, None)
    sc.collection.objects.link(racine)
    for o in nouveaux:
        if o.parent is None:
            o.parent = racine
    racine.rotation_euler.x = math.radians(90 if debout else 0)
    racine.rotation_euler.z = math.radians(rot)
    bpy.context.view_layer.update()
    lo, hi = R.bbox(nouveaux)
    centre = R.p((x0 + x1) / 2, (y0 + y1) / 2, 0)
    racine.location += Vector((centre.x - (lo.x + hi.x) / 2, centre.y - (lo.y + hi.y) / 2, -lo.z))
    return racine


def reteindre(racine, saturation, valeur):
    """Reteint la texture d'un modèle importé (couleur de base) : saturation et valeur multipliées."""
    objs = [o for o in bpy.context.scene.objects if o.parent == racine or (o.parent and o.parent.parent == racine)]
    for o in objs:
        if o.type != "MESH":
            continue
        for m in o.data.materials:
            nt = m.node_tree
            bsdf = next(n for n in nt.nodes if n.type == "BSDF_PRINCIPLED")
            lien = next((l for l in nt.links if l.to_socket == bsdf.inputs["Base Color"]), None)
            if not lien:
                continue
            hsv = nt.nodes.new("ShaderNodeHueSaturation")
            hsv.inputs["Saturation"].default_value = saturation
            hsv.inputs["Value"].default_value = valeur
            nt.links.new(lien.from_socket, hsv.inputs["Color"])
            nt.links.new(hsv.outputs["Color"], bsdf.inputs["Base Color"])


def visible(b):
    return b.config in ("", CONFIG) and b.assise in ("", ASSISE)


# ------------------------------------------------------------------ scène

# ------------------------------------------------------------------ pièces des meubles à fabriquer (pieces_3d)
def _matieres():
    return MATIERES


ARRONDI = 0.005          # m : arêtes de la planche adoucies (5 mm), comme le chant arrondi du plan de travail


def planche(nom, morceaux):
    """Une pièce de bois d'un seul tenant à partir de ses morceaux (boîtes disjointes) : la boîte englobante moins les
    vides (entailles), par soustraction booléenne, puis arêtes arrondies. Pas de joint entre les morceaux."""
    x0, x1 = min(p.x0 for p in morceaux), max(p.x1 for p in morceaux)
    y0, y1 = min(p.y0 for p in morceaux), max(p.y1 for p in morceaux)
    z0, z1 = min(p.z0 for p in morceaux), max(p.z1 for p in morceaux)
    o = boite(f"meuble__{nom}", x0, x1, y0, y1, z0, z1, _matieres()[morceaux[0].matiere][1], chanfrein=False)
    # vides : le long de chaque rangée de morceaux collés au mur, les intervalles en y qui ne sont pas couverts
    rangs = {}
    for p in morceaux:
        rangs.setdefault((p.x0, p.x1), []).append(p)
    for (a, c), rang in rangs.items():
        if (a, c) == (x0, x1):
            continue
        bords = [y0] + [v for p in sorted(rang, key=lambda p: p.y0) for v in (p.y0, p.y1)] + [y1]
        for k in range(0, len(bords), 2):
            if bords[k + 1] - bords[k] > 1e-6:
                outil = boite(f"vide__{nom}_{k}", a - 1, c, bords[k], bords[k + 1], z0 - 1, z1 + 1, "s_mur", False)
                mod = o.modifiers.new(f"entaille_{k}", "BOOLEAN")
                mod.operation, mod.solver, mod.object = "DIFFERENCE", "EXACT", outil
                bpy.context.view_layer.objects.active = o
                bpy.ops.object.modifier_apply(modifier=mod.name)
                bpy.data.objects.remove(outil, do_unlink=True)
    habiller(o, _matieres()[morceaux[0].matiere][1])
    mod = o.modifiers.new("arrondi", "BEVEL")
    mod.width, mod.segments, mod.limit_method = ARRONDI, 4, "ANGLE"
    mod.angle_limit, mod.use_clamp_overlap, mod.harden_normals = math.radians(30), True, True
    return o


def rond_y(nom, p, key):
    """Rond d'axe y (cheville en acier) inscrit dans la boîte de la pièce, bouts légèrement adoucis."""
    r = min(p.x1 - p.x0, p.z1 - p.z0) / 2
    bpy.ops.mesh.primitive_cylinder_add(vertices=32, radius=r / 100, depth=(p.y1 - p.y0) / 100,
                                        location=R.p((p.x0 + p.x1) / 2, (p.y0 + p.y1) / 2, (p.z0 + p.z1) / 2),
                                        rotation=(math.pi / 2, 0, 0))
    o = bpy.context.object
    o.name = nom
    habiller(o, key)
    mod = o.modifiers.new("arrondi", "BEVEL")
    mod.width, mod.segments, mod.limit_method = 0.0008, 2, "ANGLE"
    mod.angle_limit, mod.use_clamp_overlap = math.radians(30), True
    bpy.ops.object.shade_smooth()
    return o


def etageres():
    """Étagères de la page dédiée (etageres/volumes.py, pieces_3d) : tablettes d'une seule pièce entaillées, chevilles rondes."""
    ps = etageres_volumes.pieces_3d()
    for p in ps:
        if p.forme == "cyl_y":
            rond_y(f"etagere__{p.nom}", p, _matieres()[p.matiere][1])
        elif not p.groupe:
            boite(f"etagere__{p.nom}", p.x0, p.x1, p.y0, p.y1, p.z0, p.z1, _matieres()[p.matiere][1])
    for g in dict.fromkeys(p.groupe for p in ps if p.groupe):
        planche(f"etagere_{g}", [p for p in ps if p.groupe == g])


def build_scene():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    sc = bpy.context.scene
    rnd = random.Random(4)
    # sol carrelé (celui de l'entrée), plafond, plinthes (celles de l'entrée)
    boite("sol__carrelage", 0, M.L, 0, M.P, -2, 0, "s_carrelage", chanfrein=False)
    boite("sol__couloir", -130, 0, M.PASSAGE["y0"] - 10, M.PASSAGE["y1"] + 10, -2, 0, "s_carrelage", chanfrein=False)
    boite("plafond__salon", -12, M.L + 12, -12, M.P + 12, M.H, M.H + 2, "s_plafond", chanfrein=False)
    pl, ep = M.PLINTHES["h"], M.PLINTHES["ep"]
    boite("plinthe__nord", 0, M.DECROCHE["x0"], 0, ep, 0, pl, "s_plinthe", False)
    boite("plinthe__nord_decroche", M.DECROCHE["x0"], M.L, M.DECROCHE["y"], M.DECROCHE["y"] + ep, 0, pl, "s_plinthe", False)
    boite("plinthe__nord_retour", M.DECROCHE["x0"] - ep, M.DECROCHE["x0"], ep, M.DECROCHE["y"] + ep, 0, pl, "s_plinthe", False)
    boite("plinthe__ouest_n", 0, ep, 0, M.PASSAGE["y0"] - M.PASSAGE["cadre"], 0, pl, "s_plinthe", False)
    boite("plinthe__coffre_n", 0, M.COFFRE["x1"], M.COFFRE["y0"] - ep, M.COFFRE["y0"], 0, pl, "s_plinthe", False)
    boite("plinthe__coffre_e", M.COFFRE["x1"], M.COFFRE["x1"] + ep, M.COFFRE["y0"], M.P, 0, pl, "s_plinthe", False)
    boite("plinthe__sud", M.COFFRE["x1"], M.L, M.P - ep, M.P, 0, pl, "s_plinthe", False)
    boite("plinthe__est_s", M.L - ep, M.L, M.BAIE["y1"], M.P, 0, pl, "s_plinthe", False)
    boite("plinthe__est_n", M.L - ep, M.L, M.DECROCHE["y"], M.BAIE["y0"], 0, pl, "s_plinthe", False)
    # fond du couloir vu par le passage
    boite("mur__couloir", -130, -120, M.PASSAGE["y0"] - 10, M.PASSAGE["y1"] + 10, 0, M.H, "s_mur", False)

    for b in M.ENVELOPPE + M.MEUBLES:
        if not visible(b) or b.role in ("projection", "baie", "etagere", "montant"):   # étagères : etageres()
            continue
        nom = f"{b.role}__{b.nom}"
        if b.role == "table" and CONFIG == "f":   # plateau rond (le modèle n'en a que l'emprise)
            cylindre(nom, (b.x0 + b.x1) / 2, (b.y0 + b.y1) / 2, (b.x1 - b.x0) / 2, b.z0, b.z1, "s_noyer", n=96)
            continue
        if b.role == "rideau":                                  # plis : cylindres serrés, en quinconce
            n = round((b.y1 - b.y0) / 8)
            r = (b.x1 - b.x0) / 3
            for k in range(n):
                cy = b.y0 + r + k * (b.y1 - b.y0 - 2 * r) / max(n - 1, 1)
                cylindre(f"{nom}_{k}", (b.x0 + b.x1) / 2 + (r / 2 if k % 2 else -r / 2), cy, r, b.z0, b.z1, "lin", n=24)
            continue
        if b.role == "livre":                                   # livres d'art à plat : couvertures de couleurs
            boite(nom, b.x0, b.x1, b.y0, b.y1, b.z0, b.z1, "livre_c" if b.nom.endswith("1") else "ceramique_bleue")
            continue
        if b.role == "chaise":                                  # chaises construites plus bas, tournées
            continue
        if b.role == "livres":                                  # rangées de livres : dos de couleurs et hauteurs variées
            y = b.y0
            while y < b.y1 - 1:
                e = rnd.uniform(1.8, 4.5)
                boite(f"livres__{b.nom}_{round(y)}", b.x0, b.x0 + rnd.uniform(15, 22), y, min(y + e, b.y1),
                      b.z0, b.z0 + b.z1 - b.z0 - rnd.uniform(0, 7), rnd.choice(LIVRES), chanfrein=False)
                y += e + rnd.uniform(0, 0.3)
            continue
        key = ROLES.get(b.role, "s_mur")
        if b.role == "pied" and re.match(PIEDS_BOIS, nom):
            key = "s_chene_v"
        if b.role == "cadre_mur":                               # cadre noir et image claire en retrait
            boite(nom, b.x0, b.x1, b.y0, b.y1, b.z0, b.z1, "s_cadre", chanfrein=False)
            boite(nom + "_image", b.x0 + 3, b.x1 - 3, b.y0, b.y1 + 0.3, b.z0 + 3, b.z1 - 3,
                  rnd.choice(["ceramique", "lin", "ceramique_bleue", "livre_c"]), chanfrein=False)
            continue
        if isinstance(b, piece.Cyl):
            cylindre(nom, b.cx, b.cy, b.r, b.z0, b.z1, key)
        else:
            boite(nom, b.x0, b.x1, b.y0, b.y1, b.z0, b.z1, key, chanfrein=b.role not in SANS_CHANFREIN)
    for i, (x, y, a) in enumerate(M.CHAISES[CONFIG]):
        chaise(i, x, y, a)
    # meubles IKEA : modèles 3D des fiches produit à la place des volumes simplifiés
    c, d = M.CANAPE, M.DYVLINGE
    cacher(r"^canape__")
    sod = ikea("soderhamn-3", c["x0"], c["x1"], 0, c["p"], 0)
    reteindre(sod, 0.08, 0.6)          # Fridtuna beige clair → Gunnared gris moyen (pas de modèle 3D Gunnared)
    x0, y0, x1, y1 = M.TABLE_BASSE["pos"][CONFIG]
    cacher(rf"^(table_basse|pied)__table_basse_{CONFIG}")
    ikea("ugglerum", x0, x1, y0, y1, 90 if CONFIG == "o" else 0, debout=CONFIG == "o")
    x0, y0 = d["pos"][CONFIG]
    cacher(rf"^(fauteuil|pied)__dyvlinge_{CONFIG}_")
    ikea("dyvlinge", x0, x0 + d["p"], y0, y0 + d["l"], -90)
    # baie coulissante (cadre alu, deux vantaux vitrés)
    ba = M.BAIE
    boite("baie__dormant_h", M.L + 2, M.L + 8, ba["y0"], ba["y1"], ba["h"] - 5, ba["h"], "s_baie", False)
    boite("baie__dormant_b", M.L + 2, M.L + 8, ba["y0"], ba["y1"], 0, 4, "s_baie", False)
    for y in (ba["y0"], ba["milieu"] - 3, ba["y1"] - 6):
        boite(f"baie__montant_{y}", M.L + 2, M.L + 8, y, y + 6, 4, ba["h"] - 5, "s_baie", False)
    boite("baie__vitre_n", M.L + 4.7, M.L + 5.3, ba["y0"] + 6, ba["milieu"] - 3, 4, ba["h"] - 5, "verre", False)
    boite("baie__vitre_s", M.L + 4.7, M.L + 5.3, ba["milieu"] + 3, ba["y1"] - 6, 4, ba["h"] - 5, "verre", False)
    etageres()
    # plantes : modèle Poly Haven à la place des cylindres
    # (noms des objets d'étagère depuis la V4.21 : objet_e<k> au bout sud de chaque tablette, pot_ha / pot_hb en haut)
    R.remplacer(sc, [dict(cacher=rf"^(pot|plante)__(pot|objet|plante)_{n}$", cadre=rf"^(pot|plante)__(pot|objet|plante)_{n}$",
                          modele="potted_plant_04") for n in ("sud", "e1", "ha", "hb")])
    # objets : vases en céramique et bols en bois (Poly Haven) dans l'emprise du modèle
    R.remplacer(sc, [dict(cacher=rf"^objet__{n}$", cadre=rf"^objet__{n}$", modele=m)
                     for n, m in (("objet_e0", "ceramic_vase_04"), ("objet_e3", "ceramic_vase_04"),
                                  ("vase_haut", "ceramic_vase_04"), ("vase_table", "ceramic_vase_04"),
                                  ("objet_e2", "wooden_bowl_01"), ("bol_tb", "wooden_bowl_01"))])

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
    sun.data.energy = R.SOLEIL_FORCE
    sun.data.angle = math.radians(0.53)
    sun.data.color = (1.0, 0.95, 0.88)
    a, h = math.radians(R.SUN_AZ), math.radians(R.SUN_ALT)
    R.look_at(sun, sun.location - Vector((math.sin(a) * math.cos(h), math.cos(a) * math.cos(h), math.sin(h))))
    yc = (ba["y0"] + ba["y1"]) / 2
    portal = R.area(R.p(M.L + 14, yc, ba["h"] / 2), (ba["y1"] - ba["y0"]) / 100, 0, shape="RECTANGLE",
                    size_y=ba["h"] / 100)
    portal.data.cycles.is_portal = True
    R.look_at(portal, R.p(M.L - 100, yc, ba["h"] / 2))
    # lampes allumées, discrètes de jour : suspension, lampadaire, lampes à poser
    for b in M.MEUBLES:
        if b.role == "lampe" and visible(b):
            bpy.ops.object.light_add(type="POINT", location=R.p(b.cx, b.cy, b.z0 - 2))
            lt = bpy.context.object
            lt.data.energy, lt.data.shadow_soft_size, lt.data.color = 12, 0.08, (1.0, 0.84, 0.62)
    return sc


# ------------------------------------------------------------------ vues
def vue_de(c):
    """Une caméra de la pièce (commun.modele.Camera) en réglages de rendu : orthographique, murs cachés par motif."""
    return dict(ortho=c.ortho, loc=c.loc, target=c.cible, coupes=c.reglages.get("coupes"))


# caméras de la pièce (pieces/salon/piece.py), dans leur ordre
VIEWS = {c.id: vue_de(c) for c in piece.CAMERAS}


def camera(sc, name, v):
    cam_data = bpy.data.cameras.new(name)
    cam_data.type = "ORTHO"
    cam_data.ortho_scale = v["ortho"]
    cam = bpy.data.objects.new("cam_" + name, cam_data)
    sc.collection.objects.link(cam)
    cam.location = R.p(*v["loc"])
    R.look_at(cam, R.p(*v["target"]))
    return cam


def rendre(sc, name, v, fichier):
    sc.camera = camera(sc, name, v)
    coupes = v.get("coupes")
    for o in sc.objects:
        if o.type in ("MESH", "CURVE"):
            o.visible_camera = not (coupes and re.match(coupes, o.name))
    sc.render.filepath = os.path.join(OUT, fichier)
    bpy.ops.render.render(write_still=True)
    print("Rendu :", sc.render.filepath)


if __name__ == "__main__":
    inconnues = [a for a in VUES_DEMANDEES if a not in VIEWS]
    if inconnues:
        raise SystemExit(f"caméra inconnue : {', '.join(inconnues)}")
    vues = {n: v for n, v in VIEWS.items() if not VUES_DEMANDEES or n in VUES_DEMANDEES}
    R.ESSENCE = ESSENCE_RENDUE
    suffixe = "" if ESSENCE_RENDUE == "chene" else f"-{ESSENCE_RENDUE}"
    sc = build_scene()
    for name, v in vues.items():
        rendre(sc, name, v, f"salon-{name}{suffixe}.png")
    # un rendu qui n'a pas écrit son fichier fait échouer le lancement (la recette ne note rien)
    manquants = [f"salon-{n}{suffixe}.png" for n in vues if not os.path.exists(os.path.join(OUT, f"salon-{n}{suffixe}.png"))]
    if manquants:
        raise SystemExit(f"rendus manquants : {', '.join(manquants)}")
