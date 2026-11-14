"""Dessins du document salon/etageres, repris de 3d/salon/etageres.py (ET:351-752) : mêmes chaînes, même ordre
d'éléments. Seul écart de tracé : la virgule au lieu du point médian dans les étiquettes.

Chaque dessin a la signature `(e, aria="")` : `e` est l'état d'une disposition (`calculs.etat`), ignoré par les dessins
communs aux quatre ; `aria` remplace l'`aria-label` de l'ancien dessin (vide : l'ancien). `legendes(e)` donne les
textes qui suivaient les dessins dans l'ancienne page : ils deviennent les textes alternatifs.

`en_cm` met un dessin à l'échelle du centimètre (Mesurer lit des cm) ; `cadre_commun` et `recadrer` donnent le même
viewBox à un dessin dans les quatre variantes (la comparaison recopie le viewBox de la base). `CSS` : une règle par
classe dessinée, sur les jetons de commun/site.css.
"""
import math
import re
from html import escape
from typing import Callable, Sequence

from pieces.salon.dessin import cote_h, cote_v, f, iso_svg, rect, text
from pieces.salon.enfilade.document import ENFILADE as EN
from pieces.salon.etageres import calculs
from pieces.salon.etageres.calculs import N_TASSEAUX, PAR_TASSEAU, PR
from pieces.salon.etageres.document import (DRESSAGE, ETAGERES as ET, ETUDE_MONTANTS as EU, KERF, KERF_METAL,
                                            L_MONTANT, MONTANTS as MO, PANNEAU, ROND, TASSEAU)
from pieces.salon.etageres.volumes import pieces_3d, pieces_detail
from pieces.salon.meubles import cote as cm
from pieces.salon.piece import H

PAS = MO["pas"]
RA = ET["rainure"]
# échelles de l'ancienne page (unités de dessin par cm) des quatre dessins de Plans mis en cm
ECHELLES = {"elevation": 2.4, "dessus": 2.6, "profil": 9, "travee": 3}


def _label(aria, defaut):
    """`aria-label` du dessin : `aria` échappé, ou l'ancien (déjà écrit tel que l'ancienne page l'écrivait)."""
    return escape(aria, quote=True) if aria else defaut


def poly(cls, pts):
    return f'<polygon class="{cls}" points="{" ".join(f"{f(u)},{f(v)}" for u, v in pts)}"/>'


# ------------------------------------------------------------------ élévation (ET:351-409)
def _elevation(e, mini=False, aria=""):
    """Mur ouest vu depuis la pièce (sud à gauche, nord à droite) : enfilade en contour, montants, tablettes, bouts de
    chevilles, cotes ; mini : vignette sans cotes ni textes."""
    k, Y = ECHELLES["elevation"], EN["y1"]
    U = lambda y: (Y - y) * k  # noqa: E731
    V = lambda z: (H - z) * k  # noqa: E731
    l, ce, r = MO["l"], ET["cheville_ext"], MO["trou"] / 2
    o = [rect(0, V(H), U(0), V(0), "bgwall")]
    if not mini:
        o += [f'<line class="floorl" x1="-70" y1="{f(V(0))}" x2="{f(U(0) + 30)}" y2="{f(V(0))}"/>',
              f'<line class="ceil" x1="-70" y1="{f(V(H))}" x2="{f(U(0) + 30)}" y2="{f(V(H))}"/>',
              text(U((EN["y0"] + EN["y1"]) / 2), V(EN["z1"] / 2 + 5), "enfilade (page Enfilade)", "lbl muted")]
        for y in (EN["y1"] - 6, EN["y0"] + 6):
            o.append(rect(U(y) - 2, V(EN["pieds"]), U(y) + 2, V(0), "upper"))
    o.append(rect(U(EN["y1"]), V(EN["z1"]), U(EN["y0"]), V(EN["pieds"]), "upper"))
    for i, y in enumerate(MO["axes"]):
        o.append(rect(U(y + l / 2), V(MO["z1"]), U(y - l / 2), V(MO["z0"]), "mont"))
        if not mini:
            o.append(text(U(y), V(MO["z1"]) - 4, f"M{i + 1}", "lbls"))
    for t in e.ts:
        o.append(rect(U(t["y1"]), V(t["z"]), U(t["y0"]), V(t["z"] - ET["ep"]), "shelfc"))
        if mini:
            continue
        ym = (MO["axes"][t["b"]] + MO["axes"][t["b"] - 1]) / 2      # milieu de la travée la plus au sud
        o.append(text(U(ym), V(t["z"]) - 3, f'{t["rep"]}, {t["type"]}, {t["z"]}', "lbls"))
        for kk in range(t["a"], t["b"] + 1):
            y, zj = MO["axes"][kk], t["zs"][kk - t["a"]]
            for ya in (y + l / 2 + ce, y - l / 2):
                o += [rect(U(ya), V(zj + 2 * r), U(ya - ce), V(zj), "acier"),
                      rect(U(ya), V(zj - ET["ep"]), U(ya - ce), V(zj - MO["decalage"]), "acier")]
    if mini:
        x0, x1 = U(EN["y1"]) - 8, U(EN["y0"]) + 8
        return (f'<svg viewBox="{f(x0)} {f(V(H))} {f(x1 - x0)} {f((H - EN["z1"] + 6) * k)}" role="img" '
                f'aria-label="Disposition {escape(e.nom)}">{"".join(o)}</svg>')
    # cotes horizontales : axes (au-dessus des montants), débords (sous les montants)
    ax = [U(y) for y in MO["axes"]]
    zc = V(MO["z1"] + 12)
    o += [cote_h(U(EN["y1"]), ax[-1], zc, cm(EN["y1"] - MO["axes"][-1]))]
    o += [cote_h(b, a, zc, f(PAS)) for a, b in zip(ax, ax[1:])]
    o += [cote_h(ax[0], U(EN["y0"]), zc, cm(MO["axes"][0] - EN["y0"]))]
    ys0, ys1 = min(t["y0"] for t in e.ts), max(t["y1"] for t in e.ts)
    zd = V((MO["z0"] + EN["z1"]) / 2 - 2)
    o += [cote_h(U(EN["y1"]), U(ys1), zd, cm(abs(EN["y1"] - ys1))),
          cote_h(U(ys1), ax[-1], zd, f(ET["debord"])),
          cote_h(ax[0], U(ys0), zd, f(ET["debord"])),
          cote_h(U(ys0), U(EN["y0"]), zd, cm(abs(ys0 - EN["y0"])))]
    # cotes verticales : montants et vides (à gauche), dessus des rangs (plus à gauche) quand les tablettes sont en
    # rangs horizontaux ; sinon, la hauteur de chaque tablette est dans son étiquette
    x1, x2 = -14, -40
    for a, b in ((0, EN["z1"]), (EN["z1"], MO["z0"]), (MO["z0"], MO["z1"]), (MO["z1"], H)):
        o.append(cote_v(V(a), V(b), x1, cm(b - a)))
    zs = [0] + e.niveaux
    if len(e.niveaux) <= 4:
        o += [cote_v(V(a), V(b), x2, cm(b - a)) for a, b in zip(zs, zs[1:])]
    o += [text(-40, V(0) + 14, "sol", "lbls muted"), text(-40, V(H) - 5, f"plafond {cm(H)}", "lbls muted", "start"),
          text(2, V(0) + 14, "sud (passage)", "lbls muted", "start"),
          text(U(0) - 2, V(0) + 14, "nord (coin)", "lbls muted", "end")]
    label = _label(aria, f"Élévation du mur ouest, disposition {escape(e.nom)}")
    return (f'<svg viewBox="-75 {f(V(H) - 16)} {f(U(0) + 110)} {f(H * k + 40)}" role="img" '
            f'aria-label="{label}">{"".join(o)}</svg>')


def mini(e, aria=""):
    """Vignette d'une disposition ; son `aria-label` (« Disposition X ») reste toujours."""
    return _elevation(e, mini=True)


def elevation(e, aria=""):
    return _elevation(e, aria=aria)


# ------------------------------------------------------------------ vues de dessus (ET:412-464)
def rangs_dessus(e):
    """Tablettes rangées en vues de dessus : du haut vers le bas, une tablette va dans le premier rang où elle ne
    recouvre aucune autre (au moins 4 d'écart)."""
    rangs = []
    for t in sorted(e.ts, key=lambda t: -max(t["zs"])):
        for rg in rangs:
            if all(t["y0"] >= u["y1"] + 4 or t["y1"] <= u["y0"] - 4 for u in rg):
                rg.append(t)
                break
        else:
            rangs.append([t])
    return rangs


def dessus(e, aria=""):
    """Vues de dessus des tablettes, rangées sur quelques bandes, vues depuis la pièce face au mur : mur en haut, sud à
    gauche, nord à droite ; montants dans les entailles, chevilles."""
    k, Y = ECHELLES["dessus"], EN["y1"]
    U = lambda y: (Y - y) * k  # noqa: E731
    rang, l, ce, r = 60, MO["l"], ET["cheville_ext"], MO["trou"] / 2
    rangs = rangs_dessus(e)
    o = []
    for n_r, rg in enumerate(rangs):
        V = lambda x, n_r=n_r: (n_r * rang + x) * k  # noqa: E731
        o += [rect(U(EN["y1"]), V(-4), U(EN["y0"]), V(0), "mur-h"),
              rect(U(EN["y1"]), V(0), U(EN["y0"]), V(EN["p"]), "upper")]
        chev = []
        for t in rg:
            o.append(rect(U(t["y1"]), V(0), U(t["y0"]), V(ET["x1"]), "shelfc"))
            o.append(text(U((t["y0"] + t["y1"]) / 2), V(ET["x1"]) - 6, f'{t["rep"]}, {t["type"]}, dessus {t["z"]}', "lbls"))
            for y in MO["axes"][t["a"]:t["b"] + 1]:
                a, b = U(y + l / 2 + ce), U(y - l / 2 - ce)
                chev += [rect(a, V(MO["x_av"] - r), b, V(MO["x_av"] + r), "acierh"),
                         rect(a, V(MO["x_ar"] - r), b, V(MO["x_ar"] + r), "acier")]
        o += [rect(U(y + l / 2), V(0), U(y - l / 2), V(MO["p"]), "mont") for y in MO["axes"]]
        o += chev
    vb = ((len(rangs) - 1) * rang + EN["p"]) * k
    ax = [U(y) for y in MO["axes"]]
    o += [text(a, vb + 9, f"M{i + 1}", "lbls") for i, a in enumerate(ax)]
    o += [cote_h(b, a, vb + 24, f(PAS)) for a, b in zip(ax, ax[1:])]
    o += [cote_h(U(EN["y1"]), ax[-1], vb + 24, cm(EN["y1"] - MO["axes"][-1])),
          cote_h(ax[0], U(EN["y0"]), vb + 24, cm(MO["axes"][0] - EN["y0"])),
          cote_h(U(EN["y1"]), U(EN["y0"]), vb + 44, f'enfilade {cm(EN["y1"] - EN["y0"])}')]
    xr = U(EN["y0"]) + 12
    v0 = ((len(rangs) - 1) * rang) * k
    o += [cote_v(v0, v0 + MO["p"] * k, xr, f(MO["p"])),
          cote_v(v0 + MO["p"] * k, v0 + ET["x1"] * k, xr, f(ET["x1"] - MO["p"])),
          cote_v(v0 + ET["x1"] * k, v0 + EN["p"] * k, xr, f(EN["p"] - ET["x1"])),
          text(U(EN["y1"]) + 4, -4 * k - 4, "mur ouest", "lbls muted", "start"),
          text(U(EN["y0"]) - 4, -4 * k - 4, "sud à gauche, nord à droite (vu depuis la pièce)", "lbls muted", "end")]
    w, h = U(0) + 140, vb + 68 + 4 * k + 14
    label = _label(aria, f"Étagères vues de dessus, disposition {escape(e.nom)}")
    return (f'<svg viewBox="-110 {f(-4 * k - 14)} {f(w)} {f(h)}" role="img" '
            f'aria-label="{label}">{"".join(o)}</svg>')


# ------------------------------------------------------------------ vues iso (ET:820, ET:824)
def iso(e, aria=""):
    return iso_svg(pieces_3d(e.cle), _label(aria, f"Étagères, vue iso, disposition {e.nom}"))


def detail(e, aria=""):
    return iso_svg(pieces_detail(), _label(aria, "Étagères, détail d'une entaille en vue iso"), echelle=11,
                   style="max-width:420px;display:block;margin:0 auto")


# ------------------------------------------------------------------ profil et travée (ET:467-524)
def profil(e, aria=""):
    """Coupe de profil juste à côté d'un montant, au droit des bouts de chevilles."""
    k = ECHELLES["profil"]
    ep, r, dec = ET["ep"], MO["trou"] / 2, MO["decalage"]
    X = lambda x: f(x * k)  # noqa: E731
    Z = lambda z: f(-z * k)  # noqa: E731
    o = [f'<rect class="mur-h" x="{X(-3)}" y="{Z(14)}" width="{X(3)}" height="{f(28 * k)}"/>',
         text(-1.5 * k, -15 * k, "mur", "lbl muted"),
         f'<rect class="mont" x="0" y="{Z(14)}" width="{X(MO["p"])}" height="{f(28 * k)}"/>']
    zf = r - dec                    # centre de la cheville avant
    for dz in (-10, -5, 5, 10):     # trous libres : colonne avant sous les tablettes, arrière au-dessus
        o += [f'<circle class="trou" cx="{X(MO["x_av"])}" cy="{Z(dz + zf)}" r="{f(r * k)}"/>',
              f'<circle class="trou" cx="{X(MO["x_ar"])}" cy="{Z(dz + r)}" r="{f(r * k)}"/>']
    g0, g1 = MO["x_av"] - RA["l"] / 2, MO["x_av"] + RA["l"] / 2
    o += [f'<path class="shelfc" d="M0 {Z(0)} H{X(ET["p"])} V{Z(-ep)} H{X(g1)} V{Z(-ep + RA["prof"])} H{X(g0)} '
          f'V{Z(-ep)} H0 Z"/>',
          f'<circle class="acier" cx="{X(MO["x_av"])}" cy="{Z(zf)}" r="{f(r * k)}"/>',
          f'<circle class="acier" cx="{X(MO["x_ar"])}" cy="{Z(r)}" r="{f(r * k)}"/>',
          cote_h(0, MO["p"] * k, -14 * k - 10, f'montant {f(MO["p"])}'),
          cote_h(0, ET["p"] * k, -14 * k - 26, f'tablette {ET["p"]}, jusqu\'au mur'),
          cote_h(MO["x_ar"] * k, MO["x_av"] * k, 4.5 * k, f(MO["x_av"] - MO["x_ar"])),
          cote_v(0, ep * k, ET["p"] * k + 12, cm(ep)),
          cote_v(-r * k, -zf * k, -3 * k - 14, cm(dec)),
          cote_v(-(5 + r) * k, -r * k, -3 * k - 30, f(MO["pas_trous"])),
          text((MO["p"] + 3) * k, -2.5 * k, "cheville arrière, dessus : retient le basculement", "lbls", "start"),
          text((MO["p"] + 3) * k, (ep + 2.2) * k, "cheville avant, dessous : porte la tablette", "lbls", "start"),
          rappel(g1 * k, (ep - RA["prof"] / 2) * k, (MO["p"] + 3) * k, (ep + 4.4) * k,
                 f"dans une rainure de {cm(RA['l'] * 10)} × {cm(RA['prof'] * 10)} mm : elle ne peut ni avancer ni glisser en long",
                 "start", "lbls"),
          text((MO["p"] + 3) * k, 9 * k, "trous libres sur le flanc : la tablette monte ou descend de 5 en 5",
               "lbls muted", "start")]
    label = _label(aria, "Profil d'une tablette entaillée et de ses deux chevilles")
    return (f'<svg style="max-width:620px" viewBox="{f(-8 * k)} {f(-18.5 * k)} {f(46 * k)} {f(33 * k)}" role="img" '
            f'aria-label="{label}">{"".join(o)}</svg>')


def travee(e, aria=""):
    """Une travée vue de face : deux montants, la tablette passe devant eux, bouts de chevilles."""
    k = ECHELLES["travee"]
    X = lambda y: f(y * k)  # noqa: E731
    Z = lambda z: f(-z * k)  # noqa: E731
    l, ce, r = MO["l"], ET["cheville_ext"], MO["trou"] / 2
    o = [f'<rect class="mont" x="{X(y - l / 2)}" y="{Z(40)}" width="{X(l)}" height="{f(50 * k)}"/>'
         for y in (0, PAS)]
    for z in (0, 35):
        o.append(f'<rect class="shelfc" x="{X(-ET["debord"])}" y="{Z(z)}" '
                 f'width="{X(PAS + 2 * ET["debord"])}" height="{X(ET["ep"])}"/>')
        for y in (0, PAS):
            for y0 in (y - l / 2 - ce, y + l / 2):
                o += [f'<rect class="acier" x="{X(y0)}" y="{Z(z + 2 * r)}" width="{X(ce)}" height="{X(2 * r)}"/>',
                      f'<rect class="acier" x="{X(y0)}" y="{Z(z - ET["ep"])}" width="{X(ce)}" '
                      f'height="{X(MO["decalage"] - ET["ep"])}"/>']     # le haut de la cheville avant est dans la rainure
    o += [cote_h(-ET["debord"] * k, 0, -41 * k - 6, f'{ET["debord"]}'),
          cote_h(0, PAS * k, -41 * k - 6, f'{PAS} d\'axe en axe'),
          cote_h(PAS * k, (PAS + ET["debord"]) * k, -41 * k - 6, f'{ET["debord"]}'),
          cote_v(0, -35 * k, (PAS + ET["debord"]) * k + 10, "35"),
          text(PAS / 2 * k, -17 * k, "livres ≤ 30", "lbls muted")]
    label = _label(aria, "Une travée vue de face")
    return (f'<svg style="max-width:660px" viewBox="{f(-20 * k)} {f(-46 * k)} {f((PAS + 40) * k)} {f(58 * k)}" role="img" '
            f'aria-label="{label}">{"".join(o)}</svg>')


# ------------------------------------------------------------------ présentoir (ET:527-614)
def fleche(x0, y0, x1, y1):
    """Flèche d'effort (SVG), pointe en (x1, y1)."""
    d = math.hypot(x1 - x0, y1 - y0)
    ux, uy = (x1 - x0) / d, (y1 - y0) / d
    a, b = (x1 - 7 * ux - 3.5 * uy, y1 - 7 * uy + 3.5 * ux), (x1 - 7 * ux + 3.5 * uy, y1 - 7 * uy - 3.5 * ux)
    return (f'<line class="fl" x1="{f(x0)}" y1="{f(y0)}" x2="{f(x1 - 6 * ux)}" y2="{f(y1 - 6 * uy)}"/>'
            + poly("flh", [(x1, y1), a, b]))


def rappel(x0, y0, x1, y1, txt, anc, cls="lbl"):
    """Étiquette reportée par un trait de rappel (coordonnées SVG)."""
    return (f'<line x1="{f(x0)}" y1="{f(y0)}" x2="{f(x1)}" y2="{f(y1)}" stroke="var(--muted)" stroke-width=".7"/>'
            + text(x1 + (4 if anc == "start" else -4), y1 + 3, txt, cls, anc))


def presentoir(e, aria=""):
    """Présentoir : tablette penchée vers la pièce, profil à côté d'un montant (échelle × 9) : pincée entre la
    cheville arrière (dessus) et la cheville avant (dessous, dans sa rainure), efforts en rouge."""
    k, c, sn, r = 9, PR["c"], PR["s"], MO["trou"] / 2
    top, bas, zc, prof = PR["top"], PR["bas"], PR["zc"], PR["prof"]
    X = lambda x: x * k  # noqa: E731
    Z = lambda z: -z * k  # noqa: E731
    x_u = lambda v: (v + sn * PR["kb"]) * c  # noqa: E731 ; point du dessous d'abscisse v (le long de la pente)
    g0, g1 = x_u(PR["uc"] - PR["l"] / 2), x_u(PR["uc"] + PR["l"] / 2)
    n = (sn * prof, c * prof)                                   # vers le haut, perpendiculaire à la tablette
    pts = [(0, top(0)), (ET["p"], top(ET["p"])), (ET["p"], bas(ET["p"])), (g1, bas(g1)),
           (g1 + n[0], bas(g1) + n[1]), (g0 + n[0], bas(g0) + n[1]), (g0, bas(g0)), (0, bas(0))]
    xp = (MO["p"] + ET["p"]) / 2
    x_g0, x_g1 = 21, 28                                        # flèche du glissement, au-dessus de la tablette
    o = [rect(X(-3), Z(12), 0, Z(-14), "mur-h"), text(X(-1.5), Z(12) - 6, "mur", "lbl muted"),
         rect(0, Z(12), X(MO["p"]), Z(-14), "mont"),
         text(X(MO["p"] / 2), Z(12) - 6, "montant", "lbl"),
         poly("shelfc", [(X(x), Z(z)) for x, z in pts]),
         rect(X(ET["p"] - 2), Z(top(ET["p"]) + 2), X(ET["p"]), Z(top(ET["p"])), "shelfc"),
         f'<circle class="acier" cx="{f(X(MO["x_ar"]))}" cy="{f(Z(r))}" r="{f(r * k)}"/>',
         f'<circle class="acier" cx="{f(X(MO["x_av"]))}" cy="{f(Z(zc))}" r="{f(r * k)}"/>',
         fleche(X(xp), Z(top(xp) + 7), X(xp), Z(top(xp))),
         text(X(xp) + 6, Z(top(xp) + 5), "ce qui est posé", "lbl", "start"),
         fleche(X(MO["x_av"]), Z(zc - 7), X(MO["x_av"]), Z(zc - r)),
         fleche(X(MO["x_ar"]), Z(2 * r + 6), X(MO["x_ar"]), Z(2 * r)),
         f'<g class="glis">{fleche(X(x_g0), Z(top(x_g0) + 4), X(x_g1), Z(top(x_g1) + 4))}</g>',
         text(X(x_g1) + 5, Z(top(x_g1) + 4) + 3, "pousse à glisser", "lbls", "start"),
         rappel(X(MO["x_ar"]) + r * k, Z(r) - r * k, X(14), Z(9), "cheville arrière, dessus : retient l'arrière, qui veut se soulever", "start"),
         rappel(X(g1 + n[0] / 2), Z(bas(g1) + n[1] / 2), X(14), Z(-12.3),
                f"rainure {cm(PR['l'] * 10)} × {cm(PR['prof'] * 10)} mm à la défonceuse : la cheville avant y est prise, la tablette ne peut plus avancer", "start"),
         rappel(X(MO["x_av"]), Z(zc - 5), X(14), Z(-14.8), "cheville avant, dessous : porte la tablette", "start"),
         text(X(ET["p"]) + 6, Z(top(ET["p"]) + 1) + 3, "rebord 2 × 2 collé", "lbls", "start"),
         cote_v(Z(top(0)), Z(top(ET["p"])), X(ET["p"]) + 90, cm(top(0) - top(ET["p"])))]
    label = _label(aria, "Présentoir penché vers la pièce, profil")
    return (f'<svg style="max-width:720px" viewBox="{f(-6 * k)} {f(-15.5 * k)} {f(62 * k)} {f(31 * k)}" role="img" '
            f'aria-label="{label}">{"".join(o)}</svg>')


# ------------------------------------------------------------------ découpe (ET:617-752)
def refente(e, aria=""):
    """Les plans de travail vus de dessus, refendus en bandes, tablettes rangées dans les bandes (échelle × 2,6)."""
    k, gap = 2.6, 34
    o, y = [], 0
    for i, bandes_p in enumerate(e.panneaux):
        o += [rect(0, y, PANNEAU["l"] * k, y + PANNEAU["p"] * k, "mur-h"),
              text(0, y - 6, f"Plan P{i + 1}, {PANNEAU['nom']}", "lbl", "start")]
        for j, bande in enumerate(bandes_p):
            by = y + j * (ET["p"] + KERF) * k
            x = DRESSAGE
            for t in bande:
                o += [rect(x * k, by, (x + t["l"]) * k, by + ET["p"] * k, "shelfc"),
                      text((x + t["l"] / 2) * k, by + ET["p"] * k / 2 + 3, f'{t["rep"]}, {cm(t["l"])}', "lbl")]
                x += t["l"] + KERF
            if PANNEAU["l"] - x > 20:
                o.append(text((x + (PANNEAU["l"] - x) / 2) * k, by + ET["p"] * k / 2 + 3,
                              f'chute {cm(PANNEAU["l"] - x)}', "lbls muted"))
            # chant d'usine (arrondi) : devant de la tablette, côté extérieur du panneau
            yc = by if j == 0 else by + ET["p"] * k
            o.append(f'<line x1="0" y1="{f(yc)}" x2="{f(PANNEAU["l"] * k)}" y2="{f(yc)}" '
                     f'stroke="var(--tri)" stroke-width="1.6"/>')
        o += [cote_v(y, y + ET["p"] * k, -10, f(ET["p"])),
              cote_v(y + (ET["p"] + KERF) * k, y + (2 * ET["p"] + KERF) * k, -10, f(ET["p"])),
              cote_v(y, y + PANNEAU["p"] * k, -30, f(PANNEAU["p"]))]
        y += PANNEAU["p"] * k + gap
    o.append(cote_h(0, PANNEAU["l"] * k, y - gap + 16, f(PANNEAU["l"])))
    label = _label(aria, "Plan de découpe des plans de travail en chêne")
    return (f'<svg style="max-width:820px" viewBox="-45 -18 {f(PANNEAU["l"] * k + 60)} {f(y + 4)}" role="img" '
            f'aria-label="{label}">{"".join(o)}</svg>')


def barres(e, aria=""):
    """Tasseaux (montants) et ronds (chevilles), échelle × 2,6."""
    k, o, y = 2.6, [], 0
    for i in range(N_TASSEAUX):
        n = min(PAR_TASSEAU, MO["n"] - i * PAR_TASSEAU)
        o += [rect(0, y, TASSEAU["l"] * k, y + TASSEAU["s"][1] * k, "mur-h"),
              text(-6, y + TASSEAU["s"][1] * k / 2 + 3, f"tasseau {i + 1}", "lbls", "end")]
        x = 0
        for _ in range(n):
            o += [rect(x * k, y, (x + L_MONTANT) * k, y + TASSEAU["s"][1] * k, "mont"),
                  f'<text class="lbls" x="{f((x + L_MONTANT / 2) * k)}" y="{f(y + TASSEAU["s"][1] * k / 2 + 3)}" '
                  f'text-anchor="middle" style="fill:#fff">M, {cm(L_MONTANT)}</text>']
            x += L_MONTANT + KERF
        if TASSEAU["l"] - x > 1:
            o.append(text((x + (TASSEAU["l"] - x) / 2) * k, y + TASSEAU["s"][1] * k / 2 + 3,
                          f'chute {cm(TASSEAU["l"] - x)} : gabarit et essai', "lbls"))
        y += TASSEAU["s"][1] * k + 10
    o.append(cote_h(0, TASSEAU["l"] * k, y + 6, f'tasseau {cm(TASSEAU["l"])}'))
    y += 26
    kr = TASSEAU["l"] * k / ROND["l"]          # ronds à la même largeur de dessin que les tasseaux
    for i in range(e.n_ronds):
        o += [rect(0, y, ROND["l"] * kr, y + 6, "acier"),
              text(-6, y + 6, f"rond {i + 1}", "lbls", "end")]
        for j in range(1, e.par_rond):
            xx = j * (ET["cheville"] + KERF_METAL) * kr
            o.append(f'<line x1="{f(xx)}" y1="{f(y - 2)}" x2="{f(xx)}" y2="{f(y + 8)}" stroke="var(--ink)" stroke-width=".8"/>')
        y += 16
    o.append(cote_h(0, (ET["cheville"]) * kr, y + 4, f'C, {cm(ET["cheville"])}'))
    o.append(cote_h(0, ROND["l"] * kr, y + 22, f'rond {f(ROND["l"])} : {e.par_rond} chevilles'))
    label = _label(aria, "Débit des tasseaux et des ronds")
    return (f'<svg style="max-width:820px" viewBox="-60 -6 {f(TASSEAU["l"] * k + 70)} {f(y + 30)}" role="img" '
            f'aria-label="{label}">{"".join(o)}</svg>')


def percage(e, aria=""):
    """Un montant couché, bas à gauche : flanc (deux colonnes de trous traversants) et face avant (vis de fixation
    dans leurs lamages), échelle × 6."""
    k, L = 6, L_MONTANT
    r = MO["trou"] / 2
    av = [z - MO["z0"] for z in MO["trous_av"]]
    ar = [z - MO["z0"] for z in MO["trous_ar"]]
    vis = [5, L / 2 + 0.5, L - 4]          # hauteurs des vis depuis le bas (5, 60, 115 pour 119)
    X = lambda z: z * k  # noqa: E731
    o = []
    # flanc : x = 0 (mur) en haut, x = p (pièce) en bas
    yf = 40
    W = lambda x: yf + x * k  # noqa: E731
    o += [rect(0, W(0), X(L), W(MO["p"]), "mont"),
          text(0, yf - 30, "flanc (les deux flancs sont percés de part en part)", "lbl", "start"),
          text(X(L), yf - 30, "côté mur en haut", "lbls muted", "end")]
    o += [f'<circle class="trou" cx="{f(X(z))}" cy="{f(W(MO["x_av"]))}" r="{f(r * k)}"/>' for z in av]
    o += [f'<circle class="trou" cx="{f(X(z))}" cy="{f(W(MO["x_ar"]))}" r="{f(r * k)}"/>' for z in ar]
    o += [cote_h(0, X(ar[0]), yf - 8, cm(ar[0])),
          cote_h(X(ar[0]), X(ar[-1]), yf - 8, f'arrière : {len(ar) - 1} × {MO["pas_trous"]} = {cm(ar[-1] - ar[0])}'),
          cote_h(X(ar[-1]), X(L), yf - 8, cm(L - ar[-1])),
          cote_h(0, X(av[0]), W(MO["p"]) + 16, cm(av[0])),
          cote_h(X(av[0]), X(av[-1]), W(MO["p"]) + 16, f'avant : {len(av) - 1} × {MO["pas_trous"]} = {cm(av[-1] - av[0])}'),
          cote_h(X(av[-1]), X(L), W(MO["p"]) + 16, cm(L - av[-1])),
          cote_v(W(0), W(MO["x_ar"]), -8, f(MO["x_ar"])),
          cote_v(W(MO["x_ar"]), W(MO["x_av"]), -8, f(MO["x_av"] - MO["x_ar"])),
          cote_v(W(MO["x_av"]), W(MO["p"]), -8, f(MO["p"] - MO["x_av"])),
          cote_v(W(0), W(MO["p"]), X(L) + 14, f(MO["p"]))]
    # face avant, sous le flanc
    ya = W(MO["p"]) + 60
    A = lambda y: ya + y * k  # noqa: E731
    o += [rect(0, A(0), X(L), A(MO["l"]), "mont"),
          text(0, ya - 8, "face avant, côté pièce (pas de trous de cheville)", "lbl", "start")]
    for z in vis:
        o += [f'<circle cx="{f(X(z))}" cy="{f(A(MO["l"] / 2))}" r="{f(0.75 * k)}" fill="none" stroke="#fff" stroke-width=".8"/>',
              f'<circle cx="{f(X(z))}" cy="{f(A(MO["l"] / 2))}" r="{f(0.3 * k)}" fill="#fff"/>']
    zs = [0] + vis + [L]
    o += [cote_h(X(a), X(b), A(MO["l"]) + 16, cm(b - a)) for a, b in zip(zs, zs[1:])]
    o += [cote_v(A(0), A(MO["l"]), X(L) + 14, cm(MO["l"])),
          text(0, A(MO["l"]) + 34, f"bas du montant (z {MO['z0']})", "lbls muted", "start"),
          text(X(L), A(MO["l"]) + 34, f"haut (z {MO['z1']})", "lbls muted", "end")]
    label = _label(aria, "Plan de perçage d'un montant")
    return (f'<svg viewBox="-30 0 {f(X(L) + 60)} {f(A(MO["l"]) + 42)}" role="img" '
            f'aria-label="{label}">{"".join(o)}</svg>')


def entaille(e, aria=""):
    """Bout nord d'une tablette vu de dessus (mur en haut) : entaille, montant, chevilles (échelle × 5)."""
    k, long = 5, ET["debord"] + 44
    e_l, e_p = ET["entaille"]
    l, ce, r = MO["l"], ET["cheville_ext"], MO["trou"] / 2
    a = ET["debord"]                        # axe du montant depuis le bout de la tablette
    X = lambda y: y * k  # noqa: E731
    Y = lambda x: 24 + x * k  # noqa: E731
    o = [rect(X(-3), Y(-3), X(long), Y(0), "mur-h"),
         text(X(long), Y(-3) - 4, "mur", "lbls muted", "end"),
         f'<path class="shelfc" d="M0 {f(Y(0))} H{f(X(a - e_l / 2))} V{f(Y(e_p))} H{f(X(a + e_l / 2))} '
         f'V{f(Y(0))} H{f(X(long))} V{f(Y(ET["p"]))} H0 Z"/>',
         rect(X(a - l / 2), Y(0), X(a + l / 2), Y(MO["p"]), "mont"),
         rect(X(a - l / 2 - ce), Y(MO["x_ar"] - r), X(a + l / 2 + ce), Y(MO["x_ar"] + r), "acier"),
         rect(X(a - l / 2 - ce), Y(MO["x_av"] - r), X(a + l / 2 + ce), Y(MO["x_av"] + r), "acierh"),
         rect(X(a - RA["long"] / 2), Y(MO["x_av"] - RA["l"] / 2), X(a + RA["long"] / 2), Y(MO["x_av"] + RA["l"] / 2), "rain"),
         text(X(a + RA["long"] / 2) + 4, Y(MO["x_av"]) + 3, f"rainure dessous, {f(RA['long'])} de long", "lbls", "start"),
         cote_h(0, X(a - e_l / 2), Y(ET["p"]) + 14, cm(a - e_l / 2)),
         cote_h(X(a - e_l / 2), X(a + e_l / 2), Y(ET["p"]) + 14, cm(e_l)),
         cote_h(0, X(a), Y(ET["p"]) + 32, f"{f(a)} : axe"),
         cote_h(X(a), X(a + PAS) if a + PAS < long else X(long), Y(ET["p"]) + 32,
                f'puis {PAS} d\'axe en axe →'),
         cote_v(Y(0), Y(e_p), -12, cm(e_p)),
         cote_v(Y(0), Y(ET["p"]), X(long) + 14, f(ET["p"])),
         text(X(long / 2 + 6), Y(ET["p"] / 2), "tablette (dessus)", "lbls"),
         text(X(long / 2 + 6), Y(ET["p"]) - 6, "chant arrondi d'usine, devant", "lbls muted")]
    label = _label(aria, "Entaille d'une tablette")
    return (f'<svg style="max-width:560px" viewBox="-34 0 {f(X(long) + 60)} {f(Y(ET["p"]) + 42)}" role="img" '
            f'aria-label="{label}">{"".join(o)}</svg>')


DESSINS: dict[str, Callable] = {
    "mini": mini, "elevation": elevation, "dessus": dessus, "iso": iso, "detail": detail, "profil": profil,
    "travee": travee, "presentoir": presentoir, "refente": refente, "barres": barres, "percage": percage,
    "entaille": entaille,
}


# ------------------------------------------------------------------ légendes : les textes alternatifs
def legendes(e) -> dict[str, str]:
    """Textes qui suivaient les dessins dans l'ancienne page (ET:821-916), sans balise ni échappement."""
    arr = MO["x_av"] - MO["x_ar"]
    bandes_n = sum(len(p) for p in e.panneaux)
    t1 = calculs.etat("actuelle").ts[0]
    pos = ", ".join(cm(x) for x in t1["entailles"])
    return {
        "elevation": (
            f"Disposition {e.nom}, le mur ouest vu depuis la pièce (le sud, côté passage, à gauche ; le coin nord à "
            f"droite). L'enfilade est en tireté : les montants ne la touchent pas ({cm(MO['z0'] - EN['z1'])} de vide "
            f"au-dessus d'elle) et ne touchent pas le plafond ({cm(H - MO['z1'])} dessous). {MO['n']} montants M1 à M5 "
            f"du nord au sud, à {PAS} d'axe en axe, centrés sur l'enfilade ; {len(e.ts)} tablettes ({e.kit}), "
            f"{cm(e.metres)} m en tout ; repère, longueur et hauteur du dessus au-dessus de chacune. Chaque tablette "
            f"déborde de {ET['debord']} au-delà de l'axe de ses montants extrêmes ; aux deux bouts du mur, les "
            f"tablettes dépassent de {cm(ET['debord'] - MO['axes'][0] + EN['y0'])} les bouts de l'enfilade "
            f"({cm(MO['axes'][-1] - MO['axes'][0] + 2 * ET['debord'])} sur {cm(EN['y1'] - EN['y0'])}). Les petits "
            "rectangles gris sont les bouts des chevilles, de part et d'autre de chaque montant."),
        "dessus": (
            "Vues de dessus, vues depuis la pièce (le mur ouest en haut, le sud à gauche), les tablettes rangées du "
            "haut vers le bas sur quelques bandes (la hauteur de chacune est dans son étiquette) : la tablette touche "
            f"le mur, les montants noirs {cm(MO['l'])} × {MO['p']} sont dans ses entailles ; chevilles arrière en gris "
            f"plein (sur la tablette), chevilles avant en tireté (dessous). Devant les montants, il reste "
            f"{f(ET['x1'] - MO['p'])} pour les livres. Le tireté du fond est l'enfilade, {EN['p']} de profondeur : les "
            f"tablettes s'arrêtent à {f(ET['x1'])} du mur, {f(EN['p'] - ET['x1'])} en retrait de sa façade."),
        "iso": (
            f"Disposition {e.nom} en vue isométrique, depuis la pièce, côté sud et en hauteur (le mur ouest au fond, "
            f"le sud à gauche ; l'enfilade n'est pas dessinée) : {MO['n']} montants noirs qui traversent les "
            f"{len(e.ts)} tablettes en chêne par leurs entailles, et les bouts des chevilles d'acier de part et "
            "d'autre de chaque montant."),
        "detail": (
            "Détail agrandi, en coupe (le même dans toutes les dispositions) : un montant et une tablette, coupée à 20 "
            "du mur et, côté sud (devant à gauche), au ras du bout des chevilles. Le montant passe dans l'entaille de "
            f"{cm(ET['entaille'][0])} × {cm(ET['entaille'][1])} ; la cheville avant (à {MO['x_av']} du mur) dépasse "
            f"sous la tablette, la cheville arrière (à {MO['x_ar']}) dessus, de {cm(ET['cheville_ext'])} de chaque "
            "côté du montant."),
        "profil": (
            f"Profil juste à côté d'un montant. La tablette va jusqu'au mur ({ET['p']} de profondeur) et le montant "
            f"passe dans une entaille de {cm(ET['entaille'][0])} × {cm(ET['entaille'][1])}. Deux chevilles en acier "
            f"Ø 10 × {cm(ET['cheville'])}, peintes en noir, traversent le montant d'un flanc à l'autre et dépassent de "
            f"{cm(ET['cheville_ext'])} de chaque côté sous les joues de l'entaille. La cheville avant (à {MO['x_av']} "
            f"du mur), sous la tablette, la porte ; la cheville arrière (à {MO['x_ar']}), sur la tablette, l'empêche "
            f"de basculer vers l'avant. Les deux colonnes de trous sont décalées de {cm(MO['decalage'])} : "
            "l'épaisseur de la tablette plus une cheville, moins la rainure."),
        "travee": (
            f"Une travée vue de face : la tablette passe devant les montants et déborde de {ET['debord']} au-delà de "
            f"l'axe du dernier (≈ {cm(ET['debord'] - MO['l'] / 2)} au-delà du bois), ce qui permet deux tablettes au "
            f"même niveau sur des montants voisins sans se toucher ({cm(PAS - 2 * ET['debord'])} d'écart). Niveaux à "
            "35 : sept pas de trous, des livres jusqu'à 30."),
        "presentoir": (
            "Profil juste à côté d'un montant (comme le profil à plat de la section Le meuble). La tablette est "
            "pincée : le poids posé devant la fait pivoter sur la cheville avant, qui la porte par-dessous ; "
            "l'arrière veut alors se soulever et la cheville arrière, par-dessus, l'en empêche. Comme à plat, la "
            "cheville avant est prise dans une rainure sous la tablette, plus profonde ici "
            f"({cm(PR['prof'] * 10)} mm au lieu de {cm(RA['prof'] * 10)}) parce que la tablette penchée descend de "
            f"{cm(arr * PR['t'])} d'une cheville à l'autre. Le dessus reste plein ; entailles de 7,7 de profondeur au "
            f"lieu de {cm(ET['entaille'][1])} (le montant traverse la tablette de biais). Un rebord de 2 × 2 collé "
            f"devant retient ce qui est posé ; le devant descend de {cm(ET['p'] * PR['t'])}."),
        "refente": (
            f"Disposition {e.nom} : {len(e.panneaux)} plans de {PANNEAU['l']} × {PANNEAU['p']}, refendus en "
            f"{bandes_n} bandes de {ET['p']} (trait de scie {cm(KERF * 10)} mm, il reste "
            f"{cm(PANNEAU['p'] - 2 * ET['p'] - KERF)} pour dresser) ; les bouts sont d'abord recoupés d'équerre "
            f"({cm(DRESSAGE * 10)} mm). En rouge, le chant arrondi d'usine : il fait le devant de chaque tablette, le "
            "trait de refente va contre le mur. Les longueurs se coupent après la refente, à la scie circulaire sur "
            "rail."),
        "barres": (
            f"{N_TASSEAUX} tasseaux de {cm(TASSEAU['l'])} : {PAR_TASSEAU} montants de {cm(L_MONTANT)} par tasseau ; il "
            f"ne reste que {cm(TASSEAU['l'] - PAR_TASSEAU * L_MONTANT - KERF)} sur les deux premiers, à mesurer en "
            f"magasin (bouts fendus : prendre un tasseau de plus). {e.n_ronds} ronds de 1 m : {e.par_rond} chevilles "
            f"de {cm(ET['cheville'])} par rond (trait de scie à métaux {cm(KERF_METAL * 10)} mm), "
            f"{e.n_ronds * e.par_rond} en tout pour {e.chevilles} utiles."),
        "percage": (
            f"Le même pour toutes les dispositions. Les cotes partent du bas du montant (z {MO['z0']}). Colonne "
            f"arrière à {MO['x_ar']} du mur, colonne avant à {MO['x_av']} : {len(MO['trous_av'])} trous Ø 10 par "
            f"colonne, tous les {MO['pas_trous']}, traversants (les deux flancs). Les deux colonnes sont décalées de "
            f"{cm(MO['decalage'])} en hauteur, l'épaisseur de la tablette plus une cheville moins la rainure "
            f"({cm(RA['prof'] * 10)} mm) : avec une tablette de {cm(PANNEAU['ep'])}, ce décalage devient "
            f"{cm(PANNEAU['ep'] + MO['trou'] - RA['prof'])}. Face avant : {EU['vis']} vis 6 × 120 dans des lamages Ø 15 "
            "de 1 de profondeur, rebouchés et peints ; elles passent entre les trous."),
        "entaille": (
            f"Les entailles se taillent dans le chant arrière : deux traits de scie sauteuse (ou scie à main) de "
            f"{cm(ET['entaille'][1])}, puis le fond au ciseau à bois ; {cm(ET['entaille'][0] - MO['l'])} de jeu en "
            f"largeur, {cm(ET['entaille'][1] - MO['p'])} en profondeur. Elles sont à {ET['debord']} de chaque bout "
            f"puis à {PAS} l'une de l'autre (sur une 244, à {pos} du bout sud)."),
    }


# ------------------------------------------------------------------ mise à l'échelle et cadrage
def en_cm(svg: str, k: float) -> str:
    """Le dessin à l'échelle du centimètre : viewBox divisé par k (à 0,001 près), contenu réduit d'autant."""
    def vb(m):
        return 'viewBox="' + " ".join(f"{round(float(v) / k, 3):g}" for v in m.group(1).split()) + '"'
    tete = re.match(r"<svg[^>]*>", svg).group(0)
    return (re.sub(r'viewBox="([^"]*)"', vb, tete, count=1) + f'<g transform="scale({1 / k:.6g})">'
            + svg[len(tete):-len("</svg>")] + "</g></svg>")


def _vb(svg):
    return [float(v) for v in re.search(r'<svg[^>]*\bviewBox="([^"]*)"', svg).group(1).split()]


def cadre_commun(svgs: Sequence[str]) -> str:
    """ViewBox « x y l h » de l'union des viewBox des dessins donnés."""
    boites = [_vb(s) for s in svgs]
    x0, y0 = min(b[0] for b in boites), min(b[1] for b in boites)
    x1, y1 = max(b[0] + b[2] for b in boites), max(b[1] + b[3] for b in boites)
    return f"{f(x0)} {f(y0)} {f(x1 - x0)} {f(y1 - y0)}"


def recadrer(svg: str, viewbox: str) -> str:
    """Le même dessin, viewBox de tête remplacé."""
    tete = re.match(r"<svg[^>]*>", svg).group(0)
    return re.sub(r'viewBox="[^"]*"', f'viewBox="{viewbox}"', tete, count=1) + svg[len(tete):]


# ------------------------------------------------------------------ CSS des classes dessinées
# Repris du CSS de l'ancienne page (3d/salon/plan.py l. 412-470, ET:1102-1104), sur les jetons de commun/site.css ;
# les étiquettes ont leur couleur (hors de la scène, `.scene svg text` ne s'applique pas), les cotes la police du site.
CSS = """.bgwall{fill:var(--line);fill-opacity:.35}
.upper{fill:none;stroke:var(--ink);stroke-width:.8;stroke-dasharray:3 2}
.mont{fill:#26262A;stroke:var(--ink);stroke-width:.4}
.shelfc{fill:var(--wood);stroke:var(--ink);stroke-width:.6}
.floorl{stroke:var(--ink);stroke-width:2}
.ceil{stroke:var(--muted);stroke-width:1;stroke-dasharray:6 4}
.acier{fill:#8E9399;stroke:var(--ink);stroke-width:.4}
.acierh{fill:none;stroke:#5E6369;stroke-width:.8;stroke-dasharray:2 1.5}
.mur-h{fill:var(--line);fill-opacity:.6;stroke:var(--muted);stroke-width:.5}
.trou{fill:var(--paper)}
.rain{fill:none;stroke:var(--ink);stroke-width:.9;stroke-dasharray:4 2}
.fl{stroke:#c2410c;stroke-width:1.6;fill:none}.flh{fill:#c2410c}
.glis .fl{stroke:#4d9a3a}.glis .flh{fill:#4d9a3a}
.dim{stroke:var(--muted);stroke-width:.6;fill:none}
.dimt{fill:var(--muted);font-family:var(--ui);font-weight:600;font-variant-numeric:tabular-nums;font-size:8px}
.lbl{fill:var(--ink);font-size:7.5px}
.lbls{fill:var(--ink);font-size:6.5px}
.muted{fill:var(--muted)}
.dispos{display:grid;grid-template-columns:repeat(auto-fill,minmax(220px,1fr));gap:10px;margin:14px 0}
.dispo{display:flex;flex-direction:column;gap:4px;padding:10px;border:1px solid var(--line);border-radius:12px;background:var(--panel);color:var(--ink);text-decoration:none}
.dispo[aria-current="page"]{border-color:var(--ink);box-shadow:0 0 0 1px var(--ink)}
.dispo svg{display:block;width:100%;height:auto}
.dispo span{font-size:13px;color:var(--muted)}
"""
