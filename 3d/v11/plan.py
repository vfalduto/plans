# Génère cuisine-v11.html (plan vu de dessus + coupe A-A sur le mur nord) depuis modele.py.
#
#   python3 3d/v11/plan.py
#
# Le plan et la coupe sont des projections des volumes du modèle : rien n'est dessiné à la main.

import math
import os
import re
import sys
from html import escape

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import modele as M  # noqa: E402

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
OUT = os.path.join(ROOT, "cuisine-v11.html")

COUPE_A = 90   # plan de coupe A-A (y), regard vers le nord
COUPE_B = 150  # plan de coupe B-B (y), regard vers le sud
COUPE_C = 315  # plan de coupe C-C (x), regard vers l'est


def f(v):
    return f"{v:g}"


def rect(x0, y0, x1, y1, cls):
    return f'<rect class="{cls}" x="{f(x0)}" y="{f(y0)}" width="{f(x1 - x0)}" height="{f(y1 - y0)}"/>'


def text(x, y, s, cls="lbl", anchor="middle", extra=""):
    return f'<text class="{cls}" x="{f(x)}" y="{f(y)}" text-anchor="{anchor}"{extra}>{escape(s)}</text>'


def cote_h(x0, x1, y, label=None, t=3):
    """Cote horizontale, texte au-dessus."""
    label = label or f(x1 - x0)
    return "".join([
        f'<line class="dim" x1="{f(x0)}" y1="{f(y)}" x2="{f(x1)}" y2="{f(y)}"/>',
        f'<line class="dim" x1="{f(x0)}" y1="{f(y - t)}" x2="{f(x0)}" y2="{f(y + t)}"/>',
        f'<line class="dim" x1="{f(x1)}" y1="{f(y - t)}" x2="{f(x1)}" y2="{f(y + t)}"/>',
        text((x0 + x1) / 2, y - 2.5, label, "dimt"),
    ])


def cote_v(y0, y1, x, label=None, t=3):
    """Cote verticale, texte à gauche, tourné."""
    label = label or f(abs(y1 - y0))
    ym = (y0 + y1) / 2
    return "".join([
        f'<line class="dim" x1="{f(x)}" y1="{f(y0)}" x2="{f(x)}" y2="{f(y1)}"/>',
        f'<line class="dim" x1="{f(x - t)}" y1="{f(y0)}" x2="{f(x + t)}" y2="{f(y0)}"/>',
        f'<line class="dim" x1="{f(x - t)}" y1="{f(y1)}" x2="{f(x + t)}" y2="{f(y1)}"/>',
        text(x - 2.5, ym, label, "dimt", extra=f' transform="rotate(-90 {f(x - 2.5)} {f(ym)})"'),
    ])


def aire(poly):
    """Aire d'un polygone (formule du lacet), en cm²."""
    return abs(sum(x0 * y1 - x1 * y0 for (x0, y0), (x1, y1) in zip(poly, poly[1:] + poly[:1]))) / 2


def pts(poly):
    return " ".join(f"{f(x)},{f(y)}" for x, y in poly)


# ------------------------------------------------------------------ plan vu de dessus
PLAN_CLS = {"mur": "w", "allege": "win", "tech": "tech", "socle": None,
            "caisson_haut": "upper", "facade_haut": None, "plan": "pt", "plaque": "vitro",
            "aspiration": "asp", "evier": "inox", "cuve": "cuve", "mitigeur": "inox",
            "colonne": "tall", "facade_col": "fac", "four": "fac", "porte": None,
            "caisson": "cab", "facade": "fac", "linteau": None, "cloison": "neuf", "porte_plan": None,
            "table": "tbl", "pied": None, "chaise": "stool", "fileur": None, "banquette": "stool"}


def batons_rompus(w=8, l=32):
    """Motif de parquet en bâtons rompus : lames w × l, période 2l × 2l, posé à 45°."""
    p = 2 * l
    r = []
    for j in range(-4, 5):
        for n in range(-2 * p // w, 2 * p // w):
            ox, oy = j * l + n * w, -j * l + n * w
            for x, y, dx, dy in ((ox, oy, l, w), (ox, oy + w, w, l)):
                if x < p and y < p and x + dx > 0 and y + dy > 0:
                    r.append(f'<rect class="lame" x="{x}" y="{y}" width="{dx}" height="{dy}"/>')
    return (f'<pattern id="br" width="{p}" height="{p}" patternUnits="userSpaceOnUse" '
            f'patternTransform="rotate(-45)">{"".join(r)}</pattern>')


def plan_svg():
    o = [f"<defs>{batons_rompus()}</defs>"]
    o.append(f'<polygon class="floorbg" points="{pts(M.SOL_PARQUET)}"/>')
    o.append(f'<polygon fill="url(#br)" points="{pts(M.SOL_PARQUET)}"/>')
    o.append(f'<polygon class="ciment" points="{pts(M.SOL_CIMENT)}"/>')
    for b in M.CLOISONS_DEPOSEES:
        o.append(rect(b.x0, b.y0, b.x1, b.y1, "depose"))
    for nom, x, y in M.ZONES:
        for k, ligne in enumerate(nom.split("\n")):
            o.append(text(x, y + 8 * k, ligne, "lbls muted"))
    o.append(f'<polygon class="wc" points="{pts(M.WC)}"/>')
    o.append(text(438, 185, "WC", "lbl muted"))
    # volumes, du plus bas au plus haut
    for b in sorted(M.ENVELOPPE + M.MEUBLES, key=lambda b: b.z1):
        cls = PLAN_CLS[b.role]
        if isinstance(b, M.Cyl) and cls:
            o.append(f'<circle class="{cls}" cx="{f(b.cx)}" cy="{f(b.cy)}" r="{f(b.r)}"/>')
        elif cls:
            o.append(rect(b.x0, b.y0, b.x1, b.y1, cls))
    # fenêtre coulissante : deux vantaux dans l'épaisseur du mur
    fe = M.FENETRE
    o.append(f'<line class="glass" x1="-7" y1="{fe["y0"]}" x2="-7" y2="{(fe["y0"] + fe["y1"]) / 2 + 2}"/>')
    o.append(f'<line class="glass" x1="-13" y1="{(fe["y0"] + fe["y1"]) / 2 - 2}" x2="-13" y2="{fe["y1"]}"/>')
    # porte d'entrée coulissante côté cuisine, vers l'ouest (fermée ; ouverte en tireté)
    en = M.ENTREE
    (hx, hy), w = en["charniere"], en["vantail"]
    o.append(f'<line class="doorleaf" x1="{f(hx)}" y1="{f(hy)}" x2="{f(hx)}" y2="{f(hy - w)}"/>')
    o.append(f'<path class="swing" d="M{f(hx - w)} {f(hy)} A{f(w)} {f(w)} 0 0 1 {f(hx)} {f(hy - w)}"/>')
    o.append(text((en["x0"] + en["x1"]) / 2, 270, "Entrée", "lbls"))
    # ballon
    bl = M.BALLON
    o.append(f'<circle class="ecs" cx="{f(bl.cx)}" cy="{f(bl.cy)}" r="{f(bl.r)}"/>')
    o.append(text(bl.cx, bl.cy + 2, "Ballon ECS", "lblx"))
    o.append(text(426, 28, "chute", "lblx muted"))
    # numéros des meubles
    for b in M.MEUBLES:
        if b.role == "caisson" and b.y0 > 0:  # meubles du mur est : étiquette au centre
            o.append(text((b.x0 + b.x1) / 2, (b.y0 + b.y1) / 2 + 3, b.etiq, "lblb"))
        elif b.role == "caisson":
            nom, _, equip = b.etiq.partition(" ")
            o.append(text((b.x0 + b.x1) / 2, 74, nom, "lblb"))
            if equip:
                o.append(text((b.x0 + b.x1) / 2, 82, equip, "lbls"))
        if b.role == "banquette" and b.etiq:
            o.append(text((b.x0 + b.x1) / 2, b.y1 - 6, b.etiq, "lbls"))
        if b.role == "colonne" and b.etiq:
            o.append(text((b.x0 + b.x1) / 2, (b.y0 + b.y1) / 2 + 3, b.etiq, "lbl", extra=' font-weight="700"'))
    for b in M.MEUBLES:
        if b.role == "plaque":
            o.append(text((b.x0 + b.x1) / 2, 50, "induction", "lblx onDark"))
        if b.role == "cuve":
            o.append(text((b.x0 + b.x1) / 2, b.y1 - 3, "évier", "lblx"))
    # cellier : baie de 72, porte à définir
    bc = M.BAIE_CELLIER
    o.append(rect(bc["x0"], bc["y0"], bc["x1"], bc["y1"], "ghost"))
    o.append(cote_v(bc["y0"], bc["y1"], bc["x1"] + 8, f'baie {f(bc["y1"] - bc["y0"])}'))
    o.append(text(bc["x0"] - 3, (bc["y0"] + bc["y1"]) / 2, "porte à définir", "lblx muted", "middle",
                  extra=f' transform="rotate(-90 {f(bc["x0"] - 3)} {f((bc["y0"] + bc["y1"]) / 2)})"'))
    # réseaux d'eau
    for role, _, p, _, _ in M.RESEAUX:
        o.append(f'<polyline class="{"pin" if role == "alim" else "pout"}" points="{pts(p)}"/>')
    o.append(f'<circle class="chute" cx="{f(M.CHUTE[0])}" cy="{f(M.CHUTE[1])}" r="4.5"/>')
    o.append(f'<circle class="nourrice" cx="{f(M.NOURRICE[0])}" cy="{f(M.NOURRICE[1])}" r="2.5"/>')
    # ouvertures de l'électroménager
    for kind, nom, d in M.OUVERTURES:
        if kind == "abattant":
            x0, x1, y0, y1 = d
            o.append(rect(x0, y0, x1, y1, "swingz"))
            o.append(text((x0 + x1) / 2, (y0 + y1) / 2 + 2, f"porte {nom} abattue", "lblx muted"))
        else:
            (hx, hy), w, sens = d
            ex = hx + w if sens == "est" else hx - w
            o.append(f'<line class="doorleaf" x1="{f(hx)}" y1="{f(hy)}" x2="{f(hx)}" y2="{f(hy - w)}"/>')
            o.append(f'<path class="swing" d="M{f(ex)} {f(hy)} A{f(w)} {f(w)} 0 0 0 {f(hx)} {f(hy - w)}"/>')
            o.append(text(hx + 3, hy - w + 8, f"porte {nom} 90°", "lblx muted", "start"))
    # cellier : surface et volume
    surf = aire(M.CELLIER_SOL) / 1e4
    vol = surf * M.H / 100
    bl = M.BALLON
    net = vol - math.pi * (bl.r / 100) ** 2 * (bl.z1 - bl.z0) / 100
    for k, ligne in enumerate((f"{surf:.2f} m²", f"{vol:.2f} m³ brut", f"≈ {net:.1f} m³ net")):
        o.append(text(380, 72 + 7 * k, ligne.replace(".", ","), "lblx"))
    # table
    o.append(text(M.TABLE["cx"], M.TABLE["cy"] + 3, f'Ø {f(2 * M.TABLE["r"])}', "lblb"))
    # four (C1) / B1 : entre façades, et porte du four abattue
    yb = M.P_CAISSON + M.FACADE
    o.append(cote_v(yb, M.COL_Y0, M.COL_X0 + 54))
    o.append(cote_v(yb, M.COL_Y0 - 60, M.COL_X0 + 12))
    # triangle d'activité
    tp = [p for _, p in M.TRIANGLE]
    o.append(f'<polygon class="tri" points="{pts(tp)}"/>')
    for a, b in zip(tp, tp[1:] + tp[:1]):
        d = math.dist(a, b)
        mx, my = (a[0] + b[0]) / 2, (a[1] + b[1]) / 2
        o.append(f'<rect class="tribg" x="{f(mx - 11)}" y="{f(my - 6)}" width="22" height="10" rx="2"/>')
        o.append(text(mx, my + 1.5, f"{d:.0f}", "trit"))
    for _, (x, y) in M.TRIANGLE:
        o.append(f'<circle class="triv" cx="{f(x)}" cy="{f(y)}" r="2.5"/>')
    # coupe A-A
    for y, nom, d in ((COUPE_A, "A", -9), (COUPE_B, "B", 9)):
        o.append(f'<line class="sec" x1="-30" y1="{y}" x2="500" y2="{y}"/>')
        for x in (-30, 500):
            o.append(f'<path class="secm" d="M{x - 4} {y} l4 {d} l4 {-d} z"/>')
            o.append(text(x, y - d * 1.2 + 3, nom, "sect"))
    x = COUPE_C
    o.append(f'<line class="sec" x1="{x}" y1="-82" x2="{x}" y2="300"/>')
    for y in (-82, 300):
        o.append(f'<path class="secm" d="M{x} {y - 4} l9 4 l-9 4 z"/>')
        o.append(text(x - 7, y + 4, "C", "sect"))
    # cotes : chaîne du mur nord, total des meubles, longueur de la pièce
    caissons = [b for b in M.MEUBLES if b.role == "caisson" and b.y0 == 0]
    o.append(cote_h(0, caissons[0].x0, -30))
    for b in caissons:
        o.append(cote_h(b.x0, b.x1, -30))
    hauts = [b for b in M.MEUBLES if b.role == "caisson_haut"]
    o.append(cote_h(0, hauts[0].x0, -48))
    for b in hauts:
        o.append(cote_h(b.x0, b.x1, -48))
    for b in hauts:
        o.append(text((b.x0 + b.x1) / 2, 10, b.etiq, "lbls muted"))
    cols = [b for b in M.MEUBLES if b.role == "colonne" and b.nom.startswith("caisson_c")]
    o.append(chaine(cols, 268 + 10, lambda x: x))
    # porte d'entrée coulissante : baie, vantail, course
    o.append(cote_h(en["x0"], en["x1"], 282, f'baie {f(en["x1"] - en["x0"])}'))
    (ex, ey), ew = en["charniere"], en["vantail"]
    o.append(cote_v(ey - ew, ey, ex + 6, f'vantail {f(ew)}'))
    o.append(cote_v(M.COL_Y0, M.COL_DOS, M.COL_X0 + 8))
    o.append(cote_h(0, 434, -66))
    o.append(text(-4, -27, "bas", "lblx muted", "end"))
    o.append(text(-4, -45, "hauts", "lblx muted", "end"))
    o.append(cote_v(0, M.P_CAISSON + M.FACADE, caissons[-1].x1 - 8))
    # mur ouest
    o.append(cote_v(0, fe["y0"], -34))
    o.append(cote_v(fe["y0"], fe["y1"], -34, f'fenêtre {f(fe["y1"] - fe["y0"])}'))
    o.append(cote_v(fe["y1"], 252, -34))
    o.append(cote_v(0, 252, -52))
    # nord
    o.append('<g transform="translate(470 -60)"><path class="dark" d="M0 -10 L5 4 L0 1 L-5 4 Z"/>'
             + text(0, 14, "N", "lblb") + "</g>")
    return (f'<svg viewBox="-75 -90 590 410" role="img" aria-label="Plan vu de dessus, pièce vide, '
            f'6 meubles bas et 5 meubles hauts de 60 au mur nord">{"".join(o)}</svg>')


# ------------------------------------------------------------------ coupes
COUPE_CLS = {"mur": ("bgwall", "w"), "allege": ("bgwall", "w"), "linteau": ("wallv", "w"),
             "caisson_haut": ("cab", "cab"), "facade_haut": ("fac", "fac"), "plan": ("pt", "pt"),
             "plaque": ("dark", "dark"), "aspiration": ("dark", "dark"), "evier": ("inox", "inox"),
             "cuve": ("inox", "inox"), "mitigeur": ("inox", "inox"), "ballon": ("ecs", "ecs"),
             "tech": ("tech", "tech"), "socle": ("plinth", "plinth"),
             "caisson": ("cab", "cab"), "facade": ("fac", "fac"), "porte": ("leaf", "leaf"),
             "colonne": ("tall", "tall"), "cloison": ("wallv", "neuf"),
             "fileur": ("fac", "fac"), "banquette": ("stool", "stool"), "table": ("tbl", "tbl"), "pied": ("tbl", "tbl"), "chaise": ("stool", "stool"), "facade_col": ("fac", "fac"), "four": ("dark", "dark")}


# Regard d'une coupe : (axe coupé, sens de la profondeur, miroir de l'axe horizontal)
# nord : coupe en y, on regarde vers les y décroissants, l'ouest à gauche ; sud : l'est à gauche ;
# est : coupe en x, on regarde vers les x croissants, le nord à gauche (u = y).
REGARDS = {"nord": ("y", -1, False), "sud": ("y", 1, True), "est": ("x", 1, False)}
VERS = {"nord": "le nord", "sud": "le sud", "est": "l'est"}


def uv(b, axe):
    """(u0, u1, d0, d1) : étendue horizontale à l'écran et profondeur, selon l'axe de coupe."""
    return (b.x0, b.x1, b.y0, b.y1) if axe == "y" else (b.y0, b.y1, b.x0, b.x1)


def chaine(blocs, y, X, axe="y", origine=0):
    """Chaîne de cotes depuis le mur (origine) puis meuble par meuble, en coordonnées d'écran X(u)."""
    o = []
    bords = [origine] + [uv(b, axe)[0] for b in blocs[:1]] + [uv(b, axe)[1] for b in blocs]
    for a, b in zip(bords, bords[1:]):
        u, v = sorted((X(a), X(b)))
        o.append(cote_h(u, v, y, f(abs(b - a))))
    return "".join(o)


def coupe_svg(cut, regard, umin, umax, chaines, hauteurs, xh, extra=None, origine=0):
    """Coupe au plan cut (y pour nord/sud, x pour est). Vers le sud, l'est est à gauche : u écran = umin + umax - x."""
    axe, sens, miroir = REGARDS[regard]
    X = (lambda u: umin + umax - u) if miroir else (lambda u: u)
    o, etiquettes = [], []
    tous = M.ENVELOPPE + M.MEUBLES + [M.BALLON]

    def vu(b):
        u0, u1, d0, d1 = uv(b, axe)
        return (d1 > cut if sens > 0 else d0 < cut) and u1 > umin and u0 < umax

    vus = [b for b in tous if vu(b)]
    # du plus loin au plus proche, les éléments coupés en dernier
    vus.sort(key=lambda b: (uv(b, axe)[2] < cut < uv(b, axe)[3], -uv(b, axe)[2] if sens > 0 else uv(b, axe)[3]))
    for b in vus:
        u0, u1, d0, d1 = uv(b, axe)
        coupe = d0 < cut < d1
        u, v = sorted((X(max(u0, umin)), X(min(u1, umax))))
        o.append(rect(u, -b.z1, v, -b.z0, COUPE_CLS[b.role][1 if coupe else 0]))
        xm = (u + v) / 2
        if b.role == "allege" and coupe:
            o.append(text(xm, -150, "fenêtre", "lblx", extra=f' transform="rotate(-90 {f(xm)} -150)"'))
        if b.role == "ballon":
            etiquettes.append(text(xm, -(b.z0 + b.z1) / 2, "Ballon", "lblx"))
        if b.role == "four":
            etiquettes.append(text(xm, -(b.z0 + b.z1) / 2 + 2, "four", "lblx onDark"))
        if getattr(b, "etiq", ""):
            zm = (b.z0 + b.z1) / 2 if b.role != "colonne" else 200
            nom, _, equip = b.etiq.partition(" ")
            etiquettes.append(text(xm, -zm + 3, nom, "lblb"))
            if equip and b.role == "caisson":
                etiquettes.append(text(xm, -zm + 12, equip, "lbls"))
    # une seule étiquette par position : celle de l'élément le plus proche (ajoutée en dernier) l'emporte
    o += list({(e.split('x="')[1].split('"')[0], e.split('y="')[1].split('"')[0]): e for e in etiquettes}.values())
    if extra:
        o += extra(X)
    o.append(f'<line class="floorl" x1="{f(umin)}" y1="0" x2="{f(umax)}" y2="0"/>')
    o.append(f'<line class="ceil" x1="{f(umin)}" y1="{-M.H}" x2="{f(umax)}" y2="{-M.H}"/>')
    for blocs, y in chaines:
        o.append(chaine(blocs, y, X, axe, origine))
    zs = [0] + hauteurs + [M.H]
    for z0, z1 in zip(zs, zs[1:]):
        o.append(cote_v(-z0, -z1, xh))
    o.append(cote_v(0, -M.H, umin - 14))
    return (f'<svg viewBox="{f(umin - 40)} -285 {f(umax - umin + 80)} 337" role="img" '
            f'aria-label="Coupe à {axe} {f(cut)}, regard vers {VERS[regard]}">{"".join(o)}</svg>')


def coupe_a():
    bas = [b for b in M.MEUBLES if b.role == "caisson" and b.y0 == 0]
    hauts = [b for b in M.MEUBLES if b.role == "caisson_haut"]
    return coupe_svg(COUPE_A, "nord", -20, 494, [(bas, 22), (hauts, -M.H - 8)],
                     [M.SOCLE, M.CAISSON_H, M.PT_Z1, M.HAUT_Z0, M.HAUT_Z1], -50)


def coupe_b():
    cols = [b for b in M.MEUBLES if b.role == "colonne" and b.nom.startswith("caisson_c")]
    xmin, xmax = -20, 392
    en = M.ENTREE
    v = next(b for b in M.ENVELOPPE if b.nom == "entree_vantail")

    def porte(X):
        u0, u1 = sorted((X(en["x0"]), X(en["x1"])))
        w0, w1 = sorted((X(v.x0), X(v.x1)))
        return [cote_h(u0, u1, 38, f'baie {f(en["x1"] - en["x0"])}'),
                cote_h(w0, w1, -v.z1 - 6, f'vantail {f(v.x1 - v.x0)} × {f(v.z1 - v.z0)}'),
                cote_v(0, -en["h"], w0 - 8, f'baie h {en["h"]}')]

    return coupe_svg(COUPE_B, "sud", xmin, xmax, [(cols, 22)],
                     [M.SOCLE, 88, 148, M.COL_Z1], xmin - 30, porte)


def coupe_c():
    est = sorted([b for b in M.MEUBLES if b.nom in ("caisson_e1", "caisson_e2")], key=lambda b: b.y0)
    bc = M.BAIE_CELLIER

    def cellier(X):
        return [cote_h(X(bc["y0"]), X(bc["y1"]), -bc["h"] + 14, f'baie cellier {f(bc["y1"] - bc["y0"])}')]

    return coupe_svg(COUPE_C, "est", -20, 262, [(est, 22)],
                     [M.SOCLE, M.CAISSON_H, M.CAISSON_H + 4, M.COL_Z1], -50, cellier, origine=M.BAIE_CELLIER["y1"] + 7)


# ------------------------------------------------------------------ page
CSS = """
:root{
  --paper:#F7F8F6; --ink:#1D2A33; --muted:#5E6B73; --line:#C9D0D4; --wood:#B07A45;
  --water:#2F7FB5; --tri:#C8412C; --panel:#FFFFFF; --cab:#ECE6DA; --tall:#D8CFBD;
  --tech:#E1E6E9; --glass:#CFE4F2; --cement:#C9CBCA; color-scheme:light;
}
@media (prefers-color-scheme: dark){
  :root:not([data-theme="light"]){
    --paper:#141A1F; --ink:#E4EAED; --muted:#9AA7AE; --line:#34414A; --wood:#C9925A;
    --water:#5AA8DE; --tri:#E8664F; --panel:#1B2329; --cab:#2A3338; --tall:#394449;
    --tech:#26303A; --glass:#1F3A4E; --cement:#3A3E40; color-scheme:dark;
  }
}
:root[data-theme="dark"]{
  --paper:#141A1F; --ink:#E4EAED; --muted:#9AA7AE; --line:#34414A; --wood:#C9925A;
  --water:#5AA8DE; --tri:#E8664F; --panel:#1B2329; --cab:#2A3338; --tall:#394449;
  --tech:#26303A; --glass:#1F3A4E; --cement:#3A3E40; color-scheme:dark;
}
*{box-sizing:border-box}
html,body{margin:0}
body{background:var(--paper);color:var(--ink);font-family:Archivo,system-ui,-apple-system,"Segoe UI",Roboto,sans-serif;line-height:1.55;font-size:16px}
.wrap{max-width:1120px;margin:0 auto;padding:28px 16px 64px}
.kicker{font-family:"JetBrains Mono",ui-monospace,Menlo,monospace;font-size:12px;letter-spacing:.08em;text-transform:uppercase;color:var(--muted)}
h1{font-size:clamp(28px,5vw,44px);line-height:1.08;margin:6px 0 12px;font-weight:800;letter-spacing:-.01em}
h2{font-size:22px;margin:44px 0 10px;font-weight:700}
.pitch{font-size:18px;max-width:780px}
.fig{background:var(--panel);border:1px solid var(--line);border-radius:12px;padding:12px;margin:14px 0}
.scroll{overflow-x:auto;-webkit-overflow-scrolling:touch}
.scroll svg{display:block;width:100%;min-width:720px;height:auto}
.cap{font-size:13px;color:var(--muted);margin:8px 4px 2px}
.note{font-size:13px;color:var(--muted)}
.grid2{display:grid;grid-template-columns:repeat(auto-fit,minmax(300px,1fr));gap:16px}
h3{font-size:16px;margin:4px 4px 8px}
table{border-collapse:collapse;width:100%;font-size:14px}
th,td{text-align:left;padding:7px 8px;border-bottom:1px solid var(--line);vertical-align:top}
.mono{font-family:"JetBrains Mono",ui-monospace,monospace;white-space:nowrap}
svg text{font-family:Archivo,system-ui,sans-serif;fill:var(--ink)}
.w{fill:var(--ink)}
.bgwall{fill:var(--line);fill-opacity:.35}
.wallv{fill:#D5DADD;stroke:var(--muted);stroke-width:.5}
.floorbg{fill:var(--wood);fill-opacity:.13}
.wc{fill:var(--line);fill-opacity:.55}
.lame{fill:none;stroke:var(--wood);stroke-width:.5;stroke-opacity:.5}
.ciment{fill:var(--cement)}
.depose{fill:none;stroke:var(--muted);stroke-width:.8;stroke-dasharray:4 3}
.win{fill:var(--glass);stroke:var(--ink);stroke-width:.7}
.glass{stroke:var(--water);stroke-width:1.4}
.tech{fill:var(--tech);stroke:var(--ink);stroke-width:.7;stroke-dasharray:3 2}
.cab{fill:var(--cab);stroke:var(--ink);stroke-width:.7}
.fac{fill:var(--tall);stroke:var(--ink);stroke-width:.7}
.plinth{fill:var(--tall);stroke:var(--ink);stroke-width:.6}
.ecs{fill:var(--panel);stroke:var(--water);stroke-width:1.2}
.leaf{fill:var(--wood);stroke:var(--ink);stroke-width:.6}
.ghost{fill:none;stroke:var(--muted);stroke-width:.8;stroke-dasharray:4 3}
.dark{fill:var(--ink)}
.pt{fill:var(--panel);fill-opacity:.55;stroke:var(--ink);stroke-width:1.1}
.vitro{fill:var(--ink);stroke:var(--ink);stroke-width:.6}
.asp{fill:var(--muted)}
.inox{fill:var(--tech);stroke:var(--ink);stroke-width:.6}
.cuve{fill:var(--panel);stroke:var(--ink);stroke-width:.7}
.onDark{fill:var(--paper)}
.tall{fill:var(--tall);stroke:var(--ink);stroke-width:.8}
.neuf{fill:var(--wood);stroke:var(--ink);stroke-width:.6}
.pin{fill:none;stroke:var(--water);stroke-width:1.6}
.pout{fill:none;stroke:var(--water);stroke-width:1.6;stroke-dasharray:5 3}
.chute{fill:var(--panel);stroke:var(--water);stroke-width:1.6}
.nourrice{fill:var(--water)}
.tri{fill:var(--tri);fill-opacity:.07;stroke:var(--tri);stroke-width:1.4}
.triv{fill:var(--tri)}
.tribg{fill:var(--panel);stroke:var(--tri);stroke-width:.6}
.trit{fill:var(--tri);font-family:"JetBrains Mono",monospace !important;font-size:7px;font-weight:600;text-anchor:middle}
.tbl{fill:var(--wood);fill-opacity:.5;stroke:var(--ink);stroke-width:.9}
.stool{fill:var(--wood);fill-opacity:.28;stroke:var(--ink);stroke-width:.7}
.swingz{fill:var(--tri);fill-opacity:.05;stroke:var(--muted);stroke-width:.7;stroke-dasharray:3 2}
.swing{fill:none;stroke:var(--muted);stroke-width:.7;stroke-dasharray:2 2}
.doorleaf{stroke:var(--ink);stroke-width:2}
td.num,th.num{text-align:right;font-family:"JetBrains Mono",ui-monospace,monospace;white-space:nowrap}
tfoot td{font-weight:700}
.upper{fill:none;stroke:var(--ink);stroke-width:.8;stroke-dasharray:3 2}
.dim{stroke:var(--muted);stroke-width:.6;fill:none}
.dimt{fill:var(--muted);font-family:"JetBrains Mono",ui-monospace,monospace !important;font-size:8px}
.lbl{font-size:7.5px}.lbls{font-size:6.5px}.lblx{font-size:5px}.lblb{font-size:9px;font-weight:700}
.muted{fill:var(--muted)}
.sec{stroke:var(--tri);stroke-opacity:.3;stroke-width:.9;stroke-dasharray:10 3 2 3;fill:none}
.secm{fill:var(--tri);fill-opacity:.45}
.sect{fill:var(--tri);fill-opacity:.55;font-weight:800;font-size:11px}
.floorl{stroke:var(--ink);stroke-width:2}
.ceil{stroke:var(--muted);stroke-width:1;stroke-dasharray:6 4}
.vbar{position:sticky;top:0;z-index:5;display:flex;flex-wrap:wrap;align-items:center;gap:6px;padding:8px 16px;background:var(--paper);border-bottom:1px solid var(--line);font-family:"JetBrains Mono",ui-monospace,monospace;font-size:12px}
.vbar .back{color:var(--ink);text-decoration:none;font-weight:600;margin-right:14px}
.vbar .back:hover{text-decoration:underline}
.vbar span{color:var(--muted);text-transform:uppercase;letter-spacing:.08em;margin-right:4px}
.vbar button{font:inherit;color:var(--ink);background:var(--panel);border:1px solid var(--line);border-radius:6px;padding:4px 10px;cursor:pointer}
.vbar button[aria-pressed="true"]{background:var(--ink);color:var(--paper);border-color:var(--ink)}
@media (max-width:480px){ body{font-size:15px} }
"""


def table_rangement(lignes):
    rows = "".join(f'<tr><td>{escape(n)}</td><td class="mono">{escape(d)}</td><td class="num">{v:.0f}</td></tr>'
                   for n, v, d in lignes)
    total = sum(v for _, v, _ in lignes)
    return (f'<table><thead><tr><th>Meuble</th><th>Cotes</th><th class="num">L</th></tr></thead>'
            f'<tbody>{rows}</tbody><tfoot><tr><td colspan="2">Total fermé</td><td class="num">{total:.0f}</td></tr>'
            f'</tfoot></table>')


def contenu():
    v11 = sum(v for _, v, _ in M.RANGEMENT_V11)
    p9a = sum(v for _, v, _ in M.RANGEMENT_P9A)
    caissons = [b for b in M.MEUBLES if b.role == "caisson" and b.y0 == 0]
    x0, x1 = caissons[0].x0, caissons[-1].x1
    chute = next(b for b in M.ENVELOPPE if b.nom == "coffrage_chute")
    hauts = [b for b in M.MEUBLES if b.role == "caisson_haut"]
    cols = [b for b in M.MEUBLES if b.role == "colonne" and b.nom.startswith("caisson_c")]
    tp = M.TRIANGLE
    cotes_tri = [math.dist(a[1], b[1]) for a, b in zip(tp, tp[1:] + tp[:1])]
    tri = ", ".join(f"{a[0]} → {b[0]} {d:.0f}" for (a, b), d in zip(zip(tp, tp[1:] + tp[:1]), cotes_tri))
    lignes = "".join(f'<tr><td class="mono">{v}</td><td class="mono">{d}</td><td>{escape(c)}</td></tr>'
                     for v, d, c in M.CHANGEMENTS)
    return f"""<div class="kicker">Cuisine · {M.VERSION}</div>
<h1>Plan de la cuisine V11</h1>
<p class="pitch">Nouveau départ depuis la pièce vide. Le plan et la coupe sont générés depuis le modèle 3D : une seule source, aucune cote reportée à la main.</p>

<h2>Plan</h2>
<div class="fig"><div class="scroll">{plan_svg()}</div>
<p class="cap">Échelle : 1 unité = 1 cm. Pièce vide : chambre et ancien cellier ouverts, sans cloison. Restent la fenêtre coulissante du mur ouest (y 58 → 200), la porte d'entrée (baie x 228 → 306), le décroché de l'angle sud-est, le coffrage de la chute, le ballon et le WC. <b>Sols</b> : parquet chêne en bâtons rompus dans l'ancienne chambre (x 0 → 325), gris ciment dans l'ancien cellier et l'ancien placard (à partir de x 325) ; les cloisons déposées du relevé d'origine sont en tireté (chambre / cellier x 325 → 335, cellier / placard y 100 → 110). <b>Mur nord</b> : {len(caissons)} meubles bas de 60 (x {f(x0)} → {f(x1)}), à {f(M.ECART_OUEST)} du mur ouest ; caisson P{M.P_CAISSON} + façade {M.FACADE}, profondeur {M.P_CAISSON + M.FACADE}, sous un plan de travail de 4 (P62, débord de 2). <b>Induction</b> 60 à aspiration intégrée sur B{M.B_PLAQUE} (x {f(M.sur_bas(M.B_PLAQUE)[0])} → {f(M.sur_bas(M.B_PLAQUE)[1])}) ; <b>évier</b> inox 1 bac 56 × 50 (bac 40 × 40) sur B{M.B_EVIER} (x {f(M.sur_bas(M.B_EVIER)[0])} → {f(M.sur_bas(M.B_EVIER)[1])}), mitigeur derrière le bac ; le LV (B{M.B_LV}) entre les deux, sous 60 de plan. Il reste {f(chute.x0 - x1)} entre le dernier meuble et le coffrage de la chute (x {f(chute.x0)}). <b>Mur sud</b> : colonnes C1 (four) et C2 (frigo) de 60, P60, x {f(cols[0].x0)} → {f(cols[-1].x1)}, alignées sur le bord ouest du vantail d'entrée fermé (x {f(M.COL_X1)}, 2 avant le montant de la baie) ; elles sont avancées de 12 (façades y {f(M.COL_Y0)}, contre le mur sud). <b>Porte d'entrée</b> : battante, vantail {f(M.ENTREE["vantail"])} × {M.ENTREE["h"]}, charnières à l'est (elle pousse à droite vue du couloir) ; ouverte à 90°, elle se range le long de l'aplomb du montant est (x {f(M.ENTREE["charniere"][0])}, jusqu'à y {f(M.ENTREE["charniere"][1] - M.ENTREE["vantail"])}), à {f(M.X_MUR_EST - M.P_EST - M.FACADE - M.ENTREE["charniere"][0])} de E2. <b>Mur est</b> : deux meubles bas de 60 en profondeur réduite (caisson P{M.P_EST} + façade 2, P40), E1 y 120 → 180 et E2 y 180 → 240, contre le mur du WC, du décroché vers le nord, sous un plan de travail de 4 (P42). Devant eux, il reste {f(M.X_MUR_EST - M.P_EST - M.FACADE - 2 - M.ENTREE["x1"])} entre le plan et l'aplomb du montant est de la porte d'entrée (x 306). <b>Équipements</b> : poubelles de tri sous l'évier (B{M.B_EVIER}), lave-vaisselle 60 tout intégrable (B{M.B_LV}). <b>Triangle d'activité</b> (rouge ; centres de la plaque et de l'évier, milieu de la façade du frigo) : {tri}, total {f(round(sum(cotes_tri)))} cm. <b>Réseaux</b> (bleu, dans le vide technique derrière les caissons) : alimentation EF/EC en trait plein depuis la nourrice sous le ballon, le long du mur nord, avec un piquage pour le LV ; évacuations en tireté de l'évier (siphon, axe x {f(M.SIPHON[0])}) et du LV vers la chute (cercle, coffrage x 418 → 434), longueur ≈ {f(M.EVAC_LONGUEUR)} : à 2 cm/m, 5 cm de pente, par exemple de h 45 sous le siphon à h 40 à la chute. Les réseaux traversent la cloison du cellier dans son trumeau nord. <b>Cellier</b> : cloison de 7 à {f(M.BAIE_CELLIER["x0"] - x1)} de B5 (x {f(M.BAIE_CELLIER["x0"])} → {f(M.BAIE_CELLIER["x1"])}), du mur nord à y 120, puis retour vers l'est contre le nord de E1 (y 113 → 120) jusqu'au mur du WC ; baie de {f(M.BAIE_CELLIER["y1"] - M.BAIE_CELLIER["y0"])} face ouest (y {f(M.BAIE_CELLIER["y0"])} → {f(M.BAIE_CELLIER["y1"])}, h {M.BAIE_CELLIER["h"]}), juste au sud du plan de travail (y 62), porte à définir ; trumeau nord de {f(M.BAIE_CELLIER["y0"])}, où passent les réseaux. Une porte battante de 50 côté cuisine balaierait le devant de B5 : coulissante, pliante ou battante vers le cellier à étudier. <b>Coin repas</b> : banquette du mur ouest jusqu'à C1 (x 0 → {f(M.COL_X0)}, 50 de profondeur : assise 45 à h 45 avec coffre, dossier 5 à h 85), table ronde Ø {f(2 * M.TABLE["r"])} à pied tulipe devant (centre x {f(M.TABLE["cx"])}, y {f(M.TABLE["cy"])}), qui recouvre l'assise de 15 ; une chaise en face, glissée de {M.GLISSE}, avec un recul de {f(M.CHAISE_Y0 - M.P_CAISSON - M.FACADE)} jusqu'au front de B1. La banquette s'arrête à y {f(M.BANQ["y0"])}, au sud de la fenêtre (y 200). <b>Ouvertures</b> : porte du LV abattue (y 60 → 132), porte du four abattue (x {f(M.COL_X0)} → {f(M.COL_X0 + 60)}, y {f(M.COL_Y0 - 60)} → {f(M.COL_Y0)}), porte du frigo à 90°, charnières à l'est, côté porte d'entrée, ouverte vers l'ouest. Elle touche la porte du four abattue à x {f(M.COL_X0 + 60)} : on ne les ouvre pas en même temps. <b>Meubles hauts</b> (tireté) : {len(hauts)} de 60, x {f(hauts[0].x0)} → {f(hauts[-1].x1)}, décalés d'un demi-meuble par rapport aux bas (ils partent du milieu du meuble 1) ; caisson P{M.P_HAUT} + façade {M.FACADE}.</p></div>

<h2>Coupe A-A · mur nord</h2>
<div class="fig"><div class="scroll">{coupe_a()}</div>
<p class="cap">Coupe à y {COUPE_A}, regard vers le nord. Socle {M.SOCLE}, caissons bas h {M.SOCLE} → {M.CAISSON_H}, plan de travail 4 (h {M.CAISSON_H} → {M.PT_Z1}), meubles hauts h {M.HAUT_Z0} → {M.HAUT_Z1}, fileur de {M.H - M.HAUT_Z1} jusqu'au plafond ({M.H}).</p></div>

<h2>Coupe B-B · mur sud</h2>
<div class="fig"><div class="scroll">{coupe_b()}</div>
<p class="cap">Coupe à y {COUPE_B}, regard vers le sud : l'est est à gauche. <b>Porte d'entrée</b> : baie {f(M.ENTREE["x1"] - M.ENTREE["x0"])} × {M.ENTREE["h"]}, porte battante, vantail {f(M.ENTREE["vantail"])} × {M.ENTREE["h"]} dans une huisserie, charnières à l'est (à gauche sur la coupe), ouverture vers la cuisine. Colonnes P{M.P_CAISSON + M.FACADE}, socle {M.SOCLE}, dessus à {M.COL_Z1} comme les meubles hauts, fileur de {M.H - M.COL_Z1} jusqu'au plafond. <b>C1</b> : deux tiroirs (h 15 → 86), four 60 (h 88 → 148), porte de rangement au-dessus. <b>C2</b> : réfrigérateur intégrable (niche 178, porte h 15 → 193), porte de rangement au-dessus. À droite, la fenêtre coupée ; au centre, la baie d'entrée et son vantail fermé.</p></div>

<h2>Coupe C-C · mur est</h2>
<div class="fig"><div class="scroll">{coupe_c()}</div>
<p class="cap">Coupe à x {COUPE_C}, regard vers l'est : le nord est à gauche. Au fond, la cloison du cellier (x 320 → 327) et sa baie de {f(M.BAIE_CELLIER["y1"] - M.BAIE_CELLIER["y0"])} (h {M.BAIE_CELLIER["h"]}) ; on y voit le ballon. Puis, contre le mur du WC (x 382), <b>E1</b> (bas P40 sous plan de travail, h {M.SOCLE} → {M.CAISSON_H} + 4) et <b>E2</b> (placard toute hauteur P40, h {M.SOCLE} → {M.COL_Z1}, fileur jusqu'au plafond) ; à droite, le décroché et le mur sud coupé.</p></div>

<h2>Rangement : V11 et proposition 9 A</h2>
<div class="grid2">
<div class="fig"><h3>V11</h3>{table_rangement(M.RANGEMENT_V11)}</div>
<div class="fig"><h3>Proposition 9, variante A</h3>{table_rangement(M.RANGEMENT_P9A)}</div>
</div>
<p class="cap">Volume brut des caissons fermés : largeur × profondeur du caisson × hauteur des façades de rangement ; électroménager, socles, niches et sous-évier exclus. <b>V11 : {f(round(v11))} L contre {f(round(p9a))} L, soit {f(round(v11 - p9a)):s} L ({(v11 - p9a) / p9a * 100:+.0f} %)</b>. Le sous-évier est le même dans les deux ({f(round(M.SOUS_EVIER["v11"]))} L, poubelles). La V11 gagne surtout par les hauts, la colonne du four plus haute et les deux meubles du mur est ; elle perd le vaisselier de la colonne LV (le LV passe sous le plan), le meuble café et l'abattant au-dessus du micro-ondes. <b>Rangements ouverts</b> : la proposition 9 A en a {f(sum(v for _, v in M.OUVERT_P9A))} cm linéaires ({"; ".join(n.lower() for n, _ in M.OUVERT_P9A)}), dont le cellier ; la V11 n'en a pas encore : le cellier (≈ 45 × 100 utiles, chute dans l'angle nord-est, ballon dans la niche) reste à aménager. Avec des étagères P30 sur sa longueur (100) et 6 niveaux, il en apporterait ≈ 600.</p>

<p class="note">Repère : x vers l'est depuis le mur ouest, y vers le sud depuis le mur nord, z depuis le sol fini, en cm. Source : <span class="mono">3d/v11/modele.py</span> ; plan : <span class="mono">3d/v11/plan.py</span> ; 3D : <span class="mono">3d/v11/cad.py</span>.</p>

<section id="changements">
<h2>Changements</h2>
<table><thead><tr><th>Version</th><th>Date</th><th>Changements</th></tr></thead>
<tbody>{lignes}</tbody></table>
</section>
"""


def page(figees, racine=""):
    """figees : [(version, contenu)] ; le bouton de version bascule tout le contenu (plan, coupes, rangement)."""
    boutons = "".join(f'<button type="button" data-v="{v}">{v} figée</button>' for v, _ in figees)
    blocs = "".join(f'<div class="ver" data-v="{v}" hidden>{c}</div>' for v, c in figees)
    versions = (f'<span>Version</span><button type="button" data-v="courante" aria-pressed="true">'
                f'{M.VERSION} en cours</button>{boutons}') if figees else ""
    barre = f'<div class="vbar"><a class="back" href="{racine}index.html">← Plans</a>{versions}</div>'
    return f"""<!doctype html>
<html lang="fr">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Cuisine V11</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Archivo:wght@400;500;700;800&family=JetBrains+Mono:wght@400;600&display=swap" rel="stylesheet">
<style>{CSS}</style>
</head>
<body>
{barre}
<main class="wrap">
<div class="ver" data-v="courante">{contenu()}</div>
{blocs}
</main>
<script>
(function () {{
  var bs = document.querySelectorAll(".vbar button"), vs = document.querySelectorAll(".ver");
  function montre(v) {{
    if (!document.querySelector('.ver[data-v="' + v + '"]')) v = "courante";
    vs.forEach(function (d) {{ d.hidden = d.dataset.v !== v; }});
    bs.forEach(function (b) {{ b.setAttribute("aria-pressed", b.dataset.v === v); }});
    try {{ localStorage.setItem("cuisine-v11-version", v); }} catch (e) {{}}
  }}
  bs.forEach(function (b) {{ b.addEventListener("click", function () {{ montre(b.dataset.v); }}); }});
  var v0 = "courante";
  try {{ v0 = localStorage.getItem("cuisine-v11-version") || v0; }} catch (e) {{}}
  if (location.hash) v0 = decodeURIComponent(location.hash.slice(1));
  montre(v0);
}})();
</script>
</body>
</html>
"""



FIGEES = os.path.join(os.path.dirname(os.path.abspath(__file__)), "figees")


def figer():
    """Fige la version courante : contenu dans figees/<version>.html (identifiants SVG suffixés pour coexister
    avec la version en cours) et page autonome dans archive/cuisine-<version>.html."""
    os.makedirs(FIGEES, exist_ok=True)
    v = M.VERSION
    c = contenu()
    for ident in set(re.findall(r'id="([^"]+)"', c)):
        c = c.replace(f'id="{ident}"', f'id="{ident}-{v}"').replace(f"url(#{ident})", f"url(#{ident}-{v})")
    with open(os.path.join(FIGEES, f"{v}.html"), "w", encoding="utf-8") as fh:
        fh.write(c)
    with open(os.path.join(ROOT, "archive", f"cuisine-{v.lower()}.html"), "w", encoding="utf-8") as fh:
        fh.write(page([], "../"))
    print(f"{v} figée")


def lire_figees():
    if not os.path.isdir(FIGEES):
        return []
    r = []
    for nom in sorted(os.listdir(FIGEES), key=lambda n: [int(x) for x in re.findall(r"\d+", n)]):
        if nom.endswith(".html"):
            with open(os.path.join(FIGEES, nom), encoding="utf-8") as fh:
                r.append((nom[:-5], fh.read()))
    return r


if __name__ == "__main__":
    if "--figer" in sys.argv:
        figer()
    with open(OUT, "w", encoding="utf-8") as fh:
        fh.write(page(lire_figees()))
    print(OUT)
