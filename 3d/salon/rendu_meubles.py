# Rendus Blender (Cycles) des meubles à fabriquer du salon, pour leurs pages dédiées :
#
#   /Applications/Blender.app/Contents/MacOS/Blender -b --python 3d/salon/rendu_meubles.py -- [échantillons] [vue ...]
#   ex. : just salon-meubles-rendu 16 etageres-iso    (aperçu rapide)
#
# Vues (fichier 3d/sortie/salon-meuble-<vue>.png, copié en salon-meubles-3d/<vue>.jpg) :
#   etageres-iso      tout le mur ouest en 3/4 depuis la pièce, étagères et enfilade
#   etageres-detail   gros plan d'une entaille et de ses deux chevilles
#   enfilade-iso      enfilade fermée en 3/4, étagères au-dessus
#   enfilade-ouverte  la même, portes et tiroir du haut ouverts
#
# Les volumes viennent de pieces_3d() de etageres.py et enfilade.py (mêmes boîtes que les vues iso des pages) ;
# matières → matériaux par commun.MATIERES. Matériaux, sol et soleil repris du rendu du salon (3d/salon/rendu.py).

import importlib.util
import math
import os
import re
import sys

import bpy
from mathutils import Vector

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
_spec = importlib.util.spec_from_file_location("rendu_salon", os.path.join(HERE, "rendu.py"))
RS = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(RS)          # rendu du salon : matériaux, boîtes, sol carrelé (son main ne tourne pas)
R, M = RS.R, RS.M
import commun as C  # noqa: E402
import etageres as ET  # noqa: E402
import enfilade as EN  # noqa: E402

R.MATS.update({
    "s_melamine": ("#F1EFEA", 0.55, {}),     # mélaminé blanc, légèrement satiné
    "s_fibre":    ("#7E6047", 0.8, {}),      # panneau de fibres dures (dos)
})
VUES_DEMANDEES = [a for a in R.args if not a.isdigit()]
E = M.ENFILADE

VIEWS = {
    "etageres-iso": dict(ortho=3.3, loc=(15 + 520, 129 + 330, 165 + 260), target=(15, 129, 160)),
    "etageres-detail": dict(lens=50, loc=(62, 292, 131), target=(4, 236, 120.5)),   # montant M5, tablette T1
    "enfilade-iso": dict(ortho=3.0, loc=(22 + 520, 129 + 330, 60 + 260), target=(22, 129, 75)),
    "enfilade-ouverte": dict(ortho=3.0, loc=(22 + 520, 129 + 330, 60 + 260), target=(22, 129, 75), ouvert=True),
}


def build_scene(ouvert):
    bpy.ops.wm.read_factory_settings(use_empty=True)
    RS._mats.clear()
    sc = bpy.context.scene
    b = RS.boite
    # sol, mur ouest (cloison) et un retour du mur nord, plinthe au sud de l'enfilade
    b("sol__carrelage", 0, 260, -12, M.P, -2, 0, "s_carrelage", chanfrein=False)
    # murs minces : leur tranche du haut, à l'ombre du plafond, ne fait pas de bandeau sombre dans les vues plongeantes
    b("mur__ouest", -0.5, 0, -0.5, M.P, 0, M.H, "s_mur", False)
    b("mur__nord", -0.5, 260, -0.5, 0, 0, M.H, "s_mur", False)
    b("plafond__salon", -12, 260, -12, M.P, M.H, M.H + 2, "s_plafond", False)
    b("plinthe__ouest_s", 0, 1.5, E["y1"], M.PASSAGE["y0"] - M.PASSAGE["cadre"], 0, 8, "s_plinthe", False)
    pieces = ET.pieces_3d() + EN.pieces_3d(ouvert=ouvert)
    for p in pieces:
        if p.forme == "cyl_y":
            RS.rond_y(f"meuble__{p.nom}", p, C.MATIERES[p.matiere][1])
        elif not p.groupe:
            b(f"meuble__{p.nom}", p.x0, p.x1, p.y0, p.y1, p.z0, p.z1, C.MATIERES[p.matiere][1])
    for g in dict.fromkeys(p.groupe for p in pieces if p.groupe):
        RS.planche(g, [p for p in pieces if p.groupe == g])

    sc.render.engine = "CYCLES"
    R.reglages_cycles(sc)
    sc.render.resolution_x, sc.render.resolution_y = 1600, 1200
    sc.view_settings.view_transform = "AgX"
    sc.view_settings.look = "AgX - Base Contrast"
    sc.view_settings.exposure = -0.3
    R.monde(sc)
    # soleil du matin par la baie est (comme le rendu du salon), et une grande lumière douce côté pièce
    bpy.ops.object.light_add(type="SUN", location=(0, 0, 5))
    sun = bpy.context.object
    sun.data.energy, sun.data.angle, sun.data.color = R.SOLEIL_FORCE * 0.5, math.radians(2), (1.0, 0.95, 0.88)
    a, h = math.radians(R.SUN_AZ), math.radians(R.SUN_ALT)
    R.look_at(sun, sun.location - Vector((math.sin(a) * math.cos(h), math.cos(a) * math.cos(h), math.sin(h))))
    fill = R.area(R.p(300, 200, 200), 2.5, 250, shape="RECTANGLE", size_y=2.0)
    R.look_at(fill, R.p(0, 129, 120))
    return sc


def camera(sc, name, v):
    cd = bpy.data.cameras.new(name)
    if "ortho" in v:
        cd.type, cd.ortho_scale = "ORTHO", v["ortho"]
    else:
        cd.lens = v["lens"]
    cam = bpy.data.objects.new("cam_" + name, cd)
    sc.collection.objects.link(cam)
    cam.location = R.p(*v["loc"])
    R.look_at(cam, R.p(*v["target"]))
    return cam


if __name__ == "__main__":
    vues = {n: v for n, v in VIEWS.items() if not VUES_DEMANDEES or n in VUES_DEMANDEES}
    for ouvert in dict.fromkeys(v.get("ouvert", False) for v in vues.values()):
        sc = build_scene(ouvert)
        for name, v in vues.items():
            if v.get("ouvert", False) != ouvert:
                continue
            sc.camera = camera(sc, name, v)
            # plafond caché aux vues en plongée (il masquerait le haut des étagères)
            for o in sc.objects:
                if o.type == "MESH":
                    o.visible_camera = not re.match(r"^plafond__", o.name)
            sc.render.filepath = os.path.join(R.OUT, f"salon-meuble-{name}.png")
            bpy.ops.render.render(write_still=True)
            print("Rendu :", sc.render.filepath)
