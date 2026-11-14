"""Outils communs aux tests."""
import importlib
import importlib.util
import json
import subprocess
import sys
from html.parser import HTMLParser
from pathlib import Path

RACINE = Path(__file__).resolve().parent.parent


class _Collecteur(HTMLParser):
    def __init__(self, nom):
        super().__init__()
        self.nom = nom
        self.trouvees = []

    def handle_starttag(self, tag, attrs):
        if tag == self.nom:
            self.trouvees.append({k: (v if v is not None else "") for k, v in attrs})

    handle_startendtag = handle_starttag


def balises(html, nom, **attrs):
    """Attributs de chaque balise `nom` qui contient `attrs`.

    `classe=` teste un mot de `class`."""
    p = _Collecteur(nom)
    p.feed(html)
    p.close()
    classe = attrs.pop("classe", None)
    res = []
    for a in p.trouvees:
        if classe is not None and classe not in a.get("class", "").split():
            continue
        if all(a.get(k) == v for k, v in attrs.items()):
            res.append(a)
    return res


def charger_site():
    """Charge site.py sous le nom `site_plans` (`import site` renvoie le module standard)."""
    spec = importlib.util.spec_from_file_location("site_plans", RACINE / "site.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


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
