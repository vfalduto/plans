"""Meubles touchables du plan de la cuisine/aménagement (pieces/cuisine/amenagement/zones.py) : ids stables, emprise et
cotes tirées des blocs du modèle, contenu des rangements dans la fiche."""
import ast
import html
import re
from pathlib import Path

import pytest

from commun.blocs import cotes_meuble
from pieces.cuisine import modele as M, piece as P
from pieces.cuisine.amenagement import dessins as D, zones as Z

IDS = [m[0] for m in Z.MEUBLES_PLAN]
# lignes de CONTENU sans meuble sur le plan : elles vont à l'Explication (tâche 8)
SANS_ZONE = ["Salle de bains"]


def _blocs(motif):
    return [b for b in M.MEUBLES + M.ENVELOPPE if re.fullmatch(motif, b.nom)]


def test_ids_stables():
    attendus = ([f"b{i}" for i in range(1, 7)] + [f"h{i}" for i in range(1, 6)]
                + ["c1", "c2", "etageres", "banquette", "table", "chaise", "etagere-banquette", "rayonnage-nord",
                   "entretien", "balais", "seau", "aspirateur", "porte-cellier", "porte-entree", "tableau-noir"])
    assert IDS == attendus
    assert len(set(IDS)) == len(IDS)
    for i in IDS:
        assert re.fullmatch(r"[a-z][a-z0-9-]*", i), i
        assert not i.isdigit() and i not in ("", "elec")
    for _, titre, _, coupe, iso in Z.MEUBLES_PLAN:
        assert titre and coupe in ("A", "B", "C") and iso in ("so", "no"), titre


@pytest.mark.parametrize("id_", IDS)
def test_zone_confrontee_a_son_meuble(id_):
    motif = next(m[2] for m in Z.MEUBLES_PLAN if m[0] == id_)
    blocs = _blocs(motif)
    assert blocs, id_
    union = {c: (min if c.endswith("0") else max)(getattr(b, c) for b in blocs)
             for c in ("x0", "x1", "y0", "y1", "z0", "z1")}
    assert Z.emprise(motif) == union
    z = next(z for z in Z.zones({}) if z.id == id_)
    x0, y0, x1, y1 = union["x0"], union["y0"], union["x1"], union["y1"]
    # un meuble accroché au-dessus d'un autre : la moitié côté mur (nord ou sud) ; les autres : l'emprise entière
    attendu = {"n": (x0, y0, x1, (y0 + y1) / 2), "s": (x0, (y0 + y1) / 2, x1, y1)}.get(MURAUX.get(id_), (x0, y0, x1, y1))
    assert z.emprise == attendu
    assert z.cotes == cotes_meuble(union)


MURAUX = {**{f"h{i}": "n" for i in range(1, 6)}, "etageres": "n", "etagere-banquette": "s"}


def test_muraux_au_mur():
    """La bande murale est bien côté mur : y 0 (nu du mur nord), y 252 (nu du mur sud, face de la porte d'entrée)."""
    sud = next(p["face"] for p in P.PORTES if p["mur"] == "s")
    for id_, mur in MURAUX.items():
        e = Z.emprise(next(m[2] for m in Z.MEUBLES_PLAN if m[0] == id_))
        assert (e["y0"] == 0) if mur == "n" else (e["y1"] == sud), id_


def test_zones_reprennent_meubles_plan():
    zs = Z.zones({"b3": "Texte <b>de la page</b>."})
    assert [(z.id, z.titre, z.coupe, z.iso) for z in zs] == [(i, t, c, s) for i, t, _, c, s in Z.MEUBLES_PLAN]
    b3 = next(z for z in zs if z.id == "b3")
    assert b3.texte.startswith("Texte <b>de la page</b>.")


def test_titres_tires_des_etiquettes():
    titres = dict((m[0], m[1]) for m in Z.MEUBLES_PLAN)
    for b in M.MEUBLES:
        if getattr(b, "etiq", "") and b.nom.startswith("caisson_"):
            code, _, reste = b.etiq.partition(" ")
            assert titres[code.lower()].startswith(f"{code}, "), b.etiq
            if reste:
                assert titres[code.lower()] == f"{code}, {reste}"


def test_zone_suit_son_meuble(monkeypatch):
    motif = next(m[2] for m in Z.MEUBLES_PLAN if m[0] == "b3")
    avant = next(z for z in Z.zones({}) if z.id == "b3")
    caisson = next(b for b in M.MEUBLES if b.nom == "caisson_b3")
    monkeypatch.setattr(caisson, "x1", caisson.x1 + 10)
    assert Z.emprise(motif)["x1"] == caisson.x1
    apres = next(z for z in Z.zones({}) if z.id == "b3")
    assert apres.emprise[2] == avant.emprise[2] + 10
    assert apres.cotes != avant.cotes


def test_contenu_dans_la_fiche():
    textes = {z.id: z.texte for z in Z.zones({})}
    perdues = []
    for meuble, contenu in M.CONTENU:
        ligne = f"{html.escape(meuble)} : {html.escape(contenu)}"
        porteurs = [i for i, t in textes.items() if ligne in t]
        assert len(porteurs) <= 1, (meuble, porteurs)
        if not porteurs:
            perdues.append(meuble)
    assert perdues == SANS_ZONE


def test_cotes_sans_nombre_en_dur():
    # chaînes de MEUBLES_PLAN, des titres génériques et des libellés de CONTENU : aucun chiffre (les motifs disent
    # « \d », pas un chiffre)
    arbre = ast.parse(Path(Z.__file__).read_text(encoding="utf-8"))
    noeuds = [n for n in arbre.body if isinstance(n, ast.Assign)
              and {getattr(c, "id", "") for c in n.targets} & {"MEUBLES_PLAN", "_CONTENU_DE"}]
    assert len(noeuds) == 2
    chaines = [n.value for a in noeuds for n in ast.walk(a) if isinstance(n, ast.Constant) and isinstance(n.value, str)]
    assert len(chaines) > len(Z.MEUBLES_PLAN)
    for c in chaines:
        assert not re.search(r"[0-9]", c), c
    # les chiffres d'un titre viennent de l'étiquette du modèle
    codes = {b.etiq.partition(" ")[0] for b in M.MEUBLES if getattr(b, "etiq", "")}
    for _, titre, _, _, _ in Z.MEUBLES_PLAN:
        reste = titre
        for code in codes:
            reste = reste.replace(code, "")
        assert not re.search(r"\d", reste), titre


# ------------------------------------------------------------------ « Coupe » et « Iso » de la fiche montrent le meuble
# coupe : plan et regard, comme dessins.coupe_a/b/c ; un bloc y est s'il est au-delà du plan dans le sens du regard
# (le critère `vu` de dessins.coupe_svg)
COUPES = {"A": (D.COUPE_A, "nord"), "B": (D.COUPE_B, "sud"), "C": (D.COUPE_C, "est")}
ISOS = {"so": "iso_so", "no": "iso_no"}   # k de la vue Iso → caméra


def _dans_la_coupe(b, lettre):
    cut, regard = COUPES[lettre]
    axe, sens, _ = D.REGARDS[regard]
    _, _, d0, d1 = D.uv(b, axe)
    return d1 > cut if sens > 0 else d0 < cut


@pytest.mark.parametrize("id_, motif, coupe, iso", [(m[0], m[2], m[3], m[4]) for m in Z.MEUBLES_PLAN])
def test_coupe_et_iso_montrent_le_meuble(id_, motif, coupe, iso):
    blocs = _blocs(motif)
    assert any(_dans_la_coupe(b, coupe) for b in blocs), f"{id_} : absent de la coupe {coupe}"
    camera = next(c for c in P.CAMERAS if c.id == ISOS[iso])
    retires = re.compile(camera.reglages["coupes"])
    # nom de l'objet dans le glb : <rôle>__<nom> (cad.py)
    assert any(not retires.match(f"{b.role}__{b.nom}") for b in blocs), f"{id_} : retiré du rendu {camera.id}"


def test_coupe_et_iso_peuvent_echouer():
    """Le critère voit l'erreur de l'inventaire : le tableau noir (mur sud) n'est ni dans la coupe A ni dans l'iso SO."""
    blocs = _blocs(r"tableau_noir|zone_aimantee")
    assert not any(_dans_la_coupe(b, "A") for b in blocs)
    retires = re.compile(next(c for c in P.CAMERAS if c.id == "iso_so").reglages["coupes"])
    assert all(retires.match(f"{b.role}__{b.nom}") for b in blocs)


# ------------------------------------------------------------------ chaque zone garde une surface touchable propre
# Les zones sont écrites dans l'ordre de la liste : une zone écrite après une autre la recouvre. On échantillonne le
# plan tous les PAS cm (centres de cases) et l'on garde, pour chaque zone, les cases de son rectangle qu'aucune zone
# écrite après elle ne couvre.
# Seuils : au moins la moitié de l'emprise du meuble (son dessin est d'abord le sien), et un carré libre de COTE cm, ou
# de la plus petite dimension du meuble s'il est plus mince (tableau noir, porte du cellier : leurs zones minces sont
# un autre sujet). 10 cm : ce qui reste de l'étagère de l'entretien à l'est des balais, le plus petit des meubles
# épais ; le plan (viewBox de 590 cm) est à environ 1,9 px/cm à 1440 px, soit une vingtaine de pixels, une cible de
# souris ou de stylet ; à 390 px (0,6 px/cm), il faut zoomer, comme pour lire les cotes.
PAS, PART, COTE = 0.5, 0.5, 10


def _cases(r):
    x0, y0, x1, y1 = r
    i0, i1 = round(x0 / PAS + 0.5 - 1e-9), round(x1 / PAS - 0.5 + 1e-9)
    j0, j1 = round(y0 / PAS + 0.5 - 1e-9), round(y1 / PAS - 0.5 + 1e-9)
    return {(i, j) for i in range(int(i0) - 1, int(i1) + 2) for j in range(int(j0) - 1, int(j1) + 2)
            if x0 <= (i + 0.5) * PAS <= x1 and y0 <= (j + 0.5) * PAS <= y1}


def _plus_grand_carre(cases):
    """Côté, en cases, du plus grand carré de cases libres."""
    meilleur, cote = 0, {}
    for i, j in sorted(cases):
        c = 1 + min(cote.get((i - 1, j), 0), cote.get((i, j - 1), 0), cote.get((i - 1, j - 1), 0))
        cote[(i, j)] = c
        meilleur = max(meilleur, c)
    return meilleur


def surfaces_libres(zs):
    """Par id : (part libre de l'emprise du meuble, côté du plus grand carré libre en cm)."""
    emprises = {m[0]: Z.emprise(m[2]) for m in Z.MEUBLES_PLAN}
    sortie = {}
    for k, z in enumerate(zs):
        libres = _cases(z.emprise)
        for autre in zs[k + 1:]:
            libres -= _cases(autre.emprise)
        e = emprises[z.id]
        sortie[z.id] = (len(libres) / max(1, len(_cases((e["x0"], e["y0"], e["x1"], e["y1"])))),
                        _plus_grand_carre(libres) * PAS)
    return sortie


def test_chaque_zone_garde_une_surface_touchable():
    zs = Z.zones({})
    assert not any(z.si for z in zs)   # une zone par état d'une option : à prendre en compte ici
    emprises = {m[0]: Z.emprise(m[2]) for m in Z.MEUBLES_PLAN}
    trop_peu = {}
    for id_, (part, carre) in surfaces_libres(zs).items():
        e = emprises[id_]
        cote = min(COTE, e["x1"] - e["x0"], e["y1"] - e["y0"])
        # une rangée de cases de tolérance : B6 (P39,6) sous la demi-zone de H5 (19,8) garde exactement la moitié
        if part < PART - PAS / (e["y1"] - e["y0"]) or carre < cote - PAS:
            trop_peu[id_] = (round(part, 2), carre)
    assert trop_peu == {}


def test_recouvrement_vu():
    """Le critère voit un recouvrement : sous la zone pleine de H5, B6 (même profondeur depuis V13.31) disparaîtrait."""
    zs = [z for z in Z.zones({}) if z.id in ("b6", "h5")]
    b6, h5 = zs
    plein = Z.emprise(next(m[2] for m in Z.MEUBLES_PLAN if m[0] == "h5"))
    h5 = type(h5)(**{**h5.__dict__, "emprise": (plein["x0"], plein["y0"], plein["x1"], plein["y1"])})
    part, carre = surfaces_libres([b6, h5])["b6"]
    assert part < PART and carre == 0
