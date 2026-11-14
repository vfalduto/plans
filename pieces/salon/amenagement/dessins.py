"""Les dessins du salon/aménagement : le plan vu de dessus et les quatre coupes, projetés des volumes du modèle (rien
n'est dessiné à la main). Repris de 3d/salon/plan.py (`plan_svg`, `coupe_svg`, `coupe_a` à `coupe_d`), sur les aides de
pieces/salon/dessin.py, avec ces écarts seulement : pas de point médian (virgule), un seul SVG par coupe (les deux états
de la table, du siège et de la déco sont marqués de leur jeton `data-si` et non plus doublés en deux SVG), le texte sous
le dessin en aria-label (paramètre de l'appelant), les deux étiquettes fausses recalculées (voir plan_svg).

Les classes `cf co adyv achil dz` et les boutons de l'ancienne page n'existent plus : l'état de chaque option est
dessiné et marqué (`options.marque_bloc`), la page ne cache que ce que le jeton exclut.
"""
import math
from html import escape

from pieces.salon import piece
from pieces.salon.amenagement import document as M
from pieces.salon.amenagement import options as O
from pieces.salon.dessin import cote_h, cote_v, f, rect, text
from pieces.salon.meubles import cote

COUPE_A, COUPE_B, COUPE_C, COUPE_D = M.COUPE_A, M.COUPE_B, M.TABLE["cy"], M.COUPE_D


def _attr(s: str) -> str:
    return escape(s, quote=True)


def avec(element: str, attribut: str) -> str:
    """L'élément autofermant (`<rect …/>`) avec `attribut` (précédé d'une espace) avant `/>`."""
    return element[:-2] + attribut + "/>" if attribut else element


def degage(a, b, label=None, dt=(0, 0)):
    """Dégagement libre entre deux points (tireté rouge), valeur au milieu."""
    d = math.dist(a, b)
    xm, ym = (a[0] + b[0]) / 2 + dt[0], (a[1] + b[1]) / 2 + dt[1]
    return (f'<line class="pass" x1="{f(a[0])}" y1="{f(a[1])}" x2="{f(b[0])}" y2="{f(b[1])}"/>'
            + "".join(f'<circle class="passm" cx="{f(p[0])}" cy="{f(p[1])}" r="1.3"/>' for p in (a, b))
            + text(xm, ym, label or f"{d:.0f}", "passt"))


# ------------------------------------------------------------------ plan vu de dessus
PLAN_CLS = {"mur": "w", "linteau": None, "cadre": "cadrep", "baie": "win", "caisson": "cab", "facade": "fac",
            "pied": None, "etagere": "upper", "montant": "mont", "canape": "sofa", "table": "tbl", "chaise": None,
            "desserte": "cab", "vinyles": None, "platine": "dark", "lampe": "lampe", "volet": "dark",
            "table_basse": "tbl", "chilienne": "chil", "tapis": "tapisd", "lampe_pied": None, "plante": "plante",
            "pot": None, "cadre_mur": "cadrem", "livres": None, "fauteuil": "dyv", "projection": "proj",
            "projecteur": "projr", "clim": "clim", "papier_peint": None, "poutre": "poutre", "objet": None,
            "livre": None, "rideau": "rideau", "tringle": None}


def chaise_plan(x, y, a, cfg):
    """Chaise vue de dessus : assise 45 × 45 tournée, dossier côté extérieur."""
    h = M.CHAISE["l"] / 2
    return (f'<g transform="translate({f(x)} {f(y)}) rotate({f(a)})"{O.si(O.JETON_TABLE[cfg])}>'
            f'<rect class="stool" x="{f(-h)}" y="{f(-h)}" width="{f(2 * h)}" height="{f(2 * h)}" rx="4"/>'
            f'<rect class="stoold" x="{f(h - 5)}" y="{f(-h + 1)}" width="4" height="{f(2 * h - 2)}" rx="1.5"/></g>')


def volumes_plan():
    o = []
    for b in sorted(M.ENVELOPPE + M.MEUBLES, key=lambda b: b.z1):
        cls = PLAN_CLS[b.role]
        if not cls:
            continue
        marque = O.marque_bloc(b)
        if isinstance(b, piece.Cyl):
            o.append(f'<circle class="{cls}" cx="{f(b.cx)}" cy="{f(b.cy)}" r="{f(b.r)}"{marque}/>')
        elif b.role == "table":
            o.append(avec(rect(b.x0, b.y0, b.x1, b.y1, cls, M.TABLE["r"]), marque))
        elif b.role == "fauteuil":
            o.append(avec(rect(b.x0, b.y0, b.x1, b.y1, cls, 14), marque))
        elif b.role == "table_basse":
            o.append(avec(rect(b.x0, b.y0, b.x1, b.y1, cls, 6), marque))
        else:
            o.append(avec(rect(b.x0, b.y0, b.x1, b.y1, cls), marque))
    return o


def _vertical(x, y, s, cls):
    return text(x, y, s, cls, extra=f' transform="rotate(-90 {f(x)} {f(y)})"')


def libelles_plan():
    """Les étiquettes du plan et de ses calques : (texte « ② … » de l'enfilade, etc.) ; séparé pour être testé."""
    e = M.ENFILADE
    return {"enfilade": f'① Enfilade {cote(e["y1"] - e["y0"])} × {e["p"]}, h {e["z1"]}',
            "etageres": f"② {len(M.TABLETTES)} étagères suspendues au-dessus (tireté)",
            "desserte": "④ Desserte, platine vinyle",
            "ouverte": f'{M.CONFIGS["o"]["chaises"]} couverts, {M.TABLE["allonges"]} allonges de {cote(M.TABLE["allonge"])}',
            "quotidien": f'{M.CONFIGS["f"]["chaises"]} couverts'}


def plan_svg(aria: str, zones: str = "") -> str:
    """Le plan du salon ; `zones` (HTML des zones touchables) juste avant </svg>, role="group" alors."""
    e, c, d, t = M.ENFILADE, M.CANAPE, M.DESSERTE, M.TABLE
    pa, ba = piece.PASSAGE, piece.BAIE
    lib = libelles_plan()
    o = []
    # pièces voisines
    o.append(rect(-130, -12, -10, pa["y0"] - pa["cadre"], "room"))
    o.append(text(-70, 70, "Cellier", "roomt"))
    o.append(text(-70, 190, "WC", "roomt"))
    o.append(rect(-130, pa["y0"] - pa["cadre"], -10, M.P + 12, "room"))
    o.append(text(-70, 315, "Couloir", "roomt"))
    o.append(rect(M.L + M.EP, -12, M.L + 116, M.P + 12, "room"))
    o.append(text(M.L + 64, 330, "Pièce 1", "roomt"))
    o.append(rect(-10, M.P + 12, M.L + M.EP, M.P + 52, "room"))
    o.append(text(272, M.P + 38, "Chambre", "roomt"))
    sol = " ".join(f"{f(x)},{f(y)}" for x, y in piece.SOL)
    ca = M.CARRELAGE["taille"]
    o.append(f'<defs><pattern id="carreaux" width="{ca}" height="{ca}" patternUnits="userSpaceOnUse">'
             f'<rect class="carreau" width="{ca}" height="{ca}"/></pattern></defs>')
    o.append(f'<polygon class="floorbg" points="{sol}"/>')
    o.append(f'<polygon fill="url(#carreaux)" points="{sol}"/>')
    o += volumes_plan()
    # papier peint : bande sur la face du mur derrière la desserte
    o.append(rect(M.DECROCHE["x0"], M.DECROCHE["y"] - 2, M.L, M.DECROCHE["y"], "pp"))
    # baie coulissante : deux vantaux dans l'épaisseur du mur
    o.append(f'<line class="glass" x1="{M.L + 4}" y1="{ba["y0"]}" x2="{M.L + 4}" y2="{ba["milieu"] + 3}"/>')
    o.append(f'<line class="glass" x1="{M.L + 8}" y1="{ba["milieu"] - 3}" x2="{M.L + 8}" y2="{ba["y1"]}"/>')
    o.append(_vertical(M.L + 21, (ba["y0"] + ba["y1"]) / 2, f'baie {cote(ba["y1"] - ba["y0"])}', "lbls muted"))
    # passage sans porte
    o.append(f'<line class="seuil" x1="-10" y1="{pa["y0"]}" x2="-10" y2="{pa["y1"]}"/>')
    o.append(f'<line class="seuil" x1="0" y1="{pa["y0"]}" x2="0" y2="{pa["y1"]}"/>')
    o.append(_vertical(14, (pa["y0"] + pa["y1"]) / 2, f'passage {cote(pa["y1"] - pa["y0"])}', "lblx muted"))
    # enfilade : séparation des modules et des portes
    for y0, y1 in e["modules"][1:]:
        o.append(f'<line class="sep" x1="0" y1="{f(y0)}" x2="{f(e["p"])}" y2="{f(y0)}"/>')
    # chaises
    for cfg, lst in M.CHAISES.items():
        for x, y, a in lst:
            o.append(chaise_plan(x, y, a, cfg))
    # canapé : dossier et accoudoirs
    o.append(rect(c["x0"] + c["accoudoir"], 0, c["x1"] - c["accoudoir"], c["dossier"], "sofac"))
    for x0 in (c["x0"], c["x1"] - c["accoudoir"]):
        o.append(rect(x0, 0, x0 + c["accoudoir"], c["p"], "sofac"))
    # étiquettes
    ym = (e["y0"] + e["y1"]) / 2
    o.append(_vertical(22, ym, lib["enfilade"], "lbls"))
    o.append(_vertical(36, ym, lib["etageres"], "lblx"))
    for k, (y0, y1) in enumerate(e["modules"]):
        o.append(_vertical(9, (y0 + y1) / 2, f"M{k + 1}", "lblx muted"))
    xc = (c["x0"] + c["x1"]) / 2
    o.append(text(xc, 52, f'③ SÖDERHAMN {c["l"]} × {c["p"]}', "lbls"))
    xd = (d["x0"] + d["x1"]) / 2
    o.append(text(xd, d["y1"] + 9, lib["desserte"], "lbls"))
    rx, ry = t["ronde"]
    o.append(f'<g{O.si(O.QUOTIDIEN)}>{text(rx, ry - 10, "⑤ Table ronde Ø " + f(t["d"]), "lbls")}'
             f'{text(rx, ry - 3, lib["quotidien"], "lblx")}</g>')
    o.append(f'<g{O.si(O.OUVERTE)}>{text(t["cx"], t["cy"] - 14, "⑤ Table " + f(t["ouvert"]) + " × " + f(t["d"]), "lbls")}'
             f'{text(t["cx"], t["cy"] - 7, lib["ouverte"], "lblx")}</g>')
    tb, ch, dy, k = M.TABLE_BASSE, M.CHILIENNE, M.DYVLINGE, M.CONSOLE
    for cfg, (x0, y0, x1, y1) in tb["pos"].items():
        xm, ym = (x0 + x1) / 2, (y0 + y1) / 2
        rot = f' transform="rotate(-90 {f(xm)} {f(ym)})"' if y1 - y0 > x1 - x0 else ""
        o.append(f'<g{O.si(O.JETON_TABLE[cfg])}>{text(xm, ym + 2, "⑥ Table basse", "lblx", extra=rot)}</g>')
    for cfg, (x0, y0) in dy["pos"].items():
        o.append(f'<g{O.si(O.JETON_TABLE[cfg], O.DYVLINGE)}>'
                 f'{text(x0 + dy["p"] / 2 - 8, y0 + dy["l"] / 2 - 1, "⑦ DYVLINGE", "lblx")}'
                 f'{text(x0 + dy["p"] / 2 - 8, y0 + dy["l"] / 2 + 6, "pivotant", "lblx muted")}</g>')
    o.append(f'<g{O.si(O.QUOTIDIEN, O.CHILIENNE)}>{text(ch["x0"] + 50, ch["y0"] + ch["l"] / 2 + 2, "⑦ Chilienne", "lblx")}</g>')
    o.append(f'<g{O.si(O.OUVERTE, O.CHILIENNE)}>{text(60 + ch["l"] / 2, M.P - 18, "⑦ chilienne pliée", "lblx")}</g>')
    o.append(text((k["x0"] + k["x1"]) / 2, k["y0"] + 14, f'⑧ Meuble bas {k["l"]} × {k["p"]}', "lbls"))
    o.append(text((k["x0"] + k["x1"]) / 2, k["y0"] + 22,
                  f'écran au-dessus : image {cote(M.ECRAN["l"])} × {cote(M.ECRAN["h"])}', "lblx"))
    o.append(text((M.CLIM["x0"] + M.CLIM["x1"]) / 2, M.P - M.CLIM["p"] + 13, f'clim (h {cote(M.CLIM["z0"])})', "lblx"))
    o.append(text(360, M.P - 5, f'poutre au-dessus, dessous à {cote(M.POUTRE["z0"])}', "lblx muted"))
    pj = M.PROJECTEUR
    o.append(text(pj["cx"], pj["cy"] + pj["p"] / 2 + 7, "vidéoprojecteur (plafond)", "lblx"))
    # décoration
    dz = [text(M.TAPIS["x0"] + 6, M.TAPIS["y1"] - 4, "tapis", "lblx muted", "start"),
          text(M.LAMPADAIRE["cx"], M.LAMPADAIRE["cy"] + 2, "lampadaire", "lblx")]
    o.append(f'<g{O.si(O.AFFICHEE)}>{"".join(dz)}</g>')
    # cotes
    o.append(cote_h(0, M.L, -30))
    o.append(cote_v(0, M.P, -22))
    o.append(cote_h(c["x0"], c["x1"], -18, f'{c["l"]}'))
    o.append(cote_h(e["p"], c["x0"], -18, f'{M.ALLEE_ENFILADE}'))
    o.append(cote_h(0, e["p"], -18, f'{e["p"]}'))
    o.append(cote_v(e["y0"], e["y1"], -14 + 0, f'{cote(e["y1"] - e["y0"])} utiles'))
    o.append(cote_h(d["x0"], d["x1"], -18, f'{d["x1"] - d["x0"]}'))
    # dégagements
    lo = t["ouvert"]
    xo, xe = t["cx"] - lo / 2, t["cx"] + lo / 2
    xb, yb, _, yb1 = tb["pos"]["f"]
    o.append(f'<g{O.si(O.QUOTIDIEN)}>'
             + degage((xb + 15, c["p"]), (xb + 15, yb), dt=(6, 2))
             + degage((xb + 15, yb1), (xb + 15, k["y0"]), dt=(6, 2))
             + "</g>")
    xr = t["cx"] - 35
    o.append(f'<g{O.si(O.OUVERTE)}>'
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
    o.append(f'<line class="sec" x1="-6" y1="{f(COUPE_C)}" x2="{M.L + 6}" y2="{f(COUPE_C)}"/>')
    o.append(text(-4, COUPE_C - 5, "C", "sect", "end"))
    o.append(f'<line class="sec" x1="-6" y1="{COUPE_D}" x2="{M.L + 6}" y2="{COUPE_D}"/>')
    o.append(text(-4, COUPE_D - 5, "D", "sect", "end"))
    o.append(text(M.L + 4, COUPE_D - 5, "D", "sect", "start"))
    o.append(text(M.L + 4, COUPE_C - 5, "C", "sect", "start"))
    return (f'<svg viewBox="-150 -50 820 470" role="{"group" if zones else "img"}" aria-label="{_attr(aria)}">'
            f'{"".join(o)}{zones}</svg>')


# ------------------------------------------------------------------ coupes
COUPE_CLS = {"mur": ("bgwall", "w"), "linteau": ("wallv", "w"), "poutre": ("wallv", "w"), "cadre": ("cadrep", "cadrep"),
             "baie": ("vitre", "vitrec"), "caisson": ("cab", "cab"), "facade": ("fac", "fac"), "pied": ("dark", "dark"),
             "etagere": ("shelf", "shelfc"), "montant": ("mont", "mont"), "canape": ("sofa", "sofa"),
             "table": ("tbl", "tbl"), "chaise": ("stool", "stool"), "desserte": ("cab", "cab"),
             "vinyles": ("vinyl", "vinyl"), "platine": ("dark", "dark"), "lampe": ("lampe", "lampe"),
             "volet": ("tbl", "tbl"), "table_basse": ("tbl", "tbl"), "chilienne": ("chil", "chil"),
             "tapis": ("tapisd", "tapisd"), "lampe_pied": ("dark", "dark"), "plante": ("plante", "plante"),
             "pot": ("pot", "pot"), "cadre_mur": ("cadrem", "cadrem"), "livres": ("livre", "livre"),
             "fauteuil": ("dyv", "dyv"), "projection": ("proj", "proj"), "projecteur": ("dark", "dark"),
             "clim": ("clim", "clim"), "papier_peint": ("pp", "pp"), "objet": ("pot", "pot"),
             "livre": ("livre", "livre"), "rideau": ("rideau", "rideau"), "tringle": ("dark", "dark")}

# (axe coupé, sens du regard, miroir de l'axe horizontal)
REGARDS = {"nord": ("y", -1, False), "sud": ("y", 1, True), "est": ("x", 1, False), "ouest": ("x", -1, True)}
VERS = {"nord": "le nord", "sud": "le sud", "est": "l'est", "ouest": "l'ouest"}


def uv(b, axe):
    return (b.x0, b.x1, b.y0, b.y1) if axe == "y" else (b.y0, b.y1, b.x0, b.x1)


def visibles(cut, regard, umin, umax):
    """Les volumes vus d'une coupe, quel que soit l'état des options (chacun porte son jeton)."""
    axe, sens, _ = REGARDS[regard]
    r = []
    for b in M.ENVELOPPE + M.MEUBLES:
        u0, u1, d0, d1 = uv(b, axe)
        if (d1 > cut if sens > 0 else d0 < cut) and u1 > umin and u0 < umax:
            r.append(b)
    return r


def coupe_svg(cut, regard, umin, umax, hauteurs, aria, extra=None):
    axe, sens, miroir = REGARDS[regard]
    X = (lambda u: umin + umax - u) if miroir else (lambda u: u)
    vus = visibles(cut, regard, umin, umax)
    vus.sort(key=lambda b: (uv(b, axe)[2] < cut < uv(b, axe)[3], -uv(b, axe)[2] if sens > 0 else uv(b, axe)[3]))
    o, etiq = [], {}
    for b in vus:
        u0, u1, d0, d1 = uv(b, axe)
        coupe = d0 < cut < d1
        u, v = sorted((X(max(u0, umin)), X(min(u1, umax))))
        marque = O.marque_bloc(b)
        o.append(avec(rect(u, -b.z1, v, -b.z0, COUPE_CLS[b.role][1 if coupe else 0]), marque))
        xm = (u + v) / 2
        if b.role == "baie" and coupe:
            o.append(_vertical(xm + 7, -110, "baie", "lblx muted"))
        if b.etiq and v - u > 8:
            etiq[(round(xm), round(-(b.z0 + b.z1) / 2), marque)] = text(xm, -(b.z0 + b.z1) / 2 + 3, b.etiq, "lblb")
        if b.contenu and v - u > 20:
            zc = -(b.z1 - 8) if b.role == "facade" else -(b.z0 + b.z1) / 2 + 1
            etiq[(round(xm), round(zc), marque)] = text(xm, zc, b.contenu, "lblc")
    # une étiquette porte le jeton de son volume : celui des blocs qui la posent (marque de sa clé)
    o += [avec_g(t, marque) for (_, _, marque), t in etiq.items()]
    if extra:
        o += extra(X)
    o.append(f'<line class="floorl" x1="{f(umin)}" y1="0" x2="{f(umax)}" y2="0"/>')
    o.append(f'<line class="ceil" x1="{f(umin)}" y1="{-M.H}" x2="{f(umax)}" y2="{-M.H}"/>')
    zs = [0] + hauteurs + [M.H]
    for z0, z1 in zip(zs, zs[1:]):
        o.append(cote_v(-z0, -z1, umin - 12))
    o.append(cote_v(0, -M.H, umin - 28))
    return (f'<svg viewBox="{f(umin - 44)} -275 {f(umax - umin + 70)} 315" role="img" aria-label="{_attr(aria)}">'
            f'{"".join(o)}</svg>')


def avec_g(element: str, marque: str) -> str:
    """Un texte entouré de son `<g>` marqué, ou seul si rien ne le marque."""
    return f"<g{marque}>{element}</g>" if marque else element


def coupe_a(aria):
    e, et, mo = M.ENFILADE, M.ETAGERES, M.MONTANTS

    def cotes(X):
        u0, u1 = sorted((X(e["y0"]), X(e["y1"])))
        p0, p1 = sorted((X(piece.PASSAGE["y0"]), X(piece.PASSAGE["y1"])))
        r = [cote_h(u0, u1, 18, f'enfilade {cote(e["y1"] - e["y0"])}'),
             cote_h(p0, p1, 18, f'passage {cote(piece.PASSAGE["y1"] - piece.PASSAGE["y0"])}')]
        for y0, y1 in e["modules"]:
            a, b = sorted((X(y0), X(y1)))
            r.append(cote_h(a, b, 9, f(y1 - y0)))
        axes = sorted(X(y) for y in mo["axes"])
        for a, b in zip(axes, axes[1:]):
            r.append(cote_h(a, b, -(mo["z1"] + 7), f(mo["pas"])))
        return r

    return coupe_svg(COUPE_A, "ouest", -20, M.P + 20, [e["pieds"], e["z1"], mo["z0"]] + et["zs"] + [mo["z1"]], aria,
                     extra=cotes)


def coupe_b(aria):
    d, b = M.DESSERTE, piece.BAIE

    def cotes(X):
        u0, u1 = sorted((X(d["y0"]), X(d["y1"])))
        b0, b1 = sorted((X(b["y0"]), X(b["y1"])))
        m = X(b["milieu"])
        return [cote_h(u0, u1, 18, f'desserte {cote(d["y1"] - d["y0"])}'), cote_h(b0, b1, -b["h"] - 6, f'baie {cote(b["y1"] - b["y0"])}'),
                f'<line class="seuil" x1="{f(m)}" y1="0" x2="{f(m)}" y2="{-b["h"]}"/>',
                text((b0 + m) / 2 if X(b["y0"]) < m else (m + b1) / 2, -b["h"] + 10, "vantail nord", "lblx muted"),
                text((m + b1) / 2 if X(b["y0"]) < m else (b0 + m) / 2, -b["h"] + 10, "vantail sud", "lblx muted")]

    return coupe_svg(COUPE_B, "est", -20, M.P + 20, [d["niveaux"][1], d["z1"], d["z1"] + 14, b["h"]], aria, extra=cotes)


def coupe_c(aria):
    e, c, t = M.ENFILADE, M.CANAPE, M.TABLE

    def cotes(X):
        return [cote_h(0, e["p"], 18), cote_h(c["x0"], c["x1"], 18, f'canapé {c["l"]}')]

    return coupe_svg(COUPE_C, "nord", -20, M.L + 20, [c["assise"], t["z1"], e["z1"], M.SUSPENSION["z0"]], aria,
                     extra=cotes)


def coupe_d(aria):
    k, ec, cl = M.CONSOLE, M.ECRAN, M.CLIM

    def cotes(X):
        u0, u1 = sorted((X(ec["x0"]), X(ec["x1"])))
        k0, k1 = sorted((X(k["x0"]), X(k["x1"])))
        c0, c1 = sorted((X(cl["x0"]), X(cl["x1"])))
        return [cote_h(k0, k1, 18, f'meuble bas {k["l"]}'),
                cote_h(u0, u1, -(ec["bas"] + ec["h"]) - 6, f'image {cote(ec["l"])} × {cote(ec["h"])} (16/9)'),
                text((u0 + u1) / 2, -(ec["bas"] + ec["h"] / 2), "écran (mur peint en blanc mat)", "lblc"),
                cote_h(c0, c1, -cl["z1"] - 6, f'clim {cote(cl["x1"] - cl["x0"])}')]

    return coupe_svg(COUPE_D, "sud", -20, M.L + 20,
                     [k["pieds"], k["z1"], ec["bas"], ec["bas"] + ec["h"], cl["z0"], cl["z1"]], aria, extra=cotes)


# ------------------------------------------------------------------ CSS des dessins
# Celui de l'ancienne page (3d/salon/plan.py, CSS) réduit aux règles des dessins : ni mode sombre, ni chasse fixe, ni
# règle de page (barre, sommaire, boutons, tableaux), ni règle qui cachait un état (`.cf`, `.co`, `.adyv`, `.achil`,
# `.dz`). `cadre` et `tapis` portent ici `cadrep` (cadre du passage) et `tapisd` (tapis) : `.cadre` et `.tapis` sont des
# classes de la page. `--sofa` n'existe pas dans le site : sa valeur est écrite.
CSS_DESSINS = """
.room{fill:var(--line);fill-opacity:.25}
.roomt{fill:var(--muted);font-size:7.5px;font-weight:600;text-anchor:middle}
.floorbg{fill:#D9D2C6;fill-opacity:.35}
.carreau{fill:none;stroke:#B5AC9C;stroke-width:.4;stroke-opacity:.7}
.w{fill:var(--ink)}
.bgwall{fill:var(--line);fill-opacity:.35}
.wallv{fill:#D5DADD;stroke:var(--muted);stroke-width:.5}
.cadrep{fill:var(--panel);stroke:var(--ink);stroke-width:.6}
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
.mont{fill:#26262A;stroke:var(--ink);stroke-width:.4}
.upper{fill:none;stroke:var(--ink);stroke-width:.8;stroke-dasharray:3 2}
.sofa{fill:#C9BFAE;stroke:var(--ink);stroke-width:.8}
.sofac{fill:#C9BFAE;stroke:var(--ink);stroke-width:.6;filter:brightness(.93)}
.tbl{fill:var(--wood);fill-opacity:.5;stroke:var(--ink);stroke-width:.9}
.stool{fill:var(--wood);fill-opacity:.28;stroke:var(--ink);stroke-width:.7}
.stoold{fill:var(--wood);fill-opacity:.6;stroke:var(--ink);stroke-width:.5}
.chil{fill:#C49A6C;fill-opacity:.35;stroke:var(--ink);stroke-width:.7;stroke-dasharray:5 1.5}
.tapisd{fill:#B4553A;fill-opacity:.12;stroke:#B4553A;stroke-opacity:.5;stroke-width:.8;stroke-dasharray:1 2}
.plante{fill:#6E9B5A;fill-opacity:.7;stroke:#3F6B31;stroke-width:.6;stroke-dasharray:3 2}
.pot{fill:#C2703D;stroke:var(--ink);stroke-width:.5}
.cadrem{fill:#E9E2D2;stroke:var(--ink);stroke-width:.8}
.rideau{fill:#E8DFCC;fill-opacity:.8;stroke:#A89A80;stroke-width:.6;stroke-dasharray:2 1.5}
.livre{fill:#7C8A5E;fill-opacity:.55;stroke:var(--ink);stroke-width:.3}
.dyv{fill:#D9772B;fill-opacity:.55;stroke:var(--ink);stroke-width:.7}
.proj{fill:#FFFFFF;fill-opacity:.6;stroke:var(--water);stroke-width:.8;stroke-dasharray:5 2}
.projr{fill:var(--ink);fill-opacity:.15;stroke:var(--ink);stroke-width:.7;stroke-dasharray:3 2}
.pp{fill:#4B2E3B;fill-opacity:.75;stroke:#7E9A86;stroke-width:.6;stroke-dasharray:2 2}
.poutre{fill:none;stroke:var(--muted);stroke-width:.8;stroke-dasharray:8 3 2 3}
.clim{fill:#F4F4F2;stroke:var(--ink);stroke-width:.7;stroke-dasharray:3 2}
.vinyl{fill:#2B2B2E;fill-opacity:.75;stroke:var(--ink);stroke-width:.4}
.lampe{fill:#F2C94C;fill-opacity:.35;stroke:#B8860B;stroke-width:.7;stroke-dasharray:3 2}
.seuil{stroke:var(--muted);stroke-width:.7;stroke-dasharray:3 2}
.pass{stroke:var(--tri);stroke-width:.8;stroke-dasharray:3 2}
.passm{fill:var(--tri)}
.passt{fill:var(--tri);font-size:7px;font-weight:600;text-anchor:middle}
.dim{stroke:var(--muted);stroke-width:.6;fill:none}
.dimt{fill:var(--muted);font-size:8px}
.lbl{font-size:7.5px}
.lbls{font-size:6.5px}
.lblx{font-size:5px}
.lblb{font-size:9px;font-weight:700}
.lblc{font-size:3.6px;font-style:italic}
.muted{fill:var(--muted)}
.sec{stroke:var(--tri);stroke-opacity:.3;stroke-width:.9;stroke-dasharray:10 3 2 3;fill:none}
.sect{fill:var(--tri);fill-opacity:.55;font-weight:800;font-size:11px}
.floorl{stroke:var(--ink);stroke-width:2}
.ceil{stroke:var(--muted);stroke-width:1;stroke-dasharray:6 4}
"""
