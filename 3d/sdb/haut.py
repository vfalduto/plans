# Page autonome du meuble haut (V6.3) : sdb-meuble-haut.html, à la racine. Le caisson haut s'achète, se découpe et se
# monte avec cette seule page ; le meuble bas n'y figure que pour dire ce qu'il libère si on le construit aussi.
#
#   python3 3d/sdb/haut.py   (just sdb)
#
# Les fonctions communes (gabarit, notice, prix, matériaux) viennent de pages.py ; le calepinage des seules pièces du
# haut, de plan.py et calepinage.py.

import os
import sys
from html import escape

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import modele as M  # noqa: E402
import plan as PL  # noqa: E402
import calepinage as CAL  # noqa: E402
import pages as PG  # noqa: E402

PAGE = "sdb-meuble-haut.html"
ARCHIVE = "archive/sdb-meuble-v4.html"
ACHATS = "sdb-meuble-achats.html"
# usage des matériaux dans le débit du haut seul (le catalogue de modele.py décrit aussi le meuble bas)
USAGES = {"G": "tasseau de joint du fond G12 (non traité : poncer, puis peindre ou vernir toutes les faces)"}
BARRE = '<div class="vbar"><a class="back" href="index.html">← Plans</a><span class="sp"></span></div>'

_SEUL = []


def calepinage_seul():
    """Calepinage des seules pièces du caisson haut (K1 et G12 compris, sans les chutes du meuble bas), calculé une fois."""
    if not _SEUL:
        _SEUL.append(CAL.calepinage([p for p in PL.debit() if M.meuble(p["rep"]) == "haut"]))
    return _SEUL[0]


def rouleaux_haut():
    """Rouleaux de chant du caisson haut : son métrage (PL.chants) rapporté au rouleau de M.CHANT, arrondi au supérieur."""
    return -(-round(PL.chants()["metres"]["haut"] * 1000) // M.CHANT["rouleau"])


def lignes_article(code):
    """Lignes d'achat (nom, réf., quantité, prix, stock) d'un article du Weldom, comme PG.lignes_achats."""
    w = M.WELDOM[code]
    return [(x[0], x[4], x[2], x[1], x[3]) for x in (w if isinstance(w, list) else [w])]


def consommables_haut():
    """Consommables de M.CONSOMMABLES que les étapes du caisson haut utilisent (sauf le chant, compté à part). Le vernis
    n'a aucune étape du haut : il n'est pas acheté ici."""
    utilises = {c for n in M.MEUBLE_HAUT_ETAPES for c in M.ETAPES[n][-1]}
    return [c for c in M.CONSOMMABLES if c in utilises and c != "chant"]


def lignes():
    """Achats du caisson haut seul : panneaux et barres de son calepinage, quincaillerie propre au haut, consommables
    utilisés par ses étapes au conditionnement du magasin, chant au métrage du haut."""
    panneaux = [p for c in calepinage_seul().values() for p in c["retenu"]["panneaux"]]
    r = PL.ligne_panneaux(panneaux)
    r += PG.lignes_achats()["quinc"]["haut"]
    for code in consommables_haut():
        if M.WELDOM.get(code) is not None:
            r += lignes_article(code)
    nom, ref, _, px, st = lignes_article("chant")[0]
    r.append((nom, ref, rouleaux_haut(), px, st))
    return r


def total_lignes(ls):
    return sum(n * px for _, _, n, px, _ in ls)


def decoupe():
    seul = calepinage_seul()
    tas, tab = seul[M.STOCK["G"]], seul[M.STOCK["K"]]
    g12 = next(r for r in PL.debit() if r["rep"] == "G12")
    tasseaux = "".join(PL.tablette_svg(p, k + 1) for k, p in enumerate(tas["retenu"]["panneaux"]))
    tablettes = "".join(PL.tablette_svg(p, k + 1) for k, p in enumerate(tab["retenu"]["panneaux"]))
    n = rouleaux_haut()
    return f"""<h2 id="decoupe">Découpe</h2>
<div class="fig">{PL.table_debit("haut", USAGES)}</div>
<div class="fig"><div class="tabs">{tasseaux}</div>
<p class="cap">Tasseau de joint du fond G12 ({g12["L"]} mm) : tronçonné dans une barre de {M.PANNEAUX["G"][0]["L"]} (lot de six au magasin). Trait de scie de {CAL.TRAIT} mm compté.</p></div>
<div class="fig"><div class="tabs">{tablettes}</div>
<p class="cap">Tablettes mélaminées du caisson haut : refente en bandes sur la longueur, puis tronçonnage (trait de scie de {CAL.TRAIT} mm compté). Chants coupés visibles plaqués de chant thermocollant : {PL.virg(PL.chants()["metres"]["haut"], 2)} m, chants d'usine des tablettes tournés vers l'extérieur ; {PG.lettres(n)} rouleau{"x" if n > 1 else ""} de {PG.cm(M.CHANT["rouleau"] / 1000)} m.</p></div>
<p class="note">Faire débiter au magasin (service « découpe bois », tarif à demander) ou à la scie circulaire sur rail.</p>"""


def achats():
    """Section Achats de la page du caisson haut : seulement son prix et les renvois à la liste d'achats."""
    prix = PL.euros(total_lignes(lignes()))
    return (f'<h2 id="achats">Achats</h2><p>Le caisson haut, acheté seul, coûte <b>{prix}</b>. Sa liste, celle que suit la '
            f'découpe de cette page, est dans <a href="{ACHATS}#haut-seul">la liste d\'achats, section Meuble haut acheté '
            f'seul</a> ; pour les deux meubles ensemble, voir <a href="{ACHATS}#deux-meubles">la liste commune</a>.</p>')


def changements():
    lignes_v = [c for c in M.CHANGEMENTS if c[0] in ("V6.4", "V6.3")]
    corps = "".join(f'<tr><td class="mono">{v}</td><td class="mono">{d}</td><td>{escape(x)}</td></tr>'
                    for v, d, x in lignes_v)
    return (f'<section id="changements"><h2>Changements</h2><div class="scroll"><table><thead><tr><th>Version</th>'
            f'<th>Date</th><th>Changements</th></tr></thead><tbody>{corps}</tbody></table></div>'
            f'<p>Historique complet du meuble linge : <a href="{ARCHIVE}#changements">archive/sdb-meuble-v4.html, '
            'section Changements</a>.</p></section>')


def page():
    corps = f"""{PG.kicker("meuble haut")}
<h1>Meuble haut</h1>
<p class="pitch">{PG.pitch("haut")}</p>

<h2 id="iso">Le meuble</h2>
<div class="fig">{PG.iso_meuble("haut")}</div>

{PG.montage("haut")}

{decoupe()}

{achats()}

{PG.materiaux_haut(partage=False)}

<p class="note">Repère : origine à l'angle nord-ouest intérieur, x vers l'est, y vers le sud, z depuis le sol, cotes en cm
(débit en mm). Source : <span class="mono">3d/sdb/modele.py</span> et <span class="mono">3d/sdb/haut.py</span>
(<span class="mono">just sdb</span>).</p>

{changements()}"""
    return PG.gabarit("Meuble haut · meuble linge", "haut", corps, BARRE)


def ecrire():
    chemin = os.path.join(PL.ROOT, PAGE)
    with open(chemin, "w", encoding="utf-8") as fh:
        fh.write(page())
    print(chemin)


if __name__ == "__main__":
    ecrire()
