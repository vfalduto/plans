"""Cache des rendus : une empreinte par caméra et par variante, notée une fois l'image rendue.

Une vue est refaite quand sa caméra, les données de sa variante (et de la pièce), les réglages, le code de rendu ou la
version de Blender changent. Changer une caméra ne refait que cette caméra ; changer un meuble ne refait que les vues
de sa variante.

Chaque document déclare ce qui entre dans l'empreinte de ses rendus par une constante `CACHE_RENDU` (voir
`CacheRendu`) dans `pieces/<piece>/<document>/document.py`.

En ligne de commande (les recettes `just rendu` et `just rendu-apercu` appellent `rendre` et `apercu`) :
    python3 -m commun.rendu_cache variantes <piece>/<document>
    python3 -m commun.rendu_cache liste <piece>/<document> <variante> <échantillons> [caméra ...]
    python3 -m commun.rendu_cache noter <piece>/<document> <variante> <échantillons> <caméra> [caméra ...]
    python3 -m commun.rendu_cache rendre <piece>/<document> [<échantillons> [caméra ...]]
    python3 -m commun.rendu_cache apercu <piece>/<document> [caméra ...]
La variante d'identifiant vide (document sans variante) s'écrit `-`. La version de Blender, qui entre dans l'empreinte,
est demandée à `BLENDER_REEL` s'il est défini, sinon à `BLENDER` (défaut /opt/homebrew/bin/blender).
"""
import dataclasses
import hashlib
import importlib
import json
import os
import shutil
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
    python3 -m commun.rendu_cache rendre <piece>/<document> [<échantillons> [caméra ...]]
    python3 -m commun.rendu_cache apercu <piece>/<document> [caméra ...]
(variante `-` : document sans variante)"""


@dataclasses.dataclass(frozen=True)
class CacheRendu:
    """Ce qui entre dans l'empreinte des rendus d'un document.

    variantes : identifiant de variante (dans l'ordre des rendus, `""` pour un document sans variante) -> modules de
        données, dans l'ordre ; un nom sans point est un module du paquet du document, un nom avec point est pris tel
        quel. L'ordre et les noms comptent : ils entrent dans l'empreinte.
    code : fichiers dont le texte entre dans l'empreinte, chemins depuis la racine du dépôt, dans l'ordre.
    cameras : module qui porte CAMERAS ; vide, celui de la pièce (`pieces.<piece>.piece`).

    Le lancement de Blender (`rendre`, `apercu`) est décrit par les champs suivants, qui n'entrent pas dans l'empreinte :
    script : script Blender (chemin depuis la racine) ; sortie : (variable d'environnement du dossier de sortie, dossier
        par défaut depuis la racine) ; apercu : variable d'environnement qui vaut 1 pour l'aperçu ; variante_env :
        variable qui reçoit la variante ; png : nom de l'image écrite par le script, avec {variante} (vide, sans
        variante) et {camera}, plus le suffixe d'un réglage ; argument : nom de la caméra donné au script ({camera}) ;
        masque : le script écrit aussi <png sans .png>-masque.png ; rendues : variantes à rendre (toutes si vide) ;
        reglages : « module:fonction » qui renvoie [(variable, valeur, suffixe de fichier)], un Blender par ligne
        (sans réglage, un seul Blender) ; avant, avant_apercu : commande lancée d'abord (« just … ») ;
        copie_apercu : fichiers du dossier de sortie recopiés dans cache/apercu/ avant un aperçu.
    Image publiée : site/<piece>/<document>/rendus/[<variante>-]<caméra><suffixe>.jpg (+ -masque.png)."""
    variantes: dict
    code: tuple
    cameras: str = ""
    script: str = ""
    sortie: tuple = ("", "3d/sortie")
    apercu: str = ""
    variante_env: str = ""
    png: str = ""
    argument: str = "{camera}"
    masque: bool = False
    rendues: tuple = ()
    reglages: str = ""
    avant: str = ""
    avant_apercu: str = ""
    copie_apercu: tuple = ()


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
            raise TypeError(f"empreinte des rendus, {nom} : {e} ; la renommer en _{nom.rsplit('.', 1)[1]}"
                            " (un nom en _X reste hors de l'empreinte)") from None
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
    """Première ligne de `--version`, demandée à `BLENDER_REEL` s'il est défini (le Blender que lance
    blender-seul.sh : la question n'attend pas le verrou d'un rendu), sinon à `BLENDER`. Code non nul ou sortie vide
    (attente du verrou expirée) : `Erreur`, avec la sortie d'erreur de la commande."""
    binaire = os.environ.get("BLENDER_REEL") or BLENDER
    try:
        r = subprocess.run([binaire, "--version"], capture_output=True, text=True)
    except OSError as e:
        raise Erreur(f"version de Blender : {binaire} ne se lance pas ({e})") from None
    lignes = r.stdout.splitlines()
    if r.returncode != 0 or not lignes:
        raise Erreur(f"version de Blender : `{binaire} --version` sort en {r.returncode} sans version"
                     + (f" ; {r.stderr.strip()}" if r.stderr.strip() else ""))
    return lignes[0]


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
    if argv[:1] == ["rendre"] and len(argv) >= 2:
        rendre(argv[1], *(argv[2:3] or ["64"]), vues=argv[3:])
        return
    if argv[:1] == ["apercu"] and len(argv) >= 2:
        apercu(argv[1], argv[2:])
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


# ------------------------------------------------------------------ lancement de Blender

DEFAUT_BLENDER = "/opt/homebrew/bin/blender"


def _cameras(document: str) -> list[str]:
    cache = declaration(document)
    return [c.id for c in _importer(cache.cameras or _paquet(document).rsplit(".", 1)[0] + ".piece",
                                    f"module des caméras introuvable pour {document}").CAMERAS]


def _reglages(cache: CacheRendu, apercu: bool = False) -> list[tuple]:
    """[(variable, valeur, suffixe)] : un Blender par ligne ; un seul réglage vide sans déclaration, le premier
    seulement pour un aperçu (SALON_ESSENCE=… dans l'environnement pour un autre)."""
    if not cache.reglages:
        return [("", "", "")]
    module, fonction = cache.reglages.split(":")
    lignes = list(getattr(importlib.import_module(module), fonction)())
    return lignes[:1] if apercu else lignes


def _lancer_blender(cache: CacheRendu, env: dict, echantillons: str, cameras: list[str]) -> None:
    blender = os.environ.get("BLENDER", DEFAUT_BLENDER)
    cmd = [blender, "-b", "--python-exit-code", "1", "--python", cache.script, "--", echantillons,
           *(cache.argument.format(camera=c) for c in cameras)]
    subprocess.run(cmd, cwd=RACINE, env=env, check=True)


def _png(cache: CacheRendu, dossier: Path, variante: str, camera: str, suffixe: str = "") -> Path:
    nom = cache.png.format(variante=variante, camera=camera)
    return dossier / (nom[:-len(".png")] + suffixe + ".png")


def _masque(png: Path) -> Path:
    return png.with_name(png.stem + "-masque.png")


def rendre(document: str, echantillons: str = "64", vues: list[str] | None = None) -> None:
    """Rend les caméras dont l'empreinte a changé (ou celles nommées), copie les images dans
    site/<piece>/<document>/rendus/, note les empreintes, puis reconstruit la page du document."""
    cache = declaration(document)
    if not cache.script:
        raise Erreur(f"{document} : pas de rendu Blender déclaré (CACHE_RENDU.script)")
    var_sortie, defaut = cache.sortie
    dossier = Path(os.environ.get(var_sortie) or RACINE / defaut)
    if not dossier.is_absolute():
        dossier = RACINE / dossier
    destination = RACINE / "site" / document / "rendus"
    destination.mkdir(parents=True, exist_ok=True)
    env = {**os.environ, var_sortie: str(dossier)}
    rendues = [v for v in cache.variantes if not cache.rendues or v in cache.rendues]
    fait = False
    for variante in rendues:
        emps = empreintes(document, variante, echantillons)
        inconnues = [v for v in vues or [] if v not in emps]
        if inconnues:
            raise Erreur(f"caméra inconnue : {', '.join(inconnues)}")
        cles = vues or [c for c, e in emps.items() if a_rendre(_cle(document, variante, c), e, FICHIER)]
        if not cles:
            print(f"{document} {variante or '-'} : rien à rendre")
            continue
        fait = True
        print(f"{document} {variante or '-'} : {' '.join(cles)}")
        if cache.avant:
            subprocess.run(cache.avant, shell=True, cwd=RACINE, check=True, env=env)
        env_v = {**env, **({cache.variante_env: variante} if cache.variante_env else {})}
        for var, valeur, suffixe in _reglages(cache):
            for c in cles:   # aucun reste d'un ancien rendu à copier
                png = _png(cache, dossier, variante, c, suffixe)
                png.unlink(missing_ok=True)
                _masque(png).unlink(missing_ok=True)
            _lancer_blender(cache, {**env_v, **({var: valeur} if var else {})}, echantillons, cles)
            for c in cles:
                nom = (f"{variante}-{c}" if variante else c) + suffixe
                source = _png(cache, dossier, variante, c, suffixe)
                if not source.is_file():
                    raise Erreur(f"le script n'a pas écrit {source}")
                subprocess.run(["sips", "-s", "format", "jpeg", "-s", "formatOptions", "85", str(source), "--out",
                                str(destination / f"{nom}.jpg")], check=True, capture_output=True)
                if cache.masque:
                    shutil.copy(_masque(source), destination / f"{nom}-masque.png")
        for c in cles:
            noter(_cle(document, variante, c), emps[c], FICHIER)
    if fait:
        subprocess.run([sys.executable, "site.py", document], cwd=RACINE, check=True)


def apercu(document: str, vues: list[str] | None = None) -> None:
    """Aperçu rapide (16 échantillons, 800 × 600) de toutes les variantes rendues, dans cache/apercu/ : ni cache ni
    copie dans site/. Sans caméra nommée, toutes les caméras du document."""
    cache = declaration(document)
    if not cache.script:
        raise Erreur(f"{document} : pas de rendu Blender déclaré (CACHE_RENDU.script)")
    var_sortie, defaut = cache.sortie
    origine = Path(os.environ.get(var_sortie) or RACINE / defaut)
    sortie = RACINE / "cache" / "apercu"
    sortie.mkdir(parents=True, exist_ok=True)
    if cache.avant_apercu:
        subprocess.run(cache.avant_apercu, shell=True, cwd=RACINE, check=True, env={**os.environ, var_sortie: str(origine)})
    for f in cache.copie_apercu:
        shutil.copy(origine / f, sortie / f)
    cameras = vues or _cameras(document)
    ecrites = []
    for variante in [v for v in cache.variantes if not cache.rendues or v in cache.rendues]:
        env = {**os.environ, var_sortie: str(sortie), cache.apercu: "1",
               **({cache.variante_env: variante} if cache.variante_env else {})}
        for var, valeur, suffixe in _reglages(cache, apercu=True):
            _lancer_blender(cache, {**env, **({var: valeur} if var and var not in os.environ else {})}, "16", cameras)
            ecrites += [_png(cache, sortie, variante, c, suffixe) for c in cameras]
    for f in ecrites:
        print(f)


def main(argv: list[str]) -> int:
    try:
        _commande(argv)
    except Erreur as e:
        print(e, file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
