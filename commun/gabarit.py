"""Enveloppe commune des pages de site/ : en-tête, menu, barre, onglets, une section par vue, fiche et outils.

Le balisage suit la maquette validée (plans/maquette/app.html : rail(), barre(), fiche(), outilsZoom, outilMesure,
ICONES). La maquette dessinait une seule vue à la fois ; ici la page est statique et contient toutes les vues, et
commun/site.js n'en montre qu'une. Sans JavaScript (classe `sans-js` sur <html>), les sections se suivent.

Différences de noms avec la maquette : son `main.scene` devient `main.contenu`, et son `.stage` (la zone de dessin)
devient `.scene`.
"""
import dataclasses
import json
import posixpath
from html import escape

from commun.modele import LECTURE, NOMS_VUES, VUES, Document, Passerelle, Site, Variante, Vue

POLICES = ("https://fonts.googleapis.com/css2?family=Fira+Sans:wght@400;500;600;700"
           "&family=Fira+Sans+Condensed:wght@500;600;700&display=swap")

GENRE = {"amenagement": "Aménagement", "construction": "Construction"}

MOIS = ("janvier", "février", "mars", "avril", "mai", "juin", "juillet", "août", "septembre", "octobre",
        "novembre", "décembre")

ICONES = {
    "explication": '<path d="M5 6h14M5 11h14M5 16h9"/>',
    "plan": '<path d="M4 4h16v16H4zM4 12h5M14 4v5"/><path d="M9 12a5 5 0 0 1 5 5"/>',
    "coupes": '<path d="M3 12h18M7 8v8M17 8v8"/><path d="M7 8l-3 2M17 8l3 2"/>',
    "iso": '<path d="M12 3l8 4.5v9L12 21l-8-4.5v-9zM12 12l8-4.5M12 12v9M12 12L4 7.5"/>',
    "camera": '<path d="M4 8h3l2-2h6l2 2h3v11H4z"/><circle cx="12" cy="13.5" r="3.5"/>',
    "plans": '<path d="M4 20V4l16 16zM8 16.5v-4l4 4z"/>',
    "decoupe": '<path d="M4 5h16v14H4zM4 11h10M14 5v14M14 15h6"/>',
    "montage": '<path d="M4 7l2 2 3-4M4 16l2 2 3-4M13 7h7M13 16h7"/>',
    "achats": '<path d="M3 5h3l2 11h10l2-8H7"/><circle cx="9.5" cy="19.5" r="1.2"/>'
              '<circle cx="17" cy="19.5" r="1.2"/>',
    "historique": '<circle cx="12" cy="12" r="8"/><path d="M12 7.5V12l3 2"/>',
    "accueil": '<path d="M4 11.5 12 4l8 7.5V20H4z"/><path d="M10 20v-5h4v5"/>',
    "cuisine": '<path d="M5 10h14v6a3 3 0 0 1-3 3H8a3 3 0 0 1-3-3z"/>'
               '<path d="M3 10h18M9.5 7c0-1.2 1-1.3 1-2.5M14 7c0-1.2 1-1.3 1-2.5"/>',
    "sdb": '<path d="M3 12h18v2a5 5 0 0 1-5 5H8a5 5 0 0 1-5-5z"/>'
           '<path d="M6 12V6.2A2.2 2.2 0 0 1 8.2 4c1 0 1.9.7 2.1 1.7M7 19l-1 2M17 19l1 2"/>',
    "entree": '<path d="M6.5 21V3.5h11V21M4 21h16M14 11.5v2"/>',
    "salon": '<path d="M5.5 11V8a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v3"/>'
             '<path d="M3 13a2 2 0 0 1 4 0v2h10v-2a2 2 0 0 1 4 0v5H3zM6 18v2M18 18v2"/>',
    "chambre": '<path d="M3 19V6M3 15h18v4M21 15v-2a3 3 0 0 0-3-3h-8v5M5.5 11.5h2"/>',
    "amenagement": '<path d="M4 4h16v16H4zM4 12h5M14 4v5"/><path d="M9 12a5 5 0 0 1 5 5"/>',
    "construction": '<path d="M5 4h14v14H5zM12 4v14M9.5 10v2.5M14.5 10v2.5M7 18v2.5M17 18v2.5"/>',
    "variante": '<circle cx="6" cy="5.5" r="2"/><circle cx="18" cy="5.5" r="2"/><circle cx="12" cy="18.5" r="2"/>'
                '<path d="M6 7.5V9a3 3 0 0 0 3 3h6a3 3 0 0 0 3-3V7.5M12 12v4.5"/>',
    "options": '<path d="M4 7h8M16 7h4M4 17h4M12 17h8"/><circle cx="14" cy="7" r="2"/><circle cx="10" cy="17" r="2"/>',
    "reduire": '<path d="M4 5h16v14H4zM9.5 5v14M16 9.5 13.5 12l2.5 2.5"/>',
    "ouvrir": '<path d="M4 5h16v14H4zM9.5 5v14M13.5 9.5 16 12l-2.5 2.5"/>',
    "plus": '<path d="M12 5.5v13M5.5 12h13"/>',
    "moins": '<path d="M5.5 12h13"/>',
    "cadrer": '<path d="M4 9V4h5M15 4h5v5M20 15v5h-5M9 20H4v-5"/>',
    "mesurer": '<path d="M3.5 15.5 15.5 3.5l5 5-12 12zM7.5 14.5 9 16M10.5 11.5 12 13M13.5 8.5 15 10"/>',
    "comparer": '<path d="M12 3v18M8.5 8.5 5 12l3.5 3.5M15.5 8.5 19 12l-3.5 3.5"/>',
    "fermer": '<path d="M6 6l12 12M18 6 6 18"/>',
}


def icone(k: str, classe: str = "") -> str:
    classes = f"ico {classe}" if classe else "ico"
    return f'<svg class="{classes}" viewBox="0 0 24 24" aria-hidden="true">{ICONES[k]}</svg>'


OUTILS_ZOOM = (
    '<div class="groupe">'
    f'<button type="button" data-z="0.7" aria-label="Zoomer" title="Zoomer">{icone("plus")}</button>'
    f'<button type="button" data-z="1.43" aria-label="Dézoomer" title="Dézoomer">{icone("moins")}</button>'
    f'<button type="button" data-z="0" aria-label="Recadrer" title="Recadrer">{icone("cadrer")}'
    '<span class="long">Recadrer</span></button></div>'
)
OUTIL_MESURE = (
    '<div class="groupe"><button type="button" class="b-mesure" aria-pressed="false" aria-label="Mesurer"'
    f' title="Mesurer une distance">{icone("mesurer")}<span class="long">Mesurer</span></button></div>'
)


def _e(texte) -> str:
    return escape(str(texte), quote=True)


def _json(donnees) -> str:
    """JSON à poser dans un <script> : « < » échappé, pour qu'aucun « </script> » ne ferme la balise."""
    return json.dumps(donnees, ensure_ascii=False).replace("<", "\\u003c")


def _date_longue(jjmmaaaa: str) -> str:
    j, m, a = jjmmaaaa.split("/")
    return f"{int(j)} {MOIS[int(m) - 1]} {a}"


# ------------------------------------------------------------------ adresses

def relatif(cible: str, depuis: str) -> str:
    """Chemin de `cible` vu depuis la page `depuis`, les deux relatifs à site/.

    Un chemin qui finit par « / » désigne un dossier, servi par son index.html."""
    dossier = posixpath.dirname(depuis) or "."
    chemin = posixpath.relpath(cible or ".", dossier)
    if cible == "" or cible.endswith("/"):
        return "./" if chemin == "." else chemin + "/"
    return chemin


def adresse(doc: Document | Passerelle, variante_id: str = "") -> str:
    """Adresse sous site/ : `<piece>/<doc>/` pour la première variante, `<piece>/<doc>/<id>.html` pour les autres."""
    if isinstance(doc, Passerelle):
        return doc.page
    ids = [v.id for v in doc.variantes]
    if variante_id and variante_id not in ids:
        raise ValueError(f"{doc.piece}/{doc.id} : variante « {variante_id} » inconnue")
    if not variante_id or variante_id == ids[0]:
        return f"{doc.piece}/{doc.id}/"
    return f"{doc.piece}/{doc.id}/{variante_id}.html"


def _historique(doc: Document) -> str:
    return f"{doc.piece}/{doc.id}/historique.html"


# ------------------------------------------------------------------ menu de gauche

def menu(site: Site, courant: tuple[str, str] | None, depuis: str) -> str:
    """Le menu des pièces et des documents, réduit par défaut ; le document `courant` porte aria-current."""
    arbre = []
    for p in site.pieces:
        ici = courant is not None and courant[0] == p.id
        docs = []
        for d in p.documents:
            genre = GENRE[d.type]
            titre = d.nom if d.nom == genre else f"{d.nom} ({genre.lower()})"
            actuel = ' aria-current="page"' if ici and courant[1] == d.id else ""
            version = (f'<span class="num txt">{_e(d.variantes[0].version)}</span>'
                       if isinstance(d, Document) else "")
            docs.append(f'<li><a href="{_e(relatif(adresse(d), depuis))}" title="{_e(titre)}"{actuel}>'
                        f'{icone(d.type)}<span class="txt">{_e(d.nom)}</span>{version}</a></li>')
        arbre.append(
            f'<li><a class="piece{" ici" if ici else ""}" href="{_e(relatif(adresse(p.documents[0]), depuis))}"'
            f' title="{_e(p.nom)}">{icone(p.id if p.id in ICONES else "plan")}<span class="txt">{_e(p.nom)}</span>'
            f'</a><ul>{"".join(docs)}</ul></li>')
    journal = ' aria-current="page"' if depuis == "journal.html" else ""
    return (
        '<nav class="rail tapis" id="rail" aria-label="Pièces et documents">'
        f'<div class="rail-tete"><a class="rail-accueil" href="{_e(relatif("index.html", depuis))}"'
        f' title="Accueil : plan de l\'appartement">{icone("accueil")}<span class="txt">Plans de l\'appartement</span></a>'
        '<button type="button" class="rail-btn rail-reduire" id="b-rail" aria-expanded="false"'
        ' aria-label="Déplier le menu" title="Déplier le menu">'
        f'{icone("ouvrir", "si-reduit")}{icone("reduire", "si-deplie")}</button>'
        '<button type="button" class="rail-fermer">Fermer</button></div>'
        f'<ul class="arbre">{"".join(arbre)}</ul>'
        f'<div class="rail-pied"><a href="{_e(relatif("journal.html", depuis))}" title="Journal des changements"{journal}>'
        f'{icone("historique")}<span class="txt">Journal des changements</span></a></div>'
        '</nav>'
    )


# ------------------------------------------------------------------ barre du haut

B_MAISON = (f'<button type="button" class="b-menu" id="b-maison" aria-label="Pièces et documents"'
            f' title="Pièces et documents">{icone("accueil")}</button>')


def _barre_document(piece, doc: Document, variante: Variante, vues: dict[str, Vue], depuis: str) -> str:
    if len(piece.documents) > 1:
        choix = "".join(f'<option value="{_e(relatif(adresse(d), depuis))}"{" selected" if d.id == doc.id else ""}>'
                        f'{_e(d.nom)}</option>' for d in piece.documents)
        titre_doc = f'<select class="nu" id="c-doc" aria-label="Document de la pièce">{choix}</select>'
    else:
        titre_doc = f'<span class="doc">{_e(doc.nom)}</span>'

    cases = ""
    if len(doc.variantes) > 1:
        choix = "".join(f'<option value="{_e(v.id)}"{" selected" if v.id == variante.id else ""}>{_e(v.nom)}</option>'
                        for v in doc.variantes)
        cases += (f'<label class="b-case" title="Variante">{icone("variante")}'
                  f'<select class="nu" id="c-variante" aria-label="Variante">{choix}</select></label>')
        cases += ('<button type="button" class="b-case" id="c-comp" aria-pressed="false"'
                  f' title="Comparer avec une autre variante">{icone("comparer")}<span class="lib">Comparer</span></button>')
    if len(doc.variantes) > 2:
        choix = "".join(f'<option value="{_e(v.id)}">{_e(v.nom)}</option>'
                        for v in doc.variantes if v.id != variante.id)
        cases += ('<label class="b-case b-avec" title="Variante comparée" hidden><span class="lib">avec</span>'
                  f'<select class="nu" id="c-autre" aria-label="Variante comparée">{choix}</select></label>')
    titre = "Historique de ce document"
    date = next((c.date for c in variante.changements if c.version == variante.version), None)
    if date:
        titre += f", dernière version le {_date_longue(date)}"
    cases += (f'<a class="b-case version" href="{_e(relatif(_historique(doc), depuis))}" title="{_e(titre)}">'
              f'{icone("historique")}<span class="num">{_e(variante.version)}</span></a>')

    onglets = []
    for i, k in enumerate(VUES[doc.type]):
        vue = vues[k]
        attrs = ' aria-current="page"' if i == 0 else ""
        if vue.elements:
            attrs = f' title="{_e(NOMS_VUES[k])}"' + attrs
        else:
            attrs = f' title="{_e(vue.vide)}" aria-disabled="true"' + attrs
        onglets.append(f'<a href="#{k}" data-vue="{k}"{attrs}>{icone(k)}<span>{_e(NOMS_VUES[k])}</span></a>')
    perso = ""
    if doc.options:
        perso = ('<button type="button" class="b-case b-perso" id="c-options" title="Personnaliser">'
                 f'{icone("options")}<span class="lib">Personnaliser</span>'
                 '<span class="badge" id="n-options" hidden></span></button>')
    return (
        '<header class="barre" id="barre">'
        f'<div class="b-ligne b-haut">{B_MAISON}<div class="b-titre"><h1>{_e(piece.nom)}</h1>'
        f'<span class="sep" aria-hidden="true">›</span>{titre_doc}</div><div class="b-cases">{cases}</div></div>'
        f'<div class="b-ligne b-bas"><nav class="vues" aria-label="Vues du document">{"".join(onglets)}</nav>{perso}</div>'
        '</header>'
    )


def _barre_simple(titre: str) -> str:
    return (f'<header class="barre" id="barre"><div class="b-ligne b-haut">{B_MAISON}'
            f'<div class="b-titre"><h1>{_e(titre)}</h1></div></div></header>')


# ------------------------------------------------------------------ sections des vues

INACTIF = ' disabled title="Pas encore rendu"'


def _fiche(vue: Vue) -> str:
    segments = ""
    if len(vue.elements) > 1:
        boutons = "".join(
            f'<button type="button" data-k="{_e(e.k)}" aria-pressed="{"true" if i == 0 else "false"}"'
            f'{"" if e.actif else INACTIF}>{_e(e.nom)}</button>'
            for i, e in enumerate(vue.elements))
        segments = f'<div class="segments">{boutons}</div>'
    fiches = "".join(f'<div class="fiche-element" data-k="{_e(e.k)}" data-titre="{_e(e.titre)}">{e.fiche}</div>'
                     for e in vue.elements)
    return (f'<aside class="fiche"><button type="button" class="fiche-tete" aria-expanded="false">'
            f'<h2>{_e(vue.elements[0].titre)}</h2><i class="chevron"></i></button>'
            f'<div class="fiche-corps">{segments}{vue.fiche}{fiches}</div></aside>')


def _section(k: str, vue: Vue) -> str:
    def ouvrir(outils):
        return f'<section class="vue" data-vue="{k}" data-outils="{outils}" data-vide="{_e(vue.vide)}">'

    if not vue.elements:
        return f'{ouvrir("")}<p class="vide">{_e(vue.vide)}</p></section>'
    if k in LECTURE:
        return f'{ouvrir("")}<article class="lecture">{"".join(e.scene for e in vue.elements)}</article></section>'
    mesure = "mesure" in vue.outils
    elements = "".join(f'<div class="element" data-k="{_e(e.k)}">{e.scene}</div>' for e in vue.elements)
    return (
        f'{ouvrir("zoom mesure" if mesure else "zoom")}<div class="planche"><div class="scene">{elements}'
        f'<div class="outils">{OUTILS_ZOOM}{OUTIL_MESURE if mesure else ""}</div>'
        '<div class="bandeau"><span class="mes" hidden></span></div></div>'
        f'{_fiche(vue)}</div></section>'
    )


# ------------------------------------------------------------------ pages

def _tete(titre: str, depuis: str) -> str:
    return (
        '<!doctype html>\n<html lang="fr" class="sans-js">\n<head>\n<meta charset="utf-8">\n'
        '<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">\n'
        f'<title>{_e(titre)}</title>\n'
        f'<link rel="icon" href="{relatif("favicon.svg", depuis)}" type="image/svg+xml">\n'
        f'<link rel="apple-touch-icon" href="{relatif("apple-touch-icon.png", depuis)}">\n'
        '<link rel="preconnect" href="https://fonts.googleapis.com">\n'
        '<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>\n'
        f'<link href="{POLICES}" rel="stylesheet">\n'
        f'<link rel="stylesheet" href="{relatif("commun/site.css", depuis)}">\n'
        f'<script src="{relatif("commun/site.js", depuis)}" defer></script>\n'
        '</head>\n'
    )


def _page(titre, depuis, corps_attrs, classes, rail, barre, contenu, variantes, options, noms) -> str:
    return (
        f'{_tete(titre, depuis)}<body{corps_attrs}>\n'
        f'<div class="{classes}" id="app">\n{rail}\n{barre}\n<main class="contenu" id="contenu">{contenu}</main>\n</div>\n'
        f'<script type="application/json" id="variantes">{_json(variantes)}</script>\n'
        f'<script type="application/json" id="options">{_json(options)}</script>\n'
        f'<script type="application/json" id="noms-vues">{_json(noms)}</script>\n'
        '</body>\n</html>\n'
    )


def page_document(site: Site, doc: Document, variante: Variante, vues: dict[str, Vue]) -> str:
    """La page d'une variante d'un document : toutes ses vues, une section chacune, dans l'ordre de VUES."""
    piece = next((p for p in site.pieces if p.id == doc.piece), None)
    if piece is None:
        raise ValueError(f"{doc.piece}/{doc.id} : pièce absente du site")
    depuis = adresse(doc, variante.id)
    titre = f"{piece.nom} › {doc.nom}" + (f", {variante.nom}" if len(doc.variantes) > 1 else "")
    corps_attrs = (f' data-type="{_e(doc.type)}" data-piece="{_e(doc.piece)}" data-document="{_e(doc.id)}"'
                   f' data-variante="{_e(variante.id)}"')
    return _page(
        titre, depuis, corps_attrs, "app rail-reduit",
        menu(site, (doc.piece, doc.id), depuis),
        _barre_document(piece, doc, variante, vues, depuis),
        "".join(_section(k, vues[k]) for k in VUES[doc.type]),
        [[v.id, v.nom, relatif(adresse(doc, v.id), depuis)] for v in doc.variantes],
        [dataclasses.asdict(o) for o in doc.options],
        {k: NOMS_VUES[k] for k in VUES[doc.type]},
    )


def page_simple(site: Site, titre: str, corps: str, depuis: str, courant=None) -> str:
    """Accueil, journal ou historique : le menu, une barre sans onglets et `corps` dans un article de lecture."""
    return _page(
        titre, depuis, ' data-type="simple"', "app rail-reduit sans-onglets",
        menu(site, courant, depuis), _barre_simple(titre),
        f'<article class="lecture">{corps}</article>',
        [], [], {},
    )
