"""Journal des changements de tous les documents."""
from pathlib import Path

from commun.journal import EntreeJournal, entrees
from commun.modele import Changement, Document, Piece, Site, Variante
from tests.outils import depuis_page

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


def test_depuis_page():
    assert depuis_page(PAGE) == [
        Changement("V1.1", "12/03/2026", "Ajout du meuble & d'un tiroir"),
        Changement("V1.0", "02/03/2026", "Premier jet"),
    ]


def test_entrees_triees():
    salon = (Variante("", "Principale", "V2", (Changement("V2", "05/02/2026", "salon b"),
                                                 Changement("V1", "01/02/2026", "salon a"))),)
    var = (Variante("", "Principale", "V1", (Changement("V1", "03/02/2026", "doc"),)),
           Variante("victor", "Victor", "V1", (Changement("V1", "10/02/2026", "v1"),
                                               Changement("V0", "10/02/2026", "v2"))))
    site = Site((Piece("p", "Pièce", (
        Document("p", "salon", "Salon", "amenagement", salon, lambda v: {}),
        Document("p", "doc", "Doc", "amenagement", var, lambda v: {}),
    )),))
    res = entrees(site)
    assert [e.date_iso for e in res] == ["2026-02-10", "2026-02-10", "2026-02-05", "2026-02-03", "2026-02-01"]
    assert [e.texte for e in res[:2]] == ["v1", "v2"]
    assert res[0].variante == "Victor"
    assert res[3].variante == "Principale"
    assert res[2].variante is None and res[2].lien == "p/salon/"
    assert isinstance(res[0], EntreeJournal)


def test_entrees_une_seule_variante():
    var = (Variante("", "Principale", "V1", (Changement("V1", "03/02/2026", "doc"),)),)
    site = Site((Piece("p", "Pièce", (Document("p", "doc", "Doc", "amenagement", var, lambda v: {}),)),))
    (e,) = entrees(site)
    assert e.variante is None and e.piece == "Pièce" and e.document == "Doc" and e.version == "V1"


def test_page_d_essai():
    """Une page d'avant la refonte (tableau « Changements ») : ses changements."""
    html = (RACINE / "tests/fixtures/passerelle/essai-ancienne.html").read_text(encoding="utf-8")
    assert depuis_page(html) == [
        Changement("V1.1", "12/11/2026", "Coupe A-A ajoutée, plan & cotes repris."),
        Changement("V1.0", "02/11/2026", "Premier plan."),
    ]

