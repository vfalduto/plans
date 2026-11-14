"""Document de la cuisine/aménagement (pieces/cuisine/amenagement/document.py, vues.py) : les cinq vues et leurs
éléments, textes alternatifs repris des légendes, 90 changements, versions figées, page construite, et chaque section
de l'ancienne page à sa destination (tableau de contenu du plan)."""
import html
import json
import re

import pytest

from commun import modele
from commun.construction import _dessins, construire
from commun.css_dessins import css_dessins
from commun.journal import entrees
from commun.modele import Piece, Site
from pieces.cuisine import modele as M, piece
from pieces.cuisine.amenagement import dessins, document, legende, vues
from pieces.cuisine.amenagement import zones as Z
from tests.cuisine_anciens import FIXTURES
from tests.outils import RACINE, balises

DOC = document.construire_document()
VUES = DOC.generer("")
LEGENDES = json.loads((FIXTURES / "legendes.json").read_text(encoding="utf-8"))
TABLEAUX = json.loads((FIXTURES / "tableaux.json").read_text(encoding="utf-8"))
RENDUS = {"iso": ("iso", "so"), "iso_nuit": ("iso", "so-nuit"), "iso_no": ("iso", "no"),
          "entree": ("camera", "entree"), "fenetre": ("camera", "fenetre"), "banquette": ("camera", "banquette"),
          "dos_cellier": ("camera", "dos_cellier"), "cellier": ("camera", "cellier")}
DESSINS = {"coupe-a": ("coupes", "A"), "coupe-b": ("coupes", "B"), "coupe-c": ("coupes", "C"),
           "plan-elec": ("plan", "elec"), "elevation-elec": ("coupes", "elec")}


def _texte(fragment):
    """Texte d'un fragment, espaces réduites ; l'espace entre deux balises ne compte pas."""
    fragment = re.sub(r">\s+<", "><", fragment)
    return re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", "", fragment))).strip()


def _norm(fragment):
    return _texte(fragment).replace(" · ", ", ")


def _reference(cle):
    """Texte de la légende de référence `cle`, médian et tiret de titre remplacés par une virgule (celle de la coupe
    A garde le texte de ses pastilles : 856 caractères)."""
    return _norm(LEGENDES[cle]).replace(" — ", ", ")


def _element(vue, k):
    return next(e for e in VUES[vue].elements if e.k == k)


def _vue_texte(vue):
    v = VUES[vue]
    return _texte(v.fiche + "".join(e.scene + e.fiche for e in v.elements))


def test_vues_et_elements():
    assert list(VUES) == ["plan", "coupes", "iso", "camera", "explication"]
    assert [e.k for e in VUES["plan"].elements] == ["", "elec"]
    assert [(e.nom, e.titre) for e in VUES["plan"].elements][1] == ("Électricité", "Plan électrique")
    assert [e.k for e in VUES["coupes"].elements] == ["A", "B", "C", "elec"]
    assert [e.k for e in VUES["iso"].elements] == ["no", "ne", "so", "se", "so-nuit"]
    actifs = {e.k: e.actif for e in VUES["iso"].elements}
    assert actifs == {"no": True, "ne": False, "so": True, "se": False, "so-nuit": True}
    nuit = _element("iso", "so-nuit")
    assert (nuit.nom, nuit.titre) == ("SO nuit", "Vue iso SO, de nuit")
    assert [g["data-k"] for g in balises(VUES["iso"].fiche, "g", classe="pdv")] == ["no", "so", "so-nuit"]
    assert [e.k for e in VUES["camera"].elements] == ["entree", "fenetre", "banquette", "dos_cellier", "cellier"]
    assert VUES["explication"].elements
    modele.verifier(DOC, VUES)


def test_cone_de_nuit_au_coin_so():
    """Le cône `so-nuit` de « Position » est celui du coin SO (même point de vue, même visée), pas celui d'un autre."""
    fiche = VUES["iso"].fiche
    cone = {k: re.search(rf'<g class="pdv" data-k="{k}">(.*?)</g>', fiche).group(1) for k in ("no", "so", "so-nuit")}
    assert cone["so-nuit"] == cone["so"] != cone["no"]


def test_document():
    assert (DOC.piece, DOC.id, DOC.nom, DOC.type) == ("cuisine", "amenagement", "Aménagement", "amenagement")
    (v,) = DOC.variantes
    assert (v.id, v.nom, v.version) == ("", "Principale", "V13.30")
    assert DOC.css == dessins.CSS_DESSINS
    assert document.DOCUMENT.variantes == DOC.variantes   # exposé à la bascule (tâche 11)


def test_traits_et_fiches_des_coupes():
    xs = [x for x, _ in piece.SOL_ET_CELLIER]
    ys = [y for _, y in piece.SOL_ET_CELLIER]
    traits = {t["data-k"]: t for t in balises(VUES["coupes"].fiche, "line", classe="sec")}
    assert list(traits) == ["A", "B", "C", "elec"]
    fiches = {e.k: e.fiche for e in VUES["coupes"].elements}
    assert fiches == {"A": dessins.REGLE_LEGENDE, "B": "", "C": dessins.REGLE_LEGENDE, "elec": ""}
    assert vues.TRAITS == {"A": ((min(xs), dessins.COUPE_A), (max(xs), dessins.COUPE_A)),
                           "B": ((min(xs), dessins.COUPE_B), (max(xs), dessins.COUPE_B)),
                           "C": ((dessins.COUPE_C, min(ys)), (dessins.COUPE_C, max(ys))),
                           "elec": ((min(xs), dessins.COUPE_A), (max(xs), dessins.COUPE_A))}


def test_ids_de_zones_distincts_des_elements():
    ids = {z.id for z in Z.zones(legende.textes_par_meuble())}
    assert ids and not ids & {e.k for e in VUES["plan"].elements}
    assert len(balises(_element("plan", "").scene, "rect", classe="zone")) == len(ids)


def test_alt_est_la_legende():
    for cle, (vue, k) in DESSINS.items():
        (svg,) = balises(_element(vue, k).scene, "svg")[:1]
        assert svg["aria-label"] == _reference(cle), cle
    for cle, (vue, k) in RENDUS.items():
        (img,) = balises(_element(vue, k).scene, "img")
        assert img["alt"] == _reference(f"rendu-{cle}"), cle
        assert "·" not in img["alt"]
    plan = balises(_element("plan", "").scene, "svg")[0]["aria-label"]
    assert plan == "Plan vu de dessus, pièce vide, 6 meubles bas et 5 meubles hauts de 60 au mur nord"


def test_changements():
    (v,) = DOC.variantes
    assert len(v.changements) == 90 and v.changements[0].version == "V13.30"
    reference = re.findall(r'<tr><td class="mono">([^<]+)</td>', TABLEAUX["changements"])
    assert [c.version for c in v.changements] == reference
    # un changement est de l'histoire : texte d'origine, seul le point médian devient une virgule
    for c, (_, _, origine) in zip(v.changements, M.CHANGEMENTS, strict=True):
        assert c.texte == origine.replace(" · ", ", "), c.version
        assert "·" not in c.texte
    assert v.changements[0].texte.endswith("Lien dans le sommaire : #hauteur-du-plan-de-travail-etude.")


def test_figees():
    (v,) = DOC.variantes
    assert v.figees == document.FIGEES == (("V11.49", "archive/cuisine-v11.49.html"),
                                           ("V12.7", "archive/cuisine-v12.7.html"))
    for _, chemin in v.figees:
        assert (RACINE / "site" / chemin).exists(), chemin


def test_journal_compte():
    site = Site((Piece("cuisine", "Cuisine", (DOC,)),))
    lignes = [e for e in entrees(site, RACINE) if (e.piece, e.document) == ("Cuisine", "Aménagement")]
    assert len(lignes) == 90
    assert all(e.variante is None for e in lignes)


@pytest.mark.parametrize("vue", ["plan", "coupes", "explication"])
def test_dessins_styles(vue):
    """Chaque classe d'un élément (scène et fiche) a une règle dans dessins.css (filtré comme à la construction) ou
    site.css ; sauf les simples repères sans style : `trp-lbl` (étiquettes derrière la porte du cellier, coupe C),
    `vt` (groupe d'une porte, plan) et `regle` (règle d'une taille, coupes A et C), dont les options montrent
    l'état choisi par `data-si`."""
    css = css_dessins(DOC.css, _dessins(VUES), ".d-cuisine")
    site_css = (RACINE / "commun/site.css").read_text(encoding="utf-8")

    def regle(c, feuille):
        return re.search(rf"\.{re.escape(c)}(?![\w-])", feuille) is not None

    for e in VUES[vue].elements:
        interieur = e.scene.split(">", 1)[1] + e.fiche
        classes = {c for m in re.findall(r'class="([^"]+)"', interieur) for c in m.split()} - {"trp-lbl", "vt", "regle"}
        assert classes, (vue, e.k)
        assert sorted(c for c in classes if not regle(c, css) and not regle(c, site_css)) == [], (vue, e.k)
    if vue == "coupes":
        assert re.search(r"\.d-cuisine \.leg \.sw\{", css)


def test_rendus_existants():
    from commun.blocs import rendu
    for cle in ("iso_so", "iso_so_nuit", "iso_no", "entree", "fenetre", "banquette", "dos_cellier", "cellier"):
        assert rendu(vues.RENDUS_SITE, "", cle).existe, cle


@pytest.fixture(scope="module")
def construit(tmp_path_factory):
    tmp = tmp_path_factory.mktemp("cuisine")
    construire(Site((Piece("cuisine", "Cuisine", (DOC,)),)), (), tmp, tmp / "site")
    dossier = tmp / "site" / "cuisine" / "amenagement"
    return ((dossier / "index.html").read_text(encoding="utf-8"),
            (dossier / "historique.html").read_text(encoding="utf-8"))


def test_page_construite(construit):
    page, historique = construit
    assert "Touchez un meuble pour afficher sa fiche." in page
    assert 'type="checkbox"' not in page and "·" not in page
    assert 'id="c-comp"' not in page
    assert "archive/cuisine-v11.49.html" in historique and "archive/cuisine-v12.7.html" in historique
    assert "·" not in historique


def test_tableau_de_contenu(construit):
    """Chaque légende et chaque tableau de l'ancienne page à sa destination (colonne « Devient »)."""
    _, historique = construit
    explication = _vue_texte("explication")
    # légende du plan : conventions dans la fiche du plan, le reste dans les cartes de l'Explication
    for m in legende.morceaux():
        lieu = _texte(VUES["plan"].fiche) if m.ou == "legende" else explication
        assert _texte(m.html) in lieu, m.titre
    for cle, (vue, k) in DESSINS.items():
        assert balises(_element(vue, k).scene, "svg")[0]["aria-label"] == _reference(cle), cle
    (aria,) = re.findall(r'<svg[^>]*aria-label="([^"]*)"', VUES["explication"].elements[0].scene)
    assert html.unescape(aria) == _norm(LEGENDES["hauteur-pt"])
    for cle in ("hauteur-pt-etude", "interrupteurs", "nfc", "rendus-methode", "materiaux", "contenu", "capacite"):
        assert _norm(LEGENDES[cle]) in explication, cle
    for cle, (vue, k) in RENDUS.items():
        assert balises(_element(vue, k).scene, "img")[0]["alt"] == _reference(f"rendu-{cle}"), cle
    vus = {"plan", "hauteur-pt"} | set(DESSINS) | {f"rendu-{c}" for c in RENDUS} | {
        "hauteur-pt-etude", "interrupteurs", "nfc", "rendus-methode", "materiaux", "contenu", "capacite"}
    assert vus == set(LEGENDES) and len(LEGENDES) == 22
    # tableaux : huit dans l'Explication, les changements dans l'historique
    assert len(TABLEAUX) == 9
    for cle, table in TABLEAUX.items():
        if cle == "changements":
            continue
        if cle == "materiaux":
            table = re.search(r"<tbody>.*</tbody>", table, re.S).group()
        assert _norm(table) in explication, cle
    texte_historique = _texte(historique)
    for ligne in re.findall(r"<tr>(.*?)</tr>", TABLEAUX["changements"].split("<tbody>")[1], re.S):
        version, _, texte = re.findall(r"<td[^>]*>(.*?)</td>", ligne, re.S)
        attendu = _norm(texte)
        assert attendu in texte_historique, version


def test_classes_du_gabarit_absentes():
    """Aucune classe de mise en page du site (commun/site.css) dans les scènes, fiches et lectures : la fiche Tango,
    `<table class="fiche">`, devenait à 390 px le panneau du bas (`.fiche{position:absolute}`) et la page débordait."""
    tout = "".join(v.fiche + e.scene + e.fiche for v in VUES.values() for e in v.elements)
    classes = {c for m in re.findall(r'class="([^"]+)"', tout) for c in m.split()}
    assert not classes & {"app", "rail", "barre", "contenu", "vue", "scene", "fiche", "element", "lecture"}
    assert not re.search(r"(^|[}\s,])\.fiche[\s{.:]", DOC.css)
