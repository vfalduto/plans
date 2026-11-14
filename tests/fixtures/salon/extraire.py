"""Capture les dessins SVG que produisent les anciens générateurs du salon (3d/salon/), pour prouver après la migration
que les dessins n'ont pas changé.

  python3 tests/fixtures/salon/extraire.py

Chaque page (salon-v4.html, salon-etageres.html, salon-enfilade.html) est générée en mémoire par son ancien
générateur (rien n'est écrit à la racine) ; chaque <svg> de la page est écrit tel quel dans ce dossier, sous un nom
tiré de son document, de son aria-label, de la disposition des étagères (bloc data-d) et de la configuration de la
table (bloc cf / co). index.json donne, pour chaque fichier, la page, le titre h2 de la section, la disposition, la
configuration, l'aria-label et le rang du dessin dans la page.

À lancer depuis n'importe où ; il importe 3d/salon/ comme le font les anciens générateurs.
"""
import importlib
import json
import re
import sys
import unicodedata
from html.parser import HTMLParser
from pathlib import Path

ICI = Path(__file__).resolve().parent
RACINE = ICI.parents[2]
ANCIEN = RACINE / "3d" / "salon"
VIDES = {"br", "img", "input", "meta", "link", "hr", "wbr", "source", "col", "area", "base", "embed", "track"}


def slug(texte):
    t = unicodedata.normalize("NFKD", texte).encode("ascii", "ignore").decode().lower()
    return re.sub(r"[^a-z0-9]+", "-", t).strip("-")


class _Dessins(HTMLParser):
    """Repère chaque <svg> de premier niveau : position dans la source et éléments ouverts autour de lui."""

    def __init__(self):
        super().__init__(convert_charrefs=False)
        self.pile, self.dessins, self.h2, self.dans_h2, self.dans_svg = [], [], "", False, 0

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if self.dans_svg:
            self.dans_svg += tag == "svg"
            return
        if tag == "svg":
            self.dans_svg = 1
            dispo = next((d.get("data-d") for t, d in reversed(self.pile) if d.get("data-d")), "")
            config = next((c for t, d in reversed(self.pile) for c in d.get("class", "").split() if c in ("cf", "co")), "")
            self.dessins.append(dict(debut=self.getpos(), label=a.get("aria-label", ""), section=self.h2,
                                     disposition=dispo, config=config[1:]))
            return
        if tag == "h2":
            self.dans_h2, self.h2 = True, ""
        if tag not in VIDES:
            self.pile.append((tag, a))

    def handle_startendtag(self, tag, attrs):
        pass

    def handle_endtag(self, tag):
        if self.dans_svg:
            self.dans_svg -= tag == "svg"
            if not self.dans_svg:
                self.dessins[-1]["fin"] = self.getpos()
            return
        if tag == "h2":
            self.dans_h2 = False
        while self.pile:
            if self.pile.pop()[0] == tag:
                break

    def handle_data(self, data):
        if self.dans_h2:
            self.h2 += data


def dessins(html):
    """[(svg, infos)] dans l'ordre de la page."""
    p = _Dessins()
    p.feed(html)
    p.close()
    debuts = [0]
    for ligne in html.splitlines(keepends=True):
        debuts.append(debuts[-1] + len(ligne))
    pos = lambda lc: debuts[lc[0] - 1] + lc[1]  # noqa: E731
    res = []
    for d in p.dessins:
        a, b = pos(d.pop("debut")), pos(d.pop("fin"))
        b = html.index(">", b) + 1
        res.append((html[a:b], d))
    return res


def anciens():
    sys.path.insert(0, str(ANCIEN))
    try:
        return {n: importlib.import_module(n) for n in ("plan", "etageres", "enfilade")}
    finally:
        sys.path.remove(str(ANCIEN))


def main():
    m = anciens()
    pages = {
        "amenagement": ("salon-v4.html", m["plan"].page(m["plan"].lire_figees())),
        "etageres": ("salon-etageres.html", m["etageres"].page()),
        "enfilade": ("salon-enfilade.html", m["enfilade"].page()[0]),
    }
    for vieux in ICI.glob("*.svg"):
        vieux.unlink()
    index = {}
    for doc, (page, html) in pages.items():
        vus = {}
        for rang, (svg, d) in enumerate(dessins(html)):
            nom = "-".join(x for x in (doc, slug(d["label"]) or "sans-titre", d["disposition"], d["config"]) if x)
            vus[nom] = vus.get(nom, 0) + 1
            if vus[nom] > 1:
                nom += f"-{vus[nom]}"
            (ICI / f"{nom}.svg").write_text(svg, encoding="utf-8")
            index[f"{nom}.svg"] = dict(page=page, rang=rang, **d)
        print(f"{page} : {sum(vus.values())} dessins")
    (ICI / "index.json").write_text(json.dumps(index, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
