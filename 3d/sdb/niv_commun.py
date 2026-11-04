# Socle commun du document « niveaux de finition » du meuble bas (niveaux.py) : ce qui est validé par le client, la place
# disponible, la fiche de chaque niveau et les vues (face, coupe, dessus, iso) cadrées pareil pour tous.
#
# Validé (client, 2026-11-04) : plan massif au-dessus de la machine ; machine à droite, porte qui s'ouvre à gauche ; espace
# technique de 5 à 7 cm derrière elle (évacuation et robinet) ; au moins 3 prises au-dessus du plan.
# Demandé : deux paniers l'un au-dessous de l'autre, chacun posé sur deux traverses.
#
# Cotes en cm, repère de modele.py : x vers l'est (mur du fond à 234), y vers le sud, z depuis le sol. Vu depuis la salle de
# bain, on regarde vers l'est : le nord (y petit) est à gauche, le sud (y grand) à droite.

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import modele as M  # noqa: E402
import plan as PL  # noqa: E402
import cotes as CO  # noqa: E402
import montage as MO  # noqa: E402

cm, f, euros = PL.cm, PL.f, PL.euros
Bloc, Profil, replace = M.Bloc, M.Profil, M.replace

# ------------------------------------------------------------------ ce qui ne change à aucun niveau
PLAN = CO.nom("plan_travail")           # plan de 60 × 114,4 ; un niveau peut changer son épaisseur en le remplaçant
MACHINE, SIPHON, ARRIVEE = M.MACHINE, M.SIPHON, M.ARRIVEE
BASE = [PLAN, MACHINE, SIPHON, ARRIVEE]

# ------------------------------------------------------------------ la place pour le linge, à gauche de la machine
# BAIE : volume brut, sans aucune structure. La structure et ses jeux se retirent de là.
BAIE = dict(y0=M.Y0 + 0.3, y1=MACHINE.y0 - 0.6, x0=M.FACE, x1=M.X1 - 0.3, z0=0.0, z1=M.Z_PLAN)
LARGEUR_BAIE = BAIE["y1"] - BAIE["y0"]          # 49,9
PROF_BAIE = BAIE["x1"] - BAIE["x0"]             # 59,7 : pas de tuyau derrière les paniers (ils sont en y 66 → 82)
HAUT_BAIE = BAIE["z1"] - BAIE["z0"]             # 85,5
ZONE_TECHNIQUE = dict(x0=MACHINE.x1, x1=M.X1, y0=MACHINE.y0, y1=MACHINE.y1)   # 5 derrière la machine (5 à 7 validé)
assert 5 <= ZONE_TECHNIQUE["x1"] - ZONE_TECHNIQUE["x0"] <= 7

# ------------------------------------------------------------------ porte de la machine (charnière à gauche, côté paniers)
# Diamètre de porte et angle d'ouverture : estimés, de mémoire, à mesurer sur la machine du client.
HUBLOT = dict(y=(MACHINE.y0 + MACHINE.y1) / 2, z=MACHINE.z0 + 50, d=47.0, angle=170, saillie=10.0)
CHARNIERE_LL = HUBLOT["y"] - HUBLOT["d"] / 2    # ≈ 57 : ouverte à 170°, la porte passe devant la baie jusqu'à y ≈ 10
Y_LL_OUVERTE = CHARNIERE_LL - HUBLOT["d"]
X_LL_FACE = MACHINE.x0                          # 176 : le plan déborde de 2 devant la machine

# ------------------------------------------------------------------ porte d'entrée (ouverte à 90°, à 9 du nu du plan)
X_PORTE = M.PORTE["x1"]
JEU_PORTE = M.FACE - X_PORTE                    # 9


def prises(n=3, y0=84.0, z0=122.0, largeur_poste=7.1, hauteur=8.0, saillie=1.0, nom="prises_niche"):
    """Bloc de n prises sur le mur du fond, au-dessus du plan. Le robinet d'arrêt est à y 74, z 102 : ne pas le recouvrir."""
    y1 = y0 + n * largeur_poste
    assert n >= 3, "au moins 3 prises (validé par le client)"
    assert z0 > M.Z_DESSUS, "au-dessus du plan"
    assert y0 >= M.ROBINET["y"] + 3 or y1 <= M.ROBINET["y"] - 3 or z0 > M.ROBINET["z"] + 3, "le robinet reste accessible"
    return Bloc("prise", nom, M.X1 - saillie, M.X1, y0, y1, z0, z0 + hauteur, miroir=False)


def iso(blocs, neuves=(), titre=""):
    """Vue isométrique sans repères ; neuves : noms des pièces du niveau, dessinées en couleur."""
    return MO.dessin(list(blocs), neuves=set(neuves), reperes=False, titre=titre)


def _sol(x0, x1):
    return f'<line class="osol" x1="{f(x0)}" y1="0" x2="{f(x1)}" y2="0"/>'


def vue_face(blocs, corps=(), titre="Vue de face"):
    """Depuis la salle de bain (nord à gauche, sud à droite) ; corps : éléments SVG en plus (cotes, textes)."""
    h = M.Z_DESSUS + 8
    o = [PL.rect(M.Y0, -h, M.Y1, 0, "omur"), PL.rect(M.Y0 - 4, -h, M.Y0, 0, "omurc"), PL.rect(M.Y1, -h, M.Y1 + 4, 0, "omurc"),
         _sol(M.Y0 - 6, M.Y1 + 6)]
    o += CO.projeter(list(blocs), "face")
    o.append(CO.hublot(MACHINE, "face"))
    o.append(PL.text((MACHINE.y0 + MACHINE.y1) / 2, -(M.Z_PLAN - 10), "machine", "lt"))
    o.append(PL.text(M.Y0 - 0.6, -h - 1, "nord", "lt muted", "end"))
    o.append(PL.text(M.Y1 + 0.6, -h - 1, "sud", "lt muted", "start"))
    o += list(corps)
    return CO.svg(M.Y0 - 34, -h - 8, M.Y1 + 12, 20, o, titre)


def vue_coupe(blocs, s, corps=(), sortie=60, titre="Coupe vue vers le nord"):
    """Coupe au plan y = s, vue vers le nord (pièce à gauche, mur du fond à droite) ; sortie : place dessinée devant le plan."""
    h = M.Z_DESSUS + 8
    x0 = M.FACE - sortie
    o = [PL.rect(M.X1, -h, M.X1 + 4, 0, "omurc"), _sol(x0 - 4, M.X1 + 4)]
    o += CO.projeter(list(blocs), "cote", s)
    o.append(PL.text(M.X1 - 2, -h - 1, "mur du fond", "lt muted", "end"))
    o += list(corps)
    return CO.svg(x0 - 34, -h - 8, M.X1 + 8, 20, o, titre)


def vue_dessus(blocs, z, corps=(), titre="Vue de dessus"):
    """Coupe horizontale à la hauteur z ; dessine les murs, le vantail de la porte d'entrée ouvert et la porte de la machine
    ouverte à fond (arc en tireté), qui passent devant la baie."""
    o = [PL.rect(M.X1 - M.ALCOVE["nord"], M.Y0 - 4, M.X1 + 4, M.Y0, "omurc"),
         PL.rect(M.X1 - M.ALCOVE["sud"], M.Y1, M.X1 + 4, M.Y1 + 4, "omurc"), PL.rect(M.X1, M.Y0, M.X1 + 4, M.Y1, "omurc"),
         PL.rect(X_PORTE - 4, M.Y0, X_PORTE, M.Y0 + M.PORTE["l"], "ofac"),
         f'<path class="oswing" d="M {f(X_PORTE - M.PORTE["l"])} {f(M.Y0)} A {f(M.PORTE["l"])} {f(M.PORTE["l"])} 0 0 0 {f(X_PORTE)} {f(M.Y0 + M.PORTE["l"])}"/>']
    o += CO.projeter([b for b in blocs if b.role != "plan"], "dessus", z)
    r = HUBLOT["d"]
    o.append(f'<path class="oswing" d="M {f(X_LL_FACE - r)} {f(CHARNIERE_LL)} A {f(r)} {f(r)} 0 0 0 {f(X_LL_FACE)} {f(CHARNIERE_LL - r)}"/>')
    o.append(PL.text(X_PORTE - 28, M.Y0 + 70, "porte d'entrée ouverte", "lt muted", "end"))
    o.append(PL.text((MACHINE.x0 + MACHINE.x1) / 2, (MACHINE.y0 + MACHINE.y1) / 2, "machine", "lt"))
    o += list(corps)
    return CO.svg(M.PORTE["x0"] - 6, M.Y0 - 14, M.X1 + 14, M.Y1 + 10, o, titre)


# ------------------------------------------------------------------ fiche d'un niveau (lue par le comparatif)
# Périmètre commun du coût : le meuble bas complet, plan et finition compris, matériel des prises compris, boîtes et pots
# comptés entiers ; sans caisson haut, machine, plomberie ni main-d'œuvre de l'électricien.
CLES_FICHE = ("niveau", "nom", "resume", "lignes", "heures", "outils", "paniers", "traverses", "gestes", "ouverture",
              "independants", "prises", "finition", "risques")
CLES_LIGNE = ("libelle", "qte", "pu", "source", "statut")       # statut : "relevé" (prix lu, avec date) ou "estimé"


def cout(fiche):
    return round(sum(l["qte"] * l["pu"] for l in fiche["lignes"]), 2)


def verifier(fiche):
    manque = [k for k in CLES_FICHE if k not in fiche]
    assert not manque, f"fiche : il manque {manque}"
    for l in fiche["lignes"]:
        assert all(k in l for k in CLES_LIGNE) and l["statut"] in ("relevé", "estimé"), l
    assert fiche["prises"]["nombre"] >= 3 and fiche["paniers"]["nombre"] == 2
    return fiche


def tableau_cout(fiche):
    """Tableau de chiffrage du niveau : à placer dans section()."""
    ls = "".join(f'<tr><td>{l["libelle"]}</td><td class="num">{l["qte"]:g}</td><td class="num">{euros(l["pu"])}</td>'
                 f'<td class="num">{euros(l["qte"] * l["pu"])}</td><td>{l["source"]} · {l["statut"]}</td></tr>'
                 for l in fiche["lignes"])
    return (f'<div class="scroll"><table><thead><tr><th>Poste</th><th>Qté</th><th>Prix</th><th>Total</th><th>Source</th></tr>'
            f'</thead><tbody>{ls}<tr><td><b>Meuble bas complet</b></td><td></td><td></td><td class="num"><b>{euros(cout(fiche))}</b></td>'
            f'<td>caisson haut, plomberie et électricien non comptés</td></tr></tbody></table></div>')


if __name__ == "__main__":
    print(f"baie : largeur {LARGEUR_BAIE:.1f}  profondeur {PROF_BAIE:.1f}  hauteur {HAUT_BAIE:.1f}")
    print(f"porte machine : charnière y {CHARNIERE_LL:.1f}, ouverte jusqu'à y {Y_LL_OUVERTE:.1f}")
    print(f"porte d'entrée : {JEU_PORTE} devant le nu du plan")
