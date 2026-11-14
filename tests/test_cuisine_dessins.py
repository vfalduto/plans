"""Les sept dessins de la cuisine/aménagement (pieces/cuisine/amenagement/dessins.py) : ceux de l'ancienne page, sans
point médian, aria-label de l'appelant, zones du plan insérées, et leur CSS sans les règles de page."""
import re

import pytest

from pieces.cuisine.amenagement import dessins
from tests.cuisine_anciens import FIXTURES

ARIA = "Légende de l'appelant"
DESSINS = {
    "plan": lambda: dessins.plan_svg(ARIA),
    "coupe-a": lambda: dessins.coupe_a(ARIA),
    "coupe-b": lambda: dessins.coupe_b(ARIA),
    "coupe-c": lambda: dessins.coupe_c(ARIA),
    "elevation-elec": lambda: dessins.coupe_elec_nord(ARIA),
    "plan-elec": lambda: dessins.plan_elec_svg(ARIA),
    "hauteur-pt": lambda: dessins.hauteur_pt_svg(ARIA),
}
MEDIANS = ("cellier · ", "brut · ", "tableau noir · aimants", "L2 · LED")


def _normaliser(svg):
    """Points médians remplacés par des virgules (liste du brief), sans aria-label, role ni zones du plan."""
    for m in MEDIANS:
        svg = svg.replace(m, m.replace(" · ", ", "))
    tete, reste = svg.split(">", 1)
    tete = re.sub(r' aria-label="[^"]*"', "", tete, count=1)
    tete = re.sub(r' role="[^"]*"', "", tete, count=1)
    reste = re.sub(r'<rect class="zone"[^>]*/>', "", reste)
    return tete + ">" + reste


@pytest.mark.parametrize("nom", DESSINS)
def test_dessins_identiques_a_la_reference(nom):
    svg = DESSINS[nom]()
    attendu = (FIXTURES / "dessins" / f"{nom}.svg").read_text(encoding="utf-8")
    assert svg.startswith("<svg ") and svg.endswith("</svg>")
    assert f'aria-label="{ARIA}"' in svg.split(">", 1)[0]
    assert _normaliser(svg) == _normaliser(attendu)


def test_zones_du_plan():
    zones = '<rect class="zone" x="0" y="0" width="10" height="10"/>'
    svg = dessins.plan_svg(ARIA, zones)
    assert svg.endswith(zones + "</svg>")
    assert ' role="group"' in svg.split(">", 1)[0]
    assert ' role="img"' in dessins.plan_svg(ARIA).split(">", 1)[0]


def test_sans_point_median():
    for nom, d in DESSINS.items():
        assert "·" not in d(), nom
    assert "·" not in dessins.REGLE_LEGENDE
    assert "cellier, 1,44 m²" in dessins.plan_svg(ARIA)
    assert "L2, LED" in dessins.coupe_elec_nord(ARIA)


def test_portes_par_defaut():
    svg = dessins.plan_svg(ARIA)
    assert '<g class="vt" data-vt="entree" data-etat="ferme">' in svg
    assert '<g class="vt" data-vt="cellier" data-etat="mi">' in svg


def test_regle_175_seule_visible():
    for svg in (dessins.coupe_a(ARIA), dessins.coupe_c(ARIA)):
        assert 'data-t="175"' in svg and 'data-t="180"' in svg
    css = dessins.CSS_DESSINS
    assert '.regle[data-t="175"]{display:inline}' in css
    assert ".regle{display:none}" in css
    assert not re.search(r"\bhtml\b", css)
    assert (dessins.COUPE_A, dessins.COUPE_B, dessins.COUPE_C) == (90, 150, 315)


def test_transparence():
    css = dessins.CSS_DESSINS
    (decl,) = re.findall(r"(?:^|[}\s])\.trp\{([^}]*)\}", css)
    assert "fill:none" in decl and "stroke-dasharray:4 2" in decl
    assert ".transp" not in css
    assert not re.search(r"\.trp-lbl[^{]*\{[^}]*display:none", css)


def test_css_sans_chasse_fixe_ni_sombre():
    css = dessins.CSS_DESSINS
    for interdit in ("Mono", "monospace", "prefers-color-scheme", 'data-theme="dark"', "@media"):
        assert interdit not in css, interdit
    for cls in (".dimt", ".trit", ".diagt"):
        (decl,) = re.findall(rf"{re.escape(cls)}\{{([^}}]*)\}}", css)
        assert "font-variant-numeric:tabular-nums" in decl, cls
    for page in (".kicker", ".toc", ".vbar", ".pbar", ".impr", ".tog", ".mono", ".cap", ".fig"):
        assert not re.search(rf"{re.escape(page)}\b", css), page


@pytest.mark.parametrize("nom", DESSINS)
def test_aria_obligatoire(nom):
    """Plus de texte alternatif par défaut (celui de l'ancien générateur) : l'appelant le donne toujours."""
    fonction = {"plan": dessins.plan_svg, "coupe-a": dessins.coupe_a, "coupe-b": dessins.coupe_b,
                "coupe-c": dessins.coupe_c, "elevation-elec": dessins.coupe_elec_nord,
                "plan-elec": dessins.plan_elec_svg, "hauteur-pt": dessins.hauteur_pt_svg}[nom]
    with pytest.raises(TypeError):
        fonction()


def test_reste_de_l_ancien_generateur_retire():
    assert not hasattr(dessins, "coupe_a_seule") and not hasattr(dessins, "coupe_c_seule")
    assert ":root" not in dessins.CSS_DESSINS   # les jetons sont ceux de commun/site.css
