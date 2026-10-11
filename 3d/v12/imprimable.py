# Génère cuisine-v12-imprimable.html : version imprimable en noir et blanc, à l'échelle 1:20, sur A4 paysage.
#
#   python3 3d/v12/imprimable.py    (aussi lancé par plan.py, donc par `just v12`)
#
# Trois feuilles : la pièce meublée, la pièce vide, les meubles à part (à découper pour essayer d'autres positions).
# Tout est projeté depuis modele.py, comme le plan de la page.

import os
import sys
from html import escape

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import modele as M  # noqa: E402
from plan import ROOT, cote_h, cote_v, f, pts, rect, text  # noqa: E402

OUT = os.path.join(ROOT, "cuisine-v12-imprimable.html")
MM = 0.5                         # 1:20 → 1 cm réel = 0,5 mm sur le papier
VUE = (-50, -50, 552, 342)       # cadre des feuilles de la pièce (x, y, largeur, hauteur), en cm
ECART = 8                        # espace entre deux meubles à découper (4 mm sur le papier)


def svg(x, y, w, h, corps, label):
    return (f'<svg viewBox="{f(x)} {f(y)} {f(w)} {f(h)}" width="{f(w * MM)}mm" height="{f(h * MM)}mm" '
            f'role="img" aria-label="{escape(label)}">{corps}</svg>')


def echelle(x, y):
    """Barre d'échelle de 1 m, graduée tous les 10 cm, pour vérifier l'impression à 100 %."""
    o = [f'<rect class="eb" x="{f(x + k * 10)}" y="{f(y)}" width="10" height="3"/>' for k in range(0, 10, 2)]
    o.append(f'<rect class="ec" x="{f(x)}" y="{f(y)}" width="100" height="3"/>')
    o += [text(x + k, y + 9, f"{k}" if k else "0", "et") for k in (0, 50, 100)]
    o.append(text(x + 104, y + 3, "1 m = 5 cm à 1:20", "et", "start"))
    return "".join(o)


# ------------------------------------------------------------------ pièce vide
def piece_vide():
    o = [f'<defs><pattern id="hach" width="4" height="4" patternUnits="userSpaceOnUse" patternTransform="rotate(45)">'
         f'<line x1="0" y1="0" x2="0" y2="4" class="hl"/></pattern></defs>']
    o.append(f'<polygon class="wc" points="{pts(M.WC)}"/>')
    o.append(text(438, 185, "WC", "lbl"))
    # limite parquet / ciment
    o.append('<line class="sol" x1="325" y1="0" x2="325" y2="240"/>')
    o.append(text(160, 112, "cuisine", "zone"))
    o.append(text(400, 64, "cellier", "zone"))
    for b in M.ENVELOPPE:
        if b.role == "mur":
            o.append(rect(b.x0, b.y0, b.x1, b.y1, "mur"))
        elif b.role == "cloison":
            o.append(rect(b.x0, b.y0, b.x1, b.y1, "cloison"))
        elif b.role == "allege":
            o.append(rect(b.x0, b.y0, b.x1, b.y1, "fen"))
            o.append(f'<line class="vitre" x1="{f(b.x0)}" y1="{f(b.y0)}" x2="{f(b.x0)}" y2="{f(b.y1)}"/>')
            o.append(f'<line class="vitre" x1="{f(b.x1)}" y1="{f(b.y0)}" x2="{f(b.x1)}" y2="{f(b.y1)}"/>')
            o.append(f'<line class="vitre" x1="{f((b.x0 + b.x1) / 2)}" y1="{f(b.y0)}" '
                     f'x2="{f((b.x0 + b.x1) / 2)}" y2="{f(b.y1)}"/>')
        elif b.role == "porte":
            o.append(rect(b.x0, b.y0, b.x1, b.y1, "porte"))
    en = M.ENTREE
    o.append(text((en["x0"] + en["x1"]) / 2, 271, "entrée", "lbls"))
    o.append(text(sum(en["poche"]) / 2, 238, "galandage", "lblx"))
    o.append(text(M.PLIANTE["rail"] - 4, (M.PLIANTE["y0"] + M.PLIANTE["y1"]) / 2, "porte cellier", "lblx", "end"))
    bl = M.BALLON
    o.append(f'<circle class="ballon" cx="{f(bl.cx)}" cy="{f(bl.cy)}" r="{f(bl.r)}"/>')
    o.append(text(bl.cx, bl.cy - 6, "ballon (h 90)", "lblx"))
    o.append(f'<circle class="chute" cx="{f(M.CHUTE[0])}" cy="{f(M.CHUTE[1])}" r="4.5"/>')
    o.append(text(M.CHUTE[0], M.CHUTE[1] + 12, "chute", "lblx"))
    # cotes de la pièce
    fe = M.FENETRE
    o.append(cote_h(0, 434, -40))
    o.append(cote_h(en["x0"], en["x1"], 282, f'baie {f(en["x1"] - en["x0"])}'))
    o.append(cote_h(0, 320, -24, "320 (cloison du cellier)"))
    o.append(cote_v(0, fe["y0"], -26))
    o.append(cote_v(fe["y0"], fe["y1"], -26, f'fenêtre {f(fe["y1"] - fe["y0"])}'))
    o.append(cote_v(fe["y1"], 252, -26))
    o.append(cote_v(0, 252, -36))
    o.append(cote_v(81, 240, 300, f"{240 - 81}"))
    o.append('<g transform="translate(485 -34)"><path class="nord" d="M0 -9 L5 4 L0 1 L-5 4 Z"/>'
             + text(0, 13, "N", "lblb") + "</g>")
    return "".join(o)


# ------------------------------------------------------------------ meubles
def meubles():
    """Meubles posés au sol (et meubles hauts, au-dessus), à leur position du modèle :
    [(nom, sous-titre, x0, y0, x1, y1, détails(dx, dy) → SVG, classe)]."""
    plan = next(b for b in M.MEUBLES if b.role == "plan")
    bas = [b for b in M.MEUBLES if b.role == "caisson" and b.y0 == 0]
    r = []

    def dedans(roles, x0, x1, y0, y1):
        return [b for b in M.MEUBLES if b.role in roles and x0 <= (b.x0 + b.x1) / 2 <= x1 and y0 <= (b.y0 + b.y1) / 2 <= y1]

    for k, b in enumerate(bas):
        x0 = plan.x0 if k == 0 else b.x0     # B1 porte le fileur du mur ouest
        nom, _, equip = b.etiq.partition(" ")
        sous = [s for s in dedans(("plaque", "cuve", "egouttoir"), x0, b.x1, 0, plan.y1)]
        if any(s.role == "plaque" for s in sous):
            equip = "induction" + (" · four" if equip == "four" else "")
        if any(s.role == "cuve" for s in sous):
            equip = "évier" + (" · " + equip if equip else "")
        r.append((nom, equip, x0, 0, b.x1, plan.y1, sous, "m"))
    for b in M.MEUBLES:
        if b.role == "colonne":
            nom, _, equip = b.etiq.partition(" ")
            r.append((nom, equip, M.COL_X, b.y0, b.x1, b.y1, [], "m"))
    ba = M.BANQ
    r.append(("Banquette", "coffre · 2 tiroirs", ba["x0"], ba["y0"], ba["x1"], ba["y1"],
              [M.Bloc("dossier", "", ba["x0"], ba["x1"], ba["y1"] - 5, ba["y1"], 0, 0)], "m"))
    t = M.TABLE
    r.append(("Table", "pied central", t["x0"], t["y0"], t["x1"], t["y1"], [], "m table"))
    for nom, rv in (("Rayonnage", M.RAYON_NORD), ("Rayonnage", M.RAYON_SUD)):
        r.append((nom, f'P{rv["y1"] - rv["y0"]}', rv["x0"], rv["y0"], rv["x1"], rv["y1"], [], "m"))
    for b in M.MEUBLES:
        if b.role == "caisson_haut":
            r.append((b.etiq, "haut", b.x0, b.y0, b.x1, b.y1 + M.FACADE, [], "m haut"))
    return r


def chaise(x0, y0):
    """Chaise ajoutée à la planche de découpe (pas dans le projet) : 42 × 42, dossier au nord."""
    c = M.CHAISE
    return ("Chaise", f'{c["l"]} × {c["p"]}', x0, y0, x0 + c["l"], y0 + c["p"],
            [M.Bloc("dossier", "", x0, x0 + c["l"], y0, y0 + 4, 0, 0)], "m")


def dessin(m, dx=0, dy=0):
    """Un meuble, décalé de (dx, dy) : contour (trait de coupe), détails, nom et dimensions."""
    nom, sous, x0, y0, x1, y1, details, cls = m
    x0, y0, x1, y1 = x0 + dx, y0 + dy, x1 + dx, y1 + dy
    w, h = x1 - x0, y1 - y0
    o = []
    if "table" in cls:
        o.append(f'<rect class="{cls}" x="{f(x0)}" y="{f(y0)}" width="{f(w)}" height="{f(h)}" rx="12"/>')
    else:
        o.append(rect(x0, y0, x1, y1, cls))
    for d in details:
        if isinstance(d, M.Cyl):
            o.append(f'<circle class="det" cx="{f(d.cx + dx)}" cy="{f(d.cy + dy)}" r="{f(d.r)}"/>')
        else:
            o.append(rect(d.x0 + dx, d.y0 + dy, d.x1 + dx, d.y1 + dy, "plaque" if d.role == "plaque" else "det"))
    cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
    dim = f"{f(w)} × {f(h)}"
    if w < 30:   # meuble étroit : texte tourné
        o.append(text(cx + 2, cy, f"{nom} · {dim}", "lbln", extra=f' transform="rotate(-90 {f(cx + 2)} {f(cy)})"'))
    elif h < 25:  # meuble peu profond : une ligne
        o.append(text(cx, cy + 2, f"{nom} · {dim}", "lbld"))
    else:
        ty = cy - (2 if sous else -2)
        o.append(text(cx, ty, nom, "lbln"))
        if sous:
            o.append(text(cx, ty + 6.5, sous, "lbld"))
        o.append(text(cx, ty + (13 if sous else 6.5), dim, "lbld"))
    return "".join(o)


def piece_meublee():
    o = [piece_vide()]
    ms = meubles()
    for m in sorted(ms, key=lambda m: "haut" in m[7]):   # meubles hauts par-dessus, en tireté
        if "haut" in m[7]:
            o.append(rect(m[2], m[3], m[4], m[5], "haut"))
        else:
            o.append(dessin(m))
    bas = [m for m in ms if m[0].startswith("B")]
    for m in bas:
        o.append(cote_h(m[2], m[4], -8))
    return "".join(o)


def planche():
    """Meubles à part, rangés par lignes (plus haut d'abord), séparés de ECART : à découper au trait plein."""
    ms = meubles() + [chaise(0, 0)]
    larg = VUE[2] - 2 * ECART
    ordre = sorted(ms, key=lambda m: -(m[5] - m[3]))
    o, x, y, hl = [], 0, 0, 0
    for m in ordre:
        w, h = m[4] - m[2], m[5] - m[3]
        if x and x + w > larg:
            x, y, hl = 0, y + hl + ECART, 0
        o.append(dessin(m, x - m[2], y - m[3]))
        x, hl = x + w + ECART, max(hl, h)
    return "".join(o), y + hl


CSS = """
:root{color-scheme:light}
*{box-sizing:border-box}
html,body{margin:0}
body{background:#E6E6E6;color:#000;font-family:Archivo,system-ui,-apple-system,"Segoe UI",Roboto,sans-serif}
.barre{position:sticky;top:0;z-index:2;display:flex;flex-wrap:wrap;align-items:center;gap:10px;padding:8px 16px;background:#fff;border-bottom:1px solid #999;font:12px "JetBrains Mono",ui-monospace,Menlo,monospace}
.barre a{color:#000;font-weight:600;text-decoration:none;margin-right:8px}
.barre button{font:inherit;color:#fff;background:#000;border:1px solid #000;border-radius:6px;padding:4px 12px;cursor:pointer}
.barre .aide{color:#444}
.feuilles{padding:16px;overflow-x:auto}
.feuille{width:297mm;height:210mm;padding:8mm;margin:0 auto 16px;background:#fff;box-shadow:0 1px 4px rgba(0,0,0,.25);display:flex;flex-direction:column;overflow:hidden}
.ent{display:flex;justify-content:space-between;align-items:baseline;border-bottom:.3mm solid #000;padding-bottom:1.5mm;margin-bottom:2mm}
.ent h1{font-size:15pt;margin:0;font-weight:800}
.ent span{font:8pt "JetBrains Mono",ui-monospace,monospace}
.feuille svg{display:block;margin:auto}
.pied{font-size:7.5pt;color:#000;margin-top:auto}
svg text{font-family:Archivo,system-ui,sans-serif;fill:#000}
.mur{fill:#000}
.cloison{fill:url(#hach);stroke:#000;stroke-width:.6}
.hl{stroke:#000;stroke-width:.6}
.fen{fill:#fff;stroke:#000;stroke-width:.5}.vitre{stroke:#000;stroke-width:.4}
.porte{fill:#fff;stroke:#000;stroke-width:.6}
.wc{fill:#D9D9D9}
.sol{stroke:#000;stroke-width:.4;stroke-dasharray:2 2}
.zone{font-size:9px;fill:#9A9A9A;text-anchor:middle;letter-spacing:.1em;text-transform:uppercase}
.ballon{fill:none;stroke:#000;stroke-width:.5;stroke-dasharray:3 2}
.chute{fill:#fff;stroke:#000;stroke-width:1}
.nord{fill:#000}
.m{fill:#fff;stroke:#000;stroke-width:.8}
.haut{fill:none;stroke:#000;stroke-width:.6;stroke-dasharray:3 2}
.m.haut{stroke-dasharray:3 2}
.det{fill:none;stroke:#000;stroke-width:.4}
.plaque{fill:#BFBFBF;stroke:#000;stroke-width:.4}
.dim{stroke:#000;stroke-width:.4;fill:none}
.dimt{font-family:"JetBrains Mono",ui-monospace,monospace !important;font-size:6px}
.lbl{font-size:7.5px}.lbls{font-size:6.5px}.lblx{font-size:4.5px}.lblb{font-size:9px;font-weight:700}
.lbln{font-size:6px;font-weight:700}.lbld{font-size:4.5px}
.eb{fill:#000}.ec{fill:none;stroke:#000;stroke-width:.4}.et{font-size:5px;font-family:"JetBrains Mono",monospace !important}
@page{size:A4 landscape;margin:0}
@media print{
  body{background:#fff}
  .barre{display:none}
  .feuilles{padding:0;overflow:visible}
  .feuille{margin:0;box-shadow:none;break-after:page}
  .feuille:last-child{break-after:auto}
}
"""


def feuille(titre, sous, figure, pied):
    return (f'<section class="feuille"><div class="ent"><h1>{escape(titre)}</h1><span>{escape(sous)}</span></div>'
            f'{figure}<p class="pied">{pied}</p></section>')


def page():
    x, y, w, h = VUE
    sous = f"Cuisine {M.VERSION} · échelle 1:20 · cm"
    bar = echelle(330, 276)
    meublee = svg(x, y, w, h, piece_meublee() + bar, "Plan de la cuisine meublée, 1:20")
    vide = svg(x, y, w, h, piece_vide() + bar, "Plan de la pièce vide, 1:20")
    corps, hp = planche()
    hp += 24
    decoupe = svg(-ECART, -ECART, w, hp, corps + echelle(0, hp - 20), "Meubles à découper, 1:20")
    pied = ("Imprimer en A4 paysage à 100 % (taille réelle, sans ajustement à la page) ; la barre d'échelle doit "
            "mesurer 5 cm. ")
    return f"""<!doctype html>
<html lang="fr">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Cuisine imprimable</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Archivo:wght@400;700;800&family=JetBrains+Mono:wght@400;600&display=swap" rel="stylesheet">
<style>{CSS}</style>
</head>
<body>
<div class="barre"><a href="cuisine-v12.html">← Cuisine V12</a><button type="button" onclick="print()">Imprimer</button>
<span class="aide">A4 paysage, échelle 100 % : 3 feuilles</span></div>
<main class="feuilles">
{feuille("Cuisine meublée", sous, meublee,
         pied + "Meubles hauts en tireté (au-dessus des meubles bas) ; zone grisée : WC ; tireté vertical : limite parquet / ciment.")}
{feuille("Pièce vide", sous, vide,
         pied + "Murs en noir, cloisons neuves hachurées (doublage du galandage, retour de cloison du cellier), "
         "fenêtre et porte du cellier fermées. Poser les meubles découpés de la feuille 3.")}
{feuille("Meubles à découper", sous, decoupe,
         pied + "Découper au trait plein. Meubles bas avec leur plan de travail (P62), colonnes avec façade (P60), "
         "meubles hauts en tireté (P35, au-dessus du plan), table, banquette, rayonnages du cellier et une chaise 42 × 42.")}
</main>
</body>
</html>
"""


def ecrire():
    with open(OUT, "w", encoding="utf-8") as fh:
        fh.write(page())
    print(OUT)


if __name__ == "__main__":
    ecrire()
