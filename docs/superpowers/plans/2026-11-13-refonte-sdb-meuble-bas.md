# Salle de bain, meuble bas : migration de la page, plan d'implémentation

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal :** remplacer `sdb-meuble-bas.html` par le document de construction `sdb/meuble-bas/` (Plans, Découpe, Montage,
Achats, Explication), sans rien perdre, avec la section « Les deux meubles » dans Achats, puis rediriger l'ancienne
adresse ; préparer `pieces/sdb/` pour que le meuble haut, migré ensuite dans ce worktree, trouve la pièce prête.

**Architecture :** `pieces/sdb/` reçoit la pièce (`piece.py`, données), deux modules de dessin partagés par les deux
meubles (`dessin_cotes.py` : aides cotées de `3d/sdb/cotes.py` ; `iso.py` : projection isométrique de
`3d/sdb/montage.py`), la section commune des achats (`achats_communs.py`), les versions figées communes
(`archives.py`) et un chargeur des anciens modules (`ancien.py`). `pieces/sdb/meuble_bas/` reprend le modèle de
`3d/sdb/bas.py` (`modele.py`), ses onze dessins (`dessins.py`), les vues (`vues.py`, `explication.py`) et le document
(`document.py`, `DOCUMENT` ajouté à la bascule seulement). Tout passe par les blocs du socle (`commun.blocs`,
`commun.blocs_construction`). Le meuble haut reste en passerelle : `3d/sdb/modele.py`, `haut.py`, `achats.py`,
`plan.py`, `pages.py`, `cotes.py`, `montage.py`, `calepinage.py`, `cad.py` restent en place et fonctionnels.

**Tech Stack :** Python 3 (bibliothèque standard), pytest par `uv`, `playwright-cli` pour le script navigateur.

**Spec :** `docs/superpowers/specs/2026-11-13-refonte-site-design.md`. Consignes : `REGISTRE/consignes.md`. Inventaire :
`REGISTRE/sdb-meuble-bas/inventaire.md` (sections § 3a et § 3b, dessins § 5, ancres § 11, pièce § 12, risques R1-R12,
questions Q1-Q7) et, pour la suite, `REGISTRE/sdb-meuble-haut/inventaire.md` § 1-4. Socle : `REGISTRE/socle/rapport.md`.
Défauts connus du socle : `REGISTRE/salon-enfilade/rapport-final.md` (D1, D2, D5, D7 : ne pas les redécouvrir).
`REGISTRE` = `/Users/nvi/code/work/personal/plan/.superpowers/sdd/2026-11-13-refonte-pages`.

Worktree : `/Users/nvi/code/work/personal/plan-wt/sdb`, branche `refonte-sdb` (base `b73c60d`). Chaque commande commence
par `cd /Users/nvi/code/work/personal/plan-wt/sdb && …`.

Notation : `bas:L…` = ligne de `3d/sdb/bas.py` ; `ach:L…` = `3d/sdb/achats.py` ; `co:L…` = `3d/sdb/cotes.py` ;
`mo:L…` = `3d/sdb/montage.py` ; `pl:L…` = `3d/sdb/plan.py` ; `M6` = `3d/sdb/modele.py` chargé par
`pieces.sdb.ancien.modele()`. Dans `bas`, `M.` désigne `3d/sdb/modele.py`, `CO.` `cotes.py`, `PL.` `plan.py`, `MO.`
`montage.py`.

## Rulings du plan

Mode autonome : chaque décision prise seule est l'option réversible.

1. Ruling : `pieces/sdb/piece.py` garde le contour actuel de l'accueil (`SOL` profond de 156, `POSITION = (120, 218,
   0)`, pas de `SURFACE`) ; il porte aussi `SDB = dict(l=234, p=160)` et la porte du relevé V5.11 (`GONDS = 69`, 73 de
   large) que dessine le plan du meuble, et `PORTE_ACCUEIL = dict(x0=80, x1=156)`, la même porte sur le plan de
   l'appartement — Q1 ; l'accueil ne change pas (vérifié en mémoire : `plan_appartement` identique) — si faux : changer
   `SOL` et l'accueil bouge, à valider par le client. Les deux écarts (4 de profondeur, 9 sur les gonds) vont dans
   « À vérifier sur place » et « Au client ».
2. Ruling : `3d/sdb/modele.py` n'est pas touché (R3 : le meuble haut et la page d'achats en dépendent, ils restent
   identiques à l'octet). Les relevés copiés dans `piece.py`, et les données copiées (`PANNEAU`, `VERNIS`, `MAGASIN`,
   `RELEVE_V6`, `BUDGET`), sont gardés par un test d'égalité avec `M6` tant qu'il existe ; ce qui appartient au meuble
   haut (`Z_HAUT`, `Z_HAUT1`, `LED.x0`, `VERSION`) est lu dans `M6` par `pieces.sdb.ancien.modele()` — si faux : la
   migration du haut fait relire `piece.py` par `modele.py`.
3. Ruling : les dessins sont repris à l'octet (mêmes `f` à deux décimales et `cm` que `plan.py`, pas `commun.dessin`,
   qui arrondit à une décimale) ; seul leur `aria-label` change (ruling 10). Leur CSS est repris sans police à chasse
   fixe, sans règle de mise en page de l'ancienne page (`.feuille`, `.fcote`, `.ftitre`, `svg.cotes{…}`,
   `.op svg.cotes{…}`, `ol.pose li`), et les jetons absents de `commun/site.css` sont remplacés par leur valeur
   (`--tile` → `#E9EEF0`, `--dg` → `#D29A68`, `pl:L284`), sans jeton ajouté au socle — si faux : ajouter les jetons au
   socle. À noter pour le haut : `--bas` existe dans `site.css` mais vaut `0px` (hauteur de barre) : la couleur
   `--bas:#EDBE8C` de l'ancien meuble haut ne doit pas s'y fier.
4. Ruling : `pieces/sdb/iso.py` reprend tout `MO.dessin` (repères, trous, pièces neuves, `extra`, décalage des `Profil`),
   en lisant les pièces par leurs attributs (un `Profil` a `xz`, un prisme `xy`) au lieu de `isinstance` sur les classes
   de `M6`, et les murs dans `piece.py` — le meuble haut s'en servira avec les pièces de `M6` ; un test le compare à
   `MO.dessin` sur le modèle V6 (étape 8, murs, éclaté) — si faux : la migration du haut garde `MO.dessin`.
5. Ruling : les essais (`niv_1.py` à `niv_4.py`, `niv_commun.py`, `niv_comparatif.py`, `niveaux.py`, `var_pivot.py`,
   `var_tiroirs.py`, `var_arceaux.py`, `var_comparatif.py`, `variantes.py`) et `test_v4.py` vont dans `explorations/`
   à plat (l'arbre de la spec : « explorations/ essais de la salle de bain (niv_*, var_*, test_*) »), par `git mv`. Ils
   trouvent `3d/sdb/` par `sys.path` et écrivent dans `cache/explorations/` (ignoré par git), plus à la racine. Pas de
   recette (`just sdb-niveaux` et `just sdb-variantes` n'existent déjà plus). `test_v4.py` bouge maintenant : rien ne
   l'importe, le meuble haut n'en lit rien ; seuls ses `import bas` sont repointés (tâche 4) et une adresse redirigée
   tolérée (tâche 8) — si faux : le remettre dans `3d/sdb/` par `git mv`.
6. Ruling : `3d/sdb/bas.py`, `3d/sdb/test_bas.py` et `sdb-meuble-bas.html` restent jusqu'à la bascule (consignes : le
   générateur part une fois le tableau de contenu complet) ; `3d/sdb/achats.py` lit le nouveau module dès la tâche 4
   (R1), la page d'achats restant identique à l'octet. Les tests comparent à des copies figées des deux anciennes pages
   (`tests/fixtures/sdb/`), qui survivent à la bascule ; les comparaisons avec `bas.py` en mémoire sautent quand il
   disparaît, et chaque test garde des valeurs absolues.
7. Ruling (Q2) : la page d'achats est figée telle quelle dans `archive/sdb-meuble-achats-v8.5.html` (ses cinq liens
   relatifs préfixés de `../`), déclarée dans `pieces/sdb/archives.py:FIGEES_COMMUNES` ; ses 13 changements n'entrent
   pas dans `CHANGEMENTS` : le journal du meuble bas reste à 16 (R8) — si faux : les verser avec le préfixe « Liste
   d'achats : ».
8. Ruling (Q3) : versions figées du meuble bas, libellés distincts (le libellé est le texte du lien de l'historique) :
   propres, `("V6.2", "archive/sdb-meuble-v4-bas.html")`, `("Variantes V1.0", "archive/sdb-meuble-variantes.html")`,
   `("Niveaux de finition V1.0", "archive/sdb-meuble-niveaux.html")`, `("Revue V1.0",
   "archive/sdb-meuble-bas-revue.html")` ; communes aux deux meubles (`FIGEES_COMMUNES`) : `("Liste d'achats V8.5",
   "archive/sdb-meuble-achats-v8.5.html")`, `("V6.2, les deux meubles", "archive/sdb-meuble-v4.html")`, `("V5.24",
   "archive/sdb-meuble-v5.24.html")`, `("V5.24, notice", "archive/sdb-meuble-v5.24-montage.html")`, `("V2.2",
   "archive/sdb-meuble-v2.html")`, `("V2.2, débit", "archive/sdb-meuble-debit.html")`, `("V1, trois propositions",
   "archive/sdb-meuble-v1.html")`. Une copie chacune, rien n'est copié (elles sont déjà dans `archive/`).
9. Ruling (Q4, R11) : Plans a onze dessins, dans cet ordre et sous ces noms (titres de figure de l'ancienne page, et
   `aria-label` pour les trois iso) : `elevation` « Élévation, vue depuis la salle de bain » (par défaut), `iso` « Vue
   iso », `iso-ouvert` « Sans la porte », `eclate` « Vue éclatée », `plan` « Plan », `coupe` « Coupe par la machine »,
   `placard` « Coupe par le placard », `porte` « Porte vue de face », `joue` « Joue vue de côté », `colonne` « Colonne
   vue de face », `colonne-dessus` « Colonne vue de dessus ». Titre de la fiche « Meuble bas », formule
   `f"{cm(PY1 - PY0)} × {cm(PLATEAU_P)}, dessus à {cm(Z_DESSUS)}"` (« 114,4 × 60, dessus à 88,8 »), liens Découpe et
   Montage, pas de légende. Mesurer sur les huit dessins cotés (une unité du dessin = 1 cm), pas sur les trois iso.
10. Ruling : texte alternatif d'un dessin = son ancien `aria-label`, plus « . » et le texte sous le dessin s'il y en a
    un ; si ce texte commence par le nom du bouton (« Sans la porte : … », « Vue éclatée : … »), ce texte seul. Aucun
    texte sous un dessin ne reste à l'écran.
11. Ruling : Achats : h2 « Meuble bas », les deux paragraphes repris (`bas:L655` sans son lien, qui menait à cette
    même vue ; `ach:L54` sans le lien vers la page du bas), `tableau_achats(…, "Total du meuble bas", arrondi=False)`
    (seize lignes), la note `ach:L55-57` en remarque, puis `achats_communs.deux_meubles(liens)`. Le bloc du socle n'a
    que Article, Référence, Qté, Prix (prix de la ligne) : le prix unitaire (« 2 × 16,50 € », quand la quantité n'est
    pas 1) et le stock (« stock : 25 », quand il est connu) vont dans la note de l'article. La note du magasin dit donc
    « Stock : nombre affiché sur la fiche produit pour ce magasin, dans la note de l'article (sans note : non lu). » au
    lieu de « (« — » : non lu) » (Au client). « Les deux meubles » est un tableau propre (deux lignes et le total), la
    note du budget et la note du magasin ; sa ligne « Meuble haut » mène à
    `../../sdb-meuble-achats.html#haut-seul` tant que le haut est en passerelle — si faux : un tableau d'achats propre.
12. Ruling : Montage : `etapes([Etape("", f"<p>{li}</p>") …], titre="Montage")` avec le HTML de chaque `<li>` de
    `bas:L630-642` tel quel (son titre en gras reste le début du texte : couper au premier gras laisserait des
    fragments, « devant et au fond. ») ; puis « Les 6 équerres : » et sa liste ; puis
    `etapes(…, titre="Pose de la colonne")` (`bas:L675-679`), numérotée de 1 comme l'ancienne liste. Pas d'outils : la
    page n'en avait pas.
13. Ruling : Découpe : `tableau_debit` titré « Pièces » (`Rep.` repere, `Pièce` texte, `Qté` nombre, `Longueur`,
    `Largeur`, `Ép.` cote ; cellules par `cm`), le paragraphe de répartition, la liste des tablettes, « Pieds : 6
    vérins. », puis `<h2>Finition</h2>` et son paragraphe (le chant se plaque après la coupe). Pas de calepinage
    dessiné : il n'y en avait pas.
14. Ruling : Explication, dans l'ordre de l'ancienne page : `tete(<chapô bas:L743>)` (lien vers
    `../../archive/sdb-meuble-v4-bas.html`, Q6), quatre chiffres clés calculés (alcôve, prix du meuble, panneaux à
    découper, étapes), `<h2>Structure</h2>` et ses `<h3>` Placard, Porte, Pieds, Tenue (hiérarchie d'origine), `<h2>Colonne
    de prises</h2>`, `<h2>Mesures</h2>` et ses trois `<h3>`, `a_verifier` (trois points : la note « À confirmer » reprise,
    puis les deux écarts du ruling 1, calculés), `note_source` du repère sans les chemins de l'ancien générateur.
15. Ruling : erreurs d'affichage corrigées depuis le modèle, listées « Au client » : « 2.5 GPa » → « 2,5 GPa » et « ≈ 4.1
    kg » → « ≈ 4,1 kg » (note de la Tenue) ; « B à F : trois tablettes » → « B à G » (la colonne G est taillée dans la
    troisième ; les lettres viennent de `decoupe()`). Les autres nombres écrits en dur (inventaire § 10) restent tels
    quels dans les textes repris.
16. Ruling : ni `rendu.py`, ni `CACHE_RENDU`, ni recette de rendu ou d'aperçu, ni Blender : la salle de bain n'a aucun
    rendu (inventaire § 6) et un document de construction n'a pas de vue Iso ni Caméra (`VUES["construction"]`) ;
    Explication sans `rendus_meuble`.
17. Ruling : `DOCUMENT` n'est déclaré qu'à la bascule (tâche 8) : un `DOCUMENT` sur le disque sans entrée dans `site.py`
    fait échouer `tests/test_construction.py::test_site_py_tient_documents_et_redirections`. Avant, `document.py` ne
    porte que `VERSION`, `CHANGEMENTS`, `FIGEES` ; les tests construisent un `Document` d'essai.
18. Ruling, bascule : `git rm sdb-meuble-bas.html 3d/sdb/bas.py 3d/sdb/test_bas.py` ; `sdb-meuble-achats.html` et
    `3d/sdb/achats.py` restent (R2 : la page du haut renvoie à `#haut-seul` et `#deux-meubles`). Rien ne réécrit plus
    l'ancienne page à la racine : pas de ligne `.gitignore`. `tests/test_construction.py` n'est pas touché : la garde
    des redirections se compare déjà aux documents migrés, sans liste figée, et `sdb-meuble-achats.html` est déjà dans
    `HORS_DOCUMENTS` (le R7 de l'inventaire est périmé).
19. Ruling (Q5) : `3d/sdb/cad.py` n'est pas touché ; il reste lancé par `just sdb`.
20. Ruling (§ 11) : redirection `sdb-meuble-bas.html` → `sdb/meuble-bas/`, ancres du tableau `ANCRES_SDB_BAS` de la
    tâche 8, `changements` vers l'historique ; pas de motif. La redirection de `sdb-meuble-achats.html` attend la
    bascule du haut.

## Global Constraints

Recopiées des consignes (`REGISTRE/consignes.md`) et de la spec ; elles valent pour chaque tâche.

- **Interdits :** `git push` ; toute fusion ; écrire dans `main` ou dans le worktree d'une autre page ; modifier
  `3d/sdb/modele.py`, `haut.py`, `plan.py`, `pages.py`, `cotes.py`, `montage.py`, `calepinage.py`, `cad.py` ; lancer
  Blender ou FreeCAD ; lire le PDF du logement ; `playwright-cli close-all` ou `kill-all` ; la session `prod` ; toucher
  `achats/`, `reddit/`, `3d/sortie/`, `3d/textures/`, `3d/modeles/`, `cache/` du dépôt principal, les `git stash`.
- **Pages qui ne bougent pas :** `sdb-meuble-haut.html` (= `haut.page()`) et `sdb-meuble-achats.html`
  (= `achats.page()`) identiques à l'octet à la fin de chaque tâche ; `python3 site.py` ne change ni
  `site/index.html` ni aucun fichier de `site/entree/` avant la bascule.
- **`site/` :** jamais modifié à la main, rien de commité dessous. Après chaque `python3 site.py` :
  `git checkout -- site && git clean -fdq site`.
- **Fichiers partagés :** `commun/`, `tests/fixtures/essai/`, `tests/navigateur/*.js` (sauf `sdb-meuble-bas.js`),
  `tests/test_construction.py` : **aucun changement prévu**. Dans `site.py` et le `justfile`, seulement les lignes de la
  salle de bain, à la bascule.
- **Source unique :** toute cote d'un texte nouveau (texte alternatif, chiffres clés, formule, points à vérifier) est
  calculée depuis `piece.py` ou `meuble_bas/modele.py`. Les textes repris gardent leurs valeurs, calculées par les
  mêmes formules (sauf les trois corrections du ruling 15).
- **Rien ne se perd :** chaque section, tableau, dessin, note et lien externe des deux anciennes pages a sa place
  (tableau plus bas), ou est retiré par une décision listée.
- **Textes exacts du socle :** « Sans objet », « Pas encore rendu », « Mesuré : … cm », « À vérifier sur place ».
- **Style :** pas de point médian nulle part (virgule à la place), pas de police à chasse fixe (`JetBrains`,
  `monospace`), pas d'étiquettes en capitales (`text-transform:uppercase`), pas de flèche ajoutée aux liens, pas de mode
  sombre (`prefers-color-scheme`), pas de motif décoratif. Couleurs et polices du socle (`commun/site.css` : Fira Sans,
  Fira Sans Condensed `var(--ui)` pour les cotes, chiffres tabulaires).
- **Jamais :** cases à cocher, « Copier la liste », « À venir », « Lecture du plan », « Lecture de la coupe », texte sous
  un dessin à l'écran (texte alternatif seulement), sommaire ou barre propres à la page, bouton de version figée,
  tableau des changements dans une vue.
- **Vues de construction**, dans cet ordre : Plans (`elevation` par défaut), Découpe, Montage, Achats, Explication.
  Une seule variante (id vide) : ni « Comparer » ni choix de variante. Pas d'options.
- **Journal :** 16 changements « Salle de bain › Meuble bas » avant et après (V8.5 à V7.0).
- **Tests :** `uv run -q --no-project --with pytest pytest -q tests` (478 passés à la base `b73c60d`) ; tous verts à la
  fin de chaque tâche.
- **Navigateur :** ports 8860 à 8869, sessions `refonte-sdb-meuble-bas-<n>` :
  `PORT=8861 SESSION=refonte-sdb-meuble-bas-1 tests/navigateur/lancer.sh tests/navigateur/sdb-meuble-bas.js`.
- **Git :** commits petits, en français, sur `refonte-sdb`, terminés par la ligne
  `Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>`.

## Review Focus

Les cas que la spec implique et qu'un lecteur rencontrera, du plus probable au moins probable ; chacun a son test.

1. **Page à 390 px avec onze boutons dans la fiche de Plans et des tableaux de trois colonnes** (Mesures, Tenue) : les
   boutons passent à la ligne dans la fiche, les tableaux défilent dans leur boîte, la page ne défile pas en largeur.
   Test : tâche 8 (script, `debordements` à 390 px sur les onze repères et les quatre vues de lecture).
2. **Un élément de dessin sans règle CSS, ou une cote en chasse fixe** (`.omasse`, `.ct`, `.ibt`, et `.omel` défini
   deux fois) : rien n'est noir par défaut, la règle du meuble bas l'emporte. Tests : tâche 3
   (`test_css_couvre_les_classes`), tâche 5 (`test_classes_ont_une_regle`, `test_omel_du_meuble_bas_l_emporte`),
   tâche 8 (script : aucun aplat noir).
3. **Une ancienne adresse avec une ancre de figure (`#f-placard`), de titre (`#finition`), `#changements`, inconnue ou
   absente** : la bonne vue et le bon repère, l'historique, ou Plans par défaut. Tests : tâche 8 (`test_redirection`,
   script).
4. **Un texte sous un dessin resté à l'écran, ou perdu** : il est dans l'`aria-label`, et nulle part ailleurs à
   l'écran. Tests : tâche 5 (`test_alts`, `test_aucune_description_visible`), tâche 7 (`test_rien_ne_se_perd`).
5. **La page d'achats et la page du haut, encore en passerelle, après le changement de `achats.py`** : identiques à
   l'octet, et leurs liens vers `sdb-meuble-bas.html` arrivent sur le nouveau document. Tests : tâche 4
   (`test_pages_du_haut_et_des_achats_identiques`), tâche 8 (script : `/sdb-meuble-achats.html`, lien « Meuble bas »).

## Fichiers

| Fichier | Rôle | Tâche |
|---|---|---|
| `pieces/sdb/__init__.py`, `pieces/sdb/piece.py` | la pièce : données de l'alcôve, contour de l'accueil, réseaux, machine | 1 |
| `pieces/sdb/ancien.py` | chargeur des anciens modules de `3d/sdb/` (`modele()`, `charger(nom)`, `haut()`) | 1 |
| `tests/fixtures/sdb/sdb-meuble-bas.html`, `sdb-meuble-achats.html` | copies exactes des anciennes pages | 1 |
| `tests/sdb_anciennes.py` | aide de test : anciennes pages, dessins, sections, textes, anciens modules | 1 |
| `explorations/*.py` (14 fichiers déplacés) | essais de la salle de bain et `test_v4.py` | 2 |
| `pieces/sdb/dessin_cotes.py`, `pieces/sdb/iso.py` | aides de dessin coté et projection iso, avec leur CSS | 3 |
| `pieces/sdb/meuble_bas/__init__.py`, `modele.py`, `document.py` | modèle du meuble bas ; version et changements | 4 |
| `3d/sdb/achats.py` | lit `pieces.sdb.meuble_bas` au lieu de `bas.py` | 4 |
| `pieces/sdb/meuble_bas/dessins.py` | les onze dessins, leurs textes, le CSS du document | 5 |
| `pieces/sdb/meuble_bas/vues.py` | `vues(variante)` : Plans, Découpe, Montage, Achats | 5, 6 |
| `pieces/sdb/achats_communs.py` | section « Les deux meubles », données du magasin et du budget | 6 |
| `pieces/sdb/meuble_bas/explication.py` | `vue_explication()` | 7 |
| `pieces/sdb/archives.py`, `archive/sdb-meuble-achats-v8.5.html` | versions figées communes, page d'achats figée | 7 |
| `tests/test_sdb_*.py` | tests | 1 à 8 |
| `tests/navigateur/sdb-meuble-bas.js` | script navigateur, `@site reel` | 8 |
| `site.py`, `justfile`, `sdb-meuble-bas.html`, `3d/sdb/bas.py`, `3d/sdb/test_bas.py` (supprimés) | bascule | 8 |

## Section de l'ancienne page → vue qui la reprend

### `sdb-meuble-bas.html` (V8.5), inventaire § 3a

Colonne « Ancre » : identifiant de l'ancienne page et ce qu'en fait la redirection (tâche 8).

| # | Section de l'ancienne page | Ancre | Devient | Retiré, et décision qui le retire |
|---|---|---|---|---|
| 1 | Barre : « ← Plans » | | Menu de gauche, icône maison sur mobile | La barre propre à la page (consignes, « Retirés par décision ») ; la flèche (« À éviter ») |
| 2 | Sommaire | | Onglets des vues | Le sommaire : « une navigation identique sur toutes les pages » |
| 3 | Surtitre « Salle de bain, alcôve 115 × 62 à 68, meuble bas, V8.5 » et titre « Meuble bas » | | Barre du haut : pièce, document, pastille V8.5 ; titre de la fiche de Plans ; l'alcôve en chiffre clé de l'Explication, calculée (ruling 14) | Le surtitre lui-même ; le double titre (spec, objectif 1) |
| 4 | Chapô, avec le lien « L'ancien meuble bas » | | Explication : `tete`, texte repris, lien vers `../../archive/sdb-meuble-v4-bas.html` (Q6) | |
| 5 | Le meuble : iso porte fermée | `iso` → `plans?k=iso` | Plans, `k=iso` | |
| 6 | Le meuble : iso sans la porte, et son texte | | Plans, `k=iso-ouvert` ; texte en `aria-label` (ruling 10) | Le texte à l'écran : « pas de descriptions d'images à l'écran » |
| 7 | Le meuble : vue éclatée, et son texte | | Plans, `k=eclate` ; texte en `aria-label` | id. |
| 8 | Structure : paragraphe, 5 puces | `structure` → `explication` | Explication, « Structure » | |
| 9 | Placard : dessin et son texte | `f-placard` → `plans?k=placard` | Plans, `k=placard` ; texte en `aria-label` | Le texte à l'écran (id.) |
| 10 | Placard : 7 puces | `placard` → `explication` | Explication, « Placard » (h3) | |
| 11 | Porte : dessin et son texte | `f-porte` → `plans?k=porte` | Plans, `k=porte` ; texte en `aria-label` | id. |
| 12 | Porte : 10 puces (liens IKEA UTRUSTA, BILLSBRO) | `porte` → `explication` | Explication, « Porte » (h3) | |
| 13 | Pieds : paragraphe, 4 puces | `pieds` → `explication` | Explication, « Pieds » (h3) | |
| 14 | Joue : dessin et son texte | `f-joue` → `plans?k=joue` | Plans, `k=joue` ; texte en `aria-label` | id. |
| 15 | Finition : paragraphe | `finition` → `decoupe` | Découpe, « Finition » (ruling 13) | |
| 16 | Pièces : tableau A à G, répartition, 3 tablettes, vérins | | Découpe, « Pièces » (« B à G », ruling 15) | |
| 17 | Montage : 13 étapes, les 6 équerres | | Montage, « Montage » (ruling 12) | |
| 18 | Tenue : tableau de 4 lignes, note | | Explication, « Tenue » (h3) ; « 2,5 » et « 4,1 » (ruling 15) | |
| 19 | Achats : paragraphe du total, lien vers la liste d'achats | | Achats, premier paragraphe, sans le lien (ruling 11) | Le lien : il menait à cette même liste, devenue la vue |
| 20 | Colonne de prises : paragraphe d'ouverture | `colonne` → `explication` | Explication, « Colonne de prises » | |
| 21 | Colonne : vue de face, et son texte | `f-colonne` → `plans?k=colonne` | Plans, `k=colonne` ; texte en `aria-label` | Le texte à l'écran |
| 22 | Colonne : vue de dessus, et son texte | `f-colonne-dessus` → `plans?k=colonne-dessus` | Plans, `k=colonne-dessus` ; texte en `aria-label` | id. |
| 23 | Colonne : 7 puces (liens aucun) | `colonne` | Explication, « Colonne de prises » | |
| 24 | Pose de la colonne : 5 étapes | | Montage, « Pose de la colonne » | |
| 25 | Plan, et son texte | `plan`, `f-plan` → `plans?k=plan` | Plans, `k=plan` ; texte en `aria-label` | Le texte à l'écran |
| 26 | Élévation, et son texte | `elevation`, `f-face` → `plans?k=elevation` | Plans, `k=elevation` (par défaut) ; texte en `aria-label` | id. |
| 27 | Coupe, et son texte | `coupe`, `f-coupe` → `plans?k=coupe` | Plans, `k=coupe` ; texte en `aria-label` | id. |
| 28 | Mesures : « Toutes les cotes sont en cm. » | `mesures` → `explication` | Explication, « Mesures » | |
| 29 | Mesures : Relevées, 9 lignes | | Explication, « Mesures », « Relevées » | |
| 30 | Mesures : Reprises des versions précédentes, 10 lignes | | Explication, même titre | |
| 31 | Mesures : Ce qu'il reste, 6 puces, note « À confirmer » | | Explication, « Ce qu'il reste » ; la note devient le premier point de « À vérifier sur place » | |
| 32 | Note finale : repère, sources, recette | | Explication, `note_source` : le repère et `pieces/sdb/` | Les chemins de l'ancien générateur (`3d/sdb/modele.py`, `3d/sdb/bas.py`, `just sdb`), supprimé à la bascule (même décision que l'entrée, spec « Entrée », note finale) |
| 33 | Changements, 16 lignes | `changements` → `sdb/meuble-bas/historique.html` | Historique du document et `journal.html` | Le tableau dans une vue (consignes) |
| — | Titres de figure (`figcaption`) et `aria-label` des dessins | | Noms des boutons de Plans (ruling 9) et textes alternatifs (ruling 10) | |

Une ancre absente de ce tableau, ou pas d'ancre, ouvre la vue par défaut (Plans, élévation).

### `sdb-meuble-achats.html` (V8.5), inventaire § 3b

La page reste en passerelle, générée par `3d/sdb/achats.py`, jusqu'à la bascule du meuble haut ; ce tableau dit où son
contenu se trouve déjà dans le meuble bas.

| # | Section | Ancre | Devient | Retiré, et décision qui le retire |
|---|---|---|---|---|
| 1 | Barre : « ← Plans », « Meuble bas → », « Meuble haut → » | | Menu de gauche ; les lignes de « Les deux meubles » mènent à chaque meuble | La barre propre à la page ; les flèches ajoutées aux liens (« À éviter ») |
| 2 | Sommaire | | Onglets | Le sommaire (consignes) |
| 3 | Surtitre et titre « Liste d'achats » | | Titre de la section « Les deux meubles » de la vue Achats | Le surtitre |
| 4 | Total des deux meubles : tableau de 2 lignes et total TTC | `deux-meubles` | Achats, « Les deux meubles » (`achats_communs.deux_meubles`), lue aussi par le meuble haut à sa migration | |
| 5 | Note du budget accepté | | Achats, « Les deux meubles » | |
| 6 | Meuble bas : paragraphe, tableau de 16 lignes, note | `bas` | Achats, « Meuble bas » (ruling 11) | Le lien vers la page du bas, qui devient la page elle-même |
| 7 | Meuble haut : paragraphe, tableau de 12 lignes | `haut-seul` | Reste sur cette page (lien depuis « Les deux meubles ») ; Achats du meuble haut à sa migration | |
| 8 | Note du magasin et dates de relevé | | Achats, « Les deux meubles » (phrase du stock adaptée, ruling 11) | |
| 9 | Note source | | | Les chemins des anciens générateurs (comme l'entrée) |
| 10 | Changements, 13 lignes | `changements` | `archive/sdb-meuble-achats-v8.5.html`, versions figées des deux meubles (ruling 7) | Le tableau dans une vue (consignes) |

---

### Task 1 : La pièce (`pieces/sdb/piece.py`) et les anciennes pages de référence

**Files:**
- Create: `pieces/sdb/__init__.py` (vide), `pieces/sdb/piece.py`, `pieces/sdb/ancien.py`
- Create: `tests/fixtures/sdb/sdb-meuble-bas.html`, `tests/fixtures/sdb/sdb-meuble-achats.html` (copies)
- Create: `tests/sdb_anciennes.py`
- Test: `tests/test_sdb_piece.py`

**Interfaces:**
- Consumes : `commun.appartement` (`APPART`, `BAIES`, `contours`) ; `3d/sdb/modele.py` (lu, jamais modifié).
- Produces :
  - `pieces.sdb.piece` (données seulement, commentaire de tête sur le modèle de `pieces/chambre/piece.py`) :
    `ID = "sdb"`, `NOM = "Salle de bain"`, `POSITION = (120, 218, 0)`, `P_ACCUEIL = 156`,
    `H = 250`, `X1 = 234`, `Y0, Y1 = 0, 115`, `ALCOVE = dict(nord=62, sud=68)`, `X0 = X1 - ALCOVE["sud"]`,
    `SOL = [(0, 0), (X1, 0), (X1, Y1), (X0, Y1), (X0, P_ACCUEIL), (0, P_ACCUEIL)]`, `SDB = dict(l=234, p=160)`,
    `GONDS = 69`, `PORTE = dict(x0=X1 - GONDS - 73, x1=X1 - GONDS, l=73)`, `CHAMBRANLE = 0.5`,
    `PORTE_ACCUEIL = dict(x0=80, x1=156)`, `DOUCHE = (5, 50, 78, 155)`, `LAVABO = (82, Y1, 165, 160)`,
    `CARRELAGE = 204`, `EP_CARRELAGE = 1.0`, `ROBINET = dict(y=74, z=102)`,
    `TUYAUX = dict(zone=(229, 234, 66, 82, 50, 85.5), evacuation_z=60, arrivee_z=80, saillie_max=5)`,
    `PASSE = dict(l=6, p=4)`, `MACHINE = dict(l=59.5, p=53, h=85, nom="lave-linge 59,5 × 53 × 85 (relevé client)")`,
    `CAMERAS = ()`. Pas de `SURFACE` (l'accueil garde « alcôve 68 × 115 »). Chaque valeur a un commentaire d'origine
    (relevé client, version), repris de `M6` ; `SOL` et `SDB`, `PORTE` et `PORTE_ACCUEIL` disent leur écart.
  - `pieces.sdb.ancien` :
    - `RACINE: Path` (racine du dépôt), `ANCIEN = RACINE / "3d" / "sdb"` ;
    - `modele() -> ModuleType` : `3d/sdb/modele.py` chargé une fois par `importlib.util.spec_from_file_location`, sous
      le nom `sdb_ancien_modele` (il n'importe que `math` et `dataclasses`) ;
    - `charger(nom: str) -> ModuleType` : `3d/sdb/<nom>.py` importé comme le font les anciens générateurs (`ANCIEN` en
      tête de `sys.path` le temps de l'import), puis retiré de `sys.modules` avec ses dépendances de `3d/sdb/` (gardées
      dans un cache du module, rendues aux imports suivants), `sys.path` et `sys.modules` rendus tels qu'avant ;
      `FileNotFoundError` si le fichier n'existe pas (modèle : `tests/salon_anciens.py:ancien`, sans pytest) ;
    - `haut() -> ModuleType` : `charger("haut")`.
  - `tests/sdb_anciennes.py` :
    - `FIXTURES = RACINE / "tests/fixtures/sdb"` ; `page_bas() -> str`, `page_achats() -> str` (les copies) ;
    - `ancien(nom: str) -> ModuleType` : `pieces.sdb.ancien.charger(nom)`, `pytest.skip` si le fichier manque ;
    - `dessin(html: str, aria: str) -> str` : le `<svg …aria-label="<aria échappé, quote=True>"…>…</svg>` de `html` ;
    - `sans_aria(svg: str) -> str` : le même sans son attribut `aria-label` ;
    - `entre(html: str, debut: str, fin: str | None = None) -> str` : de `debut` à `fin` (exclu ; `None` : la fin) ;
    - `section(html: str, ancre: str) -> str` : de l'élément `id="<ancre>"` au `<h2` suivant ;
    - `texte(html: str) -> str` : balises retirées, entités décodées, blancs réunis ;
    - `morceaux(html: str) -> list[str]` : `texte` de chaque `<p>` (sauf `class="cap"`), `<li>`, `<h3>`, `<th>`,
      `<td>`, hors de `<section id="changements">`, de `<nav>` et de `<style>`/`<script>` ;
    - `CORRECTIONS: dict[str, str]` et `corrige(t: str) -> str` (remplit les tâches 5 à 7) :
      `{"2.5 GPa": "2,5 GPa", "≈ 4.1 kg": "≈ 4,1 kg", "B à F :": "B à G :", "(« — » : non lu)":
      ", dans la note de l'article (sans note : non lu)"}`.

- [ ] **Step 1 : copier les deux anciennes pages**

```bash
mkdir -p tests/fixtures/sdb
cp -p sdb-meuble-bas.html sdb-meuble-achats.html tests/fixtures/sdb/
cmp sdb-meuble-bas.html tests/fixtures/sdb/sdb-meuble-bas.html && cmp sdb-meuble-achats.html tests/fixtures/sdb/sdb-meuble-achats.html
```

Expected : aucune sortie de `cmp`.

- [ ] **Step 2 : écrire les tests**

```python
# tests/test_sdb_piece.py
from commun.appartement import APPART, BAIES, contours
from pieces.sdb import ancien, piece
from tests.sdb_anciennes import ancien as vieux, page_bas, page_achats

RELEVES = ("H", "X0", "X1", "Y0", "Y1", "ALCOVE", "SDB", "GONDS", "PORTE", "CHAMBRANLE", "DOUCHE", "LAVABO",
           "CARRELAGE", "EP_CARRELAGE", "ROBINET", "TUYAUX", "PASSE")

def test_releves_comme_modele_py():
    M = vieux("modele")
    for nom in RELEVES:
        assert getattr(piece, nom) == getattr(M, nom), nom
    assert piece.MACHINE == M.LL

def test_contour_de_l_accueil_inchange():
    (avant,) = [c for c in APPART if c.id == "sdb"]
    (apres,) = [c for c in contours() if c.id == "sdb"]
    assert apres.p == avant.p and apres.cotes == avant.cotes == "alcôve 68 × 115"
    assert not hasattr(piece, "SURFACE") and piece.CAMERAS == ()
    assert piece.SOL == [(0, 0), (234, 0), (234, 115), (166, 115), (166, 156), (0, 156)]

def test_porte_de_l_accueil():
    (baie,) = [r for r, _ in BAIES if (r[1], r[3]) == (208, 218)]       # mur nord de la salle de bain
    x, y, _ = piece.POSITION
    assert (baie[0] - x, baie[2] - x) == (piece.PORTE_ACCUEIL["x0"], piece.PORTE_ACCUEIL["x1"])
    assert piece.X1 - piece.PORTE_ACCUEIL["x1"] - piece.GONDS == 9    # l'écart du ruling 1

def test_chargeur():
    M = ancien.modele()
    assert ancien.modele() is M and M.VERSION == "V6.4" and M.Z_HAUT == 158
    H = ancien.haut()
    assert round(H.total_lignes(H.lignes()), 2) == 179.82
    import sys
    assert "modele" not in sys.modules and "haut" not in sys.modules and "plan" not in sys.modules

def test_fixtures_sont_les_pages():
    assert page_bas() == vieux("bas").page() and page_achats() == vieux("achats").page()
```

- [ ] **Step 3 : lancer, constater l'échec**

Run : `uv run -q --no-project --with pytest pytest -q tests/test_sdb_piece.py`
Expected : FAIL, `ModuleNotFoundError: No module named 'pieces.sdb'`.

- [ ] **Step 4 : écrire `pieces/sdb/__init__.py`, `piece.py`, `ancien.py`, `tests/sdb_anciennes.py`**

- [ ] **Step 5 : lancer, constater le succès, construire le site**

Run : `uv run -q --no-project --with pytest pytest -q tests`
Expected : tout passe (478 + 5).
Run : `python3 site.py && git status --short site/ ; git checkout -- site && git clean -fdq site`
Expected : `git status` n'affiche rien (l'accueil est identique).

- [ ] **Step 6 : commit**

```bash
git add pieces/sdb/__init__.py pieces/sdb/piece.py pieces/sdb/ancien.py tests/fixtures/sdb tests/sdb_anciennes.py tests/test_sdb_piece.py
git commit -m "Salle de bain : la pièce (contour de l'accueil gardé, relevés de l'alcôve) et les anciennes pages de référence

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
```

### Task 2 : Les essais dans `explorations/`

**Files:**
- Move (`git mv 3d/sdb/<f> explorations/<f>`) : `niv_1.py`, `niv_2.py`, `niv_3.py`, `niv_4.py`, `niv_commun.py`,
  `niv_comparatif.py`, `niveaux.py`, `var_pivot.py`, `var_tiroirs.py`, `var_arceaux.py`, `var_comparatif.py`,
  `variantes.py`, `test_v4.py`
- Modify : chacun des 13 fichiers déplacés (chemins seulement)
- Test: `tests/test_sdb_explorations.py`

**Interfaces:**
- Consumes : `3d/sdb/modele.py`, `plan.py`, `pages.py`, `cotes.py`, `montage.py`, `calepinage.py`, `haut.py`,
  `achats.py`, `bas.py` (importés par les essais et `test_v4.py`, inchangés).
- Produces : `explorations/niveaux.py` et `explorations/variantes.py` écrivent
  `cache/explorations/sdb-meuble-niveaux.html` et `cache/explorations/sdb-meuble-variantes.html` (constante
  `SORTIE = os.path.join(<racine>, "cache", "explorations")`, dossier créé au besoin) ; `explorations/test_v4.py`
  passe tel quel.

Modifications, et rien d'autre :
- dans chaque fichier, juste après sa ligne `sys.path.insert(0, os.path.dirname(…))` :
  `sys.path.insert(1, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "3d", "sdb"))` (les essais se
  trouvent entre eux par `explorations/`, les modules du meuble linge par `3d/sdb/`) ;
- `niveaux.py:ecrire` et `variantes.py:ecrire` : `chemin = os.path.join(SORTIE, FICHIER)` au lieu de
  `os.path.join(PL.ROOT, FICHIER)`, `os.makedirs(SORTIE, exist_ok=True)` ; leur commentaire de tête dit la commande
  (`python3 explorations/niveaux.py [--strict]`) et la sortie, au lieu de `just sdb-niveaux` / `just sdb-variantes` ;
- `test_v4.py` : chaque `os.path.join(os.path.dirname(__file__), "..", "..")` devient `os.path.join(os.path.dirname(
  __file__), "..")` (lignes 87, 96, 224) ; sa ligne 1 donne la nouvelle commande.

- [ ] **Step 1 : écrire les tests**

```python
# tests/test_sdb_explorations.py
import os
import subprocess
import sys
from tests.outils import RACINE

ESSAIS = ("niv_1.py", "niv_2.py", "niv_3.py", "niv_4.py", "niv_commun.py", "niv_comparatif.py", "niveaux.py",
          "var_pivot.py", "var_tiroirs.py", "var_arceaux.py", "var_comparatif.py", "variantes.py", "test_v4.py")
ENV = {**os.environ, "PYTHONDONTWRITEBYTECODE": "1"}

def test_essais_ranges():
    for nom in ESSAIS:
        assert (RACINE / "explorations" / nom).is_file(), nom
        assert not (RACINE / "3d" / "sdb" / nom).exists(), nom

def test_essais_tournent_sans_ecrire_a_la_racine():
    avant = sorted(p.name for p in RACINE.glob("*.html"))
    for script, sortie in (("niveaux.py", "sdb-meuble-niveaux.html"), ("variantes.py", "sdb-meuble-variantes.html")):
        r = subprocess.run([sys.executable, f"explorations/{script}", "--strict"], cwd=RACINE, env=ENV,
                           capture_output=True, text=True, timeout=180)
        assert r.returncode == 0, r.stderr[-2000:]
        assert (RACINE / "cache" / "explorations" / sortie).is_file()
    assert sorted(p.name for p in RACINE.glob("*.html")) == avant

def test_test_v4_passe():
    r = subprocess.run([sys.executable, "-m", "pytest", "-q", "-p", "no:cacheprovider", "explorations/test_v4.py"],
                       cwd=RACINE, env=ENV, capture_output=True, text=True, timeout=180)
    assert r.returncode == 0, r.stdout[-3000:]
```

- [ ] **Step 2 : lancer, constater l'échec**

Run : `uv run -q --no-project --with pytest pytest -q tests/test_sdb_explorations.py`
Expected : FAIL (`explorations/niv_1.py` absent).

- [ ] **Step 3 : déplacer par `git mv`, puis corriger les chemins**

- [ ] **Step 4 : lancer, constater le succès**

Run : `uv run -q --no-project --with pytest pytest -q tests`
Expected : tout passe (3 tests neufs). Puis `git status --short` : seulement les déplacements, les fichiers modifiés et le
test neuf (rien à la racine, `cache/` ignoré).

- [ ] **Step 5 : commit**

```bash
git add -A explorations 3d/sdb tests/test_sdb_explorations.py
git commit -m "Salle de bain : les essais (niveaux, variantes) et test_v4 rangés dans explorations/, sortie dans cache/

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
```

### Task 3 : Aides de dessin partagées (`dessin_cotes.py`, `iso.py`)

**Files:**
- Create: `pieces/sdb/dessin_cotes.py`, `pieces/sdb/iso.py`
- Test: `tests/test_sdb_dessin.py`

**Interfaces:**
- Consumes : `pieces.sdb.piece` (`X0`, `X1`, `Y1`, `H`, pour les murs de l'iso).
- Produces :
  - `pieces.sdb.dessin_cotes` : `f(v) -> str` (`pl:L30-31`, deux décimales), `cm(v) -> str` (`pl:L34-36`),
    `text(x, y, s, cls="lbl", anchor="middle", extra="") -> str` (`pl:L47-48`), `poly(pts, cls) -> str` (`pl:L43-44`),
    `cote_h(x0, x1, y, label=None, dy=0, ext=None, place="") -> str`, `cote_v(y0, y1, x, label=None, dx=0, ext=None,
    place="") -> str`, `niveaux(liste, x, droite=False) -> str`, `etiquette(x, y, tx, ty, texte, ancre="start") -> str`,
    `svg(x0, y0, x1, y1, corps, titre) -> str` : copies de `co:L77-158`, mêmes sorties à l'octet ; `CSS: str` (plus bas).
  - `pieces.sdb.iso` : `proj`, `faces`, `ecran`, `devant`, `profondeur`, `ordre`, `teinte`, `pts_svg`, `VUE`, et
    `dessin(blocs, neuves=(), murs=False, reperes=True, decale=None, extra=None, marge=14, titre="", trous=(),
    carrelage=None) -> str` : copies de `mo:L21-215`, mêmes sorties à l'octet, avec ces seuls écarts :
    `isinstance(b, M.Profil)` → `hasattr(b, "xz")` ; `isinstance(b, M.Bloc) and (b.encoche or b.entailles)` →
    `not hasattr(b, "xz") and not hasattr(b, "xy") and (getattr(b, "encoche", ()) or getattr(b, "entailles", ()))` ;
    `M.replace` → `dataclasses.replace` (un bloc à `xz` décalé par `xz`, `y0`, `y1`, sinon par ses six bornes) ;
    `M.X0`, `M.X1`, `M.Y1`, `M.H` → `piece.X0`, … ; `CSS: str` (plus bas).

CSS, exactement :
- `dessin_cotes.CSS` : `co:L452-480` recopiées, avec `var(--tile)` → `#E9EEF0`, `var(--dg)` → `#D29A68`, et
  `svg.cotes .ct{font:600 2.5px var(--ui);font-variant-numeric:tabular-nums;fill:var(--ink)}`,
  `svg.cotes .nt{font:600 2.4px var(--ui);font-variant-numeric:tabular-nums;fill:var(--ink)}` à la place des deux règles
  en JetBrains Mono ; `co:L447-451` (mise en page de l'ancienne page) ne sont pas reprises.
- `iso.CSS` : `mo:L669-691`, `mo:L722`, `mo:L723`, `mo:L749` recopiées, avec
  `.ibt{font:700 4.4px var(--ui);font-variant-numeric:tabular-nums;fill:var(--ink)}` à la place de `mo:L688`.

- [ ] **Step 1 : écrire les tests**

```python
# tests/test_sdb_dessin.py
import re
from commun.css_dessins import css_dessins
from pieces.sdb import dessin_cotes as DC, iso
from tests.outils import RACINE
from tests.sdb_anciennes import ancien

CAS = [("cote_h", (174, 234, 18), {"label": "60 plateau", "ext": 4}), ("cote_h", (0, 3, 6), {"ext": 0, "place": "gauche"}),
       ("cote_h", (5, 6.5, 6), {"dy": 3.4, "place": "droite"}), ("cote_v", (-88.8, -87, 230), {}),
       ("cote_v", (-10, -9, 5), {"place": "haut", "ext": 2}), ("cote_v", (-4, -1, 5), {"dx": 3.4, "place": "bas"}),
       ("niveaux", ([(86, "86 machine", 0), (88.8, None, 0), (90, "90", 0)], -7), {}),
       ("niveaux", ([(3.8, "3,8", 10)], 13), {"droite": True}),
       ("etiquette", (1, 2, 8, -3, "Colonne", "end"), {}), ("etiquette", (1, 2, 8, -3, "Vérin"), {}),
       ("svg", (0, -10, 20, 5, ["<g/>"], "Titre « a » & l'b"), {})]

def test_aides_comme_cotes_py():
    CO, PL = ancien("cotes"), ancien("plan")
    for nom, a, k in CAS:
        assert getattr(DC, nom)(*a, **k) == getattr(CO, nom)(*a, **k), nom
    for v in (47.50000000000001, 1.8, 0.25, 114.4):
        assert (DC.f(v), DC.cm(v)) == (PL.f(v), PL.cm(v))
    assert DC.text(1, 2, "a & b", "lt", "end") == PL.text(1, 2, "a & b", "lt", "end")
    assert DC.poly([(0, 1.234), (2, 3)], "omel") == PL.poly([(0, 1.234), (2, 3)], "omel")

def _appels():
    MO, M = ancien("montage"), ancien("modele")
    tout = M.version("d")
    bl = [b for b in tout if b.groupe == "caisson_haut" and b.etape <= 8 and b.role != "led"]
    neuves = {b.nom for b in MO.pieces_etape("d", 8)}
    dec = {"plan": (0, 0, 35), "bac": (-20, 0, 0), "machine": (-80, 75, 0)}
    return MO, [((tout,), dict(murs=True, reperes=False, carrelage=M.CARRELAGE, titre="Tout")),
                ((bl, neuves), dict(titre="Étape 8", trous=MO.trous_etape(8, bl))),
                ((tout,), dict(reperes=False, decale=dec, titre="Éclaté")),
                (([],), dict(murs=True, titre="Vide"))]

def test_iso_comme_montage_py():
    MO, appels = _appels()
    for a, k in appels:
        assert iso.dessin(*a, **k) == MO.dessin(*a, **k), k["titre"]

def test_css_couvre_les_classes():
    _, appels = _appels()
    dessins = [iso.dessin(*a, **k) for a, k in appels] + [DC.cote_h(0, 5, 1) + DC.niveaux([(3, "3", 0)], 2)
                                                          + DC.etiquette(0, 0, 1, 1, "x") + DC.svg(0, 0, 1, 1, [], "t")]
    css = css_dessins(DC.CSS + "\n" + iso.CSS, dessins, ".d-sdb")
    site = (RACINE / "commun/site.css").read_text(encoding="utf-8")
    classes = {c for s in dessins for m in re.findall(r'class="([^"]+)"', s) for c in m.split()}
    regle = lambda c, t: re.search(rf"\.{re.escape(c)}(?![\w-])", t) is not None   # noqa: E731
    assert {"isol", "inew", "itr", "ibt", "ct", "nt", "dim", "niv", "cotes"} <= classes
    assert sorted(c for c in classes if not regle(c, css) and not regle(c, site)) == []

def test_css_au_style_du_site():
    for interdit in ("JetBrains", "monospace", "uppercase", "prefers-color-scheme", "var(--tile)", "var(--dg)",
                     "var(--bas)", "var(--haut)", "min-width", ".fcote", ".feuille"):
        assert interdit not in DC.CSS + iso.CSS, interdit
    assert "svg.cotes .ct{font:600 2.5px var(--ui)" in DC.CSS and ".ibt{font:700 4.4px var(--ui)" in iso.CSS
```

- [ ] **Step 2 : lancer, constater l'échec**

Run : `uv run -q --no-project --with pytest pytest -q tests/test_sdb_dessin.py`
Expected : FAIL, `ImportError` sur `pieces.sdb.dessin_cotes`.

- [ ] **Step 3 : écrire `pieces/sdb/dessin_cotes.py` et `pieces/sdb/iso.py`**

Commentaire de module : d'où viennent les fonctions, et que les deux meubles s'en servent.

- [ ] **Step 4 : lancer, constater le succès**

Run : `uv run -q --no-project --with pytest pytest -q tests`
Expected : tout passe (4 tests neufs).

- [ ] **Step 5 : commit**

```bash
git add pieces/sdb/dessin_cotes.py pieces/sdb/iso.py tests/test_sdb_dessin.py
git commit -m "Salle de bain : aides de dessin coté et vue iso partagées par les deux meubles, sans chasse fixe

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
```

### Task 4 : Modèle du meuble bas, et `achats.py` qui le lit

**Files:**
- Create: `pieces/sdb/meuble_bas/__init__.py` (vide), `pieces/sdb/meuble_bas/modele.py`,
  `pieces/sdb/meuble_bas/document.py`
- Modify: `3d/sdb/achats.py:1-2` (commentaire), `achats.py:10-18` (imports, `VERSION`), `achats.py:53-54`
  (`B.PAGE`, `B.VERSION`)
- Modify: `explorations/test_v4.py` (fonctions `test_page_achats_sections` et `test_page_achats_suit_le_meuble_bas_courant`)
- Test: `tests/test_sdb_meuble_bas_modele.py` (port de `3d/sdb/test_bas.py`), `tests/test_sdb_achats_passerelle.py`

**Interfaces:**
- Consumes : `pieces.sdb.piece` (tâche 1), `pieces.sdb.ancien.modele()`.
- Produces :
  - `pieces.sdb.meuble_bas.modele` : copie de `bas:L61-341` et `bas:L344-345` (`cm`), mêmes noms, mêmes valeurs, où :
    `M.Y0`, `M.Y1`, `M.X1`, `M.H`, `M.ALCOVE`, `M.GONDS`, `M.PORTE`, `M.SDB`, `M.LAVABO`, `M.CHAMBRANLE`,
    `M.CARRELAGE`, `M.ROBINET`, `M.TUYAUX`, `M.PASSE` → `P.<même nom>` (`from pieces.sdb import piece as P`) ;
    `M.LL` → `P.MACHINE` ; `M.PT` → `EP = 1.8` ; `M.PROF` → `PLATEAU_P = 60` ; `M.PANNEAUX["D"][0]` →
    `PANNEAU = dict(L=2000, l=600, prix=66.90, stock=None, ref="82025610", magasin="Weldom", nom="Tablette chêne
    lamellé-collé brute FSC 200 × 60 × 18")` ; `M.VERNIS` → `VERNIS` (clés `couches`, `rendement`, `pots` de
    `M6:L1161-1165`) ; `M.Z_HAUT`, `M.Z_HAUT1`, `M.LED.x0`, `M.VERSION` → `Z_HAUT`, `Z_HAUT1`, `LED_X`,
    `VERSION_HAUT`, lus dans `ancien.modele()` (ruling 2) ; `M.Bloc` → `Bloc`, une dataclass du module aux champs
    `role, nom, x0, x1, y0, y1, z0, z1, rep="", groupe="", encoche=(), entailles=()` ; `Porte(Bloc)` (`fenetres=()`)
    et `Prisme` comme `bas:L295-315`. Fonctions : `col_pt`, `decoupe`, `chant_vu`, `rouleaux_chant`, `pot_vernis`,
    `prix`, `total`, `tenue`, `contour`, `contour_porte`, `plaque_3d`, `blocs`, `cm`.
  - `pieces.sdb.meuble_bas.document` : `VERSION = "V8.5"`, `CHANGEMENTS` (les 16 triplets de `bas:L25-42`, tels quels).
  - `3d/sdb/achats.py` lit `pieces.sdb.meuble_bas.modele` (`B`) et `document.VERSION` ; `PAGE_BAS =
    "sdb-meuble-bas.html"` dans `achats.py`.

Modification de `3d/sdb/achats.py`, et rien d'autre :

```python
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(1, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))   # pieces/
import modele as M  # noqa: E402
import plan as PL  # noqa: E402
import pages as PG  # noqa: E402
import haut as H  # noqa: E402
from pieces.sdb.meuble_bas import modele as B  # noqa: E402
from pieces.sdb.meuble_bas.document import VERSION as VERSION_BAS  # noqa: E402

PAGE = "sdb-meuble-achats.html"
PAGE_BAS = "sdb-meuble-bas.html"
VERSION = VERSION_BAS
```

et, dans `bas_courant`, `B.PAGE` → `PAGE_BAS`, `B.VERSION` → `VERSION_BAS`. Dans `explorations/test_v4.py`, les deux
`import bas` deviennent `from pieces.sdb.meuble_bas import modele as bas` et `bas.VERSION` devient
`pieces.sdb.meuble_bas.document.VERSION` ; la racine du dépôt est ajoutée à son `sys.path` (`sys.path.insert(2, …)`).

- [ ] **Step 1 : écrire les tests**

`tests/test_sdb_meuble_bas_modele.py` reprend les 26 premiers tests de `3d/sdb/test_bas.py` (tous sauf `test_page` et
`test_liens`, qui visent l'ancienne page : tâches 5 à 7), avec `bas` → `B` (`from pieces.sdb.meuble_bas import modele as
B`), `M.Y0`, `M.Y1`, `M.X1`, `M.TUYAUX`, `M.ROBINET` → `P.…`, `M.Z_HAUT` → `B.Z_HAUT`, et `M.CH`, `M.TH` →
`ancien.modele().CH`, `.TH`. Puis :

```python
from dataclasses import fields
import pytest
from pieces.sdb import ancien, piece as P
from pieces.sdb.meuble_bas import document, modele as B
from tests.sdb_anciennes import ancien as vieux, page_bas
from commun.journal import depuis_page

def _champs(b):
    noms = [f.name for f in fields(B.Bloc)] if isinstance(b, B.Bloc) or hasattr(b, "encoche") else []
    d = {n: getattr(b, n) for n in noms + ["role", "nom", "x0", "x1", "y0", "y1", "z0", "z1", "groupe"] if hasattr(b, n)}
    for n in ("fenetres", "xy", "decor", "rep"):
        if hasattr(b, n):
            d[n] = getattr(b, n)
    return type(b).__name__, d

def test_comme_bas_py():
    V = vieux("bas")
    assert [_champs(b) for b in B.blocs()] == [_champs(b) for b in V.blocs()]
    assert B.prix() == V.prix() and B.decoupe() == V.decoupe() and B.tenue() == V.tenue()
    assert (B.chant_vu(), B.rouleaux_chant(), B.contour_porte(), B.PIECES_DEBIT, B.EQUERRES) == \
           (V.chant_vu(), V.rouleaux_chant(), V.contour_porte(), V.PIECES_DEBIT, V.EQUERRES)

def test_valeurs():
    assert round(B.total(), 2) == 296.82 and B.rouleaux_chant() == 2 and B.cm(B.chant_vu() / 100) == "7,4"
    assert (B.cm(B.NIV_H), B.cm(B.Z_DESSUS), B.cm(B.PY1 - B.PY0), B.cm(B.BAIE), B.cm(B.COL_H)) == \
           ("40,7", "88,8", "114,4", "47,5", "69")
    assert len(B.prix()) == 16
    assert sum(q for _, _, q, _, _ in B.PIECES_DEBIT) == 9

def test_donnees_copiees_de_modele_py():
    M = vieux("modele")
    assert B.PANNEAU == M.PANNEAUX["D"][0] and B.EP == M.PT and B.PLATEAU_P == M.PROF
    assert {k: M.VERNIS[k] for k in ("couches", "rendement", "pots")} == B.VERNIS

def test_lit_le_meuble_haut():
    assert (B.Z_HAUT, B.Z_HAUT1, B.LED_X, B.VERSION_HAUT) == (158, 248, 191, "V6.4")

def test_changements_comme_l_ancienne_page():
    assert document.VERSION == "V8.5" and len(document.CHANGEMENTS) == 16
    assert [(c.version, c.date, c.texte) for c in depuis_page(page_bas())] == [tuple(c) for c in document.CHANGEMENTS]
```

```python
# tests/test_sdb_achats_passerelle.py
from tests.outils import RACINE
from tests.sdb_anciennes import ancien, page_achats

def test_achats_py_lit_le_nouveau_module():
    src = (RACINE / "3d/sdb/achats.py").read_text(encoding="utf-8")
    assert "import bas" not in src and "from pieces.sdb.meuble_bas import modele as B" in src

def test_pages_du_haut_et_des_achats_identiques():
    lire = lambda nom: (RACINE / nom).read_text(encoding="utf-8")    # noqa: E731
    assert ancien("achats").page() == lire("sdb-meuble-achats.html") == page_achats()
    assert ancien("haut").page() == lire("sdb-meuble-haut.html")
```

- [ ] **Step 2 : lancer, constater l'échec**

Run : `uv run -q --no-project --with pytest pytest -q tests/test_sdb_meuble_bas_modele.py tests/test_sdb_achats_passerelle.py`
Expected : FAIL (`pieces.sdb.meuble_bas` absent).

- [ ] **Step 3 : écrire `modele.py` et `document.py`, puis modifier `achats.py` et `explorations/test_v4.py`**

- [ ] **Step 4 : lancer, constater le succès**

Run : `uv run -q --no-project --with pytest pytest -q tests`
Expected : tout passe (`test_test_v4_passe` compris). Puis
`python3 3d/sdb/achats.py && python3 3d/sdb/haut.py && git status --short *.html` : rien (pages identiques).

- [ ] **Step 5 : commit**

```bash
git add pieces/sdb/meuble_bas 3d/sdb/achats.py explorations/test_v4.py tests/test_sdb_meuble_bas_modele.py tests/test_sdb_achats_passerelle.py
git commit -m "Meuble bas : modèle dans pieces/sdb/meuble_bas/, la liste d'achats le lit (page identique)

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
```

### Task 5 : Les onze dessins et la vue Plans

**Files:**
- Create: `pieces/sdb/meuble_bas/dessins.py`, `pieces/sdb/meuble_bas/vues.py`
- Test: `tests/test_sdb_meuble_bas_dessins.py`

**Interfaces:**
- Consumes : tâches 3 et 4 ; `commun.blocs_construction` (`DessinMeuble`, `vue_plans`) ; `commun.blocs.vue_lecture`.
- Produces :
  - `dessins.py` : `rect`, `trait`, `fil`, `poly_yz` (`bas:L348-362`, sur `dessin_cotes.f`) ; huit dessins cotés
    `vue_plan`, `vue_face`, `vue_porte`, `vue_placard`, `vue_colonne`, `vue_colonne_dessus`, `vue_joue`, `vue_coupe`
    (`bas:L366-567`, `CO.` → `dessin_cotes.`, `PL.text`/`PL.poly` → `dessin_cotes.text`/`.poly`, `M.` → `P.` ou `B.`)
    et trois iso `iso_ferme`, `iso_ouvert`, `eclate` (`bas:L735-737`, `MO.dessin` → `iso.dessin`, `M.CARRELAGE` →
    `P.CARRELAGE`), chacun de signature `(label: str = ARIA[k]) -> str` ;
    `ARIA: dict[str, str]` (les onze `aria-label` d'origine, inventaire § 5) ; `NOMS: dict[str, str]` (ruling 9) ;
    `DESSINS: dict[str, Callable[[str], str]]`, clés dans l'ordre du ruling 9 ;
    `legendes() -> dict[str, str]` : les huit textes sous les dessins (`bas:L587, 598, 620, 662, 663, 738, 739, 740,
    747, 748` ; clés `placard`, `porte`, `joue`, `colonne`, `colonne-dessus`, `plan`, `elevation`, `coupe`,
    `iso-ouvert`, `eclate`), mêmes formules ;
    `CSS: str` (`bas:L47-56`, `var(--tile)` → `#E9EEF0`) ; `CSS_DOCUMENT = "\n".join((dessin_cotes.CSS, iso.CSS, CSS))`
    (cet ordre : les règles `.omel` et `.otrou` du meuble bas l'emportent).
  - `vues.py` : `alts() -> dict[str, str]` (ruling 10) ; `vues(variante: str) -> dict[str, Vue]` : `ValueError` si
    `variante != ""` ; clés `plans, decoupe, montage, achats, explication` ; à cette tâche, les quatre dernières sont
    `vue_lecture(<id>, "")` (tâches 6 et 7) ; `plans = vue_plans([DessinMeuble(k, NOMS[k], DESSINS[k](alts()[k]),
    mesure=k not in ISO) for k in DESSINS], "Meuble bas", formule=<ruling 9>)` avec `ISO = ("iso", "iso-ouvert",
    "eclate")`.

- [ ] **Step 1 : écrire les tests**

```python
# tests/test_sdb_meuble_bas_dessins.py
import re
from html import escape
import pytest
from commun.css_dessins import css_dessins
from commun.modele import Document, Variante, verifier
from pieces.sdb.meuble_bas import dessins as D, vues
from tests.outils import RACINE
from tests.sdb_anciennes import dessin, page_bas, sans_aria, texte

ORDRE = ["elevation", "iso", "iso-ouvert", "eclate", "plan", "coupe", "placard", "porte", "joue", "colonne",
         "colonne-dessus"]
V = vues.vues("")

@pytest.mark.parametrize("k", ORDRE)
def test_dessin_comme_l_ancienne_page(k):
    assert D.DESSINS[k]() == dessin(page_bas(), D.ARIA[k])

def test_cinq_vues_et_verifier():
    doc = Document("sdb", "meuble-bas", "Meuble bas", "construction", (Variante("", "Meuble bas", "V8.5", ()),), vues.vues)
    verifier(doc, V)
    assert list(V) == ["plans", "decoupe", "montage", "achats", "explication"]
    with pytest.raises(ValueError):
        vues.vues("autre")

def test_plans():
    p = V["plans"]
    assert [e.k for e in p.elements] == ORDRE == list(D.DESSINS)
    assert [e.nom for e in p.elements] == ["Élévation, vue depuis la salle de bain", "Vue iso", "Sans la porte",
        "Vue éclatée", "Plan", "Coupe par la machine", "Coupe par le placard", "Porte vue de face", "Joue vue de côté",
        "Colonne vue de face", "Colonne vue de dessus"]
    assert {e.titre for e in p.elements} == {"Meuble bas"} and p.outils == ("zoom", "mesure")
    for e in p.elements:
        assert e.scene.startswith('<svg data-mesure="non"') == (e.k in ("iso", "iso-ouvert", "eclate"))
        assert sans_aria(e.scene).replace(' data-mesure="non"', "") == sans_aria(D.DESSINS[e.k]())
    assert "114,4 × 60, dessus à 88,8" in p.fiche and 'href="#decoupe"' in p.fiche and 'href="#montage"' in p.fiche

def _caps():
    return {m.group(1): texte(m.group(2)) for m in re.finditer(
        r'aria-label="([^"]*)"[^>]*>.*?</svg>(?:</div>)?<p class="cap">(.*?)</p>', page_bas(), re.S)}

def test_alts():
    a, caps = vues.alts(), _caps()
    assert a["iso"] == D.ARIA["iso"]
    assert a["iso-ouvert"].startswith("Sans la porte : ") and a["eclate"].startswith("Vue éclatée : ")
    assert a["elevation"].startswith(D.ARIA["elevation"] + ". Le nord à gauche")
    assert sorted(caps.values()) == sorted(texte(t) for t in D.legendes().values())
    for e in V["plans"].elements:
        assert f'aria-label="{escape(a[e.k], quote=True)}"' in e.scene

def test_aucune_description_visible():
    for cle, v in V.items():
        visible = texte(re.sub(r'aria-label="[^"]*"', "", "".join(e.scene for e in v.elements) + v.fiche))
        for t in D.legendes().values():
            assert texte(t) not in visible, (cle, t)

def test_classes_ont_une_regle():
    tous = [e.scene for e in V["plans"].elements]
    css = css_dessins(D.CSS_DOCUMENT, tous, ".d-sdb")
    site = (RACINE / "commun/site.css").read_text(encoding="utf-8")
    regle = lambda c, t: re.search(rf"\.{re.escape(c)}(?![\w-])", t) is not None   # noqa: E731
    classes = {c for s in tous for m in re.findall(r'class="([^"]+)"', s) for c in m.split()}
    assert {"omasse", "olibre", "ofil", "otq", "ct", "nt", "ifen", "idec", "iapp"} <= classes
    assert sorted(c for c in classes if not regle(c, css) and not regle(c, site)) == []

def test_omel_du_meuble_bas_l_emporte():
    css = css_dessins(D.CSS_DOCUMENT, [e.scene for e in V["plans"].elements], ".d-sdb")
    omel = [r for r in css.splitlines() if re.match(r"\.d-sdb \.omel\{", r)]
    assert omel[-1] == ".d-sdb .omel{fill:#fbfaf5;stroke:var(--ink);stroke-width:.25}"
    for interdit in ("JetBrains", "monospace", "var(--tile)", "ol.pose"):
        assert interdit not in D.CSS_DOCUMENT
```

(`_caps` lit les dix textes sous les dessins de l'ancienne page, chacun après le `<svg>` qu'il décrit ; s'il en lit moins
de dix, corriger l'expression sur la page de référence, pas le test des valeurs.)

- [ ] **Step 2 : lancer, constater l'échec**

Run : `uv run -q --no-project --with pytest pytest -q tests/test_sdb_meuble_bas_dessins.py`
Expected : FAIL, `ImportError` sur `dessins`.

- [ ] **Step 3 : écrire `dessins.py`, puis `vues.py`**

- [ ] **Step 4 : lancer, constater le succès**

Run : `uv run -q --no-project --with pytest pytest -q tests`
Expected : tout passe (17 tests neufs, dont 11 paramétrés).

- [ ] **Step 5 : commit**

```bash
git add pieces/sdb/meuble_bas/dessins.py pieces/sdb/meuble_bas/vues.py tests/test_sdb_meuble_bas_dessins.py
git commit -m "Meuble bas : les onze dessins repris à l'identique, vue Plans, textes sous les dessins en texte alternatif

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
```

### Task 6 : Découpe, Montage, Achats et « Les deux meubles »

**Files:**
- Create: `pieces/sdb/achats_communs.py`
- Modify: `pieces/sdb/meuble_bas/vues.py` (vues `decoupe`, `montage`, `achats`)
- Test: `tests/test_sdb_achats_communs.py`, `tests/test_sdb_meuble_bas_vues.py`

**Interfaces:**
- Consumes : tâches 4 et 5 ; `commun.blocs` (`Achat`, `tableau_achats`, `euros`, `note_source`, `vue_lecture`) ;
  `commun.blocs_construction` (`Colonne`, `tableau_debit`, `Etape`, `etapes`) ; `pieces.sdb.ancien.haut()`.
- Produces :
  - `pieces.sdb.achats_communs` :
    - `MAGASIN`, `RELEVE_V6`, `BUDGET` : copies de `M6:L819-820`, `M6:L965`, `M6:L967-968` (dicts entiers) ;
    - `prix(v: float) -> str` : l'ancien `PL.euros` (`pl:L273`), « 296,82 € », « 9,00 € », pour les textes repris ;
    - `total_haut() -> float` : `H.total_lignes(H.lignes())` de `ancien.haut()` (le haut n'est pas migré) ;
    - `deux_meubles(liens: Mapping[str, str]) -> str` : `liens` a les clés `bas` et `haut` (adresses des listes de
      chaque meuble, relatives à la page qui appelle) ; total du bas par `pieces.sdb.meuble_bas.modele.total()`, du
      haut par `total_haut()` ; HTML, dans cet ordre : `<h2>Les deux meubles</h2>`, un tableau
      `<div class="defile"><table>` (en-têtes « Meuble », « Prix du meuble entier » en `th class="d"` ; lignes
      `<a href="…">Meuble bas</a>`, `<a href="…">Meuble haut</a>`, montants `td class="num d"` par `euros` ; ligne
      `tr class="total"` « Total TTC »), `note_source` du budget (`ach:L49`, montant par `prix`), `note_source` du
      magasin (`ach:L84-86`, phrase du stock du ruling 11).
  - `vues.py` : `etapes_montage() -> list[str]` (13 `<li>` de `bas:L630-642`, sans `<li>`, mêmes formules),
    `pose_colonne() -> list[str]` (5, `bas:L675-679`) ; vues :
    - `decoupe` (ruling 13) : `tableau_debit((Colonne("Rep.", "repere"), Colonne("Pièce"), Colonne("Qté", "nombre"),
      Colonne("Longueur", "cote"), Colonne("Largeur", "cote"), Colonne("Ép.", "cote")), [(r, n, q, cm(lg), cm(la),
      cm(EP)) …], titre="Pièces")`, puis le paragraphe `bas:L625` (« <b>B à G</b> », les lettres tirées de `decoupe()`),
      la liste `bas:L575`, `bas:L627`, puis `<h2>Finition</h2>` et `bas:L622` ;
    - `montage` (ruling 12) : `etapes([Etape("", f"<p>{t}</p>") for t in etapes_montage()], titre="Montage")`,
      `<p>Les 6 équerres :</p>` (nombre par `N_EQUERRES`) et la liste `bas:L576`, puis
      `etapes([…pose_colonne()], titre="Pose de la colonne")` ;
    - `achats` (ruling 11) : `<h2>Meuble bas</h2>`, `<p>` `bas:L655` sans le lien, `<p>` `ach:L54` sans le lien,
      `tableau_achats([Achat(nom, ref, q, pu, note) for nom, ref, q, pu, st in prix()], "Total du meuble bas",
      arrondi=False)` (note : `f"{q} × {euros(pu)}"` si `q != 1`, puis `f"stock : {st}"` si `st` n'est pas `None`,
      joints par « , »), `note_source(<ach:L55-57>)` (montants par `prix`), puis
      `deux_meubles({"bas": "#achats", "haut": "../../sdb-meuble-achats.html#haut-seul"})`.

- [ ] **Step 1 : écrire les tests**

```python
# tests/test_sdb_achats_communs.py
from pieces.sdb import achats_communs as AC
from tests.sdb_anciennes import ancien, corrige, morceaux, page_achats, section, texte

S = AC.deux_meubles({"bas": "#achats", "haut": "../../sdb-meuble-achats.html#haut-seul"})

def test_donnees_comme_modele_py():
    M = ancien("modele")
    assert (AC.MAGASIN, AC.RELEVE_V6, AC.BUDGET) == (M.MAGASIN, M.RELEVE_V6, M.BUDGET)

def test_deux_meubles():
    assert S.startswith("<h2>Les deux meubles</h2>") and round(AC.total_haut(), 2) == 179.82
    assert '<a href="#achats">Meuble bas</a>' in S and '<a href="../../sdb-meuble-achats.html#haut-seul">Meuble haut</a>' in S
    for montant in ("296,82 €", "179,82 €", "476,64 €", "428,33 €"):
        assert montant in S
    assert AC.prix(9) == "9,00 €" and AC.prix(296.82) == "296,82 €"

def test_rien_ne_se_perd_de_la_page_d_achats():
    vieux = section(page_achats(), "deux-meubles")
    note = page_achats().split('<p class="note">Sauf mention', 1)[1].split("</p>", 1)[0]
    for m in morceaux(vieux) + [texte("Sauf mention" + note)]:
        assert corrige(m) in texte(S), m
```

```python
# tests/test_sdb_meuble_bas_vues.py
import re
from pieces.sdb.meuble_bas import modele as B, vues
from tests.sdb_anciennes import corrige, entre, morceaux, page_achats, page_bas, section, texte

V = vues.vues("")
def _s(cle): return V[cle].elements[0].scene

def test_decoupe():
    s = _s("decoupe")
    assert s.startswith("<h2>Pièces</h2>") and s.split("<tbody>")[1].count("<tr>") == 7 and "<h2>Finition</h2>" in s
    assert "B à G : trois tablettes" in texte(s) and "Tablette 3, 250 × 50 : C (85) + G (69)" in texte(s)
    for m in morceaux(entre(page_bas(), '<h3 id="finition">', "<h3>Montage</h3>")):
        assert corrige(m) in texte(s), m

def test_montage():
    s = _s("montage")
    assert [h for h in re.findall(r"<h2>(.*?)</h2>", s)] == ["Montage", "Pose de la colonne"]
    assert s.count('<ol class="etapes"') == 2 and len(vues.etapes_montage()) == 13 and len(vues.pose_colonne()) == 5
    assert "<b>Mesurer l'alcôve</b>" in s and "Outils à réunir" not in s
    for m in morceaux(entre(page_bas(), "<h3>Montage</h3>", "<h3>Tenue</h3>")
                      + entre(page_bas(), "<h3>Pose de la colonne</h3>", '<h2 id="plan">')):
        assert corrige(m) in texte(s), m

def test_achats():
    s = _s("achats")
    assert re.findall(r"<h2>(.*?)</h2>", s) == ["Meuble bas", "Les deux meubles"]
    table = s.split("<tbody>")[1].split("</tbody>")[0]
    assert table.count("<tr>") == 16 and "Total du meuble bas" in table and "296,82 €" in table
    for nom, ref, q, pu, st in B.prix():
        assert ref in table and nom.replace("'", "&#x27;") in table
    assert "2 × 16,50 €, stock : 25" in table and "stock : 50" in table
    assert "Le détail est dans la liste d'achats." in texte(s) and "sdb-meuble-achats.html#bas" not in s
    vieux = entre(page_bas(), "<h3>Achats</h3>", "</p>") + section(page_achats(), "bas").split("<div", 1)[0] \
        + "<p" + section(page_achats(), "bas").split('<p class="note">', 1)[1]
    for m in morceaux(vieux):
        assert corrige(m) in texte(s), m

def test_sans_point_median_ni_chasse_fixe():
    for cle in ("decoupe", "montage", "achats"):
        assert "·" not in _s(cle) and "mono" not in _s(cle), cle
```

- [ ] **Step 2 : lancer, constater l'échec**

Run : `uv run -q --no-project --with pytest pytest -q tests/test_sdb_achats_communs.py tests/test_sdb_meuble_bas_vues.py`
Expected : FAIL (`achats_communs` absent ; vues vides).

- [ ] **Step 3 : écrire `achats_communs.py`, puis remplir les trois vues de `vues.py`**

- [ ] **Step 4 : lancer, constater le succès**

Run : `uv run -q --no-project --with pytest pytest -q tests`
Expected : tout passe (7 tests neufs).

- [ ] **Step 5 : commit**

```bash
git add pieces/sdb/achats_communs.py pieces/sdb/meuble_bas/vues.py tests/test_sdb_achats_communs.py tests/test_sdb_meuble_bas_vues.py
git commit -m "Meuble bas : Découpe, Montage, Achats, et la section commune « Les deux meubles »

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
```

### Task 7 : Explication, versions figées et page d'achats figée

**Files:**
- Create: `pieces/sdb/meuble_bas/explication.py`, `pieces/sdb/archives.py`, `archive/sdb-meuble-achats-v8.5.html`
- Modify: `pieces/sdb/meuble_bas/vues.py` (la ligne `"explication": …`), `pieces/sdb/meuble_bas/document.py` (`FIGEES`)
- Test: `tests/test_sdb_meuble_bas_explication.py`

**Interfaces:**
- Consumes : tâches 4 à 6 ; `commun.blocs` (`tete`, `chiffres`, `a_verifier`, `note_source`, `vue_lecture`) ;
  `achats_communs.prix`.
- Produces :
  - `explication.vue_explication() -> Vue` (ruling 14), contenu dans l'ordre :
    1. `tete(<bas:L743>)`, lien `href="../../archive/sdb-meuble-v4-bas.html"` ;
    2. `chiffres([(f"{cm(P.Y1 - P.Y0)} × {P.ALCOVE['nord']} à {P.ALCOVE['sud']}", "Alcôve (cm)"), (prix(total()),
       "Meuble bas entier"), (str(sum(q for _, _, q, _, _ in PIECES_DEBIT)), "Panneaux à découper"),
       (str(len(etapes_montage())), "Étapes de montage")])` ;
    3. `<h2>Structure</h2>` et `bas:L578-585`, `<h3>Placard</h3>` et `bas:L588-596`, `<h3>Porte</h3>` et
       `bas:L599-610`, `<h3>Pieds</h3>` et `bas:L612-618`, `<h3>Tenue</h3>` et `bas:L647-653` (tableau en
       `<div class="defile"><table>`, plus de `class="scroll"` ; « 2,5 » par `nombre(E_AGGLO / 1e9)` et « 4,1 » par
       `cm(t["porte"])`, ruling 15) ;
    4. `<h2>Colonne de prises</h2>`, `bas:L661` et `bas:L664-672` ;
    5. `<h2>Mesures</h2>`, `bas:L723-729` (deux tableaux en `<div class="defile">`, la valeur « Page du meuble haut
       {VERSION_HAUT} ») ;
    6. `a_verifier([<bas:L730 sans « À confirmer : », première lettre en capitale>, f"Profondeur de la salle de bain :
       {cm(P.SDB['p'])} sur le plan du meuble, {cm(max(y for _, y in P.SOL))} sur le plan de l'appartement.",
       f"Gonds de la porte d'entrée : à {P.GONDS} du mur du fond sur le plan du meuble (relevé client), à
       {cm(P.X1 - P.PORTE_ACCUEIL['x1'])} sur le plan de l'appartement."])` ;
    7. `note_source("Repère : origine à l'angle nord-ouest intérieur, x vers l'est, y vers le sud, z depuis le sol,
       cotes en cm. Cotes et données : pieces/sdb/piece.py pour la pièce, pieces/sdb/meuble_bas/ pour le meuble.")`.
  - `archives.FIGEES_COMMUNES: tuple[tuple[str, str], ...]` et `document.FIGEES = (<les quatre propres>,) +
    FIGEES_COMMUNES` (ruling 8, libellés et chemins exacts).
  - `archive/sdb-meuble-achats-v8.5.html` : `sdb-meuble-achats.html` dont les cinq attributs `href="index.html"`,
    `href="favicon.svg"`, `href="apple-touch-icon.png"`, `href="sdb-meuble-bas.html"`, `href="sdb-meuble-haut.html"`
    prennent le préfixe `../` ; rien d'autre ne change.

- [ ] **Step 1 : figer la page d'achats**

```bash
python3 - <<'EOF'
import re, pathlib
src = pathlib.Path("sdb-meuble-achats.html").read_text(encoding="utf-8")
fig = re.sub(r'href="(index\.html|favicon\.svg|apple-touch-icon\.png|sdb-meuble-bas\.html|sdb-meuble-haut\.html)"',
             r'href="../\1"', src)
pathlib.Path("archive/sdb-meuble-achats-v8.5.html").write_text(fig, encoding="utf-8")
EOF
diff <(sed 's#href="\.\./#href="#g' archive/sdb-meuble-achats-v8.5.html) sdb-meuble-achats.html && echo identique
```

Expected : `identique`.

- [ ] **Step 2 : écrire les tests**

```python
# tests/test_sdb_meuble_bas_explication.py
import re
from pieces.sdb.meuble_bas import document, vues
from tests.outils import RACINE
from tests.sdb_anciennes import corrige, morceaux, page_bas, texte

V = vues.vues("")
S = V["explication"].elements[0].scene

def test_ordre_et_chiffres():
    assert re.findall(r"<h2>(.*?)</h2>", S) == ["Structure", "Colonne de prises", "Mesures", "À vérifier sur place"]
    assert re.findall(r"<h3>(.*?)</h3>", S) == ["Placard", "Porte", "Pieds", "Tenue", "Relevées",
                                                "Reprises des versions précédentes", "Ce qu&#x27;il reste"] or \
           re.findall(r"<h3>(.*?)</h3>", S) == ["Placard", "Porte", "Pieds", "Tenue", "Relevées",
                                                "Reprises des versions précédentes", "Ce qu'il reste"]
    assert re.findall(r"<dt>(.*?)</dt>", S) == ["115 × 62 à 68", "296,82 €", "9", "13"]

def test_corrections_et_a_verifier():
    assert "2,5 GPa" in S and "≈ 4,1 kg" in S and "2.5" not in S and "4.1 kg" not in S
    a = S.split("<h2>À vérifier sur place</h2>", 1)[1]
    assert a.count("<li>") == 3 and "Ces 7 cm d'écart" in texte(a)
    assert "160 sur le plan du meuble, 156 sur le plan de l'appartement" in texte(a)
    assert "à 69 du mur du fond sur le plan du meuble (relevé client), à 78 sur le plan de l'appartement" in texte(a)

def test_liens_et_repere():
    assert 'href="../../archive/sdb-meuble-v4-bas.html"' in S and "3d/sdb" not in S and "pieces/sdb/piece.py" in S
    assert "Repère : origine à l'angle nord-ouest intérieur, x vers l'est, y vers le sud, z depuis le sol, cotes en cm." \
        in texte(S)

def _tout():
    return texte("".join(e.nom + e.scene + v.fiche for v in V.values() for e in v.elements))

def test_rien_ne_se_perd():
    """Chaque paragraphe, puce, titre et cellule de l'ancienne page est dans une vue, sauf les retraits du tableau."""
    corps = page_bas().split("<main", 1)[1]
    retires = ("Repère : origine",)          # note finale : son repère est vérifié plus haut, ses chemins sont retirés
    for m in morceaux(corps):
        if not m.startswith(retires):
            assert corrige(m) in _tout(), m

def test_liens_externes_gardes():
    vieux = set(re.findall(r'href="(https://www\.ikea[^"]+)"', page_bas()))
    tout = "".join(e.scene for v in V.values() for e in v.elements)
    assert len(vieux) == 3 and vieux <= set(re.findall(r'href="(https?://[^"]+)"', tout))

def test_versions_figees():
    f = document.FIGEES
    assert len(f) == 11 and len({v for v, _ in f}) == 11 and len({c for _, c in f}) == 11
    for _, chemin in f:
        assert (RACINE / chemin).is_file(), chemin
    assert ("Liste d'achats V8.5", "archive/sdb-meuble-achats-v8.5.html") in f and ("V6.2", "archive/sdb-meuble-v4-bas.html") in f

def test_sans_point_median_ni_chasse_fixe():
    assert "·" not in S and "mono" not in S and 'class="scroll"' not in S and 'class="note"' not in S
```

(Le test d'ordre accepte l'apostrophe échappée ou non dans le `<h3>` : `tete` et les blocs échappent leurs titres, un
`<h3>` écrit par la page ne l'est pas. Garder la forme que produit le code, et retirer l'autre branche du test.)

- [ ] **Step 3 : lancer, constater l'échec**

Run : `uv run -q --no-project --with pytest pytest -q tests/test_sdb_meuble_bas_explication.py`
Expected : FAIL (Explication vide, `document.FIGEES` absent).

- [ ] **Step 4 : écrire `archives.py`, `explication.py`, `FIGEES`, brancher `vues.vues`**

- [ ] **Step 5 : lancer, constater le succès**

Run : `uv run -q --no-project --with pytest pytest -q tests`
Expected : tout passe (7 tests neufs).

- [ ] **Step 6 : commit**

```bash
git add pieces/sdb/archives.py pieces/sdb/meuble_bas/explication.py pieces/sdb/meuble_bas/vues.py pieces/sdb/meuble_bas/document.py archive/sdb-meuble-achats-v8.5.html tests/test_sdb_meuble_bas_explication.py
git commit -m "Meuble bas : Explication, versions figées, et la liste d'achats V8.5 figée dans archive/

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
```

### Task 8 : Bascule

**Files:**
- Modify: `pieces/sdb/meuble_bas/document.py` (ajout à la fin)
- Modify: `site.py:19` (import ajouté après), `site.py:29` (la `Passerelle` du meuble bas), `site.py:61` (ancres, après
  `ANCRES_CHAMBRE`), `site.py:62-71` (`REDIRECTIONS`)
- Modify: `justfile:184-189` (recette `sdb` réécrite, recette `sdb-meuble-bas` ajoutée avant elle)
- Modify: `explorations/test_v4.py` (`test_page_achats_liens_existent`)
- Delete (`git rm`) : `sdb-meuble-bas.html`, `3d/sdb/bas.py`, `3d/sdb/test_bas.py`
- Create: `tests/navigateur/sdb-meuble-bas.js`
- Test: `tests/test_sdb_meuble_bas_document.py`

**Interfaces:**
- Consumes : `vues.vues`, `dessins.CSS_DOCUMENT`, `document.VERSION`, `CHANGEMENTS`, `FIGEES` ;
  `commun.journal.entrees(site, racine)` ; `tests.outils.charger_site`.
- Produces : `pieces.sdb.meuble_bas.document.DOCUMENT` = `Document("sdb", "meuble-bas", "Meuble bas", "construction",
  (Variante("", "Meuble bas", VERSION, tuple(Changement(*c) for c in CHANGEMENTS), FIGEES),), vues.vues,
  css=dessins.CSS_DOCUMENT)`, construit à la première lecture par `_document()` et `__getattr__(nom)` (modèle :
  `pieces/entree/amenagement/document.py:308-322`, imports de `vues`, `dessins`, `commun.modele` dans la fonction) ;
  `site.ANCRES_SDB_BAS` et sa `Redirection` ; le script navigateur, `async page => {…}` qui renvoie
  `{ok, echecs, erreurs}`, marqué `@site reel` dans son commentaire de tête (modèle : `tests/navigateur/salon-enfilade.js`,
  fonctions recopiées : chaque script est autonome).

- [ ] **Step 1 : écrire les tests**

```python
# tests/test_sdb_meuble_bas_document.py
import subprocess
from commun.journal import entrees
from commun.modele import Changement
from pieces.sdb.meuble_bas import dessins, document, vues
from tests.outils import RACINE, charger_site

ANCRES = {"iso": "plans?k=iso", "structure": "explication", "placard": "explication", "f-placard": "plans?k=placard",
          "porte": "explication", "f-porte": "plans?k=porte", "pieds": "explication", "f-joue": "plans?k=joue",
          "finition": "decoupe", "colonne": "explication", "f-colonne": "plans?k=colonne",
          "f-colonne-dessus": "plans?k=colonne-dessus", "plan": "plans?k=plan", "f-plan": "plans?k=plan",
          "elevation": "plans?k=elevation", "f-face": "plans?k=elevation", "coupe": "plans?k=coupe",
          "f-coupe": "plans?k=coupe", "mesures": "explication"}

def test_document():
    d = document.DOCUMENT
    assert (d.piece, d.id, d.nom, d.type, d.css, d.generer, d.options) == \
        ("sdb", "meuble-bas", "Meuble bas", "construction", dessins.CSS_DOCUMENT, vues.vues, ())
    (v,) = d.variantes
    assert (v.id, v.nom, v.version, v.figees) == ("", "Meuble bas", "V8.5", document.FIGEES)
    assert v.changements == tuple(Changement(*c) for c in document.CHANGEMENTS) and len(v.changements) == 16
    assert not hasattr(document, "CACHE_RENDU")

def test_site_declare_le_meuble_bas():
    (sdb,) = [p for p in charger_site().SITE.pieces if p.id == "sdb"]
    assert sdb.documents[0] is document.DOCUMENT and sdb.documents[1].page == "sdb-meuble-haut.html"

def test_redirection():
    (r,) = [r for r in charger_site().REDIRECTIONS if r.ancienne == "sdb-meuble-bas.html"]
    assert (r.cible, r.ancres, r.motifs, r.pages) == ("sdb/meuble-bas/", ANCRES, (),
                                                      {"changements": "sdb/meuble-bas/historique.html"})
    assert not [x for x in charger_site().REDIRECTIONS if x.ancienne == "sdb-meuble-achats.html"]

def test_journal_garde_seize_changements():
    lignes = [e for e in entrees(charger_site().SITE, RACINE) if (e.piece, e.document) == ("Salle de bain", "Meuble bas")]
    assert [e.version for e in lignes] == [c[0] for c in document.CHANGEMENTS]

def test_ancienne_page_et_generateur_retires():
    suivis = subprocess.run(["git", "ls-files"], cwd=RACINE, capture_output=True, text=True).stdout.split()
    for nom in ("sdb-meuble-bas.html", "3d/sdb/bas.py", "3d/sdb/test_bas.py"):
        assert nom not in suivis and not (RACINE / nom).exists(), nom
    for nom in ("sdb-meuble-achats.html", "3d/sdb/achats.py", "3d/sdb/haut.py", "3d/sdb/modele.py", "3d/sdb/cad.py"):
        assert nom in suivis, nom

def test_recettes():
    j = (RACINE / "justfile").read_text(encoding="utf-8")
    assert "sdb-meuble-bas:\n    python3 site.py sdb/meuble-bas\n" in j
    sdb = j.split("\nsdb:\n", 1)[1].split("\n\n", 1)[0]
    assert "bas.py" not in sdb and "python3 3d/sdb/achats.py" in sdb and "python3 site.py sdb/meuble-bas" in sdb
```

- [ ] **Step 2 : lancer, constater l'échec**

Run : `uv run -q --no-project --with pytest pytest -q tests/test_sdb_meuble_bas_document.py`
Expected : FAIL (`AttributeError: … has no attribute 'DOCUMENT'`).

- [ ] **Step 3 : déclarer `DOCUMENT`, basculer `site.py`, réécrire les recettes, retirer l'ancienne page**

- `document.py`, à la fin : `_document()` et `__getattr__`, comme à l'entrée.
- `site.py` : `from pieces.sdb.meuble_bas import document as sdb_meuble_bas` après la ligne 19 ; la ligne 29 devient
  `sdb_meuble_bas.DOCUMENT,` ; après `ANCRES_CHAMBRE`, le commentaire « anciennes ancres de sdb-meuble-bas.html : ses
  titres h2 et h3, et ses figures (f-…) » et `ANCRES_SDB_BAS = {…}` (le dict `ANCRES` du test) ; à la fin de
  `REDIRECTIONS` : `Redirection("sdb-meuble-bas.html", "sdb/meuble-bas/", ANCRES_SDB_BAS, (),
  {"changements": "sdb/meuble-bas/historique.html"}),`.
- `justfile`, à la place des lignes 184-189 :

```
# Salle de bain, meuble bas : reconstruit sa page (site/sdb/meuble-bas/) depuis pieces/sdb/meuble_bas/
sdb-meuble-bas:
    python3 site.py sdb/meuble-bas

# Meuble linge SDB : régénère sdb-meuble-haut.html (haut.py) et sdb-meuble-achats.html (achats.py) depuis 3d/sdb/modele.py, la page du meuble bas, puis le modèle FreeCAD
sdb:
    python3 3d/sdb/haut.py
    python3 3d/sdb/achats.py
    python3 site.py sdb/meuble-bas
    /Applications/FreeCAD.app/Contents/Resources/bin/freecadcmd 3d/sdb/cad.py
```

- `explorations/test_v4.py`, `test_page_achats_liens_existent` : dans la boucle des liens, `if v == "sdb-meuble-bas.html":
  continue` avec le commentaire « redirigée vers sdb/meuble-bas/ depuis sa migration (site.py) ».
- `git rm sdb-meuble-bas.html 3d/sdb/bas.py 3d/sdb/test_bas.py`.

- [ ] **Step 4 : lancer les tests**

Run : `uv run -q --no-project --with pytest pytest -q tests`
Expected : tout passe, dont les 6 tests neufs, `tests/test_construction.py::test_site_py_tient_documents_et_redirections`
et `test_documents_declares` (aucun lien mort dans `sdb/meuble-bas/` ni son historique : les onze versions figées et
`../../sdb-meuble-achats.html` existent sous `site/`). Les tests qui comparaient à `bas.py` en mémoire sautent
(`test_comme_bas_py`) ; ceux qui lisent les copies de `tests/fixtures/sdb/` passent.

- [ ] **Step 5 : construire le site et lire `git status`**

Run : `python3 site.py && git status --short site/ && grep -c "Salle de bain › Meuble bas" site/journal.html`
Expected : sous `site/`, seulement `sdb/meuble-bas/index.html`, `sdb/meuble-bas/dessins.css`,
`sdb/meuble-bas/historique.html` et `archive/sdb-meuble-achats-v8.5.html` (nouveaux), `sdb-meuble-bas.html` (devenue
redirection), `journal.html`, `index.html` (la salle de bain mène à `sdb/meuble-bas/`) et les menus et historiques des
documents déjà migrés (`entree/…`, `salon/enfilade/…`, `chambre/…` : lien et pastille V8.5 du meuble bas) ; dans
`site/entree/`, les seuls mots changés sont ceux du menu (`git diff --word-diff=porcelain site/entree | grep
'^[-+][^-+]' | sort -u`). Le décompte du journal : 16 (ou le nombre de lignes équivalent selon le balisage ; le test
`test_journal_garde_seize_changements` fait foi).

- [ ] **Step 6 : écrire le script navigateur `tests/navigateur/sdb-meuble-bas.js`**

Vérifications, chacune une entrée d'`echecs` si elle échoue :
1. À 1440 × 900, 1100 × 800 et 390 × 844 : `DOC = ${BASE}/sdb/meuble-bas/`, chaque vue (`plans`, `decoupe`, `montage`,
   `achats`, `explication`) et chaque repère de Plans (les onze du ruling 9) : aucune erreur de console, aucune
   réponse ≥ 400, `debordements` vide (aucun défilement horizontal à 390 px).
2. `DOC` sans fragment montre Plans, élément `elevation` ; aucun `#c-comp`, aucun `#c-variante`, pas de
   « Personnaliser ».
3. Mesurer : sur `#plans?k=elevation`, activer `.b-mesure`, cliquer les deux bouts de la ligne `line.dim` la plus
   longue (coordonnées écran par `getScreenCTM`) : « Mesuré : 115 cm ». Sur `#plans?k=iso`, `.b-mesure` est caché.
4. Fiche de Plans : les liens « Découpe » et « Montage » mènent à `#decoupe` et `#montage`.
5. Dessins : dans chaque `svg` visible de Plans, aucun élément de forme ou de texte dont le `fill` calculé est
   `rgb(0, 0, 0)` ; aucun `text` dont la boîte (`getBBox`) sort du `viewBox` ; une exception, si un dessin repris à
   l'identique en a une, est listée dans `GARDES` (repère et raison) et va « Au client ».
6. Achats : « 296,82 € » et « 476,64 € » ; le lien « Meuble haut » ouvre `/sdb-meuble-achats.html#haut-seul` (statut
   200).
7. Anciennes adresses : `/sdb-meuble-bas.html#f-placard` → `/sdb/meuble-bas/#plans?k=placard` ; `#finition` →
   `#decoupe` ; `#structure` → `#explication` ; `#f-face` → `#plans?k=elevation` ; `#changements` →
   `/sdb/meuble-bas/historique.html` ; `#inconnue` et sans fragment → `/sdb/meuble-bas/` sans fragment.
8. Historique : seize `ol.fil li`, la première en V8.5 ; onze liens de versions figées, chacun en statut 200.
9. Passerelles : `/sdb-meuble-achats.html` et `/sdb-meuble-haut.html` s'ouvrent ; sur la première, le lien « Meuble
   bas » arrive sur `/sdb/meuble-bas/`.
10. Accueil : la salle de bain du plan mène à `sdb/meuble-bas/`.
11. Sans JavaScript (nouveau contexte, `javaScriptEnabled: false`) : les cinq sections se lisent l'une sous l'autre
    (« Pièces », « Pose de la colonne », « Les deux meubles », « Mesures » visibles).

- [ ] **Step 7 : vérifier et lancer le script**

Run : `node --check tests/navigateur/sdb-meuble-bas.js && grep -c "@site reel" tests/navigateur/sdb-meuble-bas.js`
Expected : aucune erreur, puis `1`.
Run : `PORT=8861 SESSION=refonte-sdb-meuble-bas-1 tests/navigateur/lancer.sh tests/navigateur/sdb-meuble-bas.js`
Expected : `"ok": true`, aucun échec, aucune erreur. Un échec dans la page se corrige dans la tâche concernée, puis on
relance. Puis `PORT=8862 SESSION=refonte-sdb-meuble-bas-2 tests/navigateur/lancer.sh tests/navigateur/entree.js` :
`"ok": true` (le menu de l'entrée change).

- [ ] **Step 8 : remettre `site/` et commiter**

```bash
git checkout -- site && git clean -fdq site
git status --short    # attendu : seulement les fichiers de cette tâche
git add pieces/sdb/meuble_bas/document.py site.py justfile explorations/test_v4.py tests/navigateur/sdb-meuble-bas.js tests/test_sdb_meuble_bas_document.py
git commit -m "Meuble bas : bascule, le document remplace la passerelle, sdb-meuble-bas.html redirige

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
```

(`git rm` a déjà mis les trois suppressions dans l'index.)
