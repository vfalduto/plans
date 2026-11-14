"""Le modèle du meuble haut : débit, calepinage, chant, achats ; les mêmes résultats que l'ancienne page (haut.py)."""
from collections import Counter

from pieces.sdb.achats_communs import deux_meubles, total_haut
from pieces.sdb.meuble_haut import modele as H
from tests.sdb_anciennes import ancien

M = H.M


def test_le_modele_est_celui_de_3d_sdb():
    from pieces.sdb import ancien as chargeur
    assert M.VERSION == "V6.4" == H.VERSION and M is chargeur.modele()


def test_debit_comme_plan_py():
    assert H.debit() == ancien("plan").debit()
    assert [p["rep"] for p in H.debit_haut()] == ["G12", "K1", "K2", "K3", "K4", "K5", "K6", "K7", "K8"]
    assert sum(p["q"] for p in H.debit_haut()) == 17


def test_pieces_posees_seules():
    poses = Counter(q[0] for c in H.calepinage_seul().values() for pn in c["retenu"]["panneaux"] for q in pn.poses())
    assert poses == Counter({r["rep"]: r["q"] for r in H.debit_haut()})
    assert {"K1", "G12"} <= set(poses)                   # celles qui étaient dans les chutes du bas


def test_chant_et_rouleaux():
    m = H.metres_chant()
    assert abs(m - 5.042) < 1e-3 and H.virg(m, 2) == "5,04"          # l'ancienne page écrivait « 54 m »
    assert H.rouleaux_haut() == 2 and H.rouleaux_haut() * M.CHANT["rouleau"] >= m * 1000 > M.CHANT["rouleau"]
    assert H.virg(0.86, 2) == "0,86" and H.virg(3.0, 2) == "3" and H.virg(5.24, 2) == "5,24"


def test_liste_d_achats_179_82():
    ls = H.lignes()
    assert len(ls) == 12
    assert abs(H.total_lignes(ls) - 179.82) < 0.005 and round(total_haut(), 2) == 179.82
    refs = [ref for _, ref, _, _, _ in ls]
    assert "5603010" not in refs                         # vernis : aucune étape du haut
    assert H.consommables_haut() == ["vis40", "silicone"]
    assert M.WELDOM["vis40"][4] in refs and M.WELDOM["silicone"][4] in refs
    assert next(n for _, ref, n, _, _ in ls if ref == M.WELDOM["chant"][4]) == H.rouleaux_haut()
    assert H.quincaillerie_totale() == {"vis40": 54, "chant": 2, "cheville": 6, "taquet": 24, "led": 1, "silicone": 1,
                                        "patins": 2}


def test_total_des_deux_meubles():
    h = deux_meubles({"bas": "", "haut": ""})
    for montant in ("296,82 €", "179,82 €", "476,64 €"):
        assert montant in h


def test_etapes_du_haut_sans_le_bas():
    assert H.ETAPES == (8, 9, 10)
    for n in H.ETAPES:
        assert "meuble bas" not in M.texte_etape(n), n


def test_ancien_total_reste_celui_des_archives():
    pages = ancien("pages")
    assert abs(pages.prix()["total"] - 428.33) < 0.005
