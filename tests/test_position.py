from commun.position import mini_plan
from pieces.entree import piece
from tests.outils import balises

SOL = piece.SOL
PORTES = piece.PORTES
TRAITS = (("A", ((-6, 60), (270, 60))), ("B", ((40, -6), (40, 380))))
CONES = (("banc", (102, 24), (42, 374), True), ("couloir", (15, 70), (150, 200), False))


def test_mini_plan_sol_et_portes():
    svg = mini_plan(SOL, PORTES)
    assert svg.startswith("<svg ") and svg.endswith("</svg>")
    assert len(balises(svg, "polygon")) == 1
    assert len(balises(svg, "line", classe="ouv")) == len(PORTES)
    assert not balises(svg, "line", classe="sec")


def test_mini_plan_traits():
    svg = mini_plan(SOL, PORTES, traits=TRAITS)
    traits = balises(svg, "line", classe="sec")
    assert [t["data-k"] for t in traits] == ["A", "B"]
    assert all("ici" not in t["class"].split() for t in traits)


def test_mini_plan_cones():
    svg = mini_plan(SOL, PORTES, cones=CONES)
    groupes = balises(svg, "g", classe="pdv")
    assert len(groupes) == 2
    assert [("ici" in g["class"].split()) for g in groupes] == [True, False]
    assert [g["data-k"] for g in groupes] == ["banc", "couloir"]     # le JS y pose `ici` selon le repère affiché
    assert len(balises(svg, "path", classe="cone")) == 2
    assert len(balises(svg, "circle", classe="cam")) == 2


def test_mini_plan_sans_texte_ni_case():
    svg = mini_plan(SOL, PORTES, traits=TRAITS, cones=CONES)
    assert "<text" not in svg and "checkbox" not in svg
