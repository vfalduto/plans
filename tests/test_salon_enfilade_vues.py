import re
from html import escape

import pytest

from commun.modele import Document, Variante, verifier
from pieces.salon.enfilade import chiffrage, vues
from tests.salon_enfilade_ancienne import corrige, morceaux, page, section, texte

V = vues.vues("")


def _scene(cle):
    return V[cle].elements[0].scene


def test_cinq_vues_et_verifier():
    doc = Document("salon", "enfilade", "Enfilade", "construction", (Variante("", "Enfilade", "V1.6", ()),), vues.vues)
    verifier(doc, V)
    assert list(V) == ["plans", "decoupe", "montage", "achats", "explication"]
    with pytest.raises(ValueError):
        vues.vues("autre")


def test_plans():
    p = V["plans"]
    assert [e.k for e in p.elements] == ["elevation", "iso", "ouverte", "profil", "dessus", "eclate"]
    assert {e.titre for e in p.elements} == {"Enfilade du mur ouest"}
    for e in p.elements:
        assert e.scene.startswith('<svg data-mesure="non"') == (e.k in ("iso", "ouverte"))
    assert p.outils == ("zoom", "mesure")
    assert "240 = 3 × 80, centré sur le mur (8,8 libres de chaque côté)" in p.fiche
    assert 'href="#decoupe"' in p.fiche and 'href="#montage"' in p.fiche


def _caps():
    return [corrige(texte(c)) for c in re.findall(r'<p class="cap">(.*?)</p>', page(), re.S)][:6]


def test_alts_sont_les_textes_sous_les_dessins():
    a = vues.alts(chiffrage.retenu(chiffrage.chiffrages()))
    ordre = ["iso", "ouverte", "elevation", "profil", "dessus", "eclate"]   # ordre de l'ancienne page
    assert [a[k] for k in ordre] == _caps()
    assert "Quatre portes de 39,7" in a["elevation"]
    for e in V["plans"].elements:
        assert f'aria-label="{escape(a[e.k], quote=True)}"' in e.scene


def test_aucune_description_visible():
    a = vues.alts(chiffrage.retenu(chiffrage.chiffrages()))
    for cle, v in V.items():
        for e in v.elements:
            visible = re.sub(r'aria-label="[^"]*"', "", e.scene + v.fiche)
            assert not any(escape(t, quote=True) in visible or t in visible for t in a.values()), cle


def test_decoupe():
    s = _scene("decoupe")
    assert s.count("<tbody>") == 1 and s.split("<tbody>")[1].count("<tr>") == 13
    assert "46 pièces, 13 repères." in s and "A : caissons." in s
    assert s.count('<figure class="calepin">') == 10 and "<h2>Plan de découpe</h2>" in s
    assert "Tablette chêne lamellé-collé 200 × 60 × 1,8 × 10" in s and "2,61 m²" in s
    for m in morceaux(section(page(), "debit")):
        assert corrige(m) in texte(s), m


def test_montage():
    s = _scene("montage")
    assert s.count("<li>") == 11 + 5 and "Outils à réunir" in s
    assert "17 kg environ" in s and "1361" not in s
    for m in morceaux(section(page(), "montage")):
        if m not in ("Outils", "Étapes"):
            assert corrige(m) in texte(s), m


def test_achats():
    s = _scene("achats")
    assert "<h3>Weldom Marseille Saint-Barnabé</h3>" in s and "<h3>Leroy Merlin</h3>" in s
    assert "904,70 €" in s and "123,25 €" in s and "1027,95 €" in s
    assert "29/10/2026" in s and "relevé" in s and "estimé" in s
    assert s.count("<tr>") == 15 + 3 + 2      # lignes, plus les deux en-têtes ; « Sous-total » est un <tr class="total">
    for m in morceaux(section(page(), "achats")):
        assert corrige(m).replace("Total : ", "Total (composition C) : ") in texte(s), m


def test_liens_externes_gardes():
    vieux = set(re.findall(r'href="(https?://[^"]+)"', section(page(), "debit") + section(page(), "achats")))
    neufs = set(re.findall(r'href="(https?://[^"]+)"', _scene("decoupe") + _scene("achats")))
    assert vieux <= neufs


def test_sans_point_median_ni_chasse_fixe():
    for cle, v in V.items():
        for e in v.elements:
            assert "·" not in e.scene + v.fiche and "mono" not in e.scene, cle
