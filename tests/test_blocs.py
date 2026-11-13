from pathlib import Path

from commun.blocs import (CALQUES, INVITE, Coupe, Lieu, Zone, cotes_meuble, figure_rendu, points_iso, rendu,
                          vue_camera, vue_coupes, vue_iso, vue_plan, zones_svg)
from commun.modele import Camera
from tests.outils import RACINE, balises

SOL = [(0, 0), (100, 0), (100, 200), (0, 200)]
PORTES = [dict(nom="ouest", mur="o", face=0, a=20, b=100)]
LIEU = Lieu(SOL, PORTES, "Position dans la chambre")
BANC = Zone(id="banc", titre="Banc & coffre", emprise=(10, 20, 105, 58), cotes="95 × 38, h 45",
            texte="Un <b>banc</b>.", coupe="A", iso="so")
PORTE = Zone(id="porte", titre="Porte", emprise=(0, 20, 14, 100), cotes="vantail de 80", texte="La porte.", iso="no")


def test_cotes_meuble():
    assert cotes_meuble({"x0": 0, "x1": 95, "y0": 0, "y1": 38, "z1": 45}) == "95 × 38, h 45"
    assert cotes_meuble({"x0": 0, "x1": 110, "y0": 0, "y1": 40, "z0": 204, "z1": 234}) == "110 × 40, h 30, dessous à 204"
    assert cotes_meuble({"x0": 0, "x1": 84, "y0": 0, "y1": 40, "z1": 236, "caisson": 35}) == "84 × 35, h 236"
    assert cotes_meuble({"x0": 0, "x1": 95, "y0": 0, "y1": 38, "z1": 45, "plateau": 2.5}, plateau=True) == "95 × 38, h 47,5"


def test_zones_svg_identifiant_stable():
    rects = balises(zones_svg([BANC]), "rect", classe="zone")
    assert len(rects) == 1
    r = rects[0]
    assert r["data-meuble"] == "banc"
    assert (r["x"], r["y"], r["width"], r["height"]) == ("10", "20", "95", "38")
    assert r["role"] == "button" and r["tabindex"] == "0"
    assert 'aria-label="Banc &amp; coffre"' in zones_svg([BANC])


def test_vue_plan():
    vue = vue_plan("<svg></svg>", [BANC, PORTE], "<p>légende</p>")
    assert vue.id == "plan" and vue.outils == ("zoom", "mesure")
    assert f"<p>{INVITE}</p>" in vue.fiche
    boutons = balises(vue.fiche, "button")
    assert [b["data-calque"] for b in boutons] == [k for k, _ in CALQUES]
    assert all(b["aria-pressed"] == "true" for b in boutons)
    assert vue.fiche.endswith("<h3>Légende</h3><p>légende</p>")
    [el] = vue.elements
    assert (el.k, el.nom, el.titre, el.scene) == ("", "Plan", "Plan", "<svg></svg>")
    [modele] = balises(el.fiche, "template", **{"data-meuble": "banc"})
    assert modele["data-titre"] == "Banc & coffre"
    assert 'data-titre="Banc &amp; coffre"' in el.fiche
    assert '<p class="cotes">95 × 38, h 45 cm</p>' in el.fiche
    assert '<a class="btn" href="#coupes?k=A">Coupe A</a><a class="btn" href="#iso?k=so">Iso</a>' in el.fiche
    porte = el.fiche.split('data-meuble="porte"')[1]
    assert "#coupes" not in porte and '<a class="btn" href="#iso?k=no">Iso</a>' in porte
    assert '<p class="cotes">vantail de 80</p>' in porte
    assert "<input" not in vue.fiche + el.fiche


def test_vue_coupes_position():
    coupes = [Coupe("A", "A mur", "Coupe A-A : mur", "<svg>a</svg>", ((0, 60), (100, 60))),
              Coupe("nord", "Nord", "Élévation nord", "<svg>n</svg>", ((0, 0), (100, 0)))]
    vue = vue_coupes(coupes, LIEU)
    assert vue.id == "coupes" and vue.outils == ("zoom", "mesure")
    assert [e.k for e in vue.elements] == ["A", "nord"]
    assert (vue.elements[0].nom, vue.elements[0].titre, vue.elements[0].scene) == ("A mur", "Coupe A-A : mur", "<svg>a</svg>")
    assert vue.fiche.startswith("<h3>Position</h3>")
    assert [t["data-k"] for t in balises(vue.fiche, "line", classe="sec")] == ["A", "nord"]
    assert balises(vue.fiche, "svg")[0]["aria-label"] == LIEU.aria
    vide = vue_coupes([], LIEU)
    assert vide.elements == [] and vide.vide == "Sans objet"


def test_rendu_nommage(tmp_path):
    r = rendu(tmp_path, "victor", "iso_so")
    assert r.image == "rendus/victor-iso_so.jpg"
    assert r.masque == "rendus/victor-iso_so-masque.png"
    assert r.fichier == tmp_path / "victor-iso_so.jpg"
    assert r.existe is False
    (tmp_path / "victor-iso_so.jpg").write_bytes(b"")
    assert rendu(tmp_path, "victor", "iso_so").existe is True
    sans = rendu(tmp_path, "", "iso_so")
    assert sans.image == "rendus/iso_so.jpg" and sans.masque == "rendus/iso_so-masque.png"


def test_figure_rendu(tmp_path):
    (tmp_path / "a-iso_so.jpg").write_bytes(b"")
    r = rendu(tmp_path, "a", "iso_so")
    simple = figure_rendu(r, "Vue & coin")
    assert [i["src"] for i in balises(simple, "img")] == ["rendus/a-iso_so.jpg"]
    assert 'alt="Vue &amp; coin"' in simple
    images = balises(figure_rendu(r, "Vue", filtre="teinte"), "img")
    assert len(images) == 2
    calque = images[1]
    assert calque["class"] == "calque" and calque["alt"] == ""
    assert "filter:url(#filtre-teinte)" in calque["style"]
    assert "url(rendus/a-iso_so-masque.png)" in calque["style"]
    assert figure_rendu(rendu(tmp_path, "b", "iso_so"), "Vue") == ""


def test_vue_iso_coins(tmp_path):
    for nom in ("a-iso_so.jpg", "a-iso_no.jpg"):
        (tmp_path / nom).write_bytes(b"")
    vue = vue_iso(tmp_path, "a", LIEU, points_iso((0, 0, 100, 200)), alts={"iso_no": "Depuis le nord-ouest"})
    assert vue.id == "iso"
    assert [e.k for e in vue.elements] == ["no", "ne", "so", "se"]
    assert [e.k for e in vue.elements if e.actif] == ["no", "so"]
    assert vue.elements[1].scene == ""
    assert [e.titre for e in vue.elements] == ["Vue iso NO", "Vue iso NE", "Vue iso SO", "Vue iso SE"]
    assert [g["data-k"] for g in balises(vue.fiche, "g", classe="pdv")] == ["no", "so"]
    assert balises(vue.elements[0].scene, "img")[0]["alt"] == "Depuis le nord-ouest"
    assert balises(vue.elements[2].scene, "img")[0]["alt"] == "Vue isométrique, coin SO"


def test_vue_iso_sans_rendu(tmp_path):
    vue = vue_iso(tmp_path, "a", LIEU, points_iso((0, 0, 100, 200)))
    assert vue.elements == [] and vue.vide == "Pas encore rendu"
    assert vue_iso(tmp_path, "a", LIEU, points_iso((0, 0, 100, 200)), vide="Sans objet").vide == "Sans objet"


def test_vue_camera_sans_camera(tmp_path):
    vue = vue_camera(tmp_path, "a", LIEU, [])
    assert vue.elements == [] and vue.vide == "Pas encore rendu"
    assert vue_camera(tmp_path, "a", LIEU, [], vide="Sans objet").vide == "Sans objet"
    rien = vue_camera(tmp_path, "a", LIEU, [Camera("banc", "Banc", (10, 20, 112), (40, 300, 112), focale=17)])
    assert rien.elements == []


def test_vue_camera(tmp_path):
    (tmp_path / "a-banc.jpg").write_bytes(b"")
    banc = Camera("banc", "Assis sur le banc", (10, 20, 112), (40, 300, 112), focale=17, yeux=112)
    porte = Camera("porte", "Devant la porte", (50, 150, 160), (50, 0, 160), focale=17)
    vue = vue_camera(tmp_path, "a", LIEU, [banc, porte])
    assert vue.id == "camera"
    assert [e.k for e in vue.elements] == ["banc", "porte"]
    assert (vue.elements[0].nom, vue.elements[0].titre) == ("Assis sur le banc", "Assis sur le banc")
    assert vue.elements[0].fiche == '<p class="cotes">yeux à 112 cm, objectif 17 mm</p>'
    assert balises(vue.elements[0].scene, "img")[0]["alt"] == "Assis sur le banc"
    assert vue.elements[1].actif is False and vue.elements[1].scene == ""
    assert vue.elements[1].fiche == '<p class="cotes">objectif 17 mm</p>'
    assert [g["data-k"] for g in balises(vue.fiche, "g", classe="pdv")] == ["banc", "porte"]
    sans = vue_camera(tmp_path, "a", LIEU, [Camera("banc", "Banc", (10, 20, 112), (40, 300, 112))])
    assert sans.elements[0].fiche == ""


def test_points_iso():
    points = points_iso((0, 0, 100, 200))
    assert list(points) == ["no", "ne", "so", "se"]
    assert points["so"] == ((-26, 226), (50.0, 100.0))


def test_commun_n_importe_pas_pieces():
    for chemin in sorted(Path(RACINE / "commun").glob("*.py")):
        texte = chemin.read_text(encoding="utf-8")
        assert "import pieces" not in texte and "from pieces" not in texte, chemin.name
