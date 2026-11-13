"""Blocs des vues d'un document : Plan, Coupes, Iso, Caméra, et le nommage des rendus.

Chaque bloc est une fonction pure qui rend du HTML (ou une `Vue`) à partir de ce que la page lui donne : rien ici
n'importe `pieces`, et les chemins (dossier des rendus) arrivent en argument. Titres, noms, libellés et cotes sont
échappés ; les textes longs (`texte` d'une zone, légende, SVG) sont insérés tels quels, à la charge de l'appelant.

Nommage des rendus : `rendu(dossier, variante, cle)` est la seule fonction qui sait nommer un rendu. Le fichier est
`<variante>-<cle>.jpg` (ou `<cle>.jpg` pour un document sans variante, d'id vide), son masque `<…>-masque.png`, et la
page les lit sous `rendus/`.
"""
from dataclasses import dataclass
from html import escape
from pathlib import Path
from typing import Mapping, Sequence

from commun.dessin import f
from commun.modele import Camera, Element, Vue
from commun.position import mini_plan

# Calques du plan : (id, nom). Le JS pose `sans-<id>` sur la section ; les éléments SVG qu'il masque portent ces classes.
CALQUES = (("cotes", "Cotes"), ("passages", "Passages libres"), ("coupes", "Traits de coupe"),
           ("voisines", "Pièces voisines"), ("annotations", "Annotations"))
COINS = ("no", "ne", "so", "se")   # ordre des éléments de l'iso, et des cônes (coins rendus) de sa fiche « Position »
MARGE_ISO = 26                     # cm entre l'enveloppe des murs et le point de vue d'un coin
INVITE = "Touchez un meuble pour afficher sa fiche."


def _e(texte):
    return escape(str(texte), quote=True)


def nombre(v: float) -> str:
    """`commun.dessin.f` avec une virgule : 2.5 -> « 2,5 »."""
    return f(v).replace(".", ",")


def cotes_meuble(m: Mapping[str, float], plateau: bool = False) -> str:
    """Cotes d'un meuble pour sa fiche : « longueur × profondeur, h hauteur », puis « dessous à z0 » s'il est suspendu.
    La longueur est le grand côté de l'emprise ; la profondeur, celle du caisson s'il est donné (`caisson`), sinon le
    petit côté ; la hauteur va du dessous au dessus, plateau compris si la zone le demande."""
    dx, dy = m["x1"] - m["x0"], m["y1"] - m["y0"]
    z0 = m.get("z0", 0)
    h = m["z1"] - z0 + (m["plateau"] if plateau else 0)
    texte = f"{nombre(max(dx, dy))} × {nombre(m.get('caisson', min(dx, dy)))}, h {nombre(h)}"
    return texte + (f", dessous à {nombre(z0)}" if z0 else "")


# ------------------------------------------------------------------ Plan
@dataclass(frozen=True)
class Zone:
    """Un meuble touchable du plan.

    `id` stable (`data-meuble`, `#plan?k=<id>`) ; `emprise` x0, y0, x1, y1 en cm ; `cotes` : `cotes_meuble(...)` ou
    texte de la page ; `texte` HTML ; `coupe` (lettre) et `iso` (coin) : boutons de la fiche, seulement si non vides."""
    id: str
    titre: str
    emprise: tuple[float, float, float, float]
    cotes: str
    texte: str
    coupe: str = ""
    iso: str = ""


def zones_svg(zones: Sequence[Zone]) -> str:
    """Rectangles touchables du plan, un par zone, à poser dans le SVG du plan."""
    rects = []
    for z in zones:
        x0, y0, x1, y1 = z.emprise
        rects.append(f'<rect class="zone" data-meuble="{_e(z.id)}" x="{f(x0)}" y="{f(y0)}" width="{f(x1 - x0)}"'
                     f' height="{f(y1 - y0)}" rx="2" tabindex="0" role="button" aria-label="{_e(z.titre)}"/>')
    return "".join(rects)


def _modeles(zones):
    """Un `<template data-meuble>` par zone : le JS le recopie dans la fiche quand on touche le meuble."""
    modeles = []
    for z in zones:
        cotes = z.cotes + (" cm" if z.cotes[:1].isdigit() else "")
        liens = ""
        if z.coupe:
            liens += f'<a class="btn" href="#coupes?k={_e(z.coupe)}">Coupe {_e(z.coupe)}</a>'
        if z.iso:
            liens += f'<a class="btn" href="#iso?k={_e(z.iso)}">Iso</a>'
        modeles.append(f'<template data-meuble="{_e(z.id)}" data-titre="{_e(z.titre)}"><p class="cotes">{_e(cotes)}</p>'
                       f'<p>{z.texte}</p><div class="actions">{liens}</div></template>')
    return "".join(modeles)


def vue_plan(svg: str, zones: Sequence[Zone], legende: str,
             calques: Sequence[tuple[str, str]] = CALQUES) -> Vue:
    """Vue Plan : le SVG (qui porte déjà `zones_svg(zones)`), une fiche par zone, calques et légende."""
    boutons = "".join(f'<button type="button" data-calque="{_e(k)}" aria-pressed="true">{_e(n)}</button>'
                      for k, n in calques)
    fiche = (f'<div class="fiche-meuble"><p>{INVITE}</p></div>'
             f'<h3>Calques</h3><div class="calques">{boutons}</div>'
             f'<h3>Légende</h3>{legende}')
    element = Element(k="", nom="Plan", titre="Plan", scene=svg, fiche=_modeles(zones))
    return Vue("plan", [element], fiche=fiche, outils=("zoom", "mesure"))


# ------------------------------------------------------------------ Position, Coupes
@dataclass(frozen=True)
class Lieu:
    """Le mini-plan « Position » : contour du sol, portes au format de `piece.PORTES`, aria-label du SVG."""
    sol: Sequence[tuple[float, float]]
    portes: Sequence[Mapping]
    aria: str


def fiche_position(lieu: Lieu, traits: Sequence = (), cones: Sequence = ()) -> str:
    """Fiche « Position » : le mini-plan avec ses traits de coupe ou ses cônes (voir `commun.position.mini_plan`)."""
    return f'<h3>Position</h3><div class="mini">{mini_plan(lieu.sol, lieu.portes, traits, cones, lieu.aria)}</div>'


@dataclass(frozen=True)
class Coupe:
    """`k` stable (« A », « nord ») ; `nom` du bouton ; `titre` de la fiche ; `scene` SVG ; `trait` sur le mini-plan,
    obligatoire (pour une élévation, le mur regardé)."""
    k: str
    nom: str
    titre: str
    scene: str
    trait: tuple[tuple[float, float], tuple[float, float]]


def vue_coupes(coupes: Sequence[Coupe], lieu: Lieu, vide: str = "Sans objet") -> Vue:
    if not coupes:
        return Vue("coupes", [], vide=vide)
    elements = [Element(k=c.k, nom=c.nom, titre=c.titre, scene=c.scene) for c in coupes]
    fiche = fiche_position(lieu, traits=[(c.k, c.trait) for c in coupes])
    return Vue("coupes", elements, fiche=fiche, outils=("zoom", "mesure"))


# ------------------------------------------------------------------ Rendus, Iso, Caméra
@dataclass(frozen=True)
class Rendu:
    """`image` et `masque` : adresses relatives à la page ; `fichier` : le jpg dans le dossier des rendus."""
    image: str
    masque: str
    fichier: Path
    existe: bool


def rendu(dossier: Path, variante: str, cle: str) -> Rendu:
    """Le rendu `cle` de `variante` (sans préfixe si la variante est d'id vide)."""
    nom = f"{variante}-{cle}" if variante else cle
    fichier = dossier / f"{nom}.jpg"
    return Rendu(image=f"rendus/{nom}.jpg", masque=f"rendus/{nom}-masque.png", fichier=fichier,
                 existe=fichier.exists())


def figure_rendu(r: Rendu, alt: str, filtre: str = "") -> str:
    """Le rendu et, si `filtre`, par-dessus sa copie recolorée par `#filtre-<filtre>` à travers son masque ; rien si
    le rendu n'existe pas."""
    if not r.existe:
        return ""
    calque = ""
    if filtre:
        masque = f"url({r.masque})"
        calque = (f'<img class="calque" src="{r.image}" alt="" aria-hidden="true" draggable="false"'
                  f' style="filter:url(#filtre-{filtre});-webkit-mask-image:{masque};mask-image:{masque}">')
    return f'<figure class="cadre rendu"><img src="{r.image}" alt="{_e(alt)}" draggable="false">{calque}</figure>'


def points_iso(enveloppe: tuple[float, float, float, float], marge: float = MARGE_ISO) -> dict[str, tuple]:
    """Point de vue de chaque coin, à `marge` de l'enveloppe (x0, y0, x1, y1), visant son centre : {coin: (loc, centre)}."""
    x0, y0, x1, y1 = enveloppe
    centre = ((x0 + x1) / 2, (y0 + y1) / 2)
    ou = {"no": (x0 - marge, y0 - marge), "ne": (x1 + marge, y0 - marge),
          "so": (x0 - marge, y1 + marge), "se": (x1 + marge, y1 + marge)}
    return {k: (ou[k], centre) for k in COINS}


def vue_iso(dossier: Path, variante: str, lieu: Lieu, points: Mapping[str, tuple],
            alts: Mapping[str, str] | None = None, filtre: str = "", vide: str = "Pas encore rendu") -> Vue:
    """Un élément par coin de `COINS`, inactif s'il n'est pas rendu ; aucun coin rendu : vue vide (onglet grisé)."""
    alts = alts or {}
    elements = []
    for k in COINS:
        cle = f"iso_{k}"
        r = rendu(dossier, variante, cle)
        scene = figure_rendu(r, alts.get(cle, f"Vue isométrique, coin {k.upper()}"), filtre)
        elements.append(Element(k=k, nom=k.upper(), titre=f"Vue iso {k.upper()}", scene=scene, actif=r.existe))
    if not any(e.actif for e in elements):
        return Vue("iso", [], vide=vide)
    # un cône par coin rendu ; le JS pose `ici` sur celui de l'élément affiché (g.pdv[data-k])
    cones = [(e.k, *points[e.k], False) for e in elements if e.actif]
    return Vue("iso", elements, fiche=fiche_position(lieu, cones=cones))


def _optique(c):
    morceaux = []
    if c.yeux is not None:
        morceaux.append(f"yeux à {nombre(c.yeux)} cm")
    if c.focale is not None:
        morceaux.append(f"objectif {nombre(c.focale)} mm")
    return f'<p class="cotes">{", ".join(morceaux)}</p>' if morceaux else ""


def vue_camera(dossier: Path, variante: str, lieu: Lieu, cameras: Sequence[Camera],
               alts: Mapping[str, str] | None = None, filtre: str = "", vide: str = "Pas encore rendu") -> Vue:
    """Un élément par caméra, dans l'ordre donné ; aucune caméra, ou aucune rendue : vue vide (onglet grisé)."""
    alts = alts or {}
    elements = []
    for c in cameras:
        r = rendu(dossier, variante, c.id)
        scene = figure_rendu(r, alts.get(c.id, c.nom), filtre)
        elements.append(Element(k=c.id, nom=c.nom, titre=c.nom, scene=scene, fiche=_optique(c), actif=r.existe))
    if not any(e.actif for e in elements):
        return Vue("camera", [], vide=vide)
    cones = [(c.id, c.loc[:2], c.cible[:2], False) for c in cameras]
    return Vue("camera", elements, fiche=fiche_position(lieu, cones=cones))
