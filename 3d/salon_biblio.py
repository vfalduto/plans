# Rendu Blender (Cycles) de la bibliothèque du mur ouest du salon, trois systèmes (salon-bibliotheque.html).
# La scène est construite directement dans Blender à partir des cotes du plan (variante B du salon) ;
# matériaux, ciel, soleil et réglages Cycles viennent de 3d/rendu.py.
# Lancement (sans interface) :
#   /Applications/Blender.app/Contents/MacOS/Blender -b --python 3d/salon_biblio.py -- [échantillons] [V S U]
#   ex. : ... -- 32 U   (aperçu rapide de l'USM Haller)
# Produit dans 3d/sortie/ : salon-biblio-<V|S|U>.png et salon-biblio-<V|S|U>.blend.
# Coordonnées du plan : x vers l'est depuis le mur ouest, y vers le sud depuis le mur nord, z depuis le sol (cm).

import math
import os
import random
import sys

import bpy

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import rendu as R  # noqa: E402

args = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
SAMPLES = next((int(a) for a in args if a.isdigit()), 256)
SYSTEMES = [a for a in args if a in ("V", "S", "U")] or ["V", "S", "U"]
R.SAMPLES = SAMPLES
R.ESSENCE = "chene"                        # bois du salon : chêne miel (étagères String, table, chaises)
R.LAMPES = ("suspension",)
# matin d'été : le soleil entre par la baie est et éclaire le mur ouest
R.SUN_ALT, R.SUN_AZ = R.position_soleil(*R.LIEU, 2026, 6, 21, 10, 0, R.UTC_DECALAGE)
R.EXPOSITION = 0.5

R.MATS.update({
    "vitsoe":     ("#E6E3DC", 0.45, {}),                       # Vitsoe off-white, acier laqué
    "usm":        ("#4A6A86", 0.3, {"laque": True}),           # USM bleu acier, tôle laquée
    "string_fil": ("#1E1E20", 0.45, {"metal": False}),          # montants String laqués noir
    "canape":     ("#C9BFAE", 0.95, {}),                        # housse lin écru
    "pierre":     ("#7D7A74", 0.6, {}),
    "livre_d":    ("#E4DCCB", 0.85, {}),
    "livre_e":    ("#34383C", 0.8, {}),
    "livre_f":    ("#7C8A5E", 0.8, {}),
    "livre_g":    ("#B4553A", 0.8, {}),
})
LIVRES = ["livre_a", "livre_b", "livre_c", "livre_d", "livre_e", "livre_f", "livre_g", "livre_d", "livre_c"]
LISSES = {"chrome", "globe", "string_fil", "noir"}             # cylindres et sphères : lissés, sans chanfrein

L, CEIL = 258, 250
VUE = dict(loc=(410, 335, R.DEBOUT), target=(0, 120, R.DEBOUT), lens=20)
OUT = R.OUT


# ------------------------------------------------------------------ primitives (cm du plan)

def box(mat, name, x0, x1, y0, y1, z0, z1):
    bpy.ops.mesh.primitive_cube_add(size=1)
    o = bpy.context.object
    o.name = f"{mat}__{name}"
    o.location = R.p((x0 + x1) / 2, (y0 + y1) / 2, (z0 + z1) / 2)
    o.scale = (abs(x1 - x0) / 100, abs(y1 - y0) / 100, abs(z1 - z0) / 100)
    bpy.ops.object.transform_apply(scale=True)
    return o


def tube(mat, name, a, b, r):
    """Cylindre de rayon r (cm) entre deux points du plan a et b."""
    va, vb = R.p(*a), R.p(*b)
    d = vb - va
    bpy.ops.mesh.primitive_cylinder_add(vertices=16, radius=r / 100, depth=d.length, location=(va + vb) / 2)
    o = bpy.context.object
    o.name = f"{mat}__{name}"
    o.rotation_euler = d.to_track_quat("Z", "Y").to_euler()
    return o


def boule(mat, name, c, r):
    bpy.ops.mesh.primitive_uv_sphere_add(segments=20, ring_count=10, radius=r / 100, location=R.p(*c))
    o = bpy.context.object
    o.name = f"{mat}__{name}"
    return o


def livres(nom, x_fond, prof, y0, y1, z, hmax, taux, graine):
    """Rangée de livres posés sur une tablette (dos vers l'est), d'y0 à y1 ; quelques piles couchées."""
    rnd = random.Random(graine)
    y = y0 + rnd.uniform(0.5, 4)
    fin = y0 + (y1 - y0) * taux
    i = 0
    while y < fin:
        if rnd.random() < 0.08 and fin - y > 26:       # pile couchée
            n = rnd.randint(3, 5)
            zz = z
            for k in range(n):
                e = rnd.uniform(2.0, 3.5)
                d = rnd.uniform(15, min(prof, 22))
                box(rnd.choice(LIVRES), f"{nom}_{i}_{k}", x_fond, x_fond + d, y, y + rnd.uniform(18, 24), zz, zz + e)
                zz += e
            y += 26
            i += 1
            continue
        e = rnd.uniform(1.8, 4.6)
        h = min(rnd.uniform(18, 30), hmax - 1)
        d = min(rnd.uniform(13, 22), prof)
        box(rnd.choice(LIVRES), f"{nom}_{i}", x_fond, x_fond + d, y, y + e, z, z + h)
        y += e + (rnd.uniform(0.0, 0.3))
        i += 1
        if rnd.random() < 0.06:
            y += rnd.uniform(6, 14)                          # trou dans la rangée


# ------------------------------------------------------------------ pièce

def piece():
    # sol, plafond, murs (épaisseurs du relevé)
    box("sol_bois", "sol", 0, 544, 0, 358, -2, 0)
    box("plafond", "plafond", -10, 556, -12, 370, CEIL, CEIL + 2)
    box("mur", "nord", -10, 556, -12, 0, 0, CEIL)
    box("mur", "sud", -10, 556, 358, 370, 0, CEIL)
    box("mur", "ouest_1", -10, 0, 0, 268, 0, CEIL)
    box("mur", "ouest_2", -10, 0, 343, 358, 0, CEIL)
    box("mur", "ouest_linteau", -10, 0, 268, 343, 204, CEIL)
    box("mur", "couloir", -130, -120, 258, 360, 0, CEIL)        # fond du couloir vu par le passage
    box("sol_bois", "sol_couloir", -130, 0, 258, 360, -2, 0)
    box("plafond", "plafond_couloir", -130, -10, 248, 370, CEIL, CEIL + 2)
    box("mur", "couloir_n", -130, -10, 248, 258, 0, CEIL)
    box("mur", "couloir_s", -130, -10, 353, 363, 0, CEIL)
    # cadre du passage (chambranle peint)
    box("porte_peinte", "cadre_n", -11, 1.5, 258, 268, 0, 204)
    box("porte_peinte", "cadre_s", -11, 1.5, 343, 353, 0, 204)
    box("porte_peinte", "cadre_h", -11, 1.5, 258, 353, 204, 214)
    # mur est : allège nulle, baie coulissante de 202 (y 72 → 274), h 215
    box("mur", "est_1", 544, 556, 0, 72, 0, CEIL)
    box("mur", "est_2", 544, 556, 274, 358, 0, CEIL)
    box("mur", "est_linteau", 544, 556, 72, 274, 215, CEIL)
    box("alu", "baie_dormant_h", 546, 552, 72, 274, 210, 215)
    box("alu", "baie_dormant_b", 546, 552, 72, 274, 0, 4)
    for y in (72, 171, 268):
        box("alu", f"baie_montant_{y}", 546, 552, y, y + 6, 4, 210)
    box("verre", "baie_vitre_1", 548.7, 549.3, 78, 171, 4, 210)
    box("verre", "baie_vitre_2", 548.7, 549.3, 177, 268, 4, 210)
    # plinthes
    box("porte_peinte", "plinthe_n", 0, 544, 0, 1, 0, 7)
    box("porte_peinte", "plinthe_s", 0, 544, 357, 358, 0, 7)


def mobilier():
    # table 160 × 90 en chêne, plateau à 75
    box("table", "plateau", 115, 205, 70, 230, 72, 75)
    for x, y in [(119, 74), (196, 74), (119, 221), (196, 221)]:
        box("table", f"pied_{x}_{y}", x, x + 5, y, y + 5, 0, 72)
    # chaises (dossier côté extérieur)
    for y in (75, 128, 181):
        for x0, dos in ((67, 67), (209, 249)):
            n = f"chaise_{x0}_{y}"
            box("chaise", n + "_assise", x0, x0 + 44, y, y + 44, 43, 46)
            for dx, dy in ((2, 2), (39, 2), (2, 39), (39, 39)):
                box("chaise", f"{n}_pied_{dx}_{dy}", x0 + dx, x0 + dx + 3, y + dy, y + dy + 3, 0, 43)
            box("chaise", n + "_dos", dos, dos + 4, y + 2, y + 42, 62, 82)
            box("chaise", n + "_dos_m1", dos, dos + 3, y + 2, y + 5, 46, 62)
            box("chaise", n + "_dos_m2", dos, dos + 3, y + 39, y + 42, 46, 62)
    # suspension au-dessus de la table
    boule("globe", "suspension", (160, 150, 168), 14)
    tube("noir", "suspension_fil", (160, 150, 182), (160, 150, CEIL), 0.3)
    # canapé SÖDERHAMN 198 × 99, dos à la table, tourné vers la baie
    box("canape", "socle", 285, 384, 76, 274, 8, 38)
    box("canape", "dos", 285, 301, 82, 268, 38, 83)
    box("canape", "accoudoir_n", 285, 384, 76, 82, 38, 60)
    box("canape", "accoudoir_s", 285, 384, 268, 274, 38, 60)
    for i in range(3):
        y0 = 82 + i * 62
        box("canape", f"assise_{i}", 301, 384, y0 + 0.5, y0 + 61.5, 38, 46)
        box("canape", f"coussin_dos_{i}", 301, 318, y0 + 1, y0 + 61, 46, 80)
    for x, y in [(287, 78), (380, 78), (287, 270), (380, 270)]:
        box("noir", f"canape_pied_{x}_{y}", x, x + 2, y, y + 2, 0, 8)
    # table basse et fauteuil
    box("table", "table_basse", 427, 477, 125, 225, 36, 40)
    for x, y in [(429, 127), (473, 127), (429, 221), (473, 221)]:
        box("table", f"tb_pied_{x}_{y}", x, x + 2, y, y + 2, 0, 36)
    box("canape", "fauteuil", 430, 510, 15, 95, 8, 42)
    box("canape", "fauteuil_dos", 430, 510, 15, 33, 42, 78)


# ------------------------------------------------------------------ systèmes

def vitsoe():
    tracks = [3.5, 94.7, 185.9, 252.6]
    for t in tracks:
        box("alu", f"etrack_{t}", 0, 1.6, t - 1.2, t + 1.2, 12, 240)
    for j, (t0, t1) in enumerate(zip(tracks, tracks[1:])):
        y0, y1 = t0 + 1.4, t1 - 1.4
        # armoire 36 × 36, dessus à 74, deux portes coulissantes
        box("vitsoe", f"armoire_{j}", 1.6, 36, y0, y1, 38, 74)
        ym = (y0 + y1) / 2
        box("vitsoe", f"porte_{j}_a", 36, 37.4, y0 + 0.3, ym + 1, 38.5, 73.5)
        box("vitsoe", f"porte_{j}_b", 37.4, 38.8, ym - 1, y1 - 0.3, 38.5, 73.5)
        for i, z in enumerate([104, 136, 168, 200, 232]):
            # tablette en tôle pliée : plateau, retour avant de 2,4
            box("vitsoe", f"tablette_{j}_{i}", 1.6, 23.6, y0, y1, z, z + 0.3)
            box("vitsoe", f"tablette_{j}_{i}_retour", 23.3, 23.6, y0, y1, z - 2.1, z + 0.3)
            if z < 232:
                livres(f"livre_v{j}{i}", 2, 21, y0, y1, z + 0.3, 31, 0.6 + 0.12 * ((i + j) % 3), 100 + 10 * j + i)
    return [
        dict(cadre=(4, 30, 112, 140, 74, 104), modele="ceramic_vase_04"),
        dict(cadre=(4, 30, 205, 235, 200.3, 230), modele="potted_plant_04"),
    ]


def string():
    panneaux = [0, 79.5, 159, 238.5]
    for k, y in enumerate(panneaux):
        yc = y + 0.75
        for x in (0.6, 29.4):
            tube("string_fil", f"montant_{k}_{x}", (x, yc, 0), (x, yc, 200), 0.35)
        for z in [1] + list(range(8, 200, 8)) + [199.6]:
            tube("string_fil", f"barreau_{k}_{z}", (0.6, yc, z), (29.4, yc, z), 0.25)
    for j in range(3):
        y0, y1 = panneaux[j] + 1.5, panneaux[j + 1]
        # tablettes 78 × 30 en chêne (1,5), retours d'appui sur les barreaux
        for i, z in enumerate([10, 106, 138, 170, 198]):
            box("etagere", f"tablette_{j}_{i}", 0, 30, y0, y1, z - 1.5, z)
            if z < 198:
                hmax = 26 if z == 170 else 30
                livres(f"livre_s{j}{i}", 1, 28, y0, y1, z, hmax, 0.55 + 0.13 * ((i + j) % 3), 200 + 10 * j + i)
        # armoire à abattant 78 × 30 × 37, dessus à 74
        box("etagere", f"armoire_{j}", 0, 30, y0, y1, 37, 74)
        box("etagere", f"abattant_{j}", 30, 31.2, y0 + 0.3, y1 - 0.3, 37.3, 73.7)
    return [
        dict(cadre=(4, 26, 160, 190, 74, 104), modele="ceramic_vase_04"),
        dict(cadre=(2, 18, 240, 257, 0, 70), modele="potted_plant_04", ajuste="hauteur"),
    ]


def usm():
    cols = [1, 76, 151, 201, 251]                 # axes depuis le nord (boules de 2 : hors tout 0 → 252)
    rows = [3.5 + 35 * i for i in range(7)]
    xs = (1, 36)
    for yc in cols:
        for x in xs:
            box("noir", f"pied_{yc}_{x}", x - 0.8, x + 0.8, yc - 0.8, yc + 0.8, 0, 2.5)   # vérin de réglage
            tube("chrome", f"vertical_{yc}_{x}", (x, yc, rows[0]), (x, yc, rows[-1]), 0.635)
            for z in rows:
                boule("chrome", f"boule_{yc}_{x}_{z}", (x, yc, z), 1.0)
        for z in rows:
            tube("chrome", f"traverse_{yc}_{z}", (xs[0], yc, z), (xs[1], yc, z), 0.635)
    for c0, c1 in zip(cols, cols[1:]):
        for x in xs:
            for z in rows:
                tube("chrome", f"lisse_{c0}_{x}_{z}", (x, c0, z), (x, c1, z), 0.635)
        y0, y1 = c0 + 1.2, c1 - 1.2
        for r, z in enumerate(rows):
            if r:
                box("usm", f"plateau_{c0}_{r}", 1.4, 35.6, y0, y1, z + 0.4, z + 0.6)
            if r < 6:
                box("usm", f"fond_{c0}_{r}", 1.0, 1.2, y0, y1, z + 1.2, rows[r + 1] - 1.2)
        for r in range(2):                         # abattants des deux rangs du bas
            z0, z1 = rows[r], rows[r + 1]
            box("usm", f"abattant_{c0}_{r}", 35.8, 36.0, y0, y1, z0 + 1.2, z1 - 1.2)
            box("chrome", f"serrure_{c0}_{r}", 36.0, 36.4, (y0 + y1) / 2 - 1, (y0 + y1) / 2 + 1, z1 - 4, z1 - 2.5)
        for r in range(2, 6):
            livres(f"livre_u{c0}{r}", 2, 30, y0, y1, rows[r] + 0.6, 33, 0.55 + 0.12 * ((r + c0) % 3), 300 + c0 + r)
    for yc in cols:                               # côtés pleins
        if yc in (1, 251, 151):
            for r in range(6):
                box("usm", f"cote_{yc}_{r}", 1.2, 35.8, yc - 0.1, yc + 0.1, rows[r] + 1.2, rows[r + 1] - 1.2)
    return [
        dict(cadre=(6, 30, 205, 245, 213.5 + 0.6, 245), modele="potted_plant_04"),
        dict(cadre=(6, 30, 20, 50, 213.5 + 0.6, 240), modele="ceramic_vase_04"),
    ]


SYS = {"V": vitsoe, "S": string, "U": usm}


# ------------------------------------------------------------------ scène et rendu

def habiller(sc):
    mats = {}
    for o in list(sc.objects):
        if o.type != "MESH" or o.get("modele"):
            continue
        key = o.name.split("__")[0]
        if key not in mats:
            mats[key] = R.make_material(key)
        o.data.materials.clear()
        o.data.materials.append(mats[key])
        opt = R.MATS.get(key, (None, None, {}))[2]
        if opt.get("tex"):
            sens = opt.get("sens", "bloc")
            if opt["tex"] == "noyer" and R.BOIS[R.ESSENCE][3] == "v" and sens in ("v", "h"):
                sens = "h" if sens == "v" else "v"
            R.make_uvs(o, sens, opt.get("echelle", 1.0))
        lisse = key in LISSES
        for poly in o.data.polygons:
            poly.use_smooth = lisse
        if not lisse and key not in ("verre", "plafond", "sol_bois", "mur"):
            R.chanfreiner(o)
        if key == "canape":                       # coussins : arêtes très arrondies
            mod = o.modifiers.get("chanfrein")
            mod.width, mod.segments = 0.025, 4
        if key == "verre":
            o.visible_shadow = False
    missing = sorted(k for k in mats if k not in R.MATS)
    if missing:
        print("Matériaux non définis (magenta) :", missing)


def scene(code):
    bpy.ops.wm.read_factory_settings(use_empty=True)
    sc = bpy.context.scene
    piece()
    mobilier()
    deco = SYS[code]()          # objets Poly Haven posés sur le meuble (cadres en cm du plan)
    habiller(sc)
    R.remplacer(sc, deco)

    sc.render.engine = "CYCLES"
    R.reglages_cycles(sc)
    sc.render.resolution_x, sc.render.resolution_y = 1600, 1200
    sc.view_settings.view_transform = "AgX"
    sc.view_settings.look = "AgX - Base Contrast"
    sc.view_settings.exposure = R.EXPOSITION
    R.monde(sc)

    bpy.ops.object.light_add(type="SUN", location=(0, 0, 5))
    sun = bpy.context.object
    sun.data.energy = R.SOLEIL_FORCE
    sun.data.angle = math.radians(0.53)
    sun.data.color = (1.0, 0.96, 0.9)
    a, h = math.radians(R.SUN_AZ), math.radians(R.SUN_ALT)
    vers_soleil = R.Vector((math.sin(a) * math.cos(h), math.cos(a) * math.cos(h), math.sin(h)))
    R.look_at(sun, sun.location - vers_soleil)

    portal = R.area(R.p(556, 173, 107), 2.02, 0, shape="RECTANGLE", size_y=2.1)
    portal.data.cycles.is_portal = True
    R.look_at(portal, R.p(400, 173, 107))
    # suspension allumée
    bpy.ops.object.light_add(type="POINT", location=R.p(160, 150, 168))
    lt = bpy.context.object
    lt.data.energy = 40
    lt.data.shadow_soft_size = 0.14
    lt.data.color = (1.0, 0.85, 0.65)

    # vue debout depuis l'angle sud-est (yeux à 163), visée horizontale vers le mur ouest
    cam_data = bpy.data.cameras.new("vue")
    cam_data.lens = VUE["lens"]
    cam_data.sensor_width = 36
    cam_data.shift_y = -0.1
    cam_data.shift_x = 0.0
    cam = bpy.data.objects.new("cam_vue", cam_data)
    sc.collection.objects.link(cam)
    cam.location = R.p(*VUE["loc"])
    R.look_at(cam, R.p(*VUE["target"]))
    sc.camera = cam
    return sc


os.makedirs(OUT, exist_ok=True)
for code in SYSTEMES:
    sc = scene(code)
    sc.render.filepath = os.path.join(OUT, f"salon-biblio-{code}.png")
    bpy.ops.render.render(write_still=True)
    print("Rendu :", sc.render.filepath, f"(soleil h {R.SUN_ALT:.1f}°, az {R.SUN_AZ:.1f}°)")
    bpy.ops.wm.save_as_mainfile(filepath=os.path.join(OUT, f"salon-biblio-{code}.blend"), compress=True)
