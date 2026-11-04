# Liste d'achats du meuble linge (V6.4) : sdb-meuble-achats.html, à la racine. Les deux meubles achetés ensemble, puis le
# meuble haut acheté seul (la liste qui suit la découpe de sdb-meuble-haut.html). Le calcul du haut seul vit dans haut.py ;
# celui des deux meubles, dans pages.py.
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

PAGE = "sdb-meuble-achats.html"
BARRE = ('<div class="vbar"><a class="back" href="index.html">← Plans</a><span class="sp"></span>'
         '<a class="btn" href="sdb-meuble-haut.html">Meuble haut →</a></div>')
BAS_ARCHIVE = "archive/sdb-meuble-v4-bas.html"


def note_version():
    return (f'<p class="note">Le meuble bas chiffré ici est celui de la version V6.2 (L basculant, page '
            f'<a href="{BAS_ARCHIVE}">archivée</a>) ; son choix reste ouvert, donc sa liste peut changer.</p>')


def deux_meubles():
    a = PG.lignes_achats()
    lg, p, mg = a["lignes"], PG.prix(), M.MAGASIN
    tables = "".join(f"<h3>{titre}</h3>{PL.liste(lg[cle], titre)[1]}"
                     for cle, titre in (("commun", "Consommables communs"), ("haut", "Meuble haut"),
                                        ("bas", "Meuble bas")))
    ail = [x for m in ("commun", "bas", "haut") for x in a["manque"][m]]
    ailleurs = (f'<p><b>À acheter ailleurs</b> : {escape(" ; ".join(ail))}. La toile des sacs '
                f'({PL.euros(M.TOILE["prix"])}) est comptée dans le total.</p>' if ail else "")
    non = (f'<p class="note">Non chiffrés, en rayon : {escape(" ; ".join(a["non_chiffres"]))}.</p>'
           if a["non_chiffres"] else "")
    accepte = ("total accepté par le client" if abs(p["total"] - M.BUDGET["accepte"]) <= 0.005 else
               f'à faire valider par le client ({PL.euros(M.BUDGET["accepte"])} accepté le {M.BUDGET["date"]})')
    total = (f'<p><b>Total TTC des deux meubles : {PL.euros(p["total"])}</b>, pour un budget visé de '
             f'{PL.euros(M.BUDGET["cible"])} : {accepte}.</p>')
    chutes = (f'<p><b>Pièces du caisson haut prises dans les achats du meuble bas</b> : {escape(PG.liste_chutes())}. '
              f'Elles ne sont donc pas comptées dans la liste Meuble haut ci-dessus ; leur dessin de découpe est dans la '
              f'<a href="{BAS_ARCHIVE}#decoupe">page archivée du meuble bas, section Découpe</a>.</p>')
    return f"""<h2 id="deux-meubles">Les deux meubles achetés ensemble</h2>
<p>Chez <b>{escape(mg["nom"])}</b> ({escape(mg["adresse"])}, {mg["tel"]}), à retirer en magasin.</p>
{tables}
{ailleurs}{non}{total}
{chutes}"""


def haut_seul():
    ls = H.lignes()
    _, tab = PL.liste(ls, "Sous-total, caisson haut seul")
    return (f'<h2 id="haut-seul">Meuble haut acheté seul</h2>'
            f'<p>Cette liste correspond à la découpe de la page <a href="{H.PAGE}">Meuble haut</a> : tout le caisson, '
            f'K1 et G12 compris, sans rien prendre dans les chutes du meuble bas. Elle ne s\'ajoute pas au total des deux '
            f'meubles : c\'est une autre façon d\'acheter le caisson.</p>{tab}')


def changements():
    lignes_v = [c for c in M.CHANGEMENTS if c[0] == "V6.4"]
    corps = "".join(f'<tr><td class="mono">{v}</td><td class="mono">{d}</td><td>{escape(x)}</td></tr>'
                    for v, d, x in lignes_v)
    return (f'<section id="changements"><h2>Changements</h2><div class="scroll"><table><thead><tr><th>Version</th>'
            f'<th>Date</th><th>Changements</th></tr></thead><tbody>{corps}</tbody></table></div>'
            f'<p>Historique de la page du meuble haut : <a href="{H.PAGE}#changements">sdb-meuble-haut.html, section '
            'Changements</a>.</p></section>')


def page():
    corps = f"""{PG.kicker("achats")}
<h1>Liste d'achats</h1>
{note_version()}

{deux_meubles()}

{haut_seul()}

<p class="note">Stock : nombre affiché sur la fiche produit pour ce magasin (« — » : non lu). Prix TTC relevés en ligne
le {M.MAGASIN["releve"]} et le {M.RELEVE_V6}.</p>
<p class="note">Source : <span class="mono">3d/sdb/modele.py</span> ; page : <span class="mono">3d/sdb/achats.py</span>
(<span class="mono">just sdb</span>).</p>

{changements()}"""
    return PG.gabarit("Liste d'achats · meuble linge", "achats", corps, BARRE)


def ecrire():
    chemin = os.path.join(PL.ROOT, PAGE)
    with open(chemin, "w", encoding="utf-8") as fh:
        fh.write(page())
    print(chemin)


if __name__ == "__main__":
    ecrire()
