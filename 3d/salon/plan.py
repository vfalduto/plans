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
COUPE_D = 300    # y, regard vers le sud : meuble bas, écran, clim


def virg(v, n=1):
    return f"{v:.{n}f}".replace(".", ",")


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
    return (f" c{b.config}" if b.config else "") + (" dz" if b.deco else "") + (f" a{b.assise}" if b.assise else "")


# ------------------------------------------------------------------ plan vu de dessus
PLAN_CLS = {"mur": "w", "linteau": None, "cadre": "cadre", "baie": "win", "caisson": "cab", "facade": "fac",
            "pied": None, "etagere": "upper", "canape": "sofa", "table": "tbl", "chaise": None, "desserte": "cab",
            "vinyles": None, "platine": "dark", "lampe": "lampe", "volet": "dark", "table_basse": "tbl",
            "chilienne": "chil", "tapis": "tapis", "lampe_pied": None, "plante": "plante", "pot": None,
            "cadre_mur": "cadrem", "livres": None, "fauteuil": "dyv", "projection": "proj", "projecteur": "projr",
            "clim": "clim", "papier_peint": None, "poutre": "poutre",
            "objet": None, "livre": None, "rideau": "rideau", "tringle": None}


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
        elif b.role == "fauteuil":
            o.append(rect(b.x0, b.y0, b.x1, b.y1, cls, 14))
        elif b.role == "table_basse":
            o.append(rect(b.x0, b.y0, b.x1, b.y1, cls, 6))
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
    o.append(rect(M.L + M.EP, -12, M.L + 116, M.P + 12, "room"))
    o.append(text(M.L + 64, 330, "Pièce 1", "lbl muted"))
    o.append(rect(-10, M.P + 12, M.L + M.EP, M.P + 52, "room"))
    o.append(text(272, M.P + 38, "Chambre", "lbl muted"))
    sol = [(0, 0), (M.DECROCHE["x0"], 0), (M.DECROCHE["x0"], M.DECROCHE["y"]), (M.L, M.DECROCHE["y"]),
           (M.L, M.P), (M.COFFRE["x1"], M.P), (M.COFFRE["x1"], M.COFFRE["y0"]), (0, M.COFFRE["y0"])]
    ca = M.CARRELAGE["taille"]
    o.append(f'<defs><pattern id="carreaux" width="{ca}" height="{ca}" patternUnits="userSpaceOnUse">'
             f'<rect class="carreau" width="{ca}" height="{ca}"/></pattern></defs>')
    o.append(f'<polygon class="floorbg" points="{" ".join(f"{f(x)},{f(y)}" for x, y in sol)}"/>')
    o.append(f'<polygon fill="url(#carreaux)" points="{" ".join(f"{f(x)},{f(y)}" for x, y in sol)}"/>')
    o += volumes_plan()
    # papier peint : bande sur la face du mur derrière la desserte
    o.append(rect(M.DECROCHE["x0"], M.DECROCHE["y"] - 2, M.L, M.DECROCHE["y"], "pp"))
    # baie coulissante : deux vantaux dans l'épaisseur du mur
    o.append(f'<line class="glass" x1="{M.L + 4}" y1="{ba["y0"]}" x2="{M.L + 4}" y2="{ba["milieu"] + 3}"/>')
    o.append(f'<line class="glass" x1="{M.L + 8}" y1="{ba["milieu"] - 3}" x2="{M.L + 8}" y2="{ba["y1"]}"/>')
    o.append(text(M.L + 21, (ba["y0"] + ba["y1"]) / 2, f'baie {f(ba["y1"] - ba["y0"])}', "lbls muted",
                  extra=f' transform="rotate(-90 {M.L + 21} {(ba["y0"] + ba["y1"]) / 2})"'))
    # passage sans porte
    o.append(f'<line class="seuil" x1="-10" y1="{pa["y0"]}" x2="-10" y2="{pa["y1"]}"/>')
    o.append(f'<line class="seuil" x1="0" y1="{pa["y0"]}" x2="0" y2="{pa["y1"]}"/>')
    o.append(text(14, (pa["y0"] + pa["y1"]) / 2, f'passage {f(pa["y1"] - pa["y0"])}', "lblx muted",
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
    o.append(text(xc, 52, f'③ SÖDERHAMN {c["l"]} × {c["p"]}', "lbls"))
    yd = (d["y0"] + d["y1"]) / 2
    xd = (d["x0"] + d["x1"]) / 2
    o.append(text(xd, d["y1"] + 9, "④ Desserte · platine vinyle", "lbls"))
    rx, ry = t["ronde"]
    o.append(f'<g class="cf">{text(rx, ry - 10, "⑤ Table ronde Ø " + f(t["d"]), "lbls")}'
             f'{text(rx, ry - 3, "4 couverts", "lblx")}</g>')
    o.append(f'<g class="co">{text(t["cx"], t["cy"] - 14, "⑤ Table " + f(t["ouvert"]) + " × " + f(t["d"]), "lbls")}'
             f'{text(t["cx"], t["cy"] - 7, "12 couverts · " + str(t["allonges"]) + " allonges de " + f(t["allonge"]), "lblx")}</g>')
    tb, ch, dy, k = M.TABLE_BASSE, M.CHILIENNE, M.DYVLINGE, M.CONSOLE
    for cfg, (x0, y0, x1, y1) in tb["pos"].items():
        xm, ym = (x0 + x1) / 2, (y0 + y1) / 2
        rot = f' transform="rotate(-90 {f(xm)} {f(ym)})"' if y1 - y0 > x1 - x0 else ""
        o.append(f'<g class="c{cfg}">{text(xm, ym + 2, "⑥ Table basse", "lblx", extra=rot)}</g>')
    for cfg, (x0, y0) in dy["pos"].items():
        o.append(f'<g class="c{cfg} adyv">{text(x0 + dy["p"] / 2 - 8, y0 + dy["l"] / 2 - 1, "⑦ DYVLINGE", "lblx")}'
                 f'{text(x0 + dy["p"] / 2 - 8, y0 + dy["l"] / 2 + 6, "pivotant", "lblx muted")}</g>')
    o.append(f'<g class="cf achil">{text(ch["x0"] + 50, ch["y0"] + ch["l"] / 2 + 2, "⑦ Chilienne", "lblx")}</g>')
    o.append(f'<g class="co achil">{text(60 + ch["l"] / 2, M.P - 18, "⑦ chilienne pliée", "lblx")}</g>')
    o.append(text((k["x0"] + k["x1"]) / 2, k["y0"] + 14, f'⑧ Meuble bas {k["l"]} × {k["p"]}', "lbls"))
    o.append(text((k["x0"] + k["x1"]) / 2, k["y0"] + 22, f'écran au-dessus : image {f(M.ECRAN["l"])} × {f(M.ECRAN["h"])}', "lblx"))
    o.append(text((M.CLIM["x0"] + M.CLIM["x1"]) / 2, M.P - M.CLIM["p"] + 13, f'clim (h {f(M.CLIM["z0"])})', "lblx"))
    o.append(text(360, M.P - 5, f'poutre au-dessus, dessous à {f(M.POUTRE["z0"])}', "lblx muted"))
    pj = M.PROJECTEUR
    o.append(text(pj["cx"], pj["cy"] + pj["p"] / 2 + 7, "vidéoprojecteur (plafond)", "lblx"))
    # décoration (bouton Déco)
    dz = [text(M.TAPIS["x0"] + 6, M.TAPIS["y1"] - 4, "tapis", "lblx muted", "start"),
          text(M.LAMPADAIRE["cx"], M.LAMPADAIRE["cy"] + 2, "lampadaire", "lblx")]
    o.append(f'<g class="dz">{"".join(dz)}</g>')
    # cotes
    o.append(cote_h(0, M.L, -30))
    o.append(cote_v(0, M.P, -22))
    o.append(cote_h(c["x0"], c["x1"], -18, f'{c["l"]}'))
    o.append(cote_h(e["p"], c["x0"], -18, f'{M.ALLEE_ENFILADE}'))
    o.append(cote_h(0, e["p"], -18, f'{e["p"]}'))
    o.append(cote_v(e["y0"], e["y1"], -14 + 0, f'{f(e["y1"] - e["y0"])} utiles'))
    o.append(cote_h(d["x0"], d["x1"], -18, f'{d["x1"] - d["x0"]}'))
    # dégagements
    lo = t["ouvert"]
    xo, xe = t["cx"] - lo / 2, t["cx"] + lo / 2
    xb, yb, _, yb1 = tb["pos"]["f"]
    o.append('<g class="cf">'
             + degage((xb + 15, c["p"]), (xb + 15, yb), dt=(6, 2))
             + degage((xb + 15, yb1), (xb + 15, k["y0"]), dt=(6, 2))
             + "</g>")
    xr = t["cx"] - 35
    o.append('<g class="co">'
             + degage((xr, c["p"]), (xr, t["cy"] - t["r"]), dt=(0, -14))
             + degage((xr, t["cy"] + t["r"]), (xr, k["y0"]), dt=(0, 16))
             + degage((e["p"], t["cy"]), (xo, t["cy"]), dt=(0, -2))
             + degage((xe, t["cy"]), (M.L, t["cy"]), dt=(0, -2))
             + "</g>")
    # traits de coupe
    for x, lab, sens in ((COUPE_A, "A", -1), (COUPE_B, "B", 1)):
        o.append(f'<line class="sec" x1="{x}" y1="-6" x2="{x}" y2="{M.P + 6}"/>')
        for y in (-10, M.P + 16):
            o.append(text(x + 8 * sens, y, lab, "sect"))
    o.append(f'<line class="sec" x1="-6" y1="{COUPE_C}" x2="{M.L + 6}" y2="{COUPE_C}"/>')
    o.append(text(-4, COUPE_C - 5, "C", "sect", "end"))
    o.append(f'<line class="sec" x1="-6" y1="{COUPE_D}" x2="{M.L + 6}" y2="{COUPE_D}"/>')
    o.append(text(-4, COUPE_D - 5, "D", "sect", "end"))
    o.append(text(M.L + 4, COUPE_D - 5, "D", "sect", "start"))
    o.append(text(M.L + 4, COUPE_C - 5, "C", "sect", "start"))
    return (f'<svg viewBox="-150 -50 820 470" role="img" aria-label="Plan du salon">{"".join(o)}</svg>')


# ------------------------------------------------------------------ coupes
COUPE_CLS = {"mur": ("bgwall", "w"), "linteau": ("wallv", "w"), "poutre": ("wallv", "w"), "cadre": ("cadre", "cadre"), "baie": ("vitre", "vitrec"),
             "caisson": ("cab", "cab"), "facade": ("fac", "fac"), "pied": ("dark", "dark"),
             "etagere": ("shelf", "shelfc"), "canape": ("sofa", "sofa"), "table": ("tbl", "tbl"),
             "chaise": ("stool", "stool"), "desserte": ("cab", "cab"), "vinyles": ("vinyl", "vinyl"),
             "platine": ("dark", "dark"), "lampe": ("lampe", "lampe"), "volet": ("tbl", "tbl"),
             "table_basse": ("tbl", "tbl"), "chilienne": ("chil", "chil"), "tapis": ("tapis", "tapis"),
             "lampe_pied": ("dark", "dark"), "plante": ("plante", "plante"), "pot": ("pot", "pot"),
             "cadre_mur": ("cadrem", "cadrem"), "livres": ("livre", "livre"), "fauteuil": ("dyv", "dyv"),
             "projection": ("proj", "proj"), "projecteur": ("dark", "dark"), "clim": ("clim", "clim"),
             "papier_peint": ("pp", "pp"), "objet": ("pot", "pot"), "livre": ("livre", "livre"),
             "rideau": ("rideau", "rideau"), "tringle": ("dark", "dark")}

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
        o.append(rect(u, -b.z1, v, -b.z0, COUPE_CLS[b.role][1 if coupe else 0] + cfg_cls(b).replace(f" c{b.config}", "")))
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
    v4, v12 = (visibles(cut, regard, umin, umax, c) for c in ("f", "o"))
    if [b.nom for b in v4 if b.config] == [] and [b.nom for b in v12 if b.config] == []:
        return coupe_svg(cut, regard, umin, umax, "f", *args[4:], **kw)
    return "".join(f'<div class="c{c}">{coupe_svg(cut, regard, umin, umax, c, *args[4:], **kw)}</div>'
                   for c in ("f", "o"))


def coupe_a():
    e, et = M.ENFILADE, M.ETAGERES

    def cotes(X):
        u0, u1 = sorted((X(e["y0"]), X(e["y1"])))
        p0, p1 = sorted((X(M.PASSAGE["y0"]), X(M.PASSAGE["y1"])))
        r = [cote_h(u0, u1, 18, f'enfilade {f(e["y1"] - e["y0"])}'),
             cote_h(p0, p1, 18, f'passage {round(M.PASSAGE["y1"] - M.PASSAGE["y0"], 1):g}')]
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
        return [cote_h(0, e["p"], 18), cote_h(c["x0"], c["x1"], 18, f'canapé {c["l"]}')]

    return coupe_configs(COUPE_C, "nord", -20, M.L + 20,
                         [c["assise"], t["z1"], e["z1"], M.SUSPENSION["z0"]], extra=cotes)


def coupe_d():
    k, ec, cl = M.CONSOLE, M.ECRAN, M.CLIM

    def cotes(X):
        u0, u1 = sorted((X(ec["x0"]), X(ec["x1"])))
        k0, k1 = sorted((X(k["x0"]), X(k["x1"])))
        c0, c1 = sorted((X(cl["x0"]), X(cl["x1"])))
        return [cote_h(k0, k1, 18, f'meuble bas {k["l"]}'),
                cote_h(u0, u1, -(ec["bas"] + ec["h"]) - 6, f'image {f(ec["l"])} × {f(ec["h"])} (16/9)'),
                text((u0 + u1) / 2, -(ec["bas"] + ec["h"] / 2), "écran (mur peint en blanc mat)", "lblc"),
                cote_h(c0, c1, -cl["z1"] - 6, f'clim {cl["x1"] - cl["x0"]}')]

    return coupe_configs(COUPE_D, "sud", -20, M.L + 20,
                         [k["pieds"], k["z1"], ec["bas"], ec["bas"] + ec["h"], cl["z0"], cl["z1"]], extra=cotes)


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
.scroll{overflow-x:auto}.scroll svg{display:block;width:100%;height:auto}.scroll>table{min-width:640px}
.cap{font-size:13px;color:var(--muted);margin:8px 4px 2px}
.note{font-size:13px;color:var(--muted)}
table{border-collapse:collapse;width:100%;font-size:14px}
th,td{text-align:left;padding:7px 8px;border-bottom:1px solid var(--line);vertical-align:top}
td.num,th.num{text-align:right;font-family:"JetBrains Mono",ui-monospace,monospace;white-space:nowrap}
.mono{font-family:"JetBrains Mono",ui-monospace,monospace;white-space:nowrap}
ul.pistes{padding-left:20px;max-width:860px}ul.pistes li{margin:6px 0}
svg text{font-family:Archivo,system-ui,sans-serif;fill:var(--ink)}
.room{fill:var(--line);fill-opacity:.25}
.floorbg{fill:#D9D2C6;fill-opacity:.35}
.carreau{fill:none;stroke:#B5AC9C;stroke-width:.4;stroke-opacity:.7}
.rendu img{display:block;width:100%;height:auto;border-radius:8px}
.rendu figure{margin:0}
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
.chil{fill:#C49A6C;fill-opacity:.35;stroke:var(--ink);stroke-width:.7;stroke-dasharray:5 1.5}
.tapis{fill:#B4553A;fill-opacity:.12;stroke:#B4553A;stroke-opacity:.5;stroke-width:.8;stroke-dasharray:1 2}
.plante{fill:#6E9B5A;fill-opacity:.7;stroke:#3F6B31;stroke-width:.6;stroke-dasharray:3 2}.pot{fill:#C2703D;stroke:var(--ink);stroke-width:.5}
.cadrem{fill:#E9E2D2;stroke:var(--ink);stroke-width:.8}
.rideau{fill:#E8DFCC;fill-opacity:.8;stroke:#A89A80;stroke-width:.6;stroke-dasharray:2 1.5}
.livre{fill:#7C8A5E;fill-opacity:.55;stroke:var(--ink);stroke-width:.3}
body:not(.deco) .dz{display:none}
body.schil .adyv,body:not(.schil) .achil{display:none}
.dyv{fill:#D9772B;fill-opacity:.55;stroke:var(--ink);stroke-width:.7}
.proj{fill:#FFFFFF;fill-opacity:.6;stroke:var(--water);stroke-width:.8;stroke-dasharray:5 2}
.projr{fill:var(--ink);fill-opacity:.15;stroke:var(--ink);stroke-width:.7;stroke-dasharray:3 2}
.pp{fill:#4B2E3B;fill-opacity:.75;stroke:#7E9A86;stroke-width:.6;stroke-dasharray:2 2}
.poutre{fill:none;stroke:var(--muted);stroke-width:.8;stroke-dasharray:8 3 2 3}
.clim{fill:#F4F4F2;stroke:var(--ink);stroke-width:.7;stroke-dasharray:3 2}
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
body.tor .cf,body:not(.tor) .co{display:none}
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
.vbar .deco{margin-left:auto}
h2{scroll-margin-top:60px}
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


def tog_table():
    return ('<div class="tog"><span>Table</span>'
            + "".join(f'<button type="button" data-t="{cfg}" aria-pressed="{str(cfg == "f").lower()}">'
                      f'{k["nom"]}{" · " + str(k["chaises"]) if k["chaises"] else ""}</button>' for cfg, k in M.CONFIGS.items())
            + '<span style="margin-left:14px">Siège</span>'
            '<button type="button" data-a="dyv" aria-pressed="true">DYVLINGE</button>'
            '<button type="button" data-a="chil" aria-pressed="false">chilienne</button></div>')


def table_rangement():
    e, d = M.ENFILADE, M.DESSERTE
    lignes = [
        ("① Enfilade", f'{f(e["y1"] - e["y0"])} × {e["p"]} × {e["z1"]}, 3 modules de {f(e["modules"][0][1] - e["modules"][0][0])}',
         f"≈ {round(M.VOLUME_ENFILADE, -1):.0f} L"),
        ("② Étagères suspendues", f'{len(M.ETAGERES["zs"])} × {f(e["y1"] - e["y0"])}, P{M.ETAGERES["p"]}',
         f'{virg(M.METRES_ETAGERES)} m · ≈ {M.METRES_ETAGERES * M.CHARGE_LIVRES:.0f} kg pleines'),
        ("④ Desserte", f'{d["x1"] - d["x0"]} × {d["y1"] - d["y0"]} × {d["z1"]} sur roulettes, 2 niveaux pour vinyles',
         f"≈ {round(M.VINYLES, -1):.0f} disques"),
    ]
    corps = "".join(f'<tr><td>{a}</td><td>{b}</td><td class="num">{c}</td></tr>' for a, b, c in lignes)
    return f'<table><thead><tr><th>Meuble</th><th>Dimensions</th><th class="num">Capacité</th></tr></thead><tbody>{corps}</tbody></table>'


def table_repliables():
    corps = "".join(
        f'<tr><td>{escape(ty)}</td><td>{f"<a href={chr(34)}{escape(u)}{chr(34)}>{escape(m)}</a>" if u else escape(m)}</td>'
        f'<td class="num">{escape(r)}</td><td>{escape(o)}</td><td>{escape(pl)}</td><td class="num">{escape(px)}</td></tr>'
        for ty, m, r, o, pl, px, u in M.TABLES_REPLIABLES)
    return ('<div class="scroll"><table><thead><tr><th>Type</th><th>Modèle</th><th class="num">Repliée</th><th>Ouverte</th>'
            f'<th>Places</th><th class="num">Prix</th></tr></thead><tbody>{corps}</tbody></table></div>')


def galerie():
    """Rendus 3D présents dans salon-v4-3d/ (faits sur demande), avec un bouton par variante."""
    blocs = []
    for titre, version, variantes in M.RENDUS:
        vus = [(v, n) for v, n in variantes if os.path.exists(os.path.join(ROOT, "salon-v4-3d", f"{v}.jpg"))]
        if not vus:
            continue
        boutons = "".join(f'<button type="button" data-rv="{v}" aria-pressed="{str(i == 0).lower()}">{escape(n)}</button>'
                          for i, (v, n) in enumerate(vus)) if len(vus) > 1 else ""
        figs = "".join(
            f'<figure data-rv="{v}"{" hidden" if i else ""}><img src="salon-v4-3d/{v}.jpg?v='
            f'{int(os.path.getmtime(os.path.join(ROOT, "salon-v4-3d", f"{v}.jpg")))}" alt="{escape(titre)} · {escape(n)}" '
            f'loading="lazy"></figure>' for i, (v, n) in enumerate(vus))
        blocs.append(f'<div class="fig rendu rgrp">{f"<div class=tog><span>Bois</span>{boutons}</div>" if boutons else ""}'
                     f'{figs}<p class="note">{escape(titre)} · modèle {version}</p></div>')
    return f'<h2>Rendu 3D</h2>\n{"".join(blocs)}\n' if blocs else ""


def contenu():
    e, et, c, d, t, dg = M.ENFILADE, M.ETAGERES, M.CANAPE, M.DESSERTE, M.TABLE, M.DEGAGEMENTS
    lignes = "".join(f'<tr><td class="mono">{v}</td><td class="mono">{dt}</td><td>{escape(x)}</td></tr>'
                     for v, dt, x in M.CHANGEMENTS)
    modules = " ; ".join(f'M{k + 1} {escape(ct)}' for k, (_, ct) in enumerate(M._MODULES))
    return f"""<div class="kicker">Salon · {M.VERSION}</div>
<h1>Salon V4</h1>
<p class="pitch">La bibliothèque reste au mur ouest : une enfilade basse avec des étagères suspendues au-dessus, le canapé dans son angle avec une table basse et un siège pivotant, face à un meuble bas sous le mur de projection. Contre le mur nord, à côté de la baie, une desserte pour la platine vinyle. La table ronde du quotidien s'ouvre au milieu pour recevoir douze personnes.</p>

<h2>Plan</h2>
<div class="fig">{tog_table()}<div class="scroll">{plan_svg()}</div>
<p class="cap">Échelle : 1 unité = 1 cm ; ouest à gauche, nord en haut. <b>① Enfilade</b> contre le mur ouest, du coin nord au cadre du passage ({f(e["y1"] - e["y0"])} utiles), profondeur {e["p"]} (caisson {e["p"] - e["facade"]} + façades {e["facade"]}), dessus à {e["z1"]}, sur pieds de {e["pieds"]} ; trois modules de {f(e["modules"][0][1] - e["modules"][0][0])} : {modules}. <b>② Étagères suspendues</b> (tireté) : {len(et["zs"])} tablettes {f(et["y1"] - et["y0"])} × {et["p"]} au-dessus de l'enfilade, sur toute sa longueur ; fixation à étudier (voir plus bas). <b>③ Canapé</b> {c["nom"]} {c["l"]} × {c["p"]} dos au mur nord, tourné vers le sud, à {M.ALLEE_ENFILADE} de l'enfilade : l'allée laisse ouvrir les portes du module nord. <b>④ Desserte</b> {d["x1"] - d["x0"]} × {d["y1"] - d["y0"]} sur roulettes, contre le mur nord, dans le décroché nord-est (x {d["x0"]} → {d["x1"]}), façade au sud : à côté de la baie, sans rien devant le vitrage. Platine au milieu du dessus, vinyles sur deux niveaux (≈ {round(M.VINYLES, -1):.0f}). <b>⑤ Table</b> à volets et allonges (type Louis-Philippe). Au quotidien, <b>ronde</b> Ø {f(t["d"])} (volets levés) dans l'angle sud-est, face à la baie, centrée en {t["ronde"]}, avec 4 chaises en biais et la suspension au-dessus. Pour recevoir, on la tire au milieu et on ajoute {t["allonges"]} allonges de {t["allonge"]} : <b>ouverte</b>, ovale de {f(t["ouvert"])} × {f(t["d"])} centrée en ({t["cx"]}, {t["cy"]}), est-ouest (nord-sud, il faudrait {f(t["ouvert"] + 2 * 70)} pour {M.P}), 12 chaises à pas de {M.PAS_CHAISES:.0f}, une à chaque bout ; les {M.CHAISES_PLIANTES} chaises de plus sont pliantes, rangées dans le kafoutche extérieur. <b>⑥ Table basse</b> <a href="{M.TABLE_BASSE["url"]}">{M.TABLE_BASSE["nom"]}</a> {M.TABLE_BASSE["l"]} × {M.TABLE_BASSE["p"]} ({M.TABLE_BASSE["prix"]} €), dessus à {M.TABLE_BASSE["z1"]} (à peine au-dessus de l'assise, {M.CANAPE["assise"]}), à {M.TABLE_BASSE["ecart"]} devant le canapé, centrée sur lui. <b>⑦ Siège</b> (bouton Siège) : <a href="{M.DYVLINGE["url"]}">IKEA DYVLINGE</a> pivotant ({M.DYVLINGE["l"]} × {M.DYVLINGE["p"]} × {M.DYVLINGE["h"]}, assise à {M.DYVLINGE["assise"]}, {M.DYVLINGE["prix"]} €) à l'est de la table basse, tourné vers le canapé ; il pivote vers l'écran ou la baie. Variante : chilienne {M.CHILIENNE["long"]} × {M.CHILIENNE["l"]}, tête à l'est. <b>⑧ Meuble bas</b> style enfilade scandinave {M.CONSOLE["l"]} × {M.CONSOLE["p"]} × {M.CONSOLE["z1"]} sur pieds, contre le mur sud en face du canapé, centré sur lui ; peu profond pour laisser passer la table ouverte. Le mur sud au-dessus sert d'<b>écran</b> : image {f(M.ECRAN["l"])} × {f(M.ECRAN["h"])} (16/9), bas à {M.ECRAN["bas"]}, vue du canapé à ≈ {M.PROJECTEUR["recul"]} (1,5 fois la largeur de l'image, le confort habituel) ; <b>vidéoprojecteur</b> au plafond au-dessus du canapé, à {M.PROJECTEUR["recul"]} du mur : il faut un rapport de projection de {virg(M.PROJECTEUR["rapport"], 2)} (zoom courant 1,2–1,6). <b>Clim</b> existante sur le mur sud, tout à l'est (x {M.CLIM["x0"]} → {M.CLIM["x1"]}, h {M.CLIM["z0"]} → {M.CLIM["z1"]}, à relever). Table ouverte : la table basse se range debout dans l'allée de l'enfilade (on n'ouvre pas le module nord pendant le dîner), le DYVLINGE recule contre le mur nord à côté de la desserte, la chilienne se plie contre le mur sud. <b>Dégagements</b> (rouge) : au quotidien, {f(dg["canape_basse"])} entre le canapé et la table basse, puis {f(M.CONSOLE["y0"] - M.TABLE_BASSE["pos"]["f"][3])} jusqu'au meuble bas ; ouverte, {f(dg["canape_table"])} entre le canapé et la table, {f(dg["table_sud"])} jusqu'au meuble bas, {f(dg["bout_ouest"])} entre son bout ouest et l'enfilade, {f(dg["bout_est"])} à l'est. À 12, il reste {f(dg["derriere_chaises"])} derrière les chaises côté canapé et côté meuble bas : on s'assoit, on ne circule plus derrière. <b>Déco</b> (bouton dans la barre du haut), proportions d'aménagement : un seul tapis, {M.TAPIS["l"]} × {M.TAPIS["p"]}, sous le coin canapé (25 de plus que le canapé de chaque côté, pieds avant du canapé et de la chilienne dessus), rien sous la table à manger ; lampadaire de lecture contre l'accoudoir est du canapé, derrière l'épaule de qui est dans le siège, hors du passage devant la desserte ; lampe à poser sur l'enfilade, sous la première tablette, et petite lampe au bout de la desserte ; plantes (vert : une grande à droite du meuble bas, hors de l'image et loin du souffle de la clim, des branches sur l'enfilade) ; paire de cadres 55 × 70 au-dessus du canapé (2/3 de sa largeur, bas à 20 du dossier), cadre 80 × 60 au-dessus de la desserte (bas à 135 : le capot de la platine s'ouvre) ; livres sur les étagères, avec un objet au bout de chaque tablette (vase, petite plante, bol) et la tablette du haut, trop basse pour des livres, garnie de deux plantes retombantes et d'un vase ; deux livres d'art et un bol sur la table basse, un vase bas au centre de la table ronde ; <b>rideau</b> de lin écru (beige) sur rail au plafond, tiré au sud de la baie sur le trumeau (au nord, la desserte) : replié, {M.RIDEAU["y1"] - M.RIDEAU["y0"]} de plis dont 15 sur le bord du vitrage. Suspension Ø {M.SUSPENSION["d"]} (tireté jaune, la moitié de la table) au-dessus de la table ronde : table ouverte, elle n'est plus centrée (à prévoir : un second point lumineux ou une suspension déplaçable).</p></div>

<h2>Coupe A-A · mur ouest</h2>
<div class="fig"><div class="scroll">{coupe_a()}</div>
<p class="cap">Coupe à x {COUPE_A}, regard vers l'ouest : le sud est à gauche. Enfilade sur pieds de {e["pieds"]}, dessus à {e["z1"]} ; tablettes de {et["ep"]} avec le dessus à {", ".join(str(z) for z in et["zs"])} (un premier vide de {et["zs"][0] - et["ep"] - e["z1"]} au-dessus de l'enfilade pour poser lampes et objets, puis {et["zs"][1] - et["zs"][0] - et["ep"]} de hauteur libre entre tablettes : les livres courants font 18 à 30). À gauche, le passage vers le couloir ({round(M.PASSAGE["y1"] - M.PASSAGE["y0"], 1):g} × {M.PASSAGE["h"]}) avec son cadre.</p></div>

<h2>Coupe B-B · baie et desserte</h2>
<div class="fig"><div class="scroll">{coupe_b()}</div>
<p class="cap">Coupe à x {COUPE_B}, regard vers l'est : le nord est à gauche. Desserte h {d["z1"]} sur roulettes de {d["roulettes"]} : deux niveaux de vinyles debout (pochettes 31,5) et la platine dessus, dont le plateau arrive vers {d["z1"] + 10}, à hauteur de main debout. Elle est coupée à gauche, contre le mur nord, à côté de la baie qui reste entièrement dégagée (tireté au milieu = jonction des vantaux). Table ronde et ses chaises devant la baie ; grande plante et cadre (déco) à droite, contre le trumeau sud.</p></div>

<h2>Coupe C-C · à travers la table</h2>
<div class="fig">{tog_table()}<div class="scroll">{coupe_c()}</div>
<p class="cap">Coupe à y {COUPE_C} (axe de la table ouverte), regard vers le nord : l'ouest est à gauche. Enfilade et étagères coupées à gauche, canapé contre le mur nord au fond, desserte et platine au fond à droite, baie coupée. Au quotidien : table basse devant le canapé, chilienne coupée, table ronde coupée à droite ; ouverte : table coupée au milieu (plateau à {t["z1"]}), table basse poussée au fond à côté du canapé. Suspension Ø {M.SUSPENSION["d"]}, bas à {M.SUSPENSION["z0"]}, soit {M.SUSPENSION["z0"] - t["z1"]} au-dessus du plateau.</p></div>

<h2>Coupe D-D · mur sud, écran</h2>
<div class="fig">{tog_table()}<div class="scroll">{coupe_d()}</div>
<p class="cap">Coupe à y {COUPE_D}, regard vers le sud : l'est est à gauche. Meuble bas {M.CONSOLE["l"]} × {M.CONSOLE["p"]}, dessus à {M.CONSOLE["z1"]}, trois façades (deux portes, un abattant au milieu pour la box et les câbles) ; au-dessus, l'image {f(M.ECRAN["l"])} × {f(M.ECRAN["h"])} de {M.ECRAN["bas"]} à {f(M.ECRAN["bas"] + M.ECRAN["h"])}, sous la clim (h {M.CLIM["z0"]}) qui reste hors de l'image, à gauche. À droite, le passage vers le couloir. Table ronde et chaises coupées au premier plan à gauche ; ouverte, la table coupée au milieu.</p></div>

{galerie()}<h2>Matériaux</h2>
<div class="fig"><table><tbody>
<tr><td>Sol</td><td>Carrelage {M.CARRELAGE["nom"]}, pose droite parallèle aux murs, joints fins ; teinte à choisir (rendu : {M.CARRELAGE["couleur"]}).</td></tr>
<tr><td>Murs et plinthes</td><td>{M.MURS["nom"]}, {M.MURS["couleur"]} ; plinthes de la couleur des murs.</td></tr>
<tr><td>Mur derrière la desserte</td><td>Papier peint {M.PAPIER_PEINT["nom"]} ; motif ≈ {M.PAPIER_PEINT["motif"]} cm, de la plinthe au plafond, sur le mur nord du décroché (violet sur le plan).</td></tr>
<tr><td>Bois</td><td>Enfilade, étagères, desserte, meuble bas : chêne miel (comme les meubles hauts de la cuisine) ; table Louis-Philippe et chaises : noyer ou merisier anciens ; table basse UGGLERUM plaqué noyer.</td></tr>
<tr><td>Tissus</td><td>Canapé SÖDERHAMN housse Gunnared gris moyen ; DYVLINGE Kelinge orange ; tapis laine beige ; rideau {M.RIDEAU["nom"]}.</td></tr>
</tbody></table></div>

<h2>Pistes déco</h2>
<p>Non dessinées : à essayer une fois le reste en place.</p>
<ul class="pistes">{"".join(f"<li><b>{a}</b> : {b}.</li>" for a, b in M.PISTES_DECO)}</ul>

<h2>Rangements</h2>
<div class="fig">{table_rangement()}
<p class="cap">Volume utile de l'enfilade : intérieur des caissons, panneaux de {e["ep"]} déduits. Étagères : {M.CHARGE_LIVRES} kg par mètre pleine de livres (ordre de grandeur), d'où la question de la fixation. Vinyles : environ 3,5 mm par disque sous pochette, rangées de 31,5 de profondeur.</p></div>

<h2>Tables qui se replient</h2>
<div class="fig">{table_repliables()}
<p class="cap">Recherche du 11/10/2026. Ronde Ø 90 : on n'en trouve pas qui dépasse ≈ 190 ouverte, soit 8 à 10 couverts ; pour 12, il faut au moins une Ø 100 et 4 allonges (280, serré : ≈ 62 par personne). Les consoles extensibles ont la plus petite emprise repliée (≈ 0,4 m²) mais sont rectangulaires et étroites (90) ; leurs rallonges se rangent dans la console ou à côté. Les tables à volets et allonges (Louis-Philippe) sont rondes volets levés et ovales avec leurs allonges, souvent anciennes, à chiner : c'est le type dessiné. Les tables à abattants seules (gateleg) se replient très bien mais plafonnent à 6 places. Dimensions et prix relevés sur les fiches : à revérifier avant achat.</p></div>

<h2>Étagères suspendues : fixation à étudier</h2>
<p>Charge à reprendre : jusqu'à {M.METRES_ETAGERES * M.CHARGE_LIVRES:.0f} kg sur {virg(M.METRES_ETAGERES)} m de tablettes, au-dessus d'un meuble qu'on ne veut pas faire porter. Le mur ouest est la cloison du cellier et du WC (nature à confirmer). Pistes à comparer :</p>
<ul class="pistes">
<li><b>Tiges ou câbles depuis le plafond</b>, tablettes accrochées dessous (vraie étagère suspendue, rien dans la cloison) : dépend du plafond (béton, hourdis, faux plafond ?) ; tiges filetées Ø 8–10 sous fourreau, ou câbles inox avec serre-câbles réglables ; un appui ponctuel au mur pour empêcher le balancement.</li>
<li><b>Montants plafond–sol</b> en tension ou vissés au plafond, derrière l'enfilade (comme la String ou la Moebe de la page bibliothèque), tablettes sur consoles : rien de porté par la cloison.</li>
<li><b>Fixations invisibles</b> (tiges dans la cloison, tablettes percées) : le plus « flottant », mais exige un mur plein ou un renfort dans la cloison ; portée 258 trop longue d'un seul tenant.</li>
<li><b>Crémaillères et consoles</b> : la solution connue (voir <a href="salon-bibliotheque-fixation.html">page Fixations</a>), à garder comme repli.</li>
</ul>
<p class="note">À relever avant de choisir : nature du plafond et de la cloison (sondage, carottage léger), position des réseaux électriques dans le mur ouest, flèche admissible d'une tablette de {et["ep"]} sur la portée retenue.</p>

<h2>Points à vérifier</h2>
<ul class="pistes">
<li><b>Prises</b> : près de la desserte (platine, ampli ou enceintes actives), près du canapé (lampadaire), derrière le meuble bas (box), au plafond (vidéoprojecteur).</li>
<li><b>Chaises</b> : 4 autour de la table ronde ; les {M.CHAISES_PLIANTES} pliantes de plus pour recevoir à 12 sont rangées dans le kafoutche extérieur.</li>
<li><b>Canapé</b> : <a href="{c["url"]}">{c["nom"]}</a>, {c["l"]} × {c["p"]} × {c["dos"]} ; hauteur d'assise à relever en magasin (dessinée à {c["assise"]}, la table basse UGGLERUM est à {M.TABLE_BASSE["z1"]}).</li>
<li><b>Table</b> : ronde Ø {f(t["d"])} à volets et allonges, à chiner (les Louis-Philippe font souvent 105 à 120) ; il faut 4 allonges de 45 pour 280. Ø 90 : 10 couverts au plus.</li>
<li><b>Clim</b> : position et dimensions à relever ; le souffle tombe sur la table ronde du quotidien (déflecteur orienté vers le haut).</li>
<li><b>Vidéoprojecteur</b> : rapport de projection {virg(M.PROJECTEUR["rapport"], 2)} pour une image de {f(M.ECRAN["l"])} à {M.PROJECTEUR["recul"]} ; prise et câble HDMI au plafond, ou projecteur posé sur une tablette au-dessus du canapé. Mur sud peint en blanc mat (ou toile tendue).</li>
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
             f'<button type="button" class="deco" aria-pressed="false">Déco</button>'
             f'<button type="button" class="expl" aria-pressed="false">Explications</button>'
             f'<button type="button" class="chg" aria-pressed="false">Changements</button></div>')
    return f"""<!doctype html>
<html lang="fr">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Salon V4</title>
<link rel="icon" href="{racine}favicon.svg" type="image/svg+xml">
<link rel="apple-touch-icon" href="{racine}apple-touch-icon.png">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Archivo:wght@400;500;700;800&family=JetBrains+Mono:wght@400;600&display=swap" rel="stylesheet">
<style>{CSS}</style>
</head>
<body>
{barre}
<nav class="toc" aria-label="Sommaire"><button type="button" class="tbtn" aria-expanded="true">Sommaire</button><ol></ol></nav>
<main class="wrap">
<div class="ver" data-v="courante">{contenu()}</div>
{blocs}
</main>
<script>
(function () {{
  function garde(k, v) {{ try {{ localStorage.setItem("{CLE}-" + k, v); }} catch (e) {{}} }}
  function lit(k) {{ try {{ return localStorage.getItem("{CLE}-" + k); }} catch (e) {{ return null; }} }}
  var bs = document.querySelectorAll(".vbar button[data-v]"), vs = document.querySelectorAll(".ver"), sommaire = function () {{}};
  function montre(v) {{
    if (!document.querySelector('.ver[data-v="' + v + '"]')) v = "courante";
    vs.forEach(function (d) {{ d.hidden = d.dataset.v !== v; }});
    bs.forEach(function (b) {{ b.setAttribute("aria-pressed", b.dataset.v === v); }});
    garde("version", v);
    sommaire();
  }}
  bs.forEach(function (b) {{ b.addEventListener("click", function () {{ montre(b.dataset.v); }}); }});
  function table(t) {{
    document.body.classList.toggle("tor", t === "o");
    document.querySelectorAll(".tog button[data-t]").forEach(function (b) {{ b.setAttribute("aria-pressed", b.dataset.t === t); }});
    garde("table", t);
  }}
  document.querySelectorAll(".tog button[data-t]").forEach(function (b) {{
    b.addEventListener("click", function () {{ table(b.dataset.t); }});
  }});
  table(lit("table") === "o" ? "o" : "f");
  function siege(a) {{
    document.body.classList.toggle("schil", a === "chil");
    document.querySelectorAll(".tog button[data-a]").forEach(function (b) {{ b.setAttribute("aria-pressed", b.dataset.a === a); }});
    garde("siege", a);
  }}
  document.querySelectorAll(".tog button[data-a]").forEach(function (b) {{
    b.addEventListener("click", function () {{ siege(b.dataset.a); }});
  }});
  siege(lit("siege") === "chil" ? "chil" : "dyv");
  function bascule(sel, cls) {{
    var b = document.querySelector(sel);
    function pose(on) {{ document.body.classList.toggle(cls, on); b.setAttribute("aria-pressed", on); garde(cls, on ? "1" : ""); }}
    b.addEventListener("click", function () {{ pose(b.getAttribute("aria-pressed") !== "true"); }});
    pose(lit(cls) === "1");
  }}
  document.querySelectorAll(".rgrp .tog button[data-rv]").forEach(function (b) {{
    b.addEventListener("click", function () {{
      var g = b.closest(".rgrp");
      g.querySelectorAll(".tog button[data-rv]").forEach(function (x) {{ x.setAttribute("aria-pressed", x === b); }});
      g.querySelectorAll("figure[data-rv]").forEach(function (f) {{ f.hidden = f.dataset.rv !== b.dataset.rv; }});
    }});
  }});
  bascule(".vbar .deco", "deco");
  bascule(".vbar .expl", "explications");
  bascule(".vbar .chg", "changements");
  // sommaire (ordinateur) : les titres h2 de la version affichée, repliable, titre courant surligné
  var toc = document.querySelector(".toc"), tol = toc.querySelector("ol"), tb = toc.querySelector(".tbtn"), hs = [];
  function ouvert(on) {{
    document.body.classList.toggle("toc-on", on);
    tb.setAttribute("aria-expanded", on);
    tb.textContent = on ? "« Sommaire" : "Sommaire »";
    garde("toc", on ? "1" : "0");
  }}
  tb.addEventListener("click", function () {{ ouvert(!document.body.classList.contains("toc-on")); }});
  ouvert(lit("toc") !== "0");
  function suivre() {{
    var haut = document.querySelector(".vbar").offsetHeight;
    toc.style.top = haut + "px";
    var k = -1;
    hs.forEach(function (h, i) {{ if (h.offsetParent && h.getBoundingClientRect().top < haut + 80) k = i; }});
    tol.querySelectorAll("a").forEach(function (a, i) {{ a.classList.toggle("on", i === k); }});
  }}
  sommaire = function () {{
    var ver = document.querySelector(".ver:not([hidden])");
    hs = ver ? Array.prototype.slice.call(ver.querySelectorAll("h2")) : [];
    tol.innerHTML = "";
    hs.forEach(function (h, i) {{
      if (!h.id) h.id = (ver.dataset.v + "-" + i).replace(/[^a-zA-Z0-9-]/g, "-");
      var li = document.createElement("li"), a = document.createElement("a");
      a.href = "#" + h.id; a.textContent = h.textContent.trim();
      a.addEventListener("click", function (e) {{
        e.preventDefault();
        if (h.closest('section[id^="changements"]')) document.querySelector(".vbar .chg").getAttribute("aria-pressed") === "true" || document.querySelector(".vbar .chg").click();
        h.scrollIntoView({{behavior: "smooth"}});
      }});
      li.appendChild(a); tol.appendChild(li);
    }});
    suivre();
  }};
  var attente = false;
  window.addEventListener("scroll", function () {{
    if (!attente) {{ attente = true; requestAnimationFrame(function () {{ attente = false; suivre(); }}); }}
  }}, {{passive: true}});
  window.addEventListener("resize", suivre);
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
