"""Salon, étagères : la page du document salon/etageres (calculs, dessins, vues, document), comparée à l'ancienne
page V1.8 figée (tests/fixtures/salon/salon-etageres.html) et aux dessins de référence (tests/fixtures/salon/)."""
import json
import math
import re
from html import escape, unescape
from html.parser import HTMLParser

import pytest

from pieces.salon.etageres import calculs
from tests.outils import RACINE

ANCIENNE = (RACINE / "tests/fixtures/salon/salon-etageres.html").read_text(encoding="utf-8")
INDEX = json.loads((RACINE / "tests/fixtures/salon/index.json").read_text(encoding="utf-8"))


# ------------------------------------------------------------------ outils
def _texte(html: str) -> str:
    """Balises remplacées par une espace, entités décodées, blancs réduits à une espace, bords ôtés."""
    return re.sub(r"\s+", " ", unescape(re.sub(r"<[^>]+>", " ", html))).strip()


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
