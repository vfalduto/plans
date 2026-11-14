"""Vues du salon/aménagement (une seule variante, d'id vide) : Plan, Coupes, Iso, Caméra, Explication.

`vues(variante)` rend le dictionnaire des vues du type « aménagement ». Plan et coupes viennent de dessins.py ; le
paragraphe sous le plan de l'ancienne page est devenu les fiches des meubles (zones.py), les cartes « Principe » de
l'Explication et le texte alternatif du plan (textes.py) ; le texte sous chaque coupe, le texte alternatif de la coupe.
Iso : les deux rendus de `site/salon/amenagement/rendus/` (sud-est et nord-ouest), chacun en chêne et en noyer (option
Bois) ; les coins nord-est et sud-ouest, sans rendu, restent grisés. Caméra : aucune caméra perspective n'a jamais été
rendue pour le salon, l'onglet est grisé.
"""
from pathlib import Path

from commun.blocs import Coupe, Lieu, points_iso, vue_camera, vue_coupes, vue_iso, vue_lecture, vue_plan, zones_svg
from commun.modele import Vue
from pieces.salon import piece
from pieces.salon.amenagement import dessins, explication, options, textes, zones

RENDUS_SITE = Path(__file__).resolve().parents[3] / "site" / "salon" / "amenagement" / "rendus"
LIEU = Lieu(piece.SOL, piece.PORTES, "Position dans le salon")
ENVELOPPE = (0, 0, piece.L, piece.P)
# trait de chaque coupe sur le mini-plan : A et B coupent le salon d'un mur à l'autre en y, C et D en x
TRAITS = {"A": ((dessins.COUPE_A, 0), (dessins.COUPE_A, piece.P)),
          "B": ((dessins.COUPE_B, 0), (dessins.COUPE_B, piece.P)),
          "C": ((0, dessins.COUPE_C), (piece.L, dessins.COUPE_C)),
          "D": ((0, dessins.COUPE_D), (piece.L, dessins.COUPE_D))}
LEGENDE = ("<p>Les chiffres cerclés ① à ⑧ numérotent les meubles ; chacun a sa carte « Principe » dans l'Explication. "
           "Tireté rouge : dégagement libre, en cm. Tireté noir : les étagères, au-dessus de l'enfilade.</p>")


def _vue_plan() -> Vue:
    zs = zones.zones()
    return vue_plan(dessins.plan_svg(textes.texte_alternatif_plan(), zones_svg(zs)), zs, LEGENDE)


def _vue_coupes() -> Vue:
    coupes = [
        Coupe("A", "A mur ouest", "Coupe A-A : mur ouest", dessins.coupe_a(textes.alt_coupe_a()), TRAITS["A"]),
        Coupe("B", "B baie et desserte", "Coupe B-B : baie et desserte", dessins.coupe_b(textes.alt_coupe_b()), TRAITS["B"]),
        Coupe("C", "C à travers la table", "Coupe C-C : à travers la table", dessins.coupe_c(textes.alt_coupe_c()),
              TRAITS["C"]),
        Coupe("D", "D mur sud, écran", "Coupe D-D : mur sud, écran", dessins.coupe_d(textes.alt_coupe_d()), TRAITS["D"]),
    ]
    return vue_coupes(coupes, LIEU)


def _vue_iso(variante: str) -> Vue:
    alts = {"iso_se": textes.alt_rendu("iso_se"), "iso_no": textes.alt_rendu("iso_no")}
    return vue_iso(RENDUS_SITE, variante, LIEU, points_iso(ENVELOPPE), alts, option=options.BOIS)


def vues(variante: str) -> dict[str, Vue]:
    if variante != "":
        raise ValueError(f"salon/amenagement : variante inconnue « {variante} »")
    return {
        "plan": _vue_plan(),
        "coupes": _vue_coupes(),
        "iso": _vue_iso(variante),
        "camera": vue_camera(RENDUS_SITE, variante, LIEU, []),
        "explication": vue_lecture("explication", explication.explication()),
    }
