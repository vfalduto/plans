# Construit le modèle FreeCAD du meuble linge de la salle de bain V3 depuis modele.py, dans les deux versions.
#
#   /Applications/FreeCAD.app/Contents/Resources/bin/freecadcmd 3d/sdb/cad.py
#
# Produit 3d/sortie/sdb-meuble-v3-{d,g}.FCStd et .glb (d : machine à droite, g : machine à gauche).
# Dans FreeCAD : X = x, Y = -y (nord en haut), Z = z, en mm. Chaque objet s'appelle « repère__nom » (ou « rôle__nom »
# pour la machine et les équipements) ; les pièces sont rangées dans un groupe par sous-ensemble.

import os
import sys

import FreeCAD
import Import
import Part
from FreeCAD import Vector as V

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import modele as M  # noqa: E402

OUT = os.path.join(HERE, "..", "sortie")
os.makedirs(OUT, exist_ok=True)


def boite(x0, x1, y0, y1, z0, z1):
    return Part.makeBox((x1 - x0) * 10, (y1 - y0) * 10, (z1 - z0) * 10, V(x0 * 10, -y1 * 10, z0 * 10))


def forme(b):
    if isinstance(b, M.Profil):
        pts = [V(x * 10, -b.y0 * 10, z * 10) for x, z in b.xz]
        face = Part.Face(Part.makePolygon(pts + pts[:1]))
        return face.extrude(V(0, -(b.y1 - b.y0) * 10, 0))
    s = boite(b.x0, b.x1, b.y0, b.y1, b.z0, b.z1)
    if b.encoche:
        x0, x1, y0, y1 = b.encoche
        s = s.cut(boite(x0, x1, y0, y1, b.z0 - 1, b.z1 + 1))
    return s


for c in ("d", "g"):
    nom = f"sdb-meuble-v3-{c}"
    doc = FreeCAD.newDocument(nom.replace("-", "_"))
    objs, groupes = [], {}
    for k, b in enumerate(M.version(c)):
        o = doc.addObject("Part::Feature", f"{b.rep or b.role}__{b.nom}")
        o.Shape = forme(b)
        g = b.groupe or "equipements"
        if g not in groupes:
            groupes[g] = doc.addObject("App::DocumentObjectGroup", g)
        groupes[g].addObject(o)
        objs.append(o)
    doc.recompute()
    doc.saveAs(os.path.join(OUT, f"{nom}.FCStd"))
    for o in objs:
        o.Shape.tessellate(0.5)  # sans interface : sinon le glTF sort vide
    Import.export(objs, os.path.join(OUT, f"{nom}.glb"))
    print(f"{len(objs)} objets → {OUT}/{nom}.glb")
