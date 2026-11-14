"""Salon, calculs et dessins partagés (pieces/salon/meubles.py, pieces/salon/dessin.py) : reprise de
3d/salon/commun.py et des aides SVG de plan.py, et dessins de référence (tests/fixtures/salon/)."""
import json

import pytest

from pieces.salon import dessin, meubles
from pieces.salon.enfilade import volumes as vol_enfilade
from pieces.salon.etageres import document as etageres
from pieces.salon.etageres import volumes as vol_etageres
from tests.outils import RACINE


FIXTURES = RACINE / "tests" / "fixtures" / "salon"


def test_calculs_partages():
    for v in (0, 1.25, 8.8, 240, 60.84):
        assert (meubles.f(v), meubles.virg(v), meubles.virg(v, 2)) == (dessin.f(v), dessin.virg(v), dessin.virg(v, 2))
    neufs = vol_etageres.pieces_3d() + vol_enfilade.pieces_3d(ouvert=True)
    assert len(meubles.ordre(neufs)) == len(neufs)
    for p in neufs:
        for face in "xyz":
            assert meubles.aretes(p, face, neufs) is not None


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
