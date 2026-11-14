"""Explication du meuble haut : le chapô, les chiffres clés, l'alcôve, les matériaux possibles et le repère.

Textes repris de l'ancienne page sdb-meuble-haut.html (V6.4), mêmes formules ; les cotes sont calculées depuis le modèle.
L'ancienne page n'avait ni rendu 3D ni « À vérifier sur place » : rien n'en est inventé.
"""
from html import escape

from commun.blocs import chiffres, note_source, tete, vue_lecture
from commun.modele import Vue
from pieces.sdb.achats_communs import prix
from pieces.sdb.meuble_haut import modele as H

M, cm = H.M, H.cm


def _chapo() -> str:
    return (f"Le caisson de {cm(M.Z_HAUT)} à {cm(M.Z_HAUT1)}, au-dessus de la niche : serviettes au nord, pharmacie au "
            f"sud, {H.lettres(H.N_PORTES)} portes coulissantes, fileur jusqu'au plafond. Chevillé au mur du fond, "
            'au-dessus du carrelage. <a href="../../archives/sdb-meuble-v4-haut.html">La version précédente</a> reste dans '
            "les archives.")


def _alcove() -> str:
    return ("<h2>Alcôve</h2>"
            f"<p>Salle de bain, alcôve de {M.Y1} de large au mur du fond, entre un mur de retour de {M.ALCOVE['nord']} "
            f"au nord et un de {M.ALCOVE['sud']} au sud (cm). Le meuble haut est le seul meuble de cette page ; le "
            'meuble bas a la sienne, et leurs achats se lisent ensemble dans <a href="#achats">Achats</a>.</p>')


def _materiaux() -> str:
    mm = lambda v: f"{v * 10:.0f}"          # noqa: E731
    corps = "".join(
        f'<tr><td><b>{escape(m["nom"])}</b>{" (retenu)" if m["retenu"] else ""}</td><td class="num">{mm(m["ep"])}</td>'
        f'<td>{escape(m["format"])}</td><td>{escape(m["qualites"])}</td><td>{escape(m["defauts"])}</td>'
        f'<td>{escape(m["finition"])}</td><td class="num">{prix(m["prix"])}</td>'
        f'<td>{escape(m["magasin"])}{" réf. " + m["ref"] if m["ref"] else ""}</td></tr>' for m in M.MATERIAUX_HAUT)
    r = next(m for m in M.MATERIAUX_HAUT if m["retenu"])
    return ("<h2>Matériaux possibles</h2>"
            "<p>Le caisson haut est au-dessus de la niche, loin des projections : il ne prend presque pas d'eau. Pas "
            "besoin de vernis marin ni de bois massif ; un panneau de "
            f'{mm(min(m["ep"] for m in M.MATERIAUX_HAUT))} ou {mm(max(m["ep"] for m in M.MATERIAUX_HAUT))} mm suffit. '
            "Un panneau brut se peint (sous-couche, puis deux couches).</p>"
            '<div class="defile"><table><thead><tr><th>Panneau</th><th class="num">Ép. (mm)</th><th>Format</th>'
            "<th>Qualités</th><th>Défauts</th><th>Finition</th><th class=\"num\">Prix</th><th>Magasin</th></tr></thead>"
            f"<tbody>{corps}</tbody></table></div>"
            f'<p><b>Retenu : {escape(r["nom"].lower())}</b>. Le moins cher qui convient : {escape(r["qualites"])}, rien à '
            f'peindre. Son défaut ({escape(r["defauts"])}) compte peu à cette hauteur : {escape(r["finition"])}. '
            "Choix laissé au constructeur.</p>"
            + note_source(f"Prix TTC du panneau entier relevés en ligne le {M.RELEVE_V6}, stock non lu."))


def vue_explication() -> Vue:
    pieces = H.debit_haut()
    stats = [(prix(H.total()), "Meuble haut entier"),
             (f"{cm(M.Z_HAUT)} à {cm(M.Z_HAUT1)}", "Hauteur du caisson (cm)"),
             (str(len(H.ETAPES)), "Étapes de montage"),
             (f"{sum(p['q'] for p in pieces)}", f"Pièces, en {len(pieces)} repères")]
    return vue_lecture("explication", tete(_chapo()) + chiffres(stats) + _alcove() + _materiaux()
                       + note_source("Repère : origine à l'angle nord-ouest intérieur, x vers l'est, y vers le sud, z "
                                     "depuis le sol, cotes en cm (débit en mm)."))
