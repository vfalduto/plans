from pieces.entree import piece
from pieces.entree.amenagement import document, plum, victor


def test_piece():
    assert piece.SOL[0] == (0, 0)
    assert len(piece.SOL) == 8
    assert piece.H == 250
    assert {c.id for c in piece.CAMERAS} == {"iso_so", "iso_no", "iso_se", "banc", "couloir"}


def test_versions():
    assert document.VERSION == "V4.8"
    assert victor.VERSION == "V1.5"
    assert victor.CHANGEMENTS[0][0] == "V1.5"


def test_cameras_communes():
    assert not hasattr(victor, "VUES")


def test_cameras_partagees():
    cams = {c.id: c for c in piece.CAMERAS}
    assert set(cams) == {"iso_so", "iso_no", "iso_se", "banc", "couloir"}
    assert cams["iso_no"].cible == (177, 190, 60)
    assert cams["banc"].focale == 17
    assert cams["banc"].yeux == 112


def test_positions_humains_victor():
    assert victor.POSITIONS_HUMAINS == {"couloir": (150, 95), "entree": (36, 300)}
    assert victor.HUMAINS["iso_no"] == "entree"


# ------------------------------------------------------------------ tâche 13 : vues Plan et Coupes
import re  # noqa: E402

import pytest  # noqa: E402

from commun import modele  # noqa: E402
from pieces.entree.amenagement import dessin_principale, dessin_victor, vues  # noqa: E402
from tests.outils import RACINE, balises  # noqa: E402

FIXTURES = RACINE / "tests" / "fixtures" / "entree"
DESSINS = {
    "principale": (document, dessin_principale, ("plan", "coupe_a", "coupe_b", "coupe_c")),
    "victor": (victor, dessin_victor, ("plan", "coupe_a", "coupe_b", "coupe_c", "coupe_d")),
}


def _sans_ajouts(svg):
    """Retire la classe plan/coupe et l'aria-label de la balise <svg> racine, seuls écarts avec les anciens dessins."""
    tete, reste = svg.split(">", 1)
    tete = re.sub(r' class="(plan|coupe)"', "", tete, count=1)
    tete = re.sub(r' aria-label="[^"]*"', "", tete, count=1)
    return tete + ">" + reste


@pytest.mark.parametrize("variante,dessin", [(v, d) for v, (_, _, ds) in DESSINS.items() for d in ds])
def test_dessins_inchanges(variante, dessin):
    M, module, _ = DESSINS[variante]
    svg = getattr(module, "plan_svg" if dessin == "plan" else dessin)(M)
    attendu = (FIXTURES / f"{variante}-{dessin}.svg").read_text(encoding="utf-8")
    assert svg.startswith('<svg class="plan"' if dessin == "plan" else '<svg class="coupe"')
    assert _sans_ajouts(svg) == _sans_ajouts(attendu)


def test_coupes():
    assert [e.k for e in vues.vues("principale")["coupes"].elements] == ["A", "B", "C"]
    assert [e.k for e in vues.vues("victor")["coupes"].elements] == ["A", "B", "C", "D"]
    premier = vues.vues("principale")["coupes"].elements[0]
    assert premier.nom == "A mur nord"
    assert premier.titre == "Coupe A-A : mur nord"
    assert vues.vues("principale")["coupes"].outils == ("zoom", "mesure")


def _plan(variante):
    v = vues.vues(variante)["plan"]
    (e,) = v.elements
    return v, e


def test_plan_zones():
    v, e = _plan("principale")
    assert e.k == ""
    assert len(balises(e.scene, "rect", classe="zone")) == 5
    modeles = balises(e.fiche + v.fiche, "template")
    assert len(modeles) == 5 and all("data-meuble" in m for m in modeles)
    for z in balises(e.scene, "rect", classe="zone"):
        assert {"data-meuble", "tabindex", "role", "aria-label"} <= set(z)
    assert [z["data-meuble"] for z in balises(e.scene, "rect", classe="zone")] == [m["data-meuble"] for m in modeles]
    assert len(balises(_plan("victor")[1].scene, "rect", classe="zone")) == 4
    assert v.outils == ("zoom", "mesure")


def test_modele_de_zone():
    _, e = _plan("principale")
    assert 'href="#coupes?k=A"' in e.fiche
    assert 'href="#iso?k=iso_so"' in e.fiche
    assert "95 × 38, h 45 cm" in e.fiche


def test_fiche_plan():
    v, _ = _plan("principale")
    assert "Touchez un meuble pour afficher sa fiche." in v.fiche
    assert "Lecture du plan" not in v.fiche


def test_calques():
    v, e = _plan("principale")
    boutons = balises(v.fiche, "button", **{})
    calques = [b for b in boutons if "data-calque" in b]
    assert [b["data-calque"] for b in calques] == ["cotes", "passages", "coupes", "voisines", "annotations"]
    assert all(b["aria-pressed"] == "true" and b["type"] == "button" for b in calques)
    assert 'type="checkbox"' not in v.fiche + e.scene + e.fiche
    assert balises(v.fiche, "div", classe="calques")
    assert "Cotes" in v.fiche and "Annotations" in v.fiche
    assert "Légende" in v.fiche and 'class="legend"' in v.fiche


def test_aria_label_est_la_legende():
    _, e = _plan("principale")
    (svg,) = balises(e.scene, "svg")
    assert svg["aria-label"].startswith("Plan vu de dessus")
    for k, c in zip("ABC", vues.vues("principale")["coupes"].elements):
        assert balises(c.scene, "svg")[0]["aria-label"].startswith(f"Coupe à ")


def test_coupes_fiche_position():
    v = vues.vues("principale")["coupes"]
    assert "Position" in v.fiche
    traits = balises(v.fiche, "line", classe="sec")
    assert [t["data-k"] for t in traits] == ["A", "B", "C"]
    assert [t["data-k"] for t in balises(vues.vues("victor")["coupes"].fiche, "line", classe="sec")] == ["A", "B", "C", "D"]


def test_vues_pas_encore_la():
    for variante in ("principale", "victor"):
        v = vues.vues(variante)
        assert list(v) == list(modele.VUES["amenagement"])
        for cle in ("iso", "camera", "explication"):
            assert v[cle].elements == []


def test_document():
    d = document.DOCUMENT
    assert (d.piece, d.id, d.nom, d.type) == ("entree", "amenagement", "Aménagement", "amenagement")
    assert [x.id for x in d.variantes] == ["principale", "victor"]
    assert d.variantes[0].version == "V4.8" and d.variantes[1].version == "V1.5"
    (teinte,) = d.options
    assert (teinte.id, teinte.css, teinte.filtre, teinte.defaut) == ("teinte", "--india", True, plum.DEFAUT)
    assert len(teinte.valeurs) == 52
    india = next(x for x in teinte.valeurs if x.code == "color_india")
    assert india.couleur == "#F5D58C" and india.groupe == "Laque de façade seulement"
    assert "peinture à faire teinter" in india.note and india.lien == ""
    lin = next(x for x in teinte.valeurs if x.code == "color_lin")
    assert lin.groupe == "Laque et peinture murale" and lin.lien.endswith("2500P-S26")
    for variante in d.variantes:
        modele.verifier(d, d.generer(variante.id))
