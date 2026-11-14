from commun.appartement import APPART, BAIES, contours
from pieces.sdb import ancien, piece
from tests.sdb_anciennes import ancien as vieux

RELEVES = ("H", "X0", "X1", "Y0", "Y1", "ALCOVE", "SDB", "GONDS", "PORTE", "CHAMBRANLE", "DOUCHE", "LAVABO",
           "CARRELAGE", "EP_CARRELAGE", "ROBINET", "TUYAUX", "PASSE")


def test_releves_comme_modele_py():
    M = vieux("modele")
    for nom in RELEVES:
        assert getattr(piece, nom) == getattr(M, nom), nom
    assert piece.MACHINE == M.LL


def test_contour_de_l_accueil_inchange():
    (avant,) = [c for c in APPART if c.id == "sdb"]
    (apres,) = [c for c in contours() if c.id == "sdb"]
    assert apres.p == avant.p and apres.cotes == avant.cotes == "alcôve 68 × 115"
    assert not hasattr(piece, "SURFACE") and piece.CAMERAS == ()
    assert piece.SOL == [(0, 0), (234, 0), (234, 115), (166, 115), (166, 156), (0, 156)]


def test_porte_de_l_accueil():
    (baie,) = [r for r, _ in BAIES if (r[1], r[3]) == (208, 218)]       # mur nord de la salle de bain
    x, y, _ = piece.POSITION
    assert (baie[0] - x, baie[2] - x) == (piece.PORTE_ACCUEIL["x0"], piece.PORTE_ACCUEIL["x1"])
    assert piece.X1 - piece.PORTE_ACCUEIL["x1"] - piece.GONDS == 9    # l'écart du ruling 1


def test_chargeur():
    M = ancien.modele()
    assert ancien.modele() is M and M.VERSION == "V6.4" and M.Z_HAUT == 158
    import sys
    plan = ancien.charger("plan")           # chargé sans rester sous son nom court
    assert plan.debit() and "modele" not in sys.modules and "plan" not in sys.modules
