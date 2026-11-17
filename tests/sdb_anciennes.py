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
               " (« — » : non lu)": ", dans la note de l'article (sans note : non lu)"}


# V8.7 : plan de travail remonté de 88,8 à 92 ; les cotes qui en dépendent changent, le texte reste le même
PLAN_A_92 = {"étages égaux de 40,7": "étages égaux de 42,3", "3/4 de 40,7, soit 30,5": "3/4 de 42,3, soit 31,7",
             "61,4 % de l'étage": "59,1 % de l'étage", "Fond. 85 × 47,5": "Fond. 88,2 × 47,5",
             "Dimensions. 84,8 × 50,7": "Dimensions. 88 × 50,7", "38,7 de large et 10 de haut": "38,7 de large et 10,4 de haut",
             "à 34,3 et à 76,8 du sol": "à 35,5 et à 79,6 du sol", "2 cornes de 6 × 10.": "2 cornes de 6 × 10,4.",
             "et 32,5 entre les deux": "et 33,7 entre les deux", "soit 7,4 m.": "soit 7,6 m.",
             "B (85) + B (85)": "B (88,2) + B (88,2)", "B (85) + E (84,8)": "B (88,2) + E (88)", "C (85) + G (69)": "C (88,2) + G (65,8)",
             "cales de 40,7": "cales de 42,3", "18 de large et 69 de haut": "18 de large et 65,8 de haut",
             "Chaque étage, hauteur : 40,7": "Chaque étage, hauteur : 42,3",
             "dessous du meuble haut : 69,2": "dessous du meuble haut : 66", "Chant : 7,4 m": "Chant : 7,6 m",
             "à 100, 110 et 120 du sol": "à 103, 113 et 123 du sol",
             "Masse du meuble ≈ 41 kg, dont ≈ 4,1 kg": "Masse du meuble ≈ 42 kg, dont ≈ 4,3 kg"}
CHIFFRES_A_92 = {"84,8": "88", "85": "88,2", "69": "65,8"}      # cellules isolées des tableaux


def corrige(t: str) -> str:
    for a, b in CORRECTIONS.items():
        t = t.replace(a, b)
    for a, b in PLAN_A_92.items():
        t = t.replace(a, b)
    return CHIFFRES_A_92.get(t, t)
