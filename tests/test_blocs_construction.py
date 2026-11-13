import re

import pytest

from commun.blocs import Achat, SectionAchats, achats, vue_lecture
from commun.blocs_construction import (Calepin, Colonne, DessinMeuble, Etape, calepinage, etapes, rendus_meuble,
                                       tableau_debit, vue_plans)
from commun.gabarit import page_document
from commun.modele import Document, Piece, Site, Variante
from tests.outils import RACINE, balises

ELEVATION = DessinMeuble("elevation", "Élévation", '<svg viewBox="0 0 100 50"><rect/></svg>')
ISO = DessinMeuble("iso", "Vue iso", '<svg viewBox="0 0 100 50"><path/></svg>', mesure=False)
COLONNES = (Colonne("Repère", "repere"), Colonne("Pièce"), Colonne("Nb", "nombre"),
            Colonne("Dimensions (cm)", "cote"), Colonne("Matière"), Colonne("Tirée de", "note"))
LIGNE = ("A", "Montant", 2, "80 × 2.5", "Chêne & pin", "panneau 1")
CSS = (RACINE / "commun" / "site.css").read_text(encoding="utf-8")


def _page(vues):
    variante = Variante("", "Principale", "V1", ())
    doc = Document("atelier", "etagere", "Étagère", "construction", (variante,), lambda v: vues)
    site = Site((Piece("atelier", "Atelier", (doc,)),))
    return page_document(site, doc, variante, vues)


def _vues(plans):
    debit = tableau_debit(COLONNES, [LIGNE], sous_titre="Un repère.")
    montage = etapes([Etape("Poser", "<p>Les montants.</p>", figure="<svg></svg>")], outils="<p>Visseuse.</p>")
    sections = [SectionAchats("Bois", [Achat("Planche", "P1", 2, 10)]),
                SectionAchats("Quincaillerie", [Achat("Vis", "V4", 1, None, note="boîte de 100")])]
    return {"plans": plans, "decoupe": vue_lecture("decoupe", debit), "montage": vue_lecture("montage", montage),
            "achats": vue_lecture("achats", achats(sections)), "explication": vue_lecture("explication", "<p>Texte.</p>")}


def test_vue_plans():
    vue = vue_plans([ELEVATION, ISO], "Disposition A & B", formule="3 × 80 cm")
    assert vue.id == "plans"
    assert [e.k for e in vue.elements] == ["elevation", "iso"]
    assert [e.nom for e in vue.elements] == ["Élévation", "Vue iso"]
    assert [e.titre for e in vue.elements] == ["Disposition A & B"] * 2
    assert '<p class="cotes">3 × 80 cm</p>' in vue.fiche
    liens = balises(vue.fiche, "a", classe="btn")
    assert [a["href"] for a in liens] == ["#decoupe", "#montage"]
    assert re.findall(r"</svg>([^<]+)</a>", vue.fiche) == ["Découpe", "Montage"]
    assert "<h3>Légende</h3>" not in vue.fiche
    assert vue.outils == ("zoom", "mesure")
    page = _page(_vues(vue))
    plans = page.split('<section class="vue" data-vue="plans"')[1].split("</section>")[0]
    segments = plans.split('<div class="segments">')[1].split("</div>")[0]
    assert [b["data-k"] for b in balises(segments, "button")] == ["elevation", "iso"]
    assert 'data-titre="Disposition A &amp; B"' in plans


def test_vue_plans_iso_sans_mesure():
    vue = vue_plans([ELEVATION, ISO], "A")
    elevation, iso = vue.elements
    assert iso.scene.startswith('<svg data-mesure="non" viewBox=')
    assert balises(iso.scene, "svg")[0]["data-mesure"] == "non"
    assert "data-mesure" not in elevation.scene
    assert vue_plans([ISO], "A").outils == ("zoom",)
    image = DessinMeuble("photo", "Photo", '<figure class="cadre"></figure>', mesure=False)
    assert vue_plans([image], "A").elements[0].scene == '<figure class="cadre"></figure>'


def test_vue_plans_liens_et_legende():
    vue = vue_plans([ELEVATION], "A", liens=("decoupe",), legende="<p>Traits fins : chants.</p>")
    assert [a["href"] for a in balises(vue.fiche, "a")] == ["#decoupe"]
    assert "Montage" not in vue.fiche
    assert vue.fiche.endswith("<h3>Légende</h3><p>Traits fins : chants.</p>")
    sans = vue_plans([ELEVATION], "A", liens=())
    assert '<div class="actions">' not in sans.fiche and sans.fiche == ""
    vide = vue_plans([], "A")
    assert vide.id == "plans" and vide.elements == [] and vide.vide == "Sans objet"


def test_tableau_debit():
    html = tableau_debit(COLONNES, [LIGNE, ("B", "Tablette", 2.5, "76", "Pin", "")], sous_titre="Deux repères.")
    assert html.startswith('<h2>Liste de débit</h2><p class="sous-titre">Deux repères.</p>'
                           '<div class="debit"><table class="cartes"><thead><tr>')
    assert [t.get("class", "") for t in balises(html, "th")] == ["", "", "d", "", "", ""]
    assert ('<td class="num"><b>A</b></td><td>Montant</td><td class="num d" data-l="×">2</td>'
            '<td class="num large" data-l="Dimensions (cm)">80 × 2.5</td><td>Chêne &amp; pin</td>'
            '<td class="large remarque" data-l="Tirée de">panneau 1</td>') in html
    assert '<td class="num d" data-l="×">2,5</td>' in html
    assert html.endswith("</tbody></table></div>")
    assert "Chêne & pin" not in html
    assert tableau_debit(COLONNES, [], titre="Débit").startswith("<h2>Débit</h2><div")
    with pytest.raises(ValueError):
        tableau_debit(COLONNES, [LIGNE[:5]])
    with pytest.raises(ValueError):
        tableau_debit((Colonne("X", "autre"),), [("a",)])


def test_calepinage():
    html = calepinage([Calepin("Panneau 1 & 2", "<svg>1</svg>"), Calepin("Panneau 3", "<svg>3</svg>")])
    assert html.startswith("<h2>Calepinage</h2>")
    assert len(balises(html, "figure", classe="calepin")) == 2
    assert html.count("<figcaption>") == 2
    assert '<figure class="calepin"><figcaption>Panneau 1 &amp; 2</figcaption><svg>1</svg></figure>' in html
    assert calepinage([]) == ""


def test_etapes():
    liste = [Etape("Poser", "<p>a</p>"), Etape("Visser & coller", "<p>b</p>", figure="<svg>b</svg>"),
             Etape("", "<p>c</p>")]
    html = etapes(liste)
    assert html.startswith('<h2>Montage</h2><ol class="etapes"><li>')
    assert html.count("<li>") == 3
    assert len(balises(html, "figure", classe="etape-figure")) == 1
    assert '<li><div><h3>Visser &amp; coller</h3><p>b</p><figure class="etape-figure"><svg>b</svg></figure></div></li>' in html
    assert "<li><div><p>c</p></div></li>" in html
    assert "<details" not in html and "style=" not in html
    avec = etapes(liste, titre="Suite", outils="<p>Visseuse.</p>", debut=8)
    assert balises(avec, "details", classe="reunir")
    assert '<details class="reunir"><summary>Outils à réunir</summary><p>Visseuse.</p></details>' in avec
    assert '<ol class="etapes" style="--debut:7">' in avec


def test_rendus_meuble(tmp_path):
    (tmp_path / "vue.jpg").write_bytes(b"")
    (tmp_path / "face.jpg").write_bytes(b"")
    html = rendus_meuble(tmp_path, "", [("face", "De face"), ("absent", "Absent"), ("vue", "Vue & dessus")])
    assert html.startswith('<h2>Rendus</h2><div class="duo">') and html.endswith("</div>")
    imgs = balises(html, "img")
    assert [i["src"] for i in imgs] == ["rendus/face.jpg", "rendus/vue.jpg"]
    assert [i["alt"] for i in imgs] == ["De face", "Vue & dessus"]
    assert all(i["loading"] == "lazy" for i in imgs)
    assert rendus_meuble(tmp_path, "", [("absent", "Absent")]) == ""


def test_page_construction_sans_case_ni_copier():
    page = _page(_vues(vue_plans([ELEVATION, ISO], "A", formule="80 cm")))
    assert "<input" not in page
    assert "Copier la liste" not in page
    assert "·" not in page


def _regle(classe):
    selecteurs = re.findall(r"([^{}]+)\{", re.sub(r"/\*.*?\*/", "", CSS, flags=re.S))
    return any(re.search(rf"\.{re.escape(classe)}(?![\w-])", s) for s in selecteurs)


def test_classes_des_blocs_ont_une_regle(tmp_path):
    attendues = {"cartes", "debit", "large", "calepin", "etapes", "etape-figure", "reunir", "duo", "total-achats"}
    vues = _vues(vue_plans([ELEVATION], "A"))
    html = "".join(vues[k].elements[0].scene for k in ("decoupe", "montage", "achats"))
    (tmp_path / "vue.jpg").write_bytes(b"")
    html += calepinage([Calepin("P", "<svg></svg>")]) + rendus_meuble(tmp_path, "", [("vue", "Vue")])
    emises = {c for valeur in re.findall(r'class="([^"]*)"', html) for c in valeur.split()}
    assert attendues <= emises
    assert [c for c in sorted(attendues) if not _regle(c)] == []


def test_site_css_sans_interdit():
    for interdit in ("prefers-color-scheme", "monospace", "text-transform", "·"):
        assert interdit not in CSS
