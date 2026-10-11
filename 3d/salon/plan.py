# Génère salon-v4.html (plan vu de dessus + coupes) depuis modele.py.
#
#   python3 3d/salon/plan.py            (just salon)
#   python3 3d/salon/plan.py --figer    (just salon-figer : fige la version courante)
#
# Le plan et les coupes sont des projections des volumes du modèle : rien n'est dessiné à la main.

import math
import os
import re
import sys
from html import escape

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import modele as M  # noqa: E402

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
OUT = os.path.join(ROOT, "salon-v4.html")
CLE = "salon-v4"          # préfixe des préférences mémorisées (localStorage)

COUPE_A = 70     # x, regard vers l'ouest : enfilade et étagères
COUPE_B = 480    # x, regard vers l'est : desserte et baie
COUPE_C = M.TABLE["cy"]  # y, regard vers le nord : à travers la table


def f(v):
    return f"{round(v, 1):g}"


def rect(x0, y0, x1, y1, cls, rx=0):
    r = f' rx="{f(rx)}"' if rx else ""
    return f'<rect class="{cls}" x="{f(x0)}" y="{f(y0)}" width="{f(x1 - x0)}" height="{f(y1 - y0)}"{r}/>'


def text(x, y, s, cls="lbl", anchor="middle", extra=""):
    return f'<text class="{cls}" x="{f(x)}" y="{f(y)}" text-anchor="{anchor}"{extra}>{escape(s)}</text>'


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
        text(x - 2.5, ym, label, "dimt", extra=f' transform="rotate(-90 {f(x - 2.5)} {f(ym)})"'),
    ])


def degage(a, b, label=None, dt=(0, 0)):
    """Dégagement libre entre deux points (tireté rouge), valeur au milieu."""
    d = math.dist(a, b)
    xm, ym = (a[0] + b[0]) / 2 + dt[0], (a[1] + b[1]) / 2 + dt[1]
    return (f'<line class="pass" x1="{f(a[0])}" y1="{f(a[1])}" x2="{f(b[0])}" y2="{f(b[1])}"/>'
            + "".join(f'<circle class="passm" cx="{f(p[0])}" cy="{f(p[1])}" r="1.3"/>' for p in (a, b))
            + text(xm, ym, label or f"{d:.0f}", "passt"))


def cfg_cls(b):
    return f" c{b.config}" if b.config else ""


# ------------------------------------------------------------------ plan vu de dessus
PLAN_CLS = {"mur": "w", "linteau": None, "cadre": "cadre", "baie": "win", "caisson": "cab", "facade": "fac",
            "pied": None, "etagere": "upper", "canape": "sofa", "table": "tbl", "chaise": None, "desserte": "cab",
            "vinyles": None, "platine": "dark", "lampe": "lampe"}


def chaise_plan(x, y, a, cls):
    """Chaise vue de dessus : assise 45 × 45 tournée, dossier côté extérieur."""
    h = M.CHAISE["l"] / 2
    return (f'<g class="{cls}" transform="translate({f(x)} {f(y)}) rotate({f(a)})">'
            f'<rect class="stool" x="{f(-h)}" y="{f(-h)}" width="{f(2 * h)}" height="{f(2 * h)}" rx="4"/>'
            f'<rect class="stoold" x="{f(h - 5)}" y="{f(-h + 1)}" width="4" height="{f(2 * h - 2)}" rx="1.5"/></g>')


def volumes_plan():
    o = []
    for b in sorted(M.ENVELOPPE + M.MEUBLES, key=lambda b: b.z1):
        cls = PLAN_CLS[b.role]
        if not cls:
            continue
        cls += cfg_cls(b)
        if isinstance(b, M.Cyl):
            o.append(f'<circle class="{cls}" cx="{f(b.cx)}" cy="{f(b.cy)}" r="{f(b.r)}"/>')
        elif b.role == "table":
            o.append(rect(b.x0, b.y0, b.x1, b.y1, cls, M.TABLE["r"]))
        else:
            o.append(rect(b.x0, b.y0, b.x1, b.y1, cls))
    return o


def plan_svg():
    e, c, d, t, dg = M.ENFILADE, M.CANAPE, M.DESSERTE, M.TABLE, M.DEGAGEMENTS
    pa, ba = M.PASSAGE, M.BAIE
    o = []
    # pièces voisines
    o.append(rect(-130, -12, -10, pa["y0"] - pa["cadre"], "room"))
    o.append(text(-70, 70, "Cellier", "lbl muted"))
    o.append(text(-70, 190, "WC", "lbl muted"))
    o.append(rect(-130, pa["y0"] - pa["cadre"], -10, M.P + 12, "room"))
    o.append(text(-70, 315, "Couloir", "lbl muted"))
    o.append(rect(556, -12, 660, M.P + 12, "room"))
    o.append(text(608, 330, "Pièce 1", "lbl muted"))
    o.append(rect(-10, M.P + 12, 556, M.P + 52, "room"))
    o.append(text(272, M.P + 38, "Chambre", "lbl muted"))
    sol = [(0, 0), (M.DECROCHE["x0"], 0), (M.DECROCHE["x0"], M.DECROCHE["y"]), (M.L, M.DECROCHE["y"]),
           (M.L, M.P), (0, M.P)]
    o.append(f'<polygon class="floorbg" points="{" ".join(f"{f(x)},{f(y)}" for x, y in sol)}"/>')
    o += volumes_plan()
    # baie coulissante : deux vantaux dans l'épaisseur du mur
    o.append(f'<line class="glass" x1="548" y1="{ba["y0"]}" x2="548" y2="{ba["milieu"] + 3}"/>')
    o.append(f'<line class="glass" x1="552" y1="{ba["milieu"] - 3}" x2="552" y2="{ba["y1"]}"/>')
    o.append(text(568, (ba["y0"] + ba["y1"]) / 2, f'baie {ba["y1"] - ba["y0"]}', "lbls muted",
                  extra=f' transform="rotate(-90 568 {(ba["y0"] + ba["y1"]) / 2})"'))
    # passage sans porte
    o.append(f'<line class="seuil" x1="-10" y1="{pa["y0"]}" x2="-10" y2="{pa["y1"]}"/>')
    o.append(f'<line class="seuil" x1="0" y1="{pa["y0"]}" x2="0" y2="{pa["y1"]}"/>')
    o.append(text(14, (pa["y0"] + pa["y1"]) / 2, f'passage {pa["y1"] - pa["y0"]}', "lblx muted",
                  extra=f' transform="rotate(-90 14 {(pa["y0"] + pa["y1"]) / 2})"'))
    # enfilade : séparation des modules et des portes
    for y0, y1 in e["modules"][1:]:
        o.append(f'<line class="sep" x1="0" y1="{f(y0)}" x2="{f(e["p"])}" y2="{f(y0)}"/>')
    # chaises
    for cfg, lst in M.CHAISES.items():
        for x, y, a in lst:
            o.append(chaise_plan(x, y, a, f"c{cfg}"))
    # canapé : dossier et accoudoirs
    o.append(rect(c["x0"] + c["accoudoir"], 0, c["x1"] - c["accoudoir"], c["dossier"], "sofac"))
    for x0 in (c["x0"], c["x1"] - c["accoudoir"]):
        o.append(rect(x0, 0, x0 + c["accoudoir"], c["p"], "sofac"))
    # étiquettes
    ym = (e["y0"] + e["y1"]) / 2
    o.append(text(22, ym, f'① Enfilade {f(e["y1"] - e["y0"])} × {e["p"]} · h {e["z1"]}', "lbls",
                  extra=f' transform="rotate(-90 22 {f(ym)})"'))
    o.append(text(36, ym, "② 4 étagères suspendues au-dessus (tireté)", "lblx",
                  extra=f' transform="rotate(-90 36 {f(ym)})"'))
    for k, (y0, y1) in enumerate(e["modules"]):
        o.append(text(9, (y0 + y1) / 2, f"M{k + 1}", "lblx muted", extra=f' transform="rotate(-90 9 {f((y0 + y1) / 2)})"'))
    xc = (c["x0"] + c["x1"]) / 2
    o.append(text(xc, 52, f'③ Canapé {c["l"]} × {c["p"]}', "lbls"))
    o.append(text((d["x0"] + d["x1"]) / 2 - 2, d["y1"] + 9, "④ Desserte", "lbls"))
    o.append(text((d["x0"] + d["x1"]) / 2 - 2, d["y1"] + 16, "platine vinyle", "lblx"))
    o.append(f'<g class="c4">{text(t["cx"], t["cy"] - 2, "⑤ Table Ø " + f(t["d"]), "lbls")}'
             f'{text(t["cx"], t["cy"] + 6, "4 couverts", "lblx")}</g>')
    o.append(f'<g class="c12">{text(t["cx"], t["cy"] - 2, "⑤ Table " + f(t["long"]) + " × " + f(t["d"]), "lbls")}'
             f'{text(t["cx"], t["cy"] + 6, str(t["allonges"]) + " allonges de " + f(t["allonge"]) + " · 12 couverts", "lblx")}</g>')
    # cotes
    o.append(cote_h(0, M.L, -30))
    o.append(cote_v(0, M.P, -22))
    o.append(cote_h(c["x0"], c["x1"], -18, f'{c["l"]}'))
    o.append(cote_h(e["p"], c["x0"], -18, f'{M.ALLEE_ENFILADE}'))
    o.append(cote_h(0, e["p"], -18, f'{e["p"]}'))
    o.append(cote_v(e["y0"], e["y1"], -14 + 0, f'{f(e["y1"] - e["y0"])} utiles'))
    o.append(cote_v(d["y0"], d["y1"], d["x0"] - 8, f'{d["y1"] - d["y0"]}'))
    # dégagements
    xr = t["cx"] + 22
    o.append(f'<g class="c4">'
             + degage((xr, c["p"]), (xr, t["cy"] - t["r"]), dt=(5, 1))
             + degage((xr, t["cy"] + t["r"]), (xr, M.P), dt=(5, 1))
             + "</g>")
    xo, xe = t["cx"] - t["r"] - t["s"], t["cx"] + t["r"] + t["s"]
    o.append(f'<g class="c12">'
             + degage((e["p"], t["cy"]), (xo, t["cy"]), dt=(0, -2))
             + degage((xe, t["cy"]), (M.L, t["cy"]), dt=(0, -2))
             + degage((266, c["p"]), (266, t["cy"] - t["r"]), dt=(0, -12))
             + degage((266, t["cy"] + t["r"]), (266, M.P), dt=(0, 14))
             + "</g>")
    # traits de coupe
    for x, lab, sens in ((COUPE_A, "A", -1), (COUPE_B, "B", 1)):
        o.append(f'<line class="sec" x1="{x}" y1="-6" x2="{x}" y2="{M.P + 6}"/>')
        for y in (-10, M.P + 16):
            o.append(text(x + 8 * sens, y, lab, "sect"))
    o.append(f'<line class="sec" x1="-6" y1="{COUPE_C}" x2="{M.L + 6}" y2="{COUPE_C}"/>')
    o.append(text(-4, COUPE_C - 5, "C", "sect", "end"))
    o.append(text(M.L + 4, COUPE_C - 5, "C", "sect", "start"))
    return (f'<svg viewBox="-150 -50 820 470" role="img" aria-label="Plan du salon">{"".join(o)}</svg>')


# ------------------------------------------------------------------ coupes
COUPE_CLS = {"mur": ("bgwall", "w"), "linteau": ("wallv", "w"), "cadre": ("cadre", "cadre"), "baie": ("vitre", "vitrec"),
             "caisson": ("cab", "cab"), "facade": ("fac", "fac"), "pied": ("dark", "dark"),
             "etagere": ("shelf", "shelfc"), "canape": ("sofa", "sofa"), "table": ("tbl", "tbl"),
             "chaise": ("stool", "stool"), "desserte": ("cab", "cab"), "vinyles": ("vinyl", "vinyl"),
             "platine": ("dark", "dark"), "lampe": ("lampe", "lampe")}

# (axe coupé, sens du regard, miroir de l'axe horizontal)
REGARDS = {"nord": ("y", -1, False), "sud": ("y", 1, True), "est": ("x", 1, False), "ouest": ("x", -1, True)}
VERS = {"nord": "le nord", "sud": "le sud", "est": "l'est", "ouest": "l'ouest"}


def uv(b, axe):
    return (b.x0, b.x1, b.y0, b.y1) if axe == "y" else (b.y0, b.y1, b.x0, b.x1)


def visibles(cut, regard, umin, umax, cfg):
    axe, sens, _ = REGARDS[regard]
    r = []
    for b in M.ENVELOPPE + M.MEUBLES:
        if b.config not in ("", cfg):
            continue
        u0, u1, d0, d1 = uv(b, axe)
        if (d1 > cut if sens > 0 else d0 < cut) and u1 > umin and u0 < umax:
            r.append(b)
    return r


def coupe_svg(cut, regard, umin, umax, cfg, hauteurs, extra=None):
    axe, sens, miroir = REGARDS[regard]
    X = (lambda u: umin + umax - u) if miroir else (lambda u: u)
    vus = visibles(cut, regard, umin, umax, cfg)
    vus.sort(key=lambda b: (uv(b, axe)[2] < cut < uv(b, axe)[3], -uv(b, axe)[2] if sens > 0 else uv(b, axe)[3]))
    o, etiq = [], {}
    for b in vus:
        u0, u1, d0, d1 = uv(b, axe)
        coupe = d0 < cut < d1
        u, v = sorted((X(max(u0, umin)), X(min(u1, umax))))
        o.append(rect(u, -b.z1, v, -b.z0, COUPE_CLS[b.role][1 if coupe else 0]))
        xm = (u + v) / 2
        if b.role == "baie" and coupe:
            o.append(text(xm + 7, -110, "baie", "lblx muted", extra=f' transform="rotate(-90 {f(xm + 7)} -110)"'))
        if b.etiq and v - u > 8:
            etiq[(round(xm), round(-(b.z0 + b.z1) / 2))] = text(xm, -(b.z0 + b.z1) / 2 + 3, b.etiq, "lblb")
        if b.contenu and v - u > 20:
            zc = -(b.z1 - 8) if b.role == "facade" else -(b.z0 + b.z1) / 2 + 1
            etiq[(round(xm), round(zc))] = text(xm, zc, b.contenu, "lblc")
    o += etiq.values()
    if extra:
        o += extra(X)
    o.append(f'<line class="floorl" x1="{f(umin)}" y1="0" x2="{f(umax)}" y2="0"/>')
    o.append(f'<line class="ceil" x1="{f(umin)}" y1="{-M.H}" x2="{f(umax)}" y2="{-M.H}"/>')
    zs = [0] + hauteurs + [M.H]
    for z0, z1 in zip(zs, zs[1:]):
        o.append(cote_v(-z0, -z1, umin - 12))
    o.append(cote_v(0, -M.H, umin - 28))
    return (f'<svg viewBox="{f(umin - 44)} -275 {f(umax - umin + 70)} 315" role="img" '
            f'aria-label="Coupe à {axe} {f(cut)}, regard vers {VERS[regard]}">{"".join(o)}</svg>')


def coupe_configs(*args, **kw):
    """Une coupe par configuration de la table, ou une seule si la table et les chaises n'y paraissent pas."""
    cut, regard, umin, umax = args[:4]
    v4, v12 = (visibles(cut, regard, umin, umax, c) for c in ("4", "12"))
    if [b.nom for b in v4 if b.config] == [] and [b.nom for b in v12 if b.config] == []:
        return coupe_svg(cut, regard, umin, umax, "4", *args[4:], **kw)
    return "".join(f'<div class="c{c}">{coupe_svg(cut, regard, umin, umax, c, *args[4:], **kw)}</div>'
                   for c in ("4", "12"))


def coupe_a():
    e, et = M.ENFILADE, M.ETAGERES

    def cotes(X):
        u0, u1 = sorted((X(e["y0"]), X(e["y1"])))
        p0, p1 = sorted((X(M.PASSAGE["y0"]), X(M.PASSAGE["y1"])))
        r = [cote_h(u0, u1, 18, f'enfilade {f(e["y1"] - e["y0"])}'),
             cote_h(p0, p1, 18, f'passage {M.PASSAGE["y1"] - M.PASSAGE["y0"]}')]
        for y0, y1 in e["modules"]:
            a, b = sorted((X(y0), X(y1)))
            r.append(cote_h(a, b, 9, f(y1 - y0)))
        xm = (u0 + u1) / 2
        r.append(text(xm, -(et["zs"][-1] + 10), "fixation des étagères à étudier (R&D)", "lblc"))
        return r

    return coupe_configs(COUPE_A, "ouest", -20, M.P + 20, [e["pieds"], e["z1"]] + et["zs"], extra=cotes)


def coupe_b():
    d, b = M.DESSERTE, M.BAIE

    def cotes(X):
        u0, u1 = sorted((X(d["y0"]), X(d["y1"])))
        b0, b1 = sorted((X(b["y0"]), X(b["y1"])))
        m = X(b["milieu"])
        return [cote_h(u0, u1, 18, f'desserte {d["y1"] - d["y0"]}'), cote_h(b0, b1, -b["h"] - 6, f'baie {b["y1"] - b["y0"]}'),
                f'<line class="seuil" x1="{f(m)}" y1="0" x2="{f(m)}" y2="{-b["h"]}"/>',
                text((b0 + m) / 2 if X(b["y0"]) < m else (m + b1) / 2, -b["h"] + 10, "vantail nord", "lblx muted"),
                text((m + b1) / 2 if X(b["y0"]) < m else (b0 + m) / 2, -b["h"] + 10, "vantail sud", "lblx muted")]

    return coupe_configs(COUPE_B, "est", -20, M.P + 20, [d["niveaux"][1], d["z1"], d["z1"] + 14, b["h"]], extra=cotes)


def coupe_c():
    e, c, t = M.ENFILADE, M.CANAPE, M.TABLE

    def cotes(X):
        return [cote_h(0, e["p"], 18), cote_h(c["x0"], c["x1"], 18, f'canapé {c["l"]}'),
                cote_h(M.DESSERTE["x0"], M.L, 18)]

    return coupe_configs(COUPE_C, "nord", -20, M.L + 20,
                         [c["assise"], t["z1"], e["z1"], M.SUSPENSION["z0"]], extra=cotes)


# ------------------------------------------------------------------ page
CSS = """
:root{
  --paper:#F7F8F6; --ink:#1D2A33; --muted:#5E6B73; --line:#C9D0D4; --wood:#B07A45;
  --water:#2F7FB5; --tri:#C8412C; --panel:#FFFFFF; --cab:#ECE6DA; --tall:#D8CFBD; --sofa:#C9BFAE;
  --glass:#CFE4F2; color-scheme:light;
}
@media (prefers-color-scheme: dark){
  :root:not([data-theme="light"]){
    --paper:#141A1F; --ink:#E4EAED; --muted:#9AA7AE; --line:#34414A; --wood:#C9925A;
    --water:#5AA8DE; --tri:#E8664F; --panel:#1B2329; --cab:#2A3338; --tall:#394449; --sofa:#4A4640;
    --glass:#1F3A4E; color-scheme:dark;
  }
}
:root[data-theme="dark"]{
  --paper:#141A1F; --ink:#E4EAED; --muted:#9AA7AE; --line:#34414A; --wood:#C9925A;
  --water:#5AA8DE; --tri:#E8664F; --panel:#1B2329; --cab:#2A3338; --tall:#394449; --sofa:#4A4640;
  --glass:#1F3A4E; color-scheme:dark;
}
*{box-sizing:border-box}
html,body{margin:0}
body{background:var(--paper);color:var(--ink);font-family:Archivo,system-ui,-apple-system,"Segoe UI",Roboto,sans-serif;line-height:1.55;font-size:16px}
.wrap{max-width:1120px;margin:0 auto;padding:28px 16px 64px}
.kicker{font-family:"JetBrains Mono",ui-monospace,Menlo,monospace;font-size:12px;letter-spacing:.08em;text-transform:uppercase;color:var(--muted)}
h1{font-size:clamp(28px,5vw,44px);line-height:1.08;margin:6px 0 12px;font-weight:800;letter-spacing:-.01em}
h2{font-size:22px;margin:44px 0 10px;font-weight:700}
h3{font-size:15px;margin:18px 0 6px}
.pitch{font-size:18px;max-width:780px}
.fig{background:var(--panel);border:1px solid var(--line);border-radius:12px;padding:12px;margin:14px 0}
.scroll svg{display:block;width:100%;height:auto}
.cap{font-size:13px;color:var(--muted);margin:8px 4px 2px}
.note{font-size:13px;color:var(--muted)}
table{border-collapse:collapse;width:100%;font-size:14px}
th,td{text-align:left;padding:7px 8px;border-bottom:1px solid var(--line);vertical-align:top}
td.num,th.num{text-align:right;font-family:"JetBrains Mono",ui-monospace,monospace;white-space:nowrap}
.mono{font-family:"JetBrains Mono",ui-monospace,monospace;white-space:nowrap}
ul.pistes{padding-left:20px;max-width:860px}ul.pistes li{margin:6px 0}
svg text{font-family:Archivo,system-ui,sans-serif;fill:var(--ink)}
.room{fill:var(--line);fill-opacity:.25}
.floorbg{fill:var(--wood);fill-opacity:.1}
.w{fill:var(--ink)}
.bgwall{fill:var(--line);fill-opacity:.35}
.wallv{fill:#D5DADD;stroke:var(--muted);stroke-width:.5}
.cadre{fill:var(--panel);stroke:var(--ink);stroke-width:.6}
.win{fill:var(--glass);stroke:var(--ink);stroke-width:.7}
.glass{stroke:var(--water);stroke-width:1.4}
.vitre{fill:var(--glass);fill-opacity:.5;stroke:var(--water);stroke-width:.8}
.vitrec{fill:var(--glass);stroke:var(--water);stroke-width:.8}
.cab{fill:var(--cab);stroke:var(--ink);stroke-width:.7}
.fac{fill:var(--tall);stroke:var(--ink);stroke-width:.6}
.sep{stroke:var(--ink);stroke-width:.7}
.dark{fill:var(--ink)}
.shelf{fill:var(--wood);fill-opacity:.3;stroke:var(--wood);stroke-width:.6}
.shelfc{fill:var(--wood);stroke:var(--ink);stroke-width:.6}
.upper{fill:none;stroke:var(--ink);stroke-width:.8;stroke-dasharray:3 2}
.sofa{fill:var(--sofa);stroke:var(--ink);stroke-width:.8}
.sofac{fill:var(--sofa);stroke:var(--ink);stroke-width:.6;filter:brightness(.93)}
.tbl{fill:var(--wood);fill-opacity:.5;stroke:var(--ink);stroke-width:.9}
.stool{fill:var(--wood);fill-opacity:.28;stroke:var(--ink);stroke-width:.7}
.stoold{fill:var(--wood);fill-opacity:.6;stroke:var(--ink);stroke-width:.5}
.vinyl{fill:#2B2B2E;fill-opacity:.75;stroke:var(--ink);stroke-width:.4}
.lampe{fill:#F2C94C;fill-opacity:.35;stroke:#B8860B;stroke-width:.7;stroke-dasharray:3 2}
.seuil{stroke:var(--muted);stroke-width:.7;stroke-dasharray:3 2}
.pass{stroke:var(--tri);stroke-width:.8;stroke-dasharray:3 2}.passm{fill:var(--tri)}
.passt{fill:var(--tri);font-family:"JetBrains Mono",ui-monospace,monospace !important;font-size:7px;font-weight:600;text-anchor:middle}
.dim{stroke:var(--muted);stroke-width:.6;fill:none}
.dimt{fill:var(--muted);font-family:"JetBrains Mono",ui-monospace,monospace !important;font-size:8px}
.lbl{font-size:7.5px}.lbls{font-size:6.5px}.lblx{font-size:5px}.lblb{font-size:9px;font-weight:700}
.lblc{font-size:3.6px;font-style:italic}
.muted{fill:var(--muted)}
.sec{stroke:var(--tri);stroke-opacity:.3;stroke-width:.9;stroke-dasharray:10 3 2 3;fill:none}
.sect{fill:var(--tri);fill-opacity:.55;font-weight:800;font-size:11px}
.floorl{stroke:var(--ink);stroke-width:2}
.ceil{stroke:var(--muted);stroke-width:1;stroke-dasharray:6 4}
body.t12 .c4,body:not(.t12) .c12{display:none}
body:not(.explications) .cap{display:none}
body:not(.changements) section[id^="changements"]{display:none}
.tog{display:flex;flex-wrap:wrap;align-items:center;gap:6px;margin:0 0 10px;font-family:"JetBrains Mono",ui-monospace,monospace;font-size:12px}
.tog span{color:var(--muted);text-transform:uppercase;letter-spacing:.08em;margin-right:4px}
.tog button,.vbar button{font:inherit;color:var(--ink);background:var(--panel);border:1px solid var(--line);border-radius:6px;padding:4px 10px;cursor:pointer}
.tog button[aria-pressed="true"],.vbar button[aria-pressed="true"]{background:var(--ink);color:var(--paper);border-color:var(--ink)}
.vbar{position:sticky;top:0;z-index:5;display:flex;flex-wrap:wrap;align-items:center;gap:6px;padding:8px 16px;background:var(--paper);border-bottom:1px solid var(--line);font-family:"JetBrains Mono",ui-monospace,monospace;font-size:12px}
.vbar .back{color:var(--ink);text-decoration:none;font-weight:600;margin-right:14px}
.vbar .back:hover{text-decoration:underline}
.vbar span{color:var(--muted);text-transform:uppercase;letter-spacing:.08em;margin-right:4px}
.vbar .expl{margin-left:auto}
@media (max-width:480px){ body{font-size:15px} }
"""


def tog_table():
    return ('<div class="tog"><span>Table</span>'
            '<button type="button" data-t="4" aria-pressed="true">4 couverts</button>'
            '<button type="button" data-t="12" aria-pressed="false">12 couverts</button></div>')


def table_rangement():
    e, d = M.ENFILADE, M.DESSERTE
    lignes = [
        ("① Enfilade", f'{f(e["y1"] - e["y0"])} × {e["p"]} × {e["z1"]}, 3 modules de {f(e["modules"][0][1] - e["modules"][0][0])}',
         f"≈ {round(M.VOLUME_ENFILADE, -1):.0f} L"),
        ("② Étagères suspendues", f'{len(M.ETAGERES["zs"])} × {f(e["y1"] - e["y0"])}, P{M.ETAGERES["p"]}',
         f'{M.METRES_ETAGERES:.1f} m · ≈ {M.METRES_ETAGERES * M.CHARGE_LIVRES:.0f} kg pleines'),
        ("④ Desserte", f'{d["y1"] - d["y0"]} × {d["x1"] - d["x0"]} × {d["z1"]}, 2 niveaux pour vinyles',
         f"≈ {round(M.VINYLES, -1):.0f} disques"),
    ]
    corps = "".join(f'<tr><td>{a}</td><td>{b}</td><td class="num">{c}</td></tr>' for a, b, c in lignes)
    return f'<table><thead><tr><th>Meuble</th><th>Dimensions</th><th class="num">Capacité</th></tr></thead><tbody>{corps}</tbody></table>'


def contenu():
    e, et, c, d, t, dg = M.ENFILADE, M.ETAGERES, M.CANAPE, M.DESSERTE, M.TABLE, M.DEGAGEMENTS
    lignes = "".join(f'<tr><td class="mono">{v}</td><td class="mono">{dt}</td><td>{escape(x)}</td></tr>'
                     for v, dt, x in M.CHANGEMENTS)
    modules = " ; ".join(f'M{k + 1} {escape(ct)}' for k, (_, ct) in enumerate(M._MODULES))
    return f"""<div class="kicker">Salon · {M.VERSION}</div>
<h1>Salon V4</h1>
<p class="pitch">La bibliothèque reste au mur ouest : une enfilade basse avec des étagères suspendues au-dessus, le canapé dans son angle. Devant la baie, une desserte pour la platine vinyle ; au milieu, une table ronde qui s'ouvre pour recevoir douze personnes.</p>

<h2>Plan</h2>
<div class="fig">{tog_table()}<div class="scroll">{plan_svg()}</div>
<p class="cap">Échelle : 1 unité = 1 cm ; ouest à gauche, nord en haut. <b>① Enfilade</b> contre le mur ouest, du coin nord au cadre du passage ({f(e["y1"] - e["y0"])} utiles), profondeur {e["p"]} (caisson {e["p"] - e["facade"]} + façades {e["facade"]}), dessus à {e["z1"]}, sur pieds de {e["pieds"]} ; trois modules de {f(e["modules"][0][1] - e["modules"][0][0])} : {modules}. <b>② Étagères suspendues</b> (tireté) : {len(et["zs"])} tablettes {f(et["y1"] - et["y0"])} × {et["p"]} au-dessus de l'enfilade, sur toute sa longueur ; fixation à étudier (voir plus bas). <b>③ Canapé</b> {c["l"]} × {c["p"]} dos au mur nord, tourné vers le sud, à {M.ALLEE_ENFILADE} de l'enfilade : l'allée laisse ouvrir les portes du module nord. <b>④ Desserte</b> {d["y1"] - d["y0"]} × {d["x1"] - d["x0"]} contre le vantail nord de la baie (y {d["y0"]} → {d["y1"]}), platine sur le dessus, vinyles sur deux niveaux ; le vantail sud reste le passage quand la baie est ouverte. <b>⑤ Table</b> ronde Ø {f(t["d"])} centrée en ({t["cx"]}, {t["cy"]}), à 4 pieds, avec {t["allonges"]} allonges de {t["allonge"]} : {f(t["long"])} × {f(t["d"])} ouverte, est-ouest, seule direction où 12 couverts tiennent (nord-sud, il faudrait {f(t["long"] + 2 * 70)} pour {M.P}). Au quotidien, 4 chaises en biais ; à 12, 3 chaises par grand côté et 3 par bout (pas de 68). <b>Dégagements</b> (rouge) : {f(dg["canape_table"])} entre le canapé et la table, {f(dg["table_sud"])} au sud ; table ouverte, {f(dg["bout_ouest"])} entre son bout ouest et l'enfilade, {f(dg["bout_est"])} à l'est. À 12, les chaises du côté nord touchent presque le canapé et celles du sud le mur : on s'assoit, on ne circule plus derrière. Suspension (tireté jaune) au-dessus du centre de la table.</p></div>

<h2>Coupe A-A · mur ouest</h2>
<div class="fig"><div class="scroll">{coupe_a()}</div>
<p class="cap">Coupe à x {COUPE_A}, regard vers l'ouest : le sud est à gauche. Enfilade sur pieds de {e["pieds"]}, dessus à {e["z1"]} ; tablettes de {et["ep"]} avec le dessus à {", ".join(str(z) for z in et["zs"])} (un premier vide de {et["zs"][0] - et["ep"] - e["z1"]} au-dessus de l'enfilade pour poser lampes et objets, puis {et["zs"][1] - et["zs"][0] - et["ep"]} de hauteur libre entre tablettes : les livres courants font 18 à 30). À gauche, le passage vers le couloir ({M.PASSAGE["y1"] - M.PASSAGE["y0"]} × {M.PASSAGE["h"]}) avec son cadre.</p></div>

<h2>Coupe B-B · baie</h2>
<div class="fig"><div class="scroll">{coupe_b()}</div>
<p class="cap">Coupe à x {COUPE_B}, regard vers l'est : le nord est à gauche. Desserte h {d["z1"]} : deux niveaux de vinyles debout (pochettes 31,5) et la platine dessus, dont le plateau arrive vers {d["z1"] + 10}, à hauteur de main debout. Elle masque le bas du vantail nord de la baie (tireté au milieu = jonction des vantaux, à confirmer sur place).</p></div>

<h2>Coupe C-C · à travers la table</h2>
<div class="fig">{tog_table()}<div class="scroll">{coupe_c()}</div>
<p class="cap">Coupe à y {COUPE_C} (centre de la table), regard vers le nord : l'ouest est à gauche. Enfilade et étagères coupées à gauche, canapé contre le mur nord au fond, table coupée au milieu (plateau à {t["z1"]}), desserte et platine au fond à droite, baie coupée. Suspension Ø {M.SUSPENSION["d"]}, bas à {M.SUSPENSION["z0"]}, soit {M.SUSPENSION["z0"] - t["z1"]} au-dessus du plateau.</p></div>

<h2>Rangements</h2>
<div class="fig">{table_rangement()}
<p class="cap">Volume utile de l'enfilade : intérieur des caissons, panneaux de {e["ep"]} déduits. Étagères : {M.CHARGE_LIVRES} kg par mètre pleine de livres (ordre de grandeur), d'où la question de la fixation. Vinyles : environ 3,5 mm par disque sous pochette, rangées de 31,5 de profondeur.</p></div>

<h2>Étagères suspendues : fixation à étudier</h2>
<p>Charge à reprendre : jusqu'à {M.METRES_ETAGERES * M.CHARGE_LIVRES:.0f} kg sur {M.METRES_ETAGERES:.1f} m de tablettes, au-dessus d'un meuble qu'on ne veut pas faire porter. Le mur ouest est la cloison du cellier et du WC (nature à confirmer). Pistes à comparer :</p>
<ul class="pistes">
<li><b>Tiges ou câbles depuis le plafond</b>, tablettes accrochées dessous (vraie étagère suspendue, rien dans la cloison) : dépend du plafond (béton, hourdis, faux plafond ?) ; tiges filetées Ø 8–10 sous fourreau, ou câbles inox avec serre-câbles réglables ; un appui ponctuel au mur pour empêcher le balancement.</li>
<li><b>Montants plafond–sol</b> en tension ou vissés au plafond, derrière l'enfilade (comme la String ou la Moebe de la page bibliothèque), tablettes sur consoles : rien de porté par la cloison.</li>
<li><b>Fixations invisibles</b> (tiges dans la cloison, tablettes percées) : le plus « flottant », mais exige un mur plein ou un renfort dans la cloison ; portée 258 trop longue d'un seul tenant.</li>
<li><b>Crémaillères et consoles</b> : la solution connue (voir <a href="salon-bibliotheque-fixation.html">page Fixations</a>), à garder comme repli.</li>
</ul>
<p class="note">À relever avant de choisir : nature du plafond et de la cloison (sondage, carottage léger), position des réseaux électriques dans le mur ouest, flèche admissible d'une tablette de {et["ep"]} sur la portée retenue.</p>

<h2>Points à vérifier</h2>
<ul class="pistes">
<li><b>Baie</b> : quel vantail coulisse, et devant lequel on passe ; la desserte suppose qu'on sort par le vantail sud.</li>
<li><b>Prises</b> : une prise près de la desserte (platine, ampli ou enceintes actives) ; une près du canapé pour une lampe.</li>
<li><b>Chaises</b> : 4 au quotidien, 8 d'appoint pour recevoir à 12 (pliantes ou empilables) : où les ranger.</li>
<li><b>Canapé</b> : dessiné en {c["l"]} × {c["p"]}. Un SÖDERHAMN 3 places (198 × 99) prendrait 9 cm de plus vers la table.</li>
<li><b>Table</b> : Ø {f(t["d"])} à {t["allonges"]} allonges ({f(t["long"])} ouverte) ; à défaut, Ø 120 → 270 donne 10 couverts confortables, 12 serrés.</li>
</ul>

<p class="note">Repère : x vers l'est depuis le mur ouest, y vers le sud depuis le mur nord, z depuis le sol fini, en cm. Source : <span class="mono">3d/salon/modele.py</span> ; page : <span class="mono">3d/salon/plan.py</span> (<span class="mono">just salon</span>). Rendus 3D sur demande.</p>

<section id="changements">
<h2>Changements</h2>
<table><thead><tr><th>Version</th><th>Date</th><th>Changements</th></tr></thead>
<tbody>{lignes}</tbody></table>
</section>
"""


def page(figees, racine=""):
    """figees : [(version, contenu)] ; le bouton de version bascule tout le contenu."""
    boutons = "".join(f'<button type="button" data-v="{v}">{v} figée</button>' for v, _ in figees)
    blocs = "".join(f'<div class="ver" data-v="{v}" hidden>{c}</div>' for v, c in figees)
    versions = (f'<span>Version</span><button type="button" data-v="courante" aria-pressed="true">'
                f'{M.VERSION} en cours</button>{boutons}')
    barre = (f'<div class="vbar"><a class="back" href="{racine}index.html">← Plans</a>{versions}'
             f'<button type="button" class="expl" aria-pressed="false">Explications</button>'
             f'<button type="button" class="chg" aria-pressed="false">Changements</button></div>')
    return f"""<!doctype html>
<html lang="fr">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Salon V4</title>
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
  function garde(k, v) {{ try {{ localStorage.setItem("{CLE}-" + k, v); }} catch (e) {{}} }}
  function lit(k) {{ try {{ return localStorage.getItem("{CLE}-" + k); }} catch (e) {{ return null; }} }}
  var bs = document.querySelectorAll(".vbar button[data-v]"), vs = document.querySelectorAll(".ver");
  function montre(v) {{
    if (!document.querySelector('.ver[data-v="' + v + '"]')) v = "courante";
    vs.forEach(function (d) {{ d.hidden = d.dataset.v !== v; }});
    bs.forEach(function (b) {{ b.setAttribute("aria-pressed", b.dataset.v === v); }});
    garde("version", v);
  }}
  bs.forEach(function (b) {{ b.addEventListener("click", function () {{ montre(b.dataset.v); }}); }});
  function table(t) {{
    document.body.classList.toggle("t12", t === "12");
    document.querySelectorAll(".tog button[data-t]").forEach(function (b) {{ b.setAttribute("aria-pressed", b.dataset.t === t); }});
    garde("table", t);
  }}
  document.querySelectorAll(".tog button[data-t]").forEach(function (b) {{
    b.addEventListener("click", function () {{ table(b.dataset.t); }});
  }});
  table(lit("table") === "12" ? "12" : "4");
  function bascule(sel, cls) {{
    var b = document.querySelector(sel);
    function pose(on) {{ document.body.classList.toggle(cls, on); b.setAttribute("aria-pressed", on); garde(cls, on ? "1" : ""); }}
    b.addEventListener("click", function () {{ pose(b.getAttribute("aria-pressed") !== "true"); }});
    pose(lit(cls) === "1");
  }}
  bascule(".vbar .expl", "explications");
  bascule(".vbar .chg", "changements");
  var v0 = lit("version") || "courante";
  if (location.hash && document.querySelector('.ver[data-v="' + decodeURIComponent(location.hash.slice(1)) + '"]'))
    v0 = decodeURIComponent(location.hash.slice(1));
  montre(v0);
}})();
</script>
</body>
</html>
"""


FIGEES = os.path.join(os.path.dirname(os.path.abspath(__file__)), "figees")


def figer():
    """Fige la version courante : contenu dans figees/<version>.html et page autonome archive/salon-<version>.html."""
    os.makedirs(FIGEES, exist_ok=True)
    v = M.VERSION
    c = contenu()
    for ident in set(re.findall(r'id="([^"]+)"', c)):
        c = c.replace(f'id="{ident}"', f'id="{ident}-{v}"').replace(f"#{ident}\"", f"#{ident}-{v}\"")
    with open(os.path.join(FIGEES, f"{v}.html"), "w", encoding="utf-8") as fh:
        fh.write(c)
    with open(os.path.join(ROOT, "archive", f"salon-{v.lower()}.html"), "w", encoding="utf-8") as fh:
        fh.write(page([], "../").replace('href="salon-bibliotheque', 'href="../salon-bibliotheque'))
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
