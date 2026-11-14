"""Vue Explication du salon/aménagement : chapô, cartes « Principe » (les passages du paragraphe sous le plan), matériaux,
pistes déco, rangements, tables qui se replient, meubles à fabriquer, points à vérifier, repère.

Textes et tableaux repris de l'ancien générateur 3d/salon/plan.py (`contenu`, `table_rangement`, `table_repliables`,
`meubles`), calculés depuis le modèle, avec ces écarts seulement : virgule à la place du point médian, plus de chasse
fixe (`mono`), nombres à la française (« 1,8 » et non « 1.8 », « 240 » et non « 240,0 »), légende sous un tableau en
`<p class="remarque">`, chaque tableau dans un `<div class="defile">`, liens vers les nouvelles adresses des deux
meubles, chemins de l'ancien générateur retirés de la remarque finale.
"""
from html import escape

from commun.blocs import Carte, a_verifier, materiaux, note_source, principes, tete
from pieces.salon.amenagement import document as M
from pieces.salon.amenagement import textes
from pieces.salon.meubles import cote as c

CHAPO = ("La bibliothèque reste au mur ouest : une enfilade basse avec des étagères suspendues au-dessus, le canapé dans "
         "son angle avec une table basse et un siège pivotant, face à un meuble bas sous le mur de projection. Contre le "
         "mur nord, à côté de la baie, une desserte pour la platine vinyle. La table ronde du quotidien s'ouvre au milieu "
         "pour recevoir douze personnes.")
REPERE = ("Repère : x vers l'est depuis le mur ouest, y vers le sud depuis le mur nord, z depuis le sol fini, en cm. "
          "Dimensions : pieces/salon/amenagement/document.py et pieces/salon/piece.py. Rendus 3D sur demande.")
# l'id du meuble du plan que montre la carte « Principe » d'un passage ; aucun pour un principe sans meuble
MEUBLE_DE = {"enfilade": "enfilade", "etageres": "etageres", "canape": "canape", "desserte": "desserte",
             "table-quotidien": "table", "table-ouverte": "table", "table-basse": "table-basse", "siege": "siege",
             "meuble-bas": "meuble-bas", "ecran": "ecran", "projecteur": "projecteur", "clim": "clim",
             "rangement-table-ouverte": "table-basse"}


def _defile(table: str) -> str:
    return f'<div class="defile">{table}</div>'


def cartes() -> list[Carte]:
    return [Carte(titre, corps, meuble=MEUBLE_DE.get(i, "")) for i, titre, corps in textes.PASSAGES]


# ------------------------------------------------------------------ tableaux
def table_rangement() -> str:
    e, d = M.ENFILADE, M.DESSERTE
    lignes = [
        ("① Enfilade", f'{c(e["y1"] - e["y0"])} × {e["p"]} × {e["z1"]}, {len(M.MODULES)} modules de '
                       f'{c(e["modules"][0][1] - e["modules"][0][0])}', f"≈ {round(M.VOLUME_ENFILADE, -1):.0f} L"),
        ("② Étagères sur montants", f'{len(M.TABLETTES)} tablettes chêne P{M.ETAGERES["p"]} sur {M.MONTANTS["n"]} montants '
                                    "pin noir", f"{c(M.METRES_ETAGERES)} m, ≈ {M.METRES_ETAGERES * M.CHARGE_LIVRES:.0f} kg pleines"),
        ("④ Desserte", f'{c(d["x1"] - d["x0"])} × {c(d["y1"] - d["y0"])} × {d["z1"]} sur roulettes, '
                       f'{len(d["niveaux"])} niveaux pour vinyles', f"≈ {round(M.VINYLES, -1):.0f} disques"),
    ]
    corps = "".join(f'<tr><td>{a}</td><td>{b}</td><td class="num">{v}</td></tr>' for a, b, v in lignes)
    return (f"<h2>Rangements</h2>"
            + _defile('<table><thead><tr><th>Meuble</th><th>Dimensions</th><th>Capacité</th></tr></thead>'
                      f"<tbody>{corps}</tbody></table>")
            + note_source(f'Volume utile de l\'enfilade : intérieur des caissons, panneaux de {c(M.ENFILADE["ep"])} '
                          f'déduits. Étagères : {M.CHARGE_LIVRES} kg par mètre pleine de livres (ordre de grandeur), '
                          'repris par les montants et la cloison (voir la page <a href="../etageres/">Étagères</a>). '
                          'Vinyles : environ 3,5 mm par disque sous pochette, rangées de 31,5 de profondeur.'))


def table_repliables() -> str:
    corps = "".join(
        f'<tr><td>{escape(ty)}</td><td>{f"<a href={chr(34)}{escape(u)}{chr(34)}>{escape(m)}</a>" if u else escape(m)}</td>'
        f'<td class="num">{escape(r)}</td><td>{escape(o)}</td><td>{escape(pl)}</td><td class="num">{escape(px)}</td></tr>'
        for ty, m, r, o, pl, px, u in M.TABLES_REPLIABLES)
    return ("<h2>Tables qui se replient</h2>"
            + _defile("<table><thead><tr><th>Type</th><th>Modèle</th><th>Repliée</th><th>Ouverte</th><th>Places</th>"
                      f"<th>Prix</th></tr></thead><tbody>{corps}</tbody></table>")
            + note_source("Recherche du 11/10/2026. Ronde Ø 90 : on n'en trouve pas qui dépasse ≈ 190 ouverte, soit 8 à 10 "
                          "couverts ; pour 12, il faut au moins une Ø 100 et 4 allonges (280, serré : ≈ 62 par personne). "
                          "Les consoles extensibles ont la plus petite emprise repliée (≈ 0,4 m²) mais sont rectangulaires "
                          "et étroites (90) ; leurs rallonges se rangent dans la console ou à côté. Les tables à volets et "
                          "allonges (Louis-Philippe) sont rondes volets levés et ovales avec leurs allonges, souvent "
                          "anciennes, à chiner : c'est le type dessiné. Les tables à abattants seules (gateleg) se "
                          "replient très bien mais plafonnent à 6 places. Dimensions et prix relevés sur les fiches : à "
                          "revérifier avant achat."))


def matieres() -> str:
    cr, mu, pp, ri = M.CARRELAGE, M.FINITION_MURS, M.PAPIER_PEINT, M.RIDEAU
    return materiaux([
        ("Sol", f'Carrelage {escape(cr["nom"])}, pose droite parallèle aux murs, joints fins ; teinte à choisir (rendu : '
                f'{cr["couleur"]}).'),
        ("Murs et plinthes", f'{escape(mu["nom"])}, {mu["couleur"]} ; plinthes de la couleur des murs.'),
        ("Mur derrière la desserte", f'Papier peint {escape(pp["nom"])} ; motif ≈ {pp["motif"]} cm, de la plinthe au '
                                     "plafond, sur le mur nord du décroché (violet sur le plan)."),
        ("Bois", "Enfilade, étagères, desserte, meuble bas : chêne miel (comme les meubles hauts de la cuisine) ; table "
                 "Louis-Philippe et chaises : noyer ou merisier anciens ; table basse UGGLERUM plaqué noyer."),
        ("Tissus", "Canapé SÖDERHAMN housse Gunnared gris moyen ; DYVLINGE Kelinge orange ; tapis laine beige ; rideau "
                   f'{escape(ri["nom"])}.'),
    ])


def pistes_deco() -> str:
    return ("<h2>Pistes déco</h2><p>Non dessinées : à essayer une fois le reste en place.</p>"
            '<ul class="liste">' + "".join(f"<li><b>{escape(a)}</b> : {escape(b)}.</li>" for a, b in M.PISTES_DECO)
            + "</ul>")


def meubles_a_fabriquer() -> str:
    mo, e = M.MONTANTS, M.ENFILADE
    return ('<h2>Meubles à fabriquer</h2><p>Les deux meubles du mur ouest ont chacun leur page, comme le meuble linge de '
            "la salle de bain : plans, matériaux, débit, achats et prix, montage.</p>"
            '<ul class="liste">'
            f'<li><a href="../etageres/"><b>Étagères</b></a> : {mo["n"]} montants en pin massif peint en noir '
            f'({c(mo["l"])} × {mo["p"]}, à {mo["pas"]} d\'axe en axe) vissés au mur au-dessus de l\'enfilade sans la '
            f'toucher, et {len(M.TABLETTES)} tablettes en chêne massif entaillées autour des montants, pincées par deux '
            f'chevilles en acier ({c(M.METRES_ETAGERES)} m de tablettes).</li>'
            f'<li><a href="../enfilade/"><b>Enfilade</b></a> : {c(e["y1"] - e["y0"])} × {e["p"]} × {e["z1"]} sur pieds, '
            "trois modules (portes, tiroirs, portes).</li></ul>")


def points() -> list[str]:
    cn, t, tb, ec, pj = M.CANAPE, M.TABLE, M.TABLE_BASSE, M.ECRAN, M.PROJECTEUR
    q, o = M.CONFIGS["f"]["chaises"], M.CONFIGS["o"]["chaises"]
    return [
        "<b>Prises</b> : près de la desserte (platine, ampli ou enceintes actives), près du canapé (lampadaire), derrière "
        "le meuble bas (box), au plafond (vidéoprojecteur).",
        f"<b>Chaises</b> : {q} autour de la table ronde ; les {M.CHAISES_PLIANTES} pliantes de plus pour recevoir à {o} sont "
        "rangées dans le kafoutche extérieur.",
        f'<b>Canapé</b> : <a href="{escape(cn["url"])}">{escape(cn["nom"])}</a>, {cn["l"]} × {cn["p"]} × {cn["dos"]} ; '
        f'hauteur d\'assise à relever en magasin (dessinée à {cn["assise"]}, la table basse UGGLERUM est à {tb["z1"]}).',
        f'<b>Table</b> : ronde Ø {c(t["d"])} à volets et allonges, à chiner (les Louis-Philippe font souvent 105 à 120) ; '
        f'il faut {t["allonges"]} allonges de {t["allonge"]} pour {c(t["ouvert"])}. Ø 90 : 10 couverts au plus.',
        "<b>Clim</b> : position et dimensions à relever ; le souffle tombe sur la table ronde du quotidien (déflecteur "
        "orienté vers le haut).",
        f'<b>Vidéoprojecteur</b> : rapport de projection {c(pj["rapport"], 2)} pour une image de {c(ec["l"])} à '
        f'{c(pj["recul"])} ; prise et câble HDMI au plafond, ou projecteur posé sur une tablette au-dessus du canapé. Mur '
        "sud peint en blanc mat (ou toile tendue).",
    ]


def explication() -> str:
    return (tete(CHAPO) + principes(cartes()) + matieres() + pistes_deco() + table_rangement() + table_repliables()
            + meubles_a_fabriquer() + a_verifier(points(), titre="Points à vérifier") + note_source(REPERE))
