# Maquette 3D de la cuisine V13 pour la page web (three.js) : cuisine-v13-maquette.html.
#
#   /Applications/Blender.app/Contents/MacOS/Blender -b --python 3d/v13/maquette.py
# Reprend la scène de rendu.py (pièces complémentaires, chaises, mannequin de video.py), remplace chaque matériau par
# sa couleur unie (glTF ne porte pas les matériaux procéduraux de Cycles), retire plafond, extérieur et lumières, et
# exporte un glb encodé en base64 dans cuisine-v13-maquette/modele.js (chargé par <script>, donc lisible en file://).

import base64
import importlib.util
import os
import re

import bpy

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))


def charger(nom, fichier):
    spec = importlib.util.spec_from_file_location(nom, os.path.join(HERE, fichier))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


V = charger("rendu_v13", "rendu.py")
VID = charger("video_v13", "video.py")
R = V.R
RETIRES = r"^(plafond__|ext_|cam_)"


def couleur(key):
    """Couleur unie (hex), rugosité et options d'un matériau de rendu.py."""
    if key in V.BETONS:
        return V.BETONS[key][0], V.BETONS[key][2], {}
    if key in V.VELOURS:
        return V.VELOURS[key], 0.9, {}
    if key.startswith("v11_chene"):
        return R.BOIS[R.ESSENCE][1], 0.5, {}
    col, rough, opt = R.MATS.get(key, (None, 0.5, {}))
    return (R.COULEUR_BAS if col == "COULEUR_BAS" else col), rough, opt


def unie(key, cache):
    if key in cache:
        return cache[key]
    col, rough, opt = couleur(key)
    if col is None:
        return None
    m = bpy.data.materials.new("web_" + key)
    m.use_nodes = True
    bsdf = m.node_tree.nodes["Principled BSDF"]
    bsdf.inputs["Base Color"].default_value = R.hexrgb(col)
    bsdf.inputs["Roughness"].default_value = rough
    bsdf.inputs["Metallic"].default_value = 1.0 if opt.get("metal") else 0.0
    if opt.get("emission"):
        bsdf.inputs["Emission Color"].default_value = R.hexrgb(col)
        bsdf.inputs["Emission Strength"].default_value = 1.0
    if opt.get("verre"):
        bsdf.inputs["Alpha"].default_value = 0.15
        m.surface_render_method = "BLENDED"
    cache[key] = m
    return m


if __name__ == "__main__":
    sc = V.build_scene()
    V.porte_cellier(sc, ouverte=False)
    VID.mannequin(sc, *VID.CENTRE)
    for o in list(sc.objects):
        if (o.type in ("CAMERA", "LIGHT") or V.exterieur(o)
                or o.type in ("MESH", "CURVE") and (o.hide_render or re.match(RETIRES, o.name))):
            bpy.data.objects.remove(o, do_unlink=True)
    cache, sans = {}, set()
    for o in sc.objects:
        for slot in o.material_slots:
            if slot.material is None or slot.material.name.startswith("mannequin"):
                continue
            key = re.sub(r"\.\d+$", "", slot.material.name)
            m = unie(key, cache)
            if m is None:
                sans.add(key)          # modèles Poly Haven (plante…) : matériau d'origine, textures comprises
            else:
                slot.material = m
    if sans:
        print("Matériaux gardés tels quels :", sorted(sans))
    glb = os.path.join(R.OUT, "cuisine-v13-maquette.glb")
    bpy.ops.export_scene.gltf(filepath=glb, export_format="GLB", export_apply=True, export_lights=False,
                              export_cameras=False, export_image_format="JPEG", export_jpeg_quality=80)
    dossier = os.path.join(ROOT, "cuisine-v13-maquette")
    os.makedirs(dossier, exist_ok=True)
    with open(glb, "rb") as f, open(os.path.join(dossier, "modele.js"), "w") as js:
        js.write("window.MODELE_GLB = \"" + base64.b64encode(f.read()).decode() + "\";\n")
    print("Maquette :", os.path.join(dossier, "modele.js"), os.path.getsize(glb) // 1024, "ko (glb)")
