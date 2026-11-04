# Meuble linge de la salle de bain : document à part qui confronte trois variantes du meuble bas au meuble actuel.
#
# Le meuble actuel (document V4, modele.py) n'est pas touché. Chaque variante vit dans son propre module, qui lit
# modele.py pour l'alcôve, la machine, le plan de travail et le caisson haut, et décrit le reste lui-même :
#   var_pivot.py      variante 1 : porte en L sur un axe pivotant (plus de charnières)
#   var_tiroirs.py    variante 2 : caisson en mélaminé, deux tiroirs (haut, bas), trou en façade pour jeter le linge
#   var_arceaux.py    variante 3 : meuble ouvert, deux rails et un arceau, les bacs se posent sur l'arceau
#   var_comparatif.py comparatif des quatre meubles (actuel + trois variantes)
#
# Contrat d'un module de variante : ID (ancre), TITRE, RESUME (une phrase), section() → HTML du chapitre (sans le h2),
# FICHE (dict lu par le comparatif). Le comparatif : TITRE, section().
#
# `just sdb-variantes` écrit sdb-meuble-variantes.html. Un module absent ou en erreur laisse un encart à sa place et un
# avertissement sur la sortie d'erreur (les agents travaillent en parallèle) ; --strict fait échouer la génération.

import importlib
import os
import sys
import traceback
from html import escape

sys.path.insert(0, os.path.dirname(__file__))
import modele as M  # noqa: E402
import plan as PL  # noqa: E402
import pages as PG  # noqa: E402

VERSION = "V1.0"
FICHIER = "sdb-meuble-variantes.html"
CLE = "sdb-variantes"
MODULES = ("var_pivot", "var_tiroirs", "var_arceaux")
CHANGEMENTS = [
    ("V1.0", "2026-11-01", "Document créé : trois variantes du meuble bas (porte en L sur axe pivotant, deux tiroirs en "
                           "mélaminé avec trou en façade, meuble ouvert à rails et arceau) et comparatif avec le meuble "
                           "actuel (V6) : mettre le linge, retirer le linge, complexité de construction."),
]
ERREURS = []

CSS = PG.CSS + """
.var-absente{border:1px dashed var(--line);border-radius:10px;padding:12px 14px;color:var(--muted)}
.var-absente pre{white-space:pre-wrap;font-size:12px}
"""


def charger(nom):
    try:
        return importlib.import_module(nom), None
    except Exception:
        return None, traceback.format_exc()


def absente(nom, err):
    ERREURS.append(nom)
    print(f"[variantes] {nom} : {err.strip().splitlines()[-1] if err else 'absent'}", file=sys.stderr)
    return (f'<div class="var-absente">Chapitre <span class="mono">{nom}.py</span> pas encore disponible.'
            f'{f"<pre>{escape(err)}</pre>" if err else ""}</div>')


def chapitre(nom):
    mod, err = charger(nom)
    if mod is None:
        return f'<h2 id="{nom}">{escape(nom)}</h2>' + absente(nom, err)
    try:
        corps = mod.section()
    except Exception:
        return f'<h2 id="{mod.ID}">{escape(mod.TITRE)}</h2>' + absente(nom, traceback.format_exc())
    return f'<section class="variante" id="{mod.ID}">\n<h2>{escape(mod.TITRE)}</h2>\n{corps}\n</section>'


def actuel():
    iso = PG.iso_meuble("bas")
    return f"""<section id="actuel">
<h2>Rappel : le meuble actuel</h2>
<div class="fig">{iso}
<p class="cap">Meuble bas du <a href="{PG.ENSEMBLE}">document V4</a> ({M.VERSION}) : trois échelles en tasseaux sous un plan en chêne à {PG.cm(M.Z_DESSUS)}, machine au sol à droite. À gauche, une porte basculante en L (porte + plateau, deux contrefiches) pivote sur deux charnières plates vissées au rail avant ; deux sacs à soufflet pendent entre une barre au dos de la porte et une demi-barre arrière accrochée sous le plan.</p></div>
</section>"""


def page(strict=False):
    ERREURS.clear()
    chap = "\n\n".join(chapitre(n) for n in MODULES)
    comp = chapitre("var_comparatif")
    lignes = "".join(f'<tr><td class="mono">{v}</td><td class="mono">{d}</td><td>{escape(x)}</td></tr>'
                     for v, d, x in CHANGEMENTS)
    corps = f"""<div class="kicker">Salle de bain · alcôve {PG.cm(M.ALCOVE["nord"])} (nord) et {PG.cm(M.ALCOVE["sud"])} (sud) × {PG.cm(M.Y1)} · variantes du meuble bas · {VERSION}</div>
<h1>Meuble linge : trois variantes du bas</h1>
<p class="pitch">Un document de confrontation : le meuble actuel ne change pas. Trois autres façons de ranger le linge sale à gauche de la machine, chacune avec son plan, sa vue isométrique et l'explication de son mécanisme, puis un comparatif des quatre meubles : mettre le linge, retirer le linge, complexité à construire. Ce qui ne bouge pas : l'alcôve, la machine au sol à droite, le plan de travail en chêne de {PG.cm(M.PROF)} de profondeur et le caisson haut.</p>

{actuel()}

{chap}

{comp}

<p class="note">Repère : origine à l'angle nord-ouest intérieur de la salle de bain, x vers l'est, y vers le sud, z depuis le sol, cotes en cm. Sources : <span class="mono">3d/sdb/variantes.py</span> et ses modules <span class="mono">var_*.py</span>, qui lisent <span class="mono">3d/sdb/modele.py</span> (<span class="mono">just sdb-variantes</span>).</p>

<section id="changements">
<h2>Changements</h2>
<div class="scroll"><table><thead><tr><th>Version</th><th>Date</th><th>Changements</th></tr></thead>
<tbody>{lignes}</tbody></table></div>
</section>"""
    if strict and ERREURS:
        raise SystemExit(f"modules en erreur : {', '.join(ERREURS)}")
    return f"""{PL.entete("Variantes du meuble linge", "", CSS)}
<body class="explications changements">
<div class="vbar"><a class="back" href="index.html">← Plans</a><span class="sp"></span><a class="btn" href="{PG.ENSEMBLE}">Meuble actuel</a></div>
<nav class="toc" aria-label="Sommaire"><button type="button" class="tbtn" aria-expanded="true">Sommaire</button><ol></ol></nav>
<main class="wrap">
{corps}
</main>
<script>{PL.ANCRES}</script>
<script>{PG.SOMMAIRE % {"cle": CLE}}</script>
</body>
</html>
"""


def ecrire(strict=False):
    chemin = os.path.join(PL.ROOT, FICHIER)
    html = page(strict)
    with open(chemin, "w", encoding="utf-8") as fh:
        fh.write(html)
    print(chemin)


if __name__ == "__main__":
    ecrire("--strict" in sys.argv)
