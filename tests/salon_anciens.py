"""Outils des tests du salon : les anciens modules de 3d/salon/, chargés à la demande, et leurs dessins.

Chaque ancien module (modele, plan, commun, etageres, enfilade) est importé seul, au premier besoin, comme le font
les anciens générateurs (3d/salon/ en tête de sys.path), sans toucher au paquet commun/ de la racine : 3d/salon/commun.py
porte le même nom. Un ancien module absent ou qui ne s'importe plus fait sauter (skip) les seuls tests qui le lisent.
"""
import ast
import dataclasses
import importlib
import importlib.util
import json
import subprocess
import sys
from types import SimpleNamespace

import pytest

from commun.journal import depuis_page
from commun.modele import Camera
from tests.outils import RACINE

ANCIEN = RACINE / "3d" / "salon"
FIXTURES = RACINE / "tests" / "fixtures" / "salon"
_NOMS = ("commun", "modele", "plan", "etageres", "enfilade")
_cache = {}


def ancien(nom):
    """Module `nom` de 3d/salon/ (et ses dépendances), importé une fois ; skip s'il n'existe plus."""
    if nom in _cache:
        return _cache[nom]
    if not (ANCIEN / f"{nom}.py").exists():
        pytest.skip(f"3d/salon/{nom}.py n'existe plus")
    gardes = {n: sys.modules.pop(n) for n in _NOMS if n in sys.modules}
    sys.modules.update(_cache)                       # dépendances déjà chargées : les mêmes objets
    # un ancien module disparu ne doit pas se résoudre ailleurs (commun → le paquet commun/ de la racine)
    sys.modules.update({n: None for n in _NOMS if n not in _cache and not (ANCIEN / f"{n}.py").exists()})
    sys.path.insert(0, str(ANCIEN))
    try:
        importlib.import_module(nom)
    except ImportError as e:
        pytest.skip(f"3d/salon/{nom}.py ne s'importe plus : {e}")
    finally:
        sys.path.remove(str(ANCIEN))
        for n in _NOMS:
            m = sys.modules.pop(n, None)
            if m is not None:
                _cache.setdefault(n, m)
        sys.modules.update(gardes)
    return _cache[nom]


def norm(v):
    """Valeur comparable d'un module à l'autre : dataclasses (Bloc, Cyl, Piece) par nom de classe et champs."""
    if dataclasses.is_dataclass(v) and not isinstance(v, type):
        champs = {k: norm(getattr(v, k)) for k in ("etiq", "contenu") if hasattr(v, k)}
        champs.update({c.name: norm(getattr(v, c.name)) for c in dataclasses.fields(v)})
        return (type(v).__name__, champs)
    if isinstance(v, SimpleNamespace):
        return norm(vars(v))
    if isinstance(v, dict):
        return {k: norm(x) for k, x in v.items()}
    if isinstance(v, (list, tuple)):
        return [norm(x) for x in v]
    if callable(v):
        code = getattr(v, "__code__", None)
        return ("fonction", v.__name__, code.co_code if code else None, code.co_consts if code else None)
    return v


def pieces(ps):
    """Liste de Piece comparable (champs seuls)."""
    return [norm(p)[1] for p in ps]


# ------------------------------------------------------------------ correspondance des noms de modele.py
# ancien nom dans 3d/salon/modele.py → (module neuf, nom neuf), par module neuf
MODELE = {
    "piece": {n: n for n in ("H", "L", "P", "EP", "PASSAGE", "COFFRE", "POUTRE", "DECROCHE", "BAIE", "CLIM",
                             "ENVELOPPE")},
    "amenagement": {**{n: n for n in (
        "VERSION", "CHANGEMENTS", "CARRELAGE", "PAPIER_PEINT", "MEUBLES", "ALLEE_ENFILADE", "CANAPE", "DESSERTE",
        "PLATINE", "CM_VINYLES", "VINYLES", "CONSOLE", "ECRAN", "PROJECTEUR", "TABLE", "CONFIGS", "CHAISE", "CHAISES",
        "CHAISES_PLIANTES", "PAS_CHAISES", "SUSPENSION", "TABLE_BASSE", "DYVLINGE", "CHILIENNE", "DECO", "TAPIS",
        "LAMPADAIRE", "CADRES", "RIDEAU", "PISTES_DECO", "DEGAGEMENTS", "TABLES_REPLIABLES", "RENDUS")},
        "MURS": "FINITION_MURS"},
    "enfilade": {"ENFILADE": "ENFILADE", "_MODULES": "MODULES", "VOLUME_ENFILADE": "VOLUME_ENFILADE"},
    "etageres": {n: n for n in ("MONTANTS", "ETAGERES", "TABLETTES", "NIVEAUX", "DISPOSITIONS", "METRES_ETAGERES",
                                "CHEVILLES", "ENTAILLES", "CHARGE_LIVRES", "ETUDE_MONTANTS")},
}


# ------------------------------------------------------------------ caméras des anciens scripts de rendu
def vues_du_rendu(nom):
    """VIEWS et ses motifs de coupe, lus dans le source de 3d/salon/<nom> (le script importe bpy)."""
    chemin = ANCIEN / nom
    if not chemin.exists():
        pytest.skip(f"3d/salon/{nom} n'existe plus")
    arbre = ast.parse(chemin.read_text(encoding="utf-8"))
    garde = []
    for n in arbre.body:
        if isinstance(n, ast.Assign):
            t = n.targets[0]
            cible = t.value.id if isinstance(t, ast.Subscript) else getattr(t, "id", "")
            if cible in ("VIEWS", "COUPES_ISO", "COUPES_ISO_NO"):
                garde.append(n)
    ns = {}
    exec(compile(ast.Module(garde, []), nom, "exec"), ns)
    return ns["VIEWS"]


def comme_vue(c: Camera):
    v = {"loc": c.loc, "target": c.cible}
    if c.ortho:
        v["ortho"] = c.ortho
    if c.focale:
        v["lens"] = c.focale
    return v


# ------------------------------------------------------------------ anciennes pages et dessins de référence
PAGES = {
    "salon-v4.html": lambda: ancien("plan").page(ancien("plan").lire_figees()),
    "salon-etageres.html": lambda: ancien("etageres").page(),
    "salon-enfilade.html": lambda: ancien("enfilade").page()[0],
}


def changements_de_la_page(page):
    return [(c.version, c.date, c.texte) for c in depuis_page(PAGES[page]())]


def verifier_dessins(page):
    """Les fichiers de référence de `page` sont exactement les <svg> que l'ancien générateur produit aujourd'hui."""
    spec = importlib.util.spec_from_file_location("extraire_salon", FIXTURES / "extraire.py")
    ex = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(ex)
    html = PAGES[page]()
    index = json.loads((FIXTURES / "index.json").read_text(encoding="utf-8"))
    lus = [svg for svg, _ in ex.dessins(html)]
    miens = sorted((d["rang"], nom) for nom, d in index.items() if d["page"] == page)
    assert len(lus) == len(miens) == html.count("<svg ")
    for rang, nom in miens:
        assert (FIXTURES / nom).read_text(encoding="utf-8") == lus[rang], nom


# ------------------------------------------------------------------ empreinte des rendus
def verifier_empreinte(*noms):
    """commun.rendu_cache.donnees_variante accepte les modules `noms` et deux processus les écrivent pareil."""
    from commun import rendu_cache
    code = ("import importlib, json, sys; from commun import rendu_cache as r; "
            "ms = [importlib.import_module(n) for n in sys.argv[1:]]; "
            "print(json.dumps(r.donnees_variante(*ms), sort_keys=True, default=r._json))")
    ms = [importlib.import_module(n) for n in noms]
    ici = json.dumps(rendu_cache.donnees_variante(*ms), sort_keys=True, default=rendu_cache._json)
    ailleurs = [subprocess.run([sys.executable, "-c", code, *noms], cwd=RACINE, capture_output=True, text=True,
                               check=True, env={"PYTHONHASHSEED": str(graine), "PATH": ""}).stdout.strip()
                for graine in (1, 2)]
    assert ailleurs == [ici, ici]
