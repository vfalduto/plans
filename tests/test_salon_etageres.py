"""Salon, étagères (pieces/salon/etageres/) : reprise de 3d/salon/modele.py (section ②) et de etageres.py."""
import inspect

import pytest

from pieces.salon import meubles
from pieces.salon.etageres import document as etageres
from pieces.salon.etageres import volumes
from tests.salon_anciens import (ANCIEN, MODELE, ancien, changements_de_la_page, comme_vue, norm, pieces, verifier_dessins,
                                 verifier_empreinte, vues_du_rendu)

# ancien nom dans 3d/salon/etageres.py → nom dans pieces/salon/etageres/document.py
REPRIS = {n: n for n in ("VERSION", "DATE", "RA_COTE", "PANNEAU", "TASSEAU", "ROND", "KERF", "KERF_METAL",
                         "DRESSAGE", "RECHANGE_CHEVILLES", "L_MONTANT", "BANDE", "N_VIS", "COEF", "KG_M",
                         "KG_MONTANT", "MAGASINS", "SURF_PEINT", "MATERIAUX", "TN", "R_ACIER", "R_MONTANT", "R_FLEX",
                         "A_JOUE", "R_JOUE", "ARR", "P_RUINE", "P_CALCUL", "SOURCES_TENUE")}
# laissés, et pourquoi : modules et alias (C, M, EN, ET, EU, MO, PAS, RA), présentoir dérivé (PR, voir
# test_presentoir), calculs de la page (DISPOS, D0, FACTEUR, PAR_TASSEAU, N_TASSEAUX), page (CSS, JS), privé (_LEVIER)
LAISSES = {"C", "M", "EN", "ET", "EU", "MO", "PAS", "RA", "PR", "DISPOS", "D0", "FACTEUR", "PAR_TASSEAU",
           "N_TASSEAUX", "CSS", "JS", "_LEVIER"}


@pytest.mark.parametrize("ancien_nom", sorted(MODELE["etageres"]))
def test_constantes_du_modele(ancien_nom):
    nom = MODELE["etageres"][ancien_nom]
    assert norm(getattr(etageres, nom)) == norm(getattr(ancien("modele"), ancien_nom))


@pytest.mark.parametrize("ancien_nom", sorted(REPRIS))
def test_constantes_du_generateur(ancien_nom):
    assert norm(getattr(etageres, REPRIS[ancien_nom])) == norm(getattr(ancien("etageres"), ancien_nom))


def test_generateur_entierement_vu():
    assert {n for n in vars(ancien("etageres")) if n.isupper()} == set(REPRIS) | LAISSES


def test_presentoir():
    PR = ancien("etageres").PR
    assert etageres.PRESENTOIR == {k: PR[k] for k in etageres.PRESENTOIR}


def test_cote_comme_cm():
    for v in (0, 1.25, 4.7, 79, 134.0, 243.96, 1 / 3):
        assert meubles.cote(v) == ancien("etageres").cm(v)


def test_cameras():
    vues = {k.removeprefix("etageres-"): v for k, v in vues_du_rendu("rendu_meubles.py").items()
            if k.startswith("etageres-")}
    assert {c.id: {**comme_vue(c), **{k: v for k, v in c.reglages.items() if k != "coupes"}}
            for c in etageres.CAMERAS} == vues
    # l'ancien rendu des meubles cache le plafond à toutes ses vues
    assert all(c.reglages["coupes"] == r"^plafond__" for c in etageres.CAMERAS)
    assert 're.match(r"^plafond__", o.name)' in (ANCIEN / "rendu_meubles.py").read_text(encoding="utf-8")


def test_rendus():
    source = inspect.getsource(ancien("etageres").section_rendus)
    assert [c.id for c in etageres.CAMERAS] == [k for k, _ in etageres.RENDUS]
    for k, texte in etageres.RENDUS:
        assert f'("{k}", "{texte}")' in source


def test_changements():
    """Les entrées du tableau de la page, texte compris et dans le même ordre (du plus récent au plus ancien)."""
    assert [tuple(c) for c in etageres.CHANGEMENTS] == changements_de_la_page("salon-etageres.html")
    assert etageres.CHANGEMENTS[0][0] == etageres.VERSION


@pytest.mark.parametrize("cle", [d["cle"] for d in etageres.DISPOSITIONS])
def test_volumes(cle):
    ET = ancien("etageres")
    e = next(x for x in ET.DISPOS if x.cle == cle)
    assert pieces(volumes.pieces_3d(cle)) == pieces(ET.pieces_3d(e))
    assert [{k: v for k, v in t.items() if k != "libres"} for t in volumes.tablettes(volumes.disposition(cle))] == \
        [{k: v for k, v in t.items() if k != "libres"} for t in e.ts]


def test_volumes_par_defaut_et_detail():
    ET = ancien("etageres")
    assert pieces(volumes.pieces_3d()) == pieces(ET.pieces_3d())
    assert pieces(volumes.pieces_detail()) == pieces(ET.pieces_detail())


def test_disposition_est_une_copie():
    d = volumes.disposition("rangs")
    d["tablettes"].append((222, 0, 1))
    assert volumes.disposition("rangs") != d


def test_dessins_de_reference():
    verifier_dessins("salon-etageres.html")


def test_empreinte_des_rendus():
    verifier_empreinte("pieces.salon.piece", "pieces.salon.etageres.document")
