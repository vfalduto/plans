import re
from html import escape

from pieces.salon.enfilade import document, vues
from tests.salon_enfilade_ancienne import corrige, morceaux, page, section, texte

S = vues.vues("")["explication"].elements[0].scene


def test_ordre_des_sections():
    assert re.findall(r"<h2>(.*?)</h2>", S) == ["Le meuble", "Rendus 3D", "Construction", "Matériaux",
        "Comparaison avec IKEA STOCKHOLM", "Comparaison avec trois METOD 80", "Points à valider"]


def test_chiffres_cles():
    assert re.findall(r"<dt>(.*?)</dt>", S) == ["240 × 60 × 80", "1 027,95 €", "788 L", "13", "46", "11",
                                               "20,3 cm", "8,2 cm"]


def test_rendus():
    for cle, alt in document.RENDUS:
        assert (vues.RENDUS_SITE / f"{cle}.jpg").is_file()
        assert f'src="rendus/{cle}.jpg" alt="{escape(alt, quote=True)}"' in S
    assert S.count('src="rendus/iso.jpg"') == 2       # la tête et « Rendus 3D » (ruling 11)


def test_construction():
    assert re.findall(r"<h3>(.*?)</h3>", section_neuve("Construction")) == ["Trois caissons plutôt qu'un", "Caisson",
        "Dessus", "Socle : 8 pieds réglables", "Portes", "Tiroirs", "Étagères", "Fixation au mur", "Finition"]
    assert "moins de 3,8 d'épaisseur" in S and "18,3 m² de faces" in S


def section_neuve(titre):
    return S.split(f"<h2>{titre}</h2>", 1)[1].split("<h2>", 1)[0]


def test_materiaux_six_compositions():
    t = section_neuve("Matériaux")
    assert t.count("<tr>") == 1 + 6 and "<b>C</b> retenu" in t
    for montant in ("901,36 €", "1 027,95 €", "1 221,86 €", "−304,00 €", "+193,91 €"):
        assert montant in t


def test_comparaisons():
    assert S.count('<figure class="schema"><svg class="enf"') == 2
    caps = [texte(c) for c in re.findall(r'<p class="cap">(.*?)</p>', page(), re.S)][6:8]
    for cap in caps:
        assert f'aria-label="{escape(cap, quote=True)}"' in S
    metod = section_neuve("Comparaison avec trois METOD 80")
    assert metod.count('<div class="defile">') == 5 and "1 035,60 €" in metod and "966,40 €" in metod


def test_rien_ne_se_perd():
    for ancre in ("meuble", "construction", "materiaux", "comparaison", "metod", "valider"):
        for m in morceaux(section(page(), ancre)):
            if m.startswith("Page générée depuis 3d/salon/"):   # remarque finale, remplacée (ruling 18)
                continue
            assert corrige(m) in texte(S), (ancre, m)
    assert S.count("<li><span>") == 12                   # points à valider


def test_liens_externes_gardes():
    vieux = set(re.findall(r'href="(https?://[^"]+)"', page()[page().index("<body"):]))
    tout = "".join(v.elements[0].scene + v.fiche for v in vues.vues("").values() if v.elements)
    assert vieux <= set(re.findall(r'href="(https?://[^"]+)"', tout))


def test_remarque_finale_et_style():
    assert 'href="../../salon-v4.html"' in S and "3d/salon" not in S
    for interdit in ("·", "mono", "badge", 'class="cap"'):
        assert interdit not in S
