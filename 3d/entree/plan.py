# Génère entree-amenagement.html (plan vu de dessus, coupes, vues 3D) depuis modele.py.
#
#   python3 3d/entree/plan.py            (just entree)
#
# Le plan et les coupes sont des projections des volumes du modèle : rien n'est dessiné à la main.

import math
import os
import sys
from html import escape

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import modele as M  # noqa: E402

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
ANCRES = open(os.path.join(ROOT, "3d", "ancres.js"), encoding="utf-8").read()   # ancres communes des pages à sommaire

OUT = os.path.join(ROOT, "entree-amenagement.html")
CLE = "entree"            # préfixe des préférences mémorisées (localStorage)
DOSSIER_3D = "entree-3d"

COUPE_A = 60     # y, regard vers le nord : banc et tableau électrique
COUPE_B = 40     # x, regard vers l'est : meuble à chaussures, angle, flanc de la penderie
COUPE_C = 130    # y, regard vers le sud : penderie, angle, porte d'entrée au fond


def virg(v, n=1):
    return f"{v:.{n}f}".replace(".", ",")


def f(v):
    return f"{round(v, 1):g}"


def rect(x0, y0, x1, y1, cls, rx=0):
    r = f' rx="{f(rx)}"' if rx else ""
    return f'<rect class="{cls}" x="{f(x0)}" y="{f(y0)}" width="{f(x1 - x0)}" height="{f(y1 - y0)}"{r}/>'


def text(x, y, s, cls="lbl", anchor="middle", extra=""):
    return f'<text class="{cls}" x="{f(x)}" y="{f(y)}" text-anchor="{anchor}"{extra}>{escape(s)}</text>'


def rot(x, y):
    return f' transform="rotate(-90 {f(x)} {f(y)})"'


def cote_h(x0, x1, y, label=None, t=3):
    label = label or f(abs(x1 - x0))
    return "".join([
        f'<line class="dim" x1="{f(x0)}" y1="{f(y)}" x2="{f(x1)}" y2="{f(y)}"/>',
        f'<line class="dim" x1="{f(x0)}" y1="{f(y - t)}" x2="{f(x0)}" y2="{f(y + t)}"/>',
        f'<line class="dim" x1="{f(x1)}" y1="{f(y - t)}" x2="{f(x1)}" y2="{f(y + t)}"/>',
        text((x0 + x1) / 2, y - 2.5, label, "dimt"),
    ])


def cote_v(y0, y1, x, label=None, t=3):
    label = label or f(abs(y1 - y0))
    ym = (y0 + y1) / 2
    return "".join([
        f'<line class="dim" x1="{f(x)}" y1="{f(y0)}" x2="{f(x)}" y2="{f(y1)}"/>',
        f'<line class="dim" x1="{f(x - t)}" y1="{f(y0)}" x2="{f(x + t)}" y2="{f(y0)}"/>',
        f'<line class="dim" x1="{f(x - t)}" y1="{f(y1)}" x2="{f(x + t)}" y2="{f(y1)}"/>',
        text(x - 2.5, ym, label, "dimt", extra=rot(x - 2.5, ym)),
    ])


def degage(a, b, label=None):
    """Passage libre entre deux points (trait vert), valeur au milieu."""
    d = math.dist(a, b)
    xm, ym = (a[0] + b[0]) / 2, (a[1] + b[1]) / 2
    vertical = abs(b[1] - a[1]) > abs(b[0] - a[0])
    t = text(xm - 3, ym, label or f"{d:.0f}", "passt", extra=rot(xm - 3, ym)) if vertical else text(xm, ym - 3, label or f"{d:.0f}", "passt")
    return (f'<line class="pass" x1="{f(a[0])}" y1="{f(a[1])}" x2="{f(b[0])}" y2="{f(b[1])}"/>'
            + "".join(f'<circle class="passm" cx="{f(p[0])}" cy="{f(p[1])}" r="1.3"/>' for p in (a, b)) + t)


def coin_arrondi(x0, x1, y0, y1, r, cls):
    """Rectangle vu de dessus, coin nord-ouest arrondi (quart de cercle de rayon r)."""
    return (f'<path class="{cls}" d="M{f(x1)} {f(y0)} L{f(x1)} {f(y1)} L{f(x0)} {f(y1)} L{f(x0)} {f(y0 + r)} '
            f'A{f(r)} {f(r)} 0 0 1 {f(x0 + r)} {f(y0)} Z"/>')


# ------------------------------------------------------------------ portes (plan)
def _porte(p):
    """Vantail ouvert à 90°, arc et zone de débattement ; porte coulissante ; passage sans porte."""
    a, b, face, mur = p["a"], p["b"], p["face"], p["mur"]
    piece_face = face + (M.EP if mur in "se" else -M.EP)
    o = []
    if p["type"] == "passage":
        x = face + M.EP / 2 + 11
        o.append(text(x, (a + b) / 2, "passage sans porte", "lblx muted", extra=rot(x, (a + b) / 2)))
        return o
    if p["type"] == "coulissante":
        o.append(rect(a, face - M.EP - 4, b, face - M.EP, "sleafc"))
        o.append(text((a + b) / 2, face - M.EP - 8, "porte coulissante côté cuisine", "lblx muted"))
        return o
    perp = face if p["vers"] == "couloir" else piece_face
    into = {"n": 1, "s": -1, "e": -1, "o": 1}[mur] * (1 if p["vers"] == "couloir" else -1)
    g, autre = (a, b) if p["gond"] == "a" else (b, a)
    L = b - a
    pt = (lambda along, d: (along, d)) if mur in "ns" else (lambda along, d: (d, along))
    H, P, Q = pt(g, perp), pt(autre, perp), pt(g, perp + into * L)
    cross = (P[0] - H[0]) * (Q[1] - H[1]) - (P[1] - H[1]) * (Q[0] - H[0])
    sw = 1 if cross > 0 else 0
    arc = f'A{f(L)} {f(L)} 0 0 {sw} {f(Q[0])} {f(Q[1])}'
    o.append(f'<path class="doorzone" d="M{f(H[0])} {f(H[1])} L{f(P[0])} {f(P[1])} {arc} Z"/>')
    o.append(f'<path class="doorarc" d="M{f(P[0])} {f(P[1])} {arc}"/>')
    o.append(f'<line class="doorleaf" x1="{f(H[0])}" y1="{f(H[1])}" x2="{f(Q[0])}" y2="{f(Q[1])}"/>')
    return o


def _jambages():
    """Traits fins aux bords des ouvertures, dans l'épaisseur de la cloison."""
    o = []
    for p in M.PORTES:
        d0, d1 = (p["face"], p["face"] + M.EP) if p["mur"] in "se" else (p["face"] - M.EP, p["face"])
        for s in (p["a"], p["b"]):
            if p["mur"] in "ns":
                o.append(f'<line class="app" x1="{f(s)}" y1="{f(d0)}" x2="{f(s)}" y2="{f(d1)}"/>')
            else:
                o.append(f'<line class="app" x1="{f(d0)}" y1="{f(s)}" x2="{f(d1)}" y2="{f(s)}"/>')
    return o


# ------------------------------------------------------------------ plan vu de dessus
def plan_svg():
    b, c, an, pe, mi = M.BANC, M.CHAUSSURES, M.ANGLE, M.PENDERIE, M.MIROIR
    o = []
    # pièces voisines
    for x0, y0, x1, y1, nom, tx, ty in ((-140, -120, 90, -10, "Cuisine", -25, -60), (150, -120, 274, -10, "WC", 212, -60),
                                        (274, -120, 434, 94, "Salon", 354, -40), (364, 104, 434, 264, "Chambre", 399, 240),
                                        (120, 218, 364, 384, "Salle de bain", 242, 300),
                                        (-140, -10, -10, 384, "Pièce ouest", -75, 230)):
        o.append(rect(x0, y0, x1, y1, "room"))
        o.append(text(tx, ty, nom, "roomt"))
    o.append(text(40, 405, "Palier", "roomt"))
    pts = " ".join(f"{f(x)},{f(y)}" for x, y in M.SOL)
    ca = M.CARRELAGE["taille"]
    o.append(f'<defs><pattern id="carreaux" width="{ca}" height="{ca}" patternUnits="userSpaceOnUse">'
             f'<rect class="carreau" width="{ca}" height="{ca}"/></pattern></defs>')
    o.append(f'<polygon class="floorbg" points="{pts}"/><polygon fill="url(#carreaux)" points="{pts}"/>')
    for m in M.MURS:
        o.append(rect(m.x0, m.y0, m.x1, m.y1, "w"))
    o += _jambages()
    for p in M.PORTES:
        o += _porte(p)
    o.append(text(39, 392, "porte d’entrée", "lbls muted"))
    # ① banc et tableau électrique
    o.append(rect(M.TABLEAU["x0"], -6, M.TABLEAU["x1"], 0, "tech"))
    o.append(rect(b["x0"], b["y0"], b["x1"], b["y1"], "cab"))
    xm = (b["x0"] + b["x1"]) / 2
    o.append(text(xm, 18.5, f'① Banc {b["x1"] - b["x0"]} × {b["y1"] - b["y0"]} · h {b["z1"]}', "lbls"))
    o.append(text(xm, 26.5, "sous le tableau électrique", "lbls"))
    # angle arrondi, meuble à chaussures, miroir, patères
    o.append(coin_arrondi(an["x0"], an["x1"], an["y0"], an["y1"], an["r"], "cab"))
    o.append(rect(c["x0"], c["y0"], c["x1"], c["y1"], "cab"))
    for y0, _ in c["modules"][1:]:
        o.append(f'<line class="app" x1="{c["x0"]}" y1="{y0}" x2="{c["x1"]}" y2="{y0}"/>')
    o.append(f'<line class="app" x1="{an["x0"]}" y1="{an["y1"]}" x2="{an["x1"]}" y2="{an["y1"]}"/>')
    o.append(rect(106.5, mi["y0"], 110, mi["y1"], "mirror"))
    ym = (c["y0"] + c["y1"]) / 2
    o.append(text(97.5, ym, f'② Chaussures {c["y1"] - c["y0"]} × {c["x1"] - c["x0"]} · h {c["z1"]}', "lbls", extra=rot(97.5, ym)))
    ymi = (mi["y0"] + mi["y1"]) / 2
    o.append(text(127, ymi, "← miroir au-dessus du meuble", "lblx muted", "start"))
    for y in M.PATERES:
        o.append(f'<circle class="hook" cx="108" cy="{y}" r="1.6"/>')
    o.append(text(79, 196, "angle arrondi", "lblx muted", "end"))
    o.append(text(79, 203, f'étagères h {c["z1"]}', "lblx muted", "end"))
    # ③ penderie : deux portes de 42, débattement en tireté
    o.append(rect(pe["x0"], pe["y0"], pe["x1"], pe["y1"], "tall"))
    xp = (pe["x0"] + pe["x1"]) / 2
    lp = (pe["x1"] - pe["x0"]) / 2
    o.append(f'<line class="app" x1="{f(xp)}" y1="{pe["y0"]}" x2="{f(xp)}" y2="{pe["y1"]}"/>')
    for x in (pe["x0"] + lp / 2, pe["x1"] - lp / 2):
        o.append(f'<line class="inner" x1="{f(x)}" y1="{pe["y0"] + 4}" x2="{f(x)}" y2="{pe["y1"] - 4}"/>')
    o.append(f'<path class="swing" d="M{pe["x0"]} {pe["y0"]} A{f(lp)} {f(lp)} 0 0 1 {f(xp)} {f(pe["y0"] - lp)}"/>')
    o.append(f'<path class="swing" d="M{pe["x1"]} {pe["y0"]} A{f(lp)} {f(lp)} 0 0 0 {f(xp)} {f(pe["y0"] - lp)}"/>')
    o.append(text(xp, 187, f'③ Penderie {pe["x1"] - pe["x0"]} × {pe["y1"] - pe["y0"]}', "lblx"))
    o.append(text(xp, 194, f"h {M.H} · 2 tringles extractibles", "lblx"))
    # passages, cotes, traits de coupe
    for d in M.PASSAGES:
        o.append(degage(d["a"], d["b"], d["label"]))
    o.append(cote_h(0, 264, -28))
    o.append(cote_h(0, 110, 424))
    o.append(cote_v(0, 374, -48))
    o.append(cote_h(110, 354, 232))
    o.append(f'<line class="sec" x1="-6" y1="{COUPE_A}" x2="270" y2="{COUPE_A}"/>')
    o.append(text(-8, COUPE_A + 4, "A", "sect", "end"))
    o.append(f'<line class="sec" x1="{COUPE_B}" y1="-6" x2="{COUPE_B}" y2="380"/>')
    o.append(text(COUPE_B + 7, 368, "B", "sect", "start"))
    o.append(f'<line class="sec" x1="-6" y1="{COUPE_C}" x2="360" y2="{COUPE_C}"/>')
    o.append(text(-8, COUPE_C + 4, "C", "sect", "end"))
    return f'<svg viewBox="-150 -130 595 560" role="img" aria-label="Plan de l\'entrée aménagée">{"".join(o)}</svg>'


# ------------------------------------------------------------------ coupes
COUPE_CLS = {"mur": ("bgwall", "w"), "linteau": ("wallv", "w"), "porte": ("porte", "portec"), "tableau": ("tech", "tech"),
             "banc": ("cab", "cabc"), "angle": ("cab", "cabc"), "caisson": ("cab", "cabc"), "plateau": ("tbl", "tbl"),
             "tall": ("tall", "tallc"), "socle": ("dark", "dark"), "miroir": ("mirror", "mirror"),
             "applique": ("lamp", "lamp"), "patere": ("dark", "dark"), "facade": ("fac", "fac"), "facade_p": ("facp", "facp")}

# (axe coupé, sens du regard, miroir de l'axe horizontal)
REGARDS = {"nord": ("y", -1, False), "sud": ("y", 1, True), "est": ("x", 1, False), "ouest": ("x", -1, True)}
VERS = {"nord": "le nord", "sud": "le sud", "est": "l'est", "ouest": "l'ouest"}


def uv(b, axe):
    return (b.x0, b.x1, b.y0, b.y1) if axe == "y" else (b.y0, b.y1, b.x0, b.x1)


def coupe_svg(cut, regard, umin, umax, hauteurs, extra=None):
    axe, sens, miroir = REGARDS[regard]
    X = (lambda u: umin + umax - u) if miroir else (lambda u: u)
    vus = []
    for b in M.ENVELOPPE + M.MEUBLES:
        u0, u1, d0, d1 = uv(b, axe)
        if (d1 > cut if sens > 0 else d0 < cut) and u1 > umin and u0 < umax:
            vus.append(b)
    vus.sort(key=lambda b: (uv(b, axe)[2] < cut < uv(b, axe)[3], -uv(b, axe)[2] if sens > 0 else uv(b, axe)[3]))
    o, etiq = [], {}
    for b in vus:
        u0, u1, d0, d1 = uv(b, axe)
        coupe = d0 < cut < d1
        u, v = sorted((X(max(u0, umin)), X(min(u1, umax))))
        o.append(rect(u, -b.z1, v, -b.z0, COUPE_CLS[b.role][1 if coupe else 0]))
        if b.etiq and v - u > 8:
            xm = (u + v) / 2
            etiq[(round(xm), round(b.z0 + b.z1))] = text(xm, -(b.z0 + b.z1) / 2 + 3, b.etiq, "lblb")
    o += etiq.values()
    if extra:
        o += extra(X)
    o.append(f'<line class="floorl" x1="{f(umin)}" y1="0" x2="{f(umax)}" y2="0"/>')
    o.append(f'<line class="ceil" x1="{f(umin)}" y1="{-M.H}" x2="{f(umax)}" y2="{-M.H}"/>')
    zs = [0] + hauteurs + [M.H]
    for z0, z1 in zip(zs, zs[1:]):
        o.append(cote_v(-z0, -z1, umin - 12))
    o.append(cote_v(0, -M.H, umin - 28))
    return (f'<svg viewBox="{f(umin - 44)} -270 {f(umax - umin + 70)} 300" role="img" '
            f'aria-label="Coupe à {axe} {f(cut)}, regard vers {VERS[regard]}">{"".join(o)}</svg>')


def portes_vues(X, mur, extra_txt=None):
    """Nom de la pièce sur chaque porte du mur vue de face."""
    r = []
    for p in M.PORTES:
        if p["mur"] == mur and p["type"] != "passage":
            u = X((p["a"] + p["b"]) / 2)
            r.append(text(u, -100, p["piece"].lower(), "lbls muted"))
    return r


def coupe_a():
    b, t = M.BANC, M.TABLEAU

    def cotes(X):
        u0, u1 = sorted((X(b["x0"]), X(b["x1"])))
        return portes_vues(X, "n") + [
            text((X(t["x0"]) + X(t["x1"])) / 2, -t["z1"] - 6, "position et taille à relever", "lblx muted"),
            cote_h(u0, u1, 12, f'banc {b["x1"] - b["x0"]}'),
            cote_h(87, 191, 22, "trumeau 104"),
        ]

    return coupe_svg(COUPE_A, "nord", -20, 284, [b["z1"], t["z0"], t["z1"], M.H_PORTE], extra=cotes)


def coupe_b():
    c, an, pe, mi = M.CHAUSSURES, M.ANGLE, M.PENDERIE, M.MIROIR

    def cotes(X):
        r = [cote_h(an["y0"], an["y1"], 12, f'angle {an["y1"] - an["y0"]}'),
             cote_h(c["y0"], c["y1"], 12, f'chaussures {c["y1"] - c["y0"]}'),
             text((mi["y0"] + mi["y1"]) / 2, -(mi["z0"] + mi["z1"]) / 2, f'miroir {mi["y1"] - mi["y0"]} × {mi["z1"] - mi["z0"]}', "lbls"),
             text(M.PATERES[0] + 8, -173, "patères", "lblx muted"),
             text(M.APPLIQUE["y"] + 10, -M.APPLIQUE["z"] + 2, "applique", "lblx muted", "start"),
             text((c["y0"] + c["y1"]) / 2, -c["z1"] - 6, f'plateau vide-poche h {c["z1"] + c["plateau"]}', "lblx muted")]
        for z in an["etageres"]:
            r.append(f'<line class="app" x1="{an["y0"]}" y1="{-z}" x2="{an["y1"]}" y2="{-z}"/>')
        return r

    return coupe_svg(COUPE_B, "est", -20, 394, [M.BANC["z1"], c["z1"], mi["z0"], M.H_PORTE, mi["z1"]], extra=cotes)


def coupe_c():
    pe = M.PENDERIE

    def cotes(X):
        u0, u1 = sorted((X(pe["x0"]), X(pe["x1"])))
        xm = (u0 + u1) / 2
        r = [f'<line class="inner" x1="{f(u0 + 3)}" y1="{-pe["etagere"]}" x2="{f(u1 - 3)}" y2="{-pe["etagere"]}"/>',
             text(xm, -pe["etagere"] - 3, f'étagère h {pe["etagere"]}', "lblx muted"),
             text(xm, -pe["tringle"] + 8, f'2 tringles extractibles h {pe["tringle"]}', "lblx muted"),
             cote_h(u0, u1, 12, f'penderie {pe["x1"] - pe["x0"]}'),
             cote_h(*sorted((X(M.ANGLE["x0"]), X(M.ANGLE["x1"]))), 12, "25")]
        for x in (pe["x0"] + 21, pe["x1"] - 21):
            r.append(f'<line class="inner" x1="{f(X(x))}" y1="{-pe["tringle"]}" x2="{f(X(x))}" y2="{-pe["tringle"] + 4}"/>')
        r += portes_vues(X, "s")
        return r

    return coupe_svg(COUPE_C, "sud", -20, 374, [pe["socle"], M.CHAUSSURES["z1"], pe["tringle"], pe["etagere"]], extra=cotes)


# ------------------------------------------------------------------ page
CSS = """
:root{
  --paper:#F7F8F6; --ink:#1D2A33; --muted:#5E6B73; --line:#C9D0D4; --wood:#B07A45;
  --water:#2F7FB5; --tri:#C8412C; --flow:#2E8B57; --panel:#FFFFFF; --cab:#ECE6DA; --tall:#D8CFBD;
  --tech:#E1E6E9; --glass:#CFE4F2; color-scheme:light;
}
@media (prefers-color-scheme: dark){
  :root:not([data-theme="light"]){
    --paper:#141A1F; --ink:#E4EAED; --muted:#9AA7AE; --line:#34414A; --wood:#C9925A;
    --water:#5AA8DE; --tri:#E8664F; --flow:#4CB97A; --panel:#1B2329; --cab:#2A3338; --tall:#394449;
    --tech:#26303A; --glass:#1F3A4E; color-scheme:dark;
  }
}
:root[data-theme="dark"]{
  --paper:#141A1F; --ink:#E4EAED; --muted:#9AA7AE; --line:#34414A; --wood:#C9925A;
  --water:#5AA8DE; --tri:#E8664F; --flow:#4CB97A; --panel:#1B2329; --cab:#2A3338; --tall:#394449;
  --tech:#26303A; --glass:#1F3A4E; color-scheme:dark;
}
*{box-sizing:border-box}
html,body{margin:0}
body{background:var(--paper);color:var(--ink);font-family:Archivo,system-ui,-apple-system,"Segoe UI",Roboto,sans-serif;line-height:1.55;font-size:16px}
.wrap{max-width:1120px;margin:0 auto;padding:28px 16px 64px}
.kicker{font-family:"JetBrains Mono",ui-monospace,Menlo,monospace;font-size:12px;letter-spacing:.08em;text-transform:uppercase;color:var(--muted)}
h1{font-size:clamp(28px,5vw,44px);line-height:1.08;margin:6px 0 12px;font-weight:800;letter-spacing:-.01em}
h2{font-size:22px;margin:44px 0 10px;font-weight:700}
h3{font-size:16px;margin:0 0 6px}
.pitch{font-size:18px;max-width:780px}
.stats{display:grid;grid-template-columns:repeat(auto-fit,minmax(170px,1fr));gap:12px;margin:22px 0 8px}
.stat{background:var(--panel);border:1px solid var(--line);border-radius:10px;padding:12px 14px}
.stat b{display:block;font-family:"JetBrains Mono",ui-monospace,monospace;font-size:24px;font-weight:600}
.stat span{font-size:13px;color:var(--muted)}
.fig{background:var(--panel);border:1px solid var(--line);border-radius:12px;padding:12px;margin:14px 0}
.scroll{overflow-x:auto}.scroll svg{display:block;width:100%;height:auto}
.scroll svg.plan{min-width:640px;max-width:900px;margin:0 auto}.scroll svg.coupe{min-width:480px;max-width:720px;margin:0 auto}
.cap{font-size:13px;color:var(--muted);margin:8px 4px 2px}
.note{font-size:13px;color:var(--muted)}
.grid2{display:grid;grid-template-columns:repeat(auto-fit,minmax(min(100%,300px),1fr));gap:16px}
.card{background:var(--panel);border:1px solid var(--line);border-radius:10px;padding:14px 16px}
.card p{margin:4px 0}
.legend{display:flex;flex-wrap:wrap;gap:8px 18px;font-size:13px;margin:10px 4px}
.legend span{display:inline-flex;align-items:center;gap:6px}
.legend svg{width:26px;height:14px;flex:none}
table{border-collapse:collapse;width:100%;font-size:14px}
th,td{text-align:left;padding:7px 8px;border-bottom:1px solid var(--line);vertical-align:top}
.mono{font-family:"JetBrains Mono",ui-monospace,monospace;white-space:nowrap}
ul.pistes{padding-left:20px;max-width:860px}ul.pistes li{margin:6px 0}
.rendu img{display:block;width:100%;height:auto;border-radius:8px}
.rendu figure{margin:0}
svg text{font-family:Archivo,system-ui,sans-serif;fill:var(--ink)}
.room{fill:var(--line);fill-opacity:.18}
.roomt{fill:var(--muted);font-size:9px;font-weight:600;text-anchor:middle}
.floorbg{fill:#D9D2C6;fill-opacity:.35}
.carreau{fill:none;stroke:#B5AC9C;stroke-width:.4;stroke-opacity:.7}
.w{fill:var(--ink)}
.bgwall{fill:var(--line);fill-opacity:.35}
.wallv{fill:#D5DADD;stroke:var(--muted);stroke-width:.5}
.app{stroke:var(--ink);stroke-width:.8;fill:none}
.cab{fill:var(--cab);stroke:var(--ink);stroke-width:.7}
.cabc{fill:var(--tall);stroke:var(--ink);stroke-width:1.2}
.tall{fill:var(--tall);stroke:var(--ink);stroke-width:.8}
.tallc{fill:var(--tall);stroke:var(--ink);stroke-width:1.4}
.fac{fill:var(--wood);fill-opacity:.35;stroke:var(--ink);stroke-width:.5}
.facp{fill:var(--panel);stroke:var(--ink);stroke-width:.6}
.tbl{fill:var(--wood);fill-opacity:.6;stroke:var(--ink);stroke-width:.6}
.tech{fill:var(--tech);stroke:var(--ink);stroke-width:.7;stroke-dasharray:3 2}
.dark{fill:var(--ink)}
.mirror{fill:var(--glass);stroke:var(--ink);stroke-width:.6}
.lamp{fill:#E8B44A;fill-opacity:.55;stroke:var(--ink);stroke-width:.6}
.hook{fill:var(--ink)}
.porte{fill:var(--panel);stroke:var(--ink);stroke-width:.6}
.portec{fill:var(--panel);stroke:var(--ink);stroke-width:1}
.inner{fill:none;stroke:var(--muted);stroke-width:.6;stroke-dasharray:3 2}
.doorzone{fill:var(--tri);fill-opacity:.06;stroke:none}
.doorarc{fill:none;stroke:var(--ink);stroke-width:.8}
.doorleaf{stroke:var(--ink);stroke-width:3}
.swing{fill:none;stroke:var(--muted);stroke-width:.6;stroke-dasharray:2 2}
.sleafc{fill:none;stroke:var(--ink);stroke-width:.8;stroke-dasharray:3 2}
.pass{stroke:var(--flow);stroke-width:.9}.passm{fill:var(--flow)}
.passt{fill:var(--flow);font-family:"JetBrains Mono",ui-monospace,monospace !important;font-size:7px;font-weight:600}
.dim{stroke:var(--muted);stroke-width:.6;fill:none}
.dimt{fill:var(--muted);font-family:"JetBrains Mono",ui-monospace,monospace !important;font-size:8px}
.lbl{font-size:7.5px}.lbls{font-size:6.5px}.lblx{font-size:5px}.lblb{font-size:8px;font-weight:700}
.muted{fill:var(--muted)}
.sec{stroke:var(--tri);stroke-opacity:.35;stroke-width:.9;stroke-dasharray:10 3 2 3;fill:none}
.sect{fill:var(--tri);fill-opacity:.6;font-weight:800;font-size:11px}
.floorl{stroke:var(--ink);stroke-width:2}
.ceil{stroke:var(--muted);stroke-width:1;stroke-dasharray:6 4}
body:not(.explications) .cap{display:none}
body:not(.changements) section[id^="changements"]{display:none}
.vbar{position:sticky;top:0;z-index:5;display:flex;flex-wrap:wrap;align-items:center;gap:6px;padding:8px 16px;background:var(--paper);border-bottom:1px solid var(--line);font-family:"JetBrains Mono",ui-monospace,monospace;font-size:12px}
.vbar button{font:inherit;color:var(--ink);background:var(--panel);border:1px solid var(--line);border-radius:6px;padding:4px 10px;cursor:pointer}
.vbar button[aria-pressed="true"]{background:var(--ink);color:var(--paper);border-color:var(--ink)}
.vbar .back{color:var(--ink);text-decoration:none;font-weight:600;margin-right:14px}
.vbar .back:hover{text-decoration:underline}
.vbar .expl{margin-left:auto}
h2{scroll-margin-top:60px}
.toc{display:none}
@media (min-width:1100px){
.toc{display:block;position:fixed;left:0;top:42px;z-index:4;font-size:13px}
.toc .tbtn{font:600 12px "JetBrains Mono",ui-monospace,monospace;color:var(--ink);background:var(--panel);border:1px solid var(--line);border-radius:0 6px 6px 0;border-left:none;padding:6px 10px;cursor:pointer}
.toc ol{display:none;list-style:none;margin:0;padding:6px 0 24px}
body.toc-on .toc{bottom:0;width:232px;overflow-y:auto;background:var(--paper);border-right:1px solid var(--line);padding:10px 0 0}
body.toc-on .toc .tbtn{border:none;background:none;padding:2px 16px 8px;color:var(--muted);text-transform:uppercase;letter-spacing:.08em}
body.toc-on .toc ol{display:block}
.toc a{display:block;padding:5px 16px;color:var(--muted);text-decoration:none;border-left:3px solid transparent;line-height:1.35}
.toc a:hover{color:var(--ink);background:var(--panel)}
.toc a.on{color:var(--ink);border-left-color:var(--ink);font-weight:600}
body.toc-on .wrap{margin-left:max(248px,calc((100vw - 1120px) / 2))}
}
@media (max-width:480px){ body{font-size:15px} .stat b{font-size:21px} }
"""


def legende():
    items = [('<rect x="0" y="0" width="26" height="14" class="tall"/>', "Meuble toute hauteur"),
             ('<rect x="0" y="0" width="26" height="14" class="cab"/>', "Meuble bas, banc"),
             ('<rect x="1" y="1" width="24" height="12" class="tech"/>', "Tableau électrique encastré"),
             ('<rect x="1" y="5" width="24" height="4" class="mirror"/>', "Miroir"),
             ('<path d="M1 13 L1 1 A12 12 0 0 1 13 13Z" class="doorzone"/><path d="M1 1 A12 12 0 0 1 13 13" class="doorarc"/>',
              "Débattement des portes"),
             ('<line x1="1" y1="7" x2="25" y2="7" class="pass"/>', "Passage libre (cm)"),
             ('<rect x="0" y="0" width="26" height="14" class="room"/>', "Pièce voisine")]
    return '<div class="legend">' + "".join(f'<span><svg viewBox="0 0 26 14">{s}</svg>{t}</span>' for s, t in items) + "</div>"


def galerie():
    """Rendus 3D présents dans entree-3d/ (just entree-rendu)."""
    figs = []
    for v, titre in M.RENDUS:
        chemin = os.path.join(ROOT, DOSSIER_3D, f"{v}.jpg")
        if os.path.exists(chemin):
            figs.append(f'<div class="fig rendu"><figure><img src="{DOSSIER_3D}/{v}.jpg?v={int(os.path.getmtime(chemin))}" '
                        f'alt="{escape(titre)}" loading="lazy"></figure><p class="note">{escape(titre)} · modèle {M.VERSION}. '
                        f'Murs du premier plan et plafond retirés ; portes fermées.</p></div>')
    return f'<h2>Vues 3D</h2>\n{"".join(figs)}\n' if figs else ""


def contenu():
    b, c, an, pe, mi = M.BANC, M.CHAUSSURES, M.ANGLE, M.PENDERIE, M.MIROIR
    lignes = "".join(f'<tr><td class="mono">{v}</td><td class="mono">{dt}</td><td>{escape(x)}</td></tr>'
                     for v, dt, x in M.CHANGEMENTS)
    lb, pb = b["x1"] - b["x0"], b["y1"] - b["y0"]
    lc, pc = c["y1"] - c["y0"], c["x1"] - c["x0"]
    lp, pp = pe["x1"] - pe["x0"], pe["y1"] - pe["y0"]
    banc_pend = pe["y0"] - b["y1"]
    return f"""<div class="kicker">Entrée · {M.VERSION}</div>
<h1>Aménagement de l'entrée</h1>
<p class="pitch">Le couloir ({virg(M.SURFACE)} m²) dessert cinq portes et le passage du salon : il faut ranger sans gêner. Un banc sous le tableau électrique, un meuble à chaussures étroit avec miroir dans la branche d'entrée, relié par un angle arrondi à une penderie face à la salle de bain.</p>
<div class="stats"><div class="stat"><b>{lp} × {pp}</b><span>penderie toute hauteur</span></div><div class="stat"><b>≈ {M.PAIRES} paires</b><span>meuble à chaussures</span></div><div class="stat"><b>{c["x0"]} cm</b><span>passage le plus étroit</span></div><div class="stat"><b>{virg(M.SURFACE)} m²</b><span>surface du couloir</span></div></div>

<h2>Plan</h2>
<div class="fig"><div class="scroll">{plan_svg().replace("<svg ", '<svg class="plan" ', 1)}</div>
<p class="cap">Plan vu de dessus, 1 unité = 1 cm ; nord en haut. Le vantail de la porte d'entrée ouvert à 90° vient en butée contre le meuble à chaussures (②) : prévoir un butoir de sol. Avec {pp} cm de profondeur, la penderie reste au sud du vantail de la pièce ouest ouvert à 90° (il s'arrête à y 160, la penderie commence à y {pe["y0"]}). Traits A, B, C : coupes ci-dessous.</p>
{legende()}</div>

{galerie()}<h2>Coupe A-A · mur nord</h2>
<div class="fig"><div class="scroll">{coupe_a().replace("<svg ", '<svg class="coupe" ', 1)}</div>
<p class="cap">Coupe à y {COUPE_A}, regard vers le nord : l'ouest est à gauche. Banc posé sous le tableau électrique encastré, entre les portes de la cuisine (coulissante, côté cuisine) et du WC. Tableau dessiné au milieu du trumeau, de {M.TABLEAU["z0"]} à {M.TABLEAU["z1"]} : position et taille à relever. À droite, le linteau du passage vers le salon.</p></div>

<h2>Coupe B-B · mur de la salle de bain</h2>
<div class="fig"><div class="scroll">{coupe_b().replace("<svg ", '<svg class="coupe" ', 1)}</div>
<p class="cap">Coupe à x {COUPE_B}, regard vers l'est : le nord est à gauche. Le banc au fond à gauche, puis le flanc de la penderie, l'angle arrondi à étagères ouvertes, le meuble à chaussures (deux modules de {c["modules"][0][1] - c["modules"][0][0]}, deux abattants chacun) et son plateau vide-poche à {c["z1"] + c["plateau"]} ; au-dessus, deux patères, le miroir {mi["y1"] - mi["y0"]} × {mi["z1"] - mi["z0"]} et l'applique. Coupées : la porte coulissante de la cuisine à gauche, la porte d'entrée à droite.</p></div>

<h2>Coupe C-C · penderie</h2>
<div class="fig"><div class="scroll">{coupe_c().replace("<svg ", '<svg class="coupe" ', 1)}</div>
<p class="cap">Coupe à y {COUPE_C}, regard vers le sud : l'est est à gauche. Penderie {lp} × {pp} toute hauteur sur socle de {pe["socle"]}, deux portes de {lp // 2} ; derrière chaque porte, une tringle extractible à {pe["tringle"]} (cintres de face), étagère à {pe["etagere"]}. À droite, l'angle arrondi devant le meuble à chaussures, la porte d'entrée au fond. Coupées : la porte de la chambre à gauche, celle de la pièce ouest à droite.</p></div>

<h2>Principe</h2>
<div class="grid2">
<div class="card"><h3>① Banc sous le tableau électrique</h3><p>Un banc de {lb} × {pb} à {b["z1"]} de haut, posé (pas fixé dans la zone du tableau), dessous ouvert. Le tableau reste visible et à portée de main au-dessus : rien n'est rangé devant, ce que la NF C 15-100 interdit. On s'y assoit pour se chausser, face au meuble à chaussures.</p></div>
<div class="card"><h3>② Meuble à chaussures dans la branche d'entrée</h3><p>Le long de la cloison de la salle de bain, {lc} cm de long et {pc} de profondeur seulement pour garder {c["x0"]} cm de passage. Quatre abattants (environ {M.PAIRES} paires), plateau vide-poche pour les clés, deux patères, miroir {mi["y1"] - mi["y0"]} × {mi["z1"] - mi["z0"]} et applique au-dessus. Il sert aussi de butée à la porte d'entrée ouverte.</p></div>
<div class="card"><h3>③ Penderie et angle arrondi</h3><p>Contre la face nord de la salle de bain : une penderie de {lp} × {pp} toute hauteur, deux portes de {lp // 2}. À {pp} cm, les cintres ne tiennent pas en travers : derrière chaque porte, une tringle extractible à {pe["tringle"]} (cintres de face, environ {pe["manteaux"]} manteaux par tringle), étagère à {pe["etagere"]}. Le meuble à chaussures se prolonge jusqu'au nu de la penderie et s'y termine par un quart de cercle ouvert de rayon {an["r"]}, à {c["z1"]} de haut (étagères pour les clés et le courrier) : pas d'arête dans le passage. {banc_pend} cm restent entre le banc et la penderie fermée.</p></div>
<div class="card"><h3>Porte de la pièce ouest</h3><p>Elle ouvre dans le couloir. Ouverte à 90°, son vantail s'arrête à y 160 ; la penderie commence à y {pe["y0"]}. Elle peut donc s'ouvrir normalement, sans gêner le passage.</p></div>
</div>

<h2>Matériaux</h2>
<div class="fig"><table><tbody>
<tr><td>Sol</td><td>Carrelage {M.CARRELAGE["nom"]}, pose droite, joints fins.</td></tr>
<tr><td>Murs</td><td>Blanc chaud, comme la cuisine et le salon ({M.MUR_COULEUR}).</td></tr>
<tr><td>Meubles</td><td>Proposition des rendus : banc, meuble à chaussures, angle et plateau en chêne miel (comme le salon) ; penderie en blanc chaud, de la couleur des murs, pour qu'elle se fasse oublier. À choisir.</td></tr>
</tbody></table></div>

<h2>Points à vérifier</h2>
<ul class="pistes">
<li><b>Tableau électrique</b> : encastré entre la cuisine et le WC (indiqué par le client) ; sa position et sa hauteur sont à relever. Si ses commandes les plus basses sont sous 1 m, le banc gêne l'accès : le raccourcir ou le décaler.</li>
<li><b>Sens de la porte d'entrée</b> : sur le relevé, les paumelles sont à droite (côté salle de bain) et la porte ouvre vers l'intérieur. Si elles sont à gauche, le vantail se range contre le mur ouest.</li>
<li><b>Portes du mur nord</b> : la gauche est celle de la cuisine (coulissante côté cuisine), la droite celle du WC, d'après le plan du salon.</li>
<li><b>Hauteur sous plafond</b> : {M.H}, reprise de la salle de bain ; le salon a été relevé à 254,5.</li>
<li><b>Passage du salon</b> : {M.PORTES[2]["b"] - M.PORTES[2]["a"]} de large sur ce relevé, 82 sur le relevé du salon (V4.12) : à remesurer.</li>
</ul>

<p class="note">Repère : x vers l'est depuis le mur ouest du couloir, y vers le sud depuis son mur nord, z depuis le sol fini, en cm. Source : <span class="mono">3d/entree/modele.py</span> ; page : <span class="mono">3d/entree/plan.py</span> (<span class="mono">just entree</span>) ; vues 3D : <span class="mono">3d/entree/rendu.py</span> (<span class="mono">just entree-rendu</span>).</p>

<section id="changements">
<h2>Changements</h2>
<div class="scroll"><table><thead><tr><th>Version</th><th>Date</th><th>Changements</th></tr></thead>
<tbody>{lignes}</tbody></table></div>
</section>
"""


def page():
    barre = ('<div class="vbar"><a class="back" href="index.html">← Plans</a>'
             '<button type="button" class="expl" aria-pressed="false">Explications</button>'
             '<button type="button" class="chg" aria-pressed="false">Changements</button></div>')
    return f"""<!doctype html>
<html lang="fr">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Aménagement de l'entrée</title>
<link rel="icon" href="favicon.svg" type="image/svg+xml">
<link rel="apple-touch-icon" href="apple-touch-icon.png">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Archivo:wght@400;500;700;800&family=JetBrains+Mono:wght@400;600&display=swap" rel="stylesheet">
<style>{CSS}</style>
</head>
<body>
{barre}
<nav class="toc" aria-label="Sommaire"><button type="button" class="tbtn" aria-expanded="true">Sommaire</button><ol></ol></nav>
<main class="wrap">
{contenu()}
</main>
<script>{ANCRES}</script>
<script>
(function () {{
  function garde(k, v) {{ try {{ localStorage.setItem("{CLE}-" + k, v); }} catch (e) {{}} }}
  function lit(k) {{ try {{ return localStorage.getItem("{CLE}-" + k); }} catch (e) {{ return null; }} }}
  function bascule(sel, cls) {{
    var b = document.querySelector(sel);
    function pose(on) {{ document.body.classList.toggle(cls, on); b.setAttribute("aria-pressed", on); garde(cls, on ? "1" : ""); }}
    b.addEventListener("click", function () {{ pose(b.getAttribute("aria-pressed") !== "true"); }});
    pose(lit(cls) === "1");
  }}
  bascule(".vbar .expl", "explications");
  bascule(".vbar .chg", "changements");
  // sommaire (ordinateur) : les titres h2, repliable, titre courant surligné
  var toc = document.querySelector(".toc"), tol = toc.querySelector("ol"), tb = toc.querySelector(".tbtn");
  var hs = Array.prototype.slice.call(document.querySelectorAll("main h2"));
  function ouvert(on) {{
    document.body.classList.toggle("toc-on", on);
    tb.setAttribute("aria-expanded", on);
    tb.textContent = on ? "« Sommaire" : "Sommaire »";
    garde("toc", on ? "1" : "0");
  }}
  tb.addEventListener("click", function () {{ ouvert(!document.body.classList.contains("toc-on")); }});
  ouvert(lit("toc") !== "0");
  function suivre() {{
    var haut = document.querySelector(".vbar").offsetHeight;
    toc.style.top = haut + "px";
    var k = -1;
    hs.forEach(function (h, i) {{ if (h.offsetParent && h.getBoundingClientRect().top < haut + 80) k = i; }});
    tol.querySelectorAll("a").forEach(function (a, i) {{ a.classList.toggle("on", i === k); }});
  }}
  hs.forEach(function (h) {{
    var li = document.createElement("li"), a = document.createElement("a");
    a.href = "#" + h.id; a.textContent = h.textContent.trim();
    a.addEventListener("click", function (e) {{
      e.preventDefault();
      if (h.closest('section[id^="changements"]')) document.querySelector(".vbar .chg").getAttribute("aria-pressed") === "true" || document.querySelector(".vbar .chg").click();
      history.replaceState(null, "", "#" + h.id);
      h.scrollIntoView({{behavior: "smooth"}});
    }});
    li.appendChild(a); tol.appendChild(li);
  }});
  var attente = false;
  window.addEventListener("scroll", function () {{
    if (!attente) {{ attente = true; requestAnimationFrame(function () {{ attente = false; suivre(); }}); }}
  }}, {{passive: true}});
  window.addEventListener("resize", suivre);
  suivre();
}})();
</script>
</body>
</html>
"""


if __name__ == "__main__":
    with open(OUT, "w", encoding="utf-8") as fh:
        fh.write(page())
    print("Page :", OUT)
