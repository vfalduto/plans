# Cuisine, aménagement : le document (construire_document) et la déclaration du cache de ses rendus.
#
# Les rendus se font en deux temps : cad.py (FreeCAD) écrit le glb depuis le modèle, rendu.py (Blender) le lit. Le glb
# est l'entrée du rendu : le modèle et cad.py entrent donc dans l'empreinte, avec rendu.py et 3d/rendu.py. La version
# de FreeCAD n'y entre pas (CacheRendu ne connaît que celle de Blender).
#
# Toute variable en capitales de ce module (sauf celles de commun.rendu_cache.EXCLUES) doit être une donnée
# sérialisable : nommer _x ce qui n'en est pas une.

from commun.rendu_cache import CacheRendu

# une seule variante, d'id vide : rendus/<caméra>.jpg, `-` en ligne de commande
CACHE_RENDU = CacheRendu(variantes={"": ("pieces.cuisine.piece", "pieces.cuisine.modele")},
                         code=("pieces/cuisine/amenagement/rendu.py", "pieces/cuisine/amenagement/cad.py",
                               "3d/rendu.py"))

# versions figées : (version, chemin sous site/)
FIGEES = (("V11.49", "archive/cuisine-v11.49.html"), ("V12.7", "archive/cuisine-v12.7.html"))


def _texte_changement(texte: str) -> str:
    """Point médian remplacé par une virgule ; l'ancienne ancre de l'étude du plan de travail devient la vue Explication."""
    return texte.replace(" · ", ", ").replace("#hauteur-du-plan-de-travail-etude", "./#explication")


def construire_document():
    """Le Document de la cuisine/aménagement (exposé en `DOCUMENT` à la bascule, tâche 11)."""
    from commun.modele import Changement, Document, Variante
    from pieces.cuisine import modele as m
    from pieces.cuisine.amenagement import dessins, vues
    changements = tuple(Changement(v, d, _texte_changement(t)) for v, d, t in m.CHANGEMENTS)
    return Document(piece="cuisine", id="amenagement", nom="Aménagement", type="amenagement",
                    variantes=(Variante("", "Principale", m.VERSION, changements, FIGEES),), generer=vues.vues,
                    css=dessins.CSS_DESSINS)
