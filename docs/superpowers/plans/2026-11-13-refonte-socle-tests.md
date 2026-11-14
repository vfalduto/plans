# Socle de la migration, lot S0 : tests indépendants des pages réelles en passerelle

> Exécution : skill `superpowers:subagent-driven-development`. Branche `refonte-socle-cache`, worktree
> `/Users/nvi/code/work/personal/plan-wt/socle-cache` (ce lot y suit le lot S3, déjà commité). Spec :
> `docs/superpowers/specs/2026-11-13-refonte-site-design.md` (« Migration »). Consignes communes de la migration :
> `/Users/nvi/code/work/personal/plan/.superpowers/sdd/2026-11-13-refonte-pages/consignes.md` (« Bascule »).

## But

Huit pages vont basculer en parallèle, chacune sur sa branche : dans `site.py`, sa `Passerelle` devient un `Document`,
ses anciennes adresses deviennent des `Redirection`, et son ancienne page est supprimée de la racine. Plusieurs tests
d'aujourd'hui supposent l'état exact du site réel (liste des huit passerelles, deux redirections, `cuisine-v13.html`
présent). Chaque bascule casserait donc les mêmes tests et modifierait les mêmes lignes : huit conflits de fusion. Ce
lot rend ces tests vrais avant, pendant et après les bascules, sans perdre de couverture.

## Contraintes globales

- **Seul `tests/` change** (`tests/test_construction.py`, `tests/test_journal.py`, `tests/test_redirections.py`,
  `tests/outils.py` au besoin, un nouveau dossier `tests/fixtures/passerelle/` si des pages d'essai sont plus claires
  en fichiers qu'écrites dans `tmp_path`). Rien dans `commun/`, `pieces/`, `site.py`, le `justfile`, la racine.
  N'ouvre pas `tests/fixtures/essai/`, `tests/test_entree.py`, `tests/test_gabarit.py`, `tests/test_rendu_cache.py`
  ni `tests/navigateur/` en écriture : d'autres lots y travaillent.
- **Trois états du site réel, la suite verte dans chacun** : (1) aujourd'hui (huit passerelles, l'entrée migrée) ;
  (2) après la bascule d'une page quelconque ; (3) à la fin, sans aucune `Passerelle` ni ancienne page à la racine.
- **Aucune liste figée de l'état de la migration** : aucun test ne nomme une page réelle en passerelle
  (`cuisine-v13.html`, `chambre-amenagement.html`, `salon-v4.html`, etc.) ni ne compte les passerelles, les documents
  migrés ou les redirections de `site.py`. Les tests propres à l'entrée (déjà migrée) peuvent continuer à nommer
  l'entrée, mais en la cherchant (par son `ancienne` adresse, par sa pièce), jamais par son rang ni par un
  dépaquetage de longueur fixe.
- **Aucune perte de couverture** : chaque affirmation retirée a une affirmation qui la remplace, sur une page d'essai
  ou sous forme de propriété du site réel.
- **Style du dépôt** : français, 120 caractères par ligne, pas de point médian, commentaires qui disent le pourquoi.
  Commits petits, en français, avec la ligne `Co-Authored-By` habituelle. `site/` n'est jamais commité ni modifié à
  la main ; s'il est régénéré, `git checkout -- site && git clean -fdq site` avant de commiter.
- **Tests** : `uv run -q --no-project --with pytest pytest -q tests` (133 tests verts au départ sur cette branche).

### Task 1 : Tests du site sans liste figée des pages en passerelle

**Constat de départ** (à compléter par `grep -n "charger_site\|RACINE\|\.html" tests/*.py`) :

- `tests/test_construction.py`, `test_documents_declares` : liste en dur des huit pages en passerelle et « le seul
  `Document` est l'entrée ».
- `tests/test_construction.py`, `test_passerelle_garde_les_adresses`, `test_menu_identique`,
  `test_plan_appartement` : `cuisine-v13.html` et `chambre-amenagement.html` servent d'exemple de page en passerelle
  (plus de dix images citées, lien du menu, lien du plan de l'accueil).
- `tests/test_journal.py`, `test_pages_reelles` : lit `cuisine-v13.html` à la racine et exige au moins une page à
  section « Changements » à la racine.
- `tests/test_redirections.py`, `test_redirections_de_l_entree` : `principale, victor = …REDIRECTIONS` (échoue dès
  qu'une page ajoute une redirection) ; `test_motifs_de_site_py` : exige de chaque redirection qu'elle traduise une
  ancre de coupe (faux pour un meuble, qui n'a pas de coupes).
- La fixture `construit` de `tests/test_construction.py` construit le site réel (copie réduite de la racine) plus le
  document d'essai : elle reste, elle vaut pour tout état du site. `test_journal_complet` exige « plus de 100 »
  changements : vérifie que ce seuil ne dépend pas des pages en passerelle (le nombre de changements d'un document
  est le même avant et après sa bascule) et dis-le.

**À faire :**

1. **Mécanisme de passerelle et journal sur des pages d'essai.** Ce que les tests vérifiaient sur
   `cuisine-v13.html` et `chambre-amenagement.html` se vérifie sur un site d'essai qui porte au moins une
   `Passerelle` vers une page d'essai (avec des images citées, une section « Changements » au format des anciennes
   pages, un en-tête `class="kicker"` portant sa version) : la page et ses images sont recopiées à la même adresse,
   le menu et le plan de l'accueil mènent à la page de la passerelle, le journal lit ses changements et sa version.
   Pour le plan de l'accueil, la pièce de la passerelle d'essai doit être une pièce que `commun/appartement.py`
   sait placer : lis-le avant de choisir.
2. **`test_documents_declares` devient un test de propriétés du site réel**, vraies à chaque bascule :
   - l'ordre des pièces : `["cuisine", "sdb", "entree", "salon", "chambre"]` ;
   - chaque `Passerelle` désigne une page qui existe à la racine ;
   - chaque `Document` de `site.py` se construit : pour chaque variante, `doc.generer(v.id)` passe
     `commun.modele.verifier` (ou la fixture `construit` l'a écrit dans `site/`, sans lien mort) ;
   - aucune ancienne page d'un document migré ne reste à la racine sans redirection. Lecture retenue : toute page
     `*.html` de la racine est soit la page d'une `Passerelle`, soit l'`ancienne` adresse d'une `Redirection` de
     `site.py`, soit une page qui n'est pas un document (`index.html` et les pages annexes ou destinées aux archives
     présentes aujourd'hui : `cuisine-plan.html`, `cuisine-couleurs.html`, `cuisine-v13-imprimable.html`,
     `cuisine-v13-maquette.html`, `sdb-meuble-achats.html`). Cette dernière liste dit « permise si présente » : une
     page de la liste qui disparaît ne fait pas échouer le test, aucune bascule n'a donc à la modifier. Si tu trouves
     une propriété plus juste sans liste, prends-la et écris ton ruling.
   - chaque `Redirection` de `site.py` vise une adresse que le site construit (page d'un `Document` ou son
     historique), et ses motifs se compilent.
3. **Redirections** : les tests de l'entrée trouvent ses deux redirections par leur `ancienne` adresse ; le test des
   motifs de `site.py` ne suppose plus que chaque redirection a des coupes (la traduction d'une ancre de coupe se
   vérifie sur les redirections de l'entrée, déjà couvertes).
4. **`test_pages_reelles`** (journal) : la lecture des changements et de la version d'une ancienne page se vérifie
   sur la page d'essai ; la propriété « toute page de la racine qui a une section Changements est lisible » reste,
   sans exiger qu'il en existe une.

**Preuve demandée : bascules simulées.** Sans rien commiter de ces essais, modifie temporairement `site.py` et la
racine du worktree pour simuler, tour à tour : (a) la bascule de la cuisine (la `Passerelle` de
`cuisine/amenagement` remplacée par un `Document` d'essai placé à cette adresse, par exemple
`dataclasses.replace` du document de `tests/fixtures/essai/document.py`, une `Redirection("cuisine-v13.html",
"cuisine/amenagement/")` ajoutée, `cuisine-v13.html` supprimé de la racine) ; (b) celle de la chambre, de la même
façon ; (c) les huit à la fois (plus aucune `Passerelle`, les huit pages supprimées, huit redirections). Lance la
suite complète dans chaque état, copie la dernière ligne de sortie dans ton rapport, puis remets tout
(`git checkout -- . && git clean -fdq` hors fichiers ignorés ; `git status --short` vide). Lance aussi la suite
dans l'état (1) réel. Si un test d'un fichier que tu n'as pas le droit de modifier échoue dans un état simulé
(`tests/test_entree.py`, `tests/test_gabarit.py`, les scripts de `tests/navigateur/`), ne le corrige pas : nomme-le
dans ton rapport avec la raison.

**Dans le rapport**, un tableau « ce que chaque test vérifiait → ce qui le vérifie maintenant », une ligne par
affirmation déplacée ou réécrite, et les sorties des quatre états.
