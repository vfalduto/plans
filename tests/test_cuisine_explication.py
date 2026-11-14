"""Vue Explication de la cuisine/aménagement (pieces/cuisine/amenagement/explication.py) : tableaux et légendes de
l'ancienne page repris, tableaux qui défilent, liens locaux qui mènent à un fichier, sans point médian ni case."""
import html
import json
import re

import pytest

from pieces.cuisine.amenagement import explication as X
from tests.cuisine_anciens import FIXTURES
from tests.outils import RACINE

DEPUIS = "cuisine/amenagement/"
RENDUS_SITE = RACINE / "site" / "cuisine" / "amenagement" / "rendus"
TABLEAUX = json.loads((FIXTURES / "tableaux.json").read_text(encoding="utf-8"))
LEGENDES = json.loads((FIXTURES / "legendes.json").read_text(encoding="utf-8"))
PAGE = X.explication(RENDUS_SITE, DEPUIS)


def _texte(fragment):
    """Texte d'un fragment, espaces réduites ; l'espace entre deux balises (retour à la ligne du source) ne compte pas."""
    fragment = re.sub(r">\s+<", "><", fragment)
    return re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", "", fragment))).strip()


def _norm(fragment):
    return _texte(fragment).replace(" · ", ", ")


TEXTE = _texte(PAGE)


@pytest.mark.parametrize("cle", [k for k in TABLEAUX if k != "changements"])
def test_tableaux_repris(cle):
    table = TABLEAUX[cle]
    if cle == "materiaux":   # le bloc `materiaux` n'a pas d'en-tête : le corps, ligne pour ligne
        table = re.search(r"<tbody>.*</tbody>", table, re.S).group()
    assert _norm(table) in TEXTE


def test_tableaux_comptes():
    lignes = {k: len(re.findall(r"<tr", v.split("<tbody>")[1])) for k, v in TABLEAUX.items()}
    assert (lignes["materiaux"], lignes["contenu"], lignes["capacite"]) == (16, 27, 17)
    assert PAGE.count("<table") == 8
    assert "Salle de bains" in TEXTE


@pytest.mark.parametrize("cle", ["hauteur-pt-etude", "interrupteurs", "nfc", "rendus-methode", "materiaux", "contenu",
                                 "capacite"])
def test_legendes_reprises(cle):
    assert _norm(LEGENDES[cle]) in TEXTE
    apos = "'"
    attendu = LEGENDES[cle].replace(" · ", ", ").replace("&#x27;", apos)
    assert f'<p class="remarque">{attendu}</p>' in PAGE.replace("&#x27;", apos)   # remarque visible, balises gardées


def test_hauteur_pt_aria():
    (aria,) = re.findall(r'<svg[^>]*aria-label="([^"]*)"', PAGE)
    assert html.unescape(aria) == _norm(LEGENDES["hauteur-pt"])
    assert _norm(LEGENDES["hauteur-pt"]) not in TEXTE   # texte alternatif, pas à l'écran


def test_ordre_et_titres():
    titres = re.findall(r"<h2>(.*?)</h2>", PAGE)
    assert titres == ["Principe", "Hauteur du plan de travail (étude)", "Porte du cellier, Mantion Tango",
                      "Électricité", "Rendus", "Matériaux", "Contenu des rangements",
                      "Capacité : V11.34 → V13.30 et proposition 9 A"]
    assert re.findall(r"<h3>([^<]*)</h3>", PAGE.split("<h2>Électricité</h2>")[1].split("<h2>")[0]) == [
        "Quel interrupteur allume quoi", "Points", "Circuits proposés"]
    assert PAGE.startswith('<div class="tete-doc">')
    assert "Nouveau départ depuis la pièce vide." in PAGE
    assert PAGE.endswith('<p class="remarque">Repère : x vers l\'est depuis le mur ouest, y vers le sud depuis le mur '
                         'nord, z depuis le sol fini, en cm. Dimensions : pieces/cuisine/modele.py.</p>')
    assert "Plans détaillés" in PAGE.split("Mantion Tango</h2>")[1].split("<h2>")[0]


def test_liens():
    assert X.LIENS == (("maquette-3d.html", "Maquette 3D"), ("imprimable.html", "Version imprimable"),
                       ("../../cuisine-v13-porte-cellier.html", "Porte du cellier"))
    for h, n in X.LIENS:
        assert f'href="{h}">{n}</a>' in PAGE


def test_tableaux_defilent():
    assert PAGE.count("<table") == PAGE.count('<div class="defile"><table')
    assert PAGE.count('<div class="defile"><table') == PAGE.count("</table></div>")


def test_liens_locaux_existent():
    site = RACINE / "site" / DEPUIS
    liens = set(re.findall(r'(?:src|href)="([^"#?]+)', PAGE))
    locaux = {l for l in liens if not re.match(r"[a-z]+:", l)} - {"maquette-3d.html", "imprimable.html"}
    assert any("cuisine-sol-reference.png" in l for l in locaux) and "rendus/iso_so.jpg" in locaux
    for l in locaux:
        cible = (site / l).resolve()
        source = RACINE / cible.relative_to((RACINE / "site").resolve())
        assert cible.exists() or source.exists(), l


def test_sans_point_median_ni_mono():
    assert "·" not in PAGE and "&middot;" not in PAGE and "&#183;" not in PAGE
    assert 'class="mono"' not in PAGE and "<h1" not in PAGE
    assert 'class="cap"' not in PAGE and "<span class=\"mono" not in PAGE


def test_aucune_case_ni_texte_interdit():
    assert 'type="checkbox"' not in PAGE
    for t in ("Copier la liste", "À venir", "Lecture du plan", "Lecture de la coupe"):
        assert t not in PAGE, t


def test_chaque_classe_a_une_regle():
    """Les classes des tableaux et du texte de l'Explication ont une règle, dans les dessins ou la feuille commune."""
    from commun.css_dessins import css_dessins
    from pieces.cuisine.amenagement.dessins import CSS_DESSINS
    gardees = css_dessins(CSS_DESSINS, [PAGE], ".d-cuisine")
    commun = (RACINE / "commun" / "site.css").read_text(encoding="utf-8")
    sans_svg = re.sub(r"<svg.*?</svg>", "", PAGE, flags=re.S)
    for c in {c for a in re.findall(r'class="([^"]+)"', sans_svg) for c in a.split()}:
        assert re.search(rf"\.{re.escape(c)}\b", gardees) or re.search(rf"\.{re.escape(c)}\b", commun), c
