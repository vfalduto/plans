"""Bascule de la cuisine/aménagement : le Document dans site.py, les trois anciennes adresses redirigées (ancres de la
page courante, des blocs figés, inconnues), la page de la porte du cellier relinkée, l'ancien générateur supprimé."""
import json
import re

import pytest

from commun.modele import Document, Passerelle
from pieces.cuisine.amenagement import document as cuisine_amenagement
from tests.cuisine_anciens import FIXTURES, ancien
from tests.outils import RACINE, charger_site

ANCRES = json.loads((FIXTURES / "ancres.json").read_text(encoding="utf-8"))
HISTORIQUE = "cuisine/amenagement/historique.html"
ARCHIVES = {"V11.49": "archive/cuisine-v11.49.html", "V12.7": "archive/cuisine-v12.7.html"}


def _redirections():
    return {r.ancienne: r for r in charger_site().REDIRECTIONS}


def _traduire(r, ancre):
    """Ce que fait commun/redirections.SCRIPT : (page, fragment) ; autre page, puis ancre exacte, puis motifs (groupe
    en capitale), sinon la cible sans fragment."""
    if ancre in r.pages:
        return r.pages[ancre], ""
    if ancre in r.ancres:
        return r.cible, r.ancres[ancre]
    for motif, gabarit in r.motifs:
        m = re.search(motif, ancre)
        if m:
            return r.cible, re.sub(r"\{(\d+)\}", lambda g: (m.group(int(g[1])) or "").upper(), gabarit)
    return r.cible, ""


def test_document_dans_site():
    (cuisine,) = [p for p in charger_site().SITE.pieces if p.id == "cuisine"]
    (amenagement,) = cuisine.documents
    assert amenagement is cuisine_amenagement.DOCUMENT and isinstance(amenagement, Document)
    assert not any(isinstance(d, Passerelle) for d in cuisine.documents)   # « Porte du cellier » : page non migrée


def test_trois_redirections():
    r = _redirections()
    assert r["cuisine-v13.html"].cible == "cuisine/amenagement/"
    assert (r["cuisine-v13-imprimable.html"].cible, r["cuisine-v13-imprimable.html"].ancres) == \
        ("cuisine/amenagement/imprimable.html", {})
    assert r["cuisine-v13-maquette.html"].cible == "cuisine/amenagement/maquette-3d.html"


@pytest.mark.parametrize("ancre,attendu", [
    ("plan", ("cuisine/amenagement/", "plan")),
    ("br", ("cuisine/amenagement/", "plan")),
    ("coupe-a-a-mur-nord", ("cuisine/amenagement/", "coupes?k=A")),
    ("coupe-b-b-mur-sud", ("cuisine/amenagement/", "coupes?k=B")),
    ("coupe-c-c-mur-est", ("cuisine/amenagement/", "coupes?k=C")),
    ("hauteur-du-plan-de-travail-etude", ("cuisine/amenagement/", "explication")),
    ("porte-du-cellier-mantion-tango", ("cuisine/amenagement/", "explication")),
    ("electricite", ("cuisine/amenagement/", "plan?k=elec")),
    ("elevation-du-mur-nord-electricite", ("cuisine/amenagement/", "coupes?k=elec")),
    ("rendus-3d", ("cuisine/amenagement/", "iso")),
    ("materiaux", ("cuisine/amenagement/", "explication")),
    ("contenu-des-rangements", ("cuisine/amenagement/", "explication")),
    ("capacite-v11-34-v13-30-et-proposition-9-a", ("cuisine/amenagement/", "explication")),
    ("changements", (HISTORIQUE, "")),
])
def test_redirection_ancres(ancre, attendu):
    assert _traduire(_redirections()["cuisine-v13.html"], ancre) == attendu


def test_redirection_ancres_figees():
    r = _redirections()["cuisine-v13.html"]
    figees = [a["id"] for a in ANCRES if a["bloc"] != "courante"]
    assert {"changements-V11.49", "changements-V12.7", "br-V11.49", "br-V12.7"} <= set(figees)
    for a in [a for a in ANCRES if a["bloc"] != "courante"] + [{"id": v, "bloc": v} for v in ARCHIVES]:
        assert _traduire(r, a["id"]) == (ARCHIVES[a["bloc"]], ""), a["id"]
    # chaque ancre du bloc courant a sa traduction (aucune n'est laissée à la vue par défaut)
    for a in ANCRES:
        if a["bloc"] == "courante":
            assert _traduire(r, a["id"]) != (r.cible, ""), a["id"]


def test_redirection_ancre_inconnue():
    r = _redirections()["cuisine-v13.html"]
    assert _traduire(r, "inconnue") == ("cuisine/amenagement/", "")
    assert _traduire(r, "") == ("cuisine/amenagement/", "")


def test_porte_liens_reecrits():
    attendu = (FIXTURES / "porte-cellier.html").read_text(encoding="utf-8")
    attendu = attendu.replace('<a class="back" href="cuisine-v13.html">', '<a class="back" href="cuisine/amenagement/">')
    attendu = attendu.replace('de la <a href="cuisine-v13.html">', 'de la <a href="cuisine/amenagement/#explication">')
    page = ancien("porte").page()
    assert page == attendu and "cuisine-v13.html" not in page
    assert (RACINE / "cuisine-v13-porte-cellier.html").read_text(encoding="utf-8") == page


def test_anciens_fichiers_supprimes():
    for chemin in ("cuisine-v13.html", "cuisine-v13-imprimable.html", "cuisine-v13-maquette.html",
                   "cuisine-v13-maquette", "3d/v13/plan.py", "cuisine-v13-3d", "site/cuisine-v13-3d",
                   "site/cuisine-v13-maquette"):
        assert not (RACINE / chemin).exists(), chemin
    for chemin in ("3d/v11", "3d/v12", "3d/cuisine_a.py", "cuisine-plan.html", "cuisine-couleurs.html", "cuisine-3d",
                   "3d/v13/porte.py", "cuisine-v13-porte-cellier.html", "archive", "images"):
        assert (RACINE / chemin).exists(), chemin
