"""Document de construction d'essai (tests/fixtures/essai/meuble.py) et site d'essai à deux documents."""
import importlib.util
import posixpath
import re

from commun.gabarit import page_document
from commun.modele import VUES, verifier
from tests.outils import RACINE, balises

ESSAI = RACINE / "tests" / "fixtures" / "essai"


def _charger(nom, fichier):
    spec = importlib.util.spec_from_file_location(nom, ESSAI / fichier)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


MEUBLE = _charger("essai_meuble", "meuble.py")
CONSTRUIRE = _charger("essai_construire", "construire.py")
IDS = ("actuelle", "rangs", "escalier")


def _variante(id):
    return next(v for v in MEUBLE.DOCUMENT.variantes if v.id == id)


def _page(id):
    return page_document(MEUBLE.SITE, MEUBLE.DOCUMENT, _variante(id), MEUBLE.vues(id))


def _scene(vue):
    return vue.elements[0].scene


def test_meuble_verifie():
    assert [v.id for v in MEUBLE.DOCUMENT.variantes] == list(IDS)
    for id in IDS:
        vues = MEUBLE.vues(id)
        verifier(MEUBLE.DOCUMENT, vues)
        assert list(vues) == list(VUES["construction"])


def test_meuble_comparaison_plans():
    reperes = {id: [e.k for e in MEUBLE.vues(id)["plans"].elements] for id in IDS}
    assert reperes == {"actuelle": ["elevation", "iso"], "rangs": ["elevation", "iso"], "escalier": ["elevation"]}
    boites = {re.search(r'viewBox="([^"]+)"', _scene(MEUBLE.vues(id)["plans"])).group(1) for id in IDS}
    assert boites == {"0 0 300 140"}


def test_meuble_sans_objet():
    vues = MEUBLE.vues("rangs")
    assert vues["montage"].elements == []
    assert vues["montage"].vide == "Sans objet"
    page = _page("rangs")
    onglet = balises(page, "a", **{"data-vue": "montage"})
    assert len(onglet) == 1
    assert onglet[0].get("aria-disabled") == "true" and onglet[0].get("title") == "Sans objet"
    assert '"#montage"' not in vues["plans"].fiche
    assert '"#decoupe"' in vues["plans"].fiche


def test_meuble_vues_remplies():
    vues = MEUBLE.vues("actuelle")
    decoupe, montage, achats, explication = (_scene(vues[k]) for k in ("decoupe", "montage", "achats", "explication"))
    assert balises(decoupe, "table", classe="cartes") and balises(decoupe, "figure", classe="calepin")
    assert len(balises(montage, "ol", classe="etapes")) == 1
    assert len(balises(montage, "li")) == 3
    assert achats.count("Sous-total") == 2
    assert balises(achats, "p", classe="total-achats")
    assert balises(explication, "dl", classe="chiffres")
    assert '<a class="btn plein" href="#plans">Plans détaillés</a>' in explication


def test_meuble_escalier_quantite_apres_les_dimensions():
    entetes = re.findall(r"<th[^>]*>([^<]+)</th>", _scene(MEUBLE.vues("escalier")["decoupe"]))
    assert entetes.index("Nb") == entetes.index("Dimensions (cm)") + 1


def test_meuble_sous_totaux_au_centime():
    """Deux sections avec des centimes : `arrondi=False`, sous-totaux et total s'additionnent (mode d'emploi)."""
    achats = _scene(MEUBLE.vues("actuelle")["achats"])
    sous = re.findall(r'<tr class="total"><td>Sous-total</td><td></td><td></td><td class="num d">([^<]+)</td>', achats)
    assert sous == ["102,40 €", "25,35 €"]
    assert '<span class="num">127,75 €</span>' in achats
    assert "<dt>127,75 €</dt><dd>Total</dd>" in _scene(MEUBLE.vues("actuelle")["explication"])
    assert "<dt>78,00 €</dt><dd>Total</dd>" in _scene(MEUBLE.vues("rangs")["explication"])


def test_meuble_total_de_l_explication():
    vues = MEUBLE.vues("actuelle")
    total = re.search(r'<p class="total-achats"><span>Total</span><span class="num">([^<]+)</span>',
                      _scene(vues["achats"])).group(1)
    assert f"<dt>{total}</dt><dd>Total</dd>" in _scene(vues["explication"])
    etapes = re.search(r"<dt>([^<]+)</dt><dd>Étapes</dd>", _scene(vues["explication"])).group(1)
    assert etapes == "3"
    assert "<dt>0</dt><dd>Étapes</dd>" in _scene(MEUBLE.vues("rangs")["explication"])


def test_meuble_sans_cote_en_dur(monkeypatch):
    avant = MEUBLE.vues("actuelle")
    assert "120 + 80 + 80 cm" in avant["plans"].fiche
    monkeypatch.setitem(MEUBLE.TABLETTES, "actuelle", (135, 80, 80))
    apres = MEUBLE.vues("actuelle")
    assert "135 + 80 + 80 cm" in apres["plans"].fiche
    assert "135 × " in _scene(apres["decoupe"]) and "120 × " not in _scene(apres["decoupe"])
    assert "120 × " in _scene(avant["decoupe"])


def _liens_du_menu(html, chemin):
    """Adresses (sous la racine du site) des documents du menu d'une page écrite à `chemin`."""
    menu = html.split('<ul class="arbre">', 1)[1].split("</ul></li></ul>", 1)[0]
    dossier = posixpath.dirname(chemin)
    liens = set()
    for href in re.findall(r'<li><a href="([^"]+)"', menu):
        cible = posixpath.normpath(posixpath.join(dossier, href))
        liens.add(cible + "/" if href.endswith("/") else cible)
    return liens


def test_construire_deux_documents(tmp_path):
    sortie = CONSTRUIRE.construire(tmp_path)
    pages = ("essai/amenagement/index.html", "essai/amenagement/b.html", "essai/amenagement/c.html",
             "atelier/etagere/index.html", "atelier/etagere/rangs.html", "atelier/etagere/escalier.html")
    for chemin in pages:
        html = (sortie / chemin).read_text(encoding="utf-8")
        assert _liens_du_menu(html, chemin) == {"essai/amenagement/", "atelier/etagere/"}, chemin
        if chemin.startswith("essai/"):
            assert '<span class="doc">Aménagement</span>' in html
            assert 'id="c-doc"' not in html
    assert (sortie / "ancienne.html").exists() and (sortie / "commun" / "site.js").exists()
