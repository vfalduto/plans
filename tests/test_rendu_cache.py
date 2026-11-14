"""Empreintes des rendus : une caméra ou une variante modifiée ne refait que ses propres vues."""
import importlib
import json
import os
import subprocess
import sys
import textwrap
from dataclasses import replace

import pytest

import pieces
from commun import rendu_cache
from pieces.entree import piece
from pieces.entree.amenagement import document, victor
from tests.outils import RACINE


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


# ------------------------------------------------------------------ déclaration CACHE_RENDU et ligne de commande
VERSION_BLENDER = "Blender 5.2.2"


@pytest.fixture
def blender(monkeypatch):
    # la ligne de version est injectée : aucun test ne lance Blender
    monkeypatch.setattr(rendu_cache, "_version_blender", lambda: VERSION_BLENDER)


@pytest.mark.parametrize("variante,module", [("principale", document), ("victor", victor)])
def test_entree_memes_empreintes_que_l_ancienne_formule(blender, variante, module):
    # ancienne formule, câblée sur l'entrée : pièce puis module de la variante, rendu.py de l'entrée puis 3d/rendu.py
    code = (RACINE / "pieces/entree/amenagement/rendu.py").read_text() + (RACINE / "3d/rendu.py").read_text()
    attendues = {c.id: rendu_cache.empreinte(c, rendu_cache.donnees_variante(piece, module), {"echantillons": 64}, code,
                                             VERSION_BLENDER) for c in piece.CAMERAS}
    assert rendu_cache.empreintes("entree/amenagement", variante, "64") == attendues


_EMPREINTES_DECLAREES = """
import json
from commun import rendu_cache
rendu_cache._version_blender = lambda: "Blender 5.2.2"
print(json.dumps({v: rendu_cache.empreintes("entree/amenagement", v, "64") for v in ("principale", "victor")}))
"""


def test_empreintes_declarees_stables_d_un_processus_a_l_autre():
    sorties = []
    for graine in ("1", "2"):
        env = {**os.environ, "PYTHONHASHSEED": graine}
        r = subprocess.run([sys.executable, "-c", _EMPREINTES_DECLAREES], cwd=RACINE, env=env, capture_output=True,
                           text=True)
        assert r.returncode == 0, r.stderr
        sorties.append(json.loads(r.stdout))
    assert set(sorties[0]["victor"]) == {c.id for c in piece.CAMERAS}
    assert sorties[0] == sorties[1]


def test_cache_rendu_hors_empreinte(monkeypatch):
    assert "pieces.entree.amenagement.document.CACHE_RENDU" not in rendu_cache.donnees_variante(piece, document)
    avant = emp(cameras()["banc"], document)
    monkeypatch.setattr(document, "CACHE_RENDU", rendu_cache.CacheRendu(variantes={}, code=()))
    assert emp(cameras()["banc"], document) == avant


# Faux documents sous tmp_path/pieces/essai, rattachés au paquet `pieces` le temps d'un test : un meuble à tiret
# (meuble-bas, paquet meuble_bas) à deux variantes et caméras propres, un plan sans variante aux caméras de la pièce.
_FAUX = {
    "essai/__init__.py": "",
    "essai/piece.py": """
        from commun.modele import Camera
        HAUTEUR = 250
        CAMERAS = (Camera("haut", "Vue de haut", (0, 0, 500), (0, 0, 0), ortho=5.0),
                   Camera("face", "De face", (0, 400, 120), (0, 0, 120), focale=20))
        """,
    "essai/meuble_bas/__init__.py": "",
    "essai/meuble_bas/document.py": """
        from commun.rendu_cache import CacheRendu
        LARGEUR = 120
        CACHE_RENDU = CacheRendu(variantes={"chene": ("pieces.essai.piece", "document"),
                                            "laque": ("pieces.essai.piece", "laque")},
                                 code=("code/meuble.py",), cameras="pieces.essai.meuble_bas.cameras")
        """,
    "essai/meuble_bas/laque.py": "TEINTE = 'blanc'\n",
    "essai/meuble_bas/cameras.py": """
        from commun.modele import Camera
        CAMERAS = (Camera("tiroir", "Tiroir ouvert", (0, 100, 60), (0, 0, 40), focale=30),
                   Camera("dessus", "Dessus", (0, 0, 300), (0, 0, 0), ortho=2.0))
        """,
    "essai/plan/__init__.py": "",
    "essai/plan/document.py": """
        from commun.rendu_cache import CacheRendu
        SOL = "chêne"
        CACHE_RENDU = CacheRendu(variantes={"": ("pieces.essai.piece", "document")}, code=("code/plan.py",))
        """,
    "essai/sans_cache/__init__.py": "",
    "essai/sans_cache/document.py": "NOM = 'pas de déclaration'\n",
    "essai/code_absent/__init__.py": "",
    "essai/code_absent/document.py": """
        from commun.rendu_cache import CacheRendu
        CACHE_RENDU = CacheRendu(variantes={"": ("document",)}, code=("code/disparu.py",))
        """,
}


@pytest.fixture
def faux(tmp_path, monkeypatch, blender):
    for chemin, texte in _FAUX.items():
        f = tmp_path / "pieces" / chemin
        f.parent.mkdir(parents=True, exist_ok=True)
        f.write_text(textwrap.dedent(texte))
    for nom in ("meuble.py", "plan.py"):
        (tmp_path / "code").mkdir(exist_ok=True)
        (tmp_path / "code" / nom).write_text(f"# rendu {nom}\n")
    monkeypatch.setattr(pieces, "__path__", [*pieces.__path__, str(tmp_path / "pieces")])
    monkeypatch.setattr(rendu_cache, "RACINE", tmp_path)
    monkeypatch.setattr(rendu_cache, "FICHIER", tmp_path / "cache" / "empreintes.json")
    yield tmp_path
    for nom in [n for n in sys.modules if n == "pieces.essai" or n.startswith("pieces.essai.")]:
        del sys.modules[nom]
    if hasattr(pieces, "essai"):
        del pieces.essai


def commande(capsys, *args):
    code = rendu_cache.main(list(args))
    sortie = capsys.readouterr()
    return code, sortie.out.strip(), sortie.err.strip()


def test_faux_meuble_a_tiret(faux, capsys):
    meuble = importlib.import_module("pieces.essai.meuble_bas.document")
    laque = importlib.import_module("pieces.essai.meuble_bas.laque")
    essai = importlib.import_module("pieces.essai.piece")
    cams = importlib.import_module("pieces.essai.meuble_bas.cameras").CAMERAS
    assert commande(capsys, "variantes", "essai/meuble-bas") == (0, "chene laque", "")
    # modules relatifs (document, laque) et absolu (pieces.essai.piece), caméras déclarées par le document
    for variante, module in (("chene", meuble), ("laque", laque)):
        attendues = {c.id: rendu_cache.empreinte(c, rendu_cache.donnees_variante(essai, module), {"echantillons": 16},
                                                 "# rendu meuble.py\n", VERSION_BLENDER) for c in cams}
        assert rendu_cache.empreintes("essai/meuble-bas", variante, "16") == attendues
    assert commande(capsys, "liste", "essai/meuble-bas", "laque", "16") == (0, "tiroir dessus", "")
    assert commande(capsys, "noter", "essai/meuble-bas", "laque", "16", "tiroir") == (0, "", "")
    assert set(json.loads(rendu_cache.FICHIER.read_text())) == {"essai/meuble-bas/laque/tiroir"}


def test_faux_document_sans_variante(faux, capsys):
    essai = importlib.import_module("pieces.essai.piece")
    plan = importlib.import_module("pieces.essai.plan.document")
    assert commande(capsys, "variantes", "essai/plan") == (0, "-", "")
    # caméras par défaut : celles de la pièce
    attendues = {c.id: rendu_cache.empreinte(c, rendu_cache.donnees_variante(essai, plan), {"echantillons": 64},
                                             "# rendu plan.py\n", VERSION_BLENDER) for c in essai.CAMERAS}
    assert rendu_cache.empreintes("essai/plan", "", "64") == attendues
    assert commande(capsys, "liste", "essai/plan", "-", "64") == (0, "haut face", "")
    assert commande(capsys, "noter", "essai/plan", "-", "64", "haut", "face") == (0, "", "")
    assert set(json.loads(rendu_cache.FICHIER.read_text())) == {"essai/plan/haut", "essai/plan/face"}
    assert commande(capsys, "liste", "essai/plan", "-", "64") == (0, "", "")


def test_liste_noter_liste(faux, capsys, monkeypatch):
    assert commande(capsys, "liste", "essai/meuble-bas", "chene", "64") == (0, "tiroir dessus", "")
    commande(capsys, "noter", "essai/meuble-bas", "chene", "64", "tiroir")
    assert commande(capsys, "liste", "essai/meuble-bas", "chene", "64") == (0, "dessus", "")
    # caméras demandées : affichées telles quelles, même déjà notées
    assert commande(capsys, "liste", "essai/meuble-bas", "chene", "64", "tiroir") == (0, "tiroir", "")
    commande(capsys, "noter", "essai/meuble-bas", "chene", "64", "dessus")
    commande(capsys, "noter", "essai/meuble-bas", "laque", "64", "tiroir", "dessus")
    for v in ("chene", "laque"):
        assert commande(capsys, "liste", "essai/meuble-bas", v, "64") == (0, "", "")
    # une donnée de la variante laque change : seules ses caméras reviennent
    monkeypatch.setattr(importlib.import_module("pieces.essai.meuble_bas.laque"), "TEINTE", "noir")
    assert commande(capsys, "liste", "essai/meuble-bas", "laque", "64") == (0, "tiroir dessus", "")
    assert commande(capsys, "liste", "essai/meuble-bas", "chene", "64") == (0, "", "")


@pytest.mark.parametrize("args,message", [
    (("variantes", "essai/absent"), "document introuvable : essai/absent (pieces.essai.absent.document)"),
    (("liste", "essai/sans-cache", "-", "64"), "CACHE_RENDU absente de pieces.essai.sans_cache.document"),
    (("liste", "essai/meuble-bas", "noyer", "64"), "variante non déclarée pour essai/meuble-bas : noyer"),
    (("liste", "essai/code-absent", "-", "64"), "fichier de code absent : code/disparu.py"),
    (("liste", "essai/meuble-bas", "chene", "64", "cote"), "caméra inconnue : cote"),
    (("liste", "essai/meuble-bas", "chene"), "usage"),
    (("noter", "essai/meuble-bas", "chene", "64"), "usage"),
    (("variantes",), "usage"),
    ((), "usage"),
    (("effacer", "essai/plan"), "usage"),
])
def test_erreurs(faux, capsys, args, message):
    code, sortie, erreur = commande(capsys, *args)
    assert code != 0
    assert sortie == ""
    assert message in erreur
    assert "Traceback" not in erreur


def test_erreur_sans_trace_en_ligne_de_commande():
    r = subprocess.run([sys.executable, "-m", "commun.rendu_cache", "liste", "entree/amenagement", "inconnue", "64"],
                       cwd=RACINE, capture_output=True, text=True)
    assert r.returncode == 1
    assert r.stderr == "variante non déclarée pour entree/amenagement : inconnue\n"


# ------------------------------------------------------------------ version de Blender (blender-seul.sh)
def _faux_binaire(dossier, nom, corps):
    f = dossier / nom
    f.write_text("#!/bin/sh\n" + corps + "\n")
    f.chmod(0o755)
    return str(f)


def test_version_lue_par_blender_reel(tmp_path, monkeypatch):
    # BLENDER est le script d'attente (blender-seul.sh) ; la question de version va droit au Blender réel
    monkeypatch.setattr(rendu_cache, "BLENDER", _faux_binaire(tmp_path, "attente", "exit 3"))
    monkeypatch.setenv("BLENDER_REEL", _faux_binaire(tmp_path, "reel", 'echo "Blender 5.2.2"; echo "build x"'))
    assert rendu_cache._version_blender() == "Blender 5.2.2"


def test_version_sans_sortie_erreur_sans_trace(tmp_path, monkeypatch):
    # attente du verrou expirée : code 3, rien sur stdout ; le message du script remonte, pas une IndexError
    monkeypatch.delenv("BLENDER_REEL", raising=False)
    monkeypatch.setattr(rendu_cache, "BLENDER", _faux_binaire(tmp_path, "attente", 'echo "verrou pris" >&2; exit 3'))
    with pytest.raises(rendu_cache.Erreur, match=r"verrou pris"):
        rendu_cache._version_blender()
    monkeypatch.setenv("BLENDER_REEL", _faux_binaire(tmp_path, "muet", "exit 0"))
    with pytest.raises(rendu_cache.Erreur, match=r"version de Blender"):
        rendu_cache._version_blender()


def test_conseil_de_nom_seulement(monkeypatch):
    # EXCLUES est commune à tous les documents : le message ne conseille que le nom en _X
    monkeypatch.setattr(victor, "GARDE", lambda c: c, raising=False)
    with pytest.raises(TypeError) as e:
        emp(cameras()["banc"], victor)
    assert "_GARDE" in str(e.value) and "EXCLUES" not in str(e.value)
