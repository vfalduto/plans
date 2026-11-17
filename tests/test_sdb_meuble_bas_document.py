import subprocess
from commun.journal import entrees
from commun.modele import Changement
from pieces.sdb.meuble_bas import dessins, document, vues
from tests.outils import RACINE, charger_site

ANCRES = {"iso": "iso?k=iso", "structure": "explication", "placard": "explication", "f-placard": "plans?k=placard",
          "porte": "explication", "f-porte": "plans?k=porte", "pieds": "explication", "f-joue": "plans?k=joue",
          "finition": "decoupe", "colonne": "explication", "f-colonne": "plans?k=colonne",
          "f-colonne-dessus": "plans?k=colonne-dessus", "plan": "plans?k=plan", "f-plan": "plans?k=plan",
          "elevation": "plans?k=elevation", "f-face": "plans?k=elevation", "coupe": "plans?k=coupe",
          "f-coupe": "plans?k=coupe", "mesures": "explication"}


def test_document():
    d = document.DOCUMENT
    assert (d.piece, d.id, d.nom, d.type, d.css, d.generer, d.options) == \
        ("sdb", "meuble-bas", "Meuble bas", "construction", dessins.CSS_DOCUMENT, vues.vues, ())
    (v,) = d.variantes
    assert (v.id, v.nom, v.version, v.figees) == ("", "Meuble bas", "V8.7", document.FIGEES)
    assert v.changements == tuple(Changement(*c) for c in document.CHANGEMENTS) and len(v.changements) == 18
    assert not hasattr(document, "CACHE_RENDU")


def test_site_declare_le_meuble_bas():
    (sdb,) = [p for p in charger_site().SITE.pieces if p.id == "sdb"]
    assert sdb.documents[0] is document.DOCUMENT and sdb.documents[1].id == "meuble-haut"


def test_redirection():
    (r,) = [r for r in charger_site().REDIRECTIONS if r.ancienne == "sdb-meuble-bas.html"]
    assert (r.cible, r.ancres, r.motifs, r.pages) == ("sdb/meuble-bas/", ANCRES, (),
                                                      {"changements": "sdb/meuble-bas/historique.html"})


def test_journal_garde_seize_changements():
    lignes = [e for e in entrees(charger_site().SITE) if (e.piece, e.document) == ("Salle de bain", "Meuble bas")]
    assert [e.version for e in lignes] == [c[0] for c in document.CHANGEMENTS]


def test_ancienne_page_et_generateur_retires():
    suivis = subprocess.run(["git", "ls-files"], cwd=RACINE, capture_output=True, text=True).stdout.split()
    for nom in ("sdb-meuble-bas.html", "3d/sdb/bas.py", "3d/sdb/test_bas.py"):
        assert nom not in suivis and not (RACINE / nom).exists(), nom
    for nom in ("3d/sdb/modele.py", "3d/sdb/cad.py"):
        assert nom in suivis, nom


def test_recettes():
    j = (RACINE / "justfile").read_text(encoding="utf-8")
    # plus de recette par page : `just site sdb/meuble-bas` ; la recette FreeCAD ne lance que cad.py
    assert "\nsdb-meuble-bas:" not in j and "\nsite *args:\n    python3 site.py {{args}}" in j
    sdb = j.split("\nsdb-cad:\n", 1)[1].split("\n\n", 1)[0]
    assert "bas.py" not in sdb and "3d/sdb/cad.py" in sdb
