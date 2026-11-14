"""L'ancien modèle de 3d/sdb/ et ses modules, chargés à la demande.

modele() : 3d/sdb/modele.py (V6.4), chargé une fois sous le nom sdb_ancien_modele (il n'importe que math et
dataclasses). Il décrit le caisson haut et l'ancien meuble bas V6 : le meuble haut (pieces/sdb/meuble_haut/) en lit les
données, le meuble bas en lit Z_HAUT, Z_HAUT1, LED et VERSION ; cad.py et explorations/ l'importent aussi.
charger(nom) : 3d/sdb/<nom>.py importé comme le font les anciens générateurs (3d/sdb/ en tête de sys.path), puis retiré
de sys.modules avec ses dépendances de 3d/sdb/ : leurs noms (modele, plan, haut…) ne restent pas visibles ailleurs.
"""
import importlib
import importlib.util
import sys
from pathlib import Path
from types import ModuleType

RACINE = Path(__file__).resolve().parents[2]
ANCIEN = RACINE / "3d" / "sdb"
_cache: dict[str, ModuleType] = {}
_modele: list[ModuleType] = []


def modele() -> ModuleType:
    if not _modele:
        spec = importlib.util.spec_from_file_location("sdb_ancien_modele", ANCIEN / "modele.py")
        m = importlib.util.module_from_spec(spec)
        sys.modules["sdb_ancien_modele"] = m       # les dataclasses du module retrouvent leur module
        try:
            spec.loader.exec_module(m)
        finally:
            del sys.modules["sdb_ancien_modele"]
        _modele.append(m)
    return _modele[0]


def charger(nom: str) -> ModuleType:
    if nom in _cache:
        return _cache[nom]
    if not (ANCIEN / f"{nom}.py").is_file():
        raise FileNotFoundError(ANCIEN / f"{nom}.py")
    noms = {p.stem for p in ANCIEN.glob("*.py")}
    gardes = {n: sys.modules.pop(n) for n in noms if n in sys.modules}
    sys.modules.update(_cache)                      # dépendances déjà chargées : les mêmes objets
    chemins = list(sys.path)
    sys.path.insert(0, str(ANCIEN))
    reussi = False
    try:
        importlib.import_module(nom)
        reussi = True
    finally:
        sys.path[:] = chemins
        for n in noms:
            m = sys.modules.pop(n, None)
            if m is not None and reussi:
                _cache.setdefault(n, m)
        sys.modules.update(gardes)
    return _cache[nom]
