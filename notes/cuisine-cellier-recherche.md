# Cellier-buanderie : inventaire, agencements avec et sans lave-linge, recommandation

Sources lues : `cuisine-plan.html` (plans A l. 228-558, B l. 561-876, C l. 880-1198 ; coupes A-A l. 1247-1430 / 1896-2080 / 2544-2727 ; coupes C-C l. 1508-1594 / 2156-2242 / 2802-2888 ; options l. 222 et 1241, CSS l. 190, script l. 3225+) et `sdb-meuble-v2.html` (4 panneaux sm-d, sm-g, co-d, co-g).
Repère du plan : 1 unité = 1 cm, x vers l'est, y vers le sud. Dans les coupes, ordonnée SVG = 250 − h. En C-C, l'abscisse SVG = y du plan (nord à gauche). En A-A, l'abscisse SVG = x du plan.
Aucun fichier du projet n'a été modifié. Les cotes ont été vérifiées par un petit script (recouvrements de rectangles, distance au gond de la porte A) : `scratchpad/check.py`.

---

## 0. Le LL du cellier est-il redondant ? Oui.

`sdb-meuble-v2.html` prévoit un lave-linge 60 × 60 × 85 sous le plan filant de l'alcôve de la salle de bain dans **les quatre** panneaux (sur mesure / commerce × machine à droite / à gauche), avec robinet encastré à h 80 sous une trappe, évacuation côté lavabo et un circuit 20 A spécialisé. Le plan de cuisine prévoit en parallèle un LL « devant le ballon » dans le cellier, dans les trois variantes A, B et C. **Deux machines sont donc dessinées** : si le meuble de SdB V2 est réalisé, le LL du cellier fait double emploi et peut être supprimé. Inversement, si le client garde le LL au cellier, l'alcôve de la SdB devrait être redessinée sans machine (ce n'est pas le cas aujourd'hui).
Point à trancher (décision client) : il n'y a pas de sèche-linge dans la SdB (l'alcôve de 114 ne le permet pas). Sans LL au cellier, celui-ci peut accueillir plus tard un sèche-linge à la place exacte prévue pour le LL dans la solution L1 (voir § 3), si on garde les réservations.

---

## 1. Inventaire du cellier actuel (identique en A, B et C sauf la porte)

### 1.1 Emprises (plan)

| Élément | Emprise | Remarque |
|---|---|---|
| Cellier principal | x 317 → 434, y 0 → 100 (117 × 100) | |
| Coffrage de chute | x 418 → 434, y 0 → 18 | toute hauteur ; reçoit l'évac. évier (h ≈ 41) et LL |
| Niche du ballon | x 434 → 484, y 44 → 100 (50 × 56) | ballon Ø 50 centré (459, 72), suspendu h 70 → 200 ; nourrice, vannes, groupe de sécurité (GS) dessous, h 0 → 70 |
| Sas (A, C) | x 317 → 382, y 100 → 129 + tableau x 312 → 317, y 62 → 129 | mur du WC à x 382 au sud de y 100 ; frigo à y 129 |
| Sas (B) | x 323 → 382, y 100 → 122 | frigo à y 122, façades à x 323 |
| Étagères P30 | x 317 → 355, y 0 → 30 | 6 niveaux h 22, 60, 98, 136, 174, 212 |
| Râtelier balais / aspi | x 357 → 410, y 0 → 38, h 0 → 210 | tablette lessive h 150 (53 × 38) |
| LL 60 × 60 | x 374 → 434, y 40 → 100, façade ouest | hublot : arc r 48 jusqu'à x 326 |
| Réseaux | alim. EF/EC : nourrice (470, 52) → x 432 → mur nord y 4, h ≈ 28 ; évac. évier y 10, h 41-45 → chute (426, 10) ; évac. GS (446, 94) → (429, 94) → chute ; évac. LL (430, 42) → chute | tout passe au ras des murs nord et est, en partie basse |

**Surfaces de sol** (shoelace sur le polygone `cellf`) : A et C 1,67 m² (1,64 m² hors coffrage) ; B 1,56 m² (1,53 m²). Le LL en occupe 0,36 m², soit 22 %.

### 1.2 Rangement par niveau (existant)

| Hauteur | Ce qui est rangé | Linéaire | Accès |
|---|---|---|---|
| 0 → 150 | râtelier balais/aspi 53 | 53 | **17 directs** (x 357 → 374) ; **36 derrière le LL** (x 374 → 410), bras tendu de côté |
| 22 → 212 | 6 étagères P30 × 38 | 228 | bon |
| 85 | dessus du LL 60 × 60 | (dépose) | encombre si on y stocke |
| 150 | tablette lessive 53 × 38 | 53 | moitié derrière le LL |
| 85 → 250 au-dessus du LL | rien | 0 | **0,59 m³ vides** |
| 150 → 250 au-dessus du râtelier | rien (hors tablette) | 0 | 0,20 m³ vides |
| 200 → 250 au-dessus du ballon | rien | 0 | 0,14 m³ vides |

Total : **281 cm** de tablettes (228 P30 + 53 P38), surface de tablettes **0,89 m²**, râtelier 53 dont 36 en second rang.

### 1.3 Accès techniques (existant)

- **GS, nourrice, vannes** : sous le ballon (x 434, y 47 → 97, h 0 → 70), **entièrement masqués par le LL**. Il faut tirer la machine vers l'ouest sur toute sa profondeur, alors que le sas ne fait que 57 (x 317 → 374), et que les flexibles et le câble le permettent. De mémoire, non vérifié : les fabricants recommandent de manœuvrer le GS environ une fois par mois. Or ce n'est pas faisable en pratique.
- **Remplacement du ballon** (Ø 50) : il faut d'abord sortir le LL.
- **Chute** : coffrage dans l'angle nord-est, derrière l'extrémité du râtelier et la poche x 410 → 434, y 18 → 40 ; une éventuelle trappe de visite n'est accessible qu'en tendant le bras.
- **Robinet du LL** : piqué sur la nourrice, donc lui aussi derrière la machine.

### 1.4 Porte selon la variante

- **A (battante 60, baie y 62 → 127, gond (316, 125))** : le vantail balaie un quart de disque de rayon 60 (x 316 → 376, y 65 → 125) et se range à y 121 → 125, x 316 → 376. Le coin du LL (374, 100) est à 63,2 du gond, soit **3 cm de jeu**. Passage ≈ 56, ce qui oblige à passer le LL « de profil » ou à dégonder.
- **B (claustra côté cuisine)** : rien ne débat dans le cellier ; passage franc 60 ; sas réduit au sud (frigo à y 122).
- **C (pivotante-coulissante 65)** : la demi-feuille côté sas se range à x 314 → 346,5, y 123 → 127 ; elle ne débat presque pas dans le sas. Passage ≈ 61.

### 1.5 Défauts

1. Le GS et les vannes sont inaccessibles sans déplacer un appareil d'environ 70 kg (poids de mémoire, non vérifié).
2. Deux tiers du râtelier et la moitié de la tablette lessive sont en second rang, derrière le LL : c'est un **angle mort**.
3. La poche x 410 → 434, y 18 → 40, entre le coffrage, le mur est et le dos du LL, est morte.
4. Il y a 165 cm de hauteur perdue au-dessus du LL, plus le dessus de la niche.
5. Le hublot ouvert (jusqu'à x 326) barre tout le sas, et le balayage de la porte A frôle le LL (3 cm).
6. L'aspirateur-balai ne dispose que de 17 cm accessibles, sans prise de recharge dessinée.

---

## 2. Contraintes de vérification appliquées à toutes les propositions

- **Porte A** : rien à moins de 60,2 du gond (316, 125) dans le quart x ≥ 316, y ≤ 125 (rayon du vantail plus la diagonale de son épaisseur de 4), ni sur la bande de rangement y 121 → 125, x 316 → 376.
- **Porte C** : la bande x 314 → 347, y 119 → 129 reste libre.
- **Porte B** : le sas s'arrête à y 122 pour x ≥ 323.
- **Réseaux** : on garde une **gaine de 8** contre le mur nord (y 0 → 8) en partie basse, pour l'alim. h ≈ 28 et l'évac. Ø 40 h 41-45. Les étagères posées sur tasseaux passent devant ; un appareil devant le mur nord commence à y 8.
- **Ballon** : zone libre devant la niche, de 50 de large au minimum, au sol, jusqu'à h ≈ 120 (accroupi), et un chemin de 50 à 55 pour sortir un ballon Ø 50.
- **Circulation** : au moins 55 à 60 entre la baie et les rangements d'usage courant.
- Dimensions d'appareils, toutes de mémoire et non vérifiées : LL 59,5 × 55-60 × 85, hublot Ø ≈ 47 à charnière à gauche, ouvrant à 90-180° ; LL « slim » 60 × 40-47 ; sèche-linge pompe à chaleur 60 × 60 × 85 ; station murale d'aspirateur-balai ≈ 25 de large × 20-25 de saillie, h ≈ 110-130 ; bac de tri 30 L ≈ 30 × 40 × 35 ; planche à repasser pliée ≈ 35 × 120 × 6.

---

## 3. Agencements AVEC lave-linge

### L1 : LL au nord, au centre, et balais à l'entrée (compatible A, B, C) **[recommandé avec LL]**

| Élément | Plan | Hauteurs | Notes |
|---|---|---|---|
| Recoin balais | x 317 → 356, y 0 → 30 (rail sur le mur nord) | balais h 0 → 150 | 3 à 4 crochets |
| Station aspirateur-balai | sur le dos de la cloison, x 317 → 330, y 32 → 58 | h 0 → 130, prise 16 A à h 110 | la plus près de l'entrée ; à 66 du gond A ✓ |
| Étagères P30 au-dessus des balais | x 317 → 356, y 0 → 30 | h 165, 200, 235 | 3 × 39 = 117 (réserve, escabeau) |
| LL, façade sud | x 358 → 418, y 8 → 68 | h 0 → 85 | gaine 8 derrière ; à 2 du recoin, 0 du coffrage |
| Plan de dépose | x 358 → 418, y 0 → 68 | h 85 → 88 | panier, lessive |
| Étagères P40 au-dessus du LL | x 358 → 418, y 0 → 40 | h 125, 160, 195, 230 | 4 × 60 = 240 |
| Robinet et prise du LL | robinet sur l'EF du mur nord, remonté à h 95, x ≈ 412 ; prise 20 A h 100, x ≈ 400 | au-dessus du plan | accessibles sans bouger la machine |
| Évac. LL | siphon sur la chute, à travers la face ouest du coffrage (x 418), h ≈ 65 | | < 15 cm de flexible |
| Zone technique libre | x 374 → 434, y 68 → 100 + x 418 → 434, y 18 → 68 | sol → plafond | accès au GS |
| Tablette dans la niche | x 434 → 484, y 44 → 100 | h 215 (15 au-dessus du ballon), démontable | réserve 50 |

- **Vérifications** : aucun recouvrement ; coin du LL (358, 68) à **70,8** du gond A, soit 11 cm de jeu (au lieu de 3). Le hublot ouvert à 90° (x ≈ 360, y 68 → 116) reste à 5 du vantail A rangé. Devant le LL, le dégagement est de 61 jusqu'au frigo, 53 avec la porte A ouverte.
- **Linéaire** : tablettes 117 (P30) + 240 (P40) + 50 (niche) = **407 cm**, soit **1,61 m²** de tablettes (au lieu de 281 cm et 0,89 m²), plus le plan de dépose de 0,41 m². Balais : 39 de rail et la station aspi, **tout en premier rang** (au lieu de 17 directs + 36 masqués).
- **Ballon** : le GS est accessible **sans déplacer la machine**, mais par un dégagement de 32 de large (y 68 → 100), qui s'élargit à 82 contre le mur est (x 418 → 434). On s'y accroupit de biais : c'est juste. Avec un LL de 55 de profondeur et une gaine de 6, la façade passe à y 63 et le dégagement à 37. Pour **remplacer le ballon**, il faut sortir le LL (comme aujourd'hui).
- **Avantages** : un seul dessin pour A, B et C. Le LL reste collé à la chute. Les balais sont à l'entrée. Le volume au-dessus du LL sert. Les robinet et prise sont accessibles.
- **Inconvénients** : le recoin balais fait 41 de large sur 68 de profondeur (on y plonge le bras). L'accès au GS reste étroit. Le hublot ouvert barre le sas pendant le chargement.

### L2 : LL au nord-ouest, balais devant la zone technique (B et C ; A seulement avec un LL « slim »)

| Élément | Plan | Hauteurs |
|---|---|---|
| LL, façade sud | x 318 → 378, y 8 → 68 | h 0 → 85, plan de dépose h 88 (x 317 → 380, y 0 → 68) |
| Étagères P40 au-dessus | x 317 → 380, y 0 → 40 | h 125, 160, 195, 230 : 4 × 63 = 252 |
| Rail balais et station aspi | x 380 → 418, y 0 → 30 (station x 392 → 418, prise h 110) | h 0 → 150 |
| Crochets (pelle, raclette, seau) | mur est x 424 → 434, y 18 → 44 | h 100 → 180, au-dessus des tuyaux |
| P30 au-dessus des balais | x 380 → 418, y 0 → 30 | h 175, 210, 240 : 3 × 38 = 114 |
| Zone technique et balais | x 380 → 434, y 30 → 100 (**54 × 70**) | libre |
| Tablette dans la niche | x 434 → 484 | h 215 |

- **Vérifications** : aucun recouvrement en B et C. **En A, conflit** : le coin du LL (318, 68) est à 57,0 du gond, donc dans le balayage. En A, il faudrait un LL slim (façade à y ≤ 61 : coin à 63 ✓) ou décaler le LL à x ≥ 340, ce qui détruit le reste.
- **Linéaire** : 252 + 114 + 50 = **416 cm, 1,63 m²**. Rail balais 38 + 24 = 62, tout en premier rang.
- **Ballon** : excellent. Zone de 54 × 70 devant la niche, et chemin de 70 pour sortir le ballon sans toucher au LL.
- **Avantages** : le meilleur accès au GS et aux balais. Le LL se charge depuis la baie.
- **Inconvénients** : il n'est pas compatible avec la porte A en LL standard. Le flexible d'évacuation fait environ 1 m le long du mur nord (dans la gaine) jusqu'à la chute. Le hublot ouvert (charnière côté ouest) barre la baie pendant le chargement.

### L3 : colonne LL + sèche-linge superposés (« buanderie complète ») à la place de L1 (A, B, C)

- Même emprise que L1 : x 358 → 418, y 8 → 68. La colonne mesure environ 173 de haut (85 + 85 + kit de superposition 3, de mémoire, non vérifié). Hublot du sèche-linge à h ≈ 110 → 165.
- Au-dessus : P40 à h 195 et 230 (2 × 60 = 120). Balais, P30 au-dessus des balais et niche comme en L1.
- **Linéaire** : 117 + 120 + 50 = 287 cm, 1,07 m². C'est l'équivalent de l'existant, mais sans angle mort.
- Sèche-linge pompe à chaleur : prise 16 A (circuit spécialisé, de mémoire, non vérifié) ; condensats dans le bac ou sur le siphon du LL.
- **Intérêt** : seulement si le client renonce au LL de la SdB, ou veut sécher au cellier. Sinon, c'est la même place que celle réservée au sèche-linge dans la solution « sans LL » (voir § 4).

Variante minimale (non retenue) : on garde le LL devant le ballon, posé sur un socle à roulettes, et on échange étagères et balais. Le coût est minimal, mais le GS reste derrière la machine et les tablettes x 374 → 418 restent en second rang. Elle ne répond pas à la contrainte « accessible ».

---

## 4. Agencements SANS lave-linge (le LL part dans la SdB)

### S1 : garde-manger P40 au nord, balais à l'entrée, zone technique dégagée (A, B, C) **[recommandé sans LL]**

| Élément | Plan | Hauteurs | Notes |
|---|---|---|---|
| Rail balais | x 317 → 356, y 0 → 30 | h 0 → 150 | comme L1 |
| Station aspirateur-balai | dos de la cloison, x 317 → 330, y 32 → 58 | prise 16 A h 110 | à 66 du gond A ✓ |
| P30 au-dessus des balais | x 317 → 356, y 0 → 30 | h 165, 200, 235 | 3 × 39 = 117 |
| **Garde-manger P40** | x 357 → 418, y 0 → 40 (tasseaux, tuyaux derrière) | sol + 6 tablettes h 40, 75, 110, 145, 180, 215 | 6 × 61 = 366 ; au sol : 2 bacs de tri 30 L (x 359 → 387 et 389 → 417) ou packs d'eau |
| Zone technique libre | x 357 → 434, y 40 → 100 (**77 × 60**) + niche | | GS, vannes, nourrice et chute en accès direct |
| Mur sud (x 384 → 426) | planche à repasser et escabeau pliant accrochés à plat, y 92 → 100 | h 20 → 160 | laisse 52 libres devant la niche ; l'escabeau sert aux tablettes h 215-235 |
| Crochets | mur est x 424 → 434, y 18 → 44 | h 120 → 180 | sacs, cabas |
| Tablette dans la niche | x 434 → 484, y 44 → 100 | h 215, démontable | 50 |

- **Vérifications** : aucun recouvrement ; tout est à plus de 72 du gond A ; la zone C et le sas B sont intacts. Le chemin pour sortir le ballon fait 60 (y 40 → 100), ou 52 avec la planche accrochée.
- **Linéaire** : 117 + 366 + 50 = **533 cm, 2,09 m²** de tablettes (**× 2,3** par rapport à l'existant), plus le niveau sol du garde-manger (61 × 40). Balais : 39 + station aspi, tout en premier rang.
- **Avantages** : aucun angle mort (les tablettes P40 font face à 60 de dégagement, et les balais sont à l'entrée). Le ballon et le GS sont en accès direct et debout, la chute aussi. Rien à dégonder pour faire passer une machine. Un seul dessin pour A, B et C.
- **Inconvénients** : 0,46 m² de sol restent vides (c'est voulu, pour la maintenance et la circulation). Les tablettes h 215 se prennent avec l'escabeau.
- **Réversible** : si on laisse l'alimentation bouchonnée, le piquage d'évacuation obturé et le circuit 20 A, un sèche-linge ou un LL pourra reprendre plus tard la place x 358 → 418, y 8 → 68 (c'est la solution L1). Il suffit d'enlever les 3 tablettes basses du garde-manger.

### S2 : étagères P30 sur toute la longueur nord, balais au mur sud (A, B, C)

| Élément | Plan | Hauteurs |
|---|---|---|
| Étagères P30 | x 317 → 418, y 0 → 30 | 6 niveaux h 22, 60, 98, 136, 174, 212 : 6 × 101 = 606 |
| Rail balais et station aspi | mur sud (face nord du mur du WC), x 384 → 434, y 75 → 100 (aspi x 384 → 410) | h 0 → 150, prise h 110 sur le mur du WC (nature du mur à vérifier) |
| Zone technique | x 384 → 434, y 30 → 75 (50 × 45) | libre |
| Niche | h 215 | 50 |

- **Vérifications** : aucun recouvrement ; le rail balais est à 72 du gond A ✓.
- **Linéaire** : **656 cm, 2,10 m²**. C'est le plus grand linéaire, mais en P30 (rien ne se perd au fond).
- **Ballon** : 45 de dégagement devant la niche. Pour sortir le ballon, on décroche 1 ou 2 balais (on retrouve alors 70).
- **Inconvénients** : les balais sont au fond, dans le dégagement du ballon, et la prise est à poser sur le mur du WC. Il n'y a pas de tablette profonde pour les packs et le petit électroménager.

### S3 : « office » complet : S1 + colonne de sas + séchage (B et C seulement)

- S1, plus une **colonne P25 dans le sas**, contre le mur du WC (face ouest), x 357 → 382, y 100 → 129 en C (y 100 → 122 en B), avec 6 tablettes de 29 (ou 22), soit environ 170 (ou 130) cm. Usage : produits d'entretien, bouteilles, casier à vin. La colonne est **incompatible avec A** : (357, 100) est à 48 du gond, dans le balayage, et sur la bande de rangement du vantail.
- **Étendoir de plafond à poulie** au-dessus de la zone technique, x 384 → 434, y 40 → 100, remonté à h ≥ 205 (le linge pend jusqu'à h ≈ 140, au-dessus d'une personne accroupie devant le GS). À condition que le cellier soit ventilé (VMC) : à vérifier.
- Casier à vin plutôt que cave réfrigérée : le ballon chauffe la pièce (de mémoire, non vérifié : environ 1 à 2 kWh/j de pertes pour un ballon de cette taille). Pas de cave de garde ici.
- **Linéaire** : S1 + 170, soit environ **700 cm, 2,5 m²**.
- **Inconvénients** : uniquement B et C. Le sas se réduit à 40 entre la baie et la colonne, mais le passage principal y 62 → 100 reste de 38 à 117 de large selon x. Le séchage rend le local humide.

---

## 5. Conséquences de la suppression du LL du cellier (plomberie, électricité) et gains

**Plomberie**
- **Alimentation** : la sortie du LL sur la nourrice est fermée par sa vanne et bouchonnée (bouchon laiton), ce qui garde la réservation. L'alimentation de la cuisine (EF et EC depuis la nourrice, le long du mur nord) ne change pas.
- **Évacuation** : on supprime le flexible et le siphon du LL (tracé `M430 42 L430 16`) et on **obture le piquage** sur la chute (bouchon à visser ou obturateur). Un siphon laissé sans usage se dessèche et laisse remonter les odeurs. L'évacuation du GS (entonnoir siphonné, tracé `M446 94 … L429 15`) **doit rester** : vérifier sur place qu'elle ne partageait pas le siphon du LL. L'évacuation de l'évier ne change pas.
- **Côté SdB**, la machine a sa propre alimentation (robinet encastré h 80) et sa propre évacuation, déjà prévues dans `sdb-meuble-v2.html`.

**Électricité** (de mémoire, NF C 15-100, non vérifié, à valider par l'électricien)
- Le LL exige un circuit spécialisé 20 A en 2,5 mm² sous 30 mA. Celui de la SdB est déjà prévu dans le document SdB. Le circuit du cellier devient libre. Trois possibilités : (a) le garder en attente, étiqueté « LL / sèche-linge », ce qui est réversible ; (b) le requalifier en circuit de prises pour alimenter la station de l'aspirateur-balai, si le tableau le permet ; (c) le récupérer pour la SdB si le cheminement est plus court que depuis le tableau.
- Il faut ajouter une prise 16 A à h 110 près de la station aspi (S1 : sur le mur nord à x ≈ 322, ou en saillie sur la cloison de 5).

**Gains**
- 0,36 m² de sol et 0,59 m³ de volume rendus au rangement ou au dégagement.
- GS, vannes et nourrice en accès direct et debout ; chemin de 60 pour remplacer le ballon.
- Tablettes : 533 cm et 2,09 m² (S1), au lieu de 281 cm et 0,89 m² ; balais 100 % en premier rang ; plus d'angle mort derrière le LL ni dans la poche x 410 → 434.
- Porte A : plus de LL à faire passer par le passage de 56 (il fallait dégonder) ni de battant à 3 cm du LL.
- Plus de bruit d'essorage ni de risque de fuite contre la cuisine au parquet chêne ; un piquage et un circuit en moins.
- Les seules pertes sont la buanderie et le séchage au cellier. L'étendoir S3 ou un futur sèche-linge (réservations conservées) les compensent.

---

## 6. Recommandations et ce qu'il faut dessiner

**Avec LL : L1.** C'est la seule solution compatible avec les trois portes sans changer de machine, et le LL reste contre la chute. Si le client retient B ou C, L2 est plus confortable : zone de 54 × 70 devant le ballon, contre 32.
**Sans LL : S1**, compatible avec A, B et C. C'est elle qui donne le plus de rangement utile, sans angle mort, avec un accès direct au ballon. La place de la machine reste réservée (réversible).

### 6.1 Mécanique de l'option « Cellier : avec LL / sans LL »

Elle reprend le mécanisme existant des options « Porte d'entrée » et « Table ». Ce mécanisme est câblé (`data-door`, `data-tbl`, CSS l. 190, script), mais aucune balise ne porte encore `door-*` ni `tbl-*`.
1. `<html lang="fr" data-door="w" data-tbl="sq" data-cel="ll">` (l. 2).
2. CSS l. 190 : ajouter `,:root[data-cel="ll"] .cel-sans,:root[data-cel="sans"] .cel-ll{display:none}`.
3. Dans les **deux** barres `.opts` (l. 222 et 1241) : `<span class="optl">Cellier</span><span class="seg"><button type="button" data-opt="cel" data-val="ll" aria-pressed="true">avec LL</button><button type="button" data-opt="cel" data-val="sans" aria-pressed="false">sans LL (LL en SdB)</button></span>`.
4. Script : ajouter `['cel',/^(ll|sans)$/]` au tableau de restauration `localStorage`.
5. Dans chacun des **9 SVG** (plan A, B, C ; A-A A, B, C ; C-C A, B, C), envelopper les éléments du cellier dans `<g class="cel-ll">…</g>` et `<g class="cel-sans">…</g>`. Dans les légendes `p.cap`, mettre les phrases propres à chaque option dans `<span class="cel-ll">` et `<span class="cel-sans">`. Règle [[variantes-toutes-vues]] : les coupes basculent aussi.

### 6.2 Plan (à répéter dans les panneaux a, b, c ; seule la porte diffère)

À **supprimer** (ou à déplacer dans le groupe de l'ancien dessin) : `rect.tall x317 y0 38×30` et ses deux textes (« Étagères P30 », « 6 niveaux ») ; `rect.broom x357 y0 53×38`, ses textes, le cercle (366, 31) et le texte « tablettes lessive au-dessus (h 150) » ; `rect.ll x374 y40 60×60`, son cercle, ses 3 textes, l'arc du hublot `M374 48 A48…` et le texte « hublot » ; le tracé `pout M430 42 L430 16`.

**Groupe `cel-ll` (L1)** :
- `rect.broom x317 y0 w39 h30` (« Balais ») ; station aspi : `rect.broom x317 y32 w13 h26` et `circle.app cx323 cy45 r5`, texte « aspi-balai · prise h 110 ».
- `rect.upper x317 y0 w39 h30` (P30 h 165 / 200 / 235, en projection).
- `rect.tech x358 y0 w60 h8` (gaine) ; `rect.ll x358 y8 w60 h60` ; `circle.app cx388 cy38 r15` ; textes « LL » et « 60 × 60 · façade sud ▾ ».
- Hublot : `path.swing d="M408 68 A48 48 0 0 1 360 116 L360 68 Z"`.
- `rect.upper x358 y0 w60 h40` (P40 h 125 → 230) ; texte « plan h 88 · 4 étagères P40 ».
- Évacuation LL : `path.pout d="M414 12 L421 12"` (vers la chute (426, 10)) ; alim. : `line.pin x1=412 y1=4 x2=412 y2=8`.
- Zone technique : `polygon points="374,68 418,68 418,18 434,18 434,100 374,100"` en tireté `var(--flow)`, avec le texte « accès ballon / GS 32 » ; cote `dim` y 68 → 100 à x ≈ 400.
- Niche : `rect.upper x434 y44 w50 h56`, avec le texte « tablette h 215 ».
- Texte `wt2` (l. 423, etc.) : « LL : alim. EF du mur nord, robinet et prise 20 A au-dessus du plan ; évac. dans la chute voisine ».

**Groupe `cel-sans` (S1)** :
- Balais, station aspi et P30 au-dessus : comme en L1.
- `rect.tall x357 y0 w61 h40 style="fill-opacity:.7"` ; textes « Garde-manger P40 » et « sol + 6 niveaux » ; deux bacs en tireté, `rect x359 y4 w28 h34` et `rect x389 y4 w28 h34`, avec le texte « tri 2 × 30 L ».
- Zone technique : `rect x357 y40 w77 h60` en tireté `var(--flow)`, avec le texte « libre 77 × 60 · ballon, GS, chute » ; cote y 40 → 100 « 60 ».
- Mur sud : `rect.cab x384 y92 w42 h8`, avec le texte « planche, escabeau (à plat) ».
- Crochets mur est : `rect.cab x424 y18 w10 h26`. Niche : `rect.upper x434 y44 w50 h56`.
- Bouchons : petit `circle` ou croix à (430, 42) (piquage LL obturé) et note « alim. LL bouchonnée sur la nourrice ».
- Texte `wt2` : « LL déplacé en SdB : piquage obturé, circuit 20 A en attente ».

**Cotes de la ligne y = −62** (à dédoubler par option) :
- L1 : `317→356` « balais 39 », `358→418` « LL 60 », `418→434` « 16 ».
- S1 : `317→356` « balais 39 », `357→418` « garde-manger 61 », `418→434` « 16 ».
- Les cotes actuelles 38, « balais 53 » et 24 disparaissent dans les deux options.

**Textes propres à chaque porte** :
- A : légende « son battant passe à 3 cm du coin du LL » → L1 : « à 11 cm du coin du LL » ; S1 : supprimé. Le texte (404, 378) « dégondée : 60 pour passer le LL » ne reste qu'en `cel-ll`.
- B : « le sas garde 57 entre la cloison et le LL » et le paragraphe « Cellier : … » de la légende sont à réécrire pour chaque option. Le label « sas 57 » (344 / 350, 90) devient « dégagement 61 » (L1) ou « libre 77 × 60 » (S1).
- Les `aria-label` des plans mentionnent « lave-linge devant le ballon et zone balais au nord » : à rendre neutres, ou à doubler.
- La légende l. 1212 « Meuble à balais » ne change pas.

### 6.3 Coupe A-A (y = 114, vue vers le nord ; on voit x 317 → 382, le mur du WC masque la suite)

À **supprimer** : le `<g>` des 6 lignes P30 (x 317 → 355, SVG y 228 … 38) et le texte « P30 » ; `rect.broom x357 y40 25×210`, ses manches `M362 60…`, la tablette `rect.cab x357 y98` et le texte « balais » ; `rect.ll x374 y165 8×85` et le texte « LL ». Le titre `h3` et la légende sont à adapter (« râtelier à balais et LL au fond »).

**`cel-ll` (L1)** :
- Balais : `rect.broom x317 y100 w39 h150` (h 0 → 150), manches `path d="M326 105 V245 M335 110 V245 M344 105 V245"`.
- P30 au-dessus : `line.app x317 → 356` à SVG y 85, 50, 15.
- LL de face (portion visible) : `rect.ll x358 y165 w24 h85`, plus `circle.app cx388 cy205 r18`, que le mur du WC, dessiné après, coupera.
- Plan : `rect.cab x358 y162 w24 h3`. P40 : `line.app x358 → 382` à SVG y 125, 90, 55, 20.
- Cotes à droite : « 85 LL » (conservée), « 88 plan », « 125 · 160 · 195 · 230 P40 », « 150 balais ».

**`cel-sans` (S1)** :
- Balais et P30 au-dessus : comme L1.
- Garde-manger : `line.app x357 → 382` à SVG y 210, 175, 140, 105, 70, 35, et un bac `rect x359 y212 w23 h38` en tireté.
- Cotes : « 40 → 215 garde-manger », « 150 balais » ; la cote « 85 LL » disparaît.

### 6.4 Coupe C-C (x = 340, vue vers l'est ; abscisse = y du plan)

À **supprimer** : `rect.broom x0 y40 38×210`, les manches `M8 60…`, l'aspi `rect x28 y150 8×96`, la tablette `rect.cab x0 y98 38×2` et le texte « râtelier » ; `rect.ll x40 y165 60×85`, ses 2 cercles, son afficheur `rect x44 y170` et le texte « LL » ; le texte « (derrière le LL) » ; les cotes « 150 tablette », « 210 râtelier », « râtelier 38 », « LL 60 (au fond) ».
Le plan de coupe x 340 **coupe désormais la zone balais** (x 317 → 356) dans les deux options. Les étagères P30 coupées actuelles (`g.cabcut`, 6 niveaux) sont remplacées.

**`cel-ll` (L1)** :
- Balais coupés : `rect.broom x0 y100 w30 h150`, manches.
- P30 coupées : `g.cabcut` avec `rect x0 w30 h2.5` à SVG y 85, 50, 15.
- Au fond, LL de profil : `rect.ll x8 y165 w60 h85`, avec le texte « LL (profil) ».
- Plan : `rect.cab x0 y162 w68 h3`. P40 : `rect.cab x0 w40 h2.5` à SVG y 125, 90, 55, 20.
- Ballon : `rect.ecs` existant (x 47 → 97, SVG y 50 → 180), passé en opacité 1, dessiné **avant** le LL. Nourrice et GS : `rect.tech x50 y185 w44 h45`, avec le texte « nourrice · gr. sécu. » (partiellement masqué par le LL jusqu'à y 68).
- Tablette de niche : `rect.cab x44 y33 w56 h2.5` (h 215).
- Cotes : « 88 plan », « 125 … 230 P40 », « 150 balais », « 215 niche » ; en bas, `x8→68` « LL 60 (profil) » et `x68→100` « accès 32 ».

**`cel-sans` (S1)** :
- Balais et P30 coupés : comme L1.
- Au fond, garde-manger de profil : `rect.cab x0 w40 h2.5` à SVG y 210, 175, 140, 105, 70, 35, et un bac `rect x2 y215 w36 h35` en tireté.
- Ballon et nourrice/GS entièrement visibles, avec le texte « (accès direct) » ; tablette de niche h 215.
- Planche et escabeau de profil : `rect.cab x92 y90 w8 h140`.
- Cotes : « 40 → 215 garde-manger », « 150 balais », « 215 niche » ; en bas, `x0→40` « P40 » et `x40→100` « libre 60 ».

Légendes C-C : « 99 cm restent libres » (y 30 → 129) reste vrai dans les deux options (91 en A porte ouverte, 93 en C).

---

## 7. À vérifier sur place

- Position exacte du GS et de son entonnoir sous le ballon, et existence d'un siphon commun avec le LL.
- Nature de la cloison de 5 (charge des tablettes, boîte de prise) et du mur du WC.
- Trappe de visite de la chute dans le coffrage.
- Profondeur réelle du LL du client (≤ 57 pour une façade à y ≤ 65).
- VMC du cellier (avant tout étendoir).
- Tableau électrique : réaffectation possible du circuit 20 A.
