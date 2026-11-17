import re
from html import escape
import pytest
from commun.css_dessins import css_dessins
from commun.modele import Document, Variante, verifier
from pieces.sdb.meuble_bas import dessins as D, vues
from tests.outils import RACINE
from tests.sdb_anciennes import dessin, page_bas, sans_aria, texte

ORDRE = ["elevation", "iso", "iso-ouvert", "eclate", "plan", "coupe", "placard", "porte", "joue", "colonne",
         "colonne-dessus"]
V = vues.vues("")


@pytest.mark.parametrize("k", ORDRE)
def test_dessin_comme_l_ancienne_page(k):
    assert D.DESSINS[k]() == dessin(page_bas(), D.ARIA[k])


def test_cinq_vues_et_verifier():
    doc = Document("sdb", "meuble-bas", "Meuble bas", "construction", (Variante("", "Meuble bas", "V8.5", ()),), vues.vues)
    verifier(doc, V)
    assert list(V) == ["plans", "iso", "decoupe", "montage", "achats", "explication"]
    with pytest.raises(ValueError):
        vues.vues("autre")


def test_plans():
    p, i = V["plans"], V["iso"]
    assert [e.k for e in i.elements + p.elements] == ["iso", "iso-ouvert", "eclate"] + [k for k in ORDRE if k not in D.ISO]
    assert ORDRE == list(D.DESSINS)
    assert [e.nom for e in p.elements] == ["Élévation, vue depuis la salle de bain", "Plan", "Coupe par la machine",
        "Coupe par le placard", "Porte vue de face", "Joue vue de côté", "Colonne vue de face", "Colonne vue de dessus"]
    assert [e.nom for e in i.elements] == ["Vue iso", "Sans la porte", "Vue éclatée"]
    assert {e.titre for e in p.elements + i.elements} == {"Meuble bas"} and p.outils == ("zoom", "mesure")
    assert i.outils == ("zoom",) and 'href="#plans"' in i.fiche
    for e in p.elements + i.elements:
        assert e.scene.startswith('<svg data-mesure="non"') == (e.k in ("iso", "iso-ouvert", "eclate"))
        assert sans_aria(e.scene).replace(' data-mesure="non"', "") == sans_aria(D.DESSINS[e.k]())
    assert "114,4 × 60, dessus à 88,8" in p.fiche and 'href="#decoupe"' in p.fiche and 'href="#montage"' in p.fiche


def _caps():
    return {m.group(1): texte(m.group(2)) for m in re.finditer(
        r'aria-label="([^"]*)"[^>]*>.*?</svg>(?:</div>)?<p class="cap">(.*?)</p>', page_bas(), re.S)}


def test_alts():
    a, caps = vues.alts(), _caps()
    assert a["iso"] == D.ARIA["iso"]
    assert a["iso-ouvert"].startswith("Sans la porte : ") and a["eclate"].startswith("Vue éclatée : ")
    assert a["elevation"].startswith(D.ARIA["elevation"] + ". Le nord à gauche")
    assert sorted(caps.values()) == sorted(texte(t) for t in D.legendes().values())
    for e in V["plans"].elements + V["iso"].elements:
        assert f'aria-label="{escape(a[e.k], quote=True)}"' in e.scene


def test_aucune_description_visible():
    for cle, v in V.items():
        visible = texte(re.sub(r'aria-label="[^"]*"', "", "".join(e.scene for e in v.elements) + v.fiche))
        for t in D.legendes().values():
            assert texte(t) not in visible, (cle, t)


def test_classes_ont_une_regle():
    tous = [e.scene for e in V["plans"].elements + V["iso"].elements]
    css = css_dessins(D.CSS_DOCUMENT, tous, ".d-sdb")
    site = (RACINE / "commun/site.css").read_text(encoding="utf-8")
    regle = lambda c, t: re.search(rf"\.{re.escape(c)}(?![\w-])", t) is not None   # noqa: E731
    classes = {c for s in tous for m in re.findall(r'class="([^"]+)"', s) for c in m.split()}
    assert {"omasse", "olibre", "ofil", "otq", "ct", "nt", "ifen", "idec", "iapp"} <= classes
    assert sorted(c for c in classes if not regle(c, css) and not regle(c, site)) == []


def test_omel_du_meuble_bas_l_emporte():
    css = css_dessins(D.CSS_DOCUMENT, [e.scene for e in V["plans"].elements + V["iso"].elements], ".d-sdb")
    omel = [r for r in css.splitlines() if re.match(r"\.d-sdb \.omel\{", r)]
    assert omel[-1] == ".d-sdb .omel{fill:#fbfaf5;stroke:var(--ink);stroke-width:.25}"
    for interdit in ("JetBrains", "monospace", "var(--tile)", "ol.pose"):
        assert interdit not in D.CSS_DOCUMENT
