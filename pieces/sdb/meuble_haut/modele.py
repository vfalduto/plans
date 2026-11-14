"""Le meuble haut de la salle de bain : le débit, le calepinage des seules pièces du caisson, le chant, la liste
d'achats et son total.

Le modèle est celui de 3d/sdb/modele.py (V6.4, `M`), chargé par pieces.sdb.ancien : il décrit toujours le caisson haut et
l'ancien meuble bas V6, que les étapes 9 et 10 dessinent encore. Il reste donc en place (cad.py et les essais de
explorations/ le lisent aussi). Les calculs ci-dessous sont repris de 3d/sdb/plan.py, haut.py et pages.py, qui
produisaient la page du meuble haut ; un test garde leurs résultats.
"""
from pieces.sdb import ancien
from pieces.sdb.meuble_haut import calepinage as CAL

M = ancien.modele()

VERSION = M.VERSION             # V6.4
# usage des matériaux dans le débit du haut seul (le catalogue de modele.py décrit aussi le meuble bas)
USAGES = {"G": "tasseau de joint du fond G12 (non traité : poncer, puis peindre ou vernir toutes les faces)"}


def cm(v):
    """Cote en cm affichée : 1 décimale au plus, virgule française."""
    return f"{round(v, 1):g}".replace(".", ",")


def virg(v, n=2):
    """Nombre à n décimales, virgule française, sans zéro inutile (5,04 ; 0,86 ; 3)."""
    s = f"{v:.{n}f}".replace(".", ",")
    return s.rstrip("0").rstrip(",") if "," in s else s


def lettres(n):
    mots = ["zéro", "un", "deux", "trois", "quatre", "cinq", "six", "sept", "huit", "neuf", "dix"]
    return mots[n] if 0 <= n < len(mots) else str(n)


# ------------------------------------------------------------------ débit
def debit() -> list[dict]:
    """Une ligne par repère : quantité, longueur × largeur × épaisseur en mm."""
    lignes = {}
    for b in M.PIECES:
        if not b.rep:
            continue
        dims = tuple(sorted((b.x1 - b.x0, b.y1 - b.y0, b.z1 - b.z0), reverse=True))
        lignes.setdefault(b.rep, []).append(dims)
    r = []
    for rep in sorted(lignes, key=lambda r: (r[0], int(r[1:]))):
        d = lignes[rep]
        L, l, e = (round(v * 10) for v in max(d))
        q = len(d)
        if rep == "E2":         # une cornière, modélisée en deux ailes
            q, l, e = 1, 30, 30
        if rep == "G11":        # écharpe : longueur de pointe à pointe, section du tasseau
            L, l, e = round(M.ECHARPE["L"] * 10), round(M.DL * 10), round(M.DE * 10)
        if rep == "G7":         # contrefiche à 45° : longueur de pointe à pointe, section du tasseau
            L, l, e = round(M.BAC["contrefiche"] * 2 ** 0.5 * 10), round(M.DL * 10), round(M.DE * 10)
        r.append(dict(rep=rep, mat=rep[0], nom=M.NOMS[rep], q=q, L=L, l=l, e=e, u=M.USINAGES.get(rep, "")))
    return r


def debit_haut() -> list[dict]:
    return [p for p in debit() if M.meuble(p["rep"]) == "haut"]


def section(p: dict) -> str:
    """Largeur d'une ligne de débit : la section d'un tasseau (38 × 38), le diamètre d'un rond, sinon la largeur."""
    if p["mat"] in "EG":
        return f'Ø {p["l"]}' if p["rep"] == "E4" else f'{p["l"]} × {p["e"]}'
    return f'{p["l"]}'


# ------------------------------------------------------------------ calepinage et chant
_SEUL = []
_DEUX = []
_CH = []


def calepinage_seul() -> dict:
    """Calepinage des seules pièces du caisson haut (K1 et G12 compris, sans les chutes du meuble bas), calculé une fois."""
    if not _SEUL:
        _SEUL.append(CAL.calepinage(debit_haut()))
    return _SEUL[0]


def calepinage_deux() -> dict:
    """Calepinage des deux meubles V6 (le haut dans les chutes du bas) : il sert au métrage du chant."""
    if not _DEUX:
        _DEUX.append(CAL.calepinage_meubles(debit()))
    return _DEUX[0]


def _rouleaux(longueurs):
    """Nombre de rouleaux de chant : chaque chant d'un seul tenant, rangé dans le premier rouleau où il tient (du plus
    long au plus court)."""
    reste = []
    for lg in sorted(longueurs, reverse=True):
        k = next((i for i, r in enumerate(reste) if r >= lg), None)
        if k is None:
            reste.append(M.CHANT["rouleau"] - lg)
        else:
            reste[k] -= lg
    return len(reste)


def chants() -> dict:
    """Chant thermocollant à plaquer, d'après le calepinage : pour chaque pièce, ses chants coupés visibles
    (M.CHANT["visibles"]) moins ceux qui tombent sur un chant long d'usine de la tablette. Renvoie chants
    [(repère, étape, longueur mm)], total, rouleaux achetés, rouleaux par étape et mètres par meuble."""
    if _CH:
        return _CH[0]
    deb = {p["rep"]: p for p in debit()}
    etape = {b.rep: b.etape for b in M.PIECES if b.rep}
    cal = calepinage_deux()
    r = []
    for st in cal:
        for grp in ("bas", "neufs"):
            for pn in cal[st][grp]:
                for rep, x, y, a, b in pn.poses():
                    if rep not in M.CHANT["visibles"]:
                        continue
                    L, l = deb[rep]["L"], deb[rep]["l"]
                    usine = (y == 0) + (y + b == pn.fmt["l"])           # chants posés sur un chant long d'usine
                    longs, courts = M.CHANT["visibles"][rep]
                    if a == L and L != l:
                        longs = max(0, longs - usine)
                    else:
                        courts = max(0, courts - usine)
                    r += [(rep, etape[rep], L + M.CHANT["marge"])] * longs + [(rep, etape[rep], l + M.CHANT["marge"])] * courts
    par_etape = {}
    for e in sorted({e for _, e, _ in r}):
        par_etape[e] = _rouleaux([lg for _, e2, lg in r if e2 == e])
    metres = {m: sum(lg for rep, _, lg in r if M.meuble(rep) == m) / 1000 for m in ("bas", "haut")}
    _CH.append(dict(chants=r, total=sum(lg for _, _, lg in r), rouleaux=_rouleaux([lg for _, _, lg in r]),
                    par_etape=par_etape, metres=metres))
    return _CH[0]


def metres_chant() -> float:
    """Métrage de chant du caisson haut, en m."""
    return chants()["metres"]["haut"]


def rouleaux_haut() -> int:
    """Rouleaux de chant du caisson haut : son métrage rapporté au rouleau de M.CHANT, arrondi au supérieur."""
    return -(-round(metres_chant() * 1000) // M.CHANT["rouleau"])


# ------------------------------------------------------------------ achats
def ligne_panneaux(panneaux) -> list[tuple]:
    """Lignes d'achat (nom, réf., quantité, prix, stock) pour une liste de panneaux du calepinage."""
    r = []
    for stock, fmts in M.PANNEAUX.items():
        for fmt in fmts:
            n = sum(1 for p in panneaux if p.fmt["ref"] == fmt["ref"])
            nom = fmt["nom"] + (f" — {fmt['magasin']}" if "magasin" in fmt else "")
            if n and "lot" in fmt:          # vendu par lots
                r.append((nom, fmt["ref"], -(-n // fmt["lot"]), fmt["prix_lot"], fmt["stock"]))
            elif n:
                r.append((nom, fmt["ref"], n, fmt["prix"], fmt["stock"]))
    return r


def lignes_article(code) -> list[tuple]:
    w = M.WELDOM[code]
    return [(x[0], x[4], x[2], x[1], x[3]) for x in (w if isinstance(w, list) else [w])]


def code_meuble(code) -> str:
    """Meuble d'un article de quincaillerie : celui des étapes où il sert (consommables : commun)."""
    if code in M.CONSOMMABLES:
        return "commun"
    etapes = {n for n, e in enumerate(M.ETAPES) if code in e[-1]}
    return "haut" if etapes and etapes <= set(M.MEUBLE_HAUT_ETAPES) else "bas"


def quincaillerie_haut() -> list[tuple]:
    return [ligne for code, w in M.WELDOM.items() if w is not None and code_meuble(code) == "haut"
            for ligne in lignes_article(code)]


def consommables_haut() -> list[str]:
    """Consommables de M.CONSOMMABLES que les étapes du caisson haut utilisent (sauf le chant, compté à part). Le vernis
    n'a aucune étape du haut : il n'est pas acheté ici."""
    utilises = {c for n in M.MEUBLE_HAUT_ETAPES for c in M.ETAPES[n][-1]}
    return [c for c in M.CONSOMMABLES if c in utilises and c != "chant"]


def lignes() -> list[tuple]:
    """Achats du caisson haut seul : panneaux et barres de son calepinage, quincaillerie propre au haut, consommables
    utilisés par ses étapes au conditionnement du magasin, chant au métrage du haut."""
    panneaux = [p for c in calepinage_seul().values() for p in c["retenu"]["panneaux"]]
    r = ligne_panneaux(panneaux) + quincaillerie_haut()
    for code in consommables_haut():
        if M.WELDOM.get(code) is not None:
            r += lignes_article(code)
    nom, ref, _, px, st = lignes_article("chant")[0]
    r.append((nom, ref, rouleaux_haut(), px, st))
    return r


def total_lignes(ls=None) -> float:
    return sum(n * px for _, _, n, px, _ in (lignes() if ls is None else ls))


def total() -> float:
    return total_lignes()


# ------------------------------------------------------------------ montage
ETAPES = M.MEUBLE_HAUT_ETAPES           # les étapes 8, 9 et 10 du modèle
N_PORTES = sum(1 for b in M.PIECES if b.rep == "K6")


def quantites(n: int) -> dict:
    """Quincaillerie de l'étape n ; le chant en rouleaux, compté sur les chants visibles des pièces de l'étape."""
    q = dict(M.ETAPES[n][-1])
    if "chant" in q:
        q["chant"] = chants()["par_etape"].get(n, 0)
        if not q["chant"]:
            del q["chant"]
    return q


def quincaillerie_totale() -> dict:
    """Quincaillerie du montage : somme des étapes ; une cartouche ou un pot sert à plusieurs étapes, on compte l'achat."""
    from collections import Counter
    q = sum((Counter(quantites(n)) for n in ETAPES), Counter())
    for k in M.EN_VOLUME:
        if k in q:
            q[k] = min(q[k], chants()["rouleaux"] if k == "chant" else M.achat(k))
    return dict(q)
