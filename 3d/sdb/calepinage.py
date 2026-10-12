# Calepinage du meuble SDB : range les pièces de chaque épaisseur dans les panneaux du commerce (modele.PANNEAUX).
#
# Coupe guillotine en deux temps, comme à la scie sur rail ou au magasin : on refend le panneau en bandes sur sa
# longueur, puis on tronçonne chaque bande ; dans une bande, des pièces plus étroites peuvent s'empiler. Rangement
# « premier qui convient, du plus grand au plus petit », en essayant les deux sens de chaque pièce (sauf fil imposé).
# Pour chaque panneau acheté (modele.STOCK), on essaie chaque format seul, puis un mélange (chaque nouveau panneau est le
# moins cher qui reçoit la pièce suivante), et on garde le moins cher. Comme l'ordre de rangement compte, on rejoue chaque
# essai sur ESSAIS ordres légèrement mélangés (tirage fixe : le résultat ne change pas d'une génération à l'autre).

import os
import random
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import modele as M  # noqa: E402

TRAIT = 4               # trait de scie, mm
MARGE = 0               # tablettes et plans : chants d'usine finis, pas de délignage
ESSAIS = 400


def pieces(debit):
    """Pièces à découper (mm) par panneau acheté : liste de (rep, longueur, largeur)."""
    r = {}
    for p in debit:
        if p["mat"] in M.STOCK:
            r.setdefault(M.STOCK[p["mat"]], []).extend((p["rep"], p["L"], p["l"]) for _ in range(p["q"]))
    return r


class Bande:
    def __init__(self, y, h, longueur):
        self.y, self.h, self.x, self.lmax, self.cols = y, h, 0, longueur, []

    def place(self, rep, a, b):
        """Place une pièce a (le long de la bande) × b (en travers) ; renvoie True si elle tient."""
        if b > self.h:
            return False
        for col in self.cols:                     # empiler dans une colonne existante
            if a <= col["l"] and col["y"] + b <= self.h:
                col["p"].append((rep, col["x"], self.y + col["y"], a, b))
                col["y"] += b + TRAIT
                return True
        if self.x + a > self.lmax:
            return False
        self.cols.append(dict(x=self.x, l=a, y=b + TRAIT, p=[(rep, self.x, self.y, a, b)]))
        self.x += a + TRAIT
        return True


class Panneau:
    def __init__(self, fmt):
        self.fmt, self.L, self.l, self.bandes = fmt, fmt["L"] - MARGE, fmt["l"] - MARGE, []
        self.y = 0

    def place(self, rep, L, l, fil):
        sens = [(L, l)] if fil else sorted({(L, l), (l, L)}, key=lambda s: -s[0])
        for b in self.bandes:
            for a, w in sens:
                if b.place(rep, a, w):
                    return True
        # nouvelle bande : la plus étroite possible
        for a, w in sorted(sens, key=lambda s: s[1]):
            if a <= self.L and self.y + w <= self.l:
                b = Bande(self.y, w, self.L)
                b.place(rep, a, w)
                self.bandes.append(b)
                self.y += w + TRAIT
                return True
        return False

    def poses(self):
        return [q for b in self.bandes for c in b.cols for q in c["p"]]

    def taux(self):
        return sum(a * b for _, _, _, a, b in self.poses()) / (self.fmt["L"] * self.fmt["l"])


def range_(tri, formats, fil=()):
    """Range les pièces dans l'ordre donné ; chaque nouveau panneau est le moins cher des formats qui reçoivent la pièce.
    None si une pièce ne tient dans aucun format."""
    panneaux = []
    for rep, a, b in tri:
        f = rep in fil
        if any(p.place(rep, a, b, f) for p in panneaux):
            continue
        for fmt in sorted(formats, key=lambda x: x["prix"]):
            p = Panneau(fmt)
            if p.place(rep, a, b, f):
                panneaux.append(p)
                break
        else:
            return None
    return panneaux


def calepinage(debit):
    """Par panneau acheté : la solution retenue (la moins chère) et l'examen des formats proposés."""
    r = {}
    for stock, liste in pieces(debit).items():
        formats = M.PANNEAUX[stock]
        essais = [(f"{fmt['L']} × {fmt['l']} seul", [fmt]) for fmt in formats]
        if len(formats) > 1:
            essais.append(("mélange de formats", formats))
        res = []
        tri = sorted(liste, key=lambda p: (-max(p[1], p[2]), -min(p[1], p[2])))
        ordres = [tri]
        hasard = random.Random(1)
        for _ in range(ESSAIS):         # du plus grand au plus petit, à peu près : on échange des voisins
            o = list(tri)
            for _ in range(len(o) // 3):
                i = hasard.randrange(len(o) - 1)
                j = min(len(o) - 1, i + hasard.randint(1, 4))
                o[i], o[j] = o[j], o[i]
            ordres.append(o)
        for nom, fmts in essais:
            best = None
            for o in ordres:
                ps = range_(o, fmts, M.FIL)
                if ps is None:
                    break
                cle = (sum(p.fmt["prix"] for p in ps), len(ps))
                if best is None or cle < best[0]:
                    best = (cle, ps)
            res.append(dict(nom=nom, n=None) if best is None else
                       dict(nom=nom, n=len(best[1]), prix=best[0][0], panneaux=best[1]))
        ok = [e for e in res if e["n"]]
        assert ok, f"aucun format ne convient pour {stock}"
        r[stock] = dict(retenu=min(ok, key=lambda e: (e["prix"], e["n"])), essais=res)
    return r


if __name__ == "__main__":
    import plan
    for stock, c in calepinage(plan.debit()).items():
        for e in c["essais"]:
            print(stock, e["nom"], e["n"], e.get("prix"))
        for p in c["retenu"]["panneaux"]:
            print("  ", p.fmt["L"], p.fmt["l"], f"{p.taux():.0%}", [q[0] for q in p.poses()])
