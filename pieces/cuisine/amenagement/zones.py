"""Meubles touchables du plan de la cuisine/aménagement.

Chaque meuble a un id stable (`#plan?k=<id>`), un titre tiré de son étiquette dans le modèle, et un motif : une
expression régulière sur les noms des blocs de `modele.MEUBLES + modele.ENVELOPPE`. L'emprise de la zone et les cotes
de sa fiche sont l'union de ces blocs, jamais un nombre recopié ; la fiche reprend les lignes de `modele.CONTENU` qui
décrivent le meuble.
"""
import re
from collections.abc import Mapping
from html import escape

from commun.blocs import Zone, cotes_meuble
from pieces.cuisine import modele as M

_COORDS = ("x0", "x1", "y0", "y1", "z0", "z1")


def _caissons(role):
    """Ids et étiquettes des caissons d'un rôle, d'ouest en est ou du nord au sud (ordre du modèle)."""
    return [(b.nom.removeprefix("caisson_"), b.etiq) for b in M.MEUBLES if b.role == role]


def _titre(etiq, generique):
    """« B2, four » pour l'étiquette « B2 four » ; « B1, meuble bas » pour une étiquette sans équipement."""
    code, _, reste = etiq.partition(" ")
    return f"{code}, {reste or generique}"


_BAS, _HAUTS, _COLONNES = _caissons("caisson"), _caissons("caisson_haut"), _caissons("colonne")

# (id, titre, motif, coupe, iso), dans l'ordre de l'inventaire (INV §8) ; porte d'entrée et tableau noir, au mur sud :
# coupe B et iso NO (l'inventaire disait A et SO, où ils ne sont pas)
MEUBLES_PLAN = tuple(
    [(i, _titre(e, "meuble bas"), rf"(socle|caisson|facade)_{i}(_\w+)?", "A", "so") for i, e in _BAS]
    + [(i, _titre(e, "meuble haut"), rf"(caisson|facade)_{i}(_\w+)?", "A", "so") for i, e in _HAUTS]
    + [(i, _titre(e, "colonne"), rf"(?!.*fileur)\w+_{i}", "C", "so") for i, e in _COLONNES]
    + [
        ("etageres", "Étagères murales", r"etagere_mur_\d+", "A", "so"),
        ("banquette", "Banquette", r"banquette_(assise|dossier)|tiroir_banquette_\d+", "B", "no"),
        ("table", "Table", r"(plateau|chant)_vera|(pied|embase)_table", "B", "no"),
        ("chaise", "Chaise", r"(pied_chaise_\d+_\d+|(assise|dossier)_chaise_\d+)", "B", "no"),
        ("etagere-banquette", "Étagère au-dessus de la banquette", r"etagere_banquette", "B", "no"),
        ("rayonnage-nord", "Rayonnage du cellier", r"(montant|etag)_nord_\d+", "A", "no"),
        ("entretien", "Étagère de l'entretien", r"etag_entretien_\d+", "C", "no"),
        ("balais", "Balais", r"(crochet|manche|tete)_balai_\d+", "C", "no"),
        ("seau", "Seau", r"seau", "C", "no"),
        ("aspirateur", "Aspirateur", r"aspirateur_\w+", "C", "no"),
        ("porte-cellier", "Porte du cellier", r"cellier_pliante", "C", "no"),
        ("porte-entree", "Porte d'entrée", r"entree_vantail", "B", "no"),
        ("tableau-noir", "Tableau noir et zone aimantée", r"tableau_noir|zone_aimantee", "B", "no"),
    ])

# Meubles accrochés au mur au-dessus d'un autre (meubles hauts, étagères) : leur zone n'est que la moitié de leur
# emprise côté mur (mur nord ou sud), pour que le meuble du dessous, recouvert par elle, reste touchable ; la fiche
# garde les cotes du meuble entier
_MURAUX = {**{i: "n" for i, _ in _HAUTS}, "etageres": "n", "etagere-banquette": "s"}

# Lignes de CONTENU des meubles sans étiquette, par début de libellé ; celles des caissons commencent par leur code
# (« B3, … », « C2 »)
_CONTENU_DE = {
    "etageres": ("Étagères à gauche",),
    "banquette": ("Banquette",),
    "rayonnage-nord": ("Cellier nord, sol", "Cellier nord, tablette"),
    "entretien": ("Cellier, étagère", "Cellier, même étagère"),
    "balais": ("Cellier, mur du WC",),
    "seau": ("Cellier, angle sud-est",),
    "aspirateur": ("Cellier nord, sous la",),
}


def emprise(motif: str) -> dict:
    """Union des blocs dont le nom correspond au motif : x0, x1, y0, y1, z0, z1 en cm."""
    blocs = [b for b in M.MEUBLES + M.ENVELOPPE if re.fullmatch(motif, b.nom)]
    if not blocs:
        raise ValueError(f"aucun bloc pour le motif {motif!r}")
    return {c: (min if c.endswith("0") else max)(getattr(b, c) for b in blocs) for c in _COORDS}


def rectangle(id_: str, e: Mapping) -> tuple[float, float, float, float]:
    """Le rectangle touchable d'un meuble (x0, y0, x1, y1) : son emprise, ou sa bande murale (_MURAUX)."""
    x0, y0, x1, y1 = e["x0"], e["y0"], e["x1"], e["y1"]
    mur = _MURAUX.get(id_)
    if mur == "n":
        y1 = (y0 + y1) / 2
    elif mur == "s":
        y0 = (y0 + y1) / 2
    return x0, y0, x1, y1


def _lignes_contenu(id_, titre):
    if id_ in dict(_BAS + _HAUTS + _COLONNES):  # caisson : son code d'étiquette
        code = titre.partition(",")[0]
        return [(m, c) for m, c in M.CONTENU if m == code or m.startswith(f"{code}, ")]
    return [(m, c) for m, c in M.CONTENU if m.startswith(_CONTENU_DE.get(id_, ()))]


def zones(textes: Mapping[str, str]) -> list[Zone]:
    """Une zone par meuble de MEUBLES_PLAN, écrites dans cet ordre (une zone recouvre celles d'avant) ; `textes` :
    HTML de la page par id, avant les lignes de CONTENU."""
    sortie = []
    for id_, titre, motif, coupe, iso in MEUBLES_PLAN:
        e = emprise(motif)
        morceaux = [textes.get(id_, "")] + [f"{escape(m)} : {escape(c)}" for m, c in _lignes_contenu(id_, titre)]
        sortie.append(Zone(id_, titre, rectangle(id_, e), cotes_meuble(e),
                           "<br>".join(t for t in morceaux if t), coupe, iso))
    return sortie
