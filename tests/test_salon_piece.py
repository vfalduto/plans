"""Salon, la pièce (pieces/salon/piece.py)."""
import math

from pieces.salon import piece
from tests.outils import verifier_empreinte


def test_piece():
    assert (piece.ID, piece.NOM) == ("salon", "Salon")
    assert piece.SOL[0] == (0, 0) and len(piece.SOL) == 8
    assert math.isclose(piece.SURFACE, (547 * 367 - 131 * 10 - 32 * 17) / 1e4)
    assert piece.MURS == [b for b in piece.ENVELOPPE if b.role == "mur"]
    assert piece.PORTES[0]["a"] == piece.PASSAGE["y0"]
    assert piece.FENETRES[0]["b"] == piece.BAIE["y1"]


def test_contour_de_l_accueil_inchange():
    """Posé par POSITION, le sol du salon est le contour que l'accueil dessinait jusqu'ici (APPART)."""
    from commun import appartement
    avant = next(c for c in appartement.APPART if c.id == "salon")
    apres = next(c for c in appartement.contours() if c.id == "salon")
    assert apres.p == avant.p


def test_cameras_de_la_piece():
    """Deux coins iso, orthographiques, murs cachés par un motif de nom d'objet."""
    assert [c.id for c in piece.CAMERAS] == ["iso_se", "iso_no"]
    assert all(c.ortho and c.reglages["coupes"] for c in piece.CAMERAS)


def test_empreinte_des_rendus():
    verifier_empreinte("pieces.salon.piece")
