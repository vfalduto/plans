"""Fichiers de référence de l'ancienne page cuisine-v13.html (tests/fixtures/cuisine/) : ils sont complets, ils
correspondent à ce que l'ancien générateur produit aujourd'hui, et les ancres suivent 3d/ancres.js."""
import html
import importlib.util
import json
import re

import pytest

from tests.cuisine_anciens import FIXTURES, ancien
from tests.outils import RACINE

_spec = importlib.util.spec_from_file_location("extraire_cuisine", FIXTURES / "extraire.py")
extraire = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(extraire)


def _texte(fragment):
    return html.unescape(re.sub(r"<[^>]+>", "", fragment))


def test_reference_complete():
    leg = json.loads((FIXTURES / "legendes.json").read_text(encoding="utf-8"))
    tab = json.loads((FIXTURES / "tableaux.json").read_text(encoding="utf-8"))
    assert len(leg) == 22 and len(tab) == 9
    assert sorted(p.stem for p in (FIXTURES / "dessins").glob("*.svg")) == sorted(
        ["plan", "coupe-a", "hauteur-pt", "coupe-b", "coupe-c", "plan-elec", "elevation-elec"])
    assert len(_texte(leg["plan"])) == 8439          # texte sans balises, entités décodées
    assert tab["changements"].count("<tr") == 91     # en-tête + 90 changements


def _racine(nom):
    """Texte d'un fichier de la racine ; saute si la bascule l'a supprimé."""
    chemin = RACINE / nom
    if not chemin.exists():
        pytest.skip(f"{nom} n'existe plus")
    return chemin.read_text(encoding="utf-8")


def test_reference_a_jour():
    plan = ancien("plan")                             # saute après la bascule
    page = _racine("cuisine-v13.html")
    assert plan.page(plan.lire_figees()) == page      # l'ancienne page se régénère à l'identique
    assert extraire.extraire(page) == extraire.lire(FIXTURES)   # mêmes morceaux que sur disque


def test_annexes_de_reference():
    assert ancien("imprimable").page() == (FIXTURES / "imprimable.html").read_text(encoding="utf-8")
    assert ancien("porte").page() == (FIXTURES / "porte-cellier.html").read_text(encoding="utf-8")
    assert (FIXTURES / "imprimable.html").read_text(encoding="utf-8") == _racine("cuisine-v13-imprimable.html")


def test_ancres():
    ids = [a["id"] for a in json.loads((FIXTURES / "ancres.json").read_text(encoding="utf-8"))]
    for a in ("plan", "coupe-a-a-mur-nord", "hauteur-du-plan-de-travail-etude", "coupe-b-b-mur-sud",
              "coupe-c-c-mur-est", "porte-du-cellier-mantion-tango", "electricite",
              "elevation-du-mur-nord-electricite", "rendus-3d", "materiaux", "contenu-des-rangements",
              "capacite-v11-34-v13-30-et-proposition-9-a", "changements", "changements-V11.49", "changements-V12.7"):
        assert a in ids, a
    assert any(i.endswith("-v11-49") for i in ids) and any(i.endswith("-v12-7") for i in ids)


def test_modele_et_rendu_de_reference():
    modele = ancien("modele")
    assert json.loads((FIXTURES / "modele.json").read_text(encoding="utf-8")) == json.loads(extraire.donnees_modele(modele))
    rendu = json.loads((FIXTURES / "rendu.json").read_text(encoding="utf-8"))
    assert sorted(rendu) == ["COUPES_ISO", "COUPES_ISO_NO"]
    if (extraire.ANCIEN / "rendu.py").exists():
        assert rendu == extraire.coupes_rendu()
    assert (FIXTURES / "maquette.html").read_text(encoding="utf-8") == _racine("cuisine-v13-maquette.html")
