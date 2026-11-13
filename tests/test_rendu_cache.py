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


_EMPREINTES = """
import json
from commun import rendu_cache
from pieces.entree import piece
from pieces.entree.amenagement import document, victor
print(json.dumps({m.__name__: {c.id: rendu_cache.empreinte(c, rendu_cache.donnees_variante(piece, m), {"echantillons": 64},
                                                           "code", "5.2.2") for c in piece.CAMERAS}
                  for m in (document, victor)}))
"""


def test_empreinte_stable_d_un_processus_a_l_autre():
    """Deux lancements de `just entree-rendu` doivent voir la même empreinte : rien ne dépend de l'adresse d'un objet
    en mémoire ni de l'ordre d'un ensemble (graine de hachage différente à chaque processus)."""
    import json
    import os
    import subprocess
    import sys
    from tests.outils import RACINE
    sorties = []
    for graine in ("1", "2"):
        env = {**os.environ, "PYTHONHASHSEED": graine}
        r = subprocess.run([sys.executable, "-c", _EMPREINTES], cwd=RACINE, env=env, capture_output=True, text=True)
        assert r.returncode == 0, r.stderr
        sorties.append(json.loads(r.stdout))
    assert set(sorties[0]) == {"pieces.entree.amenagement.document", "pieces.entree.amenagement.victor"}
    assert sorties[0] == sorties[1]


def test_donnee_non_serialisable_refusee(monkeypatch):
    # une fonction (ou tout objet que JSON ne sait pas écrire) n'a pas d'écriture stable : l'empreinte la refuse
    import pytest
    monkeypatch.setattr(victor, "GARDE", lambda c: c, raising=False)
    with pytest.raises(TypeError, match=r"victor\.GARDE : function"):
        emp(cameras()["banc"], victor)


def test_document_hors_empreinte():
    # DOCUMENT, construit à la première lecture, décrit la page : l'avoir lu ne change pas l'empreinte
    avant = emp(cameras()["banc"], document)
    document.DOCUMENT
    assert emp(cameras()["banc"], document) == avant


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


def test_constantes_de_page_sans_effet(monkeypatch):
    cams = cameras()
    avant = {k: emp(c, victor) for k, c in cams.items()}
    monkeypatch.setattr(victor, "VERSION", "V9.9")
    monkeypatch.setattr(victor, "ZONES", ())
    monkeypatch.setattr(victor, "RENDUS", [])
    assert {k: emp(c, victor) for k, c in cams.items()} == avant
