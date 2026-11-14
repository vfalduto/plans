"""Outils des tests de la cuisine : les anciens modules de 3d/v13/, chargés à la demande.

Chaque ancien module (modele, plan, imprimable, porte) est importé seul, au premier besoin, comme le font les anciens
générateurs (3d/v13/ en tête de sys.path). Un ancien module absent ou qui ne s'importe plus fait sauter (skip) les
seuls tests qui le lisent.
"""
import importlib
import sys

import pytest

from tests.outils import RACINE

ANCIEN = RACINE / "3d" / "v13"
FIXTURES = RACINE / "tests" / "fixtures" / "cuisine"
_NOMS = ("modele", "plan", "imprimable", "porte")
_cache = {}


def ancien(nom):
    """Module `nom` de 3d/v13/ (et ses dépendances), importé une fois ; skip s'il n'existe plus."""
    if nom in _cache:
        return _cache[nom]
    if not (ANCIEN / f"{nom}.py").exists():
        pytest.skip(f"3d/v13/{nom}.py n'existe plus")
    gardes = {n: sys.modules.pop(n) for n in _NOMS if n in sys.modules}
    sys.modules.update(_cache)                       # dépendances déjà chargées : les mêmes objets
    sys.path.insert(0, str(ANCIEN))
    try:
        importlib.import_module(nom)
    except ImportError as e:
        pytest.skip(f"3d/v13/{nom}.py ne s'importe plus : {e}")
    finally:
        sys.path[:] = [p for p in sys.path if p != str(ANCIEN)]   # les anciens modules s'y remettent eux-mêmes
        for n in _NOMS:
            m = sys.modules.pop(n, None)
            if m is not None:
                _cache.setdefault(n, m)
        sys.modules.update(gardes)
    return _cache[nom]
