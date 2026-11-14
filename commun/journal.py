"""Journal des changements de tous les documents (liste CHANGEMENTS de chaque variante)."""
from dataclasses import dataclass

from commun.modele import Site


@dataclass(frozen=True)
class EntreeJournal:
    piece: str
    document: str
    variante: str | None
    version: str
    date_iso: str
    texte: str
    lien: str


def _iso(date):
    j, m, a = date.split("/")
    return f"{a}-{m}-{j}"


def entrees(site: Site) -> list[EntreeJournal]:
    """Changements de tous les documents, du plus récent au plus ancien (ordre d'un même jour conservé)."""
    res = []
    for piece in site.pieces:
        for doc in piece.documents:
            for i, var in enumerate(doc.variantes):
                lien = f"{piece.id}/{doc.id}/" if i == 0 else f"{piece.id}/{doc.id}/{var.id}.html"
                for c in var.changements:
                    res.append(EntreeJournal(piece.nom, doc.nom, None if len(doc.variantes) == 1 else var.nom,
                                             c.version, _iso(c.date), c.texte, lien))
    res.sort(key=lambda e: e.date_iso, reverse=True)
    return res
