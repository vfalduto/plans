# Meuble bas de la salle de bain : document qui présente plusieurs niveaux de finition de la nouvelle partie linge (deux
# paniers superposés, chacun sur deux traverses), notés par coût, difficulté, praticité et design.
#
# Le meuble actuel (document V4, modele.py) n'est pas touché. Un module par niveau, conçu par un agent :
#   niv_1.py … niv_4.py   contrat : ID, TITRE, RESUME, section() → HTML du chapitre (sans le h2), FICHE (voir niv_commun.py)
#   niv_comparatif.py     notes et recommandation, par un agent indépendant ; contrat : ID, TITRE, section()
#
# `just sdb-niveaux` écrit sdb-meuble-niveaux.html. Un module absent ou en erreur laisse un encart à sa place et un
# avertissement sur la sortie d'erreur ; --strict fait échouer la génération.

import importlib
import os
import sys
import traceback
from html import escape

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import modele as M  # noqa: E402
import plan as PL  # noqa: E402
import pages as PG  # noqa: E402
import niv_commun as NC  # noqa: E402

VERSION = "V1.0"
FICHIER = "sdb-meuble-niveaux.html"
CLE = "sdb-niveaux"
MODULES = ("niv_1", "niv_2", "niv_3", "niv_4")
CHANGEMENTS = [
    ("V1.0", "2026-11-04", "Document créé : quatre niveaux de finition du meuble bas avec deux paniers superposés posés sur "
                           "deux traverses, plan massif, machine à droite et au moins trois prises ; notes de coût, "
                           "difficulté, praticité et design."),
]
ERREURS = []

CSS = PG.CSS + """
.var-absente{border:1px dashed var(--line);border-radius:10px;padding:12px 14px;color:var(--muted)}
.var-absente pre{white-space:pre-wrap;font-size:12px}
td.num{text-align:right;white-space:nowrap}
"""


def absente(nom, err):
    ERREURS.append(nom)
    print(f"[niveaux] {nom} : {err.strip().splitlines()[-1] if err else 'absent'}", file=sys.stderr)
    return (f'<div class="var-absente">Chapitre <span class="mono">{nom}.py</span> pas encore disponible.'
            f'{f"<pre>{escape(err)}</pre>" if err else ""}</div>')


def chapitre(nom):
    try:
        mod = importlib.import_module(nom)
    except Exception:
        return f'<h2 id="{nom}">{escape(nom)}</h2>' + absente(nom, traceback.format_exc())
    try:
        corps = mod.section()
    except Exception:
        return f'<h2 id="{mod.ID}">{escape(mod.TITRE)}</h2>' + absente(nom, traceback.format_exc())
    return f'<section class="variante" id="{mod.ID}">\n<h2>{escape(mod.TITRE)}</h2>\n{corps}\n</section>'


def valide():
    return f"""<section id="valide">
<h2>Ce qui est validé, à tous les niveaux</h2>
<ul>
<li><b>Plateau en massif</b> au-dessus de la machine, de {NC.cm(M.PROF)} de profondeur.</li>
<li><b>Machine à droite</b>, porte qui s'ouvre à gauche, <b>espace technique de 5 à 7 cm</b> derrière (évacuation et robinet).</li>
<li><b>Au moins 3 prises</b> au-dessus du plateau.</li>
<li><b>Deux paniers l'un au-dessous de l'autre</b>, chacun posé sur deux traverses, à la place de la porte basculante : chaque panier s'ouvre et se retire sans toucher à l'autre.</li>
</ul>
<p>Place disponible pour le linge, sans aucune structure : {NC.cm(NC.LARGEUR_BAIE)} de large, {NC.cm(NC.PROF_BAIE)} de profondeur, {NC.cm(NC.HAUT_BAIE)} de haut.</p>
<p class="note">Lecture retenue pour « deux traverses » : deux traverses par panier, donc quatre en tout. Elles vont d'avant en arrière, une de chaque côté du panier.</p>
</section>"""


def page(strict=False):
    ERREURS.clear()
    comp = chapitre("niv_comparatif")
    chap = "\n\n".join(chapitre(n) for n in MODULES)
    lignes = "".join(f'<tr><td class="mono">{v}</td><td class="mono">{d}</td><td>{escape(x)}</td></tr>'
                     for v, d, x in CHANGEMENTS)
    corps = f"""<div class="kicker">Salle de bain · meuble bas · niveaux de finition · {VERSION}</div>
<h1>Meuble linge : quatre niveaux de finition</h1>
<p class="pitch">La partie linge sale passe à deux paniers superposés, indépendants. Le même programme est traité à quatre niveaux, du plus simple au plus soigné, chacun avec ses dessins, son prix et ses notes.</p>

{comp}

{valide()}

{chap}

<p class="note">Repère : x vers le mur du fond, y du nord vers le sud, z depuis le sol, cotes en cm. Sources : <span class="mono">3d/sdb/niveaux.py</span> et ses modules <span class="mono">niv_*.py</span> (<span class="mono">just sdb-niveaux</span>).</p>

<section id="changements">
<h2>Changements</h2>
<div class="scroll"><table><thead><tr><th>Version</th><th>Date</th><th>Changements</th></tr></thead>
<tbody>{lignes}</tbody></table></div>
</section>"""
    if strict and ERREURS:
        raise SystemExit(f"modules en erreur : {', '.join(ERREURS)}")
    return f"""{PL.entete("Niveaux de finition du meuble linge", "", CSS)}
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
