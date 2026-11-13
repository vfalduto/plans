# Rendu Blender (Cycles) de l'entrée, construit directement depuis 3d/entree/modele.py (pas de FreeCAD).
#
#   /Applications/Blender.app/Contents/MacOS/Blender -b --python 3d/entree/rendu.py -- [échantillons] [vue ...]
#   ex. : just entree-rendu 16 iso_so    (aperçu rapide)
# Vues : iso_so (isométrique depuis le sud-ouest : murs sud et ouest et plafond retirés) ;
#        iso_no (depuis le nord-ouest : murs nord et ouest, tableau et plafond retirés).
# Produit 3d/sortie/entree-rendu-<vue>.png.
#
# Réutilise 3d/rendu.py (matériaux, soleil, ciel, réglages Cycles). Portes fermées ; ce que le modèle ne dessine qu'en
# emprise (angle arrondi à étagères, poignées) est construit ici.

import math
import os
import re
import sys

import bmesh
import bpy
from mathutils import Vector

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.dirname(HERE))
import modele as M  # noqa: E402
import rendu as R  # noqa: E402

OUT = R.OUT
VUES_DEMANDEES = [a for a in R.args if not a.isdigit()]

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
})
ROLES = {"mur": "s_mur", "linteau": "s_mur", "porte": "porte_peinte", "tableau": "electro_blanc", "banc": "s_chene",
         "caisson": "s_chene", "plateau": "s_chene", "tall": "s_blanc", "socle": "s_mur", "miroir": "s_miroir",
         "applique": "globe", "patere": "noir", "facade": "s_chene_v", "facade_p": "s_blanc"}


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


# ------------------------------------------------------------------ scène
def nom_de(b):
    return f"{b.role}__{b.nom}__{b.mur or '-'}"


def build_scene():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    sc = bpy.context.scene
    # sol : couloir, seuils des ouvertures, bout du salon vu par le passage
    prisme("sol__couloir", M.SOL, -2, 0, "s_carrelage", chanfrein=False)
    for b in M.ENVELOPPE:
        if b.role == "linteau":
            boite(f"sol__seuil_{b.nom}__{b.mur}", b.x0, b.x1, b.y0, b.y1, -2, 0, "s_carrelage", chanfrein=False)
    boite("sol__salon__n", 274, 340, -10, 94, -2, 0, "s_carrelage", chanfrein=False)

    for b in M.ENVELOPPE + M.MEUBLES:
        nom = nom_de(b)
        if b.role == "angle":                      # étagères ouvertes en quart de cercle (le plateau couvre le haut)
            ct = contour_arrondi(b.x0, b.x1, b.y0, b.y1, b.arrondi)
            prisme(nom + "_bas", ct, 0, 3, "s_chene")
            for z in M.ANGLE["etageres"]:
                prisme(f"{nom}_{z}", ct, z - 2, z, "s_chene")
            continue
        if b.role == "plateau" and b.arrondi:
            prisme(nom, contour_arrondi(b.x0, b.x1, b.y0, b.y1, b.arrondi), b.z0, b.z1, "s_chene")
            continue
        if b.role == "applique":
            boite(nom + "_platine", 108, 110, b.y0 + 2, b.y1 - 2, b.z0, b.z1, "noir")
            bpy.ops.mesh.primitive_uv_sphere_add(radius=0.055, location=R.p(103, (b.y0 + b.y1) / 2, (b.z0 + b.z1) / 2))
            o = bpy.context.object
            o.name = nom
            bpy.ops.object.shade_smooth()
            habiller(o, "globe")
            continue
        if b.role == "miroir":                     # cadre noir fin autour du miroir
            boite(nom + "_cadre", b.x0 + 0.2, b.x1, b.y0 - 1.2, b.y1 + 1.2, b.z0 - 1.2, b.z1 + 1.2, "noir", chanfrein=False)
            boite(nom, b.x0, b.x1, b.y0, b.y1, b.z0, b.z1, "s_miroir", chanfrein=False)
            continue
        key = ROLES[b.role]
        boite(nom, b.x0, b.x1, b.y0, b.y1, b.z0, b.z1, key,
              chanfrein=b.role not in ("mur", "linteau", "miroir"))

    # poignées : abattants (barre sous le chant haut), portes de la penderie (barres verticales), portes (béquilles)
    c = M.CHAUSSURES
    for k, (y0, y1) in enumerate(c["modules"]):
        ym = (y0 + y1) / 2
        for z in c["rangs"][1:]:
            boite(f"poignee__abattant_{k}_{z}__-", c["x0"] - 1.2, c["x0"], ym - 6, ym + 6, z - 8, z - 7, "noir")
    pe = M.PENDERIE
    xm = (pe["x0"] + pe["x1"]) / 2
    for dx in (-6, 5):
        boite(f"poignee__penderie_{dx}__-", xm + dx, xm + dx + 1, pe["y0"] - 1.5, pe["y0"], 116, 140, "noir")
    for p in M.PORTES:
        if p["type"] != "battante":
            continue
        autre = p["a"] + 6 if p["gond"] == "b" else p["b"] - 6
        d = p["face"] + (M.EP / 2 if p["mur"] in "se" else -M.EP / 2)
        for s in (-1, 1):
            if p["mur"] in "ns":
                boite(f"poignee__{p['nom']}_{s}__{p['mur']}", autre - 6, autre + 6, d + s * 2, d + s * 3.5, 104, 106, "noir")
            else:
                boite(f"poignee__{p['nom']}_{s}__{p['mur']}", d + s * 2, d + s * 3.5, autre - 6, autre + 6, 104, 106, "noir")

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
    sun.data.energy = R.SOLEIL_FORCE / 20
    sun.data.angle = math.radians(8)
    sun.data.color = (1.0, 0.96, 0.9)
    a, h = math.radians(R.SUN_AZ), math.radians(R.SUN_ALT)
    R.look_at(sun, sun.location - Vector((math.sin(a) * math.cos(h), math.cos(a) * math.cos(h), math.sin(h))))
    # plafonnier du couloir (le plafond est retiré, la lumière reste) et applique allumée
    lt = R.area(R.p(177, 150, M.H - 1), 2.4, 260, color=(1.0, 0.9, 0.78), shape="RECTANGLE", size_y=2.4)
    R.look_at(lt, R.p(177, 150, 0))
    bpy.ops.object.light_add(type="POINT", location=R.p(100, M.APPLIQUE["y"], M.APPLIQUE["z"]))
    lt = bpy.context.object
    lt.data.energy, lt.data.shadow_soft_size, lt.data.color = 15, 0.05, (1.0, 0.84, 0.62)
    return sc


# ------------------------------------------------------------------ vues
CX, CY = 177, 190
VIEWS = {
    # depuis le sud-ouest : banc et tableau (mur nord), meuble à chaussures, miroir, patères (mur de la salle de bain)
    "iso_so": dict(ortho=7.0, loc=(CX - 640, CY + 600, 640), target=(CX + 10, CY - 20, 110), murs="so"),
    # depuis le nord-ouest : penderie, angle arrondi, meuble à chaussures, porte d'entrée, portes de la SDB et de la chambre
    "iso_no": dict(ortho=6.4, loc=(CX - 640, CY - 600, 640), target=(CX, CY, 60), murs="no"),
}


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
    coupes = re.compile(rf"__[{v['murs']}](_|$|\.)")
    for o in sc.objects:
        if o.type == "MESH":
            o.visible_camera = not coupes.search(o.name)
    sc.render.filepath = os.path.join(OUT, fichier)
    bpy.ops.render.render(write_still=True)
    print("Rendu :", sc.render.filepath)


if __name__ == "__main__":
    vues = {n: v for n, v in VIEWS.items() if not VUES_DEMANDEES or n in VUES_DEMANDEES}
    sc = build_scene()
    for name, v in vues.items():
        rendre(sc, name, v, f"entree-rendu-{name}.png")
