"""Outils des tests de la salle de bain : les anciennes pages (copies figées), leurs dessins, leurs textes, et les
anciens modules de 3d/sdb/ (chargés par pieces.sdb.ancien ; absents, les tests qui les lisent sautent)."""
import html as _html
import re

import pytest

from pieces.sdb import ancien as _ancien
from tests.outils import RACINE

FIXTURES = RACINE / "tests" / "fixtures" / "sdb"


def page_bas() -> str:
    return (FIXTURES / "sdb-meuble-bas.html").read_text(encoding="utf-8")


def page_achats() -> str:
    return (FIXTURES / "sdb-meuble-achats.html").read_text(encoding="utf-8")


def ancien(nom: str):
    try:
        return _ancien.charger(nom)
    except FileNotFoundError:
        pytest.skip(f"3d/sdb/{nom}.py n'existe plus")


def dessin(html: str, aria: str) -> str:
    """Le <svg> de `html` dont l'aria-label est `aria`."""
    attr = f'aria-label="{_html.escape(aria, quote=True)}"'
    i = html.index(attr)
    return html[html.rindex("<svg", 0, i):html.index("</svg>", i) + len("</svg>")]


def sans_aria(svg: str) -> str:
    return re.sub(r' aria-label="[^"]*"', "", svg, count=1)


def entre(html: str, debut: str, fin: str | None = None) -> str:
    i = html.index(debut)
    return html[i:] if fin is None else html[i:html.index(fin, i + len(debut))]


def section(html: str, ancre: str) -> str:
    """De l'élément id="<ancre>" au <h2 suivant."""
    j = html.index(f'id="{ancre}"')
    i = html.rindex("<", 0, j)
    k = html.find("<h2", j)
    return html[i:] if k < 0 else html[i:k]


def texte(html: str) -> str:
    return " ".join(_html.unescape(re.sub(r"<[^>]+>", "", html)).split())


_HORS = re.compile(r'<section id="changements">.*?</section>|<nav\b.*?</nav>|<style\b.*?</style>|<script\b.*?</script>',
                   re.S)
_MORCEAU = re.compile(r"<(p|li|h3|th|td)(\s[^>]*)?>(.*?)</\1>", re.S)


def morceaux(html: str) -> list[str]:
    """Texte de chaque <p> (sauf class="cap"), <li>, <h3>, <th>, <td>, hors des changements, du menu, du style."""
    res = []
    for m in _MORCEAU.finditer(_HORS.sub("", html)):
        if m.group(1) == "p" and 'class="cap"' in (m.group(2) or ""):
            continue
        t = texte(m.group(3))
        if t:
            res.append(t)
    return res


# erreurs d'affichage de l'ancienne page, corrigées depuis le modèle (ruling 15), et la phrase du stock (ruling 11)
CORRECTIONS = {"2.5 GPa": "2,5 GPa", "≈ 4.1 kg": "≈ 4,1 kg", "B à F :": "B à G :",
               "(« — » : non lu)": ", dans la note de l'article (sans note : non lu)"}


def corrige(t: str) -> str:
    for a, b in CORRECTIONS.items():
        t = t.replace(a, b)
    return t
