"""Pages de redirection des anciennes adresses (commun/redirections.py)."""
import json
import re

from commun.construction import construire
from commun.modele import Site
from commun.redirections import Redirection, page_redirection
from outils import balises

R = Redirection(
    "ancienne.html", "essai/amenagement/",
    {"plan": "plan", "debit": "explication"},
    ((r"^coupe-([a-d])-", "coupes?k={1}"),),
)


def test_page_redirection():
    html = page_redirection(R, "dossier/ancienne.html")
    refresh = [m for m in balises(html, "meta") if m.get("http-equiv") == "refresh"]
    assert len(refresh) == 1 and refresh[0]["content"] == "0; url=../essai/amenagement/"
    liens = [a for a in balises(html, "a") if a.get("href") == "../essai/amenagement/"]
    assert liens, "lien visible vers la cible"
    assert "location.replace" in html and "location.hash" in html
    donnees = json.loads(re.search(r'<script type="application/json" id="traduction">(.*?)</script>', html, re.S)[1])
    assert donnees["cible"] == "../essai/amenagement/"
    assert donnees["ancres"]["plan"] == "plan"
    assert donnees["motifs"] == [[r"^coupe-([a-d])-", "coupes?k={1}"]]


def test_page_redirection_depuis_la_racine():
    html = page_redirection(R, "ancienne.html")
    assert 'content="0; url=essai/amenagement/"' in html


def test_page_redirection_echappe_le_texte():
    r = Redirection("a.html", "x/", {"</script>": "plan"})
    assert "</script>\"" not in page_redirection(r, "a.html").split('id="traduction">')[1].split("</script>")[0]


def test_construire_ecrit_la_redirection(tmp_path):
    racine = tmp_path / "racine"
    racine.mkdir()
    (racine / "ancienne.html").write_text("<p>ancienne page</p>")
    (racine / "autre.html").write_text("<p>autre page</p>")
    site = Site(())
    sortie = racine / "site"
    construire(site, (R,), racine, sortie)
    page = (sortie / "ancienne.html").read_text()
    assert "ancienne page" not in page and 'http-equiv="refresh"' in page
    assert (sortie / "autre.html").read_text() == "<p>autre page</p>"
    # une seconde construction ne change rien
    construire(site, (R,), racine, sortie)
    assert (sortie / "ancienne.html").read_text() == page
