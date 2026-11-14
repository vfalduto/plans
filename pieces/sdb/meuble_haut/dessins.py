"""Les dessins du meuble haut : iso du caisson et vue éclatée, pose au mur (de face et en coupe), schémas des étapes,
pièces seules, faces percées des fiches, calepinage, perçage type et icônes de quincaillerie.

Repris de 3d/sdb/montage.py et plan.py (page sdb-meuble-haut.html, V6.4), avec les mêmes calculs. Ce qui change : la
police du socle à la place de la chasse fixe, des virgules à la place des points médians dans les étiquettes, les
couleurs écrites en valeur (les jetons --dg, --haut, --tile n'existent pas dans commun/site.css, et --bas y vaut 0px),
un motif de carrelage par dessin (deux dessins ne partagent plus un même id) et un texte alternatif par face.
Le modèle est celui de 3d/sdb/modele.py (modele.M) ; la projection isométrique et les murs, ceux de pieces/sdb/iso.py.
"""
from collections import Counter
from html import escape

from pieces.sdb import dessin_cotes as DC, iso
from pieces.sdb.meuble_haut.modele import M, cm

f, text = DC.f, DC.text


# ------------------------------------------------------------------ iso du caisson, et vue éclatée
def _tout():
    return [b for b in M.version("d") if b.role != "prise"]


def iso_meuble(label="Caisson haut, vue iso") -> str:
    bl = [b for b in _tout() if b.groupe == "caisson_haut"]
    return iso.dessin(bl, reperes=False, titre=label)


SOUS_ENSEMBLE = "Caisson haut"
FILTRE = lambda b: b.groupe == "caisson_haut" and b.role != "led"      # noqa: E731
DIAM = {"insert": (1.0, None), "vis16": (0.4, 0.25), "vis60": (0.5, 0.3), "vis40": (0.4, 0.25), "vis40l": (1.0, 0.3),
        "vis16l": (1.0, 0.25), "confirmat": (0.5, 0.4), "cuvette": (3.5, None), "prise": (2.5, None),
        "cheville": (0.6, None), "depart": (1.0, None), "doigt": (2.0, None)}   # Ø passage, Ø avant-trou (cm)
FACE_NOM = {(0, -1): "face avant", (0, 1): "face arrière", (1, -1): "côté nord", (1, 1): "côté sud",
            (2, -1): "dessous", (2, 1): "dessus"}


def eclate(bl, k=0.7):
    """Écarte chaque pièce du centre du sous-ensemble ; renvoie les pièces déplacées et leur décalage par nom."""
    if len(bl) < 2:
        return bl, {b.nom: (0, 0, 0) for b in bl}
    cx = sum((b.x0 + b.x1) / 2 for b in bl) / len(bl)
    cy = sum((b.y0 + b.y1) / 2 for b in bl) / len(bl)
    cz = sum((b.z0 + b.z1) / 2 for b in bl) / len(bl)
    r, d = [], {}
    for b in bl:
        dx, dy, dz = (((b.x0 + b.x1) / 2 - cx) * k, ((b.y0 + b.y1) / 2 - cy) * k, ((b.z0 + b.z1) / 2 - cz) * k)
        d[b.nom] = (dx, dy, dz)
        if isinstance(b, M.Profil):
            r.append(M.replace(b, xz=[(x + dx, z + dz) for x, z in b.xz], y0=b.y0 + dy, y1=b.y1 + dy))
        else:
            r.append(M.replace(b, x0=b.x0 + dx, x1=b.x1 + dx, y0=b.y0 + dy, y1=b.y1 + dy, z0=b.z0 + dz, z1=b.z1 + dz))
    return r, d


def _sous_ensemble():
    return [b for b in M.version("d") if b.role not in ("prise", "sac", "machine") and FILTRE(b)]


def vue_eclatee(label="Caisson haut, vue éclatée") -> str:
    bl, dec = eclate(_sous_ensemble())
    trs = []
    for t in M.TROUS:
        if t["a"] in dec:
            dx, dy, dz = dec[t["a"]]
            trs.append(dict(t, x=t["x"] + dx, y=t["y"] + dy, z=t["z"] + dz))
    return iso.dessin(bl, {b.nom for b in bl}, titre=label, trous=trs)


# ------------------------------------------------------------------ pièces seules (cartes)
def piece_seule(rep: str, label: str) -> str:
    b = next(b for b in M.PIECES if b.rep == rep)
    if isinstance(b, M.Profil):
        bb = M.replace(b, xz=[(x - b.x0, z - b.z0) for x, z in b.xz], y0=0, y1=b.y1 - b.y0)
    else:
        bb = M.replace(b, x0=0, x1=b.x1 - b.x0, y0=0, y1=b.y1 - b.y0, z0=0, z1=b.z1 - b.z0, encoche=())
    return iso.dessin([bb], {bb.nom}, reperes=False, marge=3, titre=label)


# ------------------------------------------------------------------ schémas des étapes 8, 9 et 10
def _cales(xs, ys):
    """Deux cales de la hauteur de la niche, sous le caisson haut."""
    r = []
    for y in (12, M.Y1 - 22):
        cale = M.Bloc("cale", "cale", M.CH["x0"] + 8, M.CH["x0"] + 18, y, y + 10, M.Z_DESSUS, M.Z_HAUT)
        for fc, nn in iso.faces(cale):
            if sum(a * b for a, b in zip(nn, iso.VUE)) > 0:
                r.append(f'<polygon class="ical" points="{iso.pts_svg([iso.proj(*q) for q in fc])}"/>')
    return r


def trous_etape(n, bl):
    noms = {b.nom for b in bl}
    return [t for t in M.TROUS if t["etape"] == n and t["a"] in noms]


def dessin_etape(n: int) -> str:
    """Le résultat de l'étape n (8, 9 ou 10) : l'étape 8 le caisson seul ; les étapes 9 et 10 avec les murs et toutes
    les pièces posées jusque-là (le modèle V6 du meuble bas comprise)."""
    tout = M.version("d")
    neuves = {b.nom for b in tout if b.etape == n and b.role not in ("prise",)}
    if n == 8:
        bl = [b for b in tout if b.groupe == "caisson_haut" and b.etape <= n and b.role != "led"]
        return iso.dessin(bl, neuves, titre=f"Étape {n}", trous=trous_etape(n, bl))
    bl = [b for b in tout if 0 < b.etape <= n and b.role != "prise"]
    if n == M.POSE_HAUT:
        neuves = {b.nom for b in tout if b.groupe == "caisson_haut" and b.etape <= n}
        return iso.dessin(bl, neuves, murs=True, reperes=False, extra=_cales, titre=f"Étape {n}")
    return iso.dessin(bl, neuves, murs=n >= 4, titre=f"Étape {n}", trous=trous_etape(n, bl))


def pieces_etape(n):
    """Repères et nombre de pièces de l'étape (une cornière E2 modélisée en deux ailes compte pour une)."""
    cpt = Counter(b.rep for b in M.version("d") if b.etape == n and b.role not in ("prise",) and b.rep)
    if "E2" in cpt:
        cpt["E2"] = 1
    return sorted(cpt.items(), key=lambda t: (t[0][0], int(t[0][1:])))


def percages(n):
    """Perçages de l'étape, regroupés par assemblage : (assemblage, trous, pièce traversée, pièce reçue, vis, position)."""
    grp = {}
    for t in M.TROUS:
        if t["etape"] == n:
            g = grp.setdefault((t["ra"], t["rb"], t["vis"]), dict(q=0, pos=t["pos"]))
            g["q"] += 1
    lignes = []
    for (ra, rb, vis), g in grp.items():
        ou = f"{ra} {M.NOMS.get(ra, '')}" + (f", vers {rb} {M.NOMS.get(rb, '')}" if rb else "")
        passage, avant = M.PERCAGE[vis]
        lignes.append((ou, g["q"], passage, avant, M.VIS[vis], g["pos"]))
    return lignes


# ------------------------------------------------------------------ faces percées (fiches de pièce)
def trous_de(nom, role):
    """Trous d'une pièce : role "a" (on la traverse) ou "b" (elle reçoit la vis)."""
    return [t for t in M.TROUS if t[role] == nom]


def face_svg(b, k, s, trous_a, trous_b, label="") -> str:
    """Une face de la pièce à plat : normale k (0 x, 1 y, 2 z), sens s ; trous et entailles cotés depuis le coin bas gauche.
    Dessin schématique : la longueur est ramenée à 100, l'épaisseur des pièces très fines est agrandie pour rester
    lisible ; les cotes, elles, sont vraies (mm)."""
    bornes = [(b.x0, b.x1), (b.y0, b.y1), (b.z0, b.z1)]
    autres = [i for i in range(3) if i != k]
    h = max(autres, key=lambda i: bornes[i][1] - bornes[i][0])
    v = autres[0] if autres[1] == h else autres[1]
    profil = isinstance(b, M.Profil) and k == 1
    if profil:                          # pièce profilée (support en demi-lune) : vue de face, le dessus en haut
        h, v = 0, 2
    W, H = bornes[h][1] - bornes[h][0], bornes[v][1] - bornes[v][0]
    u0, v0 = bornes[h][0], bornes[v][0]
    sx = 100 / W if W > 25 else 4
    sy = min(max(sx, 9 / H), 90 / H)
    w_, h_ = W * sx, H * sy
    fs = 3.4
    X = lambda u: u * sx                # noqa: E731
    Y = lambda w: h_ - w * sy           # noqa: E731
    if profil:
        o = [f'<polygon class="fpc {M.meuble(b.rep)}" points="' +
             " ".join(f"{X(x - u0):.2f},{Y(z - v0):.2f}" for x, z in b.xz) + '"/>']
    else:
        o = [f'<rect class="fpc {M.meuble(b.rep)}" x="0" y="0" width="{w_:.2f}" height="{h_:.2f}"/>']
    if isinstance(b, M.Bloc) and b.encoche and k == 2:      # trou de la trappe
        x0, x1, y0, y1 = b.encoche
        r_ = {0: (x0, x1), 1: (y0, y1)}
        o.append(f'<rect class="fent" x="{X(r_[h][0] - u0):.2f}" y="{Y(r_[v][1] - v0):.2f}" '
                 f'width="{(r_[h][1] - r_[h][0]) * sx:.2f}" height="{(r_[v][1] - r_[v][0]) * sy:.2f}" rx="{0.5 * sx:.2f}"/>')
    for e in getattr(b, "entailles", ()) if k == 2 else ():
        x0, x1, y0, y1 = e
        r_ = {0: (x0, x1), 1: (y0, y1)}
        a0, a1 = r_[h]
        c0, c1 = r_[v]
        o.append(f'<rect class="fent" x="{X(a0 - u0):.2f}" y="{Y(c1 - v0):.2f}" width="{(a1 - a0) * sx:.2f}" '
                 f'height="{(c1 - c0) * sy:.2f}"/>')
    us, vs = set(), set()
    for t, cls in [(t, "fta") for t in trous_a] + [(t, "ftb") for t in trous_b]:
        c = (t["x"], t["y"], t["z"])
        u, w = c[h] - u0, c[v] - v0
        dp, da = DIAM.get(t["vis"], (0.4, 0.25))
        rr = (dp if cls == "fta" else (da or dp)) / 2 * min(sx, sy)
        o.append(f'<circle class="{cls}" cx="{X(u):.2f}" cy="{Y(w):.2f}" r="{min(max(rr, 0.9), 6):.2f}"/>')
        us.add(round(u, 1))
        vs.add(round(w, 1))
    rangs, der = [], []
    for u in sorted(us):                # cotes en bas, sur plusieurs rangs si elles se touchent
        k_ = next((i for i, x in enumerate(der) if X(u) - x > 9), len(der))
        if k_ == len(der):
            der.append(-99)
        der[k_] = X(u)
        y = h_ + (k_ + 1) * (fs + 0.8)
        o.append(f'<line class="fdim" x1="{X(u):.2f}" y1="{h_:.2f}" x2="{X(u):.2f}" y2="{y - fs + .4:.2f}"/>'
                 f'<text class="ftx" x="{X(u):.2f}" y="{y:.2f}" text-anchor="middle" style="font-size:{fs}px">{u * 10:.0f}</text>')
    nb = len(der)
    gauche, der = [], []
    for w in sorted(vs):                # cotes à gauche, décalées si elles se touchent
        k_ = next((i for i, x in enumerate(der) if Y(w) < x - fs), len(der))
        if k_ == len(der):
            der.append(999)
        der[k_] = Y(w)
        o.append(f'<text class="ftx" x="{-1 - k_ * 9:.2f}" y="{Y(w) + fs * .35:.2f}" style="font-size:{fs}px" '
                 f'text-anchor="end">{w * 10:.0f}</text>')
    o.append(f'<text class="ftx muted" x="{w_:.2f}" y="{-1.2:.2f}" text-anchor="end" style="font-size:{fs}px">'
             f'{W * 10:.0f} × {H * 10:.0f}</text>')
    gx = 3 + 9 * max(1, len(der))
    vw, vh = w_ + gx + 2, h_ + fs + 2.5 + nb * (fs + 0.8)
    return (f'<svg class="face" viewBox="{-gx:.2f} {-fs - 2:.2f} {vw:.2f} {vh:.2f}" '
            f'style="max-width:{vw * 2.6:.0f}px" role="img" aria-label="{escape(label or b.rep)}">{"".join(o)}</svg>')


def signature(b):
    """Motif de perçage d'une pièce (coordonnées locales) : deux pièces de même repère et même motif ne font qu'une fiche."""
    m = []
    for role in ("a", "b"):
        for t in trous_de(b.nom, role):
            m.append((role, t["vis"], t["n"], round(t["x"] - b.x0, 1), round(t["y"] - b.y0, 1), round(t["z"] - b.z0, 1)))
    return tuple(sorted(m))


def fiche(b, q) -> str:
    """La fiche d'une pièce : son repère, son nom, sa quantité, ses cotes, ses faces percées et avec quoi elle s'assemble."""
    faces = {}
    for role in ("a", "b"):
        for t in trous_de(b.nom, role):
            k = next(i for i, c in enumerate(t["n"]) if c)
            faces.setdefault((k, t["n"][k]), {"a": [], "b": []})[role].append(t)
    if getattr(b, "entailles", ()) and (2, 1) not in faces:
        faces[(2, 1)] = {"a": [], "b": []}
    if isinstance(b, M.Profil) and not any(k == 1 for k, _ in faces):     # profil (demi-lune) : toujours la vue de côté
        faces[(1, -1)] = {"a": [], "b": []}
    dims = sorted((b.x1 - b.x0, b.y1 - b.y0, b.z1 - b.z0), reverse=True)
    lien = Counter()
    for t in trous_de(b.nom, "a"):
        lien[(t["rb"] or "", t["vis"], "dans")] += 1
    for t in trous_de(b.nom, "b"):
        lien[(t["ra"], t["vis"], "depuis")] += 1
    liens = "".join(f'<li>{n} × {escape(M.VIS[v])} ' + (f'{"dans" if d == "dans" else "venant de"} <b>{r}</b> '
                    f'{escape(M.NOMS.get(r, ""))}' if r else f'({escape(M.PERCAGE[v][0])})') + '</li>'
                    for (r, v, d), n in lien.items())
    nom = M.NOMS.get(b.rep, b.nom)
    figs = "".join(f'<div class="fface"><div class="fnom">{FACE_NOM[(k, s)]}</div>'
                   f'{face_svg(b, k, s, f_["a"], f_["b"], f"{b.rep} {nom}, {FACE_NOM[(k, s)]}")}</div>'
                   for (k, s), f_ in sorted(faces.items()))
    if not figs:
        figs = '<p class="remarque">Aucun perçage.</p>'
    return (f'<div class="fiche"><div class="ftete"><b class="crep">{b.rep}</b> {escape(nom)}'
            f'<span class="cq">× {q}</span><span class="dims">{" × ".join(f"{d * 10:.0f}" for d in dims)}</span></div>'
            f'{figs}<ul class="fliens">{liens}</ul></div>')


def fiches() -> str:
    """Une fiche par repère et par motif de perçage."""
    tout = _sous_ensemble()
    groupes = {}
    for b in tout:
        if b.rep:
            groupes.setdefault((b.rep, signature(b)), []).append(b)
    return "".join(fiche(v[0], len(v)) for _, v in sorted(groupes.items(), key=lambda t: (t[0][0][0], int(t[0][0][1:]))))


# ------------------------------------------------------------------ calepinage
def tablette_svg(p, k: int) -> tuple[str, str]:
    """(titre, svg) d'un panneau du calepinage : « B » pour la barre de tasseau, « T » pour une tablette."""
    L, l = p.fmt["L"], p.fmt["l"]
    barre = l < 100
    o = [f'<rect class="tb" x="0" y="0" width="{L}" height="{l}"/>']
    for rep, x, y, a, b in p.poses():
        o.append(f'<rect class="pc m{rep[0]} {M.meuble(rep)}" x="{x}" y="{y}" width="{a}" height="{b}"/>')
        if barre:               # tasseau : repère et longueur sur une ligne
            o.append(f'<text class="pt ps" x="{x + a / 2}" y="{y + b / 2 + 13}" style="font-size:36px">{rep}, {a}</text>')
        elif b >= 60 and a >= 140:
            o.append(f'<text class="pt" x="{x + a / 2}" y="{y + b / 2 - 8}">{rep}</text>'
                     f'<text class="pd" x="{x + a / 2}" y="{y + b / 2 + 42}">{a} × {b}</text>')
        elif b >= 40:
            o.append(f'<text class="pt ps" x="{x + a / 2}" y="{y + b / 2 + 12}">{rep}</text>')
    nom = f'{"Barre" if barre else "Tablette"} {k}'
    titre = f'{"B" if barre else "T"}{k}, {L} × {l}, {p.taux() * 100:.0f} % utilisés'
    return titre, (f'<svg viewBox="-4 -4 {L + 8} {l + 8}" role="img" aria-label="{nom}, {L} × {l}">{"".join(o)}</svg>')


# ------------------------------------------------------------------ perçage type
def percage_type() -> str:
    """Coupe d'un vissage type de l'ossature : tasseau traversé (passage + fraisure), tasseau reçu (avant-trou), vis
    5 × 60. Cotes en mm, lues dans M.PERCAGE."""
    passage, avant = M.PERCAGE["vis60"]
    ep = M.DE * 10
    o = [f'<rect class="dg" x="0" y="0" width="60" height="{ep:g}"/>',
         f'<rect class="dg" x="0" y="{ep:g}" width="60" height="40" style="filter:brightness(.92)"/>',
         f'<path class="pvide" d="M27.5 0 L32.5 0 L32.5 {ep:g} L27.5 {ep:g} Z M25 0 L35 0 L32.5 3 L27.5 3 Z"/>',
         f'<path class="pvide" d="M28.5 {ep:g} L31.5 {ep:g} L31.5 {ep + 30:g} L28.5 {ep + 30:g} Z"/>',
         '<path class="pvis" d="M25.2 0 L34.8 0 L32 2.8 L32 56 L30 60 L28 56 L28 2.8 Z"/>']
    for y in range(6, 56, 4):
        o.append(f'<line class="pfil" x1="27.6" y1="{y}" x2="32.4" y2="{y + 2}"/>')
    for y, t in ((ep / 2, f"pièce traversée : {passage}"), (ep + 15, f"pièce reçue : avant-trou {avant}")):
        o.append(f'<text class="ptx" x="64" y="{y:g}">{escape(t)}</text>')
    o.append(f'<text class="ptx muted" x="64" y="{ep + 36:g}">ruban adhésif sur le foret = butée de profondeur</text>')
    return f'<svg viewBox="-4 -6 240 {ep + 50:g}" role="img" aria-label="Perçage type">{"".join(o)}</svg>'


# ------------------------------------------------------------------ pose au mur
def rect(x0, y0, x1, y1, cls, extra=""):
    return f'<rect class="{cls}" x="{f(x0)}" y="{f(y0)}" width="{f(x1 - x0)}" height="{f(y1 - y0)}"{extra}/>'


def cote_h(x0, x1, y, label=None, t=2):
    label = label or cm(abs(x1 - x0))
    return "".join([
        f'<line class="dim" x1="{f(x0)}" y1="{f(y)}" x2="{f(x1)}" y2="{f(y)}"/>',
        f'<line class="dim" x1="{f(x0)}" y1="{f(y - t)}" x2="{f(x0)}" y2="{f(y + t)}"/>',
        f'<line class="dim" x1="{f(x1)}" y1="{f(y - t)}" x2="{f(x1)}" y2="{f(y + t)}"/>',
        text((x0 + x1) / 2, y - 1.6, label, "dimt"),
    ])


def cote_v(y0, y1, x, label=None, t=2):
    label = label or cm(abs(y1 - y0))
    ym = (y0 + y1) / 2
    return "".join([
        f'<line class="dim" x1="{f(x)}" y1="{f(y0)}" x2="{f(x)}" y2="{f(y1)}"/>',
        f'<line class="dim" x1="{f(x - t)}" y1="{f(y0)}" x2="{f(x + t)}" y2="{f(y0)}"/>',
        f'<line class="dim" x1="{f(x - t)}" y1="{f(y1)}" x2="{f(x + t)}" y2="{f(y1)}"/>',
        text(x - 1.6, ym, label, "dimt", extra=f' transform="rotate(-90 {f(x - 1.6)} {f(ym)})"'),
    ])


def _motif(ident):
    return (f'<defs><pattern id="{ident}" width="6" height="6" patternUnits="userSpaceOnUse">'
            '<path d="M0 6 L6 0" style="stroke:var(--muted);stroke-width:.3"/></pattern></defs>')


def _cheville_z():
    return sorted({round(t["z"], 1) for t in M.TROUS if t["vis"] == "cheville"})


_CAISSON = ' style="fill:var(--cab);fill-opacity:.55;stroke:var(--ink);stroke-width:.5"'


def pose_de_face(label="Pose du caisson haut, de face") -> str:
    """Le mur du fond vu de la salle de bain : carrelage, chevilles, cales sur le plan. Cotes en cm."""
    ch, cr = M.CH, M.CARRELAGE
    tr = [t for t in M.TROUS if t["vis"] == "cheville"]
    zs = _cheville_z()
    cal = [(12, 22), (M.Y1 - 22, M.Y1 - 12)]
    o = [_motif("carreau-face"), rect(0, -M.H, M.Y1, 0, "", ' style="fill:var(--panel);stroke:var(--ink);stroke-width:.4"'),
         rect(0, -cr, M.Y1, 0, "", ' style="fill:url(#carreau-face);stroke:none"'),
         f'<line x1="0" y1="{-cr}" x2="{M.Y1}" y2="{-cr}" style="stroke:var(--ink);stroke-width:.4;stroke-dasharray:2 1.5"/>',
         text(M.Y1 - 2, -cr + 4, f"fin du carrelage {cr}", "lblx", "end"),
         rect(M.YM0, -M.Z_DESSUS, M.YM1, -M.Z_PLAN, "top"),
         text(M.Y1 / 2, -M.Z_PLAN + 5, "plan de travail", "lblx"),
         rect(ch["y0"], -ch["z1"], ch["y1"], -ch["z0"], "", _CAISSON),
         f'<line x1="{M.CENTRE}" y1="{-ch["z1"]}" x2="{M.CENTRE}" y2="{-ch["z0"]}" style="stroke:var(--ink);stroke-width:.3;stroke-dasharray:1 1"/>',
         text(M.Y1 / 2, -(ch["z0"] + 8), "caisson haut (vu à travers)", "lblx")]
    for y0, y1 in cal:
        o.append(rect(y0, -M.Z_HAUT, y1, -M.Z_DESSUS, "dg"))
    o.append(text(cal[0][1] + 2, -(M.Z_DESSUS + M.Z_HAUT) / 2, f"cale {cm(M.Z_HAUT - M.Z_DESSUS)}", "lblx", "start"))
    for t in tr:
        o.append(f'<circle cx="{t["y"]:.1f}" cy="{-t["z"]:.1f}" r="1.6" style="fill:var(--ink)"/>')
    o.append(cote_v(-cr, -zs[0], M.Y1 + 5, cm(zs[0] - cr)))
    o.append(cote_v(-zs[0], -zs[-1], M.Y1 + 5, cm(zs[-1] - zs[0])))
    o.append(cote_v(0, -cr, M.Y1 + 12, str(cr)))
    o.append(cote_v(-M.Z_DESSUS, -M.Z_HAUT, -6, cm(M.Z_HAUT - M.Z_DESSUS)))
    o.append(cote_h(0, 10, -zs[-1] - 4, "10"))
    o.append(cote_h(M.Y1 - 10, M.Y1, -zs[-1] - 4, "10"))
    o.append(text(1, 6, "nord", "lblx muted", "start"))
    o.append(text(M.Y1 - 1, 6, "sud", "lblx muted", "end"))
    return (f'<svg viewBox="-16 {-M.H - 6} {M.Y1 + 34} {M.H + 16}" role="img" aria-label="{escape(label)}">'
            f'{"".join(o)}</svg>')


def pose_en_coupe(label="Pose du caisson haut, en coupe") -> str:
    """Coupe par une cheville : la vis, la cale de l'épaisseur du carrelage, la cale sur le plan. Cotes en cm."""
    ch, cr = M.CH, M.CARRELAGE
    zs = _cheville_z()
    x0 = M.FACE - 6
    hx = M.X1 - M.F
    ep = M.EP_CARRELAGE
    # X1 = surface du carreau ; au-dessus du carrelage, le mur nu est ep plus loin
    o = [_motif("carreau-coupe"), rect(M.X1 + ep, -M.H, M.X1 + 8, 0, "w"),
         rect(M.X1, -cr, M.X1 + ep, 0, "", ' style="fill:url(#carreau-coupe);stroke:var(--ink);stroke-width:.3"'),
         text(M.X1 - 2, -cr + 6, "carrelage", "lblx", "end"),
         rect(M.FACE, -M.Z_DESSUS, M.PLAN_X1, -M.Z_PLAN, "top"),
         rect(ch["x0"], -ch["z1"], M.X1, -ch["z0"], "", _CAISSON),
         rect(hx, -ch["z1"], M.X1, -ch["z0"], "cab"),
         rect(ch["x0"] + 8, -M.Z_HAUT, ch["x0"] + 18, -M.Z_DESSUS, "dg"),
         text(ch["x0"] + 7, -(M.Z_DESSUS + M.Z_HAUT) / 2, "cale", "lblx", "end")]
    for z in zs:
        o.append(rect(M.X1, -(z + 2), M.X1 + ep, -(z - 2), "dg"))     # cale de l'épaisseur du carrelage
        o.append(f'<line x1="{hx - 1.5}" y1="{-z}" x2="{M.X1 + ep + 6}" y2="{-z}" style="stroke:var(--ink);stroke-width:.6"/>')
        o.append(rect(M.X1 + ep, -(z + 0.6), M.X1 + ep + 6, -(z - 0.6), "", ' style="fill:var(--tri);fill-opacity:.7"'))
    # étiquettes hors du caisson, à sa gauche, reliées par un trait fin à ce qu'elles nomment
    for y, t, cible in ((-zs[-1] - 3, f"vis 6 × {M.VIS_MUR['L']} tête fraisée", hx - 2),
                        (-zs[-1] + 8, f"cale de {cm(ep)} (épaisseur du carrelage)", M.X1 + ep / 2),
                        (-zs[0] + 5, "cheville Ø 8 dans le mur nu", M.X1 + ep + 3)):
        o.append(f'<line class="dim" x1="{f(ch["x0"] - 1.5)}" y1="{f(y - 1.2)}" x2="{f(cible)}" y2="{f(y - 1.2)}"/>')
        o.append(text(ch["x0"] - 2, y, t, "lblx", "end"))
    o.append(cote_h(ch["x0"], M.X1, -M.H - 3, "45"))
    o.append(cote_v(0, -cr, M.X1 + 13, str(cr)))
    o.append(cote_v(-cr, -zs[0], M.X1 + 13, cm(zs[0] - cr)))
    o.append(text(x0, 6, "pièce ←   → mur du fond", "lblx muted", "start"))
    # 2 de plus en haut que l'ancien dessin : la cote « 45 » y sortait du cadre
    # 40 de plus à gauche : les étiquettes sont à la gauche du caisson
    return (f'<svg viewBox="{x0 - 42} {-M.H - 10} {M.X1 + 62 - x0} {M.H + 20}" role="img" '
            f'aria-label="{escape(label)}">{"".join(o)}</svg>')


# ------------------------------------------------------------------ icônes de quincaillerie
ICONES = {
    "vis": '<path d="M4 12h10M14 9v6h3v-6z M6 10l1 4M8 10l1 4M10 10l1 4M12 10l1 4" />',
    "confirmat": '<path d="M3 12h11M14 8v8h4V8z M5 10l1 4M7 10l1 4M9 10l1 4M11 10l1 4"/>',
    "colle": '<path d="M8 6h8v14H8zM10 6V3h4v3M10 3l2-2 2 2"/>',
    "equerre": '<path d="M5 4v15h15v-4H9V4z"/>',
    "cheville": '<path d="M3 10h14l3 2-3 2H3zM6 10v4M9 10v4M12 10v4"/>',
    "piano": '<path d="M2 8h20v8H2zM2 12h20M6 8v8M10 8v8M14 8v8M18 8v8"/>',
    "compas": '<path d="M4 20L18 6M18 6l2 2M4 20l-2-2M10 14l3 3"/>',
    "poignee": '<path d="M4 14h16M6 14v-4h12v4"/>',
    "taquet": '<path d="M6 10h6v4H6zM12 9h6v6h-6z"/>',
    "rails": '<path d="M2 8h20M2 16h20M5 8v8M19 8v8"/>',
    "led": '<path d="M2 11h20v3H2zM6 12.5h0M10 12.5h0M14 12.5h0M18 12.5h0"/>',
    "silicone": '<path d="M4 8h12v8H4zM16 10h4l2 2-2 2h-4"/>',
    "tapis": '<path d="M3 9l9-4 9 4-9 4zM3 9v3l9 4 9-4V9"/>',
    "sac": '<path d="M4 7h16M7 7l2 13h6l2-13"/>',
    "chant": '<path d="M4 14a5 5 0 1 1 10 0a5 5 0 1 1-10 0M14 14h7M9 14h0"/>',
    "plate": '<path d="M4 4h6v10h10v6H4z"/>',
    "pinceau": '<path d="M9 3h6v8H9zM8 11h8l-1 4H9zM12 15v6"/>',
    "foret": '<path d="M3 12h4M7 10h4v4H7zM11 12h10M13 10l2 4M17 10l2 4"/>',
}
ICONE = {"vis40": "vis", "cheville": "cheville", "taquet": "taquet", "led": "led", "silicone": "silicone",
         "chant": "chant", "patins": "taquet", "colle": "colle", "fraise": "foret", "vernis": "pinceau"}


def icone(code: str) -> str:
    return f'<svg class="ico" viewBox="0 0 24 24" aria-hidden="true">{ICONES[ICONE[code]]}</svg>'


# ------------------------------------------------------------------ CSS
# Les règles dont toutes les classes figurent dans un dessin ou dans le HTML d'une vue sont gardées par
# commun/css_dessins.py, préfixées par la pièce. Couleurs en valeur : --dg #D29A68, --haut #9EC9E6, --tile #E9EEF0.
CSS = """
.tb{fill:#E9EEF0;stroke:var(--ink);stroke-width:3}
.pc{stroke:var(--ink);stroke-width:2;fill:var(--cab)}
.pc.mK{fill:var(--tall)}
.pc.mG{fill:#D29A68}
.pc.haut{fill:#9EC9E6}
.pt{font:700 64px var(--ui);fill:var(--ink);text-anchor:middle}
.pt.ps{font-size:40px}
.pd{font:400 40px var(--ui);fill:var(--muted);text-anchor:middle}
svg.face{display:block;width:100%;height:auto}
.fpc{fill:#9EC9E6;stroke:var(--ink);stroke-width:.12}
.fent{fill:var(--panel);stroke:var(--ink);stroke-width:.1;stroke-dasharray:.4 .3}
.fta{fill:var(--ink)}
.ftb{fill:var(--panel);stroke:var(--ink);stroke-width:.12}
.fdim{stroke:var(--muted);stroke-width:.06}
.ftx{fill:var(--ink);font-family:var(--ui);font-variant-numeric:tabular-nums}
.ftx.muted{fill:var(--muted)}
.dg{fill:#D29A68;fill-opacity:.75;stroke:var(--ink);stroke-width:.35}
.pvide{fill:var(--panel);stroke:var(--ink);stroke-width:.3}
.pvis{fill:#B9C2C8;stroke:var(--ink);stroke-width:.35}
.pfil{stroke:var(--ink);stroke-width:.3}
.ptx{font-size:5px;fill:var(--ink)}
.ptx.muted{fill:var(--muted)}
.cab{fill:var(--cab);stroke:var(--ink);stroke-width:.35}
.top{fill:var(--wood);fill-opacity:.55;stroke:var(--ink);stroke-width:.5}
.w{fill:var(--muted);fill-opacity:.55;stroke:var(--ink);stroke-width:.3}
.dim{stroke:var(--muted);stroke-width:.4;fill:none}
.dimt{fill:var(--muted);font-size:4.6px}
.lblx{font-size:3.5px}
.muted{fill:var(--muted)}
.percage svg{display:block;width:100%;max-width:640px;height:auto}
.vignettes{display:grid;grid-template-columns:repeat(auto-fill,minmax(150px,1fr));gap:10px;margin:8px 0}
.vignette{border:1px solid var(--line);border-radius:4px;background:var(--panel);padding:8px;display:flex;flex-direction:column}
.vignette .cdes{height:96px;display:flex;align-items:center;justify-content:center}
.vignette .cdes svg{max-width:100%;max-height:96px;width:auto;height:96px}
.cpied{display:flex;justify-content:space-between;align-items:baseline;margin-top:6px}
.crep{font:700 18px var(--ui)}
.cq{font:600 15px var(--ui);font-variant-numeric:tabular-nums}
.cnom{font-size:14px;line-height:1.3}
.cdim{font-size:13px;color:var(--muted);font-variant-numeric:tabular-nums}
.besoin{margin:6px 0 4px}
.pieces,.quinc{display:flex;flex-wrap:wrap;gap:6px;margin:6px 0}
.besoin .piece{border:1px solid var(--line);border-radius:999px;padding:1px 10px;background:var(--panel);font-size:14px}
.hw{display:flex;align-items:center;gap:6px;font-size:14px;border:1px solid var(--line);border-radius:4px;padding:3px 10px 3px 4px;background:var(--panel)}
.hw .ico{width:26px;height:26px}
.hw b{white-space:nowrap}
.hw span{color:var(--muted)}
div.ops{margin:8px 0 0}
div.op{display:grid;grid-template-columns:40px minmax(0,1fr);gap:8px;padding:8px 0;border-top:1px solid var(--line)}
div.op:first-child{border-top:none}
.opn{font:700 15px var(--ui);color:var(--muted);font-variant-numeric:tabular-nums}
.opc p{margin:0 0 6px}
.ctrl{border-left:4px solid var(--water);padding:3px 10px;background:var(--panel)}
.att{border-left:4px solid var(--tri);padding:3px 10px;background:var(--panel)}
.ctrl b,.att b{font:700 14px var(--ui);margin-right:6px}
details.perc{margin:10px 0 0}
details.perc summary{cursor:pointer;font-weight:600}
.fiches{display:grid;grid-template-columns:repeat(auto-fill,minmax(300px,1fr));gap:10px;margin:8px 0}
.fiche{background:var(--panel);border:1px solid var(--line);border-radius:4px;padding:8px 10px}
.ftete{display:flex;flex-wrap:wrap;gap:8px;align-items:baseline;font-size:15px}
.ftete .cq{margin-left:auto}
.ftete .dims{font-size:13px;color:var(--muted);font-variant-numeric:tabular-nums}
.fface{margin:6px 0}
.fnom{font-size:13px;color:var(--muted)}
.fliens{margin:4px 0 0;padding-left:18px;font-size:14px;color:var(--muted)}
.lg{display:inline-block;width:10px;height:10px;border-radius:50%;vertical-align:-1px;border:1px solid var(--ink)}
.lg.fta{background:var(--ink)}
.lg.ftb{background:var(--panel)}
.lg.fent{border-radius:2px;border-style:dashed}
.pistes{padding-left:20px}
.pistes li{margin:6px 0}
"""
CSS_DOCUMENT = "\n".join((DC.CSS, iso.CSS, CSS))
