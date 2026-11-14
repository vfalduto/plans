import re
from commun.css_dessins import css_dessins
from pieces.sdb import dessin_cotes as DC, iso
from tests.outils import RACINE
from tests.sdb_anciennes import ancien

CAS = [("cote_h", (174, 234, 18), {"label": "60 plateau", "ext": 4}), ("cote_h", (0, 3, 6), {"ext": 0, "place": "gauche"}),
       ("cote_h", (5, 6.5, 6), {"dy": 3.4, "place": "droite"}), ("cote_v", (-88.8, -87, 230), {}),
       ("cote_v", (-10, -9, 5), {"place": "haut", "ext": 2}), ("cote_v", (-4, -1, 5), {"dx": 3.4, "place": "bas"}),
       ("niveaux", ([(86, "86 machine", 0), (88.8, None, 0), (90, "90", 0)], -7), {}),
       ("niveaux", ([(3.8, "3,8", 10)], 13), {"droite": True}),
       ("etiquette", (1, 2, 8, -3, "Colonne", "end"), {}), ("etiquette", (1, 2, 8, -3, "Vérin"), {}),
       ("svg", (0, -10, 20, 5, ["<g/>"], "Titre « a » & l'b"), {})]


def test_aides_comme_cotes_py():
    CO, PL = ancien("cotes"), ancien("plan")
    for nom, a, k in CAS:
        assert getattr(DC, nom)(*a, **k) == getattr(CO, nom)(*a, **k), nom
    for v in (47.50000000000001, 1.8, 0.25, 114.4):
        assert (DC.f(v), DC.cm(v)) == (PL.f(v), PL.cm(v))
    assert DC.text(1, 2, "a & b", "lt", "end") == PL.text(1, 2, "a & b", "lt", "end")
    assert DC.poly([(0, 1.234), (2, 3)], "omel") == PL.poly([(0, 1.234), (2, 3)], "omel")


def _appels():
    MO, M = ancien("montage"), ancien("modele")
    tout = M.version("d")
    bl = [b for b in tout if b.groupe == "caisson_haut" and b.etape <= 8 and b.role != "led"]
    neuves = {b.nom for b in MO.pieces_etape("d", 8)}
    dec = {"plan": (0, 0, 35), "bac": (-20, 0, 0), "machine": (-80, 75, 0)}
    return MO, [((tout,), dict(murs=True, reperes=False, carrelage=M.CARRELAGE, titre="Tout")),
                ((bl, neuves), dict(titre="Étape 8", trous=MO.trous_etape(8, bl))),
                ((tout,), dict(reperes=False, decale=dec, titre="Éclaté")),
                (([],), dict(murs=True, titre="Vide"))]


def test_iso_comme_montage_py():
    MO, appels = _appels()
    for a, k in appels:
        assert iso.dessin(*a, **k) == MO.dessin(*a, **k), k["titre"]


def test_css_couvre_les_classes():
    _, appels = _appels()
    dessins = [iso.dessin(*a, **k) for a, k in appels] + [DC.cote_h(0, 5, 1) + DC.niveaux([(3, "3", 0)], 2)
                                                          + DC.etiquette(0, 0, 1, 1, "x") + DC.svg(0, 0, 1, 1, [], "t")]
    css = css_dessins(DC.CSS + "\n" + iso.CSS, dessins, ".d-sdb")
    site = (RACINE / "commun/site.css").read_text(encoding="utf-8")
    classes = {c for s in dessins for m in re.findall(r'class="([^"]+)"', s) for c in m.split()}
    regle = lambda c, t: re.search(rf"\.{re.escape(c)}(?![\w-])", t) is not None   # noqa: E731
    assert {"isol", "inew", "itr", "ibt", "ct", "nt", "dim", "niv", "cotes"} <= classes
    assert sorted(c for c in classes if not regle(c, css) and not regle(c, site)) == []


def test_css_au_style_du_site():
    for interdit in ("JetBrains", "monospace", "uppercase", "prefers-color-scheme", "var(--tile)", "var(--dg)",
                     "var(--bas)", "var(--haut)", "min-width", ".fcote", ".feuille"):
        assert interdit not in DC.CSS + iso.CSS, interdit
    assert "svg.cotes .ct{font:600 2.5px var(--ui)" in DC.CSS and ".ibt{font:700 4.4px var(--ui)" in iso.CSS
