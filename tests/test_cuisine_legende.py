"""Légende du plan de la cuisine/aménagement (pieces/cuisine/amenagement/legende.py) : l'ancienne légende, coupée en
morceaux (légende de la fiche du plan, cartes « Principe »), confrontée à l'originale ; rien ne se perd."""
import html
import json
import re

from commun.blocs import principes
from pieces.cuisine.amenagement import legende as L
from pieces.cuisine.amenagement import zones as Z
from tests.cuisine_anciens import FIXTURES

ORIGINALE = json.loads((FIXTURES / "legendes.json").read_text(encoding="utf-8"))["plan"]
IDS = {m[0] for m in Z.MEUBLES_PLAN}


def _texte(fragment):
    return re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", "", fragment))).strip()


def test_rien_ne_se_perd():
    morceaux = L.morceaux()
    assert _texte(" ".join(m.html for m in morceaux)) == _texte(ORIGINALE).replace(" · ", ", ")
    assert " ".join(m.html for m in morceaux) == ORIGINALE.replace(" · ", ", ")   # au caractère près
    for m in morceaux:
        assert m.html == m.html.strip() and m.html, m


def test_balises_conservees():
    gras = re.findall(r"<b>.*?</b>", ORIGINALE)
    assert re.findall(r"<b>.*?</b>", " ".join(m.html for m in L.morceaux())) == gras
    for m in L.morceaux():
        assert m.html.count("<b>") == m.html.count("</b>"), m   # aucun gras coupé en deux


def test_repartition():
    morceaux = L.morceaux()
    assert {m.ou for m in morceaux} == {"legende", "carte"}
    leg = [m for m in morceaux if m.ou == "legende"]
    assert leg == morceaux[:len(leg)]                       # la convention d'abord, comme dans l'originale
    assert leg[0].html.startswith("Échelle") and "<b>Sols</b>" in leg[-1].html and "tireté" in leg[-1].html
    for m in morceaux:
        assert bool(m.titre) == (m.ou == "carte"), m
        assert not m.meuble or m.ou == "carte", m
    titres = [c.titre for c in L.cartes()]
    assert len(titres) == len(set(titres))                  # une carte par titre
    for t in ("Mur nord", "Induction", "Réseaux", "Cellier", "Coin repas", "Meubles hauts"):
        assert t in titres, t


def test_chaque_morceau_visible_sans_js():
    page = principes(L.cartes())
    legende = L.legende_html()
    for m in L.morceaux():
        if m.ou == "carte":
            assert m.html in page, m
        else:
            assert f"<p>{m.html}</p>" in legende, m
    assert legende.count("<p>") == sum(m.ou == "legende" for m in L.morceaux())


def test_cartes_reunies():
    cartes = L.cartes()
    morceaux = [m for m in L.morceaux() if m.ou == "carte"]
    assert " ".join(c.texte for c in cartes) == " ".join(m.html for m in morceaux)
    for c in cartes:
        siens = {m.meuble for m in morceaux if m.titre == c.titre}
        assert c.meuble == (siens.pop() if len(siens) == 1 else ""), c.titre


def test_meubles_connus():
    morceaux = L.morceaux()
    for m in morceaux:
        assert not m.meuble or m.meuble in IDS, m
        assert m.meuble not in m.nomme and set(m.nomme) <= IDS, m
    # un morceau qui ne parle que d'un meuble le porte ; ceux qui en nomment plusieurs vont dans chacune de leurs fiches
    textes = L.textes_par_meuble()
    for id_ in [f"b{i}" for i in range(1, 7)] + ["h1", "c1", "c2"]:
        assert textes.get(id_), id_
    assert any(m.meuble == "porte-cellier" for m in morceaux) and any(m.meuble == "banquette" for m in morceaux)
    assert set(textes) <= IDS


def test_textes_par_meuble_en_ligne():
    for id_, t in L.textes_par_meuble().items():
        assert "<p" not in t and "<div" not in t, id_
        for m in L.morceaux():
            if id_ == m.meuble or id_ in m.nomme:
                assert m.html in t, (id_, m.titre)
    zs = {z.id: z for z in Z.zones(L.textes_par_meuble())}
    assert "<b>Porte du cellier</b>" in zs["porte-cellier"].texte


def test_sans_point_median():
    sortie = [m.html for m in L.morceaux()] + [L.legende_html(), principes(L.cartes())]
    sortie += list(L.textes_par_meuble().values()) + [c.titre for c in L.cartes()]
    for s in sortie:
        assert "·" not in s
