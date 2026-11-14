import re
from pieces.sdb.meuble_bas import modele as B, vues
from tests.sdb_anciennes import corrige, entre, morceaux, page_achats, page_bas, section, texte

V = vues.vues("")


def _s(cle): return V[cle].elements[0].scene


def test_decoupe():
    s = _s("decoupe")
    assert s.startswith("<h2>Pièces</h2>") and s.split("<tbody>")[1].count("<tr>") == 7 and "<h2>Finition</h2>" in s
    assert "B à G : trois tablettes" in texte(s) and "Tablette 3, 250 × 50 : C (85) + G (69)" in texte(s)
    for m in morceaux(entre(page_bas(), '<h3 id="finition">', "<h3>Montage</h3>")):
        assert corrige(m) in texte(s), m


def test_montage():
    s = _s("montage")
    assert [h for h in re.findall(r"<h2>(.*?)</h2>", s)] == ["Montage", "Pose de la colonne"]
    assert s.count('<ol class="etapes"') == 2 and len(vues.etapes_montage()) == 13 and len(vues.pose_colonne()) == 5
    assert "<b>Mesurer l'alcôve</b>" in s and "Outils à réunir" not in s
    for m in morceaux(entre(page_bas(), "<h3>Montage</h3>", "<h3>Tenue</h3>")
                      + entre(page_bas(), "<h3>Pose de la colonne</h3>", '<h2 id="plan">')):
        assert corrige(m) in texte(s), m


def test_achats():
    s = _s("achats")
    assert re.findall(r"<h2>(.*?)</h2>", s) == ["Meuble bas", "Les deux meubles"]
    table = s.split("<tbody>")[1].split("</tbody>")[0]
    assert table.count("<tr>") == 16 and "Total du meuble bas" in table and "296,82 €" in table
    for nom, ref, q, pu, st in B.prix():
        assert ref in table and nom.replace("'", "&#x27;") in table
    assert "2 × 16,50 €, stock : 25" in table and "stock : 50" in table
    assert "Le détail est dans la liste d'achats." in texte(s) and "sdb-meuble-achats.html#bas" not in s
    # le titre « Achats » de l'ancienne page est devenu l'onglet ; chaque paragraphe est pris entier
    vieux = entre(page_bas(), "<p>Le meuble bas entier", "</p>") + "</p>" \
        + section(page_achats(), "bas").split("<div", 1)[0] + "<p>" + section(page_achats(), "bas").split('<p class="note">', 1)[1]
    for m in morceaux(vieux):
        assert corrige(m) in texte(s), m


def test_sans_point_median_ni_chasse_fixe():
    for cle in ("decoupe", "montage", "achats"):
        assert "·" not in _s(cle) and "mono" not in _s(cle), cle
