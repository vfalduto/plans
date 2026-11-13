"""Salon, calculs et dessins partagés (pieces/salon/meubles.py, pieces/salon/dessin.py) : reprise de
3d/salon/commun.py et des aides SVG de plan.py, et dessins de référence (tests/fixtures/salon/)."""
import json

import pytest

from pieces.salon import dessin, meubles
from pieces.salon.enfilade import volumes as vol_enfilade
from pieces.salon.etageres import document as etageres
from pieces.salon.etageres import volumes as vol_etageres
from tests.salon_anciens import FIXTURES, ancien


def test_calculs_partages():
    C = ancien("commun")
    assert meubles.MATIERES == C.MATIERES
    for v in (0, 1.25, 8.8, 240, 60.84):
        assert (meubles.f(v), meubles.virg(v), meubles.virg(v, 2)) == (C.f(v), C.virg(v), C.virg(v, 2))
    vieux = ancien("etageres").pieces_3d() + ancien("enfilade").pieces_3d(ouvert=True)
    neufs = vol_etageres.pieces_3d() + vol_enfilade.pieces_3d(ouvert=True)
    assert [p.nom for p in meubles.ordre(neufs)] == [p.nom for p in C._ordre(vieux)]
    assert len(neufs) == len(vieux)
    for pn, pv in zip(neufs, vieux):            # toutes les pièces, pas seulement les premières
        for face in "xyz":
            assert meubles.aretes(pn, face, neufs) == C._aretes(pv, face, vieux)


def test_index_des_dessins():
    index = json.loads((FIXTURES / "index.json").read_text(encoding="utf-8"))
    assert sorted(index) == sorted(p.name for p in FIXTURES.glob("*.svg"))


@pytest.mark.parametrize("d", etageres.DISPOSITIONS, ids=lambda d: d["cle"])
def test_iso_des_etageres_comme_la_page(d):
    svg = dessin.iso_svg(vol_etageres.pieces_3d(d), f"Étagères, vue iso, disposition {d['nom']}")
    nom = f"etageres-etageres-vue-iso-disposition-{d['cle']}-{d['cle']}.svg"
    assert svg == (FIXTURES / nom).read_text(encoding="utf-8")


def test_iso_detail_et_enfilade_comme_la_page():
    temoins = {
        "etageres-etageres-detail-d-une-entaille-en-vue-iso.svg": dessin.iso_svg(
            vol_etageres.pieces_detail(), "Étagères, détail d'une entaille en vue iso", echelle=11,
            style="max-width:420px;display:block;margin:0 auto"),
        "enfilade-enfilade-fermee-vue-iso.svg": dessin.iso_svg(vol_enfilade.pieces_3d(), "Enfilade fermée, vue iso"),
        "enfilade-enfilade-ouverte-vue-iso.svg": dessin.iso_svg(vol_enfilade.pieces_3d(ouvert=True),
                                                                 "Enfilade ouverte, vue iso"),
    }
    for nom, svg in temoins.items():
        assert svg == (FIXTURES / nom).read_text(encoding="utf-8"), nom


def test_iso_et_rond_comme_l_ancien():
    C = ancien("commun")
    vieux, neufs = ancien("etageres").pieces_3d(), vol_etageres.pieces_3d()
    assert dessin.iso_svg(neufs, "t", legende="légende") == C.iso_svg(vieux, "t", legende="légende")
    P = lambda x, y, z: (x - y, x + y - z)  # noqa: E731
    for pn, pv in zip(neufs, vieux):
        if pn.forme == "cyl_y":
            assert dessin._rond_y(pn, P, "#111", "#222") == C._rond_y(pv, P, "#111", "#222")


def test_aides_svg_comme_l_ancien():
    """Entrées tirées des dessins (coupes du salon, élévations des meubles) : mêmes chaînes que plan.py."""
    PL = ancien("plan")
    for v in (0, 2.5, 8.8, 60.84, 247.6, -275, 1 / 3):
        assert (dessin.f(v), dessin.virg(v), dessin.virg(v, 2)) == (PL.f(v), PL.virg(v), PL.virg(v, 2))
    assert dessin.rect(0, -80, 60, -15, "cab") == PL.rect(0, -80, 60, -15, "cab")
    assert dessin.rect(296, 160, 426, 225, "tbl c-f", 50) == PL.rect(296, 160, 426, 225, "tbl c-f", 50)
    assert dessin.text(10, 20, "vantail nord", "lblx muted") == PL.text(10, 20, "vantail nord", "lblx muted")
    assert dessin.text(4, 8, "< & >", "lbls muted", "start") == PL.text(4, 8, "< & >", "lbls muted", "start")
    for args in ((8.8, 248.8, 18, "enfilade 240"), (0, 60, 18), (120, 318, -90, None, 4)):
        assert dessin.cote_h(*args) == PL.cote_h(*args)
        assert dessin.cote_v(*args) == PL.cote_v(*args)
