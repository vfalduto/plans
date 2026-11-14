# Salon, enfilade du mur ouest : le meuble (cotes extérieures, modules, emprise sur le plan du salon), ses choix de
# construction, ses matériaux, sa quincaillerie et ses prix, ses comparaisons (IKEA STOCKHOLM, METOD), VERSION et
# CHANGEMENTS de la page salon-enfilade.html.
#
# Ce fichier ne contient que des données, reprises de 3d/salon/modele.py (section ①) et de 3d/salon/enfilade.py. Il
# est le seul à décrire l'enfilade : le plan du salon (amenagement/document.py) et les étagères, centrées sur elle
# (etageres/document.py), l'importent. Les calculs (géométrie des caissons, débit, calepinage, chiffrage) et les
# dessins restent au générateur de la page.
#
# Cotes en cm, repère du salon : x vers l'est depuis le mur ouest, y vers le sud depuis le mur nord, z depuis le sol.
# Attention : L, P, EP sont ici ceux de l'enfilade (240, 60, 1,8), pas ceux du salon (piece.py).

import math

from commun.modele import Camera
from commun.rendu_cache import CacheRendu
from pieces.salon.meubles import cote
from pieces.salon.piece import PASSAGE, Bloc, Cyl


VERSION, DATE = "V1.6", "30/10/2026"
RELEVE = "29/10/2026"   # date de la recherche de prix (en ligne, sans visite en magasin)

# ------------------------------------------------------------------ le meuble dans le salon (modele.py, section ①)
# Position validée par le client : mur ouest, entre le coin nord et le cadre du passage (258 utiles).
# Meuble bas style enfilade, sur pieds, profond pour avoir du volume ; V4.25, choix du client : trois caissons de 80
# (240), centré sur le mur (8,8 libres de chaque côté), donc sur le même axe que les étagères ; V4.26, demande du
# client : 60 de profond au lieu de 45 (l'allée de 60 est gardée, le canapé et ce qui s'aligne sur lui glissent de 15).
_niche = PASSAGE["y0"] - PASSAGE["cadre"]
ENFILADE = dict(y0=round((_niche - 3 * 80) / 2, 1), y1=round((_niche + 3 * 80) / 2, 1), p=60, pieds=15, z1=80, facade=2, ep=1.8)
MODULES = [  # (façades, contenu), du nord au sud
    (["porte", "porte"], "jeux, albums, vinyles"),
    (["tiroir", "tiroir", "tiroir"], "linge de table, couverts"),
    (["porte", "porte"], "vaisselle, verres (×12)"),
]
_e = ENFILADE
_lm = (_e["y1"] - _e["y0"]) / len(MODULES)
ENFILADE["modules"] = [(_e["y0"] + i * _lm, _e["y0"] + (i + 1) * _lm) for i in range(len(MODULES))]

# emprise sur le plan et les coupes du salon : caisson, façades, pieds
_xf = _e["p"] - _e["facade"]                       # nu du caisson, côté pièce
BLOCS = [Bloc("caisson", "enfilade_caisson", 0, _xf, _e["y0"], _e["y1"], _e["pieds"], _e["z1"], etiq="①")]
for _i, ((_y0, _y1), (_facades, _contenu)) in enumerate(zip(ENFILADE["modules"], MODULES)):
    _n = len(_facades)
    if _facades[0] == "porte":   # portes côte à côte
        for _k in range(_n):
            _a, _b = _y0 + (_y1 - _y0) * _k / _n, _y0 + (_y1 - _y0) * (_k + 1) / _n
            BLOCS.append(Bloc("facade", f"enfilade_m{_i + 1}_porte{_k + 1}", _xf, _e["p"], _a + 0.2, _b - 0.2,
                              _e["pieds"] + 0.2, _e["z1"] - 0.2, contenu=_contenu if _k == 0 else ""))
    else:                        # tiroirs superposés
        _h = (_e["z1"] - _e["pieds"]) / _n
        for _k in range(_n):
            _a, _b = _e["z1"] - (_k + 1) * _h, _e["z1"] - _k * _h
            BLOCS.append(Bloc("facade", f"enfilade_m{_i + 1}_tiroir{_k + 1}", _xf, _e["p"], _y0 + 0.2, _y1 - 0.2,
                              _a + 0.2, _b - 0.2, contenu=_contenu if _k == 0 else ""))
for _y in (_e["y0"] + 6, _e["y1"] - 6):
    for _x in (6, _e["p"] - 8):
        BLOCS.append(Cyl("pied", f"enfilade_pied_{_x}_{_y}", _x, _y, 1.6, 0, _e["pieds"]))
VOLUME_ENFILADE = (_xf - 2 * _e["ep"]) * (_e["y1"] - _e["y0"] - (len(MODULES) + 1) * _e["ep"]) \
    * (_e["z1"] - _e["pieds"] - 2 * _e["ep"]) / 1000   # litres utiles

# ------------------------------------------------------------------ cotes du modèle (enfilade.py)
L = round(ENFILADE["y1"] - ENFILADE["y0"], 1)    # 240 le long du mur ouest : trois caissons de 80
NORD = ENFILADE["y0"]                    # jour entre le mur nord et le bout nord du meuble (centré sur le mur)
P, Z1, ZP, EP = ENFILADE["p"], ENFILADE["z1"], ENFILADE["pieds"], ENFILADE["ep"]
N = len(MODULES)

# ------------------------------------------------------------------ choix de construction (V1.3, à valider)
FAC = 1.8                                # façades en chêne lamellé-collé de 18
TAMPON = round(ENFILADE["facade"] - FAC, 2)   # 0,2 : tampons silicone entre caisson et façades
DOS = 0.32                               # dos en panneau de fibres dures 3,2, vissé en applique
PC = round(P - ENFILADE["facade"] - DOS, 2)   # profondeur des côtés : 60 − 2 − 0,32
JEU = 0.3                                # entre deux façades
BORD = 0.15                              # au bord d'un caisson (0,3 entre deux caissons)
TRAV = 10                                # traverses hautes (avant, arrière) à la place d'un dessus de caisson
TRAIT = 0.3                              # trait de scie
COULISSE = 50                            # coulisses à billes de 500, sortie totale
EP_COUL = 1.27                           # épaisseur d'une coulisse à billes
H_BOITE = 14                             # hauteur des boîtes de tiroir
CALE_BOITE = 2.5                         # dessous de la boîte au-dessus du bas de sa façade
PROF_ETAGERE = 55                        # étagères de 55 (refendues dans des tablettes de 60), 2,7 en retrait
CHARNIERE = dict(axe=2.2, bout=10)       # coupelle Ø 35 : axe à 2,2 du chant, à 10 du haut et du bas de la porte
PIEDS_X = (5, round(P - ENFILADE["facade"] - 5, 1))   # rangées de pieds : à 5 du mur et à 5 du nu du caisson
DESSUS = (1.8, 3)                        # (épaisseur, nombre de pièces) : une tablette de chêne 18 par caisson
# vides sous chaque étagère intérieure, du fond vers le haut, par module : vinyles debout sur le fond (31,5 + 1,5)
# au nord ; assiettes et plats, puis verres, au sud ; aucun dans le module des tiroirs (ETAGERES dans enfilade.py)
ETAGERES_CAISSONS = [[33], [], [22, 20]]
VINYLE = 31.5

# ------------------------------------------------------------------ magasins, panneaux, quincaillerie, prix
MAGASINS = {
    "weldom": dict(nom="Weldom Marseille Saint-Barnabé", court="Weldom", url="https://www.weldom.fr/"),
    "lm": dict(nom="Leroy Merlin", court="Leroy Merlin", url="https://www.leroymerlin.fr/"),
    "casto": dict(nom="Castorama", court="Castorama", url="https://www.castorama.fr/"),
}
ORDRE_MAG = list(MAGASINS)

LM_PT = "https://www.leroymerlin.fr/produits/plan-de-travail-standard-chene-lamelle-l-300-x-p-65-cm-ep-36-mm-80156840.html"
LM_HDF = "https://www.leroymerlin.fr/produits/panneau-fibres-dures-ep-3-2-mm-decoupe-sur-mesure-70826840.html"
LM_PIED = "https://www.leroymerlin.fr/produits/pied-de-meuble-carre-hettich-noir-2-5x2-5-cm-x-15-cm-69165075.html"
LM_CP = "https://www.leroymerlin.fr/produits/panneau-contreplaque-peuplier-ep-18-mm-x-l-250-x-l-122-cm-69124265.html"
LM_MC = "https://www.leroymerlin.fr/produits/tablette-melamine-chene-melamine-unilin-l-250-x-l-60-cm-x-ep-18-mm-80062934.html"
LM_PT25 = "https://www.leroymerlin.fr/produits/plan-de-travail-chene-massif-pleines-lames-3000-x-800-x-25-mm-fsc-mixte-84505452.html"
LM_T20 = "https://www.leroymerlin.fr/produits/tablette-chene-pleine-lame-l-250-cm-x-l-60-cm-x-ep-20-mm-70626031.html"
CASTO_PT = "https://www.castorama.fr/vb/plan-de-travail-chene-massif"
CASTO_PT26 = "https://www.castorama.fr/plan-de-travail-en-chene-massif-l-250-x-l-65-x-ep-2-6-cm/3428350070417_CAFR.prd"
REF_COUL = "https://www.domomat.com/43451-paire-de-coulisses-pour-tiroirs-a-billes-45-x-450-mm-fermeture-amortie-zingue-emuca-4301805.html"
REF_HUILE = "https://www.bricodepot.fr/p/3239913831006/huile-meubles-et-boiseries-biosourcee-nature-protect-incolore-mat-0-5l"

# Panneaux : L le long du fil (ou de la longueur de la tablette), l en travers. « bandes » : 2 au plus pour le
# mélaminé, pour que chaque pièce garde un chant d'usine devant (bande contre l'un des deux bords de la tablette).
# statut : « relevé » (prix lu en ligne ou déjà connu), « estimé » (ordre de grandeur, à relever en rayon).
FORMATS = {
    "C18": dict(nom="Tablette chêne lamellé-collé 200 × 60 × 1,8", court="chêne 18", L=200, l=60, ep=1.8, prix=66.90,
                ref="82025610", mag="weldom", statut="relevé", url=None, bois=True),
    "M50": dict(nom="Tablette mélaminée blanche 250 × 50 × 1,8", court="mélaminé 50", L=250, l=50, ep=1.8, prix=13.59,
                ref="—", mag="weldom", statut="relevé", url=None, bandes=2),
    "M40": dict(nom="Tablette mélaminée blanche 250 × 40 × 1,8", court="mélaminé 40", L=250, l=40, ep=1.8, prix=12.50,
                ref="—", mag="weldom", statut="relevé", url=None, bandes=2),
    "M30": dict(nom="Tablette mélaminée blanche 250 × 30 × 1,8", court="mélaminé 30", L=250, l=30, ep=1.8, prix=11.50,
                ref="—", mag="weldom", statut="relevé", url=None, bandes=2),
    "M60": dict(nom="Tablette mélaminée blanche 250 × 60 × 1,8", court="mélaminé 60", L=250, l=60, ep=1.8, prix=16.50,
                ref="—", mag="weldom", statut="relevé", url=None, bandes=2),
    "PT36": dict(nom="Plan de travail chêne lamellé 300 × 65 × 3,6", court="plan chêne 36", L=300, l=65, ep=3.6,
                 prix=329.00, ref="80156840", mag="lm", statut="relevé", url=LM_PT, bois=True),
    "HDF": dict(nom="Panneau de fibres dures 3,2, découpe sur mesure", court="fibres dures 3,2", ep=0.32, prix=12.90,
                ref="70826840", mag="lm", statut="relevé", url=LM_HDF, m2=True),
    "CP18": dict(nom="Contreplaqué peuplier 250 × 122 × 1,8", court="contreplaqué 18", L=250, l=122, ep=1.8,
                 prix=129.00, ref="69124265", mag="lm", statut="relevé", url=LM_CP, bois=True),
    "MC60": dict(nom="Tablette mélaminée décor chêne 250 × 60 × 1,8", court="mélaminé chêne", L=250, l=60, ep=1.8,
                 prix=49.90, ref="80062934", mag="lm", statut="relevé", url=LM_MC, bandes=2),
}
MELAMINE = ["M30", "M40", "M50", "M60"]

HUILE = dict(couches=2, rendement=15)   # m² par litre et par couche (ordre de grandeur, à lire sur le bidon)
# Quincaillerie et consommables. q : quantité tirée des comptes du meuble (c, calculés par la page), en données pour
# que l'empreinte des rendus puisse les lire : quantite(q, c) = par × c[compte], arrondi au sachet supérieur s'il y a
# un sachet ; ou fixe. (L'ancien générateur écrivait des lambdas, mêmes valeurs.)
QUINC = [
    dict(poste="Charnière invisible Ø 35, 110°, en applique", ref="9154863", mag="weldom", prix=5.35,
         statut="relevé", url=None, q=dict(compte="portes", par=2), note="2 par porte ; prix supposé à l'unité"),
    dict(poste="Poussoir magnétique (ouverture par pression)", ref="à choisir", mag="weldom", prix=3.90,
         statut="estimé", url=None, q=dict(compte="portes"), note="1 par porte, en haut côté ouverture"),
    dict(poste="Coulisses à billes 500, sortie totale, ouverture par pression (paire)", ref="à choisir", mag="lm",
         prix=19.90, statut="estimé", url=REF_COUL, q=dict(compte="tiroirs"),
         note="25 kg ; repère : paire Emuca 450 amortie à 13,33 € (500 à relever)"),
    dict(poste="Pied de meuble carré noir 2,5 × 2,5 × 15, patin fileté M10", ref="69165075", mag="lm", prix=3.59,
         statut="relevé", url=LM_PIED, q=dict(compte="pieds"), note="50 kg chacun ; platine 6 × 6"),
    dict(poste="Tampons silicone 2 mm (sachet de 20)", ref="à choisir", mag="weldom", prix=2.90, statut="estimé",
         url=None, q=dict(compte="facades", par=4, sachet=20), note="4 par façade"),
    dict(poste="Taquets d'étagère Ø 5 (sachet de 16)", ref="à choisir", mag="weldom", prix=2.90, statut="estimé",
         url=None, q=dict(compte="etageres", par=4, sachet=16), note="4 par étagère"),
    dict(poste="Vis de liaison de meuble Ø 5 pour 2 × 18 (sachet de 4)", ref="à choisir", mag="weldom", prix=3.50,
         statut="estimé", url=None, q=dict(compte="jonctions"), note="4 par jonction de caissons"),
    dict(poste="Équerres de fixation à trou oblong (sachet de 4)", ref="à choisir", mag="weldom", prix=3.90,
         statut="estimé", url=None, q=dict(compte="caissons"), note="dessus : 4 par caisson, le bois massif travaille"),
    dict(poste="Équerre acier 40 × 40 (anti-basculement)", ref="à choisir", mag="weldom", prix=1.20, statut="estimé",
         url=None, q=dict(compte="caissons"), note="1 par caisson, sous la traverse arrière"),
    dict(poste="Chevilles et vis pour la cloison (selon sa nature)", ref="à choisir", mag="weldom", prix=5.90,
         statut="estimé", url=None, q=dict(fixe=1), note="Molly si plaque de plâtre"),
    dict(poste="Vis bois 4 × 50 (boîte de 100)", ref="à choisir", mag="weldom", prix=7.90, statut="estimé",
         url=None, q=dict(fixe=1), note="caissons et boîtes de tiroir, avec avant-trous"),
    dict(poste="Vis 3,5 × 16 (boîte de 200)", ref="à choisir", mag="weldom", prix=5.90, statut="estimé", url=None,
         q=dict(fixe=1), note="dos, fonds, pieds, coulisses, charnières"),
    dict(poste="Vis 3,5 × 30 (boîte de 100)", ref="à choisir", mag="weldom", prix=4.90, statut="estimé", url=None,
         q=dict(fixe=1), note="façades de tiroir, dessus"),
    dict(poste="Tourillons Ø 8 × 35 et colle à bois", ref="à choisir", mag="weldom", prix=8.80, statut="estimé",
         url=None, q=dict(fixe=1), note="caissons collés, joues sans vis apparente, joints des dessus"),
    dict(poste="Huile dure incolore, bidon de 1 L", ref="à choisir", mag="weldom", prix=35.00, statut="estimé",
         url=REF_HUILE, q=dict(compte="chene_m2", par=2 * HUILE["couches"], sachet=HUILE["rendement"]),
         note="deux couches, toutes faces ; repère : 0,5 L de Blanchon à 17,50 € (Brico Dépôt)"),
    dict(poste="Abrasifs 120, 180, 240", ref="à choisir", mag="weldom", prix=7.90, statut="estimé", url=None,
         q=dict(fixe=1), note="ponçage avant huile"),
]
OUTILLAGE = [   # à acheter seulement si l'atelier ne les a pas (hors total du meuble)
    ("Mèche Forstner Ø 35 avec butée", 12.90),
    ("Gabarit de perçage pour taquets Ø 5 (ou tasseau percé maison)", 14.90),
    ("Foret à bois Ø 5 avec bague de butée", 4.90),
]

# Variantes de matériau : caisson ("mel" = mélaminé blanc, format choisi par largeur), façades, dessus (ép., pièces).
# Ce sont des options de construction étudiées dans la page, pas des variantes du document.
VARIANTES = [
    dict(cle="A", nom="Caisson mélaminé blanc, façades chêne massif, dessus chêne d'une pièce", caisson="mel",
         facade="C18", dessus=(3.6, 1)),
    dict(cle="B", nom="Comme A, dessus en trois pièces de chêne 18 (une par caisson)", caisson="mel",
         facade="C18", dessus=(1.8, N)),
    dict(cle="C", nom="Tout en chêne massif 18 (caisson, étagères et tiroirs aussi), dessus en trois pièces de 18",
         caisson="C18", facade="C18", dessus=(1.8, N), retenu=True),
    dict(cle="D", nom="Caisson contreplaqué peuplier 18, façades chêne massif, dessus d'une pièce", caisson="CP18",
         facade="C18", dessus=(3.6, 1)),
    dict(cle="E", nom="Tout mélaminé : caisson blanc, façades et dessus (trois pièces) en décor chêne",
         caisson="mel", facade="MC60", dessus=(1.8, N), chant=True),
    dict(cle="F", nom="Comme C, dessus d'une pièce dans le plan de travail chêne de 36", caisson="C18",
         facade="C18", dessus=(3.6, 1)),
]
CHANT = dict(rouleau=5, prix=6.90, statut="estimé")   # chant thermocollant décor chêne, rouleau de 5 m
RETENUE = next(v for v in VARIANTES if v.get("retenu"))
PREFIXE = {"caisson": "A", "facade": "B", "tiroir": "C", "fond": "D", "dessus": "E"}
GROUPES = {"caisson": "Caissons", "facade": "Façades et joue (chêne visible)", "tiroir": "Boîtes de tiroir",
           "fond": "Dos et fonds de tiroir", "dessus": "Dessus"}

# ------------------------------------------------------------------ comparaisons
# Buffet IKEA STOCKHOLM 2025, placage chêne, réf. 105.866.04 (fiche IKEA Belgique, relevée le 29/10/2026). IKEA ne
# publie que les cotes hors tout et l'intérieur des tiroirs : le volume intérieur est estimé (interieur).
STOCKHOLM = dict(nom="IKEA STOCKHOLM 2025", l=160.8, p=42.0, h=83.2, prix=599.00, tiroir=(68.5, 33.2),
                 interieur=(160.8 - 3 * 1.8, 42.0 - 4, 83.2 - 12 - 2 * 1.8),   # 2 côtés + 1 séparation, dos, socle
                 url="https://www.ikea.com/be/nl/p/stockholm-2025-buffetkast-eikenfineer-10586604",
                 url_fr="https://www.ikea.com/ca/fr/p/stockholm-2025-buffet-chene-plaque-10586604",
                 materiau="aggloméré plaqué chêne, vernis", contenu="2 tiroirs et 2 tablettes, ouverture par pression",
                 charges="15 kg par tablette, 10 kg par tiroir")

# Trois caissons IKEA METOD de 80 × 60 × 80 (prix relevés sur ikea.com/fr le 30/10/2026). Le caisson n'existe qu'en
# blanc et en noir-gris, et ne fait que 80 de haut (pieds METOD de 7,5 à 9,5) : le meuble est plus haut que l'enfilade.
# Posé au sol sans rail de suspension, il fait 59 de profond (fiche IKEA), plus l'épaisseur des façades.
# Deux compositions : tout IKEA (référence) et mixte, où chaque poste est pris là où il est meilleur pour son prix :
# caissons, tiroirs et quincaillerie METOD chez IKEA, plan en chêne massif chez Leroy Merlin, façades et joues dans
# les tablettes de chêne de Weldom (les mêmes que l'enfilade).
IKEA_FR = "https://www.ikea.com/fr/fr/p/"
METOD_RELEVE = "30/10/2026"
LM_PT26 = "https://www.leroymerlin.fr/produits/plan-de-travail-brut-chene-lamelle-l-250-xl-65cm-ep-26-mm-82582160.html"
METOD_CAISSON = dict(prof=59, h=80, pieds=8)    # profondeur sans rail de suspension, hauteur, pieds METOD


def quantite(q, c):
    """Quantité d'un poste de QUINC pour les comptes c du meuble (portes, tiroirs, pieds, chene_m2…)."""
    if "fixe" in q:
        return q["fixe"]
    n = q.get("par", 1) * c[q["compte"]]
    return math.ceil(n / q["sachet"]) if "sachet" in q else n


def ikea(nom, ref, q, pu, url, note, st="relevé"):
    """Poste d'achat IKEA (url : fin de l'adresse de la fiche, après IKEA_FR)."""
    return dict(nom=nom, ref=ref, q=q, pu=pu, st=st, url=IKEA_FR + url, note=note, ou="IKEA")


def huile_l(m2):
    """Litres d'huile pour m2 de chêne (une face), huilé des deux côtés comme l'enfilade."""
    return math.ceil(m2 * 2 * HUILE["couches"] / HUILE["rendement"])


KNIV = [ikea("KNIVSHULT tiroir moyen 80 × 60", "906.006.77", 2, 55, "knivshult-tiroir-moyen-gris-fonce-90600677/",
             "M2, sous les faces de 20"),
        ikea("KNIVSHULT tiroir haut 80 × 60", "706.006.64", 1, 70, "knivshult-tiroir-haut-gris-fonce-70600664/",
             "M2, sous la face de 40")]
SOCLE = [ikea("METOD pied pour élément 8 cm (2 pièces)", "705.560.67", 6, 5, "metod-pied-pour-element-70556067/",
              "4 par caisson, réglables de 7,5 à 9,5"),
         ikea("FÖRBÄTTRA plinthe mat anthracite 220 × 8", "705.267.87", 2, 21,
              "foerbaettra-plinthe-mat-anthracite-70526787/", "les pieds METOD, en plastique, sont faits pour être cachés")]
POUSSOIRS = [ikea("UTRUSTA poussoirs (2 pièces)", "802.302.24", 2, 7, "utrusta-poussoirs-80230224/", "1 par porte"),
             ikea("KNIVSHULT poussoirs pour tiroir 45-60 cm", "606.050.11", 3, 15,
                  "knivshult-poussoirs-pour-tiroir-45-60-cm-60605011/", "prix relevé, un jeu par tiroir supposé", "estimé")]
ANTI = dict(nom="Équerres anti-basculement et chevilles", ref="à choisir", q=1, pu=9.50, st="estimé", url=None,
            note="3 équerres", ou="Weldom")

# Tout IKEA : noir-gris, façades NICKEBO anthracite mat (le plus proche du noir en façade lisse), plan VRENA.
METOD = dict(nom="3 × IKEA METOD 80, tout IKEA", dessus=2.8, postes=[
    ikea("Élément bas tablette / 2 portes, noir-gris / NICKEBO anthracite mat, 80 × 60", "695.896.48", 2, 169,
         "metod-element-bas-tablette-2portes-noir-gris-nickebo-anthracite-mat-s69589648/",
         "M1 et M3 : caisson, 2 portes 40 × 80, 4 charnières amorties, 2 tablettes UTRUSTA 80 × 60"),
    ikea("METOD rangement noir-gris 80 × 60 × 80", "205.917.04", 1, 48, "metod-rangement-noir-gris-20591704/",
         "M2 : pas de combinaison 3 tiroirs 80 × 60 noir-gris / NICKEBO en ligne, on l'assemble"),
    *KNIV,
    ikea("NICKEBO face de tiroir mat anthracite 80 × 20", "605.377.34", 2, 33,
         "nickebo-face-de-tiroir-mat-anthracite-60537734/", ""),
    ikea("NICKEBO face de tiroir mat anthracite 80 × 40", "305.377.35", 1, 42,
         "nickebo-face-de-tiroir-mat-anthracite-30537735/", ""),
    *SOCLE, *POUSSOIRS,
    ikea("VRENA plan de travail chêne plaqué 246 × 63,5 × 2,8", "704.371.59", 1, 209,
         "vrena-plan-de-travail-chene-plaque-70437159/", "aggloméré plaqué chêne, recoupé à 240"),
    ANTI])

# Mixte : façades de 1,8 et joues de chêne aux deux bouts. Pièces de chêne (L × l, une face) : 4 portes, 3 faces de
# tiroir, 2 joues du sol au dessous du plan, et le plan.
JEU_METOD = 0.3                                             # jeu entre façades, comme IKEA (40 × 80 → 39,7 × 79,7)
PIECES_METOD = ([("porte", 80 - JEU_METOD, 40 - JEU_METOD)] * 4 + [("face de tiroir", 80 - JEU_METOD, 20 - JEU_METOD)] * 2
                + [("face de tiroir", 80 - JEU_METOD, 40 - JEU_METOD)] + [("joue", METOD_CAISSON["pieds"] + METOD_CAISSON["h"], 60)] * 2)
METOD_MIXTE = dict(nom="3 × METOD 80, mixte", facade=EP, dessus=2.6, joue=EP)
METOD_MIXTE.update(l=240 + 2 * EP, p=round(METOD_CAISSON["prof"] + EP, 1),
                   h=round(METOD_CAISSON["pieds"] + METOD_CAISSON["h"] + 2.6, 1))
_m2 = sum(a * b for _, a, b in PIECES_METOD) / 1e4 + METOD_MIXTE["l"] * METOD_MIXTE["p"] / 1e4
METOD_MIXTE["postes"] = [
    ikea("METOD rangement noir-gris 80 × 60 × 80", "205.917.04", 3, 48, "metod-rangement-noir-gris-20591704/",
         "caisson nu ; en blanc 38 € (10205633), mais ses chants se verraient dans les jeux entre façades"),
    ikea("UTRUSTA tablette noir-gris 80 × 60", "705.917.87", 4, 17, "utrusta-tablette-noir-gris-70591787/",
         "2 par caisson à portes, comme dans les combinaisons"),
    ikea("UTRUSTA charnières 95° (2 pièces)", "202.046.47", 4, 8, "utrusta-charnieres-20204647/",
         "2 par porte, sans amortisseur : rien ne freine la poussée du poussoir"),
    *KNIV, *SOCLE, *POUSSOIRS,
    dict(nom=FORMATS["C18"]["nom"], ref=FORMATS["C18"]["ref"], q=4, pu=FORMATS["C18"]["prix"], st="relevé", url=None,
         ou="Weldom", note="2 pour les portes et les faces de 20, 1 pour la face de 40 et une joue, 1 pour l'autre joue"),
    dict(nom="Plan de travail brut chêne lamellé 250 × 65 × 2,6", ref="82582160", q=1, pu=109, st="relevé",
         url=LM_PT26, ou="Leroy Merlin",
         note=f"chêne massif, d'une pièce, recoupé à {cote(240 + 2 * EP)} × {cote(METOD_CAISSON['prof'] + EP)} (découpe sur mesure proposée)"),
    dict(nom="Équerres de fixation à trou oblong (sachet de 4)", ref="à choisir", q=3, pu=3.90, st="estimé", url=None,
         ou="Weldom", note="plan vissé par en dessous dans les côtés des caissons ; le massif doit pouvoir glisser"),
    dict(nom="Huile dure incolore, bidon de 1 L", ref="à choisir", q=huile_l(_m2), pu=35.00, st="estimé", url=REF_HUILE,
         ou="Weldom", note=f"{cote(_m2, 1)} m² de chêne, deux couches, toutes faces"),
    dict(nom="Vis 3,5 × 30 (boîte de 100) et abrasifs", ref="à choisir", q=1, pu=12.80, st="estimé", url=None,
         ou="Weldom", note="joues vissées depuis l'intérieur des caissons, ponçage avant huile"),
    ANTI]
for _m in (METOD, METOD_MIXTE):
    _m["total"] = round(sum(x["q"] * x["pu"] for x in _m["postes"]), 2)
VRENA = next(x["pu"] for x in METOD["postes"] if x["nom"].startswith("VRENA"))
# Tout IKEA sauf le plan : le plan Leroy Merlin à la place du VRENA, avec son huile et ses abrasifs.
METOD_PLAN_LM = round(METOD["total"] - VRENA + 109 + 35 * huile_l(METOD_MIXTE["l"] * METOD_MIXTE["p"] / 1e4) + 7.90, 2)
NOIRS = [  # façades noires ou presque pour METOD, porte 40 × 80 (ikea.com/fr, 30/10/2026)
    ("NICKEBO mat anthracite", 42, "lisse, film plastique sur aggloméré", "nickebo-porte-mat-anthracite-10537717/"),
    ("UPPLÖV mat anthracite", 60, "lisse", "upploev-porte-mat-anthracite-80526758/"),
    ("LERHYTTAN teinté noir", 64, "à cadre (style rustique)", "lerhyttan-porte-teinte-noir-00356057/"),
    ("BODBYN noir", 76, "à cadre (style classique)", "bodbyn-porte-noir-00568587/"),
]

# ------------------------------------------------------------------ rendus 3D (pieces/salon/rendu_meubles.py)
# Caméras du document, dans le repère du salon ; fichiers rendus/<id>.jpg. ouvert : la porte nord
# de M1, la porte sud de M3 et le tiroir du haut de M2 ouverts (pieces_3d(ouvert=True) de l'ancien générateur).
# coupes : objets Blender cachés à la caméra ; l'ancien rendu des meubles cachait le plafond à toutes les vues
SANS_PLAFOND = r"^plafond__"
CAMERAS = (
    Camera("iso", "Enfilade fermée", (22 + 520, 129 + 330, 60 + 260), (22, 129, 75), ortho=3.0,
           reglages=dict(coupes=SANS_PLAFOND)),
    Camera("ouverte", "Enfilade ouverte", (22 + 520, 129 + 330, 60 + 260), (22, 129, 75), ortho=3.0,
           reglages=dict(ouvert=True, coupes=SANS_PLAFOND)),
)
# Empreinte des rendus (commun/rendu_cache.py) : la pièce, les deux meubles de la scène (les étagères sont au-dessus),
# puis le script de rendu et ses volumes. Document sans variante : rendus/<caméra>.jpg.
CACHE_RENDU = CacheRendu(variantes={"": ("pieces.salon.piece", "pieces.salon.etageres.document",
                                         "pieces.salon.enfilade.document")},
                         code=("pieces/salon/rendu_meubles.py", "pieces/salon/amenagement/rendu.py", "pieces/salon/etageres/volumes.py",
                               "pieces/salon/enfilade/volumes.py", "pieces/salon/meubles.py", "3d/rendu.py"),
                         cameras="pieces.salon.enfilade.document",
                         script="pieces/salon/rendu_meubles.py", sortie=("SALON_SORTIE", "3d/sortie"),
                         apercu="SALON_APERCU", png="salon-meuble-enfilade-{camera}.png", argument="enfilade-{camera}")
# (caméra, texte de la page) : section Rendus 3D de salon-enfilade.html
RENDUS = [
    ("iso", "L'enfilade fermée en trois quarts depuis la pièce, sous les étagères du mur ouest."),
    ("ouverte", "Portes et tiroir ouverts : la porte nord de M1, la porte sud de M3, le tiroir du haut de M2 sorti."),
]

# ------------------------------------------------------------------ changements (tableau de salon-enfilade.html)
# Textes tels que la page les affiche (valeurs calculées comprises, figées à leur version). Du plus récent au plus
# ancien, comme les autres documents (la page les listait du plus ancien au plus récent).
CHANGEMENTS = [
    ("V1.6", "30/10/2026",
     "Comparaison METOD en composition mixte, chaque poste pris là où il vaut le mieux : caissons, tiroirs, charnières "
     "95° sans amortisseur, poussoirs et pieds chez IKEA ; plan en chêne massif lamellé 250 × 65 × 2,6 de Leroy Merlin "
     "(109,00 €, au lieu du VRENA plaqué à 209,00 €) ; façades et joues en chêne de 18 dans les tablettes Weldom. "
     "Profondeur sans rail de suspension (caisson de 59) : 60,8. Totaux : mixte 1 035,60 €, tout IKEA 1 023,50 €, IKEA "
     "avec le plan Leroy Merlin 966,40 €. Matériaux : le plan de 250 × 65 × 2,6 n'est plus trop court pour les 240 "
     "de l'enfilade."),
    ("V1.5", "30/10/2026",
     "Profondeur de 60 au lieu de 45 (salon V4.26) : côtés de 57,68, dessus de 60 dans toute la largeur des "
     "tablettes, étagères de 55, coulisses de 500 ; total de 1 027,95 €. Comparaisons revues : STOCKHOLM recalculé ; "
     "METOD en caissons de 80 × 60 (le troisième, à tiroirs, assemblé pièce à pièce), dessus VRENA de 2,8 car le "
     "chêne de 60 ne couvre pas ses 61,6, 1 023,50 €."),
    ("V1.4", "30/10/2026",
     "Comparaison avec trois caissons IKEA METOD 80 × 37 en noir-gris, façades NICKEBO anthracite mat, même dessus en "
     "chêne : dimensions, volume, achats (946,30 €, prix relevés sur ikea.com/fr), façades noires possibles "
     "(NICKEBO, UPPLÖV, LERHYTTAN, BODBYN)."),
    ("V1.3", "29/10/2026",
     "Trois caissons de 80 (240 au lieu de 257,6), centrés sur le mur ouest avec 8,8 libres à chaque bout (salon "
     "V4.26) ; plus de fileur, six portes identiques, joue nord en M1 comme au sud ; comparaison avec le buffet IKEA "
     "STOCKHOLM 2025."),
    ("V1.2", "29/10/2026",
     "Variante C retenue, tout en chêne massif de 18 (caissons, étagères et boîtes de tiroir) ; le dessus de 3,6 "
     "(trop épais) remplacé par trois dessus de 1,8, un par caisson, joints au droit des jonctions ; l'ancienne C "
     "(dessus de 3,6) devient la variante F ; huile chiffrée selon la surface de chêne ; vues et vue iso avec caissons "
     "en chêne et dessus en trois pièces. Rendus 3D non refaits."),
    ("V1.1", "29/10/2026",
     "Vue iso fermée et ouverte (une porte de M1 et une de M3 à 90°, tiroir du haut de M2 sorti), tirée des mêmes "
     "cotes que le débit ; section Rendus 3D (rendus Blender à produire)."),
    ("V1.0", "29/10/2026",
     "Première version : construction en trois caissons (mélaminé blanc, chêne massif visible, dessus d'une pièce de "
     "3,6), élévation, coupes, vue de dessus, vue éclatée, débit repéré et plan de découpe, achats avec prix relevés "
     "et estimés, cinq variantes de matériau, montage, points à valider."),
]


# ------------------------------------------------------------------ le document du site
# Construit à la première lecture : vues importe amenagement/document.py, qui importe ce module (import circulaire).
def _document():
    from commun.modele import Changement, Document, Variante
    from pieces.salon.enfilade import dessins, vues
    variante = Variante("", "Enfilade", VERSION, tuple(Changement(*c) for c in CHANGEMENTS))
    return Document("salon", "enfilade", "Enfilade", "construction", (variante,), vues.vues, css=dessins.CSS)


def __getattr__(nom):
    if nom == "DOCUMENT":
        globals()["DOCUMENT"] = _document()
        return globals()["DOCUMENT"]
    raise AttributeError(f"module {__name__!r} has no attribute {nom!r}")
