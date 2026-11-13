"""Blocs des vues d'un document de construction (un meuble) : Plans, Découpe, Montage, Achats.

Plans est une vue de scène (`vue_plans`) ; Découpe, Montage, Achats et Explication se font par
`vue_lecture(id, <blocs concaténés>)`. Un bloc de section (`tableau_debit`, `calepinage`, `etapes`, `rendus_meuble`)
écrit son `<h2>` depuis `titre`. Titres, noms, cotes et cellules de débit sont échappés ; les textes longs (`corps`
d'une étape, `outils`, légende, SVG) sont insérés tels quels, à la charge de l'appelant.
"""
from dataclasses import dataclass
from html import escape
from pathlib import Path
from typing import Sequence

from commun.blocs import nombre, rendu
from commun.gabarit import icone
from commun.modele import NOMS_VUES, Element, Vue


def _e(texte):
    return escape(str(texte), quote=True)


# ------------------------------------------------------------------ Plans
@dataclass(frozen=True)
class DessinMeuble:
    """`k` : « elevation », « iso » (repères de la comparaison) ou un repère stable de la page ; `nom` du bouton ;
    `scene` SVG ; `mesure` faux : Mesurer est sans objet sur ce dessin (une iso axonométrique, par exemple)."""
    k: str
    nom: str
    scene: str
    mesure: bool = True


def _scene(d):
    if not d.mesure and d.scene.startswith("<svg"):
        return '<svg data-mesure="non"' + d.scene[len("<svg"):]
    return d.scene


def vue_plans(dessins: Sequence[DessinMeuble], titre: str, formule: str = "",
              liens: Sequence[str] = ("decoupe", "montage"), legende: str = "", vide: str = "Sans objet") -> Vue:
    """Un élément par dessin, même `titre` de fiche ; la fiche : cotes (`formule`), liens vers d'autres vues, légende."""
    if not dessins:
        return Vue("plans", [], vide=vide)
    elements = [Element(k=d.k, nom=d.nom, titre=titre, scene=_scene(d)) for d in dessins]
    fiche = f'<p class="cotes">{_e(formule)}</p>' if formule else ""
    if liens:
        fiche += ('<div class="actions">'
                  + "".join(f'<a class="btn" href="#{i}">{icone(i)}{NOMS_VUES[i]}</a>' for i in liens) + "</div>")
    if legende:
        fiche += f"<h3>Légende</h3>{legende}"
    outils = ("zoom", "mesure") if any(d.mesure for d in dessins) else ("zoom",)
    return Vue("plans", elements, fiche=fiche, outils=outils)


# ------------------------------------------------------------------ Découpe
@dataclass(frozen=True)
class Colonne:
    """`sorte` : « repere », « texte », « nombre », « cote », « detail » ou « note ». En carte (mobile), `repere`,
    `texte` (une seule colonne, le nom de la pièce) et `nombre` forment la première rangée ; `cote`, `detail` et `note`
    prennent chacune une rangée entière, avec leur titre en étiquette."""
    titre: str
    sorte: str = "texte"


SORTES = ("repere", "texte", "nombre", "cote", "detail", "note")


def _cellule(colonne, v):
    texte = nombre(v) if isinstance(v, (int, float)) else _e(v)
    nom = _e(colonne.titre)
    return {
        "repere": f'<td class="num"><b>{texte}</b></td>',
        "texte": f"<td>{texte}</td>",
        "nombre": f'<td class="num d" data-l="×">{texte}</td>',
        "cote": f'<td class="num large" data-l="{nom}">{texte}</td>',
        "detail": f'<td class="large" data-l="{nom}">{texte}</td>',
        "note": f'<td class="large remarque" data-l="{nom}">{texte}</td>',
    }[colonne.sorte]


def tableau_debit(colonnes: Sequence[Colonne], lignes: Sequence[Sequence[str | float]],
                  titre: str = "Liste de débit", sous_titre: str = "") -> str:
    """Liste de débit à colonnes déclarées ; en cartes sur mobile (les `data-l` y nomment les cellules)."""
    for c in colonnes:
        if c.sorte not in SORTES:
            raise ValueError(f"colonne « {c.titre} » : sorte « {c.sorte} » inconnue")
    textes = [c.titre for c in colonnes if c.sorte == "texte"]
    if len(textes) > 1:
        # la carte mobile n'a que trois pistes (repère, pièce, nombre) : une deuxième colonne texte la casserait
        raise ValueError(f"une seule colonne « texte » : déclarer {', '.join(f'« {t} »' for t in textes[1:])}"
                         " en « detail »")
    corps = []
    for ligne in lignes:
        if len(ligne) != len(colonnes):
            raise ValueError(f"ligne {list(ligne)} : {len(ligne)} cellules pour {len(colonnes)} colonnes")
        corps.append("<tr>" + "".join(_cellule(c, v) for c, v in zip(colonnes, ligne)) + "</tr>")
    tete = "".join(f'<th class="d">{_e(c.titre)}</th>' if c.sorte == "nombre" else f"<th>{_e(c.titre)}</th>"
                   for c in colonnes)
    sous = f'<p class="sous-titre">{_e(sous_titre)}</p>' if sous_titre else ""
    return (f'<h2>{_e(titre)}</h2>{sous}<div class="debit"><table class="cartes"><thead><tr>{tete}</tr></thead>'
            f'<tbody>{"".join(corps)}</tbody></table></div>')


@dataclass(frozen=True)
class Calepin:
    """Un panneau et ses pièces : `svg` dessiné par la page."""
    titre: str
    svg: str


def calepinage(calepins: Sequence[Calepin], titre: str = "Calepinage") -> str:
    if not calepins:
        return ""
    figures = "".join(f'<figure class="calepin"><figcaption>{_e(c.titre)}</figcaption>{c.svg}</figure>'
                      for c in calepins)
    return f"<h2>{_e(titre)}</h2>{figures}"


# ------------------------------------------------------------------ Montage
@dataclass(frozen=True)
class Etape:
    """`titre` vide : pas de `<h3>` ; `corps` HTML ; `figure` : SVG du résultat de l'étape."""
    titre: str
    corps: str
    figure: str = ""


def etapes(liste: Sequence[Etape], titre: str = "Montage", outils: str = "", debut: int = 1) -> str:
    """Étapes numérotées à partir de `debut` (la suite d'un autre meuble) ; `outils` HTML, dans un dépliant."""
    reunir = f'<details class="reunir"><summary>Outils à réunir</summary>{outils}</details>' if outils else ""
    style = f' style="--debut:{debut - 1}"' if debut != 1 else ""
    items = []
    for x in liste:
        h3 = f"<h3>{_e(x.titre)}</h3>" if x.titre else ""
        figure = f'<figure class="etape-figure">{x.figure}</figure>' if x.figure else ""
        items.append(f"<li><div>{h3}{x.corps}{figure}</div></li>")
    return f'<h2>{_e(titre)}</h2>{reunir}<ol class="etapes"{style}>{"".join(items)}</ol>'


# ------------------------------------------------------------------ Rendus
def rendus_meuble(dossier: Path, variante: str, rendus: Sequence[tuple[str, str]], titre: str = "Rendus") -> str:
    """Rendus (clé, texte alternatif) présents dans `dossier`, dans l'ordre donné, deux par ligne ; aucun : rien."""
    figures = []
    for cle, alt in rendus:
        r = rendu(dossier, variante, cle)
        if r.existe:
            figures.append(f'<figure><img src="{r.image}" alt="{_e(alt)}" loading="lazy"></figure>')
    if not figures:
        return ""
    return f'<h2>{_e(titre)}</h2><div class="duo">{"".join(figures)}</div>'
