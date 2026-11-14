"""Fige les sorties de l'ancienne page cuisine-v13.html et de ses générateurs (3d/v13/), pour que les tâches de la
migration s'y comparent après la disparition de l'ancienne page.

  python3 tests/fixtures/cuisine/extraire.py

La page est générée en mémoire par plan.page(plan.lire_figees()) : aucune page de la racine n'est écrite. Écrit dans
ce dossier :
- dessins/<nom>.svg : les sept <svg> de la partie courante, tels qu'ils sont dans la page ;
- legendes.json : {id: html intérieur} des 22 légendes (p.cap, figcaption.cap) de la partie courante ;
- tableaux.json : {id: html du <table>} des 9 tableaux de la partie courante ;
- ancres.json : [{id, bloc, texte}] de chaque h2 (id calculé comme 3d/ancres.js), puis les autres id de la page ;
- index.json : pour chaque dessin, sa fonction source dans plan.py, son aria-label, le nombre de caractères de texte ;
- imprimable.html, porte-cellier.html : imprimable.page() et porte.page() ;
- maquette.html : copie de cuisine-v13-maquette.html (écrite à la main, pas de générateur) ;
- modele.json : les données de 3d/v13/modele.py, comme les lit commun.rendu_cache.donnees_variante ;
- rendu.json : COUPES_ISO et COUPES_ISO_NO de 3d/v13/rendu.py (lus par ast : le script importe bpy).
"""
import ast
import html
import importlib
import json
import re
import shutil
import sys
import types
import unicodedata
from html.parser import HTMLParser
from pathlib import Path

ICI = Path(__file__).resolve().parent
RACINE = ICI.parents[2]
ANCIEN = RACINE / "3d" / "v13"
FIN_COURANTE = '<div class="ver" data-v="V11.49"'    # la partie courante de la page précède la première version figée

# dessin → fonction de plan.py qui le produit (la règle de taille est ajoutée à la coupe par page())
DESSINS = {"plan": "plan_svg", "coupe-a": "coupe_a", "hauteur-pt": "hauteur_pt_svg", "coupe-b": "coupe_b",
           "coupe-c": "coupe_c", "plan-elec": "plan_elec_svg", "elevation-elec": "coupe_elec_nord"}
# légendes, dans l'ordre de la page (p.cap et figcaption.cap mêlés)
LEGENDES = ("plan", "coupe-a", "hauteur-pt-etude", "hauteur-pt", "coupe-b", "coupe-c", "plan-elec", "interrupteurs",
            "elevation-elec", "nfc", "rendu-iso", "rendu-iso_nuit", "rendu-iso_no", "rendu-entree", "rendu-fenetre",
            "rendu-banquette", "rendu-dos_cellier", "rendu-cellier", "rendus-methode", "materiaux", "contenu",
            "capacite")
TABLEAUX = ("hauteur-pt", "tango", "interrupteurs", "points", "circuits", "materiaux", "contenu", "capacite",
            "changements")
VIDES = {"br", "img", "input", "meta", "link", "hr", "wbr", "source", "col", "area", "base", "embed", "track"}


def slug(texte):
    """Fonction slug de 3d/ancres.js."""
    t = unicodedata.normalize("NFD", texte)
    t = "".join(c for c in t if not "\u0300" <= c <= "\u036f").lower()
    return re.sub(r"[^a-z0-9]+", "-", t).strip("-") or "section"


def texte(fragment):
    """Texte sans balises, entités décodées."""
    return html.unescape(re.sub(r"<[^>]+>", "", fragment))


class _Titres(HTMLParser):
    """Repère les id de la page, et pour chaque h2 : son bloc, son texte, son id et celui de sa section."""

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.pile, self.ids, self.titres, self.h2 = [], [], [], None

    def bloc(self):
        return next((e["attrs"]["data-v"] for e in reversed(self.pile)
                     if e["tag"] == "div" and "ver" in (e["attrs"].get("class") or "").split()
                     and e["attrs"].get("data-v")), "courante")

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if a.get("id"):
            self.ids.append((a["id"], self.bloc()))
        if tag == "h2":
            parent = self.pile[-1] if self.pile else None
            section = parent["attrs"].get("id") if parent and parent["tag"] == "section" and parent["h2"] == 0 else None
            for e in self.pile:
                e["h2"] += 1
            self.h2 = dict(id=a.get("id") or "", section=section or "", bloc=self.bloc(), texte="", plein="",
                           profondeur=len(self.pile))
        if tag not in VIDES:
            self.pile.append(dict(tag=tag, attrs=a, h2=0))

    def handle_startendtag(self, tag, attrs):
        a = dict(attrs)
        if a.get("id"):
            self.ids.append((a["id"], self.bloc()))

    def handle_endtag(self, tag):
        if tag == "h2" and self.h2:
            self.titres.append(self.h2)
            self.h2 = None
        if tag in [e["tag"] for e in self.pile]:
            while self.pile.pop()["tag"] != tag:
                pass

    def handle_data(self, data):
        if self.h2 is not None:
            self.h2["plein"] += data
            if not any(e["tag"] in ("a", "span", "button") for e in self.pile[self.h2["profondeur"] + 1:]):
                self.h2["texte"] += data


def ancres(page):
    """[{id, bloc, texte}] de chaque h2 (id calculé comme 3d/ancres.js), puis les autres id de la page."""
    p = _Titres()
    p.feed(page)
    p.close()
    pris = {i for i, _ in p.ids}
    res = []
    for h in p.titres:
        t = h["texte"].strip() or h["plein"].strip()
        if h["id"]:
            ident = h["id"]
        elif h["section"]:
            ident = h["section"]
        else:
            suffixe = f"-{slug(h['bloc'])}" if h["bloc"] != "courante" else ""
            base, ident, k = slug(t) + suffixe, slug(t) + suffixe, 2
            while ident in pris:
                ident = f"{base}-{k}"
                k += 1
            pris.add(ident)
        res.append(dict(id=ident, bloc=h["bloc"], texte=t))
    vus = {a["id"] for a in res}
    res += [dict(id=i, bloc=b, texte="") for i, b in p.ids if i not in vus and not vus.add(i)]
    return res


def _liste(motif, source, attendu, quoi):
    trouves = re.findall(motif, source, flags=re.S)
    assert len(trouves) == len(attendu), f"{quoi} : {len(trouves)} trouvés, {len(attendu)} attendus"
    return dict(zip(attendu, trouves))


def extraire(page):
    """Les morceaux de la page : dessins, légendes, tableaux (partie courante seulement) et ancres (toute la page)."""
    courante = page[:page.index(FIN_COURANTE)]
    return dict(
        dessins=_liste(r"(<svg\b.*?</svg>)", courante, tuple(DESSINS), "dessins"),
        legendes=_liste(r'<(?:p|figcaption) class="cap">(.*?)</(?:p|figcaption)>', courante, LEGENDES, "légendes"),
        tableaux=_liste(r"(<table\b.*?</table>)", courante, TABLEAUX, "tableaux"),
        ancres=ancres(page))


def lire(dossier):
    """Les mêmes morceaux, lus dans `dossier`."""
    def json_(nom):
        return json.loads((dossier / nom).read_text(encoding="utf-8"))
    return dict(
        dessins={nom: (dossier / "dessins" / f"{nom}.svg").read_text(encoding="utf-8") for nom in DESSINS},
        legendes=json_("legendes.json"), tableaux=json_("tableaux.json"), ancres=json_("ancres.json"))


def anciens():
    """plan, imprimable, porte, modele de 3d/v13/, importés comme le font leurs scripts."""
    sys.path.insert(0, str(ANCIEN))
    try:
        return {n: importlib.import_module(n) for n in ("modele", "plan", "imprimable", "porte")}
    finally:
        sys.path[:] = [p for p in sys.path if p != str(ANCIEN)]


def donnees_modele(modele):
    """{nom: valeur} de commun.rendu_cache.donnees_variante, préfixe de module retiré. COLONNES_CONTENU (clés en
    tuples) est écartée : donnees_variante la refuse, et le nouveau module la nommera _COLONNES_CONTENU."""
    if str(RACINE) not in sys.path:
        sys.path.insert(0, str(RACINE))
    from commun import rendu_cache
    copie = types.ModuleType(modele.__name__)
    copie.__dict__.update({k: v for k, v in vars(modele).items() if k != "COLONNES_CONTENU"})
    donnees = {k.split(".", 1)[1]: v for k, v in rendu_cache.donnees_variante(copie).items()}
    return json.dumps(donnees, sort_keys=True, default=rendu_cache._json, ensure_ascii=False, indent=1)


def coupes_rendu():
    """COUPES_ISO et COUPES_ISO_NO, lus dans le source de 3d/v13/rendu.py."""
    res = {}
    for n in ast.parse((ANCIEN / "rendu.py").read_text(encoding="utf-8")).body:
        if isinstance(n, ast.Assign) and getattr(n.targets[0], "id", "") in ("COUPES_ISO", "COUPES_ISO_NO"):
            res[n.targets[0].id] = ast.literal_eval(n.value)
    return res


def ecrire(chemin, contenu):
    chemin.parent.mkdir(parents=True, exist_ok=True)
    chemin.write_text(contenu, encoding="utf-8")


def ecrire_json(nom, valeur):
    ecrire(ICI / nom, json.dumps(valeur, ensure_ascii=False, indent=1) + "\n")


def main():
    m = anciens()
    page = m["plan"].page(m["plan"].lire_figees())
    morceaux = extraire(page)
    for vieux in (ICI / "dessins").glob("*.svg"):
        vieux.unlink()
    for nom, svg in morceaux["dessins"].items():
        ecrire(ICI / "dessins" / f"{nom}.svg", svg)
    for nom in ("legendes", "tableaux", "ancres"):
        ecrire_json(f"{nom}.json", morceaux[nom])
    ecrire_json("index.json", {
        f"dessins/{nom}.svg": dict(source=f"plan.{DESSINS[nom]}", aria_label=re.search(r'aria-label="([^"]*)"', svg)[1],
                                   caracteres=len(texte(svg)))
        for nom, svg in morceaux["dessins"].items()})
    ecrire(ICI / "imprimable.html", m["imprimable"].page())
    ecrire(ICI / "porte-cellier.html", m["porte"].page())
    shutil.copyfile(RACINE / "cuisine-v13-maquette.html", ICI / "maquette.html")
    ecrire(ICI / "modele.json", donnees_modele(m["modele"]) + "\n")
    ecrire_json("rendu.json", coupes_rendu())
    print(f"{len(morceaux['dessins'])} dessins, {len(morceaux['legendes'])} légendes, {len(morceaux['tableaux'])} "
          f"tableaux, {len(morceaux['ancres'])} ancres")


if __name__ == "__main__":
    main()
