# Cuisine : la pièce (contour, portes) et les caméras communes à ses documents, tirées du modèle (modele.py).
#
# Ce fichier ne contient que des données. Le modèle (enveloppe et meubles, V13) reste la source unique : l'enveloppe ne
# se sépare pas des meubles (la baie du cellier dépend des colonnes), la pièce en reprend ce qu'il faut.
#
# Cotes en cm : x vers l'est depuis le mur ouest, y vers le sud depuis le mur nord, z depuis le sol fini.

from commun.modele import Camera
from pieces.cuisine import modele

ID = "cuisine"
NOM = "Cuisine"
# x, y (cm) et rotation (degrés) dans le repère de l'appartement (celui du couloir, pieces/entree/piece.py) : le coin
# nord-ouest de la cuisine, posé comme dans le plan de l'accueil (commun/appartement.py, APPART)
POSITION = (-220, -262, 0)

H, Bloc, Cyl, Pan, ENVELOPPE = modele.H, modele.Bloc, modele.Cyl, modele.Pan, modele.ENVELOPPE

# Sol : contour de la cuisine de l'accueil (APPART) moins POSITION, du coin nord-ouest dans le sens des aiguilles d'une
# montre. Les sommets tombent sur le nu des murs du modèle : cloison du cellier (x 327), mur ouest du WC (x 382),
# décroché sud-est (x 341, y 240), mur sud (y 252) ; y 115 est la limite cuisine / cellier de l'accueil.
SOL = [(0, 0), (327, 0), (327, 115), (382, 115), (382, 240), (341, 240), (341, 252), (0, 252)]
# Cuisine et cellier réunis (APPART, cellier compris) : le mini-plan « Position » montre les deux, caméras du
# cellier comprises
SOL_ET_CELLIER = [(0, 0), (434, 0), (434, 44), (484, 44), (484, 100), (382, 100), (382, 240), (341, 240), (341, 252),
                  (0, 252)]
# m², calculée sur le contour (pas de relevé de surface)
SURFACE = abs(sum(x0 * y1 - x1 * y0 for (x0, y0), (x1, y1) in zip(SOL, SOL[1:] + SOL[:1]))) / 2 / 1e4

# Ouvertures, sur le modèle de pieces/entree/piece.py : mur, ouverture (a → b le long du mur), face (coordonnée du nu
# du mur côté cuisine), type. Porte de l'entrée : la baie du mur sud (x 228 → 306 ; l'entrée la note 8 → 87 dans son
# repère, 1 cm d'écart laissé tel quel). Porte du cellier : la baie de la cloison du cellier.
PORTES = [
    dict(nom="entree", piece="Entrée", mur="s", face=252, a=modele.ENTREE["x0"], b=modele.ENTREE["x1"],
         type="galandage"),
    dict(nom="cellier", piece="Cellier", mur="e", face=320, a=modele.BAIE_Y0, b=modele.BAIE_Y1, type="pliante"),
]

# ------------------------------------------------------------------ caméras, communes aux documents
# Points de vue de 3d/v13/rendu.py (VIEWS) ; hauteur des yeux de 3d/rendu.py. Réglages : coupes (objets Blender
# cachés à la caméra, motif sur leur nom), decentrement (shift de l'objectif), porte = "fermee" (porte du cellier
# fermée), nuit (tous les éclairages allumés).
DEBOUT, ASSIS = 163, 120
# V13.27 : cloison et linteau du cellier gardés (la porte, fermée, reste dans son mur), machine à café coupée avec B6
COUPES_ISO = (r"^(mur__(ouest_nord|ouest_sud|sud_ouest|sud_est)|allege__|linteau__(linteau_fenetre|linteau_entree|"
              r"linteau_galandage)|cloison__galandage|porte__entree|ardoise__|aimant__|peinture__|joue__bas_de_mur|"
              r"socle__plinthe_|plafond__|verre__|alu__|ext_)")
COUPES_ISO_NO = (r"^(mur__(nord|nord_alcove|ouest_nord|ouest_sud)|allege__|socle__plinthe_fenetre|linteau__linteau_fenetre|"
                 r"cafetiere__|plafond__|verre__|alu__|ext_|caisson__|caisson_haut__|plan__|plaque__|evier__|"
                 r"cuve__|mitigeur__|egouttoir__|hotte__|led__|credence__|four__facade_b|facade__facade_b|facade_haut__|"
                 r"socle__socle_(b|fileur)|joue__(joue_h|fileur_ouest|fileur_est|fileur_h_est)|fileur__fileur_hauts|"
                 r"etagere_haute__etagere_mur|tech__coffre_reseaux|poignee_(inox|bois)__facade_(b|h)|aspiration__)")
_ISO = dict(loc=(-380, 700, 640), cible=(250, 120, 60), ortho=6.0)
CAMERAS = (
    # isométrique depuis le sud-ouest, murs ouest et sud et plafond coupés
    Camera("iso_so", "Isométrique sud-ouest", **_ISO, reglages=dict(coupes=COUPES_ISO)),
    # la même, de nuit
    Camera("iso_so_nuit", "Isométrique sud-ouest, de nuit", **_ISO, reglages=dict(coupes=COUPES_ISO, nuit=True)),
    # isométrique depuis le nord-ouest
    Camera("iso_no", "Isométrique nord-ouest", (-400, -470, 700), (220, 140, 60), ortho=6.0,
           reglages=dict(coupes=COUPES_ISO_NO, porte="fermee")),
    # depuis la baie d'entrée, vers la rangée nord et la fenêtre
    Camera("entree", "Depuis l'entrée", (268, 236, DEBOUT), (105, 40, DEBOUT), focale=18, yeux=DEBOUT,
           reglages=dict(decentrement=-0.12)),
    # depuis la fenêtre, vers les colonnes et le cellier
    Camera("fenetre", "Depuis la fenêtre", (12, 105, DEBOUT), (330, 140, DEBOUT), focale=18, yeux=DEBOUT,
           reglages=dict(decentrement=-0.12)),
    # assis sur la banquette (une place, mur ouest), vers l'est : chaise, colonnes, porte du cellier
    Camera("banquette", "Assis sur la banquette", (28, 217, ASSIS), (320, 150, ASSIS), focale=20, yeux=ASSIS,
           reglages=dict(decentrement=0.02)),
    # dos à la porte du cellier (fermée), vers la table et la banquette
    Camera("dos_cellier", "Dos à la porte du cellier", (312, (modele.BAIE_Y0 + modele.BAIE_Y1) / 2, DEBOUT),
           (40, 215, DEBOUT), focale=18, yeux=DEBOUT, reglages=dict(decentrement=-0.15, porte="fermee")),
    # entré dans le cellier, porte refermée derrière soi, vers le ballon
    Camera("cellier", "Entrée du cellier", (336, 72, DEBOUT), (470, 60, DEBOUT), focale=14, yeux=DEBOUT,
           reglages=dict(decentrement=-0.15, porte="fermee")),
)
