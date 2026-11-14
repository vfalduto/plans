# Chambre : la pièce (enveloppe, placard existant, porte, fenêtre, climatisation).
#
# Ce fichier ne contient que des données, reprises de l'ancienne page chambre-amenagement.html (V2.1).
# L'aménagement (lit, chevets, plan et commodes) est dans amenagement/document.py.
#
# Cotes en cm : x vers l'est depuis le nu du mur ouest, y vers le sud depuis le nu du mur nord, z depuis le sol fini.
# C'est le repère de la page ; POSITION le pose dans celui de l'appartement.

ID = "chambre"
NOM = "Chambre"
POSITION = (364, 112, 0)    # x, y (cm) et rotation (degrés) dans le repère de l'appartement
H = 250                     # hauteur sous plafond
H_PORTE = 204               # hauteur des portes (passage libre)
L, P = 441, 251             # largeur (est-ouest) et profondeur (nord-sud), placard compris

# Épaisseur des murs, au-delà du nu intérieur : ouest, nord, sud, est.
EP = dict(o=10, n=12, s=12, e=12)

# Décroché plein dans l'angle nord-est : 13 le long du mur nord, 10 le long du mur est.
DECROCHE = dict(x0=428, x1=441, y0=0, y1=10)

# Placard existant, côté ouest, au sud de la porte. cloison : épaisseur de la cloison nord ; jambage : retour du mur
# est du placard ; porte : ouverture en y ; deux vantaux coulissants de 80,5 qui se recouvrent de 6 (rails à
# x 44,5 et 42,5).
PLACARD = dict(x0=0, x1=47, y0=80, y1=251, cloison=7, jambage=5, porte=(92, 247), recouvrement=6)

# Sol, du coin nord-ouest dans le sens des aiguilles d'une montre (décroché et placard déduits).
SOL = [(0, 0), (DECROCHE["x0"], 0), (DECROCHE["x0"], DECROCHE["y1"]), (L, DECROCHE["y1"]), (L, P),
       (PLACARD["x1"], P), (PLACARD["x1"], PLACARD["y0"]), (0, PLACARD["y0"])]
# m², calculée sur le contour (la page ne l'écrit pas)
SURFACE = abs(sum(x0 * y1 - x1 * y0 for (x0, y0), (x1, y1) in zip(SOL, SOL[1:] + SOL[:1]))) / 2 / 1e4

# Porte du couloir, sur le modèle de pieces/entree/piece.py : mur ouest, ouverture y 3 → 70 (67 de large),
# charnière au nord, s'ouvre vers l'intérieur.
PORTE = dict(nom="couloir", piece="Couloir", mur="o", face=0, a=3, b=70, type="battante", gond="a", vers="piece")
PORTES = [PORTE]

# Fenêtre coulissante du mur est : vantail fixe au nord, mobile au sud. Les deux vantaux se recouvrent de 4 ;
# le plan les dessine de (y1 - y0 + recouvrement) / 2 = 73, l'élévation de ((y1 - y0 - 2 cadre) - joint) / 2 = 67.
FENETRE = dict(y0=90, y1=232, allege=106, linteau=215, recouvrement=4, cadre=3, joint=2)

# Climatisation murale, mur nord, contre le décroché, sous le plafond (cotes types).
CLIM = dict(x0=340, x1=428, y0=0, y1=22, z0=220, z1=250)

CAMERAS = ()    # pas de modèle 3D
