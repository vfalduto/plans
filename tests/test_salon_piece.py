"""Salon, la pièce (pieces/salon/piece.py) : reprise de 3d/salon/modele.py et des caméras de 3d/salon/rendu.py."""
import math

import pytest

from pieces.salon import piece
from tests.salon_anciens import MODELE, ancien, comme_vue, norm, verifier_empreinte, vues_du_rendu


@pytest.mark.parametrize("ancien_nom", sorted(MODELE["piece"]))
def test_constantes_du_modele(ancien_nom):
    assert norm(getattr(piece, MODELE["piece"][ancien_nom])) == norm(getattr(ancien("modele"), ancien_nom))


def test_modele_entierement_repris():
    """Toute constante publique de modele.py a sa place dans le paquet du salon (pièce ou un des trois documents)."""
    publiques = {n for n in vars(ancien("modele")) if n.isupper() or n == "_MODULES"}
    assert publiques == {n for noms in MODELE.values() for n in noms}


def test_piece():
    assert (piece.ID, piece.NOM) == ("salon", "Salon")
    assert piece.SOL[0] == (0, 0) and len(piece.SOL) == 8
    assert math.isclose(piece.SURFACE, (547 * 367 - 131 * 10 - 32 * 17) / 1e4)
    assert piece.MURS == [b for b in piece.ENVELOPPE if b.role == "mur"]
    assert piece.PORTES[0]["a"] == ancien("modele").PASSAGE["y0"]
    assert piece.FENETRES[0]["b"] == ancien("modele").BAIE["y1"]


def test_contour_de_l_accueil_inchange():
    """Posé par POSITION, le sol du salon est le contour que l'accueil dessinait jusqu'ici (APPART)."""
    from commun import appartement
    avant = next(c for c in appartement.APPART if c.id == "salon")
    apres = next(c for c in appartement.contours() if c.id == "salon")
    assert apres.p == avant.p


def test_cameras_de_la_piece():
    vues = vues_du_rendu("rendu.py")
    cams = {c.id: c for c in piece.CAMERAS}
    # la vue « iso » de l'ancien rendu est la caméra `iso_se` : le nom du coin de la vue Iso du document
    ancien = lambda k: "iso_se" if k.removesuffix("_noyer") == "iso" else k.removesuffix("_noyer")   # noqa: E731
    assert set(cams) == {ancien(k) for k, v in vues.items() if "essence" not in v}
    for k, v in vues.items():
        c = cams[ancien(k)]
        assert v == {**comme_vue(c), "coupes": c.reglages["coupes"], **({"essence": "noyer"} if "essence" in v else {})}


def test_empreinte_des_rendus():
    verifier_empreinte("pieces.salon.piece")
