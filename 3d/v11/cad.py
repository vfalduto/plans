# Construit le modèle FreeCAD de la cuisine V11 depuis modele.py.
#
#   /Applications/FreeCAD.app/Contents/Resources/bin/freecadcmd 3d/v11/cad.py
#
# Produit 3d/sortie/cuisine-v11.FCStd et .glb. Dans FreeCAD : X = x, Y = -y (nord en haut), Z = z, en mm.
# Chaque objet s'appelle « rôle__nom » : le rendu Blender choisira le matériau d'après le préfixe.

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

doc = FreeCAD.newDocument("cuisine_v11")
objs = []


def add(nom, shape):
    o = doc.addObject("Part::Feature", nom)
    o.Shape = shape
    objs.append(o)


def solid(x0, x1, y0, y1, z0, z1):
    return Part.makeBox((x1 - x0) * 10, (y1 - y0) * 10, (z1 - z0) * 10, V(x0 * 10, -y1 * 10, z0 * 10))


# cuves : creuses, et percent le plan de travail et la plage de l'évier (jeu 0,6 : pas de faces confondues)
cuves = [b for b in M.MEUBLES if b.role == "cuve"]
for b in M.ENVELOPPE + M.MEUBLES:
    if isinstance(b, M.Cyl):
        s = Part.makeCylinder(b.r * 10, (b.z1 - b.z0) * 10, V(b.cx * 10, -b.cy * 10, b.z0 * 10))
    else:
        s = solid(b.x0, b.x1, b.y0, b.y1, b.z0, b.z1)
    if b.role == "cuve":
        s = s.cut(solid(b.x0 + 0.5, b.x1 - 0.5, b.y0 + 0.5, b.y1 - 0.5, b.z0 + 0.5, b.z1 + 1))
    elif b.role in ("plan", "evier"):
        for c in cuves:
            s = s.cut(solid(c.x0 - 0.6, c.x1 + 0.6, c.y0 - 0.6, c.y1 + 0.6, c.z0, b.z1 + 1))
    add(f"{b.role}__{b.nom}", s)
c = M.BALLON
add(f"{c.role}__{c.nom}", Part.makeCylinder(c.r * 10, (c.z1 - c.z0) * 10, V(c.cx * 10, -c.cy * 10, c.z0 * 10)))
# réseaux d'eau : un cylindre par tronçon
for role, nom, p, z, r in M.RESEAUX:
    for k, (a, b) in enumerate(zip(p, p[1:])):
        d = V((b[0] - a[0]) * 10, -(b[1] - a[1]) * 10, 0)
        add(f"{role}__{nom}_{k + 1}", Part.makeCylinder(r * 10, d.Length, V(a[0] * 10, -a[1] * 10, z * 10), d))

for nom, poly in (("sol_parquet__chambre", M.SOL_PARQUET), ("sol_ciment__cellier_placard", M.SOL_CIMENT)):
    sol = Part.Face(Part.makePolygon([V(x * 10, -y * 10, -20) for x, y in poly + poly[:1]]))
    add(nom, sol.extrude(V(0, 0, 20)))

doc.recompute()
doc.saveAs(os.path.join(OUT, "cuisine-v11.FCStd"))
for o in objs:
    o.Shape.tessellate(0.5)  # sans interface : sinon le glTF sort vide
Import.export(objs, os.path.join(OUT, "cuisine-v11.glb"))
print(f"{len(objs)} objets → {OUT}/cuisine-v11.glb")
