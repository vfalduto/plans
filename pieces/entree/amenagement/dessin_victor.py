"""Dessins de l'entrée, variante Victor : plan et coupes A à D.

Repris de 3d/entree/plan_victor.py. Réutilise le commun de dessin_principale.py (portes, jambages, coupe_svg,
légende, styles) ; seuls le plan, les coupes et les textes propres à la variante sont ici. Chaque fonction reçoit
le module `victor` en paramètre. Calques : mêmes classes que dessin_principale.py.
"""

from html import escape

from pieces.entree.amenagement import dessin_principale as P
from pieces.entree.amenagement.dessin_principale import (coin_arrondi, cote_h, degage, f, portes_vues, rect, rot,  # noqa: F401
                                                         text, virg, cote_v, legende)

COUPE_CLS = {**P.COUPE_CLS, "tall_i": ("talli", "tallic"), "facade_pi": ("india", "india")}
CSS = P.CSS + """
.talli{fill:var(--india);stroke:var(--ink);stroke-width:.8}
.tallic{fill:var(--india);stroke:var(--ink);stroke-width:1.4}
"""

COUPE_A = 60     # y, regard vers le nord : mur nord libre, tableau électrique
COUPE_B = 40     # x, regard vers l'est : arrondi du meuble à chaussures, penderie, planche, patères
COUPE_C = 130    # y, regard vers le sud : meuble à chaussures, étagères, penderie, porte d'entrée au fond
COUPE_D = 60     # x, regard vers l'ouest : mur ouest de l'entrée, cadres, miroir, interphone


# ------------------------------------------------------------------ plan vu de dessus
def plan_svg(M, aria="Plan de l'entrée, version Victor", zones=""):
    b, pe, mi, et, pl, cd = M.CHAUSSURES, M.PENDERIE, M.MIROIR, M.ETAGERES, M.PLANCHE, M.CADRES
    o = []
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
    o += P._jambages(M)
    for p in M.PORTES:
        o += P._porte(M, p)
    o.append(text(39, 392, "porte d’entrée", "lbls muted"))
    # tableau électrique, mur nord libre
    o.append(rect(M.TABLEAU["x0"], -6, M.TABLEAU["x1"], 0, "tech"))
    o.append(text(140, 14, "tableau électrique · mur libre dessous", "lblx muted"))
    # ① meuble à chaussures avec son arrondi jusqu'au PAX, joints des abattants, étagères flottantes (tireté)
    o.append(coin_arrondi(b["x0"], b["x1"], b["y0"], b["y1"], b["r"], "cab"))
    for x in [b["xa"]] + [x0 for x0, _ in b["modules"][1:]]:
        o.append(f'<line class="app" x1="{x}" y1="{b["y0"]}" x2="{x}" y2="{b["y1"]}"/>')
    o.append(coin_arrondi(et["x0"], et["x1"], et["y0"], et["y1"], et["r"], "upper"))
    cx, cy = M.CENTRE_ARRONDI
    o.append(f'<circle class="hook" cx="{cx}" cy="{cy}" r="1.2"/>')
    xm = (b["xa"] + b["x1"]) / 2
    o.append(text(xm, b["y0"] + 7, f'① Chaussures {b["x1"] - b["xa"]} × {b["y1"] - b["y0"]} · h {b["z1"] + b["plateau"]}', "lblx"))
    o.append(text(xm, b["y0"] + 13, f'{len(b["modules"])} abattants', "lblx"))
    o.append(text(xm, et["y0"] + 14, f'2 étagères flottantes h {et["z"][0]} · {et["z"][1]}', "lblx muted"))
    o.append(text(b["xa"] - 2, b["y1"] - 4, f'R {b["r"]}', "lblx muted", "end"))
    # ③ penderie PAX : portes de 50 (nord) et 25 (sud) vers l'ouest, débattement en tireté ; tringle (cintres de face)
    o.append(rect(pe["x0"], pe["y0"], pe["x1"], pe["y1"], "talli"))
    yj = pe["y0"] + pe["portes"][0]
    o.append(f'<line class="app" x1="{pe["x0"]}" y1="{f(yj)}" x2="{pe["x1"]}" y2="{f(yj)}"/>')
    o.append(f'<line class="inner" x1="{pe["x0"] + 4}" y1="{f((pe["y0"] + pe["y1"]) / 2)}" x2="{pe["x1"] - 4}" y2="{f((pe["y0"] + pe["y1"]) / 2)}"/>')
    l1, l2 = pe["portes"]
    o.append(f'<path class="swing" d="M{pe["x0"]} {f(yj)} A{l1} {l1} 0 0 1 {f(pe["x0"] - l1)} {pe["y0"]}"/>')
    o.append(f'<path class="swing" d="M{pe["x0"]} {f(yj)} A{l2} {l2} 0 0 0 {f(pe["x0"] - l2)} {pe["y1"]}"/>')
    xt = (pe["x0"] + pe["x1"]) / 2
    ym = (pe["y0"] + pe["y1"]) / 2
    o.append(text(xt - 4, ym, f'③ Penderie PAX {pe["y1"] - pe["y0"]} × {pe["x1"] - pe["x0"] - pe["facade"]} · h {pe["z1"]}', "lblx", extra=rot(xt - 4, ym)))
    o.append(text(xt + 3, ym, "portes 50 + 25 · cintres de face", "lblx", extra=rot(xt + 3, ym)))
    o.append(text(xt + 10, ym, f'bandeau {pe["z1"]} → {M.H}', "lblx muted", extra=rot(xt + 10, ym)))
    # ⑤ planche à chaussures, patères, applique
    o.append(rect(pl["x0"], pl["y0"], pl["x1"], pl["y1"], "cab"))
    yp = (pl["y0"] + pl["y1"]) / 2
    o.append(text(pl["x0"] + 8, yp, f'⑤ Planche h {pl["z1"]}', "lblx", extra=rot(pl["x0"] + 8, yp)))
    o.append(text(pl["x0"] + 15, yp, "chaussures dessous", "lblx", extra=rot(pl["x0"] + 15, yp)))
    for y in M.PATERES:
        o.append(f'<circle class="hook" cx="108" cy="{y}" r="1.6"/>')
    o.append(text(127, 345, "← 4 patères au-dessus de la planche, applique", "lblx muted", "start"))
    # mur ouest : cadres, miroir, interphone
    o.append(rect(0, cd["y0"], cd["ep"] + 0.5, cd["y1"], "dark"))
    o.append(text(6, (cd["y0"] + cd["y1"]) / 2 + 2, f'{cd["colonnes"] * cd["rangs"]} cadres', "lblx", "start"))
    o.append(rect(0, mi["y0"], 2.5, mi["y1"], "mirror"))
    o.append(text(6, (mi["y0"] + mi["y1"]) / 2 + 2, "miroir", "lblx", "start"))
    it = M.INTERPHONE
    o.append(rect(0, it["y0"], 3, it["y1"], "facp"))
    o.append(text(6, (it["y0"] + it["y1"]) / 2 + 2, "interphone", "lblx", "start"))
    # peinture India
    yi = M.INDIA["y0"]
    for x0, y0, x1, y1 in ((0, yi, 2.5, 374), (107.5, pe["y1"], 110, 374), (0, 371.5, 110, 374)):
        o.append(rect(x0, y0, x1, y1, "indiap"))
    o.append(rect(2, 374, 77, 376, "indiap"))
    o.append(text(127, 365, "■ murs, plafond, porte et PAX en India", "lblx india-t", "start"))
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
    o.append(text(COUPE_B - 3, 368, "B", "sect", "end"))
    o.append(f'<line class="sec" x1="-6" y1="{COUPE_C}" x2="360" y2="{COUPE_C}"/>')
    o.append(text(-8, COUPE_C + 4, "C", "sect", "end"))
    o.append(f'<line class="sec" x1="{COUPE_D}" y1="-6" x2="{COUPE_D}" y2="380"/>')
    o.append(text(COUPE_D + 3, 368, "D", "sect", "start"))
    return f'<svg class="plan" viewBox="-150 -130 595 560" role="{"group" if zones else "img"}" aria-label="{escape(aria)}">{"".join(o)}{zones}</svg>'


# ------------------------------------------------------------------ coupes
def coupe_a(M, aria=None):
    t = M.TABLEAU

    def cotes(X):
        return portes_vues(M, X, "n") + [
            text((X(t["x0"]) + X(t["x1"])) / 2, -t["z1"] - 6, "position et taille à relever", "lblx muted"),
            text((X(t["x0"]) + X(t["x1"])) / 2, -30, "mur libre", "lbls muted"),
            cote_h(87, 191, 12, "trumeau 104"),
        ]

    return P.coupe_svg(M, COUPE_A, "nord", -20, 284, [t["z0"], t["z1"], M.H_PORTE], extra=cotes, aria=aria, classes=COUPE_CLS)


def coupe_b(M, aria=None):
    pe, pl = M.PENDERIE, M.PLANCHE

    def cotes(X):
        return [cote_h(pe["y0"], pe["y1"], 12, f'penderie {pe["y1"] - pe["y0"]}'),
                cote_h(pl["y0"], pl["y1"], 12, f'planche {pl["y1"] - pl["y0"]}'),
                text((pl["y0"] + pl["y1"]) / 2, -pl["z1"] + 14, "chaussures", "lblx muted"),
                text((pl["y0"] + pl["y1"]) / 2, -pl["z1"] - 4, "chaussures", "lblx muted"),
                text((pe["y0"] + pe["y1"]) / 2, -(pe["z1"] + M.H) / 2 + 2, "bandeau", "lblx muted"),
                text(pe["y0"] + pe["portes"][0] / 2, -60, f'porte {pe["portes"][0]}', "lblx muted"),
                text(pe["y1"] - pe["portes"][1] / 2, -60, f'{pe["portes"][1]}', "lblx muted"),
                text((M.PATERES[0] + M.PATERES[-1]) / 2, -M.PATERE["z"] - 6, f'4 patères en bois h {M.PATERE["z"]}', "lblx muted"),
                text(M.APPLIQUE["y"] + 10, -M.APPLIQUE["z"] + 2, "applique", "lblx muted", "start")]

    return P.coupe_svg(M, COUPE_B, "est", -20, 394, [pl["z1"], M.CHAUSSURES["z1"] + M.CHAUSSURES["plateau"], M.PATERE["z"], pe["z1"]],
                       extra=cotes, aria=aria, classes=COUPE_CLS)


def coupe_c(M, aria=None):
    b, et = M.CHAUSSURES, M.ETAGERES

    def cotes(X):
        u0, u1 = sorted((X(b["xa"]), X(b["x1"])))
        v0, v1 = sorted((X(b["x0"]), X(b["xa"])))
        xm = (u0 + u1) / 2
        return [text(xm, -b["z1"] - b["plateau"] - 4, "① chaussures", "lblb"),
                cote_h(u0, u1, 12, f'abattants {b["x1"] - b["xa"]}'),
                cote_h(v0, v1, 12, f'arrondi {b["xa"] - b["x0"]}'),
                text(xm, -et["z"][1] - et["ep"] - 3, "étagères flottantes", "lblx muted")] + portes_vues(M, X, "s")

    return P.coupe_svg(M, COUPE_C, "sud", -20, 374, [b["z1"] + b["plateau"], et["z"][0], et["z"][1], M.PENDERIE["z1"]], extra=cotes, aria=aria, classes=COUPE_CLS)


def coupe_d(M, aria=None):
    cd, mi, it = M.CADRES, M.MIROIR, M.INTERPHONE

    def cotes(X):
        u0, u1 = sorted((X(cd["y0"]), X(cd["y1"])))
        v0, v1 = sorted((X(mi["y0"]), X(mi["y1"])))
        return [cote_h(u0, u1, 12, f'{cd["colonnes"]} × {cd["rangs"]} cadres {cd["l"]} × {cd["h"]}'),
                cote_h(v0, v1, 12, f'miroir {mi["y1"] - mi["y0"]}'),
                text((v0 + v1) / 2, -mi["z1"] - 4, f'miroir {mi["y1"] - mi["y0"]} × {mi["z1"] - mi["z0"]}', "lblx muted"),
                text(X((it["y0"] + it["y1"]) / 2), -it["z0"] + 8, "interphone", "lblx muted")] + portes_vues(M, X, "o")

    return P.coupe_svg(M, COUPE_D, "ouest", -20, 394, [mi["z0"], cd["z0"], cd["z1"], mi["z1"]], extra=cotes, aria=aria, classes=COUPE_CLS)


# ------------------------------------------------------------------ textes sous les dessins et principes
SUJETS = {"A": "mur nord", "B": "mur de la salle de bain", "C": "meuble à chaussures", "D": "mur ouest de l'entrée"}


def legendes(M):
    """Texte long sous chaque dessin : il devient l'aria-label du SVG."""
    b, mi, et, pl, cd = M.CHAUSSURES, M.MIROIR, M.ETAGERES, M.PLANCHE, M.CADRES
    pb = b["y1"] - b["y0"]
    le = et["x1"] - et["x0"]
    ncd = cd["colonnes"] * cd["rangs"]
    return {
        "plan": ("Plan vu de dessus, 1 unité = 1 cm ; nord en haut. Les portes de la penderie s'ouvrent vers l'ouest, dans "
                 "la branche d'entrée (débattement en tireté). La porte d'entrée ouverte à 90° vient contre le chant de la "
                 "planche à chaussures, qui lui sert de butée. Traits A, B, C, D : coupes."),
        "A": (f"Coupe à y {COUPE_A}, regard vers le nord : l'ouest est à gauche. Rien sous le tableau électrique, entre les "
              f"portes de la cuisine et du WC. Tableau dessiné au milieu du trumeau, de {M.TABLEAU['z0']} à "
              f"{M.TABLEAU['z1']} : position et taille à relever."),
        "B": ("Coupe à x %d, regard vers l'est : le nord est à gauche. À gauche, l'arrondi du meuble à chaussures et ses "
              "étagères au fond ; puis la penderie PAX (portes FORSAND de 50 et 25, 229 de haut) et son bandeau jusqu'au "
              "plafond ; puis la planche à chaussures à %d, les quatre patères et l'applique au-dessus." % (COUPE_B, pl["z1"])),
        "C": (f"Coupe à y {COUPE_C}, regard vers le sud : l'est est à gauche. Le meuble à chaussures, {pb} de profondeur, "
              f"plateau à {b['z1'] + b['plateau']} : deux abattants de {b['modules'][0][1] - b['modules'][0][0]} puis "
              f"l'arrondi plein jusqu'à la façade du PAX ; au-dessus, deux étagères flottantes de {le} × "
              f"{et['y1'] - et['y0']} à {et['z'][0]} et {et['z'][1]}. À droite, le flanc de la penderie PAX et son "
              f"bandeau, la porte d'entrée au fond."),
        "D": (f"Coupe à x {COUPE_D}, regard vers l'ouest : le sud est à gauche. Contre la porte d'entrée, l'interphone, "
              f"puis le miroir {mi['y1'] - mi['y0']} × {mi['z1'] - mi['z0']} à coins arrondis, puis la galerie de {ncd} "
              f"cadres {cd['l']} × {cd['h']}, centrée à la même hauteur que le miroir ({virg(cd['zc'], 0)}). À droite, la "
              f"porte de la pièce ouest."),
    }


def principes(M):
    """Les cartes « Principe » : liste de (titre, texte HTML). Le rang est celui de `ZONES[i]["principe"]`."""
    b, pe, mi, et, pl, cd = M.CHAUSSURES, M.PENDERIE, M.MIROIR, M.ETAGERES, M.PLANCHE, M.CADRES
    pb = b["y1"] - b["y0"]
    lp, pp = pe["y1"] - pe["y0"], pe["x1"] - pe["x0"] - pe["facade"]
    le = et["x1"] - et["x0"]
    lpl, ppl = pl["y1"] - pl["y0"], pl["x1"] - pl["x0"]
    ncd = cd["colonnes"] * cd["rangs"]
    return [
        ("① Meuble à chaussures",
         f"À la place de la penderie, contre la face nord de la salle de bain : comme celui de la {M.BASE}, mais d'un seul "
         f"niveau d'abattants et plus profond. Deux abattants de {b['modules'][0][1] - b['modules'][0][0]} sur "
         f"{b['z1'] - b['socle']} de haut (environ {M.PAIRES_MEUBLE} paires), plateau vide-poche en chêne à "
         f"{b['z1'] + b['plateau']}. À l'ouest, il se prolonge jusqu'à la façade du PAX et s'y termine par un quart de "
         f"cercle plein de rayon {b['r']}. Tout part d'un seul centre, le coin de la salle de bain : l'arc est tangent à "
         f"la façade du PAX et à celle des abattants, sans plat ni ressaut ; le socle de {b['socle']} en retrait de "
         f"{b['retrait']} et les étagères suivent des arcs concentriques. Le meuble prend la profondeur du PAX porte "
         f"comprise ({pb}). Au-dessus, deux étagères flottantes de {le} × {et['y1'] - et['y0']}, arrondies au bout ouest "
         f"(R {et['r']}) et prolongées jusqu'au flanc du PAX (fixations invisibles), à {et['z'][0]} et {et['z'][1]}. "
         f"{b['y0']} cm de passage devant, {b['x0']} entre l'arrondi et le mur ouest."),
        ("③ Penderie IKEA PAX",
         f"Contre la cloison de la salle de bain, à partir de son coin, à la place du premier module à chaussures : un "
         f"caisson PAX de {lp} × {pp} × {pe['z1']}, fermé par une porte FORSAND de {pe['portes'][0]} et une de "
         f"{pe['portes'][1]} (229 de haut ; c'est la combinaison IKEA pour un caisson de 75), ouvertes vers l'ouest. À "
         f"{pp} de profondeur, les cintres se suspendent de face sur la tringle KOMPLEMENT à {pe['tringle']} (environ "
         f"{pe['manteaux']} manteaux, 12 kg au plus) ; deux tablettes en haut, à {pe['etageres'][0]} et "
         f"{pe['etageres'][1]}, remplacent le meuble haut (bonnets, gants, sacs). Caisson, portes et bandeau sont peints "
         f"en India comme les murs de l'entrée ; le bandeau ferme les {M.H - pe['z1']} cm jusqu'au plafond. Passage "
         f"restant : {pe['x0']} cm."),
        ("⑤ Planche à chaussures sous les patères",
         f"De la penderie au mur sud, {lpl} × {ppl}, dessus à {pl['z1']} sur deux pieds pleins : les chaussures se "
         f"rangent dessous ({pl['z1'] - pl['ep']} de haut) et dessus, environ {M.PAIRES_PLANCHE} paires. Les "
         f"{len(M.PATERES)} patères en bois restent à {M.PATERE['z']} au-dessus, avec une applique. La porte d'entrée "
         f"ouverte à 90° vient contre son chant (prévoir un tampon)."),
        ("Mur ouest : cadres et miroir",
         f"En face de la penderie, sur le mur peint : un miroir {mi['y1'] - mi['y0']} × {mi['z1'] - mi['z0']} à coins "
         f"arrondis (R {mi['r']}) juste à côté de l'interphone, puis une galerie de {ncd} cadres {cd['l']} × {cd['h']} "
         f"en grille {cd['colonnes']} × {cd['rangs']}, {cd['ecart']} d'écart, centrée sur le mur libre entre la porte de "
         f"la pièce ouest et le miroir et à la hauteur du centre du miroir. Ils ne dépassent que de {virg(cd['ep'])} "
         f"dans le passage."),
        ("Mur nord et entrée en India",
         f"Sous le tableau électrique, rien : il reste dégagé et accessible. Au sud de y {M.INDIA['y0']}, murs, plafond et "
         f"porte d'entrée en {M.INDIA['nom']}, comme dans la {M.BASE}."),
    ]
