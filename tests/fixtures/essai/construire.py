"""Construit le site d'essai dans cache/essai-site/ pour les tests du navigateur (tests/navigateur/).

Il contient les trois variantes du document d'essai (document.py), écrites par commun/gabarit.py aux adresses du
site, avec commun/site.css, commun/site.js et l'icône. tests/navigateur/lancer.sh le lance puis le sert.

    python3 tests/fixtures/essai/construire.py
"""
import importlib.util
import shutil
import sys
from pathlib import Path

RACINE = Path(__file__).resolve().parents[3]
if str(RACINE) not in sys.path:
    sys.path.insert(0, str(RACINE))

from commun.gabarit import adresse, page_document  # noqa: E402
from commun.modele import verifier  # noqa: E402
from commun.redirections import Redirection, page_redirection  # noqa: E402

SORTIE = RACINE / "cache" / "essai-site"
COMMUNS = ("commun/site.css", "commun/site.js", "favicon.svg")

# anciennes adresses de l'essai (tests/navigateur/redirections.js) : à la racine et dans un sous-dossier
REDIRECTIONS = (
    Redirection("ancienne.html", "essai/amenagement/", {"plan": "plan", "iso": "iso"},
                ((r"^coupe-([a-d])-", "coupes?k={1}"),)),
    Redirection("vieux/ancienne.html", "essai/amenagement/b.html", {"plan": "plan"},
                ((r"^coupe-([a-d])-", "coupes?k={1}"),)),
)


def _essai():
    spec = importlib.util.spec_from_file_location("essai_document", Path(__file__).with_name("document.py"))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def construire(sortie: Path = SORTIE) -> Path:
    essai = _essai()
    doc = essai.DOCUMENT
    if sortie.exists():
        shutil.rmtree(sortie)
    for v in doc.variantes:
        vues = doc.generer(v.id)
        verifier(doc, vues)
        chemin = adresse(doc, v.id)
        fichier = sortie / (chemin + "index.html" if chemin.endswith("/") else chemin)
        fichier.parent.mkdir(parents=True, exist_ok=True)
        fichier.write_text(page_document(essai.SITE, doc, v, vues), encoding="utf-8")
    for r in REDIRECTIONS:
        fichier = sortie / r.ancienne
        fichier.parent.mkdir(parents=True, exist_ok=True)
        fichier.write_text(page_redirection(r, r.ancienne), encoding="utf-8")
    for nom in COMMUNS:
        source = RACINE / nom
        if not source.exists():
            # pas d'arrêt : le test du navigateur doit pouvoir échouer sur l'absence du fichier
            print(f"construire.py : {nom} absent, non copié", file=sys.stderr)
            continue
        (sortie / nom).parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(source, sortie / nom)
    return sortie


if __name__ == "__main__":
    print(f"Site d'essai écrit dans {construire().relative_to(RACINE)}/")
