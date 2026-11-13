"""Pages de redirection des anciennes adresses (commun/redirections.py)."""
import json
import re

from commun.construction import construire
from commun.modele import Site
from commun.redirections import Redirection, page_redirection
from outils import balises, charger_site

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


def test_page_redirection_vers_une_autre_page():
    """`pages` : une ancre qui mène à une autre page que la cible, adresse écrite depuis l'ancienne page."""
    r = Redirection("ancienne.html", "essai/amenagement/b.html",
                    pages={"changements": "essai/amenagement/historique.html"})
    html = page_redirection(r, "dossier/ancienne.html")
    donnees = json.loads(re.search(r'<script type="application/json" id="traduction">(.*?)</script>', html, re.S)[1])
    assert donnees["pages"] == {"changements": "../essai/amenagement/historique.html"}
    assert donnees["cible"] == "../essai/amenagement/b.html"


# ------------------------------------------------------------------ redirections de site.py

def _traduire(r: Redirection, ancre: str) -> str:
    """Le fragment que donne le script de la page pour `ancre` : ancre exacte, puis motifs (`RegExp.exec` cherche
    n'importe où, comme `re.search`), `{n}` remplacé par le groupe n en majuscules ; sinon aucun."""
    if ancre in r.ancres:
        return r.ancres[ancre]
    for motif, gabarit in r.motifs:
        m = re.compile(motif).search(ancre)
        if m:
            return re.sub(r"\{(\d+)\}", lambda g: (m.group(int(g[1])) or "").upper(), gabarit)
    return ""


def test_motifs_de_site_py():
    redirections = charger_site().REDIRECTIONS
    assert redirections
    for r in redirections:
        for motif, _ in r.motifs:
            re.compile(motif)
        assert _traduire(r, "coupe-b-b-mur-de-la-salle-de-bain") == "coupes?k=B", r.ancienne


def test_redirections_de_l_entree():
    """Les deux anciennes pages de l'entrée : mêmes ancres (plus « Différences avec la V4.3 » chez Victor), chacune vers
    sa variante ; Changements vers l'historique."""
    principale, victor = charger_site().REDIRECTIONS
    assert (principale.ancienne, principale.cible) == ("entree-amenagement.html", "entree/amenagement/")
    assert (victor.ancienne, victor.cible) == ("entree-amenagement-victor.html", "entree/amenagement/victor.html")
    explication = ("principe", "achats-ikea-penderie", "materiaux", "points-a-verifier")
    ancres = {"plan": "plan", "vues-3d": "iso", **dict.fromkeys(explication, "explication")}
    assert principale.ancres == ancres
    assert victor.ancres == {**ancres, "differences-avec-la-v4-3": "explication"}
    for r in (principale, victor):
        assert r.pages == {"changements": "entree/amenagement/historique.html"}
        assert _traduire(r, "coupe-a-a-mur-nord") == "coupes?k=A"
        assert _traduire(r, "coupe-d-d-mur-ouest-de-l-entree") == "coupes?k=D"
        assert _traduire(r, "inconnue") == ""
