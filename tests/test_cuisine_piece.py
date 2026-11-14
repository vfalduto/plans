"""Cuisine, la pièce (pieces/cuisine/piece.py) et le modèle déplacé (pieces/cuisine/modele.py, relais 3d/v13/modele.py)."""
import importlib
import importlib.util
import json
import subprocess
import sys

import pytest

from pieces.cuisine import modele, piece
from tests.cuisine_anciens import FIXTURES, ancien
from tests.outils import RACINE

_spec = importlib.util.spec_from_file_location("extraire_cuisine", FIXTURES / "extraire.py")
extraire = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(extraire)

SOL = [(0, 0), (327, 0), (327, 115), (382, 115), (382, 240), (341, 240), (341, 252), (0, 252)]
COUPES = json.loads((FIXTURES / "rendu.json").read_text(encoding="utf-8"))


def aire(p):
    return abs(sum(x0 * y1 - x1 * y0 for (x0, y0), (x1, y1) in zip(p, p[1:] + p[:1]))) / 2


def test_modele_identique_a_la_reference():
    attendu = json.loads((FIXTURES / "modele.json").read_text(encoding="utf-8"))
    assert json.loads(extraire.donnees_modele(modele)) == attendu
    assert not hasattr(modele, "COLONNES_CONTENU")    # renommée _COLONNES_CONTENU (clés en tuples)


def test_relais():
    assert ancien("modele") is importlib.import_module("pieces.cuisine.modele")


def test_anciens_generateurs_inchanges():
    plan = ancien("plan")
    assert plan.page(plan.lire_figees()) == (RACINE / "cuisine-v13.html").read_text(encoding="utf-8")
    assert ancien("porte").page() == (FIXTURES / "porte-cellier.html").read_text(encoding="utf-8")


def test_piece():
    assert (piece.ID, piece.NOM, piece.POSITION) == ("cuisine", "Cuisine", (-220, -262, 0))
    assert piece.SOL == SOL
    assert piece.SURFACE == pytest.approx(aire(SOL) / 10000)
    assert (piece.H, piece.Bloc, piece.Cyl, piece.Pan, piece.ENVELOPPE) == (
        modele.H, modele.Bloc, modele.Cyl, modele.Pan, modele.ENVELOPPE)
    assert (piece.DEBOUT, piece.ASSIS) == (163, 120)


def test_sol_contre_l_enveloppe():
    """Les sommets du sol tombent sur le nu des murs du modèle (sauf y 115, repris de l'accueil)."""
    murs = {b.nom: b for b in modele.ENVELOPPE}
    xs = {0: murs["ouest_nord"].x1, 327: murs["cloison_cellier"].x1, 382: murs["ouest_wc"].x0,
          341: murs["decroche_se"].x0}
    ys = {0: murs["nord"].y1, 240: murs["decroche_se"].y0, 252: murs["sud_ouest"].y0}
    assert all(k == v for k, v in xs.items()) and all(k == v for k, v in ys.items())
    assert {x for x, _ in SOL} == set(xs) and {y for _, y in SOL} - {115} == set(ys)


def test_contour_de_l_accueil():
    """Posé par POSITION, le sol de la cuisine est le contour que l'accueil dessinait jusqu'ici (APPART)."""
    from commun import appartement
    avant = next(c for c in appartement.APPART if c.id == "cuisine")
    apres = next(c for c in appartement.contours() if c.id == "cuisine")
    assert apres.p == avant.p


def test_sol_et_cellier():
    """Cuisine et cellier de l'accueil, ramenés dans le repère de la cuisine, réunis en un seul contour."""
    from commun import appartement
    dx, dy, _ = piece.POSITION
    cellier = next(c for c in appartement.APPART if c.id == "cellier")
    assert [(x - dx, y - dy) for x, y in cellier.p] == [
        (327, 0), (434, 0), (434, 44), (484, 44), (484, 100), (382, 100), (382, 115), (327, 115)]
    assert piece.SOL_ET_CELLIER == [(0, 0), (434, 0), (434, 44), (484, 44), (484, 100), (382, 100), (382, 240),
                                    (341, 240), (341, 252), (0, 252)]
    assert aire(piece.SOL_ET_CELLIER) == aire(SOL) + aire([(x - dx, y - dy) for x, y in cellier.p])


def test_portes_tirees_du_modele():
    entree, cellier = piece.PORTES
    assert (entree["a"], entree["b"]) == (228, 306)
    assert (cellier["a"], cellier["b"]) == (modele.BAIE_Y0, modele.BAIE_Y1)
    assert entree == dict(nom="entree", piece="Entrée", mur="s", face=252, a=228, b=306, type="galandage")
    assert cellier == dict(nom="cellier", piece="Cellier", mur="e", face=320, a=modele.BAIE_Y0, b=modele.BAIE_Y1,
                           type="pliante")


def test_cameras():
    D, A = 163, 120
    iso = dict(loc=(-380, 700, 640), cible=(250, 120, 60), ortho=6.0, focale=None, yeux=None)
    attendu = [
        ("iso_so", "Isométrique sud-ouest", iso, dict(coupes=COUPES["COUPES_ISO"])),
        ("iso_so_nuit", "Isométrique sud-ouest, de nuit", iso, dict(coupes=COUPES["COUPES_ISO"], nuit=True)),
        ("iso_no", "Isométrique nord-ouest",
         dict(loc=(-400, -470, 700), cible=(220, 140, 60), ortho=6.0, focale=None, yeux=None),
         dict(coupes=COUPES["COUPES_ISO_NO"], porte="fermee")),
        ("entree", "Depuis l'entrée", dict(loc=(268, 236, D), cible=(105, 40, D), ortho=None, focale=18, yeux=D),
         dict(decentrement=-0.12)),
        ("fenetre", "Depuis la fenêtre", dict(loc=(12, 105, D), cible=(330, 140, D), ortho=None, focale=18, yeux=D),
         dict(decentrement=-0.12)),
        ("banquette", "Assis sur la banquette",
         dict(loc=(28, 217, A), cible=(320, 150, A), ortho=None, focale=20, yeux=A), dict(decentrement=0.02)),
        ("dos_cellier", "Dos à la porte du cellier",
         dict(loc=(312, (modele.BAIE_Y0 + modele.BAIE_Y1) / 2, D), cible=(40, 215, D), ortho=None, focale=18, yeux=D),
         dict(decentrement=-0.15, porte="fermee")),
        ("cellier", "Entrée du cellier", dict(loc=(336, 72, D), cible=(470, 60, D), ortho=None, focale=14, yeux=D),
         dict(decentrement=-0.15, porte="fermee")),
    ]
    assert [c.id for c in piece.CAMERAS] == [a[0] for a in attendu]
    for c, (ident, nom, optique, reglages) in zip(piece.CAMERAS, attendu):
        assert (c.id, c.nom, c.loc, c.cible, c.ortho, c.focale, c.yeux, c.reglages) == (
            ident, nom, optique["loc"], optique["cible"], optique["ortho"], optique["focale"], optique["yeux"],
            reglages)
    assert [c.reglages["coupes"] for c in piece.CAMERAS[:3]] == [COUPES["COUPES_ISO"]] * 2 + [COUPES["COUPES_ISO_NO"]]
    assert (piece.COUPES_ISO, piece.COUPES_ISO_NO) == (COUPES["COUPES_ISO"], COUPES["COUPES_ISO_NO"])


def test_donnees_stables():
    """donnees_variante(piece, modele) s'écrit pareil dans deux processus (graines de hachage différentes)."""
    from commun import rendu_cache
    noms = ("pieces.cuisine.piece", "pieces.cuisine.modele")
    code = ("import importlib, json, sys; from commun import rendu_cache as r; "
            "ms = [importlib.import_module(n) for n in sys.argv[1:]]; "
            "print(json.dumps(r.donnees_variante(*ms), sort_keys=True, default=r._json))")
    ici = json.dumps(rendu_cache.donnees_variante(piece, modele), sort_keys=True, default=rendu_cache._json)
    ailleurs = [subprocess.run([sys.executable, "-c", code, *noms], cwd=RACINE, capture_output=True, text=True,
                               check=True, env={"PYTHONHASHSEED": str(graine), "PATH": ""}).stdout.strip()
                for graine in (1, 2)]
    assert ailleurs == [ici, ici]
