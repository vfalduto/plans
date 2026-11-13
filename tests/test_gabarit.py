"""Gabarit de page commun, vérifié sur le document d'essai."""
import dataclasses
import importlib.util
import json

from outils import RACINE, balises

from commun.gabarit import adresse, menu, page_document, page_simple, relatif
from commun.modele import VUES, Passerelle, Piece, Site


def _charger_essai():
    spec = importlib.util.spec_from_file_location("essai_document", RACINE / "tests/fixtures/essai/document.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


ESSAI = _charger_essai()
DOC = ESSAI.DOCUMENT


def _page(variante="a", doc=DOC):
    v = next(x for x in doc.variantes if x.id == variante)
    return page_document(ESSAI.SITE, doc, v, doc.generer(v.id))


def _entre(html, debut, fin):
    return html.split(debut, 1)[1].split(fin, 1)[0]


def _json(html, id):
    return json.loads(_entre(html, f'<script type="application/json" id="{id}">', "</script>"))


def test_onglets_dans_l_ordre():
    onglets = _entre(_page(), '<nav class="vues"', "</nav>")
    assert [a["data-vue"] for a in balises(onglets, "a")] == ["plan", "coupes", "iso", "camera", "explication"]


def test_onglet_vide_grise():
    iso = balises(_page(), "a", **{"data-vue": "iso"})
    assert len(iso) == 1
    assert iso[0].get("aria-disabled") == "true"
    assert iso[0].get("title") == "Pas encore rendu"
    plan = balises(_page(), "a", **{"data-vue": "plan"})[0]
    assert "aria-disabled" not in plan


def test_comparer_et_avec():
    trois = _page()
    assert balises(trois, "select", id="c-variante")
    assert balises(trois, "button", id="c-comp")
    assert balises(trois, "select", id="c-autre")
    assert "hidden" in balises(trois, "label", classe="b-avec")[0]

    deux = _page(doc=dataclasses.replace(DOC, variantes=DOC.variantes[:2]))
    assert balises(deux, "button", id="c-comp")
    assert not balises(deux, "select", id="c-autre")

    seule = _page(doc=dataclasses.replace(DOC, variantes=DOC.variantes[:1]))
    assert not balises(seule, "select", id="c-variante")
    assert not balises(seule, "button", id="c-comp")
    assert not balises(seule, "select", id="c-autre")


def test_adresses():
    assert adresse(DOC, "a") == "essai/amenagement/"
    assert adresse(DOC) == "essai/amenagement/"
    assert adresse(DOC, "b") == "essai/amenagement/b.html"
    assert adresse(Passerelle("essai", "porte", "Porte", "construction", "essai-porte.html")) == "essai-porte.html"

    assert relatif("commun/site.css", "essai/amenagement/b.html") == "../../commun/site.css"
    assert relatif("commun/site.css", "essai/amenagement/") == "../../commun/site.css"
    assert relatif("essai/amenagement/", "essai/amenagement/b.html") == "./"
    assert relatif("essai/amenagement/b.html", "index.html") == "essai/amenagement/b.html"

    page_b = _page("b")
    assert [x["href"] for x in balises(page_b, "link", rel="stylesheet") if "site.css" in x["href"]] == ["../../commun/site.css"]
    assert [x["src"] for x in balises(page_b, "script") if "src" in x] == ["../../commun/site.js"]
    assert "defer" in balises(page_b, "script", src="../../commun/site.js")[0]
    assert _json(page_b, "variantes") == [["a", "A", "./"], ["b", "B", "b.html"], ["c", "C", "c.html"]]


def test_menu_courant():
    rail = menu(ESSAI.SITE, ("essai", "amenagement"), "essai/amenagement/b.html")
    assert balises(rail, "nav", id="rail")
    assert balises(rail, "button", id="b-rail")
    assert [x["href"] for x in balises(rail, "a", **{"aria-current": "page"})] == ["./"]
    assert "Journal des changements" in rail
    assert balises(rail, "a", href="../../journal.html")
    assert '<svg class="plan' not in rail
    assert '<svg class="plan' not in _entre(_page(), '<nav class="rail', "</nav>")


def test_choix_du_document():
    assert not balises(_page(), "select", id="c-doc")
    porte = Passerelle("essai", "porte", "Porte", "construction", "essai-porte.html")
    site = Site((Piece("essai", "Essai", (DOC, porte)),))
    v = DOC.variantes[1]
    page = page_document(site, DOC, v, DOC.generer(v.id))
    assert balises(page, "select", id="c-doc")
    assert [(o["value"], "selected" in o) for o in balises(_entre(page, 'id="c-doc"', "</select>"), "option")] == [
        ("./", True), ("../../essai-porte.html", False)]
    assert balises(menu(site, None, "index.html"), "a", href="essai-porte.html", title="Porte (construction)")


def test_sans_js():
    # le doctype reste en tête : sans lui, le navigateur passe en mode quirks
    assert _page().startswith('<!doctype html>\n<html lang="fr" class="sans-js">')


def test_script_de_tete_avant_les_feuilles():
    # pas de flash des vues : le script en ligne pose html.js et html[data-vue] avant toute feuille de style
    for page, vues in ((_page("b"), '["plan", "coupes", "iso", "camera", "explication"]'),
                       (page_simple(ESSAI.SITE, "Journal", "", "journal.html"), "[]")):
        tete = _entre(page, "<head>", "</head>")
        assert "<script>" in tete
        assert tete.index("<script>") < tete.index("<link")
        script = _entre(tete, "<script>", "</script>")
        assert vues in script and "sans-js" in script and "data-vue" in script


def test_css_une_regle_par_vue():
    css = (RACINE / "commun/site.css").read_text(encoding="utf-8")
    assert "html:not(.sans-js) .contenu > .vue{display:none}" in css
    for k in {v for vues in VUES.values() for v in vues}:
        assert f'html[data-vue="{k}"] .contenu > .vue[data-vue="{k}"]' in css, k


def test_textes_interdits():
    for v in ("a", "b", "c"):
        page = _page(v)
        for interdit in ('type="checkbox"', "Copier la liste", "À venir", "prefers-color-scheme",
                         "Lecture du plan", "Lecture de la coupe"):
            assert interdit not in page, (v, interdit)


def test_corps_et_donnees():
    page = _page("b")
    corps = balises(page, "body")[0]
    assert (corps["data-type"], corps["data-piece"], corps["data-document"], corps["data-variante"]) == (
        "amenagement", "essai", "amenagement", "b")
    assert [o["id"] for o in _json(page, "options")] == ["teinte"]
    assert _json(page, "options")[0]["css"] == "--teinte"
    assert list(_json(page, "noms-vues")) == ["plan", "coupes", "iso", "camera", "explication"]
    assert balises(page, "button", id="c-options")
    assert balises(page, "a", classe="version", href="historique.html")
    assert "V0.3" in _entre(page, 'class="b-case version"', "</a>")


def test_sections():
    page = _page("b")
    sections = balises(page, "section", classe="vue")
    assert [s["data-vue"] for s in sections] == ["plan", "coupes", "iso", "camera", "explication"]
    assert sections[0]["data-outils"] == "zoom mesure"
    assert all(s["data-vide"] == "Pas encore rendu" for s in sections)

    coupes = _entre(page, '<section class="vue" data-vue="coupes"', "</section>")
    assert [e["data-k"] for e in balises(coupes, "div", classe="element")] == ["A", "B", "C", "D"]
    assert [b["data-k"] for b in balises(coupes, "button") if "data-k" in b] == ["A", "B", "C", "D"]
    assert [e["data-k"] for e in balises(coupes, "div", classe="fiche-element")] == ["A", "B", "C", "D"]
    assert balises(coupes, "div", classe="outils") and balises(coupes, "button", classe="b-mesure")
    assert balises(coupes, "div", classe="bandeau")
    assert balises(coupes, "aside", classe="fiche")

    camera = _entre(page, '<section class="vue" data-vue="camera"', "</section>")
    assert not balises(camera, "div", classe="segments")
    assert not balises(camera, "button", classe="b-mesure")

    explication = _entre(page, '<section class="vue" data-vue="explication"', "</section>")
    assert balises(explication, "article", classe="lecture")
    assert not balises(explication, "div", classe="scene")
    assert not balises(explication, "aside", classe="fiche")

    iso = _entre(page, '<section class="vue" data-vue="iso"', "</section>")
    assert "Pas encore rendu" in iso


def test_titre_de_fiche_autour_du_bouton():
    coupes = _entre(_page("b"), '<section class="vue" data-vue="coupes"', "</section>")
    tete = _entre(coupes, '<aside class="fiche">', '<div class="fiche-corps">')
    assert tete == ('<h2 class="fiche-titre"><button type="button" class="fiche-tete" aria-expanded="false">'
                    '<span class="fiche-nom">Coupe A-A</span><i class="chevron"></i></button></h2>')


def test_segment_inactif():
    doc = dataclasses.replace(DOC, generer=lambda v: {
        **DOC.generer(v),
        "coupes": dataclasses.replace(DOC.generer(v)["coupes"], elements=[
            dataclasses.replace(e, actif=e.k != "B") for e in DOC.generer(v)["coupes"].elements]),
    })
    coupes = _entre(_page(doc=doc), '<section class="vue" data-vue="coupes"', "</section>")
    b = balises(coupes, "button", **{"data-k": "B"})[0]
    assert "disabled" in b and b["title"] == "Pas encore rendu"
    assert "disabled" not in balises(coupes, "button", **{"data-k": "A"})[0]


def test_page_simple():
    page = page_simple(ESSAI.SITE, "Journal des changements", "<p>Rien</p>", "journal.html")
    assert page.startswith('<!doctype html>\n<html lang="fr" class="sans-js">')
    assert balises(page, "link", rel="stylesheet", href="commun/site.css")
    assert balises(page, "a", href="journal.html", **{"aria-current": "page"})
    assert not balises(page, "nav", classe="vues")
    historique = page_simple(ESSAI.SITE, "Historique", "", "essai/amenagement/historique.html",
                             courant=("essai", "amenagement"))
    assert balises(historique, "a", href="./", **{"aria-current": "page"})
