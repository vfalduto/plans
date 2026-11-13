# Géométrie de l'enfilade (caissons, façades, pieds, étagères intérieures) et ses volumes 3D, repris de geometrie()
# et pieces_3d() de 3d/salon/enfilade.py.
#
# Calcul pur, sans HTML, SVG ni Blender : la vue iso de la page et le rendu des meubles (3d/salon/rendu_meubles.py)
# lisent la même liste de Piece (pieces.salon.meubles). Le débit et le chiffrage, qui partent de geometrie(), restent
# au générateur de la page. Cotes en cm, repère du salon.

import math
from collections import Counter

from pieces.salon.enfilade.document import (BORD, CALE_BOITE, COULISSE, DESSUS, DOS, EP, EP_COUL, ENFILADE as E,
                                            ETAGERES_CAISSONS, FAC, H_BOITE, JEU, MODULES, N, PC, PIEDS_X,
                                            PROF_ETAGERE, RETENUE, TAMPON, TRAV, L, P, Z1, ZP)
from pieces.salon.meubles import Piece, f, virg as _virg_n


def _virg(v, n=None):
    """Cote affichée : 1 décimale au plus, sans « ,0 » (n : nombre de décimales imposé)."""
    return f(v).replace(".", ",") if n is None else _virg_n(v, n)


def bas(v):
    """Arrondi au mm inférieur : une pièce arrondie ne déborde jamais de sa place."""
    return math.floor(v * 10 + 1e-6) / 10


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
    for k, vides in enumerate(ETAGERES_CAISSONS):
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
    return f"{_virg(sum(g['W']))} × {_virg(DOS + PC + TAMPON + FAC, 0)} × {_virg(ZP + g['HC'] + g['ep_d'], 0)}"


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
        ps.append(Piece(nom, round(x_ + x0, 3), round(x_ + x1, 3), round(y_ + y0, 3), round(y_ + y1, 3),
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
            add(f"pied {_virg(x)} / {_virg(y)}", x - 1.25, x + 1.25, max(y - 1.25, 0), min(y + 1.25, L), 0, ZP, "noir")
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
