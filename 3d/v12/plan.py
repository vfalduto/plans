# Génère cuisine-v12.html (plan vu de dessus + coupe A-A sur le mur nord) depuis modele.py.
#
#   python3 3d/v12/plan.py
#
# Le plan et la coupe sont des projections des volumes du modèle : rien n'est dessiné à la main.

import importlib
import math
import os
import re
import sys
from html import escape

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import modele as M  # noqa: E402

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
OUT = os.path.join(ROOT, "cuisine-v12.html")

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


def cote_d(a, b, t=0.5, dt=(0, 0)):
    """Cote oblique de a à b, texte au point t du segment, décalé de dt."""
    d = math.dist(a, b)
    ux, uy = (b[1] - a[1]) / d * 3, -(b[0] - a[0]) / d * 3  # demi-trait perpendiculaire
    tx, ty = a[0] + (b[0] - a[0]) * t + dt[0], a[1] + (b[1] - a[1]) * t + dt[1]
    return "".join([
        f'<line class="dim" x1="{f(a[0])}" y1="{f(a[1])}" x2="{f(b[0])}" y2="{f(b[1])}"/>',
        *(f'<line class="dim" x1="{f(p[0] - ux)}" y1="{f(p[1] - uy)}" x2="{f(p[0] + ux)}" y2="{f(p[1] + uy)}"/>'
          for p in (a, b)),
        text(tx, ty, f"{d:.0f}", "dimt"),
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
            "aspiration": "asp", "hotte": None, "evier": "inox", "egouttoir": "egout", "cuve": "cuve", "mitigeur": "inox",
            "colonne": "tall", "facade_col": "fac", "four": "fac", "porte": None,
            "caisson": "cab", "facade": "fac", "linteau": None, "cloison": "neuf", "porte_plan": None,
            "table": "tbl", "chant": None, "peinture": None, "pied": None, "chaise": "stool", "fileur": None, "banquette": "stool",
            "etagere": "shelf", "montant": "shelf", "trappe": "trappe",
            "ardoise": None, "aimant": None, "micro_onde": "fac",
            "dormant": "dorm", "dormant_haut": None, "joue": "fac", "paumelle": None,
            "ratelier": "dark", "balai": "balai", "manche": None,
            "led": "led", "etagere_haute": "upper", "enceinte": "upper", "lampe": "lampe", "fil": None, "aspirateur": "aspi",
            "plante": "plante", "pot": None}


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


def battant(h, ferme, ouvert, label):
    """Porte battante ouverte à 90° : vantail de la charnière au bout ouvert, arc depuis le bout fermé."""
    (hx, hy), (fx, fy), (ox, oy) = h, ferme, ouvert
    w = math.dist(h, ferme)
    sweep = 1 if (fx - hx) * (oy - hy) - (fy - hy) * (ox - hx) > 0 else 0
    lx, ly = hx + 0.55 * (fx - hx + ox - hx), hy + 0.55 * (fy - hy + oy - hy)
    return (f'<line class="doorleaf" x1="{f(hx)}" y1="{f(hy)}" x2="{f(ox)}" y2="{f(oy)}"/>'
            f'<path class="swing" d="M{f(fx)} {f(fy)} A{f(w)} {f(w)} 0 0 {sweep} {f(ox)} {f(oy)}"/>'
            + text(lx, ly + 2, label, "lblx muted"))


def vantail(v, ouvert=True):
    """Vantail fermé ou ouvert à son angle, à son épaisseur réelle, avec ses balais (face côté cellier) et sa paumelle ;
    ouvert, avec le balayage depuis la position fermée."""
    (hx, hy), (fx, fy), w = v["h"], v["ferme"], v["w"]
    ox, oy = v["ouvert"] if ouvert else v["ferme"]
    d0 = ((fx - hx) / w, (fy - hy) / w)                 # direction fermée
    d1 = ((ox - hx) / w, (oy - hy) / w)                 # direction ouverte
    c, s_ = d0[0] * d1[0] + d0[1] * d1[1], d0[0] * d1[1] - d0[1] * d1[0]

    def tourne(px, py):
        """Point du vantail fermé (repère : charnière) → position ouverte."""
        return hx + c * px - s_ * py, hy + s_ * px + c * py

    def piece(u0, u1, x0, x1):
        """Rectangle du vantail fermé, de u0 à u1 le long du vantail, de x0 à x1 en épaisseur (x relatif à la charnière)."""
        return [tourne(x + d0[0] * u, d0[1] * u) for x, u in ((x0, u0), (x0, u1), (x1, u1), (x1, u0))]

    o = []
    if ouvert:
        sweep = 1 if (fx - hx) * (oy - hy) - (fy - hy) * (ox - hx) > 0 else 0
        o.append(f'<path class="swing" d="M{f(fx)} {f(fy)} A{f(w)} {f(w)} 0 0 {sweep} {f(ox)} {f(oy)}"/>')
    o.append(f'<polygon class="leaf" points="{pts(piece(0, w, -M.EP_VANTAIL, 0))}"/>')
    for dist, larg in v["balais"]:
        o.append(f'<polygon class="balai" points="{pts(piece(dist - larg / 2, dist + larg / 2, 0, v["saillie"]))}"/>')
    o.append(f'<circle class="pivot" cx="{f(hx)}" cy="{f(hy)}" r="1.4"/>')
    if ouvert:
        lx, ly = hx + 0.6 * (fx - hx + ox - hx), hy + 0.6 * (fy - hy + oy - hy)
        o.append(text(lx, ly + 2, f'{f(w)} · {f(round(v["angle"]))}°', "lblx"))
    return "".join(o)


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
    # fond opaque sous le plan de travail (semi-transparent) : le sol ne doit pas apparaître là où aucun caisson
    # ne le porte (fileur du mur ouest)
    for b in M.MEUBLES:
        if b.role == "plan":
            o.append(rect(b.x0, b.y0, b.x1, b.y1, "ptbase"))
    # volumes, du plus bas au plus haut (une seule emprise par pile de tablettes)
    vues = set()
    for b in sorted(M.ENVELOPPE + M.MEUBLES, key=lambda b: b.z1):
        cls = PLAN_CLS[b.role]
        if cls == "shelf":
            if (b.x0, b.y0, b.x1, b.y1) in vues:
                continue
            vues.add((b.x0, b.y0, b.x1, b.y1))
        if isinstance(b, M.Cyl) and cls:
            o.append(f'<circle class="{cls}" cx="{f(b.cx)}" cy="{f(b.cy)}" r="{f(b.r)}"/>')
        elif cls and getattr(b, "arrondi", 0) and b.coins == "tous":
            o.append(f'<rect class="{cls}" x="{f(b.x0)}" y="{f(b.y0)}" width="{f(b.x1 - b.x0)}" height="{f(b.y1 - b.y0)}" '
                     f'rx="{f(b.arrondi)}"/>')
        elif cls and getattr(b, "arrondi", 0):
            r = b.arrondi
            o.append(f'<path class="{cls}" d="M{f(b.x0)} {f(b.y0)}H{f(b.x1)}V{f(b.y1)}H{f(b.x0 + r)}'
                     f'A{f(r)} {f(r)} 0 0 1 {f(b.x0)} {f(b.y1 - r)}Z"/>')
        elif cls:
            o.append(rect(b.x0, b.y0, b.x1, b.y1, cls))
    # fenêtre coulissante : deux vantaux dans l'épaisseur du mur
    fe = M.FENETRE
    o.append(f'<line class="glass" x1="-7" y1="{fe["y0"]}" x2="-7" y2="{(fe["y0"] + fe["y1"]) / 2 + 2}"/>')
    o.append(f'<line class="glass" x1="-13" y1="{(fe["y0"] + fe["y1"]) / 2 - 2}" x2="-13" y2="{fe["y1"]}"/>')
    # porte d'entrée à galandage : fermée en trait plein, rentrée dans sa poche en ocre
    en = M.ENTREE
    o.append(f'<g class="vt" data-vt="entree" data-etat="ferme">'
             f'<g class="ouv">{rect(en["ouvert"][0], en["y"] - 2, en["ouvert"][1], en["y"] + 2, "leaf")}</g>'
             f'<g class="fer"><line class="doorleaf" x1="{f(en["ferme"][0])}" y1="{f(en["y"])}" '
             f'x2="{f(en["ferme"][1])}" y2="{f(en["y"])}"/></g></g>')
    o.append(text((en["x0"] + en["x1"]) / 2, 270, "Entrée", "lbls"))
    o.append(text(sum(en["poche"]) / 2, 237, "tableau noir · aimants", "lblx"))
    # ballon
    bl = M.BALLON
    if isinstance(bl, M.Cyl):
        o.append(f'<circle class="ecs" cx="{f(bl.cx)}" cy="{f(bl.cy)}" r="{f(bl.r)}"/>')
        o.append(text(bl.cx, bl.cy + 2, "Ballon ECS", "lblx"))
    o.append(text(M.CHUTE[0] + 7, M.CHUTE[1] + 2, "chute", "lblx", "start"))
    o.append(text(M.NOURRICE[0] - 4, M.NOURRICE[1] - 4, "nourrice", "lblx", "end"))
    # numéros des meubles
    for b in M.MEUBLES:
        if b.role == "caisson":
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
        if b.role == "egouttoir":
            o.append(text((b.x0 + b.x1) / 2, (b.y0 + b.y1) / 2 + 2, "égouttoir", "lblx"))
    # cellier : vantaux ouverts vers le cellier, à l'épaisseur réelle, balayage et paumelles
    if M.PLIANTE:
        a = M.PLIANTE
        r, l, e, y0, y1 = a["rail"], a["l"], a["ep"], a["y0"], a["y1"]
        # ouverte : vantail du pivot rabattu vers l'ouest (y0 → y0 + e), second vantail replié contre lui ; balayage
        ouvert = (f'<path class="swing" d="M{f(r)} {f(y0 + 2 * l)} A{f(2 * l)} {f(2 * l)} 0 0 1 {f(r - l)} {f(y0 + e)}"/>'
                  f'<path class="swing" d="M{f(r)} {f(y0 + l)} A{f(l)} {f(l)} 0 0 1 {f(r - l)} {f(y0)}"/>'
                  + rect(r - l, y0, r, y0 + e, "leaf") + rect(r - l, y0 + e, r, y0 + 2 * e, "leaf")
                  + text(r - l / 2, y0 + 2 * e + 6, "porte pliante", "lblx"))
        ferme = rect(r - e / 2, y0, r + e / 2, y0 + l, "leaf") + rect(r - e / 2, y0 + l + 1, r + e / 2, y1, "leaf")
        # mi-ouverte : vantail du pivot tourné de a["mi"]° vers la cuisine, second vantail jusqu'au rail (V)
        t = math.radians(a["mi"])
        p1 = (r - l * math.sin(t), y0 + l * math.cos(t))
        p2 = (r, y0 + 2 * l * math.cos(t))
        mi = (f'<polyline class="pliee" points="{pts([(r, y0), p1, p2])}"/>'
              f'<path class="swing" d="M{f(r)} {f(y0 + l)} A{f(l)} {f(l)} 0 0 1 {f(p1[0])} {f(p1[1])}"/>'
              + text(p1[0] - 3, p1[1] + 2, f'{a["mi"]}°', "lblx", "end"))
        o.append(f'<g class="vt" data-vt="cellier" data-etat="mi"><g class="ouv">{ouvert}</g><g class="mi">{mi}</g>'
                 f'<g class="fer">{ferme}</g></g>')
        o.append(cote_v(y0 + 2 * e + 2, y1, r - 40, f'passage {f(M.PASSAGE_CELLIER)}'))
        # passages dans le cellier
        o.append(cote_v(M.RAYON_NORD["y1"], M.RAYON_SUD["y0"], 405, f'{f(M.PASSAGE_RAYONNAGES)}'))
        o.append(cote_v(M.RAYON_NORD["y1"], M.JOUE_C2, 374, f'{f(M.PASSAGE_ENTREE)}'))
        o.append(cote_v(M.Y_BALAIS + 6, M.JOUE_C2, 332, f'{f(M.JOUE_C2 - M.Y_BALAIS - 6)}'))
    for k, v in enumerate(M.CELLIER_VANTAUX):
        o.append(f'<g class="vt" data-vt="{k}"><g class="ouv">{vantail(v)}</g>'
                 f'<g class="fer">{vantail(v, ouvert=False)}</g></g>')
    # réseaux d'eau
    for role, _, p, _, _ in M.RESEAUX:
        o.append(f'<polyline class="{"pin" if role == "alim" else "pout"}" points="{pts(p)}"/>')
    o.append(f'<circle class="chute" cx="{f(M.CHUTE[0])}" cy="{f(M.CHUTE[1])}" r="4.5"/>')
    o.append(f'<circle class="nourrice" cx="{f(M.NOURRICE[0])}" cy="{f(M.NOURRICE[1])}" r="2.5"/>')
    # ouvertures de l'électroménager
    for kind, nom, d in M.OUVERTURES:
        if kind in ("abattant", "tiroir"):
            x0, x1, y0, y1 = d
            o.append(rect(x0, y0, x1, y1, "swingz"))
            lib = f"porte {nom} abattue" if kind == "abattant" else "tiroir"
            o.append(text((x0 + x1) / 2, (y0 + y1) / 2 + 2, lib, "lblx muted"))
        else:
            o.append(battant(*d, f"porte {nom} 90°"))
    # cellier : surface et volume
    surf = aire(M.CELLIER_SOL) / 1e4
    vol = surf * M.H / 100
    bl = M.BALLON
    net = vol - (math.pi * (bl.r / 100) ** 2 * (bl.z1 - bl.z0) / 100 if isinstance(bl, M.Cyl) else 0)
    for k, ligne in enumerate((f"cellier · {surf:.2f} m²", f"{vol:.2f} m³ brut · ≈ {net:.1f} net")):
        o.append(text(373, 39 + 7 * k, ligne.replace(".", ","), "lblx"))
    # table
    o.append(text(M.TABLE["cx"], M.TABLE["cy"] + 3, f'{M.TABLE["cote"]} × {M.TABLE["cote"]}', "lblb"))
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
    for x, nom, y0, y1 in ((COUPE_C, "C", -82, 300),):
        o.append(f'<line class="sec" x1="{x}" y1="{y0}" x2="{x}" y2="{y1}"/>')
        for y in (y0, y1):
            o.append(f'<path class="secm" d="M{x} {y - 4} l9 4 l-9 4 z"/>')
            o.append(text(x - 7, y + 4, nom, "sect"))
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
    for y0, y1 in ((M.COL_Y0, M.COL_Y0 + 60), (M.COL_Y0 + 60, M.COL_Y1)):
        o.append(cote_v(y0, y1, 402))
    # passages depuis l'angle sud-est des façades des meubles bas : frigo, mur nord du WC
    o.append(cote_d((caissons[-1].x1, 62), (M.COL_X, M.JOUE_C2), 0.5, (-7, 4)))
    # porte d'entrée à galandage : baie, poche
    o.append(cote_h(en["x0"], en["x1"], 282, f'baie {f(en["x1"] - en["x0"])}'))
    o.append(cote_h(*en["poche"], 282, f'poche {f(en["poche"][1] - en["poche"][0])}'))
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
             "plaque": ("dark", "dark"), "aspiration": ("dark", "dark"), "hotte": ("inox", "inox"), "evier": ("inox", "inox"), "egouttoir": ("inox", "inox"),
             "cuve": ("inox", "inox"), "mitigeur": ("inox", "inox"), "ballon": ("ecs", "ecs"),
             "tech": ("tech", "tech"), "socle": ("plinth", "plinth"),
             "caisson": ("cab", "cab"), "facade": ("fac", "fac"), "porte": ("leaf", "leaf"),
             "colonne": ("tall", "tall"), "cloison": ("wallv", "neuf"),
             "fileur": ("fac", "fac"), "banquette": ("stool", "stool"), "table": ("tbl", "tbl"), "chant": ("dark", "dark"), "peinture": ("peint", "peint"), "pied": ("tbl", "tbl"), "chaise": ("stool", "stool"), "facade_col": ("fac", "fac"), "four": ("dark", "dark"),
             "etagere": ("shelf", "shelfc"), "montant": ("shelf", "shelfc"), "trappe": ("trappe", "trappe"),
             "ardoise": ("ardoise", "ardoise"), "aimant": ("aimant", "aimant"), "micro_onde": ("dark", "dark"),
             "dormant": ("dorm", "dorm"), "dormant_haut": ("dorm", "dorm"), "joue": ("fac", "fac"),
             "paumelle": ("dark", "dark"), "ratelier": ("dark", "dark"), "balai": ("balai", "balai"),
             "manche": ("balai", "balai"), "led": ("led", "led"), "etagere_haute": ("shelf", "shelfc"),
             "enceinte": ("dark", "dark"), "lampe": ("lampe", "lampe"), "fil": ("dark", "dark"),
             "aspirateur": ("aspi", "aspi"), "plante": ("plante", "plante"), "pot": ("pot", "pot")}


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


def coupe_svg(cut, regard, umin, umax, chaines, hauteurs, xh, extra=None, origine=0, transparents=()):
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
    trans = [t for t in vus if transparents and t.nom.startswith(transparents)]

    def derriere(b):
        """b est caché par un élément transparent (porte du cellier…) quand celui-ci est opaque."""
        u0, u1, d0, d1 = uv(b, axe)
        for t in trans:
            tu0, tu1, td0, td1 = uv(t, axe)
            if (d0 >= td1 if sens > 0 else d1 <= td0) and u0 < tu1 and u1 > tu0 and b.z0 < t.z1 and b.z1 > t.z0:
                return True
        return False

    for b in vus:
        n0 = len(etiquettes)
        u0, u1, d0, d1 = uv(b, axe)
        coupe = d0 < cut < d1
        if isinstance(b, M.Pan) and coupe:
            # panneau en biais coupé : on ne voit que la partie au-delà du plan, plus sa section au point de coupe
            (ua, da), (ub, db) = [(p[0], p[1]) if axe == "y" else (p[1], p[0]) for p in (b.a, b.b)]
            ui = ua + (ub - ua) * (cut - da) / (db - da)
            loin = ua if (da - cut) * sens > 0 else ub
            u0, u1 = sorted((ui, loin))
            uc, vc = sorted((X(ui - b.ep / 2), X(ui + b.ep / 2)))
            o.append(rect(uc, -b.z1, vc, -b.z0, COUPE_CLS[b.role][1]))
            coupe = False
        u, v = sorted((X(max(u0, umin)), X(min(u1, umax))))
        # éléments dessinés en transparence (contour seul) pour voir ce qu'il y a derrière
        cls = COUPE_CLS[b.role][1 if coupe else 0]
        o.append(rect(u, -b.z1, v, -b.z0, f"{cls} trp" if transparents and b.nom.startswith(transparents) else cls))
        xm = (u + v) / 2
        if b.role == "allege" and coupe:
            o.append(text(xm, -150, "fenêtre", "lblx", extra=f' transform="rotate(-90 {f(xm)} -150)"'))
        if b.role == "ballon":
            etiquettes.append(text(xm, -(b.z0 + b.z1) / 2, "Ballon", "lblx"))
        if b.role == "four" and v - u > 10:  # pas d'étiquette sur un four vu sur chant
            etiquettes.append(text(xm, -(b.z0 + b.z1) / 2 + 2, "four", "lblx onDark"))
        if b.role == "micro_onde" and v - u > 10:
            etiquettes.append(text(xm, -(b.z0 + b.z1) / 2 + 2, "micro-ondes", "lblx onDark"))
        if getattr(b, "poignee", "") and v - u > 10:
            # poignée : tiroir en haut au centre, porte basse en haut sur le côté, porte haute en bas sur le côté,
            # relevable en bas au centre
            zt, zb, um = -b.z1 + 4, -b.z0 - 4, (u + v) / 2
            if b.role in ("facade_haut", "facade_col"):
                # façades bois : profilé toute longueur, même matière (tiroir : toute la largeur ; porte : toute la hauteur)
                if b.poignee == "tiroir":
                    o.append(f'<line class="poig bois" x1="{f(u + 2)}" y1="{f(-b.z1 + 1.5)}" x2="{f(v - 2)}" y2="{f(-b.z1 + 1.5)}"/>')
                else:
                    # C2 (frigo) : charnières au sud, poignée côté nord (à gauche en coupe C-C)
                    xp = u + 1.5 if b.nom.endswith(("_c2", "_c3")) else v - 1.5
                    o.append(f'<line class="poig bois" x1="{f(xp)}" y1="{f(-b.z1 + 2)}" x2="{f(xp)}" y2="{f(-b.z0 - 2)}"/>')
            elif b.poignee == "tiroir":
                o.append(f'<line class="poig" x1="{f(um - 8)}" y1="{f(zt)}" x2="{f(um + 8)}" y2="{f(zt)}"/>')
            elif b.poignee == "relevable":
                o.append(f'<line class="poig" x1="{f(um - 8)}" y1="{f(zb)}" x2="{f(um + 8)}" y2="{f(zb)}"/>')
            elif b.role == "facade_haut":
                o.append(f'<line class="poig" x1="{f(v - 4)}" y1="{f(zb)}" x2="{f(v - 4)}" y2="{f(zb - 12)}"/>')
            else:
                o.append(f'<line class="poig" x1="{f(v - 4)}" y1="{f(zt)}" x2="{f(v - 4)}" y2="{f(zt + 12)}"/>')
        if (getattr(b, "contenu", "") and b.role == "etagere" and not coupe and v - u > 20
                and u1 - u0 >= d1 - d0):  # tablette vue de face (pas sur chant)
            etiquettes.append(text(xm, -(b.z1 + 17), b.contenu, "lblc"))  # au milieu de l'espace au-dessus
        elif getattr(b, "contenu", "") and b.role != "etagere" and v - u > 20:
            zc = b.z0 + 13 if b.role == "facade_haut" else b.z1 - 10
            if b.role == "facade" and 44 < zc < 60:  # pas sur l'étiquette du meuble (B2…) : en bas de la façade
                zc = b.z0 + 6
            zc = -zc
            etiquettes.append(text(xm, zc, b.contenu, "lblc"))
        if b.nom == "aspirateur_bloc" and v - u > 10:
            etiquettes.append(text(xm, -(b.z0 + b.z1) / 2 + 2, "aspirateur", "lblx onDark"))
        if b.role == "enceinte" and v - u > 10:
            etiquettes.append(text(xm, -(b.z0 + b.z1) / 2 + 2, "enceinte", "lblx onDark"))
        if b.role in ("ardoise", "aimant"):
            etiquettes.append(text(xm, -(b.z0 + b.z1) / 2 + 2, "tableau noir" if b.role == "ardoise" else "aimants",
                                   "lblx onDark" if b.role == "ardoise" else "lblx"))
        if getattr(b, "etiq", ""):
            zm = (b.z0 + b.z1) / 2 if b.role != "colonne" else 200
            nom, _, equip = b.etiq.partition(" ")
            etiquettes.append(text(xm, -zm + 3, nom, "lblb"))
            if equip and b.role == "caisson":
                etiquettes.append(text(xm, -zm + 12, equip, "lbls"))
        if trans and not b.nom.startswith(transparents) and derriere(b):
            # étiquettes de ce qui est derrière la porte : visibles seulement en transparence
            etiquettes[n0:] = [e.replace('class="', 'class="trp-lbl ', 1) for e in etiquettes[n0:]]
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
    rn = M.RAYON_NORD

    def sol(X):
        xm = X((rn["x0"] + rn["x1"]) / 2)
        return [text(xm, -30, rn["sol"].split(", ")[0] + ", " + rn["sol"].split(", ")[1], "lblc"),
                text(xm, -25, ", ".join(rn["sol"].split(", ")[2:]), "lblc")]

    return coupe_svg(COUPE_A, "nord", -20, 494, [(bas, 22), (hauts, -M.H - 8)],
                     [M.SOCLE, M.CAISSON_H, M.PT_Z1, M.HAUT_Z0, M.HAUT_Z1], -50, sol)


def coupe_b():
    xmin, xmax = -20, 392
    en = M.ENTREE
    v = next(b for b in M.ENVELOPPE if b.nom == "entree_vantail")

    tn = next(b for b in M.ENVELOPPE if b.nom == "tableau_noir")
    za = next(b for b in M.ENVELOPPE if b.nom == "zone_aimantee")

    def porte(X):
        u0, u1 = sorted((X(en["x0"]), X(en["x1"])))
        w0, w1 = sorted((X(v.x0), X(v.x1)))
        p0, p1 = sorted((X(en["poche"][0]), X(en["poche"][1])))
        return [cote_h(u0, u1, 38, f'baie {f(en["x1"] - en["x0"])}'),
                cote_h(p0, p1, 38, f'poche {f(en["poche"][1] - en["poche"][0])}'),
                cote_h(w0, w1, -v.z1 - 6, f'vantail {f(v.x1 - v.x0)} × {f(v.z1 - v.z0)}'),
                cote_v(0, -en["h"], w0 - 8, f'baie h {en["h"]}'),
                cote_v(-za.z0, -za.z1, p1 + 6), cote_v(-tn.z0, -tn.z1, p1 + 6)]

    return coupe_svg(COUPE_B, "sud", xmin, xmax, [], [45, 75, 85, en["h"], M.COL_Z1], xmin - 30, porte)


def coupe_c():
    cols = sorted([b for b in M.MEUBLES if b.role == "colonne"], key=lambda b: b.y0)
    def cellier(X):
        return [cote_h(X(M.BAIE_Y0), X(M.BAIE_Y1), -M.H - 8, f"baie {f(M.BAIE_Y1 - M.BAIE_Y0)}"),
                cote_h(X(M.BAIE_Y1 - M.PASSAGE_CELLIER), X(M.BAIE_Y1), -204 - 6, f"passage {f(M.PASSAGE_CELLIER)}")]

    return coupe_svg(COUPE_C, "est", -20, 262, [(cols, 22)],
                     [M.SOCLE, M.LV_Z0, M.MO_Z0, M.MO_Z1, 193, M.COL_Z1], -50, cellier,
                     transparents=("cellier_pliante", "linteau_cellier"))


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
.scroll svg{display:block;width:100%;height:auto}
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
.plinth{fill:#EFE9DC;stroke:var(--ink);stroke-width:.6}
.ecs{fill:var(--panel);stroke:var(--water);stroke-width:1.2}
.leaf{fill:var(--wood);stroke:var(--ink);stroke-width:.6}
.ghost{fill:none;stroke:var(--muted);stroke-width:.8;stroke-dasharray:4 3}
.dark{fill:var(--ink)}
.pt{fill:var(--panel);fill-opacity:.55;stroke:var(--ink);stroke-width:1.1}
.ptbase{fill:var(--panel);stroke:none}
.peint{fill:#3F5A4E;fill-opacity:.35;stroke:none}
.egout{fill:#D9D9D6;stroke:var(--ink);stroke-width:.5;stroke-dasharray:1 1.5}
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
.ardoise{fill:#2B3230;stroke:var(--ink);stroke-width:.6}.aimant{fill:#A7AEB2;stroke:var(--ink);stroke-width:.6}
body:not(.explications) .cap{display:none}
.vbar .expl{margin-left:auto}
body:not(.changements) section[id^="changements"]{display:none}
.lampe{fill:#F2C94C;fill-opacity:.35;stroke:#B8860B;stroke-width:.7;stroke-dasharray:3 2}
.lblc{font-size:3.6px;font-style:italic;fill:var(--ink)}
.plante{fill:#6E9B5A;fill-opacity:.8;stroke:#3F6B31;stroke-width:.6;stroke-dasharray:3 2}.pot{fill:#C2703D;stroke:var(--ink);stroke-width:.5}
.aspi{fill:#8A97A3;stroke:var(--ink);stroke-width:.6}
.led{fill:#F2C94C;stroke:#B8860B;stroke-width:.4}
.poig{stroke:#8E8E8B;stroke-width:1.4;stroke-linecap:round}
.poig.bois{stroke:#8A5A2B;stroke-width:2.2;stroke-linecap:butt}
.orga td,.orga th{vertical-align:top}
.capa td.ok{background:color-mix(in srgb,#3E8E5A 20%,transparent)}
.capa td.ko{background:color-mix(in srgb,var(--tri) 22%,transparent)}
h3{font-size:15px;margin:22px 0 8px}.orga .on{background:var(--cab)}
.balai{fill:#C9A46A;stroke:var(--ink);stroke-width:.4}
.tog{display:flex;flex-wrap:wrap;align-items:center;gap:6px;margin:0 0 10px;font-family:"JetBrains Mono",ui-monospace,monospace;font-size:12px}
.tog span{color:var(--muted);text-transform:uppercase;letter-spacing:.08em;margin-right:4px}
.tog button{font:inherit;color:var(--ink);background:var(--panel);border:1px solid var(--line);border-radius:6px;padding:4px 10px;cursor:pointer}
.tog button[aria-pressed="true"]{background:var(--ink);color:var(--paper);border-color:var(--ink)}
.vt[data-etat="ferme"] .ouv,.vt[data-etat="mi"] .ouv,.vt:not([data-etat="ferme"]) .fer,.vt:not([data-etat="mi"]) .mi{display:none}
.pliee{fill:none;stroke:var(--ink);stroke-width:2.5;stroke-linejoin:round}
.transp .trp{fill:none;stroke:var(--ink);stroke-width:.7;stroke-dasharray:4 2}
.fig:not(.transp) .trp-lbl{display:none}
.dorm{fill:var(--panel);stroke:var(--ink);stroke-width:.6}
.seuil{stroke:var(--muted);stroke-width:.7;stroke-dasharray:3 2}
.slid{fill:var(--wood);fill-opacity:.55;stroke:var(--wood);stroke-width:.6}
.pivot{fill:var(--paper);stroke:var(--ink);stroke-width:.8}
.leafd{stroke:var(--ink);stroke-width:3;stroke-linecap:round}
.leafg{stroke:var(--muted);stroke-width:1.5;stroke-opacity:.45;stroke-dasharray:3 2}
.move{stroke:var(--tri);stroke-width:1;stroke-dasharray:2.5 2;fill:none}.flm{fill:var(--tri)}
.diag{stroke:var(--tri);stroke-width:1;stroke-dasharray:4 2}.diagt{font:600 8px "JetBrains Mono",monospace;fill:var(--tri)}
.celsol{fill:var(--ink);fill-opacity:.1}
.shelf,.shelfd{fill:var(--wood);fill-opacity:.3;stroke:var(--wood);stroke-width:.6}
.shelfc{fill:var(--wood);stroke:var(--ink);stroke-width:.6}
.trappe{fill:var(--wood);fill-opacity:.12;stroke:var(--ink);stroke-width:.8;stroke-dasharray:3 2}
.frame{fill:none;stroke:var(--line);stroke-width:.8}
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
.pbar{position:sticky;top:41px;z-index:4;display:flex;flex-wrap:wrap;align-items:center;gap:6px;margin:0 0 12px;padding:8px 0;background:var(--paper);font-family:"JetBrains Mono",ui-monospace,monospace;font-size:12px}
.pbar span{color:var(--muted);text-transform:uppercase;letter-spacing:.08em;margin-right:4px}
.pbar button{font:inherit;color:var(--ink);background:var(--panel);border:1px solid var(--line);border-radius:6px;padding:4px 10px;cursor:pointer}
.pbar button[aria-pressed="true"]{background:var(--ink);color:var(--paper);border-color:var(--ink)}
.vbar button[aria-pressed="true"]{background:var(--ink);color:var(--paper);border-color:var(--ink)}
@media (max-width:480px){ body{font-size:15px} }
"""


def lignes_avant_apres():
    """Mesures V11.34 (avant) et version en cours : [(mesure, avant, en cours, écart)], textes à la française."""
    a, v = M.AVANT, M.CAPACITE["v11"]
    lib = lambda x: sum(b - c for c, b in x)
    apres = dict(lin_bas=v["lin_bas"], lin_hauts=v["lin_hauts"], lin_col=v["lin_col"], modules=sum(v["modules"]),
                 tiroirs=v["tiroirs"], anglaise=len(M.TIROIRS_ANGLAISE), plan=lib(v["plan"]),
                 plan_max=max(b - c for c, b in v["plan"]), cellier_m2=aire(M.CELLIER_SOL) / 1e4,
                 tablettes=v["cellier"][1] * v["cellier"][2] + v["cellier_sud"][1] * v["cellier_sud"][2],
                 vol_cuisine=M.VOLUMES["v11"]["cuisine"], vol_cellier=M.VOLUMES["v11"]["cellier"])
    avant = dict(lin_bas=a["lin_bas"], lin_hauts=a["lin_hauts"], lin_col=a["lin_col"], modules=sum(a["modules"]),
                 tiroirs=a["tiroirs"], anglaise=a["anglaise"], plan=lib(a["plan"]),
                 plan_max=max(b - c for c, b in a["plan"]), cellier_m2=a["cellier_m2"], tablettes=a["tablettes_cm"],
                 vol_cuisine=a["volume_cuisine"], vol_cellier=a["volume_cellier"])
    fr = lambda t: re.sub(r"(\d)\.(\d)", r"\1,\2", t)
    rows = []
    for nom, k, div, fmt in LIGNES_CAPACITE:
        x, y = avant[k] / div, apres[k] / div
        d = y - x
        signe = "+" if d > 0 else "−" if d < 0 else "±"
        rows.append((nom, fr(fmt.format(x)), fr(fmt.format(y)), fr(signe + fmt.format(abs(d)))))
    tot_a, tot_v = (avant["vol_cuisine"] + avant["vol_cellier"]) / 1000, (apres["vol_cuisine"] + apres["vol_cellier"]) / 1000
    rows.append(("Volume total", fr(f"{tot_a:.2f} m³"), fr(f"{tot_v:.2f} m³"),
                 fr(f"{'+' if tot_v >= tot_a else '−'}{abs(tot_v - tot_a):.2f} m³")))
    return rows


# mesures du tableau de capacité : (libellé, clé, diviseur, format)
LIGNES_CAPACITE = [
    ("Meubles bas (m linéaires)", "lin_bas", 100, "{:.2f} m"), ("Meubles hauts (m linéaires)", "lin_hauts", 100, "{:.2f} m"),
    ("Colonnes (m linéaires)", "lin_col", 100, "{:.2f} m"), ("Nombre de meubles", "modules", 1, "{:.0f}"),
    ("Tiroirs à sortie totale", "tiroirs", 1, "{:.0f}"), ("Tiroirs à l'anglaise (derrière une porte)", "anglaise", 1, "{:.0f}"),
    ("Plan de travail utile", "plan", 100, "{:.2f} m"), ("Plus grand plan d'un seul tenant", "plan_max", 1, "{:.0f} cm"),
    ("Cellier : surface au sol", "cellier_m2", 1, "{:.2f} m²"), ("Cellier : tablettes", "tablettes", 100, "{:.2f} m"),
    ("Volume fermé de la cuisine", "vol_cuisine", 1, "{:.0f} L"), ("Volume du cellier (rayonnages)", "vol_cellier", 1, "{:.0f} L")]


def colonne_p9a():
    """Proposition 9 A (figée, ne change plus) et repères d'une cuisine de 8 m², dans l'ordre de LIGNES_CAPACITE + total."""
    p, r, vol = M.CAPACITE["p9a"], M.REPERES, M.VOLUMES["p9a"]
    segs = [b - a for a, b in p["plan"]]
    fr = lambda t: re.sub(r"(\d)\.(\d)", r"\1,\2", t)
    p9a = [f"{p['lin_bas'] / 100:.2f} m (dont le café)", f"{p['lin_hauts'] / 100:.2f} m", f"{p['lin_col'] / 100:.2f} m (LV, frigo, four)",
           f"{sum(p['modules'])}", f"{p['tiroirs']}", "0", f"{sum(segs) / 100:.2f} m ({' + '.join(f(x) for x in segs)})",
           f"{max(segs)} cm", "", f"{p['cellier'][1] * p['cellier'][2] / 100:.2f} m",
           f"{vol['cuisine']:.0f} L", f"{vol['cellier']:.0f} L", f"{sum(vol.values()) / 1000:.2f} m³"]
    rep = ["", "", "", f"{r['modules'][0]} à {r['modules'][1]}",
           "plus il y en a, mieux c'est", "", f"{r['plan'][0] / 100:g} à {r['plan'][1] / 100:g} m", "", "", "", "", "",
           f"{r['volume'][0]:g} à {r['volume'][1]:g} m³ (bien optimisée)"]
    return [fr(x) for x in p9a], [fr(x) for x in rep]


def details_capacite():
    """Lignes descriptives de la version en cours : implantation, rayonnages du cellier, rangements ouverts."""
    v = M.CAPACITE["v11"]
    n, s = v["cellier"], v["cellier_sud"]
    return dict(
        implantation=f"{max(b.x1 for b in M.MEUBLES if b.role == 'caisson' and b.y0 == 0) / 100:.2f} m, "
                     f"{v['modules'][0] + v['modules'][1]} meubles".replace(".", ","),
        rayonnages=(f"nord {n[0]} cm, {n[1]} tablettes P{n[3]} de {n[2]} ; sud (mur du WC) {s[0]} cm, "
                    f"{s[1]} tablettes P{s[3]} de {s[2]}"),
        ouverts=escape(v["autres"]))


def nombre(t):
    """Premier nombre d'un texte à la française (« 2,60 m » → 2.6), None s'il n'y en a pas."""
    m = re.search(r"\d+(?:,\d+)?", re.sub(r"<[^>]+>", "", t))
    return float(m.group().replace(",", ".")) if m else None


def note(t, lo, hi=None):
    """Classe de cellule : « ok » dans le repère, « ko » hors repère (hi None : minimum seul)."""
    x = nombre(t)
    if x is None:
        return ""
    return ' class="ok"' if lo <= x and (hi is None or x <= hi) else ' class="ko"'


def section_capacite(version, rows, details):
    """Section « Capacité » : V11.34 (avant), version affichée, écart, proposition 9 A et repères. Sert aussi à
    réécrire les versions figées (rows et details lus dans leur HTML). Cellules vertes dans le repère d'une cuisine
    de 8 m², rouges en dehors."""
    p9a, rep = colonne_p9a()
    r = M.REPERES
    lignes = [list(x) + [p9a[k], rep[k], None] for k, x in enumerate(rows)]
    # bas + hauts : c'est la somme qui a un repère
    som = lambda i: f"{nombre(lignes[0][i]) + nombre(lignes[1][i]):.2f} m".replace(".", ",")
    d = nombre(lignes[0][2]) + nombre(lignes[1][2]) - nombre(lignes[0][1]) - nombre(lignes[1][1])
    signe = "+" if d > 0.001 else "−" if d < -0.001 else "±"
    lignes.insert(2, ["Meubles bas + hauts", som(1), som(2), f"{signe}{abs(d):.2f} m".replace(".", ","), som(4),
                      f"{r['lin'][0] / 100:g} à {r['lin'][1] / 100:g} m", (r["lin"][0] / 100, r["lin"][1] / 100)])
    regles = {"Nombre de meubles": r["modules"], "Plan de travail utile": (r["plan"][0] / 100, r["plan"][1] / 100),
              "Volume total": (r["volume"][0], None)}
    corps = ""
    for k, (nom, av, ap, ec, p9, rp, regle) in enumerate(lignes):
        regle = regle or regles.get(nom)
        c = (lambda t: note(t, *regle)) if regle else (lambda t: "")
        gras = "<b>" + nom + "</b>" if k == len(lignes) - 1 else nom
        corps += (f"<tr><td>{gras}</td><td{c(av)}>{av}</td><td{c(ap)}><b>{ap}</b></td><td>{ec}</td>"
                  f"<td{c(p9)}>{p9}</td><td>{rp}</td></tr>")
    p, (i0, i1, n0, n1) = M.CAPACITE["p9a"], r["implantation"]

    def impl(t):   # longueur 2,50 → 3 m et 6 ou 7 meubles
        n = re.search(r"(\d+) meubles", t)
        ok = i0 / 100 <= nombre(t) <= i1 / 100 and n and n0 <= int(n.group(1)) <= n1
        return ' class="ok"' if ok else ' class="ko"'
    p9_impl = "2,49 m, 7 meubles + colonne LV"
    corps += "".join(f'<tr><td>{nom}</td><td></td><td colspan="2"{cx}>{x}</td><td{cy}>{y}</td><td>{z}</td></tr>'
                     for nom, x, cx, y, cy, z in [
        ("Implantation (mur nord)", details["implantation"], impl(details["implantation"]), p9_impl, impl(p9_impl),
         f"{i0 / 100:.2f} à {i1 / 100:g} m, ".replace(".", ",") + f"{n0} ou {n1} meubles"),
        ("Cellier : rayonnages", details["rayonnages"], "",
         f"{p['cellier'][0]} cm, {p['cellier'][1]} tablettes P{p['cellier'][3]} de {p['cellier'][2]}", "", ""),
        ("Rangements ouverts", details["ouverts"], "", escape(p["autres"]), "", "")])
    av = M.AVANT["version"]
    return f"""<h2>Capacité : {av} → {version} et proposition 9 A</h2>
<div class="fig"><div class="scroll"><table class="orga capa"><thead><tr><th>Mesure</th><th>{av} (avant)</th><th>{version}</th><th>Écart</th>
<th>Proposition 9 A</th><th>Repère cuisine 8 m²</th></tr></thead><tbody>{corps}</tbody></table></div>
<p class="cap">Mesurée comme le font les cuisinistes : mètres linéaires de meubles, nombre de meubles, tiroirs, plan de travail utile (hors évier et plaque) et implantation, sur la version figée {av}, la version affichée et la proposition 9 A, avec les repères d'une cuisine d'environ 8 m² (la pièce fait 3,25 × 2,52 = 8,2 m² hors cellier). <b>En vert</b> : dans le repère ; <b>en rouge</b> : en dehors (pour le volume, le repère est un minimum : au-delà de 2,5 m³, la cuisine est plus qu'optimisée). L'écart se lit par rapport à {av}. <b>Volume</b> (repère moins parlant, gardé pour comparer) : largeur × profondeur du caisson × hauteur des façades de rangement, électroménager, socles et sous-évier exclus ; cellier : largeur utile × profondeur × hauteur des rayonnages, de la première tablette au haut du rayonnage.</p></div>
"""


def texte_cellier():
    a, nord = M.PLIANTE, M.RAYON_NORD
    return (f"<b>Porte du cellier</b> ({M.PORTE_TITRE}) : un retour de cloison va du mur nord à y {f(M.CLOISON_Y1)} "
            f"(passage des réseaux) ; la baie va jusqu'au flanc nord de C3 : {f(M.BAIE_Y1 - M.BAIE_Y0)} × 204 sous un "
            f"linteau. Porte de placard pliante à deux vantaux de {f(a['l'])} posée sans dormant, rail haut côté cuisine, "
            f"pivot au nord : en s'ouvrant, les vantaux se replient l'un contre l'autre et se rangent côté cuisine contre "
            f"le retour de cloison, devant le coffre des réseaux (côté cellier, ils heurteraient le rayonnage nord) ; le "
            f"vantail du pivot balaie {f(a['l'])} côté cuisine. Poignée au sud, côté C3 ; le bouton au-dessus du plan "
            f"la montre ouverte, mi-ouverte (vantaux en V, pivot à {a['mi']}°) ou fermée. <b>Passage libre ≈ {f(M.PASSAGE_CELLIER)}</b> ; accès depuis "
            f"la cuisine, du coin du plan de B{M.N_BAS} à l'angle de C3 : {M.ACCES_CELLIER:.0f}. <b>Passages dans le "
            f"cellier</b> : {f(M.JOUE_C2 - M.Y_BALAIS - 6)} à l'entrée, devant les balais (accrochés au mur nord dans les 40 "
            f"libérés par le rayonnage) ; {f(M.PASSAGE_RAYONNAGES)} entre les deux rayonnages, {f(M.PASSAGE_ENTREE)} entre le rayonnage "
            f"nord et le flanc de C3. "
            f"<b>Organisation du cellier</b> : un <b>rayonnage toute hauteur P{nord['y1']}</b> contre le mur nord, de la "
            f"cloison jusqu'au mur de l'alcôve (x {nord['x0']} → {nord['x1']}, {len(nord['zs'])} tablettes "
            f"de {M.L_NORD}, la première à h {nord['zs'][0]} au-dessus des tuyaux), pour les denrées ; un second "
            f"<b>rayonnage toute hauteur P{M.RAYON_SUD['y1'] - M.RAYON_SUD['y0']}</b> contre le mur du WC (x "
            f"{M.RAYON_SUD['x0']} → {M.RAYON_SUD['x1']}, {len(M.RAYON_SUD['zs'])} tablettes de {M.L_SUD}), pour "
            f"l'entretien au sol et les réserves non alimentaires ; entre les deux, {M.RAYON_SUD['y0'] - nord['y1']} de "
            f"passage vers la niche : nourrice, groupe de sécurité et chute restent accessibles. "
            +             f"<b>Finitions</b> : joues de 2 sur les flancs visibles des colonnes (nord de C2, "
            f"sud de C1 jusqu'au décroché) et des meubles hauts (ouest de H1, est de H{M.N_HAUTS}), fileurs de 7 jusqu'au "
            f"plafond au-dessus des hauts et des colonnes.")


def table_materiaux():
    def ech(e):
        if isinstance(e, str):
            return f'<img src="{e}" alt="" style="width:120px;height:60px;object-fit:cover;border-radius:4px;display:block">'
        return "".join(f'<span style="display:inline-block;width:{120 // len(e)}px;height:60px;background:{c};'
                       f'{"border-radius:4px 0 0 4px;" if k == 0 else ""}{"border-radius:0 4px 4px 0;" if k == len(e) - 1 else ""}'
                       f'{"border-radius:4px;" if len(e) == 1 else ""}"></span>' for k, c in enumerate(e))
    corps = "".join(f"<tr><td>{ech(e)}</td><td>{escape(n)}</td><td><b>{escape(m)}</b><br>{escape(p)}</td></tr>"
                    for n, m, p, e in M.MATERIAUX)
    return ('<table class="orga"><thead><tr><th style="width:136px">Échantillon</th><th>Élément</th><th>Matériau</th>'
            f'</tr></thead><tbody>{corps}</tbody></table>')


def galerie(items):
    """Rendus groupés (M.RENDUS_GROUPES) : un titre par groupe, des boutons quand une même vue a des variantes.
    items : {vue: (src, titre, légende HTML)} ; sert aussi à réécrire les galeries des versions figées."""
    html = ""
    for titre, vues in M.RENDUS_GROUPES:
        vs = [(v, lib) for v, lib in vues if v in items]
        if not vs:
            continue
        variantes = bool(vs[0][1]) and len(vs) > 1
        figs = "".join(f'<figure data-rv="{v}"{" hidden" if variantes and k else ""} style="margin:0 0 18px">'
                       f'<img src="{items[v][0]}" alt="{escape(items[v][1])}" loading="lazy" '
                       f'style="width:100%;border-radius:8px;display:block">'
                       f'<figcaption class="cap"><b>{escape(items[v][1])}</b> — {items[v][2]}</figcaption></figure>'
                       for k, (v, lib) in enumerate(vs))
        boutons = ('<div class="tog rtog"><span>Variante</span>' + "".join(
            f'<button type="button" data-rv="{v}" aria-pressed="{str(k == 0).lower()}">{escape(lib)}</button>'
            for k, (v, lib) in enumerate(vs)) + "</div>") if variantes else ""
        html += f'<h3>{escape(titre)}</h3>\n<div class="fig rgrp">{boutons}{figs}</div>\n'
    return html


def galerie_rendus():
    items = {v: (f"cuisine-v12-3d/{v}.jpg?v={M.RENDUS_VERSION[v]}", t, f"{escape(c)} (rendu {M.RENDUS_VERSION[v]})")
             for v, t, c in M.RENDUS if os.path.exists(os.path.join(ROOT, "cuisine-v12-3d", f"{v}.jpg"))}
    if not items:
        return ""
    return (f'<h2>Rendus 3D</h2>\n{galerie(items)}<p class="cap">Blender (Cycles) depuis le modèle FreeCAD de '
            f'la version indiquée sous chaque image (rendus faits sur demande) : 21 juin, 17 h, soleil réel par la fenêtre, '
            'suspension et LED allumées ; matériaux de la section Matériaux (teintes indicatives).</p>\n')


def table_contenu():
    corps = "".join(f"<tr><td>{escape(n)}</td><td>{escape(u)}</td></tr>" for n, u in M.CONTENU)
    return f'<table class="orga"><thead><tr><th>Meuble</th><th>Contenu</th></tr></thead><tbody>{corps}</tbody></table>'


def contenu():
    caissons = [b for b in M.MEUBLES if b.role == "caisson" and b.y0 == 0]
    x0, x1 = caissons[0].x0, caissons[-1].x1
    hauts = [b for b in M.MEUBLES if b.role == "caisson_haut"]
    cols = [b for b in M.MEUBLES if b.role == "colonne" and b.nom.startswith("caisson_c")]
    tp = M.TRIANGLE
    cotes_tri = [math.dist(a[1], b[1]) for a, b in zip(tp, tp[1:] + tp[:1])]
    tri = ", ".join(f"{a[0]} → {b[0]} {d:.0f}" for (a, b), d in zip(zip(tp, tp[1:] + tp[:1]), cotes_tri))
    lignes = "".join(f'<tr><td class="mono">{v}</td><td class="mono">{d}</td><td>{escape(c)}</td></tr>'
                     for v, d, c in M.CHANGEMENTS)
    return f"""<div class="kicker">Cuisine · {M.VERSION}</div>
<h1>Plan de la cuisine V12</h1>
<p class="pitch">Nouveau départ depuis la pièce vide. Le plan et la coupe sont générés depuis le modèle 3D : une seule source, aucune cote reportée à la main.</p>

<h2>Plan</h2>
<div class="fig"><div class="tog"><span>Portes</span><button type="button" data-vt="entree" aria-pressed="false" data-on="ouverte" data-off="fermée">entrée : fermée</button>{"".join(f'<button type="button" data-vt="{k}" aria-pressed="true" data-on="ouverte" data-off="fermée"' + (' data-etats="ouvert|mi|ferme" data-libs="ouverte|mi-ouverte|fermée" data-i="1"' if M.PLIANTE else '') + '>cellier : ' + ('mi-ouverte' if M.PLIANTE else 'ouverte') + '</button>' for k in (["cellier"] if M.PLIANTE else range(len(M.CELLIER_VANTAUX))))}</div><div class="scroll">{plan_svg()}</div>
<p class="cap">Échelle : 1 unité = 1 cm. Pièce vide : chambre et ancien cellier ouverts, sans cloison. Restent la fenêtre coulissante du mur ouest (y 58 → 200), la porte d'entrée (baie x 228 → 306), le décroché de l'angle sud-est, la chute (sous le ballon), le ballon et le WC. <b>Sols</b> : parquet chêne en bâtons rompus dans l'ancienne chambre (x 0 → 325), gris ciment dans l'ancien cellier et l'ancien placard (à partir de x 325) ; les cloisons déposées du relevé d'origine sont en tireté (chambre / cellier x 325 → 335, cellier / placard y 100 → 110). <b>Mur nord</b> : {len(caissons)} meubles bas de {' + '.join(f(w) for w in M.LARGEURS_BAS)} (x {f(x0)} → {f(x1)}), à {f(M.ECART_OUEST)} du mur ouest ; caisson P{M.P_CAISSON} + façade {M.FACADE}, profondeur {M.P_CAISSON + M.FACADE}, sous un plan de travail de 4 (P62, débord de 2). <b>Induction</b> 60 classique, four encastré dessous et hotte intégrée dans H1 au-dessus, sur B{M.B_PLAQUE} (x {f(M.sur_bas(M.B_PLAQUE)[0])} → {f(M.sur_bas(M.B_PLAQUE)[1])}) ; <b>évier</b> inox 1 bac 56 × 50 (bac 40 × 40) sur B{M.B_EVIER} (x {f(M.sur_bas(M.B_EVIER)[0])} → {f(M.sur_bas(M.B_EVIER)[1])}), mitigeur derrière le bac, égouttoir à gauche au-dessus de B4 ; la rangée s'arrête à l'évier. <b>Mur est</b> : colonne C3 (maxi tiroir coulissant, y {f(M.JOUE_C2)} → {f(M.COL_Y0)}), colonnes C2 (frigo, y {f(M.COL_Y0)} → {f(M.COL_Y0 + 60)}) et C1 (four, micro-ondes au-dessus, y {f(M.COL_Y0 + 60)} → {f(M.COL_Y1)}) de 60, P60, contre le mur du WC (x {f(M.X_MUR_EST)}), du décroché vers le nord, façades vers l'ouest (x {f(M.COL_X)}). Le mur sud est libre entre la banquette et le caisson du galandage. <b>Porte d'entrée</b> : à galandage, vantail {f(M.ENTREE["vantail"])} × {M.ENTREE["h"]} (trait plein, fermé) ; ouverte, elle rentre vers l'ouest dans un caisson de galandage (ocre, x {f(M.ENTREE["poche"][0])} → {f(M.ENTREE["poche"][1])}) logé dans un doublage de 10 contre le mur sud (y 242 → 252), avec un montant de 4 à l'est de la baie. Le passage reste de {f(M.ENTREE["x1"] - M.ENTREE["x0"])} ; rien ne bat dans la cuisine. Face cuisine du caisson : <b>tableau noir</b> (peinture ardoise, h 120 → 200) et <b>zone aimantée</b> en dessous (h 70 → 118), sur 81 de large (coupe B-B). <b>Équipements</b> : poubelles de tri sous l'évier (B{M.B_EVIER}), four sous la plaque (B{M.B_PLAQUE}), lave-vaisselle 60 tout intégrable en hauteur dans C1. <b>Triangle d'activité</b> (rouge ; centres de la plaque et de l'évier, milieu de la façade du frigo) : {tri}, total {f(round(sum(cotes_tri)))} cm. <b>Passage</b> (cote oblique) : {math.dist((x1, 62), (M.COL_X, M.JOUE_C2)):.0f} du coin du plan de travail au bout de la rangée (x {f(x1)}, y 62) au coin nord-ouest du frigo (joue, y {M.JOUE_C2}), devant la porte du cellier. <b>Réseaux</b> (bleu ; pose type IKEA METOD, sans vide technique : 1 cm de jeu derrière les caissons). Le <b>LV</b>, en hauteur dans C1, est raccordé par le cellier sans le traverser : alimentation depuis la nourrice le long du mur est puis du mur nord du WC, sous le rayonnage sud, jusqu'au dos de C1 ; vidange pompée par le LV le long du même mur, directement dans la chute. À l'est de l'évier, les tuyaux passent dans un <b>coffre bas</b> couleur des murs contre le mur nord (x {f(M.COFFRE_RESEAUX[0])} → {f(M.COFFRE_RESEAUX[1])}, P{M.COFFRE_RESEAUX[3]}, h {M.COFFRE_RESEAUX[5]}, dessus utilisable en tablette), puis dans le retour de cloison au nord de la porte du cellier : tout <b>longe les murs</b>, en partie basse. Alimentation EF/EC en trait plein, à 3 des murs, depuis la <b>nourrice</b> (petit point, sous le ballon) : le long du retour sud de l'alcôve (y 44), de sa face ouest (x 434), puis du mur nord jusqu'à l'évier ; une seconde ligne va au LV (C1) le long du mur nord du WC. Dans la niche du cellier, tout reste dans la zone technique des {M.ZONE_TECH} premiers cm (la chute est basse, dernier étage) : l'alimentation y passe à h 20 et remonte dans l'angle, l'évacuation descend à h 25 sous la première tablette du rayonnage nord ; un coffre technique (h 0 → {M.ZONE_TECH}) couvre l'angle. Évacuation en tireté depuis le siphon de l'évier (axe x {f(M.SIPHON[0])}), à 4 du mur nord dans la cuisine, puis à 12 des murs pour passer au-delà de la nourrice : le long du mur nord, de l'alcôve, du mur est (x 484) puis du mur nord du WC jusqu'à la <b>chute</b> (cercle contre le mur du WC, sous le ballon : la colonne d'eaux usées existante, x à confirmer). Contre l'alcôve, ils passent sous la première tablette du rayonnage du mur nord ; sous le ballon (h 90), ils passent dessous ; longueur ≈ {f(M.EVAC_LONGUEUR)} : de h {M.RESEAUX[3][3]} sous le siphon à h {M.RESEAUX[4][3]} à la chute, soit {(M.RESEAUX[3][3] - M.RESEAUX[4][3]) / M.EVAC_LONGUEUR * 100:.1f} cm/m de pente moyenne (hauteur d'arrivée sur la chute à confirmer). Les réseaux traversent la cloison du cellier. <b>Cellier</b> : cloison de 7 (x 320 → 327), à {f(320 - x1)} de B{M.N_BAS}. {texte_cellier()} <b>Coin repas</b> : banquette contre le mur sud, du mur ouest au retour du doublage de l'entrée (x 0 → {f(M.BANQ["x1"])}, 50 de profondeur : assise 45 à h 45 avec coffre, dossier 5 à h 85) ; table type Véra {M.TABLE["cote"]} × {M.TABLE["cote"]} aux angles arrondis (rose poudré, chant noir), sur un pied central à embase, devant, à 10 de l'assise (x {f(M.TABLE["x0"])} → {f(M.TABLE["x1"])}, y {f(M.TABLE["y0"])} → {f(M.TABLE["y1"])}) ; pas de chaise. Pan de mur derrière la banquette peint en vert profond (voir Matériaux). La banquette s'arrête à y {f(M.BANQ["y0"])}, au sud de la fenêtre (y 200). <b>Suspension</b> (tireté jaune) : point lumineux au plafond centré sur la table, abat-jour Ø {M.SUSPENSION["d"]}, bas à h {M.SUSPENSION["z0"]}, soit {M.SUSPENSION["z0"] - 75} au-dessus du plateau (coupe B-B). <b>Places</b> : {M.PLACES_BANQUETTE} adultes à l'aise sur la banquette ({f(M.BANQ["x1"] - M.BANQ["x0"])} de long, {M.LARGEUR_PLACE} par personne), 3 en se serrant ; un tabouret pliant côté nord en appoint. <b>Sous la banquette</b> : deux tiroirs (façades h 6 → 40), de part et d'autre du pied de la table ; ils passent au-dessus de l'embase (tireté : tiroirs sortis de 35). <b>Au-dessus</b> (tireté) : étagère P25 contre le mur sud, sur toute la longueur de la banquette, dessus à h {f(M.ETAGERE_BANQ["z1"])}, avec l'enceinte audio (22 × 18 × 30) à l'est et la plante à l'ouest (coupe B-B). <b>Ouvertures</b> : porte du LV abattue (y 60 → 132), porte du four abattue (x {f(M.COL_X - 60)} → {f(M.COL_X)}, y {f(M.COL_Y1 - 60)} → {f(M.COL_Y1)}), porte du frigo à 90°, charnières au sud : elle se rabat vers le sud et on accède au frigo par le nord, côté évier. Elle touche la porte du four abattue à y {f(M.COL_Y0 + 60)} : on ne les ouvre pas en même temps. <b>Meubles hauts</b> (tireté) : {len(hauts)} de {' + '.join(f(w) for w in M.LARGEURS_HAUTS)}, x {f(hauts[0].x0)} → {f(hauts[-1].x1)}, joints au droit de ceux des bas ; à leur gauche, étagères ouvertes jusqu'au mur ouest ; caisson P{M.P_HAUT} + façade {M.FACADE}.</p></div>

<h2>Coupe A-A · mur nord</h2>
<div class="fig"><div class="scroll">{coupe_a()}</div>
<p class="cap">Coupe à y {COUPE_A}, regard vers le nord. Socle {M.SOCLE}, caissons bas h {M.SOCLE} → {M.CAISSON_H}, plan de travail 4 (h {M.CAISSON_H} → {M.PT_Z1}), meubles hauts h {M.HAUT_Z0} → {M.HAUT_Z1}, fileur de {M.H - M.HAUT_Z1} jusqu'au plafond ({M.H}). <b>Ruban LED</b> (jaune) sous H1 → H{M.N_HAUTS}, vers l'avant, pour éclairer le plan de travail. <b>Façades</b> : organisation tout en tiroirs ; les traits épais sont les poignées.</p></div>

<h2>Coupe B-B · mur sud</h2>
<div class="fig"><div class="scroll">{coupe_b()}</div>
<p class="cap">Coupe à y {COUPE_B}, regard vers le sud : l'est est à gauche. <b>Porte d'entrée</b> : baie {f(M.ENTREE["x1"] - M.ENTREE["x0"])} × {M.ENTREE["h"]}, porte à galandage, vantail {f(M.ENTREE["vantail"])} × {M.ENTREE["h"]} (fermé), qui rentre à droite dans le caisson du doublage (poche {f(M.ENTREE["poche"][1] - M.ENTREE["poche"][0])}). Sur le caisson, <b>tableau noir</b> h 120 → 200 et <b>zone aimantée</b> h 70 → 118. Banquette et table coupées, pan de mur vert derrière, avec l'étagère P25 au-dessus (h {f(M.ETAGERE_BANQ["z0"])} → {f(M.ETAGERE_BANQ["z1"])}) et l'enceinte audio ; à gauche, la colonne C2 coupée (C1 derrière). À droite, la fenêtre coupée ; au centre, la baie d'entrée et son vantail fermé.</p></div>

<h2>Coupe C-C · mur est</h2>
<div class="fig transp"><div class="tog"><span>Porte du cellier</span><button type="button" class="trbtn" aria-pressed="true">en transparence</button></div><div class="scroll">{coupe_c()}</div>
<p class="cap">Coupe à x {COUPE_C}, regard vers l'est : le nord est à gauche. Au fond, la cloison du cellier (x 320 → 327), et dans son prolongement la porte du cellier fermée ({M.PORTE_TITRE}), dessinée en transparence (tireté) avec son dormant et son linteau (bouton au-dessus de la coupe : transparente ou normale), pour montrer le fond du cellier : le ballon. Puis, contre le mur du WC (x {f(M.X_MUR_EST)}), les colonnes P{M.P_CAISSON + M.FACADE}, socle {M.SOCLE}, dessus à {M.COL_Z1} comme les meubles hauts, fileur de {M.H - M.COL_Z1} jusqu'au plafond : <b>C2</b> réfrigérateur intégrable (niche 178, porte h 15 → 193), porte de rangement au-dessus ; <b>C1</b> un tiroir (h 15 → {M.LV_Z0}), lave-vaisselle intégré en hauteur (h {M.LV_Z0} → {M.MO_Z0}), micro-ondes encastrable (niche 38, h {M.MO_Z0} → {M.MO_Z1}), porte de rangement au-dessus ; à droite, le décroché et le mur sud coupé.</p></div>

{galerie_rendus()}<h2>Matériaux</h2>
<div class="fig">{table_materiaux()}
<p class="cap">Teintes indicatives à l'écran : Canopée et chêne miel d'après le rendu 3D (laque mate Plum Living), parquet d'après la photo de référence. À valider sur échantillons.</p></div>

<h2>Contenu des rangements</h2>
<div class="fig">{table_contenu()}
<p class="cap">Organisation A, tout en tiroirs, électroménager inchangé : tout se voit d'en haut, sans se baisser ni vider l'avant (coulisses plus chères que des charnières). Le contenu est aussi écrit en italique sur les façades, dans les coupes A-A (mur nord), B-B (banquette) et C-C (colonnes). Rangement proche de l'usage : ustensiles, poêles et épices autour de la plaque ; assiettes au-dessus du LV ; couverts, verres et tasses dans C3 (tiroirs à l'anglaise), à côté du frigo.</p></div>

{section_capacite(M.VERSION, lignes_avant_apres(), details_capacite())}
<p class="note">Repère : x vers l'est depuis le mur ouest, y vers le sud depuis le mur nord, z depuis le sol fini, en cm. Source : <span class="mono">3d/v12/modele.py</span> ; plan : <span class="mono">3d/v12/plan.py</span> ; 3D : <span class="mono">3d/v12/cad.py</span>.</p>

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
    barre = (f'<div class="vbar"><a class="back" href="{racine}index.html">← Plans</a>{versions}'
             f'<button type="button" class="expl" aria-pressed="false">Explications</button>'
             f'<button type="button" class="chg" aria-pressed="false">Changements</button></div>')
    return f"""<!doctype html>
<html lang="fr">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Cuisine V12</title>
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
  var bs = document.querySelectorAll(".vbar button[data-v]"), vs = document.querySelectorAll(".ver");
  function montre(v) {{
    if (!document.querySelector('.ver[data-v="' + v + '"]')) v = "courante";
    vs.forEach(function (d) {{ d.hidden = d.dataset.v !== v; }});
    bs.forEach(function (b) {{ b.setAttribute("aria-pressed", b.dataset.v === v); }});
    try {{ localStorage.setItem("cuisine-v12-version", v); }} catch (e) {{}}
  }}
  bs.forEach(function (b) {{ b.addEventListener("click", function () {{ montre(b.dataset.v); }}); }});
  document.querySelectorAll(".tog .trbtn").forEach(function (b) {{
    b.addEventListener("click", function () {{
      var on = b.getAttribute("aria-pressed") !== "true";
      b.closest(".fig").classList.toggle("transp", on);
      b.setAttribute("aria-pressed", on);
      b.textContent = on ? "en transparence" : "normale";
    }});
  }});
  document.querySelectorAll(".tog button[data-vt]").forEach(function (b) {{
    b.addEventListener("click", function () {{
      var fig = b.closest(".fig");
      if (b.dataset.etats) {{   // porte à trois états : ouverte → mi-ouverte → fermée
        var es = b.dataset.etats.split("|"), ls = b.dataset.libs.split("|"), i = ((+b.dataset.i || 0) + 1) % es.length;
        b.dataset.i = i;
        fig.querySelectorAll('.vt[data-vt="' + b.dataset.vt + '"]').forEach(function (g) {{ g.dataset.etat = es[i]; }});
        b.setAttribute("aria-pressed", es[i] !== "ferme");
        b.textContent = b.textContent.replace(/: .*/, ": " + ls[i]);
        return;
      }}
      var ouvert = b.getAttribute("aria-pressed") !== "true";
      fig.querySelectorAll('.vt[data-vt="' + b.dataset.vt + '"]').forEach(function (g) {{ g.dataset.etat = ouvert ? "ouvert" : "ferme"; }});
      b.setAttribute("aria-pressed", ouvert);
      b.textContent = b.textContent.replace(/: .*/, ": " + (ouvert ? b.dataset.on : b.dataset.off));
    }});
  }});
  document.querySelectorAll(".rtog button[data-rv]").forEach(function (b) {{
    b.addEventListener("click", function () {{
      var g = b.closest(".rgrp");
      g.querySelectorAll(".rtog button").forEach(function (x) {{ x.setAttribute("aria-pressed", x === b); }});
      g.querySelectorAll("figure[data-rv]").forEach(function (f) {{ f.hidden = f.dataset.rv !== b.dataset.rv; }});
    }});
  }});
  var be = document.querySelector(".vbar .expl");
  function expl(on) {{
    document.body.classList.toggle("explications", on);
    be.setAttribute("aria-pressed", on);
    try {{ localStorage.setItem("cuisine-v12-expl", on ? "1" : ""); }} catch (e) {{}}
  }}
  be.addEventListener("click", function () {{ expl(be.getAttribute("aria-pressed") !== "true"); }});
  try {{ expl(localStorage.getItem("cuisine-v12-expl") === "1"); }} catch (e) {{ expl(false); }}
  var bc = document.querySelector(".vbar .chg");
  function chg(on) {{
    document.body.classList.toggle("changements", on);
    bc.setAttribute("aria-pressed", on);
    try {{ localStorage.setItem("cuisine-v12-chg", on ? "1" : ""); }} catch (e) {{}}
  }}
  bc.addEventListener("click", function () {{ chg(bc.getAttribute("aria-pressed") !== "true"); }});
  try {{ chg(localStorage.getItem("cuisine-v12-chg") === "1"); }} catch (e) {{ chg(false); }}
  var v0 = "courante";
  try {{ v0 = localStorage.getItem("cuisine-v12-version") || v0; }} catch (e) {{}}
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
    # les rendus du moment sont copiés dans cuisine-v12-3d/<version>/ : les rendus suivants ne les écrasent pas
    import shutil
    src3d, dst3d = os.path.join(ROOT, "cuisine-v12-3d"), os.path.join(ROOT, "cuisine-v12-3d", v)
    os.makedirs(dst3d, exist_ok=True)
    for nom in os.listdir(src3d):
        if nom.endswith(".jpg"):
            shutil.copy2(os.path.join(src3d, nom), dst3d)
    rendus = lambda html, racine="": re.sub(r'src="cuisine-v12-3d/(\w+)\.jpg(\?v=[^"]*)?"',
                                             rf'src="{racine}cuisine-v12-3d/{v}/\1.jpg"', html)
    c = rendus(contenu())
    for ident in set(re.findall(r'id="([^"]+)"', c)):
        c = c.replace(f'id="{ident}"', f'id="{ident}-{v}"').replace(f"url(#{ident})", f"url(#{ident}-{v})")
    with open(os.path.join(FIGEES, f"{v}.html"), "w", encoding="utf-8") as fh:
        fh.write(c)
    with open(os.path.join(ROOT, "archive", f"cuisine-{v.lower()}.html"), "w", encoding="utf-8") as fh:
        fh.write(rendus(page([], "../"), "../"))
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
