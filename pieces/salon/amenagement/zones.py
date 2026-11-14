"""Meubles touchables du plan du salon/aménagement.

Chaque meuble a un id stable (`#plan?k=<id>`), un titre, et un motif : une expression régulière sur les noms des blocs
de `document.MEUBLES + document.ENVELOPPE`. L'emprise de la zone et les cotes de sa fiche sont l'union de ces blocs,
jamais un nombre recopié. La table, la table basse et le siège n'ont pas la même emprise selon les options Table et
Siège : une zone par état (même id, `si` différent), la fiche suit l'état. Le texte de chaque fiche est un passage de
l'ancien paragraphe sous le plan (textes.py).
"""
import re
from collections.abc import Mapping

from commun.blocs import Zone, cotes_meuble
from pieces.salon.amenagement import options as O
from pieces.salon.amenagement import textes
from pieces.salon.amenagement import document as M
from pieces.salon.meubles import cote as c

_COORDS = ("x0", "x1", "y0", "y1", "z0", "z1")

# (id, titre, motif, jetons, coupe, iso, ids de passages), dans l'ordre où les zones s'écrivent : une zone recouvre
# celles d'avant. Les étagères sont au-dessus de l'enfilade, sur la même emprise : leur zone est la bande du mur
# (voir _MURAUX), pour que l'enfilade, qu'elle recouvre, reste touchable ; la fiche garde les cotes entières.
MEUBLES_PLAN = (
    ("enfilade", "Enfilade", r"enfilade_.*", (), "A", "se", ("enfilade",)),
    ("etageres", "Étagères sur montants", r"(montant|etagere)_\d+", (), "A", "se", ("etageres",)),
    ("canape", "Canapé", r"canape_.*", (), "C", "se", ("canape",)),
    ("desserte", "Desserte et platine vinyle", r"(desserte_.*|vinyles_\d+)", (), "B", "se", ("desserte",)),
    ("chaises", "Chaises", r"chaise_f_\d+(_dos)?", (O.QUOTIDIEN,), "C", "no", ("table-quotidien",)),
    ("chaises", "Chaises", r"chaise_o_\d+(_dos)?", (O.OUVERTE,), "C", "no", ("table-ouverte",)),
    ("table", "Table", r"table_(plateau|pied)_f.*", (O.QUOTIDIEN,), "C", "no", ("table-quotidien",)),
    ("table", "Table", r"table_(plateau|pied)_o.*", (O.OUVERTE,), "C", "no", ("table-ouverte",)),
    ("table-basse", "Table basse", r"table_basse_f.*", (O.QUOTIDIEN,), "C", "se", ("table-basse",)),
    ("table-basse", "Table basse", r"table_basse_o", (O.OUVERTE,), "C", "se", ("table-basse", "rangement-table-ouverte")),
    ("siege", "Siège DYVLINGE", r"dyvlinge_f_.*", (O.QUOTIDIEN, O.DYVLINGE), "C", "se", ("siege",)),
    ("siege", "Siège DYVLINGE", r"dyvlinge_o_.*", (O.OUVERTE, O.DYVLINGE), "C", "se", ("siege",)),
    ("siege", "Siège, chilienne", r"chilienne_(toile|dos)", (O.QUOTIDIEN, O.CHILIENNE), "C", "se", ("siege",)),
    ("siege", "Siège, chilienne", r"chilienne_pliee", (O.OUVERTE, O.CHILIENNE), "C", "se", ("siege", "rangement-table-ouverte")),
    ("meuble-bas", "Meuble bas", r"console_.*", (), "D", "no", ("meuble-bas",)),
    ("ecran", "Écran", r"ecran", (), "D", "no", ("ecran",)),
    ("projecteur", "Vidéoprojecteur", r"projecteur", (), "D", "no", ("projecteur",)),
    ("clim", "Clim", r"clim", (), "D", "no", ("clim",)),
)

# bande du mur : (côté du mur, épaisseur) de la zone d'un meuble que sa fiche garde entier (l'étagère au-dessus de
# l'enfilade, l'écran fin contre le mur sud) ; l'étagère garde la moitié ouest de son emprise
_MURAUX = {"etageres": ("o", 0.5), "ecran": ("s", 6)}


def _passage(id_: str) -> str:
    """Le corps HTML d'un passage de textes.PASSAGES."""
    for i, _, corps in textes.PASSAGES:
        if i == id_:
            return corps
    raise KeyError(id_)


def emprise(motif: str) -> dict:
    """Union des blocs dont le nom correspond au motif : x0, x1, y0, y1, z0, z1 en cm."""
    blocs = [b for b in M.MEUBLES + M.ENVELOPPE if re.fullmatch(motif, b.nom)]
    if not blocs:
        raise ValueError(f"aucun bloc pour le motif {motif!r}")
    return {k: (min if k.endswith("0") else max)(getattr(b, k) for b in blocs) for k in _COORDS}


def rectangle(id_: str, e: Mapping) -> tuple[float, float, float, float]:
    """Le rectangle touchable d'un meuble (x0, y0, x1, y1) : son emprise, ou sa bande murale (_MURAUX)."""
    x0, y0, x1, y1 = e["x0"], e["y0"], e["x1"], e["y1"]
    mur = _MURAUX.get(id_)
    if mur is None:
        return x0, y0, x1, y1
    cote_mur, part = mur
    if cote_mur == "o":
        x1 = x0 + (x1 - x0) * part
    elif cote_mur == "s":
        y0 = y1 - part
    return x0, y0, x1, y1


def cotes_de(id_: str, e: Mapping) -> str:
    """Les cotes de la fiche : celles de l'emprise ; l'écran n'a que son image (1 cm d'épaisseur sans intérêt)."""
    if id_ == "ecran":
        return f'image {c(M.ECRAN["l"])} × {c(M.ECRAN["h"])}, bas à {c(M.ECRAN["bas"])}'
    return cotes_meuble(e)


def zones() -> list[Zone]:
    """Une zone par ligne de MEUBLES_PLAN, écrites dans cet ordre."""
    sortie = []
    for id_, titre, motif, jetons, coupe, iso, passages in MEUBLES_PLAN:
        e = emprise(motif)
        texte = " ".join(_passage(p) for p in passages)
        sortie.append(Zone(id_, titre, rectangle(id_, e), cotes_de(id_, e), texte, coupe, iso, si=" ".join(jetons)))
    return sortie
