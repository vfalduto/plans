"""Salon, enfilade (pieces/salon/enfilade/) : reprise de 3d/salon/modele.py (section ①) et de enfilade.py."""
import inspect

import pytest

from pieces.salon import meubles
from pieces.salon.enfilade import document as enfilade
from pieces.salon.enfilade import volumes
from tests.salon_anciens import (ANCIEN, MODELE, ancien, changements_de_la_page, comme_vue, norm, pieces,
                                 verifier_dessins, verifier_empreinte, vues_du_rendu)

# ancien nom dans 3d/salon/enfilade.py → nom dans pieces/salon/enfilade/document.py
REPRIS = {n: n for n in ("VERSION", "DATE", "RELEVE", "L", "NORD", "P", "Z1", "ZP", "EP", "MODULES", "N", "FAC",
                         "TAMPON", "DOS", "PC", "JEU", "BORD", "TRAV", "TRAIT", "COULISSE", "EP_COUL", "H_BOITE",
                         "CALE_BOITE", "PROF_ETAGERE", "CHARNIERE", "PIEDS_X", "DESSUS", "VINYLE", "MAGASINS",
                         "ORDRE_MAG", "LM_PT", "LM_HDF", "LM_PIED", "LM_CP", "LM_MC", "LM_PT25", "LM_T20", "CASTO_PT",
                         "CASTO_PT26", "REF_COUL", "REF_HUILE", "FORMATS", "MELAMINE", "OUTILLAGE", "VARIANTES",
                         "HUILE", "CHANT", "RETENUE", "PREFIXE", "GROUPES", "STOCKHOLM", "IKEA_FR", "METOD_RELEVE",
                         "LM_PT26", "METOD_CAISSON", "KNIV", "SOCLE", "POUSSOIRS", "ANTI", "METOD", "JEU_METOD",
                         "PIECES_METOD", "METOD_MIXTE", "VRENA", "METOD_PLAN_LM", "NOIRS")}
REPRIS["ETAGERES"] = "ETAGERES_CAISSONS"
# laissés, et pourquoi : modules et alias (C, M, E), géométrie calculée (G, voir test_geometrie), page (FLECHE, STYLE),
# quincaillerie (QUINC, quantités devenues des données, voir test_quincaillerie)
LAISSES = {"C", "M", "E", "G", "FLECHE", "STYLE", "QUINC"}


@pytest.mark.parametrize("ancien_nom", sorted(MODELE["enfilade"]))
def test_constantes_du_modele(ancien_nom):
    nom = MODELE["enfilade"][ancien_nom]
    assert norm(getattr(enfilade, nom)) == norm(getattr(ancien("modele"), ancien_nom))


@pytest.mark.parametrize("ancien_nom", sorted(REPRIS))
def test_constantes_du_generateur(ancien_nom):
    assert norm(getattr(enfilade, REPRIS[ancien_nom])) == norm(getattr(ancien("enfilade"), ancien_nom))


def test_generateur_entierement_vu():
    assert {n for n in vars(ancien("enfilade")) if n.isupper()} == set(REPRIS) | LAISSES


def test_quincaillerie():
    """QUINC porte ses quantités en données (q) : même texte, et quantite() rend ce que rendaient les lambdas."""
    EN = ancien("enfilade")
    jeux = [dict(portes=4, tiroirs=3, pieds=8, facades=7, etageres=3, jonctions=2, caissons=3, chene_m2=6.4)]
    for v in EN.VARIANTES.values() if isinstance(EN.VARIANTES, dict) else EN.VARIANTES:
        jeux.append(EN.comptes(EN.pieces(v), EN.geometrie(v["dessus"][0]), v))
    assert len(enfilade.QUINC) == len(EN.QUINC)
    for neuf, vieux in zip(enfilade.QUINC, EN.QUINC):
        assert {k: v for k, v in neuf.items() if k != "q"} == {k: v for k, v in vieux.items() if k != "q"}
        for c in jeux:
            assert enfilade.quantite(neuf["q"], c) == vieux["q"](c), neuf["poste"]


def test_cote_comme_virg():
    """L'enfilade affichait ses cotes par sa propre virg (240 → « 240 », là où commun.dessin.virg donne « 240,0 »)."""
    EN = ancien("enfilade")
    for v in (0, 1.8, 8.8, 60.84, 240, 240.0, 1 / 3):
        assert meubles.cote(v) == EN.virg(v)
        assert meubles.cote(v, 2) == EN.virg(v, 2)
    assert meubles.cote(240) == "240" and meubles.virg(240) == "240,0"


def test_cameras():
    vues = {k.removeprefix("enfilade-"): v for k, v in vues_du_rendu("rendu_meubles.py").items()
            if k.startswith("enfilade-")}
    assert {c.id: {**comme_vue(c), **{k: v for k, v in c.reglages.items() if k != "coupes"}}
            for c in enfilade.CAMERAS} == vues
    # l'ancien rendu des meubles cache le plafond à toutes ses vues
    assert all(c.reglages["coupes"] == r"^plafond__" for c in enfilade.CAMERAS)
    assert 're.match(r"^plafond__", o.name)' in (ANCIEN / "rendu_meubles.py").read_text(encoding="utf-8")


def test_rendus():
    source = inspect.getsource(ancien("enfilade").section_rendus)
    assert [c.id for c in enfilade.CAMERAS] == [k for k, _ in enfilade.RENDUS]
    for k, texte in enfilade.RENDUS:
        assert f'("{k}", "{texte}")' in source


def test_changements():
    """Les entrées du tableau de la page, texte compris ; la page les donnait du plus ancien au plus récent."""
    assert [tuple(c) for c in enfilade.CHANGEMENTS] == changements_de_la_page("salon-enfilade.html")[::-1]
    assert enfilade.CHANGEMENTS[0][0] == enfilade.VERSION


def test_geometrie():
    EN = ancien("enfilade")
    assert volumes.G == EN.G
    for ep in (1.8, 3.6):
        assert volumes.geometrie(ep) == EN.geometrie(ep)
    assert volumes.controle() == EN.controle()


@pytest.mark.parametrize("ouvert", [False, True])
def test_volumes(ouvert):
    ps = volumes.pieces_3d(ouvert=ouvert)
    assert pieces(ps) == pieces(ancien("enfilade").pieces_3d(ouvert=ouvert))
    assert volumes.chevauchements(ps) == []


def test_dessins_de_reference():
    verifier_dessins("salon-enfilade.html")


def test_empreinte_des_rendus():
    verifier_empreinte("pieces.salon.piece", "pieces.salon.enfilade.document")
