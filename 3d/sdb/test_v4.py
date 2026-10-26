# Tests de la V4 du document (modèle V6.0) : uv run -q --no-project --with pytest pytest -q 3d/sdb/test_v4.py
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))
import modele as M  # noqa: E402


def test_epaisseurs_v6():
    assert M.VERSION == "V6.0" and M.PT == 1.8 and M.TH == 1.8


def test_plan_chene_weldom():
    d = M.PANNEAUX["D"][0]
    assert (d["L"], d["l"], d["prix"], d["ref"]) == (2000, 600, 66.90, "82025610")
    assert M.STOCK["K"] == "M18"


def test_vernis_plan_seul():
    s = sum(M._surface(b) for b in M.PIECES if b.rep.startswith("D"))
    assert abs(M.VERNIS["m2"] - s) < 1e-9 and M.VERNIS["couches"] == 3
    assert [p["ref"] for p, _ in M.VERNIS["achat"]] == ["5603010"]   # un pot de 0,75 L


def test_tuyaux_libres():
    x0, x1, y0, y1, z0, z1 = M.TUYAUX["zone"]
    for b in M.PIECES:
        assert not (b.x0 < x1 and b.x1 > x0 and b.y0 < y1 and b.y1 > y0 and b.z0 < z1 and b.z1 > z0), b.nom


def test_coins_de_calage():
    assert M.COINS["n"] == 8 and {e for e, _ in M.COINS["pos"]} == {"n", "s"}


def test_catalogues():
    assert sum(m["retenu"] for m in M.MATERIAUX_HAUT) == 1
    assert {m["ep"] for m in M.MATERIAUX_HAUT} <= {1.6, 1.8}
    assert sum(e["retenu"] for e in M.ESSENCES_PLAN) == 1
    assert next(e for e in M.ESSENCES_PLAN if e["retenu"])["ref"] == "82025610"


# ------------------------------------------------------------------ tâche 3 : les trois pages
import re  # noqa: E402

import pages  # noqa: E402
import plan as PL  # noqa: E402


def test_budget():
    p = pages.prix()
    assert p["total"] <= M.BUDGET["accepte"] + 0.005     # cible de 400 € dépassée, total accepté par le client
    lignes = sum(n * px for m in ("commun", "bas", "haut") for _, _, n, px, _ in p["lignes"][m])
    assert abs(p["total"] - (lignes + p["ailleurs"])) < 0.01
    assert abs(p["ailleurs"] - M.TOILE["prix"]) < 0.01


def test_tous_les_reperes_poses():
    from collections import Counter
    cal = PL.calepinage()
    poses = Counter(q[0] for st in cal for grp in ("bas", "neufs") for pn in cal[st][grp] for q in pn.poses())
    attendu = Counter({r["rep"]: r["q"] for r in PL.debit() if r["mat"] in M.STOCK})
    assert poses == attendu


def test_pages():
    ens, bas, haut = pages.page_ensemble(), pages.page_meuble("bas"), pages.page_meuble("haut")
    assert 'class="icarr"' in ens and f"carrelage {M.CARRELAGE}" in ens
    assert "Wenko Corno" in ens and 'id="changements"' in ens and "V6.0" in ens
    for h in (ens, bas, haut):
        # l'historique des changements cite légitimement l'ancien vocabulaire : on le retire avant de chercher
        h = re.sub(r'<section id="changements">.*?</section>', "", h, flags=re.S)
        for interdit in ("Coupe", "Élévation", "Bacs à roulettes", "sdb-meuble-v3"):
            assert interdit not in h, interdit
    for h in (bas, haut):
        for sec in ('id="iso"', 'id="montage"', 'id="decoupe"', 'id="achats"'):
            assert sec in h, sec
    assert all(m["nom"] in haut for m in M.MATERIAUX_HAUT)
    assert all(e["nom"] in bas for e in M.ESSENCES_PLAN)


def test_plus_de_v3():
    racine = os.path.join(os.path.dirname(__file__), "..", "..")
    assert not os.path.exists(os.path.join(racine, "sdb-meuble-v3.html"))
    assert not hasattr(M, "PANIERS")
