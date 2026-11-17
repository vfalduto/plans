# Le modèle du meuble bas : les tests de 3d/sdb/test_bas.py (sauf ceux de l'ancienne page), puis la comparaison avec
# l'ancien générateur, tant qu'il existe.
from tests.outils import depuis_page
from pieces.sdb import ancien, piece as P
from pieces.sdb.meuble_bas import document, modele as B
from tests.sdb_anciennes import ancien as vieux, page_bas

EPS = 1e-6


def _b(nom):
    return next(b for b in B.blocs() if b.nom == nom)


def _recouvre(a, b, axes):
    return all(getattr(a, f"{k}0") < getattr(b, f"{k}1") - EPS and getattr(b, f"{k}0") < getattr(a, f"{k}1") - EPS for k in axes)


def test_rien_ne_se_traverse():
    ps = B.blocs()
    for i, a in enumerate(ps):
        for c in ps[i + 1:]:
            assert not _recouvre(a, c, "xyz"), (a.nom, c.nom)
        assert P.Y0 < a.y0 and a.y1 < P.Y1 and a.x1 <= P.X1, a.nom


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
    assert {b.nom for b in B.blocs()} == attendu


def test_fond_et_etagere_vissés_entre_les_joues():
    f, e, n, c, p = _b("fond"), _b("etagere"), _b("joue_n"), _b("joue_c"), _b("plateau")
    for t in (f, e):
        assert abs(t.y0 - n.y1) < EPS and abs(t.y1 - c.y0) < EPS
    assert f.x1 == n.x1 and abs(f.z1 - p.z0) < EPS and f.z0 == B.JZ0 > 0
    assert abs(e.x1 - f.x0) < EPS                                                  # l'étagère touche le fond


def test_bas_du_placard_hors_du_sol_entre_les_joues():
    b, f, n, c = _b("bas"), _b("fond"), _b("joue_n"), _b("joue_c")
    assert b.z0 == B.JZ0 > 0 and abs(b.y0 - n.y1) < EPS and abs(b.y1 - c.y0) < EPS and abs(b.x1 - f.x0) < EPS
    assert b.x0 > _b("porte").x1


def test_meme_matiere_partout_sauf_le_plateau():
    for nom in ("joue_n", "joue_c", "joue_s", "fond", "bas", "etagere", "porte", "colonne"):
        assert _b(nom).role == "melamine", nom
    assert _b("plateau").role == "chene"


def test_etagere_a_mi_hauteur():
    e = _b("etagere")
    assert abs(e.z0 - _b("bas").z1 - (B.Z_DESSOUS - e.z1)) < EPS and abs(B.NIV_H - (e.z0 - _b("bas").z1)) < EPS


def test_bacs_au_plus_3_4_de_l_etage_et_poses():
    b1, b2, e = _b("bac_1"), _b("bac_2"), _b("etagere")
    assert abs(b1.z0 - _b("bas").z1) < EPS and b1.z0 > 0 and abs(b2.z0 - e.z1) < EPS   # le bac du bas ne pose pas au sol
    for b in (b1, b2):
        assert b.z1 - b.z0 <= 0.75 * B.NIV_H
        assert b.y0 > _b("joue_n").y1 and b.y1 < _b("joue_c").y0 and b.x0 >= _b("porte").x1 and b.x1 <= _b("fond").x0
    assert e.x0 <= b2.x0 and b2.x1 <= e.x1                                         # le bac du haut pose entièrement sur l'étagère


def test_decoupes_en_u_a_3_4_de_chaque_etage_au_dessus_des_bacs():
    p = _b("porte")
    assert len(B.FENETRES) == 2 and len(p.fenetres) == 2
    for (y0, y1, z0, z1), etage, bac in zip(B.FENETRES, B.ETAGES, ("bac_1", "bac_2")):
        assert abs(z0 - etage - 0.75 * B.NIV_H) < EPS
        b = _b(bac)
        assert z0 >= b.z1 and b.y0 <= y0 and y1 <= b.y1                            # le linge tombe dans le bac
        assert abs(z1 - z0 - B.FEN_H) < EPS and B.FEN_H >= 9.9                 # plus grandes que les 7,45 refusées
    assert abs(B.FENETRES[1][3] - p.z1) < EPS                                    # celle du haut s'ouvre sur le bord de la porte
    assert B.FENETRES[0][3] < B.EZ0                                            # celle du bas reste sous l'étagère
    for c, f in zip(p.fenetres, B.FENETRES):                                     # contours dans leur découpe, fond arrondi
        assert all(f[0] - EPS <= y <= f[1] + EPS and f[2] - EPS <= z <= f[3] + EPS for y, z in c)
        assert not any(abs(y - f[0]) < EPS and abs(z - f[2]) < EPS for y, z in c)
    pts = B.contour_porte()
    assert (B.FEN_Y0, p.z1) in pts and (B.FEN_Y1, p.z1) in pts                 # la porte est bien entaillée


def test_porte_en_applique_poignee_a_droite():
    p, po, n, c = _b("porte"), _b("poignee"), _b("joue_n"), _b("joue_c")
    assert abs(p.x1 + B.JEU_PORTE - n.x0) < EPS and abs(p.x0 - B.PX0) < EPS   # au nu du plateau
    assert p.y0 > n.y0 and p.y1 < c.y1 and p.y0 < n.y1 and p.y1 > c.y0            # couvre les chants, sans dépasser
    assert p.z1 < B.Z_DESSOUS and p.z0 == B.JZ0
    assert po.y0 > B.FEN_Y1 and po.y1 < p.y1                                     # dans le montant droit, côté machine
    assert B.FENETRES[0][3] < po.z0 and po.z1 < B.FENETRES[1][2]               # entre les fenêtres


def test_charnieres_hors_des_fenetres_et_de_l_etagere():
    assert B.CUV_RIVE <= B.MONTANT
    for z in B.CHARN_Z:
        for _, _, z0, z1 in B.FENETRES:
            assert z + B.CUVETTE / 2 < z0 or z - B.CUVETTE / 2 > z1
        assert z < B.EZ0 - 3 or z > B.EZ1 + 3
        assert B.PORTE_Z0 < z < B.PORTE_Z1


def test_porte_ne_touche_pas_l_etagere_ni_les_bacs():
    assert _b("etagere").x0 > _b("joue_n").x0 and _b("bac_1").x0 > _b("porte").x1


def test_vis_entrent_assez():
    assert 4 - B.EP >= 2      # 4 × 40 à travers la joue, dans le chant du panneau


def test_melamine_hors_de_leau():
    assert B.JZ0 >= 2 and _b("joue_c").z0 == B.JZ0 and _b("fond").z0 == B.JZ0 and _b("porte").z0 == B.JZ0 and _b("bas").z0 == B.JZ0


def test_les_pieces_tiennent_dans_les_achats():
    assert B.PY1 - B.PY0 <= B.PANNEAU_L and B.PLATEAU_P <= B.PANNEAU_P
    d = B.decoupe()
    assert sorted(r for _, x in d for r, _, _ in x) == ["B", "B", "B", "C", "D", "E", "F", "G"]
    for t, x in d:
        assert sum(lg for _, lg, _ in x) + B.TRAIT * (len(x) - 1) <= t["L"] + EPS
        assert all(la <= t["l"] + EPS for _, _, la in x)
    assert B.VERIN["cmin"] <= B.JZ0 <= B.VERIN["cmax"] and B.VERIN["perce"] + 2 * 0.5 <= B.EP


def test_chant_suffit():
    assert B.rouleaux_chant() * B.CHANT["rouleau"] >= B.chant_vu() * 1.1


def test_epaisseur_demandee():
    assert B.EP < 4 and B.JEU_SUD < 4.7


def test_machine_au_jeu_et_sur_tapis():
    m, t = _b("lave_linge"), _b("tapis")
    assert m.y0 - _b("joue_c").y1 >= B.JEU_MACHINE - EPS and _b("joue_s").y0 - m.y1 >= B.JEU_MACHINE - EPS
    assert m.z0 == t.z1 == B.TAPIS["ep"] and B.Z_DESSOUS - m.z1 >= B.JEU_MACHINE
    assert _b("joue_c").y1 < t.y0 and t.y1 < _b("joue_s").y0 and t.x0 >= m.x0 - 0.5
    assert P.X1 - m.x1 == B.JEU_FOND and m.x0 == _b("joue_c").x0     # joues au nu de la façade : la porte passe


def test_plateau_60_sur_toute_la_longueur():
    p = _b("plateau")
    assert p.x1 - p.x0 == 60 and p.x1 == P.X1 and p.y0 <= 0.3 + EPS and P.Y1 - p.y1 <= 0.3 + EPS


def test_tuyaux_libres():
    x0, x1, y0, y1, z0, z1 = P.TUYAUX["zone"]
    for nom in ("joue_n", "joue_c", "joue_s", "fond", "bas", "etagere"):
        b = _b(nom)
        assert not (b.x0 < x1 and b.x1 > x0 and b.y0 < y1 and b.y1 > y0 and b.z0 < z1 and b.z1 > z0), nom
    assert _b("plateau").encoche[2] < P.ROBINET["y"] < _b("plateau").encoche[3]


def test_equerres_et_prix():
    assert B.N_EQUERRES == 6
    attendu = 66.90 + 2 * 16.50 + 13.59 + 2 * 9.50 + 10 + 6 + 2 * 5.99 + 4 * 5.59 + 4 * 2.39 + 6 * 3.59 + 8.99 + 37.50 + 13.50 + 5.95 + 7.95 + 9.00
    assert abs(B.total() - attendu) < 0.01
    refs = [ref for _, ref, _, _, _ in B.prix()]
    assert B.PANNEAU["ref"] in refs and B.TAPIS["ref"] in refs and B.VERIN["ref"] in refs and B.BAC["ref"] in refs
    assert B.CHARNIERE["ref"] in refs and B.POIGNEE["ref"] in refs and len(set(refs)) == len(refs)


def test_colonne_en_diagonale_dans_l_angle():
    import math
    c, p = _b("colonne"), _b("plateau")
    assert abs(c.z0 - p.z1) < EPS and 0 < B.Z_HAUT - c.z1 <= 0.3         # posée sur le plateau, sous le meuble haut
    assert abs(P.X1 - c.x1 - B.JEU_MUR) < EPS and abs(c.y0 - B.JEU_MUR) < EPS   # à 0,3 du fond et du mur nord
    (ax, ay), (bx, by) = B.COL_A, B.COL_B
    assert abs(math.hypot(bx - ax, by - ay) - B.COL_L) < EPS and abs((bx - ax) - (by - ay)) < EPS   # 45°, 18 de face
    assert B.COL_L <= 2 * B.COL_JAMBE
    assert len(B.PRISES_Z) == 3 and min(B.PRISES_Z) - B.PRISE["plaque"] / 2 - p.z1 >= 5        # 3 prises libres, hors des éclaboussures
    assert B.PRISE["plaque"] <= B.COL_L and len(c.decor) == 4


def test_la_boite_tient_derriere_le_panneau():
    """Dans le triangle, la largeur disponible à la profondeur n derrière la face avant vaut COL_L - 2 n."""
    assert B.COL_L - 2 * B.BOITE["prof"] >= B.BOITE["d"] + 0.4


def test_passage_du_cable():
    t, n, f = B.COL_TROU, _b("joue_n"), _b("fond")
    assert (B.COL_XF - t["x"]) + (t["y"] - B.COL_YF) < B.COL_JAMBE - B.EP * 1.5    # le trou du plateau est caché par la colonne
    assert n.y1 < t["y"] and t["x"] < f.x0                               # et il débouche dans le placard
    e = _b("etagere")
    (x0, x1, y0, y1), = e.entailles
    assert x1 == e.x1 and y0 == e.y0 and y1 < _b("bac_1").y0              # l'entaille passe à côté des bacs
    assert not _b("bas").entailles                                       # le câble entre par la joue, au-dessus du bas
    a = B.ARRIVEE
    assert B.JX0 < a["x"] < B.JX1 and B.BZ1 < a["z"] - B.GOUL / 2  # la sortie tombe dans la joue nord, au-dessus du bas
    assert a["z"] + B.GOUL / 2 < B.CHARN_Z[0] - 2.5                  # la goulotte passe sous la charnière du bas
    assert n.y1 + B.GOUL < _b("bac_1").y0                              # et à côté du bac
    assert x0 <= B.DX0 - B.GOUL / 2 <= x1                            # dans l'axe de l'entaille
    assert _b("colonne").x0 > B.LED_X                                  # le fil va bien vers le profil LED


def test_vis_de_la_colonne_accessibles_des_deux_cotes():
    """En bas : dans le placard, ni sur la joue nord ni sur le fond. En haut : ni dans la joue K1 ni dans le dos du caisson."""
    n, f = _b("joue_n"), _b("fond")
    for x, y in B.COL_VIS:
        assert y > n.y1 and x < f.x0
        assert y > ancien.modele().CH["y0"] + ancien.modele().TH and x < ancien.modele().CH["x1"] - ancien.modele().TH
        assert B.COL_A[0] < x < B.COL_B[0]


def test_tenue():
    t = B.tenue()
    assert t["fleche"] < 3 and t["marge"] > 2 and t["fleche_e"] < 2


def test_valeurs():
    assert round(B.total(), 2) == 296.82 and B.rouleaux_chant() == 2 and B.cm(B.chant_vu() / 100) == "7,6"
    assert (B.cm(B.NIV_H), B.cm(B.Z_DESSUS), B.cm(B.PY1 - B.PY0), B.cm(B.BAIE), B.cm(B.COL_H)) == \
           ("42,3", "92", "114,4", "47,5", "65,8")
    assert len(B.prix()) == 16
    assert sum(q for _, _, q, _, _ in B.PIECES_DEBIT) == 9


def test_donnees_copiees_de_modele_py():
    M = vieux("modele")
    assert B.PANNEAU == M.PANNEAUX["D"][0] and B.EP == M.PT and B.PLATEAU_P == M.PROF
    assert {k: M.VERNIS[k] for k in ("couches", "rendement", "pots")} == B.VERNIS


def test_lit_le_meuble_haut():
    assert (B.Z_HAUT, B.Z_HAUT1, B.LED_X, B.VERSION_HAUT) == (158, 248, 191, "V6.4")


def test_changements_comme_l_ancienne_page():
    # les seize changements de l'ancienne page à l'identique, sous la V8.6 (onglet Iso) et la V8.7 (plan à 92) ajoutées en tête
    assert document.VERSION == "V8.7" and len(document.CHANGEMENTS) == 18
    assert document.CHANGEMENTS[0][:2] == ("V8.7", "17/11/2026") and "92" in document.CHANGEMENTS[0][2]
    assert document.CHANGEMENTS[1][:2] == ("V8.6", "17/11/2026") and "Iso" in document.CHANGEMENTS[1][2]
    assert [(c.version, c.date, c.texte) for c in depuis_page(page_bas())] == [tuple(c) for c in document.CHANGEMENTS[2:]]
