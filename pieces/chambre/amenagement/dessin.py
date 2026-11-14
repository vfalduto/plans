"""Dessins de la chambre : plan vu de dessus, élévations des murs est, sud et ouest, légende et styles des dessins.

Repris des dessins de l'ancienne page chambre-amenagement.html (V2.1, tests/fixtures/chambre/). Chaque fonction reçoit le
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


# ------------------------------------------------------------------ élévations
# Repère d'une élévation : abscisse u le long du mur regardé, ordonnée SVG = H - z (sol à H, plafond à 0).
# est : u = y (nord à gauche) ; sud : u = L - x (est à gauche) ; ouest : u = P - y (sud à gauche).
# Constantes de dessin (tracés que la page ne cote pas) :
_DEBORD = 12                                # sol et plafond dépassent de 12 le nu des murs de chaque côté
_PANTALONS = ((28, 53, 67), (16, 41, 66))   # u des pantalons de la niche (mur est), barre du fond puis de devant
_PANTALON = (22, 14)                        # largeur d'un pantalon, z de son bas
_VETEMENT = (12, 2, 50)                     # vêtement sous une patère : largeur, écart sous la patère, hauteur
_PIED = 4                                   # pied du sommier : largeur et retrait depuis le bout du lit
_TIROIR_CHEVET = 55                         # z du filet du tiroir d'un chevet
_FIL = 10                                   # fil sous une applique
_POIGNEE_PORTE = (6, 105)                   # poignée de la porte du couloir : retrait depuis le bord, z


def _rz(H, u0, u1, z0, z1, cls, rx=0):
    """Rectangle d'élévation de u0 à u1 (dans un ordre ou l'autre) et de z0 à z1."""
    return rect(min(u0, u1), H - z1, max(u0, u1), H - z0, cls, rx)


def _ligne(cls, u0, y0, u1, y1):
    return f'<line class="{cls}" x1="{f(u0)}" y1="{f(y0)}" x2="{f(u1)}" y2="{f(y1)}"/>'


def _cadre(M, longueur, ep_gauche, ep_droite):
    """Sol, plafond et murs coupés de part et d'autre d'une élévation de `longueur`."""
    H = M.H
    return [_ligne("floorl", -_DEBORD, H, longueur + _DEBORD, H),
            _ligne("el-ceil", -_DEBORD, 0, longueur + _DEBORD, 0),
            _texte(2, -3, f"plafond {H}", "lblx muted", "start"),
            rect(-ep_gauche, 0, 0, H, "w"),
            rect(longueur, 0, longueur + ep_droite, H, "w")]


def _elevation(k, viewbox, o, aria):
    return (f'<svg class="coupe" viewBox="{viewbox}" role="img" aria-label="{escape(aria or ALTS[k])}">'
            f'{_defs(k)}{"".join(o)}</svg>')


def elevation_est(M, aria=""):
    """Mur est vu depuis le lit : niche à pantalons, commodes sous la fenêtre, patères ; lit et chevet en pointillés."""
    H, P, EP, fe = M.H, M.P, M.EP, M.FENETRE
    o = _cadre(M, P, EP["n"], EP["s"])
    o.append(_rz(H, 0, M.DECROCHE["y1"], 0, H, "bgwall"))
    # fenêtre coulissante : vantail fixe au nord, mobile au sud
    o.append(_rz(H, fe["y0"], fe["y1"], fe["allege"], fe["linteau"], "win"))
    c = fe["cadre"]
    v = (fe["y1"] - fe["y0"] - 2 * c - fe["joint"]) / 2
    fixe = fe["y0"] + c
    mobile = fixe + v + fe["joint"]
    for u in (fixe, mobile):
        o.append(_rz(H, u, u + v, fe["allege"] + c, fe["linteau"] - c, "filet"))
    o.append(f'<path class="slide" d="M{f(mobile + v - 11)} 90 L{f(mobile + 11)} 90" marker-end="url(#ar-est)"/>')
    o.append(_texte(fixe + v / 2, 87, "fixe", "lblx muted"))
    o.append(_texte(mobile + v / 2, 98, "coulisse vers le nord", "lblx muted"))
    o.append(_texte((fe["y0"] + fe["y1"]) / 2, H - fe["linteau"] - 4,
                    f'fenêtre coulissante {fe["y1"] - fe["y0"]}, allège {fe["allege"]}, linteau {fe["linteau"]}',
                    "lblx muted"))
    # ④ joue et niche à pantalons : la barre du fond (côté mur) d'abord, pantalons estompés
    jo, ni = M.JOUE, M.NICHE
    o.append(_rz(H, jo["y0"], jo["y1"], 0, jo["z1"], "cabcut"))
    barres = sorted(ni["barres"], reverse=True)
    for i, ((_, z), us) in enumerate(zip(barres, _PANTALONS)):
        for u in us[:ni["pantalons"]]:
            r = _rz(H, u, u + _PANTALON[0], _PANTALON[1], z, "cloth", 2)
            o.append(r[:-2] + ' style="opacity:.45"/>' if i < len(barres) - 1 else r)
        o.append(_ligne("tringle", ni["y0"], H - z, ni["y1"], H - z))
    um = (ni["y0"] + ni["y1"]) / 2
    o.append(_texte(um, H - max(z for _, z in barres) - 1, "barres h " + " / ".join(str(z) for _, z in barres),
                    "lblx valett"))
    o.append(_texte(um, 246, f'{_numero("④")} pantalons', "lblx valett"))
    # ③ deux commodes : séparations des tiroirs et poignées, puis le plan
    co = M.COMMODE
    for cm in (M.COMMODE_NORD, M.COMMODE_SUD):
        o.append(_rz(H, cm["y0"], cm["y1"], 0, cm["z1"], "cab"))
        for z in sorted(co["separations"], reverse=True):
            o.append(_ligne("filet", cm["y0"], H - z, cm["y1"], H - z))
        uc = (cm["y0"] + cm["y1"]) / 2
        for z in co["poignees"]:
            o.append(_rz(H, uc - co["poignee_l"] / 2, uc + co["poignee_l"] / 2, z, z + co["poignee_h"], "dark"))
    pn, cn, cs = M.PLAN, M.COMMODE_NORD, M.COMMODE_SUD
    o.append(_rz(H, pn["y0"], pn["y1"], pn["z1"] - pn["ep"], pn["z1"], "head"))
    lp, pp = _dims(pn)
    lc, pc = _dims(cn)
    o.append(_texte((cn["y0"] + cs["y1"]) / 2, H - pn["z1"] - 5,
                    f'{_numero("③")} plan {pp} × {lp}, h {pn["z1"]}, 2 commodes {pc} × {lc} h {cn["z1"]}', "lblx"))
    # ④ patères et vêtements
    pa = M.PATERES
    lv, ev, hv = _VETEMENT
    for u in pa["y"]:
        o.append(rect(u - lv / 2, H - pa["z"] + ev, u + lv / 2, H - pa["z"] + ev + hv, "cloth", 3))
        o.append(f'<circle class="peg" cx="{f(u)}" cy="{f(H - pa["z"])}" r="1.8"/>')
    o.append(_texte((pa["y"][0] + pa["y"][-1]) / 2, H - pa["z"] - 5,
                    f'{_numero("④")} {len(pa["y"])} patères h {pa["z"]}', "lblx valett"))
    # premier plan : chevet est, tête de lit, lit (sommier et matelas)
    ch, te, li = M.CHEVET_EST, M.TETE, M.LIT
    o.append(_rz(H, ch["y0"], ch["y1"], 0, ch["z1"], "ghost"))
    o.append(_rz(H, te["y0"], te["y1"], te["z0"], te["z1"], "ghost"))
    o.append(_rz(H, li["y0"], li["y1"], li["pieds"], li["z1"], "ghost"))
    o.append(_texte(177, 242, "lit au premier plan", "lblx muted"))
    cl = M.CLIM
    o.append(_rz(H, cl["y0"], cl["y1"], cl["z0"], cl["z1"], "tech"))
    o.append(_texte(cl["y1"] + 3, 14, "clim (mur nord)", "lblx muted", "start"))
    # cotes : trumeau nord, fenêtre, trumeau sud
    for a, b in ((0, fe["y0"]), (fe["y0"], fe["y1"]), (fe["y1"], P)):
        o.append(_cote((a, -10), (b, -10), b - a, ((a + b) / 2, -12), "est"))
    o.append(_texte(4, 262, "nord", "lblx muted", "start"))
    o.append(_texte(P - 4, 262, "sud", "lblx muted", "end"))
    return _elevation("est", "-35 -22 320 290", o, aria)


def elevation_sud(M, aria=""):
    """Mur sud vu depuis le pied du lit : bout du plan, chevets, tête de lit et lit, placard coupé."""
    H, L, EP, pl = M.H, M.L, M.EP, M.PLACARD
    o = _cadre(M, L, EP["e"], EP["o"])
    o.append(_rz(H, L - pl["x0"], L - pl["x1"], 0, H, "closet"))
    o.append(_rz(H, L - pl["x1"], L - pl["x1"] + pl["jambage"], 0, H, "wcut"))
    xp, yp = L - (pl["x0"] + pl["x1"]) / 2, 120
    o.append(_texte(xp, yp, "placard existant (coupe)", "lblx muted", extra=rot(xp, yp)))
    # ③ bout de la commode sud et du plan
    cs, pn = M.COMMODE_SUD, M.PLAN
    o.append(_rz(H, L - cs["x0"], L - cs["x1"], 0, cs["z1"], "cab"))
    o.append(_rz(H, L - pn["x0"], L - pn["x1"], pn["z1"] - pn["ep"], pn["z1"], "head"))
    o.append(_texte(L - (pn["x0"] + pn["x1"]) / 2, H - pn["z1"] - 4, f'{_numero("③")} plan h {pn["z1"]}', "lblx"))
    # ① tête de lit, pieds, sommier, matelas, oreillers
    te, li = M.TETE, M.LIT
    o.append(_rz(H, L - te["x0"], L - te["x1"], te["z0"], te["z1"], "head", 2))
    for x in (li["x0"] + _PIED, li["x1"] - 2 * _PIED):
        o.append(_rz(H, L - x, L - x - _PIED, 0, li["pieds"], "dark"))
    z_sommier = li["pieds"] + li["sommier"]
    o.append(_rz(H, L - li["x0"], L - li["x1"], li["pieds"], z_sommier, "bed", 2))
    o.append(_rz(H, L - li["x0"], L - li["x1"], z_sommier, li["z1"], "mat", 4))
    for r in reversed(M.OREILLERS):
        o.append(_rz(H, L - r["x0"], L - r["x1"], r["z0"], r["z1"], "pil", 6))
    o.append(_texte(L - (te["x0"] + te["x1"]) / 2, 128, f'{_numero("①")} Tête de lit murale h {te["z1"]}', "lbls"))
    ul = L - (li["x0"] + li["x1"]) / 2
    o.append(_texte(ul, 184, f'matelas {li["matelas"]}, dessus h {li["z1"]}', "lblx muted"))
    o.append(_texte(ul, 214, f'sommier {li["sommier"]}', "lblx muted"))
    o.append(_texte(ul, 240, f'pieds {li["pieds"]}', "lblx muted"))
    # ② chevets, appliques, prises (chevet ouest d'abord)
    ap, pr = M.APPLIQUES, M.PRISES
    for ch, xa, xq in zip((M.CHEVET_OUEST, M.CHEVET_EST), ap["x"], pr["x"]):
        o.append(_rz(H, L - ch["x0"], L - ch["x1"], 0, ch["z1"], "cab", 1.5))
        o.append(_ligne("filet", L - ch["x1"], H - _TIROIR_CHEVET, L - ch["x0"], H - _TIROIR_CHEVET))
        o.append(_texte(L - (ch["x0"] + ch["x1"]) / 2, 220, f'{_numero("②")} h {ch["z1"]}', "lblx"))
        ua, uq = L - xa, L - xq
        o.append(_rz(H, ua - ap["l"] / 2, ua + ap["l"] / 2, ap["z0"], ap["z1"], "lamp"))
        o.append(_ligne("filet", ua, H - ap["z0"], ua, H - ap["z0"] + _FIL))
        o.append(_texte(ua, H - ap["z1"] - 4, f'applique h {ap["h"]}', "lblx muted"))
        o.append(_rz(H, uq - pr["l"] / 2, uq + pr["l"] / 2, pr["z0"], pr["z1"], "plug"))
        o.append(_texte(uq, H - pr["z1"] - 5, f'prises h {pr["h"]}', "lblx muted"))
    # cotes : largeur et haut de la tête de lit, dessus du matelas
    o.append(_cote((L - te["x1"], -8), (L - te["x0"], -8), te["x1"] - te["x0"], (L - (te["x0"] + te["x1"]) / 2, -10),
                   "sud"))
    o.append(_cote((-30, H - te["z1"]), (-30, H), te["z1"], (-33, H - te["z1"] / 2), "sud"))
    o.append(_cote((-20, H - li["z1"]), (-20, H), li["z1"], (-23, H - li["z1"] / 2), "sud"))
    return _elevation("sud", "-45 -22 520 290", o, aria)


def elevation_ouest(M, aria=""):
    """Mur ouest vu depuis la fenêtre : placard existant, porte du couloir ; lit et chevet en pointillés."""
    H, P, EP, pl, po = M.H, M.P, M.EP, M.PLACARD, M.PORTE
    o = _cadre(M, P, EP["s"], EP["n"])
    o.append(_rz(H, P - pl["y1"], P - pl["y0"], 0, H, "bgwall"))
    a, b = pl["porte"]
    o.append(_rz(H, P - b, P - a, 0, M.H_PORTE, "closet"))
    um = P - (a + b) / 2
    o.append(_ligne("filet", um, H - M.H_PORTE, um, H))
    o.append(_texte(um, H - M.H_PORTE - 4, f"placard existant, porte {b - a}", "lblx muted"))
    o.append(_rz(H, P - po["b"], P - po["a"], 0, M.H_PORTE, "appf"))
    o.append(f'<circle class="dark" cx="{f(P - po["b"] + _POIGNEE_PORTE[0])}" cy="{f(H - _POIGNEE_PORTE[1])}" r="2"/>')
    o.append(_texte(P - (po["a"] + po["b"]) / 2, H - M.H_PORTE - 4, "porte du couloir", "lblx muted"))
    # premier plan : tête de lit, lit, chevet ouest
    te, li, ch, cl = M.TETE, M.LIT, M.CHEVET_OUEST, M.CLIM
    o.append(_rz(H, P - te["y1"], P - te["y0"], te["z0"], te["z1"], "ghost"))
    o.append(_rz(H, P - li["y1"], P - li["y0"], li["pieds"], li["z1"], "ghost"))
    o.append(_rz(H, P - ch["y1"], P - ch["y0"], 0, ch["z1"], "ghost"))
    o.append(_rz(H, P - cl["y1"], P - cl["y0"], cl["z0"], cl["z1"], "tech"))
    o.append(_texte(P - (li["y0"] + li["y1"]) / 2, 220, "lit et chevet au premier plan", "lblx muted"))
    o.append(_texte(4, 262, "sud", "lblx muted", "start"))
    o.append(_texte(P - 4, 262, "nord", "lblx muted", "end"))
    return _elevation("ouest", "-35 -22 320 290", o, aria)


# Élévations dans l'ordre de la page : repère → (nom, fonction).
ELEVATIONS = {"est": ("Mur est", elevation_est), "sud": ("Mur sud", elevation_sud),
              "ouest": ("Mur ouest", elevation_ouest)}


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
    "est": ("Mur est, vu depuis le lit : la niche à pantalons au nord, sous les trois patères, puis les deux commodes "
            "sous la fenêtre coulissante. Le plan à 85 reste sous l'allège de 106. Le lit et le chevet, au premier "
            "plan, sont en pointillés."),
    "sud": ("Mur sud, vu depuis le pied du lit : à gauche, le bout du plan et de la commode sud ; le chevet est réduit "
            "à 30 de large."),
    "ouest": ("Mur ouest, vu depuis la fenêtre : le placard existant (porte de 155) à gauche, la porte du couloir à "
              "droite. Le lit et le chevet, au premier plan, sont en pointillés."),
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
.floorl{stroke:var(--ink);stroke-width:2}
.el-ceil{stroke:var(--muted);stroke-width:.8;stroke-dasharray:6 4}
.bgwall{fill:var(--line);fill-opacity:.35;stroke:none}
.wcut{fill:var(--ink)}
.dark{fill:var(--ink)}
.tech{fill:var(--tech);stroke:var(--ink);stroke-width:.7;stroke-dasharray:3 2}
.plug{fill:var(--tri)}
.cloth{fill:#7B5EA7;fill-opacity:.18;stroke:#7B5EA7;stroke-width:.6}
"""
