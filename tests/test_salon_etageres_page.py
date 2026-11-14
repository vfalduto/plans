"""Salon, étagères : la page du document salon/etageres (calculs, dessins, vues, document), comparée à l'ancienne
page V1.8 figée (tests/fixtures/salon/salon-etageres.html) et aux dessins de référence (tests/fixtures/salon/)."""
import json
import math
import re
from html import escape, unescape
from html.parser import HTMLParser

import pytest

from pieces.salon.etageres import calculs, dessins
from tests.outils import RACINE, balises

ANCIENNE = (RACINE / "tests/fixtures/salon/salon-etageres.html").read_text(encoding="utf-8")
INDEX = json.loads((RACINE / "tests/fixtures/salon/index.json").read_text(encoding="utf-8"))


# ------------------------------------------------------------------ outils
_EN_LIGNE = re.compile(r"</?(?:b|i|em|strong|span|a|small)(?:\s[^>]*)?>")


def _texte(html: str) -> str:
    """Balises remplacées par une espace (celles d'un mot dans la ligne, `b`, `span`, `a`… : ôtées, « <b>rainure</b>. »
    se lit « rainure. »), entités décodées, blancs réduits à une espace, bords ôtés."""
    sans = re.sub(r"<[^>]+>", " ", _EN_LIGNE.sub("", html))
    return re.sub(r"\s+", " ", unescape(sans)).strip()


class _Blocs(HTMLParser):
    """HTML intérieur des <div class="dv" data-d="cle">, par la profondeur des div."""

    def __init__(self, cle):
        super().__init__(convert_charrefs=False)
        self.cle, self.profondeur, self.debut, self.blocs = cle, 0, None, []

    def _pos(self):
        ligne, col = self.getpos()
        return self.lignes[ligne - 1] + col

    def handle_starttag(self, tag, attrs):
        if tag != "div":
            return
        self.profondeur += 1
        a = dict(attrs)
        if self.debut is None and a.get("class") == "dv" and a.get("data-d") == self.cle:
            self.debut = (self.profondeur, self._pos() + len(self.get_starttag_text()))

    def handle_endtag(self, tag):
        if tag != "div":
            return
        if self.debut is not None and self.profondeur == self.debut[0]:
            self.blocs.append(self.source[self.debut[1]:self._pos()])
            self.debut = None
        self.profondeur -= 1


def _blocs(cle: str) -> list[str]:
    """HTML intérieur des sept <div class="dv" data-d="cle"> de la page figée, dans l'ordre : chapô, vue iso, le
    meuble, débit, fixation, achats, point « Composition »."""
    corps = ANCIENNE[ANCIENNE.index("<body"):]
    p = _Blocs(cle)
    p.source = corps
    p.lignes = [0]
    for ligne in corps.splitlines(keepends=True):
        p.lignes.append(p.lignes[-1] + len(ligne))
    p.feed(corps)
    p.close()
    assert len(p.blocs) == 7, (cle, len(p.blocs))
    return p.blocs


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
