"""Aides SVG de la cuisine (pieces/cuisine/dessin.py) : mêmes sorties que dans les dessins de référence, et les pages
porte du cellier et imprimable n'importent plus plan.py."""
import json

from pieces.cuisine import dessin, modele
from tests.cuisine_anciens import FIXTURES, ancien
from tests.outils import RACINE


def _dessins():
    return {n: (FIXTURES / "dessins" / f"{n}.svg").read_text(encoding="utf-8") for n in ("plan", "coupe-a")}


def test_aides_identiques():
    d = _dessins()
    ensemble = d["plan"] + d["coupe-a"]
    # entrées reprises de plan_svg() (les valeurs du brief, cote_h(0, 327, -40) etc., ne figurent pas dans les dessins)
    evier = modele.sur_bas(modele.B_EVIER)[1]
    for rendu in (dessin.cote_h(0, 434, -66), dessin.cote_v(0, 252, -52),
                  dessin.cote_d((evier, 62), (modele.COL_X, modele.JOUE_C2), 0.5, (-7, 4)),
                  dessin.pts(modele.SOL_PARQUET)):
        assert rendu in ensemble
    assert dessin.virg(68.7) == "68,7"
    assert dessin.virg(60) == "60"
    assert dessin.f(2.0) == "2" and dessin.f(2.5) == "2.5"
    assert dessin.rect(0, 0, 10, 5, "w") == '<rect class="w" x="0" y="0" width="10" height="5"/>'
    assert dessin.text(1, 2, "a<b") == '<text class="lbl" x="1" y="2" text-anchor="middle">a&lt;b</text>'


def test_volumes_et_tango():
    assert "".join(dessin.volumes_plan()) in _dessins()["plan"]
    tab = json.loads((FIXTURES / "tableaux.json").read_text(encoding="utf-8"))
    assert dessin.fiche_tango() == tab["tango"]
    assert "notice commerciale Mantion Tango" in dessin.sources_tango()
    assert dessin.CSS.lstrip().startswith(":root") and dessin.RACINE == RACINE


def test_ancienne_page_reprend_les_aides():
    plan = ancien("plan")
    for nom in ("f", "rect", "text", "cote_h", "cote_d", "cote_v", "aire", "pts", "virg", "PLAN_CLS", "volumes_plan",
                "fiche_tango", "sources_tango", "CSS"):
        assert getattr(plan, nom) is getattr(dessin, nom), nom


def test_porte_inchangee():
    assert ancien("porte").page() == (FIXTURES / "porte-cellier.html").read_text(encoding="utf-8")


def test_porte_et_imprimable_n_importent_plus_plan():
    # l'imprimable est une annexe du document depuis la tâche 10 (tests/test_cuisine_annexes.py)
    for chemin in ("3d/v13/porte.py", "pieces/cuisine/amenagement/imprimable.py"):
        assert "from plan import" not in (RACINE / chemin).read_text(encoding="utf-8")
