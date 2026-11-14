# Génère cuisine-v13.html (plan vu de dessus + coupe A-A sur le mur nord) depuis modele.py.
#
#   python3 3d/v13/plan.py
#
# Le plan et la coupe sont des projections des volumes du modèle : rien n'est dessiné à la main.

import importlib
import math
import os
import re
import sys
from html import escape

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import modele as M  # noqa: E402
from pieces.cuisine.dessin import (CSS, PLAN_CLS, aire, cote_d, cote_h, cote_v, f, fiche_tango, pts, rect,  # noqa: E402,F401
                                   sources_tango, text, virg, volumes_plan)

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
ANCRES = open(os.path.join(ROOT, "3d", "ancres.js"), encoding="utf-8").read()   # ancres communes des pages à sommaire

OUT = os.path.join(ROOT, "cuisine-v13.html")

from pieces.cuisine.amenagement.dessins import (COUPE_A, COUPE_B, COUPE_C, COUPE_CLS, REGARDS,  # noqa: E402,F401
                                                REPERES_175, TAILLES, VERS, ZONES_175, batons_rompus, battant,
                                                chaine, coupe_svg, hauteur_pt_svg, minus, plan_elec_svg, pos_plan,
                                                POS_PLAN, regle, sym_inter, sym_lumiere, sym_prise, uv, vantail,
                                                zones_taille)
from pieces.cuisine.amenagement import dessins as _D  # noqa: E402
# calculs de la capacité et de la hauteur du plan : dans la vue Explication, réimportés ici
from pieces.cuisine.amenagement.explication import (LIGNES_CAPACITE, colonne_p9a, corps_capacite,  # noqa: E402,F401
                                                    details_capacite, etat, hors_fourchette, lignes_avant_apres,
                                                    nombre, note)

# les dessins sont dans pieces/cuisine/amenagement/dessins.py ; ici, l'ancienne page les garde tels qu'elle les
# montrait (aria-label d'origine, règle ajoutée par page(), points médians de plan_svg et coupe_elec_nord)
TAILLE_LEG = _D.REGLE_LEGENDE


def coupe_a():
    return _D.coupe_a_seule()


def coupe_b():
    return _D.coupe_b()


def coupe_c():
    return _D.coupe_c_seule()


# ------------------------------------------------------------------ plan vu de dessus
def plan_svg():
    o = [f"<defs>{batons_rompus()}</defs>"]
    o.append(f'<polygon class="floorbg" points="{pts(M.SOL_PARQUET)}"/>')
    o.append(f'<polygon fill="url(#br)" points="{pts(M.SOL_PARQUET)}"/>')
    o.append(f'<polygon class="ciment" points="{pts(M.SOL_CIMENT)}"/>')
    for b in M.CLOISONS_DEPOSEES:
        o.append(rect(b.x0, b.y0, b.x1, b.y1, "depose"))
    for nom, x, y in M.ZONES:
        for k, ligne in enumerate(nom.split("\n")):
            o.append(text(x, y + 8 * k, ligne, "lbls muted"))
    o.append(f'<polygon class="wc" points="{pts(M.WC)}"/>')
    o.append(text(438, 185, "WC", "lbl muted"))
    # fond opaque sous le plan de travail (semi-transparent) : le sol ne doit pas apparaître là où aucun caisson
    # ne le porte (fileur du mur ouest)
    for b in M.MEUBLES:
        if b.role == "plan":
            o.append(rect(b.x0, b.y0, b.x1, b.y1, "ptbase"))
    o += volumes_plan()
    # fenêtre coulissante : deux vantaux dans l'épaisseur du mur
    fe = M.FENETRE
    o.append(f'<line class="glass" x1="-7" y1="{fe["y0"]}" x2="-7" y2="{(fe["y0"] + fe["y1"]) / 2 + 2}"/>')
    o.append(f'<line class="glass" x1="-13" y1="{(fe["y0"] + fe["y1"]) / 2 - 2}" x2="-13" y2="{fe["y1"]}"/>')
    # porte d'entrée à galandage : fermée en trait plein, rentrée dans sa poche en ocre
    en = M.ENTREE
    o.append(f'<g class="vt" data-vt="entree" data-etat="ferme">'
             f'<g class="ouv">{rect(en["ouvert"][0], en["y"] - 2, en["ouvert"][1], en["y"] + 2, "leaf")}</g>'
             f'<g class="fer"><line class="doorleaf" x1="{f(en["ferme"][0])}" y1="{f(en["y"])}" '
             f'x2="{f(en["ferme"][1])}" y2="{f(en["y"])}"/></g></g>')
    o.append(text((en["x0"] + en["x1"]) / 2, 270, "Entrée", "lbls"))
    o.append(text(sum(en["poche"]) / 2, 237, "tableau noir · aimants", "lblx"))
    # ballon
    bl = M.BALLON
    if isinstance(bl, M.Cyl):
        o.append(f'<circle class="ecs" cx="{f(bl.cx)}" cy="{f(bl.cy)}" r="{f(bl.r)}"/>')
        o.append(text(bl.cx, bl.cy + 2, "Ballon ECS", "lblx"))
    o.append(text(M.CHUTE[0] + 7, M.CHUTE[1] + 2, "chute", "lblx", "start"))
    o.append(text(M.NOURRICE[0] - 4, M.NOURRICE[1] - 4, "nourrice", "lblx", "end"))
    # numéros des meubles
    for b in M.MEUBLES:
        if b.role == "caisson":
            nom, _, equip = b.etiq.partition(" ")
            y = 74 if b.y1 >= M.P_CAISSON else b.y1 / 2 + 3   # B6 (P40) : sur le caisson, la porte du cellier repliée devant
            o.append(text((b.x0 + b.x1) / 2, y, nom, "lblb"))
            if equip:
                o.append(text((b.x0 + b.x1) / 2, y + 8, equip, "lbls"))
        if b.role == "banquette" and b.etiq:
            o.append(text((b.x0 + b.x1) / 2, b.y0 + 12, b.etiq, "lbls"))   # V13.17 : au nord, hors de la plante
        if b.role == "colonne" and b.etiq:
            o.append(text((b.x0 + b.x1) / 2, (b.y0 + b.y1) / 2 + 3, b.etiq, "lbl", extra=' font-weight="700"'))
    for b in M.MEUBLES:
        if b.role == "plaque":
            o.append(text((b.x0 + b.x1) / 2, 50, "induction", "lblx onDark"))
        if b.role == "cuve":
            o.append(text((b.x0 + b.x1) / 2, b.y1 - 3, "évier", "lblx"))
        if b.role == "egouttoir":
            o.append(text((b.x0 + b.x1) / 2, (b.y0 + b.y1) / 2 + 2, "égouttoir", "lblx"))
    # cellier : vantaux ouverts vers le cellier, à l'épaisseur réelle, balayage et paumelles
    if M.PLIANTE:
        a = M.PLIANTE
        r, l, e, y0, y1 = a["rail"], a["l"], a["ep"], a["y0"], a["y1"]
        # ouverte : vantail du pivot rabattu vers l'ouest (y0 → y0 + e), second vantail replié contre lui ; balayage
        ouvert = (f'<path class="swing" d="M{f(r)} {f(y0 + 2 * l)} A{f(2 * l)} {f(2 * l)} 0 0 1 {f(r - l)} {f(y0 + e)}"/>'
                  f'<path class="swing" d="M{f(r)} {f(y0 + l)} A{f(l)} {f(l)} 0 0 1 {f(r - l)} {f(y0)}"/>'
                  + rect(r - l, y0, r, y0 + e, "leaf") + rect(r - l, y0 + e, r, y0 + 2 * e, "leaf")
                  + text(r - l / 2, y0 + 2 * e + 6, "porte pliante", "lblx"))
        ferme = rect(r - e / 2, y0, r + e / 2, y0 + l, "leaf") + rect(r - e / 2, y0 + l + 1, r + e / 2, y1, "leaf")
        # mi-ouverte : vantail du pivot tourné de a["mi"]° vers la cuisine, second vantail jusqu'au rail (V)
        t = math.radians(a["mi"])
        p1 = (r - l * math.sin(t), y0 + l * math.cos(t))
        p2 = (r, y0 + 2 * l * math.cos(t))
        mi = (f'<polyline class="pliee" points="{pts([(r, y0), p1, p2])}"/>'
              f'<path class="swing" d="M{f(r)} {f(y0 + l)} A{f(l)} {f(l)} 0 0 1 {f(p1[0])} {f(p1[1])}"/>'
              + text(p1[0] - 3, p1[1] + 2, f'{a["mi"]}°', "lblx", "end"))
        o.append(f'<g class="vt" data-vt="cellier" data-etat="mi"><g class="ouv">{ouvert}</g><g class="mi">{mi}</g>'
                 f'<g class="fer">{ferme}</g></g>')
        # baie et passage libre côte à côte, côté cellier, juste derrière la porte (V13.2 : la cote côté cuisine se
        # perdait dans le triangle d'activité)
        o.append(cote_v(y0, y1, 337, f'baie {f(y1 - y0)}'))
        o.append(cote_v(y0 + 2 * e + 2, y1, 348, f'passage {f(M.PASSAGE_CELLIER)}'))
        # passages dans le cellier
        o.append(cote_v(M.RAYON_NORD["y1"], M.JOUE_C2, 362, f'{f(M.PASSAGE_ENTREE)}'))
        o.append(cote_v(M.RAYON_NORD["y1"], M.Y_BALAIS - 6, 392, f'{f(M.PASSAGE_BALAIS)}'))
    for k, v in enumerate(M.CELLIER_VANTAUX):
        o.append(f'<g class="vt" data-vt="{k}"><g class="ouv">{vantail(v)}</g>'
                 f'<g class="fer">{vantail(v, ouvert=False)}</g></g>')
    # réseaux d'eau
    for role, _, p, _, _ in M.RESEAUX:
        o.append(f'<polyline class="{"pin" if role == "alim" else "pout"}" points="{pts(p)}"/>')
    o.append(f'<circle class="chute" cx="{f(M.CHUTE[0])}" cy="{f(M.CHUTE[1])}" r="4.5"/>')
    o.append(f'<circle class="nourrice" cx="{f(M.NOURRICE[0])}" cy="{f(M.NOURRICE[1])}" r="2.5"/>')
    # ouvertures de l'électroménager
    for kind, nom, d in M.OUVERTURES:
        if kind in ("abattant", "tiroir"):
            x0, x1, y0, y1 = d
            o.append(rect(x0, y0, x1, y1, "swingz"))
            lib = f"porte {nom} abattue" if kind == "abattant" else "tiroir"
            o.append(text((x0 + x1) / 2, (y0 + y1) / 2 + 2, lib, "lblx muted"))
        else:
            o.append(battant(*d, f"porte {nom} 90°"))
    # cellier : surface et volume
    surf = aire(M.CELLIER_SOL) / 1e4
    vol = surf * M.H / 100
    bl = M.BALLON
    net = vol - (math.pi * (bl.r / 100) ** 2 * (bl.z1 - bl.z0) / 100 if isinstance(bl, M.Cyl) else 0)
    for k, ligne in enumerate((f"cellier · {surf:.2f} m²", f"{vol:.2f} m³ brut · ≈ {net:.1f} net")):
        o.append(text(385, 16 + 7 * k, ligne.replace(".", ","), "lblx"))
    # table
    o.append(text(M.TABLE["cx"], M.TABLE["cy"] + 3, f'{M.TABLE["cote"]} × {M.TABLE["cote"]}', "lblb"))
    # triangle d'activité
    tp = [p for _, p in M.TRIANGLE]
    o.append(f'<polygon class="tri" points="{pts(tp)}"/>')
    for a, b in zip(tp, tp[1:] + tp[:1]):
        d = math.dist(a, b)
        mx, my = (a[0] + b[0]) / 2, (a[1] + b[1]) / 2
        o.append(f'<rect class="tribg" x="{f(mx - 11)}" y="{f(my - 6)}" width="22" height="10" rx="2"/>')
        o.append(text(mx, my + 1.5, f"{d:.0f}", "trit"))
    for _, (x, y) in M.TRIANGLE:
        o.append(f'<circle class="triv" cx="{f(x)}" cy="{f(y)}" r="2.5"/>')
    # coupe A-A
    for y, nom, d in ((COUPE_A, "A", -9), (COUPE_B, "B", 9)):
        o.append(f'<line class="sec" x1="-30" y1="{y}" x2="500" y2="{y}"/>')
        for x in (-30, 500):
            o.append(f'<path class="secm" d="M{x - 4} {y} l4 {d} l4 {-d} z"/>')
            o.append(text(x, y - d * 1.2 + 3, nom, "sect"))
    for x, nom, y0, y1 in ((COUPE_C, "C", -82, 300),):
        o.append(f'<line class="sec" x1="{x}" y1="{y0}" x2="{x}" y2="{y1}"/>')
        for y in (y0, y1):
            o.append(f'<path class="secm" d="M{x} {y - 4} l9 4 l-9 4 z"/>')
            o.append(text(x - 7, y + 4, nom, "sect"))
    # cotes : chaîne du mur nord, total des meubles, longueur de la pièce
    caissons = [b for b in M.MEUBLES if b.role == "caisson" and b.y0 == 0]
    o.append(cote_h(0, caissons[0].x0, -30))
    for b in caissons:
        o.append(cote_h(b.x0, b.x1, -30))
    o.append(cote_h(caissons[-1].x1, M.X_CLOISON, -30))
    hauts = [b for b in M.MEUBLES if b.role == "caisson_haut"]
    o.append(cote_h(0, hauts[0].x0, -48))
    for b in hauts:
        o.append(cote_h(b.x0, b.x1, -48))
    for b in hauts:
        o.append(text((b.x0 + b.x1) / 2, 10, b.etiq, "lbls muted"))
    for y0, y1 in ((M.JOUE_C2, M.COL_Y0), (M.COL_Y0, M.COL_Y0 + 60), (M.COL_Y0 + 60, M.COL_Y1)):
        o.append(cote_v(y0, y1, 402))
    # passages depuis l'angle sud-est des façades des meubles bas : frigo, mur nord du WC
    o.append(cote_d((M.sur_bas(M.B_EVIER)[1], 62), (M.COL_X, M.JOUE_C2), 0.5, (-7, 4)))
    # porte d'entrée à galandage : baie, poche
    o.append(cote_h(en["x0"], en["x1"], 282, f'baie {f(en["x1"] - en["x0"])}'))
    o.append(cote_h(*en["poche"], 282, f'poche {f(en["poche"][1] - en["poche"][0])}'))
    o.append(cote_h(0, 434, -66))
    o.append(text(-4, -27, "bas", "lblx muted", "end"))
    o.append(text(-4, -45, "hauts", "lblx muted", "end"))
    o.append(cote_v(0, M.P_CAISSON + M.FACADE, M.sur_bas(M.B_EVIER)[1] - 8))
    o.append(cote_v(0, M.P_ETROIT + M.FACADE, M.sur_bas(M.B_ETROIT)[0] + 5))
    # mur ouest
    o.append(cote_v(0, fe["y0"], -34))
    o.append(cote_v(fe["y0"], fe["y1"], -34, f'fenêtre {f(fe["y1"] - fe["y0"])}'))
    o.append(cote_v(fe["y1"], 252, -34))
    o.append(cote_v(0, 252, -52))
    # nord
    o.append('<g transform="translate(470 -60)"><path class="dark" d="M0 -10 L5 4 L0 1 L-5 4 Z"/>'
             + text(0, 14, "N", "lblb") + "</g>")
    return (f'<svg viewBox="-75 -90 590 410" role="img" aria-label="Plan vu de dessus, pièce vide, '
            f'6 meubles bas et 5 meubles hauts de 60 au mur nord">{"".join(o)}</svg>')


# ------------------------------------------------------------------ règle des hauteurs (bouton de la page)
TAILLE_BTN = ('<div class="tog"><span>Taille</span><button type="button" class="btaille" aria-pressed="true">'
              '1,75 m</button></div>')
TAILLE_JS = """
  var TAILLES = ["175", "180", "off"], TLIB = {"175": "1,75 m", "180": "1,80 m", "off": "masquée"};
  function taille(t) {
    if (TAILLES.indexOf(t) < 0) t = "175";
    document.documentElement.dataset.taille = t;
    document.querySelectorAll(".btaille").forEach(function (b) {
      b.textContent = TLIB[t]; b.setAttribute("aria-pressed", t !== "off");
    });
    document.querySelectorAll("svg[data-vb0]").forEach(function (s) {
      s.setAttribute("viewBox", t === "off" ? s.dataset.vb0 : s.dataset.vb1);
    });
    try { localStorage.setItem("cuisine-v13-taille", t); } catch (e) {}
  }
  document.querySelectorAll(".btaille").forEach(function (b) {
    b.addEventListener("click", function () {
      var i = TAILLES.indexOf(document.documentElement.dataset.taille);
      taille(TAILLES[(i + 1) % TAILLES.length]);
    });
  });
  try { taille(localStorage.getItem("cuisine-v13-taille") || "175"); } catch (e) { taille("175"); }
"""


# ------------------------------------------------------------------ hauteur du plan de travail (V13.28)
def section_hauteur_pt():
    noms = list(M.COUDES)
    ent = "".join(f"<th>{n} (coude {M.COUDES[n]})</th>" for n in noms)
    lignes = []
    for h, _, comment in M.PT_CANDIDATS:
        cells = []
        for n in noms:
            c = M.COUDES[n]
            e, el, ea = (hors_fourchette(h, c, r) for r in (M.PT_SOUS_COUDE, M.HSE_LEGER, M.HSE_APPUI))
            cells.append(f'<td class="{"ok" if e == 0 else ""}"><span class="mono">coude − {c - h}</span><br>'
                         f'cuisinistes : {etat(e)}<br><span class="note">léger : {etat(el)} · appui : {etat(ea)}</span></td>')
        tot = sum(abs(hors_fourchette(h, M.COUDES[n])) for n in noms)
        rec = ' class="hpr"' if h == M.PT_RECO else ""
        lignes.append(f'<tr{rec}><td class="mono"><b>{h}</b>{" (actuel)" if h == M.PT_Z1 else ""}</td>{"".join(cells)}'
                      f'<td class="mono">{tot}</td><td class="mono">{M.HAUT_Z0 - h}</td><td>{escape(comment)}</td></tr>')
    vi, vc = M.COUDES["Vincent"], M.COUDES["Victor"]
    (ll, lh), (al, ah) = M.HSE_LEGER, M.HSE_APPUI
    r = M.PT_RECO
    return f"""<h2>Hauteur du plan de travail (étude)</h2>
<div class="fig"><p class="cap"><b>Étude seulement</b> : rien n'est appliqué au plan, le plan de travail reste à {M.PT_Z1} dans le modèle, les coupes et les rendus.</p><div class="scroll hpw">{hauteur_pt_svg()}</div>
<p class="cap">Coudes mesurés debout, du sol au dessous du coude, avant-bras plié à 90° : Vincent {vi}, Victor {vc} ({vc - vi} d'écart). <b>Bande verte</b> : règle des cuisinistes, plan 10 à 15 sous le coude. <b>Barres fines</b> de part et d'autre (ergonomie du travail debout, HSE / <i>Bodyspace</i>) : à gauche, tâches avec appui (couper du dur, pétrir, presser), {al} à {ah} sous le coude ; à droite, gestes légers et précis (éplucher, garnir), {ll} à {lh} sous le coude. <b>Trait ocre</b> : plaque idéale, 20 sous le coude (Siemens). Tireté rouge : coude. Traits horizontaux : hauteurs candidates (plein : actuelle {M.PT_Z1} ; bleu : conseillée {r}).</p>
<table class="hpt-tab"><thead><tr><th>Plan</th>{ent}<th>Hors fourchette cuisinistes (total)</th><th>Plan → hauts</th><th>Comment l'obtenir (caisson METOD 80 + plan 4)</th></tr></thead><tbody>{"".join(lignes)}</tbody></table>
<div class="txt">
<p><b>Ce que disent les sources.</b> Tout le monde part du coude, mais pas avec le même écart. Les cuisinistes (Bora, Neff, guides allemands) disent 10 à 15 sous le coude ; la table de Neff donne coude 107 → plan 92, coude 114 → 99, coude 125 → 110. Les références d'ergonomie du travail debout (HSE, Pheasant et Haslegrave, <i>Bodyspace</i> ; NIOSH d'après Grandjean) distinguent la tâche : gestes légers {ll} à {lh} sous le coude, tâches avec appui {al} à {ah} sous le coude, travail de précision au-dessus du coude. La règle des cuisinistes (10 à 15) est un compromis entre les deux, pour une cuisine où l'on fait de tout.</p>
<p><b>Ce que ça change pour vous deux.</b> Avec la règle des cuisinistes, les fourchettes ne se recouvrent pas (Vincent {vi - 15} → {vi - 10}, Victor {vc - 15} → {vc - 10}). Avec la règle par tâche, elles se recouvrent : de {vi - lh} à {vi - ll}, le plan est « léger » pour Vincent et « appui » pour Victor, donc correct pour les deux, à condition que Victor fasse surtout la découpe et la pâte, et Vincent les gestes fins. Le plan conseillé, <b>{r}</b>, est au milieu de ce recouvrement et partage l'écart à la règle des cuisinistes : 2 de trop pour Vincent, 2 de trop peu pour Victor.</p>
<p><b>Trop haut ou trop bas ?</b> Une étude sur onze cuisines de cantine a trouvé le plan de découpe trop haut pour un tiers des cuisiniers, d'après leur coude ; les douleurs de nuque et d'épaule y étaient plus fréquentes chez les plus petits. Un plan trop haut fait lever les épaules ; un plan trop bas fait pencher le dos. Les deux fatiguent ; on compense facilement un plan trop bas (planche épaisse de 4 à 5 pour le plus grand), pas un plan trop haut.</p>
<p><b>Évier : il pousse vers le haut.</b> Neff mesure l'évier au <i>fond du bac</i> : c'est lui qui doit être à la hauteur de travail (coude − 15), et le bord peut monter jusqu'à 15 au-dessus. Avec un bac d'environ 18 à 20 de profondeur (à vérifier sur le modèle), le fond est à ≈ {r - 19} pour un plan à {r} : {vi - 15 - (r - 19)} sous la hauteur de travail de Vincent ({vi - 15}), {vc - 15 - (r - 19)} sous celle de Victor ({vc - 15}). Aucun plan standard ne met le fond du bac à la bonne hauteur : la vaisselle est le poste où l'on se penche le plus, Victor surtout, et chaque centimètre gagné sur le plan y compte. À {M.PT_Z1}, le fond serait à ≈ {M.PT_Z1 - 19}. Un bac moins profond, ou un égouttoir / bassine posé dans le bac pour la vaisselle à la main, réduit l'écart.</p>
<p><b>Plaque : elle pousse vers le bas.</b> Le bord de la casserole donne la hauteur de travail : Neff conseille la plaque 15 sous le plan, Siemens 20 sous le coude (Vincent {vi - M.PLAQUE_SOUS_COUDE}, Victor {vc - M.PLAQUE_SOUS_COUDE}) ; certains guides allemands la mettent au contraire au même niveau que l'évier, 10 sous le coude. Pas de consensus. Sur un plan continu, la plaque est à la hauteur du plan : à {r}, haute pour Vincent dans une grande casserole, correcte pour Victor.</p>
<p><b>Couples de tailles différentes.</b> Les designers proposent trois réponses : choisir la hauteur de celui qui cuisine le plus, faire des zones à deux hauteurs (souvent un îlot plus haut que le linéaire), ou un plan réglable. Ici, sans îlot, une zone à deux hauteurs voudrait dire un ressaut dans le plan du mur nord, par exemple l'évier (B{M.B_EVIER}) et B{M.B_ETROIT} plus hauts que la plaque et les tiroirs (B1 → B{M.B_TIROIRS_2}) ; c'est faisable avec des pieds différents mais cela casse la ligne du plan, de la crédence et des façades.</p>
<p><b>Avant de décider : essayer.</b> Comme pour l'implantation (V13.17), un essai grandeur nature tranche mieux que les règles : un plateau posé sur des cales à 92, 96 puis 98, et chacun y coupe des légumes, y pétrit, y tient une casserole pendant quelques minutes.</p>
<p><b>Conséquences d'un plan plus haut.</b> Les colonnes C1 et C2 sont sur les mêmes pieds : elles montent d'autant (dessus {M.COL_Z1} + Δ, fileur au-dessus réduit). Les meubles hauts restent à h {M.HAUT_Z0} : l'espace plan → hauts diminue (colonne « Plan → hauts ») ; vérifier la distance minimale plaque → hotte imposée par la notice de la hotte intégrée dans H1. Au-delà de 94, la plinthe IKEA de 8 ne suffit plus : plinthe sur mesure (même façade). Four sous la plaque et lave-vaisselle en hauteur dans C1 : non concernés.</p>
<p class="src">Sources. Règle des cuisinistes : <a href="https://www.bora.com/fr-fr/guide/la-cuisine-ergonomique-lignes-directrices-conseils">Bora</a> ; <a href="https://neff-home.com/fr/decouvrez-neff/conseils-pour-amenager-votre-cuisine/etapes/ergonomie">Neff</a> (plan, plaque, évier) et sa <a href="https://www.neff-home.com/de/neff-entdecken/kuechenplanung/schritte/ergonomie">table coude → plan</a> ; <a href="https://www.hausjournal.net/hoehe-kuechenarbeitsflaeche">Hausjournal</a> (évier et plaque 10 sous le coude) ; <a href="https://www.siemens-home.bsh-group.com/fr/inspiration-siemens/design/votre-projet-cuisine/table-de-cuisson">Siemens</a> (plaque 20 sous le coude). Ergonomie du travail debout : <a href="https://www.hse.gov.uk/MSD/uld/art/posture.htm">HSE</a> ; <a href="https://www.msdprevention.com/resource-library/standing-workstation-height-manual-tasks">CRE-MSD</a> ; <a href="https://webarchive.library.unt.edu/eot2008/20080923002046/http://www.cdc.gov/niosh/pdfs/97-117-f.pdf">NIOSH, <i>Elements of Ergonomics Programs</i></a> (d'après Grandjean). Étude en cantine : <a href="https://pubmed.ncbi.nlm.nih.gov/15676673/">PubMed 15676673</a> (résumé seul). Couples : <a href="https://www.livingetc.com/advice/should-a-kitchen-island-be-the-same-height-as-the-counters">Livingetc</a>, <a href="https://www.homesandgardens.com/kitchens/should-a-kitchen-island-be-the-same-height-as-the-counters">Homes &amp; Gardens</a>. Pieds METOD (≈ 7 → 10,5, chiffre de forum, non confirmé par IKEA) : <a href="https://www.forumconstruire.com/construire/topic-407503-remplacer-pieds-elements-metod.php">Forumconstruire</a>, <a href="https://www.ikea.com/fr/fr/p/metod-pied-70556067">fiche IKEA</a>.</p>
</div></div>
"""


# ------------------------------------------------------------------ porte du cellier : Mantion Tango (V13.14)


def section_tango():
    a, t = M.PLIANTE, M.TANGO
    return f"""<h2 class="h2b">Porte du cellier · {t["nom"]} <a class="impr" href="cuisine-v13-porte-cellier.html">Plans détaillés</a></h2>
<div class="fig">{fiche_tango()}
<div class="txt">
<p><b>Le principe.</b> Une porte pliante à deux vantaux, sans dormant ni cadre : toute la ferrure tient dans un rail en
aluminium vissé sous le linteau. Le vantail nord tourne sur deux pivots (haut et bas) placés contre le bout du mur neuf ;
le vantail sud lui est attaché par trois charnières sur chant et son bout libre est suspendu à une monture à roulements
qui roule dans le rail. Fermée, la porte est dans l'épaisseur de la cloison, au nu côté cuisine (rail à x {virg(a["rail"])}).</p>
<p><b>À l'ouverture.</b> On tire la poignée, au sud, côté C1 : le vantail nord pivote vers la cuisine, le vantail sud se
plie contre lui et la monture glisse vers le nord. Ouverte, la porte forme un paquet de {virg(2 * a["ep"])} d'épaisseur,
perpendiculaire à la baie, côté cuisine, qui dépasse de {virg(a["l"])} : il reste {virg(M.JEU_B6_PORTE)} jusqu'au plan
de B{M.B_ETROIT}. Elle ne peut pas s'ouvrir vers le cellier : le paquet heurterait le rayonnage nord. Passage libre
≈ {virg(M.PASSAGE_CELLIER)}.</p>
<p><b>Pourquoi ce modèle.</b> Il est vendu « pour portes de séparation et portes de placard » : pas de rail au sol (le
sol reste continu entre cuisine et cellier), panneaux de 16 à 40 mm et jusqu'à 40 kg, alors que les nôtres font 1,9 et
≈ 9 kg. Sa géométrie est celle dessinée sur le plan : pivot au nord, paquet replié hors de la baie, côté cuisine.</p>
<p><b>Pose.</b> Rail recoupé à la largeur de la baie et vissé sous le linteau (sous-face h 204) ; pivot bas vissé au sol
contre le mur neuf ; panneaux découpés, charnières sur chant ; réglage en hauteur à la clé (jeu de 2 sous le rail, 1,1 au
sol). En option, les charnières indexables 1504 PI tiennent la porte fermée et suppriment le jeu entre panneaux, mais
changent les cotes de découpe (refaire le calcul avec SLIDESOFT).</p>
<p><b>À vérifier avant de commander.</b> Le passage exact, que la notice ne donne pas ; l'unité du « 1,2 » de la formule
de largeur (lu en mm ; en cm, chaque panneau perd 5 mm) ; la finition des panneaux et la poignée.</p>
<p class="src">{sources_tango()}</p>
</div></div>
"""


# ------------------------------------------------------------------ électricité


def coupe_elec_nord():
    """Élévation du mur nord (coupe A-A) avec les boîtiers posés sur ce mur ou au fond des meubles de la rangée."""
    def boitiers(X):
        o = []
        for r, x, y, z, n, c, _, ou in M.PRISES:
            if y != 0:
                continue
            w = 7 if n == 1 else 13
            cls = "elpe" + (" elpd" if c not in ("plan", "autres") else "") + (" elc" if ou.startswith("dans") else "")
            o.append(rect(X(x) - w / 2, -z - 3.5, X(x) + w / 2, -z + 3.5, cls))
            o.append(text(X(x), -z - 6, r, "lblx elpt"))
        for r, _, x, y, z, _, touches in M.INTERRUPTEURS:
            if y == 0:
                h = 7 * len(touches)
                o.append(rect(X(x) - 3.5, -z - h / 2, X(x) + 3.5, -z + h / 2, "elie"))
                o.append(text(X(x), -z - h / 2 - 2.5, r, "lblx elt"))
        o.append(text(X(145), -M.HAUT_Z0 + 7, "L2 · LED", "lblx elt"))
        return o

    return coupe_svg(COUPE_A, "nord", -20, 494, [], [M.PT_Z1, 110, M.HAUT_Z0], -50, boitiers)


def tables_elec():
    lum = {r: n for r, n, *_ in M.LUMIERES}
    lignes = ""
    for r, nom, x, y, z, ou, touches in M.INTERRUPTEURS:
        for k, (t, l, mode) in enumerate(touches):
            tete = (f'<td rowspan="{len(touches)}" class="mono">{r}</td><td rowspan="{len(touches)}"><b>{escape(nom)}</b>'
                    f' · h {z}<br>{escape(ou)}</td>') if k == 0 else ""
            lignes += f"<tr>{tete}<td>{escape(t) or '—'}</td><td><b>{l}</b> {escape(minus(lum[l]))}</td><td>{escape(mode)}</td></tr>"
    lignes += ('<tr><td class="mono">—</td><td><b>Hotte</b></td><td>—</td><td>lumière de la hotte</td>'
               '<td>touches de la hotte</td></tr>')
    t1 = ('<table class="orga"><thead><tr><th>Inter.</th><th>Où</th><th>Touche</th><th>Allume</th><th>Fonctionnement</th>'
          f'</tr></thead><tbody>{lignes}</tbody></table>')
    circ = {k: n for k, n, *_ in M.CIRCUITS}
    pts_ = "".join(f'<tr><td class="mono">{r}</td><td>{escape(n)}</td><td>{escape(p)}</td><td class="num">plafond</td>'
                   f'<td>{circ["eclairage"]}</td></tr>' for r, n, _, _, p in M.LUMIERES)
    pts_ += "".join(f'<tr><td class="mono">{r}</td><td>{"prise double" if n == 2 else "prise"} · {escape(u)}</td>'
                    f'<td>{escape(ou)}</td><td class="num">{z}</td><td>{circ[c]}</td></tr>'
                    for r, x, y, z, n, c, u, ou in M.PRISES)
    t2 = ('<table class="orga"><thead><tr><th>Repère</th><th>Quoi</th><th>Où</th><th class="num">h</th><th>Circuit</th>'
          f'</tr></thead><tbody>{pts_}</tbody></table>')
    t3 = ('<table class="orga"><thead><tr><th>Circuit</th><th>Protection, section</th><th>Points</th></tr></thead><tbody>'
          + "".join(f"<tr><td>{escape(n)}</td><td>{escape(p)}</td><td>{escape(c)}</td></tr>" for _, n, p, c in M.CIRCUITS)
          + "</tbody></table>")
    return t1, t2, t3


def section_elec():
    t1, t2, t3 = tables_elec()
    return f"""<h2>Électricité</h2>
<div class="fig"><div class="scroll">{plan_elec_svg()}</div>
<p class="cap">Proposition. Les traits tiretés relient chaque interrupteur à la lumière qu'il commande. Hauteurs (h) à l'axe du boîtier, depuis le sol fini. Les prises au fond des meubles (contour tireté) sont placées à côté de l'appareil, jamais derrière lui, pour pouvoir le débrancher en ouvrant le meuble voisin : four et plaque dans B1, lave-vaisselle sous sa niche, micro-ondes et frigo au-dessus de la leur. Au-dessus du plan de travail, rien au-dessus de la plaque ni de l'évier ; les prises de crédence sont à h 110, à mi-hauteur entre le plan (h {M.PT_Z1}) et les hauts (h {M.HAUT_Z0}).</p></div>

<h3>Quel interrupteur allume quoi</h3>
<div class="fig">{t1}
<p class="cap">En entrant, la main droite trouve S1 : en haut le plafonnier, au milieu les LED du plan de travail, en bas la suspension. On cuisine : S2, au bout du plan à côté de l'évier, allume ou éteint les LED sans revenir à l'entrée ; sa touche du bas allume le cellier en passant la porte (le voyant signale une lumière oubliée derrière la porte fermée). On passe à table : la suspension se règle depuis la banquette (S3) ; S1 et S3 sont deux poussoirs d'un même variateur (appui court : allume ou éteint, appui long : varie). En sortant, tout s'éteint depuis S1, sauf le cellier (S2).</p></div>

<h2>Élévation du mur nord · électricité</h2>
<div class="fig"><div class="scroll">{coupe_elec_nord()}</div>
<p class="cap">Même coupe que A-A. Boîtiers de la crédence (P1 → P3) et S2 à h 110 ; au fond des meubles, en tireté : P4 (hotte, dans H1), P5 (four) et P6 (sortie de câble de la plaque) dans B1 ; à droite, P12 dans le cellier.</p></div>

<h3>Points</h3>
<div class="fig">{t2}</div>

<h3>Circuits proposés</h3>
<div class="fig">{t3}
<p class="cap">NF C 15-100 (vérifié sur des guides, pas sur le texte de la norme ; à confirmer par l'électricien) : au moins 6 socles dans une cuisine de plus de 4 m², sur un circuit dédié 20 A de 6 socles au plus, dont 4 au-dessus du plan de travail ; une prise double compte pour 2 socles (ici 5 au-dessus du plan, plus le micro-ondes). Pas de prise au-dessus du bac de l'évier ni de la plaque ; 60 cm entre une prise et l'évier sont conseillés (P3 est à 65 du bac). Prises de crédence à 8 cm au moins au-dessus du plan (ici 19), prise de hotte à 1,80 m au moins (P4 : 2,25), sortie 32 A à 12 cm au moins du sol (P6 : 60). Circuits spécialisés pour la plaque (32 A, 6 mm², différentiel type A), le four et le lave-vaisselle. Point lumineux de plafond sur boîtier DCL. Le plafonnier suppose une boîte au plafond : à prévoir avec la suspension (dalle béton : en saillie ou par une saignée). Vérifier aussi la puissance de l'abonnement (plaque, four et LV ensemble).</p></div>
"""


# ------------------------------------------------------------------ page


def section_capacite(version, rows, details):
    """Section « Capacité » : V11.34 (avant), version affichée, écart, proposition 9 A et repères. Sert aussi à
    réécrire les versions figées (rows et details lus dans leur HTML). Cellules vertes dans le repère d'une cuisine
    de 8 m², rouges en dehors."""
    corps = corps_capacite(rows, details)
    av = M.AVANT["version"]
    return f"""<h2>Capacité : {av} → {version} et proposition 9 A</h2>
<div class="fig"><div class="scroll"><table class="orga capa"><thead><tr><th>Mesure</th><th>{av} (avant)</th><th>{version}</th><th>Écart</th>
<th>Proposition 9 A</th><th>Repère cuisine 8 m²</th></tr></thead><tbody>{corps}</tbody></table></div>
<p class="cap">Mesurée comme le font les cuisinistes : mètres linéaires de meubles, nombre de meubles, tiroirs, plan de travail utile (hors évier et plaque) et implantation, sur la version figée {av}, la version affichée et la proposition 9 A, avec les repères d'une cuisine d'environ 8 m² (la pièce fait 3,25 × 2,52 = 8,2 m² hors cellier). <b>En vert</b> : dans le repère ; <b>en rouge</b> : en dessous ; dépasser le haut du repère n'est pas une erreur. L'écart se lit par rapport à {av}. <b>Volume</b> (repère moins parlant, gardé pour comparer) : largeur × profondeur du caisson × hauteur des façades de rangement, électroménager, socles et sous-évier exclus ; cellier : largeur utile × profondeur × hauteur des rayonnages, de la première tablette au haut du rayonnage.</p></div>
"""


def texte_cellier():
    a, nord = M.PLIANTE, M.RAYON_NORD
    return (f"<b>Porte du cellier</b> ({M.PORTE_TITRE}) : un retour de cloison va du mur nord à y {f(M.CLOISON_Y1)} "
            f"(passage des réseaux ; V13.0 : allongé de {M.DECALAGE_PORTE}, la porte descend d'autant vers le sud) ; la baie va "
            f"jusqu'au flanc nord de C1 : {f(M.BAIE_Y1 - M.BAIE_Y0)} × 204 sous un "
            f"linteau. Porte pliante sans dormant sur ferrure <b>Mantion Tango</b> ({M.TANGO['ref']}, rail alu sous le linteau, "
            f"pas de rail au sol), deux panneaux de {virg(a['l'])} × {virg(round(a['z1'] - a['z0'], 1))} × {virg(a['ep'])} à faire découper, "
            f"pivot au nord : en s'ouvrant, les vantaux se replient l'un contre l'autre et se rangent côté cuisine contre "
            f"le retour de cloison, à {f(M.JEU_B6_PORTE)} du plan de B{M.B_ETROIT} (P{f(M.P_PLAN_ETROIT)} : c'est ce qui fixe sa profondeur ; "
            f"côté cellier, ils heurteraient le rayonnage nord) ; le "
            f"vantail du pivot balaie {virg(a['l'])} côté cuisine. Poignée au sud, côté C1 ; le bouton au-dessus du plan "
            f"la montre ouverte, mi-ouverte (vantaux en V, pivot à {a['mi']}°) ou fermée. <b>Passage libre ≈ {f(M.PASSAGE_CELLIER)}</b> ; accès depuis "
            f"la cuisine, du coin du plan de B{M.B_EVIER} à l'angle de C1 : {M.ACCES_CELLIER:.0f}. <b>Passages dans le "
            f"cellier</b> : {f(M.PASSAGE_ENTREE)} à l'entrée, entre le rayonnage nord et le flanc de C1 ; {f(M.PASSAGE_BALAIS)} "
            f"entre le rayonnage nord et les balais, vers la niche. "
            f"<b>Organisation du cellier</b> : un <b>rayonnage toute hauteur P{nord['y1']}</b> contre le mur nord, du "
            f"retour de cloison (V13.0 : prolongé jusqu'à lui, sans arrondi) jusqu'au mur de l'alcôve (x {nord['x0']} → {nord['x1']}, {len(nord['zs'])} tablettes "
            f"de {M.L_NORD}, la première à h {nord['zs'][0]} au-dessus des tuyaux), pour les denrées, avec l'aspirateur couché "
            f"dessous, au bout est ; contre le mur du WC "
            f"(V13.6, à la place du rayonnage sud), <b>deux balais</b> sur un tasseau à {100 - M.Y_BALAIS} du mur, devant "
            f"les tuyaux du LV ; entre les deux, {f(M.PASSAGE_BALAIS)} de passage vers la niche : nourrice, groupe de "
            f"sécurité et chute restent accessibles. Au-dessus des balais (V13.22), une <b>étagère P{M.ENTRETIEN['y1'] - M.ENTRETIEN['y0']}</b> à deux "
            f"tablettes (h {M.ENTRETIEN['zs'][0]} et {M.ENTRETIEN['zs'][1]}) pour les produits d'entretien, à part de la "
            f"nourriture ; le <b>seau</b> au sol dans l'angle sud-est, contre C1. "
            +             f"<b>Finitions</b> : fileur chêne de {M.FILEUR_C2} au sud de C2, jusqu'au fileur couleur des murs qui ferme l'angle "
            f"au nu du montant de l'entrée (y {f(M.Y_MONTANT)}), joue à l'ouest de H1, fileurs de "
            f"{f(M.FILEUR_EST)} entre B{M.B_ETROIT} / H{M.N_HAUTS} et le retour de cloison, fileurs de 7 jusqu'au "
            f"plafond au-dessus des hauts et des colonnes.")


def table_materiaux():
    def ech(e):
        if isinstance(e, str):
            return f'<img src="{e}" alt="" style="width:120px;height:60px;object-fit:cover;border-radius:4px;display:block">'
        return "".join(f'<span style="display:inline-block;width:{120 // len(e)}px;height:60px;background:{c};'
                       f'{"border-radius:4px 0 0 4px;" if k == 0 else ""}{"border-radius:0 4px 4px 0;" if k == len(e) - 1 else ""}'
                       f'{"border-radius:4px;" if len(e) == 1 else ""}"></span>' for k, c in enumerate(e))
    corps = "".join(f"<tr><td>{ech(e)}</td><td>{escape(n)}</td><td><b>{escape(m)}</b><br>{escape(p)}</td></tr>"
                    for n, m, p, e in M.MATERIAUX)
    return ('<table class="orga"><thead><tr><th style="width:136px">Échantillon</th><th>Élément</th><th>Matériau</th>'
            f'</tr></thead><tbody>{corps}</tbody></table>')


def galerie(items):
    """Rendus groupés (M.RENDUS_GROUPES) : un titre par groupe, des boutons quand une même vue a des variantes.
    items : {vue: (src, titre, légende HTML)} ; sert aussi à réécrire les galeries des versions figées."""
    html = ""
    for titre, vues in M.RENDUS_GROUPES:
        vs = [(v, lib) for v, lib in vues if v in items]
        if not vs:
            continue
        variantes = bool(vs[0][1]) and len(vs) > 1
        figs = "".join(f'<figure data-rv="{v}"{" hidden" if variantes and k else ""} style="margin:0 0 18px">'
                       f'<img src="{items[v][0]}" alt="{escape(items[v][1])}" loading="lazy" '
                       f'style="width:100%;border-radius:8px;display:block">'
                       f'<figcaption class="cap"><b>{escape(items[v][1])}</b> — {items[v][2]}</figcaption></figure>'
                       for k, (v, lib) in enumerate(vs))
        boutons = ('<div class="tog rtog"><span>Variante</span>' + "".join(
            f'<button type="button" data-rv="{v}" aria-pressed="{str(k == 0).lower()}">{escape(lib)}</button>'
            for k, (v, lib) in enumerate(vs)) + "</div>") if variantes else ""
        html += f'<h3>{escape(titre)}</h3>\n<div class="fig rgrp">{boutons}{figs}</div>\n'
    return html


def galerie_rendus():
    items = {v: (f"cuisine-v13-3d/{v}.jpg?v={M.RENDUS_VERSION[v]}", t, f"{escape(c)} (rendu {M.RENDUS_VERSION[v]})")
             for v, t, c in M.RENDUS if os.path.exists(os.path.join(ROOT, "cuisine-v13-3d", f"{v}.jpg"))}
    if not items:
        return ""
    return (f'<h2 class="h2b">Rendus 3D <a class="impr" href="cuisine-v13-maquette.html">Maquette 3D</a></h2>\n{galerie(items)}<p class="cap">Blender (Cycles) depuis le modèle FreeCAD de '
            f'la version indiquée sous chaque image (rendus faits sur demande) : 21 juin, 17 h, soleil réel par la fenêtre, '
            'suspension et LED allumées ; matériaux de la section Matériaux (teintes indicatives).</p>\n')


def table_contenu():
    corps = "".join(f"<tr><td>{escape(n)}</td><td>{escape(u)}</td></tr>" for n, u in M.CONTENU)
    return f'<table class="orga"><thead><tr><th>Meuble</th><th>Contenu</th></tr></thead><tbody>{corps}</tbody></table>'


def contenu():
    caissons = [b for b in M.MEUBLES if b.role == "caisson" and b.y0 == 0]
    x0, x1 = caissons[0].x0, caissons[-1].x1
    hauts = [b for b in M.MEUBLES if b.role == "caisson_haut"]
    cols = [b for b in M.MEUBLES if b.role == "colonne" and b.nom.startswith("caisson_c")]
    tp = M.TRIANGLE
    cotes_tri = [math.dist(a[1], b[1]) for a, b in zip(tp, tp[1:] + tp[:1])]
    tri = ", ".join(f"{a[0]} → {b[0]} {d:.0f}" for (a, b), d in zip(zip(tp, tp[1:] + tp[:1]), cotes_tri))
    lignes = "".join(f'<tr><td class="mono">{v}</td><td class="mono">{d}</td><td>{escape(c)}</td></tr>'
                     for v, d, c in M.CHANGEMENTS)
    return f"""<div class="kicker">Cuisine · {M.VERSION}</div>
<h1>Plan de la cuisine V13</h1>
<p class="pitch">Nouveau départ depuis la pièce vide. Le plan et la coupe sont générés depuis le modèle 3D : une seule source, aucune cote reportée à la main.</p>

<h2 class="h2b">Plan <span><a class="impr" href="cuisine-v13-maquette.html">Maquette 3D</a> <a class="impr" href="cuisine-v13-porte-cellier.html">Porte du cellier</a> <a class="impr" href="cuisine-v13-imprimable.html">Version imprimable</a></span></h2>
<div class="fig"><div class="tog"><span>Portes</span><button type="button" data-vt="entree" aria-pressed="false" data-on="ouverte" data-off="fermée">entrée : fermée</button>{"".join(f'<button type="button" data-vt="{k}" aria-pressed="true" data-on="ouverte" data-off="fermée"' + (' data-etats="ouvert|mi|ferme" data-libs="ouverte|mi-ouverte|fermée" data-i="1"' if M.PLIANTE else '') + '>cellier : ' + ('mi-ouverte' if M.PLIANTE else 'ouverte') + '</button>' for k in (["cellier"] if M.PLIANTE else range(len(M.CELLIER_VANTAUX))))}</div><div class="scroll">{plan_svg()}</div>
<p class="cap">Échelle : 1 unité = 1 cm. Pièce vide : chambre et ancien cellier ouverts, sans cloison. Restent la fenêtre coulissante du mur ouest (y 58 → 200), la porte d'entrée (baie x 228 → 306), le décroché de l'angle sud-est, la chute (sous le ballon), le ballon et le WC. <b>Sols</b> : parquet chêne en bâtons rompus dans l'ancienne chambre (x 0 → 325), gris ciment dans l'ancien cellier et l'ancien placard (à partir de x 325) ; les cloisons déposées du relevé d'origine sont en tireté (chambre / cellier x 325 → 335, cellier / placard y 100 → 110). <b>Mur nord</b> : {len(caissons)} meubles bas de {' + '.join(f(w) for w in M.LARGEURS_BAS)} (x {f(x0)} → {f(x1)}), à {f(M.ECART_OUEST)} du mur ouest et {f(M.FILEUR_EST)} du retour de cloison du cellier (fileurs Canopée) : plan de travail de mur à mur ; caisson P{M.P_CAISSON} + façade {M.FACADE}, profondeur {M.P_CAISSON + M.FACADE}, sous un plan de travail de 4 (P62, débord de 2), sauf B{M.B_ETROIT} (P{M.P_ETROIT} + façade, profondeur {M.P_ETROIT + M.FACADE}, plan P{M.P_PLAN_ETROIT}) qui laisse se replier la porte du cellier. <b>Induction</b> 60 classique, four encastré dessous et hotte intégrée dans H1 au-dessus, sur B{M.B_PLAQUE} (x {f(M.sur_bas(M.B_PLAQUE)[0])} → {f(M.sur_bas(M.B_PLAQUE)[1])}) ; <b>évier</b> inox 1 bac 56 × 50 (bac 40 × 40) sur B{M.B_EVIER} (x {f(M.sur_bas(M.B_EVIER)[0])} → {f(M.sur_bas(M.B_EVIER)[1])}), mitigeur derrière le bac, égouttoir à gauche au-dessus de B4. <b>Mur est</b> : colonnes C1 (lave-vaisselle en hauteur, micro-ondes au-dessus, y {f(M.JOUE_C2)} → {f(M.COL_Y0)}) et C2 (frigo, y {f(M.COL_Y0)} → {f(M.COL_Y0 + 60)}) de 60, P60, fileur chêne de {M.FILEUR_C2} entre C2 et le décroché (la porte du frigo s'ouvre à 90° sans toucher le fileur de l'entrée), contre le mur du WC (x {f(M.X_MUR_EST)}), du décroché vers le nord, façades vers l'ouest (x {f(M.COL_X)}). Le mur sud est libre entre la table et le caisson du galandage. <b>Porte d'entrée</b> : à galandage, vantail {f(M.ENTREE["vantail"])} × {M.ENTREE["h"]} (trait plein, fermé) ; ouverte, elle rentre vers l'ouest dans un caisson de galandage (ocre, x {f(M.ENTREE["poche"][0])} → {f(M.ENTREE["poche"][1])}) logé dans un doublage de 10 contre le mur sud (y 242 → 252), avec un montant de 4 à l'est de la baie. Le passage reste de {f(M.ENTREE["x1"] - M.ENTREE["x0"])} ; rien ne bat dans la cuisine. Face cuisine du caisson : <b>tableau noir</b> (peinture ardoise, h 120 → 200) et <b>zone aimantée</b> en dessous (h 70 → 118), sur 81 de large (coupe B-B). <b>Équipements</b> : poubelles de tri sous l'évier (B{M.B_EVIER}), four sous la plaque (B{M.B_PLAQUE}), lave-vaisselle 60 tout intégrable en hauteur dans C1. <b>Triangle d'activité</b> (rouge ; centres de la plaque et de l'évier, milieu de la façade du frigo) : {tri}, total {f(round(sum(cotes_tri)))} cm. <b>Passage</b> (cote oblique) : {M.ACCES_CELLIER:.0f} du coin du plan de travail P62 (B{M.B_EVIER}, x {f(M.sur_bas(M.B_EVIER)[1])}, y 62) au coin nord-ouest de C1 (y {M.JOUE_C2}), devant la porte du cellier. <b>Réseaux</b> (bleu ; pose type IKEA METOD, sans vide technique : 1 cm de jeu derrière les caissons). Le <b>LV</b>, en hauteur dans C1, est raccordé par le cellier sans le traverser : alimentation depuis la nourrice le long du mur est puis du mur nord du WC, sous le rayonnage sud, jusqu'au dos de C1 ; vidange pompée par le LV le long du même mur, directement dans la chute. À l'est de l'évier, les tuyaux passent dans le <b>fond de B{M.B_ETROIT}</b> (découpé, tiroirs P30) et derrière son fileur, puis dans le retour de cloison au nord de la porte du cellier : tout <b>longe les murs</b>, en partie basse. Alimentation EF/EC en trait plein, à 3 des murs, depuis la <b>nourrice</b> (petit point, sous le ballon) : le long du retour sud de l'alcôve (y 44), de sa face ouest (x 434), puis du mur nord jusqu'à l'évier ; une seconde ligne va au LV (C1) le long du mur nord du WC. Dans la niche du cellier, tout reste dans la zone technique des {M.ZONE_TECH} premiers cm (la chute est basse, dernier étage) : l'alimentation y passe à h 20 et remonte dans l'angle, l'évacuation descend à h 25 sous la première tablette du rayonnage nord ; un coffre technique (h 0 → {M.ZONE_TECH}) couvre l'angle. Évacuation en tireté depuis le siphon de l'évier (axe x {f(M.SIPHON[0])}), à 4 du mur nord dans la cuisine, puis à 12 des murs pour passer au-delà de la nourrice : le long du mur nord, de l'alcôve, du mur est (x 484) puis du mur nord du WC jusqu'à la <b>chute</b> (cercle contre le mur du WC, sous le ballon : la colonne d'eaux usées existante, x à confirmer). Contre l'alcôve, ils passent sous la première tablette du rayonnage du mur nord ; sous le ballon (h 90), ils passent dessous ; longueur ≈ {f(M.EVAC_LONGUEUR)} : de h {M.RESEAUX[3][3]} sous le siphon à h {M.RESEAUX[4][3]} à la chute, soit {(M.RESEAUX[3][3] - M.RESEAUX[4][3]) / M.EVAC_LONGUEUR * 100:.1f} cm/m de pente moyenne (hauteur d'arrivée sur la chute à confirmer). Les réseaux traversent la cloison du cellier. <b>Cellier</b> : cloison de 7 (x 320 → 327), contre le fileur de B{M.N_BAS}. {texte_cellier()} <b>Coin repas</b> (V13.17) : banquette d'une place contre le mur ouest, dans l'angle sud-ouest, assise tournée vers l'est (x {f(M.BANQ["x0"])} → {f(M.BANQ["x1"])}, y {f(M.BANQ["y0"])} → {f(M.BANQ["y1"])} : {f(M.BANQ["y1"] - M.BANQ["y0"])} de long, dossier {M.BANQ["dossier"]} à h 85 contre le mur, assise {f(M.BANQ["x1"] - M.BANQ["x0"] - M.BANQ["dossier"])} à h 45 avec coffre) ; elle passe de {f(200 - M.BANQ["y0"])} sous la fenêtre (y 200), le dossier reste sous l'allège (h 106). Table type Véra {M.TABLE["cote"]} × {M.TABLE["cote"]} aux angles arrondis (rose poudré, chant noir), sur un pied central à embase, à 10 de l'assise et à 10 du bas de mur sud (x {f(M.TABLE["x0"])} → {f(M.TABLE["x1"])}, y {f(M.TABLE["y0"])} → {f(M.TABLE["y1"])}) : son bord nord est à {f(M.TABLE["y0"] - M.P_CAISSON - M.FACADE - 52)} de la porte du four ouverte (y {f(M.P_CAISSON + M.FACADE + 52)}) et à {f(M.TABLE["y0"] - 62)} du plan de travail. Une <b>chaise</b> {M.CHAISE["l"]} × {M.CHAISE["p"]} en face, côté est, dossier à l'est. Mur sud derrière la table : <b>bas de mur</b> en chêne miel (2, h {M.BAS_DE_MUR["h"]}, x {f(M.BAS_DE_MUR["x0"])} → {f(M.BAS_DE_MUR["x1"])}), où s'appuie la banquette, et papier peint Hermione au-dessus jusqu'au plafond (voir Matériaux). <b>Suspension</b> (tireté jaune) : point lumineux au plafond centré sur la table, abat-jour Ø {M.SUSPENSION["d"]}, bas à h {M.SUSPENSION["z0"]}, soit {M.SUSPENSION["z0"] - 75} au-dessus du plateau (coupe B-B). <b>Places</b> : {M.PLACES_BANQUETTE} sur la banquette + 1 sur la chaise ; un tabouret pliant côté nord en appoint. <b>Sous la banquette</b> : un seul tiroir, ouvert côté nord (façade h 6 → 40), hors des jambes et de la table (tireté : tiroir sorti de 35, jusqu'à y {f(M.BANQ["y0"] - 37)}). <b>Au-dessus</b> (tireté) : étagère P25 contre le mur sud, du mur ouest au doublage de l'entrée, dessus à h {f(M.ETAGERE_BANQ["z1"])}, avec l'enceinte audio (22 × 18 × 30) à l'est et la plante à l'ouest (coupe B-B). <b>Ouvertures</b> : porte du LV abattue (C1, x {f(M.COL_X - 58)} → {f(M.COL_X)}, y {f(M.JOUE_C2)} → {f(M.JOUE_C2 + 60)}), porte du four abattue (sous la plaque), porte du frigo (dessinée à 90°), charnières au sud : elle se rabat vers le sud, devant le fileur de C2 ({M.FILEUR_C2}), et on accède au frigo par le nord, côté évier. Elle s'ouvre au plus à ≈ {M.FRIGO_ANGLES["entree_fermee"][0]:.0f}° porte d'entrée fermée (son bout touche le vantail d'entrée) et ≈ {M.FRIGO_ANGLES["entree_ouverte"][0]:.0f}° porte d'entrée ouverte (montant du galandage) ; calcul sur une façade de 60 × 2 tournant autour de son angle avant, à quelques degrés près selon la charnière. <b>Meubles hauts</b> (tireté) : {len(hauts)} de {' + '.join(f(w) for w in M.LARGEURS_HAUTS)}, x {f(hauts[0].x0)} → {f(hauts[-1].x1)}, joints au droit de ceux des bas, fileur de {f(M.FILEUR_EST)} jusqu'au retour de cloison ; à leur gauche, étagères ouvertes jusqu'au mur ouest ; caisson P{M.P_HAUT} + façade {M.FACADE} (H5 compris, comme H4).</p></div>

<h2>Coupe A-A · mur nord</h2>
<div class="fig">{TAILLE_BTN}<div class="scroll">{regle(coupe_a(), -20, 494)}</div>
<p class="cap">Coupe à y {COUPE_A}, regard vers le nord. Pieds et plinthe {M.SOCLE} (METOD), caissons bas de {M.CAISSON_H - M.SOCLE} h {M.SOCLE} → {M.CAISSON_H}, plan de travail 4 (h {M.CAISSON_H} → {M.PT_Z1}), meubles hauts h {M.HAUT_Z0} → {M.HAUT_Z1}, fileur de {M.H - M.HAUT_Z1} jusqu'au plafond ({M.H}). <b>Ruban LED</b> (jaune) sous H1 → H{M.N_HAUTS}, vers l'avant, pour éclairer le plan de travail. <b>Façades</b> : tout en tiroirs en bas ; en haut (V13.24), caissons METOD de 80 à deux portes battantes de 40 superposées : porte basse (h {M.HAUT_Z0} → {M.HAUT_JOINT}) pour le quotidien, porte haute (h {M.HAUT_JOINT} → {M.HAUT_Z1}) pour le rare ; les traits épais sont les poignées. <b>Règle à droite</b> (V13.23) : hauteurs de rangement pour la personne qui cuisine (bouton Taille : 1,75 m, 1,80 m ou masquée), le quotidien dans la zone d'or, rien au-dessus de la main levée sans escabeau ; en tireté rouge, coude, épaule, yeux et main levée estimés par les proportions moyennes du corps. {TAILLE_LEG}</p></div>

{section_hauteur_pt()}
<h2>Coupe B-B · mur sud</h2>
<div class="fig"><div class="scroll">{coupe_b()}</div>
<p class="cap">Coupe à y {COUPE_B}, regard vers le sud : l'est est à gauche. <b>Porte d'entrée</b> : baie {f(M.ENTREE["x1"] - M.ENTREE["x0"])} × {M.ENTREE["h"]}, porte à galandage, vantail {f(M.ENTREE["vantail"])} × {M.ENTREE["h"]} (fermé), qui rentre à droite dans le caisson du doublage (poche {f(M.ENTREE["poche"][1] - M.ENTREE["poche"][0])}). Sur le caisson, <b>tableau noir</b> h 120 → 200 et <b>zone aimantée</b> h 70 → 118. Banquette (de profil, contre la fenêtre) et table au fond, devant le bas de mur en chêne et le papier peint Hermione, avec l'étagère P25 au-dessus (h {f(M.ETAGERE_BANQ["z0"])} → {f(M.ETAGERE_BANQ["z1"])}) et l'enceinte audio ; à gauche, la colonne C2 coupée (C1 derrière). À droite, la fenêtre coupée ; au centre, la baie d'entrée et son vantail fermé.</p></div>

<h2>Coupe C-C · mur est</h2>
<div class="fig transp"><div class="tog"><span>Porte du cellier</span><button type="button" class="trbtn" aria-pressed="true">en transparence</button></div>{TAILLE_BTN}<div class="scroll">{regle(coupe_c(), -20, 262)}</div>
<p class="cap">Coupe à x {COUPE_C}, regard vers l'est : le nord est à gauche. Au fond, la cloison du cellier (x 320 → 327), et dans son prolongement la porte du cellier fermée ({M.PORTE_TITRE}), dessinée en transparence (tireté) avec son dormant et son linteau (bouton au-dessus de la coupe : transparente ou normale), pour montrer le fond du cellier : le ballon. Puis, contre le mur du WC (x {f(M.X_MUR_EST)}), les colonnes P{M.P_CAISSON + M.FACADE}, pieds et plinthe {M.SOCLE_COL}, armoires METOD {M.COL_Z1 - M.SOCLE_COL}, dessus à {M.COL_Z1} (les meubles hauts finissent à {M.HAUT_Z1}), fileur de {M.H - M.COL_Z1} jusqu'au plafond : <b>C2</b> réfrigérateur intégrable (niche 178, porte h {M.SOCLE_COL} → {M.FRIGO_Z1}), porte de rangement au-dessus ; <b>C1</b> un tiroir (h {M.SOCLE_COL} → {M.LV_Z0}), lave-vaisselle intégré en hauteur (h {M.LV_Z0} → {M.MO_Z0}), micro-ondes encastrable (niche 38, h {M.MO_Z0} → {M.MO_Z1}), porte de rangement au-dessus ; à droite, le décroché et le mur sud coupé.</p></div>

{section_tango()}
{section_elec()}
{galerie_rendus()}<h2>Matériaux</h2>
<div class="fig">{table_materiaux()}
<p class="cap">Teintes indicatives à l'écran : Canopée et chêne miel d'après le rendu 3D (laque mate Plum Living), parquet d'après la photo de référence. À valider sur échantillons.</p></div>

<h2>Contenu des rangements</h2>
<div class="fig">{table_contenu()}
<p class="cap">Organisation A, tout en tiroirs, électroménager inchangé : tout se voit d'en haut, sans se baisser ni vider l'avant (coulisses plus chères que des charnières). Le contenu est aussi écrit en italique sur les façades, dans les coupes A-A (mur nord), B-B (banquette) et C-C (colonnes). Rangement proche de l'usage : ustensiles, poêles et épices autour de la plaque ; assiettes au-dessus du LV ; couverts, verres et tasses dans C3 (tiroirs à l'anglaise), à côté du frigo.</p></div>

{section_capacite(M.VERSION, lignes_avant_apres(), details_capacite())}
<p class="note">Repère : x vers l'est depuis le mur ouest, y vers le sud depuis le mur nord, z depuis le sol fini, en cm. Source : <span class="mono">3d/v13/modele.py</span> ; plan : <span class="mono">3d/v13/plan.py</span> ; 3D : <span class="mono">3d/v13/cad.py</span>.</p>

<section id="changements">
<h2>Changements</h2>
<table><thead><tr><th>Version</th><th>Date</th><th>Changements</th></tr></thead>
<tbody>{lignes}</tbody></table>
</section>
"""


def page(figees, racine=""):
    """figees : [(version, contenu)] ; le bouton de version bascule tout le contenu (plan, coupes, rangement)."""
    boutons = "".join(f'<button type="button" data-v="{v}">{v} figée</button>' for v, _ in figees)
    blocs = "".join(f'<div class="ver" data-v="{v}" hidden>{c}</div>' for v, c in figees)
    versions = (f'<span>Version</span><button type="button" data-v="courante" aria-pressed="true">'
                f'{M.VERSION} en cours</button>{boutons}') if figees else ""
    barre = (f'<div class="vbar"><a class="back" href="{racine}index.html">← Plans</a>{versions}'
             f'<button type="button" class="expl" aria-pressed="false">Explications</button>'
             f'<button type="button" class="chg" aria-pressed="false">Changements</button></div>')
    return f"""<!doctype html>
<html lang="fr" data-taille="175">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Cuisine V13</title>
<link rel="icon" href="{racine}favicon.svg" type="image/svg+xml">
<link rel="apple-touch-icon" href="{racine}apple-touch-icon.png">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Archivo:wght@400;500;700;800&family=JetBrains+Mono:wght@400;600&display=swap" rel="stylesheet">
<style>{CSS}</style>
</head>
<body>
{barre}
<nav class="toc" aria-label="Sommaire"><button type="button" class="tbtn" aria-expanded="true">Sommaire</button><ol></ol></nav>
<main class="wrap">
<div class="ver" data-v="courante">{contenu()}</div>
{blocs}
</main>
<script>{ANCRES}</script>
<script>
(function () {{
  var bs = document.querySelectorAll(".vbar button[data-v]"), vs = document.querySelectorAll(".ver"), sommaire = function () {{}};
  function montre(v) {{
    if (!document.querySelector('.ver[data-v="' + v + '"]')) v = "courante";
    vs.forEach(function (d) {{ d.hidden = d.dataset.v !== v; }});
    bs.forEach(function (b) {{ b.setAttribute("aria-pressed", b.dataset.v === v); }});
    try {{ localStorage.setItem("cuisine-v13-version", v); }} catch (e) {{}}
    sommaire();
  }}
  bs.forEach(function (b) {{ b.addEventListener("click", function () {{ montre(b.dataset.v); }}); }});
  document.querySelectorAll(".tog .trbtn").forEach(function (b) {{
    b.addEventListener("click", function () {{
      var on = b.getAttribute("aria-pressed") !== "true";
      b.closest(".fig").classList.toggle("transp", on);
      b.setAttribute("aria-pressed", on);
      b.textContent = on ? "en transparence" : "normale";
    }});
  }});
  document.querySelectorAll(".tog button[data-vt]").forEach(function (b) {{
    b.addEventListener("click", function () {{
      var fig = b.closest(".fig");
      if (b.dataset.etats) {{   // porte à trois états : ouverte → mi-ouverte → fermée
        var es = b.dataset.etats.split("|"), ls = b.dataset.libs.split("|"), i = ((+b.dataset.i || 0) + 1) % es.length;
        b.dataset.i = i;
        fig.querySelectorAll('.vt[data-vt="' + b.dataset.vt + '"]').forEach(function (g) {{ g.dataset.etat = es[i]; }});
        b.setAttribute("aria-pressed", es[i] !== "ferme");
        b.textContent = b.textContent.replace(/: .*/, ": " + ls[i]);
        return;
      }}
      var ouvert = b.getAttribute("aria-pressed") !== "true";
      fig.querySelectorAll('.vt[data-vt="' + b.dataset.vt + '"]').forEach(function (g) {{ g.dataset.etat = ouvert ? "ouvert" : "ferme"; }});
      b.setAttribute("aria-pressed", ouvert);
      b.textContent = b.textContent.replace(/: .*/, ": " + (ouvert ? b.dataset.on : b.dataset.off));
    }});
  }});
  document.querySelectorAll(".rtog button[data-rv]").forEach(function (b) {{
    b.addEventListener("click", function () {{
      var g = b.closest(".rgrp");
      g.querySelectorAll(".rtog button").forEach(function (x) {{ x.setAttribute("aria-pressed", x === b); }});
      g.querySelectorAll("figure[data-rv]").forEach(function (f) {{ f.hidden = f.dataset.rv !== b.dataset.rv; }});
    }});
  }});
{TAILLE_JS}
  var be = document.querySelector(".vbar .expl");
  function expl(on) {{
    document.body.classList.toggle("explications", on);
    be.setAttribute("aria-pressed", on);
    try {{ localStorage.setItem("cuisine-v13-expl", on ? "1" : ""); }} catch (e) {{}}
  }}
  be.addEventListener("click", function () {{ expl(be.getAttribute("aria-pressed") !== "true"); }});
  try {{ expl(localStorage.getItem("cuisine-v13-expl") === "1"); }} catch (e) {{ expl(false); }}
  var bc = document.querySelector(".vbar .chg");
  function chg(on) {{
    document.body.classList.toggle("changements", on);
    bc.setAttribute("aria-pressed", on);
    try {{ localStorage.setItem("cuisine-v13-chg", on ? "1" : ""); }} catch (e) {{}}
  }}
  bc.addEventListener("click", function () {{ chg(bc.getAttribute("aria-pressed") !== "true"); }});
  try {{ chg(localStorage.getItem("cuisine-v13-chg") === "1"); }} catch (e) {{ chg(false); }}
  // sommaire (ordinateur) : les titres h2 de la version affichée, repliable, titre courant surligné
  var toc = document.querySelector(".toc"), tol = toc.querySelector("ol"), tb = toc.querySelector(".tbtn"), hs = [];
  function sommaireOuvert(on) {{
    document.body.classList.toggle("toc-on", on);
    tb.setAttribute("aria-expanded", on);
    tb.textContent = on ? "« Sommaire" : "Sommaire »";
    try {{ localStorage.setItem("cuisine-v13-toc", on ? "1" : "0"); }} catch (e) {{}}
  }}
  tb.addEventListener("click", function () {{ sommaireOuvert(!document.body.classList.contains("toc-on")); }});
  try {{ sommaireOuvert(localStorage.getItem("cuisine-v13-toc") !== "0"); }} catch (e) {{ sommaireOuvert(true); }}
  sommaire = function () {{
    var ver = document.querySelector(".ver:not([hidden])");
    hs = ver ? Array.prototype.slice.call(ver.querySelectorAll("h2")) : [];
    tol.innerHTML = "";
    hs.forEach(function (h, i) {{
      if (!h.id) h.id = (ver.dataset.v + "-" + i).replace(/[^a-zA-Z0-9-]/g, "-");
      var c = h.cloneNode(true);
      c.querySelectorAll("a, span").forEach(function (x) {{ x.remove(); }});
      var li = document.createElement("li"), a = document.createElement("a");
      a.href = "#" + h.id; a.textContent = c.textContent.trim();
      a.addEventListener("click", function (e) {{
        e.preventDefault();
        if (h.closest('section[id^="changements"]')) chg(true);
        h.scrollIntoView({{behavior: "smooth"}});
      }});
      li.appendChild(a); tol.appendChild(li);
    }});
    suivre();
  }};
  function suivre() {{
    var vb = document.querySelector(".vbar"), haut = vb.offsetHeight;
    toc.style.top = haut + "px";
    var k = -1;
    hs.forEach(function (h, i) {{ if (h.offsetParent && h.getBoundingClientRect().top < haut + 80) k = i; }});
    tol.querySelectorAll("a").forEach(function (a, i) {{ a.classList.toggle("on", i === k); }});
  }}
  var attente = false;
  window.addEventListener("scroll", function () {{
    if (!attente) {{ attente = true; requestAnimationFrame(function () {{ attente = false; suivre(); }}); }}
  }}, {{passive: true}});
  window.addEventListener("resize", suivre);
  var v0 = "courante";
  try {{ v0 = localStorage.getItem("cuisine-v13-version") || v0; }} catch (e) {{}}
  if (location.hash) v0 = decodeURIComponent(location.hash.slice(1));
  montre(v0);
}})();
</script>
</body>
</html>
"""



FIGEES = os.path.join(os.path.dirname(os.path.abspath(__file__)), "figees")


def figer():
    """Fige la version courante : contenu dans figees/<version>.html (identifiants SVG suffixés pour coexister
    avec la version en cours) et page autonome dans archive/cuisine-<version>.html."""
    os.makedirs(FIGEES, exist_ok=True)
    v = M.VERSION
    # les rendus du moment sont copiés dans cuisine-v13-3d/<version>/ : les rendus suivants ne les écrasent pas
    import shutil
    src3d, dst3d = os.path.join(ROOT, "cuisine-v13-3d"), os.path.join(ROOT, "cuisine-v13-3d", v)
    os.makedirs(dst3d, exist_ok=True)
    for nom in os.listdir(src3d):
        if nom.endswith(".jpg"):
            shutil.copy2(os.path.join(src3d, nom), dst3d)
    rendus = lambda html, racine="": re.sub(r'src="cuisine-v13-3d/(\w+)\.jpg(\?v=[^"]*)?"',
                                             rf'src="{racine}cuisine-v13-3d/{v}/\1.jpg"', html)
    c = rendus(contenu())
    for ident in set(re.findall(r'id="([^"]+)"', c)):
        c = c.replace(f'id="{ident}"', f'id="{ident}-{v}"').replace(f"url(#{ident})", f"url(#{ident}-{v})")
    with open(os.path.join(FIGEES, f"{v}.html"), "w", encoding="utf-8") as fh:
        fh.write(c)
    with open(os.path.join(ROOT, "archive", f"cuisine-{v.lower()}.html"), "w", encoding="utf-8") as fh:
        fh.write(rendus(page([], "../"), "../"))
    print(f"{v} figée")


def lire_figees():
    if not os.path.isdir(FIGEES):
        return []
    r = []
    for nom in sorted(os.listdir(FIGEES), key=lambda n: [int(x) for x in re.findall(r"\d+", n)]):
        if nom.endswith(".html"):
            with open(os.path.join(FIGEES, nom), encoding="utf-8") as fh:
                r.append((nom[:-5], fh.read()))
    return r


if __name__ == "__main__":
    if "--figer" in sys.argv:
        figer()
    with open(OUT, "w", encoding="utf-8") as fh:
        fh.write(page(lire_figees()))
    print(OUT)
    import porte
    porte.ecrire()
