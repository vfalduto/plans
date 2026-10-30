# Génère salon-enfilade.html : l'enfilade du mur ouest à construire soi-même (plan, construction, matériaux,
# débit, plan de découpe, achats et prix, montage), sur le principe du meuble linge SDB.
#
#   python3 3d/salon/enfilade.py      (just salon)
#
# Les cotes extérieures (240 × 45 × 80, trois caissons de 80 centrés sur le mur, pieds de 15) viennent de modele.py ; la construction
# (caissons, épaisseurs, quincaillerie, prix) est décidée ici. Le HTML est seulement généré depuis ces données.

import math
import os
import sys
from collections import Counter, defaultdict
from html import escape

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import commun as C  # noqa: E402

M = C.M
f, rect, text, cote_h, cote_v = C.f, C.rect, C.text, C.cote_h, C.cote_v


def virg(v, n=None):
    """Cote affichée : 1 décimale au plus, sans « ,0 » (n : nombre de décimales imposé)."""
    return f(v).replace(".", ",") if n is None else C.virg(v, n)

VERSION, DATE = "V1.6", "30/10/2026"
RELEVE = "29/10/2026"   # date de la recherche de prix (en ligne, sans visite en magasin)

# ------------------------------------------------------------------ cotes du modèle
E = M.ENFILADE
L = round(E["y1"] - E["y0"], 1)          # 240 le long du mur ouest : trois caissons de 80
NORD = E["y0"]                           # jour entre le mur nord et le bout nord du meuble (centré sur le mur)
P, Z1, ZP, EP = E["p"], E["z1"], E["pieds"], E["ep"]
MODULES = M._MODULES                     # (façades, contenu), du nord au sud
N = len(MODULES)

# ------------------------------------------------------------------ choix de construction (V1.3, à valider)
FAC = 1.8                                # façades en chêne lamellé-collé de 18
TAMPON = round(E["facade"] - FAC, 2)     # 0,2 : tampons silicone entre caisson et façades
DOS = 0.32                               # dos en panneau de fibres dures 3,2, vissé en applique
PC = round(P - E["facade"] - DOS, 2)     # profondeur des côtés : 45 − 2 − 0,32
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
PIEDS_X = (5, round(P - E["facade"] - 5, 1))   # rangées de pieds : à 5 du mur et à 5 du nu du caisson
DESSUS = (1.8, 3)                        # (épaisseur, nombre de pièces) : une tablette de chêne 18 par caisson
# vides sous chaque étagère, du fond vers le haut, par module : vinyles debout sur le fond (31,5 + 1,5) au nord ;
# assiettes et plats, puis verres, au sud ; aucun dans le module des tiroirs
ETAGERES = [[33], [], [22, 20]]
VINYLE = 31.5


def bas(v):
    """Arrondi au mm inférieur : une pièce arrondie ne déborde jamais de sa place."""
    return math.floor(v * 10 + 1e-6) / 10


def euros(v):
    return f"{v:,.2f}".replace(",", " ").replace(".", ",") + " €"


def geometrie(ep_d=DESSUS[0]):
    """Caissons (bornes au mm), hauteur du caisson, vides intérieurs, façades (portes et tiroirs), pieds."""
    g = dict(ep_d=ep_d)
    g["Y"] = [round(k * L / N, 1) for k in range(N + 1)]
    g["W"] = [round(b - a, 1) for a, b in zip(g["Y"], g["Y"][1:])]
    g["HC"] = round(Z1 - ZP - ep_d, 1)
    g["za"], g["zb"] = ZP, round(ZP + g["HC"] - JEU, 2)          # façades : du bas du caisson à 0,3 sous le dessus
    g["zi0"], g["zi1"] = round(ZP + EP, 2), round(ZP + g["HC"] - EP, 2)   # vide intérieur (fond → traverses)
    facs = []
    for k, (types, _) in enumerate(MODULES):
        ya = g["Y"][k] + BORD
        yb = g["Y"][k + 1] - BORD
        n = len(types)
        if types[0] == "porte":
            w = bas((yb - ya - (n - 1) * JEU) / n)
            for i in range(n):
                y0 = round(ya + i * (w + JEU), 2)
                facs.append(dict(type="porte", k=k, y0=y0, y1=round(y0 + w, 2), z0=g["za"], z1=g["zb"],
                                 charniere="n" if i == 0 else "s"))   # charnières côté extérieur du module
        else:
            h = bas((g["zb"] - g["za"] - (n - 1) * JEU) / n)
            for i in range(n):                                        # du bas vers le haut
                z0 = round(g["za"] + i * (h + JEU), 2)
                facs.append(dict(type="tiroir", k=k, y0=round(ya, 2), y1=round(yb, 2), z0=z0, z1=round(z0 + h, 2)))
    g["facades"] = facs
    g["pieds_y"] = [5] + g["Y"][1:-1] + [round(L - 5, 1)]            # sous les bords et à cheval sur les jonctions
    g["etageres"] = []
    for k, vides in enumerate(ETAGERES):
        z = g["zi0"]
        for v in vides:
            g["etageres"].append((k, round(z + v, 2)))
            z += v + EP
    return g


G = geometrie()


def controle(g=G):
    """La somme des pièces redonne les cotes extérieures du modèle."""
    assert abs(sum(g["W"]) - L) < 1e-6, g["W"]
    assert abs(DOS + PC + TAMPON + FAC - P) < 1e-6
    assert abs(ZP + g["HC"] + g["ep_d"] - Z1) < 1e-6
    for fc in g["facades"]:
        assert fc["z1"] <= Z1 - g["ep_d"] - JEU + 1e-6 and fc["y0"] >= 0 and fc["y1"] <= L
        if fc["type"] == "tiroir":    # la boîte passe sous les traverses et au-dessus du fond
            assert fc["z0"] + CALE_BOITE - DOS >= g["zi0"] and fc["z0"] + CALE_BOITE + H_BOITE <= g["zi1"], fc
    for k, z in g["etageres"]:
        assert z + EP <= g["zi1"], (k, z)
    assert COULISSE <= PC - 2 and PROF_ETAGERE <= PC - 2
    return f"{virg(sum(g['W']))} × {virg(DOS + PC + TAMPON + FAC, 0)} × {virg(ZP + g['HC'] + g['ep_d'], 0)}"


# ------------------------------------------------------------------ volumes 3D (vue iso, rendus Blender)
def pieces_3d(ouvert=False, g=G):
    """Boîtes du meuble en cm dans le repère du salon (x vers l'est depuis le mur ouest, y vers le sud depuis le
    mur nord, z depuis le sol), tirées des mêmes cotes que le débit. ouvert : la porte nord de M1 et la porte sud
    de M3 ouvertes à 90° (côté charnière), le tiroir du haut de M2 sorti de toute sa course. Aucune boîte n'en
    chevauche une autre (ordre du peintre de la vue iso)."""
    y_, x_ = E["y0"], E.get("x0", 0)
    fr = DOS + PC                                    # nu avant du caisson
    ps = []
    mc = "melamine" if RETENUE["caisson"] == "mel" else "chene"   # caisson, étagères et boîtes de tiroir

    def add(nom, x0, x1, y0, y1, z0, z1, mat):
        ps.append(C.Piece(nom, round(x_ + x0, 3), round(x_ + x1, 3), round(y_ + y0, 3), round(y_ + y1, 3),
                          round(z0, 3), round(z1, 3), mat))

    zh = ZP + g["HC"]                                # haut du caisson, dessous du dessus
    for k in range(N):
        m, ya, yb = f"M{k + 1}", g["Y"][k], g["Y"][k + 1]
        add(f"{m} {'joue nord' if k == 0 else 'côté nord'}", DOS, fr, ya, ya + EP, ZP, zh, "chene" if k == 0 else mc)
        add(f"{m} {'joue sud' if k == N - 1 else 'côté sud'}", DOS, fr, yb - EP, yb, ZP, zh,
            "chene" if k == N - 1 else mc)
        add(f"{m} fond", DOS, fr, ya + EP, yb - EP, ZP, g["zi0"], mc)
        add(f"{m} traverse arrière", DOS, DOS + TRAV, ya + EP, yb - EP, g["zi1"], zh, mc)
        add(f"{m} traverse avant", fr - TRAV, fr, ya + EP, yb - EP, g["zi1"], zh, mc)
        add(f"{m} dos", 0, DOS, ya + 0.2, yb - 0.2, ZP + 0.2, zh - 0.2, "fibre")
        for i, z in enumerate(z for kk, z in g["etageres"] if kk == k):
            add(f"{m} étagère {i + 1}", DOS, DOS + PROF_ETAGERE, ya + EP + 0.2, yb - EP - 0.2, z, z + EP, mc)
    if DESSUS[1] == 1:
        add("dessus", 0, P, 0, L, Z1 - g["ep_d"], Z1, "chene")
    else:                                            # un dessus par caisson, joints au droit des jonctions
        for k in range(N):
            add(f"M{k + 1} dessus", 0, P, g["Y"][k], g["Y"][k + 1], Z1 - g["ep_d"], Z1, "chene")
    for y in g["pieds_y"]:
        for x in PIEDS_X:
            add(f"pied {virg(x)} / {virg(y)}", x - 1.25, x + 1.25, max(y - 1.25, 0), min(y + 1.25, L), 0, ZP, "noir")
    # façades : portes (numérotées du nord au sud dans leur module) et tiroirs (du bas vers le haut)
    tiroirs = [fc for fc in g["facades"] if fc["type"] == "tiroir"]
    haut = max(tiroirs, key=lambda fc: fc["z0"])
    rang = Counter()
    for fc in g["facades"]:
        m = f"M{fc['k'] + 1}"
        rang[(fc["k"], fc["type"])] += 1
        i = rang[(fc["k"], fc["type"])]
        if fc["type"] == "porte":
            w = fc["y1"] - fc["y0"]
            nord = fc["charniere"] == "n"
            ouverte = ouvert and ((fc["k"] == 0 and nord) or (fc["k"] == N - 1 and not nord))
            if ouverte:                                  # tournée autour de son chant côté charnière, vers la pièce
                y0, y1 = (fc["y0"] - FAC, fc["y0"]) if nord else (fc["y1"], fc["y1"] + FAC)
                add(f"{m} porte {i} (ouverte)", P, P + w, y0, y1, fc["z0"], fc["z1"], "chene_v")
            else:
                add(f"{m} porte {i}", P - FAC, P, fc["y0"], fc["y1"], fc["z0"], fc["z1"], "chene_v")
            continue
        dx = COULISSE if ouvert and fc is haut else 0    # sortie totale : la course de la coulisse
        t = f"{m} tiroir {i}" + (" (sorti)" if dx else "")
        add(f"{t} façade", P - FAC + dx, P + dx, fc["y0"], fc["y1"], fc["z0"], fc["z1"], "chene_v")
        li0, li1 = g["Y"][fc["k"]] + EP, g["Y"][fc["k"] + 1] - EP
        bw = bas(li1 - li0 - 2 * EP_COUL)
        b0 = li0 + (li1 - li0 - bw) / 2                  # boîte centrée entre les coulisses
        zb = fc["z0"] + CALE_BOITE
        xa, xb = fr - COULISSE + dx, fr + dx
        add(f"{t} côté nord", xa, xb, b0, b0 + EP, zb, zb + H_BOITE, mc)
        add(f"{t} côté sud", xa, xb, b0 + bw - EP, b0 + bw, zb, zb + H_BOITE, mc)
        add(f"{t} arrière", xa, xa + EP, b0 + EP, b0 + bw - EP, zb, zb + H_BOITE, mc)
        add(f"{t} avant", xb - EP, xb, b0 + EP, b0 + bw - EP, zb, zb + H_BOITE, mc)
        add(f"{t} fond", xa, xb, b0, b0 + bw, zb - DOS, zb, "fibre")
    return ps


def chevauchements(ps):
    """Paires de boîtes dont l'intersection a un volume (doit être vide)."""
    def inter(a, b):
        return all(min(a1, b1) - max(a0, b0) > 1e-6 for a0, a1, b0, b1 in
                   ((a.x0, a.x1, b.x0, b.x1), (a.y0, a.y1, b.y0, b.y1), (a.z0, a.z1, b.z0, b.z1)))
    return [(a.nom, b.nom) for i, a in enumerate(ps) for b in ps[i + 1:] if inter(a, b)]


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

# Quincaillerie et consommables : quantité calculée depuis les comptes du meuble (c).
QUINC = [
    dict(poste="Charnière invisible Ø 35, 110°, en applique", ref="9154863", mag="weldom", prix=5.35,
         statut="relevé", url=None, q=lambda c: 2 * c["portes"], note="2 par porte ; prix supposé à l'unité"),
    dict(poste="Poussoir magnétique (ouverture par pression)", ref="à choisir", mag="weldom", prix=3.90,
         statut="estimé", url=None, q=lambda c: c["portes"], note="1 par porte, en haut côté ouverture"),
    dict(poste="Coulisses à billes 500, sortie totale, ouverture par pression (paire)", ref="à choisir", mag="lm",
         prix=19.90, statut="estimé", url=REF_COUL, q=lambda c: c["tiroirs"],
         note="25 kg ; repère : paire Emuca 450 amortie à 13,33 € (500 à relever)"),
    dict(poste="Pied de meuble carré noir 2,5 × 2,5 × 15, patin fileté M10", ref="69165075", mag="lm", prix=3.59,
         statut="relevé", url=LM_PIED, q=lambda c: c["pieds"], note="50 kg chacun ; platine 6 × 6"),
    dict(poste="Tampons silicone 2 mm (sachet de 20)", ref="à choisir", mag="weldom", prix=2.90, statut="estimé",
         url=None, q=lambda c: math.ceil(4 * c["facades"] / 20), note="4 par façade"),
    dict(poste="Taquets d'étagère Ø 5 (sachet de 16)", ref="à choisir", mag="weldom", prix=2.90, statut="estimé",
         url=None, q=lambda c: math.ceil(4 * c["etageres"] / 16), note="4 par étagère"),
    dict(poste="Vis de liaison de meuble Ø 5 pour 2 × 18 (sachet de 4)", ref="à choisir", mag="weldom", prix=3.50,
         statut="estimé", url=None, q=lambda c: c["jonctions"], note="4 par jonction de caissons"),
    dict(poste="Équerres de fixation à trou oblong (sachet de 4)", ref="à choisir", mag="weldom", prix=3.90,
         statut="estimé", url=None, q=lambda c: c["caissons"], note="dessus : 4 par caisson, le bois massif travaille"),
    dict(poste="Équerre acier 40 × 40 (anti-basculement)", ref="à choisir", mag="weldom", prix=1.20, statut="estimé",
         url=None, q=lambda c: c["caissons"], note="1 par caisson, sous la traverse arrière"),
    dict(poste="Chevilles et vis pour la cloison (selon sa nature)", ref="à choisir", mag="weldom", prix=5.90,
         statut="estimé", url=None, q=lambda c: 1, note="Molly si plaque de plâtre"),
    dict(poste="Vis bois 4 × 50 (boîte de 100)", ref="à choisir", mag="weldom", prix=7.90, statut="estimé",
         url=None, q=lambda c: 1, note="caissons et boîtes de tiroir, avec avant-trous"),
    dict(poste="Vis 3,5 × 16 (boîte de 200)", ref="à choisir", mag="weldom", prix=5.90, statut="estimé", url=None,
         q=lambda c: 1, note="dos, fonds, pieds, coulisses, charnières"),
    dict(poste="Vis 3,5 × 30 (boîte de 100)", ref="à choisir", mag="weldom", prix=4.90, statut="estimé", url=None,
         q=lambda c: 1, note="façades de tiroir, dessus"),
    dict(poste="Tourillons Ø 8 × 35 et colle à bois", ref="à choisir", mag="weldom", prix=8.80, statut="estimé",
         url=None, q=lambda c: 1, note="caissons collés, joues sans vis apparente, joints des dessus"),
    dict(poste="Huile dure incolore, bidon de 1 L", ref="à choisir", mag="weldom", prix=35.00, statut="estimé",
         url=REF_HUILE, q=lambda c: math.ceil(c["chene_m2"] * 2 * HUILE["couches"] / HUILE["rendement"]),
         note="deux couches, toutes faces ; repère : 0,5 L de Blanchon à 17,50 € (Brico Dépôt)"),
    dict(poste="Abrasifs 120, 180, 240", ref="à choisir", mag="weldom", prix=7.90, statut="estimé", url=None,
         q=lambda c: 1, note="ponçage avant huile"),
]
OUTILLAGE = [   # à acheter seulement si l'atelier ne les a pas (hors total du meuble)
    ("Mèche Forstner Ø 35 avec butée", 12.90),
    ("Gabarit de perçage pour taquets Ø 5 (ou tasseau percé maison)", 14.90),
    ("Foret à bois Ø 5 avec bague de butée", 4.90),
]

# Variantes de matériau : caisson ("mel" = mélaminé blanc, format choisi par largeur), façades, dessus (ép., pièces).
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
HUILE = dict(couches=2, rendement=15)   # m² par litre et par couche (ordre de grandeur, à lire sur le bidon)
CHANT = dict(rouleau=5, prix=6.90, statut="estimé")   # chant thermocollant décor chêne, rouleau de 5 m
RETENUE = next(v for v in VARIANTES if v.get("retenu"))
PREFIXE = {"caisson": "A", "facade": "B", "tiroir": "C", "fond": "D", "dessus": "E"}
GROUPES = {"caisson": "Caissons", "facade": "Façades et joue (chêne visible)", "tiroir": "Boîtes de tiroir",
           "fond": "Dos et fonds de tiroir", "dessus": "Dessus"}


# ------------------------------------------------------------------ débit : pièces repérées
def pieces(v=RETENUE):
    """Toutes les pièces, une ligne par pièce physique, puis repérées (mêmes nom, cotes, ép. → même repère)."""
    g = geometrie(v["dessus"][0])
    ps = []
    chant = "chant d'usine" if v["caisson"] == "mel" else "chant poncé"

    def add(grp, nom, lg, lr, ep, ou, note=""):
        ps.append(dict(grp=grp, nom=nom, L=round(lg, 1), l=round(lr, 1), ep=ep, ou=ou, note=note))

    for k, w in enumerate(g["W"]):
        m, li = f"M{k + 1}", w - 2 * EP
        if k == 0:
            add("facade", "Joue nord", g["HC"], PC, EP, m, "fil vertical, côté visible")
        else:
            add("caisson", "Côté", g["HC"], PC, EP, m, f"{chant} devant")
        if k == N - 1:
            add("facade", "Joue sud", g["HC"], PC, EP, m, "fil vertical, côté visible")
        else:
            add("caisson", "Côté", g["HC"], PC, EP, m, f"{chant} devant")
        add("caisson", "Fond", li, PC, EP, m, f"{chant} devant")
        for _ in range(2):
            add("caisson", "Traverse haute", li, TRAV, EP, m, "avant et arrière")
        add("fond", "Dos", w - 0.4, g["HC"] - 0.4, DOS, m, "en applique, 2 mm en retrait des bords")
        for kk, _ in g["etageres"]:
            if kk == k:
                add("caisson", "Étagère", li - 0.4, PROF_ETAGERE, EP, m, "sur 4 taquets")
        for fc in g["facades"]:
            if fc["k"] != k:
                continue
            if fc["type"] == "porte":
                add("facade", "Porte", fc["z1"] - fc["z0"], fc["y1"] - fc["y0"], FAC, m, "fil vertical")
            else:
                bw = bas(li - 2 * EP_COUL)
                add("facade", "Façade de tiroir", fc["y1"] - fc["y0"], fc["z1"] - fc["z0"], FAC, m, "fil horizontal")
                for _ in range(2):
                    add("tiroir", "Côté de tiroir", COULISSE, H_BOITE, EP, m, f"{chant} en haut")
                for _ in range(2):
                    add("tiroir", "Avant / arrière de tiroir", bw - 2 * EP, H_BOITE, EP, m, f"{chant} en haut")
                add("fond", "Fond de tiroir", bw, COULISSE, DOS, m, "vissé sous la boîte")
    if v["dessus"][1] == 1:
        add("dessus", "Dessus", L, P, v["dessus"][0], "M1 à M3", "d'une pièce, refendu dans le plan de travail")
    else:
        for k, w in enumerate(g["W"]):
            add("dessus", "Dessus", w, P, v["dessus"][0], f"M{k + 1}", "un par caisson, joints au droit des jonctions")
    # repères : par groupe, dans l'ordre d'apparition
    vus, cpt = {}, Counter()
    for p in ps:
        cle = (p["grp"], p["nom"], p["L"], p["l"], p["ep"])
        if cle not in vus:
            cpt[p["grp"]] += 1
            vus[cle] = f'{PREFIXE[p["grp"]]}{cpt[p["grp"]]}'
        p["rep"] = vus[cle]
    return ps


def debit(ps):
    """Lignes du tableau de débit : une par repère, quantité et modules."""
    par = {}
    for p in ps:
        d = par.setdefault(p["rep"], dict(p, n=0, ous=[]))
        d["n"] += 1
        if p["ou"] not in d["ous"]:
            d["ous"].append(p["ou"])
    return sorted(par.values(), key=lambda d: (list(PREFIXE).index(d["grp"]), int(d["rep"][1:])))


def format_de(p, v):
    if p["grp"] == "fond":
        return "HDF"
    if p["grp"] == "dessus":
        return "PT36" if v["dessus"][1] == 1 else v["facade"]
    if p["grp"] == "facade":
        return v["facade"]
    if v["caisson"] != "mel":
        return v["caisson"]
    return next(m for m in MELAMINE if FORMATS[m]["l"] >= p["l"])


def calepiner(lst, F):
    """Découpe en bandes (refente puis tronçonnage) : pièces triées par largeur, posées dans la bande la plus
    étroite qui les reçoit, sinon dans une nouvelle bande, sinon sur un nouveau panneau. Une bande de mélaminé
    touche toujours un bord d'usine (deux bandes au plus par tablette)."""
    pans = []
    for rep, lg, lr in sorted(lst, key=lambda p: (-p[2], -p[1])):
        assert lg <= F["L"] and lr <= F["l"], (rep, lg, lr, F["nom"])
        ok = [(b["w"], b) for pa in pans for b in pa["bandes"] if b["w"] >= lr and b["x"] + lg <= F["L"] + 1e-6]
        if ok:
            b = min(ok, key=lambda t: t[0])[1]
        else:
            libres = [pa for pa in pans if pa["reste"] >= lr and len(pa["bandes"]) < F.get("bandes", 99)]
            if libres:
                pa = min(libres, key=lambda pa: pa["reste"])
            else:
                pa = dict(bandes=[], reste=F["l"])
                pans.append(pa)
            if F.get("bandes") == 2 and pa["bandes"]:
                y = F["l"] - lr                        # deuxième bande : contre l'autre bord d'usine
            else:
                y = F["l"] - pa["reste"]
            b = dict(w=lr, y=y, x=0, poses=[])
            pa["bandes"].append(b)
            pa["reste"] -= lr + TRAIT
        b["poses"].append((rep, lg, lr, b["x"]))
        b["x"] += lg + TRAIT
    return pans


def comptes(ps, g, v):
    nf = Counter(fc["type"] for fc in g["facades"])
    chene = sum(p["L"] * p["l"] for p in ps if FORMATS[format_de(p, v)].get("bois")) / 1e4   # m², une face
    return dict(portes=nf["porte"], tiroirs=nf["tiroir"], facades=len(g["facades"]), chene_m2=chene,
                etageres=len(g["etageres"]), caissons=N, jonctions=N - 1, pieds=len(g["pieds_y"]) * len(PIEDS_X))


def chiffrage(v=RETENUE):
    """Lignes d'achat (panneaux calepinés, fibres dures au m², quincaillerie), découpes et total TTC."""
    ps = pieces(v)
    g = geometrie(v["dessus"][0])
    par = defaultdict(list)
    for p in ps:
        par[format_de(p, v)].append(p)
    lignes, cal = [], {}
    for cle in sorted(par, key=lambda c: (ORDRE_MAG.index(FORMATS[c]["mag"]), list(FORMATS).index(c))):
        F, lst = FORMATS[cle], par[cle]
        if F.get("m2"):
            q, unite, note = math.ceil(sum(p["L"] * p["l"] for p in lst) / 1e3) / 10, "m²", "découpe faite par le magasin"
        else:
            cal[cle] = calepiner([(p["rep"], p["L"], p["l"]) for p in lst], F)
            q, unite = len(cal[cle]), "u"
            note = "repères " + ", ".join(sorted({p["rep"] for p in lst}, key=lambda r: (r[0], int(r[1:]))))
        lignes.append(dict(poste=F["nom"], ref=F["ref"], mag=F["mag"], q=q, unite=unite, pu=F["prix"],
                           statut=F["statut"], url=F["url"], note=note, panneau=True))
    if v.get("chant"):
        m = sum(2 * (p["L"] + p["l"]) for p in ps if p["grp"] in ("facade", "dessus")) / 100
        lignes.append(dict(poste="Chant thermocollant décor chêne, rouleau de 5 m", ref="à choisir", mag="lm",
                           q=math.ceil(m / CHANT["rouleau"]), unite="u", pu=CHANT["prix"], statut="estimé", url=None,
                           note=f"{virg(m)} m de chants coupés", panneau=True))
    c = comptes(ps, g, v)
    for qd in QUINC:
        lignes.append(dict(poste=qd["poste"], ref=qd["ref"], mag=qd["mag"], q=qd["q"](c), unite="u", pu=qd["prix"],
                           statut=qd["statut"], url=qd["url"], note=qd["note"], panneau=False))
    for li in lignes:
        li["total"] = round(li["q"] * li["pu"], 2)
    total = round(sum(li["total"] for li in lignes), 2)
    rel = round(sum(li["total"] for li in lignes if li["statut"] == "relevé"), 2)
    return dict(v=v, ps=ps, g=g, lignes=lignes, cal=cal, total=total, releve=rel, estime=round(total - rel, 2), c=c)


# ------------------------------------------------------------------ dessins
STYLE = """<style>
svg.enf .dimt{font-size:10px}
svg.enf .t{font-size:11.5px}svg.enf .ts{font-size:10px}svg.enf .tx{font-size:8.5px}svg.enf .tb{font-size:12px;font-weight:700}
svg.enf .inv{fill:#F7F8F6}
.mel{fill:var(--panel);stroke:var(--ink);stroke-width:.7}
.hdf{fill:#8A6E52;stroke:var(--ink);stroke-width:.3}
.hdfl{fill:#8A6E52;fill-opacity:.18;stroke:none}
.chute{fill:var(--line);fill-opacity:.3;stroke:var(--muted);stroke-width:.6}
.ouv{fill:none;stroke:var(--muted);stroke-width:.7;stroke-dasharray:4 3}
.arc{fill:none;stroke:var(--tri);stroke-width:.9;stroke-dasharray:4 2}
.porteo{fill:var(--wood);fill-opacity:.25;stroke:var(--tri);stroke-width:.7;stroke-dasharray:3 2}
.fl{stroke:var(--muted);stroke-width:.6}
.fl2{stroke:var(--tri);stroke-width:.9;fill:none;marker-end:url(#fleche)}
.flm{fill:var(--tri)}
.decoupes{display:grid;grid-template-columns:repeat(auto-fit,minmax(min(100%,720px),1fr));gap:10px}
.decoupes figure{margin:0}.decoupes figcaption{font-size:13px;color:var(--muted);margin:2px 0 4px}
.decoupes svg{display:block;width:100%;max-width:820px;height:auto}
.lg{display:inline-block;width:14px;height:10px;border:1px solid var(--ink);vertical-align:-1px;margin:0 4px 0 10px}
.lg.chene{background:var(--wood)}.lg.mel{background:var(--panel)}.lg.hdf{background:#8A6E52}.lg.chute{background:var(--line)}
tr.grp td{background:var(--paper);font-weight:700;padding-top:12px}
tr.retenu td{background:var(--paper)}tr.retenu td:first-child{box-shadow:inset 5px 0 var(--water)}
.badge{display:inline-block;font:700 11px "JetBrains Mono",ui-monospace,monospace;text-transform:uppercase;letter-spacing:.06em;border:1px solid var(--water);color:var(--water);border-radius:999px;padding:1px 8px;margin-left:6px}
.st{font:600 11px "JetBrains Mono",ui-monospace,monospace;white-space:nowrap}.st.est{color:var(--tri)}
ol.etapes{padding-left:22px;max-width:880px}ol.etapes li{margin:7px 0}
</style>"""

FLECHE = ('<defs><marker id="fleche" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" '
          'orient="auto-start-reverse"><path class="flm" d="M0,0 L10,5 L0,10 z"/></marker></defs>')


def svg(vb, corps, label):
    return f'<svg class="enf" viewBox="{vb}" role="img" aria-label="{escape(label)}">{corps}</svg>'


def cl_caisson():
    """Classe SVG des pièces du caisson, des étagères et des boîtes de tiroir dans la variante retenue."""
    return "mel" if RETENUE["caisson"] == "mel" else "shelfc"


def face_svg(g=G):
    """Élévation de face, vue de la pièce (regard vers l'ouest : le nord, contre le mur, est à droite)."""
    k = 3.4
    U = lambda y: (L - y) * k  # noqa: E731
    V = lambda z: (Z1 - z) * k  # noqa: E731
    o = [rect(U(-NORD), V(Z1 + 10), U(-NORD - 5), V(0), "mur-h"),
         text(U(-NORD - 2.5), V(0) + 15, "mur nord", "tx muted"),
         f'<line class="floorl" x1="{f(U(L) - 30)}" y1="{f(V(0))}" x2="{f(U(-NORD - 5))}" y2="{f(V(0))}"/>']
    for y in g["pieds_y"]:
        o.append(rect(U(min(y + 1.25, L)), V(ZP), U(max(y - 1.25, 0)), V(0), "mont"))
    o.append(rect(U(L), V(ZP + g["HC"]), U(0), V(ZP), cl_caisson()))
    o.append(rect(U(L), V(Z1), U(0), V(Z1 - g["ep_d"]), "shelfc"))
    for fc in g["facades"]:
        o.append(rect(U(fc["y1"]), V(fc["z1"]), U(fc["y0"]), V(fc["z0"]), "shelfc"))
        if fc["type"] == "porte":
            yh, yf = (fc["y0"], fc["y1"]) if fc["charniere"] == "n" else (fc["y1"], fc["y0"])
            zm = (fc["z0"] + fc["z1"]) / 2
            o += [f'<polyline class="ouv" points="{f(U(yf))},{f(V(fc["z1"]))} {f(U(yh))},{f(V(zm))} '
                  f'{f(U(yf))},{f(V(fc["z0"]))}"/>']
            ya = yh + (CHARNIERE["axe"] if yh == fc["y0"] else -CHARNIERE["axe"])
            for z in (fc["z0"] + CHARNIERE["bout"], fc["z1"] - CHARNIERE["bout"]):
                o.append(f'<circle class="acierh" cx="{f(U(ya))}" cy="{f(V(z))}" r="{f(1.75 * k)}"/>')
    for y in g["Y"][1:-1]:                           # jonctions (et joints du dessus s'il est en pièces)
        zj = Z1 if DESSUS[1] > 1 else Z1 - g["ep_d"]
        o.append(f'<line class="ouv" x1="{f(U(y))}" y1="{f(V(zj))}" x2="{f(U(y))}" y2="{f(V(0) + 6)}"/>')
    # contenu et cotes sous le meuble
    for k_, (types, contenu) in enumerate(MODULES):
        ym = (g["Y"][k_] + g["Y"][k_ + 1]) / 2
        o.append(text(U(ym), V(0) + 15, f"M{k_ + 1} · {contenu}", "ts"))
        o.append(cote_h(U(g["Y"][k_ + 1]), U(g["Y"][k_]), V(0) + 36, f'caisson {virg(g["W"][k_])}'))
    o.append(cote_h(U(L), U(0), V(0) + 58, f"{virg(L)} = {N} × {virg(g['W'][0])}, centré sur le mur ({virg(NORD)} libres de chaque côté)"))
    # largeurs des façades au-dessus
    yv = V(Z1) - 12
    for fc in g["facades"]:
        if fc["type"] == "porte" or fc["z0"] == g["za"]:
            o.append(cote_h(U(fc["y1"]), U(fc["y0"]), yv, virg(fc["y1"] - fc["y0"])))
    o.append(cote_h(U(0), U(-NORD), V(Z1) - 30, f"jour {virg(NORD)}"))
    # hauteurs à gauche (bout sud)
    x1, x2 = -14, -40
    o += [cote_v(V(0), V(ZP), x1, f"pieds {f(ZP)}"),
          cote_v(V(ZP), V(ZP + g["HC"]), x1, f'caisson {virg(g["HC"])}'),
          cote_v(V(Z1 - g["ep_d"]), V(Z1), x1 - 16, virg(g["ep_d"])),
          cote_v(V(0), V(Z1), x2 - 6, f"{f(Z1)}")]
    porte = next(fc for fc in g["facades"] if fc["type"] == "porte")
    o.append(cote_v(V(porte["z0"]), V(porte["z1"]), U(-5) + 16, f'portes {virg(porte["z1"] - porte["z0"])}'))
    o.append(text(U(L) + 4, V(Z1) - 4, "dessus", "tx muted", "start"))
    vb = f"{f(x2 - 30)} {f(V(Z1) - 46)} {f(U(-NORD - 5) - x2 + 60)} {f(Z1 * k + 46 + 70)}"
    return svg(vb, "".join(o), "Élévation de face cotée de l'enfilade")


def profil_svg(g=G):
    """Deux coupes de profil (mur à gauche, pièce à droite) : par un module à portes, par le module à tiroirs."""
    k = 5
    V = lambda z: (Z1 - z) * k  # noqa: E731
    o = []

    def coupe(ox, kind):
        X = lambda x: ox + x * k  # noqa: E731
        fr = DOS + PC                                       # nu avant du caisson
        s = [rect(X(-5), V(Z1 + 6), X(0), V(0), "mur-h"),
             f'<line class="floorl" x1="{f(X(-5))}" y1="{f(V(0))}" x2="{f(X(P + 10))}" y2="{f(V(0))}"/>',
             rect(X(DOS), V(ZP + g["HC"]), X(fr), V(ZP), "hdfl"),
             rect(X(0), V(ZP + g["HC"] - 0.2), X(DOS), V(ZP + 0.2), "hdf")]
        for x in PIEDS_X:
            s.append(rect(X(x - 1.25), V(ZP), X(x + 1.25), V(0), "mont"))
        s += [rect(X(DOS), V(g["zi0"]), X(fr), V(ZP), cl_caisson()),
              rect(X(DOS), V(ZP + g["HC"]), X(DOS + TRAV), V(g["zi1"]), cl_caisson()),
              rect(X(fr - TRAV), V(ZP + g["HC"]), X(fr), V(g["zi1"]), cl_caisson()),
              rect(X(0), V(Z1), X(P), V(Z1 - g["ep_d"]), "shelfc")]
        mod = 0 if kind == "porte" else next(fc["k"] for fc in g["facades"] if fc["type"] == "tiroir")
        facs = [fc for fc in g["facades"] if fc["k"] == mod]
        for fc in facs[:1] if kind == "porte" else facs:
            s.append(rect(X(P - FAC), V(fc["z1"]), X(P), V(fc["z0"]), "shelfc"))
            for z in ((fc["z0"] + 3, fc["z1"] - 3) if kind == "porte" else ((fc["z0"] + fc["z1"]) / 2,)):
                s.append(rect(X(fr), V(z + 0.6), X(fr + TAMPON), V(z - 0.6), "dark"))
        if kind == "porte":
            fc = facs[0]
            for z in (fc["z0"] + CHARNIERE["bout"], fc["z1"] - CHARNIERE["bout"]):
                s.append(rect(X(fr - 5), V(z + 0.7), X(P - FAC + 1.2), V(z - 0.7), "acier"))
            z_s = next(z for kk, z in g["etageres"] if kk == mod)
            s += [rect(X(DOS), V(z_s + EP), X(DOS + PROF_ETAGERE), V(z_s), cl_caisson()),
                  rect(X(DOS + 1), V(g["zi0"] + VINYLE), X(DOS + 1 + VINYLE), V(g["zi0"]), "vinyl"),
                  text(X(DOS + 1 + VINYLE / 2), V(g["zi0"] + VINYLE / 2) + 4, f"vinyles {virg(VINYLE)}", "ts inv"),
                  text(X(DOS + 20), V(z_s + EP) - 6, "étagère sur taquets", "tx"),
                  text(X(DOS + 20), V(g["zi1"] - 6), "jeux, albums", "tx muted"),
                  # équerre anti-basculement sous la traverse arrière, vissée au mur à travers le dos
                  rect(X(DOS), V(g["zi1"]), X(DOS + 4), V(g["zi1"] - 0.35), "acier"),
                  rect(X(DOS), V(g["zi1"]), X(DOS + 0.35), V(g["zi1"] - 4), "acier"),
                  f'<line class="fl" x1="{f(X(-3))}" y1="{f(V(g["zi1"] - 2.5))}" x2="{f(X(DOS + 0.35))}" y2="{f(V(g["zi1"] - 2.5))}"/>',
                  cote_v(V(g["zi0"]), V(z_s), X(-5) - 12, f(z_s - g["zi0"])),
                  cote_v(V(z_s + EP), V(g["zi1"]), X(-5) - 12, virg(g["zi1"] - z_s - EP))]
            titre = "Coupe par M1 : porte, étagère"
        else:
            for fc in facs:
                zb0 = fc["z0"] + CALE_BOITE
                s += [rect(X(fr - COULISSE), V(zb0 + H_BOITE), X(fr), V(zb0), cl_caisson()),
                      rect(X(fr - COULISSE), V(zb0), X(fr), V(zb0 - DOS), "hdf"),
                      rect(X(fr - COULISSE + 0.5), V(zb0 + H_BOITE / 2 + 0.6), X(fr - 0.5), V(zb0 + H_BOITE / 2 - 0.6), "acier")]
                s.append(cote_v(V(fc["z0"]), V(fc["z1"]), X(P) + 14, virg(fc["z1"] - fc["z0"])))
            top = facs[-1]
            s += [text(X(fr - COULISSE / 2), V(top["z0"] + CALE_BOITE + H_BOITE) + 13, f"boîte {f(H_BOITE)}, coulisses {f(COULISSE * 10)}", "tx"),
                  cote_v(V(top["z0"] + CALE_BOITE), V(top["z0"] + CALE_BOITE + H_BOITE), X(fr - COULISSE) - 8, f(H_BOITE))]
            titre = "Coupe par M2 : tiroirs"
        s += [text(X(P / 2), V(Z1) - 26, titre, "tb"),
              text(X(P / 2), V(Z1) - 8, f'dessus {virg(g["ep_d"])}', "tx"),
              text(X(DOS + TRAV + 2), V(g["zi1"]) + 11, f"traverses {f(TRAV)}", "tx", "start") if kind == "porte" else "",
              text(X(DOS + PC / 2), V(g["zi0"]) + 12, "fond 1,8", "tx") if kind == "tiroir" else "",
              text(X(-2.5), V(Z1 + 6) - 4, "mur", "tx muted"),
              cote_h(X(0), X(fr), V(0) + 16, virg(fr)),
              cote_h(X(fr), X(P), V(0) + 16, f(P - fr)),
              cote_h(X(0), X(P), V(0) + 34, f(P)),
              cote_v(V(0), V(ZP), X(P) + 40, f(ZP)),
              cote_v(V(ZP), V(ZP + g["HC"]), X(P) + 40, virg(g["HC"])),
              cote_v(V(Z1 - g["ep_d"]), V(Z1), X(P) + 40, virg(g["ep_d"])),
              cote_v(V(0), V(Z1), X(P) + 62, f(Z1))]
        return s

    o += coupe(60, "porte")
    o += coupe(60 + (P + 40) * k + 40, "tiroir")
    w = 60 + 2 * (P + 40) * k + 40 + 10
    return svg(f"0 {f(V(Z1) - 44)} {f(w)} {f(Z1 * k + 44 + 46)}", "".join(o), "Coupes de profil de l'enfilade")


def dessus_svg(g=G):
    """Vue de dessus, dessus enlevé : caissons, pieds (tireté), portes ouvertes à 90° et tiroir sorti dans l'allée."""
    k, c = 3, M.CANAPE
    U = lambda y: (L - y) * k  # noqa: E731   vu de dessus, mur ouest en haut : le nord à droite
    rect = lambda x0, y0, x1, y1, cls: C.rect(min(x0, x1), min(y0, y1), max(x0, x1), max(y0, y1), cls)  # noqa: E731
    V = lambda x: x * k  # noqa: E731
    fr = DOS + PC
    bas_v = c["x0"] + 22
    o = [rect(U(-NORD), V(-5), U(L + NORD), V(0), "mur-h"), rect(U(-NORD - 5), V(-5), U(-NORD), V(bas_v), "mur-h"),
         text(U(L / 2), V(-5) - 4, "mur ouest (cloison du cellier et du WC)", "tx muted"),
         rect(U(-NORD), V(c["x0"]), U(c["p"] - NORD), V(bas_v), "sofa"),
         text(U(c["p"] / 2 - NORD), V(c["x0"]) + 30, "canapé (bout ouest)", "tx")]
    for kk, w in enumerate(g["W"]):
        y0, y1 = g["Y"][kk], g["Y"][kk + 1]
        o += [rect(U(y0), V(0), U(y1), V(DOS), "hdf"),
              rect(U(y0), V(DOS), U(y1), V(fr), cl_caisson()),
              rect(U(y0), V(DOS), U(y0 + EP), V(fr), "shelfc" if kk == 0 else "cab"),
              rect(U(y1 - EP), V(DOS), U(y1), V(fr), "shelfc" if kk == N - 1 else "cab"),
              text(U((y0 + y1) / 2), V(fr / 2) + 4, f"M{kk + 1}", "tb")]
    for y in g["pieds_y"]:
        for x in PIEDS_X:
            o.append(rect(U(max(y - 1.25, 0)), V(x - 1.25), U(min(y + 1.25, L)), V(x + 1.25), "acierh"))
    o.append(rect(U(0), V(0), U(L), V(P), "upper"))
    for fc in g["facades"]:
        if fc["type"] == "tiroir":
            if fc["z0"] == g["za"]:
                o.append(rect(U(fc["y0"]), V(P - FAC), U(fc["y1"]), V(P), "shelfc"))
            continue
        w = fc["y1"] - fc["y0"]
        if fc["charniere"] == "n":
            yh, sens = fc["y0"], 1
        else:
            yh, sens = fc["y1"], -1
        yf = yh + sens * w
        o += [rect(U(min(yh, yh - sens * FAC)), V(P), U(max(yh, yh - sens * FAC)), V(P + w), "porteo"),
              f'<path class="arc" d="M{f(U(yf))},{f(V(P))} A{f(w * k)},{f(w * k)} 0 0 {0 if sens > 0 else 1} '
              f'{f(U(yh))},{f(V(P + w))}"/>']
    tz = next(fc for fc in g["facades"] if fc["type"] == "tiroir")
    o += [rect(U(tz["y0"]), V(P), U(tz["y1"]), V(P + COULISSE + FAC), "porteo"),
          text(U((tz["y0"] + tz["y1"]) / 2), V(P + COULISSE / 2) + 4, f"tiroir sorti {virg(COULISSE + FAC)}", "tx")]
    # dégagements : allée de 60 jusqu'au canapé, reste devant la porte ouverte
    p2 = [fc for fc in g["facades"] if fc["type"] == "porte" and fc["k"] == 0][-1]
    wp = p2["y1"] - p2["y0"]
    o += [cote_v(V(P), V(c["x0"]), U(c["p"] / 2 - NORD), f'allée {f(c["x0"] - P)}'),
          cote_v(V(P + wp), V(c["x0"]), U(p2["y1"]) + 8, virg(c["x0"] - P - wp)),
          cote_h(U(0), U(L), V(-5) - 22, virg(L)),
          cote_v(V(0), V(fr), U(L) - 14, virg(fr)),
          cote_v(V(0), V(P), U(L) - 34, f(P)),
          text(U(0) - 2, V(bas_v) + 14, "dessus en tireté, pieds dessous en carrés tiretés", "tx muted", "end"),
          text(U(L) + 2, V(bas_v) + 14, "sud à gauche (vers le passage), nord à droite", "tx muted", "start")]
    return svg(f"{f(U(L) - 50)} {f(V(-5) - 40)} {f(U(-NORD - 5) - U(L) + 64)} {f(V(bas_v) - V(-5) + 62)}", "".join(o),
               "Vue de dessus de l'enfilade avec les ouvertures")


def eclate_svg(g=G):
    """Vue éclatée de face : trois caissons, vis de liaison, pieds, dessus (d'une pièce ou un par caisson)."""
    k, gap, lev = 2.6, 22, 24
    V = lambda z: (Z1 + lev - z) * k  # noqa: E731
    o = [FLECHE]
    xs = {}
    u = 0
    for kk in reversed(range(N)):                        # du sud (à gauche) au nord (à droite)
        xs[kk] = u
        u += g["W"][kk] * k + gap * k
    for kk in range(N):
        w, u0 = g["W"][kk], xs[kk]
        X = lambda y, u0=u0, w=w: u0 + (w - y) * k  # noqa: E731
        o += [rect(X(w), V(ZP + g["HC"]), X(0), V(ZP), "hdfl"),
              rect(X(w), V(ZP + g["HC"]), X(w - EP), V(ZP), "shelfc" if kk == N - 1 else cl_caisson()),
              rect(X(EP), V(ZP + g["HC"]), X(0), V(ZP), cl_caisson()),
              rect(X(w - EP), V(ZP + EP), X(EP), V(ZP), cl_caisson()),
              rect(X(w - EP), V(ZP + g["HC"]), X(EP), V(g["zi1"]), cl_caisson()),
              text(X(w / 2), V(ZP + g["HC"] / 2) + 4, f"caisson M{kk + 1}", "t"),
              text(X(w / 2), V(ZP + g["HC"] / 2) + 18, f'{virg(w)} × {virg(PC + DOS)} × {virg(g["HC"])}', "tx muted")]
        for y in (3, w - 3):
            o.append(rect(X(y + 1.25), V(ZP - 8), X(y - 1.25), V(-8), "mont"))
        if kk < N - 1:                                    # vis de liaison avec le caisson voisin (au sud)
            for z in (ZP + 8, ZP + g["HC"] - 8):
                o.append(f'<line class="fl2" x1="{f(X(w) - 4)}" y1="{f(V(z))}" x2="{f(X(w) - gap * k + 6)}" y2="{f(V(z))}"/>')
    for kk in range(N - 1):
        o += [text(xs[kk] - gap * k / 2, V(ZP + g["HC"] / 2) - 6, "4 vis", "tx"),
              text(xs[kk] - gap * k / 2, V(ZP + g["HC"] / 2) + 6, "de liaison", "tx")]
    tot = u - gap * k
    if DESSUS[1] == 1:
        o += [rect(0, V(Z1 + lev), tot, V(Z1 + lev - g["ep_d"]), "shelfc"),
              text(tot / 2, V(Z1 + lev) - 6, f'dessus d\'une pièce {virg(L)} × {f(P)} × {virg(g["ep_d"])}, posé sur équerres à trou oblong', "ts")]
    else:
        for kk in range(N):
            o.append(rect(xs[kk], V(Z1 + lev), xs[kk] + g["W"][kk] * k, V(Z1 + lev - g["ep_d"]), "shelfc"))
        o.append(text(tot / 2, V(Z1 + lev) - 6, f'un dessus par caisson, {virg(g["W"][0])} × {f(P)} × {virg(g["ep_d"])}, posé sur équerres à trou oblong', "ts"))
    o += [
          f'<line class="fl2" x1="{f(tot / 2)}" y1="{f(V(Z1 + lev - g["ep_d"]) + 3)}" x2="{f(tot / 2)}" y2="{f(V(ZP + g["HC"]) - 4)}"/>',
          text(tot / 2, V(-8) + 16, f'{len(g["pieds_y"]) * len(PIEDS_X)} pieds réglables : sous les bouts et à cheval sur chaque jonction', "ts")]
    return svg(f"-10 {f(V(Z1 + lev) - 24)} {f(tot + 20)} {f((Z1 + lev + 8) * k + 50)}", "".join(o),
               "Vue éclatée de l'enfilade")


def decoupe_svg(cle, pa, n, ps):
    """Un panneau : bandes refendues, pièces repérées, chutes en gris."""
    F, k = FORMATS[cle], 3.4
    cls = "shelfc" if F.get("bois") else "mel"
    o = [rect(0, 0, F["L"] * k, F["l"] * k, "chute")]
    for b in pa["bandes"]:
        for rep, lg, lr, x in b["poses"]:
            x0, y0, x1, y1 = x * k, b["y"] * k, (x + lg) * k, (b["y"] + lr) * k
            o.append(rect(x0, y0, x1, y1, cls))
            dims = f"{virg(lg)} × {virg(lr)}"
            xm, ym = (x0 + x1) / 2, (y0 + y1) / 2
            if lr * k >= 34:
                o += [text(xm, ym - 2, rep, "tb"), text(xm, ym + 14, dims, "ts")]
            elif lr * k >= 14:
                o.append(text(xm, ym + 4, f"{rep}  {dims}" if lg * k > 120 else rep, "ts"))
            else:
                o.append(text(xm, y1 + 12, f"{rep} ({dims})", "ts"))
    used = sum(lg * lr for b in pa["bandes"] for _, lg, lr, _ in b["poses"])
    cap = f'{F["court"]} n° {n} · {virg(F["L"], 0)} × {virg(F["l"], 0)} · chute {round(100 - 100 * used / (F["L"] * F["l"]))} %'
    return (f'<figure><figcaption>{escape(cap)}</figcaption>'
            + svg(f"-2 -12 {f(F['L'] * k + 4)} {f(F['l'] * k + 24)}", "".join(o), cap) + "</figure>")


# ------------------------------------------------------------------ sections HTML
def lien(url, txt):
    return f'<a href="{escape(url)}">{escape(txt)}</a>' if url else escape(txt)


def statut(s):
    return f'<span class="st{" est" if s == "estimé" else ""}">{s}</span>'


def section_meuble(ch):
    g = ch["g"]
    portes = [fc for fc in g["facades"] if fc["type"] == "porte"]
    l1 = portes[0]["y1"] - portes[0]["y0"]
    l3 = portes[-1]["y1"] - portes[-1]["y0"]
    vol = sum((w - 2 * EP) * (PC - 0) * (g["zi1"] - g["zi0"]) for w in g["W"]) / 1000
    return f"""<h2 id="meuble">Le meuble</h2>
<p>Trois caissons de {virg(g["W"][0])} posés côte à côte et liés par des vis, sur {len(g["pieds_y"]) * len(PIEDS_X)} pieds de {f(ZP)}, sous {"un dessus en chêne d'une pièce" if DESSUS[1] == 1 else f"{lettre(N)} dessus en chêne, un par caisson"}. Tout en chêne massif de {virg(EP)}, dedans comme dehors. Façades à fleur du dessus, sans poignée : on appuie pour ouvrir. Cotes extérieures du modèle conservées : {controle(g)}.</p>
<div class="fig"><div class="scroll">{face_svg(g)}</div>
<p class="cap">Vu de la pièce, regard vers l'ouest : le nord (mur, module M1) est à droite. Tireté sur les portes : la pointe montre le côté des charnières (cercles : coupelles Ø 35). Les tiretés verticaux marquent les jonctions des caissons{" et les joints du dessus" if DESSUS[1] > 1 else ""}. Six portes de {virg(l1)}{"" if abs(l1 - l3) < 0.05 else f" (M1) et {virg(l3)} (M3)"}, {virg(NORD)} libres entre le meuble et le mur nord ; jeux de {f(JEU * 10)} mm entre façades.</p></div>
<div class="fig"><div class="scroll">{profil_svg(g)}</div>
<p class="cap">Profil : dos de {virg(DOS)} vissé en applique, côtés de {virg(PC)}, tampons de {f(TAMPON * 10)} mm, façades de {virg(FAC)} : {f(P)} en tout. En M1, les vinyles tiennent debout sur le fond ({f(ETAGERES[0][0])} libres) ; l'équerre sous la traverse arrière retient le meuble au mur. En M2, trois boîtes de {f(H_BOITE)} sur coulisses de {f(COULISSE * 10)} à sortie totale. M3 est comme M1 avec deux étagères ({f(ETAGERES[2][0])} libres pour les assiettes et les plats, {f(ETAGERES[2][1])} pour les verres, le haut pour les tasses).</p></div>
<div class="fig"><div class="scroll">{dessus_svg(g)}</div>
<p class="cap">Vue de dessus, dessus enlevé : portes ouvertes à 90° (elles vont jusqu'à 110°) et tiroir sorti. La porte la plus large de M1 laisse {virg(M.CANAPE["x0"] - P - l1)} avant le canapé ; un tiroir sorti en laisse {virg(M.CANAPE["x0"] - P - COULISSE - FAC)}. Volume utile : {vol:.0f} litres environ.</p></div>
<div class="fig"><div class="scroll">{eclate_svg(g)}</div>
<p class="cap">Vue éclatée : chaque caisson se monte à l'atelier et passe seul dans le couloir ({virg(g["W"][0])} × {virg(PC + DOS)} × {virg(g["HC"])}) ; les trois se lient sur place, puis reçoivent les pieds et {"le dessus" if DESSUS[1] == 1 else "chacun son dessus"}.</p></div>"""


def section_iso(g=G):
    ps, po = pieces_3d(g=g), pieces_3d(ouvert=True, g=g)
    assert not chevauchements(ps) and not chevauchements(po)
    return f"""<h2 id="iso">Vue iso</h2>
<div class="fig"><div class="scroll">{C.iso_svg(ps, "Enfilade fermée, vue iso")}</div>
<p class="cap">L'enfilade fermée en vue isométrique, depuis la pièce, côté sud et en hauteur (le mur ouest au fond, le sud à gauche, le nord à droite ; étagères et mur non dessinés) : {"dessus d'une pièce en chêne" if DESSUS[1] == 1 else "trois dessus en chêne bord à bord"}, façades à fleur du dessus, joues nord et sud sans vis apparente, {virg(NORD)} libres à chaque bout, pieds noirs en retrait.</p></div>
<div class="fig"><div class="scroll">{C.iso_svg(po, "Enfilade ouverte, vue iso")}</div>
<p class="cap">Ouverte : la porte nord de M1 et la porte sud de M3 tournées à 90° sur leurs charnières, le tiroir du haut de M2 sorti de toute sa course ({f(COULISSE)}). On voit l'étagère de M1 ({f(ETAGERES[0][0])} libres dessous pour les vinyles), les deux étagères de M3, et la boîte du tiroir (chêne, fond en fibres dures). La porte nord de M3 et la porte sud de M1 restent fermées : ouvertes, elles heurteraient le tiroir sorti.</p></div>"""


def section_rendus():
    return f"""<h2 id="rendus">Rendus 3D</h2>
{C.rendus_html("enfilade", [("iso", "L'enfilade fermée en trois quarts depuis la pièce, sous les étagères du mur ouest."), ("ouverte", "Portes et tiroir ouverts : la porte nord de M1, la porte sud de M3, le tiroir du haut de M2 sorti.")])}"""


def section_construction(ch):
    g = ch["g"]
    return f"""<h2 id="construction">Construction</h2>
<h3>Trois caissons plutôt qu'un</h3>
<p>Un caisson d'une pièce de {virg(L)} ne passe pas facilement le couloir et demanderait des panneaux plus longs que les tablettes de chêne vendues ({f(FORMATS["C18"]["L"])} chez Weldom). Trois caissons de {virg(g["W"][0])}, un par module, se montent à plat, se portent à deux mains et se lient sur place par {lettre(4)} vis de liaison par jonction (Ø 5, à travers les deux côtés). La jonction fait {virg(2 * EP)} d'épaisseur : on ne la voit pas, elle tombe dans le jeu entre façades.</p>
<h3>Caisson</h3>
<p>Chêne lamellé-collé de 18, comme les façades : deux côtés (fil vertical), un fond entre les côtés, deux traverses de {f(TRAV)} en haut (avant et arrière) à la place d'un plafond, puisque le dessus couvre tout. Côtés et fond ont le fil en travers de la profondeur : ils travaillent ensemble, on peut les coller. Assemblage collé et vissé (vis bois 4 × 50, avant-trous Ø 3) ; les têtes sont cachées par le caisson voisin ou le dessus. Les deux bouts se voient ({virg(NORD)} libres de chaque côté) : le côté nord de M1 et le côté sud de M3 (joues) sont assemblés par tourillons et colle, sans vis apparente. Les chants vus devant sont du chêne poncé et huilé : rien à plaquer. Dos en fibres dures de {virg(DOS)} vissé en applique tous les 15 cm : il met le caisson d'équerre et le raidit.</p>
<h3>Dessus</h3>
<p>{lettre(N).capitalize()} pièces de chêne de {virg(DESSUS[0])}, une par caisson ({virg(g["W"][0])} × {f(P)}, {"dans toute la largeur des tablettes de 60 : leurs chants d'usine font le devant et l'arrière" if P >= FORMATS["C18"]["l"] else "refendues dans des tablettes de 60"}), posées bord à bord : les deux joints tombent au droit des jonctions des caissons, dans l'alignement des jeux entre façades. Un dessus d'une pièce de {virg(L)} n'existe en chêne fin qu'en plan de travail : 36 (variante F) ou 25 sur commande. Chaque pièce couvre son caisson et le haut de ses façades, à fleur devant, fixée par en dessous sur {lettre(4)} équerres à trou oblong : le bois massif bouge de 2 à 3 mm dans sa largeur avec les saisons, il doit pouvoir glisser. Les pieds réglés au niveau mettent les trois dessus dans le même plan ; deux tourillons Ø 8 non collés par joint les gardent affleurants. Huilés sur les deux faces pour qu'ils ne se cintrent pas.</p>
<h3>Socle : {len(g["pieds_y"]) * len(PIEDS_X)} pieds réglables</h3>
<p>Pieds carrés en acier noir de 15, platine de 6 × 6 vissée sous les fonds, patin fileté M10 pour rattraper le carrelage. Deux rangées ({f(PIEDS_X[0])} du mur et {virg(P - E["facade"] - PIEDS_X[1])} du nu du caisson, en retrait des façades) et quatre files : sous les deux bouts et à cheval sur chaque jonction, la platine vissée dans les deux fonds. Sans pied au milieu des jonctions, chaque fond de 18 porterait seul vaisselle et vinyles sur {virg(g["W"][0])} : huit pieds de 50 kg suffisent largement.</p>
<h3>Portes</h3>
<p>Chêne massif de 18, fil vertical, {lettre(2)} charnières invisibles Ø 35 à 110° en applique par porte, réglables en trois directions. Ouverture par poussoir magnétique (pas de poignée) : il faut alors des charnières sans amortisseur, sinon le poussoir ne repousse pas la porte. Avec {virg(NORD)} entre la joue nord et le mur, la porte nord s'ouvre à 110° sans toucher le mur : plus de fileur. Ouvertes, les portes de M1 prennent {virg(max(fc["y1"] - fc["y0"] for fc in g["facades"] if fc["k"] == 0))} des {f(M.CANAPE["x0"] - P)} de l'allée.</p>
<h3>Tiroirs</h3>
<p>Trois façades de {virg(next(fc for fc in g["facades"] if fc["type"] == "tiroir")["z1"] - g["za"])} de haut, boîtes en chêne de 18 (hauteur {f(H_BOITE)}, profondeur {f(COULISSE)}, fond en fibres dures vissé dessous), coulisses à billes de {f(COULISSE * 10)} à sortie totale et ouverture par pression, 25 kg par paire : les couverts d'une famille (5 kg avec le range-couverts) et le linge de table y tiennent sans peine. La façade se visse par l'intérieur de la boîte une fois les jeux réglés.</p>
<h3>Étagères</h3>
<p>Chêne de 18, {f(PROF_ETAGERE)} de profondeur (refendues dans des tablettes de 60, {virg(PC - PROF_ETAGERE)} en retrait des portes), sur taquets Ø 5 dans des rangées de trous tous les 3,2 cm : elles se déplacent. Les vinyles, lourds, restent sur le fond ; l'étagère de M1 ne porte que jeux et albums. Les trous évitent la hauteur des embases de charnières.</p>
<h3>Fixation au mur</h3>
<p>Une équerre acier par caisson, sous la traverse arrière, vissée dans la cloison à travers le dos : un tiroir sorti chargé ne doit pas faire basculer le meuble. La cloison (cellier, WC) n'est pas connue : chevilles Molly si c'est de la plaque de plâtre, chevilles nylon si c'est du carreau de plâtre ou de la brique. Les pieds restent à {f(PIEDS_X[0])} du mur : une plinthe de moins de {f(PIEDS_X[0] - 1.25)} d'épaisseur et de {f(ZP)} de haut passe dessous.</p>
<h3>Finition</h3>
<p>Huile dure incolore sur tout le chêne, dedans compris ({virg(ch["c"]["chene_m2"], 1)} m² de panneaux, {round(ch["c"]["chene_m2"] * 2, 1)} m² de faces), deux couches, toutes les faces avant montage, ponçage 120, 180, puis 240 entre les couches. Les dessus se ravivent d'une couche quand ils ont soif. L'intérieur huilé se nettoie à l'éponge à peine humide ; une huile spéciale plan de travail (contact alimentaire) va mieux dans le module des assiettes et des verres.</p>"""


def lettre(n):
    return ["zéro", "une", "deux", "trois", "quatre", "cinq", "six", "sept", "huit"][n] if n < 9 else str(n)


def section_materiaux(chs):
    a = next(c for c in chs if c["v"] is RETENUE)
    lignes = []
    for ch in chs:
        v = ch["v"]
        cais = "mélaminé blanc" if v["caisson"] == "mel" else FORMATS[v["caisson"]]["court"]
        des = (f'{FORMATS["PT36"]["court"]}, une pièce' if v["dessus"][1] == 1
               else f'{FORMATS[v["facade"]]["court"]}, {v["dessus"][1]} pièces')
        ecart = ch["total"] - a["total"]
        lignes.append(f'<tr class="{"retenu" if v.get("retenu") else ""}"><td><b>{v["cle"]}</b>'
                      f'{"<span class=badge>retenu</span>" if v.get("retenu") else ""}</td><td>{escape(v["nom"])}</td>'
                      f'<td>{escape(cais)}</td><td>{escape(FORMATS[v["facade"]]["court"])}</td><td>{escape(des)}</td>'
                      f'<td class="num">{euros(ch["total"])}</td>'
                      f'<td class="num">{"—" if v.get("retenu") else ("+" if ecart > 0 else "−") + euros(abs(ecart))}</td></tr>')
    b = next(ch for ch in chs if ch["v"]["cle"] == "B")
    f_ = next(ch for ch in chs if ch["v"]["cle"] == "F")
    return f"""<h2 id="materiaux">Matériaux</h2>
<p><b>Retenu ({a["v"]["cle"]})</b> : tout en chêne massif de 18, caissons, étagères et boîtes de tiroir compris, et un dessus de 18 en trois pièces plutôt que le plan de travail de 36, jugé trop épais. Le meuble ouvert est aussi chaud que fermé, et il n'y a qu'une matière à acheter, couper et huiler. Le chêne est du lamellé-collé massif (lames collées sur chant), pas du placage : il se ponce, s'huile et se répare.</p>
<div class="scroll"><table><thead><tr><th>Variante</th><th>Composition</th><th>Caisson</th><th>Façades</th><th>Dessus</th><th class="num">Total TTC</th><th class="num">Écart</th></tr></thead>
<tbody>{"".join(lignes)}</tbody></table></div>
<p class="note">Chaque total est recalculé avec la même quincaillerie et sa propre découpe (nombre de tablettes ou de plaques). Avec un dessus de 1,8 ({", ".join(c["v"]["cle"] for c in chs if c["v"]["dessus"][0] < 3)}), le caisson et les façades gagnent 1,8 de haut : la hauteur totale reste {f(Z1)}.</p>
<ul class="pistes">
<li><b>A et B, intérieur en mélaminé blanc</b> : le chêne seulement où il se voit (façades, dessus, joues). B (même dessus de 18 en trois pièces) coûte {euros(a["total"] - b["total"])} de moins que {a["v"]["cle"]} ; un intérieur blanc éclaire la vaisselle mais fait cuisine.</li>
<li><b>F, dessus d'une pièce de 36</b> : pas de joint, mais {euros(f_["total"] - a["total"])} de plus et un plateau deux fois plus épais que les façades.</li>
<li><b>D, contreplaqué</b> : caisson plus léger et plus raide que le mélaminé, chants de contreplaqué apparents (à huiler ou plaquer). Le contreplaqué de feuillus de 12 de Castorama (244 × 122, 84,90 €) est trop mince pour les coupelles de charnières (12 à 13 mm de profondeur).</li>
<li><b>E, tout mélaminé</b> : le moins cher, mais un décor chêne imprimé, des chants à plaquer partout et un dessus qui ne se ponce pas.</li>
<li>Autres dessus d'une pièce : Leroy Merlin vend un <a href="{LM_PT25}">plan chêne massif pleines lames 300 × 80 × 2,5</a> (385,19 € en promotion, livré en 8 jours, relevé en ligne), {euros(385.19 - FORMATS["C18"]["prix"] * 2)} de plus environ que les tablettes des trois dessus ; Castorama un plan de 300 × 62 × 4 (<a href="{CASTO_PT}">GoodHome</a>, 299,90 € hors promotion), plus épais encore ; les plans de 250 × 65 × 2,6 en chêne lamellé, d'une pièce, couvrent les {virg(L)} : 99 € chez Castorama (<a href="{CASTO_PT26}">fiche</a>, en rupture le 30/10/2026), 109 € chez Leroy Merlin (<a href="{LM_PT26}">fiche</a>), moins que deux tablettes ({euros(2 * FORMATS["C18"]["prix"])}) mais 2,6 d'épaisseur au lieu de 1,8. Pour des façades de 20 (l'épaisseur du modèle), Leroy Merlin vend une <a href="{LM_T20}">tablette chêne pleine lame 250 × 60 × 2</a> à 119 €.</li>
</ul>"""


# Buffet IKEA STOCKHOLM 2025, placage chêne, réf. 105.866.04 (fiche IKEA Belgique, relevée le 29/10/2026). IKEA ne
# publie que les cotes hors tout et l'intérieur des tiroirs : le volume intérieur est estimé (interieur).
STOCKHOLM = dict(nom="IKEA STOCKHOLM 2025", l=160.8, p=42.0, h=83.2, prix=599.00, tiroir=(68.5, 33.2),
                 interieur=(160.8 - 3 * 1.8, 42.0 - 4, 83.2 - 12 - 2 * 1.8),   # 2 côtés + 1 séparation, dos, socle
                 url="https://www.ikea.com/be/nl/p/stockholm-2025-buffetkast-eikenfineer-10586604",
                 url_fr="https://www.ikea.com/ca/fr/p/stockholm-2025-buffet-chene-plaque-10586604",
                 materiau="aggloméré plaqué chêne, vernis", contenu="2 tiroirs et 2 tablettes, ouverture par pression",
                 charges="15 kg par tablette, 10 kg par tiroir")


def comparaison_svg(g=G, autres=None, titre="Comparaison des dimensions avec le buffet IKEA STOCKHOLM 2025"):
    """Élévations de face à la même échelle, alignées au sol sur le même mur : l'enfilade, puis chaque meuble de
    autres = [(nom, longueur, profondeur, hauteur, pieds, plinthe, jonctions)] (défaut : le STOCKHOLM), centrés."""
    k, S = 2.6, STOCKHOLM
    V = lambda z: (90 - z) * k  # noqa: E731
    lt = NORD * 2 + L                                 # longueur du mur, du mur nord au cadre du passage
    autres = autres or [(S["nom"], S["l"], S["p"], S["h"], 12, False, [])]
    rangs = [("cette enfilade", L, P, Z1, ZP, False, [NORD + y for y in g["Y"][1:-1]])] + autres
    o = []
    for i, (nom, l, p, h, zp, plinthe, jonctions) in enumerate(rangs):
        dy, y0 = i * 120 * k, (lt - l) / 2
        o += [f'<line class="floorl" x1="0" y1="{f(V(0) + dy)}" x2="{f(lt * k)}" y2="{f(V(0) + dy)}"/>',
                rect(0, V(h + 6) + dy, 2 * k, V(0) + dy, "mur-h"), rect(lt * k - 2 * k, V(h + 6) + dy, lt * k, V(0) + dy, "mur-h"),
                rect(y0 * k, V(h) + dy, (y0 + l) * k, V(zp) + dy, "shelfc"),
                text((y0 + l / 2) * k, V(h) + dy - 8, f"{nom} : {virg(l)} × {virg(p)} × {virg(h)}", "t"),
                cote_h(0, y0 * k, V(0) + dy + 16, virg(y0)), cote_h((y0 + l) * k, lt * k, V(0) + dy + 16, virg(lt - y0 - l))]
        if plinthe:                                   # socle plein, en retrait de 2 sous le devant
            o.append(rect((y0 + 1) * k, V(zp) + dy, (y0 + l - 1) * k, V(0) + dy, "mont"))
        else:
            for y in (y0 + 4, y0 + l - 4):
                o.append(rect((y - 1.25) * k, V(zp) + dy, (y + 1.25) * k, V(0) + dy, "mont"))
        for y in jonctions:
            o.append(f'<line class="ouv" x1="{f(y * k)}" y1="{f(V(h) + dy)}" x2="{f(y * k)}" y2="{f(V(zp) + dy)}"/>')
    return svg(f"-10 {f(V(95))} {f(lt * k + 20)} {f(V(0) - V(95) + (len(rangs) - 1) * 120 * k + 40)}", "".join(o), titre)


def section_comparaison(ch):
    g, S = ch["g"], STOCKHOLM
    vol = sum((w - 2 * EP) * PC * (g["zi1"] - g["zi0"]) for w in g["W"]) / 1000
    vs = math.prod(S["interieur"]) / 1000
    lt = NORD * 2 + L
    lignes = [("Longueur", virg(L), virg(S["l"]), f"{'+' if L > S['l'] else '−'}{virg(abs(L - S['l']))}"),
              ("Profondeur", f(P), virg(S["p"]), f"+{virg(P - S['p'])}"),
              ("Hauteur", f(Z1), virg(S["h"]), f"−{virg(S['h'] - Z1)}"),
              ("Surface du dessus", f"{virg(L * P / 1e4, 2)} m²", f"{virg(S['l'] * S['p'] / 1e4, 2)} m²",
               f"× {virg(L * P / (S['l'] * S['p']), 1)}"),
              ("Volume intérieur", f"{vol:.0f} L", f"≈ {vs:.0f} L (estimé)", f"× {virg(vol / vs, 1)}"),
              ("Rangement", f"4 portes, 3 tiroirs, {len(g['etageres'])} étagères", S["contenu"], ""),
              ("Matière", "chêne massif de 18, huilé", S["materiau"], ""),
              ("Place sur le mur", f"{virg(NORD)} libres à chaque bout", f"{virg((lt - S['l']) / 2)} libres à chaque bout (centré)", ""),
              ("Prix", f"{euros(ch['total'])} de matériaux, à construire", f"{euros(S['prix'])}, à monter", f"+{euros(ch['total'] - S['prix'])}"),
              ("Prix au litre", f"{euros(ch['total'] / vol)}", f"≈ {euros(S['prix'] / vs)}", "")]
    rows = "".join(f"<tr><td>{escape(a)}</td><td>{escape(b)}</td><td>{escape(c)}</td><td class=\"num\">{escape(d)}</td></tr>"
                   for a, b, c, d in lignes)
    return f"""<h2 id="comparaison">Comparaison avec IKEA STOCKHOLM</h2>
<p>Le buffet <a href="{S["url_fr"]}">STOCKHOLM 2025</a> en chêne plaqué ({euros(S["prix"])} sur la <a href="{S["url"]}">fiche IKEA Belgique</a>, prix France non lu) est la référence du genre : même esprit, sans poignée, sur pieds.</p>
<div class="fig"><div class="scroll">{comparaison_svg(g)}</div>
<p class="cap">À la même échelle sur le mur ouest ({virg(lt)} entre le mur nord et le cadre du passage), les deux meubles centrés. Tiretés : jonctions des trois caissons.</p></div>
<div class="scroll"><table><thead><tr><th></th><th>Cette enfilade</th><th>{escape(S["nom"])}</th><th class="num">Écart</th></tr></thead>
<tbody>{rows}</tbody></table></div>
<p class="note">STOCKHOLM : cotes hors tout et intérieur des tiroirs ({virg(S["tiroir"][0])} × {virg(S["tiroir"][1])}) d'après la fiche IKEA, charges de {S["charges"]}. IKEA ne donne pas les cotes intérieures : le volume est estimé avec des panneaux de 1,8 (deux côtés, une séparation, dessus et fond), 4 de dos et 12 de pieds, soit {" × ".join(virg(v, 1) for v in S["interieur"])} utiles. Volume de l'enfilade : comme dans « Le meuble », sous les traverses.</p>
<ul class="pistes">
<li>Sur ce mur, un STOCKHOLM laisse {virg(lt - S["l"])} vides ; deux ({virg(2 * S["l"])}) ne tiennent pas.</li>
<li>L'enfilade range environ {virg(vol / vs, 1)} fois plus, pour {euros(ch["total"] - S["prix"])} de plus en matériaux, deux week-ends de travail et l'outillage. Elle est en chêne massif (se ponce, se répare), le STOCKHOLM en placage.</li>
<li>Elle est un peu plus basse ({f(Z1)} contre {virg(S["h"])}) et plus profonde ({f(P)} contre {virg(S["p"])}) : à hauteur égale des étagères au-dessus, elle laisse {virg(M.MONTANTS["z0"] - Z1)} sous les montants, le STOCKHOLM {virg(M.MONTANTS["z0"] - S["h"])}.</li>
</ul>"""


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


def ikea(nom, ref, q, pu, url, note, st="relevé"):
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
         note=f"chêne massif, d'une pièce, recoupé à {virg(240 + 2 * EP)} × {virg(METOD_CAISSON['prof'] + EP)} (découpe sur mesure proposée)"),
    dict(nom="Équerres de fixation à trou oblong (sachet de 4)", ref="à choisir", q=3, pu=3.90, st="estimé", url=None,
         ou="Weldom", note="plan vissé par en dessous dans les côtés des caissons ; le massif doit pouvoir glisser"),
    dict(nom="Huile dure incolore, bidon de 1 L", ref="à choisir", q=huile_l(_m2), pu=35.00, st="estimé", url=REF_HUILE,
         ou="Weldom", note=f"{virg(_m2, 1)} m² de chêne, deux couches, toutes faces"),
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


def section_metod(ch):
    g, Mx, Mt = ch["g"], METOD_MIXTE, METOD
    vol = sum((w - 2 * EP) * PC * (g["zi1"] - g["zi0"]) for w in g["W"]) / 1000
    interieur = (80 - 2 * 1.8, 57.5, 80 - 2 * 1.8)   # tablette UTRUSTA 76,4 × 57,5 ; côtés, fond et dessus de 1,8
    vm = 3 * math.prod(interieur) / 1000
    lt = NORD * 2 + L
    ecart = lambda v: f"{'+' if v > 0 else '−'}{virg(abs(v))}" if v else "="  # noqa: E731
    autres = [(Mx["nom"], Mx["l"], Mx["p"], Mx["h"], METOD_CAISSON["pieds"], True, [NORD + 80, NORD + 160])]
    lignes = [("Longueur", virg(L), f"{virg(Mx['l'])} (joues de {virg(Mx['joue'])} aux bouts)", ecart(round(Mx["l"] - L, 1))),
              ("Profondeur", f(P), f"{virg(Mx['p'])} (caisson {f(METOD_CAISSON['prof'])} sans rail, façade {virg(Mx['facade'])})",
               ecart(round(Mx["p"] - P, 1))),
              ("Hauteur", f(Z1), f"{virg(Mx['h'])} (pieds {f(METOD_CAISSON['pieds'])}, caisson {f(METOD_CAISSON['h'])}, plan {virg(Mx['dessus'])})",
               ecart(round(Mx["h"] - Z1, 1))),
              ("Volume intérieur", f"{vol:.0f} L", f"≈ {vm:.0f} L", f"× {virg(vm / vol, 2)}"),
              ("Rangement", f"4 portes, 3 tiroirs, {len(g['etageres'])} étagères", "4 portes, 3 tiroirs, 4 tablettes (2 par caisson)", ""),
              ("Ce qui se voit", "chêne massif de 18, huilé", "chêne massif huilé (façades, joues, plan), plinthe anthracite", ""),
              ("Intérieur", "chêne massif", "aggloméré mélaminé noir-gris, tiroirs en acier gris foncé", ""),
              ("Pieds", f"{len(g['pieds_y']) * len(PIEDS_X)} pieds acier noir de {f(ZP)}", f"12 pieds plastique de {f(METOD_CAISSON['pieds'])} derrière une plinthe", ""),
              ("Travail", "deux week-ends, outillage", "montage IKEA, découpe et huile du chêne, perçage des charnières", ""),
              ("Prix", f"{euros(ch['total'])}", f"{euros(Mx['total'])}", f"{'+' if Mx['total'] > ch['total'] else '−'}{euros(abs(Mx['total'] - ch['total']))}")]
    rows = "".join(f"<tr><td>{escape(a)}</td><td>{escape(b)}</td><td>{escape(c)}</td><td class=\"num\">{escape(d)}</td></tr>"
                   for a, b, c, d in lignes)
    postes = [("Caissons, tablettes", "METOD noir-gris", "les mêmes, achetés nus", "les pièces du système : perçages, pieds et tiroirs METOD s'y montent sans adaptation"),
              ("Tiroirs", "KNIVSHULT, coulisses amorties", "les mêmes", "55 à 70 € le tiroir, coulisses amorties comprises ; un tiroir maison demande caisson, coulisses et réglages"),
              ("Plan", f"VRENA chêne plaqué sur aggloméré 2,8, {euros(VRENA)}", f"chêne massif lamellé 2,6 Leroy Merlin, {euros(109)} brut",
               "massif (se ponce, se répare), plus mince, moitié prix ; à huiler"),
              ("Façades", "NICKEBO anthracite, film plastique sur aggloméré", "chêne massif de 18, débitées dans les tablettes Weldom",
               "les façades de l'enfilade ; un choc se ponce ; coupelles de charnière à percer"),
              ("Bouts", "côtés du caisson noir-gris", f"joues de chêne de {virg(Mx['joue'])}, du sol au plan", "le meuble se lit en chêne, pas en caisson de cuisine"),
              ("Charnières", "110° avec amortisseur (dans les combinaisons)", "UTRUSTA 95° sans amortisseur", "avec des poussoirs, l'amortisseur freine la poussée"),
              ("Pieds, plinthe, poussoirs", "METOD, FÖRBÄTTRA, UTRUSTA, KNIVSHULT", "les mêmes", "5 € la paire de pieds ; plinthe sur le devant seulement, les joues ferment les bouts")]
    choix = "".join(f"<tr><td>{escape(a)}</td><td>{escape(b)}</td><td>{escape(c)}</td><td>{escape(d)}</td></tr>" for a, b, c, d in postes)
    achats = "".join(f'<tr><td>{escape(x["nom"])}<br><span class="note">{escape(x["note"])}</span></td><td>{escape(x["ou"])}</td>'
                     f'<td class="mono">{escape(x["ref"])}</td><td class="num">{x["q"]}</td><td class="num">{euros(x["pu"])}</td>'
                     f'<td>{statut(x["st"])}</td><td>{lien(x["url"], "fiche") if x["url"] else "—"}</td><td class="num">{euros(x["q"] * x["pu"])}</td></tr>'
                     for x in Mx["postes"])
    achats += f'<tr class="tot"><td colspan="7">Total TTC</td><td class="num">{euros(Mx["total"])}</td></tr>'
    totaux = [("Tout IKEA : noir-gris, façades NICKEBO anthracite, plan VRENA", Mt["total"]),
              ("IKEA, sauf le plan en chêne massif Leroy Merlin", METOD_PLAN_LM),
              ("Mixte : IKEA dedans, chêne massif dehors (façades, joues, plan)", Mx["total"]),
              ("Cette enfilade (variante retenue)", ch["total"])]
    tot = "".join(f'<tr><td>{escape(n)}</td><td class="num">{euros(v)}</td><td class="num">'
                  f'{(("+" if v > ch["total"] else "−") + euros(abs(v - ch["total"]))) if v != ch["total"] else "—"}</td></tr>'
                  for n, v in totaux)
    noirs = "".join(f'<tr><td>{lien(IKEA_FR + u, n)}</td><td>{escape(d)}</td><td class="num">{euros(pu)}</td></tr>'
                    for n, pu, d, u in NOIRS)
    return f"""<h2 id="metod">Comparaison avec trois METOD 80</h2>
<p>Le même meuble sur trois caissons de cuisine IKEA METOD de 80 × 60 × 80, deux à portes (M1, M3) et un à trois tiroirs (M2), comme l'enfilade. Chaque poste est pris là où il vaut le mieux pour son prix : chez IKEA ce qui fait le système (caissons, tiroirs, charnières, poussoirs, pieds), ailleurs ce qui se voit (plan en chêne massif chez Leroy Merlin, façades et joues dans les tablettes de chêne de Weldom). Prix relevés en ligne le {METOD_RELEVE}.</p>
<div class="fig"><div class="scroll">{comparaison_svg(g, autres, "Comparaison des dimensions avec trois caissons METOD 80, composition mixte")}</div>
<p class="cap">À la même échelle sur le mur ouest ({virg(lt)}), centrés. METOD sur plinthe anthracite de {f(METOD_CAISSON["pieds"])}, joues et plan de chêne. Tiretés : jonctions des caissons.</p></div>
<div class="scroll"><table><thead><tr><th></th><th>Cette enfilade</th><th>{escape(Mx["nom"])}</th><th class="num">Écart</th></tr></thead>
<tbody>{rows}</tbody></table></div>
<h3>Poste par poste</h3>
<div class="scroll"><table><thead><tr><th>Poste</th><th>Tout IKEA</th><th>Mixte</th><th>Pourquoi</th></tr></thead>
<tbody>{choix}</tbody></table></div>
<div class="scroll"><table><thead><tr><th>Composition</th><th class="num">Total TTC</th><th class="num">Écart avec l'enfilade</th></tr></thead>
<tbody>{tot}</tbody></table></div>
<h3>Achats de la composition mixte</h3>
<div class="scroll"><table class="budget"><thead><tr><th>Poste</th><th>Où</th><th>Réf.</th><th class="num">Qté</th><th class="num">Prix unit.</th><th>Prix</th><th>Source</th><th class="num">Total</th></tr></thead>
<tbody>{achats}</tbody></table></div>
<p class="note">Façades aux cotes IKEA ({virg(80 - JEU_METOD)} × {virg(40 - JEU_METOD)} pour une porte de 40 × 80, faces de {virg(80 - JEU_METOD)} × {virg(20 - JEU_METOD)} et {virg(80 - JEU_METOD)} × {virg(40 - JEU_METOD)}), à vérifier sur la notice METOD. Dans chaque tablette de 200 × 60 : deux pièces de 80 de long, chacune de 40 et de 20 de large. Joues de 60 : elles s'arrêtent à {virg(round(Mx["p"] - 60, 1))} du mur. Volume METOD : intérieur du caisson ({" × ".join(virg(v) for v in interieur)}, d'après la tablette UTRUSTA et des panneaux de 1,8) ; tiroirs non déduits, comme pour l'enfilade.</p>
<ul class="pistes">
<li>Le plan VRENA est le plus mauvais poste du tout IKEA : {euros(VRENA)} pour un placage de chêne sur aggloméré. Le <a href="{LM_PT26}">plan brut en chêne lamellé 250 × 65 × 2,6</a> de Leroy Merlin, vendu par l'enseigne et disponible dans la plupart de ses magasins, coûte {euros(109)}, d'une pièce, en massif. Ce seul changement fait passer le tout IKEA à {euros(METOD_PLAN_LM)}. Castorama a le même format à 99 € (<a href="{CASTO_PT26}">fiche</a>), mais en rupture à Marseille St-Loup et en livraison le {METOD_RELEVE}.</li>
<li>Passer des façades NICKEBO aux façades et joues en chêne coûte {euros(abs(Mx["total"] - METOD_PLAN_LM))} de {"plus" if Mx["total"] > METOD_PLAN_LM else "moins"} (tablettes, huile, charnières et tablettes UTRUSTA achetées à part), pour un meuble qui se lit en chêne comme l'enfilade. Ce qui reste IKEA ne se voit qu'ouvert : mélaminé noir-gris et tiroirs en acier gris foncé, au lieu du chêne partout.</li>
<li>Prix : le mixte coûte {euros(Mx["total"])}, {euros(abs(Mx["total"] - ch["total"]))} de {"plus" if Mx["total"] > ch["total"] else "moins"} que l'enfilade, et range environ {virg(vm / vol, 2)} fois plus. Ce qu'on gagne : les caissons et les tiroirs tout faits, les plus longs à fabriquer. Il reste une journée de montage, la découpe de neuf pièces de chêne (scie circulaire ou découpe en magasin) et la recoupe du plan, l'huile et huit coupelles de Ø 35 à percer (mèche Forstner avec butée, dans l'outillage de l'enfilade).</li>
<li>Hauteur : {virg(Mx["h"])} au lieu de {f(Z1)}. Il reste {virg(round(M.MONTANTS["z0"] - Mx["h"], 1))} sous les montants des étagères au lieu de {virg(M.MONTANTS["z0"] - Z1)}. Le plan de 2,6 est plus mince que le VRENA (2,8) et que le plan de 3,6 jugé trop épais, mais plus épais que les dessus de 1,8 de l'enfilade.</li>
<li>Profondeur : {virg(Mx["p"])}, {virg(round(Mx["p"] - P, 1))} de plus que l'enfilade dans l'allée de {M.ALLEE_ENFILADE}. Sans rail de suspension, une équerre par caisson le tient au mur.</li>
<li>Pour un meuble noir, on garde les façades IKEA. Le noir lisse n'existe qu'en anthracite mat ; le vrai noir seulement en portes à cadre (porte 40 × 80, ikea.com/fr) :</li>
</ul>
<div class="scroll"><table><thead><tr><th>Porte 40 × 80</th><th>Aspect</th><th class="num">Prix</th></tr></thead>
<tbody>{noirs}</tbody></table></div>
<p class="note">À vérifier en magasin : les charnières UTRUSTA de 95° sur une porte de 1,8 (les portes IKEA font 1,6) ; le contenu d'un jeu de poussoirs KNIVSHULT ; la fixation des faces de chêne sur les tiroirs KNIVSHULT ; la teinte du caisson noir-gris dans les jeux entre façades.</p>"""


def section_debit(ch):
    lignes, grp = [], None
    v = ch["v"]
    for d in debit(ch["ps"]):
        if d["grp"] != grp:
            grp = d["grp"]
            lignes.append(f'<tr class="grp"><td colspan="7">{escape(GROUPES[grp])}</td></tr>')
        fmt = FORMATS[format_de(d, v)]
        lignes.append(f'<tr><td class="mono"><b>{d["rep"]}</b></td><td>{escape(d["nom"])}</td>'
                      f'<td class="num">{virg(d["L"])} × {virg(d["l"])}</td><td class="num">{virg(d["ep"])}</td>'
                      f'<td class="num">{d["n"]}</td><td>{escape(fmt["court"])}</td>'
                      f'<td>{escape(", ".join(d["ous"]))} · {escape(d["note"])}</td></tr>')
    plans = []
    for cle, pans in ch["cal"].items():
        plans.append(f'<h3>{escape(FORMATS[cle]["nom"])} × {len(pans)}</h3><div class="decoupes">'
                     + "".join(decoupe_svg(cle, pa, n + 1, ch["ps"]) for n, pa in enumerate(pans)) + "</div>")
    hdf = [d for d in debit(ch["ps"]) if d["grp"] == "fond"]
    surf = sum(d["L"] * d["l"] * d["n"] for d in hdf) / 1e4
    return f"""<h2 id="debit">Débit et découpe</h2>
<p>Cotes finies en cm, longueur dans le sens du fil (ou de la longueur de la tablette) × largeur. {len(ch["ps"])} pièces, {len(debit(ch["ps"]))} repères.</p>
<div class="scroll"><table><thead><tr><th>Rep.</th><th>Pièce</th><th class="num">L × l</th><th class="num">Ép.</th><th class="num">Qté</th><th>Matière</th><th>Où · note</th></tr></thead>
<tbody>{"".join(lignes)}</tbody></table></div>
<h3>Plan de découpe</h3>
<p>Refente d'abord (bandes sur la longueur), tronçonnage ensuite ; trait de scie de {f(TRAIT * 10)} mm compté. Mettre devant le chant le plus beau de chaque pièce. <span class="lg chene"></span>chêne <span class="lg chute"></span>chute.</p>
{"".join(plans)}
<p>Dos et fonds de tiroir ({", ".join(d["rep"] for d in hdf)}) : {virg(surf, 2)} m² de fibres dures, commandés découpés aux cotes chez Leroy Merlin. Les chutes de 15 × 200 laissées par les dessus et les étagères servent aux essais de teinte d'huile et aux cales. Faire couper en magasin si le service le prend, sinon scie circulaire sur rail.</p>"""


def section_achats(ch):
    nc18 = next(li["q"] for li in ch["lignes"] if li["poste"] == FORMATS["C18"]["nom"])
    rows = []
    mag = None
    for li in sorted(ch["lignes"], key=lambda li: (ORDRE_MAG.index(li["mag"]), not li["panneau"])):
        if li["mag"] != mag:
            mag = li["mag"]
            sous = sum(x["total"] for x in ch["lignes"] if x["mag"] == mag)
            rows.append(f'<tr class="grp"><td colspan="6">{lien(MAGASINS[mag]["url"], MAGASINS[mag]["nom"])}</td>'
                        f'<td class="num">{euros(sous)}</td></tr>')
        q = virg(li["q"], 1) + " m²" if li["unite"] == "m²" else str(li["q"])
        pu = euros(li["pu"]) + (" / m²" if li["unite"] == "m²" else "")
        src = lien(li["url"], "fiche" if li["statut"] == "relevé" else "repère") if li["url"] else "—"
        rows.append(f'<tr><td>{escape(li["poste"])}<br><span class="note">{escape(li["note"])}</span></td>'
                    f'<td class="mono">{escape(li["ref"])}</td><td class="num">{q}</td><td class="num">{pu}</td>'
                    f'<td>{statut(li["statut"])}</td><td>{src}</td><td class="num">{euros(li["total"])}</td></tr>')
    rows.append(f'<tr class="tot"><td colspan="6">Total TTC (variante {ch["v"]["cle"]})</td><td class="num">{euros(ch["total"])}</td></tr>')
    outil = "".join(f"<li>{escape(n)} : {euros(p)} (estimé)</li>" for n, p in OUTILLAGE)
    return f"""<h2 id="achats">Achats et prix</h2>
<p>Weldom Marseille Saint-Barnabé d'abord, puis Leroy Merlin pour ce que Weldom n'a pas (fibres dures découpées, pieds, coulisses). Prix TTC recherchés en ligne le {RELEVE}, sans visite en magasin : <span class="st">relevé</span> = prix lu en ligne ou déjà connu, <span class="st est">estimé</span> = ordre de grandeur à relever en rayon.</p>
<div class="scroll"><table class="budget"><thead><tr><th>Poste</th><th>Réf.</th><th class="num">Qté</th><th class="num">Prix unit.</th><th>Prix</th><th>Source</th><th class="num">Total</th></tr></thead>
<tbody>{"".join(rows)}</tbody></table></div>
<p><b>Total : {euros(ch["total"])}</b>, dont {euros(ch["releve"])} de prix relevés ({round(100 * ch["releve"] / ch["total"])} %) et {euros(ch["estime"])} d'estimations. Les {next(li["q"] for li in ch["lignes"] if li["poste"] == FORMATS["C18"]["nom"])} tablettes de chêne en font {euros(next(li["total"] for li in ch["lignes"] if li["poste"] == FORMATS["C18"]["nom"]))} ; l'huile, {euros(next(li["total"] for li in ch["lignes"] if li["poste"].startswith("Huile")))} (rendement estimé de {HUILE["rendement"]} m² par litre et par couche).</p>
<p>Outillage, seulement si l'atelier ne l'a pas (hors total) :</p><ul class="pistes">{outil}</ul>
<p class="note">Weldom ne vend ni plaques entières ni 12 mm : tout le débit Weldom se fait dans des tablettes. Les prix Weldom des tablettes et des charnières sont ceux déjà relevés, à reconfirmer au magasin (stock non lu : il faut {lettre(nc18)} tablettes de chêne de 200 × 60, à choisir bien planes et de teinte voisine). Fiches Weldom : chercher la référence sur <a href="https://www.weldom.fr/">weldom.fr</a>.</p>"""


def section_montage(ch):
    g = ch["g"]
    etapes = [
        "Faire débiter : refentes et tronçonnages du plan de découpe (service découpe du magasin, ou scie circulaire sur rail). Commander dos et fonds de tiroir découpés. Marquer chaque pièce de son repère au crayon, sur une face cachée.",
        "Chêne : poncer 120 puis 180, huiler deux couches toutes faces (égrener au 240 entre les couches), laisser sécher selon la notice avant de manipuler.",
        "Percer à plat, avant d'assembler : rangées de trous Ø 5 pour les taquets (gabarit, foret à butée, 12 mm de profondeur) dans les côtés de M1 et M3, coupelles Ø 35 dans les portes (axe à 2,2 du chant, à 10 du haut et du bas, 12 mm de profondeur), embases de charnières et coulisses sur les côtés.",
        "Monter chaque caisson : fond et traverses entre les côtés, collés et vissés 4 × 50 avec avant-trous Ø 3 (trois par about de fond, deux par traverse). Joue nord de M1 et joue sud de M3 par tourillons Ø 8 collés. Contrôler l'équerrage (diagonales égales).",
        "Visser le dos (fibres dures) en applique, vis 3,5 × 16 tous les 15 cm, caisson d'équerre : le caisson devient rigide.",
        "Tiroirs : boîtes vissées 4 × 50, fond vissé dessous ; coulisses sur les côtés de M2 et sur les boîtes ; essayer à vide.",
        "Sur place : poser les trois caissons sur le dos (sur une couverture), les aligner, serre-joints, percer Ø 5 à travers les deux côtés et poser quatre vis de liaison par jonction.",
        f"Visser les {len(g['pieds_y']) * len(PIEDS_X)} pieds (platines vissées 3,5 × 16, à cheval sur les jonctions), redresser, pousser contre le mur, régler les patins au niveau sur toute la longueur ; centrer le meuble sur le mur ({virg(NORD)} de chaque côté).",
        "Fixer au mur : une équerre sous chaque traverse arrière, chevilles adaptées à la cloison.",
        "Poser les trois dessus, un par caisson, bord à bord : deux tourillons Ø 8 non collés par joint pour l'affleurement, équerres à trou oblong sous les traverses (trou oblong en travers du fil), vis 3,5 × 30 dans le dessus, sans colle.",
        "Portes : clipser sur les embases, régler les jeux de 3 mm ; poser poussoirs et tampons. Façades de tiroir : caler les jeux, visser par l'intérieur 3,5 × 30. Taquets et étagères en dernier.",
    ]
    outils = ["perceuse-visseuse, forets bois Ø 3, 5 et 8, mèche Forstner Ø 35", "scie circulaire sur rail (ou découpe en magasin), scie sauteuse",
              "4 serre-joints, équerre, mètre, niveau, compas", "ponceuse orbitale et abrasifs, chiffons pour l'huile", "gabarit de perçage des taquets (ou tasseau percé)"]
    return f"""<h2 id="montage">Outils et montage</h2>
<h3>Outils</h3><ul class="pistes">{"".join(f"<li>{escape(o)}</li>" for o in outils)}</ul>
<h3>Étapes</h3><ol class="etapes">{"".join(f"<li>{escape(e)}</li>" for e in etapes)}</ol>
<p class="note">Compter deux week-ends : un pour la découpe, le ponçage et l'huile (séchage), un pour l'assemblage et la pose. Deux personnes pour la mise en place : un caisson en chêne pèse {round(g["W"][0] * (PC * g["HC"] * 2 + PC * g["W"][0] + TRAV * g["W"][0] * 2) * EP * 0.7 / 1000)} kg environ, vide et sans façades.</p>"""


def section_valider(ch, chs):
    nc18 = next(li["q"] for li in ch["lignes"] if li["poste"] == FORMATS["C18"]["nom"])
    g = ch["g"]
    f_ = next(c for c in chs if c["v"]["cle"] == "F")
    p1 = [fc for fc in g["facades"] if fc["k"] == 0][0]
    p3 = [fc for fc in g["facades"] if fc["type"] == "porte"][-1]
    pts = [
        f"Dessus de {virg(DESSUS[0])} en trois pièces, deux joints au droit des jonctions ; d'une pièce, il faudrait le plan de 3,6 (variante F, {euros(f_['total'] - ch['total'])} de plus) ou celui de 2,5 livré par Leroy Merlin.",
        f"Les façades s'arrêtent sous le dessus, à {virg(g['zb'])} (le modèle les montre jusqu'à {virg(Z1 - 0.2)}).",
        "Intérieur en chêne huilé plutôt qu'en mélaminé : choisir une huile pour contact alimentaire pour le module de la vaisselle.",
        f"Meuble centré sur le mur, {virg(NORD)} libres à chaque bout (à garder libres ou pour un pied de lampe fin côté passage) ; portes de {virg(p1['y1'] - p1['y0'])}.",
        f"{len(g['pieds_y']) * len(PIEDS_X)} pieds carrés noirs de 2,5 au lieu de 4 pieds ronds : forme et couleur (chêne possible, non réglable, plus cher).",
        "Ouverture par pression (poussoirs, coulisses à ouverture par pression) ou poignées discrètes ; la charnière Weldom 9154863 doit être sans amortisseur pour les poussoirs, et son prix de 5,35 € s'entendre à l'unité.",
        f"Chêne massif de 18 pour des portes de {virg(p3['z1'] - p3['z0'], 0)} × {virg(p3['y1'] - p3['y0'], 0)} et des dessus de {virg(g['W'][0], 0)} × {f(P)} : risque de léger tuilage ; choisir des tablettes bien planes, huiler les deux faces pareil.",
        "Nature de la cloison ouest (chevilles), hauteur et épaisseur de la plinthe derrière le meuble.",
        f"Service de découpe des tablettes chez Weldom à confirmer, et {lettre(nc18)} tablettes de chêne 200 × 60 en stock.",
        "Coulisses de 500 à ouverture par pression et poussoirs : références à choisir en rayon, prix estimés.",
        "Table ouverte rangée debout dans l'allée devant M1 : elle bloque alors les portes de M1.",
        "Dos en fibres dures brut (brun) visible à l'intérieur, à côté du chêne : contreplaqué chêne de 3 ou 4 mm plus cher, à chiffrer si le brun dérange.",
    ]
    return f"""<h2 id="valider">Points à valider</h2>
<ul class="pistes">{"".join(f"<li>{escape(p)}</li>" for p in pts)}</ul>"""


def page():
    chs = [chiffrage(v) for v in VARIANTES]
    ch = next(c for c in chs if c["v"] is RETENUE)
    corps = f"""{STYLE}
<div class="kicker">Salon · Enfilade · {VERSION}</div>
<h1>Enfilade du mur ouest</h1>
<p class="pitch">Le meuble bas de {virg(L)} × {f(P)} × {f(Z1)} sous les étagères, à construire soi-même, tout en chêne massif de 18 huilé : trois caissons liés sur place, chacun sous son dessus, façades sans poignée, huit pieds réglables. Environ {round(ch["total"], -1):.0f} € de matériaux.</p>

{section_iso(ch["g"])}

{section_meuble(ch)}

{section_rendus()}

{section_construction(ch)}

{section_materiaux(chs)}

{section_comparaison(ch)}

{section_metod(ch)}

{section_debit(ch)}

{section_achats(ch)}

{section_montage(ch)}

{section_valider(ch, chs)}

<p class="note">Page générée depuis <span class="mono">3d/salon/modele.py</span> ({M.VERSION}) par <span class="mono">3d/salon/enfilade.py</span> (<span class="mono">just salon</span>). Plan du salon : <a href="{C.SALON}">{C.SALON}</a>.</p>

<section id="changements">
<h2>Changements</h2>
<div class="scroll"><table><thead><tr><th>Version</th><th>Date</th><th>Changements</th></tr></thead>
<tbody><tr><td class="mono">V1.0</td><td class="mono">29/10/2026</td><td>Première version : construction en trois caissons (mélaminé blanc, chêne massif visible, dessus d'une pièce de 3,6), élévation, coupes, vue de dessus, vue éclatée, débit repéré et plan de découpe, achats avec prix relevés et estimés, cinq variantes de matériau, montage, points à valider.</td></tr>
<tr><td class="mono">V1.1</td><td class="mono">29/10/2026</td><td>Vue iso fermée et ouverte (une porte de M1 et une de M3 à 90°, tiroir du haut de M2 sorti), tirée des mêmes cotes que le débit ; section Rendus 3D (rendus Blender à produire).</td></tr>
<tr><td class="mono">V1.2</td><td class="mono">29/10/2026</td><td>Variante C retenue, tout en chêne massif de 18 (caissons, étagères et boîtes de tiroir) ; le dessus de 3,6 (trop épais) remplacé par trois dessus de 1,8, un par caisson, joints au droit des jonctions ; l'ancienne C (dessus de 3,6) devient la variante F ; huile chiffrée selon la surface de chêne ; vues et vue iso avec caissons en chêne et dessus en trois pièces. Rendus 3D non refaits.</td></tr>
<tr><td class="mono">V1.3</td><td class="mono">29/10/2026</td><td>Trois caissons de 80 (240 au lieu de 257,6), centrés sur le mur ouest avec {virg(NORD)} libres à chaque bout (salon {M.VERSION}) ; plus de fileur, six portes identiques, joue nord en M1 comme au sud ; comparaison avec le buffet IKEA STOCKHOLM 2025.</td></tr>
<tr><td class="mono">V1.4</td><td class="mono">30/10/2026</td><td>Comparaison avec trois caissons IKEA METOD 80 × 37 en noir-gris, façades NICKEBO anthracite mat, même dessus en chêne : dimensions, volume, achats (946,30 €, prix relevés sur ikea.com/fr), façades noires possibles (NICKEBO, UPPLÖV, LERHYTTAN, BODBYN).</td></tr>
<tr><td class="mono">V1.5</td><td class="mono">30/10/2026</td><td>Profondeur de 60 au lieu de 45 (salon V4.26) : côtés de 57,68, dessus de 60 dans toute la largeur des tablettes, étagères de 55, coulisses de 500 ; total de 1 027,95 €. Comparaisons revues : STOCKHOLM recalculé ; METOD en caissons de 80 × 60 (le troisième, à tiroirs, assemblé pièce à pièce), dessus VRENA de 2,8 car le chêne de 60 ne couvre pas ses 61,6, 1 023,50 €.</td></tr>
<tr><td class="mono">{VERSION}</td><td class="mono">{DATE}</td><td>Comparaison METOD en composition mixte, chaque poste pris là où il vaut le mieux : caissons, tiroirs, charnières 95° sans amortisseur, poussoirs et pieds chez IKEA ; plan en chêne massif lamellé 250 × 65 × 2,6 de Leroy Merlin ({euros(109)}, au lieu du VRENA plaqué à {euros(VRENA)}) ; façades et joues en chêne de 18 dans les tablettes Weldom. Profondeur sans rail de suspension (caisson de 59) : {virg(METOD_MIXTE["p"])}. Totaux : mixte {euros(METOD_MIXTE["total"])}, tout IKEA {euros(METOD["total"])}, IKEA avec le plan Leroy Merlin {euros(METOD_PLAN_LM)}. Matériaux : le plan de 250 × 65 × 2,6 n'est plus trop court pour les 240 de l'enfilade.</td></tr></tbody></table></div>
</section>"""
    return C.gabarit("Enfilade · salon", "enfilade", corps), chs


if __name__ == "__main__":
    print("contrôle des cotes :", controle())
    for o in (False, True):
        assert not chevauchements(pieces_3d(ouvert=o)), chevauchements(pieces_3d(ouvert=o))
    html, chs = page()
    for c in chs:
        print(f'variante {c["v"]["cle"]} : {euros(c["total"])}  (relevé {euros(c["releve"])}, estimé {euros(c["estime"])})')
    C.ecrire("salon-enfilade.html", html)
