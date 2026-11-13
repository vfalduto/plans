# Volumes 3D des étagères (montants, tablettes entaillées, chevilles), repris de pieces_3d() de 3d/salon/etageres.py.
#
# Calcul pur, sans HTML, SVG ni Blender : la vue iso de la page, le rendu de l'aménagement (3d/salon/rendu.py) et
# celui des meubles (3d/salon/rendu_meubles.py) lisent la même liste de Piece (pieces.salon.meubles).
# Cotes en cm, repère du salon.

from pieces.salon.etageres.document import DISPOSITIONS, ETAGERES as ET, MONTANTS as MO, NIVEAUX, RA_COTE
from pieces.salon.meubles import Piece

RA = ET["rainure"]


def cm(v):
    """Cote en cm : 1 décimale au plus, virgule."""
    return f"{round(v, 1):g}".replace(".", ",")


def disposition(cle=None):
    """La disposition de clé `cle` (DISPOSITIONS), par défaut celle du plan du salon."""
    if cle is None:
        return DISPOSITIONS[0]
    return next(d for d in DISPOSITIONS if d["cle"] == cle)


def tablettes(dispo):
    """Tablettes d'une disposition, repérées T1… du bas vers le haut (puis du sud au nord)."""
    ts = []
    for z, a, b in dispo["tablettes"]:
        zs = [z] * (b - a + 1)
        assert all(NIVEAUX[0] <= v <= NIVEAUX[1] and (v - NIVEAUX[0]) % MO["pas_trous"] == 0 for v in zs), zs
        y0, y1 = MO["axes"][a] - ET["debord"], MO["axes"][b] + ET["debord"]
        t = dict(z=z, a=a, b=b, zs=zs, y0=y0, y1=y1, lh=y1 - y0, l=y1 - y0, n=b - a + 1, type=cm(y1 - y0))
        t["entailles"] = [y1 - MO["axes"][k] for k in range(b, a - 1, -1)]   # depuis le bout sud
        ts.append(t)
    ts.sort(key=lambda t: (min(t["zs"]), -t["y1"]))
    for i, t in enumerate(ts):
        t["rep"] = f"T{i + 1}"
    return ts


def pieces_3d(dispo=None):
    """Montants, tablettes entaillées et chevilles en boîtes sans chevauchement (cm, repère du salon).

    `dispo` : un dict de DISPOSITIONS ou sa clé ; par défaut la disposition du plan du salon.
    Chaque tablette = une bande avant (de la profondeur d'entaille jusqu'au bord) sur toute sa longueur, plus les
    morceaux arrière entre les entailles et aux bouts. Chaque cheville (section carrée ≈ Ø) est coupée en deux bouts
    qui dépassent de chaque flanc du montant : avant sous la tablette, arrière dessus. Sans l'enfilade."""
    if not isinstance(dispo, dict):
        dispo = disposition(dispo)
    ps = []
    demi_m, prof_e = MO["l"] / 2, ET["entaille"][1]
    r, demi_c = MO["trou"] / 2, ET["cheville"] / 2
    for i, y in enumerate(MO["axes"]):
        ps.append(Piece(f"montant_M{i + 1}", 0, MO["p"], y - demi_m, y + demi_m, MO["z0"], MO["z1"], "pin_noir"))
    for t in tablettes(dispo):
        z0, z1 = t["z"] - ET["ep"], t["z"]
        demi_e = ET["entaille"][0] / 2
        g = f'tablette_{t["rep"]}'
        ps.append(Piece(f'{g}_avant', ET["x0"] + prof_e, ET["x1"], t["y0"], t["y1"], z0, z1, "chene", g))
        axes = MO["axes"][t["a"]:t["b"] + 1]
        bords = [t["y0"]] + [v for y in axes for v in (y - demi_e, y + demi_e)] + [t["y1"]]
        ra, rx0, rx1 = RA, MO["x_av"] - RA["l"] / 2, MO["x_av"] + RA["l"] / 2
        for k in range(0, len(bords), 2):
            u0, u1 = bords[k], bords[k + 1]
            nom = f'{g}_arriere_{k // 2 + 1}'
            ps += [Piece(f'{nom}_mur', ET["x0"], rx0, u0, u1, z0, z1, "chene", g),
                   Piece(f'{nom}_devant', rx1, ET["x0"] + prof_e, u0, u1, z0, z1, "chene", g)]
            # au droit de la rainure : creusé sur (long − entaille) / 2 contre chaque entaille voisine
            c0 = u0 + RA_COTE if k > 0 else u0
            c1 = u1 - RA_COTE if k + 2 < len(bords) else u1
            for m, (v0, v1, zb) in enumerate(((u0, c0, z0 + ra["prof"]), (c0, c1, z0), (c1, u1, z0 + ra["prof"]))):
                if v1 - v0 > 1e-6:
                    ps.append(Piece(f'{nom}_rainure_{m}', rx0, rx1, v0, v1, zb, z1, "chene", g))
        for j, y in enumerate(axes):
            m, zj = f'M{t["a"] + j + 1}', t["zs"][j]
            for pos, x, zc in (("avant", MO["x_av"], zj + r - MO["decalage"]), ("arriere", MO["x_ar"], zj + r)):
                for cote, ya, yb in (("nord", y - demi_c, y - demi_m), ("sud", y + demi_m, y + demi_c)):
                    ps.append(Piece(f'cheville_{t["rep"]}_{m}_{pos}_{cote}', x - r, x + r, ya, yb,
                                    zc - r, zc + r, "acier", forme="cyl_y"))
    return ps


def rogne(ps, x0, x1, y0, y1, z0, z1):
    """Pièces rognées à une boîte (pour une vue de détail) ; les pièces hors de la boîte disparaissent."""
    out = []
    for p in ps:
        b = (max(p.x0, x0), min(p.x1, x1), max(p.y0, y0), min(p.y1, y1), max(p.z0, z0), min(p.z1, z1))
        if b[0] < b[1] and b[2] < b[3] and b[4] < b[5]:
            out.append(Piece(p.nom, *b, p.matiere, p.groupe, p.forme))
    return out


def pieces_detail():
    """Un montant (M2) avec la tablette T1 de la disposition actuelle et ses deux chevilles, en coupe : la tablette
    est rognée à 12 au nord de l'axe, à 20 du mur et, côté sud, au ras du bout des chevilles, pour montrer la cheville
    avant sous la joue."""
    d0 = DISPOSITIONS[0]
    y, z = MO["axes"][1], tablettes(d0)[0]["z"]
    return rogne(pieces_3d(d0), -1, 20, y - 12, y + ET["cheville"] / 2, z - 14, z + 12)
