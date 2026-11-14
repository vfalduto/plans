"""Dessins de la page salon-enfilade : élévation, coupes, dessus, vue éclatée, iso, panneaux de découpe, comparaison.

Repris de 3d/salon/enfilade.py (L486-739 et L851-874). Écarts : le point médian des étiquettes devient une virgule, le
label est un paramètre (il devient le texte sous le dessin), `en_cm` met un dessin à l'échelle du centimètre pour
Mesurer, et le CSS de l'ancienne page (sans chasse fixe) est ici, à préfixer par `css_dessins`.
"""
import re
from html import escape

from pieces.salon.amenagement.document import CANAPE
from pieces.salon.dessin import cote_h, cote_v, f, iso_svg, rect, text
from pieces.salon.dessin import rect as _rect  # `rect` est redéfini localement dans dessus_svg
from pieces.salon.enfilade.document import (CALE_BOITE, CHARNIERE, COULISSE, DESSUS, DOS, EP, FAC, FORMATS, H_BOITE, L, N,
                                            MODULES, NORD, P, PC, PIEDS_X, PROF_ETAGERE, RETENUE, STOCKHOLM, TAMPON, TRAV,
                                            VINYLE, Z1, ZP)
from pieces.salon.enfilade.volumes import G, pieces_3d
from pieces.salon.meubles import cote

ECHELLES = {"elevation": 3.4, "profil": 5, "dessus": 3, "eclate": 2.6}

CSS = """svg.enf text{font-family:var(--texte);fill:var(--ink)}
svg.enf .dim{stroke:var(--muted);stroke-width:.6;fill:none}
svg.enf .dimt{fill:var(--muted);font-family:var(--ui);font-weight:600;font-variant-numeric:tabular-nums;font-size:10px}
svg.enf .t{font-size:11.5px}svg.enf .ts{font-size:10px}svg.enf .tx{font-size:8.5px}svg.enf .tb{font-size:12px;font-weight:700}
svg.enf .inv{fill:#F7F8F6}
svg.enf .muted{fill:var(--muted)}
svg.enf .floorl{stroke:var(--ink);stroke-width:2}
svg.enf .mur-h{fill:var(--line);fill-opacity:.6;stroke:var(--muted);stroke-width:.5}
svg.enf .mont{fill:#26262A;stroke:var(--ink);stroke-width:.4}
svg.enf .shelfc{fill:var(--wood);stroke:var(--ink);stroke-width:.6}
svg.enf .cab{fill:var(--cab);stroke:var(--ink);stroke-width:.7}
svg.enf .dark{fill:var(--ink)}
svg.enf .acier{fill:#8E9399;stroke:var(--ink);stroke-width:.4}
svg.enf .acierh{fill:none;stroke:#5E6369;stroke-width:.8;stroke-dasharray:2 1.5}
svg.enf .upper{fill:none;stroke:var(--ink);stroke-width:.8;stroke-dasharray:3 2}
svg.enf .sofa{fill:#C9BFAE;stroke:var(--ink);stroke-width:.8}
svg.enf .vinyl{fill:#2B2B2E;fill-opacity:.75;stroke:var(--ink);stroke-width:.4}
svg.enf .mel{fill:var(--panel);stroke:var(--ink);stroke-width:.7}
svg.enf .hdf{fill:#8A6E52;stroke:var(--ink);stroke-width:.3}
svg.enf .hdfl{fill:#8A6E52;fill-opacity:.18;stroke:none}
svg.enf .chute{fill:var(--line);fill-opacity:.3;stroke:var(--muted);stroke-width:.6}
svg.enf .ouv{fill:none;stroke:var(--muted);stroke-width:.7;stroke-dasharray:4 3}
svg.enf .arc{fill:none;stroke:var(--tri);stroke-width:.9;stroke-dasharray:4 2}
svg.enf .porteo{fill:var(--wood);fill-opacity:.25;stroke:var(--tri);stroke-width:.7;stroke-dasharray:3 2}
svg.enf .fl{stroke:var(--muted);stroke-width:.6}
svg.enf .fl2{stroke:var(--tri);stroke-width:.9;fill:none;marker-end:url(#fleche)}
svg.enf .flm{fill:var(--tri)}
.lg{display:inline-block;width:14px;height:10px;border:1px solid var(--ink);vertical-align:-1px;margin:0 4px 0 10px}
.lg.chene{background:var(--wood)}.lg.chute{background:var(--line)}
.schema{margin:14px 0;max-width:1120px}.schema svg{display:block;width:100%;height:auto}
"""

FLECHE = ('<defs><marker id="fleche" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" '
          'orient="auto-start-reverse"><path class="flm" d="M0,0 L10,5 L0,10 z"/></marker></defs>')


def formule_longueur(g):
    return f"{cote(L)} = {N} × {cote(g['W'][0])}, centré sur le mur ({cote(NORD)} libres de chaque côté)"


def svg(vb, corps, label):
    return f'<svg class="enf" viewBox="{vb}" role="img" aria-label="{escape(label, quote=True)}">{corps}</svg>'


def en_cm(dessin, k):
    """Le dessin à l'échelle du centimètre : viewBox divisé par k, contenu réduit d'autant."""
    def vb(m):
        return 'viewBox="' + " ".join(f"{round(float(v) / k, 3):g}" for v in m.group(1).split()) + '"'
    tete = re.match(r"<svg[^>]*>", dessin).group(0)
    return re.sub(r'viewBox="([^"]*)"', vb, tete, count=1) + f'<g transform="scale({1 / k:.6g})">' + dessin[len(tete):-6] + "</g></svg>"


def iso(ouvert, label):
    return iso_svg(pieces_3d(ouvert=ouvert), escape(label, quote=True))


def cl_caisson():
    """Classe SVG des pièces du caisson, des étagères et des boîtes de tiroir dans la variante retenue."""
    return "mel" if RETENUE["caisson"] == "mel" else "shelfc"


def face_svg(g=G, label="Élévation de face cotée de l'enfilade"):
    """Élévation de face, vue de la pièce (regard vers l'ouest : le nord, contre le mur, est à droite)."""
    k = ECHELLES["elevation"]
    U = lambda y: (L - y) * k  # noqa: E731
    V = lambda z: (Z1 - z) * k  # noqa: E731
    o = [rect(U(-NORD), V(Z1 + 10), U(-NORD - 5), V(0), "mur-h"),
         text(U(-NORD - 2.5), V(0) + 15, "mur nord", "tx muted"),
         f'<line class="floorl" x1="{f(U(L) - 30)}" y1="{f(V(0))}" x2="{f(U(-NORD - 5))}" y2="{f(V(0))}"/>']
    for y in g["pieds_y"]:
        o.append(rect(U(min(y + 1.25, L)), V(ZP), U(max(y - 1.25, 0)), V(0), "mont"))
    o.append(rect(U(L), V(ZP + g["HC"]), U(0), V(ZP), cl_caisson()))
    o.append(rect(U(L), V(Z1), U(0), V(Z1 - g["ep_d"]), "shelfc"))
    for fc in g["facades"]:
        o.append(rect(U(fc["y1"]), V(fc["z1"]), U(fc["y0"]), V(fc["z0"]), "shelfc"))
        if fc["type"] == "porte":
            yh, yf = (fc["y0"], fc["y1"]) if fc["charniere"] == "n" else (fc["y1"], fc["y0"])
            zm = (fc["z0"] + fc["z1"]) / 2
            o += [f'<polyline class="ouv" points="{f(U(yf))},{f(V(fc["z1"]))} {f(U(yh))},{f(V(zm))} '
                  f'{f(U(yf))},{f(V(fc["z0"]))}"/>']
            ya = yh + (CHARNIERE["axe"] if yh == fc["y0"] else -CHARNIERE["axe"])
            for z in (fc["z0"] + CHARNIERE["bout"], fc["z1"] - CHARNIERE["bout"]):
                o.append(f'<circle class="acierh" cx="{f(U(ya))}" cy="{f(V(z))}" r="{f(1.75 * k)}"/>')
    for y in g["Y"][1:-1]:                           # jonctions (et joints du dessus s'il est en pièces)
        zj = Z1 if DESSUS[1] > 1 else Z1 - g["ep_d"]
        o.append(f'<line class="ouv" x1="{f(U(y))}" y1="{f(V(zj))}" x2="{f(U(y))}" y2="{f(V(0) + 6)}"/>')
    # contenu et cotes sous le meuble
    for k_, (types, contenu) in enumerate(MODULES):
        ym = (g["Y"][k_] + g["Y"][k_ + 1]) / 2
        o.append(text(U(ym), V(0) + 15, f"M{k_ + 1}, {contenu}", "ts"))
        o.append(cote_h(U(g["Y"][k_ + 1]), U(g["Y"][k_]), V(0) + 36, f'caisson {cote(g["W"][k_])}'))
    o.append(cote_h(U(L), U(0), V(0) + 58, formule_longueur(g)))
    # largeurs des façades au-dessus
    yv = V(Z1) - 12
    for fc in g["facades"]:
        if fc["type"] == "porte" or fc["z0"] == g["za"]:
            o.append(cote_h(U(fc["y1"]), U(fc["y0"]), yv, cote(fc["y1"] - fc["y0"])))
    o.append(cote_h(U(0), U(-NORD), V(Z1) - 30, cote(NORD)))
    o.append(text(U(0) - 4, V(Z1) - 33, "jour", "dimt", "end"))   # « jour » à gauche : le libellé entier dépasse sur le mur
    # hauteurs à gauche (bout sud)
    x1, x2 = -14, -40
    o += [cote_v(V(0), V(ZP), x1, f"pieds {f(ZP)}"),
          cote_v(V(ZP), V(ZP + g["HC"]), x1, f'caisson {cote(g["HC"])}'),
          cote_v_mince(V(Z1 - g["ep_d"]), V(Z1), x1 - 16, cote(g["ep_d"]), True),
          cote_v(V(0), V(Z1), x2 - 6, f"{f(Z1)}")]
    porte = next(fc for fc in g["facades"] if fc["type"] == "porte")
    o.append(cote_v(V(porte["z0"]), V(porte["z1"]), U(-5) + 16, f'portes {cote(porte["z1"] - porte["z0"])}'))
    o.append(text(U(L) + 4, V(Z1) - 4, "dessus", "tx muted", "start"))
    vb = f"{f(x2 - 30)} {f(V(Z1) - 46)} {f(U(-NORD - 5) - x2 + 60)} {f(Z1 * k + 46 + 70)}"
    return svg(vb, "".join(o), label)


def cote_v_mince(y0, y1, x, label, cote_a_droite=False):
    """Cote verticale d'une épaisseur trop mince pour son libellé (1,8) : le libellé est écrit à plat, à côté."""
    base = cote_v(y0, y1, x, label)
    traits = base[:base.index("<text")]
    cote_a = "start" if cote_a_droite else "end"
    return traits + text(x + (5 if cote_a_droite else -5), (y0 + y1) / 2 + 2, label, "dimt", cote_a)


def profil_svg(g=G, label="Coupes de profil de l'enfilade"):
    """Deux coupes de profil (mur à gauche, pièce à droite) : par un module à portes, par le module à tiroirs."""
    k = ECHELLES["profil"]
    V = lambda z: (Z1 - z) * k  # noqa: E731
    o = []

    def coupe(ox, kind):
        X = lambda x: ox + x * k  # noqa: E731
        fr = DOS + PC                                       # nu avant du caisson
        s = [rect(X(-5), V(Z1 + 6), X(0), V(0), "mur-h"),
             f'<line class="floorl" x1="{f(X(-5))}" y1="{f(V(0))}" x2="{f(X(P + 10))}" y2="{f(V(0))}"/>',
             rect(X(DOS), V(ZP + g["HC"]), X(fr), V(ZP), "hdfl"),
             rect(X(0), V(ZP + g["HC"] - 0.2), X(DOS), V(ZP + 0.2), "hdf")]
        for x in PIEDS_X:
            s.append(rect(X(x - 1.25), V(ZP), X(x + 1.25), V(0), "mont"))
        s += [rect(X(DOS), V(g["zi0"]), X(fr), V(ZP), cl_caisson()),
              rect(X(DOS), V(ZP + g["HC"]), X(DOS + TRAV), V(g["zi1"]), cl_caisson()),
              rect(X(fr - TRAV), V(ZP + g["HC"]), X(fr), V(g["zi1"]), cl_caisson()),
              rect(X(0), V(Z1), X(P), V(Z1 - g["ep_d"]), "shelfc")]
        mod = 0 if kind == "porte" else next(fc["k"] for fc in g["facades"] if fc["type"] == "tiroir")
        facs = [fc for fc in g["facades"] if fc["k"] == mod]
        for fc in facs[:1] if kind == "porte" else facs:
            s.append(rect(X(P - FAC), V(fc["z1"]), X(P), V(fc["z0"]), "shelfc"))
            for z in ((fc["z0"] + 3, fc["z1"] - 3) if kind == "porte" else ((fc["z0"] + fc["z1"]) / 2,)):
                s.append(rect(X(fr), V(z + 0.6), X(fr + TAMPON), V(z - 0.6), "dark"))
        if kind == "porte":
            fc = facs[0]
            for z in (fc["z0"] + CHARNIERE["bout"], fc["z1"] - CHARNIERE["bout"]):
                s.append(rect(X(fr - 5), V(z + 0.7), X(P - FAC + 1.2), V(z - 0.7), "acier"))
            z_s = next(z for kk, z in g["etageres"] if kk == mod)
            s += [rect(X(DOS), V(z_s + EP), X(DOS + PROF_ETAGERE), V(z_s), cl_caisson()),
                  rect(X(DOS + 1), V(g["zi0"] + VINYLE), X(DOS + 1 + VINYLE), V(g["zi0"]), "vinyl"),
                  text(X(DOS + 1 + VINYLE / 2), V(g["zi0"] + VINYLE / 2) + 4, f"vinyles {cote(VINYLE)}", "ts inv"),
                  text(X(DOS + 20), V(z_s + EP) - 6, "étagère sur taquets", "tx"),
                  text(X(DOS + 20), V(g["zi1"] - 6), "jeux, albums", "tx muted"),
                  # équerre anti-basculement sous la traverse arrière, vissée au mur à travers le dos
                  rect(X(DOS), V(g["zi1"]), X(DOS + 4), V(g["zi1"] - 0.35), "acier"),
                  rect(X(DOS), V(g["zi1"]), X(DOS + 0.35), V(g["zi1"] - 4), "acier"),
                  f'<line class="fl" x1="{f(X(-3))}" y1="{f(V(g["zi1"] - 2.5))}" x2="{f(X(DOS + 0.35))}" y2="{f(V(g["zi1"] - 2.5))}"/>',
                  cote_v(V(g["zi0"]), V(z_s), X(-5) - 12, f(z_s - g["zi0"])),
                  cote_v(V(z_s + EP), V(g["zi1"]), X(-5) - 12, cote(g["zi1"] - z_s - EP))]
            titre = "Coupe par M1 : porte, étagère"
        else:
            for fc in facs:
                zb0 = fc["z0"] + CALE_BOITE
                s += [rect(X(fr - COULISSE), V(zb0 + H_BOITE), X(fr), V(zb0), cl_caisson()),
                      rect(X(fr - COULISSE), V(zb0), X(fr), V(zb0 - DOS), "hdf"),
                      rect(X(fr - COULISSE + 0.5), V(zb0 + H_BOITE / 2 + 0.6), X(fr - 0.5), V(zb0 + H_BOITE / 2 - 0.6), "acier")]
                s.append(cote_v(V(fc["z0"]), V(fc["z1"]), X(P) + 14, cote(fc["z1"] - fc["z0"])))
            top = facs[-1]
            s += [text(X(fr - COULISSE / 2), V(top["z0"] + CALE_BOITE + H_BOITE) + 13, f"boîte {f(H_BOITE)}, coulisses {f(COULISSE * 10)}", "tx"),
                  cote_v(V(top["z0"] + CALE_BOITE), V(top["z0"] + CALE_BOITE + H_BOITE), X(fr - COULISSE) - 8, f(H_BOITE))]
            titre = "Coupe par M2 : tiroirs"
        s += [text(X(P / 2), V(Z1) - 26, titre, "tb"),
              text(X(P / 2), V(Z1) - 8, f'dessus {cote(g["ep_d"])}', "tx"),
              text(X(DOS + TRAV + 2), V(g["zi1"]) + 11, f"traverses {f(TRAV)}", "tx", "start") if kind == "porte" else "",
              text(X(DOS + PC / 2), V(ZP) + 14, "fond 1,8", "tx") if kind == "tiroir" else "",
              text(X(-2.5), V(Z1 + 6) - 4, "mur", "tx muted"),
              cote_h(X(0), X(fr), V(0) + 16, cote(fr)),
              cote_h(X(fr), X(P), V(0) + 16, f(P - fr)),
              cote_h(X(0), X(P), V(0) + 34, f(P)),
              cote_v(V(0), V(ZP), X(P) + 40, f(ZP)),
              cote_v(V(ZP), V(ZP + g["HC"]), X(P) + 40, cote(g["HC"])),
              cote_v_mince(V(Z1 - g["ep_d"]), V(Z1), X(P) + 40, cote(g["ep_d"])),
              cote_v(V(0), V(Z1), X(P) + 62, f(Z1))]
        return s

    o += coupe(60, "porte")
    o += coupe(60 + (P + 40) * k + 40, "tiroir")
    w = 60 + 2 * (P + 40) * k + 40 + 10
    return svg(f"0 {f(V(Z1) - 44)} {f(w)} {f(Z1 * k + 44 + 46)}", "".join(o), label)


def dessus_svg(g=G, label="Vue de dessus de l'enfilade avec les ouvertures"):
    """Vue de dessus, dessus enlevé : caissons, pieds (tireté), portes ouvertes à 90° et tiroir sorti dans l'allée."""
    k, c = ECHELLES["dessus"], CANAPE
    U = lambda y: (L - y) * k  # noqa: E731   vu de dessus, mur ouest en haut : le nord à droite
    rect = lambda x0, y0, x1, y1, cls: _rect(min(x0, x1), min(y0, y1), max(x0, x1), max(y0, y1), cls)  # noqa: E731
    V = lambda x: x * k  # noqa: E731
    fr = DOS + PC
    bas_v = c["x0"] + 22
    o = [rect(U(-NORD), V(-5), U(L + NORD), V(0), "mur-h"), rect(U(-NORD - 5), V(-5), U(-NORD), V(bas_v), "mur-h"),
         text(U(L / 2), V(-5) - 4, "mur ouest (cloison du cellier et du WC)", "tx muted"),
         rect(U(-NORD), V(c["x0"]), U(c["p"] - NORD), V(bas_v), "sofa"),
         text(U(c["p"] / 2 - NORD), V(c["x0"]) + 30, "canapé (bout ouest)", "tx")]
    for kk, w in enumerate(g["W"]):
        y0, y1 = g["Y"][kk], g["Y"][kk + 1]
        o += [rect(U(y0), V(0), U(y1), V(DOS), "hdf"),
              rect(U(y0), V(DOS), U(y1), V(fr), cl_caisson()),
              rect(U(y0), V(DOS), U(y0 + EP), V(fr), "shelfc" if kk == 0 else "cab"),
              rect(U(y1 - EP), V(DOS), U(y1), V(fr), "shelfc" if kk == N - 1 else "cab"),
              text(U((y0 + y1) / 2), V(fr / 2) + 4, f"M{kk + 1}", "tb")]
    for y in g["pieds_y"]:
        for x in PIEDS_X:
            o.append(rect(U(max(y - 1.25, 0)), V(x - 1.25), U(min(y + 1.25, L)), V(x + 1.25), "acierh"))
    o.append(rect(U(0), V(0), U(L), V(P), "upper"))
    for fc in g["facades"]:
        if fc["type"] == "tiroir":
            if fc["z0"] == g["za"]:
                o.append(rect(U(fc["y0"]), V(P - FAC), U(fc["y1"]), V(P), "shelfc"))
            continue
        w = fc["y1"] - fc["y0"]
        if fc["charniere"] == "n":
            yh, sens = fc["y0"], 1
        else:
            yh, sens = fc["y1"], -1
        yf = yh + sens * w
        o += [rect(U(min(yh, yh - sens * FAC)), V(P), U(max(yh, yh - sens * FAC)), V(P + w), "porteo"),
              f'<path class="arc" d="M{f(U(yf))},{f(V(P))} A{f(w * k)},{f(w * k)} 0 0 {0 if sens > 0 else 1} '
              f'{f(U(yh))},{f(V(P + w))}"/>']
    tz = next(fc for fc in g["facades"] if fc["type"] == "tiroir")
    o += [rect(U(tz["y0"]), V(P), U(tz["y1"]), V(P + COULISSE + FAC), "porteo"),
          text(U((tz["y0"] + tz["y1"]) / 2), V(P + COULISSE / 2) + 4, f"tiroir sorti {cote(COULISSE + FAC)}", "tx")]
    # dégagements : allée de 60 jusqu'au canapé, reste devant la porte ouverte
    p2 = [fc for fc in g["facades"] if fc["type"] == "porte" and fc["k"] == 0][-1]
    wp = p2["y1"] - p2["y0"]
    o += [cote_v(V(P), V(c["x0"]), U(c["p"] / 2 - NORD), f'allée {f(c["x0"] - P)}'),
          cote_v(V(P + wp), V(c["x0"]), U(p2["y1"]) + 8, cote(c["x0"] - P - wp)),
          cote_h(U(0), U(L), V(-5) - 22, cote(L)),
          cote_v(V(0), V(fr), U(L) - 14, cote(fr)),
          cote_v(V(0), V(P), U(L) - 34, f(P)),
          text(U(0) - 2, V(bas_v) + 14, "dessus en tireté, pieds dessous en carrés tiretés", "tx muted", "end"),
          text(U(L) + 2, V(bas_v) + 14, "sud à gauche (vers le passage), nord à droite", "tx muted", "start")]
    return svg(f"{f(U(L) - 50)} {f(V(-5) - 40)} {f(U(-NORD - 5) - U(L) + 64)} {f(V(bas_v) - V(-5) + 62)}", "".join(o),
               label)


def eclate_svg(g=G, label="Vue éclatée de l'enfilade"):
    """Vue éclatée de face : trois caissons, vis de liaison, pieds, dessus (d'une pièce ou un par caisson)."""
    k, gap, lev = ECHELLES["eclate"], 22, 24
    V = lambda z: (Z1 + lev - z) * k  # noqa: E731
    o = [FLECHE]
    xs = {}
    u = 0
    for kk in reversed(range(N)):                        # du sud (à gauche) au nord (à droite)
        xs[kk] = u
        u += g["W"][kk] * k + gap * k
    for kk in range(N):
        w, u0 = g["W"][kk], xs[kk]
        X = lambda y, u0=u0, w=w: u0 + (w - y) * k  # noqa: E731
        o += [rect(X(w), V(ZP + g["HC"]), X(0), V(ZP), "hdfl"),
              rect(X(w), V(ZP + g["HC"]), X(w - EP), V(ZP), "shelfc" if kk == N - 1 else cl_caisson()),
              rect(X(EP), V(ZP + g["HC"]), X(0), V(ZP), cl_caisson()),
              rect(X(w - EP), V(ZP + EP), X(EP), V(ZP), cl_caisson()),
              rect(X(w - EP), V(ZP + g["HC"]), X(EP), V(g["zi1"]), cl_caisson()),
              text(X(w / 2), V(ZP + g["HC"] / 2) + 4, f"caisson M{kk + 1}", "t"),
              text(X(w / 2), V(ZP + g["HC"] / 2) + 18, f'{cote(w)} × {cote(PC + DOS)} × {cote(g["HC"])}', "tx muted")]
        for y in (3, w - 3):
            o.append(rect(X(y + 1.25), V(ZP - 8), X(y - 1.25), V(-8), "mont"))
        if kk < N - 1:                                    # vis de liaison avec le caisson voisin (au sud)
            for z in (ZP + 8, ZP + g["HC"] - 8):
                o.append(f'<line class="fl2" x1="{f(X(w) - 4)}" y1="{f(V(z))}" x2="{f(X(w) - gap * k + 6)}" y2="{f(V(z))}"/>')
    for kk in range(N - 1):
        o += [text(xs[kk] - gap * k / 2, V(ZP + g["HC"] / 2) - 6, "4 vis", "tx"),
              text(xs[kk] - gap * k / 2, V(ZP + g["HC"] / 2) + 6, "de liaison", "tx")]
    tot = u - gap * k
    if DESSUS[1] == 1:
        o += [rect(0, V(Z1 + lev), tot, V(Z1 + lev - g["ep_d"]), "shelfc"),
              text(tot / 2, V(Z1 + lev) - 6, f'dessus d\'une pièce {cote(L)} × {f(P)} × {cote(g["ep_d"])}, posé sur équerres à trou oblong', "ts")]
    else:
        for kk in range(N):
            o.append(rect(xs[kk], V(Z1 + lev), xs[kk] + g["W"][kk] * k, V(Z1 + lev - g["ep_d"]), "shelfc"))
        o.append(text(tot / 2, V(Z1 + lev) - 6, f'un dessus par caisson, {cote(g["W"][0])} × {f(P)} × {cote(g["ep_d"])}, posé sur équerres à trou oblong', "ts"))
    o += [
          f'<line class="fl2" x1="{f(tot / 2)}" y1="{f(V(Z1 + lev - g["ep_d"]) + 3)}" x2="{f(tot / 2)}" y2="{f(V(ZP + g["HC"]) - 4)}"/>',
          text(tot / 2, V(-8) + 16, f'{len(g["pieds_y"]) * len(PIEDS_X)} pieds réglables : sous les bouts et à cheval sur chaque jonction', "ts")]
    return svg(f"-10 {f(V(Z1 + lev) - 24)} {f(tot + 20)} {f((Z1 + lev + 8) * k + 50)}", "".join(o),
               label)


def decoupe_svg(cle, pa, n):
    """Un panneau : bandes refendues, pièces repérées, chutes en gris. Renvoie (titre, svg)."""
    F, k = FORMATS[cle], 3.4
    cls = "shelfc" if F.get("bois") else "mel"
    o = [rect(0, 0, F["L"] * k, F["l"] * k, "chute")]
    for b in pa["bandes"]:
        for rep, lg, lr, x in b["poses"]:
            x0, y0, x1, y1 = x * k, b["y"] * k, (x + lg) * k, (b["y"] + lr) * k
            o.append(rect(x0, y0, x1, y1, cls))
            dims = f"{cote(lg)} × {cote(lr)}"
            xm, ym = (x0 + x1) / 2, (y0 + y1) / 2
            if lr * k >= 34:
                o += [text(xm, ym - 2, rep, "tb"), text(xm, ym + 14, dims, "ts")]
            elif lr * k >= 14:
                o.append(text(xm, ym + 4, f"{rep}  {dims}" if lg * k > 120 else rep, "ts"))
            else:
                o.append(text(xm, y1 + 12, f"{rep} ({dims})", "ts"))
    used = sum(lg * lr for b in pa["bandes"] for _, lg, lr, _ in b["poses"])
    titre = (f'{F["court"]} n° {n}, {cote(F["L"], 0)} × {cote(F["l"], 0)}, '
             f'chute {round(100 - 100 * used / (F["L"] * F["l"]))} %')
    return titre, svg(f"-2 -12 {f(F['L'] * k + 4)} {f(F['l'] * k + 24)}", "".join(o), titre)


def comparaison_svg(g=G, autres=None, titre="Comparaison des dimensions avec le buffet IKEA STOCKHOLM 2025"):
    """Élévations de face à la même échelle, alignées au sol sur le même mur : l'enfilade, puis chaque meuble de
    autres = [(nom, longueur, profondeur, hauteur, pieds, plinthe, jonctions)] (défaut : le STOCKHOLM), centrés."""
    k, S = 2.6, STOCKHOLM
    V = lambda z: (90 - z) * k  # noqa: E731
    lt = NORD * 2 + L                                 # longueur du mur, du mur nord au cadre du passage
    autres = autres or [(S["nom"], S["l"], S["p"], S["h"], 12, False, [])]
    rangs = [("cette enfilade", L, P, Z1, ZP, False, [NORD + y for y in g["Y"][1:-1]])] + autres
    o = []
    for i, (nom, l, p, h, zp, plinthe, jonctions) in enumerate(rangs):
        dy, y0 = i * 120 * k, (lt - l) / 2
        o += [f'<line class="floorl" x1="0" y1="{f(V(0) + dy)}" x2="{f(lt * k)}" y2="{f(V(0) + dy)}"/>',
                rect(0, V(h + 6) + dy, 2 * k, V(0) + dy, "mur-h"), rect(lt * k - 2 * k, V(h + 6) + dy, lt * k, V(0) + dy, "mur-h"),
                rect(y0 * k, V(h) + dy, (y0 + l) * k, V(zp) + dy, "shelfc"),
                text((y0 + l / 2) * k, V(h) + dy - 8, f"{nom} : {cote(l)} × {cote(p)} × {cote(h)}", "t"),
                cote_h(0, y0 * k, V(0) + dy + 16, cote(y0)), cote_h((y0 + l) * k, lt * k, V(0) + dy + 16, cote(lt - y0 - l))]
        if plinthe:                                   # socle plein, en retrait de 2 sous le devant
            o.append(rect((y0 + 1) * k, V(zp) + dy, (y0 + l - 1) * k, V(0) + dy, "mont"))
        else:
            for y in (y0 + 4, y0 + l - 4):
                o.append(rect((y - 1.25) * k, V(zp) + dy, (y + 1.25) * k, V(0) + dy, "mont"))
        for y in jonctions:
            o.append(f'<line class="ouv" x1="{f(y * k)}" y1="{f(V(h) + dy)}" x2="{f(y * k)}" y2="{f(V(zp) + dy)}"/>')
    return svg(f"-10 {f(V(95))} {f(lt * k + 20)} {f(V(0) - V(95) + (len(rangs) - 1) * 120 * k + 40)}", "".join(o), titre)
