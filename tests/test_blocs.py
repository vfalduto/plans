from pathlib import Path

from commun.blocs import (CALQUES, INVITE, Achat, Carte, Coupe, Lieu, SectionAchats, Zone, a_verifier, achats, chiffres,
                          cotes_meuble, euros, figure_rendu, materiaux, points_iso, principes, rendu, tableau_achats, tete,
                          total_achats, vue_camera, vue_coupes, vue_iso, vue_lecture, vue_plan, zones_svg)
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


# ------------------------------------------------------------------ Explication et achats
def test_euros():
    assert euros(80) == "80 €"
    assert euros(12.5) == "12,50 €"
    assert euros(64.9) == "64,90 €"
    assert euros(38.97) == "38,97 €"
    assert euros(14.99) == "14,99 €"
    assert euros(0.1 + 0.2) == "0,30 €"
    assert euros(100) == "100 €"
    assert euros(79.999) == "80 €"
    assert euros(12345.67) == "12345,67 €"


def test_somme_exacte():
    """Les montants s'additionnent sur leur écriture décimale : 3 × 12,45 + 0,15 = 37,50, arrondi à 38 (en flottants,
    37,49999999999999 tombait à 37)."""
    lignes = [Achat("Tasseau", "T", 3, 12.45), Achat("Vis", "V", 1, 0.15)]
    assert total_achats([SectionAchats("", lignes)]) == "38 €"
    assert _cellules(tableau_achats(lignes), "total") == [["Total", "", "", "38 €"]]
    assert total_achats([SectionAchats("A", lignes[:1]), SectionAchats("B", lignes[1:])], arrondi=False) == "37,50 €"


def test_rien_de_chiffre():
    """Une section sans ligne chiffrée : « non chiffré » au lieu d'un sous-total de 0 € ; de même pour le total."""
    porte = SectionAchats("Porte", [Achat("Porte", "P1", 1, None)])
    vis = SectionAchats("Vis", [Achat("Vis", "V1", 2, 1.5)])
    assert _cellules(tableau_achats(porte.achats, approx=True), "total") == [["Total", "", "", "non chiffré"]]
    deux = achats([porte, vis])
    assert _cellules(deux, "total") == [["Sous-total", "", "", "non chiffré"], ["Sous-total", "", "", "3 €"]]
    assert '<span class="num">3 €</span>' in deux
    rien = achats([porte, SectionAchats("Poignée", [Achat("Poignée", "P2", 1, None)])], approx=True)
    assert '<p class="total-achats"><span>Total</span><span class="num">non chiffré</span></p>' in rien
    assert total_achats([porte], approx=True) == "non chiffré"
    assert "0 €" not in deux + rien


def _cellules(html, classe):
    """Textes des cellules de la ligne `tr.<classe>` (une liste par ligne)."""
    lignes = html.split(f'<tr class="{classe}">')[1:]
    return [[c.split(">", 1)[1] for c in ligne.split("</tr>")[0].split("</td>")[:-1]] for ligne in lignes]


def test_tableau_achats_forme_de_l_entree():
    html = tableau_achats([Achat("Caisson", "604.582.27", 1, 80), Achat("Tablette", "702.779.95", 2, 27.5)],
                          approx=True)
    assert "<thead><tr><th>Article</th><th>Référence</th><th class=\"d\">Qté</th><th class=\"d\">Prix</th></tr></thead>" in html
    assert '<td class="num d">80 €</td>' in html and '<td class="num d">55 €</td>' in html
    assert '<td class="num d">2</td>' in html
    assert _cellules(html, "total") == [["Total", "", "", "≈ 135 €"]]
    assert html.startswith('<div class="defile"><table>') and html.endswith("</tbody></table></div>")


def test_achats_sections():
    ikea = SectionAchats("IKEA", [Achat("Caisson", "1", 1, 80.4)])
    weldom = SectionAchats("Weldom", [Achat("Vis", "2", 4, 1.1)])
    html = achats([ikea, weldom], note="Prix relevés.")
    assert html.startswith("<h2>Achats</h2>")
    assert html.count("<h3>") == 2 and "<h3>IKEA</h3>" in html and "<h3>Weldom</h3>" in html
    assert _cellules(html, "total") == [["Sous-total", "", "", "80 €"], ["Sous-total", "", "", "4 €"]]
    # arrondi depuis la somme exacte (84,8), pas depuis les sous-totaux arrondis (80 + 4)
    assert '<p class="total-achats"><span>Total</span><span class="num">85 €</span></p>' in html
    assert html.endswith('<p class="remarque">Prix relevés.</p>')
    seule = achats([SectionAchats("", [Achat("Caisson", "1", 1, 80)])], titre="Achats IKEA", approx=True)
    assert seule.startswith("<h2>Achats IKEA</h2>") and "<h3>" not in seule
    assert _cellules(seule, "total") == [["Total", "", "", "≈ 80 €"]]
    assert "total-achats" not in seule and "remarque" not in seule
    exact = achats([ikea, weldom], arrondi=False)
    assert '<span class="num">84,80 €</span>' in exact and '<td class="num d">4,40 €</td></tr></tbody>' in exact


def test_total_achats_est_celui_d_achats():
    ikea = SectionAchats("IKEA", [Achat("Caisson", "1", 1, 80.4), Achat("Porte", "3", 1, None)])
    weldom = SectionAchats("Weldom", [Achat("Vis", "2", 4, 1.1)])
    assert total_achats([ikea, weldom]) == "85 €"
    assert total_achats([ikea, weldom], approx=True, arrondi=False) == "≈ 84,80 €"
    for sections in ([ikea], [ikea, weldom]):
        for approx in (False, True):
            for arrondi in (False, True):
                html = achats(sections, approx=approx, arrondi=arrondi)
                total = total_achats(sections, approx=approx, arrondi=arrondi)
                if len(sections) == 1:
                    assert _cellules(html, "total") == [["Total", "", "", total]]
                else:
                    assert f'<p class="total-achats"><span>Total</span><span class="num">{total}</span></p>' in html


def test_achat_non_chiffre():
    html = tableau_achats([Achat("Porte", "P1", 1, None), Achat("Poignée", "P2", 2, 4.5)])
    assert '<td class="num d">non chiffré</td>' in html
    assert _cellules(html, "total") == [["Total", "", "", "9 €"]]
    assert "0 €" not in html


def test_achat_note():
    html = tableau_achats([Achat("Vis & chevilles", "R<1>", 1, 3, note="Weldom, réf. magasin")])
    assert "<td>Vis &amp; chevilles<small>Weldom, réf. magasin</small></td>" in html
    assert '<td class="num">R&lt;1&gt;</td>' in html
    assert "<small>" not in tableau_achats([Achat("Vis", "R1", 1, 3)])


def test_principes_montrer_sur_le_plan():
    html = principes([Carte("Banc & coffre", "Un <b>banc</b>.", meuble="banc"), Carte("Couleur", "India.")])
    assert html.startswith('<h2>Principe</h2><ol class="principes">') and html.endswith("</ol>")
    assert [a["href"] for a in balises(html, "a")] == ["#plan?k=banc"]
    assert ('<li><h3>Banc &amp; coffre</h3><p>Un <b>banc</b>.</p>'
            '<a class="btn" href="#plan?k=banc">Montrer sur le plan</a></li>') in html
    assert "<li><h3>Couleur</h3><p>India.</p></li>" in html


def test_tete():
    assert tete("Un <b>couloir</b>.") == '<p class="chapo">Un <b>couloir</b>.</p>'
    avec = tete("Chapô", [("#plan", "Ouvrir le plan"), ("#iso", "Voir en iso")], "<figure>f</figure>")
    assert avec == ('<div class="tete-doc"><div><p class="chapo">Chapô</p><p class="actions">'
                    '<a class="btn plein" href="#plan">Ouvrir le plan</a><a class="btn" href="#iso">Voir en iso</a></p>'
                    "</div><figure>f</figure></div>")
    figure = tete("Chapô", figure="<figure>f</figure>")
    assert figure == '<div class="tete-doc"><div><p class="chapo">Chapô</p></div><figure>f</figure></div>'
    assert balises(figure, "p", classe="actions") == []


def test_a_verifier_sans_case():
    html = a_verifier(["<b>Prise</b> : à relever.", "Plafond."])
    assert html == ('<h2>À vérifier sur place</h2><ul class="liste"><li><span><b>Prise</b> : à relever.</span></li>'
                    "<li><span>Plafond.</span></li></ul>")
    assert "<input" not in html
    assert a_verifier(["x"], titre="Points à vérifier").startswith("<h2>Points à vérifier</h2>")


def test_sequence_vide_rien():
    """Un bloc de section (et `chiffres`) sans rien à montrer ne rend rien, pas un titre seul."""
    assert principes([]) == "" and materiaux([]) == "" and a_verifier([]) == "" and chiffres([]) == ""
    assert achats([]) == "" and achats([], note="Prix relevés.") == ""
    assert achats([SectionAchats("Magasin A", []), SectionAchats("Magasin B", [])]) == ""
    assert vue_lecture("achats", achats([])).elements == []


def test_vue_lecture():
    vide = vue_lecture("explication", "")
    assert vide.id == "explication" and vide.elements == [] and vide.vide == "Sans objet"
    vue = vue_lecture("achats", "<p>x</p>")
    [el] = vue.elements
    assert (el.k, el.nom, el.titre, el.scene) == ("", "Achats", "Achats", "<p>x</p>")


def test_arrondi_demi_vers_le_haut():
    assert euros(0.125) == "0,13 €"
    assert euros(2.675) == "2,68 €"
    html = tableau_achats([Achat("Caisson", "1", 1, 80), Achat("Vis", "2", 3, 1.5)])
    assert _cellules(html, "total") == [["Total", "", "", "85 €"]]          # 84,5
    ikea = SectionAchats("IKEA", [Achat("Caisson", "1", 1, 80.5)])
    weldom = SectionAchats("Weldom", [Achat("Vis", "2", 1, 52)])
    html = achats([ikea, weldom])
    assert _cellules(html, "total")[0] == ["Sous-total", "", "", "81 €"]    # 80,5
    assert '<span class="num">133 €</span>' in html                        # 132,5
    centimes = achats([SectionAchats("A", [Achat("Clou", "1", 1, 0.005)]),
                       SectionAchats("B", [Achat("Vis", "2", 1, 0.12)])], arrondi=False)
    assert _cellules(centimes, "total")[0] == ["Sous-total", "", "", "0,01 €"]   # 0,005
    assert '<span class="num">0,13 €</span>' in centimes                        # 0,125
