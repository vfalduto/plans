"""Construction de site/ : passerelle, accueil, journal, historiques et versions figées.

Le site d'essai est celui de site.py (passerelles), plus le document d'essai, construit dans une copie réduite de la
racine (pages, archives et images, sans le code ni les rendus Blender).
"""
import dataclasses
import importlib.util
import json
import posixpath
import re
import shutil
from dataclasses import dataclass
from html import unescape
from pathlib import Path

import pytest
from outils import RACINE, balises, charger_site

from commun.construction import commande, construire, copier_passerelle, figer
from commun.journal import depuis_page
from commun.modele import Document, Passerelle, Piece, Site

# ce qui n'est pas publié : code, documentation, sorties Blender, outils
NON_COPIES = {"3d", "docs", "tests", "pieces", "site", "cache", "achats", "reddit", "explorations", "__pycache__"}


def _charger_essai():
    spec = importlib.util.spec_from_file_location("essai_document", RACINE / "tests/fixtures/essai/document.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


ESSAI = _charger_essai()


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
    _communs_d_essai(racine)
    site = Site(charger_site().SITE.pieces + ESSAI.SITE.pieces)
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


def _contenu(html):
    return re.search(r'<main class="contenu" id="contenu">.*</main>', html, flags=re.S).group(0)


def _rail(html, depuis):
    """Le <nav id="rail"> d'une page, sans le lien courant, les adresses ramenées à la racine de site/."""
    nav = re.search(r'<nav class="rail tapis" id="rail".*?</nav>', html, flags=re.S).group(0)
    nav = nav.replace(' aria-current="page"', "").replace('class="piece ici"', 'class="piece"')
    dossier = posixpath.dirname(depuis)
    return re.sub(r'href="([^"]*)"', lambda m: f'href="{posixpath.normpath(posixpath.join(dossier, m.group(1)))}"', nav)


# ------------------------------------------------------------------ tests du brief

def test_passerelle_garde_les_adresses(construit):
    sortie = construit.sortie
    page = sortie / "cuisine-v13.html"
    assert page.exists()
    images = [r for r in _references(_lire(page)) if r.lower().endswith((".jpg", ".jpeg", ".png", ".svg", ".webp"))]
    assert len(images) > 10
    manquantes = [r for r in images if not (sortie / r).is_file()]
    assert manquantes == []
    assert (sortie / "archive/entree-amenagement-v1.html").exists()
    accueil = _lire(sortie / "index.html")
    assert balises(accueil, "svg", classe="plan-appart")
    assert balises(accueil, "nav", id="rail")


def test_journal_complet(construit):
    attendu = 0
    for piece in construit.site.pieces:
        for doc in piece.documents:
            if isinstance(doc, Passerelle):
                attendu += len(depuis_page(_lire(construit.racine / doc.page)))
            else:
                attendu += sum(len(v.changements) for v in doc.variantes)
    journal = _lire(construit.sortie / "journal.html")
    lignes = [li for li in balises(journal, "li") if "data-piece" in li]
    assert attendu > 100
    assert len(lignes) == attendu
    assert balises(journal, "select", id="filtre-piece")


def test_menu_identique(construit):
    sortie = construit.sortie
    pages = {"index.html": "index.html", "journal.html": "journal.html",
             "essai/amenagement/index.html": "essai/amenagement/"}
    rails = {f: _rail(_lire(sortie / f), depuis) for f, depuis in pages.items()}
    assert rails["index.html"] == rails["journal.html"] == rails["essai/amenagement/index.html"]
    assert 'href="cuisine-v13.html"' in rails["index.html"]


def test_figer(construit):
    sortie = construit.sortie
    rendus = sortie / "essai/amenagement/rendus"
    rendus.mkdir(parents=True, exist_ok=True)
    (rendus / "b-banc.jpg").write_bytes(b"jpg")

    dossier = figer(construit.site, construit.racine, sortie, "essai/amenagement/b")
    assert dossier == sortie / "archive/essai-amenagement-b-v0.3"
    assert "Coupe D" in _lire(dossier / "index.html")
    assert (dossier / "rendus/b-banc.jpg").read_bytes() == b"jpg"
    table = json.loads(_lire(sortie / "archive/figees.json"))
    assert table["essai/amenagement/b"] == [["V0.3", "archive/essai-amenagement-b-v0.3/"]]

    # figer deux fois la même version ne la duplique pas
    figer(construit.site, construit.racine, sortie, "essai/amenagement/b")
    assert len(json.loads(_lire(sortie / "archive/figees.json"))["essai/amenagement/b"]) == 1

    construire(construit.site, (), construit.racine, sortie, seulement="essai/amenagement")
    historique = _lire(sortie / "essai/amenagement/historique.html")
    assert 'href="../../archive/essai-amenagement-b-v0.3/"' in historique
    assert "13 novembre 2026" in historique

    # la page figée se lit telle quelle : sans choix de variante ni comparaison, et sans lien mort
    page = _lire(dossier / "index.html")
    assert balises(page, "body")[0].get("data-figee") == "V0.3"
    assert not balises(page, "select", id="c-variante")
    assert not balises(page, "button", id="c-comp")
    assert not balises(page, "select", id="c-autre") and not balises(page, "label", classe="b-avec")
    assert balises(page, "a", classe="version")[0]["href"] == "../../essai/amenagement/historique.html"
    assert _liens_morts(sortie, "archive/essai-amenagement-b-v0.3/index.html") == []
    assert _contenu(page) == _contenu(_lire(sortie / "essai/amenagement/b.html"))


def test_figer_sans_lien_mort_entre_documents(tmp_path):
    """Les liens vers les autres documents de la pièce (menu, choix du document) mènent aux pages en cours."""
    _communs_d_essai(tmp_path)
    autre = dataclasses.replace(ESSAI.DOCUMENT, id="autre", nom="Autre")
    site = Site((Piece("essai", "Essai", (ESSAI.DOCUMENT, autre)),))
    construire(site, (), tmp_path, tmp_path / "site")
    figer(site, tmp_path, tmp_path / "site", "essai/autre/c")
    page = _lire(tmp_path / "site/archive/essai-autre-c-v0.1/index.html")
    assert [o["value"] for o in balises(page, "option")] == ["../../essai/amenagement/", "../../essai/autre/"]
    assert _liens_morts(tmp_path / "site", "archive/essai-autre-c-v0.1/index.html") == []


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


def test_copier_passerelle_exclues(tmp_path):
    racine, sortie = tmp_path / "racine", tmp_path / "site"
    (racine / "archive/photos").mkdir(parents=True)
    (racine / "img").mkdir()
    (racine / "img/a.jpg").write_bytes(b"a")
    (racine / "img/b.png").write_bytes(b"b")
    (racine / "archive/photos/c.jpg").write_bytes(b"c")
    (tmp_path / "hors.txt").write_text("hors de la racine")
    (racine / "index.html").write_text("ancien accueil")
    (racine / "vieux.html").write_text('<img src="img/b.png">')
    (racine / "page.html").write_text(
        '<a href="index.html">accueil</a><img src="img/a.jpg?v=3"><a href="vieux.html#x">vieux</a>'
        '<a href="https://exemple.fr/x.jpg">loin</a><img src="data:image/png;base64,AAAA"><a href="#ici">ici</a>'
        '<img src="img/absente.jpg"><a href="../hors.txt">hors</a>')
    (racine / "archive/v1.html").write_text('<a href="../index.html">accueil</a><img src="photos/c.jpg">')

    copiees = copier_passerelle(racine, sortie, {"vieux.html"})
    assert copiees == ["archive/photos/c.jpg", "archive/v1.html", "img/a.jpg", "page.html"]
    assert not (sortie / "index.html").exists()
    assert not (sortie / "vieux.html").exists()
    assert (sortie / "img/a.jpg").read_bytes() == b"a"


def test_plan_appartement(monkeypatch):
    from commun.appartement import plan_appartement
    from pieces.entree import piece as entree

    site = charger_site().SITE
    svg = plan_appartement(site)
    liens = re.findall(r'<a href="([^"]*)" aria-label="([^"]*)">', svg)
    assert ("cuisine-v13.html", "Cuisine") in liens
    assert ("entree-amenagement.html", "Entrée") in liens
    assert ("chambre-amenagement.html", "Chambre") in liens
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
    assert (sortie / "archive/essai-amenagement-v1.2/index.html").exists()
    assert "archive/essai-amenagement-v1.2/" in _lire(sortie / "essai/amenagement/historique.html")


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


def test_documents_declares():
    site = charger_site().SITE
    assert [p.id for p in site.pieces] == ["cuisine", "sdb", "entree", "salon", "chambre"]
    pages = [d.page for p in site.pieces for d in p.documents if isinstance(d, Passerelle)]
    assert pages == ["cuisine-v13.html", "cuisine-v13-porte-cellier.html", "sdb-meuble-bas.html",
                     "sdb-meuble-haut.html", "entree-amenagement.html", "salon-v4.html", "salon-etageres.html",
                     "salon-enfilade.html", "chambre-amenagement.html"]
    assert not any(isinstance(d, Document) for p in site.pieces for d in p.documents)
    assert charger_site().REDIRECTIONS == ()


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

    Les pages de la passerelle, recopiées telles quelles, gardent leurs styles : on ne regarde que celles qui ont
    le menu de la refonte.
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
    assert _liens_morts(sortie, "archive/essai-amenagement-b-v0.3/index.html") == []
