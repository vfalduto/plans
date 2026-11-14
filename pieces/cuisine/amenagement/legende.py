"""Légende du plan de la cuisine/aménagement : l'ancienne légende du plan (3d/v13/plan.py, `contenu()` et
`texte_cellier()`), calculée depuis le modèle, coupée en morceaux.

Les phrases de convention (échelle, pièce vide, sols, cloisons déposées) vont dans la légende de la fiche du plan ; le
reste en cartes « Principe » de l'Explication, reprises dans les fiches des meubles qu'elles nomment. Les morceaux,
joints par une espace, redonnent l'ancienne légende au caractère près (tests/test_cuisine_legende.py).
"""
import math
from dataclasses import dataclass

from commun.blocs import Carte
from pieces.cuisine import modele as M
from pieces.cuisine.dessin import f, virg


@dataclass(frozen=True)
class Morceau:
    """`ou` : "legende" (fiche du plan) ou "carte" ; `titre` : celui de la carte ; `meuble` : l'id de
    `zones.MEUBLES_PLAN` dont seul parle le morceau ; `nomme` : les autres meubles dont la fiche le reprend."""
    ou: str
    titre: str
    html: str
    meuble: str = ""
    nomme: tuple[str, ...] = ()


def _bas(n):
    return f"b{n}"


def morceaux() -> list[Morceau]:
    """Dans l'ordre de l'ancienne légende."""
    caissons = [b for b in M.MEUBLES if b.role == "caisson" and b.y0 == 0]
    x0, x1 = caissons[0].x0, caissons[-1].x1
    hauts = [b for b in M.MEUBLES if b.role == "caisson_haut"]
    tp = M.TRIANGLE
    cotes_tri = [math.dist(a[1], b[1]) for a, b in zip(tp, tp[1:] + tp[:1])]
    tri = ", ".join(f"{a[0]} → {b[0]} {d:.0f}" for (a, b), d in zip(zip(tp, tp[1:] + tp[:1]), cotes_tri))
    plaque, evier = M.sur_bas(M.B_PLAQUE), M.sur_bas(M.B_EVIER)
    E, BQ, T, a, nord = M.ENTREE, M.BANQ, M.TABLE, M.PLIANTE, M.RAYON_NORD
    tous_bas = tuple(_bas(i) for i in range(1, M.N_BAS + 1))

    def leg(html):
        return Morceau("legende", "", html)

    def carte(titre, html, meuble="", nomme=()):
        return Morceau("carte", titre, html, meuble, tuple(nomme))

    return [
        leg("Échelle : 1 unité = 1 cm. Pièce vide : chambre et ancien cellier ouverts, sans cloison. Restent la fenêtre "
            "coulissante du mur ouest (y 58 → 200), la porte d'entrée (baie x 228 → 306), le décroché de l'angle "
            "sud-est, la chute (sous le ballon), le ballon et le WC."),
        leg("<b>Sols</b> : parquet chêne en bâtons rompus dans l'ancienne chambre (x 0 → 325), gris ciment dans "
            "l'ancien cellier et l'ancien placard (à partir de x 325) ; les cloisons déposées du relevé d'origine sont "
            "en tireté (chambre / cellier x 325 → 335, cellier / placard y 100 → 110)."),
        carte("Mur nord",
              f"<b>Mur nord</b> : {len(caissons)} meubles bas de {' + '.join(f(w) for w in M.LARGEURS_BAS)} "
              f"(x {f(x0)} → {f(x1)}), à {f(M.ECART_OUEST)} du mur ouest et {f(M.FILEUR_EST)} du retour de cloison du "
              f"cellier (fileurs Canopée) : plan de travail de mur à mur ; caisson P{M.P_CAISSON} + façade {M.FACADE}, "
              f"profondeur {M.P_CAISSON + M.FACADE}, sous un plan de travail de 4 (P62, débord de 2), sauf "
              f"B{M.B_ETROIT} (P{M.P_ETROIT} + façade, profondeur {M.P_ETROIT + M.FACADE}, plan P{M.P_PLAN_ETROIT}) "
              f"qui laisse se replier la porte du cellier.", nomme=tous_bas),
        carte("Induction",
              f"<b>Induction</b> 60 classique, four encastré dessous et hotte intégrée dans H1 au-dessus, sur "
              f"B{M.B_PLAQUE} (x {f(plaque[0])} → {f(plaque[1])}) ;", _bas(M.B_PLAQUE), ("h1",)),
        carte("Évier",
              f"<b>évier</b> inox 1 bac 56 × 50 (bac 40 × 40) sur B{M.B_EVIER} (x {f(evier[0])} → {f(evier[1])}), "
              f"mitigeur derrière le bac, égouttoir à gauche au-dessus de B4.", _bas(M.B_EVIER), ("b4",)),
        carte("Mur est",
              f"<b>Mur est</b> : colonnes C1 (lave-vaisselle en hauteur, micro-ondes au-dessus, y {f(M.JOUE_C2)} → "
              f"{f(M.COL_Y0)}) et C2 (frigo, y {f(M.COL_Y0)} → {f(M.COL_Y0 + 60)}) de 60, P60, fileur chêne de "
              f"{M.FILEUR_C2} entre C2 et le décroché (la porte du frigo s'ouvre à 90° sans toucher le fileur de "
              f"l'entrée), contre le mur du WC (x {f(M.X_MUR_EST)}), du décroché vers le nord, façades vers l'ouest "
              f"(x {f(M.COL_X)}). Le mur sud est libre entre la table et le caisson du galandage.",
              nomme=("c1", "c2")),
        carte("Porte d'entrée",
              f"<b>Porte d'entrée</b> : à galandage, vantail {f(E['vantail'])} × {E['h']} (trait plein, fermé) ; "
              f"ouverte, elle rentre vers l'ouest dans un caisson de galandage (ocre, x {f(E['poche'][0])} → "
              f"{f(E['poche'][1])}) logé dans un doublage de 10 contre le mur sud (y 242 → 252), avec un montant de 4 "
              f"à l'est de la baie. Le passage reste de {f(E['x1'] - E['x0'])} ; rien ne bat dans la cuisine.",
              "porte-entree"),
        carte("Tableau noir",
              "Face cuisine du caisson : <b>tableau noir</b> (peinture ardoise, h 120 → 200) et <b>zone aimantée</b> "
              "en dessous (h 70 → 118), sur 81 de large (coupe B-B).", "tableau-noir"),
        carte("Équipements",
              f"<b>Équipements</b> : poubelles de tri sous l'évier (B{M.B_EVIER}), four sous la plaque "
              f"(B{M.B_PLAQUE}), lave-vaisselle 60 tout intégrable en hauteur dans C1.",
              nomme=(_bas(M.B_EVIER), _bas(M.B_PLAQUE), "c1")),
        carte("Triangle d'activité",
              f"<b>Triangle d'activité</b> (rouge ; centres de la plaque et de l'évier, milieu de la façade du frigo) : "
              f"{tri}, total {f(round(sum(cotes_tri)))} cm."),
        carte("Passage",
              f"<b>Passage</b> (cote oblique) : {M.ACCES_CELLIER:.0f} du coin du plan de travail P62 (B{M.B_EVIER}, "
              f"x {f(evier[1])}, y 62) au coin nord-ouest de C1 (y {M.JOUE_C2}), devant la porte du cellier."),
        carte("Réseaux",
              "<b>Réseaux</b> (bleu ; pose type IKEA METOD, sans vide technique : 1 cm de jeu derrière les caissons)."),
        carte("Réseaux",
              "Le <b>LV</b>, en hauteur dans C1, est raccordé par le cellier sans le traverser : alimentation depuis la "
              "nourrice le long du mur est puis du mur nord du WC, sous le rayonnage sud, jusqu'au dos de C1 ; vidange "
              "pompée par le LV le long du même mur, directement dans la chute.", "c1"),
        carte("Réseaux",
              f"À l'est de l'évier, les tuyaux passent dans le <b>fond de B{M.B_ETROIT}</b> (découpé, tiroirs P30) et "
              f"derrière son fileur, puis dans le retour de cloison au nord de la porte du cellier : tout <b>longe les "
              f"murs</b>, en partie basse.", _bas(M.B_ETROIT)),
        carte("Réseaux",
              f"Alimentation EF/EC en trait plein, à 3 des murs, depuis la <b>nourrice</b> (petit point, sous le "
              f"ballon) : le long du retour sud de l'alcôve (y 44), de sa face ouest (x 434), puis du mur nord jusqu'à "
              f"l'évier ; une seconde ligne va au LV (C1) le long du mur nord du WC. Dans la niche du cellier, tout "
              f"reste dans la zone technique des {M.ZONE_TECH} premiers cm (la chute est basse, dernier étage) : "
              f"l'alimentation y passe à h 20 et remonte dans l'angle, l'évacuation descend à h 25 sous la première "
              f"tablette du rayonnage nord ; un coffre technique (h 0 → {M.ZONE_TECH}) couvre l'angle. Évacuation en "
              f"tireté depuis le siphon de l'évier (axe x {f(M.SIPHON[0])}), à 4 du mur nord dans la cuisine, puis à "
              f"12 des murs pour passer au-delà de la nourrice : le long du mur nord, de l'alcôve, du mur est (x 484) "
              f"puis du mur nord du WC jusqu'à la <b>chute</b> (cercle contre le mur du WC, sous le ballon : la colonne "
              f"d'eaux usées existante, x à confirmer). Contre l'alcôve, ils passent sous la première tablette du "
              f"rayonnage du mur nord ; sous le ballon (h 90), ils passent dessous ; longueur ≈ "
              f"{f(M.EVAC_LONGUEUR)} : de h {M.RESEAUX[3][3]} sous le siphon à h {M.RESEAUX[4][3]} à la chute, soit "
              f"{(M.RESEAUX[3][3] - M.RESEAUX[4][3]) / M.EVAC_LONGUEUR * 100:.1f} cm/m de pente moyenne (hauteur "
              f"d'arrivée sur la chute à confirmer). Les réseaux traversent la cloison du cellier."),
        carte("Cellier", f"<b>Cellier</b> : cloison de 7 (x 320 → 327), contre le fileur de B{M.N_BAS}.",
              nomme=(_bas(M.N_BAS),)),
        # texte_cellier() de l'ancien générateur
        carte("Porte du cellier",
              f"<b>Porte du cellier</b> ({M.PORTE_TITRE}) : un retour de cloison va du mur nord à y "
              f"{f(M.CLOISON_Y1)} (passage des réseaux ; V13.0 : allongé de {M.DECALAGE_PORTE}, la porte descend "
              f"d'autant vers le sud) ; la baie va jusqu'au flanc nord de C1 : {f(M.BAIE_Y1 - M.BAIE_Y0)} × 204 sous "
              f"un linteau. Porte pliante sans dormant sur ferrure <b>Mantion Tango</b> ({M.TANGO['ref']}, rail alu "
              f"sous le linteau, pas de rail au sol), deux panneaux de {virg(a['l'])} × "
              f"{virg(round(a['z1'] - a['z0'], 1))} × {virg(a['ep'])} à faire découper, pivot au nord : en s'ouvrant, "
              f"les vantaux se replient l'un contre l'autre et se rangent côté cuisine contre le retour de cloison, à "
              f"{f(M.JEU_B6_PORTE)} du plan de B{M.B_ETROIT} (P{f(M.P_PLAN_ETROIT)} : c'est ce qui fixe sa "
              f"profondeur ; côté cellier, ils heurteraient le rayonnage nord) ; le vantail du pivot balaie "
              f"{virg(a['l'])} côté cuisine. Poignée au sud, côté C1 ; le bouton au-dessus du plan la montre ouverte, "
              f"mi-ouverte (vantaux en V, pivot à {a['mi']}°) ou fermée.", "porte-cellier"),
        carte("Porte du cellier",
              f"<b>Passage libre ≈ {f(M.PASSAGE_CELLIER)}</b> ; accès depuis la cuisine, du coin du plan de "
              f"B{M.B_EVIER} à l'angle de C1 : {M.ACCES_CELLIER:.0f}.", "porte-cellier"),
        carte("Passages dans le cellier",
              f"<b>Passages dans le cellier</b> : {f(M.PASSAGE_ENTREE)} à l'entrée, entre le rayonnage nord et le "
              f"flanc de C1 ; {f(M.PASSAGE_BALAIS)} entre le rayonnage nord et les balais, vers la niche."),
        carte("Organisation du cellier",
              f"<b>Organisation du cellier</b> : un <b>rayonnage toute hauteur P{nord['y1']}</b> contre le mur nord, "
              f"du retour de cloison (V13.0 : prolongé jusqu'à lui, sans arrondi) jusqu'au mur de l'alcôve "
              f"(x {nord['x0']} → {nord['x1']}, {len(nord['zs'])} tablettes de {M.L_NORD}, la première à h "
              f"{nord['zs'][0]} au-dessus des tuyaux), pour les denrées, avec l'aspirateur couché dessous, au bout "
              f"est ;", "rayonnage-nord", ("aspirateur",)),
        carte("Organisation du cellier",
              f"contre le mur du WC (V13.6, à la place du rayonnage sud), <b>deux balais</b> sur un tasseau à "
              f"{100 - M.Y_BALAIS} du mur, devant les tuyaux du LV ; entre les deux, {f(M.PASSAGE_BALAIS)} de passage "
              f"vers la niche : nourrice, groupe de sécurité et chute restent accessibles.", "balais"),
        carte("Organisation du cellier",
              f"Au-dessus des balais (V13.22), une <b>étagère P{M.ENTRETIEN['y1'] - M.ENTRETIEN['y0']}</b> à deux "
              f"tablettes (h {M.ENTRETIEN['zs'][0]} et {M.ENTRETIEN['zs'][1]}) pour les produits d'entretien, à part "
              f"de la nourriture ;", "entretien"),
        carte("Organisation du cellier", "le <b>seau</b> au sol dans l'angle sud-est, contre C1.", "seau"),
        carte("Finitions",
              f"<b>Finitions</b> : fileur chêne de {M.FILEUR_C2} au sud de C2, jusqu'au fileur couleur des murs qui "
              f"ferme l'angle au nu du montant de l'entrée (y {f(M.Y_MONTANT)}), joue à l'ouest de H1, fileurs de "
              f"{f(M.FILEUR_EST)} entre B{M.B_ETROIT} / H{M.N_HAUTS} et le retour de cloison, fileurs de 7 jusqu'au "
              f"plafond au-dessus des hauts et des colonnes.",
              nomme=("c2", "h1", _bas(M.B_ETROIT), f"h{M.N_HAUTS}")),
        # fin de texte_cellier()
        carte("Coin repas",
              f"<b>Coin repas</b> (V13.17) : banquette d'une place contre le mur ouest, dans l'angle sud-ouest, assise "
              f"tournée vers l'est (x {f(BQ['x0'])} → {f(BQ['x1'])}, y {f(BQ['y0'])} → {f(BQ['y1'])} : "
              f"{f(BQ['y1'] - BQ['y0'])} de long, dossier {BQ['dossier']} à h 85 contre le mur, assise "
              f"{f(BQ['x1'] - BQ['x0'] - BQ['dossier'])} à h 45 avec coffre) ; elle passe de {f(200 - BQ['y0'])} sous "
              f"la fenêtre (y 200), le dossier reste sous l'allège (h 106).", "banquette"),
        carte("Coin repas",
              f"Table type Véra {T['cote']} × {T['cote']} aux angles arrondis (rose poudré, chant noir), sur un pied "
              f"central à embase, à 10 de l'assise et à 10 du bas de mur sud (x {f(T['x0'])} → {f(T['x1'])}, y "
              f"{f(T['y0'])} → {f(T['y1'])}) : son bord nord est à {f(T['y0'] - M.P_CAISSON - M.FACADE - 52)} de la "
              f"porte du four ouverte (y {f(M.P_CAISSON + M.FACADE + 52)}) et à {f(T['y0'] - 62)} du plan de "
              f"travail.", "table"),
        carte("Coin repas",
              f"Une <b>chaise</b> {M.CHAISE['l']} × {M.CHAISE['p']} en face, côté est, dossier à l'est.", "chaise"),
        carte("Bas de mur",
              f"Mur sud derrière la table : <b>bas de mur</b> en chêne miel (2, h {M.BAS_DE_MUR['h']}, x "
              f"{f(M.BAS_DE_MUR['x0'])} → {f(M.BAS_DE_MUR['x1'])}), où s'appuie la banquette, et papier peint Hermione "
              f"au-dessus jusqu'au plafond (voir Matériaux).", nomme=("banquette",)),
        carte("Suspension",
              f"<b>Suspension</b> (tireté jaune) : point lumineux au plafond centré sur la table, abat-jour Ø "
              f"{M.SUSPENSION['d']}, bas à h {M.SUSPENSION['z0']}, soit {M.SUSPENSION['z0'] - 75} au-dessus du "
              f"plateau (coupe B-B).", nomme=("table",)),
        carte("Places",
              f"<b>Places</b> : {M.PLACES_BANQUETTE} sur la banquette + 1 sur la chaise ; un tabouret pliant côté nord "
              f"en appoint.", nomme=("banquette", "chaise")),
        carte("Sous la banquette",
              f"<b>Sous la banquette</b> : un seul tiroir, ouvert côté nord (façade h 6 → 40), hors des jambes et de la "
              f"table (tireté : tiroir sorti de 35, jusqu'à y {f(BQ['y0'] - 37)}).", "banquette"),
        carte("Au-dessus de la banquette",
              f"<b>Au-dessus</b> (tireté) : étagère P25 contre le mur sud, du mur ouest au doublage de l'entrée, dessus "
              f"à h {f(M.ETAGERE_BANQ['z1'])}, avec l'enceinte audio (22 × 18 × 30) à l'est et la plante à l'ouest "
              f"(coupe B-B).", "etagere-banquette"),
        carte("Ouvertures",
              f"<b>Ouvertures</b> : porte du LV abattue (C1, x {f(M.COL_X - 58)} → {f(M.COL_X)}, y {f(M.JOUE_C2)} → "
              f"{f(M.JOUE_C2 + 60)}), porte du four abattue (sous la plaque), porte du frigo (dessinée à 90°), "
              f"charnières au sud : elle se rabat vers le sud, devant le fileur de C2 ({M.FILEUR_C2}), et on accède au "
              f"frigo par le nord, côté évier. Elle s'ouvre au plus à ≈ "
              f"{M.FRIGO_ANGLES['entree_fermee'][0]:.0f}° porte d'entrée fermée (son bout touche le vantail "
              f"d'entrée) et ≈ {M.FRIGO_ANGLES['entree_ouverte'][0]:.0f}° porte d'entrée ouverte (montant du "
              f"galandage) ; calcul sur une façade de 60 × 2 tournant autour de son angle avant, à quelques degrés "
              f"près selon la charnière.", nomme=("c1", "c2", _bas(M.B_PLAQUE))),
        carte("Meubles hauts",
              f"<b>Meubles hauts</b> (tireté) : {len(hauts)} de {' + '.join(f(w) for w in M.LARGEURS_HAUTS)}, x "
              f"{f(hauts[0].x0)} → {f(hauts[-1].x1)}, joints au droit de ceux des bas, fileur de {f(M.FILEUR_EST)} "
              f"jusqu'au retour de cloison ; à leur gauche, étagères ouvertes jusqu'au mur ouest ; caisson "
              f"P{M.P_HAUT} + façade {M.FACADE} (H5 compris, comme H4).",
              nomme=tuple(b.nom.removeprefix("caisson_") for b in hauts) + ("etageres",)),
    ]


def legende_html() -> str:
    """Légende de la fiche du plan : les morceaux de convention, un `<p>` chacun."""
    return "".join(f"<p>{m.html}</p>" for m in morceaux() if m.ou == "legende")


def cartes() -> list[Carte]:
    """Cartes « Principe » : morceaux consécutifs de même titre réunis ; le meuble seulement s'ils n'en ont qu'un."""
    groupes: list[list[Morceau]] = []
    for m in morceaux():
        if m.ou != "carte":
            continue
        if groupes and groupes[-1][0].titre == m.titre:
            groupes[-1].append(m)
        else:
            groupes.append([m])
    sortie = []
    for g in groupes:
        meubles = {m.meuble for m in g}
        sortie.append(Carte(g[0].titre, " ".join(m.html for m in g), meubles.pop() if len(meubles) == 1 else ""))
    return sortie


def textes_par_meuble() -> dict[str, str]:
    """HTML en ligne de la fiche de chaque meuble (pour `zones.zones`) : les morceaux qui le portent ou le nomment."""
    textes: dict[str, list[str]] = {}
    for m in morceaux():
        for id_ in ((m.meuble,) if m.meuble else ()) + m.nomme:
            textes.setdefault(id_, []).append(m.html)
    return {id_: "<br>".join(t) for id_, t in textes.items()}
