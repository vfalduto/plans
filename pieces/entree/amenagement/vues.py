"""Vues Plan et Coupes de l'entrée, pour les deux variantes (principale, victor).

`vues(variante)` rend le dictionnaire des vues du type « aménagement ». Iso, Caméra et Explication sont vides
jusqu'à la tâche 14. Le plan et les coupes viennent de dessin_principale.py et dessin_victor.py ; le texte long qui
suivait chaque dessin est devenu son aria-label.
"""
from html import escape

from commun.modele import Element, Vue
from commun.position import mini_plan
from pieces.entree import piece
from pieces.entree.amenagement import dessin_principale, dessin_victor, document, victor

# (module de variante, module de dessin)
VARIANTES = {"principale": (document, dessin_principale), "victor": (victor, dessin_victor)}

# Calques du plan : (id, nom). Chaque id correspond à la classe `sans-<id>` posée sur la section par le JS ; les
# éléments SVG qu'il masque portent déjà ces classes (voir l'en-tête de dessin_principale.py).
CALQUES = (("cotes", "Cotes"), ("passages", "Passages libres"), ("coupes", "Traits de coupe"),
           ("voisines", "Pièces voisines"), ("annotations", "Annotations"))

# Trait de coupe sur le plan : axe du trait (h : horizontal, à y = repère ; v : vertical, à x = repère), bornes
TRAITS = {"A": ("h", -6, 270), "B": ("v", -6, 380), "C": ("h", -6, 360), "D": ("v", -6, 380)}


def _e(texte):
    return escape(str(texte), quote=True)


def _trait(D, lettre):
    axe, d0, d1 = TRAITS[lettre]
    coupe = getattr(D, f"COUPE_{lettre}")
    return (lettre, ((d0, coupe), (d1, coupe)) if axe == "h" else ((coupe, d0), (coupe, d1)))


def _zones(M, D, legende_principes):
    """Rectangles touchables du plan, un par meuble de `M.ZONES`."""
    rects = []
    for i, z in enumerate(M.ZONES):
        titre = legende_principes[z["principe"]][0]
        rects.append(f'<rect class="zone" data-meuble="{i}" x="{z["x0"]}" y="{z["y0"]}" width="{z["x1"] - z["x0"]}"'
                     f' height="{z["y1"] - z["y0"]}" rx="2" tabindex="0" role="button" aria-label="{_e(titre)}"/>')
    return "".join(rects)


def _modeles(M, principes):
    """Un `<template data-meuble>` par zone : le JS le recopie dans la fiche quand on touche le meuble."""
    modeles = []
    for i, z in enumerate(M.ZONES):
        titre, texte = principes[z["principe"]]
        cotes = z["cotes"] + (" cm" if z["cotes"][0].isdigit() else "")
        liens = ""
        if z["coupe"]:
            liens += f'<a class="btn" href="#coupes?k={z["coupe"]}">Coupe {z["coupe"]}</a>'
        liens += f'<a class="btn" href="#iso?k=iso_{z["iso"]}">Iso</a>'
        modeles.append(f'<template data-meuble="{i}" data-titre="{_e(titre)}"><p class="cotes">{_e(cotes)}</p>'
                       f'<p>{texte}</p><div class="actions">{liens}</div></template>')
    return "".join(modeles)


def _fiche_plan(D):
    boutons = "".join(f'<button type="button" data-calque="{k}" aria-pressed="true">{n}</button>' for k, n in CALQUES)
    return ('<div class="fiche-meuble"><p>Touchez un meuble pour afficher sa fiche.</p></div>'
            f'<h3>Calques</h3><div class="calques">{boutons}</div>'
            f'<h3>Légende</h3>{dessin_principale.legende()}')


def _vue_plan(M, D):
    legendes, principes = D.legendes(M), D.principes(M)
    svg = D.plan_svg(M, aria=legendes["plan"]).replace("</svg>", _zones(M, D, principes) + "</svg>")
    element = Element(k="", nom="Plan", titre="Plan", scene=svg, fiche=_modeles(M, principes))
    return Vue("plan", [element], fiche=_fiche_plan(D), outils=("zoom", "mesure"))


def _vue_coupes(M, D):
    legendes = D.legendes(M)
    lettres = list(D.SUJETS)
    elements = []
    for lettre in lettres:
        sujet = D.SUJETS[lettre]
        scene = getattr(D, f"coupe_{lettre.lower()}")(M, aria=legendes[lettre])
        elements.append(Element(k=lettre, nom=f"{lettre} {sujet}", titre=f"Coupe {lettre}-{lettre} : {sujet}", scene=scene))
    mini = mini_plan(piece.SOL, piece.PORTES, traits=[_trait(D, k) for k in lettres])
    return Vue("coupes", elements, fiche=f'<h3>Position</h3><div class="mini">{mini}</div>', outils=("zoom", "mesure"))


def vues(variante: str) -> dict[str, Vue]:
    M, D = VARIANTES[variante]
    return {
        "plan": _vue_plan(M, D),
        "coupes": _vue_coupes(M, D),
        "iso": Vue("iso", []),
        "camera": Vue("camera", []),
        "explication": Vue("explication", []),
    }
