# Tests du meuble bas : uv run -q --no-project --with pytest pytest -q 3d/sdb/test_bas.py
import os
import re
import sys

sys.path.insert(0, os.path.dirname(__file__))
import bas  # noqa: E402
import modele as M  # noqa: E402

EPS = 1e-6


def _b(nom):
    return next(b for b in bas.blocs() if b.nom == nom)


def _recouvre(a, b, axes):
    return all(getattr(a, f"{k}0") < getattr(b, f"{k}1") - EPS and getattr(b, f"{k}0") < getattr(a, f"{k}1") - EPS for k in axes)


def test_rien_ne_se_traverse():
    ps = bas.blocs()
    for i, a in enumerate(ps):
        for c in ps[i + 1:]:
            assert not _recouvre(a, c, "xyz"), (a.nom, c.nom)
        assert M.Y0 < a.y0 and a.y1 < M.Y1 and a.x1 <= M.X1, a.nom


def test_chaque_piece_a_un_appui_reel():
    """Constructibilité : le plateau pose directement sur les joues ; chaque joue sur ses 2 vérins, dans le chant ; les vérins au sol."""
    p = _b("plateau")
    for k in "ncs":
        j = _b(f"joue_{k}")
        assert abs(j.z1 - p.z0) < EPS and _recouvre(j, p, "xy"), k
        for i in "01":
            v = _b(f"verin_{k}{i}")
            assert abs(v.z1 - j.z0) < EPS and v.z0 == 0 and j.y0 <= v.y0 and v.y1 <= j.y1 and j.x0 <= v.x0 and v.x1 <= j.x1, k


def test_pieces_du_meuble():
    attendu = {"joue_n", "joue_c", "joue_s", "fond", "bas", "etagere", "bac_1", "bac_2", "porte", "poignee", "plateau", "lave_linge", "tapis", "colonne"} | {f"verin_{k}{i}" for k in "ncs" for i in "01"}
    assert {b.nom for b in bas.blocs()} == attendu


def test_fond_et_etagere_vissés_entre_les_joues():
    f, e, n, c, p = _b("fond"), _b("etagere"), _b("joue_n"), _b("joue_c"), _b("plateau")
    for t in (f, e):
        assert abs(t.y0 - n.y1) < EPS and abs(t.y1 - c.y0) < EPS
    assert f.x1 == n.x1 and abs(f.z1 - p.z0) < EPS and f.z0 == bas.JZ0 > 0
    assert abs(e.x1 - f.x0) < EPS                                                  # l'étagère touche le fond


def test_bas_du_placard_hors_du_sol_entre_les_joues():
    b, f, n, c = _b("bas"), _b("fond"), _b("joue_n"), _b("joue_c")
    assert b.z0 == bas.JZ0 > 0 and abs(b.y0 - n.y1) < EPS and abs(b.y1 - c.y0) < EPS and abs(b.x1 - f.x0) < EPS
    assert b.x0 > _b("porte").x1


def test_meme_matiere_partout_sauf_le_plateau():
    for nom in ("joue_n", "joue_c", "joue_s", "fond", "bas", "etagere", "porte", "colonne"):
        assert _b(nom).role == "melamine", nom
    assert _b("plateau").role == "chene"


def test_etagere_a_mi_hauteur():
    e = _b("etagere")
    assert abs(e.z0 - _b("bas").z1 - (bas.Z_DESSOUS - e.z1)) < EPS and abs(bas.NIV_H - (e.z0 - _b("bas").z1)) < EPS


def test_bacs_au_plus_3_4_de_l_etage_et_poses():
    b1, b2, e = _b("bac_1"), _b("bac_2"), _b("etagere")
    assert abs(b1.z0 - _b("bas").z1) < EPS and b1.z0 > 0 and abs(b2.z0 - e.z1) < EPS   # le bac du bas ne pose pas au sol
    for b in (b1, b2):
        assert b.z1 - b.z0 <= 0.75 * bas.NIV_H
        assert b.y0 > _b("joue_n").y1 and b.y1 < _b("joue_c").y0 and b.x0 >= _b("porte").x1 and b.x1 <= _b("fond").x0
    assert e.x0 <= b2.x0 and b2.x1 <= e.x1                                         # le bac du haut pose entièrement sur l'étagère


def test_decoupes_en_u_a_3_4_de_chaque_etage_au_dessus_des_bacs():
    p = _b("porte")
    assert len(bas.FENETRES) == 2 and len(p.fenetres) == 2
    for (y0, y1, z0, z1), etage, bac in zip(bas.FENETRES, bas.ETAGES, ("bac_1", "bac_2")):
        assert abs(z0 - etage - 0.75 * bas.NIV_H) < EPS
        b = _b(bac)
        assert z0 >= b.z1 and b.y0 <= y0 and y1 <= b.y1                            # le linge tombe dans le bac
        assert abs(z1 - z0 - bas.FEN_H) < EPS and bas.FEN_H >= 9.9                 # plus grandes que les 7,45 refusées
    assert abs(bas.FENETRES[1][3] - p.z1) < EPS                                    # celle du haut s'ouvre sur le bord de la porte
    assert bas.FENETRES[0][3] < bas.EZ0                                            # celle du bas reste sous l'étagère
    for c, f in zip(p.fenetres, bas.FENETRES):                                     # contours dans leur découpe, fond arrondi
        assert all(f[0] - EPS <= y <= f[1] + EPS and f[2] - EPS <= z <= f[3] + EPS for y, z in c)
        assert not any(abs(y - f[0]) < EPS and abs(z - f[2]) < EPS for y, z in c)
    pts = bas.contour_porte()
    assert (bas.FEN_Y0, p.z1) in pts and (bas.FEN_Y1, p.z1) in pts                 # la porte est bien entaillée


def test_porte_en_applique_poignee_a_droite():
    p, po, n, c = _b("porte"), _b("poignee"), _b("joue_n"), _b("joue_c")
    assert abs(p.x1 + bas.JEU_PORTE - n.x0) < EPS and abs(p.x0 - bas.PX0) < EPS   # au nu du plateau
    assert p.y0 > n.y0 and p.y1 < c.y1 and p.y0 < n.y1 and p.y1 > c.y0            # couvre les chants, sans dépasser
    assert p.z1 < bas.Z_DESSOUS and p.z0 == bas.JZ0
    assert po.y0 > bas.FEN_Y1 and po.y1 < p.y1                                     # dans le montant droit, côté machine
    assert bas.FENETRES[0][3] < po.z0 and po.z1 < bas.FENETRES[1][2]               # entre les fenêtres


def test_charnieres_hors_des_fenetres_et_de_l_etagere():
    assert bas.CUV_RIVE <= bas.MONTANT
    for z in bas.CHARN_Z:
        for _, _, z0, z1 in bas.FENETRES:
            assert z + bas.CUVETTE / 2 < z0 or z - bas.CUVETTE / 2 > z1
        assert z < bas.EZ0 - 3 or z > bas.EZ1 + 3
        assert bas.PORTE_Z0 < z < bas.PORTE_Z1


def test_porte_ne_touche_pas_l_etagere_ni_les_bacs():
    assert _b("etagere").x0 > _b("joue_n").x0 and _b("bac_1").x0 > _b("porte").x1


def test_vis_entrent_assez():
    assert 4 - bas.EP >= 2      # 4 × 40 à travers la joue, dans le chant du panneau


def test_melamine_hors_de_leau():
    assert bas.JZ0 >= 2 and _b("joue_c").z0 == bas.JZ0 and _b("fond").z0 == bas.JZ0 and _b("porte").z0 == bas.JZ0 and _b("bas").z0 == bas.JZ0


def test_les_pieces_tiennent_dans_les_achats():
    assert bas.PY1 - bas.PY0 <= bas.PANNEAU_L and bas.PLATEAU_P <= bas.PANNEAU_P
    d = bas.decoupe()
    assert sorted(r for _, x in d for r, _, _ in x) == ["B", "B", "B", "C", "D", "E", "F", "G"]
    for t, x in d:
        assert sum(lg for _, lg, _ in x) + bas.TRAIT * (len(x) - 1) <= t["L"] + EPS
        assert all(la <= t["l"] + EPS for _, _, la in x)
    assert bas.VERIN["cmin"] <= bas.JZ0 <= bas.VERIN["cmax"] and bas.VERIN["perce"] + 2 * 0.5 <= bas.EP


def test_chant_suffit():
    assert bas.rouleaux_chant() * bas.CHANT["rouleau"] >= bas.chant_vu() * 1.1


def test_epaisseur_demandee():
    assert bas.EP < 4 and bas.JEU_SUD < 4.7


def test_machine_au_jeu_et_sur_tapis():
    m, t = _b("lave_linge"), _b("tapis")
    assert m.y0 - _b("joue_c").y1 >= bas.JEU_MACHINE - EPS and _b("joue_s").y0 - m.y1 >= bas.JEU_MACHINE - EPS
    assert m.z0 == t.z1 == bas.TAPIS["ep"] and bas.Z_DESSOUS - m.z1 == bas.JEU_MACHINE
    assert _b("joue_c").y1 < t.y0 and t.y1 < _b("joue_s").y0 and t.x0 >= m.x0 - 0.5
    assert M.X1 - m.x1 == bas.JEU_FOND and m.x0 == _b("joue_c").x0     # joues au nu de la façade : la porte passe


def test_plateau_60_sur_toute_la_longueur():
    p = _b("plateau")
    assert p.x1 - p.x0 == 60 and p.x1 == M.X1 and p.y0 <= 0.3 + EPS and M.Y1 - p.y1 <= 0.3 + EPS


def test_tuyaux_libres():
    x0, x1, y0, y1, z0, z1 = M.TUYAUX["zone"]
    for nom in ("joue_n", "joue_c", "joue_s", "fond", "bas", "etagere"):
        b = _b(nom)
        assert not (b.x0 < x1 and b.x1 > x0 and b.y0 < y1 and b.y1 > y0 and b.z0 < z1 and b.z1 > z0), nom
    assert _b("plateau").encoche[2] < M.ROBINET["y"] < _b("plateau").encoche[3]


def test_equerres_et_prix():
    assert bas.N_EQUERRES == 6
    attendu = 66.90 + 2 * 16.50 + 13.59 + 2 * 9.50 + 10 + 6 + 2 * 5.99 + 4 * 5.59 + 4 * 2.39 + 6 * 3.59 + 8.99 + 37.50 + 13.50 + 5.95 + 7.95 + 9.00
    assert abs(bas.total() - attendu) < 0.01
    refs = [ref for _, ref, _, _, _ in bas.prix()]
    assert bas.PANNEAU["ref"] in refs and bas.TAPIS["ref"] in refs and bas.VERIN["ref"] in refs and bas.BAC["ref"] in refs
    assert bas.CHARNIERE["ref"] in refs and bas.POIGNEE["ref"] in refs and len(set(refs)) == len(refs)


def test_colonne_en_diagonale_dans_l_angle():
    import math
    c, p = _b("colonne"), _b("plateau")
    assert abs(c.z0 - p.z1) < EPS and 0 < M.Z_HAUT - c.z1 <= 0.3         # posée sur le plateau, sous le meuble haut
    assert abs(M.X1 - c.x1 - bas.JEU_MUR) < EPS and abs(c.y0 - bas.JEU_MUR) < EPS   # à 0,3 du fond et du mur nord
    (ax, ay), (bx, by) = bas.COL_A, bas.COL_B
    assert abs(math.hypot(bx - ax, by - ay) - bas.COL_L) < EPS and abs((bx - ax) - (by - ay)) < EPS   # 45°, 18 de face
    assert bas.COL_L <= 2 * bas.COL_JAMBE
    assert len(bas.PRISES_Z) == 3 and min(bas.PRISES_Z) - bas.PRISE["plaque"] / 2 - p.z1 >= 5        # 3 prises libres, hors des éclaboussures
    assert bas.PRISE["plaque"] <= bas.COL_L and len(c.decor) == 4


def test_la_boite_tient_derriere_le_panneau():
    """Dans le triangle, la largeur disponible à la profondeur n derrière la face avant vaut COL_L - 2 n."""
    assert bas.COL_L - 2 * bas.BOITE["prof"] >= bas.BOITE["d"] + 0.4


def test_passage_du_cable():
    t, n, f = bas.COL_TROU, _b("joue_n"), _b("fond")
    assert (bas.COL_XF - t["x"]) + (t["y"] - bas.COL_YF) < bas.COL_JAMBE - bas.EP * 1.5    # le trou du plateau est caché par la colonne
    assert n.y1 < t["y"] and t["x"] < f.x0                               # et il débouche dans le placard
    e = _b("etagere")
    (x0, x1, y0, y1), = e.entailles
    assert x1 == e.x1 and y0 == e.y0 and y1 < _b("bac_1").y0              # l'entaille passe à côté des bacs
    assert not _b("bas").entailles                                       # le câble entre par la joue, au-dessus du bas
    a = bas.ARRIVEE
    assert bas.JX0 < a["x"] < bas.JX1 and bas.BZ1 < a["z"] - bas.GOUL / 2  # la sortie tombe dans la joue nord, au-dessus du bas
    assert a["z"] + bas.GOUL / 2 < bas.CHARN_Z[0] - 2.5                  # la goulotte passe sous la charnière du bas
    assert n.y1 + bas.GOUL < _b("bac_1").y0                              # et à côté du bac
    assert x0 <= bas.DX0 - bas.GOUL / 2 <= x1                            # dans l'axe de l'entaille
    assert _b("colonne").x0 > bas.LED_X                                  # le fil va bien vers le profil LED


def test_vis_de_la_colonne_accessibles_des_deux_cotes():
    """En bas : dans le placard, ni sur la joue nord ni sur le fond. En haut : ni dans la joue K1 ni dans le dos du caisson."""
    n, f = _b("joue_n"), _b("fond")
    for x, y in bas.COL_VIS:
        assert y > n.y1 and x < f.x0
        assert y > M.CH["y0"] + M.TH and x < M.CH["x1"] - M.TH
        assert bas.COL_A[0] < x < bas.COL_B[0]


def test_tenue():
    t = bas.tenue()
    assert t["fleche"] < 3 and t["marge"] > 2 and t["fleche_e"] < 2


def test_page():
    h = bas.page()
    for sec in ('id="iso"', 'id="structure"', 'id="plan"', 'id="elevation"', 'id="coupe"', 'id="mesures"', 'id="changements"', bas.VERSION, 'id="pieds"', 'id="finition"', 'id="placard"', 'id="porte"', 'id="f-placard"', 'id="f-porte"', 'id="colonne"', 'id="f-colonne"', 'id="f-colonne-dessus"'):
        assert sec in h, sec
    h2 = re.sub(r'<section id="changements">.*?</section>|<style.*?</style>|<script.*?</script>', "", h, flags=re.S)
    for ancien in ("échelle", "écharpe", "bastaing", "lambourde", "portique", "tasseau", "peindre", "perforé", "skådis"):
        assert ancien not in h2.lower(), ancien


def test_liens():
    racine = os.path.join(os.path.dirname(__file__), "..", "..")
    for lien in re.findall(r'(?:href|src)="(?!https?:|data:|#)([^"#]+)', bas.page()):
        assert os.path.exists(os.path.join(racine, lien)), lien
