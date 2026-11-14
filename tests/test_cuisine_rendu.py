"""Cuisine, aménagement : chaîne de rendu FreeCAD puis Blender (pieces/cuisine/amenagement/), sans Blender ni FreeCAD.

Les scripts importent bpy ou FreeCAD : ils sont lus comme du texte (et compilés), pas importés."""
import hashlib
import json
import os
import py_compile
import re
import subprocess
import sys

import pytest

from pieces.cuisine import piece
from tests.cuisine_anciens import FIXTURES
from tests.outils import RACINE

DOSSIER = RACINE / "pieces" / "cuisine" / "amenagement"
SCRIPTS = ("rendu.py", "cad.py", "video.py", "maquette.py")
RENDUS = RACINE / "site" / "cuisine" / "amenagement" / "rendus"
# nouveau nom (id de caméra) -> ancien nom dans cuisine-v13-3d/
ANCIENS = {"iso_so": "iso", "iso_so_nuit": "iso_nuit"}


def _rendu_cache(*args, cwd):
    """`python3 -m commun.rendu_cache …` lancé depuis `cwd` (cache/empreintes.json se lit depuis le dossier courant)."""
    env = dict(os.environ, PYTHONPATH=str(RACINE), BLENDER_REEL="/opt/homebrew/bin/blender")
    return subprocess.run([sys.executable, "-m", "commun.rendu_cache", *args], cwd=cwd, env=env, capture_output=True,
                          text=True)


def test_cache_declare():
    from commun.rendu_cache import CacheRendu
    from pieces.cuisine.amenagement import document
    assert document.CACHE_RENDU == CacheRendu(
        variantes={"": ("pieces.cuisine.piece", "pieces.cuisine.modele")},
        code=("pieces/cuisine/amenagement/rendu.py", "pieces/cuisine/amenagement/cad.py", "3d/rendu.py"))


def test_cache_variantes():
    r = _rendu_cache("variantes", "cuisine/amenagement", cwd=RACINE)
    assert (r.returncode, r.stdout.strip()) == (0, "-"), r.stderr


@pytest.mark.skipif(not os.path.exists("/opt/homebrew/bin/blender"), reason="la version de Blender entre dans l'empreinte")
def test_toutes_les_vues_a_rendre(tmp_path):
    """Sans empreinte notée (dossier courant vide), les huit caméras de la pièce sont à rendre, dans leur ordre."""
    r = _rendu_cache("liste", "cuisine/amenagement", "-", "64", cwd=tmp_path)
    assert r.returncode == 0, r.stderr
    assert r.stdout.split() == [c.id for c in piece.CAMERAS]
    assert len(piece.CAMERAS) == 8
    assert not (tmp_path / "cache").exists()        # `liste` ne note rien


@pytest.mark.parametrize("nom", SCRIPTS)
def test_chemins_de_la_chaine(nom, tmp_path):
    texte = (DOSSIER / nom).read_text(encoding="utf-8")
    for interdit in ("/Applications/Blender.app", "3d/sortie", "dirname(dirname(HERE))",
                     "sys.path.insert(0, os.path.dirname(HERE))", "R.OUT"):
        assert interdit not in texte, interdit
    py_compile.compile(str(DOSSIER / nom), cfile=str(tmp_path / "x.pyc"), doraise=True)
    if nom == "rendu.py":
        assert "piece.CAMERAS" in texte and "loc=(" not in texte
        assert 'spec_from_file_location("rendu_3d"' in texte
        assert "from pieces.cuisine import modele" in texte and "from pieces.cuisine import piece" in texte
        assert 'os.path.join(RACINE, M.PAPIER_PEINT["image"])' in texte
        assert "CUISINE_SORTIE" in texte and "CUISINE_APERCU" in texte
    if nom == "cad.py":
        assert "CUISINE_SORTIE" in texte and "from pieces.cuisine import modele" in texte
    if nom in ("video.py", "maquette.py"):             # rendu.py chargé depuis leur propre dossier
        assert re.search(r'os\.path\.join\(HERE, (fichier|"rendu\.py")\)', texte)
    if nom == "maquette.py":
        assert "CUISINE_MAQUETTE" in texte and "cuisine-v13-maquette/" not in texte


def test_anciens_scripts_deplaces():
    for nom in SCRIPTS:
        assert not (RACINE / "3d" / "v13" / nom).exists(), nom
    assert (DOSSIER / "__init__.py").exists()


def _recettes():
    """Nom -> texte (en-tête et corps) de chaque recette du justfile."""
    res, nom = {}, None
    for ligne in (RACINE / "justfile").read_text(encoding="utf-8").splitlines():
        m = re.match(r"^([a-z_][\w-]*)( [^:]*)?:(?!=)", ligne)
        if m and not ligne.startswith((" ", "\t")):
            nom = m.group(1)
            res[nom] = ligne + "\n"
        elif nom and ligne.startswith((" ", "\t")):
            res[nom] += ligne + "\n"
        elif not ligne.strip() or ligne.startswith("#"):
            nom = None
    return res


def test_recettes():
    recettes = _recettes()
    cuisine = {n: t for n, t in recettes.items() if n.startswith("cuisine-amenagement-")}
    assert sorted(cuisine) == sorted(["cuisine-amenagement-cad", "cuisine-amenagement-rendu",
                                      "cuisine-amenagement-apercu", "cuisine-amenagement-maquette",
                                      "cuisine-amenagement-video-apercu", "cuisine-amenagement-video"])
    for nom, texte in cuisine.items():
        assert "/Applications/" not in texte, nom
    for nom in ("cuisine-amenagement-rendu", "cuisine-amenagement-apercu", "cuisine-amenagement-maquette",
                "cuisine-amenagement-video-apercu", "cuisine-amenagement-video"):
        assert '"${BLENDER:-/opt/homebrew/bin/blender}" -b --python-exit-code 1 --python pieces/cuisine/amenagement/' \
            in cuisine[nom], nom
    # les anciennes recettes de rendu ne lancent plus les scripts de 3d/v13/
    for nom, texte in recettes.items():
        for script in SCRIPTS:
            assert f"3d/v13/{script}" not in texte, (nom, script)


@pytest.mark.skipif(subprocess.run(["which", "just"], capture_output=True).returncode != 0, reason="just absent")
def test_recette_apercu_a_sec():
    r = subprocess.run(["just", "--dry-run", "cuisine-amenagement-apercu", "iso_so"], cwd=RACINE, capture_output=True,
                       text=True)
    assert r.returncode == 0, r.stderr
    sortie = r.stdout + r.stderr
    assert "/Applications/Blender" not in sortie
    assert "pieces/cuisine/amenagement/rendu.py -- 16 iso_so" in sortie
    assert "CUISINE_APERCU=1" in sortie and 'CUISINE_SORTIE="$PWD/cache/apercu"' in sortie


def test_rendus_repris():
    """Les huit rendus V13.26 (iso_no V13.27) repris octet pour octet, sous le nom de leur caméra."""
    hashes = json.loads((FIXTURES / "rendus.json").read_text(encoding="utf-8"))
    assert len(hashes) == 8
    ids = [c.id for c in piece.CAMERAS]
    assert sorted(p.name for p in RENDUS.iterdir()) == sorted(f"{i}.jpg" for i in ids)
    for i in ids:
        assert hashlib.sha256((RENDUS / f"{i}.jpg").read_bytes()).hexdigest() == hashes[ANCIENS.get(i, i)], i
