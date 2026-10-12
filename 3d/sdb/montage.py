# Génère sdb-meuble-v3-montage.html : notice de montage façon IKEA (pièces, quincaillerie, étapes) depuis modele.py.
#
#   python3 3d/sdb/montage.py           (just sdb)
#
# Chaque dessin est une projection isométrique des pièces du modèle : on regarde le meuble depuis la salle de bain,
# en hauteur, un peu du côté sud (le sud est à droite). Les pièces de l'étape sont en couleur, les autres en blanc.

import math
import os
import sys
from collections import Counter
from html import escape

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import modele as M  # noqa: E402
import plan as PL  # noqa: E402

OUT = os.path.join(PL.ROOT, PL.NOTICE)

# ------------------------------------------------------------------ projection
C30, S30 = math.cos(math.radians(30)), math.sin(math.radians(30))
VUE = (-1, 1, 1)        # vers la caméra : ouest, sud, haut


def proj(x, y, z):
    return ((y + x) * C30, -z + (y - x) * S30)


def faces(b):
    """Faces (points 3D, normale) d'une pièce."""
    if isinstance(b, M.Profil):
        pts = b.xz
        aire = sum(x0 * z1 - x1 * z0 for (x0, z0), (x1, z1) in zip(pts, pts[1:] + pts[:1]))
        sgn = 1 if aire > 0 else -1
        r = [([(x, b.y0, z) for x, z in pts], (0, -1, 0)), ([(x, b.y1, z) for x, z in pts], (0, 1, 0))]
        for (x0, z0), (x1, z1) in zip(pts, pts[1:] + pts[:1]):
            n = (sgn * (z1 - z0), 0, -sgn * (x1 - x0))
            r.append(([(x0, b.y0, z0), (x1, b.y0, z1), (x1, b.y1, z1), (x0, b.y1, z0)], n))
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


def dessin(blocs, neuves=(), murs=False, reperes=True, decale=None, extra=None, marge=14, titre=""):
    """Dessin isométrique : blocs dessinés, neuves = noms des pièces de l'étape (en couleur et repérées)."""
    decale = decale or {}
    vis = []
    for b in blocs:
        d = decale.get(b.groupe)
        if d:
            b = M.replace(b, x0=b.x0 + d[0], x1=b.x1 + d[0], y0=b.y0 + d[1], y1=b.y1 + d[1], z0=b.z0 + d[2], z1=b.z1 + d[2]) \
                if isinstance(b, M.Bloc) else M.replace(b, xz=[(x + d[0], z + d[2]) for x, z in b.xz], y0=b.y0 + d[1], y1=b.y1 + d[1])
        vis.append(b)
    o, xs, ys = [], [], []
    if murs:
        sol = [proj(M.X0 - 25, 0, 0), proj(M.X1, 0, 0), proj(M.X1, M.Y1, 0), proj(M.X0 - 25, M.Y1, 0)]
        fond = [proj(M.X1, 0, 0), proj(M.X1, M.Y1, 0), proj(M.X1, M.Y1, M.H), proj(M.X1, 0, M.H)]
        nord = [proj(M.X0, 0, 0), proj(M.X1, 0, 0), proj(M.X1, 0, M.H), proj(M.X0, 0, M.H)]
        for p, cls in ((sol, "isol"), (fond, "imur"), (nord, "imur2")):
            o.append(f'<polygon class="{cls}" points="{pts_svg(p)}"/>')
            xs += [x for x, _ in p]
            ys += [y for _, y in p]
    etiq = {}
    for b in ordre(vis):
        neuve = b.nom in neuves
        cls = "inew" if neuve else ("iapp" if b.role == "machine" else "ipc")
        for f, n in faces(b):
            if sum(a * c for a, c in zip(n, VUE)) <= 1e-6:
                continue
            p = [proj(*q) for q in f]
            xs += [x for x, _ in p]
            ys += [y for _, y in p]
            o.append(f'<polygon class="{cls}" style="--t:{teinte(n):.2f}" points="{pts_svg(p)}"/>')
        if b.role == "machine":
            cy, cz = (b.y0 + b.y1) / 2, b.z0 + 50
            for r in (17, 12.5):
                c = [proj(b.x0 - 0.1, cy + r * math.cos(t / 24 * math.tau), cz + r * math.sin(t / 24 * math.tau)) for t in range(24)]
                o.append(f'<polygon class="ihub" points="{pts_svg(c)}"/>')
        if neuve and reperes and b.rep and b.rep not in etiq:
            cx, cy = proj((b.x0 + b.x1) / 2, (b.y0 + b.y1) / 2, (b.z0 + b.z1) / 2)
            etiq[b.rep] = (cx, cy)
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


# ------------------------------------------------------------------ icônes de quincaillerie
ICONES = {
    "vis": '<path d="M4 12h10M14 9v6h3v-6z M6 10l1 4M8 10l1 4M10 10l1 4M12 10l1 4" />',
    "confirmat": '<path d="M3 12h11M14 8v8h4V8z M5 10l1 4M7 10l1 4M9 10l1 4M11 10l1 4"/>',
    "colle": '<path d="M8 6h8v14H8zM10 6V3h4v3M10 3l2-2 2 2"/>',
    "equerre": '<path d="M5 4v15h15v-4H9V4z"/>',
    "cheville": '<path d="M3 10h14l3 2-3 2H3zM6 10v4M9 10v4M12 10v4"/>',
    "piano": '<path d="M2 8h20v8H2zM2 12h20M6 8v8M10 8v8M14 8v8M18 8v8"/>',
    "compas": '<path d="M4 20L18 6M18 6l2 2M4 20l-2-2M10 14l3 3"/>',
    "poignee": '<path d="M4 14h16M6 14v-4h12v4"/>',
    "taquet": '<path d="M6 10h6v4H6zM12 9h6v6h-6z"/>',
    "rails": '<path d="M2 8h20M2 16h20M5 8v8M19 8v8"/>',
    "led": '<path d="M2 11h20v3H2zM6 12.5h0M10 12.5h0M14 12.5h0M18 12.5h0"/>',
    "silicone": '<path d="M4 8h12v8H4zM16 10h4l2 2-2 2h-4"/>',
    "tapis": '<path d="M3 9l9-4 9 4-9 4zM3 9v3l9 4 9-4V9"/>',
    "sac": '<path d="M6 8h12l-1 12H7zM9 8a3 3 0 0 1 6 0"/>',
}
ICONE = {"vis50": "vis", "vis40": "vis", "vis16": "vis", "confirmat": "confirmat", "colle": "colle",
         "equerre": "equerre", "cheville": "cheville", "piano": "piano", "compas": "compas", "poignee": "poignee",
         "taquet": "taquet", "rails": "rails", "led": "led", "silicone": "silicone", "tapis": "tapis", "sac": "sac"}


def icone(code):
    return f'<svg class="ico" viewBox="0 0 24 24" aria-hidden="true">{ICONES[ICONE[code]]}</svg>'


def puces_quinc(q):
    return "".join(f'<div class="hw">{icone(k)}<b>{n}×</b><span>{escape(M.QUINCAILLERIE[k])}</span></div>'
                   for k, n in q.items())


# ------------------------------------------------------------------ étapes
SEUL = {1: ["socle"], 2: ["caisson_bas"], 3: ["caisson_bas"], 5: ["bac1"], 6: ["bac1"], 9: ["caisson_haut"]}
FOIS = {5: 2, 6: 2}     # le dessin montre un exemplaire : « × 2 »


def pieces_etape(c, n):
    return [b for b in M.version(c) if b.etape == n and b.role not in ("prise",)]


def dessin_etape(c, n):
    tout = M.version(c)
    neuves = {b.nom for b in pieces_etape(c, n)}
    if n in SEUL:
        gr = SEUL[n]
        bl = [b for b in tout if b.groupe in gr and b.etape <= n and b.role != "led"]
        return dessin(bl, neuves, titre=f"Étape {n}")
    bl = [b for b in tout if 0 < b.etape <= n and b.role != "prise"]
    if n == M.POSE_HAUT:
        neuves = {b.nom for b in tout if b.groupe == "caisson_haut" and b.etape <= n}

        def cales(xs, ys):     # deux cales de la hauteur de la niche, sous le caisson haut
            r = []
            for y in (12, M.Y1 - 22):
                cale = M.Bloc("cale", "cale", M.CH["x0"] + 8, M.CH["x0"] + 18, y, y + 10, M.Z_DESSUS, M.Z_HAUT)
                for f, nn in faces(cale):
                    if sum(a * b for a, b in zip(nn, VUE)) > 0:
                        p = [proj(*q) for q in f]
                        r.append(f'<polygon class="ical" points="{pts_svg(p)}"/>')
            return r
        return dessin(bl, neuves, murs=True, reperes=False, extra=cales, titre=f"Étape {n}")
    if n == 0:
        def reseaux(xs, ys):
            r = []
            rb = M.ROBINET
            p = proj(M.X1, rb["y"], rb["z"])
            r.append(f'<circle class="ival" cx="{p[0]:.1f}" cy="{p[1]:.1f}" r="3"/>')
            r.append(f'<text class="ilbl" x="{p[0] + 4:.1f}" y="{p[1] + 1.5:.1f}">robinet h {rb["z"]}</text>')
            pr = M.PRISES
            for y in (pr.y0, pr.y0 + 7):
                q = proj(M.X1, y + 3, (pr.z0 + pr.z1) / 2)
                r.append(f'<rect class="iplug" x="{q[0] - 2.5:.1f}" y="{q[1] - 3:.1f}" width="5" height="6" rx="1"/>')
            q = proj(M.X1, pr.y0 + 14, (pr.z0 + pr.z1) / 2)
            r.append(f'<text class="ilbl" x="{q[0] + 3:.1f}" y="{q[1] + 1.5:.1f}">prises niche h {(pr.z0 + pr.z1) / 2:g}</text>')
            ll = [b for b in M.version(c) if b.role == "machine"][0]
            q = proj(M.X1, (ll.y0 + ll.y1) / 2 + 12, 60)
            r.append(f'<rect class="iplug" x="{q[0] - 2.5:.1f}" y="{q[1] - 3:.1f}" width="5" height="6" rx="1"/>')
            r.append(f'<text class="ilbl" x="{q[0] + 4:.1f}" y="{q[1] + 1.5:.1f}">prise LL (20 A)</text>')
            return r
        return dessin([], murs=True, extra=reseaux, titre="Avant de commencer")
    return dessin(bl, neuves, murs=n >= 4, titre=f"Étape {n}")


def profil_bac():
    """Petit schéma de côté : bac du bas fermé et basculé, axe de la charnière, compas."""
    c = "d"
    blocs = [b for b in M.version(c) if b.groupe == "bac1" and b.rep in ("B1", "A6")]
    caisson = [b for b in M.version(c) if b.nom in ("cb_dessous", "cb_tablette", "cb_cote_n")]
    axe = M.BAC["axe1"]
    o = []
    for b in caisson:
        o.append(PL.poly([(u, -z) for u, z in b.pts("y")], "cab"))
    for b in blocs:
        o.append(PL.poly([(u, -z) for u, z in b.pts("y")], "bac" if b.rep == "B1" else "fac"))
        p = [M.bascule(x, z, axe, M.BAC["angle"]) for x, z in b.pts("y")]
        o.append(PL.poly([(x, -z) for x, z in p], "swingp"))
    o.append(f'<circle class="axe" cx="{axe[0]}" cy="{-axe[1]:.2f}" r="1"/>')
    a = M.bascule(M.FACE, M.FACADES[0][1], axe, M.BAC["angle"])
    o.append(f'<path class="lead" d="M{M.FACE} {-M.FACADES[0][1]:.1f} A{M.FACADES[0][1] - axe[1]:.1f} '
             f'{M.FACADES[0][1] - axe[1]:.1f} 0 0 0 {a[0]:.1f} {-a[1]:.1f}"/>')
    o.append(PL.text(a[0] - 1, -a[1] - 2, f"{M.BAC['angle']}°", "lbls", "end"))
    o.append(PL.text(axe[0] + 2, -axe[1] + 5, "charnière piano", "lblx", "start"))
    x0, x1 = M.FACE - 30, M.CB["x1"] + 2
    return (f'<svg viewBox="{x0} {-(M.CASES[0][1] + 6):.1f} {x1 - x0} {M.CASES[0][1] + 14:.1f}" role="img" '
            f'aria-label="Bac basculé, vu de côté">{"".join(o)}</svg>')


def puces_pieces(c, n):
    cpt = Counter(b.rep for b in pieces_etape(c, n) if b.rep)
    if "E2" in cpt:
        cpt["E2"] = 1           # une cornière, modélisée en deux ailes
    r = "".join(f'<span class="pc"><b>{r}</b> × {q}</span>' for r, q in sorted(cpt.items(), key=lambda t: (t[0][0], int(t[0][1:]))))
    return r + (f'<span class="pc muted">dessin : 1 bac sur {FOIS[n]}</span>' if n in FOIS else "")


def bloc_etape(n):
    titre, texte, q = M.ETAPES[n]
    par_cote = n not in SEUL
    if par_cote:
        fig = f'<div class="vd">{dessin_etape("d", n)}</div><div class="vg">{dessin_etape("g", n)}</div>'
    else:
        fig = dessin_etape("d", n)
    fois = f'<div class="fois">× {FOIS[n]}</div>' if n in FOIS else ""
    extra = f'<div class="mini">{profil_bac()}</div>' if n == 6 else ""
    pcs = puces_pieces("d", n)
    return f"""<section class="etape" id="etape-{n}">
<div class="num">{n}</div>
<div class="ecorps">
<h2>{escape(titre)}</h2>
<div class="pcs">{pcs}</div>
<div class="hws">{puces_quinc(q)}</div>
<div class="edessin">{fig}{fois}{extra}</div>
<p class="consigne">{escape(texte)}</p>
</div>
</section>"""


# ------------------------------------------------------------------ pages d'ouverture : pièces, outils, vue éclatée
def carte_piece(p):
    b = next(b for b in M.PIECES if b.rep == p["rep"])
    # pièce seule, à plat contre l'origine
    if isinstance(b, M.Profil):
        bb = M.replace(b, xz=[(x - b.x0, z - b.z0) for x, z in b.xz], y0=0, y1=b.y1 - b.y0)
    else:
        bb = M.replace(b, x0=0, x1=b.x1 - b.x0, y0=0, y1=b.y1 - b.y0, z0=0, z1=b.z1 - b.z0, encoche=())
    svg = dessin([bb], {bb.nom}, reperes=False, marge=3, titre=p["nom"])
    sec = f'{p["l"]} × {p["e"]}'
    return (f'<div class="carte"><div class="cdes">{svg}</div><div class="cpied"><b class="crep">{p["rep"]}</b>'
            f'<span class="cq">{p["q"]}×</span></div><div class="cnom">{escape(p["nom"])}</div>'
            f'<div class="cdim mono">{p["L"]} × {sec}</div></div>')


def vue_eclatee(c):
    s = 1 if c == "d" else -1
    decale = {"socle": (-30, 0, 0), "bac1": (-75, 0, 0), "bac2": (-75, 0, 8), "plan": (0, 0, 48),
              "caisson_haut": (0, 0, 85), "machine": (-30, 0, 22), "supports": (0, 0, 24)}
    tout = [b for b in M.version(c) if b.role not in ("prise", "led")]
    return dessin(tout, decale=decale, reperes=False, titre="Vue éclatée")


def vue_ensemble(c):
    tout = [b for b in M.version(c) if b.role not in ("prise",)]
    return dessin(tout, murs=True, reperes=False, titre="Meuble monté")


CSS = PL.CSS + """
.isol{fill:var(--line);fill-opacity:.25}
.imur{fill:var(--line);fill-opacity:.35;stroke:var(--muted);stroke-width:.25}
.imur2{fill:var(--line);fill-opacity:.18;stroke:var(--muted);stroke-width:.25}
.ipc{fill:hsl(40 15% calc(var(--t) * 100% - 4%));stroke:var(--ink);stroke-width:.32;stroke-linejoin:round}
.inew{fill:hsl(32 80% calc(var(--t) * 72% + 8%));stroke:var(--ink);stroke-width:.4;stroke-linejoin:round}
.iapp{fill:hsl(200 10% calc(var(--t) * 100% - 2%));stroke:var(--ink);stroke-width:.35}
.ihub{fill:none;stroke:var(--ink);stroke-width:.35}
.ical{fill:var(--tri);fill-opacity:.35;stroke:var(--tri);stroke-width:.3}
.ilead{stroke:var(--ink);stroke-width:.3}
.ibul{fill:var(--panel);stroke:var(--ink);stroke-width:.45}
.ibt{font:700 4.4px "JetBrains Mono",ui-monospace,monospace;fill:var(--ink)}
.ilbl{font-size:7px;fill:var(--ink)}
.ival{fill:var(--water);stroke:var(--ink);stroke-width:.3}
.iplug{fill:var(--panel);stroke:var(--ink);stroke-width:.4}
.etape{display:grid;grid-template-columns:76px 1fr;gap:12px;border-top:2px solid var(--ink);padding:18px 0 26px;margin-top:10px}
.etape .num{font:800 56px/1 Archivo,system-ui,sans-serif;letter-spacing:-.03em}
.etape h2{margin:4px 0 8px;font-size:20px}
.ecorps{min-width:0}
.edessin{position:relative;background:var(--panel);border:1px solid var(--line);border-radius:12px;padding:10px;margin:10px 0}
.edessin svg{display:block;width:100%;height:auto;max-height:62vh}
.edessin .mini{border-top:1px dashed var(--line);margin-top:8px;padding-top:8px}
.edessin .mini svg{max-height:34vh}
.fois{position:absolute;right:16px;top:12px;font:800 30px Archivo,system-ui,sans-serif}
.consigne{max-width:760px;margin:6px 0 0}
.pcs,.hws{display:flex;flex-wrap:wrap;gap:6px;margin:4px 0}
.pc{font:12px "JetBrains Mono",ui-monospace,monospace;border:1px solid var(--line);border-radius:999px;padding:2px 10px;background:var(--panel)}
.pc.muted{color:var(--muted)}
.hw{display:flex;align-items:center;gap:6px;font-size:13px;border:1px solid var(--line);border-radius:8px;padding:3px 10px 3px 4px;background:var(--panel)}
.hw b{font-family:"JetBrains Mono",ui-monospace,monospace}
.hw span{color:var(--muted)}
.ico{width:26px;height:26px;fill:none;stroke:var(--ink);stroke-width:1.3;stroke-linecap:round;stroke-linejoin:round}
.cartes{display:grid;grid-template-columns:repeat(auto-fill,minmax(150px,1fr));gap:10px}
.carte{background:var(--panel);border:1px solid var(--line);border-radius:10px;padding:8px;display:flex;flex-direction:column}
.cdes{height:96px;display:flex;align-items:center;justify-content:center}
.cdes svg{max-width:100%;max-height:96px;width:auto;height:96px}
.cpied{display:flex;justify-content:space-between;align-items:baseline;margin-top:6px}
.crep{font:800 18px "JetBrains Mono",ui-monospace,monospace}
.cq{font:700 15px "JetBrains Mono",ui-monospace,monospace}
.cnom{font-size:12.5px;line-height:1.3}
.cdim{font-size:11.5px;color:var(--muted)}
.outils{display:flex;flex-wrap:wrap;gap:8px;padding:0;list-style:none}
.outils li{border:1px solid var(--line);border-radius:8px;padding:4px 10px;background:var(--panel);font-size:14px}
.deux{display:grid;grid-template-columns:repeat(auto-fit,minmax(320px,1fr));gap:14px}
.deux .fig svg{display:block;width:100%;height:auto;max-height:70vh}
@media (max-width:560px){ .etape{grid-template-columns:1fr} .etape .num{font-size:40px} }
"""

OUTILS = ["perceuse-visseuse", "foret Ø 5 et gabarit à taquets", "mèche à confirmat", "scie sauteuse (encoche du plan)",
          "niveau à bulle", "mètre", "serre-joints", "pistolet à silicone", "deux personnes pour la machine et le caisson haut"]


def contenu():
    deb = PL.debit()
    cartes = "".join(carte_piece(p) for p in deb)
    etapes = "".join(bloc_etape(n) for n in range(len(M.ETAPES)))
    return f"""<div class="kicker">Salle de bain · meuble linge {M.VERSION} · notice de montage</div>
<h1>Notice de montage</h1>
<p class="pitch">{len(M.ETAPES) - 1} étapes, du socle de la machine au caisson haut. Dans chaque dessin, les pièces de l'étape sont en orange avec leur repère ; celles déjà posées sont en blanc. Le bouton <b>Machine</b> retourne les dessins de pose (machine à droite ou à gauche) ; les pièces sont les mêmes dans les deux versions.</p>

<h2>Le meuble</h2>
<div class="deux">
<div class="fig"><div class="vd">{vue_ensemble("d")}</div><div class="vg">{vue_ensemble("g")}</div><p class="note">Meuble monté, vu depuis la salle de bain.</p></div>
<div class="fig"><div class="vd">{vue_eclatee("d")}</div><div class="vg">{vue_eclatee("g")}</div><p class="note">Vue éclatée : socle, caisson bas, deux bacs, supports et plan, caisson haut.</p></div>
</div>

<h2>Pièces</h2>
<div class="cartes">{cartes}</div>
<p class="note">Cotes en mm (longueur × largeur × épaisseur). Liste complète avec usinages : <a href="{os.path.basename(PL.OUT)}#debit">page des plans, Débit</a>.</p>

<h2>Quincaillerie</h2>
<div class="hws">{puces_quinc(sum((Counter(q) for _, _, q in M.ETAPES), Counter()))}</div>

<h2>Outils</h2>
<ul class="outils">{"".join(f"<li>{escape(o)}</li>" for o in OUTILS)}</ul>

{etapes}

<p class="note">Notice générée depuis <span class="mono">3d/sdb/modele.py</span> par <span class="mono">3d/sdb/montage.py</span> (<span class="mono">just sdb</span>).</p>
"""


def page():
    return f"""{PL.entete("Notice meuble linge", "", CSS)}
<body>
{PL.barre("", notice=False)}
<nav class="toc" aria-label="Sommaire"><button type="button" class="tbtn" aria-expanded="true">Sommaire</button><ol></ol></nav>
<main class="wrap">
<div class="ver" data-v="courante">{contenu()}</div>
</main>
<script>{PL.SCRIPT % {"cle": PL.CLE}}</script>
</body>
</html>
"""


if __name__ == "__main__":
    with open(OUT, "w", encoding="utf-8") as fh:
        fh.write(page())
    print(OUT)
