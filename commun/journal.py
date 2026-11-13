"""Journal des changements, lu dans les tableaux « Changements » des pages publiées."""
import re
from dataclasses import dataclass
from html import unescape
from pathlib import Path

from commun.modele import Changement, Document, Site


def _texte(h):
    return unescape(re.sub(r"\s+", " ", re.sub(r"<[^>]+>", "", h))).strip()


def _section_changements(html):
    """Contenu de la section <h2> « Changements », jusqu'au <h2> suivant."""
    parts = re.split(r"<h2[^>]*>(.*?)</h2>", html, flags=re.S)
    for i in range(1, len(parts), 2):
        if _texte(parts[i]) == "Changements":
            return parts[i + 1]
    return ""


def depuis_page(html: str) -> list[Changement]:
    """Lignes datées jj/mm/aaaa du premier tableau de la section « Changements »."""
    tables = re.findall(r"<table\b.*?</table>", _section_changements(html), flags=re.S)
    if not tables:
        return []
    res = []
    for tr in re.findall(r"<tr[^>]*>(.*?)</tr>", tables[0], flags=re.S):
        cellules = [_texte(c) for c in re.findall(r"<t[dh][^>]*>(.*?)</t[dh]>", tr, flags=re.S)]
        if len(cellules) >= 3 and re.match(r"\d\d/\d\d/\d{4}", cellules[1]):
            res.append(Changement(cellules[0], cellules[1][:10], cellules[2]))
    return res


def version_depuis_page(html: str) -> str | None:
    """Dernier morceau (après « · ») du premier `class="kicker"` qui commence par V."""
    for m in re.finditer(r'class="kicker"[^>]*>(.*?)</div>', html, flags=re.S):
        morceau = _texte(m.group(1)).split("·")[-1].strip()
        if morceau.startswith("V"):
            return morceau
    return None


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


def entrees(site: Site, racine: Path) -> list[EntreeJournal]:
    """Changements de tous les documents, du plus récent au plus ancien (ordre d'un même jour conservé)."""
    res = []
    for piece in site.pieces:
        for doc in piece.documents:
            if isinstance(doc, Document):
                seule = len(doc.variantes) == 1
                for i, var in enumerate(doc.variantes):
                    lien = f"{piece.id}/{doc.id}/" if i == 0 else f"{piece.id}/{doc.id}/{var.id}.html"
                    for c in var.changements:
                        res.append(EntreeJournal(piece.nom, doc.nom, None if seule else var.nom,
                                                 c.version, _iso(c.date), c.texte, lien))
            else:
                html = (racine / doc.page).read_text(encoding="utf-8")
                for c in depuis_page(html):
                    res.append(EntreeJournal(piece.nom, doc.nom, None, c.version, _iso(c.date), c.texte, doc.page))
    res.sort(key=lambda e: e.date_iso, reverse=True)
    return res
