# Meuble bas de la salle de bain : le document (version, changements, versions figées).
#
# Les changements sont repris de l'ancienne page sdb-meuble-bas.html (V8.5), du plus récent au plus ancien.

from pieces.sdb.archives import FIGEES_COMMUNES

VERSION = "V8.5"
CHANGEMENTS = [
    ("V8.5", "05/11/2026", "Panneau perforé et ses deux montants retirés, à la demande du client. Le meuble bas revient à 296,82 €."),
    ("V8.4", "05/11/2026", "Colonne en diagonale : un seul panneau biseauté de 18 de large coupe l'angle à 45°, les prises regardent la pièce. Panneau perforé SKÅDIS de 36 × 56 sur le mur nord, au-dessus du plateau, porté par deux montants vissés au plateau et au meuble haut : rien n'est percé dans le carrelage. Le meuble bas passe à 306,82 €."),
    ("V8.3", "05/11/2026", "Arrivée du courant relevée par le client : en bas du mur nord. Le câble traverse la joue nord, longe sa face intérieure jusqu'à l'angle arrière et monte à la colonne. Le bas du placard n'a plus d'entaille. Position exacte de la sortie à relever. Prix inchangé."),
    ("V8.2", "05/11/2026", "Colonne en mélaminé dans l'angle du fond et du mur nord, entre le plateau et le meuble haut : 3 prises libres et un 4e poste en haut pour le transformateur des LED, dont le fil monte dans la colonne. Rien n'est percé dans le carrelage. Étagère et bas entaillés dans l'angle arrière pour le câble d'alimentation, qui passe par un trou dans le plateau. Le meuble bas passe à 296,82 €."),
    ("V8.1", "05/11/2026", "Placard fermé en bas : un panneau de mélaminé à 2 du sol porte le bac du bas, qui ne pose plus au sol. Étages ramenés à 40,7. Les fenêtres deviennent des U à fond arrondi de 10 de haut : celle du haut est une encoche ouverte sur le bord de la porte, celle du bas reste fermée. Prix inchangé : le bas sort d'une chute de tablette."),
    ("V8.0", "04/11/2026", "Placard : le cadre en tasseau est retiré, le fond est un panneau dans la même matière que les joues. Joues, fond, étagère et porte en mélaminé blanc. Étagère à mi-hauteur, deux bacs SLIBB, porte à poignée à droite sur charnières IKEA UTRUSTA, percée d'une fenêtre à 3/4 de la hauteur de chaque étage. Plus de peinture."),
    ("V7.9", "04/11/2026", "Le dos devient un vrai cadre : 2 montants, 2 traverses et 1 diagonale en tasseau, vissé contre les joues nord et milieu. Les 4 équerres de l'arrière disparaissent : 6 équerres en tout."),
    ("V7.8", "04/11/2026", "Dos remplacé par 2 traverses et 1 diagonale en tasseau de 38 × 38, à la demande du client. Le mur reste visible et la place libre passe à 53,9 de profondeur. Prix inchangé : les tasseaux et les vis de la diagonale sont pris dans les achats du meuble haut."),
    ("V7.7", "04/11/2026", "Pieds : les tubes d'aluminium et les cales sont remplacés par 2 vérins réglables encastrés sous chaque joue, à 2 du sol. Joues et dos de 85 de haut."),
    ("V7.6", "04/11/2026", "Dos en panneau rétabli : le client refusait une structure en tasseaux, pas ce panneau. Aucun tasseau au sol, sous le plateau ou à l'arrière. 10 équerres. Le dos est peint côté place libre et levé comme les joues."),
    ("V7.5", "04/11/2026", "Joues levées à 2,3 du sol sur un tube d'aluminium collé. Dos retiré : plus rien entre les joues et le plateau. 6 équerres au lieu de 17. Finition limitée aux chants avant et aux faces de la place libre. Deux dalles hydrofuges au lieu de la plaque."),
    ("V7.4", "04/11/2026", "Joues et dos en aggloméré hydrofuge peint, plateau en chêne : choix provisoire tant que la matière n'est pas tranchée. Le tableau d'achats passe dans la liste d'achats."),
    ("V7.3", "04/11/2026", "Structure refaite sur un autre principe : trois joues pleines et un dos en chêne de 18, sans ossature ni diagonale. Découpe et ordre de montage vérifiés. Place libre portée à 47,5 de large."),
    ("V7.2", "04/11/2026", "Lambourdes 45 × 70 avec écharpes, tapis anti-vibration sous la machine. Structure abandonnée : trop épaisse, et les écharpes ne s'assemblaient pas."),
    ("V7.1", "04/11/2026", "Bastaings 63 × 175 en trois portiques. Structure abandonnée : trop épaisse."),
    ("V7.0", "04/11/2026", "Conception reprise de zéro : alcôve, mesures et machine en place. L'ancien meuble bas (V6.2) reste dans les archives."),
]

# versions figées du meuble bas (archive/), puis celles des deux meubles ; libellé : texte du lien de l'historique
FIGEES = (
    ("V6.2", "archive/sdb-meuble-v4-bas.html"),
    ("Variantes V1.0", "archive/sdb-meuble-variantes.html"),
    ("Niveaux de finition V1.0", "archive/sdb-meuble-niveaux.html"),
    ("Revue V1.0", "archive/sdb-meuble-bas-revue.html"),
) + FIGEES_COMMUNES


def _document():
    from commun.modele import Changement, Document, Variante
    from pieces.sdb.meuble_bas import dessins, vues
    variante = Variante("", "Meuble bas", VERSION, tuple(Changement(*c) for c in CHANGEMENTS), FIGEES)
    return Document("sdb", "meuble-bas", "Meuble bas", "construction", (variante,), vues.vues, css=dessins.CSS_DOCUMENT)


def __getattr__(nom):
    if nom == "DOCUMENT":
        globals()["DOCUMENT"] = _document()
        return globals()["DOCUMENT"]
    raise AttributeError(f"module {__name__!r} has no attribute {nom!r}")
