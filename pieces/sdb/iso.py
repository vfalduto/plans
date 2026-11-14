"""Vue isométrique, partagée par les deux meubles de la salle de bain.

Copie, à l'octet, de la projection de 3d/sdb/montage.py (proj … dessin) : on regarde le meuble depuis la salle de bain,
en hauteur, un peu du côté sud. Les pièces sont lues par leurs attributs (un profil a `xz`, un prisme `xy`, un bloc
ses six bornes), pas par leur classe : celles du meuble bas (pieces/sdb/meuble_bas/modele.py) et celles de
3d/sdb/modele.py (meuble haut, encore en passerelle) passent toutes. Les murs viennent de pieces/sdb/piece.py.
"""
import math
from dataclasses import replace
from html import escape

from pieces.sdb import piece as P


# ------------------------------------------------------------------ projection
C30, S30 = math.cos(math.radians(30)), math.sin(math.radians(30))
VUE = (-1, 1, 1)        # vers la caméra : ouest, sud, haut


def proj(x, y, z):
    return ((y + x) * C30, -z + (y - x) * S30)


def faces(b):
    """Faces (points 3D, normale) d'une pièce."""
    if hasattr(b, "xz"):            # profil : contour dans le plan x-z, extrudé le long de y
        pts = b.xz
        aire = sum(x0 * z1 - x1 * z0 for (x0, z0), (x1, z1) in zip(pts, pts[1:] + pts[:1]))
        sgn = 1 if aire > 0 else -1
        r = [([(x, b.y0, z) for x, z in pts], (0, -1, 0)), ([(x, b.y1, z) for x, z in pts], (0, 1, 0))]
        for (x0, z0), (x1, z1) in zip(pts, pts[1:] + pts[:1]):
            n = (sgn * (z1 - z0), 0, -sgn * (x1 - x0))
            r.append(([(x0, b.y0, z0), (x1, b.y0, z1), (x1, b.y1, z1), (x0, b.y1, z0)], n))
        return r
    if hasattr(b, "xy"):            # prisme : contour dans le plan x-y, extrudé le long de z
        pts = b.xy
        aire = sum(x0 * y1 - x1 * y0 for (x0, y0), (x1, y1) in zip(pts, pts[1:] + pts[:1]))
        sgn = 1 if aire > 0 else -1
        r = [([(x, y, b.z1) for x, y in pts], (0, 0, 1)), ([(x, y, b.z0) for x, y in pts], (0, 0, -1))]
        for (x0, y0), (x1, y1) in zip(pts, pts[1:] + pts[:1]):
            r.append(([(x0, y0, b.z0), (x1, y1, b.z0), (x1, y1, b.z1), (x0, y0, b.z1)], (sgn * (y1 - y0), -sgn * (x1 - x0), 0)))
        return r
    x0, x1, y0, y1, z0, z1 = b.x0, b.x1, b.y0, b.y1, b.z0, b.z1
    return [
        ([(x0, y0, z1), (x1, y0, z1), (x1, y1, z1), (x0, y1, z1)], (0, 0, 1)),
        ([(x0, y0, z0), (x0, y1, z0), (x0, y1, z1), (x0, y0, z1)], (-1, 0, 0)),
        ([(x0, y1, z0), (x1, y1, z0), (x1, y1, z1), (x0, y1, z1)], (0, 1, 0)),
        ([(x0, y0, z0), (x1, y0, z0), (x1, y1, z0), (x0, y1, z0)], (0, 0, -1)),
        ([(x1, y0, z0), (x1, y1, z0), (x1, y1, z1), (x1, y0, z1)], (1, 0, 0)),
        ([(x0, y0, z0), (x1, y0, z0), (x1, y0, z1), (x0, y0, z1)], (0, -1, 0)),
    ]


def ecran(b):
    pts = [proj(*p) for f, _ in faces(b) for p in f]
    return (min(p[0] for p in pts), min(p[1] for p in pts), max(p[0] for p in pts), max(p[1] for p in pts))


def devant(a, b):
    """True si a cache b (a plus près de la caméra), False si l'inverse, None si on ne peut pas trancher."""
    e = 0.01
    if a.x1 <= b.x0 + e:
        return True
    if b.x1 <= a.x0 + e:
        return False
    if a.y0 >= b.y1 - e:
        return True
    if b.y0 >= a.y1 - e:
        return False
    if a.z0 >= b.z1 - e:
        return True
    if b.z0 >= a.z1 - e:
        return False
    return None


def profondeur(b):
    return -(b.x0 + b.x1) / 2 + (b.y0 + b.y1) / 2 + (b.z0 + b.z1) / 2


def ordre(blocs):
    """Tri topologique du plus loin au plus près (algorithme du peintre pour des pièces disjointes)."""
    n = len(blocs)
    ec = [ecran(b) for b in blocs]
    avant = {i: set() for i in range(n)}     # avant[i] : pièces à dessiner avant i
    for i in range(n):
        for j in range(i + 1, n):
            a, b = ec[i], ec[j]
            if a[2] <= b[0] or b[2] <= a[0] or a[3] <= b[1] or b[3] <= a[1]:
                continue
            d = devant(blocs[i], blocs[j])
            if d is None:
                d = (blocs[i].role == "trappe") or (blocs[j].role != "trappe" and profondeur(blocs[i]) > profondeur(blocs[j]))
            (avant[i] if d else avant[j]).add(j if d else i)
    reste, r = set(range(n)), []
    while reste:
        libres = [i for i in reste if not (avant[i] & reste)]
        if not libres:      # cycle : on prend la plus éloignée
            libres = [min(reste, key=lambda i: profondeur(blocs[i]))]
        for i in sorted(libres, key=lambda i: profondeur(blocs[i])):
            r.append(i)
            reste.discard(i)
    return [blocs[i] for i in r]


def teinte(n):
    """Ombrage d'une face selon sa normale : dessus clair, face avant moyen, côté sud plus sombre."""
    l = math.sqrt(sum(c * c for c in n)) or 1
    nx, ny, nz = (c / l for c in n)
    return 0.55 + 0.45 * max(0, nz) + 0.3 * max(0, -nx) + 0.12 * max(0, ny)


def pts_svg(pts):
    return " ".join(f"{x:.2f},{y:.2f}" for x, y in pts)


def dessin(blocs, neuves=(), murs=False, reperes=True, decale=None, extra=None, marge=14, titre="", trous=(),
           carrelage=None):
    """Dessin isométrique : blocs dessinés, neuves = noms des pièces de l'étape (en couleur et repérées), trous = perçages
    de l'étape (dessinés sur la face par où on perce, quand elle est tournée vers nous). V6.0 : avec les murs, carrelage
    = hauteur du carrelage, dessiné en bande sur les murs du fond et nord, sous les pièces."""
    decale = decale or {}
    vis = []
    for b in blocs:
        d = decale.get(b.groupe)
        if d:
            b = replace(b, xz=[(x + d[0], z + d[2]) for x, z in b.xz], y0=b.y0 + d[1], y1=b.y1 + d[1]) \
                if hasattr(b, "xz") else replace(b, x0=b.x0 + d[0], x1=b.x1 + d[0], y0=b.y0 + d[1], y1=b.y1 + d[1],
                                                 z0=b.z0 + d[2], z1=b.z1 + d[2])
        vis.append(b)
    o, xs, ys = [], [], []
    if murs:
        sol = [proj(P.X0 - 25, 0, 0), proj(P.X1, 0, 0), proj(P.X1, P.Y1, 0), proj(P.X0 - 25, P.Y1, 0)]
        fond = [proj(P.X1, 0, 0), proj(P.X1, P.Y1, 0), proj(P.X1, P.Y1, P.H), proj(P.X1, 0, P.H)]
        nord = [proj(P.X0, 0, 0), proj(P.X1, 0, 0), proj(P.X1, 0, P.H), proj(P.X0, 0, P.H)]
        for p, cls in ((sol, "isol"), (fond, "imur"), (nord, "imur2")):
            o.append(f'<polygon class="{cls}" points="{pts_svg(p)}"/>')
            xs += [x for x, _ in p]
            ys += [y for _, y in p]
        if carrelage:
            cz = min(carrelage, P.H)
            bandes = ([proj(P.X1, 0, 0), proj(P.X1, P.Y1, 0), proj(P.X1, P.Y1, cz), proj(P.X1, 0, cz)],
                      [proj(P.X0, 0, 0), proj(P.X1, 0, 0), proj(P.X1, 0, cz), proj(P.X0, 0, cz)])
            for p in bandes:
                o.append(f'<polygon class="icarr" points="{pts_svg(p)}"/>')
            haut = [proj(P.X0, 0, cz), proj(P.X1, 0, cz), proj(P.X1, P.Y1, cz)]
            o.append(f'<polyline class="icarrl" points="{pts_svg(haut)}"/>')
            tx, ty = proj(P.X0, 0, cz)          # libellé à gauche du mur nord, au niveau du haut du carrelage
            libelle = (f'<line class="icarrl" x1="{tx - 4:.1f}" y1="{ty:.1f}" x2="{tx:.1f}" y2="{ty:.1f}"/>'
                       f'<text class="icarrt" x="{tx - 5:.1f}" y="{ty + 2.4:.1f}" text-anchor="end">carrelage {carrelage}</text>')
            xs.append(tx - 5 - 4.2 * len(f"carrelage {carrelage}"))
    else:
        carrelage = None
    etiq = {}
    par_piece = {}
    for t in trous:
        if sum(a * c for a, c in zip(t["n"], VUE)) > 1e-6:
            par_piece.setdefault(t["a"], []).append(t)
    k_t = max(1, (max(proj(*p)[1] for b in vis for f, _ in faces(b) for p in f) -
                  min(proj(*p)[1] for b in vis for f, _ in faces(b) for p in f)) / 120) if vis else 1
    for b in ordre(vis):
        neuve = b.nom in neuves
        cls = ("isac" if b.role == "sac" else "itu" if b.role == "tuyau" else "inew" if neuve else
               ("iapp" if b.role == "machine" else "imel" if b.role == "melamine" else "ibois" if b.role == "chene" else "ipc"))
        for f, n in faces(b):
            if sum(a * c for a, c in zip(n, VUE)) <= 1e-6:
                continue
            p = [proj(*q) for q in f]
            xs += [x for x, _ in p]
            ys += [y for _, y in p]
            o.append(f'<polygon class="{cls}" style="--t:{teinte(n):.2f}" points="{pts_svg(p)}"/>')
        for cl, c in getattr(b, "decor", ()):                        # plaques et trous posés sur une face : (classe, points 3D)
            o.append(f'<polygon class="{cl}" points="{pts_svg([proj(*q) for q in c])}"/>')
        for c in getattr(b, "fenetres", ()):                         # découpes d'une porte : contours (y, z) sur sa face ouest
            o.append(f'<polygon class="ifen" points="{pts_svg([proj(b.x0, y, z) for y, z in c])}"/>')
        encoche, entailles = getattr(b, "encoche", ()), getattr(b, "entailles", ())
        if not hasattr(b, "xz") and not hasattr(b, "xy") and (encoche or entailles):   # encoche, entailles : sur le dessus
            for x0, x1, y0, y1 in ((encoche,) if encoche else ()) + tuple(entailles):
                p = [proj(x0, y0, b.z1), proj(x1, y0, b.z1), proj(x1, y1, b.z1), proj(x0, y1, b.z1)]
                o.append(f'<polygon class="ihole" points="{pts_svg(p)}"/>')
        for t in par_piece.get(b.nom, ()):
            cx, cy = proj(t["x"], t["y"], t["z"])
            cls = "itr2" if t["vis"] in ("cuvette", "cheville") else "itr"
            o.append(f'<circle class="{cls}" cx="{cx:.2f}" cy="{cy:.2f}" r="{(1.6 if cls == "itr2" else .75) * k_t:.2f}" '
                     f'style="stroke-width:{.3 * k_t:.2f}"/>')
        if b.role == "machine":
            cy, cz = (b.y0 + b.y1) / 2, b.z0 + 50
            for r in (17, 12.5):
                c = [proj(b.x0 - 0.1, cy + r * math.cos(t / 24 * math.tau), cz + r * math.sin(t / 24 * math.tau)) for t in range(24)]
                o.append(f'<polygon class="ihub" points="{pts_svg(c)}"/>')
        if neuve and reperes and b.rep and b.rep not in etiq:
            cx, cy = proj((b.x0 + b.x1) / 2, (b.y0 + b.y1) / 2, (b.z0 + b.z1) / 2)
            etiq[b.rep] = (cx, cy)
    if carrelage:
        o.append(libelle)
    if extra:
        o += extra(xs, ys)
    if not xs:
        return ""
    # repères : bulles décalées vers le haut à gauche, reliées à la pièce
    k_ = max(1, (max(ys) - min(ys)) / 120)     # grands dessins : bulles plus grosses pour rester lisibles
    for k, (rep, (cx, cy)) in enumerate(sorted(etiq.items(), key=lambda t: t[1][0])):
        bx, by = cx - (10 + (k % 2) * 8) * k_, cy - (14 + (k % 3) * 9) * k_
        o.append(f'<line class="ilead" x1="{cx:.1f}" y1="{cy:.1f}" x2="{bx:.1f}" y2="{by:.1f}"/>'
                 f'<circle class="ibul" cx="{bx:.1f}" cy="{by:.1f}" r="{4.6 * k_:.1f}" style="stroke-width:{.45 * k_:.2f}"/>'
                 f'<text class="ibt" x="{bx:.1f}" y="{by + 1.7 * k_:.1f}" text-anchor="middle" '
                 f'style="font-size:{4.4 * k_:.1f}px">{rep}</text>')
        xs += [bx - 5 * k_]
        ys += [by - 5 * k_]
    x0, y0, x1, y1 = min(xs) - marge, min(ys) - marge, max(xs) + marge, max(ys) + marge
    return (f'<svg viewBox="{x0:.1f} {y0:.1f} {x1 - x0:.1f} {y1 - y0:.1f}" role="img" aria-label="{escape(titre)}">'
            f'{"".join(o)}</svg>')


CSS = """
.isol{fill:var(--line);fill-opacity:.25}
.imur{fill:var(--line);fill-opacity:.35;stroke:var(--muted);stroke-width:.25}
.imur2{fill:var(--line);fill-opacity:.18;stroke:var(--muted);stroke-width:.25}
.icarr{fill:var(--water);fill-opacity:.12;stroke:none}
.icarrl{fill:none;stroke:var(--water);stroke-width:.5;stroke-dasharray:2 1.2}
.icarrt{font-size:7px;font-weight:600;fill:var(--water)}
.itu{fill:var(--water);fill-opacity:.75;stroke:var(--ink);stroke-width:.3}
.ipc{fill:hsl(40 15% calc(var(--t) * 100% - 4%));stroke:var(--ink);stroke-width:.32;stroke-linejoin:round}
.inew{fill:hsl(32 80% calc(var(--t) * 72% + 8%));stroke:var(--ink);stroke-width:.4;stroke-linejoin:round}
.isac{fill:hsl(205 60% calc(var(--t) * 40% + 55%));fill-opacity:.8;stroke:var(--water);stroke-width:.35;stroke-dasharray:1.2 .8}
.ifen{fill:var(--ink);fill-opacity:.62;stroke:var(--ink);stroke-width:.3}
.idec{fill:#fbfaf5;stroke:var(--ink);stroke-width:.3}
.imel{fill:hsl(45 14% calc(var(--t) * 28% + 70%));stroke:var(--ink);stroke-width:.32;stroke-linejoin:round}
.ibois{fill:hsl(32 45% calc(var(--t) * 50% + 25%));stroke:var(--ink);stroke-width:.32;stroke-linejoin:round}
.iapp{fill:hsl(200 10% calc(var(--t) * 100% - 2%));stroke:var(--ink);stroke-width:.35}
.ihub{fill:none;stroke:var(--ink);stroke-width:.35}
.ical{fill:var(--tri);fill-opacity:.35;stroke:var(--tri);stroke-width:.3}
.ilead{stroke:var(--ink);stroke-width:.3}
.ibul{fill:var(--panel);stroke:var(--ink);stroke-width:.45}
.ibt{font:700 4.4px var(--ui);font-variant-numeric:tabular-nums;fill:var(--ink)}
.ilbl{font-size:7px;fill:var(--ink)}
.ival{fill:var(--water);stroke:var(--ink);stroke-width:.3}
.iplug{fill:var(--panel);stroke:var(--ink);stroke-width:.4}
.itr{fill:var(--ink);stroke:var(--panel)}
.ihole{fill:var(--paper);stroke:var(--ink);stroke-width:.3}
.itr2{fill:var(--panel);stroke:var(--ink)}
"""
