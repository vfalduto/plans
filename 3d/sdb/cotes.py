# Vues à plat cotées du meuble bas (V6.1) : feuille de cotes et dessins des opérations de la notice ; pages.py les place.
#
#   python3 3d/sdb/pages.py   (just sdb)
#
# Chaque vue est une projection orthogonale des pièces du modèle, rien n'est dessiné à la main :
#   face    on regarde le mur du fond depuis la salle de bain : u = y (nord à gauche), v = z
#   cote    on regarde vers le nord depuis le sud : u = x (le mur du fond à droite), v = z ; coupe au plan y = ys
#   dessus  on regarde d'en haut : u = x (mur du fond à droite), v = y (nord en haut) ; coupe au niveau z = zs
# Les pièces coupées sont foncées, celles vues derrière le plan de coupe claires. Cotes en cm ; niveaux depuis le sol.

import math
import os
import sys
from html import escape

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import modele as M  # noqa: E402
import plan as PL  # noqa: E402

cm, f = PL.cm, PL.f

CLS = {"bois": "obois", "pied": "omet", "vis": "omet", "facade": "ofac", "bac": "omel", "support": "omel",
       "barre": "obar", "plan": "oplan", "machine": "omach", "sac": "osac", "tuyau": "otuy"}


def bas():
    """Pièces et équipements du meuble bas (sans le caisson haut ni les prises)."""
    return [b for b in M.version("d") if b.groupe != "caisson_haut" and b.role not in ("prise", "led")]


# ------------------------------------------------------------------ contours
def _coupe_z(b, zs):
    """Étendue en x d'un profil coupé au niveau zs (profils convexes)."""
    xs = []
    pts = b.xz
    for (x0, z0), (x1, z1) in zip(pts, pts[1:] + pts[:1]):
        if (z0 - zs) * (z1 - zs) <= 0 and z0 != z1:
            xs.append(x0 + (zs - z0) / (z1 - z0) * (x1 - x0))
    return (min(xs), max(xs)) if xs else (b.x0, b.x1)


def contour(b, vue, s=None):
    """Contour de la pièce dans la vue, en coordonnées du dessin (le y du SVG descend : v = −z, ou y en dessus)."""
    if vue == "face":
        return [(u, -z) for u, z in b.pts("x")]
    if vue == "cote":
        if b.encoche and s is not None and b.encoche[2] < s < b.encoche[3]:      # coupe dans l'encoche du plan
            x1 = b.encoche[0]
            return [(b.x0, -b.z0), (x1, -b.z0), (x1, -b.z1), (b.x0, -b.z1)]
        return [(x, -z) for x, z in b.pts("y")]
    x0, x1 = _coupe_z(b, s) if isinstance(b, M.Profil) and s is not None and b.z0 < s < b.z1 else (b.x0, b.x1)
    return [(x0, b.y0), (x1, b.y0), (x1, b.y1), (x0, b.y1)]


def projeter(blocs, vue, s=None, prof=None):
    """Polygones dessinés du plus loin au plus près ; s : position du plan de coupe (cote : y, dessus : z) ;
    prof : profondeur vue derrière la coupe (au-delà, les pièces ne sont pas dessinées)."""
    o, vus, coupes = [], [], []
    for b in blocs:
        if vue == "face":
            vus.append((-b.x0, b, False))
        elif vue == "cote":
            if b.y0 >= s or (prof is not None and b.y0 < s - prof):
                continue
            (coupes if b.y1 > s else vus).append((b.y1, b, b.y1 > s))
        else:
            if b.z0 >= s:
                continue
            (coupes if b.z1 > s else vus).append((b.z1, b, b.z1 > s))
    for _, b, cut in sorted(vus, key=lambda t: t[0]) + sorted(coupes, key=lambda t: t[0]):
        cls = CLS.get(b.role, "omel") + (" cut" if cut else "")
        o.append(PL.poly(contour(b, vue, s), cls))
    return o


# ------------------------------------------------------------------ cotes et repères
def cote_h(x0, x1, y, label=None, dy=0, ext=None, place=""):
    """Cote horizontale ; dy décale le texte (petites cotes) ; ext = y de départ des lignes d'attache ; place :
    "gauche" ou "droite" pour écrire une petite cote hors de la ligne, à côté de son trait."""
    label = label or cm(abs(x1 - x0))
    o = []
    if ext is not None:
        o += [f'<line class="ext" x1="{f(x)}" y1="{f(ext)}" x2="{f(x)}" y2="{f(y)}"/>' for x in (x0, x1)]
    o += [f'<line class="dim" x1="{f(x0)}" y1="{f(y)}" x2="{f(x1)}" y2="{f(y)}"/>',
          f'<line class="tick" x1="{f(x0 - .8)}" y1="{f(y + .8)}" x2="{f(x0 + .8)}" y2="{f(y - .8)}"/>',
          f'<line class="tick" x1="{f(x1 - .8)}" y1="{f(y + .8)}" x2="{f(x1 + .8)}" y2="{f(y - .8)}"/>',
          PL.text(x0 - 1 if place == "gauche" else x1 + 1 if place == "droite" else (x0 + x1) / 2, y - 0.9 + dy, label,
                  "ct", "end" if place == "gauche" else "start" if place == "droite" else "middle")]
    return "".join(o)


def cote_v(y0, y1, x, label=None, dx=0, ext=None, place=""):
    """Cote verticale (y du dessin) ; place : "haut" ou "bas" pour une petite cote écrite au-delà de son trait."""
    label = label or cm(abs(y1 - y0))
    ym = (y0 + y1) / 2
    if place:
        ym = min(y0, y1) - 2.4 if place == "haut" else max(y0, y1) + 2.4
    o = []
    if ext is not None:
        o += [f'<line class="ext" x1="{f(ext)}" y1="{f(y)}" x2="{f(x)}" y2="{f(y)}"/>' for y in (y0, y1)]
    o += [f'<line class="dim" x1="{f(x)}" y1="{f(y0)}" x2="{f(x)}" y2="{f(y1)}"/>',
          f'<line class="tick" x1="{f(x - .8)}" y1="{f(y0 + .8)}" x2="{f(x + .8)}" y2="{f(y0 - .8)}"/>',
          f'<line class="tick" x1="{f(x - .8)}" y1="{f(y1 + .8)}" x2="{f(x + .8)}" y2="{f(y1 - .8)}"/>',
          PL.text(x - 0.9 + dx, ym, label, "ct", extra=f' transform="rotate(-90 {f(x - 0.9 + dx)} {f(ym)})"')]
    return "".join(o)


def chaine_h(xs, y, ext=None):
    """Chaîne de cotes horizontales entre des points triés ; les petites cotes passent sous la ligne, les jeux de
    moins de 1 restent sans chiffre (dits dans la légende)."""
    xs = sorted(xs)
    o, n = [], len(xs) - 1
    for k, (a, b) in enumerate(zip(xs, xs[1:])):
        petit = b - a < 4
        place = ("gauche" if k == 0 else "droite" if k == n - 1 else "") if petit else ""
        o.append(cote_h(a, b, y, label=None if b - a >= 1 else " ", dy=3.4 if petit and not place else 0, ext=ext,
                        place=place))
    return "".join(o)


def chaine_v(ys, x, ext=None):
    ys = sorted(ys)
    o, n = [], len(ys) - 1
    for k, (a, b) in enumerate(zip(ys, ys[1:])):
        petit = b - a < 4
        place = ("haut" if k == 0 else "bas" if k == n - 1 else "") if petit else ""
        o.append(cote_v(a, b, x, label=None if b - a >= 1 else " ", dx=3.4 if petit and not place else 0, ext=ext,
                        place=place))
    return "".join(o)


def niveaux(liste, x, droite=False):
    """Niveaux depuis le sol (▽ 85,5) à gauche (ou à droite) du dessin, reliés à l'élément par un trait fin ;
    liste : (z, texte ou None, x de l'élément). Les textes trop proches s'écartent vers le haut, le triangle reste au
    vrai niveau."""
    t, sens = 1.1, 1 if droite else -1
    o, der = [], None
    for z, label, x_ext in sorted(liste, key=lambda n: n[0]):
        ty = -z if der is None else min(-z, der - 3.0)
        der = ty
        o.append(f'<line class="ext" x1="{f(x)}" y1="{f(-z)}" x2="{f(x_ext)}" y2="{f(-z)}"/>'
                 f'<polygon class="niv" points="{f(x - t)},{f(-z - 2 * t)} {f(x + t)},{f(-z - 2 * t)} {f(x)},{f(-z)}"/>')
        if ty != -z:
            o.append(f'<polyline class="lead" points="{f(x + sens * t)},{f(-z - t)} {f(x + sens * 2)},{f(ty - .9)}"/>')
        o.append(PL.text(x + sens * 2.2, ty, label or cm(z), "nt", "start" if droite else "end"))
    return "".join(o)


def etiquette(x, y, tx, ty, texte, ancre="start"):
    """Repère : trait de rappel du point (x, y) au texte."""
    return (f'<line class="lead" x1="{f(x)}" y1="{f(y)}" x2="{f(tx)}" y2="{f(ty)}"/>'
            f'<circle class="pt" cx="{f(x)}" cy="{f(y)}" r=".45"/>' + PL.text(tx + (0.6 if ancre == "start" else -0.6),
                                                                              ty + 0.9, texte, "lt", ancre))


def svg(x0, y0, x1, y1, corps, titre):
    return (f'<svg class="cotes" viewBox="{f(x0)} {f(y0)} {f(x1 - x0)} {f(y1 - y0)}" role="img" '
            f'aria-label="{escape(titre)}">{"".join(corps)}</svg>')


def figure(id_, titre, dessin, legende, cls=""):
    return (f'<figure class="fcote {cls}" id="{id_}"><figcaption class="ftitre">{escape(titre)}</figcaption>'
            f'<div class="scroll">{dessin}</div><p class="cap">{legende}</p></figure>')


def hublot(m, vue):
    """Hublot de la machine en vue de face (deux cercles)."""
    if vue != "face":
        return ""
    cy, cz = (m.y0 + m.y1) / 2, m.z0 + 50
    return "".join(f'<circle class="ohub" cx="{f(cy)}" cy="{f(-cz)}" r="{r}"/>' for r in (17, 12.5))


# ------------------------------------------------------------------ feuille de cotes
def nom(n):
    return next(b for b in M.version("d") if b.nom == n)


def vue_face():
    """Vue de face, depuis la salle de bain : le mur du fond derrière, les murs nord et sud de chaque côté."""
    h = M.Z_DESSUS + 8
    o = [PL.rect(M.Y0, -h, M.Y1, 0, "omur"), PL.rect(M.Y0 - 4, -h, M.Y0, 0, "omurc"), PL.rect(M.Y1, -h, M.Y1 + 4, 0, "omurc"),
         f'<line class="osol" x1="{f(M.Y0 - 6)}" y1="0" x2="{f(M.Y1 + 6)}" y2="0"/>']
    o += projeter(bas(), "face")
    o.append(hublot(M.MACHINE, "face"))
    p = M.PORTE_BAC
    o.append(f'<circle class="otrou" cx="{f((p.y0 + p.y1) / 2)}" cy="{f(-(p.z1 - 3))}" r="1.25"/>')
    o.append(PL.text((p.y0 + p.y1) / 2, -(p.z0 + p.z1) / 2, "porte A6", "lt"))
    o.append(PL.text((p.y0 + p.y1) / 2, -(p.z0 + p.z1) / 2 + 3.4, "(linge sale)", "lt muted"))
    o.append(PL.text((M.LLZ["y0"] + M.LLZ["y1"]) / 2, -(M.Z_PLAN - 12), "machine", "lt"))
    o.append(PL.text(M.CENTRE, -M.Z_PLAN - 0.35, "plan D1", "lt muted"))
    e = M.ECH
    ys = [M.Y0, e["n"], e["n"] + M.DE, e["c"], e["c"] + M.DE, e["s"], e["s"] + M.DE, M.Y1]
    o.append(chaine_h(ys, 6, ext=0))
    o.append(cote_h(M.Y0, M.Y1, 13, f"{cm(M.Y1 - M.Y0)} entre les murs (relevé au fond)"))
    o.append(chaine_h([M.Y0, p.y0, p.y1], -h - 3))
    o.append(PL.text(p.y1 + 1, -h - 3.2, "porte", "lt muted", "start"))
    o.append(niveaux([(M.Z0, f"{cm(M.Z0)} vérins", M.Y0), (p.z0, f"{cm(p.z0)} bas de la porte", p.y0),
                      (p.z1, f"{cm(p.z1)} haut de la porte", p.y0), (M.Z_PLAN, f"{cm(M.Z_PLAN)} dessous du plan", M.Y0),
                      (M.Z_DESSUS, f"{cm(M.Z_DESSUS)} dessus du plan", M.Y0)], M.Y0 - 9))
    o.append(niveaux([(M.LL["h"], f"{cm(M.LL['h'])} machine", M.MACHINE.y1),
                      (M.Z_DESSUS, f"{cm(M.Z_DESSUS)}", M.Y1)], M.Y1 + 9, droite=True))
    o.append(PL.text(M.Y0 - 0.6, -h - 1, "nord", "lt muted", "end"))
    o.append(PL.text(M.Y1 + 0.6, -h - 1, "sud", "lt muted", "start"))
    return svg(M.Y0 - 46, -h - 8, M.Y1 + 34, 17, o, "Vue de face cotée")


def coupe_bac():
    """Coupe de côté par le sac nord, vue vers le nord : l'échelle nord derrière, le L coupé, fermé et ouvert à 20°."""
    s = (M.SACS[0].y0 + M.SACS[0].y1) / 2
    h = M.Z_DESSUS + 8
    o = [PL.rect(M.X1, -h, M.X1 + 4, 0, "omurc"),
         f'<line class="osol" x1="{f(M.FACE - 14)}" y1="0" x2="{f(M.X1 + 4)}" y2="0"/>']
    o += projeter(bas(), "cote", s)
    a, axe = M.BAC["angle"], M.BAC["axe"]
    for n in ("plateau", "contrefiche_n", "bac_porte"):        # le L ouvert à 20°, en tireté
        o.append(PL.poly([(x, -z) for x, z in (M.bascule(x, z, axe, a) for x, z in nom(n).pts("y"))], "oswing"))
    o.append(f'<circle class="oaxe" cx="{f(axe[0])}" cy="{f(-axe[1])}" r=".7"/>')
    xb0, xr0, zb0, zb1 = M.BAC["barres"]
    ex = M.X1 + 4
    o.append(chaine_h([M.FACE, M.XO0, M.XO0 + M.DL, M.XO1 - M.DL, M.XO1, M.X1], 6, ext=0))
    o.append(cote_h(M.FACE, M.X1, 13, f"{cm(M.PROF)} profondeur, plan compris"))
    o.append(cote_h(M.XO0, xr0, -h - 3, f"{cm(xr0 - M.XO0)} barre arrière", ext=-zb1))
    xb = M.BAC["x_butee"]
    o.append(cote_h(M.XO0, xb, -M.Z_BUTEE + 5.5, cm(xb - M.XO0), ext=-M.Z_BUTEE))
    o.append(etiquette(xb, -M.Z_BUTEE, xb + 9, -M.Z_BUTEE - 6, "tire-fond de butée"))
    o.append(etiquette(axe[0], -axe[1], M.FACE - 4, -axe[1] - 6, "axe (charnières plates)", "end"))
    hp = M.bascule(M.FACE, M.PORTE_BAC.z1, axe, a)
    o.append(PL.text(hp[0] - 1, -hp[1] + 4, f"{a}°", "lt", "end"))
    o.append(PL.text((M.XO0 + M.XO1) / 2 + 2, -45, "sac (coupé)", "lt"))
    o.append(niveaux([(M.Z0, f"{cm(M.Z0)} vérins", M.FACE), (M.Z0 + M.DL, f"{cm(M.Z0 + M.DL)} dessus des rails", M.XO0),
                      (M.Z_BUTEE, f"{cm(M.Z_BUTEE)} tire-fond", M.XO0),
                      ((zb0 + zb1) / 2, f"{cm((zb0 + zb1) / 2)} axe des barres", M.XO0),
                      (M.Z_PLAN, f"{cm(M.Z_PLAN)} dessous du plan", M.FACE),
                      (M.Z_DESSUS, f"{cm(M.Z_DESSUS)} dessus du plan", M.FACE)], M.FACE - 26))
    o.append(PL.text(M.FACE - 8, 4.5, "salle de bain", "lt muted", "end"))
    o.append(PL.text(ex - 3, -h - 1.4, "mur du fond", "lt muted", "end"))
    return svg(M.FACE - 56, -h - 8, ex + 6, 17, o, "Coupe par le bac")


def coupe_machine():
    """Coupe de côté par le robinet, vue vers le nord : la machine coupée, l'échelle du milieu derrière, les tuyaux."""
    s = M.ROBINET["y"]
    h = M.ROBINET["z"] + 6
    o = [PL.rect(M.X1, -h, M.X1 + 4, 0, "omurc"),
         f'<line class="osol" x1="{f(M.FACE - 14)}" y1="0" x2="{f(M.X1 + 4)}" y2="0"/>']
    o += projeter(bas(), "cote", s, prof=30)
    m = M.MACHINE
    rb = M.ROBINET
    o.append(f'<circle class="ovanne" cx="{f(M.X1 - 1.5)}" cy="{f(-rb["z"])}" r="1.6"/>')
    o.append(chaine_h([M.FACE, m.x0, m.x1, M.X1], 6, ext=0))
    o.append(cote_h(M.FACE, M.X1, 13, f"{cm(M.PROF)} profondeur"))
    tr = M.TRAPPE
    o.append(cote_h(tr["x0"], tr["x1"], -M.Z_DESSUS - 4, cm(tr["x1"] - tr["x0"]), ext=-M.Z_DESSUS))
    o.append(PL.text(tr["x0"] - 1, -M.Z_DESSUS - 4.9, "encoche du passe-tuyau", "lt muted", "end"))
    o.append(niveaux([(M.LL["h"], f"{cm(M.LL['h'])} dessus de la machine", m.x0),
                      (M.Z_PLAN, f"{cm(M.Z_PLAN)} dessous du plan ({cm(M.JEU_PLAN * 10)} mm de jeu)", M.FACE),
                      (M.Z_DESSUS, f"{cm(M.Z_DESSUS)} dessus du plan", M.FACE)], M.FACE - 26))
    o.append(niveaux([(M.TUYAUX["evacuation_z"], f"{cm(M.TUYAUX['evacuation_z'])} siphon", M.X1 - 2),
                      (M.TUYAUX["arrivee_z"], f"{cm(M.TUYAUX['arrivee_z'])} arrivée", M.X1 - 2),
                      (rb["z"], f"{cm(rb['z'])} robinet", M.X1 - 2)], M.X1 + 10, droite=True))
    o.append(PL.text((m.x0 + m.x1) / 2, -40, "machine (coupée)", "lt"))
    o.append(PL.text(M.FACE - 8, 4.5, "salle de bain", "lt muted", "end"))
    return svg(M.FACE - 60, -h - 8, M.X1 + 36, 17, o, "Coupe par la machine")


def implantation():
    """Vue de dessus coupée à 30 du sol : où poser les échelles, les rails et la machine ; le plan en tireté."""
    zs = 30
    xg = M.X1 - M.ALCOVE["sud"] - 6
    o = [PL.rect(M.X1 - M.ALCOVE["nord"], M.Y0 - 4, M.X1 + 4, M.Y0, "omurc"),
         PL.rect(M.X1 - M.ALCOVE["sud"], M.Y1, M.X1 + 4, M.Y1 + 4, "omurc"), PL.rect(M.X1, M.Y0, M.X1 + 4, M.Y1, "omurc")]
    o += projeter([b for b in bas() if b.role not in ("sac", "barre")], "dessus", zs)
    pl = nom("plan_travail")
    o.append(PL.poly([(pl.x0, pl.y0), (pl.x1, pl.y0), (pl.x1, pl.encoche[2]), (pl.encoche[0], pl.encoche[2]),
                      (pl.encoche[0], pl.encoche[3]), (pl.x1, pl.encoche[3]), (pl.x1, pl.y1), (pl.x0, pl.y1)], "oplanl"))
    for e, y in (("n", M.Y0), ("s", M.Y1)):            # coins de calage contre les murs nord et sud
        for x in (M.XO0 + M.DL / 2, M.XO1 - M.DL / 2):
            sy = 1 if e == "n" else -1
            o.append(PL.poly([(x - 1.6, y), (x + 1.6, y), (x, y + sy * 1.4)], "ocoin"))
    rb = M.ROBINET
    o.append(f'<circle class="ovanne" cx="{f(M.X1 - 1.5)}" cy="{f(rb["y"])}" r="1.6"/>')
    o.append(cote_v(rb["y"], M.Y1, M.X1 + 9, f"{cm(M.Y1 - rb['y'])}", ext=M.X1))
    o.append(PL.text(M.X1 + 11, rb["y"] - 1.5, f"robinet (h {cm(rb['z'])})", "lt", "start"))
    e = M.ECH
    o.append(chaine_v([M.Y0, e["n"], e["n"] + M.DE, e["c"], e["c"] + M.DE, e["s"], e["s"] + M.DE, M.Y1], xg - 4,
                      ext=M.FACE))
    o.append(cote_v(M.Y0, M.Y1, xg - 12, f"{cm(M.Y1 - M.Y0)}"))
    o.append(chaine_h([M.FACE, M.XO0, M.XO0 + M.DL, M.XO1 - M.DL, M.XO1, M.X1], M.Y1 + 9, ext=M.Y1))
    o.append(cote_h(M.FACE, M.X1, M.Y1 + 16, f"{cm(M.PROF)}"))
    o.append(PL.text(M.X1 - M.ALCOVE["nord"] - 1, M.Y0 - 1.2, f"mur nord (retour de {M.ALCOVE['nord']})", "lt muted", "end"))
    o.append(PL.text(M.X1 - M.ALCOVE["sud"] - 1, M.Y1 + 3.4, f"mur sud (retour de {M.ALCOVE['sud']})", "lt muted", "end"))
    o.append(PL.text((M.XO0 + M.XO1) / 2, (M.CB["y0"] + M.CB["y1"]) / 2 + 1, "bac", "lt muted"))
    o.append(PL.text((M.MACHINE.x0 + M.MACHINE.x1) / 2, (M.LLZ["y0"] + M.LLZ["y1"]) / 2 + 1, "machine", "lt"))
    return svg(xg - 22, M.Y0 - 8, M.X1 + 34, M.Y1 + 20, o, "Implantation au sol")


def feuille():
    """Section « Cotes » de la page du meuble bas."""
    figs = [
        figure("cote-face", "C1 · Vue de face", vue_face(),
               "Depuis la salle de bain. En bas, la position des trois échelles entre les murs ; à gauche, les hauteurs "
               "depuis le sol."),
        figure("cote-dessus", "C2 · Implantation au sol (vue de dessus, coupée à 30 du sol)", implantation(),
               "Où poser les échelles, les rails et la machine. Montants coupés en foncé, lisses basses et rails vus en "
               "clair, le plan de travail en tireté avec l'encoche du passe-tuyau ; triangles : les coins de calage."),
        figure("cote-bac", "C3 · Coupe par le bac (vue vers le nord)", coupe_bac(),
               f"Le L fermé, puis ouvert à {M.BAC['angle']}° en tireté rouge : les sacs l'arrêtent là. Sans les barres "
               f"arrière, il bascule jusqu'au tire-fond de butée, à {M.BAC['angle_max']}°. Derrière : l'échelle nord, "
               "son écharpe et sa lisse de barre."),
        figure("cote-machine", "C4 · Coupe par la machine et le robinet (vue vers le nord)", coupe_machine(),
               f"La machine ne touche rien : {cm(M.JEU_PLAN * 10)} mm sous le plan, {cm(M.JEU_LL)} devant le mur du "
               "fond pour le siphon et les tuyaux ; l'arrivée monte au robinet par l'encoche du plan."),
    ]
    return ('<p>Les quatre vues à plat du meuble bas, à garder sous les yeux pendant le montage. Cotes en cm ; '
            'hauteurs (▽) mesurées depuis le sol.</p><div class="feuille">' + "".join(figs) + "</div>")


# ------------------------------------------------------------------ dessins des opérations de la notice
def echelle(butee=False):
    """Échelle nord vue de côté : cotes de découpe et d'assemblage ; avec butee, la position du tire-fond."""
    bl = [b for b in bas() if b.groupe == "ossature" and b.nom.endswith("_n") and (butee or b.role != "vis")]
    s = M.ECH["n"] + M.DE
    o = projeter(bl, "cote", s + 0.01)
    e = M.ECHELLES["n"]
    x0, x1 = M.XO0, M.XO1
    o.append(chaine_h([x0, x0 + M.DL, x1 - M.DL, x1], 6, ext=0))
    o.append(cote_h(x0, x1, 12.5, f"{cm(x1 - x0)} hors tout"))
    o.append(cote_v(-M.Z0, -M.Z_CADRE, x0 - 6, f"{cm(M.Z_CADRE - M.Z0)} montant", ext=x0))
    o.append(cote_v(0, -M.Z_CADRE, x0 - 13, f"{cm(M.Z_CADRE)} avec le vérin"))
    zs = [M.Z0, e["basse"].z1, e["barre"].z0, e["barre"].z1, M.Z_CADRE]
    o.append(chaine_v([-z for z in zs], x1 + 6, ext=x1))
    if butee:
        xb, zb = M.BAC["x_butee"], M.Z_BUTEE
        o.append(cote_h(x0, xb, -zb + 7, cm(xb - x0), ext=-zb))
        o.append(cote_v(-zb, 0, xb + 10, cm(zb), ext=xb))
        o.append(etiquette(xb, -zb, xb + 14, -zb - 10, "tire-fond 8 × 60, dépasse de 25 mm"))
    else:
        d = math.hypot(x1 - x0, M.Z_CADRE - M.Z0)
        o.append(f'<line class="odiag" x1="{f(x0)}" y1="{f(-M.Z0)}" x2="{f(x1)}" y2="{f(-M.Z_CADRE)}"/>')
        o.append(f'<line class="odiag" x1="{f(x0)}" y1="{f(-M.Z_CADRE)}" x2="{f(x1)}" y2="{f(-M.Z0)}"/>')
        o.append(PL.text(x0 + 3, -M.Z_CADRE + 14, f"diagonales : {cm(d)}", "lt", "start"))
        ec = next(b for b in bl if b.rep == "G11")
        (xa, za), _, (xc, zc), _ = ec.xz
        px, pz = xa + 0.3 * (xc - xa) + M.DE / 2, za + 0.3 * (zc - za)
        o.append(etiquette(px, -pz, x1 - 3, -M.Z0 - 14, f"écharpe G11 : bouts coupés à {90 - M.ECHARPE['coupe']:.0f}°",
                           "end"))
    return svg(x0 - 22, -M.Z_CADRE - 6, x1 + 14, 16, o, "Échelle vue de côté")


def le_l():
    """Le L vu de côté, fermé : porte, plateau, contrefiche ; cotes d'assemblage."""
    bl = [nom(n) for n in ("bac_porte", "plateau", "contrefiche_n")]
    p, pl, cf = bl
    o = projeter(bl, "cote", p.y1)
    o.append(f'<line class="ext" x1="{f(p.x0)}" y1="{f(-(p.z1 - 3))}" x2="{f(p.x1)}" y2="{f(-(p.z1 - 3))}" '
             'style="stroke-dasharray:1 .6"/>')
    o.append(cote_v(-p.z0, -p.z1, p.x0 - 6, f"{cm(p.z1 - p.z0)} porte", ext=p.x0))
    o.append(cote_v(-pl.z0, -p.z0, p.x0 - 12, "0,5", dx=-2, ext=p.x0))
    o.append(cote_h(pl.x0, pl.x1, -pl.z0 + 6, f"{cm(pl.x1 - pl.x0)} plateau", ext=-pl.z0))
    L = M.BAC["contrefiche"]
    o.append(cote_h(p.x1, p.x1 + L, -pl.z1 - L - 3, f"{L} jambe", ext=-pl.z1 - L + 2))
    o.append(cote_v(-pl.z1, -pl.z1 - L, p.x1 + L + 4, f"{L}", ext=p.x1 + L))
    o.append(PL.text(p.x1 + L / 2 + 2, -pl.z1 - L / 2 + 3, "45°", "lt", "start"))
    o.append(etiquette(p.x1 - 0.9, -(p.z1 - 3), p.x1 + 10, -(p.z1 - 3) + 2, "trou de prise Ø 25, centre à 30 mm du haut"))
    o.append(etiquette(pl.x0 + 1, -pl.z0, pl.x0 + 14, -pl.z0 + 12, "dessous du plateau 0,5 sous la porte"))
    return svg(p.x0 - 22, -p.z1 - 6, pl.x1 + 6, -pl.z0 + 15, o, "Le L vu de côté")


def dos_porte():
    """La porte vue de face (supports et charnières en tireté derrière) : où visser les supports et les charnières."""
    p, pl = nom("bac_porte"), nom("plateau")
    sup = sorted((b for b in M.PIECES if b.nom.startswith("support_porte")), key=lambda b: b.y0)
    o = [PL.rect(p.y0, -p.z1, p.y1, -p.z0, "ofac"), PL.rect(pl.y0, -pl.z1, pl.y1, -pl.z0, "ocache")]
    for b in sup:
        o.append(PL.rect(b.y0, -b.z1, b.y1, -b.z0, "ocache"))
    for y in M.CHARNIERES["y"]:
        o.append(PL.rect(y - 3, -pl.z0 - 0.3, y + 3, -pl.z0 + 0.3, "ochar"))
    o.append(f'<circle class="otrou" cx="{f((p.y0 + p.y1) / 2)}" cy="{f(-(p.z1 - 3))}" r="1.25"/>')
    o.append(chaine_h([p.y0, sup[0].y0, sup[1].y0, sup[2].y1, sup[3].y1, p.y1], -p.z1 - 4, ext=-p.z1))
    o.append(cote_v(-sup[0].z1, -p.z1, p.y1 + 5, cm(p.z1 - sup[0].z1), ext=p.y1))
    o.append(cote_v(-sup[0].z0, -sup[0].z1, p.y1 + 5, cm(sup[0].z1 - sup[0].z0), ext=p.y1))
    o.append(chaine_h([pl.y0, M.CHARNIERES["y"][0], M.CHARNIERES["y"][1], pl.y1], -pl.z0 + 6, ext=-pl.z0))
    o.append(PL.text((p.y0 + p.y1) / 2, -(p.z0 + p.z1) / 2, "porte A6 vue de face", "lt"))
    o.append(PL.text((p.y0 + p.y1) / 2, -(p.z0 + p.z1) / 2 + 3.4, "supports B1 et plateau derrière, en tireté", "lt muted"))
    o.append(PL.text((pl.y0 + pl.y1) / 2, -pl.z0 + 10.5, "axes des charnières plates (sous le plateau)", "lt muted"))
    return svg(p.y0 - 6, -p.z1 - 12, p.y1 + 14, -pl.z0 + 13, o, "Porte vue de face")


def plan_seul():
    """Le plan de travail vu de dessus, comme on le voit debout devant l'alcôve : le nord à gauche, le chant arrière
    (contre le mur du fond) en haut ; longueur, encoche du passe-tuyau."""
    pl = nom("plan_travail")
    x0, x1, y0, y1 = pl.encoche
    v = lambda x: -x            # noqa: E731  (le mur du fond en haut)
    o = [PL.poly([(pl.y0, v(pl.x0)), (pl.y0, v(pl.x1)), (y0, v(pl.x1)), (y0, v(x0)), (y1, v(x0)), (y1, v(pl.x1)),
                  (pl.y1, v(pl.x1)), (pl.y1, v(pl.x0))], "oplan")]
    o.append(cote_h(pl.y0, pl.y1, v(pl.x0) + 6, f"{cm(pl.y1 - pl.y0)} (recoupe)"))
    o.append(cote_v(v(pl.x0), v(pl.x1), pl.y0 - 5, f"{cm(pl.x1 - pl.x0)} (largeur de la tablette)"))
    o.append(chaine_h([y0, y1, pl.y1], v(pl.x1) - 4, ext=v(pl.x1)))
    o.append(cote_v(v(x1), v(x0), y0 - 4, cm(x1 - x0), ext=y0))
    o.append(PL.text(pl.y0 + 2, v(pl.x0) - 2, "bord nord", "lt muted", "start"))
    o.append(PL.text(pl.y1 - 2, v(pl.x0) - 2, "bord sud", "lt muted", "end"))
    o.append(PL.text(pl.y0 + 2, v(pl.x1) + 4, "chant arrière, contre le mur du fond", "lt muted", "start"))
    o.append(PL.text((y0 + y1) / 2, v(x0) + 4, "encoche", "lt"))
    return svg(pl.y0 - 22, v(pl.x1) - 10, pl.y1 + 6, v(pl.x0) + 11, o, "Plan de travail vu de dessus")


def mur_fond():
    """Le mur du fond vu de face, avant le meuble : réseaux à faire poser ; meuble à venir en tireté."""
    h = 136
    pr = M.PRISES
    rb = M.ROBINET
    o = [PL.rect(M.Y0, -h, M.Y1, 0, "omur"), PL.rect(M.Y0 - 4, -h, M.Y0, 0, "omurc"), PL.rect(M.Y1, -h, M.Y1 + 4, 0, "omurc"),
         f'<line class="osol" x1="{f(M.Y0 - 6)}" y1="0" x2="{f(M.Y1 + 6)}" y2="0"/>',
         PL.rect(M.YM0, -M.Z_DESSUS, M.YM1, -M.Z_PLAN, "ocache"),
         PL.rect(M.MACHINE.y0, -M.LL["h"], M.MACHINE.y1, 0, "ocache")]
    for y in M.ECH.values():
        o.append(PL.rect(y, -M.Z_PLAN, y + M.DE, -M.Z0, "ocache"))
    for b in (M.SIPHON, M.ARRIVEE):
        o.append(PL.rect(b.y0, -b.z1, b.y1, -b.z0, "otuy cut"))
    o.append(f'<circle class="ovanne" cx="{f(rb["y"])}" cy="{f(-rb["z"])}" r="1.8"/>')
    o.append(PL.rect(pr.y0, -pr.z1, pr.y1, -pr.z0, "oprise"))
    ll = M.MACHINE
    yp = (ll.y0 + ll.y1) / 2 + 12
    o.append(PL.rect(yp - 2.5, -63, yp + 2.5, -57, "oprise"))
    o.append(etiquette(yp + 2.5, -60, yp + 10, -66, "prise de la machine (20 A)"))
    o.append(etiquette(pr.y0, -(pr.z0 + pr.z1) / 2, pr.y0 - 8, -(pr.z0 + pr.z1) / 2 - 6, "prises de la niche", "end"))
    o.append(etiquette(rb["y"] - 1.8, -rb["z"], rb["y"] - 12, -rb["z"] - 4, "robinet d'arrêt", "end"))
    o.append(etiquette(M.SIPHON.y0, -M.TUYAUX["evacuation_z"], M.SIPHON.y0 - 10, -M.TUYAUX["evacuation_z"] + 8,
                       "siphon", "end"))
    o.append(cote_h(rb["y"], M.Y1, -rb["z"] - 6, cm(M.Y1 - rb["y"]), ext=-rb["z"]))
    o.append(cote_h(pr.y1, M.Y1, -pr.z1 - 4, cm(M.Y1 - pr.y1), ext=-pr.z1))
    o.append(niveaux([(M.TUYAUX["evacuation_z"], f"{cm(M.TUYAUX['evacuation_z'])} siphon", M.SIPHON.y1),
                      (M.TUYAUX["arrivee_z"], f"{cm(M.TUYAUX['arrivee_z'])} arrivée", M.ARRIVEE.y1),
                      (M.Z_DESSUS, f"{cm(M.Z_DESSUS)} dessus du plan", M.YM1),
                      (rb["z"], f"{cm(rb['z'])} robinet", rb["y"] + 1.8),
                      ((pr.z0 + pr.z1) / 2, f"{cm((pr.z0 + pr.z1) / 2)} prises", pr.y1)], M.Y1 + 9, droite=True))
    return svg(M.Y0 - 30, -h - 4, M.Y1 + 40, -46, o, "Mur du fond : réseaux")


FIGURES = {"echelle": echelle, "butee": lambda: echelle(butee=True), "le_l": le_l, "dos_porte": dos_porte,
           "plan": plan_seul, "mur_fond": mur_fond, "implantation": implantation, "coupe_bac": coupe_bac,
           "coupe_machine": coupe_machine}

CSS = """
.feuille{display:grid;grid-template-columns:minmax(0,1fr);gap:14px}
.fcote{margin:0;background:var(--panel);border:1px solid var(--line);border-radius:12px;padding:12px}
.ftitre{font:700 15px Archivo,system-ui,sans-serif;margin:0 0 6px}
svg.cotes{display:block;width:100%;height:auto;max-height:80vh;min-width:560px}
.op svg.cotes{max-height:56vh;min-width:420px}
.omur{fill:var(--tile)}.omurc{fill:var(--muted);fill-opacity:.55}
.osol{stroke:var(--ink);stroke-width:.6}
.obois{fill:var(--dg);fill-opacity:.45;stroke:var(--ink);stroke-width:.22}
.obois.cut{fill:var(--dg);fill-opacity:1;stroke-width:.3}
.ofac,.omel{fill:var(--cab);stroke:var(--ink);stroke-width:.22}.ofac.cut,.omel.cut{fill:var(--tall);stroke-width:.32}
.oplan{fill:var(--wood);fill-opacity:.5;stroke:var(--ink);stroke-width:.22}.oplan.cut{fill-opacity:1;stroke-width:.3}
.omach{fill:var(--panel);stroke:var(--ink);stroke-width:.3}.omach.cut{fill:var(--tile);stroke-width:.4}
.ohub{fill:none;stroke:var(--ink);stroke-width:.3}
.omet,.obar{fill:#B9C2C8;stroke:var(--ink);stroke-width:.2}
.osac{fill:var(--glass);fill-opacity:.25;stroke:var(--water);stroke-width:.25;stroke-dasharray:1 .6}
.otuy{fill:var(--water);fill-opacity:.55;stroke:var(--ink);stroke-width:.2}
.ovanne{fill:var(--water);stroke:var(--ink);stroke-width:.25}
.oprise{fill:var(--panel);stroke:var(--ink);stroke-width:.3}
.oswing{fill:none;stroke:var(--tri);stroke-width:.35;stroke-dasharray:1.4 .8}
.oaxe{fill:var(--tri)}
.ocache{fill:none;stroke:var(--muted);stroke-width:.25;stroke-dasharray:1.2 .8}
.oplanl{fill:none;stroke:var(--wood);stroke-width:.4;stroke-dasharray:1.6 .9}
.ocoin{fill:var(--tri)}
.ochar{fill:#B9C2C8;stroke:var(--ink);stroke-width:.2}
.otrou{fill:var(--paper);stroke:var(--ink);stroke-width:.25}
.odiag{stroke:var(--tri);stroke-width:.25;stroke-dasharray:1.2 .8}
svg.cotes .dim{stroke:var(--ink);stroke-width:.16}
svg.cotes .tick{stroke:var(--ink);stroke-width:.25}
svg.cotes .ext{stroke:var(--muted);stroke-width:.12}
svg.cotes .ct{font:600 2.5px "JetBrains Mono",ui-monospace,monospace;fill:var(--ink)}
svg.cotes .nt{font:600 2.4px "JetBrains Mono",ui-monospace,monospace;fill:var(--ink)}
svg.cotes .lt{font-size:2.5px;fill:var(--ink)}svg.cotes .lt.muted{fill:var(--muted)}
svg.cotes .lead{stroke:var(--ink);stroke-width:.14}svg.cotes .pt{fill:var(--ink)}
.niv{fill:var(--ink)}
"""
