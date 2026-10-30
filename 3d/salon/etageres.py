# Génère salon-etageres.html : les étagères sur montants percés du salon, meuble constructible (même principe que
# le meuble linge SDB) : dispositions, le meuble, présentoir, matériaux, débit et découpe, charges et
# fixation, achats et prix, montage.
#
#   python3 3d/salon/etageres.py
#
# La géométrie vient de modele.py (section ② étagères sur montants percés, DISPOSITIONS) ; ce fichier garde les
# données de fabrication (pièces, débit, quincaillerie, prix, sources). Le HTML est seulement généré. Chaque vue qui
# dépend de la disposition est produite pour toutes (blocs .dv[data-d]) et suit le bouton Disposition de la barre.

import json
import math
import os
import sys
from html import escape
from types import SimpleNamespace

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import commun as C  # noqa: E402
import modele as M  # noqa: E402

f, rect, text, cote_h, cote_v = C.f, C.rect, C.text, C.cote_h, C.cote_v
VERSION = "V1.8"
DATE = "29/10/2026"          # relevé des prix (WebSearch, fiches en ligne ; stock non vérifié)
MO, ET, EN, EU = M.MONTANTS, M.ETAGERES, M.ENFILADE, M.ETUDE_MONTANTS
PAS = MO["pas"]


def cm(v):
    """Cote en cm : 1 décimale au plus, virgule."""
    return f"{round(v, 1):g}".replace(".", ",")


def euros(v):
    return f"{v:.2f}".replace(".", ",") + " €"


def poly(cls, pts):
    return f'<polygon class="{cls}" points="{" ".join(f"{f(u)},{f(v)}" for u, v in pts)}"/>'


RA = ET["rainure"]
RA_COTE = (RA["long"] - ET["entaille"][0]) / 2     # longueur de rainure de chaque côté d'une entaille


# ------------------------------------------------------------------ dispositions
def tablettes(dispo):
    """Tablettes d'une disposition, repérées T1… du bas vers le haut (puis du sud au nord)."""
    ts = []
    for z, a, b in dispo["tablettes"]:
        zs = [z] * (b - a + 1)
        assert all(M.NIVEAUX[0] <= v <= M.NIVEAUX[1] and (v - M.NIVEAUX[0]) % MO["pas_trous"] == 0 for v in zs), zs
        y0, y1 = MO["axes"][a] - ET["debord"], MO["axes"][b] + ET["debord"]
        t = dict(z=z, a=a, b=b, zs=zs, y0=y0, y1=y1, lh=y1 - y0, l=y1 - y0, n=b - a + 1, type=cm(y1 - y0))
        t["entailles"] = [y1 - MO["axes"][k] for k in range(b, a - 1, -1)]   # depuis le bout sud
        ts.append(t)
    ts.sort(key=lambda t: (min(t["zs"]), -t["y1"]))
    for i, t in enumerate(ts):
        t["rep"] = f"T{i + 1}"
    return ts


def zm(t, k):
    """Dessus moyen de t sur la travée k (entre les montants k et k + 1)."""
    return (t["zs"][k - t["a"]] + t["zs"][k + 1 - t["a"]]) / 2


def controle(ts, cle):
    """Règles de composition : même travée → 25 au moins d'un dessus à l'autre (≈ 21 de libre) ; même montant
    seulement (débords l'un au-dessus de l'autre) → 15 ; sinon même hauteur possible (bouts à 31)."""
    for i, s in enumerate(ts):
        for t in ts[i + 1:]:
            tr = set(range(s["a"], s["b"])) & set(range(t["a"], t["b"]))
            mo = set(range(s["a"], s["b"] + 1)) & set(range(t["a"], t["b"] + 1))
            if tr:
                dz = min(abs(s["zs"][j - s["a"]] - t["zs"][j - t["a"]]) for k in tr for j in (k, k + 1))
                assert dz >= 25, f"{cle} : {s['rep']} / {t['rep']} sur la même travée à {dz}"
            elif mo:
                j = mo.pop()
                assert abs(s["zs"][j - s["a"]] - t["zs"][j - t["a"]]) >= 15, f"{cle} : {s['rep']} / {t['rep']} en M{j + 1}"


def libres(ts):
    """Hauteur libre au-dessus de chaque tablette, travée par travée (jusqu'à la tablette du dessus ou au plafond)."""
    for t in ts:
        t["libres"] = []
        for k in range(t["a"], t["b"]):
            dessus = [zm(u, k) for u in ts if u is not t and u["a"] <= k < u["b"] and zm(u, k) > zm(t, k)]
            t["libres"].append((min(dessus) - zm(t, k) - ET["ep"], False) if dessus else (M.H - zm(t, k), True))


# bruts achetés (sections du commerce) et traits de scie
PANNEAU = dict(l=250, p=65, ep=2.6, nom="plan de travail chêne massif lamellé-collé abouté 250 × 65 × 2,6")
TASSEAU = dict(l=239, s=(4.4, 6.9), nom="tasseau sapin du Nord raboté 240 × 69 × 44 (longueur réelle 2,39)")
ROND = dict(l=100, d=1.0, nom="rond plein acier Ø 10 × 1 m")
KERF, KERF_METAL, DRESSAGE = 0.3, 0.15, 0.5   # scie circulaire, scie à métaux, recoupe d'équerre des bouts de panneau
RECHANGE_CHEVILLES = 4                           # chevilles de rechange au moins (une se perd)
L_MONTANT = MO["z1"] - MO["z0"]
BANDE = PANNEAU["l"] - DRESSAGE                  # longueur utile d'une bande refendue


def bandes(ts):
    """Refente des panneaux en bandes de la profondeur des tablettes, puis rangement des tablettes dans les bandes
    (plus longue d'abord, première bande où elle entre). Renvoie la liste des panneaux, chacun liste de bandes,
    chacune liste de tablettes."""
    par_panneau = int((PANNEAU["p"] + KERF) // (ET["p"] + KERF))
    libre = []       # [longueur restante, panneau, bande]
    pose = []
    for t in sorted(ts, key=lambda t: -t["l"]):
        for b in libre:
            if b[0] >= t["l"] + KERF:
                b[0] -= t["l"] + KERF
                pose[b[1]][b[2]].append(t)
                break
        else:
            if not pose or len(pose[-1]) == par_panneau:
                pose.append([])
            pose[-1].append([t])
            libre.append([BANDE - t["l"] - KERF, len(pose) - 1, len(pose[-1]) - 1])
    return pose


def barres(longueur, l_piece, n, kerf):
    """Pièces identiques dans des barres : nombre par barre, nombre de barres."""
    par = int((longueur + kerf) // (l_piece + kerf))
    return par, -(-n // par)


PAR_TASSEAU, N_TASSEAUX = barres(TASSEAU["l"], L_MONTANT, MO["n"], KERF)
N_VIS = MO["n"] * EU["vis"]

# charges : part de chaque tablette reprise par chaque montant (poutre continue sur appuis égaux, charge uniforme ;
# coefficients des réactions × pas, plus le débord aux deux bouts)
COEF = {1: (0.5, 0.5), 2: (0.375, 1.25, 0.375), 3: (0.4, 1.1, 1.1, 0.4), 4: (0.393, 1.143, 0.929, 1.143, 0.393)}
KG_M = M.CHARGE_LIVRES + ET["p"] / 100 * ET["ep"] / 100 * 700        # kg par mètre de tablette pleine, chêne compris
KG_MONTANT = L_MONTANT / 100 * MO["l"] / 100 * MO["p"] / 100 * 450


def charges(ts):
    par, tmax = [0.0] * MO["n"], 0
    for t in ts:
        cs = COEF[t["n"] - 1]
        for i, k in enumerate(range(t["a"], t["b"] + 1)):
            trib = cs[i] * PAS + (ET["debord"] if i in (0, t["n"] - 1) else 0)
            par[k] += trib / 100 * KG_M
            tmax = max(tmax, trib)
    par = [v + KG_MONTANT for v in par]
    k = max(range(MO["n"]), key=lambda i: par[i])
    return dict(par=par, max=par[k], m=k, poids=sum(par), trib=tmax, facteur=tmax / PAS)


def etat(dispo):
    ts = tablettes(dispo)
    controle(ts, dispo["cle"])
    libres(ts)
    e = SimpleNamespace(cle=dispo["cle"], nom=dispo["nom"], idee=dispo["idee"], ts=ts)
    e.types = {}
    for t in sorted(ts, key=lambda t: -t["lh"]):
        d = e.types.setdefault(t["type"], dict(type=t["type"], nb=0, l=t["l"], lh=t["lh"], n=t["n"]))
        d["nb"] += 1
    e.kit = " + ".join(f'{d["nb"]} × {d["type"]}' for d in e.types.values())
    e.n_tailles = len({d["lh"] for d in e.types.values()})
    e.panneaux = bandes(ts)
    e.entailles = sum(t["n"] for t in ts)
    e.chevilles = 2 * e.entailles
    e.par_rond, e.n_ronds = barres(ROND["l"], ET["cheville"], e.chevilles + RECHANGE_CHEVILLES, KERF_METAL)
    e.metres = sum(t["lh"] for t in ts) / 100
    e.niveaux = sorted({z for t in ts for z in t["zs"]})
    e.ch = charges(ts)
    e.surf_huile = sum(t["l"] * (2 * ET["p"] + 2 * ET["ep"]) + 2 * ET["p"] * ET["ep"] for t in ts) / 1e4   # m²
    e.achats = achats(e)
    e.total = round(sum(a["total"] for a in e.achats), 2)
    e.releve = round(sum(a["total"] for a in e.achats if a["statut"] == "relevé"), 2)
    e.estime = round(e.total - e.releve, 2)
    libs = [v for t in ts for v, plafond in t["libres"] if not plafond]
    e.libre_min, e.libre_max = min(libs), max(libs)
    return e


# ------------------------------------------------------------------ achats (prix TTC, DATE)
# statut : « relevé » (prix lu sur la fiche en ligne) ou « estimé » ; magasins dans l'ordre Weldom, Leroy Merlin,
# Castorama ; stock non vérifié (à faire en magasin).
MAGASINS = {
    "weldom": dict(nom="Weldom Marseille Saint-Barnabé", adresse="90 rue François Scaramelli, 13012 Marseille",
                   url="https://www.weldom.fr/m/weldom-marseille-saint-barnabe"),
    "leroy": dict(nom="Leroy Merlin", adresse="", url="https://www.leroymerlin.fr/"),
    "castorama": dict(nom="Castorama", adresse="", url="https://www.castorama.fr/"),
}
SURF_PEINT = MO["n"] * L_MONTANT * 2 * (MO["l"] + MO["p"]) / 1e4                                         # m²


def achats(e):
    lst = [
        dict(poste="Montants", article="Tasseau sapin du Nord raboté 240 × 69 × 44, petits nœuds (2,39 m)",
             ref="9000489", magasin="weldom", qte=N_TASSEAUX, pu=14.10, statut="relevé",
             url="https://www.weldom.fr/p/tasseau-sapin-nord-240x69x44-9000489"),
        dict(poste="Tablettes", article="Plan de travail chêne massif lamellé-collé abouté 250 × 65 × 2,6 (≈ 30,8 kg)",
             ref="3428350070417", magasin="castorama", qte=len(e.panneaux), pu=99.00, statut="relevé",
             url="https://www.castorama.fr/plan-de-travail-en-chene-massif-l-250-x-l-65-x-ep-2-6-cm/3428350070417_CAFR.prd",
             note="éco-participation de 2,30 € peut-être en sus ; plan absent chez Weldom en 2,6"),
        dict(poste="Chevilles", article="Rond plein acier brut Ø 10, 1 m", ref="9143366", magasin="weldom",
             qte=e.n_ronds, pu=9.00, statut="relevé",
             url="https://www.weldom.fr/p/rond-plein-acier-brut-l-1-m-x-diam-10-mm-9143366",
             note="rond plein, pas le tube creux de même diamètre"),
        dict(poste="Fixation", article="Lot de 75 vis acier tête fraisée Torx Spax 6 × 120", ref="9157887",
             magasin="weldom", qte=1, pu=27.90, statut="relevé",
             url="https://www.weldom.fr/p/lot-de-75-vis-acier-tete-fraisee-torx-spax-diam-6-mm-x-l-120-mm-9157887",
             note=f"{N_VIS} utiles ; pour un mur plein ou en carreaux de plâtre"),
        dict(poste="Fixation", article="Cheville nylon multimatériaux Standers 8 × 50, sachet de 8", ref="5589927",
             magasin="weldom", qte=-(-N_VIS // 8), pu=4.19, statut="relevé", url=None,
             note="prix relevé le 26/10/2026 pour le meuble SDB ; à remplacer selon la cloison"),
        dict(poste="Finition", article="Laque boiserie Valénite Dulux Valentine noir mat 0,5 L (glycéro)", ref="5592757",
             magasin="weldom", qte=1, pu=27.70, statut="relevé",
             url="https://www.weldom.fr/p/peinture-laque-boiserie-valenite-dulux-valentine-noir-mat-0-5-l-5592757",
             note=f"montants ≈ {cm(SURF_PEINT)} m², deux couches, et chevilles ; 25,90 € sur la liste du rayon"),
        dict(poste="Finition", article="Huile plan de travail Resist'Activ V33 incolore mat 1 L", ref="5566676",
             magasin="weldom", qte=1, pu=34.00, statut="relevé",
             url="https://www.weldom.fr/p/huile-plan-de-travail-resist-activ-v33-incolore-mat-1-l-5566676",
             note=f"tablettes ≈ {cm(e.surf_huile)} m², trois couches toutes faces"),
        dict(poste="Finition", article="Apprêt antirouille noir en bombe (chevilles)", ref="—", magasin="weldom",
             qte=1, pu=12.00, statut="estimé", url=None),
        dict(poste="Finition", article="Pâte à bois (bouchage des lamages) et abrasifs grains 120 et 180", ref="—",
             magasin="weldom", qte=1, pu=16.00, statut="estimé", url=None),
    ]
    for a in lst:
        a["total"] = round(a["qte"] * a["pu"], 2)
    return lst


DISPOS = [etat(d) for d in M.DISPOSITIONS]
D0 = DISPOS[0]                                   # disposition du plan du salon (TABLETTES)
assert D0.cle == "actuelle"


def pieces(e):
    """Liste des pièces d'une disposition : montants, une ligne par type de tablette, chevilles."""
    out = [dict(rep="M", nom="Montant", n=MO["n"], dims=f'{cm(L_MONTANT)} × {cm(MO["l"])} × {cm(MO["p"])}',
                matiere="sapin raboté, peint en noir mat",
                de=f'{N_TASSEAUX} tasseaux, {PAR_TASSEAU} montants par tasseau ; le reste du dernier sert de gabarit '
                   f'de perçage et d\'essai')]
    for d in e.types.values():
        reps = ", ".join(t["rep"] for t in e.ts if t["type"] == d["type"])
        de = f'{d["n"]} entailles de {cm(ET["entaille"][0])} × {cm(ET["entaille"][1])} ; {reps}'
        out.append(dict(rep=d["type"], nom=f'Tablette de {d["n"] - 1} travée'
                        + ("s" if d["n"] > 2 else ""), n=d["nb"], dims=f'{cm(d["l"])} × {ET["p"]} × {cm(ET["ep"])}',
                        matiere="chêne massif, huilé", de=de))
    out.append(dict(rep="C", nom="Cheville", n=e.chevilles, dims=f'Ø {cm(MO["trou"] * 10)} mm × {cm(ET["cheville"])}',
                    matiere="acier, peint en noir mat",
                    de=f'{e.n_ronds} ronds de 1 m, {e.par_rond} par rond ({e.n_ronds * e.par_rond - e.chevilles} de '
                       f'rechange), bouts chanfreinés'))
    return out


# ------------------------------------------------------------------ volumes 3D (vue iso, rendus Blender)
def pieces_3d(e=D0):
    """Montants, tablettes entaillées et chevilles en boîtes sans chevauchement (cm, repère du salon).

    Chaque tablette = une bande avant (de la profondeur d'entaille jusqu'au bord) sur toute sa longueur, plus les
    morceaux arrière entre les entailles et aux bouts. Chaque cheville (section carrée ≈ Ø) est coupée en deux bouts
    qui dépassent de chaque flanc du montant : avant sous la tablette, arrière dessus. Sans l'enfilade."""
    ps = []
    demi_m, prof_e = MO["l"] / 2, ET["entaille"][1]
    r, demi_c = MO["trou"] / 2, ET["cheville"] / 2
    for i, y in enumerate(MO["axes"]):
        ps.append(C.Piece(f"montant_M{i + 1}", 0, MO["p"], y - demi_m, y + demi_m, MO["z0"], MO["z1"], "pin_noir"))
    for t in e.ts:
        z0, z1 = t["z"] - ET["ep"], t["z"]
        demi_e = ET["entaille"][0] / 2
        g = f'tablette_{t["rep"]}'
        ps.append(C.Piece(f'{g}_avant', ET["x0"] + prof_e, ET["x1"], t["y0"], t["y1"], z0, z1, "chene", g))
        axes = MO["axes"][t["a"]:t["b"] + 1]
        bords = [t["y0"]] + [v for y in axes for v in (y - demi_e, y + demi_e)] + [t["y1"]]
        ra, rx0, rx1 = RA, MO["x_av"] - RA["l"] / 2, MO["x_av"] + RA["l"] / 2
        for k in range(0, len(bords), 2):
            u0, u1 = bords[k], bords[k + 1]
            nom = f'{g}_arriere_{k // 2 + 1}'
            ps += [C.Piece(f'{nom}_mur', ET["x0"], rx0, u0, u1, z0, z1, "chene", g),
                   C.Piece(f'{nom}_devant', rx1, ET["x0"] + prof_e, u0, u1, z0, z1, "chene", g)]
            # au droit de la rainure : creusé sur (long − entaille) / 2 contre chaque entaille voisine
            c0 = u0 + RA_COTE if k > 0 else u0
            c1 = u1 - RA_COTE if k + 2 < len(bords) else u1
            for m, (v0, v1, zb) in enumerate(((u0, c0, z0 + ra["prof"]), (c0, c1, z0), (c1, u1, z0 + ra["prof"]))):
                if v1 - v0 > 1e-6:
                    ps.append(C.Piece(f'{nom}_rainure_{m}', rx0, rx1, v0, v1, zb, z1, "chene", g))
        for j, y in enumerate(axes):
            m, zj = f'M{t["a"] + j + 1}', t["zs"][j]
            for pos, x, zc in (("avant", MO["x_av"], zj + r - MO["decalage"]), ("arriere", MO["x_ar"], zj + r)):
                for cote, ya, yb in (("nord", y - demi_c, y - demi_m), ("sud", y + demi_m, y + demi_c)):
                    ps.append(C.Piece(f'cheville_{t["rep"]}_{m}_{pos}_{cote}', x - r, x + r, ya, yb,
                                      zc - r, zc + r, "acier", forme="cyl_y"))
    return ps


def _rogne(ps, x0, x1, y0, y1, z0, z1):
    """Pièces rognées à une boîte (pour une vue de détail) ; les pièces hors de la boîte disparaissent."""
    out = []
    for p in ps:
        b = (max(p.x0, x0), min(p.x1, x1), max(p.y0, y0), min(p.y1, y1), max(p.z0, z0), min(p.z1, z1))
        if b[0] < b[1] and b[2] < b[3] and b[4] < b[5]:
            out.append(C.Piece(p.nom, *b, p.matiere, p.groupe, p.forme))
    return out


def pieces_detail():
    """Un montant (M2) avec la tablette T1 de la disposition actuelle et ses deux chevilles, en coupe : la tablette
    est rognée à 12 au nord de l'axe, à 20 du mur et, côté sud, au ras du bout des chevilles, pour montrer la cheville
    avant sous la joue."""
    y, z = MO["axes"][1], D0.ts[0]["z"]
    return _rogne(pieces_3d(D0), -1, 20, y - 12, y + ET["cheville"] / 2, z - 14, z + 12)


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
     f"{ET['p']} : chaque bande garde un chant arrondi d'usine, qui fait le devant de la tablette.",
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


# ------------------------------------------------------------------ dessins
def elevation(e, mini=False):
    """Mur ouest vu depuis la pièce (sud à gauche, nord à droite) : enfilade en contour, montants, tablettes, bouts de
    chevilles, cotes (échelle × 2,4) ; mini : vignette sans cotes ni textes."""
    k, Y = 2.4, EN["y1"]
    U = lambda y: (Y - y) * k
    V = lambda z: (M.H - z) * k
    l, ce, r = MO["l"], ET["cheville_ext"], MO["trou"] / 2
    o = [rect(0, V(M.H), U(0), V(0), "bgwall")]
    if not mini:
        o += [f'<line class="floorl" x1="-70" y1="{f(V(0))}" x2="{f(U(0) + 30)}" y2="{f(V(0))}"/>',
              f'<line class="ceil" x1="-70" y1="{f(V(M.H))}" x2="{f(U(0) + 30)}" y2="{f(V(M.H))}"/>',
              text(U((EN["y0"] + EN["y1"]) / 2), V(EN["z1"] / 2 + 5), "enfilade (page Enfilade)", "lbl muted")]
        for y in (EN["y1"] - 6, EN["y0"] + 6):
            o.append(rect(U(y) - 2, V(EN["pieds"]), U(y) + 2, V(0), "upper"))
    o.append(rect(U(EN["y1"]), V(EN["z1"]), U(EN["y0"]), V(EN["pieds"]), "upper"))
    for i, y in enumerate(MO["axes"]):
        o.append(rect(U(y + l / 2), V(MO["z1"]), U(y - l / 2), V(MO["z0"]), "mont"))
        if not mini:
            o.append(text(U(y), V(MO["z1"]) - 4, f"M{i + 1}", "lbls"))
    for t in e.ts:
        o.append(rect(U(t["y1"]), V(t["z"]), U(t["y0"]), V(t["z"] - ET["ep"]), "shelfc"))
        if mini:
            continue
        ym = (MO["axes"][t["b"]] + MO["axes"][t["b"] - 1]) / 2      # milieu de la travée la plus au sud
        o.append(text(U(ym), V(t["z"]) - 3, f'{t["rep"]} · {t["type"]} · {t["z"]}', "lbls"))
        for kk in range(t["a"], t["b"] + 1):
            y, zj = MO["axes"][kk], t["zs"][kk - t["a"]]
            for ya in (y + l / 2 + ce, y - l / 2):
                o += [rect(U(ya), V(zj + 2 * r), U(ya - ce), V(zj), "acier"),
                      rect(U(ya), V(zj - ET["ep"]), U(ya - ce), V(zj - MO["decalage"]), "acier")]
    if mini:
        x0, x1 = U(EN["y1"]) - 8, U(EN["y0"]) + 8
        return (f'<svg viewBox="{f(x0)} {f(V(M.H))} {f(x1 - x0)} {f((M.H - EN["z1"] + 6) * k)}" role="img" '
                f'aria-label="Disposition {escape(e.nom)}">{"".join(o)}</svg>')
    # cotes horizontales : axes (au-dessus des montants), débords (sous les montants)
    ax = [U(y) for y in MO["axes"]]
    zc = V(MO["z1"] + 12)
    o += [cote_h(U(EN["y1"]), ax[-1], zc, cm(EN["y1"] - MO["axes"][-1]))]
    o += [cote_h(b, a, zc, f(PAS)) for a, b in zip(ax, ax[1:])]
    o += [cote_h(ax[0], U(EN["y0"]), zc, cm(MO["axes"][0] - EN["y0"]))]
    ys0, ys1 = min(t["y0"] for t in e.ts), max(t["y1"] for t in e.ts)
    zd = V((MO["z0"] + EN["z1"]) / 2 - 2)
    o += [cote_h(U(EN["y1"]), U(ys1), zd, cm(abs(EN["y1"] - ys1))),
          cote_h(U(ys1), ax[-1], zd, f(ET["debord"])),
          cote_h(ax[0], U(ys0), zd, f(ET["debord"])),
          cote_h(U(ys0), U(EN["y0"]), zd, cm(abs(ys0 - EN["y0"])))]
    # cotes verticales : montants et vides (à gauche), dessus des rangs (plus à gauche) quand les tablettes sont en
    # rangs horizontaux ; sinon, la hauteur de chaque tablette est dans son étiquette
    x1, x2 = -14, -40
    for a, b in ((0, EN["z1"]), (EN["z1"], MO["z0"]), (MO["z0"], MO["z1"]), (MO["z1"], M.H)):
        o.append(cote_v(V(a), V(b), x1, cm(b - a)))
    zs = [0] + e.niveaux
    if len(e.niveaux) <= 4:
        o += [cote_v(V(a), V(b), x2, cm(b - a)) for a, b in zip(zs, zs[1:])]
    o += [text(-40, V(0) + 14, "sol", "lbls muted"), text(-40, V(M.H) - 5, f"plafond {cm(M.H)}", "lbls muted", "start"),
          text(2, V(0) + 14, "sud (passage)", "lbls muted", "start"),
          text(U(0) - 2, V(0) + 14, "nord (coin)", "lbls muted", "end")]
    return (f'<svg viewBox="-75 {f(V(M.H) - 16)} {f(U(0) + 110)} {f(M.H * k + 40)}" role="img" '
            f'aria-label="Élévation du mur ouest, disposition {escape(e.nom)}">{"".join(o)}</svg>')


def rangs_dessus(e):
    """Tablettes rangées en vues de dessus : du haut vers le bas, une tablette va dans le premier rang où elle ne
    recouvre aucune autre (au moins 4 d'écart)."""
    rangs = []
    for t in sorted(e.ts, key=lambda t: -max(t["zs"])):
        for rg in rangs:
            if all(t["y0"] >= u["y1"] + 4 or t["y1"] <= u["y0"] - 4 for u in rg):
                rg.append(t)
                break
        else:
            rangs.append([t])
    return rangs


def detail_dessus(e):
    """Vues de dessus des tablettes, rangées sur quelques bandes, vues depuis la pièce face au mur : mur en haut, sud à
    gauche, nord à droite ; montants dans les entailles, chevilles (échelle × 2,6)."""
    k, Y = 2.6, EN["y1"]
    U = lambda y: (Y - y) * k
    rang, l, ce, r = 60, MO["l"], ET["cheville_ext"], MO["trou"] / 2
    rangs = rangs_dessus(e)
    o = []
    for n_r, rg in enumerate(rangs):
        V = lambda x, n_r=n_r: (n_r * rang + x) * k
        o += [rect(U(EN["y1"]), V(-4), U(EN["y0"]), V(0), "mur-h"),
              rect(U(EN["y1"]), V(0), U(EN["y0"]), V(EN["p"]), "upper")]
        chev = []
        for t in rg:
            o.append(rect(U(t["y1"]), V(0), U(t["y0"]), V(ET["x1"]), "shelfc"))
            o.append(text(U((t["y0"] + t["y1"]) / 2), V(ET["x1"]) - 6, f'{t["rep"]} · {t["type"]} · dessus {t["z"]}', "lbls"))
            for y in MO["axes"][t["a"]:t["b"] + 1]:
                a, b = U(y + l / 2 + ce), U(y - l / 2 - ce)
                chev += [rect(a, V(MO["x_av"] - r), b, V(MO["x_av"] + r), "acierh"),
                         rect(a, V(MO["x_ar"] - r), b, V(MO["x_ar"] + r), "acier")]
        o += [rect(U(y + l / 2), V(0), U(y - l / 2), V(MO["p"]), "mont") for y in MO["axes"]]
        o += chev
    vb = ((len(rangs) - 1) * rang + EN["p"]) * k
    ax = [U(y) for y in MO["axes"]]
    o += [text(a, vb + 9, f"M{i + 1}", "lbls") for i, a in enumerate(ax)]
    o += [cote_h(b, a, vb + 24, f(PAS)) for a, b in zip(ax, ax[1:])]
    o += [cote_h(U(EN["y1"]), ax[-1], vb + 24, cm(EN["y1"] - MO["axes"][-1])),
          cote_h(ax[0], U(EN["y0"]), vb + 24, cm(MO["axes"][0] - EN["y0"])),
          cote_h(U(EN["y1"]), U(EN["y0"]), vb + 44, f'enfilade {cm(EN["y1"] - EN["y0"])}')]
    xr = U(EN["y0"]) + 12
    v0 = ((len(rangs) - 1) * rang) * k
    o += [cote_v(v0, v0 + MO["p"] * k, xr, f(MO["p"])),
          cote_v(v0 + MO["p"] * k, v0 + ET["x1"] * k, xr, f(ET["x1"] - MO["p"])),
          cote_v(v0 + ET["x1"] * k, v0 + EN["p"] * k, xr, f(EN["p"] - ET["x1"])),
          text(U(EN["y1"]) + 4, -4 * k - 4, "mur ouest", "lbls muted", "start"),
          text(U(EN["y0"]) - 4, -4 * k - 4, "sud à gauche, nord à droite (vu depuis la pièce)", "lbls muted", "end")]
    w, h = U(0) + 140, vb + 68 + 4 * k + 14
    return (f'<svg viewBox="-110 {f(-4 * k - 14)} {f(w)} {f(h)}" role="img" '
            f'aria-label="Étagères vues de dessus, disposition {escape(e.nom)}">{"".join(o)}</svg>')


def detail_profil():
    """Coupe de profil juste à côté d'un montant, au droit des bouts de chevilles (échelle × 9)."""
    k = 9
    ep, r, dec = ET["ep"], MO["trou"] / 2, MO["decalage"]
    X = lambda x: f(x * k)
    Z = lambda z: f(-z * k)
    o = [f'<rect class="mur-h" x="{X(-3)}" y="{Z(14)}" width="{X(3)}" height="{f(28 * k)}"/>',
         text(-1.5 * k, -15 * k, "mur", "lbl muted"),
         f'<rect class="mont" x="0" y="{Z(14)}" width="{X(MO["p"])}" height="{f(28 * k)}"/>']
    zf = r - dec                    # centre de la cheville avant
    for dz in (-10, -5, 5, 10):     # trous libres : colonne avant sous les tablettes, arrière au-dessus
        o += [f'<circle class="trou" cx="{X(MO["x_av"])}" cy="{Z(dz + zf)}" r="{f(r * k)}"/>',
              f'<circle class="trou" cx="{X(MO["x_ar"])}" cy="{Z(dz + r)}" r="{f(r * k)}"/>']
    g0, g1 = MO["x_av"] - RA["l"] / 2, MO["x_av"] + RA["l"] / 2
    o += [f'<path class="shelfc" d="M0 {Z(0)} H{X(ET["p"])} V{Z(-ep)} H{X(g1)} V{Z(-ep + RA["prof"])} H{X(g0)} '
          f'V{Z(-ep)} H0 Z"/>',
          f'<circle class="acier" cx="{X(MO["x_av"])}" cy="{Z(zf)}" r="{f(r * k)}"/>',
          f'<circle class="acier" cx="{X(MO["x_ar"])}" cy="{Z(r)}" r="{f(r * k)}"/>',
          cote_h(0, MO["p"] * k, -14 * k - 10, f'montant {f(MO["p"])}'),
          cote_h(0, ET["p"] * k, -14 * k - 26, f'tablette {ET["p"]}, jusqu\'au mur'),
          cote_h(MO["x_ar"] * k, MO["x_av"] * k, 4.5 * k, f(MO["x_av"] - MO["x_ar"])),
          cote_v(0, ep * k, ET["p"] * k + 12, cm(ep)),
          cote_v(-r * k, -zf * k, -3 * k - 14, cm(dec)),
          cote_v(-(5 + r) * k, -r * k, -3 * k - 30, f(MO["pas_trous"])),
          text((MO["p"] + 3) * k, -2.5 * k, "cheville arrière, dessus : retient le basculement", "lbls", "start"),
          text((MO["p"] + 3) * k, (ep + 2.2) * k, "cheville avant, dessous : porte la tablette", "lbls", "start"),
          rappel(g1 * k, (ep - RA["prof"] / 2) * k, (MO["p"] + 3) * k, (ep + 4.4) * k,
                 f"dans une rainure de {cm(RA['l'] * 10)} × {cm(RA['prof'] * 10)} mm : elle ne peut ni avancer ni glisser en long",
                 "start", "lbls"),
          text((MO["p"] + 3) * k, 9 * k, "trous libres sur le flanc : la tablette monte ou descend de 5 en 5",
               "lbls muted", "start")]
    return (f'<svg style="max-width:620px" viewBox="{f(-8 * k)} {f(-18.5 * k)} {f(46 * k)} {f(33 * k)}" role="img" '
            f'aria-label="Profil d\'une tablette entaillée et de ses deux chevilles">{"".join(o)}</svg>')


def detail_face():
    """Une travée vue de face : deux montants, la tablette passe devant eux, bouts de chevilles (échelle × 3)."""
    k = 3
    X = lambda y: f(y * k)
    Z = lambda z: f(-z * k)
    l, ce, r = MO["l"], ET["cheville_ext"], MO["trou"] / 2
    o = [f'<rect class="mont" x="{X(y - l / 2)}" y="{Z(40)}" width="{X(l)}" height="{f(50 * k)}"/>'
         for y in (0, PAS)]
    for z in (0, 35):
        o.append(f'<rect class="shelfc" x="{X(-ET["debord"])}" y="{Z(z)}" '
                 f'width="{X(PAS + 2 * ET["debord"])}" height="{X(ET["ep"])}"/>')
        for y in (0, PAS):
            for y0 in (y - l / 2 - ce, y + l / 2):
                o += [f'<rect class="acier" x="{X(y0)}" y="{Z(z + 2 * r)}" width="{X(ce)}" height="{X(2 * r)}"/>',
                      f'<rect class="acier" x="{X(y0)}" y="{Z(z - ET["ep"])}" width="{X(ce)}" '
                      f'height="{X(MO["decalage"] - ET["ep"])}"/>']     # le haut de la cheville avant est dans la rainure
    o += [cote_h(-ET["debord"] * k, 0, -41 * k - 6, f'{ET["debord"]}'),
          cote_h(0, PAS * k, -41 * k - 6, f'{PAS} d\'axe en axe'),
          cote_h(PAS * k, (PAS + ET["debord"]) * k, -41 * k - 6, f'{ET["debord"]}'),
          cote_v(0, -35 * k, (PAS + ET["debord"]) * k + 10, "35"),
          text(PAS / 2 * k, -17 * k, "livres ≤ 30", "lbls muted")]
    return (f'<svg style="max-width:660px" viewBox="{f(-20 * k)} {f(-46 * k)} {f((PAS + 40) * k)} {f(58 * k)}" role="img" '
            f'aria-label="Une travée vue de face">{"".join(o)}</svg>')


def fleche(x0, y0, x1, y1):
    """Flèche d'effort (SVG), pointe en (x1, y1)."""
    d = math.hypot(x1 - x0, y1 - y0)
    ux, uy = (x1 - x0) / d, (y1 - y0) / d
    a, b = (x1 - 7 * ux - 3.5 * uy, y1 - 7 * uy + 3.5 * ux), (x1 - 7 * ux + 3.5 * uy, y1 - 7 * uy - 3.5 * ux)
    return (f'<line class="fl" x1="{f(x0)}" y1="{f(y0)}" x2="{f(x1 - 6 * ux)}" y2="{f(y1 - 6 * uy)}"/>'
            + poly("flh", [(x1, y1), a, b]))


def rappel(x0, y0, x1, y1, txt, anc, cls="lbl"):
    """Étiquette reportée par un trait de rappel (coordonnées SVG)."""
    return (f'<line x1="{f(x0)}" y1="{f(y0)}" x2="{f(x1)}" y2="{f(y1)}" stroke="var(--muted)" stroke-width=".7"/>'
            + text(x1 + (4 if anc == "start" else -4), y1 + 3, txt, cls, anc))


# ------------------------------------------------------------------ présentoir (tablette penchée vers la pièce)
# Mêmes trous que les tablettes à plat ; la cheville avant est prise dans une rainure faite à la défonceuse sous la
# tablette (largeur l), qui l'empêche d'avancer vers la pièce et remplace la feuillure du dessus.
PR = dict(deg=15, l=RA["l"])
_th = math.radians(PR["deg"])
PR.update(t=math.tan(_th), c=math.cos(_th), s=math.sin(_th))


def _pr_geo():
    """Profil du présentoir (x depuis le mur, z depuis le dessous de la cheville arrière) : dessus, dessous, centre de
    la cheville avant, profondeur de la rainure (perpendiculaire à la tablette), position de son axe sur le dessous."""
    t, c, sn, r, ep = PR["t"], PR["c"], PR["s"], MO["trou"] / 2, ET["ep"]
    top = lambda x: -(x - MO["x_ar"]) * t                     # le dessus touche la cheville arrière
    bas = lambda x: top(x) - ep / c
    zc = r - MO["decalage"]                                    # mêmes trous qu'à plat
    u = lambda x, z: x * c - z * sn                            # abscisse le long de la pente
    prof = (zc - bas(MO["x_av"])) * c + r                      # la cheville touche le fond de la rainure
    return dict(top=top, bas=bas, zc=zc, u=u, prof=prof, uc=u(MO["x_av"], zc), axe=u(MO["x_av"], zc) - u(0, bas(0)),
                kb=MO["x_ar"] * t - ep / c)


PR.update(_pr_geo())


def passage(deg):
    """Écart entre le dessous de la cheville arrière et le dessus de la cheville avant, perpendiculaire à une
    tablette penchée de deg (négatif : devant levé) ; la tablette pleine passe si l'écart dépasse son épaisseur."""
    p = math.radians(deg)
    dz, dx = -(PR["zc"] + MO["trou"] / 2), MO["x_av"] - MO["x_ar"]
    return dz * math.cos(p) - dx * math.sin(p)


def coincement(x):
    """Frottement minimal pour que le présentoir ne glisse pas, chargé à x du mur (arc-boutement) : le glissement est
    poussé par W sin θ ; les chevilles serrent la tablette de N_av + N_ar = W cos θ (2 d / e + 1), d = x − x_av."""
    return PR["t"] / (2 * (x - MO["x_av"]) / (MO["x_av"] - MO["x_ar"]) + 1)


def presentoir():
    """Présentoir : tablette penchée vers la pièce, profil à côté d'un montant (échelle × 9) : pincée entre la
    cheville arrière (dessus) et la cheville avant (dessous, dans sa rainure), efforts en rouge."""
    k, c, sn, r = 9, PR["c"], PR["s"], MO["trou"] / 2
    top, bas, zc, prof = PR["top"], PR["bas"], PR["zc"], PR["prof"]
    X = lambda x: x * k
    Z = lambda z: -z * k
    x_u = lambda v: (v + sn * PR["kb"]) * c                     # point du dessous d'abscisse v (le long de la pente)
    g0, g1 = x_u(PR["uc"] - PR["l"] / 2), x_u(PR["uc"] + PR["l"] / 2)
    n = (sn * prof, c * prof)                                   # vers le haut, perpendiculaire à la tablette
    pts = [(0, top(0)), (ET["p"], top(ET["p"])), (ET["p"], bas(ET["p"])), (g1, bas(g1)),
           (g1 + n[0], bas(g1) + n[1]), (g0 + n[0], bas(g0) + n[1]), (g0, bas(g0)), (0, bas(0))]
    xp = (MO["p"] + ET["p"]) / 2
    x_g0, x_g1 = 21, 28                                        # flèche du glissement, au-dessus de la tablette
    o = [rect(X(-3), Z(12), 0, Z(-14), "mur-h"), text(X(-1.5), Z(12) - 6, "mur", "lbl muted"),
         rect(0, Z(12), X(MO["p"]), Z(-14), "mont"),
         text(X(MO["p"] / 2), Z(12) - 6, "montant", "lbl"),
         poly("shelfc", [(X(x), Z(z)) for x, z in pts]),
         rect(X(ET["p"] - 2), Z(top(ET["p"]) + 2), X(ET["p"]), Z(top(ET["p"])), "shelfc"),
         f'<circle class="acier" cx="{f(X(MO["x_ar"]))}" cy="{f(Z(r))}" r="{f(r * k)}"/>',
         f'<circle class="acier" cx="{f(X(MO["x_av"]))}" cy="{f(Z(zc))}" r="{f(r * k)}"/>',
         fleche(X(xp), Z(top(xp) + 7), X(xp), Z(top(xp))),
         text(X(xp) + 6, Z(top(xp) + 5), "ce qui est posé", "lbl", "start"),
         fleche(X(MO["x_av"]), Z(zc - 7), X(MO["x_av"]), Z(zc - r)),
         fleche(X(MO["x_ar"]), Z(2 * r + 6), X(MO["x_ar"]), Z(2 * r)),
         f'<g class="glis">{fleche(X(x_g0), Z(top(x_g0) + 4), X(x_g1), Z(top(x_g1) + 4))}</g>',
         text(X(x_g1) + 5, Z(top(x_g1) + 4) + 3, "pousse à glisser", "lbls", "start"),
         rappel(X(MO["x_ar"]) + r * k, Z(r) - r * k, X(14), Z(9), "cheville arrière, dessus : retient l'arrière, qui veut se soulever", "start"),
         rappel(X(g1 + n[0] / 2), Z(bas(g1) + n[1] / 2), X(14), Z(-12.3),
                f"rainure {cm(PR['l'] * 10)} × {cm(PR['prof'] * 10)} mm à la défonceuse : la cheville avant y est prise, la tablette ne peut plus avancer", "start"),
         rappel(X(MO["x_av"]), Z(zc - 5), X(14), Z(-14.8), "cheville avant, dessous : porte la tablette", "start"),
         text(X(ET["p"]) + 6, Z(top(ET["p"]) + 1) + 3, "rebord 2 × 2 collé", "lbls", "start"),
         cote_v(Z(top(0)), Z(top(ET["p"])), X(ET["p"]) + 90, cm(top(0) - top(ET["p"])))]
    return (f'<svg style="max-width:720px" viewBox="{f(-6 * k)} {f(-15.5 * k)} {f(62 * k)} {f(31 * k)}" role="img" '
            f'aria-label="Présentoir penché vers la pièce, profil">{"".join(o)}</svg>')


def decoupe_panneaux(e):
    """Les plans de travail vus de dessus, refendus en bandes, tablettes rangées dans les bandes (échelle × 2,6)."""
    k, gap = 2.6, 34
    o, y = [], 0
    for i, bandes_p in enumerate(e.panneaux):
        o += [rect(0, y, PANNEAU["l"] * k, y + PANNEAU["p"] * k, "mur-h"),
              text(0, y - 6, f"Plan P{i + 1} · {PANNEAU['nom']}", "lbl", "start")]
        for j, bande in enumerate(bandes_p):
            by = y + j * (ET["p"] + KERF) * k
            x = DRESSAGE
            for t in bande:
                o += [rect(x * k, by, (x + t["l"]) * k, by + ET["p"] * k, "shelfc"),
                      text((x + t["l"] / 2) * k, by + ET["p"] * k / 2 + 3, f'{t["rep"]} · {cm(t["l"])}', "lbl")]
                x += t["l"] + KERF
            if PANNEAU["l"] - x > 20:
                o.append(text((x + (PANNEAU["l"] - x) / 2) * k, by + ET["p"] * k / 2 + 3,
                              f'chute {cm(PANNEAU["l"] - x)}', "lbls muted"))
            # chant d'usine (arrondi) : devant de la tablette, côté extérieur du panneau
            yc = by if j == 0 else by + ET["p"] * k
            o.append(f'<line x1="0" y1="{f(yc)}" x2="{f(PANNEAU["l"] * k)}" y2="{f(yc)}" '
                     f'stroke="var(--tri)" stroke-width="1.6"/>')
        o += [cote_v(y, y + ET["p"] * k, -10, f(ET["p"])),
              cote_v(y + (ET["p"] + KERF) * k, y + (2 * ET["p"] + KERF) * k, -10, f(ET["p"])),
              cote_v(y, y + PANNEAU["p"] * k, -30, f(PANNEAU["p"]))]
        y += PANNEAU["p"] * k + gap
    o.append(cote_h(0, PANNEAU["l"] * k, y - gap + 16, f(PANNEAU["l"])))
    return (f'<svg style="max-width:820px" viewBox="-45 -18 {f(PANNEAU["l"] * k + 60)} {f(y + 4)}" role="img" '
            f'aria-label="Plan de découpe des plans de travail en chêne">{"".join(o)}</svg>')


def decoupe_barres(e):
    """Tasseaux (montants) et ronds (chevilles), échelle × 2,6."""
    k, o, y = 2.6, [], 0
    for i in range(N_TASSEAUX):
        n = min(PAR_TASSEAU, MO["n"] - i * PAR_TASSEAU)
        o += [rect(0, y, TASSEAU["l"] * k, y + TASSEAU["s"][1] * k, "mur-h"),
              text(-6, y + TASSEAU["s"][1] * k / 2 + 3, f"tasseau {i + 1}", "lbls", "end")]
        x = 0
        for _ in range(n):
            o += [rect(x * k, y, (x + L_MONTANT) * k, y + TASSEAU["s"][1] * k, "mont"),
                  f'<text class="lbls" x="{f((x + L_MONTANT / 2) * k)}" y="{f(y + TASSEAU["s"][1] * k / 2 + 3)}" '
                  f'text-anchor="middle" style="fill:#fff">M · {cm(L_MONTANT)}</text>']
            x += L_MONTANT + KERF
        if TASSEAU["l"] - x > 1:
            o.append(text((x + (TASSEAU["l"] - x) / 2) * k, y + TASSEAU["s"][1] * k / 2 + 3,
                          f'chute {cm(TASSEAU["l"] - x)} : gabarit et essai', "lbls"))
        y += TASSEAU["s"][1] * k + 10
    o.append(cote_h(0, TASSEAU["l"] * k, y + 6, f'tasseau {cm(TASSEAU["l"])}'))
    y += 26
    kr = TASSEAU["l"] * k / ROND["l"]          # ronds à la même largeur de dessin que les tasseaux
    for i in range(e.n_ronds):
        o += [rect(0, y, ROND["l"] * kr, y + 6, "acier"),
              text(-6, y + 6, f"rond {i + 1}", "lbls", "end")]
        for j in range(1, e.par_rond):
            xx = j * (ET["cheville"] + KERF_METAL) * kr
            o.append(f'<line x1="{f(xx)}" y1="{f(y - 2)}" x2="{f(xx)}" y2="{f(y + 8)}" stroke="var(--ink)" stroke-width=".8"/>')
        y += 16
    o.append(cote_h(0, (ET["cheville"]) * kr, y + 4, f'C · {cm(ET["cheville"])}'))
    o.append(cote_h(0, ROND["l"] * kr, y + 22, f'rond {f(ROND["l"])} : {e.par_rond} chevilles'))
    return (f'<svg style="max-width:820px" viewBox="-60 -6 {f(TASSEAU["l"] * k + 70)} {f(y + 30)}" role="img" '
            f'aria-label="Débit des tasseaux et des ronds">{"".join(o)}</svg>')


def percage():
    """Un montant couché, bas à gauche : flanc (deux colonnes de trous traversants) et face avant (vis de fixation
    dans leurs lamages), échelle × 6."""
    k, L = 6, L_MONTANT
    r = MO["trou"] / 2
    av = [z - MO["z0"] for z in MO["trous_av"]]
    ar = [z - MO["z0"] for z in MO["trous_ar"]]
    vis = [5, L / 2 + 0.5, L - 4]          # hauteurs des vis depuis le bas (5, 60, 115 pour 119)
    X = lambda z: z * k
    o = []
    # flanc : x = 0 (mur) en haut, x = p (pièce) en bas
    yf = 40
    W = lambda x: yf + x * k
    o += [rect(0, W(0), X(L), W(MO["p"]), "mont"),
          text(0, yf - 30, "flanc (les deux flancs sont percés de part en part)", "lbl", "start"),
          text(X(L), yf - 30, "côté mur en haut", "lbls muted", "end")]
    o += [f'<circle class="trou" cx="{f(X(z))}" cy="{f(W(MO["x_av"]))}" r="{f(r * k)}"/>' for z in av]
    o += [f'<circle class="trou" cx="{f(X(z))}" cy="{f(W(MO["x_ar"]))}" r="{f(r * k)}"/>' for z in ar]
    o += [cote_h(0, X(ar[0]), yf - 8, cm(ar[0])),
          cote_h(X(ar[0]), X(ar[-1]), yf - 8, f'arrière : {len(ar) - 1} × {MO["pas_trous"]} = {cm(ar[-1] - ar[0])}'),
          cote_h(X(ar[-1]), X(L), yf - 8, cm(L - ar[-1])),
          cote_h(0, X(av[0]), W(MO["p"]) + 16, cm(av[0])),
          cote_h(X(av[0]), X(av[-1]), W(MO["p"]) + 16, f'avant : {len(av) - 1} × {MO["pas_trous"]} = {cm(av[-1] - av[0])}'),
          cote_h(X(av[-1]), X(L), W(MO["p"]) + 16, cm(L - av[-1])),
          cote_v(W(0), W(MO["x_ar"]), -8, f(MO["x_ar"])),
          cote_v(W(MO["x_ar"]), W(MO["x_av"]), -8, f(MO["x_av"] - MO["x_ar"])),
          cote_v(W(MO["x_av"]), W(MO["p"]), -8, f(MO["p"] - MO["x_av"])),
          cote_v(W(0), W(MO["p"]), X(L) + 14, f(MO["p"]))]
    # face avant, sous le flanc
    ya = W(MO["p"]) + 60
    A = lambda y: ya + y * k
    o += [rect(0, A(0), X(L), A(MO["l"]), "mont"),
          text(0, ya - 8, "face avant, côté pièce (pas de trous de cheville)", "lbl", "start")]
    for z in vis:
        o += [f'<circle cx="{f(X(z))}" cy="{f(A(MO["l"] / 2))}" r="{f(0.75 * k)}" fill="none" stroke="#fff" stroke-width=".8"/>',
              f'<circle cx="{f(X(z))}" cy="{f(A(MO["l"] / 2))}" r="{f(0.3 * k)}" fill="#fff"/>']
    zs = [0] + vis + [L]
    o += [cote_h(X(a), X(b), A(MO["l"]) + 16, cm(b - a)) for a, b in zip(zs, zs[1:])]
    o += [cote_v(A(0), A(MO["l"]), X(L) + 14, cm(MO["l"])),
          text(0, A(MO["l"]) + 34, f"bas du montant (z {MO['z0']})", "lbls muted", "start"),
          text(X(L), A(MO["l"]) + 34, f"haut (z {MO['z1']})", "lbls muted", "end")]
    return (f'<svg viewBox="-30 0 {f(X(L) + 60)} {f(A(MO["l"]) + 42)}" role="img" '
            f'aria-label="Plan de perçage d\'un montant">{"".join(o)}</svg>')


def entaille():
    """Bout nord d'une tablette vu de dessus (mur en haut) : entaille, montant, chevilles (échelle × 5)."""
    k, long = 5, ET["debord"] + 44
    e_l, e_p = ET["entaille"]
    l, ce, r = MO["l"], ET["cheville_ext"], MO["trou"] / 2
    a = ET["debord"]                        # axe du montant depuis le bout de la tablette
    X = lambda y: y * k
    Y = lambda x: 24 + x * k
    o = [rect(X(-3), Y(-3), X(long), Y(0), "mur-h"),
         text(X(long), Y(-3) - 4, "mur", "lbls muted", "end"),
         f'<path class="shelfc" d="M0 {f(Y(0))} H{f(X(a - e_l / 2))} V{f(Y(e_p))} H{f(X(a + e_l / 2))} '
         f'V{f(Y(0))} H{f(X(long))} V{f(Y(ET["p"]))} H0 Z"/>',
         rect(X(a - l / 2), Y(0), X(a + l / 2), Y(MO["p"]), "mont"),
         rect(X(a - l / 2 - ce), Y(MO["x_ar"] - r), X(a + l / 2 + ce), Y(MO["x_ar"] + r), "acier"),
         rect(X(a - l / 2 - ce), Y(MO["x_av"] - r), X(a + l / 2 + ce), Y(MO["x_av"] + r), "acierh"),
         rect(X(a - RA["long"] / 2), Y(MO["x_av"] - RA["l"] / 2), X(a + RA["long"] / 2), Y(MO["x_av"] + RA["l"] / 2), "rain"),
         text(X(a + RA["long"] / 2) + 4, Y(MO["x_av"]) + 3, f"rainure dessous, {f(RA['long'])} de long", "lbls", "start"),
         cote_h(0, X(a - e_l / 2), Y(ET["p"]) + 14, cm(a - e_l / 2)),
         cote_h(X(a - e_l / 2), X(a + e_l / 2), Y(ET["p"]) + 14, cm(e_l)),
         cote_h(0, X(a), Y(ET["p"]) + 32, f"{f(a)} : axe"),
         cote_h(X(a), X(a + PAS) if a + PAS < long else X(long), Y(ET["p"]) + 32,
                f'puis {PAS} d\'axe en axe →'),
         cote_v(Y(0), Y(e_p), -12, cm(e_p)),
         cote_v(Y(0), Y(ET["p"]), X(long) + 14, f(ET["p"])),
         text(X(long / 2 + 6), Y(ET["p"] / 2), "tablette (dessus)", "lbls"),
         text(X(long / 2 + 6), Y(ET["p"]) - 6, "chant arrondi d'usine, devant", "lbls muted")]
    return (f'<svg style="max-width:560px" viewBox="-34 0 {f(X(long) + 60)} {f(Y(ET["p"]) + 42)}" role="img" '
            f'aria-label="Entaille d\'une tablette">{"".join(o)}</svg>')


# ------------------------------------------------------------------ sections
def par_dispo(fn):
    """Un bloc par disposition ; seul celui de la disposition choisie s'affiche."""
    return "".join(f'<div class="dv" data-d="{e.cle}">{fn(e)}</div>' for e in DISPOS)


def libre_txt(t):
    vals = sorted({round(v) for v, plafond in t["libres"] if not plafond})
    plaf = any(plafond for _, plafond in t["libres"])
    s = " et ".join(f"{v}" for v in vals)
    return (s + (" ; " if s else "") + "plafond") if plaf else s


def lien_magasin(a):
    nom = MAGASINS[a["magasin"]]["nom"].split(" Marseille")[0]
    return f'<a href="{a["url"]}">{nom}</a>' if a["url"] else nom


def note_achat(a):
    return f'<br><span class="choix">{escape(a["note"])}</span>' if a.get("note") else ""


def table_achats(e):
    lignes = "".join(
        f'<tr><td>{a["poste"]}</td><td>{escape(a["article"])}{note_achat(a)}</td>'
        f'<td class="mono">{a["ref"]}</td><td class="num">{a["qte"]}</td><td class="num">{euros(a["pu"])}</td>'
        f'<td class="num">{euros(a["total"])}</td><td>{lien_magasin(a)}</td><td>{a["statut"]}</td></tr>'
        for a in e.achats)
    return (f'<div class="fig scroll"><table class="budget"><thead><tr><th>Poste</th><th>Article</th><th>Réf.</th>'
            f'<th class="num">Qté</th><th class="num">Prix unit.</th><th class="num">Total</th><th>Source</th>'
            f'<th>Prix</th></tr></thead><tbody>{lignes}'
            f'<tr class="tot"><td colspan="5">Total TTC (disposition {escape(e.nom)})</td><td class="num">{euros(e.total)}</td><td colspan="2"></td></tr>'
            f'</tbody></table></div>')


def section_dispositions():
    vignettes = "".join(
        f'<button type="button" class="dmini" data-d="{e.cle}" aria-pressed="false"><b>{escape(e.nom)}</b>'
        f'<span class="mono">{escape(e.kit)}</span>{elevation(e, mini=True)}<span class="cap">{escape(e.idee)}</span></button>'
        for e in DISPOS)
    lignes = "".join(
        f'<tr><td><b>{escape(e.nom)}</b></td><td>{len(e.ts)} : {escape(e.kit)}</td><td class="num">{e.n_tailles}</td>'
        f'<td class="num">{cm(e.metres)}</td><td class="mono">{len(e.niveaux)} ({e.niveaux[0]} → {e.niveaux[-1]})</td>'
        f'<td class="num">{round(e.libre_min)} → {round(e.libre_max)}</td><td class="num">{e.chevilles}</td>'
        f'<td class="num">{len(e.panneaux)}</td><td class="num">{euros(e.total)}</td></tr>' for e in DISPOS)
    k2 = next(e for e in DISPOS if e.cle == "rangs")
    return f"""<h2 id="dispositions">Dispositions</h2>
<p>Les {MO["n"]} montants et leurs trous ne changent pas : percés de {M.NIVEAUX[0]} à {M.NIVEAUX[1]} de {MO["pas_trous"]} en {MO["pas_trous"]}, ils portent toutes les dispositions ci-dessous. Seules les tablettes changent, en nombre, en longueur et en hauteur. Cliquer une vignette (ou un bouton de la barre du haut) fait passer <b>toute la page</b> dans cette disposition : élévation, vues de dessus, vue iso, composition, débit, achats et prix.</p>
<div class="dgrid">{vignettes}</div>
<div class="fig scroll"><table><thead><tr><th>Disposition</th><th>Tablettes</th><th class="num">Tailles</th><th class="num">Mètres</th><th>Hauteurs de dessus</th><th class="num">Libre entre tablettes</th><th class="num">Chevilles</th><th class="num">Plans</th><th class="num">Total</th></tr></thead><tbody>{lignes}</tbody></table></div>
<h3>Deux longueurs seulement</h3>
<p>Hors disposition actuelle, toutes les tablettes font une travée (<b>79</b> : {ET["debord"]} + {PAS} + {ET["debord"]}) ou deux (<b>134</b>) ; les longues de 189 et 244 sont divisées. Une bande refendue de {cm(BANDE)} donne exactement une 134 et une 79 ({cm(BANDE - 134 - 79 - 2 * KERF)} de chute) ou trois 79 ({cm(BANDE - 3 * 79 - 3 * KERF)} de chute) : avec les deux mêmes plans de chêne qu'aujourd'hui, on tire {k2.kit} (Rangs, Décalée) ou 2 × 134 + 8 × 79 (Escalier). Une troisième longueur (189) ne se marie avec aucune autre dans 250 : elle laisserait {cm(BANDE - 189 - KERF)} de chute par bande. Les tablettes de même longueur sont <b>interchangeables</b> : Rangs et Décalée se recomposent l'une en l'autre sans rien racheter, en déplaçant les chevilles.</p>
<p>Diviser coûte des entailles et des chevilles en plus ({k2.chevilles} au lieu de {D0.chevilles}, un rond d'acier de plus), et une tablette divisée laisse une travée vide à son niveau, entre ses deux morceaux (deux bouts de {ET["debord"]} ne peuvent pas se partager un montant au même niveau) : c'est ce vide, qui change de place d'un rang à l'autre, qui fait le dessin.</p>
<h3>Règles de composition</h3>
<ul class="pistes">
<li><b>Dessus</b> de {M.NIVEAUX[0]} (la lampe posée sur l'enfilade passe dessous) à {M.NIVEAUX[1]} (la cheville arrière reste sous le haut du montant), de {MO["pas_trous"]} en {MO["pas_trous"]}.</li>
<li><b>Deux tablettes sur la même travée</b> : 25 au moins d'un dessus à l'autre, soit ≈ {cm(25 - ET["ep"])} de libre (poches, objets) ; 30 pour les livres courants, 40 pour les grands formats et les vinyles ({cm(31.5 + 0.5)} de haut).</li>
<li><b>Deux tablettes qui se partagent un montant</b> sans partager de travée (leurs débords l'un au-dessus de l'autre) : 15 au moins.</li>
<li><b>Au même niveau</b> : une travée vide entre les deux ({cm(PAS - 2 * ET["debord"])} entre les bouts).</li>
</ul>
<p class="note">Libre entre tablettes : du dessus d'une tablette au dessous de celle qui la couvre, sur une même travée ; au-dessus de la plus haute, il reste au moins {cm(M.H - M.NIVEAUX[1])} jusqu'au plafond. Le plan du salon garde la disposition actuelle tant qu'aucune n'est choisie ; les rendus 3D ne montrent qu'elle.</p>"""


def section_iso():
    def iso(e):
        return (f'<div class="fig"><div class="scroll">{C.iso_svg(pieces_3d(e), f"Étagères, vue iso, disposition {e.nom}")}</div>'
                f'<p class="cap">Disposition {escape(e.nom)} en vue isométrique, depuis la pièce, côté sud et en hauteur (le mur ouest au fond, le sud à gauche ; l\'enfilade n\'est pas dessinée) : {MO["n"]} montants noirs qui traversent les {len(e.ts)} tablettes en chêne par leurs entailles, et les bouts des chevilles d\'acier de part et d\'autre de chaque montant.</p></div>')
    return f"""<h2 id="iso">Vue iso</h2>
{par_dispo(iso)}
<div class="fig"><div class="scroll">{C.iso_svg(pieces_detail(), "Étagères, détail d'une entaille en vue iso", echelle=11, style="max-width:420px;display:block;margin:0 auto")}</div>
<p class="cap">Détail agrandi, en coupe (le même dans toutes les dispositions) : un montant et une tablette, coupée à 20 du mur et, côté sud (devant à gauche), au ras du bout des chevilles. Le montant passe dans l'entaille de {cm(ET["entaille"][0])} × {cm(ET["entaille"][1])} ; la cheville avant (à {MO["x_av"]} du mur) dépasse sous la tablette, la cheville arrière (à {MO["x_ar"]}) dessus, de {cm(ET["cheville_ext"])} de chaque côté du montant.</p></div>"""


def section_rendus():
    return f"""<h2 id="rendus">Rendus 3D</h2>
<p class="note">Disposition actuelle seulement ; les autres dispositions se rendent sur demande.</p>
{C.rendus_html("etageres", [("iso", "Le mur ouest en trois quarts depuis la pièce : les étagères au-dessus de l'enfilade."), ("detail", "Gros plan d'une entaille : le montant traverse la tablette, une cheville dessous devant, une dessus derrière.")])}"""


def meuble(e):
    compo = "".join(
        f'<tr><td class="mono">{t["rep"]}</td><td class="mono">{t["type"]}</td>'
        f'<td class="mono">{t["z"]}</td>'
        f'<td>M{t["a"] + 1} → M{t["b"] + 1}</td><td class="num">{cm(t["l"])}</td><td class="num">{t["n"]}</td>'
        f'<td class="num">{libre_txt(t)}</td></tr>' for t in e.ts)
    return f"""<div class="fig"><div class="scroll">{elevation(e)}</div>
<p class="cap">Disposition {escape(e.nom)}, le mur ouest vu depuis la pièce (le sud, côté passage, à gauche ; le coin nord à droite). L'enfilade est en tireté : les montants ne la touchent pas ({cm(MO["z0"] - EN["z1"])} de vide au-dessus d'elle) et ne touchent pas le plafond ({cm(M.H - MO["z1"])} dessous). {MO["n"]} montants M1 à M5 du nord au sud, à {PAS} d'axe en axe, centrés sur l'enfilade ; {len(e.ts)} tablettes ({escape(e.kit)}), {cm(e.metres)} m en tout ; repère, longueur et hauteur du dessus au-dessus de chacune. Chaque tablette déborde de {ET["debord"]} au-delà de l'axe de ses montants extrêmes ; aux deux bouts du mur, les tablettes dépassent de {cm(ET["debord"] - MO["axes"][0] + EN["y0"])} les bouts de l'enfilade ({cm(MO["axes"][-1] - MO["axes"][0] + 2 * ET["debord"])} sur {cm(EN["y1"] - EN["y0"])}). Les petits rectangles gris sont les bouts des chevilles, de part et d'autre de chaque montant.</p></div>
<div class="fig"><div class="scroll">{detail_dessus(e)}</div>
<p class="cap">Vues de dessus, vues depuis la pièce (le mur ouest en haut, le sud à gauche), les tablettes rangées du haut vers le bas sur quelques bandes (la hauteur de chacune est dans son étiquette) : la tablette touche le mur, les montants noirs {cm(MO["l"])} × {MO["p"]} sont dans ses entailles ; chevilles arrière en gris plein (sur la tablette), chevilles avant en tireté (dessous). Devant les montants, il reste {f(ET["x1"] - MO["p"])} pour les livres. Le tireté du fond est l'enfilade, {EN["p"]} de profondeur : les tablettes s'arrêtent à {f(ET["x1"])} du mur, {f(EN["p"] - ET["x1"])} en retrait de sa façade.</p></div>
<h3>Composition</h3>
<div class="fig scroll"><table><thead><tr><th>Repère</th><th>Longueur</th><th>Dessus</th><th>Montants</th><th class="num">Débit</th><th class="num">Entailles</th><th class="num">Libre au-dessus</th></tr></thead><tbody>{compo}</tbody></table></div>"""


def section_meuble():
    return f"""<h2 id="meuble">Le meuble</h2>
{par_dispo(meuble)}
<div class="fig"><div class="scroll">{detail_profil()}</div>
<p class="cap">Profil juste à côté d'un montant. La tablette va jusqu'au mur ({ET["p"]} de profondeur) et le montant passe dans une entaille de {cm(ET["entaille"][0])} × {cm(ET["entaille"][1])}. Deux chevilles en acier Ø 10 × {cm(ET["cheville"])}, peintes en noir, traversent le montant d'un flanc à l'autre et dépassent de {cm(ET["cheville_ext"])} de chaque côté sous les joues de l'entaille. La <b>cheville avant</b> (à {MO["x_av"]} du mur), sous la tablette, la porte ; la <b>cheville arrière</b> (à {MO["x_ar"]}), sur la tablette, l'empêche de basculer vers l'avant. Les deux colonnes de trous sont décalées de {cm(MO["decalage"])} : l'épaisseur de la tablette plus une cheville, moins la <b>rainure</b>.</p></div>
<p>La <b>rainure</b> : sous chaque tablette, au droit de la cheville avant, {cm(RA["l"] * 10)} mm de large et {cm(RA["prof"] * 10)} mm de profondeur (la moitié de la cheville), sur {f(RA["long"])} centrés sur chaque entaille ({cm(RA_COTE)} de chaque côté). La cheville avant y est logée : la tablette ne peut plus avancer vers la pièce (il faudrait la faire passer de toute son épaisseur entre les deux chevilles, en levant le devant de plus de 10°, et le montant dans l'entaille l'en empêche), et la cheville ne peut plus glisser en long dans son trou, les deux bouts de la rainure l'arrêtent. Rien ne se voit de face ; de dessous, une fente de {f(RA["long"])} autour de chaque montant, presque cachée par les bouts de cheville.</p>
<div class="fig"><div class="scroll">{detail_face()}</div>
<p class="cap">Une travée vue de face : la tablette passe devant les montants et déborde de {ET["debord"]} au-delà de l'axe du dernier (≈ {cm(ET["debord"] - MO["l"] / 2)} au-delà du bois), ce qui permet deux tablettes au même niveau sur des montants voisins sans se toucher ({cm(PAS - 2 * ET["debord"])} d'écart). Niveaux à 35 : sept pas de trous, des livres jusqu'à 30.</p></div>
<p>Une tablette se monte ou se descend de {MO["pas_trous"]} en {MO["pas_trous"]}, et peut glisser d'un montant : toutes les entailles sont à {PAS} l'une de l'autre, seule sa longueur est fixée.</p>"""


def section_presentoir():
    arr = MO["x_av"] - MO["x_ar"]
    cas = [("au milieu de la tablette", ET["p"] / 2), ("contre le rebord", ET["p"] - 3),
           ("tout contre les montants", MO["p"] + 2)]
    lig = "".join(f'<tr><td>{a}</td><td class="num">{f(x)}</td><td class="num">{cm(round(2 * (x - MO["x_av"]) / arr + 1, 1))}</td>'
                  f'<td class="num">{f"{coincement(x):.2f}".replace(".", ",")}</td><td class="num">{cm(round(0.2 / coincement(x), 1))}</td></tr>'
                  for a, x in cas)
    return f"""<h2 id="presentoir">Présentoir</h2>
<p>Possible à la place d'une courte, dans n'importe quelle disposition : une tablette dédiée, penchée de {PR["deg"]}° vers la pièce, pour une pochette de vinyle ou un livre d'art posé de face, sur les mêmes trous qu'une tablette à plat. Aucune disposition n'en a.</p>
<div class="fig"><div class="scroll">{presentoir()}</div>
<p class="cap">Profil juste à côté d'un montant (comme le profil à plat de la section Le meuble). La tablette est <b>pincée</b> : le poids posé devant la fait pivoter sur la cheville avant, qui la porte par-dessous ; l'arrière veut alors se soulever et la cheville arrière, par-dessus, l'en empêche. Comme à plat, la cheville avant est <b>prise dans une rainure</b> sous la tablette, plus profonde ici ({cm(PR["prof"] * 10)} mm au lieu de {cm(RA["prof"] * 10)}) parce que la tablette penchée descend de {cm(arr * PR["t"])} d'une cheville à l'autre. Le dessus reste plein ; entailles de 7,7 de profondeur au lieu de {cm(ET["entaille"][1])} (le montant traverse la tablette de biais). Un rebord de 2 × 2 collé devant retient ce qui est posé ; le devant descend de {cm(ET["p"] * PR["t"])}.</p></div>
<h3>Ce qui l'empêche de glisser vers la pièce</h3>
<p>Penchée, la tablette est poussée le long de sa pente (flèche verte) par ≈ {round(PR["s"] * 100)} % du poids posé. Deux choses la retiennent.</p>
<ul class="pistes">
<li><b>La rainure</b>, qui l'arrête quoi qu'il arrive : chargée ou vide, cognée par-dessous, ou le devant soulevé pour glisser une pochette. Pour avancer, la tablette devrait passer de toute son épaisseur ({cm(ET["ep"])}) entre les deux chevilles : il faudrait lever le devant de plus de {PR["deg"] + 10}° (de {PR["deg"]}° penchée à 10° relevée), ce que le montant, dans l'entaille, ne laisse pas faire.</li>
<li><b>Le coincement (arc-boutement)</b>, comme un tiroir qu'on tire par un coin et qui se bloque : plus on charge le devant, plus les deux chevilles serrent la tablette, et le frottement grandit avec ce serrage. Les chevilles n'étant qu'à {f(arr)} l'une de l'autre, ce serrage vaut plusieurs fois le poids posé ; la condition de non-glissement ne dépend alors pas du poids, seulement de la géométrie et du frottement. Chargée, la tablette ne pousse donc presque pas sur la rainure.</li>
</ul>
<div class="fig scroll"><table><thead><tr><th>Poids posé</th><th class="num">à … du mur</th><th class="num">serrage / poids</th><th class="num">frottement minimal</th><th class="num">marge avec 0,2</th></tr></thead><tbody>{lig}</tbody></table></div>
<p class="note">Frottement minimal = tan {PR["deg"]}° / (2 d / {f(arr)} + 1), d = distance du poids à la cheville avant. Acier sur bois : 0,2 à 0,6 selon les tableaux de frottement (voir les sources de la section Tenue). Le coincement disparaît dès qu'on soulève le devant : c'est la rainure qui tient alors.</p>
<ul class="pistes">
<li><b>Rainure du présentoir</b> : axe à {cm(PR["axe"])} du chant arrière (mesuré sur le dessous), {cm(PR["l"] * 10)} × {cm(PR["prof"] * 10)} mm, sur {f(RA["long"])} centrés sur chaque entaille comme à plat ; il reste {cm((ET["ep"] - PR["prof"]) * 10)} mm de chêne au-dessus, assez pour une tablette d'objets (≈ 10 kg). Profondeur à ajuster à l'essai sur une chute : la tablette doit se pincer à {PR["deg"]}°, sans jeu.</li>
<li><b>Pose et retrait</b> : comme une tablette à plat (chevilles avant, tablette posée dessus, chevilles arrière glissées par-dessus) ; pour la retirer, on sort les chevilles arrière.</li>
</ul>"""


def section_materiaux():
    lignes = "".join(f'<tr><td><b>{p}</b></td><td>{escape(r)}<br><span class="choix">{escape(w)}</span></td>'
                     f'<td>{escape(a)}</td></tr>' for p, r, w, a in MATERIAUX)
    return f"""<h2 id="materiaux">Matériaux</h2>
<div class="fig scroll"><table><thead><tr><th>Pièce</th><th>Retenu</th><th>Autres possibilités</th></tr></thead><tbody>{lignes}</tbody></table></div>
<p class="note">Le modèle est dessiné avec des montants de {cm(MO["l"])} × {MO["p"]} et des tablettes de {cm(ET["ep"])} ; les bruts retenus font {cm(TASSEAU["s"][0])} × {cm(TASSEAU["s"][1])} et {cm(PANNEAU["ep"])}. L'écart ne change ni l'aspect ni les charges, mais le perçage se règle sur les pièces réelles (voir le montage).</p>"""


def debit(e):
    lignes = "".join(f'<tr><td class="mono">{p["rep"]}</td><td>{escape(p["nom"])}</td><td class="num">{p["n"]}</td>'
                     f'<td class="mono">{p["dims"]}</td><td>{p["matiere"]}</td><td class="choix">{escape(p["de"])}</td></tr>'
                     for p in pieces(e))
    bandes_n = sum(len(p) for p in e.panneaux)
    return f"""<div class="fig scroll"><table><thead><tr><th>Repère</th><th>Pièce</th><th class="num">Nb</th><th>Dimensions</th><th>Matière</th><th>Tirée de</th></tr></thead><tbody>{lignes}</tbody></table></div>
<h3>Tablettes : refente des plans de chêne</h3>
<div class="fig"><div class="scroll">{decoupe_panneaux(e)}</div>
<p class="cap">Disposition {escape(e.nom)} : {len(e.panneaux)} plans de {PANNEAU["l"]} × {PANNEAU["p"]}, refendus en {bandes_n} bandes de {ET["p"]} (trait de scie {cm(KERF * 10)} mm, il reste {cm(PANNEAU["p"] - 2 * ET["p"] - KERF)} pour dresser) ; les bouts sont d'abord recoupés d'équerre ({cm(DRESSAGE * 10)} mm). En rouge, le chant arrondi d'usine : il fait le devant de chaque tablette, le trait de refente va contre le mur. Les longueurs se coupent après la refente, à la scie circulaire sur rail.</p></div>
<h3>Montants et chevilles</h3>
<div class="fig"><div class="scroll">{decoupe_barres(e)}</div>
<p class="cap">{N_TASSEAUX} tasseaux de {cm(TASSEAU["l"])} : {PAR_TASSEAU} montants de {cm(L_MONTANT)} par tasseau ; il ne reste que {cm(TASSEAU["l"] - PAR_TASSEAU * L_MONTANT - KERF)} sur les deux premiers, à mesurer en magasin (bouts fendus : prendre un tasseau de plus). {e.n_ronds} ronds de 1 m : {e.par_rond} chevilles de {cm(ET["cheville"])} par rond (trait de scie à métaux {cm(KERF_METAL * 10)} mm), {e.n_ronds * e.par_rond} en tout pour {e.chevilles} utiles.</p></div>"""


def section_debit():
    t1 = D0.ts[0]
    pos = ", ".join(cm(x) for x in t1["entailles"])
    return f"""<h2 id="debit">Débit et découpe</h2>
{par_dispo(debit)}
<h3>Perçage d'un montant</h3>
<div class="fig"><div class="scroll">{percage()}</div>
<p class="cap">Le même pour toutes les dispositions. Les cotes partent du bas du montant (z {MO["z0"]}). Colonne <b>arrière</b> à {MO["x_ar"]} du mur, colonne <b>avant</b> à {MO["x_av"]} : {len(MO["trous_av"])} trous Ø 10 par colonne, tous les {MO["pas_trous"]}, traversants (les deux flancs). Les deux colonnes sont décalées de {cm(MO["decalage"])} en hauteur, l'épaisseur de la tablette plus une cheville moins la rainure ({cm(RA["prof"] * 10)} mm) : avec une tablette de {cm(PANNEAU["ep"])}, ce décalage devient {cm(PANNEAU["ep"] + MO["trou"] - RA["prof"])}. Face avant : {EU["vis"]} vis 6 × 120 dans des lamages Ø 15 de 1 de profondeur, rebouchés et peints ; elles passent entre les trous.</p></div>
<h3>Entaille d'une tablette</h3>
<div class="fig"><div class="scroll">{entaille()}</div>
<p class="cap">Les entailles se taillent dans le chant arrière : deux traits de scie sauteuse (ou scie à main) de {cm(ET["entaille"][1])}, puis le fond au ciseau à bois ; {cm(ET["entaille"][0] - MO["l"])} de jeu en largeur, {cm(ET["entaille"][1] - MO["p"])} en profondeur. Elles sont à {ET["debord"]} de chaque bout puis à {PAS} l'une de l'autre (sur une 244, à {pos} du bout sud).</p></div>"""


# ------------------------------------------------------------------ tenue du mécanisme (Eurocode 5, EN 338)
# Vérification simplifiée, à la manière de l'Eurocode 5 : résistance caractéristique × kmod / γM, comparée à l'effort ×
# 1,5 (charge d'exploitation). kmod = 0,7 (stockage, longue durée, intérieur sec), γM = 1,3 (bois massif) : de mémoire.
TN = dict(d=10, fm=30, kmod=0.7, kmod_inst=1.1, gm=1.3, gq=1.5, rho=320, fc90=8.0, fy=235, f_contact=15,
          e=(MO["p"] + ET["x1"]) / 2, vis_h=(5, L_MONTANT / 2 + 0.5, L_MONTANT - 4))
TN["fh0"] = 0.082 * (1 - 0.01 * TN["d"]) * TN["rho"]                   # MPa, portance d'une broche, parallèle au fil
_bout = ET["cheville_ext"] * 10                                            # mm
_w = math.pi * TN["d"] ** 3 / 32                                           # mm³
R_ACIER = 2 * TN["fy"] * _w / (_bout / 2)                                  # N, deux bouts chargés en leur milieu
R_MONTANT = TN["fh0"] * TN["d"] * MO["l"] * 10                             # N (caractéristique)
_t_rain = (ET["ep"] - RA["prof"]) * 10                                   # mm de chêne au-dessus de la rainure
_b_rain = (RA["long"] - ET["entaille"][0]) * 10                            # mm : la rainure sans l'entaille
_levier = (MO["p"] + ET["x1"]) / 2 - MO["x_av"]                            # cm, charge → cheville avant
R_FLEX = TN["fm"] * _b_rain * _t_rain ** 2 / 6 / (_levier * 10)            # N par montant (caractéristique)
A_JOUE = 2 * TN["d"] * (_bout + TN["f_contact"])                           # mm², deux bouts, diffusion de 15 d'un côté
R_JOUE = TN["fc90"] * A_JOUE                                               # N (caractéristique)
FACTEUR = max(e.ch["facteur"] for e in DISPOS)                             # milieu d'une longue
ARR = (MO["x_av"] - MO["x_ar"])                                            # bras de levier de la cheville arrière


def kn(newtons):
    return f"{newtons / 1000:.2f}".replace(".", ",")


def taux(effort, r_k, bois=True, kmod=None):
    r_d = r_k * (kmod or TN["kmod"]) / TN["gm"] if bois else r_k
    return TN["gq"] * effort / r_d


# effort au bord d'une courte (2 montants) qui écrase les joues : charge caractéristique et charge « de calcul »
_LEVIER = (ET["x1"] - MO["x_av"]) / ARR + 1                                # cheville avant : P / 2 × (27 / 3 + 1)
P_RUINE = R_JOUE / _LEVIER * 2 / 9.81                                      # kg
P_CALCUL = R_JOUE * TN["kmod_inst"] / TN["gm"] / TN["gq"] / _LEVIER * 2 / 9.81


def fixation(e):
    """Efforts sur les vis du montant le plus chargé : cisaillement partagé, arrachement du haut par le moment."""
    w = e.ch["max"] * 9.81
    m = w * TN["e"] / 100
    hs = [h / 100 for h in TN["vis_h"]]
    t_haut = m * hs[-1] / sum(h * h for h in hs)
    v = w / EU["vis"]
    return dict(w=w, m=m, t=t_haut, v=v, r=math.hypot(t_haut, v))


SOURCES_TENUE = [
    ("https://roymech.org/Related/Construction/Timber_connections.html", "RoyMech, assemblages bois selon l'Eurocode 5 (portance des broches, pinces et entraxes)"),
    ("https://roymech.org/Related/Construction/Timber", "RoyMech, classes de résistance EN 338 (chêne D30)"),
    ("https://www.lawson-his.co.uk/fischer-535980-duopower-big-pack-8-x-40mm-pack-of-120", "fischer DuoPower 8 × 40 : charges recommandées (béton, brique pleine, plaque de plâtre)"),
    ("https://www.bouwkampioen.be/fr/mwdownloads/download/link/id/3871", "fiche technique fischer DuoPower : carreau de plâtre, coefficient de sécurité 7"),
    ("https://forums.futura-sciences.com/attachments/physique/104861d1268375997-coefficient-de-frottement-beton-humide-polyurethane-coefficients-de-frottement.pdf", "tableau de coefficients de frottement (bois sur métal 0,2 à 0,6)"),
]


def tenue_dispo(e):
    ch, fx = e.ch, fixation(e)
    return (f'<p><b>Disposition {escape(e.nom)}</b> : ≈ {ch["poids"]:.0f} kg pleine ; le montant le plus chargé, '
            f'M{ch["m"] + 1}, porte ≈ {ch["max"]:.0f} kg. Sur ses vis : ≈ {fx["v"] / 9.81:.0f} kg de cisaillement chacune, '
            f'et ≈ {fx["t"] / 9.81:.0f} kg d\'arrachement sur celle du haut (la charge est à ≈ {cm(TN["e"])} du mur, le '
            f'montant bascule sur son pied), soit ≈ {kn(fx["r"])} kN sur la vis du haut.</p>')


def section_charges():
    av, ar = EU["avant"], EU["arriere"]
    lig = [
        ("Cheville d'acier", "pli d'un bout (Ø 10, porte-à-faux de " + cm(ET["cheville_ext"]) + ")",
         av * FACTEUR, R_ACIER, taux(av * FACTEUR, R_ACIER, bois=False), f"acier courant S235, {TN['fy']} MPa"),
        ("Montant (sapin)", "écrasement du bois sous la cheville avant, dans le sens du fil",
         av * FACTEUR, R_MONTANT, taux(av * FACTEUR, R_MONTANT),
         f"portance Eurocode 5 : 0,082 (1 − 0,01 d) ρk = {cm(TN['fh0'])} MPa, ρk {TN['rho']} (bois non classé, pris en C18)"),
        ("Tablette (chêne) sur la cheville avant", "écrasement de la joue, en travers du fil",
         av * FACTEUR, R_JOUE, taux(av * FACTEUR, R_JOUE),
         f"compression transversale D30 : {cm(TN['fc90'])} MPa sur 1 × 3 par bout (contact de 1,5 et diffusion de 1,5)"),
        ("Tablette (chêne) sous la cheville arrière", "même chose, sur le dessus",
         ar * FACTEUR, R_JOUE, taux(ar * FACTEUR, R_JOUE), "idem"),
        ("Tablette (chêne) au droit de la rainure", "flexion du porte-à-faux là où elle est amincie",
         EU["effort"] * FACTEUR, R_FLEX, taux(EU["effort"] * FACTEUR, R_FLEX),
         f"flexion D30 : {TN['fm']} MPa, sur {cm(_t_rain / 10)} d'épaisseur et {cm(_b_rain / 10)} de large seulement "
         f"(la rainure moins l'entaille), charge à {cm(_levier)} de la cheville avant"),
    ]
    verdict = lambda u: "large" if u < 0.4 else ("correct" if u < 0.8 else ("juste" if u <= 1 else "insuffisant"))
    rows = "".join(f'<tr><td><b>{a}</b><br><span class="choix">{b}</span></td><td class="num">{F / 9.81:.0f} kg</td>'
                   f'<td class="num">{R / 9.81:.0f} kg</td><td class="num">{round(u * 100)} %</td><td>{verdict(u)}</td>'
                   f'<td class="choix">{escape(n)}</td></tr>' for a, b, F, R, u, n in lig)
    fx = fixation(max(DISPOS, key=lambda e: e.ch["max"]))
    src = "".join(f'<li><a href="{u}">{escape(t)}</a></li>' for u, t in SOURCES_TENUE)
    return f"""<h2 id="charges">Tenue : poids et chute</h2>
<p>Recherche faite sur les règles de l'Eurocode 5 (assemblages par broches), les classes de bois EN 338 et les fiches de chevilles fischer (sources en bas de section). Le mécanisme est une <b>pince</b> : la tablette pivote sur la cheville avant, et la cheville arrière, à {f(ARR)} seulement derrière, retient l'arrière qui veut se soulever. Avec la charge à ≈ {cm(TN["e"])} du mur, la cheville arrière reprend ≈ {cm(round(EU["arriere"] / EU["effort"], 1))} fois le poids posé, et la cheville avant ce poids plus ce qu'elle retient. Cas étudié : {PAS} de tablette pleine de livres ({M.CHARGE_LIVRES} kg/m) par montant, × {cm(FACTEUR)} au montant du milieu d'une longue (le plus chargé).</p>
<h3>Ce qui peut céder</h3>
<div class="fig scroll"><table><thead><tr><th>Pièce</th><th class="num">Effort</th><th class="num">Résistance</th><th class="num">Taux</th><th>Verdict</th><th>Base</th></tr></thead><tbody>{rows}</tbody></table></div>
<p class="note">Résistance caractéristique ; taux = effort × {cm(TN["gq"])} / (résistance × {cm(TN["kmod"])} / {cm(TN["gm"])}) pour le bois, effort × {cm(TN["gq"])} / résistance pour l'acier (méthode de l'Eurocode 5, coefficients de mémoire). En dessous de 100 %, la pièce tient avec la sécurité de la norme. Les modèles de la joue et de la rainure sont prudents : la joue, calculée comme une broche dans un trou, porterait plusieurs fois plus ; en flexion, toute la longueur de la tablette participe, pas seulement les {cm(_b_rain / 10)} autour de l'entaille.</p>
<ul class="pistes">
<li><b>Le poids des livres : ça tient.</b> Les points les plus chargés sont dans la tablette en chêne, au milieu d'une longue pleine : la flexion là où la rainure l'amincit ({round(taux(EU["effort"] * FACTEUR, R_FLEX) * 100)} %, calcul très prudent ; {round(taux(EU["effort"] * FACTEUR, R_FLEX) * ((ET["ep"] - RA["prof"]) / ET["ep"]) ** 2 * 100)} % sans rainure) et son appui sur les chevilles ({round(taux(av * FACTEUR, R_JOUE) * 100)} %) : la marge existe, sans être énorme ; une rainure plus profonde que {cm(RA["prof"] * 10)} mm n'apporterait rien et affaiblirait la tablette. Avec le temps, le chêne peut se marquer d'un demi-millimètre sous les chevilles : la tablette pencherait alors un peu vers l'avant (≈ 0,5 mm sur {f(ARR)} de levier, soit ≈ 5 mm au bord). L'acier ({round(taux(av * FACTEUR, R_ACIER, bois=False) * 100)} %) et le montant ({round(taux(av * FACTEUR, R_MONTANT) * 100)} %) sont larges. Correction de V1.4 : le montant est chargé dans le sens du fil (portance ≈ {cm(TN["fh0"])} MPa), pas en travers (2,5).</li>
<li><b>Quelqu'un qui s'appuie ou s'accroche au bord</b> d'une courte : ≈ {P_CALCUL:.0f} kg tirés au bord avec la sécurité de la norme, et vers {round(P_RUINE, -1):.0f} kg les joues de chêne s'écrasent et la tablette pique du nez (les chevilles d'acier ne cassent pas). C'est une étagère, pas une échelle : un enfant qui grimpe est le vrai risque.</li>
<li><b>Les chevilles peuvent-elles glisser de côté ?</b> La cheville avant, celle qui porte, non : elle est logée dans la rainure, dont les deux bouts l'arrêtent. La tablette ne peut pas non plus avancer vers la pièce. La cheville arrière, elle, n'est arrêtée par rien : chargée, le frottement la tient (≈ 0,2 à 0,6 fois l'effort, des dizaines de kilos) ; sur une tablette vide ou qu'on cogne, elle pourrait sortir de 1,5 et la tablette basculer de ce côté. Parade : un ajustement serré (la cheville entre au maillet, sortie avec un chasse-goupille), vérifié sur le gabarit ; ou un tour de gaine thermorétractable noire sur la partie dans le montant.</li>
<li><b>Les trous sont près des faces du montant.</b> L'Eurocode 5 demande au moins 3 d (30) entre une broche et le bord du bois ; ici {f(MO["x_ar"] * 10)} côté mur et {f((MO["p"] - MO["x_av"]) * 10)} côté pièce. L'entraxe dans une colonne ({MO["pas_trous"] * 10} = 5 d) et entre les colonnes ({f(ARR * 10)} = 3 d) est juste conforme. Les efforts sont faibles, mais le risque est la fente du montant le long d'une colonne de trous, au perçage ou sur un nœud : percer à la mèche à pointe de centrage avec un martyr, refuser un tasseau à nœuds dans la zone percée. Un montant de 44 × 95 (Leroy Merlin) remettrait les pinces aux normes (trous à 3 et 6,5 du mur) et allongerait le levier de la cheville arrière ({cm(3.5)} au lieu de {f(ARR)}, −15 % d'effort) : à décider.</li>
</ul>
<h3>Fixation au mur</h3>
{par_dispo(tenue_dispo)}
<p>C'est la cloison ouest (cellier et WC) qui porte tout, comme pour les variantes Vitsoe et fait maison de la <a href="salon-bibliotheque-fixation.html">page Fixations</a> : sa nature décide de la quincaillerie. Repère : une cheville fischer DuoPower 8 × 40 est donnée pour 62 kg en brique pleine, 15 kg en plaque de plâtre de 12,5 et ≈ 0,25 kN en carreau de plâtre (fiche fischer, sécurité de 7 comprise ; la colonne du carreau de plâtre est lue dans l'ordre des tailles, à confirmer). Au pire, la vis du haut reçoit ≈ {kn(fx["r"])} kN.</p>
<ul class="pistes">
<li><b>Brique ou béton</b> : {EU["vis"]} vis Ø 6 × 120 par montant (à 5, 60 et 115 du bas, par la face avant), chevilles nylon 8 × 50, têtes noyées dans un lamage Ø 15 bouché et peint : large.</li>
<li><b>Carreau de plâtre</b> : la vis du haut est à la charge recommandée. Passer à {EU["vis"] + 1} vis par montant (une de plus en haut, à 100), avec des chevilles de 10 (≈ 0,35 kN en carreau de plâtre chez fischer) ou des chevilles spéciales carreau de plâtre.</li>
<li><b>Plaque de plâtre sur ossature</b> : les rails sont à 60 ; passer le pas à 60 pour visser chaque montant dans un rail (débords ramenés à ≈ 9 aux deux bouts, tablettes plus longues), ou renforcer la cloison. Des chevilles dans la plaque seule : non.</li>
<li><b>Réseaux</b> : repérer les gaines du mur ouest avant de percer (détecteur), surtout côté WC.</li>
</ul>
<p class="note">Sources consultées le 30/10/2026 :</p><ul class="note">{src}</ul>
<p class="note">Non trouvé en ligne et pris de mémoire, à vérifier : kmod et γM de l'Eurocode 5, nuance de l'acier des ronds Weldom (supposé S235), classe du sapin Weldom (non classé, pris en C18). L'essai de charge du montage (chute de tablette, deux chevilles, 15 kg pendant une semaine) reste la vérification qui compte.</p>"""


def achats_dispo(e):
    n_rel = sum(1 for a in e.achats if a["statut"] == "relevé")
    return (f'{table_achats(e)}<p><b>Total : {euros(e.total)}</b>, dont {euros(e.releve)} de prix relevés ({n_rel} '
            f'lignes) et {euros(e.estime)} estimés. Sans livraison ni outillage.</p>')


def section_achats():
    mg = MAGASINS["weldom"]
    return f"""<h2 id="achats">Achats et prix</h2>
<p>D'abord chez <b><a href="{mg["url"]}">{mg["nom"]}</a></b> ({mg["adresse"]}) ; il n'a pas de plan de chêne de 2,6 : les tablettes viennent de <b>Castorama</b> (Leroy Merlin n'a pas de chêne dans ce format en ligne). Prix TTC lus en ligne le {DATE}, stock non vérifié : tout est à confirmer en magasin.</p>
{par_dispo(achats_dispo)}
<p>Les plans de 250 font ≈ 31 kg chacun : il faut un véhicule assez long, ou la livraison Castorama (non comptée). Seuls les plans de chêne et les ronds d'acier changent d'une disposition à l'autre.</p>
<p class="note">Prix relevés : lus sur la fiche du produit par une recherche web le {DATE} (sauf la cheville nylon, relevée le 26/10/2026 pour le meuble SDB) ; un écart existe parfois entre la fiche et la liste du rayon (laque : 27,70 € et 25,90 €). Prix estimés : ordre de grandeur du rayon, sans fiche. À prévoir si l'atelier ne les a pas : mèche à bois Ø 10 à pointe de centrage, mèche Forstner Ø 15, lame de scie à métaux (non comptées).</p>"""


def section_montage():
    etapes = [
        ("Sonder la cloison ouest", "Percer un trou d'essai Ø 6 à l'emplacement d'une vis, derrière l'enfilade : poussière blanche et "
         "résistance franche = carreau de plâtre ; rouge = brique ; vide après 1,3 = plaque sur ossature (pas à 60, voir les points à valider). "
         "Passer le détecteur de réseaux sur toute la zone."),
        ("Débiter", "Refendre les plans en bandes de 32, puis couper les tablettes à longueur ; couper les montants à "
         f"{cm(L_MONTANT)} et les chevilles à {cm(ET['cheville'])}, bouts chanfreinés à la lime."),
        ("Faire le gabarit de perçage", "Dans la chute du dernier tasseau, percer à la perceuse à colonne deux trous Ø 10 "
         f"traversants aux cotes du plan de perçage (à {MO['x_ar']} et {MO['x_av']} du dos, décalés de l'épaisseur mesurée de la "
         f"tablette plus 1, moins {cm(RA['prof'] * 10)} mm de rainure). Vérifier avec une vraie tablette rainurée et deux chevilles : elle doit entrer sans forcer et ne pas jouer."),
        ("Percer les montants", "Pointer les trous sur un montant avec le gabarit, puis percer à la colonne avec une butée de "
         "profondeur et une cale de bout : les cinq montants identiques, bout bas contre la cale. Mèche à pointe de centrage, "
         "martyr dessous (le bois éclate à la sortie). Lamages Ø 15 et avant-trous des vis sur la face avant."),
        ("Entailler les tablettes", f"Tracer les axes depuis un bout ({ET['debord']}, puis tous les {PAS}), présenter chaque "
         f"tablette sur les montants couchés côte à côte pour vérifier, puis scier et ciseler les entailles {cm(ET['entaille'][0])} × "
         f"{cm(ET['entaille'][1])}. Puis les rainures, dessous : défonceuse, fraise droite Ø 10, guide parallèle contre le "
         f"chant arrière (axe à {f(MO['x_av'])}), deux largeurs décalées de 1 mm, deux passes en profondeur jusqu'à "
         f"{cm(RA['prof'] * 10)} mm ; {f(RA['long'])} de long centrés sur chaque entaille, bouts tracés au crayon et "
         "équarris au ciseau. Essayer d'abord sur la chute : la tablette doit se pincer entre les chevilles sans jeu."),
        ("Finir", "Poncer (120 puis 180). Tablettes : trois couches d'huile sur toutes les faces, entailles comprises. Montants : "
         "deux couches de laque noire mate. Chevilles : dégraisser, apprêt antirouille, une couche de laque."),
        ("Essai de charge", "Une chute de tablette entaillée sur la chute de montant, deux chevilles, 15 kg de livres pendant une "
         "semaine : la tablette ne doit ni pencher ni tasser le bois autour de la cheville avant."),
        ("Poser les montants", f"Tracer au laser l'horizontale du bas des montants (z {MO['z0']}) et les verticales des axes "
         f"(à {cm(MO['axes'][0])} du coin nord puis tous les {PAS}). Présenter chaque montant, pointer, percer le mur, "
         "cheviller, visser ; contrôler l'aplomb au niveau sur deux faces avant de serrer. Un écart de 2 mm de hauteur entre "
         "deux montants se voit sur une tablette de 134 : contrôler au laser les trous d'un même niveau."),
        ("Monter les tablettes", "Pour chaque tablette, du bas vers le haut : chevilles avant dans les trous voulus, tablette "
         "posée dessus (les montants dans les entailles, les chevilles avant dans les rainures), chevilles arrière "
         "glissées par-dessus. Reboucher les lamages, retoucher la laque."),
    ]
    lis = "".join(f"<li><b>{t}</b> : {escape(c)}</li>" for t, c in etapes)
    return f"""<h2 id="montage">Outils et montage</h2>
<p><b>Outils</b> : scie circulaire et rail de guidage (ou découpe en magasin si le service existe, à vérifier), scie sauteuse, ciseau à bois de 20, défonceuse et fraise droite Ø 10 (celle de la SDB), perceuse à colonne (ou support de perceuse ; à main, les trous ne traversent pas {cm(MO["l"])} d'équerre), mèches bois Ø 10 et Forstner Ø 15, perceuse et mèche Ø 8 pour le mur, scie à métaux et étau, lime, ponceuse, laser croix, niveau, détecteur de réseaux, pinceaux.</p>
<ol class="pistes">{lis}</ol>"""


def section_valider():
    def compo(e):
        return (f'<li><b>Composition {escape(e.nom)}</b> : {len(e.ts)} tablettes ({escape(e.kit)}), {cm(e.metres)} m, '
                f'dessus à {", ".join(str(z) for z in e.niveaux)}.</li>')
    return f"""<h2 id="valider">Points à valider</h2>
<ul class="pistes">
<li><b>Disposition</b> à choisir parmi les {len(DISPOS)} ; le plan du salon et les rendus montrent l'actuelle.</li>
{"".join(f'<div class="dv" data-d="{e.cle}">{compo(e)}</div>' for e in DISPOS)}
<li><b>Rainures</b> : profondeur ({cm(RA["prof"] * 10)} mm à plat, {cm(PR["prof"] * 10)} pour un présentoir) et décalage des trous à essayer sur une chute avec le gabarit avant de rainurer les tablettes : la tablette doit se pincer sans jeu.</li>
<li><b>Pas des montants</b> : {PAS} si la cloison est pleine (carreau de plâtre, brique) ; 60 si c'est une plaque sur ossature, pour visser dans les rails.</li>
<li><b>Nature de la cloison ouest</b> : à relever (sondage, étape 1 du montage) ; elle décide des chevilles.</li>
<li><b>Sections réelles</b> : tasseaux Weldom {cm(TASSEAU["s"][0])} × {cm(TASSEAU["s"][1])} et plan Castorama de {cm(PANNEAU["ep"])}, contre {cm(MO["l"])} × {MO["p"]} et {cm(ET["ep"])} dans le modèle ; longueur réelle des tasseaux (deux montants de {cm(L_MONTANT)} dans {cm(TASSEAU["l"])}).</li>
<li><b>Stock et prix</b> en magasin (Weldom d'abord), transport des plans de 250.</li>
</ul>"""


CSS = "".join(f'body[data-d="{e.cle}"] .dv[data-d="{e.cle}"]{{display:block}}' for e in DISPOS) + f"""
.dv{{display:none}}body:not([data-d]) .dv[data-d="{D0.cle}"]{{display:block}}
.dgrid{{display:grid;grid-template-columns:repeat(auto-fill,minmax(230px,1fr));gap:10px;margin:14px 0}}
.dmini{{font:inherit;color:var(--ink);text-align:left;background:var(--panel);border:1px solid var(--line);border-radius:12px;padding:10px;cursor:pointer;display:flex;flex-direction:column;gap:4px}}
.dmini:hover{{border-color:var(--muted)}}
.rain{{fill:none;stroke:var(--ink);stroke-width:.9;stroke-dasharray:4 2}}
.fl{{stroke:#c2410c;stroke-width:1.6;fill:none}}.flh{{fill:#c2410c}}
.glis .fl{{stroke:#4d9a3a}}.glis .flh{{fill:#4d9a3a}}
.dmini[aria-pressed="true"]{{border-color:var(--ink);box-shadow:0 0 0 1px var(--ink)}}
.dmini .mono{{font-size:12px;color:var(--muted);white-space:normal}}
.dmini svg{{display:block;width:100%;height:auto;margin:4px 0}}
.dmini .cap{{margin:0}}
.vbar .dsel{{display:flex;flex-wrap:wrap;align-items:center;gap:4px}}
@media (max-width:480px){{.vbar{{flex-wrap:wrap}}.vbar .dsel{{order:9;width:100%;flex-wrap:nowrap;overflow-x:auto}}.vbar .dsel button{{white-space:nowrap}}}}
"""

JS = """
(function () {
  var cle = "salon-etageres-dispo", ds = %s;
  function lit() { try { return localStorage.getItem(cle); } catch (e) { return null; } }
  function garde(v) { try { localStorage.setItem(cle, v); } catch (e) {} }
  function pose(d) {
    if (ds.indexOf(d) < 0) d = ds[0];
    document.body.setAttribute("data-d", d);
    document.querySelectorAll("button[data-d]").forEach(function (b) { b.setAttribute("aria-pressed", b.dataset.d === d); });
    garde(d);
  }
  document.querySelectorAll("button[data-d]").forEach(function (b) {
    b.addEventListener("click", function () { pose(b.dataset.d); });
  });
  pose(lit() || ds[0]);
})();
""" % json.dumps([e.cle for e in DISPOS])


def page():
    lignes = (f'<tr><td class="mono">V1.8</td><td class="mono">30/10/2026</td><td>Rainure à la défonceuse sous toutes les '
              f'tablettes, comme au présentoir : {cm(RA["l"] * 10)} × {cm(RA["prof"] * 10)} mm au droit de la cheville avant, '
              f'sur {f(RA["long"])} centrés sur chaque entaille ; la tablette ne peut plus avancer et la cheville avant ne peut '
              f'plus glisser en long. Colonne avant des trous remontée de {cm(RA["prof"] * 10)} mm (décalage {cm(MO["decalage"])} au '
              f'lieu de {cm(MO["decalage"] + RA["prof"])}) ; profil, vue de face, entaille, vue iso et plan de perçage redessinés ; '
              f'Tenue : flexion de la tablette amincie ({round(taux(EU["effort"] * FACTEUR, R_FLEX) * 100)} %, calcul prudent) ; '
              f'présentoir sur les mêmes trous, rainure de {cm(PR["prof"] * 10)} mm. Prix inchangés ; rendus 3D non refaits.</td></tr>')
    lignes += (f'<tr><td class="mono">V1.7</td><td class="mono">30/10/2026</td><td>Présentoir : la butée vissée est '
              f'remplacée par une rainure à la défonceuse sous la tablette ({cm(PR["l"] * 10)} × {cm(PR["prof"] * 10)} mm, axe à '
              f'{cm(PR["axe"])} du chant arrière), où la cheville avant est prise ; plus de feuillure sur le dessus. Pose et '
              f'retrait à la main, devant levé à l\'horizontale. Prix et dispositions inchangés.</td></tr>')
    lignes += (f'<tr><td class="mono">V1.6</td><td class="mono">30/10/2026</td><td>Tablettes penchées le long '
              f'du mur retirées (page, pièces, vue iso). La section devient Présentoir : ce qui l\'empêche de glisser vers la '
              f'pièce, chiffré (coincement entre les deux chevilles, frottement minimal {cm(round(coincement(ET["p"] / 2), 2))} '
              f'au milieu pour 0,2 à 0,6 acier sur bois), et une butée en chêne vissée sous la tablette, contre la cheville '
              f'avant, qui la bloque même vide ou soulevée. Prix et dispositions inchangés.</td></tr>')
    lignes += (f'<tr><td class="mono">V1.5</td><td class="mono">30/10/2026</td><td>Dispositions Niche et Inclinées '
              f'retirées : restent {", ".join(e.nom for e in DISPOS)}. Tablettes inclinées redessinées : vue de face entre deux '
              f'montants avec les livres, vue iso du bout bas coupé dans la feuillure, présentoir en profil avec ce qui le '
              f'retient (la tablette pincée entre la cheville avant, dessous, et la cheville arrière, dessus). Section '
              f'Tenue : recherche sur l\'Eurocode 5, l\'EN 338 et les fiches fischer ; tableau de ce qui peut céder (acier, '
              f'montant, appui du chêne, le plus chargé à {round(taux(EU["avant"] * FACTEUR, R_JOUE) * 100)} %), effort '
              f'accidentel au bord, glissement des chevilles, pinces des trous sous le minimum de la norme, fixation au mur '
              f'selon la cloison ; correction de V1.4 (montant chargé dans le sens du fil). Prix inchangés.</td></tr>')
    lignes += (f'<tr><td class="mono">V1.4</td><td class="mono">30/10/2026</td><td>Section Dispositions : cinq '
              f'nouvelles dispositions à côté de l\'actuelle (Rangs, Décalée, Escalier, Niche, Inclinées), avec des hauteurs '
              f'de dessus variées, sur les mêmes montants percés de {M.NIVEAUX[0]} à {M.NIVEAUX[1]} ; les longues tablettes '
              f'divisées pour n\'avoir que deux longueurs (134 et 79), tirées des deux mêmes plans de chêne ; bouton '
              f'Disposition dans la barre du haut, qui fait passer toute la page (élévation, vues de dessus, vue iso, '
              f'composition avec la hauteur libre au-dessus de chaque tablette, débit, charges, achats). Section Tablettes '
              f'inclinées : penchées le long du mur d\'un pas de trous (5,2°, feuillure de ≈ '
              f'0,7, pièces dédiées, charges légères) et présentoir penché vers la pièce. Disposition '
              f'actuelle et plan du salon inchangés ; rendus 3D de l\'actuelle seulement.</td></tr>')
    lignes += '<tr><td class="mono">V1.3</td><td class="mono">29/10/2026</td><td>Chevilles dessinées rondes (acier rond Ø 10) dans la vue iso et les rendus, au lieu de petites boîtes carrées.</td></tr>'
    lignes += '<tr><td class="mono">V1.2</td><td class="mono">29/10/2026</td><td>Tablettes d\'une seule pièce dans la vue iso et les rendus : plus de trait de joint entre la bande avant et les morceaux entre les entailles (artefact du découpage en boîtes) ; arêtes des tablettes arrondies (5 mm) dans les rendus. Géométrie et prix inchangés.</td></tr>'
    lignes += '<tr><td class="mono">V1.1</td><td class="mono">29/10/2026</td><td>Vue iso du meuble et détail agrandi d\'une entaille (montant, tablette entaillée, chevilles) ; section Rendus 3D (mur ouest en trois quarts, gros plan d\'une entaille), images à produire. Géométrie et prix inchangés.</td></tr>'
    lignes += f'<tr><td class="mono">V1.0</td><td class="mono">{DATE}</td><td>Première version de la page, d\'après l\'étude du salon V4.23 : élévation du mur, vues de dessus, profil et travée ; matériaux et alternatives ; liste des pièces, refente des plans de chêne, débit des tasseaux et des ronds, plan de perçage d\'un montant, entaille ; charges et fixation ; achats chiffrés ({euros(D0.total)}, dont {euros(D0.estime)} estimés) ; outils et montage ; points à valider.</td></tr>'
    pitch = par_dispo(lambda e: (
        f'<p class="pitch">{MO["n"]} montants peints en noir, vissés au mur ouest au-dessus de l\'enfilade sans toucher '
        f'ni elle ni le plafond, et {len(e.ts)} tablettes en chêne massif entaillées autour d\'eux, pincées par des '
        f'chevilles d\'acier : disposition <b>{escape(e.nom)}</b>, {cm(e.metres)} m de rayonnage, {e.n_tailles} '
        f'longueur{"s" if e.n_tailles > 1 else ""} de tablette, pour ≈ {e.total:.0f} € de matériaux.</p>'))
    outils = ('<span class="dsel"><span>Disposition</span>' + "".join(
        f'<button type="button" data-d="{e.cle}" aria-pressed="{str(e is D0).lower()}">{escape(e.nom)}</button>'
        for e in DISPOS) + "</span>")
    corps = f"""<div class="kicker">Salon · Étagères · {VERSION}</div>
<h1>Étagères sur montants percés</h1>
{pitch}

{section_dispositions()}

{section_iso()}

{section_meuble()}

{section_presentoir()}

{section_rendus()}

{section_materiaux()}

{section_debit()}

{section_charges()}

{section_achats()}

{section_montage()}

{section_valider()}

<p class="note">Repère : origine au coin nord-ouest du salon, y vers le sud, z depuis le sol, cotes en cm. Géométrie : <span class="mono">3d/salon/modele.py</span> (salon {M.VERSION}, <span class="mono">DISPOSITIONS</span>) ; page : <span class="mono">3d/salon/etageres.py</span>. Le reste du salon : <a href="{C.SALON}">plan du salon</a>.</p>

<section id="changements">
<h2>Changements</h2>
<div class="scroll"><table><thead><tr><th>Version</th><th>Date</th><th>Changements</th></tr></thead>
<tbody>{lignes}</tbody></table></div>
</section>"""
    return C.gabarit("Étagères · salon", "etageres", corps, css=CSS, outils=outils, script=JS)


if __name__ == "__main__":
    C.ecrire(C.PAGES["etageres"], page())
    for e in DISPOS:
        print(f'{e.cle:10} {e.kit:28} {cm(e.metres):>5} m  {len(e.panneaux)} plans  {e.chevilles} chevilles  '
              f'montant max {e.ch["max"]:.0f} kg  {euros(e.total)}')
