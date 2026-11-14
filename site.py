"""Pièces et documents du site, dans l'ordre du menu ; construit site/.

  python3 site.py                                          construit tout
  python3 site.py <piece>/<document>                       reconstruit ce document, le menu, l'accueil et le journal
  python3 site.py --figer <piece>/<document>[/<variante>]  fige la version en cours d'une variante

Un document pas encore migré est une Passerelle vers sa page actuelle, recopiée telle quelle dans site/ ; un document
migré est le Document de pieces/<piece>/<document>/document.py, et son ancienne page devient une Redirection. Toute la
logique est dans commun/construction.py (`import site` donne le module standard de Python : ne rien importer d'ici).
"""
import sys
from pathlib import Path

from commun.construction import commande
from commun.modele import Passerelle, Piece, Site
from commun.redirections import Redirection
from pieces.chambre.amenagement import document as chambre_amenagement
from pieces.cuisine.amenagement import document as cuisine_amenagement
from pieces.entree.amenagement import document as entree_amenagement
from pieces.salon.enfilade import document as salon_enfilade

RACINE = Path(__file__).resolve().parent

SITE = Site((
    Piece("cuisine", "Cuisine", (
        cuisine_amenagement.DOCUMENT,
        Passerelle("cuisine", "porte-cellier", "Porte du cellier", "construction", "cuisine-v13-porte-cellier.html"),
    )),
    Piece("sdb", "Salle de bain", (
        Passerelle("sdb", "meuble-bas", "Meuble bas", "construction", "sdb-meuble-bas.html"),
        Passerelle("sdb", "meuble-haut", "Meuble haut", "construction", "sdb-meuble-haut.html"),
    )),
    Piece("entree", "Entrée", (
        entree_amenagement.DOCUMENT,
    )),
    Piece("salon", "Salon", (
        Passerelle("salon", "amenagement", "Aménagement", "amenagement", "salon-v4.html"),
        Passerelle("salon", "etageres", "Étagères", "construction", "salon-etageres.html"),
        salon_enfilade.DOCUMENT,
    )),
    Piece("chambre", "Chambre", (
        chambre_amenagement.DOCUMENT,
    )),
))

# Anciennes adresses devenues des pages de redirection (commun/redirections.py). Les ancres sont celles que le
# sommaire des anciennes pages posait sur leurs titres h2 (slug du texte : « Coupe B-B · mur de la salle de bain » →
# coupe-b-b-mur-de-la-salle-de-bain) ; une ancre absente d'ici mène à la vue par défaut.
ANCRES_ENTREE = {"plan": "plan", "vues-3d": "iso", "principe": "explication", "achats-ikea-penderie": "explication",
                 "materiaux": "explication", "points-a-verifier": "explication"}
COUPES = ((r"^coupe-([a-d])-", "coupes?k={1}"),)
HISTORIQUE_ENTREE = {"changements": "entree/amenagement/historique.html"}
# anciennes ancres de salon-enfilade.html, posées en dur par son générateur
ANCRES_ENFILADE = {"iso": "plans?k=iso", "meuble": "plans?k=elevation", "rendus": "explication",
                   "construction": "explication", "materiaux": "explication", "comparaison": "explication",
                   "metod": "explication", "debit": "decoupe", "achats": "achats", "montage": "montage",
                   "valider": "explication"}
# la page de la chambre ne posait d'identifiant que sur « Points à vérifier » (verifier) ; les trois autres sont les
# slugs de ses titres, au cas où un lien les cite
ANCRES_CHAMBRE = {"verifier": "explication", "plan-a-l-echelle": "plan", "elevations": "coupes",
                  "principe": "explication"}

# ancres de cuisine-v13.html (3d/ancres.js) : la page courante ; ses blocs figés V11.49 et V12.7 (ids relevés une
# fois dans tests/fixtures/cuisine/ancres.json, plus l'id du bloc) mènent à leur archive
ANCRES_CUISINE = {"plan": "plan", "br": "plan", "hauteur-du-plan-de-travail-etude": "explication",
                  "porte-du-cellier-mantion-tango": "explication", "electricite": "plan?k=elec",
                  "elevation-du-mur-nord-electricite": "coupes?k=elec", "rendus-3d": "iso",
                  "materiaux": "explication", "contenu-des-rangements": "explication"}
MOTIFS_CUISINE = ((r"^coupe-([a-c])-", "coupes?k={1}"), (r"^capacite-", "explication"))
_FIGEES_V11_49 = (
    "plan-v11-49", "coupe-a-a-mur-nord-v11-49", "coupe-b-b-mur-sud-v11-49", "coupe-c-c-mur-est-v11-49",
    "rendus-3d-v11-49", "materiaux-v11-49", "contenu-des-rangements-v11-49",
    "capacite-v11-34-v11-49-et-proposition-9-a-v11-49", "changements-V11.49", "br-V11.49", "V11.49")
_FIGEES_V12_7 = (
    "plan-v12-7", "coupe-a-a-mur-nord-v12-7", "coupe-b-b-mur-sud-v12-7", "coupe-c-c-mur-est-v12-7",
    "electricite-v12-7", "elevation-du-mur-nord-electricite-v12-7", "rendus-3d-v12-7", "materiaux-v12-7",
    "contenu-des-rangements-v12-7", "capacite-v11-34-v12-7-et-proposition-9-a-v12-7", "changements-V12.7",
    "br-V12.7", "V12.7")
PAGES_CUISINE = {"changements": "cuisine/amenagement/historique.html",
                 **{a: "archive/cuisine-v11.49.html" for a in _FIGEES_V11_49},
                 **{a: "archive/cuisine-v12.7.html" for a in _FIGEES_V12_7}}

REDIRECTIONS = (
    Redirection("entree-amenagement.html", "entree/amenagement/", ANCRES_ENTREE, COUPES, HISTORIQUE_ENTREE),
    # la page de Victor avait en plus « Différences avec la V4.3 », passée dans son Explication
    Redirection("entree-amenagement-victor.html", "entree/amenagement/victor.html",
                {**ANCRES_ENTREE, "differences-avec-la-v4-3": "explication"}, COUPES, HISTORIQUE_ENTREE),
    Redirection("salon-enfilade.html", "salon/enfilade/", ANCRES_ENFILADE, (),
                {"changements": "salon/enfilade/historique.html"}),
    Redirection("chambre-amenagement.html", "chambre/amenagement/", ANCRES_CHAMBRE, (),
                {"changements": "chambre/amenagement/historique.html"}),
    Redirection("cuisine-v13.html", "cuisine/amenagement/", ANCRES_CUISINE, MOTIFS_CUISINE, PAGES_CUISINE),
    Redirection("cuisine-v13-imprimable.html", "cuisine/amenagement/imprimable.html"),
    Redirection("cuisine-v13-maquette.html", "cuisine/amenagement/maquette-3d.html"),
)


def main(argv: list[str] | None = None) -> int:
    return commande(SITE, REDIRECTIONS, RACINE, sys.argv[1:] if argv is None else argv)


if __name__ == "__main__":
    sys.exit(main())
