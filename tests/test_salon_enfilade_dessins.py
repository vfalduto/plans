import re
import pytest
from commun.css_dessins import css_dessins
from pieces.salon.enfilade import chiffrage, dessins
from pieces.salon.enfilade.document import METOD_CAISSON, METOD_MIXTE, NORD
from tests.outils import RACINE

FIX = RACINE / "tests/fixtures/salon"
def _sans_aria(s): return re.sub(r' aria-label="[^"]*"', "", s)
def _ref(nom): return _sans_aria((FIX / nom).read_text(encoding="utf-8")).replace(" · ", ", ")
def _metod(): return dessins.comparaison_svg(autres=[(METOD_MIXTE["nom"], METOD_MIXTE["l"], METOD_MIXTE["p"],
    METOD_MIXTE["h"], METOD_CAISSON["pieds"], True, [NORD + 80, NORD + 160])],
    titre="Comparaison des dimensions avec trois caissons METOD 80, composition mixte")

DESSINS = {
    "enfilade-enfilade-fermee-vue-iso.svg": lambda: dessins.iso(False, "x"),
    "enfilade-enfilade-ouverte-vue-iso.svg": lambda: dessins.iso(True, "x"),
    "enfilade-elevation-de-face-cotee-de-l-enfilade.svg": dessins.face_svg,
    "enfilade-coupes-de-profil-de-l-enfilade.svg": dessins.profil_svg,
    "enfilade-vue-de-dessus-de-l-enfilade-avec-les-ouvertures.svg": dessins.dessus_svg,
    "enfilade-vue-eclatee-de-l-enfilade.svg": dessins.eclate_svg,
    "enfilade-comparaison-des-dimensions-avec-le-buffet-ikea-stockholm-2025.svg": dessins.comparaison_svg,
    "enfilade-comparaison-des-dimensions-avec-trois-caissons-metod-80-composition-mixte.svg": _metod,
}

@pytest.mark.parametrize("nom", DESSINS)
def test_dessins_comme_la_reference(nom):
    s = DESSINS[nom]()
    assert _sans_aria(s) == _ref(nom) and "·" not in s

def _panneaux():
    ch = chiffrage.retenu(chiffrage.chiffrages())
    return [dessins.decoupe_svg("C18", pa, n + 1) for n, pa in enumerate(ch["cal"]["C18"])]

def test_panneaux_comme_la_reference():
    noms = sorted((p for p in FIX.glob("enfilade-chene-18-n-*.svg")), key=lambda p: int(p.name.split("-")[4]))
    assert len(noms) == 10
    for (titre, s), p in zip(_panneaux(), noms):
        assert _sans_aria(s) == _ref(p.name)
        assert f'aria-label="{titre}"' in s and "·" not in titre
    assert _panneaux()[0][0] == "chêne 18 n° 1, 200 × 60, chute 20 %"

def test_label_echappe():
    for s in (dessins.face_svg(label='a "b" & c'), dessins.iso(False, 'a "b" & c')):
        assert 'aria-label="a &quot;b&quot; &amp; c"' in s

def test_en_cm():
    brut = dessins.face_svg()
    s = dessins.en_cm(brut, 3.4)
    vb = [float(x) for x in re.search(r'viewBox="([^"]*)"', brut).group(1).split()]
    assert re.search(r'viewBox="([^"]*)"', s).group(1) == " ".join(f"{round(v / 3.4, 3):g}" for v in vb)
    assert '<g transform="scale(0.294118)">' in s and s.endswith("</g></svg>")
    assert re.sub(r'viewBox="[^"]*"|<g transform="[^"]*">|</g></svg>$', "", s) == \
        re.sub(r'viewBox="[^"]*"|</svg>$', "", brut)

def _tous():
    return [f() for f in DESSINS.values()] + [s for _, s in _panneaux()]

def _a_une_regle(classe, css):
    return re.search(rf"\.{re.escape(classe)}(?![\w-])", css) is not None

def test_classes_ont_une_regle():
    """Chaque classe d'un élément d'un dessin (scène, Découpe, Explication) a une règle : rien n'est noir par défaut."""
    tous = _tous() + ['<span class="lg chene"></span><span class="lg chute"></span><figure class="schema"></figure>']
    css = css_dessins(dessins.CSS, tous, ".d-salon")
    site = (RACINE / "commun/site.css").read_text(encoding="utf-8")
    classes = {c for s in tous for m in re.findall(r'class="([^"]+)"', s) for c in m.split()}
    assert {"enf", "dim", "dimt", "sofa", "chute", "lg", "schema"} <= classes
    assert sorted(c for c in classes if not _a_une_regle(c, css) and not _a_une_regle(c, site)) == []
    assert ".d-salon svg.enf text{" in css

def test_css_sans_chasse_fixe_ni_capitales():
    for interdit in ("JetBrains", "monospace", "uppercase", "prefers-color-scheme", "--sofa"):
        assert interdit not in dessins.CSS
