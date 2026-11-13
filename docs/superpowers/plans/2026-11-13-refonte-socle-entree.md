# Refonte du site, étapes 0 et 1 : socle et entrée — plan de travail

> **Pour les agents qui exécutent ce plan :** utiliser superpowers:subagent-driven-development (recommandé) ou
> superpowers:executing-plans pour l'exécuter tâche par tâche. Les étapes se cochent (`- [ ]`).

**But :** publier le site depuis `site/`, avec la navigation, les vues, la comparaison, les options et le journal de
la refonte, puis y migrer l'entrée (variantes Principale et Victor). Toutes les autres pages restent en ligne à leur
adresse actuelle grâce à la passerelle.

**Architecture :**
- **Génération :** les générateurs Python écrivent des pages HTML statiques, une par document et par variante, avec
  toutes les vues en sections. `commun/gabarit.py` écrit l'enveloppe commune.
- **Interaction :** `commun/site.js` ne fait que l'interaction, en lisant des attributs `data-*` ; le contenu est
  entièrement dans le HTML.
- **Construction :** `site.py` déclare les pièces et les documents, puis appelle `commun/construction.py`, qui écrit
  `site/`.
- **Publication :** une GitHub Action publie `site/`.

**Technologies :**
- **Python 3.14**, bibliothèque standard seulement pour les générateurs ;
- **pytest**, lancé par `uv run --with pytest` ;
- **JS et CSS sans dépendance**, repris de la maquette ;
- **Blender 5.2.2 (Cycles)** pour les rendus ;
- **`playwright-cli`** pour les vérifications dans le navigateur ;
- **GitHub Actions** (`upload-pages-artifact@v3`, `deploy-pages@v4`).

**Spécification :** `docs/superpowers/specs/2026-11-13-refonte-site-design.md`.

**Maquette** (référence visuelle et JS à porter) : `/Users/nvi/code/work/personal/plans/maquette/app.html`. Ses
fonctions `dessin`, `vueImage`, `brancherZoom`, `rideau`, `calage`, `bandeau`, `pointsDeVue`, `fiche`/`brancherFiche`,
son CSS et sa table `APPART` sont le point de départ des tâches 4 à 9 et 13.

**Hors de ce plan :**
- **Migrations suivantes :** le salon, la salle de bain, la cuisine et la chambre auront chacun leur plan, écrit au
  début de leur étape.
- **Déplacements qui casseraient les anciens générateurs**, faits après la dernière migration :
  - `3d/rendu.py` vers `commun/` ;
  - `3d/sortie/` vers `cache/` ;
  - `3d/textures/` et `3d/modeles/` vers `ressources/` ;
  - les notes vers `notes/` ;
  - `explorations/` ;
  - la sortie d'`achats/` et de `reddit/`.
- **`commun/materiaux.py` :** il sera créé quand une deuxième pièce aura besoin de matériaux communs.

## Contraintes globales

- **Sources :**
  - les dimensions se calculent depuis les modèles, jamais en dur dans les textes ;
  - `site/` n'est jamais modifié à la main.
- **Écritures :** `site.py` n'écrit que dans `site/` et `cache/`.
- **Données personnelles :** le nom du propriétaire et l'adresse, qui figurent dans le PDF du logement, n'apparaissent
  nulle part.
- **Noms des pièces :** on garde ceux du site, pas ceux du PDF.
- **Couleurs :**
  - papier `#EEF0EC` ;
  - navigation `#000000c7`, posée sur le papier : `background: linear-gradient(var(--tapis), var(--tapis)),
    var(--paper)` ;
  - repère « vous êtes ici » `#F2CF4A`.
  - Pas de mode sombre (aucun `prefers-color-scheme`), pas de quadrillage.
- **Polices :**
  - Fira Sans pour le texte et Fira Sans Condensed pour l'interface et les cotes, chargées depuis Google Fonts comme dans
    la maquette ;
  - chiffres tabulaires ;
  - pas de police à chasse fixe, pas de points médians, pas d'étiquettes en capitales.
- **Mobile :** largeur ≤ 919 px. Onglets fixés en bas, fiche en feuille basse (48 px fermée, au plus 54 % de la hauteur
  ouverte), icône maison en haut à gauche, aucun défilement horizontal à 390 px.
- **Menu de gauche :** 56 px réduit, réduit par défaut, état mémorisé.
- **Ordre des onglets :**
  - aménagement : Plan, Coupes, Iso, Caméra, Explication (ouvre sur Plan) ;
  - construction : Plans, Découpe, Montage, Achats, Explication (ouvre sur Plans).
- **Adresses :**
  - `/<piece>/<document>/` (première variante), `/<piece>/<document>/<variante>.html` ;
  - état dans le fragment : `#<vue>?k=<repère>&c=<variante comparée>`.
- **Textes exacts :**
  - « Comparer » ;
  - « avec » ;
  - « <Variante> : pas d'équivalent » ;
  - « Touchez un meuble pour afficher sa fiche. » ;
  - « Position » ;
  - « Pas encore rendu » ;
  - « Sans objet » ;
  - « Personnaliser » ;
  - « Valeurs d'origine » ;
  - « Journal des changements ».
- **Jamais :**
  - cases à cocher ;
  - « Copier la liste » ;
  - « À venir » ;
  - « Lecture du plan » ;
  - « Lecture de la coupe » ;
  - description d'image affichée (texte alternatif seulement) ;
  - onglet Historique ;
  - plan de repérage dans le menu.
- **Tests :** `just tests` (`uv run -q --no-project --with pytest pytest -q tests`).
- **Navigateur :**
  - `tests/navigateur/lancer.sh <script.js>`, avec une session `playwright-cli` nommée `refonte-essai` ;
  - ne jamais lancer `close-all` ni `kill-all` ;
  - ne jamais toucher la session `prod`.
- **Git :**
  - tout se fait sur la branche `refonte`, fusionnée dans `main` à la fin des parties A et B ;
  - `git push` et le changement de source de GitHub Pages attendent l'accord du client.

## Points d'attention pour la relecture

Ce sont les cas que la spec implique sans les tester. Chacun a son test dans la tâche indiquée.

1. **Un lien partagé avec un état invalide :**
   - les cas : `c` inconnu ou égal à la base, ancien `c=1`, `k` inconnu, vue inconnue ;
   - attendu : l'état valide le plus proche (vue par défaut, premier élément, autre variante pour `c=1`), sans erreur
     de console ;
   - tâches 5 et 7.
2. **La page de la variante comparée ne se charge pas** (lecture en `file://`, 404, réseau) :
   - l'étiquette de droite dit « <Variante> : comparaison indisponible » ;
   - la scène et les outils restent utilisables, sans erreur non rattrapée ;
   - tâche 7.
3. **`localStorage` inaccessible** (navigation privée, accès qui lève une exception) : le menu est réduit, les options
   ont leur valeur d'origine, la page fonctionne. Tâches 5 et 8.
4. **Une vue sans contenu atteinte par l'adresse** (`#iso` sur un document dont Iso est grisé) : la section affiche le
   message de la vue (« Pas encore rendu »), l'onglet reste grisé, la scène ne reste pas vide. Tâche 5.
5. **Une ancienne adresse avec une ancre inconnue, ou sans ancre :** elle mène à la vue par défaut du nouveau document.
   Tâche 10.

---

## Partie A : socle

### Tâche 1 : outillage de test et fonctions de dessin communes

**Fichiers :**
- Créer :
  - `commun/__init__.py` (vide) ;
  - `commun/dessin.py` ;
  - `tests/conftest.py` (ajoute la racine du dépôt à `sys.path`) ;
  - `tests/outils.py` ;
  - `tests/test_dessin.py`.
- Modifier :
  - `justfile` : recette `tests` ;
  - `.gitignore` : `cache/`.

**Interfaces :**
- Produit, dans `commun/dessin.py`, repris à l'identique de `3d/entree/plan.py:34-92` :
  - `virg(v: float, n: int = 1) -> str`
  - `f(v: float) -> str`
  - `rect(x0, y0, x1, y1, cls: str, rx=0) -> str`
  - `text(x, y, s: str, cls="lbl", anchor="middle", extra="") -> str`
  - `rot(x, y) -> str`
  - `cote_h(x0, x1, y, label=None, t=3) -> str`
  - `cote_v(y0, y1, x, label=None, t=3) -> str`
  - `degage(a, b, label=None) -> str`
  - `coin_arrondi(x0, x1, y0, y1, r, cls: str) -> str`
- Produit, dans `tests/outils.py` :
  - `balises(html: str, nom: str, **attrs) -> list[dict]` : les attributs de chaque balise `nom` dont les attributs
    contiennent `attrs`, par `html.parser`. Le mot-clé `classe=` teste un mot de `class`.
  - `charger_site()` : charge `site.py` sous le nom `site_plans` (`importlib.util.spec_from_file_location`).
    `import site` renvoie toujours le module standard : c'est vérifié le 13/11/2026.

- [ ] **Étape 1 : capturer les sorties actuelles.**
  Lancer `cd 3d/entree && python3 -c "import plan as P; print(repr([P.virg(8.1), P.f(12.0), P.f(12.5), P.rect(0, 0, 10, 20, 'w'), P.text(5, 5, 'A-A'), P.cote_h(0, 264, -20), P.cote_v(0, 104, 300, '104'), P.degage((0, 245), (110, 245), '110'), P.coin_arrondi(85, 110, 170, 208, 25, 'cab')]))"`.
  Garder la liste affichée.
- [ ] **Étape 2 : écrire le test qui échoue.**
  Dans `tests/test_dessin.py`, `test_sorties_identiques_a_l_entree` : les neuf appels de l'étape 1, faits sur
  `commun.dessin`, égalent les chaînes capturées (copiées en littéraux).
- [ ] **Étape 3 : lancer le test.**
  `uv run -q --no-project --with pytest pytest -q tests/test_dessin.py` doit échouer sur
  `ModuleNotFoundError: commun.dessin`.
- [ ] **Étape 4 : implémenter.**
  - Copier les neuf fonctions dans `commun/dessin.py`, sans les modifier.
  - Ajouter `tests/conftest.py` et `tests/outils.py`.
  - Ajouter au `justfile` la recette `tests: uv run -q --no-project --with pytest pytest -q tests`.
- [ ] **Étape 5 : relancer.** `just tests` doit passer.
- [ ] **Étape 6 : commiter.**
  `git add commun tests justfile .gitignore && git commit -m "Refonte : fonctions de dessin communes et outillage de test"`

### Tâche 2 : structures de données des documents

**Fichiers :**
- Créer : `commun/modele.py`, `tests/test_modele.py`.

**Interfaces :**
- Produit, dans `commun/modele.py` :
  - **Constantes :**
    - `VUES = {"amenagement": ("plan", "coupes", "iso", "camera", "explication"), "construction": ("plans", "decoupe",
      "montage", "achats", "explication")}` ;
    - `NOMS_VUES` : plan → Plan, coupes → Coupes, iso → Iso, camera → Caméra, explication → Explication, plans → Plans,
      decoupe → Découpe, montage → Montage, achats → Achats ;
    - `COMPARABLES = ("plan", "coupes", "iso", "camera", "plans")` ;
    - `LECTURE = ("explication", "decoupe", "montage", "achats")`, les vues sans scène dessinée.
  - **`Changement(version: str, date: str, texte: str)`**, figée. La date est au format `jj/mm/aaaa`.
  - **`Camera(id, nom, loc: tuple, cible: tuple, ortho: float | None = None, focale: float | None = None, yeux: float |
    None = None, reglages: dict)`**, figée.
    - `reglages` contient `murs`, `expo`, `ombres` et `humain`.
    - Une variante peut changer `reglages`, jamais `loc`, `cible`, `ortho` ni `focale`.
  - **`Valeur(code, nom, couleur, groupe="", note="", lien="")`**.
  - **`Option(id, nom, surfaces, type: "nuancier" | "choix", defaut, valeurs: tuple[Valeur, ...], portee, css="",
    filtre=False, ref=0.80)`**.
    - `css` est la propriété CSS posée sur `:root` (`--india`).
    - `filtre` vaut `True` quand les rendus sont recolorés par masque.
  - **`Element(k, nom, titre, scene, fiche="", actif=True)`** : une coupe, un coin iso, une caméra ou un dessin d'un
    meuble.
  - **`Vue(id, elements: list[Element], fiche="", outils=("zoom",), vide="Pas encore rendu")`**. Une liste
    `elements` vide donne un onglet grisé.
  - **`Variante(id, nom, version, changements: tuple[Changement, ...], figees: tuple[tuple[str, str], ...] = ())`**.
    - `figees` contient des paires (version, chemin sous `site/`).
    - Un document sans variante a une seule `Variante`, d'`id` vide.
  - **`Document(piece, id, nom, type, variantes: tuple[Variante, ...], generer: Callable[[str], dict[str, Vue]],
    options: tuple[Option, ...] = ())`**. `generer(variante_id)` renvoie les vues d'une variante.
  - **`Passerelle(piece, id, nom, type, page: str)`** : un document pas encore migré, désigné par sa page à la racine.
  - **`Piece(id, nom, documents: tuple[Document | Passerelle, ...])`**.
  - **`Site(pieces: tuple[Piece, ...])`**.
  - **`verifier(doc: Document, vues: dict[str, Vue]) -> None`** : lève `ValueError` dans ces cas :
    - une clé hors de `VUES[doc.type]` ;
    - une vue manquante ;
    - deux éléments d'une même vue avec le même `k` ;
    - deux variantes avec le même `id`.

- [ ] **Étape 1 : écrire les tests qui échouent.**
  - `test_vues_dans_l_ordre` : `VUES["amenagement"][0] == "plan"` et `VUES["construction"][-1] == "explication"`.
  - `test_verifier_refuse_une_vue_inconnue` : un document « amenagement » avec une vue `plans` lève une `ValueError`
    qui contient `plans`.
  - `test_verifier_refuse_k_en_double` : deux `Element(k="A")` dans `coupes` lèvent une `ValueError`.
  - `test_vue_vide_acceptee` : `Vue("iso", [])` passe `verifier`.
- [ ] **Étape 2 : lancer les tests.** `uv run -q --no-project --with pytest pytest -q tests/test_modele.py` doit
  échouer (import).
- [ ] **Étape 3 : implémenter `commun/modele.py`** avec des dataclasses. Les classes « figées » ont `frozen=True`.
- [ ] **Étape 4 : relancer.** Les tests doivent passer.
- [ ] **Étape 5 : commiter.** `git commit -m "Refonte : structures des documents, vues et variantes"`

### Tâche 3 : journal et versions lus dans les pages actuelles

**Fichiers :**
- Créer : `commun/journal.py`, `tests/test_journal.py`.

**Interfaces :**
- Consomme : `Changement`, `Site`, `Document` et `Passerelle` (tâche 2).
- Produit :
  - **`depuis_page(html: str) -> list[Changement]`** : les lignes du premier tableau de la section `<h2>` « Changements »
    dont la date est au format `jj/mm/aaaa`. Le texte est débarrassé des balises. La lecture est reprise de
    `maquette/extraire.py:changements`.
  - **`version_depuis_page(html: str) -> str | None`** : le dernier morceau du `class="kicker"` qui commence par `V`.
  - **`EntreeJournal(piece, document, variante, version, date_iso, texte, lien)`**, figée.
  - **`entrees(site: Site, racine: Path) -> list[EntreeJournal]`** :
    - les changements de chaque variante d'un `Document`, et ceux de chaque `Passerelle`, lus par `depuis_page`
      dans `racine / page` ;
    - triés par date décroissante, sans changer l'ordre d'un même jour ;
    - `variante` vaut `None` quand le document n'en a qu'une.

- [ ] **Étape 1 : écrire les tests qui échouent.**
  - `test_depuis_page` : sur une page d'essai à deux lignes datées et une ligne d'en-tête, on obtient deux `Changement`,
    dans l'ordre, avec `texte` sans balise.
  - `test_version_depuis_page` : `<div class="kicker">Entrée · V4.8</div>` donne `"V4.8"`.
  - `test_entrees_triees` : une passerelle et un document à deux variantes donnent des dates décroissantes, et
    `variante == "Victor"` sur les lignes de Victor.
  - `test_pages_reelles` :
    - pour chaque page à la racine qui contient `id="changements"`, `depuis_page` renvoie au moins une ligne ;
    - pour `cuisine-v13.html`, la première version est `version_depuis_page(...)`.
- [ ] **Étape 2 : lancer les tests.** Ils doivent échouer (import).
- [ ] **Étape 3 : implémenter `commun/journal.py`** avec `re` et `html.unescape`, comme `extraire.py`.
- [ ] **Étape 4 : relancer.** Les tests doivent passer.
- [ ] **Étape 5 : commiter.** `git commit -m "Refonte : journal lu dans les tableaux de changements"`

### Tâche 4 : gabarit de page et document d'essai

**Fichiers :**
- Créer :
  - `commun/gabarit.py` ;
  - `tests/fixtures/essai/document.py`, un document d'essai : aménagement, variantes `a`/`b`/`c`. La variante `a` a des
    coupes A, B et C ; les variantes `b` et `c` ont A, B, C et D. Iso est vide. Option nuancier `teinte`, avec
    `css="--teinte"`, `filtre=True` et trois valeurs `v1`, `v2`, `v3` (défaut `v1`) ;
  - `tests/test_gabarit.py`.

**Interfaces :**
- Consomme : `commun/modele.py` (tâche 2).
- Produit :
  - **`relatif(cible: str, depuis: str) -> str`** : un chemin relatif entre deux fichiers de `site/`.
  - **`adresse(doc: Document | Passerelle, variante_id: str = "") -> str`** :
    - la première variante (ou `""`) donne `<piece>/<doc>/` ;
    - les autres donnent `<piece>/<doc>/<id>.html` ;
    - une passerelle donne sa `page`.
  - **`menu(site: Site, courant: tuple[str, str] | None, depuis: str) -> str`** : `<nav id="rail">`.
  - **`page_document(site: Site, doc: Document, variante: Variante, vues: dict[str, Vue]) -> str`**.
  - **`page_simple(site: Site, titre: str, corps: str, depuis: str, courant=None) -> str`** : pour l'accueil, le journal
    et les historiques.
- Contrat HTML, utilisé par `site.js` (tâches 5 à 8) :
  - **`<html class="sans-js">`** : le script retire la classe. Sans JavaScript, toutes les sections s'affichent l'une
    sous l'autre.
  - **`<body data-type data-piece data-document data-variante>`**, avec :
    - `<script type="application/json" id="variantes">`, une liste de `[id, nom, url relative]` ;
    - `<script type="application/json" id="options">` ;
    - `<script type="application/json" id="noms-vues">`.
  - **Menu (`#rail`) :**
    - un bouton `#b-rail` (réduire et déplier) ;
    - les liens des pièces et des documents, avec `aria-current="page"` sur le document courant ;
    - en pied, le lien « Journal des changements ».
  - **Barre (`header.barre`), ligne 1 :**
    - `#b-maison` (mobile) ;
    - `.b-titre`, avec un `#c-doc` si la pièce a plusieurs documents ;
    - `#c-variante` si la page a plus d'une variante ;
    - `#c-comp` (« Comparer ») ;
    - `#c-autre` avec « avec », écrit seulement s'il y a plus de deux variantes, caché tant qu'on ne compare pas ;
    - `a.version`, vers `historique.html`, qui affiche la version de la variante affichée.
  - **Barre, ligne 2 :**
    - `nav.vues`, un `a[data-vue]` par vue dans l'ordre de `VUES` ;
    - une vue sans élément a `aria-disabled="true"` et `title` égal à `Vue.vide` ;
    - `#c-options` (« Personnaliser ») si le document a des options.
  - **Une section par vue :** `<section class="vue" data-vue="…" data-outils="zoom mesure" data-vide="…">`, qui
    contient :
    - `.scene`, avec un `.element[data-k]` par élément ;
    - `.outils` (zoom ; mesure si `"mesure"` est dans `outils`) ;
    - `.bandeau` ;
    - `aside.fiche` : `.fiche-tete h2`, `.segments`, puis la fiche commune de la vue et un `.fiche-element[data-k]` par
      élément.
  - **`.segments`** : un `button[data-k]` par élément s'il y en a plus d'un. Un élément `actif=False` donne un bouton
    `disabled` avec `title="Pas encore rendu"`.
  - **Vue de lecture** (`LECTURE`) : `<article class="lecture">`, sans scène ni fiche.
  - **Pied de page :** `<script src="…/commun/site.js" defer>`, `<link rel="stylesheet" href="…/commun/site.css">`, et
    le lien Google Fonts de la maquette.

- [ ] **Étape 1 : écrire les tests qui échouent**, sur le document d'essai.
  - `test_onglets_dans_l_ordre` : les `data-vue` de `nav.vues` valent
    `["plan", "coupes", "iso", "camera", "explication"]`.
  - `test_onglet_vide_grise` : l'onglet `iso` (vue sans élément) a `aria-disabled="true"` et
    `title="Pas encore rendu"`.
  - `test_comparer_et_avec` : avec trois variantes, `#c-comp` et `#c-autre` sont présents. Avec une seule variante, ni
    `#c-variante` ni `#c-comp`.
  - `test_adresses` : `adresse(doc, "a") == "essai/amenagement/"` et
    `adresse(doc, "b") == "essai/amenagement/b.html"`. Depuis `essai/amenagement/b.html`, le CSS est
    `../../commun/site.css`.
  - `test_menu_courant` : le lien du document a `aria-current="page"`. Le menu ne contient aucun `<svg class="plan`.
  - `test_sans_js` : la page commence par `<html lang="fr" class="sans-js">`.
  - `test_textes_interdits` : la page ne contient ni `type="checkbox"`, ni « Copier la liste », ni « À venir », ni
    « prefers-color-scheme ».
- [ ] **Étape 2 : lancer les tests.** Ils doivent échouer.
- [ ] **Étape 3 : implémenter `commun/gabarit.py`.**
  - Le HTML suit le balisage de la maquette : `barre()`, `rail`, `fiche()`, `outilsZoom`, `outilMesure`. Les icônes
    SVG de la maquette (`ICONES`) passent dans un dictionnaire Python.
  - Le document d'essai a des éléments SVG simples (`<svg viewBox="0 0 100 50">` avec un `rect`).
- [ ] **Étape 4 : relancer.** Les tests doivent passer.
- [ ] **Étape 5 : commiter.** `git commit -m "Refonte : gabarit de page commun"`

### Tâche 5 : CSS et navigation (onglets, état de l'adresse, menu, fiche)

**Fichiers :**
- Créer :
  - `commun/site.css` ;
  - `commun/site.js` ;
  - `tests/fixtures/essai/construire.py`, qui écrit le site d'essai dans `cache/essai-site/` ;
  - `tests/navigateur/lancer.sh` ;
  - `tests/navigateur/navigation.js`.

**Interfaces :**
- Consomme : le contrat HTML de la tâche 4.
- Produit, dans `site.js`, en API interne de la closure :
  - **`lireEtat(hash: string) -> {vue, k, c}`** : la vue est validée contre `nav.vues`, `c` contre `#variantes`, et
    `c=1` devient l'autre variante ;
  - **`ecrireEtat(etat, {remplace})`** : `history.pushState` quand on change d'onglet, `replaceState` sinon ;
  - **`montrer(etat)`** : affiche la section et l'élément `k` (le premier élément si `k` est inconnu), et met
    `aria-current` sur l'onglet et `aria-pressed` sur les segments ;
  - **`memo.lit(cle, defaut)` et `memo.pose(cle, valeur)`** : `localStorage` sous le préfixe `plans:`, chaque accès
    dans un `try/catch`.
- `lancer.sh <script.js>` :
  1. lance `python3 tests/fixtures/essai/construire.py` ;
  2. lance `python3 -m http.server 8811 --bind 127.0.0.1` dans `cache/essai-site` ;
  3. lance `playwright-cli -s=refonte-essai open about:blank`, puis `playwright-cli -s=refonte-essai --raw run-code
     --filename=<script>` ;
  4. ferme la session `refonte-essai` et arrête le serveur ;
  5. sort en erreur si le JSON renvoyé contient `"ok": false`.

  Chaque script renvoie `{ok, echecs: [...], erreurs: [...]}`. `erreurs` regroupe les erreurs de console et de page.

- [ ] **Étape 1 : écrire le test navigateur qui échoue,** `tests/navigateur/navigation.js`, à 1440 × 900 puis
  390 × 844.
  - **Ouverture :** sur `essai/amenagement/`, la section `plan` est visible et les autres sont cachées. La classe
    `sans-js` est retirée.
  - **Onglets :** un clic sur l'onglet `coupes` donne l'adresse `#coupes`, puis « précédent » revient sur `plan`.
  - **Repère :** `#coupes?k=B` affiche l'élément B, et le segment B a `aria-pressed="true"`. Avec `k=Z`, c'est
    l'élément A, sans erreur.
  - **Vue vide :** `#iso` affiche la section `iso` avec le texte « Pas encore rendu », et l'onglet garde
    `aria-disabled="true"`.
  - **État invalide :** `#inconnu?c=zz` affiche `plan`, sans erreur.
  - **Menu :** il est réduit à 56 px par défaut. Un clic sur `#b-rail` le déplie, et il reste déplié après un
    rechargement.
  - **Sans `localStorage` :** le script d'initialisation remplace `Storage.prototype.getItem` par une fonction qui
    lève une exception. La page se charge, le menu est réduit, il n'y a aucune erreur.
  - **Mobile :**
    - `nav.vues` est fixé en bas ;
    - la fiche est fermée à 48 px et s'ouvre au plus à 54 % de la hauteur ;
    - `#b-maison` ouvre le menu en tiroir ;
    - `document.documentElement.scrollWidth <= innerWidth`.
- [ ] **Étape 2 : lancer le test.** `tests/navigateur/lancer.sh tests/navigateur/navigation.js` doit échouer
  (pas de `site.js`).
- [ ] **Étape 3 : implémenter `site.css` et la navigation de `site.js`.**
  - Le CSS de la maquette (`app.html`, bloc `<style>`) est porté sans le CSS propre aux vues de la maquette. On garde
    les jetons, le menu, la barre, les onglets, la scène, les outils, la fiche, le bandeau, la poignée et le panneau des
    options.
  - Les sections sont cachées seulement sous `html:not(.sans-js)`.
- [ ] **Étape 4 : relancer.** Le script renvoie `"ok": true`.
- [ ] **Étape 5 : commiter.** `git commit -m "Refonte : navigation par onglets et état dans l'adresse"`

### Tâche 6 : scène (zoom, déplacement, mesure, calques)

**Fichiers :**
- Modifier : `commun/site.js`.
- Créer : `tests/navigateur/scene.js`.

**Interfaces :**
- Consomme : `montrer(etat)` (tâche 5).
- Produit :
  - **`dessin(element) -> {zoomer(f), recadrer(), mesurer(on)}`** pour un élément qui contient un `<svg>` : zoom par la
    `viewBox`, bornes reprises de la maquette ;
  - **`vueImage(element, apres) -> {zoomer(f), recadrer()}`** pour un élément qui contient des `<img>` : `transform`,
    échelle de 1 à 8 ;
  - **zoom à plusieurs SVG :** `dessin` accepte plusieurs SVG qui partagent la même `viewBox` (comparaison) ;
  - **calques :** les cases `.calques input[data-calque]` de la fiche basculent la classe `sans-<calque>` sur la
    section, et le choix est mémorisé sous `calques`.

- [ ] **Étape 1 : écrire le test qui échoue,** `scene.js`.
  - **Zoom par bouton :** sur `plan`, « + » réduit la largeur de la `viewBox` d'un facteur 0,7.
  - **Recadrer :** le bouton rend la `viewBox` d'origine.
  - **Molette et glisser :** ils changent la `viewBox`.
  - **Pincement :** avec le tactile émulé par CDP (`Emulation.setTouchEmulationEnabled`, puis
    `Input.dispatchTouchEvent` à deux doigts), l'échelle d'une image dépasse 1, sans erreur.
  - **Mesurer :** deux clics sur `plan` affichent dans `.bandeau .mes` un texte de la forme « Mesuré : N cm ».
  - **Calques :** décocher « Cotes » ajoute `sans-cotes` à la section, et la classe reste après un rechargement.
- [ ] **Étape 2 : lancer le test.** Il doit échouer.
- [ ] **Étape 3 : implémenter.** Porter `dessin`, `vueImage`, `brancherZoom` et l'outil de mesure de la maquette.
- [ ] **Étape 4 : relancer.** Le script renvoie `"ok": true`.
- [ ] **Étape 5 : commiter.** `git commit -m "Refonte : zoom, mesure et calques"`

### Tâche 7 : comparaison de variantes

**Fichiers :**
- Modifier : `commun/site.js`.
- Créer : `tests/navigateur/comparaison.js`.

**Interfaces :**
- Consomme : `lireEtat`, `ecrireEtat`, `montrer`, `dessin` et `vueImage` (tâches 5 et 6).
- Produit :
  - **`chargerVariante(id) -> Promise<Document>`** : `fetch` de l'URL tirée de `#variantes`, puis `DOMParser`, avec un
    cache par id.
  - **`comparer(etat)`** :
    - si `etat.c` est valide et la vue dans `COMPARABLES`, on clone `section[data-vue=V] .element[data-k=K]` de l'autre
      page dans la scène, avec la classe `b`, et on pose la poignée et le rideau ;
    - sinon, on retire la comparaison.
  - **Bandeau :**
    - `.etiq-var` de la base à gauche, de la variante comparée à droite ;
    - `.etiq-var.manque` « <Nom> : pas d'équivalent » quand l'élément manque ;
    - « <Nom> : comparaison indisponible » si le chargement échoue.
  - **Barre :**
    - `#c-comp` pose `c`, l'autre variante, ou la retire ;
    - `#c-variante` charge l'autre page en gardant le fragment, et échange `c` et la base si `c` devient la base ;
    - `#c-autre` change `c` ;
    - `#c-comp` est caché sur les vues hors de `COMPARABLES`.

- [ ] **Étape 1 : écrire le test qui échoue,** `comparaison.js`, sur le site d'essai à trois variantes.
  - **Bouton :** sur `#plan`, un clic sur « Comparer » donne `#plan?c=b`. On voit deux SVG, la poignée et les
    étiquettes « A » et « B » en bas de la scène. La position `top` de `.outils` ne change pas.
  - **Choix « avec » :** `#c-autre` passe à `c` et l'adresse devient `#plan?c=c`.
  - **Ancienne forme :** `#plan?c=1` sur `a` compare avec `b`, la première autre variante, et l'adresse devient
    `#plan?c=b`.
  - **Lien direct :** ouvrir directement `b.html#coupes?k=D&c=a`, où la variante `a` n'a pas de coupe D, affiche
    « A : pas d'équivalent ».
  - **Échange :** sur `#plan?c=b`, choisir `b` comme base charge `b.html#plan?c=a`.
  - **Changement d'onglet :** passer à `coupes` garde `c` ; passer à `explication` cache `#c-comp`.
  - **Échec de chargement :** une route de `playwright-cli` renvoie 404 pour `c.html`. On obtient l'étiquette
    « C : comparaison indisponible », sans erreur non rattrapée.
  - **Rideau :** les flèches du clavier déplacent `--pos` de 4 points. Sur une image zoomée ×2, la coupure reste à
    moins de 1 px sous la poignée.
- [ ] **Étape 2 : lancer le test.** Il doit échouer.
- [ ] **Étape 3 : implémenter.** Porter `rideau`, `calage` et `bandeau` de la maquette ; le chargement par `fetch`
  est nouveau.
- [ ] **Étape 4 : relancer.** Le script renvoie `"ok": true`.
- [ ] **Étape 5 : commiter.** `git commit -m "Refonte : comparaison de variantes partageable par l'adresse"`

### Tâche 8 : « Personnaliser » (options génériques)

**Fichiers :**
- Modifier : `commun/site.js`, `commun/gabarit.py` (le panneau `#panneau-options`, un `<svg>` de filtres).
- Créer : `tests/navigateur/options.js`.

**Interfaces :**
- Consomme : `#options` (JSON des `Option`), `memo`.
- Produit :
  - **`appliquer(option, code)`** :
    - pose `option.css` sur `:root` ;
    - si `filtre` est vrai, met à jour les pentes de `#filtre-<id> feFunc{R,G,B}` à `canal / 255 / ref` ;
    - mémorise le choix sous `<piece>/<document>:<id>`, partagé entre les variantes.
  - **Panneau :**
    - groupes par `Valeur.groupe` ;
    - info de la valeur choisie (`note`, `lien`) ;
    - pastille `#n-options`, qui compte les options différentes de leur `defaut` ;
    - bouton « Valeurs d'origine ».
  - **Rendus recolorés :** une `<img class="calque">` porte `filter:url(#filtre-<id>)` et un masque
    `rendus/<variante>-<camera>-masque.png` en `mask-image`.

- [ ] **Étape 1 : écrire le test qui échoue,** `options.js`.
  - **Choix d'une teinte :** dans le panneau, choisir la valeur `v2` pose `--teinte` égal à sa couleur, change les
    pentes du filtre et affiche la pastille « 1 ».
  - **Mémorisation :** le choix est retrouvé sur l'autre variante après un rechargement.
  - **Retour à l'origine :** « Valeurs d'origine » rend `defaut` et cache la pastille.
  - **Sans `localStorage`** (même méthode qu'à la tâche 5) : la valeur d'origine s'affiche, sans erreur.
- [ ] **Étape 2 : lancer le test.** Il doit échouer.
- [ ] **Étape 3 : implémenter.** Le panneau générique de la maquette (`OPTIONS`) et le filtre de
  `3d/entree/plan.py:palette()` sont rendus génériques.
- [ ] **Étape 4 : relancer.** Le script renvoie `"ok": true`.
- [ ] **Étape 5 : commiter.** `git commit -m "Refonte : panneau Personnaliser générique"`

### Tâche 9 : construction du site (passerelle, accueil, journal, historiques, versions figées)

**Fichiers :**
- Créer :
  - `site.py`, qui déclare `SITE` et `REDIRECTIONS` et définit `main()` ;
  - `commun/construction.py` ;
  - `commun/appartement.py` ;
  - `tests/test_construction.py`.

**Interfaces :**
- Consomme : tâches 2 à 4 et `commun/journal.py`.
- Produit :
  - **`site.py` :**
    - **Déclaration :** `SITE: Site`, avec les pièces dans l'ordre du menu de la maquette : cuisine, salle de bain,
      entrée, salon, chambre.
    - **Passerelles :** au départ, chaque document est une `Passerelle` vers sa page actuelle :
      - cuisine : `cuisine-v13.html`, `cuisine-v13-porte-cellier.html` ;
      - salle de bain : `sdb-meuble-bas.html`, `sdb-meuble-haut.html` ;
      - entrée : `entree-amenagement.html` ;
      - salon : `salon-v4.html`, `salon-etageres.html`, `salon-enfilade.html` ;
      - chambre : `chambre-amenagement.html`.
    - **Commandes :**
      - `python3 site.py` construit tout ;
      - `python3 site.py <piece>/<document>` reconstruit ce document, le menu, l'accueil et le journal ;
      - `python3 site.py --figer <piece>/<document>[/<variante>]`.
  - **`construire(site, redirections, racine: Path, sortie: Path, seulement: str | None = None) -> None`** écrit :
    - **Documents :**
      - les pages de chaque `Document` (`doc.generer(variante.id)`, puis `verifier`, puis `page_document`) ;
      - `historique.html` par document : pour chaque variante, ses versions figées (version, date tirée de ses
        changements, lien), puis son journal.
    - **Pages communes :**
      - `journal.html`, filtrable par pièce (`<select>` côté JS) ;
      - `index.html`, l'accueil : le titre et `plan_appartement(site)`.
    - **Fichiers communs :**
      - `commun/site.css` et `commun/site.js` ;
      - `favicon.svg` (`#000000c7`, celle de la maquette) et `apple-touch-icon.png`.
    - **Passerelle et redirections :**
      - la passerelle ;
      - une page de redirection par `Redirection` (tâche 10).
  - **`copier_passerelle(racine, sortie, exclues: set[str]) -> list[str]`** :
    - copie chaque `*.html` de la racine (sauf `index.html` et `exclues`) et de `archive/` ;
    - copie aussi tous les fichiers locaux qu'ils référencent (`src=`, `href=` relatifs, sans `#`, `http` ni `data:`) ;
    - renvoie la liste copiée ;
    - les archives gardent le chemin `archive/`.

    C'est un écart assumé avec le nom `archives/` de la spec : les 59 liens publiés vers `archive/` continuent de
    marcher sans redirection.
  - **`figer(site, racine, sortie, cible: str) -> Path`** :
    - copie la page de la variante et ses `rendus/` dans
      `site/archive/<piece>-<document>[-<variante>]-<version>/` ;
    - ajoute `[version, chemin]` à `site/archive/figees.json` (clé `<piece>/<document>/<variante>`).

    `Variante.figees` est lu dans ce fichier.
  - **`commun/appartement.py`, `plan_appartement(site) -> str` :**
    - c'est le plan de l'accueil, repris de `APPART`, `MASSIFS`, `BAIES` et `VITRES` de la maquette, dans le repère du
      couloir ;
    - le contour d'une pièce migrée vient de son `piece.py` (`SOL` décalé de `POSITION`) ;
    - chaque pièce est un lien vers son premier document.

- [ ] **Étape 1 : écrire les tests qui échouent,** avec une construction dans `tmp_path` à partir d'une copie réduite
  de la racine.
  - `test_passerelle_garde_les_adresses` : `site/cuisine-v13.html` existe ; chaque image qu'elle référence existe sous
    `site/` ; `site/archive/entree-amenagement-v1.html` existe ; `site/index.html` est le nouvel accueil.
  - `test_journal_complet` : le nombre de lignes de `journal.html` égale la somme des `depuis_page` des passerelles plus
    les changements des documents.
  - `test_menu_identique` : le `<nav id="rail">` est le même, au lien courant près, dans `index.html`,
    `journal.html` et une page de document.
  - `test_figer` : `figer` sur le document d'essai crée le dossier, ajoute l'entrée à `figees.json` et fait apparaître
    la version dans `historique.html` après reconstruction.
  - `test_construire_n_ecrit_que_site_et_cache` : aucun fichier hors de `sortie` et de `cache/` n'est créé ni modifié
    (comparaison des dates de modification avant et après).
- [ ] **Étape 2 : lancer les tests.** Ils doivent échouer.
- [ ] **Étape 3 : implémenter `site.py`, `commun/construction.py` et `commun/appartement.py`.**
- [ ] **Étape 4 : relancer.** `just tests` doit passer. Puis `python3 site.py` doit produire `site/` sans erreur.
- [ ] **Étape 5 : vérifier dans le navigateur.**
  - Lancer `just apercu` (tâche 11), ou `python3 -m http.server` dans `site/`.
  - L'accueil, le journal et trois pages de passerelle s'ouvrent sans erreur ni 404, à 1440 et 390 px.
- [ ] **Étape 6 : commiter,** en incluant `site/` : `git commit -m "Refonte : construction du site, passerelle,
  accueil et journal"`.

### Tâche 10 : redirections des anciennes adresses

**Fichiers :**
- Créer : `commun/redirections.py`, `tests/test_redirections.py`, `tests/navigateur/redirections.js`.

**Interfaces :**
- Produit :
  - **`Redirection(ancienne: str, cible: str, ancres: dict[str, str], motifs: tuple[tuple[str, str], ...] = ())`**,
    figée.
    - `ancres` traduit un identifiant d'ancre en fragment (`"plan": "plan"`).
    - `motifs` donne des paires (regex, gabarit), par exemple `(r"^coupe-([a-d])-", "coupes?k={1}")`, où `{1}` est le
      premier groupe en majuscule.
  - **`page_redirection(r: Redirection, depuis: str) -> str`** :
    - `<meta http-equiv="refresh" content="0; url=…">` vers la cible sans fragment ;
    - un script qui traduit `location.hash` (ancres exactes, puis motifs, sinon aucun fragment) et appelle
      `location.replace` ;
    - un lien visible vers la cible.
  - **Identifiants d'ancres :** ce sont ceux de `3d/ancres.js`, `slug` du texte du `h2` (NFD, sans accents, en
    minuscules, `[^a-z0-9]+` remplacé par `-`).
  - **Table « ancien chemin → nouveau chemin » :** c'est celle de la spec, désormais dans le dépôt. Chaque migration y
    ajoute sa `Redirection` et met la table à jour.

- [ ] **Étape 1 : écrire les tests qui échouent.**
  - `test_page_redirection` : la page contient le `meta refresh` vers `../essai/amenagement/` (depuis un sous-dossier)
    et le lien visible.
  - Navigateur, `redirections.js` :
    - `ancienne.html#coupe-b-b-mur-de-la-salle-de-bain` mène à `…/#coupes?k=B` ;
    - `#inconnue` mène à la cible sans fragment, sur la vue par défaut ;
    - une adresse sans fragment mène aussi à la vue par défaut.
- [ ] **Étape 2 : lancer les tests.** Ils doivent échouer.
- [ ] **Étape 3 : implémenter `commun/redirections.py`,** et le brancher dans `construire` : une page par
  `REDIRECTIONS`, exclue de la passerelle.
- [ ] **Étape 4 : relancer.** `just tests` passe, et le script navigateur renvoie `"ok": true`.
- [ ] **Étape 5 : commiter.** `git commit -m "Refonte : pages de redirection des anciennes adresses"`

### Tâche 11 : publication par GitHub Action et recettes

**Fichiers :**
- Créer : `.github/workflows/pages.yml`.
- Modifier : `justfile` (`site`, `apercu`, `sync`, `pages-wait`).

**Interfaces :**
- `pages.yml` :
  - déclenché par `push` sur `main` et par `workflow_dispatch` ;
  - permissions `contents: read`, `pages: write`, `id-token: write` ;
  - `concurrency: pages` ;
  - un job `deploy` (environnement `github-pages`), avec `actions/checkout@v4`, `actions/configure-pages@v5`,
    `actions/upload-pages-artifact@v3` (`path: site`) et `actions/deploy-pages@v4`.

  `upload-pages-artifact@v3` et `deploy-pages@v4` ont été vérifiés le 13/11/2026. `checkout@v4` et
  `configure-pages@v5` sont de mémoire, non vérifiés : vérifier leur dernière version majeure avant d'écrire.
- **Recettes :**
  - `site *args` : `python3 site.py {{args}}` ;
  - `apercu` : `python3 site.py`, puis `python3 -m http.server 8800 --bind 127.0.0.1 --directory site`, puis
    l'ouverture de `http://127.0.0.1:8800/` ;
  - `sync` : lance d'abord `python3 site.py`, pour que la passerelle recopie les pages que les anciens générateurs
    viennent de réécrire à la racine ; le reste est inchangé ;
  - `pages-wait` : attend qu'une exécution de `pages.yml` existe pour le commit (`gh run list --workflow pages.yml
    --commit $sha`), puis `gh run watch <id> --exit-status`, et affiche « En ligne : {{site}} ».

- [ ] **Étape 1 : écrire le test qui échoue.**
  `test_workflow_publie_site`, dans `tests/test_construction.py` : `.github/workflows/pages.yml` contient
  `path: site`, `upload-pages-artifact@v3` et `deploy-pages@v4`. Aucun fichier de `site/` n'est un lien symbolique.
- [ ] **Étape 2 : implémenter.** Le workflow et les recettes.
- [ ] **Étape 3 : vérifier.**
  - `just tests` passe, et `just site` puis `just apercu` montrent l'accueil.
  - Ajouter une ligne au tableau des changements de `cuisine-v13.html` à la racine, puis lancer la première commande de
    `sync` (`python3 site.py`) : la ligne apparaît dans `site/cuisine-v13.html` et dans `site/journal.html`. Annuler
    ensuite la modification avec `git checkout`.
- [ ] **Étape 4 : commiter.** `git commit -m "Refonte : publication de site/ par GitHub Action"`
- [ ] **Étape 5 : fusionner la partie A.**
  - `git switch main && git merge --no-ff refonte`, puis `just tests`.
  - **Avec l'accord du client :**
    1. le client passe la source Pages sur « GitHub Actions » (réglages du dépôt, ou
       `gh api -X PUT repos/vfalduto/plans/pages -f build_type=workflow`) ;
    2. vérifier que l'ancien site reste en ligne ;
    3. `git push` ;
    4. `just pages-wait` ;
    5. vérifier en ligne l'accueil, le journal et trois pages de passerelle.
  - Revenir sur `refonte` pour la partie B.

---

## Partie B : entrée

Pendant cette partie, l'entrée est gelée pour les autres sessions (décision du client).

### Tâche 12 : pièce, document et variante Victor

**Fichiers :**
- Créer :
  - `pieces/__init__.py`, `pieces/entree/__init__.py`, `pieces/entree/amenagement/__init__.py` ;
  - `pieces/entree/piece.py` ;
  - `pieces/entree/amenagement/document.py`, à partir de `3d/entree/modele.py` moins la pièce ;
  - `pieces/entree/amenagement/victor.py`, à partir de `3d/entree/victor.py` ;
  - `pieces/entree/amenagement/plum.py`, déplacé tel quel ;
  - `tests/fixtures/entree/*.svg` ;
  - `tests/test_entree.py`.

**Interfaces :**
- Consomme : `Camera` (tâche 2).
- Produit :
  - **`pieces/entree/piece.py` :**
    - `ID = "entree"`, `NOM = "Entrée"` ;
    - `H`, `EP`, `H_PORTE`, `SOL`, `SURFACE`, `PORTES`, `MURS`, `ENVELOPPE` et la classe `Bloc`, repris de
      `modele.py:9-96` ;
    - `POSITION = (0, 0, 0)`, soit x, y et la rotation en degrés dans le repère de l'appartement ;
    - `CAMERAS: tuple[Camera, ...]`, communes aux deux variantes :
      - `iso_so`, `iso_no` et `iso_se` : les caméras de `3d/entree/rendu.py:VIEWS` ;
      - `banc` : yeux à 112, focale 17 ;
      - `couloir` : celle de `victor.py:VUES`, yeux à 160.
      - Pour `iso_no`, la cible commune est celle de la principale, `(177, 190, 60)` (choix de ce plan).
  - **`document.py` :**
    - le contenu de la variante principale, avec `VERSION = "V4.8"` et `CHANGEMENTS` ;
    - `HUMAINS`, qui donne la silhouette de chaque caméra (`{"iso_so": "couloir", …}`) ;
    - `ZONES` : les meubles touchables, repris de `ENTREE.principale.zones` de la maquette, avec `iso` exprimé en coin
      (`"so"`) ;
    - `FIGEES_ANCIENNES = (("V3.3", "archive/entree-amenagement-v3.3.html"), ("V2", "archive/entree-amenagement-v2.html"),
      ("V1", "archive/entree-amenagement-v1.html"))`.
    - Le `DOCUMENT` et les vues sont déclarés à la tâche 13.
  - **`victor.py` :**
    - importe `piece` et `document` ;
    - `VERSION = "V1.5"`, `BASE = "V4.3"` ;
    - son `VUES` disparaît : ce sont les caméras de la pièce ;
    - garde ses `HUMAINS` et ses `ZONES`, prises dans la maquette.

- [ ] **Étape 1 : capturer les dessins actuels,** avant tout déplacement.
  - Lancer `cd 3d/entree && python3 -c "import plan as P; open('../../tests/fixtures/entree/principale-plan.svg','w').write(P.plan_svg())"`.
  - Faire de même pour `coupe_a`, `coupe_b` et `coupe_c` de `plan.py`, puis pour `plan_svg` et `coupe_a` à `coupe_d`
    de `plan_victor.py` (fichiers `victor-*.svg`).
- [ ] **Étape 2 : écrire les tests qui échouent.**
  - `test_piece` :
    - `piece.SOL[0] == (0, 0)` et `len(piece.SOL) == 8` ;
    - `piece.H == 250` ;
    - les identifiants de `piece.CAMERAS` sont `{"iso_so", "iso_no", "iso_se", "banc", "couloir"}`.
  - `test_versions` : `document.VERSION == "V4.8"`, `victor.VERSION == "V1.5"` et
    `victor.CHANGEMENTS[0][0] == "V1.5"`.
  - `test_cameras_communes` : `victor` n'a pas d'attribut `VUES`.
- [ ] **Étape 3 : lancer les tests.** Ils doivent échouer.
- [ ] **Étape 4 : implémenter.**
  - Déplacer le code avec `git mv` quand le fichier garde son rôle (`plum.py`), et créer les autres.
  - Les imports deviennent absolus : `from pieces.entree import piece as P`.
- [ ] **Étape 5 : relancer.** `just tests` doit passer.
- [ ] **Étape 6 : commiter.** `git commit -m "Entrée : pièce, document et variante Victor dans pieces/"`

### Tâche 13 : vues Plan et Coupes de l'entrée

**Fichiers :**
- Créer :
  - `commun/position.py` ;
  - `pieces/entree/amenagement/dessin_principale.py`, à partir de `3d/entree/plan.py:93-482` : dessins, `COUPE_*`,
    légende et CSS des dessins ;
  - `pieces/entree/amenagement/dessin_victor.py`, à partir de `3d/entree/plan_victor.py:26-183` ;
  - `pieces/entree/amenagement/vues.py`.
- Modifier : `site.py` (l'entrée devient un `Document`), `tests/test_entree.py`.

**Interfaces :**
- Consomme :
  - `commun.dessin` (tâche 1) ;
  - `Element`, `Vue`, `Document`, `Variante` et `Option` (tâche 2) ;
  - `piece`, `document`, `victor` et `plum` (tâche 12).
- Produit :
  - **`mini_plan(sol, portes, traits=(), cones=()) -> str`**, dans `commun/position.py` :
    - SVG du mini-plan de la maquette (`miniPlan`) ;
    - `traits` donne des paires (lettre, `((x0, y0), (x1, y1))`), avec la classe `sec` et `ici` sur le trait courant ;
    - `cones` donne des triplets (loc, cible, ici), avec la classe `pdv`.
  - **`vues(variante: str) -> dict[str, Vue]`**, dans `vues.py`, qui remplit à cette tâche :
    - **`plan` :**
      - un seul élément, de `k` vide : le SVG du plan, avec ses `<rect class="zone" data-meuble tabindex="0"
        role="button" aria-label>` ;
      - un `<template data-meuble>` par zone : titre du principe, cotes, texte, liens « Coupe X » et « Iso » ;
      - la fiche commune :
        - « Touchez un meuble pour afficher sa fiche. » ;
        - les calques Cotes, Passages libres, Traits de coupe, Pièces voisines et Annotations ;
        - la légende ;
      - `outils=("zoom", "mesure")`.
    - **`coupes` :**
      - éléments `A`, `B` et `C` (et `D` pour Victor), avec `nom` = « A » plus le sujet ;
      - la fiche commune : « Position » et `mini_plan`, avec les traits ;
      - `outils=("zoom", "mesure")`.
    - Les légendes longues sous les dessins deviennent l'`aria-label` du SVG.
  - **`DOCUMENT`**, dans `document.py` :
    - `Document(piece="entree", id="amenagement", nom="Aménagement", type="amenagement", variantes=(principale,
      victor), generer=vues.vues, options=(teinte,))` ;
    - `teinte` : `Option(id="teinte", nom="Teinte de l'entrée", surfaces="murs, plafond, porte", type="nuancier",
      defaut=plum.DEFAUT, css="--india", filtre=True, portee="Visible sur le plan, les coupes et les rendus.")`.

      Ses valeurs sont les 52 teintes de `plum.PALETTE`, groupées comme dans `plan.py:palette()`. La note de chaque
      valeur est la gamme (« laque seulement, peinture à faire teinter »), et son lien la fiche peinture.

- [ ] **Étape 1 : écrire les tests qui échouent.**
  - `test_dessins_inchanges` : chaque dessin produit égale son fichier de `tests/fixtures/entree/`, à l'ajout près de la
    classe `plan` ou `coupe` et de l'`aria-label`. On compare après avoir retiré ces deux attributs.
  - `test_coupes` : les `k` des éléments de `coupes` valent `["A", "B", "C"]` pour la principale et
    `["A", "B", "C", "D"]` pour Victor.
  - `test_plan_zones` : le plan de la principale a 5 `.zone`, et autant de `<template data-meuble>`.
  - `test_fiche_plan` : la fiche contient « Touchez un meuble pour afficher sa fiche. » et non « Lecture du plan ».
- [ ] **Étape 2 : lancer les tests.** Ils doivent échouer.
- [ ] **Étape 3 : implémenter.**
  - Les fonctions de dessin prennent le module de variante `M` en paramètre au lieu d'une variable globale.
  - `dessin_victor.py` réutilise ce qui est commun dans `dessin_principale.py`.
  - Les vues `iso`, `camera` et `explication` sont des `Vue` vides jusqu'à la tâche 14.
- [ ] **Étape 4 : relancer.** `just tests` doit passer, puis `python3 site.py entree/amenagement`.
- [ ] **Étape 5 : commiter.** `git commit -m "Entrée : vues Plan et Coupes générées par le gabarit commun"`

### Tâche 14 : vues Iso, Caméra et Explication de l'entrée

**Fichiers :**
- Modifier : `pieces/entree/amenagement/vues.py`, `tests/test_entree.py`.

**Interfaces :**
- Consomme : `mini_plan` (tâche 13), `piece.CAMERAS` (tâche 12).
- Produit, dans `vues(variante)` :
  - **`iso` :**
    - éléments `no`, `ne`, `so` et `se` ;
    - `ne` a `actif=False`, et un coin sans rendu dans `site/entree/amenagement/rendus/` aussi ;
    - `scene` : `<figure>` avec `rendus/<variante>-iso_<coin>.jpg` et son calque masqué (tâche 8). Le texte d'origine
      de `RENDUS` devient l'`alt` ;
    - fiche : « Position », avec les cônes de vue aux coins de l'enveloppe des murs, marge 26 (`pointsDeVue` de la
      maquette).
  - **`camera` :**
    - éléments `banc` et `couloir` pour les deux variantes ;
    - fiche « yeux à {yeux} cm, objectif 17 mm » et « Position » avec les cônes.
  - **`explication`**, une vue de lecture :
    - chapô, chiffres clés, principes (cartes) ;
    - achats IKEA avec le total, portes du caisson, matériaux, points à vérifier (une liste sans cases) ;
    - la note de repère et de sources.

    Le texte est repris de `contenu()` (`plan.py` et `plan_victor.py`). La section « Vues 3D » et sa note
    disparaissent : leur contenu est dans les vues Iso et Caméra.

- [ ] **Étape 1 : écrire les tests qui échouent.**
  - `test_iso` : les `k` sont `["no", "ne", "so", "se"]` et l'élément `ne` a `actif=False`.
  - `test_camera_communes` : les `k` de `camera` sont `["banc", "couloir"]` pour les deux variantes.
  - `test_explication_complete` :
    - la principale contient 5 cartes de principe ;
    - « Total » est suivi de `≈ {round(sum(q * p for _, _, q, p in document.IKEA))} €` ;
    - les points à vérifier ont autant de `<li>` que dans `contenu()` à ce jour (10) ;
    - le texte ne contient ni `type="checkbox"`, ni « Copier la liste », ni « À venir ».
  - `test_alt_sans_texte_visible` : aucun texte de `RENDUS` n'apparaît hors d'un attribut `alt`.
- [ ] **Étape 2 : lancer les tests.** Ils doivent échouer.
- [ ] **Étape 3 : implémenter.**
- [ ] **Étape 4 : relancer.** `just tests` passe, puis `python3 site.py entree/amenagement`.
- [ ] **Étape 5 : commiter.** `git commit -m "Entrée : vues Iso, Caméra et Explication"`

### Tâche 15 : rendus de l'entrée avec cache

**Fichiers :**
- Créer :
  - `commun/rendu_cache.py` ;
  - `pieces/entree/amenagement/rendu.py`, à partir de `3d/entree/rendu.py` ;
  - `tests/test_rendu_cache.py`.
- Modifier : `justfile` (`entree-rendu`, `entree-apercu` ; suppression de `entree-victor-rendu`).

**Interfaces :**
- Produit :
  - **`empreinte(camera: Camera, donnees_variante: dict, reglages: dict, code: str, blender: str) -> str`** : le
    sha256 de la représentation JSON triée de ces entrées.
    - `donnees_variante` contient les constantes en majuscules du module de la variante et de `piece`, sans
      `CAMERAS` ni `CHANGEMENTS` ;
    - `code` est le contenu de `rendu.py` et de `3d/rendu.py`.
  - **`a_rendre(cle: str, emp: str, fichier: Path = Path("cache/empreintes.json")) -> bool`** et
    **`noter(cle, emp, fichier=…) -> None`**. `cle` vaut `<piece>/<document>/<variante>/<camera>`.
  - **`rendu.py`**, lancé dans Blender :
    - `ENTREE_VARIANTE=principale|victor` choisit la variante, et les caméras viennent de `piece.CAMERAS` ;
    - il écrit `3d/sortie/entree-<variante>-<camera>.png` et son masque.
  - **Recettes :**
    - `entree-rendu echantillons="64" *vues` : pour chaque variante, les caméras dont `a_rendre` est vrai. Un seul
      lancement de Blender par variante. Les JPG (qualité 85) et les masques sont copiés dans
      `site/entree/amenagement/rendus/<variante>-<camera>.jpg|-masque.png`, puis on lance `noter` et
      `python3 site.py entree/amenagement`.
    - `entree-apercu *vues` : 16 échantillons, 800 × 600, dans `cache/apercu/`, sans cache ni copie. Ouvre les
      images.

  « La partie du modèle utilisée » (spec, objectif 9) est lue ici comme « les données de la variante » :
  - changer une caméra ne refait que cette caméra ;
  - changer un meuble refait les vues de sa variante seulement.

- [ ] **Étape 1 : écrire les tests qui échouent.**
  - `test_empreinte_stable` : deux appels identiques donnent la même valeur.
  - `test_camera_isolee` : changer `loc` de `iso_so` change son empreinte, mais pas celle de `iso_no`.
  - `test_variante_isolee` : changer une constante de `victor` change l'empreinte des caméras de Victor, pas celles de
    la principale.
  - `test_a_rendre` : après `noter`, `a_rendre` renvoie `False` pour la même empreinte et `True` pour une autre.
- [ ] **Étape 2 : lancer les tests.** Ils doivent échouer.
- [ ] **Étape 3 : implémenter** `rendu_cache.py`, `rendu.py` et les recettes.
- [ ] **Étape 4 : relancer.** `just tests` doit passer.
- [ ] **Étape 5 : rendre** (long : environ 2 min 30 par variante, d'après la mesure du 13/11/2026).
  - `just entree-rendu` rend :
    - les caméras qui manquent : `couloir` pour la principale, `banc` pour Victor ;
    - l'`iso_no` de Victor, dont la cible change ;
    - et, au premier lancement, tout ce qui n'est pas encore noté.
  - Relancer `just entree-rendu` : il ne doit rien rendre.
- [ ] **Étape 6 : vérifier dans le navigateur.** Sur `entree/amenagement/#iso?k=so&c=victor`, la comparaison
  `#camera?k=banc&c=victor` montre deux images, sans « pas d'équivalent ».
- [ ] **Étape 7 : commiter,** rendus inclus : `git commit -m "Entrée : rendus partagés entre variantes, avec cache"`

### Tâche 16 : bascule de l'entrée

**Fichiers :**
- Modifier :
  - `site.py` : `REDIRECTIONS` pour l'entrée ;
  - `justfile` : `entree` devient `python3 site.py entree/amenagement`, et `entree-victor` disparaît.
- Créer : `site/archive/figees.json`, avec les trois versions figées de la principale (`FIGEES_ANCIENNES`).
- Supprimer :
  - `3d/entree/` en entier : `plan.py`, `plan_victor.py`, `rendu.py`, `modele.py`, `victor.py`, `plum.py`,
    `plum_lut.json` s'il existe ;
  - `entree-amenagement.html`, `entree-amenagement-victor.html` ;
  - `entree-3d/`, `entree-victor-3d/`.
- Créer : `tests/navigateur/entree.js`.

**Interfaces :**
- Consomme : `Redirection` (tâche 10), `figer` et `figees.json` (tâche 9).
- **Redirections :**
  - `entree-amenagement.html` mène à `entree/amenagement/`.
    - Ancres exactes :
      - `plan` → `plan` ;
      - `vues-3d` → `iso` ;
      - `principe`, `achats-ikea-penderie`, `materiaux` et `points-a-verifier` → `explication`.
    - Motif : `^coupe-([a-d])-` → `coupes?k={1}`.
    - `changements` mène à `historique.html`.
  - `entree-amenagement-victor.html` mène à `entree/amenagement/victor.html`, avec les mêmes ancres.

- [ ] **Étape 1 : écrire le test qui échoue,** `tests/navigateur/entree.js`, sur `site/` réel (serveur dans `site/`),
  à 1440, 1100 et 390 px.
  - **Vues :** toutes les vues des deux variantes s'affichent sans erreur ni 404, et rien ne déborde.
  - **Plan :** toucher le banc ouvre sa fiche, avec « Coupe A ». La touche Entrée sur une zone fait de même. En
    comparaison (`#plan?c=victor`), toucher le banc n'ouvre pas de fiche.
  - **Coupes :** `#coupes?k=D&c=principale` sur Victor affiche « Principale : pas d'équivalent ».
  - **Teinte :** choisir « Moka » change `--india` et le filtre des rendus. Le choix est retrouvé sur Victor.
  - **Redirections :** `entree-amenagement.html#coupe-b-b-mur-de-la-salle-de-bain` mène à
    `entree/amenagement/#coupes?k=B`, et `entree-amenagement-victor.html` mène à `victor.html`.
  - **Historique :** `historique.html` liste V3.3, V2 et V1 avec leur date, et les deux journaux.
  - **Sans JavaScript** (`javaScriptEnabled: false` sur un nouveau contexte) : les cinq sections sont visibles l'une sous
    l'autre.
- [ ] **Étape 2 : lancer le test.** Il doit échouer : l'ancienne page n'est pas encore une redirection.
- [ ] **Étape 3 : implémenter.** Les redirections, `figees.json`, les suppressions, puis `python3 site.py`.
- [ ] **Étape 4 : relancer.** `just tests` passe, et `entree.js` renvoie `"ok": true`.
- [ ] **Étape 5 : faire la table de contenu.**
  - Relire `git show main:entree-amenagement.html` section par section, et la page de Victor.
  - Ajouter à la fin de la spec, partie « Migration », une table « section → vue » pour l'entrée. Elle note chaque
    section retirée et la décision qui l'a retirée.
- [ ] **Étape 6 : commiter.** `git commit -m "Entrée : bascule sur la page générée par le gabarit, anciennes adresses
  redirigées"`
- [ ] **Étape 7 : fusionner.**
  - `git switch main && git merge --no-ff refonte`, puis `just tests`.
  - **Avec l'accord du client :** `git push`, `just pages-wait`, puis vérification en ligne de l'entrée et des deux
    anciennes adresses.
  - Le client passe une fois sur un vrai téléphone et dans Safari.

### Tâche 17 : seuil de bruit adaptatif

**Fichiers :**
- Modifier :
  - `3d/rendu.py` (`reglages_cycles`), seulement si la mesure le justifie ;
  - la spec, objectif 9 : le résultat.

- [ ] **Étape 1 : mesurer, machine au repos.** Aucune autre application lourde ne tourne, et la machine est sur secteur.
  - Rendre `iso_so` de la principale trois fois avec le seuil à 0,01, puis trois fois à 0,03, avec
    `just entree-apercu` à 64 échantillons et 1600 × 1200.
  - Noter les durées et l'écart moyen entre les images (0 à 255).
- [ ] **Étape 2 : décider.**
  - **Adopter 0,03** si la médiane baisse d'au moins 15 % et si l'écart moyen reste sous 0,5 sur 255.
  - Sinon, garder 0,01.
  - Dans les deux cas, écrire les chiffres dans la spec.
- [ ] **Étape 3 : commiter.** `git commit -m "Rendus : seuil de bruit mesuré"`
