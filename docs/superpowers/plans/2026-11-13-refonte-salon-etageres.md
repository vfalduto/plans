# Refonte du site, salon/etageres : plan de travail

> **Pour les agents qui exécutent ce plan :** utiliser superpowers:subagent-driven-development (recommandé) ou
> superpowers:executing-plans pour l'exécuter tâche par tâche. Les étapes se cochent (`- [ ]`).

**But :** migrer `salon-etageres.html` (V1.8, générée par `3d/salon/etageres.py`) vers le document de construction
`salon/etageres/`, à quatre variantes (`actuelle` à `salon/etageres/`, puis `rangs.html`, `decalee.html`,
`escalier.html`), généré depuis les données déjà en place dans `pieces/salon/etageres/`.

**Architecture :**
- **Données** (déjà fusionnées, à ne pas réécrire) : `pieces/salon/etageres/document.py` (montants, tablettes, les
  quatre `DISPOSITIONS`, bruts, matériaux, tenue, caméras, `RENDUS`, `CHANGEMENTS`), `volumes.py` (`tablettes`,
  `pieces_3d`, `pieces_detail`), et les modules communs au salon `pieces/salon/dessin.py` (`iso_svg`, `rect`, `text`,
  `cote_h`, `cote_v`, `f`), `meubles.py` (`cote`), `piece.py`.
- **Calculs** d'une disposition (débit, bandes, charges, achats, présentoir dérivé) : `calculs.py`, port de la partie
  calcul de `3d/salon/etageres.py`.
- **Dessins** : `dessins.py`, port des onze fonctions de dessin, identiques aux fichiers de référence
  `tests/fixtures/salon/etageres-*.svg` à la virgule près (« · » → « , »).
- **Vues** : `vues.py` (Plans, Découpe, Montage, Achats) et `explication.py`, sur les blocs de `commun.blocs` et
  `commun.blocs_construction`. Plans : six repères, cadrage commun aux quatre variantes, Mesurer en cm.
- **Bascule** : `site.py` passe de la `Passerelle` au `Document`, l'ancienne page devient une `Redirection`.

Modèle le plus proche, à lire avant chaque tâche : la page de l'enfilade, fusionnée dans `refonte` (358c024) :
`pieces/salon/enfilade/{chiffrage,dessins,vues,explication,document}.py`, `tests/test_salon_enfilade*.py`,
`tests/navigateur/salon-enfilade.js`. Le document d'essai à trois variantes avec comparaison :
`tests/fixtures/essai/meuble.py`. La dernière page d'aménagement : `pieces/chambre/`.

**Technologies :** Python 3.14 (bibliothèque standard), pytest par `just tests`, `playwright-cli` par
`tests/navigateur/lancer.sh`. Pas de Blender.

**Spécification :** `docs/superpowers/specs/2026-11-13-refonte-site-design.md` (fait autorité). Consignes de la
migration, qui font loi : `/Users/nvi/code/work/personal/plan/.superpowers/sdd/2026-11-13-refonte-pages/consignes.md`
(noté `REGISTRE/consignes.md`). Inventaire : `REGISTRE/salon-etageres/inventaire.md` (cité « inv. § N » ; `ET:N` =
ligne N de `3d/salon/etageres.py`). Mode d'emploi des blocs : `REGISTRE/socle/rapport.md` (et
`REGISTRE/socle/rapport-options.md` pour le lot S4).

## Global Constraints

Recopiées de la spec, des consignes et des contraintes globales du plan du socle
(`docs/superpowers/plans/2026-11-13-refonte-socle-entree.md`, l. 45-121). Elles lient chaque tâche.

- **Sources :** « Les dimensions se calculent depuis les modèles, jamais en dur dans les textes. » « Dimensions :
  calculées depuis le modèle, jamais écrites en dur dans un texte nouveau ni dans une fiche. Les textes repris tels
  quels de l'ancienne page gardent ce qu'ils avaient. » `site/` n'est jamais modifié à la main.
- **Rien ne se perd :** « Chaque section, tableau, dessin, image et note de l'ancienne page a sa place dans une vue, ou
  est retiré par une décision listée dans la spec (« Ce que le client a décidé », « À éviter »). Un retrait sans
  décision n'est pas permis : dans le doute, le contenu va dans l'Explication. »
- **Vues d'une construction :** Plans, Découpe, Montage, Achats, Explication ; s'ouvre sur Plans. « Une vue sans contenu
  reste un onglet grisé (« Pas encore rendu » ou « Sans objet »). Les rendus d'un meuble vont dans son Explication. »
- **Retirés par décision :** « cases à cocher ; « Copier la liste » ; « À venir » ; « Lecture du plan » et « Lecture
  de la coupe » ; textes de description sous les dessins et les rendus (ils deviennent le texte alternatif) ; sommaire
  et barres propres à l'ancienne page ; bouton d'une version figée dans la page. Le tableau des changements va dans
  l'historique et le journal, pas dans une vue. »
- **Style :** « pas de point médian (virgule à la place, y compris dans les étiquettes des dessins et les titres
  repris), pas de police à chasse fixe, pas d'étiquettes en capitales, pas de flèche ajoutée aux liens, pas de mode
  sombre, pas de motif décoratif. » Aucun « · » nulle part : ni dans les dessins (125 étiquettes), ni dans les textes,
  ni dans le CSS. Couleurs : papier `#EEF0EC`, navigation `#000000c7`, repère `#F2CF4A` ; les dessins n'utilisent que
  les jetons de `commun/site.css` ou des littéraux de l'ancienne page (`#26262A`, `#8E9399`, `#5E6369`, `#c2410c`,
  `#4d9a3a`, `#fff`) ; aucun `prefers-color-scheme`. Polices : Fira Sans et Fira Sans Condensed, chiffres tabulaires ;
  le CSS de la page ne nomme aucune police (une `font-family` ne vaut que `var(--…)`) ; pas de classe `mono`.
- **CSS des dessins :** « `Document.css` réunit le CSS de toutes les variantes ; un test vérifie que chaque classe d'un
  dessin a une règle (`dessins.css` ou `site.css`), pour chaque variante et chaque vue dessinée. » Ici les quatre
  variantes partagent un seul `dessins.CSS`, qui couvre les classes de toutes.
- **Variantes :** « chacune ne déclare que ce qui la distingue ; toutes partagent les murs, portes et caméras de
  `piece.py`. » Ici : ses tablettes et son idée (`DISPOSITIONS`) ; aucune version figée (`figees = ()`).
- **Journal :** « le nombre de changements du document est le même avant et après » : 9 avant (lignes
  « Salon › Étagères » de `site/journal.html`, lues dans la page), 9 après (`CHANGEMENTS` portés par Actuelle).
- **Erreurs de l'ancienne page :** une erreur d'affichage manifeste se corrige et se liste « Au client » ; une erreur de
  fond (rendus d'avant la V1.4, textes à valeurs écrites) se garde et se signale « Au client ».
- **Options :** aucune (« seulement ce que l'ancienne page offrait déjà comme réglage au lecteur » : le seul réglage,
  la disposition, est devenu les variantes).
- **Rendus :** « Reprends les images existantes telles quelles, sous `site/<piece>/<document>/rendus/` (nommage du
  socle). » « Ne note une empreinte dans le cache que pour une image réellement rendue par le script déplacé depuis le
  modèle courant. Sinon, laisse la vue « à rendre ». » Décision du contrôleur : `3d/salon/rendu_meubles.py` n'est
  déplacé par personne ; pas de `rendu.py`, pas de `CACHE_RENDU`, pas de recette de rendu pour cette page.
- **Interdits :** `git push`, toute écriture sur `main`, toute fusion dans `refonte`, tout réglage GitHub. « Modifier
  `site/` à la main. Commiter `site/` depuis une branche de travail, sauf : (a) les images de
  `site/<piece>/<document>/rendus/` […] ; (b) la suppression d'anciens dossiers d'images devenus orphelins. » Blender :
  jamais (cette page n'en lance pas). Jamais `playwright-cli close-all` ni `kill-all`, jamais la session `prod`, jamais
  les ports 8800 et 8811. Rien n'est supprimé ni modifié dans `3d/salon/` (décision du contrôleur : nettoyage commun
  après les trois pages du salon) ; les anciennes recettes `salon*` du `justfile` restent telles quelles ; les tests
  `tests/test_salon_*.py` qui comparent aux anciens générateurs restent.
- **Partagé :** « Dans `site.py` et le `justfile`, ne touche que les lignes de ta page. » « Un manque du socle se
  corrige dans `commun/` seulement s'il est nécessaire à ta page, par un ajout minimal, testé, qui ne change le rendu
  d'aucune page existante (`python3 site.py` ne doit modifier aucun fichier de `site/entree/`). » Ce plan ne touche
  **aucun** fichier de `commun/`, `tests/fixtures/essai/`, `tests/navigateur/*.js` (sauf `salon-etageres.js`),
  `pieces/salon/dessin.py`, `meubles.py`, `piece.py`, `pieces/salon/enfilade/`, `pieces/salon/amenagement/`. Dans
  `pieces/salon/etageres/document.py`, seuls `_document()` et `__getattr__` s'ajoutent ; aucun nom existant ne change
  (`MONTANTS` est lu par l'enfilade). `.gitignore` : une ligne (`/salon-etageres.html`), comme l'enfilade.
  `tests/test_construction.py` n'est pas modifié (sa garde des redirections se compare aux documents migrés, sans
  liste figée : ne pas la remettre en liste).
- **Tests :** `just tests` (`uv run -q --no-project --with pytest pytest -q tests`), tous verts au départ et après
  chaque tâche. Un fichier seul : `uv run -q --no-project --with pytest pytest -q tests/test_salon_etageres_page.py`.
- **Navigateur :** `PORT=8840 SESSION=refonte-salon-etageres-1 tests/navigateur/lancer.sh <script>` (ports 8840-8849,
  sessions `refonte-salon-etageres-*`) ; ne fermer que ses propres sessions.
- **Git :** branche `refonte-salon-etageres` seulement, commits petits en français finissant par
  `Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>` ; avant chaque commit,
  `git checkout -- site && git clean -fdq site` sauf les rendus commités en tâche 4.

## Décisions prises pour ce plan

Options de l'inventaire § 11 adoptées (contrôleur) : présentoir en Explication ; Composition en tête de Montage ; une
ligne de renvoi aux rendus d'Actuelle pour les trois autres variantes ; historique porté par Actuelle (V1.8, neuf
changements), les trois autres en V1.8 sans changement ; l'ancienne page redirige toujours vers Actuelle ; titre long
« Étagères sur montants percés » en tête du chapô. Décisions ajoutées, réversibles (rulings détaillés dans
`REGISTRE/salon-etageres/plan-rapport.md`) :

1. **Page figée** : `tests/fixtures/salon/salon-etageres.html` = `git show refonte:salon-etageres.html` (égale à la
   sortie du générateur, inv. en-tête), seule référence des textes et des tableaux une fois la page racine supprimée.
2. **Pas de fichier par variante** : les quatre `Variante` se tirent de `DISPOSITIONS`, qui ne déclare déjà que ce qui
   distingue une disposition (`tablettes`, `idee`).
3. **Mesurer en cm** : les dessins de Plans sont à l'échelle × k de l'ancienne page (élévation 2,4, dessus 2,6, profil
   9, travée 3) ; la scène les reçoit enveloppés par `en_cm(svg, k)` (viewBox divisé par k, contenu dans
   `<g transform="scale(1/k)">`), comme l'enfilade : même image, et Mesurer lit des cm. Vue iso et détail iso :
   `mesure=False` (axonométrie).
4. **Cadrage commun** : les dessins `iso` et `dessus` de chaque variante reçoivent le même viewBox, union des quatre
   (calculée sur les dessins des quatre dispositions), car la comparaison recopie le viewBox de la base sur la variante
   comparée (`commun/site.js`, `lier`) ; les quatre autres repères l'ont déjà identique.
5. **Achats par le bloc du socle**, une section par magasin dans l'ordre d'apparition (Weldom Marseille Saint-Barnabé,
   Castorama), au centime (`arrondi=False`) : poste, prix unitaire, source (lien vers la fiche produit) et statut
   (« prix relevé » ou « prix estimé ») passent dans la note de chaque ligne, avec la note d'origine. Le libellé
   « Total TTC (disposition X) » devient le sous-titre « Disposition X » et le total du bloc.
6. **Textes repris** : les f-strings de l'ancienne page sont portées telles quelles (valeurs tirées du modèle, comme
   avant). Deux phrases seulement changent : « Cliquer une vignette (ou un bouton de la barre du haut) fait passer
   <b>toute la page</b> dans cette disposition : » devient « Choisir une disposition change toute la page : » ; la note
   finale devient une remarque sans chemin de l'ancien générateur (tâche 4).
7. **Liens hors document** : le salon par `../../salon-v4.html` (passerelle aujourd'hui, redirection demain : jamais
   mort) ; la page Fixations par `../../archive/salon-bibliotheque-fixation.html`.
8. **`DOCUMENT` exposé à la bascule seulement** : `tests/test_construction.py::test_site_py_tient_documents_et_redirections`
   exige que tout `document.py` qui porte `DOCUMENT` soit dans `SITE`. Les tâches 1 à 5 testent `document._document()` ;
   `__getattr__("DOCUMENT")` arrive avec `site.py` en tâche 6.
9. **Dossier d'images** : après la bascule, `site/salon-meubles-3d/` n'est plus cité par aucune page (l'enfilade est
   migrée) : ses quatre images sont supprimées de `site/` (exception (b)). Le dossier racine `salon-meubles-3d/` reste :
   `3d/salon/rendu_meubles.py` (non déplacé) y écrit et les anciens générateurs le lisent.
10. **Titres des sections** : ceux de l'ancienne page (« Dispositions », « Présentoir », « Rendus 3D »,
    « Matériaux », « Tenue : poids et chute », « Débit et découpe », « Achats et prix », « Outils et montage »,
    « Composition ») ; deux nouveaux : « Le mécanisme » (paragraphes de « Le meuble ») et « À vérifier sur place »
    (« Points à valider », titre de la spec, obj. 2) ; les figures de la Découpe sous « Découpe et perçage ».

« Au client » (à reporter au rapport final) : rendus d'avant la V1.4 (sans rainure ni colonne avant remontée), repris
« à rendre » ; ligne du journal nommée « Étagères, Actuelle » ; achats regroupés par magasin ; virgules au lieu des
points médians ; « Points à valider » devenu « À vérifier sur place » ; rendu de détail sur M5 et détail iso sur M2
(inv. § 4) ; « bandes de 32 » et autres valeurs écrites des textes repris (inv. § 9).

## Review Focus

1. **Mesurer sur un dessin à l'échelle × k** : la distance affichée doit être en cm (deux axes de montants : 55), pas
   en unités du dessin (132). Test en tâche 3 (`test_mesure_en_cm`), vérification au navigateur en tâche 6.
2. **Comparer une variante plus haute que la base** (Escalier comparé depuis Actuelle, vues de dessus : 1028,4 contre
   716,4 de haut) : rien de la variante comparée ne doit être coupé. Test en tâche 3 (`test_cadrage_commun`).
3. **Un dessin hors de la scène** (Découpe, Explication : `.scene .dimt` du site ne s'y applique pas) : aucun texte
   noir par défaut ni en police à chasse fixe. Test en tâche 2 (`test_textes_ont_une_couleur`) et en tâche 5.
4. **Une ancienne adresse avec une ancre** (`#iso`, `#meuble`, `#changements`, inconnue, aucune) : la bonne vue ou
   l'historique, sinon Plans. Test en tâche 6 (`_traduire`), et au navigateur.
5. **Un lien relatif vers une page que rien ne génère** (vignettes vers `rangs.html…`, salon, archive Fixations) :
   seuls des liens permis. Test en tâche 5 (`test_liens`), plus la garde des liens morts de `tests/test_construction.py`
   après la bascule.

---

## Ancienne page → vues

Relu sur `salon-etageres.html` (V1.8, 450 lignes, `ET:1132-1211`) à la branche `refonte`. La page redirige vers
`salon/etageres/` (Actuelle). Tous les `h2` ont un identifiant explicite (`ET:801-1085`), `changements` est sur la
`section` (`ET:1206`), aucun `h3` n'a d'ancre (inv. § 10). « Varie » : un bloc par disposition dans l'ancienne page ;
chaque nouvelle variante n'en garde que le sien.

| Section de l'ancienne page | Ancre | Devient | Retiré, et décision qui le retire |
|---|---|---|---|
| Barre : « ← Plans » (`CO:79`) | | Menu de gauche, icône maison sur mobile | |
| Barre : « Disposition » et ses 4 boutons (`ET:1175-1177`) | | Choix de variante de la barre du haut (une page par disposition) et « Comparer » | Le bouton et son JS : « Une page par document et par variante » (spec, « Adresses ») |
| Barre : liens Salon, Étagères, Enfilade (`CO:77-79`) | | Menu de gauche (documents de la pièce) | Les liens dans la barre : « une navigation identique sur toutes les pages » (spec, obj. 1) |
| Sommaire repliable (`CO:36-72`) et `3d/ancres.js` | | Onglets des vues ; ancres traduites par la redirection | « sommaire et barres propres à l'ancienne page » (consignes) |
| Surtitre « Salon · Étagères · V1.8 » et `h1` (`ET:1178-1179`) | | Barre du haut : Salon › Étagères, variante, pastille V1.8 ; le `h1` « Étagères sur montants percés » en tête du chapô | Le surtitre en capitales à points médians : spec, « À éviter » |
| Chapô, un par disposition (`ET:1170-1174`) | | Explication : chapô de la variante ; chiffres clés calculés (formule, repères, étapes, total) | |
| Dispositions : texte d'ouverture (`ET:802`) | `dispositions` → `explication` | Explication, « Dispositions », dernière phrase réécrite (décision 6) | « Cliquer une vignette (ou un bouton de la barre du haut) » : le bouton n'existe plus |
| Dispositions : 4 vignettes (`ET:791-794`) | | Explication : 4 liens vers la page de chaque variante (`#explication` gardé), nom, formule, mini-élévation, idée ; la variante affichée en `aria-current` | La police à chasse fixe de la formule : « Style » |
| Dispositions : tableau comparatif, 9 colonnes (`ET:795-804`) | | Explication, même section | |
| « Deux longueurs seulement » (`ET:805-807`) | | Explication, même section | |
| « Règles de composition » et note (`ET:808-815`) | | Explication, même section | |
| Vue iso, une par disposition (`ET:818-823`) | `iso` → `plans?k=iso` | Plans, `k=iso`, cadrage commun (décision 4), sans Mesurer | La légende à l'écran : texte alternatif |
| Vue iso : détail d'une entaille (`ET:824-825`) | | Plans, `k=detail`, sans Mesurer | La légende à l'écran |
| Le meuble : élévation (`ET:840-841`) | `meuble` → `plans?k=elevation` | Plans, `k=elevation` (défaut), en cm ; fiche : formule des longueurs, liens Découpe et Montage | La légende à l'écran |
| Le meuble : vues de dessus (`ET:842-843`) | | Plans, `k=dessus`, en cm, cadrage commun | La légende à l'écran |
| Le meuble : « Composition » (`ET:844-845`) | | Montage, en tête : « Composition », 7 colonnes | |
| Le meuble : profil (`ET:851-852`) | | Plans, `k=profil`, en cm | La légende à l'écran |
| Le meuble : paragraphe de la rainure (`ET:853`) | | Explication, « Le mécanisme » | |
| Le meuble : travée de face (`ET:854-855`) | | Plans, `k=travee`, en cm | La légende à l'écran |
| Le meuble : paragraphe « de 5 en 5 » (`ET:856`) | | Explication, « Le mécanisme » | |
| Présentoir : textes, dessin, h3, listes, tableau, note (`ET:866-881`) | `presentoir` → `explication` | Explication, « Présentoir », le dessin en figure (texte alternatif = la légende) | La légende à l'écran |
| Rendus 3D : note et 2 images (`ET:828-831`) | `rendus` → `explication` | Explication d'Actuelle, « Rendus 3D » : les deux images (`rendus/actuelle-iso.jpg`, `actuelle-detail.jpg`) et la note ; les trois autres : une ligne qui renvoie à Actuelle | Les `figcaption` à l'écran (le texte reste en `alt`) |
| Matériaux : tableau 3 colonnes et note (`ET:884-889`) | `materiaux` → `explication` | Explication, « Matériaux » (bloc du socle : retenu, pourquoi, autres possibilités) et sa note | |
| Débit : liste des pièces (`ET:892-897`) | `debit` → `decoupe` | Découpe, « Débit et découpe », sous-titre calculé « Disposition X : N repères, M pièces à débiter. » | Les classes `mono` : « Style » |
| Débit : refente, débit des barres, perçage, entaille (`ET:898-916`) | | Découpe, « Découpe et perçage » : 4 figures titrées par les anciens `h3` | Les 4 légendes à l'écran : textes alternatifs |
| Tenue : intro, « Ce qui peut céder », note, 4 points (`ET:1005-1015`) | `charges` → `explication` | Explication, « Tenue : poids et chute » | |
| Tenue : « Fixation au mur », sources, note « de mémoire » (`ET:1016-1026`) | | Explication, même section ; le paragraphe de la disposition affichée seulement | |
| Achats : intro, tableau, total, transport, note (`ET:1035-1041`) | `achats` → `achats` | Achats, « Achats et prix », bloc du socle (décision 5), liens des fiches et statut gardés | |
| Outils et montage : outils, 9 étapes (`ET:1044-1078`) | `montage` → `montage` | Montage, « Outils et montage » : « Outils à réunir », 9 étapes | |
| Points à valider, 7 points (`ET:1081-1094`) | `valider` → `explication` | Explication, « À vérifier sur place », sans cases ; le point « Composition » de la variante affichée | Le `<div>` dans un `<ul>` (HTML invalide) |
| Note finale : repère, fichiers, lien au salon (`ET:1204`) | | Explication, remarque : le repère, le fichier des dimensions, le lien au salon | Les chemins de l'ancien générateur (`3d/salon/etageres.py`, `3d/salon/modele.py`) : précédent de l'entrée (spec, tableau de l'entrée) |
| Changements, 9 lignes (`ET:1133-1169`) | `changements` → `historique.html` | `salon/etageres/historique.html` (Actuelle) et `journal.html` | « Le tableau des changements va dans l'historique et le journal » (consignes) |
| CSS et JS de la page (`ET:1097-1129`, `PG:395`) | | `dessins.CSS` : les règles des classes dessinées, sur les jetons du site | `.dv`, `.dmini`, `.vbar`, `.dsel` et le JS du choix de disposition : remplacés par le socle ; police à chasse fixe : « Style » |

Une ancre absente de ce tableau, ou pas d'ancre, ouvre la vue par défaut (Plans, élévation).

## Fichiers

- Create `tests/fixtures/salon/salon-etageres.html` (copie exacte de la page à `refonte`).
- Create `pieces/salon/etageres/calculs.py` : état d'une disposition, débit, bandes, charges, achats, présentoir.
- Create `pieces/salon/etageres/dessins.py` : les dessins, `ECHELLES`, `en_cm`, `cadre_commun`, `legendes`, `CSS`.
- Create `pieces/salon/etageres/vues.py` : `vues(variante)`, Plans, Découpe, Montage, Achats.
- Create `pieces/salon/etageres/explication.py` : l'Explication.
- Modify `pieces/salon/etageres/document.py` : `_document()` (tâche 5), `__getattr__` (tâche 6), rien d'autre.
- Create `tests/test_salon_etageres_page.py` (une section par tâche). `tests/test_salon_etageres.py` n'est pas touché.
- Create `site/salon/etageres/rendus/actuelle-iso.jpg`, `actuelle-detail.jpg` (copies, tâche 4).
- Create `tests/navigateur/salon-etageres.js` (tâche 6).
- Modify `site.py`, `justfile`, `.gitignore` (lignes de la page) ; delete `salon-etageres.html`,
  `site/salon-meubles-3d/*.jpg` (tâche 6).

---

### Task 1 : Page figée et calculs d'une disposition

**Files:**
- Create: `tests/fixtures/salon/salon-etageres.html`
- Create: `pieces/salon/etageres/calculs.py`
- Test: `tests/test_salon_etageres_page.py`

**Interfaces:**
- Consumes: `pieces.salon.etageres.document` (`MONTANTS`, `ETAGERES`, `NIVEAUX`, `DISPOSITIONS`, `PANNEAU`, `TASSEAU`,
  `ROND`, `KERF`, `KERF_METAL`, `RECHANGE_CHEVILLES`, `L_MONTANT`, `BANDE`, `N_VIS`, `COEF`, `KG_M`, `KG_MONTANT`,
  `SURF_PEINT`, `MAGASINS`, `ETUDE_MONTANTS`, `CHARGE_LIVRES`, `PRESENTOIR`, `TN`), `pieces.salon.piece.H`,
  `volumes.tablettes(dispo)`, `volumes.disposition(cle)`, `meubles.cote` (l'ancien `cm`, testé égal).
- Produces, dans `calculs.py` (port de `ET:63-251`, `ET:545-577`, `ET:935-961` ; mêmes formules, mêmes noms) :
  - `CLES = ("actuelle", "rangs", "decalee", "escalier")`, tirées de `DISPOSITIONS` (ordre de la page) ;
  - `zm(t, k)`, `controle(ts, cle)`, `libres(ts)`, `bandes(ts)`, `barres(longueur, l_piece, n, kerf)`,
    `charges(ts)` : comme `ET:63-149` ;
  - `PAR_TASSEAU, N_TASSEAUX = barres(TASSEAU["l"], L_MONTANT, MONTANTS["n"], KERF)` ;
  - `achats(e) -> list[dict]` : les neuf lignes de `ET:192-227`, mêmes clés (`poste`, `article`, `ref`, `magasin`,
    `qte`, `pu`, `statut`, `url`, `note`, `total`) et mêmes textes ;
  - `etat(cle: str) -> SimpleNamespace` : comme `ET:152-177` (champs `cle, nom, idee, ts, types, kit, n_tailles,
    panneaux, entailles, chevilles, par_rond, n_ronds, metres, niveaux, ch, surf_huile, achats, total, releve, estime,
    libre_min, libre_max`) ; `ValueError` nommant la clé si elle est inconnue ;
  - `pieces(e) -> list[dict]` : comme `ET:235-251` (`rep, nom, n, dims, matiere, de`) ;
  - `FACTEUR = max(etat(c).ch["facteur"] for c in CLES)` ;
  - `PR` : `PRESENTOIR` complété comme `ET:546-563` (`t, c, s`, puis `top, bas, zc, u, prof, uc, axe, kb`),
    `passage(deg)`, `coincement(x)` ;
  - `kn(newtons)`, `taux(effort, r_k, bois=True, kmod=None)`, `fixation(e)` : comme `ET:939-961` ;
  - `note_achat(a) -> str`, `nom_magasin(a) -> str` : voir le test de l'étape 2 ;
  - `prix(v) -> str` : l'ancien `euros` (`ET:34`, deux décimales toujours : « 28,00 € »), pour les textes repris ; la
    vue Achats écrit ses montants par `commun.blocs.euros`.

- [ ] **Step 1 : Figer l'ancienne page**

```bash
cd /Users/nvi/code/work/personal/plan-wt/salon-etageres && git show refonte:salon-etageres.html > tests/fixtures/salon/salon-etageres.html \
  && git show refonte:salon-etageres.html | cmp - tests/fixtures/salon/salon-etageres.html && echo identique
```
Expected: `identique`.

- [ ] **Step 2 : Écrire les outils de test et les tests des calculs** dans `tests/test_salon_etageres_page.py`

Outils (en tête du fichier, servent à toutes les tâches) :
```python
ANCIENNE = (RACINE / "tests/fixtures/salon/salon-etageres.html").read_text(encoding="utf-8")
INDEX = json.loads((RACINE / "tests/fixtures/salon/index.json").read_text(encoding="utf-8"))

def _texte(html: str) -> str:
    """Balises remplacées par une espace, entités décodées, blancs réduits à une espace, bords ôtés."""

def _blocs(cle: str) -> list[str]:
    """HTML intérieur des sept <div class="dv" data-d="cle"> de la page figée, dans l'ordre : chapô, vue iso, le
    meuble, débit, fixation, achats, point « Composition ». Lecture par html.parser qui compte la profondeur des div."""

def _section(ident: str) -> str:
    """HTML de la page figée depuis <h2 id="ident"> jusqu'au <h2 suivant (ou à la note finale, ou à <section)."""

def _lignes(html: str) -> list[list[str]]:
    """Cellules (`_texte` de chaque td) de chaque <tr> d'un tableau, en-têtes exclus."""
```
Tests :
```python
VALEURS = {   # relevées en exécutant l'ancien générateur (V1.8)
    "actuelle": ("1 × 244 + 1 × 189 + 2 × 134 + 1 × 79", 5, 4, 7.8, (4, 122, 222), 34, 3, 2, 393.28, 365.28, 28.0, 27, 67, 6, 44, 2),
    "rangs": ("4 × 134 + 4 × 79", 8, 2, 8.52, (4, 122, 222), 40, 4, 2, 402.28, 374.28, 28.0, 27, 67, 4, 53, 1),
    "decalee": ("4 × 134 + 4 × 79", 8, 2, 8.52, (8, 122, 222), 40, 4, 2, 402.28, 374.28, 28.0, 22, 57, 4, 53, 1),
    "escalier": ("2 × 134 + 8 × 79", 10, 2, 9.0, (8, 122, 207), 44, 4, 2, 402.28, 374.28, 28.0, 27, 42, 4, 59, 3),
}  # kit, tablettes, tailles, mètres, niveaux (n, bas, haut), chevilles, ronds, plans, total, relevé, estimé,
   # libre min, libre max, repères du débit, pièces à débiter, rang du montant le plus chargé (M3, M2, M2, M4)

@pytest.mark.parametrize("cle", calculs.CLES)
def test_etat(cle):
    e = calculs.etat(cle)
    (kit, nt, tailles, metres, niv, chev, ronds, plans, total, rel, est, lmin, lmax, reps, nb, m) = VALEURS[cle]
    assert (e.kit, len(e.ts), e.n_tailles, len(e.panneaux), e.chevilles, e.n_ronds) == (kit, nt, tailles, plans, chev, ronds)
    assert math.isclose(e.metres, metres) and (len(e.niveaux), e.niveaux[0], e.niveaux[-1]) == niv
    assert (e.total, e.releve, e.estime, round(e.libre_min), round(e.libre_max), e.ch["m"]) == (total, rel, est, lmin, lmax, m)
    ps = calculs.pieces(e)
    assert (len(ps), sum(p["n"] for p in ps)) == (reps, nb)

def test_constantes():
    assert (calculs.FACTEUR, calculs.N_TASSEAUX, calculs.PAR_TASSEAU) == (1.25, 3, 2)
    assert calculs.CLES == ("actuelle", "rangs", "decalee", "escalier")
    with pytest.raises(ValueError, match="niche"):
        calculs.etat("niche")

@pytest.mark.parametrize("cle", calculs.CLES)
def test_tableaux_de_la_page(cle):
    """Liste des pièces, achats et composition : les cellules de l'ancienne page, calculées ici."""
    e = calculs.etat(cle)
    _, _, meuble, debit, _, achats, _ = _blocs(cle)
    assert [[p["rep"], p["nom"], str(p["n"]), p["dims"], p["matiere"], p["de"]] for p in calculs.pieces(e)] == _lignes(debit.split("<h3>")[0])
    *anciens, total = _lignes(achats)       # colonnes de ET:783-785 ; la dernière ligne est le total
    assert len(anciens) == len(e.achats)
    for r, a in zip(anciens, e.achats):
        # Poste, Article (+ note), Réf., Qté, Prix unit., Total, Source, Prix
        assert r == [a["poste"], _texte(escape(a["article"]) + calculs.note_achat(a)), a["ref"], str(a["qte"]),
                     calculs.prix(a["pu"]), calculs.prix(a["total"]), calculs.nom_magasin(a), a["statut"]]
    assert total[:2] == [f"Total TTC (disposition {e.nom})", calculs.prix(e.total)]
```
`calculs.note_achat(a) -> str` (port de `note_achat`, HTML d'origine) et `calculs.nom_magasin(a) -> str`
(`MAGASINS[...]["nom"].split(" Marseille")[0]`, `ET:768-770`, sans le lien) s'ajoutent aux Produces de `calculs.py`.

- [ ] **Step 3 : Lancer, constater l'échec**

Run: `uv run -q --no-project --with pytest pytest -q tests/test_salon_etageres_page.py`
Expected: FAIL, `ImportError` sur `pieces.salon.etageres.calculs`.

- [ ] **Step 4 : Écrire `calculs.py`** (calcul pur : ni HTML ni SVG ; en tête, un commentaire qui renvoie aux lignes
  `ET:` portées). Les dimensions des chaînes (`dims`, `de`, notes d'achat) s'écrivent par `meubles.cote`.

- [ ] **Step 5 : Lancer**

Run: `just tests`
Expected: tous verts.

- [ ] **Step 6 : Commit**

```bash
git add tests/fixtures/salon/salon-etageres.html pieces/salon/etageres/calculs.py tests/test_salon_etageres_page.py
git commit -m "Étagères : page V1.8 figée pour les tests, calculs d'une disposition repris de l'ancien générateur

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
```

---

### Task 2 : Dessins repris, virgules, CSS

**Files:**
- Create: `pieces/salon/etageres/dessins.py`
- Test: `tests/test_salon_etageres_page.py`

**Interfaces:**
- Consumes: `calculs` (tâche 1 : `etat`, `PR`, `coincement`, `N_TASSEAUX`, `PAR_TASSEAU`, `bandes` via `e.panneaux`) ;
  `pieces.salon.dessin` (`f`, `rect`, `text`, `cote_h`, `cote_v`, `iso_svg`) ; `volumes.pieces_3d(cle)`,
  `volumes.pieces_detail()` ; `meubles.cote` ; `document` ; `pieces.salon.enfilade.document.ENFILADE` (contour de
  l'enfilade dans l'élévation et les vues de dessus, comme `ET:25` ; présent après la fusion de `refonte` 358c024 ;
  simple lecture de donnée, symétrique de l'enfilade qui lit `MONTANTS`) ; `pieces.salon.piece.H`.
- Produces, dans `dessins.py` :
  - `ECHELLES = {"elevation": 2.4, "dessus": 2.6, "profil": 9, "travee": 3}` : les `k` de `ET:354`, `ET:429`, `ET:469`,
    `ET:504`, lus par les fonctions de dessin elles-mêmes (aucun autre `k` en dur pour ces quatre) ;
  - douze fonctions de même signature `(e: SimpleNamespace, aria: str = "") -> str`, réunies dans
    `DESSINS: dict[str, Callable]`, dans cet ordre de clés : `mini` (`elevation(e, mini=True)`, `ET:351-384`),
    `elevation` (`ET:351-409`), `dessus` (`detail_dessus`, `ET:412-464`), `iso` (`iso_svg(pieces_3d(e.cle), …)`,
    `ET:820`), `detail` (`iso_svg(pieces_detail(), …, echelle=11, style=…)`, `ET:824`), `profil` (`ET:467-499`),
    `travee` (`ET:502-524`), `presentoir` (`ET:580-614`, avec `fleche`, `rappel`, `poly` locaux), `refente`
    (`decoupe_panneaux`, `ET:617-644`), `barres` (`decoupe_barres`, `ET:647-677`), `percage` (`ET:680-722`),
    `entaille` (`ET:725-752`). `e` est ignoré par les dessins communs aux quatre. `aria` remplace l'`aria-label` de
    l'ancien dessin, échappé (`html.escape(aria, quote=True)`) ; vide : l'ancien `aria-label` (celui de `mini`,
    « Disposition X », reste toujours) ;
  - seul écart avec l'ancien tracé : « · » → « , » dans les étiquettes (`f'{t["rep"]}, {t["type"]}, {t["z"]}'`,
    `"M, 119"`, `"C, 7,5"`, `"Plan P1, plan de travail…"`, `"T1, 244"`) ;
  - `legendes(e) -> dict[str, str]` : clés `elevation, dessus, iso, detail, profil, travee, presentoir, refente,
    barres, percage, entaille` ; valeur = le texte du `<p class="cap">` qui suivait le dessin (`ET:821`, `825`, `841`,
    `843`, `852`, `855`, `869`, `900`, `903`, `913`, `916`), mêmes f-strings, sans balise (`<b>` ôtés), texte brut
    (non échappé) ;
  - `en_cm(svg: str, k: float) -> str` : même contrat que `pieces.salon.enfilade.dessins.en_cm` (viewBox divisé par
    k, arrondi à 0,001 ; contenu dans `<g transform="scale({1 / k:.6g})">`), réécrite ici (pas d'import d'une autre
    page) ;
  - `cadre_commun(svgs: Sequence[str]) -> str` : viewBox « x y l h » (nombres par `f`) de l'union des viewBox donnés ;
    `recadrer(svg: str, viewbox: str) -> str` : le même SVG, viewBox de tête remplacé ;
  - `CSS: str` : une règle par classe dessinée (`bgwall upper mont shelfc floorl ceil acier acierh mur-h trou lbl lbls
    muted rain fl flh glis dim dimt`), reprise du CSS de l'ancienne page (`3d/salon/plan.py` l. 412-470,
    `ET:1102-1104`) : `.lbl{fill:var(--ink);font-size:7.5px}`, `.lbls{fill:var(--ink);font-size:6.5px}`, puis
    `.muted{fill:var(--muted)}` après elles ; `.dim{stroke:var(--muted);stroke-width:.6;fill:none}`,
    `.dimt{fill:var(--muted);font-family:var(--ui);font-weight:600;font-variant-numeric:tabular-nums;font-size:8px}` ;
    `.mont{fill:#26262A;…}`, `.acier{fill:#8E9399;…}`, `.acierh{…#5E6369…}`, `.fl`/`.flh` en `#c2410c`, `.glis .fl` et
    `.glis .flh` en `#4d9a3a`. Aucune autre police, aucun `@media`, aucun sélecteur d'élément `table`, `button`,
    `body`, `h1-6` (`css_dessins` les retire).

Les fichiers de référence, par l'index `tests/fixtures/salon/index.json` (`label`, `disposition`) :

| Clé | `label` de l'index | Par disposition |
|---|---|---|
| `mini` | « Disposition <Nom> » | oui |
| `iso` | « Étagères, vue iso, disposition <Nom> » | oui |
| `detail` | « Étagères, détail d'une entaille en vue iso » | non |
| `elevation` | « Élévation du mur ouest, disposition <Nom> » | oui |
| `dessus` | « Étagères vues de dessus, disposition <Nom> » | oui |
| `profil` | « Profil d'une tablette entaillée et de ses deux chevilles » | non |
| `travee` | « Une travée vue de face » | non |
| `presentoir` | « Présentoir penché vers la pièce, profil » | non |
| `refente` | « Plan de découpe des plans de travail en chêne » | oui |
| `barres` | « Débit des tasseaux et des ronds » | oui |
| `percage` | « Plan de perçage d'un montant » | non |
| `entaille` | « Entaille d'une tablette » | non |

- [ ] **Step 1 : Écrire les tests**

```python
def _reference(k: str, cle: str) -> tuple[str, int]:
    """(SVG de référence, rang dans la page) du dessin `k` de la disposition `cle` (index.json : label, disposition ;
    `disposition` vide pour un dessin commun)."""

def _legende(rang: int) -> str:
    """`_texte` du premier <p class="cap"> qui suit le `rang`-ième « <svg » de la page figée."""

def _sans_aria(svg: str) -> str:
    return re.sub(r' aria-label="[^"]*"', "", svg, count=1)

CAS = [(k, c) for k in dessins.DESSINS for c in calculs.CLES] # un cas par dessin et disposition (30 distincts)

@pytest.mark.parametrize("k,cle", CAS)
def test_dessin_repris(k, cle):
    ref, _ = _reference(k, cle)
    assert _sans_aria(dessins.DESSINS[k](calculs.etat(cle))) == _sans_aria(ref.replace(" · ", ", "))

def test_virgules_au_lieu_des_points_medians():
    vus = {_reference(k, c)[0] for k, c in CAS}
    etiquettes = [t for svg in vus for t in re.findall(r"<text[^>]*>([^<]*·[^<]*)</text>", svg)]
    assert len(etiquettes) == 125
    nouveaux = "".join(dessins.DESSINS[k](calculs.etat(c)) for k, c in CAS)
    assert "·" not in nouveaux
    for t in etiquettes:
        assert f">{t.replace(' · ', ', ')}<" in nouveaux

@pytest.mark.parametrize("k,cle", [(k, c) for k, c in CAS if k != "mini"])
def test_legende_devient_texte_alternatif(k, cle):
    e = calculs.etat(cle)
    _, rang = _reference(k, cle)
    assert dessins.legendes(e)[k] == _legende(rang)
    (svg,) = balises(dessins.DESSINS[k](e, aria=dessins.legendes(e)[k]), "svg")[:1]
    assert svg["aria-label"] == dessins.legendes(e)[k] and svg["role"] == "img"

def test_en_cm_et_cadre():
    svg = '<svg viewBox="-24 0 240 120" role="img"><rect x="0" y="0" width="24" height="12"/></svg>'
    assert dessins.en_cm(svg, 2.4) == ('<svg viewBox="-10 0 100 50" role="img"><g transform="scale(0.416667)">'
                                       '<rect x="0" y="0" width="24" height="12"/></g></svg>')
    assert dessins.cadre_commun(['<svg viewBox="0 0 10 10">', '<svg viewBox="-5 2 10 20">']) == "-5 0 15 22"
    assert 'viewBox="1 2 3 4"' in dessins.recadrer('<svg viewBox="0 0 10 10" role="img"></svg>', "1 2 3 4")

def _classes(svg):
    return {c for m in re.findall(r'class="([^"]+)"', svg) for c in m.split()}

def _regle(classe, css):
    return re.search(rf"\.{re.escape(classe)}(?![\w-])[^{{]*\{{([^}}]*)\}}", css)

def test_chaque_classe_a_sa_regle():
    for k, c in CAS:
        svg = dessins.DESSINS[k](calculs.etat(c))
        assert sorted(x for x in _classes(svg) if not _regle(x, dessins.CSS)) == [], (k, c)

def test_textes_ont_une_couleur():
    """Hors de la scène (Découpe, Explication), un <text> sans règle `fill` serait noir."""
    for k, c in CAS:
        for t in re.findall(r"<text ([^>]*)>", dessins.DESSINS[k](calculs.etat(c))):
            cls = re.search(r'class="([^"]+)"', t)[1].split()
            assert "fill" in t or any("fill" in _regle(x, dessins.CSS)[1] for x in cls), (k, t)

def test_css_sur_les_jetons_du_site():
    jetons = set(re.findall(r"(--[\w-]+):", (RACINE / "commun/site.css").read_text(encoding="utf-8")))
    assert set(re.findall(r"var\((--[\w-]+)\)", dessins.CSS)) <= jetons
    assert all(v.strip().startswith("var(--") for v in re.findall(r"font-family:([^;}]*)", dessins.CSS))
    for interdit in ("monospace", "JetBrains", "Archivo", "prefers-color-scheme", "@media", "·", ".mono"):
        assert interdit not in dessins.CSS
```
Les tests `test_dessin_repris` et `test_legende…` qui portent sur un dessin commun (`profil`…) tournent quatre fois
avec le même résultat : acceptable, ou dédoublonner `CAS` pour les dessins communs (`cle = "actuelle"`).

- [ ] **Step 2 : Lancer, constater l'échec**

Run: `uv run -q --no-project --with pytest pytest -q tests/test_salon_etageres_page.py -k "dessin or virgules or legende or cm or classe or couleur or jetons"`
Expected: FAIL, `ImportError` sur `pieces.salon.etageres.dessins`.

- [ ] **Step 3 : Écrire `dessins.py`** en portant les fonctions telles quelles (mêmes chaînes, même ordre d'éléments) ;
  la seule différence de tracé permise est la virgule. Les styles en ligne de l'ancienne page (`style="fill:#fff"`,
  `stroke="var(--ink)"`, `stroke="var(--tri)"`, `style="max-width:620px"`) sont gardés.

- [ ] **Step 4 : Lancer**

Run: `just tests`
Expected: tous verts. Un écart restant se lit par `-vv` : le corriger dans le dessin, jamais dans la référence.

- [ ] **Step 5 : Commit**

```bash
git add pieces/salon/etageres/dessins.py tests/test_salon_etageres_page.py
git commit -m "Étagères : dessins repris de l'ancienne page, virgules au lieu des points médians, CSS des classes dessinées

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
```

---

### Task 3 : Plans, Découpe, Montage, Achats

**Files:**
- Create: `pieces/salon/etageres/vues.py`
- Test: `tests/test_salon_etageres_page.py`

**Interfaces:**
- Consumes: `calculs` (tâche 1), `dessins` (tâche 2), `commun.blocs` (`Achat`, `SectionAchats`, `achats`,
  `note_source`, `vue_lecture`, `euros`), `commun.blocs_construction` (`DessinMeuble`, `vue_plans`, `Colonne`,
  `tableau_debit`, `Calepin`, `calepinage`, `Etape`, `etapes`), `document.MAGASINS`, `document.DATE`.
- Produces, dans `vues.py` :
  - `RENDUS_SITE = Path(__file__).resolve().parents[3] / "site" / "salon" / "etageres" / "rendus"` ;
  - `REPERES = (("elevation", "Élévation"), ("iso", "Vue iso"), ("dessus", "Vues de dessus"), ("profil", "Profil"),
    ("travee", "Travée de face"), ("detail", "Détail d'une entaille"))` : ordre des boutons, `elevation` par défaut ;
  - `cadres() -> dict[str, str]` (mis en cache, `functools.cache`) : `{"iso": cadre_commun(iso des quatre),
    "dessus": cadre_commun(dessus des quatre)}`, sur les dessins à l'échelle de l'ancienne page ;
  - `plans(e) -> Vue` : `vue_plans([DessinMeuble(k, nom, scene, mesure=k not in ("iso", "detail")) …],
    titre=f"Disposition {e.nom}", formule=e.kit, liens=("decoupe", "montage"))` ; `scene` = le dessin avec
    `aria=legendes(e)[k]`, recadré par `cadres()` pour `iso` et `dessus`, puis `en_cm(svg, ECHELLES[k])` pour
    `elevation`, `dessus`, `profil`, `travee` ;
  - `COLONNES_DEBIT = (Colonne("Repère", "repere"), Colonne("Pièce"), Colonne("Nb", "nombre"),
    Colonne("Dimensions", "cote"), Colonne("Matière", "detail"), Colonne("Tirée de", "note"))` ;
  - `decoupe(e) -> str` : `tableau_debit(COLONNES_DEBIT, lignes de calculs.pieces(e), titre="Débit et découpe",
    sous_titre=f"Disposition {e.nom} : {len(lignes)} repères, {somme des n} pièces à débiter.")` +
    `calepinage([Calepin("Tablettes : refente des plans de chêne", refente), Calepin("Montants et chevilles", barres),
    Calepin("Perçage d'un montant", percage), Calepin("Entaille d'une tablette", entaille)],
    titre="Découpe et perçage")`, chaque SVG avec son `aria=legendes(e)[k]` ;
  - `composition(e) -> str` : `<h2>Composition</h2><div class="defile"><table>` aux 7 colonnes de `ET:845` (Repère,
    Longueur, Dessus, Montants, Débit, Entailles, Libre au-dessus ; les trois dernières `class="num"`), une ligne par
    tablette comme `ET:835-839` (`libre_txt` porté dans `vues.py`), sans `mono` ;
  - `ETAPES: tuple[tuple[str, Callable[[], str]] | …]` ou `etapes_montage() -> list[Etape]` : les neuf étapes de
    `ET:1045-1074`, titre et texte tels quels, `Etape(titre, f"<p>{escape(texte)}</p>")` ;
    `OUTILS` : le texte de `ET:1077` sans « <b>Outils</b> : », en `<p>` ;
  - `montage(e) -> str` : `composition(e) + etapes(etapes_montage(), titre="Outils et montage", outils=OUTILS)` ;
  - `sections_achats(e) -> list[SectionAchats]` : une par magasin dans l'ordre d'apparition dans `e.achats`, titre
    `MAGASINS[a["magasin"]]["nom"]` ; chaque `Achat(a["article"], a["ref"], a["qte"], a["pu"], note)` avec
    `note = f"{poste}, {euros(pu)} l'unité, {source}, prix {statut}"` + `f" ; {escape(note)}"` si l'achat a une note,
    `source` = `<a href="url">nom court</a>` (nom court : `nom.split(" Marseille")[0]`, comme `ET:768-770`) ou le nom
    court seul sans `url` ;
  - `achats_vue(e) -> str` : `achats(sections_achats(e), titre="Achats et prix", note=<note de ET:1041>,
    arrondi=False)`, et, juste après le `</h2>`, l'intro de `ET:1038` (`<p>`) et `<p class="sous-titre">Disposition
    {e.nom}</p>` ; avant la note, les paragraphes de total (`ET:1031-1032`, montants par `calculs.prix`) et de transport
    (`ET:1040`). L'insertion se fait par une fonction `_apres_titre(html, ajout)` qui échoue si `</h2>` manque ;
  - `vues(variante: str) -> dict[str, Vue]` : `plans`, `decoupe`, `montage`, `achats` ci-dessus, et `explication` vide
    (`vue_lecture("explication", "")`) jusqu'à la tâche 4 ; `ValueError` pour une variante inconnue.

- [ ] **Step 1 : Écrire les tests**

```python
V = {c: vues.vues(c) for c in calculs.CLES}

def _viewbox(svg):
    return [float(x) for x in balises(svg, "svg")[0]["viewBox"].split()]

def test_plans():
    for c, v in V.items():
        p = v["plans"]
        assert [(x.k, x.nom) for x in p.elements] == list(vues.REPERES)
        assert p.outils == ("zoom", "mesure") and {x.titre for x in p.elements} == {f"Disposition {calculs.etat(c).nom}"}
        assert f'<p class="cotes">{escape(calculs.etat(c).kit)}</p>' in p.fiche
        assert 'href="#decoupe"' in p.fiche and 'href="#montage"' in p.fiche
        for x in p.elements:
            (svg,) = balises(x.scene, "svg")[:1]
            assert svg["aria-label"] == dessins.legendes(calculs.etat(c))[x.k]
            assert (svg.get("data-mesure") == "non") == (x.k in ("iso", "detail"))

def test_cadrage_commun():
    for k in [k for k, _ in vues.REPERES]:
        assert len({balises(next(x.scene for x in v["plans"].elements if x.k == k), "svg")[0]["viewBox"]
                    for v in V.values()}) == 1, k
    iso = _viewbox(next(x.scene for x in V["actuelle"]["plans"].elements if x.k == "iso"))
    assert iso == pytest.approx([-491.8, -499.6, 553.9, 562.2], abs=0.05)
    dessus = _viewbox(next(x.scene for x in V["actuelle"]["plans"].elements if x.k == "dessus"))
    assert [v * 2.6 for v in dessus] == pytest.approx([-110, -24.4, 786.9, 1028.4], abs=0.05)

def test_mesure_en_cm():
    """Deux axes de montants voisins, lus dans le repère de la scène : 55 cm, le pas."""
    for k in ("elevation", "dessus"):
        scene = next(x.scene for x in V["actuelle"]["plans"].elements if x.k == k)
        s = float(re.search(r'<g transform="scale\(([\d.]+)\)">', scene)[1])
        monts = sorted({float(r["x"]) + float(r["width"]) / 2 for r in balises(scene, "rect", classe="mont")})
        assert (monts[1] - monts[0]) * s == pytest.approx(document.MONTANTS["pas"], abs=0.01), k

@pytest.mark.parametrize("cle,reperes,pieces", [("actuelle", 6, 44), ("rangs", 4, 53), ("decalee", 4, 53), ("escalier", 4, 59)])
def test_decoupe(cle, reperes, pieces):
    (e,) = V[cle]["decoupe"].elements
    nom = calculs.etat(cle).nom
    assert f"Disposition {nom} : {reperes} repères, {pieces} pièces à débiter." in e.scene
    assert _lignes(e.scene.split("</table>")[0]) == _lignes(_blocs(cle)[3].split("<h3>")[0])
    assert re.findall(r"<figcaption>(.*?)</figcaption>", e.scene) == [
        "Tablettes : refente des plans de chêne", "Montants et chevilles", "Perçage d'un montant", "Entaille d'une tablette"]
    assert 'class="mono"' not in e.scene

@pytest.mark.parametrize("cle", calculs.CLES)
def test_montage(cle):
    (e,) = V[cle]["montage"].elements
    ancien = _section("montage")
    assert _lignes(e.scene.split("</table>")[0]) == _lignes(_blocs(cle)[2].split("<h3>Composition</h3>")[1])
    titres = re.findall(r"<li><b>(.*?)</b> : ", ancien)
    assert re.findall(r"<h3>(.*?)</h3>", e.scene) == titres and len(titres) == 9
    for li in re.findall(r"<li><b>.*?</b> : (.*?)</li>", ancien):
        assert _texte(li) in _texte(e.scene)
    outils = re.search(r"<p><b>Outils</b> : (.*?)</p>", ancien)[1]
    assert "Outils à réunir" in e.scene and _texte(outils) in _texte(e.scene)

@pytest.mark.parametrize("cle", calculs.CLES)
def test_achats(cle):
    (v,) = V[cle]["achats"].elements
    e = calculs.etat(cle)
    assert re.findall(r"<h3>(.*?)</h3>", v.scene) == ["Weldom Marseille Saint-Barnabé", "Castorama"]
    assert f"Disposition {e.nom}" in v.scene and total_achats(vues.sections_achats(e), arrondi=False) == euros(e.total)
    for a in e.achats:
        assert escape(a["article"]) in v.scene and f"prix {a['statut']}" in v.scene
        if a["url"]:
            assert f'href="{a["url"]}"' in v.scene
    ancien = _blocs(cle)[5] + _section("achats")
    for p in re.findall(r"<p>(.*?)</p>", re.sub(r'<div class="dv".*', "", _section("achats"), flags=re.S)) \
             + re.findall(r'<p class="note">(.*?)</p>', ancien) + re.findall(r"<p><b>Total.*?</p>", ancien):
        assert _texte(p) in _texte(v.scene)
```
Imports : `escape` de `html`, `euros`, `total_achats` de `commun.blocs`.

- [ ] **Step 2 : Lancer, constater l'échec**

Run: `uv run -q --no-project --with pytest pytest -q tests/test_salon_etageres_page.py -k "plans or cadrage or cm or decoupe or montage or achats"`
Expected: FAIL, `ImportError` sur `pieces.salon.etageres.vues`.

- [ ] **Step 3 : Écrire `vues.py`** selon les interfaces.

- [ ] **Step 4 : Lancer**

Run: `just tests`
Expected: tous verts.

- [ ] **Step 5 : Commit**

```bash
git add pieces/salon/etageres/vues.py tests/test_salon_etageres_page.py
git commit -m "Étagères : vues Plans (six repères, cadrage commun, Mesurer en cm), Découpe, Montage, Achats

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
```

---

### Task 4 : Explication et rendus repris

**Files:**
- Create: `pieces/salon/etageres/explication.py`
- Modify: `pieces/salon/etageres/vues.py` (l'Explication remplace la vue vide), `pieces/salon/etageres/dessins.py`
  (règles `.dispos`, `.dispo`)
- Create: `site/salon/etageres/rendus/actuelle-iso.jpg`, `site/salon/etageres/rendus/actuelle-detail.jpg`
- Test: `tests/test_salon_etageres_page.py`

**Interfaces:**
- Consumes: `calculs`, `dessins` (`DESSINS["mini"]`, `DESSINS["presentoir"]`, `legendes`), `vues` (`RENDUS_SITE`,
  `etapes_montage`, `calculs.pieces`, `sections_achats`), `document` (`RENDUS`, `MATERIAUX`, `SOURCES_TENUE`, `TN`,
  `R_*`, `P_RUINE`, `P_CALCUL`, `ARR`, `ETUDE_MONTANTS`, `NIVEAUX`, …), `commun.blocs` (`tete`, `chiffres`,
  `materiaux`, `a_verifier`, `note_source`, `vue_lecture`, `total_achats`), `commun.blocs_construction.rendus_meuble`.
- Produces, dans `explication.py` : `explication(e) -> str`, dans cet ordre :
  1. `tete(chapo, liens=(("#plans", "Plans détaillés"), ("#achats", "Liste d'achats"), ("../../salon-v4.html", "Le salon")))`,
     `chapo = "<b>Étagères sur montants percés</b> : " + <contenu de p.pitch, ET:1171-1174, f-string telle quelle>` ;
  2. `chiffres(((e.kit, "longueurs des tablettes (cm)"), (f"{len(calculs.pieces(e))} repères", "pièces à débiter"),
     (f"{len(etapes_montage())} étapes", "de la cloison sondée au montage"),
     (total_achats(sections_achats(e), arrondi=False), "matériaux TTC, sans livraison ni outillage")))` ;
  3. `<h2>Dispositions</h2>` : le paragraphe de `ET:802` (décision 6), puis `<div class="dispos">` de quatre
     `<a class="dispo" href="H">` (H : `./#explication` pour `actuelle`, sinon `<cle>.html#explication` ; celle de la
     variante affichée porte `aria-current="page"`), chacun `<b>nom</b><span>kit</span>{DESSINS["mini"]}<span>idée</span>` ;
     puis le tableau comparatif (`ET:795-799`, `ET:804`, en `<div class="defile">`, sans `mono`), « Deux longueurs
     seulement », « Règles de composition » (`ET:805-815`), listes en `<ul class="liste">` ;
  4. `<h2>Le mécanisme</h2>` : les paragraphes de `ET:853` et `ET:856` ;
  5. `<h2>Présentoir</h2>` : `ET:866-881`, le dessin en `<figure class="calepin">` (sans `figcaption`), `aria` =
     `legendes(e)["presentoir"]` ;
  6. Rendus : pour `actuelle`, `rendus_meuble(RENDUS_SITE, "actuelle", document.RENDUS, titre="Rendus 3D")` puis
     `note_source("Disposition actuelle seulement ; les autres dispositions se rendent sur demande.")` ; pour les
     autres, `<h2>Rendus 3D</h2>` + `note_source('Rendus de la disposition Actuelle seulement (<a href="./#explication">les voir</a>) ; les autres dispositions se rendent sur demande.')` ;
  7. `materiaux([(p, f"{escape(r)}<br><small>{escape(w)}</small><br><small>Autres possibilités : {escape(a)}</small>") for p, r, w, a in MATERIAUX])`
     puis la note de `ET:889` en `note_source` ;
  8. `<h2>Tenue : poids et chute</h2>` : `ET:1005-1026` (tableau en `<div class="defile">`, listes en
     `<ul class="liste">`), le paragraphe `tenue_dispo(e)` de la seule variante, lien
     `../../archive/salon-bibliotheque-fixation.html` ;
  9. `a_verifier(points)` (titre par défaut « À vérifier sur place ») : les sept points de `ET:1087-1093`, le point
     « Composition » de la seule variante ;
  10. `note_source("Repère : origine au coin nord-ouest du salon, y vers le sud, z depuis le sol, cotes en cm.
      Dimensions : pieces/salon/etageres/document.py (DISPOSITIONS). Le reste du salon : <a href=\"../../salon-v4.html\">plan du salon</a>.")`.
- `dessins.CSS` reçoit : `.dispos{display:grid;grid-template-columns:repeat(auto-fill,minmax(220px,1fr));gap:10px;margin:14px 0}`,
  `.dispo{display:flex;flex-direction:column;gap:4px;padding:10px;border:1px solid var(--line);border-radius:12px;background:var(--panel);color:var(--ink);text-decoration:none}`,
  `.dispo[aria-current="page"]{border-color:var(--ink);box-shadow:0 0 0 1px var(--ink)}`, `.dispo svg{display:block;width:100%;height:auto}`,
  `.dispo span{font-size:13px;color:var(--muted)}` (reprises de `.dmini`, `ET:1099-1108`).

- [ ] **Step 1 : Copier les rendus tels quels**

```bash
cd /Users/nvi/code/work/personal/plan-wt/salon-etageres && mkdir -p site/salon/etageres/rendus \
  && cp salon-meubles-3d/etageres-iso.jpg site/salon/etageres/rendus/actuelle-iso.jpg \
  && cp salon-meubles-3d/etageres-detail.jpg site/salon/etageres/rendus/actuelle-detail.jpg \
  && cmp salon-meubles-3d/etageres-iso.jpg site/salon/etageres/rendus/actuelle-iso.jpg \
  && cmp salon-meubles-3d/etageres-detail.jpg site/salon/etageres/rendus/actuelle-detail.jpg && echo copies
```
Expected: `copies`. Aucune empreinte notée (`commun/rendu_cache.py` n'est pas appelé).

- [ ] **Step 2 : Écrire les tests**

```python
def _explication(cle):
    (e,) = vues.vues(cle)["explication"].elements
    return e.scene

def test_ordre_de_l_explication():
    for c in calculs.CLES:
        assert re.findall(r"<h2>(.*?)</h2>", _explication(c)) == [
            "Dispositions", "Le mécanisme", "Présentoir", "Rendus 3D", "Matériaux", "Tenue : poids et chute",
            "À vérifier sur place"]

@pytest.mark.parametrize("cle", calculs.CLES)
def test_tete_et_chiffres(cle):
    s, e = _explication(cle), calculs.etat(cle)
    chapo = re.search(r'<p class="chapo">(.*?)</p>', s)[1]
    assert chapo.startswith("<b>Étagères sur montants percés</b> : ")
    assert _texte(chapo.split(" : ", 1)[1]) == _texte(_blocs(cle)[0])
    for valeur, libelle in ((e.kit, "longueurs des tablettes (cm)"), (f"{len(calculs.pieces(e))} repères", "pièces à débiter"),
                            ("9 étapes", "de la cloison sondée au montage"), (euros(e.total), "matériaux TTC, sans livraison ni outillage")):
        assert escape(valeur) in s and libelle in s

@pytest.mark.parametrize("cle", calculs.CLES)
def test_vignettes(cle):
    liens = balises(_explication(cle), "a", classe="dispo")
    assert [a["href"] for a in liens] == ["./#explication", "rangs.html#explication", "decalee.html#explication",
                                          "escalier.html#explication"]
    assert [a.get("aria-current") for a in liens] == [("page" if c == cle else None) for c in calculs.CLES]
    for d in document.DISPOSITIONS:
        assert escape(d["idee"]) in _explication(cle)

def test_rendus():
    assert [i["src"] for i in balises(_explication("actuelle"), "img")] == ["rendus/actuelle-iso.jpg", "rendus/actuelle-detail.jpg"]
    assert [i["alt"] for i in balises(_explication("actuelle"), "img")] == [t for _, t in document.RENDUS]
    for c in ("rangs", "decalee", "escalier"):
        assert balises(_explication(c), "img") == [] and 'href="./#explication">les voir</a>' in _explication(c)

# sections de l'ancienne page → vue qui reprend leurs morceaux (p, li, td, th, h3)
DESTINATION = {"dispositions": "explication", "meuble": "explication", "presentoir": "explication",
               "rendus": "explication", "materiaux": "explication", "debit": "decoupe", "charges": "explication",
               "achats": "achats", "montage": "montage", "valider": "explication"}
# morceaux retirés ou réécrits par une décision de ce plan (décisions 5, 6 et 10, tableau « Ancienne page → vues »)
ECARTS = ("Cliquer une vignette", "<b>Outils</b> :", "Total TTC (disposition", "Géométrie :")

@pytest.mark.parametrize("cle", calculs.CLES)
@pytest.mark.parametrize("ident", sorted(DESTINATION))
def test_rien_ne_se_perd(cle, ident):
    """Chaque paragraphe, point, cellule et intertitre de l'ancienne section, dans la version de la disposition `cle`
    (blocs des autres dispositions ôtés, légendes ôtées : elles sont les textes alternatifs, testés en tâche 2), est
    dans la vue qui la reprend, ou dans Montage pour la composition."""
```
Corps de `test_rien_ne_se_perd` : retirer de `_section(ident)` les `<div class="dv" data-d="X">` des autres
dispositions (garder l'intérieur de celui de `cle`), les `<p class="cap">`, les `<button class="dmini">`, les SVG, les
cellules des montants de la vue Achats (`td.num`, écrites par le bloc au format du socle : testées en tâche 3) ; pour
chaque morceau `<(p|li|td|th|h3)>` restant qui ne contient aucun des `ECARTS`, `_texte(morceau)` doit être dans
`_texte` de la vue de destination, ou de `montage` pour la composition de `meuble`, ou de `plans` pour rien. Ajouter
le cas `_blocs(cle)[0]` (chapô) → `explication`. Les deux morceaux réécrits (« Choisir une disposition change toute la
page : élévation, vues de dessus, vue iso, composition, débit, achats et prix. », remarque du repère) ont chacun leur
assertion exacte.

- [ ] **Step 3 : Lancer, constater l'échec**

Run: `uv run -q --no-project --with pytest pytest -q tests/test_salon_etageres_page.py -k "explication or tete or vignettes or rendus or perd"`
Expected: FAIL, `ImportError` sur `pieces.salon.etageres.explication`.

- [ ] **Step 4 : Écrire `explication.py`, brancher la vue dans `vues.vues`** (import local dans `vues()` si
  `explication.py` importe `vues`, comme l'enfilade), ajouter les règles `.dispo*` à `dessins.CSS`.

- [ ] **Step 5 : Lancer**

Run: `just tests`
Expected: tous verts.

- [ ] **Step 6 : Commit** (les deux rendus sont les seuls fichiers de `site/` commités par cette branche, exception (a))

```bash
git add pieces/salon/etageres tests/test_salon_etageres_page.py site/salon/etageres/rendus/actuelle-iso.jpg site/salon/etageres/rendus/actuelle-detail.jpg
git commit -m "Étagères : Explication (dispositions, mécanisme, présentoir, matériaux, tenue, points à vérifier), rendus repris tels quels

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
```

---

### Task 5 : Document à quatre variantes et contrôles de la page

**Files:**
- Modify: `pieces/salon/etageres/document.py` (ajout de `_document()` en fin de fichier, rien d'autre)
- Test: `tests/test_salon_etageres_page.py`

**Interfaces:**
- Consumes: `vues.vues`, `dessins.CSS`, `commun.modele` (`Changement`, `Document`, `Variante`, `VUES`, `verifier`),
  `commun.construction._dessins`, `commun.css_dessins.css_dessins`.
- Produces, dans `document.py` : `_document() -> Document` (imports de `vues` et `dessins` dans la fonction : `vues`
  importe ce module) :
  `Document(piece="salon", id="etageres", nom="Étagères", type="construction", variantes=tuple(Variante(d["cle"],
  d["nom"], VERSION, tuple(Changement(*c) for c in CHANGEMENTS) if i == 0 else ()) for i, d in
  enumerate(DISPOSITIONS)), generer=vues.vues, css=dessins.CSS)`. Pas de `CACHE_RENDU`. Pas encore de `DOCUMENT`
  (décision 8).

- [ ] **Step 1 : Écrire les tests**

```python
D = document._document()
TOUT = {c: D.generer(c) for c in calculs.CLES}

def test_document():
    assert (D.piece, D.id, D.nom, D.type, D.options) == ("salon", "etageres", "Étagères", "construction", ())
    assert [(v.id, v.nom, v.version, len(v.changements), v.figees) for v in D.variantes] == [
        ("actuelle", "Actuelle", "V1.8", 9, ()), ("rangs", "Rangs", "V1.8", 0, ()),
        ("decalee", "Décalée", "V1.8", 0, ()), ("escalier", "Escalier", "V1.8", 0, ())]
    assert [(c.version, c.date, c.texte) for c in D.variantes[0].changements] == [
        (c.version, c.date, c.texte) for c in depuis_page(ANCIENNE)]
    for c, vs in TOUT.items():
        modele.verifier(D, vs)
        assert list(vs) == list(modele.VUES["construction"]) and all(v.elements for v in vs.values()), c
    assert not hasattr(document, "CACHE_RENDU")

@pytest.mark.parametrize("cle", calculs.CLES)
def test_chaque_classe_de_chaque_variante_a_sa_regle(cle):
    """Le CSS filtré comme à la construction, sur les dessins des quatre variantes réunies ; chaque classe de chaque
    scène de la variante `cle` y a une règle, sauf les classes du site (`zone`, `cotes`, `btn`, `actions`, `chapo`,
    `chiffres`, `liste`, `remarque`, `defile`, `debit`, `cartes`, `calepin`, `etapes`, `reunir`, `duo`, `num`, `d`,
    `large`, `sous-titre`, `total`, `total-achats`, `plein`, `ico`), qui ont la leur dans commun/site.css."""
    from commun.construction import _dessins
    from commun.css_dessins import css_dessins
    css = css_dessins(D.css, [s for vs in TOUT.values() for s in _dessins(vs)], ".d-salon")
    site_css = (RACINE / "commun/site.css").read_text(encoding="utf-8")
    for v in TOUT[cle].values():
        for e in v.elements:
            for c in _classes(e.scene) - {"zone"}:
                assert re.search(rf"\.{re.escape(c)}(?![\w-])", css) or re.search(rf"\.{re.escape(c)}(?![\w-])", site_css), (cle, v.id, c)

def test_aucun_interdit():
    for c, vs in TOUT.items():
        tout = "".join(v.fiche + e.scene + e.fiche for v in vs.values() for e in v.elements)
        for interdit in ("·", 'type="checkbox"', "Copier la liste", "À venir", "Lecture du plan", "Lecture de la coupe",
                         'class="mono"', 'class="cap"', 'class="dv"', "localStorage", "<figcaption class"):
            assert interdit not in tout, (c, interdit)
        visible = re.sub(r'(aria-label|alt)="[^"]*"', "", tout)
        for texte in dessins.legendes(calculs.etat(c)).values():
            assert escape(texte, quote=True) not in visible and texte not in visible

def test_liens():
    permis = {"./#explication", "rangs.html#explication", "decalee.html#explication", "escalier.html#explication",
              "../../salon-v4.html", "../../archive/salon-bibliotheque-fixation.html", "historique.html"}
    for c, vs in TOUT.items():
        for v in vs.values():
            for e in v.elements:
                for a in balises(e.scene + e.fiche + v.fiche, "a"):
                    h = a["href"]
                    assert h.startswith(("#", "https://")) or h in permis, (c, h)

def test_ids_uniques_et_classes_du_site():
    for c, vs in TOUT.items():
        tout = "".join(v.fiche + e.scene + e.fiche for v in vs.values() for e in v.elements)
        ids = re.findall(r'\bid="([^"]+)"', tout)
        assert len(ids) == len(set(ids))
        dessinees = {k for svg in re.findall(r"<svg.*?</svg>", tout, re.S) for k in _classes(svg)}
        assert not dessinees & {"app", "rail", "barre", "contenu", "vue", "scene", "fiche", "element", "outils"}
```
Imports : `depuis_page` de `commun.journal`, `modele` de `commun`.

- [ ] **Step 2 : Lancer, constater l'échec**

Run: `uv run -q --no-project --with pytest pytest -q tests/test_salon_etageres_page.py -k "document or variante or interdit or liens or ids"`
Expected: FAIL, `AttributeError: module 'pieces.salon.etageres.document' has no attribute '_document'`.

- [ ] **Step 3 : Écrire `_document()`.** Vérifier que `tests/test_salon_etageres.py::test_empreinte_des_rendus` et
  `test_generateur_entierement_vu` passent toujours (aucune constante en capitales ajoutée à `document.py`).

- [ ] **Step 4 : Lancer**

Run: `just tests`
Expected: tous verts, dont `tests/test_construction.py::test_site_py_tient_documents_et_redirections` (pas encore de
`DOCUMENT`).

- [ ] **Step 5 : Regarder le document seul, sans bascule**

Run: `python3 -c "from pieces.salon.etageres import document as d; D = d._document(); print({v.id: {k: len(x.elements) for k, x in D.generer(v.id).items()} for v in D.variantes})"`
Expected: pour chaque variante `{'plans': 6, 'decoupe': 1, 'montage': 1, 'achats': 1, 'explication': 1}`.

- [ ] **Step 6 : Commit**

```bash
git add pieces/salon/etageres/document.py tests/test_salon_etageres_page.py
git commit -m "Étagères : document à quatre variantes (Actuelle porte la V1.8 et ses neuf changements), contrôles de la page

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
```

---

### Task 6 : Bascule

**Files:**
- Modify: `pieces/salon/etageres/document.py` (`__getattr__` qui construit `DOCUMENT` à la première lecture, comme
  `pieces/salon/enfilade/document.py`)
- Modify: `site.py` (import, `Passerelle` des étagères → `salon_etageres.DOCUMENT`, `ANCRES_ETAGERES`, `Redirection`)
- Modify: `justfile` (recette `salon-etageres`, à la suite de `salon-enfilade`), `.gitignore` (`/salon-etageres.html`)
- Delete: `salon-etageres.html` ; `site/salon-meubles-3d/enfilade-iso.jpg`, `enfilade-ouverte.jpg`,
  `etageres-detail.jpg`, `etageres-iso.jpg` (décision 9, après vérification)
- Create: `tests/navigateur/salon-etageres.js`
- Test: `tests/test_salon_etageres_page.py`

**Interfaces:**
- Consumes: `document._document` (tâche 5), `commun.redirections.Redirection`, `tests.test_redirections._traduire`,
  `commun.journal.entrees`, `tests.outils.charger_site`.
- Produces, dans `site.py` :
  - `from pieces.salon.etageres import document as salon_etageres` ;
  - dans `Piece("salon", …)` : `salon_etageres.DOCUMENT` à la place de la `Passerelle` des étagères, même rang ;
  - `ANCRES_ETAGERES = {"dispositions": "explication", "iso": "plans?k=iso", "meuble": "plans?k=elevation",
    "presentoir": "explication", "rendus": "explication", "materiaux": "explication", "debit": "decoupe",
    "charges": "explication", "achats": "achats", "montage": "montage", "valider": "explication"}` (inv. § 10), avec
    un commentaire d'une ligne ;
  - `Redirection("salon-etageres.html", "salon/etageres/", ANCRES_ETAGERES, (),
    {"changements": "salon/etageres/historique.html"})`, après celle de l'enfilade.
- Produces, dans le `justfile` :
  ```
  # Salon, étagères : reconstruit ses quatre pages (site/salon/etageres/) depuis pieces/salon/etageres/
  salon-etageres:
      python3 site.py salon/etageres
  ```
  Les recettes `salon`, `salon-rendu`, `salon-meubles-rendu`, `salon-figer` ne changent pas (décision du contrôleur).

- [ ] **Step 1 : Écrire les tests de la bascule**

```python
def test_bascule():
    module = charger_site()
    (salon,) = [p for p in module.SITE.pieces if p.id == "salon"]
    assert document.DOCUMENT in salon.documents and [d.id for d in salon.documents] == ["amenagement", "etageres", "enfilade"]
    suivis = subprocess.run(["git", "ls-files", "salon-etageres.html"], cwd=RACINE, capture_output=True, text=True).stdout
    assert suivis == ""          # just salon peut réécrire la page à la racine : seul compte que git ne la suive plus
    (r,) = [r for r in module.REDIRECTIONS if r.ancienne == "salon-etageres.html"]
    assert (r.cible, r.pages) == ("salon/etageres/", {"changements": "salon/etageres/historique.html"})
    for ancre, fragment in (("dispositions", "explication"), ("iso", "plans?k=iso"), ("meuble", "plans?k=elevation"),
                            ("presentoir", "explication"), ("rendus", "explication"), ("materiaux", "explication"),
                            ("debit", "decoupe"), ("charges", "explication"), ("achats", "achats"),
                            ("montage", "montage"), ("valider", "explication"), ("inconnue", ""), ("", "")):
        assert _traduire(r, ancre) == fragment
    # chaque identifiant posé sur un titre de l'ancienne page est traduit (sauf changements, une autre page)
    assert set(re.findall(r'<h2 id="([^"]+)"', ANCIENNE)) == set(r.ancres)

def test_journal_apres_la_bascule():
    lignes = [e for e in entrees(charger_site().SITE, RACINE) if e.piece == "Salon" and e.document == "Étagères"]
    assert [(e.version, e.texte) for e in lignes] == [(c.version, c.texte) for c in depuis_page(ANCIENNE)]
    assert len(lignes) == 9 and {e.lien for e in lignes} == {"salon/etageres/"} and {e.variante for e in lignes} == {"Actuelle"}
```
Vérifier en lisant `commun/journal.py` que `e.document` est bien le nom du document et `e.variante` le nom de la
variante (sinon adapter l'assertion au champ réel, pas au code).

- [ ] **Step 2 : Lancer, constater l'échec**

Run: `uv run -q --no-project --with pytest pytest -q tests/test_salon_etageres_page.py -k "bascule or journal"`
Expected: FAIL (les étagères sont encore une `Passerelle`).

- [ ] **Step 3 : Compter le journal avant** : `python3 site.py && grep -c "Salon › Étagères" site/journal.html`
  Expected: 9. Puis `git checkout -- site && git clean -fdq site`.

- [ ] **Step 4 : Modifier `document.py` (`__getattr__`), `site.py`, `justfile`, `.gitignore`, puis
  `git rm salon-etageres.html`.**

- [ ] **Step 5 : Lancer tous les tests**

Run: `just tests`
Expected: tous verts, dont `tests/test_construction.py` (documents construits sans lien mort, toute page de la racine
connue, chaque document migré désigné par une redirection, ancres vers des vues existantes) et
`tests/test_redirections.py::test_motifs_de_site_py`. Les tests de `tests/test_salon_etageres.py` qui lisent l'ancien
générateur passent toujours (il n'est pas supprimé).

- [ ] **Step 6 : Construire le site et lire ce qu'il change**

Run: `python3 site.py && git status --short site | sort && grep -c "Étagères" site/journal.html`
Expected sous `site/` seulement : `site/salon/etageres/` (nouveau : `index.html`, `rangs.html`, `decalee.html`,
`escalier.html`, `historique.html`, `dessins.css` ; `rendus/` déjà suivi) ; `site/salon-etageres.html` (devenu une
redirection) ; `site/index.html` et `site/journal.html` (liens des neuf lignes vers `salon/etageres/`, libellé
« Étagères, Actuelle ») ; le menu de chaque page générée et historique (lien vers `salon/etageres/`). Rien sous
`site/entree/` d'autre que le menu. Neuf lignes « Étagères » au journal.

- [ ] **Step 7 : Ancien dossier d'images** : vérifier qu'aucune page restante ne cite plus `salon-meubles-3d` :
  `grep -l "salon-meubles-3d" *.html archive/*.html site/*.html site/*/*/*.html 2>/dev/null` → aucune sortie. Alors
  `git rm site/salon-meubles-3d/*.jpg` (décision 9) ; le dossier racine `salon-meubles-3d/` reste. Si une page le cite
  encore, ne rien supprimer et le noter au rapport.

- [ ] **Step 8 : Écrire `tests/navigateur/salon-etageres.js`** sur le modèle de `tests/navigateur/salon-enfilade.js`
  (en-tête `/* @site reel : … */` qui liste ce qu'il vérifie ; mêmes outils `preparer`, `ouvrir`, `attendre`,
  `debordements`), `DOC = ${BASE}/salon/etageres/`, `VARIANTES = {actuelle: "", rangs: "rangs.html",
  decalee: "decalee.html", escalier: "escalier.html"}`, `REPERES = ["elevation", "iso", "dessus", "profil", "travee",
  "detail"]`, `LARGEURS = [[1440, 900], [1100, 800], [390, 844]]` :
  - **vues** : pour chaque variante, chaque largeur, les cinq vues et les six repères : aucune erreur de console ni
    réponse en erreur, rien ne déborde, aucun défilement horizontal à 390 px, aucun onglet grisé ;
  - **variante** : choisir Rangs depuis `#plans?k=dessus` charge `rangs.html#plans?k=dessus` (fragment gardé) ; la
    pastille de version dit « V1.8 » ; aucun bouton « Personnaliser » ;
  - **comparaison** : `${DOC}#plans?k=dessus&c=escalier` montre deux SVG de même viewBox, les noms « Actuelle » et
    « Escalier » en bas, aucune étiquette « pas d'équivalent » ni « comparaison indisponible » pour aucun des six
    repères ; recharger l'adresse redonne le même état (aller-retour) ; choisir Escalier comme base inverse les deux ;
    « Comparer » absent de Découpe, Montage, Achats, Explication ;
  - **Mesurer** (Review Focus 1) : sur `#plans?k=elevation`, cliquer les centres de deux montants voisins (`rect.mont`
    1 et 2, par leurs boîtes à l'écran) affiche « 55,0 cm » à ± 0,5 ; `#plans?k=iso` : bouton Mesurer caché ;
  - **dessins lisibles** : dans chaque scène, dessin de Découpe et figure de l'Explication, aucune forme ni texte au
    `fill` ou `stroke` calculé `rgb(0, 0, 0)` ; aucune police calculée à chasse fixe ; la boîte de chaque `text` tient
    dans le viewBox de son SVG (un écart déjà présent dans le dessin de référence est relevé comme tel, sans échec) ;
  - **Explication** : quatre vignettes, celle de la variante en `aria-current` ; Actuelle : deux images chargées
    (`naturalWidth > 0`) ; les trois autres : aucune image, le lien « les voir » mène à `${DOC}#explication` ;
  - **anciennes adresses** : `/salon-etageres.html` → `/salon/etageres/` sur Plans, élévation ; chaque ancre de
    `ANCRES_ETAGERES` → son fragment ; `#inconnue` → Plans ; `#changements` → `/salon/etageres/historique.html` ;
  - **historique** : une section par variante, neuf changements sous Actuelle, aucun ailleurs, aucune version figée ;
  - **sans JavaScript** (1440 et 390 px) : classe `sans-js`, les cinq vues l'une sous l'autre, les six dessins de
    Plans visibles, la page ne déborde pas.
  Le script renvoie `{ok, echecs, erreurs}`.

- [ ] **Step 9 : Lancer le script**

Run: `PORT=8840 SESSION=refonte-salon-etageres-1 tests/navigateur/lancer.sh tests/navigateur/salon-etageres.js`
Expected: `"ok": true`, aucun échec, aucune erreur. Puis relancer `entree.js`, `chambre-amenagement.js` et
`salon-enfilade.js` (ports 8841 à 8843, sessions `refonte-salon-etageres-2` à `-4`) : le menu de leurs pages a changé ;
`"ok": true` attendu.

- [ ] **Step 10 : Remettre `site/` et commiter**

```bash
git checkout -- site && git clean -fdq site
git add site.py justfile .gitignore pieces/salon/etageres/document.py tests/test_salon_etageres_page.py tests/navigateur/salon-etageres.js
git status --short
git commit -m "Étagères : bascule, le document remplace la passerelle, salon-etageres.html redirige avec ses ancres

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
```
Expected avant le commit : `git status --short` ne montre que `site.py`, `justfile`, `.gitignore`,
`pieces/salon/etageres/document.py`, les tests, `D  salon-etageres.html` et les `D  site/salon-meubles-3d/*.jpg`
(si l'étape 7 les a supprimés), rien d'autre sous `site/`.

---

## Après le plan : vérification au navigateur (étape de l'orchestrateur, pas une tâche)

Par un agent qui n'a rien implémenté (`sonnet`), sur le site construit (`python3 site.py`) et servi en local, à 1440,
1100 et 390 px (ports 8844-8849, sessions `refonte-salon-etageres-5` et suivantes) :
- relancer `tests/navigateur/salon-etageres.js`, puis regarder une à une les captures de chaque vue de chaque
  variante, des six repères et des comparaisons (`#plans?k=iso&c=rangs`, `#plans?k=dessus&c=escalier`) ;
- comparer à l'œil avec l'ancienne page, servie à part depuis `git show refonte:salon-etageres.html` (avec les images de
  `salon-meubles-3d/`) sur un autre port, disposition par disposition (bouton Disposition de l'ancienne barre) : aucun
  contenu perdu, chaque ligne du tableau « Ancienne page → vues » retrouvée ;
- chaque ancienne adresse et ancre redirige ; sans JavaScript, la page reste lisible ;
- dessins lisibles : aucun élément noir par défaut de style, aucune étiquette coupée ;
- rapport et captures dans l'espace du plan, défauts classés (page, socle, référence).
