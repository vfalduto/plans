"""Achats communs aux deux meubles de la salle de bain : le magasin, les dates de relevé, le budget, et la section
« Les deux meubles » de la vue Achats (total de chaque meuble et des deux).

MAGASIN, RELEVE_V6 et BUDGET sont copiés de 3d/sdb/modele.py (un test les garde égaux tant qu'il existe). Le total du
meuble haut vient de pieces/sdb/meuble_haut/modele.py.
"""
from html import escape
from typing import Mapping

from commun.blocs import euros, note_source
from pieces.sdb.meuble_bas import modele as B
from pieces.sdb.meuble_haut import modele as H

MAGASIN = dict(nom="Weldom Marseille Saint-Barnabé", adresse="90 rue François Scaramelli, 13012 Marseille",
               tel="04 91 49 27 27", url="https://www.weldom.fr/m/weldom-marseille-saint-barnabe", releve="13/10/2026")
RELEVE_V6 = "26/10/2026"
# V6.0 : budget TTC des deux meubles, consommables et achats faits ailleurs compris ; total accepté par le client
BUDGET = dict(cible=400.00, accepte=428.33, date="26/10/2026",
              decision="il garde tout sauf la fraise de défonceuse, avec le 2ᵉ rouleau de chant et les vis 6 × 90")


def prix(v: float) -> str:
    """Montant toujours au centime, comme l'ancienne page : 296,82 €, 9,00 € (pour les textes repris)."""
    return f"{v:.2f}".replace(".", ",") + " €"


def total_haut() -> float:
    return H.total()


def note_article(q: float, pu: float, stock) -> str:
    """Note d'une ligne d'achat : prix unitaire (quantité autre que 1) et stock lu au magasin."""
    return ", ".join(([f"{q:g} × {euros(pu)}"] if q != 1 else []) + ([f"stock : {stock}"] if stock is not None else []))


def deux_meubles(liens: Mapping[str, str]) -> str:
    """Section « Les deux meubles » ; `liens` : adresses (relatives à la page) des achats de chaque meuble, clés
    « bas » et « haut ». Adresse vide : le meuble de la page qui appelle, écrit sans lien (pas de lien vers soi)."""
    bas, haut = B.total(), H.total()

    def ligne(nom, cle, v):
        lien = f'<a href="{escape(liens[cle], quote=True)}">{nom}</a>' if liens[cle] else nom
        return f'<tr><td>{lien}</td><td class="num d">{euros(v)}</td></tr>'

    mg = MAGASIN
    return ('<h2>Les deux meubles</h2>'
            '<div class="defile"><table><thead><tr><th>Meuble</th><th class="d">Prix du meuble entier</th></tr></thead>'
            f'<tbody>{ligne("Meuble bas", "bas", bas)}{ligne("Meuble haut", "haut", haut)}'
            f'<tr class="total"><td>Total TTC</td><td class="num d">{euros(bas + haut)}</td></tr></tbody></table></div>'
            + note_source(f"Le budget accepté le {BUDGET['date']} était de {prix(BUDGET['accepte'])}, pour l'ancien "
                          "meuble en L et le même meuble haut.")
            + note_source(f"Sauf mention, articles chez {escape(mg['nom'])} ({escape(mg['adresse'])}, {mg['tel']}). "
                          "Stock : nombre affiché sur la fiche produit pour ce magasin, dans la note de l'article (sans "
                          f"note : non lu). Prix TTC relevés en ligne le {mg['releve']}, le {RELEVE_V6} et, pour les "
                          "articles Castorama et IKEA, le 04/11/2026 (stock non lu)."))
