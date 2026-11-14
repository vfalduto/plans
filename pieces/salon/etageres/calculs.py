"""Calculs d'une disposition des étagères : tablettes, débit, bandes, charges, achats, présentoir dérivé, tenue.

Port de la partie calcul de 3d/salon/etageres.py (ET:63-251, ET:545-577, ET:935-961) : mêmes formules, mêmes noms.
Calcul pur, ni HTML ni SVG (sauf `note_achat`, la note d'origine d'un achat, lue par les tests). Les données viennent
de document.py et volumes.py ; les dimensions des textes s'écrivent par `meubles.cote` (l'ancien `cm`).
"""
import math
from html import escape
from types import SimpleNamespace

from pieces.salon.etageres import volumes
from pieces.salon.etageres.document import (BANDE, COEF, DISPOSITIONS, ETAGERES as ET, ETUDE_MONTANTS as EU, KERF,
                                            KERF_METAL, KG_M, KG_MONTANT, L_MONTANT, MAGASINS, MONTANTS as MO,
                                            N_VIS, PANNEAU, PRESENTOIR, RECHANGE_CHEVILLES, ROND, SURF_PEINT, TASSEAU,
                                            TN)
from pieces.salon.meubles import cote
from pieces.salon.piece import H

PAS = MO["pas"]
CLES = tuple(d["cle"] for d in DISPOSITIONS)


def prix(v: float) -> str:
    """L'ancien `euros` (ET:34) : deux décimales toujours (« 28,00 € »), pour les textes repris."""
    return f"{v:.2f}".replace(".", ",") + " €"


# ------------------------------------------------------------------ tablettes (ET:63-90)
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
            t["libres"].append((min(dessus) - zm(t, k) - ET["ep"], False) if dessus else (H - zm(t, k), True))


# ------------------------------------------------------------------ débit (ET:102-129)
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


# ------------------------------------------------------------------ charges (ET:139-149)
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


# ------------------------------------------------------------------ achats (ET:192-227, prix TTC, DATE)
def achats(e) -> list[dict]:
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
             note=f"montants ≈ {cote(SURF_PEINT)} m², deux couches, et chevilles ; 25,90 € sur la liste du rayon"),
        dict(poste="Finition", article="Huile plan de travail Resist'Activ V33 incolore mat 1 L", ref="5566676",
             magasin="weldom", qte=1, pu=34.00, statut="relevé",
             url="https://www.weldom.fr/p/huile-plan-de-travail-resist-activ-v33-incolore-mat-1-l-5566676",
             note=f"tablettes ≈ {cote(e.surf_huile)} m², trois couches toutes faces"),
        dict(poste="Finition", article="Apprêt antirouille noir en bombe (chevilles)", ref="—", magasin="weldom",
             qte=1, pu=12.00, statut="estimé", url=None),
        dict(poste="Finition", article="Pâte à bois (bouchage des lamages) et abrasifs grains 120 et 180", ref="—",
             magasin="weldom", qte=1, pu=16.00, statut="estimé", url=None),
    ]
    for a in lst:
        a["total"] = round(a["qte"] * a["pu"], 2)
    return lst


def nom_magasin(a) -> str:
    """Nom court du magasin d'un achat (ET:768-770, sans le lien)."""
    return MAGASINS[a["magasin"]]["nom"].split(" Marseille")[0]


def note_achat(a) -> str:
    """La note d'un achat telle que l'ancienne page l'écrivait sous l'article (ET:773-774)."""
    return f'<br><span class="choix">{escape(a["note"])}</span>' if a.get("note") else ""


# ------------------------------------------------------------------ état d'une disposition (ET:152-177)
def etat(cle: str) -> SimpleNamespace:
    if cle not in CLES:
        raise ValueError(f"salon/etageres : disposition « {cle} » inconnue ; connues : {', '.join(CLES)}")
    dispo = volumes.disposition(cle)
    ts = volumes.tablettes(dispo)
    controle(ts, cle)
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


def pieces(e) -> list[dict]:
    """Liste des pièces d'une disposition : montants, une ligne par type de tablette, chevilles (ET:235-251)."""
    out = [dict(rep="M", nom="Montant", n=MO["n"], dims=f'{cote(L_MONTANT)} × {cote(MO["l"])} × {cote(MO["p"])}',
                matiere="sapin raboté, peint en noir mat",
                de=f'{N_TASSEAUX} tasseaux, {PAR_TASSEAU} montants par tasseau ; le reste du dernier sert de gabarit '
                   f'de perçage et d\'essai')]
    for d in e.types.values():
        reps = ", ".join(t["rep"] for t in e.ts if t["type"] == d["type"])
        de = f'{d["n"]} entailles de {cote(ET["entaille"][0])} × {cote(ET["entaille"][1])} ; {reps}'
        out.append(dict(rep=d["type"], nom=f'Tablette de {d["n"] - 1} travée'
                        + ("s" if d["n"] > 2 else ""), n=d["nb"], dims=f'{cote(d["l"])} × {ET["p"]} × {cote(ET["ep"])}',
                        matiere="chêne massif, huilé", de=de))
    out.append(dict(rep="C", nom="Cheville", n=e.chevilles, dims=f'Ø {cote(MO["trou"] * 10)} mm × {cote(ET["cheville"])}',
                    matiere="acier, peint en noir mat",
                    de=f'{e.n_ronds} ronds de 1 m, {e.par_rond} par rond ({e.n_ronds * e.par_rond - e.chevilles} de '
                       f'rechange), bouts chanfreinés'))
    return out


FACTEUR = max(etat(c).ch["facteur"] for c in CLES)                         # milieu d'une longue


# ------------------------------------------------------------------ présentoir (ET:545-577)
PR = dict(PRESENTOIR)
_th = math.radians(PR["deg"])
PR.update(t=math.tan(_th), c=math.cos(_th), s=math.sin(_th))


def _pr_geo():
    """Profil du présentoir (x depuis le mur, z depuis le dessous de la cheville arrière) : dessus, dessous, centre de
    la cheville avant, profondeur de la rainure (perpendiculaire à la tablette), position de son axe sur le dessous."""
    t, c, sn, r, ep = PR["t"], PR["c"], PR["s"], MO["trou"] / 2, ET["ep"]
    top = lambda x: -(x - MO["x_ar"]) * t                     # noqa: E731 ; le dessus touche la cheville arrière
    bas = lambda x: top(x) - ep / c                           # noqa: E731
    zc = r - MO["decalage"]                                    # mêmes trous qu'à plat
    u = lambda x, z: x * c - z * sn                            # noqa: E731 ; abscisse le long de la pente
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


# ------------------------------------------------------------------ tenue (ET:939-961)
def kn(newtons):
    return f"{newtons / 1000:.2f}".replace(".", ",")


def taux(effort, r_k, bois=True, kmod=None):
    r_d = r_k * (kmod or TN["kmod"]) / TN["gm"] if bois else r_k
    return TN["gq"] * effort / r_d


def fixation(e):
    """Efforts sur les vis du montant le plus chargé : cisaillement partagé, arrachement du haut par le moment."""
    w = e.ch["max"] * 9.81
    m = w * TN["e"] / 100
    hs = [h / 100 for h in TN["vis_h"]]
    t_haut = m * hs[-1] / sum(h * h for h in hs)
    v = w / EU["vis"]
    return dict(w=w, m=m, t=t_haut, v=v, r=math.hypot(t_haut, v))
