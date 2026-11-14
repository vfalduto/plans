"""Vue Explication de la cuisine/aménagement : chapô et liens, cartes « Principe », hauteur du plan de travail, porte
du cellier Tango, électricité, rendus, matériaux, contenu des rangements, capacité, repère.

Textes et tableaux repris de l'ancien générateur 3d/v13/plan.py (`section_hauteur_pt`, `section_tango`, `tables_elec`,
`table_materiaux`, `table_contenu`, `section_capacite`), calculés depuis le modèle, avec ces écarts seulement : virgule
à la place du point médian, plus de chasse fixe (`mono`), légende sous un tableau en `<p class="remarque">`, légende
d'un dessin en texte alternatif, chaque tableau dans un `<div class="defile">`. L'ancien générateur est supprimé
depuis la bascule.
"""
import re
from html import escape, unescape
from pathlib import Path

from commun.blocs import figure_rendu, materiaux, note_source, principes, rendu, tete
from pieces.cuisine import modele as M
from pieces.cuisine.dessin import aire, f, fiche_tango, sources_tango, virg
from pieces.cuisine.amenagement import legende
from pieces.cuisine.amenagement.dessins import hauteur_pt_svg, minus

DEPUIS = "cuisine/amenagement/"
CHAPO = ("Nouveau départ depuis la pièce vide. Le plan et la coupe sont générés depuis le modèle 3D : une seule source, "
         "aucune cote reportée à la main.")
REPERE = ("Repère : x vers l'est depuis le mur ouest, y vers le sud depuis le mur nord, z depuis le sol fini, en cm. "
          "Dimensions : pieces/cuisine/modele.py.")


def _racine(depuis: str) -> str:
    """Chemin relatif de `depuis` (« cuisine/amenagement/ ») vers la racine du site."""
    return "../" * depuis.count("/")


def _liens(depuis: str) -> tuple[tuple[str, str], ...]:
    """Liens de la tête : les deux annexes du document (écrites à côté de lui), puis la page de la porte du cellier."""
    return (("maquette-3d.html", "Maquette 3D"), ("imprimable.html", "Version imprimable"),
            (f"{_racine(depuis)}cuisine-v13-porte-cellier.html", "Porte du cellier"))


LIENS = _liens(DEPUIS)


def _texte(fragment: str) -> str:
    return re.sub(r"\s+", " ", unescape(re.sub(r"<[^>]+>", "", fragment))).strip()


def _defile(table: str) -> str:
    return f'<div class="defile">{table}</div>'


# ------------------------------------------------------------------ calculs
def hors_fourchette(h, coude, regle=None):
    """Écart (cm) entre le plan h et la fourchette coude − hi → coude − lo ; > 0 trop haut, < 0 trop bas, 0 dedans."""
    lo_s, hi_s = regle or M.PT_SOUS_COUDE
    lo, hi = coude - hi_s, coude - lo_s
    return h - hi if h > hi else (h - lo if h < lo else 0)


def etat(e):
    return "oui" if e == 0 else (f"{e} trop haut" if e > 0 else f"{-e} trop bas")


# mesures du tableau de capacité : (libellé, clé, diviseur, format)
LIGNES_CAPACITE = [
    ("Meubles bas (m linéaires)", "lin_bas", 100, "{:.2f} m"), ("Meubles hauts (m linéaires)", "lin_hauts", 100, "{:.2f} m"),
    ("Colonnes (m linéaires)", "lin_col", 100, "{:.2f} m"), ("Nombre de meubles", "modules", 1, "{:.0f}"),
    ("Tiroirs à sortie totale", "tiroirs", 1, "{:.0f}"), ("Tiroirs à l'anglaise (derrière une porte)", "anglaise", 1, "{:.0f}"),
    ("Plan de travail utile", "plan", 100, "{:.2f} m"), ("Plus grand plan d'un seul tenant", "plan_max", 1, "{:.0f} cm"),
    ("Cellier : surface au sol", "cellier_m2", 1, "{:.2f} m²"), ("Cellier : tablettes", "tablettes", 100, "{:.2f} m"),
    ("Volume fermé de la cuisine", "vol_cuisine", 1, "{:.0f} L"), ("Volume du cellier (rayonnages)", "vol_cellier", 1, "{:.0f} L")]


def _fr(t):
    return re.sub(r"(\d)\.(\d)", r"\1,\2", t)


def lignes_avant_apres():
    """Mesures V11.34 (avant) et version en cours : [(mesure, avant, en cours, écart)], textes à la française."""
    a, v = M.AVANT, M.CAPACITE["v11"]
    lib = lambda x: sum(b - c for c, b in x)
    apres = dict(lin_bas=v["lin_bas"], lin_hauts=v["lin_hauts"], lin_col=v["lin_col"], modules=sum(v["modules"]),
                 tiroirs=v["tiroirs"], anglaise=len(M.TIROIRS_ANGLAISE), plan=lib(v["plan"]),
                 plan_max=max(b - c for c, b in v["plan"]), cellier_m2=aire(M.CELLIER_SOL) / 1e4,
                 tablettes=v["cellier"][1] * v["cellier"][2] + (v["cellier_sud"][1] * v["cellier_sud"][2] if v["cellier_sud"] else 0),
                 vol_cuisine=M.VOLUMES["v11"]["cuisine"], vol_cellier=M.VOLUMES["v11"]["cellier"])
    avant = dict(lin_bas=a["lin_bas"], lin_hauts=a["lin_hauts"], lin_col=a["lin_col"], modules=sum(a["modules"]),
                 tiroirs=a["tiroirs"], anglaise=a["anglaise"], plan=lib(a["plan"]),
                 plan_max=max(b - c for c, b in a["plan"]), cellier_m2=a["cellier_m2"], tablettes=a["tablettes_cm"],
                 vol_cuisine=a["volume_cuisine"], vol_cellier=a["volume_cellier"])
    rows = []
    for nom, k, div, fmt in LIGNES_CAPACITE:
        x, y = avant[k] / div, apres[k] / div
        d = y - x
        signe = "+" if d > 0 else "−" if d < 0 else "±"
        rows.append((nom, _fr(fmt.format(x)), _fr(fmt.format(y)), _fr(signe + fmt.format(abs(d)))))
    tot_a, tot_v = (avant["vol_cuisine"] + avant["vol_cellier"]) / 1000, (apres["vol_cuisine"] + apres["vol_cellier"]) / 1000
    rows.append(("Volume total", _fr(f"{tot_a:.2f} m³"), _fr(f"{tot_v:.2f} m³"),
                 _fr(f"{'+' if tot_v >= tot_a else '−'}{abs(tot_v - tot_a):.2f} m³")))
    return rows


def colonne_p9a():
    """Proposition 9 A (figée, ne change plus) et repères d'une cuisine de 8 m², dans l'ordre de LIGNES_CAPACITE + total."""
    p, r, vol = M.CAPACITE["p9a"], M.REPERES, M.VOLUMES["p9a"]
    segs = [b - a for a, b in p["plan"]]
    p9a = [f"{p['lin_bas'] / 100:.2f} m (dont le café)", f"{p['lin_hauts'] / 100:.2f} m", f"{p['lin_col'] / 100:.2f} m (LV, frigo, four)",
           f"{sum(p['modules'])}", f"{p['tiroirs']}", "0", f"{sum(segs) / 100:.2f} m ({' + '.join(f(x) for x in segs)})",
           f"{max(segs)} cm", "", f"{p['cellier'][1] * p['cellier'][2] / 100:.2f} m",
           f"{vol['cuisine']:.0f} L", f"{vol['cellier']:.0f} L", f"{sum(vol.values()) / 1000:.2f} m³"]
    rep = ["", "", "", f"{r['modules'][0]} à {r['modules'][1]}",
           "plus il y en a, mieux c'est", "", f"{r['plan'][0] / 100:g} à {r['plan'][1] / 100:g} m", "", "", "", "", "",
           f"{r['volume'][0]:g} à {r['volume'][1]:g} m³ (bien optimisée)"]
    return [_fr(x) for x in p9a], [_fr(x) for x in rep]


def details_capacite():
    """Lignes descriptives de la version en cours : implantation, rayonnages du cellier, rangements ouverts."""
    v = M.CAPACITE["v11"]
    n, s = v["cellier"], v["cellier_sud"]
    return dict(
        implantation=f"{max(b.x1 for b in M.MEUBLES if b.role == 'plan') / 100:.2f} m, "
                     f"{v['modules'][0] + v['modules'][1]} meubles".replace(".", ","),
        rayonnages=(f"nord {n[0]} cm, {n[1]} tablettes P{n[3]} de {n[2]}"
                    + (f" ; sud (mur du WC) {s[0]} cm, {s[1]} tablettes P{s[3]} de {s[2]}" if s else "")),
        ouverts=escape(v["autres"]))


def nombre(t):
    """Premier nombre d'un texte à la française (« 2,60 m » → 2.6), None s'il n'y en a pas."""
    m = re.search(r"\d+(?:,\d+)?", re.sub(r"<[^>]+>", "", t))
    return float(m.group().replace(",", ".")) if m else None


def note(t, lo, hi=None):
    """Classe de cellule : « ok » à partir du bas du repère, « ko » en dessous (dépasser le haut n'est pas une erreur)."""
    x = nombre(t)
    if x is None:
        return ""
    return ' class="ok"' if lo <= x else ' class="ko"'


def corps_capacite(rows, details):
    """Lignes du tableau de capacité : V11.34 (avant), version affichée, écart, proposition 9 A et repères. Cellules
    vertes (`ok`) dans le repère d'une cuisine de 8 m², rouges (`ko`) en dessous."""
    p9a, rep = colonne_p9a()
    r = M.REPERES
    lignes = [list(x) + [p9a[k], rep[k], None] for k, x in enumerate(rows)]
    # bas + hauts : c'est la somme qui a un repère
    som = lambda i: f"{nombre(lignes[0][i]) + nombre(lignes[1][i]):.2f} m".replace(".", ",")
    d = nombre(lignes[0][2]) + nombre(lignes[1][2]) - nombre(lignes[0][1]) - nombre(lignes[1][1])
    signe = "+" if d > 0.001 else "−" if d < -0.001 else "±"
    lignes.insert(2, ["Meubles bas + hauts", som(1), som(2), f"{signe}{abs(d):.2f} m".replace(".", ","), som(4),
                      f"{r['lin'][0] / 100:g} à {r['lin'][1] / 100:g} m", (r["lin"][0] / 100, r["lin"][1] / 100)])
    regles = {"Nombre de meubles": r["modules"], "Plan de travail utile": (r["plan"][0] / 100, r["plan"][1] / 100),
              "Volume total": (r["volume"][0], None)}
    corps = ""
    for k, (nom, av, ap, ec, p9, rp, regle) in enumerate(lignes):
        regle = regle or regles.get(nom)
        c = (lambda t: note(t, *regle)) if regle else (lambda t: "")
        gras = "<b>" + nom + "</b>" if k == len(lignes) - 1 else nom
        corps += (f"<tr><td>{gras}</td><td{c(av)}>{av}</td><td{c(ap)}><b>{ap}</b></td><td>{ec}</td>"
                  f"<td{c(p9)}>{p9}</td><td>{rp}</td></tr>")
    p, (i0, i1, n0, n1) = M.CAPACITE["p9a"], r["implantation"]

    def impl(t):   # au moins 2,50 m et 6 meubles (au-delà du repère : pas une erreur)
        n = re.search(r"(\d+) meubles", t)
        ok = i0 / 100 <= nombre(t) and n and n0 <= int(n.group(1))
        return ' class="ok"' if ok else ' class="ko"'
    p9_impl = "2,49 m, 7 meubles + colonne LV"
    corps += "".join(f'<tr><td>{nom}</td><td></td><td colspan="2"{cx}>{x}</td><td{cy}>{y}</td><td>{z}</td></tr>'
                     for nom, x, cx, y, cy, z in [
        ("Implantation (mur nord)", details["implantation"], impl(details["implantation"]), p9_impl, impl(p9_impl),
         f"{i0 / 100:.2f} à {i1 / 100:g} m, ".replace(".", ",") + f"{n0} ou {n1} meubles"),
        ("Cellier : rayonnages", details["rayonnages"], "",
         f"{p['cellier'][0]} cm, {p['cellier'][1]} tablettes P{p['cellier'][3]} de {p['cellier'][2]}", "", ""),
        ("Rangements ouverts", details["ouverts"], "", escape(p["autres"]), "", "")])
    return corps


# ------------------------------------------------------------------ hauteur du plan de travail (V13.28)
def _legende_hauteur_pt():
    vi, vc = M.COUDES["Vincent"], M.COUDES["Victor"]
    (ll, lh), (al, ah) = M.HSE_LEGER, M.HSE_APPUI
    return (f"Coudes mesurés debout, du sol au dessous du coude, avant-bras plié à 90° : Vincent {vi}, Victor {vc} "
            f"({vc - vi} d'écart). <b>Bande verte</b> : règle des cuisinistes, plan 10 à 15 sous le coude. <b>Barres "
            f"fines</b> de part et d'autre (ergonomie du travail debout, HSE / <i>Bodyspace</i>) : à gauche, tâches avec "
            f"appui (couper du dur, pétrir, presser), {al} à {ah} sous le coude ; à droite, gestes légers et précis "
            f"(éplucher, garnir), {ll} à {lh} sous le coude. <b>Trait ocre</b> : plaque idéale, 20 sous le coude "
            f"(Siemens). Tireté rouge : coude. Traits horizontaux : hauteurs candidates (plein : actuelle {M.PT_Z1} ; "
            f"bleu : conseillée {M.PT_RECO}).")


def _hauteur_pt():
    noms = list(M.COUDES)
    ent = "".join(f"<th>{n} (coude {M.COUDES[n]})</th>" for n in noms)
    lignes = []
    for h, _, comment in M.PT_CANDIDATS:
        cells = []
        for n in noms:
            c = M.COUDES[n]
            e, el, ea = (hors_fourchette(h, c, r) for r in (M.PT_SOUS_COUDE, M.HSE_LEGER, M.HSE_APPUI))
            cells.append(f'<td>coude − {c - h}<br>cuisinistes : {etat(e)}<br>'
                         f'<span class="note">léger : {etat(el)}, appui : {etat(ea)}</span></td>')
        tot = sum(abs(hors_fourchette(h, M.COUDES[n])) for n in noms)
        rec = ' class="hpr"' if h == M.PT_RECO else ""
        lignes.append(f'<tr{rec}><td><b>{h}</b>{" (actuel)" if h == M.PT_Z1 else ""}</td>{"".join(cells)}'
                      f'<td>{tot}</td><td>{M.HAUT_Z0 - h}</td><td>{escape(comment)}</td></tr>')
    vi, vc = M.COUDES["Vincent"], M.COUDES["Victor"]
    (ll, lh), (al, ah) = M.HSE_LEGER, M.HSE_APPUI
    r = M.PT_RECO
    table = (f"<table><thead><tr><th>Plan</th>{ent}<th>Hors fourchette cuisinistes (total)</th><th>Plan → hauts</th>"
             f"<th>Comment l'obtenir (caisson METOD 80 + plan 4)</th></tr></thead><tbody>{''.join(lignes)}</tbody></table>")
    return f"""<h2>Hauteur du plan de travail (étude)</h2>
<p class="remarque"><b>Étude seulement</b> : rien n'est appliqué au plan, le plan de travail reste à {M.PT_Z1} dans le modèle, les coupes et les rendus.</p>
<div class="defile hpw">{hauteur_pt_svg(_texte(_legende_hauteur_pt()))}</div>
{_defile(table)}
<p><b>Ce que disent les sources.</b> Tout le monde part du coude, mais pas avec le même écart. Les cuisinistes (Bora, Neff, guides allemands) disent 10 à 15 sous le coude ; la table de Neff donne coude 107 → plan 92, coude 114 → 99, coude 125 → 110. Les références d'ergonomie du travail debout (HSE, Pheasant et Haslegrave, <i>Bodyspace</i> ; NIOSH d'après Grandjean) distinguent la tâche : gestes légers {ll} à {lh} sous le coude, tâches avec appui {al} à {ah} sous le coude, travail de précision au-dessus du coude. La règle des cuisinistes (10 à 15) est un compromis entre les deux, pour une cuisine où l'on fait de tout.</p>
<p><b>Ce que ça change pour vous deux.</b> Avec la règle des cuisinistes, les fourchettes ne se recouvrent pas (Vincent {vi - 15} → {vi - 10}, Victor {vc - 15} → {vc - 10}). Avec la règle par tâche, elles se recouvrent : de {vi - lh} à {vi - ll}, le plan est « léger » pour Vincent et « appui » pour Victor, donc correct pour les deux, à condition que Victor fasse surtout la découpe et la pâte, et Vincent les gestes fins. Le plan conseillé, <b>{r}</b>, est au milieu de ce recouvrement et partage l'écart à la règle des cuisinistes : 2 de trop pour Vincent, 2 de trop peu pour Victor.</p>
<p><b>Trop haut ou trop bas ?</b> Une étude sur onze cuisines de cantine a trouvé le plan de découpe trop haut pour un tiers des cuisiniers, d'après leur coude ; les douleurs de nuque et d'épaule y étaient plus fréquentes chez les plus petits. Un plan trop haut fait lever les épaules ; un plan trop bas fait pencher le dos. Les deux fatiguent ; on compense facilement un plan trop bas (planche épaisse de 4 à 5 pour le plus grand), pas un plan trop haut.</p>
<p><b>Évier : il pousse vers le haut.</b> Neff mesure l'évier au <i>fond du bac</i> : c'est lui qui doit être à la hauteur de travail (coude − 15), et le bord peut monter jusqu'à 15 au-dessus. Avec un bac d'environ 18 à 20 de profondeur (à vérifier sur le modèle), le fond est à ≈ {r - 19} pour un plan à {r} : {vi - 15 - (r - 19)} sous la hauteur de travail de Vincent ({vi - 15}), {vc - 15 - (r - 19)} sous celle de Victor ({vc - 15}). Aucun plan standard ne met le fond du bac à la bonne hauteur : la vaisselle est le poste où l'on se penche le plus, Victor surtout, et chaque centimètre gagné sur le plan y compte. À {M.PT_Z1}, le fond serait à ≈ {M.PT_Z1 - 19}. Un bac moins profond, ou un égouttoir / bassine posé dans le bac pour la vaisselle à la main, réduit l'écart.</p>
<p><b>Plaque : elle pousse vers le bas.</b> Le bord de la casserole donne la hauteur de travail : Neff conseille la plaque 15 sous le plan, Siemens 20 sous le coude (Vincent {vi - M.PLAQUE_SOUS_COUDE}, Victor {vc - M.PLAQUE_SOUS_COUDE}) ; certains guides allemands la mettent au contraire au même niveau que l'évier, 10 sous le coude. Pas de consensus. Sur un plan continu, la plaque est à la hauteur du plan : à {r}, haute pour Vincent dans une grande casserole, correcte pour Victor.</p>
<p><b>Couples de tailles différentes.</b> Les designers proposent trois réponses : choisir la hauteur de celui qui cuisine le plus, faire des zones à deux hauteurs (souvent un îlot plus haut que le linéaire), ou un plan réglable. Ici, sans îlot, une zone à deux hauteurs voudrait dire un ressaut dans le plan du mur nord, par exemple l'évier (B{M.B_EVIER}) et B{M.B_ETROIT} plus hauts que la plaque et les tiroirs (B1 → B{M.B_TIROIRS_2}) ; c'est faisable avec des pieds différents mais cela casse la ligne du plan, de la crédence et des façades.</p>
<p><b>Avant de décider : essayer.</b> Comme pour l'implantation (V13.17), un essai grandeur nature tranche mieux que les règles : un plateau posé sur des cales à 92, 96 puis 98, et chacun y coupe des légumes, y pétrit, y tient une casserole pendant quelques minutes.</p>
<p><b>Conséquences d'un plan plus haut.</b> Les colonnes C1 et C2 sont sur les mêmes pieds : elles montent d'autant (dessus {M.COL_Z1} + Δ, fileur au-dessus réduit). Les meubles hauts restent à h {M.HAUT_Z0} : l'espace plan → hauts diminue (colonne « Plan → hauts ») ; vérifier la distance minimale plaque → hotte imposée par la notice de la hotte intégrée dans H1. Au-delà de 94, la plinthe IKEA de 8 ne suffit plus : plinthe sur mesure (même façade). Four sous la plaque et lave-vaisselle en hauteur dans C1 : non concernés.</p>
<p class="remarque">Sources. Règle des cuisinistes : <a href="https://www.bora.com/fr-fr/guide/la-cuisine-ergonomique-lignes-directrices-conseils">Bora</a> ; <a href="https://neff-home.com/fr/decouvrez-neff/conseils-pour-amenager-votre-cuisine/etapes/ergonomie">Neff</a> (plan, plaque, évier) et sa <a href="https://www.neff-home.com/de/neff-entdecken/kuechenplanung/schritte/ergonomie">table coude → plan</a> ; <a href="https://www.hausjournal.net/hoehe-kuechenarbeitsflaeche">Hausjournal</a> (évier et plaque 10 sous le coude) ; <a href="https://www.siemens-home.bsh-group.com/fr/inspiration-siemens/design/votre-projet-cuisine/table-de-cuisson">Siemens</a> (plaque 20 sous le coude). Ergonomie du travail debout : <a href="https://www.hse.gov.uk/MSD/uld/art/posture.htm">HSE</a> ; <a href="https://www.msdprevention.com/resource-library/standing-workstation-height-manual-tasks">CRE-MSD</a> ; <a href="https://webarchive.library.unt.edu/eot2008/20080923002046/http://www.cdc.gov/niosh/pdfs/97-117-f.pdf">NIOSH, <i>Elements of Ergonomics Programs</i></a> (d'après Grandjean). Étude en cantine : <a href="https://pubmed.ncbi.nlm.nih.gov/15676673/">PubMed 15676673</a> (résumé seul). Couples : <a href="https://www.livingetc.com/advice/should-a-kitchen-island-be-the-same-height-as-the-counters">Livingetc</a>, <a href="https://www.homesandgardens.com/kitchens/should-a-kitchen-island-be-the-same-height-as-the-counters">Homes &amp; Gardens</a>. Pieds METOD (≈ 7 → 10,5, chiffre de forum, non confirmé par IKEA) : <a href="https://www.forumconstruire.com/construire/topic-407503-remplacer-pieds-elements-metod.php">Forumconstruire</a>, <a href="https://www.ikea.com/fr/fr/p/metod-pied-70556067">fiche IKEA</a>.</p>
"""


# ------------------------------------------------------------------ porte du cellier : Mantion Tango (V13.14)
def _tango(depuis):
    a, t = M.PLIANTE, M.TANGO
    fiche = fiche_tango().replace('<table class="orga fiche">', '<table class="tango">', 1)
    return f"""<h2>Porte du cellier, {t["nom"]}</h2>
<p><a class="btn" href="{_racine(depuis)}cuisine-v13-porte-cellier.html">Plans détaillés</a></p>
{_defile(fiche)}
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
<p class="remarque">{sources_tango()}</p>
"""


# ------------------------------------------------------------------ électricité
def _tables_elec():
    lum = {r: n for r, n, *_ in M.LUMIERES}
    lignes = ""
    for r, nom, x, y, z, ou, touches in M.INTERRUPTEURS:
        for k, (t, l, mode) in enumerate(touches):
            tete_ = (f'<td rowspan="{len(touches)}">{r}</td><td rowspan="{len(touches)}"><b>{escape(nom)}</b>'
                     f', h {z}<br>{escape(ou)}</td>') if k == 0 else ""
            lignes += f"<tr>{tete_}<td>{escape(t) or '—'}</td><td><b>{l}</b> {escape(minus(lum[l]))}</td><td>{escape(mode)}</td></tr>"
    lignes += '<tr><td>—</td><td><b>Hotte</b></td><td>—</td><td>lumière de la hotte</td><td>touches de la hotte</td></tr>'
    t1 = ('<table><thead><tr><th>Inter.</th><th>Où</th><th>Touche</th><th>Allume</th><th>Fonctionnement</th>'
          f'</tr></thead><tbody>{lignes}</tbody></table>')
    circ = {k: n for k, n, *_ in M.CIRCUITS}
    pts_ = "".join(f'<tr><td>{r}</td><td>{escape(n)}</td><td>{escape(p)}</td><td class="num">plafond</td>'
                   f'<td>{circ["eclairage"]}</td></tr>' for r, n, _, _, p in M.LUMIERES)
    pts_ += "".join(f'<tr><td>{r}</td><td>{"prise double" if n == 2 else "prise"}, {escape(u)}</td>'
                    f'<td>{escape(ou)}</td><td class="num">{z}</td><td>{circ[c]}</td></tr>'
                    for r, x, y, z, n, c, u, ou in M.PRISES)
    t2 = ('<table><thead><tr><th>Repère</th><th>Quoi</th><th>Où</th><th class="num">h</th><th>Circuit</th>'
          f'</tr></thead><tbody>{pts_}</tbody></table>')
    t3 = ('<table><thead><tr><th>Circuit</th><th>Protection, section</th><th>Points</th></tr></thead><tbody>'
          + "".join(f"<tr><td>{escape(n)}</td><td>{escape(p)}</td><td>{escape(c)}</td></tr>" for _, n, p, c in M.CIRCUITS)
          + "</tbody></table>")
    return t1, t2, t3


def _electricite():
    t1, t2, t3 = _tables_elec()
    return f"""<h2>Électricité</h2>
<h3>Quel interrupteur allume quoi</h3>
{_defile(t1)}
<p class="remarque">En entrant, la main droite trouve S1 : en haut le plafonnier, au milieu les LED du plan de travail, en bas la suspension. On cuisine : S2, au bout du plan à côté de l'évier, allume ou éteint les LED sans revenir à l'entrée ; sa touche du bas allume le cellier en passant la porte (le voyant signale une lumière oubliée derrière la porte fermée). On passe à table : la suspension se règle depuis la banquette (S3) ; S1 et S3 sont deux poussoirs d'un même variateur (appui court : allume ou éteint, appui long : varie). En sortant, tout s'éteint depuis S1, sauf le cellier (S2).</p>
<h3>Points</h3>
{_defile(t2)}
<h3>Circuits proposés</h3>
{_defile(t3)}
<p class="remarque">NF C 15-100 (vérifié sur des guides, pas sur le texte de la norme ; à confirmer par l'électricien) : au moins 6 socles dans une cuisine de plus de 4 m², sur un circuit dédié 20 A de 6 socles au plus, dont 4 au-dessus du plan de travail ; une prise double compte pour 2 socles (ici 5 au-dessus du plan, plus le micro-ondes). Pas de prise au-dessus du bac de l'évier ni de la plaque ; 60 cm entre une prise et l'évier sont conseillés (P3 est à 65 du bac). Prises de crédence à 8 cm au moins au-dessus du plan (ici 19), prise de hotte à 1,80 m au moins (P4 : 2,25), sortie 32 A à 12 cm au moins du sol (P6 : 60). Circuits spécialisés pour la plaque (32 A, 6 mm², différentiel type A), le four et le lave-vaisselle. Point lumineux de plafond sur boîtier DCL. Le plafonnier suppose une boîte au plafond : à prévoir avec la suspension (dalle béton : en saillie ou par une saignée). Vérifier aussi la puissance de l'abonnement (plaque, four et LV ensemble).</p>
"""


# ------------------------------------------------------------------ rendus, matériaux, rangements, capacité
RENDUS_METHODE = ("Blender (Cycles) depuis le modèle FreeCAD de la version indiquée sous chaque image (rendus faits sur "
                  "demande) : 21 juin, 17 h, soleil réel par la fenêtre, suspension et LED allumées ; matériaux de la "
                  "section Matériaux (teintes indicatives).")


def _echantillon(e, depuis):
    """Échantillon d'un matériau : la photo (chemin depuis la racine du site), ou des aplats de couleur."""
    if isinstance(e, str):
        return (f'<img src="{_racine(depuis)}{e}" alt="" '
                'style="width:120px;height:60px;object-fit:cover;border-radius:4px;display:block">')
    return "".join(f'<span style="display:inline-block;width:{120 // len(e)}px;height:60px;background:{c};'
                   f'{"border-radius:4px 0 0 4px;" if k == 0 else ""}{"border-radius:0 4px 4px 0;" if k == len(e) - 1 else ""}'
                   f'{"border-radius:4px;" if len(e) == 1 else ""}"></span>' for k, c in enumerate(e))


def _materiaux(depuis):
    lignes = [(n, f'<span class="ech">{_echantillon(e, depuis)}</span><b>{escape(m)}</b><br>{escape(p)}')
              for n, m, p, e in M.MATERIAUX]
    bloc = materiaux(lignes).replace("<table>", '<div class="defile"><table class="mat">', 1)
    return (bloc.replace("</table>", "</table></div>", 1)
            + '\n<p class="remarque">Teintes indicatives à l\'écran : Canopée et chêne miel d\'après le rendu 3D (laque '
              "mate Plum Living), parquet d'après la photo de référence. À valider sur échantillons.</p>\n")


def _contenu():
    corps = "".join(f"<tr><td>{escape(n)}</td><td>{escape(u)}</td></tr>" for n, u in M.CONTENU)
    return f"""<h2>Contenu des rangements</h2>
{_defile(f'<table><thead><tr><th>Meuble</th><th>Contenu</th></tr></thead><tbody>{corps}</tbody></table>')}
<p class="remarque">Organisation A, tout en tiroirs, électroménager inchangé : tout se voit d'en haut, sans se baisser ni vider l'avant (coulisses plus chères que des charnières). Le contenu est aussi écrit en italique sur les façades, dans les coupes A-A (mur nord), B-B (banquette) et C-C (colonnes). Rangement proche de l'usage : ustensiles, poêles et épices autour de la plaque ; assiettes au-dessus du LV ; couverts, verres et tasses dans C3 (tiroirs à l'anglaise), à côté du frigo.</p>
"""


def _capacite():
    av, version = M.AVANT["version"], M.VERSION
    corps = corps_capacite(lignes_avant_apres(), details_capacite())
    table = (f"<table class=\"capa\"><thead><tr><th>Mesure</th><th>{av} (avant)</th><th>{version}</th><th>Écart</th>"
             f"<th>Proposition 9 A</th><th>Repère cuisine 8 m²</th></tr></thead><tbody>{corps}</tbody></table>")
    return f"""<h2>Capacité : {av} → {version} et proposition 9 A</h2>
{_defile(table)}
<p class="remarque">Mesurée comme le font les cuisinistes : mètres linéaires de meubles, nombre de meubles, tiroirs, plan de travail utile (hors évier et plaque) et implantation, sur la version figée {av}, la version affichée et la proposition 9 A, avec les repères d'une cuisine d'environ 8 m² (la pièce fait 3,25 × 2,52 = 8,2 m² hors cellier). <b>En vert</b> : dans le repère ; <b>en rouge</b> : en dessous ; dépasser le haut du repère n'est pas une erreur. L'écart se lit par rapport à {av}. <b>Volume</b> (repère moins parlant, gardé pour comparer) : largeur × profondeur du caisson × hauteur des façades de rangement, électroménager, socles et sous-évier exclus ; cellier : largeur utile × profondeur × hauteur des rayonnages, de la première tablette au haut du rayonnage.</p>
"""


def explication(rendus: Path, depuis: str = DEPUIS) -> str:
    """HTML de la vue Explication ; `rendus` : dossier des rendus du site, `depuis` : adresse du document, pour
    rebaser les liens vers la racine (porte du cellier, photo du parquet)."""
    alt = next(c for v, _, c in M.RENDUS if v == "iso")
    return (tete(CHAPO, _liens(depuis), figure_rendu(rendu(rendus, "", "iso_so"), alt))
            + principes(legende.cartes())
            + _hauteur_pt()
            + _tango(depuis)
            + _electricite()
            + f'<h2>Rendus</h2>\n<p class="remarque">{RENDUS_METHODE}</p>\n'
            + _materiaux(depuis)
            + _contenu()
            + _capacite()
            + note_source(REPERE))
