"""Meubles touchables du plan de la cuisine/aménagement (pieces/cuisine/amenagement/zones.py) : ids stables, emprise et
cotes tirées des blocs du modèle, contenu des rangements dans la fiche."""
import ast
import html
import re
from pathlib import Path

import pytest

from commun.blocs import cotes_meuble
from pieces.cuisine import modele as M
from pieces.cuisine.amenagement import zones as Z

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
    assert z.emprise == (union["x0"], union["y0"], union["x1"], union["y1"])
    assert z.cotes == cotes_meuble(union)


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
