"""Cache des rendus : une empreinte par caméra et par variante, notée une fois l'image rendue.

Une vue est refaite quand sa caméra, les données de sa variante (et de la pièce), les réglages, le code de rendu ou la
version de Blender changent. Changer une caméra ne refait que cette caméra ; changer un meuble ne refait que les vues
de sa variante.

En ligne de commande (utilisé par la recette `entree-rendu`) :
    python3 -m commun.rendu_cache liste <variante> <échantillons> [caméra ...]
    python3 -m commun.rendu_cache noter <variante> <échantillons> <caméra> [caméra ...]
"""
import dataclasses
import hashlib
import importlib
import json
import subprocess
import sys
from pathlib import Path

from commun.modele import Camera

FICHIER = Path("cache/empreintes.json")
EXCLUES = ("CAMERAS", "CHANGEMENTS")
BLENDER = "/opt/homebrew/bin/blender"
RACINE = Path(__file__).resolve().parent.parent

# Entrée, document d'aménagement : variante -> module des données
PIECE = "entree"
DOCUMENT = "amenagement"
MODULES = {"principale": "document", "victor": "victor"}
CODE = (Path("pieces/entree/amenagement/rendu.py"), Path("3d/rendu.py"))


def _json(v):
    if dataclasses.is_dataclass(v) and not isinstance(v, type):
        return dataclasses.asdict(v)
    if isinstance(v, (set, frozenset)):
        return sorted(v, key=repr)
    return repr(v)


def donnees_variante(*modules) -> dict:
    """Constantes en majuscules des modules (la pièce, puis la variante), sans CAMERAS ni CHANGEMENTS."""
    return {f"{m.__name__}.{k}": v
            for m in modules for k, v in vars(m).items()
            if k.isupper() and k not in EXCLUES and not k.startswith("_")}


def empreinte(camera: Camera, donnees_variante: dict, reglages: dict, code: str, blender: str) -> str:
    entree = dict(camera=dataclasses.asdict(camera), donnees=donnees_variante, reglages=reglages, code=code,
                  blender=blender)
    return hashlib.sha256(json.dumps(entree, sort_keys=True, default=_json).encode()).hexdigest()


def _lire(fichier: Path) -> dict:
    try:
        return json.loads(fichier.read_text())
    except (FileNotFoundError, json.JSONDecodeError):
        return {}


def a_rendre(cle: str, emp: str, fichier: Path = FICHIER) -> bool:
    return _lire(fichier).get(cle) != emp


def noter(cle: str, emp: str, fichier: Path = FICHIER) -> None:
    notes = _lire(fichier)
    notes[cle] = emp
    fichier.parent.mkdir(parents=True, exist_ok=True)
    fichier.write_text(json.dumps(notes, indent=1, sort_keys=True) + "\n")


# ------------------------------------------------------------------ ligne de commande
def _empreintes(variante: str, echantillons: str) -> dict:
    sys.path.insert(0, str(RACINE))
    piece = importlib.import_module("pieces.entree.piece")
    module = importlib.import_module(f"pieces.entree.amenagement.{MODULES[variante]}")
    donnees = donnees_variante(piece, module)
    code = "".join((RACINE / f).read_text() for f in CODE)
    blender = subprocess.run([BLENDER, "--version"], capture_output=True, text=True).stdout.splitlines()[0]
    reglages = {"echantillons": int(echantillons)}
    return {c.id: empreinte(c, donnees, reglages, code, blender) for c in piece.CAMERAS}


def _cle(variante: str, camera: str) -> str:
    return f"{PIECE}/{DOCUMENT}/{variante}/{camera}"


def main(argv: list[str]) -> int:
    action, variante, echantillons, *vues = argv
    emps = _empreintes(variante, echantillons)
    inconnues = [v for v in vues if v not in emps]
    if inconnues:
        print(f"caméra inconnue : {', '.join(inconnues)}", file=sys.stderr)
        return 1
    if action == "liste":   # caméras demandées, sinon celles dont l'empreinte a changé
        print(" ".join(vues or [c for c, e in emps.items() if a_rendre(_cle(variante, c), e)]))
    elif action == "noter":
        for c in vues:
            noter(_cle(variante, c), emps[c])
    else:
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
