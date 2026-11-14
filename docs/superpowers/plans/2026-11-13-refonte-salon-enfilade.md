# Salon, enfilade : migration de la page, plan d'implémentation

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal :** remplacer l'ancienne page `salon-enfilade.html` par le document de construction `salon/enfilade/` (Plans,
Découpe, Montage, Achats, Explication), sans rien perdre de son contenu, puis basculer l'ancienne adresse en redirection.

**Architecture :** les données sont déjà dans `pieces/salon/enfilade/document.py` et `volumes.py` (préparation du
salon). Ce plan ajoute, dans le même paquet, les calculs de la page (`chiffrage.py`), ses dessins et leur CSS
(`dessins.py`), les quatre vues de construction (`vues.py`) et l'Explication (`explication.py`), tous bâtis sur les blocs
du socle (`commun.blocs`, `commun.blocs_construction`). Le `DOCUMENT` n'est déclaré qu'à la bascule (dernière tâche),
avec son entrée dans `site.py` et sa `Redirection` : un `DOCUMENT` présent sur le disque sans entrée dans `site.py`
fait échouer `tests/test_construction.py::test_site_py_tient_documents_et_redirections`.

**Tech Stack :** Python 3 (bibliothèque standard), pytest par `uv`, `playwright-cli` pour le script navigateur.

**Spec :** `docs/superpowers/specs/2026-11-13-refonte-site-design.md` ; consignes de la migration :
`/Users/nvi/code/work/personal/plan/.superpowers/sdd/2026-11-13-refonte-pages/consignes.md` (noté `REGISTRE/consignes.md`) ;
inventaire de l'ancienne page : `REGISTRE/salon-enfilade/inventaire.md` ; blocs du socle : `REGISTRE/socle/rapport.md` ;
données du salon : `REGISTRE/salon-preparation/rapport.md`. `REGISTRE` =
`/Users/nvi/code/work/personal/plan/.superpowers/sdd/2026-11-13-refonte-pages`.

Worktree : `/Users/nvi/code/work/personal/plan-wt/salon-enfilade`, branche `refonte-salon-enfilade` (base `965af34`).
Chaque commande commence par `cd /Users/nvi/code/work/personal/plan-wt/salon-enfilade && …`.

Notation des sources : `enf:L…` = ligne de `3d/salon/enfilade.py` (l'ancien générateur, lu, jamais modifié) ; `page:L…`
= ligne de `salon-enfilade.html` ; `plan.py:L…` = ligne de `3d/salon/plan.py`. Dans `enf`, `virg(x)` à un argument est la
fonction locale (`enf:L22`), qui est exactement `pieces.salon.meubles.cote` ; `C.virg(x, n)` est `cote(x, n)` ; `f` est
`commun.dessin.f` ; `euros` est `chiffrage.prix` (tâche 1) ; `M.CANAPE`, `M.ALLEE_ENFILADE` sont dans
`pieces.salon.amenagement.document`, `M.MONTANTS` dans `pieces.salon.etageres.document`, `M.VERSION` n'est plus lu.

## Rulings du plan

Mode autonome : chaque décision est prise seule, option réversible.

1. Ruling : document de construction à une seule variante, `Variante("", "Enfilade", "V1.6", <7 Changement>, figees=())`,
   construit à la première lecture (`__getattr__` du module, comme `pieces/entree/amenagement/document.py:318`) — `vues`
   importe `amenagement.document`, qui importe `enfilade.document` : un `DOCUMENT` construit à l'import ferait un import
   circulaire — si faux : construire `DOCUMENT` dans un module à part.
2. Ruling : `DOCUMENT` ajouté seulement à la bascule (tâche 6) ; avant, les tests construisent un `Document` d'essai —
   le test du socle exige qu'un `DOCUMENT` du disque soit dans `site.py` avec sa `Redirection` — si faux : rien, l'ordre
   des tâches seul change.
3. Ruling : ni `CACHE_RENDU`, ni `rendu.py`, ni recette de rendu ou d'aperçu, ni Blender (décision du contrôleur :
   `3d/salon/rendu_meubles.py` n'est déplacé par aucune page) ; les deux images sont copiées telles quelles en
   `site/salon/enfilade/rendus/iso.jpg` et `ouverte.jpg`, sans empreinte, et restent « à rendre » (elles montrent la
   composition A, la page décrit C) — si faux : la tâche de suite des rendus ajoute `CACHE_RENDU` et la recette.
4. Ruling : Mesurer donne des cm sur les dessins cotés : `dessins.en_cm` ramène chaque dessin à 1 unité = 1 cm (viewBox
   divisé par l'échelle `k` du dessin, contenu dans `<g transform="scale(1/k)">`), le dessin restant identique à la
   référence — les anciens dessins sont à l'échelle 3,4 ; 5 ; 3 ; 2,6 et `site.js` mesure en unités du viewBox — si faux :
   retirer `en_cm` (Mesurer affiche alors des valeurs fausses) ou passer `mesure=False`.
5. Ruling : la vue Achats passe par le bloc `commun.blocs.achats` (Article, Référence, Qté, Prix) ; le statut (« relevé »
   ou « estimé »), le prix unitaire et le lien « fiche » ou « repère » vont dans la note de chaque `Achat` ; les liens des
   magasins vont dans le paragraphe d'introduction ; « Total TTC (variante C) » devient « Total » du bloc et la
   composition est nommée dans le paragraphe du total. L'option 7 de l'inventaire (renommer la colonne « Prix » en
   « Statut ») est remplie autrement : le statut est écrit en clair dans la note — spec : « les achats sont un tableau
   (article, référence, quantité, prix) avec le total » — si faux : un tableau propre à la page à sept colonnes.
6. Ruling : montants des tableaux d'achats au format du socle (`commun.blocs.euros`, « 1027,95 € », `arrondi=False`) ;
   tous les textes repris gardent le format de l'ancienne page (`chiffrage.prix`, « 1 027,95 € », « 109,00 € ») — un
   texte repris garde ce qu'il avait (consignes) — si faux : passer les textes à `euros`.
7. Ruling : la colonne « Où · note » du débit devient deux colonnes, « Où » (`detail`) et « Note » (`note`) ; les cinq
   lignes de groupe deviennent la légende des lettres de repère dans le sous-titre (« A : caissons. B : façades et joue
   (chêne visible). … ») — `tableau_debit` n'a pas de ligne de groupe ; le repère porte déjà la lettre du groupe — si
   faux : un `tableau_debit` par groupe.
8. Ruling : plan de découpe en deux titres : `<h2>Plan de découpe</h2>` et le paragraphe (refente, trait de scie,
   légende chêne et chute), puis `calepinage(..., titre="Tablette chêne lamellé-collé 200 × 60 × 1,8 × 10")` (un `h2` au
   lieu de l'ancien `h3`) — `calepinage` écrit toujours son `h2` avant les figures — si faux : un bloc commun à sous-titre.
9. Ruling : les titres des dix panneaux restent visibles (`Calepin.titre`), virgule à la place du point médian (« chêne 18
   n° 1, 200 × 60, chute 20 % ») — option 6 de l'inventaire : un titre avec des données, pas une description.
10. Ruling : les tableaux de l'Explication (six compositions, STOCKHOLM, METOD : dimensions, poste par poste, totaux,
    achats de la composition mixte, portes noires) restent des tableaux propres à la page, `<div class="defile"><table>`,
    colonnes d'origine ; la pastille « retenu » devient le mot « retenu » en clair ; plus de classe `mono` ni `badge` —
    option 4 de l'inventaire et décision du contrôleur : comparaisons entières dans l'Explication.
11. Ruling : Explication dans l'ordre de l'ancienne page : tête (chapô et rendu `iso` à côté), chiffres clés, « Le
    meuble », « Rendus 3D » (les deux images, l'`iso` revient donc deux fois), « Construction », « Matériaux », les deux
    comparaisons, « Points à valider », remarque finale — inventaire § 2 — si faux : retirer la figure de la tête.
12. Ruling : huit chiffres clés calculés : cotes hors tout, total des matériaux, volume utile, repères, pièces, étapes,
    dégagement devant la porte ouverte de M1, dégagement devant le tiroir sorti — inventaire § 2 et question 5.
13. Ruling : erreurs d'affichage corrigées depuis le modèle et listées pour « Au client » : « Six portes » → « Quatre
    portes » (alt de l'élévation) ; poids d'un caisson « 1361 kg » → « 17 kg » (formule refaite pièce par pièce) ;
    « 3.8 » → « 3,8 » (Fixation au mur) ; « 18.3 » → « 18,3 » (Finition). Le changement V1.3 garde « six portes
    identiques » (historique) — consignes, « Erreurs de l'ancienne page ».
14. Ruling : titre de la fiche de Plans « Enfilade du mur ouest » (le `h1` de l'ancienne page) ; Plans sans légende ;
    boutons « Élévation », « Vue iso », « Iso ouverte », « Profils », « Dessus », « Éclatée » ; Mesurer sur les quatre
    dessins cotés, pas sur les deux iso.
15. Ruling : CSS des dessins propre à la page (`dessins.CSS`), toutes ses règles de dessin sous `svg.enf`, sans police à
    chasse fixe ; le jeton absent `--sofa` est remplacé par la couleur claire de `plan.py:L378` (`#C9BFAE`), sans jeton
    ajouté à `commun/site.css` — si faux : ajouter `--sofa` au socle.
16. Ruling : Montage : `etapes(..., titre="Outils et montage", outils=<les cinq outils>)`, onze étapes sans titre (la
    maquette en a, l'ancienne page non : rien d'inventé), note finale en remarque.
17. Ruling : le paragraphe d'introduction des achats est le chapô de la vue Achats, avant le `h2` « Achats et prix » du
    bloc ; l'outillage hors total est une liste simple après les tableaux.
18. Ruling : remarque finale : le fichier des dimensions (`pieces/salon/enfilade/`) et un lien vers le plan du salon à son
    adresse actuelle, `../../salon-v4.html` (passerelle ou redirection selon l'avancement de salon/amenagement).
19. Ruling : tests dans des fichiers neufs `tests/test_salon_enfilade_*.py` et une aide `tests/salon_enfilade_ancienne.py` ;
    aucun test partagé modifié. Les comparaisons avec l'ancien générateur passent par `tests.salon_anciens.ancien`
    (elles sautent quand `3d/salon/enfilade.py` disparaîtra) ; chaque test garde aussi des valeurs absolues.
20. Ruling, bascule : `git rm salon-enfilade.html` ; `3d/salon/` et les recettes `salon*` intacts. Conséquences vérifiées :
    aucun test ne lit le fichier de la racine (`tests/salon_anciens.py:122-126` et `tests/fixtures/salon/extraire.py`
    génèrent l'ancienne page en mémoire) ; `just salon` et `just salon-meubles-rendu` réécrivent encore
    `salon-enfilade.html` à la racine : la passerelle ne le copie pas (exclu comme ancienne adresse redirigée) et
    `test_documents_declares` l'accepte (ancienne adresse connue), mais `just sync` (`git add -A`) le recommiterait :
    une ligne `/salon-enfilade.html` dans `.gitignore` l'en empêche — si faux : retirer la ligne. `just
    salon-meubles-rendu` écrit ses images dans `salon-meubles-3d/`, pas dans `site/salon/enfilade/rendus/` : à reprendre
    par la tâche de suite des rendus.
21. Ruling, bascule : `site/salon-meubles-3d/enfilade-*.jpg` restent (le dossier est encore cité par
    `salon-etageres.html` ; on ne supprime qu'un dossier entier devenu orphelin) ; nettoyage commun ensuite.
22. Ruling, bascule : nouvelle recette `just salon-enfilade` (`python3 site.py salon/enfilade`), lignes à soi seulement.
    À la bascule, `python3 site.py` change dans `site/entree/` le seul lien du menu vers l'enfilade
    (`salon-enfilade.html` → `salon/enfilade/`) ; avant la bascule, il n'y change rien.

## Global Constraints

Recopiées des consignes (`REGISTRE/consignes.md`) et de la spec ; elles valent pour chaque tâche.

- **Interdits :** `git push` ; toute fusion ; écrire dans `main` ou dans le worktree d'une autre page ; modifier ou
  supprimer quoi que ce soit dans `3d/salon/` ; toucher aux recettes `salon`, `salon-rendu`, `salon-meubles-rendu`,
  `salon-figer` du `justfile` ; lancer Blender ; lire le PDF du logement ; `playwright-cli close-all` ou `kill-all` ; la
  session `prod`.
- **`site/` :** jamais modifié à la main. Ne commiter sous `site/` que `site/salon/enfilade/rendus/iso.jpg` et
  `ouverte.jpg` (tâche 4). Après chaque `python3 site.py` : `git checkout -- site && git clean -fdq site`.
- **Fichiers partagés :** `commun/`, `tests/fixtures/essai/`, `tests/navigateur/*.js` (sauf `salon-enfilade.js`),
  `pieces/salon/dessin.py`, `meubles.py`, `piece.py` : **aucun ajout prévu** par ce plan. Dans `site.py` et le
  `justfile`, seulement les lignes de l'enfilade. `python3 site.py` ne modifie aucun fichier de `site/entree/` avant la
  bascule ; à la bascule, seul le lien du menu vers l'enfilade y change.
- **Source unique :** toute cote d'un texte nouveau (alt, chiffres clés, formule, légende) est calculée depuis
  `document.py`, `volumes.py` ou `chiffrage.py`. Les textes repris de l'ancienne page gardent leurs valeurs, calculées
  par les mêmes formules (sauf les quatre corrections du ruling 13).
- **Rien ne se perd :** chaque section, tableau, dessin, image, note et lien externe de l'ancienne page a sa place
  (tableau plus bas), ou est retiré par une décision listée.
- **Textes exacts du socle :** « Sans objet », « Pas encore rendu », « Outils à réunir », « Mesuré : … cm ».
- **Style :** pas de point médian nulle part (virgule à la place), pas de police à chasse fixe (`JetBrains`,
  `monospace`), pas d'étiquettes en capitales (`text-transform:uppercase`), pas de flèche ajoutée aux liens, pas de mode
  sombre (`prefers-color-scheme`), pas de motif décoratif. Couleurs et polices du socle (`commun/site.css`).
- **Jamais :** cases à cocher, « Copier la liste », « À venir », « Lecture du plan », « Lecture de la coupe », texte de
  description d'un dessin ou d'un rendu à l'écran (texte alternatif seulement), sommaire propre à la page, bouton de
  version figée.
- **Vues de construction**, dans cet ordre : Plans (`elevation` par défaut, `iso`, `ouverte`, `profil`, `dessus`,
  `eclate`), Découpe, Montage, Achats, Explication. Une seule variante : ni « Comparer » ni choix de variante.
- **Journal :** sept changements de l'enfilade avant et après (V1.0 à V1.6).
- **Tests :** `uv run -q --no-project --with pytest pytest -q tests` (395 passés à la base `965af34`) ; tous verts à la
  fin de chaque tâche.
- **Navigateur :** ports 8850 à 8859, sessions `refonte-salon-enfilade-<n>` :
  `PORT=8851 SESSION=refonte-salon-enfilade-1 tests/navigateur/lancer.sh tests/navigateur/salon-enfilade.js`.
- **Git :** commits petits, en français, sur `refonte-salon-enfilade`, terminés par la ligne
  `Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>`.

## Review Focus

Les cas que la spec implique et qu'un lecteur rencontrera, du plus probable au moins probable ; chacun a son test.

1. **Mesurer sur un dessin à l'échelle** (élévation à 3,4 unités par cm) : la distance affichée est en cm ; mesurer la
   cote de 240 affiche « Mesuré : 240 cm ». Tests : tâche 2 (`test_en_cm`), tâche 5 (script).
2. **Un élément de dessin sans règle CSS** (canapé `.sofa`, texte hors de `.scene` dans Découpe et Explication) : rien
   n'est noir par défaut, aucune cote en chasse fixe. Tests : tâche 2 (`test_classes_ont_une_regle`), tâche 5.
3. **Une ancienne adresse avec une ancre inconnue, sans ancre, ou `#changements`** : vue par défaut (Plans), ou
   l'historique. Tests : tâche 6 (`test_redirection`), tâche 5.
4. **Un texte sous un dessin resté à l'écran, ou perdu** : il est l'`aria-label` (ou l'`alt`), et nulle part ailleurs.
   Tests : tâche 3 (`test_alts_*`, `test_aucune_description_visible`), tâche 4.
5. **Page à 390 px** : les tableaux larges (débit, compositions, METOD) défilent dans leur boîte, les dessins tiennent
   dans la largeur, la page ne défile pas en largeur. Test : tâche 5.

## Fichiers

| Fichier | Rôle | Tâche |
|---|---|---|
| `pieces/salon/enfilade/chiffrage.py` | calculs de la page : pièces repérées, débit, calepinage, chiffrage des six compositions, poids, volume, dégagements, `prix`, `lettre` | 1 |
| `pieces/salon/enfilade/dessins.py` | les 18 dessins (6 de Plans, 10 panneaux, 2 comparaisons), `en_cm`, `CSS` | 2 |
| `pieces/salon/enfilade/vues.py` | `vues(variante)` : Plans, Découpe, Montage, Achats ; textes alternatifs des dessins de Plans | 3 |
| `pieces/salon/enfilade/explication.py` | `vue_explication(...)` | 4 |
| `site/salon/enfilade/rendus/iso.jpg`, `ouverte.jpg` | copies de `salon-meubles-3d/enfilade-iso.jpg`, `enfilade-ouverte.jpg` | 4 |
| `tests/salon_enfilade_ancienne.py` | aide de test : l'ancienne page en mémoire, ses sections, ses textes | 3 |
| `tests/test_salon_enfilade_chiffrage.py`, `_dessins.py`, `_vues.py`, `_explication.py`, `_document.py` | tests | 1 à 6 |
| `tests/navigateur/salon-enfilade.js` | script navigateur, `@site reel` | 5 |
| `pieces/salon/enfilade/document.py` | ajout de `DOCUMENT` (à la fin) | 6 |
| `site.py`, `justfile`, `.gitignore`, `salon-enfilade.html` (supprimé) | bascule | 6 |

## Section de l'ancienne page → vue qui la reprend

Relu sur `salon-enfilade.html` (V1.6) et `3d/salon/enfilade.py`. Colonne « Ancre » : identifiant du `h2` et ce qu'en fait
la redirection (tâche 6).

| Section de l'ancienne page | Ancre | Devient | Retiré, et décision qui le retire |
|---|---|---|---|
| Barre : « ← Plans » | | Menu de gauche, icône maison sur mobile | La barre propre à la page : « une navigation identique sur toutes les pages » |
| Barre : « Salon », « Étagères », « Enfilade » | | Barre du haut : pièce › document (liste des documents du salon) ; menu de gauche | id. |
| Sommaire repliable | | Onglets des vues | Le sommaire (consignes, « Retirés par décision ») |
| Surtitre « Salon · Enfilade · V1.6 », titre « Enfilade du mur ouest » | | Barre du haut : pièce, document, pastille V1.6 ; le titre devient celui de la fiche de Plans (ruling 14) | Le double titre (spec, objectif 1) |
| Chapô | | Explication : chapô, rendu `iso` à côté | |
| (chiffres clés, absents de l'ancienne page) | | Explication : huit chiffres calculés (ruling 12) | |
| Vue iso : enfilade fermée, et son texte | `iso` → `plans?k=iso` | Plans, `k=iso` ; texte en `aria-label` | Le texte à l'écran : « pas de descriptions d'images à l'écran » |
| Vue iso : enfilade ouverte, et son texte | | Plans, `k=ouverte` ; texte en `aria-label` | id. |
| Le meuble : paragraphe | `meuble` → `plans?k=elevation` | Explication, « Le meuble » | |
| Le meuble : élévation de face cotée, et son texte | | Plans, `k=elevation` (par défaut) ; texte en `aria-label` (« Quatre portes », ruling 13) ; formule de la fiche : la cote « 240 = 3 × 80, centré sur le mur (8,8 libres de chaque côté) » | Le texte à l'écran (id.) |
| Le meuble : coupes de profil, et leur texte | | Plans, `k=profil` ; texte en `aria-label` | id. |
| Le meuble : vue de dessus, et son texte (dégagements, volume) | | Plans, `k=dessus` ; texte en `aria-label` ; dégagements et volume en chiffres clés | id. |
| Le meuble : vue éclatée, et son texte | | Plans, `k=eclate` ; texte en `aria-label` | id. |
| Rendus 3D : deux images et leurs légendes | `rendus` → `explication` | Explication, « Rendus 3D » (`rendus/iso.jpg`, `rendus/ouverte.jpg`) ; légendes en `alt` | La `figcaption` à l'écran (id.) |
| Construction : 9 sous-titres et paragraphes | `construction` → `explication` | Explication, « Construction » (corrections 3,8 et 18,3) | |
| Matériaux : paragraphe, tableau des six compositions, note, cinq pistes | `materiaux` → `explication` | Explication, « Matériaux » (ruling 10) | La pastille en capitales et chasse fixe (style) ; le mot « retenu » reste |
| Comparaison avec IKEA STOCKHOLM : paragraphe, dessin et son texte, tableau, note, trois pistes | `comparaison` → `explication` | Explication, même titre ; dessin en figure, texte en `aria-label` | Le texte sous le dessin à l'écran |
| Comparaison avec trois METOD 80 : paragraphe, dessin et son texte, cinq tableaux, deux notes, six pistes | `metod` → `explication` | Explication, même titre, tout compris | id. |
| Débit et découpe : paragraphe et tableau de débit | `debit` → `decoupe` | Découpe : `tableau_debit` (rulings 7) | Les lignes de groupe, remplacées par la légende des lettres de repère |
| Débit et découpe : plan de découpe (paragraphe et légende, format, dix panneaux et leurs titres), paragraphe des fibres dures | | Découpe : « Plan de découpe », calepinage, paragraphe final (rulings 8, 9) | |
| Achats et prix : introduction, tableau par magasin, total, outillage, note Weldom | `achats` → `achats` | Achats : chapô, bloc `achats` (ruling 5), paragraphe du total, outillage, remarque | |
| Outils et montage : outils, onze étapes, note | `montage` → `montage` | Montage : « Outils à réunir », étapes, remarque (poids corrigé, ruling 13) | |
| Points à valider : douze points | `valider` → `explication` | Explication, « Points à valider », liste sans cases | |
| Note finale : fichiers source, recette, lien vers le salon | | Explication, remarque finale (ruling 18) | Les chemins de l'ancien générateur (`3d/salon/enfilade.py`, `just salon`), même cas que l'entrée |
| Changements (sept versions) | `changements` → `salon/enfilade/historique.html` | Historique du document et `journal.html` | Le tableau dans une vue (consignes) |

Une ancre absente de ce tableau, ou pas d'ancre, ouvre la vue par défaut (Plans).

---

### Task 1 : Calculs de la page (`chiffrage.py`)

**Files:**
- Create: `pieces/salon/enfilade/chiffrage.py`
- Test: `tests/test_salon_enfilade_chiffrage.py`

**Interfaces:**
- Consumes : `pieces.salon.enfilade.document` (`L, NORD, P, Z1, ZP, EP, N, FAC, DOS, PC, TRAV, TRAIT, COULISSE, EP_COUL,
  H_BOITE, PROF_ETAGERE, PIEDS_X, FORMATS, MELAMINE, QUINC, VARIANTES, CHANT, RETENUE, PREFIXE, ORDRE_MAG, quantite`),
  `pieces.salon.enfilade.volumes` (`G`, `geometrie`, `bas`), `pieces.salon.meubles.cote`,
  `pieces.salon.amenagement.document.CANAPE`.
- Produces (utilisés par les tâches 2 à 4) :
  - `prix(v: float) -> str` : l'ancien `euros` (`enf:L65`), « 1 027,95 € », « 109,00 € » ;
  - `lettre(n: int) -> str` : `enf:L807` ;
  - `pieces(v: dict = RETENUE) -> list[dict]`, `debit(ps: list[dict]) -> list[dict]`, `format_de(p: dict, v: dict) -> str`,
    `calepiner(lst: list[tuple], F: dict) -> list[dict]`, `comptes(ps: list[dict], g: dict, v: dict) -> dict` : copies
    de `enf:L311-422` ;
  - `chiffrage(v: dict = RETENUE) -> dict` : `enf:L425-456`, mêmes clés (`v, ps, g, lignes, cal, total, releve, estime,
    c`), la quantité d'un poste de quincaillerie par `quantite(qd["q"], c)` au lieu de `qd["q"](c)` ;
  - `chiffrages() -> list[dict]` : `chiffrage(v)` pour chaque `VARIANTES`, dans l'ordre ; `retenu(chs: list[dict]) -> dict`
    : celui dont `ch["v"] is RETENUE` ;
  - `volume_utile(g: dict = G) -> float` : litres, `sum((w - 2 * EP) * PC * (g["zi1"] - g["zi0"]) for w in g["W"]) / 1000`
    (`enf:L756`) ;
  - `degagements(g: dict = G) -> tuple[float, float]` : (devant la porte la plus large de M1, devant un tiroir sorti),
    `CANAPE["x0"] - P - l1` et `CANAPE["x0"] - P - COULISSE - FAC` arrondis à 0,1 (`enf:L764`) ;
  - `poids_caisson(g: dict = G) -> int` : kg, corrigé (ruling 13), voir l'étape 3.

- [ ] **Step 1 : écrire les tests**

```python
# tests/test_salon_enfilade_chiffrage.py
from pieces.salon.enfilade import chiffrage as C
from pieces.salon.enfilade import document as D
from tests.salon_anciens import ancien

TOTAUX = {"A": 901.36, "B": 723.95, "C": 1027.95, "D": 1274.36, "E": 595.45, "F": 1221.86}

def test_comme_l_ancien_generateur():
    EN = ancien("enfilade")
    for nouveau, vieux in zip(D.VARIANTES, EN.VARIANTES):
        assert C.pieces(nouveau) == EN.pieces(vieux)
        a, b = C.chiffrage(nouveau), EN.chiffrage(vieux)
        for cle in ("lignes", "cal", "total", "releve", "estime", "c"):
            assert a[cle] == b[cle], (nouveau["cle"], cle)
        assert C.debit(a["ps"]) == EN.debit(b["ps"])

def test_totaux_des_six_compositions():
    assert {ch["v"]["cle"]: ch["total"] for ch in C.chiffrages()} == TOTAUX
    ch = C.retenu(C.chiffrages())
    assert ch["v"]["cle"] == "C" and (ch["releve"], ch["estime"]) == (775.35, 252.6)
    assert len(ch["ps"]) == 46 and len(C.debit(ch["ps"])) == 13
    assert {k: len(v) for k, v in ch["cal"].items()} == {"C18": 10}
    assert ch["c"]["portes"] == 4 and ch["c"]["pieds"] == 8

def test_prix_et_lettre():
    assert C.prix(1027.95) == "1 027,95 €" and C.prix(109) == "109,00 €"
    assert [C.lettre(n) for n in (2, 4, 10)] == ["deux", "quatre", "10"]

def test_volume_et_degagements():
    assert round(C.volume_utile()) == 788
    assert C.degagements() == (20.3, 8.2)

def test_poids_d_un_caisson_corrige():
    assert C.poids_caisson() == 17          # l'ancienne page affichait 1361 (largeur comptée deux fois)
```

- [ ] **Step 2 : lancer, constater l'échec**

Run : `uv run -q --no-project --with pytest pytest -q tests/test_salon_enfilade_chiffrage.py`
Expected : FAIL, `ModuleNotFoundError: No module named 'pieces.salon.enfilade.chiffrage'`.

- [ ] **Step 3 : écrire `pieces/salon/enfilade/chiffrage.py`**

Copier les fonctions de `enf` citées plus haut, avec les noms du nouveau paquet (`virg` à un argument → `cote`). En
tête, un commentaire d'une ligne par fonction n'est pas demandé ; un commentaire de module dit d'où elles viennent.
Poids corrigé : côtés, fond et deux traverses d'un caisson de largeur `w = g["W"][0]`, chêne à 0,7 :

```python
def poids_caisson(g=G):
    w, li = g["W"][0], g["W"][0] - 2 * EP
    return round((2 * g["HC"] * PC + li * PC + 2 * li * TRAV) * EP * 0.7 / 1000)
```

- [ ] **Step 4 : lancer, constater le succès**

Run : `uv run -q --no-project --with pytest pytest -q tests/test_salon_enfilade_chiffrage.py`
Expected : 5 passed. Puis la suite entière : `uv run -q --no-project --with pytest pytest -q tests` → tout passe.

- [ ] **Step 5 : commit**

```bash
git add pieces/salon/enfilade/chiffrage.py tests/test_salon_enfilade_chiffrage.py
git commit -m "Enfilade : calculs de la page (débit, calepinage, chiffrage des compositions, poids corrigé)

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
```

### Task 2 : Dessins et leur CSS (`dessins.py`)

**Files:**
- Create: `pieces/salon/enfilade/dessins.py`
- Test: `tests/test_salon_enfilade_dessins.py`

**Interfaces:**
- Consumes : tâche 1 (`chiffrage`, `retenu`, `chiffrages`) ; `pieces.salon.dessin` (`iso_svg`, `rect`, `text`, `cote_h`,
  `cote_v`, `f`) ; `pieces.salon.enfilade.volumes` (`G`, `pieces_3d`) ; `pieces.salon.amenagement.document.CANAPE`.
- Produces :
  - `CSS: str` (règles plus bas) ; `ECHELLES = {"elevation": 3.4, "profil": 5, "dessus": 3, "eclate": 2.6}` ;
  - `svg(vb: str, corps: str, label: str) -> str` : `enf:L490` (label échappé, `quote=True`) ;
  - `en_cm(dessin: str, k: float) -> str` : viewBox du `<svg>` de tête divisé par `k` (chaque nombre
    `f"{round(v / k, 3):g}"`), son contenu enveloppé dans `<g transform="scale(<1/k au format :.6g>)">…</g>` ; tout le
    reste de la balise `<svg …>` inchangé ;
  - `face_svg(g=G, label="Élévation de face cotée de l'enfilade") -> str`, `profil_svg(g=G, label="Coupes de profil de
    l'enfilade")`, `dessus_svg(g=G, label="Vue de dessus de l'enfilade avec les ouvertures")`, `eclate_svg(g=G,
    label="Vue éclatée de l'enfilade")` : copies de `enf:L499-716` ; seul écart, les trois étiquettes de module de
    l'élévation `f"M{k_ + 1}, {contenu}"` (virgule, `enf:L527`) ;
  - `iso(ouvert: bool, label: str) -> str` : `iso_svg(pieces_3d(ouvert=ouvert), escape(label, quote=True))` (`iso_svg`
    n'échappe pas son titre) ;
  - `decoupe_svg(cle: str, pa: dict, n: int) -> tuple[str, str]` : (titre, svg) ; `enf:L719-739` sans la `figure` ni la
    `figcaption`, titre `f'{F["court"]} n° {n}, {cote(F["L"], 0)} × {cote(F["l"], 0)}, chute {…} %'`, aria-label = titre ;
  - `comparaison_svg(g=G, autres=None, titre="Comparaison des dimensions avec le buffet IKEA STOCKHOLM 2025") -> str` :
    `enf:L851-874` (`STOCKHOLM` de `document.py`).

- [ ] **Step 1 : écrire les tests**

Fichiers de référence : `tests/fixtures/salon/`, rangs 0 à 17 de `index.json` pour `salon-enfilade.html`. Les nouveaux
dessins s'y comparent sans leur `aria-label` (il devient le texte sous le dessin, tâche 3) et avec la virgule à la place
du point médian.

```python
# tests/test_salon_enfilade_dessins.py
import re
import pytest
from commun.css_dessins import css_dessins
from pieces.salon.enfilade import chiffrage, dessins
from pieces.salon.enfilade.document import METOD_CAISSON, METOD_MIXTE, NORD
from tests.outils import RACINE

FIX = RACINE / "tests/fixtures/salon"
def _sans_aria(s): return re.sub(r' aria-label="[^"]*"', "", s)
def _ref(nom): return _sans_aria((FIX / nom).read_text(encoding="utf-8")).replace(" · ", ", ")
def _metod(): return dessins.comparaison_svg(autres=[(METOD_MIXTE["nom"], METOD_MIXTE["l"], METOD_MIXTE["p"],
    METOD_MIXTE["h"], METOD_CAISSON["pieds"], True, [NORD + 80, NORD + 160])],
    titre="Comparaison des dimensions avec trois caissons METOD 80, composition mixte")

DESSINS = {
    "enfilade-enfilade-fermee-vue-iso.svg": lambda: dessins.iso(False, "x"),
    "enfilade-enfilade-ouverte-vue-iso.svg": lambda: dessins.iso(True, "x"),
    "enfilade-elevation-de-face-cotee-de-l-enfilade.svg": dessins.face_svg,
    "enfilade-coupes-de-profil-de-l-enfilade.svg": dessins.profil_svg,
    "enfilade-vue-de-dessus-de-l-enfilade-avec-les-ouvertures.svg": dessins.dessus_svg,
    "enfilade-vue-eclatee-de-l-enfilade.svg": dessins.eclate_svg,
    "enfilade-comparaison-des-dimensions-avec-le-buffet-ikea-stockholm-2025.svg": dessins.comparaison_svg,
    "enfilade-comparaison-des-dimensions-avec-trois-caissons-metod-80-composition-mixte.svg": _metod,
}

@pytest.mark.parametrize("nom", DESSINS)
def test_dessins_comme_la_reference(nom):
    s = DESSINS[nom]()
    assert _sans_aria(s) == _ref(nom) and "·" not in s

def _panneaux():
    ch = chiffrage.retenu(chiffrage.chiffrages())
    return [dessins.decoupe_svg("C18", pa, n + 1) for n, pa in enumerate(ch["cal"]["C18"])]

def test_panneaux_comme_la_reference():
    noms = sorted((p for p in FIX.glob("enfilade-chene-18-n-*.svg")), key=lambda p: int(p.name.split("-")[4]))
    assert len(noms) == 10
    for (titre, s), p in zip(_panneaux(), noms):
        assert _sans_aria(s) == _ref(p.name)
        assert f'aria-label="{titre}"' in s and "·" not in titre
    assert _panneaux()[0][0] == "chêne 18 n° 1, 200 × 60, chute 20 %"

def test_label_echappe():
    for s in (dessins.face_svg(label='a "b" & c'), dessins.iso(False, 'a "b" & c')):
        assert 'aria-label="a &quot;b&quot; &amp; c"' in s

def test_en_cm():
    brut = dessins.face_svg()
    s = dessins.en_cm(brut, 3.4)
    vb = [float(x) for x in re.search(r'viewBox="([^"]*)"', brut).group(1).split()]
    assert re.search(r'viewBox="([^"]*)"', s).group(1) == " ".join(f"{round(v / 3.4, 3):g}" for v in vb)
    assert '<g transform="scale(0.294118)">' in s and s.endswith("</g></svg>")
    assert re.sub(r'viewBox="[^"]*"|<g transform="[^"]*">|</g></svg>$', "", s) == \
        re.sub(r'viewBox="[^"]*"|</svg>$', "", brut)

def _tous():
    return [f() for f in DESSINS.values()] + [s for _, s in _panneaux()]

def _a_une_regle(classe, css):
    return re.search(rf"\.{re.escape(classe)}(?![\w-])", css) is not None

def test_classes_ont_une_regle():
    """Chaque classe d'un élément d'un dessin (scène, Découpe, Explication) a une règle : rien n'est noir par défaut."""
    tous = _tous() + ['<span class="lg chene"></span><span class="lg chute"></span><figure class="schema"></figure>']
    css = css_dessins(dessins.CSS, tous, ".d-salon")
    site = (RACINE / "commun/site.css").read_text(encoding="utf-8")
    classes = {c for s in tous for m in re.findall(r'class="([^"]+)"', s) for c in m.split()}
    assert {"enf", "dim", "dimt", "sofa", "chute", "lg", "schema"} <= classes
    assert sorted(c for c in classes if not _a_une_regle(c, css) and not _a_une_regle(c, site)) == []
    assert ".d-salon svg.enf text{" in css

def test_css_sans_chasse_fixe_ni_capitales():
    for interdit in ("JetBrains", "monospace", "uppercase", "prefers-color-scheme", "--sofa"):
        assert interdit not in dessins.CSS
```

- [ ] **Step 2 : lancer, constater l'échec**

Run : `uv run -q --no-project --with pytest pytest -q tests/test_salon_enfilade_dessins.py`
Expected : FAIL, `ImportError` sur `dessins`.

- [ ] **Step 3 : écrire `pieces/salon/enfilade/dessins.py`**

Fonctions de `enf` recopiées (avec `FLECHE`, `enf:L486`, et `cl_caisson`, `enf:L494`), noms du nouveau paquet. `CSS`
exactement (valeurs de `plan.py:L376-470` et du `STYLE` de `enf:L460-484`, sans chasse fixe, `--sofa` remplacé) :

```css
svg.enf text{font-family:var(--texte);fill:var(--ink)}
svg.enf .dim{stroke:var(--muted);stroke-width:.6;fill:none}
svg.enf .dimt{fill:var(--muted);font-family:var(--ui);font-weight:600;font-variant-numeric:tabular-nums;font-size:10px}
svg.enf .t{font-size:11.5px}svg.enf .ts{font-size:10px}svg.enf .tx{font-size:8.5px}svg.enf .tb{font-size:12px;font-weight:700}
svg.enf .inv{fill:#F7F8F6}
svg.enf .muted{fill:var(--muted)}
svg.enf .floorl{stroke:var(--ink);stroke-width:2}
svg.enf .mur-h{fill:var(--line);fill-opacity:.6;stroke:var(--muted);stroke-width:.5}
svg.enf .mont{fill:#26262A;stroke:var(--ink);stroke-width:.4}
svg.enf .shelfc{fill:var(--wood);stroke:var(--ink);stroke-width:.6}
svg.enf .cab{fill:var(--cab);stroke:var(--ink);stroke-width:.7}
svg.enf .dark{fill:var(--ink)}
svg.enf .acier{fill:#8E9399;stroke:var(--ink);stroke-width:.4}
svg.enf .acierh{fill:none;stroke:#5E6369;stroke-width:.8;stroke-dasharray:2 1.5}
svg.enf .upper{fill:none;stroke:var(--ink);stroke-width:.8;stroke-dasharray:3 2}
svg.enf .sofa{fill:#C9BFAE;stroke:var(--ink);stroke-width:.8}
svg.enf .vinyl{fill:#2B2B2E;fill-opacity:.75;stroke:var(--ink);stroke-width:.4}
svg.enf .mel{fill:var(--panel);stroke:var(--ink);stroke-width:.7}
svg.enf .hdf{fill:#8A6E52;stroke:var(--ink);stroke-width:.3}
svg.enf .hdfl{fill:#8A6E52;fill-opacity:.18;stroke:none}
svg.enf .chute{fill:var(--line);fill-opacity:.3;stroke:var(--muted);stroke-width:.6}
svg.enf .ouv{fill:none;stroke:var(--muted);stroke-width:.7;stroke-dasharray:4 3}
svg.enf .arc{fill:none;stroke:var(--tri);stroke-width:.9;stroke-dasharray:4 2}
svg.enf .porteo{fill:var(--wood);fill-opacity:.25;stroke:var(--tri);stroke-width:.7;stroke-dasharray:3 2}
svg.enf .fl{stroke:var(--muted);stroke-width:.6}
svg.enf .fl2{stroke:var(--tri);stroke-width:.9;fill:none;marker-end:url(#fleche)}
svg.enf .flm{fill:var(--tri)}
.lg{display:inline-block;width:14px;height:10px;border:1px solid var(--ink);vertical-align:-1px;margin:0 4px 0 10px}
.lg.chene{background:var(--wood)}.lg.chute{background:var(--line)}
.schema{margin:14px 0;max-width:1120px}.schema svg{display:block;width:100%;height:auto}
```

- [ ] **Step 4 : lancer, constater le succès**

Run : `uv run -q --no-project --with pytest pytest -q tests/test_salon_enfilade_dessins.py`
Expected : 13 passed (8 dessins paramétrés et 5 tests). Puis la suite entière : tout passe.

- [ ] **Step 5 : commit**

```bash
git add pieces/salon/enfilade/dessins.py tests/test_salon_enfilade_dessins.py
git commit -m "Enfilade : dessins repris de l'ancienne page, Mesurer en cm, CSS sans chasse fixe

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
```

### Task 3 : Vues Plans, Découpe, Montage, Achats (`vues.py`)

**Files:**
- Create: `pieces/salon/enfilade/vues.py`
- Create: `tests/salon_enfilade_ancienne.py`
- Test: `tests/test_salon_enfilade_vues.py`

**Interfaces:**
- Consumes : tâches 1 et 2 ; `commun.blocs` (`Achat`, `SectionAchats`, `achats`, `note_source`, `vue_lecture`, `euros`) ;
  `commun.blocs_construction` (`DessinMeuble`, `vue_plans`, `Colonne`, `tableau_debit`, `Calepin`, `calepinage`,
  `Etape`, `etapes`) ; `document` (`MAGASINS`, `ORDRE_MAG`, `FORMATS`, `GROUPES`, `PREFIXE`, `RELEVE`, `OUTILLAGE`,
  `HUILE`, `VARIANTES`, `RETENUE`, `TRAIT`).
- Produces :
  - `RENDUS_SITE = Path(__file__).resolve().parents[3] / "site" / "salon" / "enfilade" / "rendus"` (tâche 4) ;
  - `alts(ch: dict) -> dict[str, str]` : clés `elevation, iso, ouverte, profil, dessus, eclate`, les textes sous les
    dessins (`enf:L760, 762, 764, 766, 774, 776`), mêmes valeurs ; pour `elevation`, `f"{lettre(len(portes)).capitalize()}
    portes de …"` au lieu de « Six portes de … » (ruling 13) ;
  - `etapes_montage(g: dict) -> list[str]` (`enf:L1134-1146`, onze textes) et `OUTILS: list[str]` (`enf:L1147-1148`) ;
  - `vues(variante: str) -> dict[str, Vue]` : `variante` doit être `""` (sinon `ValueError`) ; clés `plans, decoupe,
    montage, achats, explication` ; à cette tâche `"explication": vue_lecture("explication", "")` (la tâche 4 la remplit).
  - Aide de test `tests/salon_enfilade_ancienne.py` : `page() -> str` (`ancien("enfilade").page()[0]`, gardée en
    mémoire), `section(html: str, ancre: str) -> str` (du `<h2 id="<ancre>"` au `<h2` suivant), `texte(html: str) -> str`
    (balises retirées, entités décodées, blancs réunis, `" · "` → `", "`), `morceaux(html: str) -> list[str]` (`texte` de
    chaque `<p>` sans `class="cap"`, `<li>`, `<h3>`), `CORRECTIONS = {"Six portes": "Quatre portes", "3.8": "3,8",
    "18.3": "18,3", "1361 kg": "17 kg"}` et `corrige(t: str) -> str`.

Contenu des vues :
- **Plans** : `vue_plans([DessinMeuble("elevation", "Élévation", en_cm(face_svg(g, a["elevation"]), 3.4)),
  DessinMeuble("iso", "Vue iso", iso(False, a["iso"]), mesure=False), DessinMeuble("ouverte", "Iso ouverte", iso(True,
  a["ouverte"]), mesure=False), DessinMeuble("profil", "Profils", en_cm(profil_svg(g, a["profil"]), 5)),
  DessinMeuble("dessus", "Dessus", en_cm(dessus_svg(g, …), 3)), DessinMeuble("eclate", "Éclatée", en_cm(eclate_svg(g,
  …), 2.6))], titre="Enfilade du mur ouest", formule=f"{cote(L)} = {N} × {cote(g['W'][0])}, centré sur le mur
  ({cote(NORD)} libres de chaque côté)")` (échelles : `dessins.ECHELLES`).
- **Découpe** : `tableau_debit` avec les colonnes `Colonne("Rep.", "repere")`, `Colonne("Pièce")`, `Colonne("L × l",
  "cote")`, `Colonne("Ép.", "cote")`, `Colonne("Qté", "nombre")`, `Colonne("Matière", "detail")`, `Colonne("Où",
  "detail")`, `Colonne("Note", "note")` ; cellules `f"{cote(d['L'])} × {cote(d['l'])}"`, `cote(d["ep"])`, `d["n"]`,
  `FORMATS[format_de(d, v)]["court"]`, `", ".join(d["ous"])`, `d["note"]` ; `titre="Débit et découpe"`, `sous_titre` = la
  phrase de `enf:L1096` puis la légende `" ".join(f"{PREFIXE[k]} : {GROUPES[k][0].lower() + GROUPES[k][1:]}." …)`. Puis
  `<h2>Plan de découpe</h2>` et le paragraphe de `enf:L1100` (légende `<span class="lg chene"></span>chêne <span class="lg
  chute"></span>chute`), puis pour chaque format `calepinage([Calepin(t, s) for t, s in panneaux], titre=f"{FORMATS[cle]
  ['nom']} × {len(pans)}")`, puis le paragraphe de `enf:L1102`.
- **Montage** : `etapes([Etape("", f"<p>{escape(e)}</p>") for e in etapes_montage(g)], titre="Outils et montage",
  outils="<ul>" + <un <li> échappé par outil> + "</ul>")` puis `note_source(<enf:L1152, poids par poids_caisson(g)>)`.
- **Achats** : chapô `<p class="chapo">` = `enf:L1124`, les noms des magasins en liens (`MAGASINS[m]["url"]`), « relevé »
  et « estimé » en clair ; `achats([SectionAchats(MAGASINS[m]["nom"], …) for m in ORDRE_MAG if lignes], titre="Achats et
  prix", arrondi=False)` ; lignes triées comme `enf:L1109` ; `Achat(li["poste"], li["ref"], li["q"], li["pu"],
  note=…)`. La note, en HTML : la note du poste échappée, `<br>`, le statut (« relevé » ou « estimé »), puis
  `", 2,7 m² × 12,90 € le m²"` pour une ligne au m² (`li["unite"] == "m²"`) ou `", 8 × 5,35 €"` sinon (quantité, puis
  `euros(li["pu"])`), puis, si `li["url"]`, `', <a href="<url échappée>">fiche</a>'` (relevé) ou `'… repère</a>'`
  (estimé) : le contenu des colonnes Prix unit., Prix et Source de `enf:L1115-1120`. Puis le paragraphe du
  total (`enf:L1127`, montants par `prix`, « (composition C) » après « Total »), « Outillage, seulement si l'atelier ne
  l'a pas (hors total) : » et sa liste (`enf:L1122`), puis `note_source(<enf:L1129>)`.

- [ ] **Step 1 : écrire l'aide et les tests**

```python
# tests/test_salon_enfilade_vues.py
import re
from html import escape
import pytest
from commun.modele import Document, Variante, verifier
from pieces.salon.enfilade import chiffrage, vues
from tests.salon_enfilade_ancienne import corrige, morceaux, page, section, texte

V = vues.vues("")
def _scene(cle): return V[cle].elements[0].scene

def test_cinq_vues_et_verifier():
    doc = Document("salon", "enfilade", "Enfilade", "construction", (Variante("", "Enfilade", "V1.6", ()),), vues.vues)
    verifier(doc, V)
    assert list(V) == ["plans", "decoupe", "montage", "achats", "explication"]
    with pytest.raises(ValueError):
        vues.vues("autre")

def test_plans():
    p = V["plans"]
    assert [e.k for e in p.elements] == ["elevation", "iso", "ouverte", "profil", "dessus", "eclate"]
    assert {e.titre for e in p.elements} == {"Enfilade du mur ouest"}
    for e in p.elements:
        assert e.scene.startswith('<svg data-mesure="non"') == (e.k in ("iso", "ouverte"))
    assert p.outils == ("zoom", "mesure")
    assert "240 = 3 × 80, centré sur le mur (8,8 libres de chaque côté)" in p.fiche
    assert 'href="#decoupe"' in p.fiche and 'href="#montage"' in p.fiche

def _caps():
    return [corrige(texte(c)) for c in re.findall(r'<p class="cap">(.*?)</p>', page(), re.S)][:6]

def test_alts_sont_les_textes_sous_les_dessins():
    a = vues.alts(chiffrage.retenu(chiffrage.chiffrages()))
    ordre = ["iso", "ouverte", "elevation", "profil", "dessus", "eclate"]   # ordre de l'ancienne page
    assert [a[k] for k in ordre] == _caps()
    assert "Quatre portes de 39,7" in a["elevation"]
    for e in V["plans"].elements:
        assert f'aria-label="{escape(a[e.k], quote=True)}"' in e.scene

def test_aucune_description_visible():
    a = vues.alts(chiffrage.retenu(chiffrage.chiffrages()))
    for cle, v in V.items():
        for e in v.elements:
            visible = re.sub(r'aria-label="[^"]*"', "", e.scene + v.fiche)
            assert not any(escape(t, quote=True) in visible or t in visible for t in a.values()), cle

def test_decoupe():
    s = _scene("decoupe")
    assert s.count("<tbody>") == 1 and s.split("<tbody>")[1].count("<tr>") == 13
    assert "46 pièces, 13 repères." in s and "A : caissons." in s
    assert s.count('<figure class="calepin">') == 10 and "<h2>Plan de découpe</h2>" in s
    assert "Tablette chêne lamellé-collé 200 × 60 × 1,8 × 10" in s and "2,61 m²" in s
    for m in morceaux(section(page(), "debit")):
        assert corrige(m) in texte(s), m

def test_montage():
    s = _scene("montage")
    assert s.count("<li>") == 11 + 5 and "Outils à réunir" in s
    assert "17 kg environ" in s and "1361" not in s
    for m in morceaux(section(page(), "montage")):
        if m not in ("Outils", "Étapes"):
            assert corrige(m) in texte(s), m

def test_achats():
    s = _scene("achats")
    assert "<h3>Weldom Marseille Saint-Barnabé</h3>" in s and "<h3>Leroy Merlin</h3>" in s
    assert "904,70 €" in s and "123,25 €" in s and "1027,95 €" in s
    assert "29/10/2026" in s and "relevé" in s and "estimé" in s
    assert s.count("<tr>") == 15 + 3 + 2      # lignes, plus les deux en-têtes ; « Sous-total » est un <tr class="total">
    for m in morceaux(section(page(), "achats")):
        assert corrige(m).replace("Total : ", "Total (composition C) : ") in texte(s), m

def test_liens_externes_gardes():
    vieux = set(re.findall(r'href="(https?://[^"]+)"', section(page(), "debit") + section(page(), "achats")))
    neufs = set(re.findall(r'href="(https?://[^"]+)"', _scene("decoupe") + _scene("achats")))
    assert vieux <= neufs

def test_sans_point_median_ni_chasse_fixe():
    for cle, v in V.items():
        for e in v.elements:
            assert "·" not in e.scene + v.fiche and "mono" not in e.scene, cle
```

`texte()` réunit les blancs : les tests comparent donc des phrases entières. `morceaux` d'une section ne prend que les
paragraphes, les points de liste et les sous-titres : les tableaux sont vérifiés par leurs comptes.

- [ ] **Step 2 : lancer, constater l'échec**

Run : `uv run -q --no-project --with pytest pytest -q tests/test_salon_enfilade_vues.py`
Expected : FAIL, `ImportError` sur `vues` (ou sur `tests.salon_enfilade_ancienne` si l'aide n'est pas encore écrite).

- [ ] **Step 3 : écrire `tests/salon_enfilade_ancienne.py`, puis `pieces/salon/enfilade/vues.py`**

`vues.vues` calcule une fois `chs = chiffrage.chiffrages()` et `ch = chiffrage.retenu(chs)` (la tâche 4 passe `chs` à
l'Explication). Rien d'autre à décider que ce qui est dit plus haut.

- [ ] **Step 4 : lancer, constater le succès**

Run : `uv run -q --no-project --with pytest pytest -q tests/test_salon_enfilade_vues.py`
Expected : 9 passed. Puis la suite entière : tout passe. Et `python3 site.py && git status --short site/entree` : vide ;
puis `git checkout -- site && git clean -fdq site`.

- [ ] **Step 5 : commit**

```bash
git add pieces/salon/enfilade/vues.py tests/salon_enfilade_ancienne.py tests/test_salon_enfilade_vues.py
git commit -m "Enfilade : vues Plans, Découpe, Montage et Achats

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
```

### Task 4 : Explication et rendus (`explication.py`)

**Files:**
- Create: `pieces/salon/enfilade/explication.py`
- Create: `site/salon/enfilade/rendus/iso.jpg`, `site/salon/enfilade/rendus/ouverte.jpg`
- Modify: `pieces/salon/enfilade/vues.py` (la ligne `"explication": …` de `vues`)
- Test: `tests/test_salon_enfilade_explication.py`

**Interfaces:**
- Consumes : tâches 1 à 3 (`vues.RENDUS_SITE`, `vues.etapes_montage`) ; `commun.blocs` (`tete`, `chiffres`, `rendu`,
  `figure_rendu`, `a_verifier`, `note_source`, `vue_lecture`, `total_achats`) ; `commun.blocs_construction.rendus_meuble` ;
  `document` (`RENDUS`, `STOCKHOLM`, `METOD`, `METOD_MIXTE`, `METOD_PLAN_LM`, `VRENA`, `NOIRS`, `IKEA_FR`, `LM_*`,
  `CASTO_*`, `METOD_RELEVE`, `JEU_METOD`, `METOD_CAISSON`) ; `pieces.salon.etageres.document.MONTANTS` ;
  `pieces.salon.amenagement.document` (`CANAPE`, `ALLEE_ENFILADE`).
- Produces : `vue_explication(ch: dict, chs: list[dict], n_etapes: int, total: str) -> Vue` (`total` : le total des achats
  écrit par `total_achats(<sections de la vue Achats>, arrondi=False)`, jamais recalculé) ; `vues.vues` y passe
  `len(etapes_montage(ch["g"]))` et ce total.

Contenu, dans l'ordre (ruling 11) ; aucun `h2` ne garde son ancien `id` (les tests lisent `<h2>…</h2>`) :
1. `tete(<chapô enf:L1185>, figure=figure_rendu(rendu(RENDUS_SITE, "", "iso"), RENDUS[0][1]))`.
2. `chiffres` : `(controle(), "Cotes hors tout (cm)")`, `(total, "Matériaux, composition C")`,
   `(f"{volume_utile():.0f} L", "Volume utile")`, `(str(len(debit(ps))), "Repères")`, `(str(len(ps)), "Pièces à débiter")`,
   `(str(n_etapes), "Étapes de montage")`, `(f"{cote(d1)} cm", "Devant la porte ouverte de M1")`, `(f"{cote(d2)} cm",
   "Devant un tiroir sorti")` (`d1, d2 = degagements()`).
3. `<h2>Le meuble</h2>` et le paragraphe de `enf:L758`.
4. `rendus_meuble(RENDUS_SITE, "", RENDUS, titre="Rendus 3D")`.
5. `section_construction` (`enf:L786-804`) sans `id` : « 3.8 » → `cote(PIEDS_X[0] - 1.25)` (« 3,8 ») et « 18.3 » →
   `cote(ch["c"]["chene_m2"] * 2, 1)` (« 18,3 »).
6. `section_materiaux` (`enf:L827-838`) : tableau en `<div class="defile"><table>`, cellule de variante
   `<b>C</b> retenu` pour la retenue, `class="num"` sur les montants, plus de `tr.retenu` ni de `badge`.
7. `section_comparaison` (`enf:L895-906`) : le dessin dans `<figure class="schema">`, `aria-label` = le texte sous le
   dessin (`enf:L898`, via le `titre` de `comparaison_svg`).
8. `section_metod` (`enf:L1049-1074`) : dessin en `<figure class="schema">`, `aria-label` = `enf:L1052` ; les cinq
   tableaux en `<div class="defile">`, statut en clair, plus de `class="mono"`.
9. `a_verifier([escape(p) for p in <enf:L1161-1174>], titre="Points à valider")`.
10. `note_source("Cotes et données du meuble : pieces/salon/enfilade/ (document.py, volumes.py), dans le repère du salon
    (pieces/salon/piece.py). Plan du salon : <a href=\"../../salon-v4.html\">Salon, aménagement</a>.")`.

- [ ] **Step 1 : copier les deux images**

```bash
mkdir -p site/salon/enfilade/rendus
cp -p salon-meubles-3d/enfilade-iso.jpg site/salon/enfilade/rendus/iso.jpg
cp -p salon-meubles-3d/enfilade-ouverte.jpg site/salon/enfilade/rendus/ouverte.jpg
cmp salon-meubles-3d/enfilade-iso.jpg site/salon/enfilade/rendus/iso.jpg && cmp salon-meubles-3d/enfilade-ouverte.jpg site/salon/enfilade/rendus/ouverte.jpg
```

Expected : aucune sortie de `cmp`. Aucune empreinte notée dans `cache/` (ruling 3).

- [ ] **Step 2 : écrire les tests**

```python
# tests/test_salon_enfilade_explication.py
import re
from html import escape
from pieces.salon.enfilade import chiffrage, document, vues
from tests.salon_enfilade_ancienne import corrige, morceaux, page, section, texte

S = vues.vues("")["explication"].elements[0].scene

def test_ordre_des_sections():
    assert re.findall(r"<h2>(.*?)</h2>", S) == ["Le meuble", "Rendus 3D", "Construction", "Matériaux",
        "Comparaison avec IKEA STOCKHOLM", "Comparaison avec trois METOD 80", "Points à valider"]

def test_chiffres_cles():
    assert re.findall(r"<dt>(.*?)</dt>", S) == ["240 × 60 × 80", "1027,95 €", "788 L", "13", "46", "11",
                                               "20,3 cm", "8,2 cm"]

def test_rendus():
    for cle, alt in document.RENDUS:
        assert (vues.RENDUS_SITE / f"{cle}.jpg").is_file()
        assert f'src="rendus/{cle}.jpg" alt="{escape(alt, quote=True)}"' in S
    assert S.count('src="rendus/iso.jpg"') == 2       # la tête et « Rendus 3D » (ruling 11)

def test_construction():
    assert re.findall(r"<h3>(.*?)</h3>", section_neuve("Construction")) == ["Trois caissons plutôt qu'un", "Caisson",
        "Dessus", "Socle : 8 pieds réglables", "Portes", "Tiroirs", "Étagères", "Fixation au mur", "Finition"]
    assert "moins de 3,8 d'épaisseur" in S and "18,3 m² de faces" in S

def section_neuve(titre):
    return S.split(f"<h2>{titre}</h2>", 1)[1].split("<h2>", 1)[0]

def test_materiaux_six_compositions():
    t = section_neuve("Matériaux")
    assert t.count("<tr>") == 1 + 6 and "<b>C</b> retenu" in t
    for montant in ("901,36 €", "1 027,95 €", "1 221,86 €", "−304,00 €", "+193,91 €"):
        assert montant in t

def test_comparaisons():
    assert S.count('<figure class="schema"><svg class="enf"') == 2
    caps = [texte(c) for c in re.findall(r'<p class="cap">(.*?)</p>', page(), re.S)][6:8]
    for cap in caps:
        assert f'aria-label="{escape(cap, quote=True)}"' in S
    metod = section_neuve("Comparaison avec trois METOD 80")
    assert metod.count('<div class="defile">') == 5 and "1 035,60 €" in metod and "966,40 €" in metod

def test_rien_ne_se_perd():
    for ancre in ("meuble", "construction", "materiaux", "comparaison", "metod", "valider"):
        for m in morceaux(section(page(), ancre)):
            assert corrige(m) in texte(S), (ancre, m)
    assert S.count("<li><span>") == 12                   # points à valider

def test_liens_externes_gardes():
    vieux = set(re.findall(r'href="(https?://[^"]+)"', page()[page().index("<body"):]))
    tout = "".join(v.elements[0].scene + v.fiche for v in vues.vues("").values() if v.elements)
    assert vieux <= set(re.findall(r'href="(https?://[^"]+)"', tout))

def test_remarque_finale_et_style():
    assert 'href="../../salon-v4.html"' in S and "3d/salon" not in S
    for interdit in ("·", "mono", "badge", 'class="cap"'):
        assert interdit not in S
```

- [ ] **Step 3 : lancer, constater l'échec**

Run : `uv run -q --no-project --with pytest pytest -q tests/test_salon_enfilade_explication.py`
Expected : FAIL (`h2` absents : l'Explication est encore vide).

- [ ] **Step 4 : écrire `pieces/salon/enfilade/explication.py`, brancher `vues.vues`**

- [ ] **Step 5 : lancer, constater le succès**

Run : `uv run -q --no-project --with pytest pytest -q tests/test_salon_enfilade_explication.py tests/test_salon_enfilade_vues.py`
Expected : 18 passed. Puis la suite entière : tout passe.

- [ ] **Step 6 : commit**

```bash
git add pieces/salon/enfilade/explication.py pieces/salon/enfilade/vues.py tests/test_salon_enfilade_explication.py site/salon/enfilade/rendus/iso.jpg site/salon/enfilade/rendus/ouverte.jpg
git commit -m "Enfilade : Explication (construction, matériaux, comparaisons STOCKHOLM et METOD) et rendus repris tels quels

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
```

### Task 5 : Script navigateur (`tests/navigateur/salon-enfilade.js`)

**Files:**
- Create: `tests/navigateur/salon-enfilade.js`

**Interfaces:**
- Consumes : la page construite par `python3 site.py` après la tâche 6 ; modèle : `tests/navigateur/entree.js`
  (`preparer`, `sansPolices`, `ouvrir`, `attendre`, `debordements`, à recopier : chaque script est autonome).
- Produces : une fonction `async page => {…}` qui renvoie `{ok, echecs, erreurs}`, marquée `@site reel` dans son
  commentaire de tête.

Vérifications, chacune une entrée d'`echecs` si elle échoue :
1. À 1440 × 900, 1100 × 800 et 390 × 844 : `DOC = ${BASE}/salon/enfilade/`, chaque vue (`plans`, `decoupe`, `montage`,
   `achats`, `explication`) et chaque repère de Plans (`elevation`, `iso`, `ouverte`, `profil`, `dessus`, `eclate`) :
   aucune erreur de console, aucune réponse ≥ 400, images chargées (`naturalWidth > 0`), `debordements` vide.
2. `DOC` sans fragment montre Plans, élément `elevation` ; aucun `#c-comp`, aucun `#c-variante`.
3. Mesurer : sur `#plans?k=elevation`, activer `.b-mesure`, cliquer les deux bouts de la ligne `line.dim` la plus longue
   (coordonnées écran par `getScreenCTM`) ; le bandeau affiche « Mesuré : 240 cm ». Sur `#plans?k=iso`, `.b-mesure` est
   caché.
4. Fiche de Plans : les liens « Découpe » et « Montage » mènent à `#decoupe` et `#montage`.
5. Dessins : dans chaque `svg.enf` visible, aucun élément de forme ou de texte dont le `fill` calculé est
   `rgb(0, 0, 0)` ; aucune `text` dont la boîte (`getBBox`, dans le repère du `svg`) sort du `viewBox`.
6. Achats : le total « 1027,95 € » ; Explication : deux `figure.schema`, les images `rendus/iso.jpg` et
   `rendus/ouverte.jpg`.
7. Anciennes adresses : `/salon-enfilade.html#debit` → `/salon/enfilade/#decoupe` ; `#meuble` →
   `#plans?k=elevation` ; `#iso` → `#plans?k=iso` ; `#valider` → `#explication` ; `#changements` →
   `/salon/enfilade/historique.html` ; `#inconnue` et sans fragment → `/salon/enfilade/` sans fragment.
8. Historique : `/salon/enfilade/historique.html` a sept `ol.fil li`, la première en V1.6.
9. Sans JavaScript (nouveau contexte, `javaScriptEnabled: false`) : les cinq sections sont visibles l'une sous l'autre
   (« Débit et découpe », « Outils et montage », « Achats et prix », « Points à valider » lisibles).

- [ ] **Step 1 : écrire le script**

- [ ] **Step 2 : vérifier sa syntaxe**

Run : `node --check tests/navigateur/salon-enfilade.js && grep -c "@site reel" tests/navigateur/salon-enfilade.js`
Expected : aucune erreur, puis `1`. (Le script tourne à la tâche 6, étape 7 : la page n'existe qu'après la bascule.)

- [ ] **Step 3 : commit**

```bash
git add tests/navigateur/salon-enfilade.js
git commit -m "Enfilade : script de vérification au navigateur

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
```

### Task 6 : Bascule

**Files:**
- Modify: `pieces/salon/enfilade/document.py` (ajout à la fin)
- Modify: `site.py:17` (import, ajouté après), `site.py:36` (la `Passerelle` de l'enfilade), `site.py:49` (ancres, après
  `HISTORIQUE_ENTREE`), `site.py:51-56` (`REDIRECTIONS`)
- Modify: `justfile` (nouvelle recette avant `# Salon V4 : régénère salon-v4.html…`, ligne 151)
- Modify: `.gitignore` (une ligne)
- Delete: `salon-enfilade.html` (`git rm`)
- Test: `tests/test_salon_enfilade_document.py`

**Interfaces:**
- Consumes : `vues.vues`, `dessins.CSS`, `document.VERSION`, `document.CHANGEMENTS` ; `commun.journal.entrees(site,
  racine)` ; `tests.outils.charger_site`.
- Produces : `pieces.salon.enfilade.document.DOCUMENT` : `Document("salon", "enfilade", "Enfilade", "construction",
  (Variante("", "Enfilade", VERSION, tuple(Changement(*c) for c in CHANGEMENTS)),), vues.vues, css=dessins.CSS)`,
  construit à la première lecture par `_document()` et `__getattr__(nom)` (modèle : `pieces/entree/amenagement/
  document.py:318-322`) ; `site.ANCRES_ENFILADE` et la `Redirection` de `salon-enfilade.html`.

- [ ] **Step 1 : écrire les tests**

```python
# tests/test_salon_enfilade_document.py
from commun.journal import entrees
from commun.modele import Changement
from pieces.salon.enfilade import dessins, document, vues
from tests.outils import RACINE, charger_site

ANCRES = {"iso": "plans?k=iso", "meuble": "plans?k=elevation", "rendus": "explication", "construction": "explication",
          "materiaux": "explication", "comparaison": "explication", "metod": "explication", "debit": "decoupe",
          "achats": "achats", "montage": "montage", "valider": "explication"}

def test_document():
    d = document.DOCUMENT
    assert (d.piece, d.id, d.nom, d.type, d.css, d.generer) == ("salon", "enfilade", "Enfilade", "construction",
                                                               dessins.CSS, vues.vues)
    (v,) = d.variantes
    assert (v.id, v.version, v.figees) == ("", "V1.6", ())
    assert v.changements == tuple(Changement(*c) for c in document.CHANGEMENTS) and len(v.changements) == 7

def test_site_declare_l_enfilade():
    site = charger_site().SITE
    (salon,) = [p for p in site.pieces if p.id == "salon"]
    assert [d for d in salon.documents if d.id == "enfilade"] == [document.DOCUMENT]

def test_redirection():
    (r,) = [r for r in charger_site().REDIRECTIONS if r.ancienne == "salon-enfilade.html"]
    assert (r.cible, r.ancres, r.motifs, r.pages) == ("salon/enfilade/", ANCRES, (),
                                                      {"changements": "salon/enfilade/historique.html"})
    assert r.ancres.get("inconnue", "") == ""            # ancre inconnue : vue par défaut

def test_journal_garde_sept_changements():
    lignes = [e for e in entrees(charger_site().SITE, RACINE) if (e.piece, e.document) == ("Salon", "Enfilade")]
    assert [e.version for e in lignes] == ["V1.6", "V1.5", "V1.4", "V1.3", "V1.2", "V1.1", "V1.0"]

def test_ancienne_page_retiree():
    assert not (RACINE / "salon-enfilade.html").exists()
    assert (RACINE / "3d/salon/enfilade.py").exists()     # l'ancien générateur reste (nettoyage commun)
    assert "/salon-enfilade.html" in (RACINE / ".gitignore").read_text(encoding="utf-8").split()
```

- [ ] **Step 2 : lancer, constater l'échec**

Run : `uv run -q --no-project --with pytest pytest -q tests/test_salon_enfilade_document.py`
Expected : FAIL (`AttributeError: … has no attribute 'DOCUMENT'`).

- [ ] **Step 3 : déclarer `DOCUMENT`, basculer `site.py`, la recette et `.gitignore`**

- `document.py`, à la fin : `_document()` importe `vues`, `dessins` et `Changement`, `Document`, `Variante` dans la
  fonction (pas à l'import) ; `__getattr__` comme à l'entrée.
- `site.py` : `from pieces.salon.enfilade import document as salon_enfilade` ; la ligne 36 devient
  `salon_enfilade.DOCUMENT,` ; après `HISTORIQUE_ENTREE`, `ANCRES_ENFILADE = {…}` (le dict `ANCRES` du test, avec un
  commentaire d'une ligne : « anciennes ancres de salon-enfilade.html, posées en dur par son générateur ») ; dans
  `REDIRECTIONS`, à la fin : `Redirection("salon-enfilade.html", "salon/enfilade/", ANCRES_ENFILADE, (),
  {"changements": "salon/enfilade/historique.html"}),`.
- `justfile`, avant la recette `salon` :

```
# Salon, enfilade : reconstruit sa page (site/salon/enfilade/) depuis pieces/salon/enfilade/
salon-enfilade:
    python3 site.py salon/enfilade
```

- `.gitignore` : ajouter `/salon-enfilade.html` (ruling 20).
- `git rm salon-enfilade.html`.

- [ ] **Step 4 : lancer les tests**

Run : `uv run -q --no-project --with pytest pytest -q tests`
Expected : tout passe, dont les 5 tests neufs, `tests/test_construction.py::test_site_py_tient_documents_et_redirections`
et `test_documents_declares` (aucun lien mort dans `salon/enfilade/` ni son historique).

- [ ] **Step 5 : construire le site et lire `git status`**

Run : `python3 site.py && git status --short site/ && git diff --word-diff=porcelain site/entree | grep '^[-+][^-+]' | sort -u`
Expected : sous `site/`, seulement `salon/enfilade/index.html`, `salon/enfilade/dessins.css`,
`salon/enfilade/historique.html` (nouveaux), `salon-enfilade.html` (devenue redirection), `journal.html`, `index.html`
et les menus des pages déjà construites (`entree/…`) ; dans `site/entree`, les seuls mots changés sont l'adresse du
menu, `-href="../../salon-enfilade.html"` et `+href="../../salon/enfilade/"` (ou leur forme relative à chaque page).
`grep -c "Enfilade" site/journal.html` : au moins 7 lignes « Salon › Enfilade ».

- [ ] **Step 6 : script navigateur**

Run : `PORT=8851 SESSION=refonte-salon-enfilade-1 tests/navigateur/lancer.sh tests/navigateur/salon-enfilade.js`
Expected : `"ok": true`, aucun échec, aucune erreur. Un échec dans le script ou dans la page se corrige dans la tâche
concernée, puis on relance.

- [ ] **Step 7 : remettre `site/` et commiter**

```bash
git checkout -- site && git clean -fdq site
git status --short    # attendu : seulement les fichiers de cette tâche
git add pieces/salon/enfilade/document.py site.py justfile .gitignore tests/test_salon_enfilade_document.py
git commit -m "Enfilade : bascule, le document remplace la passerelle, salon-enfilade.html redirige

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
```

(`git rm` a déjà mis la suppression de `salon-enfilade.html` dans l'index.)
