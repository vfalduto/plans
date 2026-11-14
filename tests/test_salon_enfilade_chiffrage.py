from pieces.salon.enfilade import chiffrage as C
from pieces.salon.enfilade import document as D
from tests.salon_anciens import ancien

TOTAUX = {"A": 901.36, "B": 723.95, "C": 1027.95, "D": 1274.36, "E": 595.45, "F": 1221.86}

def test_comme_l_ancien_generateur():
    EN = ancien("enfilade")
    for nouveau, vieux in zip(D.VARIANTES, EN.VARIANTES):
        assert C.pieces(nouveau) == EN.pieces(vieux)
        a, b = C.chiffrage(nouveau), EN.chiffrage(vieux)
        for cle in ("lignes", "cal", "total", "releve", "estime", "c"):
            assert a[cle] == b[cle], (nouveau["cle"], cle)
        assert C.debit(a["ps"]) == EN.debit(b["ps"])

def test_totaux_des_six_compositions():
    assert {ch["v"]["cle"]: ch["total"] for ch in C.chiffrages()} == TOTAUX
    ch = C.retenu(C.chiffrages())
    assert ch["v"]["cle"] == "C" and (ch["releve"], ch["estime"]) == (775.35, 252.6)
    assert len(ch["ps"]) == 46 and len(C.debit(ch["ps"])) == 13
    assert {k: len(v) for k, v in ch["cal"].items()} == {"C18": 10}
    assert ch["c"]["portes"] == 4 and ch["c"]["pieds"] == 8

def test_prix_et_lettre():
    assert C.prix(1027.95) == "1 027,95 €" and C.prix(109) == "109,00 €"
    assert [C.lettre(n) for n in (2, 4, 10)] == ["deux", "quatre", "10"]

def test_volume_et_degagements():
    assert round(C.volume_utile()) == 788
    assert C.degagements() == (20.3, 8.2)

def test_poids_d_un_caisson_corrige():
    assert C.poids_caisson() == 17          # l'ancienne page affichait 1361 (largeur comptée deux fois)
