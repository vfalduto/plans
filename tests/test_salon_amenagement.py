"""Salon, aménagement (pieces/salon/amenagement/document.py) : emprises, changements, versions figées, empreinte."""
from pieces.salon.amenagement import document as amenagement
from pieces.salon.enfilade import document as enfilade
from pieces.salon.etageres import document as etageres
from tests.outils import RACINE, verifier_empreinte


def test_emprises_une_seule_source():
    """Le plan du salon prend l'enfilade et les étagères dans leur document, bloc pour bloc."""
    n_en, n_et = len(enfilade.BLOCS), len(etageres.BLOCS)
    assert amenagement.MEUBLES[:n_en] == enfilade.BLOCS
    assert amenagement.MEUBLES[n_en:n_en + n_et] == etageres.BLOCS
    assert amenagement.ENFILADE is enfilade.ENFILADE and amenagement.ETAGERES is etageres.ETAGERES


def test_changements():
    assert len(amenagement.CHANGEMENTS) == 28
    assert amenagement.CHANGEMENTS[0][0] == amenagement.VERSION


def test_versions_figees_dans_archive():
    for version, chemin in amenagement.FIGEES_ANCIENNES:
        html = (RACINE / "site" / chemin).read_text(encoding="utf-8")
        assert f"Salon · {version} ·" in html


def test_empreinte_des_rendus():
    verifier_empreinte("pieces.salon.piece", "pieces.salon.amenagement.document")
