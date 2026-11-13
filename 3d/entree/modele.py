# Entrée V4 : source unique (reprend le relevé et l'aménagement de la V3.3, page dessinée à la main).
#
# Ce fichier ne contient que des données : il est lu par plan.py (HTML : plan et coupes, projetés depuis ces volumes)
# et par rendu.py (Blender). Toute modification se fait ici, jamais dans le HTML.
#
# Cotes en cm : x vers l'est depuis le mur ouest du couloir, y vers le sud depuis son mur nord, z depuis le sol fini.
# Chaque volume : Bloc(role, nom, x0, x1, y0, y1, z0, z1). Le rôle fixe le style du plan, des coupes et du rendu.

from dataclasses import dataclass

VERSION = "V4.0"
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

# Tableau électrique encastré dans le trumeau nord, entre la cuisine et le WC : position et taille à relever
# (dessiné au milieu du banc, 60 × 80, bas à 95).
TABLEAU = dict(x0=110, x1=170, z0=95, z1=175)

# ------------------------------------------------------------------ ① banc sous le tableau électrique
# Posé, pas fixé dans la zone du tableau ; dessous ouvert ; on s'y assoit pour se chausser, face au meuble à chaussures.
BANC = dict(x0=92, x1=187, y0=0, y1=38, z1=45, ep=3)

# ------------------------------------------------------------------ ② meuble à chaussures, branche d'entrée
# Contre la cloison de la salle de bain (x 110), 25 de profondeur pour garder 85 de passage ; deux modules de 83,
# chacun à deux abattants superposés (≈ 6 paires par abattant, ≈ 24 en tout) ; plateau vide-poche à 98.
CHAUSSURES = dict(x0=85, x1=110, y0=208, y1=374, z1=95, facade=2, rangs=(0, 48, 95), plateau=3)
CHAUSSURES["modules"] = [(208, 291), (291, 374)]
PAIRES = 24

# ------------------------------------------------------------------ angle arrondi
# Le meuble à chaussures se prolonge jusqu'au nu de la penderie (y 168) et s'y termine par un quart de cercle de
# rayon 25 : étagères ouvertes (clés, courrier) à 95 de haut, pas d'arête dans le passage.
ANGLE = dict(x0=85, x1=110, y0=168, y1=208, r=25, etageres=(31, 63))

# ------------------------------------------------------------------ ③ penderie
# Contre la face nord de la salle de bain, 84 × 40 toute hauteur, deux portes de 42 sur socle de 8. À 40, les cintres
# ne tiennent pas en travers : une tringle extractible derrière chaque porte, cintres de face (≈ 8 manteaux chacune).
PENDERIE = dict(x0=110, x1=194, y0=168, y1=208, socle=8, facade=2, tringle=188, etagere=202, manteaux=8)

# ------------------------------------------------------------------ mur de la salle de bain, au-dessus du meuble
MIROIR = dict(y0=251, y1=331, z0=110, z1=210)
PATERES = [216, 232]          # y, à 165 de haut
APPLIQUE = dict(y=291, z=220)

MEUBLES = [
    Bloc("tableau", "tableau", TABLEAU["x0"], TABLEAU["x1"], -1, 0.5, TABLEAU["z0"], TABLEAU["z1"], "tableau", mur="n"),
    Bloc("banc", "banc_plateau", BANC["x0"], BANC["x1"], BANC["y0"], BANC["y1"], BANC["z1"] - BANC["ep"], BANC["z1"], "① banc"),
    Bloc("banc", "banc_joue_o", BANC["x0"], BANC["x0"] + BANC["ep"], BANC["y0"], BANC["y1"], 0, BANC["z1"] - BANC["ep"]),
    Bloc("banc", "banc_joue_e", BANC["x1"] - BANC["ep"], BANC["x1"], BANC["y0"], BANC["y1"], 0, BANC["z1"] - BANC["ep"]),
    Bloc("banc", "banc_traverse", BANC["x0"] + BANC["ep"], BANC["x1"] - BANC["ep"], BANC["y0"], BANC["y0"] + 2, 30, BANC["z1"] - BANC["ep"]),
    Bloc("angle", "angle", ANGLE["x0"], ANGLE["x1"], ANGLE["y0"], ANGLE["y1"], 0, CHAUSSURES["z1"], "angle", arrondi=ANGLE["r"]),
    Bloc("caisson", "chaussures", CHAUSSURES["x0"] + CHAUSSURES["facade"], CHAUSSURES["x1"], CHAUSSURES["y0"],
         CHAUSSURES["y1"], 0, CHAUSSURES["z1"], "② chaussures"),
    Bloc("plateau", "vide_poche", ANGLE["x0"], CHAUSSURES["x1"], ANGLE["y0"], CHAUSSURES["y1"], CHAUSSURES["z1"],
         CHAUSSURES["z1"] + CHAUSSURES["plateau"], arrondi=ANGLE["r"]),
    Bloc("tall", "penderie", PENDERIE["x0"], PENDERIE["x1"], PENDERIE["y0"] + PENDERIE["facade"], PENDERIE["y1"],
         PENDERIE["socle"], H, "③ penderie"),
    Bloc("socle", "penderie_socle", PENDERIE["x0"] + 2, PENDERIE["x1"] - 2, PENDERIE["y0"] + 5, PENDERIE["y1"], 0, PENDERIE["socle"]),
    Bloc("miroir", "miroir", 109.4, 110, MIROIR["y0"], MIROIR["y1"], MIROIR["z0"], MIROIR["z1"], mur="e"),
    Bloc("applique", "applique", 104, 110, APPLIQUE["y"] - 6, APPLIQUE["y"] + 6, APPLIQUE["z"] - 6, APPLIQUE["z"] + 6, mur="e"),
] + [Bloc("patere", f"patere_{k}", 104, 110, y - 1.2, y + 1.2, 164, 166.5, mur="e") for k, y in enumerate(PATERES)]

# façades : abattants du meuble à chaussures, portes de la penderie
for k, (y0, y1) in enumerate(CHAUSSURES["modules"]):
    for r, (z0, z1) in enumerate(zip(CHAUSSURES["rangs"], CHAUSSURES["rangs"][1:])):
        MEUBLES.append(Bloc("facade", f"abattant_{k}{r}", CHAUSSURES["x0"], CHAUSSURES["x0"] + CHAUSSURES["facade"],
                            y0 + 0.2, y1 - 0.2, z0 + 0.2, z1 - 0.2))
_xm = (PENDERIE["x0"] + PENDERIE["x1"]) / 2
for k, (x0, x1) in enumerate(((PENDERIE["x0"], _xm), (_xm, PENDERIE["x1"]))):
    MEUBLES.append(Bloc("facade_p", f"porte_penderie_{k}", x0 + 0.2, x1 - 0.2, PENDERIE["y0"],
                        PENDERIE["y0"] + PENDERIE["facade"], PENDERIE["socle"] + 0.2, H - 0.5))

# ------------------------------------------------------------------ dégagements (cm)
PASSAGES = [
    dict(a=(0, 270), b=(CHAUSSURES["x0"], 270), label=f"{CHAUSSURES['x0']}"),
    dict(a=(150, BANC["y1"]), b=(150, PENDERIE["y0"]), label=f"{PENDERIE['y0'] - BANC['y1']}"),
    dict(a=(230, 104), b=(230, 208), label="104"),
]

CARRELAGE = dict(taille=60, joint=0.3, couleur="#D9D2C6", nuance="#CFC7B9", couleur_joint="#BDB5A7",
                 nom="grès cérame 60 × 60 effet pierre claire, comme le salon")
MUR_COULEUR = "#EFE9DC"

RENDUS = [("iso_so", "Isométrique depuis le sud-ouest : banc sous le tableau, meuble à chaussures, miroir"),
          ("iso_no", "Isométrique depuis le nord-ouest : penderie, angle arrondi, meuble à chaussures, porte d'entrée")]

CHANGEMENTS = [
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
