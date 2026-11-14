import math
import re

from commun.appartement import APPART, contours
from commun.journal import depuis_page
from pieces.chambre import piece
from pieces.chambre.amenagement import document
from tests.outils import RACINE

ANCIENNE = (RACINE / "tests/fixtures/chambre/chambre-amenagement.html").read_text(encoding="utf-8")


def test_piece():
    assert piece.SOL == [(0, 0), (428, 0), (428, 10), (441, 10), (441, 251), (47, 251), (47, 80), (0, 80)]
    assert math.isclose(piece.SURFACE, (441 * 251 - 47 * 171 - 13 * 10) / 1e4)
    assert (piece.H, piece.POSITION, piece.CAMERAS) == (250, (364, 112, 0), ())
    assert piece.PORTE["b"] - piece.PORTE["a"] == 67


def test_cotes_de_la_page():
    D = document
    assert D.PLAN["x1"] - D.PLAN["x0"] == 42 and D.PLAN["y1"] - D.PLAN["y0"] == 241
    assert D.PLAN["y1"] - D.PLAN["y0"] == 2 * 80 + (D.NICHE["y1"] - D.NICHE["y0"]) + (D.JOUE["y1"] - D.JOUE["y0"])
    assert D.NICHE["y1"] - D.NICHE["y0"] == 79
    assert (D.LIT["x0"] - D.PLACARD["x1"], D.L - D.LIT["x1"]) == (117, 117)
    assert D.PLACARD["y1"] - D.PLACARD["y0"] - D.PLACARD["cloison"] == 164
    assert D.PLACARD["porte"][1] - D.PLACARD["porte"][0] == 155
    assert [round(math.dist(p["a"], p["b"])) for p in D.passages(D)] == [47, 117, 70, 75, 42, 7]


def test_changements_de_la_page():
    assert [(c[0], c[1], c[2]) for c in document.CHANGEMENTS] == [
        (c.version, c.date, c.texte) for c in depuis_page(ANCIENNE)]
    assert len(document.CHANGEMENTS) == 5
    # le bandeau de la page est « Chambre · V2.1 · plan et élévations » : la version n'en est pas le dernier morceau
    assert document.VERSION == re.search(r'class="kicker">[^<]*· (V[\d.]+) ·', ANCIENNE).group(1) == "V2.1"
    assert (RACINE / "site" / document.FIGEES_ANCIENNES[0][1]).is_file()


def test_accueil():
    chambre = {c.id: c for c in contours()}["chambre"]
    assert chambre.p == next(c.p for c in APPART if c.id == "chambre")
    assert chambre.cotes == "10,3 m²"


def test_barres_de_la_niche():
    # page, carte ④ : « devant à 70, derrière à 76 » ; la pièce est côté x 401, le mur à x 441
    devant, derriere = sorted(document.NICHE["barres"])
    assert devant[0] < derriere[0]
    assert (devant[1], derriere[1]) == (70, 76)
