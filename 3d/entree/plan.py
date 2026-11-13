# Génère entree-amenagement.html (plan vu de dessus, coupes, vues 3D) depuis modele.py.
#
#   python3 3d/entree/plan.py            (just entree)
#
# Le plan et les coupes sont des projections des volumes du modèle : rien n'est dessiné à la main.

import base64
import json
import math
import os
import sys
from html import escape

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import modele as M  # noqa: E402
import plum  # noqa: E402

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
ANCRES = open(os.path.join(ROOT, "3d", "ancres.js"), encoding="utf-8").read()   # ancres communes des pages à sommaire

OUT = os.path.join(ROOT, "entree-amenagement.html")
CLE = "entree"            # préfixe des préférences mémorisées (localStorage)
DOSSIER_3D = "entree-3d"
# Recoloration des rendus : un pixel du rendu neutre qui vaut REF_MUR (valeur affichée d'un mur India bien éclairé,
# 0,78 à 0,83 selon les vues, mesurée sur les rendus neutres V4.8) prend exactement la teinte choisie ; les autres en
# proportion, canal par canal (ombres plus sombres, reflets plus clairs, teinte chaude des lampes gardée).
REF_MUR = 0.80

COUPE_A = 60     # y, regard vers le nord : banc et tableau électrique
COUPE_B = 40     # x, regard vers l'est : meuble à chaussures, angle, flanc de la penderie
COUPE_C = 130    # y, regard vers le sud : penderie, angle, porte d'entrée au fond


def virg(v, n=1):
    return f"{v:.{n}f}".replace(".", ",")


def f(v):
    return f"{round(v, 1):g}"


def rect(x0, y0, x1, y1, cls, rx=0):
    r = f' rx="{f(rx)}"' if rx else ""
    return f'<rect class="{cls}" x="{f(x0)}" y="{f(y0)}" width="{f(x1 - x0)}" height="{f(y1 - y0)}"{r}/>'


def text(x, y, s, cls="lbl", anchor="middle", extra=""):
    return f'<text class="{cls}" x="{f(x)}" y="{f(y)}" text-anchor="{anchor}"{extra}>{escape(s)}</text>'


def rot(x, y):
    return f' transform="rotate(-90 {f(x)} {f(y)})"'


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
        text(x - 2.5, ym, label, "dimt", extra=rot(x - 2.5, ym)),
    ])


def degage(a, b, label=None):
    """Passage libre entre deux points (trait vert), valeur au milieu."""
    d = math.dist(a, b)
    xm, ym = (a[0] + b[0]) / 2, (a[1] + b[1]) / 2
    vertical = abs(b[1] - a[1]) > abs(b[0] - a[0])
    t = text(xm - 3, ym, label or f"{d:.0f}", "passt", extra=rot(xm - 3, ym)) if vertical else text(xm, ym - 3, label or f"{d:.0f}", "passt")
    return (f'<line class="pass" x1="{f(a[0])}" y1="{f(a[1])}" x2="{f(b[0])}" y2="{f(b[1])}"/>'
            + "".join(f'<circle class="passm" cx="{f(p[0])}" cy="{f(p[1])}" r="1.3"/>' for p in (a, b)) + t)


def coin_arrondi(x0, x1, y0, y1, r, cls):
    """Rectangle vu de dessus, coin nord-ouest arrondi (quart de cercle de rayon r)."""
    return (f'<path class="{cls}" d="M{f(x1)} {f(y0)} L{f(x1)} {f(y1)} L{f(x0)} {f(y1)} L{f(x0)} {f(y0 + r)} '
            f'A{f(r)} {f(r)} 0 0 1 {f(x0 + r)} {f(y0)} Z"/>')


# ------------------------------------------------------------------ portes (plan)
def _porte(p):
    """Vantail ouvert à 90°, arc et zone de débattement ; porte coulissante ; passage sans porte."""
    a, b, face, mur = p["a"], p["b"], p["face"], p["mur"]
    piece_face = face + (M.EP if mur in "se" else -M.EP)
    o = []
    if p["type"] == "passage":
        x = face + M.EP / 2 + 11
        o.append(text(x, (a + b) / 2, "passage sans porte", "lblx muted", extra=rot(x, (a + b) / 2)))
        return o
    if p["type"] == "coulissante":
        o.append(rect(a, face - M.EP - 4, b, face - M.EP, "sleafc"))
        o.append(text((a + b) / 2, face - M.EP - 8, "porte coulissante côté cuisine", "lblx muted"))
        return o
    perp = face if p["vers"] == "couloir" else piece_face
    into = {"n": 1, "s": -1, "e": -1, "o": 1}[mur] * (1 if p["vers"] == "couloir" else -1)
    g, autre = (a, b) if p["gond"] == "a" else (b, a)
    L = b - a
    pt = (lambda along, d: (along, d)) if mur in "ns" else (lambda along, d: (d, along))
    H, P, Q = pt(g, perp), pt(autre, perp), pt(g, perp + into * L)
    cross = (P[0] - H[0]) * (Q[1] - H[1]) - (P[1] - H[1]) * (Q[0] - H[0])
    sw = 1 if cross > 0 else 0
    arc = f'A{f(L)} {f(L)} 0 0 {sw} {f(Q[0])} {f(Q[1])}'
    o.append(f'<path class="doorzone" d="M{f(H[0])} {f(H[1])} L{f(P[0])} {f(P[1])} {arc} Z"/>')
    o.append(f'<path class="doorarc" d="M{f(P[0])} {f(P[1])} {arc}"/>')
    o.append(f'<line class="doorleaf" x1="{f(H[0])}" y1="{f(H[1])}" x2="{f(Q[0])}" y2="{f(Q[1])}"/>')
    return o


def _jambages():
    """Traits fins aux bords des ouvertures, dans l'épaisseur de la cloison."""
    o = []
    for p in M.PORTES:
        d0, d1 = (p["face"], p["face"] + M.EP) if p["mur"] in "se" else (p["face"] - M.EP, p["face"])
        for s in (p["a"], p["b"]):
            if p["mur"] in "ns":
                o.append(f'<line class="app" x1="{f(s)}" y1="{f(d0)}" x2="{f(s)}" y2="{f(d1)}"/>')
            else:
                o.append(f'<line class="app" x1="{f(d0)}" y1="{f(s)}" x2="{f(d1)}" y2="{f(s)}"/>')
    return o


# ------------------------------------------------------------------ plan vu de dessus
def plan_svg():
    b, c, an, pe, mi = M.BANC, M.CHAUSSURES, M.ANGLE, M.PENDERIE, M.MIROIR
    o = []
    # pièces voisines
    for x0, y0, x1, y1, nom, tx, ty in ((-140, -120, 90, -10, "Cuisine", -25, -60), (150, -120, 274, -10, "WC", 212, -60),
                                        (274, -120, 434, 94, "Salon", 354, -40), (364, 104, 434, 264, "Chambre", 399, 240),
                                        (120, 218, 364, 384, "Salle de bain", 242, 300),
                                        (-140, -10, -10, 384, "Pièce ouest", -75, 230)):
        o.append(rect(x0, y0, x1, y1, "room"))
        o.append(text(tx, ty, nom, "roomt"))
    o.append(text(40, 405, "Palier", "roomt"))
    pts = " ".join(f"{f(x)},{f(y)}" for x, y in M.SOL)
    ca = M.CARRELAGE["taille"]
    o.append(f'<defs><pattern id="carreaux" width="{ca}" height="{ca}" patternUnits="userSpaceOnUse">'
             f'<rect class="carreau" width="{ca}" height="{ca}"/></pattern></defs>')
    o.append(f'<polygon class="floorbg" points="{pts}"/><polygon fill="url(#carreaux)" points="{pts}"/>')
    for m in M.MURS:
        o.append(rect(m.x0, m.y0, m.x1, m.y1, "w"))
    o += _jambages()
    for p in M.PORTES:
        o += _porte(p)
    o.append(text(39, 392, "porte d’entrée", "lbls muted"))
    # ① banc et tableau électrique
    o.append(rect(M.TABLEAU["x0"], -6, M.TABLEAU["x1"], 0, "tech"))
    o.append(rect(b["x0"], b["y0"], b["x1"], b["y1"], "cab"))
    xm = (b["x0"] + b["x1"]) / 2
    o.append(text(xm, 18.5, f'① Banc {b["x1"] - b["x0"]} × {b["y1"] - b["y0"]} · h {b["z1"]}', "lbls"))
    o.append(text(xm, 26.5, "sous le tableau électrique", "lbls"))
    # angle arrondi, meuble à chaussures, miroir, patères
    o.append(coin_arrondi(an["x0"], an["x1"], an["y0"], an["y1"], an["r"], "cab"))
    o.append(rect(c["x0"], c["y0"], c["x1"], c["y1"], "cab"))
    for y0, _ in c["modules"][1:]:
        o.append(f'<line class="app" x1="{c["x0"]}" y1="{y0}" x2="{c["x1"]}" y2="{y0}"/>')
    o.append(f'<line class="app" x1="{an["x0"]}" y1="{an["y1"]}" x2="{an["x1"]}" y2="{an["y1"]}"/>')
    o.append(rect(106.5, mi["y0"], 110, mi["y1"], "mirror"))
    ym = (c["y0"] + c["y1"]) / 2
    o.append(text(97.5, ym, f'② Chaussures {c["y1"] - c["y0"]} × {c["x1"] - c["x0"]} · h {c["z1"]}', "lbls", extra=rot(97.5, ym)))
    ymi = (mi["y0"] + mi["y1"]) / 2
    o.append(text(127, ymi, "← miroir au-dessus du meuble", "lblx muted", "start"))
    o.append(text(127, 345, "← 4 patères à droite du miroir", "lblx muted", "start"))
    for y in M.PATERES:
        o.append(f'<circle class="hook" cx="108" cy="{y}" r="1.6"/>')
    o.append(text(79, 218, "angle arrondi", "lblx muted", "end"))
    o.append(text(79, 225, f'étagères h {c["z1"]}', "lblx muted", "end"))
    it = M.INTERPHONE
    o.append(rect(0, it["y0"], 3, it["y1"], "facp"))
    o.append(text(6, (it["y0"] + it["y1"]) / 2 + 2, "interphone", "lblx", "start"))
    cd = M.CADRES
    o.append(rect(0, cd["y0"], cd["ep"], cd["y1"], "dark"))
    o.append(text(6, (cd["y0"] + cd["y1"]) / 2 + 2, f'{cd["colonnes"] * cd["rangs"]} cadres', "lblx", "start"))
    # ③ penderie PAX : portes de 50 (ouest) et 25 (est), débattement en tireté ; barres de la tringle (cintres de face)
    o.append(rect(pe["x0"], pe["y0"], pe["x1"], pe["y1"], "tall"))
    l0, l1 = pe["portes"]
    xj = pe["x0"] + l0
    o.append(f'<line class="app" x1="{f(xj)}" y1="{pe["y0"]}" x2="{f(xj)}" y2="{pe["y1"]}"/>')
    for x in pe["barres"]:
        o.append(f'<line class="inner" x1="{f(x)}" y1="{pe["y0"] + 4}" x2="{f(x)}" y2="{pe["y1"] - 4}"/>')
    o.append(f'<path class="swing" d="M{pe["x0"]} {pe["y0"] - l0} A{l0} {l0} 0 0 1 {f(xj)} {pe["y0"]}"/>')
    o.append(f'<path class="swing" d="M{pe["x1"]} {pe["y0"] - l1} A{l1} {l1} 0 0 0 {f(xj)} {pe["y0"]}"/>')
    xp = (pe["x0"] + pe["x1"]) / 2
    o.append(text(xp, 187, f'③ Penderie PAX {pe["x1"] - pe["x0"]} × 35', "lblx"))
    o.append(text(xp, 194, f'h {pe["z1"]} + bandeau · cintres de face', "lblx"))
    # ④ meuble haut (au plafond, tireté) et peinture India (bande le long des murs peints, porte d'entrée)
    mh = M.MEUBLE_HAUT
    yd = mh["y0"] + mh["etagere"]
    o.append(rect(mh["x0"], mh["y0"], mh["x1"], mh["y1"], "upperh"))
    o.append(f'<line class="upper" x1="{mh["x0"]}" y1="{yd}" x2="{mh["x1"]}" y2="{yd}"/>')
    o.append(text(42, mh["y0"] + 9, "④ meuble haut au plafond", "lblx"))
    o.append(text(42, mh["y1"] - 4, f'étagères ↑ · placard ↓ · dessous à {mh["z0"]}', "lblx muted"))
    yi = M.INDIA["y0"]
    for x0, y0, x1, y1 in ((0, yi, 2.5, 374), (107.5, pe["y1"], 110, 374), (0, 371.5, 110, 374)):
        o.append(rect(x0, y0, x1, y1, "indiap"))
    o.append(rect(2, 374, 77, 376, "indiap"))
    o.append(rect(107.5, pe["y0"], 110, pe["y1"], "indiap"))   # flanc de la penderie
    o.append(text(127, 365, "■ murs, plafond, porte et flanc de penderie en India", "lblx india-t", "start"))
    # passages, cotes, traits de coupe
    for d in M.PASSAGES:
        o.append(degage(d["a"], d["b"], d["label"]))
    o.append(cote_h(0, 264, -28))
    o.append(cote_h(0, 110, 424))
    o.append(cote_v(0, 374, -48))
    o.append(cote_h(110, 354, 232))
    o.append(f'<line class="sec" x1="-6" y1="{COUPE_A}" x2="270" y2="{COUPE_A}"/>')
    o.append(text(-8, COUPE_A + 4, "A", "sect", "end"))
    o.append(f'<line class="sec" x1="{COUPE_B}" y1="-6" x2="{COUPE_B}" y2="380"/>')
    o.append(text(COUPE_B + 7, 368, "B", "sect", "start"))
    o.append(f'<line class="sec" x1="-6" y1="{COUPE_C}" x2="360" y2="{COUPE_C}"/>')
    o.append(text(-8, COUPE_C + 4, "C", "sect", "end"))
    return f'<svg viewBox="-150 -130 595 560" role="img" aria-label="Plan de l\'entrée aménagée">{"".join(o)}</svg>'


# ------------------------------------------------------------------ coupes
COUPE_CLS = {"mur": ("bgwall", "w"), "linteau": ("wallv", "w"), "porte": ("porte", "portec"), "tableau": ("tech", "tech"),
             "banc": ("cab", "cabc"), "angle": ("cab", "cabc"), "caisson": ("cab", "cabc"), "plateau": ("tbl", "tbl"),
             "tall": ("tall", "tallc"), "socle": ("dark", "dark"), "miroir": ("mirror", "mirror"),
             "applique": ("lamp", "lamp"), "patere": ("tbl", "tbl"), "facade": ("fac", "fac"), "facade_p": ("facp", "facp"),
             "haut": ("cab", "cabc"), "facade_h": ("fac", "fac"), "india": ("india", "india"),
             "india_plafond": ("india", "india"), "india_l": ("india", "india"), "interphone": ("facp", "facp"), "cadre_mur": ("dark", "dark")}

# (axe coupé, sens du regard, miroir de l'axe horizontal)
REGARDS = {"nord": ("y", -1, False), "sud": ("y", 1, True), "est": ("x", 1, False), "ouest": ("x", -1, True)}
VERS = {"nord": "le nord", "sud": "le sud", "est": "l'est", "ouest": "l'ouest"}


def uv(b, axe):
    return (b.x0, b.x1, b.y0, b.y1) if axe == "y" else (b.y0, b.y1, b.x0, b.x1)


def coupe_svg(cut, regard, umin, umax, hauteurs, extra=None):
    axe, sens, miroir = REGARDS[regard]
    X = (lambda u: umin + umax - u) if miroir else (lambda u: u)
    vus = []
    for b in M.ENVELOPPE + M.MEUBLES:
        u0, u1, d0, d1 = uv(b, axe)
        if (d1 > cut if sens > 0 else d0 < cut) and u1 > umin and u0 < umax:
            vus.append(b)
    vus.sort(key=lambda b: (uv(b, axe)[2] < cut < uv(b, axe)[3], -uv(b, axe)[2] if sens > 0 else uv(b, axe)[3]))
    o, etiq = [], {}
    for b in vus:
        u0, u1, d0, d1 = uv(b, axe)
        coupe = d0 < cut < d1
        u, v = sorted((X(max(u0, umin)), X(min(u1, umax))))
        cls = "india" if b.nom == "porte_entree" else COUPE_CLS[b.role][1 if coupe else 0]
        o.append(rect(u, -b.z1, v, -b.z0, cls, M.MIROIR["r"] if b.role == "miroir" and axe == "x" else 0))
        if b.etiq and v - u > 8:
            xm = (u + v) / 2
            etiq[(round(xm), round(b.z0 + b.z1))] = text(xm, -(b.z0 + b.z1) / 2 + 3, b.etiq, "lblb")
    o += etiq.values()
    if extra:
        o += extra(X)
    o.append(f'<line class="floorl" x1="{f(umin)}" y1="0" x2="{f(umax)}" y2="0"/>')
    o.append(f'<line class="ceil" x1="{f(umin)}" y1="{-M.H}" x2="{f(umax)}" y2="{-M.H}"/>')
    zs = [0] + hauteurs + [M.H]
    for z0, z1 in zip(zs, zs[1:]):
        o.append(cote_v(-z0, -z1, umin - 12))
    o.append(cote_v(0, -M.H, umin - 28))
    return (f'<svg viewBox="{f(umin - 44)} -270 {f(umax - umin + 70)} 300" role="img" '
            f'aria-label="Coupe à {axe} {f(cut)}, regard vers {VERS[regard]}">{"".join(o)}</svg>')


def portes_vues(X, mur, extra_txt=None):
    """Nom de la pièce sur chaque porte du mur vue de face."""
    r = []
    for p in M.PORTES:
        if p["mur"] == mur and p["type"] != "passage":
            u = X((p["a"] + p["b"]) / 2)
            r.append(text(u, -100, p["piece"].lower(), "lbls muted"))
    return r


def coupe_a():
    b, t = M.BANC, M.TABLEAU

    def cotes(X):
        u0, u1 = sorted((X(b["x0"]), X(b["x1"])))
        return portes_vues(X, "n") + [
            text((X(t["x0"]) + X(t["x1"])) / 2, -t["z1"] - 6, "position et taille à relever", "lblx muted"),
            cote_h(u0, u1, 12, f'banc {b["x1"] - b["x0"]}'),
            cote_h(87, 191, 22, "trumeau 104"),
        ]

    return coupe_svg(COUPE_A, "nord", -20, 284, [b["z1"], t["z0"], t["z1"], M.H_PORTE], extra=cotes)


def coupe_b():
    c, an, pe, mi = M.CHAUSSURES, M.ANGLE, M.PENDERIE, M.MIROIR

    def cotes(X):
        r = [cote_h(an["y0"], an["y1"], 12, f'angle {an["y1"] - an["y0"]}'),
             cote_h(c["y0"], c["y1"], 12, f'chaussures {c["y1"] - c["y0"]}'),
             text((mi["y0"] + mi["y1"]) / 2, -(mi["z0"] + mi["z1"]) / 2, f'miroir {mi["y1"] - mi["y0"]} × {mi["z1"] - mi["z0"]}', "lbls"),
             text((M.PATERES[0] + M.PATERES[-1]) / 2, -M.PATERE["z"] - 6, f'4 patères en bois h {M.PATERE["z"]}', "lblx muted"),
             text(M.APPLIQUE["y"] + 10, -M.APPLIQUE["z"] + 2, "applique", "lblx muted", "start"),
             text((c["y0"] + c["y1"]) / 2, -c["z1"] - 6, f'plateau vide-poche h {c["z1"] + c["plateau"]}', "lblx muted")]
        for z in an["etageres"]:
            r.append(f'<line class="app" x1="{an["y0"]}" y1="{-z}" x2="{an["y1"]}" y2="{-z}"/>')
        return r

    return coupe_svg(COUPE_B, "est", -20, 394, [M.BANC["z1"], c["z1"], mi["z0"], M.H_PORTE, mi["z1"]], extra=cotes)


def coupe_c():
    pe = M.PENDERIE

    def cotes(X):
        u0, u1 = sorted((X(pe["x0"]), X(pe["x1"])))
        xm = (u0 + u1) / 2
        r = [f'<line class="inner" x1="{f(u0 + 2)}" y1="{-z}" x2="{f(u1 - 2)}" y2="{-z}"/>'
             for z in (*pe["etageres"], *pe["chaussures"])]
        r += [text(xm, -pe["etageres"][1] - 3, f'tablettes {pe["etageres"][0]} / {pe["etageres"][1]}', "lblx muted"),
              text(xm, -pe["tringle"] + 8, f'tringle h {pe["tringle"]}', "lblx muted"),
              text(xm, -pe["chaussures"][1] - 3, "chaussures", "lblx muted"),
              f'<line class="app" x1="{f(u0)}" y1="{-pe["z1"]}" x2="{f(u1)}" y2="{-pe["z1"]}"/>',
              cote_h(u0, u1, 12, f'PAX {pe["x1"] - pe["x0"]}'),
              cote_h(*sorted((X(M.ANGLE["x0"]), X(M.ANGLE["x1"]))), 12, "25")]
        for x in pe["barres"]:
            r.append(f'<line class="inner" x1="{f(X(x))}" y1="{-pe["tringle"]}" x2="{f(X(x))}" y2="{-pe["tringle"] + 4}"/>')
        r += portes_vues(X, "s")
        return r

    return coupe_svg(COUPE_C, "sud", -20, 374, [M.CHAUSSURES["z1"], pe["tringle"], pe["etageres"][0], pe["z1"]], extra=cotes)


# ------------------------------------------------------------------ page
CSS = """
:root{
  --paper:#F7F8F6; --ink:#1D2A33; --muted:#5E6B73; --line:#C9D0D4; --wood:#B07A45;
  --water:#2F7FB5; --tri:#C8412C; --flow:#2E8B57; --panel:#FFFFFF; --cab:#ECE6DA; --tall:#D8CFBD;
  --tech:#E1E6E9; --glass:#CFE4F2; color-scheme:light; --india:#F5D58C;
}
@media (prefers-color-scheme: dark){
  :root:not([data-theme="light"]){
    --paper:#141A1F; --ink:#E4EAED; --muted:#9AA7AE; --line:#34414A; --wood:#C9925A;
    --water:#5AA8DE; --tri:#E8664F; --flow:#4CB97A; --panel:#1B2329; --cab:#2A3338; --tall:#394449;
    --tech:#26303A; --glass:#1F3A4E; color-scheme:dark;
  }
}
:root[data-theme="dark"]{
  --paper:#141A1F; --ink:#E4EAED; --muted:#9AA7AE; --line:#34414A; --wood:#C9925A;
  --water:#5AA8DE; --tri:#E8664F; --flow:#4CB97A; --panel:#1B2329; --cab:#2A3338; --tall:#394449;
  --tech:#26303A; --glass:#1F3A4E; color-scheme:dark;
}
*{box-sizing:border-box}
html,body{margin:0}
body{background:var(--paper);color:var(--ink);font-family:Archivo,system-ui,-apple-system,"Segoe UI",Roboto,sans-serif;line-height:1.55;font-size:16px}
.wrap{max-width:1120px;margin:0 auto;padding:28px 16px 64px}
.kicker{font-family:"JetBrains Mono",ui-monospace,Menlo,monospace;font-size:12px;letter-spacing:.08em;text-transform:uppercase;color:var(--muted)}
h1{font-size:clamp(28px,5vw,44px);line-height:1.08;margin:6px 0 12px;font-weight:800;letter-spacing:-.01em}
h2{font-size:22px;margin:44px 0 10px;font-weight:700}
h3{font-size:16px;margin:0 0 6px}
.pitch{font-size:18px;max-width:780px}
.stats{display:grid;grid-template-columns:repeat(auto-fit,minmax(170px,1fr));gap:12px;margin:22px 0 8px}
.stat{background:var(--panel);border:1px solid var(--line);border-radius:10px;padding:12px 14px}
.stat b{display:block;font-family:"JetBrains Mono",ui-monospace,monospace;font-size:24px;font-weight:600}
.stat span{font-size:13px;color:var(--muted)}
.fig{background:var(--panel);border:1px solid var(--line);border-radius:12px;padding:12px;margin:14px 0}
.scroll{overflow-x:auto}.scroll svg{display:block;width:100%;height:auto}
.scroll svg.plan{min-width:640px;max-width:900px;margin:0 auto}.scroll svg.coupe{min-width:480px;max-width:720px;margin:0 auto}
.cap{font-size:13px;color:var(--muted);margin:8px 4px 2px}
.note{font-size:13px;color:var(--muted)}
.grid2{display:grid;grid-template-columns:repeat(auto-fit,minmax(min(100%,300px),1fr));gap:16px}
.card{background:var(--panel);border:1px solid var(--line);border-radius:10px;padding:14px 16px}
.card p{margin:4px 0}
.legend{display:flex;flex-wrap:wrap;gap:8px 18px;font-size:13px;margin:10px 4px}
.legend span{display:inline-flex;align-items:center;gap:6px}
.legend svg{width:26px;height:14px;flex:none}
table{border-collapse:collapse;width:100%;font-size:14px}
th,td{text-align:left;padding:7px 8px;border-bottom:1px solid var(--line);vertical-align:top}
.mono{font-family:"JetBrains Mono",ui-monospace,monospace;white-space:nowrap}
ul.pistes{padding-left:20px;max-width:860px}ul.pistes li{margin:6px 0}
.rendu img{display:block;width:100%;height:auto;border-radius:8px}
.rendu figure{margin:0}
svg text{font-family:Archivo,system-ui,sans-serif;fill:var(--ink)}
.room{fill:var(--line);fill-opacity:.18}
.roomt{fill:var(--muted);font-size:9px;font-weight:600;text-anchor:middle}
.floorbg{fill:#D9D2C6;fill-opacity:.35}
.carreau{fill:none;stroke:#B5AC9C;stroke-width:.4;stroke-opacity:.7}
.w{fill:var(--ink)}
.bgwall{fill:var(--line);fill-opacity:.35}
.wallv{fill:#D5DADD;stroke:var(--muted);stroke-width:.5}
.app{stroke:var(--ink);stroke-width:.8;fill:none}
.cab{fill:var(--cab);stroke:var(--ink);stroke-width:.7}
.cabc{fill:var(--tall);stroke:var(--ink);stroke-width:1.2}
.tall{fill:var(--tall);stroke:var(--ink);stroke-width:.8}
.tallc{fill:var(--tall);stroke:var(--ink);stroke-width:1.4}
.fac{fill:var(--wood);fill-opacity:.35;stroke:var(--ink);stroke-width:.5}
.facp{fill:var(--panel);stroke:var(--ink);stroke-width:.6}
.tbl{fill:var(--wood);fill-opacity:.6;stroke:var(--ink);stroke-width:.6}
.tech{fill:var(--tech);stroke:var(--ink);stroke-width:.7;stroke-dasharray:3 2}
.dark{fill:var(--ink)}
.mirror{fill:var(--glass);stroke:var(--ink);stroke-width:.6}
.lamp{fill:#E8B44A;fill-opacity:.55;stroke:var(--ink);stroke-width:.6}
.hook{fill:var(--ink)}
.india{fill:var(--india);fill-opacity:.7;stroke:none}
.indiap{fill:var(--india);stroke:var(--ink);stroke-width:.3}
.india-t{fill:var(--ink);font-weight:700}
.upper{fill:none;stroke:var(--ink);stroke-width:.8;stroke-dasharray:3 2}
.upperh{fill:var(--wood);fill-opacity:.12;stroke:var(--ink);stroke-width:.8;stroke-dasharray:3 2}
.porte{fill:var(--panel);stroke:var(--ink);stroke-width:.6}
.portec{fill:var(--panel);stroke:var(--ink);stroke-width:1}
.inner{fill:none;stroke:var(--muted);stroke-width:.6;stroke-dasharray:3 2}
.doorzone{fill:var(--tri);fill-opacity:.06;stroke:none}
.doorarc{fill:none;stroke:var(--ink);stroke-width:.8}
.doorleaf{stroke:var(--ink);stroke-width:3}
.swing{fill:none;stroke:var(--muted);stroke-width:.6;stroke-dasharray:2 2}
.sleafc{fill:none;stroke:var(--ink);stroke-width:.8;stroke-dasharray:3 2}
.pass{stroke:var(--flow);stroke-width:.9}.passm{fill:var(--flow)}
.passt{fill:var(--flow);font-family:"JetBrains Mono",ui-monospace,monospace !important;font-size:7px;font-weight:600}
.dim{stroke:var(--muted);stroke-width:.6;fill:none}
.dimt{fill:var(--muted);font-family:"JetBrains Mono",ui-monospace,monospace !important;font-size:8px}
.lbl{font-size:7.5px}.lbls{font-size:6.5px}.lblx{font-size:5px}.lblb{font-size:8px;font-weight:700}
.muted{fill:var(--muted)}
.sec{stroke:var(--tri);stroke-opacity:.35;stroke-width:.9;stroke-dasharray:10 3 2 3;fill:none}
.sect{fill:var(--tri);fill-opacity:.6;font-weight:800;font-size:11px}
.floorl{stroke:var(--ink);stroke-width:2}
.ceil{stroke:var(--muted);stroke-width:1;stroke-dasharray:6 4}
body:not(.explications) .cap{display:none}
body:not(.changements) section[id^="changements"]{display:none}
.vbar{position:sticky;top:0;z-index:5;display:flex;flex-wrap:wrap;align-items:center;gap:6px;padding:8px 16px;background:var(--paper);border-bottom:1px solid var(--line);font-family:"JetBrains Mono",ui-monospace,monospace;font-size:12px}
.vbar button{font:inherit;color:var(--ink);background:var(--panel);border:1px solid var(--line);border-radius:6px;padding:4px 10px;cursor:pointer}
.vbar button[aria-pressed="true"]{background:var(--ink);color:var(--paper);border-color:var(--ink)}
.vbar .back{color:var(--ink);text-decoration:none;font-weight:600;margin-right:14px}
.vbar .back:hover{text-decoration:underline}
.vbar .expl{margin-left:auto}
.vbar .teinte i,.sw i{display:inline-block;width:12px;height:12px;border-radius:50%;background:var(--india);border:1px solid var(--line);vertical-align:-2px;margin-right:6px}
.palette{position:sticky;top:42px;z-index:5;background:var(--paper);border-bottom:1px solid var(--line);padding:10px 16px 12px;max-height:70vh;overflow-y:auto;font-size:13px}
.palette[hidden]{display:none}
.palette h4{margin:8px 0 6px;font:600 11px "JetBrains Mono",ui-monospace,monospace;text-transform:uppercase;letter-spacing:.08em;color:var(--muted)}
.palette .sws{display:flex;flex-wrap:wrap;gap:6px}
.sw{font:inherit;font-size:12px;color:var(--ink);background:var(--panel);border:1px solid var(--line);border-radius:14px;padding:3px 10px 3px 6px;cursor:pointer}
.sw i{background:var(--c);margin-right:5px}
.sw[aria-pressed="true"]{border-color:var(--ink);box-shadow:0 0 0 1px var(--ink)}
.palette .info{margin:4px 0 2px;color:var(--ink)}
.palette .info a{color:var(--ink)}
.teinte-fig{position:relative}
.teinte-calque{position:absolute;inset:0;width:100%;height:100%;filter:url(#plum-filtre);-webkit-mask-size:100% 100%;mask-size:100% 100%;pointer-events:none}
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
@media (max-width:480px){ body{font-size:15px} .stat b{font-size:21px} }
"""


def legende():
    items = [('<rect x="0" y="0" width="26" height="14" class="tall"/>', "Meuble toute hauteur"),
             ('<rect x="0" y="0" width="26" height="14" class="cab"/>', "Meuble bas, banc"),
             ('<rect x="1" y="1" width="24" height="12" class="tech"/>', "Tableau électrique encastré"),
             ('<rect x="1" y="5" width="24" height="4" class="mirror"/>', "Miroir"),
             ('<path d="M1 13 L1 1 A12 12 0 0 1 13 13Z" class="doorzone"/><path d="M1 1 A12 12 0 0 1 13 13" class="doorarc"/>',
              "Débattement des portes"),
             ('<rect x="1" y="1" width="24" height="12" class="upperh"/>', "Meuble haut (au plafond)"),
             ('<rect x="0" y="4" width="26" height="6" class="indiap"/>', 'Peint en <span class="teinte-nom">India</span>'),
             ('<line x1="1" y1="7" x2="25" y2="7" class="pass"/>', "Passage libre (cm)"),
             ('<rect x="0" y="0" width="26" height="14" class="room"/>', "Pièce voisine")]
    return '<div class="legend">' + "".join(f'<span><svg viewBox="0 0 26 14">{s}</svg>{t}</span>' for s, t in items) + "</div>"


NOTE_ISO = "Silhouette grise : 1,75 m, pour l'échelle (Human Base Meshes, Blender Studio, CC0). Murs du premier plan et plafond retirés ; portes fermées."
NOTE_PERSP = "Vue en perspective, yeux à 1,12 m (assis), plafond en place."


def galerie():
    """Rendus 3D présents dans entree-3d/ (just entree-rendu). Avec un masque <vue>-masque.png, les surfaces India du
    rendu (grises) sont recolorées dans la page : copie du rendu passée dans le filtre SVG #plum-filtre et découpée par
    le masque, intégré en base64 (les masques CSS d'un fichier voisin sont bloqués quand la page est ouverte en file://)."""
    figs = []
    recolore = False
    for v, titre in M.RENDUS:
        chemin = os.path.join(ROOT, DOSSIER_3D, f"{v}.jpg")
        if not os.path.exists(chemin):
            continue
        src = f"{DOSSIER_3D}/{v}.jpg?v={int(os.path.getmtime(chemin))}"
        masque = os.path.join(ROOT, DOSSIER_3D, f"{v}-masque.png")
        calque = ""
        if os.path.exists(masque):
            with open(masque, "rb") as fh:
                d = "url(data:image/png;base64," + base64.b64encode(fh.read()).decode() + ")"
            calque = f'<img class="teinte-calque" src="{src}" alt="" aria-hidden="true" style="-webkit-mask-image:{d};mask-image:{d}">'
            recolore = True
        figs.append(f'<div class="fig rendu"><figure class="teinte-fig"><img src="{src}" alt="{escape(titre)}" loading="lazy">{calque}</figure>'
                    f'<p class="note">{escape(titre)} · modèle {M.VERSION}. '
                    f'{NOTE_ISO if v.startswith("iso") else NOTE_PERSP}</p></div>')
    note = ('<p class="note">Surfaces India en <b class="teinte-nom">India</b> (bouton « Teinte » en haut de page) : rendu '
            'avec ces surfaces en gris neutre, recolorées dans la page : un mur bien éclairé prend la teinte affichée '
            'par Plum Living, les zones moins éclairées s\'assombrissent en proportion. Limite : la lumière que les murs '
            'colorés renvoient sur le blanc voisin (plafond du couloir, meubles) reste celle du gris.</p>') if recolore else ""
    return f'<h2>Vues 3D</h2>\n{note}{"".join(figs)}\n' if figs else ""


def palette():
    """Sélecteur de teinte (palette Plum Living, 3d/entree/plum.py) : panneau sous la barre, filtre SVG des rendus."""
    groupes = (("Laque et peinture murale", lambda c: c[3] and c[4]), ("Laque de façade seulement", lambda c: c[3] and not c[4]),
               ("Peinture murale seulement", lambda c: c[4] and not c[3]))
    blocs = []
    for titre, garde in groupes:
        sws = "".join(f'<button type="button" class="sw" data-code="{c[0]}" style="--c:{c[2]}" title="{escape(c[1])} · {c[2]}">'
                      f'<i></i>{escape(c[1])}</button>' for c in plum.PALETTE if garde(c))
        blocs.append(f'<h4>{titre}</h4><div class="sws">{sws}</div>')
    d = plum.PAR_CODE[plum.DEFAUT]
    fn = "".join(f'<feFunc{k} type="linear" slope="{int(d[2][1 + 2 * i:3 + 2 * i], 16) / 255 / REF_MUR:.4f}" intercept="0"/>'
                 for i, k in enumerate("RGB"))
    filtre = ('<svg width="0" height="0" style="position:absolute" aria-hidden="true"><filter id="plum-filtre" '
              f'color-interpolation-filters="sRGB"><feComponentTransfer>{fn}</feComponentTransfer></filter></svg>')
    donnees = json.dumps({c[0]: [c[1], c[2], c[3], c[4]] for c in plum.PALETTE}, ensure_ascii=False, separators=(",", ":"))
    panneau = (f'<div class="palette" hidden><p class="info"></p>{"".join(blocs)}'
               '<p class="note">Palette Plum Living relevée sur plum-living.com le 13/11/2026 (valeurs d\'écran, à voir sur '
               'échantillon). Toutes les surfaces India changent ensemble : murs, plafond, porte d\'entrée et meuble peint.</p></div>')
    return panneau, filtre, donnees, d


def contenu():
    b, c, an, pe, mi = M.BANC, M.CHAUSSURES, M.ANGLE, M.PENDERIE, M.MIROIR
    lignes = "".join(f'<tr><td class="mono">{v}</td><td class="mono">{dt}</td><td>{escape(x)}</td></tr>'
                     for v, dt, x in M.CHANGEMENTS)
    lb, pb = b["x1"] - b["x0"], b["y1"] - b["y0"]
    lc, pc = c["y1"] - c["y0"], c["x1"] - c["x0"]
    lp, pp = pe["x1"] - pe["x0"], pe["y1"] - pe["y0"]
    banc_pend = pe["y0"] - b["y1"]
    mh = M.MEUBLE_HAUT
    total = round(sum(q * p for _, _, q, p in M.IKEA))
    achats = "".join(f'<tr><td>{escape(n)}</td><td class="mono">{r}</td><td class="mono">{q}</td><td class="mono">{f'{q * p:g}'.replace('.', ',')} €</td></tr>'
                     for n, r, q, p in M.IKEA)
    portes = "".join(f'<tr><td>{escape(n)}</td><td class="mono">{p} €</td></tr>' for n, p in M.PORTES_PAX)
    return f"""<div class="kicker">Entrée · {M.VERSION}</div>
<h1>Aménagement de l'entrée</h1>
<p class="pitch">Le couloir ({virg(M.SURFACE)} m²) dessert cinq portes et le passage du salon : il faut ranger sans gêner. Un banc sous le tableau électrique, un meuble à chaussures étroit avec miroir dans la branche d'entrée, relié par un angle arrondi à une penderie face à la salle de bain. Un meuble suspendu au plafond marque l'entrée ; au-delà, murs, plafond et porte sont peints en India Yellow.</p>
<div class="stats"><div class="stat"><b>PAX {lp} × 35</b><span>penderie IKEA, ≈ {total} €</span></div><div class="stat"><b>≈ {M.PAIRES} paires</b><span>meuble à chaussures</span></div><div class="stat"><b>{c["x0"]} cm</b><span>passage le plus étroit</span></div><div class="stat"><b>{virg(M.SURFACE)} m²</b><span>surface du couloir</span></div></div>

<h2>Plan</h2>
<div class="fig"><div class="scroll">{plan_svg().replace("<svg ", '<svg class="plan" ', 1)}</div>
<p class="cap">Plan vu de dessus, 1 unité = 1 cm ; nord en haut. Le vantail de la porte d'entrée ouvert à 90° vient en butée contre le meuble à chaussures (②) : prévoir un butoir de sol. Avec {pp} cm de profondeur, la penderie reste au sud du vantail de la pièce ouest ouvert à 90° (il s'arrête à y 160, la penderie commence à y {pe["y0"]}). Traits A, B, C : coupes ci-dessous.</p>
{legende()}</div>

{galerie()}<h2>Coupe A-A · mur nord</h2>
<div class="fig"><div class="scroll">{coupe_a().replace("<svg ", '<svg class="coupe" ', 1)}</div>
<p class="cap">Coupe à y {COUPE_A}, regard vers le nord : l'ouest est à gauche. Banc posé sous le tableau électrique encastré, entre les portes de la cuisine (coulissante, côté cuisine) et du WC. Tableau dessiné au milieu du trumeau, de {M.TABLEAU["z0"]} à {M.TABLEAU["z1"]} : position et taille à relever. À droite, le linteau du passage vers le salon.</p></div>

<h2>Coupe B-B · mur de la salle de bain</h2>
<div class="fig"><div class="scroll">{coupe_b().replace("<svg ", '<svg class="coupe" ', 1)}</div>
<p class="cap">Coupe à x {COUPE_B}, regard vers l'est : le nord est à gauche. Le banc au fond à gauche, puis le flanc de la penderie, l'angle arrondi à étagères ouvertes, le meuble à chaussures (deux modules de {c["modules"][0][1] - c["modules"][0][0]}, deux abattants chacun) et son plateau vide-poche à {c["z1"] + c["plateau"]} ; au-dessus, le miroir {mi["y1"] - mi["y0"]} × {mi["z1"] - mi["z0"]} (coins arrondis) et son applique, puis quatre patères en bois. En haut, le meuble haut ④ coupé (étagères au nord, placard au sud). En jaune, la peinture India de l'entrée. Coupées : la porte coulissante de la cuisine à gauche, la porte d'entrée à droite.</p></div>

<h2>Coupe C-C · penderie</h2>
<div class="fig"><div class="scroll">{coupe_c().replace("<svg ", '<svg class="coupe" ', 1)}</div>
<p class="cap">Coupe à y {COUPE_C}, regard vers le sud : l'est est à gauche. Au premier plan à droite, les étagères du meuble haut ④, dessous à {M.MEUBLE_HAUT["z0"]}. Penderie IKEA PAX de {lp} (caisson {pe["z1"]} de haut, bandeau jusqu'au plafond), portes de {pe["portes"][0]} et {pe["portes"][1]} ; dedans, tringle KOMPLEMENT à {pe["tringle"]} (deux barres d'avant en arrière, cintres de face), tablettes à {pe["etageres"][0]} et {pe["etageres"][1]}, étagères à chaussures en bas. À droite, l'angle arrondi devant le meuble à chaussures, la porte d'entrée au fond. Coupées : la porte de la chambre à gauche, celle de la pièce ouest à droite.</p></div>

<h2>Principe</h2>
<div class="grid2">
<div class="card"><h3>① Banc sous le tableau électrique</h3><p>Un banc de {lb} × {pb} à {b["z1"]} de haut, posé (pas fixé dans la zone du tableau), dessous ouvert. Le tableau reste visible et à portée de main au-dessus : rien n'est rangé devant, ce que la NF C 15-100 interdit. On s'y assoit pour se chausser, face au meuble à chaussures.</p></div>
<div class="card"><h3>② Meuble à chaussures dans la branche d'entrée</h3><p>Le long de la cloison de la salle de bain, {lc} cm de long et {pc} de profondeur seulement pour garder {c["x0"]} cm de passage. Quatre abattants (environ {M.PAIRES} paires), plateau vide-poche pour les clés ; au-dessus, miroir {mi["y1"] - mi["y0"]} × {mi["z1"] - mi["z0"]} et son applique, {len(M.PATERES)} patères en bois au sud, côté porte (chevilles de chêne Ø {virg(M.PATERE["d"])}, à {M.PATERE["z"]}). Miroir à coins arrondis (R {mi["r"]}). Il sert aussi de butée à la porte d'entrée ouverte.</p></div>
<div class="card"><h3>③ Penderie PAX et angle arrondi</h3><p>Contre la face nord de la salle de bain : une penderie IKEA PAX de {lp} × 35 × {pe["z1"]}, la seule largeur qui tienne dans les 84 cm du mur (un caisson de 100 mangerait l'huisserie de la salle de bain), et un bandeau jusqu'au plafond. Portes FORSAND de {pe["portes"][0]} et {pe["portes"][1]}. À 35 cm, les cintres ne tiennent pas en travers : la tringle KOMPLEMENT de ce caisson a deux barres d'avant en arrière, cintres de face (environ {pe["manteaux"]} manteaux) ; deux tablettes au-dessus (bonnets, sacs), deux étagères à chaussures dessous, une lampe à détecteur qui s'allume à l'ouverture. Le meuble à chaussures se prolonge jusqu'au nu de la penderie et s'y termine par un quart de cercle ouvert de rayon {an["r"]}, à {c["z1"]} de haut (étagères pour les clés et le courrier) : pas d'arête dans le passage. {banc_pend} cm restent entre le banc et la penderie fermée.</p></div>
<div class="card"><h3>④ Meuble haut et entrée en India</h3><p>Suspendu au plafond en travers de la branche d'entrée, du mur ouest à la cloison de la salle de bain ({mh["x1"] - mh["x0"]} × {mh["y1"] - mh["y0"]}, {mh["z1"] - mh["z0"]} de haut, dessous à {mh["z0"]} comme le haut des portes) : il fait comme un linteau qui marque l'entrée. Côté couloir, étagères ouvertes ({mh["etagere"]} de profondeur, une tablette) ; côté porte d'entrée, placard à deux portes de {(mh["x1"] - mh["x0"]) // 2} (bonnets, gants, sacs). Fixé au plafond et aux deux murs qui le bordent. Au sud du meuble, murs, plafond et porte d'entrée (face intérieure) sont peints en {M.INDIA["nom"]}, ainsi que le flanc de la penderie qui prolonge l'angle arrondi : l'entrée devient une petite pièce de couleur, le reste du couloir reste blanc.</p></div>
<div class="card"><h3>Porte de la pièce ouest</h3><p>Elle ouvre dans le couloir. Ouverte à 90°, son vantail s'arrête à y 160 ; la penderie commence à y {pe["y0"]}. Elle peut donc s'ouvrir normalement, sans gêner le passage.</p></div>
</div>

<h2>Achats IKEA · penderie</h2>
<div class="fig"><table><thead><tr><th>Article</th><th>Référence</th><th>Qté</th><th>Prix</th></tr></thead><tbody>{achats}
<tr><td><b>Total</b></td><td></td><td></td><td class="mono"><b>≈ {total} €</b></td></tr></tbody></table>
<p class="note">Prix IKEA France relevés sur les fiches produit le 13/11/2026, en blanc ; les portes « avec charnières » comprennent leurs 4 charnières KOMPLEMENT à fermeture silencieuse. Les deux tablettes sont à retirer si le caisson en fournit (le guide d'achat PAX en annonce, la fiche française n'en parle pas). Bandeau (chute de mélaminé blanc) et fixation murale (fournie) non comptés.</p></div>
<div class="fig"><table><thead><tr><th>Portes pour ce caisson (avec charnières)</th><th>Prix</th></tr></thead><tbody>{portes}</tbody></table>
<p class="note">En 25 de large, IKEA ne fait que FORSAND, ÅHEIM (miroir) et FARDAL. Plum Living fait des portes de 37 pour PAX : deux portes égales au lieu de 50 + 25, dans toutes ses teintes ; pas de porte coulissante sur un seul caisson de 75.</p></div>

<h2>Matériaux</h2>
<div class="fig"><table><tbody>
<tr><td>Sol</td><td>Carrelage {M.CARRELAGE["nom"]}, pose droite, joints fins.</td></tr>
<tr><td>Murs</td><td>Blanc chaud, comme la cuisine et le salon ({M.MUR_COULEUR}) ; l'entrée, au sud du meuble haut : murs, plafond, porte et flanc ouest de la penderie en {M.INDIA["nom"]} ({M.INDIA["couleur"]}, valeur affichée par plum-living.com ; à voir sur échantillon).</td></tr>
<tr><td>Meubles</td><td>Proposition des rendus : banc, meuble à chaussures, angle, plateau et meuble haut en chêne miel (comme le salon) ; penderie PAX blanche (FORSAND), de la couleur des murs, pour qu'elle se fasse oublier ; son flanc ouest, dans l'entrée, en India. À choisir.</td></tr>
</tbody></table></div>

<h2>Points à vérifier</h2>
<ul class="pistes">
<li><b>Tableau électrique</b> : encastré entre la cuisine et le WC (indiqué par le client) ; sa position et sa hauteur sont à relever. Si ses commandes les plus basses sont sous 1 m, le banc gêne l'accès : le raccourcir ou le décaler.</li>
<li><b>Teinte India</b> : India de Plum Living (Beige 11) n'existe qu'en laque de façade : il n'est pas dans les 30 peintures murales de plum-living.com (relevé du 13/11/2026). Pour les murs, faire teinter une peinture à partir d'un échantillon, ou choisir une teinte qui existe dans les deux gammes (sélecteur « Teinte », premier groupe). Le flanc du PAX (mélaminé blanc) se peint après une sous-couche d'accrochage, ou se couvre d'un panneau de finition Plum Living 37 × 236 (218 €).</li>
<li><b>PAX</b> : 9 cm restent libres à l'est du caisson, avant l'huisserie de la salle de bain ; caisson fixé au mur de la salle de bain (vérifier la nature de la cloison). Hauteur sous plafond d'au moins 237 pour le monter debout.</li>
<li><b>Cadres</b> : galerie de {M.CADRES["colonnes"] * M.CADRES["rangs"]} cadres {M.CADRES["l"]} × {M.CADRES["h"]} sur le mur ouest de l'entrée (grille {M.CADRES["colonnes"]} × {M.CADRES["rangs"]}, {M.CADRES["ecart"]} d'écart, centre à {M.CADRES["zc"]}), entre le meuble haut et l'interphone ; ils ne dépassent que de {virg(M.CADRES["ep"])} dans le passage.</li>
<li><b>Interphone</b> : au mur ouest, à droite de la porte d'entrée vue de l'intérieur ; dessiné à {M.INTERPHONE["y0"]} du mur nord, haut à {M.INTERPHONE["z1"]} : position et taille à relever.</li>
<li><b>Meuble haut</b> : vérifier qu'il n'y a ni spot, ni détecteur, ni bouche d'aération au plafond à cet endroit, et la nature des deux murs pour les fixations.</li>
<li><b>Sens de la porte d'entrée</b> : sur le relevé, les paumelles sont à droite (côté salle de bain) et la porte ouvre vers l'intérieur. Si elles sont à gauche, le vantail se range contre le mur ouest.</li>
<li><b>Portes du mur nord</b> : la gauche est celle de la cuisine (coulissante côté cuisine), la droite celle du WC, d'après le plan du salon.</li>
<li><b>Hauteur sous plafond</b> : {M.H}, reprise de la salle de bain ; le salon a été relevé à 254,5.</li>
<li><b>Passage du salon</b> : {M.PORTES[2]["b"] - M.PORTES[2]["a"]} de large sur ce relevé, 82 sur le relevé du salon (V4.12) : à remesurer.</li>
</ul>

<p class="note">Repère : x vers l'est depuis le mur ouest du couloir, y vers le sud depuis son mur nord, z depuis le sol fini, en cm. Source : <span class="mono">3d/entree/modele.py</span> ; page : <span class="mono">3d/entree/plan.py</span> (<span class="mono">just entree</span>) ; vues 3D : <span class="mono">3d/entree/rendu.py</span> (<span class="mono">just entree-rendu</span>).</p>

<section id="changements">
<h2>Changements</h2>
<div class="scroll"><table><thead><tr><th>Version</th><th>Date</th><th>Changements</th></tr></thead>
<tbody>{lignes}</tbody></table></div>
</section>
"""


def page():
    panneau, filtre, donnees, defaut = palette()
    barre = ('<div class="vbar"><a class="back" href="index.html">← Plans</a>'
             f'<button type="button" class="teinte" aria-expanded="false" title="Teinte des surfaces India (Plum Living)"><i></i>Teinte : <span class="teinte-nom">{escape(defaut[1])}</span></button>'
             '<button type="button" class="expl" aria-pressed="false">Explications</button>'
             '<button type="button" class="chg" aria-pressed="false">Changements</button></div>')
    return f"""<!doctype html>
<html lang="fr">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Aménagement de l'entrée</title>
<link rel="icon" href="favicon.svg" type="image/svg+xml">
<link rel="apple-touch-icon" href="apple-touch-icon.png">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Archivo:wght@400;500;700;800&family=JetBrains+Mono:wght@400;600&display=swap" rel="stylesheet">
<style>{CSS}</style>
</head>
<body>
{barre}
{panneau}
{filtre}
<nav class="toc" aria-label="Sommaire"><button type="button" class="tbtn" aria-expanded="true">Sommaire</button><ol></ol></nav>
<main class="wrap">
{contenu()}
</main>
<script>{ANCRES}</script>
<script>
(function () {{
  function garde(k, v) {{ try {{ localStorage.setItem("{CLE}-" + k, v); }} catch (e) {{}} }}
  function lit(k) {{ try {{ return localStorage.getItem("{CLE}-" + k); }} catch (e) {{ return null; }} }}
  function bascule(sel, cls) {{
    var b = document.querySelector(sel);
    function pose(on) {{ document.body.classList.toggle(cls, on); b.setAttribute("aria-pressed", on); garde(cls, on ? "1" : ""); }}
    b.addEventListener("click", function () {{ pose(b.getAttribute("aria-pressed") !== "true"); }});
    pose(lit(cls) === "1");
  }}
  bascule(".vbar .expl", "explications");
  bascule(".vbar .chg", "changements");
  // teinte des surfaces India : palette Plum Living, partagée entre les pages de l'entrée
  var TEINTES = {donnees}, REF = {REF_MUR}, DEFAUT = "{plum.DEFAUT}";
  var pal = document.querySelector(".palette"), bt = document.querySelector(".vbar .teinte");
  var fonctions = document.querySelectorAll("#plum-filtre feComponentTransfer > *");
  document.querySelectorAll(".india-t").forEach(function (t) {{ t.dataset.base = t.textContent; }});
  function teinte(code) {{
    var t = TEINTES[code];
    if (!t) {{ code = DEFAUT; t = TEINTES[code]; }}
    document.documentElement.style.setProperty("--india", t[1]);
    fonctions.forEach(function (fn, i) {{ fn.setAttribute("slope", (parseInt(t[1].substr(1 + 2 * i, 2), 16) / 255 / REF).toFixed(4)); }});
    document.querySelectorAll(".teinte-nom").forEach(function (e) {{ e.textContent = t[0]; }});
    document.querySelectorAll(".india-t").forEach(function (e) {{ e.textContent = e.dataset.base.replace("India", t[0]); }});
    pal.querySelectorAll(".sw").forEach(function (b) {{ b.setAttribute("aria-pressed", b.dataset.code === code); }});
    var gammes = t[2] && t[3] ? "laque de façade et peinture murale" : t[2] ? "laque de façade seulement, pas de peinture murale de cette teinte (faire teinter les murs)" : "peinture murale seulement, pas de laque de façade";
    pal.querySelector(".info").innerHTML = "<b>" + t[0] + "</b> · " + t[1] + " · " + gammes +
      (t[3] ? ' · <a href="{plum.URL_PEINTURE}' + t[3] + '" target="_blank" rel="noopener">fiche peinture</a>' : "");
    try {{ localStorage.setItem("entree-teinte", code); }} catch (e) {{}}
  }}
  pal.addEventListener("click", function (e) {{ var b = e.target.closest(".sw"); if (b) teinte(b.dataset.code); }});
  function panneau(on) {{ pal.hidden = !on; bt.setAttribute("aria-expanded", on); }}
  bt.addEventListener("click", function () {{ panneau(pal.hidden); }});
  document.addEventListener("keydown", function (e) {{ if (e.key === "Escape") panneau(false); }});
  var lu = null;
  try {{ lu = localStorage.getItem("entree-teinte"); }} catch (e) {{}}
  teinte(lu || DEFAUT);
  // sommaire (ordinateur) : les titres h2, repliable, titre courant surligné
  var toc = document.querySelector(".toc"), tol = toc.querySelector("ol"), tb = toc.querySelector(".tbtn");
  var hs = Array.prototype.slice.call(document.querySelectorAll("main h2"));
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
  hs.forEach(function (h) {{
    var li = document.createElement("li"), a = document.createElement("a");
    a.href = "#" + h.id; a.textContent = h.textContent.trim();
    a.addEventListener("click", function (e) {{
      e.preventDefault();
      if (h.closest('section[id^="changements"]')) document.querySelector(".vbar .chg").getAttribute("aria-pressed") === "true" || document.querySelector(".vbar .chg").click();
      history.replaceState(null, "", "#" + h.id);
      h.scrollIntoView({{behavior: "smooth"}});
    }});
    li.appendChild(a); tol.appendChild(li);
  }});
  var attente = false;
  window.addEventListener("scroll", function () {{
    if (!attente) {{ attente = true; requestAnimationFrame(function () {{ attente = false; suivre(); }}); }}
  }}, {{passive: true}});
  window.addEventListener("resize", suivre);
  suivre();
}})();
</script>
</body>
</html>
"""


if __name__ == "__main__":
    with open(OUT, "w", encoding="utf-8") as fh:
        fh.write(page())
    print("Page :", OUT)
