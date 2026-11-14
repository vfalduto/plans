"""Les onze dessins du meuble bas : huit vues cotées et trois vues iso, repris à l'octet de 3d/sdb/bas.py.

Chaque dessin prend son texte alternatif (`label`, par défaut son ancien aria-label, ARIA) ; vues.py y met le texte qui
était sous le dessin dans l'ancienne page (legendes()). Les nombres du SVG sont ceux de dessin_cotes (deux décimales) ;
les cotes affichées, celles du modèle (cm). CSS_DOCUMENT réunit les règles des aides partagées puis celles du meuble
bas, qui l'emportent (.omel, .otrou).
"""
import math

from pieces.sdb import dessin_cotes as DC, iso, piece as P
from pieces.sdb.meuble_bas import modele as B
from pieces.sdb.meuble_bas.modele import (
    ARRIVEE, BAC, BAC_MAX, BOITE, BOUT_NORD, BOUT_SUD, BX0, BX1, BY0, BY1, BZ0, BZ1, CHARN_Z, COL_A, COL_B, COL_C,
    COL_H, COL_JAMBE, COL_L, COL_N, COL_TROU, COL_XY, COL_YF, CUVETTE, CUV_RIVE, CY0, DX0, DX1, EQUERRES_X, ETAGES,
    EX0, EZ0, EZ1, FENETRES, FEN_Y0, FEN_Y1, GONDS_X, GOUL, JEU_MUR, JOUES, JOUE_H, JOUE_P, JX0, JX1, JZ0, MX0, MX1,
    MY0, MY1, NY1, OUVERTURE, PLATEAU_P, POIGNEE, POI_Y, POI_Z0, POI_Z1, PORTE_L, PORTE_X0, PORTE_X1, PORTE_Y0,
    PORTE_Y1, PORTE_Z0, PORTE_Z1, PRISE, PRISES_Z, PRISE_LED_Z, PROF_LIBRE, PX0, PX1, PY0, PY1, TAPIS, TX0, TX1, TY0,
    TY1, VERIN, VERINS_X, Z_DESSOUS, Z_DESSUS, Z_MACH, cm, col_pt, contour, contour_porte,
)

# texte alternatif d'origine de chaque dessin (aria-label de l'ancienne page)
ARIA = {
    "elevation": "Élévation de l'alcôve vue depuis la salle de bain",
    "iso": "Meuble bas dans l'alcôve, porte fermée",
    "iso-ouvert": "Meuble bas sans la porte",
    "eclate": "Vue éclatée",
    "plan": "Plan de l'alcôve avec le meuble, les portes et la machine",
    "coupe": "Coupe par la machine, le mur du fond à droite",
    "placard": "Coupe par le placard, le mur du fond à droite",
    "porte": "Porte du placard vue de face",
    "joue": "Joue vue de côté",
    "colonne": "Colonne de prises vue de face",
    "colonne-dessus": "Colonne vue de dessus, dans l'angle",
}


def rect(x0, y0, x1, y1, cls):
    return f'<rect class="{cls}" x="{DC.f(x0)}" y="{DC.f(y0)}" width="{DC.f(x1 - x0)}" height="{DC.f(y1 - y0)}"/>'


def trait(x0, y0, x1, y1, cls):
    return f'<line class="{cls}" x1="{DC.f(x0)}" y1="{DC.f(y0)}" x2="{DC.f(x1)}" y2="{DC.f(y1)}"/>'


def fil(pts):
    """Tracé ouvert, sans fermer le contour."""
    return '<polyline class="ofil" points="' + " ".join(f"{DC.f(a)},{DC.f(b)}" for a, b in pts) + '"/>'


def poly_yz(pts, cls):
    return DC.poly([(y, -z) for y, z in pts], cls)


# ------------------------------------------------------------------ plan
def vue_plan(label=ARIA["plan"]):
    x_g, ep = 78, 4
    y_sud = P.SDB["p"]
    px0, px1 = P.PORTE["x0"], P.PORTE["x1"]
    lx0, ly0, lx1, ly1 = P.LAVABO
    px_, py_ = PORTE_X1, PORTE_Y0 + 0.5                # pivot approché de la porte du placard
    a = math.radians(OUVERTURE)
    ox, oy = px_ - PORTE_L * math.sin(a), py_ + PORTE_L * math.cos(a)
    o = [rect(x_g, -ep, px0, P.Y0, "omur"), rect(px1, -ep, P.X1 + ep, P.Y0, "omur"),
         rect(P.X1, -ep, P.X1 + ep, y_sud + ep, "omur"),
         rect(BOUT_SUD, P.Y1, P.X1, y_sud, "omasse"),
         rect(x_g, y_sud, P.X1 + ep, y_sud + ep, "omur"),
         rect(lx0, ly0, lx1, ly1, "oequip"), DC.text((lx0 + lx1) / 2, (ly0 + ly1) / 2 + 1, "Lavabo", "lt", "middle"),
         rect(JX0, NY1, DX0, CY0, "olibre"),
         rect(BX0, BY0, BX1, BY1, "omet"),
         DC.text((BX0 + BX1) / 2, (BY0 + BY1) / 2 - 1, "Bacs", "lt", "middle"),
         DC.text((BX0 + BX1) / 2, (BY0 + BY1) / 2 + 2.4, f'{BAC["p"]} × {BAC["l"]}', "ct", "middle"),
         rect(TX0, TY0, TX1, TY1, "omet"),
         rect(MX0, MY0, MX1, MY1, "omach"),
         DC.text((MX0 + MX1) / 2, (MY0 + MY1) / 2 - 1, "Machine", "lt", "middle"),
         DC.text((MX0 + MX1) / 2, (MY0 + MY1) / 2 + 2.4, f'{cm(P.MACHINE["l"])} × {cm(P.MACHINE["p"])}', "ct", "middle"),
         trait(GONDS_X, P.Y0, GONDS_X, P.PORTE["l"], "ovant"),
         f'<path class="oswing" d="M {px0} {P.Y0} A {P.PORTE["l"]} {P.PORTE["l"]} 0 0 0 {GONDS_X} {P.PORTE["l"]}"/>',
         DC.text(GONDS_X - 3, 66, "Porte d'entrée à 90°", "lt", "end"),
         trait(px_, py_, ox, oy, "ovant"),
         f'<path class="oswing" d="M {DC.f(PORTE_X0)} {DC.f(PORTE_Y1)} A {DC.f(PORTE_L)} {DC.f(PORTE_L)} 0 0 1 {DC.f(ox)} {DC.f(oy)}"/>',
         DC.text(ox + 1, oy + 4, "Porte du placard ouverte", "lt", "start")]
    for _, y0, y1 in JOUES:
        o.append(rect(JX0, y0, JX1, y1, "omel cut"))
    o.append(rect(DX0, NY1, DX1, CY0, "omel cut"))
    o.append(rect(PORTE_X0, PORTE_Y0, PORTE_X1, PORTE_Y1, "omel cut"))
    o.append(rect(PORTE_X0 - POIGNEE["saillie"], POI_Y - 0.6, PORTE_X0, POI_Y + 0.6, "opoi"))
    o.append(rect(PX0, PY0, PX1, PY1, "oplanl"))
    o += [DC.poly(COL_XY, "omel cut"), DC.etiquette(COL_C[0], COL_C[1], COL_C[0] - 10, COL_C[1] + 7, "Colonne", "end")]
    o += [DC.text(PX0 - 1.5, 112, "Plateau", "lt", "end"),
          DC.cote_h(px0, px1, -9, f'{P.PORTE["l"]} porte'), DC.cote_h(px1, P.X1, -9, f"{P.GONDS} gonds"),
          DC.cote_h(BOUT_NORD, P.X1, -15, f'{P.ALCOVE["nord"]} mur nord', ext=-4),
          DC.cote_v(NY1, CY0, P.X1 + 10, ext=P.X1 + ep), DC.cote_v(MY0, MY1, P.X1 + 10, ext=P.X1 + ep),
          DC.cote_v(PY0, PY1, P.X1 + 18, f"{cm(PY1 - PY0)} plateau", ext=P.X1 + ep),
          DC.cote_v(P.Y0, P.Y1, P.X1 + 26, f"{cm(P.Y1 - P.Y0)} fond", ext=P.X1 + ep),
          DC.cote_h(MX0, MX1, P.Y1 + 8, ext=MY1), DC.cote_h(MX1, P.X1, P.Y1 + 8, ext=MY1, place="droite"),
          DC.cote_h(PX0, PX1, P.Y1 + 18, f"{PLATEAU_P} plateau"),
          DC.cote_h(BOUT_SUD, P.X1, P.Y1 + 28, f'{P.ALCOVE["sud"]} mur sud'),
          DC.cote_h(GONDS_X, MX0, 80, ext=None)]
    return DC.svg(x_g - 2, -20, P.X1 + 32, y_sud + ep + 2, o, label)


# ------------------------------------------------------------------ élévation vue depuis la salle de bain
def vue_face(label=ARIA["elevation"]):
    ep, r = 4, P.ROBINET
    t = P.TUYAUX
    o = [rect(P.Y0 - ep, -P.H - ep, P.Y0, ep, "omur"), rect(P.Y1, -P.H - ep, P.Y1 + ep, ep, "omur"),
         rect(P.Y0, -P.H - ep, P.Y1, -P.H, "omur"), rect(P.Y0, 0, P.Y1, ep, "omur"),
         trait(P.Y0, -P.CARRELAGE, P.Y1, -P.CARRELAGE, "ocarr"),
         rect(P.Y0 + 0.5, -B.Z_HAUT1, P.Y1 - 0.5, -B.Z_HAUT, "oequip"),
         DC.text((P.Y0 + P.Y1) / 2, -(B.Z_HAUT + B.Z_HAUT1) / 2, "Meuble haut", "lt", "middle"),
         rect(MY0, -Z_MACH, MY1, -TAPIS["ep"], "omach"), rect(TY0, -TAPIS["ep"], TY1, 0, "omet"),
         DC.text((MY0 + MY1) / 2, -Z_MACH / 2 - 8, "Machine", "lt", "middle"),
         f'<circle class="ocache" cx="{r["y"]}" cy="{-t["evacuation_z"]}" r="3"/>',
         f'<line class="ocache" x1="{r["y"]}" y1="{-t["arrivee_z"]}" x2="{r["y"]}" y2="{-r["z"]}"/>',
         f'<circle class="ovanne" cx="{r["y"]}" cy="{-r["z"]}" r="1.2"/>',
         DC.etiquette(r["y"], -r["z"], r["y"] + 8, -r["z"] - 4, f'Robinet à {r["z"]}')]
    for _, y0, y1 in JOUES:
        o.append(rect(y0, -Z_DESSOUS, y1, -JZ0, "omel cut"))
        o.append(rect((y0 + y1 - VERIN["d"]) / 2, -JZ0, (y0 + y1 + VERIN["d"]) / 2, 0, "omet"))
    o += [poly_yz(contour(FENETRES[1], True), "otrou"), poly_yz(contour_porte(), "omel"), poly_yz(contour(FENETRES[0]), "otrou")]
    o += [rect(NY1, -EZ1, CY0, -EZ0, "ocache"), rect(NY1, -BZ1, CY0, -BZ0, "ocache")]
    o += [rect(BY0, -(e + BAC["h"]), BY1, -e, "ocache") for e in ETAGES]
    o.append(rect(POI_Y - 0.6, -POI_Z1, POI_Y + 0.6, -POI_Z0, "opoi"))
    o.append(rect(PY0, -Z_DESSUS, PY1, -Z_DESSOUS, "oplan cut"))
    o += [rect(COL_YF, -(Z_DESSUS + COL_H), COL_B[1], -Z_DESSUS, "omel"), DC.etiquette(COL_B[1], -125, COL_B[1] + 10, -130, "Colonne")]
    o += [DC.cote_h(PORTE_Y0, PORTE_Y1, 11, ext=ep), DC.cote_h(MY0, MY1, 11, ext=ep),
          DC.cote_h(P.Y0, P.Y1, 18, f"{cm(P.Y1 - P.Y0)} fond", ext=ep),
          DC.niveaux([(Z_MACH, f"{cm(Z_MACH)} machine", P.Y0), (Z_DESSUS, f"{cm(Z_DESSUS)} plateau", P.Y0), (B.Z_HAUT, None, P.Y0),
                      (P.CARRELAGE, f"{P.CARRELAGE} carrelage", P.Y0), (P.H, f"{P.H} plafond", P.Y0)], P.Y0 - ep - 3),
          DC.cote_v(-B.Z_HAUT, -Z_DESSUS, P.Y1 - 0.6)]
    return DC.svg(-34, -P.H - ep - 2, P.Y1 + ep + 2, 22, o, label)


# ------------------------------------------------------------------ porte vue de face
def vue_porte(label=ARIA["porte"]):
    y0, y1 = PORTE_Y0, PORTE_Y1
    o = [trait(y0 - 6, 0, y1 + 6, 0, "ocarr"), poly_yz(contour_porte(), "omel"), poly_yz(contour(FENETRES[0]), "otrou")]
    for z in CHARN_Z:
        o.append(f'<circle class="ocache" cx="{DC.f(y0 + CUV_RIVE - CUVETTE / 2)}" cy="{DC.f(-z)}" r="{CUVETTE / 2}"/>')
    o += [rect(POI_Y - 0.6, -POI_Z1, POI_Y + 0.6, -POI_Z0, "opoi"),
                    DC.etiquette(y0 + CUV_RIVE - CUVETTE / 2, -CHARN_Z[0], y0 + 12, -CHARN_Z[0] - 5, "Charnière"),
          DC.etiquette(POI_Y, -(POI_Z0 + POI_Z1) / 2, y1 - 16, -(POI_Z0 + POI_Z1) / 2 - 5, "Poignée", "end"),
          DC.cote_h(y0, FEN_Y0, 6, ext=0, place="gauche"), DC.cote_h(FEN_Y0, FEN_Y1, 6, ext=0), DC.cote_h(FEN_Y1, y1, 6, ext=0, place="droite"),
          DC.cote_h(y0, y1, 13, ext=0),
          DC.cote_v(-PORTE_Z1, -PORTE_Z0, y0 - 12),
          DC.niveaux([(FENETRES[0][2], cm(FENETRES[0][2]), y1), (FENETRES[0][3], cm(FENETRES[0][3]), y1), (FENETRES[1][2], cm(FENETRES[1][2]), y1), (PORTE_Z1, cm(PORTE_Z1), y1)], y1 + 3, droite=True)]
    return DC.svg(y0 - 20, -PORTE_Z1 - 4, y1 + 22, 19, o, label)


# ------------------------------------------------------------------ coupe par le placard
def vue_placard(label=ARIA["placard"]):
    ep = 4
    z_f = [PORTE_Z0, FENETRES[0][2], FENETRES[0][3], FENETRES[1][2]]        # bois de la porte : sous chaque découpe
    o = [rect(P.X1, -Z_DESSUS - 6, P.X1 + ep, ep, "omur"), rect(PX0 - 14, 0, P.X1, ep, "omur"),
         rect(JX0, -Z_DESSOUS, JX1, -JZ0, "omel"),
         rect(EX0, -EZ1, DX0, -EZ0, "omel cut"), rect(EX0, -BZ1, DX0, -BZ0, "omel cut"), rect(DX0, -Z_DESSOUS, DX1, -JZ0, "omel cut"),
         rect(PX0, -Z_DESSUS, PX1, -Z_DESSOUS, "oplan cut")]
    for a, b in zip(z_f[::2], z_f[1::2]):
        o.append(rect(PORTE_X0, -b, PORTE_X1, -a, "omel cut"))
    o.append(rect(PORTE_X0 - POIGNEE["saillie"], -POI_Z1, PORTE_X0, -POI_Z0, "opoi"))
    for i, e in enumerate(ETAGES):
        o += [rect(BX0, -(e + BAC["h"]), BX1, -e, "olibre"),
              DC.text((BX0 + BX1) / 2, -e - BAC["h"] / 2 + 1, f'Bac {i + 1}', "lt", "middle"),
              trait(PORTE_X0, -(e + BAC_MAX), JX1, -(e + BAC_MAX), "otq"),
              DC.cote_v(-(e + BAC["h"]), -e, BX1 - 4, cm(BAC["h"]))]
    xg = DX0 - GOUL / 2
    o += [fil([(ARRIVEE["x"], -ARRIVEE["z"]), (xg, -ARRIVEE["z"]), (xg, -Z_DESSUS)]),
          DC.etiquette(ARRIVEE["x"], -ARRIVEE["z"], ARRIVEE["x"] - 3, -ARRIVEE["z"], "Sortie du câble", "end")]
    o += [DC.cote_h(JX0, DX0, 11, cm(PROF_LIBRE), ext=ep), DC.cote_h(PX0, PX1, 18, f"{PLATEAU_P} plateau", ext=ep),
          DC.niveaux([(BZ1, f"{cm(BZ1)} bas", P.X1), (ETAGES[0] + BAC_MAX, f"{cm(ETAGES[0] + BAC_MAX)} 3/4", P.X1), (EZ0, f"{cm(EZ0)} étagère", P.X1), (EZ1, f"{cm(EZ1)}", P.X1),
                      (EZ1 + BAC_MAX, f"{cm(EZ1 + BAC_MAX)} 3/4", P.X1), (Z_DESSOUS, f"{cm(Z_DESSOUS)} plateau", P.X1)], P.X1 + ep + 3, droite=True)]
    return DC.svg(PX0 - 16, -Z_DESSUS - 8, P.X1 + ep + 28, 22, o, label)


# ------------------------------------------------------------------ colonne vue de face
def vue_colonne(label=ARIA["colonne"]):
    d = PRISE["plaque"] / 2
    zc = Z_DESSUS + COL_H
    u0, u1 = 0, COL_L
    uc = COL_L / 2
    o = [rect(u0 - 10, -B.Z_HAUT - 6, u1 + 10, -B.Z_HAUT, "oequip"), DC.text(uc, -B.Z_HAUT - 2, "Meuble haut", "lt", "middle"),
         rect(u0 - 10, -Z_DESSUS, u1 + 10, -Z_DESSOUS, "oplan cut"),
         rect(u0, -zc, u1, -Z_DESSUS, "omel")]
    for z in PRISES_Z + (PRISE_LED_Z,):
        o += [rect(uc - d, -z - d, uc + d, -z + d, "omel"), f'<circle class="ocache" cx="{DC.f(uc)}" cy="{DC.f(-z)}" r="2"/>']
    o += [fil([(uc, -PRISE_LED_Z), (uc, -PRISE_LED_Z - d - 1), (u0 + 1, -PRISE_LED_Z - d - 1), (u0 + 1, -B.Z_HAUT + 0.6), (u0 - 10, -B.Z_HAUT + 0.6)]),
          DC.etiquette(u0 + 1, -PRISE_LED_Z - 7, u0 - 8, -PRISE_LED_Z - 3, "Fil des LED", "end"),
          fil([(uc + 3, -Z_DESSOUS + 8), (uc + 3, -PRISES_Z[0])]),
          DC.etiquette(uc + 3, -Z_DESSOUS + 5, u0 - 8, -Z_DESSOUS + 5, "Alimentation", "end"),
          DC.cote_h(u0, u1, -Z_DESSOUS + 14, cm(COL_L), ext=-Z_DESSUS),
          DC.cote_v(-zc, -Z_DESSUS, u0 - 14, cm(COL_H)),
          DC.niveaux([(z, cm(z), u1) for z in (Z_DESSUS,) + PRISES_Z + (PRISE_LED_Z, B.Z_HAUT)], u1 + 13, droite=True)]
    return DC.svg(u0 - 34, -B.Z_HAUT - 8, u1 + 28, -Z_DESSOUS + 20, o, label)


def vue_colonne_dessus(label=ARIA["colonne-dessus"]):
    x_m, y_m = P.X1 + 3, COL_B[1] + 5
    b0, b1 = col_pt(0.5 - BOITE["d"] / 2 / COL_L), col_pt(0.5 + BOITE["d"] / 2 / COL_L)
    n = BOITE["prof"]
    boite = [b0, b1, (b1[0] + n * COL_N[0], b1[1] + n * COL_N[1]), (b0[0] + n * COL_N[0], b0[1] + n * COL_N[1])]
    p = PRISE["plaque"] / 2 / COL_L
    o = [rect(COL_A[0] - 5, -3, x_m, P.Y0, "omur"), rect(P.X1, P.Y0, x_m, y_m, "omur"),
         DC.poly(COL_XY, "omel cut"), DC.poly(boite, "ocache"),
         trait(*col_pt(0.5 - p), *col_pt(0.5 + p), "ovant"),
         f'<circle class="pt" cx="{DC.f(COL_TROU["x"])}" cy="{DC.f(COL_TROU["y"])}" r="{COL_TROU["d"] / 2}"/>',
         DC.text(COL_C[0] - 5, COL_C[1] + 3, "Prises", "lt", "end"),
         DC.cote_h(COL_A[0], P.X1 - JEU_MUR, y_m + 2, cm(COL_JAMBE), ext=None),
         DC.cote_v(P.Y0 + JEU_MUR, COL_B[1], COL_A[0] - 14, cm(COL_JAMBE), ext=None)]
    return DC.svg(COL_A[0] - 28, -6, x_m + 28, y_m + 8, o, label)


# ------------------------------------------------------------------ joue vue de côté
def vue_joue(label=ARIA["joue"]):
    ep = 4
    o = [rect(P.X1, -Z_DESSUS - 6, P.X1 + ep, ep, "omur"), rect(PX0 - 6, 0, P.X1, ep, "omur"),
         rect(JX0, -Z_DESSOUS, JX1, -JZ0, "omel"),
         rect(PX0, -Z_DESSUS, PX1, -Z_DESSOUS, "oplan cut"),
         rect(VERINS_X[0] - VERIN["d"] / 2, -JZ0, VERINS_X[0] + VERIN["d"] / 2, 0, "omet"),
         rect(VERINS_X[1] - VERIN["d"] / 2, -JZ0, VERINS_X[1] + VERIN["d"] / 2, 0, "omet"),
         DC.text((JX0 + JX1) / 2, -Z_DESSOUS / 2, f"Joue {cm(JOUE_H)} × {cm(JOUE_P)}", "lt", "middle"),
         DC.etiquette(VERINS_X[0], -1, VERINS_X[0] + 7, -12, "Vérin"),
         DC.cote_h(PX0, JX0, 11, ext=ep, place="gauche"), DC.cote_h(JX0, JX1, 11, ext=ep),
         DC.cote_h(PX0, PX1, 18, f"{PLATEAU_P} plateau", ext=ep),
         DC.cote_v(-Z_DESSOUS, -JZ0, JX0 - 3, cm(JOUE_H)),
         DC.niveaux([(Z_DESSOUS, f"{cm(Z_DESSOUS)} dessous", P.X1), (Z_DESSUS, f"{cm(Z_DESSUS)} dessus", P.X1)],
                    P.X1 + ep + 3, droite=True)]
    for x in EQUERRES_X:      # équerres sous le plateau
        o.append(rect(x - 1.75, -Z_DESSOUS, x + 1.75, -Z_DESSOUS + 5, "omet"))
    return DC.svg(PX0 - 16, -Z_DESSUS - 8, P.X1 + ep + 28, 22, o, label)


# ------------------------------------------------------------------ coupe par la machine
def vue_coupe(label=ARIA["coupe"]):
    ep, r, t = 4, P.ROBINET, P.TUYAUX
    hx0 = P.X1 - 45
    x_g = GONDS_X - 12
    o = [rect(P.X1, -P.H - ep, P.X1 + ep, ep, "omur"), rect(x_g, -P.H - ep, P.X1, -P.H, "omur"),
         rect(x_g, 0, P.X1, ep, "omur"),
         trait(P.X1, -P.CARRELAGE, P.X1 + ep, -P.CARRELAGE, "ocarr"),
         trait(GONDS_X, 0, GONDS_X, -204, "ovant"), DC.text(GONDS_X - 1.5, -196, "Vantail", "lt", "end"),
         rect(hx0, -B.Z_HAUT1, P.X1, -B.Z_HAUT, "oequip"),
         DC.text((hx0 + P.X1) / 2, -(B.Z_HAUT + B.Z_HAUT1) / 2, "Meuble haut", "lt", "middle"),
         rect(TX0, -TAPIS["ep"], TX1, 0, "omet"),
         rect(MX0, -Z_MACH, MX1, -TAPIS["ep"], "omach cut"),
         DC.text((MX0 + MX1) / 2, -Z_MACH / 2, "Machine", "lt", "middle"),
         rect(PX0, -Z_DESSUS, PX1, -Z_DESSOUS, "oplan cut"),
         rect(P.X1 - 4, -t["evacuation_z"] - 3, P.X1, -t["evacuation_z"] + 3, "otuy"),
         trait(P.X1 - 1, -t["arrivee_z"], P.X1 - 1, -r["z"], "ocache"),
         f'<circle class="ovanne" cx="{P.X1 - 1}" cy="{-r["z"]}" r="1.2"/>',
         DC.cote_h(GONDS_X, MX0, 11, ext=ep), DC.cote_h(MX0, MX1, 11, ext=ep), DC.cote_h(MX1, P.X1, 11, ext=ep),
         DC.cote_h(GONDS_X, P.X1, 18, f"{P.GONDS} gonds", ext=ep),
         DC.niveaux([(t["evacuation_z"], f'{t["evacuation_z"]} siphon', P.X1), (t["arrivee_z"], f'{t["arrivee_z"]} arrivée', P.X1),
                     (Z_DESSUS, f"{cm(Z_DESSUS)} plateau", P.X1), (r["z"], f'{r["z"]} robinet', P.X1), (B.Z_HAUT, None, P.X1),
                     (P.CARRELAGE, f"{P.CARRELAGE} carrelage", P.X1), (P.H, f"{P.H} plafond", P.X1)],
                    P.X1 + ep + 3, droite=True)]
    return DC.svg(x_g - 8, -P.H - ep - 2, P.X1 + ep + 26, 22, o, label)


# ------------------------------------------------------------------ vues iso
def iso_ferme(label=ARIA["iso"]):
    return iso.dessin(B.blocs(), murs=True, reperes=False, carrelage=P.CARRELAGE, titre=label)


def iso_ouvert(label=ARIA["iso-ouvert"]):
    return iso.dessin([b for b in B.blocs() if b.groupe != "porte"], murs=True, reperes=False, carrelage=P.CARRELAGE,
                      titre=label)


def eclate(label=ARIA["eclate"]):
    return iso.dessin([b for b in B.blocs() if b.groupe != "colonne"], reperes=False,
                      decale={"plateau": (0, 0, 35), "machine": (-80, 75, 0), "porte": (-40, 0, 0)}, titre=label)


# ------------------------------------------------------------------ les onze, dans l'ordre des boutons de Plans
NOMS = {"elevation": "Élévation, vue depuis la salle de bain", "iso": "Vue iso", "iso-ouvert": "Sans la porte",
        "eclate": "Vue éclatée", "plan": "Plan", "coupe": "Coupe par la machine", "placard": "Coupe par le placard",
        "porte": "Porte vue de face", "joue": "Joue vue de côté", "colonne": "Colonne vue de face",
        "colonne-dessus": "Colonne vue de dessus"}
DESSINS = {"elevation": vue_face, "iso": iso_ferme, "iso-ouvert": iso_ouvert, "eclate": eclate, "plan": vue_plan,
           "coupe": vue_coupe, "placard": vue_placard, "porte": vue_porte, "joue": vue_joue, "colonne": vue_colonne,
           "colonne-dessus": vue_colonne_dessus}
ISO = ("iso", "iso-ouvert", "eclate")


def legendes():
    """Les textes qui étaient sous les dessins de l'ancienne page (HTML), par repère ; vues.py en fait les textes
    alternatifs."""
    return {
        "placard": "Le mur du fond à droite. En pointillé, les 3/4 de chaque étage : les bacs restent dessous, les découpes "
                   "de la porte partent de là. En tirets rouges, le câble de la colonne, le long de la joue nord ; sa "
                   "sortie est dessinée à titre d'exemple, à relever.",
        "porte": "Le nord à gauche. Les charnières côté mur, la poignée côté machine.",
        "joue": f"Le mur du fond à droite. Deux équerres sous le plateau. Le bas de la joue est à {cm(JZ0)} du sol.",
        "colonne": "Vue perpendiculairement au panneau. Le fil des LED et l'alimentation, en tirets rouges, passent "
                   "derrière.",
        "colonne-dessus": f"Dans l'angle. En tirets, la boîte de {cm(BOITE['d'] * 10)} × {cm(BOITE['prof'] * 10)} mm, "
                          "qui tient derrière le panneau. Le point marque le trou du plateau.",
        "plan": f"Le nord en haut. La machine est à {cm(B.JEU_FOND)} du mur du fond et à {cm(B.JEU_SUD)} du mur sud. "
                f"Panneaux en coupe, contour du plateau en tirets. La porte d'entrée, ouverte à 90°, passe à "
                f"{cm(B.DEVANT_PORTE)} de la porte du placard fermée.",
        "elevation": "Le nord à gauche, le sud à droite. En tirets, le bas, l'étagère, les bacs et les réseaux derrière la "
                     "machine. Sous chaque joue, ses vérins.",
        "coupe": "Le mur du fond à droite, vu vers le nord.",
        "iso-ouvert": "Sans la porte : le bas, l'étagère, les deux bacs et le fond.",
        "eclate": "Vue éclatée : le plateau levé, la porte sortie vers l'avant, la machine et son tapis aussi. La colonne "
                  "n'est pas dessinée ici.",
    }


# règles du meuble bas (3d/sdb/bas.py), après celles des aides : .omel et .otrou l'emportent
CSS = """
.olibre{fill:var(--water);fill-opacity:.12;stroke:var(--water);stroke-width:.25;stroke-dasharray:1.4 .8}
.omasse{fill:#E9EEF0;stroke:var(--ink);stroke-width:.25}
.oequip{fill:var(--panel);stroke:var(--muted);stroke-width:.25}
.ovant{stroke:var(--tri);stroke-width:.6}
.ocarr{stroke:var(--water);stroke-width:.25;stroke-dasharray:1.4 .8}
.omel{fill:#fbfaf5;stroke:var(--ink);stroke-width:.25}.omel.cut{fill:#dedbd0;stroke-width:.35}
.otrou{fill:var(--ink);fill-opacity:.62;stroke:var(--ink);stroke-width:.25}
.opoi{fill:var(--muted);stroke:var(--ink);stroke-width:.2}
.ofil{fill:none;stroke:var(--tri);stroke-width:.35;stroke-dasharray:1.2 .8}
.otq{stroke:var(--tri);stroke-width:.3;stroke-dasharray:1.6 .9}
"""
CSS_DOCUMENT = "\n".join((DC.CSS, iso.CSS, CSS))
