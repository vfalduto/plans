# Cuisine, aménagement : le document (pour l'instant, la déclaration du cache de ses rendus seule).
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
