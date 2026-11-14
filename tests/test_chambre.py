import html
import math
import re
from html import escape, unescape
from html.parser import HTMLParser

import pytest

from commun import modele
from commun.appartement import APPART, contours
from commun.dessin import f
from commun.journal import depuis_page
from pieces.chambre import piece
from pieces.chambre.amenagement import dessin, document, vues
from tests.outils import RACINE, balises

ANCIENNE = (RACINE / "tests/fixtures/chambre/chambre-amenagement.html").read_text(encoding="utf-8")


def test_piece():
    assert piece.SOL == [(0, 0), (428, 0), (428, 10), (441, 10), (441, 251), (47, 251), (47, 80), (0, 80)]
    assert math.isclose(piece.SURFACE, (441 * 251 - 47 * 171 - 13 * 10) / 1e4)
    assert (piece.H, piece.POSITION, piece.CAMERAS) == (250, (364, 112, 0), ())
    assert piece.PORTE["b"] - piece.PORTE["a"] == 67


def test_cotes_de_la_page():
    D = document
    assert D.PLAN["x1"] - D.PLAN["x0"] == 42 and D.PLAN["y1"] - D.PLAN["y0"] == 241
    assert D.PLAN["y1"] - D.PLAN["y0"] == 2 * 80 + (D.NICHE["y1"] - D.NICHE["y0"]) + (D.JOUE["y1"] - D.JOUE["y0"])
    assert D.NICHE["y1"] - D.NICHE["y0"] == 79
    assert (D.LIT["x0"] - D.PLACARD["x1"], D.L - D.LIT["x1"]) == (117, 117)
    assert D.PLACARD["y1"] - D.PLACARD["y0"] - D.PLACARD["cloison"] == 164
    assert D.PLACARD["porte"][1] - D.PLACARD["porte"][0] == 155
    assert [round(math.dist(p["a"], p["b"])) for p in D.passages(D)] == [47, 117, 70, 75, 42, 7]


def test_changements_de_la_page():
    assert [(c[0], c[1], c[2]) for c in document.CHANGEMENTS] == [
        (c.version, c.date, c.texte) for c in depuis_page(ANCIENNE)]
    assert len(document.CHANGEMENTS) == 5
    # le bandeau de la page est « Chambre · V2.1 · plan et élévations » : la version n'en est pas le dernier morceau
    assert document.VERSION == re.search(r'class="kicker">[^<]*· (V[\d.]+) ·', ANCIENNE).group(1) == "V2.1"
    assert (RACINE / "site" / document.FIGEES_ANCIENNES[0][1]).is_file()


def test_accueil():
    chambre = {c.id: c for c in contours()}["chambre"]
    assert chambre.p == next(c.p for c in APPART if c.id == "chambre")
    assert chambre.cotes == "10,3 m²"


def test_barres_de_la_niche():
    # page, carte ④ : « devant à 70, derrière à 76 » ; la pièce est côté x 401, le mur à x 441
    devant, derriere = sorted(document.NICHE["barres"])
    assert devant[0] < derriere[0]
    assert (devant[1], derriere[1]) == (70, 76)


# ------------------------------------------------------------------ dessins régénérés, comparés à la page figée
class _Lecteur(HTMLParser):
    def __init__(self):
        super().__init__()
        self.suite, self.defs, self.premiere = [], 0, True

    def handle_starttag(self, tag, attrs):
        a = {k: (v if v is not None else "") for k, v in attrs}
        premiere, self.premiere = self.premiere, False
        if self.defs or tag == "defs":
            self.defs += tag == "defs"
            return
        if tag == "rect" and "zone" in a.get("class", "").split():
            return
        if premiere and tag == "svg":
            a = {"viewBox": a.get("viewbox", "")}   # HTMLParser met les noms d'attributs en minuscules
        nombres = (lambda v: re.sub(r"-?\d+(?:\.\d+)?", lambda m: f(float(m.group())), v))
        a = {k: re.sub(r"url\(#(tk|ar)-[\w-]+\)", r"url(#\1)", nombres(v)) for k, v in a.items()}
        self.suite.append((tag, tuple(sorted(a.items()))))

    def handle_startendtag(self, tag, attrs):
        if tag != "defs":
            self.handle_starttag(tag, attrs)

    def handle_endtag(self, tag):
        if self.defs and tag == "defs":
            self.defs -= 1

    def handle_data(self, data):
        if not self.defs and data.strip():
            self.suite.append(data.strip())


def _elements(svg: str) -> list[tuple]:
    """Suite des balises ouvrantes (nom, attributs) et des textes non vides, dans l'ordre du document ; nombres des
    attributs arrondis à 0,1 et écrits sans « .0 » (`244.0` = `244`) ; `<defs>` et son contenu, `rect.zone` sautés ;
    la première balise, si c'est un <svg>, réduite à son viewBox ; `url(#tk-<k>)` et `url(#ar-<k>)` lus `url(#tk)`,
    `url(#ar)`."""
    p = _Lecteur()
    p.feed(svg)
    p.close()
    return p.suite


_FIGURES = ("plan", "est", "sud", "ouest")


def _figure(nom: str) -> str:
    """Le HTML du `<div class="fig">` du dessin `nom`, tel quel."""
    figs = re.findall(r'<div class="fig">(.*?)</div><p class="cap">(.*?)</p></div>', ANCIENNE, re.S)
    assert len(figs) == len(_FIGURES)
    return figs[_FIGURES.index(nom)]


def _ecarts(s: str) -> str:
    """Les écarts voulus : rail → tringle, app → filet, mf → passm, « · » → « , », sans rect.tile."""
    noms = {"rail": "tringle", "app": "filet", "mf": "passm"}
    s = re.sub(r'class="([^"]*)"', lambda m: 'class="%s"' % " ".join(noms.get(c, c) for c in m.group(1).split()), s)
    s = re.sub(r'<rect [^>]*class="tile"[^>]*/>\s*', "", s)
    return s.replace(" · ", ", ")


def _ancien(nom: str) -> str:
    """Le SVG `plan`, `est`, `sud` ou `ouest` de la page figée (les quatre `<div class="fig">`, dans cet ordre) ou sa
    légende (`legende`), avec les écarts voulus."""
    if nom == "legende":
        (s,) = re.findall(r'<div class="legend">.*?</span></div>', ANCIENNE)
    else:
        s = re.search(r"<svg.*</svg>", _figure(nom)[0], re.S).group()
    return _ecarts(s)


def _cap(nom: str) -> str:
    """Le texte de <p class="cap"> du dessin `nom`."""
    return html.unescape(re.sub(r"<[^>]+>", "", _figure(nom)[1]))


def test_outil_de_comparaison():
    assert _elements('<svg class="x" viewBox="0 0 1 1" role="img"><defs><marker id="tk-plan"><path d="M1 2"/></marker>'
                     '</defs><rect class="zone" x="1"/><text x="244.0" y="3">a <tspan>b</tspan></text>'
                     '<path marker-end="url(#tk-plan)"/></svg>') == [
        ("svg", (("viewBox", "0 0 1 1"),)), ("text", (("x", "244"), ("y", "3"))), "a", ("tspan", ()), "b",
        ("path", (("marker-end", "url(#tk)"),))]
    assert "tringle" in _ancien("plan") and 'class="rail"' not in _ancien("plan") and "·" not in _ancien("plan")
    assert all(_ancien(n).startswith("<svg") for n in _FIGURES)


def test_plan_regenere():
    assert _elements(dessin.plan_svg(document)) == _elements(_ancien("plan"))


def test_legende_reprise():
    assert _elements(dessin.legende()) == _elements(_ancien("legende"))


def test_plan_alt():
    assert dessin.ALTS["plan"] == _cap("plan")
    (svg,) = balises(dessin.plan_svg(document, aria=dessin.ALTS["plan"]), "svg")
    assert svg["aria-label"] == dessin.ALTS["plan"] and svg["role"] == "img"
    (svg,) = balises(dessin.plan_svg(document, zones='<rect class="zone"/>'), "svg")
    assert svg["role"] == "group"


@pytest.mark.parametrize("meuble,bord,valeur,attendus", [
    ("CHEVET_EST", "x1", 362, (">33 × 35<", ">4<")),        # chevet est élargi de 3 : étiquette et passage « 7 »
    ("LIT", "y0", 50, ("Lit 160 × 197", ">50<")),            # lit raccourci : étiquette et passage du pied
    ("PLAN", "x0", 396, ("Plan 241 × 45", ">72<"))])         # plan plus profond : étiquette et passage lit → plan
def test_plan_suit_le_modele(monkeypatch, meuble, bord, valeur, attendus):
    monkeypatch.setattr(document, meuble, {**getattr(document, meuble), bord: valeur})
    svg = re.sub(r"<tspan[^>]*>[^<]*</tspan>\s*", "", dessin.plan_svg(document))
    for attendu in attendus:
        assert attendu in svg


def test_calques_du_plan():
    svg = dessin.plan_svg(document)
    assert {c["class"] for c in balises(svg, "circle") if c.get("r") == "1.3"} == {"passm"}
    assert not balises(svg, "rect", classe="tile") and "·" not in svg


def test_css_du_plan():
    classes = {c for n in ("svg", "rect", "line", "path", "circle", "text", "tspan")
               for b in balises(dessin.plan_svg(document) + dessin.legende(), n) for c in b.get("class", "").split()}
    regles = set(re.findall(r"\.([\w-]+)", dessin.CSS))
    assert classes - {"plan", "legend"} <= regles
    assert not re.search(r"font-family|Archivo|Mono|monospace|cook2|prefers-color-scheme", dessin.CSS)
    assert not re.search(r"#[0-9A-Fa-f]{3,8}\b|var\(--", dessin.plan_svg(document) + dessin.legende())


@pytest.mark.parametrize("k", ["est", "sud", "ouest"])
def test_elevation_regeneree(k):
    _, dessiner = dessin.ELEVATIONS[k]
    assert _elements(dessiner(document)) == _elements(_ancien(k))
    assert dessin.ALTS[k] == _cap(k)


def test_elevations_dans_l_ordre():
    assert [(k, nom) for k, (nom, _) in dessin.ELEVATIONS.items()] == [
        ("est", "Mur est"), ("sud", "Mur sud"), ("ouest", "Mur ouest")]


def test_elevations_suivent_le_modele(monkeypatch):
    monkeypatch.setattr(document, "PATERES", {**document.PATERES, "z": 170})
    assert "3 patères h 170" in dessin.elevation_est(document)
    monkeypatch.setattr(document, "CHEVET_OUEST", {**document.CHEVET_OUEST, "z1": 65})
    assert ">② h 65<" in re.sub(r"<tspan[^>]*>|</tspan>", "", dessin.elevation_sud(document))


@pytest.mark.parametrize("k", ["est", "sud", "ouest"])
def test_elevation_svg(k):
    _, dessiner = dessin.ELEVATIONS[k]
    (svg,) = balises(dessiner(document), "svg")
    assert (svg["class"], svg["role"], svg["aria-label"]) == ("coupe", "img", dessin.ALTS[k])
    (svg,) = balises(dessiner(document, aria="Mur"), "svg")
    assert svg["aria-label"] == "Mur"
    assert "·" not in dessiner(document)


def test_css_des_elevations():
    svgs = "".join(d(document) for _, d in dessin.ELEVATIONS.values())
    classes = {c for n in ("svg", "rect", "line", "path", "circle", "text", "tspan")
               for b in balises(svgs, n) for c in b.get("class", "").split()}
    assert classes - {"coupe"} <= set(re.findall(r"\.([\w-]+)", dessin.CSS))
    assert not re.search(r"font-family|Archivo|Mono|monospace|cook2|prefers-color-scheme", dessin.CSS)
    assert not re.search(r"#[0-9A-Fa-f]{3,8}\b|var\(--", svgs)


def test_marqueurs_definis_dans_chaque_dessin():
    dessins = {"plan": dessin.plan_svg(document), **{k: d(document) for k, (_, d) in dessin.ELEVATIONS.items()}}
    vus = set()
    for k, svg in dessins.items():
        refs = set(re.findall(r"url\(#([\w-]+)\)", svg))
        assert refs <= set(re.findall(r'\bid="([\w-]+)"', svg)), k
        assert all(r.endswith("-" + k) for r in refs), k
        vus |= refs
    assert vus >= {"tk-plan", "ar-plan", "tk-est", "ar-est", "tk-sud"}   # l'élévation ouest n'a ni cote ni flèche


# ------------------------------------------------------------------ vues et document
V = lambda: vues.vues("")

def test_document():
    d = document.DOCUMENT
    assert (d.piece, d.id, d.nom, d.type) == ("chambre", "amenagement", "Aménagement", "amenagement")
    (var,) = d.variantes
    assert (var.id, var.version, len(var.changements), var.figees) == ("", "V2.1", 5, document.FIGEES_ANCIENNES)
    modele.verifier(d, d.generer(""))
    assert list(V()) == list(modele.VUES["amenagement"])

def test_zones_confrontees_a_leur_meuble():
    """Chaque zone : l'emprise de son meuble, sauf les bords qu'elle déclare ; sa fiche commence par sa longueur."""
    (e,) = V()["plan"].elements
    rects = balises(e.scene, "rect", classe="zone")
    assert [r["data-meuble"] for r in rects] == ["lit", "chevet_ouest", "chevet_est", "commodes", "niche"]
    for r, z in zip(rects, document.ZONES, strict=True):
        m = getattr(document, z["meuble"])
        x, y, l, h = (float(r[a]) for a in ("x", "y", "width", "height"))
        assert (x, y, x + l, y + h) == tuple(z.get(c, m[c]) for c in ("x0", "y0", "x1", "y1"))
        cotes = re.search(rf'<template data-meuble="{z["id"]}"[^>]*><p class="cotes">([^<]*)</p>', e.fiche)[1]
        assert unescape(cotes).startswith(f'{max(m["x1"] - m["x0"], m["y1"] - m["y0"]):g} × ')

def test_zone_suit_son_meuble(monkeypatch):
    monkeypatch.setattr(document, "CHEVET_EST", {**document.CHEVET_EST, "x0": 319})
    (e,) = V()["plan"].elements
    assert balises(e.scene, "rect", classe="zone", **{"data-meuble": "chevet_est"})[0]["width"] == "40"

def test_coupes():
    v = V()["coupes"]
    assert [(e.k, e.nom) for e in v.elements] == [("est", "Mur est"), ("sud", "Mur sud"), ("ouest", "Mur ouest")]
    assert [t["data-k"] for t in balises(v.fiche, "line", classe="sec")] == ["est", "sud", "ouest"]
    assert "Position" in v.fiche and v.outils == ("zoom", "mesure")
    for e in v.elements:
        assert balises(e.scene, "svg")[0]["aria-label"] == dessin.ALTS[e.k]

def test_iso_et_camera_grisees():
    for cle in ("iso", "camera"):
        assert V()[cle].elements == [] and V()[cle].vide == "Pas encore rendu"

def test_explication_reprend_la_page():
    (e,) = V()["explication"].elements
    cartes = re.findall(r'<div class="card"><h3>(.*?)</h3><p>(.*?)</p></div>', ANCIENNE)
    assert vues.PRINCIPES == cartes and len(cartes) == 6
    assert vues.POINTS == re.findall(r"<li>(.*?)</li>", ANCIENNE.split('<div class="hyp">')[1].split("</ul>")[0])
    assert len(vues.POINTS) == 7
    pitch = re.search(r'<p class="pitch">(.*?)</p>', ANCIENNE)[1]
    attendu = (pitch.replace('href="#verifier"', 'href="#explication"')
               .replace("L'historique est en fin de document (<a href=\"#changements\">",
                        "L'historique est sur sa propre page (<a href=\"historique.html\">"))
    assert vues.CHAPO == attendu
    assert e.scene.count("Montrer sur le plan") == 5
    for valeur, libelle in (("241 × 42", "plan sur 2 commodes, h 85"), ("3 + 6", "patères + pantalons"),
                            ("75", "entre le lit et le plan (cm)"), ("47", "passage au pied du lit (cm)")):
        assert valeur in e.scene and libelle in e.scene

def test_liens_internes():
    for cle, v in V().items():
        for e in v.elements:
            for a in balises(e.scene + e.fiche + v.fiche, "a"):
                assert a["href"].startswith("#") or a["href"] == "historique.html", (cle, a["href"])

def test_aucun_interdit():
    tout = "".join(v.fiche + e.scene + e.fiche for v in V().values() for e in v.elements)
    for interdit in ("·", 'type="checkbox"', "Copier la liste", "À venir", "Lecture du plan", "Lecture de la coupe"):
        assert interdit not in tout
    visible = re.sub(r'aria-label="[^"]*"', "", tout)
    for texte in dessin.ALTS.values():
        assert escape(texte, quote=True) not in visible and texte not in visible

def test_ids_uniques_et_classes_du_site():
    tout = "".join(v.fiche + e.scene + e.fiche for v in V().values() for e in v.elements)
    ids = re.findall(r'\bid="([^"]+)"', tout)
    assert len(ids) == len(set(ids)), sorted(i for i in ids if ids.count(i) > 1)
    classes = {c for m in re.findall(r'class="([^"]+)"', tout) for c in m.split()}
    assert not classes & {"app", "rail", "barre", "contenu", "vue", "scene", "fiche"}

@pytest.mark.parametrize("cle", ["plan", "coupes"])
def test_chaque_classe_a_sa_regle(cle):
    """Chaque classe d'un dessin et de la légende a une règle dans dessins.css (filtré comme à la construction),
    sauf `zone` (site.css) ; une règle de site.css qui ne fait que masquer un calque ne compte pas."""
    from commun.construction import _dessins
    from commun.css_dessins import css_dessins
    css = css_dessins(document.DOCUMENT.css, _dessins(V()), ".d-chambre")
    v = V()[cle]
    # l'intérieur de chaque <svg> de scène, et la légende de la fiche (le reste de la fiche est au gabarit et aux blocs)
    morceaux = [e.scene.split(">", 1)[1] for e in v.elements] + re.findall(r'<div class="legend">.*?</div>', v.fiche, re.S)
    for html in morceaux:
        classes = {c for m in re.findall(r'class="([^"]+)"', html) for c in m.split()} - {"zone"}
        assert sorted(c for c in classes if not re.search(rf"\.{re.escape(c)}(?![\w-])", css)) == []

def test_css_sur_les_jetons_du_site():
    jetons = set(re.findall(r"(--[\w-]+):", (RACINE / "commun/site.css").read_text(encoding="utf-8")))
    assert set(re.findall(r"var\((--[\w-]+)\)", dessin.CSS)) <= jetons
    for interdit in ("font-family", "monospace", "Archivo", "JetBrains", "prefers-color-scheme", "--cook2"):
        assert interdit not in dessin.CSS


def test_trait_de_position_visible():
    """Le trait du mur regardé, dans le mini-plan « Position » des coupes, n'a de couleur que par dessins.css
    (site.css ne règle que son opacité) : sans règle `.sec`, il ne se voit pas."""
    from commun.construction import _dessins
    from commun.css_dessins import css_dessins
    css = css_dessins(document.DOCUMENT.css, _dessins(V()), ".d-chambre")
    assert re.search(r"\.sec\{[^}]*\bstroke:", css)
