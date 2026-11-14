"""Document d'essai du gabarit : un aménagement à trois variantes.

La variante `a` a les coupes A, B et C ; `b` et `c` ont aussi D. Iso est vide. Une option nuancier `teinte` et
deux options « choix » : `table` (quotidien ou ouverte : le plan, ses zones et la coupe A changent) et `bois` (chêne,
noyer ou frêne, ce dernier sans rendu : l'image de la caméra change) ; un cercle du plan ne se montre qu'avec la table
ouverte en noyer.
"""
from pathlib import Path

from commun.blocs import Rendu, Zone, figure_choix, zones_svg
from commun.modele import Changement, Document, Element, Option, Piece, Site, Valeur, Variante, Vue

VARIANTES = (
    Variante("a", "A", "V1.2", (
        Changement("V1.2", "12/11/2026", "Coupe C ajoutée."),
        Changement("V1.1", "10/11/2026", "Plan redessiné."),
    )),
    Variante("b", "B", "V0.3", (Changement("V0.3", "13/11/2026", "Coupe D ajoutée."),)),
    Variante("c", "C", "V0.1", (Changement("V0.1", "13/11/2026", "Première version."),)),
)

COUPES = {"a": "ABC", "b": "ABCD", "c": "ABCD"}
LARGEUR = {"a": 60, "b": 70, "c": 80}

TEINTE = Option(
    id="teinte",
    nom="Teinte des murs",
    surfaces=("murs", "plafond"),
    type="nuancier",
    defaut="v1",
    valeurs=(
        Valeur("v1", "Blanc cassé", "#EEEBE3", groupe="Clairs"),
        Valeur("v2", "Sauge", "#A9B8A0", groupe="Verts", note="peinture seulement"),
        Valeur("v3", "Terre cuite", "#B5735A", groupe="Ocres"),
    ),
    portee="Visible sur le plan, les coupes et les rendus.",
    css="--teinte",
    filtre=True,
)

TABLE = Option("table", "Table", ("table",), "choix", "quotidien",
               (Valeur("quotidien", "Au quotidien"), Valeur("ouverte", "Ouverte", rendue=False)),
               "Visible sur le plan et les coupes ; les rendus montrent la table du quotidien.")
BOIS = Option("bois", "Bois", ("meubles",), "choix", "chene",
              (Valeur("chene", "Chêne", "#B07A45"), Valeur("noyer", "Noyer", "#6B4630"),
               Valeur("frene", "Frêne", "#D9BF92", rendue=False)),
              "Visible sur les rendus ; le plan et les coupes ne changent pas.")


def _svg(variante, sujet):
    return (f'<svg viewBox="0 0 100 50" role="img" aria-label="{sujet}, variante {variante.upper()}">'
            f'<rect x="10" y="10" width="{LARGEUR[variante]}" height="30"/></svg>')


ZONE = ('<rect class="zone" data-meuble="0" x="10" y="10" width="20" height="15" rx="2" tabindex="0" role="button"'
        ' aria-label="Banc"/>')
MODELE = ('<template data-meuble="0" data-titre="Banc"><p class="cotes">95 cm</p>'
          '<div class="actions"><a class="btn" href="#coupes?k=A">Coupe A</a></div></template>')
# la table : deux emprises d'un même meuble, selon l'option table ; le cercle, selon table et bois à la fois
TABLE_PLAN = ('<g data-si="table:quotidien"><rect class="table" x="70" y="38" width="15" height="8"/></g>'
              '<g data-si="table:ouverte"><rect class="table" x="60" y="38" width="25" height="8"/></g>'
              '<g data-si="table:ouverte bois:noyer"><circle class="combi" cx="92" cy="8" r="4"/></g>'
              + zones_svg((Zone("table", "Table", (70, 38, 85, 46), "15 cm", "", si="table:quotidien"),
                           Zone("table", "Table", (60, 38, 85, 46), "25 cm", "", si="table:ouverte"))))
TABLE_MODELES = ('<template data-meuble="table" data-si="table:quotidien" data-titre="Table"><p class="cotes">15 cm</p></template>'
                 '<template data-meuble="table" data-si="table:ouverte" data-titre="Table"><p class="cotes">25 cm</p></template>')
TABLE_COUPE = ('<g data-si="table:quotidien"><rect class="table" x="70" y="32" width="15" height="2"/></g>'
               '<g data-si="table:ouverte"><rect class="table" x="60" y="32" width="25" height="2"/></g>')
CALQUES = ('<h3>Calques</h3><div class="calques">'
           '<button type="button" data-calque="cotes" aria-pressed="true">Cotes</button>'
           '<button type="button" data-calque="passages" aria-pressed="true">Passages libres</button></div>')
# rendu d'essai : une image de 40 x 30 en data URI, dans le cadre des vues Iso et Caméra
MASQUE = ('data:image/svg+xml,%3Csvg%20xmlns=%27http://www.w3.org/2000/svg%27%20viewBox=%270%200%2040%2030%27%3E%3Crect'
          '%20width=%2720%27%20height=%2730%27/%3E%3C/svg%3E')
IMAGE = ('data:image/svg+xml,%3Csvg xmlns=%27http://www.w3.org/2000/svg%27 viewBox=%270 0 40 30%27%3E%3Crect'
         ' width=%2740%27 height=%2730%27 fill=%27%23ccc%27/%3E%3C/svg%3E')
RENDU = figure_choix({
    "chene": Rendu(IMAGE, MASQUE, Path("chene.jpg"), existe=True, masque_existe=True),
    "noyer": Rendu(IMAGE.replace("fill=%27%23ccc%27", "fill=%27%23963%27"), MASQUE, Path("noyer.jpg"), existe=True,
                   masque_existe=True),
    "frene": Rendu("", "", Path("frene.jpg"), existe=False),
}, BOIS, "Depuis le banc", filtre="teinte")


def vues(variante):
    coupes = [Element(k=l, nom=l, titre=f"Coupe {l}-{l}",
                      scene=_svg(variante, f"Coupe {l}").replace("</svg>", (TABLE_COUPE if l == "A" else "") + "</svg>"),
                      fiche=f"<p>Coupe {l} de la variante {variante.upper()}.</p>"
                            + ('<p data-si="table:ouverte">Table ouverte.</p>' if l == "A" else ""))
              for l in COUPES[variante]]
    return {
        "plan": Vue("plan", [Element(k="", nom="Plan", titre="Plan", scene=_svg(variante, "Plan").replace("</svg>", ZONE + TABLE_PLAN + "</svg>"),
                                    fiche=MODELE + TABLE_MODELES)],
                    fiche='<div class="fiche-meuble"><p>Touchez un meuble pour afficher sa fiche.</p></div>' + CALQUES, outils=("zoom", "mesure")),
        "coupes": Vue("coupes", coupes, fiche="<h3>Position</h3><p>Trait de coupe sur le mini-plan.</p>",
                      outils=("zoom", "mesure")),
        "iso": Vue("iso", []),
        "camera": Vue("camera", [Element(k="banc", nom="Assis sur le banc", titre="Assis sur le banc",
                                         scene=RENDU,
                                         fiche="<p class=\"cotes\">yeux à 112 cm, objectif 17 mm</p>")]),
        "explication": Vue("explication", [Element(k="", nom="Explication", titre="Explication",
                                                   scene=f"<h2>Principe</h2><p>Variante {variante.upper()}.</p>")]),
    }


DOCUMENT = Document("essai", "amenagement", "Aménagement", "amenagement", VARIANTES, vues, options=(TEINTE, TABLE, BOIS))

SITE = Site((Piece("essai", "Essai", (DOCUMENT,)),))
