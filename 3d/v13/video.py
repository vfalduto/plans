# Vidéo de la cuisine V13 : tour à 360° en vue isométrique, mannequin debout au centre.
#
#   /Applications/Blender.app/Contents/MacOS/Blender -b --python 3d/v13/video.py -- [apercu]
#   apercu : EEVEE, 960 × 540, pour valider le mouvement → 3d/sortie/v13-video-apercu-360.mp4
#   sans   : Cycles, 1920 × 1080 (rendu définitif)       → 3d/sortie/v13-video-360.mp4
# Sortie vidéo directe de Blender (FFmpeg intégré, H.264).
#
# Reprend la scène de rendu.py (matériaux, lumière du jour). Les murs entre la caméra et la pièce sont masqués à la
# caméra image par image (keyframes de visible_camera) : ils portent toujours ombres et lumière.

import importlib.util
import math
import os
import re
import sys

import bpy
from mathutils import Vector

HERE = os.path.dirname(os.path.abspath(__file__))
_spec = importlib.util.spec_from_file_location("rendu_v13", os.path.join(HERE, "rendu.py"))
V = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(V)
M, R = V.M, V.R

APERCU = "apercu" in R.args
FPS, DUREE = 24, 12                      # un tour complet en 12 s
CENTRE = (240, 135)                      # mannequin : sol libre au milieu de l'ensemble cuisine + cellier (plan, cm)
CAM_R, ELEVATION = 1000, 42              # distance horizontale de la caméra, angle au-dessus de l'horizon (degrés)
MARGE = 1.04                             # cadrage : tout l'appartement visible sur tout le tour, plus 4 %
# objets coupés quand ils sont du côté de la caméra : murs, cloisons et ce qui est posé dessus
MURS = (r"^(mur__|allege__|linteau__|cloison__|porte__entree|ardoise__|aimant__|peinture__|socle__plinthe_|verre__|"
        r"alu__|pan__|papier__|tech__)")
TOUJOURS = r"^(plafond__|ext_)"
SEUIL = 10                               # cm : un mur à plus de 10 du centre, côté caméra, est masqué


# ------------------------------------------------------------------ mannequin (1,75 m, gris neutre, sans visage)
def mannequin(sc, x, y):
    mat = bpy.data.materials.new("mannequin")
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes["Principled BSDF"]
    bsdf.inputs["Base Color"].default_value = (*R.hexrgb("#B9B5AD")[:3], 1)
    bsdf.inputs["Roughness"].default_value = 0.55
    parties = [   # (nom, centre x, y, z en cm, demi-axes x, y, z) ; x vers l'est, y vers le sud, regard vers le nord
        ("tete", 0, 0, 163, 9.5, 11, 12),
        ("cou", 0, 1, 149, 5, 5, 6),
        ("buste", 0, 1, 127, 17, 11, 20),
        ("bassin", 0, 1, 99, 16, 11, 12),
        ("cuisse_g", -9, 1, 72, 7.5, 8, 22),
        ("cuisse_d", 9, 1, 72, 7.5, 8, 22),
        ("jambe_g", -9, 2, 29, 5.5, 6, 23),
        ("jambe_d", 9, 2, 29, 5.5, 6, 23),
        ("pied_g", -9, -4, 4, 5, 12, 4),
        ("pied_d", 9, -4, 4, 5, 12, 4),
        ("bras_g", -21, 2, 126, 4.5, 5, 15),
        ("bras_d", 21, 2, 126, 4.5, 5, 15),
        ("avant_bras_g", -22, 1, 98, 4, 4.5, 14),
        ("avant_bras_d", 22, 1, 98, 4, 4.5, 14),
        ("main_g", -22, 0, 78, 3, 4.5, 7),
        ("main_d", 22, 0, 78, 3, 4.5, 7),
    ]
    for nom, cx, cy, cz, ax, ay, az in parties:
        bpy.ops.mesh.primitive_uv_sphere_add(segments=32, ring_count=16, location=R.p(x + cx, y + cy, cz))
        o = bpy.context.object
        o.name = f"mannequin__{nom}"
        o.scale = (ax / 100, ay / 100, az / 100)
        o.data.materials.append(mat)
        bpy.ops.object.shade_smooth()


# ------------------------------------------------------------------ caméra en orbite et coupes
def orbite(sc):
    cam_data = bpy.data.cameras.new("orbite")
    cam_data.type = "ORTHO"
    cam = bpy.data.objects.new("cam_orbite", cam_data)
    sc.collection.objects.link(cam)
    sc.camera = cam
    a0 = math.atan2(700 - 120, -380 - 250)      # départ : la vue iso (sud-ouest)
    n = FPS * DUREE
    cam_h = CAM_R * math.tan(math.radians(ELEVATION))
    visibles = [o for o in sc.objects if o.type == "MESH" and not (re.match(TOUJOURS, o.name) or V.exterieur(o))]
    coins = [o.matrix_world @ Vector(c) for o in visibles for c in o.bound_box]
    cible = Vector([(min(c[k] for c in coins) + max(c[k] for c in coins)) / 2 for k in range(3)])   # axe du tour
    cx, cy = cible.x * 100, -cible.y * 100
    largeur = 0
    murs = [o for o in sc.objects if o.type in ("MESH", "CURVE") and re.match(MURS, o.name)]
    centres = {o.name: sum((o.matrix_world @ Vector(c) for c in o.bound_box), Vector()) / 8 for o in murs}
    for o in sc.objects:
        if o.type in ("MESH", "CURVE") and (re.match(TOUJOURS, o.name) or V.exterieur(o)):
            o.visible_camera = False
    for f in range(1, n + 1):
        a = a0 + 2 * math.pi * (f - 1) / n
        d = (math.cos(a), math.sin(a))           # direction centre → caméra, sur le plan (cm, y vers le sud)
        cam.location = cible + R.p(CAM_R * d[0], CAM_R * d[1], cam_h)
        R.look_at(cam, cible)
        inv = cam.rotation_euler.to_matrix().inverted()
        pts = [inv @ (c - cam.location) for c in coins]
        demi_x = max(abs(q.x) for q in pts)
        demi_y = max(abs(q.y) for q in pts)
        largeur = max(largeur, 2 * demi_x, 2 * demi_y * sc.render.resolution_x / sc.render.resolution_y)
        cam.keyframe_insert("location", frame=f)
        cam.keyframe_insert("rotation_euler", frame=f)
        for o in murs:
            c = centres[o.name]
            s = (c.x * 100 - cx) * d[0] + (-c.y * 100 - cy) * d[1]
            o.visible_camera = s < SEUIL
            o.keyframe_insert("visible_camera", frame=f)
    cam_data.ortho_scale = largeur * MARGE
    sc.frame_start, sc.frame_end = 1, n
    sc.render.fps = FPS


def sortie_video(sc, fichier):
    im = sc.render.image_settings
    im.media_type = "VIDEO"
    im.file_format = "FFMPEG"
    ff = sc.render.ffmpeg
    ff.format, ff.codec = "MPEG4", "H264"
    ff.constant_rate_factor = "HIGH"
    ff.ffmpeg_preset = "GOOD"
    sc.render.filepath = os.path.join(R.OUT, fichier)


if __name__ == "__main__":
    sc = V.build_scene()
    V.porte_cellier(sc, ouverte=False)
    mannequin(sc, *CENTRE)
    sc.render.resolution_x, sc.render.resolution_y = (960, 540) if APERCU else (1920, 1080)
    orbite(sc)
    if APERCU:
        sc.render.engine = "BLENDER_EEVEE"
        sc.eevee.taa_render_samples = 16
    sortie_video(sc, "v13-video-apercu-360.mp4" if APERCU else "v13-video-360.mp4")
    bpy.ops.render.render(animation=True)
    print("Vidéo :", sc.render.filepath)
