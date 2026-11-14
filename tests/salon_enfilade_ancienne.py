"""Aide des tests de salon/enfilade : l'ancienne page (tests/fixtures/salon/salon-enfilade.html, sortie de l'ancien
générateur 3d/salon/enfilade.py au moment de sa suppression) et son texte.

`corrige` applique les quatre corrections d'affichage
du ruling 13 (« Six portes », « 3.8 », « 18.3 », « 1361 kg ») à un texte de l'ancienne page.
"""
import re
from html import unescape

from tests.outils import RACINE

_page = []

CORRECTIONS = {"Six portes": "Quatre portes", "3.8": "3,8", "18.3": "18,3", "1361 kg": "17 kg"}


def page() -> str:
    """L'ancienne page salon-enfilade.html, lue une fois."""
    if not _page:
        _page.append((RACINE / "tests/fixtures/salon/salon-enfilade.html").read_text(encoding="utf-8"))
    return _page[0]


def section(html: str, ancre: str) -> str:
    """Du `<h2 id="<ancre>"` au `<h2` suivant (ou à la fin)."""
    debut = html.index(f'<h2 id="{ancre}"')
    fin = html.find("<h2", debut + 1)
    return html[debut:] if fin < 0 else html[debut:fin]


def texte(html: str) -> str:
    """Texte lu : balises retirées, entités décodées, blancs réunis, point médian en virgule."""
    t = unescape(re.sub(r"<[^>]+>", "", html))
    return re.sub(r"\s+", " ", t).strip().replace(" · ", ", ")


_MORCEAU = re.compile(r'<p(?:\s(?![^>]*class="cap")[^>]*)?>(.*?)</p>|<li(?:\s[^>]*)?>(.*?)</li>'
                      r'|<h3(?:\s[^>]*)?>(.*?)</h3>', re.S)


def morceaux(html: str) -> list[str]:
    """`texte` de chaque `<p>` (sauf `class="cap"`), `<li>` et `<h3>`, dans l'ordre."""
    return [texte(next(g for g in m.groups() if g is not None)) for m in _MORCEAU.finditer(html)]


def corrige(t: str) -> str:
    for avant, apres in CORRECTIONS.items():
        t = t.replace(avant, apres)
    return t
