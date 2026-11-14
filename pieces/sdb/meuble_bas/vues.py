"""Les vues du meuble bas : Plans (les onze dessins), Découpe, Montage, Achats, Explication.

Une seule variante (id vide), pas d'option. Les textes qui étaient sous les dessins de l'ancienne page deviennent leur
texte alternatif (alts) : rien n'est écrit sous un dessin.
"""
import re
from html import unescape

from commun.blocs import vue_lecture
from commun.blocs_construction import DessinMeuble, vue_plans
from commun.modele import Vue
from pieces.sdb.meuble_bas import modele as B
from pieces.sdb.meuble_bas.dessins import ARIA, DESSINS, ISO, NOMS, legendes


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


def vues(variante: str) -> dict[str, Vue]:
    if variante != "":
        raise ValueError(f"meuble bas : variante « {variante} » inconnue (une seule, d'id vide)")
    return {"plans": _plans(), "decoupe": vue_lecture("decoupe", ""), "montage": vue_lecture("montage", ""),
            "achats": vue_lecture("achats", ""), "explication": vue_lecture("explication", "")}
