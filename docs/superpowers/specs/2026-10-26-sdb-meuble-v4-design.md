# Meuble linge SDB, document V4 : refonte des pages, budget et matériaux

## Intention

La V5.24 (plan en hêtre massif, caisson haut en contreplaqué de 12, vernis marin partout) revient à 645 €. Le client
trouve ce total trop élevé : le meuble est surprotégé, surtout le caisson haut, qui ne prend presque pas d'eau. Il
trouve aussi la documentation trop chargée. La V4 du document repart sur une base plus simple :
- moins de pages et de vues, chaque meuble sur sa propre page ;
- des matériaux choisis au juste niveau de protection ;
- un budget tenu ;
- une ossature basse plus rigide.

## Objectifs

1. **Budget : 400 € TTC au maximum pour les deux meubles**, consommables et frais de livraison compris. Un plan livré
   avec 69 € de port ne passe pas : on privilégie ce qui se retire en magasin.
2. **Page principale** (remplace `sdb-meuble-v3.html`) :
   - une vue isométrique des deux meubles en place dans l'alcôve, avec la machine ;
   - le carrelage dessiné sur les murs jusqu'à 204 (`CARRELAGE`), avec sa hauteur cotée ou annotée ;
   - une note sur les matériaux qu'on peut acheter en commun pour les deux meubles, seulement si ça fait une économie
     (par exemple un même panneau ou un même pot) ;
   - une note : le L basculant peut être remplacé par deux paniers à roulettes Wenko Corno 18,5 × 40 × 60, 43 L
     (`CORNO` dans `modele.py`, 45 € pièce, relevé Amazon du client), sans porte ;
   - les liens vers les deux pages de meuble et le tableau des changements en fin de page.
3. **Deux pages, une par meuble** (meuble bas, caisson haut), construites de la même façon :
   - une vue isométrique du meuble seul ;
   - la notice de montage façon IKEA (étapes, pièces, quincaillerie, perçages : ce que fait déjà `montage.py`,
     découpé par meuble) ;
   - la découpe : liste de débit et calepinage ;
   - les matériaux et le prix : liste de courses par magasin, avec un total.
4. **Caisson haut** : peu ou pas exposé à l'eau. Lister les panneaux possibles en 16 ou 18 mm, avec pour chacun :
   - ses qualités, ses défauts et sa finition (un bois brut peut se peindre) ;
   - son prix et le magasin.

   En retenir un, le moins cher qui convient, et justifier le choix sur la page.
5. **Meuble bas** :
   - **Plan de travail** : en bois massif lamellé-collé abouté. Si le hêtre est mal adapté à la salle de bain (il
     travaille beaucoup avec l'humidité, de mémoire : à vérifier sur une source), prendre une autre essence et
     justifier le choix.
   - **Vernis marin** : 2 ou 3 couches, sur le plan seulement.
   - **Ossature** : la rendre plus rigide en tenant compte des tuyaux.

## Contraintes

- **Tuyaux** (relevé client du 26/10/2026), au mur du fond, derrière la machine, au droit du robinet du modèle (y = 74,
  à 41 du mur sud : le « milieu du mur » du client était approximatif, il confirme cette cote) :
  - évacuation à 60 du sol, par un **siphon en saillie** dans la lame de 5 cm entre le dos de la machine et le mur ;
  - arrivée juste sous le dessus de la machine (≈ 80) ; le tuyau monte au robinet d'arrêt qui reste dans la niche
    (`ROBINET`), par l'encoche du plan, inchangée.

  Un renfort ne doit croiser aucun des deux tuyaux ni empêcher de raccorder ou débrancher la machine. Choix de Claude :
  derrière la machine, entre environ 50 et 90 cm de haut, rien ne passe. Un rail bas au sol ou une traverse au ras du
  plan restent possibles s'ils ne coupent pas les flexibles. La saillie du siphon est à mesurer, et la notice le dit.
- **Rigidité** (le client craint les déformations et les vibrations) :
  - le meuble peut être **calé contre les murs nord et sud** (cales ou vérins horizontaux), sans vis dans le mur ;
  - le renfort doit contenir la déformation de gauche à droite, qu'aucune pièce ne tient aujourd'hui dans la zone de
    la machine, et ne transmettre aucune vibration (la machine ne touche jamais le meuble ; tapis antivibration).
- Le meuble bas reste sans fixation murale, profondeur totale ≤ 60, machine au sol. La géométrie du L basculant ne
  change pas : sacs, butée, angles. Les sacs restent à coudre par le client : la notice garde leurs cotes, la liste de
  courses garde la toile.
- **Budget** : rien n'est encore acheté. Les 400 € comprennent tout (toile, barres, port, découpe en magasin), sauf le
  plombier.
- Le caisson haut est chevillé au-dessus du carrelage, comme aujourd'hui.
- **Magasins** : Weldom Saint-Barnabé d'abord, puis Leroy Merlin et Castorama. Les prix et les stocks sont relevés en
  ligne et datés. Distinguer ce qui est vendu par l'enseigne (retrait en magasin) des vendeurs marketplace (livrés).
- **Source unique** : `3d/sdb/modele.py`. Les pages sont générées par `just sdb`, avec des pages HTML locales. Les
  règles des plans s'appliquent : tableau des changements en fin de page, version dans le kicker, ancres du sommaire
  (`3d/ancres.js`).

## Hors champ

- Les vues retirées : plan de l'alcôve, élévations, coupes, sections d'explications, comparatifs de prix, détail des
  sacs (patron, couture), capacités, « À vérifier sur place ». Leur contenu utile au montage passe dans la notice.
- La variante bacs à roulettes : bouton, dessins et calculs disparaissent ; il ne reste que la note.
- Les rendus Blender et la vidéo.

## À éviter

- Un total au-dessus de 400 €, ou un total qui oublie la livraison.
- De la protection anti-eau sur des faces qui n'en ont pas besoin.
- Un renfort qui gêne les tuyaux ou l'accès au robinet.
- Recopier des dimensions en dur dans les textes : tout se calcule depuis `modele.py`. En V5.24, le « 1134 » d'un
  vieux texte était faux.

## Ce que le client a décidé

- La structure des pages ci-dessus et le retrait de tout le reste.
- Le budget de 400 € maximum.
- Le L basculant seul, avec la note vers les Wenko Corno.
- Le vernis marin, 2 ou 3 couches.
- L'essence du plan : changer si le hêtre ne convient pas.
- Le caisson haut en 16 ou 18 mm, peint si c'est du bois brut.
- Les positions des tuyaux.

## Choix laissés au constructeur (signalés comme tels sur les pages)

- L'essence du plan, le panneau du caisson haut, le nombre de couches (2 ou 3) et le renfort de l'ossature, dans le
  respect du budget et des tuyaux.
- **Fichiers** (choix de Claude) : `sdb-meuble-v4.html` (page principale), `sdb-meuble-v4-bas.html`,
  `sdb-meuble-v4-haut.html`. La V3 est figée dans `archive/` et listée dans l'index avec ses dates, et l'index pointe
  vers la V4.
- **Numéro de version** (choix de Claude) : V6.0, pour continuer l'historique des changements du modèle, qui va jusqu'à
  V5.24.
