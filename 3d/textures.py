# Télécharge les textures et les modèles 3D du rendu (CC0, Poly Haven et ambientCG)
# dans 3d/textures/ et 3d/modeles/.
#   python3 3d/textures.py
# Ne retélécharge pas ce qui est déjà là.

import io
import json
import os
import urllib.request
import zipfile

HERE = os.path.dirname(os.path.abspath(__file__))
DEST = os.path.join(HERE, "textures")
UA = {"User-Agent": "plans-cuisine/1.0"}

# nom local → (source, identifiant)
TEXTURES = {
    "noyer": ("polyhaven", "black_walnut_veneer_02"),    # placage noyer brut, 1 × 1 m (foncé au rendu)
    "parquet": ("polyhaven", "herringbone_parquet"),     # bâtons rompus, 3,4 × 3,4 m
    "terrazzo": ("ambientcg", "Terrazzo001"),            # terrazzo gris clair, grain fin
}
MAPS = {"diff": "Diffuse", "nor": "nor_gl", "rough": "Rough"}
ACG = {"diff": "Color", "nor": "NormalGL", "rough": "Roughness"}


def get(url):
    with urllib.request.urlopen(urllib.request.Request(url, headers=UA)) as r:
        return r.read()


def polyhaven(name, asset):
    files = json.loads(get(f"https://api.polyhaven.com/files/{asset}"))
    for short, key in MAPS.items():
        path = os.path.join(DEST, f"{name}_{short}.jpg")
        if not os.path.exists(path):
            with open(path, "wb") as f:
                f.write(get(files[key]["2k"]["jpg"]["url"]))


def ambientcg(name, asset):
    if all(os.path.exists(os.path.join(DEST, f"{name}_{s}.jpg")) for s in ACG):
        return
    z = zipfile.ZipFile(io.BytesIO(get(f"https://ambientcg.com/get?file={asset}_2K-JPG.zip")))
    for short, suffix in ACG.items():
        member = next(n for n in z.namelist() if n.endswith(f"_{suffix}.jpg"))
        with open(os.path.join(DEST, f"{name}_{short}.jpg"), "wb") as f:
            f.write(z.read(member))


# modèles 3D Poly Haven (glTF 1k), dans 3d/modeles/<id>/ ; arbres de la rue compris
MODELES = ["island_tree_01", "island_tree_02",
           "potted_plant_04", "ceramic_vase_04", "wooden_bowl_01", "food_apple_01", "lemon", "pot_enamel_01",
           "book_encyclopedia_set_01", "wicker_basket_01", "wicker_basket_02", "cardboard_box_01",
           "wooden_broom", "plastic_broom"]
MOD = os.path.join(HERE, "modeles")


def modele(asset):
    folder = os.path.join(MOD, asset)
    main = os.path.join(folder, f"{asset}.gltf")
    if os.path.exists(main):
        return
    g = json.loads(get(f"https://api.polyhaven.com/files/{asset}"))["gltf"]["1k"]["gltf"]
    for rel, info in g["include"].items():
        dst = os.path.join(folder, rel)
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        with open(dst, "wb") as f:
            f.write(get(info["url"]))
    with open(main, "wb") as f:
        f.write(get(g["url"]))


os.makedirs(DEST, exist_ok=True)
for name, (src, asset) in TEXTURES.items():
    (polyhaven if src == "polyhaven" else ambientcg)(name, asset)
    print("ok", name, asset)
for asset in MODELES:
    modele(asset)
    print("ok modèle", asset)
