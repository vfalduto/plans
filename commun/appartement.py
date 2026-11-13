"""Plan de l'appartement de l'accueil, dans le repère du couloir.

Repère : cm, x vers l'est depuis le mur ouest du couloir, y vers le sud depuis son mur nord (celui de
pieces/entree/piece.py). Les contours, massifs, baies et vitres sont repris de la maquette validée
(plans/maquette/app.html : APPART, MASSIFS, BAIES, VITRES). Chaque pièce y est posée avec les cotes de sa page ; la
pièce ouest et la place de chaque pièce viennent du plan du logement, dont les cotes sont moins justes. La chambre est
posée sur sa porte (y 115 → 186 dans le modèle de l'entrée, branche est de 90 × 104).

Une pièce qui a son pieces/<id>/piece.py y prend son contour (SOL, tourné puis décalé de POSITION) et, si le module
la donne, sa surface (SURFACE) : c'est le cas de l'entrée.
"""
import importlib
import math
from dataclasses import dataclass, replace
from html import escape

from commun.gabarit import adresse
from commun.modele import Site


@dataclass(frozen=True)
class Contour:
    id: str
    nom: str
    p: tuple                # sommets (x, y)
    cotes: str = ""         # sous le nom ; remplacées par la surface de piece.py quand elle existe
    c: tuple | None = None  # place du nom, sinon le centre du cadre
    court: str = ""         # nom affiché s'il est trop long
    vers: str = ""          # pièce du site ouverte au toucher, si ce n'est pas `id`
    inerte: bool = False    # sans document : pas de lien
    petit: bool = False     # nom seul, en petit
    muet: bool = False      # sans nom
    serre: bool = False     # cotes plus petites


APPART = (
    Contour("cuisine", "Cuisine", ((-220, -262), (107, -262), (107, -147), (162, -147), (162, -22), (121, -22),
                                   (121, -10), (-220, -10)), cotes="325 × 252", c=(-60, -128)),
    Contour("cellier", "Cellier", ((107, -262), (214, -262), (214, -218), (264, -218), (264, -162), (162, -162),
                                   (162, -147), (107, -147)), vers="cuisine", petit=True),
    Contour("wc", "WC", ((172, -152), (264, -152), (264, -10), (172, -10)), c=(218, -122), inerte=True),
    Contour("salon", "Salon", ((274, -263), (690, -263), (690, -253), (821, -253), (821, 104), (306, 104), (306, 87),
                               (274, 87)), cotes="547 × 367"),
    Contour("entree", "Entrée", ((0, 0), (264, 0), (264, 104), (354, 104), (354, 208), (110, 208), (110, 374),
                                 (0, 374)), cotes="8,1 m²", c=(132, 50)),
    Contour("sdb", "Salle de bain", ((120, 218), (354, 218), (354, 333), (286, 333), (286, 374), (120, 374)),
            cotes="alcôve 68 × 115", c=(203, 322), court="SdB", serre=True),
    Contour("chambre", "Chambre", ((364, 112), (792, 112), (792, 122), (805, 122), (805, 363), (411, 363), (411, 192),
                                   (364, 192)), cotes="441 × 251", c=(608, 233)),
    Contour("placard", "Placard", ((364, 199), (411, 199), (411, 363), (364, 363)), inerte=True, muet=True),
    Contour("ouest", "Pièce ouest", ((-220, 0), (-10, 0), (-10, 374), (-251, 374), (-251, 331), (-278, 331),
                                     (-278, 215), (-220, 215)), c=(-118, 186), inerte=True),
)

# angle du cellier, gaine de la salle de bain, façade de la chambre (+ 25 de trait) : x0, y0, x1, y1
MASSIFS = ((214, -262, 274, -218), (286, 333, 354, 374), (364, 363, 805, 374))

# ouvertures : r = (x0, y0, x1, y1) dans le mur ; b = battant (charnière, bout fermé, bout ouvert à 90°)
BAIES = (
    ((8, -10, 87, 0), None),                                                  # cuisine, porte coulissante
    ((191, -10, 264, 0), ((191, -10), (264, -10), (191, -83))),               # WC
    ((264, 2, 274, 80), None),                                                # passage du salon
    ((354, 115, 364, 186), ((364, 115), (364, 186), (435, 115))),             # chambre (modèle de l'entrée)
    ((200, 208, 276, 218), ((276, 218), (200, 218), (276, 294))),             # salle de bain
    ((2, 374, 77, 399), ((77, 374), (2, 374), (77, 299))),                    # porte d'entrée
    ((-10, 83, 0, 160), ((0, 160), (0, 83), (77, 160))),                      # pièce ouest
    ((107, -214, 107, -149), None),                                           # cellier, porte pliante
)

VITRES = ((-245, -204, -220, -62), (-245, 24, -220, 148), (821, -190, 846, 14), (805, 202, 830, 344))

MARGE = 62

# styles du plan, portés par le SVG lui-même ; les jetons (--ink, --panel…) viennent de site.css
STYLE = (
    ".pl-masse{fill:var(--ink);stroke:var(--ink);stroke-width:50;stroke-linejoin:miter}"
    ".pl-piece{fill:var(--panel);stroke:var(--ink);stroke-width:6;stroke-linejoin:miter;transition:fill .12s}"
    ".pl-piece.inerte{fill:var(--hair)}"
    "a:hover>.pl-piece,a:focus-visible>.pl-piece{fill:color-mix(in srgb,var(--repere) 32%,var(--panel))}"
    ".pl-baie{fill:var(--panel);pointer-events:none}"
    ".pl-arc{fill:none;stroke:var(--ink);stroke-width:1.2;vector-effect:non-scaling-stroke;pointer-events:none}"
    ".pl-vitre{fill:var(--glass);stroke:var(--ink);stroke-width:1;vector-effect:non-scaling-stroke;"
    "pointer-events:none}"
    ".pl-nom{font:600 29px var(--ui);fill:var(--ink);text-anchor:middle;pointer-events:none}"
    ".pl-cote{font:500 18px var(--ui);font-variant-numeric:tabular-nums;fill:var(--muted);text-anchor:middle;"
    "pointer-events:none}"
    ".pl-cote.serre{font-size:16px}"
    ".pl-petit{font:500 17px var(--ui);fill:var(--muted);text-anchor:middle;pointer-events:none}"
    ".pl-nord{fill:none;stroke:var(--muted);stroke-width:1.4;vector-effect:non-scaling-stroke}"
)


def _e(texte) -> str:
    return escape(str(texte), quote=True)


def _n(v) -> str:
    """Nombre sans « .0 » inutile."""
    v = round(v, 2)
    return str(int(v)) if v == int(v) else str(v)


def _module_piece(id):
    try:
        return importlib.import_module(f"pieces.{id}.piece")
    except ModuleNotFoundError as e:
        if e.name in (f"pieces.{id}", f"pieces.{id}.piece"):
            return None
        raise


def _pose(sol, position):
    """`sol` tourné de position[2] degrés autour de son origine, puis décalé de (position[0], position[1])."""
    dx, dy, angle = position
    cos, sin = math.cos(math.radians(angle)), math.sin(math.radians(angle))
    return tuple((round(x * cos - y * sin + dx, 2), round(x * sin + y * cos + dy, 2)) for x, y in sol)


def _surface(m2) -> str:
    return f"{m2:.1f}".replace(".", ",") + " m²"


def contours() -> list[Contour]:
    """APPART, avec le contour et la surface des pièces qui ont leur piece.py."""
    res = []
    for r in APPART:
        module = _module_piece(r.id)
        if module is not None:
            p = _pose(module.SOL, getattr(module, "POSITION", (0, 0, 0)))
            cotes = _surface(module.SURFACE) if hasattr(module, "SURFACE") else r.cotes
            r = replace(r, p=p, cotes=cotes)
        res.append(r)
    return res


def _centre(p):
    xs, ys = [q[0] for q in p], [q[1] for q in p]
    return (min(xs) + max(xs)) / 2, (min(ys) + max(ys)) / 2


def _points(p) -> str:
    return " ".join(f"{_n(x)},{_n(y)}" for x, y in p)


def plan_appartement(site: Site) -> str:
    """SVG du plan de l'appartement ; chaque pièce du site est un lien vers son premier document.

    Les liens sont relatifs à la racine de site/ (l'accueil est index.html)."""
    pieces = {p.id: p for p in site.pieces}
    zones = contours()
    tous = [q for r in zones for q in r.p]
    xs, ys = [q[0] for q in tous], [q[1] for q in tous]
    x0, y0 = min(xs) - MARGE, min(ys) - MARGE
    w, h = max(xs) - x0 + MARGE, max(ys) - y0 + MARGE

    # murs : masse pleine sous les pièces
    o = [f'<polygon class="pl-masse" points="{_points(r.p)}"/>' for r in zones]
    o += [f'<rect class="pl-masse" x="{a}" y="{b}" width="{c - a}" height="{d - b}"/>' for a, b, c, d in MASSIFS]
    for r in zones:
        piece = pieces.get(r.vers or r.id)
        poly = f'<polygon class="pl-piece{" inerte" if r.inerte else ""}" points="{_points(r.p)}"/>'
        if r.inerte or piece is None or not piece.documents:
            o.append(poly)
        else:
            o.append(f'<a href="{_e(adresse(piece.documents[0]))}" aria-label="{_e(r.nom)}">{poly}</a>')
    for (a, b, c, d), _ in BAIES:
        if c - a > d - b:
            o.append(f'<rect class="pl-baie" x="{a}" y="{b - 3}" width="{c - a}" height="{d - b + 6}"/>')
        else:
            o.append(f'<rect class="pl-baie" x="{a - 3}" y="{b}" width="{c - a + 6}" height="{d - b}"/>')
    o += [f'<rect class="pl-vitre" x="{a}" y="{b}" width="{c - a}" height="{d - b}"/>' for a, b, c, d in VITRES]
    # battant ouvert à 90° et son débattement
    for _, battant in BAIES:
        if battant is None:
            continue
        g, f, v = battant
        rayon = math.hypot(v[0] - g[0], v[1] - g[1])
        sens = 1 if (v[0] - g[0]) * (f[1] - g[1]) - (v[1] - g[1]) * (f[0] - g[0]) > 0 else 0
        o.append(f'<path class="pl-arc" d="M{g[0]},{g[1]} L{v[0]},{v[1]} A{_n(rayon)},{_n(rayon)} 0 0 {sens}'
                 f' {f[0]},{f[1]}"/>')
    for r in zones:
        if r.muet:
            continue
        cx, cy = r.c or _centre(r.p)
        if r.inerte or r.petit:
            o.append(f'<text class="pl-petit" x="{_n(cx)}" y="{_n(cy + 5)}">{_e(r.nom)}</text>')
        else:
            o.append(f'<text class="pl-nom" x="{_n(cx)}" y="{_n(cy)}">{_e(r.court or r.nom)}</text>'
                     f'<text class="pl-cote{" serre" if r.serre else ""}" x="{_n(cx)}" y="{_n(cy + 24)}">'
                     f'{_e(r.cotes)}</text>')
    o.append(f'<text class="pl-petit pl-hors" x="40" y="424">Palier</text>'
             f'<path class="pl-nord" d="M{_n(x0 + 30)},{_n(y0 + 60)} v-36 m-9,13 l9,-13 l9,13"/>'
             f'<text class="pl-petit pl-hors" x="{_n(x0 + 30)}" y="{_n(y0 + 80)}">N</text>')
    return (f'<svg class="plan-appart" viewBox="{_n(x0)} {_n(y0)} {_n(w)} {_n(h)}" role="group"'
            f' aria-label="Plan de l\'appartement"><style>{STYLE}</style>{"".join(o)}</svg>')
