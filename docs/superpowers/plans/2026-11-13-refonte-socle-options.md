# Socle des pages, lot S4 : options « choix » de « Personnaliser »

> **Pour les agents d'exécution :** skill requis : `superpowers:subagent-driven-development` (recommandé) ou
> `superpowers:executing-plans`, tâche par tâche. Les étapes se suivent par cases (`- [ ]`). Mode autonome : aucune
> question au client ; une décision imprévue se prend réversible et s'écrit dans le rapport de la tâche.

**But :** qu'un document déclare une option de type « choix » (Table, Siège, Bois du salon ; Taille, Portes,
transparence de la cuisine) et marque dans son HTML ce qui dépend de chaque valeur, sans aucun JS ni CSS propre à la
page ; l'entrée ne change pas d'un octet.

**Architecture :** l'état des options « choix » est un attribut `data-options="table:quotidien bois:chene"` sur
`<html>`, écrit par `commun/gabarit.py` aux valeurs d'origine (page lisible sans JS) puis tenu par `commun/site.js`.
Chaque élément qui dépend d'une valeur porte `data-si="<option>:<code> …"`. Le gabarit écrit, depuis la déclaration,
une règle CSS par valeur qui cache tout élément dont un jeton ne correspond pas à l'état. Les rendus par valeur sont
des `<img>` d'un même cadre, nommés par `commun.blocs.rendu(…, valeur=…)`.

**Pile :** Python 3 (bibliothèque standard), pytest par `uv`, HTML et CSS statiques, `playwright-cli`.

**Spec :** `docs/superpowers/specs/2026-11-13-refonte-site-design.md` (objectif 3 « Option », objectif 4, « Contraintes »,
« À éviter », « Vérification »). Maquette : `/Users/nvi/code/work/personal/plans/maquette/app.html` (feuille
« Personnaliser », l. 1080-1112 ; boutons `.choix-opt`). Part de l'état d'après les lots S1 et S2
(`docs/superpowers/plans/2026-11-13-refonte-socle-blocs.md`).

Worktree : `/Users/nvi/code/work/personal/plan-wt/socle`, branche `refonte-socle`. Toute commande commence par
`cd /Users/nvi/code/work/personal/plan-wt/socle && …` (noté `WT`).

## Contraintes globales

- **Critère d'octets (tâches 1 à 3) :** `cd WT && python3 site.py && git status --short site/entree` ne sort aucune
  ligne ; puis toujours `git checkout -- site && git clean -fdq site`. `site/` n'est jamais commité ici. Un document
  sans option « choix » donne la même page qu'avant, à l'octet : aucun champ nouveau dans le JSON `#options`, rien de
  nouveau dans `<html>` ni dans `<head>`.
- **Tests :** `cd WT && uv run -q --no-project --with pytest pytest -q tests` passe à la fin de chaque tâche.
- **Navigateur :** `cd WT && PORT=<p> SESSION=refonte-socle-<n> tests/navigateur/lancer.sh tests/navigateur/<script>.js`,
  ports 8826 à 8829 et sessions `refonte-socle-6` à `refonte-socle-9` pour ce lot. Jamais `close-all` ni `kill-all`,
  jamais la session `prod`, jamais les ports 8800 et 8811.
- **Intouchables :** `pieces/entree/piece.py`, `pieces/entree/amenagement/document.py`, `victor.py`, `rendu.py`,
  `3d/rendu.py`, `commun/rendu_cache.py`, `tests/test_rendu_cache.py`. Aucun fichier de `pieces/` ne change dans ce lot.
- **Jetons d'état :** identifiant d'option « choix » `^[a-z][a-z0-9-]*$`, code de valeur `^[a-z0-9][a-z0-9-]*$` ; un
  jeton s'écrit `<id>:<code>` ; plusieurs jetons sur un élément, séparés par une espace, valent « et ». Un élément ne
  porte qu'un jeton par option.
- **Règle CSS générée, exacte**, une par valeur de chaque option « choix », dans l'ordre de déclaration :
  `html:not([data-options~="<id>:<code>"]) [data-si~="<id>:<code>"]{display:none!important}`.
- **Textes exacts :** « Pas encore rendu : les rendus ne montrent pas ce choix. » (panneau, valeur `rendue=False`) ;
  « <nom de la valeur> : pas encore rendu, image en <nom de la valeur d'origine> » (scène, image absente pour une
  valeur). Inchangés : « Personnaliser », « Valeurs d'origine », « <n> option(s) modifiée(s) », « Pas encore rendu ».
- **Mémoire :** `localStorage`, clé `plans:<pièce>/<document>:<id>`, valeur JSON du code (celle des nuanciers
  aujourd'hui) ; tout accès dans un try/catch.
- **Style :** français ; pas de point médian (U+00B7), pas de police à chasse fixe, pas de capitales, pas de mode sombre,
  pas de flèche ajoutée aux liens ; jetons de `site.css` seulement. CSS : règles ajoutées à la fin de
  `commun/site.css`, aucune règle existante modifiée.
- **Nuanciers :** comportement inchangé ; le code de `site.js` qui les sert garde ses chaînes à l'identique.
- **Git :** commits petits, en français, sur `refonte-socle`, terminés par la ligne `Co-Authored-By` de la session ;
  pas de `git push`, pas de fusion ; `git status` propre en fin de tâche.
- **Dépendance S1 :** chaque nom de `commun/blocs.py` cité ici (`Zone`, `zones_svg`, `_modeles`, `Rendu`, `rendu`,
  `figure_rendu`, `vue_iso`, `vue_plan`) est **à vérifier contre le code réel au lancement de la tâche** : s'il a
  changé, garder la signature réelle et ajouter seulement ce que ce plan ajoute.

## Ce que les deux pages demandent

| Réglage (inventaire) | Effet du modèle qui le couvre |
|---|---|
| Salon, Table : quotidien ou ouverte, plan et quatre coupes en deux versions | `<g data-si>` dans un seul SVG par dessin (les deux versions d'une coupe ont la même viewBox) |
| Salon, Table : table, table basse, siège à deux emprises | deux `Zone` de même `id`, `si` différent ; fiche par `<template data-si>` |
| Salon, Siège : DYVLINGE ou chilienne, plan et coupes A, C, D, combiné à Table (`c<cfg> adyv`) | jetons combinés `table:quotidien siege:dyvlinge` |
| Salon, Déco : masquée ou affichée, plan et coupes | `<g data-si="deco:affichee">` |
| Salon, Bois : chêne ou noyer, deux images par coin iso | `vue_iso(…, option=BOIS)` ; `principale-iso_se-noyer.jpg` |
| Salon, rendus figés (table du quotidien, DYVLINGE, déco) | `Valeur(rendue=False)` et la portée en une ligne |
| Cuisine, Taille : 1,75 m, 1,80 m, masquée (règles `data-t`) | `<g data-si="taille:175">`, `taille:180` ; « masquée » ne montre aucune règle |
| Cuisine, Taille masquée : la coupe reprend sa largeur (`data-vb0`) | **hors modèle** : changement de viewBox |
| Cuisine, Portes : entrée (2 états), cellier (3 états), groupes `.vt` | deux options, `porte-entree` et `porte-cellier`, un `<g data-si>` par état |
| Cuisine, transparence de la porte du cellier (coupe C, style `.trp`, étiquettes `.trp-lbl`) | les deux dessins de la porte, chacun marqué ; les étiquettes marquées `transparence:oui` |
| Cuisine, Jour/Nuit | pas une option : élément `so-nuit` de l'Iso (décision de la page) |
| Les deux : boutons posés au-dessus des dessins | le panneau seul (spec : « Personnaliser » générique) |

## Décisions

- Ruling : état sur `<html data-options>`, éléments `data-si`, règles CSS générées dans un `<style>` de tête — le CSS
  ne sait pas comparer deux attributs, et `css_dessins` refuse toute règle visant `html` ; les règles sortent de la
  déclaration, pas de la page — si faux : déplacer les règles dans `dessins.css`.
- Ruling : `!important` dans la règle générée — l'état doit l'emporter sur le CSS des dessins (`.d-cuisine .vt .ouv`) —
  si faux : retirer le mot.
- Ruling : un script en ligne de tête (pages à option « choix » seulement) pose l'état mémorisé avant toute feuille —
  sans lui, la table ouverte clignote en quotidien au chargement — coût : trois lignes qui doublent la lecture de `memo`.
- Ruling : on marque des éléments à l'intérieur d'un `<svg>`, jamais un `<svg>` enfant direct d'un `.element` —
  `dessin()` lit la viewBox et `getScreenCTM()` du premier SVG, nuls s'il est caché — si faux : rendre `dessin()`
  sensible au SVG visible.
- Ruling : un rendu par valeur = un `<img data-si>` par valeur dans le même `figure.cadre` ; une valeur sans image
  reprend l'image d'origine et une note — le zoom pilote un seul cadre — si faux : un cadre par valeur et un
  contrôleur par cadre.
- Ruling : nommage `<variante>-<clé>-<code>.jpg`, sans suffixe pour la valeur d'origine — les images existantes
  gardent leur nom — si faux : renommer les images d'origine.
- Ruling : champ `Valeur.rendue: bool = True` ; `False` fait dire au panneau « Pas encore rendu : les rendus ne
  montrent pas ce choix. » ; la portée dit le reste — spec « elles le disent » — si faux : un texte par valeur.
- Ruling : `Valeur.couleur` prend le défaut `""` ; pour un choix, pastille de couleur seulement si `couleur` ; pas de
  ligne `.info` — maquette (`.choix-opt`, pas d'info) — si faux : rendre la ligne.
- Ruling : JSON `#options` : la clé `rendue` n'est écrite que si elle vaut `false` — critère d'octets — si faux : nul.
- Ruling : une option « choix » n'a ni `css` ni `filtre` (refusé) — aucun réglage des inventaires n'en demande — si
  faux : lever le refus.
- Ruling : Portes de la cuisine en deux options — un élément ne porte qu'un jeton par option, et les deux portes
  bougent séparément — coût : deux sections dans le panneau.
- Ruling : le document d'essai gagne une zone `table` visible ; `comparaison.js` compte deux zones au lieu d'une — si
  faux : nul.

## Points d'attention

1. Option changée pendant qu'une fiche de meuble est ouverte : la fiche suit la nouvelle emprise. Tâche 3.
2. Zone au clavier : la zone cachée n'est pas atteinte par Tab (`display:none`). Tâche 3.
3. Valeur mémorisée inconnue ou stockage refusé : valeur d'origine, y compris dans le script de tête. Tâches 1 et 3.
4. Comparaison : le clone suit l'état (dessin et image). Tâche 3.
5. Jeton mal écrit dans une page (`table:pliee`) : erreur à la construction, pas un élément jamais montré. Tâche 1.

### Task 1 : Déclaration, validation et état par défaut dans la page

**Fichiers :** Modifier `commun/modele.py`, `commun/gabarit.py`, `tests/test_modele.py`, `tests/test_gabarit.py`.

**Interfaces produites :**

```python
# commun/modele.py
@dataclass
class Valeur: code: str; nom: str; couleur: str = ""; groupe: str = ""; note: str = ""; lien: str = ""; rendue: bool = True
TYPES_OPTION = ("nuancier", "choix")
class Option:   # champs inchangés ; __post_init__ valide (ValueError, message qui cite l'id et la valeur fautive)
JETON = re.compile(r'\bdata-si="([^"]*)"')
def verifier(doc, vues) -> None   # + identifiants d'options uniques, + jetons data-si connus
# commun/gabarit.py
TETE_OPTIONS: str
def _options_json(options: Sequence[Option]) -> list[dict]
def _etat_choix(options: list[dict]) -> str        # "table:quotidien bois:chene", "" sans option choix
def _regles_choix(options: list[dict]) -> str      # règles jointes par "\n", "" sans option choix
def _script_choix(options: list[dict], cle: str) -> str   # "" sans option choix
```

- `Option.__post_init__` : `type` dans `TYPES_OPTION` ; `defaut` parmi les codes ; codes uniques ; pour un nuancier,
  chaque `couleur` vaut `#rrggbb` ; pour un choix, `id` et codes suivent les motifs des contraintes globales,
  `css == ""` et `filtre is False`.
- `verifier` : deux options de même `id` refusées ; chaque jeton de `data-si` trouvé par `JETON` dans `Element.scene`,
  `Element.fiche` et `Vue.fiche` doit être `<id>:<code>` d'une option « choix » du document (message :
  `f"{doc.piece}/{doc.id} : jeton « {jeton} » inconnu dans la vue {cle}"`).
- `_options_json` : `dataclasses.asdict(o)` pour chaque option, la clé `rendue` retirée de chaque valeur où elle vaut
  `True` (ordre des clés inchangé). `page_document` l'emploie à la place de `[dataclasses.asdict(o) …]`.
- `_tete(titre, depuis, vues, dessins=False, options=(), cle="")` et `_page(…, dessins="", cle="")` : `page_document`
  passe `cle=f"{doc.piece}/{doc.id}"`. Avec au moins une option « choix », et seulement alors :
  `<html lang="fr" class="sans-js" data-options="{_etat_choix}">` ; juste après la ligne du script `TETE_JS`,
  `<script>{_script_choix}</script>\n` ; juste après la ligne du `<link>` de `commun/site.css`,
  `<style>{_regles_choix}</style>\n`.
- `TETE_OPTIONS` (copie exacte ; `_script_choix` rend `f"{TETE_OPTIONS}({_json(codes)},{_json(cle)})"` avec
  `codes = {id: [defaut, *codes des valeurs]}` dans l'ordre de déclaration) :
  ```python
  TETE_OPTIONS = ('(function(o,p){var h=document.documentElement,t=[];for(var i in o){var v=o[i][0];'
                  'try{var m=JSON.parse(localStorage.getItem("plans:"+p+":"+i));if(o[i].indexOf(m)>0)v=m}catch(e){}'
                  't.push(i+":"+v)}h.setAttribute("data-options",t.join(" "))})')
  ```

- [ ] **Étape 1 : tests d'abord.** `tests/test_modele.py` :
  - `test_option_type_inconnu` : `type="liste"` → `ValueError` qui cite « liste ».
  - `test_option_defaut_absent` et `test_option_codes_en_double` : `ValueError`.
  - `test_option_choix_identifiants` : id `"Table"`, code `"a b"`, code `"a:b"` → `ValueError` ; code `"175"` accepté.
  - `test_option_choix_sans_css_ni_filtre` : `css="--x"` ou `filtre=True` sur un choix → `ValueError`.
  - `test_nuancier_couleur` : un nuancier dont une valeur a `couleur=""` → `ValueError` ; une valeur de choix sans
    couleur est acceptée.
  - `test_verifier_options_en_double` ; `test_verifier_jetons` : `<g data-si="table:pliee">` dans une scène →
    `ValueError` qui cite `table:pliee` ; un jeton qui nomme un nuancier → `ValueError` ; même contrôle dans
    `Element.fiche` et `Vue.fiche` ; `data-si="table:ouverte siege:chil"` valide passe.

  `tests/test_gabarit.py` (une option locale `LAMPE = Option("lampe", "Lampe", ("plafond",), "choix", "eteinte",
  (Valeur("allumee", "Allumée", rendue=False), Valeur("eteinte", "Éteinte")), "Visible sur le plan.")`, ajoutée par
  `dataclasses.replace(DOC, options=DOC.options + (LAMPE,))`) :
  - `test_choix_etat_par_defaut` : `"lampe:eteinte"` parmi les mots de `data-options` de `<html>`.
  - `test_choix_regles` : le `<style>` de `<head>` vient après le `<link>` de `site.css` et contient, à l'octet,
    `html:not([data-options~="lampe:allumee"]) [data-si~="lampe:allumee"]{display:none!important}` et la règle de
    `lampe:eteinte`.
  - `test_choix_script_de_tete` : un second `<script>` sans `src`, avant le premier `<link>`, contient
    `"plans:"`, `"lampe": ["eteinte", "allumee", "eteinte"]` et `"essai/amenagement"`.
  - `test_choix_json` : dans `#options`, la valeur `allumee` a `"rendue": false`, la valeur `eteinte` n'a pas de clé
    `rendue`.
  - `test_sans_choix_rien_de_neuf` : document à la seule option `TEINTE` → pas de `data-options=`, pas de
    `data-si~=`, un seul `<script>` sans `src` ; `_json(page, "options")[0]` égale `dataclasses.asdict(TEINTE)` sans
    les clés `rendue`.
  - `test_sans_js` : `startswith('<!doctype html>\n<html lang="fr" class="sans-js"')` (sans le `>`, pour admettre
    `data-options`).
- [ ] **Étape 2 :** `uv run -q --no-project --with pytest pytest -q tests/test_modele.py tests/test_gabarit.py` → échecs.
- [ ] **Étape 3 :** écrire le code ; les tests passent ; toute la suite passe.
- [ ] **Étape 4 :** critère d'octets (aucune ligne) ; remettre `site/`.
- [ ] **Étape 5 :** commit « Options « choix » : déclaration, validation et état par défaut dans la page ».

### Task 2 : Blocs : zones, rendus et nommage selon une valeur

**Fichiers :** Modifier `commun/blocs.py`, `tests/test_blocs.py`.

**Interfaces** (consomme `Option`, `Valeur` de la tâche 1 ; signatures de S1 à vérifier contre le code réel) :

```python
def rendu(dossier: Path, variante: str, cle: str, valeur: str = "") -> Rendu
#   nom = (f"{variante}-{cle}" si variante, sinon cle) + (f"-{valeur}" si valeur)
def jeton(option: Option, code: str) -> str        # "bois:noyer" ; ValueError si option non « choix » ou code inconnu
def si(*jetons: str) -> str                        # ' data-si="a:b c:d"' ; "" sans jeton
class Zone: …; iso: str = ""; si: str = ""          # champ ajouté à la fin : jetons séparés par une espace
def rendus_choix(dossier: Path, variante: str, cle: str, option: Option) -> dict[str, Rendu]
#   {code: rendu(dossier, variante, cle, "" si code == option.defaut sinon code)}, dans l'ordre des valeurs
def figure_choix(rendus: Mapping[str, Rendu], option: Option, alt: str, filtre: str = "") -> str
def vue_iso(…, vide: str = "Pas encore rendu", option: Option | None = None) -> Vue   # paramètre ajouté à la fin
```

- `zones_svg` : avec `z.si`, ` data-si="{si}"` juste après `data-meuble="{id}"` ; sans, chaîne inchangée.
  `_modeles` : même attribut, à la même place, sur le `<template>`.
- `figure_choix` : `""` si le rendu d'origine n'existe pas. Sinon `<figure class="cadre rendu">`, puis pour chaque
  valeur `v`, `r = rendus[v.code]` s'il existe, sinon le rendu d'origine : `<img data-si="{id}:{code}" src="{r.image}"
  alt="{a}" draggable="false">` (`a` = `alt` pour la valeur d'origine ou une image reprise, `f"{alt}, {v.nom}"` sinon,
  échappé), suivie, si `filtre`, du calque de `figure_rendu` avec le même `data-si` placé avant `src` ; puis
  `</figure>` ; puis, pour chaque valeur sans image, `<p class="note-rendu" data-si="{id}:{code}">{v.nom} : pas encore
  rendu, image en {nom d'origine}</p>`.
- `vue_iso` avec `option` : scène `figure_choix(rendus_choix(dossier, variante, f"iso_{k}", option), option, alt,
  filtre)` ; `actif` = rendu d'origine présent ; sans `option`, sortie inchangée.

- [ ] **Étape 1 : tests d'abord** (`BOIS = Option("bois", "Bois", ("meubles",), "choix", "chene", (Valeur("chene",
  "Chêne"), Valeur("noyer", "Noyer"), Valeur("frene", "Frêne", rendue=False)), "Visible sur les rendus.")`) :
  - `test_rendu_valeur` : `rendu(tmp_path, "principale", "iso_se", "noyer").image ==
    "rendus/principale-iso_se-noyer.jpg"`, `masque == "rendus/principale-iso_se-noyer-masque.png"` ;
    `rendu(tmp_path, "", "iso_se", "noyer").image == "rendus/iso_se-noyer.jpg"` ; `valeur=""` : nom de S1.
  - `test_jeton_et_si` : `jeton(BOIS, "noyer") == "bois:noyer"` ; code inconnu ou option nuancier → `ValueError` ;
    `si("a:b", "c:d") == ' data-si="a:b c:d"'` ; `si() == ""`.
  - `test_zone_selon_valeur` : `Zone(…, si="table:ouverte")` → le `rect.zone` et le `template` portent
    `data-si="table:ouverte"` ; sans `si`, aucune chaîne `data-si` (le test de S1 sur les zones passe inchangé).
  - `test_rendus_choix` (`principale-iso_se.jpg`, `principale-iso_se-noyer.jpg` créés) : clés `chene`, `noyer`,
    `frene` ; `chene.image == "rendus/principale-iso_se.jpg"` ; `existe` vaut vrai, vrai, faux.
  - `test_figure_choix` : trois `img` sans `class`, `data-si` `bois:chene`, `bois:noyer`, `bois:frene` ; la source de
    `frene` est celle de `chene` ; alts `alt`, `f"{alt}, Noyer"`, `alt` ; un seul `p.note-rendu`, `data-si="bois:frene"`,
    texte « Frêne : pas encore rendu, image en Chêne » ; avec `filtre="teinte"`, trois `img.calque` aux mêmes
    `data-si` ; rendu d'origine absent → `""`.
  - `test_vue_iso_option` : avec `option=BOIS`, la scène du coin `se` contient `data-si="bois:noyer"` ; sans
    `option`, scène égale à celle de S1.
- [ ] **Étape 2 :** `uv run -q --no-project --with pytest pytest -q tests/test_blocs.py` → échecs.
- [ ] **Étape 3 :** écrire le code ; tous les tests passent ; critère d'octets ; remettre `site/`.
- [ ] **Étape 4 :** commit « Blocs : zones et rendus selon la valeur d'une option ».

### Task 3 : site.js et site.css ; document d'essai et options.js étendus

**Fichiers :** Modifier `commun/site.js`, `commun/site.css` (fin), `tests/fixtures/essai/document.py`,
`tests/navigateur/options.js`, `tests/navigateur/comparaison.js` (compte des zones), `tests/test_gabarit.py`
(`test_corps_et_donnees` : ids `["teinte", "table", "bois"]`).

**Interfaces :** consomme `Valeur(rendue)`, l'état `html[data-options]`, `data-si` (tâche 1), `Zone.si`, `zones_svg`,
`figure_choix`, `Rendu` (tâche 2). Produit dans `site.js` :

```js
const etatChoix = () => (racine.dataset.options || "").split(" ").filter(Boolean);
const selon = el => !el.dataset.si || el.dataset.si.split(/\s+/).filter(Boolean).every(t => etatChoix().includes(t));
function poserChoix(option, code)   // remplace le jeton "<id>:…" de html[data-options] sur place, l'ajoute s'il manque
```

- `appliquer` : pour `option.type === "choix"`, `poserChoix(option, v.code)` (avant la mémoire). Après un clic sur
  une valeur ou sur « Valeurs d'origine » : `if (courant) montrer(courant)` (la fiche du meuble suit).
- `montrerMeuble` : la zone est `zones.find(z => z.dataset.meuble === n && selon(z))`, le modèle
  `templates.find(t => t.dataset.meuble === n && selon(t))` ; `ici` seulement sur cette zone.
- `blocOption`, branche « choix » : bouton `<button type="button" data-v="{code}" aria-pressed="false">`, puis
  `<i style="background:{couleur}"></i>` seulement si `couleur`, puis le nom ; à la place de `<p class="info"></p>`,
  `<p class="remarque sans-rendu" hidden>Pas encore rendu : les rendus ne montrent pas ce choix.</p>`, puis la portée.
  `afficher()` : pour un choix, `.sans-rendu` montré si `v.rendue === false` ; branche nuancier inchangée.
- `site.css`, à la fin :
  ```css
  /* options « choix » : remarque du panneau, note d'une image absente (base à gauche, clone à droite) */
  .feuille .sans-rendu{margin:10px 0 0}
  .element > .note-rendu{position:absolute;left:12px;top:12px;z-index:1;margin:0;padding:4px 8px;border:1px solid var(--line);border-radius:4px;background:var(--panel);color:var(--muted);font:500 14px var(--ui);pointer-events:none}
  .element.b > .note-rendu{left:auto;right:12px}
  .sans-js .element > .note-rendu{position:static;display:inline-block;margin:0 0 8px}
  ```
- **Document d'essai** : `TABLE = Option("table", "Table", ("table",), "choix", "quotidien", (Valeur("quotidien",
  "Au quotidien"), Valeur("ouverte", "Ouverte", rendue=False)), "Visible sur le plan et les coupes ; les rendus
  montrent la table du quotidien.")` ; `BOIS = Option("bois", "Bois", ("meubles",), "choix", "chene",
  (Valeur("chene", "Chêne", "#B07A45"), Valeur("noyer", "Noyer", "#6B4630"), Valeur("frene", "Frêne", "#D9BF92",
  rendue=False)), "Visible sur les rendus ; le plan et les coupes ne changent pas.")` ;
  `options=(TEINTE, TABLE, BOIS)`. Plan de chaque variante, après `ZONE` : `<g data-si="table:quotidien"><rect
  class="table" x="70" y="38" width="15" height="8"/></g>`, la même en `table:ouverte` de largeur 25 (x 60),
  `<g data-si="table:ouverte bois:noyer"><circle class="combi" cx="92" cy="8" r="4"/></g>`, puis `zones_svg` de deux
  `Zone("table", "Table", …, si=…)` aux mêmes emprises ; dans `fiche` du plan, deux `<template data-meuble="table"
  data-si="…" data-titre="Table"><p class="cotes">15 cm</p></template>` (25 cm pour `ouverte`). Coupe A : dans son SVG,
  deux `<g data-si>` (quotidien, ouverte) ; dans sa fiche, `<p data-si="table:ouverte">Table ouverte.</p>`. Caméra :
  `RENDU` devient `figure_choix({…}, BOIS, "Depuis le banc", filtre="teinte")` sur des `Rendu` en data URI
  (`chene` : l'image grise actuelle ; `noyer` : même SVG, `fill=%27%23963%27` ; `frene` : `existe=False`), masque
  `MASQUE`. Si `scene.js` échoue à cause des nouvelles zones, déplacer les rectangles de la table, pas le script.

- [ ] **Étape 1 : tests d'abord**, `tests/navigateur/options.js`, après les essais du nuancier (même `lire`,
  `ouvrir`, `attendre` ; `vu = sel => …checkVisibility()`) :
  - origine : `data-options` de `<html>` = `"table:quotidien bois:chene"` ; `g[data-si="table:quotidien"]` vu,
    `g[data-si="table:ouverte"]` et `circle.combi` cachés ; `img[data-si="bois:chene"]:not(.calque)` vu en caméra.
  - panneau : sections `teinte`, `table`, `bois` dans l'ordre ; boutons de `table` sans `<i>`, ceux de `bois` avec ;
    aucune `.info` dans les sections de choix ; deux portées `.remarque` lues.
  - `ouverte` : pastille « 1 », `.sans-rendu` vue dans `table`, mémoire `plans:essai/amenagement:table` =
    `"ouverte"` ; plan : `table:ouverte` vu, quotidien caché ; fiche de la coupe A : « Table ouverte. » vu.
  - zone : cliquer la zone `table` visible → `#plan?k=table`, cotes « 25 cm », une seule `rect.zone.ici` ; repasser en
    `quotidien` fiche ouverte → « 15 cm » ; au clavier, Tab ne passe que par la zone visible.
  - combinaison : `ouverte` et `noyer` → `circle.combi` vu ; `noyer` seul → caché ; caméra : `img[data-si="bois:noyer"]`
    vu ; `frene` → `.note-rendu` « Frêne : pas encore rendu, image en Chêne » vue, `.sans-rendu` vue dans `bois`.
  - pastille : teinte `v2`, `ouverte`, `noyer` → « 3 » ; « Valeurs d'origine » → pastille cachée, état d'origine.
  - script de tête : `page.route("**/commun/site.js", r => r.abort())`, `table` mémorisée à `"ouverte"` → au
    chargement `data-options` = `"table:ouverte bois:chene"` et `table:ouverte` vu ; mémoire `"zzz"` → `quotidien`.
  - comparaison : `ouverte` et `noyer`, `#coupes?k=A&c=b` → dans `.element.b`, `table:ouverte` vu, quotidien caché ;
    `#camera?c=b` → `.element.b img[data-si="bois:noyer"]:not(.calque)` vu.
  - sans JavaScript (`browser().newContext({javaScriptEnabled: false})`, comme `entree.js`) : `table:quotidien` vu,
    `table:ouverte` caché, `img[data-si="bois:noyer"]` caché, aucune erreur.
  - stockage refusé (page privée existante) : choisir `ouverte` change le plan sans erreur.
  - 390 px : panneau à trois sections, aucun défilement horizontal.
  - essais du nuancier déjà écrits : dans `lire`, `choisi`, et dans le relevé du panneau, `valeurs`, se limitent à
    `section[data-o="teinte"]` (trois valeurs choisies à la fois sinon) ; leurs attentes ne changent pas.
- [ ] **Étape 2 :** document d'essai étendu ; `test_corps_et_donnees` ; dans `comparaison.js`, chaque `e.zones === 1`
  devient `e.zones === 2`. `PORT=8826 SESSION=refonte-socle-6 tests/navigateur/lancer.sh tests/navigateur/options.js`
  → échecs sur les choix seulement (le nuancier passe).
- [ ] **Étape 3 :** `site.js` et `site.css` ; `options.js` → `"ok": true`.
- [ ] **Étape 4 :** `comparaison.js` (8827, `refonte-socle-7`), `scene.js` (8828, `refonte-socle-8`), `navigation.js`
  (8829, `refonte-socle-9`), puis `redirections.js` (8826) → `"ok": true` chacun ; toute la suite pytest ; critère
  d'octets ; remettre `site/`.
- [ ] **Étape 5 :** captures à 1440 et 390 px du panneau ouvert et du plan en `ouverte`, regardées : pas d'élément noir
  hors de l'essai, pastilles et remarques lisibles.
- [ ] **Étape 6 :** commit « Personnaliser : options « choix » appliquées, mémorisées et comparées ».

### Task 4 : Mode d'emploi pour les agents de page

**Fichier :** créer `/Users/nvi/code/work/personal/plan/.superpowers/sdd/2026-11-13-refonte-pages/socle/rapport-options.md`
(hors dépôt, pas de commit), 60 lignes au plus, en français, sans point médian.

**Interfaces :** consomme tout ce que les tâches 1 à 3 produisent, lu dans le code commité (pas dans ce plan).

Contenu, dans cet ordre :
1. **Déclarer** : un exemple `Option(type="choix", …)` avec `Valeur(…, rendue=False)` et une portée en une ligne ;
   motifs des identifiants et des codes ; ni `css` ni `filtre` ; erreurs levées par `Option` et `verifier`.
2. **Marquer**, un exemple par effet : dessin (`<g{si(jeton(TABLE, "ouverte"))}>` dans le SVG, jamais sur un `<svg>`
   enfant direct, deux versions d'une coupe dans un seul SVG) ; fiche (`<p data-si>`) ; zones à deux emprises (deux
   `Zone` de même `id`, `si` différent) ; rendu (`vue_iso(…, option=BOIS)` ou `figure_choix`) ; options combinées
   (`si(jeton(TABLE, "quotidien"), jeton(SIEGE, "dyvlinge"))`) ; un style qui change selon la valeur (les deux
   dessins, chacun marqué).
3. **Nommer les rendus** : `rendu(dossier, variante, cle, valeur)`, `<variante>-<clé>-<code>.jpg`, rien pour la valeur
   d'origine ; une image absente donne la note de la scène ; le cache de rendu ne connaît pas les valeurs.
4. **Hors modèle** : viewBox selon une valeur (Taille masquée de la cuisine : garder la viewBox avec règle) ; un
   `<svg>` enfant direct marqué ; un élément montré pour deux valeurs d'une même option (l'écrire deux fois) ; CSS ou
   JS propre à la page ; une option qui dépend d'une autre.
5. **Ce que montre le document d'essai** (`tests/fixtures/essai/document.py`, `tests/navigateur/options.js`).

- [ ] **Étape 1 :** écrire chaque exemple de code dans un script de `/private/tmp/…/scratchpad`, l'exécuter depuis `WT`
  (`python3 -B <script>`) et coller dans le rapport la sortie réellement obtenue (HTML d'un `zones_svg`, d'une
  `figure_choix`, l'erreur de `verifier` sur `table:pliee`).
- [ ] **Étape 2 :** écrire le rapport ; `wc -l` ≤ 60 ; `grep -c "·"` = 0.
- [ ] **Étape 3 :** relire contre `commun/blocs.py`, `commun/modele.py`, `commun/gabarit.py` : chaque nom et chaque
  signature cités existent tels quels.
