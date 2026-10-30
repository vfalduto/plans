# Gabarit commun des pages de meubles constructibles du salon (même principe que le meuble linge SDB) :
#
#   salon-etageres.html   étagères sur montants percés (3d/salon/etageres.py)
#   salon-enfilade.html   enfilade du mur ouest (3d/salon/enfilade.py)
#
# La géométrie vient de modele.py (source unique) ; chaque page garde ses données de fabrication (débit,
# quincaillerie, prix) dans son propre fichier. Style, aides SVG et ancres repris de plan.py.

import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import modele as M  # noqa: E402,F401
import plan as PL  # noqa: E402

ROOT = PL.ROOT
SALON = "salon-v4.html"
PAGES = {"etageres": "salon-etageres.html", "enfilade": "salon-enfilade.html"}
TITRES = {"etageres": "Étagères", "enfilade": "Enfilade"}
COURANTE = ' aria-current="page"'

# aides de dessin et de nombres (cm, virgule décimale)
f, virg, rect, text, cote_h, cote_v = PL.f, PL.virg, PL.rect, PL.text, PL.cote_h, PL.cote_v

CSS = PL.CSS + """
.vbar a.btn{color:var(--ink);background:var(--panel);border:1px solid var(--line);border-radius:6px;padding:4px 10px;text-decoration:none}
.vbar .btn[aria-current="page"]{background:var(--ink);color:var(--paper);border-color:var(--ink)}
.vbar .sp{flex:1}
.budget td.num{font-size:15px}.budget tr.tot td{border-top:2px solid var(--ink);font-weight:700}
.choix{font-size:13px;color:var(--muted)}
h3{margin:22px 0 8px}
@media (max-width:480px){.vbar{gap:4px;padding:8px 10px;flex-wrap:nowrap}.vbar .back{margin-right:2px;white-space:nowrap}.vbar a.btn{padding:4px 7px;white-space:nowrap}}
"""

SOMMAIRE = """
(function () {
  var toc = document.querySelector(".toc");
  if (!toc) return;
  function garde(k, v) { try { localStorage.setItem("%(cle)s-" + k, v); } catch (e) {} }
  function lit(k) { try { return localStorage.getItem("%(cle)s-" + k); } catch (e) { return null; } }
  var tol = toc.querySelector("ol"), tb = toc.querySelector(".tbtn");
  var hs = Array.prototype.slice.call(document.querySelectorAll("main h2"));
  hs.forEach(function (h) {
    var id = h.id || h.parentNode.id, li = document.createElement("li"), a = document.createElement("a");
    a.href = "#" + id;
    a.textContent = h.textContent.trim();
    li.appendChild(a);
    tol.appendChild(li);
  });
  function ouvert(on) {
    document.body.classList.toggle("toc-on", on);
    tb.setAttribute("aria-expanded", on);
    tb.textContent = on ? "« Sommaire" : "Sommaire »";
    garde("toc", on ? "1" : "0");
  }
  tb.addEventListener("click", function () { ouvert(!document.body.classList.contains("toc-on")); });
  ouvert(lit("toc") !== "0");
  function suivre() {
    var haut = document.querySelector(".vbar").offsetHeight, k = -1;
    toc.style.top = haut + "px";
    hs.forEach(function (h, i) { if (h.getBoundingClientRect().top < haut + 80) k = i; });
    tol.querySelectorAll("a").forEach(function (a, i) { a.classList.toggle("on", i === k); });
  }
  var attente = false;
  window.addEventListener("scroll", function () {
    if (!attente) { attente = true; requestAnimationFrame(function () { attente = false; suivre(); }); }
  }, {passive: true});
  window.addEventListener("resize", suivre);
  suivre();
})();
"""


def barre(courante, outils=""):
    """Barre du haut ; outils : boutons propres à la page (avant les liens des pages)."""
    liens = [(SALON, "Salon", "salon")] + [(PAGES[k], TITRES[k], k) for k in PAGES]
    btn = "".join(f'<a class="btn" href="{h}"{COURANTE if k == courante else ""}>{t}</a>' for h, t, k in liens)
    return f'<div class="vbar"><a class="back" href="index.html">← Plans</a>{outils}<span class="sp"></span>{btn}</div>'


def gabarit(titre, courante, corps, css="", outils="", script=""):
    """Page complète : barre de navigation, sommaire repliable (titres h2), légendes et changements visibles."""
    return f"""<!doctype html>
<html lang="fr">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{titre}</title>
<link rel="icon" href="favicon.svg" type="image/svg+xml">
<link rel="apple-touch-icon" href="apple-touch-icon.png">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Archivo:wght@400;500;700;800&family=JetBrains+Mono:wght@400;600&display=swap" rel="stylesheet">
<style>{CSS}{css}</style>
</head>
<body class="explications changements">
{barre(courante, outils)}
<nav class="toc" aria-label="Sommaire"><button type="button" class="tbtn" aria-expanded="true">Sommaire</button><ol></ol></nav>
<main class="wrap">
{corps}
</main>
<script>{PL.ANCRES}</script>
<script>{SOMMAIRE % {"cle": "salon-" + courante}}</script>
{f"<script>{script}</script>" if script else ""}
</body>
</html>
"""


def ecrire(nom, html):
    chemin = os.path.join(ROOT, nom)
    with open(chemin, "w", encoding="utf-8") as fh:
        fh.write(html)
    print(chemin)


# ------------------------------------------------------------------ volumes 3D des meubles (vue iso et rendus)
# Chaque générateur fournit pieces_3d(**options) → liste de Piece, en cm dans le repère du salon (x vers l'est depuis
# le mur ouest, y vers le sud depuis le mur nord, z depuis le sol). La même liste sert à la vue iso (SVG, ci-dessous)
# et aux rendus Blender (rendu_meubles.py) : matière → couleurs du SVG et matériau Blender.
from dataclasses import dataclass  # noqa: E402

MATIERES = {   # clé : (face avant x1, côté y1, dessus z1) pour le SVG ; matériau Blender
    "chene":    (("#B7834B", "#9C6C3A", "#CFA06B"), "s_chene"),     # fil horizontal (dessus, tablettes, côtés)
    "chene_v":  (("#B7834B", "#9C6C3A", "#CFA06B"), "s_chene_v"),   # fil vertical (portes, façades)
    "pin_noir": (("#2A2A2E", "#1E1E21", "#3A3A3F"), "s_pin_noir"),  # pin peint noir mat
    "acier":    (("#8E9399", "#73787E", "#A9AEB4"), "noir"),        # chevilles peintes en noir
    "melamine": (("#F2F0EA", "#DAD7CF", "#FBFAF6"), "s_melamine"),  # mélaminé blanc
    "fibre":    (("#8C6B4E", "#7A5C42", "#9E7C5E"), "s_fibre"),     # panneau de fibres dures (dos)
    "noir":     (("#26262A", "#1B1B1E", "#34343A"), "noir"),        # pieds, quincaillerie visible
}


@dataclass
class Piece:
    nom: str
    x0: float
    x1: float
    y0: float
    y1: float
    z0: float
    z1: float
    matiere: str = "chene"
    groupe: str = ""     # morceaux d'une même pièce de bois (tablette entaillée) : pas de joint entre eux
    forme: str = ""      # "" boîte ; "cyl_y" : rond d'axe y inscrit dans la boîte (chevilles en acier rond)


def _derriere(a, b):
    """a est caché par b (vue depuis +x, +y, +z) : séparés sur un axe, a du côté bas."""
    return a.x1 <= b.x0 + 1e-6 or a.y1 <= b.y0 + 1e-6 or a.z1 <= b.z0 + 1e-6


def _ordre(ps):
    """Ordre du peintre : tri topologique sur « derrière », repli sur la somme des centres en cas de cycle."""
    reste = sorted(ps, key=lambda p: p.x0 + p.x1 + p.y0 + p.y1 + p.z0 + p.z1)
    sortie = []
    while reste:
        for i, a in enumerate(reste):
            if not any(_derriere(b, a) and not _derriere(a, b) for b in reste if b is not a):
                sortie.append(reste.pop(i))
                break
        else:
            sortie.append(reste.pop(0))
    return sortie


def _aretes(p, face, ps):
    """Arêtes visibles d'une face (avant x1, côté y1 ou dessus z1) : moins les portions communes avec une face
    coplanaire et contiguë d'un morceau du même groupe (le joint n'existe pas dans le bois)."""
    ax = {"x": 0, "y": 1, "z": 2}[face]
    lo = lambda q: (q.x0, q.y0, q.z0)  # noqa: E731
    hi = lambda q: (q.x1, q.y1, q.z1)  # noqa: E731
    a, b = [i for i in range(3) if i != ax]                 # axes de la face
    plan = hi(p)[ax]
    voisins = [q for q in ps if q is not p and p.groupe and q.groupe == p.groupe and abs(hi(q)[ax] - plan) < 1e-6]
    seg = []
    for fixe, cote in ((a, 0), (a, 1), (b, 0), (b, 1)):
        libre = b if fixe == a else a
        val = (lo(p), hi(p))[cote][fixe]
        morceaux = [(lo(p)[libre], hi(p)[libre])]
        for q in voisins:                                   # q touche p de l'autre côté de cette arête
            if abs((hi(q), lo(q))[cote][fixe] - val) > 1e-6:
                continue
            c0, c1 = lo(q)[libre], hi(q)[libre]
            morceaux = [m for u0, u1 in morceaux for m in ((u0, min(u1, c0)), (max(u0, c1), u1)) if m[1] - m[0] > 1e-6]
        for u0, u1 in morceaux:
            k0, k1 = [0, 0, 0], [0, 0, 0]
            k0[ax] = k1[ax] = plan
            k0[fixe] = k1[fixe] = val
            k0[libre], k1[libre] = u0, u1
            seg.append((tuple(k0), tuple(k1)))
    return seg


def _rond_y(p, P, corps, bout):
    """Rond d'axe y en vue iso : silhouette (enveloppe des deux cercles d'extrémité) puis bout sud visible."""
    cx, cz, r = (p.x0 + p.x1) / 2, (p.z0 + p.z1) / 2, min(p.x1 - p.x0, p.z1 - p.z0) / 2
    cercle = lambda y: [P(cx + r * math.cos(t), y, cz + r * math.sin(t))  # noqa: E731
                        for t in (2 * math.pi * k / 24 for k in range(24))]
    pts = sorted(set(cercle(p.y0) + cercle(p.y1)))
    def env(q):                                            # enveloppe convexe (chaîne monotone)
        h = []
        for pt in q:
            while len(h) >= 2 and (h[-1][0] - h[-2][0]) * (pt[1] - h[-2][1]) - (h[-1][1] - h[-2][1]) * (pt[0] - h[-2][0]) <= 0:
                h.pop()
            h.append(pt)
        return h
    contour = env(pts)[:-1] + env(pts[::-1])[:-1]
    d1 = " ".join(f"{f(u)},{f(v)}" for u, v in contour)
    d2 = " ".join(f"{f(u)},{f(v)}" for u, v in cercle(p.y1))
    return (f'<polygon points="{d1}" fill="{corps}" stroke="#1B2A33" stroke-opacity=".6" stroke-width=".3"/>'
            f'<polygon points="{d2}" fill="{bout}" stroke="#1B2A33" stroke-opacity=".6" stroke-width=".3"/>')


def iso_svg(pieces, titre, echelle=2.2, marge=14, legende=None, style=""):
    """Vue axonométrique (isométrique) depuis la pièce, côté sud et en hauteur : faces avant, côté sud et dessus."""
    c, s = math.cos(math.radians(30)), math.sin(math.radians(30))
    # repère du salon indirect (x est, y sud, z haut) : vu de la pièce vers le mur ouest, le sud est à gauche
    P0 = lambda x, y, z: ((x - y) * c * echelle, ((x + y) * s - z) * echelle)
    pts = [P0(x, y, z) for p in pieces for x in (p.x0, p.x1) for y in (p.y0, p.y1) for z in (p.z0, p.z1)]
    u0, u1 = min(u for u, _ in pts) - marge, max(u for u, _ in pts) + marge
    v0, v1 = min(v for _, v in pts) - marge, max(v for _, v in pts) + marge
    o = []
    for p in _ordre(pieces):
        P = P0
        av, cote, dessus = MATIERES[p.matiere][0]
        if p.forme == "cyl_y":
            o.append(_rond_y(p, P, av, dessus))
            continue
        traits = []
        faces = [((p.x1, p.y0, p.z0), (p.x1, p.y1, p.z0), (p.x1, p.y1, p.z1), (p.x1, p.y0, p.z1), av),
                 ((p.x0, p.y1, p.z0), (p.x1, p.y1, p.z0), (p.x1, p.y1, p.z1), (p.x0, p.y1, p.z1), cote),
                 ((p.x0, p.y0, p.z1), (p.x1, p.y0, p.z1), (p.x1, p.y1, p.z1), (p.x0, p.y1, p.z1), dessus)]
        for (*q, coul), face in zip(faces, "xyz"):
            d = " ".join(f"{f(u)},{f(v)}" for u, v in (P(*k) for k in q))
            o.append(f'<polygon points="{d}" fill="{coul}" stroke="{coul}" stroke-width=".5" stroke-linejoin="round"/>')
            traits += _aretes(p, face, pieces)
        if traits:      # arêtes réelles seulement : une tablette entaillée se lit d'une seule pièce
            d = "".join(f"M{f(P(*k0)[0])},{f(P(*k0)[1])}L{f(P(*k1)[0])},{f(P(*k1)[1])}" for k0, k1 in traits)
            o.append(f'<path d="{d}" fill="none" stroke="#1B2A33" stroke-opacity=".6" stroke-width=".35" '
                     f'stroke-linecap="round"/>')
    if legende:
        o.append(text(u0 + 4, v1 - 4, legende, "lbls muted", "start"))
    st = f' style="{style}"' if style else ""
    return (f'<svg viewBox="{f(u0)} {f(v0)} {f(u1 - u0)} {f(v1 - v0)}"{st} role="img" aria-label="{titre}">'
            f'{"".join(o)}</svg>')


def rendus_html(meuble, vues):
    """Galerie des rendus Blender salon-meubles-3d/<meuble>-<vue>.jpg (vues = [(vue, légende)]) ; absents : rien."""
    figs = []
    for vue, leg in vues:
        nom = f"salon-meubles-3d/{meuble}-{vue}.jpg"
        if os.path.exists(os.path.join(ROOT, nom)):
            v = int(os.path.getmtime(os.path.join(ROOT, nom)))
            figs.append(f'<figure><img src="{nom}?v={v}" alt="{leg}" loading="lazy"><figcaption class="cap">{leg}</figcaption></figure>')
    return f'<div class="fig rendu">{"".join(figs)}</div>' if figs else '<p class="note">Rendus à produire : <span class="mono">just salon-meubles-rendu</span>.</p>'
