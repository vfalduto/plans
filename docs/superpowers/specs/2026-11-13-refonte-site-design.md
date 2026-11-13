# Site des plans : refonte de la navigation, des documents et des fichiers

## Intention

Le site a grandi pièce par pièce, et chaque générateur a sa propre barre, son CSS, son JS et ses fonctions de dessin.
Constat de départ (13/11/2026) :
- **Navigation :** la barre du haut passe sur deux ou trois lignes, le sommaire disparaît sous 1100 px, et la chambre
  n'a pas de barre.
- **Variantes :** il existe quatre mécanismes différents :
  - les versions figées cachées dans la page de la cuisine ;
  - une page à part pour Victor (`P.M = M`) ;
  - le sélecteur de disposition des étagères ;
  - les archives.
- **Historique :** il est éparpillé entre les tableaux « Changements » de chaque page et une liste d'archives tenue à
  la main dans l'index.
- **Mobile :** les plans ont une largeur minimale de 640 px dans une boîte à défilement horizontal. Les pages sont très
  longues : la cuisine fait 14 106 px.
- **Poids :** la cuisine pèse 427 Ko avec trois versions incluses, les étagères 936 Ko avec quatre dispositions.

Demande du client :
- uniformiser la navigation ;
- donner à chaque document les mêmes vues : une explication, le plan, les coupes, les rendus iso et les rendus caméra
  pour une pièce ; une explication, les plans détaillés, la découpe, le montage et les achats pour un meuble ;
- gérer les variantes d'une seule façon ;
- avoir un historique commun ;
- avoir une meilleure interface sur mobile ;
- avoir plus d'interaction ;
- pouvoir personnaliser quand ça a du sens (matériaux, couleurs) ;
- pouvoir à terme faire un rendu iso complet de l'appartement ;
- au passage, réduire le temps de rendu.

## Référence : la maquette

La maquette `plans/maquette/` (`app.html`, présentée par `index.html`) a été validée en huit tours de retours le
13/11/2026. Elle sert de référence visuelle et de comportement :
- ce que cette spécification ne décrit pas suit la maquette ;
- en cas de désaccord entre les deux, la spécification l'emporte.

Contenu repris dans la maquette :
- **Entrée :** V4.8, variantes Principale et Victor.
- **Étagères du salon :** quatre dispositions.
- **Autres documents :** un simple renvoi.

`maquette/extraire.py` extrait ce contenu des pages publiées vers `donnees.js`. Le JS de la maquette (zoom, mesure,
rideau, fiches, points de vue) est le point de départ de `site.js`.

## Objectifs

### 1. Une navigation identique sur toutes les pages

- **Menu de gauche :**
  - il liste les pièces, puis les documents de chaque pièce, avec des icônes ;
  - il est réduit par défaut à 56 px (icônes seules), se déplie avec un bouton, et son état est mémorisé ;
  - il n'a pas de plan de repérage ;
  - en pied de menu se trouve le lien « Journal des changements » ;
  - la pièce courante est marquée en jaune (`--repere`).
- **Barre du haut sur ordinateur, sur deux lignes :**
  - **Ligne 1, à gauche :** pièce › document. Le document est une liste déroulante si la pièce en a plusieurs.
  - **Ligne 1, à droite :**
    - le choix de la variante ;
    - « Comparer » ;
    - « avec … » (voir l'objectif 4) ;
    - la pastille de version, qui ouvre l'historique du document.
  - **Ligne 2 :** les onglets des vues, icône et nom, et à droite « Personnaliser » si le document déclare des options.
- **Mobile (≤ 919 px) :**
  - **En haut :**
    - à gauche, l'icône maison, qui ouvre le menu en tiroir ;
    - le titre sur deux lignes : la pièce, puis le document ;
    - la variante, puis « Comparer » et la version, en icônes seules ;
    - « Personnaliser », en icône.
  - **En bas :** les onglets, fixés.
  - **Pas de double titre :** la scène ne répète pas le titre de la fiche.
  - **Avec deux choix de variante** (base et comparée), la pastille de version est masquée pour que le titre reste
    lisible.
- **Style :**
  - **Couleurs :**
    - le fond est le papier `#EEF0EC` ;
    - la navigation est en `#000000c7`, toujours posée sur le papier, jamais transparente sur le contenu ;
    - le jaune `#F2CF4A` marque « vous êtes ici ».
  - **Polices :** Fira Sans pour le texte, Fira Sans Condensed pour l'interface et les cotes, avec des chiffres
    tabulaires.
  - **Exclus :** pas de mode sombre, pas de quadrillage, pas de police à chasse fixe, pas de points médians.
  - **Jetons CSS :** ils reprennent les noms du projet (`--paper`, `--ink`, `--muted`, `--line`, `--panel`, `--wood`,
    `--water`, etc.).

### 2. Deux types de documents, cinq vues chacun

| Type | Vues, dans l'ordre | S'ouvre sur |
|---|---|---|
| Aménagement (une pièce) | Plan, Coupes, Iso, Caméra, Explication | Plan |
| Construction (un meuble) | Plans, Découpe, Montage, Achats, Explication | Plans |

« Coupes » désigne les coupes d'une pièce. « Découpe » désigne la liste de débit et le calepinage d'un meuble.
L'historique n'est pas un onglet.

**Une vue sans contenu** (choix de Claude) :
- son onglet reste à sa place, mais grisé, avec une bulle « Pas encore rendu » ou « Sans objet », comme le coin NE de
  l'iso ;
- la navigation reste ainsi identique d'un document à l'autre.

Cas connus :
- **Chambre :** pas de modèle 3D, donc Iso et Caméra sont grisés. La modéliser est hors champ. Ses élévations vont dans
  Coupes, un bouton par élévation.
- **Porte du cellier :** c'est un produit acheté, donc Découpe et Montage sont « Sans objet » s'il n'y a rien à
  découper ni à monter.
- **Rendus d'un meuble** (étagères, enfilade) : ils vont dans son Explication, comme dans la maquette.

- **Plan :**
  - le dessin SVG occupe la scène ;
  - outils posés sur la scène : zoom (+, −, Recadrer, molette, pincement, glisser) et Mesurer (distance en cm) ;
  - la fiche, à droite sur ordinateur et en feuille basse sur mobile, contient :
    - « Touchez un meuble pour afficher sa fiche. » ;
    - les calques : Cotes, Passages libres, Traits de coupe, Pièces voisines, Annotations (choix mémorisé) ;
    - la légende ;
  - toucher un meuble, ou le choisir au clavier, ouvre sa fiche : titre, cotes, texte, boutons « Coupe A », « Iso »
    et « Fermer ».
- **Coupes :**
  - une coupe à la fois, avec zoom et Mesurer ;
  - la fiche contient un bouton par coupe (lettre et sujet), puis « Position » : le mini-plan avec le trait de la coupe
    courante.
- **Iso :**
  - le rendu, avec zoom ;
  - la fiche contient les boutons NO, NE, SO et SE (grisés si le coin n'est pas rendu), puis « Position » : le
    mini-plan avec les points de vue, le point courant en plein.
- **Caméra :**
  - le rendu, avec zoom ;
  - la fiche contient « yeux à X cm, objectif 17 mm », un bouton par caméra s'il y en a plusieurs, puis « Position »
    avec le cône de vision.
- **Explication :** le chapô, les chiffres clés, les principes, les matériaux, les achats (pour un aménagement) et
  « À vérifier sur place » (une liste, sans cases).
- **Plans (construction) :** l'élévation ou la vue iso (deux boutons), la formule des longueurs, des liens vers
  Découpe et Montage, et Mesurer.
- **Découpe, Montage, Achats :**
  - le contenu actuel des pages, sans cases à cocher ;
  - les achats sont un tableau (article, référence, quantité, prix) avec le total ;
  - pas de bouton « Copier la liste ».
- **Textes :**
  - les panneaux restent concis ;
  - aucune description textuelle d'image à l'écran : ces textes restent en texte alternatif ;
  - pas de bloc « À venir ».

### 3. Trois notions distinctes : variante, option, version

- **Variante :** une autre conception, menée en parallèle. Exemples : Principale et Victor pour l'entrée ; Actuelle,
  Rangs, Décalée et Escalier pour les étagères.
  - Chaque variante ne déclare que ce qui la distingue de la variante principale.
  - Toutes les variantes d'une pièce partagent ses murs, ses portes et ses caméras (`piece.py`). Les comparaisons
    tombent donc juste, et le décalage de caméra de Victor ne peut plus se produire.
- **Option :** un réglage que le lecteur change, déclaré par le document. « Personnaliser » est générique : la teinte
  de l'entrée n'est qu'un cas.
  - **Déclaration :** chaque option a un identifiant, un nom, les surfaces concernées, un type (nuancier ou choix), une
    valeur par défaut, ses valeurs, et une portée en une ligne (« Visible sur le plan, les coupes et les rendus. »).
  - **Panneau :** il se construit depuis cette liste. Une pastille compte les options changées, et un bouton remet les
    « Valeurs d'origine ».
  - **Mémorisation :** le choix est gardé par lecteur (`localStorage`).
  - **Teinte sur les rendus :** on garde la technique actuelle. Un rendu neutre et un masque PNG passent dans un filtre
    SVG `feComponentTransfer`, avec `REF_MUR` = 0,80.
  - **Options qui demandent un nouveau rendu :** elles le disent.
- **Version :** l'historique d'une variante. C'est le cas aujourd'hui : Victor est en V1.5, avec sa propre liste
  `CHANGEMENTS`.
  - **Numéro et changements :** chaque variante a son numéro et sa liste `CHANGEMENTS`. Le numéro de la variante
    principale est celui du document (V4.8 pour l'entrée), et la pastille de version montre celui de la variante
    affichée (choix de Claude).
  - **Versions figées :** figer une version fige une variante. Chaque version figée est copiée une seule fois dans
    `site/archives/` (la V11.49 de la cuisine existe aujourd'hui en trois exemplaires).
  - **Lecture d'une version figée :** elle se lit telle quelle, depuis la page d'historique du document (décision du
    client, 13/11/2026). Le bouton qui affiche aujourd'hui une version figée dans la page de la cuisine et du salon
    (« V11.9 figée ») disparaît.
  - **Comparaison :** « Comparer » ne sert qu'entre variantes. Le tableau de capacité de la cuisine, qui compare version
    figée, version affichée et proposition 9 A, est du contenu : il reste dans l'Explication.

### 4. Comparer deux variantes

C'est le comportement de la maquette, version du 13/11/2026.

- **Où :** « Comparer » est dans la barre du haut, juste après le choix de variante.
- **Choix des variantes :**
  - la variante choisie est la base ;
  - avec plus de deux variantes, un second choix « avec … » désigne la variante comparée ;
  - avec deux variantes, l'autre est prise d'office.
- **Adresse :**
  - l'adresse porte les deux variantes, donc le lien s'envoie tel quel ;
  - la comparaison reste active d'un onglet comparable à l'autre ;
  - choisir comme base la variante comparée inverse les deux.
- **Rideau :**
  - il se glisse à la souris, au doigt et au clavier (flèches gauche et droite) ;
  - la base est à gauche, la variante comparée à droite ;
  - sur un rendu zoomé, la coupure reste sous la poignée.
- **En comparaison :**
  - les outils de la scène ne bougent pas ;
  - les noms des deux variantes sont en bas de la scène ;
  - la mesure s'affiche entre les deux.
- **Équivalents :**
  - plan : toujours ;
  - coupe : même lettre ;
  - iso : même coin ;
  - caméra : même identifiant ;
  - plans d'un meuble : même vue (élévation ou iso) ;
  - s'il n'y a pas d'équivalent, l'étiquette le dit : « Principale : pas d'équivalent » (coupe D, seulement chez
    Victor).
- **Vues comparables :**
  - Plan, Coupes, Iso, Caméra, Plans ;
  - pas Explication, Découpe, Montage ni Achats : le bouton n'y apparaît pas.
- **Plan en comparaison :** les meubles ne sont pas cliquables.

### 5. Journal commun et historique d'un document

- **Journal** (`journal.html`) :
  - tous les changements de tous les documents, du plus récent au plus ancien, filtrables par pièce ;
  - construit depuis les listes `CHANGEMENTS` ;
  - chaque ligne nomme la pièce, le document et, s'il y en a plusieurs, la variante (« Entrée › Aménagement, Victor ») ;
  - il remplace la liste d'archives tenue à la main dans l'index ;
  - le 13/11/2026, il compte 179 changements en 15 jours de travail.
- **Historique d'un document** (ouvert par la pastille de version) : une seule page par document. Pour chaque
  variante, elle montre ses versions figées avec leur date, puis son journal.

### 6. Mobile

- **Scène :** le dessin ou le rendu occupe l'écran.
- **Fiche :** elle s'ouvre depuis le bas, avec 48 px fermée et au plus 54 % de la hauteur une fois ouverte.
- **Iso et caméra :** même disposition que les coupes (boutons des vues, puis le mini-plan).
- **Largeur :** rien ne dépasse de l'écran à 390 px, et la page ne défile jamais horizontalement.

### 7. Interaction

Elle est décrite dans les objectifs précédents :
- les meubles qu'on touche sur le plan ;
- Mesurer ;
- les calques ;
- le zoom sur toutes les vues dessinées ou rendues ;
- les points de vue sur le mini-plan ;
- le rideau de comparaison ;
- Personnaliser.

Contrainte commune : tout ce qui se fait au doigt se fait aussi au clavier.

### 8. Accueil : le plan de l'appartement

- **Contenu :** l'accueil montre le plan de l'appartement seul. La vue iso en maquette blanche de la maquette a été
  retirée.
- **Construction du plan :**
  - les pièces sont placées dans un repère commun ;
  - leur implantation vient du PDF du logement ;
  - les cotes viennent des pages du site, qui priment sur le PDF ;
  - la branche est du couloir reste à 90 × 104.
- **Lien vers les documents :** chaque pièce du plan mène à ses documents.
- **À terme :** le même repère servira au rendu iso complet de l'appartement (hors champ ici). Chaque `piece.py` porte
  donc sa position et son orientation dans ce repère.

### 9. Rendus plus rapides

Mesures du 13/11/2026 sur une copie du projet, pour l'entrée (M1 Pro, Blender 5.2.2, Cycles Metal, 64 échantillons,
1600 × 1200). La machine était chargée : le même rendu a pris 29 s, 46 s puis 110 s. Les écarts d'image sont fiables,
les durées non.

| Vue | Image | Masque |
|---|---|---|
| Iso | 29 s | 2,7 s |
| Caméra | 46 s | 4,8 s |

Soit environ 2 min 30 par variante pour `just entree-rendu`.

- **Ne refaire que ce qui a changé :**
  - chaque vue est rendue à nouveau seulement si ses entrées ont changé : la partie du modèle utilisée, la caméra, les
    réglages et la version de Blender ;
  - une empreinte par vue est stockée dans `cache/` ;
  - aujourd'hui, chaque commande refait tout.
- **Seuil de bruit adaptatif à 0,03, au lieu de 0,01 :** l'image est identique à l'œil (écart moyen de 0,03 à 0,14
  sur 255). Le gain de temps reste à mesurer machine au repos, avant d'adopter ce réglage.
- **Écartés :**
  - **Moins de rebonds :** le rendu caméra s'assombrit visiblement (écart de 3,6 sur 255).
  - **EEVEE :** l'image s'écarte trop (écart de 20 sur 255 en caméra).
- **Aperçu rapide :** l'aperçu Cycles de la cuisine (`v13-apercu`) s'étend à toutes les pièces.
- **Poids des pages :** une page par variante (voir « Adresses ») règle le poids des pages de la cuisine et des
  étagères.

## Approches pour la construction

1. **Générateurs Python conservés, avec un gabarit commun** (retenue) :
   - un module partagé écrit le HTML ;
   - le CSS et le JS sont deux fichiers communs ;
   - les pages restent lisibles sans JavaScript : les vues s'affichent alors l'une sous l'autre ;
   - la migration se fait document par document.
2. **Application JS qui lit des données**, comme la maquette. L'interaction serait plus libre, mais c'est une
   réécriture, et les pages ne se lisent plus sans JavaScript.
3. **Générateur de site du commerce.** Il ajoute une chaîne Node à un projet Python ; c'est écarté.

Le client a laissé le choix à Claude (« je te fais confiance »). L'approche 1 est retenue : elle garde les modèles
Python comme source unique et permet une migration progressive.

## Adresses (choix de Claude)

- **Une page par document et par variante :**
  - `/<piece>/<document>/` pour la première variante, ou pour un document sans variante ;
  - `/<piece>/<document>/<variante>.html` pour les autres ;
  - chaque page contient toutes les vues, une section par vue ;
  - changer de variante charge l'autre page en gardant le fragment.
- **L'état est dans le fragment** : `#<vue>?k=<repère>&c=<variante comparée>`.
  - `k` est la coupe (`A`), le coin iso (`so`), la caméra (`banc`), la vue d'un meuble (`iso`) ou le meuble choisi sur
    le plan.
  - Exemple : `/entree/amenagement/victor.html#coupes?k=D&c=principale`.
- **La comparaison** charge par `fetch` la page de la variante comparée, puis en extrait l'élément équivalent. Elle
  demande donc un serveur : GitHub Pages en ligne, et `python3 -m http.server` (recette `just apercu`) en local.
- **Autres pages :**
  - `/index.html` : l'accueil ;
  - `/journal.html` : le journal ;
  - `/<piece>/<document>/historique.html` : l'historique d'un document ;
  - `/archives/…` : les versions figées.
- **Anciennes adresses :**
  - chaque page publiée aujourd'hui garde son adresse, sous forme de page de redirection (`meta refresh`, plus un JS
    qui garde le fragment) ;
  - une ancre de l'ancienne page est traduite vers la vue correspondante quand c'est possible.

## Génération

- **`site.py`** est le seul point d'entrée qui construit le site :
  - il lit les pièces et leurs documents ;
  - il écrit l'accueil, le menu (le même dans toutes les pages), le journal, les historiques et les redirections ;
  - il appelle le générateur de chaque document.
- **`commun/` :**
  - `gabarit.py` : l'enveloppe de page (en-tête, menu, barre, onglets, fiche, outils) ;
  - `site.css` et `site.js` : copiés dans `site/commun/` ;
  - `dessin.py` : les fonctions SVG (`rect`, `text`, `cote_h`, `cote_v`), aujourd'hui recopiées dans chaque
    générateur ;
  - `rendu.py` : les réglages Cycles et le cache de rendu ;
  - `materiaux.py` : les matériaux ;
  - `appartement.py` : le repère commun et le plan de l'accueil.
- **`pieces/<piece>/piece.py` :** les murs, portes, fenêtres et caméras, et la position dans le repère commun.
- **`pieces/<piece>/<document>/document.py` déclare :**
  - le nom, le type, la version et les `CHANGEMENTS` ;
  - les variantes et les options ;
  - le contenu de chaque vue : SVG du plan et des coupes, coins iso rendus, textes de l'explication, débit, étapes,
    achats ;
  - les meubles du plan et leurs liens vers une coupe et un coin iso.
- **`pieces/<piece>/<document>/<variante>.py` :** seulement ce qui diffère de la variante principale.
- **Le JS** ne fait que l'interaction : onglets, zoom, mesure, calques, fiche, rideau et options. Tout le contenu est
  dans le HTML généré.
- **Les dimensions** se calculent depuis les modèles, jamais en dur dans les textes. C'est déjà une règle du dépôt.

## Organisation des fichiers

Elle a été approuvée par le client le 13/11/2026.

```
plan/
├── site.py          pièces, documents, variantes, versions → accueil, menu, journal
├── commun/          gabarit de page, dessin SVG, rendu Blender, matériaux, plan de l'appartement
├── pieces/
│   ├── entree/
│   │   ├── piece.py              murs, portes, fenêtres, caméras
│   │   └── amenagement/
│   │       ├── document.py       meubles, cotes, explication, versions
│   │       └── victor.py         seulement ce qui diffère
│   ├── salon/  cuisine/  sdb/  chambre/
├── site/            généré et publié, jamais modifié à la main ; archives/ = versions figées
├── cache/           rendus Blender (l'actuel 3d/sortie), ignoré par git
├── ressources/      textures et modèles 3D, ignorés par git
├── notes/           recherches en markdown
└── explorations/    essais de la salle de bain (niv_*, var_*, test_*)
```

- **`site/`** est versionné, car les rendus demandent Blender et ne peuvent pas être refaits par la publication.
- **`cache/` et `ressources/`** remplacent `3d/sortie/` (1,6 Go), `3d/textures/` (42 Mo) et `3d/modeles/` (133 Mo),
  déjà ignorés par git.
- **`achats/` (outil sans rapport avec le site) et `reddit/`** ne sont pas suivis par git. Ils quittent le dossier pour
  des dossiers voisins, `../achats` et `../reddit` (choix de Claude).
- **Les notes en markdown de la racine** (`cuisine-cellier-recherche.md`, `cuisine-fileurs-marges.md`) vont dans
  `notes/`.
- **`docs/superpowers/`** (spécifications et plans) reste où il est.

## Publication

Aujourd'hui, GitHub Pages publie la branche `main` depuis la racine (`build_type: legacy`, lu le 13/11/2026). Toute la
racine est donc en ligne : scripts, notes, `3d/`.

Fait vérifié le 13/11/2026 sur docs.github.com : une publication depuis une branche ne peut partir que de la racine ou
de `/docs`. `site/` demande donc l'une de ces deux solutions :

- **GitHub Action** (retenue, choix de Claude) :
  - un workflow publie `site/` avec `actions/upload-pages-artifact@v3` (`path: site`), puis `actions/deploy-pages@v4` ;
  - la source Pages passe à « GitHub Actions » dans les réglages du dépôt ;
  - `just pages-wait`, qui lit aujourd'hui `pages/builds/latest`, suit à la place l'exécution du workflow
    (`gh run watch`) ;
  - seul `site/` est publié, et le nom `site/` approuvé est gardé ;
  - `docs/superpowers/` ne bouge pas ;
  - à respecter : `site/` ne doit contenir aucun lien symbolique ni physique, et l'archive publiée doit rester sous
    1 Go.
- **Renommer `site/` en `docs/`** et déplacer `docs/superpowers/` : écarté. Cela change le nom approuvé et le chemin où
  les outils superpowers écrivent.

## Migration

Elle se fait document par document. Le site reste en ligne et cohérent à chaque étape : les pages pas encore migrées
gardent leur adresse actuelle, et le menu pointe vers elles.

**Passerelle** (choix de Claude) :
- tant qu'un document n'est pas migré, `site.py` recopie sa page actuelle et ses dossiers d'images dans `site/`, au
  même chemin ;
- une fois que seul `site/` est publié, les pages non migrées restent donc en ligne ;
- les générateurs existants continuent d'écrire à la racine, comme aujourd'hui, jusqu'à la migration de leur document.

**Branche** (choix de Claude) : la migration se fait sur une branche, fusionnée dans `main` après le socle, puis après
chaque document.

**Avec l'autre session** (décision du client, 13/11/2026) :
- **Départ :** la migration commence quand l'autre session a commité son travail en cours. Le 13/11/2026, `main` est à
  « Entrée V4.0 » et 24 fichiers ne sont pas commités : l'entrée de V4.1 à V4.8, la cuisine depuis V13.27, et tout
  Victor.
- **Gel :** pendant qu'un document est migré, l'autre session n'y touche pas. Elle continue sur les autres documents.
- **Fusion :** une fusion dans `main` après chaque document.

0. **Socle :**
   - `commun/` et `site.py` ;
   - `site.css` et `site.js`, repris de la maquette ;
   - le workflow de publication ;
   - le mécanisme de redirection et la passerelle ;
   - le journal construit depuis les `CHANGEMENTS` existants ;
   - la table complète « ancien chemin → nouveau chemin », versionnée dans le dépôt ;
   - à la fusion du socle, dans cet ordre :
     1. `just sync` et `just pages-wait` passent au workflow ;
     2. le client bascule la source Pages sur « GitHub Actions » ;
     3. le site est vérifié en ligne.
1. **Entrée :**
   - c'est la plus proche de la cible : un modèle source unique (`3d/entree/modele.py`), deux variantes, et des masques
     de teinte déjà rendus ;
   - Victor devient `victor.py` et ne déclare que ses différences ;
   - les caméras passent dans `piece.py`. Les deux points de vue (`banc` et `couloir`) sont rendus pour les deux
     variantes, pour que la comparaison caméra serve.
2. **Salon :** aménagement (`salon-v4.html`), étagères (quatre dispositions, donc quatre pages), enfilade.
3. **Salle de bain :** meuble bas et meuble haut. Les explorations de `3d/sdb/` vont dans `explorations/`.
4. **Cuisine :**
   - aménagement V13 et porte du cellier ;
   - les sources V11 et V12 deviennent des versions figées, une copie chacune, puis sortent de l'arbre ; l'historique
     git les garde.
5. **Chambre :**
   - elle est écrite à la main aujourd'hui ;
   - il faut créer `piece.py` et `document.py` à partir de la page existante.

Pour chaque document :
- **Avant de supprimer un ancien générateur :** chaque section de l'ancienne page doit avoir trouvé sa place dans une
  vue, ou être retirée en application d'une décision listée plus bas.
- **Après la migration :** l'ancienne adresse redirige.

| Page actuelle | Générée par | Devient |
|---|---|---|
| `index.html` | plusieurs générateurs | `index.html` (accueil) |
| `entree-amenagement.html` | `3d/entree/plan.py` | `entree/amenagement/` |
| `entree-amenagement-victor.html` | `3d/entree/plan_victor.py` | `entree/amenagement/victor.html` |
| `salon-v4.html` | `3d/salon/plan.py` | `salon/amenagement/` |
| `salon-etageres.html` | `3d/salon/etageres.py` | `salon/etageres/` (+ une page par disposition) |
| `salon-enfilade.html` | `3d/salon/enfilade.py` | `salon/enfilade/` |
| `sdb-meuble-bas.html` | `3d/sdb/bas.py` | `sdb/meuble-bas/` |
| `sdb-meuble-haut.html` | `3d/sdb/haut.py` | `sdb/meuble-haut/` |
| `sdb-meuble-achats.html` | `3d/sdb/achats.py` | section « Les deux meubles » de la vue Achats de chaque meuble |
| `cuisine-v13.html` | `3d/v13/plan.py` | `cuisine/amenagement/` |
| `cuisine-v13-porte-cellier.html` | `3d/v13/porte.py` | `cuisine/porte-cellier/` |
| `cuisine-v13-imprimable.html` | `3d/v13/imprimable.py` | `cuisine/amenagement/imprimable.html` (page à part, inchangée) |
| `cuisine-v13-maquette.html` | `3d/v13/maquette.py` | `cuisine/amenagement/maquette-3d.html` (page à part, inchangée) |
| `cuisine-plan.html` | `3d/v11`, `3d/cuisine_a.py` | `archives/` (Proposition 9 V2) |
| `cuisine-couleurs.html` | à la main | `archives/`, telle quelle |
| `chambre-amenagement.html` | à la main | `chambre/amenagement/` |
| `archive/*.html` (59 pages) | figées | `archives/`, une copie par version |

## Contraintes

- **Source unique :** les modèles Python restent la seule source des dimensions. `site/` n'est jamais modifié à la
  main.
- **Pas de rupture de lien :** toute adresse publiée aujourd'hui continue de mener au même contenu.
- **Mesures :** les cotes des pages priment sur le PDF du logement. Le PDF sert à placer les pièces les unes par
  rapport aux autres. Le nom du propriétaire et l'adresse, qui y figurent, n'apparaissent nulle part sur le site.
- **Noms des pièces :** on garde ceux du site, pas ceux du PDF (dans le PDF, « Chambre 1 » est la cuisine, « Cuisine »
  la pièce ouest et « Séjour » le salon).
- **Blender :** les rendus se font en local (M1 Pro, Blender 5.2.2) ; la publication ne rend rien.
- **Concurrence :** une autre session travaille dans le dépôt. Voir la section « Migration », partie « Avec l'autre
  session ».

## Hors champ

- Les cases à cocher (actions, découpe, montage, achats) : « pour l'instant ».
- Une maquette 3D à tourner au doigt pour les autres pièces. Celle de la cuisine reste une page à part.
- Le rendu iso complet de l'appartement : seule la structure qui le permettra est prévue (repère commun dans
  `piece.py`).
- Le mode sombre.
- Les options d'exemple de la maquette (bois des meubles de l'entrée, couleur des montants des étagères). Seule la
  teinte de l'entrée est une vraie option ; les autres viendront à la demande.
- Une feuille d'impression commune : l'imprimable de la cuisine reste une page à part.
- La correction des écarts entre relevés (passage du salon 78 ou 82, plafond 250 ou 254,5, branche est du couloir).

## À éviter

- Réintroduire ce qui a été retiré :
  - « Lecture du plan » et « Lecture de la coupe » ;
  - « Copier la liste » ;
  - le plan de repérage dans le menu ;
  - le double titre sur mobile ;
  - « À venir » ;
  - les descriptions d'images à l'écran ;
  - l'onglet Historique ;
  - le quadrillage du fond.
- Une page dont la navigation diffère des autres.
- Perdre du contenu pendant la migration, ou casser un lien publié.
- Des variantes dont les murs ou les caméras ne tombent pas au même endroit.
- Des dimensions écrites en dur dans les textes.
- L'allure générique d'une page générée :
  - police à chasse fixe pour les chiffres ;
  - points médians ;
  - étiquettes en capitales ;
  - flèches ajoutées aux liens.

## Ce que le client a décidé (13/11/2026)

- **Vues :**
  - une vue par écran, en onglets ;
  - Plan d'abord et Explication en dernier ;
  - un document s'ouvre sur son plan.
- **Barre du haut :** sur deux lignes. La version sur une seule ligne, et l'ancienne barre, ont été refusées.
- **Menu de gauche :** repliable, avec des icônes, réduit par défaut, sans plan.
- **Mobile :** l'icône maison en haut à gauche, sans double titre ; iso et caméra disposés comme les coupes.
- **Retraits :**
  - pas de cases à cocher ;
  - pas d'onglet Historique ;
  - pas de « Copier la liste » ;
  - pas de « Lecture de la coupe » ;
  - pas de « À venir » ;
  - pas de descriptions d'images à l'écran ;
  - des panneaux concis.
- **« Personnaliser » générique :** chaque document déclare ses options.
- **Variantes :** elles partagent les caméras de la pièce ; les murs tombent au même endroit.
- **Comparaison :**
  - « Comparer » à côté du choix de variante, avec la base et la variante comparée ;
  - l'adresse partageable ;
  - les outils immobiles ;
  - les noms en bas de la scène ;
  - « pas d'équivalent » quand il manque une vue.
- **Zoom :** sur iso et caméra, comme sur le plan et les coupes.
- **Accueil :** le plan de l'appartement seul ; implantation tirée du PDF, cotes tirées des pages, 90 × 104 gardé.
- **Style :**
  - navigation en `#000000c7` (après un essai en vert sauge) ;
  - pas de mode sombre ;
  - pas de quadrillage ;
  - Fira Sans et Fira Sans Condensed ;
  - « quelque chose qui fasse moins Claude ».
- **« Coupes » et « Découpe » :** « Coupes » pour les pièces, « Découpe » (liste de débit) pour les meubles.
- **Organisation des fichiers :** approuvée telle quelle.
- **Migration et autre session :** commencer après le commit de l'autre session, geler chaque document pendant sa
  migration, fusionner après chaque document.
- **Versions figées :** en archive seulement, sans bouton dans la page ni comparaison avec la version en cours.

## Choix de Claude, à confirmer en relisant

- La construction par générateurs Python avec gabarit commun (le client : « je te fais confiance »).
- Le schéma des adresses : une page par variante, l'état dans le fragment.
- La publication de `site/` par GitHub Action.
- Les onglets en bas sur mobile, et l'icône maison qui ouvre le menu (non commentés).
- Le masquage de la pastille de version sur mobile pendant une comparaison avec deux choix.
- L'ordre de migration : entrée, salon, salle de bain, cuisine, chambre.
- L'imprimable et la maquette 3D de la cuisine gardés comme pages à part.
- `achats/` et `reddit/` déplacés dans des dossiers voisins.
- Les onglets sans contenu grisés plutôt que masqués ; la chambre sans modèle 3D.
- Un numéro de version et une liste de changements par variante ; une page d'historique par document.
- La passerelle pour les pages non migrées, et une fusion dans `main` après chaque document.
- **Liste d'achats commune de la salle de bain :** elle devient une section « Les deux meubles », avec le total commun,
  dans la vue Achats de chaque meuble. Cela évite un document qui n'aurait que des achats.
- **`cuisine-couleurs.html` :** archivée telle quelle. En faire une option de la cuisine demanderait des rendus neutres
  et des masques pour toutes ses vues ; ce sera une demande à part.

## Laissé au constructeur

- Les noms des recettes `just`. Il faut garder `sync`, une recette par document et `apercu`.
- La structure interne de `site.js` et de `site.css`, et le découpage de `commun/`.
- La forme de l'empreinte du cache de rendu.
- Héberger les polices dans `site/` ou les charger depuis Google Fonts, comme la maquette.
- La traduction des anciennes ancres vers les vues.
- La résolution des rendus : 1600 × 1200 aujourd'hui, une image floue au-delà d'environ ×1,5 de zoom sur ordinateur,
  et 1280 × 960 mesuré à 20 s au lieu de 29 s en iso. Choisir en connaissant ce compromis.

## Vérification

Pour chaque document migré, dans un navigateur piloté, à 1440, 1100 et 390 px :
- toutes les vues, sans erreur de console ni fichier manquant, et rien ne déborde ;
- les onglets, la variante, la comparaison (aller-retour par l'adresse) et Personnaliser fonctionnent ;
- l'ancienne adresse redirige, avec son fragment ;
- la table de contenu « ancienne page → vues » est complète ;
- sans JavaScript, la page reste lisible.

Pour l'ensemble :
- le journal compte autant de changements que les listes `CHANGEMENTS` réunies ;
- une modification limitée à une vue ne relance que le rendu de cette vue ;
- le workflow publie, et le site est en ligne à la même adresse ;
- au moins un passage sur un vrai téléphone et dans Safari. La maquette n'a été testée que dans Chromium, avec le
  tactile simulé.
