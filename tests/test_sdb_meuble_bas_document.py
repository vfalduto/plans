import subprocess
from commun.journal import entrees
from commun.modele import Changement
from pieces.sdb.meuble_bas import dessins, document, vues
from tests.outils import RACINE, charger_site

ANCRES = {"iso": "plans?k=iso", "structure": "explication", "placard": "explication", "f-placard": "plans?k=placard",
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
    assert (v.id, v.nom, v.version, v.figees) == ("", "Meuble bas", "V8.5", document.FIGEES)
    assert v.changements == tuple(Changement(*c) for c in document.CHANGEMENTS) and len(v.changements) == 16
    assert not hasattr(document, "CACHE_RENDU")


def test_site_declare_le_meuble_bas():
    (sdb,) = [p for p in charger_site().SITE.pieces if p.id == "sdb"]
    assert sdb.documents[0] is document.DOCUMENT and sdb.documents[1].page == "sdb-meuble-haut.html"


def test_redirection():
    (r,) = [r for r in charger_site().REDIRECTIONS if r.ancienne == "sdb-meuble-bas.html"]
    assert (r.cible, r.ancres, r.motifs, r.pages) == ("sdb/meuble-bas/", ANCRES, (),
                                                      {"changements": "sdb/meuble-bas/historique.html"})
    assert not [x for x in charger_site().REDIRECTIONS if x.ancienne == "sdb-meuble-achats.html"]


def test_journal_garde_seize_changements():
    lignes = [e for e in entrees(charger_site().SITE, RACINE) if (e.piece, e.document) == ("Salle de bain", "Meuble bas")]
    assert [e.version for e in lignes] == [c[0] for c in document.CHANGEMENTS]


def test_ancienne_page_et_generateur_retires():
    suivis = subprocess.run(["git", "ls-files"], cwd=RACINE, capture_output=True, text=True).stdout.split()
    for nom in ("sdb-meuble-bas.html", "3d/sdb/bas.py", "3d/sdb/test_bas.py"):
        assert nom not in suivis and not (RACINE / nom).exists(), nom
    for nom in ("sdb-meuble-achats.html", "3d/sdb/achats.py", "3d/sdb/haut.py", "3d/sdb/modele.py", "3d/sdb/cad.py"):
        assert nom in suivis, nom


def test_recettes():
    j = (RACINE / "justfile").read_text(encoding="utf-8")
    assert "sdb-meuble-bas:\n    python3 site.py sdb/meuble-bas\n" in j
    sdb = j.split("\nsdb:\n", 1)[1].split("\n\n", 1)[0]
    assert "bas.py" not in sdb and "python3 3d/sdb/achats.py" in sdb and "python3 site.py sdb/meuble-bas" in sdb
