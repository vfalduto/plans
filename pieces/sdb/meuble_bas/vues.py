"""Les vues du meuble bas : Plans (les onze dessins), Découpe, Montage, Achats, Explication.

Une seule variante (id vide), pas d'option. Les textes qui étaient sous les dessins de l'ancienne page deviennent leur
texte alternatif (alts) : rien n'est écrit sous un dessin.
"""
import re
from html import escape, unescape

from commun.blocs import Achat, euros, note_source, tableau_achats, vue_lecture
from commun.blocs_construction import Colonne, DessinMeuble, Etape, etapes, tableau_debit, vue_plans
from commun.modele import Vue
from pieces.sdb import iso, piece as P
from pieces.sdb.achats_communs import deux_meubles, prix
from pieces.sdb.meuble_bas import modele as B
from pieces.sdb.meuble_bas.document import VERSION
from pieces.sdb.meuble_bas.dessins import ARIA, DESSINS, ISO, NOMS, legendes
from pieces.sdb.meuble_bas.explication import vue_explication


def _brut(html: str) -> str:
    return " ".join(unescape(re.sub(r"<[^>]+>", "", html)).split())


def alts() -> dict[str, str]:
    """Texte alternatif de chaque dessin : son aria-label d'origine, puis le texte qui était sous lui ; ce texte seul
    s'il commence par le nom du bouton (« Sans la porte : … »)."""
    res = {}
    for k in DESSINS:
        t = _brut(legendes().get(k, ""))
        if not t:
            res[k] = ARIA[k]
        elif t.startswith(NOMS[k] + " :"):
            res[k] = t
        else:
            res[k] = f"{ARIA[k]}. {t}"
    return res


def _plans() -> Vue:
    a = alts()
    return vue_plans([DessinMeuble(k, NOMS[k], DESSINS[k](a[k]), mesure=k not in ISO) for k in DESSINS], "Meuble bas",
                     formule=f"{B.cm(B.PY1 - B.PY0)} × {B.cm(B.PLATEAU_P)}, dessus à {B.cm(B.Z_DESSUS)}")


# ------------------------------------------------------------------ Découpe
def _decoupe() -> str:
    cm = B.cm
    cols = (Colonne("Rep.", "repere"), Colonne("Pièce"), Colonne("Qté", "nombre"), Colonne("Longueur", "cote"),
            Colonne("Largeur", "cote"), Colonne("Ép.", "cote"))
    debit = tableau_debit(cols, [(r, n, q, cm(lg), cm(la), cm(B.EP)) for r, n, q, lg, la in B.PIECES_DEBIT],
                          titre="Pièces")
    lettres = sorted({r for _, d in B.decoupe() for r, _, _ in d})        # les panneaux taillés dans les tablettes
    ta = "".join(f'<li>Tablette {k + 1}, {tb["L"]} × {tb["l"]} : {" + ".join(f"{r} ({cm(lg)})" for r, lg, _ in d)}</li>'
                 for k, (tb, d) in enumerate(B.decoupe()))
    return (debit
            + f"<p><b>A, le plateau</b> : une tablette de chêne de {cm(B.PANNEAU_L)} × {cm(B.PANNEAU_P)}. "
              f"<b>{lettres[0]} à {lettres[-1]}</b> : trois tablettes de mélaminé blanc, les mêmes que le meuble haut :</p>"
            + f"<ul>{ta}</ul>"
            + f'<p><b>Pieds</b> : {B.VERIN["n"] * len(B.JOUES)} vérins.</p>'
            + "<h2>Finition</h2>"
            + f"""<p>Le mélaminé ne se peint pas. Chant blanc thermocollant sur tout ce qui se voit : l'avant des 3 joues, le tour de la porte, le tour des 2 découpes et l'avant du bas et de l'étagère, soit {B.cm(B.chant_vu() / 100)} m. Le plateau, lui, reçoit {B.VERNIS["couches"]} couches de vernis sur toutes ses faces.</p>""")


# ------------------------------------------------------------------ Montage
def etapes_montage() -> list[str]:
    """Les 13 étapes de montage de l'ancienne page (HTML de chaque <li>, son titre en gras en tête)."""
    return [
        f"""<b>Mesurer l'alcôve</b> devant et au fond. Recouper le plateau à la plus petite mesure, moins {B.cm(2 * B.JEU_MUR)} : les murs ne sont jamais parfaitement droits. Faire l'encoche et le trou de la colonne, vernir.""",
        """<b>Couper les panneaux</b> à la scie circulaire avec rail, la face visible dessous, puis plaquer les chants visibles.""",
        """<b>Percer et découper la porte</b> : les 2 découpes, leur chant, les 2 cuvettes, les trous de la poignée. Visser la poignée et les charnières sur la porte.""",
        f"""<b>Poser les vérins.</b> Faire un essai sur une chute. Percer Ø {B.cm(B.VERIN["perce"] * 10)} bien droit dans le chant du bas de chaque joue, garnir le trou de colle MS, enfoncer le vérin. Enduire de colle les chants du bas des joues, du fond et de la porte. Laisser prendre selon la cartouche.""",
        f"""<b>À plat, sur les joues</b> : visser les équerres sous le plateau, en 4 × 16, à {B.cm(B.EQUERRES_X[0] - B.JX0)} de chaque bord, ras du haut, et les plaques de charnière sur la joue nord, en face des cuvettes.""",
        f"""<b>Pour le câble de la colonne</b> : percer la joue nord en face de la sortie relevée sur le mur, et entailler l'étagère de {B.GOUL} × {B.GOUL} dans son angle arrière côté nord.""",
        f"""<b>Assembler le U hors de l'alcôve</b> : le fond entre les joues nord et milieu, au nu du haut et de l'arrière, puis le bas au ras du bas des joues, puis l'étagère, posée sur deux cales de {B.cm(B.NIV_H)} sur le bas. {B.VIS_PANNEAU} vis 4 × 40 à chaque bout, à travers les joues, avant perçage, puis {B.VIS_PANNEAU} vis à travers le fond dans le bas et dans l'étagère. Le U tient debout seul.""",
        """<b>Pousser le U dans l'alcôve</b>, puis dresser la joue sud à sa place et la tenir debout.""",
        """<b>Glisser le plateau par l'avant</b> sur les joues et le fond, jusqu'au mur du fond : l'encoche vient autour du tuyau. Vérifier le niveau, régler les vérins.""",
        """<b>Visser les équerres dans le plateau</b> par en dessous, en 4 × 16. La machine n'est pas encore là : tout est accessible. Les vis ne traversent pas le plateau.""",
        """<b>Bloquer les pieds</b> : un point de colle MS autour de chaque embout de la joue sud, pour qu'elle ne glisse pas vers la machine. <b>Silicone</b> entre le plateau et les murs.""",
        """<b>Clipser la porte</b> sur ses plaques, en la tenant par les côtés et pas par les cornes du haut, régler les charnières pour un jeu égal partout, et rentrer les bacs.""",
        """<b>Poser le tapis</b> et rentrer la machine par l'avant, puis raccorder. Ouvrir sa porte à fond pour vérifier qu'elle ne bute pas sur la poignée.""",
    ]


def pose_colonne() -> list[str]:
    """Les 5 étapes de la pose de la colonne de prises."""
    return [
        f"""<b>Avant de vernir le plateau</b> : percer son trou à {B.cm(P.X1 - B.COL_TROU["x"])} du mur du fond et {B.cm(B.COL_TROU["y"])} du mur nord. Avant le montage du placard : percer la joue nord en face de la sortie du câble, entailler l'étagère.""",
        f"""<b>À l'atelier</b> : recouper le panneau à la mesure réelle entre plateau et meuble haut, moins 2 mm, couper les biseaux, percer les 4 trous Ø {B.cm(B.BOITE["d"] * 10)}, le trou du fil et l'encoche du haut.""",
        f"""<b>Une fois les deux meubles posés</b> : tirer le câble, glisser le panneau dans l'angle, visser {len(B.COL_VIS)} vis 4 × 40 à travers le plateau dans son chant depuis le placard, bacs sortis, et {len(B.COL_VIS)} vis à travers le dessous du meuble haut, depuis l'intérieur, étagère retirée. Avant perçage Ø 2,5 au milieu du chant.""",
        """<b>Électricien</b> : poser les boîtes et les prises, courant coupé.""",
        """<b>Fil des LED</b> : passer le fil, le fixer sous le meuble haut avec des clips adhésifs, brancher le transformateur.""",
    ]


def figure_montage(n: int) -> str:
    """Schéma de l'étape n (1 à 13) : ce qui est déjà monté en gris, les pièces posées à l'étape ou sur lesquelles elle
    travaille en couleur. Chaîne vide quand l'étape n'a rien à montrer (couper, silicone) : le modèle n'a pas la pièce."""
    neuves = {k for k, v in B.POSE.items() if v == n} | set(B.ACCENT.get(n, ()))
    vus = {k for k, v in B.POSE.items() if v <= n} | neuves | set(B.CONTEXTE.get(n, ()))
    if not neuves:
        return ""
    blocs = [b for b in B.blocs() if b.nom in vus and not (b.nom.startswith("verin_") and f"joue_{b.nom[6]}" not in vus)]
    return iso.dessin(blocs, neuves, reperes=False, titre=f"Montage, étape {n}")


def figure_colonne(n: int) -> str:
    """Schéma de l'étape n (1 à 5) de la pose de la colonne : la colonne seule à l'atelier, puis dans l'angle, sur le
    meuble monté. Chaîne vide pour les étapes sans pièce (percer le plateau, fil des LED)."""
    neuves = {k for k, v in B.POSE_COLONNE.items() if v == n} | set(B.ACCENT_COLONNE.get(n, ()))
    if not neuves:
        return ""
    if n == 2:
        blocs = [b for b in B.blocs() if b.nom in neuves]
    else:
        blocs = B.blocs()
    return iso.dessin(blocs, neuves, reperes=False, titre=f"Pose de la colonne, étape {n}")


def _montage() -> str:
    eq = "".join(f"<li>{escape(o)} : {n}</li>" for o, n in B.EQUERRES)
    return (etapes([Etape("", f"<p>{t}</p>", figure_montage(i)) for i, t in enumerate(etapes_montage(), 1)], titre="Montage")
            + f"<p>Les {B.N_EQUERRES} équerres :</p><ul>{eq}</ul>"
            + etapes([Etape("", f"<p>{t}</p>", figure_colonne(i)) for i, t in enumerate(pose_colonne(), 1)],
                      titre="Pose de la colonne"))


# ------------------------------------------------------------------ Achats
def _note(q, pu, stock):
    """Prix unitaire (quantité autre que 1) et stock lu au magasin, dans la note de l'article."""
    return ", ".join(([f"{q:g} × {euros(pu)}"] if q != 1 else []) + ([f"stock : {stock}"] if stock is not None else []))


def _achats() -> str:
    total = B.total()
    return ("<h2>Meuble bas</h2>"
            f"<p>Le meuble bas entier coûte <b>{prix(total)}</b> : plateau, tablettes, chant, charnières, poignées, "
            "2 bacs, 4 prises et leurs boîtes, vérins, colle, vernis, tapis, équerres, vis et silicone. Les vis 4 × 40 "
            "sont prises dans les achats du meuble haut, le kit LED aussi. Le câble, la goulotte et l'électricien ne "
            "sont pas comptés. Le détail est dans la liste d'achats.</p>"
            f"<p>Tout ce qu'il faut pour le meuble bas {VERSION}. Joues, fond, bas, étagère et porte en mélaminé blanc, "
            "levés sur des vérins, avec les 2 bacs.</p>"
            + tableau_achats([Achat(nom, ref, q, pu, _note(q, pu, st)) for nom, ref, q, pu, st in B.prix()],
                             "Total du meuble bas", arrondi=False)
            + note_source(f"Les vis 4 × 40 viennent de la liste du meuble haut, qui en a assez. Pour acheter le meuble "
                          f"bas seul, ajouter la boîte de vis ({prix(9.00)}), soit {prix(total + 9.00)}. Chant : "
                          f"{B.cm(B.chant_vu() / 100)} m à plaquer, 10 % de chutes compris. Vérins comptés à l'unité "
                          "comme l'indique la fiche ; un avis client parle d'un paquet de 5, à vérifier en magasin. Le "
                          "lot de poignées en contient 2, une seule sert. Non comptés : le câble, la goulotte et "
                          "l'électricien, la scie sauteuse, le rail de coupe, le foret à cuvette Ø 35, la scie cloche "
                          "Ø 67 et les clips adhésifs du fil des LED.")
            + deux_meubles({"bas": "", "haut": "../../sdb-meuble-achats.html#haut-seul"}))


def vues(variante: str) -> dict[str, Vue]:
    if variante != "":
        raise ValueError(f"meuble bas : variante « {variante} » inconnue (une seule, d'id vide)")
    return {"plans": _plans(), "decoupe": vue_lecture("decoupe", _decoupe()),
            "montage": vue_lecture("montage", _montage()), "achats": vue_lecture("achats", _achats()), "explication": vue_explication()}
