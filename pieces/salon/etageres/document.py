# Salon, étagères sur montants percés du mur ouest : montants, tablettes, chevilles, les quatre dispositions étudiées,
# l'emprise sur le plan du salon, les bruts achetés, les matériaux, la tenue, VERSION et CHANGEMENTS de la page
# salon-etageres.html.
#
# Ce fichier ne contient que des données, reprises de 3d/salon/modele.py (section ②) et de 3d/salon/etageres.py. Il
# est le seul à décrire les étagères : le plan du salon (amenagement/document.py) l'importe. Les volumes 3D sont
# dans volumes.py ; les autres calculs (débit, charges, achats d'une disposition) et les dessins restent au
# générateur de la page.
#
# Cotes en cm, repère du salon : x vers l'est depuis le mur ouest, y vers le sud depuis le mur nord, z depuis le sol.

import math

from commun.modele import Camera
from pieces.salon.enfilade.document import ENFILADE
from pieces.salon.piece import Bloc

VERSION = "V1.8"
DATE = "29/10/2026"          # relevé des prix (WebSearch, fiches en ligne ; stock non vérifié)

# ------------------------------------------------------------------ le meuble (modele.py, section ②, V4.21)
# Système vu par le client : montants verticaux en pin massif peint en noir, percés à pas régulier, qui ne touchent
# ni le sol ni l'enfilade (ils « flottent » au-dessus, vissés au mur) ; tablettes en chêne massif posées sur deux
# montants ou plus, en composition décalée. Pas de 55 (demande 50 à 60) : 5 montants centrés sur l'enfilade.
# V4.23, choix du client : tablette ENTAILLÉE autour de chaque montant, elle touche le mur et le montant la traverse.
# Elle est pincée par deux chevilles en acier Ø 10 qui traversent le montant d'un flanc à l'autre et dépassent de
# 1,5 de chaque côté sous les joues de l'entaille : une devant, dessous (elle porte), une derrière, dessus (elle
# empêche la tablette de basculer vers l'avant). Deux colonnes de trous sur les flancs du montant, décalées de
# l'épaisseur de la tablette plus une cheville : les trous se voient de biais, pas de face.
MONTANTS = dict(n=5, pas=55, l=4.5, p=7, z0=110, z1=229, trou=1.0, pas_trous=5, x_av=5, x_ar=2,
                bois="pin massif raboté, peint en noir mat")
_c = (ENFILADE["y0"] + ENFILADE["y1"]) / 2
MONTANTS["axes"] = [_c + (i - (MONTANTS["n"] - 1) / 2) * MONTANTS["pas"] for i in range(MONTANTS["n"])]
# tablettes : chêne massif 2,7 (lamellé-collé abouté), 32 de profondeur depuis le mur (deux bandes par plan de
# travail de 65), entaille 4,7 × 7,1 (2 de jeu en largeur, 1 en profondeur) au droit de chaque montant, 12 de
# débord au-delà de l'axe du dernier montant
ETAGERES = dict(p=32, ep=2.7, debord=12, x0=0, entaille=(MONTANTS["l"] + 0.2, MONTANTS["p"] + 0.1),
                cheville=MONTANTS["l"] + 3, cheville_ext=1.5)
ETAGERES["x1"] = ETAGERES["x0"] + ETAGERES["p"]
# rainure à la défonceuse sous chaque tablette, au droit de la cheville avant, sur 9 centrés sur chaque entaille :
# la cheville avant y est prise (ni la tablette vers la pièce, ni la cheville en long ne bougent) ; largeur, profondeur
ETAGERES["rainure"] = dict(l=1.1, prof=0.5, long=9.0)
# composition (dessus de la tablette, premier montant, dernier montant), montants numérotés 0 → 4 du nord au sud ;
# niveaux à 35 l'un de l'autre (pas des trous), tablette du haut à 32 du plafond pour des objets
TABLETTES = [(122, 0, 4), (157, 1, 4), (192, 0, 2), (192, 3, 4), (222, 1, 3)]
ETAGERES["zs"] = sorted({z for z, _, _ in TABLETTES})
# dessus possibles, sur toute la hauteur percée : de 122 (la lampe de l'enfilade passe dessous) à 222 (cheville
# arrière sous le haut du montant), de 5 en 5 ; toutes les dispositions ci-dessous tiennent sur les mêmes montants
NIVEAUX = (122, 222)
# Dispositions étudiées (page Étagères) : (dessus, premier, dernier montant), comme TABLETTES. La première est
# celle du plan (TABLETTES) ; les autres n'utilisent que deux longueurs : 134 (deux travées) et 79 (une travée).
# Seules les tablettes distinguent les dispositions : montants, trous, chevilles et bruts sont communs.
DISPOSITIONS = [
    dict(cle="actuelle", nom="Actuelle", tablettes=list(TABLETTES),
         idee="La composition du plan du salon : cinq tablettes de quatre longueurs (244, 189, 134, 79)."),
    dict(cle="rangs", nom="Rangs", tablettes=[(122, 0, 2), (122, 3, 4), (157, 0, 1), (157, 2, 4),
                                              (192, 0, 2), (192, 3, 4), (222, 0, 1), (222, 2, 4)],
         idee="Quatre rangs à 35, 35 et 30 ; chacun d'une longue et d'une courte, le vide change de travée d'un rang "
              "à l'autre, comme un appareil de briques."),
    dict(cle="decalee", nom="Décalée", tablettes=[(122, 0, 2), (137, 2, 4), (152, 0, 1), (167, 3, 4),
                                                  (182, 0, 2), (197, 2, 4), (212, 0, 1), (222, 3, 4)],
         idee="Deux demi-murs décalés de 15 en hauteur : les longues montent en zigzag autour du montant du milieu, "
              "les courtes aux bouts libèrent deux niches de 57 pour les grands formats."),
    dict(cle="escalier", nom="Escalier", tablettes=[(122, 3, 4), (137, 2, 3), (152, 1, 2), (167, 0, 1),
                                                    (162, 3, 4), (177, 2, 3), (192, 1, 2), (207, 0, 1),
                                                    (122, 0, 2), (207, 2, 4)],
         idee="Deux volées de courtes qui montent de 15 par travée vers le nord, une longue en bas au nord et une en "
              "haut au sud ; tout le mur à moins de 210."),
]
# trous : colonne avant sous les tablettes (axe à une demi-cheville sous le dessous), colonne arrière au-dessus
_r = MONTANTS["trou"] / 2
_zz = range(NIVEAUX[0], NIVEAUX[1] + 1, MONTANTS["pas_trous"])
MONTANTS["trous_av"] = [z - ETAGERES["ep"] - _r + ETAGERES["rainure"]["prof"] for z in _zz]
MONTANTS["trous_ar"] = [z + _r for z in _zz]
MONTANTS["decalage"] = ETAGERES["ep"] + MONTANTS["trou"] - ETAGERES["rainure"]["prof"]

# emprise sur le plan et les coupes du salon (disposition du plan, TABLETTES) : montants, puis tablettes
BLOCS = []
for _i, _y in enumerate(MONTANTS["axes"]):
    BLOCS.append(Bloc("montant", f"montant_{_i + 1}", 0, MONTANTS["p"], _y - MONTANTS["l"] / 2, _y + MONTANTS["l"] / 2,
                      MONTANTS["z0"], MONTANTS["z1"]))
ETAGERES["tablettes"] = []
for _i, (_z, _a, _b) in enumerate(TABLETTES):
    _y0, _y1 = MONTANTS["axes"][_a] - ETAGERES["debord"], MONTANTS["axes"][_b] + ETAGERES["debord"]
    ETAGERES["tablettes"].append((_z, _y0, _y1, _b - _a + 1))
    BLOCS.append(Bloc("etagere", f"etagere_{_i + 1}", ETAGERES["x0"], ETAGERES["x1"], _y0, _y1,
                      _z - ETAGERES["ep"], _z, etiq="②" if _i == 0 else ""))
METRES_ETAGERES = sum(y1 - y0 for _, y0, y1, _ in ETAGERES["tablettes"]) / 100
CHEVILLES = 2 * sum(n for *_, n in ETAGERES["tablettes"])
ENTAILLES = sum(n for *_, n in ETAGERES["tablettes"])
CHARGE_LIVRES = 25          # kg par mètre de tablette pleine de livres (ordre de grandeur)

# vérifications de l'étude (ordres de grandeur, g = 9,81) : un montant reprend 55 de tablette pleine ; la charge
# est au milieu de la partie devant le montant ; la tablette pivote sur la cheville avant, la cheville arrière la
# retient (couple sur l'écart des deux colonnes)
_q = CHARGE_LIVRES * MONTANTS["pas"] / 100 * 9.81                      # N par montant et par tablette
_xq = (MONTANTS["p"] + ETAGERES["x1"]) / 2                             # cm, centre de la charge depuis le mur
_m = _q * (_xq - MONTANTS["x_av"]) / 100                               # N·m autour de la cheville avant
_ar = _m / ((MONTANTS["x_av"] - MONTANTS["x_ar"]) / 100)               # N, cheville arrière (vers le haut)
_av = _ar + _q                                                         # N, cheville avant (vers le bas)
_w = math.pi * 10 ** 3 / 32                                            # module de flexion d'une cheville Ø 10, mm³
ETUDE_MONTANTS = dict(
    effort=_q, moment=_m, arriere=_ar, avant=_av,
    contrainte=_av / 2 * ETAGERES["cheville_ext"] * 10 / 2 / _w,       # MPa, bout de cheville en porte-à-faux
    pression=_av / (MONTANTS["trou"] * 10 * MONTANTS["l"] * 10),       # MPa sur le pin, sur toute la largeur
    joue=_av / 2 / (MONTANTS["trou"] * 10 * ETAGERES["cheville_ext"] * 10),  # MPa sur le chêne, sous une joue
    poids=METRES_ETAGERES * CHARGE_LIVRES + METRES_ETAGERES * ETAGERES["p"] / 100 * 0.027 * 700
    + 5 * 1.2 * 0.045 * 0.07 * 450,
    vis=3,                                                             # vis par montant
)
ETUDE_MONTANTS["par_montant"] = ETUDE_MONTANTS["poids"] / MONTANTS["n"]

# ------------------------------------------------------------------ fabrication (etageres.py)
RA_COTE = (ETAGERES["rainure"]["long"] - ETAGERES["entaille"][0]) / 2   # rainure de chaque côté d'une entaille

# bruts achetés (sections du commerce) et traits de scie
PANNEAU = dict(l=250, p=65, ep=2.6, nom="plan de travail chêne massif lamellé-collé abouté 250 × 65 × 2,6")
TASSEAU = dict(l=239, s=(4.4, 6.9), nom="tasseau sapin du Nord raboté 240 × 69 × 44 (longueur réelle 2,39)")
ROND = dict(l=100, d=1.0, nom="rond plein acier Ø 10 × 1 m")
KERF, KERF_METAL, DRESSAGE = 0.3, 0.15, 0.5   # scie circulaire, scie à métaux, recoupe d'équerre des bouts de panneau
RECHANGE_CHEVILLES = 4                           # chevilles de rechange au moins (une se perd)
L_MONTANT = MONTANTS["z1"] - MONTANTS["z0"]
BANDE = PANNEAU["l"] - DRESSAGE                  # longueur utile d'une bande refendue
N_VIS = MONTANTS["n"] * ETUDE_MONTANTS["vis"]

# charges : part de chaque tablette reprise par chaque montant (poutre continue sur appuis égaux, charge uniforme ;
# coefficients des réactions × pas, plus le débord aux deux bouts)
COEF = {1: (0.5, 0.5), 2: (0.375, 1.25, 0.375), 3: (0.4, 1.1, 1.1, 0.4), 4: (0.393, 1.143, 0.929, 1.143, 0.393)}
KG_M = CHARGE_LIVRES + ETAGERES["p"] / 100 * ETAGERES["ep"] / 100 * 700   # kg par mètre de tablette pleine, chêne compris
KG_MONTANT = L_MONTANT / 100 * MONTANTS["l"] / 100 * MONTANTS["p"] / 100 * 450

# achats (prix TTC, DATE) : statut « relevé » (prix lu sur la fiche en ligne) ou « estimé » ; magasins dans l'ordre
# Weldom, Leroy Merlin, Castorama ; stock non vérifié (à faire en magasin). La liste des articles, dont les quantités
# dépendent de la disposition, est dans achats() de l'ancien générateur.
MAGASINS = {
    "weldom": dict(nom="Weldom Marseille Saint-Barnabé", adresse="90 rue François Scaramelli, 13012 Marseille",
                   url="https://www.weldom.fr/m/weldom-marseille-saint-barnabe"),
    "leroy": dict(nom="Leroy Merlin", adresse="", url="https://www.leroymerlin.fr/"),
    "castorama": dict(nom="Castorama", adresse="", url="https://www.castorama.fr/"),
}
SURF_PEINT = MONTANTS["n"] * L_MONTANT * 2 * (MONTANTS["l"] + MONTANTS["p"]) / 1e4                       # m²

# matériaux : (pièce, retenu, pourquoi, alternatives)
MATERIAUX = [
    ("Montants",
     "Sapin du Nord raboté 44 × 69 (Weldom), peint en noir mat. Le modèle vu par le client est en pin massif : peint, "
     "un sapin raboté donne le même aspect ; la densité est proche (≈ 450 kg/m³).",
     "Choisir en magasin des tasseaux droits, sans gros nœud au droit des trous ni fente en bout : la laque cache le "
     "bois, pas les défauts de forme.",
     "Pin massif 45 × 70 chez un négociant (même résultat, plus cher) ; hêtre ou chêne (plus durs : les trous des "
     "chevilles s'ovalisent moins, mais pas en 45 × 70 au Weldom) ; 47 × 47 ou 44 × 95 à 22,90 € chez Leroy Merlin "
     "(section différente : il faudrait refendre). Pas de MDF ni d'aggloméré : les trous s'écrasent."),
    ("Tablettes",
     "Chêne massif lamellé-collé abouté, plan de travail 250 × 65 × 2,6 (Castorama, 99 €), refendu en deux bandes de "
     f"{ETAGERES['p']} : chaque bande garde un chant arrondi d'usine, qui fait le devant de la tablette.",
     "Le lamellé-collé ne se voile pas comme une planche massive d'une pièce, et 2,6 tient 55 de portée chargée de "
     "livres sans fléchir visiblement.",
     "Weldom chêne massif 300 × 65 × 3,8 à 235 € (deux fois le prix, et 3,8 change tout le perçage) ; tablettes "
     "Weldom chêne lamellé-collé 200 × 60 × 18 à 66,90 € (deux bandes de 29,8 seulement, 18 plus fin que le modèle, "
     "et trop courtes pour 244 et 189 dans la disposition actuelle) ; Castorama GoodHome Kava 300 × 62 × 2,6 à "
     "199,90 € (62 ne donne qu'une bande de 32) ; hévéa 250 × 65 × 2,6 à 129 € chez Leroy Merlin (pas du chêne)."),
    ("Chevilles",
     "Rond plein acier Ø 10 (Weldom, 1 m), coupé à la scie à métaux, bouts chanfreinés à la lime, peint en noir.",
     "Une cheville porte ≈ 79 kg en appui : l'acier travaille très en dessous de sa limite (voir les charges).",
     "Acier étiré poli Ø 10 (Brico Dépôt, 8,99 € le mètre : diamètre plus régulier, ajustement plus net dans le "
     "trou) ; inox Ø 10 (pas de peinture, plus cher) ; laiton (visible, autre style). Pas de tube creux : il s'écrase."),
    ("Peinture",
     "Laque glycéro noir mat Valénite (Weldom) : film dur, tient aux frottements des tablettes et des chevilles.",
     "Deux couches sur les montants, poncés au 180 entre les deux ; sur les chevilles, après l'apprêt antirouille.",
     "Acrylique mat « Crème de couleur » (même rayon : tire vers l'ardoise selon un avis) ; teinte noire et huile "
     "(le bois se voit sous le noir)."),
    ("Huile",
     "Huile pour plan de travail V33 Resist'Activ incolore mat (Weldom) : aspect bois brut, résiste aux taches.",
     "Trois couches sur toutes les faces et tous les chants, entailles comprises : une face nue reprend l'humidité et "
     "la tablette tuile.",
     "Huile dure d'une autre marque (même usage) ; vernis mat (plus résistant, aspect plus plastique) ; cire (fragile, "
     "à refaire)."),
]

# présentoir (tablette penchée vers la pièce) : mêmes trous que les tablettes à plat ; la cheville avant est prise
# dans une rainure faite à la défonceuse sous la tablette (largeur l). Ses dimensions dérivées (PR de l'ancien
# générateur : pente, profil, profondeur de la rainure) sont calculées par la page.
PRESENTOIR = dict(deg=15, l=ETAGERES["rainure"]["l"])

# tenue du mécanisme (Eurocode 5, EN 338) : vérification simplifiée, résistance caractéristique × kmod / γM, comparée
# à l'effort × 1,5 (charge d'exploitation). kmod = 0,7 (stockage, longue durée, intérieur sec), γM = 1,3 (bois
# massif) : de mémoire (repris tel quel de l'ancienne page).
TN = dict(d=10, fm=30, kmod=0.7, kmod_inst=1.1, gm=1.3, gq=1.5, rho=320, fc90=8.0, fy=235, f_contact=15,
          e=(MONTANTS["p"] + ETAGERES["x1"]) / 2, vis_h=(5, L_MONTANT / 2 + 0.5, L_MONTANT - 4))
TN["fh0"] = 0.082 * (1 - 0.01 * TN["d"]) * TN["rho"]                   # MPa, portance d'une broche, parallèle au fil
_bout = ETAGERES["cheville_ext"] * 10                                      # mm
_wc = math.pi * TN["d"] ** 3 / 32                                          # mm³
R_ACIER = 2 * TN["fy"] * _wc / (_bout / 2)                                 # N, deux bouts chargés en leur milieu
R_MONTANT = TN["fh0"] * TN["d"] * MONTANTS["l"] * 10                       # N (caractéristique)
_t_rain = (ETAGERES["ep"] - ETAGERES["rainure"]["prof"]) * 10              # mm de chêne au-dessus de la rainure
_b_rain = (ETAGERES["rainure"]["long"] - ETAGERES["entaille"][0]) * 10     # mm : la rainure sans l'entaille
_levier = (MONTANTS["p"] + ETAGERES["x1"]) / 2 - MONTANTS["x_av"]          # cm, charge → cheville avant
R_FLEX = TN["fm"] * _b_rain * _t_rain ** 2 / 6 / (_levier * 10)            # N par montant (caractéristique)
A_JOUE = 2 * TN["d"] * (_bout + TN["f_contact"])                           # mm², deux bouts, diffusion de 15 d'un côté
R_JOUE = TN["fc90"] * A_JOUE                                               # N (caractéristique)
ARR = (MONTANTS["x_av"] - MONTANTS["x_ar"])                                # bras de levier de la cheville arrière
# effort au bord d'une courte (2 montants) qui écrase les joues : charge caractéristique et charge « de calcul »
_LEVIER = (ETAGERES["x1"] - MONTANTS["x_av"]) / ARR + 1                    # cheville avant : P / 2 × (27 / 3 + 1)
P_RUINE = R_JOUE / _LEVIER * 2 / 9.81                                      # kg
P_CALCUL = R_JOUE * TN["kmod_inst"] / TN["gm"] / TN["gq"] / _LEVIER * 2 / 9.81

SOURCES_TENUE = [
    ("https://roymech.org/Related/Construction/Timber_connections.html", "RoyMech, assemblages bois selon l'Eurocode 5 (portance des broches, pinces et entraxes)"),
    ("https://roymech.org/Related/Construction/Timber", "RoyMech, classes de résistance EN 338 (chêne D30)"),
    ("https://www.lawson-his.co.uk/fischer-535980-duopower-big-pack-8-x-40mm-pack-of-120", "fischer DuoPower 8 × 40 : charges recommandées (béton, brique pleine, plaque de plâtre)"),
    ("https://www.bouwkampioen.be/fr/mwdownloads/download/link/id/3871", "fiche technique fischer DuoPower : carreau de plâtre, coefficient de sécurité 7"),
    ("https://forums.futura-sciences.com/attachments/physique/104861d1268375997-coefficient-de-frottement-beton-humide-polyurethane-coefficients-de-frottement.pdf", "tableau de coefficients de frottement (bois sur métal 0,2 à 0,6)"),
]

# ------------------------------------------------------------------ rendus 3D (3d/salon/rendu_meubles.py)
# Caméras du document, dans le repère du salon ; fichiers salon-meubles-3d/etageres-<id>.jpg. Disposition actuelle
# seulement (les autres se rendent sur demande).
CAMERAS = (
    Camera("iso", "Mur ouest en trois quarts", (15 + 520, 129 + 330, 165 + 260), (15, 129, 160), ortho=3.3),
    Camera("detail", "Détail d'une entaille", (62, 292, 131), (4, 236, 120.5), focale=50),   # montant M5, tablette T1
)
# (caméra, texte de la page) : section Rendus 3D de salon-etageres.html
RENDUS = [
    ("iso", "Le mur ouest en trois quarts depuis la pièce : les étagères au-dessus de l'enfilade."),
    ("detail", "Gros plan d'une entaille : le montant traverse la tablette, une cheville dessous devant, une dessus "
               "derrière."),
]

# ------------------------------------------------------------------ changements (tableau de salon-etageres.html)
# Textes tels que la page les affiche (valeurs calculées comprises, figées à leur version), du plus récent au plus
# ancien.
CHANGEMENTS = [
    ("V1.8", "30/10/2026",
     "Rainure à la défonceuse sous toutes les tablettes, comme au présentoir : 11 × 5 mm au droit de la cheville "
     "avant, sur 9 centrés sur chaque entaille ; la tablette ne peut plus avancer et la cheville avant ne peut plus "
     "glisser en long. Colonne avant des trous remontée de 5 mm (décalage 3,2 au lieu de 3,7) ; profil, vue de face, "
     "entaille, vue iso et plan de perçage redessinés ; Tenue : flexion de la tablette amincie (65 %, calcul "
     "prudent) ; présentoir sur les mêmes trous, rainure de 13,7 mm. Prix inchangés ; rendus 3D non refaits."),
    ("V1.7", "30/10/2026",
     "Présentoir : la butée vissée est remplacée par une rainure à la défonceuse sous la tablette (11 × 13,7 mm, axe "
     "à 4,9 du chant arrière), où la cheville avant est prise ; plus de feuillure sur le dessus. Pose et retrait à la "
     "main, devant levé à l'horizontale. Prix et dispositions inchangés."),
    ("V1.6", "30/10/2026",
     "Tablettes penchées le long du mur retirées (page, pièces, vue iso). La section devient Présentoir : ce qui "
     "l'empêche de glisser vers la pièce, chiffré (coincement entre les deux chevilles, frottement minimal 0 au milieu "
     "pour 0,2 à 0,6 acier sur bois), et une butée en chêne vissée sous la tablette, contre la cheville avant, qui la "
     "bloque même vide ou soulevée. Prix et dispositions inchangés."),
    ("V1.5", "30/10/2026",
     "Dispositions Niche et Inclinées retirées : restent Actuelle, Rangs, Décalée, Escalier. Tablettes inclinées "
     "redessinées : vue de face entre deux montants avec les livres, vue iso du bout bas coupé dans la feuillure, "
     "présentoir en profil avec ce qui le retient (la tablette pincée entre la cheville avant, dessous, et la cheville "
     "arrière, dessus). Section Tenue : recherche sur l'Eurocode 5, l'EN 338 et les fiches fischer ; tableau de ce qui "
     "peut céder (acier, montant, appui du chêne, le plus chargé à 57 %), effort accidentel au bord, glissement des "
     "chevilles, pinces des trous sous le minimum de la norme, fixation au mur selon la cloison ; correction de V1.4 "
     "(montant chargé dans le sens du fil). Prix inchangés."),
    ("V1.4", "30/10/2026",
     "Section Dispositions : cinq nouvelles dispositions à côté de l'actuelle (Rangs, Décalée, Escalier, Niche, "
     "Inclinées), avec des hauteurs de dessus variées, sur les mêmes montants percés de 122 à 222 ; les longues "
     "tablettes divisées pour n'avoir que deux longueurs (134 et 79), tirées des deux mêmes plans de chêne ; bouton "
     "Disposition dans la barre du haut, qui fait passer toute la page (élévation, vues de dessus, vue iso, "
     "composition avec la hauteur libre au-dessus de chaque tablette, débit, charges, achats). Section Tablettes "
     "inclinées : penchées le long du mur d'un pas de trous (5,2°, feuillure de ≈ 0,7, pièces dédiées, charges "
     "légères) et présentoir penché vers la pièce. Disposition actuelle et plan du salon inchangés ; rendus 3D de "
     "l'actuelle seulement."),
    ("V1.3", "29/10/2026",
     "Chevilles dessinées rondes (acier rond Ø 10) dans la vue iso et les rendus, au lieu de petites boîtes carrées."),
    ("V1.2", "29/10/2026",
     "Tablettes d'une seule pièce dans la vue iso et les rendus : plus de trait de joint entre la bande avant et les "
     "morceaux entre les entailles (artefact du découpage en boîtes) ; arêtes des tablettes arrondies (5 mm) dans les "
     "rendus. Géométrie et prix inchangés."),
    ("V1.1", "29/10/2026",
     "Vue iso du meuble et détail agrandi d'une entaille (montant, tablette entaillée, chevilles) ; section Rendus 3D "
     "(mur ouest en trois quarts, gros plan d'une entaille), images à produire. Géométrie et prix inchangés."),
    ("V1.0", "29/10/2026",
     "Première version de la page, d'après l'étude du salon V4.23 : élévation du mur, vues de dessus, profil et "
     "travée ; matériaux et alternatives ; liste des pièces, refente des plans de chêne, débit des tasseaux et des "
     "ronds, plan de perçage d'un montant, entaille ; charges et fixation ; achats chiffrés (393,28 €, dont 28,00 € "
     "estimés) ; outils et montage ; points à valider."),
]
