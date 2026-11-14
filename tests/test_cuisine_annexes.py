"""Pages annexes de la cuisine/aménagement : version imprimable et maquette 3D, à côté du document
(cuisine/amenagement/imprimable.html, maquette-3d.html) ; celles de l'ancienne page, liens rebasés et points médians
remplacés, rien d'autre."""
import hashlib
import posixpath
import re

from commun.construction import construire
from commun.modele import Piece, Site
from pieces.cuisine.amenagement import document, imprimable
from tests.cuisine_anciens import FIXTURES
from tests.outils import RACINE

IMPRIMABLE = "cuisine/amenagement/imprimable.html"
MAQUETTE = "cuisine/amenagement/maquette-3d.html"
MODELE_JS = RACINE / "site/cuisine/amenagement/maquette-3d/modele.js"


def _sans_median(page):
    return page.replace(" · ", ", ")


def test_imprimable_identique_hors_liens():
    attendu = (FIXTURES / "imprimable.html").read_text(encoding="utf-8")
    attendu = _sans_median(attendu.replace('href="favicon.svg"', 'href="../../favicon.svg"')
                           .replace('href="apple-touch-icon.png"', 'href="../../apple-touch-icon.png"')
                           .replace('href="cuisine-v13.html"', 'href="./"'))
    page = imprimable.page()
    assert page == attendu
    assert "·" not in page
    assert imprimable.page(IMPRIMABLE) == page


def test_maquette_identique_hors_liens():
    attendu = (FIXTURES / "maquette.html").read_text(encoding="utf-8")
    attendu = _sans_median(attendu.replace('href="favicon.svg"', 'href="../../favicon.svg"')
                           .replace('href="apple-touch-icon.png"', 'href="../../apple-touch-icon.png"')
                           .replace('href="cuisine-v13.html"', 'href="./"')
                           .replace('src="cuisine-v13-maquette/modele.js"', 'src="maquette-3d/modele.js"'))
    page = document.maquette(MAQUETTE)
    assert page == attendu
    assert "·" not in page and "cdn.jsdelivr.net/npm/three@0.170.0" in page


def test_annexes_declarees():
    doc = document.construire_document()
    assert [a.nom for a in doc.annexes] == ["imprimable.html", "maquette-3d.html"]


def test_annexes_liens_locaux(tmp_path):
    """Chaque src/href local des deux annexes, résolu depuis leur adresse sous site/, existe (modele.js compris) :
    dans le site construit, ou dans site/ (fichiers qui ne se régénèrent pas : modele.js)."""
    doc = document.construire_document()
    sortie = tmp_path / "site"
    construire(Site((Piece("cuisine", "Cuisine", (doc,)),)), (), RACINE, sortie)
    for depuis in (IMPRIMABLE, MAQUETTE):
        page = (sortie / depuis).read_text(encoding="utf-8")
        liens = re.findall(r'(?:src|href)="([^"#?]+)', page)
        locaux = [l for l in liens if not re.match(r"[a-z]+:", l)]
        assert locaux, depuis
        for lien in locaux:
            chemin = posixpath.normpath(posixpath.join(posixpath.dirname(depuis), lien))
            chemin = chemin + "/index.html" if lien.endswith("/") else chemin
            assert (sortie / chemin).exists() or (RACINE / "site" / chemin).exists(), (depuis, lien)


# SHA-256 de site/cuisine/amenagement/maquette-3d/modele.js, régénéré en V13.31 (just cuisine-amenagement-maquette)
SHA_MODELE_JS = "da1d7c94b64156672979e5de6d8c4273213ce867b06f00425a248cf69a3d1038"


def test_modele_js_repris():
    assert hashlib.sha256(MODELE_JS.read_bytes()).hexdigest() == SHA_MODELE_JS
