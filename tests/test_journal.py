"""Journal des changements lu dans les pages publiées."""
from pathlib import Path

from commun.journal import EntreeJournal, depuis_page, entrees, version_depuis_page
from commun.modele import Changement, Document, Passerelle, Piece, Site, Variante

RACINE = Path(__file__).resolve().parent.parent

PAGE = """<html><body><main>
<h2>Plan</h2><table><tr><td>01/01/2020</td><td>x</td><td>hors section</td></tr></table>
<h2 id="x">Changements</h2>
<table>
<tr><th>Version</th><th>Date</th><th>Changement</th></tr>
<tr><td>V1.1</td><td>12/03/2026</td><td>Ajout <b>du</b> meuble &amp; d'un tiroir</td></tr>
<tr><td>V1.0</td><td>02/03/2026</td><td>Premier jet</td></tr>
</table>
<h2>Fin</h2>
</main></body></html>"""


def _page(lignes):
    corps = "".join(f"<tr><td>{v}</td><td>{d}</td><td>{t}</td></tr>" for v, d, t in lignes)
    return ('<section id="changements"><h2>Changements</h2><table>'
            '<tr><th>Version</th><th>Date</th><th>Changement</th></tr>' + corps + "</table></section>")


def test_depuis_page():
    assert depuis_page(PAGE) == [
        Changement("V1.1", "12/03/2026", "Ajout du meuble & d'un tiroir"),
        Changement("V1.0", "02/03/2026", "Premier jet"),
    ]


def test_version_depuis_page():
    assert version_depuis_page('<div class="kicker">Entrée · V4.8</div>') == "V4.8"
    assert version_depuis_page("<p>rien</p>") is None


def test_entrees_triees(tmp_path):
    (tmp_path / "salon.html").write_text(_page([("V2", "05/02/2026", "salon b"), ("V1", "01/02/2026", "salon a")]))
    var = (Variante("", "Principale", "V1", (Changement("V1", "03/02/2026", "doc"),)),
           Variante("victor", "Victor", "V1", (Changement("V1", "10/02/2026", "v1"),
                                               Changement("V0", "10/02/2026", "v2"))))
    site = Site((Piece("p", "Pièce", (
        Passerelle("p", "salon", "Salon", "amenagement", "salon.html"),
        Document("p", "doc", "Doc", "amenagement", var, lambda v: {}),
    )),))
    res = entrees(site, tmp_path)
    assert [e.date_iso for e in res] == ["2026-02-10", "2026-02-10", "2026-02-05", "2026-02-03", "2026-02-01"]
    assert [e.texte for e in res[:2]] == ["v1", "v2"]
    assert res[0].variante == "Victor"
    assert res[3].variante == "Principale"
    assert res[2].variante is None and res[2].lien == "salon.html"
    assert isinstance(res[0], EntreeJournal)


def test_entrees_une_seule_variante(tmp_path):
    var = (Variante("", "Principale", "V1", (Changement("V1", "03/02/2026", "doc"),)),)
    site = Site((Piece("p", "Pièce", (Document("p", "doc", "Doc", "amenagement", var, lambda v: {}),)),))
    (e,) = entrees(site, tmp_path)
    assert e.variante is None and e.piece == "Pièce" and e.document == "Doc" and e.version == "V1"


def test_page_d_essai():
    """Une page d'avant la refonte (format des pages en passerelle) : ses changements et sa version."""
    html = (RACINE / "tests/fixtures/passerelle/essai-ancienne.html").read_text(encoding="utf-8")
    assert depuis_page(html) == [
        Changement("V1.1", "12/11/2026", "Coupe A-A ajoutée, plan & cotes repris."),
        Changement("V1.0", "02/11/2026", "Premier plan."),
    ]
    assert version_depuis_page(html) == "V1.1"


def test_pages_reelles():
    """Chaque page de la racine qui a une section Changements se lit (il n'en reste plus une fois tout migré)."""
    for p in sorted(RACINE.glob("*.html")):
        html = p.read_text(encoding="utf-8")
        if 'id="changements"' in html:
            changements = depuis_page(html)
            assert changements and changements[0].version.startswith("V"), p.name
