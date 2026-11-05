# Liste d'achats du meuble linge : sdb-meuble-achats.html, à la racine. Elle suit les meubles courants : bas.prix() pour le
# meuble bas, haut.lignes() pour le meuble haut. La liste de l'ancien meuble en L reste dans pages.py, pour les archives.
#
#   python3 3d/sdb/achats.py   (just sdb)

import os
import sys
from html import escape

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import modele as M  # noqa: E402
import plan as PL  # noqa: E402
import pages as PG  # noqa: E402
import haut as H  # noqa: E402
import bas as B  # noqa: E402

PAGE = "sdb-meuble-achats.html"
VERSION = B.VERSION
BARRE = ('<div class="vbar"><a class="back" href="index.html">← Plans</a><span class="sp"></span>'
         '<a class="btn" href="sdb-meuble-bas.html">Meuble bas →</a>'
         '<a class="btn" href="sdb-meuble-haut.html">Meuble haut →</a></div>')
CHANGEMENTS = [
    ("V8.5", "05/11/2026", "Panneau perforé retiré. Meuble bas à 296,82 €."),
    ("V8.4", "05/11/2026", "Panneau perforé SKÅDIS 36 × 56 ajouté, colonne en diagonale prise dans la même chute. Meuble bas à 306,82 €."),
    ("V8.3", "05/11/2026", "Trajet du câble de la colonne précisé, depuis le bas du mur nord. Prix inchangé : 296,82 €."),
    ("V8.2", "05/11/2026", "Colonne de prises : 4 prises et 4 boîtes, panneaux pris dans une chute. Meuble bas à 296,82 €."),
    ("V8.1", "05/11/2026", "Bas du placard ajouté, pris dans une chute de tablette ; porte découpée en U. Prix inchangé : 264,90 €."),
    ("V8.0", "04/11/2026", "Meuble bas à 264,90 € : tablettes de mélaminé blanc, chant, charnières et poignées, 2 bacs. Plus de dalles ni de peinture, plus de tasseaux du meuble haut."),
    ("V7.9", "04/11/2026", "Meuble bas à 209,01 € : le cadre remplace les 4 équerres de l'arrière, soit un lot de moins. Ses tasseaux et ses vis viennent des achats du meuble haut."),
    ("V7.8", "04/11/2026", "Dos remplacé par des tasseaux : prix inchangé, car la barre et les vis 6 × 90 viennent des achats du meuble haut."),
    ("V7.7", "04/11/2026", "Meuble bas à 214,96 € : 6 vérins à la place du tube d'aluminium. Si le vérin est vendu par paquet, le prix baisse."),
    ("V7.6", "04/11/2026", "Meuble bas à 212,92 € : dos en panneau rétabli, pris dans les mêmes dalles, et 10 équerres, soit un lot de plus."),
    ("V7.5", "04/11/2026", "Meuble bas à 206,97 € : pieds en tube d'aluminium, 6 équerres, finition limitée, deux dalles au lieu de la plaque, plus de dos."),
    ("V7.4", "04/11/2026", "La liste suit le meuble bas courant, à joues pleines, et n'est plus celle du L. Plus de pièce du haut prise dans les chutes du bas : chaque meuble a sa liste complète."),
    ("V6.4", "04/11/2026", "Liste d'achats sortie dans une page à part, pour les deux meubles."),
]


def total_deux():
    return B.total() + H.total_lignes(H.lignes())


def deux_meubles():
    return f"""<h2 id="deux-meubles">Total des deux meubles</h2>
<div class="scroll"><table><thead><tr><th>Meuble</th><th class="num">Prix du meuble entier</th></tr></thead><tbody>
<tr><td><a href="#bas">Meuble bas</a></td><td class="num">{PL.euros(B.total())}</td></tr>
<tr><td><a href="#haut-seul">Meuble haut</a></td><td class="num">{PL.euros(H.total_lignes(H.lignes()))}</td></tr>
</tbody><tfoot><tr><td><b>Total TTC</b></td><td class="num"><b>{PL.euros(total_deux())}</b></td></tr></tfoot></table></div>
<p class="note">Le budget accepté le {M.BUDGET["date"]} était de {PL.euros(M.BUDGET["accepte"])}, pour l'ancien meuble en L et le même meuble haut.</p>"""


def bas_courant():
    _, tab = PL.liste(B.prix(), "Total du meuble bas")
    return (f'<h2 id="bas">Meuble bas</h2><p>Tout ce qu\'il faut pour <a href="{B.PAGE}">le meuble bas {B.VERSION}</a>. '
            f'Joues, fond, bas, étagère et porte en mélaminé blanc, levés sur des vérins, avec les 2 bacs.</p>{tab}'
            f'<p class="note">Les vis 4 × 40 viennent de la liste du meuble haut, qui en a assez. Pour acheter le meuble bas seul, ajouter la boîte de vis (9,00 €), soit {PL.euros(B.total() + 9.00)}. '
            f'Chant : {B.cm(B.chant_vu() / 100)} m à plaquer, 10 % de chutes compris. Vérins comptés à l\'unité comme l\'indique la fiche ; un avis client parle d\'un paquet de 5, à vérifier en magasin. Le lot de poignées en contient 2, une seule sert. Non comptés : le câble, la goulotte et l\'électricien, la scie sauteuse, le rail de coupe, le foret à cuvette Ø 35, la scie cloche Ø 67 et les clips adhésifs du fil des LED.</p>')


def haut_seul():
    _, tab = PL.liste(H.lignes(), "Total du meuble haut")
    return (f'<h2 id="haut-seul">Meuble haut</h2><p>Cette liste correspond à la découpe de la page '
            f'<a href="{H.PAGE}">Meuble haut</a> : tout le caisson, K1 et G12 compris.</p>{tab}')


def changements():
    corps = "".join(f'<tr><td class="mono">{v}</td><td class="mono">{d}</td><td>{escape(x)}</td></tr>'
                    for v, d, x in CHANGEMENTS)
    return (f'<section id="changements"><h2>Changements</h2><div class="scroll"><table><thead><tr><th>Version</th>'
            f'<th>Date</th><th>Changements</th></tr></thead><tbody>{corps}</tbody></table></div></section>')


def page():
    mg = M.MAGASIN
    corps = f"""<div class="kicker">Salle de bain · meuble bas et meuble haut · achats · {VERSION}</div>
<h1>Liste d'achats</h1>

{deux_meubles()}

{bas_courant()}

{haut_seul()}

<p class="note">Sauf mention, articles chez {escape(mg["nom"])} ({escape(mg["adresse"])}, {mg["tel"]}). Stock : nombre affiché sur
la fiche produit pour ce magasin (« — » : non lu). Prix TTC relevés en ligne le {mg["releve"]}, le {M.RELEVE_V6} et, pour les
articles Castorama et IKEA, le 04/11/2026 (stock non lu).</p>
<p class="note">Source : <span class="mono">3d/sdb/bas.py</span> et <span class="mono">3d/sdb/haut.py</span> ; page :
<span class="mono">3d/sdb/achats.py</span> (<span class="mono">just sdb</span>).</p>

{changements()}"""
    return PG.gabarit("Liste d'achats · meuble linge", "achats", corps, BARRE)


def ecrire():
    chemin = os.path.join(PL.ROOT, PAGE)
    with open(chemin, "w", encoding="utf-8") as fh:
        fh.write(page())
    print(chemin)


if __name__ == "__main__":
    ecrire()
