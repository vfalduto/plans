"""Document d'essai du gabarit : un aménagement à trois variantes.

La variante `a` a les coupes A, B et C ; `b` et `c` ont aussi D. Iso est vide. Une option nuancier `teinte`.
"""
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


def _svg(variante, sujet):
    return (f'<svg viewBox="0 0 100 50" role="img" aria-label="{sujet}, variante {variante.upper()}">'
            f'<rect x="10" y="10" width="{LARGEUR[variante]}" height="30"/></svg>')


ZONE = ('<rect class="zone" data-meuble="0" x="10" y="10" width="20" height="15" rx="2" tabindex="0" role="button"'
        ' aria-label="Banc"/>')
MODELE = ('<template data-meuble="0" data-titre="Banc"><p class="cotes">95 cm</p>'
          '<div class="actions"><a class="btn" href="#coupes?k=A">Coupe A</a></div></template>')
CALQUES = ('<h3>Calques</h3><div class="calques">'
           '<button type="button" data-calque="cotes" aria-pressed="true">Cotes</button>'
           '<button type="button" data-calque="passages" aria-pressed="true">Passages libres</button></div>')
# rendu d'essai : une image de 40 x 30 en data URI, dans le cadre des vues Iso et Caméra
MASQUE = ('data:image/svg+xml,%3Csvg%20xmlns=%27http://www.w3.org/2000/svg%27%20viewBox=%270%200%2040%2030%27%3E%3Crect'
          '%20width=%2720%27%20height=%2730%27/%3E%3C/svg%3E')
RENDU = ('<figure class="cadre rendu"><img alt="Depuis le banc" draggable="false" src="data:image/svg+xml,'
         '%3Csvg xmlns=%27http://www.w3.org/2000/svg%27 viewBox=%270 0 40 30%27%3E%3Crect width=%2740%27 height=%2730%27'
         ' fill=%27%23ccc%27/%3E%3C/svg%3E"><img class="calque" alt="" aria-hidden="true" draggable="false"'
         ' src="data:image/svg+xml,%3Csvg xmlns=%27http://www.w3.org/2000/svg%27 viewBox=%270 0 40 30%27%3E%3Crect'
         ' width=%2740%27 height=%2730%27 fill=%27%23ccc%27/%3E%3C/svg%3E"'
         ' style="filter:url(#filtre-teinte);-webkit-mask-image:url('+MASQUE+');mask-image:url('+MASQUE+')">'
         '</figure>')


def vues(variante):
    coupes = [Element(k=l, nom=l, titre=f"Coupe {l}-{l}", scene=_svg(variante, f"Coupe {l}"),
                      fiche=f"<p>Coupe {l} de la variante {variante.upper()}.</p>") for l in COUPES[variante]]
    return {
        "plan": Vue("plan", [Element(k="", nom="Plan", titre="Plan", scene=_svg(variante, "Plan").replace("</svg>", ZONE + "</svg>"),
                                    fiche=MODELE)],
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


DOCUMENT = Document("essai", "amenagement", "Aménagement", "amenagement", VARIANTES, vues, options=(TEINTE,))

SITE = Site((Piece("essai", "Essai", (DOCUMENT,)),))
