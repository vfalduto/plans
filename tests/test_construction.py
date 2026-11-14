"""Construction de site/ : accueil, journal, historiques et versions figées.

Le site d'essai est celui de site.py, plus la pièce d'essai (le document d'essai), construit dans une copie réduite
de la racine (sans le code ni les rendus Blender).
"""
import dataclasses
import importlib.util
import json
import posixpath
import re
import shutil
from collections import Counter
from dataclasses import dataclass
from html import unescape
from pathlib import Path

import pytest
from outils import RACINE, balises, charger_site

from commun.construction import commande, construire, figer
from commun.gabarit import adresse
from commun.modele import Document, Piece, Site

# ce qui n'est pas publié : code, documentation, sorties Blender, outils
NON_COPIES = {"3d", "docs", "tests", "pieces", "site", "cache", "achats", "reddit", "explorations", "__pycache__"}


def _charger_essai():
    spec = importlib.util.spec_from_file_location("essai_document", RACINE / "tests/fixtures/essai/document.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


ESSAI = _charger_essai()

# pages de site/ qui ne sont pas des redirections : écrites par la construction, ou la page de la porte du cellier
# (figée par décision du client, retirée du menu)
HORS_DOCUMENTS = {"index.html", "journal.html", "cuisine-v13-porte-cellier.html"}


def _instantane(racine, sauf=("site", "cache")):
    """Date de modification de chaque fichier de `racine`, hors des dossiers `sauf`."""
    res = {}
    for f in racine.rglob("*"):
        rel = f.relative_to(racine)
        if rel.parts[0] in sauf or not f.is_file():
            continue
        res[rel.as_posix()] = f.stat().st_mtime_ns
    return res


@dataclass
class Construit:
    racine: Path
    sortie: Path
    site: Site
    avant: dict


def _communs_d_essai(racine):
    """site.css et site.js vides s'ils manquent (tâche 5), pour que les liens de l'en-tête mènent à un fichier."""
    for rel in ("commun/site.css", "commun/site.js"):
        f = racine / rel
        if not f.exists():
            f.parent.mkdir(parents=True, exist_ok=True)
            f.write_text("")


@pytest.fixture(scope="module")
def construit(tmp_path_factory):
    racine = tmp_path_factory.mktemp("racine")
    for f in RACINE.iterdir():
        if f.name.startswith(".") or f.name in NON_COPIES:
            continue
        if f.is_dir():
            shutil.copytree(f, racine / f.name)
        else:
            shutil.copy2(f, racine / f.name)
    shutil.copytree(RACINE / "site" / "archives", racine / "site" / "archives")   # pages figées, jamais régénérées
    shutil.copytree(RACINE / "site" / "images", racine / "site" / "images")
    _communs_d_essai(racine)
    site = Site(charger_site().SITE.pieces + (Piece("essai", "Essai", (ESSAI.DOCUMENT,)),))
    avant = _instantane(racine)
    construire(site, (), racine, racine / "site")
    return Construit(racine, racine / "site", site, avant)


def _lire(chemin):
    return chemin.read_text(encoding="utf-8")


def _references(html):
    """Chemins locaux des attributs src et href (sans fragment ni requête)."""
    res = set()
    for v in re.findall(r"""(?:src|href)\s*=\s*["']([^"']+)["']""", html):
        if v.startswith(("#", "http:", "https:", "data:", "mailto:", "//")):
            continue
        v = v.split("#")[0].split("?")[0]
        if v:
            res.add(v)
    return res


def _liens_morts(sortie, rel):
    """Adresses relatives d'une page de site/ (href, src, documents de #c-doc, #variantes) sans fichier derrière."""
    html = _lire(sortie / rel)
    urls = re.findall(r'(?:href|src)="([^"]*)"', html)
    choix = re.search(r'<select class="nu" id="c-doc".*?</select>', html, flags=re.S)
    if choix:
        urls += [o["value"] for o in balises(choix.group(0), "option")]
    variantes = re.search(r'<script type="application/json" id="variantes">(.*?)</script>', html, flags=re.S)
    urls += [v[2] for v in json.loads(variantes.group(1))]
    morts = []
    for u in urls:
        u = unescape(u)
        if u.startswith(("#", "//")) or re.match(r"^[a-z][a-z0-9+.-]*:", u):
            continue
        cible = sortie / posixpath.normpath(posixpath.join(posixpath.dirname(rel), u.split("#")[0].split("?")[0]))
        if cible.is_dir():
            cible = cible / "index.html"
        if not cible.is_file():
            morts.append(u)
    return morts


def _documents(site):
    return [d for p in site.pieces for d in p.documents if isinstance(d, Document)]


def _contenu(html):
    return re.search(r'<main class="contenu" id="contenu">.*</main>', html, flags=re.S).group(0)


def _rail(html, depuis):
    """Le <nav id="rail"> d'une page, sans le lien courant, les adresses ramenées à la racine de site/."""
    nav = re.search(r'<nav class="rail tapis" id="rail".*?</nav>', html, flags=re.S).group(0)
    nav = nav.replace(' aria-current="page"', "").replace('class="piece ici"', 'class="piece"')
    dossier = posixpath.dirname(depuis)
    return re.sub(r'href="([^"]*)"', lambda m: f'href="{posixpath.normpath(posixpath.join(dossier, m.group(1)))}"', nav)


# ------------------------------------------------------------------ tests du brief

def test_accueil_et_archives(construit):
    sortie = construit.sortie
    assert (sortie / "archives/entree-amenagement-v1.html").exists()
    accueil = _lire(sortie / "index.html")
    assert balises(accueil, "svg", classe="plan-appart")
    assert balises(accueil, "nav", id="rail")


def test_journal_complet(construit):
    """Chaque document a dans le journal autant de lignes, sous son lien, qu'il a de changements déclarés."""
    attendu = Counter()
    for doc in _documents(construit.site):
        for v in doc.variantes:
            attendu[adresse(doc, v.id)] += len(v.changements)
    journal = _lire(construit.sortie / "journal.html")
    lignes = re.findall(r'<li data-piece="[^"]*">(.*?)</li>', journal, flags=re.S)
    vu = Counter(re.search(r'<a href="([^"]*)"', li).group(1) for li in lignes)
    assert vu == +attendu
    assert balises(journal, "select", id="filtre-piece")


def test_menu_identique(construit):
    sortie = construit.sortie
    pages = {"index.html": "index.html", "journal.html": "journal.html",
             "essai/amenagement/index.html": "essai/amenagement/"}
    rails = {f: _rail(_lire(sortie / f), depuis) for f, depuis in pages.items()}
    assert rails["index.html"] == rails["journal.html"] == rails["essai/amenagement/index.html"]
    # le menu mène au dossier de chaque document
    for doc in _documents(construit.site):
        assert f'href="{posixpath.normpath(adresse(doc))}"' in rails["index.html"], adresse(doc)


def test_figer(construit):
    sortie = construit.sortie
    rendus = sortie / "essai/amenagement/rendus"
    rendus.mkdir(parents=True, exist_ok=True)
    (rendus / "b-banc.jpg").write_bytes(b"jpg")

    dossier = figer(construit.site, construit.racine, sortie, "essai/amenagement/b")
    assert dossier == sortie / "archives/essai-amenagement-b-v0.3"
    assert "Coupe D" in _lire(dossier / "index.html")
    assert (dossier / "rendus/b-banc.jpg").read_bytes() == b"jpg"
    table = json.loads(_lire(sortie / "archives/figees.json"))
    assert table["essai/amenagement/b"] == [["V0.3", "archives/essai-amenagement-b-v0.3/"]]

    # figer deux fois la même version ne la duplique pas
    figer(construit.site, construit.racine, sortie, "essai/amenagement/b")
    assert len(json.loads(_lire(sortie / "archives/figees.json"))["essai/amenagement/b"]) == 1

    construire(construit.site, (), construit.racine, sortie, seulement="essai/amenagement")
    historique = _lire(sortie / "essai/amenagement/historique.html")
    assert 'href="../../archives/essai-amenagement-b-v0.3/"' in historique
    assert "13 novembre 2026" in historique

    # la page figée se lit telle quelle : sans choix de variante ni comparaison, et sans lien mort
    page = _lire(dossier / "index.html")
    assert balises(page, "body")[0].get("data-figee") == "V0.3"
    assert not balises(page, "select", id="c-variante")
    assert not balises(page, "button", id="c-comp")
    assert not balises(page, "select", id="c-autre") and not balises(page, "label", classe="b-avec")
    assert balises(page, "a", classe="version")[0]["href"] == "../../essai/amenagement/historique.html"
    assert _liens_morts(sortie, "archives/essai-amenagement-b-v0.3/index.html") == []
    assert _contenu(page) == _contenu(_lire(sortie / "essai/amenagement/b.html"))


def test_figer_sans_lien_mort_entre_documents(tmp_path):
    """Les liens vers les autres documents de la pièce (menu, choix du document) mènent aux pages en cours."""
    _communs_d_essai(tmp_path)
    autre = dataclasses.replace(ESSAI.DOCUMENT, id="autre", nom="Autre")
    site = Site((Piece("essai", "Essai", (ESSAI.DOCUMENT, autre)),))
    construire(site, (), tmp_path, tmp_path / "site")
    figer(site, tmp_path, tmp_path / "site", "essai/autre/c")
    page = _lire(tmp_path / "site/archives/essai-autre-c-v0.1/index.html")
    assert [o["value"] for o in balises(page, "option")] == ["../../essai/amenagement/", "../../essai/autre/"]
    assert _liens_morts(tmp_path / "site", "archives/essai-autre-c-v0.1/index.html") == []


def test_construire_n_ecrit_que_site_et_cache(construit):
    assert _instantane(construit.racine) == construit.avant


# ------------------------------------------------------------------ compléments

def test_pages_des_documents(construit):
    sortie = construit.sortie
    for chemin in ("essai/amenagement/index.html", "essai/amenagement/b.html", "essai/amenagement/c.html"):
        html = _lire(sortie / chemin)
        assert html.startswith("<!doctype html>")
        assert len(balises(html, "section", classe="vue")) == 5
    historique = _lire(sortie / "essai/amenagement/historique.html")
    for v in ESSAI.VARIANTES:
        for c in v.changements:
            assert c.texte in historique
    assert [h for h in re.findall(r"<h2[^>]*>(.*?)</h2>", historique)] == ["A", "B", "C"]


def test_fichiers_communs(construit):
    sortie = construit.sortie
    favicon = _lire(sortie / "favicon.svg")
    assert 'fill="#000000c7"' in favicon and "#5f7a5c" not in favicon
    png = (sortie / "apple-touch-icon.png").read_bytes()
    assert png[:8] == b"\x89PNG\r\n\x1a\n"
    assert int.from_bytes(png[16:20]) == 180 and int.from_bytes(png[20:24]) == 180


def test_plan_appartement(monkeypatch):
    from commun.appartement import APPART, plan_appartement
    from pieces.entree import piece as entree

    site = charger_site().SITE
    svg = plan_appartement(site)
    liens = re.findall(r'<a href="([^"]*)" aria-label="([^"]*)">', svg)
    # chaque pièce mène à son premier document, un document
    assert {href for href, _ in liens} == {adresse(p.documents[0]) for p in site.pieces}
    # chaque lien porte le nom de son contour (le cellier mène à la cuisine) : couples (adresse, libellé)
    pieces = {p.id: p for p in site.pieces}
    assert set(liens) == {(adresse(pieces[c.vers or c.id].documents[0]), c.nom) for c in APPART if not c.inerte}
    assert ("entree/amenagement/", "Entrée") in liens
    assert not any(nom in ("WC", "Pièce ouest", "Placard") for _, nom in liens)
    # le contour de l'entrée vient de pieces/entree/piece.py, décalé de POSITION
    monkeypatch.setattr(entree, "POSITION", (10, 20, 0))
    decale = " ".join(f"{x + 10},{y + 20}" for x, y in entree.SOL)
    assert f'points="{decale}"' in plan_appartement(site)


def test_commande_seulement(tmp_path):
    racine = tmp_path
    site = Site(ESSAI.SITE.pieces)
    assert commande(site, (), racine, ["essai/amenagement"]) == 0
    sortie = racine / "site"
    assert (sortie / "essai/amenagement/b.html").exists()
    assert (sortie / "journal.html").exists() and (sortie / "index.html").exists()
    assert commande(site, (), racine, ["essai/inconnu"]) != 0
    assert commande(site, (), racine, ["--figer", "essai/amenagement"]) == 0
    assert (sortie / "archives/essai-amenagement-v1.2/index.html").exists()
    assert "archives/essai-amenagement-v1.2/" in _lire(sortie / "essai/amenagement/historique.html")


def test_seulement_rafraichit_le_menu(tmp_path):
    """Reconstruire un document met à jour sa version dans le menu des pages déjà construites des autres."""
    autre = dataclasses.replace(ESSAI.DOCUMENT, id="autre", nom="Autre")
    piece = Piece("essai", "Essai", (ESSAI.DOCUMENT, autre))
    construire(Site((piece,)), (), tmp_path, tmp_path / "site")
    v = dataclasses.replace(autre.variantes[0], version="V9.9")
    autre2 = dataclasses.replace(autre, variantes=(v,) + autre.variantes[1:])
    construire(Site((Piece("essai", "Essai", (ESSAI.DOCUMENT, autre2)),)), (), tmp_path, tmp_path / "site",
               seulement="essai/autre")
    for f in ("essai/amenagement/index.html", "essai/amenagement/c.html", "essai/amenagement/historique.html",
              "index.html", "journal.html"):
        assert '<span class="num txt">V9.9</span>' in _lire(tmp_path / "site" / f), f


def test_documents_declares(construit):
    """Propriétés de site.py vraies à chaque étape de la migration, quelles que soient les pages déjà migrées."""
    from pieces.entree.amenagement import document

    module = charger_site()
    site = module.SITE
    assert [p.id for p in site.pieces] == ["cuisine", "sdb", "entree", "salon", "chambre"]
    # l'entrée est migrée (tâche 16) : son document, à sa place dans le menu
    (entree,) = [p for p in site.pieces if p.id == "entree"]
    assert entree.documents == (document.DOCUMENT,)
    # chaque document se construit : ses pages et son historique, sans lien mort (les rendus/ viennent des recettes
    # de rendu, pas de la construction)
    for doc in _documents(site):
        for rel in [adresse(doc, v.id) for v in doc.variantes] + [f"{doc.piece}/{doc.id}/historique.html"]:
            rel = rel + "index.html" if rel.endswith("/") else rel
            morts = [u for u in _liens_morts(construit.sortie, rel) if not u.startswith("rendus/")]
            assert morts == [], (rel, morts)
    # aucune page à la racine du dépôt (les anciennes adresses sont des redirections de site/)
    assert sorted(p.name for p in RACINE.glob("*.html")) == []
    # chaque page de la racine de site/ est une redirection, une page générée, ou la porte du cellier (figée)
    connues = {r.ancienne for r in module.REDIRECTIONS} | HORS_DOCUMENTS
    assert sorted(p.name for p in (RACINE / "site").glob("*.html") if p.name not in connues) == []
    # chaque redirection mène à une page qu'écrit la construction : celle d'un document ou son historique
    # (ou, depuis la tâche 10 de la cuisine, une de ses annexes ; une version figée, sous site/archives/)
    construites = {a for d in _documents(site) for a in [adresse(d, v.id) for v in d.variantes]
                   + [f"{d.piece}/{d.id}/historique.html"] + [adresse(d, d.variantes[0].id) + x.nom for x in d.annexes]}
    construites |= {c for d in _documents(site) for v in d.variantes for _, c in v.figees
                    if (RACINE / "site" / c).is_file()}
    for r in module.REDIRECTIONS:
        for cible in (r.cible, *r.pages.values()):
            page = cible.split("#")[0]
            assert page in construites or (page.startswith("archives/") and (RACINE / "site" / page).is_file()), (r.ancienne, cible)


# documents nés sans ancienne page (« <piece>/<document> ») : dispensés d'une Redirection
SANS_ANCIENNE_PAGE = set()


def _modules_documents():
    """(dossier de la pièce, module) de chaque pieces/<piece>/<document>/document.py qui porte DOCUMENT."""
    res = []
    for f in sorted((RACINE / "pieces").glob("*/*/document.py")):
        module = importlib.import_module(".".join(f.relative_to(RACINE).with_suffix("").parts))
        if hasattr(module, "DOCUMENT"):
            res.append((f.parts[-3], module))
    return res


def _non_declares(site, modules):
    """Modules dont le DOCUMENT n'est pas dans SITE, dans la pièce de son dossier : perdu à une fusion de site.py."""
    pieces = {p.id: p.documents for p in site.pieces}
    return [m.__name__ for dossier, m in modules
            if not any(isinstance(d, Document) and d.id == m.DOCUMENT.id for d in pieces.get(dossier, ()))
            or m.DOCUMENT.piece != dossier]


def _sans_redirection(site, redirections, dispenses=frozenset()):
    """Documents de SITE qu'aucune Redirection ne désigne : leur ancienne page, perdue à une fusion, resterait morte."""
    menent = {c for r in redirections for c in (r.cible, *r.pages.values())}
    return [f"{d.piece}/{d.id}" for d in _documents(site) if f"{d.piece}/{d.id}" not in dispenses
            and not menent & {adresse(d, v.id) for v in d.variantes}]


def _vues_inconnues(site, redirections):
    """Vues visées par `ancres` et `motifs` d'une Redirection qui n'existent pas dans le type du document cible."""
    from commun.modele import VUES
    par_page = {adresse(d, v.id): d for d in _documents(site) for v in d.variantes}
    res = []
    for r in redirections:
        doc = par_page.get(r.cible)
        visees = list(r.ancres.values()) + [gabarit for _, gabarit in r.motifs]
        res += [(r.ancienne, v) for v in visees if doc is None or v.split("?")[0] not in VUES[doc.type]]
    return res


def _caches_faux(site):
    """Documents dont CACHE_RENDU ne déclare pas exactement ses variantes : une variante oubliée n'est jamais rendue."""
    res = []
    for d in _documents(site):
        module = importlib.import_module(f"pieces.{d.piece}.{d.id.replace('-', '_')}.document")
        cache = getattr(module, "CACHE_RENDU", None)
        if cache is not None and set(cache.variantes) != {v.id for v in d.variantes}:
            res.append((f"{d.piece}/{d.id}", sorted(cache.variantes), [v.id for v in d.variantes]))
    return res


def test_site_py_tient_documents_et_redirections():
    """Ce que huit branches qui touchent SITE et REDIRECTIONS peuvent perdre à la fusion, sans liste figée."""
    from commun.redirections import Redirection

    module = charger_site()
    site, redirections = module.SITE, module.REDIRECTIONS
    modules = _modules_documents()
    assert modules, "aucun document migré sur le disque"
    assert _non_declares(site, modules) == []
    assert _sans_redirection(site, redirections, SANS_ANCIENNE_PAGE) == []
    assert _vues_inconnues(site, redirections) == []
    assert _caches_faux(site) == []
    # chaque garde voit la faute qu'elle doit voir
    sans_entree = Site(tuple(dataclasses.replace(p, documents=()) if p.id == "entree" else p for p in site.pieces))
    assert "pieces.entree.amenagement.document" in _non_declares(sans_entree, modules)
    deplace = Site(tuple(dataclasses.replace(p, documents=()) if p.id == "entree" else
                         dataclasses.replace(p, documents=p.documents + (modules[0][1].DOCUMENT,)) if p.id == "salon"
                         else p for p in site.pieces))
    assert _non_declares(deplace, modules) != []
    # sans liste figée : sans redirection, chaque document migré est signalé, et lui seul ; dispensés, plus aucun
    migres = [f"{d.piece}/{d.id}" for d in _documents(site)]
    assert "entree/amenagement" in migres and _sans_redirection(site, ()) == migres
    assert _sans_redirection(site, (), set(migres)) == []
    faute = (Redirection("vieux.html", "entree/amenagement/", {"plan": "plans"}, ((r"^c-(a)", "coupe?k={1}"),)),)
    assert _vues_inconnues(site, faute) == [("vieux.html", "plans"), ("vieux.html", "coupe?k={1}")]
    entree = next(d for d in _documents(site) if d.id == "amenagement" and d.piece == "entree")
    oubli = dataclasses.replace(entree, variantes=entree.variantes + (dataclasses.replace(entree.variantes[0],
                                                                                           id="oubliee"),))
    assert _caches_faux(Site((Piece("entree", "Entrée", (oubli,)),))) != []


def test_historique_de_l_entree(construit):
    """Les versions figées de la principale viennent de FIGEES_ANCIENNES (pas de archives/figees.json), avec leur date ;
    puis le journal de chaque variante."""
    from pieces.entree.amenagement import document, victor

    historique = _lire(construit.sortie / "entree/amenagement/historique.html")
    table = construit.sortie / "archives/figees.json"   # test_figer y écrit les variantes d'essai, rien de l'entrée
    assert not table.exists() or not any(c.startswith("entree/") for c in json.loads(_lire(table)))
    assert re.findall(r"<h2[^>]*>(.*?)</h2>", historique) == ["Principale", "Victor"]
    figees = re.findall(r'<ul class="figees">(.*?)</ul>', historique, re.S)
    assert len(figees) == 1, "seule la principale a des versions figées"
    for version, chemin in document.FIGEES_ANCIENNES:
        assert f'<li><a href="../../{chemin}">{version}</a> <span class="date">1 octobre 2026</span></li>' in figees[0]
        assert (construit.sortie / chemin).is_file(), chemin
    journaux = re.findall(r'<ol class="fil">(.*?)</ol>', historique, re.S)
    assert [j.count("<li>") for j in journaux] == [len(document.CHANGEMENTS), len(victor.CHANGEMENTS)]


def test_workflow_publie_site():
    """Le workflow publie site/ et aucun fichier de site/ n'est un lien symbolique."""
    flux = (RACINE / ".github" / "workflows" / "pages.yml").read_text(encoding="utf-8")
    assert "path: site" in flux
    assert "upload-pages-artifact@v3" in flux
    assert "deploy-pages@v5" in flux
    liens = [p for p in (RACINE / "site").rglob("*") if p.is_symlink()]
    assert not liens, f"liens symboliques dans site/ : {liens[:5]}"


def test_pas_de_style_dans_le_corps(construit):
    """Les styles sont dans commun/site.css : aucune page construite ne porte de <style> après <body.

    On ne regarde que les pages qui ont le menu de la refonte (pas les archives ni la porte du cellier).
    """
    pages = [p for p in sorted(construit.sortie.rglob("*.html")) if 'id="rail"' in _lire(p)]
    assert len(pages) > 5
    fautives = [p.relative_to(construit.sortie).as_posix() for p in pages
                if "<style" in _lire(p)[_lire(p).index("<body"):]]
    assert not fautives, fautives


def test_dessins_css_ecrit(tmp_path):
    from commun.css_dessins import css_dessins
    css = ".room{fill:red}.absente{fill:blue}svg text{fill:black}"
    doc = dataclasses.replace(ESSAI.DOCUMENT, css=css)
    site = Site((Piece("essai", "Essai", (doc,)),))
    racine, sortie = tmp_path / "racine", tmp_path / "site"
    racine.mkdir()
    _communs_d_essai(racine)
    construire(site, (), racine, sortie)
    ecrit = (sortie / "essai/amenagement/dessins.css").read_text(encoding="utf-8")
    scenes = [e.scene for v in ESSAI.VARIANTES for vue in doc.generer(v.id).values() for e in vue.elements]
    assert ecrit == css_dessins(css, scenes, ".d-essai") + "\n"
    # sans css : aucun fichier
    sortie2 = tmp_path / "site2"
    construire(ESSAI.SITE, (), racine, sortie2)
    assert not (sortie2 / "essai/amenagement/dessins.css").exists()


def test_figer_garde_le_css_des_dessins(tmp_path):
    """Une version figée est autonome : son dessins.css, et chaque lien de l'en-tête mène à un fichier."""
    _communs_d_essai(tmp_path)
    def generer(variante):
        vues = ESSAI.DOCUMENT.generer(variante)
        for vue in vues.values():
            for e in vue.elements:
                e.scene = e.scene.replace("<rect ", '<rect class="room" ')
        return vues

    doc = dataclasses.replace(ESSAI.DOCUMENT, css=".room{fill:red}.absente{fill:blue}", generer=generer)
    site = Site((Piece("essai", "Essai", (doc,)),))
    sortie = tmp_path / "site"
    construire(site, (), tmp_path, sortie)
    dossier = figer(site, tmp_path, sortie, "essai/amenagement/b")
    page = _lire(dossier / "index.html")
    assert 'href="dessins.css"' in page
    assert (dossier / "dessins.css").is_file()
    assert _lire(dossier / "dessins.css") == ".d-essai .room{fill:red}\n"
    assert _lire(dossier / "dessins.css") == _lire(sortie / "essai/amenagement/dessins.css")
    assert balises(page, "main")[0]["class"] == "contenu d-essai"
    assert len(balises(page, "section", classe="vue")) == 5
    tete = page.split("</head>")[0]
    for u in _references(tete):
        assert (dossier / u).resolve().is_file(), u
    assert _liens_morts(sortie, "archives/essai-amenagement-b-v0.3/index.html") == []


# ------------------------------------------------------------------ pages annexes d'un document
def _fichiers(dossier):
    return sorted(str(f.relative_to(dossier)) for f in dossier.rglob("*") if f.is_file())


def test_annexe_ecrite(tmp_path):
    """Une `Annexe` est écrite dans le dossier du document ; `ecrire` reçoit son chemin sous site/."""
    from commun.modele import Annexe
    doc = dataclasses.replace(ESSAI.DOCUMENT, annexes=(Annexe("annexe.html", lambda d: f"<p>{d}</p>"),))
    construire(Site((Piece("essai", "Essai", (doc,)),)), (), tmp_path, tmp_path / "site")
    assert _lire(tmp_path / "site/essai/amenagement/annexe.html") == "<p>essai/amenagement/annexe.html</p>"


def test_sans_annexe_rien_de_neuf(tmp_path):
    """Un document sans annexe écrit exactement les mêmes fichiers qu'avant ; une annexe n'ajoute que sa page."""
    from commun.modele import Annexe
    assert ESSAI.DOCUMENT.annexes == ()
    construire(Site((Piece("essai", "Essai", (ESSAI.DOCUMENT,)),)), (), tmp_path / "a", tmp_path / "a/site")
    doc = dataclasses.replace(ESSAI.DOCUMENT, annexes=(Annexe("annexe.html", lambda d: "<p></p>"),))
    construire(Site((Piece("essai", "Essai", (doc,)),)), (), tmp_path / "b", tmp_path / "b/site")
    sans, avec = _fichiers(tmp_path / "a/site"), _fichiers(tmp_path / "b/site")
    assert sorted(set(avec) - set(sans)) == ["essai/amenagement/annexe.html"] and set(sans) <= set(avec)
