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
import montage as MO  # noqa: E402


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


# ------------------------------------------------------------------ revue finale
def _sans_changements(h):
    return re.sub(r'<section id="changements">.*?</section>', "", h, flags=re.S)


def test_siphon_dans_la_notice():
    bas = _sans_changements(pages.page_meuble("bas"))
    assert "siphon" in bas
    assert f"{M.TUYAUX['saillie_max'] * 10:.0f} mm" in M.ETAPES[0][1]
    assert "vidange" in M.ETAPES[6][1] and "siphon" in M.ETAPES[6][1]


def test_niveau_avant_les_coins():
    t = M.ETAPES[2][1]
    assert "niveau" in t and t.index("niveau") < t.index("coin")
    for z in sorted({z for _, z in M.COINS["pos"]}):
        assert M.cm_(z) in t
    assert "sans forcer" in t and "silicone" in M.ETAPES[2][2]
    assert "ensuite sur place" not in M.ETAPES[1][1]


def test_tasseau_de_joint_du_fond():
    deb = {p["rep"]: p for p in PL.debit()}
    assert "G12" in deb and M.meuble("G12") == "haut"
    cal = PL.calepinage()
    assert not cal["G"]["neufs"], "le tasseau de joint se taille dans les barres du meuble bas"
    assert any(q[0] == "G12" for p in cal["G"]["bas"] for q in p.poses())
    tj = next(b for b in M.PIECES if b.rep == "G12")
    for f_ in ("ch_fond_n", "ch_fond_s"):
        fond = next(b for b in M.PIECES if b.nom == f_)
        bord = fond.y1 if f_.endswith("_n") else fond.y0
        ts = [t for t in M.TROUS if t["a"] == f_ and t["b"] == tj.nom]
        assert ts and all(abs(t["y"] - bord) >= 0.8 for t in ts)
    for b in M.PIECES:      # le tasseau ne croise aucune pièce, sauf dans une entaille
        if b is tj or b.groupe != "caisson_haut":
            continue
        ov = [(max(u0, v0), min(u1, v1)) for (u0, u1), (v0, v1) in zip(M._bornes(b), M._bornes(tj))]
        if all(o1 - o0 > 1e-6 for o0, o1 in ov):
            assert any(e[0] <= ov[0][0] + 1e-6 and ov[0][1] <= e[1] + 1e-6 and e[2] <= ov[1][0] + 1e-6
                       and ov[1][1] <= e[3] + 1e-6 for e in b.entailles), b.nom


def test_achats_du_haut_renvoient_au_bas():
    haut = pages.page_meuble("haut")
    e = pages.economie_commune()
    assert e["pieces"] >= 2 and e["euros"] > 0
    assert "séparément" not in pages.materiaux_communs()
    conso = re.search(r"<p>Le caisson haut utilise aussi des consommables achetés avec le meuble bas : (.*?)</p>", haut)
    assert conso and "4 × 40" in conso[1] and "chant" in conso[1] and "silicone" in conso[1]
    assert all(t in haut for _, t in pages.chutes_du_bas())


def test_outils_et_textes():
    assert any("maillet" in o for o in MO.OUTILS["bas"])
    assert "compte peu si haut" not in pages.page_meuble("haut")
    bas = pages.page_meuble("bas")
    assert "Comment percer" in bas


def test_changements_figes():
    t = {v: x for v, _, x in M.CHANGEMENTS}
    assert "(103 du sol" in t["V5.7"]
    assert "plan à 88,1" in t["V5.0"] and "niche de 69,9" in t["V5.0"]
    assert "dessus à 88,1" in t["V4.3"]
