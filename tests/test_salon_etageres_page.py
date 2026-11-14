"""Salon, étagères : la page du document salon/etageres (calculs, dessins, vues, document), comparée à l'ancienne
page V1.8 figée (tests/fixtures/salon/salon-etageres.html) et aux dessins de référence (tests/fixtures/salon/)."""
import hashlib
import json
import math
import re
import subprocess
from html import escape, unescape
from html.parser import HTMLParser

import pytest

from commun import modele
from commun.blocs import euros, total_achats
from commun.journal import depuis_page, entrees
from pieces.salon.etageres import calculs, dessins, document, vues
from tests.outils import RACINE, balises, charger_site
from tests.test_redirections import _traduire

ANCIENNE = (RACINE / "tests/fixtures/salon/salon-etageres.html").read_text(encoding="utf-8")
INDEX = json.loads((RACINE / "tests/fixtures/salon/index.json").read_text(encoding="utf-8"))


# ------------------------------------------------------------------ outils
_EN_LIGNE = re.compile(r"</?(?:b|i|em|strong|span|a|small)(?:\s[^>]*)?>")


def _texte(html: str) -> str:
    """Balises remplacées par une espace (celles d'un mot dans la ligne, `b`, `span`, `a`… : ôtées, « <b>rainure</b>. »
    se lit « rainure. »), entités décodées, blancs réduits à une espace, bords ôtés."""
    sans = re.sub(r"<[^>]+>", " ", _EN_LIGNE.sub("", html))
    return re.sub(r"\s+", " ", unescape(sans)).strip()


class _Dv(HTMLParser):
    """Blocs <div class="dv" data-d="…"> d'un fragment, par la profondeur des div : (clé, début, début de l'intérieur,
    fin de l'intérieur, fin), en positions dans le fragment."""

    def __init__(self, source):
        super().__init__(convert_charrefs=False)
        self.source, self.profondeur, self.ouvert, self.blocs = source, 0, None, []
        self.lignes = [0]
        for ligne in source.splitlines(keepends=True):
            self.lignes.append(self.lignes[-1] + len(ligne))

    def _pos(self):
        ligne, col = self.getpos()
        return self.lignes[ligne - 1] + col

    def handle_starttag(self, tag, attrs):
        if tag != "div":
            return
        self.profondeur += 1
        a = dict(attrs)
        if self.ouvert is None and a.get("class") == "dv":
            debut = self._pos()
            self.ouvert = (self.profondeur, a["data-d"], debut, debut + len(self.get_starttag_text()))

    def handle_endtag(self, tag):
        if tag != "div":
            return
        if self.ouvert is not None and self.profondeur == self.ouvert[0]:
            fin = self._pos()
            self.blocs.append((self.ouvert[1], self.ouvert[2], self.ouvert[3], fin, fin + len("</div>")))
            self.ouvert = None
        self.profondeur -= 1


def _dv(html: str) -> list[tuple[str, int, int, int, int]]:
    p = _Dv(html)
    p.feed(html)
    p.close()
    return p.blocs


def _blocs(cle: str) -> list[str]:
    """HTML intérieur des sept <div class="dv" data-d="cle"> de la page figée, dans l'ordre : chapô, vue iso, le
    meuble, débit, fixation, achats, point « Composition »."""
    corps = ANCIENNE[ANCIENNE.index("<body"):]
    blocs = [corps[a:b] for c, _, a, b, _ in _dv(corps) if c == cle]
    assert len(blocs) == 7, (cle, len(blocs))
    return blocs


def _dispo(html: str, cle: str) -> str:
    """`html` dans la version de la disposition `cle` : les blocs des autres dispositions ôtés, celui de `cle` gardé
    sans son enveloppe."""
    out, i = [], 0
    for c, d, a, b, fin in _dv(html):
        out.append(html[i:d])
        if c == cle:
            out.append(html[a:b])
        i = fin
    return "".join(out) + html[i:]


def _section(ident: str) -> str:
    """HTML de la page figée depuis <h2 id="ident"> jusqu'au <h2 suivant (ou à la note finale, ou à <section)."""
    debut = ANCIENNE.index(f'<h2 id="{ident}"')
    fins = [i for i in (ANCIENNE.find(m, debut + 1) for m in ("<h2", '<p class="note">Repère', "<section"))
            if i >= 0]
    return ANCIENNE[debut:min(fins)]


def _lignes(html: str) -> list[list[str]]:
    """Cellules (`_texte` de chaque td) de chaque <tr> d'un tableau, en-têtes exclus."""
    out = []
    for tr in re.findall(r"<tr[^>]*>(.*?)</tr>", html, re.S):
        tds = re.findall(r"<td[^>]*>(.*?)</td>", tr, re.S)
        if tds:
            out.append([_texte(td) for td in tds])
    return out


# ------------------------------------------------------------------ tâche 1 : calculs d'une disposition
VALEURS = {   # relevées en exécutant l'ancien générateur (V1.8)
    "actuelle": ("1 × 244 + 1 × 189 + 2 × 134 + 1 × 79", 5, 4, 7.8, (4, 122, 222), 34, 3, 2, 393.28, 365.28, 28.0, 27, 67, 6, 44, 2),
    "rangs": ("4 × 134 + 4 × 79", 8, 2, 8.52, (4, 122, 222), 40, 4, 2, 402.28, 374.28, 28.0, 27, 67, 4, 53, 1),
    "decalee": ("4 × 134 + 4 × 79", 8, 2, 8.52, (8, 122, 222), 40, 4, 2, 402.28, 374.28, 28.0, 22, 57, 4, 53, 1),
    "escalier": ("2 × 134 + 8 × 79", 10, 2, 9.0, (8, 122, 207), 44, 4, 2, 402.28, 374.28, 28.0, 27, 42, 4, 59, 3),
}  # kit, tablettes, tailles, mètres, niveaux (n, bas, haut), chevilles, ronds, plans, total, relevé, estimé,
   # libre min, libre max, repères du débit, pièces à débiter, rang du montant le plus chargé (M3, M2, M2, M4)


@pytest.mark.parametrize("cle", calculs.CLES)
def test_etat(cle):
    e = calculs.etat(cle)
    (kit, nt, tailles, metres, niv, chev, ronds, plans, total, rel, est, lmin, lmax, reps, nb, m) = VALEURS[cle]
    assert (e.kit, len(e.ts), e.n_tailles, len(e.panneaux), e.chevilles, e.n_ronds) == (kit, nt, tailles, plans, chev, ronds)
    assert math.isclose(e.metres, metres) and (len(e.niveaux), e.niveaux[0], e.niveaux[-1]) == niv
    assert (e.total, e.releve, e.estime, round(e.libre_min), round(e.libre_max), e.ch["m"]) == (total, rel, est, lmin, lmax, m)
    ps = calculs.pieces(e)
    assert (len(ps), sum(p["n"] for p in ps)) == (reps, nb)


def test_constantes():
    assert (calculs.FACTEUR, calculs.N_TASSEAUX, calculs.PAR_TASSEAU) == (1.25, 3, 2)
    assert calculs.CLES == ("actuelle", "rangs", "decalee", "escalier")
    with pytest.raises(ValueError, match="niche"):
        calculs.etat("niche")


@pytest.mark.parametrize("cle", calculs.CLES)
def test_tableaux_de_la_page(cle):
    """Liste des pièces, achats et composition : les cellules de l'ancienne page, calculées ici."""
    e = calculs.etat(cle)
    _, _, meuble, debit, _, achats, _ = _blocs(cle)
    assert [[p["rep"], p["nom"], str(p["n"]), p["dims"], p["matiere"], p["de"]] for p in calculs.pieces(e)] == _lignes(debit.split("<h3>")[0])
    *anciens, total = _lignes(achats)       # colonnes de ET:783-785 ; la dernière ligne est le total
    assert len(anciens) == len(e.achats)
    for r, a in zip(anciens, e.achats):
        # Poste, Article (+ note), Réf., Qté, Prix unit., Total, Source, Prix
        assert r == [a["poste"], _texte(escape(a["article"]) + calculs.note_achat(a)), a["ref"], str(a["qte"]),
                     calculs.prix(a["pu"]), calculs.prix(a["total"]), calculs.nom_magasin(a), a["statut"]]
    assert total[:2] == [f"Total TTC (disposition {e.nom})", calculs.prix(e.total)]


# ------------------------------------------------------------------ tâche 2 : dessins
def _reference(k: str, cle: str) -> tuple[str, int]:
    """(SVG de référence, rang dans la page) du dessin `k` de la disposition `cle` (index.json : label, disposition ;
    `disposition` vide pour un dessin commun)."""
    e = calculs.etat(cle)
    labels = {"mini": f"Disposition {e.nom}", "iso": f"Étagères, vue iso, disposition {e.nom}",
              "detail": "Étagères, détail d'une entaille en vue iso",
              "elevation": f"Élévation du mur ouest, disposition {e.nom}",
              "dessus": f"Étagères vues de dessus, disposition {e.nom}",
              "profil": "Profil d'une tablette entaillée et de ses deux chevilles", "travee": "Une travée vue de face",
              "presentoir": "Présentoir penché vers la pièce, profil",
              "refente": "Plan de découpe des plans de travail en chêne", "barres": "Débit des tasseaux et des ronds",
              "percage": "Plan de perçage d'un montant", "entaille": "Entaille d'une tablette"}
    (nom, d), = [(n, d) for n, d in INDEX.items() if d["page"] == "salon-etageres.html" and d["label"] == labels[k]
                 and d["disposition"] in ("", cle)]
    return (RACINE / "tests/fixtures/salon" / nom).read_text(encoding="utf-8"), d["rang"]


def _legende(rang: int) -> str:
    """`_texte` du premier <p class="cap"> qui suit le `rang`-ième « <svg » de la page figée."""
    debut = [m.start() for m in re.finditer("<svg", ANCIENNE)][rang]
    return _texte(re.search(r'<p class="cap">(.*?)</p>', ANCIENNE[debut:], re.S)[1])


def _sans_aria(svg: str) -> str:
    return re.sub(r' aria-label="[^"]*"', "", svg, count=1)


COMMUNS = {"detail", "profil", "travee", "presentoir", "percage", "entaille"}
CAS = [(k, c) for k in dessins.DESSINS for c in calculs.CLES if k not in COMMUNS or c == "actuelle"]


def test_trente_dessins_de_reference():
    assert len(CAS) == len({_reference(k, c)[1] for k, c in CAS}) == 30


@pytest.mark.parametrize("k,cle", CAS)
def test_dessin_repris(k, cle):
    ref, _ = _reference(k, cle)
    assert _sans_aria(dessins.DESSINS[k](calculs.etat(cle))) == _sans_aria(ref.replace(" · ", ", "))


@pytest.mark.parametrize("k,cle", CAS)
def test_aria_par_defaut(k, cle):
    """Sans `aria`, l'ancien `aria-label`, tel que l'ancienne page l'écrivait."""
    ref, _ = _reference(k, cle)
    assert dessins.DESSINS[k](calculs.etat(cle)) == ref.replace(" · ", ", ")


def test_virgules_au_lieu_des_points_medians():
    vus = {_reference(k, c)[1]: _reference(k, c)[0] for k, c in CAS}.values()   # les 30 fichiers, par rang
    etiquettes = [t for svg in vus for t in re.findall(r"<text[^>]*>([^<]*·[^<]*)</text>", svg)]
    assert len(etiquettes) == 125
    nouveaux = "".join(dessins.DESSINS[k](calculs.etat(c)) for k, c in CAS)
    assert "·" not in nouveaux
    for t in etiquettes:
        assert f">{t.replace(' · ', ', ')}<" in nouveaux


@pytest.mark.parametrize("k,cle", [(k, c) for k, c in CAS if k != "mini"])
def test_legende_devient_texte_alternatif(k, cle):
    e = calculs.etat(cle)
    _, rang = _reference(k, cle)
    assert dessins.legendes(e)[k] == _legende(rang)
    (svg,) = balises(dessins.DESSINS[k](e, aria=dessins.legendes(e)[k]), "svg")[:1]
    assert svg["aria-label"] == dessins.legendes(e)[k] and svg["role"] == "img"


def test_mini_garde_son_aria():
    e = calculs.etat("rangs")
    assert balises(dessins.DESSINS["mini"](e, aria="autre"), "svg")[0]["aria-label"] == "Disposition Rangs"


def test_en_cm_et_cadre():
    svg = '<svg viewBox="-24 0 240 120" role="img"><rect x="0" y="0" width="24" height="12"/></svg>'
    assert dessins.en_cm(svg, 2.4) == ('<svg viewBox="-10 0 100 50" role="img"><g transform="scale(0.416667)">'
                                       '<rect x="0" y="0" width="24" height="12"/></g></svg>')
    assert dessins.cadre_commun(['<svg viewBox="0 0 10 10">', '<svg viewBox="-5 2 10 20">']) == "-5 0 15 22"
    assert 'viewBox="1 2 3 4"' in dessins.recadrer('<svg viewBox="0 0 10 10" role="img"></svg>', "1 2 3 4")


def _classes(svg):
    return {c for m in re.findall(r'class="([^"]+)"', svg) for c in m.split()}


def _regle(classe, css):
    return re.search(rf"\.{re.escape(classe)}(?![\w-])[^{{]*\{{([^}}]*)\}}", css)


def test_chaque_classe_a_sa_regle():
    for k, c in CAS:
        svg = dessins.DESSINS[k](calculs.etat(c))
        assert sorted(x for x in _classes(svg) if not _regle(x, dessins.CSS)) == [], (k, c)


def test_textes_ont_une_couleur():
    """Hors de la scène (Découpe, Explication), un <text> sans règle `fill` serait noir."""
    for k, c in CAS:
        for t in re.findall(r"<text ([^>]*)>", dessins.DESSINS[k](calculs.etat(c))):
            cls = re.search(r'class="([^"]+)"', t)[1].split()
            assert "fill" in t or any("fill" in _regle(x, dessins.CSS)[1] for x in cls), (k, t)


def test_css_sur_les_jetons_du_site():
    jetons = set(re.findall(r"(--[\w-]+):", (RACINE / "commun/site.css").read_text(encoding="utf-8")))
    assert set(re.findall(r"var\((--[\w-]+)\)", dessins.CSS)) <= jetons
    assert all(v.strip().startswith("var(--") for v in re.findall(r"font-family:([^;}]*)", dessins.CSS))
    for interdit in ("monospace", "JetBrains", "Archivo", "prefers-color-scheme", "@media", "·", ".mono"):
        assert interdit not in dessins.CSS
    assert dessins.ECHELLES == {"elevation": 2.4, "dessus": 2.6, "profil": 9, "travee": 3}


# ------------------------------------------------------------------ tâche 3 : Plans, Découpe, Montage, Achats
V = {c: vues.vues(c) for c in calculs.CLES}


def _viewbox(svg):
    return [float(x) for x in balises(svg, "svg")[0]["viewbox"].split()]


def test_vues_et_variante_inconnue():
    assert all(list(v) == ["plans", "decoupe", "montage", "achats", "explication"] for v in V.values())
    with pytest.raises(ValueError, match="niche"):
        vues.vues("niche")


def test_plans():
    for c, v in V.items():
        p = v["plans"]
        assert [(x.k, x.nom) for x in p.elements] == list(vues.REPERES)
        assert p.outils == ("zoom", "mesure") and {x.titre for x in p.elements} == {f"Disposition {calculs.etat(c).nom}"}
        assert f'<p class="cotes">{escape(calculs.etat(c).kit)}</p>' in p.fiche
        assert 'href="#decoupe"' in p.fiche and 'href="#montage"' in p.fiche
        for x in p.elements:
            (svg,) = balises(x.scene, "svg")[:1]
            assert svg["aria-label"] == dessins.legendes(calculs.etat(c))[x.k]
            assert (svg.get("data-mesure") == "non") == (x.k in ("iso", "detail"))


def test_cadrage_commun():
    for k in [k for k, _ in vues.REPERES]:
        assert len({balises(next(x.scene for x in v["plans"].elements if x.k == k), "svg")[0]["viewbox"]
                    for v in V.values()}) == 1, k
    iso = _viewbox(next(x.scene for x in V["actuelle"]["plans"].elements if x.k == "iso"))
    assert iso == pytest.approx([-491.8, -499.6, 553.9, 562.2], abs=0.05)
    dessus = _viewbox(next(x.scene for x in V["actuelle"]["plans"].elements if x.k == "dessus"))
    assert [v * 2.6 for v in dessus] == pytest.approx([-110, -24.4, 786.9, 1028.4], abs=0.05)


def test_mesure_en_cm():
    """Deux axes de montants voisins, lus dans le repère de la scène : 55 cm, le pas."""
    for k in ("elevation", "dessus"):
        scene = next(x.scene for x in V["actuelle"]["plans"].elements if x.k == k)
        s = float(re.search(r'<g transform="scale\(([\d.]+)\)">', scene)[1])
        monts = sorted({float(r["x"]) + float(r["width"]) / 2 for r in balises(scene, "rect", classe="mont")})
        assert (monts[1] - monts[0]) * s == pytest.approx(document.MONTANTS["pas"], abs=0.01), k


@pytest.mark.parametrize("cle,reperes,pieces", [("actuelle", 6, 44), ("rangs", 4, 53), ("decalee", 4, 53), ("escalier", 4, 59)])
def test_decoupe(cle, reperes, pieces):
    (e,) = V[cle]["decoupe"].elements
    nom = calculs.etat(cle).nom
    assert f"Disposition {nom} : {reperes} repères, {pieces} pièces à débiter." in e.scene
    assert _lignes(e.scene.split("</table>")[0]) == _lignes(_blocs(cle)[3].split("<h3>")[0])
    assert [unescape(t) for t in re.findall(r"<figcaption>(.*?)</figcaption>", e.scene)] == [
        "Tablettes : refente des plans de chêne", "Montants et chevilles", "Perçage d'un montant", "Entaille d'une tablette"]
    assert 'class="mono"' not in e.scene


@pytest.mark.parametrize("cle", calculs.CLES)
def test_montage(cle):
    (e,) = V[cle]["montage"].elements
    ancien = _section("montage")
    assert _lignes(e.scene.split("</table>")[0]) == _lignes(_blocs(cle)[2].split("<h3>Composition</h3>")[1])
    titres = re.findall(r"<li><b>(.*?)</b> : ", ancien)
    assert re.findall(r"<h3>(.*?)</h3>", e.scene) == titres and len(titres) == 9
    for li in re.findall(r"<li><b>.*?</b> : (.*?)</li>", ancien):
        assert _texte(li) in _texte(e.scene)
    outils = re.search(r"<p><b>Outils</b> : (.*?)</p>", ancien)[1]
    assert "Outils à réunir" in e.scene and _texte(outils) in _texte(e.scene)


@pytest.mark.parametrize("cle", calculs.CLES)
def test_achats(cle):
    (v,) = V[cle]["achats"].elements
    e = calculs.etat(cle)
    assert re.findall(r"<h3>(.*?)</h3>", v.scene) == ["Weldom Marseille Saint-Barnabé", "Castorama"]
    assert f"Disposition {e.nom}" in v.scene and total_achats(vues.sections_achats(e), arrondi=False) == euros(e.total)
    for a in e.achats:
        assert escape(a["article"]) in v.scene and f"prix {a['statut']}" in v.scene
        if a["url"]:
            assert f'href="{a["url"]}"' in v.scene
    # chaque ligne du bloc : quantité, montant de la ligne, prix unitaire dans la note
    rangees = re.findall(r"<tr><td>(.*?)</td><td[^>]*>(.*?)</td><td[^>]*>(.*?)</td><td[^>]*>(.*?)</td></tr>", v.scene)
    for a in e.achats:
        (r,) = [r for r in rangees if r[0].startswith(escape(a["article"]) + "<small>")]
        assert (unescape(r[1]), r[2], r[3]) == (a["ref"], f'{a["qte"]:g}', euros(a["total"])), (a["article"], r)
        assert f"{euros(a['pu'])} l'unité" in r[0]
    # intro, total de la disposition, transport, note : chaque paragraphe de la section, dans sa version `cle`
    paragraphes = re.findall(r"<p[^>]*>(.*?)</p>", _dispo(_section("achats"), cle), re.S)
    assert len(paragraphes) == 4
    for p in paragraphes:
        assert _texte(p) in _texte(v.scene)


def test_apres_titre():
    assert vues._apres_titre("<h2>A</h2><p>b</p>", "<i>x</i>") == "<h2>A</h2><i>x</i><p>b</p>"
    with pytest.raises(ValueError):
        vues._apres_titre("<p>b</p>", "x")


# ------------------------------------------------------------------ tâche 4 : Explication et rendus
def _explication(cle):
    (e,) = vues.vues(cle)["explication"].elements
    return e.scene


def test_ordre_de_l_explication():
    for c in calculs.CLES:
        assert re.findall(r"<h2>(.*?)</h2>", _explication(c)) == [
            "Dispositions", "Le mécanisme", "Présentoir", "Rendus 3D", "Matériaux", "Tenue : poids et chute",
            "À vérifier sur place"]


@pytest.mark.parametrize("cle", calculs.CLES)
def test_tete_et_chiffres(cle):
    s, e = _explication(cle), calculs.etat(cle)
    chapo = re.search(r'<p class="chapo">(.*?)</p>', s)[1]
    assert chapo.startswith("<b>Étagères sur montants percés</b> : ")
    assert _texte(chapo.split(" : ", 1)[1]) == _texte(_blocs(cle)[0])
    for valeur, libelle in ((e.kit, "longueurs des tablettes (cm)"), (f"{len(calculs.pieces(e))} repères", "pièces à débiter"),
                            ("9 étapes", "de la cloison sondée au montage"), (euros(e.total), "matériaux TTC, sans livraison ni outillage")):
        assert escape(valeur) in s and libelle in s
    assert [a["href"] for a in balises(s, "a", classe="btn")] == ["#plans", "#achats", "../amenagement/"]


@pytest.mark.parametrize("cle", calculs.CLES)
def test_vignettes(cle):
    liens = balises(_explication(cle), "a", classe="dispo")
    assert [a["href"] for a in liens] == ["./#explication", "rangs.html#explication", "decalee.html#explication",
                                          "escalier.html#explication"]
    assert [a.get("aria-current") for a in liens] == [("page" if c == cle else None) for c in calculs.CLES]
    for d in document.DISPOSITIONS:
        assert escape(d["idee"]) in _explication(cle)


def test_rendus():
    assert [i["src"] for i in balises(_explication("actuelle"), "img")] == ["rendus/actuelle-iso.jpg", "rendus/actuelle-detail.jpg"]
    assert [i["alt"] for i in balises(_explication("actuelle"), "img")] == [t for _, t in document.RENDUS]
    for c in ("rangs", "decalee", "escalier"):
        assert balises(_explication(c), "img") == [] and 'href="./#explication">les voir</a>' in _explication(c)


# empreintes de salon-meubles-3d/etageres-{iso,detail}.jpg, les images de l'ancienne page, relevées à la copie (le
# dossier racine part au nettoyage commun du salon)
EMPREINTES_RENDUS = {"iso": "a2c68f135665860428190011cef83f997006d557e1da7c4846520756ce5f4e13",
                     "detail": "047d0c84e7f25c2bbf04e04e1c1fd29c2869faa664ce9488acfe8dfc5832c575"}


def test_rendus_copies_tels_quels():
    for k, empreinte in EMPREINTES_RENDUS.items():
        assert hashlib.sha256((vues.RENDUS_SITE / f"actuelle-{k}.jpg").read_bytes()).hexdigest() == empreinte, k


# sections de l'ancienne page → vue qui reprend leurs morceaux (p, li, td, th, h3)
DESTINATION = {"dispositions": "explication", "meuble": "explication", "presentoir": "explication",
               "rendus": "explication", "materiaux": "explication", "debit": "decoupe", "charges": "explication",
               "achats": "achats", "montage": "montage", "valider": "explication"}
# morceaux retirés ou réécrits par une décision de ce plan (décisions 5, 6 et 10, tableau « Ancienne page → vues »)
ECARTS = ("Cliquer une vignette", "<b>Outils</b> :", "Total TTC (disposition")
# en-têtes des tableaux refaits par un bloc du socle (décision 5 : achats ; matériaux : retenu, pourquoi, autres
# possibilités dans une seule cellule), qui ont leurs propres en-têtes
SANS_ENTETES = ("achats", "materiaux")
# réécrit pour les trois variantes sans rendu (décisions, « Rendus 3D ») : une ligne qui renvoie à Actuelle
RENDUS_AILLEURS = "Disposition actuelle seulement ; les autres dispositions se rendent sur demande."
_MORCEAUX = re.compile(r"<(p|li|td|th|h3)(?:\s[^>]*)?>(.*?)</\1>", re.S)


def _morceaux(html):
    """(balise, morceau entier, intérieur) de chaque p, li, td, th, h3."""
    return [(x.group(1), x.group(0), x.group(2)) for x in _MORCEAUX.finditer(html)]


@pytest.mark.parametrize("cle", calculs.CLES)
@pytest.mark.parametrize("ident", sorted(DESTINATION))
def test_rien_ne_se_perd(cle, ident):
    """Chaque paragraphe, point, cellule et intertitre de l'ancienne section, dans la version de la disposition `cle`
    (blocs des autres dispositions ôtés, légendes ôtées : elles sont les textes alternatifs, testés en tâche 2), est
    dans la vue qui la reprend, ou dans Montage pour la composition."""
    vs = vues.vues(cle)
    lu = {k: _texte(v.elements[0].scene) for k, v in vs.items() if k != "plans"}
    html = _dispo(_section(ident), cle)
    html = re.sub(r'<p class="cap">.*?</p>', "", html, flags=re.S)
    html = re.sub(r'<button type="button" class="dmini".*?</button>', "", html, flags=re.S)
    html = re.sub(r"<svg.*?</svg>", "", html, flags=re.S)
    if ident == "achats":
        html = re.sub(r'<td class="num">.*?</td>', "", html)        # montants au format du socle (tâche 3)
    cibles = [lu[DESTINATION[ident]]] + ([lu["montage"]] if ident == "meuble" else [])
    vus = 0
    for balise, entier, corps in _morceaux(html):
        if any(x in entier for x in ECARTS) or (balise == "th" and ident in SANS_ENTETES):
            continue
        if ident == "rendus" and cle != "actuelle" and _texte(corps) == RENDUS_AILLEURS:
            continue
        if ident == "montage" and balise == "li":                      # étape : titre en <h3>, texte en <p>
            titre, texte = re.match(r"<b>(.*?)</b> : (.*)", corps, re.S).groups()
            assert _texte(titre) in lu["montage"] and _texte(texte) in lu["montage"]
            vus += 1
            continue
        if ident == "achats" and balise == "td" and "<br>" in corps:   # article, puis sa note dans la note du bloc
            assert all(_texte(x) in lu["achats"] for x in corps.split("<br>"))
            vus += 1
            continue
        t = _texte(corps)
        assert any(t in c for c in cibles), (ident, balise, t)
        vus += 1
    assert vus > 0 or (ident == "rendus" and cle != "actuelle")
    if ident == "dispositions":
        ouverture = re.search(r"<p>(.*?)Cliquer une vignette", html, re.S)[1]   # avant la phrase réécrite
        assert _texte(ouverture) + " Choisir une disposition" in lu["explication"]
        assert ("Choisir une disposition change toute la page : élévation, vues de dessus, vue iso, composition, "
                "débit, achats et prix.") in lu["explication"]
    if ident == "rendus" and cle != "actuelle":
        assert ("Rendus de la disposition Actuelle seulement ( les voir ) ; les autres dispositions se rendent sur "
                "demande.").replace("( ", "(").replace(" )", ")") in lu["explication"]


def test_rien_ne_se_perd_chapo_et_remarque():
    for c in calculs.CLES:
        s = _texte(_explication(c))
        assert _texte(_blocs(c)[0]) in s
        assert ("Repère : origine au coin nord-ouest du salon, y vers le sud, z depuis le sol, cotes en cm. Dimensions : "
                "pieces/salon/etageres/document.py (DISPOSITIONS). Le reste du salon : plan du salon.") in s
        assert 'href="../../archive/salon-bibliotheque-fixation.html"' in _explication(c)


# ------------------------------------------------------------------ tâche 5 : document et contrôles de la page
D = document._document()
TOUT = {c: D.generer(c) for c in calculs.CLES}


def test_document():
    assert (D.piece, D.id, D.nom, D.type, D.options) == ("salon", "etageres", "Étagères", "construction", ())
    assert [(v.id, v.nom, v.version, len(v.changements), v.figees) for v in D.variantes] == [
        ("actuelle", "Actuelle", "V1.8", 9, ()), ("rangs", "Rangs", "V1.8", 0, ()),
        ("decalee", "Décalée", "V1.8", 0, ()), ("escalier", "Escalier", "V1.8", 0, ())]
    assert [(c.version, c.date, c.texte) for c in D.variantes[0].changements] == [
        (c.version, c.date, c.texte) for c in depuis_page(ANCIENNE)]
    for c, vs in TOUT.items():
        modele.verifier(D, vs)
        assert list(vs) == list(modele.VUES["construction"]) and all(v.elements for v in vs.values()), c
    assert set(document.CACHE_RENDU.variantes) == set(calculs.CLES)   # le cache déclare les quatre dispositions


@pytest.mark.parametrize("cle", calculs.CLES)
def test_chaque_classe_de_chaque_variante_a_sa_regle(cle):
    """Le CSS filtré comme à la construction, sur les dessins des quatre variantes réunies ; chaque classe de chaque
    scène de la variante `cle` y a une règle, ou en a une dans commun/site.css (classes du site)."""
    from commun.construction import _dessins
    from commun.css_dessins import css_dessins
    css = css_dessins(D.css, [s for vs in TOUT.values() for s in _dessins(vs)], ".d-salon")
    site_css = (RACINE / "commun/site.css").read_text(encoding="utf-8")
    for v in TOUT[cle].values():
        for e in v.elements:
            for c in _classes(e.scene) - {"zone"}:
                assert re.search(rf"\.{re.escape(c)}(?![\w-])", css) or re.search(rf"\.{re.escape(c)}(?![\w-])", site_css), (cle, v.id, c)


def test_aucun_interdit():
    for c, vs in TOUT.items():
        tout = "".join(v.fiche + e.scene + e.fiche for v in vs.values() for e in v.elements)
        for interdit in ("·", 'type="checkbox"', "Copier la liste", "À venir", "Lecture du plan", "Lecture de la coupe",
                         'class="mono"', 'class="cap"', 'class="dv"', "localStorage", "<figcaption class"):
            assert interdit not in tout, (c, interdit)
        visible = re.sub(r'(aria-label|alt)="[^"]*"', "", tout)
        for texte in dessins.legendes(calculs.etat(c)).values():
            assert escape(texte, quote=True) not in visible and texte not in visible


def test_liens():
    permis = {"./#explication", "rangs.html#explication", "decalee.html#explication", "escalier.html#explication",
              "../amenagement/", "../../archive/salon-bibliotheque-fixation.html", "historique.html"}
    for c, vs in TOUT.items():
        for v in vs.values():
            for e in v.elements:
                for a in balises(e.scene + e.fiche + v.fiche, "a"):
                    h = a["href"]
                    assert h.startswith(("#", "https://")) or h in permis, (c, h)


def test_ids_uniques_et_classes_du_site():
    for c, vs in TOUT.items():
        tout = "".join(v.fiche + e.scene + e.fiche for v in vs.values() for e in v.elements)
        ids = re.findall(r'\bid="([^"]+)"', tout)
        assert len(ids) == len(set(ids))
        dessinees = {k for svg in re.findall(r"<svg.*?</svg>", tout, re.S) for k in _classes(svg)}
        assert not dessinees & {"app", "rail", "barre", "contenu", "vue", "scene", "fiche", "element", "outils"}


# ------------------------------------------------------------------ tâche 6 : bascule
def test_bascule():
    module = charger_site()
    (salon,) = [p for p in module.SITE.pieces if p.id == "salon"]
    assert document.DOCUMENT in salon.documents and [d.id for d in salon.documents] == ["amenagement", "etageres", "enfilade"]
    suivis = subprocess.run(["git", "ls-files", "salon-etageres.html"], cwd=RACINE, capture_output=True, text=True).stdout
    assert suivis == ""          # just salon peut réécrire la page à la racine : seul compte que git ne la suive plus
    (r,) = [r for r in module.REDIRECTIONS if r.ancienne == "salon-etageres.html"]
    assert (r.cible, r.pages) == ("salon/etageres/", {"changements": "salon/etageres/historique.html"})
    for ancre, fragment in (("dispositions", "explication"), ("iso", "plans?k=iso"), ("meuble", "plans?k=elevation"),
                            ("presentoir", "explication"), ("rendus", "explication"), ("materiaux", "explication"),
                            ("debit", "decoupe"), ("charges", "explication"), ("achats", "achats"),
                            ("montage", "montage"), ("valider", "explication"), ("inconnue", ""), ("", "")):
        assert _traduire(r, ancre) == fragment
    # chaque identifiant posé sur un titre de l'ancienne page est traduit (sauf changements, une autre page)
    assert set(re.findall(r'<h2 id="([^"]+)"', ANCIENNE)) == set(r.ancres)


def test_journal_apres_la_bascule():
    lignes = [e for e in entrees(charger_site().SITE, RACINE) if e.piece == "Salon" and e.document == "Étagères"]
    assert [(e.version, e.texte) for e in lignes] == [(c.version, c.texte) for c in depuis_page(ANCIENNE)]
    assert len(lignes) == 9 and {e.lien for e in lignes} == {"salon/etageres/"} and {e.variante for e in lignes} == {"Actuelle"}


def _table(html: str, entete: str) -> str:
    """Le premier <table> de `html` dont un en-tête est `entete`."""
    (t,) = [t for t in re.findall(r"<table.*?</table>", html, re.S) if f">{entete}</th>" in t][:1]
    return t


@pytest.mark.parametrize("cle", calculs.CLES)
@pytest.mark.parametrize("ident,entete", [("dispositions", "Hauteurs de dessus"), ("presentoir", "Poids posé"),
                                          ("charges", "Résistance")])
def test_tableaux_de_l_explication(cle, ident, entete):
    """Tableau comparatif, présentoir, ce qui peut céder : les lignes de l'ancienne page, cellule par cellule."""
    ancien = _table(_dispo(_section(ident), cle), entete)
    assert _lignes(_table(_explication(cle), entete)) == _lignes(ancien)
