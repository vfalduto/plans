"""Aides SVG de la cuisine : cotes, rectangles, textes, volumes du modèle vus de dessus, fiche de la porte pliante, CSS.

Reprises de l'ancien générateur 3d/v13/plan.py (supprimé), à l'identique ; la porte du cellier (3d/v13/porte.py) et la
version imprimable (pieces/cuisine/amenagement/imprimable.py) les lisent ici. Elles diffèrent de celles de commun/dessin.py (leur `f` écrit
`{v:g}`), les dessins changeraient.
"""
import math
from html import escape
from pathlib import Path

from pieces.cuisine import modele

RACINE = Path(__file__).resolve().parent.parent.parent


def f(v):
    return f"{v:g}"


def rect(x0, y0, x1, y1, cls):
    return f'<rect class="{cls}" x="{f(x0)}" y="{f(y0)}" width="{f(x1 - x0)}" height="{f(y1 - y0)}"/>'


def text(x, y, s, cls="lbl", anchor="middle", extra=""):
    return f'<text class="{cls}" x="{f(x)}" y="{f(y)}" text-anchor="{anchor}"{extra}>{escape(s)}</text>'


def cote_h(x0, x1, y, label=None, t=3):
    """Cote horizontale, texte au-dessus."""
    label = label or virg(x1 - x0)
    return "".join([
        f'<line class="dim" x1="{f(x0)}" y1="{f(y)}" x2="{f(x1)}" y2="{f(y)}"/>',
        f'<line class="dim" x1="{f(x0)}" y1="{f(y - t)}" x2="{f(x0)}" y2="{f(y + t)}"/>',
        f'<line class="dim" x1="{f(x1)}" y1="{f(y - t)}" x2="{f(x1)}" y2="{f(y + t)}"/>',
        text((x0 + x1) / 2, y - 2.5, label, "dimt"),
    ])


def cote_d(a, b, t=0.5, dt=(0, 0)):
    """Cote oblique de a à b, texte au point t du segment, décalé de dt."""
    d = math.dist(a, b)
    ux, uy = (b[1] - a[1]) / d * 3, -(b[0] - a[0]) / d * 3  # demi-trait perpendiculaire
    tx, ty = a[0] + (b[0] - a[0]) * t + dt[0], a[1] + (b[1] - a[1]) * t + dt[1]
    return "".join([
        f'<line class="dim" x1="{f(a[0])}" y1="{f(a[1])}" x2="{f(b[0])}" y2="{f(b[1])}"/>',
        *(f'<line class="dim" x1="{f(p[0] - ux)}" y1="{f(p[1] - uy)}" x2="{f(p[0] + ux)}" y2="{f(p[1] + uy)}"/>'
          for p in (a, b)),
        text(tx, ty, f"{d:.0f}", "dimt"),
    ])


def cote_v(y0, y1, x, label=None, t=3):
    """Cote verticale, texte à gauche, tourné."""
    label = label or virg(abs(y1 - y0))
    ym = (y0 + y1) / 2
    return "".join([
        f'<line class="dim" x1="{f(x)}" y1="{f(y0)}" x2="{f(x)}" y2="{f(y1)}"/>',
        f'<line class="dim" x1="{f(x - t)}" y1="{f(y0)}" x2="{f(x + t)}" y2="{f(y0)}"/>',
        f'<line class="dim" x1="{f(x - t)}" y1="{f(y1)}" x2="{f(x + t)}" y2="{f(y1)}"/>',
        text(x - 2.5, ym, label, "dimt", extra=f' transform="rotate(-90 {f(x - 2.5)} {f(ym)})"'),
    ])


def aire(poly):
    """Aire d'un polygone (formule du lacet), en cm²."""
    return abs(sum(x0 * y1 - x1 * y0 for (x0, y0), (x1, y1) in zip(poly, poly[1:] + poly[:1]))) / 2


def pts(poly):
    return " ".join(f"{f(x)},{f(y)}" for x, y in poly)



PLAN_CLS = {"mur": "w", "allege": "win", "tech": "tech", "socle": None,
            "caisson_haut": "upper", "facade_haut": None, "plan": "pt", "plaque": "vitro",
            "aspiration": "asp", "hotte": None, "evier": "inox", "egouttoir": "egout", "cuve": "cuve", "mitigeur": "inox",
            "colonne": "tall", "facade_col": "fac", "four": "fac", "porte": None,
            "caisson": "cab", "facade": "fac", "linteau": None, "cloison": "neuf", "porte_plan": None,
            "table": "tbl", "chant": None, "peinture": None, "pied": None, "chaise": "stool", "fileur": None, "banquette": "stool",
            "etagere": "shelf", "montant": "shelf", "trappe": "trappe",
            "ardoise": None, "aimant": None, "micro_onde": "fac",
            "dormant": "dorm", "dormant_haut": None, "joue": "fac", "paumelle": None,
            "ratelier": "dark", "balai": "balai", "manche": None,
            "led": "led", "etagere_haute": "upper", "enceinte": "upper", "lampe": "lampe", "fil": None, "aspirateur": "aspi", "cafetiere": "cafe",
            "plante": "plante", "pot": None, "seau": "aspi"}


def volumes_plan(exclus=()):
    """Volumes du modèle vus de dessus, du plus bas au plus haut (une seule emprise par pile de tablettes)."""
    o = []
    vues = set()
    for b in sorted([b for b in modele.ENVELOPPE + modele.MEUBLES if b.nom not in exclus], key=lambda b: b.z1):
        cls = PLAN_CLS[b.role]
        if cls == "shelf":
            if (b.x0, b.y0, b.x1, b.y1) in vues:
                continue
            vues.add((b.x0, b.y0, b.x1, b.y1))
        if isinstance(b, modele.Cyl) and cls:
            o.append(f'<circle class="{cls}" cx="{f(b.cx)}" cy="{f(b.cy)}" r="{f(b.r)}"/>')
        elif cls and getattr(b, "arrondi", 0) and b.coins == "tous":
            o.append(f'<rect class="{cls}" x="{f(b.x0)}" y="{f(b.y0)}" width="{f(b.x1 - b.x0)}" height="{f(b.y1 - b.y0)}" '
                     f'rx="{f(b.arrondi)}"/>')
        elif cls and getattr(b, "arrondi", 0):
            r = b.arrondi
            o.append(f'<path class="{cls}" d="M{f(b.x0)} {f(b.y0)}H{f(b.x1)}V{f(b.y1)}H{f(b.x0 + r)}'
                     f'A{f(r)} {f(r)} 0 0 1 {f(b.x0)} {f(b.y1 - r)}Z"/>')
        elif cls:
            o.append(rect(b.x0, b.y0, b.x1, b.y1, cls))
    return o


def virg(v):
    """Cote à une décimale au plus, virgule française (68,7 ; 60)."""
    return f"{v:.1f}".rstrip("0").rstrip(".").replace(".", ",")


def fiche_tango():
    """Tableau du modèle de porte pliante (aussi sur la page « Porte du cellier »)."""
    a, t, b = modele.PLIANTE, modele.TANGO, modele.BAIE_Y1 - modele.BAIE_Y0
    hp = round(a["z1"] - a["z0"], 1)
    lignes = [
        ("Ferrure", f'{t["nom"]} {t["ref"]} : kit 2 panneaux, rail alu de 1,20 (à recouper à {virg(b)}), 1 monture à '
                    f'roulements, pivot haut, pivot bas, 3 charnières sur chant. 40 kg par panneau, 16 à 40 d\'épaisseur.'),
        ("Panneaux (à faire découper)", f'2 × {virg(a["l"])} × {virg(hp)} × {virg(a["ep"])} (mélaminé ou plaqué chêne, '
                    f'≈ 9 kg chacun). Notice : largeur Lp = (B − 1,2 − J) / 2 mm, J = 4 pour 16 à 22 d\'épaisseur ; '
                    f'hauteur Hp = H − 64.'),
        ("Baie", f'{virg(b)} × 204 : rail 33 × 27 vissé sous le linteau, dans l\'épaisseur de la cloison de 7 ; jeu de 2 '
                 f'sous le rail, panneaux h {virg(a["z0"])} → {virg(a["z1"])}.'),
        ("Sol", "pas de rail : un seul pivot bas, au nord, contre le mur neuf. Le bout libre est tenu en haut par la monture."),
        ("Passage libre", f'≈ {virg(modele.PASSAGE_CELLIER)}. À confirmer avec le logiciel SLIDESOFT de Mantion.'),
        ("Prix", f'{t["prix"]}, plus les panneaux.'),
    ]
    corps = "".join(f"<tr><th>{escape(x)}</th><td>{escape(y)}</td></tr>" for x, y in lignes)
    return f'<table class="orga fiche"><tbody>{corps}</tbody></table>'


def sources_tango():
    t = modele.TANGO
    return (f'Sources : <a href="{t["notice"]}">notice commerciale Mantion Tango</a> (cotes de baie et de panneau), '
            f'<a href="{t["achat"]}">fiche revendeur</a> (16 à 40 mm, 750 de large au plus).')


CSS = """
:root{
  --paper:#F7F8F6; --ink:#1D2A33; --muted:#5E6B73; --line:#C9D0D4; --wood:#B07A45;
  --water:#2F7FB5; --tri:#C8412C; --panel:#FFFFFF; --cab:#ECE6DA; --tall:#D8CFBD;
  --tech:#E1E6E9; --glass:#CFE4F2; --cement:#C9CBCA; --elec:#A86F00; --prise:#7B4FBF; color-scheme:light;
}
@media (prefers-color-scheme: dark){
  :root:not([data-theme="light"]){
    --paper:#141A1F; --ink:#E4EAED; --muted:#9AA7AE; --line:#34414A; --wood:#C9925A;
    --water:#5AA8DE; --tri:#E8664F; --panel:#1B2329; --cab:#2A3338; --tall:#394449;
    --tech:#26303A; --glass:#1F3A4E; --cement:#3A3E40; --elec:#E8B84A; --prise:#B597F0; color-scheme:dark;
  }
}
:root[data-theme="dark"]{
  --paper:#141A1F; --ink:#E4EAED; --muted:#9AA7AE; --line:#34414A; --wood:#C9925A;
  --water:#5AA8DE; --tri:#E8664F; --panel:#1B2329; --cab:#2A3338; --tall:#394449;
  --tech:#26303A; --glass:#1F3A4E; --cement:#3A3E40; --elec:#E8B84A; --prise:#B597F0; color-scheme:dark;
}
*{box-sizing:border-box}
.z1{fill:#5B9E6A;opacity:.85}.z2{fill:#A9CF8F;opacity:.85}.z3{fill:#E8C26A;opacity:.85}.z4{fill:#D9826B;opacity:.85}
.rep{stroke:#C8412C;stroke-width:.5;stroke-dasharray:3 2;opacity:.7}.rept{fill:#C8412C}
.lblz{font-size:3.8px;fill:var(--ink)}.hpw svg{max-width:690px;display:block;margin:0 auto}.hsa{fill:#C98A1E;opacity:.45}.hsl{fill:#2F7FB5;opacity:.4}tr.hpr td{background:color-mix(in srgb,#2F7FB5 10%,transparent)}.hpb{opacity:.92}text.hph{fill:#C98A1E;font-weight:600;paint-order:stroke;stroke:var(--panel);stroke-width:4px}.hpg{stroke:var(--line);stroke-width:.6}.hpt{font-size:12px;fill:var(--muted)}.hpt.on{fill:#fff;font-weight:600}.hpt.rept{fill:#C8412C}.hpn{font-size:15px;font-weight:700;fill:var(--ink)}.hpp{stroke:#C98A1E;stroke-width:2}.hpc{stroke:var(--ink);stroke-width:1;stroke-dasharray:5 4;opacity:.7}.hpc.act{stroke-dasharray:none;stroke-width:2;opacity:1}.hpc.rec{stroke:#2F7FB5;opacity:1}text.hpc{stroke:none;fill:var(--ink);font-weight:600}text.hpc.rec{fill:#2F7FB5}.lblz.rept{fill:#C8412C}.regle{display:none}html[data-taille="175"] .regle[data-t="175"],html[data-taille="180"] .regle[data-t="180"]{display:inline}
.leg .sw{display:inline-block;width:12px;height:9px;border-radius:2px;margin:0 3px 0 8px;vertical-align:middle}
html,body{margin:0}
body{background:var(--paper);color:var(--ink);font-family:Archivo,system-ui,-apple-system,"Segoe UI",Roboto,sans-serif;line-height:1.55;font-size:16px}
.wrap{max-width:1120px;margin:0 auto;padding:28px 16px 64px}
.kicker{font-family:"JetBrains Mono",ui-monospace,Menlo,monospace;font-size:12px;letter-spacing:.08em;text-transform:uppercase;color:var(--muted)}
h1{font-size:clamp(28px,5vw,44px);line-height:1.08;margin:6px 0 12px;font-weight:800;letter-spacing:-.01em}
h2{font-size:22px;margin:44px 0 10px;font-weight:700}
.pitch{font-size:18px;max-width:780px}
.fig{background:var(--panel);border:1px solid var(--line);border-radius:12px;padding:12px;margin:14px 0}
.scroll{overflow-x:auto;-webkit-overflow-scrolling:touch}
.scroll svg{display:block;width:100%;height:auto}
.cap{font-size:13px;color:var(--muted);margin:8px 4px 2px}
.note{font-size:13px;color:var(--muted)}
.txt{font-size:14px;line-height:1.55;margin:10px 4px 0}.txt p{margin:0 0 8px}.txt .src{font-size:13px;color:var(--muted)}
.fiche th{width:190px}
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
.grid2{display:grid;grid-template-columns:repeat(auto-fit,minmax(300px,1fr));gap:16px}
h3{font-size:16px;margin:4px 4px 8px}
table{border-collapse:collapse;width:100%;font-size:14px}
th,td{text-align:left;padding:7px 8px;border-bottom:1px solid var(--line);vertical-align:top}
.mono{font-family:"JetBrains Mono",ui-monospace,monospace;white-space:nowrap}
svg text{font-family:Archivo,system-ui,sans-serif;fill:var(--ink)}
.w{fill:var(--ink)}
.bgwall{fill:var(--line);fill-opacity:.35}
.wallv{fill:#D5DADD;stroke:var(--muted);stroke-width:.5}
.floorbg{fill:var(--wood);fill-opacity:.13}
.wc{fill:var(--line);fill-opacity:.55}
.lame{fill:none;stroke:var(--wood);stroke-width:.5;stroke-opacity:.5}
.ciment{fill:var(--cement)}
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
.trit{fill:var(--tri);font-family:"JetBrains Mono",monospace !important;font-size:7px;font-weight:600;text-anchor:middle}
.tbl{fill:var(--wood);fill-opacity:.5;stroke:var(--ink);stroke-width:.9}
.stool{fill:var(--wood);fill-opacity:.28;stroke:var(--ink);stroke-width:.7}
.swingz{fill:var(--tri);fill-opacity:.05;stroke:var(--muted);stroke-width:.7;stroke-dasharray:3 2}
.swing{fill:none;stroke:var(--muted);stroke-width:.7;stroke-dasharray:2 2}
.doorleaf{stroke:var(--ink);stroke-width:2}
.ardoise{fill:#2B3230;stroke:var(--ink);stroke-width:.6}.aimant{fill:#A7AEB2;stroke:var(--ink);stroke-width:.6}
body:not(.explications) .cap{display:none}
.vbar .expl{margin-left:auto}
body:not(.changements) section[id^="changements"]{display:none}
.lampe{fill:#F2C94C;fill-opacity:.35;stroke:#B8860B;stroke-width:.7;stroke-dasharray:3 2}
.lblc{font-size:3.6px;font-style:italic;fill:var(--ink)}
.plante{fill:#6E9B5A;fill-opacity:.8;stroke:#3F6B31;stroke-width:.6;stroke-dasharray:3 2}.pot{fill:#C2703D;stroke:var(--ink);stroke-width:.5}
.aspi{fill:#8A97A3;stroke:var(--ink);stroke-width:.6}
.cafe{fill:#1C1E21;fill-opacity:.35;stroke:var(--ink);stroke-width:.5}
.led{fill:#F2C94C;stroke:#B8860B;stroke-width:.4}
.poig{stroke:#8E8E8B;stroke-width:1.4;stroke-linecap:round}
.poig.bois{stroke:#8A5A2B;stroke-width:2.2;stroke-linecap:butt}
.orga td,.orga th{vertical-align:top}
.capa td.ok{background:color-mix(in srgb,#3E8E5A 20%,transparent)}
.capa td.ko{background:color-mix(in srgb,var(--tri) 22%,transparent)}
h3{font-size:15px;margin:22px 0 8px}.orga .on{background:var(--cab)}
.balai{fill:#C9A46A;stroke:var(--ink);stroke-width:.4}
.tog{display:flex;flex-wrap:wrap;align-items:center;gap:6px;margin:0 0 10px;font-family:"JetBrains Mono",ui-monospace,monospace;font-size:12px}
.tog span{color:var(--muted);text-transform:uppercase;letter-spacing:.08em;margin-right:4px}
.tog button{font:inherit;color:var(--ink);background:var(--panel);border:1px solid var(--line);border-radius:6px;padding:4px 10px;cursor:pointer}
.tog button[aria-pressed="true"]{background:var(--ink);color:var(--paper);border-color:var(--ink)}
.vt[data-etat="ferme"] .ouv,.vt[data-etat="mi"] .ouv,.vt:not([data-etat="ferme"]) .fer,.vt:not([data-etat="mi"]) .mi{display:none}
.pliee{fill:none;stroke:var(--ink);stroke-width:2.5;stroke-linejoin:round}
.transp .trp{fill:none;stroke:var(--ink);stroke-width:.7;stroke-dasharray:4 2}
.fig:not(.transp) .trp-lbl{display:none}
.dorm{fill:var(--panel);stroke:var(--ink);stroke-width:.6}
.seuil{stroke:var(--muted);stroke-width:.7;stroke-dasharray:3 2}
.slid{fill:var(--wood);fill-opacity:.55;stroke:var(--wood);stroke-width:.6}
.pivot{fill:var(--paper);stroke:var(--ink);stroke-width:.8}
.leafd{stroke:var(--ink);stroke-width:3;stroke-linecap:round}
.leafg{stroke:var(--muted);stroke-width:1.5;stroke-opacity:.45;stroke-dasharray:3 2}
.move{stroke:var(--tri);stroke-width:1;stroke-dasharray:2.5 2;fill:none}.flm{fill:var(--tri)}
.diag{stroke:var(--tri);stroke-width:1;stroke-dasharray:4 2}.diagt{font:600 8px "JetBrains Mono",monospace;fill:var(--tri)}
.celsol{fill:var(--ink);fill-opacity:.1}
.shelf,.shelfd{fill:var(--wood);fill-opacity:.3;stroke:var(--wood);stroke-width:.6}
.shelfc{fill:var(--wood);stroke:var(--ink);stroke-width:.6}
.trappe{fill:var(--wood);fill-opacity:.12;stroke:var(--ink);stroke-width:.8;stroke-dasharray:3 2}
.frame{fill:none;stroke:var(--line);stroke-width:.8}
td.num,th.num{text-align:right;font-family:"JetBrains Mono",ui-monospace,monospace;white-space:nowrap}
tfoot td{font-weight:700}
.upper{fill:none;stroke:var(--ink);stroke-width:.8;stroke-dasharray:3 2}
.dim{stroke:var(--muted);stroke-width:.6;fill:none}
.dimt{fill:var(--muted);font-family:"JetBrains Mono",ui-monospace,monospace !important;font-size:8px}
.lbl{font-size:7.5px}.lbls{font-size:6.5px}.lblx{font-size:5px}.lblb{font-size:9px;font-weight:700}
.muted{fill:var(--muted)}
.sec{stroke:var(--tri);stroke-opacity:.3;stroke-width:.9;stroke-dasharray:10 3 2 3;fill:none}
.secm{fill:var(--tri);fill-opacity:.45}
.sect{fill:var(--tri);fill-opacity:.55;font-weight:800;font-size:11px}
.floorl{stroke:var(--ink);stroke-width:2}
.ceil{stroke:var(--muted);stroke-width:1;stroke-dasharray:6 4}
.vbar{position:sticky;top:0;z-index:5;display:flex;flex-wrap:wrap;align-items:center;gap:6px;padding:8px 16px;background:var(--paper);border-bottom:1px solid var(--line);font-family:"JetBrains Mono",ui-monospace,monospace;font-size:12px}
.vbar .back{color:var(--ink);text-decoration:none;font-weight:600;margin-right:14px}
.vbar .back:hover{text-decoration:underline}
.vbar span{color:var(--muted);text-transform:uppercase;letter-spacing:.08em;margin-right:4px}
.vbar button{font:inherit;color:var(--ink);background:var(--panel);border:1px solid var(--line);border-radius:6px;padding:4px 10px;cursor:pointer}
.pbar{position:sticky;top:41px;z-index:4;display:flex;flex-wrap:wrap;align-items:center;gap:6px;margin:0 0 12px;padding:8px 0;background:var(--paper);font-family:"JetBrains Mono",ui-monospace,monospace;font-size:12px}
.pbar span{color:var(--muted);text-transform:uppercase;letter-spacing:.08em;margin-right:4px}
.pbar button{font:inherit;color:var(--ink);background:var(--panel);border:1px solid var(--line);border-radius:6px;padding:4px 10px;cursor:pointer}
.pbar button[aria-pressed="true"]{background:var(--ink);color:var(--paper);border-color:var(--ink)}
.vbar button[aria-pressed="true"]{background:var(--ink);color:var(--paper);border-color:var(--ink)}
.h2b{display:flex;flex-wrap:wrap;align-items:center;gap:12px}
.impr{font:12px "JetBrains Mono",ui-monospace,monospace;font-weight:400;color:var(--ink);background:var(--panel);border:1px solid var(--line);border-radius:6px;padding:4px 10px;text-decoration:none}
.impr:hover{border-color:var(--ink)}
.fade{opacity:.4}
.ell{fill:#F2C94C;fill-opacity:.45;stroke:var(--elec);stroke-width:1}.ellx{stroke:var(--elec);stroke-width:1}
.eli{fill:var(--panel);stroke:var(--elec);stroke-width:1.1}.elil{stroke:var(--elec);stroke-width:1.1}
.elk{fill:none;stroke:var(--elec);stroke-width:.8;stroke-dasharray:3 2}
.elp,.elpe{fill:var(--panel);stroke:var(--prise);stroke-width:1.1}.elpd{fill:var(--prise)}.elc{stroke-dasharray:2 1.2}
.elie{fill:var(--panel);stroke:var(--elec);stroke-width:1.1}
.elt{fill:var(--elec);font-weight:700}.elpt{fill:var(--prise);font-weight:600}
@media (max-width:480px){ body{font-size:15px} }
"""
