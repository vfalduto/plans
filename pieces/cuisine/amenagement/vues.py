"""Vues de la cuisine/aménagement (une seule variante, d'id vide).

`vues(variante)` rend le dictionnaire des vues du type « aménagement ». Plan (meublé, puis électrique) et coupes
viennent de dessins.py ; la légende qui suivait chaque dessin de l'ancienne page (3d/v13/plan.py) en est devenue le
texte alternatif, recalculée ici depuis le modèle. Iso et Caméra sont les rendus de `site/cuisine/amenagement/rendus/`
(titre et texte de `modele.RENDUS` en alt). Explication : explication.py.
"""
import dataclasses
import re
from html import unescape
from pathlib import Path

from commun.blocs import (Coupe, Lieu, fiche_position, figure_rendu, points_iso, rendu, vue_camera, vue_coupes,
                          vue_iso, vue_lecture, vue_plan, zones_svg)
from commun.modele import Element, Vue
from pieces.cuisine import modele as M
from pieces.cuisine import piece
from pieces.cuisine.amenagement import dessins, explication, legende, zones
from pieces.cuisine.dessin import f

RENDUS_SITE = Path(__file__).resolve().parents[3] / "site" / "cuisine" / "amenagement" / "rendus"
LIEU = Lieu(piece.SOL_ET_CELLIER, piece.PORTES, "Position dans la cuisine")
CAMERAS_PRISES = ("entree", "fenetre", "banquette", "dos_cellier", "cellier")   # ordre de l'ancienne galerie
# clé de l'ancienne page (M.RENDUS) -> clé du rendu
CLES_RENDUS = {"iso": "iso_so", "iso_nuit": "iso_so_nuit"}

_X = [x for x, _ in piece.SOL_ET_CELLIER]
_Y = [y for _, y in piece.SOL_ET_CELLIER]
ENVELOPPE = (min(_X), min(_Y), max(_X), max(_Y))
# trait de chaque coupe sur le mini-plan, borné par l'étendue de la cuisine et du cellier ; l'élévation électrique est
# la coupe A
TRAITS = {"A": ((min(_X), dessins.COUPE_A), (max(_X), dessins.COUPE_A)),
          "B": ((min(_X), dessins.COUPE_B), (max(_X), dessins.COUPE_B)),
          "C": ((dessins.COUPE_C, min(_Y)), (dessins.COUPE_C, max(_Y))),
          "elec": ((min(_X), dessins.COUPE_A), (max(_X), dessins.COUPE_A))}


def _texte(fragment: str) -> str:
    """Texte d'une légende pour un attribut : balises ôtées, entités lues, point médian remplacé par une virgule."""
    return re.sub(r"\s+", " ", unescape(re.sub(r"<[^>]+>", "", fragment))).strip().replace(" · ", ", ")


# ------------------------------------------------------------------ légendes de l'ancienne page (3d/v13/plan.py)
def legende_plan_elec() -> str:
    return ("Proposition. Les traits tiretés relient chaque interrupteur à la lumière qu'il commande. Hauteurs (h) à "
            "l'axe du boîtier, depuis le sol fini. Les prises au fond des meubles (contour tireté) sont placées à côté "
            "de l'appareil, jamais derrière lui, pour pouvoir le débrancher en ouvrant le meuble voisin : four et plaque "
            "dans B1, lave-vaisselle sous sa niche, micro-ondes et frigo au-dessus de la leur. Au-dessus du plan de "
            "travail, rien au-dessus de la plaque ni de l'évier ; les prises de crédence sont à h 110, à mi-hauteur "
            f"entre le plan (h {M.PT_Z1}) et les hauts (h {M.HAUT_Z0}).")


def legende_elevation_elec() -> str:
    return ("Même coupe que A-A. Boîtiers de la crédence (P1 → P3) et S2 à h 110 ; au fond des meubles, en tireté : P4 "
            "(hotte, dans H1), P5 (four) et P6 (sortie de câble de la plaque) dans B1 ; à droite, P12 dans le cellier.")


def legende_coupe_a() -> str:
    return (f"Coupe à y {dessins.COUPE_A}, regard vers le nord. Pieds et plinthe {M.SOCLE} (METOD), caissons bas de "
            f"{M.CAISSON_H - M.SOCLE} h {M.SOCLE} → {M.CAISSON_H}, plan de travail 4 (h {M.CAISSON_H} → {M.PT_Z1}), "
            f"meubles hauts h {M.HAUT_Z0} → {M.HAUT_Z1}, fileur de {M.H - M.HAUT_Z1} jusqu'au plafond ({M.H}). "
            f"<b>Ruban LED</b> (jaune) sous H1 → H{M.N_HAUTS}, vers l'avant, pour éclairer le plan de travail. "
            "<b>Façades</b> : tout en tiroirs en bas ; en haut (V13.24), caissons METOD de 80 à deux portes battantes de "
            f"40 superposées : porte basse (h {M.HAUT_Z0} → {M.HAUT_JOINT}) pour le quotidien, porte haute (h "
            f"{M.HAUT_JOINT} → {M.HAUT_Z1}) pour le rare ; les traits épais sont les poignées. <b>Règle à droite</b> "
            "(V13.23) : hauteurs de rangement pour la personne qui cuisine (bouton Taille : 1,75 m, 1,80 m ou masquée), "
            "le quotidien dans la zone d'or, rien au-dessus de la main levée sans escabeau ; en tireté rouge, coude, "
            f"épaule, yeux et main levée estimés par les proportions moyennes du corps. {dessins.REGLE_LEGENDE}")


def legende_coupe_b() -> str:
    E, B = M.ENTREE, M.ETAGERE_BANQ
    return (f"Coupe à y {dessins.COUPE_B}, regard vers le sud : l'est est à gauche. <b>Porte d'entrée</b> : baie "
            f'{f(E["x1"] - E["x0"])} × {E["h"]}, porte à galandage, vantail {f(E["vantail"])} × {E["h"]} (fermé), qui '
            f'rentre à droite dans le caisson du doublage (poche {f(E["poche"][1] - E["poche"][0])}). Sur le caisson, '
            "<b>tableau noir</b> h 120 → 200 et <b>zone aimantée</b> h 70 → 118. Banquette (de profil, contre la "
            "fenêtre) et table au fond, devant le bas de mur en chêne et le papier peint Hermione, avec l'étagère P25 "
            f'au-dessus (h {f(B["z0"])} → {f(B["z1"])}) et l\'enceinte audio ; à gauche, la colonne C2 coupée (C1 '
            "derrière). À droite, la fenêtre coupée ; au centre, la baie d'entrée et son vantail fermé.")


def legende_coupe_c() -> str:
    return (f"Coupe à x {dessins.COUPE_C}, regard vers l'est : le nord est à gauche. Au fond, la cloison du cellier (x "
            f"320 → 327), et dans son prolongement la porte du cellier fermée ({M.PORTE_TITRE}), dessinée en "
            "transparence (tireté) avec son dormant et son linteau (bouton au-dessus de la coupe : transparente ou "
            "normale), pour montrer le fond du cellier : le ballon. Puis, contre le mur du WC (x "
            f"{f(M.X_MUR_EST)}), les colonnes P{M.P_CAISSON + M.FACADE}, pieds et plinthe {M.SOCLE_COL}, armoires "
            f"METOD {M.COL_Z1 - M.SOCLE_COL}, dessus à {M.COL_Z1} (les meubles hauts finissent à {M.HAUT_Z1}), fileur "
            f"de {M.H - M.COL_Z1} jusqu'au plafond : <b>C2</b> réfrigérateur intégrable (niche 178, porte h "
            f"{M.SOCLE_COL} → {M.FRIGO_Z1}), porte de rangement au-dessus ; <b>C1</b> un tiroir (h {M.SOCLE_COL} → "
            f"{M.LV_Z0}), lave-vaisselle intégré en hauteur (h {M.LV_Z0} → {M.MO_Z0}), micro-ondes encastrable (niche "
            f"38, h {M.MO_Z0} → {M.MO_Z1}), porte de rangement au-dessus ; à droite, le décroché et le mur sud coupé.")


def aria_plan() -> str:
    """aria-label de l'ancien plan."""
    return (f"Plan vu de dessus, pièce vide, {M.N_BAS} meubles bas et {M.N_HAUTS} meubles hauts de 60 au mur "
            "nord")


def alts() -> dict[str, str]:
    """Texte alternatif de chaque rendu : titre, texte et version de `M.RENDUS`, comme sous l'image de l'ancienne page."""
    return {CLES_RENDUS.get(v, v): _texte(f"{titre}, {texte} (rendu {M.RENDUS_VERSION[v]})")
            for v, titre, texte in M.RENDUS}


# ------------------------------------------------------------------ vues
def _vue_plan() -> Vue:
    zs = zones.zones(legende.textes_par_meuble())
    vue = vue_plan(dessins.plan_svg(aria_plan(), zones_svg(zs)), zs, legende.legende_html())
    elec = Element(k="elec", nom="Électricité", titre="Plan électrique",
                   scene=dessins.plan_elec_svg(_texte(legende_plan_elec())))
    return dataclasses.replace(vue, elements=[*vue.elements, elec])


def _vue_coupes() -> Vue:
    coupes = [Coupe("A", "A mur nord", "Coupe A-A : mur nord", dessins.coupe_a(_texte(legende_coupe_a())), TRAITS["A"]),
              Coupe("B", "B mur sud", "Coupe B-B : mur sud", dessins.coupe_b(_texte(legende_coupe_b())), TRAITS["B"]),
              Coupe("C", "C mur est", "Coupe C-C : mur est", dessins.coupe_c(_texte(legende_coupe_c())), TRAITS["C"]),
              Coupe("elec", "Électricité, mur nord", "Élévation du mur nord : électricité",
                    dessins.coupe_elec_nord(_texte(legende_elevation_elec())), TRAITS["elec"])]
    vue = vue_coupes(coupes, LIEU)
    # les pastilles de la règle des hauteurs (coupes A et C) : dans la fiche de l'élément
    elements = [dataclasses.replace(e, fiche=dessins.REGLE_LEGENDE) if e.k in ("A", "C") else e for e in vue.elements]
    return dataclasses.replace(vue, elements=elements)


def _vue_iso(variante: str) -> Vue:
    points = points_iso(ENVELOPPE)
    textes = alts()
    vue = vue_iso(RENDUS_SITE, variante, LIEU, points, textes)
    r = rendu(RENDUS_SITE, variante, "iso_so_nuit")
    nuit = Element(k="so-nuit", nom="SO nuit", titre="Vue iso SO, de nuit",
                   scene=figure_rendu(r, textes["iso_so_nuit"]), actif=r.existe)
    elements = [*vue.elements, nuit]
    # un cône par élément rendu ; celui de la nuit au point du coin SO
    cones = [(e.k, *points["so" if e.k == "so-nuit" else e.k], False) for e in elements if e.actif]
    return dataclasses.replace(vue, elements=elements, fiche=fiche_position(LIEU, cones=cones))


def _vue_camera(variante: str) -> Vue:
    cameras = {c.id: c for c in piece.CAMERAS}
    return vue_camera(RENDUS_SITE, variante, LIEU, [cameras[k] for k in CAMERAS_PRISES], alts())


def vues(variante: str) -> dict[str, Vue]:
    if variante != "":
        raise ValueError(f"cuisine/amenagement : variante inconnue « {variante} »")
    return {
        "plan": _vue_plan(),
        "coupes": _vue_coupes(),
        "iso": _vue_iso(variante),
        "camera": _vue_camera(variante),
        "explication": vue_lecture("explication", explication.explication(RENDUS_SITE, "cuisine/amenagement/")),
    }
