"""Salon, étagères (pieces/salon/etageres/) : cotes, caméras, rendus, changements, volumes, empreinte."""
import pytest

from pieces.salon import meubles
from pieces.salon.etageres import document as etageres
from pieces.salon.etageres import volumes
from tests.outils import RACINE, verifier_empreinte


def test_cote_comme_cm():
    assert [meubles.cote(v) for v in (0, 1.25, 4.7, 79, 134.0)] == ["0", "1,2", "4,7", "79", "134"]


def test_cameras():
    assert [c.id for c in etageres.CAMERAS] == ["iso", "detail"]
    # le plafond est caché à toutes les vues (il masquerait le haut des étagères)
    assert all(c.reglages["coupes"] == r"^plafond__" for c in etageres.CAMERAS)


def test_rendus():
    assert [c.id for c in etageres.CAMERAS] == [k for k, _ in etageres.RENDUS]


def test_changements():
    assert etageres.CHANGEMENTS[0][0] == etageres.VERSION


@pytest.mark.parametrize("cle", [d["cle"] for d in etageres.DISPOSITIONS])
def test_volumes(cle):
    ps = volumes.pieces_3d(cle)
    assert ps and all(p.x0 < p.x1 and p.y0 < p.y1 and p.z0 < p.z1 for p in ps)
    assert [t["rep"] for t in volumes.tablettes(volumes.disposition(cle))][0] == "T1"


def test_disposition_est_une_copie():
    d = volumes.disposition("rangs")
    d["tablettes"].append((222, 0, 1))
    assert volumes.disposition("rangs") != d


def test_cache_declare():
    """Les quatre dispositions sont déclarées, seule Actuelle est rendue (voir le justfile)."""
    assert set(etageres.CACHE_RENDU.variantes) == {d["cle"] for d in etageres.DISPOSITIONS}
    assert etageres.CACHE_RENDU.cameras == "pieces.salon.etageres.document"
    for chemin in etageres.CACHE_RENDU.code:
        assert (RACINE / chemin).is_file(), chemin


def test_empreinte_des_rendus():
    verifier_empreinte("pieces.salon.piece", "pieces.salon.enfilade.document", "pieces.salon.etageres.document")
