# Meuble haut de la salle de bain : le document (version, changements, versions figées).
#
# Les deux changements sont repris de l'ancienne page sdb-meuble-haut.html (V6.4), du plus récent au plus ancien.

from pieces.sdb.archives import FIGEES_COMMUNES

VERSION = "V6.5"
CHANGEMENTS = [
    ("V6.5", "17/11/2026", "Plans séparés en deux onglets : Plans (dessins cotés, avec Mesurer) et Iso (vues axonométriques : iso et éclatée)."),
    ("V6.4", "04/11/2026", "Liste d'achats sortie dans une page à part, pour les deux meubles."),
    ("V6.3", "04/11/2026", "Meuble haut sorti en page autonome, avec sa propre découpe et ses propres achats ; les autres documents du meuble linge sont archivés."),
]

# version figée du meuble haut (archives/), puis celles des deux meubles ; libellé : texte du lien de l'historique
FIGEES = (("V6.2", "archives/sdb-meuble-v4-haut.html"),) + FIGEES_COMMUNES


def _document():
    from commun.modele import Changement, Document, Variante
    from pieces.sdb.meuble_haut import dessins, vues
    variante = Variante("", "Meuble haut", VERSION, tuple(Changement(*c) for c in CHANGEMENTS), FIGEES)
    return Document("sdb", "meuble-haut", "Meuble haut", "construction", (variante,), vues.vues, css=dessins.CSS_DOCUMENT)


def __getattr__(nom):
    if nom == "DOCUMENT":
        globals()["DOCUMENT"] = _document()
        return globals()["DOCUMENT"]
    raise AttributeError(f"module {__name__!r} has no attribute {nom!r}")
