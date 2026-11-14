"""Options « choix » de la cuisine/aménagement (Personnaliser) : les états que l'ancienne page changeait par des boutons
posés sur ses dessins. Défauts : ceux de l'ancienne page (1,75 m, entrée fermée, cellier mi-ouvert, coupe C en
transparence). Les dessins (dessins.py) marquent chaque état de son jeton ; aucune ne change les rendus.
"""
from commun.blocs import jeton, si
from commun.modele import Option, Valeur

TAILLE = Option("taille", "Taille de la personne qui cuisine", (), "choix", "175",
                (Valeur("175", "1,75 m"), Valeur("180", "1,80 m"), Valeur("masquee", "masquée")),
                "Visible sur les coupes A et C.")
# les rendus montrent la porte d'entrée fermée, et la porte du cellier selon la caméra : pas ce choix
PORTE_ENTREE = Option("porte-entree", "Porte d'entrée", (), "choix", "fermee",
                      (Valeur("fermee", "fermée"), Valeur("ouverte", "ouverte", rendue=False)), "Visible sur le plan.")
PORTE_CELLIER = Option("porte-cellier", "Porte du cellier", (), "choix", "mi-ouverte",
                       (Valeur("fermee", "fermée", rendue=False), Valeur("mi-ouverte", "mi-ouverte"),
                        Valeur("ouverte", "ouverte", rendue=False)), "Visible sur le plan.")
TRANSPARENCE = Option("transparence", "Porte du cellier sur la coupe C", (), "choix", "oui",
                      (Valeur("non", "opaque"), Valeur("oui", "en transparence")), "Visible sur la coupe C.")
OPTIONS = (TAILLE, PORTE_ENTREE, PORTE_CELLIER, TRANSPARENCE)


def marque(option: Option, code: str) -> str:
    """` data-si="<option>:<code>"`, à poser sur le `<g>` d'un état."""
    return si(jeton(option, code))
