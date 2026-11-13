"""Blocs de lecture d'un document : Explication et achats. Réexportés par `commun.blocs`, sous les mêmes noms.

Un bloc de section (`principes`, `materiaux`, `achats`, `a_verifier`) écrit son `<h2>` depuis `titre` ; un bloc de
morceau (`tete`, `chiffres`, `tableau_achats`, `note_source`) n'en écrit pas. Titres, libellés, articles et
références sont échappés ; les textes longs (`chapo`, `texte` d'une carte, `note`, points à vérifier, deuxième colonne
des matériaux) sont insérés tels quels, à la charge de l'appelant.
"""
from dataclasses import dataclass
from decimal import ROUND_HALF_UP, Decimal
from html import escape
from typing import Sequence

from commun.modele import NOMS_VUES, Element, Vue


def _e(texte):
    return escape(str(texte), quote=True)


def tete(chapo: str, liens: Sequence[tuple[str, str]] = (), figure: str = "") -> str:
    """Chapô de la page ; avec des liens (href, libellé), le premier plein, ou une figure : la tête à deux colonnes."""
    chapo = f'<p class="chapo">{chapo}</p>'
    if not liens and not figure:
        return chapo
    actions = ""
    if liens:
        actions = '<p class="actions">' + "".join(
            f'<a class="btn{" plein" if i == 0 else ""}" href="{_e(h)}">{_e(n)}</a>' for i, (h, n) in enumerate(liens)
        ) + "</p>"
    return f'<div class="tete-doc"><div>{chapo}{actions}</div>{figure}</div>'


def chiffres(stats: Sequence[tuple[str, str]]) -> str:
    """Chiffres clés, paires (valeur, légende)."""
    corps = "".join(f"<div><dt>{_e(v)}</dt><dd>{_e(n)}</dd></div>" for v, n in stats)
    return f'<dl class="chiffres">{corps}</dl>'


@dataclass(frozen=True)
class Carte:
    """Une carte « Principe » : `texte` HTML ; `meuble` (un `Zone.id`) ajoute « Montrer sur le plan »."""
    titre: str
    texte: str
    meuble: str = ""


def principes(cartes: Sequence[Carte], titre: str = "Principe") -> str:
    def lien(c):
        return f'<a class="btn" href="#plan?k={_e(c.meuble)}">Montrer sur le plan</a>' if c.meuble else ""
    corps = "".join(f"<li><h3>{_e(c.titre)}</h3><p>{c.texte}</p>{lien(c)}</li>" for c in cartes)
    return f'<h2>{_e(titre)}</h2><ol class="principes">{corps}</ol>'


def materiaux(lignes: Sequence[tuple[str, str]], titre: str = "Matériaux") -> str:
    """Lignes (poste, texte HTML)."""
    corps = "".join(f'<tr><th scope="row">{_e(a)}</th><td>{b}</td></tr>' for a, b in lignes)
    return f"<h2>{_e(titre)}</h2><table><tbody>{corps}</tbody></table>"


# ------------------------------------------------------------------ Achats
@dataclass(frozen=True)
class Achat:
    """`unitaire` en euros, None : « non chiffré », hors du total ; `note` HTML (poste, magasin, source, lien), sous
    l'article."""
    article: str
    reference: str
    quantite: float
    unitaire: float | None
    note: str = ""


@dataclass(frozen=True)
class SectionAchats:
    """`titre` vide : pas de `<h3>`."""
    titre: str
    achats: Sequence[Achat]


def _demi(montant, pas):
    """`montant` arrondi au `pas` (« 1 », « 0.01 »), demi vers le haut, sur son écriture décimale (2.675 -> 2.68)."""
    return Decimal(str(montant)).quantize(Decimal(pas), rounding=ROUND_HALF_UP)


def euros(montant: float) -> str:
    """Au centime, demi vers le haut ; virgule, zéros finaux retirés, pas de séparateur de milliers : 80 -> « 80 € »,
    12.5 -> « 12,5 € »."""
    return f"{_demi(montant, '0.01')}".rstrip("0").rstrip(".").replace(".", ",") + " €"


def _somme(achats):
    return sum(a.quantite * a.unitaire for a in achats if a.unitaire is not None)


def _arrondi(total, arrondi):
    return _demi(total, "1" if arrondi else "0.01")


def total_achats(sections: Sequence[SectionAchats], approx: bool = False, arrondi: bool = True) -> str:
    """Texte du total général d'`achats` : somme exacte des lignes chiffrées, section par section, puis arrondie."""
    total = _arrondi(sum(_somme(s.achats) for s in sections), arrondi)
    return f'{"≈ " if approx else ""}{euros(total)}'


def tableau_achats(achats: Sequence[Achat], libelle_total: str = "Total", approx: bool = False,
                   arrondi: bool = True) -> str:
    lignes = []
    for a in achats:
        note = f"<small>{a.note}</small>" if a.note else ""
        prix = "non chiffré" if a.unitaire is None else euros(a.quantite * a.unitaire)
        lignes.append(f'<tr><td>{_e(a.article)}{note}</td><td class="num">{_e(a.reference)}</td>'
                      f'<td class="num d">{f"{a.quantite:g}".replace(".", ",")}</td><td class="num d">{prix}</td></tr>')
    total = total_achats([SectionAchats("", achats)], approx, arrondi)
    return ('<div class="defile"><table><thead><tr><th>Article</th><th>Référence</th><th class="d">Qté</th>'
            f'<th class="d">Prix</th></tr></thead><tbody>{"".join(lignes)}'
            f'<tr class="total"><td>{_e(libelle_total)}</td><td></td><td></td>'
            f'<td class="num d">{total}</td></tr></tbody></table></div>')


def achats(sections: Sequence[SectionAchats], titre: str = "Achats", note: str = "", approx: bool = False,
           arrondi: bool = True) -> str:
    """Un tableau par section, « Total » s'il n'y en a qu'une, sinon « Sous-total » et le total général, arrondi depuis
    la somme exacte ; `note` HTML en remarque."""
    libelle = "Total" if len(sections) == 1 else "Sous-total"
    morceaux = [f"<h2>{_e(titre)}</h2>"]
    for s in sections:
        if s.titre:
            morceaux.append(f"<h3>{_e(s.titre)}</h3>")
        morceaux.append(tableau_achats(s.achats, libelle, approx, arrondi))
    if len(sections) > 1:
        morceaux.append(f'<p class="total-achats"><span>Total</span>'
                        f'<span class="num">{total_achats(sections, approx, arrondi)}</span></p>')
    if note:
        morceaux.append(note_source(note))
    return "".join(morceaux)


# ------------------------------------------------------------------ Fin de page
def a_verifier(points: Sequence[str], titre: str = "À vérifier sur place") -> str:
    """Points HTML, en liste simple (pas de case à cocher)."""
    corps = "".join(f"<li><span>{p}</span></li>" for p in points)
    return f'<h2>{_e(titre)}</h2><ul class="liste">{corps}</ul>'


def note_source(texte: str) -> str:
    return f'<p class="remarque">{texte}</p>'


def vue_lecture(id: str, contenu: str, vide: str = "Sans objet") -> Vue:
    """Vue de lecture (Explication, Achats) : un seul élément ; contenu vide : vue vide (onglet grisé)."""
    if not contenu:
        return Vue(id, [], vide=vide)
    return Vue(id, [Element(k="", nom=NOMS_VUES[id], titre=NOMS_VUES[id], scene=contenu)])
