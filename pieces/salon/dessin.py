# Fonctions de dessin SVG communes aux pages du salon (aménagement, étagères, enfilade).
#
# iso_svg et _rond_y : la vue isométrique des meubles, reprise de 3d/salon/commun.py (pages Étagères et Enfilade).
# f, virg, rect, text, cote_h, cote_v : celles de commun/dessin.py, qui rendent exactement les mêmes chaînes que
# celles de 3d/salon/plan.py (reprises par 3d/salon/commun.py pour les deux meubles) ; importées, pas recopiées.
# Ce qui ne sert qu'à une page (degage, chaise_plan, poly, fleche, rappel, svg de l'enfilade…) reste à la page.

import math

from commun.dessin import cote_h, cote_v, f, rect, text, virg  # noqa: F401
from pieces.salon.meubles import MATIERES, aretes, ordre


def _rond_y(p, P, corps, bout):
    """Rond d'axe y en vue iso : silhouette (enveloppe des deux cercles d'extrémité) puis bout sud visible."""
    cx, cz, r = (p.x0 + p.x1) / 2, (p.z0 + p.z1) / 2, min(p.x1 - p.x0, p.z1 - p.z0) / 2
    cercle = lambda y: [P(cx + r * math.cos(t), y, cz + r * math.sin(t))  # noqa: E731
                        for t in (2 * math.pi * k / 24 for k in range(24))]
    pts = sorted(set(cercle(p.y0) + cercle(p.y1)))

    def env(q):                                            # enveloppe convexe (chaîne monotone)
        h = []
        for pt in q:
            while len(h) >= 2 and (h[-1][0] - h[-2][0]) * (pt[1] - h[-2][1]) - (h[-1][1] - h[-2][1]) * (pt[0] - h[-2][0]) <= 0:
                h.pop()
            h.append(pt)
        return h
    contour = env(pts)[:-1] + env(pts[::-1])[:-1]
    d1 = " ".join(f"{f(u)},{f(v)}" for u, v in contour)
    d2 = " ".join(f"{f(u)},{f(v)}" for u, v in cercle(p.y1))
    return (f'<polygon points="{d1}" fill="{corps}" stroke="#1B2A33" stroke-opacity=".6" stroke-width=".3"/>'
            f'<polygon points="{d2}" fill="{bout}" stroke="#1B2A33" stroke-opacity=".6" stroke-width=".3"/>')


def iso_svg(pieces, titre, echelle=2.2, marge=14, legende=None, style=""):
    """Vue axonométrique (isométrique) depuis la pièce, côté sud et en hauteur : faces avant, côté sud et dessus."""
    c, s = math.cos(math.radians(30)), math.sin(math.radians(30))
    # repère du salon indirect (x est, y sud, z haut) : vu de la pièce vers le mur ouest, le sud est à gauche
    P0 = lambda x, y, z: ((x - y) * c * echelle, ((x + y) * s - z) * echelle)  # noqa: E731
    pts = [P0(x, y, z) for p in pieces for x in (p.x0, p.x1) for y in (p.y0, p.y1) for z in (p.z0, p.z1)]
    u0, u1 = min(u for u, _ in pts) - marge, max(u for u, _ in pts) + marge
    v0, v1 = min(v for _, v in pts) - marge, max(v for _, v in pts) + marge
    o = []
    for p in ordre(pieces):
        P = P0
        av, cote, dessus = MATIERES[p.matiere][0]
        if p.forme == "cyl_y":
            o.append(_rond_y(p, P, av, dessus))
            continue
        traits = []
        faces = [((p.x1, p.y0, p.z0), (p.x1, p.y1, p.z0), (p.x1, p.y1, p.z1), (p.x1, p.y0, p.z1), av),
                 ((p.x0, p.y1, p.z0), (p.x1, p.y1, p.z0), (p.x1, p.y1, p.z1), (p.x0, p.y1, p.z1), cote),
                 ((p.x0, p.y0, p.z1), (p.x1, p.y0, p.z1), (p.x1, p.y1, p.z1), (p.x0, p.y1, p.z1), dessus)]
        for (*q, coul), face in zip(faces, "xyz"):
            d = " ".join(f"{f(u)},{f(v)}" for u, v in (P(*k) for k in q))
            o.append(f'<polygon points="{d}" fill="{coul}" stroke="{coul}" stroke-width=".5" stroke-linejoin="round"/>')
            traits += aretes(p, face, pieces)
        if traits:      # arêtes réelles seulement : une tablette entaillée se lit d'une seule pièce
            d = "".join(f"M{f(P(*k0)[0])},{f(P(*k0)[1])}L{f(P(*k1)[0])},{f(P(*k1)[1])}" for k0, k1 in traits)
            o.append(f'<path d="{d}" fill="none" stroke="#1B2A33" stroke-opacity=".6" stroke-width=".35" '
                     f'stroke-linecap="round"/>')
    if legende:
        o.append(text(u0 + 4, v1 - 4, legende, "lbls muted", "start"))
    st = f' style="{style}"' if style else ""
    return (f'<svg viewBox="{f(u0)} {f(v0)} {f(u1 - u0)} {f(v1 - v0)}"{st} role="img" aria-label="{titre}">'
            f'{"".join(o)}</svg>')
