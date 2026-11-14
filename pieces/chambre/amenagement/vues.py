"""Vues de l'aménagement de la chambre (une seule variante, d'id vide).

`vues(variante)` rend le dictionnaire des vues du type « aménagement ». Le plan et les élévations viennent de dessin.py ;
le texte qui suivait chaque dessin est devenu son aria-label (`dessin.ALTS`). Iso et Caméra n'ont pas de rendu (pas de
modèle 3D) : onglets grisés. Explication reprend le chapô, les chiffres clés, les six cartes « Principe » et les points
à vérifier de l'ancienne page chambre-amenagement.html (V2.1).
"""
from pathlib import Path

from commun.blocs import (Carte, Coupe, Lieu, Zone, a_verifier, chiffres, cotes_meuble, nombre, points_iso, principes,
                          tete, vue_camera, vue_coupes, vue_iso, vue_lecture, vue_plan, zones_svg)
from commun.modele import Vue
from pieces.chambre import piece
from pieces.chambre.amenagement import dessin, document

RENDUS_SITE = Path(__file__).resolve().parents[3] / "site" / "chambre" / "amenagement" / "rendus"
LIEU = Lieu(piece.SOL, piece.PORTES, "Position dans la chambre")

# Murs compris (-10, -12, 453, 263), pour les points de vue iso.
ENVELOPPE = (-piece.EP["o"], -piece.EP["n"], piece.L + piece.EP["e"], piece.P + piece.EP["s"])
# Trait « Position » d'une élévation : le mur regardé.
TRAITS = {"est": ((piece.L, 0), (piece.L, piece.P)), "sud": ((0, piece.P), (piece.L, piece.P)),
          "ouest": ((0, 0), (0, piece.P))}

# Cartes « Principe » de l'Explication : leur meuble sur le plan (un id de document.ZONES), ou rien.
MEUBLES_CARTES = ("lit", "chevet_ouest", "commodes", "niche", "niche", "")
# Les deux chevets partagent la carte ② : leur fiche le précise.
SUFFIXES = {"chevet_ouest": ", ouest", "chevet_est": ", est"}

# ------------------------------------------------------------------ textes repris tels quels de l'ancienne page
# Chapô : seuls les deux liens changent (les points à vérifier sont dans cette vue ; l'historique a sa page).
CHAPO = ("Un lit de 160 × 200 sur sommier et pieds, sans cadre, tête au mur sud contre une tête de lit murale, centré "
         "entre le placard existant et le mur est. Tout le mur est, sous la fenêtre, est occupé par un plan posé sur "
         "deux commodes. Au nord de ce plan, le coin des vêtements déjà portés, ni propres ni sales : trois patères "
         "au-dessus et une niche à pantalons en dessous. Le pied du lit laisse 47 cm jusqu'au mur nord "
         '(voir <a href="#explication">Points à vérifier</a>). '
         "L'historique est sur sa propre page (<a href=\"historique.html\">Changements</a>).")

# Cartes « Principe » : (titre, texte HTML).
PRINCIPES = [
    ("① Lit 160, tête au sud",
     "Sommier 160 × 200 de 25 sur pieds de 22, matelas de 35 : dessus du matelas à 82. Pas de cadre, donc pas de "
     "débord : le lit occupe exactement 160 × 200. La tête de lit est un panneau fixé au mur (168 × 90, 4 "
     "d'épaisseur), de 50 à 140 de haut, pour dépasser de 58 au-dessus du matelas. Le lit est centré entre le "
     "placard (x 47) et le mur est, et ne passe devant ni la porte, ni la fenêtre, ni la porte du placard."),
    ("② Chevets",
     "Hauteur 70, un peu sous le dessus du matelas (82) : on y pose la main sans se relever. Côté ouest, 40 × 35 "
     ": il laisse 70 cm devant le placard. Côté est, 30 × 35 pour laisser sortir les tiroirs de la commode sud "
     "(il reste 7 cm). Une applique de chaque côté de la tête de lit, à 140 (environ 55 au-dessus du matelas, "
     "pour lire), et des prises à 85, juste au-dessus des chevets."),
    ("③ Plan sur deux commodes",
     "Un plan de 241 × 42 × 3 (bois massif ou lamellé-collé) court du décroché jusqu'au mur sud, dessus à 85, "
     "sous l'allège de 106. Il est posé sur deux commodes de 80 × 40, h 82 (tiroirs, sans plateau ou plateau "
     "d'origine sous le plan), au sud, et au nord sur une joue de 2 cm. Un tasseau le long du mur le tient en "
     "arrière. Il sert de commode, de vide-poche et de coiffeuse sous la fenêtre."),
    ("④ Vêtements portés : patères et pantalons",
     "Le coin nord du meuble, entre le décroché et la fenêtre. Au-dessus du plan, trois patères à 165 pour une "
     "veste, une chemise, un pull. Sous le plan, une niche de 79 cm avec deux barres fixes, parallèles au mur et "
     "décalées (devant à 70, derrière à 76) : on plie un pantalon en deux sur une barre, trois par barre, six en "
     "tout. Ils restent à plat, sans faux pli, et à l'air."),
    ("Pantalons : autres solutions",
     "Si on veut cacher la niche, un porte-pantalons coulissant (cadre à barres sur coulisses, 40 de profondeur) "
     "fixé sous le plan, ou une porte sur la niche. Le cadre sort vers le lit sur 40 cm et laisse 35 cm de "
     "passage quand il est ouvert. Les barres fixes restent le plus simple et laissent mieux respirer."),
    ("Circulation",
     "La porte s'ouvre dans l'angle nord-ouest et ne touche rien. On longe le pied du lit (47 cm) pour rejoindre "
     "le côté est : 75 cm entre le lit et le plan, 42 devant un tiroir ouvert. Le côté ouest dessert le placard."),
]

# Points à vérifier, HTML.
POINTS = [
    "<b>Passage au pied du lit : 47 cm.</b> On recommande 60 cm. C'est déjà le maximum avec un 200 tête au sud "
    "(sommier sans débord, tête de lit murale de 4). Un matelas et un sommier de 190 donneraient 57.",
    "<b>Devant les commodes : 75 cm, 42 tiroir ouvert.</b> C'est juste pour se tenir devant un tiroir ouvert. "
    "Des commodes de 35 de profondeur sous un plan de 40 donneraient 5 cm de plus de chaque côté ; des tiroirs à "
    "sortie totale ne sortent pas plus loin.",
    "<b>Climatisation</b> : unité murale au plafond, sur le mur nord, contre le décroché (dessinée en cotes "
    "types, 88 × 22, de 220 au plafond). Elle souffle vers le sud, donc vers le lit : régler les volets pour ne "
    "pas viser l'oreiller. Pas de radiateur : le plan filant ne masque rien.",
    "<b>Commodes</b> : 80 × 40, h 82 est une cote type ; avec un modèle du commerce, la hauteur du plan suit "
    "(rester sous 100 pour garder 6 cm sous l'allège). La niche au nord fait ce qu'il reste (241 − 2 × 80 − 2 = "
    "79).",
    "<b>Décroché nord-est</b> : 13 le long du mur nord, 10 le long du mur est, d'après le relevé. Le plan "
    "démarre à son nu (y 10) ; s'il est plus profond, la niche se raccourcit d'autant.",
    "<b>Placard</b> : 164 de long, porte de 155. La profondeur retenue (47 au nu de la cloison) vient de 441 − "
    "393,7 ; la cote 50,3 du relevé est à confirmer.",
    "<b>Électricité</b> : position des prises et de l'interrupteur non relevée. Une prise au-dessus du plan est "
    "utile (lampe, chargeur).",
]


def _cotes(z, m):
    """Cotes de la fiche : `cotes_meuble` (grand côté d'abord), ou largeur (x) × profondeur (y) si la zone le déclare."""
    if z.get("cotes") != "largeur":
        return cotes_meuble(m)
    return f'{nombre(m["x1"] - m["x0"])} × {nombre(m["y1"] - m["y0"])}, h {nombre(m["z1"] - m.get("z0", 0))}'


def _zones(M):
    """Meubles touchables du plan, un par zone de `M.ZONES` ; un bord donné par la zone remplace celui du meuble."""
    zones = []
    for z in M.ZONES:
        m = getattr(M, z["meuble"])
        titre, texte = PRINCIPES[z["carte"]]
        zones.append(Zone(id=z["id"], titre=titre + SUFFIXES.get(z["id"], ""),
                          emprise=tuple(z.get(c, m[c]) for c in ("x0", "y0", "x1", "y1")), cotes=_cotes(z, m),
                          texte=texte, coupe=z["coupe"]))
    return zones


def _vue_plan(M):
    zones = _zones(M)
    svg = dessin.plan_svg(M, aria=dessin.ALTS["plan"], zones=zones_svg(zones))
    return vue_plan(svg, zones, dessin.legende())


def _vue_coupes(M):
    coupes = [Coupe(k, nom, f"Élévation du {nom.lower()}", scene=dessiner(M, aria=dessin.ALTS[k]), trait=TRAITS[k])
              for k, (nom, dessiner) in dessin.ELEVATIONS.items()]
    return vue_coupes(coupes, LIEU)


def _vue_explication(M):
    pl = M.PLAN
    stats = [(f'{nombre(pl["y1"] - pl["y0"])} × {nombre(pl["x1"] - pl["x0"])}',
              f'plan sur {len((M.COMMODE_NORD, M.COMMODE_SUD))} commodes, h {nombre(pl["z1"])}'),
             (f'{len(M.PATERES["y"])} + {len(M.NICHE["barres"]) * M.NICHE["pantalons"]}', "patères + pantalons"),
             (nombre(pl["x0"] - M.LIT["x1"]), "entre le lit et le plan (cm)"),
             (nombre(M.LIT["y0"]), "passage au pied du lit (cm)")]
    cartes = [Carte(t, x, m) for (t, x), m in zip(PRINCIPES, MEUBLES_CARTES, strict=True)]
    return vue_lecture("explication", tete(CHAPO) + chiffres(stats) + principes(cartes)
                       + a_verifier(POINTS, titre="Points à vérifier"))


def vues(variante: str) -> dict[str, Vue]:
    M = document
    return {
        "plan": _vue_plan(M),
        "coupes": _vue_coupes(M),
        "iso": vue_iso(RENDUS_SITE, variante, LIEU, points_iso(ENVELOPPE)),
        "camera": vue_camera(RENDUS_SITE, variante, LIEU, piece.CAMERAS),
        "explication": _vue_explication(M),
    }
