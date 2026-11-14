"""Calculs de la page salon-enfilade : débit, calepinage, chiffrage des compositions, volume, dégagements, poids.

Repris de 3d/salon/enfilade.py (pieces, debit, format_de, calepiner, comptes, chiffrage, euros, lettre) ; les données
viennent de document.py, la géométrie de volumes.py. Le poids d'un caisson est corrigé (l'ancienne page comptait la
largeur deux fois).
"""
import math
from collections import Counter, defaultdict

from pieces.salon.amenagement.document import CANAPE
from pieces.salon.enfilade.document import (CHANT, COULISSE, DOS, EP, EP_COUL, FAC, FORMATS, H_BOITE, L, MELAMINE, N,
                                            ORDRE_MAG, P, PC, PIEDS_X, PREFIXE, PROF_ETAGERE, QUINC, RETENUE, TRAIT,
                                            TRAV, VARIANTES, quantite)
from pieces.salon.enfilade.volumes import G, bas, geometrie
from pieces.salon.meubles import cote


def prix(v):
    return f"{v:,.2f}".replace(",", " ").replace(".", ",") + " €"


def lettre(n):
    return ["zéro", "une", "deux", "trois", "quatre", "cinq", "six", "sept", "huit"][n] if n < 9 else str(n)


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
                           note=f"{cote(m)} m de chants coupés", panneau=True))
    c = comptes(ps, g, v)
    for qd in QUINC:
        lignes.append(dict(poste=qd["poste"], ref=qd["ref"], mag=qd["mag"], q=quantite(qd["q"], c), unite="u", pu=qd["prix"],
                           statut=qd["statut"], url=qd["url"], note=qd["note"], panneau=False))
    for li in lignes:
        li["total"] = round(li["q"] * li["pu"], 2)
    total = round(sum(li["total"] for li in lignes), 2)
    rel = round(sum(li["total"] for li in lignes if li["statut"] == "relevé"), 2)
    return dict(v=v, ps=ps, g=g, lignes=lignes, cal=cal, total=total, releve=rel, estime=round(total - rel, 2), c=c)


def chiffrages():
    return [chiffrage(v) for v in VARIANTES]


def retenu(chs):
    return next(ch for ch in chs if ch["v"] is RETENUE)


def volume_utile(g=G):
    """Litres."""
    return sum((w - 2 * EP) * PC * (g["zi1"] - g["zi0"]) for w in g["W"]) / 1000


def degagements(g=G):
    """(devant la porte la plus large de M1, devant un tiroir sorti), en cm."""
    portes = [fc for fc in g["facades"] if fc["type"] == "porte"]
    l1 = portes[0]["y1"] - portes[0]["y0"]
    return round(CANAPE["x0"] - P - l1, 1), round(CANAPE["x0"] - P - COULISSE - FAC, 1)


def poids_caisson(g=G):
    """kg : côtés, fond et deux traverses d'un caisson, chêne à 0,7."""
    li = g["W"][0] - 2 * EP
    return round((2 * g["HC"] * PC + li * PC + 2 * li * TRAV) * EP * 0.7 / 1000)
