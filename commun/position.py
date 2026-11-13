"""Mini-plan de la fiche « Position » : où se trouve la coupe ou le point de vue affiché.

Repris de `miniPlan` et `pointsDeVue` de la maquette. Le dessin ne porte que le contour du sol, les ouvertures des
portes, les traits de coupe et les cônes de vision : la CSS de la fiche donne l'importance de chacun, et le JS pose
`ici` sur le trait ou le cône courant (le HTML statique porte `ici` seulement là où l'appelant l'a demandé).
"""
import math
from html import escape

from commun.dessin import f

MARGE = 14          # cm autour du dessin
LONGUEUR_CONE = 95  # cm
OUVERTURE_CONE = 0.75  # rad, de part et d'autre de l'axe de visée


def _ouverture(p):
    """Segment de l'ouverture d'une porte, posé sur le nu du mur côté couloir."""
    if p["mur"] in "ns":
        return (p["a"], p["face"]), (p["b"], p["face"])
    return (p["face"], p["a"]), (p["face"], p["b"])


def _cone(loc, cible, ici):
    a = math.atan2(cible[1] - loc[1], cible[0] - loc[0])

    def pt(t):
        return f"{f(loc[0] + LONGUEUR_CONE * math.cos(a + t))},{f(loc[1] + LONGUEUR_CONE * math.sin(a + t))}"

    return (f'<g class="pdv{" ici" if ici else ""}">'
            f'<path class="cone" d="M{f(loc[0])},{f(loc[1])} L{pt(-OUVERTURE_CONE)} L{pt(OUVERTURE_CONE)} Z"/>'
            f'<circle class="cam" cx="{f(loc[0])}" cy="{f(loc[1])}" r="9"/></g>')


def mini_plan(sol, portes, traits=(), cones=()) -> str:
    """SVG du mini-plan.

    - `sol` : sommets du contour du sol, en cm.
    - `portes` : dicts de la pièce (`mur`, `face`, `a`, `b`) ; chaque ouverture est un trait `ouv`.
    - `traits` : paires (lettre, ((x0, y0), (x1, y1))) ; un `line.sec[data-k=lettre]` chacun.
    - `cones` : triplets (loc, cible, ici) ; un `g.pdv` chacun, plus `ici` sur le courant.
    """
    pts = list(sol)
    for _, (a, b) in traits:
        pts += [a, b]
    for loc, cible, _ in cones:
        a = math.atan2(cible[1] - loc[1], cible[0] - loc[0])
        pts += [loc] + [(loc[0] + LONGUEUR_CONE * math.cos(a + t), loc[1] + LONGUEUR_CONE * math.sin(a + t))
                        for t in (-OUVERTURE_CONE, OUVERTURE_CONE)]
    x0, x1 = min(p[0] for p in pts) - MARGE, max(p[0] for p in pts) + MARGE
    y0, y1 = min(p[1] for p in pts) - MARGE, max(p[1] for p in pts) + MARGE
    o = [f'<polygon class="sol" points="{" ".join(f"{f(x)},{f(y)}" for x, y in sol)}"/>']
    for p in portes:
        a, b = _ouverture(p)
        o.append(f'<line class="ouv" x1="{f(a[0])}" y1="{f(a[1])}" x2="{f(b[0])}" y2="{f(b[1])}"/>')
    for lettre, (a, b) in traits:
        o.append(f'<line class="sec" data-k="{escape(lettre)}" x1="{f(a[0])}" y1="{f(a[1])}" x2="{f(b[0])}" y2="{f(b[1])}"/>')
    o += [_cone(*c) for c in cones]
    return (f'<svg viewBox="{f(x0)} {f(y0)} {f(x1 - x0)} {f(y1 - y0)}" role="img" aria-label="Position dans l\'entrée">'
            f'{"".join(o)}</svg>')
