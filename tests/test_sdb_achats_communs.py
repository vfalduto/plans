from pieces.sdb import achats_communs as AC
from tests.sdb_anciennes import ancien, corrige, morceaux, page_achats, section, texte

S = AC.deux_meubles({"bas": "#achats", "haut": "../../sdb-meuble-achats.html#haut-seul"})


def test_donnees_comme_modele_py():
    M = ancien("modele")
    assert (AC.MAGASIN, AC.RELEVE_V6, AC.BUDGET) == (M.MAGASIN, M.RELEVE_V6, M.BUDGET)


def test_deux_meubles():
    assert S.startswith("<h2>Les deux meubles</h2>") and round(AC.total_haut(), 2) == 179.82
    assert '<a href="#achats">Meuble bas</a>' in S and '<a href="../../sdb-meuble-achats.html#haut-seul">Meuble haut</a>' in S
    for montant in ("296,82 €", "179,82 €", "476,64 €", "428,33 €"):
        assert montant in S
    assert AC.prix(9) == "9,00 €" and AC.prix(296.82) == "296,82 €"


def test_rien_ne_se_perd_de_la_page_d_achats():
    vieux = section(page_achats(), "deux-meubles")
    note = page_achats().split('<p class="note">Sauf mention', 1)[1].split("</p>", 1)[0]
    for m in morceaux(vieux) + [texte("Sauf mention" + note)]:
        assert corrige(m) in texte(S), m
