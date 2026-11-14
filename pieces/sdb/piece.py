# Salle de bain : la pièce (alcôve du meuble linge, porte d'entrée, réseaux, machine).
#
# Ce fichier ne contient que des données, reprises de 3d/sdb/modele.py (V6.4), où le meuble haut les lit encore :
# un test (tests/test_sdb_piece.py) garde les deux égaux tant que l'ancien modèle existe. Le meuble bas est dans
# meuble_bas/ ; les dessins partagés par les deux meubles dans dessin_cotes.py et iso.py.
#
# Cotes en cm : x vers l'est depuis le mur ouest de la salle de bain, y vers le sud depuis son mur nord, z depuis le
# sol fini. C'est le repère des pages du meuble ; POSITION le pose dans celui de l'appartement.

ID = "sdb"
NOM = "Salle de bain"
POSITION = (120, 218, 0)    # x, y (cm) et rotation (degrés) dans le repère de l'appartement
H = 250                     # plafond (confirmé par le client)

# ------------------------------------------------------------------ alcôve est (relevés client)
X1 = 234                            # mur du fond (est) de l'alcôve, au nu du carrelage
Y0, Y1 = 0, 115                     # mur nord et mur sud (V5.6 : relevé client, fond 115 ; avant : 114)
ALCOVE = dict(nord=62, sud=68)      # profondeur des murs de retour de l'alcôve depuis le mur du fond (relevé client)
X0 = X1 - ALCOVE["sud"]             # bout du mur sud (côté lavabo) : 166

# ------------------------------------------------------------------ contour, pour le plan de l'appartement
# Contour de l'accueil, gardé tel quel : la salle de bain y est profonde de 156 (y 0 → 156), et l'alcôve
# (x 166 → 234, y 0 → 115) en sort à l'est. Le plan du meuble, lui, dessine une pièce de SDB["p"] = 160 de profondeur :
# 4 d'écart, non tranché (à vérifier sur place).
P_ACCUEIL = 156
SOL = [(0, 0), (X1, 0), (X1, Y1), (X0, Y1), (X0, P_ACCUEIL), (0, P_ACCUEIL)]
SDB = dict(l=234, p=160)            # la pièce telle que la dessine le plan du meuble (V3)

# ------------------------------------------------------------------ porte d'entrée, au mur nord
GONDS = 69              # V5.11 : gonds de la porte d'entrée à 69 du mur du fond (relevé client ; avant : 77)
PORTE = dict(x0=X1 - GONDS - 73, x1=X1 - GONDS, l=73)   # porte standard de 73 (client), vantail ouvert à 90° le long des gonds
CHAMBRANLE = 0.5        # V5.16 : le chambranle de la porte d'entrée déborde de 0,5 du mur nord (relevé client)
# La même porte sur le plan de l'appartement (commun/appartement.py, BAIES) : x 80 → 156, gonds à 78 du mur du fond au
# lieu de 69 (9 d'écart, à vérifier sur place).
PORTE_ACCUEIL = dict(x0=80, x1=156)

# ------------------------------------------------------------------ équipements de la pièce (plan du meuble, V3)
DOUCHE = (5, 50, 78, 155)               # x0, y0, x1, y1
LAVABO = (82, Y1, 165, 160)

# ------------------------------------------------------------------ murs et réseaux de l'alcôve
CARRELAGE = 204         # hauteur du carrelage (relevé client, V5.8)
EP_CARRELAGE = 1.0      # V5.16 : épaisseur carreau + colle (estimée, à mesurer) ; les cotes du relevé sont prises sur le carreau
ROBINET = dict(y=74, z=102)             # robinet d'arrêt : 41 du mur sud (V5.7), 15 au-dessus de l'ancien plan (V6.0)
# V6.0 : tuyaux au mur du fond, à l'aplomb du robinet ; zone (x0, x1, y0, y1, z0, z1) où le meuble ne met rien ;
# saillie_max : place entre le mur et le dos de la machine
TUYAUX = dict(zone=(229, 234, 66, 82, 50, 85.5), evacuation_z=60, arrivee_z=80, saillie_max=5)
PASSE = dict(l=6, p=4)                  # encoche du passe-tuyau : 6 de large, 4 de profondeur dans le chant arrière du plateau

# ------------------------------------------------------------------ machine
MACHINE = dict(l=59.5, p=53, h=85, nom="lave-linge 59,5 × 53 × 85 (relevé client)")

CAMERAS = ()    # pas de rendu de la salle de bain
