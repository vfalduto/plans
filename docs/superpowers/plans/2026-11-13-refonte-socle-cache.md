# Socle de la migration, lot S3 : cache de rendu pour tout document

> Exécution : skill `superpowers:subagent-driven-development`. Branche `refonte-socle-cache`, worktree
> `/Users/nvi/code/work/personal/plan-wt/socle-cache`. Spec : `docs/superpowers/specs/2026-11-13-refonte-site-design.md`
> (objectif 9, « Rendus plus rapides »). Consignes communes de la migration :
> `/Users/nvi/code/work/personal/plan/.superpowers/sdd/2026-11-13-refonte-pages/consignes.md`.

## But

`commun/rendu_cache.py` ne sait calculer les empreintes que de l'entrée (`PIECE`, `DOCUMENT`, `MODULES`, `CODE` en
dur). Huit documents vont être migrés en parallèle ; chacun doit pouvoir brancher ses rendus sur le même cache sans
toucher à `commun/rendu_cache.py`. Ce lot rend le cache utilisable par tout document, sans changer une seule empreinte
de l'entrée.

## Contraintes globales

- **Les empreintes de l'entrée ne changent pas.** Avec le fichier `cache/empreintes.json` déjà présent dans le worktree
  (copie de celui du dépôt, ignoré par git), `liste` ne propose aucune vue pour `principale` ni pour `victor` à 64
  échantillons, avant comme après. L'empreinte reste : caméra (`dataclasses.asdict`), données (constantes en majuscules
  des modules, clés `<nom du module>.<constante>`, sans `EXCLUES`), réglages `{"echantillons": n}`, texte des fichiers
  de code concaténés dans l'ordre déclaré, première ligne de `blender --version`.
- **Ne modifie pas** `pieces/entree/amenagement/rendu.py` ni `3d/rendu.py` : leur texte entre dans l'empreinte. Si
  c'est inévitable, arrête-toi et rends `BLOCKED` avec la raison.
- **Aucun rendu Blender.** `blender --version` (appelé par le cache) est permis ; rien d'autre.
- **Format des clés** du fichier : `<piece>/<document>/<variante>/<caméra>` (inchangé). Pour un document sans variante
  (une seule `Variante` d'id vide) : `<piece>/<document>/<caméra>`. Aucune conversion du fichier existant n'est donc
  à livrer ; si tu dois quand même changer le format, livre la conversion et dis-le.
- **Fichiers permis** : `commun/rendu_cache.py`, `tests/test_rendu_cache.py`, le `justfile` (seulement les recettes
  `entree-rendu` et `entree-apercu` et un commentaire-modèle à côté), `pieces/entree/amenagement/document.py`
  (seulement pour y poser la déclaration). Un autre lot réécrit en même temps `pieces/entree/amenagement/vues.py`,
  `commun/site.css`, `commun/site.js`, `commun/gabarit.py`, `tests/fixtures/essai/` et `tests/navigateur/` : n'y
  touche pas. Si un test a besoin d'un faux document, crée-le dans un dossier temporaire (`tmp_path`) ou sous
  `tests/fixtures/rendu_cache/`.
- **Style du dépôt** : français, lignes de 120 caractères au plus, pas de point médian dans les textes, commentaires
  qui disent le pourquoi. Commits petits, en français, avec la ligne `Co-Authored-By` habituelle.
- **Tests** : `uv run -q --no-project --with pytest pytest -q tests` (115 tests verts au départ). Tests d'abord
  (skill `superpowers:test-driven-development`).

### Task 1 : Cache de rendu pour tout document

**Fichiers :** `commun/rendu_cache.py`, `tests/test_rendu_cache.py`, `justfile`,
`pieces/entree/amenagement/document.py`.

**Ce que le document déclare.** Une constante `CACHE_RENDU` dans `pieces/<piece>/<document_>/document.py` (le paquet
Python prend un tiret bas quand l'identifiant du document a un tiret : `sdb/meuble-bas` se lit dans
`pieces.sdb.meuble_bas.document`). Elle est du type `commun.rendu_cache.CacheRendu` (dataclass gelée, à créer) :

- `variantes` : pour chaque identifiant de variante (dans l'ordre des rendus), les modules de données qui entrent dans
  l'empreinte. Un nom sans point est un module du paquet du document (`"victor"` → `pieces.entree.amenagement.victor`) ;
  un nom avec point est pris tel quel (`"pieces.entree.piece"`, `"pieces.sdb.modele"`). L'identifiant vide `""` désigne
  le document sans variante.
- `code` : les fichiers dont le texte entre dans l'empreinte, chemins depuis la racine du dépôt, dans l'ordre.
- `cameras` (facultatif) : le module qui porte la constante `CAMERAS` (tuple de `commun.modele.Camera`). Défaut :
  `pieces.<piece>.piece`. Un meuble dont les rendus ont leurs propres caméras les déclare dans un module du document.

Pour l'entrée : `variantes = {"principale": ("pieces.entree.piece", "document"), "victor": ("pieces.entree.piece",
"victor")}`, `code = ("pieces/entree/amenagement/rendu.py", "3d/rendu.py")`. `CACHE_RENDU` s'ajoute à `EXCLUES` (c'est
une constante de page : elle ne doit pas entrer dans l'empreinte). Les constantes `PIECE`, `DOCUMENT`, `MODULES` et
`CODE` de `commun/rendu_cache.py` disparaissent.

**Ligne de commande.**

    python3 -m commun.rendu_cache variantes <piece>/<document>
    python3 -m commun.rendu_cache liste <piece>/<document> <variante> <échantillons> [caméra ...]
    python3 -m commun.rendu_cache noter <piece>/<document> <variante> <échantillons> <caméra> [caméra ...]

- `variantes` affiche les identifiants déclarés, séparés par des espaces, dans l'ordre de la déclaration ; la variante
  d'id vide s'écrit `-` (à l'affichage comme en argument de `liste` et de `noter`).
- `liste` et `noter` gardent leur comportement : `liste` sans caméra affiche celles dont l'empreinte a changé ; avec
  des caméras, il les affiche telles quelles ; une caméra inconnue sort en erreur (code 1, message sur stderr).
- Erreurs dites clairement sur stderr, code de sortie non nul, sans trace Python : document introuvable (paquet
  absent), `CACHE_RENDU` absente, variante non déclarée, fichier de code absent, arguments manquants (rappel de
  l'usage).

**Recettes.** `entree-rendu` appelle la nouvelle ligne de commande (`entree/amenagement`) et tire la liste des
variantes de `variantes` au lieu de `principale victor` en dur ; son comportement ne change pas. `entree-apercu` : même
boucle sur `variantes`. Juste au-dessus, un commentaire-modèle (dix lignes au plus) donne la forme des deux recettes
d'un autre document : `<piece>-<document>-rendu echantillons="64" *vues` (variantes → `liste` → effacer les anciennes
sorties → un seul Blender par variante → copie vers `site/<piece>/<document>/rendus/` → `noter` → `python3 site.py
<piece>/<document>`) et `<piece>-<document>-apercu *vues` (16 échantillons, sortie dans `cache/apercu/`, ni cache ni
copie dans `site/`). Nommage des images copiées : `<variante>-<caméra>.jpg` et, s'il y a un masque,
`<variante>-<caméra>-masque.png` ; pour un document sans variante, `<caméra>.jpg` et `<caméra>-masque.png`. Ne crée
pas de script ni de recette générique : le modèle est un texte, chaque page écrit ses deux recettes.

**Tests à écrire d'abord** (dans `tests/test_rendu_cache.py`, les tests existants restent verts, adaptés seulement là
où ils nommaient les constantes retirées) :

1. Pour chaque variante de l'entrée et chaque caméra, l'empreinte calculée par le nouveau chemin (celui de la ligne de
   commande, pour `entree/amenagement`) est égale à celle de l'ancienne formule, réécrite dans le test :
   `empreinte(c, donnees_variante(piece, module), {"echantillons": 64}, <texte de rendu.py + texte de 3d/rendu.py>,
   <ligne de version>)`. La ligne de version de Blender est injectée (paramètre ou `monkeypatch`) : le test ne lance
   pas Blender.
2. Deux processus (`PYTHONHASHSEED` 1 et 2) calculent les mêmes empreintes par le nouveau chemin.
3. Un faux document à tiret (`essai/meuble-bas`, paquet `meuble_bas`) et un faux document sans variante : résolution
   du paquet, modules relatifs et absolus, `cameras` déclaré, clés `<piece>/<document>/<variante>/<caméra>` et
   `<piece>/<document>/<caméra>`, `variantes` qui affiche `-`.
4. `liste` puis `noter` puis `liste` sur un fichier de cache temporaire : la caméra notée n'est plus proposée ; une
   donnée modifiée dans le module d'une variante ne repropose que les caméras de cette variante.
5. Chaque erreur de la liste ci-dessus : code non nul, message qui nomme ce qui manque.
6. `CACHE_RENDU` n'entre pas dans l'empreinte.

**Vérifications à faire et à consigner dans le rapport (sorties copiées) :**

- `python3 -m commun.rendu_cache liste entree/amenagement principale 64` et `… victor 64` : sortie vide (le fichier
  `cache/empreintes.json` du worktree est la copie de celui du dépôt).
- `python3 -m commun.rendu_cache variantes entree/amenagement` : `principale victor`.
- `just --dry-run entree-rendu 64` et `just --dry-run entree-apercu` s'affichent sans erreur ; puis
  `just entree-rendu 64` lancé pour de bon : il doit dire « rien à rendre » pour les deux variantes, ne lancer aucun
  rendu, reconstruire la page ; `git status --short site/` reste vide.
- `git diff --stat refonte -- pieces/entree/amenagement/rendu.py 3d/rendu.py` : vide.
- La suite de tests complète.

**Dans le rapport**, donne aussi, prêt à recopier dans un mode d'emploi : la déclaration `CACHE_RENDU` d'un document
avec variantes, d'un document sans variante, d'un meuble à caméras propres ; le texte du modèle des deux recettes.
