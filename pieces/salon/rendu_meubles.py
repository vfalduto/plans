# Rendus Blender (Cycles) des deux meubles à fabriquer du salon, étagères et enfilade, dans une même scène (mur ouest,
# sol, plinthe) :
#
#   blender -b --python-exit-code 1 --python pieces/salon/rendu_meubles.py -- [échantillons] [vue ...]
#   ex. : just rendu-apercu salon/etageres iso    (aperçu rapide)
#
# Lancé par `just rendu salon/etageres` et `just rendu salon/enfilade` (cache des empreintes : commun/rendu_cache.py),
# et leurs recettes d'aperçu. Vues (fichier <sortie>/salon-meuble-<vue>.png, avec <sortie> = 3d/sortie, SALON_SORTIE=<dossier>
# pour un autre, SALON_APERCU=1 pour 800 x 600 au lieu de 1600 x 1200) : les caméras de pieces/salon/etageres/document.py
# et de pieces/salon/enfilade/document.py (CAMERAS), préfixées par le document :
#   etageres-iso      tout le mur ouest en 3/4 depuis la pièce, étagères et enfilade
#   etageres-detail   gros plan d'une entaille et de ses deux chevilles
#   enfilade-iso      enfilade fermée en 3/4, étagères au-dessus
#   enfilade-ouverte  la même, portes et tiroir du haut ouverts
#
# Les volumes viennent de pieces_3d() de pieces/salon/etageres/volumes.py et de pieces/salon/enfilade/volumes.py (mêmes
# boîtes que les vues iso des pages) ; matières → matériaux par pieces.salon.meubles.MATIERES. Matériaux, sol et soleil
# repris du rendu de l'aménagement (pieces/salon/amenagement/rendu.py, dont le main ne tourne pas ici).

import math
import os
import re
import sys

import bpy
from mathutils import Vector

RACINE = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, RACINE)

from pieces.salon import piece as M  # noqa: E402
from pieces.salon.amenagement import rendu as RS  # noqa: E402
from pieces.salon.enfilade import document as EN_DOC  # noqa: E402
from pieces.salon.enfilade import volumes as EN  # noqa: E402
from pieces.salon.etageres import document as ET_DOC  # noqa: E402
from pieces.salon.etageres import volumes as ET  # noqa: E402
from pieces.salon.meubles import MATIERES  # noqa: E402

R = RS.R
OUT = os.environ.get("SALON_SORTIE", R.OUT)
os.makedirs(OUT, exist_ok=True)
APERCU = os.environ.get("SALON_APERCU") == "1"
R.MATS.update({
    "s_melamine": ("#F1EFEA", 0.55, {}),     # mélaminé blanc, légèrement satiné
    "s_fibre":    ("#7E6047", 0.8, {}),      # panneau de fibres dures (dos)
})
VUES_DEMANDEES = [a for a in R.args if not a.isdigit()]
E = EN_DOC.ENFILADE

# les caméras des deux documents, sous le nom <document>-<caméra> ; réglages : ouvert, coupes
VIEWS = {f"{doc}-{c.id}": dict(ortho=c.ortho, lens=c.focale, loc=c.loc, target=c.cible, **c.reglages)
         for doc, cameras in (("etageres", ET_DOC.CAMERAS), ("enfilade", EN_DOC.CAMERAS)) for c in cameras}


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
            RS.rond_y(f"meuble__{p.nom}", p, MATIERES[p.matiere][1])
        elif not p.groupe:
            b(f"meuble__{p.nom}", p.x0, p.x1, p.y0, p.y1, p.z0, p.z1, MATIERES[p.matiere][1])
    for g in dict.fromkeys(p.groupe for p in pieces if p.groupe):
        RS.planche(g, [p for p in pieces if p.groupe == g])

    sc.render.engine = "CYCLES"
    R.reglages_cycles(sc)
    sc.render.resolution_x, sc.render.resolution_y = (800, 600) if APERCU else (1600, 1200)
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
    if v["ortho"]:
        cd.type, cd.ortho_scale = "ORTHO", v["ortho"]
    else:
        cd.lens = v["lens"]
    cam = bpy.data.objects.new("cam_" + name, cd)
    sc.collection.objects.link(cam)
    cam.location = R.p(*v["loc"])
    R.look_at(cam, R.p(*v["target"]))
    return cam


if __name__ == "__main__":
    inconnues = [a for a in VUES_DEMANDEES if a not in VIEWS]
    if inconnues:
        raise SystemExit(f"caméra inconnue : {', '.join(inconnues)}")
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
                    o.visible_camera = not re.match(v["coupes"], o.name)
            sc.render.filepath = os.path.join(OUT, f"salon-meuble-{name}.png")
            bpy.ops.render.render(write_still=True)
            print("Rendu :", sc.render.filepath)
    # un rendu qui n'a pas écrit son fichier fait échouer le lancement (la recette ne note rien)
    manquants = [n for n in vues if not os.path.exists(os.path.join(OUT, f"salon-meuble-{n}.png"))]
    if manquants:
        raise SystemExit(f"rendus manquants : {', '.join(manquants)}")
