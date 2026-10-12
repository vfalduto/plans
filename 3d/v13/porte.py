# Génère cuisine-v13-porte-cellier.html : plans détaillés de la porte du cellier (zone B6 / mur neuf / C1), placement
# et ouverture de la porte pliante Mantion Tango.
#
#   python3 3d/v13/porte.py    (aussi lancé par plan.py, donc par `just v13`)
#
# Tout est projeté depuis modele.py.

import math
import os
import sys
from html import escape

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import modele as M  # noqa: E402
from plan import CSS, ROOT, cote_d, cote_h, cote_v, fiche_tango, pts, rect, sources_tango, text, virg, volumes_plan  # noqa: E402

OUT = os.path.join(ROOT, "cuisine-v13-porte-cellier.html")

A = M.PLIANTE
AXE = 323.5                                   # axe de la cloison (x 320 → 327)
X_MUR0, X_MUR1 = 320, 327                     # faces cuisine et cellier de la cloison
B6 = M.sur_bas(M.B_ETROIT)                    # x 270 → 310
B5 = M.sur_bas(M.B_EVIER)
P_PLAN = M.P_PLAN_ETROIT                      # 42
Y_MUR = M.CLOISON_Y1                          # bout du mur neuf (y 48)
Y_C1 = M.JOUE_C2                              # flanc nord de C1 (y 115)
SANS_PORTE = ("cloison_cellier", "linteau_cellier", "cellier_pliante")


def fond(exclus=SANS_PORTE):
    o = [f'<polygon class="floorbg" points="{pts(M.SOL_PARQUET)}"/>', f'<polygon class="ciment" points="{pts(M.SOL_CIMENT)}"/>',
         f'<polygon class="wc" points="{pts(M.WC)}"/>']
    o += [rect(b.x0, b.y0, b.x1, b.y1, "ptbase") for b in M.MEUBLES if b.role == "plan"]
    return o + volumes_plan(exclus)


def svg(vue, corps, label, cls):
    x, y, w, h = vue
    return (f'<svg class="{cls}" viewBox="{x} {y} {w} {h}" role="img" aria-label="{escape(label)}">{"".join(corps)}</svg>')


def fig(vue, corps, titre, cls="vign"):
    return f'<figure>{svg(vue, corps, titre, cls)}<figcaption>{titre}</figcaption></figure>'


def mur(y1):
    return rect(X_MUR0, 0, X_MUR1, y1, "mn")


def pivot(x, y, r=1.4):
    return f'<circle class="pivot" cx="{x}" cy="{y}" r="{r}"/>'


# ------------------------------------------------------------------ vues
VUE_ZONE = (236, -24, 176, 212)
VUE_V = (252, -6, 140, 132)                   # vignettes
VUE_D = (292, 26, 46, 36)                     # détail du montant nord


def etiquettes_zone():
    return [text(253, 30, "B5", "lblb"), text(287, 16, "B6", "lblb"), text(287, 24, "placard", "lbls"),
            text(315, -3, "fileur", "lblx"), text(AXE, -3, "mur neuf", "lblx", "start"),
            text(352, 148, "C1 LV + MO", "lblb"), text(380, 62, "cellier", "lbl muted"), text(262, 130, "cuisine", "lbl muted"),
            text(380, 20, "rayonnage nord P40", "lbls")]


def zone():
    o = fond() + [mur(Y_MUR)] + etiquettes_zone()
    # chaîne x au-dessus du mur nord : B6, fileur, cloison
    o += [cote_h(B6[0], B6[1], -12, f"B6 {virg(B6[1] - B6[0])}"), cote_h(B6[1], X_MUR0, -12, virg(X_MUR0 - B6[1])),
          cote_h(X_MUR0, X_MUR1, -12, virg(X_MUR1 - X_MUR0))]
    # chaîne y le long du mur, côté cellier : mur neuf, baie, C1
    o += [cote_v(0, Y_MUR, 336, f"mur {virg(Y_MUR)} (8 + {M.DECALAGE_PORTE})"),
          cote_v(Y_MUR, Y_C1, 336, f"baie {virg(Y_C1 - Y_MUR)}"), cote_v(Y_C1, Y_C1 + 60, 336, "C1 60")]
    # profondeurs de B6 et de son plan, jeu jusqu'à la baie
    o += [cote_v(0, M.P_ETROIT + M.FACADE, 276, f"{M.P_ETROIT + M.FACADE}"), cote_v(0, P_PLAN, 315, f"plan {P_PLAN}"),
          cote_v(P_PLAN, Y_MUR, 315, virg(Y_MUR - P_PLAN))]
    # passage depuis le coin du plan de B5
    o.append(cote_d((B5[1], 62), (M.COL_X, Y_C1), 0.5, (-6, 4)))
    return svg(VUE_ZONE, o, "Zone de la porte du cellier, sans porte", "zone")


def pliante(etat):
    r0, l, e, y0, y1 = A["rail"], A["l"], A["ep"], A["y0"], A["y1"]
    o = fond() + [mur(Y_MUR), pivot(r0, y0)]
    if etat == "fermee":
        o += [rect(r0 - e / 2, y0, r0 + e / 2, y0 + l, "leaf"), rect(r0 - e / 2, y0 + l + 1, r0 + e / 2, y1, "leaf"),
              cote_v(y0, y1, 337, f"baie {virg(y1 - y0)}")]
    elif etat == "mi":
        t = math.radians(A["mi"])
        p1 = (r0 - l * math.sin(t), y0 + l * math.cos(t))
        p2 = (r0, y0 + 2 * l * math.cos(t))
        o += [f'<polyline class="pliee" points="{pts([(r0, y0), p1, p2])}"/>',
              f'<path class="swing" d="M{r0} {y0 + l} A{l} {l} 0 0 1 {p1[0]:.1f} {p1[1]:.1f}"/>',
              text(p1[0] - 2, p1[1] + 2, f'{A["mi"]}°', "lblx", "end")]
    else:
        o += [rect(r0 - l, y0, r0, y0 + e, "leaf"), rect(r0 - l, y0 + e, r0, y0 + 2 * e, "leaf"),
              f'<path class="swing" d="M{r0} {y0 + 2 * l} A{2 * l} {2 * l} 0 0 1 {r0 - l} {y0 + e}"/>',
              cote_v(y0 + 2 * e + 2, y1, 337, f"passage {virg(M.PASSAGE_CELLIER)}"),
              cote_h(r0 - l, r0, y0 + 2 * e + 8, virg(l)), cote_v(P_PLAN, y0, 300, virg(Y_MUR - P_PLAN))]
    return o


def detail():
    """Montant nord agrandi : épaisseur du mur, position des vantaux, plan de B6."""
    r0, l, e, y0 = A["rail"], A["l"], A["ep"], A["y0"]
    o = fond() + [mur(Y_MUR), rect(r0 - e / 2, y0, r0 + e / 2, y0 + 10, "leaf ghost"),
                  rect(r0 - l, y0, r0, y0 + e, "leaf"), rect(r0 - l, y0 + e, r0, y0 + 2 * e, "leaf"), pivot(r0, y0, .5),
                  f'<line class="axe" x1="{r0}" y1="28" x2="{r0}" y2="60"/>',
                  cote_h(X_MUR0, X_MUR1, 31, "mur 7", t=1), cote_h(r0 - e / 2, r0 + e / 2, 60, virg(e), t=1),
                  cote_v(P_PLAN, y0, 305, virg(y0 - P_PLAN), t=1),
                  text(r0 + 1.5, 36, f"rail x {virg(r0)}", "lblx", "start"), text(r0 + 2, y0 - 1, "pivot", "lblx", "start"),
                  text(310, 40, f"plan de B6 (P{P_PLAN})", "lblx"), text(306, y0 + 9, "vantaux repliés", "lblx"),
                  text(r0 + 2, y0 + 11, "position fermée", "lblx", "start"),
                  text(r0 + 2, y0 + 13, "(tireté)", "lblx", "start")]
    return svg(VUE_D, o, "Détail du montant nord", "detail")


def page():
    vign_p = "".join(fig(VUE_V, pliante(e), t) for e, t in (
        ("fermee", "1 · Fermée : les deux vantaux sont dans la baie, au nu du mur côté cuisine"),
        ("mi", f"2 · En cours : le vantail du pivot tourne vers la cuisine, le second suit (V à {A['mi']}°)"),
        ("ouverte", "3 · Ouverte : les vantaux repliés l'un contre l'autre, en travers, contre le mur neuf")))
    return f"""<!doctype html>
<html lang="fr">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Porte du cellier</title>
<link rel="icon" href="favicon.svg" type="image/svg+xml">
<link rel="apple-touch-icon" href="apple-touch-icon.png">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Archivo:wght@400;500;700;800&family=JetBrains+Mono:wght@400;600&display=swap" rel="stylesheet">
<style>{CSS}{CSS_PORTE}</style>
</head>
<body>
<div class="vbar"><a class="back" href="cuisine-v13.html">← Cuisine V13</a></div>
<main class="wrap">
<div class="kicker">Cuisine · {M.VERSION} · porte du cellier</div>
<h1>Porte du cellier : où elle se place</h1>
<p class="pitch">Vues de dessus agrandies de l'angle B6 / mur neuf / C1, cotes en cm, nord en haut. La porte ferme une baie
percée dans le prolongement du mur neuf (le retour de cloison qui part du mur nord) : on entre dans le cellier en allant
vers l'est. Elle est fermée par une porte pliante à deux vantaux sur ferrure Mantion Tango, dessinée fermée, en cours
d'ouverture et ouverte.</p>
<p class="leg"><span class="sw mn"></span>mur neuf (retour de cloison) <span class="sw bois"></span>porte
<span class="sw pv"></span>pivot <span class="sw ax"></span>axe du rail
(détails)</p>

<h2>1 · La zone, sans porte</h2>
<div class="fig">{zone()}
<p class="txt">Au nord, <b>B6</b> ({virg(B6[1] - B6[0])} de large, profondeur {M.P_ETROIT + M.FACADE}, plan de travail
P{P_PLAN}) et son <b>fileur</b> de {virg(X_MUR0 - B6[1])} vont jusqu'au <b>mur neuf</b> : un retour de cloison de 7
d'épaisseur (x {X_MUR0} → {X_MUR1}), long de {virg(Y_MUR)} depuis le mur nord (8 pour le passage des tuyaux + {M.DECALAGE_PORTE}
de décalage). Au sud, <b>C1</b> (lave-vaisselle et micro-ondes) commence à y {virg(Y_C1)}. Entre les deux : la
<b>baie de {virg(Y_C1 - Y_MUR)}</b>, que la porte doit fermer. Contraintes : côté cuisine, le plan de B6 s'arrête
{virg(Y_MUR - P_PLAN)} avant la baie ; à 55 devant le montant nord, rien jusqu'au plan de B5 ; côté cellier, le rayonnage
nord (P40) passe à 8 du montant nord. Diagonale : {M.ACCES_CELLIER:.0f} du coin du plan de B5 à l'angle de C1.</p></div>

<h2>2 · Porte pliante Mantion Tango</h2>
<div class="fig"><div class="vigns">{vign_p}</div>
<div class="det">{detail()}<p class="txt"><b>Placement.</b> Pas de dormant : un rail en haut de la baie, à
x {virg(A["rail"])}, porte deux vantaux de {virg(A["l"])}, épaisseur {virg(A["ep"])} (le modèle : section 3). Fermée, ils sont <b>dans l'épaisseur du
mur, au nu côté cuisine</b> (x {X_MUR0} → {virg(X_MUR0 + A["ep"])}), alignés sur la cloison. Le <b>pivot</b> est au nord,
contre le bout du mur neuf (point). <b>Ouverture.</b> On tire la poignée (au sud, côté C1) : le vantail du pivot tourne
vers la cuisine, le second se plie contre lui et glisse le long du rail. Ouverte, la porte forme un paquet de {virg(2 * A["ep"])}
d'épaisseur, en travers de la baie, côté cuisine, qui dépasse de {virg(A["l"])} du mur : il reste {virg(Y_MUR - P_PLAN)}
entre lui et le plan de B6. Côté cellier, rien ne dépasse (elle heurterait le rayonnage nord). Passage libre
{virg(M.PASSAGE_CELLIER)} (baie moins le paquet et sa ferrure).</p></div></div>

<h2>3 · Le modèle : Mantion Tango</h2>
<div class="fig">{fiche_tango()}
<p class="txt">{sources_tango()} Explications (principe, pose, ce qui reste à vérifier) : section « Porte du cellier »
de la <a href="cuisine-v13.html">page Cuisine V13</a>.</p></div>
</main>
</body>
</html>
"""


CSS_PORTE = """
.zone{display:block;width:100%;max-width:820px;height:auto;margin:0 auto}
.mn{fill:#8E979F;stroke:var(--ink);stroke-width:.6}
.leg{font-size:13px;color:var(--muted);display:flex;flex-wrap:wrap;align-items:center;gap:6px 14px}
.sw{display:inline-block;width:14px;height:10px;border:1px solid var(--ink);vertical-align:middle;margin-right:4px}
.sw.mn{background:#8E979F}.sw.bois{background:var(--wood)}
.sw.pv{background:var(--ink);border-radius:50%;width:9px;height:9px}
.sw.ax{border:none;border-top:2px dashed #C0392B;height:0;width:16px}
.vigns{display:grid;grid-template-columns:repeat(auto-fit,minmax(240px,1fr));gap:12px}
.vigns figure{margin:0}.vigns svg{width:100%;height:auto}
.vigns figcaption{font-size:12.5px;color:var(--muted);margin-top:4px;line-height:1.4}
.det{display:grid;grid-template-columns:minmax(220px,340px) 1fr;gap:16px;align-items:start;margin-top:16px}
.det svg{width:100%;height:auto;border:1px solid var(--line);border-radius:8px}
@media (max-width:640px){.det{grid-template-columns:1fr}}
.zone .dimt{font-size:4px}.zone .dim{stroke-width:.35}.zone .lblb{font-size:5px}.zone .lbls{font-size:3.6px}
.zone .lbl{font-size:4.2px}.zone .lblx{font-size:3px}
.vign .dimt{font-size:5.5px}.vign .lblx{font-size:4px}
.detail .dimt{font-size:1.8px}.detail .dim{stroke-width:.15}.detail .lblx{font-size:1.6px}
.detail .leaf,.detail .mn{stroke-width:.2}
.pivot{fill:var(--ink)}
.ghost{fill:none;stroke-dasharray:1 .6;stroke-width:.25}
.axe{stroke:#C0392B;stroke-width:.25;stroke-dasharray:1.2 .8}
.vign .axe{stroke-width:.6}
.orga .muted{color:var(--muted);font-weight:400;font-size:12.5px}
"""


def ecrire():
    with open(OUT, "w", encoding="utf-8") as fh:
        fh.write(page())
    print(OUT)


if __name__ == "__main__":
    ecrire()
