# Relais : le modèle de la cuisine est dans pieces/cuisine/modele.py. `import modele` (plan.py, porte.py,
# imprimable.py, cad.py, rendu.py) reçoit ce module-là, le même objet, noms en _ compris.
import importlib
import os
import sys

_RACINE = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if _RACINE not in sys.path:
    sys.path.append(_RACINE)     # en fin : 3d/v13/ garde la priorité pour plan, porte, rendu
sys.modules[__name__] = importlib.import_module("pieces.cuisine.modele")
