"""Fonctions de dessin SVG communes aux générateurs (reprises de 3d/entree/plan.py)."""
import math
from html import escape


def virg(v, n=1):
    return f"{v:.{n}f}".replace(".", ",")


def f(v):
    return f"{round(v, 1):g}"


def rect(x0, y0, x1, y1, cls, rx=0):
    r = f' rx="{f(rx)}"' if rx else ""
    return f'<rect class="{cls}" x="{f(x0)}" y="{f(y0)}" width="{f(x1 - x0)}" height="{f(y1 - y0)}"{r}/>'


def text(x, y, s, cls="lbl", anchor="middle", extra=""):
    return f'<text class="{cls}" x="{f(x)}" y="{f(y)}" text-anchor="{anchor}"{extra}>{escape(s)}</text>'


def rot(x, y):
    return f' transform="rotate(-90 {f(x)} {f(y)})"'


def cote_h(x0, x1, y, label=None, t=3):
    label = label or f(abs(x1 - x0))
    return "".join([
        f'<line class="dim" x1="{f(x0)}" y1="{f(y)}" x2="{f(x1)}" y2="{f(y)}"/>',
        f'<line class="dim" x1="{f(x0)}" y1="{f(y - t)}" x2="{f(x0)}" y2="{f(y + t)}"/>',
        f'<line class="dim" x1="{f(x1)}" y1="{f(y - t)}" x2="{f(x1)}" y2="{f(y + t)}"/>',
        text((x0 + x1) / 2, y - 2.5, label, "dimt"),
    ])


def cote_v(y0, y1, x, label=None, t=3):
    label = label or f(abs(y1 - y0))
    ym = (y0 + y1) / 2
    return "".join([
        f'<line class="dim" x1="{f(x)}" y1="{f(y0)}" x2="{f(x)}" y2="{f(y1)}"/>',
        f'<line class="dim" x1="{f(x - t)}" y1="{f(y0)}" x2="{f(x + t)}" y2="{f(y0)}"/>',
        f'<line class="dim" x1="{f(x - t)}" y1="{f(y1)}" x2="{f(x + t)}" y2="{f(y1)}"/>',
        text(x - 2.5, ym, label, "dimt", extra=rot(x - 2.5, ym)),
    ])


def degage(a, b, label=None):
    """Passage libre entre deux points (trait vert), valeur au milieu."""
    d = math.dist(a, b)
    xm, ym = (a[0] + b[0]) / 2, (a[1] + b[1]) / 2
    vertical = abs(b[1] - a[1]) > abs(b[0] - a[0])
    t = text(xm - 3, ym, label or f"{d:.0f}", "passt", extra=rot(xm - 3, ym)) if vertical else text(xm, ym - 3, label or f"{d:.0f}", "passt")
    return (f'<line class="pass" x1="{f(a[0])}" y1="{f(a[1])}" x2="{f(b[0])}" y2="{f(b[1])}"/>'
            + "".join(f'<circle class="passm" cx="{f(p[0])}" cy="{f(p[1])}" r="1.3"/>' for p in (a, b)) + t)


def coin_arrondi(x0, x1, y0, y1, r, cls):
    """Rectangle vu de dessus, coin nord-ouest arrondi (quart de cercle de rayon r)."""
    return (f'<path class="{cls}" d="M{f(x1)} {f(y0)} L{f(x1)} {f(y1)} L{f(x0)} {f(y1)} L{f(x0)} {f(y0 + r)} '
            f'A{f(r)} {f(r)} 0 0 1 {f(x0 + r)} {f(y0)} Z"/>')


# ------------------------------------------------------------------ portes (plan)
