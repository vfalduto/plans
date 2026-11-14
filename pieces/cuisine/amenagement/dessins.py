"""Les sept dessins de la cuisine/aménagement : plan meublé, coupes A, B et C, élévation et plan électriques, hauteur
du plan de travail, et leur CSS.

Code repris de l'ancien générateur 3d/v13/plan.py (supprimé à la bascule). Écarts avec l'ancienne page, et seulement
ceux-là : virgule à la place du point médian, aria-label donné par l'appelant, zones du plan insérées avant </svg>, et
chaque état que changeaient ses boutons (portes, taille de la règle, transparence de la coupe C) marqué du jeton de son
option (options.py, `data-si`) au lieu de classes cachées par le CSS de la page.
"""
import math
import re
from html import escape

from pieces.cuisine import modele as M
from pieces.cuisine.amenagement.options import PORTE_CELLIER, PORTE_ENTREE, TAILLE, TRANSPARENCE, marque
from pieces.cuisine.dessin import aire, cote_d, cote_h, cote_v, f, pts, rect, text, volumes_plan

COUPE_A = 90   # plan de coupe A-A (y), regard vers le nord
COUPE_B = 150  # plan de coupe B-B (y), regard vers le sud
COUPE_C = 315  # plan de coupe C-C (x), regard vers l'est


def _attr(s):
    """Valeur d'attribut : &, <, > et " échappés, l'apostrophe gardée (comme dans l'ancienne page)."""
    return escape(s, quote=False).replace('"', "&quot;")


# ------------------------------------------------------------------ plan vu de dessus


def batons_rompus(w=8, l=32):
    """Motif de parquet en bâtons rompus : lames w × l, période 2l × 2l, posé à 45°."""
    p = 2 * l
    r = []
    for j in range(-4, 5):
        for n in range(-2 * p // w, 2 * p // w):
            ox, oy = j * l + n * w, -j * l + n * w
            for x, y, dx, dy in ((ox, oy, l, w), (ox, oy + w, w, l)):
                if x < p and y < p and x + dx > 0 and y + dy > 0:
                    r.append(f'<rect class="lame" x="{x}" y="{y}" width="{dx}" height="{dy}"/>')
    return (f'<pattern id="br" width="{p}" height="{p}" patternUnits="userSpaceOnUse" '
            f'patternTransform="rotate(-45)">{"".join(r)}</pattern>')


def battant(h, ferme, ouvert, label):
    """Porte battante ouverte à 90° : vantail de la charnière au bout ouvert, arc depuis le bout fermé."""
    (hx, hy), (fx, fy), (ox, oy) = h, ferme, ouvert
    w = math.dist(h, ferme)
    sweep = 1 if (fx - hx) * (oy - hy) - (fy - hy) * (ox - hx) > 0 else 0
    lx, ly = hx + 0.55 * (fx - hx + ox - hx), hy + 0.55 * (fy - hy + oy - hy)
    return (f'<line class="doorleaf" x1="{f(hx)}" y1="{f(hy)}" x2="{f(ox)}" y2="{f(oy)}"/>'
            f'<path class="swing" d="M{f(fx)} {f(fy)} A{f(w)} {f(w)} 0 0 {sweep} {f(ox)} {f(oy)}"/>'
            + text(lx, ly + 2, label, "lblx muted"))


def vantail(v, ouvert=True):
    """Vantail fermé ou ouvert à son angle, à son épaisseur réelle, avec ses balais (face côté cellier) et sa paumelle ;
    ouvert, avec le balayage depuis la position fermée."""
    (hx, hy), (fx, fy), w = v["h"], v["ferme"], v["w"]
    ox, oy = v["ouvert"] if ouvert else v["ferme"]
    d0 = ((fx - hx) / w, (fy - hy) / w)                 # direction fermée
    d1 = ((ox - hx) / w, (oy - hy) / w)                 # direction ouverte
    c, s_ = d0[0] * d1[0] + d0[1] * d1[1], d0[0] * d1[1] - d0[1] * d1[0]

    def tourne(px, py):
        """Point du vantail fermé (repère : charnière) → position ouverte."""
        return hx + c * px - s_ * py, hy + s_ * px + c * py

    def piece(u0, u1, x0, x1):
        """Rectangle du vantail fermé, de u0 à u1 le long du vantail, de x0 à x1 en épaisseur (x relatif à la charnière)."""
        return [tourne(x + d0[0] * u, d0[1] * u) for x, u in ((x0, u0), (x0, u1), (x1, u1), (x1, u0))]

    o = []
    if ouvert:
        sweep = 1 if (fx - hx) * (oy - hy) - (fy - hy) * (ox - hx) > 0 else 0
        o.append(f'<path class="swing" d="M{f(fx)} {f(fy)} A{f(w)} {f(w)} 0 0 {sweep} {f(ox)} {f(oy)}"/>')
    o.append(f'<polygon class="leaf" points="{pts(piece(0, w, -M.EP_VANTAIL, 0))}"/>')
    for dist, larg in v["balais"]:
        o.append(f'<polygon class="balai" points="{pts(piece(dist - larg / 2, dist + larg / 2, 0, v["saillie"]))}"/>')
    o.append(f'<circle class="pivot" cx="{f(hx)}" cy="{f(hy)}" r="1.4"/>')
    if ouvert:
        lx, ly = hx + 0.6 * (fx - hx + ox - hx), hy + 0.6 * (fy - hy + oy - hy)
        o.append(text(lx, ly + 2, f'{f(w)}, {f(round(v["angle"]))}°', "lblx"))
    return "".join(o)




def plan_svg(aria: str, zones: str = "") -> str:
    """Plan meublé ; `zones` (HTML des zones cliquables) juste avant </svg>, role="group" alors."""
    o = [f"<defs>{batons_rompus()}</defs>"]
    o.append(f'<polygon class="floorbg" points="{pts(M.SOL_PARQUET)}"/>')
    o.append(f'<polygon fill="url(#br)" points="{pts(M.SOL_PARQUET)}"/>')
    o.append(f'<polygon class="ciment" points="{pts(M.SOL_CIMENT)}"/>')
    for b in M.CLOISONS_DEPOSEES:
        o.append(rect(b.x0, b.y0, b.x1, b.y1, "depose"))
    for nom, x, y in M.ZONES:
        for k, ligne in enumerate(nom.split("\n")):
            o.append(text(x, y + 8 * k, ligne, "lbls muted"))
    o.append(f'<polygon class="wc" points="{pts(M.WC)}"/>')
    o.append(text(438, 185, "WC", "lbl muted"))
    # fond opaque sous le plan de travail (semi-transparent) : le sol ne doit pas apparaître là où aucun caisson
    # ne le porte (fileur du mur ouest)
    for b in M.MEUBLES:
        if b.role == "plan":
            o.append(rect(b.x0, b.y0, b.x1, b.y1, "ptbase"))
    o += volumes_plan()
    # fenêtre coulissante : deux vantaux dans l'épaisseur du mur
    fe = M.FENETRE
    o.append(f'<line class="glass" x1="-7" y1="{fe["y0"]}" x2="-7" y2="{(fe["y0"] + fe["y1"]) / 2 + 2}"/>')
    o.append(f'<line class="glass" x1="-13" y1="{(fe["y0"] + fe["y1"]) / 2 - 2}" x2="-13" y2="{fe["y1"]}"/>')
    # porte d'entrée à galandage : fermée en trait plein, rentrée dans sa poche en ocre
    en = M.ENTREE
    o.append(f'<g class="vt" data-vt="entree">'
             f'<g{marque(PORTE_ENTREE, "ouverte")}>{rect(en["ouvert"][0], en["y"] - 2, en["ouvert"][1], en["y"] + 2, "leaf")}</g>'
             f'<g{marque(PORTE_ENTREE, "fermee")}><line class="doorleaf" x1="{f(en["ferme"][0])}" y1="{f(en["y"])}" '
             f'x2="{f(en["ferme"][1])}" y2="{f(en["y"])}"/></g></g>')
    o.append(text((en["x0"] + en["x1"]) / 2, 270, "Entrée", "lbls"))
    o.append(text(sum(en["poche"]) / 2, 237, "tableau noir, aimants", "lblx"))
    # ballon
    bl = M.BALLON
    if isinstance(bl, M.Cyl):
        o.append(f'<circle class="ecs" cx="{f(bl.cx)}" cy="{f(bl.cy)}" r="{f(bl.r)}"/>')
        o.append(text(bl.cx, bl.cy + 2, "Ballon ECS", "lblx"))
    o.append(text(M.CHUTE[0] + 7, M.CHUTE[1] + 2, "chute", "lblx", "start"))
    o.append(text(M.NOURRICE[0] - 4, M.NOURRICE[1] - 4, "nourrice", "lblx", "end"))
    # numéros des meubles
    for b in M.MEUBLES:
        if b.role == "caisson":
            nom, _, equip = b.etiq.partition(" ")
            y = 74 if b.y1 >= M.P_CAISSON else b.y1 / 2 + 3   # B6 (P40) : sur le caisson, la porte du cellier repliée devant
            o.append(text((b.x0 + b.x1) / 2, y, nom, "lblb"))
            if equip:
                o.append(text((b.x0 + b.x1) / 2, y + 8, equip, "lbls"))
        if b.role == "banquette" and b.etiq:
            o.append(text((b.x0 + b.x1) / 2, b.y0 + 12, b.etiq, "lbls"))   # V13.17 : au nord, hors de la plante
        if b.role == "colonne" and b.etiq:
            o.append(text((b.x0 + b.x1) / 2, (b.y0 + b.y1) / 2 + 3, b.etiq, "lbl", extra=' font-weight="700"'))
    for b in M.MEUBLES:
        if b.role == "plaque":
            o.append(text((b.x0 + b.x1) / 2, 50, "induction", "lblx onDark"))
        if b.role == "cuve":
            o.append(text((b.x0 + b.x1) / 2, b.y1 - 3, "évier", "lblx"))
        if b.role == "egouttoir":
            o.append(text((b.x0 + b.x1) / 2, (b.y0 + b.y1) / 2 + 2, "égouttoir", "lblx"))
    # cellier : vantaux ouverts vers le cellier, à l'épaisseur réelle, balayage et paumelles
    if M.PLIANTE:
        a = M.PLIANTE
        r, l, e, y0, y1 = a["rail"], a["l"], a["ep"], a["y0"], a["y1"]
        # ouverte : vantail du pivot rabattu vers l'ouest (y0 → y0 + e), second vantail replié contre lui ; balayage
        ouvert = (f'<path class="swing" d="M{f(r)} {f(y0 + 2 * l)} A{f(2 * l)} {f(2 * l)} 0 0 1 {f(r - l)} {f(y0 + e)}"/>'
                  f'<path class="swing" d="M{f(r)} {f(y0 + l)} A{f(l)} {f(l)} 0 0 1 {f(r - l)} {f(y0)}"/>'
                  + rect(r - l, y0, r, y0 + e, "leaf") + rect(r - l, y0 + e, r, y0 + 2 * e, "leaf")
                  + text(r - l / 2, y0 + 2 * e + 6, "porte pliante", "lblx"))
        ferme = rect(r - e / 2, y0, r + e / 2, y0 + l, "leaf") + rect(r - e / 2, y0 + l + 1, r + e / 2, y1, "leaf")
        # mi-ouverte : vantail du pivot tourné de a["mi"]° vers la cuisine, second vantail jusqu'au rail (V)
        t = math.radians(a["mi"])
        p1 = (r - l * math.sin(t), y0 + l * math.cos(t))
        p2 = (r, y0 + 2 * l * math.cos(t))
        mi = (f'<polyline class="pliee" points="{pts([(r, y0), p1, p2])}"/>'
              f'<path class="swing" d="M{f(r)} {f(y0 + l)} A{f(l)} {f(l)} 0 0 1 {f(p1[0])} {f(p1[1])}"/>'
              + text(p1[0] - 3, p1[1] + 2, f'{a["mi"]}°', "lblx", "end"))
        o.append(f'<g class="vt" data-vt="cellier"><g{marque(PORTE_CELLIER, "ouverte")}>{ouvert}</g>'
                 f'<g{marque(PORTE_CELLIER, "mi-ouverte")}>{mi}</g><g{marque(PORTE_CELLIER, "fermee")}>{ferme}</g></g>')
        # baie et passage libre côte à côte, côté cellier, juste derrière la porte (V13.2 : la cote côté cuisine se
        # perdait dans le triangle d'activité)
        o.append(cote_v(y0, y1, 337, f'baie {f(y1 - y0)}'))
        o.append(cote_v(y0 + 2 * e + 2, y1, 348, f'passage {f(M.PASSAGE_CELLIER)}'))
        # passages dans le cellier
        o.append(cote_v(M.RAYON_NORD["y1"], M.JOUE_C2, 362, f'{f(M.PASSAGE_ENTREE)}'))
        o.append(cote_v(M.RAYON_NORD["y1"], M.Y_BALAIS - 6, 392, f'{f(M.PASSAGE_BALAIS)}'))
    for k, v in enumerate(M.CELLIER_VANTAUX):
        o.append(f'<g class="vt" data-vt="{k}"><g class="ouv">{vantail(v)}</g>'
                 f'<g class="fer">{vantail(v, ouvert=False)}</g></g>')
    # réseaux d'eau
    for role, _, p, _, _ in M.RESEAUX:
        o.append(f'<polyline class="{"pin" if role == "alim" else "pout"}" points="{pts(p)}"/>')
    o.append(f'<circle class="chute" cx="{f(M.CHUTE[0])}" cy="{f(M.CHUTE[1])}" r="4.5"/>')
    o.append(f'<circle class="nourrice" cx="{f(M.NOURRICE[0])}" cy="{f(M.NOURRICE[1])}" r="2.5"/>')
    # ouvertures de l'électroménager
    for kind, nom, d in M.OUVERTURES:
        if kind in ("abattant", "tiroir"):
            x0, x1, y0, y1 = d
            o.append(rect(x0, y0, x1, y1, "swingz"))
            lib = f"porte {nom} abattue" if kind == "abattant" else "tiroir"
            o.append(text((x0 + x1) / 2, (y0 + y1) / 2 + 2, lib, "lblx muted"))
        else:
            o.append(battant(*d, f"porte {nom} 90°"))
    # cellier : surface et volume
    surf = aire(M.CELLIER_SOL) / 1e4
    vol = surf * M.H / 100
    bl = M.BALLON
    net = vol - (math.pi * (bl.r / 100) ** 2 * (bl.z1 - bl.z0) / 100 if isinstance(bl, M.Cyl) else 0)
    for k, ligne in enumerate((f"cellier, {surf:.2f} m²", f"{vol:.2f} m³ brut, ≈ {net:.1f} net")):
        o.append(text(385, 16 + 7 * k, ligne.replace(".", ","), "lblx"))
    # table
    o.append(text(M.TABLE["cx"], M.TABLE["cy"] + 3, f'{M.TABLE["cote"]} × {M.TABLE["cote"]}', "lblb"))
    # triangle d'activité
    tp = [p for _, p in M.TRIANGLE]
    o.append(f'<polygon class="tri" points="{pts(tp)}"/>')
    for a, b in zip(tp, tp[1:] + tp[:1]):
        d = math.dist(a, b)
        mx, my = (a[0] + b[0]) / 2, (a[1] + b[1]) / 2
        o.append(f'<rect class="tribg" x="{f(mx - 11)}" y="{f(my - 6)}" width="22" height="10" rx="2"/>')
        o.append(text(mx, my + 1.5, f"{d:.0f}", "trit"))
    for _, (x, y) in M.TRIANGLE:
        o.append(f'<circle class="triv" cx="{f(x)}" cy="{f(y)}" r="2.5"/>')
    # coupe A-A
    for y, nom, d in ((COUPE_A, "A", -9), (COUPE_B, "B", 9)):
        o.append(f'<line class="sec" x1="-30" y1="{y}" x2="500" y2="{y}"/>')
        for x in (-30, 500):
            o.append(f'<path class="secm" d="M{x - 4} {y} l4 {d} l4 {-d} z"/>')
            o.append(text(x, y - d * 1.2 + 3, nom, "sect"))
    for x, nom, y0, y1 in ((COUPE_C, "C", -82, 300),):
        o.append(f'<line class="sec" x1="{x}" y1="{y0}" x2="{x}" y2="{y1}"/>')
        for y in (y0, y1):
            o.append(f'<path class="secm" d="M{x} {y - 4} l9 4 l-9 4 z"/>')
            o.append(text(x - 7, y + 4, nom, "sect"))
    # cotes : chaîne du mur nord, total des meubles, longueur de la pièce
    caissons = [b for b in M.MEUBLES if b.role == "caisson" and b.y0 == 0]
    o.append(cote_h(0, caissons[0].x0, -30))
    for b in caissons:
        o.append(cote_h(b.x0, b.x1, -30))
    o.append(cote_h(caissons[-1].x1, M.X_CLOISON, -30))
    hauts = [b for b in M.MEUBLES if b.role == "caisson_haut"]
    o.append(cote_h(0, hauts[0].x0, -48))
    for b in hauts:
        o.append(cote_h(b.x0, b.x1, -48))
    for b in hauts:
        o.append(text((b.x0 + b.x1) / 2, 10, b.etiq, "lbls muted"))
    for y0, y1 in ((M.JOUE_C2, M.COL_Y0), (M.COL_Y0, M.COL_Y0 + 60), (M.COL_Y0 + 60, M.COL_Y1)):
        o.append(cote_v(y0, y1, 402))
    # passages depuis l'angle sud-est des façades des meubles bas : frigo, mur nord du WC
    o.append(cote_d((M.sur_bas(M.B_EVIER)[1], 62), (M.COL_X, M.JOUE_C2), 0.5, (-7, 4)))
    # porte d'entrée à galandage : baie, poche
    o.append(cote_h(en["x0"], en["x1"], 282, f'baie {f(en["x1"] - en["x0"])}'))
    o.append(cote_h(*en["poche"], 282, f'poche {f(en["poche"][1] - en["poche"][0])}'))
    o.append(cote_h(0, 434, -66))
    o.append(text(-4, -27, "bas", "lblx muted", "end"))
    o.append(text(-4, -45, "hauts", "lblx muted", "end"))
    o.append(cote_v(0, M.P_CAISSON + M.FACADE, M.sur_bas(M.B_EVIER)[1] - 8))
    o.append(cote_v(0, M.P_ETROIT + M.FACADE, M.sur_bas(M.B_ETROIT)[0] + 5))
    # mur ouest
    o.append(cote_v(0, fe["y0"], -34))
    o.append(cote_v(fe["y0"], fe["y1"], -34, f'fenêtre {f(fe["y1"] - fe["y0"])}'))
    o.append(cote_v(fe["y1"], 252, -34))
    o.append(cote_v(0, 252, -52))
    # nord
    o.append('<g transform="translate(470 -60)"><path class="dark" d="M0 -10 L5 4 L0 1 L-5 4 Z"/>'
             + text(0, 14, "N", "lblb") + "</g>")
    return (f'<svg viewBox="-75 -90 590 410" role="{"group" if zones else "img"}" aria-label="{_attr(aria)}">'
            f'{"".join(o)}{zones}</svg>')


# ------------------------------------------------------------------ coupes
COUPE_CLS = {"mur": ("bgwall", "w"), "allege": ("bgwall", "w"), "linteau": ("wallv", "w"),
             "caisson_haut": ("cab", "cab"), "facade_haut": ("fac", "fac"), "plan": ("pt", "pt"),
             "plaque": ("dark", "dark"), "aspiration": ("dark", "dark"), "hotte": ("inox", "inox"), "evier": ("inox", "inox"), "egouttoir": ("inox", "inox"),
             "cuve": ("inox", "inox"), "mitigeur": ("inox", "inox"), "ballon": ("ecs", "ecs"),
             "tech": ("tech", "tech"), "socle": ("plinth", "plinth"),
             "caisson": ("cab", "cab"), "facade": ("fac", "fac"), "porte": ("leaf", "leaf"),
             "colonne": ("tall", "tall"), "cloison": ("wallv", "neuf"),
             "fileur": ("fac", "fac"), "banquette": ("stool", "stool"), "table": ("tbl", "tbl"), "chant": ("dark", "dark"), "peinture": ("peint", "peint"), "pied": ("tbl", "tbl"), "chaise": ("stool", "stool"), "facade_col": ("fac", "fac"), "four": ("dark", "dark"),
             "etagere": ("shelf", "shelfc"), "montant": ("shelf", "shelfc"), "trappe": ("trappe", "trappe"),
             "ardoise": ("ardoise", "ardoise"), "aimant": ("aimant", "aimant"), "micro_onde": ("dark", "dark"),
             "dormant": ("dorm", "dorm"), "dormant_haut": ("dorm", "dorm"), "joue": ("fac", "fac"),
             "paumelle": ("dark", "dark"), "ratelier": ("dark", "dark"), "balai": ("balai", "balai"),
             "manche": ("balai", "balai"), "led": ("led", "led"), "etagere_haute": ("shelf", "shelfc"),
             "enceinte": ("dark", "dark"), "lampe": ("lampe", "lampe"), "fil": ("dark", "dark"),
             "aspirateur": ("aspi", "aspi"), "cafetiere": ("dark", "dark"), "plante": ("plante", "plante"), "pot": ("pot", "pot"),
             "seau": ("aspi", "aspi")}


# Regard d'une coupe : (axe coupé, sens de la profondeur, miroir de l'axe horizontal)
# nord : coupe en y, on regarde vers les y décroissants, l'ouest à gauche ; sud : l'est à gauche ;
# est : coupe en x, on regarde vers les x croissants, le nord à gauche (u = y).
REGARDS = {"nord": ("y", -1, False), "sud": ("y", 1, True), "est": ("x", 1, False)}


def uv(b, axe):
    """(u0, u1, d0, d1) : étendue horizontale à l'écran et profondeur, selon l'axe de coupe."""
    return (b.x0, b.x1, b.y0, b.y1) if axe == "y" else (b.y0, b.y1, b.x0, b.x1)


def chaine(blocs, y, X, axe="y", origine=0):
    """Chaîne de cotes depuis le mur (origine) puis meuble par meuble, en coordonnées d'écran X(u)."""
    o = []
    bords = [origine] + [uv(b, axe)[0] for b in blocs[:1]] + [uv(b, axe)[1] for b in blocs]
    for a, b in zip(bords, bords[1:]):
        u, v = sorted((X(a), X(b)))
        o.append(cote_h(u, v, y, f(abs(b - a))))
    return "".join(o)


def coupe_svg(cut, regard, umin, umax, chaines, hauteurs, xh, extra=None, origine=0, transparents=(), *, aria):
    """Coupe au plan cut (y pour nord/sud, x pour est). Vers le sud, l'est est à gauche : u écran = umin + umax - x.
    aria : texte alternatif, donné par l'appelant."""
    axe, sens, miroir = REGARDS[regard]
    X = (lambda u: umin + umax - u) if miroir else (lambda u: u)
    o, etiquettes = [], []
    tous = M.ENVELOPPE + M.MEUBLES + [M.BALLON]

    def vu(b):
        u0, u1, d0, d1 = uv(b, axe)
        return (d1 > cut if sens > 0 else d0 < cut) and u1 > umin and u0 < umax

    vus = [b for b in tous if vu(b)]
    # du plus loin au plus proche, les éléments coupés en dernier
    vus.sort(key=lambda b: (uv(b, axe)[2] < cut < uv(b, axe)[3], -uv(b, axe)[2] if sens > 0 else uv(b, axe)[3]))
    trans = [t for t in vus if transparents and t.nom.startswith(transparents)]

    def derriere(b):
        """b est caché par un élément transparent (porte du cellier…) quand celui-ci est opaque."""
        u0, u1, d0, d1 = uv(b, axe)
        for t in trans:
            tu0, tu1, td0, td1 = uv(t, axe)
            if (d0 >= td1 if sens > 0 else d1 <= td0) and u0 < tu1 and u1 > tu0 and b.z0 < t.z1 and b.z1 > t.z0:
                return True
        return False

    for b in vus:
        n0 = len(etiquettes)
        u0, u1, d0, d1 = uv(b, axe)
        coupe = d0 < cut < d1
        if isinstance(b, M.Pan) and coupe:
            # panneau en biais coupé : on ne voit que la partie au-delà du plan, plus sa section au point de coupe
            (ua, da), (ub, db) = [(p[0], p[1]) if axe == "y" else (p[1], p[0]) for p in (b.a, b.b)]
            ui = ua + (ub - ua) * (cut - da) / (db - da)
            loin = ua if (da - cut) * sens > 0 else ub
            u0, u1 = sorted((ui, loin))
            uc, vc = sorted((X(ui - b.ep / 2), X(ui + b.ep / 2)))
            o.append(rect(uc, -b.z1, vc, -b.z0, COUPE_CLS[b.role][1]))
            coupe = False
        u, v = sorted((X(max(u0, umin)), X(min(u1, umax))))
        # éléments dessinés en transparence (contour seul) pour voir ce qu'il y a derrière
        cls = COUPE_CLS[b.role][1 if coupe else 0]
        if transparents and b.nom.startswith(transparents):
            # les deux dessins, chacun marqué : opaque, ou en transparence (contour tireté)
            o.append(f'<g{marque(TRANSPARENCE, "non")}>{rect(u, -b.z1, v, -b.z0, cls)}</g>'
                     f'<g{marque(TRANSPARENCE, "oui")}>{rect(u, -b.z1, v, -b.z0, f"{cls} trp")}</g>')
        else:
            o.append(rect(u, -b.z1, v, -b.z0, cls))
        xm = (u + v) / 2
        if b.role == "allege" and coupe:
            o.append(text(xm, -150, "fenêtre", "lblx", extra=f' transform="rotate(-90 {f(xm)} -150)"'))
        if b.role == "ballon":
            etiquettes.append(text(xm, -(b.z0 + b.z1) / 2, "Ballon", "lblx"))
        if b.role == "four" and v - u > 10:  # pas d'étiquette sur un four vu sur chant
            etiquettes.append(text(xm, -(b.z0 + b.z1) / 2 + 2, "four", "lblx onDark"))
        if b.role == "micro_onde" and v - u > 10:
            etiquettes.append(text(xm, -(b.z0 + b.z1) / 2 + 2, "micro-ondes", "lblx onDark"))
        if getattr(b, "poignee", "") and v - u > 10:
            # poignée : tiroir en haut au centre, porte basse en haut sur le côté, porte haute en bas sur le côté,
            # relevable en bas au centre
            zt, zb, um = -b.z1 + 4, -b.z0 - 4, (u + v) / 2
            if b.role in ("facade_haut", "facade_col"):
                # façades bois : profilé toute longueur, même matière (tiroir : toute la largeur ; porte : toute la hauteur)
                if b.poignee == "tiroir":
                    o.append(f'<line class="poig bois" x1="{f(u + 2)}" y1="{f(-b.z1 + 1.5)}" x2="{f(v - 2)}" y2="{f(-b.z1 + 1.5)}"/>')
                else:
                    # C2 (frigo) : charnières au sud, poignée côté nord (à gauche en coupe C-C)
                    xp = u + 1.5 if b.nom.endswith("_c2") else v - 1.5
                    o.append(f'<line class="poig bois" x1="{f(xp)}" y1="{f(-b.z1 + 2)}" x2="{f(xp)}" y2="{f(-b.z0 - 2)}"/>')
            elif b.poignee == "tiroir":
                o.append(f'<line class="poig" x1="{f(um - 8)}" y1="{f(zt)}" x2="{f(um + 8)}" y2="{f(zt)}"/>')
            elif b.poignee == "relevable":
                o.append(f'<line class="poig" x1="{f(um - 8)}" y1="{f(zb)}" x2="{f(um + 8)}" y2="{f(zb)}"/>')
            elif b.role == "facade_haut":
                o.append(f'<line class="poig" x1="{f(v - 4)}" y1="{f(zb)}" x2="{f(v - 4)}" y2="{f(zb - 12)}"/>')
            else:
                o.append(f'<line class="poig" x1="{f(v - 4)}" y1="{f(zt)}" x2="{f(v - 4)}" y2="{f(zt + 12)}"/>')
        if (getattr(b, "contenu", "") and b.role == "etagere" and not coupe and v - u > 20
                and u1 - u0 >= d1 - d0):  # tablette vue de face (pas sur chant)
            etiquettes.append(text(xm, -(b.z1 + 17), b.contenu, "lblc"))  # au milieu de l'espace au-dessus
        elif getattr(b, "contenu", "") and b.role != "etagere" and v - u > 20:
            zc = b.z0 + 13 if b.role == "facade_haut" else b.z1 - 10
            if b.role == "facade" and 44 < zc < 60:  # pas sur l'étiquette du meuble (B2…) : en bas de la façade
                zc = b.z0 + 6
            zc = -zc
            etiquettes.append(text(xm, zc, b.contenu, "lblc"))
        if b.role == "seau" and v - u > 10:
            etiquettes.append(text(xm, -(b.z0 + b.z1) / 2 + 2, "seau", "lblx onDark"))
        if b.nom == "aspirateur_bloc" and v - u > 10:
            etiquettes.append(text(xm, -(b.z0 + b.z1) / 2 + 2, "aspirateur", "lblx onDark"))
        if b.role == "cafetiere" and v - u > 10:
            etiquettes.append(text(xm, -(b.z0 + b.z1) / 2 + 2, "café", "lblx onDark"))
        if b.role == "enceinte" and v - u > 10:
            etiquettes.append(text(xm, -(b.z0 + b.z1) / 2 + 2, "enceinte", "lblx onDark"))
        if b.role in ("ardoise", "aimant"):
            etiquettes.append(text(xm, -(b.z0 + b.z1) / 2 + 2, "tableau noir" if b.role == "ardoise" else "aimants",
                                   "lblx onDark" if b.role == "ardoise" else "lblx"))
        if getattr(b, "etiq", ""):
            zm = (b.z0 + b.z1) / 2 if b.role != "colonne" else 200
            nom, _, equip = b.etiq.partition(" ")
            etiquettes.append(text(xm, -zm + 3, nom, "lblb"))
            if equip and b.role == "caisson":
                etiquettes.append(text(xm, -zm + 12, equip, "lbls"))
        if trans and not b.nom.startswith(transparents) and derriere(b):
            # étiquettes de ce qui est derrière la porte : visibles seulement en transparence
            etiquettes[n0:] = [e.replace(' class="', f'{marque(TRANSPARENCE, "oui")} class="trp-lbl ', 1)
                               for e in etiquettes[n0:]]
    # une seule étiquette par position : celle de l'élément le plus proche (ajoutée en dernier) l'emporte
    o += list({(e.split('x="')[1].split('"')[0], e.split('y="')[1].split('"')[0]): e for e in etiquettes}.values())
    if extra:
        o += extra(X)
    o.append(f'<line class="floorl" x1="{f(umin)}" y1="0" x2="{f(umax)}" y2="0"/>')
    o.append(f'<line class="ceil" x1="{f(umin)}" y1="{-M.H}" x2="{f(umax)}" y2="{-M.H}"/>')
    for blocs, y in chaines:
        o.append(chaine(blocs, y, X, axe, origine))
    zs = [0] + hauteurs + [M.H]
    for z0, z1 in zip(zs, zs[1:]):
        o.append(cote_v(-z0, -z1, xh))
    o.append(cote_v(0, -M.H, umin - 14))
    return (f'<svg viewBox="{f(umin - 40)} -285 {f(umax - umin + 80)} 337" role="img" '
            f'aria-label="{_attr(aria)}">{"".join(o)}</svg>')


def coupe_b(aria: str) -> str:
    xmin, xmax = -20, 392
    en = M.ENTREE
    v = next(b for b in M.ENVELOPPE if b.nom == "entree_vantail")

    tn = next(b for b in M.ENVELOPPE if b.nom == "tableau_noir")
    za = next(b for b in M.ENVELOPPE if b.nom == "zone_aimantee")

    def porte(X):
        u0, u1 = sorted((X(en["x0"]), X(en["x1"])))
        w0, w1 = sorted((X(v.x0), X(v.x1)))
        p0, p1 = sorted((X(en["poche"][0]), X(en["poche"][1])))
        return [cote_h(u0, u1, 38, f'baie {f(en["x1"] - en["x0"])}'),
                cote_h(p0, p1, 38, f'poche {f(en["poche"][1] - en["poche"][0])}'),
                cote_h(w0, w1, -v.z1 - 6, f'vantail {f(v.x1 - v.x0)} × {f(v.z1 - v.z0)}'),
                cote_v(0, -en["h"], w0 - 8, f'baie h {en["h"]}'),
                cote_v(-za.z0, -za.z1, p1 + 6), cote_v(-tn.z0, -tn.z1, p1 + 6)]

    return coupe_svg(COUPE_B, "sud", xmin, xmax, [], [45, 75, 85, en["h"], M.COL_Z1], xmin - 30, porte, aria=aria)


# ------------------------------------------------------------------ règle des hauteurs de rangement (V13.23)
# Zones et repères du corps pour 1,75 m, mis à l'échelle pour les autres tailles (proportions moyennes du corps,
# estimations). Zone centrale 60 → 150 et rien au-delà de 180 sans aide d'après les guides (Bora, FCBA).
TAILLES = (175, 180)
ZONES_175 = [(0, 50, "z3", "bas"), (50, 75, "z2", "facile"), (75, 150, "z1", "zone d'or"), (150, 180, "z2", "facile"),
             (180, 200, "z3", "pointe des pieds"), (200, None, "z4", "escabeau")]
REPERES_175 = [(110, "coude"), (144, "épaule"), (163, "yeux"), (180, "main levée")]


def zones_taille(t):
    k = t / 175
    return ([(round(a * k), round(b * k) if b else M.H, c, n) for a, b, c, n in ZONES_175],
            [(round(z * k), n) for z, n in REPERES_175])


def regle(svg, umin, umax):
    """Ajoute à droite d'une coupe la règle des zones de hauteur, une par taille, marquée de sa valeur de l'option Taille.
    Masquée, aucune règle ne se montre, mais la coupe garde sa largeur avec la règle (viewBox selon la valeur : hors du
    modèle des options) ; data-vb0, data-vb1 : les deux largeurs de l'ancienne page."""
    xb = umax + 18                                   # bande de 7, noms des zones dedans (verticaux)
    o = []
    for t in TAILLES:
        zones, reperes = zones_taille(t)
        g = []
        for z0, z1, cls, nom in zones:
            zm = -(z0 + z1) / 2
            court = {"pointe des pieds": "pointe", "zone d'or": "zone d'or"}.get(nom, nom)
            g.append(rect(xb, -z1, xb + 7, -z0, cls))
            if z1 - z0 >= 18:
                g.append(f'<text class="lblz" x="{f(xb + 3.5)}" y="{f(zm)}" text-anchor="middle" dominant-baseline="central" '
                         f'transform="rotate(-90 {f(xb + 3.5)} {f(zm)})">{escape(court)}</text>')
        for z, nom in reperes:
            g.append(f'<line class="rep" x1="{f(umin)}" y1="{-z}" x2="{f(xb + 7)}" y2="{-z}"/>')
            g.append(text(xb + 9, -z + 1.5, f"{nom} {z}", "lblz rept", anchor="start"))
        g.append(text(xb + 3.5, -M.H - 8, f"{t / 100:.2f} m".replace(".", ","), "lblx"))
        o.append(f'<g class="regle" data-t="{t}"{marque(TAILLE, str(t))}>{"".join(g)}</g>')
    m = re.search(r'viewBox="(\S+) (\S+) (\S+) (\S+)"', svg)
    vb0 = " ".join(m.groups())
    vb1 = f"{m[1]} {m[2]} {f(float(m[3]) + 44)} {m[4]}"
    svg = svg.replace(m[0], f'viewBox="{vb1}" data-vb0="{vb0}" data-vb1="{vb1}"', 1)
    return svg.replace("</svg>", "".join(o) + "</svg>")


def coupe_a(aria: str) -> str:
    """Coupe A-A avec la règle des hauteurs (les deux tailles dessinées, chacune marquée de sa valeur)."""
    bas = [b for b in M.MEUBLES if b.role == "caisson" and b.y0 == 0]
    hauts = [b for b in M.MEUBLES if b.role == "caisson_haut"]
    rn = M.RAYON_NORD

    def sol(X):
        xm = X((rn["x0"] + rn["x1"]) / 2)
        return [text(xm, -30, rn["sol"].split(", ")[0] + ", " + rn["sol"].split(", ")[1], "lblc"),
                text(xm, -25, ", ".join(rn["sol"].split(", ")[2:]), "lblc")]

    svg = coupe_svg(COUPE_A, "nord", -20, 494, [(bas, 22), (hauts, -M.H - 8)],
                    [M.SOCLE, M.CAISSON_H, M.PT_Z1, M.HAUT_Z0, M.HAUT_JOINT, M.HAUT_Z1], -50, sol, aria=aria)
    return regle(svg, -20, 494)


def coupe_c(aria: str) -> str:
    """Coupe C-C avec la règle des hauteurs, la porte du cellier dessinée opaque et en transparence (option)."""
    cols = sorted([b for b in M.MEUBLES if b.role == "colonne"], key=lambda b: b.y0)
    def cellier(X):
        return [cote_h(X(M.BAIE_Y0), X(M.BAIE_Y1), -M.H - 8, f"baie {f(M.BAIE_Y1 - M.BAIE_Y0)}"),
                cote_h(X(M.BAIE_Y1 - M.PASSAGE_CELLIER), X(M.BAIE_Y1), -204 - 6, f"passage {f(M.PASSAGE_CELLIER)}")]

    svg = coupe_svg(COUPE_C, "est", -20, 262, [(cols, 22)],
                    [M.SOCLE_COL, M.LV_Z0, M.MO_Z0, M.MO_Z1, M.FRIGO_Z1, M.COL_Z1], -50, cellier,
                    transparents=("cellier_pliante", "linteau_cellier"), aria=aria)
    return regle(svg, -20, 262)


# pastilles de la légende de la règle (ancien TAILLE_LEG)
REGLE_LEGENDE = ('<span class="leg"><i class="sw" style="background:#5B9E6A"></i>zone d\'or '
                 '<i class="sw" style="background:#A9CF8F"></i>facile '
                 '<i class="sw" style="background:#E8C26A"></i>bas ou pointe des pieds '
                 '<i class="sw" style="background:#D9826B"></i>escabeau</span>')


def hauteur_pt_svg(aria: str) -> str:
    zmin, zmax, k, y0 = 78, 118, 8, 24
    Y = lambda z: y0 + (zmax - z) * k
    o = []
    for z in range(zmin, zmax + 1, 2):
        o.append(f'<line class="hpg" x1="70" y1="{Y(z)}" x2="470" y2="{Y(z)}"/>')
        if z % 4 == 2:
            o.append(f'<text class="hpt" x="62" y="{Y(z) + 4}" text-anchor="end">{z}</text>')
    for h, _, _ in M.PT_CANDIDATS:
        cls = "hpc act" if h == M.PT_Z1 else ("hpc rec" if h == M.PT_RECO else "hpc")
        lib = f"{h} actuel" if h == M.PT_Z1 else (f"{h} conseillé" if h == M.PT_RECO else str(h))
        o.append(f'<line class="{cls}" x1="80" y1="{Y(h)}" x2="470" y2="{Y(h)}"/>'
                 f'<text class="hpt {cls}" x="476" y="{Y(h) + 4}">{lib}</text>')
    (al, ah), (ll, lh) = M.HSE_APPUI, M.HSE_LEGER
    for i, (nom, c) in enumerate(M.COUDES.items()):
        x0, x1 = 110 + i * 210, 240 + i * 210
        # bandes HSE : appui à gauche, geste léger à droite (bornées au cadre du schéma)
        for xb, (s0, s1), cls in ((x0 - 12, M.HSE_APPUI, "hsa"), (x1 + 4, M.HSE_LEGER, "hsl")):
            z0, z1 = max(zmin, c - s1), min(zmax, c - s0)
            o.append(f'<rect class="{cls}" x="{xb}" y="{Y(z1)}" width="8" height="{(z1 - z0) * k}" rx="2"/>')
        lo, hi = c - M.PT_SOUS_COUDE[1], c - M.PT_SOUS_COUDE[0]
        o.append(f'<rect class="z1 hpb" x="{x0}" y="{Y(hi)}" width="{x1 - x0}" height="{(hi - lo) * k}" rx="3"/>')
        o.append(f'<text class="hpt on" x="{(x0 + x1) / 2}" y="{Y((lo + hi) / 2) + 4}" text-anchor="middle">plan {lo} → {hi}</text>')
        zp = c - M.PLAQUE_SOUS_COUDE
        o.append(f'<line class="hpp" x1="{x0}" y1="{Y(zp)}" x2="{x1}" y2="{Y(zp)}"/>'
                 f'<text class="hpt hph" x="{x0 - 16}" y="{Y(zp) + 4}" text-anchor="end">plaque {zp}</text>')
        o.append(f'<line class="rep" x1="{x0}" y1="{Y(c)}" x2="{x1}" y2="{Y(c)}" style="stroke-width:1.5"/>'
                 f'<text class="hpt rept" x="{(x0 + x1) / 2}" y="{Y(c) - 6}" text-anchor="middle">coude {c}</text>')
        o.append(f'<text class="hpn" x="{(x0 + x1) / 2}" y="14" text-anchor="middle">{nom}</text>')
    return f'<svg viewBox="0 0 570 {Y(zmin) + 12}" role="img" aria-label="{_attr(aria)}">{"".join(o)}</svg>'


# ------------------------------------------------------------------ électricité
# position du symbole sur le plan quand elle diffère du boîtier (boîtiers groupés, au fond des meubles)
POS_PLAN = {"P5": (15, 24), "P6": (15, 42), "P4": (55, 14), "P7": (372, M.JOUE_C2 + 15), "P8": (372, M.JOUE_C2 + 47),
            "P9": (372, M.COL_Y0 + 15), "S2": (M.X_CLOISON - 5, 21)}


def minus(nom):
    """Première lettre en minuscule, sauf sigle (« LED »)."""
    return nom if nom[1:2].isupper() else nom[0].lower() + nom[1:]


def pos_plan(rep, x, y):
    """Symbole devant le mur (5 vers l'intérieur de la pièce), sauf position imposée."""
    if rep in POS_PLAN:
        return POS_PLAN[rep]
    if y == 0:
        return x, 5
    if x == 0:
        return 5, y
    return x, y - 5   # mur sud ou fileur de l'entrée (face nord)


def sym_lumiere(x, y, r=6):
    d = r * 0.7
    return (f'<circle class="ell" cx="{f(x)}" cy="{f(y)}" r="{f(r)}"/>'
            f'<path class="ellx" d="M{f(x - d)} {f(y - d)}L{f(x + d)} {f(y + d)}M{f(x - d)} {f(y + d)}L{f(x + d)} {f(y - d)}"/>')


def sym_prise(x, y, socles, cache=False, dedie=False):
    cls = "elp" + (" elpd" if dedie else "") + (" elc" if cache else "")
    if socles == 1:
        return f'<circle class="{cls}" cx="{f(x)}" cy="{f(y)}" r="3"/>'
    return f'<rect class="{cls}" x="{f(x - 5.5)}" y="{f(y - 3)}" width="11" height="6" rx="3"/>'


def sym_inter(x, y):
    return (f'<circle class="eli" cx="{f(x)}" cy="{f(y)}" r="3.2"/>'
            f'<line class="elil" x1="{f(x + 2.2)}" y1="{f(y - 2.2)}" x2="{f(x + 6)}" y2="{f(y - 6)}"/>')


def plan_elec_svg(aria: str) -> str:
    o = [f'<polygon class="floorbg" points="{pts(M.SOL_PARQUET)}"/>', f'<polygon class="ciment" points="{pts(M.SOL_CIMENT)}"/>',
         f'<polygon class="wc" points="{pts(M.WC)}"/>', text(438, 185, "WC", "lbl muted"),
         '<g class="fade">'] + volumes_plan() + ["</g>"]
    for b in M.MEUBLES:
        if b.role in ("caisson", "colonne") and b.etiq:
            nom = b.etiq.split(" ")[0]
            y = (74 if b.y1 >= M.P_CAISSON else b.y1 / 2 + 3) if b.role == "caisson" else (b.y0 + b.y1) / 2 + 3
            o.append(text((b.x0 + b.x1) / 2, y, nom, "lbls muted"))
    lum = {r: (x, y) for r, _, x, y, _ in M.LUMIERES}
    inter = {r: pos_plan(r, x, y) for r, _, x, y, _, _, _ in M.INTERRUPTEURS}
    # liaisons de commande : de chaque interrupteur à la lumière qu'il commande
    for r, _, _, _, _, _, touches in M.INTERRUPTEURS:
        sx, sy = inter[r]
        for _, l, _ in touches:
            lx, ly = lum[l]
            mx, my = (sx + lx) / 2, (sy + ly) / 2
            nx, ny = -(ly - sy), lx - sx
            n = math.hypot(nx, ny) or 1
            k = 0.18 * math.dist((sx, sy), (lx, ly))
            o.append(f'<path class="elk" d="M{f(sx)} {f(sy)}Q{f(mx + nx / n * k)} {f(my + ny / n * k)} {f(lx)} {f(ly)}"/>')
    for r, nom, x, y, _ in M.LUMIERES:
        o.append(sym_lumiere(x, y))
        o.append(text(x + 8, y - 5, f"{r} {minus(nom)}", "lbls elt", "start"))
    for r, _, x, y, z, _, _ in M.INTERRUPTEURS:
        px, py = inter[r]
        o.append(sym_inter(px, py))
        ty = py + 10 if y == 0 else py - 6
        o.append(text(px + (5 if x == 0 else 0), ty, f"{r} h{z}", "lbls elt", "start" if x == 0 else "middle"))
    for r, x, y, z, n, c, _, ou in M.PRISES:
        px, py = pos_plan(r, x, y)
        o.append(sym_prise(px, py, n, ou.startswith("dans"), c not in ("plan", "autres")))
        if x == 0:
            o.append(text(px + 8, py + 2, f"{r} h{z}", "lblx elpt", "start"))
        elif x >= M.COL_DOS - 1:
            o.append(text(px - 5, py + 2, f"{r} h{z}", "lblx elpt", "end"))
        elif y == M.Y_MUR_SUD:
            o.append(text(px, py - 6, f"{r} h{z}", "lblx elpt"))
        else:
            o.append(text(px + 6, py + 2, f"{r} h{z}", "lblx elpt", "start"))
    # légende
    y = 290
    leg = [(sym_lumiere(0, y, 4.5), "point lumineux"), (sym_inter(0, y), "interrupteur"),
           (sym_prise(0, y, 1), "prise"), (sym_prise(0, y, 2), "prise double"),
           (sym_prise(0, y, 1, dedie=True), "circuit spécialisé"), (sym_prise(0, y, 1, cache=True), "dans un meuble")]
    for k, (s, t) in enumerate(leg):
        x = k * 70
        o.append(f'<g transform="translate({x} 0)">{s}</g>' + text(x + 10, y + 2, t, "lbls", "start"))
    o.append(f'<path class="elk" d="M{6 * 70} {y}h18"/>' + text(6 * 70 + 22, y + 2, "commande", "lbls", "start"))
    return f'<svg viewBox="-30 -15 545 320" role="img" aria-label="{_attr(aria)}">{"".join(o)}</svg>'


def coupe_elec_nord(aria: str) -> str:
    """Élévation du mur nord (coupe A-A) avec les boîtiers posés sur ce mur ou au fond des meubles de la rangée."""
    def boitiers(X):
        o = []
        for r, x, y, z, n, c, _, ou in M.PRISES:
            if y != 0:
                continue
            w = 7 if n == 1 else 13
            cls = "elpe" + (" elpd" if c not in ("plan", "autres") else "") + (" elc" if ou.startswith("dans") else "")
            o.append(rect(X(x) - w / 2, -z - 3.5, X(x) + w / 2, -z + 3.5, cls))
            o.append(text(X(x), -z - 6, r, "lblx elpt"))
        for r, _, x, y, z, _, touches in M.INTERRUPTEURS:
            if y == 0:
                h = 7 * len(touches)
                o.append(rect(X(x) - 3.5, -z - h / 2, X(x) + 3.5, -z + h / 2, "elie"))
                o.append(text(X(x), -z - h / 2 - 2.5, r, "lblx elt"))
        o.append(text(X(145), -M.HAUT_Z0 + 7, "L2, LED", "lblx elt"))
        return o

    return coupe_svg(COUPE_A, "nord", -20, 494, [], [M.PT_Z1, 110, M.HAUT_Z0], -50, boitiers, aria=aria)


# CSS des dessins : celui de l'ancienne page (pieces/cuisine/dessin.py, CSS) sans les règles de page (mode sombre,
# @media, mise en page, sommaire, barres, boutons, tableaux), sans police à chasse fixe (chiffres tabulaires à la
# place), sans les règles qui cachaient un état (les options le font par data-si). `.trp` : le contour tireté de la
# porte en transparence, dessin à part. --cement, --elec et --prise, absents de site.css, ont leur valeur en repli.
CSS_DESSINS = """
.z1{fill:#5B9E6A;opacity:.85}.z2{fill:#A9CF8F;opacity:.85}.z3{fill:#E8C26A;opacity:.85}.z4{fill:#D9826B;opacity:.85}
.rep{stroke:#C8412C;stroke-width:.5;stroke-dasharray:3 2;opacity:.7}.rept{fill:#C8412C}
.lblz{font-size:3.8px;fill:var(--ink)}.hsa{fill:#C98A1E;opacity:.45}.hsl{fill:#2F7FB5;opacity:.4}.hpb{opacity:.92}text.hph{fill:#C98A1E;font-weight:600;paint-order:stroke;stroke:var(--panel);stroke-width:4px}.hpg{stroke:var(--line);stroke-width:.6}.hpt{font-size:12px;fill:var(--muted)}.hpt.on{fill:#fff;font-weight:600}.hpt.rept{fill:#C8412C}.hpn{font-size:15px;font-weight:700;fill:var(--ink)}.hpp{stroke:#C98A1E;stroke-width:2}.hpc{stroke:var(--ink);stroke-width:1;stroke-dasharray:5 4;opacity:.7}.hpc.act{stroke-dasharray:none;stroke-width:2;opacity:1}.hpc.rec{stroke:#2F7FB5;opacity:1}text.hpc{stroke:none;fill:var(--ink);font-weight:600}text.hpc.rec{fill:#2F7FB5}.lblz.rept{fill:#C8412C}
.leg .sw{display:inline-block;width:12px;height:9px;border-radius:2px;margin:0 3px 0 8px;vertical-align:middle}
.w{fill:var(--ink)}
.bgwall{fill:var(--line);fill-opacity:.35}
.wallv{fill:#D5DADD;stroke:var(--muted);stroke-width:.5}
.floorbg{fill:var(--wood);fill-opacity:.13}
.wc{fill:var(--line);fill-opacity:.55}
.lame{fill:none;stroke:var(--wood);stroke-width:.5;stroke-opacity:.5}
.ciment{fill:var(--cement,#C9CBCA)}
.depose{fill:none;stroke:var(--muted);stroke-width:.8;stroke-dasharray:4 3}
.win{fill:var(--glass);stroke:var(--ink);stroke-width:.7}
.glass{stroke:var(--water);stroke-width:1.4}
.tech{fill:var(--tech);stroke:var(--ink);stroke-width:.7;stroke-dasharray:3 2}
.cab{fill:var(--cab);stroke:var(--ink);stroke-width:.7}
.fac{fill:var(--tall);stroke:var(--ink);stroke-width:.7}
.plinth{fill:#EFE9DC;stroke:var(--ink);stroke-width:.6}
.ecs{fill:var(--panel);stroke:var(--water);stroke-width:1.2}
.leaf{fill:var(--wood);stroke:var(--ink);stroke-width:.6}
.ghost{fill:none;stroke:var(--muted);stroke-width:.8;stroke-dasharray:4 3}
.dark{fill:var(--ink)}
.pt{fill:var(--panel);fill-opacity:.55;stroke:var(--ink);stroke-width:1.1}
.ptbase{fill:var(--panel);stroke:none}
.peint{fill:#4B2E3B;fill-opacity:.35;stroke:none}
.egout{fill:#D9D9D6;stroke:var(--ink);stroke-width:.5;stroke-dasharray:1 1.5}
.vitro{fill:var(--ink);stroke:var(--ink);stroke-width:.6}
.asp{fill:var(--muted)}
.inox{fill:var(--tech);stroke:var(--ink);stroke-width:.6}
.cuve{fill:var(--panel);stroke:var(--ink);stroke-width:.7}
.onDark{fill:var(--paper)}
.tall{fill:var(--tall);stroke:var(--ink);stroke-width:.8}
.neuf{fill:var(--wood);stroke:var(--ink);stroke-width:.6}
.pin{fill:none;stroke:var(--water);stroke-width:1.6}
.pout{fill:none;stroke:var(--water);stroke-width:1.6;stroke-dasharray:5 3}
.chute{fill:var(--panel);stroke:var(--water);stroke-width:1.6}
.nourrice{fill:var(--water)}
.tri{fill:var(--tri);fill-opacity:.07;stroke:var(--tri);stroke-width:1.4}
.triv{fill:var(--tri)}
.tribg{fill:var(--panel);stroke:var(--tri);stroke-width:.6}
.trit{fill:var(--tri);font-variant-numeric:tabular-nums;font-size:7px;font-weight:600;text-anchor:middle}
.tbl{fill:var(--wood);fill-opacity:.5;stroke:var(--ink);stroke-width:.9}
.stool{fill:var(--wood);fill-opacity:.28;stroke:var(--ink);stroke-width:.7}
.swingz{fill:var(--tri);fill-opacity:.05;stroke:var(--muted);stroke-width:.7;stroke-dasharray:3 2}
.swing{fill:none;stroke:var(--muted);stroke-width:.7;stroke-dasharray:2 2}
.doorleaf{stroke:var(--ink);stroke-width:2}
.ardoise{fill:#2B3230;stroke:var(--ink);stroke-width:.6}.aimant{fill:#A7AEB2;stroke:var(--ink);stroke-width:.6}
.lampe{fill:#F2C94C;fill-opacity:.35;stroke:#B8860B;stroke-width:.7;stroke-dasharray:3 2}
.lblc{font-size:3.6px;font-style:italic;fill:var(--ink)}
.plante{fill:#6E9B5A;fill-opacity:.8;stroke:#3F6B31;stroke-width:.6;stroke-dasharray:3 2}.pot{fill:#C2703D;stroke:var(--ink);stroke-width:.5}
.aspi{fill:#8A97A3;stroke:var(--ink);stroke-width:.6}
.cafe{fill:#1C1E21;fill-opacity:.35;stroke:var(--ink);stroke-width:.5}
.led{fill:#F2C94C;stroke:#B8860B;stroke-width:.4}
.poig{stroke:#8E8E8B;stroke-width:1.4;stroke-linecap:round}
.poig.bois{stroke:#8A5A2B;stroke-width:2.2;stroke-linecap:butt}
.balai{fill:#C9A46A;stroke:var(--ink);stroke-width:.4}
.pliee{fill:none;stroke:var(--ink);stroke-width:2.5;stroke-linejoin:round}
.trp{fill:none;stroke:var(--ink);stroke-width:.7;stroke-dasharray:4 2}
.dorm{fill:var(--panel);stroke:var(--ink);stroke-width:.6}
.seuil{stroke:var(--muted);stroke-width:.7;stroke-dasharray:3 2}
.slid{fill:var(--wood);fill-opacity:.55;stroke:var(--wood);stroke-width:.6}
.pivot{fill:var(--paper);stroke:var(--ink);stroke-width:.8}
.leafd{stroke:var(--ink);stroke-width:3;stroke-linecap:round}
.leafg{stroke:var(--muted);stroke-width:1.5;stroke-opacity:.45;stroke-dasharray:3 2}
.move{stroke:var(--tri);stroke-width:1;stroke-dasharray:2.5 2;fill:none}.flm{fill:var(--tri)}
.diag{stroke:var(--tri);stroke-width:1;stroke-dasharray:4 2}.diagt{font-weight:600;font-size:8px;font-variant-numeric:tabular-nums;fill:var(--tri)}
.celsol{fill:var(--ink);fill-opacity:.1}
.shelf,.shelfd{fill:var(--wood);fill-opacity:.3;stroke:var(--wood);stroke-width:.6}
.shelfc{fill:var(--wood);stroke:var(--ink);stroke-width:.6}
.trappe{fill:var(--wood);fill-opacity:.12;stroke:var(--ink);stroke-width:.8;stroke-dasharray:3 2}
.frame{fill:none;stroke:var(--line);stroke-width:.8}
.upper{fill:none;stroke:var(--ink);stroke-width:.8;stroke-dasharray:3 2}
.dim{stroke:var(--muted);stroke-width:.6;fill:none}
.dimt{fill:var(--muted);font-variant-numeric:tabular-nums;font-size:8px}
.lbl{font-size:7.5px}.lbls{font-size:6.5px}.lblx{font-size:5px}.lblb{font-size:9px;font-weight:700}
.muted{fill:var(--muted)}
.sec{stroke:var(--tri);stroke-opacity:.3;stroke-width:.9;stroke-dasharray:10 3 2 3;fill:none}
.secm{fill:var(--tri);fill-opacity:.45}
.sect{fill:var(--tri);fill-opacity:.55;font-weight:800;font-size:11px}
.floorl{stroke:var(--ink);stroke-width:2}
.ceil{stroke:var(--muted);stroke-width:1;stroke-dasharray:6 4}
.fade{opacity:.4}
.ell{fill:#F2C94C;fill-opacity:.45;stroke:var(--elec,#A86F00);stroke-width:1}.ellx{stroke:var(--elec,#A86F00);stroke-width:1}
.eli{fill:var(--panel);stroke:var(--elec,#A86F00);stroke-width:1.1}.elil{stroke:var(--elec,#A86F00);stroke-width:1.1}
.elk{fill:none;stroke:var(--elec,#A86F00);stroke-width:.8;stroke-dasharray:3 2}
.elp,.elpe{fill:var(--panel);stroke:var(--prise,#7B4FBF);stroke-width:1.1}.elpd{fill:var(--prise,#7B4FBF)}.elc{stroke-dasharray:2 1.2}
.elie{fill:var(--panel);stroke:var(--elec,#A86F00);stroke-width:1.1}
.elt{fill:var(--elec,#A86F00);font-weight:700}.elpt{fill:var(--prise,#7B4FBF);font-weight:600}
.hpw svg{display:block;width:100%;min-width:480px;max-width:690px;height:auto;margin:0 auto}
tr.hpr td{background:color-mix(in srgb,#2F7FB5 10%,transparent)}
.note{font-size:13px;color:var(--muted)}
.tango th{width:190px}
.capa td.ok{background:color-mix(in srgb,#3E8E5A 20%,transparent)}
.capa td.ko{background:color-mix(in srgb,var(--tri) 22%,transparent)}
td.num,th.num{text-align:right;white-space:nowrap}
.mat th{width:30%;color:var(--ink);font-weight:600;font-size:15px;padding-right:16px}
.ech{display:block;margin:0 0 6px}
"""
