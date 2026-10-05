# Télécharge les textures du rendu (CC0, Poly Haven et ambientCG) dans 3d/textures/.
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


os.makedirs(DEST, exist_ok=True)
for name, (src, asset) in TEXTURES.items():
    (polyhaven if src == "polyhaven" else ambientcg)(name, asset)
    print("ok", name, asset)
