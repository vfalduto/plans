import re
from pieces.sdb.meuble_bas import document, vues
from tests.outils import RACINE
from tests.sdb_anciennes import corrige, morceaux, page_bas, texte

V = vues.vues("")
S = V["explication"].elements[0].scene


def test_ordre_et_chiffres():
    assert re.findall(r"<h2>(.*?)</h2>", S) == ["Structure", "Colonne de prises", "Mesures", "À vérifier sur place"]
    assert re.findall(r"<h3>(.*?)</h3>", S) == ["Placard", "Porte", "Pieds", "Tenue", "Relevées",
                                                "Reprises des versions précédentes", "Ce qu'il reste"]
    assert re.findall(r"<dt>(.*?)</dt>", S) == ["115 × 62 à 68", "296,82 €", "9", "13"]


def test_corrections_et_a_verifier():
    assert "2,5 GPa" in S and "≈ 4,3 kg" in S and "2.5" not in S and "4.1 kg" not in S
    a = S.split("<h2>À vérifier sur place</h2>", 1)[1]
    assert a.count("<li>") == 3 and "Ces 7 cm d'écart" in texte(a)
    assert "160 sur le plan du meuble, 156 sur le plan de l'appartement" in texte(a)
    assert "à 69 du mur du fond sur le plan du meuble (relevé client), à 78 sur le plan de l'appartement" in texte(a)


def test_liens_et_repere():
    assert 'href="../../archives/sdb-meuble-v4-bas.html"' in S and "3d/sdb" not in S and "pieces/sdb/piece.py" in S
    assert "Repère : origine à l'angle nord-ouest intérieur, x vers l'est, y vers le sud, z depuis le sol, cotes en cm." \
        in texte(S)


def _tout():
    return texte("".join(e.nom + e.scene + v.fiche for v in V.values() for e in v.elements))


def test_rien_ne_se_perd():
    """Chaque paragraphe, puce, titre et cellule de l'ancienne page est dans une vue, sauf les retraits du tableau."""
    corps = page_bas().split("<main", 1)[1]
    retires = ("Repère : origine",)          # note finale : son repère est vérifié plus haut, ses chemins sont retirés
    for m in morceaux(corps):
        if not m.startswith(retires):
            m = m.replace("À confirmer : le ", "Le ")    # la note devient le premier point à vérifier (ruling 14)
            assert corrige(m) in _tout(), m


def test_liens_externes_gardes():
    vieux = set(re.findall(r'href="(https://www\.ikea[^"]+)"', page_bas()))
    tout = "".join(e.scene for v in V.values() for e in v.elements)
    assert len(vieux) == 3 and vieux <= set(re.findall(r'href="(https?://[^"]+)"', tout))


def test_versions_figees():
    f = document.FIGEES
    assert len(f) == 11 and len({v for v, _ in f}) == 11 and len({c for _, c in f}) == 11
    for _, chemin in f:
        assert (RACINE / "site" / chemin).is_file(), chemin
    assert ("Liste d'achats V8.5", "archives/sdb-meuble-achats-v8.5.html") in f and ("V6.2", "archives/sdb-meuble-v4-bas.html") in f


def test_sans_point_median_ni_chasse_fixe():
    assert "·" not in S and "mono" not in S and 'class="scroll"' not in S and 'class="note"' not in S
