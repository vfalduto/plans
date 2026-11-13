"""Construction de site/ : pages des documents, historiques, journal, accueil, fichiers communs et passerelle.

site.py déclare les pièces et les documents, puis appelle `commande`. Tout s'écrit dans `sortie` (site/), rien
ailleurs. Un fichier n'est réécrit que si son contenu change.

site/ n'est jamais vidé : il garde ce qui ne se régénère pas (versions figées et archive/figees.json, rendus copiés
par les recettes de rendu).
"""
import json
import math
import posixpath
import re
import shutil
import struct
import sys
import zlib
from collections import Counter
from html import escape, unescape
from pathlib import Path
from urllib.parse import unquote

from commun.appartement import plan_appartement
from commun.gabarit import MOIS, adresse, menu, page_document, page_simple, relatif
from commun.journal import entrees
from commun.modele import Document, Passerelle, Site, Variante, verifier
from commun.redirections import page_redirection

USAGE = """Construction de site/ :
  python3 site.py                                          construit tout
  python3 site.py <piece>/<document>                       reconstruit ce document, le menu, l'accueil et le journal
  python3 site.py --figer <piece>/<document>[/<variante>]  fige la version en cours d'une variante"""

COMMUNS = ("commun/site.css", "commun/site.js")

# écrits par la construction : la passerelle ne les copie jamais depuis la racine
GENERES = frozenset({"index.html", "journal.html", "favicon.svg", "apple-touch-icon.png", *COMMUNS})

FIGEES = "archive/figees.json"

MOIS_COURTS = ("janv.", "févr.", "mars", "avr.", "mai", "juin", "juil.", "août", "sept.", "oct.", "nov.", "déc.")


class CibleInconnue(ValueError):
    """Document, variante ou commande introuvable."""


# ------------------------------------------------------------------ écriture

def _e(texte) -> str:
    return escape(str(texte), quote=True)


def _ecrire(chemin: Path, contenu: str | bytes) -> None:
    donnees = contenu.encode("utf-8") if isinstance(contenu, str) else contenu
    if chemin.is_file() and chemin.read_bytes() == donnees:
        return
    chemin.parent.mkdir(parents=True, exist_ok=True)
    chemin.write_bytes(donnees)


def _copier(source: Path, cible: Path) -> None:
    """Copie avec la date de la source ; saute la copie si la cible a déjà la même taille et la même date."""
    if cible.is_file():
        s, c = source.stat(), cible.stat()
        if s.st_size == c.st_size and s.st_mtime_ns == c.st_mtime_ns:
            return
    cible.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source, cible)


def _fichier(sortie: Path, adr: str) -> Path:
    """Fichier d'une adresse sous site/ : un dossier (« …/ ») est servi par son index.html."""
    return sortie / (adr + "index.html" if adr == "" or adr.endswith("/") else adr)


# ------------------------------------------------------------------ dates et versions

def _date_longue(date: str) -> str:
    j, m, a = date.split("/")
    return f"{int(j)} {MOIS[int(m) - 1]} {a}"


def _date_courte(date: str) -> str:
    j, m, _ = date.split("/")
    return f"{int(j)} {MOIS_COURTS[int(m) - 1]}"


def _depuis_iso(date_iso: str) -> str:
    a, m, j = date_iso.split("-")
    return f"{j}/{m}/{a}"


def _cle_version(version: str) -> tuple:
    """« V11.49 » → (11, 49), pour trier les versions de la plus récente à la plus ancienne."""
    return tuple(int(n) for n in re.findall(r"\d+", version))


def _pluriel(n: int, mot: str) -> str:
    return f"{n} {mot}{'' if n == 1 else 's'}"


# ------------------------------------------------------------------ passerelle

ATTRIBUT = re.compile(r"""\b(?:src|href)\s*=\s*(["'])(.*?)\1""", re.S | re.I)
SCHEMA = re.compile(r"^[a-z][a-z0-9+.-]*:", re.I)


def _references(html: str) -> list[str]:
    """Chemins relatifs des attributs src et href, sans fragment ni requête (ni #…, http…, data:…, /…)."""
    res = []
    for _, v in ATTRIBUT.findall(html):
        v = unescape(v).strip()
        if not v or v.startswith(("#", "/")) or SCHEMA.match(v):
            continue
        v = unquote(v.split("#", 1)[0].split("?", 1)[0])
        if v:
            res.append(v)
    return res


def copier_passerelle(racine: Path, sortie: Path, exclues: set[str]) -> list[str]:
    """Recopie dans `sortie`, au même chemin, les pages pas encore migrées et les fichiers locaux qu'elles citent.

    Pages : chaque *.html de la racine (sauf index.html) et de archive/. `exclues` : chemins (relatifs à la racine)
    jamais copiés, ni comme page ni comme fichier cité. Renvoie les chemins de la passerelle, triés."""
    racine, sortie = Path(racine).resolve(), Path(sortie).resolve()
    hors = set(exclues) | {"index.html"}
    pages = sorted(racine.glob("*.html")) + sorted((racine / "archive").glob("*.html"))
    fichiers: dict[str, Path] = {}
    for page in pages:
        rel = page.relative_to(racine).as_posix()
        if rel in hors:
            continue
        fichiers[rel] = page
        dossier = posixpath.dirname(rel)
        for ref in _references(page.read_text(encoding="utf-8", errors="replace")):
            cible = posixpath.normpath(posixpath.join(dossier, ref))
            if cible in hors or cible in fichiers or any(p.startswith(".") for p in cible.split("/")):
                continue   # exclu, déjà vu, hors de la racine (« .. ») ou caché (.git)
            source = racine / cible
            if not source.is_file():
                continue
            vrai = source.resolve()
            if vrai.is_relative_to(racine) and not vrai.is_relative_to(sortie):
                fichiers[cible] = source
    for rel, source in fichiers.items():
        _copier(source, sortie / rel)
    return sorted(fichiers)


# ------------------------------------------------------------------ icônes

# favicon de la maquette (plans/maquette/favicon.svg) : la maison sur le fond de la navigation
FAVICON = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64">
<rect width="64" height="64" rx="10" fill="#000000c7"/>
<path d="M14 30 32 15l18 15" fill="none" stroke="#EEF5F0" stroke-width="5" stroke-linecap="round" stroke-linejoin="round"/>
<path d="M19 27v20h26V27" fill="none" stroke="#EEF5F0" stroke-width="5" stroke-linejoin="round"/>
<rect x="28" y="35" width="8" height="12" fill="#F2CF4A"/>
</svg>
"""

# les mêmes formes, pour apple-touch-icon.png (repère de 64)
TOIT = ((14, 30), (32, 15), (50, 30))     # bouts et angle arrondis
MURS = ((19, 27), (19, 47), (45, 47), (45, 27))   # bouts droits, angles arrondis
PORTE = (28, 35, 36, 47)                  # x0, y0, x1, y1
DEMI_TRAIT = 2.5
PAPIER, TAPIS_ALPHA = (0xEE, 0xF0, 0xEC), 0xC7 / 255   # #000000c7 posé sur le papier, comme la navigation
TRAIT, REPERE = (0xEE, 0xF5, 0xF0), (0xF2, 0xCF, 0x4A)


def _boite(x, y, cx, cy, hx, hy):
    qx, qy = abs(x - cx) - hx, abs(y - cy) - hy
    return math.hypot(max(qx, 0), max(qy, 0)) + min(max(qx, qy), 0)


def _segment_rond(x, y, a, b):
    lx, ly = b[0] - a[0], b[1] - a[1]
    t = max(0.0, min(1.0, ((x - a[0]) * lx + (y - a[1]) * ly) / (lx * lx + ly * ly)))
    return math.hypot(x - a[0] - t * lx, y - a[1] - t * ly) - DEMI_TRAIT


def _segment_droit(x, y, a, b):
    lx, ly = b[0] - a[0], b[1] - a[1]
    long = math.hypot(lx, ly)
    ux, uy = lx / long, ly / long
    px, py = x - a[0], y - a[1]
    return _boite(px * ux + py * uy, -px * uy + py * ux, long / 2, 0, long / 2, DEMI_TRAIT)


def _distance_maison(x, y):
    d = min(_segment_rond(x, y, a, b) for a, b in zip(TOIT, TOIT[1:]))
    d = min(d, *(_segment_droit(x, y, a, b) for a, b in zip(MURS, MURS[1:])))
    return min(d, *(math.hypot(x - v[0], y - v[1]) - DEMI_TRAIT for v in MURS[1:-1]))


def _melange(fond, couleur, part):
    return tuple(round(f + (c - f) * part) for f, c in zip(fond, couleur))


def _png(cote: int, lignes: bytes) -> bytes:
    def bloc(genre, donnees):
        return struct.pack(">I", len(donnees)) + genre + donnees + struct.pack(">I", zlib.crc32(genre + donnees))
    return (b"\x89PNG\r\n\x1a\n" + bloc(b"IHDR", struct.pack(">IIBBBBB", cote, cote, 8, 2, 0, 0, 0))
            + bloc(b"IDAT", zlib.compress(lignes, 9)) + bloc(b"IEND", b""))


def icone_apple(cote: int = 180) -> bytes:
    """apple-touch-icon.png : la maison du favicon, à fond perdu (iOS arrondit lui-même les coins)."""
    fond = tuple(round(c * (1 - TAPIS_ALPHA)) for c in PAPIER)
    k = 64 / cote   # unités du favicon par pixel
    px0, py0, px1, py1 = PORTE
    lignes = bytearray()
    for j in range(cote):
        lignes.append(0)
        for i in range(cote):
            x, y = (i + 0.5) * k, (j + 0.5) * k
            couleur = fond
            if 9 < x < 55 and 9 < y < 53:
                couleur = _melange(couleur, TRAIT, max(0.0, min(1.0, 0.5 - _distance_maison(x, y) / k)))
                porte = _boite(x, y, (px0 + px1) / 2, (py0 + py1) / 2, (px1 - px0) / 2, (py1 - py0) / 2)
                couleur = _melange(couleur, REPERE, max(0.0, min(1.0, 0.5 - porte / k)))
            lignes += bytes(couleur)
    return _png(cote, bytes(lignes))


def _fichiers_communs(racine: Path, sortie: Path) -> None:
    for rel in COMMUNS:
        if (racine / rel).is_file():
            _copier(racine / rel, sortie / rel)
        else:
            print(f"{rel} absent : non copié dans site/", file=sys.stderr)
    _ecrire(sortie / "favicon.svg", FAVICON)
    _ecrire(sortie / "apple-touch-icon.png", icone_apple())


# filtre du journal par pièce ; sans JavaScript, le choix reste caché et tout le journal se lit
FILTRE = """<script>
(() => {
  const choix = document.getElementById("filtre-piece");
  if (!choix) return;
  const filtrer = () => {
    for (const li of document.querySelectorAll(".fil li[data-piece]"))
      li.hidden = choix.value !== "" && li.dataset.piece !== choix.value;
    for (const j of document.querySelectorAll(".journee")) j.hidden = !j.querySelector("li:not([hidden])");
  };
  choix.closest("label").hidden = false;
  choix.addEventListener("change", filtrer);
  filtrer();
})();
</script>"""


# ------------------------------------------------------------------ documents et historiques

def _trouver(site: Site, chemin: str) -> Document | Passerelle:
    parties = chemin.strip("/").split("/")
    if len(parties) == 2:
        for piece in site.pieces:
            for doc in piece.documents:
                if (piece.id, doc.id) == tuple(parties):
                    return doc
    raise CibleInconnue(f"« {chemin} » : document inconnu (attendu : <piece>/<document>)")


def _ecrire_variante(site: Site, doc: Document, variante: Variante, sortie: Path) -> Path:
    vues = doc.generer(variante.id)
    verifier(doc, vues)
    chemin = _fichier(sortie, adresse(doc, variante.id))
    _ecrire(chemin, page_document(site, doc, variante, vues))
    return chemin


def _adresse_historique(doc: Document) -> str:
    return f"{doc.piece}/{doc.id}/historique.html"


def _lire_figees(sortie: Path) -> dict:
    f = sortie / FIGEES
    return json.loads(f.read_text(encoding="utf-8")) if f.is_file() else {}


def _cle(doc: Document, variante: Variante) -> str:
    return f"{doc.piece}/{doc.id}/{variante.id}"


def _figees(doc: Document, variante: Variante, table: dict) -> list[tuple[str, str]]:
    """Versions figées d'une variante : celles qu'elle déclare, puis celles de archive/figees.json."""
    liste = list(variante.figees)
    for version, chemin in table.get(_cle(doc, variante), []):
        if version not in {v for v, _ in liste}:
            liste.append((version, chemin))
    return sorted(liste, key=lambda f: _cle_version(f[0]), reverse=True)


def _ecrire_historique(site: Site, doc: Document, table: dict, sortie: Path) -> None:
    """Pour chaque variante : sa version en cours, ses versions figées avec leur date, puis ses changements."""
    depuis = _adresse_historique(doc)
    piece = next(p for p in site.pieces if p.id == doc.piece)
    blocs = []
    for v in doc.variantes:
        h = [f"<h2>{_e(v.nom)}</h2>"] if len(doc.variantes) > 1 else []
        h.append(f'<p class="sous-titre">Version en cours : <a href="{_e(relatif(adresse(doc, v.id), depuis))}">'
                 f'{_e(v.version)}</a></p>')
        dates = {c.version: c.date for c in reversed(v.changements)}
        figees = _figees(doc, v, table)
        if figees:
            items = "".join(
                f'<li><a href="{_e(relatif(chemin, depuis))}">{_e(version)}</a>'
                + (f' <span class="date">{_date_longue(dates[version])}</span>' if version in dates else "") + "</li>"
                for version, chemin in figees)
            h.append(f'<h3>Versions figées</h3><ul class="figees">{items}</ul>')
        if v.changements:
            lignes = "".join(f'<li><div class="quand"><b>{_e(c.version)}</b>{_date_courte(c.date)}</div>'
                             f'<div><p>{_e(c.texte)}</p></div></li>' for c in v.changements)
            h.append(f'<h3>Changements</h3><ol class="fil">{lignes}</ol>')
        blocs.append(f'<section class="variante">{"".join(h)}</section>')
    titre = f"{piece.nom} › {doc.nom} : historique"
    _ecrire(sortie / depuis, page_simple(site, titre, "".join(blocs), depuis, courant=(doc.piece, doc.id)))


RAIL = re.compile(r'<nav class="rail tapis" id="rail".*?</nav>', re.S)


def _rafraichir_menus(site: Site, sortie: Path, sauf: tuple[str, str]) -> None:
    """Remplace le menu des pages déjà construites des autres documents (version affichée, documents ajoutés)."""
    for piece in site.pieces:
        for doc in piece.documents:
            if not isinstance(doc, Document) or (doc.piece, doc.id) == sauf:
                continue
            for depuis in [adresse(doc, v.id) for v in doc.variantes] + [_adresse_historique(doc)]:
                f = _fichier(sortie, depuis)
                if f.is_file():
                    neuf = menu(site, (doc.piece, doc.id), depuis)
                    _ecrire(f, RAIL.sub(lambda _: neuf, f.read_text(encoding="utf-8"), count=1))


# ------------------------------------------------------------------ journal et accueil

def _ecrire_journal(site: Site, racine: Path, sortie: Path) -> None:
    lignes = entrees(site, racine)
    ids = {p.nom: p.id for p in site.pieces}
    comptes = Counter(ids[e.piece] for e in lignes)
    jours: dict[str, list] = {}
    for e in lignes:
        jours.setdefault(e.date_iso, []).append(e)
    choix = f'<option value="">Toutes les pièces ({len(lignes)})</option>' + "".join(
        f'<option value="{_e(p.id)}">{_e(p.nom)} ({comptes[p.id]})</option>' for p in site.pieces if comptes[p.id])
    corps = [f'<p class="chapo">{_pluriel(len(lignes), "changement")} en {_pluriel(len(jours), "jour")} de travail.</p>',
             f'<label class="filtre" hidden>Pièce <select id="filtre-piece">{choix}</select></label>']
    for jour, es in jours.items():
        items = "".join(
            f'<li data-piece="{_e(ids[e.piece])}"><div class="quand"><b>{_e(e.version)}</b></div><div>'
            f'<div class="ou"><a href="{_e(e.lien)}">{_e(e.piece)} › {_e(e.document)}'
            f'{", " + _e(e.variante) if e.variante else ""}</a></div><p>{_e(e.texte)}</p></div></li>' for e in es)
        corps.append(f'<section class="journee"><h2 class="jour">{_date_longue(_depuis_iso(jour))}</h2>'
                     f'<ol class="fil">{items}</ol></section>')
    corps.append(FILTRE)
    _ecrire(sortie / "journal.html", page_simple(site, "Journal des changements", "".join(corps), "journal.html"))


def _ecrire_accueil(site: Site, sortie: Path) -> None:
    documents = sum(len(p.documents) for p in site.pieces)
    corps = (f'<div class="accueil"><p class="chapo">{_pluriel(len(site.pieces), "pièce")}, '
             f'{_pluriel(documents, "document")}. Touchez une pièce pour ouvrir ses plans.</p>'
             f'<div class="tapis-plan tapis">{plan_appartement(site)}</div></div>')
    _ecrire(sortie / "index.html", page_simple(site, "Plans de l'appartement", corps, "index.html"))


# ------------------------------------------------------------------ construction

def _ecrire_redirections(redirections, sortie: Path) -> None:
    for r in redirections:
        _ecrire(sortie / r.ancienne, page_redirection(r, r.ancienne))


def construire(site: Site, redirections, racine: Path, sortie: Path, seulement: str | None = None) -> None:
    """Écrit site/ : passerelle, fichiers communs, pages et historiques des documents, journal et accueil.

    `seulement` (« <piece>/<document> ») : ce document, le menu des autres pages déjà construites, l'accueil et le
    journal. Chaque `Redirection` écrit une page à l'ancienne adresse, exclue de la passerelle."""
    racine, sortie = Path(racine), Path(sortie)
    exclues = {r.ancienne for r in redirections} | GENERES
    if seulement is None:
        copier_passerelle(racine, sortie, exclues)
        _ecrire_redirections(redirections, sortie)
        documents = [d for p in site.pieces for d in p.documents if isinstance(d, Document)]
    else:
        cible = _trouver(site, seulement)
        if isinstance(cible, Passerelle):
            copier_passerelle(racine, sortie, exclues)
            _ecrire_redirections(redirections, sortie)
            documents = []
        else:
            documents = [cible]
            _rafraichir_menus(site, sortie, sauf=(cible.piece, cible.id))
    _fichiers_communs(racine, sortie)
    table = _lire_figees(sortie)
    for doc in documents:
        for v in doc.variantes:
            _ecrire_variante(site, doc, v, sortie)
        _ecrire_historique(site, doc, table, sortie)
    _ecrire_journal(site, racine, sortie)
    _ecrire_accueil(site, sortie)


# ------------------------------------------------------------------ versions figées

BARRE = re.compile(r'<header class="barre" id="barre">.*?</header>', re.S)
CHOIX_DOCUMENT = re.compile(r'<select class="nu" id="c-doc".*?</select>', re.S)
VARIANTES = re.compile(r'(<script type="application/json" id="variantes">).*?(</script>)', re.S)
# choix de variante, « Comparer », « avec » : (balise, marque dans la balise ou son contenu)
COMPARAISON = (("label", 'id="c-variante"'), ("button", 'id="c-comp"'), ("label", "b-avec"))


def _retirer(html: str, balise: str, marque: str) -> str:
    """Retire le premier élément `balise` (sans imbrication) qui contient `marque`."""
    motif = rf"<{balise}\b(?:(?!</{balise}>).)*?{re.escape(marque)}(?:(?!</{balise}>).)*</{balise}>"
    return re.sub(motif, "", html, count=1, flags=re.S)


def _rebaser(url: str, depuis: str, vers: str) -> str:
    """`url`, écrite pour la page `depuis`, vue depuis la page `vers` (les deux relatives à site/)."""
    if not url or url.startswith(("#", "/")) or SCHEMA.match(url):
        return url
    chemin, suite = re.match(r"([^?#]*)(.*)", url, re.S).groups()
    if not chemin:
        return url
    cible = posixpath.normpath(posixpath.join(posixpath.dirname(depuis), chemin))
    if chemin.endswith("/") or posixpath.basename(chemin) in (".", ".."):
        cible = "" if cible == "." else cible + "/"
    return relatif(cible, vers) + suite


def _page_figee(site: Site, doc: Document, variante: Variante, html: str, depuis: str, vers: str) -> str:
    """La page d'une variante, écrite pour `depuis`, telle qu'elle se lit dans archive/<nom>/ (`vers`).

    - `body` porte `data-figee="<version>"` ;
    - plus de choix de variante, de « Comparer » ni de « avec », et #variantes ne garde que cette variante ;
    - le menu est refait depuis l'archive ; la pastille de version et le choix du document mènent aux pages en
      cours (historique.html du document, autres documents de la pièce) ;
    - les sections des vues ne changent pas : leurs rendus/ sont copiés à côté."""
    debut, main, reste = html.partition('<main class="contenu" id="contenu">')
    contenu, fin_main, fin = reste.rpartition("</main>")

    def barre(m):
        b = m.group(0)
        for balise, marque in COMPARAISON:
            b = _retirer(b, balise, marque)
        b = CHOIX_DOCUMENT.sub(lambda s: re.sub(
            r'value="([^"]*)"', lambda v: f'value="{_e(_rebaser(unescape(v.group(1)), depuis, vers))}"', s.group(0)), b)
        return re.sub(r'href="([^"]*)"', lambda h: f'href="{_e(_rebaser(unescape(h.group(1)), depuis, vers))}"', b)

    debut = RAIL.sub(lambda _: menu(site, (doc.piece, doc.id), vers), debut, count=1)
    debut = BARRE.sub(barre, debut, count=1)
    debut = debut.replace("<body", f'<body data-figee="{_e(variante.version)}"', 1)
    seule = json.dumps([[variante.id, variante.nom, "./"]], ensure_ascii=False).replace("<", "\\u003c")
    fin = VARIANTES.sub(lambda m: m.group(1) + seule + m.group(2), fin, count=1)
    return debut + main + contenu + fin_main + fin


def figer(site: Site, racine: Path, sortie: Path, cible: str) -> Path:
    """Copie la page en cours d'une variante et ses rendus/ dans archive/<piece>-<document>[-<variante>]-<version>/.

    La variante est la première si `cible` ne la nomme pas ; son id n'entre dans le nom du dossier que si ce n'est
    pas la première (comme dans les adresses). La version est mise en minuscules, comme les archives existantes
    (entree-amenagement-v3.3.html). L'entrée [version, chemin] s'ajoute à archive/figees.json, sous la clé
    <piece>/<document>/<variante>, une seule fois par version. La page est d'abord régénérée depuis les sources, puis
    adaptée à l'archive par `_page_figee` (pas de comparaison, aucun lien mort)."""
    sortie = Path(sortie)
    parties = cible.strip("/").split("/")
    doc = _trouver(site, "/".join(parties[:2])) if len(parties) in (2, 3) else None
    if not isinstance(doc, Document):
        raise CibleInconnue(f"« {cible} » : pas un document migré (attendu : <piece>/<document>[/<variante>])")
    if len(parties) == 2:
        variante = doc.variantes[0]
    else:
        variante = next((v for v in doc.variantes if v.id == parties[2]), None)
        if variante is None:
            raise CibleInconnue(f"« {cible} » : variante inconnue")
    page = _ecrire_variante(site, doc, variante, sortie)
    premiere = variante.id == doc.variantes[0].id
    nom = "-".join([doc.piece, doc.id] + ([] if premiere else [variante.id]) + [variante.version.lower()])
    dossier = sortie / "archive" / nom
    html = _page_figee(site, doc, variante, page.read_text(encoding="utf-8"), adresse(doc, variante.id),
                       f"archive/{nom}/")
    _ecrire(dossier / "index.html", html)
    rendus = page.parent / "rendus"
    if rendus.is_dir():
        shutil.copytree(rendus, dossier / "rendus", dirs_exist_ok=True)
    table = _lire_figees(sortie)
    liste = [e for e in table.get(_cle(doc, variante), []) if e[0] != variante.version]
    liste.append([variante.version, f"archive/{nom}/"])
    table[_cle(doc, variante)] = sorted(liste, key=lambda e: _cle_version(e[0]), reverse=True)
    lignes = (f" {json.dumps(cle, ensure_ascii=False)}: {json.dumps(v, ensure_ascii=False)}"
              for cle, v in sorted(table.items()))
    _ecrire(sortie / FIGEES, "{\n" + ",\n".join(lignes) + "\n}\n")   # une variante par ligne
    return dossier


def commande(site: Site, redirections, racine: Path, argv: list[str]) -> int:
    """Ligne de commande de site.py ; écrit dans <racine>/site. Renvoie le code de sortie."""
    racine = Path(racine)
    sortie = racine / "site"
    try:
        if argv in (["-h"], ["--help"]):
            print(USAGE)
        elif len(argv) == 2 and argv[0] == "--figer":
            dossier = figer(site, racine, sortie, argv[1])
            construire(site, redirections, racine, sortie, seulement="/".join(argv[1].strip("/").split("/")[:2]))
            print(f"Version figée : {dossier.relative_to(racine).as_posix()}/")
        elif len(argv) <= 1 and not any(a.startswith("-") for a in argv):
            construire(site, redirections, racine, sortie, seulement=argv[0] if argv else None)
            print(f"site/ construit{' pour ' + argv[0] if argv else ''}.")
        else:
            print(USAGE, file=sys.stderr)
            return 2
    except CibleInconnue as e:
        print(e, file=sys.stderr)
        return 1
    return 0
