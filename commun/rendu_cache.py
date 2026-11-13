"""Cache des rendus : une empreinte par caméra et par variante, notée une fois l'image rendue.

Une vue est refaite quand sa caméra, les données de sa variante (et de la pièce), les réglages, le code de rendu ou la
version de Blender changent. Changer une caméra ne refait que cette caméra ; changer un meuble ne refait que les vues
de sa variante.

Chaque document déclare ce qui entre dans l'empreinte de ses rendus par une constante `CACHE_RENDU` (voir
`CacheRendu`) dans `pieces/<piece>/<document>/document.py`.

En ligne de commande (utilisé par les recettes `<piece>-<document>-rendu`) :
    python3 -m commun.rendu_cache variantes <piece>/<document>
    python3 -m commun.rendu_cache liste <piece>/<document> <variante> <échantillons> [caméra ...]
    python3 -m commun.rendu_cache noter <piece>/<document> <variante> <échantillons> <caméra> [caméra ...]
La variante d'identifiant vide (document sans variante) s'écrit `-`.
"""
import dataclasses
import hashlib
import importlib
import json
import os
import subprocess
import sys
from pathlib import Path

from commun.modele import Camera

FICHIER = Path("cache/empreintes.json")
# textes et constantes de page seulement : le rendu ne les lit pas (DOCUMENT, construit à la première lecture, décrit
# la page)
EXCLUES = ("CAMERAS", "CHANGEMENTS", "VERSION", "BASE", "ZONES", "RENDUS", "FIGEES_ANCIENNES", "DOCUMENT",
           "CACHE_RENDU")
BLENDER = os.environ.get("BLENDER", "/opt/homebrew/bin/blender")
RACINE = Path(__file__).resolve().parent.parent
USAGE = """usage :
    python3 -m commun.rendu_cache variantes <piece>/<document>
    python3 -m commun.rendu_cache liste <piece>/<document> <variante> <échantillons> [caméra ...]
    python3 -m commun.rendu_cache noter <piece>/<document> <variante> <échantillons> <caméra> [caméra ...]
(variante `-` : document sans variante)"""


@dataclasses.dataclass(frozen=True)
class CacheRendu:
    """Ce qui entre dans l'empreinte des rendus d'un document.

    variantes : identifiant de variante (dans l'ordre des rendus, `""` pour un document sans variante) -> modules de
        données, dans l'ordre ; un nom sans point est un module du paquet du document, un nom avec point est pris tel
        quel. L'ordre et les noms comptent : ils entrent dans l'empreinte.
    code : fichiers dont le texte entre dans l'empreinte, chemins depuis la racine du dépôt, dans l'ordre.
    cameras : module qui porte CAMERAS ; vide, celui de la pièce (`pieces.<piece>.piece`)."""
    variantes: dict
    code: tuple
    cameras: str = ""


class Erreur(Exception):
    """Erreur de déclaration ou d'appel, dite sur stderr sans trace Python."""


def _json(v):
    """Écriture JSON de ce que json ne sait pas écrire seul : un objet de données (dataclass) et un ensemble (trié).
    Tout le reste (fonction, classe, objet quelconque) est refusé : son `repr` porte souvent une adresse mémoire, qui
    change d'un processus à l'autre et referait les rendus à chaque lancement."""
    if dataclasses.is_dataclass(v) and not isinstance(v, type):
        return dataclasses.asdict(v)
    if isinstance(v, (set, frozenset)):
        return sorted(v, key=lambda x: json.dumps(x, sort_keys=True, default=_json))
    raise TypeError(f"{type(v).__name__} n'est pas une donnée du modèle ({v!r:.80})")


def donnees_variante(*modules) -> dict:
    """Constantes en majuscules des modules (la pièce, puis la variante), sans les constantes de page (EXCLUES).

    Ce doivent être des données (nombres, textes, listes, dictionnaires, dataclasses) : une constante que `_json`
    refuse lève TypeError, avec son nom."""
    donnees = {f"{m.__name__}.{k}": v
               for m in modules for k, v in vars(m).items()
               if k.isupper() and k not in EXCLUES and not k.startswith("_")}
    for nom, v in donnees.items():
        try:
            json.dumps(v, sort_keys=True, default=_json)
        except TypeError as e:
            raise TypeError(f"empreinte des rendus, {nom} : {e} ; la renommer en _{nom.rsplit('.', 1)[1]} ou "
                            "l'ajouter à EXCLUES si le rendu ne la lit pas") from None
    return donnees


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
def _paquet(document: str) -> str:
    """`sdb/meuble-bas` -> `pieces.sdb.meuble_bas` : un nom de paquet Python ne prend pas de tiret."""
    return "pieces." + document.replace("/", ".").replace("-", "_")


def _importer(nom: str, quoi: str):
    try:
        return importlib.import_module(nom)
    except ModuleNotFoundError as e:
        # seul le module cherché (ou un de ses paquets) manque : une importation cassée plus loin garde sa trace
        if e.name and (nom == e.name or nom.startswith(e.name + ".")):
            raise Erreur(f"{quoi} ({nom})") from None
        raise


def declaration(document: str) -> CacheRendu:
    paquet = _paquet(document)
    module = _importer(f"{paquet}.document", f"document introuvable : {document}")
    if not hasattr(module, "CACHE_RENDU"):
        raise Erreur(f"CACHE_RENDU absente de {paquet}.document")
    return module.CACHE_RENDU


def _version_blender() -> str:
    return subprocess.run([BLENDER, "--version"], capture_output=True, text=True).stdout.splitlines()[0]


def empreintes(document: str, variante: str, echantillons: str) -> dict:
    """Empreinte de chaque caméra du document pour une variante (`""` : sans variante)."""
    cache = declaration(document)
    if variante not in cache.variantes:
        raise Erreur(f"variante non déclarée pour {document} : {variante or '-'}")
    paquet = _paquet(document)
    modules = [_importer(m if "." in m else f"{paquet}.{m}", f"module de données introuvable pour {document}")
               for m in cache.variantes[variante]]
    absents = [f for f in cache.code if not (RACINE / f).is_file()]
    if absents:
        raise Erreur(f"fichier de code absent : {', '.join(absents)}")
    cameras = _importer(cache.cameras or paquet.rsplit(".", 1)[0] + ".piece",
                        f"module des caméras introuvable pour {document}").CAMERAS
    donnees = donnees_variante(*modules)
    code = "".join((RACINE / f).read_text() for f in cache.code)
    blender = _version_blender()
    reglages = {"echantillons": int(echantillons)}
    return {c.id: empreinte(c, donnees, reglages, code, blender) for c in cameras}


def _cle(document: str, variante: str, camera: str) -> str:
    return f"{document}/{variante}/{camera}" if variante else f"{document}/{camera}"


def _commande(argv: list[str]) -> None:
    if argv[:1] == ["variantes"] and len(argv) == 2:
        print(" ".join(v or "-" for v in declaration(argv[1]).variantes))
        return
    if not (argv[:1] == ["liste"] and len(argv) >= 4 or argv[:1] == ["noter"] and len(argv) >= 5):
        raise Erreur(USAGE)
    action, document, variante, echantillons, *vues = argv
    variante = "" if variante == "-" else variante
    emps = empreintes(document, variante, echantillons)
    inconnues = [v for v in vues if v not in emps]
    if inconnues:
        raise Erreur(f"caméra inconnue : {', '.join(inconnues)}")
    if action == "liste":   # caméras demandées, sinon celles dont l'empreinte a changé
        print(" ".join(vues or [c for c, e in emps.items() if a_rendre(_cle(document, variante, c), e, FICHIER)]))
    else:
        for c in vues:
            noter(_cle(document, variante, c), emps[c], FICHIER)


def main(argv: list[str]) -> int:
    try:
        _commande(argv)
    except Erreur as e:
        print(e, file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
