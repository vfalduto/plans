# Meuble linge de la salle de bain, variante 2 : caisson en mélaminé blanc 18 à deux tiroirs (haut, bas), un trou en
# façade de chaque tiroir pour jeter le linge sans ouvrir.
#
# Module du document de confrontation (variantes.py → sdb-meuble-variantes.html) : il ne touche pas au meuble actuel.
# Il reprend de modele.py l'alcôve, la machine, le plan de travail, les tuyaux et l'échelle sud (qui porte le plan côté
# mur sud, au-delà de la machine) ; il décrit le reste pièce par pièce, comme modele.py (Bloc, cotes en cm).
#
# Principe : un caisson (deux côtés, fond, dos, deux traverses) debout sur quatre vérins, à gauche de la machine, porte le
# plan côté nord à la place des échelles nord et du milieu. Dedans, deux tiroirs sur coulisses à billes à sortie totale
# de 500. Chaque tiroir est une caisse (façade en applique, deux côtés, dos, fond) ; un sac en toile y pend entre deux
# barres rondes posées dans des entailles en U en haut des côtés, comme les sacs du meuble actuel. Le trou de la façade
# (stade 30 × 10) est juste au-dessus de la barre avant : le linge passe par-dessus et tombe dans le sac. Le trou sert
# aussi de poignée. Pour vider : on tire le tiroir à fond, on soulève les deux barres, le sac vient avec.
#
# Hypothèses marquées « estimé » : masses volumiques (de mémoire), masse du linge, épaisseur du vantail de la porte
# d'entrée, prix non relevés.

import math
import os
import sys
from html import escape

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import modele as M  # noqa: E402
import plan as PL  # noqa: E402
import cotes as CO  # noqa: E402
import montage as MO  # noqa: E402

ID = "tiroirs"
TITRE = "Variante 2 : caisson à deux tiroirs, trou en façade"
RESUME = ("Un caisson en mélaminé blanc à gauche de la machine, deux tiroirs superposés sur coulisses à sortie totale ; "
          "on jette le linge par un trou en façade de chaque tiroir, il tombe dans un sac en toile pendu à deux barres, "
          "qu'on soulève pour vider.")

cm, f = PL.cm, PL.f
T = M.T                                     # tablette mélaminée 18

# ------------------------------------------------------------------ caisson
# Le caisson occupe la place du bac actuel : de 0,3 du mur nord à l'échelle du milieu (CB), du nu des façades + 18 au dos
# de la machine (XO1). Fond SOUS les côtés (les côtés y sont posés : la charge passe en compression, pas dans les vis) ;
# dos entre les côtés, sur le fond ; deux traverses de 10 en haut, entre les côtés, à fleur : le plan repose sur leur
# chant et sur celui des côtés, vissé par-dessous à travers les traverses.
CX0, CX1 = M.FACE + T, M.XO1                # 175,8 → 229 (le caisson est derrière les façades en applique)
CY0, CY1 = M.CB["y0"], M.CB["y1"]           # 0,3 → 50,2
Z0 = M.Z0                                   # dessous du fond : 2 (vérins, comme le meuble actuel)
ZF = Z0 + T                                 # dessus du fond : 3,8
ZP = M.Z_PLAN                               # dessous du plan : 85,5
TRAV = 10                                   # largeur des traverses
IY0, IY1 = CY0 + T, CY1 - T                 # intérieur du caisson : 2,1 → 48,4
IX1 = CX1 - T                               # face avant du dos : 227,2

PIECES = []


def P(role, nom, x0, x1, y0, y1, z0, z1, groupe="caisson", rep=""):
    b = M.Bloc(role, nom, x0, x1, y0, y1, z0, z1, rep=rep, groupe=groupe)
    PIECES.append(b)
    return b


COTE_N = P("caisson", "c_cote_n", CX0, CX1, CY0, IY0, ZF, ZP, rep="T1")
COTE_S = P("caisson", "c_cote_s", CX0, CX1, IY1, CY1, ZF, ZP, rep="T1")
FOND = P("caisson", "c_fond", CX0, CX1, CY0, CY1, Z0, ZF, rep="T2")
DOS = P("caisson", "c_dos", IX1, CX1, IY0, IY1, ZF, ZP, rep="T3")
TRAV_AV = P("caisson", "c_traverse_av", CX0, CX0 + TRAV, IY0, IY1, ZP - T, ZP, rep="T4")
TRAV_AR = P("caisson", "c_traverse_ar", IX1 - TRAV, IX1, IY0, IY1, ZP - T, ZP, rep="T4")

# vérins sous le fond : les mêmes que ceux du meuble actuel (Hettich M8 × 30), vissés dans un écrou à griffes M8 frappé
# par-dessus dans le fond ; le bout de la tige dépasse au plus de TIGE au-dessus du fond, sous le tiroir du bas
SEMELLE = M.PIED["semelle"]
TIGE = 1.0                                  # dépassement maxi de la tige au-dessus du fond (estimé : tige 30, fond 18)
VERINS_XY = [(x, y) for x in (CX0 + 3, CX1 - 3) for y in (CY0 + 3, CY1 - 3)]
for k, (x, y) in enumerate(VERINS_XY):
    P("pied", f"c_verin_{k}", x - SEMELLE / 2, x + SEMELLE / 2, y - SEMELLE / 2, y + SEMELLE / 2, 0, Z0)

# ------------------------------------------------------------------ coulisses et tiroirs
# Coulisses à billes, montage latéral, 12,7 d'épaisseur, 45 de haut, 500 de long, sortie totale : la caisse fait la
# largeur intérieure du caisson moins deux coulisses (règle des fabricants, de mémoire, à vérifier sur la notice).
COUL = dict(ep=1.27, h=4.5, L=50.0, course=50.0, charge=30,
            nom="paire de coulisses à billes, montage latéral, H 45, sortie totale, 500 mm")
BY0, BY1 = IY0 + COUL["ep"], IY1 - COUL["ep"]   # caisse : 3,37 → 47,13
BIY0, BIY1 = BY0 + T, BY1 - T                   # intérieur de la caisse : 5,17 → 45,33
BX0, BX1 = CX0, CX0 + COUL["L"]                 # caisse derrière la façade : 175,8 → 225,8
assert IX1 - BX1 >= 0.3, "la caisse fermée s'arrête devant le dos du caisson"
assert CX1 - CX0 - T >= COUL["L"] + 0.3, "profondeur intérieure suffisante pour des coulisses de 500"

# façades en applique : comme la porte du bac actuel, de 0,3 devant le chambranle de la porte d'entrée (qui déborde du
# mur nord) jusqu'à 0,15 du bord sud du caisson ; 0,3 sous le plan, 0,3 entre les deux, 0,3 au-dessus du dessous du fond
FY0, FY1 = M.Y0 + M.CHAMBRANLE + 0.3, CY1 - 0.15
JEU_F = 0.3
_hf = (ZP - JEU_F - (Z0 + JEU_F) - JEU_F) / 2
FZ = dict(bas=(Z0 + JEU_F, Z0 + JEU_F + _hf), haut=(ZP - JEU_F - _hf, ZP - JEU_F))   # 2,3 → 43,6 et 43,9 → 85,2

# trou en stade (deux demi-cercles Ø 10 à la scie cloche, deux traits de scie sauteuse) au milieu de la largeur, son
# haut à TROU["haut"] sous le haut de la façade : on y passe la main pour tirer le tiroir
TROU = dict(l=30.0, h=10.0, haut=2.5)
TY = (FY0 + FY1) / 2
TROU["y"] = (TY - TROU["l"] / 2, TY + TROU["l"] / 2)
assert TROU["y"][0] > BIY0 + 3 and TROU["y"][1] < BIY1 - 3, "le trou tombe entre les côtés de la caisse"

BARRE = dict(d=2.2, entaille=2.5, dessus=2.0, av=2.0, ar=1.6)   # Ø, largeur de l'entaille, côté au-dessus de la barre,
# axe de la barre avant derrière la façade, axe de la barre arrière devant le dos de la caisse
FOND_T = 1.2                                # tiroir du bas : jeu entre le fond du caisson et le dessous de la caisse
assert FOND_T > TIGE + 0.1, "les tiges des vérins ne touchent pas la caisse du bas"

TIROIRS = {}


def tiroir(nom, fz, z_fond):
    """Caisse d'un tiroir : façade (fz), fond dont le dessous est à z_fond, côtés et dos jusqu'à DESSUS au-dessus des
    barres ; barres et sac. Tout dans le groupe du tiroir (décalé d'un bloc quand on l'ouvre)."""
    g = f"tiroir_{nom}"
    t_haut = fz[1] - TROU["haut"]
    t_bas = t_haut - TROU["h"]
    zb = t_bas - 0.3 - BARRE["d"] / 2                # axe des barres : leur dessus 3 mm sous le trou
    zc1 = zb + BARRE["d"] / 2 + BARRE["dessus"]      # haut des côtés et du dos
    zc0 = z_fond + T
    d = dict(nom=nom, groupe=g, fz=fz, trou=(t_bas, t_haut), zb=zb, z_fond=z_fond, zc=(zc0, zc1))
    d["facade"] = P("facade", f"t_{nom}_facade", M.FACE, CX0, FY0, FY1, fz[0], fz[1], groupe=g, rep="T5")
    d["fond"] = P("caisse", f"t_{nom}_fond", BX0, BX1, BY0, BY1, z_fond, zc0, groupe=g, rep="T6")
    d["cotes"] = [P("caisse", f"t_{nom}_cote_{k}", BX0, BX1, y0, y1, zc0, zc1, groupe=g, rep="T7")
                  for k, (y0, y1) in (("n", (BY0, BIY0)), ("s", (BIY1, BY1)))]
    d["dos"] = P("caisse", f"t_{nom}_dos", BX1 - T, BX1, BIY0, BIY1, zc0, zc1, groupe=g, rep="T8")
    xa, xr = BX0 + BARRE["av"], BX1 - T - BARRE["ar"]
    r = BARRE["d"] / 2
    d["barres"] = (xa, xr)
    # barres : dessinées entre les côtés ; réelles, elles entrent de 1,5 dans les entailles (longueur BARRE["L"])
    d["barre"] = [M.Profil("barre", f"t_{nom}_barre_{k}", M.rond(x, zb, r), BIY0, BIY1, groupe=g)
                  for k, x in (("av", xa), ("ar", xr))]
    PIECES.extend(d["barre"])
    # sac (pas à découper) : pendu sous les barres, le fond posé sur celui de la caisse
    d["sac"] = M.Bloc("sac", f"t_{nom}_sac", xa + r, xr - r, BIY0 + 0.5, BIY1 - 0.5, zc0 + 0.3, zb - r, groupe=g)
    # coulisses (partie fixe vissée au caisson), en bas des côtés de la caisse
    zs = zc0 + 1.0
    d["coulisses"] = [P("pied", f"t_{nom}_coulisse_{k}", BX0 + 0.3, BX1, y0, y0 + COUL["ep"], zs, zs + COUL["h"])
                      for k, y0 in (("n", IY0), ("s", BY1))]
    assert zs + COUL["h"] < zc1, "la coulisse tient sur le côté de la caisse"
    assert t_bas > zc0 + 15, "le trou est au-dessus du sac"
    d["sac_h"] = d["sac"].z1 - d["sac"].z0
    d["volume"] = (d["sac"].x1 - d["sac"].x0) * (d["sac"].y1 - d["sac"].y0) * d["sac_h"] / 1000
    TIROIRS[nom] = d
    return d


BAS = tiroir("bas", FZ["bas"], ZF + FOND_T)
# la caisse du haut descend jusqu'au bas de sa façade : au-dessus du trou du bas, pour que le linge entassé dans le
# tiroir du bas ne frotte pas dessous
HAUT = tiroir("haut", FZ["haut"], FZ["haut"][0])
BARRE["L"] = BIY1 - BIY0 + 2 * 1.5
assert HAUT["z_fond"] - BAS["trou"][1] >= 2.5, "le dessous de la caisse du haut passe au-dessus du trou du bas"
assert HAUT["zc"][1] < TRAV_AV.z0 - 1, "la caisse du haut passe sous les traverses"
assert BAS["zc"][1] < HAUT["z_fond"], "les deux caisses ne se touchent pas"
SACS = [BAS["sac"], HAUT["sac"]]

# ------------------------------------------------------------------ ce qui ne change pas (repris de modele.py)
_pm = {b.nom: b for b in M.PIECES}
PLAN = _pm["plan_travail"]
ECH_SUD = [b for b in M.PIECES if b.groupe == "ossature" and b.nom.endswith("_s") and b.role != "vis"]
assert ECH_SUD and all(b.y0 >= M.ECH["s"] - 1e-6 for b in ECH_SUD), "échelle sud seule"
COMMUN = [PLAN] + ECH_SUD + [M.MACHINE, M.SIPHON, M.ARRIVEE]


def blocs(ouvert=(), sacs=True):
    """Pièces de la variante, tiroirs de ouvert tirés à fond (course de la coulisse)."""
    r = []
    for b in PIECES + (SACS if sacs else []):
        if b.groupe.startswith("tiroir_") and b.groupe[7:] in ouvert:
            b = decale(b, -COUL["course"])
        r.append(b)
    return r + COMMUN


def decale(b, dx):
    if isinstance(b, M.Profil):
        return M.replace(b, xz=[(x + dx, z) for x, z in b.xz])
    return M.replace(b, x0=b.x0 + dx, x1=b.x1 + dx)


# ------------------------------------------------------------------ contrôles géométriques
def _chevauche(a, b, e=1e-6):
    return (a.x0 < b.x1 - e and b.x0 < a.x1 - e and a.y0 < b.y1 - e and b.y0 < a.y1 - e and a.z0 < b.z1 - e
            and b.z0 < a.z1 - e)


for ouv in ((), ("bas",), ("haut",), ("bas", "haut")):
    bl = blocs(ouv)
    neufs = [b for b in bl if b not in COMMUN]
    for i, a in enumerate(neufs):
        assert M.Y0 <= a.y0 and a.y1 <= M.Y1 and a.x1 <= M.X1 and a.z0 >= 0, ("dans l'alcôve", a.nom)
        for b in neufs[i + 1:] + COMMUN:
            if a.role == "sac" or b.role == "sac":
                continue
            assert not _chevauche(a, b), (ouv, a.nom, b.nom)
assert abs(BY0 - IY0 - COUL["ep"]) < 1e-9 and abs(IY1 - BY1 - COUL["ep"]) < 1e-9
assert M.MACHINE.y0 - CY1 >= 0.5, "0,6 entre le caisson et la machine, comme aujourd'hui"
assert FY1 < M.MACHINE.y0, "la façade ne passe pas devant la machine"
# vider le tiroir du bas : ouvert, la barre arrière doit sortir devant la façade du haut (on soulève le sac tout droit)
_xr_ouv = BAS["barres"][1] - COUL["course"] + BARRE["d"] / 2
JEU_SORTIE = M.FACE - _xr_ouv
assert JEU_SORTIE >= 0.3, "tiroir ouvert : la barre arrière passe devant la façade fermée du dessus et le plan"

# ------------------------------------------------------------------ porte d'entrée
# Vantail de 73 aux gonds à x = PORTE["x1"], ouvrant vers la salle de bain ; grand ouvert, il longe l'alcôve.
EP_VANTAIL = 4.0                            # estimé
GOND = (M.PORTE["x1"], M.Y0)
DEVANT = M.FACE - GOND[0]                   # tiroir tiré de plus de tant : il entre dans le débattement du vantail
assert DEVANT < COUL["course"]
_coin = (M.FACE - COUL["course"], FY0)      # coin nord-ouest de la façade d'un tiroir tiré à fond
ANGLE_PORTE = math.degrees(math.atan2(_coin[1] - GOND[1], GOND[0] - _coin[0]))   # le vantail s'y arrête
assert math.hypot(GOND[0] - _coin[0], _coin[1] - GOND[1]) < M.PORTE["l"]

# ------------------------------------------------------------------ efforts (estimations)
RHO = dict(mel=650, chene=700, sapin=450)   # kg/m³, de mémoire (comme modele.py pour le mélaminé)
LINGE = 5.0                                 # kg de linge sale dans un sac plein (estimé)
G = 9.81


def masse(b, rho):
    v = (b.x1 - b.x0) * (b.y1 - b.y0) * (b.z1 - b.z0)
    if isinstance(b, M.Profil):
        v *= 0.5 if b.role != "barre" else math.pi / 4
    return v * rho / 1e6


def _m_tiroir(d):
    return sum(masse(b, RHO["mel"]) for b in [d["facade"], d["fond"], d["dos"]] + d["cotes"])


EFFORT = {}
EFFORT["tiroir"] = {k: _m_tiroir(d) for k, d in TIROIRS.items()}
EFFORT["caisson"] = sum(masse(b, RHO["mel"]) for b in (COTE_N, COTE_S, FOND, DOS, TRAV_AV, TRAV_AR))
EFFORT["plan"] = masse(PLAN, RHO["chene"])
EFFORT["echelle"] = sum(masse(b, RHO["sapin"]) for b in ECH_SUD if b.role == "bois")
# par coulisse : tiroir du haut plein
EFFORT["coulisse"] = (EFFORT["tiroir"]["haut"] + LINGE) / 2
assert EFFORT["coulisse"] * 2 < COUL["charge"], "sous la charge de la paire de coulisses"
# effort pour tirer : roulement à billes, coefficient ≈ 0,01 (de mémoire) ; plus le cran de fermeture
EFFORT["tirer"] = (EFFORT["tiroir"]["haut"] + LINGE) * G * 0.01
EFFORT["barre"] = LINGE * G / 2             # par barre, sac plein
# basculement vers l'avant, tiroir du haut tiré à fond et plein : le meuble (caisson, tiroirs, plan, échelle sud, vissés
# ensemble) pivote sur l'arête avant des semelles des vérins avant (caisson et échelle sud presque alignés) ; on cherche
# l'appui vertical au bord de la façade ouverte qui le fait basculer. La machine n'est pas liée au meuble : elle ne
# retient rien.
PIVOT = min(CX0 + 3, M.XO0 + M.DL / 2) - SEMELLE / 2


def _moment(ouvert):
    m = 0
    for b in blocs(ouvert, sacs=False):
        if b in (M.MACHINE, M.SIPHON, M.ARRIVEE) or b.role in ("pied", "barre"):
            continue
        rho = RHO["chene"] if b is PLAN else RHO["sapin"] if b.role == "bois" else RHO["mel"]
        m += masse(b, rho) * ((b.x0 + b.x1) / 2 - PIVOT)
    for d in TIROIRS.values():                   # linge, centré dans le sac
        dx = -COUL["course"] if d["nom"] in ouvert else 0
        m += LINGE * ((d["sac"].x0 + d["sac"].x1) / 2 + dx - PIVOT)
    return m                                     # kg·cm, positif : retient


EFFORT["retient"] = _moment(("haut",))
assert EFFORT["retient"] > 0, "tiroir plein tiré à fond : le meuble tient seul"
EFFORT["appui"] = EFFORT["retient"] / (PIVOT - (M.FACE - COUL["course"]))   # kg posés au bord de la façade ouverte
EFFORT["appui_deux"] = _moment(("haut", "bas")) / (PIVOT - (M.FACE - COUL["course"]))

# ------------------------------------------------------------------ sacs (deux, cousus dans la toile du meuble actuel)
COUTURE, OURLET, FOURREAU = M.COUTURE, M.OURLET, M.FOURREAU


def _patron(d):
    s = d["sac"]
    w, fd, h = s.y1 - s.y0, s.x1 - s.x0 + BARRE["d"], d["sac_h"] + 3
    return dict(bande=(w + 2 * COUTURE, 2 * h + fd + 2 * FOURREAU), soufflet=(fd + 2 * COUTURE, h + COUTURE + OURLET))


PATRONS = {k: _patron(d) for k, d in TIROIRS.items()}
# deux bandes côte à côte, les quatre soufflets en une colonne à côté
_lz = sum(p["bande"][0] for p in PATRONS.values()) + max(p["soufflet"][0] for p in PATRONS.values())
assert _lz <= M.TOILE["laize"], _lz
TOILE_M = math.ceil(max(max(p["bande"][1] for p in PATRONS.values()),
                        sum(2 * p["soufflet"][1] for p in PATRONS.values())) / 10 - 1e-9) / 10

# ------------------------------------------------------------------ achats (meuble à linge seul)
# Les tablettes : 2 de 600 et 1 de 500 suffisent (côtés, fond et traverses dans une 600 ; dos, deux fonds de caisse et
# une façade dans une 500 ; une façade, les quatre côtés et les deux dos de caisse dans une 600).
_t = {t["l"]: t for t in M.TABLETTES_18}
_W = M.WELDOM
NB_DIREKTA = 4 * 2 + 3 * 2 + 3 + 2 * 4      # côtés sur le fond, dos aux côtés et au fond, traverses
QUINC = [
    ("Tablette mélaminée blanche 250 × 60 × 18", 2, f"Weldom réf. {_t[600]['ref']}", _t[600]["prix"], True),
    ("Tablette mélaminée blanche 250 × 50 × 18", 1, f"Weldom réf. {_t[500]['ref']}", _t[500]["prix"], True),
    (COUL["nom"] + f", {COUL['charge']} kg et plus", 2, "Leroy Merlin (série 250 → 700, la 600 à 13,90 €), ou "
     "Mr Bricolage (Cime) ; pas trouvée en ligne au Weldom", 13.00, False),
    ("Lot de 2 vérins Hettich M8 × 30 (comme le meuble actuel)", 2, f"Weldom réf. {_W['verin'][4]}", _W["verin"][1], True),
    ("Écrou à griffes M8 (à frapper), lot de 4", 1, "Weldom ou Leroy Merlin", 3.00, False),
    ("Vis Direkta 6,3 × 50 (assemblage du caisson), boîte", 1, "Weldom", 8.00, False),
    ("Lot de 6 équerres 50 × 50 × 35 (façade ↔ côtés de caisse, 4 par tiroir)", 2, f"Weldom réf. "
     f"{_W['equerre_a'][4]}", _W["equerre_a"][1], True),
    ("Boîte de vis 4 × 40 (fonds et dos des caisses)", 1, f"Weldom réf. {_W['vis40'][4]}", _W["vis40"][1], True),
    ("Lot de vis 4 × 16 (coulisses, équerres)", 1, f"Weldom réf. {_W['vis16'][4]}", _W["vis16"][1], True),
    ("Vis 4 × 30 (plan vissé par-dessous à travers les traverses), petite boîte", 1, "Weldom", 5.00, False),
    ("Bande de chant thermocollante blanche 23 mm, rouleau de 5 m", 2, f"Weldom réf. {_W['chant'][4]}",
     _W["chant"][1], True),
    (f"Rond de bois Ø {BARRE['d'] * 10:.0f} × 1 m (4 barres de {cm(BARRE['L'])})", 2, "Weldom ou Leroy Merlin", 4.50,
     False),
    (f"{cm(TOILE_M)} m de toile de transat, laize 150 (deux sacs)", 1, M.TOILE["magasin"],
     round(TOILE_M * M.TOILE["prix_m"], 2), True),
]
COUT = round(sum(q * p for _, q, _, p, _ in QUINC), 2)
COUT_RELEVE = round(sum(q * p for _, q, _, p, r in QUINC if r), 2)
N_PIECES = sum(1 for b in PIECES if b.rep) + 2 * len(TIROIRS)     # panneaux + 4 barres


# ------------------------------------------------------------------ dessins
def _stade(y0, y1, z0, z1, v=lambda z: -z, n=10):
    """Contour du trou en stade dans la vue de face (u = y, v = −z)."""
    r = (z1 - z0) / 2
    zc = (z0 + z1) / 2
    pts = [(y1 - r + r * math.cos(math.pi / 2 - math.pi * k / n), zc + r * math.sin(math.pi / 2 - math.pi * k / n))
           for k in range(n + 1)]
    pts += [(y0 + r + r * math.cos(-math.pi / 2 - math.pi * k / n), zc + r * math.sin(-math.pi / 2 - math.pi * k / n))
            for k in range(n + 1)]
    return [(u, v(z)) for u, z in pts]


def _sans_trou(bl, s=None):
    """Pour une coupe à y = s : la façade coupée dans le trou est remplacée par ses deux morceaux, sous et sur le trou."""
    r = []
    for b in bl:
        d = TIROIRS.get(b.nom[2:-7]) if b.role == "facade" and b.nom.startswith("t_") else None
        if d and s is not None and TROU["y"][0] < s < TROU["y"][1]:
            r += [M.replace(b, z1=d["trou"][0]), M.replace(b, z0=d["trou"][1])]
        else:
            r.append(b)
    return r


def iso(ouvert=(), titre=""):
    bl = blocs(ouvert)
    neuves = {b.nom for b in bl if b.groupe.startswith("tiroir_")}

    def trous(xs, ys):
        o = []
        for k, d in TIROIRS.items():
            if k not in ouvert and "haut" in ouvert and k == "bas":
                continue                          # caché par le tiroir du haut tiré
            x = M.FACE - (COUL["course"] if k in ouvert else 0) - 0.05
            pts = [MO.proj(x, u, -w) for u, w in _stade(*TROU["y"], *d["trou"])]
            o.append(f'<polygon class="ihole" style="fill:var(--ink);fill-opacity:.6" points="{MO.pts_svg(pts)}"/>')
        return o
    return MO.dessin(bl, neuves, reperes=False, extra=trous, titre=titre)


def vue_dessus():
    """Plan de l'alcôve, coupé à 60 du sol (dans le tiroir du haut) : caisson, tiroirs, machine, échelle sud ; tiroir du
    haut tiré en tireté ; porte d'entrée et son débattement."""
    zs = 60
    xg = M.FACE - COUL["course"] - 22
    o = [PL.rect(GOND[0], M.Y0 - 4, M.X1 + 4, M.Y0, "omurc"), PL.rect(M.PORTE["x0"] - 8, M.Y0 - 4, M.PORTE["x0"], M.Y0,
                                                                       "omurc"),
         PL.rect(M.X1 - M.ALCOVE["sud"], M.Y1, M.X1 + 4, M.Y1 + 4, "omurc"), PL.rect(M.X1, M.Y0, M.X1 + 4, M.Y1, "omurc")]
    o += CO.projeter([b for b in blocs() if b.role != "barre"], "dessus", zs)
    o.append(PL.poly([(PLAN.x0, PLAN.y0), (PLAN.x1, PLAN.y0), (PLAN.x1, PLAN.y1), (PLAN.x0, PLAN.y1)], "oplanl"))
    # tiroir du haut tiré à fond
    dx = -COUL["course"]
    for b in (HAUT["facade"], HAUT["fond"]):
        o.append(PL.poly([(b.x0 + dx, b.y0), (b.x1 + dx, b.y0), (b.x1 + dx, b.y1), (b.x0 + dx, b.y1)], "oswing"))
    # porte d'entrée : vantail grand ouvert (90°), arc du bord libre, vantail arrêté par un tiroir tiré
    gx, gy = GOND
    L = M.PORTE["l"]
    o.append(PL.rect(gx - EP_VANTAIL, gy, gx, gy + L, "ocache"))
    arc = " ".join(f"{f(gx - L * math.cos(math.radians(a)))},{f(gy + L * math.sin(math.radians(a)))}"
                   for a in range(0, 91, 3))
    o.append(f'<polyline points="{arc}" style="fill:none;stroke:var(--muted);stroke-width:.25;stroke-dasharray:1.2 .8"/>')
    a = math.radians(ANGLE_PORTE)
    o.append(f'<line x1="{f(gx)}" y1="{f(gy)}" x2="{f(gx - L * math.cos(a))}" y2="{f(gy + L * math.sin(a))}" '
             'style="stroke:var(--tri);stroke-width:.6"/>')
    o.append(f'<circle class="oaxe" cx="{f(gx)}" cy="{f(gy)}" r=".8"/>')
    o.append(PL.text(gx - 2, gy + L + 4, "porte d'entrée grand ouverte", "lt muted", "end"))
    o.append(PL.text(gx - L + 2, gy - 5.5, f"porte d'entrée ({L}), gonds à {M.GONDS} du fond", "lt muted", "start"))
    o.append(CO.etiquette(gx - 30, gy + 30 * math.tan(a) + 0.4, gx - 44, gy + 14,
                          f"un tiroir tiré l'arrête à {ANGLE_PORTE:.0f}°", "end"))
    # cotes
    o.append(CO.chaine_v([M.Y0, CY0, CY1, M.MACHINE.y0, M.MACHINE.y1, M.ECH["s"], M.ECH["s"] + M.DE, M.Y1], M.X1 + 9,
                         ext=M.X1))
    o.append(CO.cote_v(M.Y0, M.Y1, M.X1 + 17, cm(M.Y1 - M.Y0)))
    o.append(CO.chaine_h([M.FACE, CX0, BX1, CX1, M.X1], M.Y1 + 9, ext=M.Y1))
    o.append(CO.cote_h(M.FACE, M.X1, M.Y1 + 16, f"{cm(M.PROF)} profondeur"))
    o.append(CO.cote_h(M.FACE - COUL["course"], M.FACE, FY1 + 6, f"{cm(COUL['course'])} tiré à fond", ext=FY1))
    o.append(CO.cote_h(gx, M.FACE, -9, cm(DEVANT), ext=-4))
    o.append(PL.text((CX0 + IX1) / 2, (BY0 + BY1) / 2 + 1, "sac", "lt muted"))
    o.append(PL.text((M.MACHINE.x0 + M.MACHINE.x1) / 2, (M.MACHINE.y0 + M.MACHINE.y1) / 2 + 1, "machine", "lt"))
    o.append(PL.text((M.FACE - COUL["course"] + M.FACE) / 2, (FY0 + FY1) / 2 + 9, "tiroir tiré", "lt", "middle"))
    o.append(PL.text(M.XO0 + 1, M.ECH["s"] - 1.2, "échelle sud", "lt muted", "start"))
    o.append(PL.text(M.X1 - 1, M.Y0 - 5.5, "mur nord", "lt muted", "end"))
    o.append(PL.text(M.X1 - M.ALCOVE["sud"] - 1, M.Y1 + 3.4, "mur sud", "lt muted", "end"))
    return CO.svg(xg - 14, M.Y0 - 14, M.X1 + 26, M.Y1 + 21, o, "Vue de dessus de l'alcôve")


def vue_face():
    h = M.Z_DESSUS + 8
    o = [PL.rect(M.Y0, -h, M.Y1, 0, "omur"), PL.rect(M.Y0 - 4, -h, M.Y0, 0, "omurc"),
         PL.rect(M.Y1, -h, M.Y1 + 4, 0, "omurc"),
         f'<line class="osol" x1="{f(M.Y0 - 6)}" y1="0" x2="{f(M.Y1 + 6)}" y2="0"/>']
    o += CO.projeter([b for b in blocs() if b.role != "sac"], "face")
    o.append(CO.hublot(M.MACHINE, "face"))
    for d in TIROIRS.values():
        o.append(PL.poly(_stade(*TROU["y"], *d["trou"]), "otrou"))
        fz = d["fz"]
        o.append(PL.text(TY, -(fz[0] + 9), f"tiroir du {d['nom']}", "lt"))
    o.append(PL.text((M.MACHINE.y0 + M.MACHINE.y1) / 2, -(M.Z_PLAN - 12), "machine", "lt"))
    o.append(PL.text(M.CENTRE, -M.Z_PLAN - 0.35, "plan (inchangé)", "lt muted"))
    o.append(CO.chaine_h([M.Y0, FY0, TROU["y"][0], TROU["y"][1], FY1, M.MACHINE.y0, M.MACHINE.y1, M.Y1], 6, ext=0))
    o.append(CO.cote_h(M.Y0, M.Y1, 13, f"{cm(M.Y1 - M.Y0)} entre les murs"))
    nv = [(Z0, f"{cm(Z0)} caisson", CY0)]
    for d in (BAS, HAUT):
        nv += [(d["fz"][0], f"{cm(d['fz'][0])} façade du {d['nom']}", FY0),
               (d["trou"][0], f"{cm(d['trou'][0])} bas du trou", TROU["y"][0]),
               (d["trou"][1], f"{cm(d['trou'][1])} haut du trou", TROU["y"][0])]
    nv += [(HAUT["fz"][1], f"{cm(HAUT['fz'][1])} haut de la façade", FY0),
           (M.Z_DESSUS, f"{cm(M.Z_DESSUS)} dessus du plan", M.Y0)]
    o.append(CO.niveaux(nv, M.Y0 - 9))
    o.append(CO.niveaux([(BAS["fz"][1], f"{cm(BAS['fz'][1])} façade du bas", FY1),
                         (M.LL["h"], f"{cm(M.LL['h'])} machine", M.MACHINE.y1)], M.Y1 + 9, droite=True))
    return CO.svg(M.Y0 - 52, -h - 6, M.Y1 + 50, 17, o, "Vue de face")


def coupe_tiroirs():
    """Coupe par le milieu des tiroirs (y au milieu du trou), vue vers le nord ; tiroir du haut tiré en tireté."""
    s = TY
    h = M.Z_DESSUS + 8
    xg = M.FACE - COUL["course"]
    o = [PL.rect(M.X1, -h, M.X1 + 4, 0, "omurc"),
         f'<line class="osol" x1="{f(xg - 6)}" y1="0" x2="{f(M.X1 + 4)}" y2="0"/>']
    o += CO.projeter(_sans_trou(blocs(), s), "cote", s)
    dx = -COUL["course"]
    for b in _sans_trou([HAUT["facade"], HAUT["fond"], HAUT["dos"], HAUT["cotes"][0]], s):
        o.append(PL.poly([(x + dx, -z) for x, z in b.pts("y")], "oswing"))
    for x in HAUT["barres"]:
        o.append(f'<circle class="oswing" cx="{f(x + dx)}" cy="{f(-HAUT["zb"])}" r="{f(BARRE["d"] / 2)}"/>')
    o.append(CO.chaine_h([M.FACE, CX0, BX1, CX1, M.X1], 6, ext=0))
    o.append(CO.cote_h(xg, M.FACE, 13, f"{cm(COUL['course'])} course (sortie totale)", ext=0))
    xa, xr = BAS["barres"]
    o.append(CO.cote_h(xa, xr, -BAS["zb"] + 6, f"{cm(xr - xa)} entre barres", ext=-BAS["zb"]))
    o.append(CO.etiquette(xr + dx, -HAUT["zb"] - BARRE["d"] / 2, xr + dx - 6, -HAUT["zb"] - 8,
                          f"barre arrière, tiroir tiré : {cm(JEU_SORTIE * 10)} mm devant le plan", "end"))
    o.append(CO.etiquette(M.FACE, -(HAUT["trou"][0] + HAUT["trou"][1]) / 2, M.FACE + 12, -HAUT["fz"][1] - 4,
                          "trou (poignée)"))
    o.append(PL.text((CX0 + IX1) / 2, -(BAS["sac"].z0 + BAS["sac"].z1) / 2, "sac (coupé)", "lt"))
    o.append(PL.text((CX0 + IX1) / 2, -(HAUT["sac"].z0 + HAUT["sac"].z1) / 2, "sac (coupé)", "lt"))
    nv = [(Z0, f"{cm(Z0)} vérins", xg)]
    for d in (BAS, HAUT):
        nv += [(d["z_fond"], f"{cm(d['z_fond'])} dessous de la caisse", CX0), (d["zb"], f"{cm(d['zb'])} axe des barres", CX0),
               (d["zc"][1], f"{cm(d['zc'][1])} haut des côtés", CX0)]
    nv += [(M.Z_PLAN, f"{cm(M.Z_PLAN)} dessous du plan", xg), (M.Z_DESSUS, f"{cm(M.Z_DESSUS)} dessus", xg)]
    o.append(CO.niveaux(nv, xg - 8))
    o.append(PL.text(M.X1 - 1, -h - 1.4, "mur du fond", "lt muted", "end"))
    return CO.svg(xg - 58, -h - 8, M.X1 + 8, 17, o, "Coupe par les tiroirs")


def coupe_coulisses():
    """Coupe transversale au milieu de la profondeur (x = 200), vue vers le mur du fond : coulisses, caisses, barres."""
    xs = (BX0 + BX1) / 2
    vus, cut = [], []
    for b in _sans_trou(blocs()):
        if b.x1 <= xs or b in COMMUN[1:] and b.y0 > CY1 + 1:
            continue
        (cut if b.x0 < xs else vus).append(b)
    o = [PL.rect(M.Y0 - 4, -(M.Z_PLAN + 6), M.Y0, 0, "omurc"),
         f'<line class="osol" x1="{f(M.Y0 - 6)}" y1="0" x2="{f(M.MACHINE.y0 + 10)}" y2="0"/>']
    for b in sorted(vus, key=lambda b: -b.x0):
        o.append(PL.poly(CO.contour(b, "face"), CO.CLS.get(b.role, "omel")))
    for b in cut:
        cls = CO.CLS.get(b.role, "omel") + " cut"
        if b.role == "caisse":
            cls = "omel cut"
        o.append(PL.poly(CO.contour(b, "face"), cls))
    o.append(CO.cote_h(BIY0, BIY1, 6, f"{cm(BIY1 - BIY0)} dans la caisse", ext=-(BAS["z_fond"])))
    o.append(CO.cote_h(BY0, BY1, 12, f"{cm(BY1 - BY0)} caisse", ext=-(BAS["z_fond"])))
    o.append(CO.cote_h(IY0, IY1, 18, f"{cm(IY1 - IY0)} entre les côtés du caisson", ext=-ZF))
    d = HAUT
    co = d["coulisses"][0]
    o.append(CO.etiquette(co.y1, -(co.z0 + co.z1) / 2, co.y1 + 9, -(co.z0 + co.z1) / 2 + 6,
                          f"coulisse {cm(COUL['ep'] * 10)} mm"))
    o.append(CO.etiquette((BIY0 + BIY1) / 2, -d["zb"], BIY0 + 1, -(d["zc"][1] + 4),
                          f"barre arrière Ø {BARRE['d'] * 10:.0f}"))
    nv = []
    for d in (BAS, HAUT):
        nv += [(d["z_fond"], f"{cm(d['z_fond'])} caisse", BY0), (d["coulisses"][0].z0, f"{cm(d['coulisses'][0].z0)} coulisse", IY0),
               (d["zc"][1], f"{cm(d['zc'][1])} haut des côtés", BY0)]
    nv += [(ZF, f"{cm(ZF)} dessus du fond", CY0), (M.Z_PLAN, f"{cm(M.Z_PLAN)} plan", CY0)]
    o.append(CO.niveaux(nv, CY0 - 8))
    o.append(PL.text((CY0 + CY1) / 2, -M.Z_PLAN - 3, "vue vers le mur du fond", "lt muted"))
    o.append(PL.text(M.MACHINE.y0 + 1, -40, "machine", "lt muted", "start"))
    return CO.svg(CY0 - 40, -(M.Z_PLAN + 8), M.MACHINE.y0 + 12, 23, o, "Coupe transversale").replace(
        '<svg class="cotes"', '<svg class="cotes" style="max-width:620px;min-width:0;margin:0 auto"', 1)


# ------------------------------------------------------------------ fiche (comparatif)
FICHE = dict(
    mettre=["porte d'entrée fermée (grand ouverte, le vantail masque les trous)",
            f"tiroir du haut : pousser le linge dans le trou de la façade, à {cm(HAUT['trou'][0])}–{cm(HAUT['trou'][1])} "
            "du sol (hauteur de la main, debout)",
            f"tiroir du bas : se baisser, trou à {cm(BAS['trou'][0])}–{cm(BAS['trou'][1])} du sol (genou)",
            "rien à ouvrir"],
    retirer=[f"tirer le tiroir à fond, la main dans le trou (≈ {cm(EFFORT['tirer'])} N)",
             "soulever ensemble les deux barres : le sac pend dessous, plein",
             "le poser devant le hublot, à côté, et vider ; remettre les barres dans leurs entailles, fermer"],
    bouche=dict(l=TROU["l"], p=TROU["h"], forme="stade (trou vertical dans la façade)",
                hauteur_haut=(HAUT["trou"][0], HAUT["trou"][1]), hauteur_bas=(BAS["trou"][0], BAS["trou"][1]),
                note="largeur × hauteur en cm du trou de la façade ; dans le tiroir, le sac s'ouvre en grand "
                     f"({cm(HAUT['sac'].x1 - HAUT['sac'].x0)} × {cm(HAUT['sac'].y1 - HAUT['sac'].y0)})"),
    contenants=dict(n=2, litres=[round(BAS["volume"]), round(HAUT["volume"])], independants=True,
                    note="un sac en toile par tiroir (bas, haut), pendu à deux barres ; le linge peut s'entasser "
                         "au-dessus des barres jusqu'au trou"),
    pieces=N_PIECES,
    pieces_detail=f"{sum(1 for b in PIECES if b.rep)} panneaux de mélaminé 18 (caisson 6, deux tiroirs à 5) et 4 "
                  "barres ; l'échelle sud (5 tasseaux) est reprise du meuble actuel",
    usinages=["2 trous en stade 30 × 10 dans les façades : 2 trous de scie cloche Ø 100 par façade et 2 traits de scie "
              "sauteuse, chant thermocollant dans le trou",
              "8 entailles en U de 25 × 42 en haut des côtés de caisse (mèche plate Ø 25 puis 2 traits de sauteuse)",
              "4 trous Ø 10 dans le fond pour les écrous à griffes des vérins",
              "fixation des coulisses : vis 4 × 16 aux trous du gabarit, mêmes hauteurs des deux côtés",
              "trous ovalisés dans les traverses (le chêne bouge)", "aucune défonceuse nécessaire"],
    quincaillerie=[(n, q, s, p) for n, q, s, p, _ in QUINC if not n.startswith("Tablette")],
    outils=["scie circulaire et règle (ou découpe en magasin)", "scie sauteuse", "scie cloche Ø 100", "mèche plate Ø 25",
            "perceuse-visseuse, forets 2,5 à 5, fraise à noyer, embout Direkta", "marteau (écrous à griffes)",
            "fer à repasser et cutter (chant)", "équerre, niveau, mètre, serre-joints, cales de 3 mm",
            "machine à coudre (sacs)"],
    reglages=["vérins du caisson : plan de niveau à 85,5, 5 mm au-dessus de la machine (et vérins de l'échelle sud)",
              "coulisses : vissées à la même hauteur et parallèles au fond des deux côtés (une cale de hauteur)",
              "façades : 3 mm entre elles, 3 mm sous le plan, alignées ; équerres vissées en dernier, façade calée",
              "coins de calage contre les murs nord (caisson) et sud (échelle)"],
    risques=[f"basculement vers l'avant : un tiroir plein tiré à fond tient seul, mais un appui de plus de "
             f"≈ {EFFORT['appui']:.0f} kg sur le bord de sa façade (enfant qui s'y suspend, genou) fait basculer le "
             f"meuble (pas de fixation murale) ; ≈ {EFFORT['appui_deux']:.0f} kg seulement si les deux tiroirs sont tirés",
             "porte d'entrée : un tiroir tiré bloque le vantail ; vantail grand ouvert, les trous sont masqués",
             "linge entassé au-dessus des barres dans le tiroir du bas : il frotte sous la caisse du haut en fermant",
             "le linge se voit par le trou ; odeurs (mais le sac respire)",
             "chants coupés du mélaminé près du sol : à plaquer tous, sinon l'aggloméré gonfle à la première fuite",
             "hublot ouvert à fond vers la gauche : il peut empêcher de tirer le tiroir du bas (selon la machine)"],
    cout_estime=COUT,
    cout_detail=f"{cm(COUT)} € (dont {cm(COUT_RELEVE)} € relevés, le reste estimé), échelle sud non comptée : elle "
                "porte le plan au-delà de la machine dans toutes les variantes",
    porte_entree=f"oui : tiré de plus de {cm(DEVANT)}, un tiroir entre dans le débattement du vantail (arrêté à "
                 f"≈ {ANGLE_PORTE:.0f}°) ; vantail grand ouvert, il passe à {cm(DEVANT)} des façades et masque les "
                 "deux trous",
)


# ------------------------------------------------------------------ chapitre
def _tableau_jeux():
    lignes = [
        ("Course du tiroir", f"{cm(COUL['course'])} (sortie totale, coulisse de {COUL['L'] * 10:.0f})",
         "toute la caisse sort devant le plan : on soulève le sac tout droit"),
        ("Coulisse", f"{cm(COUL['ep'] * 10)} mm de chaque côté", f"caisse de {cm(BY1 - BY0)} pour {cm(IY1 - IY0)} entre "
                                                                 "les côtés du caisson"),
        ("Caisse fermée ↔ dos du caisson", cm(IX1 - BX1), ""),
        ("Façades", "3 mm entre elles, sous le plan et au-dessus du fond", f"{cm(FY1 - FY0)} de large, "
                                                                           f"{cm(FZ['bas'][1] - FZ['bas'][0])} de haut"),
        ("Barre ↔ trou", "3 mm", "le dessus de la barre avant est juste sous le bas du trou"),
        ("Dessous de la caisse du haut ↔ trou du bas", cm(HAUT["z_fond"] - BAS["trou"][1]),
         "place du linge entassé dans le tiroir du bas"),
        ("Barre arrière tirée ↔ nu du plan", f"{cm(JEU_SORTIE * 10)} mm", "tiroir du bas : le sac monte sans toucher"),
        ("Caisson ↔ machine", cm(M.MACHINE.y0 - CY1), "comme aujourd'hui"),
    ]
    return ('<div class="scroll"><table><thead><tr><th>Jeu</th><th>Valeur</th><th>Pourquoi</th></tr></thead><tbody>'
            + "".join(f"<tr><td>{escape(a)}</td><td class=\"mono\">{escape(b)}</td><td>{escape(c)}</td></tr>"
                      for a, b, c in lignes) + "</tbody></table></div>")


def section():
    e = EFFORT
    isos = [iso((), "Fermé"), iso(("haut",), "Tiroir du haut tiré"), iso(("bas",), "Tiroir du bas tiré")]
    caps = ["Fermé : deux façades blanches, un trou en stade dans chacune.",
            "Tiroir du haut tiré à fond : le sac pend entre ses deux barres.",
            "Tiroir du bas tiré à fond : la caisse sort entièrement devant le plan."]
    figs_iso = "".join(f'<div class="fig"><div class="scroll">{s}</div><p class="cap">{c}</p></div>'
                       for s, c in zip(isos, caps))
    cotes = "".join([
        CO.figure("tir-dessus", "Plan de l'alcôve (vue de dessus, coupée à 60 du sol)", vue_dessus(),
                  "Caisson et tiroirs coupés en foncé, machine et échelle sud ; le plan de travail en tireté. En rouge : "
                  "le tiroir du haut tiré à fond, et le vantail de la porte d'entrée qu'il arrête. Gris : le vantail "
                  "grand ouvert et l'arc de son bord libre."),
        CO.figure("tir-face", "Vue de face", vue_face(),
                  "Depuis la salle de bain. Les deux trous sont à la même place dans chaque façade, en haut : on y "
                  "passe aussi la main pour tirer."),
        CO.figure("tir-coupe", "Coupe par le milieu des tiroirs (vue vers le nord)", coupe_tiroirs(),
                  "Le côté nord du caisson derrière ; les caisses, barres et sacs coupés. En rouge : le tiroir du haut "
                  "tiré à fond (le tiroir du bas sort de la même longueur)."),
        CO.figure("tir-coulisses", "Coupe transversale (vue vers le mur du fond)", coupe_coulisses(),
                  "Au milieu de la profondeur : les deux coulisses de chaque tiroir entre le côté du caisson et celui "
                  "de la caisse, la barre arrière posée dans ses entailles."),
    ])
    return f"""<p>{escape(RESUME)} Le caisson remplace les échelles nord et du milieu ; l'échelle sud, la machine, le plan et le caisson haut ne changent pas.</p>

<div class="grid2">{figs_iso}</div>

<h3 id="tir-plans">Plans</h3>
<div class="feuille">{cotes}</div>

<h3 id="tir-mecanisme">Mécanismes</h3>
<p><b>Ce qui porte.</b> Le caisson ({cm(CX1 - CX0)} × {cm(CY1 - CY0)} × {cm(ZP - Z0)}) : deux côtés posés sur le fond, un dos plein entre eux et deux traverses de {TRAV} en haut ; le dos empêche le caisson de se mettre en losange. Il est posé sur quatre vérins (les mêmes que ceux du meuble actuel, dans des écrous à griffes frappés dans le fond). Le plan repose sur le chant des côtés et des traverses, vissé par-dessous à travers les traverses (vis 4 × 30, trous ovalisés). Côté sud, au-delà de la machine, l'échelle sud du meuble actuel le porte toujours : la portée au-dessus de la machine reste de {cm(M.ECH["s"] - CY1)}, comme aujourd'hui. Rien au mur : des coins de calage entre le côté nord et le carrelage, comme pour les échelles.</p>
<p><b>Comment ça bouge.</b> Chaque tiroir roule sur une paire de coulisses à billes à sortie totale de {COUL["L"] * 10:.0f} ({cm(COUL["ep"] * 10)} mm d'épaisseur, vissées à l'intérieur des côtés du caisson et sur les côtés de la caisse). On le tire par le trou de sa façade : il sort de {cm(COUL["course"])}, toute la caisse passe devant le plan. Effort pour tirer un tiroir plein : ≈ {cm(e["tirer"])} N (roulement à billes), plus le petit cran de fermeture des coulisses.</p>
<p><b>Ce qui arrête.</b> Fermé : la façade vient contre le chant avant des côtés et du fond du caisson. Ouvert : la butée de fin de course des coulisses ; leurs leviers permettent de sortir la caisse entière si besoin.</p>
<p><b>Le trou et le sac.</b> Un stade de {cm(TROU["l"])} × {cm(TROU["h"])} en haut de chaque façade, son bord haut à {cm(TROU["haut"])} du haut de la façade. Derrière, un sac en toile (comme ceux du meuble actuel, en plus simple : une bande et deux soufflets rectangulaires) pend entre deux barres rondes Ø {BARRE["d"] * 10:.0f} posées dans des entailles en U au haut des côtés de la caisse ; le dessus de la barre avant est 3 mm sous le trou, le linge passe par-dessus et tombe dans le sac. Sac du haut ≈ {HAUT["volume"]:.0f} L, sac du bas ≈ {BAS["volume"]:.0f} L, plus ce qui s'entasse au-dessus des barres. Pour vider : tirer le tiroir, soulever les deux barres ensemble, le sac vient plein ; la machine est juste à droite. Pas de volet : le trou reste ouvert, le linge respire (un volet basculant, charnière en haut, reste possible en option).</p>
<p><b>Le tiroir du bas.</b> Son trou est à {cm(BAS["trou"][0])}–{cm(BAS["trou"][1])} du sol, à hauteur du genou : on se baisse pour y pousser le linge, ou on le lance d'en haut. Celui du haut est à {cm(HAUT["trou"][0])}–{cm(HAUT["trou"][1])}, à hauteur de la main. Pour vider le bas, on tire à fond : la barre arrière sort à {cm(JEU_SORTIE * 10)} mm devant le nu du plan et de la façade du haut, le sac monte tout droit.</p>
<p><b>Efforts.</b> Tiroir du haut vide ≈ {cm(e["tiroir"]["haut"])} kg, plein ≈ {e["tiroir"]["haut"] + LINGE:.0f} kg (linge {LINGE:.0f} kg, estimé) : ≈ {e["coulisse"]:.0f} kg par coulisse, pour des coulisses de {COUL["charge"]} kg la paire au moins. Chaque barre porte ≈ {e["barre"]:.0f} N, sac plein. Basculement : le meuble (caisson, tiroirs, plan et échelle sud vissés ensemble, ≈ {e["caisson"] + e["tiroir"]["haut"] + e["tiroir"]["bas"] + e["plan"] + e["echelle"]:.0f} kg, estimé) pivote sur l'avant de ses vérins. Un tiroir plein tiré à fond tient seul ; il faut un appui de ≈ {e["appui"]:.0f} kg au bord de sa façade pour le faire basculer (≈ {e["appui_deux"]:.0f} kg si les deux tiroirs sont tirés). La machine, posée dessous sans lien, ne retient rien.</p>
<p><b>Porte d'entrée.</b> Grand ouverte, elle passe à {cm(DEVANT)} des façades : elle masque les deux trous et un tiroir ne s'ouvre que de {cm(DEVANT)}. Porte fermée, un tiroir tiré de plus de {cm(DEVANT)} entre dans son débattement : tiré à fond, il l'arrête à ≈ {ANGLE_PORTE:.0f}° (elle ne s'ouvre presque plus). On se sert donc des tiroirs porte fermée, et on les referme avant de sortir.</p>
{_tableau_jeux()}
<p class="note">Coût du meuble à linge seul (caisson, tiroirs, coulisses, sacs, quincaillerie ; hors plan, machine, caisson haut et échelle sud, commune à toutes les variantes) : ≈ {cm(COUT)} €, dont {cm(COUT_RELEVE)} € de prix relevés (tablettes, vérins, équerres, vis, chant, toile), le reste estimé (coulisses, écrous à griffes, Direkta, vis 4 × 30, ronds de bois). Masses volumiques et masse du linge de mémoire, non vérifiées.</p>"""


if __name__ == "__main__":
    print(f"{TITRE}\n  bas {BAS['volume']:.1f} L, haut {HAUT['volume']:.1f} L ; trous {BAS['trou']} {HAUT['trou']}")
    print(f"  coût {COUT} € (relevé {COUT_RELEVE}) ; appui de basculement {EFFORT['appui']:.1f} kg "
          f"({EFFORT['appui_deux']:.1f} les deux tirés) ; porte arrêtée à {ANGLE_PORTE:.1f}°")
    print(f"  masses : {EFFORT}")
