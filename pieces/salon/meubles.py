# Calculs partagés par les deux meubles à fabriquer du salon (étagères et enfilade), repris de 3d/salon/commun.py
# (nombres : voir plus bas). Ni HTML ni SVG : la vue iso est dans pieces/salon/dessin.py ; les
# gabarits de page et la galerie des rendus restent aux générateurs de page.
#
# Chaque document de meuble décrit ses volumes 3D en Piece (cm, repère du salon : x vers l'est depuis le mur ouest,
# y vers le sud depuis le mur nord, z depuis le sol). La même liste sert à la vue iso et aux rendus Blender :
# matière → couleurs du dessin et matériau Blender (MATIERES).

from dataclasses import dataclass


# ------------------------------------------------------------------ nombres
# f (point décimal, coordonnées) et virg (n décimales fixes, « 240,0 ») sont ceux de commun/dessin.py, que plan.py
# recopiait. Les pages des meubles écrivaient leurs cotes autrement : une décimale au plus, sans « ,0 » (« 240 »,
# « 57,7 ») : c'est cote(), ex-virg de enfilade.py et ex-cm de etageres.py.
from commun.dessin import f, virg  # noqa: E402,F401


def cote(v, n=None):
    """Cote affichée : 1 décimale au plus, virgule, sans « ,0 » ; n : nombre de décimales imposé (comme virg)."""
    return f(v).replace(".", ",") if n is None else virg(v, n)


# ------------------------------------------------------------------ volumes 3D
MATIERES = {   # clé : (face avant x1, côté y1, dessus z1) pour le dessin iso ; matériau Blender
    "chene":    (("#B7834B", "#9C6C3A", "#CFA06B"), "s_chene"),     # fil horizontal (dessus, tablettes, côtés)
    "chene_v":  (("#B7834B", "#9C6C3A", "#CFA06B"), "s_chene_v"),   # fil vertical (portes, façades)
    "pin_noir": (("#2A2A2E", "#1E1E21", "#3A3A3F"), "s_pin_noir"),  # pin peint noir mat
    "acier":    (("#8E9399", "#73787E", "#A9AEB4"), "noir"),        # chevilles peintes en noir
    "melamine": (("#F2F0EA", "#DAD7CF", "#FBFAF6"), "s_melamine"),  # mélaminé blanc
    "fibre":    (("#8C6B4E", "#7A5C42", "#9E7C5E"), "s_fibre"),     # panneau de fibres dures (dos)
    "noir":     (("#26262A", "#1B1B1E", "#34343A"), "noir"),        # pieds, quincaillerie visible
}


@dataclass
class Piece:
    nom: str
    x0: float
    x1: float
    y0: float
    y1: float
    z0: float
    z1: float
    matiere: str = "chene"
    groupe: str = ""     # morceaux d'une même pièce de bois (tablette entaillée) : pas de joint entre eux
    forme: str = ""      # "" boîte ; "cyl_y" : rond d'axe y inscrit dans la boîte (chevilles en acier rond)


def derriere(a, b):
    """a est caché par b (vue depuis +x, +y, +z) : séparés sur un axe, a du côté bas."""
    return a.x1 <= b.x0 + 1e-6 or a.y1 <= b.y0 + 1e-6 or a.z1 <= b.z0 + 1e-6


def ordre(ps):
    """Ordre du peintre : tri topologique sur « derrière », repli sur la somme des centres en cas de cycle."""
    reste = sorted(ps, key=lambda p: p.x0 + p.x1 + p.y0 + p.y1 + p.z0 + p.z1)
    sortie = []
    while reste:
        for i, a in enumerate(reste):
            if not any(derriere(b, a) and not derriere(a, b) for b in reste if b is not a):
                sortie.append(reste.pop(i))
                break
        else:
            sortie.append(reste.pop(0))
    return sortie


def aretes(p, face, ps):
    """Arêtes visibles d'une face (avant x1, côté y1 ou dessus z1) : moins les portions communes avec une face
    coplanaire et contiguë d'un morceau du même groupe (le joint n'existe pas dans le bois)."""
    ax = {"x": 0, "y": 1, "z": 2}[face]
    lo = lambda q: (q.x0, q.y0, q.z0)  # noqa: E731
    hi = lambda q: (q.x1, q.y1, q.z1)  # noqa: E731
    a, b = [i for i in range(3) if i != ax]                 # axes de la face
    plan = hi(p)[ax]
    voisins = [q for q in ps if q is not p and p.groupe and q.groupe == p.groupe and abs(hi(q)[ax] - plan) < 1e-6]
    seg = []
    for fixe, cote in ((a, 0), (a, 1), (b, 0), (b, 1)):
        libre = b if fixe == a else a
        val = (lo(p), hi(p))[cote][fixe]
        morceaux = [(lo(p)[libre], hi(p)[libre])]
        for q in voisins:                                   # q touche p de l'autre côté de cette arête
            if abs((hi(q), lo(q))[cote][fixe] - val) > 1e-6:
                continue
            c0, c1 = lo(q)[libre], hi(q)[libre]
            morceaux = [m for u0, u1 in morceaux for m in ((u0, min(u1, c0)), (max(u0, c1), u1)) if m[1] - m[0] > 1e-6]
        for u0, u1 in morceaux:
            k0, k1 = [0, 0, 0], [0, 0, 0]
            k0[ax] = k1[ax] = plan
            k0[fixe] = k1[fixe] = val
            k0[libre], k1[libre] = u0, u1
            seg.append((tuple(k0), tuple(k1)))
    return seg
