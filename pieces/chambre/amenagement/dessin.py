"""Dessins de la chambre : plan vu de dessus, légende et styles des dessins.

Repris du plan de l'ancienne page chambre-amenagement.html (V2.1, tests/fixtures/chambre/). Chaque fonction reçoit le
module `M` (document.py) au lieu de le lire dans une variable globale. Étiquettes, cotes et passages sont calculés du
modèle ; les textes de l'ancienne page sont repris tels quels (point médian remplacé par une virgule).

Écarts avec l'ancien dessin : classes `rail` → `tringle`, `app` → `filet`, `mf` → `passm` ; quadrillage retiré ;
marqueurs `tk` et `ar` dans les `<defs>` de chaque dessin, suffixés par son repère (`tk-plan`).

Calques du plan (classes des éléments SVG) : cotes .dim .dimt | passages .pass .passm .passt | voisines .room .roomt
"""

import math
from html import escape

from commun.dessin import f, rect, rot


# ------------------------------------------------------------------ outils de tracé
def _texte(x, y, html, cls, anchor="middle", extra=""):
    """Un <text> dont le contenu est déjà du HTML (pour les `<tspan class="lblb">①</tspan>`)."""
    return f'<text class="{cls}" x="{f(x)}" y="{f(y)}" text-anchor="{anchor}"{extra}>{html}</text>'


def _numero(n):
    return f'<tspan class="lblb">{n}</tspan>'


def _defs(k):
    """Marqueurs du dessin de repère `k` : tick de cote `tk-<k>`, flèche `ar-<k>`."""
    return (f'<defs><marker id="tk-{k}" viewBox="0 0 10 10" refX="5" refY="5" markerWidth="7" markerHeight="7" '
            f'orient="auto"><path class="tkm" d="M2 8 L8 2" stroke-width="1.4"/></marker>'
            f'<marker id="ar-{k}" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="6" markerHeight="6" '
            f'orient="auto"><path class="arm" d="M0 0 L10 5 L0 10 Z"/></marker></defs>')


def _cote(a, b, label, t, k="plan"):
    """Cote de a à b (ticks `tk-<k>` aux deux bouts), texte au point t, tourné si la cote est verticale."""
    vertical = a[0] == b[0]
    return (f'<path class="dim" d="M{f(a[0])} {f(a[1])} L{f(b[0])} {f(b[1])}" marker-start="url(#tk-{k})" '
            f'marker-end="url(#tk-{k})"/>'
            + _texte(t[0], t[1], escape(str(label)), "dimt", extra=rot(*t) if vertical else ""))


def _passage(a, b):
    """Passage libre de a à b, sa longueur à droite du trait vertical, au-dessus du trait horizontal."""
    d = f"{math.dist(a, b):.0f}"
    xm, ym = (a[0] + b[0]) / 2, (a[1] + b[1]) / 2
    t = _texte(xm + 4, ym + 4.5, d, "passt", "start") if a[0] == b[0] else _texte(xm, ym - 3, d, "passt")
    return (f'<path class="pass" d="M{f(a[0])} {f(a[1])} L{f(b[0])} {f(b[1])}"/>'
            + "".join(f'<circle class="passm" cx="{f(p[0])}" cy="{f(p[1])}" r="1.3"/>' for p in (a, b)) + t)


def _dims(m):
    """Largeur (x) et profondeur (y) d'un meuble."""
    return m["x1"] - m["x0"], m["y1"] - m["y0"]


# ------------------------------------------------------------------ plan vu de dessus
def plan_svg(M, aria="Plan de la chambre", zones=""):
    L, P, EP, pl, po, fe = M.L, M.P, M.EP, M.PLACARD, M.PORTE, M.FENETRE
    o = []
    # pièces voisines et sol
    o.append(rect(-130, 0, -EP["o"], 160, "room"))
    o.append(_texte(-70, 90, "Couloir", "roomt"))
    o.append(rect(-EP["o"], -60, L + EP["e"], -EP["n"], "room"))
    o.append(_texte(401, -40, "Salon", "roomt"))
    o.append(rect(0, 0, L, P, "appf")[:-2] + ' style="stroke:none"/>')
    # placard existant : cloison nord, jambages de la porte, deux vantaux coulissants
    o.append(rect(pl["x0"], pl["y0"], pl["x1"], pl["y1"], "closet"))
    xp, yp = (pl["x0"] + pl["x1"]) / 2 - 2, 190
    o.append(_texte(xp, yp, f'Placard existant, {pl["y1"] - pl["y0"] - pl["cloison"]}', "lblx muted", extra=rot(xp, yp)))
    o.append(rect(pl["x0"], pl["y0"], pl["x1"], pl["y0"] + pl["cloison"], "w"))
    a, b = pl["porte"]
    o.append(rect(pl["x1"] - pl["jambage"], pl["y0"], pl["x1"], a, "w"))
    o.append(rect(pl["x1"] - pl["jambage"], b, pl["x1"], pl["y1"], "w"))
    vantail = (b - a + pl["recouvrement"]) / 2
    o.append(f'<line class="tringle" x1="{f(pl["x1"] - 2.5)}" y1="{f(a)}" x2="{f(pl["x1"] - 2.5)}" y2="{f(a + vantail)}"/>')
    o.append(f'<line class="tringle" x1="{f(pl["x1"] - 4.5)}" y1="{f(b - vantail)}" x2="{f(pl["x1"] - 4.5)}" y2="{f(b)}"/>')
    xp, yp = pl["x1"] + 6, 200
    o.append(_texte(xp, yp, f"porte du placard {b - a}", "lblx muted", extra=rot(xp, yp)))
    # murs, décroché, fenêtre
    o.append(rect(-EP["o"], -EP["n"], L + EP["e"], 0, "w"))
    o.append(rect(-EP["o"], P, L + EP["e"], P + EP["s"], "w"))
    o.append(rect(-EP["o"], 0, 0, po["a"], "w"))
    o.append(rect(-EP["o"], po["b"], 0, P, "w"))
    o.append(rect(L, 0, L + EP["e"], fe["y0"], "w"))
    o.append(rect(L, fe["y1"], L + EP["e"], P, "w"))
    de = M.DECROCHE
    o.append(rect(de["x0"], de["y0"], de["x1"], de["y1"], "w"))
    o.append(rect(L, fe["y0"], L + EP["e"], fe["y1"], "win"))
    vf = (fe["y1"] - fe["y0"] + fe["recouvrement"]) / 2
    o.append(f'<line class="wleaf" x1="{f(L + 4)}" y1="{f(fe["y0"])}" x2="{f(L + 4)}" y2="{f(fe["y0"] + vf)}"/>')
    o.append(f'<line class="wleaf" x1="{f(L + 8)}" y1="{f(fe["y1"] - vf)}" x2="{f(L + 8)}" y2="{f(fe["y1"])}"/>')
    o.append(f'<path class="slide" d="M{f(L - 6)} 205 L{f(L - 6)} 175" marker-end="url(#ar-plan)"/>')
    xp, yp = L + 22, (fe["y0"] + fe["y1"]) / 2
    o.append(_texte(xp, yp, f'fenêtre coulissante {fe["y1"] - fe["y0"]}', "lbls muted", extra=rot(xp, yp)))
    # porte du couloir : charnière au nord (a), vantail ouvert à 90° le long du mur nord
    w = po["b"] - po["a"]
    arc = f'A{f(w)} {f(w)} 0 0 1 0 {f(po["b"])}'
    o.append(f'<path class="doorzone" d="M0 {f(po["a"])} L{f(w)} {f(po["a"])} {arc} Z"/>')
    o.append(f'<path class="doorarc" d="M{f(w)} {f(po["a"])} {arc}"/>')
    o.append(f'<line class="doorleaf" x1="0" y1="{f(po["a"])}" x2="{f(w)}" y2="{f(po["a"])}"/>')
    xp, yp = -20, (po["a"] + po["b"]) / 2
    o.append(_texte(xp, yp, "porte", "lblx muted", extra=rot(xp, yp)))
    # ① lit, couette, oreillers, tête de lit
    li, co, te = M.LIT, M.COUETTE, M.TETE
    o.append(rect(li["x0"], li["y0"], li["x1"], li["y1"], "mat", 4))
    o.append(rect(co["x0"], co["y0"], co["x1"], co["y1"], "duvet", 4))
    for r in M.OREILLERS:
        o.append(rect(r["x0"], r["y0"], r["x1"], r["y1"], "pil", 6))
    o.append(rect(te["x0"], te["y0"], te["x1"], te["y1"], "head"))
    xm = (li["x0"] + li["x1"]) / 2
    o.append(_texte(xm, 104, f'{_numero("①")} Lit {li["x1"] - li["x0"]} × {li["y1"] - li["y0"]}', "lbl"))
    o.append(_texte(xm, 114, f'sommier sur pieds, sans cadre, tête de lit murale {te["x1"] - te["x0"]}', "lbls"))
    o.append(_texte(xm, 123, "tête au mur sud", "lbls muted"))
    # ② chevets et appliques
    for ch, xa in zip((M.CHEVET_OUEST, M.CHEVET_EST), M.APPLIQUES["x"]):
        o.append(rect(ch["x0"], ch["y0"], ch["x1"], ch["y1"], "cab", 2))
        xc = (ch["x0"] + ch["x1"]) / 2
        o.append(_texte(xc, ch["y0"] + 16, _numero("②"), "lbls"))
        o.append(_texte(xc, ch["y0"] + 25, "%s × %s" % _dims(ch), "lblx"))
        o.append(f'<circle class="lamp" cx="{f(xa)}" cy="{f(ch["y1"] - 3)}" r="2"/>')
    # ③ commodes, joue, plan en transparence, tiroir ouvert
    cn, cs, jo, pn, ti, ni = M.COMMODE_NORD, M.COMMODE_SUD, M.JOUE, M.PLAN, M.TIROIR_OUVERT, M.NICHE
    o.append(rect(cn["x0"], cn["y0"], cn["x1"], cn["y1"], "cab"))
    o.append(rect(cs["x0"], cs["y0"], cs["x1"], cs["y1"], "cab"))
    o.append(rect(jo["x0"], jo["y0"], jo["x1"], jo["y1"], "cabcut"))
    o.append(rect(pn["x0"], pn["y0"], pn["x1"], pn["y1"], "head", 1).replace(' rx=', ' style="fill-opacity:.22" rx='))
    for c in (cn, cs):
        o.append(f'<line class="inner" x1="{f(c["x0"])}" y1="{f(c["y0"])}" x2="{f(c["x0"])}" y2="{f(c["y1"])}"/>')
    o.append(rect(ti["x0"], ti["y0"], ti["x1"], ti["y1"], "ghost"))
    xp, yp = (ti["x0"] + ti["x1"]) / 2, (ti["y0"] + ti["y1"]) / 2
    o.append(_texte(xp, yp, "tiroir ouvert", "lblx muted", extra=rot(xp, yp)))
    # ④ niche : barres de la niche, sous le plan
    for x, _ in ni["barres"]:
        o.append(f'<line class="tringle" x1="{f(x)}" y1="{f(ni["y0"] + 1)}" x2="{f(x)}" y2="{f(ni["y1"] - 1)}"/>')
    xp, yp = (pn["x0"] + pn["x1"]) / 2, 140
    lp, pp = _dims(pn)
    o.append(_texte(xp, yp, f'{_numero("③")} Plan {pp} × {lp} sur 2 commodes {cn["y1"] - cn["y0"]} × {cn["x1"] - cn["x0"]}',
                    "lblx", extra=rot(xp, yp)))
    # ④ patères
    pa = M.PATERES
    for y in pa["y"]:
        o.append(f'<circle class="peg" cx="{f(pa["x"])}" cy="{f(y)}" r="1.6"/>')
    xt = pn["x0"] - 4
    o.append(_texte(xt, 32, f'{_numero("④")} {len(pa["y"])} patères h {pa["z"]}', "lblx valett", "end"))
    o.append(_texte(xt, 39, "+ niche à pantalons sous le plan", "lblx valett", "end"))
    o.append(_texte(xt, 46, f'({len(ni["barres"])} barres)', "lblx valett", "end"))
    # climatisation, lampe
    cl, la = M.CLIM, M.LAMPE
    o.append(rect(cl["x0"], cl["y0"], cl["x1"], cl["y1"], "upper"))
    o.append(_texte((cl["x0"] + cl["x1"]) / 2, cl["y1"] - 8, "clim au plafond", "lblx muted"))
    o.append(f'<circle class="lamp" cx="{f(la["cx"])}" cy="{f(la["cy"])}" r="{f(la["r"])}" style="fill-opacity:.25"/>')
    # cotes et passages
    o.append(_cote((0, -24), (L, -24), L, (L / 2, -26.5)))
    o.append(_cote((pl["x1"], 273), (L, 273), L - pl["x1"], ((pl["x1"] + L) / 2, 283)))
    o.append(_cote((475, 0), (475, P), P, (472, P / 2)))
    o.append(_cote((-38, pl["y0"]), (-38, pl["y1"]), pl["y1"] - pl["y0"], (-41, (pl["y0"] + pl["y1"]) / 2)))
    for p in M.passages(M):
        o.append(_passage(p["a"], p["b"]))
    o.append(_texte((pl["x1"] + L) / 2, P + 9, "mur sud", "lblx muted"))
    role = "group" if zones else "img"
    return (f'<svg class="plan" viewBox="-140 -70 640 370" role="{role}" aria-label="{escape(aria)}">'
            f'{_defs("plan")}{"".join(o)}{zones}</svg>')


# ------------------------------------------------------------------ légende et textes sous les dessins
def legende():
    items = [('<rect x="0" y="0" width="26" height="14" class="bed"/>', "Lit"),
             ('<rect x="0" y="0" width="26" height="14" class="head"/>', "Tête de lit, plan"),
             ('<rect x="0" y="0" width="26" height="14" class="cab"/>', "Chevets, commodes"),
             ('<rect x="0" y="0" width="26" height="14" class="closet"/>', "Placard existant"),
             ('<rect x="0" y="0" width="26" height="14" class="doorzone"/>', "Débattement de porte"),
             ('<path d="M2 7 L24 7" class="pass"/>', "Passage (cm)")]
    return '<div class="legend">' + "".join(f'<span><svg viewBox="0 0 26 14">{s}</svg>{t}</span>' for s, t in items) + "</div>"


# Texte sous chaque dessin de l'ancienne page, repris tel quel : il devient l'aria-label du SVG.
ALTS = {
    "plan": ("Plan vu de dessus, 1 unité = 1 cm, nord en haut. On entre par le couloir à l'ouest (en haut à gauche). "
             "Le plan du mur est est dessiné en transparence : on voit dessous la niche à pantalons (deux barres) et les "
             "deux commodes ; le pointillé montre un tiroir ouvert."),
}


# Styles des dessins (le reste de la page, polices comprises, vient de commun/site.css). Règles de l'ancienne page ;
# `--cook2` de l'ancienne page, sans jeton du site, s'écrit #7B5EA7.
CSS = """
.legend{display:flex;flex-wrap:wrap;gap:6px 14px;font-size:13.5px;margin:6px 0}
.legend span{display:inline-flex;align-items:center;gap:6px}
.legend svg{width:26px;height:14px;flex:none}
.tkm{stroke:var(--muted)}
.arm{fill:var(--tri)}
.room{fill:var(--line);fill-opacity:.18}
.roomt{fill:var(--muted);font-size:9px;font-weight:600}
.w{fill:var(--ink)}
.appf{fill:var(--panel);stroke:var(--ink);stroke-width:.8}
.filet{fill:none;stroke:var(--ink);stroke-width:.8}
.tringle{stroke:var(--ink);stroke-width:1.1}
.closet{fill:var(--tech);stroke:var(--ink);stroke-width:.7}
.win{fill:var(--glass);stroke:var(--ink);stroke-width:.7}
.wleaf{stroke:var(--ink);stroke-width:2.2}
.slide{stroke:var(--tri);stroke-width:1;fill:none}
.doorzone{fill:var(--tri);fill-opacity:.06;stroke:none}
.doorarc{fill:none;stroke:var(--ink);stroke-width:.8}
.doorleaf{stroke:var(--ink);stroke-width:3}
.bed{fill:var(--water);fill-opacity:.10;stroke:var(--ink);stroke-width:.9}
.mat{fill:var(--panel);stroke:var(--ink);stroke-width:.6}
.pil{fill:var(--panel);stroke:var(--ink);stroke-width:.6}
.duvet{fill:var(--water);fill-opacity:.16;stroke:var(--water);stroke-width:.6}
.head{fill:var(--wood);fill-opacity:.45;stroke:var(--ink);stroke-width:.9}
.cab{fill:var(--cab);stroke:var(--ink);stroke-width:.7}
.cabcut{fill:var(--tall);stroke:var(--ink);stroke-width:1.4}
.inner{fill:none;stroke:var(--muted);stroke-width:.6;stroke-dasharray:3 2}
.ghost{fill:none;stroke:var(--muted);stroke-width:1;stroke-dasharray:4 3}
.upper{fill:none;stroke:var(--muted);stroke-width:.8;stroke-dasharray:3 2}
.lamp{fill:#E8B44A;fill-opacity:.55;stroke:var(--ink);stroke-width:.6}
.peg{fill:#7B5EA7}
.valett{fill:#7B5EA7;font-weight:700}
.pass{fill:none;stroke:var(--flow);stroke-width:.9}
.passm{fill:var(--flow)}
.passt{fill:var(--flow);font-size:7px;font-weight:600}
.dim{stroke:var(--muted);stroke-width:.6;fill:none}
.dimt{fill:var(--muted);font-size:8px}
.lbl{font-size:7.5px}
.lbls{font-size:6.5px}
.lblx{font-size:5px}
.lblb{font-size:9px;font-weight:700}
.muted{fill:var(--muted)}
"""
