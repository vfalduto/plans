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


def dessin(blocs, neuves=(), murs=False, reperes=True, decale=None, extra=None, marge=14, titre="", trous=()):
    """Dessin isométrique : blocs dessinés, neuves = noms des pièces de l'étape (en couleur et repérées), trous = perçages
    de l'étape (dessinés sur la face par où on perce, quand elle est tournée vers nous)."""
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
    par_piece = {}
    for t in trous:
        if sum(a * c for a, c in zip(t["n"], VUE)) > 1e-6:
            par_piece.setdefault(t["a"], []).append(t)
    k_t = max(1, (max(proj(*p)[1] for b in vis for f, _ in faces(b) for p in f) -
                  min(proj(*p)[1] for b in vis for f, _ in faces(b) for p in f)) / 120) if vis else 1
    for b in ordre(vis):
        neuve = b.nom in neuves
        cls = "isac" if b.role == "sac" else "inew" if neuve else ("iapp" if b.role == "machine" else "ipc")
        for f, n in faces(b):
            if sum(a * c for a, c in zip(n, VUE)) <= 1e-6:
                continue
            p = [proj(*q) for q in f]
            xs += [x for x, _ in p]
            ys += [y for _, y in p]
            o.append(f'<polygon class="{cls}" style="--t:{teinte(n):.2f}" points="{pts_svg(p)}"/>')
        if isinstance(b, M.Bloc) and (b.encoche or b.entailles):     # trou de trappe, entailles : sur le dessus
            for x0, x1, y0, y1 in ((b.encoche,) if b.encoche else ()) + tuple(b.entailles):
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
    "sac": '<path d="M4 7h16M7 7l2 13h6l2-13"/>',
    "chant": '<path d="M4 14a5 5 0 1 1 10 0a5 5 0 1 1-10 0M14 14h7M9 14h0"/>',
    "charniere": '<path d="M3 6h7v12H3zM10 10h5v4h-5M15 9h6v6h-6z"/><circle cx="6.5" cy="12" r="2.2"/>',
    "plate": '<path d="M4 4h6v10h10v6H4z"/>',
    "pinceau": '<path d="M9 3h6v8H9zM8 11h8l-1 4H9zM12 15v6"/>',
    "foret": '<path d="M3 12h4M7 10h4v4H7zM11 12h10M13 10l2 4M17 10l2 4"/>',
}
ICONE = {"vis50": "vis", "vis40": "vis", "vis16": "vis", "confirmat": "confirmat", "colle": "colle",
         "equerre": "equerre", "cheville": "cheville", "piano": "piano", "compas": "compas", "poignee": "poignee", "vis30": "vis",
         "taquet": "taquet", "rails": "rails", "led": "led", "silicone": "silicone", "tapis": "tapis", "sac": "sac", "toile": "sac",
         "chant": "chant", "vis60": "vis", "vis50": "vis", "equerre_r": "equerre", "equerre_p": "plate", "charniere": "charniere",
         "vernis": "pinceau", "forstner": "foret", "equerre_a": "equerre", "charniere_p": "piano", "crochet": "poignee",
         "elastique": "sac", "peinture": "pinceau", "patins": "taquet", "fraise": "foret", "verin": "taquet", "insert": "vis", "tirefond": "vis", "mousse": "taquet"}


def icone(code):
    return f'<svg class="ico" viewBox="0 0 24 24" aria-hidden="true">{ICONES[ICONE[code]]}</svg>'


def puces_quinc(q):
    return "".join(f'<div class="hw">{icone(k)}<b>{n}×</b><span>{escape(M.QUINCAILLERIE[k])}</span></div>'
                   for k, n in q.items())


# ------------------------------------------------------------------ étapes
SEUL = {1: ["ossature"], 3: ["bac"], 8: ["caisson_haut"]}
FOIS = {1: 3}           # le dessin montre un exemplaire : « × 3 »


def pieces_etape(c, n):
    return [b for b in M.version(c) if b.etape == n and b.role not in ("prise",)]


def dessin_etape(c, n):
    tout = M.version(c)
    neuves = {b.nom for b in pieces_etape(c, n)}
    if n in SEUL:
        gr = SEUL[n]
        bl = [b for b in tout if b.groupe in gr and b.etape <= n and b.role != "led"]
        if n == 1:          # une échelle sur trois, à plat comme on l'assemble
            bl = [b for b in bl if b.nom.endswith("_n")]
        if n == 3:          # le L seul
            bl = [b for b in bl if b.role != "sac"]
        return dessin(bl, neuves, titre=f"Étape {n}", trous=trous_etape(n, bl))
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
    return dessin(bl, neuves, murs=n >= 4, titre=f"Étape {n}", trous=trous_etape(n, bl))


def trous_etape(n, bl):
    noms = {b.nom for b in bl}
    return [t for t in M.TROUS if t["etape"] == n and t["a"] in noms]


def table_percages(n):
    """Perçages de l'étape, regroupés par assemblage : où, combien, forets, vis, position."""
    grp = {}
    for t in M.TROUS:
        if t["etape"] == n:
            g = grp.setdefault((t["ra"], t["rb"], t["vis"]), dict(q=0, pos=t["pos"]))
            g["q"] += 1
    if not grp:
        return ""
    lignes = []
    for (ra, rb, vis), g in grp.items():
        ou = f"{ra} {M.NOMS.get(ra, '')}" + (f" → {rb} {M.NOMS.get(rb, '')}" if rb else "")
        passage, avant = M.PERCAGE[vis]
        lignes.append(f'<tr><td>{escape(ou)}</td><td class="num">{g["q"]}</td><td>{escape(passage)}</td>'
                      f'<td>{escape(avant)}</td><td>{escape(M.VIS[vis])}</td><td class="u">{escape(g["pos"])}</td></tr>')
    return ('<details class="perc" open><summary>Perçages</summary><div class="scroll"><table class="debit"><thead><tr>'
            '<th>Assemblage (on perce la première pièce)</th><th class="num">Trous</th><th>Pièce traversée</th>'
            '<th>Pièce reçue</th><th>Vis</th><th>Position</th></tr></thead><tbody>' + "".join(lignes) +
            '</tbody></table></div></details>')


def profil_bac():
    """Schéma de côté à travers le sac nord : L fermé, sac et barres, puis L basculé jusqu'à la butée (tireté)."""
    axe, a = M.BAC["axe"], M.BAC["angle"]
    tout = M.version("d")
    nom = {b.nom: b for b in tout}
    o = []
    for n_ in ("rail_av", "rail_ar", "butee_vis_n", "echarpe_n", "montant_av_n", "montant_ar_n", "lisse_basse_n", "lisse_haute_n",
               "lisse_barre_n", "plan_travail"):
        b = nom[n_]
        o.append(PL.poly([(u, -z) for u, z in b.pts("y")], "dg" if b.role == "bois" else "cab"))
    o.append(PL.poly([(u, -z) for u, z in nom["bac_sac_1"].pts("y")], "sac"))
    mob = [nom[n_] for n_ in ("plateau", "contrefiche_n", "bac_porte", "support_porte_n", "barre_porte_n")]
    for b in mob + [nom["support_fixe_n"], nom["barre_fixe_n"]]:
        cls = {"facade": "fac", "barre": "tas", "bois": "dg"}.get(b.role, "cab")
        o.append(PL.poly([(u, -z) for u, z in b.pts("y")], cls))
    for b in mob:
        p = [M.bascule(x, z, axe, a) for x, z in b.pts("y")]
        o.append(PL.poly([(x, -z) for x, z in p], "swingp"))
    xf0, xr0, zb0, zb1 = M.BAC["barres"]
    bx = M.BAC["barre"][0]
    fa = M.bascule(xf0 + bx, zb0 + 1, axe, a)
    fb = M.bascule(M.XO1 - M.DL - 1, M.DL + M.T + 1, axe, a)
    fc = M.bascule(xf0 + 1, M.DL + M.T + 1, axe, a)
    o.append(PL.poly([(fa[0], -fa[1]), (xr0, -(zb0 + 1)), (fb[0], -fb[1]), (fc[0], -fc[1])], "sacopen"))
    o.append(f'<circle class="axe" cx="{axe[0]}" cy="{-axe[1]:.2f}" r="1"/>')
    h = M.bascule(M.FACE, M.FACADES[0][1], axe, a)
    rr = M.FACADES[0][1] - axe[1]
    o.append(f'<path class="lead" d="M{M.FACE} {-M.FACADES[0][1]:.1f} A{rr:.1f} {rr:.1f} 0 0 0 {h[0]:.1f} {-h[1]:.1f}"/>')
    o.append(PL.text(h[0] - 1, -h[1] - 2, f"{a}°", "lbls", "end"))
    o.append(PL.text(axe[0] + 2, -axe[1] + 5, "axe : charnières plates sur le rail avant", "lblx", "start"))
    bu = M.BUTEE
    o.append(PL.text(bu.x1 + 1.5, -(bu.z0 + 1), f"tire-fond de butée ({M.BAC['angle_max']}°)", "lblx", "start"))
    o.append(PL.text(xr0 + bx + 1.5, -(zb1 - 1), "barre arrière (amovible)", "lblx", "start"))
    o.append(PL.text((M.XO0 + M.XO1) / 2 + 4, -40, "sac", "lblx"))
    x0, x1 = M.FACE - 32, M.XO1 + 22
    return (f'<svg viewBox="{x0} {-(M.Z_DESSUS + 6):.1f} {x1 - x0} {M.Z_DESSUS + 14:.1f}" role="img" '
            f'aria-label="Porte basculée jusqu\'à la butée, vue de côté">{"".join(o)}</svg>')


def charniere_svg():
    """Détail de côté à l'axe : rail avant, fond et bas de la porte, charnière plate (lames entre rail et fond, nœud à
    l'arête avant), et le bac basculé en tireté. Cotes en cm."""
    axe, a = M.BAC["axe"], M.BAC["angle"]
    tout = {b.nom: b for b in M.version("d")}
    z0, z1 = -1.5, 12
    x0, x1 = M.FACE - 9, M.XO0 + 12
    o = []

    def coupe(b, cls, tourne=False):
        pts = [(max(min(x, x1), x0), min(z, z1)) for x, z in b.pts("y")]
        if tourne:
            pts = [M.bascule(x, z, axe, a) for x, z in pts]
        o.append(PL.poly([(x, -z) for x, z in pts], cls))

    coupe(tout["rail_av"], "dg")
    for nom in ("plateau", "bac_porte"):
        coupe(tout[nom], "fac" if nom == "bac_porte" else "cab")
        coupe(tout[nom], "swingp", True)
    # lames : 2 de long sur le rail et sous le fond, nœud Ø 0,5 à l'arête
    o.append(PL.rect(axe[0], -(axe[1] + 0.05), axe[0] + 2.0, -(axe[1] - 0.05), "chmet"))
    o.append(f'<circle class="chmet" cx="{axe[0]:.2f}" cy="{-axe[1]:.2f}" r="0.25"/>')
    o.append(f'<circle class="axe" cx="{axe[0]:.2f}" cy="{-axe[1]:.2f}" r="0.12"/>')
    o.append(PL.text(axe[0] + 2.4, -(axe[1] - 1.2), "charnière plate", "chl", "start"))
    o.append(PL.text(axe[0] + 2.4, -(axe[1] + 3.4), "plateau A3", "chl", "start"))
    o.append(PL.text(axe[0] + 2.4, -(axe[1] - 3.0), "rail G5", "chl", "start"))
    o.append(PL.text(M.FACE - 0.6, -(z1 - 1.4), "porte A6", "chl", "end"))
    o.append(PL.cote_v(-axe[1], -(axe[1] + M.BAC["porte_bas"]), M.FACE - 2.2, "0,5", t=0.6))
    return (f'<figure class="charn" style="max-width:340px"><svg viewBox="{x0:.1f} {-z1:.1f} {x1 - x0:.1f} {z1 - z0:.1f}" role="img" '
            f'aria-label="Charnière plate">{"".join(o)}</svg><figcaption>Charnière plate vue de côté : une lame sur le '
            "rail, l’autre sous le plateau, nœud à l’arête avant du rail ; la porte commence 0,5 au-dessus (place du "
            f"nœud). Tireté : basculé à {a}°.</figcaption></figure>")


def puces_pieces(c, n):
    cpt = Counter(b.rep for b in pieces_etape(c, n) if b.rep)
    if "E2" in cpt:
        cpt["E2"] = 1           # une cornière, modélisée en deux ailes
    r = "".join(f'<span class="pc"><b>{r}</b> × {q}</span>' for r, q in sorted(cpt.items(), key=lambda t: (t[0][0], int(t[0][1:]))))
    return r + (f'<span class="pc muted">dessin : 1 exemplaire sur {FOIS[n]}</span>' if n in FOIS else "")


def bloc_etape(n):
    titre, texte, q = M.ETAPES[n]
    par_cote = n not in SEUL
    if par_cote:
        fig = f'<div class="vd">{dessin_etape("d", n)}</div>'
    else:
        fig = dessin_etape("d", n)
    fois = f'<div class="fois">× {FOIS[n]}</div>' if n in FOIS else ""
    extra = f'<div class="mini"><div class="charns">{charniere_svg()}</div>{profil_bac()}</div>' if n == 4 else ""
    pcs = puces_pieces("d", n)
    return f"""<section class="etape" id="etape-{n}">
<div class="num">{n}</div>
<div class="ecorps">
<h2>{escape(titre)}</h2>
<div class="pcs">{pcs}</div>
<div class="hws">{puces_quinc(q)}</div>
<div class="edessin">{fig}{fois}{extra}</div>
<p class="consigne">{escape(texte)}</p>
{table_percages(n)}
</div>
</section>"""


# ------------------------------------------------------------------ plans des sous-ensembles (V4.3)
# Pour chaque sous-ensemble : une vue éclatée (pièces écartées du centre, repérées, trous dessinés), puis une fiche par
# pièce : ses faces percées à plat, cotées depuis le coin en bas à gauche, et avec quoi elle s'assemble.
SOUS_ENSEMBLES = [
    ("bas", "Échelle nord (côté bac)", lambda b: b.groupe == "ossature" and b.nom.endswith("_n")),
    ("bas", "Échelle du milieu (entre bac et machine)", lambda b: b.groupe == "ossature" and b.nom.endswith("_c")),
    ("bas", "Échelle du mur sud", lambda b: b.groupe == "ossature" and b.nom.endswith("_s")),
    ("bas", "Rails", lambda b: b.nom.startswith("rail_")),
    ("bas", "Porte basculante (le L)", lambda b: b.groupe == "bac" and b.role in ("facade", "bac", "bois", "support")
     and not b.nom.startswith("support_fixe") and b.nom != "accroche_centrale"),
    ("bas", "Barres arrière et accroche centrale", lambda b: b.nom.startswith(("support_fixe", "barre_fixe")) or b.nom == "accroche_centrale"),
    ("bas", "Plan de travail", lambda b: b.groupe == "plan"),
    ("haut", "Caisson haut", lambda b: b.groupe == "caisson_haut" and b.role != "led"),
]
DIAM = {"insert": (1.0, None), "vis16": (0.4, 0.25), "vis60": (0.5, 0.3), "vis40": (0.4, 0.25), "vis40l": (1.0, 0.3), "vis16l": (1.0, 0.25), "confirmat": (0.5, 0.4),
        "cuvette": (3.5, None), "prise": (2.5, None), "cheville": (0.6, None), "depart": (1.0, None), "doigt": (2.0, None)}   # Ø passage, Ø avant-trou (cm)
FACE_NOM = {(0, -1): "face avant", (0, 1): "face arrière", (1, -1): "côté nord", (1, 1): "côté sud",
            (2, -1): "dessous", (2, 1): "dessus"}


def eclate(bl, k=0.7):
    """Écarte chaque pièce du centre du sous-ensemble ; renvoie les pièces déplacées et leur décalage par nom."""
    if len(bl) < 2:
        return bl, {b.nom: (0, 0, 0) for b in bl}
    cx = sum((b.x0 + b.x1) / 2 for b in bl) / len(bl)
    cy = sum((b.y0 + b.y1) / 2 for b in bl) / len(bl)
    cz = sum((b.z0 + b.z1) / 2 for b in bl) / len(bl)
    r, d = [], {}
    for b in bl:
        dx, dy, dz = (((b.x0 + b.x1) / 2 - cx) * k, ((b.y0 + b.y1) / 2 - cy) * k, ((b.z0 + b.z1) / 2 - cz) * k)
        d[b.nom] = (dx, dy, dz)
        if isinstance(b, M.Profil):
            r.append(M.replace(b, xz=[(x + dx, z + dz) for x, z in b.xz], y0=b.y0 + dy, y1=b.y1 + dy))
        else:
            r.append(M.replace(b, x0=b.x0 + dx, x1=b.x1 + dx, y0=b.y0 + dy, y1=b.y1 + dy, z0=b.z0 + dz, z1=b.z1 + dz))
    return r, d


def trous_de(nom, role):
    """Trous d'une pièce : role "a" (on la traverse) ou "b" (elle reçoit la vis)."""
    return [t for t in M.TROUS if t[role] == nom]


def face_svg(b, k, s, trous_a, trous_b):
    """Une face de la pièce à plat : normale k (0 x, 1 y, 2 z), sens s ; trous et entailles cotés depuis le coin bas gauche.
    Dessin schématique : la longueur est ramenée à 100, l'épaisseur des pièces très fines est agrandie pour rester
    lisible ; les cotes, elles, sont vraies (mm)."""
    bornes = [(b.x0, b.x1), (b.y0, b.y1), (b.z0, b.z1)]
    autres = [i for i in range(3) if i != k]
    h = max(autres, key=lambda i: bornes[i][1] - bornes[i][0])
    v = autres[0] if autres[1] == h else autres[1]
    profil = isinstance(b, M.Profil) and k == 1
    if profil:                          # pièce profilée (support en demi-lune) : vue de face, le dessus en haut
        h, v = 0, 2
    W, H = bornes[h][1] - bornes[h][0], bornes[v][1] - bornes[v][0]
    u0, v0 = bornes[h][0], bornes[v][0]
    sx = 100 / W if W > 25 else 4
    sy = min(max(sx, 9 / H), 90 / H)
    w_, h_ = W * sx, H * sy
    fs = 3.4
    X = lambda u: u * sx                # noqa: E731
    Y = lambda w: h_ - w * sy           # noqa: E731
    if profil:
        o = [f'<polygon class="fpc {M.meuble(b.rep)}" points="' +
             " ".join(f"{X(x - u0):.2f},{Y(z - v0):.2f}" for x, z in b.xz) + '"/>']
    else:
        o = [f'<rect class="fpc {M.meuble(b.rep)}" x="0" y="0" width="{w_:.2f}" height="{h_:.2f}"/>']
    if isinstance(b, M.Bloc) and b.encoche and k == 2:      # trou de la trappe
        x0, x1, y0, y1 = b.encoche
        r_ = {0: (x0, x1), 1: (y0, y1)}
        o.append(f'<rect class="fent" x="{X(r_[h][0] - u0):.2f}" y="{Y(r_[v][1] - v0):.2f}" '
                 f'width="{(r_[h][1] - r_[h][0]) * sx:.2f}" height="{(r_[v][1] - r_[v][0]) * sy:.2f}" rx="{0.5 * sx:.2f}"/>')
    for e in getattr(b, "entailles", ()) if k == 2 else ():
        x0, x1, y0, y1 = e
        r_ = {0: (x0, x1), 1: (y0, y1)}
        a0, a1 = r_[h]
        c0, c1 = r_[v]
        o.append(f'<rect class="fent" x="{X(a0 - u0):.2f}" y="{Y(c1 - v0):.2f}" width="{(a1 - a0) * sx:.2f}" '
                 f'height="{(c1 - c0) * sy:.2f}"/>')
    us, vs = set(), set()
    for t, cls in [(t, "fta") for t in trous_a] + [(t, "ftb") for t in trous_b]:
        c = (t["x"], t["y"], t["z"])
        u, w = c[h] - u0, c[v] - v0
        dp, da = DIAM.get(t["vis"], (0.4, 0.25))
        rr = (dp if cls == "fta" else (da or dp)) / 2 * min(sx, sy)
        o.append(f'<circle class="{cls}" cx="{X(u):.2f}" cy="{Y(w):.2f}" r="{min(max(rr, 0.9), 6):.2f}"/>')
        us.add(round(u, 1))
        vs.add(round(w, 1))
    rangs, der = [], []
    for u in sorted(us):                # cotes en bas, sur plusieurs rangs si elles se touchent
        k_ = next((i for i, x in enumerate(der) if X(u) - x > 9), len(der))
        if k_ == len(der):
            der.append(-99)
        der[k_] = X(u)
        y = h_ + (k_ + 1) * (fs + 0.8)
        o.append(f'<line class="fdim" x1="{X(u):.2f}" y1="{h_:.2f}" x2="{X(u):.2f}" y2="{y - fs + .4:.2f}"/>'
                 f'<text class="ftx" x="{X(u):.2f}" y="{y:.2f}" style="font-size:{fs}px">{u * 10:.0f}</text>')
    nb = len(der)
    gauche, der = [], []
    for w in sorted(vs):                # cotes à gauche, décalées si elles se touchent
        k_ = next((i for i, x in enumerate(der) if Y(w) < x - fs), len(der))
        if k_ == len(der):
            der.append(999)
        der[k_] = Y(w)
        o.append(f'<text class="ftx" x="{-1 - k_ * 9:.2f}" y="{Y(w) + fs * .35:.2f}" style="font-size:{fs}px" '
                 f'text-anchor="end">{w * 10:.0f}</text>')
    o.append(f'<text class="ftx muted" x="{w_:.2f}" y="{-1.2:.2f}" text-anchor="end" style="font-size:{fs}px">'
             f'{W * 10:.0f} × {H * 10:.0f}</text>')
    gx = 3 + 9 * max(1, len(der))
    vw, vh = w_ + gx + 2, h_ + fs + 2.5 + nb * (fs + 0.8)
    return (f'<svg class="face" viewBox="{-gx:.2f} {-fs - 2:.2f} {vw:.2f} {vh:.2f}" '
            f'style="max-width:{vw * 2.6:.0f}px" role="img" aria-label="{escape(b.rep)}">{"".join(o)}</svg>')


def signature(b):
    """Motif de perçage d'une pièce (coordonnées locales) : deux pièces de même repère et même motif ne font qu'une fiche."""
    m = []
    for role in ("a", "b"):
        for t in trous_de(b.nom, role):
            m.append((role, t["vis"], t["n"], round(t["x"] - b.x0, 1), round(t["y"] - b.y0, 1), round(t["z"] - b.z0, 1)))
    return tuple(sorted(m))


def fiche(b, q):
    faces = {}
    for role in ("a", "b"):
        for t in trous_de(b.nom, role):
            k = next(i for i, c in enumerate(t["n"]) if c)
            faces.setdefault((k, t["n"][k]), {"a": [], "b": []})[role].append(t)
    if getattr(b, "entailles", ()) and (2, 1) not in faces:
        faces[(2, 1)] = {"a": [], "b": []}
    if isinstance(b, M.Profil) and not any(k == 1 for k, _ in faces):     # profil (demi-lune) : toujours la vue de côté
        faces[(1, -1)] = {"a": [], "b": []}
    dims = sorted((b.x1 - b.x0, b.y1 - b.y0, b.z1 - b.z0), reverse=True)
    lien = Counter()
    for t in trous_de(b.nom, "a"):
        lien[(t["rb"] or "", t["vis"], "dans")] += 1
    for t in trous_de(b.nom, "b"):
        lien[(t["ra"], t["vis"], "depuis")] += 1
    liens = "".join(f'<li>{n} × {escape(M.VIS[v])} ' + (f'{"dans" if d == "dans" else "venant de"} <b>{r}</b> '
                    f'{escape(M.NOMS.get(r, ""))}' if r else f'({escape(M.PERCAGE[v][0])})') + '</li>'
                    for (r, v, d), n in lien.items())
    figs = "".join(f'<div class="fface"><div class="fnom">{FACE_NOM[(k, s)]}</div>'
                   f'{face_svg(b, k, s, f_["a"], f_["b"])}</div>' for (k, s), f_ in sorted(faces.items()))
    if not figs:
        figs = '<p class="note">Aucun perçage.</p>'
    return (f'<div class="fiche"><div class="ftete"><b class="crep">{b.rep}</b> {escape(M.NOMS.get(b.rep, b.nom))}'
            f'<span class="cq">× {q}</span><span class="mono note">{" × ".join(f"{d * 10:.0f}" for d in dims)}</span></div>'
            f'{figs}<ul class="fliens">{liens}</ul></div>')


def sous_ensemble(meuble, titre, filtre):
    tout = [b for b in M.version("d") if b.role not in ("prise", "sac", "machine") and filtre(b)]
    bl, dec = eclate(tout)
    trs = []
    for t in M.TROUS:
        if t["a"] in dec:
            dx, dy, dz = dec[t["a"]]
            trs.append(dict(t, x=t["x"] + dx, y=t["y"] + dy, z=t["z"] + dz))
    iso = dessin(bl, {b.nom for b in bl}, titre=titre, trous=trs)
    groupes = {}
    for b in tout:
        if b.rep:
            groupes.setdefault((b.rep, signature(b)), []).append(b)
    fiches = "".join(fiche(v[0], len(v)) for _, v in sorted(groupes.items(), key=lambda t: (t[0][0][0], int(t[0][0][1:]))))
    return (f'<h3 class="se {meuble}">{escape(titre)}</h3><div class="edessin">{iso}</div>'
            f'<div class="fiches">{fiches}</div>')


def plans_sous_ensembles(meuble):
    return "".join(sous_ensemble(m, t, f) for m, t, f in SOUS_ENSEMBLES if m == meuble)


# ------------------------------------------------------------------ pages d'ouverture : pièces, outils, vue éclatée
def carte_piece(p):
    b = next(b for b in M.PIECES if b.rep == p["rep"])
    # pièce seule, à plat contre l'origine
    if isinstance(b, M.Profil):
        bb = M.replace(b, xz=[(x - b.x0, z - b.z0) for x, z in b.xz], y0=0, y1=b.y1 - b.y0)
    else:
        bb = M.replace(b, x0=0, x1=b.x1 - b.x0, y0=0, y1=b.y1 - b.y0, z0=0, z1=b.z1 - b.z0, encoche=())
    svg = dessin([bb], {bb.nom}, reperes=False, marge=3, titre=p["nom"])
    sec = f'Ø {p["l"]}' if p["rep"] == "E4" else f'{p["l"]} × {p["e"]}'
    return (f'<div class="carte"><div class="cdes">{svg}</div><div class="cpied"><b class="crep">{p["rep"]}</b>'
            f'<span class="cq">{p["q"]}×</span></div><div class="cnom">{escape(p["nom"])}</div>'
            f'<div class="cdim mono">{p["L"]} × {sec}</div></div>')


def vue_eclatee(c):
    s = 1 if c == "d" else -1
    decale = {"bac": (-75, 0, 0), "cadre": (0, 0, 22),
              "plan": (0, 0, 48), "caisson_haut": (0, 0, 85), "machine": (-45, 0, 0), "caisson": (-20, 0, 0)}
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
.isac{fill:hsl(205 60% calc(var(--t) * 40% + 55%));fill-opacity:.8;stroke:var(--water);stroke-width:.35;stroke-dasharray:1.2 .8}
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
.etape>.num{font:800 56px/1 Archivo,system-ui,sans-serif;letter-spacing:-.03em}
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
.itr{fill:var(--ink);stroke:var(--panel)}
.ihole{fill:var(--paper);stroke:var(--ink);stroke-width:.3}
.charns{display:grid;grid-template-columns:repeat(auto-fit,minmax(300px,1fr));gap:10px;margin-bottom:10px}
.charn{margin:0}.charn svg{display:block;width:100%;height:auto;max-height:40vh}
.pose .charn svg{max-height:78vh}.pose .charn .lblx{font-size:4.2px}.pose .charn .dimt{font-size:4px}.pose .charn .dim{stroke-width:.3}
.charn figcaption{font-size:12.5px;color:var(--muted)}
.chcup{fill:var(--paper);stroke:var(--ink);stroke-width:.15}.chmet{fill:#B9C2C8;stroke:var(--ink);stroke-width:.12}
.charm{fill:none;stroke:#7D8A92;stroke-width:.55;stroke-linejoin:round}.chvis{stroke:var(--ink);stroke-width:.3}
.chr{font:700 1.1px JetBrains Mono,monospace;fill:var(--ink)}.chl{font-size:.95px;fill:var(--ink)}
.charn .dimt{font-size:1px}.charn .dim{stroke-width:.08}.charn .fac{stroke-width:.15}.charn .swingp{stroke-width:.12}
.charn .dg,.charn .cab{stroke-width:.12}
h3.se{font-size:19px;margin:30px 0 6px;padding-left:10px;border-left:6px solid var(--bas)}h3.se.haut{border-left-color:var(--haut)}
.fiches{display:grid;grid-template-columns:repeat(auto-fill,minmax(300px,1fr));gap:10px}
.fiche{background:var(--panel);border:1px solid var(--line);border-radius:10px;padding:8px 10px}
.ftete{display:flex;flex-wrap:wrap;gap:8px;align-items:baseline;font-size:14px}.ftete .cq{margin-left:auto}
.fface{margin:6px 0}.fnom{font-size:12px;color:var(--muted)}
svg.face{display:block;width:100%;height:auto}
.fpc{fill:var(--bas);stroke:var(--ink);stroke-width:.12}.fpc.haut{fill:var(--haut)}
.fent{fill:var(--panel);stroke:var(--ink);stroke-width:.1;stroke-dasharray:.4 .3}
.fta{fill:var(--ink)}.ftb{fill:var(--panel);stroke:var(--ink);stroke-width:.12}
.fdim{stroke:var(--muted);stroke-width:.06}.ftx{fill:var(--ink);font-family:"JetBrains Mono",ui-monospace,monospace;text-anchor:middle}
.ftx.muted{fill:var(--muted)}
.fliens{margin:4px 0 0;padding-left:18px;font-size:12.5px;color:var(--muted)}
.lg{display:inline-block;width:10px;height:10px;border-radius:50%;vertical-align:-1px;border:1px solid var(--ink)}
.lg.fta{background:var(--ink)}.lg.ftb{background:var(--panel)}.lg.fent{border-radius:2px;border-style:dashed}
h2.partie{font-size:28px;margin:48px 0 4px;padding:10px 14px;border-radius:10px;background:var(--bas)}
h2.partie.haut{background:var(--haut)}
.itr2{fill:var(--panel);stroke:var(--ink)}
details.perc{margin:10px 0 0}details.perc summary{cursor:pointer;font-weight:700;font-size:14px}
.percage svg{display:block;width:100%;max-width:640px;height:auto}
.pvide{fill:var(--panel);stroke:var(--ink);stroke-width:.3}
.pvis{fill:#B9C2C8;stroke:var(--ink);stroke-width:.35}
.pfil{stroke:var(--ink);stroke-width:.3}
.ptx{font-size:5px;fill:var(--ink)}.ptx.muted{fill:var(--muted)}
@media (max-width:560px){ .etape{grid-template-columns:1fr} .etape>.num{font-size:40px} }
"""

# V5.15 : outils par meuble (le bas et le haut se font séparément)
OUTILS = {
    "bas": [
        "perceuse-visseuse et embouts cruciformes PZ2",
        "forets bois Ø 2,5, 3, 4 et 5 ; mèche Ø 10 (lamages sous les lisses hautes, trous des inserts des vérins)",
        "clé six pans (inserts M8 des vérins), clé plate de 13 ou pince (réglage des vérins)",
        "fraise à noyer (fraise à encastrer, têtes de vis)",
        "mèche plate Ø 25 (demi-lunes des supports B1, trou de prise de la porte)",
        "scie à onglet, ou scie égoïne et boîte à onglets : tasseaux, coupes à 45° des contrefiches",
        "fausse équerre ou rapporteur (coupes des écharpes)",
        "scie sauteuse : encoche du plan, crochet de l'accroche centrale, supports B1",
        "scie circulaire et règle de guidage pour recouper le plan et les tablettes (ou découpe en magasin)",
        "ponceuse ou cale à poncer, pinceau ou petit rouleau (peinture des tasseaux)",
        "fer à repasser (chant thermocollant) et cutter",
        "équerre de menuisier, niveau à bulle, mètre, crayon, serre-joints",
        "ruban adhésif (butée de profondeur sur les forets)",
        "pistolet à silicone",
        "machine à coudre (les deux sacs)",
        "deux personnes pour la machine",
    ],
    "haut": [
        "perceuse-visseuse et embouts cruciformes PZ2",
        "forets bois Ø 2,5 et 4 ; fraise à noyer",
        "défonceuse, fraise droite Ø 20 (ou Ø 10 en deux passes) et règle de guidage : rainures des portes",
        "scie circulaire et règle de guidage pour les tablettes (ou découpe en magasin)",
        "gabarit à taquets et foret Ø 5 avec butée (trous des étagères)",
        "fer à repasser (chant thermocollant) et cutter",
        "perceuse à percussion ou perforateur, foret selon le mur (béton / maçonnerie Ø 8, ou foret bois-métal pour le placo)",
        "détecteur de câbles et de tuyaux (les prises de la niche et le robinet sont juste en dessous)",
        "niveau à bulle de 60 ou plus, mètre, crayon",
        "deux cales de la hauteur de la niche, escabeau",
        "deux personnes pour présenter le caisson",
    ],
}



def fixation_svg():
    """Schéma de pose du caisson haut : de face (mur du fond, carrelage, chevilles, cales) et en coupe (vis, cheville,
    cale sur le plan). Cotes en cm."""
    ch, cr = M.CH, M.CARRELAGE
    tr = [t for t in M.TROUS if t["vis"] == "cheville"]
    zs = sorted({round(t["z"], 1) for t in tr})
    cal = [(12, 22), (M.Y1 - 22, M.Y1 - 12)]
    hach = ('<defs><pattern id="carreau" width="6" height="6" patternUnits="userSpaceOnUse">'
            '<path d="M0 6 L6 0" stroke="var(--muted)" stroke-width=".3"/></pattern></defs>')
    # vue de face : y vers la droite (nord à gauche), z vers le haut
    o = [hach, PL.rect(0, -M.H, M.Y1, 0, "", ' style="fill:var(--panel);stroke:var(--ink);stroke-width:.4"'),
         PL.rect(0, -cr, M.Y1, 0, "", ' style="fill:url(#carreau);stroke:none"'),
         f'<line x1="0" y1="{-cr}" x2="{M.Y1}" y2="{-cr}" style="stroke:var(--ink);stroke-width:.4;stroke-dasharray:2 1.5"/>',
         PL.text(M.Y1 - 2, -cr + 4, f"fin du carrelage {cr}", "lblx", "end"),
         PL.rect(M.YM0, -M.Z_DESSUS, M.YM1, -M.Z_PLAN, "top"),
         PL.text(M.Y1 / 2, -M.Z_PLAN + 5, "plan de travail", "lblx"),
         PL.rect(ch["y0"], -ch["z1"], ch["y1"], -ch["z0"], "", ' style="fill:var(--cab);fill-opacity:.55;stroke:var(--ink);stroke-width:.5"'),
         f'<line x1="{M.CENTRE}" y1="{-ch["z1"]}" x2="{M.CENTRE}" y2="{-ch["z0"]}" style="stroke:var(--ink);stroke-width:.3;stroke-dasharray:1 1"/>',
         PL.text(M.Y1 / 2, -(ch["z0"] + 8), "caisson haut (vu à travers)", "lblx")]
    for y0, y1 in cal:
        o.append(PL.rect(y0, -M.Z_HAUT, y1, -M.Z_DESSUS, "dg"))
    o.append(PL.text(cal[0][1] + 2, -(M.Z_DESSUS + M.Z_HAUT) / 2, f"cale {PL.cm(M.Z_HAUT - M.Z_DESSUS)}", "lblx", "start"))
    for t in tr:
        o.append(f'<circle cx="{t["y"]:.1f}" cy="{-t["z"]:.1f}" r="1.6" style="fill:var(--ink)"/>')
    o.append(PL.cote_v(-cr, -zs[0], M.Y1 + 5, PL.cm(zs[0] - cr)))
    o.append(PL.cote_v(-zs[0], -zs[-1], M.Y1 + 5, PL.cm(zs[-1] - zs[0])))
    o.append(PL.cote_v(0, -cr, M.Y1 + 12, str(cr)))
    o.append(PL.cote_v(-M.Z_DESSUS, -M.Z_HAUT, -6, PL.cm(M.Z_HAUT - M.Z_DESSUS)))
    o.append(PL.cote_h(0, 10, -zs[-1] - 4, "10"))
    o.append(PL.cote_h(M.Y1 - 10, M.Y1, -zs[-1] - 4, "10"))
    o.append(PL.text(1, 6, "nord", "lblx muted", "start"))
    o.append(PL.text(M.Y1 - 1, 6, "sud", "lblx muted", "end"))
    face = (f'<svg viewBox="-16 {-M.H - 6} {M.Y1 + 34} {M.H + 16}" role="img" aria-label="Pose du caisson haut, de face">'
            f'{"".join(o)}</svg>')
    # coupe : x vers la droite jusqu'au mur du fond, z vers le haut
    x0 = M.FACE - 6
    hx = M.X1 - M.F
    ep = M.EP_CARRELAGE
    # X1 = surface du carreau ; au-dessus du carrelage, le mur nu est ep plus loin
    o = [hach, PL.rect(M.X1 + ep, -M.H, M.X1 + 8, 0, "w"),
         PL.rect(M.X1, -cr, M.X1 + ep, 0, "", ' style="fill:url(#carreau);stroke:var(--ink);stroke-width:.3"'),
         PL.text(M.X1 - 2, -cr + 6, "carrelage", "lblx", "end"),
         PL.rect(M.FACE, -M.Z_DESSUS, M.PLAN_X1, -M.Z_PLAN, "top"),
         PL.rect(ch["x0"], -ch["z1"], M.X1, -ch["z0"], "", ' style="fill:var(--cab);fill-opacity:.55;stroke:var(--ink);stroke-width:.5"'),
         PL.rect(hx, -ch["z1"], M.X1, -ch["z0"], "cab"),
         PL.rect(ch["x0"] + 8, -M.Z_HAUT, ch["x0"] + 18, -M.Z_DESSUS, "dg"),
         PL.text(ch["x0"] + 7, -(M.Z_DESSUS + M.Z_HAUT) / 2, "cale", "lblx", "end")]
    for z in zs:
        o.append(PL.rect(M.X1, -(z + 2), M.X1 + ep, -(z - 2), "dg"))     # cale de l'épaisseur du carrelage
        o.append(f'<line x1="{hx - 1.5}" y1="{-z}" x2="{M.X1 + ep + 6}" y2="{-z}" style="stroke:var(--ink);stroke-width:.6"/>')
        o.append(PL.rect(M.X1 + ep, -(z + 0.6), M.X1 + ep + 6, -(z - 0.6), "", ' style="fill:var(--tri);fill-opacity:.7"'))
    o.append(PL.text(hx - 3, -zs[-1] - 3, "vis 6 × 70 + rondelle", "lblx", "end"))
    o.append(PL.text(hx - 3, -zs[-1] + 8, f"cale de {PL.cm(ep)} (épaisseur du carrelage)", "lblx", "end"))
    o.append(PL.text(hx - 3, -zs[0] + 5, "cheville Ø 8 dans le mur nu", "lblx", "end"))
    o.append(PL.cote_h(ch["x0"], M.X1, -M.H - 3, "45"))
    o.append(PL.cote_v(0, -cr, M.X1 + 13, str(cr)))
    o.append(PL.cote_v(-cr, -zs[0], M.X1 + 13, PL.cm(zs[0] - cr)))
    o.append(PL.text(x0, 6, "pièce ←   → mur du fond", "lblx muted", "start"))
    coupe = (f'<svg viewBox="{x0 - 2} {-M.H - 8} {M.X1 + 22 - x0} {M.H + 18}" role="img" '
             f'aria-label="Pose du caisson haut, en coupe">{"".join(o)}</svg>')
    return (f'<div class="charns pose"><figure class="charn">{face}<figcaption>De face : chevilles (points noirs) toutes '
            f'au-dessus du carrelage, deux cales de {PL.cm(M.Z_HAUT - M.Z_DESSUS)} sur le plan pour porter le caisson '
            f'pendant qu\u2019on perce et qu\u2019on visse.</figcaption></figure><figure class="charn">{coupe}<figcaption>'
            'En coupe : la vis traverse le fond du caisson et entre dans la cheville, dans le mur nu au-dessus du '
            'carrelage ; la cale tient le caisson à la bonne hauteur.</figcaption></figure></div>')


def fixation_haut():
    """Méthode de fixation du caisson haut : au-dessus du carrelage, à travers le fond, chevilles selon le mur."""
    zf = sorted({round(t["z"]) for t in M.TROUS if t["vis"] == "cheville"})
    etapes = [
        f"<b>Où</b> : six vis à travers le fond C1, toutes au-dessus du carrelage (il s'arrête à {M.CARRELAGE}) : deux "
        f"rangées de trois, à {zf[0]} et {zf[-1]} du sol, à 10 des côtés et de part et d'autre du montant central. Le "
        "carreau n'est jamais percé.",
        "<b>Le mur</b> : faire un trou d'essai dans la zone cachée par le caisson. Poussière rouge ou grise et dure : "
        "brique ou béton, chevilles nylon Ø 8 (ou chevilles « tout matériau ») ; ça traverse vite et sonne creux : placo "
        "ou brique creuse, chevilles à expansion métalliques (type Molly) Ø 8 ou chevilles pour corps creux. Vis 6 × 70 "
        "avec rondelle dans tous les cas.",
        f"<b>L'épaisseur du carrelage</b> : le relevé est pris sur le carreau ; au-dessus de {M.CARRELAGE}, le mur nu est "
        f"en retrait d'environ {PL.cm(M.EP_CARRELAGE)} (carreau + colle, à mesurer au bord du carrelage). Le fond du "
        "caisson s'appuie sur le carreau en bas ; derrière chaque cheville, glisser une cale de cette épaisseur (cales "
        "de menuisier en plastique empilées, ou chute de bois) pour que le caisson reste d'aplomb et ne se tord pas "
        "en serrant. Vis 6 × 70 au lieu de 6 × 60.",
        "<b>Les réseaux</b> : passer le détecteur sur toute la zone avant de percer ; les fils des prises de la niche "
        "et le tuyau du robinet montent souvent à la verticale au-dessus d'eux.",
        f"<b>Présenter</b> : à deux, poser le caisson sur deux cales de {PL.cm(M.Z_HAUT - M.Z_DESSUS)} posées sur le "
        "plan (le dessous du caisson tombe à la bonne hauteur), le plaquer au mur du fond, vérifier le niveau sur le "
        "dessus.",
        "<b>Marquer et percer</b> : percer les six trous Ø 6 à travers le fond jusqu'au mur pour marquer, retirer le "
        "caisson, percer le mur au foret du mur choisi (percussion seulement sur brique ou béton), poser les chevilles.",
        "<b>Visser</b> : remettre le caisson sur ses cales, visser d'abord les deux trous du haut aux coins, contrôler le "
        "niveau, puis les quatre autres. Retirer les cales.",
        "<b>Charge</b> : caisson vide ≈ 25 kg (estimation), plus les serviettes et les produits ; six chevilles adaptées au "
        "mur suffisent largement (de mémoire, à vérifier sur l'emballage des chevilles).",
    ]
    return fixation_svg() + '<ol class="pistes">' + "".join(f"<li>{e}</li>" for e in etapes) + "</ol>"


def percage_type():
    """Coupe d'un vissage type : pièce traversée (passage + fraisure), pièce reçue (avant-trou), vis."""
    o = []
    o.append('<rect class="dg" x="0" y="0" width="60" height="33"/>')
    o.append('<rect class="dg" x="0" y="33" width="60" height="40" style="filter:brightness(.92)"/>')
    o.append('<path class="pvide" d="M27.5 0 L32.5 0 L32.5 33 L27.5 33 Z M25 0 L35 0 L32.5 3 L27.5 3 Z"/>')
    o.append('<path class="pvide" d="M28.5 33 L31.5 33 L31.5 63 L28.5 63 Z"/>')
    o.append('<path class="pvis" d="M25.2 0 L34.8 0 L32 2.8 L32 60 L30 64 L28 60 L28 2.8 Z"/>')
    for y in range(6, 60, 4):
        o.append(f'<line class="pfil" x1="27.6" y1="{y}" x2="32.4" y2="{y + 2}"/>')
    lab = [(0, 16, "pièce traversée : passage Ø 5 (vis Ø 5) + fraisure"), (0, 50, "pièce reçue : avant-trou Ø 3, 30 de profondeur")]
    for x, y, t in lab:
        o.append(f'<text class="ptx" x="64" y="{y}">{escape(t)}</text>')
    o.append('<text class="ptx muted" x="64" y="70">ruban adhésif sur le foret = butée de profondeur</text>')
    return f'<svg viewBox="-4 -6 240 84" role="img" aria-label="Perçage type">{"".join(o)}</svg>' 


def contenu():
    deb = PL.debit()
    cartes = "".join(carte_piece(p) for p in deb)
    haut0 = M.MEUBLE_HAUT_ETAPES[0]
    legende = ('<p class="note">Plans des sous-ensembles : vue éclatée, puis chaque pièce à plat, face par face, cotes '
               'en mm depuis le coin en bas à gauche. <span class="lg fta"></span> on perce à travers (passage, fraisure '
               'ou lamage) · <span class="lg ftb"></span> avant-trou de la vis qui arrive · <span class="lg fent"></span> '
               'entaille.</p>')
    etapes = (bloc_etape(0) +
              '<h2 class="partie">Meuble bas</h2>' + legende + plans_sous_ensembles("bas") +
              "".join(bloc_etape(n) for n in range(1, haut0)) +
              '<h2 class="partie haut">Caisson haut</h2>' + plans_sous_ensembles("haut") +
              "".join(bloc_etape(n) for n in range(haut0, len(M.ETAPES))))
    return f"""<div class="kicker">Salle de bain · meuble linge {M.VERSION} · notice de montage</div>
<h1>Notice de montage</h1>
<p class="pitch">{len(M.ETAPES) - 1} étapes, des échelles au caisson haut. Dans chaque dessin, les pièces de l'étape sont en orange avec leur repère, celles déjà posées en blanc, et les trous à percer en points noirs ; le tableau Perçages de chaque étape donne forets, vis et positions.</p>

<h2>Le meuble</h2>
<div class="deux">
<div class="fig"><div class="vd">{vue_ensemble("d")}</div><p class="note">Meuble monté, vu depuis la salle de bain.</p></div>
<div class="fig"><div class="vd">{vue_eclatee("d")}</div><p class="note">Vue éclatée : échelles et tire-fonds de butée, rails, porte basculante en L, barres et sacs, plan, caisson haut.</p></div>
</div>

<h2>Pièces</h2>
<div class="cartes">{cartes}</div>
<p class="note">Cotes en mm (longueur × largeur × épaisseur). Liste complète avec usinages : <a href="{os.path.basename(PL.OUT)}#debit">page des plans, Débit</a>.</p>

<h2>Quincaillerie</h2>
<div class="hws">{puces_quinc(sum((Counter(q) for _, _, q in M.ETAPES), Counter()))}</div>

<h2>Outils</h2>
<h3>Meuble bas</h3>
<ul class="outils">{"".join(f"<li>{escape(o)}</li>" for o in OUTILS["bas"])}</ul>
<h3>Caisson haut</h3>
<ul class="outils">{"".join(f"<li>{escape(o)}</li>" for o in OUTILS["haut"])}</ul>

<h2>Fixer le caisson haut au mur</h2>
{fixation_haut()}

<h2>Comment percer</h2>
<div class="fig percage">{percage_type()}</div>
<ul class="pistes">
<li><b>Toujours deux forets</b> : dans la pièce qu'on traverse, un trou du diamètre de la vis (la vis serre les pièces au lieu de les écarter), fraisé pour noyer la tête ; dans la pièce reçue, un avant-trou plus fin (le bois massif ne fend pas, l'aggloméré n'éclate pas).</li>
<li><b>Où</b> : chaque étape dessine les trous (points noirs sur la face par où on perce) et donne leur position dans le tableau Perçages. En bout de pièce, deux trous dans l'axe, au tiers et aux deux tiers de la section.</li>
<li><b>Percer droit</b> : serrer les deux pièces en place (serre-joint, équerre), percer à travers la première jusque dans la seconde avec le foret fin, puis repercer la première au diamètre de la vis, fraiser, encoller, visser.</li>
<li><b>Profondeur</b> : un ruban adhésif sur le foret ; indispensable sous le plan de travail (8 mm au plus).</li>
</ul>

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
<script>{PL.ANCRES}</script>
<script>{PL.SCRIPT % {"cle": PL.CLE}}</script>
</body>
</html>
"""


if __name__ == "__main__":
    with open(OUT, "w", encoding="utf-8") as fh:
        fh.write(page())
    print(OUT)
