"""Le document du meuble haut, sa bascule : redirections, journal, recettes, ancienne page et générateurs retirés."""
import subprocess

from commun.journal import entrees
from pieces.sdb.meuble_haut import dessins, document, vues
from tests.outils import RACINE, charger_site
from tests.sdb_anciennes import ancien

ANCRES = {"iso": "iso?k=iso", "montage": "montage", "comment-percer": "montage", "fixer-haut": "montage",
          "fiches": "decoupe", "decoupe": "decoupe", "achats": "achats", "materiaux": "explication"}
ANCIENNES_ANCRES = ("iso", "montage", "etape-8", "etape-9", "etape-10", "op-8-1", "op-8-4", "op-9-3", "op-10-1",
                    "op-10-3", "comment-percer", "fixer-haut", "fiches", "decoupe", "achats", "materiaux",
                    "changements")


def test_document():
    d = document.DOCUMENT
    assert (d.piece, d.id, d.nom, d.type, d.css, d.generer, d.options) == \
        ("sdb", "meuble-haut", "Meuble haut", "construction", dessins.CSS_DOCUMENT, vues.vues, ())
    (v,) = d.variantes
    assert (v.id, v.nom, v.version, v.figees) == ("", "Meuble haut", "V6.5", document.FIGEES)
    assert v.figees[0] == ("V6.2", "archives/sdb-meuble-v4-haut.html")
    assert len(v.changements) == 3 and [c.version for c in v.changements] == ["V6.5", "V6.4", "V6.3"]


def test_changements_comme_modele_py():
    """V6.4 et V6.3 à l'identique de modele.py (figé à la V6.4) ; la V6.5 (onglet Iso) s'ajoute en tête."""
    M = ancien("modele")
    assert [tuple(c) for c in document.CHANGEMENTS[1:]] == [c for c in M.CHANGEMENTS if c[0] in ("V6.4", "V6.3")]
    assert M.VERSION == "V6.4" and document.VERSION == document.CHANGEMENTS[0][0] == "V6.5"
    assert document.CHANGEMENTS[0][1] == "17/11/2026" and "Iso" in document.CHANGEMENTS[0][2]


def test_archives_existent():
    for _, chemin in document.FIGEES:
        assert (RACINE / "site" / chemin).is_file(), chemin


def test_site_declare_le_meuble_haut():
    (sdb,) = [p for p in charger_site().SITE.pieces if p.id == "sdb"]
    assert [d.id for d in sdb.documents] == ["meuble-bas", "meuble-haut"] and sdb.documents[1] is document.DOCUMENT


def test_redirection_du_haut():
    (r,) = [r for r in charger_site().REDIRECTIONS if r.ancienne == "sdb-meuble-haut.html"]
    assert (r.cible, r.ancres, r.motifs, r.pages) == (
        "sdb/meuble-haut/", ANCRES, ((r"^etape-\d+$", "montage"), (r"^op-\d+-\d+$", "montage")),
        {"changements": "sdb/meuble-haut/historique.html"})


def test_redirection_des_achats():
    (r,) = [r for r in charger_site().REDIRECTIONS if r.ancienne == "sdb-meuble-achats.html"]
    assert r.cible == "sdb/meuble-haut/" and r.ancres["haut-seul"] == r.ancres["deux-meubles"] == "achats"
    assert r.ancres[""] == "achats" and r.pages["bas"] == "sdb/meuble-bas/#achats"
    assert r.pages["changements"] == "sdb/meuble-bas/historique.html"


def test_journal_garde_deux_changements():
    """Les deux changements de modele.py restent au journal, sous la V6.5 (onglet Iso)."""
    lignes = [e for e in entrees(charger_site().SITE) if (e.piece, e.document) == ("Salle de bain", "Meuble haut")]
    assert [e.version for e in lignes] == ["V6.5", "V6.4", "V6.3"]
    assert [(e.version, e.texte) for e in lignes] == [(c.version, c.texte) for c in document.DOCUMENT.variantes[0].changements]


def test_anciennes_pages_et_generateurs_retires():
    suivis = subprocess.run(["git", "ls-files"], cwd=RACINE, capture_output=True, text=True).stdout.split()
    for nom in ("sdb-meuble-haut.html", "sdb-meuble-achats.html", "3d/sdb/haut.py", "3d/sdb/achats.py"):
        assert nom not in suivis and not (RACINE / nom).exists(), nom
    # ce qui reste de 3d/sdb/ : le modèle V6 (lu par le meuble haut, cad.py et explorations/), pages, plan, montage,
    # cotes et calepinage (explorations/ et le modèle FreeCAD)
    for nom in ("3d/sdb/modele.py", "3d/sdb/cad.py", "3d/sdb/pages.py"):
        assert nom in suivis, nom


def test_recettes():
    j = (RACINE / "justfile").read_text(encoding="utf-8")
    assert "\nsdb-meuble-haut:" not in j and "\nsdb:" not in j
    sdb = j.split("\nsdb-cad:\n", 1)[1].split("\n\n", 1)[0]
    assert "haut.py" not in sdb and "achats.py" not in sdb and "3d/sdb/cad.py" in sdb


def test_le_bas_mene_au_nouveau_haut():
    from pieces.sdb.meuble_bas import vues as bas
    achats = bas.vues("")["achats"].elements[0].scene
    assert 'href="../meuble-haut/#achats"' in achats and "sdb-meuble-achats.html" not in achats
