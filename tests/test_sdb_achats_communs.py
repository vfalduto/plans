from pieces.sdb import achats_communs as AC
from tests.sdb_anciennes import ancien, corrige, morceaux, page_achats, section, texte

S = AC.deux_meubles({"bas": "", "haut": "../meuble-haut/#achats"})


def test_donnees_comme_modele_py():
    M = ancien("modele")
    assert (AC.MAGASIN, AC.RELEVE_V6, AC.BUDGET) == (M.MAGASIN, M.RELEVE_V6, M.BUDGET)


def test_deux_meubles():
    assert S.startswith("<h2>Les deux meubles</h2>") and round(AC.total_haut(), 2) == 179.82
    assert "<td>Meuble bas</td>" in S and "meuble-bas" not in S and '<a href="../meuble-haut/#achats">Meuble haut</a>' in S
    for montant in ("296,82 €", "179,82 €", "476,64 €", "428,33 €"):
        assert montant in S
    assert AC.prix(9) == "9,00 €" and AC.prix(296.82) == "296,82 €"



def test_le_meuble_affiche_n_est_pas_un_lien():
    """Depuis la page d'un meuble, sa propre ligne est du texte ; l'autre meuble garde son lien (règle inversée)."""
    h = AC.deux_meubles({"bas": "../meuble-bas/#achats", "haut": ""})
    assert '<a href="../meuble-bas/#achats">Meuble bas</a>' in h and "<td>Meuble haut</td>" in h
    assert h.count("<a ") == 1 and S.count("<a ") == 1


def test_rien_ne_se_perd_de_la_page_d_achats():
    vieux = section(page_achats(), "deux-meubles")
    note = page_achats().split('<p class="note">Sauf mention', 1)[1].split("</p>", 1)[0]
    for m in morceaux(vieux) + [texte("Sauf mention" + note)]:
        assert corrige(m) in texte(S), m
