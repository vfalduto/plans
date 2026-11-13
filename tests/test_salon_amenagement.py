"""Salon, aménagement (pieces/salon/amenagement/document.py) : reprise de 3d/salon/modele.py et de plan.py."""
import pytest

from pieces.salon.amenagement import document as amenagement
from pieces.salon.enfilade import document as enfilade
from pieces.salon.etageres import document as etageres
from tests.outils import RACINE
from tests.salon_anciens import FIXTURES, MODELE, ancien, changements_de_la_page, norm, verifier_dessins, verifier_empreinte


@pytest.mark.parametrize("ancien_nom", sorted(MODELE["amenagement"]))
def test_constantes_du_modele(ancien_nom):
    nom = MODELE["amenagement"][ancien_nom]
    assert norm(getattr(amenagement, nom)) == norm(getattr(ancien("modele"), ancien_nom))


@pytest.mark.parametrize("nom", ["COUPE_A", "COUPE_B", "COUPE_C", "COUPE_D"])
def test_coupes_de_plan(nom):
    assert getattr(amenagement, nom) == getattr(ancien("plan"), nom)


def test_fonctions_du_modele():
    M = ancien("modele")
    for args in ((100, 200, 45, "f", 0), (296, 180, -90, "o", 3)):
        assert norm(amenagement.chaise_blocs(*args)) == norm(M.chaise_blocs(*args))
    assert amenagement._chaises_table(90, 12) == M._chaises_table(90, 12)
    assert norm(amenagement._dyvlinge("f", 322, 108)) == norm(M._dyvlinge("f", 322, 108))


def test_emprises_une_seule_source():
    """Le plan du salon prend l'enfilade et les étagères dans leur document, bloc pour bloc."""
    n_en, n_et = len(enfilade.BLOCS), len(etageres.BLOCS)
    assert amenagement.MEUBLES[:n_en] == enfilade.BLOCS
    assert amenagement.MEUBLES[n_en:n_en + n_et] == etageres.BLOCS
    assert amenagement.ENFILADE is enfilade.ENFILADE and amenagement.ETAGERES is etageres.ETAGERES


def test_changements():
    """Même liste que modele.py (comparée plus haut) et que le tableau de la page, dans le même ordre."""
    assert len(amenagement.CHANGEMENTS) == 28
    assert [(v, d, " ".join(t.split())) for v, d, t in amenagement.CHANGEMENTS] == \
        changements_de_la_page("salon-v4.html")
    assert amenagement.CHANGEMENTS[0][0] == amenagement.VERSION


def test_versions_figees_dans_archive():
    for version, chemin in amenagement.FIGEES_ANCIENNES:
        html = (RACINE / chemin).read_text(encoding="utf-8")
        assert f"Salon · {version} ·" in html


def test_dessins_de_reference():
    verifier_dessins("salon-v4.html")
    assert (FIXTURES / "amenagement-plan-du-salon.svg").read_text(encoding="utf-8") == ancien("plan").plan_svg()


def test_empreinte_des_rendus():
    verifier_empreinte("pieces.salon.piece", "pieces.salon.amenagement.document")
