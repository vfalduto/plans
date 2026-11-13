# Entrée : la pièce (enveloppe, portes, cloisons) et les caméras communes à toutes les variantes.
#
# Ce fichier ne contient que des données. L'aménagement est dans amenagement/document.py (principale) et victor.py.
#
# Cotes en cm : x vers l'est depuis le mur ouest du couloir, y vers le sud depuis son mur nord, z depuis le sol fini.
# Chaque volume : Bloc(role, nom, x0, x1, y0, y1, z0, z1). Le rôle fixe le style du plan, des coupes et du rendu.

from dataclasses import dataclass

from commun.modele import Camera

ID = "entree"
NOM = "Entrée"
POSITION = (0, 0, 0)    # x, y (cm) et rotation (degrés) dans le repère de l'appartement
H = 250                 # hauteur sous plafond (reprise de la salle de bain)
EP = 10                 # épaisseur des cloisons
H_PORTE = 204           # hauteur des portes (passage libre)


@dataclass
class Bloc:
    role: str
    nom: str
    x0: float
    x1: float
    y0: float
    y1: float
    z0: float
    z1: float
    etiq: str = ""      # nom affiché sur les coupes
    arrondi: float = 0  # rayon du coin nord-ouest arrondi (vu de dessus), 0 : angle vif
    mur: str = ""       # mur qui le porte (n, s, e, o) : caché avec ce mur dans les vues 3D en coupe


# ------------------------------------------------------------------ enveloppe (relevé du 01/10/2026)
# Couloir en L : branche nord 264 × 104 (cuisine, WC, tableau électrique), prolongée vers l'est jusqu'à 354 entre
# y 104 et 208 (salon, chambre, salle de bain), et branche d'entrée 110 × 166 le long de la salle de bain.
SOL = [(0, 0), (264, 0), (264, 104), (354, 104), (354, 208), (110, 208), (110, 374), (0, 374)]
SURFACE = 8.1           # m², relevé

# Portes : mur, ouverture (a → b le long du mur), côté des paumelles (a ou b), sens d'ouverture, type.
#   mur n / s : a, b en x ; mur e / o : a, b en y ; face : coordonnée du nu du mur côté couloir.
PORTES = [
    dict(nom="cuisine", piece="Cuisine", mur="n", face=0, a=8, b=87, type="coulissante"),
    dict(nom="wc", piece="WC", mur="n", face=0, a=191, b=264, type="battante", gond="a", vers="piece"),
    dict(nom="salon", piece="Salon", mur="e", face=264, a=2, b=80, type="passage"),
    dict(nom="chambre", piece="Chambre", mur="e", face=354, a=115, b=186, type="battante", gond="b", vers="piece"),
    dict(nom="sdb", piece="Salle de bain", mur="s", face=208, a=200, b=276, type="battante", gond="b", vers="piece"),
    dict(nom="entree", piece="Palier", mur="s", face=374, a=2, b=77, type="battante", gond="b", vers="couloir"),
    dict(nom="ouest", piece="Pièce ouest", mur="o", face=0, a=83, b=160, type="battante", gond="b", vers="couloir"),
]

# Cloisons, ouvertures déduites ; « mur » : côté du couloir qu'elles bordent (pour les coupes 3D).
MURS = [
    Bloc("mur", "nord_o", -10, 8, -10, 0, 0, H, mur="n"),
    Bloc("mur", "nord_m", 87, 191, -10, 0, 0, H, mur="n"),
    Bloc("mur", "nord_e", 264, 274, -10, 0, 0, H, mur="n"),
    Bloc("mur", "salon_n", 264, 274, 0, 2, 0, H, mur="e"),
    Bloc("mur", "salon_s", 264, 274, 80, 104, 0, H, mur="e"),
    Bloc("mur", "salon_sud", 274, 364, 94, 104, 0, H, mur="n"),
    Bloc("mur", "chambre_n", 354, 364, 104, 115, 0, H, mur="e"),
    Bloc("mur", "chambre_s", 354, 364, 186, 218, 0, H, mur="e"),
    Bloc("mur", "sdb_n_o", 110, 200, 208, 218, 0, H, mur="s"),
    Bloc("mur", "sdb_n_e", 276, 354, 208, 218, 0, H, mur="s"),
    Bloc("mur", "sdb_o", 110, 120, 218, 384, 0, H, mur="e"),
    Bloc("mur", "entree_o", -10, 2, 374, 384, 0, H, mur="s"),
    Bloc("mur", "entree_e", 77, 110, 374, 384, 0, H, mur="s"),
    Bloc("mur", "ouest_n", -10, 0, 0, 83, 0, H, mur="o"),
    Bloc("mur", "ouest_s", -10, 0, 160, 374, 0, H, mur="o"),
]


def _linteaux_et_vantaux():
    r = []
    for p in PORTES:
        a, b = p["a"], p["b"]
        if p["mur"] in "ns":
            y0, y1 = (p["face"] - EP, p["face"]) if p["mur"] == "n" else (p["face"], p["face"] + EP)
            box = (a, b, y0, y1)
        else:
            x0, x1 = (p["face"], p["face"] + EP) if p["mur"] == "e" else (p["face"] - EP, p["face"])
            box = (x0, x1, a, b)
        r.append(Bloc("linteau", f"linteau_{p['nom']}", *box, H_PORTE, H, mur=p["mur"]))
        if p["type"] == "passage":
            continue
        # vantail fermé (coupes et rendu ; le plan le dessine ouvert à 90°) : 4 d'épaisseur au milieu de la cloison,
        # la porte coulissante de la cuisine glisse côté cuisine, contre la cloison
        if p["type"] == "coulissante":
            r.append(Bloc("porte", f"porte_{p['nom']}", a - 4, b + 4, -EP - 4, -EP, 0, H_PORTE + 2, mur=p["mur"]))
        elif p["mur"] in "ns":
            ym = (box[2] + box[3]) / 2
            r.append(Bloc("porte", f"porte_{p['nom']}", a, b, ym - 2, ym + 2, 0, H_PORTE, mur=p["mur"]))
        else:
            xm = (box[0] + box[1]) / 2
            r.append(Bloc("porte", f"porte_{p['nom']}", xm - 2, xm + 2, a, b, 0, H_PORTE, mur=p["mur"]))
    return r


ENVELOPPE = MURS + _linteaux_et_vantaux()

# ------------------------------------------------------------------ caméras, communes aux variantes
CX, CY = 177, 190
CAMERAS = (
    # depuis le sud-ouest : banc et tableau (mur nord), meuble à chaussures, miroir, patères (mur de la salle de bain)
    Camera("iso_so", "Isométrique sud-ouest", (CX - 640, CY + 600, 640), (CX + 10, CY - 20, 110), ortho=7.0,
           reglages=dict(murs="sop")),
    # depuis le nord-ouest : penderie, angle arrondi, meuble à chaussures, porte d'entrée, portes de la SDB et de la chambre
    Camera("iso_no", "Isométrique nord-ouest", (CX - 640, CY - 600, 640), (CX, CY, 60), ortho=6.4,
           reglages=dict(murs="nop")),
    # depuis le sud-est, sur la branche d'entrée : mur ouest, placard du meuble haut, angle
    Camera("iso_se", "Isométrique sud-est", (55 + 640, 270 + 600, 640), (60, 260, 130), ortho=5.4,
           reglages=dict(murs="sep", ombres=False, expo=-1.0)),
    # assis sur le banc (yeux à 112), vers la porte d'entrée ; plafond en place, perspective
    Camera("banc", "Assis sur le banc", (102, 24, 112), (42, 374, 112), focale=17, yeux=112,
           reglages=dict(murs="", expo=-0.9)),
    # debout dans le couloir devant la porte de la pièce ouest, vers le meuble à chaussures ; plafond en place
    Camera("couloir", "Debout dans le couloir", (15, 70, 160), (150, 200, 75), focale=17, yeux=160,
           reglages=dict(murs="", expo=-0.9)),
)
