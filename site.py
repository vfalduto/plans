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
from pieces.entree.amenagement import document as entree_amenagement

RACINE = Path(__file__).resolve().parent

SITE = Site((
    Piece("cuisine", "Cuisine", (
        Passerelle("cuisine", "amenagement", "Aménagement", "amenagement", "cuisine-v13.html"),
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
        Passerelle("salon", "enfilade", "Enfilade", "construction", "salon-enfilade.html"),
    )),
    Piece("chambre", "Chambre", (
        Passerelle("chambre", "amenagement", "Aménagement", "amenagement", "chambre-amenagement.html"),
    )),
))

# Anciennes adresses devenues des pages de redirection (commun/redirections.py). Les ancres sont celles que le
# sommaire des anciennes pages posait sur leurs titres h2 (slug du texte : « Coupe B-B · mur de la salle de bain » →
# coupe-b-b-mur-de-la-salle-de-bain) ; une ancre absente d'ici mène à la vue par défaut.
ANCRES_ENTREE = {"plan": "plan", "vues-3d": "iso", "principe": "explication", "achats-ikea-penderie": "explication",
                 "materiaux": "explication", "points-a-verifier": "explication"}
COUPES = ((r"^coupe-([a-d])-", "coupes?k={1}"),)
HISTORIQUE_ENTREE = {"changements": "entree/amenagement/historique.html"}

REDIRECTIONS = (
    Redirection("entree-amenagement.html", "entree/amenagement/", ANCRES_ENTREE, COUPES, HISTORIQUE_ENTREE),
    # la page de Victor avait en plus « Différences avec la V4.3 », passée dans son Explication
    Redirection("entree-amenagement-victor.html", "entree/amenagement/victor.html",
                {**ANCRES_ENTREE, "differences-avec-la-v4-3": "explication"}, COUPES, HISTORIQUE_ENTREE),
)


def main(argv: list[str] | None = None) -> int:
    return commande(SITE, REDIRECTIONS, RACINE, sys.argv[1:] if argv is None else argv)


if __name__ == "__main__":
    sys.exit(main())
