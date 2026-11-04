# Comparatif des quatre meubles bas (meuble actuel V6 + les trois variantes), lu par variantes.py (contrat : TITRE,
# section()). Il ne modifie rien : il lit modele.py et les modules var_*.py, recalcule sur une même base ce qui sert à
# noter (gestes, bouches, levées, basculement, coût) et note les trois critères du client : mettre le linge, retirer le
# linge, complexité à construire.
#
# Bases communes retenues ici (les fiches des variantes n'ont pas toutes la même) :
#   - linge sale : KG_L kg par litre de contenant, pour tous (les fiches prennent 4 ou 5 kg par contenant) ;
#   - basculement : même pivot pour tous (arête avant des semelles des vérins avant), mêmes masses volumiques ;
#   - coût : meuble bas sans le plan de travail, la machine, le tapis ni le caisson haut, échelle sud comprise, boîtes de
#     vis, peinture et chant comptés entiers dès qu'une variante en a besoin.
#
# Cotes en cm, repère de modele.py : x vers l'est (mur du fond à 234), y vers le sud, z depuis le sol.

import math
import os
import sys
from html import escape

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import modele as M  # noqa: E402
import plan as PL  # noqa: E402
import pages as PG  # noqa: E402
import var_pivot as V1  # noqa: E402
import var_tiroirs as V2  # noqa: E402
import var_arceaux as V3  # noqa: E402

ID = "var_comparatif"          # ancre du chapitre (variantes.py lit ID et TITRE)
TITRE = "Comparatif des quatre meubles"
cm, euros = PL.cm, PL.euros
KG_L = 0.12             # kg de linge sale par litre de contenant, tassé à la main (estimé, de mémoire)
NOMS = ("Meuble actuel", "V1 · axe pivotant", "V2 · deux tiroirs", "V3 · arceau ouvert")
ANCRES = ("actuel", V1.ID, V2.ID, V3.ID)

# ------------------------------------------------------------------ masses et basculement (même méthode pour tous)
RHO = dict(bois=450, plan=700, facade=650, bac=650, support=650, barre=600, caisson=650, caisse=650)   # kg/m³, de mémoire
PIVOT = M.XO0 + M.DL / 2 - M.PIED["semelle"] / 2        # arête avant des semelles des vérins avant : 176,5


def _cg(b):
    """Volume (cm³) et centre (x, z) d'une pièce, de son contour dans le plan x-z."""
    p = b.pts("y")
    s = sum(x0 * z1 - x1 * z0 for (x0, z0), (x1, z1) in zip(p, p[1:] + p[:1]))
    cx = sum((x0 + x1) * (x0 * z1 - x1 * z0) for (x0, z0), (x1, z1) in zip(p, p[1:] + p[:1])) / (3 * s)
    cz = sum((z0 + z1) * (x0 * z1 - x1 * z0) for (x0, z0), (x1, z1) in zip(p, p[1:] + p[:1])) / (3 * s)
    return abs(s) / 2 * (b.y1 - b.y0), cx, cz


def _moment(pieces, axe=None, angle=0.0, ref=PIVOT):
    """Masse (kg) et moment (kg·cm, > 0 : retient vers le mur) des pièces, basculées de angle autour de axe."""
    m = mt = 0.0
    for b in pieces:
        if b.role not in RHO:
            continue
        v, x, z = _cg(b)
        if axe:
            x, z = M.bascule(x, z, axe, angle)
        m += RHO[b.role] * v * 1e-6
        mt += RHO[b.role] * v * 1e-6 * (x - ref)
    return m, mt


_pc = {b.nom: b for b in M.PIECES}
L_ACTUEL = [_pc[n] for n in ("bac_porte", "plateau", "contrefiche_n", "contrefiche_s", "support_porte_n",
                             "support_porte_cn", "support_porte_cs", "support_porte_s", "barre_porte_n", "barre_porte_s")]
# équilibre du L actuel à vide, toutes ses pièces comptées (modele.py ne compte que porte, plateau et contrefiches)
EQ_ACTUEL = next(k / 10 for k in range(900) if _moment(L_ACTUEL, M.AXE, k / 10, M.AXE[0])[1] < 0)


def _appui(m_net, x):
    """kg posés au point x (devant le pivot) qui font basculer un meuble dont le moment net est m_net."""
    return m_net / (PIVOT - x)


def _bascule_l(fixes, mobiles, axe, angle, litres, cg_linge, x_haut):
    """L à la butée, les deux sacs pleins dedans : kg posés sur le haut de la porte qui font basculer."""
    mf = _moment([b for b in fixes if b not in mobiles])[1]
    ml = _moment(mobiles, axe, angle)[1]
    ml += 2 * KG_L * litres * (M.bascule(*cg_linge, axe, angle)[0] - PIVOT)
    return _appui(mf + ml, x_haut)


_sac_a = _cg(M.SACS[0])[1:]
_haut_a = M.bascule(M.FACE, M.PORTE_BAC.z1, M.AXE, M.BAC["angle_max"])
_fix_a = [b for b in M.PIECES if b.groupe != "caisson_haut"]
APPUI = {"actuel": _bascule_l(_fix_a, L_ACTUEL, M.AXE, M.BAC["angle_max"], M.VOLUME_BAC, _sac_a, _haut_a[0])}
_haut_1 = M.bascule(M.FACE, V1.Z_HAUT_PORTE, V1.AXE, V1.A_MAX)
APPUI[V1.ID] = _bascule_l(V1.FIXES, V1.MOBILES, V1.AXE, V1.A_MAX, V1.VOLUME_SAC, V1.LINGE_CG, _haut_1[0])


def _v2(ouverts):
    pieces = [b for b in V2.blocs(ouverts, sacs=False) if b not in (M.MACHINE, M.SIPHON, M.ARRIVEE)]
    mt = _moment(pieces)[1]
    for d in V2.TIROIRS.values():
        dx = -V2.COUL["course"] if d["nom"] in ouverts else 0
        mt += KG_L * d["volume"] * ((d["sac"].x0 + d["sac"].x1) / 2 + dx - PIVOT)
    return _appui(mt, M.FACE - V2.COUL["course"])


APPUI[V2.ID] = min(_v2(("haut",)), _v2(("bas",)))
APPUI_V2_DEUX = _v2(("haut", "bas"))
_m3 = _moment(V3.BASE)[1]
_q3 = [(V3.BAC["masse"] + KG_L * V3.BAC["litres"], (a + b) / 2 - V3.COURSE) for a, b in V3.X_CORPS]
_q3 += [(V3.MOBILE_COUL, V3.XC0 + V3.COURSE / 2 - V3.COURSE)]
_q3 += [(V3.TR["e"] * V3.TR["h"] * (V3.YM1 - V3.YM0) * RHO["bois"] * 1e-6, (a + b) / 2 - V3.COURSE) for a, b in V3.X_TR]
APPUI[V3.ID] = _appui(_m3 + sum(w * (x - PIVOT) for w, x in _q3), V3.X_POIGNEE)

# ------------------------------------------------------------------ bouches, levées, contenants
SACS_A = (len(M.SACS), M.VOLUME_BAC)
# levée : de combien monte le contenant plein pour sortir
LEVEE = {
    "actuel": _haut_a[1] - (M._zc + 1),                 # le fond du sac (sur le plateau) passe au-dessus de la porte
    V1.ID: _haut_1[1] - (V1._zc + 1),
    V2.ID: {k: d["zc"][1] - d["sac"].z0 for k, d in V2.TIROIRS.items()},   # le sac passe au-dessus des côtés
    V3.ID: V3.Z_TR1 - V3.Z_FOND,                         # le fond du bac passe au-dessus des traverses
}
Z_BOUCHE_A = M.bascule(M.XO0, M.PORTE_BAC.z1, M.AXE, M.BAC["angle"])[1]
LITRES = {"actuel": [M.VOLUME_BAC] * 2, V1.ID: [V1.VOLUME_SAC] * 2,
          V2.ID: [V2.BAS["volume"], V2.HAUT["volume"]], V3.ID: [V3.BAC["litres"]] * 2}
PLEIN = {k: [KG_L * v for v in l] for k, l in LITRES.items()}
PLEIN[V3.ID] = [p + V3.BAC["masse"] for p in PLEIN[V3.ID]]

# ------------------------------------------------------------------ gestes (comptés ici, pour un contenant)
GESTES_METTRE = {
    "actuel": ["tirer la porte : elle s'arrête seule à 20°", "lâcher le linge dans l'un des deux sacs (la porte se "
               "referme seule)"],
    V1.ID: ["tirer la porte : elle s'arrête seule à 20°", "lâcher le linge dans l'un des deux sacs (le lest referme la "
            "porte)"],
    V2.ID: ["pousser le linge dans le trou de la façade"],
    "V3 avant": ["lâcher le linge par la fente, dans le bac avant"],
    "V3 arrière": ["tirer l'arceau", "lâcher le linge dans le bac arrière", "repousser l'arceau"],
}
GESTES_RETIRER = {
    "actuel": ["ouvrir à 20°", "lever les deux demi-barres arrière (tant qu'une reste, son sac retient la porte)",
               f"accompagner la porte jusqu'à la butée ({M.BAC['angle_max']}°)",
               "sortir le sac par ses deux demi-barres, en le montant sous le chant du plan",
               "remettre le sac vide, la demi-barre de la porte dans sa demi-lune",
               "reposer les deux demi-barres arrière (support et crochet)", "refermer la porte à la main"],
    V2.ID: ["tirer le tiroir à fond", "soulever les deux barres : le sac vient plein",
            "remettre les barres dans leurs quatre entailles", "repousser le tiroir"],
    V3.ID: ["tirer l'arceau à fond", "soulever le bac par ses poignées", "le reposer entre ses traverses",
            "repousser l'arceau"],
}
GESTES_RETIRER[V1.ID] = GESTES_RETIRER["actuel"][:2] + [f"accompagner la porte jusqu'à la butée ({V1.A_MAX}°)"] \
    + GESTES_RETIRER["actuel"][3:]

# ------------------------------------------------------------------ pièces à couper (plan exclu, échelle sud comprise)
_rep = lambda b: getattr(b, "rep", "")  # noqa: E731
PIECES = {
    "actuel": sum(1 for b in M.PIECES if b.groupe != "caisson_haut" and b.rep and b.rep != "D1"),
    V1.ID: V1.FICHE["pieces"],
    V2.ID: V2.N_PIECES + sum(1 for b in V2.ECH_SUD if b.rep),
    V3.ID: sum(1 for b in V3.BASE if _rep(b) and _rep(b) != "D1") + len(V3.X_TR) + 1,      # + traverses + poteau
}

# ------------------------------------------------------------------ coût sur base commune
_W = M.WELDOM
_px = lambda code, n=1: n * _W[code][1]  # noqa: E731
_LOT_G = M.PANNEAUX["G"][0]["prix_lot"]
_REF_PLAN, _REF_TAPIS = M.PANNEAUX["D"][0]["ref"], _W["tapis"][4]
_bas = [(n, ref, q, p) for n, ref, q, p, _ in PG.prix()["lignes"]["bas"] if ref not in (_REF_PLAN, _REF_TAPIS)]
_boites = _px("vis60") + _px("vis40") + _px("vis16")
COUT_ACTUEL = round(sum(q * p for _, _, q, p in _bas) + _boites + _px("chant") + M.TOILE["prix"], 2)
_vis_tole = next(p for n, q, s, p in V1.FICHE["quincaillerie"] if n == V1.VIS_AXE["nom"])
COUT = {
    "actuel": COUT_ACTUEL,
    V1.ID: round(COUT_ACTUEL - _px("charniere_p", M.CHARNIERES["n"]) + V1.TUBE["prix"] + _vis_tole, 2),
    # V2 : sa fiche, plus l'échelle sud (un lot de tasseaux, vérins, inserts, peinture, vis 5 × 60)
    V2.ID: round(V2.COUT + _LOT_G + _px("verin") + _px("insert") + _px("peinture") + _px("vis60"), 2),
    # V3 : l'ossature du meuble actuel sans le L (deux lots de tasseaux : le poteau et les traverses y tiennent), plus
    # sa fiche sans le tasseau compté à part
    V3.ID: round(2 * _LOT_G + _px("verin", 3) + _px("insert", 2) + _px("peinture") + _px("equerre_p", M.RAIL_EQUERRES)
                 + _boites + sum(q * p for _, q, _, p in V3.QUINC), 2),
}

# ------------------------------------------------------------------ notes
# Mettre : 5, − 1 par geste au-delà d'un, − 1 si la bouche fait moins de 15 dans un sens, − 2 si elle est sous 45 du
# sol ; moyenne des deux contenants. Retirer : 5, − 1 par tranche de deux gestes au-delà de quatre, − 1 si le contenant
# plein monte de plus de 40 pour sortir, − 2 s'il faut se baisser (prise sous 45), − 1 si la remise en place demande de
# viser (barres dans des encoches) ; moyenne des deux contenants. Construire : le meuble actuel vaut 3 ; ± 1 par
# grosse difficulté en moins ou en plus.


def _n_mettre(gestes, bouche_min, z_bouche):
    return 5 - (gestes - 1) - (bouche_min < 15) - 2 * (z_bouche < 45)


def _n_retirer(gestes, levee, z_prise, viser):
    return 5 - math.ceil(max(0, gestes - 4) / 2) - (levee > 40) - 2 * (z_prise < 45) - viser


_g = lambda k: len(GESTES_METTRE[k])  # noqa: E731
_r = lambda k: len(GESTES_RETIRER[k])  # noqa: E731
_t2 = V2.TROU
NOTES = {
    "actuel": [_n_mettre(_g("actuel"), M.BAC["largeur_sac"], Z_BOUCHE_A),
               _n_retirer(_r("actuel"), LEVEE["actuel"], M.BAC["barres"][2], 1), 3],
    V1.ID: [_n_mettre(_g(V1.ID), V1._wl, V1.Z_HAUT_20), _n_retirer(_r(V1.ID), LEVEE[V1.ID], V1._zb0, 1), 2],
    V2.ID: [(_n_mettre(1, _t2["h"], V2.HAUT["trou"][0]) + _n_mettre(1, _t2["h"], V2.BAS["trou"][0])) / 2,
            (_n_retirer(_r(V2.ID), LEVEE[V2.ID]["haut"], V2.HAUT["zb"], 1)
             + _n_retirer(_r(V2.ID), LEVEE[V2.ID]["bas"], V2.BAS["zb"], 1)) / 2, 2],
    V3.ID: [(_n_mettre(_g("V3 avant"), V3.FENTE, V3.Z_BORD) + _n_mettre(_g("V3 arrière"), V3._pc, V3.Z_BORD)) / 2,
            _n_retirer(_r(V3.ID), LEVEE[V3.ID], V3.Z_BORD, 0), 4],
}
CLES = ("actuel", V1.ID, V2.ID, V3.ID)
TOTAL = {k: sum(NOTES[k]) for k in CLES}


def _note_t(v):
    return f"{v:g}".replace(".", ",") + "/5"


def _note(v):
    t = f"{v:g}".replace(".", ",")
    return (f'<span class="cmp-n">{t}<small>/5</small></span>'
            f'<span class="cmp-bar" aria-hidden="true"><i style="width:{v * 20:.0f}%"></i></span>')


CSS = """<style>
.cmp-grille td{min-width:150px}.cmp-grille td:first-child{min-width:120px}
.cmp-n{font:700 20px/1 "JetBrains Mono",ui-monospace,monospace;white-space:nowrap}.cmp-n small{font-size:12px;color:var(--muted);font-weight:400}
.cmp-bar{display:block;height:5px;margin:5px 0 6px;background:var(--line);border-radius:3px;max-width:110px}
.cmp-bar i{display:block;height:100%;background:var(--water);border-radius:3px}
.cmp-grille .j{font-size:13px;color:var(--muted)}
.cmp-grille tr.tot td{border-top:2px solid var(--ink);font-weight:700}
.cmp-grille td.top{box-shadow:inset 0 3px var(--water)}
ul.cmp-l{padding-left:20px;max-width:860px}ul.cmp-l li{margin:5px 0}
</style>"""


def _tab(entete, lignes, cls="", largeur=760):
    th = "".join(f"<th>{h}</th>" for h in entete)
    corps = "".join("<tr>" + "".join(f"<td>{c}</td>" for c in l) + "</tr>" for l in lignes)
    return (f'<div class="scroll"><table class="{cls}" style="min-width:{largeur}px"><thead><tr>{th}</tr></thead>'
            f'<tbody>{corps}</tbody></table></div>')


def _li(items):
    return "".join(f"<li>{x}</li>" for x in items)


def section():
    n, a, b2, b3 = NOTES, "actuel", V2.ID, V3.ID
    h2, h3_ = V2.HAUT, V2.BAS
    lv2 = LEVEE[b2]
    mx = [max(NOTES[k][i] for k in CLES) for i in range(3)]

    def cell(k, i, txt):
        top = ' class="top"' if NOTES[k][i] == mx[i] else ""
        return f'<td{top}>{_note(NOTES[k][i])}<div class="j">{txt}</div></td>'

    j_mettre = [
        f"2 gestes : tirer la porte, lâcher. Bouche de chaque sac {cm(M.BAC['largeur_sac'])} × {cm(M.BAC['bouche'])}, "
        f"étroite ; haut de la porte à {cm(Z_BOUCHE_A)} du sol. Porte d'entrée fermée.",
        f"Comme l'actuel : mêmes sacs de {cm(V1._wl)} de large, fente de {cm(V1.OUV)} sous le plan. Le lest assure le "
        "retour de la porte.",
        f"1 geste, rien à ouvrir, mais un trou de {cm(_t2['l'])} × {cm(_t2['h'])} : on pousse le linge. Haut à "
        f"{cm(h2['trou'][0])}–{cm(h2['trou'][1])} (4/5), bas à {cm(h3_['trou'][0])}–{cm(h3_['trou'][1])}, au genou (2/5).",
        f"Bac avant : 1 geste, fente de {cm(V3.YI1 - V3.YI0)} × {cm(V3.FENTE)}, bac de {cm(V3._lc)} × {cm(V3._pc)} "
        f"ouvert à {cm(V3.Z_BORD)} (5/5). Bac arrière : tirer l'arceau, lâcher, repousser (3/5).",
    ]
    j_retirer = [
        f"{_r(a)} gestes ; le sac plein monte d'≈ {cm(LEVEE[a])} pour passer au-dessus de la porte, en biais sous le "
        "chant du plan ; demi-barres à reposer dans la demi-lune et le crochet.",
        f"Les mêmes {_r(V1.ID)} gestes, levée ≈ {cm(LEVEE[V1.ID])} : l'axe ne change rien au vidage.",
        f"{_r(b2)} gestes : tirer, soulever les deux barres (sac levé de {cm(lv2['haut'])}), remettre, pousser. Haut : "
        f"barres à {cm(h2['zb'])} du sol (4/5) ; bas : à {cm(h3_['zb'])}, on se baisse (2/5).",
        f"{_r(b3)} gestes : tirer, soulever le bac rigide par ses poignées, reposer, pousser. Il faut le monter de "
        f"{cm(LEVEE[b3])} pour passer les traverses (bord de {cm(V3.Z_BORD)} à {cm(V3.Z_BORD + LEVEE[b3])}).",
    ]
    j_construire = [
        f"Repère. {PIECES[a]} pièces, deux sacs à soufflet à coudre (le haut des soufflets fixe l'angle d'arrêt), "
        "charnières, butée à placer, demi-lunes, crochet en J, onglets.",
        f"L'actuel ({PIECES[V1.ID]} pièces avec le tube et le lest) plus un axe : deux trous Ø 16 alignés dans les "
        "montants, une rainure à la défonceuse, le tube percé en place. − 1.",
        f"{PIECES[b2]} pièces, dont {sum(1 for b in V2.PIECES if b.rep)} panneaux de mélaminé à couper d'équerre et à "
        "plaquer de chant, deux tiroirs sur coulisses (caisse au mm), deux stades à la scie cloche. Plus de L ni de "
        "butée, sacs simples. + 1 − 2.",
        f"{PIECES[b3]} pièces, dont l'ossature actuelle sans le L : trois traverses (un tasseau refendu), un poteau, "
        "une paire de coulisses, deux bacs achetés. Rien à coudre. Écartement des échelles au mm pour les coulisses. "
        "+ 2 − 1.",
    ]
    lignes = []
    for crit, j, i in (("Mettre le linge", j_mettre, 0), ("Retirer le linge", j_retirer, 1),
                       ("Complexité à construire", j_construire, 2)):
        lignes.append(f"<tr><td><b>{crit}</b></td>" + "".join(cell(k, i, j[c]) for c, k in enumerate(CLES)) + "</tr>")
    tmax = max(TOTAL.values())
    tot = []
    for k in CLES:
        top = ' class="top"' if TOTAL[k] == tmax else ""
        t = f"{TOTAL[k]:g}".replace(".", ",")
        tot.append(f'<td{top}><span class="cmp-n">{t}<small>/15</small></span></td>')
    lignes.append('<tr class="tot"><td>Total, sans pondération</td>' + "".join(tot) + "</tr>")
    th = "".join(f'<th><a href="#{ANCRES[i]}">{escape(NOMS[i])}</a></th>' for i in range(4))
    grille = (f'<div class="scroll"><table class="cmp-grille" style="min-width:780px"><thead><tr><th>Critère</th>{th}'
              f'</tr></thead><tbody>{"".join(lignes)}</tbody></table></div>')

    # chiffres recalculés
    chiffres = _tab(["", *NOMS], [
        ["Bouche", f"2 sacs de {cm(M.BAC['largeur_sac'])} × {cm(M.BAC['bouche'])}, fente de {cm(M.BAC['ouverture'])}",
         f"2 sacs de {cm(V1._wl)} × {cm(V1.BOUCHE)}, fente de {cm(V1.OUV)}",
         f"trou {cm(_t2['l'])} × {cm(_t2['h'])} par tiroir ; sac de {cm(h2['sac'].x1 - h2['sac'].x0)} × "
         f"{cm(h2['sac'].y1 - h2['sac'].y0)} derrière",
         f"fente {cm(V3.YI1 - V3.YI0)} × {cm(V3.FENTE)} ; bac {cm(V3._lc)} × {cm(V3._pc)}"],
        ["Hauteur de la bouche", f"{cm(Z_BOUCHE_A)} (haut de la porte à 20°)", f"{cm(V1.Z_HAUT_20)}",
         f"haut {cm(h2['trou'][0])}–{cm(h2['trou'][1])} ; bas {cm(h3_['trou'][0])}–{cm(h3_['trou'][1])}",
         f"{cm(V3.Z_BORD)} (bord du bac)"],
        ["Gestes pour mettre", f"{_g(a)}", f"{_g(V1.ID)}", "1", f"{_g('V3 avant')} (avant) ; {_g('V3 arrière')} (arrière)"],
        ["Gestes pour retirer", f"{_r(a)}", f"{_r(V1.ID)}", f"{_r(b2)}", f"{_r(b3)}"],
        ["Levée du contenant plein", f"≈ {cm(LEVEE[a])}, sous le chant du plan", f"≈ {cm(LEVEE[V1.ID])}",
         f"{cm(lv2['haut'])} (haut) ; {cm(lv2['bas'])} (bas)", f"{cm(LEVEE[b3])}"],
        ["Contenants", f"2 sacs de {LITRES[a][0]:.0f} L", f"2 sacs de {LITRES[V1.ID][0]:.0f} L",
         f"sacs de {LITRES[b2][0]:.0f} L (bas) et {LITRES[b2][1]:.0f} L (haut)", f"2 bacs de {LITRES[b3][0]} L"],
        ["Poids d'un contenant plein", f"≈ {cm(PLEIN[a][0])} kg", f"≈ {cm(PLEIN[V1.ID][0])} kg",
         f"≈ {cm(PLEIN[b2][0])} à {cm(PLEIN[b2][1])} kg", f"≈ {cm(PLEIN[b3][0])} kg, bac compris"],
        ["Pièces à couper", f"{PIECES[a]}", f"{PIECES[V1.ID]}", f"{PIECES[b2]}", f"{PIECES[b3]}"],
        ["À coudre", "2 sacs à soufflet", "2 sacs à soufflet", "2 sacs simples", "rien"],
        ["Mécanisme acheté", f"{M.CHARNIERES['n']} charnières plates", "tube alu Ø 16 et 3 vis à tôle",
         "2 paires de coulisses de 500", "1 paire de coulisses de 550, 2 bacs HÅLLBAR"],
        ["Outils en plus de l'actuel", "—", "défonceuse et fraise Ø 10, mèche plate Ø 16, scie à métaux",
         "scie cloche Ø 100, scie sauteuse, fer à repasser", "scie circulaire pour la refente ; pas de machine à coudre"],
    ], largeur=820)

    # à côté des notes
    porte = M.FACE - M.PORTE["x1"]
    info = _tab(["", *NOMS], [
        ["Coût, base commune", euros(COUT[a]), euros(COUT[V1.ID]), euros(COUT[b2]), euros(COUT[b3])],
        ["Écart avec l'actuel", "—"] + [f'{"+" if COUT[k] >= COUT[a] else "−"} {euros(abs(COUT[k] - COUT[a]))}'
                                        for k in CLES[1:]],
        ["Basculement (sans fixation murale)",
         f"≈ {APPUI[a]:.0f} kg posés sur le haut de la porte à la butée, sacs pleins",
         f"≈ {APPUI[V1.ID]:.0f} kg, idem",
         f"≈ {APPUI[b2]:.0f} kg au bord d'un tiroir plein tiré ; ≈ {APPUI_V2_DEUX:.0f} kg si les deux sont tirés",
         f"≈ {APPUI[b3]:.1f} kg sur l'arceau sorti sans le poteau de niche ; avec, il tient (le caisson haut, chevillé, "
         "reprend l'effort)".replace(".", ",")],
        ["Porte d'entrée", f"fermée pour mettre et pour retirer : à 20°, le haut de la porte avance de "
         f"{cm(M.BAC['avancee'])}, le vantail tourne à {cm(porte)} du nu",
         f"pareil (avance de {cm(V1.AVANCE)})",
         f"mettre : libre, sauf grand ouverte (le vantail masque les trous à {cm(porte)}) ; retirer : fermée",
         f"pareil que V2 (le vantail grand ouvert masque aussi la fente)"],
        ["Autres risques", "porte qui claque, sacs pleins ; sacs étroits à viser",
         "sapin qui gonfle : l'axe serre ; vis dans un tube de 1 mm",
         "chants du mélaminé près du sol ; linge visible par le trou ; bas qui frotte sous la caisse du haut",
         f"meuble ouvert, bacs visibles ; lèvre du bac estimée ({cm(V3.APPUI * 10)} mm d'appui sur chaque traverse) ; "
         "prix du bac relevé en Belgique, coulisse de 550 non relevée"],
    ], largeur=860)

    return f"""{CSS}
<p>Les quatre meubles notés sur les trois critères du client, de 1 à 5, avec les chiffres refaits ici depuis le code (et non repris des fiches des variantes, qui n'ont pas la même base). À côté, sans note : le coût, la stabilité et les risques. Base commune : le linge pèse {PL.virg(KG_L, 2)} kg par litre de contenant, le basculement se compte sur l'avant des vérins avec les mêmes masses pour tous, le coût est celui du meuble bas sans le plan, la machine, le tapis ni le caisson haut.</p>

<h3 id="cmp-grille">La grille</h3>
{grille}
<p class="note">Liseré bleu : la meilleure note du critère. Pour V2 et V3, la note est la moyenne des deux contenants (tiroir du haut et du bas, bac avant et arrière), détaillée dans la case.</p>

<h3 id="cmp-notes">Comment je note</h3>
<ul class="cmp-l">
<li><b>Mettre le linge</b>, pour un contenant : on part de 5 ; − 1 par geste au-delà du premier (ouvrir, refermer à la main) ; − 1 si la bouche fait moins de 15 dans un sens ; − 2 si elle est sous 45 du sol (on se baisse). Une porte qui se referme seule ne compte pas.</li>
<li><b>Retirer le linge</b>, pour un contenant, de fermé à remis en place vide : on part de 5 ; − 1 par tranche de deux gestes au-delà de quatre (tirer, sortir, remettre, refermer) ; − 1 si le contenant plein doit monter de plus de 40 pour sortir ; − 2 s'il faut se baisser (prise sous 45) ; − 1 si la remise en place demande de viser (barres dans des encoches, crochet). Vider dans la machine est le même partout, non compté.</li>
<li><b>Complexité à construire</b> : le meuble actuel vaut 3 (sa notice est écrite et le client l'a accepté). + 1 par grosse difficulté en moins, − 1 par grosse difficulté en plus : couture des sacs, réglage au mm d'un mécanisme, panneaux à couper d'équerre en nombre, outil à sortir ou à acheter.</li>
</ul>

<h3 id="cmp-chiffres">Les chiffres</h3>
{chiffres}
<p class="note">Gestes comptés ici, pour un contenant. Retirer, meuble actuel : {escape(" ; ".join(GESTES_RETIRER[a]))}. V2 : {escape(" ; ".join(GESTES_RETIRER[b2]))}. V3 : {escape(" ; ".join(GESTES_RETIRER[b3]))}. Pièces : plan exclu, échelle sud comprise. Poids : {PL.virg(KG_L, 2)} kg de linge par litre (estimé, de mémoire).</p>

<h3 id="cmp-info">À côté des notes</h3>
{info}
<p class="note">Coût : prix des fiches et du document V4 (Weldom, Marseille Textiles, IKEA, Leroy Merlin) ; boîtes de vis, peinture et chant comptés entiers dès qu'un meuble en a besoin. Actuel : la liste d'achats du meuble bas sans plan ni tapis, plus vis, un rouleau de chant et la toile. V1 : l'actuel sans charnières, avec tube et vis. V2 : sa fiche plus l'échelle sud (un lot de tasseaux, vérins, inserts, peinture, vis 5 × 60). V3 : l'ossature actuelle sans le L (deux lots de tasseaux suffisent, poteau et traverses compris), plus sa fiche. Coulisses de V2 et V3 et bacs de V3 : prix estimés ou relevés hors de France. Basculement : masses de mémoire (sapin 450, chêne 700, mélaminé 650 kg/m³), coins de calage et joint silicone non comptés.</p>

<h3 id="cmp-synthese">Synthèse</h3>
<ul class="cmp-l">
<li><b>Mettre le linge : V3</b>, grâce au bac avant ouvert sous une large fente, à hauteur de taille. Les trois autres font jeu égal pour des raisons opposées : le L a deux gestes et des sacs étroits, V2 n'a qu'un geste mais un trou de {cm(_t2['h'])} de haut, dont un au genou.</li>
<li><b>Retirer le linge : V3</b>, puis V2. Le L (actuel et V1) est le plus pénible : {_r(a)} gestes, un sac à monter d'≈ {cm(LEVEE[a])} sous le plan, deux demi-barres à reposer. V1 ne change pas cela : elle répond au reproche fait à la charnière, pas aux trois critères.</li>
<li><b>Construire : V3</b>, la seule sans couture et sans mélaminé ; le meuble actuel ensuite ; V1 et V2 sont les plus exigeantes (axe aligné, tiroirs au mm).</li>
<li><b>Le compromis.</b> V3 l'emporte sur les trois critères, mais c'est un meuble ouvert, bacs visibles, et il ne tient arceau sorti que grâce au poteau de niche : sans lui, ≈ {cm(APPUI[b3])} kg posés sur l'arceau le font basculer. Le meuble bas s'appuie alors sur le caisson haut chevillé. Si une façade fermée compte, V2 vide mieux que le L ({_note_t(NOTES[b2][1])} contre {_note_t(NOTES[a][1])}) mais coûte ≈ {COUT[b2] - COUT[a]:.0f} € de plus, se construit moins facilement et bascule avec ≈ {APPUI_V2_DEUX:.0f} kg si l'on tire les deux tiroirs pleins.</li>
</ul>
<p><b>À trancher</b> : un meuble ouvert est-il acceptable ? le poteau de niche aussi (il vaudrait pour les quatre : le meuble actuel bascule avec ≈ {APPUI[a]:.0f} kg posés sur sa porte ouverte en grand) ? deux contenants pour trier, ou un seul rempli au quotidien (alors le bac arrière de V3 compte peu) ? <b>À mesurer</b> : la lèvre et les cotes du HÅLLBAR en magasin, et son prix en France ; l'écartement réel des échelles nord et du milieu à 60 du sol (les coulisses demandent le mm) ; le côté d'ouverture du hublot, qui peut gêner les quatre.</p>

<h3 id="cmp-ecarts">Écarts relevés dans les fiches</h3>
<ul class="cmp-l">
<li>Les coûts des fiches n'ont pas la même base : V1 compte tout le meuble bas hors plan ; V2 laisse de côté l'échelle sud ; V3 toute l'ossature. Ramenés ici à une base commune. Le linge pèse 4 kg par contenant dans V1 et V3, 5 kg dans V2 ; ici {PL.virg(KG_L, 2)} kg par litre pour tous.</li>
<li>V1 : la bouche de sa fiche ({cm(V1.FICHE['bouche']['largeur'])} de large) est la largeur du plateau ; on jette en fait dans deux sacs de {cm(V1._wl)}, comme aujourd'hui.</li>
<li>V3 : « pas de conflit » avec la porte d'entrée arceau rentré : vrai pour le choc, mais le vantail grand ouvert passe à {cm(porte)} du nu et masque la fente, comme pour V2. « Soulever le bac tout droit » : il monte de {cm(LEVEE[b3])} avant que son fond passe les traverses (la vue le montre soulevé de {V3.LEVE}, encore engagé).</li>
<li>V2 : le basculement est compté sur les vérins de l'échelle sud ({cm(PIVOT)}), un peu en avant de ceux du caisson ({cm(V2.CX0 + 3 - M.PIED['semelle'] / 2)}) : résultat un peu optimiste.</li>
<li>Meuble actuel : l'équilibre du L ({cm(M.BAC['equilibre'])}° dans le modèle) ne compte que la porte, le plateau et les contrefiches. Avec les quatre supports et les deux demi-barres de la porte, il tombe à {cm(EQ_ACTUEL)}° (V1 trouve la même chose) : à vide, la porte ouverte à {M.BAC['angle']}° se referme seule de justesse. Sans effet sur les notes.</li>
</ul>"""


if __name__ == "__main__":
    for k in CLES:
        print(k, NOTES[k], TOTAL[k], COUT[k], f"appui {APPUI[k]:.2f}", LEVEE[k], PIECES[k])
    print("V2 deux tiroirs", APPUI_V2_DEUX, "équilibre actuel", EQ_ACTUEL)
