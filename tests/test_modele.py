import dataclasses

import pytest

from commun.modele import VUES, Document, Element, Option, Valeur, Variante, Vue, verifier


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


def _choix(id="table", codes=("quotidien", "ouverte"), **kw):
    valeurs = tuple(Valeur(c, c) for c in codes)
    return Option(id, id, ("plan",), "choix", kw.pop("defaut", codes[0]), valeurs, "Visible sur le plan.", **kw)


def _nuancier(id="teinte", couleurs=("#EEEBE3", "#a9b8a0")):
    valeurs = tuple(Valeur(f"v{i}", f"v{i}", c) for i, c in enumerate(couleurs))
    return Option(id, id, ("murs",), "nuancier", "v0", valeurs, "Visible sur le plan.", css="--teinte")


def test_option_type_inconnu():
    with pytest.raises(ValueError, match="liste"):
        Option("table", "Table", ("plan",), "liste", "a", (Valeur("a", "A"),), "")


def test_option_defaut_absent():
    with pytest.raises(ValueError, match="pliee"):
        _choix(defaut="pliee")


def test_option_codes_en_double():
    with pytest.raises(ValueError, match="ouverte"):
        _choix(codes=("ouverte", "quotidien", "ouverte"))


def test_option_choix_identifiants():
    with pytest.raises(ValueError, match="Table"):
        _choix(id="Table")
    with pytest.raises(ValueError, match="a b"):
        _choix(codes=("quotidien", "a b"))
    with pytest.raises(ValueError, match="a:b"):
        _choix(codes=("quotidien", "a:b"))
    _choix(id="taille", codes=("175", "180"))


def test_option_choix_sans_css_ni_filtre():
    with pytest.raises(ValueError, match="table"):
        _choix(css="--x")
    with pytest.raises(ValueError, match="table"):
        _choix(filtre=True)


def test_nuancier_couleur():
    with pytest.raises(ValueError, match="v1"):
        _nuancier(couleurs=("#EEEBE3", ""))
    with pytest.raises(ValueError, match="v1"):
        _nuancier(couleurs=("#EEEBE3", "#abc"))
    _nuancier()
    assert _choix().valeurs[0].couleur == ""


def _avec_options(*options):
    return dataclasses.replace(_doc(), options=options)


def test_verifier_options_en_double():
    with pytest.raises(ValueError, match="table"):
        verifier(_avec_options(_choix(), _choix()), _toutes())


def test_verifier_jetons():
    doc = _avec_options(_choix(), _choix("siege", ("dyvlinge", "chil")), _nuancier())

    def scene(texte):
        vues = _toutes()
        vues["plan"] = Vue("plan", [Element("p", "p", "p", texte)])
        return vues

    with pytest.raises(ValueError, match="table:pliee"):
        verifier(doc, scene('<svg><g data-si="table:pliee"></g></svg>'))
    with pytest.raises(ValueError, match="teinte:v1"):
        verifier(doc, scene('<g data-si="teinte:v1"></g>'))
    vues = _toutes()
    vues["coupes"] = Vue("coupes", [Element("A", "A", "A", "", fiche='<template data-si="table:pliee"></template>')])
    with pytest.raises(ValueError, match="table:pliee"):
        verifier(doc, vues)
    vues = _toutes()
    vues["coupes"] = Vue("coupes", [], fiche='<p data-si="table:ouverte siege:dyv">x</p>')
    with pytest.raises(ValueError, match="siege:dyv"):
        verifier(doc, vues)
    verifier(doc, scene('<g data-si="table:ouverte siege:chil"></g>'))


def test_verifier_jetons_entre_guillemets_simples():
    doc = _avec_options(_choix())
    vues = _toutes()
    vues["plan"] = Vue("plan", [Element("p", "p", "p", "<g data-si='table:pliee'></g>")])
    with pytest.raises(ValueError, match="table:pliee"):
        verifier(doc, vues)
    vues["plan"] = Vue("plan", [Element("p", "p", "p", "<g data-si='table:ouverte'></g>")])
    verifier(doc, vues)


def test_verifier_deux_jetons_d_une_option():
    doc = _avec_options(_choix(), _choix("siege", ("dyvlinge", "chil")))
    vues = _toutes()
    vues["coupes"] = Vue("coupes", [Element("A", "A", "A", '<g data-si="table:quotidien siege:chil table:ouverte"></g>')])
    with pytest.raises(ValueError) as e:
        verifier(doc, vues)
    message = str(e.value)
    assert "entree/amenagement" in message and "coupes" in message and "table:quotidien siege:chil table:ouverte" in message
    vues["coupes"] = Vue("coupes", [], fiche="<p data-si='siege:chil siege:chil'>x</p>")
    with pytest.raises(ValueError, match="siege:chil siege:chil"):
        verifier(doc, vues)
