# Génère sdb-meuble-v3.html (plan, élévation, coupes, débit) depuis modele.py.
#
#   python3 3d/sdb/plan.py            (just sdb)
#   python3 3d/sdb/plan.py --figer    (just sdb-figer : fige la version courante)
#
# Le plan et les coupes sont des projections des pièces du modèle : rien n'est dessiné à la main.

import os
import re
import sys
from collections import Counter
from html import escape

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import modele as M  # noqa: E402
import calepinage as CAL  # noqa: E402

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
ANCRES = open(os.path.join(ROOT, "3d", "ancres.js"), encoding="utf-8").read()   # ancres communes des pages à sommaire
OUT = os.path.join(ROOT, "sdb-meuble-v3.html")
NOTICE = "sdb-meuble-v3-montage.html"
CLE = "sdb-v3"          # préfixe des préférences mémorisées (localStorage)

Z_COUPE_PLAN = 80       # le plan vu de dessus est une coupe horizontale sous le plan de travail (V4 : 100 → 90 → 88 ; V5 : 80)
COUPE_B = 80            # y, regard vers le nord : machine, passe-tuyau, robinet


def roul(c):
    """Variante V5.17 : linge sale en deux paniers à roulettes (code de version terminé par "r")."""
    return c.endswith("r")


def coupe_c(c):         # y, regard vers le nord : à travers le sac nord (variante : le panier nord)
    s0 = M.PANIERS[0] if roul(c) else M.SACS[0]
    y = (s0.y0 + s0.y1) / 2
    return y if c != "g" else M.Y1 - y


def virg(v, n=1):
    return f"{v:.{n}f}".replace(".", ",").replace(",0", "") if n else f"{v:.0f}"


def f(v):
    return f"{round(v, 2):g}"


def cm(v):
    """Cote en cm affichée : 1 décimale au plus, virgule française."""
    return f"{round(v, 1):g}".replace(".", ",")


def rect(x0, y0, x1, y1, cls, extra=""):
    return f'<rect class="{cls}" x="{f(x0)}" y="{f(y0)}" width="{f(x1 - x0)}" height="{f(y1 - y0)}"{extra}/>'


def poly(pts, cls):
    return f'<polygon class="{cls}" points="{" ".join(f"{f(u)},{f(v)}" for u, v in pts)}"/>'


def text(x, y, s, cls="lbl", anchor="middle", extra=""):
    return f'<text class="{cls}" x="{f(x)}" y="{f(y)}" text-anchor="{anchor}"{extra}>{escape(s)}</text>'


def cote_h(x0, x1, y, label=None, t=2):
    label = label or cm(abs(x1 - x0))
    return "".join([
        f'<line class="dim" x1="{f(x0)}" y1="{f(y)}" x2="{f(x1)}" y2="{f(y)}"/>',
        f'<line class="dim" x1="{f(x0)}" y1="{f(y - t)}" x2="{f(x0)}" y2="{f(y + t)}"/>',
        f'<line class="dim" x1="{f(x1)}" y1="{f(y - t)}" x2="{f(x1)}" y2="{f(y + t)}"/>',
        text((x0 + x1) / 2, y - 1.6, label, "dimt"),
    ])


def cote_v(y0, y1, x, label=None, t=2):
    label = label or cm(abs(y1 - y0))
    ym = (y0 + y1) / 2
    return "".join([
        f'<line class="dim" x1="{f(x)}" y1="{f(y0)}" x2="{f(x)}" y2="{f(y1)}"/>',
        f'<line class="dim" x1="{f(x - t)}" y1="{f(y0)}" x2="{f(x + t)}" y2="{f(y0)}"/>',
        f'<line class="dim" x1="{f(x - t)}" y1="{f(y1)}" x2="{f(x + t)}" y2="{f(y1)}"/>',
        text(x - 1.6, ym, label, "dimt", extra=f' transform="rotate(-90 {f(x - 1.6)} {f(ym)})"'),
    ])


def sens(c, nord, sud):
    """Texte qui dépend du côté : nord dans la version d pour les bacs, etc."""
    return nord if c != "g" else sud


# ------------------------------------------------------------------ styles par rôle : (vu, coupé)
CLS = {"socle": ("socle", "soclec"), "rebord": ("socle", "soclec"), "caisson": ("cab", "cabc"), "fond": ("fond", "fondc"),
       "plinthe": ("plinthe", "cabc"), "bac": ("bac", "bacc"), "facade": ("fac", "facc"), "tasseau": ("tas", "tasc"),
       "corniere": ("alu", "alu"), "plan": ("top", "topc"), "trappe": ("trap", "trap"), "etagere": ("shelf", "shelfc"),
       "porte": ("porte", "portec"), "fileur": ("cab", "cabc"), "machine": ("appf", "appc"), "led": ("led", "led"),
       "prise": ("plug", "plug"), "pied": ("appf", "appc"), "vis": ("alu", "alu"),
       "support": ("cab", "cabc"), "barre": ("tas", "tasc"), "sac": ("sac", "sacc"), "bois": ("dg", "dgc"),
       "panier": ("panier", "panierc")}


# ------------------------------------------------------------------ plan vu de dessus (coupe horizontale à z 100)
def leaf():
    return (M.PORTE["x1"] - 4, 0, M.PORTE["x1"], M.PORTE["l"])   # vantail ouvert à 90°, x0 y0 x1 y1


def inter(a, b):
    x0, y0, x1, y1 = max(a[0], b[0]), max(a[1], b[1]), min(a[2], b[2]), min(a[3], b[3])
    return (x0, y0, x1, y1) if x0 < x1 and y0 < y1 else None


def bacs_y(c):
    return (M.CB["y0"], M.CB["y1"]) if c != "g" else (M.Y1 - M.CB["y1"], M.Y1 - M.CB["y0"])


def plan_svg(c):
    blocs = M.version(c)
    o = []
    sol = [(0, 0), (234, 0), (234, M.Y1), (M.X0, M.Y1), (M.X0, 160), (0, 160)]
    o.append(poly(sol, "sdbf"))
    o.append(f'<path class="w" fill-rule="evenodd" d="M-5 -5 H239 V{M.Y1 + 5} H{M.X0 + 5} V165 H-5 Z M0 0 V160 H{M.X0} V{M.Y1} H234 V0 Z"/>')
    p = M.PORTE
    o.append(rect(p["x0"], -5.5, p["x1"], 0.5, "", ' style="fill:var(--paper)"'))
    o.append(f'<path class="doorzone" d="M{p["x0"]} 0 A{p["l"]} {p["l"]} 0 0 0 {p["x1"]} {p["l"]} L{p["x1"]} 0 Z"/>')
    o.append(f'<path class="doorarc" d="M{p["x0"]} 0 A{p["l"]} {p["l"]} 0 0 0 {p["x1"]} {p["l"]}"/>')
    lf = leaf()
    o.append(rect(*lf, "leaf"))
    o.append(text((p["x0"] + p["x1"]) / 2, -8, f"porte d'entrée {p['l']} · vantail dessiné ouvert à 90°", "lblx muted"))
    d, lv = M.DOUCHE, M.LAVABO
    o.append(rect(*d, "fixe"))
    o.append(text((d[0] + d[2]) / 2, (d[1] + d[3]) / 2, "Douche", "lbl rt"))
    o.append(rect(*lv, "fixe"))
    o.append(text((lv[0] + lv[2]) / 2, (lv[1] + lv[3]) / 2 + 2, "Lavabo", "lbl rt"))
    # pièces sous z 100, de bas en haut ; coupées par le plan horizontal en foncé
    for b in sorted([b for b in blocs if b.z0 < Z_COUPE_PLAN and b.role not in ("prise", "trappe")], key=lambda b: b.z1):
        vu, coupe = CLS[b.role]
        o.append(rect(b.x0, b.y0, b.x1, b.y1, coupe if b.z1 > Z_COUPE_PLAN else vu))
    ya, yb = bacs_y(c)
    if roul(c):
        # V5.18 : pas de porte ; panier tiré (tireté) : il sort de toute sa profondeur
        pa = M.PANIERS[0]
        bas = (pa.x0 - (pa.x1 - pa.x0), pa.y0, pa.x0, pa.y1)
        o.append(rect(*bas, "swing"))
        o.append(text((bas[0] + bas[2]) / 2, (pa.y0 + pa.y1) / 2 + 1.2, "panier tiré", "lblx muted"))
    else:
        # bacs basculés (tireté) : emprise de la façade avancée
        av = M.BAC["avancee"]
        bas = (M.FACE - av, ya + 0.15, M.FACE, yb - 0.15)
        o.append(rect(*bas, "swing"))
        o.append(text(M.FACE - av / 2, (ya + yb) / 2 + 1.5, "porte basculée", "lblx muted",
                      extra=f' transform="rotate(-90 {f(M.FACE - av / 2)} {f((ya + yb) / 2 + 1.5)})"'))
    # hublot : charnière à gauche (face au meuble, donc au nord) ; 180° si rien ne l'arrête, 90° contre le mur nord
    m = [b for b in blocs if b.role == "machine"][0]
    cx, r = M.MACHINE.x0 - 1.5, 23.5
    yh = m.y0 + 6
    if c != "g":
        o.append(f'<path class="swing" d="M{f(cx)} {f(yh + 2 * r)} A{r} {r} 0 0 1 {f(cx)} {f(yh)}"/>')
        o.append(f'<line class="swing" x1="{f(cx - 1)}" y1="{f(yh)}" x2="{f(cx - 1)}" y2="{f(yh - 2 * r)}" style="stroke-width:1.2"/>')
        hub = (cx - 3, yh - 2 * r, cx - 1, yh)
    else:
        o.append(f'<path class="swing" d="M{f(cx)} {f(yh + 2 * r)} A{2 * r} {2 * r} 0 0 1 {f(cx - 2 * r)} {f(yh)}"/>')
        o.append(f'<line class="swing" x1="{f(cx)}" y1="{f(yh)}" x2="{f(cx - 2 * r)}" y2="{f(yh)}" style="stroke-width:1.2"/>')
        hub = (cx - 2 * r, yh - 1, cx, yh + 1)
    o.append(text(M.FACE - 32, (m.y0 + m.y1) / 2 + 2, "hublot", "lblx muted"))
    # recouvrements avec le vantail ouvert
    for zone in (bas, hub):
        z = inter(zone, lf)
        if z:
            o.append(rect(*z, "conf"))
    # au-dessus : plan de travail (pointillé fin), trappe, hauts (pointillé épais)
    pl = [b for b in blocs if b.role == "plan"][0]
    o.append(rect(pl.x0, pl.y0, pl.x1, pl.y1, "planl"))
    tr = M.TRAPPE
    o.append(rect(tr["x0"], tr["y0"], tr["x1"], tr["y1"], "trap"))
    o.append(f'<circle class="valve" cx="{f(M.X1 - 1.5)}" cy="{f(M.ROBINET["y"])}" r="1.6"/>')
    ch = M.CH
    if c[0] == "m":
        ym = M.Y0 + 0.5 + M.METOD["l"]
        o.append(rect(M.METOD["x0"], ch["y0"], ch["x1"], ch["y1"], "upper"))
        o.append(f'<line class="upper" x1="{f(M.METOD["x0"])}" y1="{f(ym)}" x2="{ch["x1"]}" y2="{f(ym)}"/>')
    else:
        o.append(rect(ch["x0"], ch["y0"], ch["x1"], ch["y1"], "upper"))
        o.append(f'<line class="upper" x1="{ch["x0"]}" y1="{M.CENTRE}" x2="{ch["x1"]}" y2="{M.CENTRE}"/>')
    # étiquettes
    xm = (M.CB["x0"] + M.CB["x1"]) / 2
    if roul(c):
        for k, pa in enumerate(M.PANIERS):
            o.append(text((pa.x0 + pa.x1) / 2, (pa.y0 + pa.y1) / 2 + 1.5, f"panier {k + 1} · {M.CORNO['litres']} L", "lblx"))
    else:
        o.append(text(xm, (ya + yb) / 2 - 2, "Bac : 2 sacs", "lbls"))
        o.append(text(xm, (ya + yb) / 2 + 4, "porte basculante", "lblx"))
    o.append(text((m.x0 + m.x1) / 2, (m.y0 + m.y1) / 2 - 2, "LL", "lblb"))
    o.append(text((m.x0 + m.x1) / 2 - 8, (m.y0 + m.y1) / 2 + 8, "au sol, sur tapis", "lblx"))
    o.append(f'<path class="lead" d="M{f(tr["x0"])} {f(tr["y1"] - 4)} L{f(tr["x0"] - 9)} {f(tr["y1"] - 4)}"/>')
    o.append(text(tr["x0"] - 10, tr["y1"] - 3, "passe-tuyau, robinet au-dessus", "lblx", "end"))
    # cotes
    o.append(cote_h(M.X1 - M.ALCOVE["nord"], M.X1, -14, f"{M.ALCOVE['nord']} (mur nord)"))
    o.append(cote_h(M.X0, M.X1, M.Y1 + 12, f"{M.ALCOVE['sud']} (mur sud)"))
    o.append(cote_h(0, 234, -22, "234"))
    o.append(cote_v(0, 160, -12, "160"))
    o.append(cote_v(0, M.Y1, 262, cm(M.Y1)))
    o.append(cote_v(ya, yb, 250, cm(yb - ya)))
    ly = (M.LLZ["y0"], M.LLZ["y1"]) if c != "g" else (M.Y1 - M.LLZ["y1"], M.Y1 - M.LLZ["y0"])
    o.append(cote_v(*ly, 250, f"{cm(ly[1] - ly[0])} LL"))
    o.append(cote_h(lf[2], M.FACE, 104, cm(M.FACE - lf[2])))
    # traits de coupe
    yc = coupe_c(c)
    for y, lab in ((COUPE_B, "B"), (yc, "C")):
        o.append(f'<line class="sec" x1="140" y1="{f(y)}" x2="244" y2="{f(y)}"/>')
        o.append(text(136, y + 2, lab, "sect"))
    o.append(f'<path class="secm" d="M164 -2 l-4 -3 v6z"/>')
    o.append(text(158, 3, "A", "sect", "end"))
    o.append(text(117, 178, f"N ↑ · coupe horizontale à {Z_COUPE_PLAN} · plan de travail en pointillé fin, hauts P 45 en pointillé épais",
                  "lblx muted"))
    return f'<svg viewBox="-24 -32 304 216" role="img" aria-label="Plan, {M.VERSIONS[c]}">{"".join(o)}</svg>'


# ------------------------------------------------------------------ élévation et coupes (projection des pièces)
def visibles(blocs, axe, cut, regard):
    """axe "y" : coupe à y = cut, regard vers le nord (-1) ; axe "x" : à x = cut, regard vers l'est (+1).
    Renvoie [(coupée, pièce)] du plus loin au plus près ; les pièces coupées en dernier."""
    r = []
    for b in blocs:
        a0, a1 = (b.y0, b.y1) if axe == "y" else (b.x0, b.x1)
        if (a0 < cut) if regard < 0 else (a1 > cut):
            r.append((a0 < cut < a1, a1 if regard < 0 else -a0, b))
    r.sort(key=lambda t: (t[0], t[1]))
    return [(c, b) for c, _, b in r]


def lignes_etiq(s):
    if len(s) <= 14:
        return [s]
    i = min((k for k, ch in enumerate(s) if ch == " "), key=lambda k: abs(k - len(s) / 2))
    return [s[:i], s[i + 1:]]


def vue(c, axe, cut, regard, u0, u1, extra=None, hauteurs=(), titre=""):
    blocs = M.version(c)
    o = []
    for coupe, b in visibles(blocs, axe, cut, regard):
        vu, cp = CLS[b.role]
        o.append(poly([(u, -z) for u, z in b.pts(axe)], cp if coupe else vu))
        if b.etiq and axe == "x" and not coupe:
            um, zm = (b.y0 + b.y1) / 2, (b.z0 + b.z1) / 2
            for i, ligne in enumerate(lignes_etiq(b.etiq)):
                o.append(text(um, -zm - 4 + i * 6, ligne, "lbls"))
    if extra:
        o += extra(blocs)
    o.append(f'<line class="floorl" x1="{f(u0)}" y1="0" x2="{f(u1)}" y2="0"/>')
    o.append(f'<line class="ceil" x1="{f(u0)}" y1="{-M.H}" x2="{f(u1)}" y2="{-M.H}"/>')
    zs = [0] + list(hauteurs) + [M.H]
    for a, b in zip(zs, zs[1:]):
        o.append(cote_v(-a, -b, u0 - 8))
    o.append(cote_v(0, -M.H, u0 - 19))
    return (f'<svg viewBox="{f(u0 - 30)} -262 {f(u1 - u0 + 44)} 286" role="img" aria-label="{escape(titre)}">'
            f'{"".join(o)}</svg>')


def elevation(c):
    def extra(blocs):
        r = []
        m = [b for b in blocs if b.role == "machine"][0]
        ym, zm = (m.y0 + m.y1) / 2, m.z0 + 50
        r.append(f'<circle class="app" cx="{f(ym)}" cy="{f(-zm)}" r="17"/><circle class="app" cx="{f(ym)}" cy="{f(-zm)}" r="12.5"/>')
        r.append(f'<line class="app" x1="{f(m.y0 + 0.5)}" y1="{f(-(m.z1 - 14))}" x2="{f(m.y1 - 0.5)}" y2="{f(-(m.z1 - 14))}"/>')
        r.append(text(ym, -(m.z0 + 4), f"LL {M.LL['l']} × {M.LL['p']} × {M.LL['h']}", "lblx"))
        # trou de prise de la porte et sens de bascule
        ya, yb = bacs_y(c)
        if roul(c):
            r.append(text((ya + yb) / 2, -(M.CORNO["h"] + 8), f"2 paniers {M.CORNO['litres']} L, sans porte", "lblx"))
        else:
            for k, (z0, z1) in enumerate(M.FACADES):
                r.append(f'<circle class="handle" cx="{f((ya + yb) / 2)}" cy="{f(-(z1 - 3))}" r="1.25"/>')
                r.append(text((ya + yb) / 2, -(z0 + z1) / 2 + 6, f"2 sacs ≈ {M.VOLUME_BAC:.0f} L", "lblx"))
                r.append(text((ya + yb) / 2, -(z0 + z1) / 2 + 12, f"bascule à {M.BAC['angle']}°", "lblx"))
        # niche
        r.append(text(57, -(M.Z_HAUT - 10), f"Niche {cm(M.Z_HAUT - M.Z_DESSUS)} : prises + USB, crochet sèche-cheveux, LED",
                      "lblx"))
        r.append(f'<path class="hook" d="M6 {f(-(M.Z_HAUT - 5))} v6 q0 3 3 3"/>')
        # vantail ouvert (tireté rouge), devant
        r.append(rect(0 - 5, -204, M.PORTE["l"], 0, "leafg"))
        r.append(text(57, 19, f"tireté rouge : vantail de la porte ouvert à 90°, {cm(M.FACE - leaf()[2])} cm devant les façades", "lblx rt"))
        r.append(text(-3, 7, "nord · porte", "lblx muted", "start"))
        r.append(text(117, 7, "sud · lavabo", "lblx muted", "end"))
        ly = (M.LLZ["y0"], M.LLZ["y1"]) if c != "g" else (M.Y1 - M.LLZ["y1"], M.Y1 - M.LLZ["y0"])
        r.append(cote_h(ya, yb, 11, cm(yb - ya)))
        r.append(cote_h(*ly, 11, f"{cm(ly[1] - ly[0])} machine"))
        return r

    hz = [M.Z_PLAN, M.Z_DESSUS, M.Z_HAUT, M.METOD["z"][1] if c[0] == "m" else M.Z_HAUT1]
    return vue(c, "x", 150, +1, -6, 120, extra, hz, f"Élévation A, {M.VERSIONS[c]}")


def murs_coupe(r):
    r.append(rect(M.X1, -M.H - 4, M.X1 + 6, 4, "w"))
    lf = leaf()
    r.append(rect(lf[0], -204, lf[2], 0, "leafg"))
    r.append(text(lf[0] - 3, -140, "vantail ouvert à 90°", "lblx muted", extra=f' transform="rotate(-90 {f(lf[0] - 3)} -140)"'))
    r.append(text(150, -M.H - 6, "ouest ←   → est", "lblx muted"))


def coupe_b(c):
    def extra(blocs):
        r = []
        murs_coupe(r)
        m = [b for b in blocs if b.role == "machine"][0]
        r.append(text((m.x0 + m.x1) / 2, -(m.z0 + 30), f"LL {M.LL['l']} × {M.LL['p']} × {M.LL['h']}", "lbls"))
        r.append(text((m.x0 + m.x1) / 2, -(m.z0 + 24), f"jeu arrière {cm(M.X1 - m.x1)} · {cm(M.JEU_PLAN * 10)} mm sous le plant", "lblx"))
        r.append(text((m.x0 + m.x1) / 2, -(m.z0 + 4), "au sol, sur tapis antivibration", "lblx"))
        rb = M.ROBINET
        r.append(rect(M.X1 - 3, -(rb["z"] + 2), M.X1, -(rb["z"] - 2), "valve"))
        # étiquette dans la niche (sous le plan, les sacs occupent la place)
        r.append(f'<path class="lead" d="M{M.X1 - 2} {-rb["z"] - 2} L{M.X1 - 4} {-M.Z_DESSUS - 24}"/>')
        r.append(text(M.X1 - 5, -M.Z_DESSUS - 29, f"robinet h {rb['z']}, dans la niche", "lblx", "end"))
        r.append(text(M.X1 - 5, -M.Z_DESSUS - 24.5, "+ prise de la LL à côté", "lblx", "end"))
        r.append(f'<path class="lead" d="M{M.TRAPPE["x0"] + 4} {-M.Z_DESSUS - 1} L{M.TRAPPE["x0"] - 6} {-M.Z_DESSUS - 12}"/>')
        r.append(text(M.TRAPPE["x0"] - 7, -M.Z_DESSUS - 13, f"passe-tuyau {M.PASSE['l']} × {M.PASSE['p']}", "lblx", "end"))
        r.append(text(M.CH["x0"] - 2, -(M.Z_HAUT + 50), "serviettes", "lblx", "end"))
        r.append(text(M.CH["x0"] - 2, -(M.Z_HAUT + 44), "(au nord, au fond)", "lblx muted", "end"))
        r.append(text(M.FACE + 4, -(M.Z_DESSUS + 32), "niche", "lblx", "start"))
        r.append(cote_h(M.METOD["x0"], M.X1, -(M.H + 4)) if c[0] == "m" else cote_h(M.CH["x0"], M.CH["x1"], -(M.H + 4), "45"))
        r.append(cote_h(M.FACE, M.X1, 12, cm(M.X1 - M.FACE)))
        r.append(cote_h(leaf()[2], M.FACE, 12, cm(M.FACE - leaf()[2])))
        return r

    return vue(c, "y", COUPE_B, -1, 140, 244, extra, [M.SOCLE_H + M.LL["h"], M.Z_PLAN, M.Z_DESSUS, M.Z_HAUT],
               f"Coupe B-B, {M.VERSIONS[c]}")


def coupe_c_svg(c):
    yc = coupe_c(c)

    def extra_r(blocs):
        r = []
        murs_coupe(r)
        pa, co = M.PANIERS[0], M.CORNO
        r.append(text((pa.x0 + pa.x1) / 2, -(pa.z1 / 2 + 3), "Wenko Corno", "lblx"))
        r.append(text((pa.x0 + pa.x1) / 2, -(pa.z1 / 2 - 3), f"{co['litres']} L, à roulettes", "lblx"))
        rr = M.RAILS[1]
        r.append(f'<path class="lead" d="M{f(rr.x0 + 1)} {f(-rr.z1)} L{f(rr.x0 + 1)} {f(-(co["h"] + 4))}"/>')
        r.append(text(rr.x0, -(co["h"] + 5), "rail arrière (seul rail)", "lblx", "end"))
        r.append(text(M.FACE + 2, 6, "sans porte ni rail avant", "lblx", "start"))
        r.append(cote_h(M.FACE, pa.x1, 12, cm(pa.x1 - M.FACE)))
        r.append(cote_h(pa.x1, rr.x0, 12, cm(rr.x0 - pa.x1)))
        r.append(cote_h(M.METOD["x0"], M.X1, -(M.H + 4)) if c[0] == "m" else cote_h(M.CH["x0"], M.CH["x1"], -(M.H + 4), "45"))
        return r

    def extra(blocs):
        r = []
        murs_coupe(r)
        # L basculé (tireté) : porte, plateau, contrefiche, supports et barre de la porte tournés autour de l'axe ; le
        # sac ouvert va de la barre de la porte basculée à la barre arrière
        axe, a = M.BAC["axe"], M.BAC["angle"]
        for b in blocs:
            if b.groupe == "bac" and b.role in ("facade", "bac", "bois") or b.nom.startswith(("support_porte", "barre_porte")):
                if b.y0 <= coupe_c(c) + 4 and b.y1 >= M.Y0:
                    pts = [M.bascule(x, z, axe, a) for x, z in b.pts("y")]
                    r.append(poly([(x, -z) for x, z in pts], "swingp"))
        xf0, xr0, zb0, zb1 = M.BAC["barres"]
        bx = M.BAC["barre"][0]
        fa = M.bascule(xf0 + bx, zb0 + 1, axe, a)
        fb = M.bascule(M.XO1 - M.DL - 1, M.DL + M.T + 1, axe, a)
        fc = M.bascule(xf0 + 1, M.DL + M.T + 1, axe, a)
        r.append(poly([(fa[0], -fa[1]), (xr0, -(zb0 + 1)), (fb[0], -fb[1]), (fc[0], -fc[1])], "sacopen"))
        am = M.BAC["angle_max"]
        for b in blocs:
            if b.nom in ("bac_porte", "plateau"):
                pts = [M.bascule(x, z, axe, am) for x, z in b.pts("y")]
                r.append(poly([(x, -z) for x, z in pts], "leafg"))
        hm = M.bascule(M.FACE, M.FACADES[0][1], axe, am)
        r.append(text(hm[0] - 1, -hm[1] + 6, f"{am}° : sortie du sac", "lblx rt", "end"))
        r.append(f'<circle class="axe" cx="{f(axe[0])}" cy="{f(-axe[1])}" r="0.9"/>')
        r.append(text(M.CB["x0"] + 22, -40, f"sac ≈ {M.VOLUME_BAC:.0f} L", "lblx"))
        r.append(text(M.FACE - 16, -(M.FACADES[0][1] - 6), f"basculé {M.BAC['angle']}°", "lblx muted"))
        r.append(text(axe[0] + 1, 6, "axe : charnières plates sur le rail", "lblx", "start"))
        bu = M.BUTEE
        r.append(f'<path class="lead" d="M{f(bu.x0)} {f(-(bu.z0 + 1))} L{f(bu.x0 - 6)} {f(-(bu.z0 + 12))}"/>')
        r.append(text(bu.x0 - 7, -(bu.z0 + 13), "vis de butée", "lblx", "end"))
        r.append(f'<path class="lead" d="M{f(xr0 + 1)} {f(-zb1)} L{f(xr0 + 8)} {f(-(zb1 - 8))}"/>')
        r.append(text(xr0 + 9, -(zb1 - 9), f"barres Ø {bx * 10:.0f}", "lblx", "start"))
        r.append(cote_h(M.CB["x0"], xr0, 12, cm(M.BAC["prof"])))
        r.append(cote_h(M.FACE - M.BAC["avancee"], M.FACE, 12, cm(M.BAC["avancee"])))
        r.append(cote_h(M.METOD["x0"], M.X1, -(M.H + 4)) if c[0] == "m" else cote_h(M.CH["x0"], M.CH["x1"], -(M.H + 4), "45"))
        return r

    if roul(c):
        return vue(c, "y", yc, -1, 140, 244, extra_r, [M.CORNO["h"], M.Z_PLAN, M.Z_DESSUS, M.Z_HAUT],
                   f"Coupe C-C, {M.VERSIONS[c]}")
    return vue(c, "y", yc, -1, 140, 244, extra, [M.BAC["z_butee"], M.Z_PLAN, M.Z_DESSUS, M.Z_HAUT],
               f"Coupe C-C, {M.VERSIONS[c]}")


# ------------------------------------------------------------------ débit
def debit():
    """Une ligne par repère : quantité, longueur × largeur × épaisseur en mm (version d ; la version g a les mêmes pièces)."""
    lignes = {}
    for b in M.PIECES:
        if not b.rep:
            continue
        dims = tuple(sorted((b.x1 - b.x0, b.y1 - b.y0, b.z1 - b.z0), reverse=True))
        lignes.setdefault(b.rep, []).append(dims)
    cle = lambda r: (r[0], int(r[1:]))
    r = []
    for rep in sorted(lignes, key=cle):
        d = lignes[rep]
        L, l, e = (round(v * 10) for v in max(d))
        q = len(d)
        if rep == "E2":         # une cornière, modélisée en deux ailes
            q, l, e = 1, 30, 30
        if rep == "G11":        # écharpe : longueur de pointe à pointe, section du tasseau
            L, l, e = round(M.ECHARPE["L"] * 10), round(M.DL * 10), round(M.DE * 10)
        if rep == "G7":         # contrefiche à 45° : longueur de pointe à pointe, section du tasseau
            L, l, e = round(M.BAC["contrefiche"] * 2 ** 0.5 * 10), round(M.DL * 10), round(M.DE * 10)
        r.append(dict(rep=rep, mat=rep[0], nom=M.NOMS[rep], q=q, L=L, l=l, e=e, u=M.USINAGES.get(rep, "")))
    return r


def table_debit(meuble):
    """Débit d'un des deux meubles ("bas" ou "haut")."""
    o, mat = [], None
    surf = Counter()
    lignes = [p for p in debit() if M.meuble(p["rep"]) == meuble]
    for p in lignes:
        if p["mat"] != mat:
            mat = p["mat"]
            n, d, _ = M.MATERIAUX[mat]
            o.append(f'<tr class="mat"><td colspan="6"><span class="sw m{mat}"></span>{mat} — {escape(n)} '
                     f'<span class="note">· {escape(d)}</span></td></tr>')
        if mat not in "EG":
            surf[mat] += p["q"] * p["L"] * p["l"] / 1e6
        sec = (f'Ø {p["l"]}' if p["rep"] == "E4" else f'{p["l"]} × {p["e"]}') if mat in "EG" else f'{p["l"]}'
        o.append(f'<tr class="{meuble}"><td class="mono">{p["rep"]}</td><td>{escape(p["nom"])}</td><td class="num">{p["q"]}</td>'
                 f'<td class="num">{p["L"]}</td><td class="num">{sec}</td><td class="u">{escape(p["u"])}</td></tr>')
    tot = " · ".join(f'{m} {virg(v, 2)} m²' for m, v in sorted(surf.items()))
    ml = sum(p["q"] * p["L"] for p in lignes if p["mat"] == "G") / 1000
    if ml:
        tot += f" · G {virg(ml, 2)} m linéaires"
    return (f'<div class="scroll"><table class="debit"><thead><tr><th>Rep.</th><th>Pièce</th><th class="num">Qté</th>'
            f'<th class="num">Long.</th><th class="num">Larg.</th><th>Usinages, remarques</th></tr></thead>'
            f'<tbody>{"".join(o)}</tbody></table></div><p class="note">Cotes en mm, pièces finies. Surfaces nettes : {tot}.</p>')


# ------------------------------------------------------------------ achats (calepinage + liste de courses)
def tablette_svg(p, k):
    L, l = p.fmt["L"], p.fmt["l"]
    o = [f'<rect class="tb" x="0" y="0" width="{L}" height="{l}"/>']
    for rep, x, y, a, b in p.poses():
        o.append(f'<rect class="pc m{rep[0]} {M.meuble(rep)}" x="{x}" y="{y}" width="{a}" height="{b}"/>')
        if l < 100:             # tasseau : repère et longueur sur une ligne
            o.append(f'<text class="pt ps" x="{x + a / 2}" y="{y + b / 2 + 13}" style="font-size:36px">{rep} · {a}</text>')
        elif b >= 60 and a >= 140:
            o.append(f'<text class="pt" x="{x + a / 2}" y="{y + b / 2 - 8}">{rep}</text>'
                     f'<text class="pd" x="{x + a / 2}" y="{y + b / 2 + 42}">{a} × {b}</text>')
        elif b >= 40:
            o.append(f'<text class="pt ps" x="{x + a / 2}" y="{y + b / 2 + 12}">{rep}</text>')
    return (f'<div class="tab"><div class="tabt"><b>{"B" if l < 100 else "T"}{k}</b> · {L} × {l} · {p.taux():.0%} utilisés</div>'
            f'<svg viewBox="-4 -4 {L + 8} {l + 8}" role="img" aria-label="Tablette {k}, {L} × {l}">{"".join(o)}</svg></div>')


def code_meuble(code):
    """Meuble d'un article de quincaillerie : celui des étapes où il sert (consommables : commun)."""
    if code in M.CONSOMMABLES:
        return "commun"
    etapes = {n for n, (_, _, q) in enumerate(M.ETAPES) if code in q}
    return "haut" if etapes and etapes <= set(M.MEUBLE_HAUT_ETAPES) else "bas"


def ligne_panneaux(panneaux):
    """Lignes d'achat (nom, réf., quantité, prix, stock) pour une liste de panneaux du calepinage."""
    r = []
    for stock, fmts in M.PANNEAUX.items():
        for fmt in fmts:
            n = sum(1 for p in panneaux if p.fmt["ref"] == fmt["ref"])   # panneaux copiés : comparer les réf.
            if n and "lot" in fmt:          # vendu par lots
                r.append((fmt["nom"], fmt["ref"], -(-n // fmt["lot"]), fmt["prix_lot"], fmt["stock"]))
            elif n:
                r.append((fmt["nom"], fmt["ref"], n, fmt["prix"], fmt["stock"]))
    return r


def liste(lignes, titre):
    total = sum(n * px for _, _, n, px, _ in lignes)
    corps = "".join(
        f'<tr><td>{escape(nom)}</td><td class="mono">{ref}</td><td class="num">{n}</td><td class="num">{euros(px)}</td>'
        f'<td class="num">{euros(n * px)}</td><td class="num">{"—" if st is None else st}</td></tr>'
        for nom, ref, n, px, st in lignes)
    return total, (f'<div class="scroll"><table class="debit"><thead><tr><th>Article Weldom</th><th>Réf.</th>'
                   f'<th class="num">Qté</th><th class="num">Prix</th><th class="num">Total</th><th class="num">Stock</th>'
                   f'</tr></thead><tbody>{corps}</tbody><tfoot><tr><td colspan="4"><b>{escape(titre)}</b></td>'
                   f'<td class="num"><b>{euros(total)}</b></td><td></td></tr></tfoot></table></div>')


_CAL = []


def calepinage():
    """Calepinage des deux meubles, calculé une fois (il sert aux achats et au comparatif METOD)."""
    if not _CAL:
        _CAL.append(CAL.calepinage_meubles(debit()))
    return _CAL[0]


def eur(v):
    return f"{v:.2f} €".replace(".", ",")


def comparatif_haut():
    """Tableau poste par poste : caisson haut fait maison (Weldom) contre IKEA METOD, mêmes portes coulissantes rainurées."""
    mt, px = M.METOD, M.METOD["prix"]
    neufs = [p for st in calepinage() for p in calepinage()[st]["neufs"]]
    panneaux = sum(n * prix for _, _, n, prix, _ in ligne_panneaux(neufs))
    w = M.WELDOM
    taquets = w["taquet"][1] * w["taquet"][2]
    led = w["led"][1] * w["led"][2]
    tab18 = M.TABLETTES_18[0]["prix"]
    nt = sum(mt["tablettes"])
    lignes = [
        ("Caisson (côtés, dessus, dessous, fond, montant)", panneaux, "panneaux Weldom neufs (achat 2), portes, étagères et fileur compris",
         2 * px["structure"], f"2 structures METOD 60 × 37 × 80 à {eur(px['structure'])}, dont une recoupée à {cm(mt['coupe'])}"),
        ("Étagères", taquets, f"taillées dans les panneaux ; {w['taquet'][2]} lots de taquets",
         nt * px["tablette"], f"{nt} tablettes UTRUSTA 60 × 37 à {eur(px['tablette'])}"),
        ("Portes, bandeaux et fileur", 0, "taillés dans les panneaux (ligne Caisson)",
         tab18, f"1 tablette mélaminée Weldom 250 × 60"),
        ("Fixation au mur", 0, "6 chevilles et vis (non chiffrées)",
         px["rail"], f"rail de suspension METOD 200 à {eur(px['rail'])} (+ chevilles, non chiffrées)"),
        ("Portes coulissantes", 2 * px["patins"], "rainures à la défonceuse + 2 lots de patins PTFE",
         2 * px["patins"], "bandeaux rainurés (dans la tablette des portes) + 2 lots de patins PTFE"),
        ("Éclairage", led, "kit ruban LED Weldom", led, "le même"),
    ]
    t1 = sum(a for _, a, _, _, _ in lignes)
    t2 = sum(b for _, _, _, b, _ in lignes)
    corps = "".join(f'<tr><td>{escape(p)}</td><td class="num">{eur(a)}</td><td class="u">{escape(da)}</td>'
                    f'<td class="num">{eur(b)}</td><td class="u">{escape(db)}</td></tr>' for p, a, da, b, db in lignes)
    corps += (f'<tr class="tot"><td><b>Total</b></td><td class="num"><b>{eur(t1)}</b></td><td></td>'
              f'<td class="num"><b>{eur(t2)}</b></td><td class="u">{"+" if t2 >= t1 else "−"} {eur(abs(t2 - t1))} '
              f'par rapport au fait maison</td></tr>')
    return ('<div class="scroll"><table class="debit"><thead><tr><th>Poste</th><th class="num">Fait maison</th>'
            '<th>Détail</th><th class="num">IKEA METOD</th><th>Détail</th></tr></thead><tbody>' + corps +
            '</tbody></table></div>')


def comparatif_bac():
    """V5.17 : ce qui change à l'achat entre le L basculant et les deux paniers à roulettes. Les tablettes du meuble bas
    sont recalculées par le calepinage des pièces de la variante (V5.18 : sans porte, il n'en faut plus)."""
    old = M.PIECES
    M.PIECES = [b for b in M.version("dr") if b in old]
    try:
        cal_r = CAL.calepinage_meubles(debit())
    finally:
        M.PIECES = old
    tab = lambda cal: sum(n * prix for _, _, n, prix, _ in ligne_panneaux(cal["M18"]["bas"]))  # noqa: E731
    bois = (tab(calepinage()), tab(cal_r))
    assert len(cal_r["M18"]["neufs"]) == len(calepinage()["M18"]["neufs"]), "caisson haut inchangé"
    co, w = M.CORNO, M.WELDOM
    lignes = [
        ("Paniers", M.TOILE["prix"], f"toile des 2 sacs : {cm(M.TOILE['achat_m'])} m à {eur(M.TOILE['prix_m'])} "
         "(Marseille Textiles) ; 4 demi-barres de récupération",
         2 * co["prix"], f"2 × Wenko Corno 43 L à {eur(co['prix'])} ({co['source']})"),
        ("Charnières", w["charniere_p"][1] * w["charniere_p"][2], f"{w['charniere_p'][2]} charnières plates Hettich",
         0, "aucune (pas de porte)"),
        ("Équerres", w["equerre_a"][1] + w["equerre_p"][1], "lot de 6 équerres (L, accroche) + 1 équerre plate (rail avant)",
         0, "plus d'équerre d'assemblage ; 1 équerre plate (rail arrière)"),
        ("Tablettes du meuble bas", bois[0], "porte et plateau du L, supports",
         bois[1], "aucune : sans porte ni plateau, le meuble bas n'est qu'en tasseaux et plan"),
    ]
    t1 = sum(a for _, a, _, _, _ in lignes)
    t2 = sum(b for _, _, _, b, _ in lignes)
    corps = "".join(f'<tr><td>{escape(p)}</td><td class="num">{eur(a)}</td><td class="u">{escape(da)}</td>'
                    f'<td class="num">{eur(b)}</td><td class="u">{escape(db)}</td></tr>' for p, a, da, b, db in lignes)
    corps += (f'<tr class="tot"><td><b>Écart</b></td><td class="num"><b>{eur(t1)}</b></td><td></td>'
              f'<td class="num"><b>{eur(t2)}</b></td><td class="u">{"+" if t2 >= t1 else "−"} {eur(abs(t2 - t1))} '
              f'par rapport au L basculant</td></tr>')
    return ('<div class="scroll"><table class="debit"><thead><tr><th>Poste</th><th class="num">L basculant</th>'
            '<th>Détail</th><th class="num">Bacs à roulettes</th><th>Détail</th></tr></thead><tbody>' + corps +
            '</tbody></table></div>')


def achats():
    cal = calepinage()
    tot = Counter()
    for _, _, q in M.ETAPES:
        tot.update(q)
    quinc = {"commun": [], "bas": [], "haut": []}
    manque = {"commun": [], "bas": [], "haut": []}
    for code, w in M.WELDOM.items():
        m = code_meuble(code)
        if w is None:
            manque[m].append(M.QUINCAILLERIE[code])
        else:
            quinc[m].append((w[0], w[4], w[2], w[1], w[3]))
    non_chiffres = [f"{tot[c]} × {M.QUINCAILLERIE[c]}" for c in M.CONSOMMABLES if c not in M.WELDOM and tot[c]]
    bas_p = [p for st in ("G", "M18", "D") for p in cal[st]["bas"]]
    neufs = [p for st in cal for p in cal[st]["neufs"]]
    t0, l0 = liste(quinc["commun"], "Consommables")
    t1, l1 = liste(ligne_panneaux(bas_p) + quinc["bas"], "Achat 1 · meuble bas")
    t2, l2 = liste(ligne_panneaux(neufs) + quinc["haut"], "Achat 2 · caisson haut")
    barres = "".join(tablette_svg(p, k + 1) for k, p in enumerate(cal["G"]["bas"]))
    tabs1 = "".join(tablette_svg(p, k + 1) for k, p in enumerate(cal["M18"]["bas"]))
    tabs2 = "".join(tablette_svg(p, len(cal["M18"]["bas"]) + k + 1) for k, p in enumerate(cal["M18"]["neufs"]))
    plan_ = "".join(tablette_svg(p, "P") for p in cal["D"]["bas"])
    reste = sum(1 for p in cal["M18"]["bas"] for q in p.poses() if M.meuble(q[0]) == "haut")
    mg = M.MAGASIN
    ail = lambda m: (f'<p><b>À acheter ailleurs</b> : {escape(" ; ".join(manque[m]))}.</p>' if manque[m] else "")  # noqa: E731
    return f"""<p>Tout vient de <b>{escape(mg['nom'])}</b> ({escape(mg['adresse'])}, {mg['tel']}), en deux achats : le meuble bas d'abord, avec les consommables communs aux deux meubles ; le caisson haut ensuite, taillé d'abord dans les chutes des tablettes du bas (pièces en bleu sur les tablettes du bas : les garder), puis dans des tablettes neuves. Prix et stock relevés en ligne le {mg['releve']}.</p>
{LEGENDE}
<h3>Consommables · communs aux deux meubles (avec l'achat 1)</h3>
{l0}
<p class="note">Non chiffrés, en rayon : {escape(" ; ".join(non_chiffres))}.</p>
{ail("commun")}

<h3>Achat 1 · meuble bas</h3>
<p>Ossature en tasseaux de sapin brut non traité 38 × 38 de 2 m, vendus par lots de 6, peints ou vernis ; tablettes mélaminées blanches de 18 ; plan de travail de 28.</p>
<div class="fig"><div class="tabs">{barres}</div>
<p class="cap">Débit des tasseaux de 2000 : chaque barre est tronçonnée (trait de scie de {CAL.TRAIT} compté). Couper les six montants G3 ensemble pour qu'ils aient la même longueur.</p></div>
<div class="fig"><div class="tabs">{tabs1}</div>
<p class="cap">Tablettes du meuble bas : refente en bandes sur la longueur, puis tronçonnage (trait de scie compté). En bleu, {reste} pièces du caisson haut qui tiennent dans la chute : les tracer et les couper avec le bas, ou garder la chute. Les chants longs d'usine sont déjà plaqués ; les chants coupés visibles reçoivent un chant thermocollant.</p></div>
<div class="fig"><div class="tabs">{plan_}</div>
<p class="cap">Plan de travail 1800 × 640 × 28 recoupé à {cal['D']['bas'][0].poses()[0][3]}.</p></div>
{l1}
{ail("bas")}

<h3>Achat 2 · caisson haut</h3>
<p>Les pièces du caisson haut qui ne tiennent pas dans les chutes du bas, dans {len(cal['M18']['neufs'])} tablettes neuves, et la quincaillerie du haut.</p>
<div class="fig"><div class="tabs">{tabs2}</div>
<p class="cap">Tablettes neuves du caisson haut.</p></div>
{l2}
{ail("haut")}
<p><b>Total des deux achats : {euros(t0 + t1 + t2)}</b> (consommables {euros(t0)}, meuble bas {euros(t1)}, caisson haut {euros(t2)}).</p>
<p class="note">Stock : nombre affiché sur la fiche produit pour ce magasin le {mg['releve']} (« — » : en stock, nombre non lu). La découpe en magasin existe (service « découpe bois ») ; tarif et nombre de coupes non publiés : appeler avant.</p>"""


LEGENDE = ('<p class="leg">Code couleur des découpes :<span class="sw bas"></span>meuble bas (socle, ossature, '
           'tablette, portes, plan)<span class="sw haut"></span>caisson haut</p>')


def euros(v):
    return f"{v:.2f}".replace(".", ",") + " €"


def quincaillerie(meuble):
    tot = Counter()
    for n, (_, _, q) in enumerate(M.ETAPES):
        if (n in M.MEUBLE_HAUT_ETAPES) == (meuble == "haut"):
            tot.update(q)
    return "".join(f'<li><b>{n}</b> × {escape(M.QUINCAILLERIE[k])}</li>' for k, n in tot.items())


# ------------------------------------------------------------------ page
CSS = """
:root{
  --paper:#F7F8F6; --ink:#1D2A33; --muted:#5E6B73; --line:#C9D0D4; --wood:#B07A45;
  --water:#2F7FB5; --tri:#C8412C; --panel:#FFFFFF; --cab:#ECE6DA; --tall:#D8CFBD; --bac:#E3C9A0;
  --socle:#C8B79B; --glass:#CFE4F2; --tile:#E9EEF0; --dg:#D29A68; --bas:#EDBE8C; --haut:#9EC9E6; color-scheme:light;
}
@media (prefers-color-scheme: dark){
  :root:not([data-theme="light"]){
    --paper:#141A1F; --ink:#E4EAED; --muted:#9AA7AE; --line:#34414A; --wood:#C9925A;
    --water:#5AA8DE; --tri:#E8664F; --panel:#1B2329; --cab:#2A3338; --tall:#394449; --bac:#5B4B33;
    --socle:#4C4436; --glass:#1F3A4E; --tile:#1D262C; --dg:#8C5E3A; --bas:#7A5534; --haut:#2F5677; color-scheme:dark;
  }
}
:root[data-theme="dark"]{
  --paper:#141A1F; --ink:#E4EAED; --muted:#9AA7AE; --line:#34414A; --wood:#C9925A;
  --water:#5AA8DE; --tri:#E8664F; --panel:#1B2329; --cab:#2A3338; --tall:#394449; --bac:#5B4B33;
  --socle:#4C4436; --glass:#1F3A4E; --tile:#1D262C; --dg:#8C5E3A; --bas:#7A5534; --haut:#2F5677; color-scheme:dark;
}
*{box-sizing:border-box}
html,body{margin:0}
body{background:var(--paper);color:var(--ink);font-family:Archivo,system-ui,-apple-system,"Segoe UI",Roboto,sans-serif;line-height:1.55;font-size:16px}
.wrap{max-width:1120px;margin:0 auto;padding:28px 16px 64px}
.kicker{font-family:"JetBrains Mono",ui-monospace,Menlo,monospace;font-size:12px;letter-spacing:.08em;text-transform:uppercase;color:var(--muted)}
h1{font-size:clamp(28px,5vw,44px);line-height:1.08;margin:6px 0 12px;font-weight:800;letter-spacing:-.01em}
h2{font-size:22px;margin:44px 0 10px;font-weight:700;scroll-margin-top:60px}
h3{font-size:15px;margin:18px 0 6px}
.pitch{font-size:18px;max-width:780px}
.fig{background:var(--panel);border:1px solid var(--line);border-radius:12px;padding:12px;margin:14px 0}
.scroll{overflow-x:auto}.scroll svg{display:block;width:100%;height:auto;max-height:78vh}
.grid2{display:grid;grid-template-columns:repeat(auto-fit,minmax(320px,1fr));gap:14px}
.grid2 .fig{margin:0}
.cap{font-size:13px;color:var(--muted);margin:8px 4px 2px}
.note{font-size:13px;color:var(--muted)}
table{border-collapse:collapse;width:100%;font-size:14px}
th,td{text-align:left;padding:7px 8px;border-bottom:1px solid var(--line);vertical-align:top}
td.num,th.num{text-align:right;font-family:"JetBrains Mono",ui-monospace,monospace;white-space:nowrap}
.mono{font-family:"JetBrains Mono",ui-monospace,monospace;white-space:nowrap}
td.u{font-size:13px;color:var(--muted)}
tr.mat td{background:var(--paper);font-weight:700;padding-top:12px}
.debit{min-width:680px}
.debit tfoot td{border-top:2px solid var(--ink)}
.tabs{display:grid;gap:10px}
.tab svg{display:block;width:100%;height:auto}
.tabt{font-size:13px;color:var(--muted);margin-bottom:3px}.tabt b{color:var(--ink)}
.tb{fill:var(--tile);stroke:var(--ink);stroke-width:3}
.pc{stroke:var(--ink);stroke-width:2;fill:var(--cab)}.pc.mB{fill:var(--bac)}.pc.mC{fill:var(--tall)}.pc.mS{fill:var(--socle)}.pc.mD{fill:var(--wood)}.pc.mG{fill:var(--dg)}
.pc.bas{fill:var(--bas)}.pc.haut{fill:var(--haut)}
.sw.bas{background:var(--bas)}.sw.haut{background:var(--haut)}
tr.bas td:first-child{box-shadow:inset 5px 0 var(--bas)}tr.haut td:first-child{box-shadow:inset 5px 0 var(--haut)}
.leg{font-size:13px;color:var(--muted);margin:6px 2px}.leg .sw{margin-left:12px}
.pt{font:700 64px "JetBrains Mono",ui-monospace,monospace;fill:var(--ink);text-anchor:middle}
.pt.ps{font-size:40px}
.pd{font:400 40px "JetBrains Mono",ui-monospace,monospace;fill:var(--muted);text-anchor:middle}
.sw{display:inline-block;width:12px;height:12px;border-radius:3px;margin-right:8px;vertical-align:-1px;border:1px solid var(--ink)}
.mA{background:var(--cab)}.mB{background:var(--bac)}.mC{background:var(--tall)}.mD{background:var(--wood)}.mS{background:var(--socle)}.mG{background:var(--dg)}.mE{background:#B9C2C8}
ul.pistes{padding-left:20px;max-width:860px}ul.pistes li{margin:6px 0}
.cta{display:inline-block;margin:6px 0;padding:10px 16px;border-radius:8px;background:var(--ink);color:var(--paper);text-decoration:none;font-weight:700}
svg text{font-family:Archivo,system-ui,sans-serif;fill:var(--ink)}
.sdbf{fill:var(--tile)}
.w{fill:var(--ink)}
.fixe{fill:var(--tri);fill-opacity:.07;stroke:var(--tri);stroke-width:.6;stroke-dasharray:3 2}
.rt{fill:var(--tri)}
.doorzone{fill:var(--tri);fill-opacity:.05}.doorarc{fill:none;stroke:var(--muted);stroke-width:.5;stroke-dasharray:2 2}
.leaf{fill:var(--muted)}
.leafg{fill:none;stroke:var(--tri);stroke-width:.7;stroke-dasharray:3 2}
.conf{fill:var(--tri);fill-opacity:.55}
.cab{fill:var(--cab);stroke:var(--ink);stroke-width:.35}
.cabc{fill:var(--tall);stroke:var(--ink);stroke-width:.45}
.fond{fill:var(--tall);fill-opacity:.6;stroke:var(--ink);stroke-width:.3}.fondc{fill:var(--muted);stroke:var(--ink);stroke-width:.3}
.plinthe{fill:var(--tall);stroke:var(--ink);stroke-width:.3}
.fac{fill:var(--cab);stroke:var(--ink);stroke-width:.55}.facc{fill:var(--tall);stroke:var(--ink);stroke-width:.55}
.bac{fill:var(--bac);fill-opacity:.55;stroke:var(--ink);stroke-width:.35}.bacc{fill:var(--bac);stroke:var(--ink);stroke-width:.45}
.socle{fill:var(--socle);stroke:var(--ink);stroke-width:.4}.soclec{fill:var(--socle);stroke:var(--ink);stroke-width:.5;filter:brightness(.85)}
.tas{fill:var(--wood);fill-opacity:.6;stroke:var(--ink);stroke-width:.3}.tasc{fill:var(--wood);stroke:var(--ink);stroke-width:.4}
.dg{fill:var(--dg);fill-opacity:.75;stroke:var(--ink);stroke-width:.35}.dgc{fill:var(--dg);stroke:var(--ink);stroke-width:.45;filter:brightness(.85)}
.pat{fill:var(--glass);stroke:var(--water);stroke-width:.4}.patp{fill:none;stroke:var(--water);stroke-width:.3;stroke-dasharray:1.5 1}
.patc{fill:none;stroke:var(--ink);stroke-width:.25;stroke-dasharray:.8 .8}.toile{fill:none;stroke:var(--muted);stroke-width:.4}
.alu{fill:#B9C2C8;stroke:var(--ink);stroke-width:.3}
.top{fill:var(--wood);fill-opacity:.55;stroke:var(--ink);stroke-width:.5}.topc{fill:var(--wood);stroke:var(--ink);stroke-width:.5}
.planl{fill:none;stroke:var(--wood);stroke-width:.7;stroke-dasharray:1.5 1.5}
.trap{fill:url(#hach) var(--wood);fill:var(--wood);fill-opacity:.25;stroke:var(--ink);stroke-width:.5;stroke-dasharray:1.5 1}
.shelf{fill:var(--wood);fill-opacity:.35;stroke:var(--ink);stroke-width:.3}.shelfc{fill:var(--wood);stroke:var(--ink);stroke-width:.4}
.porte{fill:var(--cab);stroke:var(--ink);stroke-width:.55}.portec{fill:var(--tall);stroke:var(--ink);stroke-width:.5}
.appf{fill:var(--panel);stroke:var(--ink);stroke-width:.7}.appc{fill:var(--panel);stroke:var(--ink);stroke-width:.9}
.app{fill:none;stroke:var(--ink);stroke-width:.6}
.led{fill:#F2C94C;stroke:#B8860B;stroke-width:.3}
.plug{fill:var(--panel);stroke:var(--ink);stroke-width:.4}
.valve{fill:var(--water);stroke:var(--ink);stroke-width:.3}
.handle{fill:var(--ink)}
.hook{fill:none;stroke:var(--ink);stroke-width:.8}
.upper{fill:none;stroke:var(--ink);stroke-width:.9;stroke-dasharray:4 2}
.swing{fill:none;stroke:var(--muted);stroke-width:.6;stroke-dasharray:2 1.5}
.sac{fill:var(--glass);fill-opacity:.55;stroke:var(--water);stroke-width:.35;stroke-dasharray:1.2 .8}.sacc{fill:var(--glass);stroke:var(--water);stroke-width:.4}
.sacopen{fill:none;stroke:var(--water);stroke-width:.45;stroke-dasharray:2 1.2}
.swingp{fill:var(--bac);fill-opacity:.12;stroke:var(--tri);stroke-width:.5;stroke-dasharray:2 1.2}
.axe{fill:var(--tri)}
.lead{fill:none;stroke:var(--muted);stroke-width:.4}
.dim{stroke:var(--muted);stroke-width:.4;fill:none}
.dimt{fill:var(--muted);font-family:"JetBrains Mono",ui-monospace,monospace !important;font-size:4.6px}
.lbl{font-size:6.5px}.lbls{font-size:4.6px;font-weight:600}.lblx{font-size:3.5px}.lblb{font-size:8px;font-weight:700}
.muted{fill:var(--muted)}
.sec{stroke:var(--tri);stroke-opacity:.45;stroke-width:.6;stroke-dasharray:6 2 1.5 2;fill:none}
.secm{fill:var(--tri)}
.sect{fill:var(--tri);font-weight:800;font-size:7px}
.floorl{stroke:var(--ink);stroke-width:1.4}
.ceil{stroke:var(--muted);stroke-width:.6;stroke-dasharray:4 3}
body.mg .vd,body:not(.mg) .vg{display:none}
body.rb .vl,body:not(.rb) .vr{display:none}
.panier{fill:var(--glass);fill-opacity:.7;stroke:var(--water);stroke-width:.45}.panierc{fill:var(--glass);stroke:var(--water);stroke-width:.6}
.hinge{fill:var(--muted)}
body:not(.explications) .cap{display:none}
body:not(.changements) section[id^="changements"]{display:none}
.vbar{position:sticky;top:0;z-index:5;display:flex;flex-wrap:wrap;align-items:center;gap:6px;padding:8px 16px;background:var(--paper);border-bottom:1px solid var(--line);font-family:"JetBrains Mono",ui-monospace,monospace;font-size:12px}
.vbar .back{color:var(--ink);text-decoration:none;font-weight:600;margin-right:14px}
.vbar .back:hover{text-decoration:underline}
.vbar span{color:var(--muted);text-transform:uppercase;letter-spacing:.08em;margin:0 4px 0 10px}
.vbar button,.vbar a.btn{font:inherit;color:var(--ink);background:var(--panel);border:1px solid var(--line);border-radius:6px;padding:4px 10px;cursor:pointer;text-decoration:none}
.vbar button[aria-pressed="true"]{background:var(--ink);color:var(--paper);border-color:var(--ink)}
.vbar .sp{margin-left:auto}
.toc{display:none}
@media (min-width:1100px){
.toc{display:block;position:fixed;left:0;top:42px;z-index:4;font-size:13px}
.toc .tbtn{font:600 12px "JetBrains Mono",ui-monospace,monospace;color:var(--ink);background:var(--panel);border:1px solid var(--line);border-radius:0 6px 6px 0;border-left:none;padding:6px 10px;cursor:pointer}
.toc ol{display:none;list-style:none;margin:0;padding:6px 0 24px}
body.toc-on .toc{bottom:0;width:232px;overflow-y:auto;background:var(--paper);border-right:1px solid var(--line);padding:10px 0 0}
body.toc-on .toc .tbtn{border:none;background:none;padding:2px 16px 8px;color:var(--muted);text-transform:uppercase;letter-spacing:.08em}
body.toc-on .toc ol{display:block}
.toc a{display:block;padding:5px 16px;color:var(--muted);text-decoration:none;border-left:3px solid transparent;line-height:1.35}
.toc a:hover{color:var(--ink);background:var(--panel)}
.toc a.on{color:var(--ink);border-left-color:var(--ink);font-weight:600}
body.toc-on .wrap{margin-left:max(248px,calc((100vw - 1120px) / 2))}
}
@media (max-width:480px){ body{font-size:15px} }
"""


def deux(fn):
    """V5.2 : deux variantes du caisson haut, fait maison (d) et IKEA METOD (m) ; V5.17 : deux variantes du linge sale,
    L basculant et paniers à roulettes (r). Quatre dessins, basculés par les boutons du bandeau."""
    return "".join(f'<div class="{"vd" if c[0] == "d" else "vg"} {"vr" if roul(c) else "vl"}">{fn(c)}</div>'
                   for c in ("d", "m", "dr", "mr"))


def patron_svg():
    """Placement des pièces des deux sacs dans la toile : les deux bandes en long, les quatre côtés en deux colonnes."""
    pt = M.PATRON
    bw, bl = pt["bande"]
    sw, sh = pt["soufflet"]
    lt, L = pt["tissu"], pt["metrage"] * 100
    o = [rect(0, 0, lt, L, "toile")]
    c = M.COUTURE

    def piece(x, y, w, h, lab, plis=(), trap=0):
        if trap:                # soufflet : trapèze, grand côté (haut du sac) en haut, petit côté réduit de trap
            d = trap / 2
            o.append(poly([(x, y), (x + w, y), (x + w - d, y + h), (x + d, y + h)], "pat"))
        else:
            o.append(rect(x, y, x + w, y + h, "pat"))
            o.append(rect(x + c, y + c, x + w - c, y + h - c, "patc"))
        for p in plis:
            o.append(f'<line class="patp" x1="{f(x)}" y1="{f(y + p)}" x2="{f(x + w)}" y2="{f(y + p)}"/>')
        o.append(text(x + w / 2, y + h / 2, lab, "lbls"))
        o.append(text(x + w / 2, y + h / 2 + 6, f"{cm(w)} × {cm(h)}", "dimt"))

    fo, hs, ds = M.FOURREAU, pt["hauteur"], pt["fond"]
    plis = (fo, fo + hs, fo + hs + ds, fo + 2 * hs + ds)
    for k in range(2):
        piece(k * bw, 0, bw, bl, f"bande {k + 1}", plis)
    for k in range(4):
        piece(2 * bw + (k // 2) * sw, (k % 2) * sh, sw, sh, "soufflet", (M.OURLET,),
              trap=pt["soufflet_haut"] - pt["soufflet_bas"])
    for k, y in enumerate(plis):
        o.append(text(-2, y + 1.2, ("fourreau", "pli du fond", "pli du fond", "fourreau")[k], "lblx muted", "end"))
    o.append(cote_h(0, lt, -6, f"laize {lt}"))
    o.append(cote_v(0, L, lt + 8, cm(L)))
    return (f'<svg viewBox="-30 -16 {f(lt + 48)} {f(L + 24)}" role="img" aria-label="Patron des sacs">'
            f'{"".join(o)}</svg>')


def couture():
    pt = M.PATRON
    bw, bl = pt["bande"]
    sw, sh = pt["soufflet"]
    c = cm(M.COUTURE)
    etapes = [
        f"<b>Couper</b> deux bandes de {cm(bw)} × {cm(bl)} et quatre soufflets en trapèze de {cm(sh)} de haut, "
        f"{cm(pt['soufflet_haut'])} en haut et {cm(pt['soufflet_bas'])} en bas, dans "
        f"{cm(M.TOILE['achat_m'])} m de toile en {pt['tissu']} : toile de transat "
        f"polyester 420 g/m² chez {M.TOILE['magasin']}, {eur(M.TOILE['prix_m'])} le mètre, soit "
        f"{eur(M.TOILE['prix'])} (relevé en ligne du {M.TOILE['releve']}) ; ou coton épais (canevas), lavable à 60°.",
        "<b>Surfiler</b> tous les bords au zigzag.",
        f"<b>Marquer</b> sur l'envers de chaque bande les deux plis du fond, à {cm(M.FOURREAU + pt['hauteur'])} de chaque "
        f"bout : entre eux, le fond ({cm(pt['fond'])}).",
        "<b>Ourler</b> le haut de chaque soufflet : replier 1 puis 1, piquer.",
        f"<b>Assembler</b> chaque soufflet à sa bande, endroit contre endroit, à {c} du bord : le bas du soufflet sur le "
        "fond, entre les deux plis, puis ses côtés sur le devant et sur le dos. Aux angles, aiguille piquée, cranter la "
        "bande jusqu'à la couture et pivoter. Deux soufflets par sac.",
        f"<b>Fourreaux</b> : en haut du devant et du dos, replier 1 puis {cm(M.FOURREAU - 1)}, piquer à "
        f"{cm(M.FOURREAU - 1.5)} du pli : un tunnel de 10 de tour pour une barre Ø 22.",
        f"<b>Retourner</b>. Sac fini : {cm(pt['largeur'])} de large, {cm(pt['fond'])} de fond, {cm(pt['hauteur'])} de "
        "haut ; les deux sacs s'enfilent côte à côte sur les deux barres.",
    ]
    return "".join(f"<li>{e}</li>" for e in etapes)


def capacites():
    ch = M.CH
    _et = next(b for b in M.PIECES if b.nom == "ch_etagere_n1")
    lignes = [
        ("Linge sale", f'<span class="vl">2 sacs à soufflet côte à côte, {cm(M.BAC["largeur_sac"])} de large, '
         f'{cm(M.BAC["h_sac"])} de haut, entre deux barres</span><span class="vr">2 paniers Wenko Corno à roulettes, '
         f'{cm(M.CORNO["l"])} × {cm(M.CORNO["p"])} × {cm(M.CORNO["h"])}</span>',
         f'<span class="vl">2 × ≈ {M.VOLUME_BAC:.0f} L</span><span class="vr">2 × {M.CORNO["litres"]} L</span>'),
        ("Serviettes (nord)", f"{ch['serviettes']} étagères, cases de {cm(ch['case_serviettes'])}, "
         f"{cm(_et.y1 - _et.y0)} × {cm(_et.x1 - _et.x0)} utiles",
         "≈ 30 serviettes de bain"),
        ("Pharmacie et produits divers (sud)", f"{ch['pharmacie']} étagères, cases de {cm(ch['case_pharmacie'])}",
         "10 bacs à tirer 16 × 16 × 35"),
        ("Plan de travail", f"{cm(M.Y1 - 2 * M.J)} × {cm(M.PLAN_P)} à {cm(M.Z_DESSUS)}", "pliage"),
        ("Niche", f"{cm(M.Y1)} de large × {cm(M.PLAN_P)} de profondeur (tout le plan) × {cm(M.Z_HAUT - M.Z_DESSUS)} de haut, sous les hauts",
         "sèche-cheveux, brosse à dents"),
    ]
    corps = "".join(f'<tr><td>{a}</td><td>{b}</td><td class="num">{c}</td></tr>' for a, b, c in lignes)
    return f'<table><thead><tr><th>Rangement</th><th>Dimensions</th><th class="num">Capacité</th></tr></thead><tbody>{corps}</tbody></table>'


def contenu():
    b, mt = M.BAC, M.METOD
    equilibre = (f"le poids du L reste derrière l'axe jusqu'à ≈ {b['equilibre']:g}°, au-delà de la butée ({b['angle']}°) : "
                 "lâché, il retombe fermé, à vide comme chargé." if b["equilibre"] > b["angle"] else
                 f"à vide, le L reste fermé jusqu'à ≈ {b['equilibre']:g}° puis s'ouvre seul jusqu'à la butée ; chargé, "
                 "le linge posé sur le plateau le ramène fermé.")
    lignes = "".join(f'<tr><td class="mono">{v}</td><td class="mono">{d}</td><td>{escape(x)}</td></tr>'
                     for v, d, x in M.CHANGEMENTS)
    return f"""<div class="kicker">Salle de bain · alcôve {cm(M.ALCOVE["nord"])} (nord) et {cm(M.ALCOVE["sud"])} (sud) × {cm(M.Y1)} · {M.VERSION}</div>
<h1>Meuble linge V5</h1>
<p class="pitch">En bas, trois échelles en tasseaux de sapin peints ou vernis, debout sur le carrelage ; le plan de travail filant est posé sur leur tête, à {cm(M.Z_DESSUS)}. La machine est posée au sol et passe sous le plan à {cm(M.JEU_PLAN * 10)} mm près. <span class="vl">À côté, une seule porte basculante : la porte et un plateau forment un L qui pivote au pied ; deux sacs côte à côte pendent entre une barre sur la porte et une barre arrière sous le plan. On tire la porte, le L bascule jusqu'à sa butée, les sacs s'ouvrent, on jette le linge.</span><span class="vr">À côté, sans porte, deux paniers à linge étroits à roulettes du commerce, côte à côte : on tire le panier et on le roule jusqu'à la machine.</span> Au-dessus : la niche avec les prises, puis les placards jusqu'au plafond.</p>
<p><a class="cta" href="{NOTICE}">Notice de montage, avec les perçages →</a></p>

<h2>Plan</h2>
<div class="fig"><div class="scroll">{deux(plan_svg)}</div>
<p class="cap">Coupe horizontale à {Z_COUPE_PLAN} cm, sous le plan de travail : pièces coupées en foncé (montants et lisses hautes en tasseaux). Portes à x {cm(M.FACE)}, à {cm(M.FACE - leaf()[2])} du vantail de la porte ouvert. Tireté : <span class="vl">porte basculée (elle avance de {cm(b['avancee'])})</span><span class="vr">panier nord tiré (pas de porte)</span> et hublot ouvert. Rouge plein : recouvrement avec le vantail ouvert. Passe-tuyau (hachuré) au chant arrière du plan, sous le robinet remonté dans la niche ; hauts de 45 en pointillé épais.</p></div>

<h2>Élévation A · face au meuble</h2>
<div class="fig"><div class="scroll">{deux(elevation)}</div>
<p class="cap">Vue vers l'est : le nord (porte) à gauche, le sud (lavabo) à droite. Machine au sol, de 0 à {cm(M.LL['h'])}, {cm(M.JEU_PLAN * 10)} mm de jeu sous le plan de {cm(M.PT * 10)} mm de {cm(M.Z_PLAN)} à {cm(M.Z_DESSUS)}. <span class="vl">Une seule porte de {cm(M.FACADES[0][1] - M.FACADES[0][0])} de haut, au-dessus du rail avant (retrait de 1,8 au pied) ; un trou de prise Ø 25 en haut.</span><span class="vr">Pas de porte : les deux paniers sont à nu, entre les échelles.</span> Niche de {cm(M.Z_HAUT - M.Z_DESSUS)}, caisson haut de {M.Z_HAUT} à {M.Z_HAUT1}, fileur jusqu'au plafond, deux portes coulissantes.</p></div>

<div class="grid2">
<div class="fig"><h3>Coupe B-B · machine</h3><div class="scroll">{deux(coupe_b)}</div>
<p class="cap">Coupe à y {COUPE_B}, regard vers le nord. Machine posée au sol sur le tapis antivibration, reculée à {M.JEU_LL} du mur du fond ; le robinet d'arrêt est dans la niche, au-dessus du plan, le tuyau passe par une encoche au chant arrière ; entre les échelles du milieu et du mur sud. Au-dessus de la machine, le plan franchit les {cm(M.LL_ZONE)} entre les deux échelles. Au fond, les hauts côté serviettes.</p></div>
<div class="fig"><h3>Coupe C-C · linge sale</h3><div class="scroll">{deux(coupe_c_svg)}</div>
<p class="cap"><span class="vl">Coupe à travers le sac nord, regard vers le nord. Le L (porte et plateau, contrefiche en diagonale) repose fermé sur les deux rails au sol et pivote sur l'arête avant du rail avant (point rouge), où deux charnières plates relient le rail et le plateau. On tire la porte jusqu'à {b['angle']}°, où les sacs tendus entre les barres l'arrêtent ; la porte avance de {cm(b['avancee'])} et emmène sa barre : la bouche des sacs passe de {cm(b['bouche_fermee'])} à {cm(b['bouche'])} (tireté bleu). La barre arrière, à {b['prof']} du nu avant, est posée dans deux supports sous le plan. Barres arrière levées, le L va jusqu'aux vis de butée, à {b['angle_max']}° (pointillé rouge) : le sac plein sort.</span><span class="vr">Coupe à travers le panier nord ; plus de L, de barres, de rail avant ni de porte : le panier affleure presque le nu du plan.</span></p></div>
</div>

<h2>Ossature</h2>
<ul class="pistes">
<li><b>Pas de socle</b> (V5) : la machine est posée au sol sur son tapis ; le plan descend à {cm(M.Z_DESSUS)} (93,7 en V4.4), la niche gagne d'autant.</li>
<li><b>Échelles</b> : trois cadres verticaux (deux montants G3, une lisse basse au sol, une lisse haute sous le plan, une écharpe G11 en diagonale), debout sur le carrelage, vissés sans colle. L'écharpe, taillée dans les tasseaux en rab, rend chaque échelle indéformable d'avant en arrière.</li>
<li><b>Rails</b> : entre les deux échelles du bac, deux rails G5 au sol, au droit des montants avant et arrière : ils lient les deux échelles et portent le L.</li>
<li><b>Vis de butée</b> : une vis 5 × 60 plantée dans la face intérieure de l'écharpe de chaque échelle du bac, enfoncée de 35, qui dépasse de 25 au-dessus du bord du plateau ; à {cm(M.Z_BUTEE)} du sol et à {cm(M.BAC['x_butee'] - M.XO0)} du nu avant des montants. Plus près de l'axe, elle sortirait de l'écharpe ; plus loin, la contrefiche la heurterait en basculant ({cm(M.VIS_BUTEE['marge'])} de marge). Effort estimé ≈ {M.VIS_BUTEE['effort']:.0f} N par vis, L à vide.</li>
<li><b>Lisses de barre</b> : dans les deux échelles du bac, une lisse G8 sous la lisse haute porte les supports de la barre arrière.</li>
<li><b>Plan</b> : posé sur la tête des échelles et vissé par-dessous dans les lisses hautes ; c'est lui qui relie le haut des trois échelles. Les murs nord, sud et est tiennent l'ensemble sur les côtés. Rien n'est fixé aux murs.</li>
</ul>

<h2>Porte basculante</h2>
<ul class="pistes">
<li><b>Le L</b> : la porte A6 et le plateau A3, tenus d'équerre par deux contrefiches G7 en tasseau à 45° (jambes de {b['contrefiche']}) aux bords du plateau ; vissées par-dessous à travers le plateau, une équerre contre la porte.</li>
<li><b>Charnières plates</b> : deux charnières universelles entre le dessus du rail avant et le dessous du plateau, nœud à l'arête avant : pas de réglage, pas de Forstner.</li>
<li><b>Deux arrêts</b> : en usage courant, les barres arrêtent le L à {b['angle']}° : le haut des soufflets, coupé juste à la bouche, se tend entre la barre de la porte et la barre arrière. Barres arrière levées, le L bascule plus loin, jusqu'aux vis de butée : le plateau monte et s'appuie sous elles à {b['angle_max']}°.</li>
<li><b>Sortie du sac plein</b> (vérifiée) : le sac sort entre le haut de la porte et le chant du plan. À {b['angle']}°, ce passage fait {cm(b['ouverture'])}, moins que le fond du sac ({cm(b['fond_sac'])}) : le sac plein ne passe pas. À {b['angle_max']}°, il fait {cm(b['ouverture_max'])} ({cm(M.MARGE_SAC)} de marge au moins) ; le haut de la porte avance alors de {cm(b['avancee_max'])} dans la pièce (porte d'entrée fermée).</li>
<li><b>Sacs</b> : deux sacs à soufflet côte à côte, entre les contrefiches, enfilés sur deux barres rondes : la barre de la porte dans deux supports B1 au dos de la porte, la barre arrière, amovible, posée d'un bout dans un support B1 sur la lisse G8 et de l'autre dans le crochet de l'accroche centrale G10, sous le plan. Chaque sac a ses deux demi-barres. Le fond des sacs repose sur le plateau.</li>
<li><b>Vider</b> : porte basculée à {b['angle']}°, soulever les deux demi-barres arrière de leur support et les tirer hors du crochet (tant qu'une est en place, son sac garde le L à {b['angle']}°) ; le L bascule jusqu'aux vis de butée, à {b['angle_max']}° ; sortir chaque sac en tenant ses deux demi-barres. À vide, le L reste ouvert à la butée (au-delà de son équilibre, ≈ {b['equilibre']:g}°) : le repousser fermé, puis reposer sacs et barres.</li>
<li><b>Volume</b> : ≈ {M.VOLUME_BAC:.0f} L par sac, ≈ {M.VOLUME_CASE:.0f} L en tout (V4.4 : 2 × 43) ; les contrefiches prennent {cm(2 * M.DE)} de largeur.</li>
<li><b>Équilibre</b> (estimation) : {equilibre}</li>
</ul>

<h2>Sacs : découpe et couture</h2>
<div class="fig"><div class="scroll">{patron_svg()}</div>
<p class="cap">Placement des pièces des deux sacs dans {cm(M.PATRON['metrage'] * 100)} cm de toile en {M.PATRON['tissu']} de laize. Cotes de coupe, coutures de {cm(M.COUTURE * 10)} mm comprises (pointillé noir) ; tireté bleu : plis du fond et rempli du rabat.</p></div>
<ol class="pistes">
{couture()}
</ol>

<h2>Linge sale : variante bacs à roulettes</h2>
<p>Le bouton « Linge sale » du bandeau bascule le plan, l'élévation et les coupes entre le L basculant et cette variante. La notice de montage reste celle du L.</p>
<ul class="pistes">
<li><b>Paniers</b> : deux paniers à linge étroits à roulettes Wenko Corno 43 L ({cm(M.CORNO['l'])} de large × {cm(M.CORNO['p'])} de profondeur × {cm(M.CORNO['h'])} de haut, polyester, 4 roulettes, poignées, couvercle à cordon ; coloris noir, gris, beige ou taupe), roulés côte à côte entre les échelles du bac : {M.VOLUME_ROUL} L en tout ({M.VOLUME_CASE:.0f} L avec les sacs du L). Dimensions d'après les fiches La Redoute et Galaxus ; Bricomarché en donne d'autres (sans doute le carton) : mesurer à réception.</li>
<li><b>Place</b> : {cm(M.CORNO['place']['l'])} entre les échelles (2 × {cm(M.CORNO['l'])} + {cm(M.CORNO['entre'])} entre les paniers, {cm(M.CORNO['jeu_cote'])} de chaque côté), {cm(M.CORNO['place']['p'])} du nu du plan au rail arrière (paniers à {cm(M.CORNO['recul'])} en retrait du nu, {cm(M.CORNO['place']['p'] - M.CORNO['p'] - M.CORNO['recul'])} de rab derrière), {cm(M.CORNO['place']['h'])} sous les lisses de barre ({cm(M.CORNO['place']['h'] - M.CORNO['h'])} au-dessus des paniers : le couvercle s'ouvre en place).</li>
<li><b>Retirés</b> : le rail avant G5 (les roulettes ne le passeraient pas), la butée G6, le plateau A3, la porte A6, les contrefiches G7, les supports B1, les barres E4, l'accroche G10, les sacs à coudre, les charnières plates et les équerres. Le rail arrière reste au sol derrière les paniers et lie le bas des deux échelles, le plan en lie le haut ; les écharpes et les lisses de barre G8 restent.</li>
<li><b>Pas de porte</b> : les paniers restent visibles, couvercle à cordon fermé ; on les tire par la poignée. Plus de façade à couper ni de charnière : le meuble bas n'a plus besoin de tablette mélaminée.</li>
<li><b>Porte d'entrée</b> : un panier tiré avance de {cm(M.CORNO['p'])} devant le meuble, dans le débattement du vantail : le sortir porte d'entrée fermée, comme pour charger la machine.</li>
</ul>
<h3>Prix : L basculant ou bacs à roulettes</h3>
<p>Seuls les postes qui changent ; plan, lots de tasseaux et tablettes du caisson haut restent les mêmes (calepinage refait : une barre de tasseau en moins, toujours deux lots). Prix Weldom relevés le 13/10/2026 ; Corno au prix Amazon relevé par le client.</p>
<div class="fig">{comparatif_bac()}</div>

<h2>Caisson haut : variante IKEA METOD</h2>
<p>Le bouton « Caisson haut » du bandeau bascule le plan, l'élévation et les coupes entre le caisson fait maison et cette variante.</p>
<ul class="pistes">
<li><b>Structures</b> : deux METOD « rangement mural » 60 × 37 × 80 blanc (réf. {mt['refs']['structure']}, {cm(mt['prix']['structure'])} € pièce), panneaux de 18, accrochées à un rail de suspension METOD de 200 (réf. {mt['refs']['rail']}, {cm(mt['prix']['rail'])} €) recoupé à 113, vissé dans le carrelage. Profondeur {cm(mt['p'])} (+ {cm(mt['rail'])} de rail) au lieu de 45 : la niche gagne {cm(M.CH['x0'] - mt['x0'] + 0.0)} devant les portes.</li>
<li><b>Une structure recoupée</b> : celle de la pharmacie passe de 60 à {cm(mt['coupe'])} : recouper dessus, dessous, dos et tablettes de {cm(mt['l'] - mt['coupe'])}, puis repercer pour remonter le côté (tourillons et excentriques, à reporter depuis le côté d'origine). L'autre reste entière (serviettes).</li>
<li><b>Hauteur</b> : 80 (la gamme fait 40, 60, 80, 100) ; dessous à {cm(mt['z'][0])} comme le fait maison, la niche ne change pas ; fileur de {cm(M.H - mt['z'][1])} jusqu'au plafond. En 100, la niche perdrait 10.</li>
<li><b>Tablettes</b> : UTRUSTA 60 × 37 (réf. {mt['refs']['tablette']}, {cm(mt['prix']['tablette'])} €) : {mt['tablettes'][0]} côté serviettes (cases de {cm(mt['case_n'])}), {mt['tablettes'][1]} côté pharmacie (cases de {cm(mt['case_s'])}, recoupées à la largeur).</li>
<li><b>Portes coulissantes</b> : IKEA ne fait pas de porte coulissante pour METOD, et les kits du commerce (rails à roulettes) sont faits pour des portes de placard ou de 30 kg. Ici, comme pour le caisson fait maison : deux bandeaux de mélaminé de 18, vissés sous et sur les deux structures et débordant de {cm(mt['bandeau'])} devant, rainurés à la défonceuse (deux rainures de {cm(M.RAINURE['l'] * 10)} mm, {cm(M.RAINURE['haut'] * 10)} en haut, {cm(M.RAINURE['bas'] * 10)} en bas) ; deux portes de {cm(mt['porte'][0])} × {cm(mt['porte'][1])} en mélaminé 18 glissent dedans sur des patins PTFE, recouvrement de {cm(mt['rec'])} au milieu. Portes et bandeaux sortent d'une tablette du Weldom.</li>

</ul>

<h3>Prix : fait maison ou METOD</h3>
<p>Caisson haut seul, à prestations égales (portes coulissantes rainurées sur patins, même éclairage). Prix IKEA France et Weldom Saint-Barnabé relevés le 13/10/2026.</p>
<div class="fig">{comparatif_haut()}</div>

<h2>Capacités</h2>
<div class="fig">{capacites()}</div>

<h2 id="debit">Débit</h2>
{LEGENDE}
<h3>Meuble bas</h3>
<div class="fig">{table_debit("bas")}</div>
<p>Quincaillerie du meuble bas :</p>
<ul class="pistes">{quincaillerie("bas")}</ul>
<h3>Caisson haut</h3>
<div class="fig">{table_debit("haut")}</div>
<p>Quincaillerie du caisson haut :</p>
<ul class="pistes">{quincaillerie("haut")}</ul>
<p><a class="cta" href="{NOTICE}">Notice de montage →</a></p>

<h2 id="achats">Achats</h2>
{achats()}

<h2>À vérifier sur place</h2>
<ul class="pistes">
<li><b>Hauteur de la machine</b> : {M.LL['h']} pieds réglés au plus (à mesurer avant de couper les montants) ; le dessous du plan est à {cm(M.Z_PLAN)}. Régler les pieds pour qu'une cale de 5 mm posée sur la machine passe juste sous une règle posée sur les échelles : elle effleure le plan sans le toucher, les vibrations ne passent pas au plan.</li>
<li><b>Montants</b> : la hauteur du plan se joue sur leur longueur ({cm(M.Z_CADRE)}) : les couper ensemble, et vérifier la hauteur de la machine avant de couper. Sol irrégulier : caler sous les montants.</li>
<li><b>Plan à {cm(M.Z_DESSUS)}</b> : machine {M.LL['h']} + {cm(M.JEU_PLAN)} de jeu + plan {cm(M.PT)} ; un peu bas pour plier debout si on est grand, et le hublot est plus bas qu'en V4 (machine au sol).</li>
<li><b>Plan de travail</b> : vissé par-dessous à travers les lisses hautes, avec un lamage Ø 10 de 10 dans la lisse : la vis 4 × 40 traverse les 26 de tasseau restants et entre de 14 dans les 28 du plan ; avant-trou de 12 au plus dans le plan (ruban sur le foret).</li>
<li><b>Machine</b> : elle tient entre l'échelle du caisson et celle du mur sud, sur le tapis antivibration (0,6 de jeu de chaque côté).</li>
<li><b>Porte d'entrée</b> : gonds à {M.GONDS} du mur du fond (relevé), vantail de {M.PORTE['l']}, ouvert à {cm(M.FACE - leaf()[2])} de la façade ; on bascule le bac et on charge la machine porte fermée.</li>
<li><b>Robinet</b> d'arrêt quart de tour remonté dans la niche à {M.ROBINET['z']} (66 aujourd'hui), à 41 du mur sud ; d'après la NF C 15-100 (de mémoire, non vérifié ; à valider par l'électricien), circuit 20 A spécialisé pour la machine et prises hors des volumes 1 et 2.</li>
<li><b>Humidité</b> : les tasseaux sont en sapin brut non traité : poncés puis peints ou vernis sur toutes les faces, le bout des pieds compris (ils sont posés sur le carrelage ; une fuite de la machine ne doit pas les tremper). Peinture blanche : l'ossature se fond avec le mélaminé. Les tablettes sont en aggloméré mélaminé non hydrofuge : tous les chants coupés sont plaqués, le plan est siliconé contre les murs. Sous la machine, le tapis antivibration fait aussi bac.</li>
<li><b>Murs</b> : carrelés jusqu'à {M.CARRELAGE} (relevé). Le meuble bas n'est fixé à aucun mur ; le caisson haut est chevillé au-dessus du carrelage, dans le mur nu (variante METOD : rail de suspension en haut des structures, au-dessus aussi) : aucun perçage dans le carreau. Chevilles adaptées au mur (à vérifier : brique, placo, béton ?). Joint silicone entre plan et carrelage.</li>
<li><b>Charnières plates</b> : leurs lames se logent entre le rail et le plateau (≈ 1 mm, sans entaille) ; vis de 16 dans le rail, de 12 au plus dans le plateau (aggloméré de 18).</li>
<li><b>Alcôve</b> : mesurer la largeur en trois hauteurs ; au-delà de 5 mm d'écart, prévoir des fileurs.</li>
</ul>

<p class="note">Repère : origine à l'angle nord-ouest intérieur, x vers l'est, y vers le sud, z depuis le sol, cotes en cm (débit en mm). « Droite » et « gauche » s'entendent face au meuble. Source : <span class="mono">3d/sdb/modele.py</span> ; page : <span class="mono">3d/sdb/plan.py</span>, notice : <span class="mono">3d/sdb/montage.py</span>, modèle FreeCAD : <span class="mono">3d/sdb/cad.py</span> (<span class="mono">just sdb</span>).</p>

<section id="changements">
<h2>Changements</h2>
<table><thead><tr><th>Version</th><th>Date</th><th>Changements</th></tr></thead>
<tbody>{lignes}</tbody></table>
</section>
"""


SCRIPT = """
(function () {
  function garde(k, v) { try { localStorage.setItem("%(cle)s-" + k, v); } catch (e) {} }
  function lit(k) { try { return localStorage.getItem("%(cle)s-" + k); } catch (e) { return null; } }
  var bs = document.querySelectorAll(".vbar button[data-v]"), vs = document.querySelectorAll(".ver"), sommaire = function () {};
  function montre(v) {
    if (!document.querySelector('.ver[data-v="' + v + '"]')) v = "courante";
    vs.forEach(function (d) { d.hidden = d.dataset.v !== v; });
    bs.forEach(function (b) { b.setAttribute("aria-pressed", b.dataset.v === v); });
    garde("version", v);
    sommaire();
  }
  bs.forEach(function (b) { b.addEventListener("click", function () { montre(b.dataset.v); }); });
  function machine(c) {
    document.body.classList.toggle("mg", c === "m");
    document.querySelectorAll(".vbar button[data-m]").forEach(function (b) { b.setAttribute("aria-pressed", b.dataset.m === c); });
    garde("caisson", c);
  }
  document.querySelectorAll(".vbar button[data-m]").forEach(function (b) {
    b.addEventListener("click", function () { machine(b.dataset.m); });
  });
  machine(lit("caisson") === "m" ? "m" : "d");
  function linge(c) {
    document.body.classList.toggle("rb", c === "r");
    document.querySelectorAll(".vbar button[data-r]").forEach(function (b) { b.setAttribute("aria-pressed", b.dataset.r === c); });
    garde("linge", c);
  }
  document.querySelectorAll(".vbar button[data-r]").forEach(function (b) {
    b.addEventListener("click", function () { linge(b.dataset.r); });
  });
  linge(lit("linge") === "r" ? "r" : "l");
  function bascule(sel, cls, def) {
    var b = document.querySelector(sel);
    if (!b) return function () {};
    function pose(on) { document.body.classList.toggle(cls, on); b.setAttribute("aria-pressed", on); garde(cls, on ? "1" : "0"); }
    b.addEventListener("click", function () { pose(b.getAttribute("aria-pressed") !== "true"); });
    var v = lit(cls);
    pose(v === null ? def : v === "1");
    return pose;
  }
  bascule(".vbar .expl", "explications", true);
  var chg = bascule(".vbar .chg", "changements", false);
  var toc = document.querySelector(".toc");
  if (toc) {
    var tol = toc.querySelector("ol"), tb = toc.querySelector(".tbtn"), hs = [];
    function ouvert(on) {
      document.body.classList.toggle("toc-on", on);
      tb.setAttribute("aria-expanded", on);
      tb.textContent = on ? "« Sommaire" : "Sommaire »";
      garde("toc", on ? "1" : "0");
    }
    tb.addEventListener("click", function () { ouvert(!document.body.classList.contains("toc-on")); });
    ouvert(lit("toc") !== "0");
    function suivre() {
      var haut = document.querySelector(".vbar").offsetHeight;
      toc.style.top = haut + "px";
      var k = -1;
      hs.forEach(function (h, i) { if (h.offsetParent && h.getBoundingClientRect().top < haut + 80) k = i; });
      tol.querySelectorAll("a").forEach(function (a, i) { a.classList.toggle("on", i === k); });
    }
    sommaire = function () {
      var ver = document.querySelector(".ver:not([hidden])");
      hs = ver ? Array.prototype.slice.call(ver.querySelectorAll("h2")) : [];
      tol.innerHTML = "";
      hs.forEach(function (h) {
        var li = document.createElement("li"), a = document.createElement("a");
        var id = ancre(h);
        a.href = "#" + id; a.textContent = h.textContent.trim();
        a.addEventListener("click", function (e) {
          e.preventDefault();
          if (location.hash !== "#" + id) history.pushState(null, "", "#" + id);
          va(h, true);
        });
        li.appendChild(a); tol.appendChild(li);
      });
      suivre();
    };
    var attente = false;
    window.addEventListener("scroll", function () {
      if (!attente) { attente = true; requestAnimationFrame(function () { attente = false; suivre(); }); }
    }, {passive: true});
    window.addEventListener("resize", suivre);
  }
  // ancres : chaque titre de section reçoit un id lisible (« plan », « debit », « achats »…), suffixé par la version
  // pour les versions figées ; le sommaire et l'adresse (#ancre) pointent dessus.
  function ancre(h) {       // titre d'une section qui a déjà un id (Changements) : l'ancre est celle de la section
    return h.id || h.parentNode.id;
  }
  function slug(t) {
    return t.normalize("NFD").replace(/[\u0300-\u036f]/g, "").toLowerCase().replace(/[^a-z0-9]+/g, "-")
      .replace(/^-+|-+$/g, "");
  }
  vs.forEach(function (ver) {
    var suffixe = ver.dataset.v === "courante" ? "" : "-" + slug(ver.dataset.v);
    ver.querySelectorAll("h2").forEach(function (h) {
      if (!h.id && !h.parentNode.id) h.id = slug(h.textContent) + suffixe;
    });
  });
  function va(h, doux) {
    if (h.closest('section[id^="changements"]')) chg(true);
    h.scrollIntoView({behavior: doux ? "smooth" : "auto"});
  }
  function cible() {
    var id = decodeURIComponent(location.hash.slice(1)), h = id && document.getElementById(id);
    if (h && h.tagName === "SECTION") h = h.querySelector("h2");
    return h && h.tagName === "H2" ? h : null;
  }
  window.addEventListener("hashchange", function () {
    var h = cible();
    if (!h) return;
    var ver = h.closest(".ver");
    if (ver && ver.hidden) montre(ver.dataset.v);
    va(h, true);
  });
  var v0 = lit("version") || "courante", h0 = cible();
  if (location.hash && document.querySelector('.ver[data-v="' + decodeURIComponent(location.hash.slice(1)) + '"]'))
    v0 = decodeURIComponent(location.hash.slice(1));
  if (h0 && h0.closest(".ver")) v0 = h0.closest(".ver").dataset.v;
  montre(v0);
  if (h0) requestAnimationFrame(function () { va(h0, false); });
})();
"""


def barre(racine, figees=(), notice=True, cle=CLE):
    boutons = "".join(f'<button type="button" data-v="{v}">{v} figée</button>' for v, _ in figees)
    versions = (f'<span>Version</span><button type="button" data-v="courante" aria-pressed="true">{M.VERSION} en cours'
                f'</button>{boutons}') if figees else ""
    mach = ('<span>Caisson haut</span><button type="button" data-m="d" aria-pressed="true">Fait maison</button>'
            '<button type="button" data-m="m" aria-pressed="false">IKEA METOD</button>'
            '<span>Linge sale</span><button type="button" data-r="l" aria-pressed="true">L basculant</button>'
            '<button type="button" data-r="r" aria-pressed="false">Bacs à roulettes</button>') if notice else ""
    lien = (f'<a class="btn" href="{racine}{NOTICE}">Notice de montage</a>' if notice
            else f'<a class="btn" href="{racine}{os.path.basename(OUT)}">Plans</a>')
    return (f'<div class="vbar"><a class="back" href="{racine}index.html">← Plans</a>{versions}{mach}'
            f'<span class="sp"></span>{lien}<button type="button" class="expl" aria-pressed="false">Explications</button>'
            f'<button type="button" class="chg" aria-pressed="false">Changements</button></div>')


def entete(titre, racine, css):
    return f"""<!doctype html>
<html lang="fr">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{titre}</title>
<link rel="icon" href="{racine}favicon.svg" type="image/svg+xml">
<link rel="apple-touch-icon" href="{racine}apple-touch-icon.png">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Archivo:wght@400;500;700;800&family=JetBrains+Mono:wght@400;600&display=swap" rel="stylesheet">
<style>{css}</style>
</head>"""


def page(figees, racine=""):
    blocs = "".join(f'<div class="ver" data-v="{v}" hidden>{c}</div>' for v, c in figees)
    return f"""{entete("Meuble linge V5", racine, CSS)}
<body>
{barre(racine, figees)}
<nav class="toc" aria-label="Sommaire"><button type="button" class="tbtn" aria-expanded="true">Sommaire</button><ol></ol></nav>
<main class="wrap">
<div class="ver" data-v="courante">{contenu()}</div>
{blocs}
</main>
<script>{ANCRES}</script>
<script>{SCRIPT % {"cle": CLE}}</script>
</body>
</html>
"""


FIGEES = os.path.join(os.path.dirname(os.path.abspath(__file__)), "figees")


def figer():
    """Fige la version courante : contenu dans figees/<version>.html et page autonome archive/sdb-meuble-<version>.html."""
    os.makedirs(FIGEES, exist_ok=True)
    v = M.VERSION
    c = contenu()
    for ident in set(re.findall(r'id="([^"]+)"', c)):
        c = c.replace(f'id="{ident}"', f'id="{ident}-{v}"')
    with open(os.path.join(FIGEES, f"{v}.html"), "w", encoding="utf-8") as fh:
        fh.write(c)
    with open(os.path.join(ROOT, "archive", f"sdb-meuble-{v.lower()}.html"), "w", encoding="utf-8") as fh:
        fh.write(page([], "../").replace(f'href="{NOTICE}"', f'href="../{NOTICE}"'))
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
