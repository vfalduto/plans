from pieces.entree import piece
from pieces.entree.amenagement import document, victor


def test_piece():
    assert piece.SOL[0] == (0, 0)
    assert len(piece.SOL) == 8
    assert piece.H == 250
    assert {c.id for c in piece.CAMERAS} == {"iso_so", "iso_no", "iso_se", "banc", "couloir"}


def test_versions():
    assert document.VERSION == "V4.8"
    assert victor.VERSION == "V1.5"
    assert victor.CHANGEMENTS[0][0] == "V1.5"


def test_cameras_communes():
    assert not hasattr(victor, "VUES")


def test_cameras_partagees():
    cams = {c.id: c for c in piece.CAMERAS}
    assert set(cams) == {"iso_so", "iso_no", "iso_se", "banc", "couloir"}
    assert cams["iso_no"].cible == (177, 190, 60)
    assert cams["banc"].focale == 17
    assert cams["banc"].yeux == 112


def test_positions_humains_victor():
    assert victor.POSITIONS_HUMAINS == {"couloir": (150, 95), "entree": (36, 300)}
    assert victor.HUMAINS["iso_no"] == "entree"
