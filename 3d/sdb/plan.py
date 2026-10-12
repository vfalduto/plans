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
OUT = os.path.join(ROOT, "sdb-meuble-v3.html")
NOTICE = "sdb-meuble-v3-montage.html"
CLE = "sdb-v3"          # préfixe des préférences mémorisées (localStorage)

Z_COUPE_PLAN = 100      # le plan vu de dessus est une coupe horizontale sous le plan de travail
COUPE_B = 55            # y, regard vers le nord : machine, trappe, robinet (mêmes dans les deux versions)


def coupe_c(c):         # y, regard vers le nord : à travers les bacs
    y = (M.CB["y0"] + M.CB["y1"]) / 2
    return y if c == "d" else M.Y1 - y


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
    return nord if c == "d" else sud


# ------------------------------------------------------------------ styles par rôle : (vu, coupé)
CLS = {"socle": ("socle", "soclec"), "rebord": ("socle", "soclec"), "caisson": ("cab", "cabc"), "fond": ("fond", "fondc"),
       "plinthe": ("plinthe", "cabc"), "bac": ("bac", "bacc"), "facade": ("fac", "facc"), "tasseau": ("tas", "tasc"),
       "corniere": ("alu", "alu"), "plan": ("top", "topc"), "trappe": ("trap", "trap"), "etagere": ("shelf", "shelfc"),
       "porte": ("porte", "portec"), "fileur": ("cab", "cabc"), "machine": ("appf", "appc"), "led": ("led", "led"),
       "prise": ("plug", "plug"),
       "support": ("cab", "cabc"), "barre": ("tas", "tasc"), "sac": ("sac", "sacc")}


# ------------------------------------------------------------------ plan vu de dessus (coupe horizontale à z 100)
def leaf():
    return (M.PORTE["x1"] - 4, 0, M.PORTE["x1"], M.PORTE["l"])   # vantail ouvert à 90°, x0 y0 x1 y1


def inter(a, b):
    x0, y0, x1, y1 = max(a[0], b[0]), max(a[1], b[1]), min(a[2], b[2]), min(a[3], b[3])
    return (x0, y0, x1, y1) if x0 < x1 and y0 < y1 else None


def bacs_y(c):
    return (M.CB["y0"], M.CB["y1"]) if c == "d" else (M.Y1 - M.CB["y1"], M.Y1 - M.CB["y0"])


def plan_svg(c):
    blocs = M.version(c)
    o = []
    sol = [(0, 0), (234, 0), (234, 114), (167, 114), (167, 160), (0, 160)]
    o.append(poly(sol, "sdbf"))
    o.append('<path class="w" fill-rule="evenodd" d="M-5 -5 H239 V119 H172 V165 H-5 Z M0 0 V160 H167 V114 H234 V0 Z"/>')
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
    for b in sorted([b for b in blocs if b.z0 < Z_COUPE_PLAN and b.role not in ("prise",)], key=lambda b: b.z1):
        vu, coupe = CLS[b.role]
        o.append(rect(b.x0, b.y0, b.x1, b.y1, coupe if b.z1 > Z_COUPE_PLAN else vu))
    # bacs basculés (tireté) : emprise de la façade avancée
    ya, yb = bacs_y(c)
    av = M.BAC["avancee"]
    bas = (M.FACE - av, ya + 0.15, M.FACE, yb - 0.15)
    o.append(rect(*bas, "swing"))
    o.append(text(M.FACE - av / 2, (ya + yb) / 2 + 1.5, "façades basculées", "lblx muted",
                  extra=f' transform="rotate(-90 {f(M.FACE - av / 2)} {f((ya + yb) / 2 + 1.5)})"'))
    # hublot : charnière à gauche (face au meuble, donc au nord) ; 180° si rien ne l'arrête, 90° contre le mur nord
    m = [b for b in blocs if b.role == "machine"][0]
    cx, r = M.FACE - 1.5, 23.5
    yh = m.y0 + 6
    if c == "d":
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
    o.append(rect(ch["x0"], ch["y0"], ch["x1"], ch["y1"], "upper"))
    o.append(f'<line class="upper" x1="{ch["x0"]}" y1="{M.CENTRE}" x2="{ch["x1"]}" y2="{M.CENTRE}"/>')
    # étiquettes
    xm = (M.CB["x0"] + M.CB["x1"]) / 2
    o.append(text(xm, (ya + yb) / 2 - 2, "Sacs 1 et 2", "lbls"))
    o.append(text(xm, (ya + yb) / 2 + 4, "façades basculantes", "lblx"))
    o.append(text((m.x0 + m.x1) / 2, (m.y0 + m.y1) / 2 - 2, "LL", "lblb"))
    o.append(text((m.x0 + m.x1) / 2 - 8, (m.y0 + m.y1) / 2 + 8, f"sur socle de {M.SOCLE_H}", "lblx"))
    o.append(f'<path class="lead" d="M{f(tr["x0"])} {f(tr["y1"] - 4)} L{f(tr["x0"] - 9)} {f(tr["y1"] - 4)}"/>')
    o.append(text(tr["x0"] - 10, tr["y1"] - 3, "trappe robinet", "lblx", "end"))
    # cotes
    o.append(cote_h(M.X0, M.X1, -14, "67 (alcôve)"))
    o.append(cote_h(0, 234, -22, "234"))
    o.append(cote_v(0, 160, -12, "160"))
    o.append(cote_v(0, 114, 262, "114"))
    o.append(cote_v(ya, yb, 250, cm(yb - ya)))
    ly = (M.LLZ["y0"], M.LLZ["y1"]) if c == "d" else (M.Y1 - M.LLZ["y1"], M.Y1 - M.LLZ["y0"])
    o.append(cote_v(*ly, 250, f"{cm(ly[1] - ly[0])} LL"))
    o.append(cote_h(lf[2], M.FACE, 104, cm(M.FACE - lf[2])))
    # traits de coupe
    yc = coupe_c(c)
    for y, lab in ((COUPE_B, "B"), (yc, "C")):
        o.append(f'<line class="sec" x1="140" y1="{f(y)}" x2="244" y2="{f(y)}"/>')
        o.append(text(136, y + 2, lab, "sect"))
    o.append(f'<path class="secm" d="M164 -2 l-4 -3 v6z"/>')
    o.append(text(158, 3, "A", "sect", "end"))
    o.append(text(117, 178, "N ↑ · coupe horizontale à 100 · plan de travail en pointillé fin, hauts P 45 en pointillé épais",
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
        s = M.SOCLE
        r.append(text(ym, -(M.SOCLE_H / 2) + 1.5, f"socle {M.SOCLE_H}", "lblx"))
        # poignées des façades et sens de bascule
        ya, yb = bacs_y(c)
        for k, (z0, z1) in enumerate(M.FACADES):
            r.append(rect((ya + yb) / 2 - 6, -(z1 - 3), (ya + yb) / 2 + 6, -(z1 - 4.2), "handle"))
            r.append(text((ya + yb) / 2, -(z0 + z1) / 2 + 6, f"sac ≈ {M.VOLUME_BAC:.0f} L · bascule à {M.BAC['angle']}°", "lblx"))
        # niche
        r.append(text(57, -(M.Z_HAUT - 10), f"Niche {cm(M.Z_HAUT - M.Z_DESSUS)} : prises + USB, crochet sèche-cheveux, LED",
                      "lblx"))
        r.append(f'<path class="hook" d="M6 {f(-(M.Z_HAUT - 5))} v6 q0 3 3 3"/>')
        # vantail ouvert (tireté rouge), devant
        r.append(rect(0 - 5, -204, M.PORTE["l"], 0, "leafg"))
        r.append(text(57, 19, "tireté rouge : vantail de la porte ouvert à 90°, 11 cm devant les façades", "lblx rt"))
        r.append(text(-3, 7, "nord · porte", "lblx muted", "start"))
        r.append(text(117, 7, "sud · lavabo", "lblx muted", "end"))
        ly = (M.LLZ["y0"], M.LLZ["y1"]) if c == "d" else (M.Y1 - M.LLZ["y1"], M.Y1 - M.LLZ["y0"])
        r.append(cote_h(ya, yb, 11, cm(yb - ya)))
        r.append(cote_h(*ly, 11, f"{cm(ly[1] - ly[0])} machine"))
        return r

    hz = [M.PLINTHE, M.FACADES[0][1], M.Z_PLAN, M.Z_DESSUS, M.Z_HAUT, M.Z_HAUT1]
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
        rb = M.ROBINET
        r.append(rect(M.X1 - 3, -(rb["z"] + 2), M.X1, -(rb["z"] - 2), "valve"))
        r.append(f'<path class="lead" d="M{M.X1 - 3} {-rb["z"]} L{M.X1 - 8} {-rb["z"] - 6}"/>')
        r.append(text(M.X1 - 9, -rb["z"] - 8, f"robinet encastré h {rb['z']}", "lblx", "end"))
        r.append(text(M.X1 - 9, -rb["z"] - 3.5, "+ prise de la LL à côté", "lblx", "end"))
        r.append(f'<path class="lead" d="M{M.TRAPPE["x0"] + 4} {-M.Z_DESSUS - 1} L{M.TRAPPE["x0"] - 6} {-M.Z_DESSUS - 12}"/>')
        r.append(text(M.TRAPPE["x0"] - 7, -M.Z_DESSUS - 13, "trappe 30 × 10, couvercle amovible", "lblx", "end"))
        m = [b for b in blocs if b.role == "machine"][0]
        r.append(text((m.x0 + m.x1) / 2, -(m.z0 + 30), f"LL {M.LL['l']} × {M.LL['p']} × {M.LL['h']}", "lbls"))
        r.append(text((m.x0 + m.x1) / 2, -(m.z0 + 24), f"jeu arrière {cm(M.X1 - m.x1)} · jeu sous le plan {cm(M.JEU_PLAN)}", "lblx"))
        r.append(text((m.x0 + m.x1) / 2, -(M.SOCLE_H / 2) + 1.5, f"socle en tablettes de 18, h {M.SOCLE_H}", "lblx"))
        r.append(text(M.CH["x0"] - 2, -(M.Z_HAUT + 50), "serviettes", "lblx", "end"))
        r.append(text(M.CH["x0"] - 2, -(M.Z_HAUT + 44), "(au nord, au fond)", "lblx muted", "end"))
        r.append(text(M.FACE + 4, -(M.Z_DESSUS + 32), "niche", "lblx", "start"))
        r.append(cote_h(M.CH["x0"], M.CH["x1"], -(M.H + 4), "45"))
        r.append(cote_h(M.FACE, M.X1, 12, cm(M.X1 - M.FACE)))
        r.append(cote_h(leaf()[2], M.FACE, 12, cm(M.FACE - leaf()[2])))
        return r

    return vue(c, "y", COUPE_B, -1, 140, 244, extra, [M.SOCLE_H, M.SOCLE_H + M.LL["h"], M.Z_DESSUS, M.Z_HAUT],
               f"Coupe B-B, {M.VERSIONS[c]}")


def coupe_c_svg(c):
    yc = coupe_c(c)

    def extra(blocs):
        r = []
        murs_coupe(r)
        # façades basculées (tireté) : façade, supports et barre avant tournés autour de l'axe ; le sac ouvert va de la
        # barre avant basculée à la barre arrière
        for k in (1, 2):
            axe, a = M.BAC[f"axe{k}"], M.BAC["angle"]
            xf0, xr0, zb0, zb1 = M.BAC[f"barres{k}"]
            bx = M.BAC["barre"][0]
            for b in blocs:
                if b.groupe == f"bac{k}" and (b.role == "facade" or b.nom.endswith("_av") or "support_av" in b.nom):
                    pts = [M.bascule(x, z, axe, a) for x, z in b.pts("y")]
                    r.append(poly([(x, -z) for x, z in pts], "swingp"))
            fa = M.bascule(xf0 + bx, zb0 + 1, axe, a)
            r.append(poly([(fa[0], -fa[1]), (xr0, -(zb0 + 1)), (xr0 + bx - 1, -(axe[1] + 1)),
                           (fa[0] + 4, -(axe[1] + 1))], "sacopen"))
            r.append(f'<circle class="axe" cx="{f(axe[0])}" cy="{f(-axe[1])}" r="0.9"/>')
            z0, z1 = M.CASES[k - 1]
            r.append(text(M.CB["x0"] + 16, -(z0 + 14), f"sac ≈ {M.VOLUME_BAC:.0f} L", "lblx"))
        r.append(text(M.FACE - 14, -(M.FACADES[1][1] - 2), f"basculé {M.BAC['angle']}°", "lblx muted"))
        r.append(f'<path class="lead" d="M{f(M.CB["x0"])} {f(-M.BAC["axe2"][1])} L{f(M.CB["x0"] + 16)} {f(-M.BAC["axe2"][1] + 7)}"/>')
        r.append(text(M.CB["x0"] + 17, -M.BAC["axe2"][1] + 9, "charnière piano (axe)", "lblx", "start"))
        xf0, xr0, zb0, zb1 = M.BAC["barres2"]
        r.append(f'<path class="lead" d="M{f(xr0 + 1)} {f(-zb1)} L{f(xr0 + 8)} {f(-(zb1 + 5))}"/>')
        r.append(text(xr0 + 9, -(zb1 + 5.5), "barres 20 × 40", "lblx", "start"))
        r.append(cote_h(M.CB["x0"], xr0, 12, cm(M.BAC["prof"])))
        r.append(cote_h(M.FACE - M.BAC["avancee"], M.FACE, 12, cm(M.BAC["avancee"])))
        r.append(cote_h(M.CH["x0"], M.CH["x1"], -(M.H + 4), "45"))
        return r

    z1, z2 = M.CASES
    return vue(c, "y", yc, -1, 140, 244, extra, [M.PLINTHE, z1[1], z2[0], M.Z_PLAN, M.Z_DESSUS, M.Z_HAUT],
               f"Coupe C-C, {M.VERSIONS[c]}")


# ------------------------------------------------------------------ débit
def debit():
    """Une ligne par repère : quantité, longueur × largeur × épaisseur en mm (version d ; la version g a les mêmes pièces)."""
    lignes = {}
    for b in M.PIECES:
        if not b.rep:
            continue
        if isinstance(b, M.Profil):
            dims = (b.x1 - b.x0, b.z1 - b.z0, b.y1 - b.y0)
        else:
            e = sorted((b.x1 - b.x0, b.y1 - b.y0, b.z1 - b.z0), reverse=True)
            dims = tuple(e)
        lignes.setdefault(b.rep, []).append(dims)
    cle = lambda r: (r[0], int(r[1:]))
    r = []
    for rep in sorted(lignes, key=cle):
        d = lignes[rep]
        L, l, e = (round(v * 10) for v in max(d))
        q = len(d)
        if rep == "E2":         # une cornière, modélisée en deux ailes
            q, l, e = 1, 30, 30
        r.append(dict(rep=rep, mat=rep[0], nom=M.NOMS[rep], q=q, L=L, l=l, e=e, u=M.USINAGES.get(rep, "")))
    return r


def table_debit():
    o, mat = [], None
    surf = Counter()
    for p in debit():
        if p["mat"] != mat:
            mat = p["mat"]
            n, d, _ = M.MATERIAUX[mat]
            o.append(f'<tr class="mat"><td colspan="6"><span class="sw m{mat}"></span>{mat} — {escape(n)} '
                     f'<span class="note">· {escape(d)}</span></td></tr>')
        if mat not in "E":
            surf[mat] += p["q"] * p["L"] * p["l"] / 1e6
        sec = f'{p["l"]} × {p["e"]}' if mat == "E" else f'{p["l"]}'
        o.append(f'<tr><td class="mono">{p["rep"]}</td><td>{escape(p["nom"])}</td><td class="num">{p["q"]}</td>'
                 f'<td class="num">{p["L"]}</td><td class="num">{sec}</td><td class="u">{escape(p["u"])}</td></tr>')
    tot = " · ".join(f'{m} {virg(v, 2)} m²' for m, v in sorted(surf.items()))
    return (f'<div class="scroll"><table class="debit"><thead><tr><th>Rep.</th><th>Pièce</th><th class="num">Qté</th>'
            f'<th class="num">Long.</th><th class="num">Larg.</th><th>Usinages, remarques</th></tr></thead>'
            f'<tbody>{"".join(o)}</tbody></table></div><p class="note">Cotes en mm, pièces finies. Surfaces nettes : {tot} '
            f'(compter 20 à 30 % de chute).</p>')


# ------------------------------------------------------------------ achats (calepinage + liste de courses)
def tablette_svg(p, k):
    L, l = p.fmt["L"], p.fmt["l"]
    o = [f'<rect class="tb" x="0" y="0" width="{L}" height="{l}"/>']
    for rep, x, y, a, b in p.poses():
        o.append(f'<rect class="pc m{rep[0]}" x="{x}" y="{y}" width="{a}" height="{b}"/>')
        if b >= 60 and a >= 140:
            o.append(f'<text class="pt" x="{x + a / 2}" y="{y + b / 2 - 8}">{rep}</text>'
                     f'<text class="pd" x="{x + a / 2}" y="{y + b / 2 + 42}">{a} × {b}</text>')
        elif b >= 40:
            o.append(f'<text class="pt ps" x="{x + a / 2}" y="{y + b / 2 + 12}">{rep}</text>')
    return (f'<div class="tab"><div class="tabt"><b>T{k}</b> · {L} × {l} · {p.taux():.0%} utilisés</div>'
            f'<svg viewBox="-4 -4 {L + 8} {l + 8}" role="img" aria-label="Tablette {k}, {L} × {l}">{"".join(o)}</svg></div>')


def achats():
    cal = CAL.calepinage(debit())
    t = cal["M18"]["retenu"]
    d = cal["D"]["retenu"]
    tabs = "".join(tablette_svg(p, k + 1) for k, p in enumerate(t["panneaux"]))
    plan_ = "".join(tablette_svg(p, "P") for p in d["panneaux"])
    essais = " ; ".join(f'{e["nom"]} : ' + (f'{e["n"]} tablettes, {euros(e["prix"])}' if e["n"] else "impossible")
                        for e in cal["M18"]["essais"])
    lignes = []
    for fmt in M.PANNEAUX["M18"] + M.PANNEAUX["D"]:
        stock = "M18" if fmt in M.PANNEAUX["M18"] else "D"
        n = sum(1 for p in cal[stock]["retenu"]["panneaux"] if p.fmt is fmt)
        if n:
            lignes.append((fmt["nom"], fmt["ref"], n, fmt["prix"], fmt["stock"]))
    tot = Counter()
    for _, _, q in M.ETAPES:
        tot.update(q)
    manque = []
    for code, w in M.WELDOM.items():
        if w is None:
            manque.append(M.QUINCAILLERIE[code])
        else:
            lignes.append((w[0], w[4], w[2], w[1], w[3]))
    total = sum(n * px for _, _, n, px, _ in lignes)
    corps = "".join(
        f'<tr><td>{escape(nom)}</td><td class="mono">{ref}</td><td class="num">{n}</td><td class="num">{euros(px)}</td>'
        f'<td class="num">{euros(n * px)}</td><td class="num">{"—" if st is None else st}</td></tr>'
        for nom, ref, n, px, st in lignes)
    mg = M.MAGASIN
    return f"""<p>Tout le bois vient de <b>{escape(mg['nom'])}</b> ({escape(mg['adresse'])}, {mg['tel']}). Le magasin ne vend ni plaque entière, ni panneau de 12, ni contreplaqué ou MDF hydrofuge de 18 : les seuls panneaux de 18 sont les tablettes mélaminées blanches de 2500 de long. Le meuble entier est donc taillé dans {t['n']} tablettes de 18 et un plan de travail de 28. Prix et stock relevés en ligne le {mg['releve']}.</p>
<div class="fig"><div class="tabs">{tabs}</div>
<p class="cap">Calepinage des tablettes de 18 : refente en bandes sur la longueur, puis tronçonnage (trait de scie de {CAL.TRAIT} compté). Les chants longs d'usine sont déjà plaqués ; les chants coupés visibles reçoivent un chant thermocollant. Formats comparés : {essais}. Retenu : le mélange.</p></div>
<div class="fig"><div class="tabs">{plan_}</div>
<p class="cap">Plan de travail 1800 × 640 × 28 recoupé à {d['panneaux'][0].poses()[0][3]} ; le couvercle de trappe D2 est taillé dans la chute de l'encoche (dessiné ici à part).</p></div>
<h3>Liste de courses · {escape(mg['nom'])}</h3>
<div class="scroll"><table class="debit"><thead><tr><th>Article Weldom</th><th>Réf.</th><th class="num">Qté</th><th class="num">Prix</th><th class="num">Total</th><th class="num">Stock</th></tr></thead>
<tbody>{corps}</tbody><tfoot><tr><td colspan="4"><b>Total Weldom</b></td><td class="num"><b>{euros(total)}</b></td><td></td></tr></tfoot></table></div>
<p class="note">Stock : nombre affiché sur la fiche produit pour ce magasin le {mg['releve']} (« — » : en stock, nombre non lu). La découpe en magasin existe (service « découpe bois ») ; tarif et nombre de coupes non publiés : appeler avant. Vis, colle, chevilles et silicone : en rayon, non chiffrés.</p>
<p><b>À acheter ailleurs</b> (absent du catalogue du magasin) : {escape(" ; ".join(manque))} ; profil alu pour le ruban LED.</p>"""


def euros(v):
    return f"{v:.2f}".replace(".", ",") + " €"


def quincaillerie():
    tot = Counter()
    for _, _, q in M.ETAPES:
        tot.update(q)
    return "".join(f'<li><b>{n}</b> × {escape(M.QUINCAILLERIE[k])}</li>' for k, n in tot.items())


# ------------------------------------------------------------------ page
CSS = """
:root{
  --paper:#F7F8F6; --ink:#1D2A33; --muted:#5E6B73; --line:#C9D0D4; --wood:#B07A45;
  --water:#2F7FB5; --tri:#C8412C; --panel:#FFFFFF; --cab:#ECE6DA; --tall:#D8CFBD; --bac:#E3C9A0;
  --socle:#C8B79B; --glass:#CFE4F2; --tile:#E9EEF0; color-scheme:light;
}
@media (prefers-color-scheme: dark){
  :root:not([data-theme="light"]){
    --paper:#141A1F; --ink:#E4EAED; --muted:#9AA7AE; --line:#34414A; --wood:#C9925A;
    --water:#5AA8DE; --tri:#E8664F; --panel:#1B2329; --cab:#2A3338; --tall:#394449; --bac:#5B4B33;
    --socle:#4C4436; --glass:#1F3A4E; --tile:#1D262C; color-scheme:dark;
  }
}
:root[data-theme="dark"]{
  --paper:#141A1F; --ink:#E4EAED; --muted:#9AA7AE; --line:#34414A; --wood:#C9925A;
  --water:#5AA8DE; --tri:#E8664F; --panel:#1B2329; --cab:#2A3338; --tall:#394449; --bac:#5B4B33;
  --socle:#4C4436; --glass:#1F3A4E; --tile:#1D262C; color-scheme:dark;
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
.pc{stroke:var(--ink);stroke-width:2;fill:var(--cab)}.pc.mB{fill:var(--bac)}.pc.mC{fill:var(--tall)}.pc.mS{fill:var(--socle)}.pc.mD{fill:var(--wood)}
.pt{font:700 64px "JetBrains Mono",ui-monospace,monospace;fill:var(--ink);text-anchor:middle}
.pt.ps{font-size:40px}
.pd{font:400 40px "JetBrains Mono",ui-monospace,monospace;fill:var(--muted);text-anchor:middle}
.sw{display:inline-block;width:12px;height:12px;border-radius:3px;margin-right:8px;vertical-align:-1px;border:1px solid var(--ink)}
.mA{background:var(--cab)}.mB{background:var(--bac)}.mC{background:var(--tall)}.mD{background:var(--wood)}.mS{background:var(--socle)}.mE{background:#B9C2C8}
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
    """Les deux versions d'une figure ; le bouton Machine de la barre choisit laquelle est visible."""
    return f'<div class="vd">{fn("d")}</div><div class="vg">{fn("g")}</div>'


def comparatif():
    ya_d, yb_d = bacs_y("d")
    ya_g, yb_g = bacs_y("g")
    lf = leaf()
    rec_g = max(0, lf[3] - ya_g)
    lignes = [
        ("Basculer les façades porte d'entrée ouverte", "non (façades derrière le vantail)",
         f"non : le bas de la façade recouvre le vantail sur {cm(rec_g)}"),
        ("Charger la machine porte ouverte", "non (hublot à 7 du vantail)", "non (machine dans la zone du vantail)"),
        ("Hublot", "180°, rabattu contre les façades", "90° (mur nord)"),
        ("Distance de l'évacuation", "courte (côté lavabo)", "≈ 50 de plus"),
        ("Plan, niche, hauts, trappe", "identiques", "identiques"),
    ]
    corps = "".join(f"<tr><td>{a}</td><td>{b}</td><td>{c}</td></tr>" for a, b, c in lignes)
    return (f'<div class="scroll"><table><thead><tr><th>Critère</th><th>Machine à droite</th><th>Machine à gauche</th>'
            f'</tr></thead><tbody>{corps}</tbody></table></div>')


def capacites():
    ch = M.CH
    _et = next(b for b in M.PIECES if b.nom == "ch_etagere_n1")
    lignes = [
        ("Linge sale", f"2 sacs en tissu {cm(M.BAC['largeur_sac'])} de large, {cm(M.BAC['h_sac'])} de haut, entre "
         f"deux barres", f"2 × ≈ {M.VOLUME_BAC:.0f} L"),
        ("Serviettes (nord)", f"{ch['serviettes']} étagères, cases de {cm(ch['case_serviettes'])}, "
         f"{cm(_et.y1 - _et.y0)} × {cm(_et.x1 - _et.x0)} utiles",
         "≈ 30 serviettes de bain"),
        ("Pharmacie et produits divers (sud)", f"{ch['pharmacie']} étagères, cases de {cm(ch['case_pharmacie'])}",
         "10 bacs à tirer 16 × 16 × 35"),
        ("Plan de travail", f"{cm(M.Y1 - 2 * M.J)} × {cm(M.PLAN_P)} à {cm(M.Z_DESSUS)}", "pliage"),
        ("Niche", f"{cm(M.Y1)} × {cm(M.Z_HAUT - M.Z_DESSUS)} de haut, {cm(M.CH['x0'] - M.FACE)} dégagés devant les hauts",
         "sèche-cheveux, brosse à dents"),
    ]
    corps = "".join(f'<tr><td>{a}</td><td>{b}</td><td class="num">{c}</td></tr>' for a, b, c in lignes)
    return f'<table><thead><tr><th>Rangement</th><th>Dimensions</th><th class="num">Capacité</th></tr></thead><tbody>{corps}</tbody></table>'


def contenu():
    b, s = M.BAC, M.SOCLE
    lignes = "".join(f'<tr><td class="mono">{v}</td><td class="mono">{d}</td><td>{escape(x)}</td></tr>'
                     for v, d, x in M.CHANGEMENTS)
    return f"""<div class="kicker">Salle de bain · alcôve 67 × 114 · {M.VERSION}</div>
<h1>Meuble linge V3</h1>
<p class="pitch">La machine monte de {M.SOCLE_H} cm sur un socle en bois : le hublot est un peu plus haut. Le plan de travail filant passe au-dessus, à {cm(M.Z_DESSUS)}. À côté, deux sacs en tissu superposés reçoivent le linge sale : on tire la façade, elle bascule et ouvre le sac, on jette le linge. Au-dessus : la niche avec les prises, puis les placards jusqu'au plafond. Le bouton <b>Machine</b> de la barre place la machine à droite ou à gauche, sur toutes les vues.</p>
<p><a class="cta" href="{NOTICE}">Notice de montage, étape par étape →</a></p>

<h2>Plan</h2>
<div class="fig"><div class="scroll">{deux(plan_svg)}</div>
<p class="cap">Coupe horizontale à {Z_COUPE_PLAN} cm, sous le plan de travail : pièces coupées en foncé. Façades à x {cm(M.FACE)}, à {cm(M.FACE - leaf()[2])} du vantail de la porte ouvert. Tireté : façades basculées (elles avancent de {cm(b['avancee'])}) et hublot ouvert. Rouge plein : recouvrement avec le vantail ouvert. Trappe du robinet (hachurée) au fond du plan, centrée sur le meuble ; hauts de 45 en pointillé épais.</p></div>

<h2>Élévation A · face au meuble</h2>
<div class="fig"><div class="scroll">{deux(elevation)}</div>
<p class="cap">Vue vers l'est : le nord (porte) à gauche, le sud (lavabo) à droite. Socle de {M.SOCLE_H}, machine de {M.SOCLE_H} à {M.SOCLE_H + M.LL['h']}, {cm(M.JEU_PLAN)} de jeu, plan de {cm(M.PT * 10)} mm de {cm(M.Z_PLAN)} à {cm(M.Z_DESSUS)}. Deux façades de sac identiques ({cm(M.FACADES[0][1] - M.FACADES[0][0])}) séparées par le chant de la tablette ; poignée en haut de chaque façade. Niche de {cm(M.Z_HAUT - M.Z_DESSUS)}, caisson haut de {M.Z_HAUT} à {M.Z_HAUT1}, fileur jusqu'au plafond, deux portes coulissantes.</p></div>

<div class="grid2">
<div class="fig"><h3>Coupe B-B · machine et trappe</h3><div class="scroll">{deux(coupe_b)}</div>
<p class="cap">Coupe à y {COUPE_B}, regard vers le nord. Socle plein en tablettes de 18 (cadre et plateau, rebord de {s['rebord']} sur trois côtés, tapis antivibration). Le robinet d'arrêt, dans le jeu de {cm(M.X1 - M.FACE - M.LL['p'])} derrière la machine, s'atteint par la trappe du plan. Au fond, les hauts côté serviettes.</p></div>
<div class="fig"><h3>Coupe C-C · sacs basculants</h3><div class="scroll">{deux(coupe_c_svg)}</div>
<p class="cap">Coupe à travers les sacs, regard vers le nord. Dans chaque case, le sac pend entre deux barres de bois : l'avant posé dans deux supports au dos de la façade, l'arrière dans deux supports aux côtés du caisson, à {b['prof']} du bord avant. La façade pivote sur une charnière piano au bord avant de sa case (point rouge) ; deux compas l'arrêtent à {b['angle']}° : elle avance de {cm(b['avancee'])}, emmène la barre avant, et la bouche du sac passe de {cm(b['bouche_fermee'])} à {cm(b['bouche'])} (tireté bleu).</p></div>
</div>

<h2>Sacs basculants</h2>
<ul class="pistes">
<li><b>Principe</b> : un sac en tissu tendu entre deux barres de bois, l'une suit la façade, l'autre reste dans le caisson. On tire la façade, le sac s'ouvre, on jette le linge. Plus de caisse en bois à porter.</li>
<li><b>Vider</b> : façade basculée, on soulève la barre arrière de ses entailles, puis la barre avant, et on sort le sac en tenant les deux barres : il se ferme tout seul en les rapprochant. On l'emporte à la machine.</li>
<li><b>Le sac</b> : {escape(b['sac'])} ; à coudre ou à faire coudre (toile de coton épaisse ou polyester lavable), absent du Weldom. Deux sacs par case permettent d'en laver un pendant que l'autre sert.</li>
<li><b>Superposés sur toute la largeur</b> : ≈ {M.VOLUME_BAC:.0f} L chacun ; sac du haut à hauteur de main ({cm(M.CASES[1][0])} → {cm(M.CASES[1][1])}), sac du bas pour le linge qu'on trie moins souvent.</li>
<li><b>Arrêt</b> : deux compas d'abattant à frein par façade ; elle revient seule en place, sans claquer.</li>
</ul>

<h2>Capacités</h2>
<div class="fig">{capacites()}</div>

<h2>Droite ou gauche</h2>
<div class="fig">{comparatif()}</div>

<h2 id="debit">Débit</h2>
<div class="fig">{table_debit()}</div>
<p>Quincaillerie (toutes étapes) :</p>
<ul class="pistes">{quincaillerie()}</ul>
<p><a class="cta" href="{NOTICE}">Notice de montage →</a></p>

<h2 id="achats">Achats</h2>
{achats()}

<h2>À vérifier sur place</h2>
<ul class="pistes">
<li><b>Hauteur de la machine</b> : {M.LL['h']} pieds réglés au plus ; avec le socle, le dessus est à {M.SOCLE_H + M.LL['h']} et le plan à {cm(M.Z_PLAN)} dessous ({cm(M.JEU_PLAN)} de jeu, les feuillures de la trappe passent à {cm(M.Z_PLAN - M.FEUIL - M.SOCLE_H - M.LL['h'])} au-dessus).</li>
<li><b>Plan à {cm(M.Z_DESSUS)}</b> : hauteur d'un plan de cuisine haut, bonne pour plier debout ; elle suit le socle (socle + {M.LL['h']} + {cm(M.JEU_PLAN)} de jeu + {cm(M.PT)} de plan).</li>
<li><b>Socle</b> : la machine doit être d'aplomb et ne pas « marcher » ; le socle est vissé au caisson bas et au mur. Pour une machine de plus de 1 400 tr/min, ajouter une traverse sous chaque pied.</li>
<li><b>Porte d'entrée</b> : paumelles à x ≈ 157, vantail de 76 ; dans les deux versions, on bascule les façades et on charge la machine porte fermée.</li>
<li><b>Robinet</b> d'arrêt quart de tour encastré à {M.ROBINET['z']}, saillie ≤ 3 ; d'après la NF C 15-100 (de mémoire, non vérifié ; à valider par l'électricien), circuit 20 A spécialisé pour la machine et prises hors des volumes 1 et 2.</li>
<li><b>Humidité</b> : les tablettes sont en aggloméré mélaminé non hydrofuge (comme la plupart des meubles de salle de bain en kit) ; tous les chants coupés sont plaqués, le plan est siliconé contre les murs. Le socle sous la machine est le point faible en cas de fuite : le tapis antivibration fait aussi bac ; sinon, dalle d'aggloméré hydrofuge 2050 × 610 × 22 en stock au même magasin (22,50 €).</li>
<li><b>Murs carrelés</b> : tasseaux, cornière, caisson bas, socle et caisson haut se fixent dans le carrelage. Percer au foret carrelage (ou foret verre) à basse vitesse, sans percussion jusqu'au mur, ruban de masquage sur le carreau ; dans les joints quand c'est possible ; chevilles adaptées au mur derrière (à vérifier : brique, placo, béton ?). Joint silicone entre plan et carrelage.</li>
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
    document.body.classList.toggle("mg", c === "g");
    document.querySelectorAll(".vbar button[data-m]").forEach(function (b) { b.setAttribute("aria-pressed", b.dataset.m === c); });
    garde("machine", c);
  }
  document.querySelectorAll(".vbar button[data-m]").forEach(function (b) {
    b.addEventListener("click", function () { machine(b.dataset.m); });
  });
  machine(lit("machine") === "g" ? "g" : "d");
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
    mach = ('<span>Machine</span><button type="button" data-m="d" aria-pressed="true">à droite</button>'
            '<button type="button" data-m="g" aria-pressed="false">à gauche</button>')
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
    return f"""{entete("Meuble linge V3", racine, CSS)}
<body>
{barre(racine, figees)}
<nav class="toc" aria-label="Sommaire"><button type="button" class="tbtn" aria-expanded="true">Sommaire</button><ol></ol></nav>
<main class="wrap">
<div class="ver" data-v="courante">{contenu()}</div>
{blocs}
</main>
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
