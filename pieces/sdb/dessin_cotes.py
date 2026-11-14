"""Aides du dessin coté, partagées par les deux meubles de la salle de bain.

Copies, à l'octet, de 3d/sdb/plan.py (f, cm, text, poly) et de 3d/sdb/cotes.py (cote_h, cote_v, niveaux, etiquette, svg) :
nombres à deux décimales dans le SVG (pas commun.dessin, qui arrondit à une décimale), cotes affichées à une décimale.
CSS : les règles des dessins de cotes.py, sans la mise en page de l'ancienne page ni police à chasse fixe ; les jetons
absents de commun/site.css (--tile, --dg) sont remplacés par leur valeur.
"""
from html import escape


def f(v):
    return f"{round(v, 2):g}"


def cm(v):
    """Cote en cm affichée : 1 décimale au plus, virgule française."""
    return f"{round(v, 1):g}".replace(".", ",")


def poly(pts, cls):
    return f'<polygon class="{cls}" points="{" ".join(f"{f(u)},{f(v)}" for u, v in pts)}"/>'


def text(x, y, s, cls="lbl", anchor="middle", extra=""):
    return f'<text class="{cls}" x="{f(x)}" y="{f(y)}" text-anchor="{anchor}"{extra}>{escape(s)}</text>'


def cote_h(x0, x1, y, label=None, dy=0, ext=None, place=""):
    """Cote horizontale ; dy décale le texte (petites cotes) ; ext = y de départ des lignes d'attache ; place :
    "gauche" ou "droite" pour écrire une petite cote hors de la ligne, à côté de son trait."""
    label = label or cm(abs(x1 - x0))
    o = []
    if ext is not None:
        o += [f'<line class="ext" x1="{f(x)}" y1="{f(ext)}" x2="{f(x)}" y2="{f(y)}"/>' for x in (x0, x1)]
    o += [f'<line class="dim" x1="{f(x0)}" y1="{f(y)}" x2="{f(x1)}" y2="{f(y)}"/>',
          f'<line class="tick" x1="{f(x0 - .8)}" y1="{f(y + .8)}" x2="{f(x0 + .8)}" y2="{f(y - .8)}"/>',
          f'<line class="tick" x1="{f(x1 - .8)}" y1="{f(y + .8)}" x2="{f(x1 + .8)}" y2="{f(y - .8)}"/>',
          text(x0 - 1 if place == "gauche" else x1 + 1 if place == "droite" else (x0 + x1) / 2, y - 0.9 + dy, label,
                  "ct", "end" if place == "gauche" else "start" if place == "droite" else "middle")]
    return "".join(o)


def cote_v(y0, y1, x, label=None, dx=0, ext=None, place=""):
    """Cote verticale (y du dessin) ; place : "haut" ou "bas" pour une petite cote écrite au-delà de son trait."""
    label = label or cm(abs(y1 - y0))
    ym = (y0 + y1) / 2
    if place:
        ym = min(y0, y1) - 2.4 if place == "haut" else max(y0, y1) + 2.4
    o = []
    if ext is not None:
        o += [f'<line class="ext" x1="{f(ext)}" y1="{f(y)}" x2="{f(x)}" y2="{f(y)}"/>' for y in (y0, y1)]
    o += [f'<line class="dim" x1="{f(x)}" y1="{f(y0)}" x2="{f(x)}" y2="{f(y1)}"/>',
          f'<line class="tick" x1="{f(x - .8)}" y1="{f(y0 + .8)}" x2="{f(x + .8)}" y2="{f(y0 - .8)}"/>',
          f'<line class="tick" x1="{f(x - .8)}" y1="{f(y1 + .8)}" x2="{f(x + .8)}" y2="{f(y1 - .8)}"/>',
          text(x - 0.9 + dx, ym, label, "ct", extra=f' transform="rotate(-90 {f(x - 0.9 + dx)} {f(ym)})"')]
    return "".join(o)


def chaine_h(xs, y, ext=None):
    """Chaîne de cotes horizontales entre des points triés ; les petites cotes passent sous la ligne, les jeux de
    moins de 1 restent sans chiffre (dits dans la légende)."""
    xs = sorted(xs)
    o, n = [], len(xs) - 1
    for k, (a, b) in enumerate(zip(xs, xs[1:])):
        petit = b - a < 4
        place = ("gauche" if k == 0 else "droite" if k == n - 1 else "") if petit else ""
        o.append(cote_h(a, b, y, label=None if b - a >= 1 else " ", dy=3.4 if petit and not place else 0, ext=ext,
                        place=place))
    return "".join(o)


def chaine_v(ys, x, ext=None):
    ys = sorted(ys)
    o, n = [], len(ys) - 1
    for k, (a, b) in enumerate(zip(ys, ys[1:])):
        petit = b - a < 4
        place = ("haut" if k == 0 else "bas" if k == n - 1 else "") if petit else ""
        o.append(cote_v(a, b, x, label=None if b - a >= 1 else " ", dx=3.4 if petit and not place else 0, ext=ext,
                        place=place))
    return "".join(o)


def niveaux(liste, x, droite=False):
    """Niveaux depuis le sol (▽ 85,5) à gauche (ou à droite) du dessin, reliés à l'élément par un trait fin ;
    liste : (z, texte ou None, x de l'élément). Les textes trop proches s'écartent vers le haut, le triangle reste au
    vrai niveau."""
    t, sens = 1.1, 1 if droite else -1
    o, der = [], None
    for z, label, x_ext in sorted(liste, key=lambda n: n[0]):
        ty = -z if der is None else min(-z, der - 3.0)
        der = ty
        o.append(f'<line class="ext" x1="{f(x)}" y1="{f(-z)}" x2="{f(x_ext)}" y2="{f(-z)}"/>'
                 f'<polygon class="niv" points="{f(x - t)},{f(-z - 2 * t)} {f(x + t)},{f(-z - 2 * t)} {f(x)},{f(-z)}"/>')
        if ty != -z:
            o.append(f'<polyline class="lead" points="{f(x + sens * t)},{f(-z - t)} {f(x + sens * 2)},{f(ty - .9)}"/>')
        o.append(text(x + sens * 2.2, ty, label or cm(z), "nt", "start" if droite else "end"))
    return "".join(o)


def etiquette(x, y, tx, ty, texte, ancre="start"):
    """Repère : trait de rappel du point (x, y) au texte."""
    return (f'<line class="lead" x1="{f(x)}" y1="{f(y)}" x2="{f(tx)}" y2="{f(ty)}"/>'
            f'<circle class="pt" cx="{f(x)}" cy="{f(y)}" r=".45"/>' + text(tx + (0.6 if ancre == "start" else -0.6),
                                                                              ty + 0.9, texte, "lt", ancre))


def svg(x0, y0, x1, y1, corps, titre):
    return (f'<svg class="cotes" viewBox="{f(x0)} {f(y0)} {f(x1 - x0)} {f(y1 - y0)}" role="img" '
            f'aria-label="{escape(titre)}">{"".join(corps)}</svg>')


CSS = """
.omur{fill:#E9EEF0}.omurc{fill:var(--muted);fill-opacity:.55}
.osol{stroke:var(--ink);stroke-width:.6}
.obois{fill:#D29A68;fill-opacity:.45;stroke:var(--ink);stroke-width:.22}
.obois.cut{fill:#D29A68;fill-opacity:1;stroke-width:.3}
.ofac,.omel{fill:var(--cab);stroke:var(--ink);stroke-width:.22}.ofac.cut,.omel.cut{fill:var(--tall);stroke-width:.32}
.oplan{fill:var(--wood);fill-opacity:.5;stroke:var(--ink);stroke-width:.22}.oplan.cut{fill-opacity:1;stroke-width:.3}
.omach{fill:var(--panel);stroke:var(--ink);stroke-width:.3}.omach.cut{fill:#E9EEF0;stroke-width:.4}
.ohub{fill:none;stroke:var(--ink);stroke-width:.3}
.omet,.obar{fill:#B9C2C8;stroke:var(--ink);stroke-width:.2}
.osac{fill:var(--glass);fill-opacity:.25;stroke:var(--water);stroke-width:.25;stroke-dasharray:1 .6}
.otuy{fill:var(--water);fill-opacity:.55;stroke:var(--ink);stroke-width:.2}
.ovanne{fill:var(--water);stroke:var(--ink);stroke-width:.25}
.oprise{fill:var(--panel);stroke:var(--ink);stroke-width:.3}
.oswing{fill:none;stroke:var(--tri);stroke-width:.35;stroke-dasharray:1.4 .8}
.oaxe{fill:var(--tri)}
.ocache{fill:none;stroke:var(--muted);stroke-width:.25;stroke-dasharray:1.2 .8}
.oplanl{fill:none;stroke:var(--wood);stroke-width:.4;stroke-dasharray:1.6 .9}
.ocoin{fill:var(--tri)}
.ochar{fill:#B9C2C8;stroke:var(--ink);stroke-width:.2}
.otrou{fill:var(--paper);stroke:var(--ink);stroke-width:.25}
.odiag{stroke:var(--tri);stroke-width:.25;stroke-dasharray:1.2 .8}
svg.cotes .dim{stroke:var(--ink);stroke-width:.16}
svg.cotes .tick{stroke:var(--ink);stroke-width:.25}
svg.cotes .ext{stroke:var(--muted);stroke-width:.12}
svg.cotes .ct{font:600 2.5px var(--ui);font-variant-numeric:tabular-nums;fill:var(--ink)}
svg.cotes .nt{font:600 2.4px var(--ui);font-variant-numeric:tabular-nums;fill:var(--ink)}
svg.cotes .lt{font-size:2.5px;fill:var(--ink)}svg.cotes .lt.muted{fill:var(--muted)}
svg.cotes .lead{fill:none;stroke:var(--ink);stroke-width:.14}svg.cotes .pt{fill:var(--ink)}
.niv{fill:var(--ink)}
"""
