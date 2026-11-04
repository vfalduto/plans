# Aides communes aux trois pages du meuble linge SDB (débit, tablettes, CSS, en-tête) ; les pages sont générées par pages.py.
#
#   python3 3d/sdb/plan.py            (just sdb)
#   python3 3d/sdb/plan.py --figer    (just sdb-figer : fige la version courante)
#
# Le plan et les coupes sont des projections des pièces du modèle : rien n'est dessiné à la main.

import os
import sys
from collections import Counter
from html import escape

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import modele as M  # noqa: E402
import calepinage as CAL  # noqa: E402

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
ANCRES = open(os.path.join(ROOT, "3d", "ancres.js"), encoding="utf-8").read()   # ancres communes des pages à sommaire







def virg(v, n=1):
    return f"{v:.{n}f}".replace(".", ",").replace(",0", "") if n else f"{v:.0f}"


def f(v):
    return f"{round(v, 2):g}"


def cm(v):
    """Cote en cm affichée : 1 décimale au plus, virgule française."""
    return f"{round(v, 1):g}".replace(".", ",")


def rect(x0, y0, x1, y1, cls, extra=""):
    return f'<rect class="{cls}" x="{f(x0)}" y="{f(y0)}" width="{f(x1 - x0)}" height="{f(y1 - y0)}"{extra}/>'


def poly(pts, cls):
    return f'<polygon class="{cls}" points="{" ".join(f"{f(u)},{f(v)}" for u, v in pts)}"/>'


def text(x, y, s, cls="lbl", anchor="middle", extra=""):
    return f'<text class="{cls}" x="{f(x)}" y="{f(y)}" text-anchor="{anchor}"{extra}>{escape(s)}</text>'


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




























# ------------------------------------------------------------------ débit
def debit():
    """Une ligne par repère : quantité, longueur × largeur × épaisseur en mm (version d ; la version g a les mêmes pièces)."""
    lignes = {}
    for b in M.PIECES:
        if not b.rep:
            continue
        dims = tuple(sorted((b.x1 - b.x0, b.y1 - b.y0, b.z1 - b.z0), reverse=True))
        lignes.setdefault(b.rep, []).append(dims)
    cle = lambda r: (r[0], int(r[1:]))
    r = []
    for rep in sorted(lignes, key=cle):
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


def table_debit(meuble, descriptions=None):
    """Débit d'un des deux meubles ("bas" ou "haut"). descriptions : usage propre à la page, par matériau (sinon celui de M.MATERIAUX)."""
    o, mat = [], None
    surf = Counter()
    lignes = [p for p in debit() if M.meuble(p["rep"]) == meuble]
    for p in lignes:
        if p["mat"] != mat:
            mat = p["mat"]
            n, d, _ = M.MATERIAUX[mat]
            d = (descriptions or {}).get(mat, d)
            o.append(f'<tr class="mat"><td colspan="6"><span class="sw m{mat}"></span>{mat} — {escape(n)} '
                     f'<span class="note">· {escape(d)}</span></td></tr>')
        if mat not in "EG":
            surf[mat] += p["q"] * p["L"] * p["l"] / 1e6
        sec = (f'Ø {p["l"]}' if p["rep"] == "E4" else f'{p["l"]} × {p["e"]}') if mat in "EG" else f'{p["l"]}'
        o.append(f'<tr class="{meuble}"><td class="mono">{p["rep"]}</td><td>{escape(p["nom"])}</td><td class="num">{p["q"]}</td>'
                 f'<td class="num">{p["L"]}</td><td class="num">{sec}</td><td class="u">{escape(p["u"])}</td></tr>')
    tot = " · ".join(f'{m} {virg(v, 2)} m²' for m, v in sorted(surf.items()))
    ml = sum(p["q"] * p["L"] for p in lignes if p["mat"] == "G") / 1000
    if ml:
        tot += f" · G {virg(ml, 2)} m linéaires"
    return (f'<div class="scroll"><table class="debit"><thead><tr><th>Rep.</th><th>Pièce</th><th class="num">Qté</th>'
            f'<th class="num">Long.</th><th class="num">Larg.</th><th>Usinages, remarques</th></tr></thead>'
            f'<tbody>{"".join(o)}</tbody></table></div><p class="note">Cotes en mm, pièces finies. Surfaces nettes : {tot}.</p>')


# ------------------------------------------------------------------ achats (calepinage + liste de courses)
def tablette_svg(p, k):
    L, l = p.fmt["L"], p.fmt["l"]
    o = [f'<rect class="tb" x="0" y="0" width="{L}" height="{l}"/>']
    for rep, x, y, a, b in p.poses():
        o.append(f'<rect class="pc m{rep[0]} {M.meuble(rep)}" x="{x}" y="{y}" width="{a}" height="{b}"/>')
        if l < 100:             # tasseau : repère et longueur sur une ligne
            o.append(f'<text class="pt ps" x="{x + a / 2}" y="{y + b / 2 + 13}" style="font-size:36px">{rep} · {a}</text>')
        elif b >= 60 and a >= 140:
            o.append(f'<text class="pt" x="{x + a / 2}" y="{y + b / 2 - 8}">{rep}</text>'
                     f'<text class="pd" x="{x + a / 2}" y="{y + b / 2 + 42}">{a} × {b}</text>')
        elif b >= 40:
            o.append(f'<text class="pt ps" x="{x + a / 2}" y="{y + b / 2 + 12}">{rep}</text>')
    return (f'<div class="tab"><div class="tabt"><b>{"B" if l < 100 else "T"}{k}</b> · {L} × {l} · {p.taux():.0%} utilisés</div>'
            f'<svg viewBox="-4 -4 {L + 8} {l + 8}" role="img" aria-label="Tablette {k}, {L} × {l}">{"".join(o)}</svg></div>')


def code_meuble(code):
    """Meuble d'un article de quincaillerie : celui des étapes où il sert (consommables : commun)."""
    if code in M.CONSOMMABLES:
        return "commun"
    etapes = {n for n, e in enumerate(M.ETAPES) if code in e[-1]}
    return "haut" if etapes and etapes <= set(M.MEUBLE_HAUT_ETAPES) else "bas"


def ligne_panneaux(panneaux):
    """Lignes d'achat (nom, réf., quantité, prix, stock) pour une liste de panneaux du calepinage."""
    r = []
    for stock, fmts in M.PANNEAUX.items():
        for fmt in fmts:
            n = sum(1 for p in panneaux if p.fmt["ref"] == fmt["ref"])   # panneaux copiés : comparer les réf.
            nom = fmt["nom"] + (f" — {fmt['magasin']}" if "magasin" in fmt else "")   # V5.24 : hors Weldom
            if n and "lot" in fmt:          # vendu par lots
                r.append((nom, fmt["ref"], -(-n // fmt["lot"]), fmt["prix_lot"], fmt["stock"]))
            elif n:
                r.append((nom, fmt["ref"], n, fmt["prix"], fmt["stock"]))
    return r


def liste(lignes, titre):
    total = sum(n * px for _, _, n, px, _ in lignes)
    corps = "".join(
        f'<tr><td>{escape(nom)}</td><td class="mono">{ref}</td><td class="num">{n}</td><td class="num">{euros(px)}</td>'
        f'<td class="num">{euros(n * px)}</td><td class="num">{"—" if st is None else st}</td></tr>'
        for nom, ref, n, px, st in lignes)
    return total, (f'<div class="scroll"><table class="debit"><thead><tr><th>Article (Weldom sauf mention)</th><th>Réf.</th>'
                   f'<th class="num">Qté</th><th class="num">Prix</th><th class="num">Total</th><th class="num">Stock</th>'
                   f'</tr></thead><tbody>{corps}</tbody><tfoot><tr><td colspan="4"><b>{escape(titre)}</b></td>'
                   f'<td class="num"><b>{euros(total)}</b></td><td></td></tr></tfoot></table></div>')


_CAL = []


def calepinage():
    """Calepinage des deux meubles, calculé une fois (il sert aux achats et au comparatif des variantes)."""
    if not _CAL:
        _CAL.append(CAL.calepinage_meubles(debit()))
    return _CAL[0]










_CH = []


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


def chants():
    """Chant thermocollant à plaquer, d'après le calepinage : pour chaque pièce, ses chants coupés visibles
    (M.CHANT["visibles"]) moins ceux qui tombent sur un chant long d'usine de la tablette (déjà fini ; on tourne ce chant
    vers l'extérieur). Renvoie chants [(repère, étape, longueur mm)], total, rouleaux achetés, rouleaux par étape et
    mètres par meuble."""
    if _CH:
        return _CH[0]
    deb = {p["rep"]: p for p in debit()}
    etape = {b.rep: b.etape for b in M.PIECES if b.rep}
    cal = calepinage()
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


def achat(code):
    """Quantité achetée : celle du modèle, sauf le chant, compté sur le calepinage."""
    return chants()["rouleaux"] if code == "chant" else M.achat(code)


def euros(v):
    return f"{v:.2f}".replace(".", ",") + " €"




# ------------------------------------------------------------------ page
CSS = """
:root{
  --paper:#F7F8F6; --ink:#1D2A33; --muted:#5E6B73; --line:#C9D0D4; --wood:#B07A45;
  --water:#2F7FB5; --tri:#C8412C; --panel:#FFFFFF; --cab:#ECE6DA; --tall:#D8CFBD; --bac:#E3C9A0;
  --socle:#C8B79B; --glass:#CFE4F2; --tile:#E9EEF0; --dg:#D29A68; --bas:#EDBE8C; --haut:#9EC9E6; color-scheme:light;
}
@media (prefers-color-scheme: dark){
  :root:not([data-theme="light"]){
    --paper:#141A1F; --ink:#E4EAED; --muted:#9AA7AE; --line:#34414A; --wood:#C9925A;
    --water:#5AA8DE; --tri:#E8664F; --panel:#1B2329; --cab:#2A3338; --tall:#394449; --bac:#5B4B33;
    --socle:#4C4436; --glass:#1F3A4E; --tile:#1D262C; --dg:#8C5E3A; --bas:#7A5534; --haut:#2F5677; color-scheme:dark;
  }
}
:root[data-theme="dark"]{
  --paper:#141A1F; --ink:#E4EAED; --muted:#9AA7AE; --line:#34414A; --wood:#C9925A;
  --water:#5AA8DE; --tri:#E8664F; --panel:#1B2329; --cab:#2A3338; --tall:#394449; --bac:#5B4B33;
  --socle:#4C4436; --glass:#1F3A4E; --tile:#1D262C; --dg:#8C5E3A; --bas:#7A5534; --haut:#2F5677; color-scheme:dark;
}
*{box-sizing:border-box}
html,body{margin:0}
body{background:var(--paper);color:var(--ink);font-family:Archivo,system-ui,-apple-system,"Segoe UI",Roboto,sans-serif;line-height:1.55;font-size:16px}
.wrap{max-width:1120px;margin:0 auto;padding:28px 16px 64px}
.kicker{font-family:"JetBrains Mono",ui-monospace,Menlo,monospace;font-size:12px;letter-spacing:.08em;text-transform:uppercase;color:var(--muted)}
h1{font-size:clamp(28px,5vw,44px);line-height:1.08;margin:6px 0 12px;font-weight:800;letter-spacing:-.01em}
h2{font-size:22px;margin:44px 0 10px;font-weight:700;scroll-margin-top:60px}
h3{font-size:15px;margin:18px 0 6px}
.pitch{font-size:18px;max-width:780px}
.fig{background:var(--panel);border:1px solid var(--line);border-radius:12px;padding:12px;margin:14px 0}
.scroll{overflow-x:auto}.scroll svg{display:block;width:100%;height:auto;max-height:78vh}
.grid2{display:grid;grid-template-columns:repeat(auto-fit,minmax(320px,1fr));gap:14px}
.grid2 .fig{margin:0}
.cap{font-size:13px;color:var(--muted);margin:8px 4px 2px}
.note{font-size:13px;color:var(--muted)}
table{border-collapse:collapse;width:100%;font-size:14px}
th,td{text-align:left;padding:7px 8px;border-bottom:1px solid var(--line);vertical-align:top}
td.num,th.num{text-align:right;font-family:"JetBrains Mono",ui-monospace,monospace;white-space:nowrap}
.mono{font-family:"JetBrains Mono",ui-monospace,monospace;white-space:nowrap}
td.u{font-size:13px;color:var(--muted)}
tr.mat td{background:var(--paper);font-weight:700;padding-top:12px}
.debit{min-width:680px}
.debit tfoot td{border-top:2px solid var(--ink)}
.tabs{display:grid;gap:10px}
.tab svg{display:block;width:100%;height:auto}
.tabt{font-size:13px;color:var(--muted);margin-bottom:3px}.tabt b{color:var(--ink)}
.tb{fill:var(--tile);stroke:var(--ink);stroke-width:3}
.pc{stroke:var(--ink);stroke-width:2;fill:var(--cab)}.pc.mB{fill:var(--bac)}.pc.mC{fill:var(--tall)}.pc.mK{fill:var(--tall)}.pc.mS{fill:var(--socle)}.pc.mD{fill:var(--wood)}.pc.mG{fill:var(--dg)}
.pc.bas{fill:var(--bas)}.pc.haut{fill:var(--haut)}
.sw.bas{background:var(--bas)}.sw.haut{background:var(--haut)}
tr.bas td:first-child{box-shadow:inset 5px 0 var(--bas)}tr.haut td:first-child{box-shadow:inset 5px 0 var(--haut)}
.leg{font-size:13px;color:var(--muted);margin:6px 2px}.leg .sw{margin-left:12px}
.pt{font:700 64px "JetBrains Mono",ui-monospace,monospace;fill:var(--ink);text-anchor:middle}
.pt.ps{font-size:40px}
.pd{font:400 40px "JetBrains Mono",ui-monospace,monospace;fill:var(--muted);text-anchor:middle}
.sw{display:inline-block;width:12px;height:12px;border-radius:3px;margin-right:8px;vertical-align:-1px;border:1px solid var(--ink)}
.mA{background:var(--cab)}.mB{background:var(--bac)}.mC{background:var(--tall)}.mK{background:var(--tall)}.mD{background:var(--wood)}.mS{background:var(--socle)}.mG{background:var(--dg)}.mE{background:#B9C2C8}
ul.pistes{padding-left:20px;max-width:860px}ul.pistes li{margin:6px 0}
.cta{display:inline-block;margin:6px 0;padding:10px 16px;border-radius:8px;background:var(--ink);color:var(--paper);text-decoration:none;font-weight:700}
svg text{font-family:Archivo,system-ui,sans-serif;fill:var(--ink)}
.sdbf{fill:var(--tile)}
.w{fill:var(--ink)}
.fixe{fill:var(--tri);fill-opacity:.07;stroke:var(--tri);stroke-width:.6;stroke-dasharray:3 2}
.rt{fill:var(--tri)}
.doorzone{fill:var(--tri);fill-opacity:.05}.doorarc{fill:none;stroke:var(--muted);stroke-width:.5;stroke-dasharray:2 2}
.leaf{fill:var(--muted)}
.leafg{fill:none;stroke:var(--tri);stroke-width:.7;stroke-dasharray:3 2}
.conf{fill:var(--tri);fill-opacity:.55}
.cab{fill:var(--cab);stroke:var(--ink);stroke-width:.35}
.cabc{fill:var(--tall);stroke:var(--ink);stroke-width:.45}
.fond{fill:var(--tall);fill-opacity:.6;stroke:var(--ink);stroke-width:.3}.fondc{fill:var(--muted);stroke:var(--ink);stroke-width:.3}
.plinthe{fill:var(--tall);stroke:var(--ink);stroke-width:.3}
.fac{fill:var(--cab);stroke:var(--ink);stroke-width:.55}.facc{fill:var(--tall);stroke:var(--ink);stroke-width:.55}
.bac{fill:var(--bac);fill-opacity:.55;stroke:var(--ink);stroke-width:.35}.bacc{fill:var(--bac);stroke:var(--ink);stroke-width:.45}
.socle{fill:var(--socle);stroke:var(--ink);stroke-width:.4}.soclec{fill:var(--socle);stroke:var(--ink);stroke-width:.5;filter:brightness(.85)}
.tas{fill:var(--wood);fill-opacity:.6;stroke:var(--ink);stroke-width:.3}.tasc{fill:var(--wood);stroke:var(--ink);stroke-width:.4}
.dg{fill:var(--dg);fill-opacity:.75;stroke:var(--ink);stroke-width:.35}.dgc{fill:var(--dg);stroke:var(--ink);stroke-width:.45;filter:brightness(.85)}
.pat{fill:var(--glass);stroke:var(--water);stroke-width:.4}.patp{fill:none;stroke:var(--water);stroke-width:.3;stroke-dasharray:1.5 1}
.patc{fill:none;stroke:var(--ink);stroke-width:.25;stroke-dasharray:.8 .8}.toile{fill:none;stroke:var(--muted);stroke-width:.4}
.alu{fill:#B9C2C8;stroke:var(--ink);stroke-width:.3}
.top{fill:var(--wood);fill-opacity:.55;stroke:var(--ink);stroke-width:.5}.topc{fill:var(--wood);stroke:var(--ink);stroke-width:.5}
.planl{fill:none;stroke:var(--wood);stroke-width:.7;stroke-dasharray:1.5 1.5}
.trap{fill:url(#hach) var(--wood);fill:var(--wood);fill-opacity:.25;stroke:var(--ink);stroke-width:.5;stroke-dasharray:1.5 1}
.shelf{fill:var(--wood);fill-opacity:.35;stroke:var(--ink);stroke-width:.3}.shelfc{fill:var(--wood);stroke:var(--ink);stroke-width:.4}
.porte{fill:var(--cab);stroke:var(--ink);stroke-width:.55}.portec{fill:var(--tall);stroke:var(--ink);stroke-width:.5}
.appf{fill:var(--panel);stroke:var(--ink);stroke-width:.7}.appc{fill:var(--panel);stroke:var(--ink);stroke-width:.9}
.app{fill:none;stroke:var(--ink);stroke-width:.6}
.led{fill:#F2C94C;stroke:#B8860B;stroke-width:.3}
.plug{fill:var(--panel);stroke:var(--ink);stroke-width:.4}
.valve{fill:var(--water);stroke:var(--ink);stroke-width:.3}
.handle{fill:var(--ink)}
.hook{fill:none;stroke:var(--ink);stroke-width:.8}
.upper{fill:none;stroke:var(--ink);stroke-width:.9;stroke-dasharray:4 2}
.swing{fill:none;stroke:var(--muted);stroke-width:.6;stroke-dasharray:2 1.5}
.sac{fill:var(--glass);fill-opacity:.55;stroke:var(--water);stroke-width:.35;stroke-dasharray:1.2 .8}.sacc{fill:var(--glass);stroke:var(--water);stroke-width:.4}
.sacopen{fill:none;stroke:var(--water);stroke-width:.45;stroke-dasharray:2 1.2}
.swingp{fill:var(--bac);fill-opacity:.12;stroke:var(--tri);stroke-width:.5;stroke-dasharray:2 1.2}
.axe{fill:var(--tri)}
.lead{fill:none;stroke:var(--muted);stroke-width:.4}
.dim{stroke:var(--muted);stroke-width:.4;fill:none}
.dimt{fill:var(--muted);font-family:"JetBrains Mono",ui-monospace,monospace !important;font-size:4.6px}
.lbl{font-size:6.5px}.lbls{font-size:4.6px;font-weight:600}.lblx{font-size:3.5px}.lblb{font-size:8px;font-weight:700}
.muted{fill:var(--muted)}
.sec{stroke:var(--tri);stroke-opacity:.45;stroke-width:.6;stroke-dasharray:6 2 1.5 2;fill:none}
.secm{fill:var(--tri)}
.sect{fill:var(--tri);font-weight:800;font-size:7px}
.floorl{stroke:var(--ink);stroke-width:1.4}
.ceil{stroke:var(--muted);stroke-width:.6;stroke-dasharray:4 3}
body.rb .vl,body:not(.rb) .vr{display:none}
.panier{fill:var(--glass);fill-opacity:.7;stroke:var(--water);stroke-width:.45}.panierc{fill:var(--glass);stroke:var(--water);stroke-width:.6}
.hinge{fill:var(--muted)}
body:not(.explications) .cap{display:none}
body:not(.changements) section[id^="changements"]{display:none}
.vbar{position:sticky;top:0;z-index:5;display:flex;flex-wrap:wrap;align-items:center;gap:6px;padding:8px 16px;background:var(--paper);border-bottom:1px solid var(--line);font-family:"JetBrains Mono",ui-monospace,monospace;font-size:12px}
.vbar .back{color:var(--ink);text-decoration:none;font-weight:600;margin-right:14px}
.vbar .back:hover{text-decoration:underline}
.vbar span{color:var(--muted);text-transform:uppercase;letter-spacing:.08em;margin:0 4px 0 10px}
.vbar button,.vbar a.btn{font:inherit;color:var(--ink);background:var(--panel);border:1px solid var(--line);border-radius:6px;padding:4px 10px;cursor:pointer;text-decoration:none}
.vbar button[aria-pressed="true"]{background:var(--ink);color:var(--paper);border-color:var(--ink)}
.vbar .sp{margin-left:auto}
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
@media (max-width:480px){ body{font-size:15px} }
"""




def patron_svg():
    """Placement des pièces des deux sacs dans la toile : les deux bandes en long, les quatre côtés en deux colonnes."""
    pt = M.PATRON
    bw, bl = pt["bande"]
    sw, sh = pt["soufflet"]
    lt, L = pt["tissu"], pt["metrage"] * 100
    o = [rect(0, 0, lt, L, "toile")]
    c = M.COUTURE

    def piece(x, y, w, h, lab, plis=(), trap=0):
        if trap:                # soufflet : trapèze, grand côté (haut du sac) en haut, petit côté réduit de trap
            d = trap / 2
            o.append(poly([(x, y), (x + w, y), (x + w - d, y + h), (x + d, y + h)], "pat"))
        else:
            o.append(rect(x, y, x + w, y + h, "pat"))
            o.append(rect(x + c, y + c, x + w - c, y + h - c, "patc"))
        for p in plis:
            o.append(f'<line class="patp" x1="{f(x)}" y1="{f(y + p)}" x2="{f(x + w)}" y2="{f(y + p)}"/>')
        o.append(text(x + w / 2, y + h / 2, lab, "lbls"))
        o.append(text(x + w / 2, y + h / 2 + 6, f"{cm(w)} × {cm(h)}", "dimt"))

    fo, hs, ds = M.FOURREAU, pt["hauteur"], pt["fond"]
    plis = (fo, fo + hs, fo + hs + ds, fo + 2 * hs + ds)
    for k in range(2):
        piece(k * bw, 0, bw, bl, f"bande {k + 1}", plis)
    for k in range(4):
        piece(2 * bw + (k // 2) * sw, (k % 2) * sh, sw, sh, "soufflet", (M.OURLET,),
              trap=pt["soufflet_haut"] - pt["soufflet_bas"])
    for k, y in enumerate(plis):
        o.append(text(-2, y + 1.2, ("fourreau", "pli du fond", "pli du fond", "fourreau")[k], "lblx muted", "end"))
    o.append(cote_h(0, lt, -6, f"laize {lt}"))
    o.append(cote_v(0, L, lt + 8, cm(L)))
    return (f'<svg viewBox="-30 -16 {f(lt + 48)} {f(L + 24)}" role="img" aria-label="Patron des sacs">'
            f'{"".join(o)}</svg>')












def entete(titre, racine, css):
    return f"""<!doctype html>
<html lang="fr">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{titre}</title>
<link rel="icon" href="{racine}favicon.svg" type="image/svg+xml">
<link rel="apple-touch-icon" href="{racine}apple-touch-icon.png">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Archivo:wght@400;500;700;800&family=JetBrains+Mono:wght@400;600&display=swap" rel="stylesheet">
<style>{css}</style>
</head>"""










