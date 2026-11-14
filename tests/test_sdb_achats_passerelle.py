from tests.outils import RACINE
from tests.sdb_anciennes import ancien, page_achats


def test_achats_py_lit_le_nouveau_module():
    src = (RACINE / "3d/sdb/achats.py").read_text(encoding="utf-8")
    assert "import bas" not in src and "from pieces.sdb.meuble_bas import modele as B" in src


def test_pages_du_haut_et_des_achats_identiques():
    lire = lambda nom: (RACINE / nom).read_text(encoding="utf-8")    # noqa: E731
    assert ancien("achats").page() == lire("sdb-meuble-achats.html") == page_achats()
    assert ancien("haut").page() == lire("sdb-meuble-haut.html")
