# Entrée, variante principale : l'aménagement (meubles, finitions, changements). La pièce est dans ../piece.py.
#
# Ce fichier ne contient que des données : il est lu par les générateurs de l'entrée. Toute modification se fait ici,
# jamais dans le HTML.
#
# Cotes en cm : x vers l'est depuis le mur ouest du couloir, y vers le sud depuis son mur nord, z depuis le sol fini.

from commun.modele import Changement, Document, Option, Valeur, Variante
from commun.rendu_cache import CacheRendu
import math

from pieces.entree.piece import Bloc, EP, ENVELOPPE, H, H_PORTE, MURS, PORTES, PRISE_FIBRE, SOL, SURFACE  # noqa: F401

VERSION = "V4.13"

# Empreinte des rendus (just rendu entree/amenagement) : la pièce puis le module de la variante, le code de rendu de l'entrée puis
# celui de 3d/. Noms et ordre entrent dans l'empreinte : les changer refait tous les rendus.
CACHE_RENDU = CacheRendu(variantes={"principale": ("pieces.entree.piece", "document"),
                                    "victor": ("pieces.entree.piece", "victor")},
                         code=("pieces/entree/amenagement/rendu.py", "3d/rendu.py"),
                         script="pieces/entree/amenagement/rendu.py", sortie=("ENTREE_SORTIE", "3d/sortie"),
                         apercu="ENTREE_APERCU", variante_env="ENTREE_VARIANTE", png="entree-{variante}-{camera}.png",
                         masque=True)   # un masque par surface recolorable : -masque.png (India), -masque-pax.png…

# silhouette de chaque caméra
HUMAINS = {"iso_so": "couloir", "iso_no": "couloir", "iso_se": "entree"}

# versions figées : (version, chemin sous site/)
FIGEES_ANCIENNES = (("V3.3", "archives/entree-amenagement-v3.3.html"), ("V2", "archives/entree-amenagement-v2.html"),
                    ("V1", "archives/entree-amenagement-v1.html"))

# Tableau électrique encastré dans le trumeau nord, entre la cuisine et le WC : position et taille à relever
# (dessiné au milieu du banc, 60 × 80, bas à 95).
TABLEAU = dict(x0=110, x1=170, z0=95, z1=175)

# ------------------------------------------------------------------ ① banc sous le tableau électrique
# Posé, pas fixé dans la zone du tableau ; dessous ouvert ; on s'y assoit pour se chausser, face au meuble à chaussures.
BANC = dict(x0=92, x1=187, y0=0, y1=38, z1=45, ep=3)

# ------------------------------------------------------------------ ② meuble à chaussures, branche d'entrée
# Contre la cloison de la salle de bain (x 110), 25 de profondeur pour garder 85 de passage.
# V4.9 : le module côté porte d'entrée est retiré ; il reste un module de 83 (y 208 → 291), trois abattants
# superposés (≈ 6 paires par abattant), monté à 120 (plateau vide-poche à 123). Il est arrondi aux deux bouts : au
# nord l'angle à étagères ouvertes jusqu'au nu de la penderie (y 170), au sud un quart de cercle de rayon 25, ouvert
# lui aussi (y 291 → 316). La prise fibre (PRISE_FIBRE, à 26 du sol) est derrière le bas du module, côté nord : pas de
# dos dans le compartiment du bas, un passe-câble dans la joue nord vers l'étagère basse de l'angle (box à l'air libre).
# V4.10 : l'arrondi sud est retiré (le meuble s'arrête net au bout du module, y 291 : la porte d'entrée s'ouvre au-delà
# de 90°, voir OUVERTURE) ; plinthe de 8 en retrait de 4 sous tout le meuble, comme le banc de la version Victor
# (peinte comme le mur : le meuble flotte) ; abattants au-dessus, hauteur totale toujours 120. L'angle devient un
# volume plein en chêne (quart de cercle R 12, de la plinthe au plateau, comme le meuble de Victor) : plus d'étagères
# ouvertes ; la box fibre va dans le compartiment du bas, avec la prise, derrière l'abattant.
# Dictionnaire : y0 → y1 l'emprise entière (arrondis compris), ya → yb le caisson à abattants.
NU_PENDERIE = 170   # nu nord de la penderie PAX (V4.7) : caisson 35,5 + porte 1,6 + jeu ≈ 38 depuis la face nord de la SDB
CHAUSSURES = dict(x0=85, x1=110, y0=NU_PENDERIE, ya=208, yb=291, y1=291, z1=120, facade=2, rangs=(8, 45, 83, 120),
                  plateau=3, socle=8, retrait=4)
CHAUSSURES["modules"] = [(CHAUSSURES["ya"], CHAUSSURES["yb"])]
PAIRES = 18

# ------------------------------------------------------------------ angle arrondi du meuble à chaussures (bout nord)
# Quart de cercle plein (V4.10 : rayon réduit de 25 à 12), posé sur la plinthe (8) : pas d'arête dans le passage.
ANGLE = dict(x0=CHAUSSURES["x0"], x1=CHAUSSURES["x1"], y0=NU_PENDERIE, y1=CHAUSSURES["ya"], r=12)

# ------------------------------------------------------------------ meuble haut au-dessus du meuble à chaussures (V4.12)
# Même forme que le meuble à chaussures, vu de dessus (x 85 → 110, y 170 → 291, angle plein au coin R 12) : l'angle
# reste un volume plein en chêne, le module de 83 est un caisson fermé par deux portes de placard battantes (au lieu
# d'abattants), de 180 (57 au-dessus du plateau vide-poche) au plafond. Rien à voir avec l'ancien meuble haut en travers
# de l'entrée, retiré à la V4.11.
MEUBLE_HAUT = dict(x0=CHAUSSURES["x0"], x1=CHAUSSURES["x1"], y0=CHAUSSURES["y0"], ya=CHAUSSURES["ya"],
                   yb=CHAUSSURES["yb"], y1=CHAUSSURES["y1"], z0=180, z1=H, facade=CHAUSSURES["facade"], r=ANGLE["r"])
_ym = (MEUBLE_HAUT["ya"] + MEUBLE_HAUT["yb"]) / 2
MEUBLE_HAUT["portes"] = [(MEUBLE_HAUT["ya"], _ym), (_ym, MEUBLE_HAUT["yb"])]

# ------------------------------------------------------------------ ③ penderie IKEA PAX (V4.7)
# Contre la face nord de la salle de bain, à partir de la cloison (x 110) : caisson PAX 75 × 35 × 236 (cotes réelles
# 74,8 × 35,5 × 236,4, pieds réglables), le seul qui tienne dans les 84 (un 100 mangerait l'huisserie de la salle de
# bain à x 200) ; 9 libres à l'est. Portes FORSAND blanc 50 + 25 (règle IKEA pour un caisson de 75), charnières
# KOMPLEMENT à fermeture silencieuse fournies avec les portes. Intérieur KOMPLEMENT pour 35 de profondeur : tringle
# 75 × 35 (cadre à deux barres d'avant en arrière, cintres de face, ≈ 5 manteaux par barre, 12 kg), deux tablettes
# au-dessus, deux étagères à chaussures en bas, lampe LED à détecteur sur pile sous la tablette. Bandeau blanc de 14
# du caisson (236) au plafond. Montage debout possible dès 237 de hauteur sous plafond (fiche IKEA).
# caisson : profondeur du caisson PAX (35 sur la fiche IKEA), celle des cotes ; l'emprise (38) compte la porte et le jeu.
# V4.10 : posée sur une plinthe de 8 en retrait de 4, comme le meuble à chaussures (même hauteur, même teinte) : caisson
# de 8 à 244, bandeau de 6 au-dessus ; hauteurs intérieures (tringle, tablettes, étagères) depuis le sol fini.
# V4.11 : plinthe continue avec celle de l'angle du meuble à chaussures : pas de retrait à l'ouest (elle bute contre la
# plinthe de l'angle, à x 110) et nu avant aligné sur elle (4 en retrait des portes, y 174) ; avant, le flanc India de la
# penderie se voyait entre les deux plinthes.
PENDERIE = dict(x0=110, x1=185, y0=NU_PENDERIE, y1=208, h=236, socle=8, retrait=4, facade=2, portes=(50, 25),
                barres=(129, 166), manteaux=10, caisson=35)
PENDERIE.update(z1=PENDERIE["socle"] + PENDERIE["h"], porte_z=(PENDERIE["socle"] + 4, PENDERIE["socle"] + 233.4),
                tringle=PENDERIE["socle"] + 195, etageres=(PENDERIE["socle"] + 200, PENDERIE["socle"] + 218),
                chaussures=(PENDERIE["socle"] + 10, PENDERIE["socle"] + 32))
IKEA = [   # IKEA France, fiches produit relevées le 13/11/2026, blanc
    ("PAX caisson d'armoire 75 × 35 × 236", "604.582.27", 1, 80),
    ("FORSAND porte avec charnières 50 × 229", "692.443.12", 1, 55),
    ("FORSAND porte avec charnières 25 × 229", "292.794.74", 1, 50),
    ("KOMPLEMENT tringle à habits 75 × 35", "804.464.55", 1, 12),
    ("KOMPLEMENT tablette 75 × 35", "702.779.95", 2, 11),
    ("KOMPLEMENT étagère à chaussures 75 × 35", "802.572.61", 2, 15),
    ("KÖLVATTEN éclairage LED à détecteur, sur pile, 50 cm", "205.689.87", 1, 14.99),
]
# Portes possibles pour ce caisson (prix de la porte avec ses charnières) : FORSAND blanc 50 + 25 = 105 € ;
# ÅHEIM miroir 25 à la place de la FORSAND 25 (80 €) ; FARDAL brillant blanc 105 + 75 ; Plum Living : deux portes
# 37 × 236 en laque mate (232 € pièce, toutes teintes dont India) + 2 × 4 charnières KOMPLEMENT (16 € les 4).
PORTES_PAX = [
    ("FORSAND blanc 50 + 25 (retenu)", 105),
    ("FORSAND 50 + ÅHEIM miroir 25", 135),
    ("FARDAL brillant blanc 50 + 25", 180),
    ("Plum Living 2 × 37 laque mate (India possible)", 496),
]

# ------------------------------------------------------------------ mur de la salle de bain, côté porte d'entrée
# V4.2 : quatre patères en bois au sud (chevilles de chêne), à 180
# V4.9 : comme la version Victor, sans la planche à chaussures : patères au-dessus du sol libre, applique au-dessus
PATERES = [316, 331, 346, 361]          # y
PATERE = dict(z=180, d=3.5, saillie=8)  # patères en bois (chevilles de chêne) : hauteur d'axe, diamètre, saillie
APPLIQUE = dict(y=338, z=220)

# interphone (téléphone de la sonnette, blanc) au mur ouest, à droite de la porte d'entrée vue de l'intérieur ;
# position et taille à relever (dessiné 10 × 22, haut à 162)
INTERPHONE = dict(y0=335, y1=345, z0=140, z1=162)

# ------------------------------------------------------------------ miroir (V4.9 : mur ouest, comme la version Victor)
# 50 × 100 à coins arrondis R 12, juste au nord de l'interphone (8 d'écart), de 110 à 210.
MIROIR = dict(y0=INTERPHONE["y0"] - 8 - 50, y1=INTERPHONE["y0"] - 8, z0=110, z1=210, r=12)

# ------------------------------------------------------------------ meuble haut : retiré (V4.11)
# Le meuble suspendu au plafond en travers de la branche d'entrée (V4.1 → V4.10, en option avec / sans à la V4.10) est
# retiré définitivement à la demande du client ; la peinture India commence toujours au nu nord de la penderie.

# ------------------------------------------------------------------ peinture de l'entrée (V4.1)
# Au sud du meuble haut : murs, plafond et porte d'entrée en India Yellow (Farrow & Ball n° 66, teinte supposée).
# V4.2 : India de Plum Living (« Beige 11 - India », jaune soleil lumineux), valeur écran relevée sur plum-living.com
# V4.11 : sans meuble haut, l'India commence toujours au nu nord de la penderie (y 170).
INDIA = dict(nom="India de Plum Living (Beige 11)", couleur="#F5D58C", y0=NU_PENDERIE)

MEUBLES = [
    Bloc("tableau", "tableau", TABLEAU["x0"], TABLEAU["x1"], -1, 0.5, TABLEAU["z0"], TABLEAU["z1"], "tableau", mur="n"),
    Bloc("banc", "banc_plateau", BANC["x0"], BANC["x1"], BANC["y0"], BANC["y1"], BANC["z1"] - BANC["ep"], BANC["z1"], "① banc"),
    Bloc("banc", "banc_joue_o", BANC["x0"], BANC["x0"] + BANC["ep"], BANC["y0"], BANC["y1"], 0, BANC["z1"] - BANC["ep"]),
    Bloc("banc", "banc_joue_e", BANC["x1"] - BANC["ep"], BANC["x1"], BANC["y0"], BANC["y1"], 0, BANC["z1"] - BANC["ep"]),
    Bloc("banc", "banc_traverse", BANC["x0"] + BANC["ep"], BANC["x1"] - BANC["ep"], BANC["y0"], BANC["y0"] + 2, 30, BANC["z1"] - BANC["ep"]),
    Bloc("socle", "chaussures_socle", CHAUSSURES["x0"] + CHAUSSURES["retrait"], CHAUSSURES["x1"], CHAUSSURES["ya"],
         CHAUSSURES["yb"] - CHAUSSURES["retrait"], 0, CHAUSSURES["socle"]),
    Bloc("socle", "chaussures_socle_angle", CHAUSSURES["x0"] + CHAUSSURES["retrait"], CHAUSSURES["x1"],
         ANGLE["y0"] + CHAUSSURES["retrait"], CHAUSSURES["ya"], 0, CHAUSSURES["socle"],
         arrondi=ANGLE["r"] - CHAUSSURES["retrait"]),
    Bloc("angle", "angle", ANGLE["x0"], ANGLE["x1"], ANGLE["y0"], ANGLE["y1"], CHAUSSURES["socle"], CHAUSSURES["z1"], "angle",
         arrondi=ANGLE["r"]),
    Bloc("caisson", "chaussures", CHAUSSURES["x0"] + CHAUSSURES["facade"], CHAUSSURES["x1"], CHAUSSURES["ya"],
         CHAUSSURES["yb"], CHAUSSURES["socle"], CHAUSSURES["z1"], "② chaussures"),
    Bloc("plateau", "vide_poche", CHAUSSURES["x0"], CHAUSSURES["x1"], CHAUSSURES["y0"], CHAUSSURES["y1"], CHAUSSURES["z1"],
         CHAUSSURES["z1"] + CHAUSSURES["plateau"], arrondi=ANGLE["r"]),
    # meuble haut (V4.12) : angle plein, caisson ; ses portes avec les façades, plus bas
    Bloc("angle", "mh_angle", MEUBLE_HAUT["x0"], MEUBLE_HAUT["x1"], MEUBLE_HAUT["y0"], MEUBLE_HAUT["ya"], MEUBLE_HAUT["z0"],
         MEUBLE_HAUT["z1"], arrondi=MEUBLE_HAUT["r"]),
    Bloc("caisson", "mh_caisson", MEUBLE_HAUT["x0"] + MEUBLE_HAUT["facade"], MEUBLE_HAUT["x1"], MEUBLE_HAUT["ya"],
         MEUBLE_HAUT["yb"], MEUBLE_HAUT["z0"], MEUBLE_HAUT["z1"], "meuble haut"),
    Bloc("socle", "penderie_socle", PENDERIE["x0"], PENDERIE["x1"] - PENDERIE["retrait"],
         PENDERIE["y0"] + PENDERIE["retrait"], PENDERIE["y1"], 0, PENDERIE["socle"]),
    Bloc("tall", "penderie", PENDERIE["x0"], PENDERIE["x1"], PENDERIE["y0"] + PENDERIE["facade"], PENDERIE["y1"],
         PENDERIE["socle"], PENDERIE["z1"], "③ penderie PAX"),
    Bloc("tall", "bandeau", PENDERIE["x0"], PENDERIE["x1"], PENDERIE["y0"], PENDERIE["y1"], PENDERIE["z1"], H),
    Bloc("miroir", "miroir", 0, 0.6, MIROIR["y0"], MIROIR["y1"], MIROIR["z0"], MIROIR["z1"], mur="o"),
    Bloc("applique", "applique", 104, 110, APPLIQUE["y"] - 6, APPLIQUE["y"] + 6, APPLIQUE["z"] - 6, APPLIQUE["z"] + 6, mur="e"),
] + [Bloc("patere", f"patere_{k}", 110 - PATERE["saillie"], 110, y - PATERE["d"] / 2, y + PATERE["d"] / 2,
          PATERE["z"] - PATERE["d"] / 2, PATERE["z"] + PATERE["d"] / 2, mur="e") for k, y in enumerate(PATERES)]

MEUBLES.append(Bloc("interphone", "interphone", 0, 3, INTERPHONE["y0"], INTERPHONE["y1"], INTERPHONE["z0"], INTERPHONE["z1"], mur="o"))

# ------------------------------------------------------------------ cadres (V4.4)
# Mur ouest de l'entrée, fins cadres noirs, passe-partout blanc ; 6 d'écart (règle de galerie : cadres identiques,
# écarts égaux et serrés, 5 à 8).
# V4.9 : le miroir prend la place côté interphone ; 4 cadres 30 × 40 en grille 2 × 2 (66 de large) dans les 69 libres
# entre le meuble haut (y 208) et le miroir (y 277), centrés à la hauteur du centre du miroir (160), comme Victor.
# V4.11 : meuble haut retiré, la galerie garde sa place (y 208 : l'alignement du coin de la salle de bain).
CADRES_Y0 = PENDERIE["y1"]
CADRES = dict(l=30, h=40, ecart=6, colonnes=2, rangs=2, zc=(MIROIR["z0"] + MIROIR["z1"]) / 2, ep=2.5)
_lg = CADRES["colonnes"] * CADRES["l"] + (CADRES["colonnes"] - 1) * CADRES["ecart"]
_hg = CADRES["rangs"] * CADRES["h"] + (CADRES["rangs"] - 1) * CADRES["ecart"]
CADRES["yc"] = (CADRES_Y0 + MIROIR["y0"]) / 2
CADRES["y0"], CADRES["y1"] = CADRES["yc"] - _lg / 2, CADRES["yc"] + _lg / 2
CADRES["z0"], CADRES["z1"] = CADRES["zc"] - _hg / 2, CADRES["zc"] + _hg / 2
for i in range(CADRES["colonnes"]):
    for j in range(CADRES["rangs"]):
        _y = CADRES["y0"] + i * (CADRES["l"] + CADRES["ecart"])
        _z = CADRES["z0"] + j * (CADRES["h"] + CADRES["ecart"])
        MEUBLES.append(Bloc("cadre_mur", f"cadre_{i}{j}", 0, CADRES["ep"], _y, _y + CADRES["l"], _z, _z + CADRES["h"], mur="o"))

# peinture India : fines couches sur les faces côté couloir, au sud du meuble haut ; le plafond aussi
_y = INDIA["y0"]
MEUBLES += [
    Bloc("india", "india_ouest", 0, 0.3, _y, 374, 0, H, mur="o"),
    Bloc("india", "india_sdb", 109.7, 110, max(_y, PENDERIE["y1"]), 374, 0, H, mur="e"),
    Bloc("india", "india_sud_o", 0, 2, 373.7, 374, 0, H, mur="s"),
    Bloc("india", "india_sud_e", 77, 110, 373.7, 374, 0, H, mur="s"),
    Bloc("india", "india_sud_linteau", 2, 77, 373.7, 374, H_PORTE, H, mur="s"),
    Bloc("india_plafond", "india_plafond", 0, 110, _y, 374, H - 0.3, H, mur="p"),
    # V4.2 : flanc ouest de la penderie, dans le prolongement de l'angle arrondi, en laque India
    Bloc("india_l", "india_penderie", PENDERIE["x0"] - 0.3, PENDERIE["x0"], PENDERIE["y0"], PENDERIE["y1"], PENDERIE["socle"], H),
]

# façades : abattants du meuble à chaussures, portes de la penderie
for k, (y0, y1) in enumerate(CHAUSSURES["modules"]):
    for r, (z0, z1) in enumerate(zip(CHAUSSURES["rangs"], CHAUSSURES["rangs"][1:])):
        MEUBLES.append(Bloc("facade", f"abattant_{k}{r}", CHAUSSURES["x0"], CHAUSSURES["x0"] + CHAUSSURES["facade"],
                            y0 + 0.2, y1 - 0.2, z0 + 0.2, z1 - 0.2))
for k, (y0, y1) in enumerate(MEUBLE_HAUT["portes"]):     # portes de placard du meuble haut, face à l'ouest
    MEUBLES.append(Bloc("facade", f"mh_porte_{k}", MEUBLE_HAUT["x0"], MEUBLE_HAUT["x0"] + MEUBLE_HAUT["facade"],
                        y0 + 0.2, y1 - 0.2, MEUBLE_HAUT["z0"] + 0.2, MEUBLE_HAUT["z1"] - 0.2))
_xm = PENDERIE["x0"] + PENDERIE["portes"][0]          # joint des portes de 50 (ouest) et 25 (est)
for k, (x0, x1) in enumerate(((PENDERIE["x0"], _xm), (_xm, PENDERIE["x1"]))):
    MEUBLES.append(Bloc("facade_p", f"porte_penderie_{k}", x0 + 0.2, x1 - 0.2, PENDERIE["y0"],
                        PENDERIE["y0"] + PENDERIE["facade"], *PENDERIE["porte_z"]))

# ------------------------------------------------------------------ déco (variante décorée de la vue du banc, V4.4)
# Emprises seulement ; rendu.py y place des modèles (plante, bol, vase, paniers, livres) ou des volumes simples.
# Tapis de couloir plat (la porte d'entrée passe dessus) de 60 × 140, à 10 du mur ouest et de l'angle.
DECO = [
    Bloc("tapis", "tapis", 10, 70, 222, 362, 0, 0.8),
    Bloc("plante", "plante_angle", 88, 108, 172, 194, 123, 175),                 # sur le plateau, au-dessus de l'angle
    Bloc("bol", "bol_cles", 89, 107, 226, 244, 123, 129),                        # vide-poche pour les clés
    Bloc("vase", "vase_plateau", 92, 106, 270, 284, 123, 153),
    Bloc("sac", "sac_patere", 104.5, 108, 318, 346, 140, 180),                   # tote en toile à la première patère
]

# ------------------------------------------------------------------ dégagements (cm)
# V4.9 : coin nord-est de la penderie (façade) → coin du mur qui sépare le salon du couloir et de la chambre (x 264,
# y 104, au bout du passage du salon) : la diagonale la plus courte du couloir à cet endroit.
PAX_MUR = dict(a=(185, NU_PENDERIE), b=(264, 104))
PAX_MUR["d"] = math.dist(PAX_MUR["a"], PAX_MUR["b"])
PASSAGES = [
    dict(a=(0, 270), b=(CHAUSSURES["x0"], 270), label=f"{CHAUSSURES['x0']}"),
    dict(a=(0, 345), b=(110, 345), label="110"),
    dict(a=PAX_MUR["a"], b=PAX_MUR["b"], label=f"{PAX_MUR['d']:.0f}"),
    dict(a=(150, BANC["y1"]), b=(150, PENDERIE["y0"]), label=f"{PENDERIE['y0'] - BANC['y1']}"),
    dict(a=(310, 104), b=(310, 208), label="104"),      # V4.9 : déplacé de x 230 à 310, hors de la diagonale
]

# ------------------------------------------------------------------ ouverture de la porte d'entrée (V4.10)
# Vantail de 75 sur paumelles côté salle de bain (x 77), ouvrant vers le couloir ; pivot au nu intérieur (77, 374),
# comme le plan. Ouvert, sa face intérieure regarde l'est : la béquille intérieure (axe à 6 du chant libre, levier de
# 12 tourné vers les paumelles, saillie 7 depuis la face, à 105 du sol) passe devant le bout du meuble à chaussures puis
# vient contre la cloison de la salle de bain. On tourne le vantail de degré en degré au-delà de 90° jusqu'au premier
# contact : vantail (0 → 204) contre tout, béquille contre ce qui monte à 105 (meuble, cloison).
VANTAIL = dict(pivot=(77, 374), l=75, ep=4, h=H_PORTE)
BEQUILLE = dict(axe=6, long=12, saillie=7, z=105)


def _vantail(phi, s0, s1, t0, t1):
    """Rectangle du vantail ouvert de phi degrés (0 fermé, 90 contre le mur ouest de l'ouverture) : s le long du vantail
    depuis le pivot, t perpendiculaire (positif côté intérieur, la face de la béquille). Renvoie ses 4 coins."""
    a = math.radians(phi)
    u, n = (-math.cos(a), -math.sin(a)), (math.sin(a), -math.cos(a))
    px, py = VANTAIL["pivot"]
    return [(px + s * u[0] + t * n[0], py + s * u[1] + t * n[1]) for s, t in ((s0, t0), (s1, t0), (s1, t1), (s0, t1))]


def vantail(phi):
    return _vantail(phi, 0, VANTAIL["l"], -VANTAIL["ep"], 0)


def bequille(phi):
    """Encombrement de la béquille (rectangle de la rosette au bout du levier, tourné vers les paumelles)."""
    b, l = BEQUILLE, VANTAIL["l"]
    return _vantail(phi, l - b["axe"] - b["long"], l - b["axe"], 0, b["saillie"])


def bequille_trait(phi):
    """Béquille vue de dessus : rosette sur la face, tige, levier vers les paumelles (3 points)."""
    b, l = BEQUILLE, VANTAIL["l"]
    s0 = l - b["axe"]
    return [_vantail(phi, s, s, t, t)[0] for s, t in ((s0, 0), (s0, b["saillie"]), (s0 - b["long"], b["saillie"]))]


def _points(poly, pas=0.25):
    """Points sur le contour d'un polygone, tous les `pas` cm."""
    r = []
    for (x0, y0), (x1, y1) in zip(poly, poly[1:] + poly[:1]):
        n = max(1, int(math.dist((x0, y0), (x1, y1)) / pas))
        r += [(x0 + (x1 - x0) * k / n, y0 + (y1 - y0) * k / n) for k in range(n)]
    return r


def _obstacles(z0, z1):
    """Emprises au sol (nom, x0, x1, y0, y1) de ce qui occupe la tranche de hauteur z0 → z1 dans la branche d'entrée."""
    r = [("cloison de la salle de bain", 110, 200, 208, 374)]
    r += [(b.nom, b.x0, b.x1, b.y0, b.y1) for b in MEUBLES
          if b.z0 < z1 and b.z1 > z0 and b.y1 > 208 and b.role not in ("india", "india_l", "india_plafond")]
    return r


def _contact(poly, obstacles):
    for x, y in _points(poly):
        for nom, x0, x1, y0, y1 in obstacles:
            if x0 < x < x1 and y0 < y < y1:
                return nom
    return None


def _distance(poly, x0, x1, y0, y1):
    return min(math.hypot(max(x0 - x, 0, x - x1), max(y0 - y, 0, y - y1)) for x, y in _points(poly))


def ouverture():
    """Angle d'ouverture maximal (au demi-degré) et ce qui l'arrête ; jeu entre la béquille et le meuble à 90°."""
    obst_v = _obstacles(0, VANTAIL["h"])
    obst_b = _obstacles(BEQUILLE["z"] - 2, BEQUILLE["z"] + 2)
    phi = 90.0
    while True:
        nom = _contact(vantail(phi + 0.5), obst_v) or _contact(bequille(phi + 0.5), obst_b)
        if nom:
            break
        phi += 0.5
    c = CHAUSSURES
    jeu = _distance(bequille(90), c["x0"], c["x1"], c["y0"], c["y1"])
    return dict(max=phi, obstacle=nom, jeu_meuble=jeu,
                jeu_vantail=_distance(vantail(90), c["x0"], c["x1"], c["y0"], c["y1"]))


OUVERTURE = ouverture()
OUVERTURE["cause"] = ("le vantail touche la première patère" if OUVERTURE["obstacle"].startswith("patere")
                      else "la béquille touche la cloison" if OUVERTURE["obstacle"].startswith("cloison")
                      else f"contact : {OUVERTURE['obstacle']}")
OUVERTURE["butoir"] = 5 * math.floor((OUVERTURE["max"] - 3) / 5)      # butoir de sol quelques degrés avant le contact

# V4.11 : texture tirée de la photo du carrelage en place (client, 17/11/2026) : un carreau entier, éclairage aplani
# (tache de soleil et ombre retirées), retourné en miroir d'un carreau à l'autre ; taille des carreaux non relevée.
# couleur : teinte multipliée à la photo, gamma : contraste (rendu seulement ; le plan garde son fond clair).
CARRELAGE = dict(taille=60, joint=0.3, couleur="#DDD6CB", gamma=1.3, nuance="#CFC7B9", couleur_joint="#7E766B",
                 texture="pieces/entree/textures/carrelage_travertin.jpg",
                 nom="existant, effet travertin beige (d'après photo), carreaux dessinés en 60 × 60")
MUR_COULEUR = "#EFE9DC"            # blanc chaud de la cuisine et du salon (texte, variante Victor)
PAX_TEINTE = "color_blanc_pur"     # teinte d'origine de la penderie (FORSAND blanc) dans le sélecteur Plum Living
PLINTHE_TEINTE = "color_galet"     # plinthes du meuble à chaussures et de la penderie, proches du blanc des murs
# V4.11 : murs du couloir hors de l'entrée India, au choix dans « Personnaliser » ; par défaut Galet, la peinture murale
# Plum Living la plus proche du blanc chaud de la cuisine et du salon
MUR_TEINTE = "color_galet"

# meubles touchables du plan : meuble = nom du dictionnaire dont la zone prend l'emprise et la fiche ses cotes
# (vues.py) ; porte = nom de la porte de la pièce ; un bord donné ici (x0…y1) remplace celui du meuble.
# principe = rang de l'explication, coupe = repère de la coupe, iso = coin
ZONES = (
    dict(meuble="BANC", principe=0, coupe="A", iso="so"),
    dict(meuble="CHAUSSURES", plateau=True, principe=1, coupe="B", iso="so"),
    dict(meuble="PENDERIE", principe=2, coupe="C", iso="no"),
    dict(porte="ouest", principe=4, coupe=None, iso="no"),
)

RENDUS = [("iso_so", "Isométrique depuis le sud-ouest : banc sous le tableau, meuble à chaussures sur plinthe, patères"),
          ("iso_no", "Isométrique depuis le nord-ouest : penderie, meuble à chaussures sur plinthe, porte d'entrée"),
          ("iso_se", "Isométrique depuis le sud-est, sur l'entrée : mur ouest en India avec cadres, miroir et interphone"),
          ("banc", "Assis sur le banc, vers la porte d'entrée : penderie, entrée en India")]

CHANGEMENTS = [
    ("V4.13", "17/11/2026", "Plinthes murales de 8 le long de tous les murs du couloir, arrêtées aux ouvertures, dans "
     "les rendus ; même teinte que les plinthes des meubles (option « Teinte des plinthes »). Rendus refaits."),
    ("V4.12", "17/11/2026", "Meuble haut au-dessus du meuble à chaussures, de la même forme vu de dessus (angle plein "
     "au coin arrondi R 12, module de 83) : de 180 au plafond, fermé par deux portes de placard battantes au lieu "
     "d'abattants. Rendus refaits."),
    ("V4.11", "17/11/2026", "Plinthe continue de l'angle du meuble à chaussures à la penderie : la plinthe de la "
     "penderie n'est plus en retrait côté ouest et s'aligne sur celle de l'angle (4 en retrait des portes) ; le bout de "
     "flanc peint en India qui se voyait entre les deux a disparu. Meuble haut retiré définitivement (et l'option "
     "« Meuble haut ») ; l'India commence toujours au nu de la penderie, les cadres gardent leur place. Teinte des murs "
     "du reste du couloir au choix dans « Personnaliser » (sélecteur Plum Living, Galet par défaut) : rendus et murs "
     "vus de face sur les coupes. Sol des rendus refait d'après la photo du carrelage en place (effet travertin beige). "
     "Rendus refaits."),
    ("V4.10", "16/11/2026", "Meuble à chaussures : l'arrondi sud et ses étagères sont retirés, le meuble s'arrête net au "
     "bout du module (121 de long, angle arrondi au nord compris). L'angle devient un quart de cercle plein en chêne "
     "(R 12, de la plinthe au plateau), sans étagères ; la box fibre passe dans le compartiment du bas. Meuble haut "
     "peint en India comme les murs et le plafond qui l'entourent (plus de chêne) : tablette retirée côté couloir "
     "(une seule niche ouverte), placard côté entrée fermé par une seule porte coulissante qui glisse de gauche à "
     "droite, au lieu des portes battantes ; il se lit mieux sur les coupes (contour). Arrondi de l'angle réduit de "
     "R 25 à R 12. Penderie PAX sur une plinthe de 8 en retrait de 4, comme le meuble à chaussures (caisson "
     "de 8 à 244, bandeau de 6) ; teinte des plinthes au choix (sélecteur Plum Living, Galet par défaut). "
     "Option « Meuble haut » (avec ou sans) dans « Personnaliser » : plan, coupes et rendus. "
     "Sélecteurs de teinte compacts : une pastille, qui ouvre la fenêtre des teintes. "
     "Teinte de la penderie PAX au choix dans « Personnaliser » : second sélecteur Plum Living (laques de façade), "
     "comme celui des murs ; plan, coupes et rendus suivent (un masque de rendu par surface). "
     "Plinthe de 8 en retrait de 4 sous tout le meuble, "
     "peinte comme le mur, comme le banc de la version Victor : abattants de 37 au-dessus, hauteur toujours 120. "
     "Ouverture de la porte d'entrée vérifiée avec la béquille : à 90°, elle passe à 14 cm du bout du meuble ; la "
     "porte va jusqu'à 112° (le vantail touche alors la première patère), butoir de sol à 105°. Débattement, "
     "béquille et position maximale dessinés sur le plan."),
    ("V4.9", "16/11/2026", "Idées de la version Victor reprises. Meuble à chaussures : le module côté porte d'entrée est "
     "retiré ; il reste un module de 83 à trois abattants (≈ 18 paires), monté à 120 (plateau à 123), arrondi aux deux "
     "bouts : l'angle à étagères au nord, un quart de cercle ouvert de rayon 25 au sud. La prise fibre (cloison de la "
     "salle de bain, en bas côté nord, à 26 du sol) reste accessible derrière l'abattant du bas, sans dos, avec un "
     "passe-câble vers l'étagère basse de l'angle. Côté porte, sol libre (110 de passage) et les quatre patères de "
     "Victor, sans planche, applique au-dessus. Miroir 50 × 100 sur le mur ouest, à côté de l'interphone ; galerie "
     "réduite à 4 cadres (2 × 2) entre le meuble haut et le miroir. Nouvelle coupe D (mur ouest). Cote du coin de la "
     "penderie au coin du mur entre salon et chambre : 103 en diagonale (79 en x, 66 en y)."),
    ("V4.8", "13/11/2026", "Sélecteur « Teinte » dans la barre du haut : les 52 teintes Plum Living (40 laques de "
     "façade, 30 peintures murales, relevées sur plum-living.com), groupées selon la gamme. Il change ensemble toutes "
     "les surfaces India : plan, coupes et vues 3D, sans un rendu par couleur (rendu neutre + masque, recoloré par "
     "un filtre SVG : un mur bien éclairé prend la teinte affichée par Plum Living). Choix gardé d'une page de l'entrée à l'autre. Constat : India "
     "n'existe pas en peinture murale chez Plum Living."),
    ("V4.7", "13/11/2026", "Penderie remplacée par une IKEA PAX 75 × 35 × 236 (la seule largeur qui tienne dans les 84) : "
     "portes FORSAND blanc 50 + 25 avec charnières à fermeture silencieuse, tringle KOMPLEMENT 75 × 35 (cintres de "
     "face, ≈ 10 manteaux), deux tablettes, deux étagères à chaussures, lampe LED à détecteur ; bandeau de 14 "
     "jusqu'au plafond ; ≈ 264 €. Nu nord à y 170 (au lieu de 168) : l'angle arrondi, le meuble haut et la "
     "peinture India suivent. Section Achats IKEA et comparatif des portes."),
    ("V4.6", "13/11/2026", "Silhouette remplacée par un corps humain réaliste (Human Base Meshes de Blender Studio, CC0), mis à 1,75 m."),
    ("V4.5", "13/11/2026", "Silhouette de 1,75 m semi-transparente dans les trois vues isométriques, pour l'échelle."),
    ("V4.4", "13/11/2026", "Galerie de 6 cadres 30 × 40 (grille 3 × 2, centrée à 150) sur le mur ouest de l'entrée, "
     "entre le meuble haut et l'interphone. La vue décorée du banc, essayée, est retirée de la page."),
    ("V4.3", "13/11/2026", "Meuble haut aligné sur la penderie (y 168 → 208, 40 de profondeur) : la couleur India commence "
     "à son nu nord. Interphone blanc au mur ouest, à droite de la porte d'entrée. Deux vues de plus : isométrique "
     "depuis le sud-est sur l'entrée, et vue assis sur le banc."),
    ("V4.2", "13/11/2026", "Couleur India : celle de Plum Living (Beige 11 - India, jaune soleil, #F5D58C) au lieu de "
     "l'India Yellow de Farrow & Ball. Flanc ouest de la penderie, dans le prolongement de l'angle arrondi, en India. "
     "Miroir à coins arrondis (R 12). Les deux patères au nord du miroir sont retirées ; les quatre du sud sont des "
     "chevilles en chêne, montées à 180. Vues isométriques refaites."),
    ("V4.1", "13/11/2026", "Miroir réduit à 50 de large (raccourci au sud, applique recentrée) et quatre patères de "
     "plus à sa droite (six en tout). Nouveau meuble haut ④ suspendu au plafond en travers de la branche d'entrée "
     "(110 × 34, de 204 au plafond) : étagères ouvertes côté couloir, placard à deux portes côté porte d'entrée ; il "
     "délimite l'entrée. Au sud de ce meuble, murs, plafond et porte d'entrée peints en India Yellow (Farrow & Ball "
     "n° 66). Vues isométriques refaites."),
    ("V4.0", "13/11/2026", "Page refaite sur le modèle du salon et de la cuisine : une source de données "
     "(3d/entree/modele.py) dont sont tirés le plan, trois coupes et le rendu 3D ; deux vues isométriques "
     "(sud-ouest et nord-ouest) ; boutons Explications et Changements, sommaire. Aménagement inchangé (V3.3). "
     "La V3.3 est archivée (archive/entree-amenagement-v3.3.html)."),
    ("V3.3", "01/10/2026", "Penderie moins profonde : 84 × 40 au lieu de 84 × 60, deux tringles extractibles (cintres "
     "de face) au lieu d'une tringle en travers. Angle arrondi raccourci en conséquence (meuble à chaussures jusqu'à "
     "y 193, quart de cercle R 25 jusqu'au nu de la penderie, y 168). 130 cm entre le banc et la penderie ; la porte de "
     "la pièce ouest n'a plus besoin de s'ouvrir à 180°."),
    ("V3.2", "01/10/2026", "Angle arrondi aligné sur la façade de la penderie : le meuble à chaussures se prolonge "
     "jusqu'à y 173, puis un quart de cercle de rayon 25 arrive au nu de la penderie (y 148)."),
    ("V3.1", "01/10/2026", "Angle arrondi redessiné : quart de cercle de rayon 25 au bout du meuble à chaussures, contre "
     "le flanc de la penderie (au lieu d'un quart d'ellipse 25 × 60)."),
    ("V3", "01/10/2026", "Banc et penderie échangés (demande du client) : banc 95 × 38 posé sous le tableau électrique, "
     "entre la cuisine et le WC ; penderie 84 × 60 toute hauteur contre la face nord de la salle de bain ; angle arrondi "
     "agrandi à 25 × 60, ouvert, à 95 de haut ; patères du mur nord de la SDB supprimées (2 restent au-dessus du meuble "
     "à chaussures). Porte de la pièce ouest à ouvrir à 180°. La V2.1 est archivée (archive/entree-amenagement-v2.html)."),
    ("V2.1", "01/10/2026", "Porte du salon supprimée : l'ouverture du couloir vers le salon est un passage libre."),
    ("V2", "01/10/2026", "Penderie supprimée : le tableau électrique est encastré dans le trumeau entre la cuisine et le "
     "WC, et la NF C 15-100 interdit d'y ranger quoi que ce soit devant. Les manteaux passent sur 8 patères (6 au-dessus "
     "du banc, 2 au-dessus du meuble à chaussures). Angle arrondi en quart de rond 25 × 38 entre le meuble à chaussures "
     "(166 × 25) et le banc (84 × 38). La V1 est archivée (archive/entree-amenagement-v1.html)."),
    ("V1", "01/10/2026", "Première proposition à partir du relevé : penderie 95 × 60 entre la cuisine et le WC, meuble "
     "à chaussures 160 × 25 avec miroir le long de la salle de bain, banc 82 × 38 avec patères face au nord. Plan et "
     "trois élévations."),
]


# ------------------------------------------------------------------ le document déclaré (tâche 13)
# DOCUMENT dépend de victor.py, qui lit ce fichier : on le construit à la première lecture (`document.DOCUMENT`),
# pas à l'import, pour éviter l'import circulaire.


def _options():
    """Sélecteurs Plum Living : la teinte de l'entrée (India), celle de la penderie PAX (laques), des plinthes et des
    murs du reste du couloir (V4.11)."""
    from pieces.entree.amenagement import plum
    return (plum.selecteur("teinte", "Teinte de l'entrée", ("murs", "plafond", "porte"), css="--india"),
            plum.selecteur("pax", "Teinte de la penderie PAX", ("caisson", "portes"), defaut=PAX_TEINTE, css="--pax",
                           laques=True, portee="Penderie de la variante principale : plan, coupes et rendus."),
            plum.selecteur("plinthe", "Teinte des plinthes", ("meuble à chaussures", "penderie", "murs"), defaut=PLINTHE_TEINTE,
                           css="--plinthe", portee="Coupes et rendus."),
            plum.selecteur("murs", "Teinte des murs du couloir", ("murs hors de l'entrée",), defaut=MUR_TEINTE,
                           css="--mur", portee="Coupes et rendus."),
            option_coussin())


def option_coussin():
    """Teinte du coussin du banc de la version Victor (V1.6) : tissus, pas des peintures."""
    from pieces.entree.amenagement import victor
    return Option(id="coussin", nom="Teinte du coussin", surfaces=("coussin du banc",), type="nuancier",
                  defaut=victor.COUSSIN_DEFAUT, css="--coussin", filtre=True,
                  valeurs=tuple(Valeur(code=c, nom=n, couleur=h, groupe="Tissus",
                                       note="valeur d'écran indicative, à choisir sur échantillon")
                                for c, n, h in victor.COUSSIN_TEINTES),
                  portee="Version Victor : coupes et rendus.")


def _changements(liste):
    return tuple(Changement(*c) for c in liste)


def _document():
    from pieces.entree.amenagement import victor, vues
    principale = Variante("principale", "Principale", VERSION, _changements(CHANGEMENTS), FIGEES_ANCIENNES)
    var_victor = Variante("victor", "Victor", victor.VERSION, _changements(victor.CHANGEMENTS))
    # dessins.css sert toutes les variantes : il réunit le CSS du module de dessin de chacune (celui de Victor ajoute
    # .talli et .tallic) ; css_dessins n'en garde qu'une fois les règles communes
    css = "\n".join(dessin.CSS for _, dessin in vues.VARIANTES.values())
    return Document(piece="entree", id="amenagement", nom="Aménagement", type="amenagement",
                    variantes=(principale, var_victor), generer=vues.vues, options=_options(), css=css)


def __getattr__(nom):
    if nom == "DOCUMENT":
        globals()["DOCUMENT"] = _document()
        return globals()["DOCUMENT"]
    raise AttributeError(f"module {__name__!r} has no attribute {nom!r}")
