"""Salon, enfilade (pieces/salon/enfilade/) : cotes, caméras, rendus, changements, volumes, empreinte."""
import pytest

from pieces.salon import meubles
from pieces.salon.enfilade import document as enfilade
from pieces.salon.enfilade import volumes
from tests.outils import verifier_empreinte


def test_cote_comme_virg():
    """L'enfilade affiche ses cotes par `cote` (240 donne « 240 », là où virg donne « 240,0 »)."""
    assert meubles.cote(240) == "240" and meubles.virg(240) == "240,0"
    assert meubles.cote(1.8) == "1,8" and meubles.cote(60.84, 2) == "60,84"


def test_cameras():
    assert [c.id for c in enfilade.CAMERAS] == ["iso", "ouverte"]
    assert [c.reglages.get("ouvert", False) for c in enfilade.CAMERAS] == [False, True]
    # le plafond est caché à toutes les vues (il masquerait le haut des étagères)
    assert all(c.reglages["coupes"] == r"^plafond__" for c in enfilade.CAMERAS)


def test_rendus():
    assert [c.id for c in enfilade.CAMERAS] == [k for k, _ in enfilade.RENDUS]


def test_changements():
    assert len(enfilade.CHANGEMENTS) == 7
    assert enfilade.CHANGEMENTS[0][0] == enfilade.VERSION


def test_geometrie():
    assert volumes.G == volumes.geometrie()
    assert volumes.controle() is not None


@pytest.mark.parametrize("ouvert", [False, True])
def test_volumes(ouvert):
    assert volumes.chevauchements(volumes.pieces_3d(ouvert=ouvert)) == []


def test_cache_declare():
    assert set(enfilade.CACHE_RENDU.variantes) == {""}
    assert enfilade.CACHE_RENDU.cameras == "pieces.salon.enfilade.document"


def test_empreinte_des_rendus():
    verifier_empreinte("pieces.salon.piece", "pieces.salon.enfilade.document")
