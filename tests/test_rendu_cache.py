"""Empreintes des rendus : une caméra ou une variante modifiée ne refait que ses propres vues."""
from dataclasses import replace

from commun import rendu_cache
from pieces.entree import piece
from pieces.entree.amenagement import document, victor


def cameras():
    return {c.id: c for c in piece.CAMERAS}


def emp(camera, module, reglages=None, code="code", blender="5.2.2"):
    donnees = rendu_cache.donnees_variante(piece, module)
    return rendu_cache.empreinte(camera, donnees, reglages or {"echantillons": 64}, code, blender)


def test_empreinte_stable():
    cam = cameras()["iso_so"]
    assert emp(cam, document) == emp(cam, document)
    assert len(emp(cam, document)) == 64


def test_camera_isolee():
    cams = cameras()
    avant = {k: emp(c, document) for k, c in cams.items()}
    deplacee = replace(cams["iso_so"], loc=(0, 0, 640))
    assert emp(deplacee, document) != avant["iso_so"]
    assert emp(cams["iso_no"], document) == avant["iso_no"]


def test_variante_isolee(monkeypatch):
    cams = cameras()
    avant_victor = emp(cams["iso_so"], victor)
    avant_principale = emp(cams["iso_so"], document)
    monkeypatch.setattr(victor, "PAIRES", victor.PAIRES + 1)
    assert emp(cams["iso_so"], victor) != avant_victor
    assert emp(cams["iso_so"], document) == avant_principale


def test_reglages_code_et_blender_comptent():
    cam = cameras()["banc"]
    base = emp(cam, document)
    assert emp(cam, document, reglages={"echantillons": 16}) != base
    assert emp(cam, document, code="autre") != base
    assert emp(cam, document, blender="9.9") != base


def test_a_rendre(tmp_path):
    fichier = tmp_path / "cache" / "empreintes.json"
    cle = "entree/amenagement/victor/banc"
    assert rendu_cache.a_rendre(cle, "abc", fichier)
    rendu_cache.noter(cle, "abc", fichier)
    assert not rendu_cache.a_rendre(cle, "abc", fichier)
    assert rendu_cache.a_rendre(cle, "def", fichier)
    assert rendu_cache.a_rendre("entree/amenagement/victor/couloir", "abc", fichier)
