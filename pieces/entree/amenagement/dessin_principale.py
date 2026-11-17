"""Dessins de l'entrée, variante principale : plan vu de dessus, coupes, légende et styles des dessins.

Repris de l'ancien générateur 3d/entree/plan.py (retiré à la bascule de l'entrée ; l'historique git le garde). Le plan
et les coupes sont des projections des volumes du modèle : rien n'est dessiné à la main. Chaque fonction reçoit le
module de variante `M` (document.py ou victor.py) au lieu de le lire dans une variable globale. Le dessin ne change
pas : tests/fixtures/entree/.

Calques du plan (classes des éléments SVG, sans groupe en plus) :
  cotes .dim .dimt | passages .pass .passm .passt | coupes .sec .sect | voisines .room .roomt | annotations .lblx .lbls
"""

import math
from html import escape

from commun.dessin import coin_arrondi, cote_h, cote_v, degage, f, rect, rot, text, virg  # noqa: F401

COUPE_A = 60     # y, regard vers le nord : banc et tableau électrique
COUPE_B = 40     # x, regard vers l'est : meuble à chaussures, angle, flanc de la penderie
COUPE_C = 130    # y, regard vers le sud : penderie, angle, porte d'entrée au fond
COUPE_D = 60     # x, regard vers l'ouest : mur ouest de l'entrée, cadres, miroir, interphone


def arrondi_svg(x0, x1, y0, y1, r, coins, cls):
    """Rectangle vu de dessus, coins ouest nommés dans `coins` (« no », « so ») en quart de cercle de rayon r."""
    d = f"M{f(x1)} {f(y0)} L{f(x1)} {f(y1)} "
    d += f"L{f(x0 + r)} {f(y1)} A{f(r)} {f(r)} 0 0 1 {f(x0)} {f(y1 - r)} " if "so" in coins else f"L{f(x0)} {f(y1)} "
    d += f"L{f(x0)} {f(y0 + r)} A{f(r)} {f(r)} 0 0 1 {f(x0 + r)} {f(y0)} " if "no" in coins else f"L{f(x0)} {f(y0)} "
    return f'<path class="{cls}" d="{d}Z"/>'


# ------------------------------------------------------------------ portes (plan)
def _porte(M, p):
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


def _jambages(M):
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


def _poly(pts, cls):
    return f'<polygon class="{cls}" fill="none" stroke="currentColor" points="{" ".join(f"{f(x)},{f(y)}" for x, y in pts)}"/>'


def _trait(pts, cls):
    return f'<polyline class="{cls}" fill="none" stroke="currentColor" points="{" ".join(f"{f(x)},{f(y)}" for x, y in pts)}"/>'


def _ouverture(M):
    """Porte d'entrée : béquille à 90°, débattement au-delà de 90° jusqu'au contact, vantail et béquille à l'angle maximal,
    jeu entre la béquille et le meuble à chaussures."""
    if not hasattr(M, "OUVERTURE"):
        return []
    ov, v = M.OUVERTURE, M.VANTAIL
    (px, py), l = v["pivot"], v["l"]
    a = math.radians(ov["max"])
    fin = (px - l * math.cos(a), py - l * math.sin(a))
    o = [f'<path class="swing" d="M{f(px)} {f(py - l)} A{f(l)} {f(l)} 0 0 1 {f(fin[0])} {f(fin[1])}"/>',
         _poly(M.vantail(ov["max"]), "leafmax"), _trait(M.bequille_trait(ov["max"]), "bqmax"),
         _trait(M.bequille_trait(90), "bq")]
    bx, by = M.bequille_trait(90)[2]
    o.append(text(bx - 10, by + 2, "béquille", "lblx muted", "end"))
    # jeu béquille ↔ bout du meuble : du coin de la béquille le plus proche au coin sud-ouest du meuble
    c = M.CHAUSSURES
    coin = min(M.bequille(90), key=lambda p: math.dist(p, (c["x0"], c["y1"])))
    o.append(degage(coin, (c["x0"], c["y1"]), f'{ov["jeu_meuble"]:.0f}'))
    o.append(text(127, 318, f'← porte d’entrée : {ov["max"]:.0f}° au plus, {ov["cause"]}', "lblx", "start"))
    o.append(text(127, 325, f'   butoir de sol à {ov["butoir"]}° ; à 90°, béquille à {ov["jeu_meuble"]:.0f} du meuble', "lblx muted", "start"))
    return o


# ------------------------------------------------------------------ plan vu de dessus
def plan_svg(M, aria="Plan de l'entrée aménagée", zones=""):
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
    o += _jambages(M)
    for p in M.PORTES:
        o += _porte(M, p)
    o += _ouverture(M)
    o.append(text(39, 392, "porte d’entrée", "lbls muted"))
    # ① banc et tableau électrique
    o.append(rect(M.TABLEAU["x0"], -6, M.TABLEAU["x1"], 0, "tech"))
    o.append(rect(b["x0"], b["y0"], b["x1"], b["y1"], "cab"))
    xm = (b["x0"] + b["x1"]) / 2
    o.append(text(xm, 18.5, f'① Banc {b["x1"] - b["x0"]} × {b["y1"] - b["y0"]}, h {b["z1"]}', "lbls"))
    o.append(text(xm, 26.5, "sous le tableau électrique", "lbls"))
    # meuble à chaussures (angle arrondi au nord, bout sud droit), plinthe en retrait (tireté), prise fibre, patères
    o.append(arrondi_svg(c["x0"], c["x1"], c["y0"], c["y1"], an["r"], "no", "cab"))
    rt = c["retrait"]
    o.append(arrondi_svg(c["x0"] + rt, c["x1"], c["y0"] + rt, c["y1"] - rt, an["r"] - rt, "no", "plinthe").replace("<path ", '<path fill="none" ', 1))
    o.append(f'<line class="app" x1="{c["x0"]}" y1="{c["ya"]}" x2="{c["x1"]}" y2="{c["ya"]}"/>')
    ym = (c["ya"] + c["yb"]) / 2
    o.append(text(97.5, ym, f'② Chaussures, h {c["z1"]}', "lbls", extra=rot(97.5, ym)))
    pf = M.PRISE_FIBRE
    o.append(rect(pf["x"] - 2, pf["y0"], pf["x"], pf["y1"], "tech"))
    o.append(text(127, (pf["y0"] + pf["y1"]) / 2 + 2, f'← prise fibre à {pf["axe"]} du sol, derrière le meuble', "lblx muted", "start"))
    o.append(text(127, 345, "← 4 patères, sol libre dessous", "lblx muted", "start"))
    for y in M.PATERES:
        o.append(f'<circle class="hook" cx="108" cy="{y}" r="1.6"/>')
    o.append(text(79, 218, "2 portes, 6 niveaux", "lblx muted", "end"))
    o.append(text(79, 225, "angle : colonne technique", "lblx muted", "end"))
    mh = M.MEUBLE_HAUT    # même emprise que le meuble à chaussures : seulement nommé
    o.append(text(79, 240, "meuble haut au-dessus,", "lblx muted", "end"))
    o.append(text(79, 247, f'{mh["z0"]} → {mh["z1"]} + fileur, 2 portes', "lblx muted", "end"))
    o.append(text(127, c["yb"] - 6, f'← plinthe {c["socle"]} en retrait de {rt} (tireté)', "lblx muted", "start"))
    it = M.INTERPHONE
    o.append(rect(0, it["y0"], 3, it["y1"], "facp"))
    o.append(text(6, (it["y0"] + it["y1"]) / 2 + 2, "interphone", "lblx", "start"))
    o.append(rect(0, mi["y0"], 2, mi["y1"], "mirror"))
    o.append(text(6, (mi["y0"] + mi["y1"]) / 2 + 2, f'miroir {mi["y1"] - mi["y0"]} × {mi["z1"] - mi["z0"]}', "lblx", "start"))
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
    o.append(text(xp, 187, f'③ Penderie PAX {pe["x1"] - pe["x0"]} × {pe["caisson"]}', "lblx"))
    o.append(text(xp, 194, f'h {pe["h"]} sur plinthe {pe["socle"]}, cintres de face', "lblx"))
    # peinture India (bande le long des murs peints, porte d'entrée)
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
    o.append(f'<line class="sec" x1="{COUPE_D}" y1="200" x2="{COUPE_D}" y2="380"/>')
    o.append(text(COUPE_D + 7, 368, "D", "sect", "start"))
    return f'<svg class="plan" viewBox="-150 -130 595 560" role="{"group" if zones else "img"}" aria-label="{escape(aria)}">{"".join(o)}{zones}</svg>'


# ------------------------------------------------------------------ coupes
COUPE_CLS = {"mur": ("bgwall", "w"), "linteau": ("wallv", "w"), "porte": ("porte", "portec"), "tableau": ("tech", "tech"),
             "banc": ("cab", "cabc"), "angle": ("cab", "cabc"), "caisson": ("cab", "cabc"), "plateau": ("tbl", "tbl"),
             "tall": ("tall", "tallc"), "socle": ("plv", "plc"), "miroir": ("mirror", "mirror"),
             "applique": ("lamp", "lamp"), "patere": ("tbl", "tbl"), "facade": ("fac", "fac"), "facade_p": ("facp", "facp"),
             "india": ("india", "india"),
             "india_plafond": ("india", "india"), "india_l": ("india", "india"), "interphone": ("facp", "facp"), "cadre_mur": ("dark", "dark"),
             "coussin": ("coussin", "coussin")}

# (axe coupé, sens du regard, miroir de l'axe horizontal)
REGARDS = {"nord": ("y", -1, False), "sud": ("y", 1, True), "est": ("x", 1, False), "ouest": ("x", -1, True)}
VERS = {"nord": "le nord", "sud": "le sud", "est": "l'est", "ouest": "l'ouest"}


def uv(b, axe):
    return (b.x0, b.x1, b.y0, b.y1) if axe == "y" else (b.y0, b.y1, b.x0, b.x1)


def coupe_svg(M, cut, regard, umin, umax, hauteurs, extra=None, aria=None, classes=None):
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
        cls = "india" if b.nom == "porte_entree" else (classes or COUPE_CLS)[b.role][1 if coupe else 0]
        o.append(rect(u, -b.z1, v, -b.z0, cls, M.MIROIR["r"] if b.role == "miroir" and axe == "x" else 0))
        if b.etiq and v - u > 8:
            xm = (u + v) / 2
            t = text(xm, -(b.z0 + b.z1) / 2 + 3, b.etiq, "lblb")
            etiq[(round(xm), round(b.z0 + b.z1))] = t
    o += etiq.values()
    if extra:
        o += extra(X)
    o.append(f'<line class="floorl" x1="{f(umin)}" y1="0" x2="{f(umax)}" y2="0"/>')
    o.append(f'<line class="ceil" x1="{f(umin)}" y1="{-M.H}" x2="{f(umax)}" y2="{-M.H}"/>')
    zs = [0] + hauteurs + [M.H]
    for z0, z1 in zip(zs, zs[1:]):
        o.append(cote_v(-z0, -z1, umin - 12))
    o.append(cote_v(0, -M.H, umin - 28))
    aria = aria or f"Coupe à {axe} {f(cut)}, regard vers {VERS[regard]}"
    return (f'<svg class="coupe" viewBox="{f(umin - 44)} -270 {f(umax - umin + 70)} 300" role="img" '
            f'aria-label="{escape(aria)}">{"".join(o)}</svg>')


def portes_vues(M, X, mur):
    """Nom de la pièce sur chaque porte du mur vue de face."""
    r = []
    for p in M.PORTES:
        if p["mur"] == mur and p["type"] != "passage":
            u = X((p["a"] + p["b"]) / 2)
            r.append(text(u, -100, p["piece"].lower(), "lbls muted"))
    return r


def coupe_a(M, aria=None):
    b, t = M.BANC, M.TABLEAU

    def cotes(X):
        u0, u1 = sorted((X(b["x0"]), X(b["x1"])))
        return portes_vues(M, X, "n") + [
            text((X(t["x0"]) + X(t["x1"])) / 2, -t["z1"] - 6, "position et taille à relever", "lblx muted"),
            cote_h(u0, u1, 12, f'banc {b["x1"] - b["x0"]}'),
            cote_h(87, 191, 22, "trumeau 104"),
        ]

    return coupe_svg(M, COUPE_A, "nord", -20, 284, [b["z1"], t["z0"], t["z1"], M.H_PORTE], extra=cotes, aria=aria)


def coupe_b(M, aria=None):
    c, an, pf = M.CHAUSSURES, M.ANGLE, M.PRISE_FIBRE

    def cotes(X):
        r = [cote_h(an["y0"], an["y1"], 12, f'angle {an["y1"] - an["y0"]}'),
             cote_h(c["ya"], c["yb"], 12, f'2 portes {c["yb"] - c["ya"]}'),
             *[f'<line class="inner" x1="{c["ya"] + 2}" y1="{-z}" x2="{c["yb"] - 2}" y2="{-z}"/>' for z in c["tablettes"]],
             text((c["ya"] + c["yb"]) / 2, -c["tablettes"][-1] - 3, "tablettes, chaussures en long", "lblx muted"),
             text((an["y0"] + an["y1"]) / 2, -c["z1"] + 10, "colonne", "lblx muted"),
             text((an["y0"] + an["y1"]) / 2, -c["z1"] + 16, "technique", "lblx muted"),
             text((an["y0"] + an["y1"]) / 2, -c["z1"] + 22, "(box)", "lblx muted"),
             cote_h(c["y0"], c["y1"], 22, f'meuble {c["y1"] - c["y0"]}'),
             text((M.PATERES[0] + M.PATERES[-1]) / 2, -M.PATERE["z"] - 6, f'4 patères en bois h {M.PATERE["z"]}', "lblx muted"),
             text(M.APPLIQUE["y"] + 10, -M.APPLIQUE["z"] + 2, "applique", "lblx muted", "start"),
             text((c["y0"] + c["y1"]) / 2, -c["z1"] - 6, f'plateau vide-poche h {c["z1"] + c["plateau"]}', "lblx muted"),
             text((c["y0"] + c["y1"]) / 2, -M.MEUBLE_HAUT["z0"] + 6, "2 portes de placard", "lblx muted"),
             rect(pf["y0"], -pf["z1"], pf["y1"], -pf["z0"], "tech"),
             text(pf["y1"] + 3, -pf["z1"] - 2, f'prise fibre h {pf["axe"]}, derrière → colonne technique', "lblx", "start"),
             text(c["yb"] + 3, -2, f'plinthe {c["socle"]}, retrait {c["retrait"]}', "lblx muted", "start")]
        return r

    return coupe_svg(M, COUPE_B, "est", -20, 394, [c["socle"], M.BANC["z1"], c["z1"], M.MEUBLE_HAUT["z0"], M.MEUBLE_HAUT["z1"]],   # patères aussi à 180
                     extra=cotes, aria=aria)


def coupe_c(M, aria=None):
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
              cote_h(*sorted((X(M.CHAUSSURES["x0"]), X(M.CHAUSSURES["x1"]))), 12, f'{M.CHAUSSURES["x1"] - M.CHAUSSURES["x0"]}')]
        for x in pe["barres"]:
            r.append(f'<line class="inner" x1="{f(X(x))}" y1="{-pe["tringle"]}" x2="{f(X(x))}" y2="{-pe["tringle"] + 4}"/>')
        r += portes_vues(M, X, "s")
        return r

    return coupe_svg(M, COUPE_C, "sud", -20, 374, [M.CHAUSSURES["z1"], pe["tringle"], pe["etageres"][0], pe["z1"]], extra=cotes, aria=aria)



def coupe_d(M, aria=None):
    cd, mi, it = M.CADRES, M.MIROIR, M.INTERPHONE

    def cotes(X):
        u0, u1 = sorted((X(cd["y0"]), X(cd["y1"])))
        v0, v1 = sorted((X(mi["y0"]), X(mi["y1"])))
        return [cote_h(u0, u1, 12, f'{cd["colonnes"]} × {cd["rangs"]} cadres {cd["l"]} × {cd["h"]}'),
                cote_h(v0, v1, 12, f'miroir {mi["y1"] - mi["y0"]}'),
                text((v0 + v1) / 2, -mi["z1"] - 4, f'miroir {mi["y1"] - mi["y0"]} × {mi["z1"] - mi["z0"]}', "lblx muted"),
                text(max(X(it["y0"]), X(it["y1"])), -it["z0"] + 8, "interphone", "lblx muted", "end")] + portes_vues(M, X, "o")

    return coupe_svg(M, COUPE_D, "ouest", 160, 394, [mi["z0"], cd["z0"], cd["z1"], mi["z1"]], extra=cotes, aria=aria)


# Styles des dessins (le reste de la page vient de commun/site.css).
CSS = """
.legend{display:flex;flex-wrap:wrap;gap:6px 14px;font-size:13.5px;margin:6px 0}
.legend span{display:inline-flex;align-items:center;gap:6px}
.legend svg{width:26px;height:14px;flex:none}
svg text{font-family:Archivo,system-ui,sans-serif;fill:var(--ink)}
.room{fill:var(--line);fill-opacity:.18}
.roomt{fill:var(--muted);font-size:9px;font-weight:600;text-anchor:middle}
.floorbg{fill:#D9D2C6;fill-opacity:.35}
.carreau{fill:none;stroke:#B5AC9C;stroke-width:.4;stroke-opacity:.7}
.w{fill:var(--ink)}
.bgwall{fill:var(--mur,var(--line));fill-opacity:.6}
.wallv{fill:#D5DADD;stroke:var(--muted);stroke-width:.5}
.app{stroke:var(--ink);stroke-width:.8;fill:none}
.cab{fill:var(--cab);stroke:var(--ink);stroke-width:.7}
.cabc{fill:var(--tall);stroke:var(--ink);stroke-width:1.2}
.tall{fill:var(--pax,var(--tall));stroke:var(--ink);stroke-width:.8}
.tallc{fill:var(--pax,var(--tall));stroke:var(--ink);stroke-width:1.4}
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
.porte{fill:var(--panel);stroke:var(--ink);stroke-width:.6}
.portec{fill:var(--panel);stroke:var(--ink);stroke-width:1}
.inner{fill:none;stroke:var(--muted);stroke-width:.6;stroke-dasharray:3 2}
.doorzone{fill:var(--tri);fill-opacity:.06;stroke:none}
.doorarc{fill:none;stroke:var(--ink);stroke-width:.8}
.doorleaf{stroke:var(--ink);stroke-width:3}
.slide{stroke:var(--ink);stroke-width:.8}
.coussin{fill:var(--coussin,#B4623F);stroke:var(--ink);stroke-width:.6}
.plv{fill:var(--plinthe,#EBE7E4);stroke:var(--ink);stroke-width:.6}.plc{fill:var(--plinthe,#EBE7E4);stroke:var(--ink);stroke-width:1.2}
.swing{fill:none;stroke:var(--muted);stroke-width:.6;stroke-dasharray:2 2}
.plinthe{fill:none;stroke:var(--muted);stroke-width:.5;stroke-dasharray:1.5 1.5}
.leafmax{fill:none;stroke:var(--ink);stroke-width:.6;stroke-dasharray:3 1.5}
.bq{fill:none;stroke:var(--ink);stroke-width:1.2;stroke-linecap:round;stroke-linejoin:round}
.bqmax{fill:none;stroke:var(--ink);stroke-width:.7;stroke-linecap:round;stroke-linejoin:round}
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
"""


def legende():
    items = [('<rect x="0" y="0" width="26" height="14" class="tall"/>', "Meuble toute hauteur"),
             ('<rect x="0" y="0" width="26" height="14" class="cab"/>', "Meuble bas, banc"),
             ('<rect x="1" y="1" width="24" height="12" class="tech"/>', "Tableau électrique encastré"),
             ('<rect x="1" y="5" width="24" height="4" class="mirror"/>', "Miroir"),
             ('<path d="M1 13 L1 1 A12 12 0 0 1 13 13Z" class="doorzone"/><path d="M1 1 A12 12 0 0 1 13 13" class="doorarc"/>',
              "Débattement des portes"),
             ('<rect x="0" y="4" width="26" height="6" class="indiap"/>', 'Peint en <span class="teinte-nom">India</span>'),
             ('<line x1="1" y1="7" x2="25" y2="7" class="pass"/>', "Passage libre (cm)"),
             ('<rect x="0" y="0" width="26" height="14" class="room"/>', "Pièce voisine")]
    return '<div class="legend">' + "".join(f'<span><svg viewBox="0 0 26 14">{s}</svg>{t}</span>' for s, t in items) + "</div>"


# ------------------------------------------------------------------ textes sous les dessins et principes
# Sujet de chaque coupe : nom de l'onglet « A mur nord » et titre de la fiche « Coupe A-A : mur nord ».
SUJETS = {"A": "mur nord", "B": "mur de la salle de bain", "C": "penderie", "D": "mur ouest de l'entrée"}


def legendes(M):
    """Texte long sous chaque dessin (ancienne légende de la page) : il devient l'aria-label du SVG."""
    c, mi, pe = M.CHAUSSURES, M.MIROIR, M.PENDERIE
    pp = pe["y1"] - pe["y0"]
    lp = pe["x1"] - pe["x0"]
    return {
        "plan": (f"Plan vu de dessus, 1 unité = 1 cm ; nord en haut. Le vantail de la porte d'entrée ouvert à 90° longe "
                 f"le sol libre sous les patères et s'arrête à côté de l'arrondi sud du meuble à chaussures (②) : prévoir "
                 f"un butoir de sol. La porte de la pièce ouest s'ouvre vers l'intérieur de cette pièce : rien ne dépasse "
                 f"dans le couloir. Du coin nord-est de la "
                 f"penderie au coin du mur qui sépare le salon du couloir et de la chambre : "
                 f"{M.PAX_MUR['d']:.0f} cm en diagonale. Traits A, B, C, D : coupes."),
        "A": (f"Coupe à y {COUPE_A}, regard vers le nord : l'ouest est à gauche. Banc posé sous le tableau électrique "
              f"encastré, entre les portes de la cuisine (coulissante, côté cuisine) et du WC. Tableau dessiné au milieu "
              f"du trumeau, de {M.TABLEAU['z0']} à {M.TABLEAU['z1']} : position et taille à relever. À droite, le linteau "
              f"du passage vers le salon."),
        "B": (f"Coupe à x {COUPE_B}, regard vers l'est : le nord est à gauche. Le banc au fond à gauche, puis le flanc de "
              f"la penderie, la colonne technique de l'angle arrondi (box), le meuble à chaussures (un module de "
              f"{c['yb'] - c['ya']} à deux portes, tablettes en tireté, sur une plinthe de {c['socle']}), sous un plateau "
              f"vide-poche à {c['z1'] + c['plateau']} ; la prise fibre, derrière le bas du module, câble vers la colonne. Puis le sol libre sous "
              f"les quatre patères en bois et leur applique. Au-dessus du meuble, de {M.MEUBLE_HAUT['z0']} à {M.MEUBLE_HAUT['z1']} puis un fileur jusqu'au plafond, le meuble "
              f"haut de même forme, à deux portes de placard. En jaune, la peinture India de l'entrée. Coupées : la porte coulissante de la cuisine à gauche, la "
              f"porte d'entrée à droite."),
        "C": (f"Coupe à y {COUPE_C}, regard vers le sud : l'est est à gauche. Penderie IKEA PAX de {lp} (caisson {pe['z1']} de haut, "
              f"bandeau jusqu'au plafond), portes de {pe['portes'][0]} et {pe['portes'][1]} ; dedans, tringle KOMPLEMENT à "
              f"{pe['tringle']} (deux barres d'avant en arrière, cintres de face), tablettes à {pe['etageres'][0]} et "
              f"{pe['etageres'][1]}, étagères à chaussures en bas. À droite, l'angle arrondi devant le meuble à chaussures, "
              f"la porte d'entrée au fond. Coupées : la porte de la chambre à gauche, celle de la pièce ouest à droite."),
        "D": (f"Coupe à x {COUPE_D}, regard vers l'ouest : le sud est à gauche. Le mur ouest de l'entrée, peint en India : "
              f"galerie de {M.CADRES['colonnes'] * M.CADRES['rangs']} cadres {M.CADRES['l']} × {M.CADRES['h']}, miroir {mi['y1'] - mi['y0']} × {mi['z1'] - mi['z0']} à coins arrondis, puis "
              f"l'interphone, {M.INTERPHONE['y0'] - mi['y1']} cm plus au sud."),
    }


def principes(M):
    """Les cartes « Principe » : liste de (titre, texte HTML). Le rang est celui de `ZONES[i]["principe"]`."""
    b, c, an, pe = M.BANC, M.CHAUSSURES, M.ANGLE, M.PENDERIE
    lb, pb = b["x1"] - b["x0"], b["y1"] - b["y0"]
    lc, pc = c["y1"] - c["y0"], c["x1"] - c["x0"]
    lp = pe["x1"] - pe["x0"]
    banc_pend = pe["y0"] - b["y1"]
    return [
        ("① Banc sous le tableau électrique",
         f'Un banc de {lb} × {pb} à {b["z1"]} de haut, posé (pas fixé dans la zone du tableau), dessous ouvert. Le tableau '
         "reste visible et à portée de main au-dessus : rien n'est rangé devant, ce que la NF C 15-100 interdit. On s'y "
         "assoit pour se chausser, face au meuble à chaussures."),
        ("② Meuble à chaussures dans la branche d'entrée",
         f'Le long de la cloison de la salle de bain, {lc} cm de long angle compris et {pc} de profondeur seulement '
         f'pour garder {c["x0"]} cm de passage. Un module de {c["yb"] - c["ya"]} fermé par deux portes battantes, avec '
         f'{len(c["tablettes"])} tablettes réglables : les chaussures y sont posées en long, la paire côte à côte dans '
         f'les 22 de profondeur, 2 à 3 paires par niveau et les bottines en bas (environ {M.PAIRES_MEUBLE} paires ; des '
         'abattants n\'en prendraient qu\'une rangée à cette profondeur), {c["z1"]} de haut, plateau vide-poche à {c["z1"] + c["plateau"]} pour les clés, sur une '
         f'plinthe de {c["socle"]} en retrait de {c["retrait"]} peinte comme le mur : le meuble flotte. L\'angle arrondi, '
         'au nord, est une colonne technique fermée (porte de 26 à poussoir) pour les box ; au sud, le meuble s\'arrête net pour laisser la porte d\'entrée s\'ouvrir : '
         f'à 90°, sa béquille passe à {M.OUVERTURE["jeu_meuble"]:.0f} cm du bout du meuble, et la porte va jusqu\'à '
         f'{M.OUVERTURE["max"]:.0f}°, où {M.OUVERTURE["cause"]} (butoir de sol à {M.OUVERTURE["butoir"]}°). Au-dessus, '
         f'de {M.MEUBLE_HAUT["z0"]} ({M.MEUBLE_HAUT["z0"] - c["z1"] - c["plateau"]} au-dessus du plateau) à {M.MEUBLE_HAUT["z1"]}, '
         'aligné sur le caisson de la PAX et surmonté d\'un fileur jusqu\'au plafond comme elle, un '
         'meuble haut de la même forme, angle plein compris, fermé par deux portes de placard battantes (bonnets, gants, '
         f'sacs). La prise fibre ({M.PRISE_FIBRE["axe"]} du sol, sur la cloison) est derrière '
         'le bas du module, côté nord : un passe-câble dans la joue mène la fibre à la colonne technique de l\'angle, '
         'où vont la box internet et, à terme, les box domotique (aération par la plinthe en retrait et sous le '
         'plateau ; prévoir une prise de courant dans la colonne). '
         f'Côté porte, le sol reste libre sous {len(M.PATERES)} patères en bois (chevilles de chêne Ø '
         f'{virg(M.PATERE["d"])}, à {M.PATERE["z"]}) et leur applique : 110 de passage pour entrer avec un sac.'),
        ("③ Penderie PAX et angle arrondi",
         f'Contre la face nord de la salle de bain : une penderie IKEA PAX de {lp} × {pe["caisson"]} × {pe["h"]}, posée sur une plinthe de {pe["socle"]} comme le meuble à chaussures, la seule largeur qui '
         "tienne dans les 84 cm du mur (un caisson de 100 mangerait l'huisserie de la salle de bain), et un bandeau "
         f'jusqu\'au plafond. Portes FORSAND de {pe["portes"][0]} et {pe["portes"][1]}. À 35 cm, les cintres ne tiennent '
         f'pas en travers : la tringle KOMPLEMENT de ce caisson a deux barres d\'avant en arrière, cintres de face '
         f'(environ {pe["manteaux"]} manteaux) ; deux tablettes au-dessus (bonnets, sacs), deux étagères à chaussures '
         f'dessous ({M.PAIRES_PAX} paires, 3 par étagère d\'après IKEA), une lampe à détecteur qui s\'allume à l\'ouverture. Le meuble à chaussures se prolonge jusqu\'au nu '
         f'de la penderie et s\'y termine par un quart de cercle de rayon {an["r"]}, à {c["z1"]} de haut, '
         'en chêne comme le meuble (la colonne technique) : pas d\'arête dans le passage. {banc_pend} cm restent entre le banc '
         "et la penderie fermée."),
        ("Entrée en India, couloir au choix",
         f'Au sud du nu de la penderie, murs, plafond et porte d\'entrée (face intérieure) sont peints en '
         f'{M.INDIA["nom"]}, ainsi que le flanc de la penderie qui prolonge l\'angle arrondi : l\'entrée devient une '
         "petite pièce de couleur. Le reste du couloir garde une teinte claire, Galet de Plum Living par défaut (la "
         "peinture murale la plus proche du blanc chaud de la cuisine et du salon), à choisir dans « Personnaliser »."),
    ]
