# Refonte du site, chambre/amenagement : plan de travail

> **Pour les agents qui exécutent ce plan :** utiliser superpowers:subagent-driven-development (recommandé) ou
> superpowers:executing-plans pour l'exécuter tâche par tâche. Les étapes se cochent (`- [ ]`).

**But :** migrer `chambre-amenagement.html` (V2.1, écrite à la main) vers `chambre/amenagement/`, document
d'aménagement généré depuis un modèle Python qui n'existe pas encore : `pieces/chambre/piece.py` et
`pieces/chambre/amenagement/document.py`, écrits depuis la page.

**Architecture :**
- **Modèle :** la pièce (sol, murs, porte, fenêtre, placard, clim) dans `piece.py` ; les meubles, passages, zones,
  version et changements dans `document.py`, qui réexporte les constantes de la pièce (comme l'entrée).
- **Dessins :** le plan et les trois élévations sont **régénérés** depuis le modèle par `pieces/chambre/amenagement/dessin.py`
  (fonctions de `commun/dessin.py` et petites fonctions locales), et un test compare chaque dessin régénéré au dessin
  de l'ancienne page, figée dans `tests/fixtures/chambre/`, élément par élément, à l'arrondi près.
- **Vues :** `vues.py` assemble Plan (zones touchables), Coupes (trois élévations, « Position »), Iso et Caméra
  grisées, Explication, avec les blocs de `commun.blocs` ; `document.DOCUMENT` les déclare.
- **Bascule :** `site.py` passe de la `Passerelle` au `Document`, l'ancienne page devient une `Redirection`.

**Technologies :** Python 3.14 (bibliothèque standard), pytest par `just tests`, `playwright-cli` par
`tests/navigateur/lancer.sh`. Pas de Blender : la chambre n'a pas de modèle 3D.

**Spécification :** `docs/superpowers/specs/2026-11-13-refonte-site-design.md` (fait autorité). Consignes de la
migration, qui font loi : `/Users/nvi/code/work/personal/plan/.superpowers/sdd/2026-11-13-refonte-pages/consignes.md`
(noté `REGISTRE/consignes.md`). Inventaire de la page : `REGISTRE/chambre-amenagement/inventaire.md` (numéros de
ligne de `chambre-amenagement.html`, cités `l. N` plus bas). Mode d'emploi des blocs : `REGISTRE/socle/rapport.md`.
Modèle à imiter : `pieces/entree/`, `tests/test_entree.py`, `tests/navigateur/entree.js`.

## Global Constraints

Recopiées de la spec, des consignes et des contraintes globales du plan du socle (`docs/superpowers/plans/2026-11-13-refonte-socle-entree.md`, l. 45-121). Elles lient chaque tâche.

- **Sources :** les dimensions se calculent depuis les modèles, jamais en dur dans un texte nouveau, un dessin ni une
  fiche ; « les textes repris tels quels de l'ancienne page gardent ce qu'ils avaient ». `site/` n'est jamais modifié
  à la main, et n'est pas commité depuis cette branche (on le remet par `git checkout -- site && git clean -fdq site`).
- **Couleurs :** papier `#EEF0EC`, navigation `#000000c7`, repère « vous êtes ici » `#F2CF4A`. Les dessins n'utilisent
  que les jetons de `commun/site.css` (`--ink`, `--muted`, `--line`, `--panel`, `--wood`, `--water`, `--tri`,
  `--flow`, `--cab`, `--tall`, `--tech`, `--glass`) ; une couleur de l'ancienne page sans jeton du site s'écrit en
  littéral dans le CSS de la chambre (`--cook2` → `#7B5EA7`). Pas de mode sombre (aucun `prefers-color-scheme`), pas de
  quadrillage.
- **Polices :** Fira Sans (texte), Fira Sans Condensed (interface et cotes), chiffres tabulaires, données par
  `commun/site.css`. Le CSS de la chambre ne nomme aucune police (ni Archivo, ni JetBrains Mono, ni `monospace`).
- **Style :** pas de point médian nulle part (virgule à la place, y compris dans les étiquettes des dessins), pas
  d'étiquettes en capitales, pas de flèche ajoutée aux liens, pas de motif décoratif.
- **Vues d'un aménagement :** Plan, Coupes, Iso, Caméra, Explication ; s'ouvre sur Plan. Une vue sans contenu reste un
  onglet grisé.
- **Textes exacts :** « Touchez un meuble pour afficher sa fiche. », « Position », « Pas encore rendu »,
  « Sans objet », « Journal des changements ».
- **Jamais :** cases à cocher ; « Copier la liste » ; « À venir » ; « Lecture du plan » ; « Lecture de la coupe » ;
  description d'image affichée (texte alternatif seulement) ; onglet Historique ; sommaire ou barre propre à
  l'ancienne page ; bouton de version figée dans la page.
- **Rien ne se perd :** chaque section, dessin, tableau et note de l'ancienne page a sa place (tableau plus bas), ou
  est retiré par une décision de la spec ou des consignes. Dans le doute, le contenu va dans l'Explication.
- **Meubles du plan :** identifiants stables (`lit`, `chevet_ouest`…), jamais un rang ; emprise et cotes de la fiche
  tirées du modèle.
- **CSS des dessins :** `Document.css` porte toutes les règles des dessins ; chaque classe d'un dessin a sa règle.
- **Journal :** 5 changements de la chambre avant la bascule, 5 après.
- **Erreurs de l'ancienne page :** une erreur de fond se garde et se signale « Au client » ; la migration ne refait pas
  la conception.
- **Partagé :** dans `site.py` et le `justfile`, ne toucher que les lignes de la chambre. Aucun fichier de `commun/`,
  `tests/fixtures/essai/` ni `tests/navigateur/*.js` (sauf `chambre-amenagement.js`) n'est modifié par ce plan.
- **Tests :** `just tests` (`uv run -q --no-project --with pytest pytest -q tests`, 395 tests verts au départ).
  Un fichier seul : `uv run -q --no-project --with pytest pytest -q tests/test_chambre.py`.
- **Navigateur :** `PORT=8900 SESSION=refonte-chambre-amenagement-1 tests/navigateur/lancer.sh <script>` (ports
  8900-8909, sessions `refonte-chambre-amenagement-*`) ; jamais `close-all` ni `kill-all`, jamais la session `prod`,
  jamais les ports 8800 et 8811.
- **Git :** branche `refonte-chambre` seulement, commits petits en français finissant par
  `Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>` ; pas de push, pas de fusion.

## Décisions prises pour ce plan

Les rulings du registre (`REGISTRE/chambre-amenagement/progress.md`) s'appliquent tels quels : porte du couloir 67 ;
placard 164 utile et cote 171 du plan, toutes deux calculées (171 = 164 + cloison 7) ; lampe gardée sans fiche ;
chapô qui renvoie à l'historique ; coupes `est`, `sud`, `ouest` nommées « Mur est », « Mur sud », « Mur ouest » ;
placard hors du `SOL` ; une variante d'id vide, figée V1.2. Décisions ajoutées par ce plan, réversibles :

1. **Surface déclarée.** Fait vérifié : `commun/appartement.py` (`contours()`) remplace les cotes du contour de l'accueil
   par `SURFACE` dès que `pieces/<id>/piece.py` la donne, et l'entrée (`SURFACE = 8.1`) comme le salon (calculée du
   sol) la déclarent déjà. Le ruling dit alors de la déclarer : `SURFACE` est calculée du sol (102 524 cm², soit
   10,2524 m²), et l'accueil affiche « 10,3 m² » au lieu de « 441 × 251 » dès la tâche 1 (dès que `piece.py` existe,
   même avant la bascule). Le contour posé par `POSITION = (364, 112, 0)` est identique à celui d'`APPART`.
   Coût si faux : retirer une constante.
2. **Classe `rail` renommée `tringle`, pas `barre`.** Le ruling disait `barre`, mais `commun/site.css` l. 40, 93, 255
   stylent déjà `.barre` (la barre du haut, `header.barre`). `tringle` ne figure nulle part dans `site.css` ni `site.js`.
3. **Classe `app` renommée `filet`.** `commun/site.css` l. 38 pose `.app{display:grid;…;height:100dvh}` (l'enveloppe
   de la page) ; `height` est une propriété géométrique du `<rect>` SVG, et l'élévation est dessine ses vantaux en
   `rect.app` (l. 354-355).
4. **Classe `mf` renommée `passm`.** Le calque « Passages libres » de `site.css` (l. 194) masque `.pass`, `.passm`,
   `.passt` : sous `mf`, les points des passages resteraient affichés calque masqué.
5. **Quadrillage retiré.** Le `rect.tile` du plan (l. 250, motif `tl` de 30, l. 235) est le quadrillage du fond :
   spec, « À éviter » et « Ce que le client a décidé », « pas de quadrillage ».
6. **Marqueurs dans chaque dessin.** Les marqueurs `tk` (tick de cote) et `ar` (flèche) étaient dans un SVG caché commun
   à la page (l. 234-238). Chaque dessin porte ses `<defs>`, ids suffixés par son repère (`tk-plan`, `ar-est`…) : une
   même id dans quatre SVG serait invalide, et un marqueur défini dans une coupe masquée ne s'afficherait pas ailleurs.
7. **Trait « Position » d'une élévation = le mur regardé** (socle : « une élévation est une Coupe, son trait est le
   mur regardé ») : est `((441, 0), (441, 251))`, sud `((0, 251), (441, 251))`, ouest `((0, 0), (0, 251))`, et non les
   traits de l'inventaire §6.
8. **Lien `#verifier` du chapô** → `#explication` (le chapô est déjà dans cette vue ; le fragment `#<vue>` ne sait pas
   viser une section). Lien `#changements` → `historique.html`, et la phrase devient « L'historique est sur sa propre
   page (<a href="historique.html">Changements</a>). » (seul « en fin de document » change, selon le ruling).
9. **Zones du plan :** cinq zones sans recouvrement : `lit` (carte ①), `chevet_ouest` et `chevet_est` (carte ②),
   `commodes` (plan et commodes, du nu nord de la commode nord au mur sud, carte ③), `niche` (niche, joue et patères,
   du plan à la commode nord, carte ④). La carte « Pantalons : autres solutions » montre la niche ; « Circulation » n'a
   pas de meuble. La tête de lit est dans la fiche du lit (même carte).
10. **Textes repris tels quels** (chapô, six cartes, sept points, quatre textes sous les dessins) : écrits en
    littéral dans `vues.py` et `dessin.py`, et un test les confronte à la page figée. Les chiffres clés, les étiquettes
    des dessins, les cotes et les passages sont calculés du modèle.
11. **Légende reprise telle quelle**, pastille « Lit » en `.bed` comprise (le plan dessine le lit en `.mat` et
    `.duvet` : écart de l'ancienne page, gardé, à signaler « Au client »).
12. **Pas de note « Repère » ni de liens « Ouvrir le plan » dans l'Explication** : l'ancienne page n'en avait pas.

« Au client » (à reporter dans le rapport final) : porte 67 contre 71 dans l'entrée ; placard 164 ou 171 ; surface
affichée à l'accueil ; vantaux de la fenêtre de 73 en plan et 67 en élévation (gardés, écart de fond) ; pastille « Lit »
de la légende ; lampe au centre du lit sans texte ; « 75 » mesuré au plan (débord de 2), pas à la façade des commodes.

## Review Focus

1. **Plusieurs SVG dans une page qui partagent une id** (marqueurs `tk`, `ar`) : l'id résolue serait celle d'un dessin
   masqué et les ticks des cotes disparaîtraient. Test en tâche 4 : toutes les `id` des scènes et fiches de la page
   sont uniques.
2. **Une classe de dessin qui est aussi une classe de mise en page du site** (`app`, `rail`, `barre`, `vue`, `scene`) :
   le site la met en page à sa façon. Test en tâche 4 : aucune classe d'un dessin n'est dans la liste
   `{"app", "rail", "barre", "contenu", "vue", "scene", "fiche"}`.
3. **Un calque masqué qui laisse des restes** (points des passages restés affichés) : test en tâche 2, les points
   des passages (`circle` de rayon 1,3) ne portent que `passm`, que le calque « Passages libres » masque.
4. **Une ancienne adresse avec une ancre inconnue, sans ancre, ou `#changements`** : vue Plan, Plan, historique.
   Test Python en tâche 5 (`_traduire`), et vérification au navigateur.
5. **Un lien relatif de l'Explication vers une page que rien ne génère** : seuls `historique.html` et des fragments
   `#…` sont permis. Test en tâche 4.

---

## Ancienne page → vues

Relu sur `chambre-amenagement.html` (V2.1, 504 lignes) à la branche `refonte`. La page redirige vers
`chambre/amenagement/` (`REDIRECTIONS` de `site.py`). Seuls deux `h2` ont une ancre (`verifier`, `changements`) ; les
slugs `plan-a-l-echelle`, `elevations`, `principe` n'ont jamais existé, mais sont acceptés par prudence (inventaire §8).

| Section de l'ancienne page (lignes) | Ancre | Devient | Retiré, et décision qui le retire |
|---|---|---|---|
| En-tête `.ph` : « ← Plans » et titre (229-232) | | Menu de gauche, icône maison sur mobile ; barre du haut | La barre : « sommaire et barres propres à l'ancienne page » |
| Surtitre « Chambre · V2.1 · plan et élévations » et `h1` (239-240) | | Barre du haut : Chambre › Aménagement, pastille V2.1 | Le surtitre en capitales et police à chasse fixe : « Style » |
| Chapô (241), liens `#verifier` et `#changements` | | Explication : chapô ; liens vers `#explication` et `historique.html` (décision 8) | |
| Chiffres clés (242) : 241 × 42, 3 + 6, 75, 47 | | Explication : chiffres, calculés du modèle | |
| Plan à l'échelle : dessin (244-343) | `plan-a-l-echelle` → `plan` | Plan : dessin régénéré dans la scène, cinq meubles touchables, calques | Le quadrillage `rect.tile` : « pas de quadrillage » (décision 5) |
| Plan : texte sous le dessin (343) | | Texte alternatif du plan | Le texte à l'écran : « pas de descriptions d'images à l'écran » |
| Légende du plan (344) | | Plan : légende dans la fiche | |
| Élévations : mur est (347-409) | `elevations` → `coupes` | Coupes, `k=est`, « Mur est », dessin régénéré, « Position » | |
| Élévations : mur sud (410-453) | | Coupes, `k=sud`, « Mur sud » | |
| Élévations : mur ouest (454-472) | | Coupes, `k=ouest`, « Mur ouest » | |
| Texte sous chaque élévation (409, 453, 472) | | Texte alternatif de chaque élévation | Le texte à l'écran, même décision |
| Principe : six cartes (474-482) | `principe` → `explication` | Explication, « Principe », « Montrer sur le plan » pour les cinq qui ont un meuble ; cartes ① à ④ dans la fiche de leur meuble | |
| Points à vérifier : sept puces (484-493) | `verifier` → `explication` | Explication, « Points à vérifier », une liste sans cases | |
| Changements : tableau de cinq lignes (495-501) | `changements` → `historique.html` | `historique.html` (version figée V1.2, puis les cinq changements) et `journal.html` | Le tableau dans une vue : « Le tableau des changements va dans l'historique et le journal » |
| Définitions SVG communes (234-238) | | Marqueurs `tk` et `ar` dans les `<defs>` de chaque dessin (décision 6) | Le motif `tl` du quadrillage (décision 5) |
| CSS de la page (12-226) | | `dessin.CSS` : les règles des classes dessinées, sur les jetons du site | Mode sombre (19-32), capitales du surtitre, polices à chasse fixe : « Style » ; environ cent règles d'autres pages, sans classe dessinée |
| Vues Iso et Caméra | | Onglets grisés « Pas encore rendu » | Pas de modèle 3D (spec, « Cas connus : Chambre ») |
| Version figée V1.2 (`archive/chambre-amenagement-v1.2.html`) | | `Variante.figees`, lue depuis l'historique | |

Une ancre absente de ce tableau, ou pas d'ancre, ouvre la vue par défaut (Plan).

## Fichiers

- Create `tests/fixtures/chambre/chambre-amenagement.html` : copie exacte de `git show refonte:chambre-amenagement.html`,
  seule référence des dessins, textes et changements une fois la page racine supprimée.
- Create `pieces/chambre/__init__.py`, `pieces/chambre/amenagement/__init__.py` (vides).
- Create `pieces/chambre/piece.py` : la pièce, données seulement.
- Create `pieces/chambre/amenagement/document.py` : meubles, passages, zones, version, changements, `DOCUMENT`.
- Create `pieces/chambre/amenagement/dessin.py` : plan, trois élévations, légende, `CSS`, `ALTS`.
- Create `pieces/chambre/amenagement/vues.py` : `vues(variante)`, textes de l'Explication.
- Create `tests/test_chambre.py` (une section par tâche, comme `tests/test_entree.py`).
- Create `tests/navigateur/chambre-amenagement.js`.
- Modify `site.py` (lignes de la chambre), `justfile` (recette `chambre`). Delete `chambre-amenagement.html`.
- `commun/` : aucun fichier touché.

---

### Task 1 : Page figée et modèle de la chambre

**Files:**
- Create: `tests/fixtures/chambre/chambre-amenagement.html`
- Create: `pieces/chambre/__init__.py`, `pieces/chambre/piece.py`, `pieces/chambre/amenagement/__init__.py`,
  `pieces/chambre/amenagement/document.py`
- Test: `tests/test_chambre.py`

**Interfaces:**
- Produces, `pieces/chambre/piece.py` (repère de la page : cm, x vers l'est depuis le nu du mur ouest, y vers le sud
  depuis le nu du mur nord, z depuis le sol fini ; l. 245, 343) :
  - `ID = "chambre"`, `NOM = "Chambre"`, `POSITION = (364, 112, 0)`, `H = 250`, `H_PORTE = 204`, `L, P = 441, 251` ;
  - `EP = dict(o=10, n=12, s=12, e=12)` (l. 259-264) ;
  - `DECROCHE = dict(x0=428, x1=441, y0=0, y1=10)` (l. 265) ;
  - `PLACARD = dict(x0=0, x1=47, y0=80, y1=251, cloison=7, jambage=5, porte=(92, 247), recouvrement=6)`
    (l. 251-258 ; deux vantaux coulissants de 80,5 qui se recouvrent de 6, rails à x 44,5 et 42,5) ;
  - `SOL` : liste de huit sommets tirée de `L`, `P`, `DECROCHE`, `PLACARD`, égale à
    `[(0, 0), (428, 0), (428, 10), (441, 10), (441, 251), (47, 251), (47, 80), (0, 80)]` ;
  - `SURFACE` : aire de `SOL` (formule du lacet, comme `pieces/salon/piece.py` l. 90) en m², 10,2524 ;
  - `PORTE = dict(nom="couloir", piece="Couloir", mur="o", face=0, a=3, b=70, type="battante", gond="a", vers="piece")`
    (67 de large, ruling ; charnière au nord) et `PORTES = [PORTE]` ;
  - `FENETRE = dict(y0=90, y1=232, allege=106, linteau=215, recouvrement=4, cadre=3, joint=2)` (mur est ; vantaux de
    73 en plan, l. 267-268, de 67 en élévation, l. 354-355 : deux dessins, deux largeurs, toutes deux tirées d'ici) ;
  - `CLIM = dict(x0=340, x1=428, y0=0, y1=22, z0=220, z1=250)` ;
  - `CAMERAS = ()`.
- Produces, `pieces/chambre/amenagement/document.py` (réexporte `from pieces.chambre.piece import …` toutes les
  constantes ci-dessus, `# noqa: F401`, comme `pieces/entree/amenagement/document.py` l. 10) :
  - `VERSION = "V2.1"`, `FIGEES_ANCIENNES = (("V1.2", "archive/chambre-amenagement-v1.2.html"),)` ;
  - `CHANGEMENTS` : cinq tuples `(version, date, texte)`, V2.1 en tête, textes exacts du tableau (l. 499) sans balises ;
  - meubles en dicts `x0, x1, y0, y1` (plan) et `z0`/`z1` (hauteurs), valeurs de l'inventaire §4.2 :
    `LIT = dict(x0=164, x1=324, y0=47, y1=247, z1=82, pieds=22, sommier=25, matelas=35)`,
    `TETE = dict(x0=160, x1=328, y0=247, y1=251, z0=50, z1=140)`, `COUETTE`, `OREILLERS`,
    `CHEVET_OUEST = dict(x0=117, x1=157, y0=216, y1=251, z1=70)`, `CHEVET_EST = dict(x0=329, x1=359, y0=216, y1=251, z1=70)`,
    `APPLIQUES` (x 137 et 344, h 140), `PRISES` (h 85),
    `PLAN = dict(x0=399, x1=441, y0=10, y1=251, z1=85, ep=3)` (sans `z0` : sa fiche dit « h 85 »),
    `COMMODE_NORD = dict(x0=401, x1=441, y0=91, y1=171, z1=82)`, `COMMODE_SUD` (y 171 → 251), `COMMODE` (tiroirs :
    séparations et poignées des élévations), `JOUE = dict(x0=401, x1=441, y0=10, y1=12, z1=82)`,
    `NICHE = dict(x0=401, x1=441, y0=12, y1=91, z1=82, barres=((413, 76), (429, 70)), pantalons=3)`,
    `PATERES = dict(x=439.5, y=(28, 48, 68), z=165)`, `TIROIR_OUVERT` (x0 = commode − 35, soit 366 → 401, y 95 → 167),
    `LAMPE = dict(cx=244, cy=149, r=5)` ;
  - `passages(M) -> list[dict]` : six `dict(a=(x, y), b=(x, y))` dont les bouts sont tirés des meubles de `M` (le
    module `document`, lu à l'appel : un meuble retouché par un test déplace son passage) (le pied du lit à x 250 de y 0 à
    `LIT["y0"]` ; placard → lit à y 180 ; placard → chevet ouest à y 226 ; lit → plan à y 70 ; lit → tiroir ouvert à
    y 185 ; chevet est → tiroir à y 233), dans l'ordre du plan (l. 319-342).
  - Une valeur qui ne sert qu'au tracé (décalage d'une étiquette, position d'un pantalon, cadrage) n'est pas du modèle :
    elle va en constante nommée de `dessin.py` (tâches 2 et 3).

- [ ] **Step 1 : Figer l'ancienne page**

```bash
cd /Users/nvi/code/work/personal/plan-wt/chambre && mkdir -p tests/fixtures/chambre \
  && git show refonte:chambre-amenagement.html > tests/fixtures/chambre/chambre-amenagement.html \
  && git show refonte:chambre-amenagement.html | cmp - tests/fixtures/chambre/chambre-amenagement.html && echo identique
```
Expected: `identique`.

- [ ] **Step 2 : Écrire les tests du modèle** dans `tests/test_chambre.py`

```python
ANCIENNE = (RACINE / "tests/fixtures/chambre/chambre-amenagement.html").read_text(encoding="utf-8")

def test_piece():
    assert piece.SOL == [(0, 0), (428, 0), (428, 10), (441, 10), (441, 251), (47, 251), (47, 80), (0, 80)]
    assert math.isclose(piece.SURFACE, (441 * 251 - 47 * 171 - 13 * 10) / 1e4)
    assert (piece.H, piece.POSITION, piece.CAMERAS) == (250, (364, 112, 0), ())
    assert piece.PORTE["b"] - piece.PORTE["a"] == 67

def test_cotes_de_la_page():
    D = document
    assert D.PLAN["x1"] - D.PLAN["x0"] == 42 and D.PLAN["y1"] - D.PLAN["y0"] == 241
    assert D.PLAN["y1"] - D.PLAN["y0"] == 2 * 80 + (D.NICHE["y1"] - D.NICHE["y0"]) + (D.JOUE["y1"] - D.JOUE["y0"])
    assert D.NICHE["y1"] - D.NICHE["y0"] == 79
    assert (D.LIT["x0"] - D.PLACARD["x1"], D.L - D.LIT["x1"]) == (117, 117)
    assert D.PLACARD["y1"] - D.PLACARD["y0"] - D.PLACARD["cloison"] == 164
    assert D.PLACARD["porte"][1] - D.PLACARD["porte"][0] == 155
    assert [round(math.dist(p["a"], p["b"])) for p in D.passages(D)] == [47, 117, 70, 75, 42, 7]

def test_changements_de_la_page():
    assert [(c[0], c[1], c[2]) for c in document.CHANGEMENTS] == [
        (c.version, c.date, c.texte) for c in depuis_page(ANCIENNE)]
    assert len(document.CHANGEMENTS) == 5
    assert document.VERSION == version_depuis_page(ANCIENNE) == "V2.1"
    assert (RACINE / "site" / document.FIGEES_ANCIENNES[0][1]).is_file()

def test_accueil():
    chambre = {c.id: c for c in contours()}["chambre"]
    assert chambre.p == next(c.p for c in APPART if c.id == "chambre")
    assert chambre.cotes == "10,3 m²"
```
Imports : `math`, `RACINE` de `tests.outils`, `depuis_page`, `version_depuis_page` de `commun.journal`, `APPART`,
`contours` de `commun.appartement`, `piece` et `document` de `pieces.chambre`.

- [ ] **Step 3 : Lancer les tests, constater l'échec**

Run: `uv run -q --no-project --with pytest pytest -q tests/test_chambre.py`
Expected: FAIL, `ModuleNotFoundError: No module named 'pieces.chambre'`.

- [ ] **Step 4 : Écrire `piece.py` et `document.py`** (données seulement, en tête un commentaire sur le repère, comme
  `pieces/entree/piece.py` l. 1-6). Pas encore de `DOCUMENT` ni de `ZONES` (tâche 4).

- [ ] **Step 5 : Lancer les tests**

Run: `just tests`
Expected: tous verts (395 + 4).

- [ ] **Step 6 : Commit**

```bash
git add tests/fixtures/chambre tests/test_chambre.py pieces/chambre
git commit -m "Chambre : page V2.1 figée pour les tests, modèle de la pièce et des meubles écrit depuis la page

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
```

---

### Task 2 : Plan régénéré depuis le modèle

**Files:**
- Create: `pieces/chambre/amenagement/dessin.py`
- Test: `tests/test_chambre.py`

**Interfaces:**
- Consumes: le module `document` de la tâche 1 (tout dessin le reçoit en argument `M`, jamais en variable globale, pour
  qu'un test puisse le retoucher par `monkeypatch`).
- Produces, dans `dessin.py` :
  - `plan_svg(M, aria: str = "Plan de la chambre", zones: str = "") -> str` : `<svg class="plan" viewBox="-140 -70 640 370"
    role="group|img" aria-label="…">` (`group` si `zones`, comme l'entrée), puis ses `<defs>` (marqueurs `tk-plan`,
    `ar-plan`), puis les éléments dans l'ordre de l'ancienne page (l. 245-343), puis `zones` ;
  - `legende() -> str` : `<div class="legend">` des six pastilles (l. 344) ;
  - `ALTS: dict[str, str]` : `"plan"` → le texte sous le plan (l. 343), tel quel ;
  - `CSS: str` : règles des classes du plan et de la légende, sur le modèle de `dessin_principale.CSS` ;
  - fonctions locales de tracé : `_texte(x, y, html, cls, anchor="middle", extra="")` (contenu déjà en HTML, pour les
    `<tspan class="lblb">①</tspan>`), `_cote(a, b, label, t)` (un `<path class="dim" d="M… L…" marker-start
    marker-end="url(#tk-<k>)">` et son texte placé au point `t`, rotation si verticale, comme l. 311-318),
    `_passage(a, b)` (`<path class="pass">`, deux `<circle class="passm" r="1.3">`, le texte `passt` : à droite du
    trait vertical en `start`, au-dessus du trait horizontal, l. 319-342). `commun.dessin.rect`, `f`, `rot` servent
    tels quels ; un `style` en ligne de l'ancienne page (`fill-opacity:.22`, `stroke:none`) est gardé.

Écarts voulus avec l'ancien plan, appliqués par le test à la page figée avant comparaison (et seulement ceux-là) :
`rail` → `tringle`, `app` → `filet`, `mf` → `passm` (décisions 2 à 4) ; « · » → « , » dans les textes (étiquettes
l. 252, 281) ; `rect.tile` retiré (décision 5) ; balise `<svg>` racine comparée par son `viewBox` seulement ; `<defs>`
du nouveau dessin ignorées et `url(#tk-plan)` lu `url(#tk)` (décision 6) ; `rect.zone` ignorés. Couleurs : seulement
dans `CSS` (jetons du site, `#7B5EA7` pour l'ancien `--cook2`), aucune dans les éléments.

- [ ] **Step 1 : Écrire l'outil de comparaison et les tests du plan**

```python
def _elements(svg: str) -> list[tuple]:
    """Suite des balises ouvrantes (nom, attributs) et des textes non vides, dans l'ordre du document ; nombres des
    attributs arrondis à 0,1 et écrits sans « .0 » (`244.0` = `244`) ; `<defs>` et son contenu, `rect.zone` sautés ;
    la première balise, si c'est un <svg>, réduite à son viewBox ; `url(#tk-<k>)` et `url(#ar-<k>)` lus `url(#tk)`,
    `url(#ar)`. Lecture par `html.parser.HTMLParser`, comme `tests/outils.balises`."""

def _ancien(nom: str) -> str:
    """Le SVG `plan`, `est`, `sud` ou `ouest` de la page figée (les quatre `<div class="fig">`, dans cet ordre) ou sa
    légende (`legende`), avec les écarts voulus : rail → tringle, app → filet, mf → passm, « · » → « , », sans rect.tile."""

def _cap(nom: str) -> str:   # le texte de <p class="cap"> du dessin `nom`

def test_plan_regenere():
    assert _elements(dessin.plan_svg(document)) == _elements(_ancien("plan"))

def test_legende_reprise():
    assert _elements(dessin.legende()) == _elements(_ancien("legende"))

def test_plan_alt():
    assert dessin.ALTS["plan"] == _cap("plan")
    (svg,) = balises(dessin.plan_svg(document, aria=dessin.ALTS["plan"]), "svg")
    assert svg["aria-label"] == dessin.ALTS["plan"] and svg["role"] == "img"

@pytest.mark.parametrize("meuble,bord,valeur,attendus", [
    ("CHEVET_EST", "x1", 362, (">33 × 35<", ">4<")),        # chevet est élargi de 3 : étiquette et passage « 7 »
    ("LIT", "y0", 50, ("Lit 160 × 197", ">50<")),            # lit raccourci : étiquette et passage du pied
    ("PLAN", "x0", 396, ("Plan 241 × 45", ">72<"))])         # plan plus profond : étiquette et passage lit → plan
def test_plan_suit_le_modele(monkeypatch, meuble, bord, valeur, attendus):
    monkeypatch.setattr(document, meuble, {**getattr(document, meuble), bord: valeur})
    svg = re.sub(r"<tspan[^>]*>[^<]*</tspan>\s*", "", dessin.plan_svg(document))
    for attendu in attendus:
        assert attendu in svg

def test_calques_du_plan():
    svg = dessin.plan_svg(document)
    assert {c["class"] for c in balises(svg, "circle") if c.get("r") == "1.3"} == {"passm"}
    assert not balises(svg, "rect", classe="tile") and "·" not in svg
```
`plan_svg` lit les passages par `M.passages(M)` (tâche 1), jamais une liste calculée à l'import.

- [ ] **Step 2 : Lancer, constater l'échec**

Run: `uv run -q --no-project --with pytest pytest -q tests/test_chambre.py -k "plan or legende"`
Expected: FAIL, `ImportError` sur `pieces.chambre.amenagement.dessin`.

- [ ] **Step 3 : Écrire `dessin.py`** : `plan_svg`, `legende`, `ALTS["plan"]`, `CSS` du plan. Chaque nombre d'étiquette,
  de cote et de passage vient de `M` (« Placard existant, 164 » = longueur moins cloison ; cote « 171 » = longueur du
  placard ; « 394 » = `L - PLACARD["x1"]` ; « porte du placard 155 » ; « fenêtre coulissante 142 » ; « 40 × 35 »…).
  Règles CSS : celles des l. 72-225 de l'ancienne page pour chaque classe dessinée, `var(--cook2)` → `#7B5EA7`,
  `.dimt` et `.passt` sans `font-family`, `.tringle` = l'ancienne `.rail`, `.filet` = l'ancienne `.app`,
  `.passm{fill:var(--flow)}`, et les trois règles `.legend` de `dessin_principale.CSS`.

- [ ] **Step 4 : Lancer**

Run: `uv run -q --no-project --with pytest pytest -q tests/test_chambre.py`
Expected: PASS. Un écart restant se lit dans le diff de pytest (`-vv`) : le corriger dans le dessin, jamais en
ajoutant un écart voulu non listé ici.

- [ ] **Step 5 : Commit**

```bash
git add pieces/chambre/amenagement/dessin.py tests/test_chambre.py
git commit -m "Chambre : plan régénéré depuis le modèle, identique au dessin de la V2.1 hors écarts voulus

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
```

---

### Task 3 : Les trois élévations régénérées

**Files:**
- Modify: `pieces/chambre/amenagement/dessin.py`
- Test: `tests/test_chambre.py`

**Interfaces:**
- Consumes: `document` (tâche 1), `_texte`, `_cote` et `CSS` (tâche 2).
- Produces, dans `dessin.py` :
  - `elevation_est(M, aria: str = "") -> str`, `elevation_sud(M, aria: str = "") -> str`,
    `elevation_ouest(M, aria: str = "") -> str` : `<svg class="coupe" viewBox=… role="img" aria-label=…>`, ses
    `<defs>` (`tk-<k>`, `ar-<k>`), puis les éléments dans l'ordre de l'ancienne page ;
  - `ELEVATIONS: dict[str, tuple[str, Callable]]` : `{"est": ("Mur est", elevation_est), "sud": ("Mur sud", …),
    "ouest": ("Mur ouest", …)}`, dans cet ordre (celui de la page) ;
  - `ALTS["est"]`, `ALTS["sud"]`, `ALTS["ouest"]` : les textes sous les élévations (l. 409, 453, 472), tels quels.
- Repères des élévations (inventaire §3) : ordonnée SVG = `H - z` (sol à 250, plafond à 0) ; abscisse : est `u = y`
  (nord à gauche), sud `u = L - x` (est à gauche), ouest `u = P - y` (sud à gauche). `viewBox` : est et ouest
  `-35 -22 320 290`, sud `-45 -22 520 290` (cadrage, constantes de dessin).
- Écarts voulus : les mêmes que la tâche 2 (`rail`, `app`, `mf`, points médians des étiquettes l. 359, 388, 429, 462,
  `<defs>` et `url(#tk-…)`, `<svg>` racine par son `viewBox`, la classe `small` disparaît avec elle).

- [ ] **Step 1 : Écrire les tests**

```python
@pytest.mark.parametrize("k", ["est", "sud", "ouest"])
def test_elevation_regeneree(k):
    _, dessiner = dessin.ELEVATIONS[k]
    assert _elements(dessiner(document)) == _elements(_ancien(k))
    assert dessin.ALTS[k] == _cap(k)

def test_elevations_dans_l_ordre():
    assert [(k, nom) for k, (nom, _) in dessin.ELEVATIONS.items()] == [
        ("est", "Mur est"), ("sud", "Mur sud"), ("ouest", "Mur ouest")]

def test_elevations_suivent_le_modele(monkeypatch):
    monkeypatch.setattr(document, "PATERES", {**document.PATERES, "z": 170})
    assert "3 patères h 170" in dessin.elevation_est(document)
    monkeypatch.setattr(document, "CHEVET_OUEST", {**document.CHEVET_OUEST, "z1": 65})
    assert ">② h 65<" in re.sub(r"<tspan[^>]*>|</tspan>", "", dessin.elevation_sud(document))
```

- [ ] **Step 2 : Lancer, constater l'échec**

Run: `uv run -q --no-project --with pytest pytest -q tests/test_chambre.py -k elevation`
Expected: FAIL, `AttributeError: module … has no attribute 'ELEVATIONS'`.

- [ ] **Step 3 : Écrire les trois fonctions.** Étiquettes et cotes tirées de `M` : « plafond 250 » (`H`),
  « fenêtre coulissante 142, allège 106, linteau 215 », cotes 90 / 142 / 19 (bords de la fenêtre et `P`), « barres
  h 76 / 70 », « plan 241 × 42, h 85, 2 commodes 80 × 40 h 82 », « 3 patères h 165 », « plan h 85 », « Tête de lit
  murale h 140 », « matelas 35, dessus h 82 », « sommier 25 », « pieds 22 », « h 70 », « applique h 140 »,
  « prises h 85 », cotes 168, 140, 82, « placard existant, porte 155 ». Un tracé qui n'est pas sur sa cote (applique
  dessinée de z 135 à 143 pour « h 140 », poignées et pantalons) garde son tracé par une constante de dessin nommée ;
  la cote du texte reste celle du modèle. Ajouter à `CSS` les règles des classes des élévations (`bgwall`, `cloth`,
  `dark`, `el-ceil`, `floorl`, `tech`, `bed`, `plug`, `wcut`…).

- [ ] **Step 4 : Lancer**

Run: `uv run -q --no-project --with pytest pytest -q tests/test_chambre.py`
Expected: PASS.

- [ ] **Step 5 : Commit**

```bash
git add pieces/chambre/amenagement/dessin.py tests/test_chambre.py
git commit -m "Chambre : élévations est, sud et ouest régénérées depuis le modèle

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
```

---

### Task 4 : Vues et document

**Files:**
- Create: `pieces/chambre/amenagement/vues.py`
- Modify: `pieces/chambre/amenagement/document.py` (ajout de `ZONES` et `DOCUMENT`)
- Test: `tests/test_chambre.py`

**Interfaces:**
- Consumes: `dessin.plan_svg`, `dessin.legende`, `dessin.ELEVATIONS`, `dessin.ALTS`, `dessin.CSS` (tâches 2 et 3) ;
  `commun.blocs` : `Zone`, `zones_svg`, `cotes_meuble`, `vue_plan`, `Lieu`, `Coupe`, `vue_coupes`, `vue_iso`,
  `points_iso`, `vue_camera`, `Carte`, `tete`, `chiffres`, `principes`, `a_verifier`, `vue_lecture` (signatures dans
  `REGISTRE/socle/rapport.md`).
- Produces :
  - `document.ZONES` : tuple de dicts `dict(id=…, meuble="<NOM DU DICT>", carte=<rang>, coupe=<k>)`, un bord donné
    (`x0`…`y1`) remplaçant celui du meuble, comme l'entrée :
    `lit`/`LIT`/0/`sud` ; `chevet_ouest`/`CHEVET_OUEST`/1/`sud` ; `chevet_est`/`CHEVET_EST`/1/`sud` ;
    `commodes`/`PLAN`/2/`est` avec `y0=COMMODE_NORD["y0"]` ; `niche`/`NICHE`/3/`est` avec `x0=PLAN["x0"]`,
    `y0=PLAN["y0"]`.
  - `vues.CHAPO: str`, `vues.PRINCIPES: list[tuple[str, str]]` (six cartes, titre et texte HTML, l. 476-481),
    `vues.POINTS: list[str]` (sept puces HTML, l. 486-492), en littéral, tels quels (décision 10, chapô selon la
    décision 8).
  - `vues.LIEU = Lieu(piece.SOL, piece.PORTES, "Position dans la chambre")` ;
    `vues.TRAITS = {"est": ((441, 0), (441, 251)), "sud": ((0, 251), (441, 251)), "ouest": ((0, 0), (0, 251))}`, tirés
    de `L` et `P` (décision 7).
  - `vues.vues(variante: str) -> dict[str, Vue]` : `plan`, `coupes`, `iso`, `camera`, `explication`.
    - Plan : `Zone(id, titre, emprise, cotes_meuble(meuble), texte de la carte, coupe=…)` ; titre = titre de la carte,
      suivi de « , ouest » et « , est » pour les deux chevets ; svg = `plan_svg(document, aria=ALTS["plan"],
      zones=zones_svg(zones))`, légende = `dessin.legende()`.
    - Coupes : `Coupe(k, nom, f"Élévation du {nom.lower()}", scene=dessiner(document, aria=ALTS[k]), trait=TRAITS[k])`.
    - Iso : `vue_iso(RENDUS_SITE, "", LIEU, points_iso((-10, -12, 453, 263)))` ; Caméra :
      `vue_camera(RENDUS_SITE, "", LIEU, piece.CAMERAS)` ; `RENDUS_SITE` = `site/chambre/amenagement/rendus` (absent) :
      toutes deux vides, « Pas encore rendu ».
    - Explication : `vue_lecture("explication", tete(CHAPO) + chiffres(stats) + principes(cartes) +
      a_verifier(POINTS, titre="Points à vérifier"))` ; `cartes` : `Carte(titre, texte, meuble)` avec les meubles
      `lit`, `chevet_ouest`, `commodes`, `niche`, `niche`, `""` ; `stats`, calculés du modèle :
      `("241 × 42", "plan sur 2 commodes, h 85")`, `("3 + 6", "patères + pantalons")`,
      `("75", "entre le lit et le plan (cm)")`, `("47", "passage au pied du lit (cm)")`.
  - `document.DOCUMENT` : construit à la première lecture par `__getattr__` (comme l'entrée, l. 307-322, à cause de
    l'import circulaire avec `vues`) : `Document(piece="chambre", id="amenagement", nom="Aménagement",
    type="amenagement", variantes=(Variante("", "Principale", VERSION, changements, FIGEES_ANCIENNES),),
    generer=vues.vues, css=dessin.CSS)`.

- [ ] **Step 1 : Écrire les tests**

```python
V = lambda: vues.vues("")

def test_document():
    d = document.DOCUMENT
    assert (d.piece, d.id, d.nom, d.type) == ("chambre", "amenagement", "Aménagement", "amenagement")
    (var,) = d.variantes
    assert (var.id, var.version, len(var.changements), var.figees) == ("", "V2.1", 5, document.FIGEES_ANCIENNES)
    modele.verifier(d, d.generer(""))
    assert list(V()) == list(modele.VUES["amenagement"])

def test_zones_confrontees_a_leur_meuble():
    """Chaque zone : l'emprise de son meuble, sauf les bords qu'elle déclare ; sa fiche commence par sa longueur."""
    (e,) = V()["plan"].elements
    rects = balises(e.scene, "rect", classe="zone")
    assert [r["data-meuble"] for r in rects] == ["lit", "chevet_ouest", "chevet_est", "commodes", "niche"]
    for r, z in zip(rects, document.ZONES, strict=True):
        m = getattr(document, z["meuble"])
        x, y, l, h = (float(r[a]) for a in ("x", "y", "width", "height"))
        assert (x, y, x + l, y + h) == tuple(z.get(c, m[c]) for c in ("x0", "y0", "x1", "y1"))
        cotes = re.search(rf'<template data-meuble="{z["id"]}"[^>]*><p class="cotes">([^<]*)</p>', e.fiche)[1]
        assert unescape(cotes).startswith(f'{max(m["x1"] - m["x0"], m["y1"] - m["y0"]):g} × ')

def test_zone_suit_son_meuble(monkeypatch):
    monkeypatch.setattr(document, "CHEVET_EST", {**document.CHEVET_EST, "x0": 319})
    (e,) = V()["plan"].elements
    assert balises(e.scene, "rect", classe="zone", **{"data-meuble": "chevet_est"})[0]["width"] == "40"

def test_coupes():
    v = V()["coupes"]
    assert [(e.k, e.nom) for e in v.elements] == [("est", "Mur est"), ("sud", "Mur sud"), ("ouest", "Mur ouest")]
    assert [t["data-k"] for t in balises(v.fiche, "line", classe="sec")] == ["est", "sud", "ouest"]
    assert "Position" in v.fiche and v.outils == ("zoom", "mesure")
    for e in v.elements:
        assert balises(e.scene, "svg")[0]["aria-label"] == dessin.ALTS[e.k]

def test_iso_et_camera_grisees():
    for cle in ("iso", "camera"):
        assert V()[cle].elements == [] and V()[cle].vide == "Pas encore rendu"

def test_explication_reprend_la_page():
    (e,) = V()["explication"].elements
    cartes = re.findall(r'<div class="card"><h3>(.*?)</h3><p>(.*?)</p></div>', ANCIENNE)
    assert vues.PRINCIPES == cartes and len(cartes) == 6
    assert vues.POINTS == re.findall(r"<li>(.*?)</li>", ANCIENNE.split('<div class="hyp">')[1].split("</ul>")[0])
    assert len(vues.POINTS) == 7
    pitch = re.search(r'<p class="pitch">(.*?)</p>', ANCIENNE)[1]
    attendu = (pitch.replace('href="#verifier"', 'href="#explication"')
               .replace("L'historique est en fin de document (<a href=\"#changements\">",
                        "L'historique est sur sa propre page (<a href=\"historique.html\">"))
    assert vues.CHAPO == attendu
    assert e.scene.count("Montrer sur le plan") == 5
    for valeur, libelle in (("241 × 42", "plan sur 2 commodes, h 85"), ("3 + 6", "patères + pantalons"),
                            ("75", "entre le lit et le plan (cm)"), ("47", "passage au pied du lit (cm)")):
        assert valeur in e.scene and libelle in e.scene

def test_liens_internes():
    for cle, v in V().items():
        for e in v.elements:
            for a in balises(e.scene + e.fiche + v.fiche, "a"):
                assert a["href"].startswith("#") or a["href"] == "historique.html", (cle, a["href"])

def test_aucun_interdit():
    tout = "".join(v.fiche + e.scene + e.fiche for v in V().values() for e in v.elements)
    for interdit in ("·", 'type="checkbox"', "Copier la liste", "À venir", "Lecture du plan", "Lecture de la coupe"):
        assert interdit not in tout
    visible = re.sub(r'aria-label="[^"]*"', "", tout)
    for texte in dessin.ALTS.values():
        assert escape(texte, quote=True) not in visible and texte not in visible

def test_ids_uniques_et_classes_du_site():
    tout = "".join(v.fiche + e.scene + e.fiche for v in V().values() for e in v.elements)
    ids = re.findall(r'\bid="([^"]+)"', tout)
    assert len(ids) == len(set(ids)), sorted(i for i in ids if ids.count(i) > 1)
    classes = {c for m in re.findall(r'class="([^"]+)"', tout) for c in m.split()}
    assert not classes & {"app", "rail", "barre", "contenu", "vue", "scene", "fiche"}

@pytest.mark.parametrize("cle", ["plan", "coupes"])
def test_chaque_classe_a_sa_regle(cle):
    """Chaque classe d'un dessin et de la légende a une règle dans dessins.css (filtré comme à la construction),
    sauf `zone` (site.css) ; une règle de site.css qui ne fait que masquer un calque ne compte pas."""
    from commun.construction import _dessins
    from commun.css_dessins import css_dessins
    css = css_dessins(document.DOCUMENT.css, _dessins(V()), ".d-chambre")
    v = V()[cle]
    # l'intérieur de chaque <svg> de scène, et la légende de la fiche (le reste de la fiche est au gabarit et aux blocs)
    morceaux = [e.scene.split(">", 1)[1] for e in v.elements] + re.findall(r'<div class="legend">.*?</div>', v.fiche, re.S)
    for html in morceaux:
        classes = {c for m in re.findall(r'class="([^"]+)"', html) for c in m.split()} - {"zone"}
        assert sorted(c for c in classes if not re.search(rf"\.{re.escape(c)}(?![\w-])", css)) == []

def test_css_sur_les_jetons_du_site():
    jetons = set(re.findall(r"(--[\w-]+):", (RACINE / "commun/site.css").read_text(encoding="utf-8")))
    assert set(re.findall(r"var\((--[\w-]+)\)", dessin.CSS)) <= jetons
    for interdit in ("font-family", "monospace", "Archivo", "JetBrains", "prefers-color-scheme", "--cook2"):
        assert interdit not in dessin.CSS
```
- [ ] **Step 2 : Lancer, constater l'échec**

Run: `uv run -q --no-project --with pytest pytest -q tests/test_chambre.py`
Expected: FAIL, `ModuleNotFoundError: No module named 'pieces.chambre.amenagement.vues'`.

- [ ] **Step 3 : Écrire `vues.py`, `ZONES` et `DOCUMENT`** selon les interfaces ci-dessus.

- [ ] **Step 4 : Lancer**

Run: `just tests`
Expected: tous verts.

- [ ] **Step 5 : Construire le document seul, sans bascule, pour le regarder**

Run: `python3 -c "from pieces.chambre.amenagement import document as d; v = d.DOCUMENT.generer(''); print({k: len(x.elements) for k, x in v.items()})"`
Expected: `{'plan': 1, 'coupes': 3, 'iso': 0, 'camera': 0, 'explication': 1}`.

- [ ] **Step 6 : Commit**

```bash
git add pieces/chambre/amenagement tests/test_chambre.py
git commit -m "Chambre : vues Plan, Coupes, Iso et Caméra grisées, Explication ; document déclaré

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
```

---

### Task 5 : Bascule

**Files:**
- Modify: `site.py` (l. 17 : import ; l. 38-40 : pièce Chambre ; `REDIRECTIONS` : une entrée de plus et ses tables)
- Modify: `justfile` (une recette `chambre`, à la suite de `entree`)
- Delete: `chambre-amenagement.html`
- Create: `tests/navigateur/chambre-amenagement.js`
- Test: `tests/test_chambre.py`

**Interfaces:**
- Consumes: `document.DOCUMENT` (tâche 4), `commun.redirections.Redirection`, `tests.test_redirections._traduire`,
  `commun.journal.entrees`, `tests.outils.charger_site`.
- Produces, dans `site.py` :
  - `from pieces.chambre.amenagement import document as chambre_amenagement` ;
  - `Piece("chambre", "Chambre", (chambre_amenagement.DOCUMENT,))` ;
  - `ANCRES_CHAMBRE = {"verifier": "explication", "plan-a-l-echelle": "plan", "elevations": "coupes",
    "principe": "explication"}` (les trois derniers par prudence : inventaire §8) ;
  - `Redirection("chambre-amenagement.html", "chambre/amenagement/", ANCRES_CHAMBRE, (),
    {"changements": "chambre/amenagement/historique.html"})`.
- Produces, dans le `justfile` :
  ```
  # Chambre : reconstruit la page (site/chambre/amenagement/) depuis pieces/chambre/
  chambre:
      python3 site.py chambre/amenagement
  ```
  (aucune ancienne recette de la chambre à retirer : la page était écrite à la main ; pas de recette de rendu).

- [ ] **Step 1 : Écrire les tests de la bascule**

```python
def test_bascule():
    module = charger_site()
    (chambre,) = [p for p in module.SITE.pieces if p.id == "chambre"]
    assert chambre.documents == (document.DOCUMENT,)
    assert not (RACINE / "chambre-amenagement.html").exists()
    (r,) = [r for r in module.REDIRECTIONS if r.ancienne == "chambre-amenagement.html"]
    assert r.cible == "chambre/amenagement/"
    assert r.pages == {"changements": "chambre/amenagement/historique.html"}
    for ancre, fragment in (("verifier", "explication"), ("plan-a-l-echelle", "plan"), ("elevations", "coupes"),
                            ("principe", "explication"), ("inconnue", ""), ("", "")):
        assert _traduire(r, ancre) == fragment

def test_journal_apres_la_bascule():
    lignes = [e for e in entrees(charger_site().SITE, RACINE) if e.piece == "Chambre"]
    assert [(e.version, e.texte) for e in lignes] == [(c.version, c.texte) for c in depuis_page(ANCIENNE)]
    assert {e.lien for e in lignes} == {"chambre/amenagement/"} and {e.variante for e in lignes} == {None}
```

- [ ] **Step 2 : Lancer, constater l'échec**

Run: `uv run -q --no-project --with pytest pytest -q tests/test_chambre.py -k "bascule or journal"`
Expected: FAIL (la chambre est encore une `Passerelle`).

- [ ] **Step 3 : Modifier `site.py` et le `justfile`, puis `git rm chambre-amenagement.html`.** L'ancienne page ne cite
  aucun dossier d'images (seulement `favicon.svg` et `apple-touch-icon.png`, communs) : rien d'autre à supprimer.

- [ ] **Step 4 : Lancer tous les tests**

Run: `just tests`
Expected: tous verts, dont ceux du vrai site de `tests/test_construction.py` (documents construits sans lien mort,
aucune page racine sans passerelle ni redirection) et `tests/test_redirections.py::test_motifs_de_site_py`.

- [ ] **Step 5 : Construire le site et lire ce qu'il change**

Run: `python3 site.py && git status --short site | sort | head -40`
Expected sous `site/` seulement : `site/chambre/amenagement/` (nouveau : `index.html`, `historique.html`,
`dessins.css`) ; `site/chambre-amenagement.html` (devenu une redirection) ; `site/index.html` (lien et
« 10,3 m² » de la chambre) ; `site/journal.html` (lien des cinq lignes de la chambre) ; le menu de chaque page générée
(`site/entree/…`, historiques) qui mène maintenant à `chambre/amenagement/`. Rien d'autre. Vérifier aussi :
`grep -c "Chambre ›" site/journal.html` donne le même nombre de lignes de la chambre qu'avant (5).

- [ ] **Step 6 : Écrire `tests/navigateur/chambre-amenagement.js`** sur le modèle de `tests/navigateur/entree.js`
  (en-tête `/* @site reel : … */`, mêmes outils `preparer`, `sansPolices`, `ouvrir`, `attendre`, `debordements`,
  `partie`), `DOC = ${BASE}/chambre/amenagement/`, une seule variante, `LARGEURS = [[1440, 900], [1100, 800], [390, 844]]` :
  - **vues** : à chaque largeur, les cinq vues et chaque élévation (`est`, `sud`, `ouest`) : aucune erreur de console
    ni réponse en erreur, rien ne déborde, aucun défilement horizontal à 390 px ; Plan, Coupes, Explication non grisées ;
    `#iso` et `#camera` : onglet `aria-disabled="true"`, la section affiche « Pas encore rendu » ;
  - **pas de comparaison** : ni choix de variante, ni « Comparer » dans la barre ;
  - **plan** : toucher `rect.zone[data-meuble="lit"]` ouvre la fiche « ① Lit 160, tête au sud » avec « Coupe sud » ;
    la touche Entrée au clavier aussi ; un calque masqué (Cotes, Passages libres) masque tous ses éléments ;
  - **Position** : sur chaque élévation, seul `line.sec[data-k=<k>]` du mini-plan porte `ici` ;
  - **dessins lisibles** : dans chaque scène visible, aucune forme (`rect`, `path`, `circle`, `line`, `text`) n'a un
    `fill` ou un `stroke` calculé à `rgb(0, 0, 0)` (l'encre du site est `#1D2A33`), et la boîte de chaque `text` tient
    dans le `viewBox` de son SVG ;
  - **anciennes adresses** : `/chambre-amenagement.html` → `/chambre/amenagement/` sans fragment, vue Plan ;
    `#verifier` → `#explication` ; `#elevations` → `#coupes` ; `#plan-a-l-echelle` → `#plan` ; `#principe` →
    `#explication` ; `#inconnue` → Plan ; `#changements` → `/chambre/amenagement/historique.html` ;
  - **historique** : versions figées `["V1.2 4 octobre 2026"]`, son lien répond 200, un journal de 5 lignes ;
  - **accueil** : la chambre du plan mène à `chambre/amenagement/` et affiche « 10,3 m² » ;
  - **sans JavaScript** (1440 et 390 px) : classe `sans-js`, les cinq vues l'une sous l'autre, la page ne déborde pas.
  Le script renvoie `{ok, echecs, erreurs}`.

- [ ] **Step 7 : Lancer le script**

Run: `PORT=8900 SESSION=refonte-chambre-amenagement-1 tests/navigateur/lancer.sh tests/navigateur/chambre-amenagement.js`
Expected: `"ok": true`, aucun échec, aucune erreur. (La comparaison à l'œil avec l'ancienne page, servie à part depuis
`git show refonte:chambre-amenagement.html` sur le port 8901, et les captures regardées une à une, sont l'étape de
vérification au navigateur de l'orchestrateur, par un autre agent.)

- [ ] **Step 8 : Remettre `site/` et commiter**

```bash
git checkout -- site && git clean -fdq site
git add site.py justfile tests/test_chambre.py tests/navigateur/chambre-amenagement.js
git status --short
git commit -m "Chambre : bascule, le document remplace la passerelle, l'ancienne page redirige avec ses ancres

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
```
Expected avant le commit : `git status --short` ne montre que `site.py`, `justfile`, `tests/…` et
`D  chambre-amenagement.html`, rien sous `site/`.
