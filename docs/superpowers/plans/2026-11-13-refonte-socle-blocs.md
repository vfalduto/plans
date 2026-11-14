# Socle des pages : blocs communs de contenu et document de construction

> **Pour les agents d'exécution :** skill requis : `superpowers:subagent-driven-development` (recommandé) ou
> `superpowers:executing-plans`, tâche par tâche. Les étapes se suivent par cases (`- [ ]`). Mode autonome : aucune
> question au client ; une décision imprévue se prend réversible et s'écrit dans le rapport de la tâche.

**But :** que les huit pages à migrer écrivent le même HTML avec les mêmes fonctions : blocs communs des vues
d'aménagement et de l'Explication (S1, l'entrée les utilise sans changer d'un octet), blocs des vues de construction et
un document de construction d'essai vérifié au navigateur (S2), puis un mode d'emploi pour les agents de page.

**Architecture :** des fonctions pures dans `commun/blocs.py` (Plan, Coupes, Iso, Caméra, nommage des rendus,
Explication, achats) et `commun/blocs_construction.py` (Plans, Découpe, Montage, rendus d'un meuble). Un bloc prend des
données et rend une chaîne HTML ; les fonctions `vue_*` rendent une `commun.modele.Vue`. Rien dans `commun/` n'importe
`pieces.*` : dossiers et textes propres à une page passent en argument. Le CSS des nouveaux blocs s'ajoute à la fin de
`commun/site.css`, repris de la maquette ; `commun/site.js` gagne une règle (Mesurer sans objet sur un dessin marqué).

**Pile :** Python 3 (bibliothèque standard), pytest par `uv`, HTML et CSS statiques, `playwright-cli` pour les scripts
de navigateur.

**Spec :** `docs/superpowers/specs/2026-11-13-refonte-site-design.md` (objectifs 1 à 5, « Génération », « Contraintes »,
« À éviter », « Vérification »). Maquette : `/Users/nvi/code/work/personal/plans/maquette/app.html`.

Worktree : `/Users/nvi/code/work/personal/plan-wt/socle`, branche `refonte-socle`. Toute commande commence par
`cd /Users/nvi/code/work/personal/plan-wt/socle && …` (noté `WT` plus bas).

## Contraintes globales

- **Fonctions pures.** Aucun `import pieces` ni `from pieces` dans `commun/` (un test le vérifie, tâche 1). Les
  chemins (dossier des rendus) passent en argument (`pathlib.Path`). Les textes propres à l'entrée restent dans
  `pieces/entree/amenagement/vues.py`.
- **Échappement.** Titres, noms, libellés, cotes, cellules de débit, articles et références : échappés
  (`html.escape(..., quote=True)`). Textes longs (`texte` d'une carte ou d'une zone, `chapo`, `corps` d'une étape,
  `note`, points à vérifier, `outils`, deuxième colonne des matériaux, légende, SVG) : HTML inséré tel quel, à la
  charge de l'appelant.
- **Textes exacts :** « Touchez un meuble pour afficher sa fiche. » ; « Position » ; « Pas encore rendu » ;
  « Sans objet » ; « Montrer sur le plan » ; « Coupe <lettre> » et « Iso » (boutons de la fiche d'un meuble) ;
  « yeux à <X> cm, objectif <N> mm » ; calques « Cotes », « Passages libres », « Traits de coupe »,
  « Pièces voisines », « Annotations » ; « Total », « Sous-total », « non chiffré » ; « Outils à réunir » ;
  « Découpe », « Montage » (liens de la fiche de Plans) ; « Comparer », « avec », « <Variante> : pas d'équivalent »
  (déjà dans le gabarit et `site.js`, à ne pas changer).
- **Jamais :** cases à cocher (`<input type="checkbox">`), « Copier la liste », « À venir », « Lecture du plan »,
  « Lecture de la coupe », description d'image à l'écran (texte alternatif seulement), cote écrite en dur dans un bloc.
- **Style :** pas de mode sombre (`prefers-color-scheme`), pas de police à chasse fixe, pas de `text-transform` ni
  d'étiquette en capitales, pas de point médian (« · », U+00B7) dans le code ni les textes produits, pas de flèche
  ajoutée aux liens, pas de motif décoratif. Jetons de `site.css` seulement (`--ink`, `--muted`, `--line`, `--panel`,
  `--paper`, `--actif`, `--sur-actif`, `--ui`, `--texte`, `--hair`).
- **CSS :** seulement des règles ajoutées à la fin de `commun/site.css`, sur des classes qu'aucune page existante
  n'utilise ; aucune règle existante modifiée.
- **Fichiers intouchables :** `pieces/entree/piece.py`, `pieces/entree/amenagement/document.py`, `victor.py`,
  `rendu.py`, `3d/rendu.py`, `commun/rendu_cache.py`, `tests/test_rendu_cache.py`, les recettes `entree-*` du
  `justfile`. `commun/modele.py` et `commun/gabarit.py` : non modifiés par ce plan (voir les décisions). De l'entrée,
  seul `vues.py` change (et `tests/test_entree.py` seulement si un test nommait une fonction déplacée : aucun ne le
  fait aujourd'hui).
- **Critère d'octets (tâches 1 à 4) :**
  ```bash
  cd WT && python3 site.py && git status --short site/entree   # attendu : aucune ligne
  git checkout -- site && git clean -fdq site                    # toujours, après chaque python3 site.py
  ```
  Vérifié avant ce plan : sur `bf0d557`, la première commande ne sort rien. `site/` n'est jamais commité ici.
- **Tests :** `cd WT && uv run -q --no-project --with pytest pytest -q tests` (même chose que `just tests`) : tout
  passe à la fin de chaque tâche.
- **Navigateur :** `cd WT && PORT=<port> SESSION=refonte-socle-<n> tests/navigateur/lancer.sh tests/navigateur/<script>.js`,
  ports 8820 à 8829 seulement, sessions `refonte-socle-*` seulement. Jamais `close-all` ni `kill-all`, jamais la
  session `prod`, jamais les ports 8800 et 8811. `entree.js` (marque `@site reel`) lance `python3 site.py` : remettre
  `site/` ensuite (commande ci-dessus).
- **Git :** commits petits, en français, sur `refonte-socle`, terminés par la ligne `Co-Authored-By` habituelle de la
  session. Pas de `git push`, pas de fusion. `git status` propre en fin de tâche.

## Ce que les pages demandent

Sondé le 13/11/2026 (anciennes pages, générateurs, inventaire de la porte du cellier) ; ces constats ont dicté les signatures.

- **Débit :** colonnes différentes sur chaque page (étagères : Repère, Pièce, Nb, Dimensions, Matière, Tirée de ; enfilade :
  Rep., Pièce, L × l, Ép., Qté, Matière, Où et note ; meuble bas : Rep., Pièce, Qté, Longueur, Largeur, Ép. ; meuble haut :
  …, Usinages et remarques). D'où des colonnes déclarées (`Colonne`). Calepinage : un SVG titré par panneau.
- **Montage :** étapes titrées (étagères), sans titre (enfilade), numérotées 8 à 10 avec résultat, pièces, opérations et un
  dessin du résultat (meuble haut, suite du meuble bas). D'où `Etape(titre, corps, figure)` et un numéro de départ.
- **Achats :** colonnes variées (Poste, Réf., Qté, Prix unit., Total, Source, Magasin, Stock) ramenées par la spec à article,
  référence, quantité, prix, le reste en note ; sections par magasin (étagères), « Les deux meubles » (salle de bain) ; une
  ligne non chiffrée et un prix approché (porte du cellier).
- **Plans :** élévation et iso (étagères) ; cinq dessins et une légende (porte du cellier) ; plan, élévation, coupe, joue…
  (meuble bas). D'où des repères libres. L'iso des meubles de la salle de bain est un SVG axonométrique : Mesurer y ment.
- **Porte du cellier :** une seule `Variante`, d'id vide : rendus sans préfixe. **Chambre :** ni caméra ni rendu (Iso et
  Caméra grisés), élévations dans Coupes. **Salon :** meubles décrits autrement (`ENFILADE` : `y0`, `y1`, `p`, `z1`) : la
  fiche prend un texte de cotes déjà calculé. **`mini_plan`** écrit « Position dans l'entrée » en dur.

## Décisions

- Ruling : un seul bloc `achats` (dans `blocs.py`) sert l'Explication d'un aménagement et la vue Achats d'un meuble — la
  spec demande le même tableau — si faux : un paramètre de plus.
- Ruling : pas de bandeau `.somme` — son chiffre « magasins » ne vaut que pour les étagères ; le total général suffit —
  si faux : trois règles CSS et un paramètre.
- Ruling : Mesurer est sans objet sur un SVG marqué `data-mesure="non"` (posé par `vue_plans`) et sur tout élément qui
  n'est pas un SVG ; `site.js` cache alors le bouton et éteint la mesure ; `modele.py` et `gabarit.py` inchangés — la
  règle tient en JS et ne touche pas l'entrée (ses vues mesurées sont des SVG) — si faux : un champ `Element.mesure`.
- Ruling : débit à colonnes déclarées ; Plans à repères libres (`elevation`, `iso` par convention de comparaison) — les
  pages diffèrent — si faux : nul.
- Ruling : le document de construction d'essai est dans une pièce à part, « Atelier » (`atelier/etagere/`) ; le `SITE`
  de `tests/fixtures/essai/document.py` ne change pas, seul `construire.py` réunit les deux pièces — dans la même pièce,
  la barre de l'aménagement d'essai prendrait un `<select id="c-doc">`, que `tests/test_gabarit.py` regarde — si faux :
  un script qui compte les pièces du menu s'adapte (tâche 4 le vérifie).
- Ruling : `mini_plan` gagne `aria` (défaut « Position ») ; l'entrée passe « Position dans l'entrée » — si faux : nul.
- Ruling : Iso ou Caméra sans aucun rendu présent donne une vue vide (onglet grisé) plutôt que des éléments inactifs —
  la spec grise ces onglets pour la chambre — si faux : nul pour l'entrée, qui a ses rendus.
- Ruling : le trait d'une `Coupe` est obligatoire, élévation comprise (le mur regardé) — défaut I1 — si faux : une page
  dessine un trait de plus.
- Ruling : prix au format de l'entrée (virgule, zéros finaux retirés, pas de séparateur de milliers : `80 €`, `12,5 €`),
  total arrondi à l'euro par défaut — critère d'octets — si faux : un paramètre de format.
- Ruling : un bloc de section (`principes`, `materiaux`, `achats`, `a_verifier`, `tableau_debit`, `calepinage`,
  `etapes`, `rendus_meuble`) écrit son `<h2>` depuis `titre` ; un bloc de morceau (`tete`, `chiffres`,
  `tableau_achats`, `note_source`) n'en écrit pas — les titres de l'entrée passent par `titre` — si faux : nul.
- Ruling : `Zone.id` est l'identifiant stable ; l'entrée passe son rang (`"0"` à `"4"`) — décision du contrôleur,
  critère d'octets — reste connu de l'entrée.
- Ruling : si `commun/blocs.py` dépasse 320 lignes, la tâche 2 sort l'Explication et les achats dans
  `commun/blocs_lecture.py`, réexportés par `blocs.py` (mêmes noms) — si faux : nul.

## Points d'attention

Cas que la spec implique et qu'un test de tâche tient :
1. Document sans variante (id vide) : rendus `rendus/<clé>.jpg`, jamais `rendus/-<clé>.jpg`. Tâche 1.
2. Pièce sans caméra ni rendu (chambre) : onglets Iso et Caméra grisés, sans erreur. Tâche 1.
3. Ligne d'achat sans prix (porte du cellier) : « non chiffré », hors du total, pas de « 0 € ». Tâche 2.
4. Iso d'un meuble : « Mesurer » caché, mesure éteinte en y passant depuis l'élévation. Tâches 3 et 5.
5. Débit à 390 px : lignes en cartes, aucun défilement horizontal de la page. Tâche 5.
6. Titres avec « & », « < » ou guillemets : échappés dans `data-titre`, `aria-label`, `<h3>`. Tâches 1 et 3.

### Task 1 : Blocs du plan, des coupes et des rendus ; l'entrée les utilise

**Fichiers :**
- Créer : `commun/blocs.py`, `tests/test_blocs.py`
- Modifier : `commun/position.py` (paramètre `aria`), `pieces/entree/amenagement/vues.py`

**Interfaces (produites, reprises telles quelles par les tâches 2 à 6) :**

```python
# commun/blocs.py
CALQUES = (("cotes", "Cotes"), ("passages", "Passages libres"), ("coupes", "Traits de coupe"),
           ("voisines", "Pièces voisines"), ("annotations", "Annotations"))
COINS = ("no", "ne", "so", "se")
MARGE_ISO = 26
INVITE = "Touchez un meuble pour afficher sa fiche."

def nombre(v: float) -> str                      # commun.dessin.f(v) avec une virgule : 2.5 -> "2,5"
def cotes_meuble(m: Mapping[str, float], plateau: bool = False) -> str

# Toutes les classes sont des @dataclass(frozen=True), champs dans cet ordre.
class Zone: id: str; titre: str; emprise: tuple[float, float, float, float]; cotes: str; texte: str; coupe: str = ""; iso: str = ""
#   id stable (data-meuble, #plan?k=<id>) ; emprise x0, y0, x1, y1 en cm ; cotes : cotes_meuble(...) ou texte de la page ;
#   texte HTML ; coupe (lettre) et iso (coin) : boutons de la fiche, seulement si non vides

def zones_svg(zones: Sequence[Zone]) -> str
def vue_plan(svg: str, zones: Sequence[Zone], legende: str,
             calques: Sequence[tuple[str, str]] = CALQUES) -> Vue

class Lieu: sol: Sequence[tuple[float, float]]; portes: Sequence[Mapping]; aria: str
#   le mini-plan « Position » : contour du sol, portes au format de piece.PORTES, aria-label (« Position dans l'entrée »)

def fiche_position(lieu: Lieu, traits: Sequence = (), cones: Sequence = ()) -> str

class Coupe: k: str; nom: str; titre: str; scene: str; trait: tuple[tuple[float, float], tuple[float, float]]
#   k stable (« A », « nord ») ; nom du bouton ; titre de la fiche ; scene SVG ; trait sur le mini-plan, obligatoire

def vue_coupes(coupes: Sequence[Coupe], lieu: Lieu, vide: str = "Sans objet") -> Vue

class Rendu: image: str; masque: str; fichier: Path; existe: bool
#   image et masque : adresses relatives à la page (rendus/<nom>.jpg, rendus/<nom>-masque.png) ; fichier : <dossier>/<nom>.jpg

def rendu(dossier: Path, variante: str, cle: str) -> Rendu
def figure_rendu(r: Rendu, alt: str, filtre: str = "") -> str
def points_iso(enveloppe: tuple[float, float, float, float], marge: float = MARGE_ISO) -> dict[str, tuple]
def vue_iso(dossier: Path, variante: str, lieu: Lieu, points: Mapping[str, tuple],
            alts: Mapping[str, str] | None = None, filtre: str = "", vide: str = "Pas encore rendu") -> Vue
def vue_camera(dossier: Path, variante: str, lieu: Lieu, cameras: Sequence[Camera],
               alts: Mapping[str, str] | None = None, filtre: str = "", vide: str = "Pas encore rendu") -> Vue
```

`commun/position.py` : `mini_plan(sol, portes, traits=(), cones=(), aria="Position") -> str` (`aria-label`, échappé).

**Ce que rend chaque bloc** (les chaînes sont celles que `vues.py` écrit aujourd'hui ; les reproduire à l'octet) :

- `nombre`, `cotes_meuble` : `vues._nombre` et `vues._cotes` déplacées sans changement (« longueur × profondeur,
  h hauteur », puis « , dessous à z0 » si `z0` ; profondeur `caisson` si donnée ; `plateau=True` ajoute `m["plateau"]`).
- `zones_svg` : un `<rect class="zone" data-meuble="{id}" x y width height rx="2" tabindex="0" role="button"
  aria-label="{titre}"/>` par zone, nombres par `commun.dessin.f`, comme `vues._zones`.
- `vue_plan` : `Vue("plan", [Element(k="", nom="Plan", titre="Plan", scene=svg, fiche=<modèles>)],
  fiche=<fiche>, outils=("zoom", "mesure"))`. Modèles : un `<template data-meuble="{id}" data-titre="{titre}"><p
  class="cotes">{cotes}</p><p>{texte}</p><div class="actions">{liens}</div></template>` par zone, « cm » ajouté aux
  cotes qui commencent par un chiffre, liens `<a class="btn" href="#coupes?k={coupe}">Coupe {coupe}</a>` puis
  `<a class="btn" href="#iso?k={iso}">Iso</a>`, chacun seulement si non vide (`vues._modeles`). Fiche :
  `<div class="fiche-meuble"><p>{INVITE}</p></div><h3>Calques</h3><div class="calques">` + un `<button type="button"
  data-calque="{id}" aria-pressed="true">{nom}</button>` par calque + `</div><h3>Légende</h3>{legende}`
  (`vues._fiche_plan`).
- `fiche_position` : `<h3>Position</h3><div class="mini">{mini_plan(lieu.sol, lieu.portes, traits, cones,
  lieu.aria)}</div>`.
- `vue_coupes` : un `Element(k, nom, titre, scene)` par coupe ; fiche `fiche_position(lieu, traits=[(k, trait)…])` ;
  `outils=("zoom", "mesure")` ; liste vide : `Vue("coupes", [], vide=vide)`.
- `rendu` : `nom = f"{variante}-{cle}"` si `variante`, sinon `cle` ; `image = f"rendus/{nom}.jpg"`,
  `masque = f"rendus/{nom}-masque.png"`, `fichier = dossier / f"{nom}.jpg"`, `existe = fichier.exists()`. C'est la
  seule fonction qui sait nommer un rendu (Iso, Caméra, Explication, rendus d'un meuble passent par elle).
- `figure_rendu` : `""` si `not r.existe` ; sinon `<figure class="cadre rendu"><img src="{image}" alt="{alt}"
  draggable="false">` puis, si `filtre`, `<img class="calque" src="{image}" alt="" aria-hidden="true"
  draggable="false" style="filter:url(#filtre-{filtre});-webkit-mask-image:url({masque});mask-image:url({masque})">`,
  puis `</figure>` (`vues._figure`).
- `points_iso` : `vues._coins_iso` sur une enveloppe donnée (`x0, y0, x1, y1`) : `{coin: (loc, centre)}` dans l'ordre
  de `COINS`.
- `vue_iso` : un élément par coin de `COINS`, `k=coin`, `nom=coin.upper()`, `titre=f"Vue iso {coin.upper()}"`,
  `actif = rendu(dossier, variante, f"iso_{coin}").existe`, scène `figure_rendu(…, alt, filtre)` (alt :
  `alts[f"iso_{coin}"]`, sinon `f"Vue isométrique, coin {coin.upper()}"`), vide si inactif ; fiche
  `fiche_position(lieu, cones=[(k, *points[k], False)` pour chaque coin actif`])`. Aucun coin rendu : `Vue("iso", [],
  vide=vide)`.
- `vue_camera` : un élément par caméra, dans l'ordre donné, `k=c.id`, `nom=titre=c.nom`, alt `alts[c.id]` sinon
  `c.nom`, fiche d'élément `<p class="cotes">yeux à {nombre(c.yeux)} cm, objectif {nombre(c.focale)} mm</p>` (« yeux à
  … cm, » omis si `yeux` est `None`, « objectif … mm » omis si `focale` est `None`, pas de `<p>` si les deux manquent) ;
  fiche de vue `fiche_position(lieu, cones=[(c.id, c.loc[:2], c.cible[:2], False)` pour toutes les caméras`])`. Aucune
  caméra, ou aucune rendue : `Vue("camera", [], vide=vide)`.

**Dans `vues.py` après la tâche** (correspondance) : `CALQUES`, `COINS`, `MARGE_ISO` → `blocs` ; `_nombre` →
`nombre` ; `_cotes` → `cotes_meuble` ; `_zones` → une fonction `_zones(M, D) -> list[Zone]` (ids `str(i)`, titre et
texte de `D.principes(M)`, emprise et cotes de `_zone`) puis `zones_svg` ; `_modeles`, `_fiche_plan`, `_vue_plan` →
`vue_plan(svg, zones, dessin_principale.legende())` ; `_vue_coupes` → liste de `Coupe` (nom `f"{lettre} {sujet}"`,
titre `f"Coupe {lettre}-{lettre} : {sujet}"`, trait de `_trait`) puis `vue_coupes` ; `_rendu_existe`, `_figure` →
`rendu`, `figure_rendu` ; `_coins_iso` → `points_iso(<enveloppe de piece.MURS>)` ; `_fiche_position` →
`fiche_position` ; `_vue_iso`, `_vue_camera` → `vue_iso`, `vue_camera` (`alts=dict(M.RENDUS)`, `filtre="teinte"`,
caméras `CAMERAS_PRISES` prises dans `piece.CAMERAS`) ; `_alt` disparaît. Restent : `VARIANTES`, `TRAITS`,
`SAILLIE_PORTE`, `RENDUS_SITE`, `CAMERAS_PRISES`, `_trait`, `_emprise_porte`, `_zone`, un `LIEU = Lieu(piece.SOL,
piece.PORTES, "Position dans l'entrée")`, toute l'Explication (tâche 2), `vues()`. `_article` appelle
`figure_rendu(rendu(RENDUS_SITE, cle, "iso_so"), …, filtre="teinte")` à la place de `_figure`.

- [ ] **Étape 1 : écrire les tests d'abord**, dans `tests/test_blocs.py` (outil `tests.outils.balises`) :
  - `test_cotes_meuble` : `{"x0": 0, "x1": 95, "y0": 0, "y1": 38, "z1": 45}` → `"95 × 38, h 45"` ;
    `{"x0": 0, "x1": 110, "y0": 0, "y1": 40, "z0": 204, "z1": 234}` → `"110 × 40, h 30, dessous à 204"` ;
    `caisson=35` remplace la profondeur ; `plateau=True` avec `plateau=2.5` → `"…, h 47,5"`.
  - `test_zones_svg_identifiant_stable` : `Zone(id="banc", titre="Banc & coffre", emprise=(10, 20, 105, 58), …)` →
    un `rect.zone` de `data-meuble="banc"`, `x="10" y="20" width="95" height="38"`, `aria-label="Banc &amp; coffre"`.
  - `test_vue_plan` : invite exacte dans `vue.fiche` ; cinq `button[data-calque]` dans l'ordre de `CALQUES`, tous
    `aria-pressed="true"` ; légende recopiée ; un `template[data-meuble="banc"]` de `data-titre` « Banc & coffre »
    échappé ; `<p class="cotes">95 × 38, h 45 cm</p>` ; liens `#coupes?k=A` « Coupe A » et `#iso?k=so` « Iso » ; une
    zone sans `coupe` n'a pas de lien de coupe ; cotes « vantail de 80 » sans « cm » ; `outils == ("zoom", "mesure")` ;
    aucun `input`.
  - `test_vue_coupes_position` : deux `Coupe` (« A », « nord ») → `k` dans l'ordre, fiche avec « Position » et un
    `line.sec` par coupe de même `data-k`, `aria-label` du SVG égal à `lieu.aria` ; `vue_coupes([], lieu).elements ==
    []` et `vide == "Sans objet"`.
  - `test_rendu_nommage` (`tmp_path`) : `rendu(tmp_path, "victor", "iso_so")` → `image ==
    "rendus/victor-iso_so.jpg"`, `masque == "rendus/victor-iso_so-masque.png"`, `existe is False` ; après création du
    fichier, `True` ; `rendu(tmp_path, "", "iso_so").image == "rendus/iso_so.jpg"` et `masque ==
    "rendus/iso_so-masque.png"`.
  - `test_figure_rendu` : sans filtre, une seule `img` ; avec `filtre="teinte"`, la seconde a `class="calque"`,
    `alt=""` et `filter:url(#filtre-teinte)` et le masque dans son `style` ; rendu absent → `""`.
  - `test_vue_iso_coins` (`tmp_path` avec `a-iso_so.jpg` et `a-iso_no.jpg`) : `k == ["no", "ne", "so", "se"]`, actifs
    `no` et `so` seulement, scène vide pour `ne` ; `g.pdv` de la fiche : `["no", "so"]` ; alt donné par `alts` sinon
    « Vue isométrique, coin SO ».
  - `test_vue_iso_sans_rendu` et `test_vue_camera_sans_camera` : `elements == []`, `vide == "Pas encore rendu"` (et
    `vide="Sans objet"` transmis).
  - `test_vue_camera` : `Camera("banc", "Assis sur le banc", (10, 20, 112), (40, 300, 112), focale=17, yeux=112)` et
    une seconde caméra sans image → `<p class="cotes">yeux à 112 cm, objectif 17 mm</p>`, deux `g.pdv` (toutes les
    caméras), la seconde `actif is False` ; `yeux=None` → « objectif 17 mm » seul.
  - `test_points_iso` : `points_iso((0, 0, 100, 200))["so"] == ((-26, 226), (50.0, 100.0))`.
  - `test_commun_n_importe_pas_pieces` : aucun fichier `commun/*.py` ne contient `import pieces` ni `from pieces`.
  - `tests/test_position.py` : ajouter `test_mini_plan_aria` (`aria="Position dans la chambre"` dans l'`aria-label`).
- [ ] **Étape 2 :** `uv run -q --no-project --with pytest pytest -q tests/test_blocs.py tests/test_position.py` →
  échecs (`ModuleNotFoundError: commun.blocs`).
- [ ] **Étape 3 :** écrire `commun/blocs.py` (docstring : rôle, rien de `pieces`, nommage des rendus) et `aria` de
  `mini_plan` ; les tests de l'étape 1 passent.
- [ ] **Étape 4 :** brancher `vues.py` sur les blocs selon la correspondance ci-dessus ; retirer le code devenu mort.
- [ ] **Étape 5 :** tous les tests passent ; critère d'octets : `git status --short site/entree` vide ; remettre `site/`.
- [ ] **Étape 6 :** commit « Socle : blocs communs du plan, des coupes et des rendus ».

### Task 2 : Blocs de l'Explication et des achats ; l'entrée les utilise

**Fichiers :** Modifier `commun/blocs.py`, `pieces/entree/amenagement/vues.py`, `tests/test_blocs.py`.

**Interfaces :** consomme `rendu`, `figure_rendu`, `nombre` (tâche 1). Produit, dans `commun/blocs.py` :

```python
def tete(chapo: str, liens: Sequence[tuple[str, str]] = (), figure: str = "") -> str   # liens : (href, libellé)
def chiffres(stats: Sequence[tuple[str, str]]) -> str                                 # (valeur, légende)

class Carte: titre: str; texte: str; meuble: str = ""      # texte HTML ; meuble = Zone.id, ajoute « Montrer sur le plan »

def principes(cartes: Sequence[Carte], titre: str = "Principe") -> str
def materiaux(lignes: Sequence[tuple[str, str]], titre: str = "Matériaux") -> str

class Achat: article: str; reference: str; quantite: float; unitaire: float | None; note: str = ""
#   unitaire en euros, None : « non chiffré » ; note HTML (poste, magasin, source, lien), sous l'article
class SectionAchats: titre: str; achats: Sequence[Achat]   # titre "" : pas de <h3>

def euros(montant: float) -> str
def tableau_achats(achats: Sequence[Achat], libelle_total: str = "Total", approx: bool = False,
                   arrondi: bool = True) -> str
def achats(sections: Sequence[SectionAchats], titre: str = "Achats", note: str = "", approx: bool = False,
           arrondi: bool = True) -> str
def a_verifier(points: Sequence[str], titre: str = "À vérifier sur place") -> str
def note_source(texte: str) -> str
def vue_lecture(id: str, contenu: str, vide: str = "Sans objet") -> Vue
```

**Ce que rend chaque bloc :**
- `tete` : sans lien ni figure, `<p class="chapo">{chapo}</p>` ; sinon `<div class="tete-doc"><div><p
  class="chapo">{chapo}</p>` + (si liens) `<p class="actions">` + le premier lien `<a class="btn plein"
  href="{href}">{libellé}</a>`, les suivants `<a class="btn" …>` + `</p>` + `</div>{figure}</div>`.
- `chiffres` : `<dl class="chiffres">` + `<div><dt>{valeur}</dt><dd>{légende}</dd></div>` par paire + `</dl>`.
- `principes` : `<h2>{titre}</h2><ol class="principes">` + `<li><h3>{titre}</h3><p>{texte}</p>{lien}</li>` par carte,
  lien `<a class="btn" href="#plan?k={meuble}">Montrer sur le plan</a>` si `meuble` + `</ol>`.
- `materiaux` : `<h2>{titre}</h2><table><tbody>` + `<tr><th scope="row">{a}</th><td>{b}</td></tr>` + `</tbody></table>`.
- `euros` : `f"{round(m, 2):.2f}".rstrip("0").rstrip(".").replace(".", ",") + " €"`.
- `tableau_achats` : `<div class="defile"><table><thead><tr><th>Article</th><th>Référence</th><th class="d">Qté</th>
  <th class="d">Prix</th></tr></thead><tbody>` + par achat `<tr><td>{article}{<small>note</small> si note}</td><td
  class="num">{reference}</td><td class="num d">{quantité}</td><td class="num d">{euros(quantite * unitaire) ou « non
  chiffré »}</td></tr>` (quantité : `f"{q:g}"` avec une virgule) + `<tr class="total"><td>{libelle_total}</td><td></td>
  <td></td><td class="num d">{"≈ " si approx}{euros(total)}</td></tr></tbody></table></div>` ; `total` : somme des
  lignes chiffrées, `round(total)` si `arrondi`, sinon `round(total, 2)`. C'est la forme de `vues._achats`.
- `achats` : `<h2>{titre}</h2>` puis, pour chaque section, `<h3>{titre}</h3>` si titre et `tableau_achats` ; une seule
  section : libellé « Total » ; plusieurs : libellé « Sous-total », puis `<p class="total-achats"><span>Total</span>
  <span class="num">{"≈ " si approx}{euros(total général)}</span></p>` ; enfin `<p class="remarque">{note}</p>` si
  note. Les arrondis suivent `arrondi`, le total général est arrondi depuis la somme exacte.
- `a_verifier` : `<h2>{titre}</h2><ul class="liste">` + `<li><span>{point}</span></li>` + `</ul>` (pas de case).
- `note_source` : `<p class="remarque">{texte}</p>`.
- `vue_lecture` : `contenu` vide → `Vue(id, [], vide=vide)` ; sinon `Vue(id, [Element(k="", nom=NOMS_VUES[id],
  titre=NOMS_VUES[id], scene=contenu)])`.

**Dans `vues.py` après la tâche :** `_chiffres` → `chiffres` ; `_principes` → `principes(cartes)` avec des `Carte`
construites dans `vues.py` (`meuble` = `str` de la première zone de ce principe, comme aujourd'hui) ; `_achats` →
`achats([SectionAchats("", [Achat(n, r, q, p) for n, r, q, p in M.IKEA])], titre="Achats IKEA pour la penderie",
note=…, approx=…)` suivi de `_portes_caisson` (qui reste) ; `_materiaux` → `materiaux` ; dans `_article`, le chapô et
les deux liens (« Ouvrir le plan » `#plan`, « Voir en iso » `#iso`) → `tete`, « Points à vérifier » → `a_verifier(…,
titre="Points à vérifier")`, la phrase « Repère : … » + source → `note_source` ; `_vue_explication` →
`vue_lecture("explication", …)`. Le tableau « Différences avec la V4.3 » de Victor et `_portes_caisson` restent dans
`vues.py`.

- [ ] **Étape 1 : tests d'abord**, dans `tests/test_blocs.py` :
  - `test_euros` : `80` → `"80 €"`, `12.5` → `"12,5 €"`, `38.97` → `"38,97 €"`, `0.1 + 0.2` → `"0,3 €"`, `100` →
    `"100 €"`, `12345.67` → `"12345,67 €"`.
  - `test_tableau_achats_forme_de_l_entree` : deux achats `(…, 1, 80)` et `(…, 2, 27.5)` → lignes « 80 € » et « 55 € »,
    total `approx=True` → `≈ 135 €` dans `tr.total`, en-têtes exacts Article, Référence, Qté, Prix.
  - `test_achats_sections` : deux sections titrées → deux `<h3>`, deux `tr.total` « Sous-total », un
    `p.total-achats` avec la somme ; une seule section sans titre → pas de `<h3>`, « Total », pas de `total-achats`.
  - `test_achat_non_chiffre` : `unitaire=None` → cellule « non chiffré », total des seules lignes chiffrées, aucun
    « 0 € ».
  - `test_achat_note` : `note="Weldom, réf. magasin"` → `<small>` dans la cellule de l'article ; article « Vis & chevilles »
    échappé.
  - `test_principes_montrer_sur_le_plan` : `Carte(…, meuble="banc")` → `href="#plan?k=banc"` et texte « Montrer sur le
    plan » ; sans `meuble`, pas de lien.
  - `test_tete` : trois formes (chapô seul ; liens, premier `btn plein` ; figure sans lien, pas de `p.actions`).
  - `test_a_verifier_sans_case` : titre par défaut « À vérifier sur place », aucun `input`.
  - `test_vue_lecture` : contenu vide → `elements == []`, `vide == "Sans objet"` ; sinon un élément `k == ""`.
- [ ] **Étape 2 :** les nouveaux tests échouent (`ImportError`) ; écrire les blocs, puis brancher `vues.py`.
- [ ] **Étape 3 :** tous les tests passent ; critère d'octets vide ; remettre `site/`. Si `commun/blocs.py` dépasse 320
  lignes, appliquer le ruling de découpe et le dire.
- [ ] **Étape 4 : scripts de navigateur existants**, l'un après l'autre sur le port 8821, session `refonte-socle-1` :
  `navigation.js`, `comparaison.js`, `options.js`, `redirections.js`, `scene.js`, `entree.js` → chacun sort
  `"ok": true`. Remettre `site/` après `entree.js`.
- [ ] **Étape 5 :** commit « Socle : blocs communs de l'Explication et des achats ».

### Task 3 : Blocs des vues de construction, leur CSS et la règle de Mesurer

**Fichiers :** Créer `commun/blocs_construction.py`, `tests/test_blocs_construction.py`. Modifier `commun/site.css`
(ajout en fin de fichier), `commun/site.js` (abonné `surMontrer` de `brancherScenes`).

**Interfaces :** consomme `rendu`, `nombre`, `vue_lecture`, `achats` (tâches 1 et 2), `commun.gabarit.icone`,
`commun.modele.NOMS_VUES`. Produit :

```python
# commun/blocs_construction.py
# Classes en @dataclass(frozen=True), champs dans cet ordre.
class DessinMeuble: k: str; nom: str; scene: str; mesure: bool = True
#   k : "elevation", "iso" ou un repère stable de la page ; nom du bouton (« Élévation », « Vue iso ») ; scene SVG

def vue_plans(dessins: Sequence[DessinMeuble], titre: str, formule: str = "",
              liens: Sequence[str] = ("decoupe", "montage"), legende: str = "", vide: str = "Sans objet") -> Vue

class Colonne: titre: str; sorte: str = "texte"            # sorte : "repere", "texte", "nombre", "cote", "note"

def tableau_debit(colonnes: Sequence[Colonne], lignes: Sequence[Sequence[str | float]],
                  titre: str = "Liste de débit", sous_titre: str = "") -> str

class Calepin: titre: str; svg: str

def calepinage(calepins: Sequence[Calepin], titre: str = "Calepinage") -> str

class Etape: titre: str; corps: str; figure: str = ""       # titre "" : pas de <h3> ; corps HTML ; figure : SVG du résultat

def etapes(liste: Sequence[Etape], titre: str = "Montage", outils: str = "", debut: int = 1) -> str
def rendus_meuble(dossier: Path, variante: str, rendus: Sequence[tuple[str, str]], titre: str = "Rendus") -> str
```

Une vue Découpe, Montage, Achats ou Explication se fait par `vue_lecture(id, <blocs concaténés>)` : pas de `vue_*`
propre à ces vues.

**Ce que rend chaque bloc** (balisage de la maquette, `app.html` lignes 990 à 1012) :
- `vue_plans` : un `Element(k=d.k, nom=d.nom, titre=titre, scene=…)` par dessin ; si `d.mesure` est faux et que la
  scène commence par `<svg`, ` data-mesure="non"` est inséré juste après ce `<svg`. Fiche de vue : `<p
  class="cotes">{formule}</p>` si formule, puis si liens `<div class="actions">` + `<a class="btn"
  href="#{id}">{icone(id)}{NOMS_VUES[id]}</a>` par id + `</div>`, puis `<h3>Légende</h3>{legende}` si légende.
  `outils=("zoom", "mesure")` si un dessin au moins est mesurable, sinon `("zoom",)`. Aucun dessin : `Vue("plans", [],
  vide=vide)`. Le gabarit pose déjà les boutons de segment quand il y a plus d'un dessin.
- `tableau_debit` : `<h2>{titre}</h2>` + `<p class="sous-titre">{sous_titre}</p>` si sous-titre + `<div
  class="debit"><table class="cartes"><thead><tr>` + un `<th>` par colonne (`<th class="d">` pour `nombre`) +
  `</tr></thead><tbody>` + par ligne un `<td>` par cellule selon la sorte : `repere` `<td class="num"><b>v</b></td>`,
  `texte` `<td>v</td>`, `nombre` `<td class="num d" data-l="×">v</td>`, `cote` `<td class="num large"
  data-l="{titre}">v</td>`, `note` `<td class="large remarque" data-l="{titre}">v</td>` + `</tbody></table></div>`.
  Une cellule nombre (`int`, `float`) s'écrit par `nombre` ; une chaîne est échappée. Ligne de longueur différente du
  nombre de colonnes, ou sorte inconnue : `ValueError`.
- `calepinage` : `""` si vide ; sinon `<h2>{titre}</h2>` + `<figure class="calepin"><figcaption>{titre du
  calepin}</figcaption>{svg}</figure>` par calepin.
- `etapes` : `<h2>{titre}</h2>` + (si outils) `<details class="reunir"><summary>Outils à réunir</summary>{outils}
  </details>` + `<ol class="etapes"` + (si `debut != 1`) ` style="--debut:{debut - 1}"` + `>` + par étape
  `<li><div>{<h3>titre</h3> si titre}{corps}{<figure class="etape-figure">figure</figure> si figure}</div></li>` +
  `</ol>`.
- `rendus_meuble` : figures des rendus présents (`rendu(dossier, variante, cle).existe`), dans l'ordre donné ; aucun :
  `""` ; sinon `<h2>{titre}</h2><div class="duo">` + `<figure><img src="{image}" alt="{alt}" loading="lazy"></figure>`
  par rendu + `</div>`.

**CSS** (à la fin de `site.css`, sous un titre de bloc « Construction : Plans, Découpe, Montage, Achats, rendus ») :
- maquette ligne 225, en `.lecture .cartes td.d,.lecture .cartes th.d{padding-right:18px}` (le préfixe passe devant
  `.lecture td.d`) ;
- maquette lignes 241 à 245 (`.etapes` et ses enfants) telles quelles, le compteur en
  `counter-reset:e var(--debut,0)` ; plus `.etapes .etape-figure{margin:10px 0 0}` et `.etapes .etape-figure
  svg{display:block;width:100%;max-width:520px;height:auto}` ;
- maquette lignes 252 à 254 (`.duo`) telles quelles ;
- `.reunir{margin:0 0 8px}`, `.reunir summary{cursor:pointer;font-weight:600}` (styles en ligne, maquette l. 1006) ;
  `.calepin{margin:18px 0 0}`, `.calepin figcaption{font:600 16px var(--ui);margin:0 0 6px}`, `.calepin
  svg{display:block;width:100%;height:auto}` ;
- `.lecture td > small{display:block;color:var(--muted);font-size:14px;margin-top:2px}` (de `.liste small`, maquette
  ligne 230) ;
- `.total-achats{display:flex;justify-content:space-between;gap:12px;max-width:820px;margin:18px 0 0;padding:10px 0
  0;border-top:2px solid var(--ink);font:700 18px var(--ui);font-variant-numeric:tabular-nums}` ;
- un `@media (max-width:919px){…}` avec la maquette ligne 370 (`.duo` sur une colonne) et lignes 373 à 377 (`.cartes`
  en cartes), sélecteurs gardés.
- Avant d'écrire : `grep -nE '\.(cartes|etapes|etape-figure|duo|debit|calepin|reunir|total-achats)\b' commun/site.css`
  ne sort rien, et `grep -c '<small' site/entree/amenagement/*.html` donne 0 (la règle `td > small` ne touche pas
  l'entrée).

**JS** (`commun/site.js`, dans l'abonné `surMontrer` de `brancherScenes`, après `controleur(el)`) : si la section a
un `.b-mesure`, l'élément affiché est mesurable quand il a un enfant direct `svg:not([data-mesure="non"])`. Sinon :
cacher le `.groupe` qui contient le bouton (`hidden`) et, si le bouton est enfoncé, l'éteindre comme son propre clic
(`aria-pressed="false"`, classe `mesure` retirée de la scène, `mesurer(false)` sur chaque contrôleur, `.bandeau .mes`
caché). Mesurable : montrer le groupe. Commentaire d'une ligne au-dessus. Rien d'autre ne change.

- [ ] **Étape 1 : tests d'abord**, `tests/test_blocs_construction.py` :
  - `test_vue_plans` : dessins `elevation` puis `iso` → `k`, noms des boutons, même `titre` sur les deux ; fiche avec
    `<p class="cotes">` de la formule, liens `href="#decoupe"` « Découpe » et `href="#montage"` « Montage » ;
    `outils == ("zoom", "mesure")` ; page rendue par `commun.gabarit.page_document` (un `Document` de type
    construction monté dans le test) : `.segments` à deux boutons.
  - `test_vue_plans_iso_sans_mesure` : `mesure=False` → `data-mesure="non"` sur le `svg` de l'iso, absent de
    l'élévation ; un seul dessin non mesurable → `outils == ("zoom",)`.
  - `test_vue_plans_liens_et_legende` : `liens=("decoupe",)` → pas de lien Montage ; `legende` → « Légende » ; aucun
    dessin → `elements == []`, `vide == "Sans objet"`.
  - `test_tableau_debit` : six colonnes de la maquette → classes et `data-l` par sorte, `th.d` pour Nb, `2.5` écrit
    `2,5`, « Chêne & pin » échappé ; ligne trop courte et sorte « autre » → `ValueError`.
  - `test_calepinage` : deux calepins → deux `figure.calepin` avec `figcaption` ; liste vide → `""`.
  - `test_etapes` : trois étapes, figure sur la deuxième seulement → trois `li`, une `figure.etape-figure` ; titre
    vide → pas de `<h3>` ; `outils` → `details.reunir` et « Outils à réunir » ; `debut=8` → `style="--debut:7"`.
  - `test_rendus_meuble` (`tmp_path`, document sans variante) : seuls les rendus présents, `src="rendus/vue.jpg"`,
    `loading="lazy"`, alt donné ; aucun présent → `""`.
  - `test_page_construction_sans_case_ni_copier` : page d'un document construit avec ces blocs et `achats` : aucun
    `input`, ni « Copier la liste », ni « · ».
  - `test_classes_des_blocs_ont_une_regle` : chaque classe émise par les blocs de cette tâche (`cartes`, `debit`,
    `large`, `calepin`, `etapes`, `etape-figure`, `reunir`, `duo`, `total-achats`) a une règle dans `site.css`.
  - `test_site_css_sans_interdit` : `site.css` ne contient ni `prefers-color-scheme`, ni `monospace`, ni
    `text-transform`, ni « · ».
- [ ] **Étape 2 :** les tests échouent (module absent) ; écrire `commun/blocs_construction.py`, le CSS, puis le JS.
- [ ] **Étape 3 :** tous les tests passent ; critère d'octets vide ; remettre `site/` ; `scene.js` et
  `comparaison.js` (port 8822, session `refonte-socle-2`) sortent `"ok": true` (Mesurer reste sur le plan d'essai).
- [ ] **Étape 4 :** commit « Socle : blocs des vues de construction, leur CSS et Mesurer sans objet ».

### Task 4 : Document de construction d'essai et site d'essai à deux documents

**Fichiers :** Créer `tests/fixtures/essai/meuble.py`, `tests/test_essai_meuble.py`. Modifier
`tests/fixtures/essai/construire.py` ; les scripts `tests/navigateur/*.js` existants seulement si l'étape 3 l'exige.
`tests/fixtures/essai/document.py` ne change pas.

**Interfaces :** consomme les blocs des tâches 1 à 3. Produit, dans `meuble.py` : `VARIANTES`, `vues(variante: str)
-> dict[str, Vue]`, `DOCUMENT = Document("atelier", "etagere", "Étagère", "construction", VARIANTES, vues)`,
`SITE = Site((Piece("atelier", "Atelier", (DOCUMENT,)),))`. Dans `construire.py` : `construire(sortie: Path = SORTIE)
-> Path` écrit les pages des deux documents avec `Site(document.SITE.pieces + meuble.SITE.pieces)`.

**Le document** (une étagère murale ; toutes ses longueurs viennent d'un dict `TABLETTES = {"actuelle": (120, 80, 80),
"rangs": (100, 100), "escalier": (60, 90, 120)}` et de constantes `PROFONDEUR = 32`, `EPAISSEUR = 2.7`, jamais d'une
cote recopiée dans un texte) :

| Variante | id, nom, version | Plans | Découpe | Montage | Achats | Explication |
|---|---|---|---|---|---|---|
| 1 | `actuelle`, « Actuelle », V1.2 (deux changements) | `elevation` (mesurable), `iso` (`mesure=False`) | débit à six colonnes (Repère, Pièce, Nb, Dimensions (cm), Matière, Tirée de) et un calepin | trois étapes, la deuxième avec une figure, `outils` | deux sections, « Magasin A » et « Magasin B » | `tete` (chapô, lien `#plans` « Plans détaillés »), `chiffres` (formule, repères, étapes, total) |
| 2 | `rangs`, « Rangs », V0.3 | `elevation`, `iso` | débit | vide : « Sans objet » | une section sans titre | `tete`, `chiffres` |
| 3 | `escalier`, « Escalier », V0.1 | `elevation` seulement | débit | trois étapes sans figure | une section, une ligne non chiffrée | `tete`, `chiffres` |

- Élévations : `viewBox="0 0 300 140"` pour les trois, tablettes de largeur `TABLETTES[variante]`, `fill` en attribut,
  `aria-label` « Élévation, variante <Nom> » ; iso : `viewBox="0 0 300 200"`, `aria-label` « Vue iso, variante <Nom> ».
- `vue_plans(…, titre=f"Étagère {nom}", formule=" + ".join(nombre(l) for l in TABLETTES[v]) + " cm",
  liens=<vues non vides parmi decoupe et montage>)`.
- `rendus_meuble` n'est pas appelé (aucune image dans le site d'essai) : il est couvert par la tâche 3.

**`construire.py` :** charger `meuble.py` comme `document.py` (`importlib`), écrire ses trois pages après celles de
l'aménagement, toutes avec le site réuni ; redirections et fichiers communs inchangés ; docstring à jour.

- [ ] **Étape 1 : tests d'abord**, `tests/test_essai_meuble.py` (modules chargés comme `_charger_essai`) :
  - `test_meuble_verifie` : `commun.modele.verifier(DOCUMENT, vues(v))` passe pour les trois variantes ; ordre des vues
    `VUES["construction"]`.
  - `test_meuble_comparaison_plans` : `actuelle` et `rangs` ont `["elevation", "iso"]`, `escalier` `["elevation"]` ;
    même `viewBox` pour les trois élévations.
  - `test_meuble_sans_objet` : `rangs`, Montage vide, `vide == "Sans objet"` ; dans sa page (`page_document`), l'onglet
    `a[data-vue="montage"]` a `aria-disabled="true"` et `title="Sans objet"` ; Plans de `rangs` n'a pas de lien
    `#montage`.
  - `test_meuble_vues_remplies` : dans `actuelle`, Découpe contient `table.cartes` et `figure.calepin`, Montage
    `ol.etapes` (trois `li`), Achats deux « Sous-total » et `p.total-achats`, Explication `dl.chiffres`.
  - `test_meuble_sans_cote_en_dur` : changer `TABLETTES["actuelle"]` (monkeypatch) change la formule de Plans et le
    débit.
  - `test_construire_deux_documents` (`tmp_path`) : `construire(tmp_path)` écrit `essai/amenagement/index.html`,
    `b.html`, `c.html`, `atelier/etagere/index.html`, `rangs.html`, `escalier.html` ; le menu de chaque page lie les
    deux documents ; la barre de l'aménagement garde `<span class="doc">` (pas de `#c-doc`).
- [ ] **Étape 2 :** les tests échouent (module absent) ; écrire `meuble.py`, puis adapter `construire.py`.
- [ ] **Étape 3 : scripts existants sur le site d'essai à deux documents.** Lire d'abord, dans chaque script, ce qui
  dépend du menu ou du nombre de documents (`grep -nE 'rail|arbre|piece|c-doc|aria-current' tests/navigateur/*.js`).
  Puis lancer `navigation.js`, `comparaison.js`, `options.js`, `redirections.js`, `scene.js` (port 8823, session
  `refonte-socle-3`) : chacun `"ok": true`. Un échec dû à la pièce ajoutée se corrige dans le script par
  l'adaptation la plus petite (un sélecteur restreint à `essai`), écrite dans le rapport de la tâche ; un autre échec
  se diagnostique (`superpowers:systematic-debugging`) avant toute retouche.
- [ ] **Étape 4 :** tous les tests passent ; critère d'octets vide ; remettre `site/`.
- [ ] **Étape 5 :** commit « Essai : un document de construction à trois variantes ».

### Task 5 : Script de navigateur du document de construction

**Fichiers :** Créer `tests/navigateur/construction.js` (site d'essai, sans marque `@site reel`).

**Interfaces :** consomme le site d'essai de la tâche 4 : `${BASE}/atelier/etagere/`, `rangs.html`, `escalier.html`.

Forme des scripts existants (`async page => {…}` qui renvoie `{ok, echecs, erreurs}`) ; recopier d'`entree.js`
`preparer`, `attendre`, `partie`, `debordements` (l. 46 à 61) et le contexte sans JavaScript (l. 308 à 333).
À 1440 × 900, 1100 × 800 et 390 × 844, chaque vérification dans sa `partie` :

1. **Onglets :** à l'ouverture de `atelier/etagere/`, onglets dans l'ordre Plans, Découpe, Montage, Achats,
   Explication, Plans courant, section `plans` seule visible ; un clic sur chaque onglet montre sa section et écrit
   `#<vue>` dans l'adresse.
2. **Variante :** sur `#decoupe`, choisir « Rangs » dans `#c-variante` → adresse `…/rangs.html#decoupe`, section
   Découpe visible ; idem de `rangs.html#plans?k=iso` vers « Actuelle » → `…/etagere/#plans?k=iso`.
3. **Comparaison :** `#plans?k=elevation&c=rangs` → deux `.etiq-var` (« Actuelle », « Rangs »), un `.element.b` et
   une `.poignee` ; `#plans?k=iso&c=escalier` → étiquette « Escalier : pas d'équivalent », aucun clone ; « avec »
   visible (trois variantes).
4. **Pas de Comparer** : sur `#decoupe`, `#montage`, `#achats`, `#explication`, `#c-comp` caché (`checkVisibility`
   faux), y compris arrivé avec `&c=rangs` dans l'adresse (et aucun `.etiq-var`).
5. **Onglet grisé :** `rangs.html` : `a[data-vue="montage"]` a `aria-disabled="true"` et `title="Sans objet"` ; un clic
   ne change pas la vue ; `rangs.html#montage` montre `.vide` « Sans objet ».
6. **Mesurer :** sur `#plans?k=elevation`, le bouton « Mesurer » est visible ; l'enfoncer, puis passer au segment
   « Vue iso » : le bouton est caché et `aria-pressed="false"` ; revenir à l'élévation : bouton visible, éteint.
7. **Largeur :** à 390 px, pour chaque vue de chaque variante, `debordements` ne renvoie rien (dont `page`) ; à 1100 et
   1440 px, la barre et la fiche ne débordent pas.
8. **Sans JavaScript** (1440 et 390 px, les trois pages) : `html.sans-js`, les cinq sections visibles l'une sous
   l'autre dans l'ordre, le texte « Liste de débit » et « Sous-total » (actuelle) présents, pas de débordement de
   page.
9. **Console :** `erreurs` vide à la fin (aucune erreur de console ni de page, aucun fichier manquant).

- [ ] **Étape 1 :** écrire le script ; le lancer : `PORT=8824 SESSION=refonte-socle-4 tests/navigateur/lancer.sh
  tests/navigateur/construction.js` → `"ok": true`. Un échec révèle un défaut d'une tâche précédente : le corriger à
  sa place (bloc, CSS, JS), avec son test Python s'il en manque un, et le dire dans le rapport.
- [ ] **Étape 2 :** pour s'assurer que le script attrape un défaut, retirer provisoirement la règle JS de Mesurer
  (tâche 3) : la partie 6 échoue ; remettre la règle, le script repasse.
- [ ] **Étape 3 :** les cinq scripts existants et `entree.js` repassent (port 8825, session `refonte-socle-5`) ;
  remettre `site/` ; tests Python verts.
- [ ] **Étape 4 :** commit « Navigateur : vérification du document de construction ».

### Task 6 : Mode d'emploi pour les agents de page

**Fichiers :** Créer `/Users/nvi/code/work/personal/plan/.superpowers/sdd/2026-11-13-refonte-pages/socle/rapport.md`
(hors dépôt, non commité ; créer le dossier `socle/` s'il manque). Rien dans le dépôt, sauf un défaut trouvé à
l'étape 2.

**Avant d'écrire :** S3 (cache de rendu) est fusionné. Lire `commun/rendu_cache.py`, les recettes du `justfile` qui
l'appellent et le rapport de S3 (chemin donné par le contrôleur ; à défaut, `grep -l rendu_cache` dans
`/Users/nvi/code/work/personal/plan/.superpowers/sdd/*/*/rapport.md`). Si `git diff bf0d557 -- commun/rendu_cache.py`
est vide, S3 manque : écrire la partie 4 depuis le code présent, titre suivi de « (avant S3) ».

**Contenu, 150 lignes au plus, en français, sans relire le code pour s'en servir :**
1. **En tête** (cinq lignes) : où sont les blocs (`commun/blocs.py`, `commun/blocs_construction.py`), règle « un bloc
   prend des données et rend du HTML ou une `Vue` », règle d'échappement, rien de `pieces` dans `commun/`.
2. **Pour chaque bloc** des tâches 1 à 3 : nom, signature exacte, ce qu'il rend (balise et classe de tête), un exemple
   d'appel d'une à trois lignes. Regrouper par vue : Plan, Coupes, Iso, Caméra, Explication, Plans, Découpe, Montage,
   Achats.
3. **Rendus :** `rendu(dossier, variante, cle)`, le nommage `rendus/<variante>-<clé>.jpg`, `-masque.png`, et
   `rendus/<clé>.jpg` sans variante ; les clés (`iso_<coin>`, l'id de la caméra, une clé libre pour les rendus d'un
   meuble) ; le dossier à passer (`site/<piece>/<document>/rendus`, en chemin absolu depuis le fichier de la page,
   comme `RENDUS_SITE` dans `pieces/entree/amenagement/vues.py`).
4. **Cache de rendu et recettes :** comment un document déclare son cache et ses recettes `just` (depuis S3).
5. **Document d'essai de construction :** ce que montre `tests/fixtures/essai/meuble.py` (tableau des trois
   variantes), comment le voir (`python3 tests/fixtures/essai/construire.py`, puis `python3 -m http.server` sur
   `cache/essai-site` sur un port à soi), ce que vérifie `construction.js`.
6. **Pièges :** ceux des points d'attention de ce plan, l'identifiant de meuble stable (`Zone.id`, pas le rang :
   l'entrée garde son rang, cas connu), `Document.css` qui réunit le CSS de toutes les variantes (défaut C1), une
   `Coupe` toujours avec son trait (I1), les cotes par `cotes_meuble` ou calculées (I3), pas de point médian (m5).

- [ ] **Étape 1 :** écrire le rapport ; `wc -l` ≤ 150.
- [ ] **Étape 2 : chaque exemple s'exécute.** Extraire les exemples dans un script du dossier temporaire de la
  session (pas dans le dépôt), précédé des imports qu'ils supposent, et le lancer depuis `WT` avec
  `PYTHONPATH=WT python3 <script>` : sortie sans erreur. Comparer chaque signature écrite à `inspect.signature` de la
  fonction (même script) : aucune différence. Un exemple faux se corrige dans le rapport ; un défaut du code trouvé
  ainsi se corrige dans le dépôt avec son test, commité à part (« Socle : … »).
- [ ] **Étape 3 :** relire le rapport en se mettant à la place d'un agent de page qui ne lira que lui : chaque vue
  de son type de document a son bloc, chaque texte exact y figure.

---
