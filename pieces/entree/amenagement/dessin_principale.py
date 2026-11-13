"""Dessins de l'entrée, variante principale : plan vu de dessus, coupes, légende et styles des dessins.

Repris de 3d/entree/plan.py (qui reste en place jusqu'à la tâche 16). Le plan et les coupes sont des projections des
volumes du modèle : rien n'est dessiné à la main. Chaque fonction reçoit le module de variante `M` (document.py ou
victor.py) au lieu de le lire dans une variable globale. Le dessin ne change pas : tests/fixtures/entree/.

Calques du plan (classes des éléments SVG, sans groupe en plus) :
  cotes .dim .dimt | passages .pass .passm .passt | coupes .sec .sect | voisines .room .roomt | annotations .lblx .lbls
"""

from html import escape

from commun.dessin import coin_arrondi, cote_h, cote_v, degage, f, rect, rot, text, virg  # noqa: F401

COUPE_A = 60     # y, regard vers le nord : banc et tableau électrique
COUPE_B = 40     # x, regard vers l'est : meuble à chaussures, angle, flanc de la penderie
COUPE_C = 130    # y, regard vers le sud : penderie, angle, porte d'entrée au fond


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


# ------------------------------------------------------------------ plan vu de dessus
def plan_svg(M, aria="Plan de l'entrée aménagée"):
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
    return f'<svg class="plan" viewBox="-150 -130 595 560" role="img" aria-label="{escape(aria)}">{"".join(o)}</svg>'


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

    return coupe_svg(M, COUPE_B, "est", -20, 394, [M.BANC["z1"], c["z1"], mi["z0"], M.H_PORTE, mi["z1"]], extra=cotes, aria=aria)


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
              cote_h(*sorted((X(M.ANGLE["x0"]), X(M.ANGLE["x1"]))), 12, "25")]
        for x in pe["barres"]:
            r.append(f'<line class="inner" x1="{f(X(x))}" y1="{-pe["tringle"]}" x2="{f(X(x))}" y2="{-pe["tringle"] + 4}"/>')
        r += portes_vues(M, X, "s")
        return r

    return coupe_svg(M, COUPE_C, "sud", -20, 374, [M.CHAUSSURES["z1"], pe["tringle"], pe["etageres"][0], pe["z1"]], extra=cotes, aria=aria)



# Styles des dessins (le reste de la page vient de commun/site.css).
CSS = """
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


# ------------------------------------------------------------------ textes sous les dessins et principes
# Sujet de chaque coupe : nom de l'onglet « A mur nord » et titre de la fiche « Coupe A-A : mur nord ».
SUJETS = {"A": "mur nord", "B": "mur de la salle de bain", "C": "penderie"}


def legendes(M):
    """Texte long sous chaque dessin (ancienne légende de la page) : il devient l'aria-label du SVG."""
    c, mi, pe = M.CHAUSSURES, M.MIROIR, M.PENDERIE
    pp = pe["y1"] - pe["y0"]
    lp = pe["x1"] - pe["x0"]
    return {
        "plan": (f"Plan vu de dessus, 1 unité = 1 cm ; nord en haut. Le vantail de la porte d'entrée ouvert à 90° vient "
                 f"en butée contre le meuble à chaussures (②) : prévoir un butoir de sol. Avec {pp} cm de profondeur, la "
                 f"penderie reste au sud du vantail de la pièce ouest ouvert à 90° (il s'arrête à y 160, la penderie "
                 f"commence à y {pe['y0']}). Traits A, B, C : coupes."),
        "A": (f"Coupe à y {COUPE_A}, regard vers le nord : l'ouest est à gauche. Banc posé sous le tableau électrique "
              f"encastré, entre les portes de la cuisine (coulissante, côté cuisine) et du WC. Tableau dessiné au milieu "
              f"du trumeau, de {M.TABLEAU['z0']} à {M.TABLEAU['z1']} : position et taille à relever. À droite, le linteau "
              f"du passage vers le salon."),
        "B": (f"Coupe à x {COUPE_B}, regard vers l'est : le nord est à gauche. Le banc au fond à gauche, puis le flanc de "
              f"la penderie, l'angle arrondi à étagères ouvertes, le meuble à chaussures (deux modules de "
              f"{c['modules'][0][1] - c['modules'][0][0]}, deux abattants chacun) et son plateau vide-poche à "
              f"{c['z1'] + c['plateau']} ; au-dessus, le miroir {mi['y1'] - mi['y0']} × {mi['z1'] - mi['z0']} (coins "
              f"arrondis) et son applique, puis quatre patères en bois. En haut, le meuble haut ④ coupé (étagères au nord, "
              f"placard au sud). En jaune, la peinture India de l'entrée. Coupées : la porte coulissante de la cuisine à "
              f"gauche, la porte d'entrée à droite."),
        "C": (f"Coupe à y {COUPE_C}, regard vers le sud : l'est est à gauche. Au premier plan à droite, les étagères du "
              f"meuble haut ④, dessous à {M.MEUBLE_HAUT['z0']}. Penderie IKEA PAX de {lp} (caisson {pe['z1']} de haut, "
              f"bandeau jusqu'au plafond), portes de {pe['portes'][0]} et {pe['portes'][1]} ; dedans, tringle KOMPLEMENT à "
              f"{pe['tringle']} (deux barres d'avant en arrière, cintres de face), tablettes à {pe['etageres'][0]} et "
              f"{pe['etageres'][1]}, étagères à chaussures en bas. À droite, l'angle arrondi devant le meuble à chaussures, "
              f"la porte d'entrée au fond. Coupées : la porte de la chambre à gauche, celle de la pièce ouest à droite."),
    }


def principes(M):
    """Les cartes « Principe » : liste de (titre, texte HTML). Le rang est celui de `ZONES[i]["principe"]`."""
    b, c, an, pe, mi, mh = M.BANC, M.CHAUSSURES, M.ANGLE, M.PENDERIE, M.MIROIR, M.MEUBLE_HAUT
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
         f'Le long de la cloison de la salle de bain, {lc} cm de long et {pc} de profondeur seulement pour garder '
         f'{c["x0"]} cm de passage. Quatre abattants (environ {M.PAIRES} paires), plateau vide-poche pour les clés ; '
         f'au-dessus, miroir {mi["y1"] - mi["y0"]} × {mi["z1"] - mi["z0"]} et son applique, {len(M.PATERES)} patères en '
         f'bois au sud, côté porte (chevilles de chêne Ø {virg(M.PATERE["d"])}, à {M.PATERE["z"]}). Miroir à coins '
         f'arrondis (R {mi["r"]}). Il sert aussi de butée à la porte d\'entrée ouverte.'),
        ("③ Penderie PAX et angle arrondi",
         f'Contre la face nord de la salle de bain : une penderie IKEA PAX de {lp} × 35 × {pe["z1"]}, la seule largeur qui '
         "tienne dans les 84 cm du mur (un caisson de 100 mangerait l'huisserie de la salle de bain), et un bandeau "
         f'jusqu\'au plafond. Portes FORSAND de {pe["portes"][0]} et {pe["portes"][1]}. À 35 cm, les cintres ne tiennent '
         f'pas en travers : la tringle KOMPLEMENT de ce caisson a deux barres d\'avant en arrière, cintres de face '
         f'(environ {pe["manteaux"]} manteaux) ; deux tablettes au-dessus (bonnets, sacs), deux étagères à chaussures '
         f'dessous, une lampe à détecteur qui s\'allume à l\'ouverture. Le meuble à chaussures se prolonge jusqu\'au nu '
         f'de la penderie et s\'y termine par un quart de cercle ouvert de rayon {an["r"]}, à {c["z1"]} de haut '
         f'(étagères pour les clés et le courrier) : pas d\'arête dans le passage. {banc_pend} cm restent entre le banc '
         "et la penderie fermée."),
        ("④ Meuble haut et entrée en India",
         f'Suspendu au plafond en travers de la branche d\'entrée, du mur ouest à la cloison de la salle de bain '
         f'({mh["x1"] - mh["x0"]} × {mh["y1"] - mh["y0"]}, {mh["z1"] - mh["z0"]} de haut, dessous à {mh["z0"]} comme le '
         f'haut des portes) : il fait comme un linteau qui marque l\'entrée. Côté couloir, étagères ouvertes '
         f'({mh["etagere"]} de profondeur, une tablette) ; côté porte d\'entrée, placard à deux portes de '
         f'{(mh["x1"] - mh["x0"]) // 2} (bonnets, gants, sacs). Fixé au plafond et aux deux murs qui le bordent. Au sud du '
         f'meuble, murs, plafond et porte d\'entrée (face intérieure) sont peints en {M.INDIA["nom"]}, ainsi que le flanc '
         "de la penderie qui prolonge l'angle arrondi : l'entrée devient une petite pièce de couleur, le reste du couloir "
         "reste blanc."),
        ("Porte de la pièce ouest",
         f'Elle ouvre dans le couloir. Ouverte à 90°, son vantail s\'arrête à y 160 ; la penderie commence à y '
         f'{pe["y0"]}. Elle peut donc s\'ouvrir normalement, sans gêner le passage.'),
    ]
