"""Données du salon (pieces/salon/) : chaque constante reprise est celle des anciens générateurs de 3d/salon/.

Les anciens modules sont chargés par leur chemin, à part : 3d/salon/commun.py porte le nom du paquet commun/ de la
racine, et 3d/salon/ s'importe par sys.path (`import modele as M`). Ces tests tombent avec la bascule des pages, qui
suppriment les anciens générateurs : chaque page retire alors les comparaisons qui la concernent.
"""
import ast
import dataclasses
import importlib
import importlib.util
import math
import sys
from types import SimpleNamespace

import pytest

from commun.journal import depuis_page
from commun.modele import Camera
from pieces.salon import meubles, piece
from pieces.salon.amenagement import document as amenagement
from pieces.salon.enfilade import document as enfilade
from pieces.salon.enfilade import volumes as vol_enfilade
from pieces.salon.etageres import document as etageres
from pieces.salon.etageres import volumes as vol_etageres
from tests.outils import RACINE

ANCIEN = RACINE / "3d" / "salon"
_NOMS = ("commun", "modele", "plan", "etageres", "enfilade")
_cache = {}


def ancien(nom):
    """Module `nom` de 3d/salon/, importé comme le font les anciens générateurs, sans toucher aux modules du site."""
    if not _cache:
        gardes = {n: sys.modules.pop(n) for n in _NOMS if n in sys.modules}
        sys.path.insert(0, str(ANCIEN))
        try:
            for n in _NOMS:
                _cache[n] = importlib.import_module(n)
        finally:
            sys.path.remove(str(ANCIEN))
            for n in _NOMS:
                sys.modules.pop(n, None)
            sys.modules.update(gardes)
    return _cache[nom]


def norm(v):
    """Valeur comparable d'un module à l'autre : dataclasses (Bloc, Cyl, Piece) par nom de classe et champs."""
    if dataclasses.is_dataclass(v) and not isinstance(v, type):
        champs = {k: norm(getattr(v, k)) for k in ("etiq", "contenu") if hasattr(v, k)}
        champs.update({c.name: norm(getattr(v, c.name)) for c in dataclasses.fields(v)})
        return (type(v).__name__, champs)
    if isinstance(v, SimpleNamespace):
        return norm(vars(v))
    if isinstance(v, dict):
        return {k: norm(x) for k, x in v.items()}
    if isinstance(v, (list, tuple)):
        return [norm(x) for x in v]
    if callable(v):
        return ("fonction", v.__name__)
    return v


# ------------------------------------------------------------------ correspondance des noms
# ancien nom dans 3d/salon/modele.py → (module neuf, nom neuf)
MODELE = {
    "H": (piece, "H"), "L": (piece, "L"), "P": (piece, "P"), "EP": (piece, "EP"),
    "PASSAGE": (piece, "PASSAGE"), "COFFRE": (piece, "COFFRE"), "POUTRE": (piece, "POUTRE"),
    "DECROCHE": (piece, "DECROCHE"), "BAIE": (piece, "BAIE"), "CLIM": (piece, "CLIM"),
    "ENVELOPPE": (piece, "ENVELOPPE"),
    "VERSION": (amenagement, "VERSION"), "CHANGEMENTS": (amenagement, "CHANGEMENTS"),
    "CARRELAGE": (amenagement, "CARRELAGE"), "MURS": (amenagement, "FINITION_MURS"),
    "PAPIER_PEINT": (amenagement, "PAPIER_PEINT"), "MEUBLES": (amenagement, "MEUBLES"),
    "ENFILADE": (enfilade, "ENFILADE"), "_MODULES": (enfilade, "MODULES"),
    "VOLUME_ENFILADE": (enfilade, "VOLUME_ENFILADE"),
    "MONTANTS": (etageres, "MONTANTS"), "ETAGERES": (etageres, "ETAGERES"), "TABLETTES": (etageres, "TABLETTES"),
    "NIVEAUX": (etageres, "NIVEAUX"), "DISPOSITIONS": (etageres, "DISPOSITIONS"),
    "METRES_ETAGERES": (etageres, "METRES_ETAGERES"), "CHEVILLES": (etageres, "CHEVILLES"),
    "ENTAILLES": (etageres, "ENTAILLES"), "CHARGE_LIVRES": (etageres, "CHARGE_LIVRES"),
    "ETUDE_MONTANTS": (etageres, "ETUDE_MONTANTS"),
}
for _nom in ("ALLEE_ENFILADE", "CANAPE", "DESSERTE", "PLATINE", "CM_VINYLES", "VINYLES", "CONSOLE", "ECRAN",
             "PROJECTEUR", "TABLE", "CONFIGS", "CHAISE", "CHAISES", "CHAISES_PLIANTES", "PAS_CHAISES", "SUSPENSION",
             "TABLE_BASSE", "DYVLINGE", "CHILIENNE", "DECO", "TAPIS", "LAMPADAIRE", "CADRES", "RIDEAU", "PISTES_DECO",
             "DEGAGEMENTS", "TABLES_REPLIABLES", "RENDUS"):
    MODELE[_nom] = (amenagement, _nom)

# ancien nom dans 3d/salon/etageres.py → nom dans pieces/salon/etageres/document.py
ETAGERES = {n: n for n in ("VERSION", "DATE", "RA_COTE", "PANNEAU", "TASSEAU", "ROND", "KERF", "KERF_METAL",
                           "DRESSAGE", "RECHANGE_CHEVILLES", "L_MONTANT", "BANDE", "N_VIS", "COEF", "KG_M",
                           "KG_MONTANT", "MAGASINS", "SURF_PEINT", "MATERIAUX", "TN", "R_ACIER", "R_MONTANT", "R_FLEX",
                           "A_JOUE", "R_JOUE", "ARR", "P_RUINE", "P_CALCUL", "SOURCES_TENUE")}

# ancien nom dans 3d/salon/enfilade.py → nom dans pieces/salon/enfilade/document.py
ENFILADE = {n: n for n in ("VERSION", "DATE", "RELEVE", "L", "NORD", "P", "Z1", "ZP", "EP", "MODULES", "N", "FAC",
                           "TAMPON", "DOS", "PC", "JEU", "BORD", "TRAV", "TRAIT", "COULISSE", "EP_COUL", "H_BOITE",
                           "CALE_BOITE", "PROF_ETAGERE", "CHARNIERE", "PIEDS_X", "DESSUS", "VINYLE", "MAGASINS",
                           "ORDRE_MAG", "LM_PT", "LM_HDF", "LM_PIED", "LM_CP", "LM_MC", "LM_PT25", "LM_T20", "CASTO_PT",
                           "CASTO_PT26", "REF_COUL", "REF_HUILE", "FORMATS", "MELAMINE", "OUTILLAGE", "VARIANTES",
                           "HUILE", "CHANT", "RETENUE", "PREFIXE", "GROUPES", "STOCKHOLM", "IKEA_FR", "METOD_RELEVE",
                           "LM_PT26", "METOD_CAISSON", "KNIV", "SOCLE", "POUSSOIRS", "ANTI", "METOD", "JEU_METOD",
                           "PIECES_METOD", "METOD_MIXTE", "VRENA", "METOD_PLAN_LM", "NOIRS")}
ENFILADE["ETAGERES"] = "ETAGERES_CAISSONS"


@pytest.mark.parametrize("ancien_nom", sorted(MODELE))
def test_constantes_du_modele(ancien_nom):
    module, nom = MODELE[ancien_nom]
    assert norm(getattr(module, nom)) == norm(getattr(ancien("modele"), ancien_nom))


def test_modele_entierement_repris():
    """Toute constante publique de modele.py a sa place dans le paquet du salon."""
    publiques = {n for n, v in vars(ancien("modele")).items()
                 if n.isupper() or n == "_MODULES"} - {"Bloc", "Cyl"}
    assert publiques == set(MODELE)


def test_fonctions_du_modele():
    M = ancien("modele")
    for args in ((100, 200, 45, "f", 0), (296, 180, -90, "o", 3)):
        assert norm(amenagement.chaise_blocs(*args)) == norm(M.chaise_blocs(*args))
    assert amenagement._chaises_table(90, 12) == M._chaises_table(90, 12)


@pytest.mark.parametrize("ancien_nom", sorted(ETAGERES))
def test_constantes_des_etageres(ancien_nom):
    assert norm(getattr(etageres, ETAGERES[ancien_nom])) == norm(getattr(ancien("etageres"), ancien_nom))


def test_presentoir():
    PR = ancien("etageres").PR
    assert etageres.PRESENTOIR == {k: PR[k] for k in etageres.PRESENTOIR}


@pytest.mark.parametrize("ancien_nom", sorted(ENFILADE))
def test_constantes_de_l_enfilade(ancien_nom):
    assert norm(getattr(enfilade, ENFILADE[ancien_nom])) == norm(getattr(ancien("enfilade"), ancien_nom))


def test_quincaillerie_de_l_enfilade():
    """QUINC porte des quantités en fonctions : même texte, mêmes quantités pour des comptes quelconques."""
    QUINC = ancien("enfilade").QUINC
    comptes = dict(portes=4, tiroirs=3, pieds=8, facades=7, etageres=3, jonctions=2, caissons=3, chene_m2=6.4)
    assert len(enfilade.QUINC) == len(QUINC)
    for neuf, vieux in zip(enfilade.QUINC, QUINC):
        assert {k: v for k, v in neuf.items() if k != "q"} == {k: v for k, v in vieux.items() if k != "q"}
        assert neuf["q"](comptes) == vieux["q"](comptes)


def test_emprises_une_seule_source():
    """Le plan du salon prend l'enfilade et les étagères dans leur document, bloc pour bloc."""
    n_en, n_et = len(enfilade.BLOCS), len(etageres.BLOCS)
    assert amenagement.MEUBLES[:n_en] == enfilade.BLOCS
    assert amenagement.MEUBLES[n_en:n_en + n_et] == etageres.BLOCS
    assert amenagement.ENFILADE is enfilade.ENFILADE and amenagement.ETAGERES is etageres.ETAGERES


# ------------------------------------------------------------------ pièce
def test_piece():
    assert (piece.ID, piece.NOM) == ("salon", "Salon")
    assert piece.SOL[0] == (0, 0) and len(piece.SOL) == 8
    assert math.isclose(piece.SURFACE, (547 * 367 - 131 * 10 - 32 * 17) / 1e4)
    assert piece.MURS == [b for b in piece.ENVELOPPE if b.role == "mur"]
    assert piece.PORTES[0]["a"] == ancien("modele").PASSAGE["y0"]
    assert piece.FENETRES[0]["b"] == ancien("modele").BAIE["y1"]


def test_contour_de_l_accueil_inchange():
    """Posé par POSITION, le sol du salon est le contour que l'accueil dessinait jusqu'ici (APPART)."""
    from commun import appartement
    avant = next(c for c in appartement.APPART if c.id == "salon")
    apres = next(c for c in appartement.contours() if c.id == "salon")
    assert apres.p == avant.p


# ------------------------------------------------------------------ caméras
def _vues_du_rendu(nom):
    """VIEWS et ses motifs de coupe, lus dans le source (le script importe bpy)."""
    arbre = ast.parse((ANCIEN / nom).read_text(encoding="utf-8"))
    garde = []
    for n in arbre.body:
        if isinstance(n, ast.Assign):
            t = n.targets[0]
            cible = t.value.id if isinstance(t, ast.Subscript) else getattr(t, "id", "")
            if cible in ("VIEWS", "COUPES_ISO", "COUPES_ISO_NO"):
                garde.append(n)
    ns = {}
    exec(compile(ast.Module(garde, []), nom, "exec"), ns)
    return ns["VIEWS"]


def _comme_vue(c: Camera):
    v = dict(loc=c.loc, target=c.cible)
    if c.ortho:
        v["ortho"] = c.ortho
    if c.focale:
        v["lens"] = c.focale
    return v


def test_cameras_de_la_piece():
    vues = _vues_du_rendu("rendu.py")
    cams = {c.id: c for c in piece.CAMERAS}
    assert set(cams) == {k for k, v in vues.items() if "essence" not in v}
    for k, v in vues.items():
        c = cams[k.removesuffix("_noyer")]
        assert v == {**_comme_vue(c), "coupes": c.reglages["coupes"], **({"essence": "noyer"} if "essence" in v else {})}


@pytest.mark.parametrize("module,meuble", [(etageres, "etageres"), (enfilade, "enfilade")])
def test_cameras_des_meubles(module, meuble):
    vues = {k.removeprefix(meuble + "-"): v for k, v in _vues_du_rendu("rendu_meubles.py").items()
            if k.startswith(meuble + "-")}
    assert {c.id: {**_comme_vue(c), **c.reglages} for c in module.CAMERAS} == vues


@pytest.mark.parametrize("module,meuble", [(etageres, "etageres"), (enfilade, "enfilade")])
def test_rendus_des_meubles(module, meuble):
    import inspect
    source = inspect.getsource(ancien(meuble).section_rendus)
    assert [c.id for c in module.CAMERAS] == [k for k, _ in module.RENDUS]
    for k, texte in module.RENDUS:
        assert f'("{k}", "{texte}")' in source


# ------------------------------------------------------------------ changements et versions
def test_changements_de_l_amenagement():
    assert len(amenagement.CHANGEMENTS) == len(ancien("modele").CHANGEMENTS) == 28
    html = ancien("plan").contenu()
    assert len(depuis_page(html)) == len(amenagement.CHANGEMENTS)


@pytest.mark.parametrize("module,page", [(etageres, lambda: ancien("etageres").page()),
                                         (enfilade, lambda: ancien("enfilade").page()[0])])
def test_changements_des_meubles(module, page):
    """Mêmes entrées que le tableau de l'ancienne page, texte compris (du plus récent au plus ancien)."""
    lus = depuis_page(page())
    assert len(module.CHANGEMENTS) == len(lus)
    assert sorted(module.CHANGEMENTS) == sorted((c.version, c.date, c.texte) for c in lus)
    assert module.CHANGEMENTS[0][0] == module.VERSION


def test_versions_figees_dans_archive():
    for version, chemin in amenagement.FIGEES_ANCIENNES:
        html = (RACINE / chemin).read_text(encoding="utf-8")
        assert f"Salon · {version} ·" in html


# ------------------------------------------------------------------ calculs partagés et volumes 3D
def _pieces(ps):
    return [norm(p)[1] for p in ps]


@pytest.mark.parametrize("cle", [d["cle"] for d in etageres.DISPOSITIONS])
def test_volumes_des_etageres(cle):
    ET = ancien("etageres")
    e = next(x for x in ET.DISPOS if x.cle == cle)
    assert _pieces(vol_etageres.pieces_3d(cle)) == _pieces(ET.pieces_3d(e))
    assert [{k: v for k, v in t.items() if k not in ("libres",)} for t in vol_etageres.tablettes(
        vol_etageres.disposition(cle))] == [{k: v for k, v in t.items() if k != "libres"} for t in e.ts]


def test_volumes_des_etageres_par_defaut_et_detail():
    ET = ancien("etageres")
    assert _pieces(vol_etageres.pieces_3d()) == _pieces(ET.pieces_3d())
    assert _pieces(vol_etageres.pieces_detail()) == _pieces(ET.pieces_detail())


@pytest.mark.parametrize("ouvert", [False, True])
def test_volumes_de_l_enfilade(ouvert):
    EN = ancien("enfilade")
    ps = vol_enfilade.pieces_3d(ouvert=ouvert)
    assert _pieces(ps) == _pieces(EN.pieces_3d(ouvert=ouvert))
    assert vol_enfilade.chevauchements(ps) == []


def test_geometrie_de_l_enfilade():
    EN = ancien("enfilade")
    assert vol_enfilade.G == EN.G
    for ep in (1.8, 3.6):
        assert vol_enfilade.geometrie(ep) == EN.geometrie(ep)
    assert vol_enfilade.controle() == EN.controle()


def test_calculs_partages():
    C = ancien("commun")
    assert meubles.MATIERES == C.MATIERES
    for v in (0, 1.25, 8.8, 240, 60.84):
        assert (meubles.f(v), meubles.virg(v), meubles.virg(v, 2)) == (C.f(v), C.virg(v), C.virg(v, 2))
    vieux = ancien("etageres").pieces_3d() + ancien("enfilade").pieces_3d(ouvert=True)
    neufs = vol_etageres.pieces_3d() + vol_enfilade.pieces_3d(ouvert=True)
    assert [p.nom for p in meubles.ordre(neufs)] == [p.nom for p in C._ordre(vieux)]
    for pn, pv in zip(neufs[:60], vieux[:60]):
        for face in "xyz":
            assert meubles.aretes(pn, face, neufs) == C._aretes(pv, face, vieux)


# ------------------------------------------------------------------ dessins de référence (tests/fixtures/salon/)
FIXTURES = RACINE / "tests" / "fixtures" / "salon"


def test_dessins_de_reference_a_jour():
    """Les fichiers de référence sont les dessins que produisent aujourd'hui les anciens générateurs, tous."""
    import json
    spec = importlib.util.spec_from_file_location("extraire_salon", FIXTURES / "extraire.py")
    ex = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(ex)
    pages = {"salon-v4.html": ancien("plan").page(ancien("plan").lire_figees()),
             "salon-etageres.html": ancien("etageres").page(), "salon-enfilade.html": ancien("enfilade").page()[0]}
    index = json.loads((FIXTURES / "index.json").read_text(encoding="utf-8"))
    assert sorted(index) == sorted(p.name for p in FIXTURES.glob("*.svg"))
    for page, html in pages.items():
        lus = [svg for svg, _ in ex.dessins(html)]
        miens = sorted((d["rang"], nom) for nom, d in index.items() if d["page"] == page)
        assert len(lus) == len(miens) == html.count("<svg ")
        for rang, nom in miens:
            assert (FIXTURES / nom).read_text(encoding="utf-8") == lus[rang], nom
    assert (FIXTURES / "amenagement-plan-du-salon.svg").read_text(encoding="utf-8") == ancien("plan").plan_svg()


# ------------------------------------------------------------------ dessin partagé (pieces/salon/dessin.py)
from pieces.salon import dessin  # noqa: E402


@pytest.mark.parametrize("d", etageres.DISPOSITIONS, ids=lambda d: d["cle"])
def test_iso_des_etageres_comme_la_page(d):
    svg = dessin.iso_svg(vol_etageres.pieces_3d(d), f"Étagères, vue iso, disposition {d['nom']}")
    nom = f"etageres-etageres-vue-iso-disposition-{d['cle']}-{d['cle']}.svg"
    assert svg == (FIXTURES / nom).read_text(encoding="utf-8")


def test_iso_detail_et_enfilade_comme_la_page():
    temoins = {
        "etageres-etageres-detail-d-une-entaille-en-vue-iso.svg": dessin.iso_svg(
            vol_etageres.pieces_detail(), "Étagères, détail d'une entaille en vue iso", echelle=11,
            style="max-width:420px;display:block;margin:0 auto"),
        "enfilade-enfilade-fermee-vue-iso.svg": dessin.iso_svg(vol_enfilade.pieces_3d(), "Enfilade fermée, vue iso"),
        "enfilade-enfilade-ouverte-vue-iso.svg": dessin.iso_svg(vol_enfilade.pieces_3d(ouvert=True),
                                                                 "Enfilade ouverte, vue iso"),
    }
    for nom, svg in temoins.items():
        assert svg == (FIXTURES / nom).read_text(encoding="utf-8"), nom


def test_iso_et_rond_comme_l_ancien():
    C = ancien("commun")
    vieux, neufs = ancien("etageres").pieces_3d(), vol_etageres.pieces_3d()
    assert dessin.iso_svg(neufs, "t", legende="légende") == C.iso_svg(vieux, "t", legende="légende")
    P = lambda x, y, z: (x - y, x + y - z)  # noqa: E731
    for pn, pv in zip(neufs, vieux):
        if pn.forme == "cyl_y":
            assert dessin._rond_y(pn, P, "#111", "#222") == C._rond_y(pv, P, "#111", "#222")


def test_aides_svg_comme_l_ancien():
    """Entrées tirées des dessins (coupes du salon, élévations des meubles) : mêmes chaînes que plan.py."""
    PL = ancien("plan")
    for v in (0, 2.5, 8.8, 60.84, 247.6, -275, 1 / 3):
        assert (dessin.f(v), dessin.virg(v), dessin.virg(v, 2)) == (PL.f(v), PL.virg(v), PL.virg(v, 2))
    assert dessin.rect(0, -80, 60, -15, "cab") == PL.rect(0, -80, 60, -15, "cab")
    assert dessin.rect(296, 160, 426, 225, "tbl c-f", 50) == PL.rect(296, 160, 426, 225, "tbl c-f", 50)
    assert dessin.text(10, 20, "vantail nord", "lblx muted") == PL.text(10, 20, "vantail nord", "lblx muted")
    assert dessin.text(4, 8, "< & >", "lbls muted", "start") == PL.text(4, 8, "< & >", "lbls muted", "start")
    for args in ((8.8, 248.8, 18, "enfilade 240"), (0, 60, 18), (120, 318, -90, None, 4)):
        assert dessin.cote_h(*args) == PL.cote_h(*args)
        assert dessin.cote_v(*args) == PL.cote_v(*args)
