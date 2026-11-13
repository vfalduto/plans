"""Outils communs aux tests."""
import importlib.util
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
