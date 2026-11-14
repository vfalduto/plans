import subprocess

from commun.journal import entrees
from commun.modele import Changement
from pieces.salon.enfilade import dessins, document, vues
from tests.outils import RACINE, charger_site

ANCRES = {"iso": "plans?k=iso", "meuble": "plans?k=elevation", "rendus": "explication", "construction": "explication",
          "materiaux": "explication", "comparaison": "explication", "metod": "explication", "debit": "decoupe",
          "achats": "achats", "montage": "montage", "valider": "explication"}


def test_document():
    d = document.DOCUMENT
    assert (d.piece, d.id, d.nom, d.type, d.css, d.generer) == ("salon", "enfilade", "Enfilade", "construction",
                                                               dessins.CSS, vues.vues)
    (v,) = d.variantes
    assert (v.id, v.version, v.figees) == ("", "V1.6", ())
    assert v.changements == tuple(Changement(*c) for c in document.CHANGEMENTS) and len(v.changements) == 7


def test_site_declare_l_enfilade():
    site = charger_site().SITE
    (salon,) = [p for p in site.pieces if p.id == "salon"]
    assert [d for d in salon.documents if d.id == "enfilade"] == [document.DOCUMENT]


def test_redirection():
    (r,) = [r for r in charger_site().REDIRECTIONS if r.ancienne == "salon-enfilade.html"]
    assert (r.cible, r.ancres, r.motifs, r.pages) == ("salon/enfilade/", ANCRES, (),
                                                      {"changements": "salon/enfilade/historique.html"})


def test_journal_garde_sept_changements():
    lignes = [e for e in entrees(charger_site().SITE, RACINE) if (e.piece, e.document) == ("Salon", "Enfilade")]
    assert [e.version for e in lignes] == ["V1.6", "V1.5", "V1.4", "V1.3", "V1.2", "V1.1", "V1.0"]


def test_ancienne_page_retiree():
    suivis = subprocess.run(["git", "ls-files", "salon-enfilade.html"], cwd=RACINE, capture_output=True, text=True,
                            check=True).stdout
    assert suivis == ""
    assert not (RACINE / "3d" / "salon").exists()
