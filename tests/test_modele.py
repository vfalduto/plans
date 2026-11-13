import pytest

from commun.modele import VUES, Document, Element, Variante, Vue, verifier


def _doc(type="amenagement", variantes=None):
    variantes = variantes or (Variante("", "Principale", "1.0", ()),)
    return Document("entree", "amenagement", "Aménagement", type, variantes, lambda v: {})


def _elt(k):
    return Element(k=k, nom=k, titre=k, scene="")


def _toutes(type="amenagement"):
    return {v: Vue(v, []) for v in VUES[type]}


def test_vues_dans_l_ordre():
    assert VUES["amenagement"][0] == "plan"
    assert VUES["construction"][-1] == "explication"


def test_verifier_refuse_une_vue_inconnue():
    vues = _toutes()
    vues["plans"] = Vue("plans", [])
    with pytest.raises(ValueError, match="plans"):
        verifier(_doc(), vues)


def test_verifier_refuse_k_en_double():
    vues = _toutes()
    vues["coupes"] = Vue("coupes", [_elt("A"), _elt("A")])
    with pytest.raises(ValueError):
        verifier(_doc(), vues)


def test_vue_vide_acceptee():
    vues = _toutes()
    vues["iso"] = Vue("iso", [])
    verifier(_doc(), vues)


def test_verifier_refuse_une_vue_manquante():
    vues = _toutes()
    del vues["camera"]
    with pytest.raises(ValueError, match="camera"):
        verifier(_doc(), vues)


def test_verifier_refuse_deux_variantes_de_meme_id():
    v = Variante("a", "A", "1.0", ())
    with pytest.raises(ValueError):
        verifier(_doc(variantes=(v, v)), _toutes())
