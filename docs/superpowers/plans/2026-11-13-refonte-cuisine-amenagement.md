# Cuisine, aménagement : migration de `cuisine-v13.html` vers `cuisine/amenagement/` (plan de travail)

> **Pour les agents qui exécutent ce plan :** skill requis : `superpowers:subagent-driven-development` (recommandé) ou
> `superpowers:executing-plans`, tâche par tâche, tests d'abord (`superpowers:test-driven-development`). Les étapes se
> cochent (`- [ ]`). Mode autonome : aucune question au client ; une décision imprévue se prend réversible et s'écrit
> dans le rapport de la tâche sous la forme `Ruling : <décision> — <pourquoi> — <coût si faux>`.

**But :** reprendre la cuisine V13.30 (`cuisine-v13.html` et ses deux annexes) dans le document `cuisine/amenagement`
du site refondu, vues Plan, Coupes, Iso, Caméra, Explication, sans rien perdre, puis rediriger les trois anciennes
adresses.

**Architecture :**
- **Données :** `3d/v13/modele.py` devient `pieces/cuisine/modele.py` (copie fidèle, source unique des deux documents
  de la cuisine) ; `pieces/cuisine/piece.py` en tire la pièce (contour, portes, caméras) ; `3d/v13/modele.py` reste
  un relais pour `porte.py` (page porte du cellier, migrée plus tard dans ce worktree).
- **Dessins et page :** les aides SVG de la cuisine vont dans `pieces/cuisine/dessin.py` (partagé avec `porte.py`) ;
  les sept dessins, la répartition de la légende du plan, l'Explication, les zones et les vues vont dans
  `pieces/cuisine/amenagement/` ; tout passe par les blocs de `commun/blocs.py`.
- **Rendu :** `cad.py` (FreeCAD) puis `rendu.py` (Blender) déplacés dans `pieces/cuisine/amenagement/`, branchés sur
  `commun/rendu_cache.py` ; les huit images actuelles sont reprises telles quelles, laissées « à rendre ».
- **Annexes :** un ajout minimal au socle (`commun.modele.Annexe`) écrit `imprimable.html` et `maquette-3d.html` à
  côté du document.

**Technologies :** Python 3.14 (bibliothèque standard), pytest par `uv`, FreeCAD 1.x (`freecadcmd`, Python 3.11),
Blender 5.2.2 (Cycles) par `blender-seul.sh`, `playwright-cli` par `tests/navigateur/lancer.sh`.

**Spécification :** `docs/superpowers/specs/2026-11-13-refonte-site-design.md` (fait autorité). À lire aussi :
`REGISTRE/consignes.md`, `REGISTRE/cuisine-amenagement/inventaire.md` (noté **INV** : ses numéros de ligne renvoient
à `cuisine-v13.html` = P, `3d/v13/plan.py` = PL, `3d/v13/modele.py` = MO, `3d/v13/rendu.py` = RE),
`REGISTRE/socle/rapport.md` (mode d'emploi des blocs), et le document à imiter : `pieces/entree/`,
`tests/test_entree.py`, `tests/navigateur/entree.js`.

`REGISTRE` = `/Users/nvi/code/work/personal/plan/.superpowers/sdd/2026-11-13-refonte-pages`. `WT` =
`/Users/nvi/code/work/personal/plan-wt/cuisine` (branche `refonte-cuisine`, base `refonte` 965af34). **Toute commande
commence par `cd /Users/nvi/code/work/personal/plan-wt/cuisine && …`.**

## Global Constraints

Chaque tâche les inclut sans les répéter.

- **Commandes :**
  - tests : `cd WT && uv run -q --no-project --with pytest pytest -q tests` (un fichier : `… pytest -q tests/<f>.py`) ;
  - construction : `cd WT && python3 site.py` (ou `python3 site.py cuisine/amenagement`) ;
  - après toute construction : `git checkout -- site && git clean -fdq site`, sauf les fichiers que la tâche commite
    sous `site/cuisine/amenagement/rendus/` et `site/cuisine/amenagement/maquette-3d/`.
- **Blender :** seulement par `REGISTRE/outils/blender-seul.sh`, jamais directement :
  `BLENDER_REEL=/opt/homebrew/bin/blender BLENDER=REGISTRE/outils/blender-seul.sh just <recette> …` (chemin absolu).
  Aperçu à 16 échantillons d'une vue seulement ; **aucune passe complète**, aucune empreinte notée dans
  `cache/empreintes.json` pour les huit vues de la cuisine.
- **FreeCAD :** `/Applications/FreeCAD.app/Contents/Resources/bin/freecadcmd` (Python 3.11 : tout module importé par
  `cad.py`, `pieces/cuisine/piece.py`, `pieces/cuisine/modele.py`, `commun/modele.py` reste lisible en 3.11, sans
  f-string imbriquée sur les mêmes guillemets ni syntaxe 3.12+).
- **Navigateur :** `cd WT && PORT=<8880…8889> SESSION=refonte-cuisine-amenagement-<n> tests/navigateur/lancer.sh
  tests/navigateur/cuisine-amenagement.js`. Jamais `close-all`, `kill-all`, la session `prod`, ni les ports 8800 et
  8811. Fermer seulement ses propres sessions.
- **Interdits :** `git push` ; fusion dans `refonte` ; écriture sur `main` ; réglages GitHub ; lire le PDF du
  logement ; modifier `site/` à la main ; commiter `site/` hors `site/cuisine/amenagement/rendus/`,
  `site/cuisine/amenagement/maquette-3d/modele.js` et la suppression des dossiers orphelins `site/cuisine-v13-3d/`,
  `site/cuisine-v13-maquette/` (tâche 11) ; toucher `3d/sortie/`,
  `3d/textures/`, `3d/modeles/`, `cache/` du dépôt principal, `achats/`, `reddit/`, les `git stash`.
- **Ne jamais supprimer :** `3d/v11/`, `3d/v12/`, `3d/cuisine_a.py`, `cuisine-plan.html`, `cuisine-couleurs.html`,
  `cuisine-3d/`, `cuisine-v13-porte-cellier.html`, `3d/v13/porte.py`, `3d/v13/figees/`, `3d/rendu.py`,
  `3d/ancres.js`, `archive/`, `images/`.
- **`porte.py` reste fonctionnel :** `python3 3d/v13/porte.py` passe à chaque commit ; jusqu'à la bascule il écrit
  un fichier identique à `tests/fixtures/cuisine/porte-cellier.html` ; à la bascule, seuls ses deux liens vers
  `cuisine-v13.html` changent (tâche 11).
- **`commun/` :** seul ajout permis avant la tâche 12 : `Annexe` (tâche 10). Aucune modification de
  `commun/site.js`, de `commun/site.css` ni de `commun/blocs.py` pour les options. Après tout changement de `commun/` :
  `python3 site.py && git status --short site/entree` ne sort aucune ligne.
- **`site.py` et `justfile` :** ne toucher que les lignes de la cuisine/aménagement (et la recette `v13-porte`).
- **Document :** pièce `cuisine`, id `amenagement`, nom « Aménagement », type `amenagement` ; **une seule variante,
  d'id vide `""`**, nom « Principale », version `"V13.30"` (lue dans `modele.VERSION`) ; **90 changements**, dans
  l'ordre de `modele.CHANGEMENTS` (V13.30 d'abord) ; `figees = (("V11.49", "archive/cuisine-v11.49.html"),
  ("V12.7", "archive/cuisine-v12.7.html"))`.
- **Vues, dans l'ordre :** Plan, Coupes, Iso, Caméra, Explication ; s'ouvre sur Plan.
  - Plan : éléments `""` (« Plan ») puis `"elec"` (« Électricité ») ; aucune zone n'a l'id `""` ni `"elec"`.
  - Coupes : `"A"`, `"B"`, `"C"`, `"elec"` (majuscules : le motif de redirection met la lettre en capitale).
  - Iso : coins `no`, `so` rendus, `ne`, `se` grisés (« Pas encore rendu »), puis l'élément `"so-nuit"`.
  - Caméra : `entree`, `fenetre`, `banquette`, `dos_cellier`, `cellier` (ordre de l'ancienne galerie).
- **Rendus :** sous `site/cuisine/amenagement/rendus/`, sans préfixe de variante : `iso_so.jpg` (ancien `iso`),
  `iso_so_nuit.jpg` (`iso_nuit`), `iso_no.jpg`, `entree.jpg`, `fenetre.jpg`, `banquette.jpg`, `cellier.jpg`,
  `dos_cellier.jpg`, octet pour octet ceux de `cuisine-v13-3d/` (V13.26, `iso_no` V13.27).
- **Valeurs figées jusqu'à la tâche 12 (= défauts de l'ancienne page, ruling de l'orchestrateur) :** taille
  **1,75 m** (règle `data-t="175"` seule visible), porte de l'entrée **fermée** (`data-etat="ferme"`), porte du
  cellier **mi-ouverte** (`data-etat="mi"`, comme `plan.py` l.252), porte du cellier **en transparence** sur la
  coupe C (comme `plan.py` l.1324 : `.trp` tireté, étiquettes `.trp-lbl` visibles ; la légende reprise dit
  « dessinée en transparence »). CSS sans sélecteur `.fig`/`.transp`/`html` (filtrés par `css_dessins`) : règle
  `.trp{…}` directe, `.trp-lbl` jamais cachée.
- **Style :** aucun point médian (U+00B7) dans ce que génère la page, ses annexes, ses alt et ses changements : une
  virgule à la place (« cellier, 1,44 m² », « L2, LED ») ; aucune police à chasse fixe (`JetBrains Mono`,
  `monospace`) dans `dessins.css` ; pas d'étiquette en capitales, pas de flèche ajoutée, pas de mode sombre
  (`prefers-color-scheme`) ; jetons de couleur de `site.css`.
- **Textes exacts :** « Pas encore rendu », « Sans objet », « Touchez un meuble pour afficher sa fiche. »,
  « Position », « Personnaliser », « Valeurs d'origine ». **Jamais :** cases à cocher, « Copier la liste »,
  « À venir », « Lecture du plan », « Lecture de la coupe », description d'image à l'écran, onglet Historique.
- **Dimensions :** aucun nombre écrit en dur dans un texte nouveau ni dans une fiche ; les textes repris de
  l'ancienne page gardent leurs chiffres (ils sont déjà calculés par les f-strings de `plan.py`).
- **Git :** commits petits, en français, sur `refonte-cuisine`, terminés par la ligne
  `Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>` ; `git status` propre en fin de tâche.

## Review Focus

1. **Lien vers un meuble ou vers le plan électrique** (`#plan?k=b3`, `#plan?k=elec`, ancien `#electricite`) : `k`
   désigne à la fois l'élément et le meuble ; un meuble ouvre sa fiche sur le plan meublé, `elec` montre le plan
   électrique sans fiche de meuble. Testé : tâche 9 (`test_ids_de_zones_distincts_des_elements`), tâche 11 (script).
2. **Page sans JavaScript :** les fiches de meubles sont des `<template>` invisibles ; tout texte de la légende du
   plan doit aussi se lire dans l'Explication. Testé : tâche 7 (`test_chaque_morceau_visible_sans_js`).
3. **Ancienne adresse avec une ancre d'une version figée ou inconnue** (`#V11.49`, `#coupe-a-a-mur-nord-v12-7`,
   `#br`, `#inconnue`) : archive de la version, ou vue par défaut. Testé : tâche 11
   (`test_redirection_ancres_figees`, `test_redirection_ancre_inconnue`).
4. **Fichiers cités depuis une adresse plus profonde** (`images/cuisine-sol-reference.png`, `modele.js` de la
   maquette, `favicon.svg` des annexes) : aucune réponse 404. Testé : tâche 8 (`test_liens_locaux_existent`),
   tâche 10 (`test_annexes_liens_locaux`), tâche 11 (script).
5. **Largeur 390 px :** tableaux larges de l'Explication (capacité, points, hauteur du plan) et dessin de hauteur
   du plan : chaque `<table>` est dans un `<div class="defile">`. Testé : tâche 8 (`test_tableaux_defilent`), tâche
   11 (script).

## Rulings de ce plan

- Ruling : variante unique d'id `""` (et non `principale`) — convention du socle pour un document sans variante
  (rendus `rendus/<clé>.jpg`, `-` en ligne de commande) — coût : renommer les images et la clé du cache.
- Ruling : `pieces/cuisine/modele.py` reste un seul module, copie de `3d/v13/modele.py` ; `piece.py` en tire la pièce
  (et non l'inverse) — la baie du cellier dépend des colonnes (`JOUE_C2`), l'enveloppe ne se sépare pas des meubles
  sans réécrire le modèle — coût : inverser la dépendance plus tard.
- Ruling : modèle au niveau de la pièce (`pieces/cuisine/`), pas du document — la porte du cellier le lit aussi
  (`TANGO`, `PLIANTE`) — coût : un déplacement de module.
- Ruling : aides SVG propres à la cuisine dans `pieces/cuisine/dessin.py`, pas celles de `commun/dessin.py` — leur
  `f` diffère (`f"{v:g}"` contre `round(v, 1)`) : les dessins changeraient — coût : deux jeux d'aides.
- Ruling : plan électrique = second élément de la vue Plan (`k="elec"`), élévation électrique = quatrième coupe
  (`k="elec"`, trait de la coupe A) — INV §3 lignes 8 et 9 — coût : déplacer un élément.
- Ruling : rendu de nuit = élément `so-nuit` de l'Iso, caméra `iso_so_nuit` — pas une option (INV §14, plan des
  options du socle) — coût : une option Jour/Nuit à ajouter plus tard.
- Ruling : la chaîne de rendu écrit dans `cache/cuisine/` (ignoré par git, propre au worktree) au lieu de
  `3d/sortie/` (lien partagé avec le dépôt principal) — spec : `cache/` remplace `3d/sortie/`, et deux worktrees ne
  s'écrasent pas — coût : le `.blend` et le `.glb` ne sont plus au chemin d'avant.
- Ruling : la version de FreeCAD n'entre pas dans l'empreinte (le code de `cad.py` et le modèle, si) — `CacheRendu`
  ne connaît que la version de Blender — coût : une mise à jour de FreeCAD ne relance pas les rendus.
- Ruling : légende du plan coupée en morceaux ; les phrases de convention (échelle, sols, cloisons déposées) vont dans
  la légende de la fiche du plan, tout le reste en cartes « Principe » de l'Explication ; la fiche d'un meuble
  reprend les cartes qui le nomment et sa ligne de `CONTENU` — rien ne se perd, tout se lit sans JS — coût : texte en
  double (carte et fiche).
- Ruling : légende sous un dessin = texte alternatif du dessin (aria-label) ; légende sous un tableau ou note de
  section = remarque visible de l'Explication — consignes « Retirés par décision » — coût : rendre visible un alt.
- Ruling : `Annexe` (adresse sous le dossier du document, fonction qui rend la page) ajoutée à `commun/modele.py` et
  écrite par `commun/construction.py` — le socle n'a aucun mécanisme de page annexe (INV §5) — coût : annexes en
  passerelle à la racine.
- Ruling : `modele.js` de la maquette commité sous `site/cuisine/amenagement/maquette-3d/modele.js`, écrit par
  `maquette.py` — `site.py` ne sait pas le refaire (Blender), consignes « Interdits » (a) — coût : déplacer 5 Mo.
- Ruling : annexes reprises telles quelles, liens rebasés et points médians remplacés ; polices d'origine gardées
  (signalé au client) — spec « page à part, inchangée » — coût : restyler deux pages.
- Ruling : `SURFACE` calculée sur `SOL` dans `piece.py` (comme le salon) — l'accueil affiche une surface au lieu de
  « 325 × 252 » (au client) — coût : retirer `SURFACE`.
- Ruling : `DOCUMENT` n'est exposé par `document.py` qu'à la bascule ; avant, `document.construire_document()` —
  `tests/test_construction.py::test_documents_declares` exige que tout `DOCUMENT` sur disque soit dans `SITE` —
  coût : aucun.
- Ruling : coupes en majuscules `A`, `B`, `C` (INV proposait des minuscules) — `commun/redirections.py` met le groupe
  du motif en capitale, l'entrée fait de même — coût : réécrire les motifs.
- Ruling : la recette `v13` est remplacée par `v13-porte` (`python3 3d/v13/porte.py`) — `plan.py` disparaît, la
  page porte du cellier doit rester régénérable — coût : un nom de recette.
- Ruling (orchestrateur, remplace celui du plan) : valeurs figées et défauts des options = défauts de l'ancienne
  page (1,75 m, entrée fermée, cellier mi-ouvert, coupe C en transparence) — consignes : « le plus fidèle à
  l'ancienne page », et la légende reprise de la coupe C dit « dessinée en transparence » — coût : deux défauts à
  changer.

## Tableau de contenu : chaque section de l'ancienne page, et la vue qui la reprend

Relu sur `cuisine-v13.html` (V13.30, P l.185-297 ; blocs figés l.298-417). 22 légendes (14 `p.cap`, 8 `figcaption`),
9 tableaux, 7 dessins, 8 rendus. Colonne « Ancre » : identifiant que `3d/ancres.js` posait sur le `h2` → fragment de
la nouvelle adresse (`site.py`, tâche 11). Une ancre absente ouvre le Plan.

| # | Section de l'ancienne page | Ancre | Devient (tâche) | Retiré, et décision qui le retire |
|---|---|---|---|---|
| 1 | Barre : « V13.30 en cours », « V11.49 figée », « V12.7 figée » | `V11.49`, `V12.7` → archives | `historique.html` : versions figées V11.49 et V12.7 (`Variante.figees`, 9) | Les boutons : « bouton d'une version figée dans la page » (consignes) ; spec « Versions figées : en archive seulement » |
| 2 | Barre : « Explications » (montrait les légendes) | | Légendes des dessins et des rendus en texte alternatif (5, 9) | Le bouton : « pas de descriptions d'images à l'écran » |
| 3 | Barre : « Changements » | | Pastille de version → `historique.html` (9) | |
| 4 | Barre : « ← Plans » | | Menu de gauche, icône maison (socle) | |
| 5 | Sommaire | | Onglets des vues (socle) | Le sommaire : « une navigation identique sur toutes les pages » |
| 6 | Surtitre « Cuisine, V13.30 » et titre « Plan de la cuisine V13 » | | Barre du haut : pièce, document, pastille de version (socle) | |
| 7 | Chapô (`p.pitch`) | | Explication : chapô de `tete` (8) | |
| 8 | Titre du plan : liens « Maquette 3D », « Porte du cellier », « Version imprimable » | `plan` → `plan` | Explication : liens de `tete` vers `maquette-3d.html`, `imprimable.html`, la page porte du cellier (8) | |
| 9 | Plan : boutons « Portes » (entrée 2 états, cellier 3 états) | | Entrée fermée, cellier mi-ouvert, figés (5) ; options `porte-entree`, `porte-cellier` de « Personnaliser » (12, si `rapport-options.md`) | Les boutons posés sur le dessin : spec « Personnaliser » générique |
| 10 | Plan : dessin (dessin 1/7) | | Plan, élément `""`, meubles touchables (`Zone`, ids stables) (5, 6, 9) | |
| 11 | Plan : légende, 8 439 caractères (légende 1/22) | | Conventions → légende de la fiche du plan ; le reste → cartes « Principe » de l'Explication, chacune reprise dans la fiche de son meuble (7) | |
| 12 | Coupe A-A : dessin (2/7) | `coupe-a-a-mur-nord` → `coupes?k=A` | Coupes, `A` (5, 9) | |
| 13 | Coupe A-A : légende, 856 c. (2/22) | | Texte alternatif de la coupe A (9) | Le texte à l'écran : « pas de descriptions d'images à l'écran » |
| 14 | Coupes A et C : bouton « Taille » et règle des hauteurs | | Règle 1,75 m figée (5) ; option `taille` (12, si `rapport-options.md`) | Le bouton sur le dessin : « Personnaliser » générique |
| 15 | Coupe A-A : pastilles de couleur de la règle (`TAILLE_LEG`) | | Fiche des éléments A et C de Coupes (9) | |
| 16 | Hauteur du plan de travail (étude) : titre | `hauteur-du-plan-de-travail-etude` → `explication` | Explication, « Hauteur du plan de travail (étude) » (8) | |
| 17 | … légende « Étude seulement », 118 c. (3/22) | | Même partie, remarque sous le titre (8) | |
| 18 | … dessin (3/7) | | Même partie, figure (5, 8) | |
| 19 | … légende du dessin, 584 c. (4/22) | | Texte alternatif du dessin (8) | Le texte à l'écran : « pas de descriptions d'images à l'écran » |
| 20 | … tableau des hauteurs candidates (tableau 1/9) et texte (sources comprises) | | Même partie (8) | |
| 21 | Coupe B-B : dessin (4/7) | `coupe-b-b-mur-sud` → `coupes?k=B` | Coupes, `B` (5, 9) | |
| 22 | Coupe B-B : légende, 573 c. (5/22) | | Texte alternatif de la coupe B (9) | « pas de descriptions d'images à l'écran » |
| 23 | Coupe C-C : dessin (5/7) | `coupe-c-c-mur-est` → `coupes?k=C` | Coupes, `C` (5, 9) | |
| 24 | Coupe C-C : légende, 853 c. (6/22) | | Texte alternatif de la coupe C (9) | « pas de descriptions d'images à l'écran » |
| 25 | Coupe C-C : bouton « en transparence » | | En transparence, figée (5) ; option `transparence` (12, si `rapport-options.md`) | Le bouton sur le dessin : « Personnaliser » générique |
| 26 | Porte du cellier, Mantion Tango : titre et lien « Plans détaillés » | `porte-du-cellier-mantion-tango` → `explication` | Explication, « Porte du cellier, Mantion Tango », lien vers la page porte du cellier (8) | |
| 27 | … fiche Tango, 6 lignes (tableau 2/9) | | Même partie (8) | |
| 28 | … texte (principe, ouverture, pourquoi, pose) et sources | | Même partie (8) | |
| 29 | Électricité : plan électrique (6/7) | `electricite` → `plan?k=elec` | Plan, élément `elec` (5, 9) | |
| 30 | … légende du plan électrique, 566 c. (7/22) | | Texte alternatif du plan électrique (9) | « pas de descriptions d'images à l'écran » |
| 31 | … « Quel interrupteur allume quoi » : tableau 7 lignes (3/9) et légende 576 c. (8/22) | | Explication, « Électricité » : le tableau puis la remarque (8) | |
| 32 | Élévation du mur nord, électricité : dessin (7/7) | `elevation-du-mur-nord-electricite` → `coupes?k=elec` | Coupes, `elec`, trait de la coupe A (5, 9) | |
| 33 | … légende, 211 c. (9/22) | | Texte alternatif de l'élévation (9) | « pas de descriptions d'images à l'écran » |
| 34 | … « Points », 17 lignes (4/9) | | Explication, « Électricité » (8) | |
| 35 | … « Circuits proposés », 8 lignes (5/9) | | Explication, « Électricité » (8) | |
| 36 | … note NF C 15-100, 950 c. (10/22) | | Explication, « Électricité », remarque (8) | |
| 37 | Rendus 3D : titre et lien « Maquette 3D » | `rendus-3d` → `iso` | Iso et Caméra (9) ; lien dans `tete` (8) | |
| 38 | … iso sud-ouest de jour et iso nord-ouest (rendus 1-2/8) | | Iso, `so` et `no` ; `ne`, `se` grisés (4, 9) | |
| 39 | … iso de nuit (3/8) et bouton « Jour / Nuit » | | Iso, élément `so-nuit` (4, 9) | Le bouton : remplacé par l'élément (ruling) |
| 40 | … depuis l'entrée, la fenêtre, la banquette, dos au cellier, entrée du cellier (4-8/8) | | Caméra : `entree`, `fenetre`, `banquette`, `dos_cellier`, `cellier` (4, 9) | |
| 41 | … légendes des huit rendus (11-18/22) | | Texte alternatif de chaque rendu ; « yeux à X cm, objectif Y mm » dans la fiche caméra (9) | Le texte à l'écran : « pas de descriptions d'images à l'écran » |
| 42 | … note de méthode des rendus, 240 c. (19/22) | | Explication, « Rendus », remarque (8) | |
| 43 | Matériaux : tableau 16 lignes (6/9), échantillons et photo du parquet | `materiaux` → `explication` | Explication, « Matériaux » (bloc `materiaux`, échantillon en tête de la seconde colonne) (8) | |
| 44 | … légende, 166 c. (20/22) | | Même partie, remarque (8) | |
| 45 | Contenu des rangements : tableau 27 lignes (7/9) et légende 467 c. (21/22) | `contenu-des-rangements` → `explication` | Explication, même titre (8) ; chaque ligne aussi dans la fiche de son meuble (6) | |
| 46 | Capacité V11.34 → V13.30 et proposition 9 A : tableau 17 lignes (8/9) et légende 740 c. (22/22) | `capacite-…` (motif `^capacite-`) → `explication` | Explication, même titre (8) ; spec objectif 3 le garde dans l'Explication | |
| 47 | Note « Repère… Source… » | | Explication, `note_source` : le repère et le fichier des dimensions `pieces/cuisine/modele.py` (8) | Les chemins de l'ancien générateur (`3d/v13/plan.py`, `cad.py`), supprimé ou déplacé |
| 48 | Changements : tableau 90 lignes (9/9) | `changements` → `historique.html` | `historique.html` et `journal.html`, 90 entrées « Cuisine › Aménagement » (9) | De la page : « Le tableau des changements va dans l'historique » (consignes) |
| 49 | Bloc figé V11.49 (P l.298-347) | `V11.49`, `changements-V11.49`, `<h2>-v11-49` → `archive/cuisine-v11.49.html` | Historique : version figée V11.49 (9, 11) | La copie dans la page : version figée lue en archive (spec) |
| 50 | Bloc figé V12.7 (P l.348-417) | `V12.7`, `changements-V12.7`, `<h2>-v12-7` → `archive/cuisine-v12.7.html` | Historique : version figée V12.7 (9, 11) | Idem |
| 51 | Scripts (ancres, versions, sommaire, portes, taille, transparence, Jour/Nuit) | `br`, `br-V11.49`, `br-V12.7` → `plan` | `commun/site.js` (socle) ; réglages : lignes 9, 14, 25, 39 | Scripts propres à la page : « barres propres à l'ancienne page » |
| 52 | Annexe `cuisine-v13-imprimable.html` | sans ancre | `cuisine/amenagement/imprimable.html` (10) | |
| 53 | Annexe `cuisine-v13-maquette.html` et `cuisine-v13-maquette/modele.js` | sans ancre | `cuisine/amenagement/maquette-3d.html`, `maquette-3d/modele.js` (10) | |

Contrôle des comptes : légendes 11, 13, 17, 19, 22, 24, 30, 31, 33, 36, 41 (×8), 42, 44, 45, 46 = 22 ; tableaux
20, 27, 31, 34, 35, 43, 45, 46, 48 = 9 ; dessins 10, 12, 18, 21, 23, 29, 32 = 7 ; rendus 38 (×2), 39, 40 (×5) = 8.
Le test `test_tableau_de_contenu` (tâche 9) vérifie chaque destination sur les fichiers de référence de la tâche 1.

## Fichiers

| Fichier | Rôle | Tâche |
|---|---|---|
| `tests/fixtures/cuisine/extraire.py` et ses sorties | référence figée de l'ancienne page (dessins, légendes, tableaux, ancres, annexes, modèle) | 1 |
| `tests/cuisine_anciens.py` | charge un ancien module de `3d/v13/`, saute le test s'il n'existe plus | 1 |
| `pieces/cuisine/__init__.py`, `modele.py` | source unique de la cuisine (ancien `3d/v13/modele.py`) | 2 |
| `3d/v13/modele.py` | relais : le module `pieces.cuisine.modele` lui-même | 2 |
| `pieces/cuisine/piece.py` | pièce : contour, portes, caméras, position | 2 |
| `pieces/cuisine/dessin.py` | aides SVG de la cuisine, CSS de l'ancienne page, fiche Tango (partagés avec `porte.py`) | 3 |
| `pieces/cuisine/amenagement/{__init__,rendu,cad,video,maquette}.py` | chaîne FreeCAD puis Blender | 4 |
| `pieces/cuisine/amenagement/document.py` | `CACHE_RENDU`, puis Document (9), puis `DOCUMENT` (11) | 4, 9, 11 |
| `pieces/cuisine/amenagement/dessins.py` | les sept dessins et leur CSS (`CSS_DESSINS`) | 5 |
| `pieces/cuisine/amenagement/zones.py` | meubles touchables du plan | 6 |
| `pieces/cuisine/amenagement/legende.py` | légende du plan en morceaux | 7 |
| `pieces/cuisine/amenagement/explication.py` | contenu de la vue Explication | 8 |
| `pieces/cuisine/amenagement/vues.py` | `vues(variante)` | 9 |
| `commun/modele.py`, `commun/construction.py` | `Annexe` | 10 |
| `pieces/cuisine/amenagement/imprimable.py`, `maquette-3d.html` | les deux annexes | 10 |
| `tests/test_cuisine_*.py` | un fichier par tâche | 1-12 |
| `tests/navigateur/cuisine-amenagement.js` | vérification au navigateur (`@site reel`) | 11 |

---

### Task 1 : Fichiers de référence de l'ancienne page

L'ancienne page et ses générateurs disparaissent à la tâche 11 : leurs sorties sont figées ici, et toutes les tâches
suivantes s'y comparent.

**Files:**
- Create: `tests/fixtures/cuisine/extraire.py`, `tests/fixtures/cuisine/{dessins/*.svg, legendes.json, tableaux.json,
  ancres.json, index.json, imprimable.html, porte-cellier.html, maquette.html, modele.json, rendu.json}`
- Create: `tests/cuisine_anciens.py`, `tests/test_cuisine_reference.py`

**Interfaces:**
- Produces:
  - `tests/cuisine_anciens.py` : `ancien(nom: str) -> types.ModuleType` (importe `3d/v13/<nom>.py` avec `3d/v13` en
    tête de `sys.path` ; `pytest.skip` si le fichier n'existe plus) ; `FIXTURES: Path` = `tests/fixtures/cuisine`.
  - `dessins/<nom>.svg`, sept fichiers, le `<svg>` tel qu'il est dans la page : `plan`, `coupe-a` (avec la règle),
    `hauteur-pt`, `coupe-b`, `coupe-c` (avec la règle), `plan-elec`, `elevation-elec`.
  - `legendes.json` : `{id: html intérieur}`, 22 clés exactement : `plan`, `coupe-a`, `hauteur-pt-etude`,
    `hauteur-pt`, `coupe-b`, `coupe-c`, `plan-elec`, `interrupteurs`, `elevation-elec`, `nfc`, `rendu-iso`,
    `rendu-iso_nuit`, `rendu-iso_no`, `rendu-entree`, `rendu-fenetre`, `rendu-banquette`, `rendu-dos_cellier`,
    `rendu-cellier`, `rendus-methode`, `materiaux`, `contenu`, `capacite`.
  - `tableaux.json` : `{id: html du <table>}`, 9 clés : `hauteur-pt`, `tango`, `interrupteurs`, `points`, `circuits`,
    `materiaux`, `contenu`, `capacite`, `changements`.
  - `ancres.json` : liste ordonnée `[{"id", "bloc", "texte"}]` de chaque `h2` de la page (bloc `courante`, `V11.49`,
    `V12.7`), id calculé comme `3d/ancres.js` (fonction `slug` portée en Python : NFD, sans diacritiques, minuscules,
    `[^a-z0-9]+` → `-`, sans tirets de bord ; texte du `h2` sans ses `a`, `span`, `button` ; suffixe `-<slug(version)>`
    dans un bloc figé ; id de la `section` parente s'il en a un ; `-2`, `-3` en cas de doublon), plus les autres `id`
    de la page (`br`, `br-V11.49`, …).
  - `imprimable.html`, `porte-cellier.html` : `imprimable.page()` et `porte.page()` ; `maquette.html` : copie de
    `cuisine-v13-maquette.html` (écrite à la main, pas de générateur).
  - `modele.json` : `{nom: valeur}` de `commun.rendu_cache.donnees_variante(<module modele>)`, préfixe de module retiré,
    écrit par `json.dumps(..., sort_keys=True, default=commun.rendu_cache._json, ensure_ascii=False, indent=1)`.
  - `rendu.json` : `{"COUPES_ISO": str, "COUPES_ISO_NO": str}`, lus par `ast` dans `3d/v13/rendu.py` (pas d'import :
    il demande `bpy`).
  - `index.json` : pour chaque fichier : source (fonction de `plan.py`), aria-label, nombre de caractères du texte.

- [ ] **Step 1 : écrire les tests** dans `tests/test_cuisine_reference.py`.

```python
def test_reference_complete():
    leg = json.loads((FIXTURES / "legendes.json").read_text(encoding="utf-8"))
    tab = json.loads((FIXTURES / "tableaux.json").read_text(encoding="utf-8"))
    assert len(leg) == 22 and len(tab) == 9
    assert sorted(p.stem for p in (FIXTURES / "dessins").glob("*.svg")) == sorted(
        ["plan", "coupe-a", "hauteur-pt", "coupe-b", "coupe-c", "plan-elec", "elevation-elec"])
    assert len(_texte(leg["plan"])) == 8439          # texte sans balises, entités décodées
    assert tab["changements"].count("<tr") == 91     # en-tête + 90 changements

def test_reference_a_jour():
    plan = ancien("plan")                             # saute après la bascule
    page = (RACINE / "cuisine-v13.html").read_text(encoding="utf-8")
    assert plan.page(plan.lire_figees()) == page      # l'ancienne page se régénère à l'identique
    assert extraire.extraire(page) == extraire.lire(FIXTURES)   # mêmes morceaux que sur disque

def test_annexes_de_reference():
    assert ancien("imprimable").page() == (FIXTURES / "imprimable.html").read_text(encoding="utf-8")
    assert ancien("porte").page() == (FIXTURES / "porte-cellier.html").read_text(encoding="utf-8")
    assert (FIXTURES / "imprimable.html").read_text(encoding="utf-8") == (RACINE / "cuisine-v13-imprimable.html").read_text(encoding="utf-8")

def test_ancres():
    ids = [a["id"] for a in json.loads((FIXTURES / "ancres.json").read_text(encoding="utf-8"))]
    for a in ("plan", "coupe-a-a-mur-nord", "hauteur-du-plan-de-travail-etude", "coupe-b-b-mur-sud",
              "coupe-c-c-mur-est", "porte-du-cellier-mantion-tango", "electricite",
              "elevation-du-mur-nord-electricite", "rendus-3d", "materiaux", "contenu-des-rangements",
              "capacite-v11-34-v13-30-et-proposition-9-a", "changements", "changements-V11.49", "changements-V12.7"):
        assert a in ids, a
    assert any(i.endswith("-v11-49") for i in ids) and any(i.endswith("-v12-7") for i in ids)
```

- [ ] **Step 2 : lancer, constater l'échec** : `… pytest -q tests/test_cuisine_reference.py` → `ModuleNotFoundError`
  ou fichiers absents.

- [ ] **Step 3 : écrire `extraire.py`** (modèle : `tests/fixtures/salon/extraire.py`) : `extraire(page: str) -> dict`
  (les morceaux ci-dessus, seulement la partie courante pour légendes, tableaux et dessins : avant
  `<div class="ver" data-v="V11.49"`), `lire(dossier: Path) -> dict` (même forme depuis le disque), et `__main__` qui
  régénère la page par `plan.page(plan.lire_figees())` **en mémoire** (aucune écriture à la racine) et écrit le
  dossier. Lancer `python3 tests/fixtures/cuisine/extraire.py`.

- [ ] **Step 4 : vérifier** : `… pytest -q tests/test_cuisine_reference.py` → 4 passés ; `git status` ne montre que
  `tests/` (aucune page de la racine modifiée).

- [ ] **Step 5 : commit**

```bash
git add tests/fixtures/cuisine tests/cuisine_anciens.py tests/test_cuisine_reference.py
git commit -m "Cuisine : fichiers de référence de l'ancienne page (dessins, légendes, tableaux, ancres, annexes)"
```

### Task 2 : Source unique et pièce de la cuisine

**Files:**
- Move: `3d/v13/modele.py` → `pieces/cuisine/modele.py` (`git mv`, contenu inchangé sauf l'en-tête de commentaire)
- Create: `pieces/cuisine/__init__.py`, `pieces/cuisine/piece.py`, `3d/v13/modele.py` (relais)
- Create: `tests/test_cuisine_piece.py`

**Interfaces:**
- Consumes: `tests/fixtures/cuisine/modele.json`, `rendu.json` (tâche 1) ; `commun.modele.Camera`.
- Produces:
  - `pieces.cuisine.modele` : tous les noms de l'ancien `3d/v13/modele.py`, mêmes valeurs.
  - `3d/v13/modele.py` : `sys.path` pointé sur la racine, puis
    `sys.modules[__name__] = importlib.import_module("pieces.cuisine.modele")` (le même objet module : `import modele
    as M` dans `porte.py`, `plan.py`, `imprimable.py` voit les mêmes valeurs, `_` compris).
  - `pieces.cuisine.piece` : `ID = "cuisine"`, `NOM = "Cuisine"`, `POSITION = (-220, -262, 0)`, `H`, `Bloc`, `Cyl`,
    `Pan`, `ENVELOPPE` (ceux du modèle) ; `SOL` (8 sommets, repère de la cuisine : (0, 0), (327, 0), (327, 115),
    (382, 115), (382, 240), (341, 240), (341, 252), (0, 252), tirés de `commun.appartement.APPART` moins
    `POSITION` et vérifiés contre l'enveloppe) ; `SOL_ET_CELLIER` (cuisine et cellier, pour « Position ») ;
    `SURFACE: float` (m², aire de `SOL`) ; `PORTES` : `[dict(nom="entree", piece="Entrée", mur="s", face=252,
    a=ENTREE["x0"], b=ENTREE["x1"], type="galandage"), dict(nom="cellier", piece="Cellier", mur="e", face=320,
    a=BAIE_Y0, b=BAIE_Y1, type="pliante")]` (valeurs lues dans le modèle) ; `DEBOUT = 163`, `ASSIS = 120` ;
    `COUPES_ISO`, `COUPES_ISO_NO` (les motifs de `rendu.json`) ; `CAMERAS: tuple[Camera, ...]`.
  - Caméras (RE l.476-496 ; `reglages` : `coupes`, `decentrement`, `porte` = `"fermee"`, `nuit`) :

| id | nom | loc | cible | optique | reglages |
|---|---|---|---|---|---|
| `iso_so` | Isométrique sud-ouest | (-380, 700, 640) | (250, 120, 60) | `ortho=6.0` | `coupes=COUPES_ISO` |
| `iso_so_nuit` | Isométrique sud-ouest, de nuit | idem | idem | `ortho=6.0` | `coupes=COUPES_ISO, nuit=True` |
| `iso_no` | Isométrique nord-ouest | (-400, -470, 700) | (220, 140, 60) | `ortho=6.0` | `coupes=COUPES_ISO_NO, porte="fermee"` |
| `entree` | Depuis l'entrée | (268, 236, DEBOUT) | (105, 40, DEBOUT) | `focale=18, yeux=DEBOUT` | `decentrement=-0.12` |
| `fenetre` | Depuis la fenêtre | (12, 105, DEBOUT) | (330, 140, DEBOUT) | `focale=18, yeux=DEBOUT` | `decentrement=-0.12` |
| `banquette` | Assis sur la banquette | (28, 217, ASSIS) | (320, 150, ASSIS) | `focale=20, yeux=ASSIS` | `decentrement=0.02` |
| `dos_cellier` | Dos à la porte du cellier | (312, (BAIE_Y0 + BAIE_Y1) / 2, DEBOUT) | (40, 215, DEBOUT) | `focale=18, yeux=DEBOUT` | `decentrement=-0.15, porte="fermee"` |
| `cellier` | Entrée du cellier | (336, 72, DEBOUT) | (470, 60, DEBOUT) | `focale=14, yeux=DEBOUT` | `decentrement=-0.15, porte="fermee"` |

- [ ] **Step 1 : écrire les tests** (`tests/test_cuisine_piece.py`) :
  - `test_modele_identique_a_la_reference` : `donnees_variante(pieces.cuisine.modele)` sans préfixe, sérialisé comme à
    la tâche 1, égale `modele.json` clé pour clé.
  - `test_relais` : `ancien("modele") is importlib.import_module("pieces.cuisine.modele")`.
  - `test_anciens_generateurs_inchanges` : `ancien("plan").page(ancien("plan").lire_figees())` égale
    `cuisine-v13.html` ; `ancien("porte").page()` et `ancien("imprimable").page()` égalent leurs fichiers de référence.
  - `test_piece` : `ID`, `NOM`, `POSITION`, `SOL` (liste ci-dessus), `SURFACE == pytest.approx(aire(SOL) / 10000)`.
  - `test_contour_de_l_accueil` : `SOL` posé par `POSITION` redonne le contour `cuisine` de `APPART` sommet pour
    sommet (modèle : `tests/test_salon_piece.py::test_contour_de_l_accueil_inchange`).
  - `test_portes_tirees_du_modele` : `PORTES[0]["a"], PORTES[0]["b"] == (228, 306)` ;
    `PORTES[1]["a"], PORTES[1]["b"] == (modele.BAIE_Y0, modele.BAIE_Y1)`.
  - `test_cameras` : les huit lignes du tableau, valeur pour valeur ; `CAMERAS[i].reglages["coupes"]` égale le motif
    de `rendu.json` ; ids dans l'ordre `iso_so, iso_so_nuit, iso_no, entree, fenetre, banquette, dos_cellier,
    cellier`.
  - `test_donnees_stables` : deux processus (`PYTHONHASHSEED=1` et `2`, `subprocess`) écrivent la même sérialisation
    de `donnees_variante(piece, modele)` (modèle : `tests/test_salon_piece.py::test_empreinte_des_rendus`).

- [ ] **Step 2 : lancer, constater l'échec** (`ModuleNotFoundError: pieces.cuisine`).
- [ ] **Step 3 : implémenter** : `git mv`, relais, `piece.py`. Une constante que `donnees_variante` refuse (fonction,
  lambda) : la renommer `_X` dans le modèle et dans ses lecteurs (`plan.py`, `porte.py`, `imprimable.py`,
  `3d/v13/rendu.py`, `cad.py`) ; noter chaque renommage au rapport.
- [ ] **Step 4 : vérifier** : `… pytest -q tests/test_cuisine_piece.py tests/test_cuisine_reference.py` passe ;
  `python3 3d/v13/porte.py && git diff --exit-code cuisine-v13-porte-cellier.html` ;
  `python3 site.py && git status --short site/` : seule l'étiquette de la cuisine sur `site/index.html` change
  (surface), puis `git checkout -- site && git clean -fdq site` ; suite complète verte.
- [ ] **Step 5 : commit** — `git commit -m "Cuisine : modèle déplacé dans pieces/cuisine (relais dans 3d/v13), pièce et caméras"`

### Task 3 : Aides de dessin partagées

**Files:**
- Create: `pieces/cuisine/dessin.py`, `tests/test_cuisine_dessin.py`
- Modify: `3d/v13/plan.py` (importe ses aides de `pieces.cuisine.dessin`), `3d/v13/porte.py` et
  `3d/v13/imprimable.py` (`from pieces.cuisine.dessin import …` au lieu de `from plan import …` ; `ROOT` calculé dans
  chacun : `os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))`, racine mise sur `sys.path`)

**Interfaces:**
- Produces: `pieces.cuisine.dessin` : `f`, `rect`, `text`, `cote_h`, `cote_d`, `cote_v`, `aire`, `pts`, `virg`,
  `PLAN_CLS`, `volumes_plan(exclus=())`, `fiche_tango()`, `sources_tango()`, `CSS` (le CSS de l'ancienne page, que
  `porte.py` insère) — code repris de `plan.py` à l'identique, rien d'autre. `RACINE: Path` (racine du dépôt).

- [ ] **Step 1 : tests** (on compare des sorties, pas du code source) :
  - `test_aides_identiques` : pour des entrées tirées des dessins (`cote_h(0, 327, -40)`, `cote_d((10, 62),
    (322, 115))`, `cote_v(0, 252, -40)`, `pts(M.SOL_PARQUET)`, `virg(68.7) == "68,7"`, `virg(60) == "60"`), chaque
    chaîne rendue par `pieces.cuisine.dessin` figure telle quelle dans `dessins/plan.svg` ou `dessins/coupe-a.svg` ;
    `fiche_tango()` égale `tableaux.json["tango"]`.
  - `test_ancienne_page_inchangee` : `test_reference_a_jour` (tâche 1) passe toujours, `plan.py` important ses aides.
  - `test_porte_et_imprimable_inchanges` : `ancien("porte").page()` et `ancien("imprimable").page()` égalent leurs
    références.
  - `test_porte_n_importe_plus_plan` : `"from plan import"` absent de `3d/v13/porte.py` et de `3d/v13/imprimable.py`.
- [ ] **Step 2 : constater l'échec.**
- [ ] **Step 3 : implémenter** (déplacer les définitions, `plan.py` les réimporte : une seule copie du code).
- [ ] **Step 4 : vérifier** : tests de la tâche et de la tâche 1 ; `python3 3d/v13/porte.py && python3
  3d/v13/imprimable.py && git diff --exit-code cuisine-v13-porte-cellier.html cuisine-v13-imprimable.html` ;
  `test_reference_a_jour` passe toujours.
- [ ] **Step 5 : commit** — `git commit -m "Cuisine : aides SVG dans pieces/cuisine/dessin.py, porte.py et imprimable.py n'importent plus plan.py"`

### Task 4 : Chaîne de rendu FreeCAD puis Blender

**Files:**
- Move: `3d/v13/{rendu,cad,video,maquette}.py` → `pieces/cuisine/amenagement/` (`git mv`)
- Create: `pieces/cuisine/amenagement/__init__.py`, `pieces/cuisine/amenagement/document.py` (pour l'instant :
  `CACHE_RENDU` seul), `tests/test_cuisine_rendu.py`
- Copy (commit permis) : `cuisine-v13-3d/<ancien>.jpg` → `site/cuisine/amenagement/rendus/<nouveau>.jpg`, huit
  fichiers (Global Constraints, « Rendus »)
- Modify: `justfile` (recettes de la cuisine/aménagement ; les anciennes `v13*` restent jusqu'à la tâche 11 mais
  `v13-rendu`, `v13-video*`, `v13-maquette`, `v13-apercu` pointent vers les nouveaux chemins ou sont retirées)

**Interfaces:**
- Consumes: `pieces.cuisine.piece.CAMERAS`, `pieces.cuisine.modele`.
- Produces:
  - `CACHE_RENDU = CacheRendu(variantes={"": ("pieces.cuisine.piece", "pieces.cuisine.modele")},
    code=("pieces/cuisine/amenagement/rendu.py", "pieces/cuisine/amenagement/cad.py", "3d/rendu.py"))`.
  - Variables d'environnement : `CUISINE_SORTIE` (défaut `<racine>/cache/cuisine`), `CUISINE_APERCU=1` (800 × 600,
    sinon 1600 × 1200), `CUISINE_MAQUETTE` (défaut `<racine>/site/cuisine/amenagement/maquette-3d/modele.js`).
  - `cad.py` écrit `$CUISINE_SORTIE/cuisine-v13.FCStd` et `cuisine-v13.glb` ; `rendu.py -- <échantillons> [caméra …]`
    lit ce glb et écrit `$CUISINE_SORTIE/cuisine-<caméra>.png` pour chaque caméra de `piece.CAMERAS` demandée (toutes
    sans argument) ; les rendus temporaires (`zellige`, `fume`, `coussins`) restent appelables par leur nom.
  - Recettes : `cuisine-amenagement-cad` (freecadcmd), `cuisine-amenagement-rendu echantillons="64" *vues` (cache :
    `liste`, rien si vide ; sinon cad puis un seul Blender ; `sips` vers `site/cuisine/amenagement/rendus/<caméra>.jpg`
    ; `noter` ; `python3 site.py cuisine/amenagement`), `cuisine-amenagement-apercu *vues` (cad si le glb manque ou
    est plus ancien que `pieces/cuisine/modele.py`, puis 16 échantillons, `CUISINE_APERCU=1`,
    `CUISINE_SORTIE=$PWD/cache/apercu`, ni cache ni copie), `cuisine-amenagement-maquette`,
    `cuisine-amenagement-video-apercu`, `cuisine-amenagement-video echantillons="64"`. Toutes lancent
    `"${BLENDER:-/opt/homebrew/bin/blender}" -b --python-exit-code 1 --python …` (modèle : `entree-rendu`,
    `entree-apercu` ; sans variante : `nom="$c"`, `-` en ligne de commande).

Les sept points cassés (INV §13), chacun corrigé et testé :
1. `rendu.py` charge `3d/rendu.py` par son chemin (`spec_from_file_location("rendu_3d", RACINE/"3d/rendu.py")`,
   comme `pieces/entree/amenagement/rendu.py`) et importe `pieces.cuisine.modele`, `pieces.cuisine.piece` depuis
   `RACINE` (`parents[3]`) ; ses `VIEWS` sont construites depuis `piece.CAMERAS` (plus aucune coordonnée en dur).
2. Papier peint : `os.path.join(RACINE, M.PAPIER_PEINT["image"])`.
3. `cad.py` : `OUT = os.environ.get("CUISINE_SORTIE", <racine>/cache/cuisine)`, racine sur `sys.path`.
4. `video.py`, `maquette.py` chargent `rendu.py` depuis leur propre dossier (inchangé, mais vérifié après le
   déplacement).
5. `maquette.py` écrit `CUISINE_MAQUETTE` (plus `ROOT/cuisine-v13-maquette/modele.js`).
6. Aucun `/Applications/Blender.app` dans les recettes de la cuisine : `${BLENDER:-/opt/homebrew/bin/blender}`.
7. Cache : `CACHE_RENDU` ci-dessus (glb = entrée du rendu : `cad.py` et le modèle sont dans l'empreinte).

- [ ] **Step 1 : tests** (`tests/test_cuisine_rendu.py`, sans Blender ni FreeCAD) :
  - `test_cache_variantes` : `subprocess.run([python3, "-m", "commun.rendu_cache", "variantes",
    "cuisine/amenagement"])` sort `-`.
  - `test_toutes_les_vues_a_rendre` : `liste cuisine/amenagement - 64` sort les huit ids de `piece.CAMERAS` (aucune
    empreinte notée) ; environnement `BLENDER_REEL=/opt/homebrew/bin/blender`.
  - `test_chemins_de_la_chaine` : dans les quatre scripts, aucune occurrence de `/Applications/Blender.app`,
    `3d/sortie`, `dirname(dirname(HERE))`, `sys.path.insert(0, os.path.dirname(HERE))` ; `rendu.py` contient
    `piece.CAMERAS` et aucun `loc=(` ; `cad.py` contient `CUISINE_SORTIE`.
  - `test_recettes` : `just --dry-run cuisine-amenagement-apercu iso_so` (ou lecture du `justfile`) : aucune recette
    `cuisine-amenagement-*` ne cite `/Applications/`.
  - `test_rendus_repris` : `tests/fixtures/cuisine/rendus.json` (`{ancien nom: SHA-256}` des huit fichiers de
    `cuisine-v13-3d/`, écrit à cette étape) ; chaque fichier de `site/cuisine/amenagement/rendus/` a le hash de son
    ancien nom (`iso_so` ← `iso`, `iso_so_nuit` ← `iso_nuit`, les autres au même nom) ; le test tient après la
    bascule, quand `cuisine-v13-3d/` n'existe plus.
- [ ] **Step 2 : constater l'échec.**
- [ ] **Step 3 : implémenter** (déplacements, sept points, `document.py` avec `CACHE_RENDU`, recettes, copie des
  images, `rendus.json`).
- [ ] **Step 4 : vérifier la chaîne pour de vrai :**
  - `time BLENDER=… just cuisine-amenagement-cad` (freecadcmd réel) : `cache/cuisine/cuisine-v13.glb` existe ; durée
    notée au rapport (sous deux minutes attendu). S'il dépasse deux minutes, l'arrêter, le dire, garder le glb de
    `3d/sortie/cuisine-v13.glb` copié dans `cache/cuisine/` pour l'aperçu.
  - `BLENDER_REEL=/opt/homebrew/bin/blender BLENDER=REGISTRE/outils/blender-seul.sh just cuisine-amenagement-apercu
    iso_so` : `cache/apercu/cuisine-iso_so.png` existe, 800 × 600 (`sips -g pixelWidth -g pixelHeight`) ; ouvrir
    l'image (Read) et la comparer à l'œil à `site/cuisine/amenagement/rendus/iso_so.jpg` (même cadrage).
  - `maquette.py` : `CUISINE_MAQUETTE=$PWD/cache/maquette-essai.js BLENDER_REEL=… REGISTRE/outils/blender-seul.sh -b
    --python-exit-code 1 --python pieces/cuisine/amenagement/maquette.py` si la durée tient sous deux minutes (sinon
    le dire) ; le fichier commence comme l'actuel `modele.js` (même préfixe JS).
  - `video.py` : non lancé (plus de deux minutes) ; `python3 -m py_compile` passe.
  - `python3 -m commun.rendu_cache liste cuisine/amenagement - 64` sort toujours les huit vues :
    **aucune empreinte notée**.
  - `git status` : `cache/` absent (ignoré), rien sous `3d/sortie/` du dépôt principal n'a changé de date
    (`ls -l 3d/sortie/cuisine-v13.glb` avant, après).
- [ ] **Step 5 : commit**

```bash
git add pieces/cuisine/amenagement justfile site/cuisine/amenagement/rendus tests/test_cuisine_rendu.py tests/fixtures/cuisine/rendus.json
git commit -m "Cuisine : chaîne de rendu FreeCAD puis Blender dans pieces/cuisine/amenagement, branchée sur le cache ; rendus V13.26 repris, à rendre"
```

### Task 5 : Les sept dessins

**Files:**
- Create: `pieces/cuisine/amenagement/dessins.py`, `tests/test_cuisine_dessins.py`

**Interfaces:**
- Consumes: `pieces.cuisine.dessin` (aides), `pieces.cuisine.modele as M`.
- Produces (chaque fonction rend un `<svg>` complet, code repris de `plan.py`) :
  - `plan_svg(aria: str, zones: str = "") -> str` — `zones` (le HTML de `zones_svg`) inséré juste avant `</svg>` ;
    `role="group"` quand `zones` n'est pas vide (comme l'entrée).
  - `coupe_a(aria: str) -> str`, `coupe_b(aria: str) -> str`, `coupe_c(aria: str) -> str` (A et C portent la règle
    de `regle()`, les deux tailles dessinées), `coupe_elec_nord(aria: str) -> str`, `plan_elec_svg(aria: str) -> str`,
    `hauteur_pt_svg(aria: str) -> str`.
  - `COUPE_A, COUPE_B, COUPE_C = 90, 150, 315` ; `REGLE_LEGENDE: str` (ancien `TAILLE_LEG`, HTML des pastilles).
  - `CSS_DESSINS: str` : le CSS de `plan.py` (l.923-1093) sans les règles de page : retirer `:root` sombre et tout
    `@media (prefers-color-scheme…)`, `JetBrains Mono` et `monospace` (la déclaration de police seule ;
    `font-variant-numeric:tabular-nums` à la place pour `.dimt`, `.trit`, `.diagt`), `body:not(.explications) .cap`,
    `.kicker`, `.toc*`, `.vbar`, `.pbar`, `.impr`, `.tog*`, `.mono`. Valeurs figées : la règle
    `html[data-taille…] .regle[data-t…]` devient `.regle[data-t="175"]{display:inline}` ; `.fig:not(.transp)
    .trp-lbl{display:none}` est retirée (étiquettes visibles) ; `.transp .trp{…}` devient `.trp{…}` (transparence
    par défaut ; la tâche 12 la rend réglable). Portes : `.vt[data-etat…]` gardées telles quelles.
- Changements imposés par rapport à l'ancien dessin, et seulement ceux-là :
  1. point médian → virgule (« cellier, 1,44 m² », « 3,61 m³ brut, ≈ 3,4 net », « tableau noir, aimants »,
     « L2, LED ») ;
  2. `data-etat` figé : `ferme` pour `entree`, `mi` pour `cellier` (états par défaut de l'ancienne page) ;
  3. aria-label : celui que passe l'appelant ;
  4. zones du plan insérées.

- [ ] **Step 1 : tests :**
  - `test_dessins_identiques_a_la_reference` (paramétré sur les sept) : `_normaliser(dessin)` égale
    `_normaliser(référence)`, où `_normaliser` remplace « · » par « , » selon la liste ci-dessus, retire l'attribut
    `aria-label`, `role`, et les `<rect class="zone"…/>` (les `data-etat` de référence sont déjà `ferme` et `mi` :
    rien à normaliser) (modèle : `tests/test_entree.py::_sans_ajouts`).
  - `test_sans_point_median` : `"·"` absent des sept dessins et de `REGLE_LEGENDE`.
  - `test_portes_par_defaut` : dans le plan, le groupe `data-vt="entree"` a `data-etat="ferme"`, le groupe
    `data-vt="cellier"` a `data-etat="mi"`.
  - `test_regle_175_seule_visible` : `coupe_a` contient `data-t="175"` et `data-t="180"` ; `CSS_DESSINS` contient
    `.regle[data-t="175"]{display:inline}` et `.regle{display:none}`, aucune règle visant `html`.
  - `test_transparence` : `CSS_DESSINS` contient une règle `.trp{…}` avec le tireté de l'ancienne `.transp .trp`
    (`fill:none`, `stroke-dasharray:4 2`), aucune occurrence de `.transp`, et ne cache pas `.trp-lbl`.
  - `test_css_sans_chasse_fixe_ni_sombre` : ni `Mono`, ni `monospace`, ni `prefers-color-scheme` dans `CSS_DESSINS`.
- [ ] **Step 2 : constater l'échec.**
- [ ] **Step 3 : implémenter.**
- [ ] **Step 4 : vérifier** : `… pytest -q tests/test_cuisine_dessins.py`, suite complète.
- [ ] **Step 5 : commit** — `git commit -m "Cuisine : les sept dessins de l'aménagement, sans point médian, états par défaut de l'ancienne page"`

### Task 6 : Meubles touchables du plan

**Files:**
- Create: `pieces/cuisine/amenagement/zones.py`, `tests/test_cuisine_zones.py`

**Interfaces:**
- Consumes: `pieces.cuisine.modele` (`MEUBLES`, `ENVELOPPE`, `CONTENU`, `HAUTS_CONTENU`, `COLONNES_CONTENU`, …),
  `commun.blocs.Zone`, `cotes_meuble`.
- Produces:
  - `MEUBLES_PLAN: tuple[tuple[str, str, str, str, str], ...]` : `(id, titre, motif, coupe, iso)` ; `motif` : regex
    sur `Bloc.nom` de `M.MEUBLES + M.ENVELOPPE` (et `Cyl`) ; ids et lecture de INV §8 : `b1`…`b6`, `h1`…`h5`, `c1`,
    `c2`, `etageres`, `banquette`, `table`, `chaise`, `etagere-banquette`, `rayonnage-nord`, `entretien`, `balais`,
    `seau`, `aspirateur`, `porte-cellier`, `porte-entree`, `tableau-noir` ; coupe `A`, `B` ou `C`, iso `so` ou `no`.
    Titres : nom du meuble avec son étiquette du modèle (« B1, tiroirs » si `Bloc.etiq`), jamais un nombre en dur.
  - `emprise(motif: str) -> dict` : `x0, x1, y0, y1, z0, z1` = union des blocs dont le nom correspond.
  - `zones(textes: Mapping[str, str]) -> list[Zone]` : une `Zone(id, titre, (x0, y0, x1, y1), cotes_meuble(e),
    textes.get(id, "") + <ligne de CONTENU du meuble, s'il en a une>, coupe, iso)` par ligne de `MEUBLES_PLAN`.
- [ ] **Step 1 : tests :**
  - `test_ids_stables` : ids uniques, conformes à `^[a-z][a-z0-9-]*$`, aucun n'est un nombre, ni `""` ni `"elec"`.
  - `test_zone_confrontee_a_son_meuble` (paramétré sur chaque id) : le motif trouve au moins un bloc ; l'emprise de la
    zone égale l'union de ces blocs ; `cotes` égale `cotes_meuble` de cette union (modèle :
    `tests/test_entree.py::test_zone_confrontee_a_son_meuble`).
  - `test_zone_suit_son_meuble` : `monkeypatch` d'un bord d'un bloc de `b3` → l'emprise de `b3` suit.
  - `test_contenu_dans_la_fiche` : chaque ligne de `M.CONTENU` dont le meuble a une zone se retrouve (texte échappé)
    dans le `texte` de cette zone ; aucune ligne de `CONTENU` n'est perdue (celles sans zone sont listées par le test
    et vont à l'Explication, tâche 8).
  - `test_cotes_sans_nombre_en_dur` : `zones.py` ne contient aucun littéral numérique dans un titre ou un texte
    (relecture : grep de `\d` dans les chaînes de `MEUBLES_PLAN`).
- [ ] **Step 2 : constater l'échec.** — [ ] **Step 3 : implémenter.** — [ ] **Step 4 : vérifier.**
- [ ] **Step 5 : commit** — `git commit -m "Cuisine : meubles touchables du plan, ids stables, emprise et cotes tirées du modèle"`

### Task 7 : Légende du plan répartie

La légende de 8 439 caractères (PL l.1312) est un f-string calculé depuis le modèle. Elle est réécrite en une suite
ordonnée de morceaux dont la concaténation redonne la légende d'origine.

**Files:**
- Create: `pieces/cuisine/amenagement/legende.py`, `tests/test_cuisine_legende.py`

**Interfaces:**
- Consumes: `pieces.cuisine.modele as M`, `pieces.cuisine.dessin.f`, `texte_cellier` (repris de `plan.py` ici).
- Produces:
  - `@dataclass(frozen=True) class Morceau: ou: str; titre: str; html: str; meuble: str = ""` — `ou` vaut
    `"legende"` (fiche du plan) ou `"carte"` ; `titre` : titre de la carte (`""` pour la légende) ; `meuble` : id de
    `zones.MEUBLES_PLAN` ou `""`.
  - `morceaux() -> list[Morceau]` : dans l'ordre de la légende d'origine, découpée aux `<b>…</b>` (« Sols »,
    « Mur nord », « Induction », « évier », « Mur est », « Porte d'entrée », « tableau noir », « Équipements »,
    « Triangle d'activité », « Passage », « Réseaux », « LV », « Cellier », « Coin repas », « chaise », « bas de mur »,
    « Suspension », « Places », « Sous la banquette », « Au-dessus », « Ouvertures », « Meubles hauts »…) ; la phrase
    « Échelle… », la pièce vide et les sols, les cloisons déposées : `ou="legende"` ; le reste en cartes, titre tiré
    du mot en gras, `meuble` quand le morceau ne parle que d'un meuble.
  - `legende_html() -> str` (les morceaux `legende`, chacun dans un `<p>`) ; `cartes() -> list[Carte]` (morceaux
    `carte` consécutifs de même titre réunis, `Carte(titre, html, meuble)`) ; `textes_par_meuble() -> dict[str, str]`
    (pour `zones.zones`).
- [ ] **Step 1 : tests :**
  - `test_rien_ne_se_perd` : `_texte(" ".join(m.html for m in morceaux()))` égale
    `_texte(legendes["plan"]).replace(" · ", ", ")`, `_texte` = balises retirées, entités décodées, blancs réduits à
    une espace (la confrontation demandée par la commande : la légende d'origine contre sa répartition).
  - `test_balises_conservees` : les `<b>…</b>` de la légende d'origine se retrouvent tous, dans le même ordre, dans les
    morceaux concaténés.
  - `test_chaque_morceau_visible_sans_js` : chaque `html` de morceau `carte` figure dans `principes(cartes())` ;
    chaque morceau `legende` dans `legende_html()`.
  - `test_meubles_connus` : chaque `meuble` non vide est un id de `zones.MEUBLES_PLAN` ; au moins un morceau par
    meuble des rangées nord et est (`b1`…`b6`, `h1`, `c1`, `c2`).
  - `test_sans_point_median`.
- [ ] **Step 2 : constater l'échec.** — [ ] **Step 3 : implémenter.** — [ ] **Step 4 : vérifier.**
- [ ] **Step 5 : commit** — `git commit -m "Cuisine : légende du plan répartie en légende et cartes de principe, confrontée à l'originale"`

### Task 8 : Explication

**Files:**
- Create: `pieces/cuisine/amenagement/explication.py`, `tests/test_cuisine_explication.py`

**Interfaces:**
- Consumes: `commun.blocs` (`tete`, `principes`, `materiaux`, `note_source`, `figure_rendu`, `rendu`), `legende.cartes()`,
  `dessins.hauteur_pt_svg`, `pieces.cuisine.dessin.fiche_tango`, `sources_tango`, `RENDUS_SITE` (passé en argument).
- Produces: `explication(rendus: Path, depuis: str) -> str` (HTML de la vue, `depuis` =
  `"cuisine/amenagement/"` pour rebaser les liens) ; `LIENS: tuple[tuple[str, str], ...]` =
  `(("maquette-3d.html", "Maquette 3D"), ("imprimable.html", "Version imprimable"),
  (<adresse de la page porte du cellier vue de depuis>, "Porte du cellier"))`.
- Contenu, dans cet ordre (lignes 7, 8, 16-20, 26-28, 31, 34-36, 42-47 du tableau) :
  1. `tete(<pitch d'origine>, LIENS, figure_rendu(rendu(rendus, "", "iso_so"), <alt iso_so>))` ;
  2. `principes(legende.cartes())` ;
  3. `<h2>Hauteur du plan de travail (étude)</h2>` : remarque (légende 118), figure du dessin (alt : légende 584),
     tableau (dans `<div class="defile">`), texte et sources de `section_hauteur_pt()` ;
  4. `<h2>Porte du cellier, Mantion Tango</h2>` : lien « Plans détaillés », fiche, texte, sources ;
  5. `<h2>Électricité</h2>` : `<h3>Quel interrupteur allume quoi</h3>` + tableau + remarque 576, `<h3>Points</h3>`,
     `<h3>Circuits proposés</h3>`, remarque NF C (950) ;
  6. `<h2>Rendus</h2>` : remarque de méthode (240) ;
  7. `materiaux(lignes)` : 16 lignes `(élément, échantillon + <b>matériau</b><br>précision)`, l'image du parquet en
     `../../images/cuisine-sol-reference.png` (relatif à `depuis`), puis remarque 166 ;
  8. `<h2>Contenu des rangements</h2>` : tableau 27 lignes + remarque 467 ;
  9. `<h2>Capacité : V11.34 → V13.30 et proposition 9 A</h2>` (titre d'origine, médian remplacé) : tableau 17 lignes +
     remarque 740 ;
  10. `note_source("Repère : x vers l'est depuis le mur ouest, y vers le sud depuis le mur nord, z depuis le sol fini,
      en cm. Dimensions : pieces/cuisine/modele.py.")`.
  Textes et tableaux : repris des fonctions de `plan.py` (`section_hauteur_pt`, `section_tango`, `tables_elec`,
  `table_materiaux`, `table_contenu`, `section_capacite`, `lignes_avant_apres`, `details_capacite`), code déplacé ici,
  avec : point médian → virgule ; classe `mono` retirée ; `p.cap` → `<p class="remarque">` ; aucun `h1`.
- [ ] **Step 1 : tests :**
  - `test_tableaux_repris` (paramétré sur les 8 tableaux hors changements) : le texte de chaque tableau de
    `tableaux.json`, normalisé (`_texte`, médian → virgule), figure dans le texte de l'Explication.
  - `test_legendes_reprises` : les légendes `hauteur-pt-etude`, `interrupteurs`, `nfc`, `rendus-methode`,
    `materiaux`, `contenu`, `capacite`, normalisées, figurent dans le texte ; `hauteur-pt` est l'aria-label du dessin.
  - `test_tableaux_defilent` : chaque `<table` est précédé de `<div class="defile">`.
  - `test_liens_locaux_existent` : pour chaque `src`/`href` local de l'Explication, résolu depuis
    `site/cuisine/amenagement/`, le fichier existe après `python3 site.py` (ou sa source à la racine : `images/…`,
    `cuisine-v13-porte-cellier.html`) ; `maquette-3d.html` et `imprimable.html` sont exclus jusqu'à la tâche 10.
  - `test_sans_point_median_ni_mono` : ni « · », ni `class="mono"`, ni `<h1`.
  - `test_aucune_case_ni_texte_interdit` : ni `type="checkbox"`, ni « Copier la liste », « À venir », « Lecture du
    plan », « Lecture de la coupe ».
- [ ] **Step 2 : constater l'échec.** — [ ] **Step 3 : implémenter.** — [ ] **Step 4 : vérifier.**
- [ ] **Step 5 : commit** — `git commit -m "Cuisine : vue Explication (hauteur du plan, porte Tango, électricité, matériaux, rangements, capacité)"`

### Task 9 : Document et vues

**Files:**
- Create: `pieces/cuisine/amenagement/vues.py`, `tests/test_cuisine_document.py`
- Modify: `pieces/cuisine/amenagement/document.py`

**Interfaces:**
- Consumes: tâches 2 à 8.
- Produces:
  - `vues.RENDUS_SITE = parents[3] / "site/cuisine/amenagement/rendus"` ; `vues.LIEU = Lieu(piece.SOL_ET_CELLIER,
    piece.PORTES, "Position dans la cuisine")` ; `vues.vues(variante: str) -> dict[str, Vue]` (`variante == ""`).
  - Plan : `vue_plan(dessins.plan_svg(aria, zones_svg(zs)), zs, legende.legende_html())` (aria : celui de
    l'ancien dessin, médian remplacé) avec `zs = zones.zones(legende.textes_par_meuble())`, puis
    `Element(k="elec", nom="Électricité", titre="Plan électrique", scene=dessins.plan_elec_svg(<légende 566 en
    texte>))` ajouté à `elements`.
  - Coupes : `vue_coupes([Coupe("A", "A mur nord", "Coupe A-A : mur nord", coupe_a(<légende 856>), trait_A),
    Coupe("B", "B mur sud", "Coupe B-B : mur sud", …), Coupe("C", "C mur est", "Coupe C-C : mur est", …),
    Coupe("elec", "Électricité, mur nord", "Élévation du mur nord : électricité", coupe_elec_nord(<légende 211>),
    trait_A)], LIEU)` ; traits : A et `elec` horizontaux à `y = COUPE_A`, B à `y = COUPE_B`, C vertical à
    `x = COUPE_C`, bornés par l'étendue de `SOL_ET_CELLIER` ; `fiche` des éléments A et C = `REGLE_LEGENDE`.
  - Iso : `vue_iso(RENDUS_SITE, "", LIEU, points_iso(<enveloppe de SOL_ET_CELLIER>), alts)` puis
    `Element(k="so-nuit", nom="SO nuit", titre="Vue iso SO, de nuit", scene=figure_rendu(rendu(…, "iso_so_nuit"),
    alt))` ajouté, et `fiche` refaite par `commun.blocs.fiche_position(LIEU, cones=…)` avec un cône `so-nuit` au point
    du coin `so`.
  - Caméra : `vue_camera(RENDUS_SITE, "", LIEU, [entree, fenetre, banquette, dos_cellier, cellier], alts)`.
  - `alts` : `{clé: f"{titre}, {légende} (rendu {version})"}` depuis `M.RENDUS` et `M.RENDUS_VERSION`, médian
    remplacé (`iso` → `iso_so`, `iso_nuit` → `iso_so_nuit`).
  - Explication : `vue_lecture("explication", explication.explication(RENDUS_SITE, "cuisine/amenagement/"))`.
  - `document.construire_document() -> Document` : `Document(piece="cuisine", id="amenagement", nom="Aménagement",
    type="amenagement", variantes=(Variante("", "Principale", M.VERSION, changements, FIGEES),), generer=vues.vues,
    css=dessins.CSS_DESSINS)` ; `changements` : `Changement(version, date, texte)` pour chaque ligne de
    `M.CHANGEMENTS`, texte avec médian → virgule et lien `#hauteur-du-plan-de-travail-etude` → `./#explication` ;
    `FIGEES` (Global Constraints). Pas de `DOCUMENT` (tâche 11).
- [ ] **Step 1 : tests :**
  - `test_vues_et_elements` : clés `plan, coupes, iso, camera, explication` ; `k` du Plan `["", "elec"]`, des Coupes
    `["A", "B", "C", "elec"]`, de l'Iso `["no", "ne", "so", "se", "so-nuit"]` avec `ne`, `se` inactifs, de la Caméra
    `["entree", "fenetre", "banquette", "dos_cellier", "cellier"]` ; `commun.modele.verifier(doc, vues)` passe.
  - `test_ids_de_zones_distincts_des_elements` : aucun id de zone parmi les `k` du Plan.
  - `test_alt_est_la_legende` : aria-label de chaque coupe, du plan électrique et de l'élévation = texte de sa légende
    de référence (médian remplacé) ; alt de chaque rendu contient le texte de sa légende de référence.
  - `test_changements` : 90 changements, premier `V13.30`, même ordre et mêmes versions que
    `tableaux.json["changements"]` ; aucun « · » ; aucun lien `#hauteur-du-plan-de-travail-etude`.
  - `test_figees` : `variantes[0].figees` égale la constante ; chaque chemin existe sous `archive/`.
  - `test_journal_compte` : `commun.journal` sur un site où la cuisine est ce Document donne 90 entrées
    « Cuisine › Aménagement » (même nombre qu'avant : 90 dans `site/journal.html` sur la base).
  - `test_dessins_styles` (paramétré sur `plan`, `coupes`, `explication`) : chaque classe d'un élément a une règle
    dans `css_dessins(doc.css, _dessins(vues), ".d-cuisine")` ou `site.css` (modèle :
    `tests/test_entree.py::test_entree_dessins_styles`).
  - `test_rendus_existants` : les huit `rendu(RENDUS_SITE, "", clé).existe`.
  - `test_page_construite` : `construire(Site((Piece("cuisine", "Cuisine", (doc,)),)), (), tmp, tmp/"site")` (racine
    réduite, modèle `tests/test_construction.py`) écrit `cuisine/amenagement/index.html` et `historique.html` ; la
    page contient « Touchez un meuble pour afficher sa fiche. », aucun `type="checkbox"`, aucun « · », pas de bouton
    « Comparer » visible (une seule variante) ; `historique.html` cite `archive/cuisine-v11.49.html` et
    `archive/cuisine-v12.7.html`.
  - `test_tableau_de_contenu` : pour chacune des 22 légendes et des 9 tableaux de référence, sa destination (colonne
    « Devient ») : texte dans la vue nommée, ou aria/alt de l'élément nommé, ou (changements) dans l'historique.
- [ ] **Step 2 : constater l'échec.** — [ ] **Step 3 : implémenter.** — [ ] **Step 4 : vérifier** (suite complète ;
  `python3 site.py` passe et ne change rien sous `site/entree/`).
- [ ] **Step 5 : commit** — `git commit -m "Cuisine : document et vues (plan, électricité, coupes, iso jour et nuit, caméras, explication), 90 changements"`

### Task 10 : Pages annexes (imprimable, maquette 3D)

**Files:**
- Modify: `commun/modele.py` (ajout), `commun/construction.py` (ajout), `tests/test_construction.py` (ajout)
- Move: `3d/v13/imprimable.py` → `pieces/cuisine/amenagement/imprimable.py`
- Create: `pieces/cuisine/amenagement/maquette-3d.html` (copie de `cuisine-v13-maquette.html`, liens rebasés),
  `site/cuisine/amenagement/maquette-3d/modele.js` (copie de `cuisine-v13-maquette/modele.js`, commit permis),
  `tests/test_cuisine_annexes.py`
- Modify: `pieces/cuisine/amenagement/document.py` (`annexes=`), `explication.py` (liens maintenant vérifiés)

**Interfaces:**
- Produces:
  - `commun.modele.Annexe` : `@dataclass(frozen=True) class Annexe: nom: str; ecrire: Callable[[str], str]` — page
    écrite à `<dossier du document>/<nom>`, `ecrire(depuis)` reçoit son chemin sous `site/`
    (`"cuisine/amenagement/imprimable.html"`) et rend la page complète.
  - `Document.annexes: tuple[Annexe, ...] = ()` (champ ajouté en dernier, défaut vide : aucune page existante ne
    change) ; `construire()` écrit chaque annexe après les variantes du document.
  - `imprimable.page(depuis: str = "cuisine/amenagement/imprimable.html") -> str` : la page d'origine, avec
    `favicon.svg` et `apple-touch-icon.png` → `relatif(<fichier>, depuis)`, lien retour `cuisine-v13.html` →
    `relatif("cuisine/amenagement/", depuis)`, point médian → virgule.
  - `maquette(depuis: str) -> str` (dans `document.py` ou `vues.py`) : lit `maquette-3d.html`, rebase `favicon.svg`,
    `apple-touch-icon.png`, `cuisine-v13.html` → `./`, `cuisine-v13-maquette/modele.js` → `maquette-3d/modele.js`,
    médian → virgule ; rien d'autre (three.js 0.170.0 de jsdelivr gardé).
- [ ] **Step 1 : tests :**
  - `tests/test_construction.py::test_annexe_ecrite` : document d'essai avec `Annexe("annexe.html", lambda d:
    f"<p>{d}</p>")` → `site/essai/amenagement/annexe.html` contient `essai/amenagement/annexe.html` ;
    `test_sans_annexe_rien_de_neuf` : un document sans annexe écrit exactement les mêmes fichiers qu'avant.
  - `test_imprimable_identique_hors_liens` : `imprimable.page()` égale `imprimable.html` de référence après les seuls
    remplacements ci-dessus.
  - `test_maquette_identique_hors_liens` : `maquette(...)` égale `tests/fixtures/cuisine/maquette.html` (tâche 1)
    après les seuls remplacements ci-dessus.
  - `test_annexes_liens_locaux` : chaque `src`/`href` local des deux annexes, résolu depuis leur adresse sous `site/`,
    existe après `python3 site.py` (`modele.js` compris).
  - `test_modele_js_repris` : même SHA-256 que `cuisine-v13-maquette/modele.js`.
- [ ] **Step 2 : constater l'échec.** — [ ] **Step 3 : implémenter.**
- [ ] **Step 4 : vérifier** : suite complète ; `python3 site.py && git status --short site/entree` vide ; puis
  `git checkout -- site && git clean -fdq site` (garder `site/cuisine/amenagement/maquette-3d/modele.js`, commité).
- [ ] **Step 5 : commit** — `git commit -m "Socle : pages annexes d'un document (Annexe) ; cuisine : imprimable et maquette 3D à côté du document"`
  (rapport : fichiers communs touchés `commun/modele.py`, `commun/construction.py`, `tests/test_construction.py`,
  raison « pages annexes »).

### Task 11 : Bascule

**Files:**
- Modify: `site.py` (la `Passerelle` de `cuisine/amenagement` devient `cuisine_amenagement.DOCUMENT` ; trois
  `Redirection`), `pieces/cuisine/amenagement/document.py` (`DOCUMENT` par `__getattr__`, comme l'entrée), `justfile`,
  `3d/v13/porte.py` (deux liens), `tests/test_construction.py` (seulement si un test cite l'ancienne page de la
  cuisine comme passerelle)
- Delete (`git rm`): `cuisine-v13.html`, `cuisine-v13-imprimable.html`, `cuisine-v13-maquette.html`,
  `cuisine-v13-maquette/modele.js`, `3d/v13/plan.py`, `cuisine-v13-3d/` (8 jpg) ; sous `site/`, seulement les anciens
  dossiers d'images devenus orphelins (consignes, « Interdits » (b)) : `site/cuisine-v13-3d/` (8 jpg) et
  `site/cuisine-v13-maquette/modele.js` — **après** avoir vérifié par `grep -rl "cuisine-v13-3d/\|cuisine-v13-maquette/"
  *.html archive/ site/` que plus aucune page restante ne les cite. `site/cuisine-v13*.html` ne sont pas touchées à la
  main : `site.py` y écrit les redirections et le contrôleur reconstruit `site/` après la fusion.
- Create: `tests/navigateur/cuisine-amenagement.js`, `tests/test_cuisine_bascule.py`

**Interfaces:**
- Produces, dans `site.py` :

```python
ANCRES_CUISINE = {"plan": "plan", "br": "plan", "hauteur-du-plan-de-travail-etude": "explication",
                  "porte-du-cellier-mantion-tango": "explication", "electricite": "plan?k=elec",
                  "elevation-du-mur-nord-electricite": "coupes?k=elec", "rendus-3d": "iso",
                  "materiaux": "explication", "contenu-des-rangements": "explication"}
MOTIFS_CUISINE = ((r"^coupe-([a-c])-", "coupes?k={1}"), (r"^capacite-", "explication"))
PAGES_CUISINE = {"changements": "cuisine/amenagement/historique.html",
                 **{a: "archive/cuisine-v11.49.html" for a in <ids du bloc V11.49 dans ancres.json, plus "V11.49">},
                 **{a: "archive/cuisine-v12.7.html" for a in <ids du bloc V12.7, plus "V12.7">}}
Redirection("cuisine-v13.html", "cuisine/amenagement/", ANCRES_CUISINE, MOTIFS_CUISINE, PAGES_CUISINE)
Redirection("cuisine-v13-imprimable.html", "cuisine/amenagement/imprimable.html")
Redirection("cuisine-v13-maquette.html", "cuisine/amenagement/maquette-3d.html")
```
  Les ids des blocs figés sont écrits en clair dans `site.py` (liste lue une fois dans `ancres.json`, pas d'import de
  `tests/`) ; `br-V11.49` et `br-V12.7` vont aussi à leur archive.
- `justfile` : retirer `v13`, `v13-rendu`, `v13-video-apercu`, `v13-video`, `v13-maquette`, `v13-apercu`,
  `v13-figer` ; ajouter `cuisine-amenagement` (`python3 site.py cuisine/amenagement`) et `v13-porte`
  (`python3 3d/v13/porte.py`).
- `porte.py` : `href="cuisine-v13.html"` → `href="cuisine/amenagement/"` (l.138) et
  `href="cuisine/amenagement/#explication"` (l.174), seuls changements.

- [ ] **Step 1 : tests Python** (`tests/test_cuisine_bascule.py`) :
  - `test_document_dans_site` : `site.SITE` contient `cuisine_amenagement.DOCUMENT` dans la pièce `cuisine`, la
    porte du cellier reste une `Passerelle` ; `tests/test_construction.py::test_documents_declares` passe.
  - `test_redirection_ancres` (paramétré) : pour chaque ancre de INV §12, le fragment ou la page attendue, en
    appliquant les tables comme `commun/redirections.SCRIPT` (pages, puis ancres exactes, puis motifs avec groupe en
    capitale) : `coupe-a-a-mur-nord` → `coupes?k=A`, `coupe-c-c-mur-est` → `coupes?k=C`, `capacite-v11-34-v13-30-et-
    proposition-9-a` → `explication`, `electricite` → `plan?k=elec`, `changements` → historique.
  - `test_redirection_ancres_figees` : chaque id des blocs V11.49 et V12.7 de `ancres.json`, plus `V11.49`, `V12.7`,
    `changements-V11.49`, `changements-V12.7`, mène à son archive ; chaque ancre de `ancres.json` du bloc courant a
    une traduction (sauf celles qui ouvrent le Plan par défaut, listées).
  - `test_redirection_ancre_inconnue` : `inconnue` → aucun fragment (vue par défaut).
  - `test_porte_liens_reecrits` : `porte.page()` égale `porte-cellier.html` de référence avec les deux seuls
    remplacements.
  - `test_anciens_fichiers_supprimes` : `cuisine-v13.html`, `3d/v13/plan.py`, `cuisine-v13-3d/` absents ; présents :
    `3d/v11/`, `3d/v12/`, `3d/cuisine_a.py`, `cuisine-plan.html`, `cuisine-couleurs.html`, `cuisine-3d/`,
    `3d/v13/porte.py`, `cuisine-v13-porte-cellier.html`.
- [ ] **Step 2 : constater l'échec, puis implémenter** (ordre : `DOCUMENT`, `site.py`, `justfile`, `porte.py`, puis
  les `git rm` après le `grep`).
- [ ] **Step 3 : construire et vérifier :** `python3 site.py` passe ; `just tests` passe ; `python3 3d/v13/porte.py
  && git diff --stat cuisine-v13-porte-cellier.html` : deux liens seulement ; `git status --short site/` ne montre
  que ce que la page explique : `site/cuisine/amenagement/**` (pages, `dessins.css`, historique, annexes),
  `site/cuisine-v13*.html` devenues redirections, `site/index.html` et `site/journal.html` (menu, surface),
  `site/cuisine-v13-3d/` supprimé ; rien sous `site/entree/`. Noter cette liste au rapport, puis remettre `site/`.
- [ ] **Step 4 : script navigateur** `tests/navigateur/cuisine-amenagement.js`, marque `@site reel` (modèle :
  `tests/navigateur/entree.js`, mêmes aides `preparer`, `sansPolices`, `attendre`) :
  - à 1440 × 900, 1100 × 800, 390 × 844 : chaque vue et chaque repère (`plan`, `plan?k=elec`, `coupes?k=A|B|C|elec`,
    `iso?k=no|so|so-nuit`, `camera?k=<cinq>`, `explication`) : aucune erreur de console ni réponse ≥ 400, images
    chargées (`naturalWidth > 0`), rien ne déborde (`scrollWidth <= innerWidth` à 390 px), « Position » marque
    l'élément affiché (`.mini [data-k].ici` = le `k`), onglets `ne`, `se` désactivés ;
  - Plan : toucher la zone `b3` ouvre sa fiche (titre, « Coupe A », « Iso »), la touche Entrée aussi ; `#plan?k=b3`
    ouvre la fiche sur le plan meublé ; `#plan?k=elec` montre le plan électrique sans fiche de meuble ;
  - pas de bouton « Comparer » visible, pas de « Personnaliser » (aucune option avant la tâche 12) ;
  - anciennes adresses : `/cuisine-v13.html` → `/cuisine/amenagement/#plan` (ou sans fragment), `#coupe-b-b-mur-sud`
    → `#coupes?k=B`, `#electricite` → `#plan?k=elec`, `#changements` → `historique.html`, `#V12.7` →
    `archive/cuisine-v12.7.html`, `/cuisine-v13-imprimable.html` → `imprimable.html`, `/cuisine-v13-maquette.html` →
    `maquette-3d.html` (la maquette charge `modele.js` sans 404 ; three.js depuis jsdelivr : laisser passer le réseau
    ou servir un module vide, au choix, et le dire) ;
  - sans JavaScript (`javaScriptEnabled: false`) : les cinq sections se lisent, les cartes de principe aussi ;
  - historique : versions figées V11.49 et V12.7, 90 lignes de changements.
  Lancer : `cd WT && PORT=8880 SESSION=refonte-cuisine-amenagement-1 tests/navigateur/lancer.sh
  tests/navigateur/cuisine-amenagement.js` → `"ok": true`. Faire aussi des captures des cinq vues à 1440 et 390 px et
  les regarder une à une (aucun élément noir par défaut de style, aucune étiquette coupée).
- [ ] **Step 5 : vérifier les sept scripts du socle** sur le vrai site (ports 8881-8887, sessions
  `refonte-cuisine-amenagement-2…8`) : `entree.js`, `redirections.js`, `navigation.js` et les autres de
  `tests/navigateur/` restent verts.
- [ ] **Step 6 : remettre `site/`** (`git checkout -- site && git clean -fdq site`, puis refaire les `git rm` de
  `site/cuisine-v13-3d/` et `site/cuisine-v13-maquette/`, seules suppressions commitées sous `site/`), `git status`
  propre hors ces deux dossiers.
- [ ] **Step 7 : commit**

```bash
git add -A site.py justfile pieces/cuisine 3d/v13/porte.py tests
git rm -r cuisine-v13.html cuisine-v13-imprimable.html cuisine-v13-maquette.html cuisine-v13-maquette cuisine-v13-3d 3d/v13/plan.py site/cuisine-v13-3d site/cuisine-v13-maquette
git commit -m "Cuisine, aménagement : bascule (document dans site.py, trois anciennes adresses redirigées, ancien générateur supprimé)"
```

### Task 12 : Options « choix » (Taille, Portes, transparence)

**N'a lieu que si `REGISTRE/socle/rapport-options.md` existe.**

- [ ] **Step 0 : condition.** `test -f /Users/nvi/code/work/personal/plan/.superpowers/sdd/2026-11-13-refonte-pages/socle/rapport-options.md`.
  Absent : ne rien fusionner, ne rien changer ; écrire au rapport `Ruling : options non faites, rapport-options.md
  absent — valeurs figées (1,75 m, entrée fermée, cellier mi-ouvert, coupe C en transparence) — coût : une tâche après la livraison du lot S4` ; fin.
- [ ] **Step 1 : `git merge refonte`** (conflits : garder les deux côtés dans `site.py`, `justfile`, `commun/` ;
  `commun/modele.py` : `Annexe` et l'apport du socle) ; suite de tests verte avant d'aller plus loin. Lire
  `rapport-options.md` en entier : il donne l'API exacte (`Option(type="choix", …)`, `Valeur`, `si(...)`,
  `data-si`, `rendue=False`). Les noms ci-dessous suivent `REGISTRE/socle/plan-options.md` ; si le rapport en diffère,
  le rapport gagne.

**Files:**
- Modify: `pieces/cuisine/amenagement/dessins.py`, `vues.py`, `document.py`, `tests/navigateur/cuisine-amenagement.js`
- Create: `tests/test_cuisine_options.py`

**Interfaces (déclarations) :**

| id | nom | valeurs (code : nom) | défaut | portée | marques dans les dessins |
|---|---|---|---|---|---|
| `taille` | Taille de la personne qui cuisine | `175` : 1,75 m ; `180` : 1,80 m ; `masquee` : masquée | `175` | « Visible sur les coupes A et C. » | `<g class="regle" data-t="175" data-si="taille:175">`, idem 180 ; masquée : aucune règle |
| `porte-entree` | Porte d'entrée | `fermee` : fermée ; `ouverte` : ouverte | `fermee` | « Visible sur le plan. » | un `<g data-si>` par état du groupe `.vt[data-vt="entree"]` |
| `porte-cellier` | Porte du cellier | `fermee` ; `mi-ouverte` ; `ouverte` | `mi-ouverte` | « Visible sur le plan. » | un `<g data-si>` par état du groupe `.vt[data-vt="cellier"]` |
| `transparence` | Porte du cellier sur la coupe C | `non` : opaque ; `oui` : en transparence | `oui` | « Visible sur la coupe C. » | porte dessinée deux fois (opaque `transparence:non`, tiretée `transparence:oui`), `.trp-lbl` marquées `transparence:oui` |

Aucune option n'a `filtre` ; les rendus ne changent pas (`rendue=False` si le socle l'exige pour les portes : les
rendus montrent la porte d'entrée fermée et la porte du cellier selon la caméra).

- [ ] **Step 2 : tests** (`tests/test_cuisine_options.py`) : `test_declarations` (quatre options, défauts ci-dessus,
  ids et codes conformes `^[a-z][a-z0-9-]*$`) ; `test_jetons_connus` (`commun.modele.verifier` du socle passe) ;
  `test_defaut_inchange` (avec l'état par défaut, le dessin visible égale celui de la tâche 5) ; `test_css_fige_retire`
  (`.regle[data-t="175"]{display:inline}` et la règle `.trp{…}` directe retirées de `CSS_DESSINS`, la visibilité vient des
  règles générées) ; `test_masquee` : la largeur de la coupe « masquée » — **hors modèle du socle** (changement de
  viewBox) : la coupe garde sa viewBox élargie, la règle est seulement cachée ; ruling à écrire.
- [ ] **Step 3 : implémenter**, aucun JS ni CSS propre à la page.
- [ ] **Step 4 : vérifier** : suite complète ; `python3 site.py && git status --short site/entree` vide ; script
  navigateur complété (« Personnaliser » : chaque valeur change le dessin, « Valeurs d'origine » revient, choix gardé
  au rechargement, `localStorage` indisponible : défauts) puis lancé sur `PORT=8889
  SESSION=refonte-cuisine-amenagement-9` → `"ok": true`.
- [ ] **Step 5 : commit** — `git commit -m "Cuisine : options Taille, Porte d'entrée, Porte du cellier et transparence dans Personnaliser"`

---

## Au client (à reporter dans le rapport final)

- Rendus V13.26 et V13.27 repris tels quels, sur un modèle V13.30 : « à rendre » (aucune empreinte notée).
- Texte alternatif du rendu du cellier : « rayonnage sud à droite », supprimé en V13.6 (erreur de fond gardée).
- Porte de l'entrée : 228 → 306 dans la cuisine (8 → 86 dans le couloir) contre 8 → 87 dans `pieces/entree/piece.py`.
- `JOUE_C2` vaut 115 ; son commentaire du modèle dit « y 110 ».
- Accueil : l'étiquette de la cuisine passe de « 325 × 252 » à sa surface calculée.
- Défauts de l'ancienne page gardés : porte du cellier mi-ouverte, coupe C en transparence.
- Annexes : polices d'origine (Archivo, JetBrains Mono) gardées ; points médians remplacés.
- Points médians remplacés partout ailleurs (étiquettes des dessins, alt, un changement).
