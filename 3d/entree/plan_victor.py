# Génère entree-amenagement-victor.html (variante Victor de l'entrée) depuis victor.py.
#
#   python3 3d/entree/plan_victor.py      (just entree-victor)
#
# Reprend la mise en page, les styles, les coupes et le script de plan.py ; seuls le plan, les coupes et le texte
# propres à la variante sont écrits ici.

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import plan as P  # noqa: E402
import victor as M  # noqa: E402
from plan import coin_arrondi, cote_h, cote_v, degage, escape, f, portes_vues, rect, rot, text, virg  # noqa: E402

P.M = M                                       # les fonctions communes de plan.py lisent la variante
P.OUT = os.path.join(P.ROOT, "entree-amenagement-victor.html")
P.CLE = "entree-victor"
P.DOSSIER_3D = "entree-victor-3d"
P.COUPE_CLS.update({"tall_i": ("talli", "tallic"), "facade_pi": ("india", "india")})
P.CSS += """
.talli{fill:var(--india);stroke:var(--ink);stroke-width:.8}
.tallic{fill:var(--india);stroke:var(--ink);stroke-width:1.4}
"""

COUPE_A = 60     # y, regard vers le nord : mur nord libre, tableau électrique
COUPE_B = 40     # x, regard vers l'est : arrondi du meuble à chaussures, penderie, planche, patères
COUPE_C = 130    # y, regard vers le sud : meuble à chaussures, étagères, penderie, porte d'entrée au fond
COUPE_D = 60     # x, regard vers l'ouest : mur ouest de l'entrée, cadres, miroir, interphone


# ------------------------------------------------------------------ plan vu de dessus
def plan_svg():
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
    o += P._jambages()
    for p in M.PORTES:
        o += P._porte(p)
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
    return f'<svg viewBox="-150 -130 595 560" role="img" aria-label="Plan de l\'entrée, version Victor">{"".join(o)}</svg>'


# ------------------------------------------------------------------ coupes
def coupe_a():
    t = M.TABLEAU

    def cotes(X):
        return portes_vues(X, "n") + [
            text((X(t["x0"]) + X(t["x1"])) / 2, -t["z1"] - 6, "position et taille à relever", "lblx muted"),
            text((X(t["x0"]) + X(t["x1"])) / 2, -30, "mur libre", "lbls muted"),
            cote_h(87, 191, 12, "trumeau 104"),
        ]

    return P.coupe_svg(COUPE_A, "nord", -20, 284, [t["z0"], t["z1"], M.H_PORTE], extra=cotes)


def coupe_b():
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

    return P.coupe_svg(COUPE_B, "est", -20, 394, [pl["z1"], M.CHAUSSURES["z1"] + M.CHAUSSURES["plateau"], M.PATERE["z"], pe["z1"]],
                       extra=cotes)


def coupe_c():
    b, et = M.CHAUSSURES, M.ETAGERES

    def cotes(X):
        u0, u1 = sorted((X(b["xa"]), X(b["x1"])))
        v0, v1 = sorted((X(b["x0"]), X(b["xa"])))
        xm = (u0 + u1) / 2
        return [text(xm, -b["z1"] - b["plateau"] - 4, "① chaussures", "lblb"),
                cote_h(u0, u1, 12, f'abattants {b["x1"] - b["xa"]}'),
                cote_h(v0, v1, 12, f'arrondi {b["xa"] - b["x0"]}'),
                text(xm, -et["z"][1] - et["ep"] - 3, "étagères flottantes", "lblx muted")] + portes_vues(X, "s")

    return P.coupe_svg(COUPE_C, "sud", -20, 374, [b["z1"] + b["plateau"], et["z"][0], et["z"][1], M.PENDERIE["z1"]], extra=cotes)


def coupe_d():
    cd, mi, it = M.CADRES, M.MIROIR, M.INTERPHONE

    def cotes(X):
        u0, u1 = sorted((X(cd["y0"]), X(cd["y1"])))
        v0, v1 = sorted((X(mi["y0"]), X(mi["y1"])))
        return [cote_h(u0, u1, 12, f'{cd["colonnes"]} × {cd["rangs"]} cadres {cd["l"]} × {cd["h"]}'),
                cote_h(v0, v1, 12, f'miroir {mi["y1"] - mi["y0"]}'),
                text((v0 + v1) / 2, -mi["z1"] - 4, f'miroir {mi["y1"] - mi["y0"]} × {mi["z1"] - mi["z0"]}', "lblx muted"),
                text(X((it["y0"] + it["y1"]) / 2), -it["z0"] + 8, "interphone", "lblx muted")] + portes_vues(X, "o")

    return P.coupe_svg(COUPE_D, "ouest", -20, 394, [mi["z0"], cd["z0"], cd["z1"], mi["z1"]], extra=cotes)


# ------------------------------------------------------------------ texte
def contenu():
    b, pe, mi, et, pl, cd = M.CHAUSSURES, M.PENDERIE, M.MIROIR, M.ETAGERES, M.PLANCHE, M.CADRES
    lignes = "".join(f'<tr><td class="mono">{v}</td><td class="mono">{dt}</td><td>{escape(x)}</td></tr>'
                     for v, dt, x in M.CHANGEMENTS)
    lb, pb = b["x1"] - b["x0"], b["y1"] - b["y0"]
    lp, pp = pe["y1"] - pe["y0"], pe["x1"] - pe["x0"] - pe["facade"]
    total = sum(q * p for _, _, q, p in M.IKEA)
    achats = "".join(f'<tr><td>{escape(n)}</td><td class="mono">{r}</td><td class="mono">{q}</td><td class="mono">{q * p} €</td></tr>'
                     for n, r, q, p in M.IKEA)
    le = et["x1"] - et["x0"]
    lpl, ppl = pl["y1"] - pl["y0"], pl["x1"] - pl["x0"]
    ncd = cd["colonnes"] * cd["rangs"]
    return f"""<div class="kicker">Entrée · version Victor · {M.VERSION}</div>
<h1>Aménagement de l'entrée, version Victor</h1>
<p class="pitch">Variante de l'<a href="entree-amenagement.html">aménagement {M.BASE}</a>. Le mur sous le tableau électrique reste libre. Un meuble à chaussures bas à abattants, deux étagères flottantes au-dessus, prend la place de la penderie face à la salle de bain ; il file jusqu'à la penderie et s'y termine en arrondi. La penderie, un PAX d'IKEA de 75 × 35 qui monte presque au plafond, passe dans la branche d'entrée ; une planche à chaussures court sous les patères. En face, sur le mur ouest peint en India, des cadres et un miroir à côté de l'interphone.</p>
<div class="stats"><div class="stat"><b>PAX {lp} × {pp}</b><span>penderie IKEA, ≈ {total} €</span></div><div class="stat"><b>≈ {M.PAIRES} paires</b><span>meuble à abattants et planche</span></div><div class="stat"><b>{pe["x0"]} cm</b><span>passage le plus étroit</span></div><div class="stat"><b>{b["y0"]} cm</b><span>devant le meuble à chaussures</span></div></div>

<h2>Différences avec la {M.BASE}</h2>
<div class="fig"><table><thead><tr><th>Élément</th><th>{M.BASE}</th><th>Version Victor</th></tr></thead><tbody>
<tr><td>Sous le tableau électrique</td><td>Banc 95 × 38</td><td>Rien : mur libre</td></tr>
<tr><td>Face nord de la salle de bain</td><td>Penderie 84 × 40 toute hauteur</td><td>Meuble à chaussures {b["x1"] - b["xa"]} × {pb}, un niveau d'abattants, arrondi jusqu'au PAX, deux étagères flottantes au-dessus</td></tr>
<tr><td>Angle</td><td>Quart de cercle R 25 à étagères ouvertes</td><td>Quart de cercle plein R {b["r"]} centré sur le coin de la salle de bain, bout du meuble à chaussures</td></tr>
<tr><td>Cloison de la salle de bain, après le coin</td><td>Meuble à chaussures, premier module (83)</td><td>Penderie IKEA PAX {lp} × {pp} × {pe["z1"]}, bandeau jusqu'au plafond</td></tr>
<tr><td>Cloison de la salle de bain, côté porte</td><td>Meuble à chaussures, second module (83), miroir</td><td>Planche à chaussures {lpl} × {ppl} à {pl["z1"]}, les 4 patères au-dessus, applique</td></tr>
<tr><td>Meuble haut</td><td>En travers de la branche d'entrée, 110 × 40</td><td>Supprimé : deux tablettes en haut de la penderie</td></tr>
<tr><td>Mur ouest de l'entrée</td><td>Interphone</td><td>{ncd} cadres, miroir {mi["y1"] - mi["y0"]} × {mi["z1"] - mi["z0"]}, interphone</td></tr>
<tr><td>Chaussures</td><td>≈ 24 paires</td><td>≈ {M.PAIRES} paires</td></tr>
<tr><td>Passage le plus étroit</td><td>85 (devant le meuble à chaussures)</td><td>{pe["x0"]} (devant la penderie)</td></tr>
</tbody></table></div>

<h2>Plan</h2>
<div class="fig"><div class="scroll">{plan_svg().replace("<svg ", '<svg class="plan" ', 1)}</div>
<p class="cap">Plan vu de dessus, 1 unité = 1 cm ; nord en haut. Les portes de la penderie s'ouvrent vers l'ouest, dans la branche d'entrée (débattement en tireté). La porte d'entrée ouverte à 90° vient contre le chant de la planche à chaussures, qui lui sert de butée. Traits A, B, C, D : coupes ci-dessous.</p>
{P.legende()}</div>

{P.galerie()}<h2>Coupe A-A · mur nord</h2>
<div class="fig"><div class="scroll">{coupe_a().replace("<svg ", '<svg class="coupe" ', 1)}</div>
<p class="cap">Coupe à y {COUPE_A}, regard vers le nord : l'ouest est à gauche. Rien sous le tableau électrique, entre les portes de la cuisine et du WC. Tableau dessiné au milieu du trumeau, de {M.TABLEAU["z0"]} à {M.TABLEAU["z1"]} : position et taille à relever.</p></div>

<h2>Coupe B-B · mur de la salle de bain</h2>
<div class="fig"><div class="scroll">{coupe_b().replace("<svg ", '<svg class="coupe" ', 1)}</div>
<p class="cap">Coupe à x {COUPE_B}, regard vers l'est : le nord est à gauche. À gauche, l'arrondi du meuble à chaussures et ses étagères au fond ; puis la penderie PAX (portes FORSAND de 50 et 25, 229 de haut) et son bandeau jusqu'au plafond ; puis la planche à chaussures à {pl["z1"]}, les quatre patères et l'applique au-dessus.</p></div>

<h2>Coupe C-C · meuble à chaussures</h2>
<div class="fig"><div class="scroll">{coupe_c().replace("<svg ", '<svg class="coupe" ', 1)}</div>
<p class="cap">Coupe à y {COUPE_C}, regard vers le sud : l'est est à gauche. Le meuble à chaussures, {pb} de profondeur, plateau à {b["z1"] + b["plateau"]} : deux abattants de {b["modules"][0][1] - b["modules"][0][0]} puis l'arrondi plein jusqu'à la façade du PAX ; au-dessus, deux étagères flottantes de {le} × {et["y1"] - et["y0"]} à {et["z"][0]} et {et["z"][1]}. À droite, le flanc de la penderie PAX et son bandeau, la porte d'entrée au fond.</p></div>

<h2>Coupe D-D · mur ouest de l'entrée</h2>
<div class="fig"><div class="scroll">{coupe_d().replace("<svg ", '<svg class="coupe" ', 1)}</div>
<p class="cap">Coupe à x {COUPE_D}, regard vers l'ouest : le sud est à gauche. Contre la porte d'entrée, l'interphone, puis le miroir {mi["y1"] - mi["y0"]} × {mi["z1"] - mi["z0"]} à coins arrondis, puis la galerie de {ncd} cadres {cd["l"]} × {cd["h"]}, centrée à la même hauteur que le miroir ({virg(cd["zc"], 0)}). À droite, la porte de la pièce ouest.</p></div>

<h2>Principe</h2>
<div class="grid2">
<div class="card"><h3>① Meuble à chaussures</h3><p>À la place de la penderie, contre la face nord de la salle de bain : comme celui de la {M.BASE}, mais d'un seul niveau d'abattants et plus profond. Deux abattants de {b["modules"][0][1] - b["modules"][0][0]} sur {b["z1"] - b["socle"]} de haut (environ {M.PAIRES_MEUBLE} paires), plateau vide-poche en chêne à {b["z1"] + b["plateau"]}. À l'ouest, il se prolonge jusqu'à la façade du PAX et s'y termine par un quart de cercle plein de rayon {b["r"]}. Tout part d'un seul centre, le coin de la salle de bain : l'arc est tangent à la façade du PAX et à celle des abattants, sans plat ni ressaut ; le socle de {b["socle"]} en retrait de {b["retrait"]} et les étagères suivent des arcs concentriques. Le meuble prend la profondeur du PAX porte comprise ({pb}). Au-dessus, deux étagères flottantes de {le} × {et["y1"] - et["y0"]}, arrondies au bout ouest (R {et["r"]}) et prolongées jusqu'au flanc du PAX (fixations invisibles), à {et["z"][0]} et {et["z"][1]}. {b["y0"]} cm de passage devant, {b["x0"]} entre l'arrondi et le mur ouest.</p></div>
<div class="card"><h3>③ Penderie IKEA PAX</h3><p>Contre la cloison de la salle de bain, à partir de son coin, à la place du premier module à chaussures : un caisson PAX de {lp} × {pp} × {pe["z1"]}, fermé par une porte FORSAND de {pe["portes"][0]} et une de {pe["portes"][1]} (229 de haut ; c'est la combinaison IKEA pour un caisson de 75), ouvertes vers l'ouest. À {pp} de profondeur, les cintres se suspendent de face sur la tringle KOMPLEMENT à {pe["tringle"]} (environ {pe["manteaux"]} manteaux, 12 kg au plus) ; deux tablettes en haut, à {pe["etageres"][0]} et {pe["etageres"][1]}, remplacent le meuble haut (bonnets, gants, sacs). Caisson, portes et bandeau sont peints en India comme les murs de l'entrée ; le bandeau ferme les {M.H - pe["z1"]} cm jusqu'au plafond. Passage restant : {pe["x0"]} cm.</p></div>
<div class="card"><h3>⑤ Planche à chaussures sous les patères</h3><p>De la penderie au mur sud, {lpl} × {ppl}, dessus à {pl["z1"]} sur deux pieds pleins : les chaussures se rangent dessous ({pl["z1"] - pl["ep"]} de haut) et dessus, environ {M.PAIRES_PLANCHE} paires. Les {len(M.PATERES)} patères en bois restent à {M.PATERE["z"]} au-dessus, avec une applique. La porte d'entrée ouverte à 90° vient contre son chant (prévoir un tampon).</p></div>
<div class="card"><h3>Mur ouest : cadres et miroir</h3><p>En face de la penderie, sur le mur peint : un miroir {mi["y1"] - mi["y0"]} × {mi["z1"] - mi["z0"]} à coins arrondis (R {mi["r"]}) juste à côté de l'interphone, puis une galerie de {ncd} cadres {cd["l"]} × {cd["h"]} en grille {cd["colonnes"]} × {cd["rangs"]}, {cd["ecart"]} d'écart, centrée sur le mur libre entre la porte de la pièce ouest et le miroir et à la hauteur du centre du miroir. Ils ne dépassent que de {virg(cd["ep"])} dans le passage.</p></div>
<div class="card"><h3>Mur nord et entrée en India</h3><p>Sous le tableau électrique, rien : il reste dégagé et accessible. Au sud de y {M.INDIA['y0']}, murs, plafond et porte d'entrée en {M.INDIA["nom"]}, comme dans la {M.BASE}.</p></div>
</div>

<h2>Achats IKEA · penderie</h2>
<div class="fig"><table><thead><tr><th>Article</th><th>Référence</th><th>Qté</th><th>Prix</th></tr></thead><tbody>{achats}
<tr><td><b>Total</b></td><td></td><td></td><td class="mono"><b>{total} €</b></td></tr></tbody></table>
<p class="note">Prix IKEA France relevés sur les fiches produit le 13/11/2026, en blanc. Charnières KOMPLEMENT en plus (nombre et prix à lire sur la fiche des portes), bandeau et fixation murale non comptés.</p></div>

<h2>Matériaux</h2>
<div class="fig"><table><tbody>
<tr><td>Sol</td><td>Carrelage {M.CARRELAGE["nom"]}, comme la {M.BASE}.</td></tr>
<tr><td>Murs</td><td>Blanc chaud ({M.MUR_COULEUR}) ; l'entrée en {M.INDIA["nom"]} ({M.INDIA["couleur"]}).</td></tr>
<tr><td>Meubles</td><td>Proposition des rendus : meuble à chaussures, étagères flottantes et planche en chêne miel ; penderie PAX (caisson, portes FORSAND, bandeau) peinte en India comme les murs ; cadres noirs fins, passe-partout blanc. À choisir.</td></tr>
</tbody></table></div>

<h2>Points à vérifier</h2>
<ul class="pistes">
<li><b>Passage</b> : {pe["x0"]} cm entre la penderie et le mur ouest, contre 85 en {M.BASE} ; {pl["x0"]} devant la planche. Porte de 50 ouverte, il reste {pe["x0"] - pe["portes"][0]} cm.</li>
<li><b>Peinture du PAX</b> : caisson et portes FORSAND sont en mélaminé blanc : poncer légèrement, sous-couche d'accrochage, puis la peinture des murs (ou une laque teintée à l'identique). Autre piste : des façades sur mesure pour PAX dans la teinte (Plum Living en propose, à vérifier). India n'existe chez Plum Living qu'en laque de façade, pas en peinture murale (relevé du 13/11/2026) : avec India, faire teinter la peinture sur échantillon ; le sélecteur « Teinte » indique pour chaque couleur les gammes où elle existe.</li>
<li><b>Plafond</b> : IKEA demande au moins 1 cm au-dessus du caisson pour monter et ouvrir des portes battantes ; avec {M.H} sous plafond, il en reste {M.H - pe["z1"]}.</li>
<li><b>Porte d'entrée</b> : ouverte à 90°, elle s'arrête contre la planche ; un tampon sur le chant évite les marques.</li>
<li><b>Planche</b> : {pl["z1"] - pl["ep"]} cm sous la planche, assez pour des baskets et des chaussures de ville, pas pour des bottes (à ranger dessus).</li>
<li><b>Étagères flottantes</b> : fixations cachées dans la cloison de la salle de bain : vérifier sa nature (carreaux de plâtre, placo) et la charge admise.</li>
<li><b>Interphone</b> : le miroir est calé {M.INTERPHONE["y0"] - mi["y1"]} cm à côté ; sa position est à relever.</li>
<li><b>Tableau électrique, plafond</b> : mêmes points que la <a href="entree-amenagement.html">{M.BASE}</a>.</li>
</ul>

<p class="note">Repère : x vers l'est depuis le mur ouest du couloir, y vers le sud depuis son mur nord, z depuis le sol fini, en cm. Source : <span class="mono">3d/entree/victor.py</span> ; page : <span class="mono">3d/entree/plan_victor.py</span> (<span class="mono">just entree-victor</span>) ; vues 3D : <span class="mono">3d/entree/rendu.py</span> (<span class="mono">just entree-victor-rendu</span>).</p>

<section id="changements">
<h2>Changements</h2>
<div class="scroll"><table><thead><tr><th>Version</th><th>Date</th><th>Changements</th></tr></thead>
<tbody>{lignes}</tbody></table></div>
</section>
"""


P.contenu = contenu

if __name__ == "__main__":
    html = P.page().replace("<title>Aménagement de l'entrée</title>", "<title>Entrée, version Victor</title>", 1)
    with open(P.OUT, "w", encoding="utf-8") as fh:
        fh.write(html)
    print("Page :", P.OUT)
