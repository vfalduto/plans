# Meuble linge SDB, document V4 : plan de travail

> **Pour les agents qui exécutent ce plan :** utiliser superpowers:subagent-driven-development (recommandé) ou
> superpowers:executing-plans pour l'exécuter tâche par tâche. Les étapes se cochent (`- [ ]`).

**But :** remplacer `sdb-meuble-v3.html` et sa notice par trois pages :
- `sdb-meuble-v4.html` : vue iso de l'ensemble, note sur les matériaux communs, note Corno, changements ;
- `sdb-meuble-v4-bas.html` et `sdb-meuble-v4-haut.html` : vue iso du meuble, notice façon IKEA, découpe, matériaux et
  prix.

Le tout pour 400 € TTC au plus.

**Architecture :**
- `3d/sdb/modele.py` reste la source unique. Il passe en V6.0 avec les nouveaux matériaux, la protection réduite, les
  tuyaux, les coins de calage et les catalogues de matériaux candidats.
- Un nouveau générateur `3d/sdb/pages.py` écrit les trois pages en réutilisant :
  - dans `plan.py` : débit, calepinage, listes d'achat, en-tête, CSS ;
  - dans `montage.py` : dessin iso, étapes, fiches.
- Les deux anciens générateurs perdent leurs pages et le code mort : vues, coupes, comparatifs, variante roulettes.

**Pile technique :** Python 3 sans dépendance, SVG inline, pytest lancé par `uv`, FreeCAD (`cad.py`, inchangé).

**Spécification :** `docs/superpowers/specs/2026-10-26-sdb-meuble-v4-design.md`. La lire avant toute tâche.

## Contraintes globales

- **Budget :** total TTC ≤ 400,00 €. Il comprend :
  - les consommables, le meuble bas et le caisson haut ;
  - les achats faits ailleurs (toile des sacs `TOILE["prix"]`) ;
  - la livraison s'il y en a une (aucune avec les choix ci-dessous) ;
  - pas le plombier.
- **Matériaux retenus** (relevés en ligne le 26/10/2026, Weldom Marseille Saint-Barnabé, magasin choisi, stock non
  lu) :
  - **plan de travail :** tablette chêne lamellé-collé brute FSC 2000 × 600 × 18, réf. 82025610, 66,90 € ;
  - **caisson haut :** tablettes mélaminées blanches 18 (`TABLETTES_18`, inchangées) ;
  - **chant :** bande de chant thermocollante blanc Primo 500 × 2,3 cm, réf. 5566191, 9,50 € ;
  - **vernis :** vernis marin Syntilor incolore satiné, 12 m²/L par couche (réf. 5703473 en 0,25 L à 20,90 €,
    5603010 en 0,75 L à 37,50 €, 1085572 en 2,5 L à 69,90 €).
- **Vernis :** trois couches, sur les pièces de repère `D` seulement (le plan). Rien sur le caisson haut.
- **Tuyaux :** au mur du fond, y = `ROBINET["y"]` (74).
  - évacuation par un siphon à z = 60, dans la lame entre `XO1` (229) et `X1` (234) ;
  - arrivée à z = 80, qui monte au robinet par l'encoche `TRAPPE`.

  Aucune pièce du meuble ne doit entrer dans la zone y ∈ [ROBINET["y"] − 8, ROBINET["y"] + 8],
  x ∈ [XO1, X1], z ∈ [50, Z_PLAN].
- **Calage :** coins taillés dans des chutes de tasseau, sans vis dans le mur, entre les montants des deux échelles du
  bord et les murs nord et sud.
- **Fichiers produits** :
  - `sdb-meuble-v4.html`, `sdb-meuble-v4-bas.html`, `sdb-meuble-v4-haut.html` ;
  - la V5.24 archivée en `archive/sdb-meuble-v5.24.html` et `archive/sdb-meuble-v5.24-montage.html` ;
  - `sdb-meuble-v3*.html` supprimés à la racine.
- **Règles des plans :**
  - version dans le kicker, `VERSION = "V6.0"` ;
  - tableau des changements en fin de page principale, avec une ligne V6.0 ;
  - ancres du sommaire (`PL.ANCRES`) sur les trois pages ;
  - aucune cote écrite en dur dans les textes, tout est calculé depuis `modele.py` ;
  - français correct, accents compris.
- **Tests :** `uv run -q --no-project --with pytest pytest -q 3d/sdb/test_v4.py`, depuis la racine du dépôt.

## Points à surveiller en relecture

1. **Budget qui « tient » en oubliant un poste.** Le total doit additionner exactement les lignes affichées, plus les
   achats faits ailleurs. Test : la somme des lignes des trois listes, plus `TOILE["prix"]`, est égale à
   `prix()["total"]` (tâche 3).
2. **Pièce du caisson haut perdue entre le bas et le haut.** Le calepinage range une partie du haut dans les chutes du
   bas. Chaque repère du haut doit figurer une fois et une seule dans les tablettes dessinées des deux pages. Test :
   le multiensemble des repères posés est égal au débit (tâche 3).
3. **Vernis compté sur les mauvaises pièces.** Test : `VERNIS["m2"]` égale la surface des seules pièces `D` (tâche 2).
4. **Renfort ou pièce qui entre dans la zone des tuyaux.** Test d'intersection (tâche 2).
5. **Page qui garde un reste de l'ancienne V3.** On ne doit plus trouver « Coupe », « Élévation », le bouton
   « Bacs à roulettes », ni de lien vers `sdb-meuble-v3`. La page principale doit nommer « Wenko Corno » avec sa
   référence ou son prix (tâche 3).

---

### Tâche 1 : archiver la V5.24

**Fichiers :**
- Créer : `archive/sdb-meuble-v5.24.html`, `archive/sdb-meuble-v5.24-montage.html`, `3d/sdb/figees/V5.24.html`
- Modifier : `index.html`, section des archives (lignes ≈ 140-146)

**Interfaces :** aucune.

- [ ] **Étape 1 :** depuis la racine, lancer `python3 3d/sdb/plan.py --figer`. Attendu : « V5.24 figée », et
  `archive/sdb-meuble-v5.24.html` existe.
- [ ] **Étape 2 :** copier `sdb-meuble-v3-montage.html` vers `archive/sdb-meuble-v5.24-montage.html`, puis réécrire
  dans les deux pages archivées :
  - les liens relatifs vers `../` (favicon, `index.html`) ;
  - le lien croisé plans ↔ notice vers les fichiers archivés (`sdb-meuble-v5.24.html` ↔ `sdb-meuble-v5.24-montage.html`).

  Vérifier qu'aucun `href` ne pointe vers `sdb-meuble-v3` :
  `grep -c 'sdb-meuble-v3' archive/sdb-meuble-v5.24*.html`. Attendu : 0 et 0.
- [ ] **Étape 3 :** ajouter deux lignes à la liste des archives de `index.html`, au même format que les lignes
  « Meuble linge V2 » : « Meuble linge V5.24 » et « Notice meuble linge V5.24 ».
  - date de création : celle du premier commit de `sdb-meuble-v3.html`
    (`git log --diff-filter=A --format=%as -- sdb-meuble-v3.html | tail -1`) ;
  - date de modification : 2026-10-26.
- [ ] **Étape 4 :** commiter avec le message « Meuble linge SDB : V5.24 archivée avant la V4 du document » et la ligne
  Co-Authored-By de la session.

### Tâche 2 : modèle V6.0

**Fichiers :**
- Modifier : `3d/sdb/modele.py`
- Créer : `3d/sdb/test_v4.py`

**Interfaces :**
- Utilise : `PIECES`, `TABLETTES_18`, `PANNEAUX`, `STOCK`, `WELDOM`, `QUINCAILLERIE`, `ETAPES`, `CHANGEMENTS`, `CH`,
  `RAINURE`, `ROBINET`, `TRAPPE`, `XO1`, `X1`, `Z_PLAN`.
- Produit :
  - `PT == 1.8` et `TH == 1.8` ;
  - `PANNEAUX["D"] == [dict(L=2000, l=600, prix=66.90, stock=None, ref="82025610", nom=…)]` et `STOCK["K"] == "M18"` ;
  - `VERNIS` (dict avec les clés `couches`, `rendement`, `pots`, `m2`, `litres`, `achat`) ;
  - `TUYAUX` : dict avec `zone=(x0, x1, y0, y1, z0, z1)`, `evacuation_z=60`, `arrivee_z=80` ;
  - `COINS` : dict avec `n` (nombre de coins) et `pos` (liste de (nom de l'échelle, z)) ;
  - `MATERIAUX_HAUT` et `ESSENCES_PLAN` : listes de dicts aux clés `nom, ep, magasin, ref, prix, format, qualites,
    defauts, finition`, plus `retenu: bool` ; `ESSENCES_PLAN` a en plus `retrait_t` (%, None si inconnu) et `source` ;
  - `CORNO` est gardé.

- [ ] **Étape 1 : écrire les tests qui échouent** dans `3d/sdb/test_v4.py`. Le fichier commence par
  `sys.path.insert(0, os.path.dirname(__file__))` puis `import modele as M`.

```python
def test_epaisseurs_v6():
    assert M.VERSION == "V6.0" and M.PT == 1.8 and M.TH == 1.8

def test_plan_chene_weldom():
    d = M.PANNEAUX["D"][0]
    assert (d["L"], d["l"], d["prix"], d["ref"]) == (2000, 600, 66.90, "82025610")
    assert M.STOCK["K"] == "M18"

def test_vernis_plan_seul():
    s = sum(M._surface(b) for b in M.PIECES if b.rep.startswith("D"))
    assert abs(M.VERNIS["m2"] - s) < 1e-9 and M.VERNIS["couches"] == 3
    assert [p["ref"] for p, _ in M.VERNIS["achat"]] == ["5603010"]   # un pot de 0,75 L

def test_tuyaux_libres():
    x0, x1, y0, y1, z0, z1 = M.TUYAUX["zone"]
    for b in M.PIECES:
        assert not (b.x0 < x1 and b.x1 > x0 and b.y0 < y1 and b.y1 > y0 and b.z0 < z1 and b.z1 > z0), b.nom

def test_coins_de_calage():
    assert M.COINS["n"] == 8 and {e for e, _ in M.COINS["pos"]} == {"n", "s"}

def test_catalogues():
    assert sum(m["retenu"] for m in M.MATERIAUX_HAUT) == 1
    assert {m["ep"] for m in M.MATERIAUX_HAUT} <= {1.6, 1.8}
    assert sum(e["retenu"] for e in M.ESSENCES_PLAN) == 1
    assert next(e for e in M.ESSENCES_PLAN if e["retenu"])["ref"] == "82025610"
```

- [ ] **Étape 2 :** lancer les tests. Attendu : ÉCHEC (VERSION vaut "V5.24", `TUYAUX` n'existe pas).
- [ ] **Étape 3 : modifier `modele.py`.**
  - **Version et épaisseurs :** `VERSION = "V6.0"`, `PT = 1.8`, `TH = 1.8`. Commentaire : V6.0, demande client, budget
    de 400 € et protection au juste niveau.
  - **Plan :** remplacer `PANNEAUX["D"]` par la tablette chêne (valeurs des contraintes globales,
    `magasin="Weldom"` et `nom="Tablette chêne lamellé-collé brute FSC 200 × 60 × 18"`). Réécrire `MATERIAUX["D"]` et
    `USINAGES["D1"]` : recoupé à `(YM1 - YM0) * 10` de long, plus de recoupe en profondeur (la tablette fait déjà 600),
    vernis marin 3 couches toutes faces, trous ovalisés gardés (le chêne bouge moins que le hêtre, mais il bouge).
    Mettre à jour l'étape « Plan de travail » d'`ETAPES` (supprimer la recoupe en profondeur).
  - **Caisson haut :** `STOCK["K"] = "M18"`. `MATERIAUX["K"]` = tablette mélaminée blanche 18, chants coupés plaqués de
    chant thermocollant. Fond de nouveau en deux moitiés `ch_fond_n` et `ch_fond_s`, jointes derrière le montant
    central, comme avant la V5.24 (`git show HEAD~1:3d/sdb/modele.py`, à adapter aux repères K). Rétablir les boucles
    de vis et de chevilles sur les deux moitiés. `RAINURE = dict(l=2.0, haut=1.2, bas=0.5, bord=0.5, entre=1.0,
    prise=0.6)`. Retirer la mention « avant le vernis » de l'étape « Caisson haut ».
  - **Vernis :** dans le calcul `VERNIS["m2"]`, filtrer `b.rep[:1] == "D"`. Le texte de `QUINCAILLERIE["vernis"]` dit
    « plan de travail seulement ». L'étape 0 ne vernit plus que le plan.
  - **Chant :** `WELDOM["chant"] = ("Bande de chant thermocollante blanc Primo 500 × 2,3 cm", 9.50, 1, None,
    "5566191")`.
  - **Tuyaux :** `TUYAUX = dict(zone=(XO1, X1, ROBINET["y"] - 8, ROBINET["y"] + 8, 50, Z_PLAN), evacuation_z=60,
    arrivee_z=80)`, avec un `assert` équivalent au test. Ajouter deux `Bloc` d'équipement de rôle `"tuyau"` (siphon :
    cylindre approché par un bloc 6 × 6 × 12 centré sur z = 60 ; arrivée : bloc 2 × 2 de z = 80 à `ROBINET["z"]`)
    dans `EQUIPEMENTS`, `miroir=False`.
  - **Coins :** `COINS = dict(n=8, pos=[(e, z) for e in ("n", "s") for z in (Z0 + 5, Z_PLAN - 5)])`. Chaque position
    vaut pour les deux montants, avant et arrière, d'où 8 coins. Pas de pièce de débit : les coins viennent des chutes
    de tasseau. Ajouter une phrase à l'étape « Pose, rails et butée » : enfoncer au maillet un coin entre chaque
    montant des échelles du bord et le carreau, en bas et en haut, sans vis, avec un point de silicone.
  - **Catalogues :**

    `MATERIAUX_HAUT`, valeurs relevées au Weldom le 26/10/2026 :
    - mélaminé blanc 18 (`TABLETTES_18`), retenu : aucune finition, chants à plaquer, aggloméré qui gonfle à l'eau ;
    - aggloméré brut 16 (demi-panneau 2500 × 600, 21,50 €, ou prédécoupe 120 × 60, réf. 9128556, 13,35 €) : à peindre
      (sous-couche), chants poreux ;
    - médium 16 (prédécoupes 120 × 40, réf. 9128677, 12,50 €, et 80 × 60, réf. 9128697, 12,50 €) : se peint très bien,
      lourd, petites plaques seulement ;
    - OSB3 18 trois plis Swiss Krono 2500 × 675 (réf. 68398456, 20,50 €) : aspect brut, se peint mais la texture
      reste ;
    - sapin lamellé-collé 18, tablette 200 × 50 (36,70 €) : bois massif, se peint ou se vernit, plus cher.

    `ESSENCES_PLAN` :
    - hêtre : Leroy Merlin, 200 × 65 × 26, 59,90 € ; `retrait_t=11.7`, non durable ;
    - chêne : Weldom, tablette 82025610, retenu ; `retrait_t=8.4`, très bonne résistance à la pourriture ;
    - chêne : Leroy Merlin, 250 × 65 × 26, 109 € ; `retrait_t=8.4` ;
    - acacia huilé : Leroy Merlin, 250 × 65 × 26, 119 € ; `retrait_t=None`.

    Sources : `https://www.wood-database.com/european-beech/` et `https://www.wood-database.com/english-oak/`.
  - **Changements :** ajouter en tête de `CHANGEMENTS` une ligne
    `("V6.0", "26/10/2026", …)` qui résume le document V4 (trois pages, le reste retiré), le budget de 400 €, le plan en
    chêne de 18, le caisson haut en mélaminé, le vernis sur le plan seul, les coins de calage et les tuyaux.
- [ ] **Étape 4 :** lancer les tests. Attendu : tous passent. Lancer aussi `python3 -c "import sys;
  sys.path.insert(0,'3d/sdb'); import modele"` : aucune assertion du modèle ne doit casser.
- [ ] **Étape 5 :** commiter `3d/sdb/modele.py` et `3d/sdb/test_v4.py` avec le message
  « Meuble linge SDB V6.0 : modèle (chêne 18, mélaminé, vernis plan seul, coins, tuyaux) ».

### Tâche 3 : les trois pages

**Fichiers :**
- Créer : `3d/sdb/pages.py`
- Modifier :
  - `3d/sdb/montage.py`, fonction `dessin` : paramètre `carrelage` ;
  - `3d/sdb/test_v4.py` ;
  - `justfile`, recette `sdb` ;
  - `index.html`, section Salle de bain.

**Interfaces :**
- Utilise :
  - `PL.debit()`, `PL.table_debit(meuble)`, `PL.tablette_svg(p, k)`, `PL.liste(lignes, titre)`,
    `PL.ligne_panneaux(panneaux)`, `PL.calepinage()`, `PL.code_meuble(code)`, `PL.entete(titre, racine, css)`,
    `PL.ANCRES`, `PL.euros(v)`, `PL.patron_svg()` ;
  - `MO.dessin(...)`, `MO.bloc_etape(n)`, `MO.plans_sous_ensembles(meuble)`, `MO.carte_piece(p)`, `MO.OUTILS`,
    `MO.fixation_haut()`, `MO.puces_quinc(counter)`, `MO.CSS` ;
  - `CAL.calepinage(debit)`.
- Produit :
  - `MO.dessin(..., carrelage: float | None = None)` : quand `murs=True` et `carrelage` est donné, une bande
    `class="icarr"` sur les murs du fond et nord, de 0 à `carrelage`, sous les pièces, avec le libellé
    « carrelage {carrelage} » ;
  - `pages.prix() -> dict` avec les clés `consommables, bas, haut, ailleurs, total` (en €) et `lignes`
    (dict meuble → liste des tuples `(nom, ref, n, prix, stock)`) ;
  - `pages.economie_commune() -> dict(pieces=int, euros=float)` : pièces du haut qui tiennent dans les chutes du bas,
    et euros gagnés par rapport au haut acheté seul (`CAL.calepinage` des seules lignes du haut) ;
  - `pages.page_ensemble() -> str`, `pages.page_meuble(meuble: str) -> str` (avec `meuble` dans {"bas", "haut"}) ;
  - `pages.ecrire()` écrit les trois fichiers à la racine.

- [ ] **Étape 1 : écrire les tests qui échouent** à la suite de `test_v4.py`, après `import pages`.

```python
def test_budget():
    p = pages.prix()
    assert p["total"] <= 400.00
    lignes = sum(n * px for m in ("commun", "bas", "haut") for _, _, n, px, _ in p["lignes"][m])
    assert abs(p["total"] - (lignes + p["ailleurs"])) < 0.01
    assert abs(p["ailleurs"] - M.TOILE["prix"]) < 0.01

def test_tous_les_reperes_poses():
    from collections import Counter
    cal = PL.calepinage()
    poses = Counter(q[0] for st in cal for grp in ("bas", "neufs") for pn in cal[st][grp] for q in pn.poses())
    attendu = Counter({r["rep"]: r["q"] for r in PL.debit() if r["mat"] in M.STOCK})
    assert poses == attendu

def test_pages():
    ens, bas, haut = pages.page_ensemble(), pages.page_meuble("bas"), pages.page_meuble("haut")
    assert 'class="icarr"' in ens and f"carrelage {M.CARRELAGE}" in ens
    assert "Wenko Corno" in ens and 'id="changements"' in ens and "V6.0" in ens
    for h in (ens, bas, haut):
        for interdit in ("Coupe", "Élévation", "Bacs à roulettes", "sdb-meuble-v3"):
            assert interdit not in h, interdit
    for h in (bas, haut):
        for sec in ('id="iso"', 'id="montage"', 'id="decoupe"', 'id="achats"'):
            assert sec in h, sec
    assert all(m["nom"] in haut for m in M.MATERIAUX_HAUT)
    assert all(e["nom"] in bas for e in M.ESSENCES_PLAN)
```

- [ ] **Étape 2 :** lancer les tests. Attendu : ÉCHEC (`No module named 'pages'`).
- [ ] **Étape 3 : `dessin(..., carrelage=None)` dans `montage.py`.** Ajouter le CSS `.icarr` (motif de carreaux
  discret, ou `fill:var(--water);fill-opacity:.12`) et `.icarrt` pour le libellé, en clair et en sombre.
- [ ] **Étape 4 : `pages.py`.**
  - **`prix()`** reprend le calcul de `PL.achats()` sans le HTML.
    - `ailleurs` vaut `TOILE["prix"]` ; les barres sont de récupération, sans coût.
    - Les lignes de vernis sont incluses (consommables).
  - **`page_ensemble()`** :
    - barre de navigation : « ← Plans » (`index.html`), « Meuble bas », « Caisson haut » ;
    - kicker avec `M.VERSION` ;
    - h1 « Meuble linge » ;
    - `<h2 id="ensemble">` : iso de `M.version("d")` avec `murs=True`, `carrelage=M.CARRELAGE` (tuyaux compris) ;
    - `<h2 id="materiaux-communs">` : `economie_commune()` et les consommables communs, affichés seulement si
      `euros > 0`, sinon une phrase qui le dit ;
    - une note « Remplacer le L par deux paniers » : Wenko Corno, `CORNO["l"]` × `CORNO["p"]` × `CORNO["h"]`,
      `CORNO["litres"]` L, `CORNO["prix"]` € pièce, `CORNO["source"]`, sans porte ;
    - le budget : trois montants et le total, comparé à 400 € ;
    - `<section id="changements">` : tableau de `M.CHANGEMENTS`.
  - **`page_meuble(meuble)`**, sections dans cet ordre :
    - `id="iso"` : iso du meuble seul (pièces de `M.meuble(rep) == meuble`, plus la machine et les tuyaux pour le
      bas) ;
    - `id="montage"` : cartes pièces, outils `MO.OUTILS[meuble]`, quincaillerie, puis les étapes
      `range(0, haut0)` pour le bas et `range(haut0, len(M.ETAPES))` pour le haut, avec
      `MO.plans_sous_ensembles(meuble)`. Pour le bas, ajouter `PL.patron_svg()` et les cotes du sac ; pour le haut,
      `MO.fixation_haut()` ;
    - `id="decoupe"` : `PL.table_debit(meuble)` et les dessins `PL.tablette_svg` des panneaux de ce meuble. Pour le
      haut : les neufs, et la liste des pièces prises dans les chutes du bas ;
    - `id="achats"` : liste d'achats du meuble avec `PL.liste`, sous-total, et rappel du total général ;
    - **pour le haut**, `id="materiaux"` : tableau de `M.MATERIAUX_HAUT`, une ligne par panneau, avec qualités,
      défauts, finition (« se peint » pour un bois brut), prix, et le retenu signalé ;
    - **pour le bas**, `id="essence"` : tableau de `M.ESSENCES_PLAN` avec le retrait tangentiel, les liens source, le
      retenu signalé, et une phrase sur la rigidité (coins de calage, plan vissé sur les trois échelles, écharpes,
      zone des tuyaux laissée libre, machine qui ne touche jamais le meuble).
  - **`ecrire()`** écrit les trois fichiers, `__main__` appelle `ecrire()`. Les liens entre pages sont relatifs.
- [ ] **Étape 5 :** remplacer la recette `sdb` du `justfile` (commentaire compris) par `python3 3d/sdb/pages.py`, puis
  la ligne FreeCAD existante. Supprimer la recette `sdb-figer`. Dans `index.html`, section Salle de bain, une seule
  carte « Meuble linge » vers `sdb-meuble-v4.html`, sous-titre « Meuble bas et caisson haut, notice et prix ».
- [ ] **Étape 6 :** lancer `just sdb`, puis les tests. Attendu : tous passent, sans trace d'erreur. Le total a été
  estimé à environ 390 € pendant la préparation du plan. Si `test_budget` échoue, ne changer aucun matériau : s'arrêter
  et rapporter le détail des trois sous-totaux au client.
- [ ] **Étape 7 : vérification visuelle.** Servir la racine (`python3 -m http.server 8765`) et ouvrir les trois pages
  avec `playwright-cli`, à 1280 et à 390 de large. Vérifier :
  - pas de défilement horizontal ;
  - la console sans erreur ;
  - le carrelage visible sur l'iso de l'ensemble ;
  - les sommaires qui fonctionnent.
- [ ] **Étape 8 :** commiter les fichiers créés et modifiés, plus les trois HTML générés, avec le message
  « Meuble linge SDB V6.0 : document V4 en trois pages ».

### Tâche 4 : retirer l'ancien

**Fichiers :**
- Modifier :
  - `3d/sdb/plan.py` : garder seulement ce que `pages.py` et `montage.py` importent ;
  - `3d/sdb/montage.py` : retirer `contenu()`, `page()`, `OUT`, `__main__` ;
  - `3d/sdb/modele.py` : retirer `PANIERS`, `RETIRES_ROUL`, `VOLUME_ROUL` et la branche "dr" de `version()`, mais
    garder `CORNO`.
- Supprimer : `sdb-meuble-v3.html`, `sdb-meuble-v3-montage.html`, `3d/sdb/figees/`.

**Interfaces :** `PL.*` et `MO.*` utilisés par `pages.py` (liste de la tâche 3) restent tels quels.

- [ ] **Étape 1 :** ajouter le test qui garde le nettoyage.

```python
def test_plus_de_v3():
    import os
    racine = os.path.join(os.path.dirname(__file__), "..", "..")
    assert not os.path.exists(os.path.join(racine, "sdb-meuble-v3.html"))
    assert not hasattr(M, "PANIERS")
```

- [ ] **Étape 2 :** lancer le test. Attendu : ÉCHEC.
- [ ] **Étape 3 :** supprimer les fonctions de `plan.py` qui ne servent plus :
  - vues : `plan_svg`, `vue`, `elevation`, `coupe_b`, `coupe_c_svg`, `murs_coupe`, `visibles` ;
  - comparatifs et pages : `comparatif_bac`, `capacites`, `contenu`, `page`, `figer`, `lire_figees`, `barre`,
    `SCRIPT`, `__main__`.

  Faire de même pour le code mort de `montage.py` et `modele.py` listé ci-dessus. Vérifier avec
  `grep -n "roul\|PANIERS\|coupe_\|elevation" 3d/sdb/*.py`. Attendu : plus aucune occurrence, sauf les mentions dans
  `CHANGEMENTS`.
- [ ] **Étape 4 :** supprimer les fichiers listés. Lancer `just sdb` et tous les tests. Attendu : tous passent. Vérifier
  les liens avec `grep -rn "sdb-meuble-v3" --include=*.html .`. Attendu : seulement dans `archive/`.
- [ ] **Étape 5 :** mettre à jour la mémoire `sdb-meuble.md` (V6.0, trois pages, `just sdb` → `pages.py`) et la ligne
  de `MEMORY.md`. Commiter avec le message « Meuble linge SDB : retrait de la V3 (vues, coupes, variante roulettes) ».
